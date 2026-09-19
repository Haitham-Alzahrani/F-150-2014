# Context

The owner is a working mechanic in Jeddah, Saudi Arabia. He does the
hands-on work himself — give him diagnostic reasoning, specs and procedures,
not "see a mechanic."

## The truck

**2014 Ford F-150 XL Regular Cab · 3.7L V6 Ti-VCT · 6R80 auto · 4x4**
VIN `1FTMF1EM1EFC80632` · 131,000 km (Aug 2026) · Jeddah

**DRIVE TYPE — 4x4, owner-confirmed 2026-09-06.** Earlier revisions of this file
said 4x2 on a VIN decode and used that to dismiss the history report. **The owner
has the truck in front of him and says it is 4x4; that outranks a decode.** The
conflict is unresolved and matters for parts: `1FTMF1E` decodes as Regular Cab
4x2 in the position-4 series codes, where 4x4 Regular Cab is normally `1FTNF1E`.
Confirm before ordering any driveline part by checking for a transfer case, a
front driveshaft and a 4x4 selector.

**It also puts driveline parts back on the table that a 4x2 does not have** —
transfer case, front driveshaft, front differential, front CV axles. None of them
turn at a standstill in Park, so they cannot explain the Park idle shake, but the
transfer case is bolted to the transmission and adds mass and mounting to the
powertrain assembly.

**COOLING FANS ARE ELECTRIC, not a belt-driven clutch fan** (owner, 2026-09-06).
An electric fan loads the engine only through the alternator, which is a far
smaller and differently-shaped load than a mechanical fan clutch. Any reasoning
that treated a fan clutch as a direct crankshaft load is withdrawn.

## RUNNING LOCALLY WITH THE TRUCK ATTACHED — [`docs/START-HERE.md`](docs/START-HERE.md)

**First time on the owner's Windows machine: run `setup.cmd`.** It builds the
environment, installs, runs the self-test, and exercises the car link against a
**simulated** adapter before you go near the truck.

**THE CAR LINK IS [`data/f150_agent.py`](data/f150_agent.py), and it is the one
an agent can actually drive.** `data/f150_live.py` reads typed commands from
stdin, which a person can use and an agent cannot: **every shell command is a
separate process**, so the connection dies between questions and each reading
costs a fresh ELM327 handshake. So the link is split —

```
serve     ONE long-lived process owns the adapter, holds one handshake open,
          and logs Engine RPM continuously at full rate
clients   status | read <NAME> | snapshot | log start|stop | list | stop
          dtc | readiness | freeze | monitors | vehicle | healthcheck | did
          each a one-shot command returning one JSON object
```

**Measured: 32.4 Hz logging sustained through a status call, a read and an
11-channel snapshot on the same connection.** The CSV it writes is
`elapsed_s,rpm`, which `rpm_rate.py` and `idle_events.py` read directly — the
whole loop from capture to analysis is verified end to end.

**Read-only, guarded on the SERVICE MODE, not on a name.** Modes 1/2/3/6/7/9
allowed, **mode 4 refused**. `read CLEAR_DTC` returns REFUSED — verified, because
`getattr(obd.commands, 'CLEAR_DTC')` passes a `hasattr` check and sits in
`base_commands()`, so a name blocklist would not be enough.

**`serve --sim` runs it all with no hardware**, and every reply then carries
`"sim": true`. **Never report a simulated number as the truck.**

`.claude/settings.json` pre-approves these commands so a local session is not
prompted for each one, and denies anything naming CLEAR_DTC.

## IS IT AS GOOD AS THE SCAN APP? — [`docs/SCANNER-PARITY.md`](docs/SCANNER-PARITY.md)

**Until 2026-09-19 the link read LIVE SENSOR DATA AND NOTHING ELSE** — one of the
six things a scan app does. Fault codes, freeze frame, on-board monitor results,
vehicle information and readiness were **absent**, not weak. All five are in now
(`data/f150_obd2.py`), plus **permanent codes, service 0A, which `python-obd`
does not implement at all.**

**`healthcheck` runs all of it in one call.**

**SERVICE 06 CHANGES CAPTURE 1.** `MONITOR_MISFIRE_CYLINDER_1`–`_6` are
**cumulative counters with the module's own pass/fail limits**, not an
instantaneous channel. Capture 1 asks for thirty minutes because the live
misfire channel must be **sampled during an event**. A counter does not have to
be caught in the act. **Whether this PCM answers those identifiers is untested —
one command settles it.**

