#!/usr/bin/env python3
"""Compare eval.py runs on the same validation file. Prints aggregates only.

For each run it prints accuracy with a 95 % Wilson interval, overall, by
language and by stratum (text-only or with a figure, crossed with whether OCR
found the five options), plus the letters it answered. For each run after the
first it prints an exact McNemar test against the first run, paired by
problem id and language.

It never prints problem text, so its output can go into a committed report.

Usage:
    python3 laptop/compare_runs.py data/val.jsonl \\
        baseline=results/eval-...-laptop-baseline.csv \\
        decider=results/eval-...-laptop-decider.csv
"""

from collections import Counter
import csv
import json
from math import comb, sqrt
import sys


def wilson(k, n, z=1.96):
    """95 % Wilson score interval for k successes out of n, in percent."""
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return 100 * (c - h), 100 * (c + h)


def mcnemar(pairs):
    """Exact two-sided McNemar from (first right, other right) pairs."""
    only_first = sum(a and not b for a, b in pairs)
    only_other = sum(b and not a for a, b in pairs)
    n = only_first + only_other
    tail = sum(comb(n, i) for i in range(min(only_first, only_other) + 1))
    p = min(1.0, 2 * tail / 2**n) if n else 1.0
    return only_first, only_other, p


def is_right(row):
    return row["correct"] in ("1", "True", "true")


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    val_path, run_args = sys.argv[1], sys.argv[2:]

    meta = {}
    with open(val_path) as f:
        for line in f:
            r = json.loads(line)
            meta[(r["id"], r["language"])] = {
                "language": r["language"],
                "text_only": bool(r["text_only"]),
                "options": len(r.get("options") or {}) == 5,
                "label": r["label"],
            }

    runs = {}
    for arg in run_args:
        name, path = arg.split("=", 1)
        with open(path) as f:
            runs[name] = {(r["id"], r["language"]): r for r in csv.DictReader(f)}
        missing = meta.keys() - runs[name].keys()
        if missing:
            sys.exit(f"{name}: {len(missing)} validation rows missing from {path}")

    groups = {"all": lambda m: True}
    for lang in sorted({m["language"] for m in meta.values()}):
        groups[f"lang={lang}"] = lambda m, lang=lang: m["language"] == lang
    for text_only in (True, False):
        for options in (True, False):
            label = f"{'text-only' if text_only else 'figure'}, {'5 options' if options else 'no options'}"
            groups[label] = lambda m, t=text_only, o=options: (
                m["text_only"] == t and m["options"] == o
            )

    names = list(runs)
    for label, keep in groups.items():
        keys = [k for k, m in meta.items() if keep(m)]
        n = len(keys)
        labels = Counter(meta[k]["label"] for k in keys)
        floors = ", ".join(f"always {x} {100 * labels[x] / n:.1f}%" for x in "ABCDE")
        print(f"\n== {label}  (n={n}{', noise: n<50' if n < 50 else ''})")
        print(f"   floors: {floors}")
        for name in names:
            k = sum(is_right(runs[name][key]) for key in keys)
            lo, hi = wilson(k, n)
            letters = Counter(runs[name][key]["answer"] for key in keys)
            mix = " ".join(f"{x}={letters[x]}" for x in "ABCDE")
            print(
                f"   {name:<16} {100 * k / n:5.1f}% [{lo:4.1f}-{hi:4.1f}]  {k}/{n}  answers {mix}"
            )
        for name in names[1:]:
            pairs = [(is_right(runs[names[0]][key]), is_right(runs[name][key])) for key in keys]
            a, b, p = mcnemar(pairs)
            print(
                f"   McNemar {names[0]} vs {name}: only {names[0]} right={a}, only {name} right={b}, p={p:.3f}"
            )


if __name__ == "__main__":
    main()
