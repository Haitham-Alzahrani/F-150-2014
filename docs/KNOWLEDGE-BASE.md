# The diagnostic knowledge base — two layers and a gate that bites

**Built 2026-09-19, before the vehicle was connected.** `data/diag.db`,
22 tables, seeded from six sources.

```
FORD KNOWLEDGE BASE        definitions + applicability, NEVER narrowed
        |  match on VIN / calibration / module / protocol
        v
VEHICLE CAPABILITY MAP     candidates for THIS truck
        |  discover -> request -> decode -> plausibility -> cross-check
        v
VEHICLE-VERIFIED PROFILE   levels 4-5, the only thing diagnostics may use
```

## What is in it

| | Rows |
|---|---|
| `pid_definitions` | **2,566** |
| `dtc_catalogue` | **2,066** |
| `mode06_catalogue` | **56** |
| `pid_applicability` | 126 |
| `modules` | 6 |
| `test_procedures` | 4 |
| `pid_sources` | 6 |

| Source | Confidence | What it really is |
|---|---|---|
| `python-obd` command tables | high | Legislated SAE J1979. Same on every vehicle. |
| `python-obd` DTC table | medium | **Generic** descriptions — not Ford's wording, no set/clear conditions |
| **mode 06 capture 2026-09-05** | high | **Level 3** — screenshots of the app reading *this* truck |
| `commaai/opendbc` Ford DBC | **low** | **Broadcast CAN signals, NOT diagnostic PIDs** |
| Module addressing | mixed | **Only `7E0` has ever answered in this project** |
| Scan app sensor list | medium | Applicability for this VIN only — no scaling, no byte layout |

## The levels, and why they are enforced in code

```
0 UNKNOWN            1 DOCUMENTED        2 FORD_APPLICATION
3 PROTOCOL_VERIFIED  4 VEHICLE_VERIFIED  5 VEHICLE_VALIDATED
```

A wrong identifier **does not return an error — it returns a plausible number,
and a plausible number condemns a good part.** So the levels are not a comment
field. `promote()` enforces them, and the gates were tested:

| Attempt | Result |
|---|---|
| Assert level 4 at insert | **REFUSED** |
| Promote to 4 with no evidence | **REFUSED** |
| Promote to 4 from a **simulated** response | **REFUSED** |
| Promote to 4 with one real response | allowed |
| Promote to 5 without a cross-check | **REFUSED** |
| Promote to 5 with 3 responses + cross-check | allowed |

**Nothing is at level 4 or 5.** Nothing has been read from the truck through
this tool yet.

**Nothing is ever deleted.** A definition this truck does not answer is marked
`not_supported` *for this vehicle* and stays in the Ford layer — the same
identifier may be right on another 3.7 application.

## What the Ford CAN import is and is not

2,150 signals from `opendbc`. **They are broadcast frames read by sniffing the
bus, not by asking a module a question.** An ELM327 cannot fetch them the way
it fetches a PID. They are reverse-engineered, not Ford-official, and the file
states no model-year applicability — so it is recorded as unknown rather than
guessed. They are in the base because they are Ford knowledge, not because they
are reachable today.

## The rate law is enforced, not described

An ELM327 answers **one request at a time**. Measured on this truck's own data:
one channel sustained **33.3 Hz — a flat 30 ms per request.** That does not
divide:

> **per-channel rate ≈ 33 ÷ N**

`acquisition.plan()` computes it and refuses to flatter a group. Channels named
under `simultaneous_with` are counted too — they consume the same bandwidth,
and not counting them flattered exactly the groups whose purpose is
cross-channel comparison.

| Group | Channels | Per channel | Needs | Verdict |
|---|---|---|---|---|
| `ENGINE_SPEED_FAST` | 1 | 33.3 Hz | 16 | OK |
| `ELECTRICAL` | 2 | 16.7 Hz | 1 | OK |
| `ENGINE_IDLE_CONTEXT` | 14 | 2.4 Hz | 1 | OK |
| **`CYLINDER_BALANCE`** | 7 | **4.8 Hz** | **16** | **UNDER-SAMPLED** |
| **`TRANSMISSION`** | 8 | **4.2 Hz** | **5** | **UNDER-SAMPLED** |

**Counters are not streams.** Mode 06 misfire counters are cumulative — read
once, before and after a change, never polled in a group.

## Reading it

```
python -m f150diag.kb data/diag.db
```

```
python -c "import sys;sys.path.insert(0,'src');from f150diag import acquisition;print(acquisition.report())"
```

## Still missing

* **A Ford-wide source beyond this vehicle.** FORScan's definitions are
  proprietary and unpublished. The next real seed is **your own FORScan
  installation** — its PID list and log headers are Ford-application
  definitions for this platform, and they are licensed to you.
* **No service 0x22 identifier is verified**, so cylinder acceleration, the
  transmission channels and cam phasing remain unreachable by this tool.
* **MS-CAN** — `python-obd` selects protocols `1`–`A`; there is no
  user-defined `B`/`C` where 125 kbps lives. FORScan reaches it; this tool
  does not.
