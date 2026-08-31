#!/usr/bin/env python3
"""
obd_logger.py - real-time OBD-II data logger for the 2014 F-150 3.7L.

Talks to an ELM327-compatible adapter (vLinker FS/FD, OBDLink, generic clone)
over a serial port and records live engine parameters to CSV and JSON Lines.

READ-ONLY. Issues standard SAE J1979 Mode 01 requests and ELM327 configuration
commands only. It never writes to a control module, clears a DTC, or actuates
anything.

Usage
-----
    # No hardware needed - validates every decoder against known byte values
    /home/user/f-150-2014/.venv/bin/python src/obd_logger.py --self-test

    # What can this machine see?
    /home/user/f-150-2014/.venv/bin/python src/obd_logger.py --list-ports
    /home/user/f-150-2014/.venv/bin/python src/obd_logger.py --list-pids

    # Log the default parameter set for 60 seconds
    /home/user/f-150-2014/.venv/bin/python src/obd_logger.py \\
        --port /dev/ttyUSB0 --duration 60

    # Fuel-trim focus, tagged with the test condition
    /home/user/f-150-2014/.venv/bin/python src/obd_logger.py \\
        --port /dev/ttyUSB0 --pids rpm,stft_b1,ltft_b1,stft_b2,ltft_b2 \\
        --label "idle-park" --duration 45

Adapter note: keep the PID count modest. A cheap ELM327 clone manages only a
few samples per second, and every extra PID divides that further.
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import re
import signal
import statistics
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterable, Sequence

try:
    import serial
    from serial.tools import list_ports
except ImportError:
    sys.exit(
        "pyserial is not installed in this environment.\n"
        "Install it with:\n"
        "  /home/user/f-150-2014/.venv/bin/pip install -r requirements.txt"
    )


log = logging.getLogger("obd")

DEFAULT_BAUD = 38400
ELM_PROMPT = b">"

# Adapter replies that are answers about the conversation, not vehicle data.
NON_DATA_REPLIES = (
    "NO DATA", "SEARCHING", "STOPPED", "UNABLE TO CONNECT", "BUS INIT",
    "BUS ERROR", "CAN ERROR", "DATA ERROR", "BUFFER FULL", "ERROR", "?",
)


# ---------------------------------------------------------------------------
# PID definitions (SAE J1979 Mode 01)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Pid:
    """One Mode 01 parameter and how to turn its bytes into a number."""
    code: str                              # hex PID, e.g. "0C"
    name: str                              # short key used in output columns
    label: str                             # human description
    unit: str
    nbytes: int                            # data bytes expected after 41 XX
    decode: Callable[[Sequence[int]], float]

    @property
    def request(self) -> str:
        return f"01{self.code}"


def _percent_255(d: Sequence[int]) -> float:
    """0-100% scaled over a single byte."""
    return d[0] * 100.0 / 255.0


def _trim(d: Sequence[int]) -> float:
    """Fuel trim: -100% to +99.2%, centred on 128."""
    return (d[0] - 128) * 100.0 / 128.0


PIDS: tuple[Pid, ...] = (
    Pid("04", "engine_load",  "Calculated engine load",     "%",    1, _percent_255),
    Pid("05", "ect",          "Engine coolant temperature", "degC", 1, lambda d: d[0] - 40),
    Pid("06", "stft_b1",      "Short-term fuel trim B1",    "%",    1, _trim),
    Pid("07", "ltft_b1",      "Long-term fuel trim B1",     "%",    1, _trim),
    Pid("08", "stft_b2",      "Short-term fuel trim B2",    "%",    1, _trim),
    Pid("09", "ltft_b2",      "Long-term fuel trim B2",     "%",    1, _trim),
    Pid("0B", "map",          "Intake manifold pressure",   "kPa",  1, lambda d: float(d[0])),
    Pid("0C", "rpm",          "Engine RPM",                 "rpm",  2, lambda d: ((d[0] << 8) | d[1]) / 4.0),
    Pid("0D", "speed",        "Vehicle speed",              "km/h", 1, lambda d: float(d[0])),
    Pid("0E", "timing_adv",   "Timing advance",             "deg",  1, lambda d: (d[0] / 2.0) - 64.0),
    Pid("0F", "iat",          "Intake air temperature",     "degC", 1, lambda d: d[0] - 40),
    Pid("10", "maf",          "Mass air flow",              "g/s",  2, lambda d: ((d[0] << 8) | d[1]) / 100.0),
    Pid("11", "throttle",     "Throttle position",          "%",    1, _percent_255),
    Pid("2C", "egr_cmd",      "Commanded EGR",              "%",    1, _percent_255),
    Pid("2D", "egr_error",    "EGR error",                  "%",    1, _trim),
    Pid("42", "module_volts", "Control module voltage",     "V",    2, lambda d: ((d[0] << 8) | d[1]) / 1000.0),
    Pid("43", "abs_load",     "Absolute load value",        "%",    2, lambda d: ((d[0] << 8) | d[1]) * 100.0 / 255.0),
    Pid("46", "ambient_temp", "Ambient air temperature",    "degC", 1, lambda d: d[0] - 40),
)

PIDS_BY_NAME = {p.name: p for p in PIDS}

# The parameters that matter for the open idle-quality investigation.
DEFAULT_PIDS = (
    "rpm", "speed", "engine_load",
    "stft_b1", "ltft_b1", "stft_b2", "ltft_b2",
    "ect", "maf", "throttle",
)


# ---------------------------------------------------------------------------
# ELM327 transport
# ---------------------------------------------------------------------------

class ElmError(RuntimeError):
    """The adapter answered, but not with usable vehicle data."""


class Elm327:
    """Minimal, read-only ELM327 client."""

    def __init__(self, port: str, baud: int = DEFAULT_BAUD, timeout: float = 5.0):
        self.port_name = port
        self.baud = baud
        self.timeout = timeout
        self.ser: serial.Serial | None = None

    def __enter__(self) -> "Elm327":
        self.open()
        return self

    def __exit__(self, *exc_info) -> None:
        self.close()

    def open(self) -> None:
        log.info("opening %s at %d baud", self.port_name, self.baud)
        self.ser = serial.Serial(self.port_name, self.baud, timeout=self.timeout)
        time.sleep(0.5)                     # let a clone adapter settle
        self.ser.reset_input_buffer()
        self._initialise()

    def close(self) -> None:
        if self.ser and self.ser.is_open:
            self.ser.close()
            log.info("serial port closed")

    def _initialise(self) -> None:
        """Standard ELM327 bring-up. Configuration only - nothing reaches the ECU."""
        for command, description in (
            ("ATZ",   "reset"),
            ("ATE0",  "echo off"),
            ("ATL0",  "linefeeds off"),
            ("ATS0",  "spaces off"),
            ("ATH0",  "headers off"),
            ("ATAT1", "adaptive timing"),
            ("ATSP0", "auto protocol"),
        ):
            reply = self._command(command)
            log.debug("%-6s (%s) -> %s", command, description, reply)
            time.sleep(0.1)

        identity = self._command("ATI")
        log.info("adapter: %s", identity or "unknown")

        protocol = self._command("ATDP")
        log.info("protocol: %s", protocol or "unknown")

    def _command(self, cmd: str) -> str:
        """Send a raw command and return the reply text, prompt stripped."""
        if not self.ser:
            raise ElmError("serial port is not open")
        self.ser.reset_input_buffer()
        self.ser.write((cmd + "\r").encode("ascii"))
        self.ser.flush()
        return self._read_until_prompt()

    def _read_until_prompt(self) -> str:
        """Read until the ELM327 '>' prompt or the timeout expires."""
        assert self.ser is not None
        buf = bytearray()
        deadline = time.monotonic() + self.timeout
        while time.monotonic() < deadline:
            chunk = self.ser.read(self.ser.in_waiting or 1)
            if chunk:
                buf.extend(chunk)
                if ELM_PROMPT in buf:
                    break
            else:
                time.sleep(0.01)
        return buf.replace(ELM_PROMPT, b"").decode("ascii", errors="replace").strip()

    def query(self, pid: Pid) -> float | None:
        """Request one PID. Returns the decoded value, or None if unavailable."""
        raw = self._command(pid.request)
        try:
            data = parse_mode01(raw, pid)
        except ElmError as exc:
            log.debug("%s: %s", pid.name, exc)
            return None
        try:
            return round(float(pid.decode(data)), 3)
        except (IndexError, ValueError, TypeError) as exc:
            log.warning("%s: could not decode %s (%s)", pid.name, data, exc)
            return None


_FRAME_INDEX_RE = re.compile(r"^[0-9A-F]:")
_LENGTH_HEADER_RE = re.compile(r"^[0-9A-F]{3}$")


def parse_mode01(raw: str, pid: Pid) -> list[int]:
    """
    Pull the data bytes out of an ELM327 reply to a Mode 01 request.

    Handles single-frame replies ("410C1AF8") and the multi-frame form the
    adapter prints with headers off, where a length header precedes lines
    tagged "0:", "1:" and so on.

    Raises ElmError when the reply carries no usable data.
    """
    text = raw.upper()
    for marker in NON_DATA_REPLIES:
        if marker in text:
            raise ElmError(f"adapter replied {marker!r}")

    hex_parts: list[str] = []
    for line in re.split(r"[\r\n]+", text):
        line = line.strip().replace(" ", "")
        if not line or _LENGTH_HEADER_RE.match(line):
            continue
        line = _FRAME_INDEX_RE.sub("", line)
        hex_parts.append(line)

    payload = "".join(hex_parts)
    if not payload or not re.fullmatch(r"[0-9A-F]+", payload):
        raise ElmError(f"unparseable reply {raw!r}")

    expected = f"41{pid.code}"
    start = payload.find(expected)
    if start < 0:
        raise ElmError(f"no {expected} response in {payload!r}")

    body = payload[start + len(expected):]
    needed = pid.nbytes * 2
    if len(body) < needed:
        raise ElmError(f"short reply: wanted {pid.nbytes} bytes, got {len(body)//2}")

    return [int(body[i:i + 2], 16) for i in range(0, needed, 2)]


# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------

def configure_logging(verbose: bool, logfile: Path | None) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    log.setLevel(level)
    log.handlers.clear()

    console = logging.StreamHandler(sys.stderr)
    console.setLevel(level)
    console.setFormatter(logging.Formatter("%(asctime)s %(levelname)-7s %(message)s",
                                           datefmt="%H:%M:%S"))
    log.addHandler(console)

    if logfile:
        logfile.parent.mkdir(parents=True, exist_ok=True)
        handler = logging.FileHandler(logfile, encoding="utf-8")
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)-7s %(name)s %(message)s"))
        log.addHandler(handler)
        log.info("session log: %s", logfile)


# ---------------------------------------------------------------------------
# Sampling
# ---------------------------------------------------------------------------

class Recorder:
    """Writes each sample to CSV and JSON Lines, and keeps running statistics."""

    def __init__(self, out_dir: Path, pids: Sequence[Pid], label: str | None):
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        tag = f"-{re.sub(r'[^A-Za-z0-9_-]', '_', label)}" if label else ""
        out_dir.mkdir(parents=True, exist_ok=True)

        self.pids = pids
        self.label = label
        self.csv_path = out_dir / f"obd-{stamp}{tag}.csv"
        self.jsonl_path = out_dir / f"obd-{stamp}{tag}.jsonl"
        self.columns = ["timestamp", "elapsed_s", "label"] + [p.name for p in pids]
        self.samples = 0
        self._values: dict[str, list[float]] = {p.name: [] for p in pids}

        self._csv_fh = self.csv_path.open("w", newline="", encoding="utf-8")
        self._csv = csv.DictWriter(self._csv_fh, fieldnames=self.columns)
        self._csv.writeheader()
        self._jsonl_fh = self.jsonl_path.open("w", encoding="utf-8")

    def write(self, elapsed: float, readings: dict[str, float | None]) -> None:
        row: dict[str, object] = {
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
            "elapsed_s": round(elapsed, 2),
            "label": self.label or "",
        }
        row.update(readings)
        self._csv.writerow(row)
        self._csv_fh.flush()
        self._jsonl_fh.write(json.dumps(row) + "\n")
        self._jsonl_fh.flush()

        self.samples += 1
        for name, value in readings.items():
            if value is not None:
                self._values[name].append(value)

    def summary(self) -> list[tuple[str, str, int, float, float, float, float]]:
        """Per-PID (name, unit, n, min, mean, max, stdev)."""
        rows = []
        for pid in self.pids:
            vals = self._values[pid.name]
            if not vals:
                continue
            rows.append((
                pid.name, pid.unit, len(vals),
                round(min(vals), 2),
                round(statistics.fmean(vals), 2),
                round(max(vals), 2),
                round(statistics.pstdev(vals), 3) if len(vals) > 1 else 0.0,
            ))
        return rows

    def close(self) -> None:
        self._csv_fh.close()
        self._jsonl_fh.close()


_stop = False


def _handle_sigint(_signum, _frame) -> None:
    global _stop
    if _stop:                                # second Ctrl-C: give up immediately
        raise KeyboardInterrupt
    _stop = True
    log.warning("stopping after this sample - press Ctrl-C again to abort")


def run_capture(elm: Elm327, pids: Sequence[Pid], recorder: Recorder,
                duration: float, interval: float) -> None:
    log.info("logging %d parameters for %.0fs (interval %.2fs)",
             len(pids), duration, interval)
    started = time.monotonic()
    next_sample = started

    while not _stop:
        now = time.monotonic()
        elapsed = now - started
        if elapsed >= duration:
            break
        if now < next_sample:
            time.sleep(min(0.02, next_sample - now))
            continue

        readings = {p.name: elm.query(p) for p in pids}
        recorder.write(elapsed, readings)

        shown = " ".join(
            f"{n}={v}" for n, v in readings.items() if v is not None
        )
        log.info("t=%6.2fs %s", elapsed, shown or "(no data)")

        next_sample += interval
        if next_sample < time.monotonic():   # adapter slower than the interval
            next_sample = time.monotonic()


# ---------------------------------------------------------------------------
# Self-test - proves the decoders without any hardware
# ---------------------------------------------------------------------------

SELF_TEST_CASES: tuple[tuple[str, str, float], ...] = (
    # (pid name, raw adapter reply, expected decoded value)
    ("rpm",          "410C1AF8",   1726.0),   # 0x1AF8 / 4
    ("rpm",          "410C0A28",   650.0),    # typical warm idle
    ("speed",        "410D50",     80.0),
    ("speed",        "410D00",     0.0),
    ("ltft_b1",      "410780",     0.0),      # 128 -> 0%
    ("ltft_b1",      "410790",     12.5),     # 144 -> +12.5%
    ("stft_b1",      "410670",     -12.5),    # 112 -> -12.5%
    ("ect",          "410578",     80.0),     # 0x78 - 40
    ("iat",          "410F41",     25.0),
    ("maf",          "411001F4",   5.0),      # 500 / 100
    ("throttle",     "41117F",     49.804),
    ("engine_load",  "410440",     25.098),
    ("timing_adv",   "410E80",     0.0),      # (128/2) - 64
    ("module_volts", "41423A98",   15.0),
    ("egr_cmd",      "412C00",     0.0),
    ("map",          "410B23",     35.0),
)

MALFORMED_CASES: tuple[tuple[str, str], ...] = (
    ("rpm", "NO DATA"),
    ("rpm", "SEARCHING..."),
    ("rpm", "?"),
    ("rpm", "UNABLE TO CONNECT"),
    ("rpm", "410C1A"),          # truncated - only one byte of two
    ("rpm", "41051AF8"),        # answer to a different PID
    ("rpm", ""),
    ("rpm", "ZZZZ"),
)


def self_test() -> int:
    """Validate every decoder and the reply parser. Returns a process exit code."""
    passed = failed = 0

    print("decoding known replies")
    for name, raw, expected in SELF_TEST_CASES:
        pid = PIDS_BY_NAME[name]
        try:
            got = round(float(pid.decode(parse_mode01(raw, pid))), 3)
        except Exception as exc:                       # noqa: BLE001 - report anything
            print(f"  FAIL {name:<13} {raw:<12} raised {type(exc).__name__}: {exc}")
            failed += 1
            continue
        if abs(got - expected) < 0.01:
            print(f"  ok   {name:<13} {raw:<12} -> {got} {pid.unit}")
            passed += 1
        else:
            print(f"  FAIL {name:<13} {raw:<12} -> {got}, expected {expected}")
            failed += 1

    print("\nrejecting malformed replies")
    for name, raw in MALFORMED_CASES:
        pid = PIDS_BY_NAME[name]
        try:
            parse_mode01(raw, pid)
        except ElmError:
            print(f"  ok   rejected {raw!r}")
            passed += 1
        else:
            print(f"  FAIL accepted bad reply {raw!r}")
            failed += 1

    print("\nmulti-frame reassembly")
    multi = "014\r0:410C1AF8\r1:00000000"
    try:
        value = PIDS_BY_NAME["rpm"].decode(parse_mode01(multi, PIDS_BY_NAME["rpm"]))
        if abs(value - 1726.0) < 0.01:
            print(f"  ok   multi-frame -> {value} rpm")
            passed += 1
        else:
            print(f"  FAIL multi-frame -> {value}, expected 1726.0")
            failed += 1
    except Exception as exc:                           # noqa: BLE001
        print(f"  FAIL multi-frame raised {type(exc).__name__}: {exc}")
        failed += 1

    print(f"\n{passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def resolve_pids(spec: str | None) -> list[Pid]:
    names = [n.strip() for n in spec.split(",")] if spec else list(DEFAULT_PIDS)
    unknown = [n for n in names if n not in PIDS_BY_NAME]
    if unknown:
        raise SystemExit(
            f"unknown PID(s): {', '.join(unknown)}\n"
            f"available: {', '.join(sorted(PIDS_BY_NAME))}"
        )
    return [PIDS_BY_NAME[n] for n in names]


def autodetect_port() -> str | None:
    candidates = list(list_ports.comports())
    for port in candidates:
        text = f"{port.description} {port.manufacturer or ''}".lower()
        if any(k in text for k in ("obd", "elm", "vlink", "ftdi", "ch340", "usb serial")):
            return port.device
    return candidates[0].device if candidates else None


def print_ports() -> None:
    ports = list(list_ports.comports())
    if not ports:
        print("no serial ports found")
        print("check the adapter is plugged in, and that you have permission")
        print("to read the device (on Linux, membership of the 'dialout' group)")
        return
    for port in ports:
        print(f"{port.device:<20} {port.description}")
        if port.manufacturer:
            print(f"{'':<20} manufacturer: {port.manufacturer}")


def print_pids() -> None:
    print(f"{'name':<14} {'pid':<5} {'unit':<6} description")
    print("-" * 66)
    for pid in PIDS:
        default = " *" if pid.name in DEFAULT_PIDS else ""
        print(f"{pid.name:<14} 01{pid.code:<3} {pid.unit:<6} {pid.label}{default}")
    print("\n* included in the default set")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="obd_logger.py",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--port", help="serial device, e.g. /dev/ttyUSB0 (autodetected if omitted)")
    p.add_argument("--baud", type=int, default=DEFAULT_BAUD, help=f"baud rate (default {DEFAULT_BAUD})")
    p.add_argument("--duration", type=float, default=60.0, help="seconds to log (default 60)")
    p.add_argument("--interval", type=float, default=0.5, help="seconds between samples (default 0.5)")
    p.add_argument("--pids", help="comma-separated PID names (see --list-pids)")
    p.add_argument("--label", help="tag for this capture, e.g. 'idle-park'")
    p.add_argument("--out-dir", type=Path, default=Path("logs"), help="output directory (default ./logs)")
    p.add_argument("--timeout", type=float, default=5.0, help="serial read timeout (default 5.0)")
    p.add_argument("--verbose", "-v", action="store_true", help="debug logging")
    p.add_argument("--list-ports", action="store_true", help="list serial ports and exit")
    p.add_argument("--list-pids", action="store_true", help="list supported PIDs and exit")
    p.add_argument("--self-test", action="store_true", help="validate decoders without hardware")
    return p


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)

    if args.self_test:
        return self_test()
    if args.list_pids:
        print_pids()
        return 0
    if args.list_ports:
        print_ports()
        return 0

    pids = resolve_pids(args.pids)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    configure_logging(args.verbose, args.out_dir / "obd_logger.log")

    port = args.port or autodetect_port()
    if not port:
        log.error("no serial port given and none detected - try --list-ports")
        return 2

    signal.signal(signal.SIGINT, _handle_sigint)

    recorder = Recorder(args.out_dir, pids, args.label)
    log.info("writing %s", recorder.csv_path)
    log.info("writing %s", recorder.jsonl_path)

    try:
        with Elm327(port, args.baud, args.timeout) as elm:
            run_capture(elm, pids, recorder, args.duration, args.interval)
    except serial.SerialException as exc:
        log.error("serial error: %s", exc)
        return 2
    except ElmError as exc:
        log.error("adapter error: %s", exc)
        return 2
    except KeyboardInterrupt:
        log.warning("aborted")
    finally:
        recorder.close()

    rows = recorder.summary()
    if rows:
        print(f"\n{recorder.samples} samples -> {recorder.csv_path}\n")
        print(f"{'parameter':<14} {'unit':<6} {'n':>5} {'min':>9} {'mean':>9} {'max':>9} {'stdev':>9}")
        print("-" * 68)
        for name, unit, n, lo, mean, hi, sd in rows:
            print(f"{name:<14} {unit:<6} {n:>5} {lo:>9} {mean:>9} {hi:>9} {sd:>9}")
    else:
        print("\nno data captured - check the adapter, ignition and protocol")

    return 0


if __name__ == "__main__":
    sys.exit(main())
