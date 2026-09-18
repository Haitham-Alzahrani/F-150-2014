"""PCM `Control module voltage` against BCM `[BCM] Vehicle Battery Voltage`.

CLAUDE.md has carried this as the one absolute criterion the truck FAILS:
`Control module voltage` reads 12.49-12.77 V with the engine running, against
13.0-14.8 expected.  It is explained away with Ford smart charging and "a BCM
reading of 13.8 V", and then correctly doubted, because the file also records
that the supply channels were never polled together.

THEY REALLY WERE NEVER POLLED TOGETHER - and not by accident.  In the one
session carrying both, they share a 145-minute span and coincide ZERO times,
even at a 30 s tolerance.  Two channels on different pages of the app are never
polled simultaneously (the tiles law), and if the adapter also switches between
HS-CAN and MS-CAN - the PCM is on HS-CAN, the BCM on MS-CAN - then simultaneous
sampling is physically impossible, not merely unlucky.

So an instant-by-instant comparison cannot be made from any log that exists.
What CAN be compared is their DISTRIBUTIONS over the same window with the
engine confirmed running, which is a weaker but honest test - and it is enough,
because the two do not overlap.

    python3 data/voltage_compare.py
"""
import glob
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from carscanner_lib import load

sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent))
from _repo import ROOT, utf8, data_globs   # Windows + cwd safety

PCM_KEY = 'Control module voltage'
BCM_KEY = '[BCM] Vehicle Battery Voltage'
CHARGING = (13.5, 14.5)      # what a healthy charging system should show
RUNNING = 400.0


def main():
    for p in sorted(q for g in data_globs() for q in glob.glob(g, recursive=True)):
        if not os.path.isfile(p) or not any(p.endswith(e) for e in ('.csv', '.csv.gz', '.zip')):
            continue
        try:
            d = load(p)
        except Exception:
            continue
        pk = next((k for k in d if k.startswith(PCM_KEY)), None)
        bk = next((k for k in d if k.startswith(BCM_KEY)), None)
        rk = next((k for k in d if k.startswith('Engine RPM (')), None)
        if not (pk and bk and rk):
            continue

        tp, vp = (np.asarray(x, float) for x in d[pk])
        tb, vb = (np.asarray(x, float) for x in d[bk])
        tr, vr = (np.asarray(x, float) for x in d[rk])
        print('\n%s' % os.path.basename(p))

        # 1. Can they be paired at all?
        for tol in (0.15, 1.0, 5.0, 30.0):
            n = 0
            for T in tp:
                k = np.searchsorted(tb, T)
                if any(0 <= j < len(tb) and abs(tb[j] - T) <= tol for j in (k - 1, k)):
                    n += 1
            print('  simultaneous samples within %5.2f s : %d' % (tol, n))

        # 2. Distributions over each channel's own window, engine confirmed running.
        print('  %-6s %6s %8s %8s %8s %8s %10s' %
              ('', 'n', 'median', 'p10', 'p90', 'max', 'in 13.5-14.5'))
        for nm, t, v in (('PCM', tp, vp), ('BCM', tb, vb)):
            m = (tr >= t[0]) & (tr <= t[-1])
            if m.sum() == 0 or (vr[m] > RUNNING).mean() < 0.99:
                print('  %-6s engine not confirmed running for this window' % nm)
                continue
            inband = 100 * ((v >= CHARGING[0]) & (v <= CHARGING[1])).mean()
            print('  %-6s %6d %8.2f %8.2f %8.2f %8.2f %9.1f %%' %
                  (nm, len(v), np.median(v), *np.percentile(v, [10, 90]), v.max(), inband))
        print('  (engine speed %.0f-%.0f rpm across both windows)'
              % (vr.min(), vr[vr > RUNNING].max()))


if __name__ == '__main__':
    utf8()                 # Windows console/pipe safety - see data/_repo.py
    main()
