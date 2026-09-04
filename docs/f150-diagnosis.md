# 2014 F-150 3.7L — Unstable Idle Diagnosis

Working log for VIN `1FTMF1EM1EFC80632`. Records what was checked, what it
ruled out, and what is still open.

**Status:** open — but the first open question is no longer *which fault*.
It is **whether there is a fault at all.** See
[Is this a fault?](#is-this-a-fault) before spending anything further.

---

## Vehicle identification

Decoded from the VIN and the door jamb label.

| Field | Value |
|---|---|
| VIN | `1FTMF1EM1EFC80632` |
| Model | Ford F-150 XL, Regular Cab, 8-ft box |
| Engine | 3.7L V6 Ti-VCT (Cyclone), ~302 hp |
| Transmission | 6R80 6-speed automatic |
| Drive | **4x2** — VIN position 5 (`F1E`) |
| Built | 08/2014 · in service 19 Nov 2014 |
| Odometer | 131,000 km (Aug 2026) |

Door label: GVWR 3016 kg (6650 lb) · FAWR 1497 kg · RAWR 1588 kg ·
P255/65R17 108H on 17x7.5J · **35 psi cold, front and rear** ·
WB 126" · axle code 26 · paint UJ Sterling Gray · interior CS Steel Gray.

### Errors in the vehicle history report

The purchased report contains two fields that contradict the VIN. Do not
act on them:

- Lists fuel type as **"Electric"** — it is gasoline.
- Lists drive as **"Four-wheel Drive"** — VIN says 4x2. Confirm visually
  (look for a front driveshaft and transfer case) before ordering any
  driveline part.

---

## History report findings

Source: Saudi vehicle history report #9016795, dated 2025-01-26.
32 dealer visits with Aljazirah Vehicles, 2015–2021.

### Odometer sequence is not monotonic

| Date | Reading |
|---|---|
| 2016-12-26 | 49,306 km |
| 2020-03-08 | **40,124 km** ← lower than 2016 |
| 2020-03-23 | 40,547 km |
| 2021-03-04 | 49,381 km |
| 2021-04-29 | 54,533 km |
| 2022-08-28 | 91,205 km |
| 2023-08-18 | 108,905 km |
| 2025-01-03 | 117,029 km |

The 2016 entry sits ~9,000 km above the 2020 readings. Either a data-entry
error in 2016, or a cluster was swapped or rolled back between 2016 and
2020. Note that 49,306 (2016) and 49,381 (2021) are suspiciously close,
which points toward a mis-keyed record — but it cannot be proven from the
report alone.

**Consequence: true accumulated distance may exceed 131,000 km. Treat all
wear-item intervals as "at least."**

### Service gap

Last dealer visit 2021-04-29 at 54,533 km. That leaves roughly **76,500 km
with no dealer service record.** Whatever was or wasn't done in that period
is unknown — relevant to cam phaser condition, which depends on oil history.

### Other notes

- 2020-02-26 visit logged as *فحص الماكينة لا تعمل* — engine inspection,
  no-start / not running.
- No accident history. Two owners. No recalls on file.
- Warranty expired 2017-11-19.
- Service life in Aseer, Jizan and Dammam — hot climate, so every
  maintenance interval should be treated as severe duty.

---

## Symptom — as actually characterised

A **small** vibration felt in the cab, with visible movement on the
tachometer. Refined description from the owner:

- It is **felt, not heard.** From under the hood a trained ear cannot tell
  the engine has a problem.
- The engine **does not lope, stumble, or feel close to stalling.**
- Idle rpm is normal, **650–750** warm in P, A/C off.
- **No change with A/C on.**
- **Identical cold and hot.**
- Present **since purchase** — the truck has never been smooth in this
  owner's hands.
- **No check engine light, ever**, and a complete multi-module scan shows
  **no powertrain code of any kind** — see *Codes read* below.

That description matters. A charge-dilution or vacuum-leak fault severe
enough to shake a cab produces an *audibly* uneven idle. This one does not.

---

## Codes read — 2026-09

First real scan data on this vehicle. Complete multi-module scan, generic
scan app, engine warm.

| Module | Code | Meaning | State |
|---|---|---|---|
| OBD-II + engine control unit | **U0422(00)** | Invalid data received — body control module | Archive (inactive). "Confirmed, test failed since last DTC clear" |
| OCS | **U0140(00)** | Data bus, body control module — no communication | Archive (inactive), confirmed |
| RCM | **B11D8(14)** | Restraints event notification | Archive (inactive), confirmed |

### What matters most is what is absent

**Not one P-code.** No misfire, no fuel trim, no VCT, no lean or rich code,
across a scan that covered every module. The PCM's own monitors have nothing
to say about how this engine runs.

That is a second independent line of evidence pointing where the load curve
already pointed: whatever is felt in the cab, the engine management system
does not consider it a fault.

### What the codes that are present mean

Three modules complaining about the **body control module** — invalid data
from it, no communication with it — plus a restraint entry, **and every one
of them inactive**. That is the signature of a **voltage event**, not four
independent faults. Modules drop off the bus when supply voltage sags and
each logs what it saw.

This truck had its battery disconnected. U0422 reports "test failed since
last DTC clear", so a clear happened and this logged after it. The timeline
fits.

**None of it explains the vibration.** These are body-network and restraint
codes, they are not currently active, and the vibration has been constant
since purchase — long before the battery was disconnected. An inactive code
cannot produce a continuously present symptom.

### The restraint entry, on its own account

`B11D8` in the RCM alongside an OCS module that lost communication is worth
separating from the idle question.

- **No airbag warning light** — confirmed by the owner. So this is
  historical, consistent with the voltage-event reading, and not an active
  restraint fault.
- The purchased history report claims **no accident history**. A restraints
  event entry does not contradict that on its own, since a voltage drop can
  log one — but that same report also got the fuel type and drivetrain wrong,
  so it is not strong evidence either way.

[VERIFY] Ford's exact definition of B11D8 and the meaning of the `(14)`
sub-code were not confirmed — the sources were unreachable from the
environment where this was written. Look both up before acting on them.

### Next step on codes

1. **Read permanent codes (Mode `0A`) before clearing anything.** They
   survive a clear and a battery disconnect, and they are the only code
   history that cannot be destroyed. Not yet read.
2. Then clear these four and drive normally for a week. What returns is real;
   what does not was the voltage event.

Clearing is normally refused in this project because it destroys freeze-frame
and misfire history. That objection does not apply here: there are no
powertrain codes, so there is nothing of diagnostic value to lose, and
return-after-clear is the only way to separate a live fault from a logged
past event.

---

## Is this a fault?

**Not established.** This must be settled before more money is spent.

### The case that it is normal

- The truck is a base **regular cab XL** — minimal sound deadening, cab
  mounted close to the engine, no acoustic glass.
- The 3.7 is a **60° V6**, which is not inherently balanced the way an
  inline-six or a cross-plane V8 is.
- Never smooth in the owner's entire ownership — a characteristic, not a
  change.
- No code in years, across every condition.
- Normal idle rpm; nothing stalls or nearly stalls.
- Perfect under load.
- **Six competent repairs, aimed at six different systems, every one of
  which changed nothing.** The simplest explanation for a fault that
  resists every repair is that there is no fault.

### The two tests that settle it — both free

1. **Control sample.** Find another 2014-ish F-150 regular cab with the 3.7.
   Hand on the fender at idle, then sit in the cab. Two minutes, and it
   answers what six repairs have not.
2. **Quantify the rpm movement.** Log the RPM PID for 60 s at warm idle in
   P — `src/obd_logger.py` already does this.

| RPM movement at steady warm idle | Reading |
|---|---|
| ±25–50 rpm, gentle wander | **Normal** closed-loop idle control. Every engine does this. |
| ±100 rpm or more, or a rhythmic hunt | **Real fault.** Work the ranked suspects below. |

---

## The load relationship — the key observation

Symptom strength tracks engine load, inversely:

| Condition | Manifold vacuum | Shake |
|---|---|---|
| P / N at standstill | Highest | **Worst** |
| D / R at standstill | Slightly lower | **Less** |
| Driving under load | Lowest | **Absent — pulls great, no vibration** |

**Rpm is not the variable; load is.** Across a no-load rpm sweep in Park the
symptom is roughly equal at all engine speeds. It is the arrival of *load*
that removes it.

If a fault exists, it is one whose effect scales with manifold vacuum and
vanishes when the throttle opens.

### Superseded reasoning — do not reuse

Earlier revisions of this document argued:

> In D/R the torque converter is coupled and loaded, and the fluid coupling
> damps torsional pulses... **The engine is genuinely running rough; the
> converter is masking it in gear.**

That was wrong on two counts:

1. **Every** torque-converter automatic is smoother in gear at a standstill.
   The observation was never evidence of a fault.
2. The truck being flawless under real road load rules out the entire
   worsens-under-load family that this reasoning pointed at — which is most
   of what the old ranked-suspect table contained.

### The better mount test

**D and R feel the same as each other.** Engine torque reacts in opposite
directions in D and R, so a collapsed mount or a torque-reaction contact
point would feel different between them. It does not.

Combined with the symptom reproducing at a standstill in **Park**, this
rules out mounts, flexplate, driveshaft, U-joints, tyres and wheel balance
more firmly than the old D-vs-N test ever did.

---

## Work already performed — none of it changed the shake

| Work | Detail |
|---|---|
| Spark plugs | Replaced. No change. |
| Air filter | Replaced. |
| **Throttle body** | **Removed from the manifold and hand-cleaned. No change.** |
| **Fuel injectors** | **Removed, cleaned and flow-tested.** |
| Engine oil and filter | Changed. Currently 5W-30. |
| Coolant | Flushed and replaced. Level steady since. |
| 6R80 fluid | Changed at 113,000 km. |
| Oxygen sensors | "Cleaned" — **method unknown**. |
| Intake manifold | Off during the injector work, refitted. **No change.** |
| Battery | Disconnected once; relearn done plus ~300 km driven. |

### Also established

- **Factory airbox and duct**, no oiled aftermarket filter — MAF
  calibration is as Ford intended.
- **Always 95 octane, same station** — fuel supply is constant.
- **No aftermarket tune**, no evidence of prior engine work.
- **Thermostat reaches and holds** normal temperature — the PCM does exit
  warm-up enrichment.
- **Rear differential fluid** changed at some point.
- Oil is **5W-30** against a 5W-20 spec — correct at the next change, but it
  is not the cause: sluggish phasers hurt more under load, and this truck is
  flawless under load.

### Concern: the oxygen sensors — separate from the shake

Heated O2 sensors are not serviceable by cleaning. Solvent attacks the
platinum layer and the ceramic element, and mechanical cleaning damages the
shroud's diffusion slots. Either is permanent.

**But they are not the cause of this shake.** The symptom is identical cold,
where the PCM runs open loop and ignores them entirely.

**Still check upstream HO2S switching rate at 2,500 rpm.** A healthy sensor
crosses 0.1↔0.9 V several times per second. Slow, lazy or parked mid-range
means replace. Treat as a separate, owed repair.

---

## Elimination record

Everything below is ruled out, with the evidence that ruled it out.

| Ruled out | Evidence |
|---|---|
| Fuel delivery — pump, filter, pressure | Pulls great under load; these fail under load first |
| Compression, valves, cam timing, phasers *stuck in position* | Same — all worsen under load |
| Ignition — plugs, coils, boots | Plugs changed nothing; ignition faults bite under load |
| Mounts, damper, flexplate, driveline, exhaust contact | Reproduces in Park; D and R identical; nothing mechanical moves a tachometer needle |
| O2 sensors as *root cause* | Symptom identical cold, in open loop |
| MAF / metering error | Factory airbox and duct, no oiled filter |
| Fuel quality or octane | Always 95, same station; symptom utterly constant |
| Aftermarket PCM tune | Never tuned; no evidence of prior engine work |
| Unlearned adaptive memory | Relearn done, plus 300 km |
| Intake manifold gasket disturbed in the injector job | Manifold off and refitted with **zero** change |
| **Throttle body carbon** | **Properly removed, hand-cleaned, no change** |
| **Injectors** | **Removed, cleaned and flow-tested** |
| Thermostat / warm-up enrichment | Reaches and holds temperature |
| Coolant intrusion / internal water pump | Level steady, no loss |
| Idle air control / low idle speed | Idle normal at 650–750; no change with A/C load |

---

## Open suspects, ranked

Only if the rpm-movement test shows a genuine fault. Note what they have in
common: **every survivor is a vacuum- or charge-control component that has
never been touched.**

| # | Suspect | Why it fits | Test |
|---|---|---|---|
| 1 | **EVAP purge valve stuck partly open** | Never touched. Reported as a very common failure on the 2009–2014 F-150. Stuck open = a constant unmetered air and vapour leak, rough idle that shakes when stopped, worst at a standstill, **frequently no code**. Part is cheap. | Pinch its hose to the manifold at idle. Or hand-vacuum-pump the inlet with the connector unplugged — it must hold. |
| 2 | **PCV valve, hose, elbow** | Never inspected. 12 years of Jeddah heat hardens the rubber; cracks open hot and close cold. Same leak signature. | Flex it **hot and running**. Pinch test at idle. Oil filler cap test. |
| 3 | **VCT solenoid / cam phaser** | This engine's *internal EGR* is done by cam overlap — see the note below. A phaser or solenoid misbehaving specifically at idle, where oil pressure and phaser authority are lowest, produces dilution that clears as load and pressure rise. | Commanded vs actual cam position at idle. **Swap solenoids bank to bank** — if the fault follows, it is the solenoid. Inspect solenoid screens. |
| 4 | **Vacuum leak elsewhere** | Brake booster hose, manifold gaskets, fittings. Not excluded, but the manifold refit changed nothing. | Smoke test — **only after trims justify it**. |

### Why suspect 3 was previously eliminated, and why it is back

An earlier revision ruled out cam phasers on the grounds that they worsen
under load. That argument conflated two different failure modes:

- **Phaser stuck in a fixed wrong position** — costs power under load. The
  truck pulling great genuinely rules this out.
- **Phaser or VCT solenoid misbehaving at idle** — oil pressure is lowest
  at idle, so control authority is weakest exactly there. Cam position
  wanders, rpm wanders with it, and it cleans up as load and oil pressure
  rise. The elimination never applied to this mode.

Two things still argue against it: VCT faults normally set **P0010–P0024**
and there have been no codes, and the classic description is
rough-cold-smooths-warm, while this is identical cold and hot.

### There is no external EGR valve on this engine

The 3.7 Ti-VCT uses twin independent cam phasing to create **internal EGR**
through controlled valve overlap; retarding the exhaust cam does the job the
EGR valve used to do, so the valve was deleted. RockAuto's catalogue is
consistent with this — the 2014 F-150 **3.5L EcoBoost** lists an EGR valve
control solenoid, the **3.7L** does not.

Earlier revisions of this document listed "EGR stuck or leaking" as a ranked
suspect and "EGR actual position at idle" as required scan data. **Both were
wrong** — there is no such valve and likely no such PID. The dilution
mechanism survives; it lives in the phasers. [VERIFY against the service
manual]

---

## Data still needed

1. **RPM movement at warm idle, logged** — the threshold question. See
   [Is this a fault?](#is-this-a-fault).
2. **Codes — permanent (Mode $0A) especially.** The battery disconnect
   wiped stored and pending; permanent codes are the only surviving history.
3. **LTFT bank 1 and bank 2** at warm idle in P, in D on the brake, and at
   2,500 rpm no load.
4. **Misfire counters per cylinder.**
5. **VCT commanded vs actual** at idle, both banks.
6. **HO2S upstream switching rate** — separate, owed repair.

### How to read the results

| Reading | Healthy | Fault indication |
|---|---|---|
| RPM at steady warm idle | ±25–50 rpm wander | ±100 rpm or rhythmic hunting |
| LTFT B1 / B2, warm idle | within ±5%, ±10% tolerable | Double-digit positive that **shrinks** at 2,500 rpm → unmetered air. The key reading. |
| LTFT split between banks | within a few % of each other | One bank high → narrows to three cylinders |
| Misfire counters | 0, or a stray count | One cylinder dominant → that cylinder. Even spread → global cause |
| Rough idle **with normal trims** | — | **Dilution, not mixture** → suspect 3 |
| VCT actual vs commanded | tracks within a few degrees | Lagging, wandering or not following → phaser or solenoid |
| HO2S upstream @ 2,500 rpm | 0.1↔0.9 V, several times/sec | Slow or parked mid-range → sensor damaged |
| ECT warm | ~88–100 °C | Confirmed normal on this truck |

**Trims decide whether to smoke test, not the other way round.** LTFT within
±10% at idle means no leak present is significant enough to explain a shake,
and a smoke test would only surface leaks too small to matter. Any 12-year
old engine shows *some* smoke somewhere.

---

## Test procedures

### 1. EVAP purge valve (free, do first)

The valve is **normally closed** when de-energized. Everything below tests
that. Fuel vapour is involved — no ignition sources.

- **Pinch test.** Warm idle in P. Clamp the hose from the purge valve to the
  intake manifold, watch 20 s. *Idle steadies, shake reduces, rpm may rise
  slightly* → **the valve was leaking.** No change → move on.
- **Vacuum hold, engine off.** Disconnect both hoses, hand vacuum pump on
  the inlet port, connector unplugged. Must **hold**. Bleeds down → stuck
  open.
- **Flow test, running.** Unplug the connector so the PCM cannot command it
  open, pull the canister-side hose, finger over the port. Vacuum pulling →
  passing with no command → stuck open.
- **Scan tool.** Command 0% then 100% duty at idle. Rpm and STFT must react
  when commanded open and be flat when commanded closed.

If any test is positive, **replace rather than clean.**

### 2. PCV valve, hose, elbow (free)

- **Flex it hot and running.** Heat-hardened rubber cracks open when flexed
  and closes cold — a cold visual inspection misses it. Look for glazing,
  crazing, a chalky surface.
- **Pinch test at idle.** Rough idle smooths → air was getting in. Idle
  rises slightly then settles → normal.
- **Oil filler cap.** Lift slowly at idle. Small change that settles →
  normal. Idle drops hard → restricted ventilation. Idle *smooths* →
  crankcase pressure problem.

[VERIFY] Confirm against the parts catalogue whether this engine has a
serviceable PCV valve at all — several Ford engines of this era integrate a
fixed orifice into the valve cover with no replaceable valve.

### 3. Vacuum leak, general

- **Smoke test.** Seal the intake. **Clamp off the PCV and purge lines
  first**, or a leaking valve shows up as "system leaks" and localises
  nothing. Run twice — clamped and unclamped; the difference isolates the
  valves from the manifold. Inspect manifold gaskets, throttle body base,
  every hose and fitting, brake booster hose, dipstick tube.
- **Vacuum gauge, manifold port, warm idle.** Steady 18–22 inHg → healthy at
  this elevation. Steady but low → leak or retarded timing. Needle drifting
  slowly → mixture instability. Rapid regular flicker → valve or guide.
- **Brake booster.** Clamp its hose at idle; a change means booster or check
  valve.

Do not spray flammable cleaner around a hot running engine to hunt leaks.
Smoke does the same job with none of the risk.

### 4. VCT solenoid and phasers

- **Scan data both banks at idle.** Actual tracking commanded smoothly →
  working. Wandering, lagging or hunting → solenoid or phaser.
- **Bank swap.** Swap the two VCT solenoids side to side. Fault moves →
  **the solenoid** (cheap). Fault stays → phaser, chain or oil supply.
- **Solenoid screens.** Pull and inspect for debris or a holed screen.
- **Oil pressure at hot idle**, mechanical gauge. Reported requirement is at
  least **25 psi** for phasers and tensioners. [VERIFY — reported in a TSB
  summary, source document not read]
- **Chain stretch.** Reported TSB method: **VCT_INT_ACT1 ≥ +6° at idle**
  indicates a worn chain; with the cover off, **more than 5 teeth** of
  tensioner extension confirms. [VERIFY — same caveat]

---

## Quick checks — ten minutes, engine off, before anything else

Both physical tests come from the **Mustang 3.7 community**: the same Cyclone
engine as this truck, and a far larger source of engine-specific knowledge
than the F-150 3.7 community. Run `f150diag run quick-wins` to be walked
through them.

| # | Test | Result that finds the fault |
|---|---|---|
| 1 | **PCV valve shake test.** Passenger-side valve cover, roughly halfway forward. Pull and shake. | **No rattle = clogged.** Mustang 3.7 sources name PCV clogging as a known rough-idle cause on this engine. |
| 2 | **Purge valve vacuum hold.** Engine off, connector unplugged, hand pump on the inlet port. | **Bleeds down = stuck open.** Mustang sources say stuck-open is *the* failure mode of Ford's purge valve. |
| 3 | **Calibration check.** `f150diag survey` reads the PCM calibration IDs. | A later calibration existing for this VIN would be a reflash with no parts. |

Neither physical test needs the engine running, so neither carries the stall
risk that makes vacuum work awkward on this engine.

**Expectation, stated honestly:** six competent repairs have already failed,
so a quick win is unlikely. Run these because they cost ten minutes and target
the two components never inspected — and because a clean result eliminates two
of the top three suspects with evidence rather than by assumption.

### Documents worth fetching

- **`MC-10184634-0001`** — an NHTSA bulletin titled *"Vibration/Rough Idle In
  DRIVE Or REVERSE, Lack Of…"*. The title matches this truck's symptom pattern
  closely. Applicability unknown; the document could not be opened from the
  environment where this note was written. Highest-value single thing to fetch.
  `https://static.nhtsa.gov/odi/tsbs/2020/MC-10184634-0001.pdf`

### Ideas considered and rejected

Recorded so they are not re-derived and re-tested at the owner's expense. See
the knowledge base entries prefixed `dismissed-`.

- **Oil change / viscosity** — the reported case was rough-when-cold, cured by
  an oil change. This truck is identical cold and hot, so the mechanism cannot
  be the same. (5W-30 against a 5W-20 spec is still worth correcting.)
- **Carbon cleaning / Seafoam** — the 3.7 is **port** injected, so valve-back
  carbon matters far less than on a direct-injected engine, and the injectors
  here were already flow-tested and the throttle body properly cleaned.
- **Aftermarket tune** — never tuned, no evidence of prior engine work.

---

## Vacuum testing on this engine

**The lines are hard plastic. They cannot be clamped or pinched.** Isolating
one means disconnecting it and plugging the manifold port.

**And it must be done with the engine OFF** — opening a manifold port on a
running engine is a leak large enough to stall it.

Every isolation test therefore runs: engine off, disconnect, plug, restart,
settle 30 s, measure. Because each test involves a restart, the comparison
baseline is taken the same way, so all measurements are made under identical
conditions.

Order: **purge, then booster, then PCV.** Sealing the first two should change
nothing on a healthy engine, so they give a clean signal. PCV is a metered air
path in normal operation, so blocking it shifts the idle even when nothing is
wrong — read the instability, not the rpm number.

Check no plug is left in a port afterwards.

---

## Recommended next actions

0. **Quick wins** — PCV shake test and purge valve vacuum hold. Ten minutes,
   engine off, no scan tool. `f150diag run quick-wins`.
1. **Establish whether there is a fault.** Control-sample another vehicle with
   this engine, and log the rpm movement at warm idle. Free. Note that Ford's
   stated position on a 2011-2014 Mustang 3.7 vibration complaint was that it
   is normal operation of the engine.
2. **Purge valve and PCV pinch tests.** Free, two minutes, no tools, and
   they target the two components never touched in twelve years.
3. **Read permanent codes, fuel trims and misfire counters.**
4. **Smoke test** — only if trims show a leak that matters.
5. **VCT cam position tracking and bank-swap** — if trims are normal but the
   rpm movement is genuinely out of range.
6. **HO2S switching rate** — separate, owed regardless.

**Do not fit another part before steps 1 and 2.** Six repairs have been
bought chasing a symptom nobody has yet established is abnormal, and every
one of them targeted a fault that gets *worse* under load — which this truck
does not have.

---

## Research note

Forum and TSB sources were searched, but this environment's network policy
blocks f150forum, ford-trucks, fordf150.net, edmunds, reddit, RockAuto,
go-parts and static.nhtsa.gov. **Findings attributed to those sources come
from search-engine summaries, not pages actually opened.** Treat them as
second-hand. The purge valve failure-rate claim and the VCT/TSB thresholds
above are both in that category.

---

## Note on this engine

The 3.7L Cyclone uses an **internal, timing-chain-driven water pump.** When
it fails it dumps coolant into the oil pan rather than onto the ground. If
any coolant loss appears with no external leak, check the dipstick for milky
oil or an over-full pan before chasing anything else. **Level is currently
steady.**
