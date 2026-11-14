"""Seed and project decision stores, precedence, project.yaml."""
from __future__ import annotations

import glob
import os

import yaml

from . import skill_path
from .records import key, load_yaml, dump_yaml

PROJECT_SUBDIR = os.path.join(".claude", "vis-decisions")


def find_project_dir(start: str | None = None, explicit: str | None = None) -> str:
    """Walk up from `start` to the nearest folder holding `.claude/`; else use start."""
    if explicit:
        return os.path.abspath(explicit)
    cur = os.path.abspath(start or os.getcwd())
    while True:
        if os.path.isdir(os.path.join(cur, ".claude")):
            return os.path.join(cur, PROJECT_SUBDIR)
        parent = os.path.dirname(cur)
        if parent == cur:
            return os.path.join(os.path.abspath(start or os.getcwd()), PROJECT_SUBDIR)
        cur = parent


def seed_dir() -> str:
    return skill_path("decisions", "seed")


def load_dir(path: str, origin: str) -> list[dict]:
    recs = []
    for f in sorted(glob.glob(os.path.join(path, "*.yaml"))):
        if os.path.basename(f) == "project.yaml":
            continue
        try:
            r = load_yaml(f)
        except Exception as e:  # pragma: no cover
            print(f"warning: cannot read {f}: {e}")
            continue
        if not isinstance(r, dict) or "id" not in r:
            continue
        r.setdefault("provenance", {}).setdefault("origin", origin)
        r["_path"] = f
        recs.append(r)
    return recs


def load_project_yaml(project_dir: str) -> dict:
    p = os.path.join(project_dir, "project.yaml")
    return load_yaml(p) if os.path.exists(p) else {}


def save_project_yaml(project_dir: str, data: dict):
    dump_yaml(data, os.path.join(project_dir, "project.yaml"),
              header="vis-design project preferences (library is asked every run and stored here)")


def merged(project_dir: str) -> tuple[dict[tuple, dict], list[dict]]:
    """Return {key: record} with project precedence, and the list of all live records."""
    proj_cfg = load_project_yaml(project_dir)
    disabled = set(proj_cfg.get("disabled_seeds", []) or [])
    seeds = [r for r in load_dir(seed_dir(), "seed") if r["id"] not in disabled]
    project = load_dir(project_dir, "project")
    superseded = {r.get("provenance", {}).get("supersedes") for r in project}
    live = {}
    for r in seeds + project:  # project after seeds → shadows same key
        if r.get("status") not in ("declared", "candidate"):
            continue
        if r["id"] in superseded:
            continue
        live[key(r)] = r
    return live, [r for r in seeds + project if r.get("status") in ("declared", "candidate")]
