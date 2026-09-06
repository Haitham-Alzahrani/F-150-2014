# Ignition, spark strategy, knock control and combustion quality

2014 F-150 XL · 3.7 L V6 Ti-VCT (Cyclone) · 6R80 · 131,000 km · Jeddah
Analysis date 2026-09-06. Source: four Car Scanner logs in `data/carscanner/`
(2026-09-04 22:24 → 2026-09-05 05:07) plus `data/mode06.csv`.

**Bank convention used throughout: Bank 1 = passenger side = cylinders 1, 2 and 3.
Bank 2 = driver side = cylinders 4, 5 and 6.** Written out in full every time it
matters.

**Method.** Logs loaded with `carscanner_lib.load`, which keeps every channel on
its own true sample times. **Nothing was forward-filled.** Where two channels had
to be compared they were interpolated onto a common 0.06 s grid with
`on_grid(..., max_gap=0.3–0.5 s)`, which returns NaN across any silence longer
than the gap, and every cross-correlation uses only index pairs finite in both
series. Car Scanner polls channels round-robin in bursts, so **which channels were
on screen together is the binding constraint on this analysis** — that is stated
explicitly wherever it bit.

---

## 1. Summary

| Parameter | Measured | Reference | Verdict |
|---|---|---|---|
| Idle spark, Park, warm, standstill | **12.05° BTDC** pooled mean (sd 1.14°, median 12.0°), **n = 11,456**; per-window means 11.89 – 12.46° | Community: 13–17° at 650 rpm in Park (forum figure, **not** a Ford spec). Project guide: 16–22° (Level 3 heuristic, uncorroborated) | **NORMAL — reference withdrawn.** See §3.2 |
| Idle spark, Drive, standstill | **12.80°** mean (sd 0.85°), n = 1,349 samples | Project guide 12–17° (Level 3) | **NORMAL** |
| Idle spark swing (10 s peak-to-peak) | **3.0 – 3.5°** in steady windows; 13.5° in the one high-disturbance early window | Project guide: 3–5° P-P typical controlled swing (Level 3) | **NORMAL** |
| Spark vs engine speed, lag | **spark LAGS rpm by 0.06 – 0.12 s** (1–2 sample steps), 6 independent windows | A governor lags its disturbance | **NORMAL — prior finding independently reproduced** |
| Spark vs engine speed, correlation | **r = −0.64 to −0.93**, 6 windows, n = 630 – 5,365 paired grid points each | — | **NORMAL (correcting, not causing)** |
| Governor gain | **−0.073 to −0.116 °/rpm** in Park; **−0.143 °/rpm** in Drive | — | **NORMAL** |
| Total spark authority exercised | **−7.0° to +40.0°** (47° span), 16,009 samples, 0.5° quantisation | A healthy PCM uses deep retard on decel and full advance at light load | **NORMAL — authority is not the constraint** |
| Knock retard | **0.0° in every sample. n = 38, ~26 s of coverage, all at Park idle, none under load** | 0° expected at idle | **UNCERTAIN — the number is right, the coverage is almost nil.** See §3.6 |
| Knock retard at wide open throttle | **not logged — the channel was not on screen during either WOT pull** | — | **NOT DETERMINED** |
| Spark at wide open throttle | **not logged — same reason** | — | **NOT DETERMINED** |
| Spark ~30 s after two WOT pulls (87 km/h cruise) | **33.0 – 40.0°**, mean 37.05°, n = 10, 1,620–1,682 rpm | Full light-load cruise advance | **NORMAL — no residual retard** |
| Learned octane (Ford OAR) | **−0.5999 before the KAM wipe** (n = 32) → **0** (n = 5) → **+0.0815** (n = 30) | OAR: −1 = best fuel quality, +1 = worst, 0 = reset value | **NORMAL — the pre-wipe −0.60 is a good-fuel verdict.** See §3.7 |
| Mode 06 misfire, current drive cycle | cyl 1 **0**, 2 **0**, 3 **0**, 4 **2**, 5 **0**, 6 **1** (TID $0C) | Counter range 0 – 65,535; the rate tests below are the pass/fail | **NORMAL** |
| Mode 06 misfire, 10-cycle EWMA | **0 on all six cylinders** (TID $0B) | — | **NORMAL** |
| Mode 06 misfire rate, catalyst-damage window | **0.000 % on all six and on the engine total** (TID $80) | limit 30.976 % | **NORMAL** |
| Mode 06 misfire rate, emissions window | **0.000 % on all six and on the engine total** (TID $81) | limit 0.949 % | **NORMAL** |
| Mode 06 MID $A1 TID $84 = 527.198 | **identified: inferred catalyst mid-bed temperature, °C** | limit 0 – 918.874 °C | **NORMAL — the [VERIFY] item in CLAUDE.md is closed** |
| Mode 06 VVT error | Bank 1 **0.06°**, Bank 2 **0.05°** | limit 20° | **NORMAL — cam-to-crank reference is sound** |
| Half-order (once-per-engine-cycle) content in engine speed | **present at exactly rpm/120 in every idle window**, amplitude **0.14 – 0.32 rpm**, 2.1 – 6.0× the local noise floor | No control sample exists | **UNCERTAIN — real signal, ambiguous cause.** See §3.9 |
| First-order (once-per-revolution) content in engine speed | **absent** — the alias frequency shows 0.9 – 1.8× floor, i.e. nothing | A crank reluctor defect would live here | **NORMAL — weak evidence against the crank-signal hypothesis** |
| Ethanol fuel percent (inferred) | **16.08 %** pre-wipe, **19.22 %** post-wipe, on E0 pump fuel | Saudi pump petrol is normally E0 | **ABNORMAL as a reading — consequence unproven.** See §3.10 |

**Bottom line for this domain: the ignition system produces a clean bill of
health, and the one measurement that would have complicated it — spark and knock
retard at wide open throttle — was never captured.**

---

## 2. Data inventory for this domain

