"""Mode 22 (Ford enhanced) for this truck - and the discipline that makes it safe.

THE PROBLEM THIS SOLVES
-----------------------
`python-obd` implements no mode 22, so every `[PCM]` channel in the owner's
sensor list is unreachable from the agent link: the misfire counter, the six
cylinder acceleration values, both knock sensors, A/C pressure, cylinder head
temperature, the transmission shaft speeds.  Those are most of what the
investigation still wants.

THE REASON GUESSING IS FORBIDDEN, AND IT IS A GOOD REASON
---------------------------------------------------------
`CLAUDE.md`: *"DID_REGISTRY stays empty until an entry is verified against
FORScan on this VIN.  A wrong Mode 22 address returns a plausible number rather
than an error, and that number will condemn a good part."*

That is exactly right, and it is why this module does NOT ship a table of
addresses copied from a forum.  A mode 22 response is just bytes.  Nothing in
the reply says what it means or how it is scaled, so a wrong address does not
fail - it lies.

WHAT REPLACES GUESSING: IDENTIFY EACH ADDRESS FROM THE TRUCK ITSELF
-------------------------------------------------------------------
1. SCAN.   Sweep the address space and record which addresses ANSWER.  No
           interpretation at all - just "the PCM replied" or "it did not".
2. IDENTIFY BY CORRELATION.  Log a candidate alongside a STANDARD channel whose
           meaning is already known (mode 01 engine speed, coolant, load...).
           An address carrying engine speed correlates ~1.0 with mode 01 engine
           speed.  That is proof from this truck, not from a table.
           The same regression yields the SCALE AND OFFSET empirically, with an
           r-squared that says how well it holds - so the units are measured
           too, never assumed.
3. IDENTIFY BY MANIPULATION.  Channels with no standard twin - cylinder
           acceleration, knock - cannot be correlated.  For those, predict a
           physical change FIRST, then make it: switch the air conditioning on
           and see which address steps.  The prediction is written before the
           change, which is this project's own rule.
4. GATE.   An address enters the registry only with its evidence attached: how
           it was identified, the r-squared or the manipulation, the fitted
           scale and offset, and the date.  `unverified` entries are carried
           but every reading from one is flagged.

READ-ONLY, AND NARROWER THAN THE REST OF THE LINK
--------------------------------------------------
Service 0x22 is ReadDataByIdentifier - a read by definition.  This module will
construct NOTHING ELSE.  Every other UDS service that could change the truck is
refused by name and by number, including 0x2E WriteDataByIdentifier, 0x10
DiagnosticSessionControl, 0x11 ECUReset, 0x27 SecurityAccess, 0x31
RoutineControl and 0x14 ClearDiagnosticInformation.
"""
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / 'data' / 'did_registry.json'

SERVICE = 0x22                    # ReadDataByIdentifier. The only one allowed.
PCM_HEADER = b'7E0'               # powertrain, HS-CAN
FORBIDDEN = {
    # 0x04 is the one this whole project is built around refusing: it erases
    # the freeze frame and the stored-code history, which is evidence.
    0x04: 'ClearDiagnosticInformation (OBD-II service 04)',
    0x10: 'DiagnosticSessionControl', 0x11: 'ECUReset',
    0x14: 'ClearDiagnosticInformation', 0x27: 'SecurityAccess',
    0x2E: 'WriteDataByIdentifier', 0x2F: 'InputOutputControlByIdentifier',
    0x31: 'RoutineControl', 0x34: 'RequestDownload', 0x36: 'TransferData',
    0x3E: 'TesterPresent', 0x85: 'ControlDTCSetting',
}


def _decoder(messages):
    """Return the raw payload bytes as hex, or None. No interpretation."""
    if not messages:
        return None
    data = getattr(messages[0], 'data', None)
    if not data:
        return None
    return data.hex()


def did_command(obd, did, nbytes=16, header=PCM_HEADER):
    """Build a mode 22 read for one identifier. Refuses anything but 0x22."""
    if not 0 <= did <= 0xFFFF:
        raise ValueError('identifier out of range: %r' % did)
    cmd = bytes([SERVICE]) + did.to_bytes(2, 'big')
    if cmd[0] != SERVICE:
        raise AssertionError('service byte is not 0x22')
    return obd.OBDCommand('DID_%04X' % did, 'mode 22 read %04X' % did,
                          cmd.hex().upper().encode(), nbytes, _decoder,
                          ecu=obd.protocols.ECU.ALL, fast=False, header=header)


def guard(service):
    """Raise on any service this module must never send."""
    if service in FORBIDDEN:
        raise PermissionError(
            'REFUSED: service 0x%02X (%s) can change the vehicle. This link '
            'reads only, service 0x22.' % (service, FORBIDDEN[service]))
    if service != SERVICE:
        raise PermissionError('REFUSED: only service 0x%02X is permitted' % SERVICE)


# ------------------------------------------------------------------ registry
def load_registry():
    if not REGISTRY.exists():
        return {'entries': {}, 'scans': []}
    return json.loads(REGISTRY.read_text())


def save_registry(reg):
    REGISTRY.write_text(json.dumps(reg, indent=2, sort_keys=True) + '\n')


def add_entry(reg, did, name, method, evidence, scale=1.0, offset=0.0,
              nbytes=2, byteorder='big', signed=False, verified=False):
    """Record an identification WITH the evidence that produced it.

    `verified` is never set by inference. It is set only when the evidence
    meets the gate: a correlation identification with r-squared >= 0.99 over
    at least 200 paired samples, or a manipulation whose prediction was written
    down before the change and then observed.
    """
    reg['entries']['%04X' % did] = dict(
        name=name, method=method, evidence=evidence, scale=scale, offset=offset,
        nbytes=nbytes, byteorder=byteorder, signed=signed, verified=bool(verified),
        recorded=time.strftime('%Y-%m-%d'))
    return reg


def decode(entry, hexdata):
    """Apply a registry entry's measured scale and offset to a raw reply."""
    raw = bytes.fromhex(hexdata)
    n = entry.get('nbytes', 2)
    # A mode 22 reply echoes 62 <did hi> <did lo> before the payload.
    payload = raw[3:3 + n] if len(raw) >= 3 + n else raw[-n:]
    if not payload:
        return None
    val = int.from_bytes(payload, entry.get('byteorder', 'big'),
                         signed=entry.get('signed', False))
    return val * entry.get('scale', 1.0) + entry.get('offset', 0.0)