**A LIBRARY BUG WOULD HAVE REPORTED THE WRONG VIN.** `python-obd` 0.7.3 ends its
service 09 decoder with `bytes.strip`, which treats its argument as a **set of
bytes** — it strips the digits `0`, `1` and `2` off both ends. This VIN comes
back as `FTMF1EM1EFC8063`: leading `1` and trailing `2` eaten. **Every Ford VIN
starts with `1`.** Service 09 is decoded in this repository instead.
**`CALIBRATION_ID` is the custom tune's fingerprint and nothing here had ever
recorded it.**

## READING THE `[PCM]` CHANNELS — [`docs/MODE-22.md`](docs/MODE-22.md)

**The `[PCM]` family is Ford enhanced service 0x22, and `python-obd` has no
service 0x22 at all** — its table stops at modes 1, 2, 3, 4, 6, 7 and 9. So the
link could read engine speed and the trims but **not** the misfire counter, the
knock sensors or the cylinder acceleration values. `data/f150_did.py` builds
those requests by hand.

**Guarded on the SERVICE BYTE, by number — 0x22 only.** `0x2E` write, `0x31`
routine, `0x27` security, `0x34`/`0x36` reflash and `0x11` reset are all refused
explicitly, and `did_command()` asserts its own first byte before it returns.

**`data/did_registry.json` is EMPTY BY DESIGN and no identifier has been
verified on this VIN.** An unidentified read returns raw bytes with a refusal
attached. Two routes in, and no third: **correlation against a standard channel
at r-squared >= 0.99 over >= 200 samples**, or **a manipulation predicted in
writing first**.

**IDENTIFY WITH THE THROTTLE SWEPT, NOT AT IDLE.** See method rule 22 — at idle
the same correct address calibrated 11 % low.

## THE DASHBOARD — [`docs/DIAGNOSTIC-DASHBOARD.md`](docs/DIAGNOSTIC-DASHBOARD.md)

**Built 2026-09-18: every system classified CONFIRMED / HIGH-CONFIDENCE SUSPECT
/ POSSIBLE / NORMAL / UNKNOWN, from archived data only.** Read it for the state
of the whole truck rather than the state of one argument.

**Confirmed faults: none.** **One high-confidence suspect: the PCM supply
voltage.** **The largest unexamined system is the TRANSMISSION** — commanded
against measured gear ratio exists at n=591, but every sample is at a
standstill, where the measured ratio is a division by zero and the constant
0.829 "error" is a clamp, not slip. **It has never been measured while moving.**

## THE SYMPTOM, RESTATED BY THE OWNER — READ THIS BEFORE ANY DIAGNOSIS (2026-09-17)

**Owner's own words, and they re-scope this entire file:**

> *"When I ask you to diagnose my car don't think that I'm talking about the old
> shake which resolved by changing the mounts. My current ongoing problem is the
> engine feel like shaking and rpm unstable on very low non-noticeable events.
> Don't assume I'm complaining about something shaking hard. It's very small
> vibration associated with engine rpm change. It's still the same even after the
> custom tune."*

| | |
|---|---|
| **THE BIG SEAT SHAKE** | **CLOSED. The mounts fixed it. Do not re-open it, do not chase it, do not cite it.** |
| **THE CURRENT PROBLEM** | **A very small vibration that accompanies engine speed CHANGING** — low-level, easy to miss, not violent. Plus the speed being unsteady. |
| **The custom tune** | **Changed nothing about it.** |

**THIS FILE IS FULL OF LANGUAGE WRITTEN FOR THE OLD SYMPTOM.** Every phrase about
"the felt shake", "moves him in the seat", "shakes a person", and every test aimed
at a strong vibration is **about a complaint that is finished**. Read those
sections as history. **Do not hand him a test designed to find something violent.**

### WHAT THIS CHANGES LOGICALLY — the separation proof does NOT apply any more

This file states, twice and in capitals, that the felt shake and the 0.3 Hz rpm
oscillation are **separate phenomena, proven by two natural experiments** — the
mounts killed the shake and left the oscillation; the battery quietened the
oscillation and left the shake.

**Both experiments used the BIG shake as the variable.** The small
speed-linked vibration he is describing now **was never the thing being watched in
either one.** So:

**THE SEPARATION IS PROVEN FOR THE OLD SYMPTOM AND IS UNTESTED FOR THE NEW ONE.**
Do not carry it over. It is the single easiest mistake available here, because the
conclusion is written in this file in bold.

**And the new description points the other way.** A vibration that tracks engine
speed *changing* is what the 0.3 Hz oscillation would feel like — not as a 0.3 Hz
buzz, which is far too slow to feel as vibration, but as the engine's motion on
its mounts shifting every ~3 s. **The tune leaving it unchanged fits**: the tune
altered shift points and throttle response and touched neither idle fuelling nor
the catalyst dither that drives the oscillation.

