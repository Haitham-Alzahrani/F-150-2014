# ENGINE ORDERS IN THE RPM CHANNEL — the port reaches 10.8 Hz after all (2026-09-16)

**Analysis: [`data/order_track_rpm.py`](../data/order_track_rpm.py).**
Run it against any log; it finds the 33 Hz stretches by itself.

## Why this was worth redoing

`CLAUDE.md` rules in five separate places that the OBD port cannot see the felt
shake. Every one of those rulings rests on the same arithmetic:

> Car Scanner samples each channel at ~17 Hz (60 ms). Nyquist is **8.3 Hz**.
> Firing (32.5 Hz) and first order (10.8 Hz) are still invisible.

**That sample rate is wrong and has been known to be wrong since 2026-09-14.**
One or two tiles on screen gives **33.3 Hz**, so **Nyquist is 16.65 Hz**.
First order at 650 rpm is 10.8 Hz. **It is inside.** So is the whole 8–15 Hz
band in which an engine rocks on its mounts. Nobody went back and re-tested
after the rate law was established.

## Method

A plain spectrum smears engine orders, because idle speed wanders 621–700 rpm
and an order moves with it. Resampling onto **uniform crank angle** — integrate
engine speed to get revolutions elapsed, interpolate onto an even revolution
grid — turns each order into a fixed line whatever the speed does.

At 33.3 Hz against a 650 rpm idle that gives **3.07 samples per revolution**, so
orders up to **1.5** are reachable. **Half order (0.5) and first order (1.0) are
in. Firing order (3.0) is out and always will be** — it would need 65 Hz, above
the adapter's ceiling.

Each line is scored against a **local median background**, not against the
global noise floor, so the spectrum's natural rolloff cannot manufacture a peak.

## Result — both orders are present, and first order is REAL

Eleven stretches at 33 Hz exist in the whole project. Ten are warm Park idle in
the 09-04 log; one is 899.6 rpm in `2026-09-14_14-45-16`.

| Order | Lands at | Present | Line strength | **Amplitude** |
|---|---|---|---|---|
| **1.0 — first order** | **exactly 1.000, 11 of 11** | always | 1.87–6.80×, median 3.95× | **0.173 rpm** |
| **0.5 — half order** | 0.470–0.500 | 7 of 10 at idle, **absent at 900 rpm** | 1.46–8.82×, median 2.85× | **0.576 rpm** |

### First order is not an aliasing artefact — this is the part that matters

An order above the sampling ceiling folds down to a false low order, and where
it lands **depends on the sampling ratio**. That ratio is set by engine speed.

The 899.6 rpm stretch runs at **2.22 samples per revolution against 3.07** — a
**38 % different ratio**. A folded artefact would have moved. **First order
stayed on exactly 1.000, and gave its strongest line of the whole set, 6.52×.**

**First order content in engine speed is real, repeatable, and measurable
through the OBD port.** At 650 rpm it sits at **10.8 Hz**, inside the band that
rocks an engine on its mounts.

## What it does NOT mean — read before quoting any of this

**The amplitudes are tiny.** 0.173 rpm at first order and 0.576 at half order,
against a **19 rpm** slow oscillation and a **9.4 rpm** total idle standard
deviation. First order is roughly **110× smaller** than the 0.33 Hz breathing
this project has spent weeks on.

**That smallness is expected and is not evidence of a healthy engine.** Crank
speed is a poor transducer for a torque imbalance: the flywheel, flexplate and
converter inertia absorb a per-cylinder torque difference almost entirely, which
is exactly why it takes an accelerometer on the seat to feel what the crank
barely registers. **A small number here does not mean a small vibration at the
cab.** It means engine speed is the wrong end of the mechanism to measure it at.

**THERE IS NO CONTROL.** The 2023 has no 33 Hz stretch anywhere, so whether
0.173 rpm of first order is normal for a healthy engine is **unknown**. Every
reciprocating engine has some. Nothing here is abnormal until something
comparable is measured.

**The half order observation is weaker than the first order one.** It moves
around (0.470–0.500 rather than landing exact), it is absent in the one
higher-speed stretch, and the aliasing test that cleared first order has not
been passed for it — orders near 2.5 and 3.5 fold close to 0.5 at this sampling
ratio. **Treat it as a lead, not a measurement.**

## Why it is worth having anyway

**Every stretch above is from 2026-09-04 — before the mounts, before the
battery, before the intake gasket, before the oxygen sensors were swapped side
to side.** It is a clean pre-repair baseline in a band nobody has ever measured
on this truck, using a method that reruns in one command.

**A fresh capture is directly comparable**: same channel, same rate, same
analysis. That makes it the first metric in this project that (a) sits in the
frequency range of the actual complaint and (b) has a before-value already
banked.

## The capture that extends it

`Engine RPM` **alone on the page** — proven flat 30.0 ms — warm, Park,
standstill, air conditioning off, phone left alone with the screen awake.

1. **Five minutes at idle.** Compare first and half order against the table above.
2. **Two minutes held at about 1200 rpm.** At 1200 the ratio falls to 1.67
   samples per revolution. **Half order is still reachable and a fold would
   move.** This is the test that settles whether the half order line is genuine,
   and it is the one piece of the analysis the existing data cannot supply.
