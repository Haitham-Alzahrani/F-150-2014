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
READ_MODES = {1, 2, 3, 6, 7, 9}
WRITE_MODE = 4                   # Clear DTCs and Freeze data.  Never sent.
LOG_DIR = ROOT / 'logs'


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

    def query(self, cmd):
        time.sleep(0.030)                                   # the 33 Hz ceiling
        n = getattr(cmd, 'name', str(cmd))
        if n == 'RPM':
            # idle with a slow 0.3 Hz wander, like the real thing
            t = time.monotonic() - self._t
            import math
            return SimResponse(SimValue(652 + 9 * math.sin(2 * math.pi * 0.33 * t)
                                        + self._r.gauss(0, 3)))
        if n == 'GET_DTC':
            return SimResponse([])
        if n == 'ELM_VOLTAGE':
            return SimResponse(SimValue(12.7))
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
        self._n = 0
        self._last = None

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
        while not self.stop.is_set():
            if self._logging:
                with self.lock:
                    r = self.conn.query(self.cmd('RPM'))
                if not r.is_null():
                    v = r.value.magnitude
                    self._last = v
                    self._writer.writerow({'elapsed_s': '%.4f' % (time.monotonic() - self._t0),
                                           'rpm': '%.2f' % v})
                    self._n += 1
                    if self._n % 200 == 0:
                        self._fh.flush()
            else:
                time.sleep(0.05)

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
            return self.log(req.get('action'), req.get('label', 'idle'))
        if op == 'list':
            return {'ok': True, 'sim': self.sim,
                    'supported': sorted(c.name for c in self.conn.supported_commands),
                    'note': 'python-obd implements no mode 22, so NO [PCM] channel '
                            'appears here. Library reach, not truck capability.'}
        if op == 'stop':
            self.stop.set()
            return {'ok': True, 'stopping': True}
        return {'ok': False, 'error': 'unknown op %r' % op}

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

    def log(self, action, label):
        if action == 'start':
            if self._logging:
                return {'ok': False, 'error': 'already recording', 'file': str(self._fh.name)}
            LOG_DIR.mkdir(exist_ok=True)
            name = '%s-%s.csv' % (datetime.now().strftime('%Y-%m-%d_%H-%M-%S'),
                                  label.replace(' ', '-'))
            self._fh = open(LOG_DIR / name, 'w', newline='')
            self._writer = csv.DictWriter(self._fh, fieldnames=['elapsed_s', 'rpm'])
            self._writer.writeheader()
            self._t0 = time.monotonic(); self._n = 0; self._logging = True
            return {'ok': True, 'recording': str(LOG_DIR / name), 'sim': self.sim}
        if action == 'stop':
            if not self._logging:
                return {'ok': False, 'error': 'not recording'}
            el = time.monotonic() - self._t0
            self._logging = False
            path = self._fh.name
            self._fh.close()
            return {'ok': True, 'file': path, 'samples': self._n,
                    'seconds': round(el, 1), 'hz': round(self._n / el, 1) if el else 0,
                    'next': 'python data/rpm_rate.py "%s"' % path, 'sim': self.sim}
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
    r = sub.add_parser('read', help='one reading'); r.add_argument('name')
    sn = sub.add_parser('snapshot', help='a set of readings in one call')
    sn.add_argument('names', nargs='*')
    lg = sub.add_parser('log', help='continuous Engine RPM recording')
    lg.add_argument('action', choices=['start', 'stop'])
    lg.add_argument('label', nargs='?', default='idle')

    a = ap.parse_args()
    if a.op == 'serve':
        return serve(a)
    if a.op == 'ports':
        p = list_ports()
        print(json.dumps({'ok': True, 'ports': [{'device': d, 'description': s} for d, s in p],
                          'note': 'BLE adapters present no serial port and cannot be used.'}))
        return 0
    req = {'op': a.op}
    if a.op == 'read':
        req['name'] = a.name
    if a.op == 'snapshot':
        req['names'] = a.names or None
    if a.op == 'log':
        req['action'], req['label'] = a.action, a.label
    rep = client(req, a.listen)
    print(json.dumps(rep, indent=None))
    return 0 if rep.get('ok') else 1


if __name__ == '__main__':
    raise SystemExit(main())
