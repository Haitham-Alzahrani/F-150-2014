"""Compare EVERY channel both trucks recorded at settled idle.

Owner asked whether anything is wrong with how the engine runs, explicitly not
limited to his complaint.  This is the unbiased sweep: take every parameter the
2014 and the 2023 both produced at settled idle and put them side by side.

Idle is defined per truck as +-8 % of that truck's own median idle, and a
channel sample counts only if an engine-speed sample within 1 s says the engine
was at idle then - so nothing from a blip or a drive can leak in.
"""
import sys, os, glob, pickle
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from carscanner_lib import load

BAND = 0.08
NEAR_S = 1.0
MIN_N = 30


def idle_samples(path):
    try:
        d = load(path)
    except Exception:
        return None
    k = next((k for k in d if k.startswith('Engine RPM (')), None)
    if not k:
        return None
    tr, vr = d[k]
    tr = np.asarray(tr, float); vr = np.asarray(vr, float)
    run = vr[vr > 400]
    if len(run) < 500:
        return None
    idle = float(np.median(run[run < 900]))
    if not (520 < idle < 720):
        return None
    ok = tr[(vr > idle * (1 - BAND)) & (vr < idle * (1 + BAND))]
    if len(ok) < 300:
        return None
    out = {}
    for ch, (tc, vc) in d.items():
        tc = np.asarray(tc, float); vc = np.asarray(vc, float)
        if len(vc) < MIN_N:
            continue
        j = np.searchsorted(ok, tc)
        near = np.zeros(len(tc), bool)
        for s in (-1, 0):
            jj = np.clip(j + s, 0, len(ok) - 1)
            near |= np.abs(ok[jj] - tc) < NEAR_S
        if near.sum() >= MIN_N:
            out[ch] = vc[near]
    return idle, out


def collect():
    g = {'2014': [], '2023': []}
    for p in sorted(glob.glob('data/carscanner/**/*', recursive=True) +
                    glob.glob('data/control-2023/**/*', recursive=True)):
        if not os.path.isfile(p) or not any(p.endswith(e) for e in ('.csv', '.csv.gz', '.zip')):
            continue
        r = idle_samples(p)
        if not r:
            continue
        who = '2023' if ('control-2023' in p or '20260906_17' in p or '20260906_18' in p) else '2014'
        g[who].append((os.path.basename(p), r[0], r[1]))
    return g


def pool(sessions, ch):
    v = [o[ch] for _, _, o in sessions if ch in o]
    return np.concatenate(v) if v else None


def main():
    g = collect()
    print('sessions with settled idle:  2014 = %d   2023 control = %d\n'
          % (len(g['2014']), len(g['2023'])))
    chans = sorted({c for _, _, o in g['2014'] for c in o} &
                   {c for _, _, o in g['2023'] for c in o})
    print('%d channels recorded at idle on BOTH trucks\n' % len(chans))
    print('  %-46s %19s %19s' % ('channel', '2014  med [sd]', '2023  med [sd]'))
    rows = []
    for ch in chans:
        a, b = pool(g['2014'], ch), pool(g['2023'], ch)
        if a is None or b is None:
            continue
        rows.append((ch, len(a), np.median(a), a.std(), len(b), np.median(b), b.std()))
    for ch, na, ma, sa, nb, mb, sb in rows:
        print('  %-46s %9.3f [%6.3f] %9.3f [%6.3f]' % (ch[:46], ma, sa, mb, sb))
    pickle.dump(g, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     '..', '.idle_sweep.pkl'), 'wb'))


if __name__ == '__main__':
    main()
