#!/usr/bin/env python3
"""Draw a stratified sample of the figure rows (text_only false) for a time-boxed run.

Strata: language x whether OCR found the options. Each stratum gets its share of n
(largest remainder), drawn with a fixed seed. Prints counts only, never problem text.

    python3 laptop/sample_txto_no.py --n 175

The output stays in data/interim/, out of Git (M3Kang rule).
"""
import argparse
import json
import random
from collections import defaultdict


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--input", default="data/interim/val_txto_no.jsonl")
    p.add_argument("--n", type=int, default=175)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--output", help="default: data/interim/txto_no_s<n>.jsonl")
    args = p.parse_args()

    with open(args.input) as f:
        rows = [json.loads(line) for line in f if line.strip()]
    strata = defaultdict(list)
    for r in rows:
        strata[(r["language"], bool(r.get("options")))].append(r)

    keys = sorted(strata)
    quota = {k: args.n * len(strata[k]) / len(rows) for k in keys}
    take = {k: int(quota[k]) for k in keys}
    for k in sorted(keys, key=lambda k: quota[k] - take[k], reverse=True)[:args.n - sum(take.values())]:
        take[k] += 1

    rng = random.Random(args.seed)
    sample = []
    print(f"{'language':<9}{'options':<9}{'population':>11}{'sample':>8}")
    for k in keys:
        sample += rng.sample(strata[k], take[k])
        print(f"{k[0]:<9}{str(k[1]):<9}{len(strata[k]):>11}{take[k]:>8}")
    print(f"{'total':<18}{len(rows):>11}{len(sample):>8}")

    out = args.output or f"data/interim/txto_no_s{args.n}.jsonl"
    with open(out, "w") as f:
        for r in sample:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
