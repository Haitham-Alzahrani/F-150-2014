"""THE LINK AN AGENT CAN ACTUALLY DRIVE.  Daemon owns the adapter; clients ask it.

WHY THIS EXISTS AND f150_live.py DOES NOT REPLACE IT
----------------------------------------------------
`f150_live.py` reads typed commands from stdin.  A person can drive it.  An
AGENT CANNOT: every shell command an agent runs is a SEPARATE PROCESS, so the
connection dies between questions, and re-opening it means a fresh ELM327
handshake every time - seconds per reading, and the adapter renegotiating the
protocol over and over.

So this splits in two:

    serve     one long-lived process.  Owns the adapter, holds ONE handshake
              open, logs Engine RPM continuously at full rate, and listens on
              127.0.0.1 for requests.
    clients   one-shot commands - `status`, `read RPM`, `log start`, `snapshot`
              - each connects to that daemon, asks one thing, prints JSON and
              exits.  Which is exactly the shape a tool call has.

READ-ONLY, GUARDED ON WHAT A COMMAND DOES
-----------------------------------------
Modes 1, 2, 3, 6, 7 and 9 are reads and are allowed.  MODE 4 IS REFUSED.
Verified against python-obd 0.7.3: `getattr(obd.commands, 'CLEAR_DTC')` passes a
hasattr check and resolves to OBDCommand('CLEAR_DTC', ..., b'04'), and CLEAR_DTC
is in `base_commands()` so the library treats it as always supported.  A name
blocklist is not enough; the guard is on the service mode.

NO CAR?  `serve --sim` runs the whole thing against a simulated ELM327, so the
plumbing can be tested with nothing plugged in.  It is obvious in every reply:
every response carries "sim": true.
"""
import argparse
import csv
import json
import socket
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _repo import ROOT, utf8

HOST = '127.0.0.1'
PORT = 51507                     # arbitrary high port, localhost only
READ_MODES = {1, 2, 3, 6, 7, 9, 0x0A}
WRITE_MODE = 4                   # Clear DTCs and Freeze data.  Never sent.
LOG_DIR = ROOT / 'logs'

# python-obd's name -> the label the OWNER'S SENSOR LIST uses, exactly.
# Two reasons this matters more than it looks:
#   1. Every analysis tool in data/ looks channels up by these strings, so a
#      capture written with them is read by rpm_rate, idle_events, bank_offset,
#      idle_sweep, voltage_compare and check_capture with NO changes - an agent
#      capture becomes indistinguishable from a Car Scanner export.
#   2. CLAUDE.md forbids quoting a graph header or an abbreviation back to the
#      owner. Writing the sensor-list label into the file makes that automatic.
LABELS = {
    'RPM':                    'Engine RPM (rpm)',
    'SPEED':                  'Vehicle speed (km/h)',
    'COOLANT_TEMP':           'Engine coolant temperature (\u2103)',
    'INTAKE_TEMP':            'Intake air temperature (\u2103)',
    'AMBIANT_AIR_TEMP':       'Ambient air temperature (\u2103)',
    'SHORT_FUEL_TRIM_1':      'Short term fuel % trim - Bank 1 (%)',
    'SHORT_FUEL_TRIM_2':      'Short term fuel % trim - Bank 2 (%)',
    'LONG_FUEL_TRIM_1':       'Long term fuel % trim - Bank 1 (%)',
    'LONG_FUEL_TRIM_2':       'Long term fuel % trim - Bank 2 (%)',
    'TIMING_ADVANCE':         'Timing advance (\u00b0)',
    'MAF':                    'MAF air flow rate (g/sec)',
    'ENGINE_LOAD':            'Calculated engine load value (%)',
    'ABSOLUTE_LOAD':          'Absolute load value (%)',
    'THROTTLE_POS':           'Throttle position (%)',
    'BAROMETRIC_PRESSURE':    'Barometric pressure (kPa)',
    'EVAPORATIVE_PURGE':      'Commanded evaporative purge (%)',
    'COMMANDED_EQUIV_RATIO':  'Fuel/Air commanded equivalence ratio ()',
    'CONTROL_MODULE_VOLTAGE': 'Control module voltage (V)',
}


