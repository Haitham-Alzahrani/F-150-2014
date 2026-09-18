# DIAGNOSTIC DASHBOARD — 2014 F-150 3.7 Ti-VCT

**Built 2026-09-18 from 44 archived logging sessions. NOT a live link.**
No reading here was taken today; every figure names the session it came from.
A cloud session cannot reach the truck — see `CLAUDE.md`.

State: **ANOMALY DETECTION → DISCRIMINATING TEST**, blocked on a physical
measurement only the owner can take.

---

## VEHICLE

| | | evidence |
|---|---|---|
| VIN | `1FTMF1EM1EFC80632` | door label |
| Engine | 3.7L V6 Ti-VCT (Cyclone) | VIN position 8 = `M` |
| Transmission | 6R80 6-speed | commanded ratio 4.171 = 6R80 1st (4.17:1) |
| Drivetrain | **4x4 — owner-confirmed**, VIN decodes 4x2 | **unresolved conflict** |
| Odometer | 131,313 km | `PCM Odometer` |
| Calibration | **changed on a dyno 2026-09-16** | +10.2 % power, +10.3 % torque |
| Adaptive memory | wiped at the retune | long term trim 0.0000 both banks |

**Channels: 129 answer on this VIN** — 75 move, 21 constant, 33 are the app's
own arithmetic. 7 more plus 12 `[BCM]` flags are offered and left blank.

---

## CONFIRMED FAULTS

**None.** No powertrain DTC has ever been recorded. Mode 06 passed on every
monitor with margin. This is stated as a finding, not as reassurance — see
UNKNOWN, which is where the unexamined systems sit.

---

## HIGH-CONFIDENCE SUSPECT

### PCM supply voltage sits 0.33 V below the BCM's, and the control shows no such gap

| 2026-09-04, engine 602–812 rpm throughout | n | median | in 13.5–14.5 V |
|---|---|---|---|
| `Control module voltage` (PCM, HS-CAN) | 3,276 | **12.67 V** | **0.7 %** |
| `[BCM] Vehicle Battery Voltage` (BCM, MS-CAN) | 2,756 | **13.00 V** | **47.9 %** |
| **2023 control, same two channels** | 10 / 3 | **13.47 / 13.40** | agree within **0.07 V** |

**Causes still plausible:** resistance in the PCM's feed or ground · the channel
reporting a post-regulator rail rather than raw supply · a genuinely weak
charging system.
**Eliminated:** "smart charging explains it" as stated — that rested on a single
13.8 V snapshot, and the BCM median across 2,756 samples is 13.00 V.
**Cannot be resolved from logs:** the two channels share a 145-minute span and
coincide **zero times even at 30 s**, because they sit on different buses and
different app pages.
**Why it matters beyond charging:** every sensor reference on this engine rides
on that supply.

Full record: [`VOLTAGE-PCM-VS-BCM.md`](VOLTAGE-PCM-VS-BCM.md).

---

## ACTIVE FINDING — the owner's actual complaint

**A small vibration that accompanies engine speed CHANGING**, plus unsteady
speed. Unchanged by the retune. *(The old seat shake is closed — the mounts
fixed it.)*

| metric | 2014 | 2023 control | ratio |
|---|---|---|---|
| Rate of change at idle | **13.53 rpm/s** | 7.17 | **1.89×** |
| Median 10 s peak-to-peak | **38.0 rpm** | 20.0 | **1.90×** |
| Oscillation energy in one line | **up to 63 %** | 19 % | — |

**Two independent metrics agree at 1.89× and 1.90×.** The idle is measurably
outside what the healthy truck does. **No part has been named**, and the driving
signal is a normal PCM function (catalyst dither) that this engine responds to
roughly twice as hard as the control does.

---

## NORMAL — investigated, evidence supports normal operation

| system | evidence |
|---|---|
| Fuel trims | all four inside ±5 % where the limit is ±10 % |
| Fuel delivery | both banks peg on overrun fuel cut; 12.3:1 at wide throttle |
| Upstream oxygen sensors | 0.014 s response against a 0.4 s limit, both banks |
| Engine breathing | 96.47 % absolute load, 215 g/s, no plateau to 6,832 rpm |
| Catalysts | 0.371 / 0.363 against a 0.836 limit — 44 % of threshold |
| Cam phasers | VVT error 0.06° / 0.05° against a 20° limit |
| Misfire | Mode 06 zero on the 10-cycle average, all six cylinders |
| Idle speed, airflow, spark | 652 rpm, 3.00 g/s, 12.0° |
| Transmission temperature | 92.75 °C max; control reached 97.12 °C |

