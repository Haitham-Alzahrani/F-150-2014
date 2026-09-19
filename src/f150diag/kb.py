"""THE DIAGNOSTIC KNOWLEDGE BASE — two layers, and a promotion rule that bites.

    FORD KNOWLEDGE BASE        definitions + applicability, never narrowed
            |  match on VIN / calibration / module / protocol
            v
    VEHICLE CAPABILITY MAP     candidates for THIS truck
            |  discover -> request -> decode -> plausibility -> cross-check
            v
    VEHICLE-VERIFIED PROFILE   levels 4-5, the only thing diagnostics may use

WHY THE LEVELS ARE ENFORCED IN CODE AND NOT BY CONVENTION
---------------------------------------------------------
A wrong identifier does not return an error.  It returns a PLAUSIBLE NUMBER,
and a plausible number condemns a good part.  This repository already carries
`DID_REGISTRY stays empty` and an empty `did_registry.json` for exactly that
reason.  So `promote()` refuses to reach level 4 without a stored raw response
from this VIN, and refuses level 5 without repeat reads AND a passed
cross-check.  A caller cannot simply assert a level.

    0 UNKNOWN                  no reliable definition
    1 DOCUMENTED               found in a source, whatever its quality
    2 FORD_APPLICATION         known to apply to a Ford platform/application
    3 PROTOCOL_VERIFIED        request/response format technically verified
    4 VEHICLE_VERIFIED         read and decoded from THIS vehicle
    5 VEHICLE_VALIDATED        read repeatedly AND cross-checked for plausibility

NOTHING IS EVER DELETED.  A definition that this truck does not support is
marked not-applicable for this vehicle and stays in the Ford layer, because the
same identifier may be correct on another 3.7 application.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

UNKNOWN, DOCUMENTED, FORD_APPLICATION, PROTOCOL_VERIFIED, \
    VEHICLE_VERIFIED, VEHICLE_VALIDATED = range(6)

LEVEL_NAMES = {
    0: 'UNKNOWN', 1: 'DOCUMENTED', 2: 'FORD_APPLICATION',
    3: 'PROTOCOL_VERIFIED', 4: 'VEHICLE_VERIFIED', 5: 'VEHICLE_VALIDATED',
}

SCHEMA = """
PRAGMA foreign_keys = ON;

-- ------------------------------------------------ knowledge layer
CREATE TABLE IF NOT EXISTS vehicles (
  vehicle_id INTEGER PRIMARY KEY, vin TEXT UNIQUE, year INTEGER, make TEXT,
  model TEXT, engine TEXT, transmission TEXT, drive TEXT, notes TEXT);

CREATE TABLE IF NOT EXISTS pid_sources (
  source_id INTEGER PRIMARY KEY, name TEXT NOT NULL, source_type TEXT,
  reference TEXT, url TEXT, fetched_utc TEXT, publisher TEXT, licence TEXT,
  confidence TEXT, sha256 TEXT, notes TEXT);

CREATE TABLE IF NOT EXISTS modules (
  module_id INTEGER PRIMARY KEY, name TEXT NOT NULL, address_req TEXT,
  address_resp TEXT, bus TEXT, protocol TEXT, description TEXT,
  verification_level INTEGER NOT NULL DEFAULT 0,
  source_id INTEGER REFERENCES pid_sources(source_id),
  UNIQUE(name, address_req, bus));

CREATE TABLE IF NOT EXISTS pid_definitions (
  def_id INTEGER PRIMARY KEY,
  service TEXT NOT NULL, pid TEXT, name TEXT NOT NULL, description TEXT,
  module_name TEXT, bus TEXT, can_id TEXT,
  request_format TEXT, response_format TEXT,
  byte_start INTEGER, byte_len INTEGER, bit_start INTEGER, bit_len INTEGER,
  formula TEXT, scale REAL, data_offset REAL, unit TEXT,
  signed INTEGER, endianness TEXT,
  min_raw REAL, max_raw REAL, normal_min REAL, normal_max REAL,
  condition_dependency TEXT, ford_interpretation TEXT, diagnostic_purpose TEXT,
  sampling_notes TEXT, sync_requirement TEXT,
  verification_level INTEGER NOT NULL DEFAULT 0,
  source_id INTEGER REFERENCES pid_sources(source_id),
  created_utc TEXT,
  UNIQUE(service, pid, name, module_name, source_id));

