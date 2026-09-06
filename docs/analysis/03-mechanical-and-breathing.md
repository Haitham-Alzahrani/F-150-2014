# Mechanical condition and engine breathing — analysis of the four Car Scanner logs

2014 Ford F-150 XL · 3.726 L DOHC 24-valve 60° V6 Ti-VCT (Cyclone) · 6R80 · 4x2 ·
131,313 km on the PCM odometer · Jeddah, ambient 32–37 °C.

**Bank convention used throughout: Bank 1 is the passenger side, cylinders 1, 2 and 3.
Bank 2 is the driver side, cylinders 4, 5 and 6.**

Source data: `data/carscanner/` — four logs, loaded with `carscanner_lib.load`, every
channel kept on its own true sample times. No forward-filling anywhere. Mode 06 from
`data/mode06.csv`. Scripts and intermediate output were run ad hoc; every number below
carries its sample count and its time window.

---

## 1. Summary table

| # | Parameter | Measured | Reference | Verdict |
|---|---|---|---|---|
| 1 | Peak airflow at wide open throttle | **215.27 g/s @ 6219 rpm** (n=115 in the pull) | ~170–210 g/s for a 302 hp NA engine [community rule of thumb] | **NORMAL** (upper end) |
| 2 | Peak absolute load | **96.47 % @ 4935 rpm** (n=125 in the pull) | 90–100 % on a healthy NA engine | **NORMAL** |
| 3 | Airflow curve shape 3000→6400 rpm | smooth, no plateau; VE falls only 104.6 %→102.3 % over the last 1000 rpm | a restriction shows as airflow going flat while rpm climbs | **NORMAL** |
| 4 | Volumetric efficiency, 4000–6500 rpm | **102–105 %** referenced to 96.5 kPa / 33 °C ambient | 95–105 % typical for a modern DOHC NA with cam phasing | **NORMAL** |
| 5 | Estimated crank power | **303 hp** (range 283–323) | 302 hp @ 6500 rpm [Ford] | **NORMAL** |
| 6 | Max engine speed reached | **6832 rpm**, clean, no fuel-starve dip | limiter ~6800–6900 | **NORMAL** |
| 7 | Park idle airflow | **3.001 ± 0.055 g/s @ 651 rpm** (n=5699) | project guide 3.17–3.63 g/s [Level 3 observed]; 0.8–1.2 g/s per litre [community] | **NORMAL** once corrected for 97 kPa / 37 °C — see §4 |
| 8 | Idle airflow stability over 3.2 h | block means 2.918 → 3.055 g/s across 13 separate bursts | drift or steps would indicate a sensor or breathing fault | **NORMAL** |
| 9 | In-gear idle airflow | **3.413 ± 0.128 g/s @ 578 rpm** (n=46) | more air per cycle at lower rpm = converter load | **NORMAL** |
| 10 | Manifold absolute pressure | **CHANNEL DOES NOT EXIST in any log** | — | **CANNOT BE DETERMINED** — see §4.3 |
| 11 | Cam phaser, intake Bank 1, live PID | 7,935 samples, **two values only: 0.000 and −0.0625° (one 1/16° step)** — and **every single sample was taken between 623 and 724 rpm** | Ford Ti-VCT intake phaser parks at 0° advance at idle by design | **NORMAL at idle; NOT TESTED above 724 rpm** |
| 12 | Mode 06 VVT monitor | Bank 1 **0.06**, Bank 2 **0.05**, limit 20 (TID $85); all other VVT TIDs 0 | — | **NORMAL** — and this is the only evidence the phasers move at all |
| 13 | Mode 06 catalyst monitor | Bank 1 **0.3711**, Bank 2 **0.3633**, limit 0.8359 | 44 % and 43 % of the failure threshold, banks within 2.1 % | **NORMAL** |
| 14 | Catalyst temperature, both banks | **the same number on both PIDs** — 1491/1520 samples exactly equal, residual explained by the 30 ms sampling offset | a PCM **model**, not two thermocouples | **NOT A MEASUREMENT** — carries no bank information |
| 15 | Coolant temperature, continuous record | clean sawtooth **92 ↔ 101 °C**, period **288 s**, fall 0.19 °C/s, rise 0.042 °C/s (n=485 over 485 s) | classic cooling-fan hysteresis cycle | **NORMAL** |
| 16 | The "81–83 °C for forty minutes then rose" shape | **artefact of burst sampling plus a real accessory load** — see §6 | — | **EXPLAINED, and the previous reading is withdrawn** |
| 17 | Cycling accessory load, minutes ~15–40 | calculated load steps **28.6 % ↔ 36.8 %** on a **15.78 s ± 1.17 s** period, 6.9 s on / 8.9 s off, n=627; fuel rate **1.344 vs 1.002 L/h (+34 %)** | nothing on a correctly idling engine does this | **ABNORMAL for a "no-load idle" — almost certainly the A/C compressor. See §6** |
| 18 | Airflow content at the 3.1 s idle hunt frequency | **0.0043 g/s at 0.304 Hz = 0.14 % of mean**; 8.9 % of MAF's 0.05–4 Hz power in the hunt band vs 34.4 % for rpm | — | **NORMAL — and it eliminates every breathing-side cause of the hunt. See §7** |
| 19 | Deceleration fuel cut | both banks peg at 29.383 and hold flat; longest runs **46.5 s (Bank 1)**, **26.6 s (Bank 2)** | — | **NORMAL** |
| 20 | Knock retard | **0.0° in every sample (n=38 across three logs)** | 0° expected | **NORMAL — but never sampled at wide open throttle. See §10** |
| 21 | Spark advance at light cruise ~1630 rpm | **33–40°** (n=10) | high advance = no knock, healthy chamber | **NORMAL** |
| 22 | Inferred ethanol content | 16.078 % before the KAM wipe, **19.216 % after** (n=149) | Saudi pump fuel is normally E0 | **ABNORMAL — affects open-loop (WOT) fuelling only. See §10.2** |
| 23 | Learned octane | −0.6 pre-wipe → 0.0 at wipe → **+0.081** after relearn (n=67) | scaling unknown for this app | **UNCERTAIN [VERIFY]** |
| 24 | Timing chain / internal water pump | no direct evidence available; coolant holds a clean regulated sawtooth with no loss over 3.2 h | — | **NO EVIDENCE OF A FAULT — but not tested** |

---

## 2. Wide open throttle — the engine breathes correctly

