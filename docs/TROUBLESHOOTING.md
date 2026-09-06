# Pinpoint test — idle vibration, 2014 F-150 3.7

## COMPLAINT
1. Body shake felt in the seat. Idle only. Gone by 1000–1500 rpm.
2. RPM needle jumps. Whole rpm range. Never stops.

## CONFIRMED BY MEASUREMENT
| | |
|---|---|
| Idle oscillation | 0.304 Hz, 3.0 s period, 40 rpm p-p in Park, 15 in Drive |
| Spark | Follows rpm by 0.10 s, r = −0.91. Correcting, not causing |
| Commanded air/fuel | Leads rpm. Explains ~20 % of the swing |
| Unexplained | ~80 % of the swing. No PCM output accounts for it |
| Felt shake | NOT the 0.3 Hz oscillation. Different frequency, never measured |

## RULED OUT — do not spend money here
Fuel delivery · injectors · both upstream O2 · both downstream O2 · both
catalysts · fuel trims · vacuum leaks · purge valve · cam phasers · throttle ·
MAF · breathing · compression · misfire · all Mode 06 tests · all DTCs

---

# TEST 1 — ACCESSORY LOAD
**Aim:** find the unexplained 80 %.

1. Warm engine, Park, standstill.
2. Graph `Engine RPM`. Record 2 min with everything OFF.
3. Turn ON: headlights, high beam, blower max, rear demist, hazards.
4. Record 2 min more.

| Result | Meaning | Go to |
|---|---|---|
| Swing gets **smaller** | Load damps it. Disturbance is a torque/load effect | TEST 2 |
| Swing gets **bigger** | An accessory is the driver | TEST 2 |
| **No change** | Not electrical load | TEST 3 |

---

# TEST 2 — COOLING FAN
**Aim:** the fan is the only load known to cycle on its own.

1. Cold start. Graph `Engine RPM` + `Engine coolant temperature`.
2. Idle in Park 25 min without touching anything. Do not switch off.
3. Listen for the fan cutting in and out. Note the time each time.

| Result | Meaning | Go to |
|---|---|---|
| Swing steps at the **same coolant value twice** | Confirmed — fan or thermal | TEST 2A |
| Swing steps but at **different values** | Not temperature. Time or load | TEST 3 |
| No step at all | Earlier step was a one-off | TEST 3 |

## TEST 2A — unplug the fan
Engine off. Unplug the fan connector. Restart, idle in Park, record 2 min.
**Watch coolant — do not exceed 105 °C. Reconnect immediately after.**

| Result | Action |
|---|---|
| Swing drops | Fan clutch/motor drag is a contributor. Inspect fan and its bearing |
| No change | Fan eliminated → TEST 3 |

---

# TEST 3 — CYLINDER BALANCE
**Aim:** the only untried mechanical test the ECU cannot do. Needs no control sample.

1. Warm, Park, graph `Engine RPM`.
2. Unplug **one injector connector**. Wait 15 s. Record the rpm drop.
3. Reconnect. Wait 30 s for rpm to settle.
4. Repeat for all six. Write down six numbers.

| Result | Meaning | Go to |
|---|---|---|
| All six drops **within 15 % of each other** | Cylinders equal. Not a contribution fault | TEST 4 |
| One drop clearly **smaller** | That cylinder is already weak — it is the fault | Compression + leak-down on that cylinder |
| One drop clearly **larger** | That cylinder is carrying more than its share | Same, other five |

**Expect a code to set. It clears itself or with a scan tool.**

---

# TEST 4 — MEASURE THE SHAKE
**Aim:** the felt vibration. No OBD tool can see it. This is the only test aimed at the actual complaint.

1. Phone flat on the seat. Spectrum app (phyphox, Vibration Analysis).
2. Warm idle, Park, 60 s. Then Drive with brake, 60 s.
3. Read the strongest peak.

| Peak | Meaning | Action |
|---|---|---|
| **~33 Hz** | Firing pulse through a bare cab floor | Isolation, not engine. TEST 5 |
| **~11 Hz** | Rotational imbalance | Harmonic balancer, pulley, flexplate |
| **~5.5 Hz** | One cylinder differing | Back to TEST 3 — it missed something |
| **8–15 Hz broad** | Engine rocking on mounts | TEST 5 |
| **Amplitude rising and falling every ~3 s** | The measured oscillation IS reaching the seat | Chase the 0.3 Hz after all |

---

# TEST 5 — MOUNTS AND CONTACT
**Aim:** transmission path. Engine running, Park.

1. Hand on engine → hand on frame rail beside the mount → hand on cab floor.
   Frame nearly as bad as engine = mount is passing it through.
2. Helper watches the engine rock while you shift P → D → R → P.
3. Hand along exhaust, A/C lines, power steering lines, cooler lines, looms,
   heat shields. Find one spot buzzing harder than its neighbours.
4. Push/pull that part while someone reports the seat.
5. Pry bar, gently unload each mount in turn while idling.

| Result | Action |
|---|---|
| One spot buzzes harder / seat changes when pushed | That contact is the path. Clearance or isolate it |
| Frame rail nearly as bad as engine | Mount has lost damping. Replace that mount |
| Nothing found | Report back with TEST 4 frequency and we re-plan |

---

# DO NOT DO
- Do not replace injectors, coils, plugs, O2 sensors, catalysts, purge valve,
  PCV, or the MAF. All measured good.
- Do not smoke test. No lean bias left.
- Do not clear codes or disconnect the battery before a test. It wipes the
  learned data the next measurement depends on.
- Do not chase the 97 kPa barometric reading. Your other truck reads 99.

# CAPTURE SETTINGS, EVERY TIME
Car Scanner · **CSV #2 (Horizontal)** · **Round values OFF** · note gear,
A/C state, coolant, and what you were testing.
