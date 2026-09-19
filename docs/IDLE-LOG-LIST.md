# WHAT TO LOG AT IDLE — corrected against the owner's own sensor list (2026-09-17)

**The owner corrected the first version: `Intake manifold absolute pressure` is
NOT in his sensor list.** He is right, and checking it exposed three further
errors. All are fixed below.

## FOUR CORRECTIONS THIS FORCED

**1. `Intake manifold absolute pressure` IS A 2023-ONLY CHANNEL.** A raw header
scan of every file in the repository finds it in **exactly three files, all three
the 2023 control**. `CLAUDE.md` and `docs/SENSOR-INVENTORY.md` both credit this
truck with *"99 kPa in all 16 samples it ever produced, engine off"* and call it
**"untested, not dead."** **That is the same 2023-attribution error this project
already recorded once for the secondary oxygen sensor trims.** Withdrawn.

**What this truck actually has is `Manifold absolute pressure (high resolution)`,
and it reads BLANK with a 0 ms refresh time** — offered by the app, not answered
by the truck. **So manifold pressure is genuinely unavailable here. A mechanical
vacuum gauge on a manifold port is the only route, and the "one minute settles
it" capture I put at the top of the previous list does not exist.**

**2, 3 and 4 — "never logged" was wrong three times.** These have all been
recorded, in small amounts:

| Channel | Samples | Sessions | Reads |
|---|---|---|---|
| `[PCM] Currently Detected Engine Misfire` | **53** | 3 | **exactly 0.0000 in every one** |
| `[PCM] Knock Sensor 1` | 48 | 3 | 156–394 |
| `[PCM] Knock Sensor 2` | 48 | 3 | 170–483 |
| `[PCM] Cylinder 1–6 Acceleration Value` | 8–42 each | 1 | ±0.078, except cylinder 6 |

**The misfire capture is still needed, but for a different reason than I gave.**
Not "never logged" — **never logged for long enough to overlap an event.** At one
measured rate of 0.44–1.66 events per minute, 53 scattered samples almost
certainly never coincided with one.

---

Every entry below is a **separate recording**. Conditions for all of them:

**Warm · Park · standstill · air conditioning OFF · phone left alone, screen
awake, no page switching · export CSV #2 (Horizontal) · note the phone clock and
the odometer.**

## The rule that shapes the list

The tiles law: two channels give 32.9 Hz, three drop to 15.5 Hz. **That cliff
only matters when engine speed ITSELF is being analysed** — orders, rate of
change, event shape. **Fuel trims step in 0.78 % and move over seconds, so
15.5 Hz is far more than they need.**

**Two tiles when the question is about engine speed. Three when engine speed is
only there to prove the condition.**

---

## 1 — THIRTY MINUTES. The hiccup capture, now the top of the list

> **CHECK SERVICE 06 BEFORE SPENDING THE THIRTY MINUTES (added 2026-09-19).**
> This capture is long because the live misfire channel has to be **sampled at
> the moment of an event**. The on-board monitor holds **cumulative per-cylinder
> misfire counters** instead, with the module's own pass/fail limits, and a
> counter does not have to be caught in the act. One command reads all six:
>
> ```
> python data/f150_agent.py monitors --only misfire
> ```
>
> **Whether this PCM answers those identifiers is untested** — if it does, it
> may replace this capture outright, and if it does not, nothing is lost but a
> minute. See [`SCANNER-PARITY.md`](SCANNER-PARITY.md).

```
Engine RPM
[PCM] Currently Detected Engine Misfire
```

The idle events are **0.24 s wide — about one engine cycle**, which is combustion
timescale. This channel asks directly whether a cylinder is missing or partly
missing at those moments.

**Thirty minutes because events arrive at 0.44–1.66 per minute.** That gives
**13 to 50** depending on which session's rate this one resembles. The 53 samples already on record all read 0, but they are scattered and
almost certainly never landed on an event — which is exactly the gap this fills.

## 2 — THREE MINUTES. Settle the oxygen sensor swap

```
Short term fuel % trim - Bank 1
Short term fuel % trim - Bank 2
Engine RPM
```

Three tiles deliberately. **The last attempt recorded no engine state, and that
is what cost the reading its meaning.**

Reproduces the method behind the pre-swap **+1.95 %**. Current reading is
**+0.62 % on Bank 1** — opposite side, under a third the size.

**Do not touch the throttle.** The bank difference reverses sign under throttle
movement (−0.91 % during blips); one blip contaminates the recording.

## 3 — FIVE MINUTES, then TWO MORE. The post-tune baseline

```
Engine RPM
```

Alone, flat 33.3 Hz. Then **two minutes held at about 1200 rpm.**

Feeds `data/rpm_rate.py`, `data/order_track_rpm.py` and `data/idle_events.py`.
**Every existing number from all three is pre-tune.** At 1200 rpm the sampling
ratio changes, so a false order line moves and a real one does not — the one test
the existing data cannot do.

## 4 — SIX CAPTURES, ONE MINUTE EACH. Per-cylinder contribution

```
Engine RPM
[PCM] Cylinder 1 Acceleration Value        (then 2, 3, 4, 5, 6)
```

One at a time — **all six on a page drops the rate to 2 Hz.**

Existing coverage is 8–42 samples each from a single session, and the cylinder 6
spread in it is a known artefact of being the only one still polled after a
throttle lift. **Repeat all six after a stop and restart** — a real weak cylinder
repeats, an artefact does not.

## 5 — TWO MINUTES. The knock sensors, and there is a reason now

```
[PCM] Knock Sensor 1
[PCM] Knock Sensor 2
```

**Sensor 2 reads consistently higher than sensor 1** across all three sessions
that carry them — 170–483 against 156–394. **Raw units, no documented scaling,
48 samples each, mixed conditions including driving.** Not a finding, but the two
should be comparable at a steady idle and nobody has ever put them side by side
under a known condition.

## 6 — ONE MINUTE. Confirm the manifold channel really is blank

```
Engine RPM
Manifold absolute pressure (high resolution)
```

**The claim that this reads blank rests on a single screenshot.** One minute of
logging either confirms it (the column stays empty, the channel is genuinely
unsupported and the vacuum gauge is the only route) or it produces numbers and a
significant measurement returns.

## 7 — ONE MINUTE, no scanner at all

**A meter across the battery posts at idle.** `Control module voltage` reads
**12.49–12.77 V with the engine running** against 13.0–14.8 expected — the only
absolute criterion this engine fails, and the smart-charging explanation for it
rests on a channel that was never sampled alongside it.

**13.5–14.5 V with occasional drops = the strategy working. A steady 12.6 V
running = not.**

---

## If there is only time for two

**Numbers 1 and 2.** The first is aimed squarely at the symptom as the owner now
describes it. The second closes an experiment already half-done.

## Dropped from the previous list

**`Barometric pressure` + `Intake manifold absolute pressure` with the engine
off**, which was going to cross-check the 97 kPa barometric reading. **It cannot
be done — the second channel does not exist on this truck.** Barometric has no
partner here to be checked against.
