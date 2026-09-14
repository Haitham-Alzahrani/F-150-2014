# Full re-test protocol — every item re-eliminated at proper sample rate

Written 2026-09-14 at the owner's request: *"if I want to redo all tests again
with the perfect Hz to re-eliminate every item."*

**Why this exists.** Almost every elimination in this project rests on data
captured at 8–15 samples per second, often with the two channels of interest
never polled at the same instant. Four false findings came from exactly that.
Two channels on screen gives **33 samples per second** and guarantees the pair
lands on the same instants. This protocol re-does the whole differential on that
basis.

## THE RULES — same for every capture

* **Two channels visible. Nothing else on the page.** The rate is set by tiles on
  screen, not by the sensor list. Two gives 33 Hz, three gives 15, four gives 11.
* **Do not touch the phone during a capture.** Every fast stretch in the archive
  ended because a page was switched.
* Screen set to never sleep.
* Warm engine unless the capture says otherwise. Park, standstill, air
  conditioning **off** unless the capture says otherwise.
* Bonnet closed, doors closed, nobody moving around in the cab.
* Export **CSV #2 (Horizontal)**. Never #3 — it invents samples.
* **Write down for each: capture number, odometer, phone clock, air
  conditioning state.**
* Three minutes each unless a longer time is given.

Channel names below are **sensor list labels** — the text as it appears in the
list scrolled on the phone, not the short header the app prints on the graph.

---

## SESSION 1 — COLD START. First thing, engine sat overnight.

**1.1 — 20 minutes. Start the recording BEFORE turning the key.**
```
Engine RPM
Engine coolant temperature
```
Two channels only. The 2026-09-13 cold start had 73 channels and ran at 8.5 Hz;
at 33 Hz the first thirty seconds become readable. Re-tests: whether the
oscillation exists before the fuel loop closes, whether the amplitude steps at
any coolant value, and cold high idle versus warm idle.

---

## SESSION 2 — WARM IDLE IN PARK, AIR CONDITIONING OFF

The core of the protocol. Work down the list without moving the truck.

**2.1 — 20 MINUTES. The most important capture in the project.**
```
Engine RPM
Fuel/Air commanded equivalence ratio
```
Re-tests: does the commanded mixture move BEFORE a large beat. At one large beat
every 82 seconds this catches about 15 of them with the command genuinely
alongside. Decides whether the catalyst dither drives the irregularity or merely
accompanies it.

**2.2**
```
Engine RPM
Timing advance
```
Re-tests: governor gain in degrees per 100 engine speed, and the lag. Previously
measured at 8–15 Hz as 0.10 s lag and 8.0–8.3 degrees per 100. Confirms the
governor is correcting and not causing.

**2.3**
```
Engine RPM
MAF air flow rate
```
Re-tests the strongest unresolved correlation in the project. Airflow swing
explained 31.7 % of beat-to-beat amplitude but was measured simultaneously, so
cause and effect could not be separated. At 33 Hz the lead or lag is measurable.
**If airflow LEADS engine speed, air is driving the beats. If it follows, it is
intake pulsation and downstream.**

**2.4**
```
Engine RPM
Control module voltage
```
Re-tests: supply voltage explained 7.0 % of beat amplitude and the new battery
changed the period jitter significantly. Does voltage lead the beats.

**2.5**
```
Engine RPM
Short term fuel % trim - Bank 1
```
**2.6**
```
Engine RPM
Short term fuel % trim - Bank 2
```
Re-tests the fuel loop response on each bank separately at full rate.

**2.7**
```
Oxygen sensor 1 Wide Range Equivalence ratio
Oxygen sensor 5 Wide Range Equivalence ratio
```
Re-tests: do the two banks genuinely read the same at idle when sampled at the
same instants. Previously 1,490 paired samples gave a 0.052 % difference — good,
but at 15 Hz.

