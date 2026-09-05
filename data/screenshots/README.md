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

`owner_caption` is the important column. It is where "this while AC on", "this
is A laps is 5 seconds", "those i P idle" and "this is from 100 to 30" live, and
those captions are the only record of the condition each capture was taken under.

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
