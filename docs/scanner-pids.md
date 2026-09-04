# Sensor names as the scan app shows them

**Purpose: when a reading is requested, it must be requested by the exact
label that appears on the phone.** Not an abbreviation, not the engineering
term, not the SAE PID name. The owner navigates a list; a name that does not
match the list wastes his time at the truck.

Every name below was read off the app's **All sensors** screen on the phone,
session 10:26–10:33. Names from graph headers are marked as such, because the
graph screen abbreviates some labels differently from the list.

**Values shown are one instant** and are here only to mark which channels
return data and which come back blank. For measured findings see
[`f150-diagnosis.md`](f150-diagnosis.md).

## The red millisecond number is the response time — read it

Each row carries a red figure in milliseconds at its right. **That is how long
the truck took to answer that request.**

- **A number (e.g. `453ms`) means the channel answered.** It is live.
- **`0ms` with an empty value means the truck did not answer at all.** The
  channel is unsupported on this vehicle, or the app never polled it.

This matters because **a channel can be blank in one session and live in the
next.** Barometric pressure, evaporative system vapor pressure and both wide
range current channels all read blank at 10:26-10:33 and all returned real
values at 01:00. Do not mark a channel unsupported from one blank reading —
check the millisecond figure, and check twice.

---

## Engine — the channels this investigation uses

| Exact app label | That session |
|---|---|
| `Engine RPM` | 661 rpm |
| `Engine RPM x1000` | 0.7 |
| `Engine coolant temperature` | 93–94 °C |
| `Intake air temperature` | 38 °C |
| `Ambient air temperature` | 37 °C |
| `MAF air flow rate` | 2.93 g/sec |
| `Timing advance` | 11.5 ° |
| `Knock retard` | 0 ° |
| `Learned octane` | −0.6 |
| `Variable camshaft actual advance #1` | −0.06 ° |
| `Calculated engine load value` | 27.06 % |
| `Absolute load value` | 14.12 % |
| `Vehicle speed` | 0 km/h |
| `Run time since engine start` | 0.00:37:42, later 0.03:06:10 |
| `Fan speed desired` | **blank, 0ms** |
| `Engine fuel rate` | **blank, 0ms** |
| `Engine oil pressure raw` | **blank, 0ms** |
| `Barometric pressure` | 97 kPa |

## Fuel and mixture

| Exact app label | That session |
|---|---|
| `Short term fuel % trim - Bank 1` | 0.78 %, later 3.13 % |
| `Long term fuel % trim - Bank 1` | 0 % |
| `Short term fuel % trim - Bank 2` | 0 % |
| `Long term fuel % trim - Bank 2` | 0 % |
| `Fuel/Air commanded equivalence ratio` | 14.41 |
| `Lambda` | 0.99 |
| `Air:fuel ratio` | 14.52 |
| `Fuel System Status` | Closed loop, using oxygen sensor feedback |
| `Ethanol fuel percent` | 16.08 % |
| `Fuel level input (%)` | 52.94 % |
| `Fuel level input (V)` | 26.47 L |
| `Free space in fuel tank` | 23.53 L |

**On the graph screen** `Short term fuel % trim - Bank 2` is headed **`STFT B2`**.

## Oxygen sensors

| Exact app label | That session | Position |
|---|---|---|
| `Oxygen sensor 1 Wide Range Equivalence ratio` | 14.92 | Before the converter, bank 1 |
| `Oxygen sensor 1 Wide Range Current (mA)` | **blank** | |
| `Oxygen sensor 5 Wide Range Equivalence ratio` | 14.8 | Before the converter, bank 2 |
| `Oxygen sensor 5 Wide Range Current (mA)` | 0 mA | |
| `Oxygen sensor 2 Bank 1 Voltage` | 0.71 V | After the converter, bank 1 |
| `Oxygen sensor 2 Bank 1 Short term fuel trim` | n/a | |
| `Oxygen sensor 2 Bank 2 Voltage` | 0.73 V | After the converter, bank 2 |
| `Oxygen sensor 2 Bank 2 Short term fuel trim` | n/a | |
| `Catalyst temperature Bank 1 Sensor 1` | 458.9 °C | |
| `Catalyst temperature Bank 2 Sensor 1` | 458.9 °C | |

**Sensor 1 and sensor 5 are the two upstream wideband sensors** — one per bank.
**Sensor 2 Bank 1 and Sensor 2 Bank 2 are the two downstream sensors.**

## Throttle and pedal

| Exact app label | That session |
|---|---|
| `Throttle position` | 12.55 % |
| `Relative throttle position` | 0.78 % |
| `Absolute throttle position B` | 13.73 % |
| `Throttle Position Desired` | 7.29 ° |
| `Throttle Position Actually` | 7.56 ° |
| `Commanded throttle actuator` | 1.18 % |
| `Absolute pedal position D` | 14.9 % |
| `Absolute pedal position E` | 7.45 % |

Note the app carries **two different throttle scales at once** — a percentage
set and a degrees set. They are not the same number and must not be compared.

## Emissions and evaporative

| Exact app label | That session |
|---|---|
| `Commanded evaporative purge` | 41.18 % |
| `Evap. system vapor pressure` | **blank** |
| `Distance traveled with MIL on` | 0 km |
| `# warm-ups since codes cleared` | 3 |
| `Distance traveled since codes cleared` | 101 km |
| `Monitor status since DTCs cleared.` | see diagnosis doc |
| `Monitor status this drive cycle` | see diagnosis doc |
| `OBD standards this vehicle conforms to` | OBD as defined by the EPA |

