# Context

The owner is a working mechanic in Jeddah, Saudi Arabia. He does the
hands-on work himself — give him diagnostic reasoning, specs and procedures,
not "see a mechanic."

## The truck

**2014 Ford F-150 XL Regular Cab · 3.7L V6 Ti-VCT · 6R80 auto · 4x4**
VIN `1FTMF1EM1EFC80632` · 131,000 km (Aug 2026) · Jeddah

**DRIVE TYPE — 4x4, owner-confirmed 2026-09-06.** Earlier revisions of this file
said 4x2 on a VIN decode and used that to dismiss the history report. **The owner
has the truck in front of him and says it is 4x4; that outranks a decode.** The
conflict is unresolved and matters for parts: `1FTMF1E` decodes as Regular Cab
4x2 in the position-4 series codes, where 4x4 Regular Cab is normally `1FTNF1E`.
Confirm before ordering any driveline part by checking for a transfer case, a
front driveshaft and a 4x4 selector.

**It also puts driveline parts back on the table that a 4x2 does not have** —
transfer case, front driveshaft, front differential, front CV axles. None of them
turn at a standstill in Park, so they cannot explain the Park idle shake, but the
transfer case is bolted to the transmission and adds mass and mounting to the
powertrain assembly.

**COOLING FANS ARE ELECTRIC, not a belt-driven clutch fan** (owner, 2026-09-06).
An electric fan loads the engine only through the alternator, which is a far
smaller and differently-shaped load than a mechanical fan clutch. Any reasoning
that treated a fan clutch as a direct crankshaft load is withdrawn.

## THE DASHBOARD — [`docs/DIAGNOSTIC-DASHBOARD.md`](docs/DIAGNOSTIC-DASHBOARD.md)

**Built 2026-09-18: every system classified CONFIRMED / HIGH-CONFIDENCE SUSPECT
/ POSSIBLE / NORMAL / UNKNOWN, from archived data only.** Read it for the state
of the whole truck rather than the state of one argument.

**Confirmed faults: none.** **One high-confidence suspect: the PCM supply
voltage.** **The largest unexamined system is the TRANSMISSION** — commanded
against measured gear ratio exists at n=591, but every sample is at a
standstill, where the measured ratio is a division by zero and the constant
0.829 "error" is a clamp, not slip. **It has never been measured while moving.**

## THE SYMPTOM, RESTATED BY THE OWNER — READ THIS BEFORE ANY DIAGNOSIS (2026-09-17)

**Owner's own words, and they re-scope this entire file:**

> *"When I ask you to diagnose my car don't think that I'm talking about the old
> shake which resolved by changing the mounts. My current ongoing problem is the
> engine feel like shaking and rpm unstable on very low non-noticeable events.
> Don't assume I'm complaining about something shaking hard. It's very small
> vibration associated with engine rpm change. It's still the same even after the
> custom tune."*

| | |
|---|---|
| **THE BIG SEAT SHAKE** | **CLOSED. The mounts fixed it. Do not re-open it, do not chase it, do not cite it.** |
| **THE CURRENT PROBLEM** | **A very small vibration that accompanies engine speed CHANGING** — low-level, easy to miss, not violent. Plus the speed being unsteady. |
| **The custom tune** | **Changed nothing about it.** |

**THIS FILE IS FULL OF LANGUAGE WRITTEN FOR THE OLD SYMPTOM.** Every phrase about
"the felt shake", "moves him in the seat", "shakes a person", and every test aimed
at a strong vibration is **about a complaint that is finished**. Read those
sections as history. **Do not hand him a test designed to find something violent.**

### WHAT THIS CHANGES LOGICALLY — the separation proof does NOT apply any more

This file states, twice and in capitals, that the felt shake and the 0.3 Hz rpm
oscillation are **separate phenomena, proven by two natural experiments** — the
mounts killed the shake and left the oscillation; the battery quietened the
oscillation and left the shake.

**Both experiments used the BIG shake as the variable.** The small
speed-linked vibration he is describing now **was never the thing being watched in
either one.** So:

**THE SEPARATION IS PROVEN FOR THE OLD SYMPTOM AND IS UNTESTED FOR THE NEW ONE.**
Do not carry it over. It is the single easiest mistake available here, because the
conclusion is written in this file in bold.

**And the new description points the other way.** A vibration that tracks engine
speed *changing* is what the 0.3 Hz oscillation would feel like — not as a 0.3 Hz
buzz, which is far too slow to feel as vibration, but as the engine's motion on
its mounts shifting every ~3 s. **The tune leaving it unchanged fits**: the tune
altered shift points and throttle response and touched neither idle fuelling nor
the catalyst dither that drives the oscillation.

### THE RIGHT METRIC IS THE DERIVATIVE — and it AGREES with amplitude (corrected 2026-09-17)

**Tool: [`data/rpm_rate.py`](data/rpm_rate.py). Log record:
[`docs/LOG-2026-09-17.md`](docs/LOG-2026-09-17.md).**

What pushes an engine against its mounts is **reaction torque, proportional to
angular ACCELERATION** — not how far the speed swings. Every other metric in this
file measures the swing.

**A RAW DERIVATIVE IS USELESS** — it is dominated by the sample interval: the
2023 control gave 60.3 rpm/s in one session and 90.0 in another **on the same
evening**, purely from 0.130 s against 0.049 s logging. **Fix the bandwidth
first.** At a fixed 0.3 s those two read **7.09 and 7.25** — agreeing within 2 %
across a 2.6× rate difference.

**A BUG IN THIS TOOL WAS CAUGHT ON 2026-09-17 AND IT CHANGED THE ANSWER.**
`np.interp` draws a straight line across any gap in the source, and a straight
line has almost no rate of change. The 09-17 log has a **47.5-minute hole** in
`Engine RPM`; **44 % of its grid fell inside it**, and the tool reported
**1.82 rpm/s** — which would have been a spectacular four-times-quieter-than-
healthy result. **Real coverage only: 12.50 rpm/s.** Both this tool and
`data/idle_events.py` now discard grid points spanning a gap over 1 s, and every
session was recomputed.

| | Before the fix | **After** |
|---|---|---|
| 2014 median | 8.37 rpm/s | **13.53 rpm/s** |
| 2023 control | 7.17 | **7.17** |
| **Ratio** | 1.17× | **1.89×** |

**THE PREVIOUS ENTRY HERE SAID "two metrics, same data, very different
verdicts" — 1.90× on peak-to-peak against 1.17× on rate of change. THAT
DISAGREEMENT WAS THE BUG.** Corrected, rate of change gives **1.89×** against
peak-to-peak's **1.90×**. **They agree almost exactly and are measuring the same
thing.** The question of which metric tracks what he feels dissolves.

## THE 108-MINUTE LOG, 2026-09-17 — the post-tune baseline arrived

**Full record: [`docs/LOG-2026-09-17.md`](docs/LOG-2026-09-17.md). Log:
`data/carscanner/2026-09-17-full-page/`.** 108 minutes stationary
(`Vehicle speed` 0.00 in all 596 samples), idle 652 rpm, 74 channels.

**IT IS THE QUIETEST IDLE THIS TRUCK HAS EVER MEASURED, on every metric:**

| Metric | Today | Other 2014 sessions | 2023 control |
|---|---|---|---|
| Median 10 s span (decimated to 0.215 s) | **31.0 rpm**, 302 windows | 25.5–38.0 | not rate-matchable |
| Rate of change | **12.50 rpm/s**, n=33,979 | 10.99–15.12 | 7.09 / 7.25 |
| Discrete events | **0.442 /min**, 56.5 min idle | 0.128–1.664 | 0.372 / 0.975 |
| Band-passed sd | **5.72 rpm — lowest of any 2014 session** | 6.82–19.30 | 4.54 / 6.20 |

**AND THE COMPRESSOR STATE IS KNOWN FOR THE FIRST TIME.** This file has insisted
for weeks that every amplitude figure must state whether the air conditioning was
running and none could. **`[PCM] A/C Pressure` answers: 1070–1518 kPa, 7,621
samples, cycling with a dominant period of 49.4 s** — **not** the 15.78 s recorded
in 2026-09. The only previous session with the compressor known to be cycling
gave a **69 rpm** span; today, cycling, **31.0**. Conditions unmatched and the
methods differ, so not a clean before-and-after — but the compressor is at last
measured rather than guessed.

**WHAT THE CAPTURE FAILED TO DO — 74 TILES ON THE PAGE.** `[PCM] Currently
Detected Engine Misfire` got **1 sample**. Knock sensors **2 and 1**.
`Timing advance` **2**. **And `Engine RPM` has a 47.5-minute hole that covers the
ENTIRE window in which all six cylinder channels were polled** — all six DO
overlap for 10.8 minutes at ~591 samples each, the window wanted since night one,
**but engine speed is absent from every second of it**, which is exactly the flaw
that invalidated the last per-cylinder reading. In the 60-minute block where
engine speed does exist, `Short term fuel % trim - Bank 1` has **1 sample**.

**THE RULE: putting everything on the page does not capture everything. It
captures a little of a lot, badly, and the app chooses which.** Two tiles; three
only when engine speed is there to prove the condition.

## WHAT TO LOG AT IDLE — [`docs/IDLE-LOG-LIST.md`](docs/IDLE-LOG-LIST.md)

**OWNER CORRECTED THIS LIST 2026-09-17: `Intake manifold absolute pressure` is
NOT in his sensor list. He is right, and checking it exposed four errors.**

**1. `Intake manifold absolute pressure` IS A 2023-ONLY CHANNEL.** A raw header
scan of every file in this repository finds it in **exactly three files, all
three the 2023 control**. This file and `docs/SENSOR-INVENTORY.md` both credit
this truck with *"99 kPa in all 16 samples, engine off"* and call it **"untested,
not dead"** — **the same 2023-attribution error already recorded once for the
secondary oxygen sensor trims. WITHDRAWN.**

**What this truck has is `Manifold absolute pressure (high resolution)`, and it
reads BLANK at 0 ms refresh** — offered by the app, not answered by the truck.
**Manifold pressure is genuinely unavailable here. A mechanical vacuum gauge is
the only route.** The "one minute settles it" capture this file listed first does
not exist.

**2–4. "NEVER LOGGED" WAS WRONG THREE TIMES.** All three have been recorded:
`[PCM] Currently Detected Engine Misfire` **53 samples, 3 sessions, exactly
0.0000 in every one**; `[PCM] Knock Sensor 1`/`2` **48 samples each**;
`[PCM] Cylinder 1–6 Acceleration Value` **8–42 each**. **The misfire capture is
still needed — not because it was never logged, but because 53 scattered samples
almost certainly never landed on an event. **Rate measured: 0.44–1.66 per
minute across sessions** — the 09-04 log gives 136 events in 122 idle minutes,
one per 54 s.

**THE RULE THAT SHAPES THE LIST: the 33 Hz cliff only matters when ENGINE SPEED
ITSELF is analysed** — orders, rate of change, event shape. **Trims step in
0.78 % and move over seconds, so 15.5 Hz is ample.** Two tiles for engine-speed
questions; **three when engine speed is only there to prove the condition** —
which the trim capture needs, because the last one had no engine state and that
cost it its meaning.

| # | Time | Channels | What it settles |
|---|---|---|---|
| **1** | **30 min** | `Engine RPM` + `[PCM] Currently Detected Engine Misfire` | The hiccups. Events are 0.24 s — combustion timescale. At the measured 0.44–1.66 per minute, thirty minutes gives **13–50**. |
| **2** | **3 min** | `Short term fuel % trim - Bank 1` + `- Bank 2` + `Engine RPM` | The swap. **Do not touch the throttle** — the bank difference reverses sign under throttle movement. |
| **3** | **5 min + 2 min** | `Engine RPM` alone, then held ~1200 rpm | Post-tune baseline for all three rpm tools. At 1200 a false order moves, a real one does not. |
| **4** | **6 × 1 min** | `Engine RPM` + one `[PCM] Cylinder N Acceleration Value` | One at a time; all six drops to 2 Hz. **Repeat after a restart.** |
| **5** | **2 min** | `[PCM] Knock Sensor 1` + `[PCM] Knock Sensor 2` | **Sensor 2 reads higher than sensor 1 in all three sessions** (170–483 vs 156–394). Raw units, mixed conditions — not a finding, never compared at a known idle. |
| **6** | **1 min** | `Engine RPM` + `Manifold absolute pressure (high resolution)` | The blank claim rests on ONE screenshot. Confirm it, or a real measurement returns. |
| **7** | **1 min, no scanner** | Meter across the battery posts at idle | `Control module voltage` reads 12.49–12.77 V running. **13.5–14.5 with drops = normal. Steady 12.6 = not.** |

**IF THERE IS ONLY TIME FOR TWO: numbers 1 and 2.**

**DROPPED:** the engine-off `Barometric pressure` cross-check — **its partner
channel does not exist on this truck**, so the 97 kPa barometric reading has
nothing here to be checked against.

## IS THE ENGINE RUNNING BADLY? NO — the unbiased sweep (2026-09-17)

**Full record: [`docs/IS-THE-ENGINE-OK.md`](docs/IS-THE-ENGINE-OK.md). Tool:
[`data/idle_sweep.py`](data/idle_sweep.py).** Owner asked directly and asked not
to be limited to his complaint. Every channel both trucks recorded at settled
idle, then the 2014 judged on **absolute criteria needing no control**.

| | median at idle | expected | |
|---|---|---|---|
| Spark advance | **12.00°** | 10–20, steady | normal |
| Short term trim B1 / B2 | **0.00 / 3.12 %** | within ±10 | normal |
| Long term trim B1 / B2 | **0.00 / 1.56 %** | within ±10 | normal |
| Airflow | **3.00 g/s** | 2–5 for a 3.7 | normal |
| Idle speed | **652 rpm** | 600–750 | normal |
| Calculated engine load | **28.2 %** | 15–35 | normal |

**Every trim sits inside ±5 % where the limit is ±10 %. Nothing measured says an
engine running badly.**

**THE ONE ABSOLUTE CRITERION IT FAILS IS ELECTRICAL: `Control module voltage`
reads 12.49–12.77 V WITH THE ENGINE RUNNING**, against 13.0–14.8 expected.

**ADVANCED 2026-09-18 — see
[`docs/VOLTAGE-PCM-VS-BCM.md`](docs/VOLTAGE-PCM-VS-BCM.md). Tool:
[`data/voltage_compare.py`](data/voltage_compare.py).**

**The two supply channels can never be paired, and it is structural.** In the
one session carrying both they share a **145-minute** span and coincide **zero
times, even at a 30 s tolerance** — different pages of the app, and the PCM is
on HS-CAN while the BCM is on MS-CAN, so a bus-switching adapter makes
simultaneous sampling physically impossible. **No log will ever pair them.**

**Their distributions over the same window, engine confirmed running throughout,
do not overlap:**

| 2026-09-04, engine 602–812 rpm | n | median | **in 13.5–14.5 V** |
|---|---|---|---|
| `Control module voltage` (PCM) | 3,276 | **12.67 V** | **0.7 %** |
| `[BCM] Vehicle Battery Voltage` | 2,756 | **13.00 V** | **47.9 %** |

**The BCM is in the charging band about half the time; the PCM essentially
never.** And **the 13.8 V this file uses to explain the problem is not typical**
— the BCM median across 2,756 samples is **13.00 V**. The explanation rested on
one snapshot.

**THE CONTROL TRUCK DOES NOT SHOW THE GAP: PCM 13.47 V against BCM 13.40 V,
agreeing within 0.07 V** (n=10 and n=3 — a hint, not a measurement). The 2014's
two channels are five times further apart, and its PCM channel sits 0.80 V below
the control's.

**A candidate that fits: a voltage drop in the PCM's own supply or ground.**
That would be a real fault, and it matters because **every sensor reference
rides on that supply.** The alternative is that the channel reports a
post-regulator rail, in which case a fixed offset is normal.

**A meter across the battery posts at idle separates them in one minute** — it
measures the battery directly instead of asking two modules on two buses. Then
the ground-drop test if the battery is healthy while the PCM reads low.

**`Calculated boost` IS GARBAGE ON THIS TRUCK — never read it.** +0.256 bar at
idle, 0.17 to **7.08 bar** across sessions. A naturally aspirated engine at idle
is in vacuum. **Traced: the 2023 reports `Intake manifold absolute pressure`
(28–46 kPa, correct) and its boost is properly negative; the 2014 reports no
manifold pressure running, so the app computes from nothing.** Add it to the
app-arithmetic list.

**That makes manifold pressure the real gap, and the channel is NOT dead here** —
it answered 99 kPa with the engine at 0 rpm, correct atmospheric. It has never
been selected running. **Roughly 30–40 kPa at warm idle means the load signal is
finally available; still 99 kPa means the reporting path is genuinely wrong, and
THAT would be an engine-run problem** because load feeds fuelling and idle control.

**A POOLING ARTEFACT NEARLY BECAME THE HEADLINE — record the rule.** The first
pass pooled samples per truck and reported the 2014's oxygen sensor pumping
current at **−0.074 mA against the control's −0.012**, six times worse and 3.5×
more variable. **It was one session: 18,232 of ~18,500 pooled samples came from
the 09-04 log.** Per session, every later 2014 reading (−0.033, −0.029, −0.020)
sits on the control (−0.012, −0.008); the outlier is the pre-purge-valve session
with its known leak. **Aggregate as the median of per-session medians, never by
pooling samples — pooling weights by sample count and one long log becomes the
truck.**

**WHAT THE SWEEP CANNOT JUDGE.** The control has **two** sessions with settled
idle and most channels appear in only one, so nearly every comparison is n=1
against n=1. **And the four measurements most likely to show a combustion problem
have never been logged:** `[PCM] Currently Detected Engine Misfire`, the six
`[PCM] Cylinder N Acceleration Value` channels, `[PCM] Knock Sensor 1`/`2`, and
manifold pressure with the engine running. **Nothing measured shows a fault, and
the measurements that would show one have not been taken.**

## THE HICCUPS MEASURED — and the healthy truck has them too (2026-09-17)

**Full record: [`docs/IDLE-EVENTS.md`](docs/IDLE-EVENTS.md). Tool:
[`data/idle_events.py`](data/idle_events.py).** Owner asked whether saved data can
name what makes the engine hiccup. **It measures the events. It cannot name the
cause, and the reason is specific.**

**A HICCUP AND AN OSCILLATION ARE DIFFERENT SIGNALS.** Every metric in this file
describes a *continuous* wobble. The owner describes **discrete events**. A
detector for one does not find the other — this needed its own.

**THE EVENTS ARE REAL: 136 in 122 minutes of Park idle, median 31 rpm —
a rate of 1.114 per minute, one every 54 s.**

**CORRECTED 2026-09-18: this said "one every 84 s" and cited the "57 outliers,
median spacing 82.3 s" line as agreement. That was two different populations.**
The 84 s belonged to the 57 *large outliers*; the 136 is every detected event.
Quoting one population's count with another's spacing is not a match.

**AND THE SPACING CANNOT BE MEASURED ON THIS DATA AT ALL.** Idle in that session
is not one block — it is **65 separate stretches**, so any gap long enough to
matter is cut short by the end of its stretch. Restricting to pairs inside one
stretch drops a third of the gaps, and they are the long ones: median 9.6 s
against 14.8 s for all gaps, mean 13.4 s against 85.3 s. **That is right-
censoring, not a measurement.** A spacing column was added to the tool, checked,
and removed; the reasoning is in `data/idle_events.py` so nobody re-adds it.
**Use the rate, which divides events by idle time and is unaffected.**

**THEY ARE SHORT — 0.24 s at half height, about ONE ENGINE CYCLE (0.185 s at
650 rpm).** The flanking dips in the averaged shape were checked against the
filter and **are filter ringing, not a precursor** — a pure impulse produces them
too. The *width* survives the check, and it rules out every slow mechanism:
**air conditioning compressor 15.78 s (65× too slow), purge 10–30 s, the 0.33 Hz
dither 3 s (12× too slow), fan and coolant far slower.** Only a combustion-scale
event fits.

**BUT THE 2023 CONTROL HAS THEM AT THE SAME RATE AND SIZE.**

| | Events/min | Median size |
|---|---|---|
| 2014, **seven** sessions | **0.128 – 1.664** | 27.8–37.8 rpm |
| **2023 control, two sessions** | **0.368 and 0.954** | **29 and 39 rpm** |

**The two control sessions are the same healthy truck on the same evening and
differ by 2.6×. Both sit inside the 2014's own range. So event rate cannot
distinguish the trucks, and size is identical. By rate and size these events are
NOT the fault.**

*The size range excludes two 2014 sessions whose "median" comes from n=2 events
(174.6 and 319.6 rpm). Two events do not have a median worth quoting.*

**One weak thread survives: 105 dips against 77 rises on the 2014, 58 %,
p = 0.045** — the direction a weak combustion event gives, the opposite of a
momentary load release. **Control is 7 and 7, far too few to compare.**

