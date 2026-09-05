# Data dictionary

Ten tables. The CSVs are the source of truth and stay human-readable;
[`f150.db`](f150.db) is the same content in SQLite with numeric types and
indexes, rebuilt by `python3 data/build_db.py`.

| File | Rows | What it is |
|---|---|---|
| `analysis_ready.csv` | 324 | **Start here.** Readings plus numeric types, timestamps, session and epoch |
| `readings.csv` | 324 | Every measurement with the condition it was taken under |
| `findings.csv` | 163 | Every conclusion, including the 19 withdrawn ones |
| `subjective.csv` | 139 | The owner's own reports |
| `eliminations.csv` | 102 | Every system ruled in or out |
| `timeline.csv` | 64 | Repairs, resets, drives |
| `mode06.csv` | 56 | On-board monitor tests with limits |
| `sessions.csv` | 37 | Capture sessions as reconstructed from the conversation |
| `sessions_from_exif.csv` | 23 | Capture sessions rebuilt from image timestamps |
| `screenshots_manifest.csv` | 277 | One row per screenshot |

---

## `analysis_ready` — the joined table

Everything in `readings.csv`, plus:

| Column | Meaning |
|---|---|
| `channel` | The scan-app channel, graph header preferred over list label |
| `value_num` `min_num` `max_num` `span_num` | Floats. **Null where the field was not a bare number** — never a guess |
| `rpm_num` `coolant_num` | Same, for the condition columns |
| `is_admissible` | 1 or 0. **0 means recorded but not usable as a measurement** |
| `msg` | Conversation message, looks up in `conversation/transcript.txt` |
| `captured_at` | Wall clock from the source image's EXIF. Empty if no image |
| `minutes_from_start` | Minutes since the first capture of the night |
| `exif_session` | `EX01`–`EX23`, from `sessions_from_exif.csv` |
| `epoch_by_time` | Repair epoch derived from the clock, independent of the extraction |

**232 of 324 readings carry a wall-clock time.** The remainder come from messages
with no screenshot — values quoted in prose, or the owner's own reports.

## The columns that decide whether a number can be used

### `is_admissible`

`no` where `reading_method` is `app_minmaxavg`: the scan app's Min/Avg/Max
fields accumulate over the whole session, not the window on screen. Quoting them
as per-window values produced two withdrawn conclusions before it was
understood. They are kept because they were on screen.

`unknown` where the source did not say which it was.

### `reading_method`

| | |
|---|---|
| `curve_read` | Read off the plotted trace. The admissible graph source |
| `app_minmaxavg` | The cumulative fields. **Not admissible** |
| `value_read` | A numeric list screen |
| `menu` | Mode 06, monitor status, DTC menus |
| `owner_report` | The owner's own answer — a distinct grade of evidence |
| `inferred` | Derived by the assistant, not read from the vehicle. **Not admissible** |

### `epoch` and `epoch_by_time`

The purge valve was replaced and the adaptive memory wiped **between 01:32:39
and 03:11:06 on 5 September** — a 1 h 38 m gap visible in the image timestamps.
Readings either side are not comparable: the wipe erased every learned value.

`epoch` is what the extraction assigned. `epoch_by_time` is derived from the
image clock. **They agree on every timed row** — the cross-check found two rows
the extraction had mislabelled, and the clock was right.

### `gear` `load` `thermal` `ac`

The condition. **`unknown` is common and it is honest** — `gear` is unknown on
most pre-repair rows because "warm, in Park" was requested but never confirmed.

`ac` is `unknown` on 116 rows. It was inferred from an instruction on 81 of them
until that was corrected: an instruction is not a measurement, and this exact
assumption had already invalidated one analysis when the owner said "this while
AC on".

## Provenance

Every row carries `source`, citing conversation messages as `[147]`. Those look
up in [`conversation/transcript.txt`](conversation/transcript.txt).

`screenshots_manifest.csv` joins a reading to its image on
**`reply_message` = `analysis_ready.msg`** — the reading cites the message that
*analysed* the image, one after the message the image arrived in. Joining on
`message` instead links only 190 of 277.

Each manifest row also names its OCR text file, so the full screen contents
behind any reading are one join away.
