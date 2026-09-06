# Full vehicle assessment — 2014 F-150 XL 3.7 Ti-VCT / 6R80 / 4x4

**2026-09-06. Five parallel domain analyses of 135,000+ logged samples across four
Car Scanner sessions (2026-09-04 22:24 → 09-05 05:07), plus the 277-screenshot
record and the Mode 06 on-board test results.** Component reports:
[fuel and air](analysis/01-fuel-and-air.md) ·
[ignition and combustion](analysis/02-ignition-and-combustion.md) ·
[mechanical and breathing](analysis/03-mechanical-and-breathing.md) ·
[transmission and electrical](analysis/04-transmission-and-electrical.md) ·
[history and records](analysis/05-history-and-oncoming-tests.md)

**Corrected 2026-09-06 by the owner, who has the truck in front of him:** the
vehicle is **4x4**, not 4x2 — the VIN pattern decodes as 4x2 and that conflict is
unresolved, so confirm against the vehicle before ordering any driveline part.
The cooling **fans are electric**, not a belt-driven clutch fan. And the **air
conditioning was ON** during part of the long idle session. Sections 3.3 and 8
are rewritten accordingly.

**Terminology used throughout.** This engine is a V6 — two rows of three
cylinders. Each row is a *bank*, with its own exhaust manifold, its own catalytic
converter and its own pair of oxygen sensors.

* **Bank 1 = passenger side = cylinders 1, 2, 3.** Upstream sensor is `O2S1
  air:fuel`, downstream is `O2S2 volt. (B1)`.
* **Bank 2 = driver side = cylinders 4, 5, 6.** Upstream sensor is `O2S5
  air:fuel`, downstream is `O2S2 volt. (B2)`.

Firing order 1-4-2-5-3-6, alternating between the two sides.

---

## 1. VERDICT

**The engine is mechanically excellent and the vehicle is in good health.** After
five independent analyses of every channel this truck produces, **no part is
identified as faulty.** The strongest single measurement is that the engine
breathes at **100–108 % volumetric efficiency** at wide open throttle and makes
an estimated **303 hp against its 302 hp rating** — an engine cannot do that with
a restricted exhaust, a blocked converter, worn rings, leaking valves or slipped
cam timing. All of those are eliminated by one measurement.

**Nothing on this truck needs replacing on the evidence available.** Two small
items need attention and neither is related to the vibration.

---

## 2. SYSTEM-BY-SYSTEM CONDITION

| System | Condition | Evidence |
|---|---|---|
| **Engine mechanical / breathing** | **EXCELLENT** | VE 100–108 % at WOT, no airflow plateau, 303 hp estimated vs 302 rated |
| **Fuel injectors, both banks** | **EXCELLENT** | On overrun fuel cut both banks peg at 29.3826 AFR with standard deviation **exactly 0.00000** over 46.5 s (n=680) and 26.6 s (n=412), 16 episodes. Nothing leaks |
| **Upstream oxygen sensors, both banks** | **EXCELLENT** | Banks matched to **0.007 AFR** on 6,695 paired samples; transitions 0.12–0.63 s; Mode 06 response 0.014 s against a 0.4 s limit |
| **Downstream oxygen sensors, both banks** | **GOOD** | Symmetric when properly compared (see §4.1); Mode 06 0.792 / 0.856 s against a 10 s limit |
| **Catalytic converters, both banks** | **GOOD** | Mode 06 0.3711 / 0.3633 against a 0.8359 limit — both at 44 % of band, within 2.1 % of each other |
| **Fuel trims** | **GOOD** | Post-relearn **−0.781 % on both banks**, on all 1,535 and 1,470 samples |
| **Air metering (MAF)** | **CONFIRMED CORRECT** | VE 100–108 % at WOT validates the calibration outright. Idle 2.98–3.00 g/s is normal for Jeddah air density |
| **Ignition timing and control** | **EXCELLENT** | 16,009 samples. Full authority −7.0° to +40.0° and the PCM uses all of it |
| **Knock / combustion quality** | **GOOD, poorly covered** | Octane adaptation had learned a **good-fuel** verdict before the memory wipe. But knock retard was never sampled under load — see §5 |
| **Cam phasing (Ti-VCT)** | **GOOD** | Mode 06 VVT error 0.06° / 0.05° against a **20°** limit, both banks |
| **Misfire** | **EXCELLENT** | 3 events in ~88,000 firing events = 0.003 %, about 280× below the emissions threshold |
| **Evaporative system** | **REPAIRED AND CONFIRMED** | Independent corroboration of the old valve fault and its fix — see §4.3 |
| **6R80 transmission** | **EXCELLENT** | All gear ratios within 2 % of published; converter locks; **13 measured upshifts, zero engine flare on every one** |
| **Torque converter** | **GOOD** | Controlled slip 0.93 % in 5th, 1.5–1.8 % in 4th — as designed |
| **Charging / electrical** | **EXCELLENT** | Regulates to **51 mV over 11 minutes**; three independent voltage sources agree within 0.20 V, so no ground drop on any leg |
| **Cooling system** | **GOOD** | Thermostat reaches and holds temperature; fan cycling visible in the data |
| **Tyres** | **ONE LOW** | Right front 211.7 kPa against a 241 kPa label — see §3.1 |

