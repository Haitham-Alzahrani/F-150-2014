# THE COMPLETE SENSOR LIST FOR THIS TRUCK — built batch by batch

**Purpose: read every channel the owner's app offers on this VIN, once, properly,
and stop guessing what is reachable.** This project has repeatedly written that a
measurement "requires FORScan" or "the OBD port cannot see it" without ever
having read the list. At least one of those statements was wrong — per-cylinder
contribution is in the app.

**Status: COLLECTING. Do not draw conclusions until every batch is in.**

| Batch | Images | Session clock | Covers |
|---|---|---|---|
| 01 | 12 | 02:55 – 02:57 | `All sensors` page, `[PCM]` block, `Emission tests` |
| 02a | 9 — all duplicates of batch 01 | — | re-read at full detail |
| 02 | 9 sent, **7 new** | 02:51 – 02:55 | rest of `All sensors`, both wide range oxygen sensors, both banks' trims |

**Rules for this file**
* Every channel is recorded **exactly as the sensor list spells it**, including
  the `[PCM]` prefix, capitalisation and spacing. That label is what the owner
  searches for on the phone.
* A value is recorded **only as evidence the channel answers** — never as a
  measurement. The truck was moving, conditions were not controlled.
* `n/a` means the truck answered "not supported". That is different from the
  channel being absent from the list.
* Nothing here is a finding.

---

## THE APP PRINTS ITS OWN REFRESH TIME BESIDE EVERY CHANNEL

**In red, in milliseconds, on the right of each row.** Nobody in this project had
noticed. It is the app stating, per channel, how long since that value was last
refreshed — the tiles-on-screen rule measured by the app itself.

| Page state | Refresh times seen |
|---|---|
| `All sensors`, whole list scrolling | **324 – 696 ms** |
| GPS-derived channels on the same page | **3 ms** — computed on the phone, never polled |
| Channels scrolled off the visible area | **0 ms** — stale, not being polled at all |

**Two things follow.** With the full list on screen every engine channel updates
at roughly **1.5 to 3 Hz**, against 33 Hz for one tile alone — the same law, now
confirmed by the app's own reporting rather than by counting samples in a log.
And **0 ms marks a channel that is displayed but not being refreshed**, which is
exactly the "configured but idle" state that produced four false findings here.

**Use this at the truck: if the red number beside a channel is not small, that
channel is not being sampled fast enough to analyse.**

---

## BATCH 01 — 12 images, clock 02:55 to 02:57

`data/sensor-list-2026-09-14/batch-01/01.jpg` to `12.jpg`.
Truck was **moving** — 49.5 km/h, gear 5 and 6, ambient 37 °C.

### The `[PCM]` block — absent from every log and from `docs/scanner-pids.md`

| Channel | Reading A | Reading B |
|---|---|---|
| `[PCM] Cylinder 1 Acceleration Value` | −0.03 | −0.02 |
| `[PCM] Cylinder 2 Acceleration Value` | −0.02 | 0 |
| `[PCM] Cylinder 3 Acceleration Value` | −0.03 | 0 |
| `[PCM] Cylinder 4 Acceleration Value` | **−0.08** | — |
| `[PCM] Cylinder 5 Acceleration Value` | −0.02 | — |
| `[PCM] Cylinder 6 Acceleration Value` | 0 | — |
| `[PCM] Desired Electronic Throttle Control` | 15.31 ° | 19.55 ° |
| `[PCM] Actual Electronic Throttle Control` | 15.25 ° | 19.62 ° |
| `[PCM] Knock Sensor 1` | 323 | 293 |
| `[PCM] Knock Sensor 2` | 336 | — |
| `[PCM] Currently Detected Engine Misfire` | 0 | — |
| `[PCM] A/C Pressure` | **1282 kPa** | — |
| `[PCM] Battery voltage` | 12.7 V | — |
| `[PCM] Cylinder head temperature` | 83 °C | — |
| `[PCM] ATF Temperature` | 62.81 °C | — |
| `[PCM] Fuel level` | 86.27 % | 86.67 % |
| `[PCM] Commanded Gear` | 6 | 5 |
| `[PCM] Commanded Gear Ratio` | 0.69 | 0.87 |
| `[PCM] Measured Gear Ratio` | 0.69 | — |
| `[PCM] Actual Turbine Shaft Speed` | 1458 rpm | — |
| `[PCM] Actual Output Shaft Speed` | 2117.75 rpm | — |
| `[PCM] Actual Torque Converter Slip` | 12 rpm | — |
| `[PCM] Desired Torque Converter Slip` | 10.25 rpm | — |

