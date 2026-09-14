# SENSOR INVENTORY — 2014 F-150 3.7, VIN `1FTMF1EM1EFC80632`

**One list. Every log file and every screenshot this project holds for this
truck, scanned in full on 2026-09-14.** It replaces the guesswork in
`docs/scanner-pids.md` about what this truck can and cannot report.

## Exactly what was scanned

| Source | Count | How |
|---|---|---|
| Logging sessions | **44** | every column header and **every value in every row** counted |
| Unique screenshots | **279** of 606 files, de-duplicated by checksum | |
| — old set, `data/screenshots/` | 258 | all 277 extracted text files scanned; the sensor-list pages opened and read directly |
| — this session's batches | 19 | read directly |
| Sensor-list pages inside the old set | **21** | `m105-01` to `-11` and `m182-01` to `-10`, which are **the same 11 screens uploaded twice** — one pass through the list, 2026-09-04 at 22:31 |

Everything else in the old set is a graph screen, a Mode 06 screen, the fault-code
screen, or the accelerometer app — none of which can show a channel the list does
not already carry.

**THE 2023 CONTROL TRUCK WAS EXCLUDED, AND THE EXCLUSION WAS VERIFIED.** The
owner's other F-150 — a 2023 5.0 — was logged with the same phone and app on
2026-09-06, and its files sit in the same folder. Three sessions (17:38:25,
18:20:55, 18:44:59) were removed. **Every one of the 34 channels that dropped out
traces to those three sessions and to nothing else.** Without that step the other
truck's channels land in this truck's inventory — which is exactly what happened
with `Long term secondary oxygen sensor trim`.

**Sample and session counts are evidence of availability, nothing more.** They say
a channel answers on this VIN. They are not measurements.

---

## WHAT THE FULL SCAN CHANGED

**`Long term secondary oxygen sensor trim Bank 1` and `Bank 2` have NEVER been
selected on this truck, and do not appear in any of its 279 screenshots.** The
only two files carrying them are the 2023 control. Status here: **unknown, not
unsupported.**

**Per-cylinder contribution is already logged.** All six
`[PCM] Cylinder N Acceleration Value` channels answered in
`2026-09-14_14-49-23`, quantised in steps of about 0.0156. Only 8 to 42 samples
each across ~20 seconds with the whole list on screen, so nothing to analyse —
but it needs no FORScan.

**Seven channels are offered by the app and left blank by the truck** — found
only by reading the old screenshots, because a channel that returns nothing never
reaches a CSV. See Tier 4.

**`PCM Odometer` reads 131,313 km.** Use that, not "131,000".

**The old sensor-list pass has one gap.** `Abs Wheel Speed 1` to `4`,
`Abs Lateral Accelaration` and `Steering Wheel Angle` were logged on this truck
but appear in **no screenshot at all** — they sit between
`(ABS) Front right wheel speed` and the `[BCM]` block, which no screen captured.

---

## TIER 1 — ANSWERS AND MOVES  (75)

