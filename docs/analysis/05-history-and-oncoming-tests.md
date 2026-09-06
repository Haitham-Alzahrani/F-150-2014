# 05 — History, on-board test results, and the record that only exists in screenshots

2014 Ford F-150 XL · 3.7L V6 Ti-VCT · 6R80 · 4x2 · VIN `1FTMF1EM1EFC80632` · 131,313 km (PCM odometer, 2026-09-04)

**Scope.** Everything that lives only in the 277-screenshot record and the owner's own
answers — diagnostic trouble codes, Mode 06 on-board test results, readiness monitors,
repair history — plus a cross-check of those screenshot-derived claims against the four
Car Scanner datalogs wherever the two cover the same clock time.

**Bank convention used throughout:** Bank 1 = passenger side, cylinders 1, 2 and 3.
Bank 2 = driver side, cylinders 4, 5 and 6.

**Evidence grades used below:** `[FORD]` Ford service information · `[SAE]` SAE/ISO
standard · `[COMMUNITY]` forum, parts catalogue or trade-press summary, not verified at
source · `[LOG]` measured in a Car Scanner datalog in this repository · `[SHOT]` read
from a screenshot · `[OWNER]` owner statement · `[SPEC]` speculation, labelled as such.

---

## 1. Mode 06 — the on-board test results, every row

**When read:** 2026-09-05, 04:36:02 → 04:37:39 local (screenshot EXIF, 16 images
`m253-01` … `m253-16`). Engine idling in Park.

**What the numbers rest on — read this before the table.** The Keep Alive Memory was
wiped at the purge-valve replacement between 01:35 and 03:09 that same night. At the
moment the Mode 06 screens were photographed the PCM reported `[LOG]`:

| Counter | Value at 04:48 |
|---|---|
| Distance since codes cleared | **52 → 56 km** |
| **Warm-ups since codes cleared** | **0** |

So **every Mode 06 value below was accumulated in a single driving cycle of roughly
55 km, with zero completed warm-up cycles.** That matters most for the ten-driving-cycle
misfire average — see the caveat under the misfire block.

### 1.1 Full table

Margin is expressed as the fraction of the PCM's own pass band still unused. For counters
whose "maximum" is only the numeric range of the PID (65535) rather than a limit, margin
is meaningless and is marked n/a.

| Monitor | MID | TID | What it is | Value | Pass band | Position in band | Verdict |
|---|---|---|---|---|---|---|---|
| **Misfire, cylinder 1** | $A2 | $0C | misfire counts, current/last driving cycle | **0** | 0–65535 (range) | n/a | PASSED |
| Misfire, cylinder 2 | $A3 | $0C | same | **0** | 0–65535 | n/a | PASSED |
| Misfire, cylinder 3 | $A4 | $0C | same | **0** | 0–65535 | n/a | PASSED |
| **Misfire, cylinder 4** | $A5 | $0C | same | **2** | 0–65535 | n/a | PASSED |
| Misfire, cylinder 5 | $A6 | $0C | same | **0** | 0–65535 | n/a | PASSED |
| **Misfire, cylinder 6** | $A7 | $0C | same | **1** | 0–65535 | n/a | PASSED |
| Misfire cyl 1–6 | $A2–$A7 | $0B | EWMA misfire counts, last ten driving cycles | **0** on all six | 0–65535 | n/a | PASSED |
| Misfire cyl 1–6 | $A2–$A7 | $80 | that cylinder's misfire rate vs the **catalyst-damage** rate | **0 %** on all six | 0–**30.976274 %** | 0 % of band | PASSED |
| Misfire cyl 1–6 | $A2–$A7 | $81 | that cylinder's misfire rate vs the **emission-threshold** rate | **0 %** on all six | 0–**0.949172 %** | 0 % of band | PASSED |
| Misfire general | $A1 | $80 | **total engine** misfire rate vs catalyst-damage rate | **0 %** | 0–30.976274 % | 0 % | PASSED |
| Misfire general | $A1 | $81 | **total engine** misfire rate vs emission-threshold rate | **0 %** | 0–0.949172 % | 0 % | PASSED |
| **Misfire general** | **$A1** | **$84** | **inferred catalyst mid-bed temperature** — see §1.4 | **527.198** | 0–**918.874** | **57.4 % of band** | PASSED |
| **Catalyst, bank 1** | $21 | $81 | oxygen-storage index | **0.371089** | 0–**0.835927** | **44.4 %** | PASSED, **55.6 % margin** |
| **Catalyst, bank 2** | $22 | $81 | oxygen-storage index | **0.363277** | 0–0.835927 | **43.5 %** | PASSED, **56.5 % margin** |
| **O2 bank 1 sensor 1 (upstream)** | $01 | $87 | response time | **0.014 s** | 0–**0.4 s** | **3.5 %** | PASSED, **96.5 % margin** |
| O2 bank 1 sensor 1 | $01 | $88 | second response-time test | **0.006 s** | 0–0.4 s | 1.5 % | PASSED |
| **O2 bank 2 sensor 1 (upstream)** | $05 | $87 | response time | **0.014 s** | 0–0.4 s | **3.5 %** | PASSED, identical to bank 1 |
| **O2 bank 2 sensor 1** | **$05** | **$88** | second response-time test | **0.008 s** | 0–0.4 s | 2.0 % | PASSED — **missing from `data/mode06.csv`**, present in OCR `m253-15` |
| O2 bank 1 sensor 2 (downstream) | $02 | $85 | max negative voltage slope | **−3846 mV/s** | −30000 – 0 | 12.8 % from the zero end | PASSED |
| O2 bank 2 sensor 2 (downstream) | $06 | $85 | max negative voltage slope | **−3788 mV/s** | −30000 – 0 | 12.6 % from the zero end | PASSED |
| O2 bank 1 sensor 2 | $02 | $86 | response time | **0.792 s** | 0–**10 s** | **7.9 %** | PASSED |
| O2 bank 2 sensor 2 | $06 | $86 | response time | **0.856 s** | 0–10 s | **8.6 %** | PASSED |
| O2 heater bank 1 sensor 1 | $41 | $81 | heater current | **2550 mA** | **1120–3800 mA** | **53.4 %** (mid-band) | PASSED |
| O2 heater bank 2 sensor 1 | $45 | $81 | heater current | **2455 mA** | 1120–3800 mA | **49.8 %** (mid-band) | PASSED |
| O2 heater bank 1 sensor 2 | $42 | $81 | heater current | **637 mA** | **220–3000 mA** | **15.0 %** | PASSED, 2.9× the lower limit |
| O2 heater bank 2 sensor 2 | $46 | $81 | heater current | **652 mA** | 220–3000 mA | **15.5 %** | PASSED, 2.9× the lower limit |
| **VVT bank 1** | $35 | $85 | phaser position error | **0.06 °** | 0–**20 °** | **0.30 %** | PASSED, **99.7 % margin** |
| **VVT bank 2** | $36 | $85 | phaser position error | **0.05 °** | 0–20 ° | **0.25 %** | PASSED, **99.75 % margin** |
| VVT bank 1 | $35 | $82 | — | 0 ° | 0–20 ° | 0 % | PASSED |
| VVT bank 1 | $35 | $83 | — | 0 ° | 0–26.45 ° | 0 % | PASSED |
| VVT bank 1 | $35 | $84 | — | 0 ° | 0–22.36 ° | 0 % | PASSED |
| VVT bank 2 | $36 | $82 | — | 0 ° | 0–20 ° | 0 % | PASSED |
| **VVT bank 2** | **$36** | **$83** | — | **0 °** | 0–26.45 ° | 0 % | PASSED — **missing from `data/mode06.csv`**, present in OCR `m253-13` |
| VVT bank 2 | $36 | $84 | — | 0 ° | 0–22.36 ° | 0 % | PASSED |
| **Fuel system, bank 1** | $81 | $80 | — | **0** | 0–**0.796865** | **0 %** | PASSED, full margin |
| **Fuel system, bank 2** | $82 | $80 | — | **0** | 0–0.796865 | **0 %** | PASSED, full margin |
| EVAP monitor 0.040" | $3B | $80 | — | 0 Pa | **0–0 Pa** | — | **empty, not a pass** — see §1.5 |
| EVAP monitor 0.090" | $3A | $80/$81/$82 | — | 0 Pa | 0–0 Pa | — | **empty, not a pass** |
| Purge flow monitor | $3D | $80/$81/$82 | — | 0 Pa, 0 Pa/s | 0–0 Pa | — | **empty, not a pass** |

