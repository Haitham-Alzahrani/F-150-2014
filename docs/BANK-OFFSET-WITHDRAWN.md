# THE SENSOR SWAP RESULT IS WITHDRAWN — the offset was never stable enough to track

**Date: 2026-09-18. Tool: [`data/bank_offset.py`](../data/bank_offset.py).**

Owner asked whether flipping the oxygen sensors changed anything. Re-deriving the
answer from every session that ever polled both banks — rather than from the two
this project had looked at — destroys the finding.

## What was claimed

`CLAUDE.md`, `docs/SENSOR-SWAP-RESULT.md` and `docs/DYNO-WINDOW-LOGS.md` all state
that the offset **followed the hardware**: Bank 2 needed +1.95 % more fuel before
the swap, Bank 1 needed +0.62 % after it, and that this **named the upstream
oxygen sensor** that moved from Bank 2 to Bank 1.

## Three errors, each sufficient on its own

### 1. It read short term trim alone after long term had learned

The two halves of the correction trade off — this file has said so since 09-09:
*"when long term rises, short term falls by the same amount."* The only
comparable quantity is the **total, short + long, same bank, same instant.**

On the 2026-09-17 log long term trim has **re-learned asymmetrically** since the
wipe — Bank 1 **−3.125 %**, Bank 2 **−2.344 %**, in 4,615 of 4,631 samples. That
is −0.781 points, and it points the **opposite way** to the short term difference:

| 2026-09-17, n=4,484 paired | |
|---|---|
| Short term, Bank 1 − Bank 2 | **+1.116 %** |
| Long term, Bank 1 − Bank 2 | **−0.781 %** |
| **Total correction difference** | **+0.336 %** |

**The long term trim absorbs 70 % of it.** Quoting +1.116 % is quoting one half
of a quantity whose halves cancel.

### 2. "Settled idle confirmed" rested on 4 engine speed samples

The +0.62 % came from minutes 17:55–17:58 of `2026-09-16_17-54-19`.
**Those minutes contain ZERO engine speed samples.** The claim that engine speed
"confirms settled idle" there came from 4 samples in the last of them.

Where engine speed *does* exist in that log, the sign is the other way:

| Minute | Engine speed | Bank 1 − Bank 2 | |
|---|---|---|---|
| 17:55 / 17:56 / 17:57 | **not sampled at all** | +0.703 / +0.607 / +0.607 % | condition unknown |
| 17:58 | 4 samples | +0.781 % | n=2 clean |
| 17:59 / 18:00 / 18:01 | sampled, guard-band clean | **−0.308 / −1.136 / −0.977 %** | **Bank 2 needs more** |

**The half of the log with engine speed says Bank 2. The half without says
Bank 1.** Neither is clean — the rpm-bearing minutes are the ones containing the
throttle blips, and short term trim lags engine speed by 0.65 s, so a 2 s guard
band may not clear a recovery from 1,314 rpm.

### 3. The offset is not stable — it changes sign INSIDE one session

`docs/READINGS-SCAN.md` said *"only ONE session in the entire project ever polled
both short term trims together at settled idle."* **Twelve sessions carry both
channels.** That scan globbed `*.csv`; the rest are stored **gzipped or zipped**,
so a sweep meant to be exhaustive read 2 of 12 files.

The largest of them was never analysed: **2026-09-04, 3.2 hours of unbroken Park
idle, 1,746 samples that pass the guard band.** Long term trim is *fixed* at
+3.125 / +2.344 for almost all of it, so the drift below is real and is entirely
in short term:

| Block of the session | short B1 | short B2 | long B1 | long B2 | **TOTAL B1−B2** |
|---|---|---|---|---|---|
| 1 | −0.467 | −0.518 | +2.685 | +2.014 | **+0.722** |
| 2 | −0.038 | −0.107 | +3.125 | +2.344 | **+0.851** |
| 3 | +0.572 | +1.818 | +3.125 | +2.344 | **−0.515** |
| 4 | +1.069 | +3.273 | +3.125 | +2.344 | **−1.423** |
| 5 | +0.513 | +2.717 | +3.125 | +2.344 | **−1.423** |
| 6 | +0.502 | +2.593 | +3.125 | +2.344 | **−1.368** |

**It crosses zero in the middle of one continuous idle, with nothing done to the
truck.** Range **+0.85 to −1.42 — 2.3 points.** The swap was being judged on a
difference of well under one point.

**And it is not a settling curve that could be waited out.** The two long sessions
drift in *opposite* directions:

| minutes into the session | 2026-09-04 | 2026-09-17 |
|---|---|---|
| 15–30 | **+0.788** | +0.124 |
| 30–45 | — | −0.115 |
| 45–60 | — | +0.643 |
| 60–75 | **+0.852** | **+0.994** |
| 135–150 | **−1.379** | — |

**One ends negative, the other ends positive.** There is no "settled" value to
compare.

### What the sessions give, side by side

| Session | Era | Total at guard-band idle | n |
|---|---|---|---|
| `2026-09-04 22-23-38` | pre | **−0.466 %** (range +0.85 … −1.42) | **1,746** |
| `20260905_041723` | pre | −1.373 % | 42 |
| `20260908_154859` | pre | +0.220 % | 42 |
| `2026-09-16_17-54-19` | **post** | −0.686 % | 140 |
| `2026-09-17_15-49-53` | **post** | +0.336 %, **no idle confirmation** | 4,484 |

**Every post-swap number sits inside the range the truck covered before the swap,
within a single session.**

## What actually stands

* **The bank difference is real but it is not a constant.** It wanders across
  roughly 2.3 points on a timescale of tens of minutes at a steady Park idle.
* **The swap cannot be judged against it.** Every post-swap reading falls inside
  the range the truck already covered by itself, before anything was touched.
* **The swap is unevaluated — not refuted.** A sensor bias may well have moved.
  Nothing measured can currently see it.
* **A single number for "the bank offset" should not be quoted again** without the
  session it came from and where in that session it sits.

## The capture that settles it

Unchanged from `docs/IDLE-LOG-LIST.md` #2, with one addition now forced:

```
Short term fuel % trim - Bank 1
Short term fuel % trim - Bank 2
Engine RPM
Long term fuel % trim - Bank 1        <- second run, swap against one short term
Long term fuel % trim - Bank 2
```

Three tiles, three minutes, warm Park idle, **do not touch the throttle** — the
sign reverses under throttle movement. Then repeat with the long term pair, because
**all four are needed and four tiles costs too much rate to run at once.**

Engine speed must be on the page. Without it the capture cannot be read, which is
the single lesson this correction repeats for the fourth time in this project.