CREATE TABLE IF NOT EXISTS pid_applicability (
  app_id INTEGER PRIMARY KEY,
  def_id INTEGER NOT NULL REFERENCES pid_definitions(def_id),
  platform TEXT, model TEXT, year_from INTEGER, year_to INTEGER, engine TEXT,
  pcm_strategy TEXT, module_name TEXT, transmission TEXT, protocol TEXT,
  applicability TEXT,                     -- documented | verified | not_supported
  vehicle_id INTEGER REFERENCES vehicles(vehicle_id),
  source_id INTEGER REFERENCES pid_sources(source_id), notes TEXT);

CREATE TABLE IF NOT EXISTS pid_conflicts (
  conflict_id INTEGER PRIMARY KEY,
  def_a INTEGER NOT NULL REFERENCES pid_definitions(def_id),
  def_b INTEGER NOT NULL REFERENCES pid_definitions(def_id),
  field TEXT, value_a TEXT, value_b TEXT, detected_utc TEXT, resolution TEXT);

CREATE TABLE IF NOT EXISTS pid_relations (
  rel_id INTEGER PRIMARY KEY,
  def_id INTEGER NOT NULL REFERENCES pid_definitions(def_id),
  related_def_id INTEGER REFERENCES pid_definitions(def_id),
  related_name TEXT, relation TEXT);

CREATE TABLE IF NOT EXISTS dtc_catalogue (
  dtc_id INTEGER PRIMARY KEY, dtc TEXT NOT NULL, module TEXT,
  description TEXT, system TEXT, set_conditions TEXT, clear_conditions TEXT,
  freeze_frame_relevance TEXT, possible_causes TEXT, confirmation_tests TEXT,
  related_pids TEXT, related_dtcs TEXT,
  verification_level INTEGER NOT NULL DEFAULT 0,
  source_id INTEGER REFERENCES pid_sources(source_id),
  UNIQUE(dtc, module, source_id));

CREATE TABLE IF NOT EXISTS mode06_catalogue (
  entry_id INTEGER PRIMARY KEY, mid TEXT NOT NULL, tid TEXT NOT NULL,
  description TEXT, module TEXT, unit TEXT, uas_id TEXT,
  limit_min TEXT, limit_max TEXT, system TEXT, cylinder INTEGER,
  verification_level INTEGER NOT NULL DEFAULT 0,
  source_id INTEGER REFERENCES pid_sources(source_id),
  UNIQUE(mid, tid, module, source_id));

-- ------------------------------------------------ evidence layer
CREATE TABLE IF NOT EXISTS diagnostic_sessions (
  session_id INTEGER PRIMARY KEY, uuid TEXT UNIQUE,
  vehicle_id INTEGER REFERENCES vehicles(vehicle_id),
  started_utc TEXT, label TEXT, adapter TEXT, protocol TEXT,
  sim INTEGER NOT NULL DEFAULT 0, file_path TEXT, notes TEXT);

CREATE TABLE IF NOT EXISTS raw_requests (
  req_id INTEGER PRIMARY KEY,
  session_id INTEGER NOT NULL REFERENCES diagnostic_sessions(session_id),
  seq INTEGER, t_req_s REAL, module TEXT, service TEXT, pid TEXT,
  name TEXT, raw_request TEXT);

CREATE TABLE IF NOT EXISTS raw_responses (
  resp_id INTEGER PRIMARY KEY,
  req_id INTEGER NOT NULL REFERENCES raw_requests(req_id),
  t_resp_s REAL, latency_ms REAL, raw_response TEXT,
  ok INTEGER, error TEXT, connected INTEGER);

