"""Seeding the knowledge base FROM SOURCES THAT EXIST, and no others.

Nothing in this module writes a definition from memory.  Every entry carries a
source row, and the source row says what it is and how much to trust it.

FOUR SEEDS, FOUR VERY DIFFERENT QUALITIES
-----------------------------------------
standard OBD-II   python-obd 0.7.3's own tables.  Legislated, stable, and the
                  same on every vehicle.  LEVEL 1.
DTC descriptions  python-obd's 2,066-entry table.  Generic text, not Ford's
                  own wording, and NOT Ford's set/clear conditions.  LEVEL 1.
mode 06           the 2026-09-05 capture archived in data/f150.db, read off
                  SCREENSHOTS OF THE APP.  That confirms the MID/TID meanings
                  and that this PCM answers them - but a screenshot is NOT a
                  raw response, so it stops at LEVEL 3.  Promotion to 4 waits
                  for a capture through our own link.
Ford CAN          commaai/opendbc, reverse-engineered.  LEVEL 1, low
                  confidence, and - READ THIS - these are BROADCAST CAN
                  SIGNALS, not diagnostic PIDs.  They are read by sniffing the
                  bus, not by asking a module a question.  They are in the
                  knowledge base because they are Ford knowledge, not because
                  the ELM327 can fetch them.
"""

from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path

from . import kb

DBC_SIGNAL = re.compile(
    r'^\s*SG_\s+(?P<name>[\w]+)\s*:\s*(?P<start>\d+)\|(?P<len>\d+)@'
    r'(?P<order>[01])(?P<sign>[+-])\s*\((?P<factor>[^,]+),(?P<offset>[^)]+)\)\s*'
    r'\[(?P<min>[^|]*)\|(?P<max>[^\]]*)\]\s*"(?P<unit>[^"]*)"')
DBC_MESSAGE = re.compile(r'^BO_\s+(?P<id>\d+)\s+(?P<name>[\w]+)\s*:\s*(?P<dlc>\d+)')


def seed_standard_obd2(db):
    import obd
    sid = kb.add_source(
        db, 'python-obd 0.7.3 command tables', source_type='library',
        reference='obd.commands', publisher='python-OBD', licence='GPLv2',
        confidence='high',
        notes='Legislated SAE J1979 parameters. Identical across manufacturers. '
              'Scaling and units are the library\'s, not read from a Ford document.')
    n = 0
    for mode in obd.commands.modes:
        for c in mode:
            if c is None:
                continue
            svc = c.command[:2].decode()
            pid = c.command[2:].decode() or None
            if kb.add_definition(
                    db, service=svc, name=c.name, source_id=sid,
                    level=kb.DOCUMENTED, pid=pid, description=c.desc,
                    module_name='PCM', bus='HS-CAN',
                    request_format=c.command.decode(),
                    byte_len=c.bytes or None,
                    diagnostic_purpose='standard OBD-II',
                    sync_requirement='sequential; one request at a time'):
                n += 1
    return sid, n


def seed_dtc_catalogue(db):
    import obd.codes as codes
    sid = kb.add_source(
        db, 'python-obd DTC description table', source_type='library',
        reference='obd.codes.DTC', publisher='python-OBD', licence='GPLv2',
        confidence='medium',
        notes='Generic SAE descriptions. NOT Ford wording, and carries no '
              'set/clear conditions, causes or confirmation tests - those '
              'fields stay empty until a Ford source fills them.')
    rows = [(d, 'PCM', t, kb.DOCUMENTED, sid) for d, t in codes.DTC.items()]
    db.executemany(
        "INSERT OR IGNORE INTO dtc_catalogue (dtc, module, description,"
        " verification_level, source_id) VALUES (?,?,?,?,?)", rows)
    db.commit()
    return sid, len(rows)


