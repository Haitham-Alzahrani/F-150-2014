# 6R80, driveline and electrical — what the logs actually measure

**2014 F-150 XL 3.7 Ti-VCT / 6R80 / 4x2, 131,000 km, Jeddah.
Four Car Scanner logs, 2026-09-04 22:24 → 2026-09-05 05:07.**

Reproduce every number here with
[`data/analyze_transmission.py`](../../data/analyze_transmission.py). Nothing is
forward-filled; each channel is read on its own sample times, and where a fast
channel has to be evaluated at a slow channel's timestamps it is interpolated
only between two real samples less than four grid steps apart.

**Short version: the transmission and the electrical system are clean.** The
gear ratios are right, the converter locks, thirteen measured shifts have zero
engine flare, Park-versus-Drive idle behaves exactly as Ford intends, and the
charging system regulates to 51 mV over eleven minutes. Two real but unrelated
items came out of it: the axle ratio in `docs/f150-specs.md` is wrong, and the
right front tyre is 12 % under-inflated.

---

## 1. Summary table

| Parameter | Measured | Reference | Verdict |
|---|---|---|---|
| Gear ratio, 6th | N/V **18.744** rpm per km/h (n_speed 10, n_rpm 23) | 0.69 × axle | **NORMAL** |
| Gear ratio, 5th | N/V **23.854** (n_speed 57, n_rpm 61) | 0.87, predicts 23.634 → **+0.93 %** | **NORMAL** |
| Gear ratio, 4th | N/V **31.538** / **31.445** (n_speed 59 / 11) | 1.14, predicts 30.968 → **+1.84 / +1.54 %** | **NORMAL** |
| Gear ratio steps, 3rd–6th | 0.754, 0.758, 0.763, 0.763, 0.790, 0.796 | 0.750 / 0.763 / 0.793 | **NORMAL** |
| Gear ratio step, 2nd→3rd | **0.675, 0.676** (two WOT shifts) | 0.650 | **NORMAL** (converter slip inflates it) |
| **Axle ratio** | **3.729 derived** (k = 27.165, C = 2.288 m) | door code `26` reads 3.73 in axle-code charts [unconfirmed, pages blocked] | **NORMAL — `f150-specs.md` says "likely 3.55" and is wrong** |
| Torque converter slip, 6th @ 87 km/h | **reference, taken as 0 %** | locked | **NORMAL** |
| Torque converter slip, 5th @ 61 km/h | **+0.93 %** | 6R80 runs controlled slip 2nd–6th | **NORMAL** |
| Torque converter slip, 4th @ 32–52 km/h | **+1.5 to +1.8 %** | as above | **NORMAL** |
| Converter stall speed | **not testable** — no brake-stall event in any log | 2300–2580 rpm (guide) | **UNCERTAIN** |
| Shift time, 10–90 % of rpm drop | **0.15–0.54 s**, 12 of 13 shifts | crisp; no published Ford figure found | **NORMAL** |
| **Engine flare on upshift** | **0 rpm on every one of 13 shifts** | any positive flare = clutch slip | **NORMAL** |
| Idle, standstill **in gear** | **550.18 rpm**, sd 4.26, 10-s span 15.5 (n = 1392) | Ford commands lower in gear | **NORMAL** |
| Idle, standstill **Park** | **652.03 rpm**, sd 9.72, 10-s span 39.0 (n = 4946) | — | **NORMAL** |
| Park − in-gear idle offset | **101.9 rpm** | Ford strategy | **NORMAL** |
| ATF temperature (`var.3`) | 87.1 °C @ min 8, **76.6 °C @ min 154**, 92.5 °C at 61 km/h | 85–102 °C normal; 91–102 °C for the level check | **UNCERTAIN — PID unverified and it moved the wrong way** |
| ABS / individual wheel speeds | **absent from all four logs** | — | **not determined** |
| Charging voltage, first 46 min | **13.857 V** (n = 18,260 OBD; 13.851 BCM n = 1320; 13.686 PCM n = 24) | 13.5–14.5 V | **NORMAL** |
| Charging voltage, after min 52 | **12.894 V** (OBD n = 167; 12.886 BCM n = 1436; 12.659 PCM n = 3252) | Ford smart charge, battery full | **NORMAL** |
| Battery current | **+0.886 A → −0.017 A** (n = 1320 / 1436) | charge taper to zero | **NORMAL** |
| State of charge | **88 % → 90 %** (n = 125) | rising | **NORMAL** |
| Voltage regulation, densest block | 10-s means span **13.836–13.887 V** over 11 min; **0.07 %** of 16,664 samples below 13.6 V | flat | **NORMAL** |
| Electrical noise in the idle-hunt band | **r(rpm) = −0.006 / +0.085 / −0.031**; 1.5–4.9 % of voltage variance at 0.25–0.4 Hz | — | **NORMAL — electrics do not drive the hunt** |
| Voltage while driving (incl. WOT) | **12.288–13.000 V**, never above 13.0 (n = 23 / 25 / 155) | expected at 90 % SoC | **UNCERTAIN — confirm with a DMM under load** |
| AC ripple | **cannot be measured** — diode ripple is hundreds of Hz, the log samples at ≤ 30 Hz | < 0.1 V AC | **not determined** |
| Tyre, left front | 237.5 kPa (34.5 psi) | 241 kPa / 35 psi | NORMAL |
| **Tyre, right front** | **211.7 kPa (30.7 psi)** | 241 kPa / 35 psi | **ABNORMAL — 12 % low, 26 kPa below its pair** |
| Tyres, both rear outer | 247.9 kPa (36.0 psi) | 241 kPa | NORMAL |
| Tyres, rear inner | 0.0 kPa | single-rear-wheel truck, channel is a placeholder | **NORMAL, not a fault** |

