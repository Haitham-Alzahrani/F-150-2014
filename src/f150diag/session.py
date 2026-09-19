"""RAW DIAGNOSTIC SESSION LOG — one record per request, raw bytes never discarded.

WHY THIS EXISTS
---------------
Before this module, every recorder in this project wrote DECODED VALUES ONLY,
and `recorder.measure` wrote a whole set of sequentially-polled parameters under
ONE shared timestamp:

    readings = {p.name: read_pid(elm, p) for p in pids}   # polled one by one
    rec.add(elapsed, readings)                            # written as simultaneous

That is a false claim of simultaneity, and four wrong findings in this project
came from comparing channels that were never measured at the same moment.

So the unit of record here is THE REQUEST, not the sample set.  Every request
carries its own request time, response time and latency, and nothing is written
that groups two measurements under one clock reading.

ONE CLOCK, ONE ANCHOR
---------------------
All timing is `time.monotonic()` measured from session start, stored as seconds
with microsecond resolution.  The wall clock is recorded ONCE, at session start,
as `started_utc`.  Any absolute time is that anchor plus the offset.

This is deliberate.  `data/f150_agent.py` took the seconds from
`time.localtime()` and the fraction from `(monotonic_elapsed % 1)` - two
unsynchronised clocks - and produced timestamps that jump backwards by up to
999 ms inside a single second.  Mixing clocks is the bug; one clock is the fix.

RAW IS NEVER DISCARDED
----------------------
`raw_request` and `raw_response` hold the bytes exactly as sent and received.
A session can therefore be re-analysed, or re-decoded with a corrected decoder,
WITHOUT connecting to the vehicle again.  `replay()` does that.
"""

from __future__ import annotations

import json
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator, Sequence

SCHEMA = 1


class _Request:
    """One in-flight request.  Timed by the context manager that yields it."""

    __slots__ = ('module', 'service', 'pid', 'name', 'raw_request',
                 'raw_response', 'value', 'unit', 'error', 'extra')

    def __init__(self, module, service, pid, name):
        self.module = module
        self.service = service
        self.pid = pid
        self.name = name
        self.raw_request = None
        self.raw_response = None
        self.value = None
        self.unit = None
        self.error = None
        self.extra = {}


class Session:
    """A JSON Lines log of every request made during one connection."""

    def __init__(self, out_dir, vin=None, label='session', sim=False,
                 adapter=None, protocol=None):
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        self.session_id = uuid.uuid4().hex[:12]
        self.started_utc = datetime.now(timezone.utc).isoformat(
            timespec='microseconds')
        self.vin = vin
        self.sim = bool(sim)
        stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        safe = ''.join(c if c.isalnum() or c in '-_' else '_' for c in label)
        self.path = out_dir / ('%s-%s.session.jsonl' % (stamp, safe or 'run'))
        self._fh = self.path.open('w', encoding='utf-8')
        self._t0 = time.monotonic()
        self._seq = 0
        self._connected = True
        self.last = None            # the most recently committed record

        self._write({
            'record': 'header', 'schema': SCHEMA,
            'session_id': self.session_id, 'started_utc': self.started_utc,
            'vin': vin, 'label': label, 'sim': self.sim,
            'adapter': adapter, 'protocol': protocol,
            'clock': 'time.monotonic() seconds from session start; '
                     'absolute time = started_utc + t_resp_s',
        })

    # -- writing ----------------------------------------------------------
    def _write(self, obj):
        self._fh.write(json.dumps(obj, default=str) + '\n')
        self._fh.flush()

    def set_connected(self, state):
        """Record a connection state change as its own event."""
        state = bool(state)
        if state != self._connected:
            self._connected = state
            self._write({'record': 'connection', 't_s': self.elapsed(),
                         'connected': state})

    def note(self, text, **kw):
        """A free-form marker in the timeline - a gear change, a key event."""
        self._write(dict(record='note', t_s=self.elapsed(), text=text, **kw))

    def elapsed(self):
        return round(time.monotonic() - self._t0, 6)

    # -- the unit of record ------------------------------------------------
    def request(self, service, pid=None, name=None, module=None):
        """Context manager: stamps request and response time around one call.

        Latency is recorded even when the call raises, because a timeout is a
        measurement too - and a session that silently drops failed requests
        misrepresents the sampling interval of the ones that succeeded.
        """
        return _RequestContext(self, service, pid, name, module)

    def _commit(self, req, t_req, t_resp):
        self._seq += 1
        rec = {
            'record': 'request', 'seq': self._seq,
            'session_id': self.session_id, 'vin': self.vin,
            'module': req.module, 'service': req.service, 'pid': req.pid,
            'name': req.name,
            't_req_s': round(t_req, 6), 't_resp_s': round(t_resp, 6),
            'latency_ms': round((t_resp - t_req) * 1000.0, 3),
            'raw_request': req.raw_request,
            'raw_response': req.raw_response,
            'value': req.value, 'unit': req.unit,
            'ok': req.error is None, 'error': req.error,
            'connected': self._connected, 'sim': self.sim,
        }
        if req.extra:
            rec['extra'] = req.extra
        self._write(rec)
        self.last = rec
        return rec

    def close(self, reason='closed'):
        if not self._fh.closed:
            self._write({'record': 'footer', 't_s': self.elapsed(),
                         'requests': self._seq, 'reason': reason})
            self._fh.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close('error: %r' % exc if exc else 'closed')
        return False


