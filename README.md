# 2014 Ford F-150 3.7L — Diagnostics

A working diagnostic record for one truck, and a read-only OBD-II tool built
to answer the question it poses.

**2014 Ford F-150 XL Regular Cab · 3.7L V6 Ti-VCT · 6R80 automatic · 4x2**
VIN `1FTMF1EM1EFC80632` · 131,000 km · Jeddah, Saudi Arabia

---

## The open question

A **small** vibration felt in the cab at idle, with visible movement on the
tachometer. Felt, not heard — from under the hood a trained ear cannot tell
the engine has a problem. Normal idle rpm. No code, ever. Present since
purchase.

**The first question is not which fault it is. It is whether there is one.**

Symptom strength tracks engine load, inversely:

| Condition | Manifold vacuum | Shake |
|---|---|---|
| P / N at standstill | Highest | **Worst** |
| D / R at standstill | Slightly lower | **Less** |
| Driving under load | Lowest | **Absent — pulls great** |

Rpm is not the variable; load is. If a fault exists, it is one whose effect
scales with manifold vacuum and disappears when the throttle opens — which
rules out the entire worsens-under-load family: fuel delivery, compression,
cam timing, ignition.

Against a fault existing at all: the truck has never been smooth in this
owner's hands, has never set a code, idles at a normal speed, is flawless
under load, and has had **six competent repairs across six different systems,
every one of which changed nothing.** It is also a base regular cab — little
sound deadening, cab close to the engine — with a 60° V6, which is not
inherently balanced the way an inline-six or a cross-plane V8 is.

Two free tests settle it, and neither needs a scan tool:

1. **Idle another vehicle with this engine alongside** and compare by hand
   and by seat. A control sample answers in two minutes what six repairs have
   not.
2. **Log the rpm for 120 s at warm idle.** ±25–50 rpm of gentle wander is
   normal closed-loop idle control. **±100 rpm, or any rhythmic hunt, is a
   real fault.** That threshold is the whole question.

### If it is a fault

Every surviving suspect is a vacuum- or charge-control component that has
never been touched in twelve years:

1. **EVAP purge valve stuck open** — Mustang 3.7 sources say stuck-open is
   *the* failure mode of Ford's purge valve, and it frequently sets no code
2. **PCV valve, hose and elbow** — never inspected
3. **VCT solenoid / cam phaser** — this engine has **no external EGR valve**;
   internal EGR is made by cam overlap, so the dilution path lives here

Full reasoning, the elimination record with evidence, and test procedures:
[`docs/f150-diagnosis.md`](docs/f150-diagnosis.md).

---

## The tool

`src/f150diag/` — read-only OBD-II diagnostics that walk adaptive protocols,
record what they measure, and reason from the measurements.

```
python -m f150diag.cli selftest
```

No vehicle needed. Validates decoders, DTC decoding, the condition evaluator,
periodicity detection, every protocol's step graph, and the knowledge base.

| Protocol | Does |
|---|---|
| `quick-wins` | Ten minutes, engine off, no scan tool — PCV shake test, purge valve vacuum hold, calibration check |
| `triage` | Five-minute opener: what the vehicle is, what it reports, whether the idle is abnormal |
| `idle-quality` | The full investigation — fault-or-not, load sweep, trim comparison, vacuum line isolation |
| `vct-check` | Cam timing, via a FORScan handoff |
| `o2-health` | Upstream sensor switching rate |

What it does that a live-data screen cannot:

- **Tells scatter from a hunt.** Idle control is a closed loop, so rpm always
  moves. Random scatter and a real oscillation look identical to the eye and
  completely different to an autocorrelation — gated on amplitude, since a
  2 rpm ripple is correct behaviour, not a fault.
- **Tells cause from effect.** With rpm and fuel trim on one timebase,
  cross-correlation says which moves first. Trim leading means fuel control is
  driving the instability; rpm leading means it is only reacting — which is
  dilution or mechanical, and points somewhere else entirely.

### Design rules

- **Read-only.** Service 04 (clear codes) is deliberately absent — clearing
  destroys the freeze frame and the permanent-code history a diagnosis
  depends on. No blind writes to any module: a bricked PCM is a dead truck.
- **`DID_REGISTRY` ships empty.** Ford does not publish its enhanced data
  identifiers, and a wrong Mode 22 address returns a plausible number rather
  than an error — that number then condemns a good part.
- **Every knowledge-base entry carries provenance and a test.** `verified`
  means somebody opened the source, not that it appeared in a search summary.
  An issue with no way to check it is folklore.

### FORScan is driven, not shared

A serial port is opened by one process at a time, so the two never hold the
adapter together. A `handoff` step releases it, launches FORScan, watches for
its CSV export and imports it automatically — the operator never relays a
filename. See [`docs/FORSCAN.md`](docs/FORSCAN.md).

---

## Contents

| File | What it is |
|---|---|
| [`CLAUDE.md`](CLAUDE.md) | Auto-loaded context, so a session opened here already knows the truck |
| [`docs/f150-diagnosis.md`](docs/f150-diagnosis.md) | The diagnostic log — symptom, load relationship, elimination record with evidence, ranked suspects, test procedures |
| [`docs/f150-specs.md`](docs/f150-specs.md) | Vehicle reference — identification, engine, transmission, capacities, fluids, bus layout, intervals, part numbers. Every figure marked verified, spec, or verify-before-use |
| [`docs/TOOL.md`](docs/TOOL.md) | Tool architecture, how to write a protocol, how to add a knowledge entry |
| [`docs/LOCAL-SETUP.md`](docs/LOCAL-SETUP.md) | Running it at the truck with Claude Code |
| [`docs/FORSCAN.md`](docs/FORSCAN.md) | Working alongside FORScan, and the handoff mechanism |
| [`docs/ENHANCED-PIDS.md`](docs/ENHANCED-PIDS.md) | Why the DID registry is empty and how to fill it honestly |
| [`docs/android-claude-code-setup.md`](docs/android-claude-code-setup.md) | Claude Code on Android via Termux, to work this repo from the phone |
| `protocols/*.yaml` | Diagnostic protocols — data, not code |
| `knowledge/issues/*.yaml` | The issue base, with provenance on every claim |

---

## Working this at the truck

```
git clone https://github.com/Haitham-Alzahrani/F-150-2014.git
```

```
cd F-150-2014
```

```
python3 -m venv .venv
```

```
.venv/bin/pip install -r requirements.txt
```

```
claude
```

Starting `claude` inside this folder loads `CLAUDE.md` automatically, so the
session already knows the truck, the symptom, what has been eliminated and on
what evidence, and what is still unmeasured.

From an Android phone, `proot-distro login debian` first — see
[`docs/android-claude-code-setup.md`](docs/android-claude-code-setup.md).

---

## A note on sources

Findings drawn from forums and bulletins were gathered through search
summaries, in an environment whose network policy blocked every source domain.
**None of those pages was opened.** They are marked `verified: false` with the
specific claim to confirm recorded against each one:

```
python -m f150diag.cli kb verify
```

The only claims marked verified are those measured on this vehicle. Evidence
about this truck outranks any document about trucks in general — and a claim
nobody has checked should say so.