def seed_mode06_from_archive(db, archive='data/f150.db'):
    """The 2026-09-05 capture. LEVEL 3 - screenshots, not raw frames."""
    p = Path(archive)
    if not p.exists():
        return None, 0
    sid = kb.add_source(
        db, 'mode 06 capture 2026-09-05 04:36 local', source_type='vehicle capture',
        reference='data/f150.db table mode06; images data/screenshots/m253-*',
        fetched_utc='2026-09-05T01:38:46Z', publisher='owner', confidence='high',
        notes='Read off SCREENSHOTS of the scan app, verified against the '
              'original images. Confirms the MID/TID meanings and that this '
              'PCM answers MID $A1-$A7. A screenshot is NOT a raw response, so '
              'these stop at level 3 until captured through our own link. '
              'PRE-TUNE.')
    src = sqlite3.connect(p)
    src.row_factory = sqlite3.Row
    n = 0
    for r in src.execute("SELECT monitor, mid, tid, description, value,"
                         " limit_min, limit_max, result FROM mode06"):
        mid = (r['mid'] or '').replace('MID$', '').replace('$', '')
        tid = (r['tid'] or '').replace('TID$', '').replace('$', '').strip()
        cyl = None
        m = re.search(r'Misfire Cylinder (\d)', r['monitor'] or '')
        if m:
            cyl = int(m.group(1))
        db.execute(
            "INSERT OR IGNORE INTO mode06_catalogue (mid, tid, description,"
            " module, limit_min, limit_max, system, cylinder,"
            " verification_level, source_id) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (mid, tid, '%s - %s' % (r['monitor'], r['description'] or ''),
             'PCM', r['limit_min'], r['limit_max'],
             'misfire' if cyl or 'Misfire' in (r['monitor'] or '') else
             (r['monitor'] or '').split(' Monitor')[0],
             cyl, kb.PROTOCOL_VERIFIED, sid))
        n += 1
    src.close()
    db.commit()
    return sid, n


def seed_sensor_list(db, vehicle_id, path='docs/scanner-pids.md'):
    """Channels the scan app OFFERS for this VIN. Applicability, not decoding.

    The app offering a channel says the PID is documented for this application;
    it says nothing about scaling, and blank-in-one-session is not unsupported.
    """
    p = Path(path)
    if not p.exists():
        return None, 0
    sid = kb.add_source(
        db, 'scan app sensor list for VIN 1FTMF1EM1EFC80632',
        source_type='application list', reference=str(p), publisher='owner',
        confidence='medium',
        notes='The channels the app offers for this vehicle. Establishes Ford '
              'APPLICABILITY only - no scaling, no byte layout. A channel that '
              'returned blank in one session is NOT proven unsupported.')
    names = set()
    for line in p.read_text(encoding='utf-8', errors='replace').splitlines():
        for cell in re.findall(r'`([^`]+)`', line):
            if len(cell) > 3 and not cell.startswith(('0x', 'AT ', 'python')):
                names.add(cell.strip())
    n = 0
    for name in sorted(names):
        did = kb.add_definition(
            db, service='01' if not name.startswith('[PCM]') else '22',
            name=name, source_id=sid, level=kb.FORD_APPLICATION,
            description='offered by the scan app for this VIN',
            module_name='PCM',
            diagnostic_purpose='applicability evidence only',
            sampling_notes='rate set by tiles on screen: 2 tiles ~33 Hz, '
                           '3 ~15.5 Hz, 7+ ~2 Hz')
        if did:
            db.execute("INSERT INTO pid_applicability (def_id, vehicle_id,"
                       " platform, model, year_from, year_to, engine,"
                       " transmission, module_name, protocol, applicability,"
                       " source_id) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                       (did, vehicle_id, 'Ford P415', 'F-150', 2014, 2014,
                        '3.7L Cyclone V6', '6R80', 'PCM',
                        'ISO 15765-4 11-bit 500k', 'documented', sid))
            n += 1
    db.commit()
    return sid, n