---

## UNKNOWN — not measured, or measured and unusable

| | why |
|---|---|
| **Transmission under load** | **Never diagnosed.** Commanded vs measured gear ratio exists (n=591) but **every sample is at a standstill**, where measured ratio is a division by zero — the constant 0.829 "error" is a clamp, not slip. Converter slip: 39 samples total, no session with speed. |
| **`Gear (AT)`** | Called a dead channel here. **Withdrawn** — every 2014 sample with a co-sampled speed was at **0 km/h**. Untested, not dead. |
| **Manifold pressure** | Genuinely unavailable on this VIN. Mechanical gauge only. |
| **Per-cylinder contribution** | 8–42 samples each, never with engine speed co-sampled long enough. |
| **Knock sensors** | 48 samples each, never compared at a known idle. |
| **Bank fuel offset** | **Unevaluable** — it changes sign inside one session, range 2.3 points. |
| **Crankshaft signal quality** | No channel reports it. Timing light is the only route. |
| **Fuel in the tank** | PCM infers 9.8–22.4 % ethanol; no sensor exists. Water test settles it. |

---

## USER ACTION REQUIRED — one test, ten minutes, no scanner

**ACTION** — Digital multimeter on DC volts, probes directly on the battery
posts (the lead posts, not the clamps).

**CONDITION** — Engine running, warm, Park, air conditioning off. Then repeat
with headlights and blower on maximum.

**MEASUREMENT** — The voltage, and whether it is steady or moving.

**EXPECTED** — 13.5–14.5 V on a healthy charging system.

**INTERPRETATION**
* **13.5–14.5 V, occasional dips** → charging is fine. The PCM channel reports
  something other than raw supply. **This closes and the suspect is dismissed.**
* **Steady ~12.6 V** → the charging system genuinely is not charging. The BCM's
  47.9 % in-band becomes the reading to distrust.
* **~13.8 V at the battery while the scanner shows 12.6 V** → **a drop in the
  PCM's own supply or ground.** Confirms the suspect.

**NEXT STEP** — On the third result only: voltage drop on DC millivolts, engine
idling with loads on — battery negative → engine block, block → chassis, battery
negative → chassis. **Each under 0.1 V.** Anything above names the bad path.

---

## NEXT TESTS, in order of value per minute

1. **30 min** — `Engine RPM` + `[PCM] Currently Detected Engine Misfire`.
   Two tiles. At 0.44–1.66 events/min that is 13–50 events.
2. **3 min ×2** — both short term trims + `Engine RPM`, then both long term
   trims. **Do not touch the throttle.** All four are needed; four tiles costs
   too much rate to run at once.
3. **A DRIVING capture** — `[PCM] Commanded Gear Ratio` + `[PCM] Measured Gear
   Ratio`, or the two shaft speeds. **The transmission has never been measured
   while moving.** This is the largest untouched system on the truck.

---

## WHERE THE GENERIC PROTOCOL DOES NOT APPLY TO THIS VEHICLE

* **"Clamp or isolate a hose"** — the vacuum lines are hard plastic and cannot
  be clamped. Disconnect and plug the manifold port, **engine off**; opening a
  manifold port on a running engine stalls it. *(Owner's instruction.)*
* **"Read MAP"** — no manifold pressure channel answers on this VIN.
* **"Increase sampling frequency"** — not requestable. Car Scanner's rate is set
  by **how many tiles are on the phone screen**: 2 tiles = 33 Hz, 3 = 15.5,
  7–9 = 2.1. The second tile is free; the third costs half the rate.
* **"Swap two compatible sensors"** — already done. All four oxygen sensors were
  swapped side for side on 09-16, and the result is **unevaluable** because the
  quantity it relied on is not stable.
* **"Compare commanded versus actual"** — valid, but on this truck the
  transmission pair only exists at a standstill, where it means nothing.
