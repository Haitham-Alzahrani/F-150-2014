"""Ten-second idle windows across every log, tagged with coolant temperature.

Answers one question: does the idle oscillation track coolant temperature?

Method notes that matter for reading the result:

* Engine speed is never interpolated. A window is used only if it holds at least
  50 real rpm samples inside its 10 seconds.
* Coolant temperature IS held forward, up to `ECT_HOLD` seconds. Coolant moves
  over minutes, so carrying the last reading a short way is defensible in a way
  that carrying an rpm sample never is. Windows with no reading inside that
  horizon are written with ect blank and excluded from the correlation.
* Only standstill idle is kept: rpm 500-750 and, where vehicle speed was
  sampled nearby, zero. Driving and throttle events are a different population.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from carscanner_lib import load, logs  # noqa: E402

WIN = 10.0          # window length, seconds
MIN_SAMPLES = 50    # real rpm samples required in a window
ECT_HOLD = 300.0    # how far a coolant reading may be carried forward
OUT = Path(__file__).parent / "analysis" / "idle_windows.csv"
EVENTS = Path(__file__).parent / "analysis" / "night_events.csv"


def load_events():
    """The night's conditions as recorded from the screenshots, by clock time."""
    def secs(s):
        h, m, sec = s.split(":")
        v = int(h) * 3600 + int(m) * 60 + float(sec)
        return v + 86400 if v < 12 * 3600 else v      # after midnight = next day
    out = []
    with EVENTS.open() as fh:
        for r in csv.DictReader(fh):
            out.append((secs(r["clock_start"]), secs(r["clock_end"]), r))
    return out


def event_at(events, when):
    when = when % 86400
    when = when + 86400 if when < 12 * 3600 else when
    for a, b, r in events:
        if a <= when <= b:
            return r
    return None


def held(t_series, v_series, when, horizon):
    """Most recent reading at or before `when`, or None past the horizon."""
    if len(t_series) == 0:
        return None
    i = int(np.searchsorted(t_series, when, side="right")) - 1
    if i < 0 or when - t_series[i] > horizon:
        return None
    return float(v_series[i])


def main() -> None:
    events = load_events()
    rows = []
    for path in logs(Path(__file__).parent / "carscanner"):
        d = load(path)
        tr, vr = d["Engine RPM (rpm)"]
        te, ve = d.get("Engine coolant temperature (℃)", (np.array([]), np.array([])))
        ts, vs = d.get("Vehicle speed (km/h)", (np.array([]), np.array([])))
        for start in np.arange(tr[0], tr[-1] - WIN, WIN):
            m = (tr >= start) & (tr < start + WIN)
            if m.sum() < MIN_SAMPLES:
                continue
            w = vr[m]
            mid = start + WIN / 2
            speed = held(ts, vs, mid, 120.0)
            if not (500 <= w.mean() <= 750):
                continue
            if speed is not None and speed > 0:
                continue
            # Ford commands a lower idle in gear, so mean rpm separates the two
            # populations at a standstill without a gear PID: ~550 in D/R,
            # ~650 in P/N. In gear the converter damps the same disturbance, so
            # mixing them would read as a temperature effect that is really a
            # gear effect.
            gear = "in_gear" if w.mean() < 600 else ("park_neutral" if w.mean() > 620 else "ambiguous")
            rows.append({
                "log": path.name,
                "gear_proxy": gear,
                "t_start_s": round(float(start), 2),
                "clock": _clock(start),
                "rpm_mean": round(float(w.mean()), 1),
                "rpm_span": round(float(w.max() - w.min()), 1),
                "rpm_sd": round(float(w.std()), 2),
                "n_samples": int(m.sum()),
                "ect_c": held(te, ve, mid, ECT_HOLD),
                "ect_age_s": _age(te, mid),
                "speed_kmh": speed,
            })
            ev = event_at(events, mid)
            rows[-1]["event_id"] = ev["event_id"] if ev else ""
            rows[-1]["condition"] = ev["condition"] if ev else ""
            rows[-1]["being_tested"] = ev["what_was_being_tested"] if ev else ""
            rows[-1]["epoch"] = ev["epoch"] if ev else ""

    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        wr.writeheader()
        wr.writerows(rows)
    print(f"wrote {len(rows)} idle windows -> {OUT}")

    have = [r for r in rows if r["ect_c"] is not None]
    print(f"{len(have)} of them carry a coolant reading within {ECT_HOLD:.0f} s\n")

    have = [r for r in have if r["gear_proxy"] == "park_neutral"]
    print(f"{len(have)} of those are Park/Neutral (in-gear windows are damped by the\n"
          f"converter and would read as a temperature effect that is really a gear effect)\n")

    ect = np.array([r["ect_c"] for r in have])
    span = np.array([r["rpm_span"] for r in have])
    sd = np.array([r["rpm_sd"] for r in have])
    print(f"Pearson r, span vs coolant : {np.corrcoef(ect, span)[0,1]:+.3f}  (n={len(have)})")
    print(f"Pearson r, sd   vs coolant : {np.corrcoef(ect, sd)[0,1]:+.3f}")
    rk = lambda x: np.argsort(np.argsort(x))          # noqa: E731
    print(f"Spearman rho, span vs coolant: {np.corrcoef(rk(ect), rk(span))[0,1]:+.3f}\n")

    print(" coolant    n   median span   mean span   p10   p90   median sd")
    edges = [80, 84, 88, 92, 95, 98, 102]
    for lo, hi in zip(edges, edges[1:]):
        m = (ect >= lo) & (ect < hi)
        if m.sum() < 5:
            continue
        print(f"  {lo}-{hi}  {m.sum():5d}   {np.median(span[m]):8.1f}   {span[m].mean():9.1f}"
              f"  {np.percentile(span[m],10):5.0f} {np.percentile(span[m],90):5.0f}"
              f"   {np.median(sd[m]):8.2f}")


def _clock(t: float) -> str:
    t = t % 86400
    return f"{int(t//3600):02d}:{int(t%3600//60):02d}:{t%60:05.2f}"


def _age(te, when):
    if len(te) == 0:
        return None
    i = int(np.searchsorted(te, when, side="right")) - 1
    return round(float(when - te[i]), 1) if i >= 0 else None


if __name__ == "__main__":
    main()