**2.8**
```
Oxygen sensor 2 Bank 1 Voltage
Oxygen sensor 2 Bank 2 Voltage
```
Re-tests a claim that was **withdrawn for lack of overlap**: that the two banks
run their catalyst loops at different rates (3.95 s against 3.26 s), which would
beat against each other every 20 s and explain the period jitter. The original
finding died because Bank 1 was polled 6836–7132 s and Bank 2 7150–7899 s with
zero overlap. One window with both settles it.

**2.9**
```
Fuel/Air commanded equivalence ratio
Oxygen sensor 2 Bank 1 Voltage
```
Re-tests: these two have **zero shared timestamps in every log ever taken**.
If the rear sensor LEADS the command, the catalyst loop is closed feedback. If
it FOLLOWS, the dither is a fixed schedule and the rear sensors are spectators.
Decides whether disconnecting them could change anything.

**2.10**
```
Engine RPM
Absolute load value
```
Re-tests the largest correlation found (72.2 % of beat amplitude, air
conditioning off, n=26). Small sample, simultaneous measurement, direction
unknown. At 33 Hz with a proper sample, lead or lag becomes measurable.

**2.11**
```
Engine RPM
Commanded evaporative purge
```
Re-tests the purge valve, now the new one, at full rate. Purge moves over tens of
seconds; the beat is 3 seconds. Confirms the separation cleanly.

**2.12**
```
Engine RPM
Throttle Position Actually
```
Re-tests: the plate reads dead still at idle on every previous capture (median
movement 0.0000). At 33 Hz, confirms the computer is not moving air at all.

---

## SESSION 3 — LEARNED VALUES. Four channels is fine, these move slowly.

**3.1 — 3 minutes, warm idle in Park**
```
Long term secondary oxygen sensor trim Bank 1
Long term secondary oxygen sensor trim Bank 2
Long term fuel % trim - Bank 1
Long term fuel % trim - Bank 2
```
**The first two have never been read once on this truck.** They read exactly
0.0000 on both banks of the 2023 control. This is the one learned value that
directly modifies the commanded mixture, and a memory wipe has improved the
symptom three times out of three.

**If the first two are not in the sensor list, record that** — it means the
computer does not support them and the hypothesis closes.

**3.2 — values only, photograph the screen**
```
Ethanol fuel percent
Barometric pressure
Distance traveled since codes cleared
# warm-ups since codes cleared
```
Re-tests: inferred ethanol has moved 16.08 → 19.22 → 9.80 across the project
with no change of fuel. Barometric pressure read 97 kPa at sea level, about 4 %
low, and was never confirmed against local weather. The last two date the
adaptives.

---

## SESSION 4 — AIR CONDITIONING ON, warm idle in Park

**4.1**
```
Engine RPM
Absolute load value
```
Re-tests the compressor as a load step: 15.78 s period, load 28.6 to 36.8 %,
which doubles the oscillation. At 33 Hz the engine's ring-down after each
engagement is measurable, which gives the loop's damping directly.

---

## SESSION 5 — IN GEAR AT A STANDSTILL. Foot firmly on the brake.

**5.1 — Drive**
```
Engine RPM
Fuel/Air commanded equivalence ratio
```
**No capture in this project has ever recorded the commanded mixture in gear.**
In gear the engine measures the same as the healthy 2023 (0.780 % against
0.780 %). If the command is identical in Park and in gear while the response
differs 2.4 times, that proves the difference is damping and not the command.

**5.2 — Drive**
```
Engine RPM
Timing advance
```
Re-tests the in-gear governor, previously measured at 15.5–24.0 degrees per 100
against 8.2–9.6 in Park.

**5.3 — Reverse, same pair as 5.1.** The owner has always reported Drive and
Reverse feeling alike; no data has ever tested it.

---

## SESSION 6 — HELD 1500 ENGINE SPEED IN PARK

**The owner's oldest report is that the needle moves at every engine speed, and
it has still never been measured above idle.** The cold start showed the swing is
a fixed 1.19 % at both 651 and 903. This extends it.

