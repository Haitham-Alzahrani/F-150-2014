# Deep analysis — the truck against the reference guide and published figures

2026-09-06. Every number in the "measured" column comes from the four Car Scanner
logs in `data/carscanner/` (135,000+ engine-speed samples at ~17 Hz), restricted
to warm standstill idle unless stated. Reference values come from
`ford-3.7-cyclone-6r80-guide.md` and from web search.

**What "reference" is worth here.** The guide's idle numbers are Level 3 by its
own classification — observed calibration heuristics, not Ford acceptance
criteria — and the validation record in section 10 of that guide records that no
primary source could be opened from this container. Web search corroborates some
published figures and reaches nothing at all for others. **So a deviation from a
reference below is a lead to test, never a fault proven.**

---

## The abnormality table

| # | Measurement | This truck | Reference | Verdict |
|---|---|---|---|---|
| 1 | **Park idle rpm peak-to-peak** | median **40**, early-session **61–70** | Guide: ≥40 Marginal, >50 Poor | **ABNORMAL** |
| 2 | **Oscillation character** | rhythmic **0.32 Hz**, constant amplitude, hours | Guide: constant-amplitude = control-loop instability / hunting | **ABNORMAL — the guide's own definition** |
| 3 | **Idle spark advance, Park** | mean **12.0°**, all four logs | Guide: P/N **16–22°** BTDC | **4–10° BELOW** |
| 4 | **MAF at Park idle** | **3.004 g/s** | Guide: 3.17–3.63; 1 g/s/L rule: 3.7; general: 2–7 | **Below the guide, inside the general range** |
| 5 | **Barometric pressure** | **97 kPa** (96 in one session) | Sea level ≈ 101 | **~4 kPa low** |
| 6 | **Ethanol fuel percent** | **16.08 % → 19.22 %** | Saudi pump fuel is E0 | **ABNORMAL** (inferred, not sensed) |
| 7 | **Learned octane** | **−0.600 → 0 → +0.081** across the KAM wipe | COBB: −1 = high fuel quality, +1 = low | **Moved a long way — see below** |
| 8 | Drive idle rpm p2p | median **14.8** | Guide: <20 Excellent | Normal — excellent |
| 9 | Idle spark, in gear | **12.76°** | Guide: Drive 12–17° | Normal |
| 10 | Spark peak-to-peak | median **3.0–4.0°** | Guide: ≤4° Excellent | Normal on size; **rhythmic**, so Poor by the corrected rule |
| 11 | Long term trims, post-repair | **−0.78 % both banks** | Near 0 | Normal — excellent |
| 12 | Bank trim difference | **0.00 %** | Guide: <3 % | Normal |
| 13 | Lambda | **0.998** | 1.000 | Normal |
| 14 | Knock retard | **0.000**, always | 0 | Normal |
| 15 | Cam phaser at idle | **0.062°** total movement | parked | Normal |
| 16 | Catalyst temperatures | **460.007 / 460.008 °C** | matched | Normal — within 0.001 |
| 17 | Calculated load at idle | **28.9 %** | ~20–30 | Normal |
| 18 | Control module voltage | **12.67 V** running | 13.5–14.5 | Explained — Ford smart charging |

---

## The three that deserve work

### 3 — Idle spark advance sits 4–10° below the reference range

**12.0° in every log, pre-repair and post-repair, in Park.** The guide puts
Park/Neutral idle at 16–22° BTDC and in-gear at 12–17°. This truck idles in Park
at the value the guide expects **in gear**.

**Why it could matter.** Ford holds a spark reserve at idle so the governor can
add torque instantly by advancing. Sitting near the bottom of the range leaves
less reserve in the advance direction and more in retard, which is exactly the
asymmetry a governor would show if it were working harder than it should.

