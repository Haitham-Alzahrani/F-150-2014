# Engine scorecard and electrical investigation

2026-09-06. Every figure from the four Car Scanner logs (135,000+ samples) unless
marked otherwise. Bank 1 = passenger side, cylinders 1, 2, 3. Bank 2 = driver
side, cylinders 4, 5, 6.

---

## PART 1 — ENGINE SCORECARD

Rated against the best reference available for each item, with the reference's
authority stated. **A grade is only as good as its reference**, so the source
column matters as much as the verdict.

### Combustion and mixture

| Item | Your value | Standard | Source | Grade |
|---|---|---|---|---|
| Lambda at idle | **0.998** | 1.000 | Physics | **A+** |
| Long term trim, Bank 1 (passenger) | **−0.781 %** on all 1,535 samples | ±10 % fails, ±5 % investigate | Community | **A+** |
| Long term trim, Bank 2 (driver) | **−0.781 %** on all 1,470 samples | as above | Community | **A+** |
| Upstream sensors, bank to bank | **0.007 AFR apart** (6,695 paired samples) | <0.3 typical | Community | **A+** |
| Short term trim spread, bank to bank | **−0.79 % to +2.33 %**, wanders | >3–5 % investigate | Guide, Level 3 | **B** |
| Commanded dither amplitude | ±1.54 % before, ±1.58 % after repair | normal Ford fore/aft control | Technical | **A** |
| Misfire rate, 200 and 1000 revolutions | **0.000 %** both | limit 0.949 % / 30.976 % | Ford, Mode 06 | **A+** |
| Per-cylinder misfire counts | cyl 4 = 2, cyl 6 = 1, rest 0 | 3 events in ~88,000 firings = 0.003 % | Ford, Mode 06 | **A+** |
| Fuel system monitor, both banks | **0.000** | limit 0.797 | Ford, Mode 06 | **A+** |

### Breathing and mechanical

| Item | Your value | Standard | Source | Grade |
|---|---|---|---|---|
| Volumetric efficiency at WOT | **100–108 %**, peak 104.6 % | 85–100 % healthy NA | Engineering | **A+** |
| Absolute load at WOT | **96.47 %** | 90–100 % healthy | Guide | **A+** |
| Peak airflow | **215.27 g/s** | ~170–210 for 302 hp | Rule of thumb | **A+** |
| Airflow curve shape | **smooth to the limiter, no plateau** | a plateau means restriction | Engineering | **A+** |
| Estimated power | **303 hp** (283–323, ±7 %) | 302 hp rated | Ford | **A+** |
| Brake specific fuel consumption | **0.46 lb/hp·hr** | 0.45–0.50 typical NA | Engineering | **A** |
| Rev limiter reached | **6,832 rpm**, clean pull | — | — | **A+** |
| Idle airflow | 3.00 g/s = **3.32 g/s** density-corrected | 3.17–3.63 observed | Guide, Level 3 | **A** |
| Cam phaser error, both banks | **0.06° / 0.05°** | limit **20°** | Ford, Mode 06 | **A+** |

### Ignition

| Item | Your value | Standard | Source | Grade |
|---|---|---|---|---|
| Timing at Park idle | **12.05°**, sd 1.14 (n=11,456) | 13–17 community; **no Ford spec exists** | Community | **A−** |
| Spark authority used | **−7.0° to +40.0°** = 47° | full range, no clipping | Measured | **A+** |
| Knock retard, idle | **0.000°**, all 38 samples | 0 expected | — | **A** |
| Knock retard, under load | **NEVER SAMPLED** | — | — | **not graded** |
| Octane adaptation before the wipe | **−0.5999** | −1 best, +1 worst | COBB, community | **A** |

### Exhaust and aftertreatment

| Item | Your value | Standard | Source | Grade |
|---|---|---|---|---|
| Catalyst monitor, Bank 1 (passenger) | **0.3711** | limit 0.8359 — **55.6 % margin** | Ford, Mode 06 | **A** |
| Catalyst monitor, Bank 2 (driver) | **0.3633** | limit 0.8359 — **56.5 % margin** | Ford, Mode 06 | **A** |
| Bank to bank catalyst difference | **2.1 %** | <10 % | Engineering | **A** |
| Upstream O2 response, both banks | **0.014 s** | limit **0.4 s** | Ford, Mode 06 | **A+** |
| Downstream O2 response | 0.792 / 0.856 s | limit **10 s** | Ford, Mode 06 | **A+** |
| Injector sealing on overrun | pegged 29.3826 AFR, **sd exactly 0.00000** for 46.5 s | any leak stops the peg | Measured | **A+** |

### Idle quality

