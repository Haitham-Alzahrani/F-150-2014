# IS THERE A PROBLEM IN HOW THE ENGINE RUNS? — the unbiased sweep (2026-09-17)

**Tool: [`data/idle_sweep.py`](../data/idle_sweep.py).** Owner asked directly, and
asked not to be limited to his complaint. This compares **every channel both
trucks recorded at settled idle**, then judges the 2014 on **absolute criteria**
that need no control at all.

Idle is defined per truck as ±8 % of that truck's own median idle, and a channel
sample counts only if an engine-speed sample within 1 s confirms idle at that
moment — so nothing from a blip or a drive leaks in.

## THE ANSWER: no measurable engine fault

Judged against absolute criteria, on the 2014 alone:

| What | p5 | median | p95 | Expected | |
|---|---|---|---|---|---|
| Spark advance at idle | 10.50 | **12.00** | 14.00 | 10–20°, steady | **normal** |
| Short term fuel trim Bank 1 | −2.34 | **0.00** | 4.69 | within ±10 % | **normal** |
| Short term fuel trim Bank 2 | −1.56 | **3.12** | 4.69 | within ±10 % | **normal** |
| Long term fuel trim Bank 1 | −0.78 | **0.00** | 3.12 | within ±10 % | **normal** |
| Long term fuel trim Bank 2 | −0.78 | **1.56** | 2.34 | within ±10 % | **normal** |
| Airflow at idle | 2.94 | **3.00** | 3.37 | 2–5 g/s for a 3.7 | **normal** |
| Idle speed | 636 | **652** | 670 | 600–750 warm in Park | **normal** |
| Coolant | 64 | **80** | 97 | reaches 88–100 warm | **normal** |
| Calculated engine load | 27.8 | **28.2** | 36.9 | 15–35 % | **normal** |

**Every fuel trim sits inside ±5 % where the limit is ±10 %. Spark advance is
mid-range and steady. Airflow is textbook for this engine at idle.** Nothing here
says an engine running badly.

## THE ONE ROW OUTSIDE SPEC — and it is electrical, not combustion

**`Control module voltage` reads 12.49–12.77 V with the engine RUNNING.**
Expected 13.0–14.8 V.

`CLAUDE.md` answers this with Ford's smart charging — the BCM showed 13.8 V and
state of charge rising 88 → 90 %, so the system charges then backs off. **That
explanation is probably right and it has a hole in it:** this file separately
records that **the four supply voltage channels span 1.26 V and three of the four
pairings were never polled together.** The 13.8 V that explains the 12.67 V comes
from a different channel that was never sampled alongside it, and the 12.67 V
itself is **one session**.

**This is the only absolute criterion the engine fails, and it is unresolved
rather than explained.** It matters because every sensor reference runs off the
module supply. **A meter across the battery posts at idle settles it in one
minute** — 13.5–14.5 V with occasional drops is the smart-charging strategy;
a steady 12.6 V with the engine running is not.

## THREE THINGS ARE WRONG WITH THE MEASUREMENTS, NOT THE ENGINE

### 1. `Calculated boost` is garbage on this truck and must never be read

It reads **+0.256 bar at idle**, and across sessions ranges **0.17 to 7.08 bar**.
**A naturally aspirated engine at idle is in deep vacuum. Seven bar of boost is
impossible.**

Traced: **the 2023 reports `Intake manifold absolute pressure` at 28–46 kPa —
correct idle vacuum — and its `Calculated boost` is correctly negative, −0.55 to
−0.73 bar.** The 2014 reports no manifold pressure at all while running, so the
app computes boost from a missing input.

**It is app arithmetic, not a vehicle reading. Add it to the never-analyse list.**

### 2. Manifold pressure is the real gap, and a same-family Ford does report it

`CLAUDE.md` already flags that manifold vacuum is the variable the symptom tracks
and the truck has never reported it running. **The sweep adds that the 2023 does
report it**, which is not proof the 2014's sensor is faulty — nine model years
apart, different supported-PID sets — but it removes "Ford does not offer this"
as the explanation.

**And the channel is NOT dead here:** it answered 99 kPa in 16 samples with the
engine at 0 rpm, which is correct atmospheric. **It has simply never been
selected with the engine running.** One minute at warm idle settles it: roughly
30–40 kPa means the load signal is available at last; still 99 kPa with the
engine running means the sensor or its reporting path is genuinely wrong — and
that WOULD be an engine-run problem, because the PCM's load calculation feeds
fuelling and idle control.

### 3. A POOLING ARTEFACT nearly became a finding — record this

The first pass pooled all samples per truck and reported the 2014's oxygen sensor
pumping current at **−0.074 mA against the control's −0.012** — six times further
from stoichiometric, and 3.5× more variable. It looked like the strongest result
of the sweep.

**It was one session.** Of ~18,500 pooled 2014 samples, **18,232 came from the
09-04 log**, so "the 2014" was that single recording. Per session:

| Session | Median current | Measured AFR |
|---|---|---|
| 2014, 09-04 | −0.078 / −0.066 | 14.59 / 14.61 |
| 2014, 09-05 04:17 | −0.033 / −0.029 | 14.73 / 14.77 |
| 2014, 09-08 22:05 | −0.020 | 14.76 |
| **2023 control** | **−0.012 / −0.008** | **14.77 / 14.82** |

**Every later 2014 session sits on the control.** The 09-04 outlier is the
pre-purge-valve session, with the known vacuum leak and +3.13 % trims.

**Rule: aggregate as the median of per-session medians, never by pooling
samples.** Pooling weights by sample count, and one long log becomes the truck.

## WHAT THIS SWEEP CANNOT JUDGE — state it plainly

**The control has TWO sessions with settled idle, and most channels appear in only
one of them.** Of 50 channels recorded at idle on both trucks, after removing trip
counters and GPS, nearly every comparison is **n=1 against n=1**. There is no
power to detect anything but a gross difference.

**And four measurements that would speak directly to combustion have never been
logged at all:**

* `[PCM] Currently Detected Engine Misfire` — in the sensor list, never recorded
* `[PCM] Cylinder N Acceleration Value` — per-cylinder contribution, one
  screenshot only
* `[PCM] Knock Sensor 1` and `2` — read 323 / 336 in one screenshot, never analysed
* `Intake manifold absolute pressure` with the engine running

**So the honest verdict is: nothing that has been measured shows an engine fault,
and the measurements most likely to show one have not been taken.**
