# 2026-09-14 — the sample-rate test, and the discovery of the `[PCM]` channel family

Four captures, 14:43 to 14:59, taken to answer one question: **does showing a
single channel on the live data page raise the sample rate above the 32.9 Hz
that two channels give?**

## Answer: no — 33.3 Hz is a CEILING, and two channels already reach it

| Capture | What was on the page | `Engine RPM` |
|---|---|---|
| `14-45-16` | **`Engine RPM` alone** | 1,861 samples, **33.3 Hz (30.0 ms)**, 56 s |
| `14-43-48` | 4 channels, then 1 | see below |
| `14-47-34` | no engine channel at all | **none** |
| `14-49-23` | no engine channel at all | **none** |

**This is the first single-channel capture ever recorded on this truck.** The
09-14 rate table in `CLAUDE.md` had a row reading "1 channel — 0, never once
recorded". It is now filled: **33.3 Hz.**

Two channels measured 32.9 Hz in the 09-04 log. One channel gives 33.3. The
difference is one part in eighty — the adapter's own limit, not a per-channel
budget. **Keep two tiles. The second channel is free.**

## The rate law, proven INSIDE one file

`14-43-48` contains the transition live. Three extra channels were on the page
for the first 2.7 seconds and then left it:

| Same file, same drive, seconds apart | `Engine RPM` rate |
|---|---|
| t < 53042.4 — `Engine coolant temperature`, `Fuel/Air commanded equivalence ratio`, `[PCM] ATF Temperature` also polled | **8.4 Hz** |
| t > 53043 — `Engine RPM` alone | **33.3 Hz** |

**Four times faster the moment the other tiles left the screen.** Every earlier
measurement of this law compared different logs on different days; this one is
immune to that objection.

## Two of the four captured nothing

`14-47-34` and `14-49-23` contain only GPS position and the app's own
fuel-economy arithmetic — `Altitude (GPS)`, `Speed (GPS)`, `Distance travelled`,
`Fuel used`, `Instant engine power`. **No `Engine RPM`, no engine channel of any
kind.** `14-49-23` did poll `Catalyst temperature Bank 1 Sensor 1`,
`Catalyst temperature Bank 2 Sensor 1` and `Absolute load value` at 3.0 Hz for
part of its run, but never engine speed.

**Rule this confirms: a recording is only as good as the page left on screen.**
Check the tile is showing before pressing record, and do not navigate away.
