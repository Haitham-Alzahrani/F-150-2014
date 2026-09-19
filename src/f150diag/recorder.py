"""Sampling and recording. Every measurement is written to disk as it happens.

EACH READING CARRIES ITS OWN TIMESTAMP. THIS IS THE POINT OF THIS MODULE.
------------------------------------------------------------------------
The previous version of this file did:

    readings = {p.name: read_pid(elm, p) for p in pids}   # polled ONE BY ONE
    rec.add(elapsed, readings)                            # written as one row,
                                                          # ONE shared timestamp

An ELM327 answers one request at a time.  Six parameters are six round trips,
spread over as much as a second, and writing them under a single `elapsed_s`
asserts a simultaneity that never happened.  Four wrong findings in this
project came from comparing channels that were never measured together, and
this recorder was manufacturing exactly that error in new data.

Now every parameter is timestamped when ITS OWN reply arrives, and the CSV has
one row per reading.  Cross-channel comparison is still possible - the offsets
are simply visible instead of hidden, and `session.pair_offsets` reports them.

Two files are written per measurement:

    .csv            one row per reading, sparse, for the analysis tools
    .session.jsonl  every request with raw bytes, latency and both timestamps
"""

from __future__ import annotations

import csv
import json
import logging
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Sequence

from .pids import Pid
from .services import read_pid_raw
from .session import Session
from .transport import Elm327

log = logging.getLogger("f150diag.recorder")


class Recording:
    """One measurement window.

    `samples` keeps the grouped, one-dict-per-cycle shape that
    `analysis.metrics` consumes.  That grouping is a CONVENIENCE FOR SUMMARY
    STATISTICS ONLY - the per-reading times in the CSV and the session file are
    the record of when anything was actually measured.
    """

    def __init__(self, out_dir: Path, pids: Sequence[Pid], label: str,
                 vin: str | None = None, sim: bool = False):
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        safe = re.sub(r"[^A-Za-z0-9_-]", "_", label) or "run"
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        self.label = label
        self.pids = list(pids)
        self.csv_path = out_dir / f"{stamp}-{safe}.csv"
        self.columns = ["elapsed_s", "channel", "value", "unit",
                        "latency_ms"] + [p.name for p in self.pids]
        self.session = Session(out_dir, vin=vin, label=label, sim=sim)
        self.jsonl_path = self.session.path

        self._csv_fh = self.csv_path.open("w", newline="", encoding="utf-8")
        self._csv = csv.DictWriter(self._csv_fh, fieldnames=self.columns)
        self._csv.writeheader()
        self._cycles: list[dict] = []
        self._open_cycle: dict | None = None
        self.n_readings = 0

    # -- per-reading -------------------------------------------------------
    def add_reading(self, pid: Pid, value, t_req: float, t_resp: float,
                    raw_request=None, raw_response=None, error=None) -> None:
        """One parameter, timestamped when ITS OWN reply arrived."""
        row = {c: "" for c in self.columns}
        row["elapsed_s"] = "%.6f" % t_resp
        row["channel"] = pid.name
        row["unit"] = pid.unit
        row["latency_ms"] = "%.3f" % ((t_resp - t_req) * 1000.0)
        if value is not None:
            row["value"] = repr(value)
            row[pid.name] = repr(value)
        self._csv.writerow(row)
        self._csv_fh.flush()
        self.n_readings += 1

        if self._open_cycle is not None:
            self._open_cycle[pid.name] = value
            self._open_cycle.setdefault("_t", {})[pid.name] = round(t_resp, 6)

    # -- cycle grouping, for summary statistics only -----------------------
    def begin_cycle(self, elapsed: float) -> None:
        self._open_cycle = {"elapsed_s": round(elapsed, 6)}

    def end_cycle(self) -> dict:
        cyc = self._open_cycle or {}
        self._cycles.append(cyc)
        self._open_cycle = None
        return cyc

    @property
    def samples(self) -> list[dict]:
        """Grouped view. The per-reading times live under each cycle's `_t`."""
        return self._cycles

    def close(self) -> None:
        if not self._csv_fh.closed:
            self._csv_fh.close()
        self.session.close()

    def __enter__(self) -> "Recording":
        return self

    def __exit__(self, *exc) -> None:
        self.close()


def measure(elm: Elm327, pids: Sequence[Pid], seconds: float, out_dir: Path,
            label: str, on_sample: Callable[[int, dict], None] | None = None,
            vin: str | None = None) -> Recording:
    """
    Poll a set of PIDs for a fixed window, timestamping each reply separately.

    Keep the PID count modest. A cheap ELM327 clone manages only a few samples
    per second and every extra parameter divides that further - and for the
    periodicity analysis, sample rate is what buys resolution.
    """
    rec = Recording(out_dir, pids, label, vin=vin)
    start = time.monotonic()
    try:
        while True:
            elapsed = time.monotonic() - start
            if elapsed >= seconds:
                break
            rec.begin_cycle(elapsed)
            for p in pids:
                with rec.session.request(service="01", pid=p.code,
                                         name=p.name, module="7E0") as r:
                    value, raw_req, raw_resp, err = read_pid_raw(elm, p)
                    r.raw_request = raw_req
                    r.raw_response = raw_resp
                    r.value = value
                    r.unit = p.unit
                    r.error = err
                # the session stamped both times when the block exited
                stamped = rec.session.last or {}
                rec.add_reading(p, value,
                                t_req=stamped.get("t_req_s", elapsed),
                                t_resp=stamped.get("t_resp_s", elapsed),
                                raw_request=raw_req, raw_response=raw_resp,
                                error=err)
            cyc = rec.end_cycle()
            if on_sample:
                on_sample(len(rec.samples), {k: v for k, v in cyc.items()
                                             if not k.startswith("_")})
    except KeyboardInterrupt:
        log.warning("measurement interrupted at %.1f s", time.monotonic() - start)
    finally:
        rec.close()
    log.info("%s: %d readings in %d cycles -> %s",
             label, rec.n_readings, len(rec.samples), rec.csv_path.name)
    return rec

