# 2014 F-150 3.7L — Unstable Idle Diagnosis

Working log for VIN `1FTMF1EM1EFC80632`. Records what was checked, what it
ruled out, and what is still open.

**Status:** open — but there is now a measured lead with the right shape.
**Long term fuel trim reads +2.34 % at idle and 0 % at ~2000 rpm** — the lean
correction exists only at idle and vanishes when the throttle opens. That is the
signature of a vacuum leak, and it is the same load curve as the symptom itself.
See [THE 2000 RPM LOAD TEST](#the-2000-rpm-load-test--the-lean-correction-exists-only-at-idle-2026-09-0118-0120).
One confirmation is outstanding: re-read the load cell after a proper drive, to
rule out its 0 % being un-learned rather than learned.

---

## Vehicle identification

Decoded from the VIN and the door jamb label.

| Field | Value |
|---|---|
| VIN | `1FTMF1EM1EFC80632` |
| Model | Ford F-150 XL, Regular Cab, 8-ft box |
| Engine | 3.7L V6 Ti-VCT (Cyclone), ~302 hp |
| Transmission | 6R80 6-speed automatic |
| Drive | **4x2** — VIN position 5 (`F1E`) |
| Built | 08/2014 · in service 19 Nov 2014 |
| Odometer | 131,000 km (Aug 2026) |

Door label: GVWR 3016 kg (6650 lb) · FAWR 1497 kg · RAWR 1588 kg ·
P255/65R17 108H on 17x7.5J · **35 psi cold, front and rear** ·
WB 126" · axle code 26 · paint UJ Sterling Gray · interior CS Steel Gray.

### Errors in the vehicle history report

The purchased report contains two fields that contradict the VIN. Do not
act on them:

- Lists fuel type as **"Electric"** — it is gasoline.
- Lists drive as **"Four-wheel Drive"** — VIN says 4x2. Confirm visually
  (look for a front driveshaft and transfer case) before ordering any
  driveline part.

---

## History report findings

Source: Saudi vehicle history report #9016795, dated 2025-01-26.
32 dealer visits with Aljazirah Vehicles, 2015–2021.

### Odometer sequence is not monotonic

| Date | Reading |
|---|---|
| 2016-12-26 | 49,306 km |
| 2020-03-08 | **40,124 km** ← lower than 2016 |
| 2020-03-23 | 40,547 km |
| 2021-03-04 | 49,381 km |
| 2021-04-29 | 54,533 km |
| 2022-08-28 | 91,205 km |
| 2023-08-18 | 108,905 km |
| 2025-01-03 | 117,029 km |

The 2016 entry sits ~9,000 km above the 2020 readings. Either a data-entry
error in 2016, or a cluster was swapped or rolled back between 2016 and
2020. Note that 49,306 (2016) and 49,381 (2021) are suspiciously close,
which points toward a mis-keyed record — but it cannot be proven from the
report alone.

**Consequence: true accumulated distance may exceed 131,000 km. Treat all
wear-item intervals as "at least."**

### Service gap

Last dealer visit 2021-04-29 at 54,533 km. That leaves roughly **76,500 km
with no dealer service record.** Whatever was or wasn't done in that period
is unknown — relevant to cam phaser condition, which depends on oil history.

### Other notes

- 2020-02-26 visit logged as *فحص الماكينة لا تعمل* — engine inspection,
  no-start / not running.
- No accident history. Two owners. No recalls on file.
- Warranty expired 2017-11-19.
- Service life in Aseer, Jizan and Dammam — hot climate, so every
  maintenance interval should be treated as severe duty.

---

## Symptom — as actually characterised

A **small** vibration felt in the cab, with visible movement on the
tachometer. Refined description from the owner:

- It is **felt, not heard.** From under the hood a trained ear cannot tell
  the engine has a problem.
- The engine **does not lope, stumble, or feel close to stalling.**
- Idle rpm is normal, **650–750** warm in P, A/C off.
- **No change with A/C on.**
- **Identical cold and hot.**
- Present **since purchase** — the truck has never been smooth in this
  owner's hands.
- **No check engine light, ever**, and a complete multi-module scan shows
  **no powertrain code of any kind** — see *Codes read* below.

That description matters. A charge-dilution or vacuum-leak fault severe
enough to shake a cab produces an *audibly* uneven idle. This one does not.

---

## RPM stability — 2026-09 — A RHYTHMIC IDLE HUNT IS PRESENT

**This section reverses an earlier conclusion. Read the correction first.**

### The correction

Earlier revisions of this document read the scan app's graph x-axis as
wall-clock time and concluded that the rpm pattern had a 3-5 minute period,
which was attributed to load tracking and called normal idle control.

**The screen width is about 15 seconds, timed against the phone clock.** The
repeating pattern therefore has a period of roughly **2.5-4 seconds**, not
minutes. The owner also confirms the tachometer needle **visibly breathes** at
idle, which independently establishes the timescale without reference to the
app at all.

A rhythmic oscillation of a few seconds is exactly what this file's own
threshold names as a fault: *"±100 rpm or a rhythmic hunt is a real fault."*
The amplitude is modest, but the structure is unmistakable.

**The previous verdict of "idle speed control is working correctly" was wrong,
and it was one of four independent lines of evidence for there being no fault.
That line is withdrawn.**

### The measurement

Amplitude, measured as max minus min per screen:

| Condition | Spans |
|---|---|
| **A/C OFF** | 37, 74, 38, 30, 53 rpm |
| **A/C ON** | 64, 76, 64, 81, 75, 68 rpm |

Bare idle sits in a **30-53 rpm band around 650**, with 4-6 cycles per
15-second screen — a period of about **2.5-4 seconds**.

A/C on roughly doubles the amplitude, as expected from compressor cycling
adding load on top of the underlying oscillation. **The oscillation is present
in both conditions**, so the compressor is not its cause.

**One discrete event:** in one A/C-off window rpm dips to 606-612, holds
briefly, then recovers with an overshoot to 680. It has width, so it is not a
dropped frame. Something loaded the engine momentarily — cooling fan
engagement is the obvious candidate — and the PCM caught it. One occurrence in
five windows.

### Paired traces — what has now been eliminated (2026-09)

Two parameters captured against rpm on a shared timebase, 15-second screen
width, warm idle in Park.

**Test A — rpm against short-term fuel trim, bank 1.**

STFT is quantised in 0.78 % steps (one LSB of the PID) and never leaves the
band between −1.56 % and +1.56 %. Session averages across eight captures:
−0.92, −0.44, −0.17, −0.39, −0.34, −0.25, −0.61, −0.47.

That is essentially zero correction, continuously. **If the closed-loop fuel
loop were hunting, STFT would swing ±10-20 % in rhythm with the rpm. It does
not.** The loop is dithering at its resolution floor.

**The oxygen sensor hypothesis is eliminated.** Those sensors are producing
corrections far too small to move the idle 40 rpm. They may still be worth
replacing on their own merits; they are not causing this.

**Test B — rpm against commanded evaporative purge.**

Purge is **flat**: 40.78 % holding steady, then stepping down one resolution
unit at a time (40.78 → 40.39 → 40.30 → 40.00) across about two minutes.
Those steps are 0.39 % apart, exactly one LSB. A slow drift, not a cycle.

**A flat command cannot drive an oscillation. Purge is eliminated.** This also
withdraws an earlier over-reading: the consistently slightly-negative STFT
average was taken as a possible vapour signature, but at half a percent that
was reading meaning into a rounding step.

### Reading these graphs: check the axis before judging amplitude

**The scan app auto-scales the y-axis to whatever range the data occupies.**
When a value is nearly constant, the axis zooms in until normal rounding
flicker fills the whole screen height and looks like a violent oscillation.

Two examples from this vehicle, both of which misled the analysis at first:

- The **purge** trace shows full-height vertical spikes. Its axis spans 40.40
  to 40.78 — a range of **0.38 %**. The spikes are the value flicking between
  40.39 and 40.78, which are *adjacent* values: the PID resolves 0.392 % per
  step, so there is nothing between them. Rounding noise on a flat signal.
- The **short-term fuel trim** trace looks like a square wave. Its axis spans
  about ±1.5 %, and its resolution is 0.78 % per step. It is the loop
  dithering across two or three steps.

By contrast the **rpm** axis spans 618-703, an 85 rpm range, and the trace
genuinely occupies a third of it. That one is a real oscillation.

This caused a real error: the consistently slightly-negative trim average was
read as a possible fuel-vapour signature and had to be withdrawn. Check the
axis range first, every time.

### Amplitude — stated honestly

In the paired captures the band is **24-34 rpm**, tighter than the 30-53
measured earlier. That is ±12-17 rpm around 650.

That is small. This project's own tooling gates a "hunt" at 30 rpm
peak-to-peak, so the truck sits on the line. **A limit cycle of ±15 rpm is
something many healthy engines do** — the idle governor has finite bandwidth
and hunts slightly by design.

Two readings remain alive and rpm alone cannot separate them:

1. A real fault
2. A normal governor limit cycle that happens to be visible in the needle

### Test C — rpm against timing advance: the governor is using spark

Axis check first: the timing axis spans 9.5-13.5 degrees in most windows, a
real 3-4 degree range rather than a zoom artifact.

**Spark advance oscillates between about 10 and 13.5 degrees, continuously,
in rhythm with the rpm.**

The clearest evidence is a transient at 59:49. Rpm surges to 723 and timing is
driven down to **6 degrees**; rpm then falls through to 614 and timing jumps
to **15 degrees**. That is a governor behaving exactly as designed — retard
spark to remove torque when speed is high, advance it to add torque when speed
is low.

**The PCM is controlling idle speed with spark, not air.** That is why the
throttle sat motionless: it is not the actuator in use. The earlier
discriminator therefore needs restating — a static throttle did not mean the
PCM was passive, it meant the PCM was using the other lever.

### Why this is a control loop and not a mechanical disturbance

The decisive argument is arithmetic rather than graphical. **Nothing in this
engine cycles at 3.5-4 seconds.**

| Process | Frequency at 650 rpm |
|---|---|
| Firing events | ~33 Hz |
| Crankshaft rotation | ~11 Hz |
| Camshaft rotation | ~5.5 Hz |
| **The observed oscillation** | **~0.28 Hz** |

A mechanical or combustion disturbance must originate in something that moves.
Nothing in the engine moves at a quarter of a hertz. That period belongs to a
feedback loop with lag in it, not to a rotating assembly.

**Reading: the idle governor is limit-cycling.** Not a mechanical fault.

**Honest limit:** lead versus lag cannot be determined by eye from
screenshots. Spark and rpm are locked in a closed loop, and separating cause
from effect requires the two cross-correlated on a synchronised log — which is
what `f150diag analyze` exists to do and what the phone app cannot provide.

### Test D — cam phaser: parked, eliminated

`Variable camshaft actual advance #1` reads between 0.00 and −0.06 degrees.
The axis spans six hundredths of a degree and those two values are adjacent
quantisation steps, so the dense vertical lines are the auto-scaling artifact
recorded above, not movement. **The phaser sits at its rest position and does
not move.** VCT is eliminated as the source of the oscillation.

Limit: this is intake bank 1 only, one of four phasers. At idle all four
would be parked together, but only one was measured.

### The scoreboard: every PCM output is static except spark

| PCM output | State at warm idle |
|---|---|
| Throttle position | static |
| Fuel trim | static, ±1.5 % |
| Commanded purge | static |
| Cam phaser | parked |
| **Spark advance** | **swinging 10-13.5°** |

The governor holds idle with its fast fine-trim lever alone, everything else
frozen. **The OBD investigation is exhausted** — there is nothing further to
ask the PCM.

### Untested hypothesis that would explain the whole data set

**Is the rpm signal itself true?**

Every rpm figure in this investigation is the PCM's own measurement, taken
from the crankshaft position sensor. If that signal is noisy — a marginal
sensor, a damaged connector, a reluctor wheel defect, twelve years of Jeddah
heat on a harness — then the PCM *believes* rpm is wandering, modulates spark
to correct a disturbance that does not exist, and **that spark modulation
makes the engine genuinely oscillate.**

One fault, producing every observation recorded here: static air, static fuel,
parked cam, swinging spark, wandering rpm, and a felt roughness.

**Test by measuring engine speed independently of the PCM:**

- A timing light with a tach function, or an inductive tach on a plug lead
- The phone accelerometer: firing frequency should equal rpm/60 × 3

If the independent reading is steadier than the app's, the crank signal is
lying and the sensor or its wiring is the fault.

### Withdrawn: the adaptives hypothesis

An earlier revision proposed that young adaptives were the likely contributor,
on the basis of 101 km and 3 warm-ups since codes were cleared with LTFT at
exactly 0.0 % on both banks.

**The owner has since confirmed a relearn was performed and 300 km driven,
with no change to the symptom. The hypothesis is withdrawn.**

### Amplitude, in perspective

A 3.5 degree spark swing at idle is modest; many PCMs modulate considerably
more for idle control. Combined with a ±12-17 rpm result, this may well be
normal governor behaviour made visible by young adaptives.

### What oscillates with a period of a few seconds

**SUPERSEDED — this section named the oxygen sensors as the leading suspect.
They have since been measured and are fast, clean and symmetric across both
banks. The seconds-scale period belongs to the fore/aft catalyst control loop,
whose dither the PCM commands deliberately. See
[Paired traces](#paired-traces--2026-09--the-pcm-commands-the-oscillation).
The reasoning below is kept only because the cold-start test it proposes is
still worth running.**

A 2.5-4 second cycle is characteristic of the **closed-loop fuel control
loop**, whose speed is set by how fast the upstream oxygen sensors switch. A
slow sensor lengthens the loop and increases its overshoot: mixture goes rich,
the sensor reports late, the correction overshoots lean, and repeats. Each
cycle moves the idle slightly.

**The oxygen sensors on this truck were "cleaned" by an unknown method.** That
has been carried as a separate housekeeping item throughout this project. It
is now the leading suspect for this oscillation.

Other candidates at this period:

- **EVAP purge cycling** — commanded at 41 % at warm idle, measured
- **Idle air control instability**

### The test that separates them, and it is free

**Watch the tachometer on a cold start, before the engine warms.**

A cold engine runs **open loop** — the PCM ignores the oxygen sensors entirely
and fuels from a table.

| Observation | Conclusion |
|---|---|
| Breathing **absent cold**, appears once warm | Closed-loop fuel control. The O2 sensors are the cause. |
| Breathing **present cold and warm alike** | Not the fuel loop. Look at purge and idle air control. |

Note carefully: the owner reports the *felt shake* is identical cold and hot.
**Nobody has yet asked whether the needle breathing is identical cold and hot.**
Those are different observations and earlier revisions of this file treated
them as one.

**Second free test, warm:** unplug the purge valve's electrical connector and
watch the needle for a minute. De-energised the valve closes. No hose is
disconnected, so there is no stall risk. If the breathing stops, it is purge.

**The trace that separates them — rpm against throttle position actual:**

| Observation | Meaning |
|---|---|
| Throttle angle oscillating in rhythm with rpm | The PCM is actively moving the throttle — idle governor cycling. Normal, or at worst an idle relearn / throttle body matter. |
| Throttle angle steady while rpm oscillates | The PCM is holding still and something is *disturbing* the engine. Mechanical or combustion. |

Then rpm against timing advance. If advance is swinging, the PCM is fighting a
disturbance with spark, which points the same way as a steady throttle.

### Does this explain the felt vibration?

**Probably not on its own.** A 3-second breathing is about 0.3 Hz. The felt
vibration at 660 rpm is the firing frequency, 33 Hz. Those remain different
phenomena.

It is likely there are **two separate observations** here: a slow idle
breathing, now measured and worth chasing, and a fast vibration that no OBD
log can resolve. The frequency test described below addresses the second.

---

## Paired traces — 2026-09 — THE PCM COMMANDS THE OSCILLATION

Every trace in this section is a phone-app graph screen paired with
`Engine RPM`, ~15 s wide, 5 s gridlines, warm idle in Park, A/C off, timed
against the phone clock. Values are read off the plotted curve. **The app's
Min/Avg/Max fields are session-cumulative, not per-window, and are not used
anywhere below** — proof: they read an identical 617/703 on every screenshot
regardless of what the curve was doing.

### The finding

**The mixture oscillation at idle is commanded by the PCM. It is not a
disturbance the PCM is reacting to.**

`Fuel/Air commanded equivalence ratio` is a **square wave**, alternating
between about **14.41 and 14.86 AFR** (lambda ~0.98 / ~1.012), ±1.5 % about
stoichiometric, at the same 3.4-4 s period as everything else. The measured
upstream sensors follow that command. Rpm follows the resulting torque
variation. Spark advance then modulates to hold rpm.

**The causal chain, in the order the measurements support it:**

```
PCM commands a +/-1.5 % AFR square wave  (measured: 14.41 <-> 14.86)
        v
measured lambda follows                   (measured: 0.98-1.02 both banks)
        v
cylinder torque varies slightly
        v
rpm swings +/-15-20 at 3.4-4 s            (measured: 24-34 rpm p2p)
        v
spark advance modulates 10-13.5 deg       (measured: ~3.5 deg p2p)
```

This is the shape of **fore/aft catalyst control** — the deliberate rich/lean
dither a PCM uses to exercise the catalyst's oxygen storage and to run the
catalyst monitor. Its period is set by how slowly the catalyst stores and
releases oxygen, which is exactly why it lands at seconds rather than at any
frequency the engine itself turns at.

### This corrects an earlier claim in this file

An earlier revision said "fuel control is eliminated, STFT stays within
±1.56 %." That was a **conceptual error**: short-term fuel trim is the
*correction applied around the commanded ratio*, not the mixture itself. With
the dither living in the command, trim correctly stays near zero. Flat trim
was never evidence of flat mixture. **Fuel control is not eliminated — it is
the source.**

### Measured this session — what moves and what does not

| Channel | Reading across the window | Verdict |
|---|---|---|
| `Throttle actuator control` (commanded) | 1.57 %, min = max | **static** |
| `Throttle position actual` | min = max on a 6.2-8.2 deg axis | **static** |
| `Mass air flow` | ~3.01 g/s, ±1.7 % | **flat** |
| `Calculated load` | tracks rpm | derived, not a witness |
| `Timing advance` | 10-13.5 deg, ~3.5 deg p2p | **swinging, in rhythm** |
| `Fuel/Air commanded equiv ratio` | 14.41 <-> 14.86 square wave | **swinging — the driver** |
| `O2S1 air:fuel` (upstream B1) | 14.41-15.05, avg 14.64-14.67 | follows the command |
| `O2S5 air:fuel` (upstream B2) | 14.35-15.23, avg 14.66-14.70 | follows the command |
| `Short term fuel trim B1` | within ±1.56 % (2 LSB) | near zero, as expected |
| `Commanded purge` | flat ~40 %, 1 LSB drift over 2 min | **flat** |
| `Cam actual advance #1` | 0.00 to -0.06 deg | **parked** |

**The throttle never moves at idle on this engine.** Both the commanded and
the actual channel are dead flat while rpm swings 40. A static throttle was
earlier misread as "the PCM is passive". It is not passive — it holds idle
with spark, its fast fine-trim lever, and leaves the air path alone.

**MAF being flat is expected, not suspicious.** At idle the throttle is a
fixed restriction with ~30 kPa manifold against ~100 kPa baro — that is
choked flow, so mass flow is set by the throttle area and barometric
pressure, essentially independent of engine speed. A flat MAF under a
swinging rpm is what a healthy engine does here; it does not rule an air-path
disturbance in or out.

### Bank symmetry — upstream identical, downstream not

**SUPERSEDED IN PART.** The heading's claim that the banks are fuelled
identically is wrong — see *Bank 2 short-term trim runs +3.5 %* below. The
upstream sensors do read the same, but that is the corrected mixture, not the
fuelling. The downstream observation below still stands.

| | Bank 1 | Bank 2 |
|---|---|---|
| Upstream (wideband AFR) | 14.41-15.05, avg 14.65 | 14.35-15.23, avg 14.68 |
| Downstream (narrowband V) | avg **0.58-0.63**, swing **0.17-0.82** | avg **0.70-0.72**, swing **0.30-0.83** |

**Same fuel going in; different exhaust coming out.** Both upstream sensors
report the commanded dither faithfully, fast, and at the same amplitude, so
fuelling is symmetric across banks and neither upstream sensor is lazy. The
only asymmetry anywhere in this data set is downstream: bank 1's post-cat
voltage swings deeper and leaner than bank 2's, meaning bank 1's catalyst is
buffering less of the dither.

**Do not condemn a catalyst on this.** Two reasons:

1. **Idle is the wrong operating point.** Exhaust mass flow and temperature
   are at their lowest; downstream sensors are least informative here. The
   reading that matters is at steady cruise, 60-80 km/h.
2. **The period argues against it.** A catalyst with less oxygen storage
   would let the fore/aft loop run *faster*, not at the slow 3.4-4 s
   observed. If anything the slow period suggests storage is intact.

It is a real, reproducible asymmetry and it is the first thing in this
investigation to point at one component on one bank. That is worth a cruise
capture. It is not worth a converter.

### Bank 2 short-term trim runs +3.5 % where bank 1 runs 0 % (2026-09)

**WITHDRAWN — see [Session 01:00-01:01](#session-0100-0101--long-term-trims-have-learned).
Long term fuel trim has since learned to +3.13 % on bank 1 and +2.34 % on
bank 2 — a difference of one quantisation step. The banks are fuelled the same.
Everything in this section that depends on a bank difference is dead: the
bank-specific vacuum leak, the exhaust leak upstream of one sensor, the
one-sided sensor bias. Kept only as a record of how the error was made.**

**Also downgraded on its own terms, before that measurement existed:**

The bank 1 figure below came from the scan app's own **Avg** field, which is
session-cumulative rather than per-window and which this project has already
ruled inadmissible. The bank 2 figure came from reading the curve directly.
A good number was compared against a bad one.

The offset is withdrawn on that ground alone. It is not withdrawn because of
the 10:26-10:33 value read — **those screenshots are from an earlier session,
about two hours before the graphs, so they cannot contradict them.** Trims move
between sessions and across a warm-up; readings from different sessions are not
comparable and must not be set against each other. Recorded for completeness
only, from that earlier session: `Short term fuel % trim - Bank 1` showed
0.78 % on one screen and 3.13 % on another seconds later, with `Bank 2` at 0 %.
That says trims move; it says nothing about the later graphs.

**What still stands:** nine consecutive windows of `Short term fuel % trim -
Bank 2` stepping between 3.13 and 3.91 %. That is a properly read curve and it
is solid. What is *not* established is that bank 1 differs from it.

**Nothing may be concluded from this until `Short term fuel % trim - Bank 1`
and `Short term fuel % trim - Bank 2` are captured in the same window.** The
leak and sensor-bias reasoning further down is contingent on that capture and
must not be acted on before it.


Nine consecutive ~15 s windows, `Engine RPM` paired with `STFT B2`, warm idle
in Park.

| | Bank 1 | Bank 2 |
|---|---|---|
| STFT baseline | ~**0 %** (-0.9 to +1.6) | ~**+3.5 %** (steps 3.13 <-> 3.91) |
| STFT excursions | +/-1.56 % | 1.56 % to 6.25 % |

Bank 2 is consistent across all nine windows: the trace steps between 3.13 and
3.91 %, two adjacent quantisation codes (1 LSB = 0.78125 %), so the true value
sits at about **+3.5 %**, with excursions up to 5.47 and 6.25 and dips to 1.56.

**Bank 2 needs about 3.5 % more fuel than bank 1 to reach the same measured
lambda.**

#### This corrects "fuelling is symmetric across banks"

An earlier entry read the two upstream wideband sensors (avg 14.65 B1 vs
14.68 B2) as proof that both banks were fuelled identically. **Wrong variable.**
The upstream sensor reads the mixture *after* the PCM has corrected it; the
trim reads *how much correction was needed*. Identical lambda with different
trims means the underlying fuelling is not identical — bank 2 arrives leaner
and the PCM makes up the difference. Same class of error as reading STFT as
though it were the mixture.

#### It agrees with the downstream asymmetry

Bank 2 gets more fuel added, so its exhaust runs marginally richer, so its
downstream sensor sits higher (0.70-0.72 V against bank 1's 0.58-0.63 V). Two
independent measurements pointing the same direction, which makes both more
credible than either alone.

#### How much does 3.5 % matter?

**On its own, very little.** Anything within +/-10 % is normal and a few points
of bank-to-bank spread is ordinary — intake manifold air distribution alone can
produce it. It will not set a code and it is not a fault by itself.

What makes it worth pursuing is that it is the **second** consistent asymmetry,
and the causes of a bank-specific lean bias *that appears only at idle* match
this truck's load curve:

- **A small vacuum leak feeding one bank.** Largest effect at idle, when total
  airflow is smallest and any fixed leak is the biggest fraction of it.
  Vanishes proportionally as the throttle opens.
- **An exhaust leak upstream of the bank 2 sensor.** At idle, exhaust flow is
  low and strongly pulsating, so the negative pulses draw fresh air in through
  a small leak; the sensor reads lean and the PCM adds fuel. Under load,
  exhaust pressure stays positive and no air is drawn in. Lean at idle, normal
  under load, no code.
- **Bank 2 upstream sensor bias.** A sensor reading slightly lean makes the PCM
  add fuel it does not need. The O2 sensors on this truck were "cleaned" by an
  unknown method.

Neither of the first two is claimed. They are recorded because the *shape* of
the symptom fits them and nothing else examined so far has that shape.

#### The test that settles the offset

`STFT B1` and `STFT B2` **paired in one window.** Both figures above come from
captures taken at different points in the same session; a single window removes
any doubt that the offset is real rather than drift between captures. Quick to
set up and it should be done before anything is concluded from it.

#### Axis width — now settled by two clocks

Across these nine screenshots the graph clock ran 21:20 to 23:55 while the
phone clock ran 12:48 to 12:51. That is **2 min 35 s of graph against ~3 min of
real time**, so the axis is MM:SS, gridlines are 5 seconds, and the screen is
~15 seconds wide. An HH:MM reading would require 2 h 35 m to elapse in 3
minutes. This independently confirms the screen width assumed throughout, and
retires the question.

#### Phase against rpm

Not readable by eye. Bank 2's trim moves at the same seconds-scale rhythm as
everything else, but whether it leads or lags rpm cannot be judged from
screenshots of a closed loop. That needs a synchronised log and
cross-correlation (`f150diag analyze`).

### Is this dither abnormal?

**Unknown, and this is the honest limit.** ±1.5 % commanded AFR at idle is
within the range many Ford PCMs run. Nothing measured says the amplitude is
excessive; nothing measured says it is normal either. Separating the two needs
one of:

- **A control sample** — the same two channels on another 2011-2014 3.7 at
  warm idle. Still the single most decisive free test available.
- **Cross-correlation on a synchronised log**, not screenshots — which is what
  `f150diag analyze` computes. By eye, lead and lag cannot be separated in a
  closed loop.

### It still does not explain the felt vibration

The commanded dither and everything downstream of it run at ~0.28 Hz. The
vibration felt in the seat at 660 rpm is the firing pulse at ~33 Hz. These
remain two separate observations, and no OBD channel sampled at this rate can
resolve the second one. The phone-accelerometer frequency test is what
addresses the actual complaint.

### Open, from this session

- **`ECU voltage` averaged 12.62 V with the engine running**, in windows taken
  minutes after other windows in the same session read 13.76-14.0 V. Either
  Ford's smart-charging strategy dropping field excitation, or the alternator
  has stopped charging. **Deferred to a multimeter test** — the app's own
  voltage reading is not the instrument to settle this with.
- `Short term fuel trim - Bank 2` not yet captured; bank 1 only.
- `Knock retard` not yet captured paired with rpm.

---

## THE 2000 RPM LOAD TEST — the lean correction exists ONLY at idle (2026-09, 01:18-01:20)

Thirteen consecutive ~15 s windows pairing `STFT B1` with `LTFT - B2`, graph
clock 50:57 through 53:57. Sequence: idle, then a held ~2000 rpm, then back to
idle.

**This is the most informative measurement taken in this investigation.**

### The measurement

| Graph clock | `LTFT - B2` | Event |
|---|---|---|
| 50:57-51:17 | **2.34 %** | Idle |
| **51:17** | 2.34 → 0.78 → **0** | Throttle opened. `STFT B1` spikes to **+9.38** at the same instant — tip-in enrichment. |
| 51:17-53:45 | **0.00 %**, flat for 2 min 28 s | Held ~2000 rpm |
| **53:45** | 0 → 0.78 → **2.34** | Throttle closed. `STFT B1` crashes to **−11.72** at the same instant — overrun. |

### Why this proves load cells, not a reset

**Long term trim returned to exactly 2.34 %, instantly** — not to zero followed
by a slow climb back. A reset would have to re-learn from zero over minutes. An
instantaneous return to the identical value can only mean the PCM switched back
to a **stored cell it had never lost**.

Ford stores long term fuel trim in separate cells indexed by load and rpm. The
displayed value is whichever cell is currently active. This capture watched the
PCM change cells twice and come back to the same number, which establishes the
mechanism beyond argument.

**The two spikes in `STFT B1` are useful markers in their own right:** +9.38 %
on tip-in and −11.72 % on throttle closure are ordinary transient enrichment and
overrun behaviour, and they timestamp the throttle events precisely against the
long term trim's cell changes.

### What the two cells say

| Condition | Learned correction, bank 2 |
|---|---|
| **Idle** | **+2.34 %** — adding fuel |
| **~2000 rpm** | **0 %** — adding nothing |

**The engine runs lean at idle and stops running lean as soon as the throttle
opens.**

That is the signature of **unmetered air entering downstream of the MAF** — a
vacuum leak. The arithmetic is straightforward: a fixed-size opening is a large
fraction of the very small airflow at idle and a negligible fraction of the
airflow at 2000 rpm, so its fuelling effect shrinks in proportion. A MAF or
barometric calibration error would behave the opposite way, staying roughly
constant across both cells.

### It matches the symptom's own shape

| Condition | Manifold vacuum | Reported shake |
|---|---|---|
| P / N at standstill | Highest — leak draws hardest | **Worst** |
| D / R at standstill | Slightly lower | **Less** |
| Driving under load | Lowest — leak irrelevant | **Absent** |

This is the load curve recorded at the top of this document from the owner's own
description, arrived at independently. **It is the first measured finding in
this investigation whose shape matches the complaint.**

### The honest caveat, and how to close it

`LTFT - B2` read exactly 0.00 in the higher-load cell. Two readings are possible:

1. **The cell is learned, and it learned zero** — no correction needed at load.
   This is the leak conclusion.
2. **The cell is un-learned** and simply sits at its 0 % default. Only 101 km
   and 3 warm-ups have elapsed since the codes were cleared, and the idle cell
   got roughly three hours of exposure this session while the load cell got
   whatever driving happened in 101 km.

**Two things separate them, and both are already planned:**

- **The drive.** After 15-20 minutes of ordinary driving with sustained cruise,
  the load cell will be thoroughly learned. Re-read it. **If it is still at or
  near 0 % while idle sits at +2.3 to +3.1 %, reading 1 is established and the
  leak is confirmed.** If it has climbed to +3 %, the correction is proportional
  and the answer is the MAF or the barometric reading instead.
- **`Long term fuel % trim - Bank 1` paired with `Long term fuel % trim -
  Bank 2`**, captured at idle and again at 2000 rpm. Both banks, both cells, one
  capture. Bank 1's idle cell is already known at +3.13 %; its load cell is not.

### `STFT B1` during the hold — recorded, not over-read

| Window | `STFT B1` centre |
|---|---|
| 51:27-51:42 | −2.2 |
| 51:47-52:02 | −2.6 |
| 52:07-52:22 | −2.3 |
| 52:18-52:33 | −0.1 |
| 52:27-52:42 | −1.5 |
| 52:37-52:52 | **−4.5** |
| 52:47-53:02 | −1.8 |
| 53:05-53:20 | **+2.8** |
| 53:12-53:27 | +3.4 |
| 53:28-53:43 | +3.5 |

Short term trim on bank 1 ran negative for the first ~100 s of the hold and
positive for the last ~40 s. **This is not interpreted here.** Two reasons:

- **It is the wrong pairing.** `STFT B1` is bank 1; `LTFT - B2` is bank 2. A
  total correction can only be computed from both halves of the *same* bank, so
  neither bank's total is available from this capture.
- **The throttle was held by hand.** Any rpm drift changes how much the leak
  matters, and a drift downward late in the hold would produce exactly this
  rising trend. That is consistent with the leak reading but it is not evidence
  for it, because the rpm was not recorded.

The finding rests on the long term cell values alone, which do not depend on
either of those.

### What to look at, if it is a leak

The 3.7 has few vacuum connections, and the ones never inspected in twelve years
of Jeddah heat are:

- **PCV valve, its hose, grommet and elbow** — never inspected. Hard plastic
  elbows crack with age and heat.
- **Brake booster line and its check valve** — never tested.
- **EVAP purge valve and its line** — never touched, and `Commanded evaporative
  purge` runs at ~40 % at idle, so this circuit is actively flowing.
- **Intake manifold gasket** — composite manifold, twelve years.
- **Throttle body gasket** and **injector O-rings** — both joints were disturbed
  during earlier work (the throttle body was removed and hand-cleaned; the
  injectors were removed for flow testing). **They cannot be the original
  cause** — the owner reports the shake predates all repair work — but a
  disturbed joint can leak now regardless of what started it.

**A smoke test is now justified.** Earlier revisions of this file said trims did
not warrant one; that was correct at the time, when long term trim read 0 % and
was believed un-learned. It now reads +2.34 % at idle and 0 % at load, which is
precisely the pattern a smoke test is designed to locate.

**If the leak is uneven — feeding one runner more than the others — it would
also explain the felt vibration.** The bank average would move only two or three
percent, far too little to code, while the affected cylinder runs materially
leaner than its neighbours and contributes a weaker power stroke once per engine
cycle. That appears at **half engine speed, ~5.5 Hz at this idle**, which is
exactly what the phone accelerometer test is designed to detect and what the
injector-kill balance test would name.

## Session 01:12-01:13 — the trims are handing off, total correction unchanged

Four consecutive ~15 s windows pairing `STFT B1` with `LTFT - B2`, warm idle,
stationary, graph clock 45:35 through 46:43.

### LTFT B2 is settled

`LTFT - B2` plots as a **perfectly flat line at 2.34 %** in all four windows,
with min, max and average all reading 2.34. Long term trim on bank 2 has
converged and is holding.

### STFT B1 is walking negative — and that is the two trims trading off

| Window | `STFT B1` centre |
|---|---|
| 45:35-45:50 | ~**0** (swinging −1.56 to +1.56) |
| 45:55-46:12 | ~**−1.3** |
| 46:15-46:30 | ~**−1.4** |
| 46:28-46:43 | ~**−1.6** |

Bank 1's short term trim drifted steadily negative across 70 seconds. It moves
in 0.78 % steps (0, −0.78, −1.56, −2.34), so the movement is real and not
rounding.

**THE RULE THAT EXPLAINS IT, AND THAT GOVERNS EVERY TRIM READING IN THIS
PROJECT:**

```
Total fuel correction = short term trim + long term trim
```

Long term is the slow learned value; short term is the fast correction applied
on top of it. **When long term rises, short term falls by the same amount** —
the engine still needs the same total correction, it has simply been migrated
from the fast term into learned memory.

| | Long term B1 | Short term B1 | **Total** |
|---|---|---|---|
| 01:00 | +3.13 % | 0 % | **+3.1 %** |
| 01:13 | ~+4.5 % (inferred) | −1.4 % | **~+3.1 %** |

**The total has not moved.** The engine still wants about +3 % more fuel than
the PCM's base calculation. All that changed is where the PCM is storing that
knowledge.

### Consequences

1. **Neither trim number means anything on its own.** Every trim reading from
   here must capture **both halves of the same bank** — `Short term fuel % trim
   - Bank 1` paired with `Long term fuel % trim - Bank 1`, and likewise for
   bank 2. Pairing one bank's short term against the other bank's long term, as
   this capture did, cannot yield a total for either bank.
2. **The +3 % figure is confirmed, not contradicted**, by a short term trim that
   has gone negative. That negative reading is the signature of successful
   learning, not of the mixture changing.
3. **The adaptives are still actively moving.** The long term value at idle is
   not final; it was 3.13 % at 01:00 and is inferred near 4.5 % thirteen
   minutes later. Re-read it fresh rather than reusing the 01:00 figure.

### The load test is unaffected

The question the 2000 rpm test answers — does the correction shrink when
airflow triples — is a question about the **total**, and the total is stable at
about +3 %. The test stands exactly as designed, with one refinement: capture
`Short term` and `Long term` **for the same bank** so the total is readable
directly rather than inferred.

## Session 01:00-01:01 — long term trims have LEARNED

Phone clock 01:00-01:01. `Run time since engine start` **0.03:06:10** — the
engine had been idling for over three hours. Warm idle, stationary, 640 rpm.

This session settles two questions and opens one.

### Long term fuel trim is no longer zero — and the banks match

| Reading | Bank 1 | Bank 2 |
|---|---|---|
| `Long term fuel % trim` | **+3.13 %** | **+2.34 %** |
| `Short term fuel % trim` (instant) | 0 %, later 0.78 % | 4.69 % |

**The un-relearned caveat is closed.** Earlier readings had both long term trims
at exactly 0 %, which this file recorded as probably un-learned rather than
learned-and-perfect. They have now learned, and they read +3.13 and +2.34.

**The bank asymmetry is dead.** The two banks differ by 0.79 % — exactly one
quantisation step, the smallest difference the PID can express. Long term trim
is the *learned average*; it is far better evidence than snapshots of a short
term trim that swings every second. **The engine fuels both banks the same.**

Everything built on a bank difference is withdrawn: the bank-specific vacuum
leak, the exhaust leak upstream of one sensor, the one-sided sensor bias. None
of them survive two long term trims within one LSB of each other.

### What replaces it: a small, EVEN, lean bias across the whole engine

Both banks learned **positive**, both about **+2.3 to +3.1 %**. The PCM has
settled on adding roughly 3 % more fuel than its base calculation, equally on
both sides.

That is small — anything within ±10 % is normal and sets no code — but it is
now a *learned* value rather than a snapshot, and it is even. An even lean bias
has different candidates from a one-sided one:

- **A leak the intake shares equally** — the brake booster line, the PCV
  circuit, the throttle body gasket, or a manifold gasket that feeds the plenum
  rather than one runner.
- **The MAF reading slightly low**, so the PCM calculates less air than is
  actually entering and under-fuels, and the oxygen sensors add it back.
- **Barometric pressure reading low** — see below.
- **Normal drift** on a twelve-year-old engine. +3 % is genuinely unremarkable.

**The test that separates a leak from a calibration offset is load.** A leak is
a fixed hole: it is a large fraction of the air entering at idle and a small
fraction at 2000 rpm, so its trim contribution shrinks as the throttle opens. A
MAF or barometric error is proportional and stays roughly constant at every
load. Ford stores long term trim in separate cells by load, so reading it at
idle and again after sustained driving reads both cells directly.

### Barometric pressure reads 97 kPa — worth checking

`Barometric pressure` returned **97 kPa**. Jeddah is at sea level, where
standard pressure is 101.3 kPa and ordinary weather variation is a couple of
kPa either side. 97 kPa is about 4 % low for this location.

Ford derives barometric pressure from the MAP sensor. If that reading is low,
the PCM's air estimate is low, it under-fuels, and the oxygen sensors correct
it back — **which is the direction and roughly the magnitude of the +2.3 to
+3.1 % long term trim just measured.**

[VERIFY] This is suggestive, not established. Two things are unchecked: the
actual barometric pressure in Jeddah at that hour, and how heavily this PCM
weights barometric pressure against the MAF on a mass-flow-based fuelling
strategy — on a MAF system the barometric term is a correction, not the primary
input, so a 4 % error there should not produce a full 4 % fuelling error. Do
not act on it until the local pressure is confirmed against a second source.

### The charging question is answered — smart charging, not a failed alternator

| Reading | 10:26-10:33 | 01:00-01:01 |
|---|---|---|
| `[BCM] Vehicle Battery Voltage` | 13.8 V | **12.8 V** |
| `[BCM] Vehicle Battery Current` | 1 A | **0 A** |
| `[BCM] Battery SoC` | 88 % | **90 %** |
| `Control module voltage` | 13.76 V | 12.7-12.75 V |
| `OBD Module Voltage` | 14 V | 12.9 V |

**The state of charge went UP, from 88 % to 90 %, and then charging stopped.**
A failed alternator cannot raise the state of charge. The system charged the
battery, the battery reached 90 %, current fell to zero and voltage settled to
battery level.

That is precisely Ford's smart charging strategy: reduce alternator output once
the battery is full, to cut the drag on the engine. **The 12.62 V average that
was once at the top of the physical test list is normal operation.** The item is
closed. A meter check across the posts is still welcome for completeness, but
nothing hangs on it, and the AC ripple and ground drop tests remain worth doing
on their own merits.

### Downstream oxygen sensor snapshots — the asymmetry does not survive them

| Reading | Bank 1 | Bank 2 |
|---|---|---|
| One screen | 0.79 V | 0.67 V |
| Seconds later | — | 0.79 V |

Bank 2 moved from 0.67 to 0.79 between two screens. **These signals swing
constantly; a single value carries no information.** The graph capture that gave
bank 1 an average of 0.58-0.63 against bank 2's 0.70-0.72 remains the better
measurement, but the ranges overlap heavily and these snapshots show both banks
reaching the same values. **Treat the downstream asymmetry as weak and
unconfirmed**, not as a finding.

### Other values from this session

| App label | Value | Note |
|---|---|---|
| `Engine coolant temperature` | **98 °C** | Up from 93-94. Three hours idling at 36 °C ambient. Within normal; fan should cycle around 100-105. |
| `Evap. system vapor pressure` | −412.5 Pa | Slight tank vacuum, consistent with purge commanded at 40 % — confirms purge is actually flowing |
| `Commanded evaporative purge` | 40.39 % | Unchanged |
| `Calculated engine load value` | 29.02 % | Up from 27.06 |
| `Timing advance` | 13 ° | Within the 10-13.5 ° band measured on the graphs |
| `MAF air flow rate` | 2.97 g/sec | Unchanged |
| `Catalyst temperature Bank 1 / Bank 2 Sensor 1` | 459.9 / 459.9 °C | Still identical |
| `Throttle Position Desired` / `Actually` | 8.28 ° / 7.85 ° | Tracking within 0.43 ° |
| `ATF temperature var.3` | 76.69 °C | Down from 87.13 — three hours stationary, cooler doing its job |
| `Ambient air temperature` | 36 °C | |
| `Variable camshaft actual advance #1` | −0.06 ° | Still parked |
| `Knock retard` | 0 ° | Still zero |
| `Ethanol fuel percent` | 16.08 % | Unchanged and still unexplained |
| `Fuel System Status` | Closed loop | |
| Monitors | Catalyst, Oxygen Sensor, Fuel System all **Not completed** | Unchanged — still needs a drive cycle |

## Full sensor list read from the app — 2026-09, 10:26-10:33

Values as the app labels them, warm idle, 37 minutes of run time since start.
This is a value read, not a graph, so every figure is one instant.

**Dating rule — the phone clock is the only timestamp that matters.** This
session reads 10:26-10:33 on the phone; the paired graph session reads
12:48-12:51. They are about two hours apart. **Readings from different sessions
must never be compared against each other** — trims, temperatures and adaptives
all move across a warm-up and between sessions. Every screenshot in this
project is dated by its phone clock, and any comparison must state that both
sides came from the same session.

### The charging concern is largely answered

The BCM reports its own view of the electrical system:

| App label | Value |
|---|---|
| `[BCM] Vehicle Battery Voltage` | **13.8 V** |
| `[BCM] Vehicle Battery Current` | **1 A** |
| `[BCM] Battery SoC` | **88 %** |
| `Control module voltage` | 13.76 V |
| `OBD Module Voltage` | 14 V |
| `[BCM] Normalized cumulative charge when ignition is on` | 121.6 |
| `[BCM] Normalized cumulative discharge, engine on` | 10.6 |
| `[BCM] Normalized cumulative discharge, engine off` | 2.9 |

The battery is 88 % charged and taking only **1 A**. This truck therefore has
a battery monitoring sensor on the negative cable and runs Ford's smart
charging strategy, which **deliberately reduces charging voltage once the
battery is full** to reduce alternator drag. Under that strategy system voltage
routinely falls to around 12.6 V for periods, then recovers.

**That is the most likely explanation for the 12.62 V average seen in the
later session, and it demotes "the alternator has stopped charging" from the
top of the physical list.** Confirm with a meter when convenient; it is no
longer urgent, and the AC-ripple and ground-drop checks are now the more
useful electrical tests.

### Monitors — the catalyst and oxygen sensor tests have not run

`Monitor status since DTCs cleared`:

| Monitor | State |
|---|---|
| Misfire | Available / **Completed** |
| Fuel System | Available / **Not completed** |
| Components | Available / Completed |
| Catalyst | Available / **Not completed** |
| Evaporative System | Available / **Not completed** |
| Oxygen Sensor | Available / **Not completed** |
| Oxygen Sensor Heater | Available / **Not completed** |
| EGR system | Available / Completed |

**Consequence: the on-board monitoring test results (Mode 06) will hold nothing
useful about the catalysts or the oxygen sensors** — those tests have not
executed since the codes were cleared, so there is no stored result to read.
Only the misfire monitor has run, and it passed with DTC count 0.

Running them requires a proper drive cycle: full warm-up then sustained steady
cruise. The planned 60-80 km/h capture therefore does double duty — it supplies
the readings wanted *and* it makes the PCM run its own catalyst and oxygen
sensor tests, after which Mode 06 becomes worth reading.

`Fuel System Status` reads **"Closed loop, using oxygen sensor feedback to
determine fuel mix"** — confirming the engine was in closed loop for every
measurement in this project.

### Values that close out open questions

| App label | Value | What it settles |
|---|---|---|
| `Catalyst temperature Bank 1 Sensor 1` | **458.9 °C** | Identical to bank 2 |
| `Catalyst temperature Bank 2 Sensor 1` | **458.9 °C** | Both banks at the same exhaust temperature |
| `Knock retard` | **0 °** | No knock. Does not need a paired graph. |
| `Learned octane` | −0.6 | A small adaptive offset, nothing alarming |
| `Barometric pressure` | **blank** | Not supported on this vehicle — drop from the list |
| `Manifold absolute pressure (high resolution)` | **blank** | Not supported — drop from the list |
| `Absolute pedal position D` / `E` | 14.9 % / 7.45 % | Resting values, foot off the pedal |
| `PCM Odometer` | **131,313 km** | Matches the cluster — the history report's non-monotonic odometer is not reflected in the PCM |
| `ATF temperature var.3` | 87.13 °C | Transmission fluid at normal operating temperature |
| `Ambient air temperature` / `Intake air temperature` | 37 °C / 38 °C | 1 °C apart after 37 min idling — no intake heat soak |
| `Run time since engine start` | 0:37:42 | Fully warmed for every reading here |
| `Vehicle speed` | 0 km/h | Stationary |
| `Oxygen sensor 2 Bank 1 Voltage` | 0.71 V | |
| `Oxygen sensor 2 Bank 2 Voltage` | 0.73 V | Snapshots — no asymmetry visible in an instant |
| `Oxygen sensor 1 Wide Range Equivalence ratio` | 14.92 | |
| `Oxygen sensor 5 Wide Range Equivalence ratio` | 14.8 | |
| `Commanded evaporative purge` | 41.18 % | |
| `Ethanol fuel percent` | 16.08 % | Unchanged from the earlier read — still unexplained on E0 pump fuel |
| `Calculated engine load value` | 27.06 % | |
| `Absolute load value` | 14.12 % | |
| `Throttle Position Desired` / `Actually` | 7.29° / 7.56° | Tracking within 0.27° |

### Open question raised by this list

`Gear (AT)` reads **1**. On the 6R80 the transmission commands first gear
internally even with the selector in Park, so this does not by itself prove the
truck was in Drive — but every reading in this project is recorded as "Park"
and that should be confirmed rather than assumed, because Park and Drive are
known to differ in this vehicle's symptom.

### Tyre pressures, unrelated but real

| Position | Reading | Label calls for 241 kPa (35 psi) |
|---|---|---|
| Left Front | 237.53 kPa | Close enough |
| **Right Front** | **211.68 kPa** | **~4 psi low — inflate** |
| Right Rear Outer | 247.88 kPa | Fine |
| Left Rear Outer | 247.88 kPa | Fine |
| Rear Inner (both) | 0 kPa | No inner wheels — single rear wheel truck, expected |

## Live data — 2026-09, warm idle in Park

Read on the vehicle, engine warm (ECT 93–94 °C), 37 minutes running, A/C off,
ambient 37 °C. **This is the data the diagnosis was blocked on.**

### The decisive numbers

| Parameter | Reading | Reading of it |
|---|---|---|
| **Short-term fuel trim B1** | **0.78 % / 3.13 %** | Tiny. The engine needs almost no correction |
| **Short-term fuel trim B2** | **0 %** | Same |
| **Long-term fuel trim B1 / B2** | **0 % / 0 %** | See caveat below |
| **Misfire monitor** | **Available / COMPLETED**, DTC count 0 | The monitor ran and passed |
| Lambda | 0.99 | 1 % rich of stoichiometric — correct |
| Air:fuel ratio | 14.52 | Correct |
| Knock retard | 0° | No knock |
| Timing advance | 11.5° | Normal at idle |
| Engine RPM | 661 | Normal |
| ECT | 93–94 °C | Thermostat confirmed good |
| Cam actual advance #1 | −0.06° | At rest position, as expected at idle |
| Throttle desired / actual | 7.29° / 7.56° | Tracking within 0.27° — the electronic throttle is fine |
| Catalyst temp B1 / B2 | 458.9 / 458.9 °C | Identical — no bank imbalance |
| Charging voltage | 13.8–14.0 V | Charging system fine |

**Short-term trim is the strong evidence here, and it does not depend on
adaptive learning.** An unmetered air leak makes the mixture lean the instant
it exists, and short-term trim corrects positive immediately — before
long-term trim learns anything. STFT sitting between 0 % and 3 % at idle means
**there is no air leak of any significance.**

That eliminates the entire leak family by measurement: purge valve, PCV,
brake booster, intake gaskets.

**Caveat on long-term trim.** Only 101 km and 3 warm-ups since codes were
cleared, and the Fuel System monitor reads "not completed". Long-term trim of
exactly 0.0 % on both banks is more likely *not yet re-learned* than *learned
and perfect*. Re-read it after several hundred kilometres before treating it
as confirmation. The short-term reading stands on its own regardless.

### What this means

Every measurement available says the engine is running correctly. No misfire —
the monitor completed and passed. No mixture error. No leak. No knock. Cam at
its expected idle position. Throttle tracking its target. Temperature normal.

**Combined with the load curve and the absence of any powertrain code, this is
a third independent line of evidence that there is no engine fault to find.**

### Anomalies worth noting

- **Ethanol fuel percent: 16.08 %.** This is a flex-fuel truck, and on a 2014
  Ford the ethanol content is *inferred*, not measured by a sensor. Saudi pump
  fuel is normally E0. A PCM that believes the tank holds E16 will calculate
  base fuelling richer than needed — closed loop corrects that, but open loop
  (cold start, wide-open throttle) does not. Worth watching, particularly
  given the O2 sensors were "cleaned" by an unknown method and the inference
  depends on them. [VERIFY the reading against a second tool before acting]
- **Commanded evaporative purge: 41 % at warm idle.** Normal and designed —
  but it invalidated an assumption in the idle-quality protocol. See below.
- **MAF 2.93 g/s at 661 rpm** — low-normal for a 3.7 at this idle speed. Not
  alarming on its own; worth a second look if anything else points at metering.
- **Right front tyre 211.7 kPa (30.7 psi)** against a 241 kPa (35 psi) door
  label — about 4 psi low. Unrelated to the idle, but real.
- **PCM odometer 131,313 km**, consistent with the recorded distance.
- **"EGR system" monitor: Available / Completed.** Notable given this engine
  has no external EGR valve. On this engine that monitor covers the internal
  EGR function performed by cam overlap. It ran and passed. It does not prove
  a valve exists.

### Correction this forced to the idle-quality protocol

The protocol said sealing the purge port "should change nothing at all on a
healthy system". **That was wrong.** With purge commanded at 41 % at warm
idle, sealing the port changes the idle on a perfectly healthy engine.

The protocol now records commanded purge alongside the measurement, and
distinguishes a valve flowing when it is *not* commanded — which is a fault —
from flow proportional to a high commanded value, which is the system working.

---

## Codes read — 2026-09

First real scan data on this vehicle. Complete multi-module scan, generic
scan app, engine warm.

| Module | Code | Meaning | State |
|---|---|---|---|
| OBD-II + engine control unit | **U0422(00)** | Invalid data received — body control module | Archive (inactive). "Confirmed, test failed since last DTC clear" |
| OCS | **U0140(00)** | Data bus, body control module — no communication | Archive (inactive), confirmed |
| RCM | **B11D8(14)** | Restraints event notification | Archive (inactive), confirmed |

### What matters most is what is absent

**Not one P-code.** No misfire, no fuel trim, no VCT, no lean or rich code,
across a scan that covered every module. The PCM's own monitors have nothing
to say about how this engine runs.

That is a second independent line of evidence pointing where the load curve
already pointed: whatever is felt in the cab, the engine management system
does not consider it a fault.

### What the codes that are present mean

Three modules complaining about the **body control module** — invalid data
from it, no communication with it — plus a restraint entry, **and every one
of them inactive**. That is the signature of a **voltage event**, not four
independent faults. Modules drop off the bus when supply voltage sags and
each logs what it saw.

This truck had its battery disconnected. U0422 reports "test failed since
last DTC clear", so a clear happened and this logged after it. The timeline
fits.

**None of it explains the vibration.** These are body-network and restraint
codes, they are not currently active, and the vibration has been constant
since purchase — long before the battery was disconnected. An inactive code
cannot produce a continuously present symptom.

### The restraint entry, on its own account

`B11D8` in the RCM alongside an OCS module that lost communication is worth
separating from the idle question.

- **No airbag warning light** — confirmed by the owner. So this is
  historical, consistent with the voltage-event reading, and not an active
  restraint fault.
- The purchased history report claims **no accident history**. A restraints
  event entry does not contradict that on its own, since a voltage drop can
  log one — but that same report also got the fuel type and drivetrain wrong,
  so it is not strong evidence either way.

[VERIFY] Ford's exact definition of B11D8 and the meaning of the `(14)`
sub-code were not confirmed — the sources were unreachable from the
environment where this was written. Look both up before acting on them.

### Next step on codes

1. **Read permanent codes (Mode `0A`) before clearing anything.** They
   survive a clear and a battery disconnect, and they are the only code
   history that cannot be destroyed. Not yet read.
2. Then clear these four and drive normally for a week. What returns is real;
   what does not was the voltage event.

Clearing is normally refused in this project because it destroys freeze-frame
and misfire history. That objection does not apply here: there are no
powertrain codes, so there is nothing of diagnostic value to lose, and
return-after-clear is the only way to separate a live fault from a logged
past event.

---

## Is this a fault?

**Not established.** This must be settled before more money is spent.

### The case that it is normal

- The truck is a base **regular cab XL** — minimal sound deadening, cab
  mounted close to the engine, no acoustic glass.
- The 3.7 is a **60° V6**, which is not inherently balanced the way an
  inline-six or a cross-plane V8 is.
- Never smooth in the owner's entire ownership — a characteristic, not a
  change.
- No code in years, across every condition.
- Normal idle rpm; nothing stalls or nearly stalls.
- Perfect under load.
- **Six competent repairs, aimed at six different systems, every one of
  which changed nothing.** The simplest explanation for a fault that
  resists every repair is that there is no fault.

### The two tests that settle it — both free

1. **Control sample.** Find another 2014-ish F-150 regular cab with the 3.7.
   Hand on the fender at idle, then sit in the cab. Two minutes, and it
   answers what six repairs have not.
2. **Quantify the rpm movement.** Log the RPM PID for 60 s at warm idle in
   P — `src/obd_logger.py` already does this.

| RPM movement at steady warm idle | Reading |
|---|---|
| ±25–50 rpm, gentle wander | **Normal** closed-loop idle control. Every engine does this. |
| ±100 rpm or more, or a rhythmic hunt | **Real fault.** Work the ranked suspects below. |

---

## The load relationship — the key observation

Symptom strength tracks engine load, inversely:

| Condition | Manifold vacuum | Shake |
|---|---|---|
| P / N at standstill | Highest | **Worst** |
| D / R at standstill | Slightly lower | **Less** |
| Driving under load | Lowest | **Absent — pulls great, no vibration** |

**Rpm is not the variable; load is.** Across a no-load rpm sweep in Park the
symptom is roughly equal at all engine speeds. It is the arrival of *load*
that removes it.

If a fault exists, it is one whose effect scales with manifold vacuum and
vanishes when the throttle opens.

### Superseded reasoning — do not reuse

Earlier revisions of this document argued:

> In D/R the torque converter is coupled and loaded, and the fluid coupling
> damps torsional pulses... **The engine is genuinely running rough; the
> converter is masking it in gear.**

That was wrong on two counts:

1. **Every** torque-converter automatic is smoother in gear at a standstill.
   The observation was never evidence of a fault.
2. The truck being flawless under real road load rules out the entire
   worsens-under-load family that this reasoning pointed at — which is most
   of what the old ranked-suspect table contained.

### The better mount test

**D and R feel the same as each other.** Engine torque reacts in opposite
directions in D and R, so a collapsed mount or a torque-reaction contact
point would feel different between them. It does not.

Combined with the symptom reproducing at a standstill in **Park**, this
rules out mounts, flexplate, driveshaft, U-joints, tyres and wheel balance
more firmly than the old D-vs-N test ever did.

---

## Work already performed — none of it changed the shake

| Work | Detail |
|---|---|
| Spark plugs | Replaced. No change. |
| Air filter | Replaced. |
| **Throttle body** | **Removed from the manifold and hand-cleaned. No change.** |
| **Fuel injectors** | **Removed, cleaned and flow-tested.** |
| Engine oil and filter | Changed. Currently 5W-30. |
| Coolant | Flushed and replaced. Level steady since. |
| 6R80 fluid | Changed at 113,000 km. |
| Oxygen sensors | "Cleaned" — **method unknown**. |
| Intake manifold | Off during the injector work, refitted. **No change.** |
| Battery | Disconnected once; relearn done plus ~300 km driven. |

### Also established

- **Factory airbox and duct**, no oiled aftermarket filter — MAF
  calibration is as Ford intended.
- **Always 95 octane, same station** — fuel supply is constant.
- **No aftermarket tune**, no evidence of prior engine work.
- **Thermostat reaches and holds** normal temperature — the PCM does exit
  warm-up enrichment.
- **Rear differential fluid** changed at some point.
- Oil is **5W-30** against a 5W-20 spec — correct at the next change, but it
  is not the cause: sluggish phasers hurt more under load, and this truck is
  flawless under load.

### Concern: the oxygen sensors — separate from the shake

Heated O2 sensors are not serviceable by cleaning. Solvent attacks the
platinum layer and the ceramic element, and mechanical cleaning damages the
shroud's diffusion slots. Either is permanent.

**But they are not the cause of this shake.** The symptom is identical cold,
where the PCM runs open loop and ignores them entirely.

**Still check upstream HO2S switching rate at 2,500 rpm.** A healthy sensor
crosses 0.1↔0.9 V several times per second. Slow, lazy or parked mid-range
means replace. Treat as a separate, owed repair.

---

## Elimination record

Everything below is ruled out, with the evidence that ruled it out.

| Ruled out | Evidence |
|---|---|
| Fuel delivery — pump, filter, pressure | Pulls great under load; these fail under load first |
| Compression, valves, cam timing, phasers *stuck in position* | Same — all worsen under load |
| Ignition — plugs, coils, boots | Plugs changed nothing; ignition faults bite under load |
| Mounts, damper, flexplate, driveline, exhaust contact | Reproduces in Park; D and R identical; nothing mechanical moves a tachometer needle |
| O2 sensors as *root cause* | Symptom identical cold, in open loop |
| MAF / metering error | Factory airbox and duct, no oiled filter |
| Fuel quality or octane | Always 95, same station; symptom utterly constant |
| Aftermarket PCM tune | Never tuned; no evidence of prior engine work |
| Unlearned adaptive memory | Relearn done, plus 300 km |
| Intake manifold gasket disturbed in the injector job | Manifold off and refitted with **zero** change |
| **Throttle body carbon** | **Properly removed, hand-cleaned, no change** |
| **Injectors** | **Removed, cleaned and flow-tested** |
| Thermostat / warm-up enrichment | Reaches and holds temperature |
| Coolant intrusion / internal water pump | Level steady, no loss |
| Idle air control / low idle speed | Idle normal at 650–750; no change with A/C load |

---

## Open suspects, ranked

Only if the rpm-movement test shows a genuine fault. Note what they have in
common: **every survivor is a vacuum- or charge-control component that has
never been touched.**

| # | Suspect | Why it fits | Test |
|---|---|---|---|
| 1 | **EVAP purge valve stuck partly open** | Never touched. Reported as a very common failure on the 2009–2014 F-150. Stuck open = a constant unmetered air and vapour leak, rough idle that shakes when stopped, worst at a standstill, **frequently no code**. Part is cheap. | Pinch its hose to the manifold at idle. Or hand-vacuum-pump the inlet with the connector unplugged — it must hold. |
| 2 | **PCV valve, hose, elbow** | Never inspected. 12 years of Jeddah heat hardens the rubber; cracks open hot and close cold. Same leak signature. | Flex it **hot and running**. Pinch test at idle. Oil filler cap test. |
| 3 | **VCT solenoid / cam phaser** | This engine's *internal EGR* is done by cam overlap — see the note below. A phaser or solenoid misbehaving specifically at idle, where oil pressure and phaser authority are lowest, produces dilution that clears as load and pressure rise. | Commanded vs actual cam position at idle. **Swap solenoids bank to bank** — if the fault follows, it is the solenoid. Inspect solenoid screens. |
| 4 | **Vacuum leak elsewhere** | Brake booster hose, manifold gaskets, fittings. Not excluded, but the manifold refit changed nothing. | Smoke test — **only after trims justify it**. |

### Why suspect 3 was previously eliminated, and why it is back

An earlier revision ruled out cam phasers on the grounds that they worsen
under load. That argument conflated two different failure modes:

- **Phaser stuck in a fixed wrong position** — costs power under load. The
  truck pulling great genuinely rules this out.
- **Phaser or VCT solenoid misbehaving at idle** — oil pressure is lowest
  at idle, so control authority is weakest exactly there. Cam position
  wanders, rpm wanders with it, and it cleans up as load and oil pressure
  rise. The elimination never applied to this mode.

Two things still argue against it: VCT faults normally set **P0010–P0024**
and there have been no codes, and the classic description is
rough-cold-smooths-warm, while this is identical cold and hot.

### There is no external EGR valve on this engine

The 3.7 Ti-VCT uses twin independent cam phasing to create **internal EGR**
through controlled valve overlap; retarding the exhaust cam does the job the
EGR valve used to do, so the valve was deleted. RockAuto's catalogue is
consistent with this — the 2014 F-150 **3.5L EcoBoost** lists an EGR valve
control solenoid, the **3.7L** does not.

Earlier revisions of this document listed "EGR stuck or leaking" as a ranked
suspect and "EGR actual position at idle" as required scan data. **Both were
wrong** — there is no such valve and likely no such PID. The dilution
mechanism survives; it lives in the phasers. [VERIFY against the service
manual]

---

## Data still needed

1. **RPM movement at warm idle, logged** — the threshold question. See
   [Is this a fault?](#is-this-a-fault).
2. **Codes — permanent (Mode $0A) especially.** The battery disconnect
   wiped stored and pending; permanent codes are the only surviving history.
3. **LTFT bank 1 and bank 2** at warm idle in P, in D on the brake, and at
   2,500 rpm no load.
4. **Misfire counters per cylinder.**
5. **VCT commanded vs actual** at idle, both banks.
6. **HO2S upstream switching rate** — separate, owed repair.

### How to read the results

| Reading | Healthy | Fault indication |
|---|---|---|
| RPM at steady warm idle | ±25–50 rpm wander | ±100 rpm or rhythmic hunting |
| LTFT B1 / B2, warm idle | within ±5%, ±10% tolerable | Double-digit positive that **shrinks** at 2,500 rpm → unmetered air. The key reading. |
| LTFT split between banks | within a few % of each other | One bank high → narrows to three cylinders |
| Misfire counters | 0, or a stray count | One cylinder dominant → that cylinder. Even spread → global cause |
| Rough idle **with normal trims** | — | **Dilution, not mixture** → suspect 3 |
| VCT actual vs commanded | tracks within a few degrees | Lagging, wandering or not following → phaser or solenoid |
| HO2S upstream @ 2,500 rpm | 0.1↔0.9 V, several times/sec | Slow or parked mid-range → sensor damaged |
| ECT warm | ~88–100 °C | Confirmed normal on this truck |

**Trims decide whether to smoke test, not the other way round.** LTFT within
±10% at idle means no leak present is significant enough to explain a shake,
and a smoke test would only surface leaks too small to matter. Any 12-year
old engine shows *some* smoke somewhere.

---

## Test procedures

### 1. EVAP purge valve (free, do first)

The valve is **normally closed** when de-energized. Everything below tests
that. Fuel vapour is involved — no ignition sources.

- **Pinch test.** Warm idle in P. Clamp the hose from the purge valve to the
  intake manifold, watch 20 s. *Idle steadies, shake reduces, rpm may rise
  slightly* → **the valve was leaking.** No change → move on.
- **Vacuum hold, engine off.** Disconnect both hoses, hand vacuum pump on
  the inlet port, connector unplugged. Must **hold**. Bleeds down → stuck
  open.
- **Flow test, running.** Unplug the connector so the PCM cannot command it
  open, pull the canister-side hose, finger over the port. Vacuum pulling →
  passing with no command → stuck open.
- **Scan tool.** Command 0% then 100% duty at idle. Rpm and STFT must react
  when commanded open and be flat when commanded closed.

If any test is positive, **replace rather than clean.**

### 2. PCV valve, hose, elbow (free)

- **Flex it hot and running.** Heat-hardened rubber cracks open when flexed
  and closes cold — a cold visual inspection misses it. Look for glazing,
  crazing, a chalky surface.
- **Pinch test at idle.** Rough idle smooths → air was getting in. Idle
  rises slightly then settles → normal.
- **Oil filler cap.** Lift slowly at idle. Small change that settles →
  normal. Idle drops hard → restricted ventilation. Idle *smooths* →
  crankcase pressure problem.

[VERIFY] Confirm against the parts catalogue whether this engine has a
serviceable PCV valve at all — several Ford engines of this era integrate a
fixed orifice into the valve cover with no replaceable valve.

### 3. Vacuum leak, general

- **Smoke test.** Seal the intake. **Clamp off the PCV and purge lines
  first**, or a leaking valve shows up as "system leaks" and localises
  nothing. Run twice — clamped and unclamped; the difference isolates the
  valves from the manifold. Inspect manifold gaskets, throttle body base,
  every hose and fitting, brake booster hose, dipstick tube.
- **Vacuum gauge, manifold port, warm idle.** Steady 18–22 inHg → healthy at
  this elevation. Steady but low → leak or retarded timing. Needle drifting
  slowly → mixture instability. Rapid regular flicker → valve or guide.
- **Brake booster.** Clamp its hose at idle; a change means booster or check
  valve.

Do not spray flammable cleaner around a hot running engine to hunt leaks.
Smoke does the same job with none of the risk.

### 4. VCT solenoid and phasers

- **Scan data both banks at idle.** Actual tracking commanded smoothly →
  working. Wandering, lagging or hunting → solenoid or phaser.
- **Bank swap.** Swap the two VCT solenoids side to side. Fault moves →
  **the solenoid** (cheap). Fault stays → phaser, chain or oil supply.
- **Solenoid screens.** Pull and inspect for debris or a holed screen.
- **Oil pressure at hot idle**, mechanical gauge. Reported requirement is at
  least **25 psi** for phasers and tensioners. [VERIFY — reported in a TSB
  summary, source document not read]
- **Chain stretch.** Reported TSB method: **VCT_INT_ACT1 ≥ +6° at idle**
  indicates a worn chain; with the cover off, **more than 5 teeth** of
  tensioner extension confirms. [VERIFY — same caveat]

---

## Quick checks — ten minutes, engine off, before anything else

Both physical tests come from the **Mustang 3.7 community**: the same Cyclone
engine as this truck, and a far larger source of engine-specific knowledge
than the F-150 3.7 community. Run `f150diag run quick-wins` to be walked
through them.

| # | Test | Result that finds the fault |
|---|---|---|
| 1 | **PCV valve shake test.** Passenger-side valve cover, roughly halfway forward. Pull and shake. | **No rattle = clogged.** Mustang 3.7 sources name PCV clogging as a known rough-idle cause on this engine. |
| 2 | **Purge valve vacuum hold.** Engine off, connector unplugged, hand pump on the inlet port. | **Bleeds down = stuck open.** Mustang sources say stuck-open is *the* failure mode of Ford's purge valve. |
| 3 | **Calibration check.** `f150diag survey` reads the PCM calibration IDs. | A later calibration existing for this VIN would be a reflash with no parts. |

Neither physical test needs the engine running, so neither carries the stall
risk that makes vacuum work awkward on this engine.

**Expectation, stated honestly:** six competent repairs have already failed,
so a quick win is unlikely. Run these because they cost ten minutes and target
the two components never inspected — and because a clean result eliminates two
of the top three suspects with evidence rather than by assumption.

### Documents worth fetching

- **`MC-10184634-0001`** — an NHTSA bulletin titled *"Vibration/Rough Idle In
  DRIVE Or REVERSE, Lack Of…"*. The title matches this truck's symptom pattern
  closely. Applicability unknown; the document could not be opened from the
  environment where this note was written. Highest-value single thing to fetch.
  `https://static.nhtsa.gov/odi/tsbs/2020/MC-10184634-0001.pdf`

### Ideas considered and rejected

Recorded so they are not re-derived and re-tested at the owner's expense. See
the knowledge base entries prefixed `dismissed-`.

- **Oil change / viscosity** — the reported case was rough-when-cold, cured by
  an oil change. This truck is identical cold and hot, so the mechanism cannot
  be the same. (5W-30 against a 5W-20 spec is still worth correcting.)
- **Carbon cleaning / Seafoam** — the 3.7 is **port** injected, so valve-back
  carbon matters far less than on a direct-injected engine, and the injectors
  here were already flow-tested and the throttle body properly cleaned.
- **Aftermarket tune** — never tuned, no evidence of prior engine work.

---

## Vacuum testing on this engine

**The lines are hard plastic. They cannot be clamped or pinched.** Isolating
one means disconnecting it and plugging the manifold port.

**And it must be done with the engine OFF** — opening a manifold port on a
running engine is a leak large enough to stall it.

Every isolation test therefore runs: engine off, disconnect, plug, restart,
settle 30 s, measure. Because each test involves a restart, the comparison
baseline is taken the same way, so all measurements are made under identical
conditions.

Order: **purge, then booster, then PCV.** Sealing the first two should change
nothing on a healthy engine, so they give a clean signal. PCV is a metered air
path in normal operation, so blocking it shifts the idle even when nothing is
wrong — read the instability, not the rpm number.

Check no plug is left in a port afterwards.

---

## Recommended next actions

0. **Quick wins** — PCV shake test and purge valve vacuum hold. Ten minutes,
   engine off, no scan tool. `f150diag run quick-wins`.
1. **Establish whether there is a fault.** Control-sample another vehicle with
   this engine, and log the rpm movement at warm idle. Free. Note that Ford's
   stated position on a 2011-2014 Mustang 3.7 vibration complaint was that it
   is normal operation of the engine.
2. **Purge valve and PCV pinch tests.** Free, two minutes, no tools, and
   they target the two components never touched in twelve years.
3. **Read permanent codes, fuel trims and misfire counters.**
4. **Smoke test** — only if trims show a leak that matters.
5. **VCT cam position tracking and bank-swap** — if trims are normal but the
   rpm movement is genuinely out of range.
6. **HO2S switching rate** — separate, owed regardless.

**Do not fit another part before steps 1 and 2.** Six repairs have been
bought chasing a symptom nobody has yet established is abnormal, and every
one of them targeted a fault that gets *worse* under load — which this truck
does not have.

---

## Research note

Forum and TSB sources were searched, but this environment's network policy
blocks f150forum, ford-trucks, fordf150.net, edmunds, reddit, RockAuto,
go-parts and static.nhtsa.gov. **Findings attributed to those sources come
from search-engine summaries, not pages actually opened.** Treat them as
second-hand. The purge valve failure-rate claim and the VCT/TSB thresholds
above are both in that category.

---

## Note on this engine

The 3.7L Cyclone uses an **internal, timing-chain-driven water pump.** When
it fails it dumps coolant into the oil pan rather than onto the ground. If
any coolant loss appears with no external leak, check the dipstick for milky
oil or an over-full pan before chasing anything else. **Level is currently
steady.**
