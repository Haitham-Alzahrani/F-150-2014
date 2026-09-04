# Working alongside FORScan on the same machine

## They cannot share the adapter

A serial port is opened by one process at a time. Whoever gets there first
holds it; everyone else is refused. FORScan and `f150diag` therefore **take
turns** — one disconnects, the other connects. There is no software fix,
because the exclusivity is in the operating system's handling of the device.

Two adapters on a Y-splitter is physically possible, since CAN is a
multi-drop bus and additional listeners are electrically fine. It is still a
bad idea: two testers polling at once produce request collisions and replies
attributed to the wrong requester, which is worse than no data because it
looks like data.

So the integration is at the **file level**, and the division of labour is
clean:

| Tool | Does |
|---|---|
| **FORScan** | Ford enhanced parameters — cam position commanded vs actual above all — and module-level access this tool does not have |
| **f150diag** | Generic OBD, adaptive protocols, guided physical procedures, statistics, causality, the knowledge base |

---

## Driving FORScan from a protocol

FORScan has no command line, no API and no scripting interface — nothing
public — so it cannot be called as a library. It can be *orchestrated*: this
tool owns the sequence, hands the adapter over, and collects the result.

A protocol step does the whole handoff:

```yaml
- id: vct_handoff
  type: handoff
  request: vct          # vct | misfire | fuel
  label: vct
  seconds: 90
  timeout_s: 1200
  next: vct_verdict
```

What happens when it runs:

1. The adapter is **closed and released**. The session stays live; only the
   port is given up.
2. FORScan is launched, if it can be found.
3. The exact parameter list to add is printed, and what to record.
4. The tool **watches for a new export** across the FORScan data folder,
   Documents, Downloads and Desktop — waiting for the file size to settle
   before reading, since a file appears in the directory before it is
   finished being written.
5. The export is imported, cam tracking computed, and the metrics enter the
   protocol context so the next `branch` can decide on them.
6. The adapter is reconnected and the protocol continues.

Step 4 is the point. The alternative — "export it and tell me the filename" —
puts a person in the middle of every handoff.

Branch on the result like any other measurement:

```yaml
- when: vct_worst_error > 5 or vct_actual_periodic
  finding: vct-solenoid-phaser
```

Published metrics: `vct_worst_error`, `vct_actual_periodic`, `vct_tracks`,
`vct_pairs`, and per-channel `vct_<cam>_<bank>_worst_error` / `_mean_error` /
`_sd` / `_periodic`. `<label>.imported` says whether an export arrived at all.

`f150diag forscan-status` shows where FORScan was found, whether it is
running, which folders are watched, and the parameter sets available. Set
`FORSCAN_EXE` and `FORSCAN_DATA` if the defaults miss.

Two protocols use this: `vct-check` standalone, and `idle-quality`, which
offers the handoff automatically when it finds an unstable idle with normal
fuel trims — the case where fuel control has been excluded and cam timing is
the remaining dilution path.

Before a session starts, `f150diag run` refuses to open the port if FORScan
is already running, rather than failing with a permission error mid-protocol.

## The workflow

1. Run the `idle-quality` protocol with `f150diag`. Disconnect when it ends.
2. Open FORScan. Add the parameters this tool cannot read — for the open
   question that means **VCT intake and exhaust, desired and actual, both
   banks**, plus rpm so the two can be aligned.
3. Record a run at warm idle. Stop it, then save as **CSV**, not `.fsl` —
   `.fsl` is FORScan's own format for replaying inside the app.
4. Bring it back:

```
f150diag forscan <exported>.csv
```

That runs the same analysis as a native log — rpm stability, periodicity,
fuel-trim causality — and adds cam tracking: desired against actual, the
worst tracking error, and whether actual position oscillates while the
command sits still.

On Windows, saved runs live under the FORScan folder in `AppData\Roaming`,
with an `fsl` subfolder for recorded live data. [VERIFY — from search
summaries, not from a machine with FORScan installed.]

---

## Column mapping

FORScan header text varies with version, language and vehicle profile, so
columns are matched by synonym rather than by position. Headers are
normalised before matching — `Long FT1 (%)`, `LONGFT1` and `long_ft1` all
collapse to the same key.

Every import prints what it mapped and what it did not. **Unmapped columns
are carried through under their original names rather than dropped**, so
nothing disappears silently. If something useful is unmapped, add it to
`SYNONYMS` in `src/f150diag/forscan.py`.

The mapping table is marked `[VERIFY]` throughout. It uses the conventional
Ford PID mnemonics, but none has been confirmed against a real export from
this vehicle. **A wrong mapping is worse than a missing one**, because it
relabels real data with the wrong name — check the mapping report on the
first import before trusting any conclusion drawn from it.

---

## What this does NOT let us do

**It does not give this tool the enhanced PIDs.** Reading FORScan's export
tells us what FORScan measured; it does not tell us the data identifiers
FORScan used to measure it. `DID_REGISTRY` stays empty.

I had expected FORScan's own configuration files to carry those addresses.
They do not: reportedly it is **not possible to add custom PID definitions to
FORScan's internal database** in current versions, and vehicle profiles are
stored in a coded format rather than as readable definitions. [VERIFY]

The documented route to the addresses is different: **capture the traffic
FORScan sends to the adapter while it displays a parameter, and read the
Mode 22 requests directly.** The community does this with a serial port
monitor for USB adapters, or Wireshark for network adapters — vary the engine
condition, watch which identifier's response tracks the value on screen.

That is a legitimate way to learn a real address, and the resulting entry
would be `provenance: verified` — measured on this vehicle and cross-checked
against a tool that already knows the parameter. It is also the only route
that does not involve guessing, which is why `DID_REGISTRY` ships empty.
See `docs/ENHANCED-PIDS.md` for the verification procedure.