### THE RIGHT METRIC IS THE DERIVATIVE — and it AGREES with amplitude (corrected 2026-09-17)

**Tool: [`data/rpm_rate.py`](data/rpm_rate.py). Log record:
[`docs/LOG-2026-09-17.md`](docs/LOG-2026-09-17.md).**

What pushes an engine against its mounts is **reaction torque, proportional to
angular ACCELERATION** — not how far the speed swings. Every other metric in this
file measures the swing.

**A RAW DERIVATIVE IS USELESS** — it is dominated by the sample interval: the
2023 control gave 60.3 rpm/s in one session and 90.0 in another **on the same
evening**, purely from 0.130 s against 0.049 s logging. **Fix the bandwidth
first.** At a fixed 0.3 s those two read **7.09 and 7.25** — agreeing within 2 %
across a 2.6× rate difference.

**A BUG IN THIS TOOL WAS CAUGHT ON 2026-09-17 AND IT CHANGED THE ANSWER.**
`np.interp` draws a straight line across any gap in the source, and a straight
line has almost no rate of change. The 09-17 log has a **47.5-minute hole** in
`Engine RPM`; **44 % of its grid fell inside it**, and the tool reported
**1.82 rpm/s** — which would have been a spectacular four-times-quieter-than-
healthy result. **Real coverage only: 12.50 rpm/s.** Both this tool and
`data/idle_events.py` now discard grid points spanning a gap over 1 s, and every
session was recomputed.

| | Before the fix | **After** |
|---|---|---|
| 2014 median | 8.37 rpm/s | **13.53 rpm/s** |
| 2023 control | 7.17 | **7.17** |
| **Ratio** | 1.17× | **1.89×** |

**THE PREVIOUS ENTRY HERE SAID "two metrics, same data, very different
verdicts" — 1.90× on peak-to-peak against 1.17× on rate of change. THAT
DISAGREEMENT WAS THE BUG.** Corrected, rate of change gives **1.89×** against
peak-to-peak's **1.90×**. **They agree almost exactly and are measuring the same
thing.** The question of which metric tracks what he feels dissolves.

## WHAT TO LOG AT IDLE — [`docs/IDLE-LOG-LIST.md`](docs/IDLE-LOG-LIST.md)

**OWNER CORRECTED THIS LIST 2026-09-17: `Intake manifold absolute pressure` is
NOT in his sensor list. He is right, and checking it exposed four errors.**

**1. `Intake manifold absolute pressure` IS A 2023-ONLY CHANNEL.** A raw header
scan of every file in this repository finds it in **exactly three files, all
three the 2023 control**. This file and `docs/SENSOR-INVENTORY.md` both credit
this truck with *"99 kPa in all 16 samples, engine off"* and call it **"untested,
not dead"** — **the same 2023-attribution error already recorded once for the
secondary oxygen sensor trims. WITHDRAWN.**

**What this truck has is `Manifold absolute pressure (high resolution)`, and it
reads BLANK at 0 ms refresh** — offered by the app, not answered by the truck.
**Manifold pressure is genuinely unavailable here. A mechanical vacuum gauge is
the only route.** The "one minute settles it" capture this file listed first does
not exist.

**2–4. "NEVER LOGGED" WAS WRONG THREE TIMES.** All three have been recorded:
`[PCM] Currently Detected Engine Misfire` **53 samples, 3 sessions, exactly
0.0000 in every one**; `[PCM] Knock Sensor 1`/`2` **48 samples each**;
`[PCM] Cylinder 1–6 Acceleration Value` **8–42 each**. **The misfire capture is
still needed — not because it was never logged, but because 53 scattered samples
almost certainly never landed on an event. **Rate measured: 0.44–1.66 per
minute across sessions** — the 09-04 log gives 136 events in 122 idle minutes,
one per 54 s.

**THE RULE THAT SHAPES THE LIST: the 33 Hz cliff only matters when ENGINE SPEED
ITSELF is analysed** — orders, rate of change, event shape. **Trims step in
0.78 % and move over seconds, so 15.5 Hz is ample.** Two tiles for engine-speed
questions; **three when engine speed is only there to prove the condition** —
which the trim capture needs, because the last one had no engine state and that
cost it its meaning.

