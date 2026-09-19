# The per-cylinder misfire counters were captured on 2026-09-05

**This repository states three times that per-cylinder misfire counts have
"never been obtained". That is wrong. They are in `data/f150.db`, in the
`mode06` table, and the source screenshots are in `data/screenshots/`.**

Found 2026-09-19 while re-verifying the cylinder acceleration analysis. The
same failure as `[PCM] Currently Detected Engine Misfire`, `[PCM] Knock
Sensor 1`/`2` and the cylinder acceleration channels, all of which this file
once called "never logged" — **the data was already here and nobody looked.**

## The baseline

**2026-09-05, phone clock 04:36 local, uploaded 01:38:46 UTC.** Verified by
reading the original images, not only the transcribed text.

| Cylinder | MID | TID $0B — EWMA over last 10 driving cycles | TID $0C — counts, last/current cycle | Result |
|---|---|---|---|---|
| 1 | `$A2` | 0 | 0 | PASSED |
| 2 | `$A3` | 0 | **0** | PASSED |
| 3 | `$A4` | 0 | 0 | PASSED |
| 4 | `$A5` | 0 | **2** | PASSED |
| 5 | `$A6` | 0 | 0 | PASSED |
| 6 | `$A7` | 0 | **1** | PASSED |

**The ten-driving-cycle average is zero on every cylinder.** Counts of 1 and 2
against a maximum of 65535 are single events, not a pattern.

**This also settles a question `docs/MODE-22.md` left open: MID `$A1`–`$A7` ARE
answered by this PCM**, mapping cylinder *N* to MID `$A1+N`. That mapping is no
longer an assumption from a standard — it is confirmed on this VIN.

## Every other monitor, same capture

| Monitor | Bank 1 | Bank 2 | Limit | Result |
|---|---|---|---|---|
| Catalyst | 0.371 | 0.363 | 0–0.836 | PASSED |
| Fuel System | 0 | 0 | 0–0.797 | PASSED |
| Oxygen sensor heater, sensor 1 | 2550 | 2455 | 1120–3800 | PASSED |
| Oxygen sensor heater, sensor 2 | 637 | 652 | 220–3000 | PASSED |
| Cam phasing, TID `$85` | 0.060 | 0.05 | 0–20 | PASSED |
| Purge Flow | 0 | — | 0–0 | PASSED |

**Every monitor passed with wide margin and every bank-paired monitor is
symmetric.** Note the catalyst monitor gives a genuine per-bank number, which
the live `Catalyst temperature Bank 1/2 Sensor 1` channels do not — those track
each other within 0.1 °C across thousands of samples and cannot discriminate
between banks.

## WHAT THIS DOES TO THE CYLINDER 6 THEORY

The cylinder acceleration analysis of `2026-09-17_15-49-53.csv` makes cylinder 6
the lowest — stably, in all three thirds of the window, and in 100 % of 5,000
bootstrap resamples. **The misfire counters do not corroborate it, and they rank
cylinder 4 above cylinder 6.** Cylinder 2, the alleged second suspect, is at
zero.

The counter is a **direct count of combustion events with the module's own
limits**. Cylinder acceleration is **derived, dimensionless, quantised to
0.0156, and its six values sum to −0.133 rather than zero** — so its zero point
is not the engine average and its absolute sign carries no meaning.

**The direct measurement outranks the derived one.**

## THE LIMIT — and it is the reason to re-read

**The baseline is PRE-TUNE.** The cylinder acceleration capture is 2026-09-17,
twelve days later and after the custom tune. The two cannot refute each other
as they stand. **A fresh reading closes that gap in two minutes:**

```
python data/diagnose.py misfire
```

It reads the counters live, prints them beside this baseline, and says which
branch of the decision tree the truck is on.

**Clearing codes or disconnecting the battery RESETS these counters.** If either
has happened since 2026-09-05 the comparison is void — drive it and re-read.