**WHY THE CAUSE CANNOT BE EXTRACTED — the tiles law, again.** The only session
with hours of settled idle (09-04, 136 events) had **just `Engine RPM` polled
fast**; every other channel in that file had 13 samples or fewer. Every log
carrying fuel trim, timing or airflow at speed has **minutes** of idle at most.
Across all logs exactly one stretch has a channel densely co-sampled with engine
speed for 30+ minutes, and it contains **4 minutes of idle and 2 events**.

**A TRAP CAUGHT IN THE PROCESS, worth remembering:** run over that same stretch
without an idle restriction, the detector found 23 "events" at a 231.8 rpm
threshold with a fuel-trim difference at p < 0.001. **Those were throttle
transients** — the tip-in and overrun spikes this file already documents at
+9.38 % and −11.72 %. **An event detector run over a log containing driving will
find the driving.** Require idle across the whole neighbourhood, not at the centre.

**THE CAPTURE THAT ANSWERS IT: two tiles at 33 Hz, warm Park idle, THIRTY
MINUTES** — about 20 events, enough to test. The second tile is free and this
project has never spent it on a long idle session.
**First choice partner: `[PCM] Currently Detected Engine Misfire`** — in the
owner's sensor list and exactly the right timescale for a 0.24 s event.
**Not "never logged" — that was wrong, see the idle logging list above: 53
samples across 3 sessions, exactly 0.0000 in every one.** What is missing is a
capture long enough to overlap an event. Events run 0.44–1.66 per minute.
Then one `[PCM] Cylinder N Acceleration
Value` at a time; then `Timing advance`, which separates a real torque
disturbance (the governor answers) from a false reading (it does not).

## THE TRUCK WAS DYNO'D AND RETUNED ON 2026-09-16 — every baseline is now BEFORE/AFTER

**Full record: [`docs/DYNO-2026-09-16.md`](docs/DYNO-2026-09-16.md). Screenshot:
[`data/dyno-2026-09-16/`](data/dyno-2026-09-16/).** Dynojet, WinPEP 8, correction
factor STD, smoothing 5, 18:29, 38 °C ambient. Owner: *"Today i did dyno test and
we fix shifting pount and throttle response."*

| | Before (`RunFile_0`) | After (`RunFile_3`) | Change |
|---|---|---|---|
| **Peak power** | **227.16 hp @ 5400** | **250.34 hp @ 5800** | **+23.18, +10.2 %** |
| **Peak torque** | **225.03 ft-lb @ 4130** | **248.30 ft-lb @ 4020** | **+23.27, +10.3 %** |
| At 4665 rpm | 187.02 hp | 209.79 hp | **+12.2 %** |

Axis assignment verified, not assumed — torque × rpm ÷ 5252 reproduces both
cursor callouts to 0.01 %.

**TWO STATEMENTS IN THIS FILE ARE NOW OUT OF DATE.** It says in three places that
this truck has **"no aftermarket tune"** and lists **"PCM tune"** among the items
eliminated. **The calibration was deliberately changed on 2026-09-16.**

**CONSEQUENCE, AND IT APPLIES TO EVERY NUMBER BELOW THIS LINE.** Every measurement
in this repository was taken on the **previous calibration** — the idle governor
gain, the 0.33 Hz oscillation, the ±0.9° spark authority, the trims, the inferred
ethanol value, the first-order content in engine speed. **All of it remains valid
as history and NONE of it is a valid comparison for anything captured from
2026-09-16 onward** unless that capture is labelled post-tune.

**This file ASKED for a calibration change and called it the only legitimate lever
on this idle** — *"A Ford calibration update... the only legitimate lever on
dither amplitude and governor gain."* **Something in that family has now happened
by a different route. Whether it touched idle at all is unknown and is directly
testable.**

**THE PARK IDLE SHAKE SHOULD NOT BE EXPECTED TO CHANGE.** Shift points do not
apply in Park; a throttle map does not apply at a closed throttle. Unchanged
tomorrow is the expected result, not a failure.

**BUT THE THROTTLE CHANGE TOUCHES A STANDING COMPLAINT.** The owner's *"it is hard
for me to adjust the RPM at 1000 because something is working on behalf of me"* is
a pedal-to-plate complaint on a drive-by-wire throttle, and that mapping is
exactly what was altered. **Ask whether holding 1000 and 1500 feels different now.**

**THE SENSOR SWAP EXPERIMENT SURVIVES.** A calibration applies to both banks
equally, so a bank-versus-bank difference is not destroyed by it. **What would
destroy it is an adaptive memory reset, which tuners routinely do when flashing.
Establish that before reading any trim** — this file's rule *"never wipe the
adaptive memory before a measurement unless the wipe is the experiment"* has now
been at risk twice in three days without anyone asking.

**`Air/Fuel Ratio 1` read 14.84 before and 12.78 after, at 4665 rpm. DO NOT ACT
ON IT — the source is unknown.** If it is a dyno wideband it is an independent
measurement that **contradicts this file's own "12.3:1 commanded and delivered at
wide throttle"**, which would be the two-sensors-disagreeing evidence this file
says has never been captured. If WinPEP read it from the OBD port it is not
independent and means only that the tune changed the command. **One question to
the shop decides which.**

**AND AN ESTIMATE MUST STOP BEING QUOTED AS A MEASUREMENT.** This file says
*"215 g/s × ~1.4 ≈ 301 hp against a 302 hp rating"*. That is airflow arithmetic
with a rule-of-thumb multiplier. There is now a real dynamometer number: **227
hp at the wheels, 75 % of the 302 crank rating, rising to 83 % after the tune** —
consistent with an ordinary 4x4 driveline loss, and it does **not** establish a
power deficit, because whether it ran in two or four wheel drive is unrecorded.

## HOW TO CAPTURE — the sample rate is set by TILES ON SCREEN, not by the sensor list

**Measured across 265 one-minute windows in 10 logs (2026-09-14).** This
overturns the standing "Car Scanner samples each channel at ~17 Hz" claim: there
is no fixed rate. **Car Scanner polls only the channels visible on the page the
owner is looking at**, so the rate is set by how many tiles are on screen.

| Channels polled at >= 1 Hz | Windows | Median `Engine RPM` rate | p10-p90 |
|---|---|---|---|
| **1** | 1 | **33.3 Hz** | flat 30.0 ms |
| **2** | 6 | **32.9 Hz** | 15.7-33.2 |
| 3 | 100 | 15.5 Hz | 13.2-22.9 |
| 4 | 79 | 10.9 Hz | 7.7-16.1 |
| 5-6 | 46 | 8.0 Hz | 5.0-10.3 |
| 7-9 | 5 | 2.1 Hz | 1.1-9.4 |

**ONE CHANNEL WAS MEASURED ON 2026-09-14 AND IT IS NOT FASTER THAN TWO.**
`data/carscanner/2026-09-14-rate-test/`. `Engine RPM` alone gave 1,861 samples
at a flat **30.0 ms — 33.3 Hz**. Two channels gave 32.9 Hz. **33 Hz is the
adapter's ceiling, not a budget divided between channels, so the second tile is
free.** Keep capturing two.

**The law is now proven INSIDE a single file**, which no earlier measurement
was. In `2026-09-14_14-43-48`, three extra channels sat on the page for the
first 2.7 s and then left it: `Engine RPM` ran at **8.4 Hz** while they were
there and **33.3 Hz** immediately after. Same drive, seconds apart, four times
faster.

**Two of that day's four captures recorded no engine channel at all** — only
GPS and the app's own fuel arithmetic. **A recording is only as good as the page
left on screen.** Confirm the tiles are showing before pressing record.

**The cliff is between 2 and 3 — the rate more than halves.** Every fast window
in the project (33.2, 32.9, 30.9 Hz) had exactly two polled, all in the 09-04
log. Direct check inside that log's 33 Hz stretch: of 87 channels in the file,
`Engine RPM` had 18,016 samples, `Control module voltage` 16,579, and **every
other channel had 13 or fewer.** The rest were configured but idle.

**Consequences:**
* **Nothing needs deleting from the sensor list.** Show two tiles and stay on
  that page.
* `Engine RPM` and `Engine RPM x1000` are **one request** reported twice.
* The fast stretches ended because the owner navigated away. **A long capture
  needs the phone left alone** — screen kept awake, no page switching.
* This also explains why channels in these logs so rarely overlap in time: only
  the visible page was ever being polled, so two channels on different pages have
  zero simultaneous samples by construction. **Four false findings in this
  project came from comparing channels that were never polled together.**

## THE CSV CONFIRMS THE SWAP RESULT, AND THE MEMORY WAS WIPED (2026-09-17)

**Full record: [`docs/DYNO-WINDOW-LOGS.md`](docs/DYNO-WINDOW-LOGS.md). Logs:
[`data/carscanner/2026-09-16-17-dyno-window/`](data/carscanner/2026-09-16-17-dyno-window/).**
Three logs around the 18:29 retune — **one 34 minutes before it, two after.**
**Neither post-retune log can answer the bank question:** 22:10 was taken with the
engine OFF (`Engine RPM` 0 in all 63 samples), and 00:49 carries only Bank 1,
n=8.

**THE ADAPTIVE MEMORY WAS WIPED — not merely a code clear.** `Long term fuel %
trim` reads **exactly 0.0000 on BOTH banks across all 213 samples**, which is the
test this file named in advance. The counters agree: **364 km / 7 warm-ups on
09-14 → 142 km / 0 now**, matching the signature of the 09-05 and 09-09 resets
exactly. **Short term trim is therefore carrying the whole correction alone**,
which is why it swings −20.31 to +15.62 % here.

**THE BANK OFFSET CLAIM FROM THIS LOG IS WITHDRAWN — see
[`docs/BANK-OFFSET-WITHDRAWN.md`](docs/BANK-OFFSET-WITHDRAWN.md) (2026-09-18).**
This section previously read *"CONFIRMED ON BANK 1 — +0.621 %, n=1,711"* and
called it corroboration that the offset followed the hardware. **It was neither
confirmed nor at settled idle.**

| Minute | Engine speed | Bank 1 − Bank 2 | |
|---|---|---|---|
| 17:55 / 17:56 / 17:57 | **ZERO samples** | +0.703 / +0.607 / +0.607 % | condition unknown |
| 17:58 | **4 samples** | +0.781 % | n=2 after the guard band |
| 17:59 / 18:00 / 18:01 | sampled, guard-band clean | **−0.308 / −1.136 / −0.977 %** | **Bank 2 needs more** |

**The 1,711 samples were the minutes with no engine speed on the page.** The
"confirmed idle" rested on **four** samples in the last of them. Where engine
speed does exist the sign is the other way, at n=140.

**Neither half is clean** — the rpm-bearing minutes are the ones holding the
throttle blips, and short term trim lags engine speed by 0.65 s, so a 2 s guard
band may not clear a recovery from 1,314 rpm. **The post-swap bank offset at
settled idle has never been measured.**

**THE SIGN REVERSES UNDER THROTTLE MOVEMENT.** During the blips Bank 2 needs
more. **That is tip-in and overrun, not a bank property** (this file already
records a +9.38 % tip-in spike and a −11.72 % overrun crash). **A whole-session
average is condition-soup** — mixing everything gives +0.480 %.

**METHOD WARNING THAT COST A WRONG INTERMEDIATE ANSWER HERE:** selecting idle
samples by the **time span** of the qualifying engine-speed readings sweeps in the
blips between them. **Select by each sample's own condition, never by a window
bounded by qualifying samples** — and require idle across a guard band, not just
at the centre sample.

**TWO OF THE FOUR MISSING CROSS-CHECKS ARE NOW DONE.** `Engine coolant
temperature` vs `[PCM] Cylinder head temperature`: identical in **99.5 %** of
1,679 pairs, never over 1 °C apart. **This clears nothing** — Ford derives coolant
temperature from the cylinder head sensor on several engines, and if it does here
these are one measurement on two channels, **the same trap the catalyst channels
turned out to be.** [VERIFY whether this engine has a separate coolant sensor.]
`Intake air temperature` sits **19 °C above ambient** — ordinary heat soak on a
stationary engine; the r = −0.959 is both channels following time in opposite
directions, not a relationship.

**PARTIAL CORRECTION TO THE CATALYST FINDING.** This file calls the two catalyst
temperature channels *"one computed value printed on two channels."* Here, n=3,359:
r=0.9999 but **identical in only 53.2 %**, differing **−6 to +9 °C**. **They do
diverge** — still far too coupled to be independent evidence, but not one value
copied twice.

**`Ethanol fuel percent` = 18.43 %, a FOURTH discrete value** (byte 47), after
9.80, 19.22 and 22.35.

## DOES FLIPPING THE SENSORS CHANGE ANYTHING? UNEVALUATED — and the claim that it did is WITHDRAWN (2026-09-18)

**Full record: [`docs/BANK-OFFSET-WITHDRAWN.md`](docs/BANK-OFFSET-WITHDRAWN.md).
Tool: [`data/bank_offset.py`](data/bank_offset.py).** Owner asked directly. Every
session that ever polled both banks was re-derived, and the finding does not
survive.

**THIS SECTION PREVIOUSLY SAID THE OFFSET FOLLOWED THE HARDWARE AND NAMED A
PART** — *"the upstream oxygen sensor that used to be on Bank 2 and is now on
Bank 1"*, on Bank 2 +1.95 % before against Bank 1 +0.58/+0.62 % after. **Three
errors, each sufficient on its own.**

**1. IT READ SHORT TERM TRIM ALONE AFTER LONG TERM HAD LEARNED.** The two halves
trade off — this file has said so since 09-09. On the 09-17 log long term has
**re-learned asymmetrically**: Bank 1 **−3.125 %**, Bank 2 **−2.344 %**, in 4,615
of 4,631 samples, pointing the **opposite way** to short term.

| 2026-09-17, n=4,484 paired | |
|---|---|
| Short term, Bank 1 − Bank 2 | **+1.116 %** |
| Long term, Bank 1 − Bank 2 | **−0.781 %** |
| **TOTAL correction difference** | **+0.336 %** |

**Long term absorbs 70 % of it.** Only the total is comparable across sessions.

**2. THE PRE-SWAP BASELINE WAS NOT ONE SESSION.** `docs/READINGS-SCAN.md` says
*"only ONE session in the entire project ever polled both short term trims
together."* **Twelve do.** That scan globbed `*.csv` and **the others are stored
gzipped or zipped — it read 2 of 12 files.** Standing rule: **glob `**/*` with no
extension filter, or use `carscanner_lib.logs()`, which handles all three.**
`data/idle_sweep.py`, `data/idle_events.py` and `data/rpm_rate.py` were checked
and already do this; the fault was in the scan, not the tools.

**3. THE OFFSET CHANGES SIGN INSIDE ONE CONTINUOUS SESSION.** The largest paired
dataset in the project had never been analysed — **2026-09-04, 3.2 h of unbroken
Park idle, 1,746 guard-band-clean samples.** Long term sits *fixed* at
+3.125 / +2.344 throughout, so this drift is entirely in short term:

| Block | short B1 | short B2 | **TOTAL B1−B2** |
|---|---|---|---|
| 1 | −0.467 | −0.518 | **+0.722** |
| 2 | −0.038 | −0.107 | **+0.851** |
| 3 | +0.572 | +1.818 | **−0.515** |
| 4 | +1.069 | +3.273 | **−1.423** |
| 6 | +0.502 | +2.593 | **−1.368** |

**It crosses zero mid-session with nothing done to the truck — range +0.85 to
−1.42, 2.3 points.** The swap was being judged on well under one point.

**AND IT IS NOT A SETTLING CURVE THAT COULD BE WAITED OUT.** The two long
sessions drift in **opposite** directions — at 60–75 minutes in, 09-04 reads
**+0.852** and 09-17 reads **+0.994**, but 09-04 then goes to **−1.379** by minute
150 while 09-17 never does. There is no settled value to compare.

| Session | Era | Total at guard-band idle | n |
|---|---|---|---|
| `2026-09-04 22-23-38` | pre | **−0.466 %** (range +0.85 … −1.42) | **1,746** |
| `20260905_041723` | pre | −1.373 % | 42 |
| `20260908_154859` | pre | +0.220 % | 42 |
| `2026-09-16_17-54-19` | **post** | −0.686 % | 140 |
| `2026-09-17_15-49-53` | **post** | +0.336 %, **no idle confirmation** | 4,484 |

**EVERY POST-SWAP NUMBER SITS INSIDE THE RANGE THE TRUCK COVERED BEFORE THE SWAP,
WITHIN A SINGLE SESSION.**

**THE SWAP IS UNEVALUATED, NOT REFUTED.** A sensor bias may well have moved;
nothing measured can currently see it. **Do not quote a single number for "the
bank offset" again** without naming the session and where in that session it sits.

**WHAT SETTLES IT — and it now needs two runs, not one.** Three tiles, three
minutes, warm Park idle, **do not touch the throttle**:

```
Short term fuel % trim - Bank 1
Short term fuel % trim - Bank 2
Engine RPM
```

then the same again with `Long term fuel % trim - Bank 1` and `- Bank 2`.
**All four are needed and four tiles costs too much rate to run at once.**
**Engine speed must be on the page** — without it the capture cannot be read,
which is the fourth time this project has learned that lesson.

## THE SENSOR SWAP — the decisive experiment, PREDICTION LOCKED BEFORE THE DATA (2026-09-16)

**Owner changed the intake gaskets AND swapped all four oxygen sensors side for
side — every sensor moved to the mirror position on the opposite bank.**

**This makes the driver-side offset decidable for the first time.** The project
has carried two candidates for it since 09-09 and no measurement could separate
them:

* **A real physical difference on that side** — a leak, an exhaust leak upstream
  of the sensor, anything bolted to that bank. **Stays with the BANK.**
* **A lean-biased Bank 2 sensor.** **Moves with the SENSOR.**

**They now sit on opposite sides of the engine. One reading separates them.**

### THE SHAKE CANNOT BE ANSWERED FROM THIS CAPTURE — owner asked, 2026-09-16

**The owner asked whether the data can tell him if the shake is present. It
cannot, and saying otherwise would be inventing it.** This file settled the point
twice with two natural experiments: the mounts killed the felt shake and left the
oscillation unchanged; the battery quietened the oscillation and left the shake.
On 09-09 the owner reported the shake back while the oscillation had not returned
— quiet versus relapsed, **Mann-Whitney p = 0.633.**

**The physics agrees.** The oscillation is 0.3 Hz; what shakes a seat is 10-33 Hz;
the port cannot resolve those frequencies at all.

**The phone accelerometer is the instrument for it, and it is the only test in
this investigation aimed at the actual complaint.** Phone flat on a rigid surface,
warm Park idle 60 s, then Drive on the brake 60 s. At ~650 rpm: **~33 Hz** is the
firing pulse and normal in a bare cab · **~11 Hz** is rotational imbalance ·
**~5.5 Hz** is one cylinder differing · **8-15 Hz** is engine rock on the mounts.
**Also look for the amplitude rising and falling every ~3 s** — that would tie the
felt shake to the 0.3 Hz oscillation for the first time.

### THE PREDICTION, written down before the reading exists

**OUTCOME, 2026-09-18: the third branch is the one that came true, and this table
named it in advance.** *"Both banks equal — either the gasket closed a real leak,
or the offset was never robust."* **It was never robust.** The bank difference
changes sign inside a single 3.2-hour session, by 2.3 points, with nothing done
to the truck — a range wider than anything the swap could have produced. The
first two branches both assumed a stable offset to move, and there is not one.
See [`docs/BANK-OFFSET-WITHDRAWN.md`](docs/BANK-OFFSET-WITHDRAWN.md).

**The table below is kept as written, because a locked prediction must not be
edited after the fact.** Read it as the prediction it was, not as a verdict.

| `Short term fuel % trim` at warm Park idle | What it proves |
|---|---|
| **Bank 2 still needs more fuel** | The offset lives with the **BANK**. **Sensor bias ELIMINATED.** Physical, on that side — and the new intake gasket did not fix it. |
| **Bank 1 now needs more fuel** | **The offset MOVED WITH THE SENSOR. A lean-biased sensor is PROVEN.** Four sightings of a "driver-side lean offset" become one biased part. |
| **Both banks equal** | Either the gasket closed a real leak, or the offset was never robust. **Cannot separate these two without the pre-swap baseline**, and the gasket change is a second variable. |

**THE CONFOUND, stated plainly: two things changed at once.** New intake gaskets
and swapped sensors, in one operation — exactly the mistake this file recorded
after the purge valve went in with a memory wipe. **It does not spoil this test**,
because the question "which SIDE does the offset live on" is answerable whatever
the gasket did to the overall level. It does spoil any conclusion about whether
the gasket fixed a leak.

### What must be captured, and what must NOT happen first

**OWNER CONFIRMS: the battery was NOT disconnected, but the shop may have
cleared the codes** (2026-09-16).

**A code clear is NOT a memory wipe, and the difference matters here.** Clearing
removes the codes, the freeze frame, monitor readiness, and the distance and
warm-up counters. **It does not remove the learned adaptive fuel tables** — those
need a battery disconnect or a specific adaptive-reset function, and neither was
done. **So the learned trims should have survived**, which makes the pre-swap
values a live baseline rather than an erased one. That is the better case for
this experiment.

