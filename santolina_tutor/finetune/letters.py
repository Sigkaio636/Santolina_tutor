"""Build the head-A dataset: the board's exact A-E prompt, with shuffled options.

Each training problem with five OCR options appears with --perms option orders,
the label moved with its option. The letter alone then carries no signal, so the
model can't learn a letter bias. Validation keeps the original order, the way
the jury's test set arrives.

The prompt comes from copilot/llm.py (build_messages), the same function the
board calls, so training and inference can't drift apart.

    uv run python -m santolina_tutor.finetune.letters \
        --train data/train.jsonl --val data/val.jsonl --out data/finetune/letters

Output is derived from M3Kang (research use only): it stays under data/.
"""
import argparse
import collections
import json
import os
import random

from copilot.llm import build_messages

LETTERS = "ABCDE"


def has_options(p):
    return set(p.get("options") or {}) == set(LETTERS)


def permuted(p, order):
    """The same problem with options reordered: order[i] is the old letter shown at LETTERS[i]."""
    options = {new: p["options"][old] for new, old in zip(LETTERS, order)}
    label = LETTERS[order.index(p["label"])]
    return {**p, "options": options, "label": label}


def row(p, perm):
    return {"id": p["id"], "language": p["language"], "level": p["level"], "perm": perm,
            "messages": build_messages(p), "label": p["label"]}


def read(path):
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--train", required=True)
    ap.add_argument("--val", required=True)
    ap.add_argument("--out", required=True, help="folder for train.jsonl and val.jsonl")
    ap.add_argument("--perms", type=int, default=4, help="option orders per training problem")
    ap.add_argument("--languages", default="eng,cat,esp")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    langs = set(args.languages.split(","))
    rng = random.Random(args.seed)
    train = [p for p in read(args.train) if p["language"] in langs and has_options(p)]
    val = [p for p in read(args.val) if p["language"] in langs and has_options(p)]
    assert not {p["id"] for p in train} & {p["id"] for p in val}, "train and val share ids"

    train_rows = []
    for p in train:
        orders = [tuple(LETTERS)]
        while len(orders) < args.perms:  # distinct random orders, the original first
            order = tuple(rng.sample(LETTERS, 5))
            if order not in orders:
                orders.append(order)
        train_rows += [row(permuted(p, list(o)), "".join(o)) for o in orders]
    rng.shuffle(train_rows)
    val_rows = [row(p, LETTERS) for p in val]

    os.makedirs(args.out, exist_ok=True)
    for name, rows in (("train", train_rows), ("val", val_rows)):
        with open(os.path.join(args.out, f"{name}.jsonl"), "w") as f:
            f.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)
        letters = collections.Counter(r["label"] for r in rows)
        langs_n = collections.Counter(r["language"] for r in rows)
        print(f"{name}: {len(rows)} rows, letters {dict(sorted(letters.items()))}, "
              f"languages {dict(langs_n)}")


if __name__ == "__main__":
    main()
