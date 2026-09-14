# THE COMPLETE SENSOR LIST FOR THIS TRUCK — built batch by batch

**Purpose: read every channel the owner's app offers on this VIN, once, properly,
and stop guessing what is reachable.** This project has repeatedly written that a
measurement "requires FORScan" or "the OBD port cannot see it" without ever
having read the list. At least one of those statements was wrong — per-cylinder
contribution is in the app.

**Status: COLLECTING. Do not draw conclusions until every batch is in.**

| Batch | Screenshots | Received | Covers |
|---|---|---|---|
| 01 | 12 | 2026-09-14 | Mixed — live data pages and part of the sensor list |
| 02 | — | awaiting | — |

**Rules for this file**
* Every channel is recorded **exactly as the sensor list spells it**, including
  the `[PCM]` prefix, capitalisation and spacing. That label is what the owner
  searches for on the phone.
* A value seen in a screenshot is recorded beside it **only as evidence the
  channel answers** — never as a measurement. Conditions were not controlled and
  the phone clock was not always legible.
* `n/a` means the truck answered "not supported". That is different from the
  channel being absent from the list.
* Nothing here is a finding.

---

## BATCH 01 — 12 screenshots, 2026-09-14

Images: `data/sensor-list-2026-09-14/batch-01/01.jpg` to `12.jpg`

### The `[PCM]` block — none of these appear in any log or in `docs/scanner-pids.md`

| Channel | Seen reading |
|---|---|
| `[PCM] Cylinder 1 Acceleration Value` | −0.03 / −0.02 |
| `[PCM] Cylinder 2 Acceleration Value` | −0.02 / 0 |
| `[PCM] Cylinder 3 Acceleration Value` | −0.03 / 0 |
| `[PCM] Cylinder 4 Acceleration Value` | **−0.08** |
| `[PCM] Cylinder 5 Acceleration Value` | −0.02 |
| `[PCM] Cylinder 6 Acceleration Value` | 0 |
| `[PCM] Desired Electronic Throttle Control` | 15.31° / 19.55° |
| `[PCM] Actual Electronic Throttle Control` | 15.25° / 19.62° |
| `[PCM] Knock Sensor 1` | 323 / 293 |
| `[PCM] Knock Sensor 2` | 336 |
| `[PCM] Currently Detected Engine Misfire` | 0 |
| `[PCM] A/C Pressure` | **1282 kPa — works; the unprefixed channel is dead** |
| `[PCM] Cylinder head temperature` | 83 °C |
| `[PCM] ATF Temperature` | 62.81 °C |
| `[PCM] Battery voltage` | 12.7 V |
| `[PCM] Fuel level` | 86.27 % |
| `[PCM] Actual Turbine Shaft Speed` | 1458 rpm |
| `[PCM] Actual Output Shaft Speed` | 2117.75 rpm |
| `[PCM] Actual Torque Converter Slip` | 12 rpm |
| `[PCM] Desired Torque Converter Slip` | 10.25 rpm |
| `[PCM] Commanded Gear Ratio` | present |
| `[PCM] Commanded Gear` | present |
| `[PCM] Measured Gear Ratio` | present |

### Standard channels seen in this batch

| Channel | Seen reading |
|---|---|
| `Long term fuel % trim - Bank 1` | −2.34 % |
| `Long term fuel % trim - Bank 2` | −3.13 % |
| `Oxygen sensor 2 Bank 1 Short term fuel trim` | **n/a %** — not supported |
| `Oxygen sensor 2 Bank 2 Short term fuel trim` | **n/a %** — not supported |
| `Ethanol fuel percent` | 22.35 % |
| `Barometric pressure` | 98 kPa |
| `Control module voltage` | 13.38 V |
| `Timing advance` | 49.5° at 1343 rpm, 73 km/h |
| `Commanded evaporative purge` | 0 % |
| `Run time since engine start` | 0:00:11:31 |
| `Distance traveled since codes cleared` | 364 km |
| `# warm-ups since codes cleared` | 7 |

### Absent from this batch — confirm by searching the list

* `Long term secondary oxygen sensor trim Bank 1`
* `Long term secondary oxygen sensor trim Bank 2`

### Searches still to run in the app's filter box

`secondary` · `cylinder` · `knock` · `throttle` · `misfire` · `oxygen` · `fuel`
