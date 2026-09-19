"""ACQUISITION PLAN — what to collect, how fast, under what condition, and why.

THE RATE LAW, MEASURED ON THIS TRUCK'S OWN DATA
-----------------------------------------------
An ELM327 answers ONE REQUEST AT A TIME.  One channel sustained 33.3 Hz - a
flat 30 ms per request.  That 30 ms is the round trip and it DOES NOT DIVIDE:

    per-channel rate  ~=  33 / N          for N polled channels

So a twelve-channel "idle group" samples each channel at 2.8 Hz.  That is fine
for fuel trims, which step in 0.78 % and move over seconds.  It is useless for
engine-speed rate of change, engine orders or 0.24 s misfire events.

`plan()` computes this and REFUSES TO PRETEND.  A group whose question needs
more bandwidth than its channel count allows is reported as under-sampled, with
the split that would fix it.

COUNTERS ARE NOT STREAMS
------------------------
Mode 06 misfire counters are cumulative.  They are read once, before and after
a change - never polled in a group.  Putting them in a live group costs
bandwidth and answers nothing, because a counter does not have to be caught in
the act.
"""

from __future__ import annotations

# Measured: 1 channel = 33.3 Hz, flat 30.0 ms (data/carscanner/2026-09-14-rate-test).
ROUND_TRIP_MS = 30.0

#: Questions and the bandwidth each one actually needs.
BANDWIDTH_NEED_HZ = {
    'engine speed rate of change': 16.0,
    'engine orders / periodicity': 16.0,
    'misfire event shape (0.24 s)': 16.0,
    'idle oscillation (0.3 Hz)': 3.0,
    'fuel trim behaviour': 1.0,
    'temperature behaviour': 0.5,
    'cam phasing response': 4.0,
    'transmission shift behaviour': 5.0,
    'charging behaviour': 1.0,
    'applicability / presence': 0.2,
}

#: One entry per subsystem. `channels` are python-obd command names unless the
#: name is marked ford:, which means service 0x22 and NOT YET REACHABLE.
PLAN = {
    'ENGINE_IDLE_CONTEXT': dict(
        question='fuel trim behaviour',
        service='01',
        channels=['RPM', 'MAF', 'ENGINE_LOAD', 'ABSOLUTE_LOAD', 'THROTTLE_POS',
                  'COOLANT_TEMP', 'INTAKE_TEMP', 'SHORT_FUEL_TRIM_1',
                  'SHORT_FUEL_TRIM_2', 'LONG_FUEL_TRIM_1', 'LONG_FUEL_TRIM_2',
                  'TIMING_ADVANCE', 'COMMANDED_EQUIV_RATIO',
                  'CONTROL_MODULE_VOLTAGE'],
        duration_s=180, condition='warm idle, Park, throttle untouched',
        simultaneous_with=None,
        calculate=['mean', 'median', 'sd', 'p2p', 'coefficient_of_variation',
                   'bank_difference(short+long, per bank)', 'trend'],
        abnormal_if=['total correction per bank outside -10..+10 %',
                     'bank difference > 5 % sustained',
                     'commanded equivalence ratio far from stoichiometric at idle'],
        follow_up='bank-specific: swap upstream oxygen sensors and re-measure; '
                  'both banks: unmetered air or fuel supply'),

    'ENGINE_SPEED_FAST': dict(
        question='engine speed rate of change',
        service='01',
        channels=['RPM'],
        duration_s=300, condition='warm idle, Park, throttle untouched',
        simultaneous_with=None,
        calculate=['rate_of_change at fixed 0.3 s bandwidth', 'p2p', 'orders',
                   'event detection', 'rolling sd'],
        abnormal_if=['median rate of change far above a healthy reference',
                     'periodic structure at a half or whole engine order'],
        follow_up='if elevated, pair with one cylinder channel at a time'),

    'MISFIRE_COUNTERS': dict(
        question='applicability / presence',
        service='06',
        channels=['MONITOR_MISFIRE_CYLINDER_1..6', 'MONITOR_MISFIRE_GENERAL'],
        duration_s=0, condition='engine running, any; counters are cumulative',
        simultaneous_with=None, counters=True,
        calculate=['per-cylinder TID 0B (ten-cycle average) and TID 0C (counts)',
                   'delta against the 2026-09-05 baseline'],
        abnormal_if=['any ten-cycle average above 0',
                     'one cylinder far above the others'],
        follow_up='elevated cylinder -> discriminating swap against cylinder 3'),

    'CYLINDER_BALANCE': dict(
        question='misfire event shape (0.24 s)',
        service='22',
        channels=['ford:cylinder_acceleration_1..6'],
        duration_s=60, condition='warm idle, Park, one cylinder at a time',
        simultaneous_with=['RPM'],
        requires=['service 0x22 identifier verified on this VIN'],
        calculate=['mean', 'median', 'sd', 'rms', 'percent negative',
                   'cylinder-to-cylinder difference', 'stability across thirds',
                   'bootstrap rank confidence'],
        abnormal_if=['one cylinder consistently lowest across thirds AND '
                     'corroborated by the mode 06 counter'],
        follow_up='NEVER conclude from this channel alone - it is derived, '
                  'dimensionless, and its six values do not sum to zero'),

    'FUEL_AIR': dict(
        question='fuel trim behaviour', service='01',
        channels=['RPM', 'MAF', 'SHORT_FUEL_TRIM_1', 'SHORT_FUEL_TRIM_2',
                  'LONG_FUEL_TRIM_1', 'LONG_FUEL_TRIM_2',
                  'COMMANDED_EQUIV_RATIO', 'O2_S1_WR_CURRENT',
                  'EVAPORATIVE_PURGE', 'ABSOLUTE_LOAD'],
        duration_s=180, condition='warm idle, then 1200 rpm held',
        simultaneous_with=None,
        calculate=['airflow plausibility: mass air flow against load and speed',
                   'total correction per bank', 'purge influence'],
        abnormal_if=['mass air flow implausible for speed and load',
                     'trims move with purge commanded'],
        follow_up='mechanical vacuum gauge - manifold pressure is unavailable '
                  'on this truck'),

    'VVT_CAM': dict(
        question='cam phasing response', service='22',
        channels=['ford:vct_commanded_b1', 'ford:vct_actual_b1',
                  'ford:vct_commanded_b2', 'ford:vct_actual_b2'],
        duration_s=120, condition='warm idle, then a slow throttle sweep',
        simultaneous_with=['RPM'],
        requires=['service 0x22 identifiers, or a FORScan log'],
        calculate=['commanded minus actual error per bank', 'response lag',
                   'bank-to-bank difference'],
        abnormal_if=['sustained error on one bank', 'slow or hunting response'],
        follow_up='FORScan is the practical route - it already reads these'),

    'TRANSMISSION': dict(
        question='transmission shift behaviour', service='22',
        channels=['ford:atf_temp', 'ford:turbine_speed', 'ford:output_shaft_speed',
                  'ford:commanded_gear', 'ford:measured_gear_ratio',
                  'ford:tcc_slip'],
        duration_s=900, condition='MOVING - every archived sample is at a '
                                  'standstill, where measured ratio clamps',
        simultaneous_with=['RPM', 'SPEED'],
        requires=['service 0x22 identifiers, or a FORScan log', 'a drive'],
        calculate=['commanded against measured ratio', 'converter slip',
                   'shift timing', 'ratio error per gear'],
        abnormal_if=['measured ratio departs from commanded while moving',
                     'converter clutch slip outside expectation when locked'],
        follow_up='largest unexamined system on this truck'),

    'ELECTRICAL': dict(
        question='charging behaviour', service='01',
        channels=['CONTROL_MODULE_VOLTAGE', 'RPM'],
        duration_s=120,
        condition='warm idle; then headlights, blower high, rear defroster ON',
        simultaneous_with=None,
        calculate=['mean', 'min', 'max', 'sd', 'percent in 13.5-14.5 V',
                   'delta when electrical load applied'],
        abnormal_if=['stays at ~12.6 V under load and falls'],
        follow_up='a meter across the battery posts answers this without a '
                  'scanner and is the cheapest ten minutes available'),

    'THERMAL': dict(
        question='temperature behaviour', service='01',
        channels=['COOLANT_TEMP', 'INTAKE_TEMP', 'AMBIANT_AIR_TEMP',
                  'CATALYST_TEMP_B1S1', 'CATALYST_TEMP_B2S1', 'RPM'],
        duration_s=1200, condition='from cold start through warm-up',
        simultaneous_with=None,
        calculate=['warm-up rate', 'thermal consistency between sensors',
                   'catalyst bank difference'],
        abnormal_if=['coolant and intake disagree implausibly when cold-soaked',
                     'warm-up far slower than expected'],
        follow_up='the live catalyst channels track within 0.1 C and CANNOT '
                  'discriminate banks - use the mode 06 catalyst monitor'),
}


