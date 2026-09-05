# Field sheet — after the purge valve replacement

Complete capture protocol. Channel names are exactly as the app lists them; if a
name here does not match what you see, tell me and I will correct it.

**Method, every graph capture:**

- Keep the screen at its normal width — **~15 seconds, 5-second gridlines.**
- **5–6 screenshots per capture**, consecutive.
- **Phone clock visible.** Never compare readings from different sessions.
- **Ignore the Min / Avg / Max line.** It is cumulative over the whole session,
  not the window on screen. I read the plotted curve.
- **Note the y-axis top and bottom** if it looks unusual — the app auto-scales
  and a flat signal on a zoomed axis looks violent.
- The red **milliseconds** figure is response time. `0ms` with no value means the
  truck did not answer.

**The state of play:** the purge valve was one source of unmetered air and
replacing it cleared D and R. P and N still shake — the condition with the
highest manifold vacuum. So at least one more vacuum-dependent source remains,
and the truck now gives us a good condition and a bad condition minutes apart.

---

## SESSION A — standstill, BEFORE you drive anywhere

**Do this first and do not drive beforehand.** Long term trim still holds the
values it learned around the old valve (+3.13 % bank 1, +2.34 % bank 2). Short
term trim is now correcting *against* that stale memory. **That mismatch is the
fingerprint of a successful repair, and it vanishes the moment the computer
relearns.**

Warm the engine at idle until `Engine coolant temperature` is above 90 °C.

### A1 — Park · bank 1 trims
`Short term fuel % trim - Bank 1` + `Long term fuel % trim - Bank 1`

Expect long term still near +3.13. **If short term now sits around −2 to −3, the
total correction has dropped and the new valve removed real air.**

### A2 — Park · bank 2 trims
`Short term fuel % trim - Bank 2` + `Long term fuel % trim - Bank 2`

Same reading, other bank. Long term should still be near +2.34.

### A3 — Park · the hunt
`Engine RPM` + `Timing advance`

The needle used to breathe ~40 rpm every 3–4 s while spark swung 10–13.5°.
**Is that still happening in Park?**

### A4 — Park · is the mixture still swinging
`Engine RPM` + `Oxygen sensor 1 Wide Range Equivalence ratio`

Previously a clean sine, 14.41–15.05, same 3.4 s period as everything else.

### A5 — Park · command versus spark
`Fuel/Air commanded equivalence ratio` + `Timing advance`

Never captured. Tells me whether spark is *reacting* to the commanded mixture
swing or moving on its own.

### A6 — Park · throttle
`Engine RPM` + `Throttle Position Actually`

The plate never moved before. Confirm that is still true.

### A7 — Park · value read
Write these down together with the phone clock:

`Commanded evaporative purge` · `Evap. system vapor pressure` ·
`Engine RPM` · `MAF air flow rate` · `Calculated engine load value` ·
`Timing advance` · `Knock retard` · `Engine coolant temperature` ·
`Intake air temperature` · `Ambient air temperature` · `Barometric pressure` ·
`Variable camshaft actual advance #1` · `Fuel System Status` ·
`Run time since engine start` · all four trim channels ·
`Oxygen sensor 2 Bank 1 Voltage` · `Oxygen sensor 2 Bank 2 Voltage`

**`Commanded evaporative purge` is the one that matters most here.** The old
valve ran a flat ~40 % at idle. What the PCM commands the *new* valve to do says
a lot about what the old one was actually doing.

---

## SESSION B — the same thing in DRIVE ⭐

**Foot firmly on the brake, standstill, engine warm.** This is the strongest
comparison available in this whole investigation: your truck shakes in P and
does not in D, minutes apart, same engine, same temperature.

### B1 — Drive · bank 1 trims
`Short term fuel % trim - Bank 1` + `Long term fuel % trim - Bank 1`

### B2 — Drive · bank 2 trims
`Short term fuel % trim - Bank 2` + `Long term fuel % trim - Bank 2`

**Watch for a load-cell switch**, the way the 2000 rpm test showed one. If long
term jumps to a different value in D, that value is the correction the engine
needs in the condition where it *doesn't* shake — and the gap between the two is
the size of what is left.

### B3 — Drive · the hunt
`Engine RPM` + `Timing advance`

**If the needle stops breathing in D and starts again in P, the hunt and the
shake are the same fault.** That single observation would tie the whole thing
together.

