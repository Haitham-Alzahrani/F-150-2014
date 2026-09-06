# 01 — Fuel, air metering, oxygen sensors, mixture control and EVAP

**Scope:** fuel system, air metering, oxygen sensors, mixture control, evaporative
emissions. 2014 F-150 XL 3.7 L Ti-VCT, VIN `1FTMF1EM1EFC80632`, 131,313 km on the
PCM odometer, Jeddah.

**Data:** the four Car Scanner logs in `data/carscanner/`, loaded with
`carscanner_lib.load`, every channel kept on its own true sample times. Nothing
is forward-filled. Every bank-to-bank comparison in this document is made on
samples taken **in the same window of the same log**; where that was impossible
it is said so explicitly.

| Log | Clock | Duration | Condition |
|---|---|---|---|
| `2026-09-04 22-23-38.zip` | 22:24:01 – 01:35:49 | 191.8 min | **Pre-repair.** Old purge valve, Park idle throughout, A/C off (`A/C pressure` = 0, n=37), vehicle speed 0 |
| `20260905_030915.csv.gz` | 03:09:42 – 03:30:15 | 20.5 min | Post valve **+ KAM wipe**. Drive idle then Park idle, standstill |
| `20260905_034051.csv.gz` | 03:46:46 – 04:04:12 | 17.4 min | **The drive.** 0–88 km/h, decelerations, one pull to 6832 rpm |
| `20260905_041723.csv.gz` | 04:17:37 – 05:07:27 | 49.8 min | After the drive. Mostly standstill idle, some low-speed |

Bank convention used throughout: **Bank 1 = passenger side, cylinders 1-2-3.
Bank 2 = driver side, cylinders 4-5-6.**

---

## 1. Summary table

| Parameter | Measured | n | Reference | Verdict |
|---|---|---|---|---|
| **Total fuel correction, Bank 1 (passenger, 1-2-3), Park idle, pre-repair** | **+2.91 % / +3.95 %** in two blocks | 1,985 / 3,057 | ±10 % LTFT, ±5 % STFT (community) | **NORMAL** |
| **Total fuel correction, Bank 2 (driver, 4-5-6), Park idle, pre-repair** | **+2.12 % / +5.34 %** same two blocks | 1,985 / 3,057 | as above | **NORMAL** |
| **Bank-to-bank difference (B2 − B1), pre-repair** | **−0.79 % then +1.38 %** in one session | 1,985 / 3,057 | "should be similar"; <3 % rule of thumb | **NORMAL in size, UNCERTAIN in stability** |
| **Bank-to-bank difference, post-repair relearned** | **+2.33 %** (04:19:01–04:19:32) | 251 | as above | **UNCERTAIN — short window** |
| **LTFT both banks, post-repair, fully relearned** | **−0.781 % / −0.781 %**, every single sample | 1,535 / 1,470 | 0 ± 10 % | **NORMAL — excellent** |
| **LTFT both banks immediately after KAM wipe** | **0.000 %**, every sample | 5,498 / 6,592 | erased | Expected |
| **Total correction at in-gear idle (~550 rpm), post-wipe** | B1 **+0.21 %**, B2 **+0.60 %** | 3,718 / 4,559 | ±5 % | **NORMAL** |
| Fuel trim at cruise / acceleration / overrun | **NOT PRESENT IN ANY LOG** | 0 | — | **CANNOT DETERMINE** |
| **Upstream wideband B1 (passenger), Park idle** | AFR 14.231–15.178, mean 14.662, **λ 0.998** | 7,948 | λ 1.00 ± 0.03 | **NORMAL** |
| **Upstream wideband B2 (driver), Park idle** | AFR 14.115–15.231, mean 14.680, **λ 0.999** | 13,386 | λ 1.00 ± 0.03 | **NORMAL** |
| **Upstream bank symmetry, paired same window** | **B1 − B2 = −0.007 AFR** | 6,695 | matched | **NORMAL** |
| **Upstream response, deceleration fuel cut-off** | both peg at **29.3826** (PID ceiling, λ ≈ 2.0), **sd = 0.00000** | 680 (B1) / 412 (B2) longest | full range, fast | **NORMAL — both banks' injectors seal** |
| **DFCO entry / exit transition time** | B1 0.24–0.63 s in, 0.13–0.45 s out; B2 0.12–0.60 s in, 0.18–0.60 s out | 9 / 7 episodes | Mode 06 limit 0.4 s (rise) | **NORMAL** |
| **Upstream sensor internal consistency** (AFR vs pump current) | r = **+0.988** (B1), **+0.987** (B2) | 7,948 / 13,386 | monotonic | **NORMAL** |
| Upstream AFR at wide open throttle | **NOT SAMPLED** — both channels off during the 4:02:28–4:02:36 WOT | 0 | 12.0–13.0 expected | **CANNOT DETERMINE** |
| **Downstream B1 (passenger) swing vs B2, truly simultaneous** | sd ratio **0.95, 1.15, 1.27, 0.27** (4 windows, pre-repair); **1.01 / 0.99 / 0.88** (logs 1/2/3) | 32–137 per window | matched | **NORMAL — prior "2×" claim REFUTED** |
| **Downstream both banks, pre-repair, active windows** | 0.085–0.875 V, p2p **0.62–0.79 V**, at the dither period | 2,407 (B1) / 2,137 (B2) | steady = good cat | **ABNORMAL-looking, but see §4.3** |
| **Downstream both banks, post-repair, all three logs** | steady **0.735–0.860 V**, p2p **0.045–0.156 V** | 42 / 69 / 114 | 0.6–0.8 V steady | **NORMAL** |
| **Downstream drives its own bank's trim** | B1 downstream vs STFT B1 **r = −0.439 at −0.60 s**; vs STFT B2 **r = +0.079** | 4,549 / 4,730 | per-bank loop | **NORMAL** |
| **Commanded air/fuel dither, pre-repair** | λ 0.9847–1.0159, **±1.54 %**, period **3.92 s** (0.255 Hz) | 7,515 | fore/aft catalyst dither | **NORMAL** |
| **Commanded air/fuel dither, post-repair** | λ 0.9800–1.0224, **±1.58 %**, period **3.28 s** (0.305 Hz) | 17,418 | as above | **NORMAL — unchanged by the repair** |
| **Measured λ swing vs commanded** | measured p2p 0.95–1.12 AFR vs commanded 0.46 AFR | 7,948 / 7,515 | measured ≥ commanded | **NORMAL** |
| **MAF, Park idle, pre-repair** | **2.980 g/s** (sd 0.041) and **2.952 g/s** (sd 0.011), median 3.010 over the session | 681 / 103 / 4,118 | 0.8–1.2 g/s per litre → **2.96–4.44 g/s**; general 2–7 g/s | **NORMAL — at the bottom of the band** |
| **MAF, idle, post-repair** | 3.33–5.88 g/s across 8 short bursts | 4–12 each, 57 total | as above | **NORMAL, but sparse** |
| **MAF at wide open throttle** | peak **215.27 g/s at 6219 rpm** → **VE 101–107 %** | 72 samples >150 g/s | 95–105 % is excellent for NA port injection | **NORMAL — validates MAF calibration** |
| **Commanded EVAP purge, pre-repair** | **37.255–41.176 %**, only **11 distinct values in 2.5 hours** | 7,533 | should modulate | **ABNORMAL — flat command** |
| **Commanded EVAP purge, post-repair** | **33.3–50.2 %**, 23 distinct values, stepping in 0.39 % increments | 2,107 | modulating | **NORMAL** |
| **EVAP vapour pressure, pre-repair idle** | **−292 to −748 Pa**, mean **−602 Pa**, sustained 2.5 h | 1,500 | ≈ 0 Pa when not testing | **ABNORMAL** |
| **EVAP vapour pressure, during the drive** | mean **−13.8 Pa**, hovering at atmosphere | 259 | ≈ 0 Pa | **NORMAL** |
| **EVAP vapour pressure, after the drive** | −77 to −447 Pa | 20 | — | **UNCERTAIN — sparse** |
| **Ethanol fuel percent, pre-KAM-wipe** | **16.078 %** (= raw byte 41/255), zero variance | 109 | Saudi pump fuel is E0 | **ABNORMAL (inferred, not sensed)** |
| **Ethanol fuel percent, post-KAM-wipe** | **19.216 %** (= raw byte 49/255), zero variance | 4 + 36 | as above | **ABNORMAL — and it went UP across a wipe** |
| **Barometric pressure** | **97 kPa** flat (96 once during the drive) | 1,500 / 263 / 14 | Jeddah is at sea level, ≈ 100–101 kPa | **UNCERTAIN — see §7.2** |
| **Two long-term-trim suspension events, steady idle** | both LTFTs → 0.00 % for **148 s** and **104 s**, then returned to the exact prior values | 2,321 / 1,630 | — | **ABNORMAL — new finding, §3.4** |
| **Bank 2 upstream dropout** | reads exactly 0.0000 for 26 consecutive samples, 04:01:48–49 | 26 of 5,684 | — | **NORMAL — single artefact** |
| Catalyst temperature, both banks | identical to 3 decimal places in every log | 1,521 / 1,520 | — | Modelled value, not a measurement |
| Knock retard | 0.000° on every sample in every log | 21 + 5 + 12 | 0° | **NORMAL** |

