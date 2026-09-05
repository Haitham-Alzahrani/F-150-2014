#!/usr/bin/env python3
"""Make the screenshots machine-readable.

Runs OCR over every image in data/screenshots/, writes the full text beside it in
data/screenshots_ocr/, and pulls the fields worth having as columns back into
screenshots_manifest.csv.

The phone clock burned into the status bar is this project's authoritative
timestamp and was previously only recoverable from the owner's captions. This
reads it directly.

    python3 data/ocr_screenshots.py            # all images missing OCR text
    python3 data/ocr_screenshots.py --force    # redo everything
"""
from __future__ import annotations

import argparse
import csv
import pathlib
import re
import subprocess
import sys
import tempfile

from PIL import Image, ImageChops, ImageOps

DATA = pathlib.Path(__file__).resolve().parent
SHOTS = DATA / "screenshots"
OCRDIR = DATA / "screenshots_ocr"
MANIFEST = DATA / "screenshots_manifest.csv"

#: The scan app draws values in red, green and yellow on a near-black ground.
#: Red is almost invisible under a luminance grayscale, so take the brightest
#: channel per pixel instead - that keeps every colour of text legible.
def prepare(im: Image.Image) -> Image.Image:
    r, g, b = im.convert("RGB").split()
    mx = ImageChops.lighter(ImageChops.lighter(r, g), b)
    mx = ImageOps.autocontrast(mx)
    inv = ImageOps.invert(mx)
    return inv.resize((inv.width * 2, inv.height * 2), Image.LANCZOS)


def ocr(img: Image.Image, psm: str) -> str:
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tf:
        img.save(tf.name)
        try:
            out = subprocess.run(
                ["tesseract", tf.name, "stdout", "--psm", psm],
                capture_output=True, text=True, timeout=120,
            )
            return out.stdout
        finally:
            pathlib.Path(tf.name).unlink(missing_ok=True)


TIME = re.compile(r"\b([0-2]?\d:[0-5]\d)\b")
BATT = re.compile(r"\b(\d{1,3})\s*%")
PING = re.compile(r"Ping[:\s]+(\d+)\s*ms", re.I)
MINAVGMAX = re.compile(
    r"Min[:\s]+(-?[\d.]+).{0,40}?Avg[:\s]+(-?[\d.]+).{0,40}?Max[:\s]+(-?[\d.]+)",
    re.I | re.S,
)


def exif_datetime(path: pathlib.Path) -> str:
    try:
        with Image.open(path) as im:
            ex = im.getexif()
            for tag in (36867, 36868, 306):
                v = ex.get(tag)
                if v:
                    return str(v)
    except Exception:
        pass
    return ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="re-OCR images already done")
    ap.add_argument("--limit", type=int, help="stop after this many (for testing)")
    args = ap.parse_args()

    OCRDIR.mkdir(exist_ok=True)
    images = sorted(p for p in SHOTS.iterdir() if p.suffix.lower() == ".jpg")
    if args.limit:
        images = images[: args.limit]

    fields: dict[str, dict[str, str]] = {}
    done = skipped = 0
    for i, p in enumerate(images, 1):
        txt_path = OCRDIR / (p.stem + ".txt")
        if txt_path.exists() and not args.force:
            text = txt_path.read_text(encoding="utf-8")
            skipped += 1
        else:
            with Image.open(p) as im:
                full = prepare(im)
                # The status bar is small and benefits from its own pass.
                bar = prepare(im.crop((0, 0, min(700, im.width), 110)))
            body = ocr(full, "4")
            if len(body.strip()) < 40:
                body = ocr(full, "6")
            barred = ocr(bar, "7")
            text = f"### status bar\n{barred.strip()}\n\n### page\n{body.strip()}\n"
            txt_path.write_text(text, encoding="utf-8")
            done += 1
            if done % 25 == 0:
                print(f"  ... {i}/{len(images)}", flush=True)

        bar_part = text.split("### page")[0]
        clock = TIME.search(bar_part)
        batt = BATT.search(bar_part)
        ping = PING.search(text)
        mam = MINAVGMAX.search(text)
        fields[p.name] = dict(
            phone_clock_ocr=clock.group(1) if clock else "",
            battery_pct_ocr=batt.group(1) if batt else "",
            ping_ms_ocr=ping.group(1) if ping else "",
            app_min_ocr=mam.group(1) if mam else "",
            app_avg_ocr=mam.group(2) if mam else "",
            app_max_ocr=mam.group(3) if mam else "",
            exif_datetime=exif_datetime(p),
            ocr_chars=str(len(text)),
        )

    print(f"\nOCR: {done} new, {skipped} already had text")

    rows = list(csv.DictReader(MANIFEST.open(newline="", encoding="utf-8")))
    hdr = list(rows[0].keys())
    for c in ("phone_clock_ocr", "battery_pct_ocr", "ping_ms_ocr",
              "app_min_ocr", "app_avg_ocr", "app_max_ocr",
              "exif_datetime", "ocr_chars", "ocr_text_file"):
        if c not in hdr:
            hdr.append(c)
    hit = 0
    for r in rows:
        f = fields.get(r["filename"])
        if not f:
            continue
        r.update(f)
        r["ocr_text_file"] = f"screenshots_ocr/{pathlib.Path(r['filename']).stem}.txt"
        if f["phone_clock_ocr"]:
            hit += 1
    with MANIFEST.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=hdr)
        w.writeheader()
        w.writerows(rows)

    print(f"phone clock read from {hit}/{len(rows)} images")
    return 0


if __name__ == "__main__":
    sys.exit(main())