| # | Time | Channels | What it settles |
|---|---|---|---|
| **1** | **30 min** | `Engine RPM` + `[PCM] Currently Detected Engine Misfire` | The hiccups. Events are 0.24 s — combustion timescale. At the measured 0.44–1.66 per minute, thirty minutes gives **13–50**. |
| **2** | **3 min** | `Short term fuel % trim - Bank 1` + `- Bank 2` + `Engine RPM` | The swap. **Do not touch the throttle** — the bank difference reverses sign under throttle movement. |
| **3** | **5 min + 2 min** | `Engine RPM` alone, then held ~1200 rpm | Post-tune baseline for all three rpm tools. At 1200 a false order moves, a real one does not. |
| **4** | **6 × 1 min** | `Engine RPM` + one `[PCM] Cylinder N Acceleration Value` | One at a time; all six drops to 2 Hz. **Repeat after a restart.** |
| **5** | **2 min** | `[PCM] Knock Sensor 1` + `[PCM] Knock Sensor 2` | **Sensor 2 reads higher than sensor 1 in all three sessions** (170–483 vs 156–394). Raw units, mixed conditions — not a finding, never compared at a known idle. |
| **6** | **1 min** | `Engine RPM` + `Manifold absolute pressure (high resolution)` | The blank claim rests on ONE screenshot. Confirm it, or a real measurement returns. |
| **7** | **1 min, no scanner** | Meter across the battery posts at idle | `Control module voltage` reads 12.49–12.77 V running. **13.5–14.5 with drops = normal. Steady 12.6 = not.** |

**IF THERE IS ONLY TIME FOR TWO: numbers 1 and 2.**

**DROPPED:** the engine-off `Barometric pressure` cross-check — **its partner
channel does not exist on this truck**, so the 97 kPa barometric reading has
nothing here to be checked against.

## CHECK THE CAPTURE BEFORE YOU LEAVE THE TRUCK — [`data/check_capture.py`](data/check_capture.py)

**Every wasted capture in this project failed the same way: the file did not
contain what the question needed, and nobody noticed for days.**

```
python data/check_capture.py <file.csv>
```

It does not analyse anything. It asks, of one file: **which of the open
questions can this answer, and if not, exactly why not** — channel by channel,
with sample counts, the best sustained rate over any 60 s, minutes at
guard-band-confirmed idle, gaps in `Engine RPM`, and how many samples each pair
actually shares.

**Run it while the engine is still warm and the capture can be repeated.**

On the 74-tile session it returns `THIS CAPTURE ANSWERS NOTHING ON THE LIST`,
and names every reason: the misfire channel at 0.0 Hz, the trims with **0.0 min
at confirmed idle**, **zero** shared samples between engine speed and the
cylinder channels, and the **47.5-minute hole**. Each of those took a long time
to find by hand. It finds them in one command.

It judges by the **best sustained 60 s rate, not the file median** — the 09-04
log medians 16.7 Hz but contains a **33.2 Hz stretch at 2105 s**, and the whole
engine-order analysis came out of that stretch. Judging by the median would
throw away the part that answers the question.


## HOW TO CAPTURE — the sample rate is set by TILES ON SCREEN, not by the sensor list

**Measured across 265 one-minute windows in 10 logs (2026-09-14).** This
overturns the standing "Car Scanner samples each channel at ~17 Hz" claim: there
is no fixed rate. **Car Scanner polls only the channels visible on the page the
owner is looking at**, so the rate is set by how many tiles are on screen.

| Channels polled at >= 1 Hz | Windows | Median `Engine RPM` rate | p10-p90 |
|---|---|---|---|
| **1** | 1 | **33.3 Hz** | flat 30.0 ms |
| **2** | 6 | **32.9 Hz** | 15.7-33.2 |
| 3 | 100 | 15.5 Hz | 13.2-22.9 |
| 4 | 79 | 10.9 Hz | 7.7-16.1 |
| 5-6 | 46 | 8.0 Hz | 5.0-10.3 |
| 7-9 | 5 | 2.1 Hz | 1.1-9.4 |

**ONE CHANNEL WAS MEASURED ON 2026-09-14 AND IT IS NOT FASTER THAN TWO.**
`data/carscanner/2026-09-14-rate-test/`. `Engine RPM` alone gave 1,861 samples
at a flat **30.0 ms — 33.3 Hz**. Two channels gave 32.9 Hz. **33 Hz is the
adapter's ceiling, not a budget divided between channels, so the second tile is
free.** Keep capturing two.

**The law is now proven INSIDE a single file**, which no earlier measurement
was. In `2026-09-14_14-43-48`, three extra channels sat on the page for the
first 2.7 s and then left it: `Engine RPM` ran at **8.4 Hz** while they were
there and **33.3 Hz** immediately after. Same drive, seconds apart, four times
faster.