**Two readings establish which state the truck is actually in**, and both belong
on one page:

```
Distance traveled since codes cleared
# warm-ups since codes cleared
```

They read **364 km and 7 warm-ups** on 09-14. **Near zero now means the shop
cleared.** And if `Long term fuel % trim` reads **exactly 0.0000 on both banks**,
the adaptive memory went with it after all — which would change how every other
number in the capture must be read.

**Short term trim answers the swap question either way.** It does not depend on
learning.

**Short term trim is the channel that answers this.** It does not depend on
learning. Long term needs a relearn drive before it means anything.

## FIRST ORDER IS VISIBLE IN THE RPM CHANNEL — a standing ruling is WITHDRAWN (2026-09-16)

**Full analysis: [`docs/RPM-ORDER-ANALYSIS.md`](docs/RPM-ORDER-ANALYSIS.md).
Tool: [`data/order_track_rpm.py`](data/order_track_rpm.py).**

**This file says in five places that the OBD port cannot reach the frequencies
that shake a cab. Every one of those rulings uses Nyquist 8.3 Hz, from the
~17 Hz sample rate that was overturned on 2026-09-14.** At the proven **33.3 Hz**
Nyquist is **16.65 Hz**. **First order at 650 rpm is 10.8 Hz — it is inside**,
and so is the whole 8–15 Hz engine-rock band. Nobody re-tested after the rate
law changed.

**Re-tested now, by resampling engine speed onto uniform crank angle** so orders
become fixed lines instead of smearing as idle wanders:

| Order | Means | Lands at | **Amplitude** |
|---|---|---|---|
| **1.0 first order** — rotational imbalance | damper, pulley, flexplate | **exactly 1.000, 11 of 11 stretches**, median 3.95× background | **0.173 rpm** |
| **0.5 half order** — one cylinder differing | a weak cylinder repeats once per engine cycle | 0.470–0.500, 7 of 10 at idle, **absent at 900 rpm** | **0.576 rpm** |
| **3.0 firing** | the buzz that is actually felt | **unreachable — needs 65 Hz** | — |

**First order is not an alias.** A folded order moves when the sampling ratio
changes. The 899.6 rpm stretch runs at a **38 % different ratio** and first
order **stayed on exactly 1.000**, with the strongest line of the set. It is
real, repeatable and measurable through the port.

**BUT THE AMPLITUDES ARE TINY AND THERE IS NO CONTROL.** 0.173 rpm against a
19 rpm slow oscillation — **110× smaller**. The 2023 has no 33 Hz stretch, so
whether that is normal is **unknown**. **Do not read the small number as a
healthy engine:** flywheel and converter inertia absorb a per-cylinder torque
difference almost entirely, which is precisely why it takes an accelerometer to
feel what the crank barely registers. **Engine speed is the wrong end of the
mechanism to judge cab vibration at.** The half order line is weaker still —
it wanders, and the aliasing test that cleared first order has not been passed
for it.

**What it is genuinely good for: every stretch above is from 2026-09-04 —
before the mounts, the battery, the intake gasket and the oxygen sensor swap.**
It is a banked pre-repair baseline in the band of the actual complaint, and it
reruns in one command. **A fresh `Engine RPM`-alone capture is directly
comparable.** Five minutes warm Park idle, plus two minutes held at ~1200 rpm —
at 1200 a fold would move, which is the one test the existing data cannot do.

**Standing correction: before writing that a frequency is out of reach, check it
against 16.65 Hz, not 8.3.** Firing order is still out. First order is not.

## FULL SCAN OF EVERY READING — [`docs/READINGS-SCAN.md`](docs/READINGS-SCAN.md) (2026-09-15)

**Every numeric value in all 44 sessions, 129 channels, statistics on raw samples.**

**THE ONE NEW FINDING: the PCM re-learns an ethanol content of 19-22 % after every
refuel, and it resets to 9.80 % on a memory wipe.** Three discrete values across
every session ever logged - bytes 25, 49, 57. It jumped **9.80 -> 22.35 %** across
a fill that took the tank from 29 % to 86 %, and at 22.35 % **both banks' long term
trims are the most negative in the entire dataset**. On E0 fuel a 22 % estimate
targets roughly 13.5:1 instead of 14.7:1 - about 9 % more fuel commanded, which
closed loop corrects and open loop does not.

**THE 2023 CONTROL TRUCK ALSO REPORTS ETHANOL - 11.37 %** (byte 29, n=116,
constant). **Neither truck reads zero**, and the healthy one's value sits INSIDE
the 2014's own range. **A non-zero ethanol estimate is therefore not a fault
marker** - the smooth truck has one too. It raises the real possibility that
Saudi pump fuel does contain roughly 10 % ethanol, which this file has denied as
fact without ever checking. It does not settle it: the 2023 infers the same way,
and two PCMs using one method are not two measurements. **The 2014 still reads
roughly double the 2023 at its highest, and that gap is the part worth
explaining.** The water test answers both trucks at once.

**The 2023 also confirms `Long term secondary oxygen sensor trim` Bank 1 and
Bank 2 at exactly 0.0000** across 116 and 108 samples.

**And a caution against this file's own trim reasoning: across that session the
2023's long term trims ranged -5.47 to +5.47 %** - wider excursions than anything
the 2014 has shown. Conditions were not matched, so it is not a like-for-like
comparison and must not be used as one; it is recorded because **the healthy
truck's trims are not tidier than the sick one's.** The bank comparison on the
2023 could not be done at all - only 10 paired samples at settled idle - so
**whether a healthy F-150 carries a bank offset is still unknown.** And the
2014's own +1.95 % no longer needs a control to be doubted: its bank difference
**changes sign inside a single session** — see
[`docs/BANK-OFFSET-WITHDRAWN.md`](docs/BANK-OFFSET-WITHDRAWN.md).

**THERE IS NO ETHANOL SENSOR ON THIS TRUCK.** Ford deleted the physical fuel
composition sensor on 2004-and-newer vehicles; the PCM infers the value from
oxygen sensor feedback and how the trims settle after a refuel. **So it cannot be
reading wrong, and it cannot say what is in the tank.** A reading of 22.35 % means
only "after the last fill this engine behaved as though it needed more fuel than
my model predicted" - **the lean bias restated in different units, not independent
evidence of a second problem.** Stop treating it as a separate anomaly.

**Where it still does damage: open loop.** Closed loop drives to lambda 1 whatever
the PCM believes; the first ~20 s of a cold start and wide open throttle do not.

**"Saudi pump fuel is normally E0" is an ASSUMPTION this file has repeated as
fact and nobody has ever checked.** A search returned Aramco octane grades and no
ethanol specification.

**SETTLE IT WITH THE WATER DILUTION TEST - ten minutes, no tools.** 10 ml water in
a graduated cylinder, top to 100 ml with fuel, invert ten times, stand five
minutes, read the water layer. Unchanged at 10 ml = E0 and the PCM's estimate is
wrong. About 32 ml = E22 and the estimate is right and the whole line closes.
**Cheapest remaining test in the investigation.** Full procedure in the scan file.

**It is still a learned value that wipes and climbs back - the signature this
investigation has chased since the D/R relapse.** Not proof: the shake returned on
09-09 while the estimate was still 9.80 %.

**BANK 2 NEEDED +1.95 % MORE FUEL THAN BANK 1 ON 2026-09-05**, paired within
0.15 s at settled idle, n=108, t=15.5, p=3.4e-29. **This one reading stands.**

**BUT THE CAVEAT PRINTED HERE WAS WRONG AND IT MATTERED.** It said *"only ONE
session in the whole project ever polled both short term trims together at
idle."* **Twelve sessions carry both channels** — the scan that produced that
claim globbed `*.csv` and every one of the others is stored **gzipped**. Across
them the offset **does not hold a sign**: it is already on Bank 1 by 09-08, three
days before any sensor was touched. **It is not a "fourth sighting of a
driver-side offset"; it is one solid reading surrounded by unstable ones.** See
[`docs/BANK-OFFSET-WITHDRAWN.md`](docs/BANK-OFFSET-WITHDRAWN.md).

**TWO CHANNELS MUST STOP BEING READ AS ABSOLUTE NUMBERS.**
`Throttle Position Actually` exceeds 90 degrees in 2.67 % of samples, maximum
**127.99** - a throttle plate cannot do that, so the scaling is not plate angle.
Use it only as "does it move". And both downstream oxygen sensor voltage channels
reach **1.275 V**, above what a narrowband zirconia sensor can produce.

**A LOOMING ARTEFACT WAS CAUGHT.** `[PCM] Cylinder 6 Acceleration Value` spans
-0.452 to +0.374, six to ten times the others - entirely because it was the only
cylinder still polled after a throttle lift. In the one window all six share it is
ordinary. **In that window cylinder 5 is the outlier; the screenshot and Mode 06
both named cylinder 4.** Three looks, two cylinders, n=8. That is noise.

**THE FOUR SUPPLY VOLTAGE CHANNELS SPAN 1.26 V** and three of the four pairings
were never polled together. Any electrical reasoning that mixed them is unsound.

**Also still open: the right front tyre is 211.7 kPa against 237.5 on the left and
a 241 label.** Unchanged since the first scan.

## TRANSMISSION FLUID TEMPERATURE - highest ever recorded is 92.75 C (2026-09-15)

`ATF temperature var.3`, in `20260905_041723`, at **61 km/h and 1449 rpm**.
`[PCM] ATF Temperature` peaked at 63.06 C in a different session.

**Not a concern** - ordinary for a 6R80, and **the 2023 control reached 97.12 C
on the same channel**, hotter than the 2014 has ever been recorded. The truck
attribution was checked explicitly; a mixed sweep would have returned the 2023's
number.

**It is the highest RECORDED, not the highest REACHED.** The maximum came from a
steady cruise - the easiest condition a torque converter sees - from 22 samples
out of 1,806. **This truck has never been logged towing, climbing, or in stopped
traffic with the air conditioning loaded.**

**The two channels have never been polled together** - zero simultaneous samples -
so the 29 C gap between their maxima cannot be attributed and neither should be
quoted against the other.

## IS A SENSOR LYING? NO CLEAR CLUE - and one piece of evidence is VACUOUS

**Cross-checked every pairing of channels that must physically agree.** Full
table in [`docs/READINGS-SCAN.md`](docs/READINGS-SCAN.md).

**CORRECTION - CATALYST TEMPERATURE IS MODELLED, NOT MEASURED.** The two banks'
values are **exactly equal in 78.3 % of 1,494 paired samples**, r = 1.000, and
the rest differ by at most 1.5 C. Two separate sensors in different thermal
environments cannot do that. **It is one computed value printed on two channels.**
This file cites "catalyst temps identical both banks" as evidence of health in
two places. **That evidence is worthless** - identical is what a shared
calculation produces whatever the catalysts are doing.

**Both upstream oxygen sensors track together** - 1,192 paired samples, r = 0.986,
mean difference 0.01, and Mode 06 timed both at 0.014 s against a 0.4 s limit.
Neither is lazy. **But this does NOT rule out a biased sensor and must not be read
as if it does:** in closed loop each bank is driven to stoichiometric by its own
trim, so a lean-reading Bank 2 sensor would have the PCM add fuel until that
sensor reads stoichiometric - both sensors agree and Bank 2's trim sits positive,
which is exactly the observed pattern.

**FOUR OF SEVEN CROSS-CHECKS HAVE ZERO PAIRED SAMPLES.** Coolant against cylinder
head temperature, intake air against ambient, and the two load channels were
never polled together. **The comparisons that would most directly expose a lying
sensor are the ones nobody has captured.**

**No clue is present that would name one:** no code on any powertrain circuit
ever, no two sensors of the same quantity disagreeing, nothing out of physical
range that the reporting path does not explain, no monitor short of margin.

**The one sensor that fits the symptom cannot be tested through the port** -
crankshaft position. The timing light against `Engine RPM` at idle and a held
1500 is the test, and it has been outstanding since night one.

**THE CAPTURE THIS SECTION USED TO NAME CANNOT BE TAKEN.** It asked for
`Barometric pressure` + `Intake manifold absolute pressure` with the engine off,
to cross-check one against the other. **The second channel does not exist on this
truck** — it is 2023-only (owner correction, 2026-09-17). The 97 kPa barometric
reading has nothing here to be checked against, and a mechanical vacuum gauge is
the only route to manifold pressure.

## THE SENSOR INVENTORY — [`docs/SENSOR-INVENTORY.md`](docs/SENSOR-INVENTORY.md)

**One reliable list, built 2026-09-14 from all 44 logging sessions AND all 279
unique screenshots. Read it before claiming any measurement is out of reach.**
129 channels answer on this VIN: **75 that move**, **21 that returned a constant
in every sample they ever produced**, and **33 that are the app's own arithmetic
and must never be analysed as vehicle data.** Beyond those, **7 channels plus 12
`[BCM]` start/stop flags are offered by the app and left blank by the truck** —
findable only in screenshots, because a channel that returns nothing never
reaches an export.

**It also carries the graph-header to sensor-list mapping**, taken from the
screenshots themselves. `CLAUDE.md` forbids asking the owner for a graph header
and this project has broken that rule repeatedly; the table is the fix.

**Three things it settles:**

* **`Long term secondary oxygen sensor trim Bank 1` and `Bank 2` have never been
  selected on THIS truck.** The two files carrying them are the **2023 control**.
  Their status here is **unknown, not unsupported** — every statement in this
  file that treats them as read or as absent is withdrawn. Search the sensor list
  for `secondary` to settle it.
* **Per-cylinder contribution already logged**, in `2026-09-14_14-49-23`, all six
  `[PCM] Cylinder N Acceleration Value` channels, quantised at ~0.0156. Too few
  samples to analyse; enough to prove it needs no FORScan.
* **`PCM Odometer` reads 131,313 km.** Use that, not "131,000".

**It also names the collisions that have been silently mixed in this file:**
seven throttle channels in two different units; `Calculated engine load value`
69.02 % against `Absolute load value` 14.12 % at the same instant; four supply
voltage channels; two transmission fluid temperature channels. **Every figure
quoted anywhere must say which channel it came from.**

**MANIFOLD PRESSURE — the one blank channel that touches this investigation.**
Manifold vacuum is the variable the symptom tracks, and the truck has never
reported it once while running. `Manifold absolute pressure (high resolution)`
was **blank with the engine turning at 661 rpm**, so it is unsupported here.
**`Intake manifold absolute pressure` IS NOT A CHANNEL ON THIS TRUCK — the
"99 kPa in all 16 samples" belongs to the 2023 control** (owner correction,
2026-09-17; a raw header scan finds it in exactly three files, all three the
control). Every statement that this truck's copy is "untested, not dead" is
**WITHDRAWN**, and so is the one-minute capture built on it.

**Manifold pressure is genuinely unavailable here. A mechanical vacuum gauge is
the only route.**

**Nothing else blank or absent is powertrain.** Three DPF counters for a diesel
filter this engine does not have, `Oil Life %`, two ABS wheel speeds and the
steering angle (chassis, and the symptom reproduces at a standstill in Park), and
twelve `[BCM]` flags for an automatic stop/start system this truck does not have.

**And the limit: no channel on this truck reports crankshaft or camshaft sensor
signal quality, injector pulse width, coil dwell, or plausible fuel rail
pressure.** The crank-signal hypothesis cannot be tested through the port.

## A `[PCM]` CHANNEL FAMILY EXISTS THAT THIS PROJECT NEVER KNEW ABOUT (2026-09-14)

**Twelve screenshots of the owner's sensor list show a block of channels
prefixed `[PCM]` that appear in no log, in no analysis, and in
`docs/scanner-pids.md` nowhere.** Several of them read values this project spent
weeks saying were unreachable without FORScan.

| Channel, as the sensor list spells it | Observed |
|---|---|
| **`[PCM] Cylinder 1 Acceleration Value`** | −0.03 |
| **`[PCM] Cylinder 2 Acceleration Value`** | −0.02 |
| **`[PCM] Cylinder 3 Acceleration Value`** | −0.03 |
| **`[PCM] Cylinder 4 Acceleration Value`** | **−0.08** |
| **`[PCM] Cylinder 5 Acceleration Value`** | −0.02 |
| **`[PCM] Cylinder 6 Acceleration Value`** | 0 |
| `[PCM] Desired Electronic Throttle Control` | 15.31° / 19.55° |
| `[PCM] Actual Electronic Throttle Control` | 15.25° / 19.62° |
| `[PCM] Knock Sensor 1` / `[PCM] Knock Sensor 2` | 323 / 336 (raw, no units) |
| `[PCM] Currently Detected Engine Misfire` | 0 |
| `[PCM] A/C Pressure` | **1282 kPa — the unprefixed one is dead, this one is not** |
| `[PCM] Cylinder head temperature` | 83 °C |
| `[PCM] ATF Temperature` | 62.81 °C |
| `[PCM] Actual Turbine Shaft Speed` | 1458 rpm |
| `[PCM] Actual Output Shaft Speed` | 2117.75 rpm |
| `[PCM] Actual Torque Converter Slip` | 12 rpm |
| `[PCM] Desired Torque Converter Slip` | 10.25 rpm |
| `[PCM] Commanded Gear Ratio` / `[PCM] Commanded Gear` / `[PCM] Measured Gear Ratio` | present |
| `[PCM] Battery voltage` | 12.7 V |
| `[PCM] Fuel level` | 86.27 % |

### `[PCM] Cylinder N Acceleration Value` is per-cylinder contribution

**This is the measurement the investigation has wanted since night one.** It is
what the injector-kill balance test approximates by hand and what the
accelerometer test tries to infer from the outside. `CLAUDE.md` and
`docs/DATA-REQUESTS.md` both say per-cylinder contribution needs FORScan and
manufacturer-specific addressing. **It is in the owner's app.**

**Cylinder 4 read −0.08 against −0.02 and −0.03 for its neighbours — roughly
three times the others.** Mode 06 logged **2 misfire counts on cylinder 4**, the
highest of the six, with everything else at 0 or 1. Those are two independent
tools naming the same cylinder.

**DO NOT TREAT THIS AS A FINDING YET.** It is one snapshot off a screenshot, the
units are undocumented, the sign convention is unknown, the engine condition at
that moment was not recorded, and six numbers with no repeat tell nobody
anything. **It is a lead, and it is the strongest-shaped lead available.**

**What it needs:** `Engine RPM` plus one `[PCM] Cylinder N Acceleration Value`
at a time, warm Park idle, two tiles, 33 Hz, one minute each — six captures.
Then the same six again after a stop and restart. A real weak cylinder repeats;
an artefact does not.

### What is still NOT in the list

`Long term secondary oxygen sensor trim Bank 1` and `Bank 2` appear in **none**
of the twelve screenshots. Outstanding capture #2 may not be possible on this
truck. Confirm by searching the sensor list for `secondary` before removing it
from the protocol.

`Oxygen sensor 2 Bank 1 Short term fuel trim` and `Oxygen sensor 2 Bank 2 Short
term fuel trim` are in the list but read **n/a %** — the truck answered "not
supported". That is a different thing from the channel being absent.

### Standing correction this forces

**The phrase "the OBD port cannot see it" appears repeatedly in this file and
has now been wrong at least once.** Before writing that a measurement requires
FORScan, a different tool, or hardware the owner does not have, **ask him to
search his sensor list for it first.** The list is longer than this project
assumed and nobody had ever read all of it.

## NAMING — use the SENSOR LIST label, never the graph header, never an abbreviation

**Owner's instruction, 2026-09-14: "never use shortcut and never use terms that
doesn't match my scanner list."** This file already carried the rule and it was
broken anyway — `O2S1 air:fuel` and `Fuel/Air com. ratio` were given as things to
enable. Those are what the app prints **on the graph**. They are not what appears
in the **sensor list** he scrolls on the phone.

| WRONG — graph header or abbreviation | RIGHT — sensor list label |
|---|---|
| `O2S1 air:fuel` | `Oxygen sensor 1 Wide Range Equivalence ratio` |
| `O2S5 air:fuel` | `Oxygen sensor 5 Wide Range Equivalence ratio` |
| `Fuel/Air com. ratio` | `Fuel/Air commanded equivalence ratio` |
| `Tim. adv.` | `Timing advance` |
| `LTFT - B1` | `Long term fuel % trim - Bank 1` |
| `STFT B2` | `Short term fuel % trim - Bank 2` |
| `ECU voltage` | `Control module voltage` |
| `MAF` | `MAF air flow rate` |
| `Abs. load` | `Absolute load value` |
| `EVAP purge` | `Commanded evaporative purge` |

**Also write words out in prose.** No WOT, no STFT/LTFT, no KAM, no ECT, no p2p
when addressing the owner. "Wide open throttle", "short term fuel trim", "memory
wipe", "coolant temperature", "peak to peak".

## FULL RE-TEST PROTOCOL — [`docs/RETEST-PROTOCOL.md`](docs/RETEST-PROTOCOL.md)

