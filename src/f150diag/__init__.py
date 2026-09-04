"""
f150diag — adaptive OBD-II diagnostics for a 2014 Ford F-150 3.7L Ti-VCT.

Read-only. Services 01, 03, 06, 07, 09, 0A and 22 are all reads. Service 04
(clear codes) is deliberately not implemented: clearing destroys the freeze
frame and the permanent-code history a diagnosis depends on.
"""

__version__ = "0.1.0"
