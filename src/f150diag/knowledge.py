"""
The issue knowledge base.

Two kinds of knowledge matter here and they are not equal:

  * What Ford published — service manual, TSBs, customer satisfaction
    programmes.
  * What owners and independent technicians worked out and published —
    which is often the only account of a failure Ford never documented,
    and sometimes the only account of one Ford documented quietly.

Both belong in the base. Neither may be silently promoted to the other.
Every entry therefore carries `provenance` with an explicit confidence and a
`verified` flag meaning "somebody actually opened the source", not "it was in
a search result summary".

An entry is a hypothesis with an address, not a conclusion.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

import yaml

log = logging.getLogger("f150diag.knowledge")

CONFIDENCE_ORDER = {"high": 3, "medium": 2, "low": 1, "unknown": 0}
VALID_SOURCES = {"ford-official", "ford-tsb", "community", "measured",
                 "inferred", "unverified"}


@dataclass
class Source:
    source: str = "unverified"
    confidence: str = "unknown"
    note: str = ""
    url: str = ""
    verified: bool = False           # did somebody actually READ the source?
    check: str = ""                  # what to confirm when someone can reach it

    @property
    def weight(self) -> int:
        base = CONFIDENCE_ORDER.get(self.confidence, 0)
        return base + (1 if self.verified else 0)

    @property
    def needs_verification(self) -> bool:
        return not self.verified and bool(self.url or self.check)


@dataclass
class Issue:
    id: str
    title: str
    summary: str = ""
    systems: list[str] = field(default_factory=list)
    symptoms: list[str] = field(default_factory=list)
    codes: list[str] = field(default_factory=list)
    load_signature: str = ""          # worst-at-idle | worse-under-load | rpm-linked | none
    temperature: str = ""             # cold-only | hot-only | independent | unknown
    sets_code: str = "unknown"        # always | sometimes | rarely | never
    tests: list[str] = field(default_factory=list)
    fix: str = ""
    cost: str = ""
    applies_to: dict[str, Any] = field(default_factory=dict)
    provenance: list[Source] = field(default_factory=list)
    notes: str = ""

    @property
    def confidence(self) -> int:
        return max((s.weight for s in self.provenance), default=0)

    @property
    def is_verified(self) -> bool:
        return any(s.verified for s in self.provenance)

    @classmethod
    def from_dict(cls, data: dict) -> "Issue":
        prov = [Source(**s) for s in data.pop("provenance", [])]
        known = {f for f in cls.__dataclass_fields__ if f != "provenance"}
        unknown = set(data) - known
        if unknown:
            log.warning("%s: ignoring unknown fields %s", data.get("id"), sorted(unknown))
        return cls(provenance=prov, **{k: v for k, v in data.items() if k in known})

    def problems(self) -> list[str]:
        """Schema complaints. A base nobody validates rots quietly."""
        out = []
        if not self.provenance:
            out.append("no provenance — every entry must say where it came from")
        for s in self.provenance:
            if s.source not in VALID_SOURCES:
                out.append(f"unknown source {s.source!r}")
            if s.verified and not s.url:
                out.append("marked verified but carries no source reference")
        if not self.tests:
            out.append("no test — an issue with no way to check it is folklore")
        return out


class KnowledgeBase:
    def __init__(self, issues: dict[str, Issue]):
        self.issues = issues

    @classmethod
    def load(cls, directory: Path) -> "KnowledgeBase":
        issues: dict[str, Issue] = {}
        for path in sorted(directory.rglob("*.yaml")):
            try:
                payload = yaml.safe_load(path.read_text(encoding="utf-8"))
            except yaml.YAMLError as exc:
                log.error("%s: %s", path.name, exc)
                continue
            entries = payload if isinstance(payload, list) else [payload]
            for entry in entries:
                if not entry:
                    continue
                issue = Issue.from_dict(dict(entry))
                if issue.id in issues:
                    log.warning("duplicate issue id %r in %s", issue.id, path.name)
                issues[issue.id] = issue
        log.info("knowledge base: %d issues", len(issues))
        return cls(issues)

    # -- queries -----------------------------------------------------------

    def by_code(self, code: str) -> list[Issue]:
        code = code.upper()
        return [i for i in self.issues.values() if code in {c.upper() for c in i.codes}]

    def by_signature(self, load_signature: str = "", temperature: str = "",
                     sets_code: str = "") -> list[Issue]:
        """
        Match on behaviour rather than on a code.

        This is the query that matters for a fault with no code: it selects
        candidates whose *mechanism* fits the observed load and temperature
        dependence, which is the only evidence such a fault leaves.
        """
        out = []
        for issue in self.issues.values():
            if load_signature and issue.load_signature and issue.load_signature != load_signature:
                continue
            if temperature and issue.temperature and issue.temperature not in (temperature, "unknown"):
                continue
            if sets_code and issue.sets_code and sets_code == "never" and issue.sets_code == "always":
                continue
            out.append(issue)
        return sorted(out, key=lambda i: -i.confidence)

    def search(self, term: str) -> list[Issue]:
        t = term.lower()
        hits = []
        for issue in self.issues.values():
            haystack = " ".join([issue.id, issue.title, issue.summary,
                                 " ".join(issue.symptoms), " ".join(issue.systems),
                                 " ".join(issue.codes)]).lower()
            if t in haystack:
                hits.append(issue)
        return sorted(hits, key=lambda i: -i.confidence)

    def validate(self) -> dict[str, list[str]]:
        return {i.id: p for i, p in ((i, i.problems()) for i in self.issues.values()) if p}

    def verification_queue(self) -> list[tuple[Issue, Source]]:
        """
        Every claim still resting on something nobody opened.

        This is the base's honest debt. Work it where the network allows it:
        open the source, confirm the specific claim in `check`, then set
        verified and record what was confirmed.
        """
        out = []
        for issue in sorted(self.issues.values(), key=lambda i: i.id):
            for source in issue.provenance:
                if source.needs_verification:
                    out.append((issue, source))
        return out


def render(issue: Issue) -> str:
    """One issue as readable text, provenance included — never stripped."""
    lines = [f"{issue.id}  —  {issue.title}"]
    if issue.summary:
        lines.append(f"  {issue.summary}")
    if issue.load_signature:
        lines.append(f"  load signature : {issue.load_signature}")
    if issue.temperature:
        lines.append(f"  temperature    : {issue.temperature}")
    if issue.sets_code:
        lines.append(f"  sets a code    : {issue.sets_code}")
    if issue.codes:
        lines.append(f"  codes          : {', '.join(issue.codes)}")
    if issue.tests:
        lines.append("  tests:")
        lines.extend(f"    - {t}" for t in issue.tests)
    if issue.fix:
        lines.append(f"  fix            : {issue.fix}")
    if issue.cost:
        lines.append(f"  cost           : {issue.cost}")
    lines.append("  provenance:")
    for s in issue.provenance:
        mark = "read" if s.verified else "NOT READ"
        lines.append(f"    - {s.source} / {s.confidence} / {mark}")
        if s.note:
            lines.append(f"      {s.note}")
        if s.url:
            lines.append(f"      {s.url}")
        if s.check and not s.verified:
            lines.append(f"      TO CONFIRM: {s.check}")
    if issue.notes:
        lines.append(f"  notes: {issue.notes}")
    return "\n".join(lines)


def summarise(issues: Iterable[Issue]) -> str:
    rows = []
    for i in issues:
        flag = "✓" if i.is_verified else "?"
        rows.append(f"  {flag} {i.id:<34} {i.title}")
    return "\n".join(rows) or "  (nothing matched)"
