#!/usr/bin/env python3
"""Validate the extracted dataset.

Checks structure, controlled vocabulary, citation presence and internal
consistency. Exits non-zero if any check fails, so it can gate a commit.

    python3 data/validate.py
"""
from __future__ import annotations

import csv
import pathlib
import re
import sys

DATA = pathlib.Path(__file__).resolve().parent

SCHEMA: dict[str, list[str]] = {
    "readings.csv": [
        "reading_id", "session_date", "phone_clock", "graph_clock", "capture_type",
        "channel_graph_header", "channel_list_label", "paired_with", "gear", "load",
        "thermal", "coolant_c", "ac", "rpm_at_capture", "value", "value_min",
        "value_max", "span", "units", "reading_method", "admissible", "epoch",
        "notes", "source",
    ],
    "sessions.csv": [
        "session_id", "session_date", "phone_clock_start", "phone_clock_end",
        "graph_clock_start", "graph_clock_end", "gear", "load", "thermal",
        "coolant_c", "engine_run_time", "channels_captured", "n_screenshots",
        "epoch", "purpose", "summary", "source",
    ],
    "subjective.csv": [
        "obs_id", "session_date", "phone_clock", "gear", "load", "thermal",
        "observation", "category", "epoch", "source",
    ],
    "timeline.csv": [
        "event_id", "event_date", "phone_clock", "event", "category",
        "effect_on_data", "source",
    ],
    "findings.csv": [
        "finding_id", "finding_date", "statement", "status", "evidence",
        "superseded_by", "reason_withdrawn", "source",
    ],
    "eliminations.csv": [
        "elim_id", "item", "verdict", "evidence", "confidence", "date", "epoch",
        "source",
    ],
}

VOCAB: dict[tuple[str, str], set[str]] = {
    ("readings.csv", "gear"): {"P", "N", "D", "R", "driving", "unknown", "n/a"},
    ("readings.csv", "capture_type"): {
        "graph_paired", "graph_single", "value_read", "mode06", "monitor_status",
        "dtc", "physical", "subjective", "calculation",
    },
    ("readings.csv", "admissible"): {"yes", "no", "unknown"},
    ("readings.csv", "epoch"): {
        "pre_purge_valve", "post_purge_valve_pre_drive", "post_drive", "unknown",
    },
    ("readings.csv", "reading_method"): {
        # curve_read   - read off the plotted trace, the only admissible graph source
        # app_minmaxavg- the app's session-cumulative Min/Avg/Max fields, inadmissible
        # value_read   - a numeric list screen, neither a curve nor a cumulative field
        # menu         - Mode 06 / monitor / DTC menus
        # owner_report - the owner's own answer, a distinct grade of evidence
        # inferred     - derived by the assistant, not read from the vehicle
        "curve_read", "app_minmaxavg", "value_read", "instantaneous", "menu",
        "owner_report", "inferred", "unknown",
    },
    ("subjective.csv", "category"): {
        "symptom", "symptom_change", "method_correction", "vehicle_fact",
        "history", "constraint",
    },
    ("timeline.csv", "category"): {
        "repair", "reset", "drive", "measurement_milestone", "prior_history",
    },
    ("findings.csv", "status"): {
        "standing", "withdrawn", "superseded", "open_question", "verify_needed",
    },
    ("eliminations.csv", "verdict"): {
        "eliminated", "cleared", "suspect", "confirmed_fault", "reopened",
        "untested",
    },
    ("eliminations.csv", "confidence"): {
        "measured", "inferred", "reported", "assumed",
    },
}

#: A citation is a bracketed transcript message number, or a document reference.
CITATION = re.compile(r"\[\d+\]|\w")

problems: list[str] = []
notes: list[str] = []


def check(name: str) -> list[dict[str, str]]:
    path = DATA / name
    if not path.exists():
        problems.append(f"{name}: MISSING")
        return []
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        problems.append(f"{name}: no data rows")
        return []

    expected = SCHEMA[name]
    actual = list(rows[0].keys())
    if actual != expected:
        missing = [c for c in expected if c not in actual]
        extra = [c for c in actual if c not in expected]
        problems.append(f"{name}: header mismatch — missing {missing}, extra {extra}")

    ids = [r[expected[0]] for r in rows]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        problems.append(f"{name}: duplicate ids {sorted(dupes)[:5]}")

    for i, row in enumerate(rows, start=2):
        for (fname, col), allowed in VOCAB.items():
            if fname != name:
                continue
            val = (row.get(col) or "").strip()
            if val and val not in allowed:
                problems.append(f"{name}:{i} {col}={val!r} not in vocabulary")
        src = (row.get("source") or "").strip()
        if not src:
            problems.append(f"{name}:{i} missing source citation")

    return rows


def main() -> int:
    counts: dict[str, int] = {}
    data: dict[str, list[dict[str, str]]] = {}
    for name in SCHEMA:
        rows = check(name)
        counts[name] = len(rows)
        data[name] = rows

    readings = data.get("readings.csv", [])

    # The app's cumulative Min/Avg/Max fields must never be marked admissible.
    for i, r in enumerate(readings, start=2):
        if r.get("reading_method") == "app_minmaxavg" and r.get("admissible") == "yes":
            problems.append(
                f"readings.csv:{i} app_minmaxavg marked admissible — "
                "those fields are session-cumulative"
            )

    # A reading with a span should have the span match max - min.
    for i, r in enumerate(readings, start=2):
        try:
            lo, hi, span = (float(r[k]) for k in ("value_min", "value_max", "span"))
        except (ValueError, KeyError):
            continue
        if abs((hi - lo) - span) > 0.011:
            problems.append(
                f"readings.csv:{i} span {span} != max {hi} - min {lo}"
            )

    # Every withdrawn finding should say why.
    for i, r in enumerate(data.get("findings.csv", []), start=2):
        if r.get("status") == "withdrawn" and not (r.get("reason_withdrawn") or "").strip():
            problems.append(f"findings.csv:{i} withdrawn without reason_withdrawn")

    # Coverage sanity: these are known to exist and must appear somewhere.
    blob = "\n".join(
        "\t".join(row.values()) for rows in data.values() for row in rows
    ).lower()
    for probe, label in [
        ("3.13", "the +3.13% idle long term trim"),
        ("2.34", "the +2.34% idle long term trim"),
        ("-0.78", "the -0.78% relearned idle trim"),
        ("96.4", "the 96.47% absolute load at WOT"),
        ("215", "the 215 g/s peak MAF"),
        ("29.38", "the fuel-cut AFR peg"),
        ("14.86", "the commanded equivalence ratio square wave"),
        ("0.371", "the bank 1 catalyst monitor value"),
        ("6832", "the peak rpm reached"),
        ("u0422", "the archived BCM communication code"),
        ("650", "the reported idle speed"),
        ("since i got it", "the owner's statement that it was never smooth"),
    ]:
        if probe not in blob:
            problems.append(f"COVERAGE: {label} ({probe!r}) not found anywhere")

    print("=" * 62)
    print("DATASET VALIDATION")
    print("=" * 62)
    for name, n in counts.items():
        print(f"  {name:<22} {n:>5} rows")
    print(f"  {'TOTAL':<22} {sum(counts.values()):>5} rows")
    print()

    if notes:
        print("Notes:")
        for n in notes:
            print(f"  - {n}")
        print()

    if problems:
        print(f"FAILED — {len(problems)} problem(s):")
        for p in problems[:60]:
            print(f"  ! {p}")
        if len(problems) > 60:
            print(f"  ... and {len(problems) - 60} more")
        return 1

    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
