# f150diag — how the tool works and how to extend it

A read-only OBD-II diagnostic tool that walks adaptive test protocols,
records what it measures, and reasons from the measurements rather than from
a fixed checklist.

```
f150diag ports                     what serial ports exist
f150diag --port /dev/ttyUSB0 survey    what the vehicle supports
f150diag --port /dev/ttyUSB0 dtc       stored, pending and permanent codes
f150diag --port /dev/ttyUSB0 live --pids idle --seconds 120
f150diag analyze logs/<file>.csv       statistics and causality on a log
f150diag forscan <export>.csv          import a FORScan CSV and analyse it
f150diag run triage --port /dev/ttyUSB0
f150diag run idle-quality --port /dev/ttyUSB0
f150diag run <protocol> --dry-run      rehearse the prompts, no adapter
f150diag kb list | show <id> | search <term> | validate | verify
f150diag selftest                      everything checkable with no vehicle
```

---

## Design rules

**Read-only.** Services 01, 03, 06, 07, 09, 0A and 22 are all reads. Service
04 (clear codes) is deliberately absent: clearing destroys the freeze frame
and the permanent-code history that a diagnosis depends on, and it is the
single most common way a useful fault history gets thrown away.

**No blind writes.** The Mode 22 framework reads identifiers. Writing to a
module can brick a PCM, and a bricked PCM is a dead truck. Any write
capability gets added only when we know exactly what it does — not to protect
the operator, but to protect the vehicle.

**Provenance is not decoration.** Every knowledge-base entry states where it
came from and whether anybody actually opened the source. Ford does not
publish everything, and the community fills real gaps — but a forum summary
and a service manual page are different kinds of evidence and the tool never
silently promotes one to the other.

**Measurements over assumptions.** The first request of any session asks the
vehicle what it supports. That is how the tool establishes, for instance,
that this engine has no external EGR — the vehicle says so, rather than a
document claiming it.

---

## Layout

| Path | What lives there |
|---|---|
| `src/f150diag/transport.py` | ELM327 serial conversation, reply cleaning |
| `src/f150diag/pids.py` | Mode 01 parameter registry and PID groups |
| `src/f150diag/services.py` | Services 01/03/06/07/09/0A/22, DTC decoding |
| `src/f150diag/recorder.py` | Sampling to CSV and JSON Lines |
| `src/f150diag/analysis.py` | Statistics, periodicity, causality, thresholds |
| `src/f150diag/runner.py` | Protocol graph execution, condition evaluation |
| `src/f150diag/forscan.py` | FORScan CSV import and column mapping |
| `src/f150diag/knowledge.py` | Issue base with provenance |
| `src/f150diag/cli.py` | Commands |
| `protocols/*.yaml` | Diagnostic protocols (data, not code) |
| `knowledge/issues/*.yaml` | The issue base (data, not code) |
| `logs/` | Every measurement, written as it happens |

---

## The two analyses that justify logging

A live-data screen shows you numbers. A log lets you ask two questions no
screen can answer.

**1. Scatter or a hunt?** Idle control is a closed loop, so rpm always moves
a little. Random scatter and a genuine oscillation look identical to the eye
and completely different to an autocorrelation: scatter decorrelates
immediately, a hunt returns to the same phase over and over.

Amplitude gates the result (`RPM_HUNT_MIN_P2P`, 30 rpm). A perfectly regular
two-rpm ripple is textbook correct behaviour; without the gate the detector
would report every healthy engine as hunting.

**2. Cause or effect?** With rpm and short-term fuel trim on one timebase,
cross-correlation says which moves first.

- *Trim leads rpm* → fuel control is driving the instability.
- *Rpm leads trim* → something else disturbs the engine and fuel control is
  only reacting. That is dilution or mechanical, and it points somewhere
  entirely different.

---

## Writing a protocol

Protocols are YAML graphs in `protocols/`. Steps:

| Type | Does |
|---|---|
| `prompt` | Ask the operator to do something physical; optionally capture an answer with `ask:` and `options:` |
| `measure` | Poll PIDs for `seconds`; metrics enter the context |
| `service` | Run a read-only service: `survey`, `dtcs`, `mode06` |
| `branch` | Evaluate `checks` in order, take the first that matches |
| `finding` | Record a conclusion |
| `end` | Stop |

