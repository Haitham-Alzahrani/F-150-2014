# Ford enhanced parameters — the honest position

## What is missing and why it matters

Generic OBD-II (service 01) carries emissions data. Everything else a Ford
dealer tool reads lives behind manufacturer-specific data identifiers, read
with **service 22 (ReadDataByIdentifier)**, addressed to a specific module.

For this truck's open question the gap is concrete:

| Wanted | Available generically? |
|---|---|
| Fuel trims, MAF, MAP, rpm, timing | Yes — service 01 |
| Stored / pending / permanent codes | Yes — services 03 / 07 / 0A |
| Misfire monitor results | Partly — service 06, raw and unscaled |
| **Cam position commanded vs actual** | **No — Ford enhanced only** |
| **Per-cylinder misfire counters as Ford reports them** | **No** |
| Actuator commands, service routines | No — needs write access |

The VCT branch of the idle diagnosis therefore cannot be completed with this
tool. FORScan or Ford IDS is the right instrument for it.

---

## Why `DID_REGISTRY` is empty

Ford does not publish these identifiers. What circulates is community reverse
engineering — genuinely valuable, sometimes the only public record of a
parameter, and of wildly varying accuracy.

An address that is wrong does not fail loudly. It returns *a number*. That
number then gets used to condemn a cam phaser.

So the registry ships empty rather than seeded with plausible-looking values,
and every entry that gets added carries provenance saying exactly where it
came from and whether anyone confirmed it on this vehicle.

---

## Adding a DID properly

```python
Did(
    did="1E1C",                    # 4 hex characters
    name="vct_intake_actual_b1",
    description="Intake cam actual position, bank 1",
    unit="deg",
    nbytes=2,
    scale=0.0078125,
    offset=-24.0,
    module="7E0",                  # PCM
    provenance="verified",         # verified | community | unverified
    notes="Cross-checked against FORScan on VIN ...80632, 2026-09-xx",
)
```

`provenance` values:

- **verified** — read on *this* vehicle and cross-checked against a tool that
  already knows the parameter, such as FORScan showing the same value at the
  same moment. This is the only grade that may drive a conclusion alone.
- **community** — published by somebody else, plausible, unconfirmed here.
  Usable as a hypothesis. Say so in the report.
- **unverified** — guessed or inferred. Never let it reach a conclusion.

---

## How to verify one, concretely

1. Run FORScan alongside, displaying the parameter you want.
2. Read the candidate DID with this tool at the same moment:
   `read_did(elm, candidate)`.
3. Vary the engine condition — idle, 2500 rpm, cold, hot — and confirm the
   two move together across the whole range. A single matching value at idle
   proves nothing; two unrelated parameters can agree once.
4. Only then write the entry with `provenance="verified"` and a note saying
   what it was checked against and when.

---

## Discovery scanning

Sweeping the DID space to see what answers is a read operation and does not
reprogram anything. Two cautions that are engineering, not nervousness:

- A scan is slow and floods the bus. Do it with the engine off and the
  battery on a maintainer, not mid-diagnosis.
- An address that answers tells you a parameter exists. It does not tell you
  what the parameter *is*. Discovery finds candidates; step 3 above is what
  turns a candidate into knowledge.

A discovery command is not implemented yet. When it is, it belongs behind an
explicit flag and should write its results as `unverified` entries, never as
usable parameters.