### 2.1 There were TWO separate pulls, not one

This matters, because the two headline numbers in `CLAUDE.md` — 96.47 % absolute load and
215.27 g/s MAF — **do not come from the same pull, and neither pull has both channels.**
Car Scanner polls round-robin, and the two channels were being polled in different phases
of the session.

| | Pull A | Pull B |
|---|---|---|
| Window (log `20260905_034051`, seconds from log start) | **941.7 → 950.0** | **1002.6 → 1011.0** |
| Engine speed | 1343 → **6818** rpm (log peak 6832) | 1300 → **6402** rpm |
| `Absolute load value` | **sampled, n=125, peak 96.47 %** | **not sampled** |
| `MAF air flow rate` | **not sampled** | **sampled, n=115, peak 215.27 g/s** |
| Upstream O2 (either bank) | **not sampled** (channel coverage ends at t=912.7) | **not sampled** |
| `Timing advance` | **not sampled** | **not sampled** |

The two pulls are 53 seconds apart in the same session at the same temperature, so treating
them as one engine condition is defensible. Treating them as one *measurement* is not.

### 2.2 Airflow versus engine speed — no plateau

Pull B, MAF binned by engine speed (engine speed interpolated onto each MAF sample's own
time; interpolation of engine speed between samples 60 ms apart is legitimate, and no
channel was forward-filled):

| rpm band | n | MAF (g/s) | air per cycle (g) | VE @ 96.5 kPa / 33 °C | VE @ 96.5 kPa / 43 °C |
|---|---|---|---|---|---|
| 1500–2000 | 4 | 50.8 | 3.338 | 81.6 % | 84.2 % |
| 3000–3500 | 19 | 104.6 | 3.854 | 94.2 % | 97.3 % |
| 3500–4000 | 12 | 121.2 | 3.933 | 96.1 % | 99.3 % |
| 4000–4500 | 24 | 149.5 | 4.226 | **103.3 %** | 106.7 % |
| 4500–5000 | 13 | 165.9 | 4.204 | 102.8 % | 106.1 % |
| 5000–5500 | 12 | 188.5 | 4.253 | 103.9 % | 107.3 % |
| 5500–6000 | 16 | 205.1 | 4.281 | **104.6 %** | 108.0 % |
| 6000–6500 | 10 | 213.5 | 4.184 | 102.3 % | 105.6 % |

Air per cycle = 120 × MAF / rpm. VE = (air per cycle) / (ρ × 3.726 L), with
ρ = P/RT — 1.0981 g/L at 96.5 kPa and 33 °C ambient, 1.0634 g/L at 43 °C intake.
The 33 °C column is the honest one for VE: it uses the density of the air the engine is
actually drawing from outside. The 43 °C column uses the heat-soaked intake sensor reading
and is an upper bound.

**Reading:** VE climbs to ~103 % by 4000 rpm, holds 103–105 % through 6000, and gives back
2 points by 6400. That is a textbook naturally-aspirated curve with tuned runners and cam
phasing, and it flattens rather than falling off a cliff. A restricted exhaust, a plugged
catalyst, a restricted intake, worn rings, leaking valves or slipped cam timing all show as
VE *falling* through the top end, usually 10–25 points. Nothing here does.

**Caveat on the shape, not the magnitude:** both pulls were dynamic — engine speed rose at
roughly 450–600 rpm/s — so the rpm at which VE peaks carries transient error. The peak
*magnitude* is robust; the claim "VE peaks at 5500–6000 rpm" is not, and published torque
peak is 4000 rpm.

Pull A, absolute load binned the same way (VE = absolute load × 1.0782, the ratio of the
SAE 1.184 g/L reference density to the actual 1.0981 g/L):

| rpm band | n | Absolute load | implied VE |
|---|---|---|---|
| 1500–2000 | 7 | 78.3 % | 84.4 % |
| 4000–4500 | 8 | 92.6 % | 99.8 % |
| 4500–5000 | 26 | 91.2 % | 98.3 % |
| 5000–5500 | 27 | 92.0 % | 99.2 % |
| 5500–6000 | 28 | 92.5 % | 99.7 % |
| 6000–6500 | 13 | 91.0 % | 98.1 % |
| 6500–7000 | 8 | 87.1 % | 93.9 % |

The peak single sample, 96.47 % absolute load at 4935 rpm, occurred immediately after a
6R80 upshift dropped engine speed from 6818 to 4935 rpm in 0.4 s with the throttle still
wide open — i.e. at the best VE point in the range, exactly where it should be.

**The two pulls agree with each other to within about 4 points of VE.** They were taken
53 s apart with the engine hotter for the later one. That is good cross-validation of both
channels.

### 2.3 Power estimate, and its uncertainty

**Conversion factor and its derivation.** Fuel mass rate = MAF / AFR. Crank power =
fuel mass rate × lower heating value × brake thermal efficiency.

- MAF at peak = **215.27 g/s**
- Commanded WOT AFR ≈ **12.3:1** — **this comes from the screenshot record in
  `CLAUDE.md`, not from these logs.** Neither upstream O2 channel was being polled during
  either pull (Bank 1 coverage ends at t=982.5 s, Bank 2 at t=912.7 s).
- Gasoline LHV = 43.0 MJ/kg
- Brake thermal efficiency at peak-power WOT for a port-injected NA gasoline engine =
  **28–32 %**

| η | Fuel | Power |
|---|---|---|
| 0.28 | 17.50 g/s | 210.7 kW = **283 hp** |
| 0.30 | 17.50 g/s | 225.8 kW = **303 hp** |
| 0.32 | 17.50 g/s | 240.8 kW = **323 hp** |

**Central estimate 303 hp against a 302 hp rating.** The uncertainty band is ±7 % and it is
dominated by the efficiency assumption, not by the airflow measurement. Cross-check by
brake specific fuel consumption: 17.50 g/s = 138.9 lb/h; at 302 hp that is
**0.46 lb/hp·hr**, squarely in the 0.45–0.50 range expected for this engine class. The
crude industry factor of 1.4 hp per g/s gives 301 hp and lands in the same place.

**Do not use the app's power channels.** They are pure rescalings of MAF and carry no
independent information whatsoever:

