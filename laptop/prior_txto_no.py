#!/usr/bin/env python3
"""Measure no-model letter heuristics on the figure rows (text_only false).

Report: docs/experiments/2026-11-txto-no-heuristics.md.

Splits the rows by what OCR left in the options (the `kind` of copilot/prior.py),
then compares each heuristic with always answering D, on train and on val, with an
exact McNemar test on one row per problem. Prints only counts and percentages,
never problem text (M3Kang rule).

    python3 laptop/prior_txto_no.py
"""
import argparse
import collections
import difflib
import json
import os
import re
import statistics
import sys
from math import comb

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from copilot.prior import kind, number  # noqa: E402

L = "ABCDE"


def load(path):
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def numbers(r):
    """Option values when all five options hold one number each (ties allowed)."""
    o = r.get("options") or {}
    if any(x not in o for x in L):
        return None
    v = {x: number(o[x]) for x in L}
    return None if None in v.values() else v


def by_rank(v, i):
    return sorted(L, key=lambda x: (v[x], x))[i]


def neighbours(v):
    """The option whose value +-1, x2 or /2 is also among the options."""
    score = {x: sum(v[y] in (v[x] * 2, v[x] / 2, v[x] + 1, v[x] - 1) for y in L if y != x) for x in L}
    return max(L, key=lambda x: (score[x], x == "D"))


def closest_mean(v):
    m = statistics.mean(v.values())
    return min(L, key=lambda x: (abs(v[x] - m), x != "D"))


def text_rule(r, name):
    t = {x: re.sub(r"\s+", " ", str(r["options"][x]).strip().lower()) for x in L}
    if name in ("longest", "shortest"):
        sign = 1 if name == "longest" else -1
        return max(L, key=lambda x: (sign * len(t[x]), x == "D"))
    sim = {x: sum(difflib.SequenceMatcher(None, t[x], t[y]).ratio() for y in L if y != x) for x in L}
    sign = 1 if name == "most_similar" else -1
    return max(L, key=lambda x: (sign * sim[x], x == "D"))


NUMERIC = {"median": lambda v: by_rank(v, 2), "rank 2": lambda v: by_rank(v, 1),
           "rank 4": lambda v: by_rank(v, 3), "closest to mean": closest_mean,
           "neighbours": neighbours}
TEXT = ["longest", "shortest", "most_similar", "least_similar"]


def mcnemar(b, c):
    n = b + c
    return 1.0 if n == 0 else min(1.0, 2 * sum(comb(n, i) for i in range(min(b, c) + 1)) / 2 ** n)


def pct(k, n):
    return f"{100 * k / n:5.1f} %" if n else "   -  "


def compare(rows, rule):
    """Accuracy of rule and of D over rows, and McNemar on one row per problem."""
    k = sum(rule(r) == r["label"] for r in rows)
    d = sum(r["label"] == "D" for r in rows)
    first = {}
    for r in rows:
        first.setdefault(r["id"], r)
    b = sum(rule(r) == r["label"] != "D" for r in first.values())
    c = sum(r["label"] == "D" != rule(r) for r in first.values())
    return k, d, len(rows), len(first), b, c


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--train", default="data/train.jsonl")
    p.add_argument("--val", default="data/interim/val_txto_no.jsonl")
    args = p.parse_args()
    splits = {"train": [r for r in load(args.train) if not r["text_only"]],
              "val": [r for r in load(args.val) if not r["text_only"]]}
    splits["both"] = splits["train"] + splits["val"]

    print("Rows and label shares by kind of options")
    for name, rows in splits.items():
        groups = collections.defaultdict(list)
        for r in rows:
            groups[kind(r)[0]].append(r)
        for k in ("none", "text", "sorted", "mixed"):
            g = groups[k]
            c = collections.Counter(r["label"] for r in g)
            print(f"  {name:5s} {k:6s} rows={len(g):4d} problems={len({r['id'] for r in g}):3d} "
                  + " ".join(f"{x}:{pct(c[x], len(g))}" for x in L))

    print("\nAnswer position by value rank (1 = smallest), distinct numeric options")
    for name, rows in splits.items():
        for k in ("sorted", "mixed"):
            ranks = collections.Counter(kind(r)[1].index(r["label"]) + 1 for r in rows if kind(r)[0] == k)
            n = sum(ranks.values())
            print(f"  {name:5s} {k:6s} n={n:4d} " + " ".join(f"{i}:{pct(ranks[i], n)}" for i in range(1, 6)))

    print("\nHeuristic vs always D: rows right (rule / D), and McNemar on one row per problem")
    cases = [(f"numeric {k}: {rn}", lambda r, k=k: kind(r)[0] == k, lambda r, f=f: f(numbers(r)))
             for k in ("sorted", "mixed") for rn, f in NUMERIC.items()]
    cases += [(f"text: {t}", lambda r: kind(r)[0] == "text", lambda r, t=t: text_rule(r, t)) for t in TEXT]
    for label, keep, rule in cases:
        out = []
        for name, rows in splits.items():
            k, d, n, probs, b, c = compare([r for r in rows if keep(r)], rule)
            out.append(f"{name} {pct(k, n)} / {pct(d, n)}")
        print(f"  {label:28s} " + " | ".join(out) + f" | problems={probs} rule-only={b} D-only={c} p={mcnemar(b, c):.3f}")

    print("\nWhole policy")
    for name, rows in splits.items():
        n = len(rows)
        median_numeric = sum((kind(r)[1][2] if kind(r)[1] else "D") == r["label"] for r in rows)
        median_mixed = sum((kind(r)[1][2] if kind(r)[0] == "mixed" else "D") == r["label"] for r in rows)
        all_d = sum(r["label"] == "D" for r in rows)
        print(f"  {name:5s} rows={n:4d} always D {pct(all_d, n)} | median on mixed {pct(median_mixed, n)}"
              f" | median on sorted+mixed (current prior) {pct(median_numeric, n)}")


if __name__ == "__main__":
    main()
