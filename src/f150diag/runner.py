"""
The adaptive part.

A protocol is a small graph of steps written in YAML. The runner walks it,
and every branch is decided by measurements taken seconds earlier — so the
path through the graph depends on the vehicle, not on a script author's
guess about what the vehicle will do.

Step types
----------
prompt   ask the operator to do something physical, wait, optionally capture
         an answer as a variable
measure  poll PIDs for N seconds; the resulting metrics enter the context
service  run a read-only diagnostic service (dtcs, survey, mode06, vin)
branch   evaluate conditions in order, take the first that matches
finding   record a conclusion and continue
end      stop

Conditions are ordinary expressions over measured metrics, e.g.

    rpm_p2p > 100 or rpm_periodic
    ltft_mean > 10 and idle2500.ltft_mean < 5

Metrics from an earlier `measure` stay reachable as `<label>.<metric>`, which
is what lets a protocol compare idle against 2500 rpm — the comparison that
separates an air leak from everything else.
"""

from __future__ import annotations

import ast
import logging
import operator
from dataclasses import dataclass, field
import time
from pathlib import Path
from typing import Any, Callable

import yaml

from . import analysis, forscan, forscan_control, pids as pidmod, services
from .recorder import measure
from .transport import Elm327

log = logging.getLogger("f150diag.runner")


# ---------------------------------------------------------------------------
# Safe expression evaluation
# ---------------------------------------------------------------------------

_BINOPS = {
    ast.Add: operator.add, ast.Sub: operator.sub,
    ast.Mult: operator.mul, ast.Div: operator.truediv,
    ast.Mod: operator.mod, ast.Pow: operator.pow,
}
_CMPOPS = {
    ast.Eq: operator.eq, ast.NotEq: operator.ne,
    ast.Lt: operator.lt, ast.LtE: operator.le,
    ast.Gt: operator.gt, ast.GtE: operator.ge,
}


class ConditionError(ValueError):
    """A protocol condition is malformed or references something unmeasured."""


def evaluate(expression: str, context: dict[str, Any]) -> bool:
    """
    Evaluate a protocol condition.

    Deliberately not `eval`. Protocols are data files that get edited during a
    diagnostic session, and a data file should never be able to execute code.
    Only arithmetic, comparison and boolean logic over known names.
    """
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise ConditionError(f"cannot parse {expression!r}: {exc}") from exc

    def walk(node: ast.AST) -> Any:
        if isinstance(node, ast.Expression):
            return walk(node.body)
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Name):
            if node.id not in context:
                raise ConditionError(f"{node.id!r} was never measured")
            return context[node.id]
        if isinstance(node, ast.Attribute):
            # "label.metric" arrives as Attribute(Name(label), metric)
            base = node.value
            if isinstance(base, ast.Name):
                key = f"{base.id}.{node.attr}"
                if key not in context:
                    raise ConditionError(f"{key!r} was never measured")
                return context[key]
            raise ConditionError("only one level of attribute access is allowed")
        if isinstance(node, ast.UnaryOp):
            if isinstance(node.op, ast.Not):
                return not walk(node.operand)
            if isinstance(node.op, ast.USub):
                return -walk(node.operand)
            raise ConditionError(f"unsupported unary operator {type(node.op).__name__}")
        if isinstance(node, ast.BinOp):
            fn = _BINOPS.get(type(node.op))
            if fn is None:
                raise ConditionError(f"unsupported operator {type(node.op).__name__}")
            return fn(walk(node.left), walk(node.right))
        if isinstance(node, ast.BoolOp):
            values = [walk(v) for v in node.values]
            return all(values) if isinstance(node.op, ast.And) else any(values)
        if isinstance(node, ast.Compare):
            left = walk(node.left)
            for op, comparator in zip(node.ops, node.comparators):
                fn = _CMPOPS.get(type(op))
                if fn is None:
                    raise ConditionError(f"unsupported comparison {type(op).__name__}")
                right = walk(comparator)
                if not fn(left, right):
                    return False
                left = right
            return True
        raise ConditionError(f"disallowed expression element {type(node).__name__}")

    return bool(walk(tree))


# ---------------------------------------------------------------------------
# Protocols
# ---------------------------------------------------------------------------

@dataclass
class Finding:
    id: str
    summary: str
    detail: str = ""
    step: str = ""