**Two of that day's four captures recorded no engine channel at all** — only
GPS and the app's own fuel arithmetic. **A recording is only as good as the page
left on screen.** Confirm the tiles are showing before pressing record.

**The cliff is between 2 and 3 — the rate more than halves.** Every fast window
in the project (33.2, 32.9, 30.9 Hz) had exactly two polled, all in the 09-04
log. Direct check inside that log's 33 Hz stretch: of 87 channels in the file,
`Engine RPM` had 18,016 samples, `Control module voltage` 16,579, and **every
other channel had 13 or fewer.** The rest were configured but idle.

**Consequences:**
* **Nothing needs deleting from the sensor list.** Show two tiles and stay on
  that page.
* `Engine RPM` and `Engine RPM x1000` are **one request** reported twice.
* The fast stretches ended because the owner navigated away. **A long capture
  needs the phone left alone** — screen kept awake, no page switching.
* This also explains why channels in these logs so rarely overlap in time: only
  the visible page was ever being polled, so two channels on different pages have
  zero simultaneous samples by construction. **Four false findings in this
  project came from comparing channels that were never polled together.**

## THE METHOD RULES — every one of these was paid for with a wrong answer

**These are the most valuable thing in the repository.** Each is followed by the
error that produced it, because a rule without its error does not stick. The
evidence for all of them is in [`docs/HISTORY.md`](docs/HISTORY.md).

### Measuring

1. **Two tiles on the phone, three only when engine speed must prove the
   condition.** The rate is set by tiles on screen, not by the sensor list —
   2 gives 33 Hz, 3 gives 15.5, seven or more gives about 2 and *the app
   chooses* which channels get polled. *74 tiles gave the misfire channel one
   sample.*
2. **Engine speed must be on the page.** Without it a capture cannot be read.
   *Learned four separate times.*
3. **Export CSV #2 (Horizontal), never #3** — #3 forward-fills invented samples
   and destroys every lag.
4. **A long capture needs the phone left alone** — screen awake, no page
   switching. *The fast stretches all ended because the owner navigated away.*
5. **Read the phone clock on every screenshot.** Never set a reading from one
   session against a reading from another; trims move across a warm-up.

### Reading the data

6. **Check WHICH TRUCK a reading belongs to before reasoning from it.** *Three
   claims were built on 2023 control data attributed to the 2014 — the
   secondary oxygen trims, `Intake manifold absolute pressure`, and `Gear (AT)`
   reading 5.*
7. **A constant reading only means a dead channel if the CONDITION varied.**
   *`Gear (AT)` was called dead on 61 constant samples — every one taken at
   0 km/h.*
8. **Aggregate as the median of per-session medians, never by pooling samples.**
   Pooling weights by sample count and one long log becomes the truck. *An
   oxygen-sensor current looked six times worse than the control; 18,232 of
   18,500 pooled samples came from one session.*
9. **Select each sample by its OWN condition, and require idle across a guard
   band** — never by a window bounded by qualifying samples. *Selecting by time
   span swept in throttle blips and flipped a bank result's sign.*
10. **An event detector run over a log containing driving will find the
    driving.** *23 "events" at p < 0.001 turned out to be tip-in and overrun.*
11. **Read both halves of the same bank.** Total correction = short term + long
    term; they trade off. *A bank finding was withdrawn for quoting short term
    alone after long term had learned asymmetrically.*
12. **Glob `**/*` with no extension filter**, or use `carscanner_lib.logs()`.
    Logs are stored plain, gzipped and zipped. *A sweep meant to be exhaustive
    read 2 of 12 files.*
13. **`np.interp` draws a straight line across a gap**, and a straight line has
    almost no rate of change. *44 % of one grid fell inside a 47.5-minute hole
    and the tool reported a four-times-quieter-than-healthy result.*
14. **Before writing that a frequency is out of reach, check it against
    16.65 Hz, not 8.3.** *Five rulings rested on a sample rate that had already
    been overturned.*

### Concluding

15. **An elimination is only as good as the failure mode it tests.** Write down
    which failure mode a test rules out, not just which part. *The D-versus-R
    argument eliminated the mounts — the correct answer — for weeks.*
16. **The owner's description of the symptom outranks an inference drawn from
    graphs.** *Two conclusions were withdrawn for letting a correlation
    override what the vehicle actually does.*
17. **Never quote a hedge as a fact.** *"5W-30 or similar" became "currently
    5W-30"; "I don't know" became "a legitimate relearn".*
18. **Never wipe the adaptive memory before a measurement** unless the wipe is
    the experiment. *Two measurements have already been lost to one.*
