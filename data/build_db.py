#!/usr/bin/env python3
"""Build data/f150.db and data/analysis_ready.csv from the CSVs.

The CSVs are the source of truth and stay human-readable. This adds what an
analysis needs on top of them: real numeric types, a wall-clock timestamp on
every reading, the capture session it belongs to, and the flat joined table.

    python3 data/build_db.py
"""
from __future__ import annotations

import csv
import datetime as dt
import pathlib
import re
import sqlite3
import sys

DATA = pathlib.Path(__file__).resolve().parent
DB = DATA / "f150.db"
FLAT = DATA / "analysis_ready.csv"

TABLES = [
    "readings", "sessions", "subjective", "timeline", "findings",
    "eliminations", "mode06", "sessions_from_exif", "screenshots_manifest",
]

#: The purge valve went in and the adaptive memory was wiped in the long gap
#: between these two captures. Readings either side are not comparable.
REPAIR_START = dt.datetime(2026, 9, 5, 1, 32, 39)
REPAIR_END = dt.datetime(2026, 9, 5, 3, 11, 6)


def num(v: str):
    """Float if the field is a bare number, else None. Never guesses."""
    if v is None:
        return None
    s = str(v).strip().replace("%", "").replace("+", "")
    if not s or s.lower() in {"unknown", "n/a", "none", ""}:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def load(name: str) -> list[dict[str, str]]:
    p = DATA / f"{name}.csv"
    if not p.exists():
        return []
    with p.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def main() -> int:
    tables = {t: load(t) for t in TABLES}

    # message number -> capture time and session, from the image EXIF
    msg_time: dict[int, dt.datetime] = {}
    msg_session: dict[int, str] = {}
    for r in tables["screenshots_manifest"]:
        try:
            t = dt.datetime.strptime(r["exif_datetime"], "%Y:%m:%d %H:%M:%S")
        except (ValueError, KeyError):
            continue
        for key in ("message", "reply_message"):
            try:
                m = int(r[key])
            except (ValueError, KeyError):
                continue
            # first image of a message defines its time
            if m not in msg_time or t < msg_time[m]:
                msg_time[m] = t
                msg_session[m] = r.get("exif_session", "")

    t0 = min(msg_time.values()) if msg_time else None

    flat = []
    for r in tables["readings"]:
        msgs = [int(m) for m in re.findall(r"\[(\d+)\]", r.get("source", ""))]
        when = next((msg_time[m] for m in msgs if m in msg_time), None)
        sess = next((msg_session[m] for m in msgs if m in msg_session), "")
        row = dict(r)
        row["msg"] = msgs[0] if msgs else None
        row["captured_at"] = when.isoformat(sep=" ") if when else ""
        row["exif_session"] = sess
        row["minutes_from_start"] = round((when - t0).total_seconds() / 60, 2) if when and t0 else None
        row["value_num"] = num(r.get("value"))
        row["min_num"] = num(r.get("value_min"))
        row["max_num"] = num(r.get("value_max"))
        row["span_num"] = num(r.get("span"))
        row["rpm_num"] = num(r.get("rpm_at_capture"))
        row["coolant_num"] = num(r.get("coolant_c"))
        row["is_admissible"] = 1 if r.get("admissible") == "yes" else 0
        # epoch straight from the clock, independent of the extraction's own label
        if when:
            row["epoch_by_time"] = ("pre_purge_valve" if when < REPAIR_START
                                    else "post_purge_valve" if when >= REPAIR_END
                                    else "during_repair")
        else:
            row["epoch_by_time"] = "unknown"
        row["channel"] = (r.get("channel_graph_header") or "").strip() or \
                         (r.get("channel_list_label") or "").strip() or "unknown"
        flat.append(row)

    if flat:
        hdr = list(flat[0].keys())
        with FLAT.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=hdr)
            w.writeheader()
            for row in flat:
                w.writerow({k: ("" if row.get(k) is None else row.get(k)) for k in hdr})

    DB.unlink(missing_ok=True)
    con = sqlite3.connect(DB)
    for name, rows in list(tables.items()) + [("analysis_ready", flat)]:
        if not rows:
            continue
        cols = list(rows[0].keys())
        quoted = ", ".join(f'"{c}"' for c in cols)
        con.execute(f'CREATE TABLE "{name}" ({quoted})')
        con.executemany(
            f'INSERT INTO "{name}" VALUES ({", ".join("?" * len(cols))})',
            [[r.get(c) for c in cols] for r in rows],
        )
    con.execute("CREATE INDEX ix_read_channel ON analysis_ready(channel)")
    con.execute("CREATE INDEX ix_read_time ON analysis_ready(captured_at)")
    con.execute("CREATE INDEX ix_read_epoch ON analysis_ready(epoch_by_time)")
    con.commit()

    print(f"{DB.name}:")
    for name, rows in list(tables.items()) + [("analysis_ready", flat)]:
        if rows:
            print(f"  {name:<24} {len(rows):>5} rows")
    timed = sum(1 for r in flat if r["captured_at"])
    numeric = sum(1 for r in flat if r["value_num"] is not None)
    print(f"\nreadings with a wall-clock time : {timed}/{len(flat)}")
    print(f"readings with a numeric value   : {numeric}/{len(flat)}")
    con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
