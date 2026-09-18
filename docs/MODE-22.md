# Mode 22 — reading the `[PCM]` channels directly

**Status: the mechanism is built and proven against the simulator. Nothing in
`data/did_registry.json` has been verified on this VIN yet, and the registry is
empty by design.**

## What this is for

The channels that matter most to the current symptom — `[PCM] Currently Detected
Engine Misfire`, `[PCM] Knock Sensor 1`/`2`, `[PCM] Cylinder 1–6 Acceleration
Value` — are **not** standard OBD-II. Car Scanner gets them through Ford
enhanced **service 0x22, ReadDataByIdentifier**, and `python-obd` has no service
0x22 at all: its `commands` table holds modes 1, 2, 3, 4, 6, 7 and 9 and stops.

That is the gap. Without service 0x22 the link can read engine speed, the fuel
trims and the voltages, but none of the `[PCM]` family — which is exactly the
set that would settle the misfire question.

`data/f150_did.py` builds service 0x22 requests by hand and sends them through
the same adapter connection the rest of the link uses.

## The safety guard is on the SERVICE BYTE, not on a name

Service 0x22 reads. Its neighbours in the same protocol do not:

| | |
|---|---|
| `0x2E` WriteDataByIdentifier | writes a value into the module |
| `0x31` RoutineControl | runs an actuator or a self-test |
| `0x27` SecurityAccess | unlocks the module for programming |
| `0x34`/`0x36` RequestDownload / TransferData | **reflash** |
| `0x11` ECUReset | resets the module |
| `0x14` ClearDiagnosticInformation | destroys the freeze frame |

`guard()` refuses every service except 0x22, by number:

```
REFUSED: service 0x2E (WriteDataByIdentifier) can change the vehicle.
This link reads only, service 0x22.
```

`did_command()` asserts its own first byte is 0x22 before it returns, so a
request cannot be assembled with any other service byte even by mistake.

## An address that answers tells you NOTHING about what it carries

This is the whole difficulty. A wrong identifier does not return an error — it
returns a **plausible number**, and a plausible number will condemn a good part.
That is why `DID_REGISTRY` in `src/f150diag/` has always been empty, and why
this registry starts empty too.

`data/did_scan.py scan` finds which addresses answer. On the simulator it walked
177 addresses, found exactly the three that respond, and printed:

> *An address answering says NOTHING about what it carries.*

Nothing is interpreted until it is identified. An unidentified read comes back
as raw bytes with a refusal attached:

```json
{"ok": true, "did": "11A6", "hex": "6211a607c4",
 "note": "not identified on this VIN. Raw bytes only - do not interpret."}
```

## Two routes to a verified entry, and no third

**1. Correlation against a standard channel.** Poll the identifier and a known
OBD-II channel alternately, then fit every plausible reading of the payload — 1,
2 and 4 bytes, big and little endian, signed and unsigned. **Gate: r-squared
>= 0.99 over >= 200 samples.** Scale and offset come out **measured, not
assumed.**

**2. Predicted manipulation.** For a channel with no standard twin, write down
in advance what a deliberate change should do to it, then do it and record the
result. `did_scan.py confirm` stores the prediction and the observation
together. A prediction written afterwards is not a prediction.

## THE TRAP: regression dilution — measured, not theorised

The identifier and the standard channel are polled **one after the other, not at
the same instant**, so the quantity moves between the two reads. Error in the
x-variable attenuates a fitted slope: **the scale comes out LOW.**

At warm idle the engine speed only wanders about 30 rpm, and that is not enough:

| Engine speed range during the test | Fitted scale | r-squared |
|---|---|---|
| ~6 rpm | 0.116 | 0.194 |
| ~18 rpm | 0.224 | 0.783 |
| **~32 rpm (real idle)** | **0.2225** | **0.738** |
| ~60 rpm | 0.246 | 0.979 |
| ~200 rpm | 0.249 | 0.998 |
| **~2,300 rpm (throttle swept)** | **0.2493–0.2513** | **0.9999** |

The true scale is **0.25**. At idle the fit reads **11 % low**; swept, it lands
within **0.5 %**, and four independent runs bracketed the truth from both sides.

**THE CURE IS A WIDER SIGNAL, NOT A BETTER FIT.** Identify while deliberately
sweeping the quantity across as much of its range as is safe — for engine speed,
blip the throttle right through the test; for a temperature, start from cold.

**The r-squared gate is what protects the scale**: at r-squared 0.99 the
remaining attenuation is about 1 %. The tool now recognises the signature — a
middling r-squared with a plausible slope — and says so rather than letting it
read as a wrong address.

## The second trap: field width

A quantity stored in two bytes also correlates well read as its **first byte
alone** — the same quantity, truncated. On the swept run the one-byte reading
fitted to **0.99931** against the two-byte **0.99989**. Both clear the gate, and
**their scales differ by a factor of 256.**

The rule stays **highest r-squared**, because it is correct in both directions:
reading a two-byte field as one byte truncates it and fits worse; reading a
one-byte field as two pulls in a foreign padding byte and also fits worse. A
"prefer the wider field" tie-break would pick wrongly on a genuine one-byte
identifier — it was written, tested and removed.

But when two widths fit within 0.005 of each other the test has **not** resolved
the width, so the tool says so instead of choosing silently, and names the
discriminator: the narrow reading quantises in steps of 64.4 rpm, so a wide
enough sweep makes its residual go stair-shaped.

## A weaker repeat cannot demote a verified entry

The registry is keyed by identifier, so a second, narrower run would otherwise
overwrite a measured scale with a diluted one. It is discarded instead:

```
1100 IS ALREADY VERIFIED (r-squared 0.99973 over a range of 1979.07).
This weaker run is DISCARDED, not written - the earlier measurement stands.
```

## Doing it at the truck

```
python data/f150_agent.py serve
```

```
python data/did_scan.py scan --from 0x1100 --to 0x11FF
```

```
python data/did_scan.py identify 0x1100 RPM --samples 250 --name "Engine speed (mode 22)"
```

**Blip the throttle steadily through that capture** — the whole point of the
table above. Then:

```
python data/did_scan.py show
```

```
python data/f150_agent.py did 0x1100
```

**`serve --sim` rehearses all of it with no hardware**, and every reply then
carries `"sim": true`. `python data/f150_agent.py sim sweep on` drives the
simulated throttle sweep so the identification path can be practised before
going near the truck. **Never report a simulated number as the truck.**

## What is NOT established

* **No identifier has been verified on this VIN.** Every number above is from
  the simulator, where the scaling is known because it was planted.
* The addresses this truck's PCM answers are unknown until the scan is run on
  it. The Ford identifiers for the `[PCM]` family are not published here and
  have not been confirmed from any source.
* `src/f150diag/`'s `DID_REGISTRY` stays empty regardless — it is a separate
  table with a separate rule, and nothing here feeds it automatically.