| Log | Clock | `Timing advance (°)` | `Knock retard (°)` | `Learned octane ()` |
|---|---|---|---|---|
| `2026-09-04 22-23-38.zip` (pre-repair) | 22:24 – 01:35 | n = 5,550, 970 s in 30 bursts | n = 21, 14 s | n = 32, 19 s |
| `20260905_030915.csv.gz` | 03:09 – 03:30 | n = 6,583, 443 s | n = 5, 4 s | n = 5, 4 s |
| `20260905_034051.csv.gz` (the drive + WOT) | 03:40 – 04:07 | **n = 108, 26 s only** | **absent** | **absent** |
| `20260905_041723.csv.gz` | 04:17 – 05:07 | n = 3,768, 300 s | n = 12, 8 s | n = 30, 15 s |

**16,009 timing-advance samples in total. 38 knock-retard samples. 67 learned-octane samples.**

Timing advance is quantised to **0.5°** and takes 53 distinct values across the
whole dataset — consistent with SAE Mode 01 PID $0E (range −64 to +63.5°,
0.5° resolution), which is what Car Scanner's "Timing advance" is.

---

## 3. Detailed findings

### 3.1 The spark map

Every operating point where spark was actually sampled. Engine speed paired to
each spark sample by nearest real sample within 0.15 s; **no interpolation across
a poll gap.**

| Condition | Window | n | Engine speed | Spark, min…max | Spark mean |
|---|---|---|---|---|---|
| Park idle, warm, standstill | 22:51:05–22:54:25 | 559 | 652 ± 13 | 6.0 … 19.5 | **12.46** |
| Park idle, warm, standstill | 23:22:02–23:26:04 | 3,738 | 652 ± 11 | 6.0 … 16.0 | **11.89** |
| Park idle, warm, standstill | 00:48:47–00:55:06 | 810 | 652 ± 8 | 6.5 … 15.0 | **12.23** |
| Park idle, warm, standstill | 00:55:26–00:56:24 | 120 | 651 ± 6 | 10.5 … 13.5 | **12.04** |
| **In-gear (Drive) idle, standstill** | 03:23:10–03:24:43 | 1,349 | 550.4 ± 4.4 | 8.5 … 15.0 | **12.80** |
| Park idle, warm, standstill | 03:24:52–03:30:15 | 5,055 | 652.1 ± 9.6 | 7.0 … 16.5 | **12.16** |
| Park idle (throttle being blipped by hand) | 04:46:38–04:48:32 | 1,582 | 655 (625–699) | 7.0 … 21.0 | 11.88 |
| Park idle, throttle held at 9.44° | 04:51:28–04:53:56 | 2,108 | 654 (633–676) | 10.0 … 14.5 | **11.98** |
| Idle, immediately before the drive | 03:46:47–03:46:58 | 61 | 620–688 | 7.5 … 19.0 | 13.43 |
| Rising, 663 → 1,193 rpm | 03:46:58–03:47:02 | 16 | 663–1,193 | 3.5 … 21.5 | 14.00 |
| **Light load, 1,248 → 1,631 rpm** | 03:47:02–03:47:04 | 9 | 1,248–1,631 | **30.0 … 39.5** | **35.44** |
| **Decelerating to idle, 1,629 → 746 rpm** | 03:47:04–03:47:08 | 12 | 746–1,629 | **29.0 … −7.0** | −0.29 |
| **Cruise 87 km/h, ~30 s after two WOT pulls** | 04:04:06–04:04:10 | 10 | 1,620–1,682 | **33.0 … 40.0** | **37.05** |
| **Wide open throttle, 6,832 and 6,402 rpm** | 04:02:29–04:02:39, 04:03:30–04:03:41 | **0** | — | **not sampled** | — |

What the PCM does, read off that table:

- **At idle it holds about 12° and trims around it.** Throttle is static, cam
  phasers are parked, so spark is the fast lever, exactly as the project already
  concluded.
- **Off idle at light load it goes to full advance** — 30–40° by 1,250–1,700 rpm.
  That is a normal naturally-aspirated part-load advance and it is where MBT
  lives at low load.
- **On a closing throttle it retards hard to −7°** to kill torque and stop the
  idle flaring. This is the idle-entry / dashpot torque-reduction function and
  it is working.
- **At wide open throttle we have no data at all.**

### 3.2 Settling the idle-spark question — the reference is wrong, not the truck

The open question was whether ~12.0° at Park idle is low against the project
guide's 16–22°.

**What the guide actually is.** `docs/ford-3.7-cyclone-6r80-guide.md` §2E labels
its table "Typical Observed Calibration Range — **Not Factory Specification**",
Evidence Level 3, and its own §10 records that web search could not corroborate
it. Its own prose sentence one line above the table gives a *wider* range —
"approximately 12–22° BTDC depending on load state" — which this truck sits
inside.

**What searching found.** No Ford specification exists to compare against, and
that is a substantive result rather than a failure:

- Ford's own service position on coil-on-plug engines is that **ignition timing
  is not adjustable and is computed by the PCM**; there is no serviceable idle
  timing figure for a 2014 3.7 the way there is for a distributor engine. Any
  number quoted for "idle spark on a modern Ford" is somebody's observation, not
  a specification.