@dataclass
class Protocol:
    id: str
    title: str
    entry: str
    steps: dict[str, dict]
    description: str = ""
    path: Path | None = None

    @classmethod
    def load(cls, path: Path) -> "Protocol":
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        steps = {s["id"]: s for s in data.get("steps", [])}
        if not steps:
            raise ValueError(f"{path}: protocol has no steps")
        entry = data.get("entry") or data["steps"][0]["id"]
        return cls(id=data["id"], title=data.get("title", data["id"]),
                   description=data.get("description", ""),
                   entry=entry, steps=steps, path=path)

    def validate(self) -> list[str]:
        """Every `next` must exist. Catches typos before you are at the truck."""
        problems: list[str] = []
        valid = set(self.steps) | {"END", "end", None}
        if self.entry not in self.steps:
            problems.append(f"entry step {self.entry!r} does not exist")
        for sid, step in self.steps.items():
            targets = [step.get("next")]
            for branch in step.get("checks", []):
                targets.append(branch.get("next"))
            for t in targets:
                if t is not None and t not in valid:
                    problems.append(f"step {sid!r} points at unknown step {t!r}")
            if step.get("type") not in {"prompt", "measure", "service", "branch",
                                        "finding", "end", "handoff"}:
                problems.append(f"step {sid!r} has unknown type {step.get('type')!r}")
        return problems


def load_all(directory: Path) -> dict[str, Protocol]:
    out: dict[str, Protocol] = {}
    for path in sorted(directory.glob("*.yaml")):
        try:
            proto = Protocol.load(path)
        except Exception as exc:                       # noqa: BLE001
            log.error("%s: %s", path.name, exc)
            continue
        out[proto.id] = proto
    return out


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------

Asker = Callable[[str, list[str] | None], str]


