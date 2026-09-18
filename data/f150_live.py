"""Persistent, READ-ONLY live link to the truck: continuous logging + ad-hoc queries.

WHY NOT A SIMPLE QUERY-PER-COMMAND LOOP
---------------------------------------
The obvious design - block on stdin, query one PID, print it - cannot answer a
single open question on this truck, for two reasons this project has already
paid for:

  1. RATE.  Every question here is about how engine speed MOVES: rate of change
     (data/rpm_rate.py), 0.24 s events (data/idle_events.py), engine orders
     (data/order_track_rpm.py).  Those need continuous sampling at tens of Hz.
     One sample per typed command is ~1 Hz at best, and one sample per agent
     round trip is far slower still.  Nyquist at 1 Hz is 0.5 Hz - below even the
     0.33 Hz idle oscillation, and nowhere near first order at 10.8 Hz.
  2. IT KEEPS NOTHING.  A printed value cannot be fed to any tool in this
     repository.  Every finding here came from a logged CSV analysed offline.

So this script does both jobs at once: ONE background thread owns the adapter
and logs continuously at full rate to CSV, while the foreground answers typed
questions by posting them to that same thread.  A serial port has one owner -
docs/FORSCAN.md makes the same point about FORScan - so the connection is never
touched from two places.

The CSV is written with `elapsed_s` and `rpm` headers, which is the format
data/rpm_rate.py and data/idle_events.py already read, so a capture drops
straight into the existing analysis with no conversion.

READ-ONLY
---------
Commands are validated against an explicit ALLOWLIST, not a blocklist.  Nothing
outside it is ever sent.  `obd.commands.CLEAR_DTC` is deliberately never
imported or referenced: clearing destroys the freeze frame, the monitor
readiness and the distance/warm-up counters, and this project has twice had a
measurement ruined by an adaptive reset nobody asked for.

    python3 data/f150_live.py                       auto-detect the adapter
    python3 data/f150_live.py --port /dev/ttyUSB0 --baud 115200
    python3 data/f150_live.py --port COM5           Windows

Type `help` once it is running.
"""
import argparse
import csv
import queue
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

try:
    import obd
except ImportError:
    sys.exit("python-obd is not installed.  pip install obd\n"
             "(or `pip install -e .` from the repository root)")

# Every command this script will ever send.  Names are kept close to the
# owner's sensor list where python-obd has an equivalent; where it does not,
# the note says so, because a name that does not match the phone wastes his
# time at the truck.
ALLOWLIST = {
    'rpm':          (obd.commands.RPM,                 'Engine RPM'),
    'speed':        (obd.commands.SPEED,               'Vehicle speed'),
    'load':         (obd.commands.ENGINE_LOAD,         'Calculated engine load value'),
    'absload':      (obd.commands.ABSOLUTE_LOAD,       'Absolute load value'),
    'coolant':      (obd.commands.COOLANT_TEMP,        'Engine coolant temperature'),
    'intaketemp':   (obd.commands.INTAKE_TEMP,         'Intake air temperature'),
    'ambient':      (obd.commands.AMBIANT_AIR_TEMP,    'Ambient air temperature'),
    'maf':          (obd.commands.MAF,                 'MAF air flow rate'),
    'timing':       (obd.commands.TIMING_ADVANCE,      'Timing advance'),
    'stft1':        (obd.commands.SHORT_FUEL_TRIM_1,   'Short term fuel % trim - Bank 1'),
    'stft2':        (obd.commands.SHORT_FUEL_TRIM_2,   'Short term fuel % trim - Bank 2'),
    'ltft1':        (obd.commands.LONG_FUEL_TRIM_1,    'Long term fuel % trim - Bank 1'),
    'ltft2':        (obd.commands.LONG_FUEL_TRIM_2,    'Long term fuel % trim - Bank 2'),
    'purge':        (obd.commands.EVAPORATIVE_PURGE,   'Commanded evaporative purge'),
    'baro':         (obd.commands.BAROMETRIC_PRESSURE, 'Barometric pressure'),
    'throttle':     (obd.commands.THROTTLE_POS,        'Throttle position'),
    'modulevolts':  (obd.commands.CONTROL_MODULE_VOLTAGE, 'Control module voltage'),
    'adaptervolts': (obd.commands.ELM_VOLTAGE,         'adapter supply voltage - NOT a truck channel'),
    'codes':        (obd.commands.GET_DTC,             'stored trouble codes (read only)'),
    'fuel':         (obd.commands.FUEL_LEVEL,          'Fuel level'),
}

LOG_DIR = Path(__file__).resolve().parent.parent / 'logs'


