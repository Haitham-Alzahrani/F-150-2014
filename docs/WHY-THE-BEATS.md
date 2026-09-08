# Why the 2014's idle beats — the deepest analysis this data supports

2026-09-06. Every number measured from the four 2014 logs and the three 2023
control logs. Bank 1 = passenger side, cylinders 1-2-3. Bank 2 = driver side,
cylinders 4-5-6.

---

## 1. The "irregular" character is NORMAL — both trucks do it

The beats are not a fault. A spectrogram of each truck, 120-second windows:

| | 2014 3.7 | 2023 5.0 |
|---|---|---|
| Dominant frequency | 0.302 Hz | 0.175 Hz |
| **How much it wanders** | **±9.3 %** | **±15.2 %** |
| Envelope swing (p10 → p90) | 0.71 → 9.26 rpm, **13.0×** | 0.22 → 3.14 rpm, **14.6×** |
| Beat period | one every 100 s | one every 178 s |
| Period-to-period correlation | +0.19 | +0.16 |

**The healthy truck wanders MORE and beats just as much.** Neither engine holds a
fixed rate; both drift, and drifting frequency plus a fixed observation window is
what makes an oscillation look like it comes in irregular bursts.

The lag-1 correlation of successive periods is near zero on both, so the jitter
is random rather than a pattern such as alternating long-short cycles. **This is
a driven loop with a variable delay, not a resonance and not a chaotic system.**

**So the irregularity is not the finding. The size is.**

---

## 2. What is different: the loop runs twice as fast and three times as big

| | 2014 3.7 | 2023 5.0 | Ratio |
|---|---|---|---|
| Oscillation frequency | **0.302 Hz** | 0.175 Hz | **1.7× faster** |
| Averaged cycle amplitude | **17.32 rpm** | 5.24 rpm | **3.3× bigger** |
| Q factor (damping) | **6.3** | 3.3 | **1.9× less damped** |

---

## 3. The mechanism — Ford's own documentation names it

The 0.30 Hz mixture command comes from **fore/aft oxygen sensor control**, the
slow loop that keeps the catalyst's oxygen store half full. Its rate is set by
**how much oxygen the converter can hold.**

Ford's OBD System Operation Summary states the relationship directly:

> *"When the catalytic converter is storing oxygen properly, the downstream HO2S
> sensors provide low-frequency voltage signals. Conversely, when the catalyst's
> oxygen storage capacity declines, the switching frequency increases."*
>
> *"High efficiency catalysts reduce the amplitude of rear HO2S switches compared
> to the switching frequency and amplitude of the front HO2S."*

**Both of Ford's stated indicators — faster switching AND larger amplitude — are
what this truck shows against the control.**

### What the downstream sensors actually do on the 2014

Paired at the same instants, both banks, warm Park idle (287 simultaneous samples):

| | Bank 1 (passenger) | Bank 2 (driver) |
|---|---|---|
| Mean | 0.637 V | 0.664 V |
| Standard deviation | 0.201 | 0.176 |
| **Peak to peak** | **0.700 V** | **0.705 V** |
| **Time spent at the rails** (<0.25 V or >0.75 V) | **46 %** | **48 %** |

**A post-catalyst sensor on a converter with good oxygen storage sits nearly
still.** These swing across almost the full sensor range and spend close to half
their time pinned at one end or the other.

### And the control truck

| | Peak to peak | At the rails |
|---|---|---|
| 2023, Bank 1 | **0.125 V** | — |
| 2023, Bank 2 | **0.145 V** | — |
| 2023, second file, both banks | **0.010 V and 0.000 V** — flat at 0.72 V | 0 % |

**Five to seventy times less movement.** The second file shows the textbook
picture: a downstream sensor pinned at a steady voltage, not switching at all.

---

## 4. The complete chain, every link measured

```
catalyst oxygen storage reduced by age and heat
  ↓  downstream sensor can no longer be held steady
downstream O2 swings 0.70 V peak-to-peak, 47 % of the time at the rails
  ↓  the fore/aft loop reacts to that sensor
mixture command dithers at 0.30 Hz, ±0.23 AFR — 1.7× faster than the control
  ↓  coherence 0.70-0.79 at exactly 0.30 Hz, five windows, two nights
engine torque swings ±0.38 N.m
  ↓  gain 24-30 rpm per AFR unit
ENGINE SPEED OSCILLATES 38 rpm at 0.30 Hz
  ↓  governor applies 1.75 degrees of a 47 degree authority
nothing damps it — Q = 6.3 against the control's 3.3
```

---

## 5. The counter-evidence, stated plainly

**The PCM's own catalyst monitor passes both converters with 56 % margin.**
Bank 1 scored 0.3711 and Bank 2 0.3633 against a 0.8359 limit — both at 44 % of
the failure threshold and within 2.1 % of each other. **There is no P0420 or
P0430 and there never has been.**

Three things reconcile that with the above:

1. **The monitor runs at part-throttle cruise, not idle.** Idle is the worst
   operating point for a converter — lowest flow, lowest temperature. A converter
   with reduced but adequate storage passes at cruise and still fails to buffer
   at idle.
2. **The monitor's threshold is set for emissions failure, not for as-new.** A
   converter at 44 % of the failure limit has lost storage relative to new while
   remaining legal and functional.
3. **Age.** Twelve years, 131,000 km, Jeddah heat. The oxygen-storage component
   of a converter degrades thermally long before conversion efficiency fails.

**The claim is NOT that the catalysts are failed. It is that their oxygen storage
is reduced relative to a two-year-old truck's, and that this sets the fore/aft
loop faster and larger.**

---

## 6. What is NOT established

* **The 2023's downstream sensors were never sampled at idle.** Its comparison
  figures come from 895-1388 rpm, where any converter buffers better. **Some of
  the 5-70× difference is operating condition, not health.** This is the single
  biggest gap in the argument.
* **The fore/aft loop was never observed closing on this truck.** Only 26-40
  samples of the downstream sensor and the fuel command exist simultaneously
  across all four logs — far too few.
* **One control vehicle**, a 5.0 V8 nine model years newer, is not a population.

## 7. What would settle it — two captures

**On the 2014:** `Fuel/Air com. ratio` + `O2S2 volt. (B1)`, three minutes, warm
Park idle. If the downstream sensor leads the fuel command, the loop is confirmed
closed and this whole chain is proven end to end.

**On the 2023:** `O2S2 volt. (B1)` + `Engine RPM`, three minutes at true warm
stationary idle. That removes the operating-condition objection and makes the
comparison exact.

**Neither needs a part, a tool, or a workshop.**

---

## 8. A false finding caught, for the record

An intermediate result showed a Ford switch-count ratio of **0.429 on Bank 1
against 0.031 on Bank 2** — a fourteen-fold bank asymmetry that would have been a
major finding. **It was an artefact of the two sensors being sampled in different
windows.** Restricted to the 287 genuinely simultaneous samples, the banks are
the same: standard deviations 0.201 against 0.176, peak-to-peak 0.700 against
0.705, time at the rails 46 % against 48 %.

**Both converters behave identically.** This is the fourth time in this project
that comparing two channels across non-overlapping windows produced a false
asymmetry, and the second time on these same two sensors.
