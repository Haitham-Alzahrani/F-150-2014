"""RUN THE DECISION TREE AT THE TRUCK, AGAINST THE STORED BASELINE.

WHY THIS EXISTS
---------------
Reading a number is not diagnosis.  The misfire counters only mean something
against the ones already recorded on this truck, and the repository HAS those -
2026-09-05 04:36 local, all six cylinders, in the mode06 table of data/f150.db.
They sat there unanalysed while the project wrote three times that per-cylinder
misfire counts had "never been obtained".

So this tool does not just read.  It reads, compares against that baseline, and
says which branch of the decision tree the truck is on.

    baseline    print the stored 2026-09-05 counters and their provenance
    misfire     read them live, compare, and give the verdict
    voltage     the charging test, guided, with live readings
    status      what can and cannot be measured right now, and exactly why

WHAT IT CANNOT DO, AND WHY - READ THIS BEFORE TRUSTING A CLEAN RESULT
---------------------------------------------------------------------
`[PCM] Cylinder N Acceleration Value`, `[PCM] ATF Temperature`, turbine shaft
speed and the gear ratios are Ford enhanced service 0x22 channels.  They are
NOT standard OBD-II and python-obd has no service 0x22 at all.  The mechanism
to read them exists (data/f150_did.py) but NO IDENTIFIER IS VERIFIED ON THIS
VIN, so those channels are unreachable until the identification in
docs/MODE-22.md has been run at the truck.  `status` prints this honestly
rather than silently returning nothing.
"""
import argparse
import json
import sqlite3
import socket
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _repo import ROOT, utf8

utf8()
DB = ROOT / 'data' / 'f150.db'
BASELINE_DATE = '2026-09-05'
BASELINE_CLOCK = '04:36 local (01:38 UTC)'
CYL = 6

# A count this small is a single event - a start, a gear engagement - not a
# pattern.  The ten-driving-cycle average is the number that matters, and on
# the baseline it is zero for every cylinder.
NOISE_FLOOR = 5


def ask(req, port=51507, host='127.0.0.1'):
    s = socket.create_connection((host, port), timeout=30)
    s.sendall((json.dumps(req) + '\n').encode())
    buf = b''
    while not buf.endswith(b'\n'):
        chunk = s.recv(65536)
        if not chunk:
            break
        buf += chunk
    s.close()
    return json.loads(buf.decode() or '{}')


def load_baseline():
    """The 2026-09-05 counters, straight from the database."""
    if not DB.exists():
        return None
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    out = {}
    for r in c.execute("select monitor, mid, tid, value, limit_max, result, source "
                       "from mode06 where monitor like 'Misfire Cylinder%'"):
        n = int(r['monitor'].split()[2])
        tid = (r['tid'] or '').upper().replace('TID$', '').replace('$', '')
        if tid in ('0B', '0C'):
            out.setdefault(n, {})[tid] = dict(
                value=float(r['value']), limit_max=r['limit_max'],
                result=r['result'], source=r['source'], mid=r['mid'])
    c.close()
    return out or None


def cmd_baseline(a):
    b = load_baseline()
    if not b:
        print('NO BASELINE in %s' % DB)
        return 1
    print('STORED BASELINE - %s, %s' % (BASELINE_DATE, BASELINE_CLOCK))
    print('This is PRE-TUNE. Any live comparison is post-tune.\n')
    print('  %-4s %-7s %14s %14s' % ('cyl', 'MID', 'EWMA (TID 0B)', 'count (TID 0C)'))
    for n in range(1, CYL + 1):
        e = b.get(n, {})
        print('  %-4d %-7s %14s %14s' % (
            n, e.get('0C', {}).get('mid', '?'),
            e.get('0B', {}).get('value', '-'), e.get('0C', {}).get('value', '-')))
    src = b[1]['0C']['source']
    print('\n  provenance: %s' % src)
    print('  EWMA is the ten-driving-cycle average. It is 0 on every cylinder.')
    return 0


def _live(port):
    r = ask({'op': 'monitors', 'only': 'misfire'}, port)
    if not r.get('ok'):
        return None, r
    out = {}
    for name, tests in (r.get('monitors') or {}).items():
        if 'MISFIRE_CYLINDER_' not in name:
            continue
        n = int(name.rsplit('_', 1)[1])
        for t in tests:
            lbl = (t.get('test') or '').upper()
            key = '0B' if 'AVERAGE' in lbl or 'EWMA' in lbl else (
                  '0C' if 'COUNT' in lbl else None)
            if key:
                try:
                    out.setdefault(n, {})[key] = float(str(t['value']).split()[0])
                except (ValueError, KeyError):
                    pass
    return out, r


