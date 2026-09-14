# SENSOR INVENTORY — 2014 F-150 3.7, VIN `1FTMF1EM1EFC80632`

**One list. Built 2026-09-14 from every log file and every sensor-list screenshot
this project holds for this truck.** It replaces the guesswork in
`docs/scanner-pids.md` about what is and is not reachable.

## How it was built, and why it can be trusted

* **44 logging sessions** were parsed directly — the exporter writes the app's
  exact sensor-list label as the column header, so no name here was read off a
  photograph.
* **Every value in every row was counted.** A channel is listed as answering only
  if it returned at least one non-empty value. A channel whose value never
  changed across every sample it ever produced is listed separately.
* **THE 2023 CONTROL TRUCK WAS EXCLUDED.** The owner's other F-150 — a 2023 5.0 —
  was logged with the same phone and app on 2026-09-06, and its files sit in the
  same upload folder. Three sessions (17:38:25, 18:20:55, 18:44:59) were removed
  before counting. **A sweep that misses this puts the other truck's channels in
  this truck's inventory**, which is exactly how `Long term secondary oxygen
  sensor trim` nearly got recorded as available here.
* **Re-uploaded sessions were de-duplicated by timestamp**, so a session sent
  twice is counted once.

**Sample and session counts are evidence of availability, nothing more.** They
say a channel answers on this VIN. They are not measurements — the conditions
behind them vary from Park idle to wide open throttle.

---

## WHAT THIS ANSWERS

**`Long term secondary oxygen sensor trim Bank 1` and `Bank 2` have NEVER been
selected on this truck.** They appear in exactly two files, both of which are the
**2023 control**. Their status on the 2014 is therefore **unknown, not
unsupported** — nobody has ever put them on the screen. That is a different
finding from the one this project has been carrying, and it is testable in two
minutes by searching the sensor list for `secondary`.

**Per-cylinder contribution has already been logged on this truck.** All six
`[PCM] Cylinder N Acceleration Value` channels answered in
`2026-09-14_14-49-23`, quantised in steps of about 0.0156. Sample counts are 8 to
42 across roughly 20 seconds of driving with the whole list on screen, so there
is nothing to analyse — but the channel is proven to log, and it needs no FORScan.

**The odometer is readable.** `PCM Odometer` returned **131,313 km**, one session,
24 samples, constant. This project has been working from "131,000 km (Aug 2026)".

---

## TIER 1 — CHANNELS THAT ANSWER AND MOVE  (75)

These are the real measurements available through the port on this truck.

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

**A constant is not a reading.** Each of these answered every time it was asked
and returned the same number in every sample it ever produced.

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



| Channel | Constant value | What it means |
|---|---|---|
| `A/C pressure` | 0 | **Dead.** Use `[PCM] A/C Pressure`, which moves (1098–1282 kPa). |
| `Gear (AT)` | 1 | **Dead.** Use `[PCM] Commanded Gear`, which reports 5 and 6. |
| `Vane position sensor` | 0 | Dead or not fitted. |
| `Intake manifold absolute pressure` | 99 | 16 samples, one session, sitting at barometric. **Not established as working.** |
| `Fuel rail press.` | 7770 kPa | Implausible on a port-injected engine. Wrong scaling or unsupported. **Do not use.** |
| `Steering Wheel Angle` | −6.25 | One session, truck stationary. Untested. |
| `Abs Wheel Speed 1–4` | 0 | One session, stationary. Untested. |
| `[BCM] Left Rear Inner` / `Right Rear Inner Tire Pressure` | 0 | **Correct** — single rear wheels, no inner sensors exist. |
| `Knock retard` | 0 | **Probably real.** 87 samples across 7 sessions including wide open throttle. |
| `[PCM] Currently Detected Engine Misfire` | 0 | **Probably real.** 102 samples, 4 sessions. |
| `Distance traveled with MIL on` | 0 | **Real** — the warning lamp has never been on. |
| `PCM Odometer` | 131313 km | Real, and the truck's actual distance. |
| `[BCM] Battery Temperature` | 37 °C | 8 samples only. Untested. |
| `[BCM] Normalized cumulative` ×3 | 121.6 / 2.9 / 10.6 | 2,756 samples each in **one** session, all frozen. Suspect. |

---

## TIER 3 — THE APP'S OWN ARITHMETIC, NOT READINGS FROM THE TRUCK  (33)

**Never analyse these as vehicle data.** They are computed on the phone from GPS
or from other channels, and at least one is provably nonsense: `Calculated boost`
reported 0.17 bar and 4.21 bar on a naturally aspirated engine with no boost.

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

`Air:fuel ratio` and `Lambda` are the app's two presentations of the same
measurement and carry identical sample counts (17,979 across 13 sessions each).
`Power from MAF` tracks `MAF air flow rate` exactly, sample for sample.

---

## TIER 4 — IN THE SENSOR LIST, NEVER LOGGED

Seen in the 2026-09-14 screenshots, absent from every export. Most are text or
status fields the exporter does not write.

| Channel | Observed |
|---|---|
| `Fuel System Status` | "Closed loop, using oxygen sensor feedback to determine fuel mix" |
| `Monitor status since DTCs cleared.` | all monitors Completed |
| `Monitor status this drive cycle` | MIL:OFF, DTC count 0 |
| `OBD standards this vehicle conforms to` | "OBD as defined by the EPA" |
| `Auxillary Input Status` | "Power take off: not active" — the app's own spelling |
| `Run time since engine start` | 0:00:11:31 |
| `Current time` | 14:55 |
| `Oxygen sensor 2 Bank 1 Short term fuel trim` | **n/a — the truck answered "not supported"** |
| `Oxygen sensor 2 Bank 2 Short term fuel trim` | **n/a — not supported** |
| `Reset distance, fuel used, avg.speed, avg.fuel consumption` | an action, not a reading |

---

## NAMING COLLISIONS — every figure in this project must say which channel it came from

**Seven separate throttle channels exist and they do not agree.**

| Channel | Unit | Note |
|---|---|---|
| `Throttle position` | % | |
| `Absolute throttle position B` | % | |
| `Relative throttle position` | % | |
| `Commanded throttle actuator` | % | |
| `Throttle Position Actually` | ° | degrees, not percent |
| `Throttle Position Desired` | ° | degrees |
| `[PCM] Actual Electronic Throttle Control` | ° | |
| `[PCM] Desired Electronic Throttle Control` | ° | |

**Two load channels, read at the same moment: `Calculated engine load value`
69.02 % against `Absolute load value` 14.12 %.**

**Four supply voltage channels:** `Control module voltage`, `OBD Module Voltage`,
`[PCM] Battery voltage`, `[BCM] Vehicle Battery Voltage`. None has ever been
compared against another.

**Two transmission fluid temperature channels:** `ATF temperature var.3` and
`[PCM] ATF Temperature`.

**`A/C pressure` is dead and `[PCM] A/C Pressure` works. `Gear (AT)` is dead and
`[PCM] Commanded Gear` works.** In both cases the prefixed channel is the real
one — the standing instruction in `CLAUDE.md` to never request them again applies
only to the unprefixed pair.

---

## NOT AVAILABLE ANYWHERE — no channel exists on this truck for any of these

Nothing in 129 logged channels or in any screenshot reports: crankshaft position
sensor signal quality · camshaft position sensor signal · individual injector
pulse width · individual coil dwell · cylinder pressure · fuel rail pressure that
reads plausibly · engine oil temperature · engine oil pressure (the
`Engine oil pressure raw` label appears only in the 2023 control).

**Consequence: the crankshaft signal hypothesis cannot be tested through this
port.** It needs the timing-light comparison against an independent tachometer.

---

## RULES THAT FOLLOW FROM THIS FILE

1. **Use the label exactly as written above.** It is the exporter's own string.
2. **Two tiles on screen, never more**, for anything that will be analysed. The
   app prints a refresh time in red beside each channel: 30 ms for one tile,
   324–696 ms with the whole list showing, and **0 ms for a channel that is
   displayed but not being polled at all.**
3. **Never analyse a Tier 3 channel as vehicle data.**
4. **Before writing that a measurement needs FORScan or another tool, check this
   file.** Per-cylinder contribution was declared unreachable here twice and it
   logs through the ordinary app.
