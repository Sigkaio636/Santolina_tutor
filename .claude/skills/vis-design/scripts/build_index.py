#!/usr/bin/env python3
"""Regenerate the derived files of vis-design and check everything cross-references.

    python3 build_index.py            # regenerate decisions/index.json and the generated references
    python3 build_index.py --check    # validate only; exit 1 on any problem

Generated: decisions/index.json, references/user-profiles.md, references/problem-archetypes.md,
references/chart-catalog.md.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from visdesign import skill_path, catalog, store, vocab  # noqa: E402
from visdesign.records import validate, key  # noqa: E402
from visdesign.shape import signature, canonicalize  # noqa: E402


def rule_ids() -> set[str]:
    ids = set()
    p = skill_path("references", "encoding-essentials.md")
    if os.path.exists(p):
        ids |= set(re.findall(r"\b([A-Z]{3}-\d{2}|IDM-[A-Z/]+|TRUNC-\d+|TEXT-\d+|MEANBAR-\d+|RAIN-\d+)\b", open(p, encoding="utf-8").read()))
    return ids


def check_all() -> list[str]:
    problems = []
    cat = catalog.load()
    arch = catalog.archetypes()
    prof = catalog.profiles()
    funcs = catalog.functions()
    rules = rule_ids()
    # vocab coverage
    for pid in vocab.values("user_profiles"):
        if pid not in prof:
            problems.append(f"vocab user_profiles '{pid}' has no profiles/users file")
    for pid in prof:
        if pid not in vocab.values("user_profiles"):
            problems.append(f"profile file '{pid}' not in vocab user_profiles")
    # profiles
    for p in prof.values():
        c = p.get("capabilities", {})
        for f, enum in (("vis_literacy", "vis_literacy"), ("time_per_chart", "time_per_chart")):
            if c.get(f) not in vocab.values(enum):
                problems.append(f"profile {p['id']}: capabilities.{f} '{c.get(f)}' not in {enum}")
        t = p.get("cognitive_tasks", {})
        for lst in ("low_level_primary", "low_level_secondary"):
            for x in t.get(lst, []):
                if x not in vocab.values("low_level_tasks"):
                    problems.append(f"profile {p['id']}: {lst} '{x}' not a task")
        for x in t.get("shneiderman", []):
            if x not in vocab.values("shneiderman_tasks"):
                problems.append(f"profile {p['id']}: shneiderman '{x}'")
        for x in p.get("prefer_families", []):
            if x not in vocab.values("idiom_families"):
                problems.append(f"profile {p['id']}: prefer_families '{x}' not a family")
    # archetypes
    for a in arch.values():
        for f in a.get("catalog_functions", []):
            if f not in funcs:
                problems.append(f"archetype {a['id']}: function '{f}' unknown")
        for i in a.get("preferred_idioms", []):
            if i not in cat:
                problems.append(f"archetype {a['id']}: preferred idiom '{i}' not in catalog")
        for d in a.get("discouraged_idioms", []):
            if d.get("idiom") not in cat:
                problems.append(f"archetype {a['id']}: discouraged idiom '{d.get('idiom')}' not in catalog")
            if rules and d.get("rule") not in rules:
                problems.append(f"archetype {a['id']}: rule '{d.get('rule')}' not in encoding-essentials")
        for r in a.get("related_archetypes", []):
            if r not in arch:
                problems.append(f"archetype {a['id']}: related '{r}' unknown")
        dt = a.get("default_tasks", {})
        for x in dt.get("low_level", []):
            if x not in vocab.values("low_level_tasks"):
                problems.append(f"archetype {a['id']}: task '{x}'")
        for x in dt.get("temporal", []):
            if x not in vocab.values("temporal_tasks"):
                problems.append(f"archetype {a['id']}: temporal task '{x}'")
        if len(a.get("domain_examples", [])) < 2:
            problems.append(f"archetype {a['id']}: fewer than two domain_examples")
    covered = {f for a in arch.values() for f in a.get("catalog_functions", [])}
    for f in funcs:
        if f not in covered:
            problems.append(f"catalog function '{f}' covered by no archetype")
        for cid in funcs[f]["charts"]:
            if cid not in cat:
                problems.append(f"function {f}: chart '{cid}' not in catalog")
        for a_id in funcs[f].get("archetypes", []):
            if a_id not in arch:
                problems.append(f"function {f}: archetype '{a_id}' unknown")
    # catalog
    for cid, e in cat.items():
        if len(e.get("summary", "").split()) > 60:
            problems.append(f"catalog {cid}: summary over 60 words")
        if len(e.get("anatomy", "").split()) > 40:
            problems.append(f"catalog {cid}: anatomy over 40 words")
        for f in e.get("functions", []):
            if f not in funcs:
                problems.append(f"catalog {cid}: function '{f}' unknown")
        for s in e.get("similar", []):
            if s not in cat:
                problems.append(f"catalog {cid}: similar '{s}' not in catalog")
        o = e.get("ours")
        if not o:
            problems.append(f"catalog {cid}: missing ours")
            continue
        if o.get("family") not in vocab.values("idiom_families"):
            problems.append(f"catalog {cid}: family '{o.get('family')}'")
        if o.get("munzner", {}).get("mark") not in vocab.values("marks"):
            problems.append(f"catalog {cid}: mark '{o.get('munzner', {}).get('mark')}'")
        for ch in o.get("munzner", {}).get("channels", []):
            if ch not in vocab.values("channels"):
                problems.append(f"catalog {cid}: channel '{ch}'")
        for t in o.get("tasks", []):
            if t not in vocab.values("low_level_tasks"):
                problems.append(f"catalog {cid}: task '{t}'")
        for a_id in o.get("archetypes", []):
            if a_id not in arch:
                problems.append(f"catalog {cid}: archetype '{a_id}' unknown")
        for p in o.get("profile_fit", []):
            if p not in prof:
                problems.append(f"catalog {cid}: profile '{p}' unknown")
        if rules:
            for r in o.get("rules", []):
                if r not in rules:
                    problems.append(f"catalog {cid}: rule '{r}' not in encoding-essentials")
    # seeds
    seeds = store.load_dir(store.seed_dir(), "seed")
    seen_keys = {}
    for r in seeds:
        errs = validate(r, set(cat), set(arch), set(prof), rules or None)
        for e in errs:
            problems.append(f"seed {r['id']}: {e}")
        k = key(r)
        if k in seen_keys:
            problems.append(f"seed {r['id']}: duplicate key with {seen_keys[k]}")
        seen_keys[k] = r["id"]
        if os.path.splitext(os.path.basename(r["_path"]))[0] != r["id"]:
            problems.append(f"seed {r['id']}: file name does not match id")
    for a in arch.values():
        if not any(r["problem"]["archetype"] == a["id"] for r in seeds):
            problems.append(f"archetype {a['id']}: no seed decision")
    return problems


def gen_index():
    seeds = store.load_dir(store.seed_dir(), "seed")
    idx = {"by_key": {}, "by_archetype": {}, "count": len(seeds)}
    for r in seeds:
        r2 = dict(r)
        r2["data"] = canonicalize(r2["data"])
        k = "|".join(str(x) for x in key(r2))
        idx["by_key"][k] = r["id"]
        idx["by_archetype"].setdefault(r["problem"]["archetype"], []).append(r["id"])
    with open(skill_path("decisions", "index.json"), "w", encoding="utf-8") as fh:
        json.dump(idx, fh, indent=1, ensure_ascii=False)


def gen_profiles_md():
    prof = catalog.profiles()
    lines = ["# User profiles (generated from profiles/users/*.yaml by build_index.py)", "",
             "Each profile states the reader's capabilities and the cognitive tasks they perform, which the",
             "questionnaire uses to pick defaults and which the matcher uses as part of the decision key.", "",
             "| id | literacy | time | why | primary tasks | prefers | avoid |", "|---|---|---|---|---|---|---|"]
    for p in sorted(prof.values(), key=lambda p: p["id"]):
        c, t = p["capabilities"], p["cognitive_tasks"]
        w = t["why"]
        lines.append(f"| `{p['id']}` | {c['vis_literacy']} | {c['time_per_chart']} | {w['goal']}/{w['search']}/{w['query']} | "
                     f"{', '.join(t['low_level_primary'])} | {', '.join(p['prefer_families'])} | {', '.join(p['avoid'])} |")
    for p in sorted(prof.values(), key=lambda p: p["id"]):
        c, t = p["capabilities"], p["cognitive_tasks"]
        lines += ["", f"## {p['name']} (`{p['id']}`)", "", p["summary"].strip(), "",
                  f"- Capabilities: literacy {c['vis_literacy']}, domain {c['domain_knowledge']}, statistics {c['statistical_literacy']}, "
                  f"time {c['time_per_chart']}, interaction tolerance {c['interaction_tolerance']}, working-memory budget {c['working_memory_budget']} chunks.",
                  f"- Idioms that need no explanation: {', '.join(c['learned_idioms'])}; need explanation: {', '.join(c['needs_explanation']) or 'none'}.",
                  f"- Cognitive tasks: primary {', '.join(t['low_level_primary'])}; secondary {', '.join(t['low_level_secondary'])}; Shneiderman {', '.join(t['shneiderman'])}.",
                  f"- Text: title {p['text_needs']['title_style']}, annotations {p['text_needs']['annotation_density']}, units and n {'required' if p['text_needs']['needs_units_and_n'] else 'optional'}.",
                  f"- Confidence needs: {', '.join(p['confidence_needs'])}. Default mode: {p['default_mode']}. Default modifiers: {', '.join(p['default_modifiers']) or 'none'}.",
                  f"- Typical readers: {', '.join(p.get('typical_readers', []))}."]
    with open(skill_path("references", "user-profiles.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def gen_archetypes_md():
    arch = catalog.archetypes()
    seeds = store.load_dir(store.seed_dir(), "seed")
    by_a = {}
    for r in seeds:
        by_a.setdefault(r["problem"]["archetype"], []).append(r["id"])
    lines = ["# Problem archetypes (generated from profiles/problems/*.yaml by build_index.py)", "",
             "An archetype is a family of questions with an expected data shape, default tasks and preferred",
             "idioms. Stage 1 maps the user's question to one archetype; the seeds under decisions/seed/ hold",
             "the declared solutions per (archetype, data shape, profile, mode).", "",
             "| id | question | functions | preferred idioms | seeds |", "|---|---|---|---|---|"]
    for a in sorted(arch.values(), key=lambda a: a["id"]):
        lines.append(f"| `{a['id']}` | {a['question_templates'][0]} | {', '.join(a['catalog_functions'])} | "
                     f"{', '.join(a['preferred_idioms'])} | {', '.join(by_a.get(a['id'], [])) or '—'} |")
    for a in sorted(arch.values(), key=lambda a: a["id"]):
        sh = a["expected_shape"]
        keys = "; ".join(f"{k['type']} ({'/'.join(k['cardinality'])})" for k in sh["keys"]) or "none"
        vals = "; ".join(v["type"] + (f" ({v['semantics']})" if v.get("semantics") else "") for v in sh["values"]) or "none"
        lines += ["", f"## {a['name']} (`{a['id']}`)", "",
                  "Questions: " + " · ".join(a["question_templates"]),
                  f"- Data shape: {sh['dataset_type']}; keys {keys}; values {vals}.",
                  f"- Default tasks: why {a['default_tasks']['why']}; low-level {', '.join(a['default_tasks']['low_level'])}"
                  + (f"; temporal {', '.join(a['default_tasks']['temporal'])}" if a['default_tasks']['temporal'] else "") + ".",
                  f"- Preferred idioms: {', '.join(a['preferred_idioms'])}.",
                  "- Discouraged: " + "; ".join(f"{d['idiom']} when {d['when']} ({d['rule']})" for d in a["discouraged_idioms"]) + ".",
                  f"- Related: {', '.join(a['related_archetypes'])}. Sibling chart-types.md sections: {', '.join(a['chart_types_md_sections']) or 'none'}.",
                  f"- Disambiguation: {a['disambiguation'].strip()}",
                  f"- Examples: {', '.join(a['domain_examples'])}."]
    with open(skill_path("references", "problem-archetypes.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def gen_catalog_md():
    cat = catalog.load()
    funcs = catalog.functions()
    lines = ["# Chart catalog (generated from data/chart-catalog.json by build_index.py)", "",
             "Facts (functions, similar charts) come from datavizcatalogue.com; summaries are paraphrases;",
             "the characterization lines (data, tasks, scale, fit, rules) are ours. Entries marked",
             "*supplement* are not on the site.", "", "## Functions", ""]
    for fid, f in funcs.items():
        lines.append(f"- **{f['name']}** (`{fid}`): {f['description']} Charts: {', '.join(f['charts'])}. "
                     f"Archetypes: {', '.join(f.get('archetypes', []))}.")
    lines += ["", "## Charts", ""]
    for cid, e in sorted(cat.items(), key=lambda kv: kv[0].lower()):
        o = e["ours"]
        sup = " *(supplement)*" if (e.get("source") or {}).get("origin") == "supplement" else ""
        sh = o["data_shape"]
        keys = "; ".join(f"{k['type']} ({'/'.join(k['cardinality'])})" for k in sh.get("keys", [])) or "none"
        vals = "; ".join(v["type"] + (f" ({v['semantics']})" if v.get("semantics") else "") for v in sh.get("values", [])) or "none"
        lines += [f"### {e['name']} (`{cid}`){sup}", "",
                  e["summary"].strip(), "",
                  f"- Also known as: {', '.join(e.get('aliases', [])) or '—'}. Functions: {', '.join(e.get('functions', []))}.",
                  f"- Anatomy: {e['anatomy'].strip()}",
                  f"- Fits: {'; '.join(e.get('fits', []))}.",
                  f"- Limits: {'; '.join(e.get('limits', []))}.",
                  f"- Data: {sh.get('dataset_type')}; keys {keys}; values {vals}. Mark {o['munzner']['mark']}; channels {', '.join(o['munzner']['channels'])}.",
                  f"- Tasks: {', '.join(o['tasks'])}. Scale: {o['scalability']}. Modes: {', '.join(o['mode_fit'])}. Profiles: {', '.join(o['profile_fit'])}.",
                  f"- Rules: {', '.join(o['rules'])}. " + (f"Discouraged ({o['discouraged']['rule']}): {o['discouraged']['reason']}. " if o.get("discouraged") else "")
                  + f"Libraries: altair {o['library_support']['altair']}, matplotlib {o['library_support']['matplotlib']}, plotly {o['library_support']['plotly']}.",
                  f"- Archetypes: {', '.join(o['archetypes'])}. Similar: {', '.join(e.get('similar', [])) or '—'}."
                  + (f" Sibling chart-types.md: {o['chart_types_md_section']}." if o.get("chart_types_md_section") else ""), ""]
    with open(skill_path("references", "chart-catalog.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    problems = check_all()
    if args.check:
        for p in problems:
            print("PROBLEM:", p)
        print(f"{len(problems)} problem(s)")
        sys.exit(1 if problems else 0)
    gen_index()
    gen_profiles_md()
    gen_archetypes_md()
    gen_catalog_md()
    for p in problems:
        print("PROBLEM:", p)
    print(f"generated index.json, user-profiles.md, problem-archetypes.md, chart-catalog.md; {len(problems)} problem(s)")


if __name__ == "__main__":
    main()
