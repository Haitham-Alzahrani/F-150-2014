"""6R80, driveline and electrical analysis of the Car Scanner logs.

Everything here works on each channel's own sample times. Nothing is
forward-filled. Where a fast channel has to be read at a slow channel's
timestamps it is interpolated between two real samples that straddle the point
by less than `max_gap`, and returned as NaN otherwise.

Output: docs/analysis/04-transmission-and-electrical.md was written from this.
Run:  python3 data/analyze_transmission.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from carscanner_lib import load, on_grid, rate  # noqa: E402

LOGS = HERE / "carscanner"
IDLE_3H = "2026-09-04 22-23-38.zip"
PARK_DRIVE = "20260905_030915.csv.gz"
DRIVE_WOT = "20260905_034051.csv.gz"
DRIVE_SPEED = "20260905_041723.csv.gz"

GEARS = {1: 4.17, 2: 2.34, 3: 1.52, 4: 1.14, 5: 0.87, 6: 0.69}
RPM = "Engine RPM (rpm)"
SPD = "Vehicle speed (km/h)"


def rel(d, ch):
    t, v = d[ch]
    return t - d[RPM][0][0], v


def nv(d, a, b, label):
    """Mean engine-speed-per-road-speed over a window, each channel on its own
    samples. Reported separately so the reader can see both counts."""
    tv, vv = rel(d, SPD)
    tr, vr = rel(d, RPM)
    ms = (tv >= a) & (tv <= b)
    mr = (tr >= a) & (tr <= b)
    out = dict(label=label, n_speed=int(ms.sum()), n_rpm=int(mr.sum()),
               v=vv[ms].mean(), v_sd=vv[ms].std(), rpm=vr[mr].mean(), rpm_sd=vr[mr].std())
    out["nv"] = out["rpm"] / out["v"]
    return out


def idle_stats(d, a, b, label):
    tr, vr = rel(d, RPM)
    m = (tr >= a) & (tr <= b)
    r = vr[m]
    spans = []
    for s in np.arange(a, b - 10, 10.0):
        mm = (tr >= s) & (tr < s + 10)
        if mm.sum() > 80:
            spans.append(vr[mm].max() - vr[mm].min())
    spans = np.array(spans)
    return dict(label=label, n=int(m.sum()), mean=r.mean(), sd=r.std(),
                lo=r.min(), hi=r.max(), n_win=len(spans),
                span=np.median(spans) if len(spans) else np.nan)


def shift(d, a, b, label):
    """One shift: pre level, peak (flare test), trough, post level, 10-90 % time."""
    tr, vr = rel(d, RPM)
    m = (tr >= a - 1.5) & (tr <= b + 1.5)
    tt, rr = tr[m], vr[m]
    if len(tt) < 8:
        return None
    pre = rr[(tt >= a - 0.6) & (tt <= a)]
    peak = rr[(tt >= a - 0.3) & (tt <= b)].max()
    mn = rr[(tt >= a) & (tt <= b + 0.4)].min()
    post = rr[(tt >= b) & (tt <= b + 0.6)]
    hi, lo = pre.mean(), mn
    band = (rr >= lo + 0.1 * (hi - lo)) & (rr <= lo + 0.9 * (hi - lo)) & (tt >= a - 0.4) & (tt <= b + 0.5)
    dur = tt[band][-1] - tt[band][0] if band.sum() >= 2 else np.nan
    return dict(label=label, n=int(m.sum()), hz=m.sum() / (tt[-1] - tt[0]),
                pre=pre.mean(), peak=peak, mn=mn, post=post.mean() if len(post) else np.nan,
                ratio=(post.mean() if len(post) else np.nan) / pre.mean(),
                t1090=dur, flare=peak - pre.max())


def volt_vs_rpm(d, ch, a, b, dt):
    """Is system voltage participating in the 0.3 Hz idle hunt?"""
    t, v = rel(d, ch)
    tr, vr = rel(d, RPM)
    grid = np.arange(a, b, dt)
    V, R = on_grid(t, v, grid, 4 * dt), on_grid(tr, vr, grid, 4 * dt)
    ok = np.isfinite(V) & np.isfinite(R)
    if ok.sum() < 200:
        return None
    Vv, Rr = V[ok] - V[ok].mean(), R[ok] - R[ok].mean()
    n = len(Vv)
    F = np.abs(np.fft.rfft(Vv * np.hanning(n))) ** 2
    f = np.fft.rfftfreq(n, dt)
    tot = F[1:].sum()
    return dict(ch=ch, n=int(ok.sum()), sd=Vv.std(), r=np.corrcoef(Vv, Rr)[0, 1],
                hunt_band=100 * F[(f >= 0.25) & (f < 0.4)].sum() / tot)


def main():
    d_idle = load(LOGS / IDLE_3H)
    d_pd = load(LOGS / PARK_DRIVE)
    d_wot = load(LOGS / DRIVE_WOT)
    d_spd = load(LOGS / DRIVE_SPEED)

    print("=" * 88)
    print("1. GEAR RATIOS — engine speed per km/h, on steady plateaus")
    plateaus = [nv(d_spd, 0, 16, "4th, accel 32-45 km/h  (drive2)"),
                nv(d_spd, 154, 160.3, "4th, accel 45-52 km/h  (drive2)"),
                nv(d_spd, 174, 199.5, "5th, cruise 61-62 km/h (drive2)"),
                nv(d_wot, 1038, 1044, "6th, cruise 87-88 km/h (drive1)")]
    k6 = plateaus[-1]["nv"] / GEARS[6]
    for p in plateaus:
        print("  %-38s n_speed=%3d n_rpm=%5d  v=%6.2f km/h  rpm=%7.1f  N/V=%6.3f"
              % (p["label"], p["n_speed"], p["n_rpm"], p["v"], p["rpm"], p["nv"]))
    print("\n  Taking 6th as the locked reference: k = N/V per unit gear ratio = %.3f" % k6)
    for p, g in zip(plateaus, [4, 4, 5, 6]):
        pred = k6 * GEARS[g]
        print("     %-38s gear %d  predicted N/V %6.3f  measured %6.3f  slip %+5.2f %%"
              % (p["label"], g, pred, p["nv"], 100 * (p["nv"] / pred - 1)))
    print("\n  Axle-ratio sensitivity: axle = k * C / (1000/60), C = rolling circumference")
    for C, lab in [(2.288, "703 rev/mile (loaded P255/65R17)"),
                   (2.346, "686 rev/mile (Michelin LTX 255/65R17 published)"),
                   (2.402, "670 rev/mile (theoretical free diameter)")]:
        print("     C=%.3f m  %-46s -> axle %.3f" % (C, lab, k6 * C / (1000 / 60)))

    print("\n" + "=" * 88)
    print("2. PARK vs IN GEAR at standstill — one log, one engine, minutes apart")
    for s in [idle_stats(d_pd, 600, 898, "IN GEAR, standstill"),
              idle_stats(d_pd, 915, 1230, "PARK, standstill")]:
        print("  %-22s n=%5d  mean=%7.2f  sd=%5.2f  min=%4.0f max=%4.0f  10-s span median=%5.1f (n_win=%d)"
              % (s["label"], s["n"], s["mean"], s["sd"], s["lo"], s["hi"], s["span"], s["n_win"]))

    print("\n" + "=" * 88)
    print("3. SHIFTS — ratio, 10-90 %% time, and engine flare")
    events_wot = [(944.50, 945.20, "WOT upshift, at limiter"), (949.65, 950.55, "upshift on lift"),
                  (951.30, 951.75, "coast upshift"), (952.40, 952.75, "coast upshift"),
                  (953.40, 953.80, "coast upshift"), (1011.40, 1012.10, "WOT upshift"),
                  (1012.80, 1013.20, "upshift"), (1013.95, 1014.40, "upshift"),
                  (1014.90, 1015.35, "upshift"), (826.90, 827.40, "part-throttle upshift"),
                  (668.75, 669.20, "part-throttle upshift"), (738.50, 738.90, "part-throttle upshift")]
    for a, b, lab in events_wot:
        s = shift(d_wot, a, b, lab)
        print("  t=%8.2f %-24s n=%3d @%4.1f Hz  pre=%5.0f peak=%5.0f post=%5.0f  ratio=%.3f  10-90%%=%.2f s  flare=%+.0f rpm"
              % (a, s["label"], s["n"], s["hz"], s["pre"], s["peak"], s["post"], s["ratio"], s["t1090"], s["flare"]))
    s = shift(d_spd, 160.15, 160.70, "4->5 at 52-54 km/h")
    print("  t=%8.2f %-24s n=%3d @%4.1f Hz  pre=%5.0f peak=%5.0f post=%5.0f  ratio=%.3f  (rpm only %.1f Hz here)"
          % (160.15, s["label"], s["n"], s["hz"], s["pre"], s["peak"], s["post"], s["ratio"], s["hz"]))

    print("\n" + "=" * 88)
    print("4. ELECTRICAL — three independent voltage sources, 3.2 h idle log")
    for ch in ["OBD Module Voltage (V)", "Control module voltage (V)",
               "[BCM] Vehicle Battery Voltage (V)", "[BCM] Vehicle Battery Current (A)",
               "[BCM] Battery SoC (%)"]:
        t, v = rel(d_idle, ch)
        early = (t < 2800)
        late = (t > 3100)
        print("  %-36s n=%6d | before min 46: n=%5d mean=%8.3f | after min 52: n=%5d mean=%8.3f"
              % (ch, len(v), early.sum(), v[early].mean() if early.sum() else np.nan,
                 late.sum(), v[late].mean() if late.sum() else np.nan))
    print("\n  Regulation quality, densest block (OBD Module Voltage, t=960-1620 s):")
    t, v = rel(d_idle, "OBD Module Voltage (V)")
    m = (t >= 960) & (t <= 1620)
    means = [v[(t >= a) & (t < a + 10)].mean() for a in np.arange(960, 1620, 10)
             if ((t >= a) & (t < a + 10)).sum() > 30]
    print("     n=%d  mean=%.3f V  10-s means span %.3f-%.3f V  samples below 13.6 V: %d (%.2f %%)"
          % (m.sum(), v[m].mean(), min(means), max(means), (v[m] < 13.6).sum(),
             100 * (v[m] < 13.6).sum() / m.sum()))
    print("\n  Is voltage part of the 0.3 Hz idle hunt?")
    for args in [("OBD Module Voltage (V)", 960, 1620, 0.06),
                 ("OBD Module Voltage (V)", 2160, 2280, 0.06),
                 ("Control module voltage (V)", 5700, 5900, 0.06)]:
        r = volt_vs_rpm(d_idle, *args)
        if r:
            print("     %-30s t=%5d-%5d  n=%5d  sd=%.4f V  r(rpm)=%+.3f  power in 0.25-0.4 Hz = %.1f %%"
                  % (r["ch"], args[1], args[2], r["n"], r["sd"], r["r"], r["hunt_band"]))
    print("\n  Voltage while driving (no window above 13.0 V in either driving log):")
    for nm, dd in [(DRIVE_WOT, d_wot), (DRIVE_SPEED, d_spd)]:
        for ch in ["Control module voltage (V)", "OBD Module Voltage (V)"]:
            if ch in dd:
                t, v = rel(dd, ch)
                print("     %-24s %-30s n=%4d  mean=%.3f  min=%.3f  max=%.3f"
                      % (nm, ch, len(v), v.mean(), v.min(), v.max()))

    print("\n" + "=" * 88)
    print("5. TYRE PRESSURES (BCM). Label 241 kPa / 35 psi. Inner channels are SRW placeholders.")
    for ch in sorted(k for k in d_idle if "Tire Pressure" in k):
        t, v = rel(d_idle, ch)
        print("  %-44s n=%3d  %8.2f kPa  %5.1f psi" % (ch, len(v), v.mean(), v.mean() * 0.145038))

    print("\n" + "=" * 88)
    print("6. ATF TEMPERATURE (Car Scanner 'var.3' — PID identity NOT verified)")
    for nm, dd in [(IDLE_3H, d_idle), (DRIVE_SPEED, d_spd)]:
        ch = "ATF temperature var.3 (℃)"
        if ch in dd:
            t, v = rel(dd, ch)
            for lo, hi in [(t[0] - 1, t[0] + 30), (t[-1] - 30, t[-1] + 1)]:
                m = (t >= lo) & (t <= hi)
                if m.sum():
                    print("  %-24s t=%7.0f s (min %5.1f)  n=%2d  mean=%6.2f C"
                          % (nm, t[m][0], t[m][0] / 60, m.sum(), v[m].mean()))


if __name__ == "__main__":
    main()
