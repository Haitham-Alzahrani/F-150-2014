# Driving tests — everything the truck can only tell you while moving

Companion to [`FIELD-SHEET.md`](FIELD-SHEET.md), which covers standstill.
Channel names are exactly as the scan app lists them.

**Method reminders:** ~15 s screen, 5 s gridlines · 5–6 screenshots per capture ·
phone clock visible · **read the plotted curve, never the Min/Avg/Max line** ·
note the y-axis range · `0ms` in red means the truck did not answer.

**Practical:** a second person holds the phone and screenshots. Several of these
need an empty road and full attention on driving. Mark the phone clock when you
start and end each test so the captures can be matched to what you were doing.

**Why driving matters here.** Every measurement so far has been at idle, where
the engine is unloaded, breathing ~3 g/s, and running closed loop at one
operating point. Load changes the fuelling, the spark, the exhaust temperature,
the cylinder pressure and the way the engine sits on its mounts. Several
mechanisms cannot show themselves at all until the engine is working.

---

## Before you set off

Note the phone clock and read: `Engine coolant temperature` ·
`Long term fuel % trim - Bank 1` and `- Bank 2` · `Commanded evaporative purge` ·
`Monitor status since DTCs cleared.`

The adaptives were wiped with the purge valve replacement, so the long term
values at the start of this drive are the baseline you are driving away from.

---

## TEST 1 — Steady cruise, 60–80 km/h

**Hold a genuinely steady speed for at least 5 minutes** before capturing.
Not accelerating, not coasting, light constant throttle.

### 1A — the cruise trim cells
`Long term fuel % trim - Bank 1` + `Long term fuel % trim - Bank 2`

**The single most important driving capture.** Before the repair, the load cells
read 0 % while idle read +3.13 / +2.34 — the signature of a leak that only
matters at idle. That whole table was erased by the memory wipe. This rebuilds
it.

| What you see after the drive | Meaning |
|---|---|
| Cruise near 0 and idle near 0 | **The leak is gone.** The purge valve was it. |
| Cruise near 0, idle back up to +3 | **Another leak remains.** PCV and booster next. |
| Both climbing to +3 together | Not a leak — a proportional error. MAF or barometric. |

### 1B — one bank's total at cruise
`Short term fuel % trim - Bank 1` + `Long term fuel % trim - Bank 1`
Then the same pair for bank 2.

Both halves of one bank gives the true total correction at cruise.

### 1C — catalyst, bank 1 ⭐
`Oxygen sensor 1 Wide Range Equivalence ratio` + `Oxygen sensor 2 Bank 1 Voltage`

Before the converter and after it, on one time axis, **at the only operating
point where a converter can honestly be judged.** Idle is the worst place to
look — lowest flow, lowest temperature.

| Downstream trace | Meaning |
|---|---|
| **Slow, small, lazy** — barely follows upstream | Converter is storing oxygen. Working. |
| **Tracking upstream closely in size and timing** | Converter is not buffering. Suspect. |

### 1D — catalyst, bank 2
`Oxygen sensor 5 Wide Range Equivalence ratio` + `Oxygen sensor 2 Bank 2 Voltage`

Bank 1's downstream sensor swung deeper and leaner than bank 2's at idle. This
says whether that difference is real at a load where it means something.

### 1E — spark under load
`Engine RPM` + `Timing advance`

At cruise, timing should run **25–40°** [rule of thumb, VERIFY against the
manual]. At idle it sits 11–16°. If cruise timing is unusually low, the PCM is
pulling it for a reason — heat, knock, or a bad load calculation.

### 1F — cruise value read
`Vehicle speed` · `Engine RPM` · `MAF air flow rate` ·
`Calculated engine load value` · `Absolute load value` · `Timing advance` ·
`Knock retard` · `Commanded evaporative purge` ·
`Catalyst temperature Bank 1 Sensor 1` · `Catalyst temperature Bank 2 Sensor 1` ·
`Engine coolant temperature` · all four trims

---

## TEST 2 — Deceleration fuel cut (overrun)

**From 80 km/h, lift completely off the throttle and coast in gear down to about
30 km/h.** Do not touch the brake or the throttle.

The PCM shuts the injectors off entirely during this. Nothing is being burned.

### Capture
`Oxygen sensor 1 Wide Range Equivalence ratio` + `Engine RPM`

Then repeat with `Oxygen sensor 5 Wide Range Equivalence ratio`.

| What you see | Meaning |
|---|---|
| AFR pegs hard lean (a high number) within a second or two | **Injectors are shutting off cleanly.** Normal. |
| AFR stays near 14.7, or drifts lean slowly | **Something is still putting fuel in.** A leaking injector, or purge flowing fuel vapour. |

**This is a genuine leaking-injector test and it costs nothing.** A leaking
injector at idle would make one cylinder rich, produce an uneven power stroke,
and set no code — exactly the profile being chased.

Also watch `Short term fuel % trim - Bank 1` here: it crashes to about −11 % on
overrun, which is normal and simply marks the event.

---

## TEST 3 — Neutral coast — WITHDRAWN, IT DOES NOT WORK

