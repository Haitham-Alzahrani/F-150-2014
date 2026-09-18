"""Discover and IDENTIFY Ford mode 22 identifiers empirically, on this VIN.

    python data/did_scan.py scan     0x1100 0x11FF     which addresses answer
    python data/did_scan.py identify 0x1100 RPM        what does this one carry
    python data/did_scan.py confirm  0x11A6 "A/C ..."  record a manipulation
    python data/did_scan.py show                       the registry

Needs the agent daemon running (`f150_agent.py serve`), because that process
owns the adapter.  Add `--sim` to the daemon to rehearse all of this with no
car attached.

WHY IDENTIFY RATHER THAN LOOK UP
--------------------------------
A mode 22 reply is bytes.  Nothing in it says what it means or how it is
scaled, so a wrong address does not fail - it returns a plausible number.  This
project's rule is that the registry stays empty until an entry is verified on
THIS VIN, and that rule is correct.

`identify` satisfies it without FORScan.  It logs the candidate beside a
STANDARD channel whose meaning is already known, tries every plausible byte
interpretation, and regresses each against the known channel.  If one fits, it
has proved the identity from the truck AND measured the scale and offset - the
units are derived, never assumed.  The r-squared says how well.

`confirm` covers what correlation cannot reach: cylinder acceleration, knock -
channels with no standard twin.  There, a physical change is PREDICTED IN
WRITING, then made, then observed.  Prediction before data is this project's
own rule.
"""
import argparse
import json
import socket
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _repo import utf8
from f150_did import (REGISTRY, add_entry, load_registry, save_registry)

HOST, PORT = '127.0.0.1', 51507
R2_GATE, N_GATE = 0.99, 200
TIE = 0.005          # r-squared margin within which two readings fit "as well"


def ask(req, port):
    try:
        with socket.create_connection((HOST, port), timeout=30) as s:
            s.sendall((json.dumps(req) + '\n').encode())
            return json.loads(s.makefile().readline())
    except ConnectionRefusedError:
        return {'ok': False, 'error': 'no daemon on %s:%d - start '
                'f150_agent.py serve (add --sim to rehearse)' % (HOST, port)}


# ----------------------------------------------------------------- decoding
def interpretations(hexdata):
    """Every plausible reading of a mode 22 payload, as {label: integer}.

    The reply echoes 62 <did hi> <did lo> before the payload, so the first
    three bytes are stripped.  Nothing here decides which reading is right -
    the regression does.
    """
    raw = bytes.fromhex(hexdata)
    body = raw[3:] if len(raw) > 3 and raw[0] == 0x62 else raw
    out = {}
    for n in (1, 2, 4):
        if len(body) < n:
            continue
        for order in ('big', 'little'):
            for signed in (False, True):
                if n == 1 and order == 'little':
                    continue
                key = '%dB-%s-%s' % (n, order[0], 's' if signed else 'u')
                out[key] = int.from_bytes(body[:n], order, signed=signed)
    return out


