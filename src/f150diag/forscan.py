"""
Reading FORScan exports.

FORScan and this tool cannot share an adapter — a serial port is opened by one
process at a time. So they take turns on the port and meet in the filesystem:
FORScan records what only it can read (Ford enhanced parameters, cam position
above all), exports CSV, and this module brings that into the same analysis
that runs on native logs.

FORScan saves a run as `.fsl`, its own format, or as `.csv`. Use CSV. On
Windows the saved runs live under the FORScan folder in AppData\\Roaming.
[VERIFY — path and behaviour are from search summaries, not from a machine
with FORScan installed.]

Column naming is matched by synonym rather than assumed, because the exact
header text varies with FORScan version, language and vehicle profile. Every
import reports what it mapped and what it did not, so an unrecognised column
is visible rather than silently dropped.
"""

from __future__ import annotations

import csv
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

log = logging.getLogger("f150diag.forscan")


#: FORScan parameter name -> this tool's channel name.
#: Keys are compared after upper-casing and stripping non-alphanumerics, so
#: "Long FT1 (%)", "LONGFT1" and "long_ft1" all collapse to the same key.
#:
#: [VERIFY] These are the conventional Ford PID mnemonics. Confirm each
#: against a real export from this vehicle before trusting a mapping — a
#: wrong mapping is worse than an unmapped column, because it silently
#: relabels data.
SYNONYMS: dict[str, str] = {
    # engine speed, load, air
    "RPM": "rpm", "ENGRPM": "rpm", "ENGINESPEED": "rpm",
    "LOAD": "engine_load", "LOADPCT": "engine_load", "LOADABS": "abs_load",
    "MAF": "maf", "MAFMASSAIRFLOW": "maf",
    "MAP": "map", "MAPKPA": "map",
    "IAT": "iat", "IATC": "iat",
    "BARO": "baro",
    "TP": "throttle", "TPS": "throttle", "THROTTLEPOS": "throttle",
    "APP": "accel_pedal", "TPD": "throttle_desired",
    # temperature and speed
    "ECT": "ect", "ECTC": "ect", "COOLANTTEMP": "ect",
    "VSS": "speed", "SPEED": "speed",
    "EOT": "oil_temp", "OILTEMP": "oil_temp",
    # fuel
    "SHRTFT1": "stft_b1", "STFT1": "stft_b1", "SHORTFT1": "stft_b1",
    "LONGFT1": "ltft_b1", "LTFT1": "ltft_b1",
    "SHRTFT2": "stft_b2", "STFT2": "stft_b2", "SHORTFT2": "stft_b2",
    "LONGFT2": "ltft_b2", "LTFT2": "ltft_b2",
    "FUELPW1": "fuel_pw_b1", "FUELPW2": "fuel_pw_b2",
    "FRP": "fuel_pressure", "FUELRAILPRESSURE": "fuel_pressure",
    # ignition
    "SPARKADV": "timing_adv", "SPARK": "timing_adv", "ADV": "timing_adv",
    "KNOCKRETARD": "knock_retard",
    # oxygen sensors
    "O2S11": "o2_b1s1_v", "O2B1S1": "o2_b1s1_v", "HO2S11": "o2_b1s1_v",
    "O2S12": "o2_b1s2_v", "O2B1S2": "o2_b1s2_v", "HO2S12": "o2_b1s2_v",
    "O2S21": "o2_b2s1_v", "O2B2S1": "o2_b2s1_v", "HO2S21": "o2_b2s1_v",
    "O2S22": "o2_b2s2_v", "O2B2S2": "o2_b2s2_v", "HO2S22": "o2_b2s2_v",
    # evap
    "EVAPPCT": "evap_purge", "EVAPCP": "evap_purge", "PURGEDC": "evap_purge",
    # variable cam timing — the reason to run FORScan at all
    "VCTINTACT1": "vct_int_act_b1", "VCTACTINT1": "vct_int_act_b1",
    "VCTINTDES1": "vct_int_des_b1", "VCTINTCMD1": "vct_int_des_b1",
    "VCTINTACT2": "vct_int_act_b2", "VCTACTINT2": "vct_int_act_b2",
    "VCTINTDES2": "vct_int_des_b2", "VCTINTCMD2": "vct_int_des_b2",
    "VCTEXHACT1": "vct_exh_act_b1", "VCTEXHDES1": "vct_exh_des_b1",
    "VCTEXHACT2": "vct_exh_act_b2", "VCTEXHDES2": "vct_exh_des_b2",
    "VCTERR1": "vct_err_b1", "VCTERR2": "vct_err_b2",
    # misfire
    "MISFIRE1": "misfire_c1", "MISFIRE2": "misfire_c2", "MISFIRE3": "misfire_c3",
    "MISFIRE4": "misfire_c4", "MISFIRE5": "misfire_c5", "MISFIRE6": "misfire_c6",
    "MISGENERAL": "misfire_general",
    # electrical
    "VPWR": "module_volts", "BATTV": "module_volts", "VOLT": "module_volts",
}

