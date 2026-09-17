# WHAT TO LOG AT IDLE — the list, in order (2026-09-17)

Owner asked directly. Every entry below is a **separate recording**. Conditions
are the same for all of them unless stated:

**Warm · Park · standstill · air conditioning OFF · phone left alone, screen
awake, do not switch pages · export CSV #2 (Horizontal) · note the phone clock
and the odometer.**

## A rule that changes the plan — 33 Hz is only needed for engine SPEED

The tiles law says two channels give 32.9 Hz and three drop to 15.5 Hz. **That
cliff only matters when engine speed itself is being analysed** — orders, the
rate of change, event shape. **Fuel trims quantise at 0.78 % and move over
seconds; 15.5 Hz is far more than they need.**

**So the trim capture can afford a third tile for `Engine RPM`** — and it should,
because the last trim capture had no engine state recorded and that cost the
whole reading its meaning. **Two tiles when the question is about engine speed.
Three when engine speed is only there to prove the condition.**

---

## 1 — ONE MINUTE. Do this first; it is the cheapest and it can find a real fault

```
Engine RPM
Intake manifold absolute pressure
```

**This is the only outstanding capture that could reveal a genuine engine-run
problem.** Manifold vacuum is the variable the symptom tracks, and this truck has
never reported it once with the engine running.

**The channel is not dead here** — it answered 99 kPa in 16 samples with the
engine at 0 rpm, which is the correct atmospheric value.

| What it reads at warm idle | Meaning |
|---|---|
| **roughly 30–40 kPa** | Working. The load signal is available at last and a large gap in this investigation closes. |
| **still 99 kPa, or blank** | **The reporting path is wrong.** The computer's load calculation feeds fuelling and idle control, so this would be a real fault and would move to the top of the list. |

## 2 — THIRTY MINUTES. The hiccup capture

```
Engine RPM
[PCM] Currently Detected Engine Misfire
```

**Never logged.** The events measured at idle are **0.24 s wide, about one
engine cycle** — combustion timescale. This channel answers directly whether a
cylinder is missing or partly missing at those moments.

**Thirty minutes because the events arrive about every 84 s** — that gives ~20 of
them, enough to test against control moments. A five-minute capture gives three
and settles nothing.

## 3 — THREE MINUTES. Settle the oxygen sensor swap properly

```
Short term fuel % trim - Bank 1
Short term fuel % trim - Bank 2
Engine RPM
```

Three tiles deliberately — see the rule above. **The last attempt had no engine
state and the reading could not be trusted because of it.**

This reproduces the method behind the pre-swap **+1.95 %** and makes the two
numbers comparable. Current reading is **+0.62 % on Bank 1** — opposite side,
under a third the size.

**Do not touch the throttle during this capture.** The bank difference reverses
sign under throttle movement (−0.91 % during blips), so a single blip
contaminates the whole recording.

## 4 — FIVE MINUTES. The post-tune baseline

```
Engine RPM
```

Alone, at a flat 33.3 Hz. Feeds `data/rpm_rate.py` (rate of change), 
`data/order_track_rpm.py` (half and first order) and `data/idle_events.py`
(events). **Every existing number from those three tools is pre-tune** — this is
the first directly comparable post-tune reading.

**Then two minutes held at about 1200 rpm.** At 1200 the sampling ratio changes,
so a false order line moves and a real one does not. It is the one test the
existing data cannot do.

## 5 — SIX CAPTURES, ONE MINUTE EACH. Per-cylinder contribution

```
Engine RPM
[PCM] Cylinder 1 Acceleration Value        (then 2, 3, 4, 5, 6)
```

One cylinder at a time — **all six on one page would drop the rate to 2 Hz and
the readings would not be simultaneous with anything.**

Cylinder 4 read **−0.08** against −0.02 and −0.03 for its neighbours in the one
screenshot that exists, and Mode 06 logged its highest misfire count on the same
cylinder. **Two tools naming one cylinder, from a single snapshot each.**
**Repeat all six after a stop and restart** — a real weak cylinder repeats, an
artefact does not.

## 6 — TWO MINUTES. Knock sensors, never logged

```
[PCM] Knock Sensor 1
[PCM] Knock Sensor 2
```

Read 323 and 336 in one screenshot, raw with no units, and have never been
recorded. At idle with 95 octane they should be quiet and matched. **Worth two
minutes purely because nobody has ever looked.**

## 7 — ENGINE OFF, one minute. The sensor cross-check

```
Barometric pressure
Intake manifold absolute pressure
```

**With the engine stopped both channels read the same thing — atmospheric — so
they must agree.** Barometric has been reading **97 kPa** where Jeddah at sea
level should be near 101. If it sits 4 % below the manifold channel, that is a
quantified sensor offset in the same direction and roughly the same size as the
lean bias this project has chased for weeks.

## 8 — NO SCANNER. A meter across the battery posts at idle

`Control module voltage` reads **12.49–12.77 V with the engine running**, against
13.0–14.8 expected. It is the only absolute criterion the engine fails. The smart
charging explanation rests on a different channel that was never sampled
alongside it.

**13.5–14.5 V with occasional drops = the strategy working. A steady 12.6 V
running = not.** One minute, no scan tool.

---

## If there is only time for two

**Number 1 and number 2.** The first can find a real fault for one minute of
effort. The second is the only capture aimed squarely at the symptom as the owner
now describes it.
