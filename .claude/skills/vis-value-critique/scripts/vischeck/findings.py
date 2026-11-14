"""Finding records and report envelope shared by all inspectors."""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field, asdict
from typing import Any

SEVERITIES = ("crit", "major", "minor", "info")


@dataclass
class Finding:
    rule: str            # catalog ID, e.g. "EXP-08" or "TRUNC-1"
    severity: str        # crit | major | minor | info
    message: str         # one sentence, what is wrong
    evidence: str = ""   # the concrete fact observed (numbers, names)
    kind: str = "DET"    # DET (fact) | SEMI (trigger, judgment needed)
    where: str = ""      # unit / axes / trace identifier
    exception: str = ""  # when this does not apply; the critic must check it

    def __post_init__(self):
        if self.severity not in SEVERITIES:
            raise ValueError(f"bad severity {self.severity}")


class Report:
    """Collects findings, warnings, summary facts and artifact paths."""

    def __init__(self, input_path: str, input_type: str):
        self.input = input_path
        self.type = input_type
        self.findings: list[Finding] = []
        self.warnings: list[str] = []
        self.summary: dict[str, Any] = {}
        self.artifacts: list[str] = []

    def add(self, rule, severity, message, evidence="", kind="DET", where="",
            exception=""):
        f = Finding(rule, severity, message, evidence, kind, where, exception)
        # de-duplicate identical findings (same rule + where + message)
        for g in self.findings:
            if (g.rule, g.where, g.message) == (f.rule, f.where, f.message):
                return f
        self.findings.append(f)
        return f

    def warn(self, msg: str):
        self.warnings.append(msg)

    def to_dict(self) -> dict:
        order = {s: i for i, s in enumerate(SEVERITIES)}
        fs = sorted(self.findings, key=lambda f: (order[f.severity], f.rule))
        counts = {s: sum(1 for f in fs if f.severity == s) for s in SEVERITIES}
        return {
            "input": self.input,
            "type": self.type,
            "summary": self.summary,
            "counts": counts,
            "findings": [asdict(f) for f in fs],
            "warnings": self.warnings,
            "artifacts": self.artifacts,
            "note": ("Deterministic findings are evidence, not verdicts: check the "
                     "exception of each rule in references/rules-catalog.md. "
                     "Absence of findings says nothing about value."),
        }

    def dump(self, stream=None):
        json.dump(self.to_dict(), stream or sys.stdout, indent=2, ensure_ascii=False)
        (stream or sys.stdout).write("\n")


def looks_like_raw_name(title: str | None) -> bool:
    """True when an axis/legend title is a bare variable name rather than prose."""
    if not title:
        return True
    t = str(title).strip()
    if not t:
        return True
    if "(" in t and ")" in t:   # likely has units
        return False
    if "_" in t and " " not in t:
        return True
    if any(t.startswith(p) for p in ("count(", "sum(", "mean(", "average(", "median(",
                                      "min(", "max(")):
        return True
    if t.islower() and " " not in t and len(t) <= 14:
        return True
    return False


UNIT_HINT = ("(", "%", "€", "$", "km", " m", "kg", "°", "per ", "/", "mm", "h", "s")


def has_units(title: str | None) -> bool:
    if not title:
        return False
    t = str(title)
    return any(h in t for h in UNIT_HINT)


NON_ADDITIVE_HINTS = ("temp", "rate", "pct", "percent", "ratio", "avg", "mean",
                      "median", "price", "index", "share", "density", "per_",
                      "per ", "speed", "velocity", "score", "level")


def looks_non_additive(name: str | None) -> bool:
    if not name:
        return False
    n = str(name).lower()
    return any(h in n for h in NON_ADDITIVE_HINTS)


RAW_COUNT_HINTS = ("total", "count", "population", "number", "num_", "n_", "sum")
RATE_HINTS = ("per", "rate", "density", "pct", "percent", "share", "ratio", "capita")


def looks_like_raw_count(name: str | None) -> bool:
    if not name:
        return False
    n = str(name).lower()
    return any(h in n for h in RAW_COUNT_HINTS) and not any(h in n for h in RATE_HINTS)


TIME_HINTS = ("year", "date", "month", "day", "time", "week", "hour", "quarter",
              "any", "mes", "fecha", "dia", "semana", "periodo", "period", "yr")


def looks_temporal(name: str | None) -> bool:
    if not name:
        return False
    n = str(name).lower()
    return any(n == h or n.startswith(h) or n.endswith(h) for h in TIME_HINTS)