Conditions are expressions over measured metrics:

```yaml
- id: trim_branch
  type: branch
  checks:
    - when: idle_park.ltft_mean > 10 and rpm_2500.ltft_mean < idle_park.ltft_mean - 5
      finding: unmetered-air
      summary: "Trim high at idle and falling at 2500 rpm — an unmetered air leak."
      next: leak_purge
    - finding: dilution-or-mechanical
      next: leak_purge
```

Each `measure` publishes `<channel>_mean`, `_sd`, `_p2p`, `_min`, `_max`, plus
`rpm_periodic`, `rpm_period_s`, `ltft_mean`, `ltft_split`, `stft_leads_rpm`
and the O2 switching metrics. Every metric is also reachable as
`<label>.<metric>`, which is what lets a branch compare idle against 2500 rpm.

**Use underscores in measurement labels.** `idle_park.ltft_mean` parses as an
attribute; `idle-park.ltft_mean` parses as a subtraction and will not work.

Conditions are evaluated by a restricted AST walker, not `eval` — arithmetic,
comparison and boolean logic over known names only. Protocols are data files
edited during a session, and a data file must never be able to execute code.

`f150diag selftest` validates every protocol's step graph, so a typo in a
`next:` is caught at the desk rather than at the truck.

---

## Adding a knowledge-base entry

```yaml
- id: some-failure
  title: Short human name
  summary: What actually happens, mechanically.
  systems: [intake]
  symptoms: [...]
  codes: [P0171]
  load_signature: worst-at-idle    # worst-at-idle | worse-under-load | rpm-linked | none
  temperature: independent          # cold-only | hot-only | independent | unknown
  sets_code: sometimes              # always | sometimes | rarely | never
  tests:
    - "How to confirm it, concretely"
  fix: What repairs it.
  provenance:
    - source: community             # ford-official | ford-tsb | community | measured | inferred | unverified
      confidence: medium
      verified: false               # true ONLY if somebody opened the source
      note: Where this came from and how sure we are.
      check: What specifically to confirm when someone can reach it.
      url: https://...
```

`check` is what makes the base self-correcting. An unverified claim without
one is a dead end; with one it is a task. `f150diag kb verify` prints every
claim still resting on an unopened source, with its URL and what to confirm —
work the list wherever the network allows it, then set `verified: true` and
replace `note` with what was actually read.

`source: measured` with `verified: true` means the claim came from this
vehicle. That is the strongest evidence in the base — better than any
document, because it is about this truck rather than trucks in general — and
it is the grade to use when a test on the vehicle eliminates a suspect.

`load_signature` is the field that earns its keep. It is the strongest
discriminator available for a fault that sets no code, and `kb.by_signature()`
selects candidates on mechanism rather than on a code that never appeared.

Validation is enforced: an entry with no provenance, or with no test, fails
`f150diag kb validate` and `selftest`. An issue with no way to check it is
folklore.

---

## Known limits

**Ford enhanced parameters are not implemented.** Cam position commanded
versus actual, per-cylinder misfire counters as Ford reports them, and the
rest of what FORScan reads live behind manufacturer-specific Mode 22 data
identifiers. `DID_REGISTRY` in `services.py` is empty on purpose — guessed
addresses presented as facts are worse than no data. Populate it from
verified sources and mark provenance honestly. See `docs/ENHANCED-PIDS.md`.

**No bidirectional control.** Commanding an actuator or running a
manufacturer routine needs write access this tool does not have.

**FORScan cannot be run concurrently.** A serial port is exclusive, so the
two tools take turns on the adapter and meet in the filesystem — see
`docs/FORSCAN.md`. Importing a FORScan export gives us its *measurements*,
never its data identifiers.

**Mode 06 unit scaling is not decoded.** Values are reported raw against
their raw limits, which is enough to see pass/fail and margin. The UAS
scaling table is not implemented because a wrong scale factor produces a
confident wrong number.