| Channel | Unit | Samples | Sessions |
|---|---|---|---|
| `Engine RPM` | rpm | 307791 | 31 |
| `Engine RPM x1000` | rpm | 307791 | 31 |
| `Short term fuel % trim - Bank 1` | % | 103461 | 31 |
| `OBD Module Voltage` | V | 83084 | 29 |
| `Fuel/Air commanded equivalence ratio` |  | 62953 | 18 |
| `Long term fuel % trim - Bank 2` | % | 62120 | 23 |
| `Long term fuel % trim - Bank 1` | % | 46890 | 32 |
| `Timing advance` | ° | 26725 | 24 |
| `Oxygen sensor 5 Wide Range Current (mA)` | mA | 25341 | 16 |
| `Oxygen sensor 5 Wide Range Equivalence ratio` |  | 25341 | 16 |
| `Short term fuel % trim - Bank 2` | % | 25218 | 30 |
| `Oxygen sensor 1 Wide Range Current (mA)` | mA | 24263 | 19 |
| `Oxygen sensor 1 Wide Range Equivalence ratio` |  | 24263 | 19 |
| `Throttle Position Actually` | ° | 23974 | 10 |
| `Engine coolant temperature` | ℃ | 15358 | 33 |
| `Commanded evaporative purge` | % | 11965 | 13 |
| `Calculated engine load value` | % | 11188 | 28 |
| `Absolute throttle position B` | % | 10446 | 14 |
| `MAF air flow rate` | g/sec | 9366 | 26 |
| `Commanded throttle actuator` | % | 9254 | 14 |
| `Variable camshaft actual advance #1` | ° | 7983 | 7 |
| `Vehicle speed` | km/h | 4592 | 27 |
| `Oxygen sensor 2 Bank 1 Voltage` | V | 4427 | 24 |
| `Control module voltage` | V | 4091 | 14 |
| `Throttle position` | % | 3613 | 27 |
| `Absolute load value` | % | 3228 | 14 |
| `Oxygen sensor 2 Bank 2 Voltage` | V | 3172 | 24 |
| `Catalyst temperature Bank 1 Sensor 1` | ℃ | 3034 | 15 |
| `Catalyst temperature Bank 2 Sensor 1` | ℃ | 3022 | 17 |
| `[BCM] Vehicle Battery Current` | A | 2756 | 1 |
| `[BCM] Vehicle Battery Voltage` | V | 2756 | 1 |
| `Distance traveled since codes cleared` | km | 2402 | 12 |
| `Intake air temperature` | ℃ | 2320 | 24 |
| `Evap. system vapor pressure` | Pa | 2220 | 12 |
| `Barometric pressure` | kPa | 2218 | 14 |
| `[PCM] Actual Electronic Throttle Control` | ° | 2192 | 4 |
| `[PCM] ATF Temperature` | ℃ | 2042 | 6 |
| `ATF temperature var.3` | ℃ | 1828 | 14 |
| `Relative throttle position` | % | 1172 | 14 |
| `Free space in fuel tank` | L | 938 | 16 |
| `Fuel level input (%)` | % | 938 | 16 |
| `Fuel level input (V)` | L | 938 | 16 |
| `# warm-ups since codes cleared` |  | 866 | 12 |
| `Ambient air temperature` | ℃ | 735 | 14 |
| `Absolute pedal position D` | % | 675 | 14 |
| `Absolute pedal position E` | % | 635 | 14 |
| `Ethanol fuel percent` | % | 366 | 16 |
| `[PCM] Desired Electronic Throttle Control` | ° | 288 | 4 |
| `[BCM] Battery SoC` | % | 141 | 3 |
| `[BCM] Vehicle Battery SoC` | A | 141 | 3 |
| `Learned octane` |  | 134 | 7 |
| `Throttle Position Desired` | ° | 132 | 8 |
| `[BCM] Left Front Tire Pressure` | kPa | 131 | 3 |
| `[BCM] Right Front Tire Pressure` | kPa | 124 | 3 |
| `[BCM] Right Rear Outer Tire Pressure` | kPa | 123 | 3 |
| `[PCM] Commanded Gear Ratio` |  | 94 | 4 |
| `[PCM] Fuel level` | % | 94 | 4 |
| `[PCM] Commanded Gear` |  | 92 | 4 |
| `[PCM] Knock Sensor 1` |  | 92 | 4 |
| `[PCM] Knock Sensor 2` |  | 92 | 4 |
| `[PCM] Cylinder 6 Acceleration Value` |  | 84 | 2 |
| `[PCM] Measured Gear Ratio` |  | 76 | 4 |
| `[PCM] Actual Output Shaft Speed` | rpm | 74 | 4 |
| `[PCM] Actual Torque Converter Slip` | rpm | 74 | 4 |
| `[PCM] Actual Turbine Shaft Speed` | rpm | 74 | 4 |
| `[PCM] Desired Torque Converter Slip` | rpm | 74 | 4 |
| `[PCM] Cylinder 1 Acceleration Value` |  | 56 | 2 |
| `[PCM] Cylinder 2 Acceleration Value` |  | 56 | 2 |
| `[PCM] Cylinder 3 Acceleration Value` |  | 56 | 2 |
| `[PCM] Cylinder head temperature` | ℃ | 56 | 2 |
| `[PCM] Cylinder 4 Acceleration Value` |  | 54 | 2 |
| `[PCM] A/C Pressure` | kPa | 40 | 2 |
| `[PCM] Battery voltage` | V | 40 | 2 |
| `Abs Lateral Accelaration` | g | 32 | 2 |
| `[PCM] Cylinder 5 Acceleration Value` |  | 16 | 2 |

---

## TIER 2 — LOGGED, BUT THE VALUE NEVER CHANGED  (21)

**A constant is not a reading.** Each answered every time it was asked and
returned the same number in every sample it ever produced.

