# RUNNING THIS REPOSITORY ON WINDOWS, FROM `cmd`

**Written 2026-09-18. Every failure below was reproduced, not guessed.**

---

## 1. Clone and install

```
git clone <this repo>
cd F-150-2014
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -e .
```

**Do not run `.venv\Scripts\activate`** — this project's rule is to invoke the
interpreter directly, which avoids the whole question of which environment a
shell is in:

```
.venv\Scripts\python.exe -m f150diag.cli selftest
```

It should end with `all checks passed`. If the module is not found you are in a
different environment from the one you installed into; `set PYTHONPATH=src` and
`python -m f150diag.cli` always works from the repository root.

---

## 2. THE TWO THINGS THAT BROKE, AND ARE NOW FIXED

### The console codepage — this one stopped the first command in the docs

`f150diag selftest` **died part way through on cp437**, the standard US Windows
`cmd` codepage:

```
UnicodeEncodeError: 'charmap' codec can't encode character '—'
```

— an em dash in the tool's own output. cp850 the same. cp1252 survives the em
dash but still fails on the arrows, ticks and box drawing elsewhere in the
package, and on the `℃` in this project's channel names.

**Why it can look fine when you type it by hand.** Python writes Unicode
straight to a Windows *console* through the wide API, so an interactive run
often works. The crash bites when output is **redirected or piped** — `> out.txt`,
`| more`, or **an agent running the command and capturing the result**, which is
the normal case here.

**Fixed in code**, so nothing needs configuring: `cli.py` and every tool in
`data/` now force UTF-8 on stdout and stderr at startup. Verified afterwards on
cp437, cp850 and cp1252 — all three reach `all checks passed`.

If you want the console itself to render the characters rather than substitute
them, `chcp 65001` before running. Not required.

### Relative paths — silent, which is worse

The analysis tools globbed `data/carscanner/**/*` relative to the **current
directory**. Run from anywhere except the repository root and they matched
nothing, printed an empty table and **exited 0**. No error.

**Fixed**: `data/_repo.py` anchors every path to the repository, so the tools
work from any directory. Verified by running them from `/tmp`.

---

## 3. Finding the adapter

```
.venv\Scripts\python.exe data\f150_live.py --ports
```

Prints every serial port with its description. **Use this before connecting** —
auto-detect takes the first port that answers, and on a laptop with several
virtual COM ports that is often the wrong one, which then looks like a dead
adapter.

| Adapter | What to pass to `--port` |
|---|---|
| **USB** (OBDLink SX and similar) | `COM3`, `COM5` — whatever `--ports` shows |
| **Bluetooth Classic** | Pair it first, then use the **outgoing** COM port from Bluetooth settings |
| **BLE / Bluetooth 4.0+** | **Will not work.** `python-obd` speaks to a serial port and BLE presents none. Most cheap clones and anything paired to an iPhone are BLE. No port string fixes this. |

---

## 4. The commands you will actually use

```
.venv\Scripts\python.exe -m f150diag.cli selftest
.venv\Scripts\python.exe data\f150_live.py --ports
.venv\Scripts\python.exe data\f150_live.py --port COM5
```

Inside the live link: `log park-idle` · `rpm` · `rate` · `endlog` · `help`.
It is **read-only by allowlist**, and OBD service 04 (clear codes) is refused —
`read clear_dtc` comes back `REFUSED`, verified.

Then the analysis, which reads the CSV the live link just wrote:

```
.venv\Scripts\python.exe data\rpm_rate.py logs\<file>.csv
.venv\Scripts\python.exe data\idle_events.py logs\<file>.csv
.venv\Scripts\python.exe data\voltage_compare.py
.venv\Scripts\python.exe data\bank_offset.py
```

Backslashes are fine — Python accepts either separator on Windows.

---

## 5. What still will not work on Windows, and is not a bug

* **A cloud session cannot reach the truck at all.** No serial device exists in a
  container. Only a machine physically plugged into the truck can open an adapter.
* **`python-obd` implements no mode 22**, so no `[PCM]` channel — knock sensors,
  cylinder acceleration, cylinder head temperature, A/C pressure, ATF
  temperature, turbine speed, gear ratio — is reachable from it on any platform.
  Car Scanner on the phone and FORScan reach those. It **does** reach Mode 06,
  including per-cylinder misfire counts.
* **FORScan is Windows-only and that is an advantage here** — the one platform
  where the enhanced Ford data is available is the one you are now on. See
  [`FORSCAN.md`](FORSCAN.md).