**The owner attempted this and reported two problems that invalidate it. Both
are correct.**

1. **Idle speed is not the same.** Shifting to Neutral above a road-speed
   threshold makes the PCM raise idle well above its stationary value. The whole
   premise of the test was that the engine would be in the *identical* state as
   at a standstill in Park. It is not.
2. **Road and tyre vibration swamps the measurement.** At 60 km/h the cab is
   already full of vibration from the road surface. A small idle shake cannot be
   judged against that background.

**Replaced by the rpm sweep in Park** (see below), plus the electrical load test
and the mount touch test in [`FIELD-SHEET.md`](FIELD-SHEET.md) Session G. The
original description is kept below only as a record of the reasoning.

### TEST 3B — THE RPM SWEEP IN PARK, the replacement ⭐

Warm, stationary, in Park. Hold each of these steady for 20-30 seconds and rate
the strength of the shake felt in the seat:

**650 (idle) → 800 → 900 → 1000 → 1200 → 1500 → 1800**

**Why it discriminates.** The engine produces vibration at several orders
simultaneously, and each scales with rpm at a different rate:

| Order | At 650 rpm | At 1200 rpm |
|---|---|---|
| Half order — one cylinder differing | 5.4 Hz | 10 Hz |
| First order — rotational imbalance | **10.8 Hz** | 20 Hz |
| Firing pulse, 3rd order | 32.5 Hz | 60 Hz |

**The engine rocking on its mounts resonates at roughly 8-15 Hz.** Which order is
exciting that resonance therefore depends entirely on engine speed, and sweeping
the rpm sweeps each order through the resonance band in turn.

| Behaviour as rpm rises | Interpretation |
|---|---|
| **Worst at idle, clearly fading by 900-1000** | First order driving the mount rock mode — **a mount, or rotational imbalance** (damper, pulley, flexplate) |
| **Worsens around 1000-1800, then fades** | **Half order** — one cylinder contributing differently, sweeping into the resonance |
| **Steadily reduces, no peak** | Normal. Idle is the roughest point any engine runs at. |
| **Grows continuously with rpm** | Rotational imbalance driven directly rather than through a resonance |

Free, stationary, no instruments, and the four behaviours are distinguishable by
feel.

### TEST 3C — Electrical load at idle in Park

Headlights, blower on maximum, rear demister, every load available, at warm idle
in Park. The alternator then puts real drag on the engine — a mild version of
what the converter does in Drive.

| Result | Interpretation |
|---|---|
| **Shake reduces** | Load damping is the mechanism, which fits the D/R observation and points at ordinary torque ripple rather than a broken component |
| **No change** | Load is not the mechanism, and the D/R difference comes from somewhere else — engine position on the mounts, or a contact point that breaks when the engine rotates |

### The original test, for the record



**At about 60 km/h on a clear straight road, shift into Neutral and coast.**
The engine drops to idle, unloaded, exactly as it is in Park — but the truck is
moving.

**Now feel the seat.**

| What you feel | What it means |
|---|---|
| **The shake is there, same as in Park** | It is the engine, and it does not care whether the truck is moving. Mounts, cylinder balance, or the engine itself. |
| **The shake is gone** | The engine is in the identical state and you cannot feel it. So the transmission path changed — **something about being stationary is letting the vibration into the cab.** Exhaust or a line touching, suspension unloaded, mount sitting differently. |

**This is the cleanest test on this list.** Same engine state, same idle speed,
same load — the only variable removed is standing still. Nothing else you can do
isolates the vibration path that precisely.

Do it several times. Also try it at 40 km/h and 80 km/h — if the shake in
Neutral changes with road speed, the road speed is involved and it is not the
engine at all.

### Capture while coasting in Neutral
`Engine RPM` + `Tim. adv.`

**Compare the rpm span directly against the Park numbers** (44–55 rpm, ~3.4 s
period) and the Drive numbers (13–18 rpm). If Neutral-while-moving looks like
Park, the hunt is about engine load. If it looks like Drive, something else
is going on.

---

## TEST 4 — Engine speed versus road speed

The standard way to identify any vibration: **hold one, change the other.**

### 4A — same road speed, different engine speed
Drive at a steady **60 km/h**, then use the gear selector to hold a lower gear
so the same road speed runs at a higher rpm. Repeat at two or three different
gears.

| Vibration follows | Cause lives in |
|---|---|
| **Engine rpm** | Engine, mounts, flexplate, damper, converter |
| **Road speed** | Wheels, tyres, driveshaft, axle |
| **Neither** | Something resonant — exhaust, heat shield, bracket, line |

### 4B — same engine speed, different road speed
Find two gear/speed combinations that give the same rpm at different road
speeds. Same table, read the other way.

### Capture
`Engine RPM` + `Vehicle speed` throughout, so each combination is recorded.

**Your complaint is at a standstill, so this may come back clean.** Run it
anyway — it takes ten minutes and it definitively separates the driveline from
the engine, which no test so far has done.

---

## TEST 5 — Torque converter lockup

