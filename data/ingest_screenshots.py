#!/usr/bin/env python3
"""Ingest screenshots dropped into data/screenshots/inbox/.

Reads each image's capture time (EXIF DateTimeOriginal, falling back to the file
modification time), matches it against the recorded sessions, and proposes a
manifest row and a name. Nothing is renamed or moved without --apply.

    python3 data/ingest_screenshots.py            # dry run, prints the plan
    python3 data/ingest_screenshots.py --apply    # do it

The phone clock in the image is the authoritative timestamp for this project,
and this tool cannot read it. It matches on file time, which is close but not
identical, so every proposal is printed for review rather than applied blindly.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import pathlib
import re
import sys

DATA = pathlib.Path(__file__).resolve().parent
SHOTS = DATA / "screenshots"
INBOX = SHOTS / "inbox"
MANIFEST = DATA / "screenshots_manifest.csv"

#: Recognised content tags, so a name can be given at drop time.
TAGS = [
    "rpm", "stft", "ltft", "timing", "throttle", "maf", "purge", "commanded-afr",
    "upstream-o2", "downstream-o2", "lambda-afr", "calc-load", "cam",
    "ecu-voltage", "wot", "fuelcut", "mode06", "monitors", "dtc", "sensor-list",
    "accelerometer", "misc",
]


def capture_time(path: pathlib.Path) -> tuple[dt.datetime, str]:
    """Best available capture time, and where it came from."""
    try:
        from PIL import Image  # type: ignore

        with Image.open(path) as im:
            exif = im.getexif()
            for tag in (36867, 36868, 306):  # DateTimeOriginal, Digitized, DateTime
                raw = exif.get(tag)
                if raw:
                    return dt.datetime.strptime(str(raw), "%Y:%m:%d %H:%M:%S"), "exif"
    except Exception:
        pass
    return dt.datetime.fromtimestamp(path.stat().st_mtime), "mtime"


def sha(path: pathlib.Path) -> str:
    """Content hash, so a re-uploaded image is recognised whatever it is called."""
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def archive_hashes() -> dict[str, str]:
    """sha256 -> filename for everything already filed."""
    out: dict[str, str] = {}
    for p in SHOTS.iterdir():
        if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png"}:
            out[sha(p)] = p.name
    return out


def load_sessions() -> list[dict[str, str]]:
    p = DATA / "sessions.csv"
    if not p.exists():
        return []
    with p.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def guess_tag(name: str) -> str:
    low = name.lower()
    for t in TAGS:
        if t in low:
            return t
    return "misc"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="rename and record, not just plan")
    ap.add_argument("--tag", choices=TAGS, help="force a content tag for everything in the inbox")
    ap.add_argument("--session", help="session_id from sessions.csv to attach these to")
    args = ap.parse_args()

    if not INBOX.exists():
        print(f"no inbox at {INBOX}")
        return 1
    incoming = sorted(
        (p for p in INBOX.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"}),
        key=lambda p: capture_time(p)[0],
    )
    if not incoming:
        print(f"inbox is empty: {INBOX}")
        print("Drop screenshots there, then run this again.")
        return 0

    sessions = load_sessions()
    print(f"{len(incoming)} image(s) in the inbox, {len(sessions)} known sessions")

    # Re-uploading images that are already filed is expected - the owner cannot
    # tell from a phone gallery which ones were sent before. Recognise them by
    # content, not by name, and drop them.
    known = archive_hashes()
    print(f"{len(known)} image(s) already in the archive\n")

    existing = set()
    if MANIFEST.exists():
        with MANIFEST.open(newline="", encoding="utf-8") as fh:
            existing = {r["filename"] for r in csv.DictReader(fh)}

    plan, dupes, seen = [], [], set()
    for i, p in enumerate(incoming, 1):
        digest = sha(p)
        if digest in known:
            dupes.append((p, known[digest]))
            continue
        if digest in seen:
            dupes.append((p, "another file in this same batch"))
            continue
        seen.add(digest)
        when, how = capture_time(p)
        tag = args.tag or guess_tag(p.name)
        stamp = when.strftime("%Y%m%d-%H%M%S")
        name = f"new-{stamp}_{len(plan)+1:02d}_{tag}.jpg"
        plan.append((p, name, when, how, tag))
        print(f"  {p.name}")
        print(f"    -> {name}")
        print(f"       captured {when:%Y-%m-%d %H:%M:%S} (from {how}), tag={tag}")

    if dupes:
        print(f"\n{len(dupes)} duplicate(s), already filed - will be deleted:")
        for p, match in dupes[:10]:
            print(f"  {p.name}  ==  {match}")
        if len(dupes) > 10:
            print(f"  ... and {len(dupes) - 10} more")

    if not plan and not dupes:
        print("Nothing to do.")
        return 0

    if not args.apply:
        print(f"\nDry run: {len(plan)} new, {len(dupes)} duplicate.")
        print("Re-run with --apply to file the new ones and remove the duplicates.")
        print("Tip: --tag NAME forces a content tag, --session ID attaches a session.")
        return 0

    for p, _ in dupes:
        p.unlink()

    rows = []
    for src, name, when, how, tag in plan:
        if name in existing:
            print(f"  ! {name} already in the manifest - skipped")
            continue
        dest = SHOTS / name
        src.rename(dest)
        rows.append(dict(
            filename=name, original=src.name, message="uploaded_later",
            uploaded_utc=when.isoformat(timespec="seconds"), index_in_message="",
            images_in_message="", content_tag=tag,
            channels="", owner_caption=f"time source: {how}"
                     + (f"; session {args.session}" if args.session else ""),
            size_kb=round(dest.stat().st_size / 1024),
        ))
    if rows:
        write_header = not MANIFEST.exists()
        with MANIFEST.open("a", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            if write_header:
                w.writeheader()
            w.writerows(rows)
    print(f"\nfiled {len(rows)} new image(s), removed {len(dupes)} duplicate(s)")
    print(f"manifest: {MANIFEST}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
