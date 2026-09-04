"""Sampling and recording. Every measurement is written to disk as it happens."""

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
from .services import read_pid
from .transport import Elm327

log = logging.getLogger("f150diag.recorder")


class Recording:
    """One measurement window: CSV, JSON Lines, and the samples in memory."""

    def __init__(self, out_dir: Path, pids: Sequence[Pid], label: str):
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        safe = re.sub(r"[^A-Za-z0-9_-]", "_", label) or "run"
        out_dir.mkdir(parents=True, exist_ok=True)

        self.label = label
        self.pids = list(pids)
        self.csv_path = out_dir / f"{stamp}-{safe}.csv"
        self.jsonl_path = out_dir / f"{stamp}-{safe}.jsonl"
        self.samples: list[dict] = []
        self.columns = ["timestamp", "elapsed_s", "label"] + [p.name for p in self.pids]

        self._csv_fh = self.csv_path.open("w", newline="", encoding="utf-8")
        self._csv = csv.DictWriter(self._csv_fh, fieldnames=self.columns)
        self._csv.writeheader()
        self._jsonl_fh = self.jsonl_path.open("w", encoding="utf-8")

    def add(self, elapsed: float, readings: dict[str, float | None]) -> None:
        row: dict = {
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
            "elapsed_s": round(elapsed, 3),
            "label": self.label,
        }
        row.update(readings)
        self._csv.writerow(row)
        self._csv_fh.flush()
        self._jsonl_fh.write(json.dumps(row) + "\n")
        self._jsonl_fh.flush()
        self.samples.append({"elapsed_s": row["elapsed_s"], **readings})

    def close(self) -> None:
        self._csv_fh.close()
        self._jsonl_fh.close()

    def __enter__(self) -> "Recording":
        return self

    def __exit__(self, *exc) -> None:
        self.close()


def measure(elm: Elm327, pids: Sequence[Pid], seconds: float, out_dir: Path,
            label: str, on_sample: Callable[[int, dict], None] | None = None) -> Recording:
    """
    Poll a set of PIDs for a fixed window.

    Keep the PID count modest. A cheap ELM327 clone manages only a few samples
    per second and every extra parameter divides that further — and for the
    periodicity analysis, sample rate is what buys resolution.
    """
    rec = Recording(out_dir, pids, label)
    start = time.monotonic()
    try:
        while True:
            elapsed = time.monotonic() - start
            if elapsed >= seconds:
                break
            readings = {p.name: read_pid(elm, p) for p in pids}
            rec.add(elapsed, readings)
            if on_sample:
                on_sample(len(rec.samples), readings)
    except KeyboardInterrupt:
        log.warning("measurement interrupted at %.1f s", time.monotonic() - start)
    finally:
        rec.close()
    log.info("%s: %d samples -> %s", label, len(rec.samples), rec.csv_path.name)
    return rec
