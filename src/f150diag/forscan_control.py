"""
Driving FORScan as an instrument.

FORScan exposes no command line, no API and no scripting interface — nothing
public, and its `.fsl` log format is closed binary that only FORScan reads.
So it cannot be called as a library. What it can be is *orchestrated*: this
module owns the sequence, hands the adapter over, launches FORScan, watches
where its exports land, and picks the result up the moment it appears.

The port is never shared. It is handed over and handed back, explicitly:

    1. this tool closes the adapter and records that FORScan owns it
    2. FORScan is launched (or the operator is told to start it)
    3. the operator records the parameters this tool cannot read
    4. a new export appears; this module detects and imports it
    5. FORScan closes, the adapter comes back, the protocol continues

Step 4 is what makes FORScan a tool rather than a detour. The alternative —
"export it and tell me the filename" — puts a person in the middle of every
handoff. Watching the folder removes them.

[VERIFY] Install paths and the AppData layout are from search summaries, not
from a machine with FORScan on it. Override with FORSCAN_EXE and
FORSCAN_DATA if the defaults miss.
"""

from __future__ import annotations

import logging
import os
import platform
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

log = logging.getLogger("f150diag.forscan_control")

PROCESS_NAME = "FORScan.exe"

#: Where the Windows installer normally puts it. [VERIFY]
INSTALL_CANDIDATES = (
    r"C:\Program Files (x86)\FORScan\FORScan.exe",
    r"C:\Program Files\FORScan\FORScan.exe",
)

EXPORT_SUFFIXES = (".csv", ".fsl")


def find_executable() -> Path | None:
    """FORSCAN_EXE, else the usual install locations."""
    override = os.environ.get("FORSCAN_EXE")
    if override:
        path = Path(override)
        return path if path.exists() else None
    for candidate in INSTALL_CANDIDATES:
        path = Path(candidate)
        if path.exists():
            return path
    return None


def data_directory() -> Path | None:
    """
    Where FORScan keeps vehicle profiles and saved live-data runs.

    Reported as the FORScan folder under AppData\\Roaming, with an `fsl`
    subfolder holding recorded runs. [VERIFY]
    """
    override = os.environ.get("FORSCAN_DATA")
    if override:
        path = Path(override)
        return path if path.is_dir() else None
    appdata = os.environ.get("APPDATA")
    if appdata:
        path = Path(appdata) / "FORScan"
        if path.is_dir():
            return path
    return None