**Nothing is close to its limit.** Ranked by closest approach to any failing edge of its
band, the three tightest rows in the whole set are:

1. **Downstream O2 slope, MID $02 / $06 TID $85 — 12.6 % and 12.8 % of the band from the
   zero end.** Zero is the failing end here (a dead sensor has no slope); −3846 and
   −3788 mV/s are healthy slopes, and the two banks match within 1.5 %. The band itself
   (−30000 to 0) is so wide that this test barely constrains anything.
2. **Downstream O2 heater current — 15.0 % and 15.5 % of the 220–3000 mA band.** 637 and
   652 mA sit at nearly **three times** the lower failure limit and match each other
   within 2.4 %.
3. **Catalyst monitor — 44 % of its band, i.e. 55.6 % and 56.5 % margin**, with the two
   banks agreeing within 2.1 % of each other.

Everything else in the table sits at 90 % margin or better, and most of it reads exactly
zero. **There is no row in this set that a technician should look at twice.**

### 1.2 What $80 and $81 actually mean — this was never stated in the project record

`[COMMUNITY]` Ford's Mode $06 misfire structure uses two thresholds, and both appear
against every cylinder:

- **TID $80 — the catalyst-damage misfire rate**, updated every 200 revolutions. The
  PCM's current threshold here is **30.976274 %**. A misfire rate that high melts a
  converter, which is why the number is enormous.
- **TID $81 — the emission-threshold (FTP) misfire rate**, updated every 1000
  revolutions. Threshold **0.949172 %** — roughly one miss in a hundred, which is the
  federal emissions criterion.

Every one of the twelve per-cylinder entries and both general entries read **0.000 %**.
So the engine's measured misfire rate is zero at both the emissions criterion and the
catalyst criterion, on every cylinder.

### 1.3 The misfire counts, honestly weighted

Raw counts this driving cycle: **cyl 1 = 0 · cyl 2 = 0 · cyl 3 = 0 · cyl 4 = 2 ·
cyl 5 = 0 · cyl 6 = 1.** Cylinders 4 and 6 are both on **bank 2 (driver side)**, which
is worth recording only because the record has repeatedly raised and dropped bank-2
suspicions; three counts is not a bank signature.

The project record leans on "the ten-cycle EWMA is ZERO on all six" as strong evidence.
**That claim is much weaker than it reads.** The PCM reported **zero warm-ups since codes
cleared** at the time of the read `[LOG]`. A ten-driving-cycle exponentially weighted
average that has seen one driving cycle is an average of one sample, and an EWMA
initialised at zero and updated once with a count of 2 rounds to zero anyway. **The
EWMA row carries almost no information here.** What does carry information is TID $80
and $81 reading 0.000 % — those are rates over 200 and 1000 revolutions and they are
genuinely zero.

The record's explanation for the 2 and 1 — that the WOT pulls hit the 6832 rpm rev
limiter, which cuts fuel and spark and can be logged as misfire — is supported by the
logs: **`Engine RPM` peaks at exactly 6832 rpm** in `20260905_034051.csv.gz` `[LOG]`.
It remains an explanation, not a proof.

**Standing conclusion:** the single-weak-cylinder hypothesis is not supported, but the
strength of that elimination should be stated as "no cylinder exceeded 0.0 % misfire
rate over one 55 km driving cycle", not as "ten clean driving cycles".

### 1.4 The unidentified value — MID $A1 TID $84 = 527.198 — IDENTIFIED

`[COMMUNITY]` Two independent web searches return the same definition: on Ford's Mode $06
misfire monitor block, **MID $A1 TID $84 is the inferred catalyst mid-bed temperature, in
degrees Celsius** — a value the PCM calculates rather than measures, used to decide
whether a given misfire rate is catalyst-damaging. Companion TIDs in the same block are
$80 (catalyst-damage rate, 200 revs), $81 (emission-threshold rate, 1000 revs), $82
(highest catalyst-damage misfire and its threshold) and $83 (highest emission-threshold
misfire and its threshold).

Searched: *"Ford Mode 06 Misfire Monitor General Data MID$A1 TID $84 meaning"* and
*"$A1 misfire monitor $84 catalyst mid-bed temperature mode 06 Ford TID"*. Sources found
include Fender Bender's *Ford Mode $06 Misfire Tests*, aa1car's *OBD II Mode $06
Diagnostics*, MOTOR's *Diagnosing Ford Misfires* and a Ford service-content OBD SM PDF.
**None of those pages could be opened from this container — the network egress proxy
blocked aa1car.com, fenderbender.com, crownvic.net, ford-trucks.com, engine-codes.com
and static.nhtsa.gov.** The identification therefore rests on two search summaries that
agree, not on a page this analysis read. Mark it `[COMMUNITY]`, not `[FORD]`.

**But it can be checked inside this dataset, and it checks out.** The Mode 06 screen was
photographed at **04:36:02**. The datalog `20260905_041723.csv.gz` sampled
`Catalyst temperature Bank 1 Sensor 1` at **543.5 °C at 04:19:56** and **477.9 °C at
04:44:51**, falling smoothly `[LOG]`. Linear interpolation to 04:36 gives **≈ 501 °C** at
the upstream sensor location. The Mode 06 value is **527.2 °C** — 5 % higher, and hotter
than the upstream location is exactly what a **mid-bed** temperature should be, because
the exotherm happens inside the brick.

**Verdict: 527.198 is a catalyst mid-bed temperature in °C, it is normal for a warm idle,
and the 918.874 maximum is the catalyst overtemperature ceiling.** It is not a fault
indicator and it is not a diagnostic lead. The `[VERIFY]` flag on this value in
`CLAUDE.md` can be closed to `[COMMUNITY] + corroborated in-dataset`.

### 1.5 Three Mode 06 blocks that are empty, not passing

