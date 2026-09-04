"""Command line entry point for the F-150 diagnostic tool."""

from __future__ import annotations

import argparse
import csv
import json
import logging
import sys
from pathlib import Path

from . import (analysis, forscan, forscan_control, knowledge,
               pids as pidmod, runner, services)
from .transport import Elm327, available_ports

REPO = Path(__file__).resolve().parents[2]
PROTOCOL_DIR = REPO / "protocols"
KNOWLEDGE_DIR = REPO / "knowledge"
LOG_DIR = REPO / "logs"

log = logging.getLogger("f150diag")


def configure_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stderr,
    )


def connect(args) -> Elm327:
    if not args.port:
        raise SystemExit("no --port given. Run `ports` to see what is available.")
    elm = Elm327(args.port, baud=args.baud)
    elm.open()
    return elm


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_ports(args) -> int:
    found = available_ports()
    if not found:
        print("no serial ports visible to this machine")
        return 1
    for device, description in found:
        print(f"{device:<24} {description}")
    return 0


def cmd_survey(args) -> int:
    with connect(args) as elm:
        cap = services.survey(elm)
    print(f"adapter        : {cap.adapter}")
    print(f"protocol       : {cap.protocol}")
    print(f"VIN (reported) : {cap.vin}")
    print(f"calibrations   : {', '.join(cap.calibrations) or 'none reported'}")
    print(f"\nsupported ({len(cap.supported)}):")
    print("  " + ", ".join(cap.supported))
    print(f"\nNOT supported ({len(cap.unsupported)}):")
    print("  " + ", ".join(cap.unsupported))
    if "egr_cmd" in cap.unsupported:
        print("\nNote: EGR parameters are not supported by this vehicle — consistent")
        print("with the 3.7 Ti-VCT having no external EGR valve. This is a")
        print("measurement, not an assumption.")
    return 0


def cmd_dtc(args) -> int:
    with connect(args) as elm:
        stored = services.stored_dtcs(elm)
        pending = services.pending_dtcs(elm)
        permanent = services.permanent_dtcs(elm)

    kb = knowledge.KnowledgeBase.load(KNOWLEDGE_DIR)
    for title, codes in (("stored (service 03)", stored),
                         ("pending (service 07)", pending),
                         ("permanent (service 0A)", permanent)):
        print(f"\n{title}: {', '.join(codes) if codes else 'none'}")
        for code in codes:
            for issue in kb.by_code(code):
                print(f"    {code} → {issue.id}: {issue.title}")

    if not (stored or pending or permanent):
        print("\nNo codes of any kind. Note that a battery disconnect wipes stored")
        print("and pending codes but NOT permanent ones — an empty permanent list")
        print("is real history, not a cleared one.")
    return 0


def cmd_live(args) -> int:
    from .recorder import measure
    selected = pidmod.resolve(args.pids)
    with connect(args) as elm:
        rec = measure(elm, selected, args.seconds, LOG_DIR, args.label)
    m = analysis.metrics(rec.samples)
    _print_metrics(m)
    print(f"\nwrote {rec.csv_path}")
    return 0


def cmd_analyze(args) -> int:
    samples = _read_samples(Path(args.file))
    if not samples:
        print("no samples in that file")
        return 1
    m = analysis.metrics(samples)
    _print_metrics(m)

    dt = analysis.sample_interval(samples)
    for a, b in (("stft_b1", "rpm"), ("stft_b2", "rpm"), ("map", "rpm")):
        ll = analysis.lead_lag(samples, a, b, dt)
        if ll:
            print(f"\n{a} vs {b}: lag {ll.lag_s}s  r={ll.correlation}")
            print(f"  {ll.verdict}")
    return 0


