# The raw session log — one record per request, raw bytes never discarded

**Built 2026-09-19, before the vehicle was connected.** The unit of record is
**the request**, not the sample set.

## The problem it replaces

`recorder.measure` used to do this:

```python
readings = {p.name: read_pid(elm, p) for p in pids}   # polled ONE BY ONE
rec.add(elapsed, readings)                            # written as simultaneous
```

An ELM327 answers one request at a time. Six parameters are six round trips
spread over as much as a second, and writing them under a single `elapsed_s`
**asserts a simultaneity that never happened**. Four wrong findings in this
project came from comparing channels that were never measured together — and
this recorder was manufacturing that same error in every new capture.

## What is recorded now

Every request, as one JSON Lines record:

| Field | |
|---|---|
| `seq`, `session_id`, `vin` | identity |
| `module`, `service`, `pid`, `name` | what was asked, of whom |
| `t_req_s`, `t_resp_s` | **its own** request and response time |
| `latency_ms` | round trip, recorded **even when the request fails** |
| `raw_request`, `raw_response` | **the bytes. Never discarded.** |
| `value`, `unit` | the decode |
| `ok`, `error`, `connected`, `sim` | state |

A failed request is still a record. A session that silently drops failures
misrepresents the sampling interval of the ones that succeeded.

## ONE CLOCK, ONE ANCHOR

All timing is `time.monotonic()` from session start. The wall clock is recorded
**once**, as `started_utc`. Absolute time is that anchor plus the offset.

This is deliberate. `data/f150_agent.py` took the seconds from
`time.localtime()` and the fraction from `(monotonic_elapsed % 1)` — two
unsynchronised clocks — and wrote timestamps that jumped **backwards by up to
999 ms inside one second**:

```
elapsed 0.990  ->  02:38:59.990
elapsed 1.020  ->  02:38:59.020     <- 970 ms backwards
```

Fixed 2026-09-19 and verified on a 265-sample capture crossing 9 second
boundaries: **zero negative intervals, strictly monotonic, 33.3 Hz.**

## The anti-simultaneity check

```python
S.pair_offsets(records, 'rpm', 'maf')
```
```
rpm vs maf: n=57 median offset 0.0335 s, p90 0.0373 s, max 0.0392 s
simultaneous: False
```

**This number must be quoted with any cross-channel comparison.** It is never
zero for sequentially polled parameters, and saying so is the point.

`channel_timing()` gives the **measured** interval per channel — median, p10,
p90, hertz and latency — rather than the interval that was requested.

## Replay — re-analysis with no vehicle

```python
for rec in S.replay(path, decoder=my_corrected_decoder):
    ...
```

Because the raw bytes are kept, a decoder fixed later can be applied to data
already captured. Verified: 57 of 57 engine-speed records re-decoded from raw
reproduced the stored values exactly, with no connection.

## Files written per measurement

```
<stamp>-<label>.csv             one row per READING, sparse, for the analysis tools
<stamp>-<label>.session.jsonl   every request, with raw bytes and both timestamps
```

`Recording.samples` still returns the grouped, one-dict-per-cycle shape that
`analysis.metrics` consumes. **That grouping is a convenience for summary
statistics only** — the per-reading times are the record of when anything was
actually measured, and each cycle carries its readings' true times under `_t`.

## Not yet done

The session layer is wired into `f150diag`'s recorder. **`data/f150_agent.py`
still writes only its CSV** — its timestamps are now correct, but it does not
yet emit a session file with raw bytes and latency.
