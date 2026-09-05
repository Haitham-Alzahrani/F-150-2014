# Inbox — drop new screenshots here

Upload straight into this folder from the browser:

**[Upload files here](https://github.com/Haitham-Alzahrani/F-150-2014/upload/main/data/screenshots/inbox)**

On a phone, switch Chrome to **Desktop site** first — the upload control does not
render in mobile view.

- Up to **100 files per commit**, 25 MB each. Screenshots here run ~630 KB.
- Drag the files in, or tap **choose your files**, then **Commit changes**.

## Then say what condition they were taken under

**This is the part no tool can recover from the file.** For each batch:

- **Gear** — P, N, D or R
- **Load** — idle, a held rpm, cruising, wide open throttle, coasting
- **Thermal** — cold start, warming up, or fully warm
- **A/C** — on or off

A screenshot without its condition is a number with no meaning. This project has
already had to discard the A/C condition on 81 rows because it was assumed from
an instruction rather than stated — so state it, even briefly.

## Filing them

```
python3 data/ingest_screenshots.py          # dry run, shows the plan
python3 data/ingest_screenshots.py --apply  # rename and add manifest rows
```

Files move up into [`../`](../) and get a row in
[`../../screenshots_manifest.csv`](../../screenshots_manifest.csv).