---

## 2. The headline

**Nothing in the fuel, air-metering, oxygen-sensor or mixture-control system
measures faulty.** Every number that has a defensible reference sits inside it,
usually with wide margin. The one channel set that genuinely looked wrong —
the EVAP purge command and the evaporative vapour pressure — looked wrong
**before** the purge valve was replaced and looks right after it. This analysis
therefore adds an independent, previously unused corroboration that the old purge
valve was a real fault, and it adds nothing new to explain the felt shake.

**Two prior conclusions in this project are corrected by numbers below:**

1. **"Bank 1's post-catalyst sensor swings nearly twice as far as bank 2's"** is
   **refuted**. It came from comparing two *consecutive but non-overlapping*
   sampling bursts. In the four windows where both sensors were genuinely sampled
   at the same time, the standard-deviation ratio is 0.95, 1.15, 1.27 and 0.27 —
   and in the other three logs 1.01, 0.99, 0.88. §4.3.
2. **"Bank trim difference 0.00 % / the bank asymmetry question is closed"** is
   **softened**. The session-average difference is small because the difference
   *changes sign inside the session*: −0.79 % early, +1.38 % late. The size is
   never a fault, but "0.00 %" is a session average of two different states. §3.2.

---

## 3. Fuel trim

### 3.1 What exists, and what does not

Fuel trim in these logs is **only ever recorded at standstill idle**. There is no
short-term trim sample anywhere in the dataset at cruise, at acceleration or on
overrun. In the drive log (`20260905_034051`) the trim channels were not being
polled at all except long term trim from 04:04:11 to 04:06:03, after the drive
was over. **Every trim statement below is an idle statement.**

Total correction is always computed as **short term + long term of the same
bank**, on a common 10 Hz grid, with a NaN wherever either channel's nearest real
samples straddle a gap wider than 0.6 s.

### 3.2 Pre-repair, Park idle ~652 rpm, A/C off, old purge valve

Three contiguous blocks in which **all four trim channels were being polled at
once**:

| Block | n | rpm | ST B1 | LT B1 | **Total B1** | ST B2 | LT B2 | **Total B2** | **B2 − B1** |
|---|---|---|---|---|---|---|---|---|---|
| 22:51:05–22:54:25 | 1,985 | 652.5 | −0.21 | +3.12 | **+2.91** | −0.22 | +2.34 | **+2.12** | **−0.79** |
| 00:48:49–00:55:05 | 3,057 | 651.6 | +0.83 | +3.12 | **+3.95** | +2.99 | +2.34 | **+5.34** | **+1.38** |
| 00:55:27–00:56:22 | 423 | 650.8 | +0.75 | +3.12 | **+3.88** | +2.84 | +2.34 | **+5.19** | **+1.31** |
| all simultaneous | 5,962 | 651.9 | | | **+3.47** | | | **+3.99** | **+0.52** |

