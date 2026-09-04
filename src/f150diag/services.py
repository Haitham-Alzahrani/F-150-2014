"""
Diagnostic services on top of the ELM327 transport.

Implements the read-only J1979 services a scan tool uses:

    01  live data                     09  vehicle information (VIN, CAL IDs)
    03  stored DTCs                   0A  permanent DTCs
    06  on-board monitor results      22  ReadDataByIdentifier (manufacturer)
    07  pending DTCs

Service 04 (clear codes) is deliberately absent. Clearing wipes the freeze
frame and the permanent-code history that this truck's diagnosis depends on.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from .pids import Pid, BY_CODE
from .transport import Elm327, ElmError, NoDataError, clean_hex, to_bytes

log = logging.getLogger("f150diag.services")


# ---------------------------------------------------------------------------
# Service 01 — live data
# ---------------------------------------------------------------------------

def read_pid(elm: Elm327, pid: Pid) -> float | None:
    """One Mode 01 parameter. None when the ECU will not answer."""
    try:
        payload = clean_hex(elm.command(pid.request))
    except NoDataError:
        return None
    except ElmError as exc:
        log.debug("%s: %s", pid.name, exc)
        return None

    marker = f"41{pid.code}"
    start = payload.find(marker)
    if start < 0:
        log.debug("%s: no %s in %s", pid.name, marker, payload)
        return None

    body = payload[start + len(marker):]
    if len(body) < pid.nbytes * 2:
        log.debug("%s: short reply %s", pid.name, body)
        return None

    data = to_bytes(body[:pid.nbytes * 2])
    try:
        return round(float(pid.decode(data)), 3)
    except (IndexError, ValueError, TypeError, ZeroDivisionError) as exc:
        log.warning("%s: cannot decode %s (%s)", pid.name, data, exc)
        return None


def supported_pids(elm: Elm327) -> dict[str, bool]:
    """
    Walk the supported-PID bitmaps (0100, 0120, 0140, ...).

    Returns {pid_code: supported}. This is how you find out what the vehicle
    actually implements instead of assuming — it is the cheapest and most
    honest first request of any session.
    """
    found: dict[str, bool] = {}
    base = 0x00
    while base <= 0xC0:
        code = f"{base:02X}"
        try:
            payload = clean_hex(elm.command(f"01{code}"))
        except ElmError:
            break

        marker = f"41{code}"
        start = payload.find(marker)
        if start < 0:
            break
        body = payload[start + len(marker):start + len(marker) + 8]
        if len(body) < 8:
            break

        bits = int(body, 16)
        for i in range(32):
            pid_num = base + i + 1
            supported = bool(bits & (1 << (31 - i)))
            found[f"{pid_num:02X}"] = supported

        if not (bits & 1):          # bit 0 = "next bitmap is supported"
            break
        base += 0x20
    return found


def supported_names(elm: Elm327) -> tuple[list[str], list[str]]:
    """Split this package's known PIDs into (supported, unsupported) names."""
    table = supported_pids(elm)
    yes, no = [], []
    for code, pid in BY_CODE.items():
        (yes if table.get(code) else no).append(pid.name)
    return sorted(yes), sorted(no)


# ---------------------------------------------------------------------------
# Services 03 / 07 / 0A — trouble codes
# ---------------------------------------------------------------------------

_DTC_LETTER = ("P", "C", "B", "U")


def decode_dtc(hi: int, lo: int) -> str:
    """Two raw bytes to the familiar five-character code."""
    letter = _DTC_LETTER[(hi >> 6) & 0x03]
    return f"{letter}{(hi >> 4) & 0x03}{hi & 0x0F:X}{lo >> 4:X}{lo & 0x0F:X}"


def _read_dtcs(elm: Elm327, service: str, reply: str) -> list[str]:
    try:
        payload = clean_hex(elm.command(service))
    except NoDataError:
        return []
    except ElmError as exc:
        log.debug("service %s: %s", service, exc)
        return []

    start = payload.find(reply)
    if start < 0:
        return []
    body = payload[start + len(reply):]

    # CAN replies lead with a count byte; ignore it and read pairs.
    data = to_bytes(body)
    if data and len(data) % 2 == 1:
        data = data[1:]

    codes: list[str] = []
    for i in range(0, len(data) - 1, 2):
        hi, lo = data[i], data[i + 1]
        if hi == 0 and lo == 0:
            continue
        codes.append(decode_dtc(hi, lo))
    return codes


def stored_dtcs(elm: Elm327) -> list[str]:
    """Service 03 — confirmed codes. Wiped by a battery disconnect."""
    return _read_dtcs(elm, "03", "43")


def pending_dtcs(elm: Elm327) -> list[str]:
    """Service 07 — one failed drive cycle, no lamp yet. Also wiped."""
    return _read_dtcs(elm, "07", "47")


def permanent_dtcs(elm: Elm327) -> list[str]:
    """
    Service 0A — permanent codes.

    These survive a battery disconnect and a scan-tool clear. The ECU erases
    them only after its own monitors pass. On a vehicle whose history has been
    cleared, this is the only surviving record.
    """
    return _read_dtcs(elm, "0A", "4A")


# ---------------------------------------------------------------------------
# Service 06 — on-board monitor test results
# ---------------------------------------------------------------------------