**Owner asked 2026-09-14 to redo every test at the proper sample rate and
re-eliminate every item.** That protocol supersedes the three-capture list below
and contains it. 23 captures across 8 sessions, every one two channels at 33 Hz,
each stating what it re-tests and what it can settle. It also carries the
hands-on items that need no scanner: mount bolt re-torque, ground voltage drops,
alternator ripple, crankcase ventilation valve, calibration identifier, and a
driver-side exhaust leak check.

**The eight questions it can settle cleanly** are listed at the end of that file.
The one it cannot is what sets the loop's phase margin at 0.32 Hz — a calibration
constant no capture reaches.

## THE THREE CAPTURES STILL OUTSTANDING — highest priority within the protocol

Two tiles at a time, everything else off the visible page. Warm, Park,
standstill, air conditioning off. Export **CSV #2 (Horizontal)**. Note the
odometer and the phone clock on each.

**1 — 20 minutes.** The 33 Hz beat-shape capture. Never obtained.
```
Engine RPM
Fuel/Air commanded equivalence ratio
```
These two have 13,348 simultaneous samples in `20260905_041723` but only at
~15 Hz. At 30 Hz the question becomes answerable: does the fuel command move
BEFORE a big beat?

**2 — 3 minutes.** **NEVER SELECTED on this truck — status unknown.** The two
logs carrying these are the 2023 control, not this truck. Confirm the channels
exist here by searching the sensor list for `secondary` before planning around
them.
```
Long term secondary oxygen sensor trim Bank 1
Long term secondary oxygen sensor trim Bank 2
```
Reads exactly 0.0000 on both banks of the 2023 control. It is the one learned
value that directly modifies the commanded mixture, and a memory wipe has
improved the symptom three times out of three.

**3 — while driving, pedal fully to the floor.** Third gear to ~5,000, then lift.
```
Oxygen sensor 1 Wide Range Equivalence ratio
Oxygen sensor 5 Wide Range Equivalence ratio
```
Separates the Bank 2 fuel offset into a driver-side air leak (invisible at full
throttle, where that bank flows ~107 g/s and a fixed leak is 0.026 %) versus a
lean-biased sensor (offset persists). The 09-05 wide-open-throttle pull reached
6,832 rpm but those two sensors have **zero** simultaneous samples in it.

**Also due at the truck, independent of all scanning: re-torque the engine and
transmission mount bolts.** Fitted 09-06, driven since, never re-torqued, and
this file has said since the day they went in that fresh mounts relax after the
first heat cycles. It targets the felt symptom, which the rpm data has twice
shown is a separate phenomenon.

## COLD START, 2026-09-13 — coolant ELIMINATED, and the oscillation scales with rpm

**19.6 min continuous from a 43 C cold start, recording begun before cranking.**
`data/carscanner/2026-09-13-cold-start/`. Engine speed and commanded ratio share
a rate (9,969 and 9,874 samples at 0.117 s).

**THE OPEN-LOOP TEST CANNOT BE DONE ON THIS TRUCK.** Closed loop begins **20 s
after start, at ECT 45.9 C** — not the ~80 C the 2023 shows. Commanded AFR p2p
goes 0.0000 (engine off) to 0.0540 (open loop, t+79 to t+99) to 0.4117. Those
20 s are the startup ramp, engine speed falling 1,268 to 931 rpm, detrended sd
188.66. There is no steady open-loop idle to measure. In Jeddah's ambient the
oxygen sensors are ready before the engine settles. **The only remaining route to
open loop is disconnecting the two upstream oxygen sensors.**

### COOLANT TEMPERATURE IS ELIMINATED — the minute 40-50 item is CLOSED

46 settled idle windows (rpm 600-700) spanning ECT **62 to 90 C**:

| | |
|---|---|
| ECT vs rpm sd | r = -0.219, **p = 0.143** |
| ECT vs 10 s span | r = -0.259, **p = 0.082** |
| Below 75 C vs above 85 C | sd 7.92 (n=13) vs 7.24 (n=8), **p = 0.301** |

This is exactly the separation this file asked for: on a cold start coolant
climbs fast while elapsed time is short, breaking the 88 % collinearity that made
the original observation untestable. **The amplitude does not step at any coolant
value. The minute 40-50 halving was not temperature.**

### THE OSCILLATION IS A FIXED FRACTION OF ENGINE SPEED

| | Mean rpm | Detrended sd | % of idle |
|---|---|---|---|
| Cold high idle | 903.4 | 10.72 | **1.187 %** |
| Warm idle | 651.5 | 7.80 | **1.198 %** |

n = 558 and 4,840. Identical to two decimal places across 250 rpm. **This is the
first measurement of the owner's standing report that the needle moves at every
engine speed** — it does, by the same percentage. **It also rules out raising
idle speed as a fix:** the absolute swing scales with it.

### THE FREQUENCY DOES NOT SCALE WITH ENGINE SPEED

**0.326 Hz (3.07 s) at 905 rpm and at 651 rpm**, and in all three separate warm
windows. A rotating order would shift with engine speed; this does not. Together
with the amplitude result: a torque disturbance of constant fractional size at a
fixed frequency — a control loop or a chemical process, not a moving part.

## THE FUEL DITHER EXPLAINS UNDER 5 PERCENT OF THE BEAT-TO-BEAT IRREGULARITY

Per-beat analysis, every individual cycle detected by rising zero crossings of
the band-passed signal, correlated against each channel sampled inside that same
beat:

| Predictor of beat amplitude | R2 | n |
|---|---|---|
| Engine load swing, A/C off | **72.2 %** | 26 |
| Engine load swing, A/C cycling | 58.8 % | 66 |
| MAF airflow swing | 31.7 % | 132 |
| Supply voltage swing | 7.0 % | 199 |
| **Commanded fuel swing** | **3.6-4.6 %** | 151, 267 |
| Throttle movement | 1.9 % | 136 — median swing **0.0000** |

Confounds checked: the load result is **stronger** with the A/C off, so it is not
a compressor artefact; and load vs rpm is r = -0.121 on 2,656 simultaneous
samples, MAF vs rpm r = +0.064, so neither is an arithmetic mirror of rpm.

**Direction is NOT established.** The commanded ratio is the only channel where
the PREVIOUS beat predicts better than the current one (r = +0.260 and +0.316
against +0.214 and +0.190, two independent sessions) — a causal signature. Load
and airflow correlate simultaneously, which an effect does as readily as a cause,
and with the throttle plate provably still and flow choked, airflow through the
sensor should not vary at all; intake pulsation modulating the MAF reading is the
likelier explanation, which would make it downstream.

**Net: the one channel that leads is too small, and everything large enough is
downstream. Nothing in the OBD channel set explains the irregularity.**

### THE IRREGULAR BEATS THEMSELVES

3.2 h log, 2,224 beats measured individually: **57 outliers at 62.8 rpm against a
typical 18.1 (3.48x)**, arriving **randomly** — median spacing 82.3 s,
sd/mean = 1.21 (Poisson), not clustered, not periodic.

**Period jitter is what the battery changed, not amplitude:**

| State | Beats | Period jitter | Amplitude |
|---|---|---|---|
| 09-04 worst | 2,224 | 34.0 % | 19.9 rpm |
| 09-08 after new battery, owner reports quiet | 36 | **19.1 %** | 17.4 |
| 09-09 after relearn, owner reports it back | 38 | **33.9 %** | 15.2 |

Levene: quiet vs now **p = 0.0127**; now vs worst **p = 0.66** (identical); quiet
vs worst p = 0.0003. Amplitude quiet vs now p = 0.633 — unchanged. **The beats
did not get bigger; they got irregular again.**

**Caveat that matters: the healthy 2023 has the HIGHEST jitter of all, 57.1 %.**
Its oscillation is broad and shallow — peak 16x above the noise floor against
this truck's 213x. Jitter alone is not the fault. Strong rhythm with low jitter
is the quiet state; strong rhythm with high jitter is what the owner feels.

## THE FELT SHAKE AND THE RPM OSCILLATION ARE SEPARATE — PROVEN TWICE (2026-09-09)

**Two repairs, each moving one symptom and not the other. This is now settled.**

| Repair | Felt shake | Measured 0.3 Hz rpm oscillation |
|---|---|---|
| Engine + transmission mounts, 09-06 | **GONE** | unchanged, 37.3 -> 32.3 rpm |
| Battery replacement, 09-08 | (returned 09-09) | **32.3 -> 25.3 rpm, quieter** |

On 09-09 the owner reported *"after relearn complete i feel the shake back"* and
captured it the same afternoon. **The rpm oscillation had not come back:**

| State | n windows | Median 10 s span |
|---|---|---|
| 09-08 15:49 before the battery | 18 | 32.3 rpm |
| 09-08 22:05 after, owner reports quiet | 16 | **25.3** |
| 09-09 17:42, owner reports the shake back | 14 | **27.3** |

**Quiet versus relapsed: Mann-Whitney p = 0.633.** No difference.

**Consequence: stop using the needle as a proxy for what the owner feels.** The
0.3 Hz oscillation is a control-loop property worth understanding on its own
merits, but it is not the complaint. Rate-matched Park-idle span is the metric
for the oscillation; only the owner's report, or an accelerometer, measures the
shake.

**What to chase for the FELT shake instead.** `CLAUDE.md` already carries the
answer and it is due now: **the new mounts have never been re-torqued.** This
file says *"Re-torque everything after a few hundred kilometres before treating
this as a fault."* They went in 09-06 and the truck has been driven since.

## LONG TERM TRIM: BANK 1 IS NOT LEARNING, BANK 2 IS (2026-09-09)

After the battery wipe and a 64-minute drive:

| Capture | Bank 1 | Bank 2 |
|---|---|---|
| 09-08 17:04, before | -0.7812 (n=201) | -0.7812 |
| 09-09 16:24, after 64 min | **0.0000 flat** (n=5,971) | 0.0000 -> +0.7812 (n=5,945) |
| 09-09 17:42 | **0.0000 flat** (n=986) | +0.7812 -> +1.5625 (n=984) |

**Bank 1 holds exactly 0.0000 across 7,165 samples while Bank 2 learns in the
same samples.** Not a disabled learning mode — Bank 2 is moving. Bank 1 needs no
correction; Bank 2 (driver side) needs more fuel.

**Third independent sighting of the driver-side lean offset**, after the +1.64 %
paired short-term measurement (n=227, se 0.10) and the +2.00 % that survived the
09-05 wipe unchanged. Two possible causes, and the sensors cannot separate them:
a real driver-side air leak, or a lean-biased Bank 2 upstream sensor. **The
separating test is the two upstream sensors at wide open throttle**, where fuel
is open loop and a fixed leak becomes negligible while a sensor bias persists.

## THE DITHER GREW WHILE THE RESPONSE DID NOT (2026-09-09)

| Capture | Commanded p2p | As % of mean | Lean-side |
|---|---|---|---|
| 09-04 pre-wipe (n=7,515) | 0.4559 | 3.126 % | 47.8 % |
| 09-09 16:12 (n=125) | 0.5291 | **3.627 %** | 40.0 % |

~16 % larger command and more rich-side time, the direction a relearned rich
bias predicts — while the rpm response stayed at its post-battery level.
**Whatever the new battery changed sits on the response side, not the command.**
Caveat: n=125 against n=7,515, five days apart, and **no commanded-AFR channel
exists in the quiet 09-08 22:05 capture**, so the quiet-state dither is still
unmeasured.

## SOLVED — THE ENGINE AND TRANSMISSION MOUNTS WERE THE CAUSE (2026-09-06)

**The owner replaced all engine mounts and the transmission mount. The seat shake
is gone.** Owner's direct report, same day. That closes the complaint this
project was opened to solve.

**What it confirms, and what it corrects:**

* The mounts were the right answer, and they were **ruled out twice** in this
  file on a bad argument — that D and R feel the same, so no mount could be at
  fault. That test is valid only for a *torque-reaction* failure. A mount that
  has **lost its damping without collapsing** is not direction-dependent, and
  that is what these had done, after twelve Jeddah summers.
* **[SETTLED 2026-09-06] These are SOLID RUBBER mounts. The old ones had no
  fluid.** Owner inspected the removed parts. Two earlier claims are withdrawn:
  that they were hydraulic (carried over from a general F-150 article without
  checking this engine), and that a solid-rubber replacement for a fluid-filled
  original explained the new symptom. **Neither applies. Like for like.**
* **The failure mode was rubber ageing, not fluid loss.** Twelve Jeddah summers
  of heat and ozone harden bonded rubber. **Hardened rubber transmits vibration
  instead of absorbing it** — the damping in a rubber mount is the rubber's own
  internal hysteresis, and that is what heat destroys. It also explains why the
  symptom was present from purchase and never changed with any engine repair.
* **Every scan-tool finding stands and none of it mattered to the symptom.**
  The engine measured healthy on 135,000 samples because the engine *was*
  healthy. The vibration was normal engine motion reaching the cab through
  mounts that had stopped isolating it.
* **The 0.30 Hz idle oscillation is a separate matter and is untouched by this.**
  It is a control-loop property, it is 30× too slow to be felt, and the control
  sample shows it is real. It stays open on its own merits.

**Standing lesson, and it is the third time this file has had to record one:**
the D-versus-R argument eliminated the correct answer for weeks. **An elimination
is only as good as the failure mode it tests.** Write down which failure mode a
test rules out, not just which part.

## NEW SYMPTOM AFTER THE REPAIR — "shocked, then fights back"

**Owner, same day: the seat shake is gone, but there are now occasional shock
points — mild, felt in the cabin, as if the engine is knocked and pushes back.**

Not yet diagnosed. Recorded here so it is not lost. The three readings that fit,
in order:

0. **THE TRADE-OFF THAT COMES WITH SOFT MOUNTS — leading explanation.** The old
   mounts were hard. A hard mount **holds the engine still and passes vibration
   through**: continuous buzz, little movement. A new compliant mount does the
   opposite — it **blocks the buzz but lets the engine actually move.** So a
   torque step that the old hard mounts held against now displaces the engine,
   and the mount's spring returns it. **"It gets shocked and fights back" is a
   soft mount doing its job.** The obvious trigger is the A/C compressor clutch
   on its measured 15.78 s cycle, which steps engine load 28.6 to 36.8 % and fuel
   rate by 34 %. That step was always there; the old mounts simply would not let
   the engine move in response to it.
1. **Normal settling of new mounts.** A fresh mount is far stiffer than a dead
   one and transmits events the old ones absorbed by being limp. Mount bolts also
   relax after the first heat cycles. **Re-torque everything after a few hundred
   kilometres before treating this as a fault.**
2. **The engine ringing its own mounts.** With mounts that now have a real spring
   rate, any torque *step* — the A/C compressor clutch engaging on its 15.78 s
   cycle, or a gear engagement — excites the 8–15 Hz engine-rock mode as a brief
   decaying ring. "Shocked and fights back" is a precise description of that.
   **This is the mounts working, not failing.**
3. **Something is now being struck.** The engine can move further than it could
   on hardened mounts. **A clearance that was adequate for twelve years may not
   be any more** — a pipe, a line, a loom, a bracket, or a heat shield. This
   project already carried contact points as a candidate for the original
   symptom; the new mounts make it more likely, not less. If the sensation is a
   genuine *impact* rather than a smooth lurch, check this first.
4. **Loose or under-torqued mount bolts**, which would give exactly an impact
   feel and can damage the mount.
5. **Wrong durometer or wrong part.** An aftermarket mount softer than Ford's
   allows excessive travel.
6. **Driveline angle changed.** The transmission mount sets the driveline angle,
   and this truck is **4x4** — a transfer case and a front driveshaft the earlier
   revisions of this file did not know existed. A mount of different height, or
   one not seated square, shifts those angles.

**Part numbers found by search, NOT verified against a Ford catalogue** — every
parts page was blocked at the network layer, so these are search-summary level
and must be confirmed by VIN at a parts counter before ordering:

| Part | Reported as |
|---|---|
| `BL3Z-6038-A` | Motor mount, **driver side (LH)**, 2011–2016 F-150 |
| `BL3Z-6038-G` | Motor mount, **passenger side (RH)**, listed compatible with 3.7L |
| `DL3Z-6038-C` | **Right side, 3.7L, build date from 6/12/13** — a mid-2013 running change |
| `BL3Z-6038-C / -E / -F / -H / -J` | Other variants in the same family |

Ford calls the part an **"Insulator Assembly"**. **The build-date split matters:**
a 2014 truck built after 12 June 2013 may take a different right-side part from
one built before.

**What separates them: when it happens.** Only at idle in gear points at the
compressor or engine rock; only while driving points at driveline angle; random
and fading over days points at settling.

## THE CONTROL SAMPLE ARRIVED — and the idle IS abnormal (2026-09-06)

**The owner's 2023 F-150 5.0, 20 minutes of continuous stationary idle at
600 rpm, 6,449 samples, same app, same adapter, same city, same evening.**
Logs in `data/control-2023/`. This is the measurement this project has wanted
since night one, and it changes the verdict.

### Amplitude — the 2014 swings twice as far

| | 2023 F-150 5.0 | **2014 F-150 3.7** | Ratio |
|---|---|---|---|
| Idle speed | 599.3 rpm | 651.8 | — |
| Standard deviation | **5.64 rpm** | **9.36** | **1.66×** |
| As a percentage of idle | **0.94 %** | **1.44 %** | 1.53× |
| **Median 10 s peak-to-peak** | **20.0 rpm** | **38.0** | **1.90×** |
| p10 – p90 | 17 – 25 | 28 – 52 | — |
| Windows measured | 91 | 707 | — |

**Identical method, identical window length, both stationary, both warm, A/C
compressor not cycling in either.** The 2014 moves **1.9× as much**.

### Rhythm — BOTH have one. The "random wander is normal" claim is WITHDRAWN.

An earlier revision of this file argued that a healthy engine wanders randomly
and a locked rhythm is itself the abnormality. **That is wrong.** The 2023 has a
dominant peak too, at **0.167 Hz (6.0 s)** — a different rate, but a rhythm.

**What differs is how sharply the oscillation is locked on:**

| | 2023 5.0 | 2014 3.7, 62 min | 2014 3.7, post-repair |
|---|---|---|---|
| Dominant frequency | 0.167 Hz (6.0 s) | 0.317 Hz (3.16 s) | 0.333 Hz (3.00 s) |
| **Peak ÷ median power** | **30×** | **144×** | **353×** |
| **Power within ±15 % of the peak** | **19.3 %** | **37.4 %** | **62.8 %** |
| Slow-band rms | 0.235 | 0.554 | 0.569 |

**The 2023's oscillation is broad and shallow. The 2014's is a spike.** Up to
**63 % of all its slow-band energy sits in one narrow line**, against 19 % on the
healthy truck, and the peak stands **12× further above the noise floor**.

### What this means

**The 2014's idle is genuinely outside what a healthy Ford of the same family
does — by amplitude and by how tightly the energy is concentrated.** Both trucks
run the same fore/aft catalyst control; the 2023 responds to it with a soft,
spread-out wander and the 2014 responds with a sharp resonance at twice the rate
and twice the size.

**This does NOT identify a broken part**, and every part on the 2014 still
measures healthy. It says the *idle control response* is different, which points
at the calibration, at the engine's damping at 0.3 Hz, or at a load the 2023 does
not have.

**Caveats, stated plainly:** different engine (5.0 V8 vs 3.7 V6), different model
year, different transmission, nine years newer. A V8 idles more smoothly than a
V6 by construction. **This is one control sample, not a population** — but it is
the only one this project has ever had, and it points the opposite way to the
previous "your idle is normal" conclusion.

## THE CAUSE OF THE IDLE OSCILLATION — FOUND (2026-09-06)

**The PCM's own fore/aft catalyst-control dither drives about three quarters of
the idle rpm oscillation.** Every earlier statement in this file that the dither
"accounts for about a fifth" is **withdrawn — it used the wrong metric.**

The r = −0.41 broadband correlation is diluted by everything the two signals do
at frequencies where they are genuinely unrelated. The question "what causes the
*rhythm*" has to be asked **at the rhythm's frequency**. Magnitude-squared
coherence at 0.30 Hz, Welch method, 30–40 s segments:

| Window | Condition | Seconds | Segments | **Coherence @ 0.30 Hz** | Significance threshold | Gain, rpm per AFR unit |
|---|---|---|---|---|---|---|
| log 3, 2180–2500 s | Park, post-repair | 232 | 14 | **0.749** | 0.206 | 25.0 |
| log 3, 2500–2800 s | Park, post-repair | 162 | 9 | **0.721** | 0.312 | 25.1 |
| log 3, 2800–2980 s | Park, post-repair | 140 | 8 | **0.766** | 0.348 | 28.9 |
| log 0, 5880–6150 s | Park, **pre-repair** | 104 | 5 | **0.791** | 0.527 | 29.8 |
| log 0, 6150–6420 s | Park, **pre-repair** | 214 | 13 | **0.701** | 0.221 | 24.4 |

**Coherence away from the rhythm (0.6–2 Hz) is 0.085–0.091 — nothing.** The
relationship exists only at the oscillation frequency, which is exactly what a
driver looks like and exactly what a coincidence does not.