### B4 — Drive · mixture
`Engine RPM` + `Oxygen sensor 1 Wide Range Equivalence ratio`

### B5 — Drive · value read
Same list as A7.

### B6 — Neutral, one value read
`Short term fuel % trim - Bank 1` · `Long term fuel % trim - Bank 1` ·
`Engine RPM` · `Commanded evaporative purge` · `Calculated engine load value`

You report N behaves like P. One reading confirms N sits with P and not with D.

---

## SESSION C — 2000 rpm in Park

Warm, in Park, hold ~2000 rpm as steadily as you can for **2 minutes**, then let
it fall back to idle and catch one more window.

### C1 — the load cells
`Long term fuel % trim - Bank 1` + `Long term fuel % trim - Bank 2`

Last time: idle +3.13 / +2.34, just off idle +0.78, 2000 rpm 0 — a slope.
**A flatter slope now means the purge valve was part of it. An unchanged slope
means what remains is the same size as what we started with.**

### C2 — why the rpm would not sit still
`Engine RPM` + `Throttle Position Actually`

You said something was moving the revs while you held the throttle. This shows
whether the PCM is moving the plate on its own, or whether it is the cooling fan
loading the engine.

### C3 — one bank's total at load
`Short term fuel % trim - Bank 1` + `Long term fuel % trim - Bank 1`

Both halves of one bank at 2000 rpm gives a true total, which the earlier
capture could not (it paired bank 1 short term with bank 2 long term).

---

## SESSION D — the drive

**20–30 minutes**, mixed, including at least **10 minutes of steady 60–80 km/h.**

This does three jobs: it relearns the adaptives around the new valve, it reads
the cruise trim cell, and it finally makes the truck run its own catalyst and
oxygen sensor tests, which have read "Not completed" throughout.

Capture while **holding a steady speed**, not while accelerating.

### D1 — cruise trim cells
`Long term fuel % trim - Bank 1` + `Long term fuel % trim - Bank 2`

**Near 0 while idle stays positive** = what remains is still idle-only, so still
a leak. **Both climbing toward +3 %** = the correction is proportional, and the
answer is the MAF or the barometric reading, not a hole.

### D2 — one bank's total at cruise
`Short term fuel % trim - Bank 1` + `Long term fuel % trim - Bank 1`

### D3 — catalyst, bank 1
`Oxygen sensor 1 Wide Range Equivalence ratio` + `Oxygen sensor 2 Bank 1 Voltage`

Before the converter and after it, on one screen, at the only operating point
where a converter can honestly be judged. Shows how much the converter smooths
the mixture swing and how long it delays it.

### D4 — catalyst, bank 2
`Oxygen sensor 5 Wide Range Equivalence ratio` + `Oxygen sensor 2 Bank 2 Voltage`

### D5 — cruise value read
`Vehicle speed` · `Engine RPM` · `MAF air flow rate` ·
`Calculated engine load value` · `Timing advance` · `Knock retard` ·
`Commanded evaporative purge` · `Catalyst temperature Bank 1 Sensor 1` ·
`Catalyst temperature Bank 2 Sensor 1` · all four trims

---

## SESSION E — standstill again, straight after the drive

Engine hot, adaptives now relearned around the new hardware.

### E1 — repeat A1, A2, A3 in Park
### E2 — repeat B1, B2, B3 in Drive

**Now the numbers describe the truck as it is today.** The A-versus-E comparison
shows how far the adaptives moved once they were free to relearn.

### E3 — the monitors
`Monitor status since DTCs cleared.` — read the whole block.

Have **Catalyst**, **Oxygen Sensor** and **Fuel System** changed from "Not
completed" to "Completed"? If so, the next item finally has data in it.

### E4 — on-board monitoring test results (Mode 06)
The app's own menu, not a live-data channel. **Per-cylinder misfire counts, the
catalyst monitor's actual test values against their limits, oxygen sensor
response times.** This has been empty all along because the tests had not run.

### E5 — permanent codes (Mode 0A)
The only code history a clear cannot erase. Never read on this truck.

### E6 — freeze frame
If anything is stored.

---

## SESSION F — cold start, next morning

**The single most valuable free observation still outstanding, and it takes one
minute.**

A cold engine runs **open loop** — the PCM ignores the oxygen sensors entirely
and fuels from a table.

Start it cold, in Park, and **watch the tachometer needle before it warms up.**