def cmd_forscan(args) -> int:
    """Import a FORScan CSV export and run the same analysis as a native log."""
    result = forscan.load(Path(args.file))
    print(result.report())
    if not result.samples:
        return 1

    m = analysis.metrics(result.samples)
    _print_metrics(m)

    dt = analysis.sample_interval(result.samples)
    for a, b in (("stft_b1", "rpm"), ("stft_b2", "rpm")):
        ll = analysis.lead_lag(result.samples, a, b, dt)
        if ll:
            print(f"\n{a} vs {b}: lag {ll.lag_s}s  r={ll.correlation}")
            print(f"  {ll.verdict}")

    pairs = forscan.vct_channels(result.samples)
    if not pairs:
        print("\nNo cam position channels found in this export.")
        print("Log VCT desired and actual for both banks in FORScan — tracking")
        print("error at idle is the one thing this tool cannot measure itself.")
        return 0

    print("\nCAM TIMING TRACKING")
    for desired, actual in pairs:
        des = analysis.describe(result.samples, desired)
        act = analysis.describe(result.samples, actual)
        if not des or not act:
            continue
        errors = [s[actual] - s[desired] for s in result.samples
                  if s.get(actual) is not None and s.get(desired) is not None]
        if not errors:
            continue
        worst = max(abs(e) for e in errors)
        mean_err = sum(errors) / len(errors)
        act_per = analysis.find_periodicity(
            [s[actual] for s in result.samples if s.get(actual) is not None], dt)
        print(f"\n  {desired} -> {actual}")
        print(f"    desired mean {des.mean}  actual mean {act.mean}")
        print(f"    tracking error: mean {mean_err:.2f}  worst {worst:.2f}")
        print(f"    actual position sd {act.sd}, periodic={act_per.periodic}")
        if worst > 5:
            print("    → actual departs from commanded by more than 5 degrees.")
            print("      Swap the VCT solenoids bank to bank: if it follows the")
            print("      solenoid it is the solenoid, if it stays it is the")
            print("      phaser, chain or oil supply.")
        elif act_per.periodic:
            print(f"    → cam position oscillates ({act_per.period_s}s period)")
            print("      while commanded is steady — hunting phaser control.")
        else:
            print("    → tracks commanded position. No VCT fault evident here.")
    return 0


def cmd_forscan_status(args) -> int:
    """Where FORScan is, whether it is running, and where its exports land."""
    exe = forscan_control.find_executable()
    data = forscan_control.data_directory()
    print(f"executable : {exe or 'not found — set FORSCAN_EXE'}")
    print(f"data folder: {data or 'not found — set FORSCAN_DATA'}")
    print(f"running    : {forscan_control.is_running()}")
    roots = forscan_control.search_roots()
    print("\nwatched for exports:")
    for root in roots:
        print(f"  {root}")
    if not roots:
        print("  none — set FORSCAN_DATA, or exports will not be found")
    recent = forscan_control.newest_export(since=0.0, roots=roots)
    if recent:
        import datetime as _dt
        when = _dt.datetime.fromtimestamp(recent.modified).isoformat(timespec="seconds")
        print(f"\nmost recent export: {recent.path}  ({when})")
    print("\nParameter sets this tool knows how to ask FORScan for:")
    for name, pids in sorted(forscan_control.REQUESTS.items()):
        print(f"  {name:<10} {', '.join(pids)}")
    return 0


def cmd_protocols(args) -> int:
    protos = runner.load_all(PROTOCOL_DIR)
    for proto in protos.values():
        problems = proto.validate()
        flag = "  ✗ " + "; ".join(problems) if problems else ""
        print(f"{proto.id:<24} {proto.title}{flag}")
    return 0


def cmd_run(args) -> int:
    protos = runner.load_all(PROTOCOL_DIR)
    proto = protos.get(args.protocol)
    if proto is None:
        print(f"unknown protocol {args.protocol!r}. Known: {', '.join(protos)}")
        return 1

    if not args.dry_run and forscan_control.is_running():
        print("FORScan appears to be running and will be holding the adapter.")
        print("Close it before starting — a serial port is opened by one")
        print("process at a time.")
        return 1

    elm = None if args.dry_run else connect(args)
    session = runner.Session(
        elm=elm, out_dir=LOG_DIR, dry_run=args.dry_run,
        reconnect=(None if args.dry_run else lambda: connect(args)))
    try:
        findings = session.run(proto)
    finally:
        if elm:
            elm.close()

    print("\n" + "=" * 70)
    print("FINDINGS")
    print("=" * 70)
    if not findings:
        print("none recorded")
    kb = knowledge.KnowledgeBase.load(KNOWLEDGE_DIR)
    for f in findings:
        print(f"\n• {f.summary}")
        if f.detail:
            print(f"  {f.detail}")
        issue = kb.issues.get(f.id)
        if issue:
            print(knowledge.render(issue))

    transcript = LOG_DIR / f"session-{proto.id}.txt"
    transcript.write_text("\n".join(session.transcript), encoding="utf-8")
    print(f"\ntranscript: {transcript}")
    return 0