- The nearest community figure found is **13–17° BTDC at 650 rpm in Park**
  ([ford-trucks.com timing advance thread](https://www.ford-trucks.com/forums/1450485-timing-advance-numbers.html),
  surfaced via search; **community figure, not Ford**). This truck's per-window
  means of 11.89 – 12.46° sit **0.5 to 1.1 degrees below the bottom of that
  band** — one to two quantisation steps of the PID.
- Other Ford owners report *lower* idle spark still — 5–6° on some scan-tool
  readouts — but those threads are confounded by tools that report "spark
  advance" and "ignition timing" as two different numbers, so they are not
  comparable.

**The guide's table is also internally inconsistent with this vehicle in a way
that discredits it.** It expects Park (16–22°) to run **more** advance than Drive
(12–17°). This truck does the opposite, measured minutes apart in the same
session on the same engine: **Drive 12.80° at 550 rpm (n = 1,349) versus Park
12.16° at 652 rpm (n = 5,055).** In gear the engine is loaded by the converter
and running slower, and the PCM gives it slightly *more* advance. That is the
physically expected direction. A reference whose ordering is backwards for the
vehicle it describes cannot be used to condemn an absolute value.

**Verdict: 12.0° at warm Park idle on this engine is NORMAL and the 16–22°
expectation should be deleted from the project's working assumptions.** The
reasons are (a) there is no Ford specification to be below, (b) the community
figure is 13–17° and being about one degree under it is inside the spread of how
different tools, calibrations and idle speeds report, (c) the spark *behaviour* — swing,
gain, phase, authority — is textbook in every respect measured below, and
(d) **the engine shows zero knock retard and a learned-octane value that says
the PCM thinks the fuel is good, which is the opposite of what an engine forced
to run retarded looks like.**

If the timing were genuinely low for a reason, the cause would have to be knock
(it is not — §3.6, §3.7), an EGR/dilution correction (there is no external EGR
and the phasers are parked, VVT error 0.05–0.06° in Mode 06), or a hot-air
correction. Intake air temperature during these idles was **36–56 °C** and
ambient 32–37 °C. A charge-temperature spark correction of a degree or two at
those intake temperatures is normal calibration behaviour and would account for
sitting at the bottom of a community range in Jeddah in September. Marked as
**plausible mechanism, not measured** — the log has no way to separate a
temperature correction from the base table.

### 3.3 Spark lags engine speed — independently reproduced

The prior project finding (spark lags rpm by 0.10 s, r = −0.84 to −0.91) was
re-derived from scratch here with a different pairing routine and a NaN-aware
correlation that never lets an interpolated value cross a poll gap.

| Log | Window | n grid points | Condition | Peak r | at lag |
|---|---|---|---|---|---|
| pre-repair zip | 22:51:05–22:54:25 | 3,297 | Park idle | **−0.932** | **−0.06 s** |
| pre-repair zip | 23:22:02–23:26:04 | 3,964 | Park idle | **−0.885** | **−0.12 s** |
| pre-repair zip | 00:48:47–00:55:06 | 4,517 | Park idle | **−0.794** | **−0.12 s** |
| pre-repair zip | 00:55:26–00:56:24 | 630 | Park idle | −0.709 | −0.12 s |
| 030915 | 03:23:10–03:24:43 | 1,498 | **Drive idle** | **−0.763** | **−0.12 s** |
| 030915 | 03:24:52–03:30:15 | 5,365 | Park idle | −0.640 | −0.12 s |

Negative lag means spark must be shifted *backwards* to line up with engine
speed — **spark comes after.** One grid step is 0.06 s, so "0.06–0.12 s" is one
to two sample intervals and the honest statement is **spark follows engine speed
by about a tenth of a second.** Confirmed. The sign is negative in all six
windows: rpm up, spark pulled back.

**Governor gain.** Regressing spark(t) on rpm(t − 0.12 s):

| Window | n | Condition | °/rpm | °/100 rpm | r |
|---|---|---|---|---|---|
| 22:51:05–22:54:25 | 3,298 | Park | −0.1163 | **−11.6** | −0.927 |
| 23:22:02–23:26:04 | 3,961 | Park | −0.0794 | **−7.9** | −0.885 |
| 00:48:47–00:55:06 | 4,485 | Park | −0.0729 | **−7.3** | −0.794 |
| 03:23:10–03:24:43 | 1,602 | **Drive** | −0.1426 | **−14.3** | −0.708 |
| 03:24:52–03:30:15 | 5,410 | Park | −0.0796 | −8.0 | −0.629 |

Roughly **8 degrees of spark per 100 rpm of error in Park, 14 in Drive.** The
higher gain in gear is what you would want — in gear the engine is loaded and
low, so the same rpm error is a larger fractional error.

**A useful cross-check on "is spark following or leading".** In the earliest
window (22:51, coolant 82 °C) the rpm swing was largest and the spark swing was
largest with it: spark sd 1.65° against rpm sd 13.1°. Half an hour later (23:22,
coolant 96 °C) **both had halved together** — spark sd 0.97° against rpm sd
10.8°, and by 00:48 spark sd 0.76° against rpm sd 8.3°. The ratio barely moves.
**The spark swing is proportional to the rpm swing at a nearly constant gain.
That is a follower, not a driver** — a spark-driven oscillation would not
politely scale itself to the disturbance it was supposedly creating.

### 3.4 NEW — commanded air/fuel leads spark by 0.30 s, exactly as predicted

The project has never measured spark against commanded air/fuel directly,
because Car Scanner rarely had both on screen. **It did, once:** log
`20260905_041723.csv.gz`, 04:51:28–04:53:56, both channels dense, Park idle at
654 rpm with the throttle held perfectly still at 9.44°.

| | n | Result |
|---|---|---|
| Commanded AFR vs spark, 04:51:28–04:53:56 (throttle static) | **2,114** | **r = +0.633, commanded AFR LEADS spark by +0.30 s** |
| Commanded AFR vs spark, 04:46:38–04:48:32 (throttle being blipped) | 1,637 | confused: +0.42 at +0.12 s, −0.49 at +1.38 s — window contaminated, discard |

**The clean window confirms the project's causal chain to within one sample
interval.** The chain says commanded AFR leads rpm by ~+0.15 s and spark lags rpm
by ~0.12 s, so commanded AFR should lead spark by ~0.27 s with a positive sign
(leaner command → rpm dip → spark advanced). **Measured: +0.30 s, r = +0.633.**

It also discriminates between two readings of the data that had not been
separated. If the PCM were driving spark and the fuel dither from the same
internal scheduler, spark would correlate best with the dither. It does not:
**spark correlates with engine speed at |r| = 0.88 and with commanded air/fuel at
only 0.63.** Spark is a function of engine speed, not a co-commanded output.

### 3.5 Spark authority is not the constraint — this corrects CLAUDE.md

CLAUDE.md currently says of the idle governor: *"its authority is tiny: 1.75°
peak-to-peak, ±0.9° about the mean."*

**That conflates authority with applied correction.** In this same dataset the
PCM took spark to **−7.0°** on a closing throttle and to **+40.0°** at light
cruise. **The authority is 47 degrees and the PCM demonstrably uses all of it.**
What is small is the *correction it chooses to apply* against the idle
oscillation — 1.75° cycle-averaged, 3.0–3.5° instantaneous over 10 s.

That is a different and more interesting statement. The governor is not
saturated, not clipped and not out of range: the spark distribution at Park idle
is smooth and unimodal: pooling every warm Park-idle sample across all three
logs that have them, **n = 11,456, mean 12.05°, sd 1.14°, mode 12.0° (2,111
samples), 5th percentile 10.5°, median 12.0°, 95th percentile 14.0°, with only
0.48 % of samples below 9° and 0.17 % above 16° — and no pile-up at any limit.** **The PCM has plenty of
spark left and is choosing not to spend it.** That is a gain and bandwidth
choice in the idle calibration, not a fault, and it means "the governor cannot
cancel the swing" should be restated as "the governor is not tuned to cancel a
swing this slow."

### 3.6 Knock retard — the right answer on almost no evidence

**Every knock retard sample in the entire dataset is 0.0°.** n = 38 across three
logs.

That is a true statement and a nearly worthless one:

- **Total coverage is about 26 seconds** out of 6 hours 43 minutes of logging.
- **Every one of the 38 samples was taken at Park idle**, where a 3.7 at 12°
  advance and ~30 kPa manifold pressure physically cannot knock.
- **The channel was not present at all in `20260905_034051.csv.gz`** — the log
  containing both wide-open-throttle pulls (6,832 rpm at 04:02:29–04:02:39 and
  6,402 rpm at 04:03:30–04:03:41, 96.5 % absolute load, 215 g/s MAF).

**Knock retard has never been observed under load on this truck.** Recording it
at idle proves nothing; it is the one condition where the answer is guaranteed.

The two indirect pieces of evidence that *do* bear on knock:

1. **30 seconds after two full-throttle pulls to the rev limiter, at 87 km/h and
   1,620–1,682 rpm, the PCM was running 33–40° of advance** (n = 10). An engine
   that had just been knocking would still be holding some borrowed retard at
   that point. It was not.
2. **The learned octane value the engine reached over its whole service life was
   −0.60**, which on Ford's scale is a good-fuel verdict (§3.7). A chronically
   knocking engine drives that number the other way.

**Verdict: UNCERTAIN, leaning strongly to normal.** The finding is not "knock
retard is zero", it is "knock retard has never been measured where it could be
non-zero."

### 3.7 "Learned octane" — this is Ford's Octane Adjust Ratio, and −0.60 is a good number

**Three values, in time order:**

| Log | Clock | Value | n | Context |
|---|---|---|---|---|
| pre-repair zip | 22:32 and 00:58 | **−0.599854** | 32 | Learned over the owner's whole ownership |
| 030915 | 03:09 | **0.000000** | 5 | ~95 min after the KAM wipe at ~01:32 |
| 041723 | 04:20, 04:28, 04:51 | **+0.081482** | 30 | After the 03:52–04:05 drive, which included two WOT pulls |

**The encoding identifies the PID.** Both non-zero values are exact multiples of
2⁻¹⁴: −0.599854 × 16384 = **−9828.000** and +0.0814819 × 16384 = **+1335.000**.
That is a signed 16-bit Q14 quantity, i.e. a ratio carried on a ±1.0 scale — the
shape of Ford's Octane Adjust Ratio, not a coincidence.

**The convention.** Searching settles this for a 2014 naturally-aspirated engine:

- Ford's **Octane Adjust Ratio (OAR)** starts at **0.0** and learns in two
  directions. **Optimal fuel quality and knock feedback drive it toward −1.0;
  sub-optimal drive it toward +1.0.** −1.0 is normally only reached on premium
  93 AKI; +1.0 corresponds to the minimum octane Ford recommends
  ([COBB Tuning, Octane Adjust Ratio](https://www.cobbtuning.com/ford-ecoboost-and-the-octane-adjust-ratio-monitor/);
  [COBB support wiki](https://cobbtuning.atlassian.net/wiki/spaces/PRS/pages/62357561/Octane+Adjust+Ratio+(OAR)+and+How+it+works+for+Ford+Vehicles);
  **tuner documentation, not a Ford publication**).
- **Knock Octane Modifier (KOM) is the same memory with the sign inverted**, and
  KOM appears on **2018-and-later** EcoBoost calibrations
  ([Mustang EcoBoost forum, KOM/OAR](https://www.mustangecoboost.net/threads/knock-octane-modifier-kom-aka-octane-adjust-ratio-oar-stuck-at-1-00-on-cobb-accessport.21259/)).
  **A 2014 F-150 predates KOM, so the OAR convention applies.**
- The PID is **not EcoBoost-only.** It is reported present on **2010–2015 Ford
  and Lincoln gasoline models** under names including *Inferred Octane*,
  *Octane_Ratio*, *Learned Relative Octane Adjust* and *OAR*
  ([FORScan forum, Learned Relative Octane Adjust](https://forscan.org/forum/viewtopic.php?t=169);
  [f150forum, Display Octane Adjustment Ratio in FORScan](https://www.f150forum.com/f129/display-octane-adjustment-ratio-forscan-547929/)).
  **Community sourcing; no Ford document was reachable.**

**Reading this truck's numbers on that convention:**

- **−0.5999 is a good result.** The PCM had learned, over thousands of
  kilometres of the owner's 95 RON from the same station, that the fuel is
  roughly 60 % of the way toward the best-fuel extreme. **An engine with a knock
  problem, bad fuel, carbon deposits raising compression, or a failing knock
  sensor would sit positive.** This is the single strongest piece of evidence in
  the ignition domain that the combustion side of this engine is healthy, and it
  is a long-integration result that no single measurement session can fake.
- **0.000 immediately after the KAM wipe is the documented reset value** — a
  clean confirmation that the wipe did what it was supposed to.
- **+0.0815 is early relearn, not a knock verdict.** OAR only learns above idle
  with the engine warm and load above roughly 0.375, and the post-wipe period
  was almost entirely Park idling; the only qualifying driving was the ~13-minute
  run at 03:52–04:05. **+0.08 out of a 2.0-unit range is 4 %, one small step from
  zero.**

**The direction is worth a note, though.** It moved *positive* across a drive
containing two full-throttle pulls to 6,832 rpm in 33 °C ambient with 47 °C
intake air. That is consistent with the knock system seeing something at wide
open throttle — and **knock retard was not being logged during those pulls**, so
we cannot tell whether it did. Marked **speculation.** The test is in §5.

**Open item for the owner:** re-read Learned octane after 500–1,000 km of normal
driving. **If it works back toward −0.5 or −0.6, the fuel and the combustion
chamber are fine and this line closes permanently. If it settles positive, the
PCM is now inferring worse fuel quality than it did before the wipe, and that is
a real change that needs the WOT knock capture in §5.**

### 3.8 Mode 06, fully interpreted

`data/mode06.csv`, read 2026-09-05 04:36, **before** the KAM wipe cleared it.

**Test identifications, from Ford's OBD System Operation Summary as surfaced by
search ([Ford OBDSM608 / OBDSM1900](http://www.fordservicecontent.com/ford_content/catalog/motorcraft/OBDSM608.pdf) —
the PDFs themselves were unreachable from this environment, so these are search-
surfaced definitions of a Ford document, not a direct read):**

| TID | Meaning | Units |
|---|---|---|
| $0B (MID $A2–$A7) | EWMA misfire counts, last 10 driving cycles | events |
| $0C (MID $A2–$A7) | Misfire counts, last/current driving cycle | events |
| $80 | Misfire rate vs **catalyst-damage** threshold, updated every 200 revolutions | % |
| $81 | Misfire rate vs **emissions** threshold, updated every 1,000 revolutions | % |
| $84 (MID $A1 only) | **Inferred catalyst mid-bed temperature** | °C |

**Per-cylinder misfire.** MID $A2 = cylinder 1 through MID $A7 = cylinder 6:

| Cylinder | Bank | $0C (this drive cycle) | $0B (10-cycle EWMA) | $80 (cat-damage rate, limit 30.976 %) | $81 (emissions rate, limit 0.949 %) |
|---|---|---|---|---|---|
| 1 | Bank 1, passenger side | 0 | 0 | 0.000 | 0.000 |
| 2 | Bank 1, passenger side | 0 | 0 | 0.000 | 0.000 |
| 3 | Bank 1, passenger side | 0 | 0 | 0.000 | 0.000 |
| 4 | **Bank 2, driver side** | **2** | 0 | 0.000 | 0.000 |
| 5 | Bank 2, driver side | 0 | 0 | 0.000 | 0.000 |
| 6 | **Bank 2, driver side** | **1** | 0 | 0.000 | 0.000 |
| Engine total (MID $A1) | — | — | — | 0.000 | 0.000 |

**Interpretation.**

- **Three events, both cylinders on Bank 2 (driver side).** That looks like a
  pattern until it is put in scale. The drive cycle those counts came from ran
  roughly 17 minutes at a mean 1,722 rpm — about **29,000 crank revolutions,
  ~88,000 firing events.** Three events is **0.003 %**, about **280× below the
  emissions threshold** the PCM itself applies.
- **Both rate windows read exactly 0.000 %** for every cylinder and for the
  engine total. The 200-revolution and 1,000-revolution rate calculations never
  registered anything at all — meaning the three events were never close enough
  together in time to make a rate.
- **The 10-cycle EWMA is 0 on all six.** Nothing persisted across drive cycles.
- **The most likely source of the three counts is the rev limiter.** That drive
  contained two pulls to **6,832 and 6,402 rpm**. The limiter cuts fuel and
  spark, and the misfire monitor can and does log the resulting rough combustion
  events. Two pulls, three events.
- **A cylinder that was genuinely weak enough to be felt in a cab would not
  produce 3 events in 88,000. It would produce hundreds and it would put a number
  in $80 or $81.**

**Verdict: the per-cylinder misfire data is clean and the single-weak-cylinder
hypothesis stays eliminated.** The Bank 2 (driver side) clustering is not
significant at n = 3.

**Two other Mode 06 results that belong to this domain:**

- **VVT monitor, TID $85: Bank 1 = 0.06°, Bank 2 = 0.05°, against a 20° limit.**
  That is **0.3 % of allowance** and it is the strongest evidence in the whole
  dataset that the **cam-to-crank reference is intact** — which matters here
  because spark is scheduled off that reference. Timing chain stretch, a
  slipped phaser or a degraded cam/crank correlation would show up here first.
- **MID $A1 TID $84 = 527.198 °C** of a 0–918.874 °C range, PASSED. This is the
  inferred catalyst mid-bed temperature, not a fault metric — **the "only value
  neither near zero nor matched between banks" note in CLAUDE.md can be
  closed.** It is a temperature; there is nothing for it to match.

### 3.9 NEW — a half-order component exists in engine speed, and it is not the crank sensor

Half engine order is **once per complete four-stroke cycle**, and in the
crankshaft-speed literature it is the specific harmonic used to detect a cylinder
contributing less than the others
([ASME, *The Frequency Analysis of the Crankshaft's Speed Variation*](https://asmedigitalcollection.asme.org/gasturbinespower/article/123/2/428/451059/The-Frequency-Analysis-of-the-Crankshaft-s-Speed);
[SAE 2001-01-1007](https://saemobilus.sae.org/papers/quantifying-relationships-crankshafts-speed-variation-gas-pressure-torque-2001-01-1007)).
At 652 rpm it is **5.433 Hz**, which is below the 8.33 Hz Nyquist of a 16.67 Hz
log and therefore visible. Nobody in this project had looked.

**It is there, in every warm idle window, at exactly rpm/120.** Welch PSD,
120 s and 30 s segments, 50 % overlap, Hanning, amplitude calibrated against a
synthetic sinusoid:

| Window | segments | mean rpm | predicted rpm/120 | peak found at | peak/floor | amplitude |
|---|---|---|---|---|---|---|
| pre-repair Park idle, 22:51:05–23:26:04 | **122 × 30 s**, n = 30,848 | 652.1 | **5.434 Hz** | **5.433 Hz** | 4.28× | 0.300 rpm |
| post-repair Park idle, 03:24:52–03:30:15 | 38 × 30 s, n = 5,230 | 652.0 | 5.433 Hz | **5.433 Hz** | 3.57× | 0.267 rpm |
| **Drive idle, 03:23:10–03:24:43** | 8 × 30 s, n = 1,446 | **550.4** | **4.586 Hz** | **4.600 Hz** | 6.63× | 0.280 rpm |

**The peak moves with engine speed.** In Park it is at 5.433 Hz and there is
nothing at 4.6 Hz. Minutes later in Drive at 550 rpm it is at 4.600 Hz and there
is nothing at 5.433 Hz (0.64× floor). **A fixed artefact of the app, the sample
rate or the filter cannot do that.** Across thirteen separate warm Park-idle
windows the peak lands between **5.425 and 5.450 Hz** against predictions of
**5.422 – 5.446 Hz** in twelve of them — inside one FFT bin. The thirteenth
(00:11:09–00:16:22) put its maximum at 4.867 Hz instead, and it is also the
window with the weakest peak in the set (2.49× floor) — the line was buried
there, not moved.

**Amplitude: 0.14 to 0.32 rpm zero-to-peak**, against a hunt fundamental of
7.2–12.8 rpm in the same windows. **The half-order component is 2–3 % of the
hunt** and about 0.04 % of engine speed. It is only recoverable at all because
the rpm PID is quantised to 1 rpm and hundreds of segments were averaged.

**First order is absent, and that matters.** Once per crank revolution is
10.87 Hz at Park idle — above Nyquist — but it aliases to a predictable
**5.79–5.82 Hz**, and in Drive to 7.49 Hz. Checked in all fourteen windows: the
alias frequency sits at **0.9–1.8× the local floor**, i.e. it is the floor.
**There is no once-per-revolution component in the reported engine speed.** A
defective crank reluctor, a damaged tone wheel or a rotational imbalance is a
first-order phenomenon. **This is the first quantitative evidence in the project
against the crank-signal hypothesis.** It is not conclusive — the PCM's own
filtering attenuates 10.9 Hz more than 5.4 Hz before the scan tool ever samples
it — but the hypothesis now has a measurement pointing away from it rather than
just an absence of measurements.

**And a bonus: the 0.32 Hz hunt is not an aliasing artefact either.** 1.5 engine
order at 652 rpm is 16.30 Hz, which aliases to 0.37 Hz — uncomfortably close to
the hunt. But at 550 rpm in Drive that same alias moves to 2.9 Hz, and the hunt
in Drive was still measured at 0.33 Hz. **The hunt does not move with engine
speed, so it is not an alias of anything the engine turns at.**

**What the half order means: honestly, two readings and the data cannot separate
them.**

1. **A genuine, very small cylinder-to-cylinder torque difference.** This is what
   half order means physically, and every six-cylinder engine has some.
2. **An artefact of how the PCM refreshes the rpm variable.** If the PCM updates
   engine speed once per engine cycle, a sample-and-hold staircase would put a
   line at exactly rpm/120 with no imbalance at all.

**One test in the data leans against reading 2.** A staircase artefact scales
with the rate of change of the underlying signal. Between the Drive window
(03:23:10) and the Park window two minutes later (03:24:52), **the hunt amplitude
rose by a factor of 2.5 — 4.79 to 11.78 rpm — while the half-order amplitude did
not move at all: 0.280 to 0.267 rpm.** Across fourteen Park-idle windows the
correlation between half-order amplitude and hunt amplitude is only **r = +0.44,
n = 14**, which is not significant. A staircase artefact should track the
disturbance tightly. It does not.

**Verdict: UNCERTAIN. The signal is real and it is at exactly half engine order;
its cause is not established.** It is far too small to be what shakes the cab —
0.3 rpm is not felt — and Mode 06 says no cylinder is missing fire. **It is
recorded because it is the correct frequency for "one cylinder differs" and
because it is a genuinely new measurement, not because it accuses anything.**

### 3.10 Things in this domain that look wrong

**1. The inferred ethanol content, and the reason it belongs to ignition.**
`Ethanol fuel percent` read **16.08 %** before the KAM wipe and **19.22 %** after,
on a truck fuelled with Saudi 95 RON, which is normally E0.

This has been treated in CLAUDE.md as a fuelling curiosity. **It is also a spark
issue.** On Ford's sensorless flex-fuel strategy the ethanol fraction is inferred
from fuel-trim behaviour, and the inferred value blends both the fuelling *and
the spark tables* — ethanol is more knock-resistant, so a higher inferred
fraction lets the PCM run more advance
([Auto Service World, Finding Flex Fuel Faults](https://www.autoserviceworld.com/ford-flex-fuel-faults/);
[Diagnostic Network, Flex Fuel Inferred Too High](https://diag.net/msg/m14lejppf10qm17qx3xzggxu0v) —
**trade-press and technician-forum sourcing, not Ford**). If the PCM believes it
has E19 and it actually has E0, it is scheduling spark for a fuel with more knock
margin than is in the tank.

**Three reasons not to act on this yet.** At idle, at 12° advance and 30 kPa
manifold pressure, the difference is unmeasurable and irrelevant to the felt
shake. The learned octane sat at **−0.60** for the whole pre-wipe period, which
is the PCM saying it found no knock. And **it goes the wrong way to explain low
idle timing** — an over-estimated ethanol fraction would give *more* advance, not
less.

**It is, however, the single mechanism in this domain that could bite at wide
open throttle — 33 °C ambient with 47 °C intake air on those pulls — and wide
open throttle is exactly where no
ignition data exists.** It is also the most plausible reason the post-wipe OAR
stepped positive after two full-throttle pulls. Marked **speculation, testable.**

**2. Catalyst temperature bank symmetry must not be over-read.** Bank 1 and
Bank 2 catalyst temperatures are essentially identical in every log — mean
difference **+0.00 °C, sd 0.01–0.15 °C, worst single difference 0.75 °C**, over
ranges from 456 to 853 °C, n = 1,512 / 276 / 21. That is tempting as evidence of
symmetric combustion. **It is not.** These are *inferred* values on this
vehicle — modelled by the PCM from the same inputs for both banks — so their
agreement mostly proves the model is running. **Do not cite bank-equal catalyst
temperature as evidence of equal combustion.**

**3. No cold-start data exists in this domain.** The coldest coolant temperature
anywhere in the four logs is **81 °C.** Every spark number here is warm-engine.
CLAUDE.md's standing question — "is the needle breathing present on a COLD
start?" — is unanswerable from these logs, and so is the matching ignition
question of what the cold-start spark ramp looks like.

---

## 4. Suspect parts, ranked

Nothing in this domain rises to "replace". Ranked by what the evidence supports.

| # | Item | Action | Confirming test | Why it is where it is |
|---|---|---|---|---|
| 1 | **Nothing — ignition system** | **LEAVE ALONE** | — | Spark authority 47° and fully exercised; governor phase, sign and gain all correct in 6 windows; knock retard 0; learned octane −0.60 (good fuel); Mode 06 misfire 3 events in ~88,000 with both rate windows at exactly 0.000 %; VVT error 0.05–0.06° of 20°. **There is no ignition fault to find.** Spark plugs have already been replaced with no change, which is consistent. |
| 2 | **Wide-open-throttle knock behaviour** | **TEST — do not buy anything** | Log `Knock retard (°)` + `Timing advance (°)` + `Engine RPM` together through two hard pulls. See §5 | The only ignition question the four logs cannot answer. Cheap, free, and it either closes the domain completely or opens the only remaining lead in it. |
| 3 | **Learned octane trend after relearn** | **TEST — free, just read it** | Read `Learned octane ()` after 500–1,000 km. Works back toward −0.5/−0.6 = closed. Settles positive = real change | The pre-wipe −0.60 is the strongest long-integration evidence of healthy combustion in the project; the KAM wipe destroyed it and it is worth watching rebuild. |
| 4 | **Inferred ethanol percent (16 → 19 % on E0 fuel)** | **TEST, then decide** | Confirmed only if #2 shows knock retard at WOT. A FORScan flex-fuel-inference reset would be the intervention, not a part | Real anomaly, plausible spark mechanism at high load, **cannot explain the idle symptom** and goes the wrong direction for low idle timing. |
| 5 | **Half-order torque imbalance** | **TEST — the injector-kill balance test** | Unplug one injector at a time at warm idle, note each rpm drop. Six numbers; an unequal drop names the cylinder. Also settles §3.9 reading 1 vs 2 | 0.14–0.32 rpm is far too small to shake a cab, and Mode 06 says nothing is missing fire. Worth doing only because the test is free and the frequency is exactly right. |
| 6 | **Knock sensors and wiring** | **LEAVE ALONE — do not inspect on this evidence** | Would only become relevant if #2 showed knock and the PCM did *not* retard | A failed knock sensor sets P0325/P0330 and, on Ford, pushes learned octane toward +1. This truck has no code and learned −0.60. Actively contraindicated. |
| 7 | **Spark plugs (brand, part number, gap never recorded)** | **INSPECT only if opportunity arises** | Ask the owner for the brand, part number and gap. `docs/f150-specs.md` lists Motorcraft SP-534 (CYFS-12Y-2), gap ~1.25–1.35 mm — **both marked [VERIFY] there, so check the manual before treating either as the spec** | CLAUDE.md flags that the brand, part number and gap were never stated. A wrong plug or gap is an ignition-domain unknown — but it cannot be causing what is measured here, since combustion is measurably clean. Record-keeping, not a lead. |

---

## 5. What could not be determined, and the capture that settles it

### The one capture that matters — spark and knock at wide open throttle

**Every ignition question left open in this analysis collapses into one missing
capture.** Log `20260905_034051.csv.gz` contains two full-throttle pulls to
**6,832 rpm** and **6,402 rpm** at **96.5 % absolute load** and **215 g/s** — the
single best load excursion in the whole dataset — and **`Timing advance` was on
screen for only 26 seconds of that log, none of it during either pull, and
`Knock retard` was not in the channel set at all.**

**Capture, using the exact Car Scanner labels:**

```
Engine RPM (rpm)
Timing advance (°)
Knock retard (°)
Intake air temperature (℃)
Absolute load value (%)
```

Two pulls, second or third gear, from about 2,000 rpm to the limiter, warm
engine, on the same 95 octane. Export **CSV #2 (Horizontal)**, rounding off.

**What each outcome means:**

| At wide open throttle | Reading |
|---|---|
| Knock retard stays 0 and spark climbs smoothly with rpm | **The ignition domain closes completely.** Items 2, 4 and 6 above all die at once. |
| Knock retard goes non-zero by a degree or two on the first pull and settles | Normal adaptation, especially at 33 °C ambient with 47 °C intake air. Watch learned octane. |
| Knock retard several degrees and sustained, and/or spark visibly pulled back | Real knock. Then the inferred ethanol content (§3.10) becomes the leading suspect and a flex-fuel inference reset is the cheap intervention — **but note this still would not explain a shake at idle.** |

### Other items this dataset cannot answer

| Open item | Why it could not be determined | What settles it |
|---|---|---|
| **Cold-start spark** | Coldest coolant anywhere in the four logs is 81 °C. No cold start was ever recorded. | Start the truck cold with `Engine RPM (rpm)` + `Timing advance (°)` + `Engine coolant temperature (℃)` and log the first 5 minutes. Also answers CLAUDE.md's standing "is the needle breathing on a cold start" question. |
| **Whether ~12° at Park idle is normal for *this* engine** | No Ford specification exists; the community band is 13–17° and the project guide's 16–22° is uncorroborated and has its Park/Drive ordering backwards for this vehicle. | **A control sample.** Any 2011–2014 F-150 3.7 or Mustang V6 3.7 at warm idle in Park, one screenshot of `Timing advance (°)`. This is the same control sample the rest of the project already needs and it costs nothing. |
| **Whether the half-order line is cylinder imbalance or an rpm-update artefact** | The two hypotheses make nearly the same prediction in a 16.67 Hz OBD log. The one discriminator available (half order does not scale with the hunt) leans toward "real" but is not decisive. | The **injector-kill cylinder balance test** — six rpm drops, unequal ones name the cylinder. Or a phone accelerometer on the seat at warm idle looking for a line at **5.4 Hz** in Park and **4.6 Hz** in Drive; if the line moves with idle speed the way the rpm data says, it is combustion, not the tool. |
| **Spark against commanded air/fuel in more than one window** | Car Scanner had both channels dense together for exactly one clean 149-second window in the whole dataset. | Log `Timing advance (°)` + `Fuel/Air commanded equivalence ratio ()` + `Engine RPM (rpm)` as a set of three, warm Park idle, 5 minutes, throttle untouched. Reproducing +0.30 s / r = +0.63 in a second session would nail the chain down. |
| **Spark during deceleration fuel cut** | The fuel-cut coasts at 03:49 and 03:58 were logged with oxygen-sensor channels, not `Timing advance`. | Add `Timing advance (°)` to the next decel-fuel-cut capture. Low value — spark during fuel cut is not very diagnostic — listed only for completeness. |

---

## 6. Sources

Searched 2026-09-06. **Several sites were unreachable from this environment
(the network egress proxy blocked `forscan.org`, `cobbtuning.com`,
`cobbtuning.atlassian.net`, `fordservicecontent.com`, `motorsport-developments.co.uk`
and `en.wikipedia.org`), so the entries below marked "via search" are search-engine
summaries of those pages rather than pages I opened.** They are cited as community
or tuner documentation, never as Ford specification.

- [COBB Tuning — Ford EcoBoost and the Octane Adjust Ratio Monitor](https://www.cobbtuning.com/ford-ecoboost-and-the-octane-adjust-ratio-monitor/) — OAR starts at 0.0, learns toward −1.0 on good fuel and +1.0 on poor. *Tuner documentation, via search.*
- [COBB Tuning support wiki — Octane Adjust Ratio (OAR) and How it works for Ford Vehicles](https://cobbtuning.atlassian.net/wiki/spaces/PRS/pages/62357561/Octane+Adjust+Ratio+(OAR)+and+How+it+works+for+Ford+Vehicles) — −1.0 generally only on 93 octane; +1.0 = minimum recommended octane; reset by KAM clear; relearn needs warm engine, above idle, load > 0.375. *Tuner documentation, via search.*
- [Mustang EcoBoost forum — KOM aka OAR](https://www.mustangecoboost.net/threads/knock-octane-modifier-kom-aka-octane-adjust-ratio-oar-stuck-at-1-00-on-cobb-accessport.21259/) — KOM is the same memory with inverted sign, on 2018+ calibrations. *Community, via search.*
- [FORScan forum — Learned Relative Octane Adjust](https://forscan.org/forum/viewtopic.php?t=169) and [f150forum — Display Octane Adjustment Ratio in FORScan](https://www.f150forum.com/f129/display-octane-adjustment-ratio-forscan-547929/) — the PID exists on 2010–2015 Ford/Lincoln gasoline models under several names. *Community, via search.*
- [Ford OBD System Operation Summary (OBDSM608 / OBDSM1900)](http://www.fordservicecontent.com/ford_content/catalog/motorcraft/OBDSM608.pdf) — Mode 06 TID definitions: $0B EWMA misfire counts last 10 driving cycles; $0C misfire counts last/current driving cycle; $80 misfire rate per 200 revolutions vs catalyst-damage threshold; $81 misfire rate per 1,000 revolutions vs emissions threshold; **MID $A1 TID $84 = inferred catalyst mid-bed temperature, °C**. *Ford document, but read via search summary — the PDF itself was blocked. Re-verify before treating $84 as settled beyond doubt.*
- [ford-trucks.com — Timing Advance Numbers](https://www.ford-trucks.com/forums/1450485-timing-advance-numbers.html) — 13–17° BTDC at idle at 650 rpm in Park. **Community figure, not a Ford specification.**
- [ford-trucks.com — Ignition timing](https://www.ford-trucks.com/forums/120395-ignition-timing.html) and [easyautodiagnostics — Ford coil-pack ignition](https://easyautodiagnostics.com/ford/4600-5400/troubleshooting-the-ignition-module) — on PCM-controlled coil-on-plug Fords, ignition timing is not adjustable and there is no serviceable idle timing figure.
- [ASME J. Eng. Gas Turbines Power 123(2):428 — *The Frequency Analysis of the Crankshaft's Speed Variation*](https://asmedigitalcollection.asme.org/gasturbinespower/article/123/2/428/451059/The-Frequency-Analysis-of-the-Crankshaft-s-Speed) and [SAE 2001-01-1007](https://saemobilus.sae.org/papers/quantifying-relationships-crankshafts-speed-variation-gas-pressure-torque-2001-01-1007) — the 0.5, 1 and 1.5 orders of crankshaft speed carry cylinder-contribution information; the half order identifies a deficient cylinder. *Peer-reviewed, via search.*
- [Auto Service World — Finding Flex Fuel Faults](https://www.autoserviceworld.com/ford-flex-fuel-faults/) and [Diagnostic Network — Flex Fuel Inferred Too High](https://diag.net/msg/m14lejppf10qm17qx3xzggxu0v) — Ford infers ethanol content from fuel trim on sensorless flex-fuel systems; a wrong inference moves both fuelling and spark. *Trade press and technician forum, via search.*

---

## Appendix — what this analysis changes in CLAUDE.md

Four statements should be updated:

1. **"Its authority is tiny: 1.75° peak-to-peak"** — replace. Spark **authority**
   is 47° (−7.0° to +40.0°, both extremes exercised in these logs). 1.75° is the
   **correction the governor chooses to apply**, which is a gain choice, not a
   limit. §3.5.
2. **"[VERIFY] one unidentified value: Misfire Monitor General Data MID $A1
   TID $84 = 527.198"** — identified as **inferred catalyst mid-bed temperature
   in °C**. It is a temperature, not a fault metric, and it has no counterpart on
   the other bank to match. §3.8.
3. **The reference guide's 16–22° Park idle spark expectation** — should be
   withdrawn as a benchmark for this truck. It is a Level 3 heuristic its own
   authors could not corroborate, and its Park-higher-than-Drive ordering is
   backwards for this vehicle as measured. §3.2.
4. **The crank-signal hypothesis** — now has a measurement pointing away from it
   for the first time. **First-order (once-per-revolution) content in engine
   speed is absent** at its alias frequency in all fourteen idle windows, while
   half order is present and tracks engine speed correctly. Not conclusive
   (PCM filtering attenuates 10.9 Hz more than 5.4 Hz), but it is evidence where
   before there was none. §3.9.