At steady **70–90 km/h** in top gear the converter clutch locks, mechanically
tying the engine to the transmission. You will see rpm drop 150–300 with no
change in speed.

### Capture
`Engine RPM` + `Vehicle speed`

Then read `Gear (AT)` before and after the drop.

| What you feel | Meaning |
|---|---|
| Smooth before lockup, **vibration appears after** | The converter clutch damper is passing engine pulses through. |
| No change | Converter clutch is fine. |

Relevant because a locked converter removes the damping that makes your truck
smooth in D at a standstill.

---

## TEST 6 — Wide open throttle ⭐ the engine breathing test

**Needs a clear, empty stretch.** From about 40 km/h, floor it and hold to about
100 km/h, then lift.

This is the only test that asks the engine to breathe as hard as it can.

### Capture
`Absolute load value` + `Engine RPM`

Then repeat with `MAF air flow rate` + `Engine RPM`, and once more with
`Fuel/Air commanded equivalence ratio` + `Engine RPM`.

### What the numbers should do

| Channel | Healthy at WOT | If it falls short |
|---|---|---|
| `Absolute load value` | **approaching 90–100 %** | **Below ~80 % means the engine is not breathing.** Blocked catalyst, exhaust restriction, cam timing, worn engine. |
| `MAF air flow rate` | peak in the region of **170–210 g/s** for a 302 hp engine [rule of thumb, VERIFY] | Well below that, same conclusion |
| `Fuel/Air commanded equivalence ratio` | goes **rich, roughly 12.5–13.0 AFR** | Staying at 14.7 under full load is wrong |
| `Knock retard` | 0–3° | More than that means the PCM is fighting knock |
| `Timing advance` | pulls back from cruise values | Normal under load |

**A partially blocked catalyst is the classic finding here**, and it is worth
checking on this truck because bank 1's downstream sensor behaved differently
from bank 2's. A blocked converter chokes the engine at high flow and is
invisible at idle.

---

## TEST 7 — Knock under load

`Engine RPM` + `Knock retard`, captured during a **hard pull in a high gear from
low rpm** — third or fourth gear from about 1500 rpm, steady heavy throttle.

Knock retard reads 0 at idle on this truck. It only appears when cylinder
pressure is high. Anything beyond a few degrees means carbon, heat, fuel quality
or a genuine knock sensor problem.

---

## TEST 8 — Electrical load

Driving at a steady speed, switch on **headlights, blower on maximum, rear
demister, and anything else** at once.

### Capture
`Control module voltage` + `Engine RPM`

Then read `[BCM] Vehicle Battery Voltage` and `[BCM] Vehicle Battery Current`.

| What you see | Meaning |
|---|---|
| Voltage holds 13.5–14.5 | Charging system copes |
| **Voltage sags below ~13** under load | Alternator output is marginal |
| **rpm dips as loads switch on** | The idle/load compensation is working hard |

The 12.6 V reading earlier was explained as Ford's smart charging backing off on
a full battery. Loading the system forces it to charge and shows whether it can.

---

## TEST 9 — A/C, on and off, while driving

Steady speed, A/C off for a window, then on for a window.

### Capture
`Engine RPM` + `Timing advance`, then `Engine RPM` + `Calculated engine load
value`

A/C roughly doubled the idle rpm oscillation amplitude at a standstill. This
says whether it does the same under load.

---

## AFTER THE DRIVE — read these before the engine cools

### The monitors
`Monitor status since DTCs cleared.` — read the whole block.

The drive should flip **Catalyst**, **Oxygen Sensor**, **Fuel System** and
**Evaporative System** from "Not completed" to "Completed". Until they do, the
next item is empty.

### On-board monitoring test results (Mode 06) ⭐
A separate menu, not a live-data channel. Look for **"On-board monitoring
tests"**, "Test results" or "Mode 06".

**This is where per-cylinder misfire counts live** — one row per cylinder, each
with a value and its limit. The standard misfire monitor only flags above roughly
2 % misfire; **a cylinder producing 10 % less torque while never actually
misfiring passes it cleanly.** Mode 06 gives the raw counts instead of the
pass/fail, and it is the only place in the ECU that can show one cylinder
differing from the other five.

After the drive it will also hold **catalyst monitor results for both banks** —
the actual test value against its limit, which settles the bank 1 versus bank 2
question far better than any idle reading.

### Permanent DTCs (Mode 0A)
The one code history a memory wipe cannot erase. Never read on this truck.

### Freeze frame
If anything is stored.

### Repeat the standstill captures
Park and Drive, `Short term` + `Long term` for each bank, and
`Engine RPM` + `Tim. adv.` — now with relearned adaptives. **And check whether
the shake has come back in D and R.** If it has, the improvement came from the
memory wipe rather than the new valve.

---

## What driving still cannot tell you

A mount that has stopped isolating, or a pipe touching the body, produces **no
ECU signature at all**. Test 3 (neutral coast) is the closest any driving test
gets to them, because it changes the vibration path while leaving the engine
untouched. Everything else about those two lives in
[`FIELD-SHEET.md`](FIELD-SHEET.md) Session G.