**`[PCM] Measured Gear Ratio` equals `[PCM] Commanded Gear Ratio` to two
decimals** and converter slip is 12 rpm against a commanded 10.25. The
transmission is doing exactly what it is told. Recorded, not interpreted.

### Standard channels confirmed present and answering

| Channel | Reading |
|---|---|
| `Control module voltage` | 13.38 V |
| `Absolute load value` | 14.12 % |
| `Fuel/Air commanded equivalence ratio` | 12.44 |
| `Catalyst temperature Bank 1 Sensor 1` | 642.5 °C |
| `Catalyst temperature Bank 2 Sensor 1` | **642.5 °C — identical** |
| `Ambient air temperature` | 37 °C |
| `Ethanol fuel percent` | 22.35 % |
| `Relative throttle position` | 2.35 % |
| `Absolute throttle position B` | 16.47 / 16.86 % |
| `Absolute pedal position D` | 16.08 % |
| `Absolute pedal position E` | 7.84 % |
| `Commanded throttle actuator` | 3.14 % |
| `Engine RPM x1000` | 1.9 rpm |
| `Fuel level input (V)` | 42.94 L |
| `Free space in fuel tank` | 7.06 L |
| `Monitor status this drive cycle` | MIL:OFF, DTC count 0 |
| `Long term fuel % trim - Bank 1` | −2.34 % |
| `Long term fuel % trim - Bank 2` | −3.13 % |
| `Barometric pressure` | 98 kPa |
| `Timing advance` | 49.5 ° |
| `Commanded evaporative purge` | 0 % |
| `Run time since engine start` | 0:00:11:31 |
| `Distance traveled since codes cleared` | 364 km |
| `# warm-ups since codes cleared` | 7 |

### Not supported — the truck itself answered `n/a`

* `Oxygen sensor 2 Bank 1 Short term fuel trim`
* `Oxygen sensor 2 Bank 2 Short term fuel trim`

### App arithmetic, not readings from the truck — do not analyse these

`Speed (GPS)` · `Altitude (GPS)` · `Average speed (GPS)` · `Average speed` ·
`Average fuel consumption` and its Today / total / Week / 10 sec variants ·
`Calculated instant fuel consumption` · `Calculated instant fuel rate` ·
`Distance travelled` and variants · `Fuel used` and variants · `Fuel used price`
and variants · `Fuel economizer (based on fuel system status and throttle
position)` · `Instant engine power (based on fuel consumption)` ·
`Power from MAF` · `Vehicle acceleration` · `Calculated boost`

**`Calculated boost` read 0.17 bar on one screen and 4.21 bar on another.** This
engine is naturally aspirated and has no boost. The channel is the app computing
something meaningless. `Power from MAF` at 49.68 hp is in the same family, though
it does confirm `MAF air flow rate` is being read.

### `Emission tests` — the monitor list, clock 02:57

**STATUS SINCE DTC RESET — every monitor Completed:**

| Monitor | Supported | Result |
|---|---|---|
| Misfire | Available | Completed |
| Fuel System | Available | Completed |
| Components | Available | Completed |
| Catalyst | Available | Completed |
| Heated Catalyst | Not available | Completed |
| **Evaporative System** | **Available** | **Completed** |
| Secondary Air System | Not available | Completed |
| A/C refrigerant | Not available | Completed |
| Oxygen Sensor | Available | Completed |
| Oxygen Sensor Heater | Available | Completed |
| EGR system | Available | Completed |

**The Evaporative System monitor has now run.** `CLAUDE.md` says it was the one
monitor never completed since the purge valve was fitted, because the fuel level
and cold soak conditions had not been met. They have been met, and it passed.

**CURRENT DRIVE CYCLE STATUS** — Misfire and Fuel System completed; Components,
Catalyst, Evaporative System and EGR system **not completed**. That is a monitor
list partway through a drive, not a fault.

### Still absent from every image so far

* `Long term secondary oxygen sensor trim Bank 1`
* `Long term secondary oxygen sensor trim Bank 2`

### Not yet seen anywhere, and expected to exist

`MAF air flow rate` · `Engine coolant temperature` · `Intake air temperature` ·
`Short term fuel % trim - Bank 1` and `- Bank 2` · the four
`Oxygen sensor N Wide Range Equivalence ratio` channels · `Intake manifold
absolute pressure` · `Engine oil temperature` · `Absolute throttle position` ·
the `[BCM]` block seen in earlier sessions

---

## BATCH 02 — 7 new images, clock 02:51 to 02:55

`data/sensor-list-2026-09-14/batch-02/03.jpg` to `09.jpg`. Two of the nine sent
duplicated batch 01 and were removed.

