# THE SENSOR SWAP READING — the offset changed sides (2026-09-17, phone clock 5:57)

**Screenshot:
[`data/sensor-swap-2026-09-17/stft-both-banks-0557.jpg`](../data/sensor-swap-2026-09-17/stft-both-banks-0557.jpg).
Extraction tool: [`data/read_trim_screenshot.py`](../data/read_trim_screenshot.py).**

`Short term fuel % trim - Bank 1` and `Short term fuel % trim - Bank 2`, two
tiles, one 15-second window. Owner changed the intake gaskets and moved **all
four oxygen sensors to the mirror position on the opposite bank**.

## Why this was not read by eye

**The two panels are drawn on DIFFERENT vertical scales** — Bank 1 runs
3.91 to −3.0, Bank 2 runs 3.91 to −3.8. Comparing curve heights across them is
exactly the error recorded in `CLAUDE.md` as *"a good number was compared against
a bad one."* The traces were therefore extracted pixel by pixel and both
converted to trim percent using the gridlines, which are 0.6 % apart in both
panels (80 px in the top, 72 px in the bottom).

**The extraction validates against the app's own figures**: it recovers Bank 1
−3.13 to 3.89 against the app's −3.12 to 3.91, and Bank 2 −3.92 to 3.77 against
−3.91 to 3.91.

**A time skew was found and corrected.** Panel 2's vertical gridlines sit 4–5 px
left of panel 1's — the two channels were drawn about **59 ms** apart. Corrected
before comparing; it changes the result by 0.01 %.

## THE RESULT — the offset is on the OTHER BANK now

| | Bank 1 | Bank 2 |
|---|---|---|
| **Before the swap** (n=108 CSV samples, paired within 0.15 s) | baseline | **+1.95 % MORE fuel** |
| **After the swap** (999 columns, one 15 s window) | **+0.58 % more fuel** | baseline |

Bank 1 sits higher in **78 %** of columns, median **+0.64 %**, and the sign holds
in all three thirds of the window (+0.21 %, +1.06 %, +0.47 %; Bank 1 higher in
71 %, 95 %, 70 %).

**THE PREDICTION WRITTEN INTO `CLAUDE.md` BEFORE THIS READING EXISTED:**

> **Bank 1 now needs more fuel** → **The offset MOVED WITH THE SENSOR. A
> lean-biased sensor is PROVEN.** Four sightings of a "driver-side lean offset"
> become one biased part.

**That is the branch the data landed on.** The offset did not stay with the bank,
which is what a driver-side air leak or exhaust leak would have done. It followed
the hardware across the engine.

**It names a physical part for the first time in this investigation.** The
suspect is the **upstream oxygen sensor that used to be on Bank 2 and is now on
Bank 1** — a specific sensor, identifiable, in a known location.

## WHY THIS IS NOT YET PROVEN — four reasons, and they are not small

**1. The magnitude did not mirror.** A pure sensor bias carried across should
reappear at a similar size with the opposite sign: −1.95 % expected, **+0.58 %
observed — under a third.** It is also **less than one quantisation step**
(0.78 %), so it exists only as a duty cycle between adjacent steps rather than as
a clean offset. Something is different besides which side the sensor is on.

**2. The engine state was not recorded.** Warm or cold, Park or Drive, air
conditioning on or off — none of it is known. **Both trims swing roughly −3.9 to
+3.9 % on a slow cycle**, far wider than the settled-idle behaviour in every
earlier capture. `CLAUDE.md` records the air conditioning compressor cycling on a
**15.78 s period**, and the visible window is only about 15 s, so **this capture
cannot separate a compressor cycle from anything else.** If the compressor was
running, the whole window is a disturbed condition.

**3. It is a screenshot, not an export.** The +1.95 % it is being compared against
came from 108 CSV samples paired within 0.15 s. This is one 15-second window read
off a photograph. **Adjacent pixel columns are not independent samples**, so no
significance test may be computed from them — the sign and the size are the
usable part and the t value is not.

**4. THREE things changed, not one.** Intake gaskets, the sensor swap, **and the
truck was dyno-tuned on 2026-09-16** — shift points and throttle response. The
retune landed after the prediction was written.

**On the retune specifically: a calibration applies to both banks equally, so a
bank-versus-bank difference should survive it.** That argument is why the
experiment was still worth running. It is reasoning, not a measurement.

## WHAT SETTLES IT

**The same two channels, exported as CSV #2 (Horizontal), at a known engine
state** — warm, Park, standstill, air conditioning off, three minutes. That
reproduces the exact method behind the +1.95 %, and makes the two numbers
comparable instead of merely opposite.

**If a genuine mirror appears at a known state, a sensor is proven and the part
is named.** If it collapses toward zero, the gasket closed a real leak and the
apparent reversal was this window's condition.