def is_running() -> bool:
    """
    Is FORScan holding the adapter right now?

    Used to refuse opening the port rather than discovering the conflict as a
    permission error halfway through a measurement — which is why a false
    positive is expensive: it blocks a session that could have run.

    The command-line match must exclude this process and its parent. Running
    `f150diag forscan-status` puts the word "forscan" in our own command line,
    so a naive pgrep reports FORScan running whenever we ask the question.
    """
    try:
        if platform.system() == "Windows":
            out = subprocess.run(
                ["tasklist", "/FI", f"IMAGENAME eq {PROCESS_NAME}"],
                capture_output=True, text=True, timeout=10).stdout
            return PROCESS_NAME.lower() in out.lower()

        result = subprocess.run(["pgrep", "-fi", "forscan"],
                                capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            return False
        mine = {os.getpid(), os.getppid()}
        for line in result.stdout.split():
            try:
                pid = int(line)
            except ValueError:
                continue
            if pid in mine:
                continue
            try:
                cmdline = Path(f"/proc/{pid}/cmdline").read_bytes().decode(
                    "utf-8", "replace")
            except OSError:
                continue
            # Our own tooling mentions forscan constantly; it is not FORScan.
            if "f150diag" in cmdline:
                continue
            return True
        return False
    except (OSError, subprocess.SubprocessError) as exc:
        log.debug("could not check for a running FORScan: %s", exc)
        return False


def launch() -> subprocess.Popen | None:
    """Start FORScan. It takes no arguments, so this just opens the GUI."""
    exe = find_executable()
    if exe is None:
        log.warning("FORScan executable not found — set FORSCAN_EXE")
        return None
    if is_running():
        log.info("FORScan is already running")
        return None
    log.info("launching %s", exe)
    try:
        return subprocess.Popen([str(exe)])
    except OSError as exc:
        log.error("could not launch FORScan: %s", exc)
        return None


# ---------------------------------------------------------------------------
# Watching for an export
# ---------------------------------------------------------------------------

@dataclass
class Export:
    path: Path
    modified: float

    @property
    def is_csv(self) -> bool:
        return self.path.suffix.lower() == ".csv"


def search_roots(extra: Path | None = None) -> list[Path]:
    """Everywhere an export plausibly lands, most specific first."""
    roots: list[Path] = []
    if extra:
        roots.append(extra)
    data = data_directory()
    if data:
        roots.extend([data / "fsl", data])
    home = Path.home()
    for name in ("Documents", "Downloads", "Desktop"):
        candidate = home / name
        if candidate.is_dir():
            roots.append(candidate)
    return [r for r in roots if r.is_dir()]


def newest_export(since: float, roots: list[Path] | None = None) -> Export | None:
    """The most recently written FORScan export newer than `since`."""
    best: Export | None = None
    for root in (roots if roots is not None else search_roots()):
        for suffix in EXPORT_SUFFIXES:
            for path in root.glob(f"**/*{suffix}"):
                try:
                    mtime = path.stat().st_mtime
                except OSError:
                    continue
                if mtime <= since:
                    continue
                if best is None or mtime > best.modified:
                    best = Export(path=path, modified=mtime)
    return best


def wait_for_export(since: float, timeout_s: float = 900.0,
                    poll_s: float = 2.0,
                    roots: list[Path] | None = None,
                    on_wait=None) -> Export | None:
    """
    Block until a new export appears, or the timeout expires.

    Settling matters: a file shows up in the directory before it is finished
    being written, and importing a half-written CSV produces a truncated log
    that looks like a short recording rather than an error.
    """
    deadline = time.monotonic() + timeout_s
    announced = False
    while time.monotonic() < deadline:
        found = newest_export(since, roots)
        if found:
            size = -1
            for _ in range(10):                     # wait for the size to settle
                time.sleep(0.5)
                try:
                    current = found.path.stat().st_size
                except OSError:
                    break
                if current == size and current > 0:
                    return found
                size = current
            return found
        if not announced and on_wait:
            on_wait()
            announced = True
        time.sleep(poll_s)
    return None


# ---------------------------------------------------------------------------
# What to ask FORScan for
# ---------------------------------------------------------------------------

#: Named parameter sets to request, since FORScan has no way to be told
#: programmatically. The operator adds these by name in FORScan's PID list.
REQUESTS: dict[str, tuple[str, ...]] = {
    "vct": (
        "RPM",
        "VCT_INT_DES1", "VCT_INT_ACT1",
        "VCT_INT_DES2", "VCT_INT_ACT2",
        "VCT_EXH_DES1", "VCT_EXH_ACT1",
        "VCT_EXH_DES2", "VCT_EXH_ACT2",
    ),
    "misfire": (
        "RPM", "MISFIRE1", "MISFIRE2", "MISFIRE3",
        "MISFIRE4", "MISFIRE5", "MISFIRE6", "MIS_GENERAL",
    ),
    "fuel": ("RPM", "LONGFT1", "LONGFT2", "SHRTFT1", "SHRTFT2",
             "FUELPW1", "FUELPW2", "MAF", "MAP"),
}


def instructions(request: str, seconds: int = 90) -> str:
    """The operator-facing script for one handoff."""
    names = REQUESTS.get(request)
    if not names:
        raise KeyError(f"unknown FORScan request {request!r}. "
                       f"Known: {', '.join(sorted(REQUESTS))}")
    listed = "\n".join(f"      - {n}" for n in names)
    return f"""HANDOFF TO FORSCAN — {request}

  The adapter has been released. FORScan can now connect to it; this tool
  will not touch the port again until you are finished.

  1. Connect FORScan to the vehicle.
  2. Add these parameters to the PID list:
{listed}
  3. Record for about {seconds} seconds at the condition asked for above.
  4. Stop the recording and SAVE AS CSV — not .fsl. The .fsl format is
     FORScan's own and nothing else reads it. (If you have already saved an
     .fsl, FORScan converts it to CSV offline, with no adapter needed.)
  5. Close FORScan so the adapter is free again.

  This tool is watching for the export and will pick it up on its own — you
  do not need to tell it where the file is.

  Any parameter FORScan does not offer for this vehicle: skip it and carry
  on. A missing channel is reported, not fatal."""
