"""The Kangaroo library: the solved problems of a board's retrieval index, by topic and level.

The teacher copies it from a plugged-in board (`refresh`): the index (`rag_index_path`,
built by build_index.py) and the topic labels (`topics.jsonl` in the board root). Both stay
in the teacher app's folder, outside Git: M3Kang is for research use only. A pack made from
the library (`make_pack`) keeps `m3kang_id` and `topic`, so the copilot finds each problem's
neighbours and the student app groups Practice by topic.
"""

import json
from pathlib import Path
import shutil
import sqlite3
import tempfile

from classroom import paths
from classroom.packs import write_pack

from .m3kang import exercise_from, manifest_for

# The order of the LED matrix's mastery map (docs/LED_MATRIX_DESIGN.md)
TOPICS = (
    "arithmetic",
    "algebra",
    "number_theory",
    "counting",
    "logic",
    "geometry",
    "spatial",
    "measurement",
    "patterns",
)
LEVELS = tuple(range(8))
INDEX = "index.db"
TOPIC_FILE = "topics.jsonl"


def folder(home: Path) -> Path:
    return Path(home) / "kangaroo"


def refresh(link, home: Path) -> dict:
    """Copy the index and the topics of a plugged-in board. Returns what was copied."""
    status = link.status()
    path = (status.get("rag") or {}).get("path") or (status.get("identity") or {}).get(
        "rag_index_path"
    )
    if not path:
        raise FileNotFoundError("the board reports no retrieval index")
    out = folder(home)
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        link.pull_index(path, Path(tmp) / INDEX)
        shutil.move(Path(tmp) / INDEX, out / INDEX)
        topics = link.read_text(paths.TOPICS)
    if topics is not None:
        (out / TOPIC_FILE).write_text(topics, encoding="utf-8")
    problems = load(home)
    return {
        "problems": len(problems),
        "with_topic": sum(1 for p in problems if p.get("topic")),
        "topics_file": topics is not None,
    }


def load(home: Path) -> list:
    """Every problem of the library, with its topic when the labels have it. [] if empty."""
    out = folder(home)
    if not (out / INDEX).is_file():
        return []
    topics = {}
    if (out / TOPIC_FILE).is_file():
        for line in (out / TOPIC_FILE).read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                topics[row["id"]] = row.get("topic")
    db = sqlite3.connect(f"file:{out / INDEX}?mode=ro", uri=True)
    try:
        rows = [json.loads(problem) for (problem,) in db.execute("SELECT problem FROM problems")]
    finally:
        db.close()
    for p in rows:
        p["topic"] = p.get("topic") or topics.get(p.get("id"))
        p["key"] = f"{p['id']}|{p['language']}"
        p["usable"] = bool(p.get("options")) and p.get("text_only") is not False
    rows.sort(key=lambda p: (p.get("level") or 0, p.get("year") or 0, p["key"]))
    return rows


def languages(problems: list) -> list:
    return sorted({p["language"] for p in problems})


def select(problems, topic=None, level=None, language=None, query="", usable=True) -> list:
    query = (query or "").strip().lower()
    return [
        p
        for p in problems
        if (not usable or p["usable"])
        and (not topic or p.get("topic") == topic)
        and (level is None or p.get("level") == level)
        and (not language or p["language"] == language)
        and (not query or query in (p.get("text") or "").lower())
    ]


def grid(problems: list, language=None) -> list:
    """Rows of the topic x level grid: [{"topic", "cells": [n per level], "total"}]."""
    counts = {}
    for p in select(problems, language=language):
        counts[(p.get("topic"), p.get("level"))] = (
            counts.get((p.get("topic"), p.get("level")), 0) + 1
        )
    topics = list(TOPICS) + sorted({t for t, _ in counts if t and t not in TOPICS})
    if any(t is None for t, _ in counts):
        topics.append(None)
    rows = [{"topic": t, "cells": [counts.get((t, lv), 0) for lv in LEVELS]} for t in topics]
    for r in rows:
        r["total"] = sum(r["cells"])
    return [r for r in rows if r["total"]]


def make_pack(problems: list, keys: list, out_dir: Path, pack_id: str, title: str) -> Path:
    """A pack with the chosen problems, in the order of the library."""
    chosen = set(keys)
    exercises = [exercise_from(p) for p in problems if p["key"] in chosen and p["usable"]]
    if not exercises:
        raise ValueError("no usable problem chosen")
    return write_pack(Path(out_dir) / pack_id, manifest_for(exercises, pack_id, title), exercises)