def seed_ford_can(db, dbc='data/sources/ford_lincoln_base_pt.dbc'):
    """Ford broadcast CAN signals. NOT diagnostic PIDs. Read the note."""
    p = Path(dbc)
    if not p.exists():
        return None, 0
    meta = {}
    mp = Path(str(p) + '.source.json')
    if mp.exists():
        meta = json.loads(mp.read_text())
    sid = kb.add_source(
        db, 'commaai/opendbc ford_lincoln_base_pt.dbc',
        source_type='community reverse-engineered CAN database',
        reference=p.name, url=meta.get('url'), fetched_utc=meta.get('fetched_utc'),
        publisher='commaai/opendbc', licence='MIT', confidence='low',
        sha256=meta.get('sha256'),
        notes='BROADCAST CAN SIGNALS, NOT DIAGNOSTIC PIDs. Obtained by passive '
              'sniffing, not by requesting them from a module - an ELM327 '
              'cannot fetch these the way it fetches a PID. Reverse-engineered, '
              'not Ford-official. Model-year applicability is NOT stated by the '
              'file, so it is left unknown rather than guessed.')
    msg = None
    rows = []
    for line in p.read_text(encoding='utf-8', errors='replace').splitlines():
        mm = DBC_MESSAGE.match(line)
        if mm:
            msg = mm.group('name')
            msg_id = int(mm.group('id'))
            continue
        sm = DBC_SIGNAL.match(line)
        if sm and msg:
            g = sm.groupdict()
            rows.append(dict(
                service='CAN', pid=None, name='%s.%s' % (msg, g['name']),
                description='Ford broadcast CAN signal in message %s' % msg,
                module_name=None, bus='HS-CAN',
                can_id=hex(msg_id & 0x1FFFFFFF),
                bit_start=int(g['start']), bit_len=int(g['len']),
                scale=_num(g['factor']), data_offset=_num(g['offset']),
                unit=g['unit'] or None, signed=1 if g['sign'] == '-' else 0,
                endianness='little' if g['order'] == '1' else 'big',
                normal_min=_num(g['min']), normal_max=_num(g['max']),
                diagnostic_purpose='broadcast signal - requires CAN sniffing, '
                                   'NOT reachable by an OBD-II PID request',
                sync_requirement='broadcast; arrives on the bus, not polled'))
    n = 0
    for r in rows:
        if kb.add_definition(db, r.pop('service'), r.pop('name'), sid,
                             level=kb.DOCUMENTED, **r):
            n += 1
    db.commit()
    return sid, n


def _num(s):
    try:
        return float(str(s).strip())
    except (TypeError, ValueError):
        return None


def seed_modules(db):
    """Module addresses. ONLY 7E0 HAS EVER ANSWERED IN THIS PROJECT."""
    sid = kb.add_source(
        db, 'module addressing', source_type='mixed',
        reference='7E0 observed in this project; others are convention',
        confidence='mixed',
        notes='A wrong header returns SILENCE, not a wrong number, so trying '
              'is safe - but silence must NOT be read as "the module is not '
              'there". Only 7E0 has ever replied here.')
    rows = [
        ('PCM', '7E0', '7E8', 'HS-CAN', 'ISO 15765-4 11-bit 500k',
         'Powertrain control module - the only module that has answered',
         kb.PROTOCOL_VERIFIED),
        ('TCM', '7E1', '7E9', 'HS-CAN', 'ISO 15765-4 11-bit 500k',
         'Transmission control module - address is CONVENTION, never confirmed here',
         kb.UNKNOWN),
        ('ABS', '760', '768', 'HS-CAN', 'ISO 15765-4 11-bit 500k',
         'Anti-lock brakes - address unconfirmed', kb.UNKNOWN),
        ('BCM', '726', '72E', 'MS-CAN', 'MS-CAN 125 kbps',
         'Body control module - MS-CAN, NOT reachable by python-obd '
         '(no user-defined protocol); FORScan reaches it', kb.UNKNOWN),
        ('IPC', '720', '728', 'MS-CAN', 'MS-CAN 125 kbps',
         'Instrument cluster - MS-CAN, same limitation', kb.UNKNOWN),
        ('RCM', '737', '73F', 'HS-CAN', 'ISO 15765-4 11-bit 500k',
         'Restraints control module - address unconfirmed', kb.UNKNOWN),
    ]
    n = 0
    for name, req, resp, bus, proto, desc, lvl in rows:
        cur = db.execute(
            "INSERT OR IGNORE INTO modules (name, address_req, address_resp,"
            " bus, protocol, description, verification_level, source_id)"
            " VALUES (?,?,?,?,?,?,?,?)",
            (name, req, resp, bus, proto, desc, lvl, sid))
        n += 1 if cur.rowcount else 0
    db.commit()
    return sid, n


