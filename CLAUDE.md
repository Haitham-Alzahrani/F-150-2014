# Context

The owner is a working mechanic in Jeddah, Saudi Arabia. He does the
hands-on work himself — give him diagnostic reasoning, specs and procedures,
not "see a mechanic."

## The truck

**2014 Ford F-150 XL Regular Cab · 3.7L V6 Ti-VCT · 6R80 auto · 4x2**
VIN `1FTMF1EM1EFC80632` · 131,000 km (Aug 2026) · Jeddah

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
octane from the same station · no aftermarket tune, no evidence of prior
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
thermostat · coolant intrusion · PCM tune · adaptive memory.

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

What remains is **vibration and its transmission path**, which the OBD port
cannot see for reasons of physics: the app answers every 56–117 ms, resolving
4–8 Hz at best, while first order at 650 rpm is **10.8 Hz** and firing is
**32.5 Hz**. **Everything from here is hands-on** — harmonic balancer, engine
mounts, contact point, and the phone accelerometer to name the frequency.

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
the felt shake, which is **invisible to this tool by physics**: the app's
response time is 56–117 ms, resolving 4–8 Hz at best, while first order at
650 rpm is 10.8 Hz and firing is 32.5 Hz. **No tool sampling through the OBD port
can see the frequencies that shake a cab.**

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
- The purchased history report wrongly lists fuel type as "Electric" and
  drive as "4WD". The VIN says **4x2**. Ignore the report on both.
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

- **Virtual environment path:** `/home/user/f-150-2014/.venv/`
- **Never use `source .venv/bin/activate`.** Always invoke the binary path
  directly.
- **Run a script:** `/home/user/f-150-2014/.venv/bin/python <filename>.py`
- **Install packages:** `/home/user/f-150-2014/.venv/bin/pip install <package>`
- The package lives under `src/`, so run it as
  `PYTHONPATH=src /home/user/f-150-2014/.venv/bin/python -m f150diag.cli ...`
