#!/usr/bin/env python3
"""Check the intent-router message files before a run.

Method and expected output: docs/experiments/2026-11-router-messages-method.md.

Prints the SHA256, the label x language counts and the boundary cases of
each file, and fails on duplicate ids, unknown problems or moves, missing
languages, or messages repeated across files. With --m3kang-dir it also
counts 8-word sequences shared with the local M3Kang files (*.jsonl). It
prints only counts and our own ids, never M3Kang text.

Usage:
    python3 laptop/router_messages_check.py
    python3 laptop/router_messages_check.py --m3kang-dir data
"""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
FILES = [HERE / "router_messages.json", HERE / "router_messages_r2.json"]
LABELS = ["stuck", "concept", "attempt", "solution", "not_productive"]
LANGS = ["cat", "esp", "eng"]


def grams(text, n=8):
    """8-word sequences, without those made only of option letters and numbers ("a 1 b 3 c 5 d 7")."""
    words = re.findall(r"\w+", text.lower())
    out = {tuple(words[i:i + n]) for i in range(len(words) - n + 1)}
    return {g for g in out if not all(re.fullmatch(r"[a-e]|\d+", w) for w in g)}


def strings(spec):
    yield from ((f"message {m['id']}", m["text"]) for m in spec["messages"])
    yield from ((f"move {k}", v) for k, v in spec["moves"].items())
    yield from ((f"problem {k}/{lang}", v) for k, p in spec["problems"].items() for lang, v in p.items())


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("files", nargs="*", type=Path, default=FILES)
    parser.add_argument("--m3kang-dir", type=Path, help="folder with the local M3Kang *.jsonl files")
    args = parser.parse_args()

    errors, seen = [], {}
    for path in args.files:
        spec = json.loads(path.read_text())
        msgs = spec["messages"]
        print(f"== {path.name}  sha256 {hashlib.sha256(path.read_bytes()).hexdigest()}")
        print(f"   {len(msgs)} messages, {len(spec['problems'])} problems, {len(spec['moves'])} moves")
        counts = Counter((m["label"], m["lang"]) for m in msgs)
        print("   " + " " * 15 + " ".join(f"{x:>4}" for x in LANGS))
        for label in LABELS:
            print(f"   {label:<15}" + " ".join(f"{counts[(label, x)]:>4}" for x in LANGS))
        boundary = Counter((m["boundary"], m["label"]) for m in msgs if m.get("boundary"))
        print(f"   boundary cases: {sum(boundary.values())}")
        for (kind, label), k in sorted(boundary.items()):
            print(f"     {k} x {kind} -> {label}")
        if len({m["id"] for m in msgs}) != len(msgs):
            errors.append(f"{path.name}: duplicate ids")
        for name, p in spec["problems"].items():
            if sorted(p) != sorted(LANGS):
                errors.append(f"{path.name}: problem {name} lacks a language")
        for m in msgs:
            if m["problem"] not in spec["problems"] or m["move"] not in spec["moves"]:
                errors.append(f"{path.name}: {m['id']} has an unknown problem or move")
            if m["label"] not in LABELS or m["lang"] not in LANGS:
                errors.append(f"{path.name}: {m['id']} has an unknown label or language")
            key = m["text"].strip().lower()
            if key in seen and seen[key] != path.name:
                errors.append(f"{path.name}: {m['id']} repeats a message of {seen[key]}")
            seen.setdefault(key, path.name)

    if args.m3kang_dir:
        ref = set()
        for f in sorted(args.m3kang_dir.glob("*.jsonl")):
            with open(f) as fh:
                for line in fh:
                    ref |= grams(line)
        for path in args.files:
            hits = [name for name, text in strings(json.loads(path.read_text())) if grams(text) & ref]
            print(f"== {path.name}: strings sharing an 8-word sequence with M3Kang: {len(hits)} {hits}")
            if hits:
                errors.append(f"{path.name}: shares text with M3Kang")

    for e in errors:
        print("ERROR:", e)
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
