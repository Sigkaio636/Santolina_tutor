"""Chart catalog loading and candidate ranking."""
from __future__ import annotations

import functools
import glob
import json
import os

import yaml

from . import skill_path
from .shape import shape_compatible, canonicalize


@functools.lru_cache(maxsize=1)
def load() -> dict[str, dict]:
    with open(skill_path("data", "chart-catalog.json"), encoding="utf-8") as fh:
        d = json.load(fh)
    return {e["id"]: e for e in d["charts"]}


@functools.lru_cache(maxsize=1)
def functions() -> dict:
    with open(skill_path("data", "catalog-functions.json"), encoding="utf-8") as fh:
        return json.load(fh)["functions"]


@functools.lru_cache(maxsize=1)
def archetypes() -> dict[str, dict]:
    out = {}
    for f in glob.glob(skill_path("profiles", "problems", "*.yaml")):
        with open(f, encoding="utf-8") as fh:
            a = yaml.safe_load(fh)
        out[a["id"]] = a
    return out


@functools.lru_cache(maxsize=1)
def profiles() -> dict[str, dict]:
    out = {}
    for f in glob.glob(skill_path("profiles", "users", "*.yaml")):
        with open(f, encoding="utf-8") as fh:
            p = yaml.safe_load(fh)
        out[p["id"]] = p
    return out


def rank_candidates(q: dict, limit: int = 5) -> list[dict]:
    """Catalog entries that fit the query's archetype, data shape, profile, mode, constraints."""
    cat = load()
    arch = archetypes().get((q.get("problem") or {}).get("archetype"))
    if not arch:
        return []
    funcs = set(arch.get("catalog_functions", []))
    preferred = arch.get("preferred_idioms", [])
    disc = {d["idiom"]: d for d in arch.get("discouraged_idioms", [])}
    profile = (q.get("user") or {}).get("profile")
    mode = (q.get("problem") or {}).get("mode")
    constraints = set(q.get("constraints") or [])
    qdata = canonicalize(q.get("data") or {})
    out = []
    for cid, e in cat.items():
        o = e["ours"]
        in_pool = bool(funcs & set(e.get("functions", []))) or cid in preferred or \
            arch["id"] in o.get("archetypes", [])
        if not in_pool:
            continue
        compatible = shape_compatible(qdata, o["data_shape"]) if qdata.get("keys") or qdata.get("values") else True
        s = 0.0
        notes = []
        if cid in preferred:
            s += 1.0 - preferred.index(cid) * 0.15
        if profile in o.get("profile_fit", []):
            s += 0.2
        if mode in o.get("mode_fit", []):
            s += 0.1
        if arch["id"] in o.get("archetypes", []):
            s += 0.2
        if not compatible:
            s -= 0.3
            notes.append("data shape does not match the idiom's expected keys/values")
        if o.get("discouraged"):
            s -= 0.5
            notes.append(f"discouraged ({o['discouraged']['rule']}): {o['discouraged']['reason']}")
        if cid in disc:
            notes.append(f"archetype discourages it when {disc[cid]['when']} ({disc[cid]['rule']})")
            s -= 0.2
        if "static-only" in constraints and o.get("family") in ("network", "parallel") and profile in ("general-public", "executive"):
            s -= 0.2
        if "no-geometry-file" in constraints and o.get("family", "").startswith("map-"):
            s -= 1.0
            notes.append("needs a geometry file")
        if "exact-values" in constraints and o.get("family") in ("pie", "treemap", "proportional-area", "radial"):
            s -= 0.5
        lib = (q.get("library") or "").lower()
        if lib and o.get("library_support", {}).get(lib) == "none":
            s -= 0.4
            notes.append(f"no native support in {lib}")
        out.append({"idiom": cid, "name": e["name"], "family": o["family"], "score": round(s, 3),
                    "mark": o["munzner"]["mark"], "channels": o["munzner"]["channels"],
                    "tasks": o["tasks"], "scalability": o["scalability"], "rules": o["rules"],
                    "limits": e.get("limits", [])[:3], "library_support": o.get("library_support"),
                    "notes": notes})
    out.sort(key=lambda c: -c["score"])
    return out[:limit]