CREATE TABLE IF NOT EXISTS decoded_values (
  val_id INTEGER PRIMARY KEY,
  resp_id INTEGER NOT NULL REFERENCES raw_responses(resp_id),
  def_id INTEGER REFERENCES pid_definitions(def_id),
  name TEXT, value REAL, text_value TEXT, unit TEXT, decoder_version TEXT);

CREATE TABLE IF NOT EXISTS samples (
  sample_id INTEGER PRIMARY KEY,
  session_id INTEGER NOT NULL REFERENCES diagnostic_sessions(session_id),
  name TEXT NOT NULL, t_s REAL NOT NULL, value REAL, unit TEXT,
  source_resp_id INTEGER REFERENCES raw_responses(resp_id));

-- ------------------------------------------------ reasoning layer
CREATE TABLE IF NOT EXISTS observations (
  obs_id INTEGER PRIMARY KEY,
  session_id INTEGER REFERENCES diagnostic_sessions(session_id),
  statement TEXT NOT NULL, evidence TEXT, metric TEXT, value REAL,
  condition TEXT, created_utc TEXT);

CREATE TABLE IF NOT EXISTS hypotheses (
  hyp_id INTEGER PRIMARY KEY, obs_id INTEGER REFERENCES observations(obs_id),
  statement TEXT NOT NULL, prior REAL, posterior REAL,
  status TEXT, created_utc TEXT, updated_utc TEXT);

CREATE TABLE IF NOT EXISTS test_procedures (
  proc_id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, purpose TEXT,
  discriminates TEXT, instructions TEXT, pids_required TEXT, condition TEXT,
  duration_s REAL, expected_confirm TEXT, expected_reject TEXT,
  next_on_confirm TEXT, next_on_reject TEXT, reversible INTEGER,
  requires_physical_action INTEGER);

CREATE TABLE IF NOT EXISTS test_results (
  result_id INTEGER PRIMARY KEY,
  proc_id INTEGER REFERENCES test_procedures(proc_id),
  hyp_id INTEGER REFERENCES hypotheses(hyp_id),
  session_id INTEGER REFERENCES diagnostic_sessions(session_id),
  outcome TEXT, measured TEXT, notes TEXT, created_utc TEXT);

CREATE TABLE IF NOT EXISTS physical_actions (
  action_id INTEGER PRIMARY KEY, hyp_id INTEGER REFERENCES hypotheses(hyp_id),
  instruction TEXT NOT NULL, issued_utc TEXT, performed_utc TEXT,
  confirmed INTEGER, notes TEXT);

CREATE TABLE IF NOT EXISTS anomalies (
  anom_id INTEGER PRIMARY KEY,
  session_id INTEGER REFERENCES diagnostic_sessions(session_id),
  name TEXT NOT NULL, severity TEXT, statement TEXT,
  supports TEXT, does_not_prove TEXT, discriminating_test TEXT,
  created_utc TEXT);

-- ------------------------------------------------ state layer
CREATE TABLE IF NOT EXISTS state_snapshots (
  snap_id INTEGER PRIMARY KEY,
  vehicle_id INTEGER REFERENCES vehicles(vehicle_id),
  state_label TEXT NOT NULL,
  session_id INTEGER REFERENCES diagnostic_sessions(session_id),
  captured_utc TEXT, odometer_km REAL, km_since_reset REAL, notes TEXT);

CREATE TABLE IF NOT EXISTS baseline_values (
  base_id INTEGER PRIMARY KEY,
  vehicle_id INTEGER REFERENCES vehicles(vehicle_id),
  name TEXT NOT NULL, condition TEXT, stat TEXT, value REAL, n INTEGER,
  session_id INTEGER REFERENCES diagnostic_sessions(session_id),
  captured_utc TEXT);

CREATE TABLE IF NOT EXISTS learned_values (
  learn_id INTEGER PRIMARY KEY,
  vehicle_id INTEGER REFERENCES vehicles(vehicle_id),
  name TEXT NOT NULL, value REAL, unit TEXT, captured_utc TEXT,
  km_since_reset REAL,
  session_id INTEGER REFERENCES diagnostic_sessions(session_id));

