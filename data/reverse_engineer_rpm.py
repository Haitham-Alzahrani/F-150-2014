"""Reverse engineering: what moves BEFORE engine speed, and what follows it.

Every channel in every log is aligned against engine speed on its own real
sample times, cross-correlated, and reported with the sign and size of its lag.
A channel that consistently peaks at a POSITIVE lag changed first — it is a
candidate cause. A channel at a NEGATIVE lag is responding.

Two guards that decide whether the answer is real:

* The oscillation is nearly periodic at ~3.0 s, so cross-correlation repeats
  every period. The search is limited to +/- half a period; a lag reported
  outside that is the same phase repeated, not a different delay.
* Nothing is forward-filled. A channel is only used where it and engine speed
  were genuinely sampled close together.

Run:  python3 data/reverse_engineer_rpm.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from carscanner_lib import load, logs, on_grid, xcorr  # noqa: E402

DT = 0.05
HUNT_HZ = 0.304
MAX_LAG = 1.55                # half the oscillation period
MIN_POINTS = 400
LOGS = Path(__file__).parent / "carscanner"

# channels that are arithmetic on other channels, not measurements
DERIVED = ("Power from MAF", "Calculated instant fuel", "Calculated boost",
           "Engine RPM x1000", "Instant engine power", "Fuel used", "Distance",
           "Average speed", "Average fuel", "Fuel economizer", "Fuel used price",
           "Distance to empty", "Free space in fuel tank")


def band_power(x: np.ndarray) -> float:
    """Fraction of this channel's slow-band power sitting at the hunt frequency."""
    y = (x - x.mean()) * np.hanning(len(x))
    f = np.fft.rfftfreq(len(y), DT)
    p = np.abs(np.fft.rfft(y)) ** 2
    hunt = (f > HUNT_HZ * 0.85) & (f < HUNT_HZ * 1.15)
    total = (f > 0.05) & (f < 4.0)
    return float(p[hunt].sum() / p[total].sum()) if p[total].sum() else 0.0


def scan(data, name):
    tr, vr = data["Engine RPM (rpm)"]
    out = []
    for chan, (t, v) in data.items():
        if chan == "Engine RPM (rpm)" or any(k in chan for k in DERIVED):
            continue
        if len(v) < 200 or v.std() == 0:
            continue
        lo, hi = max(t.min(), tr.min()), min(t.max(), tr.max())
        if hi - lo < 60:
            continue
        grid = np.arange(lo, hi, DT)
        r = on_grid(tr, vr, grid, 0.5)
        x = on_grid(t, v, grid, 0.5)          # tight: real samples only
        ok = np.isfinite(r) & np.isfinite(x)
        if ok.sum() < MIN_POINTS:
            continue
        R, X = r[ok], x[ok]
        # idle only — mixing driving in would swamp everything
        idle = (R > 615) & (R < 700)
        if idle.sum() < MIN_POINTS:
            continue
        R, X = R[idle], X[idle]
        if X.std() == 0:
            continue
        lag, c = xcorr(X, R, DT, MAX_LAG)
        j, k = int(np.argmax(c)), int(np.argmin(c))
        i = j if abs(c[j]) >= abs(c[k]) else k
        out.append({"log": name, "chan": chan, "n": len(R), "r": float(c[i]),
                    "lag": float(lag[i]), "p2p": float(np.ptp(X)),
                    "hunt": band_power(X)})
    return out


def main() -> None:
    rows = []
    for p in logs(LOGS):
        rows += scan(load(p), p.name[:22])

    rows.sort(key=lambda d: -abs(d["r"]))
    print("=" * 108)
    print("EVERY CHANNEL vs ENGINE SPEED AT IDLE — sorted by strength of relationship")
    print("=" * 108)
    print(f"{'channel':44s} {'log':24s} {'n':>6s} {'r':>7s} {'lag s':>7s} "
          f"{'p2p':>9s} {'@0.30Hz':>8s}  verdict")
    for d in rows:
        if abs(d["r"]) < 0.15:
            continue
        if d["lag"] > 0.02:
            verdict = f"LEADS rpm by {d['lag']:.2f}s"
        elif d["lag"] < -0.02:
            verdict = f"follows rpm by {abs(d['lag']):.2f}s"
        else:
            verdict = "simultaneous"
        print(f"{d['chan'][:43]:44s} {d['log']:24s} {d['n']:6d} {d['r']:+7.3f} "
              f"{d['lag']:+7.2f} {d['p2p']:9.3f} {100*d['hunt']:7.1f}%  {verdict}")

    print()
    print("=" * 108)
    print("NO RELATIONSHIP — measured and excluded (|r| < 0.15)")
    print("=" * 108)
    weak = [d for d in rows if abs(d["r"]) < 0.15]
    for d in sorted(weak, key=lambda d: d["chan"]):
        print(f"  {d['chan'][:46]:48s} {d['log']:24s} n={d['n']:6d}  r={d['r']:+.3f}")

    print()
    print("=" * 108)
    print("THE CHAIN, ordered by when each thing moves")
    print("=" * 108)
    strong = [d for d in rows if abs(d["r"]) >= 0.25]
    for d in sorted(strong, key=lambda d: -d["lag"]):
        when = ("BEFORE" if d["lag"] > 0.02 else
                "WITH  " if abs(d["lag"]) <= 0.02 else "AFTER ")
        print(f"  {d['lag']:+6.2f}s  {when}  r={d['r']:+.3f}  {d['chan'][:44]:46s} ({d['log']})")


if __name__ == "__main__":
    main()
