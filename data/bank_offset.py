"""Bank fuel offset across every session that polled both short term trims.

THE RULE THIS TOOL EXISTS TO ENFORCE:  a bank difference in SHORT TERM trim
alone is meaningless once LONG TERM has learned, because the two halves trade
off - CLAUDE.md records this ("when long term rises, short term falls by the
same amount").  The only comparable quantity is the TOTAL correction,
short + long, same bank, same instant.

Every sample is selected by its OWN condition - an engine speed sample within
NEAR_S confirming settled idle - never by a time window bounded by qualifying
samples, which sweeps in throttle blips and flips the sign.
"""
import glob, re, sys
import numpy as np

sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
from carscanner_lib import load

PAIR_TOL  = 0.15   # s, between the two banks' short term samples
NEAR_S    = 1.0    # s, how close a confirming sample must be
IDLE_LO, IDLE_HI = 600.0, 700.0
GUARD_S   = 2.0    # every engine speed sample within +/- this must also be idle.
                   # Selecting on the centre sample alone admits blip recovery:
                   # the engine passes through 650 rpm on its way down from 1300.
MIN_N     = 30

SWAP_T = '20260916'   # all four oxygen sensors swapped side for side on this date


def datestamp(name):
    """Filenames use three different date spellings across the project."""
    digits = re.sub(r'[^0-9]', '', name)
    return digits[:8] if len(digits) >= 8 else '00000000'


def near(T, ta, va, tol):
    k0 = np.searchsorted(ta, T)
    for k in (k0 - 1, k0):
        if 0 <= k < len(ta) and abs(ta[k] - T) <= tol:
            return va[k]
    return np.nan


def session(path):
    try:
        d = load(path)          # not every CSV here is a Car Scanner export
    except Exception:
        return None
    get = lambda k: next((d[c] for c in d if c.startswith(k)), None)
    s1, s2 = get('Short term fuel % trim - Bank 1'), get('Short term fuel % trim - Bank 2')
    l1, l2 = get('Long term fuel % trim - Bank 1'),  get('Long term fuel % trim - Bank 2')
    rpm    = get('Engine RPM (')
    if s1 is None or s2 is None:
        return None
    short, total, conf = [], [], []
    for i, T in enumerate(s1[0]):
        b2 = near(T, s2[0], s2[1], PAIR_TOL)
        if np.isnan(b2):
            continue
        ok = False
        if rpm is not None:
            r = near(T, rpm[0], rpm[1], NEAR_S)
            if not np.isnan(r) and IDLE_LO < r < IDLE_HI:
                lo = np.searchsorted(rpm[0], T - GUARD_S)
                hi = np.searchsorted(rpm[0], T + GUARD_S)
                w = rpm[1][lo:hi]
                ok = len(w) > 1 and w.min() > IDLE_LO and w.max() < IDLE_HI
        short.append(s1[1][i] - b2)
        conf.append(ok)
        if l1 is not None and l2 is not None:
            L1, L2 = near(T, l1[0], l1[1], NEAR_S), near(T, l2[0], l2[1], NEAR_S)
            total.append((s1[1][i] + L1) - (b2 + L2) if not np.isnan(L1 + L2) else np.nan)
        else:
            total.append(np.nan)
    return np.array(short), np.array(total), np.array(conf, bool)


def main(paths):
    print('BANK 1 MINUS BANK 2, positive = Bank 1 needs MORE fuel')
    print('"idle confirmed" = an Engine RPM sample within %.1f s reads %g-%g rpm\n' % (NEAR_S, IDLE_LO, IDLE_HI))
    print('%-46s %5s %8s %8s %6s %9s' % ('session', 'n', 'short', 'TOTAL', 'idle n', 'TOTAL@idle'))
    for p in paths:
        r = session(p)
        if r is None:
            continue
        short, total, conf = r
        if len(short) < MIN_N:
            continue
        ti = total[conf]
        ti = ti[~np.isnan(ti)]
        name = p.split('/')[-1].replace('.csv.gz', '').replace('.csv', '')
        era = 'POST' if datestamp(name) >= SWAP_T else 'pre '
        print('%-4s %-41s %5d %+8.3f %+8.3f %6d %9s'
              % (era, name[:41], len(short), np.nanmean(short), np.nanmean(total),
                 conf.sum(), '%+.3f' % ti.mean() if len(ti) >= MIN_N else '-'))


if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        # glob '**/*' with no extension filter: these logs are stored plain,
        # gzipped and zipped, and a '*.csv' sweep silently read 2 of 11 files.
        args = sorted(glob.glob('data/**/*', recursive=True))
    main(args)
