# 2014 Ford F-150 3.7L — Diagnostics

Working diagnostic record for a 2014 Ford F-150 XL, 3.7L V6 Ti-VCT, 6R80
automatic, 4x2.

VIN `1FTMF1EM1EFC80632` · 131,000 km · Jeddah, Saudi Arabia

## Contents

| File | What it is |
|---|---|
| [`docs/f150-diagnosis.md`](docs/f150-diagnosis.md) | The diagnostic log — vehicle ID, history report findings, symptom, tests performed, ruled-out causes, ranked open suspects, and the scan data still needed |
| [`docs/android-claude-code-setup.md`](docs/android-claude-code-setup.md) | Running Claude Code on Android via Termux + proot Debian, so this repo can be worked from the phone at the truck |
| [`CLAUDE.md`](CLAUDE.md) | Auto-loaded context so a session opened here already knows the truck |

## Current state — open

**Symptom:** small shake in the cab, unstable RPM held around 1,000–2,000.
Present before any repair work.

**Ruled out:** engine and transmission mounts, cracked flexplate, torque
converter. The gear-position test settles it — the shake is *less* in D/R
than in N, the inverse of the mount signature. The converter damps the
pulses when coupled, so the engine is genuinely running rough and the
converter masks it in gear.

**Already replaced or serviced, with no effect on the shake:** spark plugs,
air filter, injector clean, oil and filter, coolant flush, 6R80 fluid at
113,000 km, and an O2 sensor "cleaning" that may have damaged the sensors.

**Top unexplored lead:** the throttle body, never cleaned. Needs no scan
tool. Clean it, then run the idle relearn.

**Blocked on:** fuel trims both banks (idle in P/N vs D vs 2,500 rpm),
per-cylinder misfire counters, EGR actual position at idle, and codes —
stored, pending and permanent.

Two numbers collapse most of the diagnosis: fuel trims say whether it is a
mixture problem, misfire counters say whether it is one cylinder or all six.

## Working this from the phone

```
proot-distro login debian
```

```
git clone https://github.com/Haitham-Alzahrani/F-150-2014.git
```

```
cd F-150-2014
```

```
claude
```

Starting `claude` from inside this folder loads `CLAUDE.md` automatically, so
the session already knows the truck, the symptom, what has been ruled out,
and what data is still missing.