def cmd_kb(args) -> int:
    kb = knowledge.KnowledgeBase.load(KNOWLEDGE_DIR)
    if args.action == "list":
        print(knowledge.summarise(sorted(kb.issues.values(), key=lambda i: i.id)))
    elif args.action == "show":
        issue = kb.issues.get(args.term or "")
        if not issue:
            print(f"no issue with id {args.term!r}")
            return 1
        print(knowledge.render(issue))
    elif args.action == "search":
        print(knowledge.summarise(kb.search(args.term or "")))
    elif args.action == "verify":
        queue = kb.verification_queue()
        verified = sum(1 for i in kb.issues.values() if i.is_verified)
        print(f"{len(kb.issues)} issues, {verified} with at least one source "
              f"somebody actually opened.\n")
        if not queue:
            print("Nothing outstanding.")
            return 0
        print(f"{len(queue)} claims still resting on an unopened source:\n")
        current = None
        for issue, source in queue:
            if issue.id != current:
                current = issue.id
                print(f"\n{issue.id}  —  {issue.title}")
            print(f"  [{source.source}/{source.confidence}]")
            if source.check:
                print(f"    confirm : {source.check}")
            if source.url:
                print(f"    source  : {source.url}")
            if not source.url and not source.check:
                print("    (no source reference and nothing stated to confirm)")
        print("\nWhen a source is opened and the claim confirmed, set")
        print("verified: true and replace `note` with what was actually read.")
        return 0
    elif args.action == "validate":
        problems = kb.validate()
        if not problems:
            print(f"{len(kb.issues)} issues, all valid")
            return 0
        for issue_id, items in problems.items():
            print(f"{issue_id}:")
            for item in items:
                print(f"  - {item}")
        return 1
    return 0


