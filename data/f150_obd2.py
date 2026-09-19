"""EVERYTHING THE SCAN APP READS THAT THE LIVE LINK COULD NOT.

THE GAP THIS CLOSES
-------------------
The car link read LIVE SENSOR DATA and nothing else.  That is one of the six
things the scan app does.  A scan app also reads:

    fault codes           stored (service 03), pending (07), PERMANENT (0A)
    freeze frame          service 02 - the sensor snapshot taken when a code set
    monitor test results  service 06 - the on-board monitors' own numbers,
                          WITH the limits the module judges them against
    vehicle information   service 09 - VIN, calibration identifier, calibration
                          verification number
    readiness             service 01 PID 01 - lamp state, stored-code count, and
                          which monitors have finished

None of that was reachable.  This module adds all of it.

THE ONE THAT MATTERS MOST HERE IS SERVICE 06
--------------------------------------------
`MONITOR_MISFIRE_CYLINDER_1` .. `_6` are CUMULATIVE COUNTERS kept by the module,
not an instantaneous channel.  The whole difficulty with capture 1 in
docs/IDLE-LOG-LIST.md is that the live misfire channel has to be SAMPLED AT THE
MOMENT OF AN EVENT - 53 scattered samples over three sessions almost certainly
never landed on one, which is why thirty minutes of logging was being asked for.

A counter does not have to be caught in the act.  It is read once and reports
what already happened, per cylinder, with the module's own pass/fail limits
attached.

SERVICE 0A DOES NOT EXIST IN python-obd
---------------------------------------
Verified against 0.7.3 on 2026-09-19: its command table holds services 01, 02,
03, 04, 06, 07 and 09 and stops.  Permanent codes are built here by hand, the
same way service 0x22 is.  They matter because a permanent code CANNOT be
cleared by a scan tool - it clears only when the module's own monitor passes.
Anything that survived a previous clear is still visible here.

READ-ONLY, GUARDED ON THE SERVICE BYTE
--------------------------------------
Every service in READ_SERVICES is a read.  Service 04 is refused with the rest
of the writers, by number, in f150_did.FORBIDDEN - it is the one that destroys
the freeze frame and the permanent-code history.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _repo import utf8
from f150_did import FORBIDDEN

utf8()

# Services this module is allowed to send.  All reads.
READ_SERVICES = {0x01, 0x02, 0x03, 0x06, 0x07, 0x09, 0x0A}

# Ford module addresses.  UNVERIFIED on this VIN - 7E0 is the only one this
# project has ever actually received an answer from.  A wrong header returns
# nothing rather than something wrong, so this is safe to try, but do not
# report a module as "absent" on the strength of silence from a guessed address.
MODULES = {'PCM': b'7E0', 'TCM': b'7E1'}

FREEZE_FRAME_PIDS = [
    'DTC_FREEZE_DTC', 'DTC_RPM', 'DTC_SPEED', 'DTC_ENGINE_LOAD',
    'DTC_COOLANT_TEMP', 'DTC_INTAKE_TEMP', 'DTC_MAF', 'DTC_THROTTLE_POS',
    'DTC_TIMING_ADVANCE', 'DTC_SHORT_FUEL_TRIM_1', 'DTC_LONG_FUEL_TRIM_1',
    'DTC_SHORT_FUEL_TRIM_2', 'DTC_LONG_FUEL_TRIM_2', 'DTC_FUEL_STATUS',
    'DTC_ABSOLUTE_LOAD', 'DTC_CONTROL_MODULE_VOLTAGE',
]

# Service 09 identifiers, decoded HERE and not by the library.  See
# _ascii_payload for why - python-obd's own decoder corrupts this VIN.
VEHICLE_INFO_PIDS = [('VIN', b'0902', 'ascii'),
                     ('CALIBRATION_ID', b'0904', 'ascii'),
                     ('CVN', b'0906', 'hex')]


def guard(service):
    """Refuse anything that is not a read, BY NUMBER."""
    if service in FORBIDDEN:
        raise PermissionError(
            'REFUSED: service 0x%02X (%s) can change the vehicle. '
            'This link reads only.' % (service, FORBIDDEN[service]))
    if service not in READ_SERVICES:
        raise PermissionError(
            'REFUSED: service 0x%02X is not in the read set %s'
            % (service, sorted('0x%02X' % s for s in READ_SERVICES)))


def permanent_dtc_command(obd):
    """Service 0A.  python-obd has no such command - this builds it.

    Same response shape as service 03 (`4A <count> <code pairs>`), so the
    library's own DTC decoder reads it without modification.
    """
    guard(0x0A)
    return obd.OBDCommand('PERMANENT_DTC', 'Permanent diagnostic trouble codes',
                          b'0A', 0, obd.decoders.dtc,
                          ecu=obd.protocols.ECU.ALL, fast=False)


def _ascii_payload(messages):
    """Printable bytes only.

    python-obd's own service 09 decoder CANNOT BE USED HERE.  It ends with

        d.strip(b'\x00' b'\x01' b'\x02' b'\\x00' b'\\x01' b'\\x02')

    and `bytes.strip` treats its argument as a SET OF BYTES, not as a prefix.
    That set works out to {0x00, 0x01, 0x02, '0', '1', '2', '\\', 'x'}, so the
    decoder strips the DIGITS 0, 1 and 2 off both ends of the result.

    Verified on 2026-09-19 against python-obd 0.7.3: this VIN,
    1FTMF1EM1EFC80632, comes back as FTMF1EM1EFC8063 - the leading 1 and the
    trailing 2 both eaten.  Every Ford VIN begins with 1, so this is not an
    edge case here, and the VIN is how a reading is tied to a vehicle at all.

    Keeping only printable characters drops the message-count byte and the NUL
    padding without touching the payload.
    """
    if not messages:
        return None
    data = b''.join(bytes(getattr(m, 'data', b'')) for m in messages)
    body = data[2:]                      # drop the service and identifier echo
    text = bytes(b for b in body if 0x20 <= b <= 0x7E)
    return text.decode('ascii', 'replace').strip() or None


def _hex_payload(messages):
    if not messages:
        return None
    data = b''.join(bytes(getattr(m, 'data', b'')) for m in messages)
    body = data[2:].lstrip(b'\x00')
    if body and body[0] <= 0x04:         # message-count byte
        body = body[1:]
    return body.rstrip(b'\x00').hex() or None


def info_command(obd, name, request, kind):
    """A service 09 read with a decoder that does not corrupt the payload."""
    guard(int(request[:2], 16))
    dec = _ascii_payload if kind == 'ascii' else _hex_payload
    return obd.OBDCommand(name, 'service 09 %s' % name, request, 0, dec,
                          ecu=obd.protocols.ECU.ALL, fast=False)


def _codes(resp):
    if resp is None or resp.is_null() or not resp.value:
        return []
    return [{'code': c, 'description': d} for c, d in resp.value]


def read_dtcs(obd, conn):
    """All three fault-code services, including the one that cannot be cleared."""
    out = {}
    for key, cmd in (('stored', obd.commands.GET_DTC),
                     ('pending', obd.commands.GET_CURRENT_DTC)):
        guard(int(cmd.command[:2], 16))
        out[key] = _codes(conn.query(cmd, force=True))
    out['permanent'] = _codes(conn.query(permanent_dtc_command(obd), force=True))
    out['note'] = ('permanent codes clear only when the module\'s own monitor '
                   'passes - a scan tool cannot erase them')
    return out


def read_readiness(obd, conn):
    """Service 01 PID 01: lamp, stored-code count, and which monitors finished."""
    guard(0x01)
    resp = conn.query(obd.commands.STATUS, force=True)
    if resp is None or resp.is_null() or resp.value is None:
        return {'available': False}
    s = resp.value
    out = {'available': True,
           'malfunction_indicator_lamp_on': bool(getattr(s, 'MIL', False)),
           'stored_code_count': getattr(s, 'DTC_count', None),
           'ignition_type': getattr(s, 'ignition_type', None),
           'monitors': {}}
    # vars(), NOT dir(): the library's status object carries an entry whose
    # name is None, and dir() sorts its result, so dir(s) raises TypeError.
    for name, t in vars(s).items():
        if not name or name in ('MIL', 'DTC_count', 'ignition_type'):
            continue
        if hasattr(t, 'available') and hasattr(t, 'complete'):
            out['monitors'][name] = {'supported': bool(t.available),
                                     'complete': bool(t.complete)}
    return out


def read_freeze_frame(obd, conn):
    """Service 02: the sensor snapshot the module stored when a code set.

    Empty is the NORMAL answer when no code is stored.  It is not a failure.
    """
    guard(0x02)
    out = {}
    for name in FREEZE_FRAME_PIDS:
        cmd = getattr(obd.commands, name, None)
        if cmd is None:
            continue
        r = conn.query(cmd, force=True)
        if r is not None and not r.is_null() and r.value is not None:
            out[name] = str(r.value)
    return out


def read_vehicle_info(obd, conn):
    """Service 09.  The calibration identifier is the TUNE'S FINGERPRINT.

    This truck has a custom tune.  The calibration identifier and the
    calibration verification number are what distinguish the calibration now in
    the module from the factory one, and nothing else in this project records
    them.
    """
    guard(0x09)
    out = {}
    for name, request, kind in VEHICLE_INFO_PIDS:
        r = conn.query(info_command(obd, name, request, kind), force=True)
        if r is None or r.is_null() or r.value is None:
            continue
        out[name] = str(r.value).strip()
    return out


def monitor_commands(obd, only=None):
    """Every service 06 command, or just the misfire counters."""
    names = [c.name for c in obd.commands.modes[6] if c is not None]
    names = [n for n in names if n.startswith('MONITOR_')]
    if only == 'misfire':
        names = [n for n in names if 'MISFIRE' in n]
    return names


def read_monitors(obd, conn, only=None, cylinders=6):
    """Service 06: the on-board monitors' own numbers AND their limits.

    Each test carries the value, the minimum and the maximum the module judges
    it against, so pass/fail is the MODULE'S verdict, not an interpretation
    applied here.
    """
    guard(0x06)
    out = {}
    for name in monitor_commands(obd, only):
        if 'MISFIRE_CYLINDER_' in name:
            n = int(name.rsplit('_', 1)[1])
            if n > cylinders:            # a V6 has no cylinder 7-12
                continue
        cmd = getattr(obd.commands, name, None)
        if cmd is None:
            continue
        r = conn.query(cmd, force=True)
        if r is None or r.is_null() or r.value is None:
            continue
        tests = []
        for tname, t in vars(r.value).items():
            if not tname:
                continue
            if not hasattr(t, 'value') or not hasattr(t, 'min'):
                continue
            if getattr(t, 'is_null', lambda: True)():
                continue
            tests.append({'test': t.name or tname,
                          'description': t.desc,
                          'value': str(t.value),
                          'min': str(t.min), 'max': str(t.max),
                          'passed': bool(t.passed)})
        if tests:
            out[name] = tests
    return out
