# Running this locally with Claude Code

The point of running locally is the closed loop: Claude opens the adapter,
reads a result, and picks the next test from what it just measured. Sending
logs back and forth is one round trip per day; local is one per second.

---

## 1. Hardware

| For | You need |
|---|---|
| Everything in this tool | Any ELM327-class adapter, USB or Bluetooth |
| Ford enhanced data (cam position, Ford misfire counters) | Windows laptop + FORScan + an adapter it supports (OBDLink EX or similar) |

The 2014 F-150 uses ISO 15765-4 CAN. The tool auto-detects the protocol.

A cheap clone manages only a few samples per second, and every extra PID
divides that further. Sample rate is what buys resolution in the periodicity
analysis, so keep PID counts modest when the question is rpm stability.

---

## 2. Clone and install

```
git clone <this repo>
cd F-150-2014
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Verify with no vehicle attached:

```
.venv/bin/python -m f150diag.cli selftest
```

That exercises the PID decoders, DTC decoding, the condition evaluator
(including that it refuses to execute code), the periodicity detector, the
verdict thresholds, every protocol's step graph, and the knowledge base
schema. It should end with `all checks passed`.

If the module is not found, run with `PYTHONPATH=src`, or
`.venv/bin/pip install -e .` once a packaging file exists.

---

## 3. Find the adapter

```
.venv/bin/python -m f150diag.cli ports
```

Linux usually shows `/dev/ttyUSB0`; a Bluetooth adapter appears as
`/dev/rfcomm0` after binding. On Windows it is a `COM` port. If the port
exists but is refused on Linux, the user needs to be in the `dialout` group.

---

## 4. At the truck

Start with triage — five minutes, and it stops you running a long protocol
against the wrong system:

```
.venv/bin/python -m f150diag.cli --port /dev/ttyUSB0 run triage
```

Then the deep protocol it names, usually:

```
.venv/bin/python -m f150diag.cli --port /dev/ttyUSB0 run idle-quality
```

Rehearse the questions first, without a vehicle, so you know what you will be
asked to do and what to have within reach:

```
.venv/bin/python -m f150diag.cli run idle-quality --dry-run
```

A dry run prints every prompt but records no findings — it has measured
nothing, so it has concluded nothing.

---

## 5. Working with Claude Code alongside

Claude reads the same repo. Useful things to ask for at the truck:

- *"Run the idle-quality protocol and interpret each measurement as it lands"*
- *"That rpm log looks periodic — is it, and at what frequency?"*
- *"Fuel trims came back at +14 idle, +3 at 2500. What does that rule out?"*
- *"Add a protocol step that tests X"* — protocols are data; they can be
  edited between runs without touching code
- *"Add what we just found to the knowledge base"* — with provenance
  `measured`, which is the highest grade of evidence in this base because it
  came from this vehicle

The network here is not blocked the way the cloud container is, so locally
Claude can actually open forum threads, TSB documents and parts catalogues
and populate the knowledge base with `verified: true` entries — which none of
the current ones are.

---

## 6. What to have within reach

- Hose clamping pliers (the pinch tests are the cheapest real evidence)
- Hand vacuum pump
- Mechanical oil pressure gauge, if the VCT branch comes up
- Vacuum gauge
- Smoke machine, if trims justify it
- **Vacuum caps or plugs** sized to the manifold ports — the lines on this
  engine are hard plastic and cannot be clamped, so every isolation test means
  disconnecting and plugging, with the engine off

---

## 7. Order of work for the open idle question

0. `run quick-wins` — PCV shake test and purge valve vacuum hold. Ten
   minutes, engine off, no scan tool. Both target components never inspected
   on this truck, and both come from the Mustang 3.7 community — the same
   engine.
1. `run triage` — establishes whether anything is abnormal at all
2. If it says idle-abnormal: `run idle-quality`
3. If that lands on **unmetered air**: the protocol's own clamp tests localise
   it — purge valve, PCV, booster, in that order
4. If it lands on **dilution or mechanical** with normal trims: disconnect
   this tool, run FORScan, log VCT desired and actual for both banks plus
   rpm, export as CSV, then `f150diag forscan <file>.csv` to analyse the cam
   tracking. Swap the VCT solenoids bank to bank if it shows error.
   The two tools cannot hold the adapter at once — see `docs/FORSCAN.md`
5. `run o2-health` regardless — the sensors were "cleaned" by an unknown
   method and that question is owed an answer on its own account

Before any of it, the free test no tool can do: idle another F-150 regular
cab with the same engine alongside and compare by hand and by seat.
