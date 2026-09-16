"""Order-track Engine RPM into the crank-angle domain.

Why this exists: CLAUDE.md ruled that the OBD port cannot see the felt shake,
on the basis that Car Scanner samples at ~17 Hz (Nyquist 8.3 Hz) while first
order at 650 rpm is 10.8 Hz.  That rate is now known to be wrong - one or two
tiles on screen gives 33 Hz, Nyquist 16.65 Hz.  Half order and first order are
inside that.  Firing order is not and never will be.

Resampling onto uniform crank angle turns engine orders into fixed lines
regardless of how the idle speed wanders, which plain FFT smears.

Usage: python3 data/order_track_rpm.py <log> [<log> ...]
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from carscanner_lib import load

SAMPLES_PER_REV = 3.0          # set by the 33 Hz rate against a ~650 rpm idle
MIN_STRETCH = 250              # samples; ~7.5 s at 33 Hz
GRID = np.arange(0.02, 1.50, 0.01)


def fast_stretches(t, v, max_dt=0.045, min_len=MIN_STRETCH):
    idx = np.where(np.diff(t) < max_dt)[0]
    if not len(idx):
        return []
    runs = np.split(idx, np.where(np.diff(idx) > 1)[0] + 1)
    return [(r[0], r[-1] + 1) for r in runs if len(r) >= min_len]


def order_spectrum(t, v):
    """Return (orders, power, revolutions) for one contiguous stretch."""
    t = np.asarray(t, float); v = np.asarray(v, float)
    rev = np.concatenate([[0], np.cumsum(v[:-1] / 60.0 * np.diff(t))])
    grid = np.arange(0, rev[-1], 1.0 / SAMPLES_PER_REV)
    y = np.interp(grid, rev, v)
    y = y - np.polyval(np.polyfit(np.arange(len(y)), y, 3), np.arange(len(y)))
    w = np.hanning(len(y)); y = y * w
    o = np.fft.rfftfreq(len(y), 1.0 / SAMPLES_PER_REV)
    P = np.abs(np.fft.rfft(y)) ** 2 / (w ** 2).sum()
    return o, P, rev[-1]


def line_ratio(g, A, lo, hi, halfwidth=25):
    """Peak in [lo,hi) against the local median background - a line test."""
    bg = np.array([np.median(A[max(0, i - halfwidth):i + halfwidth])
                   for i in range(len(A))])
    m = (g >= lo) & (g < hi)
    i = int(np.argmax(A * m))
    return A[i] / bg[i], g[i]


def main(paths):
    for p in paths:
        d = load(p)
        key = next((k for k in d if k.startswith('Engine RPM (')), None)
        if key is None:
            print('%s: no Engine RPM channel' % os.path.basename(p)); continue
        t, v = d[key]
        st = fast_stretches(t, v)
        print('\n%s' % os.path.basename(p))
        if not st:
            print('  no stretch at 33 Hz long enough to order-track')
            continue
        print('  %d stretches' % len(st))
        print('  %-9s %-7s %-16s %-16s' % ('stretch', 'revs', 'order 0.5', 'order 1.0'))
        rat5 = []
        for n, (a, b) in enumerate(st, 1):
            o, P, revs = order_spectrum(t[a:b], v[a:b])
            A = np.interp(GRID, o, P)
            r5, f5 = line_ratio(GRID, A, 0.44, 0.56)
            r1, f1 = line_ratio(GRID, A, 0.94, 1.06)
            rat5.append(r5)
            print('  %-9d %-7d %5.2fx @ %.3f   %5.2fx @ %.3f' % (n, revs, r5, f5, r1, f1))
        rat5 = np.array(rat5)
        print('  half order above 2x in %d of %d, median %.2fx'
              % ((rat5 > 2).sum(), len(rat5), np.median(rat5)))


if __name__ == '__main__':
    main(sys.argv[1:] or ['data/carscanner/2026-09-04 22-23-38.zip'])