class Link(threading.Thread):
    """Owns the adapter.  Logs `rpm` continuously; answers ad-hoc requests."""

    def __init__(self, port, baud):
        super().__init__(daemon=True)
        self.port, self.baud = port, baud
        self.requests = queue.Queue()
        self.connected = threading.Event()
        self.fail = None
        self.stop = threading.Event()
        self._writer = self._fh = None
        self._logging = False
        self._t0 = None
        self._n = 0

    # -- logging control, called from the foreground ----------------------
    def start_log(self, label):
        self.requests.put(('_startlog', label, None))

    def stop_log(self):
        q = queue.Queue(); self.requests.put(('_stoplog', None, q)); return q.get()

    def ask(self, key):
        q = queue.Queue(); self.requests.put(('_query', key, q)); return q.get()

    def status(self):
        q = queue.Queue(); self.requests.put(('_status', None, q)); return q.get()

    # -- the thread body ---------------------------------------------------
    def run(self):
        try:
            conn = obd.OBD(self.port, baudrate=self.baud) if self.port else obd.OBD()
        except Exception as exc:                       # noqa: BLE001
            self.fail = str(exc); self.connected.set(); return
        if not conn.is_connected():
            self.fail = ('adapter did not answer. Ignition ON? correct port? '
                         'On Bluetooth the virtual serial port must be bound first.')
            self.connected.set(); return
        self.conn = conn
        self.connected.set()

        while not self.stop.is_set():
            # Serve any pending foreground request first - a human waiting on a
            # reading matters more than one more rpm sample.
            try:
                op, arg, reply = self.requests.get_nowait()
                self._serve(op, arg, reply)
                continue
            except queue.Empty:
                pass
            if self._logging:
                self._sample()
            else:
                time.sleep(0.05)
        self._close_log()
        conn.close()

    def _sample(self):
        r = self.conn.query(obd.commands.RPM)
        if r.is_null():
            return
        self._writer.writerow({'elapsed_s': '%.4f' % (time.monotonic() - self._t0),
                               'rpm': '%.2f' % r.value.magnitude})
        self._n += 1
        if self._n % 200 == 0:
            self._fh.flush()

    def _serve(self, op, arg, reply):
        if op == '_startlog':
            self._close_log()
            LOG_DIR.mkdir(exist_ok=True)
            name = '%s-%s.csv' % (datetime.now().strftime('%Y-%m-%d_%H-%M-%S'), arg)
            self._fh = open(LOG_DIR / name, 'w', newline='')
            self._writer = csv.DictWriter(self._fh, fieldnames=['elapsed_s', 'rpm'])
            self._writer.writeheader()
            self._t0 = time.monotonic(); self._n = 0; self._logging = True
            print('[LOG] recording Engine RPM to logs/%s' % name, flush=True)
        elif op == '_stoplog':
            reply.put(self._close_log())
        elif op == '_status':
            el = (time.monotonic() - self._t0) if self._logging else 0
            reply.put((self._logging, self._n, el, self._n / el if el else 0))
        elif op == '_query':
            cmd, label = ALLOWLIST[arg]
            if not self.conn.supports(cmd) and arg != 'adaptervolts':
                reply.put((label, None, 'this truck does not support it'))
                return
            r = self.conn.query(cmd)
            reply.put((label, None if r.is_null() else r.value,
                       None if not r.is_null() else 'no answer'))

    def _close_log(self):
        if not self._logging:
            return None
        el = time.monotonic() - self._t0
        self._logging = False
        self._fh.close()
        path = Path(self._fh.name)
        return (path, self._n, el, self._n / el if el else 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', default=None,
                    help='e.g. /dev/ttyUSB0, /dev/rfcomm0, COM5. Omit to auto-detect.')
    ap.add_argument('--baud', type=int, default=115200)
    a = ap.parse_args()

    print('[SYSTEM] opening adapter%s ...' % (' on %s' % a.port if a.port else ' (auto-detect)'),
          flush=True)
    link = Link(a.port, a.baud)
    link.start()
    link.connected.wait()
    if link.fail:
        sys.exit('[ERROR] %s' % link.fail)
    print('[READY] connected. READ-ONLY: %d commands allowed, clear-codes is not one '
          'of them.' % len(ALLOWLIST), flush=True)
    print("[READY] type 'log <label>' to start recording engine speed, 'help' for "
          'commands.', flush=True)

    try:
        for raw in sys.stdin:
            c = raw.strip().lower()
            if not c:
                continue
            if c in ('exit', 'quit', 'stop'):
                break
            if c == 'help':
                print('[HELP] readings: %s' % ', '.join(sorted(ALLOWLIST)), flush=True)
                print('[HELP] log <label> | endlog | rate | exit', flush=True)
            elif c.startswith('log'):
                link.start_log(c[3:].strip().replace(' ', '-') or 'idle')
            elif c == 'endlog':
                r = link.stop_log()
                print('[LOG] %s - %d samples in %.1f s = %.1f Hz' % (r[0].name, r[1], r[2], r[3])
                      if r else '[LOG] not recording', flush=True)
                if r:
                    print('[NEXT] python3 data/rpm_rate.py %s' % r[0], flush=True)
            elif c == 'rate':
                on, n, el, hz = link.status()
                print('[RATE] %s - %d samples, %.1f s, %.1f Hz'
                      % ('recording' if on else 'idle', n, el, hz), flush=True)
            elif c in ALLOWLIST:
                label, val, err = link.ask(c)
                print('[DATA] %s: %s' % (label, err if err else val), flush=True)
            else:
                print("[ERROR] '%s' is not allowed or not known. 'help' lists everything."
                      % c, flush=True)
    except KeyboardInterrupt:
        pass
    finally:
        r = link.stop_log()
        if r:
            print('[LOG] saved %s - %d samples, %.1f Hz' % (r[0].name, r[1], r[3]), flush=True)
        link.stop.set(); link.join(timeout=3)
        print('[SYSTEM] connection closed.', flush=True)


if __name__ == '__main__':
    main()