def fit(x, y):
    """Least squares y = a*x + b, returning (a, b, r2)."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) < 3 or x.std() == 0:
        return 0.0, 0.0, 0.0
    a, b = np.polyfit(x, y, 1)
    pred = a * x + b
    ss_res = ((y - pred) ** 2).sum()
    ss_tot = ((y - y.mean()) ** 2).sum()
    return a, b, (1 - ss_res / ss_tot) if ss_tot else 0.0


# -------------------------------------------------------------------- scan
def cmd_scan(a):
    lo, hi = int(a.start, 0), int(a.end, 0)
    if hi < lo or hi - lo > 4096:
        sys.exit('range must be ascending and at most 4096 wide')
    print('scanning %04X..%04X - read-only, service 0x22 only' % (lo, hi))
    print('%d addresses at about %.0f/s, roughly %.1f min\n'
          % (hi - lo + 1, 1 / a.delay, (hi - lo + 1) * a.delay / 60))
    found, t0 = [], time.time()
    for did in range(lo, hi + 1):
        rep = ask({'op': 'did', 'did': did}, a.listen)
        if rep.get('ok') and rep.get('hex'):
            found.append((did, rep['hex']))
            print('  %04X  ANSWERS  %s' % (did, rep['hex']))
        elif not rep.get('ok') and 'no daemon' in str(rep.get('error', '')):
            sys.exit(rep['error'])
        time.sleep(a.delay)
    el = time.time() - t0
    print('\n%d of %d answered, in %.1f s' % (len(found), hi - lo + 1, el))
    reg = load_registry()
    reg.setdefault('scans', []).append(
        dict(range='%04X-%04X' % (lo, hi), answered=['%04X' % d for d, _ in found],
             when=time.strftime('%Y-%m-%d %H:%M')))
    save_registry(reg)
    if found:
        print('\nAn address answering says NOTHING about what it carries.')
        print('Identify each one:')
        for d, _ in found[:6]:
            print('   python data/did_scan.py identify 0x%04X RPM' % d)
    return 0


# ---------------------------------------------------------------- identify
def cmd_identify(a):
    did = int(a.did, 0)
    print('identifying %04X against the standard channel %s' % (did, a.against))
    print('sampling %d pairs ...\n' % a.samples)
    raws, knowns, sim = [], [], False
    for i in range(a.samples):
        d = ask({'op': 'did', 'did': did}, a.listen)
        k = ask({'op': 'read', 'name': a.against}, a.listen)
        if d.get('sim') or k.get('sim'):
            sim = True
        if d.get('ok') and d.get('hex') and k.get('ok'):
            try:
                knowns.append(float(str(k['value']).split()[0]))
                raws.append(d['hex'])
            except ValueError:
                pass
        if i % 25 == 0 and i:
            print('   %d/%d' % (i, a.samples))
    if len(raws) < 20:
        sys.exit('only %d usable pairs - is the daemon connected?' % len(raws))

    print('\n%d paired samples. Trying every byte interpretation:\n' % len(raws))
    print('  %-12s %12s %12s %9s' % ('reading', 'scale', 'offset', 'r-squared'))
    best, rows = None, []
    for key in interpretations(raws[0]):
        xs = []
        for h in raws:
            iv = interpretations(h)
            if key not in iv:
                break
            xs.append(iv[key])
        if len(xs) != len(raws):
            continue
        sc, off, r2 = fit(xs, knowns)
        print('  %-12s %12.6f %12.4f %9.5f' % (key, sc, off, r2))
        rows.append((key, sc, off, r2))
        if best is None or r2 > best[3]:
            best = (key, sc, off, r2)

    # HIGHEST r-squared IS the right rule, in BOTH directions: reading a 2-byte
    # field as 1 byte truncates it and fits worse; reading a 1-byte field as 2
    # pulls in a foreign byte and also fits worse.  Do NOT "prefer the wider
    # field" - that picks wrongly on a genuine 1-byte identifier.  But when two
    # WIDTHS fit within TIE of each other the test has not resolved the width,
    # and the scales differ by 256x, so say so rather than choose silently.
    rival = [r for r in rows
             if r[0][0] != best[0][0] and r[3] >= best[3] - TIE]
    width_note = None
    if rival:
        r = max(rival, key=lambda r: r[3])
        width_note = '%s vs %s' % (best[0], r[0])
        print('\nFIELD WIDTH NOT RESOLVED: %s fits to %.5f against %s at '
              '%.5f.' % (r[0], r[3], best[0], best[3]))
        print('Those two scales differ by a factor of 256, so this matters.')
        print('A constant padding byte makes both fit equally; a wider sweep '
              'separates them, because the narrow reading quantises in steps '
              'of %.4g and the residual goes stair-shaped.' % abs(r[1]))

    key, sc, off, r2 = best
    spread = float(np.ptp(knowns))
    print('\nbest: %s, scale %.6f, offset %.4f, r-squared %.5f' % (key, sc, off, r2))
    print('%s moved over a range of %.1f during the test.' % (a.against, spread))
    verified = r2 >= R2_GATE and len(raws) >= N_GATE
    if verified:
        print('\nPASSES THE GATE (r2 >= %.2f over >= %d samples).' % (R2_GATE, N_GATE))
        print('%04X carries %s. Scale and offset were MEASURED, not assumed.'
              % (did, a.against))
    else:
        why = []
        if r2 < R2_GATE:
            why.append('r-squared %.5f is below %.2f' % (r2, R2_GATE))
        if len(raws) < N_GATE:
            why.append('%d samples is below %d' % (len(raws), N_GATE))
        print('\nDOES NOT PASS: %s.' % ' and '.join(why))
        print('Recorded as unverified. Every reading from it will be flagged.')
        if 0.3 < r2 < R2_GATE:
            print('''
THIS IS PROBABLY REGRESSION DILUTION, NOT A WRONG ADDRESS.
The identifier and the standard channel are polled one after the other, not at
the same instant, so the quantity moves between the two reads.  Error in the
x-variable ATTENUATES the fitted slope - the scale comes out LOW - and drags
r-squared down with it.  Measured on this pipeline: with the quantity moving
over only ~9 units the slope read 10 % low; over ~400 units it read 0.04 % low
and r-squared reached 0.9999.

THE CURE IS A WIDER SIGNAL, NOT A BETTER FIT.  Repeat the identification while
deliberately SWEEPING the quantity over as much of its range as you safely can
- for engine speed, blip the throttle through the whole test; for a
temperature, run it from cold.  The r-squared gate is what protects the scale:
at r-squared 0.99 the remaining attenuation is about 1 %.''')
        elif r2 <= 0.3:
            print('An r-squared this low usually means %04X carries something '
                  'ELSE entirely - try identifying it against a different '
                  'standard channel.' % did)

    # A SIMULATED LINK CANNOT VERIFY ANYTHING.  The simulator's scaling was
    # planted, so a pass there proves the PIPELINE works and says nothing about
    # this VIN.  Rehearsal must never leave a registry entry that later reads
    # as a measurement from the truck.
    if sim:
        verified = False
        print('\nSIMULATED LINK - this entry is recorded as UNVERIFIED '
              'whatever it fitted.')
        print('The simulator\'s scaling was planted, so this tests the method, '
              'not the truck.')

    # A REPEAT THAT FAILS MUST NOT DEMOTE A MEASUREMENT THAT PASSED.  The
    # registry is keyed by identifier, so a second, narrower run would
    # otherwise overwrite a verified scale with a diluted one.
    reg = load_registry()
    prior = reg.get('entries', {}).get('%04X' % did)
    if prior and prior.get('verified') and not verified:
        print('\n%04X IS ALREADY VERIFIED (r-squared %s over a range of %s).'
              % (did, prior.get('evidence', {}).get('r2'),
                 prior.get('evidence', {}).get('spread')))
        print('This weaker run is DISCARDED, not written - the earlier '
              'measurement stands.')
        print('To replace it, delete the entry from %s first.' % REGISTRY.name)
        return 2

    n = int(key.split('B')[0])
    reg = add_entry(reg, did, a.name or a.against, 'correlation',
                    dict(against=a.against, r2=round(r2, 5), samples=len(raws),
                         reading=key, spread=round(spread, 2),
                         width_unresolved=width_note, sim=sim),
                    scale=sc, offset=off, nbytes=n,
                    byteorder='big' if '-b-' in key else 'little',
                    signed=key.endswith('-s'), verified=verified)
    save_registry(reg)
    print('\nwritten to %s' % REGISTRY.name)
    return 0 if verified else 2


# ----------------------------------------------------------------- confirm
def cmd_confirm(a):
    """Record a manipulation result for a channel with no standard twin."""
    did = int(a.did, 0)
    reg = load_registry()
    key = '%04X' % did
    e = reg['entries'].get(key)
    if not e:
        sys.exit('%s is not in the registry - scan and identify it first' % key)
    e['method'] = 'manipulation'
    e['evidence'] = dict(prediction=a.prediction, observed=a.observed,
                         when=time.strftime('%Y-%m-%d %H:%M'))
    e['verified'] = bool(a.confirmed)
    e['name'] = a.name or e['name']
    save_registry(reg)
    print('%s recorded as %s' % (key, 'VERIFIED' if a.confirmed else 'still unverified'))
    print('prediction: %s' % a.prediction)
    print('observed  : %s' % a.observed)
    return 0


def cmd_show(a):
    reg = load_registry()
    es = reg.get('entries', {})
    if not es:
        print('registry is empty - as it should be until something is identified '
              'on this VIN.')
        return 0
    print('%-6s %-30s %-12s %-9s %s' % ('did', 'name', 'method', 'verified', 'evidence'))
    for k in sorted(es):
        e = es[k]
        print('%-6s %-30s %-12s %-9s %s'
              % (k, e['name'][:30], e['method'],
                 'YES' if e['verified'] else 'no', json.dumps(e['evidence'])[:46]))
    return 0


def main():
    utf8()
    p = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    p.add_argument('--listen', type=int, default=PORT)
    sub = p.add_subparsers(dest='op', required=True)

    s = sub.add_parser('scan'); s.add_argument('start'); s.add_argument('end')
    s.add_argument('--delay', type=float, default=0.05)

    i = sub.add_parser('identify'); i.add_argument('did'); i.add_argument('against')
    i.add_argument('--samples', type=int, default=250); i.add_argument('--name')

    c = sub.add_parser('confirm'); c.add_argument('did')
    c.add_argument('prediction'); c.add_argument('observed')
    c.add_argument('--name'); c.add_argument('--confirmed', action='store_true')

    sub.add_parser('show')
    a = p.parse_args()
    return dict(scan=cmd_scan, identify=cmd_identify,
                confirm=cmd_confirm, show=cmd_show)[a.op](a)


if __name__ == '__main__':
    raise SystemExit(main())