def plan(group_name, round_trip_ms=ROUND_TRIP_MS):
    """Return the group with its REAL per-channel rate and an honest verdict."""
    g = dict(PLAN[group_name])
    # Channels named under `simultaneous_with` MUST be polled in the same
    # rotation, so they consume the same bandwidth. Counting only `channels`
    # understated every group that has them - which flattered exactly the
    # groups whose whole point is cross-channel comparison.
    chans = list(g['channels']) + list(g.get('simultaneous_with') or [])
    n = 0
    for c in chans:
        n += 6 if '1..6' in c else 1
    per_channel_hz = (1000.0 / round_trip_ms) / n if n else 0.0
    need = BANDWIDTH_NEED_HZ.get(g['question'], 1.0)
    g['n_channels'] = n
    g['per_channel_hz'] = round(per_channel_hz, 2)
    g['needed_hz'] = need
    if g.get('counters'):
        g['verdict'] = 'COUNTERS - read once, not polled. Rate is irrelevant.'
    elif per_channel_hz >= need:
        g['verdict'] = 'OK - %0.2f Hz per channel meets the %0.1f Hz this ' \
                       'question needs' % (per_channel_hz, need)
    else:
        max_ch = max(1, int((1000.0 / round_trip_ms) // need))
        g['verdict'] = (
            'UNDER-SAMPLED - %0.2f Hz per channel, but this question needs '
            '%0.1f Hz. At most %d channel(s) can be polled together for it. '
            'SPLIT: run the fast channels alone, and the slow context '
            'separately.' % (per_channel_hz, need, max_ch))
    return g


def report(round_trip_ms=ROUND_TRIP_MS):
    lines = ['ACQUISITION PLAN - round trip %.0f ms (%.1f Hz single channel)'
             % (round_trip_ms, 1000.0 / round_trip_ms), '']
    for name in PLAN:
        g = plan(name, round_trip_ms)
        lines.append('%s' % name)
        lines.append('   question   %s (needs %.1f Hz)' % (g['question'], g['needed_hz']))
        lines.append('   channels   %d  ->  %.2f Hz each' % (g['n_channels'], g['per_channel_hz']))
        lines.append('   condition  %s' % g['condition'])
        if g.get('requires'):
            lines.append('   REQUIRES   %s' % '; '.join(g['requires']))
        lines.append('   %s' % g['verdict'])
        lines.append('')
    return '\n'.join(lines)
