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

### THE 2023 CONTROL TRUCK ALSO REPORTS ETHANOL — 11.37 % (2026-09-15)

**The owner asked whether his other truck has the channel. It does, and the
answer substantially weakens the finding above.**

| Truck | `Ethanol fuel percent` | Raw byte | n |
|---|---|---|---|
| **2023 F-150 5.0** — the healthy control | **11.37 %** | 29 | 116, constant |
| 2014 F-150 3.7 | 9.80 / 19.22 / **22.35 %** | 25 / 49 / 57 | across 7 sessions |

**NEITHER TRUCK READS ZERO.** The control truck — the one the owner reports as
smooth, the one this project uses as its reference for a healthy idle — reports
**11.37 % ethanol**, and that value sits **inside the 2014's own range**.

**What this kills:** the idea that a non-zero ethanol estimate is by itself a
fault marker. It is not. A healthy 2023 F-150 in the same city, same week, same
owner, same app reports one too.

**What it raises:** the real possibility that **Saudi pump fuel genuinely
contains ethanol**, somewhere near 10 %. This project has asserted E0 as fact
without ever checking, and two independent Ford PCMs both disagree with it.

**What it does NOT settle.** The 2023 infers its value the same way — Ford
deleted the physical sensor across the range. **Two PCMs using the same inference
can be wrong in the same direction.** Agreement between them is not confirmation;
it is one method sampled twice.

**The 2014 still reads roughly double the 2023 at its highest**, 22.35 against
11.37. That gap is the part still worth explaining — but it is a gap between two
estimates, not between an estimate and a measurement.

**Consequence: the water dilution test now answers BOTH trucks at once.** If the
fuel comes back near E10, the 2023 is right, the 2014 is high by about a factor
of two, and the question narrows to why. If it comes back E0, both PCMs are
inferring ethanol that is not there and the whole channel is unusable on either
vehicle.

**Also confirmed from the same 2023 session:** `Long term secondary oxygen sensor
trim Bank 1` and `Bank 2` read **exactly 0.0000** across 116 and 108 samples,
which is what `CLAUDE.md` has always said.

**And one observation that cuts against this project's trim reasoning:** across
that session the 2023's `Long term fuel % trim - Bank 1` ranged **−5.47 to
+2.34 %** and `- Bank 2` **−0.78 to +5.47 %** — **wider excursions than anything
the 2014 has shown.** Conditions were not matched (the 2023 log includes
driving), so this is not a like-for-like comparison and must not be used as one.
It is recorded because the healthy truck's trims are not tidier than the sick
one's, and this file has repeatedly treated small trim numbers on the 2014 as
though they were.

**The bank comparison on the 2023 could NOT be done.** Its three sessions yield
only **10 paired short-term-trim samples at settled idle** — far too few. So
whether a healthy F-150 also carries a bank offset is **still unknown**, and the
2014's +1.95 % has no control to be judged against.

### THERE IS NO ETHANOL SENSOR ON THIS TRUCK — the number is INFERRED

**Ford deleted the physical fuel composition sensor on 2004-and-newer vehicles.**
The PCM derives `Ethanol fuel percent` from **oxygen sensor feedback and how the
long term fuel trims settle after a refuel**. It is a computed guess, not a
measurement of what is in the tank.

**This reframes the whole finding.**

* **It cannot be "reading wrong" in the sensor sense** — there is no sensor to
  drift, foul or fail.
* **It cannot tell anyone what is in the fuel.** A reading of 22.35 % means only
  *"after the last refuel this engine behaved as though it needed more fuel than
  my model predicted."*
* **Therefore the ethanol estimate is the lean bias restated in different
  units** — not independent evidence of a second problem. This project must stop
  treating it as a separate anomaly.

**Where it still does real damage: open loop.** In closed loop the wideband
oxygen sensors drive mixture to lambda 1 whatever the PCM believes about the
fuel, and the trims absorb the error. **In open loop nothing corrects it** — the
first ~20 s of every cold start, and wide open throttle. An over-estimated
ethanol figure genuinely over-fuels there.