## Electrical

| Exact app label | That session |
|---|---|
| `Control module voltage` | 13.76 V |
| `OBD Module Voltage` | 14 V |
| `[BCM] Vehicle Battery Voltage` | 13.8 V |
| `[BCM] Vehicle Battery Current` | 1 A |
| `[BCM] Battery SoC` | 88 % |
| `[BCM] Vehicle Battery SoC` | 88 |
| `[BCM] Vehicle Battery B Voltage` | **blank** |
| `[BCM] Vehicle Battery B Current` | **blank** |
| `[BCM] Battery Current: Predicted` | **blank** |
| `[BCM] Battery Quinscent Current: low range` | **blank** |
| `[BCM] Normalized cumulative charge when ignition is on [Cn]` | 121.6 |
| `[BCM] Normalized cumulative discharge from battery with engine on [Cn]` | 10.6 |
| `[BCM] Normalized cumulative discharge from battery with engine off [Cn]` | 2.9 |
| `[BCM] Battery State Detection Status` | **blank** |

**On the graph screen** `Control module voltage` is headed **`ECU voltage`**.

The BCM also lists start/stop readiness flags, all blank on this truck, which
has no start/stop: `[BCM] Battery Voltage too low for Start/Stop`,
`[BCM] Battery Refresh Cycle in progress for Start/Stop`,
`[BCM] Battery Temperature Too Low for auto stop`,
`[BCM] Battery Voltage Too Low for auto restart`,
`[BCM] Battery SoC too low for start/stop`,
`[BCM] Battery Capacity too low for start/stop`,
`[BCM] Battery Current too high for start/stop`,
`[BCM] Battery Voltage too low for cold cranking capability`.

## Transmission and chassis

| Exact app label | That session |
|---|---|
| `Gear (AT)` | 1 |
| `ATF temperature var.3` | 87.13 °C |
| `PCM Odometer` | 131,313 km |
| `(ABS) Front left wheel speed` | **blank** |
| `(ABS) Front right wheel speed` | **blank** |
| `[BCM] Left Front Tire Pressure` | 237.53 kPa |
| `[BCM] Right Front Tire Pressure` | 211.68 kPa |
| `[BCM] Right Rear Outer Tire Pressure` | 247.88 kPa |
| `[BCM] Left Rear Outer Tire Pressure` | 247.88 kPa |
| `[BCM] Right Rear Inner Tire Pressure` | 0 kPa |
| `[BCM] Left Rear Inner Tire Pressure` | 0 kPa |

## Returns blank on this vehicle — do not request these

Confirmed over two sessions, blank with `0ms` in both:

| Exact app label | Note |
|---|---|
| `Manifold absolute pressure (high resolution)` | 0ms both sessions |
| `Oil Life %` | 0ms both sessions |
| `(ABS) Front left / right / Rear left / Rear right wheel speed` | 0ms both sessions |
| `Fan speed desired` | 0ms |
| `Engine fuel rate` | 0ms |
| `Engine oil pressure raw` | 0ms |
| `[BCM] Vehicle Battery B Voltage` / `B Current` | 0ms — second battery, not fitted |
| `[BCM] Battery Current: Predicted` | 0ms |
| `[BCM] Battery Quinscent Current: low range` | 0ms |
| `[BCM] Battery State Detection Status` | 0ms |

**These were wrongly listed as unsupported and DO work** — they returned blank
at 10:26-10:33 and real values at 01:00:

| Exact app label | 01:00 value |
|---|---|
| `Barometric pressure` | **97 kPa** |
| `Evap. system vapor pressure` | **−412.5 Pa** |
| `Oxygen sensor 1 Wide Range Current (mA)` | **−0.07 mA** |
| `Oxygen sensor 5 Wide Range Current (mA)` | **−0.09 mA** |
| `DPF average distance between regen` | Diesel channel — not applicable |
| `DPF failed regens` / `DPF failed regens (average)` | Diesel channel — not applicable |
| `Vane position sensor` | Reads 0 V — variable-geometry turbo channel, not applicable |
| `A/C pressure` | Reads 0 kPa — no sensor reported |
| `Calculated boost` | Reads 0.22 bar — meaningless on a naturally aspirated engine |

## App-computed, not measured — ignore for diagnosis

These are the app's own arithmetic from other channels, not readings from the
truck. They carry no independent information:

`Instant engine power (based on fuel consumption)` ·
`Power from MAF` · `Vehicle acceleration` · `Average speed` ·
`Calculated instant fuel consumption` · `Calculated instant fuel rate` ·
`Distance to empty` · `Distance travelled` and its Today/total/Week variants ·
`Fuel used` and its Week/total variants · `Fuel used price` and its variants ·
`Average fuel consumption` and its Today/total/Week/10 sec variants ·
`Fuel economizer (based on fuel system status and throttle position)` ·
`Current time` · `Reset distance, fuel used, avg.speed, avg.fuel consumption`

---

## Rules for using this file

1. **Request by the exact label.** If a channel is not in this file, say so
   rather than inventing a plausible name.
2. **The graph screen abbreviates.** Where a graph header differs from the list
   label, both are recorded above. Ask by the list label; the owner finds it
   there.
3. **Never quote the app's Min / Avg / Max fields.** They are cumulative over
   the whole session, not the window on screen. Read the plotted curve.
4. **Date every screenshot by the phone clock**, and never compare a reading
   from one session against a reading from another.
5. **Two channels can be graphed together**, and either channel is selectable —
   `Engine RPM` is not fixed. Pairing two channels on one time axis is the
   strongest measurement this app can make.