Two things follow.

**The engine was running lean at idle by +2 to +5 %.** Small — well inside the
±10 % that would be called normal, and nowhere near the ±25 % that sets a code —
but consistently positive on both banks for three hours. This is the lean bias
the project already attributed to the purge valve, and the numbers here agree
with the screenshot-derived figures.

**The bank difference is not a constant offset.** Both long term trims sat pinned
at exactly +3.125 % (B1) and +2.344 % (B2) for the whole session — 7,078 and
23,882 samples at those exact values. All of the movement was in short term trim,
and it moved differently on the two banks: bank 1's short term walked from −0.21
to +0.83 %, bank 2's from −0.22 to **+2.99 %**. So the difference **B2 − B1
swung from −0.79 % to +1.38 % inside one steady, unchanging Park idle**, at
constant rpm, with no intervention.

Coolant rose 82 → 97 °C over the same interval and intake air fell 38 → 37 °C.
The upstream sensors did not move: bank 1 averaged 14.66 AFR, bank 2 14.68 AFR
across the whole session (§4.1), so both banks were being *held* at the same
lambda; only the amount of correction needed to hold them there differed.

*Speculation, labelled as such:* a purge valve stuck partly open flows
continuously, and the manifold's purge port does not feed both banks equally. For
the first hour the canister still had fuel vapour in it (the purge stream adds
fuel to the bank it favours); after three hours of continuous flow the canister
is dry and the same stream is plain air (it now leans that bank). That would
produce exactly a slow, one-sided drift with the sign observed, and it would end
when the valve was replaced. Nothing in this dataset tests it.

### 3.3 Post-repair

**Immediately after the KAM wipe (log `20260905_030915`).** Both long term trims
read **0.000 % on every one of 5,498 and 6,592 samples** — erased, as expected.
Short term trim is therefore the entire correction.

The two banks were polled in alternating blocks in this log, not simultaneously
(only 30 grid points have both), so **the two banks may not be compared against
each other here.** Each bank may be compared against itself across conditions:

| Bank | Park idle ~651 rpm | n | In-gear idle ~550 rpm | n | Change |
|---|---|---|---|---|---|
| B1 (passenger, 1-2-3) | **−1.58 %** (03:09:39–03:11:53) | 1,860 | **+0.21 %** (03:19:01–03:23:03) | 3,718 | **+1.79** |
| B2 (driver, 4-5-6) | **−1.24 %** (03:09:42–03:14:03) | 1,995 | **+0.60 %** (03:14:03–03:23:12) | 4,559 | **+1.84** |

Both banks moved by the same amount, +1.8 %, going into gear. That is a normal
load-cell effect — in gear the converter loads the engine and the operating point
moves. **Caveat: time and condition are confounded here.** The Park samples are
the first two minutes after a KAM wipe, when short term trim is still converging;
the in-gear samples are ten minutes later. Do not treat +1.8 % as a measured
Park-vs-Drive coefficient.

**After the drive and a full relearn (log `20260905_041723`).** Long term trim
reads **exactly −0.781 % on all 1,535 bank 1 samples and all 1,470 bank 2
samples** — one quantisation step below zero, identical on both banks, no
variation at all. That is as clean a long term trim as an engine can have.

Short term trim in that log is polled only 184 (B1) and 147 (B2) times. In the
one 31-second block where both are dense (04:19:01–04:19:32, n=251 grid points,
606 rpm at standstill) the totals are B1 **+0.33 %**, B2 **+2.66 %**,
**difference +2.33 %**. That is the largest bank difference anywhere in the
dataset, but it rests on 31 seconds and should not be treated as established.

The intermediate read (log `20260905_034051`, 04:04:11–04:06:03, after the drive)
gives long term B1 median **−1.562 %** (n=1,582) and B2 **−0.781 %** (n=1,462) —
one step apart, both essentially zero.

### 3.4 NEW: long term trim was suspended twice at steady idle

Something not previously recorded. In the pre-repair session, at unchanging Park
idle (651–654 rpm), **both long term trims dropped to 0.00 % and then returned to
their exact previous values**:

| Event | Bank 1 | Bank 2 | Duration |
|---|---|---|---|
| 01:14:55 – 01:17:24 | not polled | **0.00 %**, n=2,321 | **148 s** |
| 01:26:51 – 01:28:35 | **0.00 %**, n=1,617 | **0.00 %**, n=1,630 | **104 s** |

Both returned by ramping back up through +0.781 and +1.562 to the exact prior
+3.125 / +2.344. During the first event short term trim on bank 1 went from
sd 1.07 % to **sd 2.65 %**, with excursions to **−11.72 %** and **+9.38 %** —
*the two largest short term trim excursions in the entire 3-hour session both
fall inside that 148-second window*, at a dead-steady idle.

| STFT B1 window | n | mean | sd | min | max |
|---|---|---|---|---|---|
| 01:10–01:14, before | 3,865 | −0.78 | 1.07 | −4.69 | +3.12 |
| **01:14–01:18, event** | **3,744** | −0.62 | **2.65** | **−11.72** | **+9.38** |
| 01:18–01:22, after | 3,916 | +1.16 | 1.06 | −2.34 | +3.12 |

*Speculation, labelled as such:* long term trim reading zero while short term
swings wildly and then handing back the identical learned value is the signature
of a PCM-initiated diagnostic that suspends adaptive learning while it perturbs
the mixture. The obvious candidate on this truck is the **EVAP purge flow / leak
check**, which commands the purge valve shut and open and watches the trims
respond. With a valve stuck partly open, that test would produce a large
response — which is what is logged. Purge command and evaporative vapour pressure
were **not being polled** in either window, so this cannot be confirmed from this
data. §9 gives the capture that would settle it.