- `Power from MAF (hp)` = **1.20000 × MAF**, R² = 1.000000, n=892.
- `Calculated instant fuel rate (L/h)` = **0.33035 × MAF + 0.0013**, R² = 0.999999, n=891 —
  which is MAF ÷ 14.63 converted to litres. The app assumes a fixed stoichiometric AFR, so
  **at wide open throttle its fuel rate is about 19 % low** and the derived
  `Instant engine power (based on fuel consumption)` peak of 278 hp is not an independent
  figure.
- `Calculated boost (bar)` = **0.082718 × Absolute load − 0.916716**, R² = 0.999200, n=992.
  It is absolute load rescaled. It is not a pressure and it is not a measurement.

### 2.4 What wide open throttle eliminates

Reaching 96.5 % absolute load, 215 g/s and 102–105 % VE at 6200–6400 rpm on a hot engine at
96.5 kPa ambient rules out, with evidence and not by inference:

- restricted or plugged **catalytic converter** (either bank)
- restricted **exhaust** anywhere downstream
- restricted **intake**, airbox, duct or filter
- **worn rings or bores**, **burned or leaking valves**, **carboned valve seats** —
  all of these cost VE, and there is no VE deficit to spend
- **slipped timing chain** or mistimed cams of any consequential amount

An engine cannot pump 105 % of its own displacement per cycle with any of these present.

---

## 3. Catalyst and exhaust

### 3.1 The catalyst temperature channels are one modelled number reported twice

**Verified.** Pairing each Bank 1 sample with its nearest Bank 2 sample:

| Log | paired n (within 0.35 s) | exactly equal | max \|B1 − B2\| | median sampling offset |
|---|---|---|---|---|
| `2026-09-04 22-23-38` (3.2 h idle) | 1520 | **1491 (98.1 %)** | 0.1 °C = one quantisation step | 0.030 s |
| `20260905_034051` (WOT log) | 281 | 203 (72.2 %) | 0.8 °C | 0.030 s |
| `20260905_041723` (driving) | 25 | 21 (84.0 %) | 0.1 °C | 0.032 s |

In the idle log the two channels take **the identical set of 81 distinct values** and the
worst disagreement anywhere is a single 0.1 °C step. In the WOT log the disagreement grows
to 0.8 °C only where the value is slewing at several °C per second and the 30 ms polling
offset between the two channels starts to matter.

**Conclusion: this is one PCM-modelled exhaust gas temperature published on two PIDs. The
2014 F-150 3.7 has no catalyst temperature sensors.** The consequences are absolute:

- **Catalyst temperature can never detect a bank-to-bank difference on this truck**, because
  the number is not derived from anything bank-specific. Any past or future finding of
  "both banks read the same catalyst temperature, therefore the converters match" is
  circular and must be discarded.
- The absolute value (460 °C at idle, 853 °C at WOT, 547 °C in traffic) is only as good as
  Ford's model. It is useful as a sanity indicator of load and spark, nothing more.

### 3.2 Mode 06 catalyst monitor — the real evidence, and it is good

Bank 1 **0.3711**, Bank 2 **0.3633**, limit **0.8359**. Both at 43–44 % of the failure
threshold and within **2.1 %** of each other. Combined with §2.2 and §2.4, the converters
are neither restricted nor degraded, on either bank.

This also finally kills the "Bank 1 downstream oxygen sensor swings deeper" asymmetry
recorded earlier from idle screenshots: idle is the worst operating point at which to judge
a converter, and the on-board monitor, which judges it at the right operating point,
finds the two banks equal.

---

## 4. Volumetric efficiency at idle — and the 3.004 g/s question

### 4.1 The measurement

Log `2026-09-04 22-23-38`, Park, standstill (`Vehicle speed` = 0 for all 1993 samples),
warm, over 3 h 12 m:

- `MAF air flow rate`: n=5712, mean **3.0039**, median 3.000, sd 0.0905 g/s.
  Excluding transients above 3.6 g/s and restricting to 600–720 rpm: n=**5699**,
  mean **3.0008 g/s**, sd **0.0551**.
- Engine speed at those samples: mean **651.2 rpm**, sd 7.4.
- Barometric pressure **97 kPa** (n=1500, single value all session).
- Intake air temperature **37 °C**; ambient **36–37 °C**.

Derived:

- Air per engine cycle = 120 × 3.0008 / 651.2 = **0.5530 g**
- Air per cylinder per cycle = **0.0922 g**
- Specific idle airflow = **0.805 g/s per litre**

### 4.2 Is 3.0 g/s low? No — once you correct for Jeddah

This is the crux of the open question, and the answer is that the raw number is being
compared against references that assume sea-level standard air.

Correcting the measurement to standard conditions by ρ ∝ P/T:

| | value |
|---|---|
| Measured, at 97 kPa and 37 °C | **3.001 g/s** |
| Same engine at 101.325 kPa and 20 °C | **3.316 g/s** |
| Same engine at 101.325 kPa and 25 °C | **3.261 g/s** |
| Corrected and normalised to 700 rpm | **3.51–3.57 g/s** |

Now compare:

| Reference | Band | Where 3.001 raw falls | Where 3.32 corrected falls |
|---|---|---|---|
| Project guide, "observed P/N range" for this engine (`docs/ford-3.7-cyclone-6r80-guide.md` §2D, marked **Level 3 — observed, not an acceptance limit**) | 3.17–3.63 g/s | **below** | **inside, mid-band** |
| ~1 g/s per litre rule of thumb [community heuristic, same guide] | ≈ 3.73 g/s | below | 11 % below |
| 0.8–1.2 g/s per litre for a warm engine [community, general] | 2.98–4.47 g/s | at the bottom edge | comfortably inside |

**Verdict: the idle airflow is normal.** The 3.004 g/s figure looked low only because it was
being read against sea-level, 20 °C references while the truck is running on 97 kPa air at
37 °C — air that is **9.5 % less dense than standard**. Correct for that and the truck sits
in the middle of the band its own reference guide gives for this engine in Park.

Two further supports:

1. **Measured `Absolute load value` at idle is 13.7–14.5 %** (n=225 across six bursts).
   The MAF-derived figure, referenced to actual ambient density, is 0.5530 / (1.0981 ×
   3.726) = **13.5 %**. The two agree to within one quantisation step. (They are not fully
   independent — both come from the PCM's airflow model — but a MAF transfer-function error
   would still show as the two diverging from a physical VE estimate, and it does not.)
2. **In gear at a standstill** (log `20260905_030915`, n=46 MAF samples excluding
   transients): **3.413 g/s at 578 rpm** = 0.7085 g per cycle. That is **28 % more air per
   cycle at 11 % lower engine speed** than in Park — exactly the torque converter load, and
   exactly the right direction and size. An engine that could not breathe would not be able
   to answer a load step like that.