| What you see | What it means |
|---|---|
| Needle **steady cold**, starts breathing once warm | The breathing lives in the fuel feedback loop |
| Needle **breathing cold and warm alike** | Not the fuel loop. Air path or mechanical. |

You have reported the *felt shake* is identical cold and hot. **Nobody has ever
asked whether the needle breathing is.** They are different observations.

If you can, also capture `Engine RPM` + `Short term fuel % trim - Bank 1` during
the first two minutes from cold.

---

## SESSION G — physical tests, engine off

Same method every time, and it respects the hard-plastic lines: **engine OFF →
disconnect → plug the manifold port so it seals → restart → let it settle 2–3
minutes → read `Short term fuel % trim - Bank 1` and `- Bank 2` at warm idle.**

Short term is the live indicator; long term will lag. **Short term diving
negative names that circuit as the source.**

### G1 — PCV valve, hose, grommet, elbow
Never inspected. Twelve years of Jeddah heat; the plastic elbows go hard and
crack. **Also do the shake test:** pull the valve and shake it — **no rattle
means clogged.**

### G2 — Brake booster line and check valve
Never tested. Also: with the engine off, pump the brake pedal to exhaust the
reserve, hold it down, start the engine — the pedal should sink slightly. Then a
hand vacuum pump on the check valve, which **must hold**.

### G3 — Smoke test
For the joints nothing can be unplugged to isolate: **intake manifold gasket,
throttle body gasket, injector O-rings.** The throttle body and the injectors
were both opened during earlier work — they cannot be what *started* this, since
the shake predates all repairs, but an opened joint can leak now regardless.

### G4 — Cylinder balance, by injector
Unplug one injector at a time and note the rpm drop for each. **Six numbers.**
Equal drops mean all six cylinders pull their weight. One small drop names the
cylinder — and an unevenly distributed leak feeding one runner is exactly what
would produce a felt vibration with no code.

### G5 — Vacuum gauge on the manifold
Not for finding leaks — the trims do that better. For **combustion character** at
a bandwidth no scan tool can reach: a steady needle, a drifting needle and a
rhythmically twitching needle mean three different things.

### G6 — Multimeter, three readings
- **DC volts across the battery posts at warm idle** — 13.5–14.5 V, dropping at
  times as the smart charging backs off. Confirms the charging story.
- **AC volts across the battery at idle** — must be under **0.1 V**. Above that,
  an alternator diode is injecting ripple into every sensor reference.
- **DC millivolts, ground drops**, idling with loads on: battery negative → block,
  block → chassis, battery negative → chassis. **Each under 0.1 V.**

### G7 — Wiggle test
Idling with the rpm graph on screen, flex and tap the **crank sensor connector
and its harness first**, then the cam sensors, MAF and coils. Any rpm response is
the fault.

---

## SESSION H — measure the vibration itself

Everything above measures proxies. This measures **the actual complaint.**

Phone flat on the seat, spectrum or accelerometer app, warm idle at ~660 rpm.
**Do it in Park (shakes) and in Drive (clean) and compare.**

| Frequency | Meaning |
|---|---|
| **~33 Hz** (3rd order) | The V6's normal firing pulse through a bare regular-cab floor. **Normal. Nothing to fix.** |
| **~11 Hz** (1st order) | Rotational imbalance — damper, pulley, flexplate |
| **~5.5 Hz** (half order) | **One cylinder contributing differently from the other five.** A single weak cylinder repeats once per full engine cycle, which is half crank speed. G4 names which one. |

Also worth doing: **an independent rpm reading** — a timing light with a tach
function against the app's number. Every rpm figure in this investigation is the
PCM's own measurement from the crank sensor. If that signal is noisy, the PCM
would modulate spark to chase a phantom, and that modulation would make the
engine genuinely oscillate.

---

## SESSION I — the control sample

**Still the only way to know whether any of this is abnormal.**

Find another 2011–2014 F-150 or Mustang with the 3.7. Hand on the fender at warm
idle, then sit in the cab. Two minutes answers what months of measurement
cannot: whether a small idle vibration is simply what this engine does in a bare
regular cab.

If the owner will let you plug in: `Long term fuel % trim - Bank 1` and
`- Bank 2` at warm idle, and `Engine RPM` + `Timing advance`. Those three numbers
from a healthy 3.7 would settle several open questions at once.