CREATE INDEX IF NOT EXISTS ix_def_lookup ON pid_definitions(service, pid, name);
CREATE INDEX IF NOT EXISTS ix_app_def   ON pid_applicability(def_id);
CREATE INDEX IF NOT EXISTS ix_samples   ON samples(session_id, name, t_s);
CREATE INDEX IF NOT EXISTS ix_resp_req  ON raw_responses(req_id);
"""


def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def open_db(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.executescript(SCHEMA)
    db.commit()
    return db


def add_source(db, name, **kw):
    cur = db.execute(
        "INSERT INTO pid_sources (name, source_type, reference, url, fetched_utc,"
        " publisher, licence, confidence, sha256, notes)"
        " VALUES (?,?,?,?,?,?,?,?,?,?)",
        (name, kw.get('source_type'), kw.get('reference'), kw.get('url'),
         kw.get('fetched_utc'), kw.get('publisher'), kw.get('licence'),
         kw.get('confidence'), kw.get('sha256'), kw.get('notes')))
    db.commit()
    return cur.lastrowid


def add_definition(db, service, name, source_id, level=DOCUMENTED, **kw):
    """Insert a definition.  LEVEL 4 AND 5 ARE REFUSED HERE - use promote()."""
    if level >= VEHICLE_VERIFIED:
        raise ValueError(
            'level %s cannot be asserted at insert - it requires a stored raw '
            'response from the vehicle. Use promote().' % LEVEL_NAMES[level])
    cols = dict(service=service, name=name, source_id=source_id,
                verification_level=level, created_utc=now())
    cols.update({k: v for k, v in kw.items() if v is not None})
    keys = ','.join(cols)
    marks = ','.join('?' * len(cols))
    cur = db.execute("INSERT OR IGNORE INTO pid_definitions (%s) VALUES (%s)"
                     % (keys, marks), tuple(cols.values()))
    db.commit()
    if cur.lastrowid:
        return cur.lastrowid
    row = db.execute("SELECT def_id FROM pid_definitions WHERE service=? AND "
                     "name=? AND IFNULL(pid,'')=IFNULL(?,'') AND source_id=?",
                     (service, name, kw.get('pid'), source_id)).fetchone()
    return row['def_id'] if row else None


def promote(db, def_id, level, vehicle_id, resp_ids=(), cross_check=None):
    """Raise a definition's verification level.  THE GATES ARE HERE.

    level 4 needs at least one stored raw response from this vehicle.
    level 5 needs at least three, AND a cross-check that passed.
    """
    if level < VEHICLE_VERIFIED:
        raise ValueError('promote() is for levels 4 and 5 only')
    resp_ids = list(resp_ids)
    have = db.execute(
        "SELECT COUNT(*) n FROM raw_responses rr JOIN raw_requests rq"
        " ON rq.req_id = rr.req_id JOIN diagnostic_sessions s"
        " ON s.session_id = rq.session_id"
        " WHERE rr.resp_id IN (%s) AND s.vehicle_id = ? AND rr.ok = 1"
        " AND s.sim = 0" % ','.join('?' * len(resp_ids)) if resp_ids else
        "SELECT 0 n",
        (tuple(resp_ids) + (vehicle_id,)) if resp_ids else ()).fetchone()['n']
    if level == VEHICLE_VERIFIED and have < 1:
        raise PermissionError(
            'REFUSED: level 4 needs >=1 successful non-simulated raw response '
            'from this vehicle; %d supplied' % have)
    if level == VEHICLE_VALIDATED:
        if have < 3:
            raise PermissionError(
                'REFUSED: level 5 needs >=3 successful non-simulated responses '
                'from this vehicle; %d supplied' % have)
        if not cross_check:
            raise PermissionError(
                'REFUSED: level 5 needs a passed cross-check against a related '
                'signal. Bytes coming back is not evidence of meaning.')
    db.execute("UPDATE pid_definitions SET verification_level=? WHERE def_id=?",
               (level, def_id))
    db.execute("INSERT INTO pid_applicability (def_id, vehicle_id, applicability,"
               " notes) VALUES (?,?,?,?)",
               (def_id, vehicle_id, 'verified',
                'promoted to %s; cross_check=%s' % (LEVEL_NAMES[level], cross_check)))
    db.commit()
    return True


def mark_not_supported(db, def_id, vehicle_id, note=''):
    """This vehicle does not answer it.  THE DEFINITION IS NOT DELETED."""
    db.execute("INSERT INTO pid_applicability (def_id, vehicle_id, applicability,"
               " notes) VALUES (?,?,?,?)",
               (def_id, vehicle_id, 'not_supported', note))
    db.commit()


def record_conflict(db, def_a, def_b, field, value_a, value_b):
    db.execute("INSERT INTO pid_conflicts (def_a, def_b, field, value_a, value_b,"
               " detected_utc) VALUES (?,?,?,?,?,?)",
               (def_a, def_b, field, str(value_a), str(value_b), now()))
    db.commit()


def summary(db):
    out = {}
    for t in ('pid_sources', 'pid_definitions', 'pid_applicability',
              'pid_conflicts', 'modules', 'dtc_catalogue', 'mode06_catalogue',
              'diagnostic_sessions', 'raw_requests', 'raw_responses',
              'test_procedures'):
        out[t] = db.execute('SELECT COUNT(*) n FROM %s' % t).fetchone()['n']
    out['by_level'] = {
        LEVEL_NAMES[r['verification_level']]: r['n'] for r in db.execute(
            "SELECT verification_level, COUNT(*) n FROM pid_definitions"
            " GROUP BY verification_level ORDER BY verification_level")}
    return out


def report(db):
    """A readable state-of-the-knowledge-base summary."""
    s = summary(db)
    out = ['KNOWLEDGE BASE', '']
    for k in ('pid_sources', 'modules', 'pid_definitions', 'pid_applicability',
              'pid_conflicts', 'dtc_catalogue', 'mode06_catalogue',
              'test_procedures', 'diagnostic_sessions', 'raw_responses'):
        out.append('  %-22s %d' % (k, s[k]))
    out += ['', '  definitions by verification level:']
    for name in ('UNKNOWN', 'DOCUMENTED', 'FORD_APPLICATION',
                 'PROTOCOL_VERIFIED', 'VEHICLE_VERIFIED', 'VEHICLE_VALIDATED'):
        out.append('     %-20s %d' % (name, s['by_level'].get(name, 0)))
    out += ['', '  mode 06 catalogue by level (its own table):']
    for r in db.execute("SELECT verification_level v, COUNT(*) n"
                        " FROM mode06_catalogue GROUP BY v ORDER BY v"):
        out.append('     %-20s %d' % (LEVEL_NAMES[r['v']], r['n']))
    out += ['', '  sources:']
    for r in db.execute("SELECT name, source_type, confidence,"
                        " (SELECT COUNT(*) FROM pid_definitions d"
                        "  WHERE d.source_id = pid_sources.source_id) n"
                        " FROM pid_sources ORDER BY source_id"):
        out.append('     %-46s %-10s %s defs' % (r['name'][:46],
                                                 r['confidence'] or '-', r['n']))
    out += ['', '  NOTHING IS AT LEVEL 4 OR 5. Nothing has been read from the',
            '  vehicle through this tool yet, and the gates will not let a',
            '  definition claim otherwise. The mode 06 entries reach level 3',
            '  because they came from screenshots of the app reading this',
            '  truck - which confirms the MID/TID meanings, but a screenshot',
            '  is not a raw response.']
    return '\n'.join(out)


def _main():
    import sys as _sys
    path = _sys.argv[1] if len(_sys.argv) > 1 else 'data/diag.db'
    print(report(open_db(path)))


if __name__ == '__main__':
    _main()