| Channel | Unit | Samples | Sessions |
|---|---|---|---|
| `[BCM] Normalized cumulative discharge from battery with engine on [Cn]` |  | 2756 | 1 |
| `[BCM] Normalized cumulative discharge from battery with engine off [Cn]` |  | 2756 | 1 |
| `[BCM] Normalized cumulative charge when ignition is on [Cn]` |  | 2756 | 1 |
| `Distance traveled with MIL on` | km | 583 | 13 |
| `[BCM] Right Rear Inner Tire Pressure` | kPa | 115 | 1 |
| `[BCM] Left Rear Inner Tire Pressure` | kPa | 115 | 1 |
| `[BCM] Left Rear Outer Tire Pressure` | kPa | 115 | 1 |
| `[PCM] Currently Detected Engine Misfire` |  | 102 | 4 |
| `Gear (AT)` |  | 93 | 7 |
| `Knock retard` | ° | 87 | 7 |
| `A/C pressure` | kPa | 79 | 7 |
| `Vane position sensor` | V | 52 | 3 |
| `Abs Wheel Speed 4` | km/h | 32 | 2 |
| `Abs Wheel Speed 1` | km/h | 32 | 2 |
| `Steering Wheel Angle` | ° | 32 | 2 |
| `Abs Wheel Speed 2` | km/h | 32 | 2 |
| `Abs Wheel Speed 3` | km/h | 32 | 2 |
| `PCM Odometer` | km | 24 | 1 |
| `Intake manifold absolute pressure` | kPa | 16 | 1 |
| `Fuel rail press.` | kPa | 10 | 1 |
| `[BCM] Battery Temperature` | ℃ | 8 | 2 |

| Channel | Constant | Reading |
|---|---|---|
| `A/C pressure` | 0 | **Dead.** Use `[PCM] A/C Pressure` — it moves, 1098–1282 kPa. |
| `Gear (AT)` | 1 | **Dead.** Use `[PCM] Commanded Gear` — reports 5 and 6. |
| `Vane position sensor` | 0 | Dead or not fitted. |
| `Intake manifold absolute pressure` | 99 | **The engine was OFF.** All 16 samples came with `Engine RPM` = 0 and `Calculated engine load value` = 0, where 99 kPa is the correct atmospheric answer. **This channel has never once been read with the engine running. It is untested, not dead.** |
| `Fuel rail press.` | 7770 kPa | Impossible on a port-injected engine. **Do not use.** |
| `Steering Wheel Angle` | −6.25 | One session, stationary. Untested. |
| `Abs Wheel Speed 1`–`4` | 0 | One session, stationary. Untested. |
| `[BCM] Left Rear Inner` / `Right Rear Inner Tire Pressure` | 0 | **Correct** — single rear wheels, no inner sensors exist. |
| `Knock retard` | 0 | **Probably real** — 87 samples, 7 sessions, includes wide open throttle. |
| `[PCM] Currently Detected Engine Misfire` | 0 | **Probably real** — 102 samples, 4 sessions. |
| `Distance traveled with MIL on` | 0 | **Real** — the lamp has never been on. |
| `PCM Odometer` | 131313 km | Real. |
| `[BCM] Battery Temperature` | 37 °C | 8 samples. Untested. |
| `[BCM] Normalized cumulative` ×3 | 121.6 / 2.9 / 10.6 | 2,756 samples each in **one** session, all frozen. Suspect. |

---

## TIER 3 — THE APP'S OWN ARITHMETIC, NOT THE TRUCK  (33)

**Never analyse these as vehicle data.** Computed on the phone from GPS or from
other channels. `Calculated boost` reported 0.17 bar and 4.21 bar on a naturally
aspirated engine with no boost.

| Channel | Unit | Samples | Sessions |
|---|---|---|---|
| `Latitude` |  | 375555 | 34 |
| `Longtitude` |  | 375555 | 34 |
| `Air:fuel ratio` |  | 17979 | 13 |
| `Lambda` |  | 17979 | 13 |
| `Altitude (GPS)` | m | 15519 | 36 |
| `Speed (GPS)` | km/h | 15501 | 27 |
| `Average speed (GPS)` | km/h | 15486 | 27 |
| `Power from MAF` | hp | 9366 | 26 |
| `Calculated instant fuel rate` | L/h | 9334 | 34 |
| `Instant engine power (based on fuel consumption)` | hp | 9334 | 34 |
| `Fuel used (Today)` | L | 9247 | 34 |
| `Fuel used (total)` | L | 9247 | 34 |
| `Fuel used (Week)` | L | 9247 | 34 |
| `Fuel used price` | $ | 9247 | 34 |
| `Fuel used price (Today)` | $ | 9247 | 34 |
| `Fuel used price (total)` | $ | 9247 | 34 |
| `Fuel used price (Week)` | $ | 9247 | 34 |
| `Fuel used` | L | 9241 | 26 |
| `Distance travelled (Today)` | km | 4509 | 35 |
| `Distance travelled (total)` | km | 4509 | 35 |
| `Distance travelled (Week)` | km | 4509 | 35 |
| `Average speed` | km/h | 4503 | 27 |
| `Distance travelled` | km | 4503 | 27 |
| `Vehicle acceleration` | g | 4495 | 24 |
| `Fuel economizer (based on fuel system status and throttle position)` |  | 3098 | 28 |
| `Calculated boost` | bar | 2489 | 15 |
| `Average fuel consumption (total)` | L/100km | 1732 | 31 |
| `Average fuel consumption (Week)` | L/100km | 1642 | 29 |
| `Average fuel consumption (Today)` | L/100km | 764 | 20 |
| `Average fuel consumption` | L/100km | 755 | 19 |
| `Calculated instant fuel consumption` | L/100km | 450 | 8 |
| `Distance to empty` | km | 400 | 11 |
| `Average fuel consumption 10 sec` | L/100km | 217 | 17 |