---

## 4. Oxygen sensors

Channel identity: `Oxygen sensor 1 Wide Range …` is **bank 1 sensor 1
(upstream, passenger side)**; `Oxygen sensor 5 Wide Range …` is **bank 2 sensor 1
(upstream, driver side)** — Ford's OBD sensor numbering assigns 1–4 to bank 1 and
5–8 to bank 2. `Oxygen sensor 2 Bank 1 / Bank 2 Voltage` are the two post-catalyst
narrowband sensors.

Car Scanner reports the wideband PIDs as AFR. The underlying PID is dimensionless
lambda with a 2/65536 step; the app's multiplier works out at 14.6913 for the
sensor channels (the deceleration ceiling 29.3826 = λ 1.9988 ≈ the PID maximum of
2.0) and 14.6313 for the commanded channel. Lambda values below are computed with
those constants.

### 4.1 Upstream widebands — both healthy, matched, fast

Pre-repair Park idle, whole session:

| | n | AFR min | AFR max | AFR mean | **λ mean** | sd |
|---|---|---|---|---|---|---|
| B1 (passenger, 1-2-3) | 7,948 | 14.231 | 15.178 | 14.662 | **0.998** | 0.175 |
| B2 (driver, 4-5-6) | 13,386 | 14.115 | 15.231 | 14.680 | **0.999** | 0.186 |

**Paired on a common 0.06 s grid, 22:32:03–00:57:14, n=6,695: B1 − B2 =
−0.007 AFR.** The two banks are held at the same mixture to within one part in
two thousand.

**Internal consistency.** Each sensor's reported AFR correlates with its own
reported pump current at **r = +0.988** (B1, n=7,948) and **r = +0.987** (B2,
n=13,386). The two numbers come from the same physical measurement and they
agree, which is a check that the channels are real rather than defaults.

**Speed.** At idle, median |dAFR/dt| is 0.125 (B1) and 0.137 (B2) AFR/s; the 99th
percentile is 1.66 and 1.74. During the drive the peaks are **149 AFR/s (B1)** and
**245 AFR/s (B2)**. Neither sensor is lazy, and if anything bank 2 is the faster
of the two.

**One dropout.** Bank 2's upstream read exactly 0.0000 for 26 consecutive samples
at 04:01:48–04:01:49, during a deceleration. That is 0.46 % of that burst and it
happened once in 19,000 bank 2 samples across the dataset. Treated as a data
artefact.

### 4.2 Deceleration fuel cut-off — both banks' injectors seal

This is the strongest single measurement in this analysis. On overrun the PCM
shuts the injectors; a leaking injector or a lazy sensor would prevent the
reading from pegging.

**Bank 1 (passenger, 1-2-3): 9 episodes.** Longest **46.5 s** (03:49:47–03:50:33,
n=680 samples, 1784 → 940 rpm), value **29.3826 with a standard deviation of
exactly 0.00000** — every one of the 680 samples identical, at the top of the
PID's range.

**Bank 2 (driver, 4-5-6): 7 episodes.** Longest **26.6 s** (03:58:25–03:58:52,
n=412, 1788 → 1469 rpm), same value, same zero standard deviation.

Transition times, measured from the last sample below AFR 20 to the first at the
ceiling:

| | entering fuel cut | leaving fuel cut |
|---|---|---|
| B1 | 0.240 – 0.634 s (9 episodes) | 0.126 – 0.451 s |
| B2 | 0.122 – 0.601 s (7 episodes) | 0.181 – 0.603 s |

Both banks, both directions, well inside the 0.4 s response allowance that Mode 06
applied to the rise. **Leaking injectors are eliminated on both banks, on the
engine, under real manifold vacuum, repeatedly.** Both upstream sensors sweep
their full range fast in both directions.

Richest values seen while driving: **11.339 AFR (λ 0.772) on bank 1** at
03:48:58, 1580 rpm, and **11.204 AFR (λ 0.763) on bank 2** at 04:01:20, 1878 rpm
— transient tip-in enrichment, normal, and matched between banks to 0.14 AFR.

Closed-loop control during the drive, by rpm band (non-cut samples only):

| rpm | B1 λ | n | B2 λ | n |
|---|---|---|---|---|
| 500–700 | 0.992 | 57 | 1.005 | 103 |
| 700–1000 | 0.983 | 556 | 0.982 | 305 |
| 1000–1300 | 1.032 | 486 | 0.971 | 212 |
| 1300–1700 | 1.003 | 1,542 | 1.029 | 501 |
| 1700–2200 | 1.005 | 2,983 | 1.003 | 2,923 |
| 2200–3000 | 1.001 | 264 | 1.002 | 401 |
| 3000–7000 | not sampled | 0 | 0.999 | 200 |

