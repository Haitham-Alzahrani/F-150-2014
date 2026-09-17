"""Read the two short term fuel trim traces off a Car Scanner screenshot.

The two panels are drawn on DIFFERENT vertical scales, so comparing them by eye
is unsound - which is the specific error this project has made before. This
converts both to trim percent using the gridlines as calibration.
"""
import sys
import numpy as np
from PIL import Image

PANELS = [  # (name, top_row, bottom_row, value_at_top_row, value_at_bottom_row)
    ('Short term fuel % trim - Bank 1', 427, 1309,  3.6, -3.0),
    ('Short term fuel % trim - Bank 2', 1587, 2452, 3.4, -3.8),
]


def trace(a, y0, y1, x0, x1):
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    blue = (b > 120) & (b - r > 60) & (b - g > 30)
    out = {}
    for x in range(x0, x1):
        ys = np.where(blue[y0:y1, x])[0]
        if len(ys):
            out[x] = (ys.min() + y0, ys.max() + y0)
    return out


def main(path):
    a = np.asarray(Image.open(path).convert('RGB')).astype(int)
    series = []
    for name, ytop, ybot, vtop, vbot in PANELS:
        t = trace(a, ytop - 45, ybot + 20, 150, 1170)
        scale = (vbot - vtop) / (ybot - ytop)
        vals = {x: (vtop + (lo - ytop) * scale, vtop + (hi - ytop) * scale)
                for x, (lo, hi) in t.items()}
        series.append((name, vals))
        mids = np.array([(v[0] + v[1]) / 2 for v in vals.values()])
        print('%s: %d columns, visible range %.2f to %.2f %%'
              % (name, len(vals), min(v[1] for v in vals.values()),
                 max(v[0] for v in vals.values())))
    # compare column by column - same x pixel is the same instant in both panels
    (n1, s1), (n2, s2) = series
    common = sorted(set(s1) & set(s2))
    d = np.array([((s1[x][0] + s1[x][1]) / 2) - ((s2[x][0] + s2[x][1]) / 2)
                  for x in common])
    print('\n%d columns present in both panels' % len(common))
    print('Bank 1 minus Bank 2, per column:')
    print('  mean   %+.3f %%' % d.mean())
    print('  median %+.3f %%' % np.median(d))
    print('  sd      %.3f' % d.std(ddof=1))
    print('  Bank 1 higher in %.1f %% of columns' % (100 * (d > 0).mean()))
    n = len(d)
    se = d.std(ddof=1) / np.sqrt(n)
    print('  standard error %.3f, t = %.2f' % (se, d.mean() / se))
    print('\n  CAUTION: adjacent columns are not independent samples - one trim')
    print('  sample spans many pixels - so the t value above is inflated and must')
    print('  NOT be quoted as a significance test. The sign and size are the')
    print('  usable part.')
    return d


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1
         else 'data/sensor-swap-2026-09-17/stft-both-banks-0557.jpg')