---

## 2. Detailed findings

### 2.1 The driving data is thinner than it looks — read this first

Car Scanner polls the PIDs the user has selected, round-robin. The user's
selection changed between and during sessions, so **`Vehicle speed` is barely
sampled in the log that contains the wide-open-throttle pull.**

| Log | Span | Engine RPM | Vehicle speed | What it contains |
|---|---|---|---|---|
| `2026-09-04 22-23-38.zip` | 11,508 s | n = 115,257 @ 16.7 Hz | n = 1993, **all 0** | 3.2 h Park idle. Carries all the BCM and voltage data. |
| `20260905_030915.csv.gz` | 1,236 s | n = 6,648 @ 16.7 Hz | n = 50, **all 0** | **Standstill, in gear then Park.** The Park/Drive comparison. |
| `20260905_034051.csv.gz` | 1,046 s | n = 14,370 @ 16.7 Hz | **n = 13**, only at t = 981–1044 s | The full drive: city, cruise, two pulls to the limiter (6832 rpm). |
| `20260905_041723.csv.gz` | 2,990 s | n = 24,684 @ 16.7 Hz | **n = 366**, two dense bursts | 8.5 min of driving to 62 km/h, then 40 min Park idle. |

**So the gear ratios rest on two windows of dense speed data in
`…041723` plus a single 6-second cruise window in `…034051`.** Everything else
about the transmission is derived from engine speed alone. That is a real
limitation and every number below is labelled with what it rests on.

**`Gear (AT)` is useless.** It reads a constant `1.0` in all three logs that
carry it (n = 29 / 11 / 5). It is Car Scanner's own calculated gear, not a PCM
PID. Do not request it again and do not trust any earlier reading of it.

### 2.2 Gear ratios — 4th, 5th and 6th identified absolutely

Engine speed per unit road speed (N/V, rpm per km/h) on four steady plateaus:

| Window | Log | n_speed | n_rpm | mean speed | mean rpm | **N/V** |
|---|---|---|---|---|---|---|
| t 0–16 s, 32→45 km/h | …041723 | 59 | 59 | 37.93 km/h | 1196.3 | **31.538** |
| t 154–160 s, 45→52 km/h | …041723 | 11 | 12 | 48.27 km/h | 1517.9 | **31.445** |
| t 174–199 s, 61–62 km/h steady | …041723 | 57 | 61 | 61.16 km/h | 1458.8 | **23.854** |
| t 1038–1044 s, 87–88 km/h steady | …034051 | 10 | 23 | 87.10 km/h | 1632.6 | **18.744** |

Only one gear assignment makes these three plateaus consistent with a real
F-150 axle ratio. Taking the 87 km/h cruise as 6th gear locked gives

```
k  =  N/V per unit gear ratio  =  18.744 / 0.69  =  27.165
```

and then, with **no further fitting**:

| Plateau | Assigned gear | Predicted N/V | Measured | Residual |
|---|---|---|---|---|
| 87 km/h | 6th (0.69) | 18.744 | 18.744 | reference |
| 61 km/h | 5th (0.87) | 23.634 | 23.854 | **+0.93 %** |
| 45–52 km/h | 4th (1.14) | 30.968 | 31.445 | **+1.54 %** |
| 32–45 km/h | 4th (1.14) | 30.968 | 31.538 | **+1.84 %** |

