# Screenshots — the raw evidence

**277 images, ~170 MB, every one taken at the truck.** These are the primary
source. Every number in `../readings.csv` was read off one of them.

They were preserved from an ephemeral session container. **Had they not been
copied here they would have been lost**, and the extracted readings would have
had no verifiable source behind them.

## Naming

```
m253-04_mode06.jpg
│    │  └── what it shows
│    └───── 4th image in that message
└────────── conversation message 253
```

Images uploaded after the fact are named `new-<date>-<time>_NN_<tag>.jpg`.

## The index

[`../screenshots_manifest.csv`](../screenshots_manifest.csv) — one row per image:

| Column | |
|---|---|
| `filename` | as stored here |
| `message` | conversation message it arrived in |
| `uploaded_utc` | verified against file time — median drift 1 s, max 10 s |
| `index_in_message` / `images_in_message` | position within its batch |
| `content_tag` | what the screen shows |
| `channels` | the exact scan-app channel names |
| `owner_caption` | **what the owner said when he sent it** — the condition |
| `reply_message` | the analysis message — readings cite this, not the image message |
| `extracted_rows` | **the reading and observation ids taken from this image** |
| `n_extracted_rows` | how many |
| `width` `height` | 1220 x 2712 on every image |
| `has_exif` | yes on all 277 |
| `sha256` | content hash — how re-uploads are recognised |

**Every one of the 277 images links to the rows extracted from it.** Going the
other way, a reading's `source` cites the analysis message, so
`reply_message` is the column that joins them — not `message`. That off-by-one
was found and fixed by checking rather than assuming: the first attempt linked
only 190 of 277.

`owner_caption` is the important column. It is where "this while AC on", "this
is A laps is 5 seconds", "those i P idle" and "this is from 100 to 30" live, and
those captions are the only record of the condition each capture was taken under.

## Every image is machine-readable

`python3 data/ocr_screenshots.py` OCRs each screenshot into
[`../screenshots_ocr/`](../screenshots_ocr/) and pulls fields into the manifest.

**The phone clock is no longer trapped in the pixels.** It reads on **276 of 277**
images, and it agrees with the file's EXIF capture time on **275 of those 276**.
The single exception is a one-minute OCR slip, not a conflict.

**The EXIF is the better timestamp.** Phone clock `10:26` against EXIF
`2026:09:04 22:26:11` — the same moment, but to the second, and with the AM/PM
ambiguity settled that the on-screen clock could never resolve.

Preprocessing note, because it was not obvious: the app draws values in red,
green and yellow on near-black, and **red is almost invisible under a luminance
grayscale** — a first attempt silently lost every "Completed" in the monitor
screens. Taking the brightest of the three channels per pixel keeps all colours.

## The sessions rebuild themselves from the timestamps

[`../sessions_from_exif.csv`](../sessions_from_exif.csv) — **23 capture sessions**
across **6 h 36 m**, from 22:26 on 4 September to 05:02 on the 5th, clustered on a
four-minute idle gap. Each row carries its start, end, duration, image count,
message range and content.

**The largest gap is 1 h 38 m, between 01:32:39 and 03:11:06.** That is the purge
valve replacement and the memory wipe — **visible in the file timestamps without
anyone having written it down.** The epoch boundary that the whole before-and-
after comparison rests on is now independently confirmed by the files themselves:
189 images before the repair, the rest after.

Three other gaps mark real events: 23 min after 03:25 (the relearning drive
starting), 23 min after 04:05 (returning from it), 20 min after 00:28.

## 18 images were sent twice

258 of the 277 files are unique; **18 groups covering 37 files are byte-identical
duplicates.** The owner re-sent them, which is entirely reasonable — a phone
gallery gives no way to tell what has already been sent.

The largest group matters for reading the record: **the whole 10:26-10:33 value
list was sent twice**, once at message 105 and again at message 182. It was
analysed both times. The second time the owner said *"this is old screenshot
always read phone clock"* — and he was right; the assistant had begun treating a
re-sent session as new data.

They are kept, not deduplicated. Both arrivals are part of the record and each
carries its own caption.

## Content

| Tag | Images | |
|---|---|---|
| `mode06` | 58 | On-board monitoring test results |
| `timing` | 29 | RPM against timing advance |
| `stft` | 28 | Short term fuel trim |
| `fuelcut` | 22 | Deceleration fuel cut, both banks |
| `throttle` | 20 | Throttle position |
| `commanded-afr` | 16 | Commanded equivalence ratio |
| `wot` | 14 | Wide open throttle |
| `ltft` | 11 | Long term fuel trim |
| `monitors` | 11 | Monitor status |
| `purge` | 8 | Commanded evaporative purge |
| `maf` `lambda-afr` `accelerometer` | 6 each | |
| `rpm-ac-on` `ecu-voltage` | 5 each | |
| `downstream-o2` | 4 | |
| `dtc` | 1 | The multi-module code scan |
| `misc` | 27 | Tagged by caption in the manifest |

## Adding more

### The easy route: send them in chat

The chat attachment button is a file browser — select as many as you like. That
is how all 277 of these arrived. They get named, indexed and pushed from there.

**It is also the only route where the caption travels with the images**, and the
caption is what records the condition. Prefer it.

### Bulk upload without chat: GitHub web

On a phone, open the repository in Chrome, switch on **Desktop site** (the upload
button does not exist in mobile view), navigate to `data/screenshots/inbox`, then
**Add file → Upload files**. 100 files per commit, 25 MB per file.

From a computer, clone the repo and copy the folder in directly — no limits.

### Filing what lands in the inbox

1. `python3 data/ingest_screenshots.py` — dry run, shows the plan.
2. `python3 data/ingest_screenshots.py --apply` to file them.

Optional: `--tag mode06` to force a content tag, `--session P3S-004` to attach a
session id.

### From Termux, in one command

[`../phone-upload.sh`](../phone-upload.sh) copies the phone's screenshots from a
given date into the inbox, commits and pushes:

```
bash data/phone-upload.sh 2026-09-05 idle
```

Needs `termux-setup-storage` once, and the repo cloned to `~/F-150-2014`.

### There is no upload webpage

A published page cannot store files on this account — the capabilities available
here cover shared data, republishing, downloads, connectors, presence and asking
Claude, but not file storage. A page that accepted images would have nowhere to
put them, so none was built.

**It reads EXIF capture time, falling back to file time.** It cannot read the
phone clock burned into the image, which is this project's authoritative
timestamp — so it prints every proposal for review instead of applying blindly.

**When you add images, say what condition they were taken under.** Gear, load,
warm or cold, A/C. That is the one thing no tool can recover from the file, and
it is what makes a reading usable. This project has already had to discard an
A/C condition on 81 rows because it was assumed rather than stated.
