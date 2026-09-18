"""Rate of change of engine speed at idle, at a FIXED bandwidth.

Why: what pushes an engine against its mounts is reaction torque, which is
proportional to angular ACCELERATION, not to the size of the speed swing.
Every metric in this project so far measured the swing. The owner's current
symptom - a small vibration that accompanies engine speed CHANGING - points at
the derivative instead.

Why the fixed bandwidth matters: a raw difference quotient is dominated by the
sample interval.  The 2023 control gave 60.3 rpm/s in one session and 90.0 in
another ON THE SAME EVENING, purely because one was logged at 0.130 s and the
other at 0.049 s.  Any comparison across sessions MUST fix the bandwidth first.

Method: interpolate onto a uniform grid, smooth with a fixed-width window, and
differentiate over a fixed time step, so every session is measured through the
same filter whatever its raw rate.
"""
import sys, os, glob
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from carscanner_lib import load

sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent))
from _repo import ROOT, utf8, data_globs   # Windows + cwd safety

GRID_HZ = 10.0     # uniform resample rate
SMOOTH_S = 0.3     # moving-average width - sets the bandwidth
STEP_S = 0.3       # differentiation interval
MAX_GAP_S = 1.0    # a grid point spanning a larger hole is invented, not measured
MIN_RATE_HZ = 4.0  # a session sampled slower than this cannot be filtered to it


def idle_rate(t, v, idle, band=0.08):
    """Return |d(rpm)/dt| samples at a fixed bandwidth, idle only."""
    t = np.asarray(t, float); v = np.asarray(v, float)
    if np.median(np.diff(t)) > 1.0 / MIN_RATE_HZ:
        return None
    grid = np.arange(t[0], t[-1], 1.0 / GRID_HZ)
    y = np.interp(grid, t, v)
    # BUG FIXED 2026-09-17: np.interp draws a straight line across any gap in the
    # source, and a straight line has almost no rate of change.  On the 09-17 log
    # 44 % of the grid fell inside a 47 min hole and dragged the median from
    # 12.50 rpm/s down to 1.82.  Only keep grid points that sit between two real
    # samples less than MAX_GAP_S apart.
    real = np.zeros(len(grid), bool)
    for i in np.where(np.diff(t) < MAX_GAP_S)[0]:
        real |= (grid >= t[i]) & (grid <= t[i + 1])
    w = max(3, int(SMOOTH_S * GRID_HZ) | 1)
    y = np.convolve(y, np.ones(w) / w, mode='same')
    k = max(1, int(STEP_S * GRID_HZ))
    r = (y[k:] - y[:-k]) / (k / GRID_HZ)
    mid = (y[k:] + y[:-k]) / 2
    lo, hi = idle * (1 - band), idle * (1 + band)
    ok = (mid > lo) & (mid < hi) & real[:len(mid)]
    # drop the smoother's edge transients
    ok[:w] = False; ok[-w:] = False
    return np.abs(r[ok]) if ok.sum() > 100 else None


def load_any(path):
    """Return (time, rpm) from either a Car Scanner export or an f150diag log."""
    import csv as _csv
    with open(path, newline='', encoding='utf-8', errors='replace') as fh:
        head = fh.readline()
    if 'elapsed_s' in head:                      # f150diag's own recorder
        t, v = [], []
        with open(path, newline='', encoding='utf-8', errors='replace') as fh:
            for row in _csv.DictReader(fh):
                try:
                    r = float(row['rpm'])
                except (KeyError, TypeError, ValueError):
                    continue
                t.append(float(row['elapsed_s'])); v.append(r)
        return (np.array(t), np.array(v)) if len(t) > 50 else None
    d = load(path)                                # Car Scanner export
    k = next((k for k in d if k.startswith('Engine RPM (')), None)
    return d[k] if k else None


