"""Decision records: schema validation, key, ids, YAML I/O."""
from __future__ import annotations

import datetime as dt
import os
import re

import yaml

from . import vocab
from .shape import canonicalize, signature

SCHEMA_VERSION = 1
REQUIRED_TOP = ["schema_version", "id", "status", "title", "problem", "user", "tasks", "data",
                "constraints", "solution", "rationale", "confidence", "provenance"]
REQUIRED_SOLUTION = ["idiom", "family", "mark", "encodings", "color", "text", "interaction",
                     "rejected_alternatives", "validation"]


def load_yaml(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def dump_yaml(obj: dict, path: str, header: str | None = None):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        if header:
            fh.write(f"# {header}\n")
        yaml.safe_dump(obj, fh, sort_keys=False, allow_unicode=True, width=100)


def key(rec: dict) -> tuple:
    p, u, d = rec.get("problem", {}), rec.get("user", {}), rec.get("data", {})
    return (p.get("archetype"), p.get("mode"), u.get("profile"),
            d.get("signature") or signature(d))


def slug(text: str, maxlen: int = 40) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")
    if len(s) > maxlen:
        s = s[:maxlen].rsplit("-", 1)[0] if "-" in s[:maxlen] else s[:maxlen]
    return s.rstrip("-") or "decision"


def new_project_id(rec: dict, existing: set[str]) -> str:
    base = f"p-{rec['problem']['archetype']}--{slug(rec.get('title', 'decision'), 30)}-{dt.date.today():%Y%m%d}"
    cand, n = base, 2
    while cand in existing:
        cand = f"{base}-{n}"
        n += 1
    return cand


def validate(rec: dict, catalog_ids: set[str] | None = None, archetype_ids: set[str] | None = None,
             profile_ids: set[str] | None = None, rule_ids: set[str] | None = None) -> list[str]:
    """Return a list of problems (empty = valid)."""
    e: list[str] = []
    for f in REQUIRED_TOP:
        if f not in rec:
            e.append(f"missing top-level field '{f}'")
    if e:
        return e
    if rec["schema_version"] != SCHEMA_VERSION:
        e.append(f"schema_version {rec['schema_version']} != {SCHEMA_VERSION}")
    vocab.check("record_status", rec["status"], e, "status")
    vocab.check("confidence", rec["confidence"], e, "confidence")
    p = rec["problem"]
    for f in ("archetype", "mode", "statement"):
        if f not in p:
            e.append(f"problem.{f} missing")
    vocab.check("modes", p.get("mode"), e, "problem.mode")
    vocab.check("catalog_functions", p.get("catalog_functions", []), e, "problem.catalog_functions")
    if archetype_ids is not None and p.get("archetype") not in archetype_ids:
        e.append(f"problem.archetype '{p.get('archetype')}' unknown")
    ex = p.get("domain_examples", [])
    if rec.get("provenance", {}).get("origin") == "seed" and len(ex) < 2:
        e.append("seed records need at least two domain_examples")
    u = rec["user"]
    vocab.check("user_profiles", u.get("profile"), e, "user.profile")
    if profile_ids is not None and u.get("profile") not in profile_ids:
        e.append(f"user.profile '{u.get('profile')}' has no profile file")
    vocab.check("modifiers", u.get("modifiers", []), e, "user.modifiers")
    t = rec["tasks"]
    why = t.get("why", {})
    vocab.check("why_goal", why.get("goal"), e, "tasks.why.goal")
    vocab.check("why_search", why.get("search"), e, "tasks.why.search")
    vocab.check("why_query", why.get("query"), e, "tasks.why.query")
    vocab.check("low_level_tasks", t.get("low_level", []), e, "tasks.low_level")
    vocab.check("temporal_tasks", t.get("temporal", []), e, "tasks.temporal")
    vocab.check("shneiderman_tasks", t.get("shneiderman", []), e, "tasks.shneiderman")
    d = canonicalize(rec["data"])
    vocab.check("dataset_types", d.get("dataset_type"), e, "data.dataset_type")
    for i, k in enumerate(d["keys"]):
        vocab.check("attribute_types", k.get("type"), e, f"data.keys[{i}].type")
        vocab.check("key_roles", k.get("role"), e, f"data.keys[{i}].role")
        vocab.check("cardinality_bands", k.get("cardinality"), e, f"data.keys[{i}].cardinality")
        vocab.check("temporal_grains", k.get("grain"), e, f"data.keys[{i}].grain")
    for i, v in enumerate(d["values"]):
        vocab.check("attribute_types", v.get("type"), e, f"data.values[{i}].type")
        vocab.check("value_roles", v.get("role"), e, f"data.values[{i}].role")
        vocab.check("value_semantics", v.get("semantics"), e, f"data.values[{i}].semantics")
    vocab.check("items_bands", d.get("items"), e, "data.items")
    sig = signature(d)
    if rec["data"].get("signature") and rec["data"]["signature"] != sig:
        e.append(f"data.signature '{rec['data']['signature']}' != computed '{sig}'")
    vocab.check("constraints", rec.get("constraints", []), e, "constraints")
    s = rec["solution"]
    for f in REQUIRED_SOLUTION:
        if f not in s:
            e.append(f"solution.{f} missing")
    if catalog_ids is not None and s.get("idiom") not in catalog_ids:
        e.append(f"solution.idiom '{s.get('idiom')}' not in catalog")
    vocab.check("idiom_families", s.get("family"), e, "solution.family")
    vocab.check("marks", s.get("mark"), e, "solution.mark")
    attrs = {k.get("role") for k in d["keys"]} | {v.get("role") for v in d["values"]} | {"derived", "highlight", "none"}
    for i, enc in enumerate(s.get("encodings", []) or []):
        vocab.check("channels", enc.get("channel"), e, f"solution.encodings[{i}].channel")
        vocab.check("scale_types", enc.get("scale"), e, f"solution.encodings[{i}].scale")
        if enc.get("attribute") not in attrs:
            e.append(f"solution.encodings[{i}].attribute '{enc.get('attribute')}' is not a declared role")
    c = s.get("color", {}) or {}
    vocab.check("color_purposes", c.get("purpose"), e, "solution.color.purpose")
    vocab.check("palette_types", c.get("palette_type"), e, "solution.color.palette_type")
    tx = s.get("text", {}) or {}
    vocab.check("title_styles", tx.get("title"), e, "solution.text.title")
    it = s.get("interaction", {}) or {}
    vocab.check("interaction_levels", it.get("level"), e, "solution.interaction.level")
    vocab.check("interaction_intents", it.get("intents", []), e, "solution.interaction.intents")
    for i, alt in enumerate(s.get("rejected_alternatives", []) or []):
        if catalog_ids is not None and alt.get("idiom") not in catalog_ids:
            e.append(f"solution.rejected_alternatives[{i}].idiom '{alt.get('idiom')}' not in catalog")
        if rule_ids is not None and alt.get("rule") and alt["rule"] not in rule_ids:
            e.append(f"solution.rejected_alternatives[{i}].rule '{alt['rule']}' unknown")
    if rule_ids is not None:
        for r in (s.get("validation", {}) or {}).get("stage3_checks", []) or []:
            if r not in rule_ids:
                e.append(f"solution.validation.stage3_checks '{r}' unknown")
    e.extend(validate_composition(s.get("composition"), catalog_ids))
    pr = rec["provenance"]
    vocab.check("origins", pr.get("origin"), e, "provenance.origin")
    return e


def validate_composition(comp: dict | None, catalog_ids: set[str] | None = None) -> list[str]:
    """Check the optional solution.composition block (multi-view designs).

    It is not part of the match key: a record without it is a single view.
    """
    e: list[str] = []
    if comp is None:
        return e
    if not isinstance(comp, dict):
        return ["solution.composition must be a mapping"]
    where = "solution.composition"
    if "type" not in comp:
        e.append(f"{where}.type missing")
    vocab.check("view_compositions", comp.get("type"), e, f"{where}.type")
    vocab.check("data_sharing", comp.get("data_sharing"), e, f"{where}.data_sharing")
    vocab.check("encoding_sharing", comp.get("encoding_sharing"), e, f"{where}.encoding_sharing")
    vocab.check("view_relations", comp.get("relation"), e, f"{where}.relation")
    views = comp.get("views") or []
    if comp.get("type") not in (None, "single") and len(views) < 2:
        e.append(f"{where}.views needs at least two views for type '{comp.get('type')}'")
    ids: set[str] = set()
    for i, v in enumerate(views):
        vid = v.get("id")
        if not vid:
            e.append(f"{where}.views[{i}].id missing")
        elif vid in ids:
            e.append(f"{where}.views[{i}].id '{vid}' duplicated")
        ids.add(vid)
        vocab.check("view_roles", v.get("role"), e, f"{where}.views[{i}].role")
        if catalog_ids is not None and v.get("idiom") not in catalog_ids:
            e.append(f"{where}.views[{i}].idiom '{v.get('idiom')}' not in catalog")
    for i, ln in enumerate(comp.get("links") or []):
        vocab.check("link_types", ln.get("type"), e, f"{where}.links[{i}].type")
        if "type" not in ln:
            e.append(f"{where}.links[{i}].type missing")
        for end in ("from", "to"):
            if ln.get(end) not in ids:
                e.append(f"{where}.links[{i}].{end} '{ln.get(end)}' is not a declared view")
    return e


def touch(rec: dict):
    pr = rec.setdefault("provenance", {})
    pr["times_used"] = int(pr.get("times_used") or 0) + 1
    pr["last_used"] = dt.date.today().isoformat()


def strip_for_answers(rec: dict) -> dict:
    """The answers.json view of a record (stages 1–2 only)."""
    return {k: rec[k] for k in ("problem", "user", "tasks", "data", "constraints") if k in rec}
