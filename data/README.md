# Structured dataset — extraction in progress

Machine-readable extraction of every reading taken during the idle-vibration
investigation, so the data can be sorted, filtered and correlated instead of
re-read out of prose.

**Status: extraction running.** The CSVs are not present yet. This directory
currently holds the schema and the tooling.

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