**Why it may be nothing — and this got weaker on 2026-09-06.** The 16–22° figure
is a Level 3 observed range in the guide, and web search does not support it for
F-150 applications. Forum sources describing F-150 spark advance at idle put it
at roughly **13–16°**, and a 3.5 EcoBoost F-150 at **3–15°**. Both brackets
contain or nearly contain this truck's 12.0°. **The deviation may be against a
wrong reference rather than a wrong engine.** Those are unverified forum
snippets about unspecified engines, so they do not close the item — but they move
it down the list, and the control sample now matters more for settling this than
for anything else. A different calibration, a
different idle target, or a different measurement convention would move it.

**It is not the learned octane.** Octane adjust moved from −0.600 to +0.081
across the reset and **idle spark did not change by a tenth of a degree**
(12.00 / 12.17 / 11.94 across the logs). That is expected — octane adjust
modifies borderline-knock spark under load, and idle is nowhere near knock — but
it does rule out the obvious link.

### 6 and 7 — two KAM values were wiped and are relearning

| | Before the wipe | Immediately after | Later |
|---|---|---|---|
| Learned octane | **−0.5999** (32 samples, constant) | **0** | **+0.0815** |
| Ethanol percent | **16.078 %** | — | **19.216 %** |

**This is the class of thing the central hypothesis needs.** This project's
leading explanation is that *the reset helps and the symptom returns as something
relearns*. Here are two learned values, both destroyed by the battery
disconnect, both relearning — and the D/R shake came back at about the same
distance.

**Two cautions, and they are real:**

* **The direction of "learned octane" is ambiguous.** COBB documents Ford's
  Octane Adjust Ratio as −1 = high fuel quality, +1 = low, but also states that
  the Knock Octane Modifier is the same memory *inverted*, with a different
  label. Car Scanner calls this PID "Learned octane" and which convention it
  follows is unknown. So it is not established whether −0.600 was good or bad.
* **Ethanol 16 % on E0 fuel is inferred, not measured**, and the inference runs
  off the oxygen sensors. It rising to 19 % after a wipe is consistent with
  re-inference, not with the fuel changing.

**Neither has been shown to affect idle.** Idle spark is unchanged across the
whole excursion.

### 5 — barometric pressure, and why it is weaker than it looks

97 kPa where sea level is about 101. But Ford latches this value rather than
sampling it continuously, so the zero variance across 1500 samples is **expected
behaviour, not a stuck sensor** — and it did read 96 in a different session, so
it does update. More decisively: a low baro would bias fuelling lean, and the
**post-repair trims are −0.78 %**, slightly rich. There is no lean bias left for
it to explain.

---

## The 2023 F-150 5.0 — what its one log could and could not settle

A 72-second log from the owner's other truck, VIN `1FTFW1E50PKE57201`, taken
2026-09-01 01:02. **It cannot serve as an idle control: the engine was never
running.** Engine speed reads 0 across all 47 samples, calculated load 0 %,
timing advance −2° (its parked default), manifold pressure equal to ambient.
Coolant at 88 °C and intake air at 67–68 °C say it was a hot soak shortly after
shutdown, key on, engine off. Every channel in the file is a single constant
value.

Two things in it are still worth having.

**It nearly closes the barometric question.** With the engine off, manifold
absolute pressure *is* atmospheric pressure, and the 2023 reads **99 kPa** in the
same city. The 2014 reports barometric **97 kPa**. So the gap is about **2 kPa
against another Ford's sensor**, not 4 kPa against a sea-level textbook value —
and 2 kPa is inside ordinary sensor tolerance. Different days and different
sensors, so this is supporting evidence rather than proof, but it points the same
way as the reasoning that already downgraded this item.

**It puts the trim numbers in perspective.** The 2023 carries learned long term
trims of **−2.34 % on both banks**. The 2014, post-repair, reads **−0.78 % on
both banks** — closer to zero than the two-year-old truck. Whatever else is wrong
here, the fuelling is not it.

**It also names a PID worth retrying on the 2014.** The 2023 returns `Intake
manifold absolute pressure`, which Car Scanner has never returned on the 2014. If
it can be made to answer, manifold pressure at idle would allow a real
volumetric-efficiency calculation and would settle whether the 3.004 g/s MAF
reading is genuinely low or simply what this engine breathes at 652 rpm.

