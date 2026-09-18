# THE TWO VOLTAGE CHANNELS DISAGREE ON THE 2014 AND AGREE ON THE CONTROL

**2026-09-18. Tool: [`data/voltage_compare.py`](../data/voltage_compare.py).**

`CLAUDE.md` carries one absolute criterion this truck fails: `Control module
voltage` reads **12.49–12.77 V with the engine running**, against 13.0–14.8
expected. It is explained with Ford smart charging and *"a BCM reading of
13.8 V"* — and then correctly doubted, because the file also records that the
supply channels were never polled together.

**They were never polled together, and it is not bad luck.**

## They cannot be paired at all

One session carries both: `2026-09-04 22-23-38`. They share a **145-minute**
span and coincide **zero times — even at a 30 second tolerance**.

| tolerance | simultaneous samples |
|---|---|
| 0.15 s | **0** |
| 1 s | **0** |
| 5 s | **0** |
| 30 s | **0** |

Two channels on different pages of the app are never polled together — the tiles
law. And the PCM is on **HS-CAN** while the BCM is on **MS-CAN**
(`docs/f150-specs.md`), so if the adapter switches buses, simultaneous sampling
is **physically impossible**, not merely unlucky. **No instant-by-instant
comparison can ever be made from a log.**

## What can be compared, and it is enough

Their **distributions over the same window with the engine confirmed running**.
Weaker than pairing — but the two do not overlap, so it settles the direction.

**2014, engine 602–812 rpm, confirmed running across 100 % of both windows:**

| | n | median | p10 | p90 | max | **in 13.5–14.5 V** |
|---|---|---|---|---|---|---|
| `Control module voltage` (PCM) | 3,276 | **12.67** | 12.54 | 12.77 | 13.79 | **0.7 %** |
| `[BCM] Vehicle Battery Voltage` | 2,756 | **13.00** | 12.85 | 13.95 | 14.05 | **47.9 %** |

**The BCM sits in the normal charging band about half the time. The PCM
essentially never does — 0.7 % of 3,276 samples.** They differ by **0.33 V** at
the median, in the same session, with the engine running throughout.

**And the 13.8 V that this file uses to explain the problem is not typical.**
Across 2,756 BCM samples the median is **13.00 V**, not 13.8. The explanation
rested on one snapshot.

## The control truck does NOT show the gap

**2023 F-150, `20260906_182055`:**

| | n | median |
|---|---|---|
| `Control module voltage` (PCM) | 10 | **13.47** |
| `[BCM] Vehicle Battery Voltage` | 3 | **13.40** |

**They agree within 0.07 V.** On the 2014 they differ by 0.33 V — roughly five
times as far apart — and the 2014's PCM channel is a full 0.80 V below the
control's.

## What it means, and what it does not

**A candidate that fits: voltage drop between the battery and the PCM's supply
or ground.** That is a real fault, and it matters beyond charging — **every
sensor reference on this engine rides on that supply.** The existing ground-drop
and ripple checks in `CLAUDE.md` are aimed at exactly this and have never been
done.

**The honest alternatives:** the PCM channel may simply report a
post-regulator rail rather than raw supply, in which case a fixed offset is
normal and means nothing.

**Caveats, stated plainly:**

* **No instantaneous pairing on either truck.** Distributions over a shared
  window, not matched samples.
* **The control is n=10 and n=3.** That is a hint, not a measurement, and its
  engine speed reached 1,776 rpm so it is not idle-matched to the 2014.
* **One 2014 session.** Every figure above comes from `2026-09-04`.

## The test, and it is now the highest-value ten minutes available

**A meter across the battery posts at idle** — item 7 on
[`IDLE-LOG-LIST.md`](IDLE-LOG-LIST.md), and it sidesteps the whole problem by
measuring the battery directly instead of asking two modules on two buses.

* **13.5–14.5 V with occasional drops** → charging is fine, the PCM channel
  reports something other than raw supply, and this closes.
* **A steady ~12.6 V** → the charging system genuinely is not charging, and the
  BCM's 47.9 % in-band is the channel to distrust.
* **Battery ~13.8 V while the PCM reports 12.6 V** → **a drop in the PCM's own
  supply or ground.** Then do the ground-drop test: battery negative → block,
  block → chassis, each under 0.1 V.