---

## 3. WHAT ACTUALLY NEEDS DOING

### 3.1 Right front tyre — INFLATE. Five minutes.

**211.7 kPa (30.7 psi) against the 241 kPa (35 psi) door label, and 26 kPa below
its own pair on the left.** A 12 % under-inflation on one front corner. This has
nothing to do with the vibration but it is real, it affects steering, wear and
braking balance, and it is free to correct. Inflate to 241 kPa cold, then check
again in a week — if it drops, the tyre or valve needs looking at.

### 3.2 Axle ratio record — CORRECT THE PAPERWORK. No parts.

`docs/f150-specs.md` records the axle as "likely 3.55". **It is 3.73**, derived
from engine speed against road speed across three gears with one free constant,
and matching the door-code reading. 3.55 would require a 27.4 inch tyre, which
this truck does not have. Nothing to repair — but any future gearing, speedometer
or shift-point calculation built on 3.55 would be wrong.

### 3.3 The cycling load — IDENTIFIED, nothing to do. [RESOLVED 2026-09-06]

Between minute 15 and 40 of the long idle session a clutch cycled on a **15.78
second period**: calculated load stepping **28.6 % ↔ 36.8 %**, airflow **3.43 →
5.08 g/s**, fuel rate **+34 %**. At minute 37–38 it stopped and the engine-speed
oscillation halved at the same moment.

**It was the air-conditioning compressor.** The owner confirms the A/C was on for
part of that session, and with electric cooling fans the compressor is the only
clutch that loads the crankshaft directly. The load statistics settle it:

| Minutes | rpm sd | Median 10 s span | **Calculated load sd** |
|---|---|---|---|
| **15–38, compressor cycling** | **13.94** | **69.0 rpm** | **4.252 %** |
| 40–70 | 8.97 | **35.0** | **0.317 %** |
| 70–131 | 9.27 | 38.0 | 0.373 % |

**Engine load stops varying by a factor of thirteen at the same minute the
oscillation halves.** No further test is needed and no part is implicated — a
compressor cycling at idle disturbs any engine.

**Consequence for the whole project: every amplitude figure must state whether
the compressor was running.** Without that, the same truck reads as two different
trucks. It also restores the original screenshot finding — A/C off 30–53 rpm, A/C
on 64–81 — which a later analysis had wrongly doubted. The logs give 35–38
against 69. **The screenshots were right.**

### 3.3b Two dead channels — never request them again

`A/C pressure` reads exactly **0.000 in every sample of every log**, including
while driving. `Gear (AT)` reads a constant **1.000 in all 45 samples**. Neither
channel answers on this truck. **Every past conclusion that rested on "A/C
pressure reads 0, therefore the A/C was off" is withdrawn** — that is what sent
this investigation looking for a coolant-temperature effect that was never there.

### 3.3c What 4x4 adds — superseded heading kept for reference

