"""Load Car Scanner horizontal CSV exports without inventing samples.

The app polls PIDs round-robin, so most cells in a row are blank. Blank means
"not sampled at this instant", not "unchanged" — every function here keeps each
channel on its own true sample times and never forward-fills.
"""
from __future__ import annotations

import csv
from pathlib import Path

import numpy as np


def parse_clock(raw: str) -> float:
    h, m, s = raw.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def load(path: Path) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    """Return {channel: (t_seconds, values)} using each channel's own samples."""
    text = Path(path).read_text(encoding="utf-8-sig", errors="replace")
    rows = list(csv.DictReader(text.splitlines()))
    headers = [h for h in rows[0].keys() if h and h != "time"]
    times = np.array([parse_clock(r["time"]) for r in rows])

    out: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for h in headers:
        idx, vals = [], []
        for i, r in enumerate(rows):
            raw = (r.get(h) or "").strip()
            if raw in ("", "-", "n/a", "N/A", "ERROR"):
                continue
            try:
                vals.append(float(raw.replace(",", ".")))
            except ValueError:
                continue
            idx.append(i)
        if idx:
            out[h] = (times[np.array(idx)], np.array(vals))
    return out


def rate(t: np.ndarray) -> float:
    """Median sample rate in Hz."""
    d = np.diff(t)
    d = d[d > 0]
    return float(1.0 / np.median(d)) if len(d) else float("nan")


def on_grid(t: np.ndarray, v: np.ndarray, grid: np.ndarray,
            max_gap: float) -> np.ndarray:
    """Linear interpolation onto `grid`, NaN wherever the nearest real samples
    straddle a gap wider than `max_gap`. Interpolating a continuously varying
    quantity between two nearby real samples is defensible; carrying a value
    across a long silence is not, and that is what the NaN prevents."""
    out = np.interp(grid, t, v, left=np.nan, right=np.nan)
    j = np.searchsorted(t, grid).clip(1, len(t) - 1)
    gap = t[j] - t[j - 1]
    out[gap > max_gap] = np.nan
    out[(grid < t[0]) | (grid > t[-1])] = np.nan
    return out


def segments(t: np.ndarray, keep: np.ndarray, min_len: float,
             max_gap: float = 2.0) -> list[tuple[float, float]]:
    """Contiguous runs where `keep` holds, as (start, end) in seconds."""
    runs, start, prev = [], None, None
    for ti, k in zip(t, keep):
        if k and start is None:
            start, prev = ti, ti
        elif k:
            if ti - prev > max_gap:
                if prev - start >= min_len:
                    runs.append((start, prev))
                start = ti
            prev = ti
        elif start is not None:
            if prev - start >= min_len:
                runs.append((start, prev))
            start = None
    if start is not None and prev - start >= min_len:
        runs.append((start, prev))
    return runs


def xcorr(a: np.ndarray, b: np.ndarray, dt: float, max_lag_s: float):
    """Cross-correlation of two equally sampled series after mean removal.

    Returns (lags_seconds, r). A peak at POSITIVE lag means `a` must be shifted
    forward to line up with `b` — that is, `a` LEADS `b`.
    """
    ok = np.isfinite(a) & np.isfinite(b)
    a, b = a[ok] - np.nanmean(a[ok]), b[ok] - np.nanmean(b[ok])
    n = int(round(max_lag_s / dt))
    denom = np.sqrt(np.sum(a * a) * np.sum(b * b))
    lags = np.arange(-n, n + 1)
    r = np.array([
        np.sum(a[max(0, -k):len(a) - max(0, k)] * b[max(0, k):len(b) - max(0, -k)])
        for k in lags
    ]) / denom
    return lags * dt, r
