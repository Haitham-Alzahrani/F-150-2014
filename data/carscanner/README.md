# Car Scanner log inbox

Drop Car Scanner CSV exports here. One file per recording session, original
filename kept — the app names them by date and time, which is the only record of
when the session was taken.

## Export settings

**Format: `CSV #2 (Horizontal layout)`.**

The app offers four. Only one of them is right for this project:

| Option | Use it? | Why |
|---|---|---|
| CSV #1 (Vertical layout) | No | Long format; has to be pivoted before anything can read it. |
| **CSV #2 (Horizontal layout)** | **Yes** | One row per timestamp, one column per channel, blanks where a channel was not sampled on that pass. This is exactly what `f150diag forscan` reads, and the blanks are the honest record of the app's round-robin polling. |
| CSV #3 (Horizontal + fill gaps with previous values) | No | Forward-fills the blanks. The file then contains samples that were never measured, and nothing downstream can tell them from real ones. It would corrupt any timing result — period, lead/lag, cross-correlation — which is the main reason these logs are wanted. |
| BRC (internal Car Scanner format) | No | Proprietary. Not readable outside the app. |

**Leave "Round values in recorded data" switched OFF.** Fuel trim moves in
0.78 % steps and lambda in the third decimal; rounding destroys the resolution
the analysis depends on.

`Record location data` makes no difference either way.

## Big files — compress before uploading

GitHub's web uploader refuses anything over **25 MB**, and a long session runs
well past that. **Compress the file on the phone first.** These logs are highly
repetitive text and shrink about **15:1** — the 6.3 MB log in this folder is
355 KB gzipped, so a 35 MB export lands near 2 MB and clears every limit with
room to spare.

On Android: long-press the file in any file manager (Files by Google, MiXplorer,
ZArchiver, Solid Explorer) and choose **Compress** or **Zip**. Upload the
resulting `.zip` exactly as you would the CSV.

Logs are **stored compressed here** and read that way. `carscanner_lib.read_text`
accepts `.csv`, `.csv.gz` and `.zip` (one CSV inside) and hands back the same
text, so nothing downstream knows or cares which form arrived. The analysis was
rerun against the compressed copies and reproduces byte-identical output.

To gzip one here instead: `gzip -9 <file>.csv`.

## VIN

This truck is `1FTMF1EM1EFC80632`. The app's session list has held recordings
from at least one other vehicle (`1FTFW1E50PKE57201`). Check the VIN under the
session name before exporting, and if a foreign-VIN file lands here anyway, note
it — do not merge it into this truck's dataset.

## Reading one

```
PYTHONPATH=src python3 -m f150diag.cli forscan data/carscanner/<file>.csv
PYTHONPATH=src python3 -m f150diag.cli analyze data/carscanner/<file>.csv
```

The importer takes the first time-like column as the clock and carries unmapped
channel names through unchanged, so an unrecognised PID name is reported rather
than silently dropped.