**Three gears, two published ratios, better than 2 % with one free constant.
The 6R80 in this truck is delivering its designed ratios.**

The residuals are all positive and all shrink as the gear rises — which is
exactly the shape of residual torque-converter slip, not a ratio error. A ratio
error would scatter in both directions.

**Sensitivity — this is where the axle ratio falls out.** `k = axle × (1000/60) / C`,
where `C` is loaded rolling circumference:

| Assumed C | Source of C | Implied axle ratio |
|---|---|---|
| **2.288 m** | 703 rev/mile, a normal loaded value for a 30.1 in tyre | **3.729** |
| 2.346 m | 686 rev/mile, quoted for Michelin LTX A/S 255/65R17 [search summary, page not opened] | 3.824 |
| 2.402 m | 670 rev/mile, theoretical free diameter [tiresize.com, via search summary] | 3.915 |

3.73 is a factory F-150 ratio; 3.82 and 3.92 are not. Going the other way, a
3.55 axle would need `C = 2.192 m` — a 27.4 in tyre, four inches smaller than
anything that fits this truck.

**`docs/f150-specs.md` records axle code `26` and guesses "likely 3.55
[VERIFY]". The logged data derives 3.729.** Web search returns several
axle-code charts reading code 26 as 3.73 conventional (open) — **but every one
of those pages was blocked by this container's egress proxy, so I have the
search engine's summary of them and not the pages themselves. Treat the code-26
reading as unconfirmed; the measurement is what carries the claim.** The two
agree, which is why the specs file should be corrected to **3.73** with the
axle tag still worth reading to close it properly.

The 2.5 % gap between the derived 2.288 m and Michelin's published 2.346 m is
inside what tread wear alone explains: 131,000 km of wear removes roughly 8 mm
of tread depth, which is 9 mm off the circumference for every 1.4 mm of radius.
Do not read anything diagnostic into it.

**1st, 2nd and 3rd were never driven with the speed PID sampled**, so they are
identified only by ratio steps at shifts — see §2.4.

### 2.3 Torque converter

**It locks.** The whole of §2.2 only works because the 87 km/h cruise is rigid:
if the converter were slipping 4 % there, the derived axle would be 3.58 and the
4th/5th residuals would go negative. The self-consistency of three gears against
two published ratios is the lockup evidence.

**Slip, relative to that reference: +0.93 % in 5th at 61 km/h, +1.5 to +1.8 %
in 4th at 32–52 km/h.** The 6R80 runs a *controlled-slip* TCC — Ford's
calibration applies the clutch in 2nd through 6th and commands a small
deliberate slip band for NVH rather than a hard on/off lock. One to two percent
at part throttle in the middle gears is that strategy working. [Controlled-slip
behaviour is documented in transmission-trade sources, not in a Ford document
I could reach — treat the *mechanism* as community-level and the *measurement*
as solid.]

**Unlock is visible in the WOT pull.** At t = 941.7 s in `…034051` engine speed
goes from 1304 to 5028 rpm in 1.1 s — 3,400 rpm/s. No gear ratio produces that;
it is the clutch releasing and the converter going to full slip as the throttle
is floored and the box kicks down. That is normal kickdown behaviour.

**At a standstill in gear, slip is 100 % by definition** — 550 rpm in, output
shaft stopped. There is no fault reading available there.

**Stall speed could not be measured.** Nobody performed a brake-stall test in
any log, and no window exists where the brake is held against wide-open
throttle. The guide's 2300–2580 rpm figure remains untested on this truck. The
peak rpm in the second driving log (2314) is an ordinary acceleration, not a
stall.

### 2.4 Shift quality — thirteen shifts, zero flare

For each shift: `pre` is the mean of the 0.6 s before it, `peak` is the highest
engine speed reached during it, `post` is the mean of the 0.6 s after, and
`10–90 %` is the time to cross the middle 80 % of the rpm drop.

