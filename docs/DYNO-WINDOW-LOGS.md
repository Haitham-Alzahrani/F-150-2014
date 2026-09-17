# THE THREE LOGS AROUND THE DYNO — 2026-09-16/17

**`data/carscanner/2026-09-16-17-dyno-window/`.** The dyno retune was at **18:29
on 09-16**, which places one log before it and two after.

| Log | Clock | Relative to the retune | What it can answer |
|---|---|---|---|
| `2026-09-16_17-54-19` | 17:55–18:01 | **34 min BEFORE** | **Both banks' short term trim, 1,885 paired samples** |
| `2026-09-16_22-10-53` | engine OFF | after | The codes-cleared counters; nothing running |
| `2026-09-17_00-49-22` | ~56 min | after | Temperatures only — **one bank of trim, n=8** |

**Neither post-retune log can answer the bank question.** The 22:10 log was taken
with `Engine RPM` **0 in all 63 samples** — key on, engine off — and its page was
fuel consumption and airflow. The 00:49 log carries only
`Short term fuel % trim - Bank 1`, eight samples. **The comparison exists in the
pre-retune log only.**

## 1. THE ADAPTIVE MEMORY WAS WIPED — not merely a code clear

**`Long term fuel % trim - Bank 1` and `- Bank 2` both read EXACTLY 0.0000 across
all 213 samples** in the 17:54 log.

`CLAUDE.md` named this test in advance: *"if `Long term fuel % trim` reads exactly
0.0000 on both banks, the adaptive memory went with it after all."* **It did.**

The counters agree, and the history makes the pattern unambiguous:

| Log | Distance since cleared | Warm-ups |
|---|---|---|
| 09-04 | 101 km | 3 |
| **09-05 03:40** | **28–40 km** | **0** ← purge valve + memory wipe |
| 09-08 17:04 | 189 km | 3 |
| **09-09 16:12** | **2 km** | **0** ← battery change |
| 09-14 | 360–364 km | 7 |
| **09-16 22:10** | **127–142 km** | **0** ← **this event** |

**Every reset in this project shows the same signature and this one matches it.**
So short term trim is carrying the entire fuel correction alone, which is why it
swings **−20.31 to +15.62 %** here against the few points seen in settled
captures.

## 2. THE BANK OFFSET AT SETTLED IDLE — Bank 1, and it is stable

`Short term fuel % trim - Bank 1` minus `- Bank 2`, paired within 0.15 s:

| Minute | Engine speed | Bank 1 − Bank 2 | n |
|---|---|---|---|
| 17:55 | not sampled | **+0.613 %** | 399 |
| 17:56 | not sampled | **+0.679 %** | 520 |
| 17:57 | not sampled | **+0.599 %** | 540 |
| **17:58** | **629–690 rpm** | **+0.564 %** | 252 |
| 17:59 | 523–787 | −0.859 % | 91 |
| 18:00 | 562–1314 | −0.960 % | 83 |

**Four consecutive minutes give the same answer within 0.12 points**, and the one
minute where engine speed is on the page **confirms 629–690 rpm settled idle** and
matches the three before it. Together: **+0.621 %, n=1,711.**

**This corroborates the screenshot read by pixel, which gave +0.58 %** — two
independent methods, same sign, same size.

| | Bank 1 | Bank 2 |
|---|---|---|
| Before the swap (n=108) | baseline | **+1.95 % more fuel** |
| After the swap, settled idle (n=1,711) | **+0.62 % more fuel** | baseline |

**The offset is on the opposite bank from before. It followed the hardware.**

### The sign REVERSES under throttle movement — a genuinely new observation

Minutes 4 and 5 are throttle blips: engine speed to 1,314 rpm, trims −21 to +16.
There **Bank 2** needs more fuel, **−0.907 %, n=174**.

**This is not a bank property and must not be averaged with the idle figure.**
Tip-in and overrun throw trims in both directions, and `CLAUDE.md` already records
a **+9.38 %** tip-in spike and a **−11.72 %** overrun crash on this truck. **It
does mean any whole-session average is condition-soup**: mixing everything gives
+0.480 %, which is neither number.

**A caution on method that cost a wrong intermediate answer here:** selecting the
idle samples by the *time span* of the 600–700 rpm readings sweeps in the blips
sitting between them and flips the result to −0.711 %. **Select by each sample's
own condition, not by a time window bounded by qualifying samples.**

## 3. Still not a mirror — and the gasket is the likely reason

A carried-across sensor bias should reappear at similar size with opposite sign:
−1.95 % expected, **+0.62 % observed**.

**One reading fits both facts: there were two contributions, and only one moved.**
A physical leak on the driver's side that the new intake gaskets closed, plus a
sensor bias that travelled with the part. That would shrink the total and flip
what remains. **It is a hypothesis that fits, not a measurement** — the gasket and
the sensors were changed in one operation, which is the confound recorded when the
work was done.

## 4. Two cross-checks that had ZERO paired samples are now done

`CLAUDE.md`: *"FOUR OF SEVEN CROSS-CHECKS HAVE ZERO PAIRED SAMPLES... the
comparisons that would most directly expose a lying sensor are the ones nobody has
captured."* The 00:49 log captured two of them.

**`Engine coolant temperature` vs `[PCM] Cylinder head temperature`** — n=1,679,
**identical in 99.5 %**, never more than 1 °C apart, r=0.9951. **This does NOT
clear either sensor.** Ford derives coolant temperature from the cylinder head
temperature sensor on several engines; if it does so here, these are one
measurement on two channels and the check is **vacuous — the same trap the
catalyst temperature channels turned out to be**. [VERIFY whether the 3.7 has a
separate coolant temperature sensor at all.]

**`Intake air temperature` vs `Ambient air temperature`** — n=3,358, intake sits
**19 °C above ambient (median)**. **Normal heat soak** on a stationary engine with
no airflow through the bay. The r = −0.959 is not a sensor relationship: over
56 stationary minutes intake climbed 38→56 °C while the evening ambient fell
39→36 °C. **Both were following time in opposite directions.**

### And a partial correction to the catalyst finding

`CLAUDE.md` states the two catalyst temperature channels are *"one computed value
printed on two channels."* In this session, n=3,359: r=0.9999 but **identical in
only 53.2 %**, differing by **−6 to +9 °C**. **They do diverge.** The earlier
session had them exactly equal 78.3 % of the time and never more than 1.5 °C
apart. **The channels are not a single value copied twice**, though they remain
far too tightly coupled to be treated as independent evidence.

## 5. `Ethanol fuel percent` = 18.43 % — a FOURTH discrete value

`CLAUDE.md` records only three ever seen: 9.80, 19.22, 22.35 (bytes 25, 49, 57).
**18.43 % is byte 47 and is new.** Consistent with the established behaviour — a
learned value that resets on a memory wipe and climbs back.
