# Can this tool do everything the scan app does?

**Before 2026-09-19: no, and not nearly.** The link read **live sensor data**
and nothing else. That is one of six things a scan app does. Fault codes,
freeze frame, on-board monitor results, vehicle information and readiness were
all unreachable — not badly implemented, **absent**.

**Now: yes for everything that reads the truck, with two deliberate exceptions
and one that still needs work at the vehicle.**

| What the scan app does | Service | Before | Now |
|---|---|---|---|
| Live sensor data | 01 | **yes** | yes, and faster — see below |
| Freeze frame — the snapshot stored when a code set | 02 | no | **yes** |
| Stored fault codes | 03 | no | **yes** |
| On-board monitor test results, with the module's own limits | 06 | no | **yes** |
| Pending fault codes | 07 | no | **yes** |
| VIN, calibration identifier, calibration verification number | 09 | no | **yes** |
| **Permanent fault codes** | **0A** | no | **yes — hand-built** |
| Readiness: lamp, stored-code count, monitor completion | 01 PID 01 | no | **yes** |
| Ford enhanced `[PCM]` channels | 22 | no | **reachable; none identified yet** |
| Recording to CSV | — | yes | yes, in the app's own CSV shape |
| Clearing codes | 04 | **refused** | **refused — deliberate, not a gap** |
| Trip computer, fuel economy, GPS | — | no | **not replicated, on purpose** |

## The one that matters most here: service 06

`MONITOR_MISFIRE_CYLINDER_1` through `_6` are **cumulative counters kept by the
module**, not an instantaneous channel. They carry the module's own minimum and
maximum, so pass or fail is the **module's verdict**, not an interpretation
applied afterwards.

**This bears directly on capture 1 in [`IDLE-LOG-LIST.md`](IDLE-LOG-LIST.md).**
That capture asks for thirty minutes of logging because the live misfire channel
has to be **sampled at the moment of an event** — 53 scattered samples across
three sessions almost certainly never landed on one. **A counter does not have
to be caught in the act.**

**What is NOT established:** whether this PCM answers the misfire monitor
identifiers at all. Standard practice puts cylinder *N* at identifier `0xA1+N`
with test `0x0C`, and python-obd's table agrees, but **no Ford document was
opened and this truck has never been asked.** One command settles it, and until
it has been run, service 06 is *reachable*, not *proven*.

## A library bug that would have reported the wrong VIN

python-obd 0.7.3 decodes service 09 strings ending with

```
d.strip(b'\x00' b'\x01' b'\x02' b'\x00' b'\x01' b'\x02')
```

**`bytes.strip` treats its argument as a SET OF BYTES, not a prefix.** That set
works out to `{0x00, 0x01, 0x02, '0', '1', '2', '\', 'x'}` — so the decoder
strips the **digits 0, 1 and 2** off both ends of every string it returns.

**Verified on this VIN, 2026-09-19:**

| | |
|---|---|
| True VIN | `1FTMF1EM1EFC80632` |
| What the library returns | `FTMF1EM1EFC8063` |

The leading `1` and the trailing `2` are both eaten. **Every Ford VIN begins
with `1`**, so this is not an edge case here. The VIN is how a reading is tied
to a vehicle at all, and rule 6 in `CLAUDE.md` exists because three claims in
this project were already built on data attributed to the wrong truck.

`data/f150_obd2.py` decodes service 09 itself and keeps printable characters
only. Full VIN confirmed intact end to end.

**The calibration identifier is the reason to care beyond the VIN.** This truck
has a custom tune, and nothing in this project has ever recorded which
calibration is actually in the module. The identifier and the verification
number are that fingerprint.

## Where the tool is BETTER than the scan app

**It polls exactly what you name.** The scan app's sample rate is set by **tiles
on the phone screen** — two tiles give 33 Hz, three give 15.5, seven or more
give about 2 and *the app chooses* which channels get polled. That law cost this
project four false findings, built from channels that were never polled at the
same time. This tool has no tiles: name one channel and it polls one channel.

**It holds one handshake open.** Every reading through the app costs a fresh
connection; the daemon keeps one and sustains a measured 32.4 Hz while
simultaneously answering questions.

**It refuses to interpret what it has not verified.** An unidentified service
0x22 read returns raw bytes and says so. The scan app would show a number.

**Its output feeds the analysis tools directly** — the recorded file uses the
owner's own sensor-list labels, so `rpm_rate.py`, `idle_events.py`,
`bank_offset.py` and `check_capture.py` read an agent capture with no changes.

## What is deliberately NOT replicated

**Clearing codes (service 04).** Refused by number, along with write, routine
control, security access, reflash and reset. Clearing destroys the freeze frame
and the stored-code history — evidence this project has repeatedly needed.
**This is a design decision, not a missing feature.**

**The trip computer, fuel economy and GPS.** Tier 3 of
[`SENSOR-INVENTORY.md`](SENSOR-INVENTORY.md) already classifies 33 of the app's
channels as **the app's own arithmetic, not the truck**. Reproducing arithmetic
this project has ruled inadmissible would add nothing.

**A gauge dashboard.** The output is JSON because an agent reads it.

## Still open

* **No service 0x22 identifier is verified on this VIN**, and the registry is
  empty by design. See [`MODE-22.md`](MODE-22.md).
* **Other modules have never answered.** `MODULES` in `data/f150_obd2.py` lists
  the transmission at header `7E1`, and **that address is a guess** — only
  `7E0` has ever replied in this project. A wrong header returns silence, not a
  wrong number, so trying is safe; **do not read silence as "the module is not
  there."** The transmission is the largest unexamined system on the truck.
* **Everything above is verified against the simulator**, which now builds real
  response frames and feeds them through the real library decoders rather than
  faking decoded values. **Nothing here has been run on the truck.**

## Commands

```
python data/f150_agent.py serve
```

```
python data/f150_agent.py healthcheck
```

That one call reads vehicle information, readiness, all three code services,
the freeze frame and every monitor, and reports each independently — one dead
service cannot lose the other four. The individual commands are `vehicle`,
`readiness`, `dtc`, `freeze` and `monitors --only misfire`.
