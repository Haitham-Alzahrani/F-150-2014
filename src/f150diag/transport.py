"""
ELM327 transport.

Owns the serial port and the adapter conversation. Knows nothing about what
the bytes mean — that is services.py.

READ-ONLY BY DESIGN. This module can send arbitrary strings to the adapter,
but every caller in this package issues diagnostic *read* services only.
Nothing here writes to a control module, clears a DTC, or actuates anything.
"""

from __future__ import annotations

import logging
import re
import time

try:
    import serial
    from serial.tools import list_ports
except ImportError:                                          # pragma: no cover
    serial = None
    list_ports = None

log = logging.getLogger("f150diag.transport")

DEFAULT_BAUD = 38400
PROMPT = b">"

#: Adapter replies that are answers about the conversation, not vehicle data.
NON_DATA_REPLIES = (
    "NO DATA", "SEARCHING", "STOPPED", "UNABLE TO CONNECT", "BUS INIT",
    "BUS ERROR", "CAN ERROR", "DATA ERROR", "BUFFER FULL", "ERROR", "?",
)


class ElmError(RuntimeError):
    """The adapter answered, but not with usable vehicle data."""


class NoDataError(ElmError):
    """The ECU declined to answer — usually an unsupported PID or service."""


def available_ports() -> list[tuple[str, str]]:
    """Every serial port this machine can see, as (device, description)."""
    if list_ports is None:
        return []
    return [(p.device, p.description or "") for p in list_ports.comports()]


class Elm327:
    """Minimal ELM327 client: bring-up, raw commands, and reply cleaning."""

    def __init__(self, port: str, baud: int = DEFAULT_BAUD, timeout: float = 5.0):
        if serial is None:
            raise RuntimeError(
                "pyserial is not installed.\n"
                "  .venv/bin/pip install -r requirements.txt"
            )
        self.port_name = port
        self.baud = baud
        self.timeout = timeout
        self.ser = None
        self.adapter_id = ""
        self.protocol = ""

    # -- lifecycle ---------------------------------------------------------

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
        """Standard bring-up. Adapter configuration only — nothing reaches the ECU."""
        for command, description in (
            ("ATZ",   "reset"),
            ("ATE0",  "echo off"),
            ("ATL0",  "linefeeds off"),
            ("ATS0",  "spaces off"),
            ("ATH0",  "headers off"),
            ("ATAT1", "adaptive timing"),
            ("ATSP0", "auto protocol"),
        ):
            reply = self.command(command)
            log.debug("%-6s (%s) -> %s", command, description, reply)
            time.sleep(0.1)

        self.adapter_id = self.command("ATI")
        self.protocol = self.command("ATDP")
        log.info("adapter: %s", self.adapter_id or "unknown")
        log.info("protocol: %s", self.protocol or "unknown")

    # -- raw I/O -----------------------------------------------------------

    def command(self, cmd: str) -> str:
        """Send a raw command; return the reply text with the prompt stripped."""
        if not self.ser:
            raise ElmError("serial port is not open")
        self.ser.reset_input_buffer()
        self.ser.write((cmd + "\r").encode("ascii"))
        self.ser.flush()
        return self._read_until_prompt()

    def _read_until_prompt(self) -> str:
        buf = bytearray()
        deadline = time.monotonic() + self.timeout
        while time.monotonic() < deadline:
            chunk = self.ser.read(self.ser.in_waiting or 1)
            if chunk:
                buf.extend(chunk)
                if PROMPT in buf:
                    break
            else:
                time.sleep(0.01)
        return buf.replace(PROMPT, b"").decode("ascii", errors="replace").strip()

    def set_header(self, header: str | None) -> None:
        """Address a specific module (e.g. '7E0' for the PCM), or None for default."""
        self.command(f"ATSH{header}" if header else "ATSH7DF")


# ---------------------------------------------------------------------------
# Reply cleaning
# ---------------------------------------------------------------------------

_FRAME_INDEX_RE = re.compile(r"^[0-9A-F]:")
_LENGTH_HEADER_RE = re.compile(r"^[0-9A-F]{3}$")


def clean_hex(raw: str) -> str:
    """
    Reduce an ELM327 reply to one uninterrupted hex string.

    Handles the single-frame form ("410C1AF8") and the multi-frame form the
    adapter prints with headers off, where a length header precedes lines
    tagged "0:", "1:" and so on. Raises on replies that carry no data.
    """
    text = raw.upper()
    for marker in NON_DATA_REPLIES:
        if marker in text:
            if marker in ("NO DATA", "?"):
                raise NoDataError(f"adapter replied {marker!r}")
            raise ElmError(f"adapter replied {marker!r}")

    parts: list[str] = []
    for line in re.split(r"[\r\n]+", text):
        line = line.strip().replace(" ", "")
        if not line or _LENGTH_HEADER_RE.fullmatch(line):
            continue
        parts.append(_FRAME_INDEX_RE.sub("", line))

    payload = "".join(parts)
    if not payload or not re.fullmatch(r"[0-9A-F]+", payload):
        raise ElmError(f"unparseable reply {raw!r}")
    return payload


def to_bytes(payload: str) -> list[int]:
    """Hex string to byte values."""
    return [int(payload[i:i + 2], 16) for i in range(0, len(payload) - 1, 2)]