### 4.3 A real volumetric efficiency at idle CANNOT be calculated — no manifold pressure exists

**Checked exhaustively.** Across all four logs, 89 + 42 + 63 + 78 = 272 column headers were
scanned. There is **no manifold absolute pressure channel of any kind.** The pressure-named
channels present are barometric pressure, EVAP vapour pressure, A/C pressure, four tyre
pressures, and `Calculated boost` — which §2.3 shows is absolute load rescaled.

`docs/scanner-pids.md` records `Manifold absolute pressure (high resolution)` returning
blank on two separate sessions, and `data/readings.csv` records the same at two more
(readings PART2-0031 and PART3-0011).

**What this means:**

- **Cannot be concluded:** a true volumetric efficiency at idle. VE at idle requires the
  density of the charge actually entering the cylinder, and that requires manifold pressure.
  Everything at idle is throttled to roughly a quarter of atmospheric, so a VE referenced to
  ambient (13.5 %) is not a VE — it is a load number.
- **Can be concluded:** the *product* VE × MAP is pinned at **13.6 kPa** by the airflow
  measurement alone. Solving for plausible idle VE values:

| assumed VE | implied manifold pressure (charge at 45 °C) | implied vacuum against 97 kPa |
|---|---|---|
| 40 % | 33.9 kPa | 18.6 inHg |
| 45 % | 30.1 kPa | 19.7 inHg |
| **50 %** | **27.1 kPa** | **20.6 inHg** |
| 55 % | 24.6 kPa | 21.4 inHg |
| 60 % | 22.6 kPa | 22.0 inHg |

  A warm idling engine of this type has VE around 45–55 % and manifold vacuum around
  19–21 inHg. **The measured airflow is consistent with a completely normal manifold
  vacuum**, and it is inconsistent with a badly leaking or badly sealing engine, which would
  need much higher airflow to hold 651 rpm.

**Two cheap captures would close this properly, and neither has been tried:**

1. **Request the plain `Manifold absolute pressure` PID (SAE mode 01 PID $0B), not the
   high-resolution one.** Only the high-resolution variant has ever been requested on this
   truck, and it is a different PID. The standard one is mandatory on all OBD-II vehicles
   and there is a good chance it answers.
2. **A vacuum gauge on a manifold port at warm idle.** Ten dollars, thirty seconds, and it
   settles VE, valve sealing and manifold integrity in one reading. Steady 18–22 inHg is
   healthy; a needle that flutters rhythmically is a valve; a low steady reading is late
   cam timing or a leak.

---

## 5. Cam phasers (Ti-VCT)

### 5.1 The live channel proves less than it appears to

`Variable camshaft actual advance #1` (intake, Bank 1 — passenger side, cylinders 1–3),
pooled across all four logs:

| Log | n | distinct values | peak-to-peak | engine speed range of those samples |
|---|---|---|---|---|
| `2026-09-04 22-23-38` | 7,919 | {0.000, −0.0625} | 0.0625° | **623–724 rpm** |
| `20260905_030915` | 5 | {0.000} | 0.000° | **682–683 rpm** |
| `20260905_034051` (the WOT log) | — | **channel absent entirely** | — | — |
| `20260905_041723` | 11 | {0.000, −0.0625} | 0.0625° | **644–654 rpm** |
| **total** | **7,935** | **two values** | **one 1/16° step** | **623–724 rpm, without exception** |

Two things follow, and the second is the important one.

**First: 0.0625° is exactly 1/16 of a degree — one quantisation step.** The channel is not
"moving 0.062°"; it is reading zero, dithering by one least significant bit. The intake
phaser is genuinely parked.

**Second, and this corrects the framing in `CLAUDE.md`: every one of those 7,935 samples was
taken between 623 and 724 rpm.** The channel was never polled above 724 rpm in any of the
four logs, and it was not being polled at all during the log that contains the wide open
throttle pulls. **These logs contain zero evidence about phaser behaviour under load.**
The statement "cam phasers eliminated at idle" is correct and well supported. Any statement
about phaser behaviour off idle is not supported by this data set at all.

**A parked intake phaser at idle is correct behaviour, not a fault.** Ford's Ti-VCT intake
phaser is spring-and-lock-pin biased to full retard (0° advance) and is held there at idle
to keep valve overlap low and idle quality high. Movement at idle would be the abnormal
finding.

### 5.2 Mode 06 is the only evidence the phasers move — and it is good evidence

| Monitor | TID | Value | Limit | Fraction of allowance |
|---|---|---|---|---|
| VVT Bank 1 (passenger, cyls 1–3) | $85 | **0.06** | 20 | 0.3 % |
| VVT Bank 2 (driver, cyls 4–6) | $85 | **0.05** | 20 | 0.25 % |
| VVT Bank 1 | $82 / $83 / $84 | 0 / 0 / 0 | 20 / 26.45 / 22.36 | 0 |
| VVT Bank 2 | $82 / $84 | 0 / 0 | 20 / 22.36 | 0 |

The 0.06 and 0.05 are, again, roughly one 1/16° step — i.e. zero error to the resolution the
PCM reports.

**The monitor having a result at all is the finding.** A VVT monitor cannot complete without
the PCM commanding the phasers away from their park position and measuring whether the
camshafts followed. It ran, on both banks, and the commanded-versus-actual error came back
at essentially zero. **Ti-VCT phasers, phaser oil control valves, cam drive and cam timing
are all confirmed functional and confirmed matched between banks** — by the one test that
actually exercises them.

**What is still not measured:** how far, how fast and how smoothly the phasers move under
real load, and whether the exhaust phasers behave (the live channel only covers intake
Bank 1, and Mode 06 does not separate intake from exhaust). If phaser response ever needs to
be judged properly, it needs FORScan logging commanded versus actual VCT on both banks
during a 2000–4000 rpm load sweep. Nothing in the current evidence calls for that.

---

## 6. Thermal behaviour — the "81–83 °C then rose to 91–98 °C" shape is explained, and the previous reading is withdrawn

### 6.1 The coolant temperature was not warming up. It was cycling.

`Engine coolant temperature`, log `2026-09-04 22-23-38`, n=1633 samples over 9170 s. The
channel was polled in **bursts separated by gaps of up to 3292 s (55 minutes)**. Reading a
burst-sampled signal as a trend is what produced the "sat at 81–83 then rose" description.

