# Prepared analysis products

Built from the four Car Scanner logs in `../carscanner/`. Regenerate with
`python3 data/windows_by_temp.py` and `python3 data/analyze_carscanner.py`.

| File | Rows | What it is |
|---|---|---|
| `idle_windows.csv` | 835 | Every 10-second standstill-idle window across all four logs, with peak-to-peak span, standard deviation, coolant temperature where available, a gear proxy, and the night's condition annotations joined on by clock time |
| `night_events.csv` | 14 | The night's timeline as established from the screenshots — what was being tested in each stretch, and what the screenshots concluded |
| `../../docs/carscanner-timing-analysis.txt` | — | Output of the phase analysis: what leads what |

## idle_windows.csv columns

`log` · `gear_proxy` · `t_start_s` · `clock` · `rpm_mean` · `rpm_span` ·
`rpm_sd` · `n_samples` · `ect_c` · `ect_age_s` · `speed_kmh` · `event_id` ·
`condition` · `being_tested` · `epoch`

**`gear_proxy`** is inferred from mean rpm, not read from a gear PID: Ford
commands a lower idle in gear, so ~550 is D/R and ~650 is P/N at a standstill.
Windows between 600 and 620 are marked `ambiguous`. The distinction matters
because the converter damps the same disturbance in gear, so mixing the two
populations makes a gear effect look like something else.

**`ect_c`** is held forward from the last real reading, up to 300 seconds, and
`ect_age_s` says how stale it is. Coolant moves over minutes so a short hold is
defensible; engine speed is never treated this way. **Only 198 of 835 windows
carry a coolant reading at all**, and 189 of those come from one log — any
conclusion about temperature rests on a single session.

## What these logs do NOT contain

The logs hold live PID data only. Everything below exists solely in the
screenshot record and cannot be recovered from any log:

* **Mode 06 on-board test results** — per-cylinder misfire counts, catalyst
  monitor, oxygen sensor response times, VVT monitor. A separate OBD service that
  Car Scanner does not record.
* **Diagnostic trouble codes** and readiness-monitor status.
* **Anything observed by eye** — the dash tachometer needle, the malfunction
  indicator lamp, tyre pressure, oil viscosity in the sump, coolant level.
* **Derived figures** computed during the investigation — order frequencies,
  graph-axis width, adapter response time.

Live channels are the other way round: the logs carry them far more completely
than the screenshots ever did, at ~17 Hz continuously rather than as a handful of
15-second windows.

## Screenshot readings confirmed against the raw log

Spot-checks of the trim findings, which the whole vacuum-leak case rested on:

| Screenshot claim | Raw log |
|---|---|
| 01:13 — LTFT B2 flat at 2.34 % | 2.34 on **1143 of 1143** samples |
| 01:18–01:20 — LTFT B2 steps 2.34 → 0 → 2.34 | values present: 2.34 (3480), 0.00 (366), 0.78 (14) |
| 01:30–01:32 — LTFT B1 +3.13 %, B2 +2.34 % | B1 3.12 on **2594 of 2594**; B2 2.34 on **2595 of 2595** |

The load-cell slope and the bank symmetry are confirmed sample by sample.
