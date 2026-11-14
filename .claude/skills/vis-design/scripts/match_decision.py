#!/usr/bin/env python3
"""Find the stored decision (project store > seeds) that applies to an answers.json.

    python3 match_decision.py answers.json [--project-dir DIR] [--top 5]

answers.json holds the stage 1–2 answers (see references/answers-schema.md):
  problem {archetype, mode, statement, catalog_functions?}, user {profile, modifiers},
  tasks {why, low_level, temporal, shneiderman}, data {dataset_type, keys, values, items},
  constraints [], library? (optional)

Output JSON: tier (EXACT | REUSE | ADAPT | NONE), best, candidates[], catalog_candidates[],
defaults (stage-3 answers prefilled from best, library from project.yaml), store paths.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from visdesign import store, scoring, catalog  # noqa: E402
from visdesign.records import key  # noqa: E402
from visdesign.shape import canonicalize, signature  # noqa: E402


def summarize(rec: dict) -> dict:
    s = rec.get("solution", {}) or {}
    pr = rec.get("provenance", {}) or {}
    return {"id": rec["id"], "title": rec.get("title"), "status": rec.get("status"),
            "origin": pr.get("origin"), "created": pr.get("created"), "times_used": pr.get("times_used", 0),
            "idiom": s.get("idiom"), "family": s.get("family"), "confidence": rec.get("confidence"),
            "path": rec.get("_path")}


def defaults_from(rec: dict | None, project_cfg: dict) -> dict:
    d = {"library": project_cfg.get("library"), "host": project_cfg.get("host"),
         "output_dir": project_cfg.get("output_dir")}
    if rec:
        s = rec.get("solution", {}) or {}
        d.update({"idiom": s.get("idiom"), "family": s.get("family"), "mark": s.get("mark"),
                  "encodings": s.get("encodings"), "ordering": s.get("ordering"),
                  "color": s.get("color"), "text": s.get("text"), "interaction": s.get("interaction"),
                  "layout": s.get("layout"), "derived_data": s.get("derived_data"),
                  "rejected_alternatives": s.get("rejected_alternatives"),
                  "stage3_checks": (s.get("validation") or {}).get("stage3_checks"),
                  "library_notes": s.get("library_notes"), "decision_id": rec["id"]})
    return d


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("answers")
    ap.add_argument("--project-dir", help="folder holding project records (default: nearest .claude/vis-decisions)")
    ap.add_argument("--top", type=int, default=5)
    args = ap.parse_args()

    with open(args.answers, encoding="utf-8") as fh:
        q = json.load(fh)
    q["data"] = canonicalize(q.get("data") or {})
    q["data"]["signature"] = signature(q["data"])
    project_dir = store.find_project_dir(os.path.dirname(os.path.abspath(args.answers)), args.project_dir)
    project_cfg = store.load_project_yaml(project_dir)
    live, all_live = store.merged(project_dir)
    archetypes, profiles = catalog.archetypes(), catalog.profiles()

    out = {"query_key": list(key(q)), "project_dir": project_dir, "seed_dir": store.seed_dir(),
           "project_library": project_cfg.get("library"), "candidates": [], "excluded": []}
    qk = key(q)
    exact = live.get(qk)
    q_tasks = set((q.get("tasks") or {}).get("low_level") or [])
    if exact:
        r_tasks = set((exact.get("tasks") or {}).get("low_level") or []) | set((exact.get("tasks") or {}).get("low_level_secondary") or [])
        if q_tasks <= r_tasks or not q_tasks:
            out["tier"] = "EXACT"
            out["best"] = summarize(exact)
            out["best"]["score"] = 1.0
    scored = []
    for rec in all_live:
        inc = scoring.incompatible(q, rec)
        if inc:
            out["excluded"].append({"id": rec["id"], "constraint": inc})
            continue
        total, breakdown = scoring.score(q, rec, archetypes, profiles)
        scored.append((total, breakdown, rec))
    scored.sort(key=lambda t: -t[0])
    for total, breakdown, rec in scored[:args.top]:
        c = summarize(rec)
        c["score"] = total
        c["breakdown"] = breakdown
        c["tier"] = scoring.tier(total)
        out["candidates"].append(c)
    if "tier" not in out:
        if scored and (live.get(key(scored[0][2])) is scored[0][2] or True):
            total, breakdown, rec = scored[0]
            out["tier"] = scoring.tier(total)
            out["best"] = summarize(rec) if out["tier"] != "NONE" else None
            if out["best"]:
                out["best"]["score"] = total
                out["best"]["differs"] = breakdown.get("differs", [])
        else:
            out["tier"], out["best"] = "NONE", None
    best_rec = None
    if out.get("best"):
        best_rec = next(r for r in all_live if r["id"] == out["best"]["id"])
    out["defaults"] = defaults_from(best_rec, project_cfg)
    out["catalog_candidates"] = catalog.rank_candidates(q, limit=args.top)
    arch = archetypes.get((q.get("problem") or {}).get("archetype"))
    out["archetype"] = {"id": arch["id"], "name": arch["name"], "disambiguation": arch.get("disambiguation"),
                        "default_tasks": arch.get("default_tasks")} if arch else None
    out["explanations"] = []
    if out["tier"] == "EXACT":
        out["explanations"].append(f"Stored decision {out['best']['id']} applies exactly: same archetype, mode, "
                                   "profile and data-shape signature. Offer its solution as the recommended default.")
    elif out["tier"] == "REUSE":
        out["explanations"].append(f"Stored decision {out['best']['id']} is close enough to reuse; differs in: "
                                   f"{out['best'].get('differs')}.")
    elif out["tier"] == "ADAPT":
        out["explanations"].append(f"Closest stored decision {out['best']['id']} needs adaptation; ask explicitly about: "
                                   f"{out['best'].get('differs')}.")
    else:
        out["explanations"].append("No stored decision is close; use the catalog candidates.")
    json.dump(out, sys.stdout, indent=2, ensure_ascii=False, default=str)
    print()


if __name__ == "__main__":
    main()