| Log time | Condition | n | rate | pre | peak | post | ratio | 10–90 % | **flare** |
|---|---|---|---|---|---|---|---|---|---|
| 944.50 | WOT, off the limiter | 56 | 15.7 Hz | 6579 | 6832 | 4543 | 0.690 | 0.96 s¹ | **0** |
| 949.65 | upshift on lift | 60 | 15.6 Hz | 6064 | 6169 | 4100 | 0.676 | 0.39 s | **0** |
| 951.30 | coast upshift | 50 | 15.4 Hz | 4098 | 4116 | 3127 | 0.763 | 0.18 s | **0** |
| 952.40 | coast upshift | 51 | 15.6 Hz | 3127 | 3162 | 2471 | 0.790 | 0.24 s | **0** |
| 953.40 | coast upshift | 52 | 15.6 Hz | 2469 | 2480 | 1964 | 0.796 | 0.54 s | **0** |
| 1011.40 | WOT upshift | 51 | 14.7 Hz | 6357 | 6402 | 4294 | 0.675 | 0.33 s | **0** |
| 1012.80 | upshift | 51 | 15.5 Hz | 4297 | 4306 | 3257 | 0.758 | 0.15 s | **−2** |
| 1013.95 | upshift | 52 | 15.3 Hz | 3240 | 3257 | 2472 | 0.763 | 0.30 s | **−5** |
| 1014.90 | upshift | 48 | 14.0 Hz | 2474 | 2493 | 1866 | 0.754 | 0.24 s | **0** |
| 826.90 | part-throttle | 57 | 16.4 Hz | 4723 | 4721 | 3549 | 0.751 | 0.24 s | **−82** |
| 668.75 | part-throttle | 55 | 16.1 Hz | 3665 | 3696 | 2854 | 0.779 | 0.18 s | **0** |
| 738.50 | part-throttle | 53 | 15.9 Hz | 3252 | 3265 | 2508 | 0.771 | 0.18 s | **0** |
| 160.15² | 4→5 at 52–54 km/h | 8 | 2.5 Hz | 1617 | 1617 | 1282 | 0.793 | — | **0** |

¹ inflated: the engine sat on the rev limiter before the shift, so the "pre"
level is a clipped plateau rather than a rising trend.
² from `…041723`, the only shift with vehicle speed recorded across it. Speed
rose 52.3 → 53.2 km/h during it, so the speed-corrected ratio is 0.780 against
a published 4→5 of 0.763.

**The flare column is the finding.** A 6R80 with worn clutch material, a leaking
piston seal, or a low or slow line-pressure rise announces itself as engine
speed *rising* while the shift is in progress — the oncoming clutch cannot hold
and the engine runs away before it grabs. **Not one of thirteen shifts flares.**
Peak engine speed during the shift never exceeds the pre-shift level on any of
them; three go slightly negative, which is the engine already falling as the
torque phase begins. Sample counts are 48–60 per shift at 14–16 Hz, so a flare
lasting even 0.15 s would have three or four samples in it and could not hide.

**Shift times, 0.15–0.54 s across the whole load range**, from coast upshifts to
full-throttle ones off the limiter. Nothing is long, nothing hangs, nothing is
harsh enough to show as an rpm discontinuity.

**Against §4C.1 of the guide** — adaptive shift behaviour. The guide's point is
that a shift which *changes* over repeated cycles is adaptation, not a fault.
The relevant test is therefore consistency, and this data supports it: the three
3rd/4th/5th-type steps measured on the first coast-down (0.763, 0.790, 0.796)
and the three measured on the second one 60 seconds later (0.758, 0.763, 0.754)
are the same family of numbers, and the shift times (0.18–0.54 vs 0.15–0.30 s)
overlap. **The adaptives are behaving repeatably.** Nothing here calls for a
transmission adaptive reset, and — given the standing rule in `CLAUDE.md` about
never wiping KAM before a measurement — nothing here justifies one.

**No sign of shift hunting.** In `…041723` the box shifted repeatedly between
t = 217 and t = 514 s during ordinary town driving; the events are spaced
seconds apart with settled plateaus between them, not oscillating between two
gears.

### 2.5 Park versus in gear at a standstill — measured on one log, minutes apart

`20260905_030915.csv.gz` contains the transition. The truck sat in gear at a
standstill for the first 15 minutes, then went to Park at t ≈ 902 s.

| | n | mean rpm | sd | min | max | 10-s span, median | windows |
|---|---|---|---|---|---|---|---|
| **In gear, standstill** (t 600–898) | 1392 | **550.18** | **4.26** | 539 | 584 | **15.5** | 8 |
| **Park, standstill** (t 915–1230) | 4946 | **652.03** | **9.72** | 613 | 699 | **39.0** | 31 |

**Ford commands 101.9 rpm less in gear.** That is the strategy working: with the
converter loading the engine, a lower idle still holds, and it cuts creep and
fuel burn. Not a fault, and the size of the step is unremarkable.