**The app's own `Current time` channel reads `14:55` while the phone shows
`2:55`.** The phone is on a 12-hour clock and this is the afternoon. Every
"02:5x" in this file means **14:5x**.

The truck was driving throughout — 73 km/h at 1343 rpm, then 32 km/h at 999 rpm.

### BOTH UPSTREAM WIDE RANGE OXYGEN SENSORS EXIST AND ANSWER

**This is outstanding capture #3's channel pair, which `CLAUDE.md` lists as never
obtained.** They are in the list and they return values.

| Channel | 02:51 | 02:55 |
|---|---|---|
| `Oxygen sensor 1 Wide Range Equivalence ratio` | 14.73 | 13.84 |
| `Oxygen sensor 5 Wide Range Equivalence ratio` | 15.12 | 13.8 |
| `Oxygen sensor 1 Wide Range Current (mA)` | −0.01 | −0.38 |
| `Oxygen sensor 5 Wide Range Current (mA)` | +0.08 | −0.42 |

**Not a measurement.** These were read at different refresh moments on a moving
truck, and the two banks' rows carry different millisecond stamps. The pair is
recorded here only to prove both channels are reachable. **The wide open
throttle capture is now possible and should be taken.**

### Both banks' trims, both halves — all four channels present

| Channel | Readings seen |
|---|---|
| `Short term fuel % trim - Bank 1` | 3.13 % |
| `Long term fuel % trim - Bank 1` | **−0.78 % and −2.34 %, both within the same minute** |
| `Short term fuel % trim - Bank 2` | 0 %, twice |
| `Long term fuel % trim - Bank 2` | −3.13 %, twice |

**`Long term fuel % trim - Bank 1` was seen at two different values inside one
minute**, both rows freshly stamped (210 ms and 450 ms). It is moving, so any
single reading of it is a snapshot of a value in motion.

### Newly confirmed channels

| Channel | Readings |
|---|---|
| `Fuel System Status` | **"Closed loop, using oxygen sensor feedback to determine fuel mix"** |
| `Engine coolant temperature` | 84 °C |
| `MAF air flow rate` | 5.02 / 5.08 g/sec |
| `Intake air temperature` | 36 / 37 °C |
| `Calculated engine load value` | 69.02 % |
| `Absolute load value` | 14.12 / 65.49 % |
| `Throttle position` | 13.33 / 14.12 % |
| `Engine RPM` | 1343 / 999 rpm |
| `Vehicle speed` | 73 / 32 km/h |
| `Timing advance` | 49.5 ° / 26.5 ° |
| `Oxygen sensor 2 Bank 1 Voltage` | 0.18 V / 0 V |
| `Oxygen sensor 2 Bank 2 Voltage` | 0.22 V / 0 V |
| `Evap. system vapor pressure` | **85.5 Pa / 34 Pa — it answers** |
| `Commanded evaporative purge` | 0 % / 25.88 % |
| `Control module voltage` | 12.62 V |
| `OBD Module Voltage` | 12.9 V |
| `Current time` | 14:55 |
| `Fuel level input (%)` | 85.49 / 86.27 % |
| `Distance traveled with MIL on` | **0 km** |
| `Auxillary Input Status` | "Power take off: not active" — the app's own spelling |
| `OBD standards this vehicle conforms to` | "OBD as defined by the EPA" |
| `Monitor status since DTCs cleared.` | all Completed — the trailing full stop is the app's |
| `Reset distance, fuel used, avg.speed, avg.fuel consumption` | an action, not a reading |

**`Fuel System Status` is the channel that names the loop state directly.** The
cold start work had to infer open versus closed loop from the commanded ratio's
peak to peak. This channel says it in words.

**`Evap. system vapor pressure` answers.** `docs/scanner-pids.md` lists it among
channels that returned blank. It does not.

**Two separate voltage channels exist** — `Control module voltage` at 12.62 V and
`OBD Module Voltage` at 12.9 V, read minutes apart. Also `[PCM] Battery voltage`.
Three different supply readings, none of them yet compared against each other.

**Two separate load channels exist** — `Calculated engine load value` 69.02 % and
`Absolute load value` 14.12 %, at the same moment. Every load figure in this
project must state which one it came from.

### Still absent from every image so far

* `Long term secondary oxygen sensor trim Bank 1`
* `Long term secondary oxygen sensor trim Bank 2`

### Still not seen

`Intake manifold absolute pressure` · `Engine oil temperature` ·
`Absolute throttle position` (unsuffixed) · `Variable camshaft actual advance` ·
the `[BCM]` block · anything naming a crankshaft or camshaft position sensor
