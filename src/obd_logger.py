#!/usr/bin/env python3
"""
Superseded by the f150diag package.

This script logged a fixed set of PIDs to CSV. That capability now lives in
`f150diag live`, alongside the analysis, protocols and knowledge base that
turn a log into a finding.

    old:  python src/obd_logger.py --port /dev/ttyUSB0 --duration 60
    new:  python -m f150diag.cli --port /dev/ttyUSB0 live --seconds 60

    old:  python src/obd_logger.py --self-test
    new:  python -m f150diag.cli selftest

    old:  python src/obd_logger.py --list-ports
    new:  python -m f150diag.cli ports

See docs/TOOL.md for everything the new tool does that this one did not.
"""

import sys

MESSAGE = __doc__


def main() -> int:
    print(MESSAGE.strip(), file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