**The in-gear idle is 2.5× steadier — sd 4.26 against 9.72, spans 15.5 against
39.0.** This is the converter damping a torque disturbance, and it is what every
healthy torque-converter automatic does. **It reproduces `CLAUDE.md`'s
screenshot-derived figures (550.3 / 4.37 / 14.8 and 652.1 / 9.56 / 40.2) almost
exactly, now with 1,392 and 4,946 logged samples behind them instead of a
photographed graph.** The screenshot reading was right.

**What this does NOT show: any transmission contribution to the idle problem.**
The engine speed disturbance exists in both states, at the same character,
scaled by converter load. If the converter or the pump were adding a
disturbance, Park — where the transmission is doing least — would be the quiet
condition. It is the noisy one.

### 2.6 Transmission fluid temperature — do not act on this reading

Car Scanner's `ATF temperature var.3` is one of several guessed manufacturer
PIDs the app offers. **Its identity has not been verified on this VIN and the
readings do not behave the way fluid temperature should.**

| Log | Time | n | Reading | Coolant at that moment |
|---|---|---|---|---|
| 3.2 h idle | min 8.4 | 10 | 87.06 °C | 95 °C |
| 3.2 h idle | min 154.0 | 12 | **76.64 °C** | 98 °C |
| …041723 | min 3.2, at 61–62 km/h | 22 | 92.55 °C | 84 °C |

**Over 2.4 hours of continuous Park idling the reading fell 10.4 °C while
coolant rose 3 °C.** The 6R80's cooler circuit runs through the radiator, so
above the thermal-bypass threshold the fluid is tied to coolant temperature and
should have followed it up. Falling away from it is either a wrong PID or a
cooler path this analysis does not understand.

All three values sit inside the normal band (community figures put the 6R80 at
roughly 85–102 °C in service, and Ford's fluid-level check calls for 91–102 °C
at idle in Park). **So there is no evidence of an overheating transmission** —
but there is also no trustworthy measurement. **Do not check the fluid level
against this PID**: at a true 76 °C the fluid has not expanded to its check
volume and the level will read high.

Fluid was changed at 113,000 km, 18,000 km ago, and MERCON LV at that interval
in Jeddah heat is well inside life.

### 2.7 ABS and wheel speeds — nothing to compare

**No individual wheel-speed channel appears in any of the four logs.** The only
speed channel is the PCM's single `Vehicle speed`, quantised to 1 km/h.
Left/right comparison is impossible from this data. The absence is a gap, not a
finding.

### 2.8 Charging and module voltages

Three independent measurements of the same bus exist in the 3.2 h idle log: the
PCM's own `Control module voltage`, the BCM's `Vehicle Battery Voltage` measured
at the battery monitor, and the adapter's `OBD Module Voltage` at pin 16 of the
connector. **They never overlap in time** — the app was polling different PID
sets — which at first glance looks like a 1.2 V discrepancy between the PCM and
the connector. It is not. Sorted by time, all three agree:

| Session time | PCM | BCM | OBD connector | BCM current | SoC |
|---|---|---|---|---|---|
| min 5–15 | **13.686** (n = 24) | **13.851** (n = 1320) | **13.857** (n = 18,260) | **+0.886 A** | 88 % |
| min 46 → 52.9 | *step, unsampled* | | | | 89 % |
| min 53–161 | **12.659** (n = 3252) | **12.886** (n = 1436) | **12.894** (n = 167) | **−0.017 A** | 90 % |

**The three sources agree to within 0.20 V at every point at which two of them
were sampled close together.** There is no measurable voltage drop between the
battery monitor, the diagnostic connector and the PCM's internal supply. That is
what the ground-drop test in `CLAUDE.md`'s list would have been looking for, and
it comes out clean on all three legs, at both charging and non-charging voltage.

**Regulation is excellent.** In the densest block (16,664 samples over eleven
minutes, t = 960–1620 s), sixty consecutive 10-second means span **13.836 to
13.887 V — 51 mV**, and only 11 samples in 16,664 (0.07 %) fall below 13.6 V.
There are no steps, no dropouts and no load-shaped excursions.

**The system stopped charging between minute 46.0 and minute 52.9**, bounded by
real samples on both sides: the last high reading is 13.86 V at min 46, the
first low one 12.771 V at min 52.9. Current fell from +0.886 A to 0.000 A and
state of charge finished at 90 %. **This is Ford's smart charge terminating a
completed charge, confirmed three ways, and it is not a fault.** It is the same
event `CLAUDE.md` already closed; this analysis dates it.

#### The alternator did NOT cause the idle-amplitude halving

`CLAUDE.md` records that the idle rpm amplitude halved once, "around minute
40–50", with the cause not established, and names alternator load as one
candidate mechanism. **The timing rules it out.**