def default_asker(question: str, options: list[str] | None) -> str:
    if options:
        print(f"\n{question}")
        for i, opt in enumerate(options, 1):
            print(f"  {i}. {opt}")
        raw = input("choice> ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1]
        return raw
    return input(f"\n{question}\n> ").strip()


@dataclass
class Session:
    """One run of one protocol against one vehicle."""
    elm: Elm327 | None
    out_dir: Path
    context: dict[str, Any] = field(default_factory=dict)
    findings: list[Finding] = field(default_factory=list)
    transcript: list[str] = field(default_factory=list)
    asker: Asker = default_asker
    dry_run: bool = False
    #: Called to re-open the adapter after it has been handed to FORScan.
    reconnect: Callable[[], Elm327] | None = None

    @property
    def live(self) -> bool:
        """
        True when this session is really measuring.

        Not simply "is the adapter open" — during a FORScan handoff the port
        is deliberately released while the session is still very much live.
        """
        return not self.dry_run

    def record(self, finding: Finding) -> None:
        """
        Record a conclusion — but only one the vehicle actually supported.

        Without an adapter every condition falls through for want of data, so
        a protocol's default branch would otherwise assert a clean bill of
        health it never measured. A dry run rehearses the questions; it does
        not get to answer them.
        """
        if not self.live:
            self.say(f"\n  [dry run] would record: {finding.summary}")
            return
        self.findings.append(finding)
        self.say(f"\n→ {finding.summary}")

    def say(self, text: str) -> None:
        print(text)
        self.transcript.append(text)

    # -- individual step types --------------------------------------------

    def do_prompt(self, step: dict) -> None:
        text = step["text"].strip()
        self.say("\n" + "─" * 70)
        self.say(text)
        self.say("─" * 70)
        if "ask" in step:
            answer = self.asker(step.get("question", "Result?"), step.get("options"))
            self.context[step["ask"]] = answer
            self.transcript.append(f"[{step['ask']}] {answer}")
        else:
            self.asker(step.get("confirm", "Press Enter when done"), None)

    def do_measure(self, step: dict) -> None:
        if self.dry_run:
            self.say(f"  [dry run] would measure {step.get('label', step['id'])} "
                     f"for {step.get('seconds', 60)} s")
            return
        if self.elm is None:
            raise RuntimeError("the adapter is not connected — a handoff may "
                               "have failed to hand it back")
        selected = pidmod.resolve(step.get("pids", ["idle"]))
        seconds = float(step.get("seconds", 60))
        label = step.get("label", step["id"])
        self.say(f"\nMeasuring {label} for {seconds:.0f} s "
                 f"({len(selected)} parameters)…")

        rec = measure(self.elm, selected, seconds, self.out_dir, label)
        m = analysis.metrics(rec.samples)
        self.context.update(m)
        for key, value in m.items():
            self.context[f"{label}.{key}"] = value

        verdict, why = analysis.idle_verdict(m)
        self.context["idle_verdict"] = verdict
        self.say(f"  samples {m.get('sample_count')} at {m.get('sample_dt')} s")
        if "rpm_mean" in m:
            self.say(f"  rpm  mean {m['rpm_mean']}  sd {m['rpm_sd']}  "
                     f"peak-to-peak {m['rpm_p2p']}")
            self.say(f"  verdict: {verdict} — {why}")
        for key in ("ltft_mean", "ltft_split", "stft_mean"):
            if key in m:
                self.say(f"  {key}: {m[key]}")

    def do_service(self, step: dict) -> None:
        if self.dry_run:
            self.say(f"  [dry run] would run service {step['service']}")
            return
        if self.elm is None:
            raise RuntimeError("the adapter is not connected — a handoff may "
                               "have failed to hand it back")
        what = step["service"]

        if what == "survey":
            cap = services.survey(self.elm)
            self.context["vin_reported"] = cap.vin or ""
            self.context["egr_supported"] = "egr_cmd" in cap.supported
            self.context["supported_count"] = len(cap.supported)
            self.say(f"  VIN reported by vehicle: {cap.vin}")
            self.say(f"  calibration IDs: {', '.join(cap.calibrations) or 'none'}")
            self.say(f"  supported parameters: {len(cap.supported)}")
            self.say(f"  EGR PIDs supported: {self.context['egr_supported']}")

        elif what == "dtcs":
            stored = services.stored_dtcs(self.elm)
            pending = services.pending_dtcs(self.elm)
            permanent = services.permanent_dtcs(self.elm)
            self.context["dtc_stored_count"] = len(stored)
            self.context["dtc_pending_count"] = len(pending)
            self.context["dtc_permanent_count"] = len(permanent)
            self.context["dtc_total"] = len(stored) + len(pending) + len(permanent)
            self.say(f"  stored:    {', '.join(stored) or 'none'}")
            self.say(f"  pending:   {', '.join(pending) or 'none'}")
            self.say(f"  permanent: {', '.join(permanent) or 'none'}")
            for code in stored + pending + permanent:
                self.findings.append(Finding(id=f"dtc:{code}",
                                             summary=f"trouble code {code}",
                                             step=step["id"]))


        elif what == "mode06":
            results = services.misfire_monitors(self.elm)
            reported = {mid: tests for mid, tests in results.items() if tests}
            self.context["mode06_monitors"] = len(reported)
            failing = 0
            for mid, tests in reported.items():
                for t in tests:
                    flag = "" if t.passed else "  ← OUT OF LIMITS"
                    if not t.passed:
                        failing += 1
                    self.say(f"  MID {mid:02X} TID {t.tid:02X}: value {t.value} "
                             f"limits {t.min_limit}..{t.max_limit} "
                             f"margin {t.margin}{flag}")
            self.context["mode06_failing"] = failing
            if not reported:
                self.say("  no monitor results reported "
                         "(common on a generic tool — needs Ford enhanced access)")
        else:
            raise ValueError(f"unknown service {what!r}")

    def do_handoff(self, step: dict) -> None:
        """
        Hand the adapter to FORScan, then take back what it measured.

        The port is released, never shared. FORScan reads what this tool
        cannot — cam position above all — and its export is collected
        automatically, so the operator never has to relay a filename.
        """
        request = step.get("request", "vct")
        label = step.get("label", f"forscan_{request}")
        seconds = int(step.get("seconds", 90))
        timeout = float(step.get("timeout_s", 900))

        self.say("\n" + "═" * 70)
        self.say(forscan_control.instructions(request, seconds))
        self.say("═" * 70)

        if self.dry_run:
            self.say("  [dry run] would release the port, launch FORScan and "
                     "wait for an export")
            return

        if self.elm is not None:
            self.elm.close()
            self.elm = None
            self.say("\n  adapter released — FORScan may connect now")

        started = time.time()
        if step.get("launch", True):
            forscan_control.launch()

        self.say(f"  watching for a new export (up to {timeout / 60:.0f} min)…")
        export = forscan_control.wait_for_export(
            since=started, timeout_s=timeout,
            on_wait=lambda: self.say("  nothing yet — recording, then save as CSV"))

        if export is None:
            self.say("  no export appeared within the timeout.")
            self.context[f"{label}.imported"] = False
        elif not export.is_csv:
            self.say(f"  found {export.path.name}, which is FORScan's own "
                     f"format and cannot be read here.")
            self.asker("Re-save it as CSV in FORScan (it converts offline, no "
                       "adapter needed), then press Enter", None)
            export = forscan_control.wait_for_export(since=started, timeout_s=300)
            self.context[f"{label}.imported"] = export is not None and export.is_csv

        if export is not None and export.is_csv:
            imported = forscan.load(export.path)
            self.say("\n" + imported.report())
            metrics = analysis.metrics(imported.samples)
            metrics.update(forscan.tracking_metrics(imported.samples))
            self.context[f"{label}.imported"] = True
            for key, value in metrics.items():
                self.context[key] = value
                self.context[f"{label}.{key}"] = value
            if metrics.get("vct_pairs"):
                self.say(f"  cam pairs found: {metrics['vct_pairs']}")
                self.say(f"  worst tracking error: {metrics.get('vct_worst_error')} deg")
                self.say(f"  actual position oscillating: "
                         f"{metrics.get('vct_actual_periodic')}")
            else:
                self.say("  no cam channels in this export — check the PID "
                         "names against the mapping report above")

        if self.reconnect is not None:
            self.asker("Close FORScan so the adapter is free, then press Enter",
                       None)
            try:
                self.elm = self.reconnect()
                self.say("  adapter reconnected")
            except Exception as exc:                       # noqa: BLE001
                self.say(f"  could not reconnect the adapter: {exc}")

    def do_branch(self, step: dict) -> str | None:
        for check in step.get("checks", []):
            condition = check.get("when")
            if condition is None:
                matched = True
            else:
                try:
                    matched = evaluate(condition, self.context)
                except ConditionError as exc:
                    log.warning("step %s: %s — treating as not matched",
                                step["id"], exc)
                    matched = False
            if matched:
                if "finding" in check:
                    self.record(Finding(
                        id=check["finding"],
                        summary=check.get("summary", check["finding"]),
                        detail=check.get("detail", ""),
                        step=step["id"]))
                return check.get("next")
        return step.get("next")

    # -- the walk ----------------------------------------------------------

    def run(self, protocol: Protocol, max_steps: int = 200) -> list[Finding]:
        problems = protocol.validate()
        if problems:
            raise ValueError("protocol is malformed:\n  " + "\n  ".join(problems))

        self.say(f"\n╔{'═' * 68}╗")
        self.say(f"║ {protocol.title[:66]:<66} ║")
        self.say(f"╚{'═' * 68}╝")
        if protocol.description:
            self.say(protocol.description.strip())

        current: str | None = protocol.entry
        for _ in range(max_steps):
            if current is None or current.upper() == "END":
                break
            step = protocol.steps.get(current)
            if step is None:
                raise ValueError(f"protocol jumped to unknown step {current!r}")

            kind = step["type"]
            log.debug("step %s (%s)", current, kind)

            if kind == "prompt":
                self.do_prompt(step)
                current = step.get("next")
            elif kind == "measure":
                self.do_measure(step)
                current = step.get("next")
            elif kind == "service":
                self.say(f"\n{step.get('text', step['service'])}")
                self.do_service(step)
                current = step.get("next")
            elif kind == "handoff":
                self.do_handoff(step)
                current = step.get("next")
            elif kind == "branch":
                current = self.do_branch(step)
            elif kind == "finding":
                self.record(Finding(id=step["finding"],
                                    summary=step.get("summary", step["finding"]),
                                    detail=step.get("detail", ""),
                                    step=current))
                current = step.get("next")
            elif kind == "end":
                break
            else:
                raise ValueError(f"unknown step type {kind!r}")
        else:
            log.warning("step limit reached — protocol may contain a loop")

        return self.findings