**Arithmetic, if the fuel really is E0:** at 22.35 % the PCM targets roughly
**13.4:1 instead of 14.7:1** — about **9.5 % more fuel**. The measured trims are
only −2.3 to −3.1 %, which is **far less than a 9.5 % base error should require**.
So either the fuel contains real ethanol, or the estimate is not being applied at
face value. **Unresolved, and it should not be guessed at.**

**Saudi pump fuel ethanol content is NOT established.** Searching returned octane
grades for Aramco 91 and 95 but no ethanol specification. This project has
repeatedly written "Saudi pump fuel is normally E0" as though it were a fact. **It
is an assumption and it has never been checked.**

### How to settle it — the water dilution test

**This measures the fuel directly.** Ethanol dissolves into water; petrol does
not. Water pulls the ethanol out of a fuel sample and **grows by the volume of
ethanol that was in it**, while the fuel layer shrinks by the same amount.

**SAFETY FIRST: this is an open container of petrol.** Outdoors or a fully
ventilated bay. No ignition source, no smoking, no grinder running nearby. Keep
it capped except while pouring.

**The container**

* **Tall and narrow beats short and wide.** The same volume change shows as a
  bigger height change, which is where the accuracy comes from.
* **Glass is ideal.** Polypropylene or high-density polyethylene are fine.
* **NEVER polystyrene — petrol dissolves it.** Acrylic crazes. Clear PET is
  tolerable for a few minutes but no longer.
* **1 ml graduations.** A 100 ml laboratory measuring cylinder is the right tool.

**Water: distilled, and dyed**

* **Use distilled or deionised water** — the sort sold for batteries and steam
  irons. Tap water will work chemically, but distilled removes any argument about
  minerals coming out of solution and clouding the reading.
* **Add one drop of WATER-BASED food colouring to the water before you start.**
  Petrol will not take up a water-soluble dye, so the boundary becomes
  unmistakable instead of a faint refractive line. **Check the dye is not
  alcohol-based** — an alcohol carrier would corrupt the very thing being
  measured.

**The procedure**

1. **10 ml of dyed distilled water** into the cylinder. Read the level and write
   it down.
2. Add fuel to the **100 ml** mark — that is **90 ml of fuel** — straight from
   the tank or the pump nozzle.
3. Cap it. **Invert slowly ten times over about thirty seconds.**
   **Do not shake it hard.** Vigorous shaking makes an emulsion that can take an
   hour to clear; gentle inversion extracts just as completely.
4. Stand it upright and still for **ten to fifteen minutes** — longer than the
   five minutes first written here. The boundary is sharp when it stops moving.
5. **Read the water layer.**

**Cross-check, and it is free:** the fuel layer must fall by the same amount the
water rose. Water 10 → 19 ml and fuel 90 → 81 ml agree. If they do not, the
sample was not given long enough to separate.

**Resolution:** with 90 ml of fuel, **each 1 % of ethanol moves the boundary
0.9 ml**, so 1 ml graduations resolve a little better than 1 %. Ample.

**Do it at one temperature.** Sample and cylinder both at ambient, and keep it
out of direct sun — in Jeddah heat an uncapped sample loses light ends fast.

**One caveat that does NOT matter:** petrol and water are very slightly soluble
in each other even with zero ethanol, but that is on the order of hundredths of a
millilitre. **A true E0 sample reads 10 ml unchanged.**

**What each outcome means:**

| Water layer | Reading |
|---|---|
| **10 ml, unchanged** | The fuel is E0 and **the PCM's 22 % estimate is wrong.** The inference is being driven by a real lean bias, and it is over-fuelling every cold start and every full-throttle pull. |
| **12–14 ml (E10-ish)** | Ordinary blended fuel. The estimate is high but not absurd, and the trims make sense. |
| **≈ 32 ml (E22)** | The estimate is **correct** and there is nothing wrong with the fuelling at all. The whole line closes. |

**Do this before anything else in the fuel line.** It is the cheapest test left in
the entire investigation and it decides whether a reading this project has carried
as an anomaly since day one is a fault or a fact.

### Then, at the truck



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
