# FULL SCAN OF EVERY READING — 2026-09-15

**Every numeric value in all 44 sessions of this truck, 129 channels, statistics
computed on raw samples rather than on the app's Min/Avg/Max.** The 2023 control
truck is excluded. Ranked by how much each finding is worth.

---

## 1. THE PCM RE-LEARNS AN ETHANOL CONTENT OF 19–22 % AFTER EVERY REFUEL — NEW

**`Ethanol fuel percent` takes exactly three values across every session ever
logged, and it moves at refuelling.**

| Session | `Ethanol fuel percent` | `Fuel level input (%)` | `Long term fuel % trim - Bank 1` | `- Bank 2` |
|---|---|---|---|---|
| 09-05 03:40 | **19.22 %** | 43.9–47.5 | −2.34 … 0.00 | −0.78 … 0.00 |
| 09-05 04:17 | **19.22 %** | 33.3–45.1 | −0.78 | −0.78 |
| 09-08 17:04 | **9.80 %** | 45.5–45.9 | −0.78 | — |
| 09-09 16:12 | **9.80 %** | 35.3 | 0.00 | 0.00 |
| 09-09 16:24 | **9.80 %** | 33.3–33.7 | 0.00 | 0.00 … +0.78 |
| 09-13 08:01 | **9.80 %** | 29.0–29.4 | −0.78 | −1.56 |
| **09-14 14:49** | **22.35 %** | **85.5–86.3** | **−2.34 … −0.78** | **−3.12 … −1.56** |

**The tank went from 29 % to 86 % between 09-13 and 09-14 — he refuelled — and the
ethanol estimate jumped 9.80 → 22.35 % across exactly that event.** The same thing
had happened before: 19.22 % on 09-05, also after fuelling.

**The three values are bytes 25, 49 and 57** on the standard `A × 100 ÷ 255`
scaling — 9.8039, 19.2157, 22.3529 %. Not noise. Three discrete learned states.

**And at 22.35 %, both banks' long term trims are the most negative in the entire
dataset.** That is the direction the mechanism predicts: a higher ethanol estimate
makes the PCM command more fuel, the oxygen sensors see rich, and trim pulls fuel
back out.

### Why this matters

**Saudi pump fuel is normally E0, and the owner buys 95 octane from the same
station every time.** This truck is flex-fuel capable; without a composition
sensor the PCM *infers* ethanol content from the fuel trim response after a fuel
level rise. If it is inferring 22 % on E0 fuel, it is targeting a stoichiometric
ratio near **13.5:1 instead of 14.7:1** — roughly **9 % more fuel commanded.**

Closed loop corrects it, which is what the negative trims are doing. **Open loop
does not:** the first 20 seconds of every cold start, and wide open throttle.

### What it does NOT yet establish

* **The fuel has not been tested.** Saudi 95 is normally E0 but that is an
  assumption here, not a measurement.
* **2–3 % of negative trim is less than a 22-point ethanol error should need.**
  Either the fuel does contain some ethanol, or the estimate error is smaller than
  its face value, or the inference feeds back on itself. Not resolved.
* **Direction is not proven.** The ethanol estimate is derived *from* fuel trim
  behaviour, so a real lean bias would also drive the estimate up. This may be a
  symptom of the driver-side offset rather than a separate fault.

### How to settle it

1. **Read `Ethanol fuel percent` before and immediately after the next fill**, on
   the same tank of fuel from the same pump. If it moves again, the inference is
   re-running on fuel that has not changed.
2. **A memory wipe resets it to 9.80 %.** That is the one value that appears only
   after a wipe. Note it, then watch how many kilometres it takes to climb.

**This is a learned value that resets on a wipe and climbs back. That is the exact
signature this investigation has been chasing since the D/R relapse.** It is not
proof — the shake returned on 09-09 while the estimate was still at 9.80 % — but
it is the first learned value anybody has actually tracked across wipes.

---

## 2. BANK 2 NEEDS +1.95 % MORE FUEL THAN BANK 1 — paired, at settled idle

**The measurement `CLAUDE.md` has demanded since the bank asymmetry was first
raised: both short term trims, same samples, same moment.**

| | |
|---|---|
| Paired samples, within 0.15 s, engine 600–720 rpm | **108** |
| `Short term fuel % trim - Bank 1` | **+0.130 %** |
| `Short term fuel % trim - Bank 2` | **+2.076 %** |
| **Bank 2 minus Bank 1** | **+1.946 %** |
| standard deviation / standard error | 1.296 / 0.125 |
| paired t-test | **t = 15.5, p = 3.4 × 10⁻²⁹** |

**Fourth independent sighting of the driver-side lean offset**, and consistent with
the +1.64 % recorded earlier.

**The caveat is severe and must travel with the number: only ONE session in the
entire project ever polled both short term trims together at settled idle.** All
108 samples come from `20260905_041723`. This is a strong measurement of one
session, not a replicated finding. **Repeat it before acting.**

---

## 3. `Throttle Position Actually` EXCEEDS THE PHYSICAL RANGE OF A THROTTLE PLATE

**239 of 8,950 samples read above 90°, with a maximum of 127.99°.** A throttle
plate cannot open past 90° from closed. **The channel's scaling does not map to
plate angle.**

**Consequence: every absolute value read from this channel in this project is
unsafe.** `CLAUDE.md` uses it in the held-1500-rpm test and in the 2000 rpm
capture. As a *relative* indicator — does it move, and when — it is still fine, and
that is how every conclusion drawn from it was actually framed. As a number of
degrees it is not.