def cmd_misfire(a):
    base = load_baseline()
    live, raw = _live(a.port)
    if live is None:
        print('COULD NOT READ: %s' % raw.get('error') or raw.get('refused'))
        print('Is the daemon running?  python data/f150_agent.py serve')
        return 1
    if raw.get('sim'):
        print('*** SIMULATED LINK - these are NOT the truck. ***\n')
    if not live:
        print('The PCM returned no completed misfire monitor test.')
        print('That is not the same as zero counts - it means the monitor has')
        print('not run its drive cycle, or these identifiers are unsupported.')
        print('Baseline says MID $A2-$A7 DID answer on 2026-09-05, so an empty')
        print('result here is a changed condition worth noting, not a dead end.')
        return 2

    print('MISFIRE COUNTERS - live against the %s baseline\n' % BASELINE_DATE)
    print('  %-4s %10s %10s   %10s %10s' % ('cyl', 'EWMA now', 'EWMA then', 'count now', 'count then'))
    worst, worst_n = -1.0, None
    for n in range(1, CYL + 1):
        ln, bn = live.get(n, {}), (base or {}).get(n, {})
        e_now, c_now = ln.get('0B'), ln.get('0C')
        e_then = bn.get('0B', {}).get('value') if bn else None
        c_then = bn.get('0C', {}).get('value') if bn else None
        print('  %-4d %10s %10s   %10s %10s' % (
            n, '-' if e_now is None else e_now, '-' if e_then is None else e_then,
            '-' if c_now is None else c_now, '-' if c_then is None else c_then))
        score = max(e_now or 0, c_now or 0)
        if score > worst:
            worst, worst_n = score, n

    ewmas = [v.get('0B', 0) or 0 for v in live.values()]
    counts = [v.get('0C', 0) or 0 for v in live.values()]
    print('\nVERDICT')
    if max(ewmas) == 0 and max(counts) <= NOISE_FLOOR:
        print('  CLEAN. Every ten-driving-cycle average is 0 and no count exceeds %d.' % NOISE_FLOOR)
        print('  A count of 1 or 2 against a 65535 limit is a single event, not a')
        print('  pattern. THE CYLINDER ACCELERATION RANKING IS NOT A MISFIRE.')
        print('\n  NEXT: stop cylinder work. Do not swap a coil. Go to the charging')
        print('        test (python data/diagnose.py voltage) and the transmission,')
        print('        which has never been measured while moving.')
    else:
        others = sorted(max(v.get('0B', 0) or 0, v.get('0C', 0) or 0)
                        for n, v in live.items() if n != worst_n)
        med = others[len(others) // 2] if others else 0
        print('  CYLINDER %d IS THE HIGHEST (%g against a median of %g elsewhere).' % (worst_n, worst, med))
        print('  This is a DIRECT combustion measurement and it outranks the')
        print('  cylinder acceleration channel.')
        print('\n  NEXT: swap the cylinder %d ignition coil with cylinder 3 - NOT' % worst_n)
        print('        cylinder 4, whose acceleration channel is the worst-sampled')
        print('        in the archive. Then re-run this command.')
    print('\n  BEFORE BELIEVING EITHER: have codes been cleared or the battery')
    print('  disconnected since %s? That RESETS these counters and makes the' % BASELINE_DATE)
    print('  comparison meaningless. If so, drive it and re-read.')
    return 0


def cmd_voltage(a):
    print('CHARGING TEST - the alternator reached 13.89 V in 2 of 7 archived')
    print('sessions and 12.59-12.77 V in the other 5. So the hardware works and')
    print('the question is REGULATION. Load it and watch.\n')
    r = ask({'op': 'read', 'name': 'CONTROL_MODULE_VOLTAGE'}, a.port)
    if not r.get('ok'):
        print('COULD NOT READ: %s' % (r.get('error') or r.get('refused')))
        return 1
    if r.get('sim'):
        print('*** SIMULATED - not the truck. ***')
    print('  engine idling, no load:      %s V' % r.get('value'))
    print('\n  Now switch on headlights, blower on high, rear defroster.')
    print('  Wait 30 seconds, then run this command again.\n')
    print('  RISES toward 13.5-14.5 V  -> regulated smart-charge behaviour.')
    print('                               CHARGING CLOSED.')
    print('  STAYS at 12.6 V and falls -> the alternator is not carrying the')
    print('                               load. Investigate charging.')
    print('\n  A meter across the battery posts is just as good and needs no scanner.')
    return 0


MODE22_NEEDED = [
    '[PCM] Cylinder 1-6 Acceleration Value',
    '[PCM] ATF Temperature',
    '[PCM] Actual Turbine Shaft Speed',
    '[PCM] Commanded Gear Ratio / Measured Gear Ratio',
]


def cmd_status(a):
    import f150_did as D
    reg = D.load_registry()
    entries = reg.get('entries', {})
    verified = [k for k, v in entries.items() if v.get('verified')]
    print('WHAT CAN BE MEASURED RIGHT NOW\n')
    print('  READY - standard OBD-II, no identification needed:')
    print('     misfire counters per cylinder      service 06   diagnose.py misfire')
    print('     charging voltage                   service 01   diagnose.py voltage')
    print('     engine speed, trims, mass air flow service 01   f150_agent.py read')
    print('     fault codes incl. permanent        03/07/0A     f150_agent.py dtc')
    print('     freeze frame, readiness, VIN       02/01/09     f150_agent.py healthcheck')
    print('\n  NOT READY - Ford enhanced service 0x22, identification required:')
    for c in MODE22_NEEDED:
        print('     %s' % c)
    print('\n     verified identifiers on this VIN: %d' % len(verified))
    if not verified:
        print('     THE REGISTRY IS EMPTY. Until docs/MODE-22.md has been run at')
        print('     the truck, cylinder acceleration and every transmission')
        print('     channel are UNREADABLE by this tool. A clean misfire result')
        print('     does not depend on them; a cylinder-balance capture does.')
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    p.add_argument('--port', type=int, default=51507)
    sub = p.add_subparsers(dest='op', required=True)
    for n in ('baseline', 'misfire', 'voltage', 'status'):
        sub.add_parser(n)
    a = p.parse_args()
    return dict(baseline=cmd_baseline, misfire=cmd_misfire,
                voltage=cmd_voltage, status=cmd_status)[a.op](a)


if __name__ == '__main__':
    raise SystemExit(main())
