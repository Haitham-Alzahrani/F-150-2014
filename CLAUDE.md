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
ownership, no code in years, normal idle rpm, perfect under load, and
**six competent repairs aimed at six different systems, every one of which
changed nothing.**

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

### Current leads, if the rpm test shows a real fault

1. **EVAP purge valve stuck partly open** — never touched. Documented as a
   very common failure on the 2009–2014 F-150, causes a rough idle that
   shakes when stopped, and frequently sets **no code**. Free to test.
2. **PCV valve, hose and elbow** — never inspected, 12 years of Jeddah heat.
3. **VCT solenoid / cam phaser** — see the EGR note under *Careful*. Weak on
   two counts: no codes (P0010–P0024 expected) and no cold/hot difference.
4. **Vacuum leak elsewhere** — smoke test, but only after trims justify it.

**Eliminated with evidence:** throttle body (properly cleaned, no change) ·
injectors (flow-tested) · MAF and intake (factory) · fuel delivery and fuel
quality · ignition · compression, cam timing and phasers *in their
stuck-in-position mode* (all worsen under load) · mounts and driveline ·
thermostat · coolant intrusion · PCM tune · adaptive memory.

### Blocked on

Scan data: fuel trims (LTFT both banks, idle in P/N vs D vs 2,500 rpm),
per-cylinder misfire counters, VCT commanded vs actual at idle, and codes
(stored, pending **and permanent** — the battery disconnect wiped stored and
pending, so permanent codes are the only surviving history).

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
python -m f150diag.cli --port /dev/ttyUSB0 run triage
python -m f150diag.cli --port /dev/ttyUSB0 run idle-quality
python -m f150diag.cli analyze logs/<file>.csv
python -m f150diag.cli kb list
```

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
