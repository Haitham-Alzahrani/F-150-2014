# Data collection checklist — scan app

Every capture that has been taken, and every one still outstanding, for the
open idle-oscillation investigation on VIN `1FTMF1EM1EFC80632`.

## Method

- Top graph **`Engine RPM`**, bottom graph the named sensor, so both share a
  timebase and lead/lag is visible
- Warm engine, **Park**, **A/C off**, no electrical loads unless the test
  says otherwise
- Let both traces fill the screen before capturing
- Screen width is about **15 seconds**, gridlines every 5 s
- **Always record the bottom graph's axis range.** The app auto-scales, so a
  near-constant value zooms in until one-LSB rounding flicker fills the
  screen and looks like a violent oscillation. See the axis note in
  `f150-diagnosis.md` — this has already caused two misreadings.
- Ignore the Min/Avg/Max readouts: they are **session-cumulative**, not
  per-window. Read the trace itself.

---

## Already captured

| Pair | Result |
|---|---|
| RPM + `Short term fuel % trim - Bank 1` | Trim within ±1.56 %, quantised in 0.78 % steps. ~~**Fuel control eliminated**~~ **WITHDRAWN** — short-term trim is the correction applied *around* the commanded ratio, not the mixture. The dither lives in the command, so flat trim was never evidence of flat mixture. |
| RPM + `Commanded evaporative purge` | Flat ~40 %, drifting one LSB at a time. **Purge eliminated as the driver of the 3.4 s oscillation** — but the valve was later found leaking unmetered air and its replacement removed the shake in D and R. |
| RPM + `Throttle Position Actually` | Static; min = max on wide-axis windows. ~~**Air path eliminated**~~ **OVERSTATED** — it shows only that the PCM does not govern idle with the throttle. It says nothing about air entering elsewhere, and a purge leak was subsequently found. |
| RPM + `Timing advance` | **Swinging 10-13.5°** in rhythm. The governor's only active lever |
| RPM + `Variable camshaft actual advance #1` | 0.00 to −0.06°, two adjacent steps. **VCT eliminated** |
| RPM alone, A/C on vs off | A/C on 64-81 rpm span, off 30-53. Compressor is not the cause |
| Codes, all modules | No P-codes. Four inactive body/network codes |
| Full sensor list, warm idle | Lambda 0.99, knock 0, misfire monitor completed, ECT 93-94 °C |

---

## Outstanding — Tier 1

Highest value first. All paired against `Engine RPM`.

| Bottom graph | Question it answers |
|---|---|
| **`MAF air flow rate`** | Throttle is static, but MAF measures what actually *enters*. Oscillating MAF with a static throttle means air is varying through another path — a leak, PCV flutter, a valve. Flat MAF means air is genuinely constant and the torque variation is combustion or spark. |
| **`Commanded throttle actuator`** | *Actual* throttle position is already measured and static. This is what the PCM **asks** for. Commanded oscillating while actual sits still = the plate is binding. |
| `Calculated engine load value` | Independent cross-check on airflow; should track MAF |
| `Lambda` or `Air:fuel ratio` | Trim is flat — but is the *mixture* still swinging? |
| `Control module voltage` | Electrical instability correlating with rpm; ties to the alternator-ripple and ground hypotheses |

## Outstanding — Tier 2

| Bottom graph | Question it answers |
|---|---|
| `Short term fuel % trim - Bank 2` | Only Bank 1 has been captured. Bank asymmetry localises a fault to three cylinders |
| `Oxygen sensor 1 Wide Range Equivalence ratio` | Upstream bank 1, raw |
| `Oxygen sensor 5 Wide Range Equivalence ratio` | Upstream bank 2, raw. Compare the two — a lazy or differently-behaving sensor shows here |
| `Knock retard` | Should be flat 0. If it spikes, knock is pulling timing and that alone explains the spark swing |
| `Intake air temperature` | Sanity — should be steady. A jumping IAT is a sensor fault |

## Outstanding — Tier 3, values only

No graph needed. Capture the value list twice, a few minutes apart.

- `Catalyst temperature Bank 1 Sensor 1` **and** `Bank 2 Sensor 1` — divergence
  between banks means one bank is running differently
- `Oxygen sensor 2 Bank 1 Voltage` **and** `Bank 2 Voltage` — downstream,
  should sit fairly steady
- `Ethanol fuel percent` — is the 16.08 % reading stable or drifting?
- `Absolute pedal position D` **and** `E` — confirms the pedal is genuinely at rest
- `Gear (AT)` — confirms Park
- `Fuel/Air commanded equivalence ratio`
- `Learned octane`
- `Manifold absolute pressure (high resolution)` — read blank previously.
  **Retry.** If it ever returns a real kPa value it is the single most
  valuable signal available, because MAP oscillating with rpm shows pumping
  variation directly.

## Outstanding — app menus rather than sensors

- **Mode 06 / on-board monitoring test results** — where **per-cylinder
  misfire counts** live. Never obtained, and they directly test combustion
  evenness. The misfire *monitor* passing only means no cylinder crossed a
  threshold.
- **Permanent DTCs (Mode 0A)** — still unread; the only code history a clear
  cannot destroy
- **Freeze frame** — if anything is stored

---

## Physical tests, no scan tool

These now outrank further scanning: every PCM output except spark is static,
so the OBD side is exhausted.

| Test | Pass criterion |
|---|---|
| Alternator AC ripple, DMM on AC volts across the battery at idle | **under 0.1 V AC** — above means a failed diode injecting ripple into every sensor reference |
| Ground drops, DMM on DC mV, idling with loads on: battery negative → block, block → chassis, battery negative → chassis | **each under 0.1 V** |
| Wiggle test — flex and tap the **crank sensor connector and harness first**, then cam sensors, MAF, coils, with the rpm graph visible | **no rpm response** |
| Independent rpm — timing-light tach against the app's reading | the two agree, and the independent one is no steadier |
| Vacuum gauge at warm idle | steady **18-22 inHg**. Not for leaks — trim already excludes those — but for combustion character at a bandwidth OBD cannot reach |
| Cylinder balance — unplug one injector at a time, note each rpm drop | **six roughly equal drops** |
| Phone accelerometer at warm idle | dominant frequency ~33 Hz = firing pulse, normal; ~11 Hz = rotational imbalance |
