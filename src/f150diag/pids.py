"""
SAE J1979 Mode 01 parameter registry.

Every entry says how many data bytes the ECU returns and how to turn them
into a number in a stated unit. Add new parameters here, not in call sites.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence


@dataclass(frozen=True)
class Pid:
    code: str                               # hex PID, e.g. "0C"
    name: str                               # short key used in CSV columns
    description: str
    unit: str
    nbytes: int
    decode: Callable[[Sequence[int]], float]

    @property
    def request(self) -> str:
        return f"01{self.code}"


def _percent_255(d):  return d[0] * 100.0 / 255.0
def _trim(d):         return (d[0] - 128) * 100.0 / 128.0
def _u16(d):          return (d[0] << 8) | d[1]


PIDS: tuple[Pid, ...] = (
    # --- fuel and mixture ------------------------------------------------
    Pid("03", "fuel_status",  "Fuel system status (raw)",   "code", 2, lambda d: float(d[0])),
    Pid("06", "stft_b1",      "Short-term fuel trim B1",    "%",    1, _trim),
    Pid("07", "ltft_b1",      "Long-term fuel trim B1",     "%",    1, _trim),
    Pid("08", "stft_b2",      "Short-term fuel trim B2",    "%",    1, _trim),
    Pid("09", "ltft_b2",      "Long-term fuel trim B2",     "%",    1, _trim),
    Pid("0A", "fuel_pressure", "Fuel rail pressure (gauge)", "kPa", 1, lambda d: d[0] * 3.0),
    Pid("44", "equiv_ratio",  "Commanded equivalence ratio", "λ",   2, lambda d: _u16(d) / 32768.0),
    Pid("5E", "fuel_rate",    "Engine fuel rate",           "L/h",  2, lambda d: _u16(d) / 20.0),

    # --- air and load ----------------------------------------------------
    Pid("04", "engine_load",  "Calculated engine load",     "%",    1, _percent_255),
    Pid("0B", "map",          "Intake manifold pressure",   "kPa",  1, lambda d: float(d[0])),
    Pid("0F", "iat",          "Intake air temperature",     "degC", 1, lambda d: d[0] - 40),
    Pid("10", "maf",          "Mass air flow",              "g/s",  2, lambda d: _u16(d) / 100.0),
    Pid("11", "throttle",     "Throttle position",          "%",    1, _percent_255),
    Pid("33", "baro",         "Barometric pressure",        "kPa",  1, lambda d: float(d[0])),
    Pid("43", "abs_load",     "Absolute load value",        "%",    2, lambda d: _u16(d) * 100.0 / 255.0),
    Pid("45", "rel_throttle", "Relative throttle position", "%",    1, _percent_255),
    Pid("47", "abs_throttle_b", "Absolute throttle position B", "%", 1, _percent_255),
    Pid("4C", "cmd_throttle", "Commanded throttle actuator", "%",   1, _percent_255),

    # --- speed, timing, temperature --------------------------------------
    Pid("05", "ect",          "Engine coolant temperature", "degC", 1, lambda d: d[0] - 40),
    Pid("0C", "rpm",          "Engine RPM",                 "rpm",  2, lambda d: _u16(d) / 4.0),
    Pid("0D", "speed",        "Vehicle speed",              "km/h", 1, lambda d: float(d[0])),
    Pid("0E", "timing_adv",   "Timing advance",             "deg",  1, lambda d: (d[0] / 2.0) - 64.0),
    Pid("5C", "oil_temp",     "Engine oil temperature",     "degC", 1, lambda d: d[0] - 40),

    # --- oxygen sensors (voltage + that sensor's short-term trim) --------
    # Mapping for a two-bank, two-sensor-per-bank engine. Confirm against the
    # supported-PID bitmap: an engine reporting via PID 1D maps differently.
    Pid("14", "o2_b1s1_v",    "O2 B1S1 voltage",            "V",    2, lambda d: d[0] / 200.0),
    Pid("15", "o2_b1s2_v",    "O2 B1S2 voltage",            "V",    2, lambda d: d[0] / 200.0),
    Pid("18", "o2_b2s1_v",    "O2 B2S1 voltage",            "V",    2, lambda d: d[0] / 200.0),
    Pid("19", "o2_b2s2_v",    "O2 B2S2 voltage",            "V",    2, lambda d: d[0] / 200.0),

    # --- EGR (expected UNSUPPORTED on the 3.7 Ti-VCT — see docs) ---------
    Pid("2C", "egr_cmd",      "Commanded EGR",              "%",    1, _percent_255),
    Pid("2D", "egr_error",    "EGR error",                  "%",    1, _trim),

    # --- EVAP ------------------------------------------------------------
    Pid("2E", "evap_purge",   "Commanded evaporative purge", "%",   1, _percent_255),
    Pid("32", "evap_vp",      "EVAP system vapour pressure", "Pa",  2,
        lambda d: (((d[0] << 8) | d[1]) - 65536 if d[0] & 0x80 else ((d[0] << 8) | d[1])) / 4.0),

    # --- electrical and housekeeping -------------------------------------
    Pid("42", "module_volts", "Control module voltage",     "V",    2, lambda d: _u16(d) / 1000.0),
    Pid("1F", "run_time",     "Run time since start",       "s",    2, _u16),
    Pid("21", "dist_mil",     "Distance with MIL on",       "km",   2, _u16),
    Pid("30", "warmups_clr",  "Warm-ups since codes cleared", "n",  1, lambda d: float(d[0])),
    Pid("31", "dist_clr",     "Distance since codes cleared", "km", 2, _u16),
    Pid("46", "ambient_temp", "Ambient air temperature",    "degC", 1, lambda d: d[0] - 40),
)

BY_NAME = {p.name: p for p in PIDS}
BY_CODE = {p.code: p for p in PIDS}


#: Named groups, so protocols can ask for a meaningful set in one word.
GROUPS: dict[str, tuple[str, ...]] = {
    "idle": ("rpm", "map", "maf", "engine_load", "throttle",
             "stft_b1", "ltft_b1", "stft_b2", "ltft_b2",
             "timing_adv", "ect"),
    "fuel": ("rpm", "stft_b1", "ltft_b1", "stft_b2", "ltft_b2",
             "equiv_ratio", "maf", "map"),
    "o2":   ("rpm", "o2_b1s1_v", "o2_b2s1_v", "o2_b1s2_v", "o2_b2s2_v",
             "stft_b1", "stft_b2"),
    "evap": ("rpm", "evap_purge", "evap_vp", "stft_b1", "stft_b2", "map"),
    "air":  ("rpm", "maf", "map", "baro", "iat", "throttle", "cmd_throttle",
             "engine_load", "abs_load"),
    "full": tuple(p.name for p in PIDS),
}


def resolve(names: Sequence[str]) -> list[Pid]:
    """Turn PID names and group names into a de-duplicated list of Pids."""
    out: list[Pid] = []
    seen: set[str] = set()
    for token in names:
        expanded = GROUPS.get(token, (token,))
        for name in expanded:
            if name in seen:
                continue
            if name not in BY_NAME:
                raise KeyError(f"unknown PID or group: {name!r}")
            seen.add(name)
            out.append(BY_NAME[name])
    return out