Between minute 15 and minute 40 of the long idle session, **a clutch was cycling
on a 15.78 second period**: calculated load stepping **28.6 % ↔ 36.8 %**, airflow
**3.43 → 5.08 g/s**, fuel rate **+34 %**. At minute 37–38 it stopped, and the
engine-speed oscillation **halved at the same moment** (10-second span median
70 → 26 rpm, standard deviation 15.66 → 9.15).

Three independent analyses found this event and agree on its timing. **The
alternator is eliminated** — charging did not stop until minute 46–52.9, which is
8 to 15 minutes *after* the step, so it cannot be the cause.

The truck is **4x4**, which adds a transfer case, a front driveshaft, a front
differential and front CV axles that a 4x2 does not have. **None of them turn at
a standstill in Park**, so none can explain the Park idle shake. But the transfer
case is bolted to the transmission and adds mass and mounting to the powertrain
assembly, so **transfer-case mounting joins the list for the mount and
contact-point checks** — on a 4x2 it would not exist at all.

---

## 4. FOUR CORRECTIONS TO THIS PROJECT'S OWN RECORD

### 4.1 The Bank 1 catalyst asymmetry is REFUTED — it was my error

An earlier revision of this analysis reported that Bank 1's downstream sensor
(passenger side) swings roughly twice as far as Bank 2's, and called it the one
real abnormality on the truck.

**It came from comparing two sampling bursts that do not overlap in time** —
Bank 1 measured 00:11:17–00:14:05 and Bank 2 measured 00:14:03–00:16:34. In the
**seven windows across all four logs where both sensors were sampled at the same
instants**, the ratio of their swings is 0.95, 1.15, 1.27, 0.27, 1.01, 0.99, 0.88
— **never near 2**, and peak-to-peak matches within 10 %.

It also agrees with Mode 06, which scored the two converters within 2.1 % of each
other. **Strike the Bank 1 converter from the suspect list.** This is the third
time in this project that a cross-window comparison has produced a false finding.

### 4.2 The 12° idle timing is NORMAL — the reference was wrong

Pooled across all four logs at warm Park idle: **12.05° BTDC, sd 1.14°, median
12.0°, n = 11,456.**

**There is no Ford specification for idle spark on this engine.** Timing is not
adjustable on a coil-on-plug engine; it is a control-loop output. The nearest
community figure for an F-150 is 13–17° at 650 rpm in Park, so this truck sits
**0.5–1.1° under it — one to two quantisation steps of the PID.**

The project guide's 16–22° expectation is a Level 3 heuristic its own authors
could not corroborate, and it **also has its Park/Drive ordering backwards for
this vehicle**: measured minutes apart, **Drive 12.80° (n=1,349) against Park
12.16° (n=5,055)**. The guide expects Park higher. It is lower.

**Delete the 16–22° expectation. This truck's idle timing is not a finding.**

### 4.3 "Spark authority is tiny, 1.75°" — WRONG, and it matters

CLAUDE.md states the spark governor's authority is 1.75° peak-to-peak. That
conflates **authority** with **applied correction**.

**Measured spark authority is 47 degrees** — from **−7.0°** on deceleration to
**+40.0°** at light cruise — and the distribution shows the PCM using the whole
range with no clipping at either end. The 1.75° is what the governor *chose to
apply* during one idle window.

**The governor is not running out of range. It is choosing a small gain.** That
is a completely different diagnosis, and it removes "the PCM cannot correct
enough" from the table.

### 4.4 "Both banks matched at 0.00 %" — softened

The session-average bank difference is near zero because **the difference changes
sign inside the session**. Measured simultaneously at a constant 652 rpm Park
idle with both long-term trims pinned:

| Window | Bank 2 minus Bank 1, short term trim | n |
|---|---|---|
| 22:51–22:54 | **−0.79 %** | 1,985 |
| 00:48–00:55 | **+1.38 %** | 3,057 |
| Post-repair, one 31 s block | **+2.33 %** | 251 |

Maximum magnitude **2.3 %**, which is under every diagnostic threshold — the
guide flags 3–5 %. **But it is not a fixed offset, and calling it "0.00 %,
closed" was too strong.** It is small, it wanders, and it does not currently
justify any action.

---

## 5. THE ONE MEASUREMENT THAT MATTERS AND DOES NOT EXIST