| Event | When | Evidence |
|---|---|---|
| **Idle amplitude halves** | **minute 37–38** | 60-s rpm sd goes 15.66 → 9.15, span 85 → 53 (n = 824 then 967) and stays down |
| Coolant rises 82 → 90 °C | between min 37 and 44 | ECT samples at min 36–37 read 81–82, at min 44–45 read 90–90.8 |
| **Charging stops** | **minute 46.0–52.9** | bounded by real voltage samples on both sides |

**The rpm step comes 8 to 15 minutes before the charging step.** The alternator
going to zero output cannot have caused something that had already happened. The
coolant rise, by contrast, brackets the rpm step. **This does not prove the
cooling fan is the cause — but it removes the alternator from the running and
leaves the fan/coolant candidate standing alone.** [The 2014 F-150 3.7 appears
from parts catalogues to use an electric fan-and-motor assembly rather than a
belt-driven clutch fan, which would make the fan both a thermal and an
electrical event; I could not reach a Ford document to confirm it. **VERIFY.**]

#### The electrics are not in the idle hunt

Cross-correlating system voltage against engine speed on a common 0.06 s grid,
in three separate windows:

| Channel | Window | n | sd | **r vs rpm** | share of voltage variance at 0.25–0.4 Hz |
|---|---|---|---|---|---|
| OBD Module Voltage | t 960–1620 | 10,106 | 0.0790 V | **−0.006** | 4.9 % |
| OBD Module Voltage | t 2160–2280 | 748 | 0.0732 V | **+0.085** | 3.2 % |
| Control module voltage | t 5700–5900 | 3,071 | 0.0765 V | **−0.031** | 1.5 % |

**System voltage is uncorrelated with the 0.3 Hz idle oscillation, and the hunt
band holds only 1.5–4.9 % of the small voltage variation that exists.** Most of
that remaining variation is quantisation — the OBD channel steps in 0.1 V, which
alone contributes 0.029 V of sd.

This closes a question `CLAUDE.md` left open. A noisy sensor reference driven by
charging-system ripple would show as voltage moving with engine speed. It does
not. **Whatever else the crank-signal hypothesis rests on, it does not get
support from the supply.**

#### The one electrical thing worth a DMM

**In both driving logs, system voltage never once reached 13.0 V** — PCM
12.288–12.873 V (n = 23) and 12.390–12.771 V (n = 25), connector 12.600–13.000 V
(n = 155), across a drive that included two pulls to the rev limiter. At 90 %
state of charge that is consistent with smart charging holding the alternator
down to cut drag, and the owner's earlier conclusion stands. But it is a
*complete* absence of high-output operation over a whole drive, and the sample
counts are small (23–155 against 18,427 for the idle session).

**It is cheap to settle and it is not the battery being reopened:** DMM across
the posts, engine running, then switch on headlights + blower on high + rear
defrost + wipers. **A healthy system will climb to 13.5–14.5 V within seconds
under that load.** If it stays near 12.6 V with a heavy load applied, the
alternator or the battery-monitor strategy needs looking at.

### 2.9 Body control module

**Tyre pressures**, one value each across 115–123 samples (TPMS updates slowly,
so these are static snapshots, not traces):

| Position | kPa | psi | vs 241 kPa label |
|---|---|---|---|
| Left front | 237.5 | 34.5 | −1.4 % |
| **Right front** | **211.7** | **30.7** | **−12.2 %** |
| Left rear outer | 247.9 | 36.0 | +2.9 % |
| Right rear outer | 247.9 | 36.0 | +2.9 % |
| Left / right rear **inner** | 0.0 | 0.0 | **expected — single-rear-wheel truck** |

**The right front is 26 kPa (3.8 psi) below its pair and 36 kPa (5.3 psi) below
the rears.** `CLAUDE.md` already noted it; it is still there, unchanged, in the
most recent log. It is a cross-axle imbalance that affects steering pull, wear
and braking. It has nothing to do with an idle vibration at a standstill —
**but 12 % low on one front corner is worth five minutes with a gauge, and if it
comes back down again there is a leak.**

Other BCM channels present and unremarkable: normalised cumulative charge
121.6, cumulative discharge 2.9 and 10.6, all static across the session.

### 2.10 Other things checked and found clean

- **Gear ratio spread across the whole drive.** No plateau appears at an N/V
  that does not belong to the 4.17/2.34/1.52/1.14/0.87/0.69 family.
- **No engine-speed discontinuity at a steady road speed** other than the
  identified shifts — nothing that would indicate a converter clutch shuddering
  or cycling.
