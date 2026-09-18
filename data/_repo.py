"""Windows and working-directory safety. Import this FIRST in every tool here.

TWO THINGS BREAK THESE TOOLS OUTSIDE A LINUX SHELL SITTING IN THE REPO ROOT,
and both were measured on 2026-09-18 rather than guessed.

1. CONSOLE ENCODING.  The channel names in these logs contain U+2103 (the single
   character '℃'), and the tool output contains arrows, ticks and em dashes.
   NONE of those encode in cp437, cp850 or cp1252 - the codepages a Windows
   console actually runs.  Python writes Unicode straight to a Windows CONSOLE
   through the wide API, so typing a command by hand often looks fine; but as
   soon as output is REDIRECTED OR PIPED - which is what happens when an agent
   runs the command and captures the result - stdout falls back to the locale
   codepage and raises UnicodeEncodeError mid-table.
   `utf8()` forces UTF-8 on stdout and stderr so both cases behave.

2. RELATIVE PATHS.  The globs were written as 'data/carscanner/**/*', relative
   to the current directory.  Run from anywhere else and they match nothing, and
   the tool prints an empty table and exits 0 - the same "looks like it worked"
   failure this project has already had twice.  `ROOT` anchors every path to the
   repository instead, so the tools work from any directory.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def utf8():
    """Make stdout/stderr UTF-8 whatever the console codepage is."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding='utf-8', errors='replace')
        except (AttributeError, ValueError):
            pass          # already wrapped, or a stream that cannot reconfigure


def data_globs():
    """Every log in the repository, whatever directory the tool was run from.

    Covers .csv, .csv.gz and .zip - a '*.csv' sweep once read 2 of 12 files.
    """
    return [str(ROOT / 'data' / '**' / '*'), str(ROOT / 'logs' / '**' / '*')]
