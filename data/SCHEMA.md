# Extraction schema — 2014 F-150 3.7 idle vibration dataset

You are extracting a scattered diagnostic conversation into structured rows so it
can be analysed properly. **Completeness matters more than tidiness. Do not skip a
reading because it seems unimportant, redundant, or wrong — record it and mark it.**

## Ground rules

1. **Every numeric reading gets a row.** Including repeats, including ones later
   withdrawn, including ones from superseded sessions.
2. **Never invent a value.** If a field is unknown write `unknown`. Never guess an
   rpm, a temperature, or a condition that was not stated.
3. **Preserve the exact channel name** as the scan app shows it. Do not normalise
   `LTFT - B1` into something else; put the graph header in one column and the
   full list label in another when both are known, else `unknown`.
4. **The phone clock is the authoritative timestamp.** The graph clock is a
   separate MM:SS axis. Record both when present.
5. **Mark inadmissible readings.** The scan app's Min / Avg / Max fields are
   session-cumulative, not per-window. Readings taken from those fields are
   `reading_method=app_minmaxavg` and `admissible=no`. Readings taken by reading
   the plotted curve are `reading_method=curve_read` and `admissible=yes`.
6. **CSV format:** comma-separated, UTF-8, quote any field containing a comma,
   header row exactly as specified. No blank rows.
7. **Cite your source.** `source` = the message number in square brackets from the
   transcript, e.g. `[147]`. If a row comes from several, list them: `[147];[149]`.

## Vocabulary — use these exact tokens

- `gear`: `P` `N` `D` `R` `driving` `unknown` `n/a`
- `load`: `idle` `2000rpm` `rpm_sweep` `cruise` `WOT` `overrun` `coast` `shift`
  `key_on_engine_off` `unknown` `n/a`
- `thermal`: `cold` `warming` `warm` `unknown` — plus `coolant_c` as a number when stated
- `ac`: `on` `off` `unknown`
- `capture_type`: `graph_paired` `value_read` `mode06` `monitor_status` `dtc`
  `physical` `subjective` `calculation`
- `admissible`: `yes` `no` `unknown`
- `epoch`: which repair era the reading belongs to —
  `pre_purge_valve` `post_purge_valve_pre_drive` `post_drive` `unknown`
  (The purge valve was replaced and the battery/KAM was wiped at the same time.
  The drive that relearned the adaptives came after that.)

---

## FILE 1 — `readings.csv`

Every numeric or categorical measurement taken from the vehicle.

```
reading_id,session_date,phone_clock,graph_clock,capture_type,channel_graph_header,channel_list_label,paired_with,gear,load,thermal,coolant_c,ac,rpm_at_capture,value,value_min,value_max,span,units,reading_method,admissible,epoch,notes,source
```

- `reading_id`: `PART<n>-0001` incrementing, where `<n>` is your assigned part number.
- `value`: the single figure, or the representative/baseline figure of a curve.
- `value_min` / `value_max` / `span`: for graph windows. `span` = max − min.
- `notes`: shape of the curve, period, anything qualitative. Keep it factual.

## FILE 2 — `sessions.csv`

One row per distinct capture session (a continuous run of screenshots at one
condition).

```
session_id,session_date,phone_clock_start,phone_clock_end,graph_clock_start,graph_clock_end,gear,load,thermal,coolant_c,engine_run_time,channels_captured,n_screenshots,epoch,purpose,summary,source
```

## FILE 3 — `subjective.csv`

**The owner's own reports.** These are data and they have twice overturned
conclusions drawn from graphs. Record every statement about what the vehicle does
or feels like, including corrections he made to the assistant.

```
obs_id,session_date,phone_clock,gear,load,thermal,observation,category,epoch,source
```

- `category`: `symptom` `symptom_change` `method_correction` `vehicle_fact`
  `history` `constraint`

## FILE 4 — `timeline.csv`

Every event that changed the vehicle or the data: repairs, part replacements,
battery disconnection / KAM wipe, code clears, drives, monitor completions.

```
event_id,event_date,phone_clock,event,category,effect_on_data,source
```

- `category`: `repair` `reset` `drive` `measurement_milestone` `prior_history`

## FILE 5 — `findings.csv`

Every conclusion drawn, **including the ones later withdrawn.** The withdrawal
history is itself important data.

```
finding_id,finding_date,statement,status,evidence,superseded_by,reason_withdrawn,source
```

- `status`: `standing` `withdrawn` `superseded` `open_question` `verify_needed`

## FILE 6 — `eliminations.csv`

Every system, component or hypothesis ruled in or out.

```
elim_id,item,verdict,evidence,confidence,date,epoch,source
```

- `verdict`: `eliminated` `cleared` `suspect` `confirmed_fault` `reopened` `untested`
- `confidence`: `measured` `inferred` `reported` `assumed`

---

## What good output looks like

- A reading captured as a paired graph produces **one row per channel**, both
  sharing the same `graph_clock` and cross-referenced in `paired_with`.
- A value-read screen listing 20 channels produces **20 rows**.
- A Mode 06 screen produces one row per Test ID, with `value_min`/`value_max` set
  to the test's own limits and `notes` carrying the PASSED/FAILED result.
- If the assistant later said a reading was misread, keep the original row AND add
  the correction in `notes`, and record the withdrawal in `findings.csv`.