**For comparison, spark advance has coherence 0.998 with rpm** at the same
frequency — and 0.68 everywhere else. Spark tracks rpm at all frequencies. It is
a pure follower, as established.

### What this means

```
PCM commands ±0.23 AFR (±1.5 %) at 0.30 Hz     — fore/aft catalyst control, NORMAL
  × engine responds at 24–30 rpm per AFR unit  — lightly damped Park idle
  = ±6–7 rpm at the fundamental, ~75 % of the rhythm
  + harmonics, the A/C compressor when running, and noise = the 38 rpm span
```

**The rpm oscillation is the engine faithfully following a normal control
function.** The dither amplitude (±1.5 %) is textbook Ford. The period (3.3 s) is
set by the catalysts' oxygen storage, which Mode 06 puts at 44 % of limit on both
banks. The engine's response gain is a property of the idle calibration — how
much damping the governor applies at 0.3 Hz — and this governor uses ±0.9° of a
47° spark authority, which is a low-gain choice.

**No part is broken. This is calibration behaviour.** Whether the dither amplitude
or the response gain are *typical for this engine* still cannot be judged without
another 3.7 — but nothing about it is a fault by any measurement available.

### What would change it

* **A Ford calibration update**, if one exists for this PCM. That is the only
  legitimate lever on dither amplitude and governor gain. `f150diag survey` prints
  the calibration IDs; a dealer can say whether a later one was released.
* **Nothing mechanical.** Replacing sensors, injectors, or converters would not
  touch it — every one of those measures healthy, and the driving signal is a
  command the PCM generates on purpose.

### One thing still worth capturing

`Fuel/Air com. ratio` and `O2S2 volt. (B1)` on the same graph for three minutes.
Only 26–40 simultaneous samples of the downstream sensor and the fuel command
exist in all four logs. If the downstream sensor leads the command, the fore/aft
loop is confirmed closed and its behaviour can be judged directly.

### And the felt shake is still a separate problem

None of this touches it. The oscillation is 0.30 Hz; what shakes a seat is
10–33 Hz; the port cannot see it. **The accelerometer recording is still the only
test aimed at the symptom the owner actually complained of.**

## THE CYCLE, TRACED — 926 cycles ensemble-averaged (2026-09-06)

**[`data/trace_rpm_cycle.py`](data/trace_rpm_cycle.py), output in
[`docs/rpm-cycle-trace.txt`](docs/rpm-cycle-trace.txt).** Individual cycles are
noisy; stretching each to a common phase axis and averaging 926 of them recovers
the shape that repeats. **Whatever survives 926 cycles is real** — the averaged
shape carries a standard error of ±0.25 rpm.

| | Measured |
|---|---|
| Period | **2.993 s mean, 3.000 median, sd 0.564 — 19 % jitter** |
| Fundamental | **0.304 Hz** |
| 2nd harmonic | 5.5 % of fundamental power |
| 3rd harmonic | 1.2 % |
| **Anything above 1 Hz** | **under 1 %. 4–8 Hz is 0.09 %** |
| Averaged amplitude | 18–21 rpm |

**The wave is close to a sine, and it is asymmetric.** It rises through **43 %**
of the cycle and falls through 57 %. Steepest rise **+29.3 rpm/s**, steepest fall
**−17.0 rpm/s** — **the rise is 1.7× steeper than the fall.**

### What happens inside one cycle

| Phase | Event |
|---|---|
| 0.00 | rpm crosses its mean going up, **rising fastest** |
| 0.25 | **rpm peak** |
| 0.28 | commanded air/fuel at its **richest** |
| 0.31 | spark at its **most retarded** |
| 0.58 | rpm falling fastest |
| 0.75–0.79 | **rpm trough** |
| 0.81 | spark at its **most advanced**, air/fuel at its **leanest** |
| 0.96 | rpm rising fastest again |

**Spark is fully advanced exactly at the rpm trough and fully retarded exactly at
the peak.** That is a governor doing precisely what a governor should. It is not
the cause; it is the correction, and it is *in the right place in the cycle*.

**But its authority is tiny: 1.75° peak-to-peak, ±0.9° about the mean.** It
opposes the swing and does not cancel it.

**The rich command sits on the rpm peak and the lean command on the trough**,
amplitude 0.296 AFR units, leading rpm slightly. Rich → more torque → rpm up.
The physics runs the right way.

### What the trace rules out

**No fast content.** Between 4 and 8 Hz the spectrum holds **0.09 %** of the
fundamental's power. Within the bandwidth this tool can see, engine speed is
smooth — there is no per-event roughness, no stumble, nothing intermittent.
(Firing at 32.5 Hz is still above Nyquist and still invisible.)

**19 % period jitter is not a mechanical resonance.** A rotating or structural
resonance holds its frequency far tighter than that. This is a driven or
limit-cycling loop with a variable delay.

### Where it leaves the case

The trace is consistent with **the catalyst dither driving a torque swing that
the spark governor opposes with too little authority to cancel** — dither leads,
rpm follows, spark corrects a tenth of a second later at ±0.9°. It does not prove
that, because the dither only accounts for about a fifth of the variance, and the
asymmetric rise says the torque excursion is briefer and larger than a pure sine
would give.

## THE PRE-REPAIR SESSION REPLICATES IT EXACTLY (2026-09-05, 3.2 h log)

**A fourth log: 2026-09-04 22:24 → 09-05 01:35, 35 MB, 115,257 rpm samples, Park
idle throughout, A/C off (`A/C pressure` reads 0 all session).** This is the
**old purge valve**, hours before the repair — so it tests whether anything found
after the repair was created by it.

| Signal | vs engine speed | Pre-repair | Post-repair |
|---|---|---|---|
| Timing advance | **LAGS 0.10 s** | **r = −0.885** | r = −0.84 / −0.91 / −0.76 |
| Commanded air/fuel | **LEADS 0.15 s** | **r = −0.418** | r = −0.38 to −0.50 |
| Short term trim B1 | **LAGS 0.65 s** | r = −0.302 | — |
| Throttle | own 19.3 s rhythm | r = +0.18 | 18.7 s, r = +0.20 |
| Purge | own 17.0 s rhythm | r = +0.12 | 16.8 s, r = −0.24 |
| Cam phaser | **nothing at all** | **p2p 0.062°, r = +0.05** | — |

**Identical, to the hundredth, across a repair that changed the fuel system.**
The control structure is not something the purge valve created or fixed.

**The full chain now has all four links timed:**

```
commanded AFR  +0.15 s  →  RPM  0  →  spark  −0.10 s  →  short term trim  −0.65 s
```

Short term trim arriving **last** is exactly right — it is the O2 loop reacting
to a mixture change that already happened. It is not driving anything.

**CAM PHASERS ELIMINATED AT IDLE, properly this time.** 9,824 paired samples
against rpm: total movement **0.062°**, one quantisation step, correlation
**+0.05**. The earlier elimination rested on a screenshot of a parked needle.

### THE A/C COMPRESSOR DOUBLES THE IDLE OSCILLATION — SETTLED (2026-09-06)

**The owner confirms the air conditioning was ON during part of the long
session.** With electric cooling fans, the only clutch that can cycle as a direct
crankshaft load is the A/C compressor. Both remaining candidates collapse to one,
and the data matches it exactly.

| Minutes into the session | rpm sd | Median 10 s span | **Calculated load sd** |
|---|---|---|---|
| **15–38, A/C cycling** | **13.94** | **69.0 rpm** | **4.252 %** |
| 40–70, after | 8.97 | 35.0 rpm | **0.317 %** |
| 70–131, after | 9.27 | 38.0 rpm | 0.373 % |

**Engine load stops varying by a factor of thirteen at minute 37–38, and the
engine-speed oscillation halves at the same moment.** The compressor was cycling
on a **15.78 s period**, stepping load 28.6 ↔ 36.8 %, airflow 3.43 → 5.08 g/s and
fuel rate **+34 %**.

**This restores the original screenshot finding, which a later analysis had
wrongly called into question.** The screenshots recorded A/C OFF at 30–53 rpm and
A/C ON at 64–81 rpm. The logs give 35–38 against 69. **The screenshot record was
right and the doubt was wrong.**

**`A/C pressure` is a DEAD CHANNEL on this truck** — exactly 0.000 in every
sample of every log, including while driving. Every statement in this file that
"A/C was off, confirmed by A/C pressure reading 0" is withdrawn: that channel
never answers. **Do not request it, and do not treat its values as data.**

**`Gear (AT)` IS NOT DEAD — that claim is WITHDRAWN (2026-09-18).** This file
said *"dead the same way, constant 1.000 in all 45 samples"* and told the owner
never to request it again. It is constant on this truck — 1.000 in all 61
samples across four sessions — **but every sample that has a co-sampled vehicle
speed was taken at 0 km/h, at 637–667 rpm.** A transmission standing still
reports a constant legitimately. **The channel has never once been sampled while
the truck was moving, so it is UNTESTED, not dead**, and the 2023 control reads
**5** on the same channel, which proves the channel can carry other values.

**The rule this repeats for the third time: a constant reading only means a dead
channel if the CONDITION varied.** The same error produced the manifold pressure
mix-up and the catalyst-temperature claim. **Check what the truck was doing
before calling a channel dead.**

**CORRECTION 2026-09-14 — `[PCM] A/C Pressure` IS A DIFFERENT CHANNEL AND IT
WORKS.** The owner's sensor list carries both. The `[PCM]`-prefixed one read
**1282 kPa** in a screenshot. The instruction above applies ONLY to the
unprefixed `A/C pressure`. **Use `[PCM] A/C Pressure` to establish compressor
state** — that has been an unmeasured confound on every amplitude figure in this
file. The same caution now applies in reverse to `Gear (AT)`: a `[PCM]` variant
(`[PCM] Commanded Gear`) exists and has not been tested.

**Is doubling the amplitude with A/C on a fault?** No — a compressor cycling on
and off at idle disturbs any engine, and this one recovers to a stable idle
between cycles. It is recorded because it explains a change this project spent
considerable effort calling unexplained, and because **it means every amplitude
figure in this file must state whether the compressor was running.**

### THE AMPLITUDE HALVED ONCE, EARLY IN THE NIGHT — superseded, see above

**835 ten-second idle windows across all four logs, in
[`data/analysis/idle_windows.csv`](data/analysis/idle_windows.csv).** Restricted
to Park/Neutral, engine never switched off, A/C off:

| Minutes into the session | Median span | ECT |
|---|---|---|
| 10–40 | **67, 69, 61 rpm** | **81–83 °C** |
| 40–50 | **31.5** | **81 → 91 °C** |
| 50–200 | **38, 39, 34, 38, 41, 38, 40, 40, 36, 40, 30** | **93–98 °C** |

**Something changed once, around minute 40–50, and the halving held for the next
two and a half hours.** It is the first change in the hunt this project has
observed that no repair caused.

**But coolant temperature is NOT established as the cause, and an earlier
revision of this file said it was. Withdrawn.** Three reasons:

1. **Above 88 °C the correlation reverses** — r = **+0.41**, hotter meaning
   *more* movement. A real temperature law would not change sign in the middle.
2. **ECT and elapsed time are 88 % collinear** in this session (r = +0.884).
   They rose together, so nothing here can separate them.
3. **It rests on one session.** Of 189 Park windows carrying a coolant reading,
   **all 189 come from the same log.** The other three barely sampled ECT.

Overall r = −0.455, which is real but is carried almost entirely by the
first-40-minutes block being worse than everything after it.

**A better candidate than temperature: the cooling fan.** ECT sat at 81–83 °C for
forty minutes of idling and then *rose* to 91–98 °C, which is the shape of a fan
switching off, not of an engine warming up. The fan is an engine load, and this
project has already noted it cycling. **Load changing is a mechanism; temperature
alone is only a correlate.**

**How to settle it, and it is free:** idle from cold with `Engine coolant
temperature` on the graph beside `Engine RPM`, and watch whether the amplitude
steps at the same coolant value twice. One repeat in a second session decides it.

## SPARK FOLLOWS RPM — measured, not inferred (2026-09-05, from logged data)

**Three Car Scanner CSV logs, ~17 Hz per channel on true timestamps, 135,000
rows.** Screenshots could give amplitude but never phase. These can, and they
answer the question this investigation has turned on since night one.

| Signal | vs engine speed | Correlation |
|---|---|---|
| **Timing advance** | **LAGS by 0.10 s** | **r = −0.84, −0.91, −0.76** (three windows) |
| **Commanded air/fuel** | **LEADS by 0.00–0.20 s** | r = −0.38 to −0.50 |
| Throttle | own rhythm, 18.7 s | r = +0.20, unrelated |
| Purge | own rhythm, 16.8 s | r = −0.24, unrelated |

**THE PCM IS NOT DRIVING THE RPM WITH SPARK.** Spark moves *after* engine speed,
by 100 ms, anti-correlated at **r = −0.91** — rpm rises, spark is pulled back a
tenth of a second later. That is a governor reacting to a disturbance it did not
create. **"Something is adjusting the rpm on my behalf" is answered: yes, and it
is correcting, not causing.** Every reading of the screenshots that had spark
driving the oscillation is withdrawn.

**The commanded air/fuel dither leads engine speed, with the physically correct
sign** — a leaner command precedes a dip in rpm. Order of events, measured:

```
commanded AFR dither  →  rpm responds ~0.1 s later  →  spark corrects ~0.1 s after that
```

**But it is not the whole disturbance.** |r| ≈ 0.45 accounts for roughly a fifth
of the variance in engine speed. Something else supplies the rest, and these logs
do not name it.

### The period is 3.1 s, not 3.4–3.5 s

**0.32 Hz, in every window, in Park and in Drive, in both rpm and spark.** The
old figure came from counting cycles by eye on a 15 s screen. Use **3.1 s / 0.32
Hz** from here on.

### Park vs Drive, quantified properly

| | Mean | SD | 10 s spans, median | Period |
|---|---|---|---|---|
| **Drive** at standstill | 550.3 | **4.37** | **14.8** (11–44) | 3.03 s |
| **Park** | 652.1 | **9.56** | **40.2** (24–85) | 3.13 s |

**Same oscillation, same frequency, 2.7× the amplitude in Park.** In gear it is
damped, not absent — consistent with converter loading, and it means D and R were
never "clean", only below the threshold of feeling.

### What this does to the crank-signal hypothesis

**Weakened, not eliminated.** The rpm swing is phase-locked to a commanded fuel
change with the right sign and the right delay, which is what a *real* torque
disturbance looks like. A lying crank sensor would not produce that relationship.
It remains the only hypothesis that explains reset-helps-then-returns, so it
stays open — but it no longer has the field to itself.

### The sample rate was wrong in this file

**Car Scanner samples each channel at ~17 Hz (60 ms), not 56–117 ms.** Nyquist is
**8.3 Hz**. Firing (32.5 Hz) and first order (10.8 Hz) are still invisible, so the
felt shake is still out of reach — but 8.3 Hz reaches the **bottom edge of the
8–15 Hz engine-rock band**, which this file previously said was unreachable.

**Logs live in `data/carscanner/`. The analysis is
[`data/analyze_carscanner.py`](data/analyze_carscanner.py), output in
[`docs/carscanner-timing-analysis.txt`](docs/carscanner-timing-analysis.txt).**
Export as **CSV #2 (Horizontal)** — never #3, which forward-fills invented
samples and would have destroyed every lag above.

## THE D/R FIX RELAPSED — the reset helped, not the valve (2026-09-05)

| | P / N | D / R |
|---|---|---|
| Before the purge valve | shakes | less |
| After the valve **+ KAM wipe** | shakes | **clean** |
| **After ~100 km** | shakes | **shakes again** |

**The confound was called in advance and has resolved against the valve.** This
file said: *"if the improvement came from the reset, the shake returns in D and R
as long term re-learns."* It returned.

**The valve was still a real fault, genuinely fixed** — idle long term trim went
**+3.13 / +2.34 % → −0.78 / −0.78 %** and held through a full relearn; the
load-cell slope is gone. **But it was not the cause of the symptom.** It joins the
other six repairs that changed nothing.

### THE NEW EVIDENCE: reset helps, relearning brings it back

**Wiping the PCM's learned memory temporarily improves the symptom; it returns as
the memory relearns.** Twice now — the owner's earlier relearn plus 300 km, and
this repair.

**No purely mechanical fault behaves this way.** A dead mount, a delaminated
damper, an exhaust touching the body — none care what is in the PCM's memory.
**Whatever is wrong involves something the PCM learns.** This is the first
evidence that discriminates mechanical from control-system, and it points at the
control system.

### It supports the night-one hypothesis that was never tested

**Is the rpm signal itself true?** Ford PCMs learn a **crankshaft position
variation correction** — a profile of reluctor tooth spacing errors, cleared by a
KAM wipe and relearned over subsequent driving. [VERIFY against Ford service
information.] A defective crank signal or reluctor would make the PCM *believe*
rpm is wandering, modulate spark and fuel for a phantom, and **that modulation
would make the engine genuinely oscillate.**

It accounts for: needle jumping at **every** rpm · no codes ever · **better after
a reset, back after ~100 km** · untouched by six fuel/ignition repairs · present
since purchase · "something is adjusting the rpm on my behalf" · the ripple being
constant while only idle is unloaded enough to let it reach the cab.

**It is the only hypothesis that accounts for reset-and-return.** Every
mechanical candidate fails that test outright.

**TESTS, none done:** ① **independent rpm** — timing-light tach vs the app at idle
and at 1500; if the truck's reading is jumpier than the crank actually is, the
signal is lying · ② crankshaft position variation relearn status via FORScan/IDS ·
③ inspect and wiggle-test the crank sensor connector and harness · ④ **re-measure
Drive now the symptom is back** — `Engine RPM` + `Tim. adv.` gave **13–18 rpm**
when D/R was clean; a bigger span means the disturbance grew, the same span with
a felt shake means the path changed.

**Measurement gap this exposed:** the commanded AFR dither was never captured
during the window when D/R was clean. **Rule: when a repair or reset changes the
symptom, re-measure the full channel set immediately — that window is short and
does not come back.**

## THE PROBLEM IS NOT AN IDLE FAULT — read this first (2026-09-05)

**The owner's own description, which re-scopes everything below it.** There are
**two** symptoms and they have different ranges:

| Symptom | Where |
|---|---|
| **RPM instability — the needle visibly jumping** | **The WHOLE rpm range.** 650, 1000, 1500, 2000. It never stops. |
| **Body shake — felt through the seat** | **Idle only.** Gone by 1000–1500. |

> "When I bring it to 1000, 1500, the body shake disappears, **but the RPM needle
> is still jumping and bouncing.** And it is hard for me to adjust the RPM at 1000
> because **something is working on behalf of me of adjusting the RPM**… **the
> problem exists in a wide range of RPM and not only limited to one RPM.**"

**This resolves the apparent conflict** between his early "present everywhere,
roughly equal" and his late "worst at idle 650": the first describes the *rpm
instability*, the second describes *what he feels*. Both correct, different
phenomena, never in tension.

**Consequence: the entire investigation was scoped as an idle fault and that was
wrong.** Every elimination below rests on idle data or two short 2000 rpm holds.
**The owner reported the wider scope twice and it was filed as a side note both
times** — once explained away as drive-by-wire throttle plus fan cycling, never
tested.

**It weakens the leading explanation.** The measured ±1.5 % AFR square wave at
3.5 s is fore/aft catalyst control — a closed-loop fuelling function
characterised entirely at idle. Above idle the idle governor releases and the PCM
should follow the pedal; if rpm still wanders at a held 1500, idle speed control
is not the explanation.

**It strengthens a night-one hypothesis that was never tested: is the rpm signal
itself true?** A noisy crank signal would make the PCM *believe* rpm is
wandering, modulate spark and fuel for a phantom, and that modulation would make
the engine genuinely oscillate — one fault, every rpm, no code.

**THE TESTS, AT A HELD 1500 rpm — not at idle:**

1. `Engine RPM` + `Throttle Position Actually` — flat throttle with wandering rpm
   means torque is varying or the rpm reading is lying; a moving plate under a
   still pedal means **the PCM is doing it deliberately**.
2. `Engine RPM` + `Fuel/Air com. ratio` — **no square wave but rpm still
   wandering kills the dither explanation** and forces a re-read of everything
   concluded from it at idle.
3. `Engine RPM` + `Tim. adv.` at the same hold.
4. **Independent rpm** — timing-light tach against the app, at idle and at 1500.

## The open problem

A **small** vibration felt in the cab at idle and light load, with visible
movement on the tachometer. Felt, not heard — **from under the hood a
trained ear cannot tell the engine has a problem.** It does not lope,
stumble or threaten to stall. Present since purchase, before any repair
work.

### First question: is this a fault at all?

Not yet established, and it must be before more money is spent. The truck
is a base **regular cab XL** — minimal sound deadening, cab close to the
engine — and the 3.7 is a **60° V6**, which is not inherently balanced the
way an inline-six or a cross-plane V8 is. A small idle vibration reaching
the seat may simply be what this truck is.

