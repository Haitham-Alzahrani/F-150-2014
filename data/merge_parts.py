#!/usr/bin/env python3
"""Merge the per-agent extraction shards in data/parts/ into the final CSVs.

Each extraction agent writes its own shard so the agents cannot collide. This
concatenates them, keeps one header, sorts where a sensible key exists, and
reports what came from where.

    python3 data/merge_parts.py
"""
from __future__ import annotations

import csv
import pathlib
import sys

DATA = pathlib.Path(__file__).resolve().parent
PARTS = DATA / "parts"

#: target file -> the shard filenames that feed it, in order
SOURCES: dict[str, list[str]] = {
    "readings.csv": ["part1_readings.csv", "part2_readings.csv", "part3_readings.csv"],
    "sessions.csv": ["part1_sessions.csv", "part2_sessions.csv", "part3_sessions.csv"],
    "subjective.csv": ["part1_subjective.csv", "part2_subjective.csv", "part3_subjective.csv"],
    "timeline.csv": ["part1_timeline.csv", "part2_timeline.csv", "part3_timeline.csv"],
    "findings.csv": ["part4_findings.csv"],
    "eliminations.csv": ["part4_eliminations.csv"],
}


def main() -> int:
    missing: list[str] = []
    for target, shards in SOURCES.items():
        header: list[str] | None = None
        rows: list[dict[str, str]] = []
        provenance: list[str] = []

        for shard in shards:
            path = PARTS / shard
            if not path.exists():
                missing.append(shard)
                continue
            with path.open(newline="", encoding="utf-8") as fh:
                reader = csv.DictReader(fh)
                shard_rows = [r for r in reader if any((v or "").strip() for v in r.values())]
                if reader.fieldnames is None:
                    continue
                if header is None:
                    header = list(reader.fieldnames)
                elif list(reader.fieldnames) != header:
                    print(f"  ! {shard}: header differs from {shards[0]} — not merged")
                    continue
            rows.extend(shard_rows)
            provenance.append(f"{shard}={len(shard_rows)}")

        if header is None:
            print(f"  - {target}: no shards available")
            continue

        out = DATA / target
        with out.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=header)
            writer.writeheader()
            for row in rows:
                writer.writerow({k: (row.get(k) or "") for k in header})
        print(f"  {target:<22} {len(rows):>5} rows   ({', '.join(provenance)})")

    if missing:
        print(f"\nMissing shards (agents may still be running): {missing}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
