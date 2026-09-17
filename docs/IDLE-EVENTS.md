# THE HICCUPS — discrete idle events, measured (2026-09-17)

**Tool: [`data/idle_events.py`](../data/idle_events.py).** Owner asked whether the
saved data can name what makes the engine hiccup. **It can measure the events. It
cannot name their cause, and the reason is specific and fixable.**

## Why this needed a different detector

**A hiccup and an oscillation are different signals.** Everything this project has
measured — peak-to-peak span, standard deviation, the 0.33 Hz line, jitter,
orders — describes a *continuous* wobble. The owner describes **discrete
events**. A detector for one does not find the other.

Method: resample to a common grid, remove everything below ~0.5 Hz (that is the
breathing), keep 0.5–5 Hz, and count excursions past a **fixed 25 rpm** threshold.
Fixed, not per-session sigma — a sigma threshold makes every session flag its own
noise and destroys comparability. Idle must hold across the whole ±1.5 s
neighbourhood, so a throttle blip cannot contribute.

## The events are real

**3.2 hours of Park idle, 09-04: 136 events, one every 84 s, median 31 rpm.**
Matches the "57 outliers, median spacing 82.3 s" already in `CLAUDE.md`, which
nobody followed up.

### They are SHORT — about one engine cycle

Ensemble-averaged over 113 sign-aligned events: **width at half height 0.24 s.**
At 650 rpm one full engine cycle is 0.185 s.

**The shape was checked against the filter, not assumed.** The averaged event has
dips either side of the spike, which looks like a precursor. **It is not** — the
same filter fed a pure one-sample impulse produces the same flanking dips. What
survives the check is the *width*: a 1 s disturbance produces a visibly different
shape that the data does not show.

**That short duration rules out every slow mechanism by arithmetic:**

| Candidate | Its timescale | Verdict |
|---|---|---|
| Air conditioning compressor | 15.78 s cycle | **65× too slow** |
| Commanded evaporative purge | moves over 10–30 s | **too slow** |
| Catalyst dither / the 0.33 Hz breathing | 3 s | **12× too slow** |
| Cooling fan, coolant temperature | tens of seconds to minutes | **far too slow** |
| **A single combustion event** | **0.185 s** | **matches** |

**Whatever makes a hiccup operates on the timescale of one or two combustion
events.** That is the first real narrowing this symptom has had.

## BUT THE HEALTHY TRUCK HAS THEM TOO

| Truck | Session | Idle min | Events/min | Median size |
|---|---|---|---|---|
| 2014 | 09-05 04:17 | 42.9 | **0.909** | 29.0 rpm |
| 2014 | 09-04 (3.2 h) | 191.3 | **0.711** | 31.3 |
| 2014 | 09-05 03:09 | 10.2 | **0.490** | 33.5 |
| 2014 | 09-13 cold start | 15.7 | **0.127** | — |
| **2023 CONTROL** | 09-06 17:38 | 19.0 | **0.368** | 29.0 |
| **2023 CONTROL** | 09-06 18:20 | 7.3 | **0.954** | 39.0 |

**The two control sessions were recorded on the same evening on the same healthy
truck and differ by 2.6× — 0.368 against 0.954.** That spread is **wider than any
gap between the two trucks.**

**So the event rate cannot distinguish a healthy engine from this one**, and the
event *size* is the same on both (29 rpm on the control, 29–33 on the 2014).
**By rate and by size, these events are not the fault.**

### One asymmetry survives, weakly

**2014 pooled: 105 dips against 77 rises — 58 % dips, binomial p = 0.045.** The
engine loses speed more often than it gains it, which is the direction a missed
or weak combustion event gives and the *opposite* of what a momentary load release
gives. **The control has 7 and 7 — far too few to compare.** Treat this as the one
thread worth pulling, not as a result.

## WHAT THE SAVED DATA CANNOT DO, AND EXACTLY WHY

**To name a cause, something else must be measured at the instant of an event.
That measurement does not exist in any log.**

The tiles law is why. **The only session with hours of settled idle — 09-04,
3.2 h, 136 events — had just `Engine RPM` and a voltage channel polled fast**; of
87 channels in that file, every other one had 13 samples or fewer. Every log that
*does* carry fuel trim, timing, airflow or oxygen sensors at speed has minutes of
idle at most.

Tested directly and it fails on sample coverage:

* Across all logs, only **one** stretch has any channel densely co-sampled with
  engine speed for over 30 minutes — 09-08 15:48, short term fuel trim and supply
  voltage. **It contains 4 minutes of settled idle and 2 events.**
* In that same stretch, a first pass without an idle restriction produced 23
  "events" at a 231.8 rpm threshold and a fuel trim difference at p < 0.001.
  **Those were throttle transients, not hiccups** — tip-in and overrun, which
  `CLAUDE.md` already documents at +9.38 % and −11.72 %. Restricting to idle left
  2 events and nothing testable. **An event detector run over a log containing
  driving will find the driving.**

## THE CAPTURE THAT WOULD ANSWER IT

**Two tiles, both polled at ~33 Hz, at settled warm Park idle, for at least
thirty minutes.** At 0.7 events per minute that is ~20 events — enough to test.
The second tile is free; this project proved that and has never spent it on a
long idle session.

**First choice for the partner channel: `[PCM] Currently Detected Engine Misfire`.**
It is in the owner's sensor list, it read 0 in one screenshot, and **it has never
been logged.** If a hiccup is a missed or partial combustion event, this is the
channel that says so directly, and the 0.24 s width says that is the right
timescale to be asking about.

**Second: one `[PCM] Cylinder N Acceleration Value` at a time** — per-cylinder
contribution, already proven loggable on this truck. If events concentrate on one
cylinder, that names it.

**Third: `Timing advance`.** It is the governor's response rather than a cause,
but it establishes whether the engine was disturbed or the reading merely jumped —
a real torque event makes the governor answer; a bad crank signal does not.

Locally the tool does this directly, with no phone page to worry about:

```
f150diag --port /dev/ttyUSB0 --baud 115200 live --pids rpm misfire --seconds 1800 --label hiccups
python3 data/idle_events.py
```
