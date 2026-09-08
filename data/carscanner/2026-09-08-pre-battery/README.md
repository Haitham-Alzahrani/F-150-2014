# 2026-09-08 — captures taken BEFORE the battery replacement

Owner's note: *"all those today before replacing battery, some AC on and some AC
off, and it's mixed idle and drive."*

**Why this batch is its own epoch.** A battery replacement drains Keep Alive
Memory — the third KAM wipe in this project's record. Everything here is the
**fully relearned, symptomatic** state: ~131,000 km, mounts replaced 09-06,
purge valve replaced 09-05, and well past the ~100 km at which the D/R
improvement relapsed last time. Captures taken after the new battery belong in a
separate directory and must not be pooled with these.

Timestamps are the phone clock. Odometer and adaptives are not re-read here.

| File | Clock | Duration | Channels | Notes |
|---|---|---|---|---|
| `20260908_154859.csv.gz` | 15:49:08 → 16:26:43 | 37.6 min | 44 | The only file with `Engine RPM` (n=17,562 at 0.120 s). Reaches 6,781 rpm, GPS to 119 km/h — driving. ECT 62–67 °C, so it starts warming. |
| `20260908_165822.csv.gz` | 16:58:22 → 17:04:16 | 5.9 min | 11 | Driving, GPS to 63 km/h. Load 13.7–91.4 %. ECT 84–86 °C. |
| `20260908_170417.csv.gz` | 17:04:24 → 17:17:45 | 13.3 min | 68 | Stationary (GPS ≤ 1.1 km/h, `Vehicle speed` 0). ECT 100–101 °C. Widest channel set in the batch. |
| `20260908_171750.csv.gz` | 17:17:58 → 18:19:29 | 61.5 min | 29 | Longest. Mixed — GPS 0 → 39.6 km/h. ECT 83–84 °C. |
| `20260908_181946.csv.gz` | 18:19:54 → 18:33:11 | 13.3 min | 23 | GPS/fuel-economy channels only. No engine PIDs. |

## Coverage gap, recorded at intake and not yet acted on

**`Engine RPM` appears in one file of five.** The four later captures have fuel
trims, load, coolant and oxygen sensors but no engine speed, so nothing in them
can be timed or correlated against the rpm oscillation. The one file that does
carry it pairs it with `Short term fuel % trim - Bank 1` at the same 0.120 s
rate (n=17,562 and 17,187) — the first time those two have been co-sampled
densely in this project.

Also absent from the whole batch: `Fuel/Air com. ratio`, `Timing advance`
(3 samples in `154859`, none elsewhere), and
`Long term secondary oxygen sensor trim`.

## Provenance

Car Scanner, CSV #2 (Horizontal), same adapter and phone as every earlier
capture. Uploaded 2026-09-08. A/C state per capture is **not recorded** — the
owner says the batch is mixed and `A/C pressure` is a dead channel on this
truck, so A/C state must be inferred from the engine-load signature (compressor
cycling steps load on a ~15.78 s period) before any capture here is used.