`Air:fuel ratio` and `Lambda` are two presentations of one measurement — identical
sample counts, 17,979 across 13 sessions each. `Power from MAF` tracks
`MAF air flow rate` sample for sample.

---

## TIER 4 — OFFERED BY THE APP, LEFT BLANK BY THE TRUCK

**Found only by reading screenshots.** A channel that returns nothing never
appears in an export, so no amount of log analysis can find these. All seven show
their unit with no value on `m105-02` / `m182-01`, confirmed by opening the image.

| Channel | Why |
|---|---|
| `DPF average distance between regen` | Diesel particulate filter. **This is a petrol engine.** |
| `DPF failed regens` | same |
| `DPF failed regens (average)` | same |
| `Oil Life %` | Offered, not answered on this vehicle |
| `(ABS) Front left wheel speed` | Blank here; **answers on the 2023** |
| `(ABS) Front right wheel speed` | Blank here; answers on the 2023 |
| `Manifold absolute pressure (high resolution)` | Blank **with the engine running at 661 rpm**; answers on the 2023 |

**Twelve `[BCM]` start/stop flags are also offered and blank** —
`Battery Voltage too low for Start/Stop`, `Battery Refresh Cycle in progress for
Start/Stop`, `Battery Temperature Too Low for auto stop`, `Battery Voltage Too Low
for auto restart`, `Battery State Detection Status`, `Battery SoC too low for
start/stop`, `Battery Capacity too low for start/stop`, `Battery Current too high
for start/stop`, `Battery Voltage too low for cold cranking capability`,
`Battery Current: Predicted`, `Battery Quinscent Current: low range`,
`Vehicle Battery B Voltage` and `B Current`. **This truck has no automatic
stop/start system.** Every one of them answers on the 2023, which does.

---

### MANIFOLD PRESSURE IS THE ONE BLANK CHANNEL THAT MATTERS

**Manifold vacuum is the variable this truck's symptom tracks.** `CLAUDE.md`'s
central observation is the load curve — worst in Park and Neutral at the highest
vacuum, less in Drive and Reverse, gone under load. **The truck has never
reported manifold pressure once while running.**

| Channel | Status |
|---|---|
| `Manifold absolute pressure (high resolution)` | **Blank while the engine ran at 661 rpm** (`m105-02`, same pass as `m105-09`). Genuinely unsupported here. |
| `Intake manifold absolute pressure` | **Never tried with the engine running.** 16 samples, engine off, correctly reporting atmospheric. |

**The second one is worth one minute at the truck.** Put it on the page at warm
idle in Park. A healthy 3.7 should read roughly **30–40 kPa** there. If it does,
this project gains the load signal it has been inferring all along from
`MAF air flow rate` and the two load channels. If it stays at 99, manifold
pressure is unreachable through the port and the **vacuum gauge** is the only
route — which `CLAUDE.md` already lists, for combustion character at a bandwidth
the port cannot reach.

**Nothing else that is blank or absent touches the powertrain.** The DPF
counters are for a diesel particulate filter this petrol engine does not have.
`Oil Life %` is a maintenance counter. The ABS wheel speeds, `Abs Lateral
Accelaration` and `Steering Wheel Angle` are chassis channels, and the symptom
reproduces at a standstill in Park where the wheels do not turn. The twelve
`[BCM]` flags are battery management for an automatic stop/start system this
truck does not have.

## TIER 5 — IN THE LIST, NEVER EXPORTED

Text and status fields the exporter does not write.

