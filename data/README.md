# Structured dataset

Machine-readable extraction of every reading taken during the idle-vibration
investigation, so the data can be sorted, filtered and correlated instead of
re-read out of prose.

**829 rows across six tables. `python3 data/validate.py` passes.**

| Table | Rows |
|---|---|
| `readings.csv` | 324 |
| `findings.csv` | 163 |
| `subjective.csv` | 139 |
| `eliminations.csv` | 102 |
| `timeline.csv` | 64 |
| `sessions.csv` | 37 |
| `mode06.csv` | 56 |
| `sessions_from_exif.csv` | 23 |
| `screenshots_manifest.csv` | 277 |

## Everything is text, and the pictures are the proof

| | |
|---|---|
| `screenshots/` | **277 images**, the raw evidence |
| `screenshots_ocr/` | **277 text files** — every screen OCR'd in full |
| `conversation/transcript.txt` | **269 messages** — the source of every extracted row |
| `conversation/owner_answers.txt` | **15 rounds** of the owner's direct answers |
| `mode06.csv` | **56 Mode 06 tests** with limits and results |
| `sessions_from_exif.csv` | **23 capture sessions** rebuilt from image timestamps |

Every row cites the message it came from; every message is in the transcript;
every image links to the rows taken from it and to its own OCR text. **The chain
runs both ways and nothing in it is out of reach.**

### The OCR found readings the extraction had missed

Mode 06 is the case in point. The conversation quoted 29 test results in prose;
the screens actually hold **41**, and merging both sources gives **56 distinct
tests** with their limits. The twelve the prose never mentioned were each
cylinder's two manufacturer-defined entries, the EVAP and purge-flow monitors,
and three of the four VVT test IDs per bank. **All 56 read PASSED.**

That is the argument for keeping the images and OCRing them rather than trusting
the write-up: **the write-up is a selection, and the screen is the record.**

## What the extraction found in the documents

The audit corrected the source documents as well as building the dataset:

- **15 rounds of the owner's direct answers had never been extracted at all** —
  they lived in interactive-tool results, not in message text. They contain
  "same cold and hot", "never, not once", "silent — just felt, not heard", and
  "like this since I got it".
- **Several hedges had been promoted to facts** in `CLAUDE.md` — the oil
  viscosity, the idle relearn after the throttle body clean, the belt inspection,
  the battery age. All now recorded as the hedges they were.
- **81 rows carried an inferred A/C state.** A/C-off was *requested* in the
  instructions and recorded as though measured. Downgraded to `unknown` — this
  is the assumption that already failed once, when the owner corrected an
  analysis with "this while AC on".
- **`docs/DATA-REQUESTS.md` was stale**, still asserting three conclusions that
  had been withdrawn. Struck through in place with a header warning.
- **Four contradictions inside `CLAUDE.md`** where a later section reversed an
  earlier one without the earlier one being marked. All four now cross-reference.
- **An early answer conflicts with a late one.** Asked early how the shake
  behaves through an rpm sweep in Park, the answer was *"present everywhere,
  roughly equal"*. The held-and-rated sweep at the end gave *"worst at idle
  650"*. Flagged in `PART0-0002`, `PART0-0018`, `P0O-0004`, `P0O-0007` rather
  than averaged away.

## Why this exists

Every measurement in this investigation was taken under a specific set of
conditions — gear, load, thermal state, engine speed, and which side of the purge
valve repair it fell on. In the working log those conditions live in sentences
around the numbers. That is readable but not analysable: you cannot sort it, you
cannot group by condition, and you cannot check whether two numbers are even
comparable.

These tables put the condition **in the row with the reading.**

## Files

| File | Contents |
|---|---|
| `SCHEMA.md` | Column definitions and the controlled vocabulary. Read this first. |
| `readings.csv` | Every measurement with the condition it was taken under |
| `sessions.csv` | One row per capture run |
| `subjective.csv` | The owner's own observations — data in their own right |
| `timeline.csv` | Repairs, resets, drives — events that break comparability |
| `findings.csv` | Every conclusion, **including withdrawn ones and why** |
| `eliminations.csv` | Every system ruled in or out, with its evidence |
| `parts/` | Per-agent extraction shards, kept for provenance |
| `merge_parts.py` | Concatenates the shards into the six files above |
| `validate.py` | Checks structure, vocabulary, citations and coverage |

## Three columns that carry most of the weight

**`epoch`** — `pre_purge_valve`, `post_purge_valve_pre_drive`, `post_drive`.
The purge valve was replaced and the Keep Alive Memory was wiped in the same
operation, and the adaptives only relearned after a subsequent drive. **Readings
from different epochs are not comparable** and this column is what stops them
being compared by accident.

**`admissible`** — the scan app shows Min / Avg / Max fields that are cumulative
over the whole session rather than the window on screen. Early in the
investigation those were quoted as though they were per-window, which produced a
bank-asymmetry claim that had to be withdrawn. Any row sourced from those fields
is marked `no`.

**`source`** — every row cites the transcript message number it came from, so any
value can be traced back and checked.

## Using it

```
python3 data/validate.py      # structure, vocabulary, citations, coverage probes
python3 data/merge_parts.py   # rebuild the six CSVs from parts/
```

`validate.py` carries coverage probes for values known to exist in the record —
the +3.13 % idle trim, the −0.78 % relearned trim, 96.47 % absolute load, the
29.38 fuel-cut peg, the 0.371 catalyst monitor value. If an extraction pass drops
a session, a probe fails.

## What the dataset is for

The measurements are complete enough that the remaining questions are comparative
rather than exploratory:

- Whether the ~3.5 s commanded-mixture oscillation and the rpm hunt are related by
  more than shared period — needs cross-correlation on synchronised samples
- How the same channel behaved across epochs, at the same condition
- Whether Park and Drive differ in anything besides rpm span
- What a control sample from another 3.7 would have to look like to settle the
  open question of whether any of this is abnormal

None of those can be answered from prose. All of them can be answered from a
table.
