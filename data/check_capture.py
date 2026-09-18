"""Judge a Car Scanner capture THE MOMENT IT COMES OFF THE PHONE.

Every wasted capture in this project failed the same way: the file did not
contain what the question needed, and nobody noticed for days.

  * 74 tiles on the page -> `[PCM] Currently Detected Engine Misfire` got 1
    sample, knock sensors 2 and 1, `Timing advance` 2.
  * `Engine RPM` had a 47.5-minute hole covering the ENTIRE window in which all
    six cylinder channels were polled - so the one per-cylinder window this
    project had ever obtained was unreadable.
  * Two of four captures on 2026-09-14 recorded no engine channel at all.
  * Four findings came from comparing channels that were never polled together.

So this does not analyse anything.  It asks, of ONE file: which of the open
questions can this answer, and if not, exactly why not.  Run it at the truck,
while the engine is still warm and the capture can be repeated.

    python data/check_capture.py <file.csv>
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _repo import utf8
from carscanner_lib import load

IDLE_LO, IDLE_HI = 600.0, 700.0
GUARD_S = 2.0
PAIR_TOL = 0.15
GAP_S = 1.0

# Each question: what it needs, how densely, and for how long.
QUESTIONS = [
    dict(n=1, name='The hiccups - what makes the engine stumble',
         need=['Engine RPM (', '[PCM] Currently Detected Engine Misfire'],
         idle_min=20.0, rate_hz=15.0, pair=True),
    dict(n=2, name='The oxygen sensor swap - which bank needs more fuel',
         need=['Short term fuel % trim - Bank 1', 'Short term fuel % trim - Bank 2',
               'Engine RPM ('],
         idle_min=2.0, rate_hz=3.0, pair=True, no_throttle=True),
    dict(n=3, name='Post-tune engine-speed baseline (orders, rate, events)',
         need=['Engine RPM ('],
         idle_min=4.0, rate_hz=25.0, pair=False),
    dict(n=4, name='Per-cylinder contribution',
         need=['Engine RPM (', '[PCM] Cylinder'],
         idle_min=0.8, rate_hz=10.0, pair=True),
    dict(n=5, name='Knock sensors compared at a known idle',
         need=['[PCM] Knock Sensor 1', '[PCM] Knock Sensor 2'],
         idle_min=0.0, rate_hz=1.0, pair=True),
    dict(n=6, name='Is manifold pressure really blank on this truck',
         need=['Engine RPM (', 'Manifold absolute pressure'],
         idle_min=0.5, rate_hz=1.0, pair=True),
]


def find(d, prefix):
    return [k for k in d if k.startswith(prefix)]


def series(d, prefix):
    ks = find(d, prefix)
    if not ks:
        return None
    t, v = d[ks[0]]
    return ks[0], np.asarray(t, float), np.asarray(v, float)


def rate(t):
    return 1.0 / np.median(np.diff(t)) if len(t) > 2 else 0.0


def best_rate(t, window=60.0):
    """Fastest sustained rate over any `window` seconds, not the file median.

    A file's median rate understates what it holds.  The 2026-09-04 log medians
    16.7 Hz, but contains 33 Hz stretches - and the whole engine-order analysis
    came out of those stretches.  Judging the file by its median would throw
    away the part that answers the question.
    """
    if len(t) < 3:
        return 0.0, 0.0
    best, best_at = 0.0, 0.0
    lo = 0
    for hi in range(len(t)):
        while t[hi] - t[lo] > window:
            lo += 1
        span = t[hi] - t[lo]
        if span >= window * 0.9:
            hz = (hi - lo) / span
            if hz > best:
                best, best_at = hz, t[lo]
    return best, best_at


def idle_mask(tr, vr, t):
    """True where an engine-speed sample within GUARD_S confirms settled idle."""
    out = np.zeros(len(t), bool)
    for i, T in enumerate(t):
        lo = np.searchsorted(tr, T - GUARD_S)
        hi = np.searchsorted(tr, T + GUARD_S)
        w = vr[lo:hi]
        out[i] = len(w) > 1 and w.min() > IDLE_LO and w.max() < IDLE_HI
    return out


def paired(ta, tb, tol=PAIR_TOL):
    n = 0
    for T in ta:
        k = np.searchsorted(tb, T)
        if any(0 <= j < len(tb) and abs(tb[j] - T) <= tol for j in (k - 1, k)):
            n += 1
    return n


def main(path):
    utf8()
    d = load(path)
    print('\n%s' % Path(path).name)
    print('=' * 78)

    # --- what is in the file, and how fast -----------------------------
    fast = []
    for k, (t, v) in d.items():
        t = np.asarray(t, float)
        if len(t) > 2 and rate(t) >= 1.0:
            fast.append((k, len(t), rate(t)))
    fast.sort(key=lambda x: -x[2])
    print('\nCHANNELS POLLED AT 1 Hz OR MORE: %d' % len(fast))
    for k, n, hz in fast[:14]:
        print('   %-52s n=%-7d %6.1f Hz' % (k[:52], n, hz))
    if len(fast) > 14:
        print('   ... and %d more' % (len(fast) - 14))

    # The rate law: tiles on screen set the rate.
    expect = {1: 33.3, 2: 32.9, 3: 15.5, 4: 10.9, 5: 8.0, 6: 8.0}.get(len(fast))
    if expect:
        print('\n   %d tiles -> the rate law predicts about %.1f Hz.' % (len(fast), expect))
    elif len(fast) > 6:
        print('\n   %d tiles is well past the cliff. Expect about 2 Hz, and the app'
              % len(fast))
        print('   CHOOSES which channels actually get polled - usually not the ones')
        print('   you care about. Two tiles; three only when engine speed must prove')
        print('   the condition.')

    # --- engine speed, the channel everything else is judged against ----
    r = series(d, 'Engine RPM (')
    if r is None:
        print('\nENGINE RPM: ABSENT.')
        print('   Nothing in this file can be read, because no capture can be')
        print('   trusted without the engine state that proves the condition.')
        return 1
    _, tr, vr = r
    gaps = np.diff(tr)
    big = gaps[gaps > GAP_S]
    idle = idle_mask(tr, vr, tr)
    idle_min = idle.sum() / rate(tr) / 60 if rate(tr) else 0
    bhz, bat = best_rate(tr)
    print('\nENGINE RPM: n=%d, median %.1f Hz, span %.1f min'
          % (len(tr), rate(tr), (tr[-1] - tr[0]) / 60))
    print('   best sustained rate over any 60 s: %.1f Hz (starting %.0f s in)'
          % (bhz, bat - tr[0]))
    print('   range %.0f-%.0f rpm' % (vr.min(), vr.max()))
    print('   guard-band-clean idle (%g-%g rpm): %.1f min' % (IDLE_LO, IDLE_HI, idle_min))
    if len(big):
        print('   *** %d GAPS OVER %.0f s, TOTALLING %.1f MIN - largest %.1f min ***'
              % (len(big), GAP_S, big.sum() / 60, big.max() / 60))
        print('   A gap is invisible in the app and fatal to the analysis. Any channel')
        print('   polled only inside a gap has NO engine state and cannot be read.')

    # --- can this file answer anything? --------------------------------
    print('\nWHAT THIS CAPTURE CAN ANSWER')
    print('-' * 78)
    any_pass = False
    for q in QUESTIONS:
        have, missing = [], []
        for pre in q['need']:
            s = series(d, pre)
            (have if s else missing).append((pre, s))
        if missing:
            print('  %d. %-46s NO' % (q['n'], q['name'][:46]))
            print('        missing: %s' % ', '.join(m[0].rstrip(' (') for m in missing))
            continue

        reasons = []
        for pre, s in have:
            k, t, v = s
            hz, at = best_rate(t)
            if hz < q['rate_hz']:
                reasons.append('%s best sustained %.1f Hz, needs %.0f'
                               % (k[:34], hz, q['rate_hz']))
            m = idle_mask(tr, vr, t)
            mins = m.sum() / hz / 60 if hz else 0
            if mins < q['idle_min']:
                reasons.append('%s has %.1f min at confirmed idle, needs %.1f'
                               % (k[:34], mins, q['idle_min']))
        if q.get('pair') and len(have) > 1:
            base = have[0][1]
            for pre, s in have[1:]:
                n = paired(base[1], s[1])
                if n < 30:
                    reasons.append('%s and %s share only %d samples within %.2f s'
                                   % (base[0][:22], s[0][:22], n, PAIR_TOL))
        if reasons:
            print('  %d. %-46s NO' % (q['n'], q['name'][:46]))
            for x in reasons[:3]:
                print('        %s' % x)
        else:
            any_pass = True
            print('  %d. %-46s YES' % (q['n'], q['name'][:46]))
            if q.get('no_throttle'):
                print('        (check the throttle was never touched - the bank')
                print('         difference reverses sign under throttle movement)')

    print('-' * 78)
    if not any_pass:
        print('\nTHIS CAPTURE ANSWERS NOTHING ON THE LIST.')
        print('Re-take it while the engine is still warm. Two tiles, stay on that')
        print('page, screen awake, phone left alone. See docs/IDLE-LOG-LIST.md.')
    return 0


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    raise SystemExit(max(main(p) for p in sys.argv[1:]))