Supporting the "no fault" reading: never smooth in the owner's entire
ownership, **zero powertrain codes on a complete multi-module scan**, normal
idle rpm, perfect under load, and **six competent repairs aimed at six
different systems, every one of which changed nothing.**

**But a rhythmic idle hunt of 2.5–4 seconds HAS now been measured** — see the
RPM stability section. That is a real, reproducible finding, and it means the
answer to "is this a fault at all" is no longer a clean no.

Two tests settle it, both free:

1. **Compare against another 2014-ish F-150 regular cab 3.7 at idle.** Hand
   on the fender, then sit in the cab. A control sample answers in two
   minutes what six repairs have not.
2. **Quantify the rpm movement** — log the RPM PID for 60 s at warm idle in
   P. **±25–50 rpm of gentle wander is normal** closed-loop idle control.
   **±100 rpm or a rhythmic hunt is a real fault.** That threshold is the
   whole question.

### The load relationship — the key observation

Symptom strength tracks engine load inversely:

| Condition | Manifold vacuum | Shake |
|---|---|---|
| P / N at standstill | Highest | **Worst** |
| D / R at standstill | Slightly lower | **Less** |
| Driving under load | Lowest | **Absent — pulls great** |

**Rpm is not the variable; load is.** If a fault exists it is one whose
effect scales with manifold vacuum and disappears when the throttle opens.

**Superseded reasoning — do not reuse.** This file previously argued that
the converter *damps* pulses in gear, therefore the engine is genuinely
rough. That was wrong twice over: every torque-converter automatic is
smoother in gear at a standstill, so the observation was never evidence of
a fault; and the truck being flawless under load rules out the whole
worsens-under-load family the old reasoning pointed at.

**MOUNTS ARE NO LONGER RULED OUT BY THIS TEST — see *THE SHAKE IS STRONG* below.**
The D-vs-R argument excludes a *torque-reaction* fault but is blind to a mount
that has lost its damping, which is not direction-dependent.

**D and R feel the same as each other.** Engine torque reacts in opposite
directions in D and R, so a collapsed mount or a torque-reaction contact
would differ between them. This is a better mount test than the old D-vs-N
one, and it keeps **flexplate and driveline ruled out** — as does
the symptom reproducing at a standstill in Park.

### Already done — none of it changed the shake

Spark plugs · air filter · oil and filter · coolant flush · 6R80 fluid
(113,000 km) · **throttle body removed and hand-cleaned** · **injectors
removed, cleaned and flow-tested** · O2 sensors "cleaned", method unknown.

Also established: factory airbox and duct (no oiled filter) · always 95
octane from the same station · **no aftermarket tune UNTIL 2026-09-16, when
the calibration was changed on a dyno — see the dyno section at the top of this
file** · no evidence of prior
engine work · thermostat reaches and holds temperature · coolant level
steady · battery disconnected once, relearn done plus 300 km.

**Weaker than this file previously claimed — the owner's actual answers were
hedged, and the hedges were dropped:**

| Claimed here | What the owner actually said |
|---|---|
| "currently 5W-30" | **"5W-30 or similar"** — the viscosity in the sump is not established |
| Spark plugs replaced | **The brand, part number and gap were never stated.** "Replacing spark plugs never changed the shake" answers a different question |
| An idle relearn followed the throttle body clean | **"I don't know — they said drive it 250 km and it will relearn."** This file once called that "a legitimate drive-cycle relearn" and concluded the adaptives were mature. That is stronger than the answer supports. |
| Serpentine belt, tensioner, idler | **"Don't know"** — eliminated by reasoning, never inspected |
| Battery age | **"Don't know"** — the whole charging analysis sits on top of this gap |
| Rear diff lubricant | **"Changed at some point"** — no date, no distance |
| What was done to the O2 sensors | **"Don't know what they did"** — the method remains unknown |

None of these change the diagnosis. They are recorded because a hedge silently
promoted to a fact is how this investigation went wrong more than once.

### Do these first — ten minutes, engine off, no scan tool

Both come from the Mustang 3.7 community, which is the **same Cyclone
engine** and a far larger source than the F-150 3.7 community. Run
`python -m f150diag.cli run quick-wins` to be walked through them.

1. **PCV valve shake test.** Passenger-side valve cover, roughly halfway
   forward [VERIFY on the F-150; that location is documented for the Mustang
   3.7]. Pull it and shake it — **no rattle means clogged.** Mustang 3.7
   sources name PCV clogging as a known rough-idle cause on this engine.
2. **Purge valve vacuum-hold test.** Engine off, connector unplugged, hand
   pump on the inlet — **it must hold.** Mustang sources state the common
   failure mode of Ford's purge valve is stuck **open**.
3. **Calibration check.** `f150diag survey` prints the PCM calibration IDs.
   Give those and the VIN to a Ford dealer and ask whether a later
   calibration exists — a reflash is a repair with no parts.

### Current leads, if the rpm test shows a real fault

1. **EVAP purge valve stuck partly open** — never touched. Documented as a
   very common failure on the 2009–2014 F-150, and Mustang 3.7 sources say
   stuck-open is *the* failure mode. Frequently sets **no code**.
2. **PCV valve, hose and elbow** — never inspected, 12 years of Jeddah heat.
3. **VCT solenoid / cam phaser** — see the EGR note under *Careful*. Weak on
   two counts: no codes (P0010–P0024 expected) and no cold/hot difference.
   `f150diag run vct-check` drives the FORScan handoff that measures it.
4. **Vacuum leak elsewhere** — smoke test, but only after trims justify it.

**Vacuum lines on this engine are hard plastic.** They cannot be clamped or
pinched. Isolating one means disconnecting it and plugging the manifold port,
**engine off** — opening a manifold port on a running engine will stall it.

### Same engine, other models

The 3.7 Ti-VCT is the engine in the **2011–2014 Mustang V6**. That community
is much larger, so search it too. **Engine-level claims transfer** — phasers,
chain, water pump, PCV, purge valve, fuel trim behaviour. **Vehicle-level
ones do not** — mounts, driveline, exhaust, cab, NVH, installation and
routing.

Relevant finding from it: Mustang 3.7 owners raised a vibration complaint
large enough to reach a public petition, and **Ford's stated position is that
it is normal operation**. Their described symptom is 2200–2800 rpm and
shifter vibration, which is not this truck's idle symptom — but Ford
considering a 3.7 vibration normal bears directly on the first question above.

**Eliminated with evidence:** throttle body (properly cleaned, no change) ·
injectors (flow-tested) · MAF and intake (factory) · fuel delivery and fuel
quality · ignition · compression, cam timing and phasers *in their
stuck-in-position mode* (all worsen under load) · mounts and driveline ·
thermostat · coolant intrusion · ~~PCM tune~~ (**WITHDRAWN 2026-09-16 — the
calibration was deliberately changed; it is a live variable again**) · adaptive
memory.

### Codes — read 2026-09, complete multi-module scan

**No P-code of any kind.** No misfire, fuel trim, VCT or lean code. The PCM's
own monitors have nothing to say about how this engine runs — a second
independent line of evidence alongside the load curve.

Four codes exist, **all inactive (archive)**, none powertrain:

| Module | Code | Meaning |
|---|---|---|
| OBD-II + PCM | U0422 | Invalid data received from BCM |
| OCS | U0140 | No communication with BCM |
| RCM | B11D8(14) | Restraints event notification |

Three modules complaining about the BCM, all inactive, is the signature of a
**voltage event rather than four faults** — and this truck had its battery
disconnected. U0422 reads "test failed since last DTC clear", which fits.
**No airbag warning light**, so the RCM entry is historical, not an active
restraint fault.

Do not describe this truck as having "no codes" — it has no *powertrain*
codes, which is the claim the diagnosis actually rests on.

[VERIFY] Ford's exact definition of B11D8 and the (14) sub-code were not
confirmed — the sources were unreachable.

### Live data — read 2026-09, warm idle in Park

**Largely unblocked.** The engine measures healthy on every parameter available:

- **STFT 0.78–3.13 % B1, 0 % B2** — no air leak of any significance. Short-term
  trim corrects a leak *immediately*, before long-term trim learns anything,
  so this eliminates the whole leak family: purge, PCV, booster, gaskets.
- **Misfire monitor: available and COMPLETED, DTC count 0** — it ran, it passed.
- Lambda 0.99, AFR 14.52, knock retard 0°, timing 11.5°, RPM 661, ECT 93–94 °C
- Cam actual advance −0.06° (rest position, expected at idle)
- Throttle desired 7.29° vs actual 7.56° — tracking within 0.27°
- Catalyst temps identical both banks; charging 13.8–14.0 V

**Caveat:** only 101 km and 3 warm-ups since codes were cleared, and the Fuel
System monitor reads "not completed". **LTFT 0 % / 0 % is probably
un-relearned rather than learned-and-perfect** — re-read after several hundred
km. The short-term reading does not depend on learning and stands on its own.

**Third independent line of evidence that there is no engine fault**, after the
load curve and the absence of powertrain codes.

### Anomalies from that scan

- **Ethanol fuel percent 16.08 %** on a flex-fuel truck where the content is
  *inferred*, not sensed, and Saudi pump fuel is normally E0. Affects open-loop
  fuelling only. The inference depends on the O2 sensors, which were "cleaned"
  by an unknown method. [VERIFY against a second tool]
- **Commanded purge 41 % at warm idle** — normal, but it broke an assumption in
  the idle-quality protocol. Sealing the purge port DOES change a healthy idle.
- Right front tyre 211.7 kPa against a 241 kPa label. Unrelated, but real.
- "EGR system" monitor available and completed — on this engine that covers the
  internal EGR done by cam overlap. Does not prove a valve exists.

### RPM stability — A RHYTHMIC IDLE HUNT IS PRESENT (2026-09)

**The scan app's graph screen width is ~15 seconds**, timed against the phone
clock — not the 15 minutes an earlier revision of this file assumed. The
repeating pattern therefore has a period of about **2.5–4 seconds**, and the
owner confirms the **tachometer needle visibly breathes** at idle.

That is a rhythmic hunt. **The earlier verdict of "idle control working
correctly" is withdrawn** — it was one of four independent lines of evidence
for there being no fault, and it was based on a misread axis.

| Condition | Spans (max − min per screen) |
|---|---|
| **A/C OFF** | 37, 74, 38, 30, 53 rpm |
| **A/C ON** | 64, 76, 64, 81, 75, 68 rpm |

Bare idle: **30–53 rpm band around 650, 4–6 cycles per 15 s screen.** A/C
roughly doubles the amplitude but the oscillation is present either way, so
the compressor is not its cause.

### Paired traces (2026-09) — the PCM COMMANDS the oscillation

**`Fuel/Air commanded equivalence ratio` is a square wave**, alternating
between about **14.41 and 14.86 AFR** (lambda ~0.98 / ~1.012) at the same
3.4–4 s period as everything else. Measured lambda on both banks follows it.
The chain, in the order the measurements support it:

```
PCM commands ±1.5 % AFR square wave → measured lambda follows (0.98–1.02)
→ cylinder torque varies → rpm swings ±15–20 → spark modulates 10–13.5°
```

That is the shape of **fore/aft catalyst control** — the deliberate dither
that exercises the catalyst's oxygen storage. Its period is set by how slowly
the catalyst stores and releases oxygen, which is why it lands at seconds
rather than at any frequency the engine turns at.

**CORRECTION — "fuel control is OUT" is withdrawn.** An earlier revision read
STFT staying within ±1.56 % as proof the fuel loop was quiet. That was a
conceptual error: **STFT is the correction applied around the commanded
ratio, not the mixture.** With the dither living in the *command*, trim
correctly sits near zero. Flat trim was never evidence of flat mixture. Fuel
control is not eliminated — it is the source of the oscillation.

**Still OUT, and these hold:**

- **EVAP purge** — commanded flat at ~40 %, drifting one LSB at a time
  (40.78 → 40.39 → 40.30 → 40.00) over two minutes. A flat command cannot
  drive an oscillation.
- **A/C compressor** — the hunt is present with A/C off.
- **Throttle, both channels** — commanded 1.57 % and actual both read
  min = max on a wide axis while rpm swings 40. The throttle never moves at
  idle on this engine.
- **MAF** — ~3.01 g/s, ±1.7 %, flat. Expected: at idle the throttle is a fixed
  restriction with ~30 kPa manifold against ~100 kPa baro, so flow is choked
  and nearly independent of engine speed. Flat MAF rules nothing in or out.
- **Cam phaser** — 0.00 to −0.06°, parked.

**Is the dither abnormal? Unknown — this is the honest limit.** ±1.5 %
commanded AFR at idle is within what many Ford PCMs run. Settling it needs a
control sample on another 3.7, or cross-correlation on a synchronised log
(`f150diag analyze`), not screenshots.

### Bank symmetry — the only asymmetry is downstream (2026-09)

| | Bank 1 | Bank 2 |
|---|---|---|
| Upstream wideband AFR | 14.41–15.05, avg 14.65 | 14.35–15.23, avg 14.68 |
| Downstream narrowband | avg **0.58–0.63**, swing **0.17–0.82** | avg **0.70–0.72**, swing **0.30–0.83** |

**Same fuel in, different exhaust out.** Both upstream sensors report the
commanded dither faithfully, fast and at equal amplitude — so fuelling is
symmetric and neither upstream sensor is lazy. Bank 1's post-cat voltage
swings deeper and leaner, meaning **bank 1's catalyst buffers less of the
dither.** First thing in this investigation to point at one component on one
bank.

**Do not condemn a catalyst on this.** Idle is the worst operating point to
judge one (lowest flow and temperature), and the slow 3.4–4 s period argues
*for* intact oxygen storage, not against it — less storage would make the loop
run faster. The reading that matters is at steady 60–80 km/h cruise.

### CONFIRMED BOTH BANKS — the correction is a SLOPE (2026-09, 01:30–01:32)

Thirteen windows of `LTFT - B1` paired with `LTFT - B2`. Idle → held ~2000 rpm
for 2 min 7 s → idle.

| | Bank 1 | Bank 2 |
|---|---|---|
| **Idle, before** | **+3.13 %** | **+2.34 %** |
| **~2000 rpm** | **0 %** | **0 %** |
| **Idle, after** | **+3.12 %**, min = avg = max | **+2.34 %**, min = avg = max |

Both banks left their idle value on throttle opening and returned to the
identical value on closing, with no re-learning interval. The load-cell
mechanism is now beyond doubt.

**The new finding: it is a gradient, not a step.** During the hold `LTFT - B1`
kept flicking to **0.78 %** and back (bank 2 less often) — the rpm would not sit
still, so the PCM kept crossing into neighbouring cells, and those hold 0.78 %.

| Operating point | Learned correction |
|---|---|
| Idle | **+3.13 / +2.34 %** |
| Just above idle | **+0.78 %** |
| ~2000 rpm | **0 %** |

**The correction fades smoothly as airflow rises — the behaviour of a fixed-size
opening.** A MAF or baro calibration error is a *proportional* error and would
put the same value in every cell. This slope is stronger evidence than the two
endpoints, and it substantially weakens the un-learned-cell objection: cells
across the range hold distinct, ordered values, which is not what an untouched
default table looks like.

**Owner's note: rpm would not hold steady at 2000.** Two ordinary explanations —
the throttle is drive-by-wire, so a steady foot is not a steady plate (this
project has already measured the PCM moving it), and coolant at 98 °C means the
fan is cycling and loading the engine. Does not touch the trim finding, which
rests on learned cell values. Worth its own capture: `Engine RPM` +
`Throttle Position Actually` at a held 2000 rpm.

### MODE 06 — the ECU is EXHAUSTED and everything PASSED (2026-09, 04:36)

**The last unread item in the ECU. It closes the electronic phase.**

**Per-cylinder misfire, TID $0C:** cyl 1 **0** · 2 **0** · 3 **0** · 4 **2** ·
5 **0** · 6 **1**. **The 10-cycle EWMA (TID $0B) is ZERO on all six.** Two counts
and one count across hundreds of thousands of firing events, with nothing
persistent, is noise. And the WOT pulls in the same session hit **6832 rpm** —
the rev limiter cuts fuel and spark, which the misfire monitor can log.
**THE SINGLE-WEAK-CYLINDER HYPOTHESIS IS ELIMINATED** — it was the last
ECU-visible mechanism that could shake a cab with no code.

**Catalysts — settled, both good, both equal:** Bank 1 **0.3711**, Bank 2
**0.3633**, limit **0.8359**. Both at 44 % of the failure threshold and within
2 % of each other. **This kills the bank 1 downstream asymmetry** recorded
earlier from idle snapshots — that was an artefact of reading a swinging
narrowband signal at the worst point for judging a converter.

**All four O2 sensors — healthy and matched:** upstream B1 and B2 both
**0.014 s** response against a **0.4 s** limit (3.5 % of allowance, identical);
downstream 0.792 / 0.856 s against 10 s. Heater currents matched too.

**Cam phasers — essentially perfect:** VVT error **0.06 ° (B1) / 0.05 ° (B2)**
against a **20 °** limit. **VCT and cam timing eliminated with evidence**, far
stronger than the live-data reading.

**Fuel system monitor:** 0 on both banks against a 0.797 limit.

**[VERIFY] one unidentified value:** `Misfire Monitor General Data` MID$A1
**TID $84 = 527.198** of 0–918.874, PASSED. Manufacturer-defined, undocumented
here, and the only value in the whole set neither near zero nor matched between
banks. It passed, so it is not a fault by the PCM's reckoning.

**Monitors since reset:** all Completed except Evaporative System, which needs
fuel-level and cold-soak conditions not yet met since the valve change.

### THE ECU PHASE IS OVER

Every test the powertrain computer can run has been run and **all passed with
margin**. The engine is sound mechanically, electronically and in its
combustion, by every measurement the vehicle can produce. **An engine-running
fault would have shown itself in at least one of them.**

What remains is **vibration and its transmission path**.

**THE PHYSICS ARGUMENT THAT WAS HERE IS PARTLY WITHDRAWN (2026-09-16).** It said
the port resolves 4–8 Hz at best and therefore cannot see anything that shakes a
cab. **The rate law measured on 2026-09-14 gives 33.3 Hz with two tiles on
screen, so Nyquist is 16.65 Hz** — and first order at 650 rpm (**10.8 Hz**) has
since been measured through the port, landing on exactly 1.000 in 11 of 11
stretches. Firing at **32.5 Hz** needs 65 Hz and remains out of reach.

**Much of what follows is still hands-on** — harmonic balancer, engine mounts,
contact point, and the phone accelerometer, which is still the only instrument
that reaches the firing pulse.

### THE LEAK IS CLOSED — idle trim −0.78 % BOTH banks (2026-09, 04:28–04:31)

`LTFT - B1` + `LTFT - B2`, warm idle in Park, three windows, adaptives fully
relearned after a proper drive.

| | Before the valve | **After, relearned** |
|---|---|---|
| `Long term fuel % trim - Bank 1` | **+3.13 %** | **−0.78 %** |
| `Long term fuel % trim - Bank 2` | **+2.34 %** | **−0.78 %** |

Both banks min = avg = max = −0.78 %, flat across all three windows, and
**identical to each other** — the same value, not merely within one step.

**This is the idle cell, at the operating point where the symptom lives, with
relearned adaptives.** It is the measurement the whole vacuum-leak investigation
was built to obtain. **The engine no longer runs lean at idle by any amount. The
purge valve was the leak.**

**The unmetered-air line is FINISHED.** PCV, brake booster, manifold gasket,
throttle body gasket, injector O-rings and the smoke test are all withdrawn —
there is no lean bias left for them to explain.

**The new valve behaves differently:** `EVAP purge` now runs **47.06–49.80 %,
actively stepping** in 0.39 % increments over tens of seconds, where the old one
sat flat at 40–41 %. The PCM is genuinely controlling purge now. It does *not*
drive the hunt — purge moves over 10–30 s, the hunt runs at 3–4 s.

**THE HUNT IS UNCHANGED:** 56, 51, 57, **67**, 61 rpm spans, same ~3.4 s rhythm,
if anything wider than the 44–55 measured at 03:23. **Clean separation — the leak
is gone and the hunt did not change. The leak was never causing the hunt.**

**Remaining, and only these:** ① **Mode 06 per-cylinder misfire counts**, the one
ECU item never read · ② the hunt itself, needing a control sample to judge · ③
the felt shake. **THE CLAIM THAT WAS HERE IS WITHDRAWN** — it read *"no tool
sampling through the OBD port can see the frequencies that shake a cab"*, on a
56–117 ms response time and Nyquist 4–8 Hz. **The measured rate is 33.3 Hz with
two tiles, Nyquist 16.65 Hz, and first order at 10.8 Hz has since been measured
through the port.** Firing at 32.5 Hz is still out of reach. See the first-order
section above.

### WIDE OPEN THROTTLE — the engine breathes PERFECTLY (2026-09, 04:02–04:03)

| Channel | Peak | Healthy target |
|---|---|---|
| `Abs. load` | **96.47 %**, sustained 91–94 % | 90–100 % on a healthy NA engine |
| `MAF` | **215.27 g/sec** | ~170–210 for 302 hp [rule of thumb] |
| `Engine RPM` | clean pull to **6832** | — |