def seed_test_procedures(db):
    """Discriminating tests. Each names what it RULES OUT, not just what it touches."""
    rows = [
        dict(name='misfire-counter-reread',
             purpose='Compare the PCM\'s own per-cylinder misfire counters '
                     'against the 2026-09-05 baseline, post-tune.',
             discriminates='a real combustion fault from a derived-channel artefact',
             instructions='Engine running and warm. Read mode 06 MID $A1-$A7, '
                          'TID $0B and $0C. Note whether codes have been cleared '
                          'or the battery disconnected since 2026-09-05 - either '
                          'RESETS these counters and voids the comparison.',
             pids_required='MONITOR_MISFIRE_CYLINDER_1..6, MONITOR_MISFIRE_GENERAL',
             condition='engine running, any load', duration_s=120,
             expected_confirm='one cylinder clearly above the others, or any '
                              'ten-cycle average above 0',
             expected_reject='all ten-cycle averages 0 and no count above ~5',
             next_on_confirm='coil-swap-discriminator on the elevated cylinder',
             next_on_reject='stop cylinder work; go to charging-under-load and '
                            'the transmission, which has never been measured moving',
             reversible=1, requires_physical_action=0),

        dict(name='coil-swap-discriminator',
             purpose='Determine whether a cylinder abnormality follows the coil.',
             discriminates='ignition coil vs everything else on that cylinder '
                           '(plug, injector, compression, valvetrain, wiring)',
             instructions='Engine OFF and cool enough to touch. Swap the '
                          'suspect cylinder\'s ignition coil with CYLINDER 3 - '
                          'not cylinder 4, whose acceleration channel is the '
                          'worst-sampled in the archive. Reconnect both '
                          'connectors fully. Start and warm to the same '
                          'condition, then repeat the identical capture.',
             pids_required='MONITOR_MISFIRE_CYLINDER_1..6 + the identical live capture',
             condition='warm idle, Park, same as the baseline capture',
             duration_s=300,
             expected_confirm='the abnormality MOVES to cylinder 3 -> the coil is faulty',
             expected_reject='the abnormality STAYS on the original cylinder -> '
                             'coil eliminated',
             next_on_confirm='replace that coil; re-measure to confirm it cleared',
             next_on_reject='swap the spark plug next, same protocol; if it '
                            'still stays, the injector; only then compression '
                            'and leak-down',
             reversible=1, requires_physical_action=1),

        dict(name='charging-under-load',
             purpose='Decide whether low idle voltage is regulation or a fault.',
             discriminates='smart-charge regulation vs an alternator not '
                           'carrying the load',
             instructions='Meter across the battery posts at warm idle. Record. '
                          'Then switch on headlights, blower on high and rear '
                          'defroster. Wait 30 seconds and record again.',
             pids_required='CONTROL_MODULE_VOLTAGE (a meter is equally good)',
             condition='warm idle', duration_s=120,
             expected_confirm='rises toward 13.5-14.5 V under load -> regulated '
                              'behaviour, charging closed',
             expected_reject='stays near 12.6 V and falls -> alternator not '
                             'carrying the load',
             next_on_confirm='close the charging question',
             next_on_reject='inspect belt, alternator output and the sense circuit',
             reversible=1, requires_physical_action=1),

        dict(name='mode22-identify-sweep',
             purpose='Verify a service 0x22 identifier against a known channel.',
             discriminates='a correct identifier from an address that merely answers',
             instructions='Run the identification WHILE SWEEPING THE QUANTITY '
                          'WIDE - for engine speed, blip the throttle through '
                          'the whole capture. At idle the same correct address '
                          'calibrates 11 % low from regression dilution.',
             pids_required='the candidate identifier + a standard channel',
             condition='engine running, quantity swept across its range',
             duration_s=300,
             expected_confirm='r-squared >= 0.99 over >= 200 samples',
             expected_reject='r-squared below 0.3 -> the address carries '
                             'something else entirely',
             next_on_confirm='promote to level 4; repeat for level 5',
             next_on_reject='try a different standard channel',
             reversible=1, requires_physical_action=1),
    ]
    n = 0
    for r in rows:
        keys = ','.join(r)
        marks = ','.join('?' * len(r))
        cur = db.execute("INSERT OR IGNORE INTO test_procedures (%s) VALUES (%s)"
                         % (keys, marks), tuple(r.values()))
        n += 1 if cur.rowcount else 0
    db.commit()
    return n


def ensure_vehicle(db):
    db.execute(
        "INSERT OR IGNORE INTO vehicles (vin, year, make, model, engine,"
        " transmission, drive, notes) VALUES (?,?,?,?,?,?,?,?)",
        ('1FTMF1EM1EFC80632', 2014, 'Ford', 'F-150 XL Regular Cab',
         '3.7L Cyclone V6 Ti-VCT', '6R80', '4x4 (owner-confirmed; VIN series '
         'code decodes 4x2 - conflict unresolved)',
         'Jeddah. Electric cooling fans, no external EGR valve, internal '
         'timing-chain-driven water pump.'))
    db.commit()
    return db.execute("SELECT vehicle_id FROM vehicles WHERE vin=?",
                      ('1FTMF1EM1EFC80632',)).fetchone()['vehicle_id']
