# 2026-09-09 — the relapse the owner reported, measured

Owner, same day: *"now after relearn complete i feel the shake back."*

New battery (09-08 ~21:00), new engine and transmission mounts (09-06). Nothing
touched between 09-08 22:05 and these captures.

| File | Clock | Duration | Channels | What it is |
|---|---|---|---|---|
| `2026_09_09_16_12_50.csv.gz` | 16:12:50 → 16:24:34 | 11.7 min | 92 | Widest set. Carries **commanded** air/fuel, n=125. |
| `2026_09_09_16_24_29.csv.gz` | 16:24:37 → 17:29:01 | 64.4 min | 55 | 86 % driving. Engine speed n=6,093 with **both long term trims** at a matched 0.121 s. |
| `2026_09_09_17_40_46.csv.gz` | 17:40:54 → 17:41:44 | 0.8 min | 16 | Stationary, ECT 85 °C. |
| `2026_09_09_17_42_15.csv.gz` | 17:42:45 → 17:47:31 | 4.8 min | 40 | Stationary idle, the amplitude measurement. |

## THE HEADLINE: the rpm oscillation did NOT come back

Rate-matched to 0.212 s, Park idle 600–720 rpm, 10 s windows:

| State | n | Median span |
|---|---|---|
| 09-08 15:49, before the battery | 18 | 32.3 rpm |
| 09-08 22:05, after the battery, owner reports it quiet | 16 | **25.3** |
| **09-09 17:42, owner reports the shake back** | **14** | **27.3** |

**Quiet versus "relapsed": Mann-Whitney p = 0.633.** Statistically identical.
Against the pre-battery state, p = 0.108.

The needle stayed where the new battery put it. **What the owner feels came back;
what the crankshaft does did not.** This is the mirror image of the mount repair,
where the rpm was untouched and the seat shake vanished — and it is the second
independent demonstration that the felt symptom and the 0.3 Hz oscillation are
separate phenomena.

## Long term fuel trim — Bank 1 has not learned at all

| Capture | Bank 1 | Bank 2 |
|---|---|---|
| 09-08 17:04, before the battery | −0.7812 (n=201) | −0.7812 |
| 09-09 16:24, after a 64 min drive | **0.0000 flat** (n=5,971) | 0.0000 → +0.7812 (n=5,945) |
| 09-09 17:40 | **0.0000** (n=208) | **+1.5625** (n=23) |
| 09-09 17:42 | **0.0000 flat** (n=986) | +0.7812 → +1.5625 (n=984) |

**Bank 1 sits at exactly 0.0000 across 7,165 samples while Bank 2 climbs to
+1.5625.** Bank 1 is not frozen by a disabled learning mode — Bank 2 is learning
in the same samples. Bank 1 simply needs no correction and Bank 2 needs more
fuel. Third independent sighting of the driver-side lean offset, after the
+1.64 % paired short-term measurement and the +2.00 % that survived the 09-05
wipe.

## The commanded dither got BIGGER

| Capture | Peak-to-peak | As % of mean | Lean-side time |
|---|---|---|---|
| 09-04 pre-wipe (n=7,515) | 0.4559 | 3.126 % | 47.8 % |
| 09-09 16:12 (n=125) | 0.5291 | **3.627 %** | 40.0 % |
| 09-09 16:24 (n=20) | 0.5389 | 3.662 % | 10.0 % |

~16 % larger command, and more time on the rich side — the direction a relearned
rich bias predicts. **Small n, and no commanded-AFR channel exists in the quiet
09-08 22:05 capture**, so the quiet-state dither remains unmeasured and the
comparison is against a different session five days earlier.

The combination still matters: **the command grew while the rpm response did
not.** Whatever the new battery changed, it is on the response side.
