# The conversation — the source everything else came from

Every reading, finding and elimination in `../` was extracted from these two
files. They were held in a temporary session directory and would have been lost
with it, leaving the derived data with nothing behind it.

## `transcript.txt`

The full text record: **269 messages**, 4 September 22:26 to 5 September 05:02,
about 6 h 36 m of work at the truck.

Each message is headed `===== [n] ROLE timestamp =====`. **That `[n]` is the
citation used throughout the dataset** — every row in `readings.csv`,
`subjective.csv`, `findings.csv` and the rest carries a `source` naming the
message it came from, and this is where to look it up.

Screenshots appear as `[IMAGE]` placeholders. The images themselves are in
[`../screenshots/`](../screenshots/), and
[`../screenshots_manifest.csv`](../screenshots_manifest.csv) joins them to the
message they arrived in and the rows extracted from them.

## `owner_answers.txt`

**15 rounds of direct questions to the owner, and his answers.**

These were nearly lost. They travelled as interactive-tool results rather than
as message text, so the first pass at building `transcript.txt` dropped them
entirely — the assistant appeared to reason from answers that were not in the
record. An extraction agent noticed the gap and they were recovered.

They are the highest grade of evidence in the project: the owner's own words,
answering a specific question. They include "same cold and hot", "never, not
once", "silent - just felt, not heard", "like this since I got it", "pulls great
with no vibration at all" — and the hedges that matter just as much, such as
"5W-30 or similar", "I don't know", and "not sure" about the A/C state during the
live-data scan.

## Why the raw text is kept and not just the extraction

The extraction is a reading of the source, and readings have been wrong here more
than once — a graph axis misread by a factor of sixty, a session-cumulative
average quoted as a per-window value, an inferred A/C state recorded as measured.
Each was caught by going back to what was actually said. **Keeping the source
means the next correction is possible too.**
