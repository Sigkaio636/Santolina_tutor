"""Label every M3Kang problem with a topic, using Claude through `claude -p`.

Runs on the laptop, on the user's Claude subscription (no API key). Each call
gets a batch of English problems with their images and returns one label per
problem, validated against a JSON schema. Labels are per `id`, so they apply
to the Catalan and Spanish versions of the same problem too.

    uv run python -m santolina_tutor.topics \
        --problems data/train.jsonl data/val.jsonl \
        --images claude_workspace/explore/img/eng \
        --model haiku --out data/topics/haiku.jsonl --limit 100

The output is derived from M3Kang (research use only): keep it under data/,
which Git ignores. Never commit it.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
import random
import subprocess
import sys
import time

from santolina_tutor.claude_cli import claude_json

TOPICS = {
    "arithmetic": "computing with numbers in a story: sums, products, money, ages, fractions, percentages",
    "algebra": "unknown quantities found by setting up and solving equations or inequalities",
    "number_theory": "digits, divisibility, primes, remainders, parity, properties of integers",
    "counting": "counting arrangements, paths, subsets or cases; combinatorics and probability",
    "logic": "truth-tellers and liars, who-is-where, orderings, deductions from statements",
    "geometry": "plane figures: lengths, areas, perimeters, angles, triangles, circles, grids measured",
    "spatial": "visual and 3D reasoning: cubes, nets, folding, rotations, mirrors, which piece fits",
    "measurement": "time, clocks, calendars, units, speed and distance",
    "patterns": "sequences, repeating patterns, rules that continue, operations defined in the problem",
}
METHODS = ["direct_computation", "equation", "enumeration", "case_analysis",
           "visual_inspection", "construction"]
ANSWER_TYPES = ["number", "expression", "figure", "statement"]

LABEL_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "topic": {"type": "string", "enum": list(TOPICS)},
        "needs_figure": {"type": "boolean"},
        "answer_type": {"type": "string", "enum": ANSWER_TYPES},
        "method": {"type": "string", "enum": METHODS},
        "program_solvable": {"type": "boolean"},
    },
    "required": ["id", "topic", "needs_figure", "answer_type", "method", "program_solvable"],
    "additionalProperties": False,
}
BATCH_SCHEMA = {
    "type": "object",
    "properties": {"labels": {"type": "array", "items": LABEL_SCHEMA}},
    "required": ["labels"],
    "additionalProperties": False,
}

SYSTEM = """You label Kangaroo math competition problems for a dataset. You do not solve them.
For each problem, read its image with the Read tool (the image shows the figure and the five options), then give:

topic: the single best fit.
""" + "\n".join(f"- {k}: {v}" for k, v in TOPICS.items()) + """

needs_figure: true if the problem cannot be solved from the text and the option values alone.
answer_type: what the five options are (number, expression, figure, or statement in words).
method: the main way a strong student would solve it.
program_solvable: true only if a short Python program, written from the text and the option values (no figure), could compute the correct answer, for example by solving equations or by brute-force search over cases.

Return exactly one label per problem, with the problem's id unchanged."""


def load_english(paths):
    problems = {}
    for path in paths:
        with open(path) as f:
            for line in f:
                p = json.loads(line)
                if p.get("language") == "eng":
                    problems[p["id"]] = p
    return problems


def describe(p, image_path):
    lines = [f"id: {p['id']} (level {p['level']})", f"image: {image_path}", p["text"].strip()]
    options = p.get("options") or {}
    if options:
        lines += [f"{k}) {v}" for k, v in sorted(options.items())]
    else:
        lines.append("(options: only in the image)")
    return "\n".join(lines)


def classify_batch(batch, images, model, timeout):
    prompt = "Label these problems.\n\n" + "\n\n---\n\n".join(
        describe(p, os.path.join(images, p["id"] + ".png")) for p in batch)
    output, ms = claude_json(prompt, SYSTEM, BATCH_SCHEMA, model, timeout, read_dir=images)
    labels = {lab["id"]: lab for lab in output["labels"]}
    missing = [p["id"] for p in batch if p["id"] not in labels]
    if missing:
        raise RuntimeError(f"missing labels for {missing}")
    return [labels[p["id"]] for p in batch], ms


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--problems", nargs="+", required=True, help="train/val JSONL from prepare_m3kang.py")
    ap.add_argument("--images", required=True, help="folder with <id>.png for every English problem")
    ap.add_argument("--model", default="haiku", help="claude -p model alias or full name")
    ap.add_argument("--out", required=True, help="JSONL output; existing ids are skipped (resume)")
    ap.add_argument("--limit", type=int, default=0, help="only a fixed random sample of N problems")
    ap.add_argument("--batch", type=int, default=10)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--timeout", type=int, default=600, help="seconds per batch")
    args = ap.parse_args()

    problems = load_english(args.problems)
    ids = sorted(problems)
    if args.limit:  # a fixed random sample, so every level is in a pilot
        ids = sorted(random.Random(0).sample(ids, args.limit))
    done = set()
    if os.path.exists(args.out):
        with open(args.out) as f:
            done = {json.loads(line)["id"] for line in f if line.strip()}
    todo = [problems[i] for i in ids if i not in done]
    missing_images = [p["id"] for p in todo if not os.path.exists(os.path.join(args.images, p["id"] + ".png"))]
    if missing_images:
        sys.exit(f"{len(missing_images)} images missing, e.g. {missing_images[:3]}")
    batches = [todo[i:i + args.batch] for i in range(0, len(todo), args.batch)]
    print(f"{len(ids)} problems, {len(done)} already labelled, {len(batches)} batches to run "
          f"with {args.model}", file=sys.stderr)

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    failed = 0
    start = time.time()
    with open(args.out, "a") as out, ThreadPoolExecutor(args.workers) as pool:
        futures = {pool.submit(classify_batch, b, args.images, args.model, args.timeout): b for b in batches}
        for n, fut in enumerate(as_completed(futures), 1):
            batch = futures[fut]
            try:
                labels, ms = fut.result()
            except (RuntimeError, subprocess.TimeoutExpired, json.JSONDecodeError, KeyError) as error:
                # one bad batch must not stop the run; rerunning resumes it
                failed += 1
                print(f"[{n}/{len(batches)}] FAILED {batch[0]['id']}..: {error}", file=sys.stderr)
                continue
            out.writelines(json.dumps({**lab, "model": args.model}) + "\n" for lab in labels)
            out.flush()
            print(f"[{n}/{len(batches)}] {len(labels)} labels in {ms / 1000:.0f} s", file=sys.stderr)
    print(f"done in {time.time() - start:.0f} s, {failed} failed batches", file=sys.stderr)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