`EVAP Monitor (0.040")` MID $3B, `EVAP Monitor (0.090")` MID $3A and `Purge Flow Monitor`
MID $3D all report **value 0, minimum 0, maximum 0**. A test whose own pass band is zero
width has not run. This is consistent with the readiness block, which still shows
**Evaporative System: Not completed** at 04:37 `[SHOT]` `m253-03`. The scan app renders
them "PASSED"; they are blanks. **Do not cite them as evidence about the EVAP system.**

### 1.6 Two rows missing from `data/mode06.csv`

Both are visible in the OCR of the screenshots and both pass:

1. **Oxygen Sensor Monitor Bank 2 – Sensor 1, MID $05 TID $88 = 0.008 s** (band 0–0.4 s) —
   OCR `m253-15`. Its bank 1 counterpart (MID $01 TID $88 = 0.006 s) *is* in the CSV, so
   the dataset currently supports a bank-1-only claim on a test where both banks were read.
2. **VVT Monitor Bank 2, MID $36 TID $83 = 0 °** (band 0–26.45 °) — OCR `m253-13`. Its
   bank 1 counterpart (MID $35 TID $83) *is* in the CSV.

Neither changes a conclusion. Both should be added so the two banks are symmetric in the
dataset as they are in the vehicle.

### 1.7 What Mode 06 does *not* cover

The 3.7 Ti-VCT has **four** phasers — intake and exhaust on each bank. Mode 06 exposes
**two** VVT monitor IDs, one per bank. Whatever TIDs $82–$85 separate, the data does not
give per-camshaft resolution, so "the phasers are perfect" is properly "each bank's VVT
monitor reports essentially zero error". `[SPEC]` that TIDs $82/$83 vs $84/$85 split
intake from exhaust is a guess and is not supported by anything here.

---

## 2. Diagnostic trouble codes and readiness monitors

### 2.1 The codes, verified from the source image

The complete multi-module scan is one screenshot, `m101-01_dtc.jpg`, EXIF **2026-09-04
22:26:11**, phone clock 10:26 PM. Its OCR reads in full:

| Module | Code | Ford text on screen | Status line |
|---|---|---|---|
| OBD-II | **U0422(00)** | "Invalid data received – body control module" | Archive (inactive) · **Confirmed, Test failed since last DTC clear** |
| Engine control unit | **U0422(00)** | same | Archive (inactive) · Confirmed, Test failed since last DTC clear |
| OCS (occupant classification) | **U0140(00)** | "Data bus, body control module (BCM) – no communication" | Archive (inactive) · Confirmed |
| RCM (restraints control) | **B11D8(14)** | "RESTRAINTS EVENT NOTIFICATION" | Archive (inactive) · Confirmed |

The owner confirmed the list was not truncated — *"That is everything"* — and that the
airbag lamp is not lit — *"No light, cluster normal"* `[OWNER]`.

**Zero P-codes of any kind.** That is the claim the diagnosis rests on and it is correctly
recorded. Note it is U0422 that carries the sub-code `(00)`, and it appears **twice**
because two modules each stored their own copy.

### 2.2 What each code means

- **U0422 — "Invalid data received from Body Control Module."** `[SAE]` A U0xxx code is a
  network/communication code. "Invalid data" means the message arrived but its content
  failed a plausibility or checksum test. Two modules logged it independently, which is
  what a single bus disturbance looks like.
- **U0140 — "Lost communication with Body Control Module."** `[SAE]` The OCS stopped
  hearing the BCM entirely. U0140 and U0422 on the same night are the same event seen at
  two severities.
- **B11D8:14 — "Restraint Event Notification"**, set by the RCM. `[COMMUNITY]` Web search
  returns "B11D8:14 — Restraint Event Notification: circuit short to ground or open",
  with the fault set when the RCM sees a short to ground or an open on the event
  notification signal circuit for more than 15 seconds. **This could not be verified at
  source** — engine-codes.com, autocodes.com and the MHH thread were all blocked by the
  egress proxy, and no Ford workshop-manual page was reachable. Grade it `[COMMUNITY]`.
  - `[SAE]` The `:14` suffix is a standard **failure type byte** from SAE J2012 / ISO
    15031-6, not a Ford-specific number. In that scheme the 0x1x family is circuit
    faults — 0x11 short to ground, 0x12 short to battery, 0x13 open — and **0x14 is the
    combined "circuit short to ground **or** open"** used where the module cannot
    distinguish the two. Search did **not** return a page confirming 0x14 specifically
    (the SAE J2012DA digital annex is paywalled), so this is the standard convention
    rather than a quoted definition.
  - The "event notification" circuit is how the restraints module tells other modules a
    crash has occurred (fuel pump shutoff, door unlock, horn). **A short-or-open on that
    circuit is exactly what a battery disconnect looks like to the RCM.**

**Reading, unchanged and correct:** three modules complaining about the BCM, all inactive,
all consistent with a **voltage event**, on a truck whose battery has been disconnected at
least twice. U0422's status line — *"Test failed since last DTC clear"* — dates it after
the previous clear. No airbag lamp, so the restraint entry is historical.

**None of these can explain the vibration.** They are body-network and restraint codes,
they are archived, and the vibration predates every battery disconnect by years.

### 2.3 What the codes were worth — the counter nobody quoted

At the moment of that DTC read the PCM also reported `[LOG]`, at 22:26–22:34 in
`2026-09-04 22-23-38.zip`:

| Counter | Value |
|---|---|
| Distance since codes cleared | **101 km** |
| Warm-ups since codes cleared | **3** |
| MIL | **OFF**, DTC count **0** |

**"Zero powertrain codes" therefore covers 101 km and three warm-ups, not twelve years.**
The long-horizon evidence is the owner's report that the malfunction indicator lamp has
*never* illuminated — a lamp observation, not a code read. That distinction is already
noted in `CLAUDE.md` and it is the right one; the 101 km number puts a size on it.

### 2.4 Readiness monitors — full state, both times, from the screenshots

**Before the drive** — `m182-10`, 2026-09-04 22:31, 101 km / 3 warm-ups since clear:

| Monitor | Available? | Since DTC clear |
|---|---|---|
| Misfire | Available | **Completed** |
| Fuel System | Available | **Not completed** |
| Components | Available | **Completed** |
| Catalyst | Available | **Not completed** |
| Heated Catalyst | Not available | Completed |
| Evaporative System | Available | **Not completed** |
| Secondary Air System | Not available | Completed |
| A/C refrigerant | Not available | Completed |
| Oxygen Sensor | Available | **Not completed** |
| Oxygen Sensor Heater | Available | **Not completed** |
| EGR system | Available | **Completed** |

**After the drive** — `m253-01/02/03`, 2026-09-05 04:37, after the KAM wipe **and** the
relearning drive:

> **Everything Completed except Evaporative System: Not completed.**
> (Current-drive-cycle block additionally shows `Components: Not completed`.)

**What this is worth.** Five emissions monitors had not run when the "no codes" finding was
first recorded — including the two that matter most to this investigation, **Catalyst** and
**Oxygen Sensor**. The Mode 06 read at 04:36 is only meaningful *because* the drive
completed them; the earlier attempt at Mode 06 was correctly cancelled for exactly this
reason `[SHOT]` `P3E-001`.

The one still-incomplete monitor, **Evaporative System**, needs fuel level in a window and
a cold soak. It tests the fuel tank and canister for vapour leaks **downstream of a closed
purge valve** — it cannot affect how the engine idles. It is the reason the three EVAP and
purge-flow Mode 06 blocks are empty (§1.5).