**What is still needed from that truck:** three minutes of `Engine RPM` and
`Timing advance` at warm idle in Park with the **engine running**, A/C off, at a
standstill. That single capture answers two questions this investigation has
carried open since the first night — whether a healthy engine shows a clean
line-spectrum oscillation at idle, and what idle spark advance a Ford truck
actually runs.

---

## What is causing the oscillation

**Measured, not inferred:**

```
commanded AFR dither   leads rpm by 0.00–0.20 s   r = −0.38 to −0.50
engine speed           the disturbance appears here
timing advance         lags rpm by 0.10 s          r = −0.76 to −0.91
short term fuel trim   lags rpm by 0.65 s          r = −0.30
```

**1. The PCM is not driving it with spark.** Spark moves *after* engine speed,
every time, anti-correlated at up to r = −0.91. That is a governor correcting a
disturbance it did not create.

**2. The catalyst dither supplies part of the disturbance.** It leads, with the
physically correct sign — a leaner command precedes a dip in rpm.

**3. About four fifths of the variance is unexplained.** |r| ≈ 0.45 accounts for
roughly 20 %. **No logged PCM output accounts for the rest**: throttle runs on a
19 s rhythm, purge on 17 s, the cam phaser does not move at all.

**4. Whatever supplies the rest is not visible through the OBD port.** The
remaining candidates are loads and mechanical effects that vary on a seconds
timescale — the cooling fan (which the amplitude step points at), alternator
load, power steering — or a cylinder-to-cylinder fuelling non-uniformity that the
closed loop chases without ever resolving.

**5. The felt shake is still a separate problem.** 0.32 Hz cannot be felt as
vibration. What shakes the seat is first order (10.8 Hz) or firing (32.5 Hz), and
the logs sample at 17 Hz — Nyquist 8.3 Hz. **Nothing in this analysis touches the
symptom the owner actually feels.** It never could.

---

## What to do next, in order

**1. Settle the idle spark question — free, and it is now the best lead.**
Log `Engine RPM` + `Tim. adv.` at warm idle in Park on **any other 3.7 or 3.5
Cyclone**. If a healthy one idles at 16–22° and this one sits at 12°, that is a
real finding with a mechanism. If the other one also reads 12°, the guide's range
is wrong for this engine and the lead closes. Same trip answers the rpm question
that has been open since night one: **is 40 rpm peak-to-peak normal on this
engine?**

**2. Cold start with coolant on the graph — free.**
`Engine RPM` + `Engine coolant temperature`, from cold, twenty minutes. The
amplitude halved once mid-session at the same moment coolant stepped 82 → 91 °C.
One repeat decides whether that is temperature, the cooling fan, or coincidence —
and it is the only change in the hunt that no repair caused.

**3. Electrical and accessory load at idle in Park — free.**
Headlights, blower, rear demist, everything on, then off, watching the rpm graph.
This is the direct test for the unexplained four fifths. If amplitude changes
with load, the disturbance is a load; if not, it is internal to the engine.

**4. The accelerometer — free, and it is the only test aimed at the actual
complaint.** Phone flat on the seat, warm idle, Park then Drive. Look for
**~10 Hz** (engine rocking on its mounts), **11 Hz** (rotational imbalance),
**5.5 Hz** (one cylinder differing), **33 Hz** (firing pulse through a bare
floor) — and for a **0.32 Hz amplitude modulation** of whichever one appears,
which would tie the felt shake to the measured oscillation for the first time.

**5. Hands on the engine — free.** Mounts and contact points, per the physical
test list. Nothing in three nights of OBD work has explained a shake strong
enough to move a person in the seat, and the ECU has now been exhausted twice
over.

**What NOT to do:** do not chase the barometric reading, do not replace an oxygen
sensor over the ethanol figure, and do not touch fuel or ignition parts. Trims
are at −0.78 % on both banks, both catalysts are at 44 % of their limit, all four
oxygen sensors respond in 0.014 s against a 0.4 s allowance, and every Mode 06
test passed. **There is nothing left to fix in the fuel or ignition system.**