**The curve shape matters as much as the peak.** MAF rose smoothly and linearly
from 10 to 215 g/s all the way to the limiter with **no plateau**, falling only
on lift. A restriction shows as airflow going flat while rpm keeps rising. This
engine does not do that. Cross-check: 215 g/s × ~1.4 ≈ 301 hp against a 302 hp
rating.

**ELIMINATED OUTRIGHT:** blocked or restricted **catalytic converter** (a live
suspect from the downstream O2 asymmetry — it cannot hide from this test) ·
restricted exhaust · restricted intake · poor volumetric efficiency from wear,
valve sealing or cam timing. **An engine with a breathing problem cannot reach
96 % absolute load.**

### Long term trims after the drive (04:04–04:05)

`LTFT - B1` **−1.56 %** flat · `LTFT - B2` **−0.78 %** flat — min = avg = max on
both, one quantisation step apart, both essentially zero and slightly negative.
**The +3.13 / +2.34 % lean bias is gone.** No leak signature remains.

[VERIFY] the operating condition was not recorded. **Re-read both long term
trims at warm idle in Park** — the idle cell is the one that matters for a
symptom that only appears at idle.

### WHERE THE DIAGNOSIS NOW STANDS

| System | Verdict |
|---|---|
| Fuel delivery | **Eliminated** — both banks seal on cut, 12.3:1 at WOT |
| Upstream O2 sensors | **Eliminated** — both full range, fast |
| Fuel trims | **Clean** — near zero, banks matched |
| Vacuum leak / unmetered air | **Clean** — lean bias gone after the purge valve |
| Engine breathing | **Excellent** — 96 % load, 215 g/s, no plateau |
| Catalytic converters | **Eliminated** — no restriction |
| Ignition / knock | Clean — 0° retard |
| Misfire monitor | Passed |
| Codes | None, ever |

**And the shake in P and N is still there.** The scan tool has been exhausted
honestly, and what it establishes is that **the engine is sound.** What remains
is either per-cylinder contribution (**Mode 06 — read at 04:36, after this
section was written; see *MODE 06* above, where it passed on all six cylinders**)
or mechanical isolation and contact, which produce no ECU signature at all.

### FUEL CUT TEST — bank 1 injectors SEALED (2026-09, 03:49–03:50)

Coasting in gear from ~100 km/h to 30 with the throttle shut, `Engine RPM` +
`O2S1 air:fuel`.

| Graph clock | RPM | `O2S1 air:fuel` |
|---|---|---|
| 8:36–8:54 | 1783 → 1859, on throttle | oscillating 13.49–15.84 |
| **8:55** | throttle closed | **steps vertically to 29.38** |
| 8:58–9:41 | 1631 → 843 | **29.38 flat**, min = avg = max, three windows |

29.38 is the top of the PID's range. Fuel cut held from ~1850 rpm to ~850 rpm.
(The dips and spikes in rpm during the coast are downshifts. Normal.)

**Nothing is putting fuel into bank 1 during overrun.** Injectors commanded off,
only air through the cylinders — any seepage would stop it pegging. It pegged
dead flat for a minute.

- **Leaking injector, bank 1 — ELIMINATED**, on the engine and under real
  manifold vacuum, not just on a flow bench.
- **Best O2 sensor test in this investigation.** 13.49 → 29.38 in a fraction of a
  second, held flat, repeated. A lazy or contaminated sensor cannot do that.
  **Bank 1 upstream sensor: healthy, full range, fast.** Closes an item carried
  open since the sensors were "cleaned" by an unknown method.

**Bank 2 did exactly the same** (03:58): `O2S5 air:fuel` pegged 29.38 flat,
min = avg = max, two windows, 1772 → 1381 rpm. It also swept **12.33 → 29.38** —
wider than bank 1, fast in both directions.

**THE FUEL SYSTEM IS ELIMINATED.** Leaking injectors both banks — out. Both
upstream O2 sensors — confirmed healthy across full range, closing the "cleaned
by unknown method" item carried since day one. Fuel delivery under load —
proven, 12.3:1 commanded and delivered at wide throttle, exercising pump,
regulator and injectors. With trims near zero at idle after the new purge valve,
**there is nothing left to find in fuelling.**

### THE SHAKE IS STRONG — mechanical side REOPENED (2026-09)

**Owner: the shake moves him in the seat.** Not subtle, not needle-only.

**"The hunt and the shake are one phenomenon" is WITHDRAWN.** A ±25 rpm swing at
3.4 s is a 4 % cycling of engine speed — it moves a needle, it does not shake a
person. The inference was weak anyway: **the converter damps everything** in
gear, so "both vanish in D" never distinguished them.

**MOUNTS ARE NOT ELIMINATED.** This file ruled them out because D and R feel the
same — sound for *torque-reaction* faults (a collapsed mount would load
differently in D than R), but **blind to a mount that has lost its damping**,
which is not direction-dependent.

- The engine rocks on its mounts at **8–15 Hz** at idle — felt through a seat,
  not heard.
- **Fluid-filled mounts exist to damp exactly that mode.** One that loses its
  fluid stops damping it.
- **In gear, converter drag preloads the engine against the mounts**, shifting it
  millimetres and changing the rocking mode.

[VERIFY] whether the 2014 F-150 3.7 uses hydraulic engine mounts.

**Second candidate, raised far too late: CONTACT.** Something resting against the
frame or cab — exhaust pipe, A/C line, power steering line, cooler line, wiring
loom, heat shield. **Shifting into gear rotates the engine slightly and a part
that merely touches at rest breaks contact.** Gives: strong in P, gone in D, felt
not heard, invisible to every sensor, present since purchase, unaffected by
plugs/injectors/throttle body/fluids.

**No scan data could ever see either.** Consistent with three nights of OBD work
finding a real but small fuel fault and nothing that explains a strong vibration.

**RPM SWEEP IN PARK — the best free test now available.** Hold 650, 800, 900,
1000, 1200, 1500, 1800 rpm for 20–30 s each and rate the shake. The engine rocks
on its mounts at **8–15 Hz**, and each order sweeps through that band at a
different rpm: half order is 5.4 Hz at idle, first order **10.8 Hz at idle**,
firing 32.5 Hz.

| Behaviour as rpm rises | Interpretation |
|---|---|
| Worst at idle, fading by 900–1000 | First order driving the mount rock mode — **mount or rotational imbalance** |
| Worsens around 1000–1800 then fades | **Half order — one cylinder differing**, sweeping into resonance |
| Steadily reduces, no peak | Normal; idle is the roughest point any engine runs at |
| Grows continuously with rpm | Rotational imbalance driven directly |

**ELECTRICAL LOAD AT IDLE IN PARK.** All loads on — alternator drag is a mild
version of what the converter does in D. Shake reduces → load damping is the
mechanism, fitting the D/R story. No change → load is not the mechanism and the
D/R difference comes from engine position or a contact that breaks in gear.

**The neutral coast is WITHDRAWN — it does not work.** The owner found two
faults with it and both are correct: shifting to N above a road-speed threshold
makes the PCM raise idle, so the engine is not in the same state at all; and
road and tyre vibration at 60 km/h swamps a small idle shake.

**The other tests, all free:** ① hand on engine → frame rail beside the mount →
cab floor; frame nearly as bad as engine means the mount is passing it through ·
② helper watches the engine rock through P→D→R→P · ③ hand along exhaust, A/C,
power steering, cooler lines, looms, heat shields for one spot buzzing harder
than its neighbours, then push/pull it while someone reports the seat · ④ pry bar
gently unloading each mount in turn while idling · ⑤ accelerometer to name the
family (**~10 Hz = engine rock on mounts** · 11 Hz = rotational imbalance ·
5.5 Hz = one weak cylinder · 33 Hz = firing pulse, so an isolation problem).

**Standing lesson: the owner's description of the symptom outranks an inference
drawn from graphs.** Two conclusions here have now been withdrawn because a
measured correlation was allowed to override what the vehicle actually does.

### PARK vs DRIVE, same session — the rpm hunt, measured (2026-09, 03:23–03:25)

`Engine RPM` + `Tim. adv.`, warm, standstill, minutes apart on the same engine.
**The first clean within-vehicle comparison in this investigation.**

| | **Park** — shakes | **Drive** — clean |
|---|---|---|
| Idle speed | ~650 rpm | ~550 rpm (Ford commands lower in gear) |
| RPM span | **44, 55, 53, 50 rpm** | **15, 13, 18 rpm** |
| Shape | **clean, regular, repeating** | unstructured, no rhythm |
| Period | **~3.4–3.5 s**, 4 cycles/screen | none |
| `Tim. adv.` | 11.5–16° (**≈4.5°**) | 12–14° (**≈2°**) |

**The hunt and the felt shake appear together in Park and vanish together in
Drive.** Earlier revisions argued they were separate phenomena — a 0.28 Hz
breathing and a 33 Hz vibration. **That separation is withdrawn.** A ±25 rpm
swing every 3.4 s is a 4 % cycling of engine speed: exactly a visibly breathing
needle, and exactly what is felt in a bare cab as rhythmic unevenness without
ever loping or sounding wrong. **There is one thing to explain, not two.**

**But the P/D difference is also what every healthy automatic does.** In gear the
converter loads and damps the engine, so the same torque disturbance moves the
speed far less, and a loop that limit-cycles unloaded can be stable loaded. The
coherent picture, every element measured:

```
PCM commands ±1.5 % AFR dither at ~3.4 s  (catalyst control)
→ cylinder torque ripples at that period
→ PARK  unloaded, low inertia   → ±25 rpm, FELT
→ DRIVE converter-loaded, damped → ±8 rpm, not felt
```

The purge leak added to the disturbance; removing it dropped D/R below
perception, Park is still above it.

**Whether ±25 rpm in Park is abnormal for a 3.7 is still unknown — no other one
has ever been measured. That control sample is now the deciding test.**

**Consequence for the accelerometer test:** look for a **~0.28 Hz amplitude
modulation** of the firing pulse — vibration strength rising and falling every
~3.4 s — not only for fixed frequencies. In Park and in Drive.

### ADAPTIVES WERE WIPED WITH THE REPAIR — read before any trim number

The owner disconnected the battery negative and bridged the cable to the
positive post to drain capacitance — **a full Keep Alive Memory wipe** — at the
same time as fitting the purge valve.

**Invalidated:** "long term trim learned to zero" (it was *erased*) · the whole
load-cell slope (idle +3.13/+2.34, just off idle +0.78, 2000 rpm 0) which was
learned around the OLD valve · the archived DTCs U0422 / U0140 / B11D8 · the
monitor results, freeze frame and the distance/warm-up counters. Mode 06 is
empty again.

**Survives, and it is the part that matters: short term trim is live and does
not depend on learning.** With long term at 0, short term *is* the whole
correction requested.

| Warm idle in Park | Long term | Short term | **Live total** |
|---|---|---|---|
| Before the valve | +3.13 % | ~0 | **+3.1 %** adding fuel |
| After the valve | 0 (wiped) | **−1.5 %** | **−1.5 %** removing fuel |

**~4.6 points of swing, untouched by the wipe.** The engine genuinely no longer
runs lean at idle.

**The confound:** new valve AND wiped adaptives in one operation, so the D/R
improvement has two candidate causes. Against the reset: the owner already did a
relearn plus 300 km earlier with no change — a reset alone has been tried and
failed. **Close it by letting the adaptives relearn: if the improvement came
from the reset, the shake returns in D and R as long term re-learns.**

**Rule: never wipe KAM before a measurement unless the wipe is the experiment.**
It destroys learned trims, code history, freeze frames and monitors in one
action, and adds a second variable to any repair done alongside it.

### PURGE VALVE REPLACED — shake GONE in D and R, still in P and N

**First change in the symptom in the owner's entire ownership.**

| Condition | Before | After the new purge valve |
|---|---|---|
| P / N standstill | **Worst** | **Still present** |
| D / R standstill | Less | **Gone** |
| Driving | Absent | Absent |

**The purge valve was a real contributor** — six earlier repairs changed
nothing; this one moved the symptom boundary, exactly as the trim slope
predicted. **And it is not the whole story:** the remaining shake sits in the
condition with the *highest* manifold vacuum, so the symptom still tracks vacuum
inversely and **at least one more unmetered-air source remains.**

**The truck is now its own control.** P/N shakes, D/R is clean, minutes apart,
same engine, same temperature. Ask every remaining question as *"how does P
differ from D at a standstill"* — it is the best comparison this investigation
has ever had, and it is free.

**Caveats:** the adaptives have NOT relearned — long term trim still holds
+3.13 / +2.34 %, learned around hardware no longer fitted. **Short term trim is
the honest reading now**, and it should sit *negative* at idle until long term
catches up. Also confirm the improvement survives a heat cycle before treating
it as permanent.