| Item | Your value | Standard | Source | Grade |
|---|---|---|---|---|
| Idle speed, Park | **651.8 rpm**, same across 4 sessions | 550–750 typical | Guide | **A+** |
| Idle speed, in gear | 550.18 rpm (sd 4.26) | Ford commands lower in gear | Technical | **A+** |
| Peak-to-peak, Park, A/C off | **38 rpm** (p10 28, p90 52) | ≥30–<40 Acceptable | Guide, Level 3 | **C** |
| Peak-to-peak, Park, A/C cycling | **69 rpm** | ≥50 Poor by size | Guide, Level 3 | **D** |
| Peak-to-peak, in gear | **14.8 rpm** | <20 Perfect | Guide, Level 3 | **A+** |
| Character of the movement | **rhythmic 0.304 Hz, holds for hours** | rhythmic = hunting by definition | Guide, Level 3 | **D** |
| Spark swing at idle | 1.75–4.0° peak-to-peak | ≤4° Excellent | Guide, Level 3 | **A** |

### Transmission and driveline

| Item | Your value | Standard | Source | Grade |
|---|---|---|---|---|
| Gear ratios, derived from the data | within **2 %** of published, all gears | 4.17 / 2.34 / 1.52 / 1.14 / 0.87 / 0.69 | Ford | **A+** |
| Upshift quality | **13 shifts, zero engine flare on every one** | any flare = clutch slip | Engineering | **A+** |
| Shift times | 0.15–0.54 s | typical | Engineering | **A** |
| Converter slip, 5th | +0.93 % | controlled slip by design | Ford | **A** |
| Converter lockup, 6th | locks | — | — | **A+** |
| Adaptive repeatability | two coast-downs 60 s apart, **same ratios, same times** | — | Guide 4C.1 | **A+** |

**Overall: this engine grades A to A+ on every measurement that has a real
standard behind it.** The only C and D grades are on the idle-stability table,
whose values the guide's own authors label as observed heuristics they could not
corroborate — and the D for character, which is a real observation.

---

## PART 2 — ELECTRICAL: voltage drop, shorts, harness

### What the logs CAN say

**Charging regulation is excellent.** Sixty ten-second means spanning **51 mV
over 11 minutes**. A failing regulator or a worn brush would not hold that.

**Voltage is not in the idle hunt.** Correlation with engine speed across three
windows: **r = −0.006, +0.085, −0.031** — no relationship at all. Only 1.5–4.9 %
of voltage variance sits in the 0.25–0.4 Hz band. **Whatever drives the idle
oscillation, it is not electrical.**

**Charging behaviour is Ford smart charging working correctly.** 13.857 V and
+0.886 A while charging, falling to 12.894 V and −0.017 A once the battery
reached 90 % state of charge. That is the strategy reducing alternator drag, not
a fault.

**No pattern of harness glitching.** Every channel was scanned for isolated
single-sample spikes — a value jumping and immediately returning, which is the
signature an intermittent connector or a chafed wire leaves in data. The only
channels flagged are ones whose entire range is one or two quantisation steps
(the cam phaser moves 0.062° in total, so every step it takes counts as a
"spike"), plus 5–7 events in 7,500–17,400 samples on two others, which is 0.03 to
0.2 %. **That is normal data, not a wiring fault.**

**One genuine dropout, once.** Bank 2's upstream air/fuel sensor (driver side)
read exactly **0.000 for 26 consecutive samples — 1.5 seconds — at 04:01:49**,
during a deceleration. One occurrence in 5,684 samples, and Mode 06 timed that
same sensor at 0.014 s against a 0.4 s limit. **Almost certainly a data artefact.
Worth a second look only if it repeats.**

### What the logs CANNOT say — and why

**A voltage-drop test is impossible from this data.** The three voltage sources
are polled in **separate bursts that never overlap in time**:

| Source | When it was sampled |
|---|---|
| OBD port | 22:24–22:24, 22:31, 22:39–22:51, 23:00–23:01, … |
| PCM supply | 22:32, 23:59–00:03, 00:23, 00:57 |
| BCM battery | 22:33–22:39, 00:58–01:05 |

At a ±5 second tolerance there are **zero** simultaneous points. Widening to
±120 seconds gives 77 matches, and those show the OBD port reading **0.163 V**
above the PCM supply and the BCM reading **0.098 V** above it. **Those numbers
must not be read as voltage drops** — two minutes apart, with charging voltage
drifting, is not a simultaneous measurement.

**Ripple cannot be measured at all.** Alternator diode ripple is at hundreds of
hertz. The fastest channel in any log is 30 Hz. **This is a physics limit.**

**Shorts and chafing cannot be seen.** A short to ground, a chafed wire or a
corroded pin shows as a resistance change under vibration or heat. Nothing in a
data stream reveals it unless it is actually failing at the moment of logging.

### THE ELECTRICAL TESTS THAT DO SETTLE IT — with a multimeter

You need a digital multimeter. Each test is a few minutes.

#### Test E1 — AC ripple across the battery
**Why:** a failed alternator diode injects AC ripple onto the 12 V rail. Every
sensor reference on the engine rides on that rail, so ripple makes the PCM see
noise on the crank sensor, the MAF and the oxygen sensors at once.

1. Engine running, warm, idle, all electrical loads OFF.
2. Meter on **AC volts**, lowest range.
3. Black probe to battery negative post, red to positive post.
4. Read it. Then switch the headlights and blower on and read again.

| Reading | Verdict |
|---|---|
| **under 0.05 V AC** | Excellent |
| 0.05–0.10 V AC | Acceptable |
| **over 0.10 V AC** | One or more diodes failing. Replace the alternator |
| over 0.5 V AC | Severe. It will affect sensor readings |

