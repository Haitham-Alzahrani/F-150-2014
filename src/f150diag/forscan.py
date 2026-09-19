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

    # ---------------------------------------------------------------------
    # TRANSMISSION — the largest unexamined system on this truck, and every
    # channel here is Ford enhanced, so FORScan is the only way in until a
    # service 0x22 identifier is verified. See docs/MODE-22.md.
    #
    # THE EXACT FORSCAN HEADER TEXT FOR THIS VEHICLE IS NOT VERIFIED. These
    # are the plausible forms. An unmapped column is REPORTED BY NAME and
    # still carried through, so a miss is visible and costs nothing - add the
    # real header here once a FORScan export has been seen.
    # ---------------------------------------------------------------------
    "TFT": "atf_temp", "TOT": "atf_temp", "ATFTEMP": "atf_temp",
    "ATFTEMPERATURE": "atf_temp", "TRANSFLUIDTEMP": "atf_temp",
    "PCMATFTEMPERATURE": "atf_temp",

    "TSS": "turbine_speed", "TURBINESPEED": "turbine_speed",
    "TURBINESHAFTSPEED": "turbine_speed",
    "PCMACTUALTURBINESHAFTSPEED": "turbine_speed",

    "ISS": "input_shaft_speed", "INPUTSHAFTSPEED": "input_shaft_speed",
    "OSS": "output_shaft_speed", "OUTPUTSHAFTSPEED": "output_shaft_speed",

    "GEAR": "gear_cmd", "CGEAR": "gear_cmd", "COMMANDEDGEAR": "gear_cmd",
    "PCMCOMMANDEDGEAR": "gear_cmd", "TR": "trans_range",

    # commanded against measured is the whole point - keep them distinct
    "CGEARRATIO": "gear_ratio_cmd", "COMMANDEDGEARRATIO": "gear_ratio_cmd",
    "PCMCOMMANDEDGEARRATIO": "gear_ratio_cmd",
    "GEARRATIO": "gear_ratio_measured",
    "MEASUREDGEARRATIO": "gear_ratio_measured",
    "PCMMEASUREDGEARRATIO": "gear_ratio_measured",

    "TCC": "tcc_cmd", "TCCCMD": "tcc_cmd", "TCCDC": "tcc_duty",
    "TCCSLIP": "tcc_slip", "TCSLIP": "tcc_slip",
    "TORQUECONVERTERSLIP": "tcc_slip",
}

# ---------------------------------------------------------------------------
# CAR SCANNER SENSOR-LIST LABELS.
#
# The table above is FORScan's short acronyms. Car Scanner exports the long
# sensor-list labels instead, and on a real 76-column export only 11 columns
# mapped. Adding cylinder acceleration WITHOUT engine speed would break method
# rule 2 - engine speed must be on the page or a capture cannot be read - so
# the diagnostic channels are completed here.
#
# The app's own arithmetic (fuel used, distance, power-from-MAF, GPS) is
# deliberately NOT mapped: SENSOR-INVENTORY.md classifies those as the app's
# computation rather than readings from the truck.
# ---------------------------------------------------------------------------
SYNONYMS.update({
    "ENGINERPM": "rpm", "ENGINERPMX1000": "rpm_x1000",
    "VEHICLESPEED": "speed",
    "ENGINECOOLANTTEMPERATURE": "ect",
    "INTAKEAIRTEMPERATURE": "iat",
    "AMBIENTAIRTEMPERATURE": "ambient_temp",
    "MAFAIRFLOWRATE": "maf",
    "CALCULATEDENGINELOADVALUE": "engine_load",
    "ABSOLUTELOADVALUE": "abs_load",
    "THROTTLEPOSITION": "throttle",
    "ABSOLUTETHROTTLEPOSITIONB": "throttle_b",
    "TIMINGADVANCE": "timing_adv",
    "BAROMETRICPRESSURE": "baro",
    "SHORTTERMFUELTRIMBANK1": "stft_b1", "SHORTTERMFUELTRIMBANK2": "stft_b2",
    "LONGTERMFUELTRIMBANK1": "ltft_b1", "LONGTERMFUELTRIMBANK2": "ltft_b2",
    "FUELAIRCOMMANDEDEQUIVALENCERATIO": "equiv_ratio_cmd",
    "COMMANDEDEVAPORATIVEPURGE": "evap_purge",
    "CONTROLMODULEVOLTAGE": "module_volts",
    "OBDMODULEVOLTAGE": "obd_module_volts",
    "OXYGENSENSOR1WIDERANGEEQUIVALENCERATIO": "o2_s1_equiv",
    "OXYGENSENSOR5WIDERANGEEQUIVALENCERATIO": "o2_s5_equiv",
    "OXYGENSENSOR1WIDERANGECURRENTMA": "o2_s1_current",
    "OXYGENSENSOR5WIDERANGECURRENTMA": "o2_s5_current",
    "OXYGENSENSOR2BANK1VOLTAGE": "o2_b1s2_v",
    "OXYGENSENSOR2BANK2VOLTAGE": "o2_b2s2_v",
    "CATALYSTTEMPERATUREBANK1SENSOR1": "cat_temp_b1",
    "CATALYSTTEMPERATUREBANK2SENSOR1": "cat_temp_b2",
    "PCMCURRENTLYDETECTEDENGINEMISFIRE": "misfire_current",
    "PCMKNOCKSENSOR1": "knock_1", "PCMKNOCKSENSOR2": "knock_2",
    "PCMCYLINDERHEADTEMPERATURE": "cyl_head_temp",
    "PCMACTUALELECTRONICTHROTTLECONTROL": "etc_actual",
    "PCMDESIREDELECTRONICTHROTTLECONTROL": "etc_desired",
    "PCMACPRESSURE": "ac_pressure",
    "PCMFUELLEVEL": "fuel_level",
    # real readings, not app arithmetic
    "EVAPSYSTEMVAPORPRESSURE": "evap_vapor_pressure",
    "ABSOLUTEPEDALPOSITIOND": "pedal_d",
    "ABSOLUTEPEDALPOSITIONE": "pedal_e",
})

