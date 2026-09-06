"""Does the felt vibration pulse in time with the measured rpm oscillation?

The engine speed oscillates at 0.304 Hz — one cycle every 3.0 seconds. That is
far too slow to be felt as vibration. But if the FAST vibration (the firing
pulse at ~32.5 Hz, or engine rock at ~10 Hz) gets stronger and weaker in time
with it, then the slow oscillation is reaching the seat after all — as amplitude
modulation rather than as motion the body can feel directly.

That is the one measurement that would join the two symptoms this project has
kept separate. This script tests it.

Method:
  1. Read a phyphox raw accelerometer export.
  2. Identify the engine orders present (half, first, firing).
  3. Take the amplitude envelope of the fast vibration.
  4. Take the spectrum OF THAT ENVELOPE. A peak at 0.304 Hz means the shake
     pulses in time with the engine-speed oscillation.

Run:  python3 data/analyze_accelerometer.py <export.csv> [rpm]
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

RPM_HUNT_HZ = 0.304          # measured engine-speed oscillation


def read_phyphox(path: Path):
    """Return (t, magnitude). Handles phyphox's several export layouts."""
    text = Path(path).read_text(encoding="utf-8-sig", errors="replace")
    delim = ";" if text.splitlines()[0].count(";") > text.splitlines()[0].count(",") else ","
    rows = list(csv.DictReader(text.splitlines(), delimiter=delim))
    if not rows:
        raise SystemExit("empty file")
    head = {k.lower().strip(): k for k in rows[0] if k}

    def col(*names):
        for n in names:
            for low, real in head.items():
                if low.startswith(n):
                    return real
        return None

    tcol = col("time", "t (")
    if tcol is None:
        raise SystemExit(f"no time column found in: {list(head.values())}")

    acol = col("absolute", "magnitude", "a (")
    xs = col("linear acceleration x", "acceleration x", "x (")
    ys = col("linear acceleration y", "acceleration y", "y (")
    zs = col("linear acceleration z", "acceleration z", "z (")

    def num(r, c):
        try:
            return float((r.get(c) or "").replace(",", "."))
        except (TypeError, ValueError):
            return np.nan

    t = np.array([num(r, tcol) for r in rows])
    if acol:
        a = np.array([num(r, acol) for r in rows])
    elif xs and ys and zs:
        a = np.sqrt(sum(np.array([num(r, c) for r in rows]) ** 2 for c in (xs, ys, zs)))
    else:
        raise SystemExit(f"no acceleration column found in: {list(head.values())}")

    ok = np.isfinite(t) & np.isfinite(a)
    return t[ok], a[ok]


def spectrum(x, fs, fmin, fmax):
    y = (x - x.mean()) * np.hanning(len(x))
    f = np.fft.rfftfreq(len(y), 1 / fs)
    p = np.abs(np.fft.rfft(y))
    band = (f >= fmin) & (f <= fmax)
    return f[band], p[band]


def envelope(x, fs, lo, hi):
    """Amplitude envelope of the band lo-hi Hz, by rectify and low-pass."""
    f = np.fft.rfftfreq(len(x), 1 / fs)
    X = np.fft.rfft(x - x.mean())
    X[(f < lo) | (f > hi)] = 0
    band = np.fft.irfft(X, n=len(x))
    rect = np.abs(band)
    # low-pass the rectified signal at 2 Hz to leave only the slow envelope
    F = np.fft.rfft(rect)
    ff = np.fft.rfftfreq(len(rect), 1 / fs)
    F[ff > 2.0] = 0
    return np.fft.irfft(F, n=len(rect))


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    path = Path(sys.argv[1])
    rpm = float(sys.argv[2]) if len(sys.argv) > 2 else 652.0

    t, a = read_phyphox(path)
    fs = 1.0 / np.median(np.diff(t))
    print(f"{path.name}: {len(a)} samples, {t[-1]-t[0]:.1f} s, {fs:.1f} Hz "
          f"(Nyquist {fs/2:.1f} Hz)")
    print(f"assumed engine speed {rpm:.0f} rpm\n")

    orders = {"half order (one cylinder differing)": rpm / 120,
              "first order (rotational imbalance)": rpm / 60,
              "second order": rpm / 30,
              "third order = FIRING pulse": rpm / 20}

    print("ENGINE ORDERS IN THE VIBRATION")
    f, p = spectrum(a, fs, 1.0, min(120.0, fs / 2 - 1))
    floor = np.median(p)
    for name, hz in orders.items():
        if hz > f.max():
            print(f"  {name:38s} {hz:6.2f} Hz  above the measurable range")
            continue
        w = (f > hz * 0.94) & (f < hz * 1.06)
        pk = p[w].max() if w.any() else 0.0
        at = f[w][int(np.argmax(p[w]))] if w.any() else float("nan")
        print(f"  {name:38s} {hz:6.2f} Hz  peak {pk:8.3f} at {at:6.2f} Hz"
              f"   {pk/floor:5.1f}x the noise floor"
              f"   {'<-- PRESENT' if pk > 3*floor else ''}")

    biggest = f[int(np.argmax(p))]
    print(f"\n  strongest peak overall: {biggest:.2f} Hz "
          f"= engine order {biggest/(rpm/60):.2f}")

    print("\nDOES IT PULSE EVERY 3 SECONDS?")
    for lo, hi, label in ((rpm/20*0.8, min(rpm/20*1.2, fs/2-1), "firing pulse"),
                          (8.0, 15.0, "engine rock band"),
                          (1.0, min(60.0, fs/2-1), "everything")):
        if hi <= lo:
            continue
        env = envelope(a, fs, lo, hi)
        ef, ep = spectrum(env, fs, 0.1, 1.5)
        i = int(np.argmax(ep))
        w = (ef > RPM_HUNT_HZ*0.85) & (ef < RPM_HUNT_HZ*1.15)
        at_hunt = ep[w].max() if w.any() else 0.0
        base = np.median(ep)
        verdict = ("YES - the shake pulses in time with the rpm oscillation"
                   if at_hunt > 3 * base and abs(ef[i] - RPM_HUNT_HZ) < 0.06
                   else "no clear modulation at the rpm-oscillation frequency")
        print(f"  {label:18s} envelope peaks at {ef[i]:5.3f} Hz "
              f"(period {1/ef[i]:4.1f} s), {ep[i]/base:4.1f}x floor")
        print(f"  {'':18s} at 0.304 Hz specifically: {at_hunt/base:4.1f}x floor  -> {verdict}")


if __name__ == "__main__":
    main()
