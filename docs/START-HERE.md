# START HERE — running locally, with the truck attached

**For a Claude session on the owner's Windows machine. Read this before anything.**

---

## 0. What you are looking at

A 2014 F-150 3.7 with **one open complaint**: *a very small vibration that
accompanies engine speed CHANGING*, plus unsteady speed. The big seat shake is
**closed** — new mounts fixed it. Do not chase it, do not cite it.

State of the whole truck: [`DIAGNOSTIC-DASHBOARD.md`](DIAGNOSTIC-DASHBOARD.md).
**Confirmed faults: none. One high-confidence suspect: the PCM supply voltage.**

**The owner is a working mechanic. Give him reasoning, specs and procedures.**

---

## 1. First time on this machine

```
setup.cmd
```

Creates the virtual environment, installs, runs the self-test, and exercises the
car link against a **simulated** adapter so the plumbing is proven before you go
near the truck. It stops at the first real failure.

---

## 2. THE CAR LINK — this is the part that lets Claude talk to the truck

An interactive script that reads typed commands **cannot be driven by an agent**:
every shell command is a separate process, so the connection dies between
questions and each reading costs a fresh ELM327 handshake.

So the link is split. **One daemon owns the adapter. Every question is a
separate one-shot client command.** That is exactly the shape of a tool call.

**Start the daemon once** (leave the window open, or run it in the background):

```
.venv\Scripts\python.exe data\f150_agent.py serve --port COM5
```

Don't know the port:

```
.venv\Scripts\python.exe data\f150_agent.py ports
```

**Then ask it things, one command at a time:**

| Command | What it does |
|---|---|
| `f150_agent.py status` | up? logging? how many samples, what rate |
| `f150_agent.py read RPM` | one reading, any python-obd command name |
| `f150_agent.py snapshot` | ~11 channels in one call |
| `f150_agent.py log start park-idle` | **continuous Engine RPM at full rate** |
| `f150_agent.py log stop` | stops, prints the file and the analysis command |
| `f150_agent.py list` | what python-obd can reach |
| `f150_agent.py stop` | shut the daemon down |

Every reply is one JSON object. **Logging keeps running at full rate while you
ask other questions** — measured at **32.4 Hz sustained** through a status call,
a read and an 11-channel snapshot on the same connection.

**No car? `serve --sim`** runs the whole thing against a simulated adapter.
Every reply then carries `"sim": true`. Never report simulated numbers as the
truck.

### It is read-only, and the guard is on the service mode

Modes 1, 2, 3, 6, 7, 9 allowed. **Mode 4 refused.** Verified against python-obd
0.7.3: `getattr(obd.commands, 'CLEAR_DTC')` passes a `hasattr` check, resolves to
`OBDCommand('CLEAR_DTC', ..., b'04')`, and sits in `base_commands()` so the
library treats it as always supported. A name blocklist would not be enough.
`read CLEAR_DTC` returns **REFUSED**.

Clearing destroys the freeze frame, monitor readiness and the distance and
warm-up counters. **Two measurements in this project have already been lost to
an adaptive reset nobody asked for.**

**A NOTE ON `.claude/settings.json`, because testing changed it.** The deny list
first read `Bash(*CLEAR_DTC*)`. That blocked the command that **verifies the
guard works** — `f150_agent.py read CLEAR_DTC`, whose whole job is to come back
REFUSED — and it would block a grep for the string too. **A rule that prevents
testing a safety property while adding no safety is worse than no rule**, because
it reads like protection and is not. The real protection is the mode-4 guard in
the code, which is tested. The deny is now narrowed to
`Bash(*obd.commands.CLEAR*)`, the shape of constructing the command object
directly in raw python, which is the actual dangerous act.

---

## 2c. THE `[PCM]` CHANNELS — service 0x22

The channels that would settle the misfire question — `[PCM] Currently Detected
Engine Misfire`, `[PCM] Knock Sensor 1`/`2`, `[PCM] Cylinder 1-6 Acceleration
Value` — are Ford enhanced, and **`python-obd` has no service 0x22 at all**.
`data/f150_did.py` builds those requests by hand, through the same connection.

**The guard is on the service byte, by number: 0x22 only.** Write, routine
control, security access, reflash and reset are each refused explicitly.

```
python data/did_scan.py scan --from 0x1100 --to 0x11FF
```

```
python data/did_scan.py identify 0x1100 RPM --samples 250 --name "Engine speed (mode 22)"
```

**Blip the throttle steadily all the way through that second command.** An
address that answers tells you nothing about what it carries, so the scale is
fitted against a known channel — and at idle, where engine speed moves only
about 30 rpm, the fit comes out **11 % low** on an address that is *correct*.
Swept, it lands within 0.5 %. Full reasoning and the measured table:
[`MODE-22.md`](MODE-22.md).

Nothing is interpreted until it is identified. **`data/did_registry.json` is
empty and no identifier has been verified on this VIN.**

```
python data/f150_agent.py sim sweep on
```

rehearses the whole identification path against `serve --sim`, with no hardware.

## 3. From a capture to an answer

The daemon writes `elapsed_s,rpm`, which the analysis tools read directly:

```
.venv\Scripts\python.exe data\rpm_rate.py logs\<file>.csv
.venv\Scripts\python.exe data\idle_events.py logs\<file>.csv
```

**`rpm_rate.py` needs about 500 samples — 15 s at 33 Hz.** Shorter and it tells
you so rather than printing an empty table.

Reference, whole archive: 2014 median **13.53 rpm/s** against the 2023 control's
**7.17** — **1.89×**, agreeing with peak-to-peak's 1.90×.

---

## 4. What to capture, in order of value

1. **30 min** — `Engine RPM` + `[PCM] Currently Detected Engine Misfire`.
   **Car Scanner, not this tool** — the `[PCM]` channels need mode 22.
2. **Meter across the battery posts at idle.** Ten minutes, no scanner, and it
   settles the one high-confidence suspect. Procedure in the dashboard.
3. **3 min ×2** — both short term trims + `Engine RPM`, then both long term
   trims. **Do not touch the throttle.**
4. **A DRIVING capture** — the transmission has never been measured while moving.

---

## 5. Limits that are real, not bugs

* **`python-obd` implements no mode 22.** Every `[PCM]` channel — knock sensors,
  cylinder acceleration, cylinder head temperature, A/C pressure, ATF
  temperature, turbine speed, gear ratio — is **invisible to this tool**. Car
  Scanner on the phone and FORScan reach them. `list` reports the library's
  reach, not the truck's. It **does** reach Mode 06 misfire counts.
* **BLE adapters cannot work.** python-obd opens a serial port; Bluetooth Low
  Energy presents none. Most cheap clones, and anything paired to an iPhone.
* **FORScan is Windows-only**, so this machine is the one platform where the
  enhanced Ford data is reachable at all. See [`FORSCAN.md`](FORSCAN.md).
* **Manifold pressure is unavailable on this VIN.** Mechanical gauge only.

---

## 6. Rules this project enforces on itself

* **Work on `main`.** Never the `claude/ready-girabz` branch.
* **Use the sensor list label**, never a graph header or abbreviation, and write
  words out in prose — no WOT, no STFT, no KAM.
* **Never wipe the adaptive memory before a measurement** unless the wipe is the
  experiment.
* **A constant reading only means a dead channel if the CONDITION varied.**
  Three claims in this repo were withdrawn for breaking that.
* **Say what was verified and what was not.** Every withdrawn claim here was
  withdrawn because somebody re-ran it, not because somebody doubted it.