def cmd_selftest(args) -> int:
    """Everything that can be checked without a vehicle attached."""
    failures = 0

    print("PID decoders")
    checks = [
        ("rpm", [0x1A, 0xF8], 1726.0),
        ("ect", [0x7B], 83.0),
        ("ltft_b1", [0x80], 0.0),
        ("ltft_b1", [0x90], 12.5),
        ("maf", [0x01, 0xF4], 5.0),
        ("timing_adv", [0x90], 8.0),
        ("map", [0x21], 33.0),
    ]
    for name, data, expected in checks:
        got = round(float(pidmod.BY_NAME[name].decode(data)), 3)
        ok = abs(got - expected) < 0.01
        failures += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {name:<12} {data} -> {got} (want {expected})")

    print("\nDTC decoding")
    for hi, lo, expected in ((0x01, 0x43, "P0143"), (0x41, 0x96, "C0196"),
                             (0xC1, 0x23, "U0123"), (0x00, 0x16, "P0016")):
        got = services.decode_dtc(hi, lo)
        ok = got == expected
        failures += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {hi:02X}{lo:02X} -> {got} (want {expected})")

    print("\nCondition evaluator")
    context = {"rpm_p2p": 120.0, "rpm_periodic": True, "ltft_mean": 3.0,
               "sweep.ltft_mean": 1.0}
    cases = [("rpm_p2p > 100", True), ("rpm_p2p > 100 and not rpm_periodic", False),
             ("ltft_mean < 10 or rpm_periodic", True),
             ("sweep.ltft_mean < ltft_mean", True)]
    for expr, expected in cases:
        got = runner.evaluate(expr, context)
        ok = got == expected
        failures += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {expr!r} -> {got}")

    print("  refusing unsafe expressions:")
    for bad in ("__import__('os').system('ls')", "open('/etc/passwd')"):
        try:
            runner.evaluate(bad, context)
            print(f"  FAIL {bad!r} was allowed")
            failures += 1
        except runner.ConditionError:
            print(f"  ok   {bad[:34]!r} rejected")

    print("\nPeriodicity detection")
    import math as _math
    import random as _random
    rng = _random.Random(20140901)
    gate = analysis.RPM_HUNT_MIN_P2P

    scatter = [700 + rng.gauss(0, 8) for _ in range(300)]
    hunting = [700 + 60 * _math.sin(i * 2 * _math.pi / 25) for i in range(300)]
    ripple = [700 + 3 * _math.sin(i * 2 * _math.pi / 8) for i in range(300)]

    cases = [
        ("random scatter", scatter, False),
        ("60 rpm hunt", hunting, True),
        ("3 rpm closed-loop ripple", ripple, False),
    ]
    for name, series, want in cases:
        got = analysis.find_periodicity(series, 0.1, min_p2p=gate)
        ok = got.periodic == want
        failures += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {name:<26} periodic={got.periodic} "
              f"(want {want}) {got.note}")

    print("\nIdle verdict thresholds")
    for p2p, periodic, want in ((30, False, "normal"), (150, False, "fault"),
                                (80, False, "borderline"), (30, True, "fault")):
        verdict, _ = analysis.idle_verdict(
            {"rpm_p2p": p2p, "rpm_periodic": periodic, "rpm_period_s": 2.5,
             "rpm_periodic_strength": 0.8})
        ok = verdict == want
        failures += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} p2p={p2p} periodic={periodic} -> {verdict}")

    print("\nFORScan import")
    import tempfile as _tempfile
    sample = (
        "Time (s),RPM (1/min),Long FT1 (%),VCT_INT_ACT1 (deg),Mystery (x)\n"
        "0.00,700,3.1,4.0,7\n"
        "0.20,705,3.1,4.2,7\n"
        "0.40,698,3.2,4.1,7\n"
    )
    with _tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
        fh.write(sample)
        sample_path = Path(fh.name)
    imported = forscan.load(sample_path)
    sample_path.unlink(missing_ok=True)

    fs_checks = [
        ("row count", len(imported.samples), 3),
        ("time column found", bool(imported.time_column), True),
        ("rpm mapped", imported.mapped.get("RPM (1/min)"), "rpm"),
        ("trim mapped", imported.mapped.get("Long FT1 (%)"), "ltft_b1"),
        ("cam mapped", imported.mapped.get("VCT_INT_ACT1 (deg)"), "vct_int_act_b1"),
        ("unknown column reported", "Mystery (x)" in imported.unmapped, True),
        ("elapsed normalised", imported.samples[1]["elapsed_s"], 0.2),
    ]
    for name, got, want in fs_checks:
        ok = got == want
        failures += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {name:<26} {got!r} (want {want!r})")

    for header, expected in (("Long FT1 (%)", "LONGFT1"), ("RPM(1/min)", "RPM"),
                             ("vct_int_act1", "VCTINTACT1")):
        got = forscan.normalise(header)
        ok = got == expected
        failures += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} normalise {header!r} -> {got!r}")

    print("\nFORScan orchestration")
    import math as _m2
    tracking_samples = []
    for i in range(200):
        tt = i * 0.1
        tracking_samples.append({
            "elapsed_s": round(tt, 3),
            "vct_int_des_b1": 4.0,
            "vct_int_act_b1": 4.0 + 9.0 * _m2.sin(2 * _m2.pi * tt / 2.5),
            "vct_int_des_b2": 4.0,
            "vct_int_act_b2": 4.1,
        })
    tm = forscan.tracking_metrics(tracking_samples)
    orch_checks = [
        ("pairs detected", tm.get("vct_pairs"), 2),
        ("worst error found", round(tm.get("vct_worst_error", 0)) >= 9, True),
        ("oscillation detected", tm.get("vct_actual_periodic"), True),
        ("tracks verdict false", tm.get("vct_tracks"), False),
        ("steady bank not periodic", tm.get("vct_int_act_b2_periodic"), False),
    ]
    for name, got, want in orch_checks:
        ok = got == want
        failures += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {name:<26} {got!r} (want {want!r})")

    try:
        forscan_control.instructions("vct", 90)
        forscan_control.instructions("misfire", 60)
        print("  ok   handoff instructions render for known requests")
    except Exception as exc:                                  # noqa: BLE001
        failures += 1
        print(f"  FAIL handoff instructions: {exc}")
    try:
        forscan_control.instructions("nonsense", 60)
        print("  FAIL unknown request was accepted")
        failures += 1
    except KeyError:
        print("  ok   unknown request rejected")

    newest = forscan_control.newest_export(since=0.0, roots=[])
    ok = newest is None
    failures += 0 if ok else 1
    print(f"  {'ok  ' if ok else 'FAIL'} empty search roots return nothing")

    # Asking whether FORScan is running puts "forscan" in our own command
    # line. A self-match here would refuse to start a session that could run.
    ok = forscan_control.is_running() is False
    failures += 0 if ok else 1
    print(f"  {'ok  ' if ok else 'FAIL'} process check does not match this process")

    print("\nProtocols")
    protos = runner.load_all(PROTOCOL_DIR)
    if not protos:
        print("  FAIL no protocols found")
        failures += 1
    for proto in protos.values():
        problems = proto.validate()
        failures += len(problems)
        print(f"  {'ok  ' if not problems else 'FAIL'} {proto.id}"
              + ("" if not problems else ": " + "; ".join(problems)))

    print("\nKnowledge base")
    kb = knowledge.KnowledgeBase.load(KNOWLEDGE_DIR)
    problems = kb.validate()
    for issue_id, items in problems.items():
        failures += len(items)
        print(f"  FAIL {issue_id}: {'; '.join(items)}")
    print(f"  {len(kb.issues)} issues loaded, {len(problems)} with problems")

    print("\n" + ("all checks passed" if failures == 0 else f"{failures} FAILURES"))
    return 0 if failures == 0 else 1


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _print_metrics(m: dict) -> None:
    verdict, why = analysis.idle_verdict(m)
    print(f"\nsamples {m.get('sample_count')} at {m.get('sample_dt')} s interval")
    if "rpm_mean" in m:
        print(f"rpm    mean {m['rpm_mean']}  sd {m['rpm_sd']}  p2p {m['rpm_p2p']}")
        print(f"       periodic={m.get('rpm_periodic')} "
              f"period={m.get('rpm_period_s')}s strength={m.get('rpm_periodic_strength')}")
        print(f"\nVERDICT: {verdict}\n  {why}")
    for key in sorted(k for k in m if k.endswith("_mean") and not k.startswith("rpm")):
        print(f"  {key:<22} {m[key]}")