def label(name):
    return LABELS.get(name, name)


# ---------------------------------------------------------------- simulator
class SimValue:
    def __init__(self, m): self.magnitude = m
    def __str__(self): return '%.2f' % self.magnitude


class SimResponse:
    def __init__(self, v): self.value = v
    def is_null(self): return self.value is None


class SimConnection:
    """Enough of an OBD connection to exercise every path with no hardware."""
    def __init__(self):
        import random
        self._r = random.Random(1)
        self._t = time.monotonic()

    def is_connected(self): return True
    def port_name(self): return 'SIMULATED'
    def protocol_name(self): return 'ISO 15765-4 CAN (11 bit, 500 kbaud) [SIM]'

    @property
    def supported_commands(self):
        import obd_shim as _s
        return _s.SUPPORTED

    def supports(self, cmd): return cmd.name not in ('AMBIANT_AIR_TEMP',)

    # Three mode 22 identifiers answer, and their scaling is DELIBERATELY not
    # round.  Nothing tells the discovery tools what it is - they have to
    # recover it by regression, which is the whole point of the exercise.
    AC_ON = False
    SWEEP = False
    CODES = False                # rehearse the fault-code path on demand
    MISFIRE_CLEAN = True         # emit the archived 2026-09-05 pattern

    def _did(self, ident):
        import math
        t = time.monotonic() - self._t
        rpm = 652 + 9 * math.sin(2 * math.pi * 0.33 * t) + self._r.gauss(0, 3)
        if SimConnection.SWEEP:            # a simulated throttle sweep
            rpm += 1200 * (1 + math.sin(2 * math.pi * 0.05 * t))
        if ident == 0x1100:                     # engine speed, quarter-rpm
            return int(round(rpm * 4)).to_bytes(2, 'big')
        if ident == 0x1173:                     # cylinder 4 accel, signed, /1024
            return (int(round(self._r.gauss(-0.03, 0.02) * 1024))
                    & 0xFFFF).to_bytes(2, 'big')
        if ident == 0x11A6:                     # A/C pressure, kPa * 8
            base = 1300 if SimConnection.AC_ON else 250
            return int(round((base + self._r.gauss(0, 20)) * 8)).to_bytes(2, 'big')
        return None

    def _msg(self, hexdata):
        """One synthetic CAN message, fed through the REAL library decoder.

        Faking the DECODED value would test nothing - the decode is most of
        what these services are.  Building the bytes the truck would send and
        letting python-obd parse them exercises the actual path.
        """
        from obd.protocols.protocol import Message, ECU
        m = Message([])
        m.data = bytes.fromhex(hexdata)
        m.ecu = ECU.ENGINE
        return m

    def _service(self, cmd):
        """Synthetic answers for services 02, 03, 06, 07, 09 and 0A."""
        name = getattr(cmd, 'name', '')
        codes = SimConnection.CODES
        if name == 'GET_DTC':
            return self._msg('4301' + '0316') if codes else self._msg('4300')
        if name == 'GET_CURRENT_DTC':
            return self._msg('4700')
        if name == 'PERMANENT_DTC':
            return self._msg('4A01' + '0420') if codes else self._msg('4A00')
        if name == 'STATUS':
            # malfunction lamp off, no stored codes, spark ignition
            return self._msg('4101' + ('8107E5E5' if codes else '0007E5E5'))
        if name == 'VIN':
            return self._msg('490201' + '1FTMF1EM1EFC80632'.encode().hex())
        if name == 'CALIBRATION_ID':
            return self._msg('490401' + b'CDE1104-SIMTUNE'.hex() + '00')
        if name == 'CVN':
            return self._msg('490601' + '1A2B3C4D')
        if name.startswith('DTC_') and codes:
            # Service 02 answers only while a code is stored, which is exactly
            # what a freeze frame is: the snapshot taken when one set.
            pid = bytes(cmd.command)[2:4].decode()
            body = {'0C': '0C5E',      # 791.5 rpm
                    '05': '5A',        # 90 C coolant
                    '04': '4D',        # 30 % load
                    '06': '85', '07': '7E',
                    '0E': '9A'}.get(pid)
            nbytes = max(0, getattr(cmd, 'bytes', 4) - 2)
            if body is None:
                body = '00' * nbytes
            return self._msg('42' + pid + body)
        if name.startswith('MONITOR_MISFIRE'):
            mid = int(bytes(cmd.command)[2:4], 16)
            cyl = mid - 0xA1                    # MID A2 is cylinder 1
            if SimConnection.MISFIRE_CLEAN:
                # the pattern actually archived on 2026-09-05: zero everywhere
                # except a single count on cylinders 4 and 6
                ewma = 0
                cnt = {4: 2, 6: 1}.get(cyl, 0)
            else:
                ewma = 0 if cyl <= 0 else self._r.randint(0, 3)
                cnt = 0 if cyl <= 0 else self._r.randint(0, 60)
            # two 9-byte blocks: TID 0x0B (EWMA) then TID 0x0C (counts),
            # scaling 0x24 = raw counts, each with value / min / max
            return self._msg('46%02X0B24%04X0000FFFF%02X0C24%04X0000FFFF'
                             % (mid, ewma, mid, cnt))
        if name.startswith('MONITOR_') and codes:
            mid = int(bytes(cmd.command)[2:4], 16)
            return self._msg('46%02X010124000000FFFF' % mid)
        return None

    def query(self, cmd, force=False):
        time.sleep(0.030)                                   # the 33 Hz ceiling
        raw = getattr(cmd, 'command', None)
        if (getattr(cmd, 'name', '') == 'STATUS'
                or (raw and bytes(raw)[:2] in (b'02', b'03', b'06',
                                               b'07', b'09', b'0A'))):
            m = self._service(cmd)
            if m is None:
                return SimResponse(None)
            return SimResponse(cmd([m]).value)
        if raw and bytes(raw).startswith(b'22'):
            ident = int(bytes(raw)[2:6], 16)
            pay = self._did(ident)
            if pay is None:
                return SimResponse(None)        # negative response / no answer
            msg = type('M', (), {'data': bytes([0x62])
                                 + ident.to_bytes(2, 'big') + pay})()
            return SimResponse(cmd.decode([msg]))
        n = getattr(cmd, 'name', str(cmd))
        if n == 'RPM':
            # idle with a slow 0.3 Hz wander, like the real thing
            t = time.monotonic() - self._t
            import math
            rpm = (652 + 9 * math.sin(2 * math.pi * 0.33 * t)
                   + self._r.gauss(0, 3))
            if SimConnection.SWEEP:
                rpm += 1200 * (1 + math.sin(2 * math.pi * 0.05 * t))
            return SimResponse(SimValue(rpm))
        if n == 'GET_DTC':
            return SimResponse([])
        if n in ('ELM_VOLTAGE', 'CONTROL_MODULE_VOLTAGE'):
            # the archived idle median on this truck, not a random number -
            # a rehearsal that prints 44 V teaches the wrong reflex
            return SimResponse(SimValue(12.67 + self._r.gauss(0, 0.05)))
        return SimResponse(SimValue(round(self._r.uniform(1, 90), 2)))

    def close(self): pass


