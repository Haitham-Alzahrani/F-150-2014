# 2026-09-08 22:05 — the first capture AFTER the battery replacement

Owner: *"after replacing the battery the rpm is static, it's not bouncing."*

`20260908_220538.csv.gz` — 22:05:48 → 22:09:51, 4.1 min, 34 channels,
stationary throughout (`Vehicle speed` 0.000 in all 301 samples), A/C off
(MAF 3.42–3.58 g/s; the compressor puts it near 5). Engine speed n=2,014 at
0.091 s. Contains one rev to 4,087 rpm; the idle analysis excludes it.

**This is the third KAM wipe in the project's record** (battery disconnect
2026-09-05 with the purge valve, an owner relearn plus 300 km before that, this
battery replacement). Both earlier wipes improved the symptom and both relapsed
by roughly 100 km. The odometer trip here reads 1.598 km, so this capture sits
at the very start of that window.

## What changed, measured

Rate-matched to 0.212 s, Park idle 600–720 rpm, 10 s windows:

| Capture | n | Median 10 s span | p10–p90 |
|---|---|---|---|
| Pre-wipe 09-04, 3.2 h | 704 | 34.2 rpm | 24.4–63.5 |
| Post-purge-wipe 09-05 | 123 | 37.3 | 24.9–52.1 |
| Pre-battery 09-08 15:49 | 18 | 32.3 | 18.2–43.2 |
| **Post-battery 09-08 22:05** | **16** | **25.3** | **20.6–33.7** |

Mann-Whitney against pre-wipe 09-04 p = 6.5e-5, against post-purge 09-05
p = 2.9e-5, **against the same-day pre-battery capture p = 0.062 — not
significant at n=18 vs 16.** The same-day pair is the fairest comparison and it
is the weakest result. Treat the improvement as real but not yet established.

## What did NOT change — the rhythm is intact

Longest continuous in-range idle run, Welch on a 0.2 s grid:

| Capture | Run | Peak | Peak ÷ median | Power in peak | sd |
|---|---|---|---|---|---|
| Pre-wipe 09-04 | 773 s | 0.312 Hz | 125× | 57.5 % | 8.57 |
| Post-purge 09-05 | 427 s | 0.332 Hz | 177× | 66.3 % | 9.85 |
| Pre-battery 09-08 | 106 s | **0.293 Hz** | 650× | 75.8 % | **13.38** |
| **Post-battery 09-08** | 117 s | **0.293 Hz** | 213× | 61.4 % | **7.52** |
| 2023 control, healthy | 864 s | 0.156 Hz | 16× | 22.1 % | 4.40 |

**Same frequency to three decimal places, before and after.** The oscillation
did not stop; its amplitude fell by 44 % in standard deviation while its
structure — rate, sharpness, concentration — is unchanged. The truck remains far
from the healthy control on sharpness (213× against 16×) and closer on
amplitude (7.52 against 4.40).

## Why this window matters

CLAUDE.md's standing rule: *"when a repair or reset changes the symptom,
re-measure the full channel set immediately — that window is short and does not
come back."* It was missed after the 09-05 wipe. This capture opens it again and
carries only `Engine RPM` and one bank's short-term trim at rate; commanded
air/fuel, timing advance and the secondary oxygen sensor trim are all absent.