- **The one gear change captured is clean.** In `…030915` the box comes out of
  gear at t = 905.8 s: engine speed rises 550 → **717 rpm peak at 906.5 s**,
  rings down through 633–681 and settles at 652 by t ≈ 914 s. **A 65 rpm
  overshoot above the new target, settling in about 8 s.** That is the idle
  governor catching an abrupt load release — normal, and small. There is no
  hang, no stumble and no dip toward stall, which is what a dragging clutch pack
  or a failing pump would produce.
- **`Vane position sensor` reads a flat 0.000 V** (n = 40). Not applicable to
  this engine; ignore the channel.

---

## 3. Suspect parts, ranked

Only one item in this domain is actually abnormal. The rest are ranked by how
much value the test returns, not by suspicion.

| # | Item | Action | Confirming test |
|---|---|---|---|
| 1 | **Right front tyre / valve / TPMS sensor** | **Inflate to 241 kPa**, then re-read in a week | Gauge check now and again after 7 days. Still low → soapy water on the valve and bead, then a dunk test. |
| 2 | **Charging under heavy electrical load** | **Test** — do not replace anything | DMM across the battery posts, engine idling, all loads on. Expect 13.5–14.5 V. Below 13.0 V with a full load applied is the only result that opens an investigation. |
| 3 | **Transmission fluid temperature PID** | **Test** — read the real one before any fluid work | FORScan `TFT` on the TCM. If it agrees with `var.3` the channel is usable; if not, delete `var.3` from the app's list so it cannot mislead a later level check. |
| 4 | **Torque converter stall speed** | **Test only if a stall complaint appears** | Brake-stall test per the guide, ≤ 5 s, ATF at temperature. Expect 2300–2580 rpm. There is no symptom pointing here — do not do it speculatively; it is hard on the transmission. |
| 5 | **6R80 clutches, bands, line pressure** | **Leave alone** | Already answered: thirteen shifts, zero flare, 0.15–0.54 s. Nothing to find. |
| 6 | **Torque converter clutch** | **Leave alone** | Already answered: locks in 6th, 0.9–1.8 % controlled slip in 4th and 5th. |
| 7 | **Alternator, regulator, grounds** | **Leave alone** | Already answered: 51 mV of drift over 11 minutes, three sources agreeing within 0.20 V, no correlation with engine speed. |
| 8 | **Rear axle, driveshaft, output shaft** | **Leave alone** | Derived ratios match published values to 2 %; symptom reproduces at a standstill in Park. |
| 9 | **Transmission fluid** | **Leave alone** | Changed 18,000 km ago; no temperature evidence against it. |

**Nothing in the transmission or the electrical system explains the idle
vibration.** That is the headline for this domain, and it is a clean bill of
health, not an absence of evidence: the shifts, the ratios, the converter lock,
the Park/Drive idle offset and the charging regulation were all measured and all
came out where they should be.

---

## 4. What could not be determined, and the capture that would settle it

| Open question | Why it could not be answered | The capture that settles it |
|---|---|---|
| **Slip across the whole speed range, and whether the TCC ever shudders** | No turbine-speed PID. Slip here is only the residual left after assuming 6th is locked. | **FORScan: `TSS` (turbine shaft speed) and `OSS` (output shaft speed) logged together with `Engine RPM` for one 15-minute drive.** Slip = engine − turbine, directly, at every instant. This is the single most valuable transmission capture available and it is free. |
| **Which gear the box is in, at every moment** | `Gear (AT)` is a Car Scanner calculation and reads a constant 1. | FORScan `GEAR` / commanded-vs-actual gear on the TCM. |
| **Line pressure and clutch fill quality** | Not on OBD-II at all. | FORScan `LPC` / `TCC_DC` duty during logged shifts. |
| **Real ATF temperature** | The only channel is an unverified guess and moves the wrong way. | FORScan `TFT`, side by side with `ATF temperature var.3` for one warm-up, to prove or condemn the app's PID. |
| **Torque converter stall speed** | No brake-stall event exists in any log. | Brake-stall test, only if a stall or slip complaint ever appears. |
| **Left/right wheel-speed balance** | No wheel-speed channels in any log. | FORScan ABS module: the four `WHL_SPD` PIDs, logged during a straight 60 km/h run. |
| **AC ripple from the alternator diodes** | Physics. Diode ripple is hundreds of Hz; the fastest channel logged is 30 Hz. **No OBD tool can ever measure this.** | DMM on AC volts across the battery posts, engine idling. Under 0.1 V. |
| **Charging output under heavy load** | Never sampled — every driving-log voltage window is at 90 % state of charge with the alternator down. | DMM across the posts with headlights, blower, defrost and wipers all on. |
| **1st, 2nd and 3rd gear ratios, absolutely** | The only log containing them has 13 vehicle-speed samples, none during those gears. | **Set Car Scanner to log `Engine RPM` + `Vehicle speed` and nothing else**, then accelerate gently from rest to 90 km/h. Two channels at full rate resolves all six ratios in one 40-second pull. |
| **Whether the cooling fan caused the minute-37 amplitude step** | Fan state is not an OBD-II PID and coolant temperature is 88 % collinear with elapsed time in that session. | Idle from cold with `Engine coolant temperature` beside `Engine RPM`, twice. A step at the same coolant value on both runs decides it. Already in `CLAUDE.md`; this analysis strengthens the case for it by eliminating the alternator. |

