# Context

The owner is a working mechanic in Jeddah, Saudi Arabia. He does the
hands-on work himself — give him diagnostic reasoning, specs and procedures,
not "see a mechanic."

## The truck

**2014 Ford F-150 XL Regular Cab · 3.7L V6 Ti-VCT · 6R80 auto · 4x2**
VIN `1FTMF1EM1EFC80632` · 131,000 km (Aug 2026) · Jeddah

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

**D and R feel the same as each other.** Engine torque reacts in opposite
directions in D and R, so a collapsed mount or a torque-reaction contact
would differ between them. This is a better mount test than the old D-vs-N
one, and it keeps **mounts, flexplate and driveline ruled out** — as does
the symptom reproducing at a standstill in Park.

### Already done — none of it changed the shake

Spark plugs · air filter · oil and filter · coolant flush · 6R80 fluid
(113,000 km) · **throttle body removed and hand-cleaned** · **injectors
removed, cleaned and flow-tested** · O2 sensors "cleaned", method unknown.

Also established: factory airbox and duct (no oiled filter) · always 95
octane from the same station · no aftermarket tune, no evidence of prior
engine work · thermostat reaches and holds temperature · coolant level
steady · currently 5W-30 (spec is 5W-20 — correct at next change, but it is
not the cause) · battery disconnected once, relearn done plus 300 km.

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
4. Whether the A/C was running during the live-data scan. If it was, those
   trims were measured under load, which makes them stronger evidence.
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
evap vapor pressure) so they are never requested again, and which are the app's
own arithmetic rather than readings from the truck.

**Specs and technical data: [`docs/f150-specs.md`](docs/f150-specs.md)** —
identification, engine, transmission, capacities, fluids, OBD-II buses,
intervals, part numbers. Figures are marked [VIN] / [SPEC] / [VERIFY];
never act on a [VERIFY] torque or capacity without checking the manual.

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
