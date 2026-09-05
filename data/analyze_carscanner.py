"""Timing analysis of the Car Scanner logs — what leads what at idle.

Screenshots could give amplitude but never phase. These logs sample each channel
at ~17 Hz on its own true timestamps, which is enough to ask the question the
whole investigation turns on: when the idle oscillates, is the PCM reacting to
engine speed or driving it?

Run:  python3 data/analyze_carscanner.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from carscanner_lib import load, on_grid, xcorr  # noqa: E402

LOGS = Path(__file__).parent / "carscanner"
DT = 0.05                 # analysis grid, 20 Hz
MAX_LAG = 1.55            # seconds — see note in phase()


def spectrum(x: np.ndarray) -> tuple[float, float]:
    """Dominant frequency between 0.05 and 3 Hz, and its period."""
    y = (x - x.mean()) * np.hanning(len(x))
    f = np.fft.rfftfreq(len(y), DT)
    p = np.abs(np.fft.rfft(y)) ** 2
    band = (f > 0.05) & (f < 3.0)
    pk = float(f[band][np.argmax(p[band])])
    return pk, 1.0 / pk


def pair(data, chan, a, b):
    """Align a channel with engine speed over [a, b] seconds from log start."""
    tr, vr = data["Engine RPM (rpm)"]
    grid = np.arange(tr[0] + a, tr[0] + b, DT)
    r = on_grid(tr, vr, grid, 0.5)
    t, v = data[chan]
    x = on_grid(t, v, grid, 1.0)
    ok = np.isfinite(x) & np.isfinite(r)
    return (x[ok], r[ok]) if ok.sum() >= 500 else (None, None)


def phase(x, r):
    """Cross-correlation peak within half an oscillation period.

    The oscillation is nearly periodic at ~3.2 s, so the correlation repeats
    every period: a peak reported at -3.3 s is the SAME phase as one at +0.1 s,
    not a different lag. Searching only +/-1.55 s keeps the answer unambiguous.
    A positive lag means the channel leads engine speed.
    """
    lag, c = xcorr(x, r, DT, MAX_LAG)
    j, k = int(np.argmax(c)), int(np.argmin(c))
    i = j if abs(c[j]) >= abs(c[k]) else k
    return float(c[i]), float(lag[i])


def report(data, chan, a, b, label):
    x, r = pair(data, chan, a, b)
    if x is None:
        print(f"  {label:<34} not sampled together in this window")
        return
    fx, px = spectrum(x)
    fr, pr = spectrum(r)
    c, lag = phase(x, r)
    lead = "leads" if lag > 0 else ("lags" if lag < 0 else "in phase with")
    print(f"  {label:<34} n={len(x):5d}")
    print(f"      channel  p2p {x.max()-x.min():8.3f}   dominant {fx:.3f} Hz = {px:.2f} s")
    print(f"      rpm      p2p {r.max()-r.min():8.1f}   dominant {fr:.3f} Hz = {pr:.2f} s")
    print(f"      r = {c:+.3f} at {lag:+.2f} s  ->  channel {lead} engine speed")


def main() -> None:
    d1 = load(LOGS / "20260905_030915.csv.gz")
    d3 = load(LOGS / "20260905_041723.csv.gz")

    print("=" * 72)
    print("SPARK vs ENGINE SPEED   (log 20260905_030915, 17 Hz both channels)")
    print("=" * 72)
    report(d1, "Timing advance (°)", 910, 1050, "Park idle 03:24:52-03:27:12")
    report(d1, "Timing advance (°)", 1050, 1233, "Park idle 03:27:12-03:30:15")
    report(d1, "Timing advance (°)", 800, 900, "Drive idle 03:23:03-03:24:43")

    print()
    print("=" * 72)
    print("COMMANDED AIR/FUEL vs ENGINE SPEED   (log 20260905_041723)")
    print("=" * 72)
    for a, b in ((2180, 2400), (2400, 2600), (2600, 2800), (2800, 2980)):
        report(d3, "Fuel/Air commanded equivalence ratio ()", a, b,
               f"Park idle window {a}-{b}s")

    print()
    print("=" * 72)
    print("EVERYTHING ELSE THE PCM DRIVES")
    print("=" * 72)
    report(d3, "Throttle Position Actually (°)", 1872, 2032, "Throttle, Park idle")
    report(d3, "Commanded evaporative purge (%)", 735, 871, "Purge, Park idle")

    print()
    print("=" * 72)
    print("PARK vs DRIVE, same session, minutes apart")
    print("=" * 72)
    tr, vr = d1["Engine RPM (rpm)"]
    for a, b, name in ((800, 900, "Drive"), (910, 1233, "Park")):
        grid = np.arange(tr[0] + a, tr[0] + b, DT)
        r = on_grid(tr, vr, grid, 0.5)
        r = r[np.isfinite(r)]
        spans = [r[i:i + 200].max() - r[i:i + 200].min()
                 for i in range(0, len(r) - 200, 200)]
        f, p = spectrum(r)
        print(f"  {name:<6} mean {r.mean():6.1f} rpm   sd {r.std():5.2f}   "
              f"10 s spans median {np.median(spans):4.1f} "
              f"(min {min(spans):.0f}, max {max(spans):.0f})   {f:.3f} Hz = {p:.2f} s")


if __name__ == "__main__":
    main()