**Knock retard was never sampled under load. Not once, in any log.**

All 38 samples of `Knock retard` are 0.0°, which sounds reassuring — but that is
about **26 seconds in total, every one of it at Park idle**, where an engine is
nowhere near knocking. The channel was **absent entirely from the log containing
both wide-open-throttle pulls** (6,832 and 6,402 rpm, 96.5 % load).

**Spark advance was also not sampled during either pull.** And neither wideband
oxygen sensor was sampled during them, which means this project's recorded claim
of "12.3:1 commanded and delivered at wide throttle" **is not supported by these
logs**.

Indirect evidence is good — 30 seconds after the pulls the PCM was running 33–40°
at cruise with no residual retard, which a knocking engine would not allow. But
the direct measurement is missing.

### The capture that closes it

One drive, four channels, ten minutes:

`Engine RPM` · `Tim. adv.` · `Knock retard` · `O2S1 air:fuel`

Warm engine. Two or three hard accelerations from about 2000 rpm to 5000 in a
low gear, then two minutes of steady cruise. Export CSV #2, rounding off.

**That single capture settles knock under load, spark under load, wide-open-
throttle mixture, and whether the octane adaptation is moving in the right
direction — all four at once.** It is the highest-value thing left to record on
this vehicle.

---

## 6. THE OCTANE ADAPTATION — the best news in the dataset

The `Learned octane` PID is Ford's **Octane Adjust Ratio**. Both observed values
are exact multiples of 2⁻¹⁴ (−9828/16384 and +1335/16384), which identifies it as
a Q14 fixed-point ratio on a ±1 scale. On that scale **−1 means the best fuel
quality and +1 the worst.**

| | Value | Meaning |
|---|---|---|
| Before the battery disconnect | **−0.5999** | Well toward the good-fuel end |
| Immediately after | **0** | The documented reset value |
| After one drive | **+0.0815** | Early relearn, not yet settled |

**The −0.60 is the strongest long-integration evidence of healthy combustion in
this entire project.** It is a value the PCM built up over weeks of driving on
the owner's usual 95 octane, and it says the engine was not knocking and the fuel
was good.

**It was destroyed by the battery disconnect and is now rebuilding from zero.**
That is not a fault — it is the expected consequence — but it means the current
+0.08 says nothing yet. Re-read it after several hundred kilometres.

---

## 7. WHAT THE LOGS PROVED ABOUT THE OLD PURGE VALVE

The evaporative channels had never been used in this investigation and they
independently confirm both the fault and the repair.

| | Before the valve was replaced | After |
|---|---|---|
| Purge command | **Flat — 11 distinct values in 2 h 25 min across 7,533 samples** | 23 values, stepping in 0.39 % increments |
| Evaporative vapour pressure | **Sustained −602 Pa for the whole session (n=1,500)** | At atmosphere, −13.8 Pa (n=259) |

A purge command that barely moves for two and a half hours is a PCM that has
given up controlling a valve that is not responding. The sustained tank vacuum is
the flow the old valve was passing. **Both signatures disappear after the
replacement.** It also proves the canister vent is not blocked.

**The valve was a genuine fault, correctly identified and correctly fixed.** It
was not the cause of the vibration — that was established when the improvement
relapsed — but the repair itself was sound.

---

## 8. THE IDLE OSCILLATION — where it now stands

Not a fault in any part, and progressively narrowed by these analyses.

**What it is:** engine speed cycling at **0.304 Hz**, 3.0 second period, about
40 rpm peak to peak in Park and 15 in Drive, holding for hours. The averaged
shape over 926 cycles rises through 43 % of the cycle and falls through 57 %.

**What is now eliminated as its cause:**

| Candidate | How it was eliminated |
|---|---|
| Spark / the PCM driving it | Spark **follows** engine speed by 0.06–0.12 s at r = −0.64 to −0.93, in six windows. A follower, not a driver |
| Throttle, phaser, cycling leak, any air path | Airflow modulation at 0.304 Hz is **0.14 % of mean** — about nine times too small |
| Electrical noise | Voltage correlates with engine speed at r = −0.006 to +0.085 |
| Alternator load | Charging stopped 8–15 minutes *after* the amplitude step |
| The governor running out of authority | It has 47° and uses 1.75° |
| Fuel trim chasing it | Short term trim **lags** engine speed by 0.65 s — it is downstream of everything |

