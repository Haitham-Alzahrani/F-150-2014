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