**6.1 — hold 1500 steady by hand, 3 minutes**
```
Engine RPM
Fuel/Air commanded equivalence ratio
```
**If the square wave is absent but engine speed still wanders, the catalyst
dither explanation dies outright.**

**6.2 — hold 1500, 3 minutes**
```
Engine RPM
Throttle Position Actually
```
A still plate under a moving foot means the computer is doing it deliberately.

**6.3 — hold 2000, 3 minutes**
```
Engine RPM
Absolute load value
```

---

## SESSION 7 — DRIVING

**7.1 — third gear, pedal fully to the floor to about 5,000, then lift**
```
Oxygen sensor 1 Wide Range Equivalence ratio
Oxygen sensor 5 Wide Range Equivalence ratio
```
**Separates the driver-side fuel offset into a leak versus a biased sensor.**
At full throttle the trims freeze. A fixed leak becomes 0.026 % of that bank's
flow and disappears; a sensor bias persists. The 2026-09-05 pull reached 6,832
but these two sensors have **zero** simultaneous samples in it.

**7.2 — steady 80 km/h cruise, 3 minutes**
```
Long term fuel % trim - Bank 1
Long term fuel % trim - Bank 2
```
Reads the cruise load cell. A fixed-size leak shrinks with airflow; a sensor or
airflow calibration error does not.

**7.3 — closed-throttle coast from about 100 km/h down to 30**
```
Oxygen sensor 1 Wide Range Equivalence ratio
Oxygen sensor 5 Wide Range Equivalence ratio
```
Re-confirms both banks' injectors seal and both sensors sweep full range, this
time with the two of them on the same instants.

---

## SESSION 8 — ENGINE OFF AND HANDS-ON. No scanner.

**8.1 — Re-torque the engine and transmission mount bolts.** Fitted 2026-09-06,
driven since, never re-torqued. Targets the felt symptom, which the data has
twice shown is separate from the oscillation. **Do this one first.**

**8.2 — Ground voltage drops.** Multimeter on direct-current millivolts, engine
idling with headlights and blower on: battery negative to engine block, block to
chassis, battery negative to chassis. **Each under 0.1 V.** Never measured.

**8.3 — Alternator ripple.** Multimeter on alternating-current volts across the
battery posts at idle. **Under 0.1 V.** Above that, a diode is injecting ripple
into every sensor reference in the truck. Never measured.

**8.4 — Positive crankcase ventilation valve.** Pull it, shake it. **No rattle
means blocked.** Twelve years of Jeddah heat and never inspected.

**8.5 — Calibration identifier and verification number.** Read them, photograph
them, give them with the vehicle identification number to Al Jazirah Ford and ask
whether a later calibration was released. The governor's phase margin and the
dither amplitude are both calibration constants. Free, no risk.

**8.6 — Exhaust leak check, driver side.** With the engine cold, start it and
feel and listen along the driver-side exhaust manifold and the pipe joint ahead
of the upstream sensor. A leak there draws air in at low exhaust flow, makes that
sensor read lean, and produces exactly the one-bank fuel offset measured three
separate ways. Soapy water on the joints while cold and idling will show it.

---

## WHAT THIS PROTOCOL CAN AND CANNOT SETTLE

**Can settle, cleanly:**
* Whether the commanded mixture leads the large beats (2.1)
* Whether airflow leads or follows engine speed (2.3)
* Whether the two catalyst loops run at different rates (2.8)
* Whether the catalyst loop is closed feedback or a fixed schedule (2.9)
* Whether a learned rear-sensor value is non-zero on this truck (3.1)
* Whether the driver-side offset is a leak or a sensor (7.1)
* Whether the oscillation exists above idle (6.1)
* Whether the in-gear improvement is damping or a different command (5.1)

**Cannot settle:** what sets the loop's phase margin at 0.32 Hz. That is a
calibration constant and no capture reaches it. If everything above comes back
clean, 8.5 is the remaining lever.