**"Heated Catalyst", "Secondary Air System" and "A/C refrigerant" read `Not available`** —
this engine does not have those systems. Their "Completed" is a formality.

### 2.5 A correction: permanent codes are still readable

The elimination record (`E-098`) states that Mode $0A permanent DTCs were "erased by the
KAM wipe performed with the purge valve". **That is wrong.** `[COMMUNITY, strongly
sourced]` Permanent DTCs are stored in non-volatile RAM specifically so that they
**cannot** be cleared by a scan tool, a KAM reset, or removing battery power — the whole
point of the mode is to stop a vehicle passing inspection after a battery disconnect. They
clear only when the PCM's own monitor passes over several drive cycles.

**Consequence: Mode $0A can still be read today, and it is the only code history that
survived both battery disconnects.** It moves from "destroyed" to "outstanding and free".

---

## 3. Repair and maintenance history — the complete timeline

Dates before 2026-09-02 are unknown; the owner gave outcomes, not dates. Ordering within
the "before the investigation" block is not established.

### 3.1 Before the investigation

| # | Work | When | What changed | What it eliminates | What it does **not** eliminate |
|---|---|---|---|---|---|
| 0 | **Truck acquired — vibration already present.** *"Like this since I got it."* | unknown | — | **Nothing fitted or done since can be the original cause.** This is the single most load-bearing fact in the history. | — |
| 1 | **Spark plugs replaced** | unknown | *"Replacing spark plugs never changed the shake behavior"* | Worn plugs as the cause | **Brand, part number and gap were never stated.** A wrong gap installed at this job is *not* excluded — the owner answered a different question |
| 2 | **Air filter replaced** | unknown | no change | A blocked filter | — |
| 3 | **Oil and filter changed** | unknown | no change | Oil-related rough idle | Viscosity is **not established** — owner said *"5W-30 or similar"* against a 5W-20 spec |
| 4 | **Coolant flush** | unknown | no change | — | — |
| 5 | **6R80 transmission fluid** | at 113,000 km | no change to the idle symptom | Fluid-related converter shudder | Pan drop vs full exchange unknown |
| 6 | **Throttle body removed from the manifold and hand-cleaned** | unknown | *"No change whatsoever"* | Throttle body carbon, on a properly conducted test | **The idle relearn was not confirmed** — owner: *"I don't know, they said drive it 250 km and it will relearn"* |
| 7 | **Injectors removed, cleaned and flow-tested; intake manifold came off** | unknown | *"Exactly the same as before"* | Injector flow and spray pattern; **and** the manifold face, since the joint was disturbed and refitted with zero change | Whether an O-ring or gasket disturbed at this job leaks *now* |
| 8 | **O2 sensors "cleaned"** | unknown | no change | — | **Method unknown** — *"Don't know what they did."* Later closed by measurement instead (§3.3) |
| 9 | **Rear differential lubricant** | *"changed at some point"* | — | Nothing relevant | Date and distance unknown |
| 10 | **Battery disconnected; idle relearn done; ~300 km driven** | before 2026-09 | **no change to the symptom** | **The "young adaptives" hypothesis** — a reset plus a full relearn had already been tried and failed | Battery age unknown; this wipe is what put U0422 / U0140 / B11D8 in the archive |

**No dealer service record exists for roughly the last 76,500 km.** Everything above is
owner-reported.

### 3.2 The investigation itself

| Date / time | Event | Effect |
|---|---|---|
| 2026-09-02 | Diagnostic conversation opens. **No scan tool had ever been connected** to this truck. | Everything before this point is reasoning from owner reports |
| 2026-09-04 22:24 | **First datalog starts** (3 h 11 m, 35 MB, Park idle throughout) | The only continuous record of the pre-repair engine |
| 2026-09-04 22:26 | **Complete multi-module DTC scan** photographed | Four inactive body/network codes, zero P-codes |
| 2026-09-04 22:26–22:33 | **First full live-data value read** (~11 screenshots) | First fuel trims, lambda, purge, ethanol, MAF, voltages |
| 2026-09-04 ~22:59–23:09 | **The idle amplitude halves and stays halved** — not noticed at the time | See §4.6 |
| 2026-09-05 01:14–01:17 and 01:27–01:29 | **The two 2000 rpm load tests** | The load-cell trim finding |
| 2026-09-05 01:35 → 03:09 | **EVAP purge valve replaced AND battery negative disconnected and bridged (full KAM wipe) — in one operation** | Two variables changed together. Erased learned trims, the load-cell slope, the archived DTCs, the monitors, freeze frame and Mode 06 |
| 2026-09-05 03:09–03:30 | First post-repair data; **shake gone in D and R, still in P and N** | First symptom change in the owner's entire ownership |
| 2026-09-05 03:46–04:06 | **The relearning drive** — cruise, deceleration fuel-cut coasts on both banks, WOT to 6832 rpm | Relearned adaptives, ran the catalyst and O2 monitors, refilled Mode 06 |
| 2026-09-05 04:28–04:31 | **Idle long term trim −0.78 % both banks** | The leak is closed |
| 2026-09-05 04:36–04:37 | **Mode 06 read** | Every test passes |
| after ~100 km | **The D/R improvement relapsed** | Attributed to the reset, not the valve |

### 3.3 Repair 11 — the purge valve, and what it actually proved

| Condition | Before | Immediately after valve + KAM wipe | After ~100 km |
|---|---|---|---|
| P / N standstill | worst | **still present** | still present |
| D / R standstill | less | **gone** | **shakes again** |
| Driving | absent | absent | absent |

**Proved:** the valve was a real fault. Learned idle long term trim went **+3.13 / +2.34 %
before → −0.78 / −0.78 % after a full relearn**, both banks identical, and the load-cell
slope disappeared `[LOG, verified — see §4.3]`. The unmetered-air family is genuinely
closed.

**Did not prove:** that the valve caused the symptom. The improvement relapsed as the
adaptives re-learned, which is what the record itself predicted would happen if the
improvement came from the reset rather than the part.

**The methodological cost was high.** Two variables were changed in one operation, and the
wipe destroyed the archived DTCs, the freeze frame, the monitor state, the learned load-cell
slope and the entire Mode 06 history — the last of which is why the ten-cycle misfire EWMA
now carries no information (§1.3). The record has already adopted the rule
*"never wipe KAM before a measurement unless the wipe is the experiment"*; the size of
what was lost justifies it.

### 3.4 Hedges recorded as facts — the audit

`CLAUDE.md` already carries a table of these. Checking the owner's literal answers against
the record turns up the same seven and **three more**:

| Recorded as | What was actually said or measured | Status |
|---|---|---|
| "currently 5W-30" | *"5W-30 or similar"* | already flagged |
| Spark plugs replaced (implying correct plugs, correct gap) | *"Replacing spark plugs never changed the chake behavior"* — a different question | already flagged |
| "a legitimate drive-cycle relearn followed the throttle body clean" | *"I don't know they said drive it 250km and it will relearn"* | already flagged |
| Serpentine belt, tensioner, idler eliminated | *"Don't know"* — never inspected | already flagged |
| Battery age known | *"Don't know"* | already flagged |
| Rear diff lubricant serviced | *"Changed at some point"* | already flagged |
| O2 sensors cleaned (method) | *"Don't know what they did"* | already flagged — later closed by measurement |
| **"A/C off (`A/C pressure` reads 0 all session)"** | **`A/C pressure` reads exactly 0.0 in all 52 samples across all four logs, in six short clusters. It is a constant, not a measurement — a charged system that the owner says *"cools properly"* cannot read 0 kPa at 37 °C ambient even with the compressor off.** | **NEW — the channel is dead, so it is not evidence of A/C state either way** |
| **"A/C on roughly doubles the amplitude (64–81 rpm vs 30–53)"** | **Not supported by the log. The claimed A/C-on and A/C-off sessions both sit inside the high-amplitude era; the amplitude step is at 22:59–23:09 and is not aligned to either.** | **NEW — see §4.6** |
| **"the ten-cycle misfire EWMA is ZERO on all six"** | **True, but the PCM reports zero warm-ups since the clear. One driving cycle had elapsed.** | **NEW — §1.3** |
| **"permanent codes were erased by the KAM wipe"** | **Permanent DTCs live in NVRAM and survive both a clear and a battery disconnect.** | **NEW — §2.5** |
| "Gear (AT) reads 1 — was the truck in Park?" (never answered) | `Gear (AT)` reads **1.000 in every one of the 45 samples across three logs**, including while stationary in Park at 03:09 and 04:28. It is a constant. | resolved: the channel says nothing |

---

## 4. Screenshot claims checked against the raw logs

The four datalogs and the screenshot EXIF timestamps share a clock, so most screenshot
sessions can be located in the logs to the second. **21 of the 25 headline claims that
could be checked, agree — several of them to the third decimal.** The disagreements are
listed with the agreements so the ratio is visible.

### 4.1 Method note that matters — screenshot EXIF is not always the data time

For live captures, the EXIF time and the data time coincide. For the two 2000 rpm load
tests they do **not**: the throttle was held from **01:14:54 to 01:17:23** and from
**01:26:51 to 01:28:57**, but the screenshots are stamped **01:18:14–01:20:57** and
**01:30:18–01:32:39**. The owner photographed the graph *after* the event, scrolling back
through it. An analysis that aligns screenshots to logs on EXIF alone will conclude the
2000 rpm test never happened. It did.

### 4.2 Agreements — exact

| Claim `[SHOT]` | Log `[LOG]` | Window |
|---|---|---|
| Throttle blip to **22.68 °** | `Throttle Position Actually` max **22.681 °** | 23:17–23:19 |
| Timing driven to **6 °** at rpm 723, and to **15 °** at rpm 614 | Timing min **6.000**, max **15.000**; rpm min **613**, max **724** | 23:22–23:23 |
| Commanded throttle flat at **1.57 %**, later one LSB to **1.18 %** | min **1.176**, max **1.569** | 23:47–23:49 |
| Purge stepping **40.78 → 40.39 → 40.30 → 40.00 %** | min **40.000**, max **40.784** | 23:09–23:11 |
| Cam actual advance **0.00 to −0.06 °** | min **−0.062**, max **0.000** | 23:34–23:35 |
| ECU voltage min **12.39** max **12.82** avg **12.62** | min **12.415** mean **12.652** max **12.822** | 23:59–00:00 |
| Downstream O2 bank 1 **0.17–0.82 V**, avg **0.58–0.63** | min **0.170** mean **0.613** max **0.815** | 00:11–00:13 |
| Long term trim **+3.13 / +2.34 %** learned | **3.125 / 2.344**, min = mean = max | 00:48–01:25 |
| Long term trim B2 flat **2.34** while STFT B1 walks negative | **2.344** exactly, 880 samples, zero variance | 01:12–01:13 |
| **2 min 28 s** hold at 0 % on bank 2 | **01:14:54 → 01:17:23 = 2 min 29 s** | test 1 |
| **2 min 7 s** hold on both banks | **01:26:51 → 01:28:57 = 2 min 6 s** | test 2 |
| "returned to *exactly* 2.34 instantly" | 0 → 0.781 → 1.562 → 2.344 → 3.125 inside **0.3 s** | 01:28:57 |
| "bank 1 kept flicking to 0.78 and back, bank 2 less often" | B1 alternates ~40 times in the hold; B2 spends 24 s at 0.781 vs 101 s at 0.000 | 01:26–01:28 |
| Post-repair Park STFT **−1.5 to −2.0 / −0.8 to −1.8 %**, LTFT 0 flat | mean **−1.78 / −1.25**, LTFT **0.000** flat | 03:11–03:12 |
| Drive STFT **+0.3 / +0.4 %** | mean **+0.239 / +0.460** | 03:17–03:19 |
| Drive: one transient to **584 rpm**, timing pulled **13 → 8.5 °** | rpm max **584**, timing min **8.5** | 03:23–03:24 |
| Fuel cut bank 2 sweeps to **12.33** and pegs **29.38** | min **12.327**, max **29.383** | 03:57–03:59 |
| WOT `Abs. load` **96.47 %**, MAF **215.27 g/s**, rpm **6832** | **96.471 %**, **215.270 g/s**, **6832** | 03:46–04:06 |
| Idle LTFT **−0.78 % both banks**, min = avg = max | **−0.781** both, zero variance, 1082 + 1115 samples | 04:28–04:31 |
| Commanded AFR square wave **14.42 ↔ 14.86** | min **14.414**, max **14.858** | 04:49–04:54 |
| `Throttle Position Actually` stepping **9.44 / 9.55 / 9.88 / 10.33 °** | min **9.436**, max **10.327** | 04:49–04:54 |
| Ethanol **16.08 %**, baro **97 kPa**, right front tyre **211.7 kPa**, odometer **131313 km**, learned octane **−0.6**, catalyst temps **458.9 / 458.9 °C**, knock retard **0** | all reproduced exactly | 22:26–22:34 |
| Throttle desired **7.29 °** vs actual **7.56 °** | desired 7.080–7.288, actual **7.556** flat | 22:26–22:34 |
| Park spans **44/55/53/50 rpm**, Drive **15/13/18 rpm** | Park 10 s spans 31–53 (median 41), Drive 12–20 (median 15) | 03:23–03:30 |

### 4.3 Agreements — with a small correction

| Claim | Log | Correction |
|---|---|---|
| STFT B1 "never outside −1.56 to +1.56 %" | min **−2.344 %** in the same window | one extra quantisation step; conclusion unaffected |
| MAF "~3.01 g/s, axis 2.97–3.08" | min **2.770**, mean **3.016**, max **3.080** | the axis clipped a low excursion |
| Downstream O2 bank 2 "minima 0.30–0.39 V" | min **0.205 V** | the log dips lower than the screenshots showed |
| Purge on the new valve "47.06–49.80 %" | **46.275–49.804 %** | trivially wider |
| Bank 2 STFT "about **+3.5 %**" | mean **+3.22 %** over 00:48–00:56, 802 samples | slightly overstated |

### 4.4 **Disagreement 1 — the bank 2 short-term trim offset is real, is smaller than claimed, and was never actually withdrawn correctly**

The record states the bank asymmetry is **dead**, on the grounds that the two *long term*
trims settled one quantisation step apart (+3.13 vs +2.34). That reasoning is sound for
long term trim. But short term trim tells a different story, and the log lets both banks
be compared **in the same minute**, which the screenshots never did:

| Window | STFT B1 | STFT B2 | delta B2−B1 | n (B1 / B2) |
|---|---|---|---|---|
| 22:52 | +0.009 | +0.000 | **−0.01** | 336 / 336 (identical timestamps, r = 0.95) |
| 23:00 | −1.027 | −1.714 | −0.69 | 678 / 36 |
| 23:32 | +0.526 | +0.459 | **−0.07** | 46 / 46 |
| **00:48** | +1.174 | +3.223 | **+2.05** | 155 / 802 |
| **00:50** | +1.089 | +3.266 | **+2.18** | 256 / 255 |
| **00:52** | +0.597 | +2.859 | **+2.26** | 258 / 258 |
| **00:54** | +0.558 | +2.676 | **+2.12** | 224 / 226 |
| **01:04** | +0.177 | +2.295 | **+2.12** | 366 / 238 |
| 03:11 (post-repair, pre-drive) | −1.695 | −1.253 | +0.44 | — |
| 03:18 (Drive) | +0.215 | +0.560 | +0.35 | — |
| **04:18 (post-drive)** | +0.170 | +2.163 | **+1.99** | 129 / 134 |

**Three things follow.**

1. **The two banks track each other exactly until about 23:35, then bank 2 sits ~2.1
   points richer-demanding than bank 1 and stays there.** At 00:50 both channels were
   polled equally often (256 vs 255 samples over two minutes) and still differed by 2.18
   points — this is not a sampling artefact.
2. **The screenshot-era figure of "+3.5 % on bank 2 against ~0 % on bank 1" overstated the
   gap**, because the two halves came from different moments. The honest simultaneous
   figure is **+2.0 to +2.3 points of short term trim**, or **+1.1 to +1.5 points of total
   correction** once the 0.78-point long-term difference the other way is netted off.
3. **It survived the repair.** It is back at **+1.99 points at 04:18**, after a new purge
   valve, a full KAM wipe and a 55 km relearning drive.

`[SPEC]` This is small — well inside the ±10 % that would ever set a code — and it is a
*fuelling* asymmetry, not a *combustion* one, since Mode 06 says both catalysts, all four
oxygen sensors and every cylinder's misfire rate are matched. It is recorded here because
the project declared this line closed and the log says it is not, not because it is
claimed to explain the vibration.

### 4.5 **Disagreement 2 — "A/C on roughly doubles the amplitude" is not supported**

The record's A/C table (A/C off: 37, 74, 38, 30, 53 rpm · A/C on: 64, 76, 64, 81, 75, 68)
underwrites the elimination `E-080`. Against the log, in five-minute bins of the median
10-second rpm span:

| Clock | mean rpm | median 10 s span |
|---|---|---|
| 22:39 | 653.3 | **68.0** |
| 22:44 (the "A/C ON" screenshots are here) | 653.7 | **73.0** |
| 22:49 | 654.2 | **72.0** |
| 22:54 | 653.0 | **70.0** |
| 22:59 | 653.2 | **54.0** |
| 23:04 | 651.9 | **37.5** |
| 23:09 | 651.1 | **26.0** |
| 23:14 → 00:44 | 651–652 | **33.5 – 41.5** |

The amplitude does not track an A/C state; it **steps down once, at 22:59–23:09**, and
stays down. Both the "A/C on" and "A/C off" screenshot sessions were taken in the
high-amplitude era. And `A/C pressure` is a dead channel (§3.4), so nothing in the data
records the A/C state at all.

**What survives:** the oscillation is present in both eras, so the compressor is not its
cause — `E-080`'s conclusion holds. **What does not survive:** the "doubles" figure and
any use of the A/C-on windows as a loaded-idle comparison.

**Also settled:** the record lists *"whether the A/C was running during the live-data
scan"* as **asked and unrecoverable**. It is recoverable in one respect and unanswerable
in another — the truck's own idle speed was **identical (652–654 rpm mean before and
after the step)**. `[COMMUNITY]` Ford PCMs normally raise commanded idle when the
compressor engages; if that holds for this calibration — **unverified for this VIN** —
then the constant idle speed says the compressor state did not change across the step.
That does not prove the A/C was off; it does mean no A/C-driven load difference is
visible anywhere in the data.

### 4.6 **Disagreement 3 — the coolant story behind the amplitude halving is wrong in shape**

`CLAUDE.md` describes ECT as sitting at **81–83 °C for forty minutes and then rising** to
91–98 °C, "the shape of a fan switching off". The logged `Engine coolant temperature`
`[LOG]`, which is sampled only in bursts when the value screen was open, is **not
monotonic**:

| Clock | ECT |
|---|---|
| 22:24 | **88–89 °C** |
| 22:31 | **93–95 °C** |
| 22:39 | **83 °C** |
| 22:50–22:54 | **82 °C** |
| 23:00–23:01 | **81–82 °C** |
| 23:09 | **90–91 °C** |
| 23:26 | **96–97 °C** |
| 23:32–23:34 | **92–101 °C** |
| 00:48–00:56 | **92–101 °C** |

Coolant **falls** from 93 °C to 81 °C over the first 37 minutes, then **rises** to 101 °C
and thereafter cycles between roughly 92 and 101 °C. That is a cooling-system duty cycle
with a wide hysteresis band, not a warm-up. **The amplitude halving at 22:59–23:09
coincides exactly with ECT leaving the 81–82 °C floor and climbing to 90–96 °C.**

`[SPEC]` If the cooling fan is the mechanism, the direction is the *opposite* of the
load-damping story the record proposes: high amplitude occurred while coolant was low
(cooling active), low amplitude after coolant rose (cooling backed off). Any fan-load
explanation has to account for that sign. Also `[VERIFY]` whether the 2014 F-150 3.7 uses
an electric fan or a viscous clutch fan — nothing in this repository establishes it, and
the two behave differently as loads.

**Independent of the mechanism, one thing is now firm:** the correlation work that put
ECT against amplitude rests on a channel sampled in **nine short bursts over three hours**,
with values that reverse direction inside the session. Treat r = −0.455 accordingly.

### 4.7 A minor cross-check worth keeping

`Catalyst temperature Bank 1 Sensor 1` and `Bank 2 Sensor 1` differ by up to **40.8 °C**
if compared sample-to-sample, which looks like a bank imbalance. Interpolated onto a common
2-second grid during the drive they differ by **−0.02 ± 0.14 °C** across a 686–853 °C
range. **The 40.8 °C was a sampling-offset artefact on a fast transient.** Two "measured"
temperatures that agree to 0.14 °C over a 167 °C excursion are both outputs of the same
PCM model, not two sensors. `E-087` ("bank imbalance in exhaust temperature — eliminated")
reaches the right verdict for the wrong reason: **the channel cannot detect a bank
imbalance at all.**

### 4.8 Two adaptive values that moved across the wipe

| | Before the wipe | After the wipe and drive |
|---|---|---|
| `Ethanol fuel percent` | **16.078 %** | **19.22 %** |
| `Learned octane` | **−0.6** | **+0.08** |

Both are inferred, learned values, and both reset and re-inferred to different numbers on
the same fuel from the same station. `[SPEC]` This weakens the "16.08 % ethanol on E0 pump
fuel is an anomaly" line — the inference is evidently loose enough to land 3 points apart
on two consecutive readings of the same tank.

---

## 5. The complete list of gaps — never measured, never inspected, or "don't know"

### 5.1 Never measured, on the vehicle

1. **Independent engine speed** — timing-light tach against the app, at idle and at 1500 rpm. The direct test of the crank-signal hypothesis. Never done.
2. **The vibration itself.** One phyphox spectrum was taken and is unusable: the axis spanned 0–210 Hz, so 5–33 Hz was compressed into the left edge, and rpm, phone placement, engine state and an engine-off noise floor were all unrecorded.
3. **Permanent DTCs (Mode $0A).** Requested repeatedly, never read — and, contrary to the record, **still readable** (§2.5).
4. **Freeze frame.** Never captured; the pre-wipe copy is gone.
5. **PCM calibration IDs.** Never read, so the "does a later calibration exist" question was never put to a Ford dealer. A reflash is a repair with no parts.
6. **AC ripple across the battery** (DMM, AC volts, < 0.1 V) — deferred by the owner, never done.
7. **Three ground voltage drops** (battery negative → block, block → chassis, battery negative → chassis, each < 0.1 V) — never done.
8. **Wiggle test** on the crank sensor connector and harness, then cam sensors, MAF, coils, with the rpm graph live — never done.
9. **Vacuum gauge on the manifold** at warm idle — never done. Not for leaks; for combustion character at a bandwidth OBD cannot reach.
10. **Cylinder balance by injector kill** (six rpm drops) — never done.
11. **Oil pressure at hot idle** against the phaser requirement — never done.
12. **Cold-start capture** of `Engine RPM` + `Fuel/Air com. ratio`. A cold engine runs open loop and the catalyst dither does not run at all, so this separates the dither from everything else. Never done — and it is free.
13. **Whether the needle breathing is present on a cold start.** The owner has confirmed the *shake* is identical cold and hot; nobody ever asked about the *needle*.
14. **A held-1500 rpm capture of any kind.** The owner's central complaint — *"the problem exists in a wide range of RPM"* — has never been instrumented. Every measurement in this project is idle plus two short 2000 rpm holds.
15. **The control sample.** No other 2011–2014 F-150 or Mustang 3.7 has ever been measured at warm idle in Park. Whether ±25 rpm is abnormal for this engine is still unknown.
16. **The rpm sweep follow-up.** The owner reported "worst idle at 650"; the follow-up — does it drop off sharply by 900 or taper and persist at 1200–1500 — was asked and never answered.
17. **Electrical load test at idle in Park** (all loads on) — specified, never done.
18. **Local barometric pressure** at the hour the PCM read 97 kPa — never checked, so the 4 %-low question is still open.
19. **A smoke test.** Justified twice and withdrawn twice; never performed.

### 5.2 Never inspected, physically

20. **PCV valve, hose, grommet and elbow** — never inspected, in twelve years. Withdrawn as a *leak* suspect on trim evidence, but that is not the same as having looked at it.
21. **Brake booster line and check valve** — never tested.
22. **Engine mounts** — never touched, never pried, never observed rocking through P→D→R→P.
23. **Harmonic balancer / crank pulley damper** — never inspected. Twelve years of Jeddah heat on the bonding rubber.
24. **Contact hunt** — exhaust, A/C line, power steering line, transmission cooler line, wiring looms, heat shields. Never done.
25. **Touch test** across the mount — engine, frame rail, cab floor. Never done.
26. **Serpentine belt, tensioner, idler pulleys** — *"Don't know."* Eliminated by reasoning, never seen.
27. **Coil boots and spark plug wells** — never inspected for carbon tracking or oil.
28. **Spark plug gap as installed** — never verified.
29. **Timing chain / tensioner extension** — never inspected.

### 5.3 Answered "don't know" or hedged

30. Battery age — *"Don't know."* The entire charging analysis sits on top of this gap.
31. What was done to the O2 sensors — *"Don't know what they did."* (Since closed by measurement, not by an answer.)
32. Whether an idle relearn was actually run after the throttle body clean — *"I don't know."*
33. Oil viscosity currently in the sump — *"5W-30 or similar."*
34. Spark plug brand, part number and gap — never stated.
35. Rear differential lubricant date and distance — *"changed at some point."*
36. 6R80 fluid: pan drop or full exchange — unknown.
37. Whether the A/C was running during the first live-data scan — *"Not sure"*, and the `A/C pressure` channel is dead, so it cannot be recovered from the data either.
38. Whether the truck was in Park during the 22:26–22:33 value read — asked, never answered; `Gear (AT)` is a constant and cannot answer it. (`Vehicle speed` was 0.)

### 5.4 Data-integrity gaps inside this repository

39. `data/mode06.csv` is missing **MID $05 TID $88** and **MID $36 TID $83** (§1.6).
40. Three Mode 06 blocks (EVAP ×2, purge flow) are recorded as "PASSED" when they are **empty results** (§1.5).
41. `A/C pressure` and `Gear (AT)` are constant-valued channels being treated as measurements (§3.4).
42. `data/readings.csv` records only four readiness monitors; the screenshots contain the **complete eleven-monitor block, twice** (§2.4).

---

## 6. Parts and systems still unproven because nobody looked — ranked

Ranked by *how much a null result would change the diagnosis*, not by likelihood.

| Rank | Item | Why it matters | Cost to close | Status |
|---|---|---|---|---|
| **1** | **Independent rpm measurement** | The crank-signal hypothesis is the only one that explains reset-helps-then-returns, and **every rpm number in this project is the PCM's own.** If the crank signal is lying, the entire dataset is measuring a phantom. | A timing light with a tach function. Ten minutes. | Never done |
| **2** | **The vibration's frequency** | The actual complaint has never been measured. ~10–11 Hz points at mount rock or imbalance; ~5.5 Hz at one cylinder; ~33 Hz at firing pulse and therefore isolation. These are different repairs. | Phone, phyphox, axis set to 0–50 Hz, plus an engine-off noise floor. | One unusable attempt |
| **3** | **A control sample on another 3.7** | The unanswered first question — *is this a fault at all?* Six repairs and four datalogs have not touched it. | Two minutes beside another truck. | Never done |
| **4** | **Engine mounts (hydraulic damping)** | `[COMMUNITY]` The 2012–2017 F-150 is catalogued with **hydraulic, fluid-filled** engine mounts (BL3Z-6038 family, suffixes by engine and drivetrain — search returned this from a parts guide; **no Ford source was reachable**). A fluid-filled mount that has lost its fluid stops damping the 8–15 Hz rock mode, is **not** direction-dependent, and is therefore invisible to the D-vs-R test that "eliminated" mounts. | Pry bar, a helper, ten minutes. | Never inspected. Reopened on paper, never looked at |
| **5** | **A contact point** — exhaust, A/C line, power steering line, cooler line, loom, heat shield | Explains strong-in-P, gone-in-D (the engine rotates slightly in gear and a resting contact breaks), felt not heard, invisible to every sensor, present since purchase, unaffected by every repair. | A hand along each line at idle. Free. | Never done |
| **6** | **Permanent DTCs (Mode $0A)** | The only code history that survived both battery disconnects. It is the one remaining piece of *long-horizon* evidence available, against a "no codes" finding that actually covers 101 km. | One scan-tool screen. | Never read — and **still readable** |
| **7** | **Harmonic balancer** | First-order (10.8 Hz at idle) sits inside the 8–15 Hz engine-rock band. Twelve years of Jeddah heat on bonded rubber. | Visual: check the outer ring's timing mark against the keyway. | Never inspected |
| **8** | **PCM calibration level** | A repair with no parts. Ford has issued idle-quality recalibrations for this engine family. | Read the calibration IDs, hand them and the VIN to a dealer. | Never read |
| **9** | **PCV valve, hose, grommet, elbow** | Withdrawn as a *leak* suspect on sound trim evidence — but a collapsed or rattling PCV is also a mechanical noise/vibration source, and that is a different failure mode from the one the trims excluded. | Pull it and shake it. Free. | Never inspected in twelve years |
| **10** | **Charging system ripple and ground drops** | An alternator diode injecting ripple onto the sensor reference would corrupt the crank signal — which loops straight back to rank 1. `Control module voltage` sits at **12.39–12.82 V with the engine running** in two separate sessions two hours apart `[LOG]`, explained as smart charging but never confirmed with a meter. | DMM, five minutes. | Deferred, never done |
| **11** | **Spark plug gap / coil boots** | The plugs were changed and the shake did not change — but the gap was never verified and the boots were never looked at. `[COMMUNITY]` Ford TSB 14-0160 is cited in the record for boots plus gap check on 2010–2016 F-150s. | Pull one coil. | Never done |
| **12** | **Timing chain and tensioner** | The 3.7's internal water pump is chain-driven, and chain wear shows as a phaser-authority problem at idle — where oil pressure is lowest. Mode 06 VVT error of 0.05–0.06 ° argues strongly against it. | Cover off. Expensive. | Correctly deprioritised |

### 6.1 One record item disposed of

`F-154` carries **NHTSA TSB MC-10184634-0001, "Vibration/Rough Idle In DRIVE Or REVERSE,
Lack Of…"** as an open question because the title matches the symptom. `[COMMUNITY]` Web
search returns its content: the bulletin covers **vibration/rough idle in DRIVE or REVERSE
plus lack of acceleration and shudder, caused by torque converter overheating**, and the
service action is **replacing the torque converter and damaged internal transmission
components**. The PDF itself could not be fetched (`static.nhtsa.gov` is blocked by the
egress proxy).

**It does not match this truck.** This truck's symptom is **worst in Park and Neutral**,
where the converter is unloaded, and is *least* bad in Drive and Reverse — the opposite of
the bulletin's pattern. The truck also pulls normally with no shudder. **Close `F-154`
unless the D/R symptom ever becomes the dominant one.**

---

## 7. Sources

- [Ford Mode $06 Misfire Tests — Fender Bender](https://www.fenderbender.com/running-a-shop/operations/article/33022601/ford-mode-06-misfire-tests) (search summary only — page blocked)
- [OBD II Mode $06 Diagnostics — aa1car](https://www.aa1car.com/library/2005/us010516.htm) (search summary only — page blocked)
- [Diagnosing Ford Misfires — MOTOR Information Systems](https://www.motor.com/magazine-summary/diagnosing-ford-misfires/)
- [Mode $06 Test ID $84 error — crownvic.net](https://www.crownvic.net/ubbthreads/ubbthreads.php?ubb=showflat&Number=4155958) (search summary only — page blocked)
- [Ford OBD System Operation Summary (fordservicecontent.com PDF)](https://www.fordservicecontent.com/Ford_Content/catalog/motorcraft/OBDSM2400OUTPUT_16Jul2024_WSM_final_V2_MCS7001.pdf)
- [B11D8 Ford Code — Restraint Event Notification, engine-codes.com](https://www.engine-codes.com/b11d8_ford.html) (search summary only — page blocked)
- [Code B11D8 Ford Restraint Event Notification — autocodes.com](https://www.autocodes.com/b11d8_ford.html)
- [2016 Ford F-150 Codes B11D8:14 & B11D8:01 — MHH Auto](https://mhhauto.com/Thread-2016-Ford-F-150-Codes-B11D8-14-B11D8-01)
- [What Is a Failure Type Byte (FTB)? — AutoDTCs](https://autodtcs.com/what-is-a-failure-type-byte-ftb/)
- [SAE J2012DA Digital Annex of DTC and Failure Type Byte Definitions](https://webstore.ansi.org/standards/sae/SAE2012DA2013J2012DA) (paywalled)
- [Ford: Permanent Diagnostic Trouble Codes — Underhood Service](https://www.underhoodservice.com/ford-permanent-diagnostic-trouble-codes-dtcs/)
- [$0A Permanent Diagnostic Trouble Code (PDTC) — RLEscalambre](https://www.rlescalambre.net/0a-permanent-diagnostic-trouble-code-pdtc)
- [Ford F-150/F-250: How to Reset Adaptive Memory — ford-trucks.com](https://www.ford-trucks.com/how-tos/a/ford-f150-f250-how-to-reset-adaptive-memory-359981)
- [A Guide to Replacing Engine Mounts on the 2012-2017 Ford F-150 — Go-Parts](https://www.go-parts.com/garage/ps-2012-2017-ford-f-150-engine-mount)
- [2011-2016 Ford F-150 Motor Mount BL3Z-6038-A — Tasca Parts](https://www.tascaparts.com/oem-parts/ford-motor-mount-driver-s-side-lh-bl3z6038a)
- [Vibration/Rough Idle In DRIVE Or REVERSE, Lack Of… — NHTSA MC-10184634-0001](https://static.nhtsa.gov/odi/tsbs/2020/MC-10184634-0001.pdf) (search summary only — page blocked)

**In-repository sources:** `data/mode06.csv` · `data/readings.csv` · `data/timeline.csv` ·
`data/sessions.csv` · `data/eliminations.csv` · `data/findings.csv` ·
`data/screenshots_manifest.csv` · `data/screenshots_ocr/m101-01_dtc.txt` ·
`data/screenshots_ocr/m182-07,-10_monitors.txt` · `data/screenshots_ocr/m253-01…16_mode06.txt` ·
`data/conversation/owner_answers.txt` · `data/analysis/night_events.csv` ·
`data/carscanner/2026-09-04 22-23-38.zip`, `20260905_030915.csv.gz`,
`20260905_034051.csv.gz`, `20260905_041723.csv.gz`.

### One more thing that is free and settles a lot

**Ford's crankshaft position variation correction — the "misfire monitor neutral profile
correction" — is learned during closed-throttle, non-braking, defuelled decelerations**
`[COMMUNITY]`. The relearning drive on 2026-09-05 contained exactly that: two deceleration
fuel-cut coasts from ~100 km/h. `[SPEC]` If a defective reluctor or crank signal is the
fault, then the KAM wipe cleared that correction and the coasts began re-learning it —
which would be a mechanism for *reset helps, returns after ~100 km*. **This is speculation
and it is testable:** read the crankshaft position variation learn status with FORScan or
IDS, and measure engine speed independently with a timing light. Neither has been done.
