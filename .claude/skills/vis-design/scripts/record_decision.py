#!/usr/bin/env python3
"""Validate and persist a decision record in the project store.

    python3 record_decision.py record.yaml|record.json [--project-dir DIR] [--dry-run]
                               [--supersede OLD_ID] [--assumed] [--library L --host H --output-dir D]
    python3 record_decision.py --touch ID [--project-dir DIR]
    python3 record_decision.py --set-library L [--host H] [--output-dir D] [--project-dir DIR]

- Validates against profiles/vocab.yaml, the catalog ids, archetype and profile ids and the
  rule ids known to the skill (references/encoding-essentials.md, or the sibling's catalog).
- Assigns a project id (p-<archetype>--<slug>-<yyyymmdd>) unless the record already has an
  id that lives in the project store (then it is a new version: the old file is marked
  superseded and the new one carries provenance.supersedes).
- Never overwrites a file. Seeds are never edited; a project record with the same key
  shadows the seed.
- --touch only bumps times_used/last_used of a project record (seeds: no-op).
- Writes project.yaml (library/host/output_dir) when given.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from visdesign import store, catalog  # noqa: E402
from visdesign.records import (validate, key, new_project_id, dump_yaml, load_yaml,  # noqa: E402
                               touch, SCHEMA_VERSION)
from visdesign.shape import canonicalize, signature  # noqa: E402
from visdesign import skill_path  # noqa: E402


def known_rule_ids() -> set[str]:
    ids = set()
    for p in (skill_path("references", "encoding-essentials.md"),):
        if os.path.exists(p):
            ids |= set(re.findall(r"\b([A-Z]{3}-\d{2}|IDM-[A-Z/]+|TRUNC-\d+|TEXT-\d+|MEANBAR-\d+)\b", open(p, encoding="utf-8").read()))
    sib = os.path.join(os.path.dirname(skill_path()), "vis-value-critique", "references", "rules-catalog.md")
    if os.path.exists(sib):
        ids |= set(re.findall(r"\*\*([A-Z]{3}-\d{2}|IDM-[A-Z/]+)\*\*", open(sib, encoding="utf-8").read()))
    return ids


def load_record(path: str) -> dict:
    if path.lower().endswith(".json"):
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    return load_yaml(path)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("record", nargs="?")
    ap.add_argument("--project-dir")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--supersede", help="id of the project record this one replaces")
    ap.add_argument("--assumed", action="store_true", help="store with status candidate (autonomous run)")
    ap.add_argument("--touch", help="bump usage of this record id")
    ap.add_argument("--set-library")
    ap.add_argument("--library")
    ap.add_argument("--host")
    ap.add_argument("--output-dir")
    args = ap.parse_args()

    project_dir = store.find_project_dir(None, args.project_dir)
    os.makedirs(project_dir, exist_ok=True)
    cfg = store.load_project_yaml(project_dir)
    lib = args.set_library or args.library
    if lib or args.host or args.output_dir:
        if lib:
            cfg["library"] = lib
        if args.host:
            cfg["host"] = args.host
        if args.output_dir:
            cfg["output_dir"] = args.output_dir
        cfg["updated"] = dt.date.today().isoformat()
        if not args.dry_run:
            store.save_project_yaml(project_dir, cfg)
    if args.touch:
        live, all_live = store.merged(project_dir)
        rec = next((r for r in all_live if r["id"] == args.touch), None)
        if not rec:
            raise SystemExit(f"no live record with id {args.touch}")
        if rec["provenance"].get("origin") == "project" and not args.dry_run:
            path = rec.pop("_path")
            touch(rec)
            dump_yaml(rec, path, header="vis-design decision record (project)")
            print(json.dumps({"touched": args.touch, "path": path, "times_used": rec["provenance"]["times_used"]}))
        else:
            print(json.dumps({"touched": args.touch, "note": "seed or dry-run: nothing written"}))
        if not args.record:
            return
    if not args.record:
        print(json.dumps({"project_dir": project_dir, "project": cfg}))
        return

    rec = load_record(args.record)
    rec.setdefault("schema_version", SCHEMA_VERSION)
    rec["data"] = canonicalize(rec.get("data") or {})
    rec["data"]["signature"] = signature(rec["data"])
    rec.setdefault("constraints", [])
    rec.setdefault("rationale", "")
    rec.setdefault("confidence", "medium")
    pr = rec.setdefault("provenance", {})
    pr["origin"] = "project"
    pr.setdefault("author", "vis-design")
    pr.setdefault("created", dt.date.today().isoformat())
    pr["updated"] = dt.date.today().isoformat()
    pr.setdefault("times_used", 1)
    pr.setdefault("last_used", dt.date.today().isoformat())
    if args.supersede:
        pr["supersedes"] = args.supersede
    rec["status"] = "candidate" if args.assumed else rec.get("status", "declared")
    if rec["status"] not in ("declared", "candidate"):
        rec["status"] = "declared"
    existing = {os.path.splitext(os.path.basename(f))[0] for f in os.listdir(project_dir) if f.endswith(".yaml")}
    rid = rec.get("id")
    if not rid or rid in existing or not str(rid).startswith("p-"):
        rec["id"] = new_project_id(rec, existing)
    rec.setdefault("title", rec["problem"].get("statement", rec["id"])[:80])
    errors = validate(rec, set(catalog.load()), set(catalog.archetypes()), set(catalog.profiles()), known_rule_ids() or None)
    out = {"id": rec["id"], "key": list(key(rec)), "project_dir": project_dir, "errors": errors,
           "status": rec["status"]}
    if errors:
        out["written"] = False
        print(json.dumps(out, indent=2, ensure_ascii=False))
        sys.exit(1)
    path = os.path.join(project_dir, rec["id"] + ".yaml")
    if args.dry_run:
        out["written"] = False
        out["would_write"] = path
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return
    dump_yaml(rec, path, header="vis-design decision record (project)")
    if args.supersede:
        old = os.path.join(project_dir, args.supersede + ".yaml")
        if os.path.exists(old):
            txt = open(old, encoding="utf-8").read()
            txt = re.sub(r"^status:.*$", "status: superseded", txt, count=1, flags=re.M)
            open(old, "w", encoding="utf-8").write(txt)
            out["superseded"] = old
    out["written"] = True
    out["path"] = path
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