Here is the actual record, with the polling gaps marked:

| time (min) | ECT | note |
|---|---|---|
| 0.0 – 0.2 | 88 → 89 | |
| — | | **gap 425 s** |
| 7.3 – 7.9 | 93 → 95 | |
| — | | **gap 457 s** |
| 15.6 | 83 | |
| — | | gap 659 s |
| 26.6 – 37.3 | 82, dipping to 81 | *coincides with the load episode in §6.3* |
| — | | gap 459 s |
| 45.0 | 90 → 91 | |
| — | | **gap 1015 s** |
| 62.0 – 62.2 | 96 → 97 | |
| — | | gap 368 s |
| 68.5 – 70.0 | **101 → 92 in 69 s, then rising again** | first visible fan cycle |
| — | | **gap 1184 s**, then **gap 3292 s** |
| 144.8 – 152.9 | **continuous, 485 s — see below** | |

### 6.2 The only continuous stretch shows a textbook cooling-fan sawtooth

Minutes 144.8 → 152.9, ECT sampled continuously:

| segment | ECT | duration | rate |
|---|---|---|---|
| 8685.7 → 8734.1 s | **101 → 92 °C** | 48.4 s | **−0.186 °C/s** |
| 8734.1 → 8946.1 s | **92 → 101 °C** | 212.0 s | **+0.042 °C/s** |
| 8946.1 → 8977.4 s | held 101 °C | 31.3 s | 0 |
| 8977.4 → 9022.6 s | **101 → 92 °C** | 45.2 s | **−0.199 °C/s** |
| 9022.6 → 9155.4 s | **92 → 98 °C, still rising at end of log** | 132.8 s | +0.045 °C/s |

**Trough-to-trough period: 288.5 s (4.8 minutes). Cooling is 4.5× faster than heating.**

That asymmetry is the signature and it is unambiguous: something turns on at 101 °C, removes
heat four and a half times faster than the engine is making it, turns off at 92 °C, and the
engine coasts back up. **The cooling fan is working, the thermostat is regulating, and the
cooling system is behaving exactly as designed** — idling for over two and a half hours in
36 °C ambient without ever exceeding 101 °C, with no drift, no creep and no coolant loss.

This is also a positive finding for the **internal timing-chain-driven water pump**: a pump
with a failed or eroded impeller cannot hold a 9 °C regulation band with a 4.5:1 cool/heat
asymmetry at idle. It does not prove the seal is not weeping — nothing here can — but there
is no circulation deficiency.

### 6.3 The 81–83 °C block was real, and it came with a cycling engine load

Minutes ~15 to ~40 are genuinely different from the rest of the session, and coolant
temperature is only one of four things that were different. All four point the same way.

| | minutes 15–40 | minutes 45–192 |
|---|---|---|
| **Coolant temperature** | **81–83 °C** — below the fan-on band entirely | 92–101 °C sawtooth |
| **`Calculated engine load value`** | **oscillating 28.6 % ↔ 36.8 %** (n=627, low state n=359 mean 28.60 sd 0.62; high state n=268 mean 36.75 sd 1.47) | **flat 28.16 sd 0.37** (n=2663) and **28.67 sd 0.36** (n=997) |
| fraction of samples in the "high" state | **42.7 %** | **0.08 % and 0.20 %** |
| **`MAF air flow rate`** | 3.43 → **5.08** g/s within 8 s (n=11) | **3.00 ± 0.06** g/s (n=4131) |
| **`Calculated instant fuel rate`** | **1.344 L/h** (n=11) | **1.002 L/h** (n=940) — **+34 %** |
| **10-second rpm span** (median, n windows) | **67, 70, 61 rpm** (min 10–40) | **31.5 – 41 rpm** for the next 150 minutes |

**The load steps are extremely regular:** 15 rising edges, intervals
12.7, 18.8, 15.5, 15.5, 15.7, 15.4, 15.7, 15.9, 16.2, 15.9, 15.9, 15.8, 15.8, 15.8 s —
**mean 15.75 s, median 15.78 s, sd 1.17 s (7 % jitter)**. On-duration 6.9 s, off-duration
8.9 s. Step size **+8.15 percentage points of load = +29 % relative**.

A 7 %-jitter square wave of this size is a **clutch cycling**, not a control loop and not a
combustion effect.

### 6.4 What it was: almost certainly the air conditioning compressor

Ranked, with the reasoning:

1. **A/C compressor cycling (most likely).** It explains all four observations at once and
   with the right signs:
   - A compressor clutch at idle cycles on a 10–30 s period when the evaporator is near
     setpoint. **15.8 s, 6.9 s on, is a normal cycle.**
   - It is a 2–4 hp load at idle. **+34 % fuel on a ~7 hp idle is +2.4 hp.** Correct size.
   - **Ford commands the cooling fan on whenever the A/C is on.** A fan running continuously
     at idle in still air pulls coolant below the thermostat's regulation point and holds it
     there. **That is precisely the 81–83 °C plateau.**
   - `CLAUDE.md`'s own earlier screenshot measurements record **A/C ON: 64, 76, 64, 81, 75,
     68 rpm spans** and **A/C OFF: 37, 74, 38, 30, 53 rpm**. The first 40 minutes here
     measure **67, 70, 61**; the rest measures **31–41**. The two sets match the two
     populations.

2. **Cooling fan staging on its own** (electric fan stepping speeds, or a viscous clutch
   engaging). Explains the coolant plateau and the load, but a fan does not cycle on a
   15.8 s period — a viscous clutch has a thermal time constant of minutes, and the observed
   fan cycle later in the same log is 288 s.

3. **Alternator load.** Ruled out on size. `[BCM] Vehicle Battery Current` reads +0.886 A
   at 13.85 V during minutes 9.2–15.6 (n=1320) — about 12 W of battery charging. Even a
   heavily loaded alternator is a fraction of the observed step.

4. **Power steering.** Ruled out — the truck was stationary in Park for the entire session.

### 6.5 The consequences for the rest of the investigation

- **`CLAUDE.md`'s statement that this session was "A/C off (`A/C pressure` reads 0 all
  session)" is not supported.** `A/C pressure` reads **exactly 0.000 in every sample of
  every log**, including the driving log recorded in 33 °C Jeddah heat: log 1 n=37,
  `20260905_030915` n=4, `20260905_041723` n=11 — all zero. `docs/scanner-pids.md` already
  records this channel as returning 0 because no sensor is reported. **A channel that
  returns a constant zero under every condition is a dead channel, not a measurement.**
  It cannot establish that the A/C was off, and it should not be cited for that again.