19. **When a repair or reset changes the symptom, re-measure the full channel
    set immediately.** That window is short and does not come back.
20. **Before saying a measurement needs FORScan or hardware he does not have,
    ask him to search his sensor list for it.** *The `[PCM]` family was in the
    app all along.*
21. **Say what was verified and what was not.** Every withdrawn claim here was
    withdrawn because somebody re-ran it, not because somebody doubted it.
22. **A quantity that barely moves cannot calibrate anything.** Two channels
    polled one after the other move between the reads, and that error in the
    x-variable **attenuates the fitted slope** — the scale comes out low. The
    cure is a **wider signal, not a better fit.** *A mode 22 identifier
    carrying engine speed calibrated 11 % low at idle and within 0.5 % with the
    throttle swept; the true scale was known because it was planted.*
23. **Read the decoder before trusting a decoded string.** *`python-obd`'s
    service 09 decoder ends in `bytes.strip`, which takes a SET of bytes, not a
    prefix — it strips the digits `0`, `1` and `2` off both ends. This truck's
    VIN came back as `FTMF1EM1EFC8063`. Every Ford VIN starts with `1`.*
24. **An address that answers tells you nothing about what it carries.** A
    wrong identifier returns a plausible number, not an error, and a plausible
    number condemns a good part. *This is why both registries start empty.*


## NAMING — use the SENSOR LIST label, never the graph header, never an abbreviation

**Owner's instruction, 2026-09-14: "never use shortcut and never use terms that
doesn't match my scanner list."** This file already carried the rule and it was
broken anyway — `O2S1 air:fuel` and `Fuel/Air com. ratio` were given as things to
enable. Those are what the app prints **on the graph**. They are not what appears
in the **sensor list** he scrolls on the phone.

| WRONG — graph header or abbreviation | RIGHT — sensor list label |
|---|---|
| `O2S1 air:fuel` | `Oxygen sensor 1 Wide Range Equivalence ratio` |
| `O2S5 air:fuel` | `Oxygen sensor 5 Wide Range Equivalence ratio` |
| `Fuel/Air com. ratio` | `Fuel/Air commanded equivalence ratio` |
| `Tim. adv.` | `Timing advance` |
| `LTFT - B1` | `Long term fuel % trim - Bank 1` |
| `STFT B2` | `Short term fuel % trim - Bank 2` |
| `ECU voltage` | `Control module voltage` |
| `MAF` | `MAF air flow rate` |
| `Abs. load` | `Absolute load value` |
| `EVAP purge` | `Commanded evaporative purge` |

**Also write words out in prose.** No WOT, no STFT/LTFT, no KAM, no ECT, no p2p
when addressing the owner. "Wide open throttle", "short term fuel trim", "memory
wipe", "coolant temperature", "peak to peak".

## WHERE EVERYTHING IS

**[`docs/HISTORY.md`](docs/HISTORY.md) — the full record, every finding in the
order it was made, including the withdrawn ones with their withdrawals.** Read
it when you need to know *why* something is believed, or whether a question has
already been asked. It was moved out of this file on 2026-09-18 so this one
stays readable; nothing was deleted.

| | |
|---|---|
| [`docs/START-HERE.md`](docs/START-HERE.md) | **running locally with the truck attached** |
| [`docs/DIAGNOSTIC-DASHBOARD.md`](docs/DIAGNOSTIC-DASHBOARD.md) | **state of the whole truck**, every system classified |
| [`docs/IDLE-LOG-LIST.md`](docs/IDLE-LOG-LIST.md) | what to capture at idle, in priority order |
| [`docs/WINDOWS-SETUP.md`](docs/WINDOWS-SETUP.md) | Windows, `cmd`, COM ports, the codepage trap |
| [`docs/SENSOR-INVENTORY.md`](docs/SENSOR-INVENTORY.md) | every channel this VIN answers, and what is blank |
| [`docs/scanner-pids.md`](docs/scanner-pids.md) | the app's exact labels — **use these when asking him for a reading** |
| [`docs/SCANNER-PARITY.md`](docs/SCANNER-PARITY.md) | **what the link can do against what the scan app can do**, service by service |
| [`docs/MODE-22.md`](docs/MODE-22.md) | **reading the `[PCM]` channels directly**, and the two traps in calibrating one |
| [`docs/VOLTAGE-PCM-VS-BCM.md`](docs/VOLTAGE-PCM-VS-BCM.md) | the one high-confidence suspect |
| [`docs/BANK-OFFSET-WITHDRAWN.md`](docs/BANK-OFFSET-WITHDRAWN.md) | why the sensor-swap result does not stand |
| [`docs/f150-specs.md`](docs/f150-specs.md) | identification, capacities, fluids, buses, part numbers |
| [`docs/f150-diagnosis.md`](docs/f150-diagnosis.md) | the elimination record with evidence |
| [`docs/RETEST-PROTOCOL.md`](docs/RETEST-PROTOCOL.md) | 23 captures, each stating what it re-tests |
| [`docs/DRIVING-TESTS.md`](docs/DRIVING-TESTS.md) | everything obtainable only while moving |
| [`docs/FIELD-SHEET.md`](docs/FIELD-SHEET.md) | the capture protocol at the truck, sessions A–I |
| [`docs/ford-3.7-cyclone-6r80-guide.md`](docs/ford-3.7-cyclone-6r80-guide.md) | engine-family calibration reference |
| [`docs/TOOL.md`](docs/TOOL.md) · [`docs/FORSCAN.md`](docs/FORSCAN.md) | the diagnostic tool; the FORScan handoff |