**The wide-open-throttle mixture is missing.** The peak load event —
absolute load 96.47 %, 6832 rpm, at 04:02:28–04:02:36 — falls in a gap where
neither wideband channel was being polled (bank 1's burst ended 03:56:08,
bank 2's 04:01:59). **No claim about WOT enrichment can be made from these logs.**

### 4.3 Downstream sensors — the "Bank 1 swings twice as far" claim is refuted

The prior finding rests on these two numbers, and both are correct as far as they
go:

| Burst | Window | n | sd |
|---|---|---|---|
| Downstream B1 | **00:11:17 – 00:14:05** | 2,407 | **0.204 V** |
| Downstream B2 | **00:14:03 – 00:16:34** | 2,137 | **0.103 V** |

They are **consecutive, not simultaneous.** The app polled one sensor, then the
other. Comparing them is exactly the cross-window comparison this project has
already had to withdraw a finding over.

There are four windows in the pre-repair log where both downstream sensors were
sampled **at the same time**, plus one in each of the other three logs:

| Window | Log | n (B1 / B2) | sd B1 | sd B2 | **ratio B1/B2** | p2p B1 | p2p B2 |
|---|---|---|---|---|---|---|---|
| 22:31:50–22:32:05 | pre-repair | 35 / 34 | 0.0060 | 0.0223 | **0.27** | 0.020 | 0.090 |
| 00:11:17–00:11:27 | pre-repair | 34 / 32 | 0.2121 | 0.1669 | **1.27** | 0.640 | 0.525 |
| 00:56:46–00:57:03 | pre-repair | 32 / 32 | 0.2157 | 0.2272 | **0.95** | 0.675 | 0.665 |
| 01:05:18–01:05:36 | pre-repair | 83 / 83 | 0.2465 | 0.2136 | **1.15** | 0.685 | 0.680 |
| 03:09:43–03:23:12 | post + wipe | 53 grid pts | 0.0153 | 0.0151 | **1.01** | 0.045 | 0.054 |
| 03:46:51–04:04:26 | drive | 80 grid pts | 0.0478 | 0.0484 | **0.99** | 0.155 | 0.156 |
| 04:18:28–04:53:56 | after drive | 137 grid pts | 0.0370 | 0.0419 | **0.88** | 0.100 | 0.125 |

**In every window where the two sensors were measured together, they behave the
same.** The ratio never approaches 2. The one outlier (0.27) is a 15-second window
in which neither sensor was doing anything. Peak-to-peak — which is less sensitive
to waveform shape than standard deviation — is within 10 % in the three active
pre-repair windows.

This agrees with the PCM's own catalyst monitor, which scored bank 1 at 0.3711 and
bank 2 at 0.3633 against a 0.8359 limit — within 2 % of each other. **Two
independent lines now say the converters are matched. The bank 1 downstream
asymmetry should be struck from the suspect list.**

The one small difference that *is* consistent across the pre-repair session's
three **active** simultaneous windows: bank 1's downstream sits **0.025 to
0.060 V lower** (leaner) than bank 2's — 0.590 vs 0.650, 0.596 vs 0.621, 0.578 vs
0.629. In the fourth window, where neither sensor was doing anything, the sign
reverses (0.717 vs 0.706). Post-repair the direction is not consistent either
(0.797/0.802, 0.774/0.788, 0.771/0.759). One quantisation step of these
narrowband channels is 0.005 V, so the difference is real but tiny, and it does
not survive the repair.

### 4.4 What DID change downstream: the catalysts stopped passing the dither

This is a change nobody has recorded, and it is on **both** banks together.

| | Downstream range | p2p | Dominant period | n |
|---|---|---|---|---|
| **Pre-repair**, 00:11–00:14 (B1) | 0.145 – 0.815 V | **0.670 V** | 3.91 s | 2,407 |
| **Pre-repair**, 00:14–00:16 (B2) | 0.205 – 0.830 V | **0.625 V** | 3.22 s | 2,137 |
| **Pre-repair**, 00:48–00:55 (B1) | 0.085 – 0.875 V | **0.790 V** | 3.66 s | 809 |
| Post + wipe, 03:09–03:23 | 0.755 – 0.800 (B1), 0.735–0.790 (B2) | **0.045 / 0.054** | flat | 42 / 42 |
| Drive, 03:46–04:04 | 0.670 – 0.825 (B1), 0.675–0.840 (B2) | **0.155 / 0.156** | — | 69 / 69 |
| After drive, 04:18–04:53 | 0.755 – 0.855 (B1), 0.735–0.860 (B2) | **0.100 / 0.125** | — | 114 / 92 |

Before the valve change, both post-catalyst sensors were swinging across almost
the full narrowband range **at the same 3.2–3.9 s period as the commanded
mixture dither** — that is, the dither was passing through the converters
essentially unbuffered. Community diagnostic guidance treats a downstream sensor
that mirrors the upstream as the classic low-converter-efficiency signature. After
the valve change both sit steady at 0.74–0.86 V, which is the classic
healthy-converter signature.

**Do not read this as "the converters were bad and got better."** Converters do
not heal. Two readings are consistent with the data and this analysis cannot
separate them:

* the pre-repair mixture excursion arriving at the converters was **larger than
  what the commanded dither alone implies** — a stuck-open purge valve dumping a
  varying vapour/air stream into the manifold would do exactly that — and it
  simply overwhelmed the oxygen storage at idle flow rates; or
* the fore/aft control loop was running in a different mode with the old valve.

The PCM's own catalyst monitor, run under its proper conditions, passed both banks
at 44 % of the limit. Idle is the worst operating point at which to judge a
converter. **Recheck at 60–80 km/h cruise.**

### 4.5 The fore/aft loop works, and it works per bank

In the 00:48:48–00:55:06 window, cross-correlation on a 0.06 s grid:

| | | n | peak r | lag |
|---|---|---|---|---|
| Downstream B1 voltage | vs **STFT B1** | 4,549 | **−0.439** | **−0.60 s** (downstream lags) |
| Downstream B1 voltage | vs STFT B2 | 4,730 | +0.079 | +0.36 s |
| Downstream B1 voltage | vs engine rpm | 4,857 | −0.404 | 0.00 s |
| STFT B1 | vs STFT B2 | 4,605 | +0.349 | 0.00 s |

Bank 1's post-catalyst sensor going rich (higher voltage) is followed 0.6 s later
by bank 1's short term trim taking fuel out — correct sign, sensible delay. It has
**no relationship at all with bank 2's trim (r = +0.079)**. The secondary fuel
control loop is closed, correctly polarised, and correctly separated by bank.

---

## 5. Commanded air/fuel ratio

| | n | AFR range | **λ range** | mean λ | **amplitude (p5–p95)** | dominant period |
|---|---|---|---|---|---|---|
| Pre-repair, Park idle | 7,515 | 14.408 – 14.864 | 0.9847 – 1.0159 | **0.9967** | **±1.54 %** | **3.92 s** (0.255 Hz) |
| Post-repair | 17,418 | 14.338 – 14.959 | 0.9800 – 1.0224 | **1.0021** | **±1.58 %** | **3.28 s** (0.305 Hz) |

Median peak-to-peak over 20-second windows: **0.4488 AFR units** pre-repair
(23 windows), **0.4555** post-repair (59 windows). **The dither is unchanged by
the repair** — same amplitude to within 1.5 %.

Its period tightened from 3.92 s to 3.28 s, matching the engine-speed period
change already recorded elsewhere in this project.

The mean commanded lambda moved from **0.9967 to 1.0021** — 0.5 % leaner — which
is the direction expected when a source of unmetered fuel vapour is removed. The
dither's skew also changed: pre-repair the command sat richer than its own mean
**61.6 %** of the time; post-repair **44.0 %**.

**Measured lambda swings about twice as far as commanded** (upstream p2p 0.95 AFR
on bank 1 and 1.12 on bank 2, against a commanded 0.46). That is the normal
consequence of short-term trim being applied *on top of* the commanded ratio plus
transport delay through the manifold; it is not a sign of overshoot in a
diagnosable sense.

**±1.5 % at 0.25–0.3 Hz is the shape of fore/aft catalyst control.** Nothing in
this dataset says it is abnormal, and nothing says it is normal either — that
still needs a control sample from another 3.7.

---

## 6. Air metering

### 6.1 MAF at idle

**Pre-repair Park idle is extremely steady.** The two long blocks:

| Window | n | mean | median | sd | min | max | rpm |
|---|---|---|---|---|---|---|---|
| 00:48:40 – 00:55:05 | 681 | **2.980** | 2.970 | **0.041** | 2.83 | 3.28 | 651 |
| 00:55:19 – 00:56:18 | 103 | **2.952** | 2.950 | **0.011** | 2.93 | 2.98 | 651 |
| whole session, rpm 600–700 | 4,118 | 3.007 | **3.010** | 0.082 | 2.77 | 6.17 | 651 |

That is 1.4 % standard deviation over six minutes — the flattest channel in the
dataset. Post-repair idle MAF is higher and much less steady: eight short bursts
totalling 57 samples spread over 04:18–04:51, ranging **3.33 to 5.88 g/s**, at
605–656 rpm with intake air 38–47 °C. Log `20260905_030915` gives 3.33 g/s at
661 rpm (n=5). The post-repair figure is too sparse to compare properly against
the pre-repair one.

**Reference (searched, community source, not a Ford specification).** The
diagnostic rule of thumb is **0.8 to 1.2 g/s per litre of displacement at warm
idle**, which for 3.7 L gives **2.96 – 4.44 g/s**; and a general range of
2 – 7 g/s across passenger vehicles. Sources are cited at the end. **3.0 g/s sits
at the very bottom of the per-litre band and comfortably inside the general one.
Verdict: normal.**

### 6.2 The MAF calibration is validated at the top of its range

The WOT pull gives an independent check that does not depend on any rule of thumb.
Peak MAF **215.27 g/s at 6219 rpm**:

| Assumed IAT | baro 96 kPa | baro 97 kPa |
|---|---|---|
| 32 °C | VE 101.7 % | 100.7 % |
| 37 °C | 103.4 % | 102.3 % |
| 42 °C | 105.1 % | 104.0 % |
| 47 °C | 106.7 % | 105.6 % |

(Intake air temperature was logged at 32, 42 and 43 °C in that session, n=22;
barometric at 96–97 kPa, n=263. The table brackets the whole plausible range
rather than holding one value forward.) Across all 72 samples above 150 g/s the
median volumetric efficiency is **105.8 %**, maximum 108.3 %, over 4250–6402 rpm.

**A MAF reading systematically low cannot produce 100–108 % volumetric
efficiency.** Combined with long term trims at −0.78 % on both banks, the mass
air flow calibration is sound. This also removes the "MAF reading low" candidate
for the historic lean bias.

### 6.3 What idle VE cannot be computed

`Intake manifold absolute pressure` is not returned on this vehicle in any of the
four logs, so idle volumetric efficiency cannot be calculated. For reference: at
3.010 g/s, 651 rpm and 37.4 °C intake air, the air actually ingested corresponds
to **13.3 kPa manifold pressure at 100 % VE**, i.e. about 44 % VE if manifold
pressure at warm idle is 30 kPa or 53 % if it is 25 kPa. Both are plausible for an
engine with heavy internal EGR from cam overlap, so **this resolves nothing
without a real MAP reading.**

---

## 7. Evaporative emissions

### 7.1 Purge command and vapour pressure — the clearest before/after in the dataset

| | Pre-repair (old valve) | Post-repair (new valve) |
|---|---|---|
| Commanded purge, idle | **37.255 – 41.176 %**, only **11 distinct values in 2 h 25 min**, median 39.7 (n=7,533) | **33.3 – 50.2 %**, **23 distinct values**, stepping in 0.39 % increments, mean 47.9 (n=2,107) |
| Commanded purge, driving | not sampled | up to **70.196 %** (n=18) |
| Evap vapour pressure, idle | **−292 to −748 Pa**, mean **−602 Pa**, sustained across the whole session (n=1,500) | **−77 to −447 Pa** (n=20) |
| Evap vapour pressure, driving | not sampled | **mean −13.8 Pa**, sitting at atmosphere ±20 Pa (n=259) |

Two independent EVAP channels changed across the repair, in the same direction.

**A flat purge command is not the PCM controlling purge.** Eleven distinct values
across 7,533 samples over two and a half hours is a command that is not being
modulated. After the valve change the same channel produces 23 values and visibly
steps. The PCM is now controlling purge and was not before.

**A sustained −600 Pa in the evaporative system is unusual.** That is 0.6 kPa of
vacuum held in the tank/canister continuously for hours while the engine idles.
With a valve that seals when commanded shut, purge flow is intermittent and the
system returns to atmosphere between pulses — which is exactly what the drive log
shows post-repair (mean −13.8 Pa, hovering at zero). A valve that never fully
closes pulls the canister down continuously, which is what the pre-repair figure
looks like. **This is an independent corroboration of the stuck-open purge valve
from a channel this project has never used.**

**The canister vent is not blocked.** During the drive, with purge commanded up to
70 %, the system reached and held atmospheric pressure (0 ± 20 Pa). A restricted
vent could not do that.

**Caveat:** the post-repair vapour pressure samples are sparse (n=20, in two
clusters at 04:19 and 04:44–04:48), and by 04:44 the reading was back to −378 to
−447 Pa. That is roughly two thirds of the pre-repair level, with purge actively
commanded at 46–50 %. It may simply be the pressure drop across the vent at
higher purge duty. **This item is not fully closed.**

### 7.2 Ethanol fuel percent

| | Value | Raw byte | n | Variance |
|---|---|---|---|---|
| Pre-KAM-wipe (22:32–00:57) | **16.078 %** | 41/255 | 109 | zero |
| Post-KAM-wipe (04:01, 04:19–04:48) | **19.216 %** | 49/255 | 4 + 36 | zero |

On this platform the ethanol content is **inferred by the PCM from the oxygen
sensor feedback, not measured by a sensor.** Saudi pump fuel is normally E0, so
both readings are wrong in the same direction.

**The interesting part is that it went UP across a memory wipe.** A KAM wipe
should return an adaptive value to its calibration default and then relearn. It
did not go to zero; it went from 16.1 % to 19.2 %. Two readings are consistent
with the data:

* the value is genuinely being re-inferred and landed higher on the second pass —
  a false ethanol inference is exactly what a small unmetered-air source produces,
  and the second reading was taken shortly after the leak was fixed; or
* this PID is not actually an adaptive value on this vehicle and the two numbers
  are calibration constants that changed for another reason.

**Consequence, and it is small.** Inferred ethanol content only affects
**open-loop** fuelling — cranking, cold start, and wide open throttle. In closed
loop the O2 feedback corrects it away, which is why the trims are near zero. A
19.2 % ethanol assumption over-fuels open-loop by roughly 5 %. Nothing in the
symptom (warm idle, closed loop) is downstream of this.

**Do not replace an oxygen sensor over this number.** All four sensors have been
shown healthy here and by Mode 06.

### 7.3 Barometric pressure

**97 kPa on all 1,500 pre-repair samples with zero variance**, 96–97 during the
drive (n=263), 97 after (n=14). Jeddah is at sea level, where the number should be
near 100–101 kPa.

The zero variance is expected — Ford latches this from the MAP sensor at key-on
and at wide throttle rather than sampling it continuously — and it did read 96 in
another session, so it does update. Web search did not return a September station
pressure climatology for Jeddah, so **the true local value at those hours is
unestablished** and this remains UNCERTAIN rather than ABNORMAL.

Its practical weight is now near zero regardless: a barometric reading 3–4 kPa low
biases fuelling **lean**, and post-repair long term trims read **−0.78 % on both
banks**. There is no lean bias left for it to explain.

---

## 8. Suspect parts, ranked

### 1. EVAP purge valve — ALREADY REPLACED. Leave alone. Data now corroborates it three ways.

This analysis adds two channels that were never used to judge the old valve, and
both say it was faulty:

* **Purge command was flat** — 11 distinct values in 2 h 25 min over 7,533
  samples. After replacement, 23 values with visible 0.39 % stepping.
* **Evaporative vapour pressure sat at a sustained −602 Pa** for the whole
  pre-repair session; during the post-repair drive the system sat at atmosphere.

Plus the already-known trim change: total correction **+3.5 / +4.1 %** before,
**−0.78 / −0.78 %** after a full relearn.

**Confirming test if any doubt remains:** none needed. The item is closed on four
independent measurements.

### 2. Bank 2 (driver side, cylinders 4-5-6) fuelling — WATCH. Do not touch any part.

Bank 2's total correction ran **+1.31 to +1.38 % above bank 1** in the two long
simultaneous pre-repair blocks and **+2.33 % above** in the one short post-repair
block, while running **0.79 % below** it in the early block. Maximum magnitude
2.33 %, against a ±10 % normal band and a "<3 % between banks" rule of thumb. It
is not a fault by any threshold. It is listed only because it is not a fixed
offset and because it is the only asymmetry left after the downstream O2 claim was
refuted.

**Confirming test:** one 10-minute capture at warm Park idle with **all four**
trim channels on one screen — `Short term fuel % trim - Bank 1`,
`Long term fuel % trim - Bank 1`, `Short term fuel % trim - Bank 2`,
`Long term fuel % trim - Bank 2` — repeated on **two separate days**. If B2 − B1
lands in the same place both times, it is a real offset worth chasing (bank 2
upstream sensor bias, an exhaust leak upstream of the bank 2 sensor, or uneven
purge/PCV distribution). If it wanders, it is loop noise and the item closes.

### 3. The two long-term-trim suspension events — TEST, do not replace anything.

148 s and 104 s of long term trim reading zero at dead-steady idle, with the
session's two largest short-term excursions (−11.72 %, +9.38 %) inside the first
one. Most likely a PCM-initiated EVAP diagnostic, which would now be a *normal*
event with a working valve.

**Confirming test:** 20 minutes at warm Park idle logging
`Commanded evaporative purge` + `Evap. system vapor pressure` +
`Short term fuel % trim - Bank 1` + `Long term fuel % trim - Bank 1` together. If
purge command drops to 0 and vapour pressure falls at the moment long term trim
goes to zero, it is the EVAP monitor and the item closes. If long term trim
suspends with purge unchanged, something else is disturbing the mixture.

### 4. Inferred ethanol percent — INVESTIGATE cheaply, replace nothing.

19.2 % on E0 fuel, up from 16.1 % across a memory wipe.

**Confirming test:** read `Ethanol fuel percent` with **FORScan** (a second tool)
to check that Car Scanner is not reporting a default; then read it again after the
next full tank of the same fuel. A value that moves with refuelling is a live
inference; one that never moves is a constant. Either way this only affects
open-loop fuelling and cannot cause a warm-idle symptom.

### 5. Barometric pressure — LEAVE ALONE.

97 kPa against a sea-level expectation near 100–101. It updates (96 was seen), the
error direction is lean, and there is no lean bias left. Not worth a part or a
test.

### 6. CLOSED — remove from the suspect list entirely.

| Item | Why it is closed |
|---|---|
| **Bank 1 downstream O2 / bank 1 catalyst asymmetry** | Refuted on seven simultaneous windows across four logs; sd ratio 0.88–1.27, never near 2. Mode 06 agrees (0.3711 vs 0.3633). |
| **Leaking injectors, either bank** | Both banks peg at the PID ceiling on overrun with standard deviation exactly 0.00000, for 46.5 s (B1, n=680) and 26.6 s (B2, n=412). |
| **Either upstream oxygen sensor lazy, biased or dead** | Full range, sub-0.6 s transitions in both directions on 16 fuel-cut episodes, AFR/pump-current correlation +0.99, banks matched to 0.007 AFR on 6,695 paired samples. |
| **MAF reading low** | 100–108 % volumetric efficiency at WOT on 72 samples. |
| **Restricted intake / air filter** | Same measurement. |
| **Unmetered air anywhere (PCV, booster, gaskets, injector O-rings)** | Long term trim −0.781 % on all 1,535 and 1,470 post-relearn samples. There is no lean bias left to attribute. |
| **Commanded mixture dither being abnormal, or changed by the repair** | ±1.54 % before, ±1.58 % after; 20 s peak-to-peak 0.4488 vs 0.4555 AFR. |

---

## 9. What could NOT be determined, and the capture that would settle it

| Question | Why the data cannot answer it | Capture that would |
|---|---|---|
| **Fuel trim at cruise, acceleration and overrun** | Every trim sample in all four logs is at standstill idle. The drive log was not polling the trim channels. | 20 minutes of driving with `Short term fuel % trim - Bank 1` + `Long term fuel % trim - Bank 1` on one screen, then repeat for bank 2. Ford indexes long term trim by load — the cruise cell has never been read on this truck. |
| **Wide open throttle mixture** | Neither wideband was being polled during the 04:02:28–04:02:36 pull. | One WOT pull with `O2S1 air:fuel` **and** `O2S5 air:fuel` on the graph. Expect λ 0.80–0.88. |
| **Whether the bank 2 trim offset is real** | It changes sign inside one session and the largest value rests on 31 seconds. | All four trim channels on one screen, warm Park idle, 10 minutes, on two separate days. |
| **Whether the LTFT suspension events are the EVAP monitor** | Purge command and vapour pressure were not polled in either window. | `Commanded evaporative purge` + `Evap. system vapor pressure` + `Short term fuel % trim - Bank 1` + `Long term fuel % trim - Bank 1`, 20 min at idle. |
| **Whether the fuel system was actually in closed loop** | `Fuel System Status` appears in no log. | Add `Fuel System Status` to any idle capture. It is a one-line confirmation. |
| **Idle volumetric efficiency — is 3.0 g/s genuinely low?** | `Intake manifold absolute pressure` returns nothing on this vehicle. Car Scanner does return it on the owner's 2023 truck. | Retry `Intake manifold absolute pressure` (and `Intake manifold absolute pressure high resolution`) at warm idle. With MAP, MAF, rpm and IAT together, idle VE is arithmetic. |
| **Whether the catalysts stopped passing the dither because of the valve or for another reason** | Both post-catalyst sensors were sampled at only 2.2–2.8 Hz post-repair, in short bursts. | `Oxygen sensor 2 Bank 1 Voltage` + `Oxygen sensor 2 Bank 2 Voltage` **together**, 5 minutes at warm idle and 5 minutes at 60–80 km/h steady cruise. Cruise is the only condition where a converter can be judged. |
| **Whether ±1.5 % commanded dither is normal for this engine** | No control sample exists. | `Fuel/Air commanded equivalence ratio` for 3 minutes at warm idle on **any other 3.7 or 3.5 Cyclone**. |
| **Fuel rail pressure** | No pressure PID in any log; this engine has no OBD-accessible fuel pressure sensor in the returned set. | Mechanical gauge, if fuelling ever needs revisiting. It does not today. |
| **True local barometric pressure at Jeddah** | Web search returned no September station-pressure climatology. | Read the local METAR (OEJN) at the hour of the next capture. |

---

## 10. Sources consulted

Reference values in this document that did not come from the truck are all
**community/forum or general diagnostic sources, not Ford specifications**, and
are marked as such above.

* MAF idle rule of thumb (0.8–1.2 g/s per litre; general 2–7 g/s) —
  [Engineer Fix / EngineerSkill](https://engineerskill.blog/maf-sensor-readings-healthy-engine),
  [Motorverso](https://www.motorverso.com/what-should-maf-read-at-idle/)
* Fuel trim acceptable ranges (±5 % STFT, ±10 % LTFT; ±25 % sets a code) —
  [Motor Magazine](https://www.motor.com/magazine-summary/fuel-trimming-diagnostic-time/),
  [GTC](https://gtc.ca/blog/long-term-fuel-trim-and-short-trim-fuel-trim/)
* Downstream O2 behaviour as a converter indicator (steady = good, mirroring the
  upstream = poor efficiency) —
  [Brake & Front End](https://www.brakeandfrontend.com/tech-tip-oxygen-sensors-monitoring-converter-efficiency/),
  [Innova](https://www.innova.com/blogs/fix-advices/reading-o2-sensor-voltage-ranges-in-live-data)
* VIN 8th digit `M` = 3.7 L V6 on a 2014 F-150 — multiple parts catalogues; **flex-fuel
  status for this specific build was NOT confirmed**, so the ethanol PID's meaning
  on this vehicle remains partly open.
* Jeddah September station pressure — **searched, not found.** The barometric item
  is left UNCERTAIN for that reason.