# Cylinder acceleration, generated so the six cannot drift apart by a typo.
# Also Ford enhanced, and the channel the 2026-09-17 capture was built on -
# see docs/MISFIRE-BASELINE.md for why it does NOT by itself mean a misfire.
for _n in range(1, 7):
    for _form in ("CYL%dACC", "CYL%dACCEL", "CYL%dACCELERATION",
                  "CYLINDER%dACCELERATION", "CYLINDER%dACCELERATIONVALUE",
                  "PCMCYLINDER%dACCELERATIONVALUE"):
        SYNONYMS[_form % _n] = "cyl_accel_c%d" % _n
    # the sensor-list label Car Scanner exports, normalised
    SYNONYMS["PCMCYLINDER%dACCELERATIONVALUE" % _n] = "cyl_accel_c%d" % _n
del _n, _form

TIME_KEYS = {"TIME", "PCTIME", "TIMESTAMP", "ELAPSED", "ELAPSEDTIME", "T"}

# Strip ONLY a trailing unit group, and only one whose contents hold no further
# brackets.  The previous pattern was `\s*[\(\[].*?[\)\]]\s*$`, which begins
# matching at the FIRST bracket in the header: a Car Scanner label such as
# "[PCM] Cylinder 6 Acceleration Value ()" matched from its leading "[PCM]" all
# the way to the trailing "()" and normalised to the EMPTY STRING - so every
# [PCM] channel collided on one key and none of them could ever be mapped.
_UNIT_SUFFIX = re.compile(r"\s*[\(\[][^()\[\]]*[\)\]]\s*$")
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


def tracking_metrics(samples: list[dict]) -> dict[str, float | bool]:
    """
    Reduce cam desired-versus-actual to names a protocol can branch on.

    Publishes `vct_worst_error` (the largest departure of actual from
    commanded, across every bank and cam present), `vct_pairs` and
    `vct_actual_periodic` — actual position oscillating while the command
    sits still is a hunting phaser, which is a different fault from one that
    simply cannot reach its target.
    """
    from .analysis import column, describe, find_periodicity, sample_interval

    out: dict[str, float | bool] = {}
    pairs = vct_channels(samples)
    out["vct_pairs"] = len(pairs)
    if not pairs:
        return out

    dt = sample_interval(samples)
    worst_overall = 0.0
    any_periodic = False

    for desired, actual in pairs:
        errors = [s[actual] - s[desired] for s in samples
                  if s.get(actual) is not None and s.get(desired) is not None]
        if not errors:
            continue
        worst = max(abs(e) for e in errors)
        worst_overall = max(worst_overall, worst)

        stem = actual.replace("vct_", "")
        out[f"vct_{stem}_worst_error"] = round(worst, 3)
        out[f"vct_{stem}_mean_error"] = round(sum(errors) / len(errors), 3)

        stats = describe(samples, actual)
        if stats:
            out[f"vct_{stem}_sd"] = stats.sd
        series = column(samples, actual)
        if series:
            per = find_periodicity(series, dt, min_p2p=2.0)
            out[f"vct_{stem}_periodic"] = per.periodic
            any_periodic = any_periodic or per.periodic

    out["vct_worst_error"] = round(worst_overall, 3)
    out["vct_actual_periodic"] = any_periodic
    out["vct_tracks"] = worst_overall <= 5.0 and not any_periodic
    return out