**What remains:** the commanded air/fuel dither leads engine speed with the
physically correct sign and accounts for about a fifth of the variance. The other
four fifths is **an engine load that varies on a seconds timescale**, and §3.3
names the two candidates and how to tell them apart.

---

## 9. THE FELT VIBRATION — untouched by any of this

**None of the above addresses the shake in the seat, and none of it can.**

The oscillation is 0.3 cycles per second. Vibration felt through a seat is 10 to
33 cycles per second. The logs sample at about 17 Hz, so the fastest thing they
can resolve is 8.3 Hz — **below every frequency that can shake a cab.** This is a
physics limit, not a missing test.

One new and relevant measurement did come out of it: **a half-order component
exists in engine speed at exactly rpm/120** — 5.433 Hz in Park, moving correctly
to 4.600 Hz in Drive at 550 rpm. Half order is the harmonic that flags one
cylinder contributing differently from the other five. **But its amplitude is
0.14–0.32 rpm, far too small to be felt**, and its cause is ambiguous between a
real imbalance and a sampling artefact.

**More usefully, first order is absent** — its alias frequency sits at the noise
floor in all 14 windows tested. That is **the first quantitative evidence against
the crankshaft-reluctor hypothesis**, which has been this project's leading
explanation for reset-helps-then-returns.

The felt shake still needs the accelerometer test, and after it the mounts and
contact-point checks. Nothing measurable through the diagnostic port will ever
reach it.

---

## 10. DO NOT DO THESE

Every one of these has been measured and is healthy. Spending money here is
spending it for nothing.

* **Do not replace injectors.** Both banks seal perfectly on overrun.
* **Do not replace any oxygen sensor.** All four are within a few percent of
  each other and Mode 06 timed the upstream pair at 0.014 s against a 0.4 s limit.
* **Do not replace either catalytic converter.** Both at 44 % of the failure
  threshold and within 2.1 % of each other. The asymmetry that suggested
  otherwise was a measurement error — see §4.1.
* **Do not replace the mass airflow sensor or clean it.** Volumetric efficiency
  of 100–108 % at wide open throttle validates its calibration outright.
* **Do not replace the purge valve again.** The new one is working and the data
  proves it.
* **Do not smoke test.** There is no lean bias left to explain.
* **Do not chase the barometric reading.** The owner's other truck reads 99 kPa
  in the same city against this one's 97 — inside sensor tolerance.
* **Do not touch the transmission.** Thirteen shifts, zero flare.
* **Do not disconnect the battery again before a measurement.** It destroyed the
  octane adaptation, the trims, the monitors and the code history in one action,
  and that data has not finished rebuilding.

---

## 11. NEXT ACTIONS, IN ORDER

| # | Action | Cost | What it settles |
|---|---|---|---|
| 1 | **Inflate the right front tyre** to 241 kPa | 5 min | A real, unrelated defect |
| 2 | ~~Identify which clutch cycles~~ **DONE — it was the A/C compressor** | — | Resolved 2026-09-06. No action, no part |
| 3 | **Log `Engine RPM` + `Tim. adv.` + `Knock retard` + `O2S1 air:fuel` on a drive with hard pulls** | 10 min | Knock under load, spark under load, WOT mixture, octane relearn — the biggest hole in the dataset |
| 4 | **Read permanent codes (Mode $0A)** | 5 min | The only code history the battery disconnect could not erase — it lives in non-volatile memory for exactly that reason |
| 5 | **Accelerometer on the seat, Park then Drive** | 15 min | The only test aimed at the vibration actually complained of |
| 6 | **Cylinder balance — unplug each injector in turn, record the rpm drop** | 30 min | Six numbers compared against each other. Needs no reference vehicle |
| 7 | **Request `Manifold absolute pressure` (the plain PID, not high-resolution)** | — | Would allow a real idle volumetric-efficiency calculation |

