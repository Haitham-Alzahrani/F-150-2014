"""Per-cylinder contribution from the six [PCM] Cylinder N Acceleration Value channels.

This is the measurement the project has wanted since night one, and until the
2026-09-17 log there was never a window where all six were sampled together.

The previous attempt produced a false outlier: cylinder 6 spanned six to ten
times the others purely because it was the only channel still polled after a
throttle lift.  So idle is required across the whole NEIGHBOURHOOD of every
sample, not just at it - a blip anywhere near a sample disqualifies it.
"""
import sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from carscanner_lib import load

GUARD_S = 2.0          # idle must hold this far either side of a sample
IDLE_LO, IDLE_HI = 600, 700


def idle_mask(t_ch, t_rpm, v_rpm, guard=GUARD_S):
    """True where engine speed stayed inside the idle band right around t_ch."""
    out = np.zeros(len(t_ch), bool)
    for i, T in enumerate(t_ch):
        m = (t_rpm >= T - guard) & (t_rpm <= T + guard)
        if m.sum() >= 3 and v_rpm[m].min() > IDLE_LO and v_rpm[m].max() < IDLE_HI:
            out[i] = True
    return out


def main(path):
    d = load(path)
    t_rpm, v_rpm = d['Engine RPM (rpm)']
    t_rpm = np.asarray(t_rpm, float); v_rpm = np.asarray(v_rpm, float)
    ch = {}
    for i in range(1, 7):
        k = '[PCM] Cylinder %d Acceleration Value ()' % i
        if k not in d:
            continue
        t, v = d[k]
        ch[i] = (np.asarray(t, float), np.asarray(v, float))
    if len(ch) < 6:
        print('only %d cylinder channels present' % len(ch)); return
    lo = max(t[0] for t, _ in ch.values())
    hi = min(t[-1] for t, _ in ch.values())
    print('window where all six overlap: %.1f minutes\n' % ((hi - lo) / 60))
    print('  cyl      n   median     mean       sd     p5      p95   min     max')
    res = {}
    for i in range(1, 7):
        t, v = ch[i]
        m = (t >= lo) & (t <= hi)
        m &= idle_mask(t[m] if False else t, t_rpm, v_rpm)
        s = v[m]
        res[i] = s
        print('  %3d %6d %+8.4f %+8.4f %8.4f %+7.3f %+7.3f %+6.3f %+6.3f'
              % (i, len(s), np.median(s), s.mean(), s.std(),
                 np.percentile(s, 5), np.percentile(s, 95), s.min(), s.max()))
    means = np.array([res[i].mean() for i in range(1, 7)])
    print('\n  spread of the six means: %+.4f to %+.4f  (range %.4f)'
          % (means.min(), means.max(), means.ptp()))
    print('  weakest by mean: cylinder %d      strongest: cylinder %d'
          % (int(np.argmin(means)) + 1, int(np.argmax(means)) + 1))
    # is any cylinder separated from the pack beyond noise?
    from scipy import stats
    print('\n  each cylinder against the pooled other five:')
    for i in range(1, 7):
        others = np.concatenate([res[j] for j in range(1, 7) if j != i])
        u = stats.mannwhitneyu(res[i], others, alternative='two-sided')
        se = np.sqrt(res[i].var(ddof=1) / len(res[i]) + others.var(ddof=1) / len(others))
        print('    cyl %d  mean %+.4f vs %+.4f   diff %+.4f (se %.4f)   p = %.3g'
              % (i, res[i].mean(), others.mean(), res[i].mean() - others.mean(), se, u.pvalue))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1
         else 'data/carscanner/2026-09-17-full-page/2026-09-17_15-49-53.csv')
