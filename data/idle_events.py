"""Discrete events in engine speed at settled idle - the 'hiccup' metric.

The owner's symptom is small DISCRETE events, not the continuous 0.33 Hz
breathing this project has measured to death.  A hiccup and an oscillation are
different signals and need different detectors.

Method: resample to a common grid, remove everything below ~0.5 Hz (that is the
breathing), keep 0.5-5 Hz, and count excursions past a FIXED absolute threshold
so sessions with different sample rates and different amounts of idle stay
comparable.  A per-session sigma threshold would not be comparable - a quiet
session would flag its own noise.

Idle is required across the whole neighbourhood of an event, not just at its
centre, so a throttle blip cannot contribute.
"""
import sys, os, glob
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from carscanner_lib import load

FS = 1 / 0.060          # common grid
THRESH = 25.0           # rpm, fixed so sessions are comparable
MAX_GAP_S = 1.0         # a grid point spanning a bigger hole is invented
GUARD_S = 1.5           # idle must hold this far either side


def ma(x, n):
    n = max(1, int(n) | 1)
    return np.convolve(x, np.ones(n) / n, mode='same')


def analyse(t, v, idle_lo, idle_hi):
    t = np.asarray(t, float); v = np.asarray(v, float)
    if np.median(np.diff(t)) > 0.25:      # too slow to see a 0.25 s event
        return None
    g = np.arange(t[0], t[-1], 1 / FS)
    y = np.interp(g, t, v)
    # Same gap bug as rpm_rate.py, fixed 2026-09-17: np.interp invents a straight
    # line across any hole in the source.  A straight line produces no events, so
    # a gapped session would report an artificially LOW event rate.
    real = np.zeros(len(g), bool)
    for i in np.where(np.diff(t) < MAX_GAP_S)[0]:
        real |= (g >= t[i]) & (g <= t[i + 1])
    w = int(GUARD_S * FS)
    hi = np.array([y[max(0, i - w):i + w].max() for i in range(len(y))])
    lo = np.array([y[max(0, i - w):i + w].min() for i in range(len(y))])
    idle = (hi < idle_hi) & (lo > idle_lo) & real
    if idle.sum() < 60 * FS:              # need at least a minute of idle
        return None
    slow = ma(y, int(2.0 * FS))
    r = y - slow
    band = r - (r - ma(r, int(0.10 * FS)))
    idx = np.where((np.abs(band) > THRESH) & idle)[0]
    runs = [rr for rr in np.split(idx, np.where(np.diff(idx) > int(0.5 * FS))[0] + 1) if len(rr)]
    peaks = np.array([band[rr[np.argmax(np.abs(band[rr]))]] for rr in runs])
    mins = idle.sum() / FS / 60
    # NO SPACING METRIC HERE, DELIBERATELY - tried and removed 2026-09-18.
    # CLAUDE.md quoted "one every 84 s" and nothing computed it, so a median
    # inter-event spacing was added.  It cannot be measured on this data.
    # Idle is not one block: on the 09-04 log it is 94 separate stretches, so a
    # gap that would have been long is cut short by the end of its stretch.
    # Restricting to pairs inside one stretch drops 32 of 100 gaps and those are
    # the LONG ones - median falls to 9.6 s against 14.8 s for all gaps, and a
    # mean of 13.4 s against 85.3 s.  That is right-censoring, not a measurement.
    # Report the RATE, which divides events by idle time and is unaffected.
    # Reinstate only with a capture that holds unbroken idle for its whole length.
    stretches = 1 + int(np.sum(np.diff(idle.astype(int)) == 1))
    return dict(minutes=mins, n=len(peaks), per_min=len(peaks) / mins,
                dips=int((peaks < 0).sum()), rises=int((peaks > 0).sum()),
                median_size=float(np.median(np.abs(peaks))) if len(peaks) else 0.0,
                sd_band=float(band[idle].std()), stretches=stretches)


def main():
    print('DISCRETE IDLE EVENTS, fixed %.0f rpm threshold, 0.5-5 Hz band\n' % THRESH)
    print('  session                          idle min   events  per min   dips/rises  median  band sd  idle runs')
    out = []
    for p in sorted(glob.glob('data/carscanner/**/*', recursive=True) +
                    glob.glob('data/control-2023/**/*', recursive=True)):
        if not os.path.isfile(p) or not any(p.endswith(e) for e in ('.csv', '.csv.gz', '.zip')):
            continue
        try:
            d = load(p)
        except Exception:
            continue
        k = next((k for k in d if k.startswith('Engine RPM (')), None)
        if not k:
            continue
        t, v = d[k]
        v = np.asarray(v, float)
        run = v[v > 400]
        if len(run) < 2000:
            continue
        idle = np.median(run[run < 900])
        if not (520 < idle < 720):
            continue
        res = analyse(t, v, idle * 0.90, idle * 1.10)
        if res is None:
            continue
        ctl = 'control-2023' in p or '20260906_17' in p or '20260906_18' in p
        out.append((ctl, os.path.basename(p)[:28], res))
    for ctl, name, r in sorted(out, key=lambda x: (x[0], -x[2]['per_min'])):
        print('  %-28s %8.1f %8d %8.3f %6d/%-5d %7.1f %7.2f %9d%s'
              % (name, r['minutes'], r['n'], r['per_min'], r['dips'], r['rises'],
                 r['median_size'], r['sd_band'], r['stretches'],
                 '  <- 2023 CONTROL' if ctl else ''))
    a = [r['per_min'] for c, _, r in out if not c]
    b = [r['per_min'] for c, _, r in out if c]
    print()
    if a and b:
        print('  2014 median %.3f events/min (%d sessions)  |  2023 control %.3f (%d)'
              % (np.median(a), len(a), np.median(b), len(b)))


if __name__ == '__main__':
    main()