# ---------------------------------------------------------------- the daemon
class Daemon:
    def __init__(self, port, baud, sim):
        self.sim = sim
        self.port, self.baud = port, baud
        self.conn = None
        self.err = None
        self.lock = threading.Lock()
        self.stop = threading.Event()
        self._logging = False
        self._fh = self._writer = None
        self._t0 = None
        self._wall0 = None           # wall-clock anchor, set with _t0
        self._n = 0
        self._last = None
        self._channels = ['RPM']
        self._per = {}

    # -- connect ---------------------------------------------------------
    def connect(self):
        if self.sim:
            self.conn = SimConnection()
            return True
        try:
            import obd
        except ImportError:
            self.err = 'python-obd is not installed. pip install obd'
            return False
        self._obd = obd
        try:
            self.conn = obd.OBD(self.port, baudrate=self.baud) if self.port else obd.OBD()
        except Exception as exc:                                  # noqa: BLE001
            self.err = '%s: %s' % (type(exc).__name__, exc)
            return False
        if not self.conn.is_connected():
            self.err = ('adapter did not answer. Ignition ON? correct port? '
                        'A Bluetooth Low Energy adapter presents no serial port '
                        'and cannot work here.')
            return False
        return True

    def cmd(self, name):
        if self.sim:
            c = type('C', (), {'name': name, 'mode': 4 if name == 'CLEAR_DTC' else 1})()
            return c
        if not self._obd.commands.has_name(name):
            return None
        return getattr(self._obd.commands, name, None)

    # -- the sampling loop ------------------------------------------------
    def run(self):
        turn = 0
        while not self.stop.is_set():
            if not self._logging:
                time.sleep(0.05)
                continue
            # Round robin, one channel per pass.  Each row carries the single
            # channel just sampled and leaves the rest blank - which is exactly
            # what Car Scanner writes, and what carscanner_lib expects: every
            # channel keeps its OWN true sample times and nothing is forward
            # filled.  Polling N channels divides the rate by N, the same
            # arithmetic as the tiles law on the phone.
            name = self._channels[turn % len(self._channels)]
            turn += 1
            c = self.cmd(name)
            if c is None:
                continue
            with self.lock:
                r = self.conn.query(c)
            if r.is_null():
                continue
            v = getattr(r.value, 'magnitude', r.value)
            try:
                v = float(v)
            except (TypeError, ValueError):
                continue
            if name == 'RPM':
                self._last = v
            el = time.monotonic() - self._t0
            # ONE CLOCK.  This previously took the seconds from
            # time.localtime() and the fraction from (el % 1) - two
            # unsynchronised clocks - so the written time could jump BACKWARDS
            # by up to 999 ms inside one second, and any interval computed from
            # the file was wrong.  Reproduced 2026-09-19: elapsed 0.980 -> 1.040
            # wrote ...18.980 -> ...18.040.  The wall clock is now an ANCHOR
            # taken once at log start; absolute time is anchor + monotonic
            # offset, so seconds and fraction always come from the same clock.
            wall = self._wall0 + el
            row = {'time': time.strftime('%H:%M:%S', time.localtime(wall))
                           + ('%.3f' % (wall % 1))[1:]}
            row[label(name)] = '%.4f' % v
            self._writer.writerow(row)
            self._n += 1
            self._per[name] = self._per.get(name, 0) + 1
            if self._n % 200 == 0:
                self._fh.flush()

    # -- request handlers -------------------------------------------------
    def handle(self, req):
        op = req.get('op')
        if op == 'status':
            el = (time.monotonic() - self._t0) if self._logging else 0
            return {'ok': True, 'connected': True, 'sim': self.sim,
                    'interface': self.conn.port_name(),
                    'protocol': self.conn.protocol_name(),
                    'logging': self._logging, 'samples': self._n,
                    'seconds': round(el, 1),
                    'hz': round(self._n / el, 1) if el else 0,
                    'last_rpm': self._last}
        if op == 'read':
            return self.read(req['name'].upper())
        if op == 'snapshot':
            out = {}
            for n in req.get('names') or ['RPM', 'COOLANT_TEMP', 'ENGINE_LOAD',
                                          'SHORT_FUEL_TRIM_1', 'SHORT_FUEL_TRIM_2',
                                          'LONG_FUEL_TRIM_1', 'LONG_FUEL_TRIM_2',
                                          'TIMING_ADVANCE', 'MAF',
                                          'CONTROL_MODULE_VOLTAGE', 'ELM_VOLTAGE']:
                out[n] = self.read(n)
            return {'ok': True, 'sim': self.sim, 'snapshot': out}
        if op == 'log':
            return self.log(req.get('action'), req.get('label', 'idle'),
                            req.get('channels'))
        if op == 'sim':
            if not self.sim:
                return {'ok': False, 'error': 'not a simulated link'}
            what, on = req.get('what'), bool(req.get('on'))
            if what == 'ac':
                SimConnection.AC_ON = on
            elif what == 'sweep':
                SimConnection.SWEEP = on
            elif what == 'codes':
                SimConnection.CODES = on
            elif what == 'misfire-clean':
                SimConnection.MISFIRE_CLEAN = on
            else:
                return {'ok': False,
                        'error': 'sim what must be ac, sweep or codes'}
            return {'ok': True, 'sim': True, what: on}
        if op == 'did':
            return self.did(int(req['did']))
        if op in ('dtc', 'readiness', 'freeze', 'monitors', 'vehicle'):
            return self.service(op, req)
        if op == 'healthcheck':
            return self.healthcheck()
        if op == 'list':
            return {'ok': True, 'sim': self.sim,
                    'supported': sorted(c.name for c in self.conn.supported_commands),
                    'note': 'python-obd implements no mode 22, so NO [PCM] channel '
                            'appears here. Library reach, not truck capability.'}
        if op == 'stop':
            self.stop.set()
            return {'ok': True, 'stopping': True}
        return {'ok': False, 'error': 'unknown op %r' % op}

    # -- the services the live link used to be missing ---------------------
    def service(self, op, req):
        """Fault codes, freeze frame, monitor tests, vehicle info, readiness."""
        import obd
        import f150_obd2 as S
        try:
            if op == 'dtc':
                out = S.read_dtcs(obd, self.conn)
            elif op == 'readiness':
                out = S.read_readiness(obd, self.conn)
            elif op == 'freeze':
                out = S.read_freeze_frame(obd, self.conn)
                if not out:
                    out = {'empty': True, 'note': 'no freeze frame stored - '
                           'this is the normal answer with no stored code'}
            elif op == 'vehicle':
                out = S.read_vehicle_info(obd, self.conn)
            else:
                out = S.read_monitors(obd, self.conn, req.get('only'))
                if not out:
                    out = {'empty': True, 'note': 'no monitor returned a '
                           'completed test - monitors report only after their '
                           'own drive cycle has run'}
        except PermissionError as e:
            return {'ok': False, 'refused': str(e)}
        return {'ok': True, 'sim': self.sim, op: out}

    def healthcheck(self):
        """Everything a scan tool reads in one pass, in one call."""
        import obd
        import f150_obd2 as S
        out = {}
        for name, fn in (('vehicle', S.read_vehicle_info),
                         ('readiness', S.read_readiness),
                         ('dtc', S.read_dtcs),
                         ('freeze', S.read_freeze_frame),
                         ('monitors', S.read_monitors)):
            try:
                out[name] = fn(obd, self.conn)
            except PermissionError as e:
                out[name] = {'refused': str(e)}
            except Exception as e:                 # one dead service must not
                out[name] = {'error': repr(e)}     # lose the other four
        return {'ok': True, 'sim': self.sim, 'healthcheck': out}

    def did(self, ident):
        """Mode 22 read. Service 0x22 ONLY - see data/f150_did.py for why."""
        import f150_did as D
        D.guard(D.SERVICE)                     # refuses every write service
        if self.sim:
            import obd as _o
            cmd = D.did_command(_o, ident)
        else:
            cmd = D.did_command(self._obd, ident)
        with self.lock:
            r = self.conn.query(cmd, force=True)
        if r.is_null() or not r.value:
            return {'ok': False, 'did': '%04X' % ident,
                    'error': 'no answer (the PCM has no such identifier, or '
                             'refused it)', 'sim': self.sim}
        hexdata = str(r.value)
        out = {'ok': True, 'did': '%04X' % ident, 'hex': hexdata, 'sim': self.sim}
        # If it has been identified ON THIS VIN, decode it - and say so.
        reg = D.load_registry()
        e = reg.get('entries', {}).get('%04X' % ident)
        if e:
            out['name'] = e['name']
            out['value'] = D.decode(e, hexdata)
            out['verified'] = e['verified']
            if not e['verified']:
                out['warning'] = ('UNVERIFIED identification - this number may '
                                  'be meaningless. See data/did_registry.json.')
        else:
            out['note'] = ('not identified on this VIN. Raw bytes only - do not '
                           'interpret. Run data/did_scan.py identify.')
        return out

    def read(self, name):
        c = self.cmd(name)
        if c is None:
            return {'ok': False, 'sensor': name, 'error': 'python-obd has no command by that name'}
        if c.mode == WRITE_MODE:
            return {'ok': False, 'sensor': name,
                    'error': 'REFUSED: OBD service %d erases codes and freeze frame. '
                             'This link is read-only.' % WRITE_MODE}
        if c.mode not in READ_MODES:
            return {'ok': False, 'sensor': name, 'error': 'REFUSED: service %s is not a read mode' % c.mode}
        with self.lock:
            r = self.conn.query(c)
        if r.is_null():
            return {'ok': False, 'sensor': name, 'error': 'no answer / not supported'}
        return {'ok': True, 'sensor': name, 'value': str(r.value), 'sim': self.sim}

    def log(self, action, lbl, channels=None):
        if action == 'start':
            if self._logging:
                return {'ok': False, 'error': 'already recording', 'file': str(self._fh.name)}
            chans = [c.upper() for c in (channels or ['RPM'])]
            bad = [c for c in chans if self.cmd(c) is None]
            if bad:
                return {'ok': False, 'error': 'unknown channel(s): %s' % ', '.join(bad)}
            ref = [c for c in chans if self.cmd(c).mode == WRITE_MODE]
            if ref:
                return {'ok': False,
                        'error': 'REFUSED: %s is OBD service %d' % (ref[0], WRITE_MODE)}
            LOG_DIR.mkdir(exist_ok=True)
            name = '%s-%s.csv' % (datetime.now().strftime('%Y-%m-%d_%H-%M-%S'),
                                  lbl.replace(' ', '-'))
            self._fh = open(LOG_DIR / name, 'w', newline='', encoding='utf-8')
            self._writer = csv.DictWriter(
                self._fh, fieldnames=['time'] + [label(c) for c in chans],
                restval='', extrasaction='ignore')
            self._writer.writeheader()
            self._channels = chans
            self._t0 = time.monotonic(); self._wall0 = time.time()
            self._n = 0; self._per = {}
            self._logging = True
            warn = None
            if len(chans) > 3:
                warn = ('%d channels divides the rate by %d. Engine-speed questions '
                        '- orders, rate of change, event shape - need 25 Hz or '
                        'better, so use two.' % (len(chans), len(chans)))
            return {'ok': True, 'recording': str(LOG_DIR / name),
                    'channels': [label(c) for c in chans], 'warning': warn,
                    'sim': self.sim}
        if action == 'stop':
            if not self._logging:
                return {'ok': False, 'error': 'not recording'}
            el = time.monotonic() - self._t0
            self._logging = False
            path = self._fh.name
            self._fh.close()
            return {'ok': True, 'file': path, 'samples': self._n,
                    'seconds': round(el, 1),
                    'total_hz': round(self._n / el, 1) if el else 0,
                    'per_channel_hz': {label(k): round(v / el, 1)
                                       for k, v in self._per.items()},
                    'next': 'python data/check_capture.py "%s"' % path,
                    'sim': self.sim}
        return {'ok': False, 'error': 'log action must be start or stop'}