- **The open item "THE AMPLITUDE HALVED ONCE, EARLY IN THE NIGHT — cause not established"
  now has a mechanical candidate with four independent confirmations.** The amplitude did
  not halve; the *first forty minutes were loaded* and the rest was not.
- **The coolant-temperature hypothesis for the halving is dead in both directions.** ECT was
  not a cause — it was a *consequence* of the fan, which was itself a consequence of the
  load. That also explains why the correlation reversed sign above 88 °C: above 88 °C you
  are in the ordinary fan-cycling regime with no A/C, and there is no relationship there to
  find.
- **Settling it costs nothing:** idle in Park for fifteen minutes with the A/C confirmed OFF
  at the panel, logging `MAF air flow rate` and `Calculated engine load value`, then switch
  the A/C ON and log another five minutes. If the 15.8 s, +29 % load square wave appears
  with the A/C and not without it, the question is closed permanently.

---

## 7. The idle hunt is not an airflow phenomenon — a new elimination

This is the one test the air side can contribute to the main investigation, and it has not
been done before.

The longest continuous MAF burst in the whole data set is log `2026-09-04 22-23-38`,
minutes 78.4–83.7: **n=4130 MAF samples at 16.39 Hz over 316 s**, alongside continuous
engine speed. Both were placed on a common 12.5 Hz grid with `on_grid` (NaN across any gap
wider than 0.30 s for MAF, 0.20 s for rpm; 3723 of 3950 grid points valid), and the
spectra compared.

| | Engine speed | MAF |
|---|---|---|
| mean | 651.3 rpm | 3.0117 g/s |
| sd | 7.79 rpm | 0.0674 g/s |
| dominant frequency, 0.1–1.0 Hz | **0.3156 Hz (3.17 s)** | 0.1007 Hz (9.93 s) |
| fraction of 0.05–4 Hz power in the **0.25–0.40 Hz** hunt band | **34.4 %** | **8.9 %** |
| **amplitude at 0.304 Hz** | **0.94 rpm** | **0.0043 g/s = 0.14 % of mean** |
| correlation with rpm at zero lag | — | **+0.077** |

MAF's own broadband distribution, at native rate: 25.7 % of 0.1–6.7 Hz power in 0.1–0.5 Hz,
26.5 % in 0.5–1 Hz, 31.6 % in 1–2 Hz, 15.4 % in 2–4 Hz, **0.9 % in 4–6.7 Hz** — i.e. flat
broadband noise with no peak anywhere, and nothing at the hunt frequency.

**Reading.** The engine is drawing a constant mass of air while its speed swings ±10 rpm at
3.1 s. The 0.0043 g/s figure is below the MAF PID's own 0.01 g/s quantisation step, so the
honest statement of the ceiling is: **any airflow modulation at the hunt frequency is under
0.01 g/s, i.e. under 0.33 % of mean airflow.** If the ±20 rpm swing (±3 % of 651) were being
driven by an airflow swing, that swing would have to be of order ±3 % = ±0.09 g/s —
**about nine times larger than the ceiling this measurement sets, and twenty times larger than the amplitude actually measured.**

**Therefore the following are eliminated as causes of the 3.1 s idle oscillation, from the
air side, quantitatively:**

- a throttle plate moving at idle (already eliminated by direct observation; now confirmed
  independently)
- a cam phaser hunting or oscillating — a phaser moving would change VE and therefore
  airflow
- a sticking, fluttering or oscillating idle air path of any kind
- an intermittent or cycling vacuum leak
- an EVAP purge flow oscillating enough to move torque (purge enters downstream of the MAF
  and would show as the PCM closing the throttle, i.e. as a *fall* in MAF — nothing at
  0.3 Hz appears)
- a valve, valve spring or lifter behaving intermittently in a way that changes breathing

**What is left is torque per unit of air** — mixture, spark or combustion — which is exactly
where the fuel-dither and spark-governor findings already point. The air side now supports
that story independently instead of merely not contradicting it.

**Caveat, stated plainly:** the MAF PID samples at 16.4 Hz and quantises at 0.01 g/s. This
test is decisive for the 0.3 Hz hunt. It says nothing about the felt 8–33 Hz vibration,
which remains out of reach of any OBD channel.

---

## 8. Fuel cut on the overrun — both banks seal, both upstream sensors are fast

Log `20260905_034051`. Both upstream wide-range sensors peg at 29.383 (the top of the PID's
range) whenever the throttle shuts on the overrun, and hold flat.

**Bank 1 (passenger side, cylinders 1–3), longest runs:**

| window (s from log start) | duration | n | engine speed |
|---|---|---|---|
| 180.5 – 227.0 | **46.5 s** | 680 | 1784 → 940 rpm |
| 344.8 – 366.3 | 21.5 s | 335 | 2127 → 1076 rpm |
| 536.3 – 549.4 | 13.1 s | 42 | 1734 → 1094 rpm |

**Bank 2 (driver side, cylinders 4–6), longest runs:**

| window | duration | n | engine speed |
|---|---|---|---|
| 699.1 – 725.7 | **26.6 s** | 412 | 1788 → 1469 rpm |
| 566.0 – 583.6 | 17.5 s | 270 | 1507 → 927 rpm |
| 880.3 – 891.9 | 11.6 s | 189 | 1754 → 985 rpm |

Nine such runs on Bank 1, seven on Bank 2, all reaching the same 29.383 rail and all dead
flat with min = max.

**Mechanically this establishes:** no injector on either bank seeps under real manifold
vacuum; nothing is putting hydrocarbons into either exhaust during a minute of pumping pure
air, which also means **no cylinder is passing oil in any quantity a sensor can see**; and
both upstream sensors sweep the full range instantly in both directions on both banks.

---

## 9. In-gear idle and part-throttle driving

**In gear at a standstill** (`20260905_030915`, `Vehicle speed` 0 for all 50 samples,
engine speed mean 628.6 sd 44.0, range 539–717): MAF **3.413 ± 0.128 g/s** (n=46 after
excluding one transient), engine speed at those samples mean 578 rpm.
Air per cycle **0.7085 g** against **0.5530 g** in Park — **+28 % per cycle at 11 % lower
engine speed**. Correct converter behaviour, correct magnitude, no anomaly.