TIME_KEYS = {"TIME", "PCTIME", "TIMESTAMP", "ELAPSED", "ELAPSEDTIME", "T"}

_UNIT_SUFFIX = re.compile(r"\s*[\(\[].*?[\)\]]\s*$")
_NON_ALNUM = re.compile(r"[^A-Z0-9]")


def normalise(header: str) -> str:
    """'Long FT1 (%)' -> 'LONGFT1'."""
    text = _UNIT_SUFFIX.sub("", header.strip()).upper()
    return _NON_ALNUM.sub("", text)


@dataclass
class Import:
    samples: list[dict] = field(default_factory=list)
    mapped: dict[str, str] = field(default_factory=dict)     # source -> channel
    unmapped: list[str] = field(default_factory=list)
    time_column: str = ""
    source: Path | None = None

    def report(self) -> str:
        lines = [f"imported {len(self.samples)} samples from {self.source}"]
        lines.append(f"time column: {self.time_column or 'none found — using row order'}")
        lines.append(f"mapped {len(self.mapped)} channels:")
        for src, dst in sorted(self.mapped.items(), key=lambda kv: kv[1]):
            lines.append(f"  {src:<28} -> {dst}")
        if self.unmapped:
            lines.append(f"NOT mapped ({len(self.unmapped)}) — these are carried "
                         f"through under their original names:")
            for name in self.unmapped:
                lines.append(f"  {name}")
            lines.append("Add any that matter to SYNONYMS in forscan.py.")
        return "\n".join(lines)


def _parse_time(raw: str) -> float | None:
    """Accept seconds, or a clock time like 14:22:07.350."""
    raw = raw.strip()
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError:
        pass
    parts = raw.split(":")
    try:
        if len(parts) == 3:
            h, m, s = parts
            return int(h) * 3600 + int(m) * 60 + float(s)
        if len(parts) == 2:
            m, s = parts
            return int(m) * 60 + float(s)
    except ValueError:
        return None
    return None


def _sniff_dialect(text: str) -> str:
    """FORScan exports comma-separated; some locales produce semicolons."""
    head = text.splitlines()[0] if text else ""
    return ";" if head.count(";") > head.count(",") else ","


def load(path: Path) -> Import:
    """Read a FORScan CSV export into samples this tool's analysis understands."""
    text = Path(path).read_text(encoding="utf-8-sig", errors="replace")
    delimiter = _sniff_dialect(text)
    rows = list(csv.DictReader(text.splitlines(), delimiter=delimiter))
    result = Import(source=Path(path))
    if not rows:
        return result

    headers = [h for h in (rows[0].keys()) if h]
    channel_of: dict[str, str] = {}
    for header in headers:
        key = normalise(header)
        if key in TIME_KEYS and not result.time_column:
            result.time_column = header
            continue
        target = SYNONYMS.get(key)
        if target:
            channel_of[header] = target
            result.mapped[header] = target
        else:
            channel_of[header] = header.strip()
            result.unmapped.append(header)

    times: list[float | None] = []
    for row in rows:
        raw = row.get(result.time_column, "") if result.time_column else ""
        times.append(_parse_time(raw or ""))

    known = [t for t in times if t is not None]
    base = known[0] if known else 0.0

    for index, row in enumerate(rows):
        sample: dict = {}
        t = times[index]
        # FORScan rows are evenly spaced when it is polling steadily; falling
        # back to row order keeps the analysis usable but makes any period
        # reported in "samples" rather than seconds, so say so loudly.
        sample["elapsed_s"] = round(t - base, 3) if t is not None else float(index)
        for header, channel in channel_of.items():
            raw = (row.get(header) or "").strip().replace(",", ".")
            if raw in ("", "-", "n/a", "N/A", "ERROR"):
                sample[channel] = None
                continue
            try:
                sample[channel] = float(raw)
            except ValueError:
                sample[channel] = None
        result.samples.append(sample)

    if not known:
        log.warning("no usable time column — elapsed_s is row index, so any "
                    "period is in samples, not seconds")
    log.info("forscan import: %d samples, %d channels mapped, %d unmapped",
             len(result.samples), len(result.mapped), len(result.unmapped))
    return result


def vct_channels(samples: list[dict]) -> list[tuple[str, str]]:
    """Pairs of (desired, actual) cam channels present in the data."""
    present = {k for s in samples for k in s}
    pairs = []
    for bank in ("b1", "b2"):
        for cam in ("int", "exh"):
            des, act = f"vct_{cam}_des_{bank}", f"vct_{cam}_act_{bank}"
            if des in present and act in present:
                pairs.append((des, act))
    return pairs