def serve(a):
    d = Daemon(a.port, a.baud, a.sim)
    if not d.connect():
        print(json.dumps({'ok': False, 'error': d.err}), flush=True)
        return 1
    threading.Thread(target=d.run, daemon=True).start()
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((HOST, a.listen))
    srv.listen(8)
    srv.settimeout(0.5)
    print(json.dumps({'ok': True, 'serving': '%s:%d' % (HOST, a.listen),
                      'interface': d.conn.port_name(),
                      'protocol': d.conn.protocol_name(), 'sim': a.sim}), flush=True)
    while not d.stop.is_set():
        try:
            c, _ = srv.accept()
        except socket.timeout:
            continue
        with c:
            try:
                data = c.makefile().readline()
                rep = d.handle(json.loads(data))
            except Exception as exc:                              # noqa: BLE001
                rep = {'ok': False, 'error': '%s: %s' % (type(exc).__name__, exc)}
            c.sendall((json.dumps(rep) + '\n').encode())
    srv.close()
    d.conn.close()
    print(json.dumps({'ok': True, 'stopped': True}), flush=True)
    return 0


def client(req, listen):
    try:
        with socket.create_connection((HOST, listen), timeout=15) as s:
            s.sendall((json.dumps(req) + '\n').encode())
            return json.loads(s.makefile().readline())
    except ConnectionRefusedError:
        return {'ok': False, 'error': 'no daemon on %s:%d. Start one:\n'
                '  python data/f150_agent.py serve --port COM5\n'
                '  (or --sim to test with no car)' % (HOST, listen)}
    except Exception as exc:                                      # noqa: BLE001
        return {'ok': False, 'error': '%s: %s' % (type(exc).__name__, exc)}