**Part-throttle city driving** (`20260905_041723`, 0–62 km/h, engine speed to 2314):

| rpm band | n | MAF | VE @ 97 kPa / 42 °C |
|---|---|---|---|
| 500–750 | 128 | 4.28 g/s | 20.3 % |
| 1250–1500 | 91 | 24.46 g/s | 51.3 % |
| 1500–1750 | 10 | 28.21 g/s | 53.3 % |
| 1750–2000 | 6 | 34.21 g/s | 56.5 % |

**These are not engine VE numbers and must not be read as such.** At part throttle the
restriction is the throttle plate, not the engine; the figures reflect how far the pedal was
down. They are included only to show nothing anomalous and to warn against misreading them.
The only VE numbers with mechanical meaning are the wide open throttle ones in §2.2.

Spark advance in this log at ~1630 rpm light cruise: **33.0, 34.0, 35.5, 37.0, 38.5, 39.5,
40.0, 40.0 degrees** (n=10). That much advance at cruise means the PCM is finding no knock
and no need to protect the engine — consistent with a clean chamber, correct cam timing and
good fuel.

---

## 10. Loose ends inside my domain

### 10.1 Knock was never sampled at wide open throttle

`Knock retard` reads **0.0° in all 38 samples across three logs** — but all 38 were taken at
idle or at low-speed city driving. **Neither WOT pull has a single knock sample, and neither
has a single spark advance sample.** The claim "0° knock retard" is true for the conditions
sampled and says nothing about the conditions where knock actually occurs.

The engine reaching 96.5 % load and 6832 rpm without a power fall-off is indirect evidence
that it was not being heavily retarded, and the 33–40° of cruise advance says the same. But
it is indirect.

### 10.2 The inferred ethanol content is wrong, and it matters at wide open throttle

| | value | n |
|---|---|---|
| Before the KAM wipe | **16.078 %** | 109 |
| After the KAM wipe | **19.216 %** | 40 |

Saudi pump fuel is normally E0. This truck is flex-fuel and the PCM *infers* ethanol content
from the oxygen sensors rather than measuring it — there is no flex-fuel sensor in the
reported channel set. The inference is not merely stale; it **increased** across a full
memory wipe and relearn, so the PCM re-derived 19.2 % from live data.

**Mechanically this only matters in open loop, which is wide open throttle.** A PCM that
believes it has E19 in the tank commands roughly 3 % more fuel mass at WOT than it would for
E0, because ethanol's stoichiometric ratio is lower. That is a small enrichment, in the safe
direction, and it will not damage anything. It does mean:

- the 12.3:1 commanded WOT AFR quoted from screenshots is a *commanded* value derived under
  a wrong ethanol assumption, which adds an extra couple of percent of uncertainty to the
  power estimate in §2.3 (already inside the stated ±7 %);
- it slightly reduces peak power and slightly increases fuel consumption at full throttle;
- it is worth a **[VERIFY] against a second scan tool**, as `CLAUDE.md` already flagged.

### 10.3 Learned octane — noted, not usable

−0.6 before the wipe (n=32), 0.0 immediately after (n=5), **+0.081** after relearning
(n=30). The direction is benign — the PCM has learned it does *not* need to protect against
poor fuel on the 95 octane the truck runs. But **the scaling of this channel in this app is
undocumented** and a negative value does not fit the 0–1 range Ford's octane adjust ratio is
usually described with. **[VERIFY] before building anything on it.**

### 10.4 Timing chain and internal water pump

No channel in these logs bears directly on either. What can be said:

- The cooling system holds a clean 92↔101 °C regulated sawtooth for over two and a half
  hours of idling in 36 °C ambient with no drift and no loss (§6.2). A failing internal
  water pump impeller shows first as loss of regulation at low engine speed, and there is
  none.
- 102–105 % VE at 4000–6500 rpm (§2.2) and a VVT monitor error of one quantisation step
  (§5.2) together mean the cam drive is not retarded by any amount that matters. A stretched
  chain retards cam timing and costs top-end VE; neither is present.
- **The known failure mode of this engine — the timing-chain-driven internal water pump
  weeping coolant into the sump — produces no OBD signature at all.** It is found by pulling
  the oil fill cap and the dipstick and looking for emulsion. Coolant level is reported
  steady, so there is nothing to act on, but **this is the one mechanical item on this engine
  that the entire scan-tool phase is structurally blind to**, and it deserves a two-minute
  visual check at every oil change regardless of symptoms.

---

## 11. Suspect parts, ranked

Nothing in this analysis produces a mechanical suspect for the felt vibration. The engine's
breathing, volumetric efficiency, cam timing, catalysts, exhaust, cooling and combustion all
measure healthy. **That is the finding, and it is a real one.** The ranking below is
therefore short and mostly says "leave alone".

| Rank | Item | Action | Confirming test |
|---|---|---|---|
| 1 | **A/C compressor / cooling fan as an intermittent idle load** — the only genuinely abnormal thing found, and it is abnormal only relative to the assumption that the session was unloaded | **TEST — do not replace anything** | 15 min Park idle with the A/C **confirmed off at the panel**, logging `MAF air flow rate` + `Calculated engine load value`, then 5 min with A/C **on**. The 15.8 s / +29 % square wave appearing only with the A/C settles it. Free. |
| 2 | **Manifold vacuum** — the one breathing measurement that has never been made | **TEST** | Vacuum gauge on a manifold port, warm idle in Park. Steady 18–22 inHg = healthy. A rhythmically fluttering needle = a valve. A low steady reading = late cam timing or a leak. Also try the plain `Manifold absolute pressure` PID ($0B) in the app — only the high-resolution variant has ever been requested. |
| 3 | **Internal timing-chain-driven water pump** | **INSPECT — visual only, no work** | Oil fill cap and dipstick, cold: any tan emulsion means coolant in the oil. Two minutes. No evidence of a problem; this is on the list because OBD is structurally blind to it, not because anything points there. |
| 4 | **Ethanol inference (19.2 % on E0 fuel)** | **VERIFY against a second scan tool** | If a second tool also reads ~19 %, it is the PCM's inference and it is wrong; a fuel-system relearn after several tanks is the only remedy and the effect is small. Do not chase it as a fault. |
| 5 | Catalytic converters, both banks | **LEAVE ALONE** | Already settled three independent ways: Mode 06 at 43–44 % of limit and banks within 2.1 %; 215 g/s and 96.5 % load at WOT with no plateau; VE 102–105 %. |
| 6 | Exhaust system, intake, air filter, airbox | **LEAVE ALONE** | Same evidence. An engine with any of these restricted cannot reach 105 % VE. |
| 7 | Cam phasers, phaser oil control valves, timing chain | **LEAVE ALONE** | Mode 06 VVT error 0.06 / 0.05 against a limit of 20, both banks, monitor completed. Top-end VE intact. |
| 8 | Rings, bores, valves, valve seats, head gaskets | **LEAVE ALONE** | 102–105 % VE at 4000–6500 rpm is not achievable with meaningful blow-by or valve leakage. Both banks peg lean and hold flat for 46 s of overrun fuel cut, so nothing is passing oil either. |
| 9 | Thermostat, radiator, fan, coolant circulation | **LEAVE ALONE** | 92↔101 °C regulated sawtooth, cooling 4.5× faster than heating, 2.5 h of idling in 36 °C ambient with no drift. |
| 10 | Catalyst temperature readings, either bank | **DISREGARD ENTIRELY** | Verified to be one PCM model published on two PIDs — 1491/1520 samples exactly equal. It can never carry bank information on this truck. |

