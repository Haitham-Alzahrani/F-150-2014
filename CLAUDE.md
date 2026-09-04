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

### RPM stability — measured 2026-09, six windows of 10–15 min

Mean 650–660. Raw peak-to-peak 64–81 rpm, but **the raw span overstates it**:
the vertical drops to 621–626 are one sample wide, so they are adapter frame
losses rather than engine events. Excluding those, the body of every trace
sits **638–668 rpm, a band about 30 rpm wide** — normal closed-loop control.

There is a slow cycle of roughly **4–5 minutes** — the PCM tracking cooling
fan cycling, purge cycling and alternator load. **That is not a hunt.** A
hunting idle oscillates over seconds.

**Two corrections this forced:**

1. **No OBD log can resolve this vibration.** At 660 rpm a V6 fires at
   **33 Hz**; these recordings sample at about **0.3 Hz**. Tachometer movement
   and felt vibration are different phenomena and earlier revisions of this
   file wrongly treated them as one symptom.
2. The ±25–50 rpm figure above is for a **120-second** window. Judging a
   10-minute span by it is not like-for-like — slow load drift accumulates.

**Fourth independent line of evidence that there is no engine fault**, after
the load curve, the absent powertrain codes, and the live fuel data.

### The remaining test is not electronic

Measure the vibration, not a proxy. Phone accelerometer or spectrum app, flat
on the seat, warm idle. At ~660 rpm:

- **~33 Hz (3rd order)** → the V6 firing pulse felt through a bare regular-cab
  floor. Normal. Nothing to fix.
- **~11 Hz (1st order)** → rotational imbalance: damper, pulley, flexplate.

### Still unmeasured

1. **Permanent codes (Mode 0A)** — the only code history a clear cannot destroy.
2. LTFT after several hundred km, since the current 0 % is probably un-relearned.
3. VCT commanded vs actual, via the FORScan handoff, if anything still points there.

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

**Specs and technical data: [`docs/f150-specs.md`](docs/f150-specs.md)** —
identification, engine, transmission, capacities, fluids, OBD-II buses,
intervals, part numbers. Figures are marked [VIN] / [SPEC] / [VERIFY];
never act on a [VERIFY] torque or capacity without checking the manual.

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