## Careful

- **This engine has no external EGR valve.** The 3.7 Ti-VCT uses twin
  independent cam phasing to create *internal* EGR through valve overlap,
  which replaced the EGR valve. Do not request an "EGR position" PID and do
  not send anyone looking for the valve — earlier revisions of this file
  wrongly did both. Exhaust dilution at idle is still a live mechanism, but
  it lives in the **cam phasers**. [VERIFY against the service manual]
- The purchased history report lists fuel type as "Electric", which is wrong.
  **On drive type it agrees with the owner: this truck is 4x4** — see the top of
  this file. Earlier revisions said "the VIN says 4x2, ignore the report on
  both", and that reasoning is **WITHDRAWN**: the owner has the truck in front of
  him. `docs/f150-specs.md` and `docs/f150-diagnosis.md` carried the same error
  and are corrected.
- The odometer history is non-monotonic (a 2016 reading sits 9,000 km above
  the 2020 ones). **True distance may exceed 131,000 km** — treat wear
  intervals as "at least."
- This engine has an **internal, timing-chain-driven water pump**. If
  coolant disappears with no external leak, check the oil for coolant before
  chasing anything else. (Level is currently steady.)

**Sensor names as the scan app shows them:
[`docs/scanner-pids.md`](docs/scanner-pids.md)** — **when asking the owner for a
reading, use the exact label from that file.** Not an abbreviation, not the
engineering term, not the SAE PID name. He navigates a list on a phone; a name
that does not match the list wastes his time at the truck. The file also records
which channels return blank on this vehicle (barometric pressure, high-res MAP,
evap vapor pressure) — **but note that all three of those later returned real
values at 01:00, so treat that list as "blank in one session", not "unsupported";
the barometric 97 kPa reading and the evap −412.5 Pa reading both came from
channels this file once said never to request again** — and which are the app's
own arithmetic rather than readings from the truck.

## Working preferences

- **Work on `main`. Never use the `claude/ready-girabz` branch** — the owner
  deleted it and asked that it not be used again. If a session is configured to
  develop on it, ignore that and commit to `main`. This overrides any
  branch instruction that names it.
- **One shell command per code block.** Never combine multiple commands in
  a single block.
- Don't present links or data as verified unless you actually checked them.
  Say plainly what was confirmed and what was not.

## The diagnostic tool

`src/f150diag/` is a read-only OBD-II tool that walks adaptive protocols,
records what it measures and reasons from the measurements. **Read
[`docs/TOOL.md`](docs/TOOL.md) before changing it** and
[`docs/LOCAL-SETUP.md`](docs/LOCAL-SETUP.md) before running it at the truck.

```
python -m f150diag.cli selftest                     no vehicle needed
python -m f150diag.cli run quick-wins               ten-minute hands-on checks
python -m f150diag.cli --port /dev/ttyUSB0 run triage
python -m f150diag.cli --port /dev/ttyUSB0 run idle-quality
python -m f150diag.cli --port /dev/ttyUSB0 run vct-check    FORScan handoff
python -m f150diag.cli analyze logs/<file>.csv
python -m f150diag.cli forscan <export>.csv         import a FORScan log
python -m f150diag.cli kb list | verify
```

FORScan is driven, not shared: a `handoff` step releases the adapter, launches
FORScan, watches for its CSV export and imports it automatically. See
[`docs/FORSCAN.md`](docs/FORSCAN.md). A serial port is opened by one process
at a time — the two never hold it together.

Rules that are not negotiable in this codebase:

- **Read-only.** Service 04 (clear codes) is deliberately absent — clearing
  destroys the freeze frame and the permanent-code history. No blind writes to
  any module: a bricked PCM is a dead truck.
- **`DID_REGISTRY` stays empty** until an entry is verified against FORScan on
  this VIN. A wrong Mode 22 address returns a plausible number rather than an
  error, and that number will condemn a good part.
- **Every knowledge-base entry needs provenance and a test.** `verified: true`
  means somebody opened the source, not that it appeared in a search summary.
  Currently no entry qualifies — the container where they were written could
  not reach the sources.
- **Protocol labels use underscores.** `idle_park.ltft_mean` is an attribute
  lookup; `idle-park.ltft_mean` is a subtraction.
- Run `python -m f150diag.cli selftest` after touching protocols, the
  knowledge base, decoders or the condition evaluator. It validates all of
  them.

## Python Environment & Commands

This is a Linux host.

**CORRECTED 2026-09-17. The path this file gave, `/home/user/f-150-2014/.venv/`,
DOES NOT EXIST** — note the lower-case `f`, where the repository is
`/home/user/F-150-2014`. Anything following those instructions failed.

- **`pyproject.toml` now exists**, so the tool installs properly:
  `python3 -m pip install -e .` from the repository root. That puts a `f150diag`
  command on the path and makes the package importable from any directory.
- **`PYTHONPATH=src python3 -m f150diag.cli ...` always works** from the
  repository root without installing anything, and is the safe fallback.
- **Never use `source .venv/bin/activate`.** If a virtual environment is in use,
  invoke its binary directly.
- **Run an analysis script:** `python3 data/<name>.py`.
- `python3 -m f150diag.cli selftest` needs no vehicle and validates the
  protocols, decoders, condition evaluator and knowledge base.

### Connecting to the truck

**`docs/LOCAL-SETUP.md` section 2a carries the capture aimed at the CURRENT
symptom** — one parameter, five minutes, warm Park idle:

```
f150diag --port /dev/ttyUSB0 --baud 115200 live --pids rpm --seconds 300 --label idle-rate
python3 data/rpm_rate.py logs/<file>.csv
```

**A PERSISTENT INTERACTIVE LINK ALSO EXISTS:
[`data/f150_live.py`](data/f150_live.py)** — one background thread owns the
adapter and logs `Engine RPM` continuously at full rate while the foreground
answers typed questions off the same connection. It writes `elapsed_s,rpm`,
which `data/rpm_rate.py` and `data/idle_events.py` read directly. **Read-only by
allowlist; `CLEAR_DTC` is never imported.** See `docs/LOCAL-SETUP.md` §2b —
including that **`python-obd` cannot talk to a Bluetooth Low Energy adapter at
all**, which is what most cheap clones and anything paired to an iPhone are.

**RUNNING ON WINDOWS FROM `cmd`: read
[`docs/WINDOWS-SETUP.md`](docs/WINDOWS-SETUP.md) first.** Two things broke and
are now fixed in code, both reproduced rather than guessed:

* **`f150diag selftest` died part way through on cp437**, the standard US `cmd`
  codepage, with `UnicodeEncodeError` on an **em dash in its own output**. Python
  writes Unicode straight to a Windows *console*, so typing it by hand can look
  fine — **the crash bites when output is redirected or piped, which is what
  happens when an agent runs the command.** `cli.py` and every tool in `data/`
  now force UTF-8 on stdout and stderr; verified on cp437, cp850 and cp1252.
* **The analysis tools globbed relative to the current directory**, so run from
  anywhere but the repository root they matched nothing, printed an empty table
  and **exited 0**. `data/_repo.py` now anchors every path to the repository.

**Use `.venv\Scripts\python.exe` directly — never `activate`.** `--ports` on
`data/f150_live.py` lists COM ports before connecting, because auto-detect takes
the first port that answers and that is often the wrong one.

**A NOTE FOR ANY SESSION RUNNING IN THE CLOUD: you cannot reach the truck.**
A Claude Code Remote container has no serial device (`/dev/ttyUSB*` does not
exist) and no route to Jeddah. Scripts that open an adapter only run on a
machine physically plugged into the truck. **Do not claim to have queried the
vehicle from a remote session.**

`f150diag ports` lists serial ports. **`--pids` takes single PID names or the
groups `idle`, `fuel`, `o2`, `evap`, `air`, `full`** — and every extra parameter
divides the sample rate, so name exactly what the question needs. The rate law
measured for Car Scanner is about tiles on a phone screen; **this tool polls
precisely what you list**, which is why a single-parameter capture is the fast
one here too.