---

## 12. What could not be determined, and the capture that would settle each

| # | Question | Why it is open | The capture that settles it |
|---|---|---|---|
| 1 | **True volumetric efficiency at idle** | **No manifold absolute pressure channel exists in any of the four logs.** Only the high-resolution MAP PID was ever requested, and it returns blank. Without MAP, idle VE is unobtainable — the airflow measurement only pins the *product* VE × MAP at 13.6 kPa. | Request the plain `Manifold absolute pressure` PID ($0B) in Car Scanner. If it also returns blank, a **vacuum gauge on a manifold port at warm idle** gives the same answer for ten dollars. |
| 2 | **Whether the phasers move properly under load** | The live cam channel exists in three logs and **all 7,935 samples were taken between 623 and 724 rpm**. It is absent entirely from the log containing the WOT pulls. Mode 06 confirms the phasers move and track, but not how they behave dynamically. | FORScan, logging commanded VCT versus actual VCT on **both** banks, intake **and** exhaust, through a 1500 → 4000 rpm load sweep. Only worth doing if something else ever points there — nothing currently does. |
| 3 | **Knock behaviour at wide open throttle** | All 38 `Knock retard` samples were taken at idle or light city driving. Neither WOT pull captured knock or spark advance. | A single WOT pull with `Knock retard` + `Timing advance` + `Engine RPM` on the graph — three channels, so the polling rate stays high. |
| 4 | **Air/fuel ratio at wide open throttle, measured** | Neither upstream sensor was being polled during either pull. The 12.3:1 figure comes from screenshots, not from these logs. | `Engine RPM` + `Oxygen sensor 1 Wide Range Equivalence ratio` + `Oxygen sensor 5 Wide Range Equivalence ratio` through one WOT pull. This also turns the power estimate from ±7 % into ±4 %. |
| 5 | **What the cycling load in minutes 15–40 actually was** | Four independent observations identify a real, regular, clutch-like 15.8 s load, but `A/C pressure` is a dead channel on this truck and cannot confirm the A/C state, and the fan type on the 2014 3.7 was not established — web sources did not resolve whether it is a belt-driven viscous clutch or an electric fan. **[VERIFY]** | The A/C on/off experiment in §11 row 1. Separately, a thirty-second visual: look behind the radiator — a belt-driven fan bolted to a clutch hub on the front of the engine, or an electric fan in a plastic shroud. |
| 6 | **Whether idle airflow is normal against a real control sample** | The 3.32 g/s corrected figure sits inside the project guide's observed band, but that band is marked **Level 3 — observed, not an acceptance limit**, and no other 3.7 has ever been measured for this project. | The control sample already on the project's list: another 2011–2014 3.7 at warm idle in Park, logging `MAF air flow rate` + `Engine RPM` + `Barometric pressure` + `Intake air temperature` for sixty seconds. Correct both trucks to the same conditions before comparing. |
| 7 | **The felt 8–33 Hz vibration** | Out of reach by physics. The MAF PID's 16.4 Hz sample rate resolves 8 Hz at absolute best, and the airflow test in §7 is decisive only for the 0.3 Hz hunt. First order at 651 rpm is 10.8 Hz and firing is 32.6 Hz. | Not an OBD problem. Accelerometer, as the project already plans. |
| 8 | **Internal water pump seal condition** | Produces no OBD signature of any kind. | Oil fill cap and dipstick inspection for emulsion; coolant level over time. |

---

## Appendix — method notes and channels that must not be trusted

**Loading.** All four logs read with `carscanner_lib.load`, which keeps each channel on its
own true sample times and never fills a blank. Engine speed was interpolated onto other
channels' sample times only where the two nearest real engine-speed samples were within
0.2 s (16.7 Hz polling, so 60 ms typical); `on_grid` was used for spectral work with an
explicit maximum-gap NaN.

**Channels verified to carry no independent information on this truck:**

| Channel | What it actually is | Evidence |
|---|---|---|
| `Power from MAF (hp)` | **1.20000 × MAF** | R² = 1.000000, n=892 |
| `Calculated instant fuel rate (L/h)` | **MAF ÷ 14.63**, i.e. assumes stoichiometric always — **~19 % low at WOT** | fit 0.33035 × MAF + 0.0013, R² = 0.999999, n=891 |
| `Instant engine power (based on fuel consumption)` | derived from the above | — |
| `Calculated boost (bar)` | **0.082718 × Absolute load − 0.916716** | R² = 0.999200, n=992 |
| `Catalyst temperature Bank 1 / Bank 2 Sensor 1` | **one PCM model on two PIDs** | 1491/1520 samples exactly equal, log 1 |
| `A/C pressure (kPa)` | **dead channel** — exactly 0.000 in every sample of every log including the driving log | n=37 + 4 + 11 |
| `Vane position sensor (V)` | variable-geometry turbo channel, not applicable | constant 0, n=40 |

**One correction to the record, for the avoidance of doubt:** the 96.47 % absolute load and
the 215.27 g/s MAF cited together in `CLAUDE.md` come from **two different pulls 53 seconds
apart**, and no single pull in this data set has both channels. The conclusion drawn from
them is unaffected — both pulls independently show healthy breathing — but the two numbers
are not one measurement.