def _read_samples(path: Path) -> list[dict]:
    if not path.exists():
        raise SystemExit(f"no such file: {path}")
    rows: list[dict] = []
    if path.suffix == ".jsonl":
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
    else:
        with path.open(encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                rows.append(row)
    out = []
    for row in rows:
        clean: dict = {}
        for k, v in row.items():
            if k in ("timestamp", "label"):
                continue
            try:
                clean[k] = float(v) if v not in ("", None) else None
            except (TypeError, ValueError):
                clean[k] = None
        out.append(clean)
    return out


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="f150diag",
        description="Adaptive OBD-II diagnostic tool for the 2014 F-150 3.7L.")
    p.add_argument("-v", "--verbose", action="store_true")
    p.add_argument("--port", help="serial port of the ELM327 adapter")
    p.add_argument("--baud", type=int, default=38400)
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("ports", help="list serial ports").set_defaults(fn=cmd_ports)
    sub.add_parser("survey", help="ask the vehicle what it supports").set_defaults(fn=cmd_survey)
    sub.add_parser("dtc", help="read stored, pending and permanent codes").set_defaults(fn=cmd_dtc)
    sub.add_parser("selftest", help="check everything that needs no vehicle").set_defaults(fn=cmd_selftest)
    sub.add_parser("protocols", help="list diagnostic protocols").set_defaults(fn=cmd_protocols)

    live = sub.add_parser("live", help="log parameters for a fixed window")
    live.add_argument("--pids", nargs="+", default=["idle"],
                      help="PID names or group names (idle, fuel, o2, evap, air, full)")
    live.add_argument("--seconds", type=float, default=60)
    live.add_argument("--label", default="live")
    live.set_defaults(fn=cmd_live)

    sub.add_parser("forscan-status",
                   help="where FORScan is installed and where its exports land"
                   ).set_defaults(fn=cmd_forscan_status)

    fs = sub.add_parser("forscan",
                        help="import and analyse a FORScan CSV export")
    fs.add_argument("file")
    fs.set_defaults(fn=cmd_forscan)

    ana = sub.add_parser("analyze", help="analyse a recorded log")
    ana.add_argument("file")
    ana.set_defaults(fn=cmd_analyze)

    run = sub.add_parser("run", help="run a diagnostic protocol")
    run.add_argument("protocol")
    run.add_argument("--dry-run", action="store_true",
                     help="walk the protocol without an adapter (prompts only)")
    run.set_defaults(fn=cmd_run)

    kb = sub.add_parser("kb", help="query the issue knowledge base")
    kb.add_argument("action",
                    choices=["list", "show", "search", "validate", "verify"])
    kb.add_argument("term", nargs="?")
    kb.set_defaults(fn=cmd_kb)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    configure_logging(args.verbose)
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