def sessions(paths, skipped=None):
    """Yield analysable sessions.  `skipped` collects (path, reason) pairs.

    A file dropped in silence is the same failure this tool already had once:
    at the truck you record, run this, get an empty table and no idea why.
    Every rejection now says which gate it failed, so a short or non-idle
    capture is obvious instead of invisible.
    """
    note = (lambda p, why: skipped.append((p, why))) if skipped is not None else \
           (lambda p, why: None)
    for p in paths:
        if not os.path.isfile(p) or not any(p.endswith(e) for e in ('.csv', '.csv.gz', '.zip')):
            continue
        try:
            got = load_any(p)
        except Exception as exc:                      # noqa: BLE001
            note(p, 'could not be read (%s)' % type(exc).__name__)
            continue
        if got is None:
            note(p, 'no Engine RPM column, or fewer than 50 rows')
            continue
        t, v = got
        v = np.asarray(v, float)
        if len(v) < 500:
            note(p, 'only %d engine-speed samples, need 500 (about 15 s at 33 Hz)' % len(v))
            continue
        run = v[v > 400]
        if len(run) < 300:
            note(p, 'only %d samples with the engine running, need 300' % len(run))
            continue
        idle = np.median(run[run < 900])
        if not (520 < idle < 720):
            note(p, 'median idle %.0f rpm is outside 520-720 - not a settled Park idle' % idle)
            continue
        r = idle_rate(t, v, idle)
        if r is None:
            note(p, 'no stretch long enough at idle after the gap and bandwidth filters')
            continue
        yield p, idle, np.median(np.diff(t)), r


def main(paths=None):
    # BUG FIXED 2026-09-18: this ignored sys.argv and always re-ran the historical
    # sweep, while CLAUDE.md and docs/LOCAL-SETUP.md both document
    # `python3 data/rpm_rate.py logs/<file>.csv`.  At the truck that printed a
    # tidy table of OLD sessions and silently said nothing about the capture just
    # taken - the worst kind of failure, because it looks like it worked.
    # `logs/` is in the default sweep now too, so local captures are never missed.
    print('ENGINE SPEED RATE OF CHANGE AT IDLE, fixed %.1f s bandwidth\n' % SMOOTH_S)
    print('  session                          n     median   90th pct   idle   raw dt')
    out = []
    skipped = []
    if not paths:
        paths = sorted(p for g in data_globs() for p in glob.glob(g, recursive=True))
    for p, idle, dt, r in sessions(paths, skipped):
        ctl = 'control-2023' in p or '20260906_17' in p or '20260906_18' in p
        out.append((ctl, os.path.basename(p)[:30], len(r), np.median(r),
                    np.percentile(r, 90), idle, dt))
    for ctl, n, cnt, med, p90, idle, dt in sorted(out, key=lambda x: (x[0], x[3])):
        print('  %-30s %6d  %7.2f   %7.2f  %6.1f  %.3f%s'
              % (n, cnt, med, p90, idle, dt, '   <- 2023 CONTROL' if ctl else ''))
    if skipped and len(skipped) <= 12:
        print('\n  not analysed:')
        for p, why in skipped:
            print('    %-30s %s' % (os.path.basename(p)[:30], why))
    elif skipped:
        print('\n  %d files not analysed (pass them by name to see why)' % len(skipped))
    a = [x[3] for x in out if not x[0]]
    b = [x[3] for x in out if x[0]]
    print()
    if a and b:
        print('  2014 median %.2f rpm/s (%d sessions)  |  2023 control %.2f (%d)  |  ratio %.2fx'
              % (np.median(a), len(a), np.median(b), len(b), np.median(a) / np.median(b)))
        print('\n  raw dt now spans %.3f-%.3f s across these sessions and the numbers no'
              % (min(x[6] for x in out), max(x[6] for x in out)))
        print('  longer track it - that is the point of the fixed bandwidth.')


if __name__ == '__main__':
    utf8()                 # Windows console/pipe safety - see data/_repo.py
    main(sys.argv[1:] or None)
