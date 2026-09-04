"""
Turning a log into a finding.

Pure Python on purpose — a few hundred samples does not need numpy, and the
tool has to run on whatever laptop is standing next to the truck.

The two questions this module exists to answer:

  1. Is the rpm movement normal control behaviour, or a real oscillation?
     Scatter and a periodic hunt look identical to the eye and completely
     different to an autocorrelation.

  2. Does fuel control lead the rpm, or follow it? Leading means fuel control
     is causing the instability. Following means something else disturbs the
     engine and fuel control is only reacting — dilution or mechanical.

No live-data screen answers either one. That is the whole reason to log.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, asdict
from statistics import fmean, pstdev
from typing import Sequence

Sample = dict[str, float | None]

#: Below this peak-to-peak, a periodic rpm ripple is closed-loop idle control
#: doing its job, not a hunt worth chasing.
RPM_HUNT_MIN_P2P = 30.0


# ---------------------------------------------------------------------------
# Basic statistics
# ---------------------------------------------------------------------------

@dataclass
class Series:
    name: str
    n: int
    mean: float
    sd: float
    minimum: float
    maximum: float

    @property
    def p2p(self) -> float:
        return round(self.maximum - self.minimum, 3)

    def as_dict(self) -> dict:
        d = asdict(self)
        d["p2p"] = self.p2p
        return d


def column(samples: Sequence[Sample], name: str) -> list[float]:
    """Every non-missing value of one channel, in order."""
    return [s[name] for s in samples if s.get(name) is not None]


def describe(samples: Sequence[Sample], name: str) -> Series | None:
    values = column(samples, name)
    if len(values) < 2:
        return None
    return Series(
        name=name,
        n=len(values),
        mean=round(fmean(values), 3),
        sd=round(pstdev(values), 3),
        minimum=round(min(values), 3),
        maximum=round(max(values), 3),
    )


# ---------------------------------------------------------------------------
# Periodicity — scatter versus a hunt
# ---------------------------------------------------------------------------

@dataclass
class Periodicity:
    periodic: bool
    period_s: float | None
    strength: float             # 0..1, peak normalised autocorrelation
    note: str


def autocorrelation(values: Sequence[float], max_lag: int) -> list[float]:
    """Normalised autocorrelation of the de-meaned series, lags 0..max_lag."""
    n = len(values)
    mean = fmean(values)
    dev = [v - mean for v in values]
    denom = sum(d * d for d in dev)
    if denom <= 0:
        return [0.0] * (max_lag + 1)
    out = []
    for lag in range(max_lag + 1):
        acc = sum(dev[i] * dev[i + lag] for i in range(n - lag))
        out.append(acc / denom)
    return out


def find_periodicity(values: Sequence[float], dt: float,
                     min_strength: float = 0.35,
                     min_p2p: float = 0.0) -> Periodicity:
    """
    Look for a repeating oscillation that is large enough to matter.

    Random control scatter decorrelates immediately: every lag beyond the
    first is near zero. A hunt keeps returning to the same phase, so its
    autocorrelation shows a clear positive peak at the hunt period.

    `min_p2p` gates on amplitude, and it is not optional in practice. Idle
    control is a closed loop, so it always oscillates a little; a perfectly
    regular two-rpm ripple is textbook correct behaviour, not a fault. Without
    an amplitude floor the detector reports every healthy engine as hunting.
    """
    n = len(values)
    if n < 20 or dt <= 0:
        return Periodicity(False, None, 0.0, "too few samples to judge")

    amplitude = max(values) - min(values)
    if amplitude < min_p2p:
        return Periodicity(False, None, 0.0,
                           f"oscillation amplitude {amplitude:.1f} is below the "
                           f"{min_p2p:.0f} threshold — normal closed-loop ripple")

    max_lag = n // 2
    acf = autocorrelation(values, max_lag)

    # Skip the monotonic decay off lag 0: start after the first zero crossing.
    start = 1
    while start < len(acf) and acf[start] > 0:
        start += 1

    best_lag, best = 0, 0.0
    for lag in range(start, max_lag):
        if acf[lag] > best:
            best, best_lag = acf[lag], lag

    if best >= min_strength and best_lag > 0:
        return Periodicity(True, round(best_lag * dt, 3), round(best, 3),
                           "repeating oscillation — a hunt, not scatter")
    return Periodicity(False, None, round(best, 3),
                       "no repeating structure — consistent with control scatter")


# ---------------------------------------------------------------------------
# Lead / lag — who is causing what
# ---------------------------------------------------------------------------

@dataclass
class LeadLag:
    a: str
    b: str
    lag_s: float | None
    correlation: float
    verdict: str


def cross_correlate(a: Sequence[float], b: Sequence[float], max_lag: int) -> list[tuple[int, float]]:
    """Normalised cross-correlation for lags -max_lag..+max_lag."""
    n = min(len(a), len(b))
    a, b = list(a[:n]), list(b[:n])
    ma, mb = fmean(a), fmean(b)
    da = [x - ma for x in a]
    db = [x - mb for x in b]
    na = math.sqrt(sum(x * x for x in da))
    nb = math.sqrt(sum(x * x for x in db))
    if na == 0 or nb == 0:
        return [(0, 0.0)]

    out = []
    for lag in range(-max_lag, max_lag + 1):
        acc = 0.0
        for i in range(n):
            j = i + lag
            if 0 <= j < n:
                acc += da[i] * db[j]
        out.append((lag, acc / (na * nb)))
    return out


def lead_lag(samples: Sequence[Sample], a: str, b: str, dt: float,
             max_lag_s: float = 3.0) -> LeadLag | None:
    """
    Does channel `a` move before channel `b`?

    Positive lag means `a` leads. For (stft, rpm): stft leading says fuel
    control is driving the instability; rpm leading says fuel control is
    merely responding to a disturbance it did not create.
    """
    va, vb = column(samples, a), column(samples, b)
    if len(va) < 20 or len(vb) < 20 or dt <= 0:
        return None

    max_lag = max(1, int(max_lag_s / dt))
    pairs = cross_correlate(va, vb, min(max_lag, len(va) // 3))
    lag, corr = max(pairs, key=lambda p: abs(p[1]))

    if abs(corr) < 0.3:
        verdict = "no meaningful relationship"
    elif lag > 0:
        verdict = f"{a} leads {b} — {a} is driving"
    elif lag < 0:
        verdict = f"{b} leads {a} — {a} is reacting"
    else:
        verdict = "simultaneous — cannot separate cause from effect"

    return LeadLag(a=a, b=b, lag_s=round(lag * dt, 3),
                   correlation=round(corr, 3), verdict=verdict)


# ---------------------------------------------------------------------------
# Metrics for protocol branch conditions
# ---------------------------------------------------------------------------

def sample_interval(samples: Sequence[Sample]) -> float:
    """Median time between samples, in seconds."""
    times = [s["elapsed_s"] for s in samples if s.get("elapsed_s") is not None]
    if len(times) < 2:
        return 0.0
    gaps = sorted(t2 - t1 for t1, t2 in zip(times, times[1:]) if t2 > t1)
    return gaps[len(gaps) // 2] if gaps else 0.0


def metrics(samples: Sequence[Sample]) -> dict[str, float | bool]:
    """
    Flatten a measurement into names a protocol condition can test.

    Produces `<channel>_mean`, `_sd`, `_p2p`, `_min`, `_max` for every channel
    present, plus rpm periodicity and the fuel-control lead/lag verdict.
    """
    out: dict[str, float | bool] = {}
    if not samples:
        return out

    channels = {k for s in samples for k, v in s.items()
                if v is not None and isinstance(v, (int, float))}
    channels -= {"elapsed_s"}

    for name in channels:
        stats = describe(samples, name)
        if stats is None:
            continue
        out[f"{name}_mean"] = stats.mean
        out[f"{name}_sd"] = stats.sd
        out[f"{name}_p2p"] = stats.p2p
        out[f"{name}_min"] = stats.minimum
        out[f"{name}_max"] = stats.maximum

    dt = sample_interval(samples)
    out["sample_dt"] = round(dt, 4)
    out["sample_count"] = len(samples)

    rpm = column(samples, "rpm")
    if rpm:
        per = find_periodicity(rpm, dt, min_p2p=RPM_HUNT_MIN_P2P)
        out["rpm_periodic"] = per.periodic
        out["rpm_period_s"] = per.period_s if per.period_s is not None else 0.0
        out["rpm_periodic_strength"] = per.strength

    # Oxygen sensor switching. A healthy upstream sensor crosses the
    # stoichiometric line several times a second; a sensor damaged by
    # "cleaning" goes slow or parks mid-range and stops crossing at all.
    for channel in ("o2_b1s1_v", "o2_b2s1_v", "o2_b1s2_v", "o2_b2s2_v"):
        values = column(samples, channel)
        if len(values) < 10 or dt <= 0:
            continue
        crossings = sum(
            1 for a, b in zip(values, values[1:])
            if (a - 0.45) * (b - 0.45) < 0
        )
        span = len(values) * dt
        out[f"{channel}_switch_hz"] = round(crossings / span, 3) if span else 0.0
        out[f"{channel}_parked"] = crossings == 0

    ll = lead_lag(samples, "stft_b1", "rpm", dt)
    if ll:
        out["stft_leads_rpm"] = (ll.lag_s or 0) > 0
        out["stft_rpm_corr"] = ll.correlation

    # Mean of both banks, when both are present — the number that matters most.
    for kind in ("ltft", "stft"):
        b1 = out.get(f"{kind}_b1_mean")
        b2 = out.get(f"{kind}_b2_mean")
        if b1 is not None and b2 is not None:
            out[f"{kind}_mean"] = round((b1 + b2) / 2, 3)
            out[f"{kind}_split"] = round(abs(b1 - b2), 3)
    return out


# ---------------------------------------------------------------------------
# Reference thresholds
# ---------------------------------------------------------------------------

#: Interpretation limits. Sources are stated because a threshold with no
#: provenance is just an opinion with a number attached.
THRESHOLDS = {
    "rpm_p2p_normal": (60.0, "±25-50 rpm of wander is normal closed-loop idle control"),
    "rpm_p2p_fault": (100.0, "±100 rpm or a rhythmic hunt is a real fault"),
    "ltft_normal": (10.0, "within ±10% means no leak significant enough to matter"),
    "ltft_high": (15.0, "double-digit positive that shrinks at 2500 rpm = unmetered air"),
    "trim_split": (8.0, "banks differing by more than this narrows to one bank"),
    "o2_switch_hz": (1.0, "a healthy upstream sensor crosses several times per second"),
}


def idle_verdict(m: dict) -> tuple[str, str]:
    """Reduce idle metrics to a verdict and the reasoning behind it."""
    p2p = m.get("rpm_p2p")
    if p2p is None:
        return "unknown", "no rpm data"

    periodic = bool(m.get("rpm_periodic"))
    if periodic:
        return ("fault",
                f"rpm oscillates with a {m.get('rpm_period_s')} s period "
                f"(strength {m.get('rpm_periodic_strength')}) — a hunt, not scatter")
    if p2p >= THRESHOLDS["rpm_p2p_fault"][0]:
        return "fault", f"rpm peak-to-peak {p2p} rpm exceeds the {THRESHOLDS['rpm_p2p_fault'][0]} rpm threshold"
    if p2p <= THRESHOLDS["rpm_p2p_normal"][0]:
        return ("normal",
                f"rpm peak-to-peak {p2p} rpm, no periodic structure — "
                "normal closed-loop idle control")
    return ("borderline",
            f"rpm peak-to-peak {p2p} rpm sits between the normal and fault "
            "thresholds — repeat the measurement and compare against another truck")