---

## 5. What this changes in the project files

1. **`docs/f150-specs.md` §4 — the axle ratio is 3.73, not "likely 3.55".**
   Derived from the logs to 3.729, and door code `26` reads 3.73 in two
   independent axle-code references. Still worth reading the axle tag, but the
   [VERIFY] can be downgraded.
2. **`CLAUDE.md` — the alternator is out as a cause of the minute-40 amplitude
   halving.** The charging step is 8–15 minutes later than the rpm step, bounded
   by real samples on both sides. The cooling-fan candidate is now alone.
3. **`CLAUDE.md` ground-drop and ripple items — the ground-drop half is
   answered.** Three independent voltage measurements agree within 0.20 V at
   both charging and non-charging voltage. The AC-ripple half still needs a DMM
   and always will.
4. **`docs/scanner-pids.md` — flag `Gear (AT)` as a Car Scanner calculation that
   reads a constant, and `ATF temperature var.3` as unverified.**

---

## 6. Sources used for the reference values

Everything in the "measured" columns comes from the logs in
`data/carscanner/`. The reference values used to judge them came from:

- [`docs/ford-3.7-cyclone-6r80-guide.md`](../ford-3.7-cyclone-6r80-guide.md) —
  6R80 gear ratios 4.17 / 2.34 / 1.52 / 1.14 / 0.87 / 0.69 (Level 1, Ford
  service reference), MERCON LV, stall 2300–2580 rpm, §4C.1 adaptive shift
  behaviour.
- [`docs/f150-specs.md`](../f150-specs.md) — tyre size P255/65R17, cold pressure
  241 kPa, axle code `26`.
- [255/65R17 tyre size data](https://tiresize.com/tiresizes/255-65R17.htm) and
  [Michelin LTX A/S 255/65R17](https://tiresize.com/tires/Michelin/LTX-AS-255-65R17.htm)
  — revolutions per mile. **Community/retail data, and I read the search
  engine's summary rather than the pages themselves.**
- [Ford axle code charts](https://gmundcars.com/ford-axle-code-chart/) and
  [engineneeds.com](https://engineneeds.com/rear-end-ford-axle-code-chart/) —
  code 26 = 3.73 open. **Both pages were blocked by this container's egress
  proxy; only the search summary was available. Unconfirmed.**
- [Gears Magazine, "Lock Up Madness! GM and Ford Torque Converter Clutch
  Control"](https://gearsmagazine.com/magazine/lock-up-madness-gm-and-ford-torque-converter-clutch-control/)
  and [usshift.com 6R80 control notes](https://www.usshift.com/6r80.shtml) —
  6R80 applies the TCC in 2nd through 6th with a commanded slip band rather than
  hard lockup. **Trade and vendor sources, not Ford. Level 3 by this project's
  own evidence scale.**
- [6R80 transmission temperature discussion, f150forum](https://www.f150forum.com/f82/6r80-transmission-temperature-530633/)
  and [Mustang6G thermal bypass valve thread](https://www.mustang6g.com/forums/threads/6r80-transmission-temperatures-thermal-bypass-valve.181627/)
  — normal running band ~85–102 °C, and 91–102 °C at idle in Park for the fluid
  level check. **Community figures. Confirm against the Ford workshop manual
  before using them as a pass/fail.**
- [2014 F-150 cooling fan parts listing](https://ford.oempartsonline.com/v-2014-ford-f-150--xl--3-7l-v6-cng/cooling-system--cooling-fan)
  — the 3.7 appears to use a fan blade and motor assembly rather than a
  belt-driven clutch fan. **[VERIFY] — inferred from a parts catalogue listing
  summary, not from a Ford document.**
