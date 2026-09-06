"""Trace the shape of one rpm oscillation, averaged over hundreds of cycles.

Individual cycles are noisy. Ensemble-averaging them on a phase axis - each
cycle stretched to a common length, then averaged - recovers the shape that
repeats and cancels what does not. Whatever survives 900 cycles is real.

Cycle boundaries are upward crossings of the mean after the slow drift is
removed with a 20 s moving mean, which is long compared with the 3 s cycle and
short compared with the drift. Cycles shorter than 2 s or longer than 4.5 s are
rejected as mis-detections.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from carscanner_lib import load, on_grid  # noqa: E402

DT = 0.05
LOGS = Path(__file__).parent / "carscanner"


def movmean(x: np.ndarray, n: int) -> np.ndarray:
    if n % 2 == 0:
        n += 1
    c = np.cumsum(np.insert(x.astype(float), 0, 0))
    out = np.full(len(x), np.nan)
    h = n // 2
    out[h:len(x) - h] = (c[n:] - c[:-n]) / n
    return out


def cycles(data, a, b, other=None, bins=36):
    tr, vr = data["Engine RPM (rpm)"]
    grid = np.arange(tr[0] + a, tr[0] + b, DT)
    r = on_grid(tr, vr, grid, 0.5)
    x = on_grid(*data[other], grid, 0.5) if other else None
    ok = np.isfinite(r) & (np.isfinite(x) if other else True)
    r, g = r[ok], grid[ok]
    x = x[ok] if other else None

    osc = r - movmean(r, int(20 / DT))
    xo = x - movmean(x, int(20 / DT)) if other else None
    m = np.isfinite(osc) & (np.isfinite(xo) if other else True)
    osc, g = osc[m], g[m]
    xo = xo[m] if other else None

    smooth = np.nan_to_num(movmean(osc, int(0.5 / DT)))
    up = np.where((smooth[:-1] < 0) & (smooth[1:] >= 0))[0]

    q = np.linspace(0, 1, bins, endpoint=False)
    stack_r, stack_x, periods = [], [], []
    for i in range(len(up) - 1):
        t0, t1 = g[up[i]], g[up[i + 1]]
        if not (2.0 < t1 - t0 < 4.5):
            continue
        seg = (g >= t0) & (g < t1)
        if seg.sum() < 25:
            continue
        ph = (g[seg] - t0) / (t1 - t0)
        stack_r.append(np.interp(q, ph, osc[seg]))
        if other:
            stack_x.append(np.interp(q, ph, xo[seg]))
        periods.append(t1 - t0)
    return np.array(stack_r), (np.array(stack_x) if other else None), np.array(periods)


def main() -> None:
    d0 = load(LOGS / "2026-09-04 22-23-38.zip")
    S, _, per = cycles(d0, 4200, 7900)
    mean, sem, n = S.mean(0), S.std(0) / np.sqrt(len(S)), len(S)
    print(f"HOT PARK IDLE, 62 minutes, pre-repair — {n} cycles")
    print(f"  period  mean {per.mean():.3f} s  median {np.median(per):.3f}  "
          f"sd {per.std():.3f} ({100*per.std()/per.mean():.0f} % jitter)")
    lo, hi = int(np.argmin(mean)), int(np.argmax(mean))
    print(f"  averaged cycle: peak at phase {hi/len(mean):.2f}, trough at {lo/len(mean):.2f}, "
          f"amplitude {np.ptp(mean):.1f} rpm, SEM +/-{sem.mean():.2f}")
    slope = np.diff(np.concatenate([mean, mean[:1]])) / (np.median(per) / len(mean))
    print(f"  steepest rise {slope.max():+.1f} rpm/s, steepest fall {slope.min():+.1f} rpm/s "
          f"-> the rise is {abs(slope.max()/slope.min()):.1f}x steeper")
    print(f"  fraction of the cycle spent rising: {((hi - lo) % len(mean))/len(mean):.2f}")

    print("\n  phase   rpm deviation")
    for i in range(0, len(mean), 2):
        bar = int(round((mean[i] - mean.min()) / np.ptp(mean) * 44))
        print(f"   {i/len(mean):4.2f}  {mean[i]:+6.2f}  |{' ' * bar}*")

    for path, a, b, chan, label in (
        ("20260905_030915.csv.gz", 910, 1233, "Timing advance (°)", "SPARK"),
        ("20260905_041723.csv.gz", 2180, 2980,
         "Fuel/Air commanded equivalence ratio ()", "COMMANDED AIR/FUEL"),
    ):
        d = load(LOGS / path)
        S, X, per = cycles(d, a, b, other=chan)
        mr, mx = S.mean(0), X.mean(0)
        print(f"\n{label} against the same cycle — {len(S)} cycles")
        print(f"  rpm    amplitude {np.ptp(mr):5.2f}   peak at phase "
              f"{np.argmax(mr)/len(mr):.2f}, trough at {np.argmin(mr)/len(mr):.2f}")
        print(f"  signal amplitude {np.ptp(mx):5.3f}   peak at phase "
              f"{np.argmax(mx)/len(mx):.2f}, trough at {np.argmin(mx)/len(mx):.2f}")


if __name__ == "__main__":
    main()