class _RequestContext:
    def __init__(self, session, service, pid, name, module):
        self.s = session
        self.req = _Request(module, service, pid, name)
        self.t_req = None

    def __enter__(self):
        self.t_req = self.s.elapsed()
        return self.req

    def __exit__(self, exc_type, exc, tb):
        t_resp = self.s.elapsed()
        if exc is not None and self.req.error is None:
            self.req.error = '%s: %s' % (exc_type.__name__, exc)
        self.s._commit(self.req, self.t_req, t_resp)
        return False


# ---------------------------------------------------------------- reading
def read(path) -> list[dict]:
    """Every record in a session file, header and footer included."""
    out = []
    with Path(path).open(encoding='utf-8') as fh:
        for line in fh:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def header(records) -> dict:
    for r in records:
        if r.get('record') == 'header':
            return r
    return {}


def requests(records) -> list[dict]:
    return [r for r in records if r.get('record') == 'request']


def replay(path, decoder=None) -> Iterator[dict]:
    """Re-run a session from its RAW bytes, with no vehicle connected.

    With no decoder, yields the stored records unchanged.  With one, calls
    `decoder(record)` on each and yields the result - which is how a corrected
    decoder is applied to data already captured.
    """
    for r in requests(read(path)):
        yield decoder(r) if decoder else r


# ---------------------------------------------------------------- timing
def _percentile(xs, q):
    if not xs:
        return None
    xs = sorted(xs)
    k = (len(xs) - 1) * q
    lo, hi = int(k), min(int(k) + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (k - lo)


def channel_timing(records) -> dict:
    """Per-channel ACTUAL sampling interval, measured, not assumed."""
    by = {}
    for r in requests(records):
        if r.get('ok'):
            by.setdefault(r.get('name') or r.get('pid'), []).append(r['t_resp_s'])
    out = {}
    for name, ts in by.items():
        ts.sort()
        gaps = [b - a for a, b in zip(ts, ts[1:])]
        lat = [r['latency_ms'] for r in requests(records)
               if (r.get('name') or r.get('pid')) == name and r.get('ok')]
        out[name] = {
            'n': len(ts), 'span_s': round(ts[-1] - ts[0], 3) if len(ts) > 1 else 0.0,
            'median_interval_s': round(_percentile(gaps, 0.5), 6) if gaps else None,
            'p10_interval_s': round(_percentile(gaps, 0.10), 6) if gaps else None,
            'p90_interval_s': round(_percentile(gaps, 0.90), 6) if gaps else None,
            'hz': round(len(gaps) / (ts[-1] - ts[0]), 2) if len(ts) > 1 and ts[-1] > ts[0] else None,
            'median_latency_ms': round(_percentile(lat, 0.5), 3) if lat else None,
        }
    return out


def pair_offsets(records, a, b) -> dict:
    """THE ANTI-SIMULTANEITY CHECK: how far apart two channels really are.

    For every sample of `a`, the time to the nearest sample of `b`.  This is the
    number that must be reported alongside any cross-channel comparison.  It is
    never zero for sequentially polled parameters, and saying so is the point.
    """
    ta = sorted(r['t_resp_s'] for r in requests(records)
                if (r.get('name') or r.get('pid')) == a and r.get('ok'))
    tb = sorted(r['t_resp_s'] for r in requests(records)
                if (r.get('name') or r.get('pid')) == b and r.get('ok'))
    if not ta or not tb:
        return {'a': a, 'b': b, 'n': 0,
                'note': 'one or both channels have no successful samples'}
    import bisect
    offs = []
    for t in ta:
        i = bisect.bisect_left(tb, t)
        cands = [tb[j] for j in (i - 1, i) if 0 <= j < len(tb)]
        offs.append(min(abs(t - c) for c in cands))
    return {
        'a': a, 'b': b, 'n': len(offs),
        'median_offset_s': round(_percentile(offs, 0.5), 6),
        'p90_offset_s': round(_percentile(offs, 0.90), 6),
        'max_offset_s': round(max(offs), 6),
        'simultaneous': False,
        'note': 'these channels were polled SEQUENTIALLY; the offsets above are '
                'the real spacing and must be quoted with any comparison',
    }
