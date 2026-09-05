# Inbox — drop new screenshots here

Upload straight into this folder from the browser:

**[Upload files here](https://github.com/Haitham-Alzahrani/F-150-2014/upload/main/data/screenshots/inbox)**

On a phone, switch Chrome to **Desktop site** first — the upload control does not
render in mobile view.

- **Upload about 90 at a time.** GitHub refuses more than 100 per commit
  ("Yowza, that's a lot of files") — 90 keeps you clear of it.
- 25 MB per file. Screenshots here run ~630 KB, so a full batch is fine.
- Tap **choose your files**, select a batch, then **Commit changes**. Repeat.

**Do not worry about sending the same image twice.** 277 screenshots are already
filed, and you cannot tell which from a phone gallery. The ingest tool compares
by content hash, not filename — anything already held is recognised and removed,
whatever it has been renamed to along the way. Upload everything and let the tool
sort it out.

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