Items 1 to 4 are the ones worth doing first. **None of them costs a part.**

---

## 12. WHY DOES THE PCM ADJUST THE FUEL? — the loop, and which sensor drives it

### The fuel command has two layers

**Layer 1, the fast loop, driven by the two UPSTREAM sensors.** It holds the
mixture at lambda 1 and corrects within a second or so. On this truck those
sensors respond in **0.014 s against a 0.4 s limit** (Mode 06) and the two banks
agree to **0.007 AFR** on 6,695 paired samples. This layer is not the source of a
three-second rhythm — it is far too fast.

**Layer 2, the slow loop, driven by the two DOWNSTREAM sensors.** Ford calls this
fore/aft, or rear oxygen trim. Its job is to bias the target slightly rich or
lean so the catalytic converter's oxygen store stays about half full. **Its
period is set by how long the converter takes to fill and empty, which is
seconds.** That is where a 3-second rhythm comes from, and it is the layer this
truck's 0.304 Hz command almost certainly belongs to.

### The measurement that would prove it was never taken

Cross-correlating the commanded air/fuel against every channel that overlaps it:

| Channel | Result |
|---|---|
| Upstream air/fuel, Bank 1 (passenger) | **follows** the command by 0.70 s, r = +0.588 |
| Engine speed | **follows** the command by 0.15 s, r = −0.41 |
| **Downstream O2, either bank** | **only 26–40 simultaneous samples — not analysable** |
| Engine coolant temperature | **zero simultaneous samples** |

The 0.70 s delay on the upstream sensor is exactly right — command, injection,
combustion, exhaust travel, sensor response. **Nothing in the data leads the fuel
command**, which is consistent with a scheduled dither rather than a reaction —
but **the one sensor that drives that loop was never sampled alongside it.**

**The capture that closes this: `Fuel/Air com. ratio` together with
`O2S2 volt. (B1)` on the same graph, three minutes at warm idle in Park.** If the
downstream sensor leads the fuel command, the fore/aft loop is confirmed as the
source and its behaviour can be judged. If it does not, the dither is an
open-loop schedule and no sensor is responsible.

### Sensors that could make this loop misbehave, ranked

| Rank | Sensor | Why it could do this | What the data already says |
|---|---|---|---|
| **1** | **Downstream oxygen sensor, either bank** | It is the sensor that drives the slow loop. Lazy, biased or contaminated, the PCM responds late, overshoots, and the loop hunts | Switching response **0.792 / 0.856 s against a 10 s limit** — excellent. But the downstream **slope** test is the tightest approach in the whole Mode 06 set at **12.6–12.8 % from the zero end**, and heater current sits at about **3× its lower limit**. Not failing, but the least comfortable numbers on the truck |
| **2** | **Engine coolant temperature sensor** | Fuelling and idle target are both scheduled on it. A noisy or drifting signal modulates fuel directly | **Never co-sampled with the fuel command — zero simultaneous samples.** Completely untested against this |
| **3** | The catalytic converter itself (not a sensor) | The loop's period is set by its oxygen storage. A degraded converter makes the loop run faster | Both at **44 % of the failure limit**, within 2.1 % of each other |
| **4** | Upstream wideband sensors | Drive the fast loop; a lazy one makes it oscillate | **0.014 s against a 0.4 s limit.** Effectively eliminated |
| **5** | Mass airflow sensor | A wandering airflow signal would move the fuel command | **r = +0.106 against engine speed** on 13,349 samples. Eliminated |
| **6** | Fuel rail pressure sensor / regulator | Pressure swing changes delivered fuel | **This PID never returned on this truck.** Unmeasured, but secondary — the command itself is swinging, not just the delivery |

### The honest limit

**The dither is normal in kind.** ±1.5 % commanded air/fuel on a seconds timescale
is what fore/aft catalyst control looks like on a healthy Ford. Whether its
amplitude and period are normal **for this engine** cannot be judged without
another 3.7 to compare against.

**And even a perfect fuel command would not remove the oscillation.** The command
accounts for r = −0.41, which is **17 % of the variance in engine speed**. Fixing
the fuel loop entirely would leave four fifths of the movement untouched.