---

## 4. `[PCM] Knock Sensor 2` READS CONSISTENTLY HIGHER THAN SENSOR 1

Same samples, matched within 0.3 s, both sessions that ever polled the pair:

| Session | n | Sensor 1 | Sensor 2 | Difference |
|---|---|---|---|---|
| 09-13 cold start | 5 | 159 | 173 | **+8.8 %** |
| 09-14 | 41 | 302 | 323 | **+6.8 %** |

Same direction, two independent sessions. **But the units are undocumented, the
spread is wide (sd 34 on a mean difference of 21), and a bank-to-bank difference in
raw knock sensor output is normal** — the two sensors sit in different places on a
different bank of a V6 and hear different structure-borne noise.

**Not a finding. Recorded because `Knock retard` is 0.000 across 87 samples,** so
whatever these counts represent, the PCM is not acting on them.

---

## 5. THE PER-CYLINDER DATA NAMES A DIFFERENT CYLINDER EVERY TIME

**And one alarming-looking result was an artefact, caught before it became a
finding.**

`[PCM] Cylinder 6 Acceleration Value` spans −0.452 to +0.374 across the whole
dataset — six to ten times every other cylinder. **It is not a cylinder problem.**
Cylinder 6 was the only one still being polled after the throttle closed from 16°
to 2.5°; every cylinder swings on a throttle lift. Restricted to the window where
all six were polled together it reads −0.031 to +0.016, entirely ordinary.

**In that shared window — the only honest comparison that exists:**

| Cylinder | n | min | max | mean |
|---|---|---|---|---|
| 1 | 8 | −0.047 | +0.031 | −0.0019 |
| 2 | 8 | −0.016 | +0.047 | +0.0117 |
| 3 | 8 | −0.016 | +0.062 | +0.0097 |
| 4 | 7 | −0.031 | +0.016 | −0.0022 |
| **5** | 8 | **−0.078** | **0.000** | **−0.0331** |
| 6 | 8 | −0.031 | +0.016 | −0.0039 |

**Cylinder 5 is the outlier here — every sample at or below zero, mean roughly
three times its neighbours.** The 09-14 screenshot named **cylinder 4**. Mode 06
named **cylinder 4**. This window names **cylinder 5**.

**n = 8. Three looks, two different cylinders. That is what noise does.** The
six-capture protocol in `CLAUDE.md` is the way to settle it and it has not been run.

---

## 6. DOWNSTREAM OXYGEN SENSOR VOLTAGE EXCEEDS ITS PHYSICAL CEILING

| Channel | n | Samples above 1.0 V | Maximum |
|---|---|---|---|
| `Oxygen sensor 2 Bank 1 Voltage` | 805 | 9 (1.12 %) | **1.275 V** |
| `Oxygen sensor 2 Bank 2 Voltage` | 761 | 9 (1.18 %) | **1.275 V** |

A narrowband zirconia sensor saturates near 0.9–1.0 V. **1.275 V is outside what
the sensor can produce**, on both banks, at the same rate. Identical maxima on both
banks points at the reporting path rather than at the sensors. Low priority, but
**do not treat anything above 1.0 V from these channels as a measurement.**

---

## 7. THE RIGHT FRONT TYRE IS STILL 26 kPa LOW

| | |
|---|---|
| `[BCM] Left Front Tire Pressure` | 237.5 kPa |
| `[BCM] Right Front Tire Pressure` | **211.7 kPa** |
| Door label | 241 kPa |

Unchanged since the first scan in this project. **Nothing to do with the shake**,
and a front tyre 12 % below its pair is worth thirty seconds with an airline.

---

## 8. THE FOUR SUPPLY VOLTAGE CHANNELS CANNOT BE RECONCILED

| Channel | n | median |
|---|---|---|
| `OBD Module Voltage` | 83,084 | 13.900 V |
| `[BCM] Vehicle Battery Voltage` | 2,756 | 13.000 V |
| `Control module voltage` | 4,091 | 12.695 V |
| `[PCM] Battery voltage` | 40 | 12.644 V |

**A 1.26 V spread between channels that should all read the same bus.** Of the four
possible pairings, **three were never polled together at all**, and the fourth
(`Control module voltage` against `OBD Module Voltage`) has **two** simultaneous
samples, differing by −0.254 V.

**Nothing can be concluded and nothing should be.** Any electrical reasoning in
this project that mixed these channels is unsound. **One capture fixes it: two
tiles, `Control module voltage` and `OBD Module Voltage`, three minutes at idle.**

---

## WHAT THE SCAN FOUND NOTHING WRONG WITH

`Engine coolant temperature` 39–101 °C, normal for Jeddah idling · `Knock retard`
0.000 in all 87 samples · `[PCM] Currently Detected Engine Misfire` 0 in all 102 ·
`Variable camshaft actual advance #1` spans 0.062°, parked · both catalyst
temperatures identical to the decimal at every sample · `Distance traveled with
MIL on` 0 km · both upstream oxygen sensors sweeping the full 0–29.38 range ·
`Barometric pressure` 92–98 kPa · `[BCM] Battery SoC` 81–90 %.

**`Intake air temperature` reaches 68 °C against a 32–40 °C ambient** — 28 °C of
heat soak. Normal for a stationary truck in Jeddah; recorded because it reduces
charge density and nobody had looked at it.