@dataclass
class MonitorTest:
    mid: int                 # monitor id
    tid: int                 # test id
    uas: int                 # unit and scaling id
    value: int
    min_limit: int
    max_limit: int

    @property
    def passed(self) -> bool:
        return self.min_limit <= self.value <= self.max_limit

    @property
    def margin(self) -> float:
        """How close to the limit, 0..1. Low values are about to fail."""
        span = self.max_limit - self.min_limit
        if span <= 0:
            return 1.0
        nearest = min(self.value - self.min_limit, self.max_limit - self.value)
        return round(nearest / span, 3)


def monitor_tests(elm: Elm327, mid: int) -> list[MonitorTest]:
    """
    Service 06 for one monitor id. Records are 9 bytes each.

    Misfire monitors are conventionally MID 0x01-0x0A (0x01 = general,
    0x02.. = per cylinder). Confirm the mapping for this PCM before reading
    a cylinder number off a MID — it is a convention, not a guarantee.
    """
    try:
        payload = clean_hex(elm.command(f"06{mid:02X}"))
    except ElmError:
        return []

    start = payload.find("46")
    if start < 0:
        return []
    data = to_bytes(payload[start + 2:])

    out: list[MonitorTest] = []
    for i in range(0, len(data) - 8, 9):
        r = data[i:i + 9]
        out.append(MonitorTest(
            mid=r[0], tid=r[1], uas=r[2],
            value=(r[3] << 8) | r[4],
            min_limit=(r[5] << 8) | r[6],
            max_limit=(r[7] << 8) | r[8],
        ))
    return out


def misfire_monitors(elm: Elm327) -> dict[int, list[MonitorTest]]:
    """Sweep the misfire monitor id range. Empty lists mean 'nothing reported'."""
    return {mid: monitor_tests(elm, mid) for mid in range(0x01, 0x0B)}


# ---------------------------------------------------------------------------
# Service 09 — vehicle information
# ---------------------------------------------------------------------------

def vin(elm: Elm327) -> str | None:
    """Ask the vehicle for its own VIN rather than trusting the label."""
    try:
        payload = clean_hex(elm.command("0902"))
    except ElmError:
        return None
    start = payload.find("4902")
    if start < 0:
        return None
    body = to_bytes(payload[start + 4:])
    if body and body[0] == 0x01:          # message count / index byte
        body = body[1:]
    text = "".join(chr(b) for b in body if 32 <= b < 127)
    return text.strip() or None


def calibration_ids(elm: Elm327) -> list[str]:
    """Service 09 PID 04 — calibration IDs. A non-stock tune shows up here."""
    try:
        payload = clean_hex(elm.command("0904"))
    except ElmError:
        return []
    start = payload.find("4904")
    if start < 0:
        return []
    body = to_bytes(payload[start + 4:])
    if body and body[0] <= 0x08:
        body = body[1:]
    text = "".join(chr(b) if 32 <= b < 127 else " " for b in body)
    return [t for t in text.split() if t]


# ---------------------------------------------------------------------------
# Service 22 — ReadDataByIdentifier (manufacturer-specific)
# ---------------------------------------------------------------------------

@dataclass
class Did:
    """
    One manufacturer data identifier.

    `provenance` is not decoration. Ford does not publish these; every entry
    is either measured on this truck or taken from community reverse
    engineering, and the two carry very different confidence. Never let an
    unverified DID reach a diagnostic conclusion.
    """
    did: str                                  # 4 hex chars, e.g. "1E1C"
    name: str
    description: str
    unit: str = ""
    nbytes: int = 1
    scale: float = 1.0
    offset: float = 0.0
    module: str = "7E0"                       # 7E0 = PCM
    provenance: str = "unverified"            # verified | community | unverified
    notes: str = ""

    def decode(self, data: list[int]) -> float:
        raw = 0
        for b in data[:self.nbytes]:
            raw = (raw << 8) | b
        return raw * self.scale + self.offset


#: Verified DIDs go here as we confirm them on this truck. Empty is honest.
#: See docs/ENHANCED-PIDS.md for how to add one without guessing.
DID_REGISTRY: dict[str, Did] = {}


def read_did(elm: Elm327, did: Did) -> tuple[float | None, list[int]]:
    """
    Raw ReadDataByIdentifier. Returns (decoded, raw_bytes).

    Reading an identifier is a read. It cannot reprogram anything. An address
    the module does not implement simply returns a negative response.
    """
    elm.set_header(did.module)
    try:
        payload = clean_hex(elm.command(f"22{did.did}"))
    except ElmError:
        return None, []
    finally:
        elm.set_header(None)

    marker = f"62{did.did}"
    start = payload.find(marker)
    if start < 0:
        return None, []
    raw = to_bytes(payload[start + len(marker):])
    if not raw:
        return None, []
    try:
        return round(did.decode(raw), 3), raw
    except (IndexError, ValueError, TypeError):
        return None, raw


@dataclass
class Capability:
    """What this vehicle actually answers to — established, not assumed."""
    vin: str | None = None
    adapter: str = ""
    protocol: str = ""
    supported: list[str] = field(default_factory=list)
    unsupported: list[str] = field(default_factory=list)
    calibrations: list[str] = field(default_factory=list)


def survey(elm: Elm327) -> Capability:
    """Opening move of any session: ask the vehicle what it is and what it offers."""
    yes, no = supported_names(elm)
    return Capability(
        vin=vin(elm),
        adapter=elm.adapter_id,
        protocol=elm.protocol,
        supported=yes,
        unsupported=no,
        calibrations=calibration_ids(elm),
    )