**Still on the list, same method (engine off → disconnect → plug manifold port →
restart → read both banks' short term trim):** PCV valve/hose/grommet/elbow,
then brake booster line and check valve. Then a smoke test for the joints that
cannot be isolated by unplugging — manifold gasket, throttle body gasket,
injector O-rings.

### Superseded suspect: EVAP purge flowing unmetered air at idle

`Commanded evaporative purge` runs at **~40 % at warm idle**, flat, on a truck
that had been idling for over three hours — long past when a canister should
still hold fuel vapour. **Purge flow enters downstream of the MAF.** If the
canister is dry, that flow is plain air the PCM never measured.

**The fraction is the whole argument.** At idle the engine takes ~3 g/s total.
At 2000 rpm it takes several times that. The same purge flow is therefore a
large share of idle airflow and a small share at 2000 rpm — **which is exactly
the slope measured above.**

It has never been touched, Mustang 3.7 sources name stuck-open as *the* purge
valve failure mode, and it frequently sets no code.

**Test it without disconnecting anything on a running engine:** engine OFF,
disconnect the purge line at the intake manifold, **plug the manifold port**,
restart, and watch `Short term fuel % trim - Bank 1` and `- Bank 2` at warm
idle. Trims falling toward zero name purge as the source. Leave the valve's
electrical connector attached so no circuit code is set.

Then the same method for the **PCV** circuit and the **brake booster** line.

### THE 2000 RPM LOAD TEST — lean ONLY at idle (2026-09, 01:18–01:20)

**The strongest finding in this investigation.** Thirteen windows of `STFT B1`
paired with `LTFT - B2`, idle → held ~2000 rpm → idle.

| Graph clock | `LTFT - B2` | Event |
|---|---|---|
| 50:57–51:17 | **2.34 %** | Idle |
| **51:17** | 2.34 → 0 | Throttle opened; `STFT B1` spikes **+9.38** (tip-in) |
| 51:17–53:45 | **0.00 %** flat, 2 min 28 s | Held ~2000 rpm |
| **53:45** | 0 → **2.34** | Throttle closed; `STFT B1` crashes **−11.72** (overrun) |

**It returned to *exactly* 2.34 instantly** — not zero climbing back. That can
only be the PCM switching back to a stored load cell it never lost. Ford indexes
long term trim by load; this capture watched it change cells twice.

| Condition | Learned correction, bank 2 |
|---|---|
| **Idle** | **+2.34 %** — adding fuel |
| **~2000 rpm** | **0 %** — adding nothing |

**The engine runs lean at idle and stops the moment the throttle opens.** That
is unmetered air downstream of the MAF — **a vacuum leak.** A fixed hole is a
large fraction of idle airflow and negligible at 2000 rpm; a MAF or baro
calibration error would stay constant across both cells instead.

**It matches the symptom's own load curve** — highest vacuum → worst shake,
throttle open → gone. First measured finding whose shape matches the complaint.

**Outstanding caveat:** the 0 % load cell could be un-learned rather than
learned (only 101 km since the codes were cleared). **Close it by re-reading the
load cell after 15–20 min of real driving.** Still ~0 % while idle sits at +2.3
to +3.1 % confirms the leak; climbing to +3 % means it is proportional — MAF or
baro — instead.

**`STFT B1` during the hold is NOT interpreted:** wrong pairing (bank 1 short
term against bank 2 long term gives no bank's total) and the throttle was
hand-held with rpm unrecorded. The finding rests on the cell values alone.

**Where to look, if it is a leak:** PCV valve, hose, grommet and elbow (never
inspected, twelve years of Jeddah heat, hard plastic cracks) · brake booster
line and check valve (never tested) · EVAP purge valve and line (never touched,
and purge runs ~40 % at idle so it is actively flowing) · intake manifold
gasket · throttle body gasket and injector O-rings (both joints disturbed during
earlier work — they cannot be the *original* cause since the shake predates all
repairs, but a disturbed joint can leak now).

**A smoke test is now justified.** Earlier revisions said trims did not warrant
one — correct then, when long term trim read 0 % and was believed un-learned.

**If the leak is uneven, feeding one runner more than the others, it also
explains the felt vibration:** the bank average moves only 2–3 %, far too little
to code, while the affected cylinder runs materially leaner and contributes a
weaker power stroke once per engine cycle — **~5.5 Hz at this idle**, which is
what the accelerometer test detects and the injector-kill test names.

### Trims trade off — read BOTH halves of the SAME bank (2026-09, 01:13)

```
Total fuel correction = short term trim + long term trim
```

Long term is the slow learned value; short term is the fast correction on top.
**When long term rises, short term falls by the same amount** — the engine
still wants the same total, the PCM has just moved it into learned memory.

| | Long term B1 | Short term B1 | **Total** |
|---|---|---|---|
| 01:00 | +3.13 % | 0 % | **+3.1 %** |
| 01:13 | ~+4.5 % (inferred) | −1.4 % | **~+3.1 %** |

`STFT B1` walked from 0 to about −1.6 % over 70 s while `LTFT - B2` held a
perfectly flat 2.34 %. **A short term trim going negative is the signature of
successful learning, not of the mixture changing. The total is unmoved at
+3 %.**

**Consequences:** neither trim number means anything alone — always capture
`Short term fuel % trim - Bank N` paired with `Long term fuel % trim - Bank N`,
same bank. And the idle long term value is still moving, so re-read it fresh
rather than reusing an earlier figure.

### Long term trims have LEARNED — and the banks match (2026-09, 01:00)

After 3 h 06 m of run time, with the engine warm at 640 rpm:

| | Bank 1 | Bank 2 |
|---|---|---|
| `Long term fuel % trim` | **+3.13 %** | **+2.34 %** |

**Two things close here.**

**1. The un-relearned caveat is gone.** Long term trim previously read exactly
0 % on both banks, which this file recorded as probably un-learned rather than
learned-and-perfect. It has now learned.

**2. THE BANK ASYMMETRY IS DEAD.** The banks differ by 0.79 % — one
quantisation step, the smallest difference the PID can express. Long term trim
is the *learned average*, far better evidence than snapshots of a short term
trim that swings every second. **Both banks are fuelled the same.** Everything
built on a bank difference is withdrawn: the bank-specific vacuum leak, the
exhaust leak upstream of one sensor, the one-sided sensor bias. The downstream
O2 asymmetry is also weak — snapshots at 01:00 show B1 at 0.79 V and B2 moving
0.67 → 0.79 between screens, so the ranges overlap heavily.

**What replaces it: a small, EVEN, lean bias.** Both banks learned positive at
about +2.3 to +3.1 %. Small — ±10 % is normal — but learned, and even. An even
bias has different candidates from a one-sided one: a leak the intake shares
equally (booster line, PCV circuit, throttle body or plenum gasket), the MAF
reading slightly low, barometric pressure reading low, or ordinary drift on a
twelve-year-old engine.

**Load separates a leak from a calibration offset.** A leak is a fixed hole —
a large fraction of idle airflow, a small fraction at 2000 rpm — so its trim
contribution shrinks as the throttle opens. A MAF or baro error is proportional
and stays constant. Ford stores long term trim in separate cells by load, so
reading it at idle and again after sustained driving reads both cells directly.

### Barometric pressure reads 97 kPa — [VERIFY]

Jeddah is at sea level, where standard is 101.3 kPa and weather moves it a
couple of kPa. 97 kPa is ~4 % low. Ford derives it from the MAP sensor; a low
reading makes the PCM under-estimate air, under-fuel, and the O2 sensors add it
back — the direction and roughly the size of the +2.3–3.1 % trim just measured.
**Suggestive, not established.** Unchecked: the actual local pressure at that
hour, and how heavily a MAF-based strategy weights the baro term (on a mass-flow
system it is a correction, not the primary input, so 4 % there should not give
4 % of fuelling error). Confirm local pressure before acting.

### Charging: ANSWERED — smart charging, not a failed alternator (2026-09)

| | 10:26–10:33 | 01:00–01:01 |
|---|---|---|
| `[BCM] Vehicle Battery Voltage` | 13.8 V | 12.8 V |
| `[BCM] Vehicle Battery Current` | 1 A | **0 A** |
| `[BCM] Battery SoC` | 88 % | **90 %** |

**State of charge rose 88 → 90 %, then charging stopped.** A failed alternator
cannot raise state of charge. The system charged the battery, it filled, current
fell to zero, voltage settled to battery level — exactly Ford's smart charging
strategy cutting alternator drag. **The 12.62 V is normal operation and the item
is closed.** Ripple and ground drops are still worth doing on their own merits.

### Superseded: bank 2 trim +3.5 % (2026-09)

**The offset is unproven.** The bank 1 half of it came from the scan app's
**Avg** field, which is session-cumulative and already ruled inadmissible here.
The bank 2 half came from reading the curve properly. A good number was
compared against a bad one. What stands: nine consecutive windows of `Short
term fuel % trim - Bank 2` stepping between 3.13 and 3.91 %. What does not:
that bank 1 differs from it. **Nothing below may be acted on until `Short term
fuel % trim - Bank 1` and `- Bank 2` are captured in one window.**

**Dating rule — read the phone clock on every screenshot.** Sessions hours
apart are not comparable; trims and adaptives move across a warm-up. Never set
a reading from one session against a reading from another.


Nine consecutive ~15 s windows of `STFT B2` paired with rpm. Bank 2's trace
steps between **3.13 and 3.91 %** — two adjacent 0.78 % codes, so the true
value is about **+3.5 %** — with excursions to 6.25 and dips to 1.56. Bank 1
sits at ~0 % (−0.9 to +1.6).

**Bank 2 needs ~3.5 % more fuel than bank 1 to reach the same lambda.**

**CORRECTION — "fuelling is symmetric across banks" is withdrawn.** That came
from the two upstream sensors reading almost the same AFR (14.65 vs 14.68).
Wrong variable: the upstream sensor reads the mixture *after* correction, the
trim reads *how much correction was needed*. Same lambda + different trim =
different underlying fuelling. Same class of error as reading STFT as the
mixture.

**It agrees with the downstream asymmetry.** More fuel into bank 2 → richer
exhaust → higher downstream voltage (0.70–0.72 vs 0.58–0.63). Two independent
measurements, same direction.

**3.5 % is not a fault on its own** — anything within ±10 % is normal and will
not set a code. What makes it worth chasing is that it is the *second*
consistent asymmetry, and the causes of a bank-specific lean bias **that
appears only at idle** match this truck's load curve:

- **Small vacuum leak feeding one bank** — biggest fraction of total airflow at
  idle, proportionally vanishing as the throttle opens.
- **Exhaust leak upstream of the bank 2 sensor** — at idle, low pulsating flow
  draws fresh air in through the leak, the sensor reads lean, the PCM adds
  fuel. Under load, exhaust pressure stays positive and no air enters. Lean at
  idle, normal under load, no code.
- **Bank 2 upstream sensor bias** — the O2 sensors were "cleaned" by an unknown
  method.

Neither of the first two is claimed. They are recorded because the *shape* fits
and nothing else examined so far does.

**Settle the offset first:** capture `STFT B1` and `STFT B2` **paired in one
window.** Both figures above come from captures taken at different points in
the same session.

### Graph axis width — settled by two clocks (2026-09)

Across nine consecutive screenshots the graph clock ran 21:20 → 23:55 while the
phone clock ran 12:48 → 12:51. That is **2 min 35 s of graph against ~3 min of
real time**, so the axis is MM:SS, gridlines are 5 s, and the screen is ~15 s
wide. An HH:MM reading would need 2 h 35 m to elapse in 3 minutes. The question
is retired.

**Why this matters more than it looks.** *Every* period, cycle count and
frequency in this investigation is derived from that screen width — the 3.4 s
oscillation, the 0.28 Hz, the whole order analysis. It originated as the owner's
approximate by-eye estimate ("about 15 seconds"), and an earlier revision of this
file assumed 15 *minutes* and was wrong by a factor of sixty. **The two-clock
check is what makes it safe to build on**, because it confirms the axis
independently of the estimate. Do not weaken it back to an estimate.

### Amplitude — do not overstate it

Paired captures show a **24–34 rpm** band, tighter than the earlier 30–53.
That is ±12–17 rpm. This project's own tooling gates a hunt at 30 rpm p2p, so
the truck sits **on the line**. A ±15 rpm limit cycle is something many
healthy engines do — the idle governor has finite bandwidth.

Two readings remain and rpm alone cannot separate them: a real fault, or a
normal governor limit cycle that happens to be visible in the needle.

### Measured: the governor is limit-cycling on SPARK

**Throttle: static.** In four windows with a wide axis (6.2–8.2°) the throttle
reads min = max, dead flat, while rpm swings 40. The apparent movement in
other windows is monotonic drift of 0.03–0.06° on a zoomed axis.

**Timing advance: swinging 10–13.5°**, ~3.5° peak-to-peak, in rhythm with rpm.
On a transient at 59:49 rpm surged to 723 and timing was driven to **6°**;
rpm then fell to 614 and timing jumped to **15°**. Textbook governor action.

**So the PCM trims idle with spark, not air** — which is why the throttle sat
still. A static throttle did not mean a passive PCM; it meant the other lever.

**Why this is a control loop, not a mechanical fault — the decisive argument
is arithmetic.** Nothing in this engine cycles at 3.5–4 s. Firing is ~33 Hz,
crank ~11 Hz, cam ~5.5 Hz; the oscillation is **~0.28 Hz**. A mechanical
disturbance must come from something that *moves*, and nothing moves at a
quarter of a hertz. That period belongs to a feedback loop with lag.

**Honest limit:** lead vs lag cannot be judged by eye from screenshots. Spark
and rpm are in a closed loop; separating cause from effect needs them
cross-correlated on a synchronised log — what `f150diag analyze` is for.

**Adaptives ELIMINATED.** The owner performed a relearn and drove 300 km with
no change. An earlier revision proposed young adaptives as the likely
contributor; that is withdrawn.

**VCT ELIMINATED.** `Variable camshaft actual advance #1` reads 0.00 to
−0.06° — two adjacent quantisation steps, an axis spanning six hundredths of
a degree. The phaser is parked and does not move. (Intake bank 1 only, but at
idle all four would be parked together.)

**Every PCM output is static except spark:** throttle static, fuel trim ±1.5 %,
purge flat, cam parked, spark swinging 10–13.5°. The governor holds idle with
its fast fine-trim lever alone. **OBD is exhausted** — there is nothing left to
ask the PCM.

**Correction to an over-claim.** An earlier revision argued "nothing moves at
0.28 Hz, therefore this is a control loop." That holds for *rotating* parts —
crank, cam, firing — but NOT for actuated or fluttering components, which can
oscillate on a seconds timescale. The mechanical door was closed too early.

### Untested hypothesis that fits everything: is the rpm signal itself true?

Every rpm figure in this investigation is the PCM's own measurement from the
crank sensor. If that signal is noisy — marginal sensor, damaged connector,
reluctor defect, twelve years of heat — the PCM would *believe* rpm is
wandering, modulate spark to correct a phantom, and **that spark modulation
would make the engine genuinely oscillate.** One fault, explaining the whole
data set.

**Test it by measuring engine speed independently of the PCM:** a timing light
with a tach function, or the phone accelerometer (firing frequency = rpm/60 ×
3). If the independent reading is steadier than the app's, the crank signal
is lying.

**Perspective:** 3.5° of spark swing at idle is modest — many PCMs modulate
more. With a ±12–17 rpm result this may simply be normal governor behaviour
made visible by young adaptives.

### Next — all physical, OBD is done

0. **Charging voltage — largely explained, no longer urgent.** `ECU voltage`
   averaged **12.62 V with the engine running** in one session. But the BCM
   reports `Vehicle Battery Voltage` **13.8 V**, `Vehicle Battery Current`
   **1 A**, `Battery SoC` **88 %** — so this truck has a battery monitor on the
   negative cable and runs Ford's smart charging, which deliberately drops
   charging voltage once the battery is full. Voltage falling to ~12.6 V for
   periods is that strategy working, not a dead alternator. Confirm with a DMM
   across the posts when convenient (13.5–14.5 V, dropping at times) — but the
   ripple and ground-drop checks below are now the more useful electrical
   tests.
1. **AC ripple across the battery.** DMM on AC volts at idle: under 0.1 V.
   Above that an alternator diode is injecting ripple into every sensor
   reference.
2. **Ground voltage drops.** DMM on DC mV, idling with loads on: battery
   negative → block, block → chassis, battery negative → chassis. Each under
   0.1 V.
3. **Wiggle test.** Idling with the rpm graph visible, flex and tap the crank
   sensor connector and harness first, then cam sensors, MAF, coils. Any rpm
   response is the fault.
4. **Independent rpm** — timing-light tach against the app's reading.
5. **Vacuum gauge** — not for leaks (STFT rules those out) but for combustion
   character at a bandwidth OBD cannot reach.
6. **Cylinder balance** — unplug one injector at a time, note each rpm drop.
   Six numbers; unequal drops name the cylinder.
7. **Compare against another 3.7** — still the only way to know whether
   ±15 rpm is abnormal on this engine.
8. **The felt vibration remains unexplained.** 0.28 Hz cannot be what is felt
   at 33 Hz. The phone accelerometer test addresses the actual complaint.

Still worth doing: **watch the needle on a COLD start.** The owner reports the
felt SHAKE is identical cold and hot; nobody has asked whether the NEEDLE
BREATHING is. Different observations.

### This probably does not explain the felt vibration

A 3-second breathing is ~0.3 Hz; the felt vibration at 660 rpm is firing
frequency, ~33 Hz. Likely **two separate observations**: a slow idle breathing
now measured, and a fast vibration no OBD log can resolve.

### The remaining test is not electronic

Measure the vibration, not a proxy. Phone accelerometer or spectrum app, flat
on the seat, warm idle. At ~660 rpm:

- **~33 Hz (3rd order)** → the V6 firing pulse felt through a bare regular-cab
  floor. Normal. Nothing to fix.
- **~11 Hz (1st order)** → rotational imbalance: damper, pulley, flexplate.
- **~5.5 Hz (half order)** → **one cylinder contributing differently from the
  other five.** A single weak cylinder repeats once per full engine cycle, which
  is half crank speed — not firing frequency. Correcting an earlier slip in this
  file: an uneven cylinder does NOT show up at 33 Hz. The test that names the
  cylinder is the injector-kill balance test.

### Still unmeasured

1. **Is the needle breathing present on a COLD start?** The single most
   valuable free observation available — it separates the fuel loop from
   everything else.
2. **Permanent codes (Mode 0A)** — the only code history a clear cannot destroy.
3. LTFT after several hundred km, since the current 0 % is probably un-relearned.
4. ~~Whether the A/C was running during the live-data scan.~~ **ASKED AND
   UNRECOVERABLE.** The owner's answer was **"not sure"**. The A/C state during
   that scan cannot now be established, so every reading from it must carry
   `ac=unknown` and none of it may be treated as measured-under-load.
5. VCT commanded vs actual, via the FORScan handoff, if anything still points there.

Two numbers collapse most of the diagnosis — fuel trims say whether it's a
mixture problem, misfire counters say whether it's one cylinder or all six.
**Trims also decide whether a smoke test is worth doing:** LTFT within ±10%
at idle means no leak significant enough to matter, and a smoke test would
only find leaks too small to explain anything.

## Careful

- **This engine has no external EGR valve.** The 3.7 Ti-VCT uses twin
  independent cam phasing to create *internal* EGR through valve overlap,
  which replaced the EGR valve. Do not request an "EGR position" PID and do
  not send anyone looking for the valve — earlier revisions of this file
  wrongly did both. Exhaust dilution at idle is still a live mechanism, but
  it lives in the **cam phasers**. [VERIFY against the service manual]
- The purchased history report lists fuel type as "Electric", which is wrong.
  **On drive type it agrees with the owner: this truck is 4x4** — see the top of
  this file. Earlier revisions said "the VIN says 4x2, ignore the report on
  both", and that reasoning is **WITHDRAWN**: the owner has the truck in front of
  him. `docs/f150-specs.md` and `docs/f150-diagnosis.md` carried the same error
  and are corrected.
- The odometer history is non-monotonic (a 2016 reading sits 9,000 km above
  the 2020 ones). **True distance may exceed 131,000 km** — treat wear
  intervals as "at least."
- This engine has an **internal, timing-chain-driven water pump**. If
  coolant disappears with no external leak, check the oil for coolant before
  chasing anything else. (Level is currently steady.)

**Sensor names as the scan app shows them:
[`docs/scanner-pids.md`](docs/scanner-pids.md)** — **when asking the owner for a
reading, use the exact label from that file.** Not an abbreviation, not the
engineering term, not the SAE PID name. He navigates a list on a phone; a name
that does not match the list wastes his time at the truck. The file also records
which channels return blank on this vehicle (barometric pressure, high-res MAP,
evap vapor pressure) — **but note that all three of those later returned real
values at 01:00, so treat that list as "blank in one session", not "unsupported";
the barometric 97 kPa reading and the evap −412.5 Pa reading both came from
channels this file once said never to request again** — and which are the app's
own arithmetic rather than readings from the truck.

**Calibration and tuning reference for this engine family:
[`docs/ford-3.7-cyclone-6r80-guide.md`](docs/ford-3.7-cyclone-6r80-guide.md)** —
Ford 3.7 Cyclone and 6R80, covering 2011–2014 Mustang and F-150. It carries a
four-level evidence system separating Ford-verified specifications from
technical references, observed calibration heuristics and OSID-specific values
that must be read from the vehicle. **Its idle-stability classification table is
the nearest thing this project has to a control sample**, though the values are
observed heuristics rather than Ford acceptance criteria and it says so.

**Specs and technical data: [`docs/f150-specs.md`](docs/f150-specs.md)** —
identification, engine, transmission, capacities, fluids, OBD-II buses,
intervals, part numbers. Figures are marked [VIN] / [SPEC] / [VERIFY];
never act on a [VERIFY] torque or capacity without checking the manual.

**Field sheet — the full capture protocol at the truck:
[`docs/FIELD-SHEET.md`](docs/FIELD-SHEET.md)** — every capture worth taking after
the purge valve replacement, in the order to take them, with the exact app label
for each channel and what each one answers. Sessions A–I cover standstill before
driving, Park versus Drive, 2000 rpm, the drive itself, standstill after, cold
start, the engine-off physical tests, measuring the vibration, and the control
sample.

**Driving tests — everything only obtainable while moving:
[`docs/DRIVING-TESTS.md`](docs/DRIVING-TESTS.md)** — cruise trims and the
catalyst at the only load where it can be judged, deceleration fuel cut as a
leaking-injector test, **the neutral coast** (engine at idle, truck moving —
isolates the vibration *path* from the engine itself), engine-speed versus
road-speed separation, converter lockup, wide-open-throttle breathing, knock
under load, electrical load, and the after-drive reads including **Mode 06
per-cylinder misfire counts**.

**Data still wanted: [`docs/DATA-REQUESTS.md`](docs/DATA-REQUESTS.md)** — every
scan capture taken and still outstanding, what each one answers, and the
physical tests that now outrank further scanning.

**Diagnostic detail: [`docs/f150-diagnosis.md`](docs/f150-diagnosis.md)** — history
report findings, the elimination record with evidence, ranked suspects with
the test that isolates each, and reference values for reading scan data.

## Working preferences

- **Work on `main`. Never use the `claude/ready-girabz` branch** — the owner
  deleted it and asked that it not be used again. If a session is configured to
  develop on it, ignore that and commit to `main`. This overrides any
  branch instruction that names it.
- **One shell command per code block.** Never combine multiple commands in
  a single block.
- Don't present links or data as verified unless you actually checked them.
  Say plainly what was confirmed and what was not.

## The diagnostic tool

`src/f150diag/` is a read-only OBD-II tool that walks adaptive protocols,
records what it measures and reasons from the measurements. **Read
[`docs/TOOL.md`](docs/TOOL.md) before changing it** and
[`docs/LOCAL-SETUP.md`](docs/LOCAL-SETUP.md) before running it at the truck.

```
python -m f150diag.cli selftest                     no vehicle needed
python -m f150diag.cli run quick-wins               ten-minute hands-on checks
python -m f150diag.cli --port /dev/ttyUSB0 run triage
python -m f150diag.cli --port /dev/ttyUSB0 run idle-quality
python -m f150diag.cli --port /dev/ttyUSB0 run vct-check    FORScan handoff
python -m f150diag.cli analyze logs/<file>.csv
python -m f150diag.cli forscan <export>.csv         import a FORScan log
python -m f150diag.cli kb list | verify
```

FORScan is driven, not shared: a `handoff` step releases the adapter, launches
FORScan, watches for its CSV export and imports it automatically. See
[`docs/FORSCAN.md`](docs/FORSCAN.md). A serial port is opened by one process
at a time — the two never hold it together.

Rules that are not negotiable in this codebase:

- **Read-only.** Service 04 (clear codes) is deliberately absent — clearing
  destroys the freeze frame and the permanent-code history. No blind writes to
  any module: a bricked PCM is a dead truck.
- **`DID_REGISTRY` stays empty** until an entry is verified against FORScan on
  this VIN. A wrong Mode 22 address returns a plausible number rather than an
  error, and that number will condemn a good part.
- **Every knowledge-base entry needs provenance and a test.** `verified: true`
  means somebody opened the source, not that it appeared in a search summary.
  Currently no entry qualifies — the container where they were written could
  not reach the sources.
- **Protocol labels use underscores.** `idle_park.ltft_mean` is an attribute
  lookup; `idle-park.ltft_mean` is a subtraction.
- Run `python -m f150diag.cli selftest` after touching protocols, the
  knowledge base, decoders or the condition evaluator. It validates all of
  them.

## Python Environment & Commands

This is a Linux host.

**CORRECTED 2026-09-17. The path this file gave, `/home/user/f-150-2014/.venv/`,
DOES NOT EXIST** — note the lower-case `f`, where the repository is
`/home/user/F-150-2014`. Anything following those instructions failed.

- **`pyproject.toml` now exists**, so the tool installs properly:
  `python3 -m pip install -e .` from the repository root. That puts a `f150diag`
  command on the path and makes the package importable from any directory.
- **`PYTHONPATH=src python3 -m f150diag.cli ...` always works** from the
  repository root without installing anything, and is the safe fallback.
- **Never use `source .venv/bin/activate`.** If a virtual environment is in use,
  invoke its binary directly.
- **Run an analysis script:** `python3 data/<name>.py`.
- `python3 -m f150diag.cli selftest` needs no vehicle and validates the
  protocols, decoders, condition evaluator and knowledge base.

### Connecting to the truck

**`docs/LOCAL-SETUP.md` section 2a carries the capture aimed at the CURRENT
symptom** — one parameter, five minutes, warm Park idle:

```
f150diag --port /dev/ttyUSB0 --baud 115200 live --pids rpm --seconds 300 --label idle-rate
python3 data/rpm_rate.py logs/<file>.csv
```

**A PERSISTENT INTERACTIVE LINK ALSO EXISTS:
[`data/f150_live.py`](data/f150_live.py)** — one background thread owns the
adapter and logs `Engine RPM` continuously at full rate while the foreground
answers typed questions off the same connection. It writes `elapsed_s,rpm`,
which `data/rpm_rate.py` and `data/idle_events.py` read directly. **Read-only by
allowlist; `CLEAR_DTC` is never imported.** See `docs/LOCAL-SETUP.md` §2b —
including that **`python-obd` cannot talk to a Bluetooth Low Energy adapter at
all**, which is what most cheap clones and anything paired to an iPhone are.

**RUNNING ON WINDOWS FROM `cmd`: read
[`docs/WINDOWS-SETUP.md`](docs/WINDOWS-SETUP.md) first.** Two things broke and
are now fixed in code, both reproduced rather than guessed:

* **`f150diag selftest` died part way through on cp437**, the standard US `cmd`
  codepage, with `UnicodeEncodeError` on an **em dash in its own output**. Python
  writes Unicode straight to a Windows *console*, so typing it by hand can look
  fine — **the crash bites when output is redirected or piped, which is what
  happens when an agent runs the command.** `cli.py` and every tool in `data/`
  now force UTF-8 on stdout and stderr; verified on cp437, cp850 and cp1252.
* **The analysis tools globbed relative to the current directory**, so run from
  anywhere but the repository root they matched nothing, printed an empty table
  and **exited 0**. `data/_repo.py` now anchors every path to the repository.

**Use `.venv\Scripts\python.exe` directly — never `activate`.** `--ports` on
`data/f150_live.py` lists COM ports before connecting, because auto-detect takes
the first port that answers and that is often the wrong one.

**A NOTE FOR ANY SESSION RUNNING IN THE CLOUD: you cannot reach the truck.**
A Claude Code Remote container has no serial device (`/dev/ttyUSB*` does not
exist) and no route to Jeddah. Scripts that open an adapter only run on a
machine physically plugged into the truck. **Do not claim to have queried the
vehicle from a remote session.**

`f150diag ports` lists serial ports. **`--pids` takes single PID names or the
groups `idle`, `fuel`, `o2`, `evap`, `air`, `full`** — and every extra parameter
divides the sample rate, so name exactly what the question needs. The rate law
measured for Car Scanner is about tiles on a phone screen; **this tool polls
precisely what you list**, which is why a single-parameter capture is the fast
one here too.
