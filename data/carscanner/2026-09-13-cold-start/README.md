# 2026-09-13 08:01 — cold start, the open-loop test

`2026_09_13_08_01_51.csv.gz` — 08:01:51 → 08:21:28, 19.6 min continuous, 73
channels. Recording started **before** cranking: engine speed reads 0 for the
first 78 s, so the crank itself is captured. Coolant starts at **43 °C** (Jeddah
ambient) and reaches 91 °C. Park, standstill, A/C off.

All three requested channels present and, critically, engine speed and the
commanded ratio share a rate: **9,969 and 9,874 samples at 0.117 s.**

## THE TEST FAILED, and the reason is the finding

Closed loop begins **20 s after the engine starts**, at ECT 45.9 °C — not at the
~80 °C the 2023 control shows.

| Phase | Commanded AFR |
|---|---|
| Key on, engine off (t+13 → t+78) | 14.6316, **p2p 0.0000**, one value |
| **Open loop, t+79 → t+99** | p2p **0.0540** |
| t+99 onward | p2p **0.4117** — the dither is running |

The open-loop window is 20 s **during which engine speed falls 1,268 → 931 rpm.**
Detrended (cubic) sd there is **188.66** — the startup ramp, not an oscillation.
There is no steady open-loop idle on this vehicle to measure. In Jeddah's ambient
the oxygen sensors reach operating temperature before the engine settles.

**Consequence: "does the oscillation exist without the dither" cannot be answered
by a cold start on this truck.** The only remaining route is to force open loop
by disconnecting the two upstream oxygen sensors.

## THREE RESULTS THAT DID COME OUT CLEAN

### 1. The oscillation is a fixed FRACTION of engine speed

| | Mean rpm | Detrended sd | % of idle |
|---|---|---|---|
| Cold high idle (t+115–175) | 903.4 | 10.72 | **1.187 %** |
| Warm idle (t+600–1150) | 651.5 | 7.80 | **1.198 %** |

n = 558 and 4,840. Identical to two decimal places across a 250 rpm difference.
First measurement of the owner's long-standing report that the needle moves at
every engine speed: it does, **by the same percentage**. It also rules out
raising idle speed as a fix — the absolute swing scales with it.

### 2. The frequency does NOT scale with engine speed

0.326 Hz (3.07 s) at 905 rpm and at 651 rpm, and in all three separate warm
windows. **A rotating order would shift with engine speed. This does not.**
Together with (1): a torque disturbance of constant fractional size at a fixed
frequency — a control loop or a chemical process, not a moving part.

### 3. COOLANT TEMPERATURE HAS NO EFFECT — hypothesis closed

46 settled idle windows (rpm 600–700), ECT 62 → 90 °C:

| | |
|---|---|
| ECT vs rpm sd | r = −0.219, p = 0.143 |
| ECT vs 10 s span | r = −0.259, p = 0.082 |
| Below 75 °C vs above 85 °C | sd 7.92 (n=13) vs 7.24 (n=8), p = 0.301 |

This is the within-session, temperature-versus-time separation the project has
wanted since the "amplitude halved at minute 40–50" observation, where ECT and
elapsed time were 88 % collinear. On a cold start coolant climbs fast while
elapsed time is short, and the amplitude does not step at any coolant value.
**The minute 40–50 halving was not temperature.**

## Note on channel count

73 channels were enabled, giving 8.5 Hz on engine speed. Adequate here — the
oscillation is 0.3 Hz — but it is not the single-channel 33 Hz capture still
outstanding.
