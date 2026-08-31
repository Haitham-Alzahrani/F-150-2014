# 2014 Ford F-150 3.7L — Diagnostics

Working notes and tools for diagnosing a 2014 Ford F-150 XL 3.7L V6, and for
running the diagnostic tooling from an Android phone without a laptop.

VIN `1FTMF1EM1EFC80632` · 131,000 km · Jeddah, Saudi Arabia

## Contents

| File | What it is |
|---|---|
| [`docs/f150-diagnosis.md`](docs/f150-diagnosis.md) | Full diagnostic log — vehicle ID, history report findings, symptom, tests performed, ruled-out causes, ranked open suspects, and the scan data still needed |
| [`docs/android-claude-code-setup.md`](docs/android-claude-code-setup.md) | Verified procedure for running Claude Code on Android via Termux + proot Debian, including the PATH trap that breaks it silently |
| [`haraj_laptops.py`](haraj_laptops.py) | Searches haraj.com.sa for used business laptops, filters out auction posts, scores listings against a spec |
| [`CLAUDE.md`](CLAUDE.md) | Auto-loaded context so a Claude Code session in this folder already knows the truck |

## Current state

**Truck: open.** Mounts, flexplate and torque converter are ruled out by the
gear-position test — the shake is *less* in D/R than in N, which points at
combustion roughness masked by the converter when it is coupled. The top
unexplored lead is the throttle body, which has never been cleaned. Blocked
on scan data: fuel trims, per-cylinder misfire counters, EGR position.

**Tooling:** Claude Code confirmed running on Android — Termux → proot
Debian → Node 24 → Claude Code v2.1.250.

## Get this on the phone

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
and what data is still missing. No re-explaining.

## The laptop search script

```
pip install requests
```

Probe the site first — the parser is written against an unverified page
structure, and recon reports what actually comes back:

```
python3 haraj_laptops.py --recon
```

Then search:

```
python3 haraj_laptops.py --max-price 500
```

Filters applied: auction posts (السوم / مزاد with no final price) are
dropped, pre-8th-gen Intel is a hard reject by default, and unknown specs
are flagged rather than assumed.

### Buying spec

For running FORScan, Claude Code and the Python diagnostic tooling, the real
requirement is modest — any Core i5 with 8 GB RAM is comfortable. The
8th-gen threshold in the script's default scoring is about Windows 11
support, not capability; lower `MIN_CPU_GEN` for a tighter budget.

Reject regardless of price: 4 GB RAM, a BIOS/supervisor password (common on
ex-fleet machines and often unfixable), or no stated price. A mechanical
hard drive is acceptable if you plan to fit an SSD — that upgrade matters
more to daily usability than the CPU generation does.