#### Test E2 — Ground voltage drops
**Why:** a bad ground makes the engine's electrical reference float. It is the
single most common cause of unexplained sensor misbehaviour, and it does not set
a code.

Engine idling, **loads ON** (headlights, blower on max, rear demist). Meter on
**DC millivolts**.

| Measure between | Limit |
|---|---|
| Battery negative post → engine block | **under 0.1 V (100 mV)** |
| Engine block → chassis / frame | **under 0.1 V** |
| Battery negative post → chassis | **under 0.1 V** |
| Battery negative post → alternator case | **under 0.1 V** |
| **Any one of them over 0.2 V** | **That connection is bad. Clean it.** |

**How to clean one:** disconnect the battery negative first. Undo the strap,
wire-brush both the terminal and the surface it bolts to down to bright metal,
refit, torque, and put a light film of dielectric grease over the outside — not
between the mating faces.

#### Test E3 — Positive-side drop
Same method, DC millivolts, engine running with loads on:

| Measure between | Limit |
|---|---|
| Alternator B+ output stud → battery positive post | **under 0.2 V** |

Above that, the main charging cable or its connections are resistive.

#### Test E4 — Wiggle test on the engine harness
**Why:** this is the test that finds a chafed wire or a loose pin, and nothing in
a datalog can substitute for it.

1. Engine idling, warm. Put `Engine RPM` on the scan tool graph where you can
   see it.
2. Work through these connectors **one at a time**. For each: grip the connector
   body and push, pull and rock it, then flex the harness 15 cm either side of it.

   * **Crankshaft position sensor** — this one first. It is the signal every
     other conclusion depends on.
   * Camshaft position sensors (four on this engine, two per bank)
   * Mass airflow sensor
   * Throttle body
   * All six ignition coils
   * All six injectors
   * Both upstream oxygen sensors
   * The main engine-harness-to-body connectors
   * Every ground strap you found in Test E2

3. **Any rpm movement, stumble, or change in engine note as you move a
   connector or a harness section is the fault.** Mark that spot.

4. Then look at the harness itself where it passes near anything hard or hot:
   exhaust manifolds, the alternator bracket, the power steering pump, the
   transmission bellhousing, any body edge. **You are looking for a shiny spot,
   a flattened section, melted insulation, or a section of tape that has gone
   hard and split.** Jeddah heat destroys harness tape and loom.

#### Test E5 — Independent engine speed
**Why:** every rpm number in this entire investigation is the PCM's own reading
from the crankshaft sensor. If that signal is noisy, the PCM would believe the
speed is wandering and correct for a phantom — and that correction would make
the engine genuinely oscillate.

Use a **timing light with a tachometer function** on the crankshaft pulley at
warm idle, and compare its reading against the scan tool.

| Result | Verdict |
|---|---|
| Both steady and equal | The crank signal is honest. Hypothesis dead |
| **Timing light steady, scan tool wandering** | **The crank signal is lying. That is the fault** |
| Both wandering together | The engine really is oscillating. Signal is fine |

**Note:** one of the five analyses found that **first order is absent from the
engine-speed spectrum** — its frequency sits at the noise floor in all 14 windows
tested. A defective reluctor or a marginal crank sensor would normally put energy
there. **That is the first quantitative evidence against this hypothesis**, but
it is indirect. Test E5 is direct and settles it.

---

## PART 3 — CAN ANYTHING IN THE LOGS CAUSE A SHAKE?

**Simulated from the measured data.** Taking the engine's rotating inertia at the
crankshaft as **0.20 kg·m²** [ASSUMED, typical for this class — the conclusion is
not sensitive to it within the plausible 0.15–0.30 range]:

| Quantity | Value |
|---|---|
| Engine speed oscillation | ±9.10 rpm |
| Angular acceleration during it | ±1.967 rad/s², peak 16.87 |
| **Net torque imbalance driving the hunt** | **±0.39 N·m, peak 3.37 N·m** |
| Engine torque at idle, from the measured 1.02 L/h fuel rate | **~27 N·m** |
| **The hunt as a fraction of engine torque** | **1.45 %** |
| Each combustion event, peak torque | **~218 N·m**, three times per crank revolution |
| **Firing pulse compared with the hunt** | **about 550× larger** |

**Read that last line carefully.** The thing you can measure through the
diagnostic port is **one five-hundredth** of the force of a single combustion
event. It moves a needle. It cannot move a person.

**What you feel in the seat is the firing pulse, or the engine rocking on its
mounts, and the logs cannot see either.** At about 17 samples per second the
fastest thing they resolve is 8.3 Hz; the firing pulse is 32.5 Hz and engine rock
is 8–15 Hz. **No tool connected to that port will ever answer this question.**

**Nothing found in any log is capable of causing a felt shake.** Not the idle
oscillation, not the mixture, not the spark, not the voltage. That is not a
failure of the investigation — it is the correct and final answer from this
instrument, and it is why the accelerometer, the mounts and the contact points
are the only work left.