| Channel | Observed |
|---|---|
| `Fuel System Status` | "Closed loop, using oxygen sensor feedback to determine fuel mix" |
| `Monitor status since DTCs cleared.` | the trailing full stop is the app's |
| `Monitor status this drive cycle` | MIL:OFF, DTC count 0 |
| `OBD standards this vehicle conforms to` | "OBD as defined by the EPA" |
| `Auxillary Input Status` | "Power take off: not active" — the app's own misspelling |
| `Run time since engine start` | 0:00:37:42 |
| `Current time` | phone clock, 12-hour display against the app's 24-hour |
| `Oxygen sensor 2 Bank 1 Short term fuel trim` | **n/a — the truck answered "not supported"** |
| `Oxygen sensor 2 Bank 2 Short term fuel trim` | **n/a — not supported** |
| `Reset distance, fuel used, avg.speed, avg.fuel consumption` | an action, not a reading |

---

## GRAPH HEADER → SENSOR LIST LABEL

**`CLAUDE.md` forbids using graph headers when asking the owner for a reading, and
this project has broken that rule repeatedly.** Here is the mapping, taken from
the screenshots themselves rather than from memory.

| Printed on the graph | The sensor list label to ask for |
|---|---|
| `LTFT - B1` / `LTFT - BI` | `Long term fuel % trim - Bank 1` |
| `LTFT - B2` | `Long term fuel % trim - Bank 2` |
| `STFT B1` | `Short term fuel % trim - Bank 1` |
| `STFT B2` | `Short term fuel % trim - Bank 2` |
| `Tim. adv.` | `Timing advance` |
| `EVAP purge` | `Commanded evaporative purge` |
| `Fuel/Air com. ratio` | `Fuel/Air commanded equivalence ratio` |
| `O2S1 air:fuel` | `Oxygen sensor 1 Wide Range Equivalence ratio` |
| `O2S5 air:fuel` | `Oxygen sensor 5 Wide Range Equivalence ratio` |
| `O2S2 volt.` | `Oxygen sensor 2 Bank 1 Voltage` |
| `OBD Volts` | `OBD Module Voltage` |
| `ECU voltage` | `Control module voltage` |
| `MAF` | `MAF air flow rate` |
| `Calc. eng. load` | `Calculated engine load value` |
| `Abs. load` | `Absolute load value` |
| `Throttle actuator` | `Commanded throttle actuator` |

---

## NAMING COLLISIONS — every figure must say which channel it came from

**Eight throttle channels, in two different units.**

| Channel | Unit |
|---|---|
| `Throttle position` | % |
| `Absolute throttle position B` | % |
| `Relative throttle position` | % |
| `Commanded throttle actuator` | % |
| `Throttle Position Actually` | ° |
| `Throttle Position Desired` | ° |
| `[PCM] Actual Electronic Throttle Control` | ° |
| `[PCM] Desired Electronic Throttle Control` | ° |

**Two load channels, same instant: `Calculated engine load value` 69.02 % against
`Absolute load value` 14.12 %.**

**Four supply voltage channels:** `Control module voltage`, `OBD Module Voltage`,
`[PCM] Battery voltage`, `[BCM] Vehicle Battery Voltage`. Never compared.

**Two transmission fluid temperatures:** `ATF temperature var.3` and
`[PCM] ATF Temperature`.

**Two pedal channels:** `Absolute pedal position D` and `E` — they disagree by
roughly half (16.08 % against 7.84 %), which is normal for a redundant pair.

---

## NOT AVAILABLE ANYWHERE ON THIS TRUCK

Across 129 logged channels and 279 screenshots, nothing reports: crankshaft
position sensor signal quality · camshaft position sensor signal · injector pulse
width · coil dwell · cylinder pressure · engine oil temperature · engine oil
pressure · a plausible fuel rail pressure.

**Consequence: the crankshaft-signal hypothesis cannot be tested through this
port.** It needs a timing light against an independent tachometer.

---

## RULES THAT FOLLOW

1. **Use the label exactly as written here.** These are the exporter's own strings
   and the sensor list's own spellings, misspelling included.
2. **Two tiles on screen, never more,** for anything to be analysed. The app
   prints its refresh time in red beside each row: **30 ms** for one tile,
   **324–696 ms** with the whole list showing, **0 ms** for a channel displayed
   but not polled at all.
3. **Never analyse a Tier 3 channel as vehicle data.**
4. **Never ask the owner for a graph header.** Use the mapping above.
5. **Before writing that a measurement needs FORScan or other hardware, check this
   file.** Per-cylinder contribution was declared unreachable twice and it logs
   through the ordinary app.