def list_ports():
    try:
        from serial.tools import list_ports
    except ImportError:
        return []
    return [(p.device, p.description or '') for p in list_ports.comports()]


def main():
    utf8()
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--listen', type=int, default=PORT)
    sub = ap.add_subparsers(dest='op', required=True)

    s = sub.add_parser('serve', help='run the daemon that owns the adapter')
    s.add_argument('--port', default=None, help='COM5, /dev/ttyUSB0, ... omit to auto-detect')
    s.add_argument('--baud', type=int, default=115200)
    s.add_argument('--sim', action='store_true', help='simulated adapter, no hardware')

    sub.add_parser('status', help='is the link up, is it logging, at what rate')
    sub.add_parser('ports', help='list serial ports')
    sub.add_parser('list', help='what python-obd can reach on this truck')
    sub.add_parser('stop', help='shut the daemon down')
    dd = sub.add_parser('did', help='mode 22 read by identifier (read-only)')
    dd.add_argument('ident', help='hex, e.g. 0x1100')
    sub.add_parser('dtc', help='fault codes: stored, pending and permanent')
    sub.add_parser('readiness', help='lamp, stored-code count, monitor status')
    sub.add_parser('freeze', help='the sensor snapshot stored when a code set')
    sub.add_parser('vehicle', help='VIN, calibration identifier, verification')
    mo = sub.add_parser('monitors', help='service 06 on-board monitor results')
    mo.add_argument('--only', choices=['misfire'], help='misfire counters only')
    sub.add_parser('healthcheck', help='every service above, in one pass')
    sm = sub.add_parser('sim', help='simulated manipulations, --sim links only')
    sm.add_argument('what', choices=['ac', 'sweep', 'codes', 'misfire-clean'])
    sm.add_argument('state', choices=['on', 'off'])
    r = sub.add_parser('read', help='one reading'); r.add_argument('name')
    sn = sub.add_parser('snapshot', help='a set of readings in one call')
    sn.add_argument('names', nargs='*')
    lg = sub.add_parser('log', help='continuous multi-channel recording')
    lg.add_argument('action', choices=['start', 'stop'])
    lg.add_argument('label', nargs='?', default='idle')
    lg.add_argument('channels', nargs='*',
                    help='python-obd names, default RPM. Each extra channel '
                         'divides the rate, exactly like tiles on the phone.')

    a = ap.parse_args()
    if a.op == 'serve':
        return serve(a)
    if a.op == 'ports':
        p = list_ports()
        print(json.dumps({'ok': True, 'ports': [{'device': d, 'description': s} for d, s in p],
                          'note': 'BLE adapters present no serial port and cannot be used.'}))
        return 0
    req = {'op': a.op}
    if a.op == 'did':
        req['did'] = int(a.ident, 0)
    if a.op == 'sim':
        req['what'], req['on'] = a.what, a.state == 'on'
    if a.op == 'monitors':
        req['only'] = a.only
    if a.op == 'read':
        req['name'] = a.name
    if a.op == 'snapshot':
        req['names'] = a.names or None
    if a.op == 'log':
        req['action'], req['label'] = a.action, a.label
        req['channels'] = a.channels or None
    rep = client(req, a.listen)
    print(json.dumps(rep, indent=None))
    return 0 if rep.get('ok') else 1


if __name__ == '__main__':
    raise SystemExit(main())
