# Query cookbook

Everything is in [`../f150.db`](../f150.db) (SQLite) and mirrored as CSVs. The
table to start from is **`analysis_ready`** — the readings with real numeric
types, a wall-clock timestamp, a capture session and a repair epoch attached.

```
sqlite3 data/f150.db
python3 -c "import sqlite3,pandas as pd; \
  df=pd.read_sql('select * from analysis_ready', sqlite3.connect('data/f150.db'))"
```

## Read this before trusting a number

**`is_admissible = 0` means do not use the value as a measurement.** It is
recorded because it was on screen, not because it can be relied on. The main
cause is the scan app's Min/Avg/Max fields, which are cumulative over the whole
session rather than over the window displayed — a distinction that produced two
withdrawn conclusions before it was understood.

**`epoch_by_time` is derived from the source image's clock; `epoch` is what the
extraction assigned.** They now agree on every timed row. Where a reading has no
image behind it, `captured_at` is empty and `epoch_by_time` is `unknown`.

**The repair is the dividing line.** The purge valve went in and the adaptive
memory was wiped between 01:32:39 and 03:11:06 on 5 September. Trims either side
are not comparable, and neither are anything downstream of them.

---

## The comparison the whole investigation turns on

```sql
SELECT captured_at, channel, gear, value_num, epoch_by_time
FROM analysis_ready
WHERE channel LIKE 'LTFT%' AND load = 'idle' AND is_admissible = 1
ORDER BY captured_at;
```

Long term trim at idle: **+3.13 / +2.34 % before the repair, −0.78 / −0.78 %
after**, both banks identical afterwards.

## The load slope that proved a fixed-size air leak

```sql
SELECT load, channel, value_num, captured_at
FROM analysis_ready
WHERE channel LIKE 'LTFT%' AND epoch_by_time = 'pre_purge_valve'
  AND is_admissible = 1
ORDER BY captured_at;
```

Idle **+3.13 / +2.34**, just off idle **+0.78**, 2000 rpm **0** — a correction
that fades as airflow rises, which is what a fixed opening does and a
proportional sensor error does not.

## Park versus Drive, the same engine minutes apart

```sql
SELECT gear, channel, value_num, span_num, captured_at, notes
FROM analysis_ready
WHERE channel IN ('Engine RPM','Tim. adv.') AND gear IN ('P','D')
  AND span_num IS NOT NULL
ORDER BY captured_at;
```

## How the rpm hunt behaved over the whole night

```sql
SELECT captured_at, gear, span_num, epoch_by_time
FROM analysis_ready
WHERE channel = 'Engine RPM' AND span_num IS NOT NULL
ORDER BY captured_at;
```

The span is the peak-to-peak wander per ~15 s window. It did not shrink when the
leak was fixed — which is the evidence that the leak was never driving it.

## Every Mode 06 test with its limit

```sql
SELECT monitor, mid, tid, value, limit_min, limit_max, result FROM mode06
ORDER BY monitor, tid;
```

56 tests, all PASSED. Twelve of them appear nowhere in the written record and
were recovered by OCR of the screenshots.

## What was concluded, and what was withdrawn

```sql
SELECT status, COUNT(*) FROM findings GROUP BY 1;
SELECT statement, reason_withdrawn FROM findings WHERE status = 'withdrawn';
```

The withdrawal history is data. Nineteen findings were withdrawn, each with the
reason — misread axis, cumulative average quoted as per-window, short-term trim
confused with mixture, readings compared across sessions.

## The owner's own words

```sql
SELECT phone_clock, category, observation FROM subjective
WHERE category IN ('symptom','symptom_change') ORDER BY obs_id;
```

These outrank inference. Three conclusions were withdrawn because a measured
correlation was allowed to override what the owner actually reported.

## From a reading back to the picture it came from

```sql
SELECT r.reading_id, r.channel, r.value, m.filename, m.ocr_text_file
FROM analysis_ready r
JOIN screenshots_manifest m ON m.reply_message = r.msg
WHERE r.reading_id = 'PART3-0130';
```

## Everything captured in one session

```sql
SELECT s.exif_session, s.start, s.duration, s.n_images, s.content
FROM sessions_from_exif s ORDER BY s.start;
```

23 sessions across 6 h 36 m. The 1 h 38 m gap between EX15 and EX16 is the
repair.
