"""Enumerations and band helpers. Everything validates against profiles/vocab.yaml."""
from __future__ import annotations

import functools
import os

from . import skill_path

try:
    import yaml
except ImportError as e:  # pragma: no cover
    raise SystemExit("vis-design needs PyYAML: pip install pyyaml") from e


@functools.lru_cache(maxsize=1)
def load() -> dict:
    with open(skill_path("profiles", "vocab.yaml"), encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def values(name: str) -> list:
    v = load()[name]
    return list(v.keys()) if isinstance(v, dict) else list(v)


def check(name: str, value, errors: list, where: str):
    """Append an error if value is not in enumeration `name`."""
    if value is None:
        return
    allowed = values(name)
    if isinstance(value, list):
        for x in value:
            if x not in allowed:
                errors.append(f"{where}: '{x}' not in {name}")
    elif value not in allowed:
        errors.append(f"{where}: '{value}' not in {name}")


def band_for(n: int | None) -> str | None:
    """Cardinality band for n distinct levels."""
    if n is None:
        return None
    for name, lim in load()["cardinality_bands"].items():
        lo, hi = lim["min"], lim["max"]
        if n >= lo and (hi is None or n <= hi):
            return name
    return "huge"


def items_band(n: int | None) -> str | None:
    if n is None:
        return None
    for name, lim in load()["items_bands"].items():
        if lim["max"] is None or n <= lim["max"]:
            return name
    return "large"


BAND_ORDER = ["one", "few", "some", "many", "huge"]


def band_distance(a: str, b: str) -> int:
    try:
        return abs(BAND_ORDER.index(a) - BAND_ORDER.index(b))
    except ValueError:
        return 9
