"""Head B data: Claude writes a short Python solve() per problem, code checks it.

    generate  Claude (claude -p, subscription) writes one program per problem. It sees
              the text and the options, never the label, so a program can only
              pass by actually computing the answer.
    verify    Each program runs in a separate, resource-limited Python process. Its
              result is matched to the option values; it passes only if it matches
              exactly one option and that option is the label.

    uv run python -m santolina_tutor.finetune.programs generate \
        --problems data/train.jsonl data/val.jsonl --topics data/topics/topics.jsonl \
        --out data/programs/sonnet.jsonl
    uv run python -m santolina_tutor.finetune.programs verify \
        --problems data/train.jsonl data/val.jsonl --programs data/programs/sonnet.jsonl \
        --out data/programs/verified.jsonl

Candidates: English problems labelled program_solvable and not needs_figure, with
all five OCR options. Output is derived from M3Kang: it stays under data/.
"""
import argparse
import collections
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
import subprocess
import sys

from copilot.program_head import format_problem, is_constant, matches, run_program

from santolina_tutor.claude_cli import claude_json

LETTERS = "ABCDE"
SYSTEM = """You write tiny Python programs that solve math competition problems by computing the answer.

For each problem, write a function solve() that returns the answer's value: a number (int, float or fractions.Fraction) or, if the options are not numbers, a string equal to one option's text. Rules:
- Compute the answer from the data in the problem: equations, formulas, or brute-force search over cases. Never return a value you worked out in your head, and never return an option letter.
- Only the standard library: math, itertools, fractions, functools, collections. No input, no printing, no files.
- As short as possible: a small model will learn to write these. Aim for under 12 lines, no comments, short names.
- It must finish in under one second.
Return one program per problem, with the problem's id unchanged."""

SCHEMA = {
    "type": "object",
    "properties": {"programs": {"type": "array", "items": {
        "type": "object",
        "properties": {"id": {"type": "string"}, "program": {"type": "string"}},
        "required": ["id", "program"], "additionalProperties": False}}},
    "required": ["programs"], "additionalProperties": False,
}

def read_jsonl(path):
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def english(paths):
    """English problems by id, each tagged with its split from the file name (train/val)."""
    split = lambda path: "val" if "val" in os.path.basename(path) else "train"
    return {p["id"]: {**p, "split": split(path)}
            for path in paths for p in read_jsonl(path) if p["language"] == "eng"}


def prompt_text(p):
    return format_problem(p)


# ---------- generate ----------

def generate_batch(batch, model, timeout):
    """batch: list of (problem, retry) where retry is None or {"attempt", "note", "revealed"}."""
    def block(p, retry):
        text = f"id: {p['id']}\n{prompt_text(p)}"
        return text + (f"\n\n{retry['note']}" if retry else "")
    prompt = "Write solve() for each problem.\n\n" + "\n\n---\n\n".join(block(p, r) for p, r in batch)
    output, ms = claude_json(prompt, SYSTEM, SCHEMA, model, timeout)
    progs = {x["id"]: x["program"] for x in output["programs"]}
    missing = [p["id"] for p, _ in batch if p["id"] not in progs]
    if missing:
        raise RuntimeError(f"missing programs for {missing}")
    return [{"id": p["id"], "program": progs[p["id"]], "model": model,
             "attempt": r["attempt"] if r else 1, "revealed": bool(r and r["revealed"])}
            for p, r in batch], ms


def run_batches(items, args):
    """Send (problem, retry) items to Claude in batches and append the programs to args.out."""
    batches = [items[i:i + args.batch] for i in range(0, len(items), args.batch)]
    print(f"{len(items)} problems in {len(batches)} batches", file=sys.stderr)
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    failed = 0
    with open(args.out, "a") as out, ThreadPoolExecutor(args.workers) as pool:
        futures = {pool.submit(generate_batch, b, args.model, args.timeout): b for b in batches}
        for n, fut in enumerate(as_completed(futures), 1):
            try:
                rows, ms = fut.result()
            except (RuntimeError, subprocess.TimeoutExpired, json.JSONDecodeError, KeyError) as error:
                failed += 1  # rerunning resumes the missing ones
                print(f"[{n}/{len(batches)}] FAILED: {error}", file=sys.stderr)
                continue
            out.writelines(json.dumps(r) + "\n" for r in rows)
            out.flush()
            print(f"[{n}/{len(batches)}] {len(rows)} programs in {ms / 1000:.0f} s", file=sys.stderr)
    sys.exit(1 if failed else 0)


def generate(args):
    problems = english(args.problems)
    topics = {t["id"]: t for t in read_jsonl(args.topics)}
    ids = sorted(i for i, t in topics.items()
                 if t["program_solvable"] and not t["needs_figure"]
                 and set(problems[i].get("options") or {}) == set(LETTERS))
    if args.limit:
        ids = ids[:: max(1, len(ids) // args.limit)][: args.limit]
    done = {r["id"] for r in read_jsonl(args.out)} if os.path.exists(args.out) else set()
    print(f"{len(ids)} candidates, {len(done)} done", file=sys.stderr)
    run_batches([(problems[i], None) for i in ids if i not in done], args)


def feedback(r, reveal, options):
    """What the retry is told about its last program. Only `reveal` gives the answer away."""
    last = f"Your previous solve() was wrong:\n{r['program']}\n"
    if r["status"] == "error":
        note = f"It failed with: {r['error']}"
    elif r["status"] == "no_match":
        note = f"It returned {r['value']!r}, which is none of the five options."
    elif r["status"] == "ambiguous":
        note = f"It returned {r['value']!r}, which matches more than one option."
    elif r["status"] == "constant":
        note = "It returned a constant. Compute the answer from the problem's data instead."
    else:  # wrong: rules one option out, still has to compute the answer
        note = f"It returned {r['value']!r}, option {r['letter']}, which is not the correct answer."
    if reveal:
        note += (f"\nThe correct answer is {r['label']}) {options[r['label']]}. Write a program that "
                 "computes it from the problem's data; do not return it as a constant.")
    return last + note + "\nWrite a new, correct solve()."


def retry(args):
    """Ask again, with feedback, for every training problem whose best program has not passed."""
    problems = english(args.problems)
    best = read_jsonl(args.verified)
    todo = []
    for r in best:
        if r["split"] != "train" or r["status"] == "correct" or r["attempt"] >= args.max_attempts:
            continue  # val is never retried: it would leak labels into the evaluation
        p = problems[r["id"]]
        todo.append((p, {"attempt": r["attempt"] + 1, "revealed": args.reveal,
                         "note": feedback(r, args.reveal, p["options"])}))
    print(f"retrying {len(todo)} training problems (attempt <= {args.max_attempts}, "
          f"reveal={args.reveal})", file=sys.stderr)
    run_batches(todo, args)


# ---------- verify ----------

def verify(args):
    problems = english(args.problems)
    rows = read_jsonl(args.programs)
    results = []
    with ThreadPoolExecutor(args.workers) as pool:
        runs = list(pool.map(lambda r: run_program(r["program"], args.seconds), rows))
    for r, (value, error) in zip(rows, runs):
        p = problems[r["id"]]
        hits = matches(value, p["options"]) if error is None else []
        status = ("error" if error else "no_match" if not hits else "ambiguous" if len(hits) > 1
                  else "wrong" if hits[0] != p["label"]
                  else "constant" if is_constant(r["program"])  # right, but not computed: unusable
                  else "correct")
        results.append({"id": r["id"], "split": p["split"], "level": p["level"], "label": p["label"],
                        "letter": hits[0] if len(hits) == 1 else None, "status": status,
                        "value": value, "error": error, "program": r["program"],
                        "program_chars": len(r["program"]), "attempt": r.get("attempt", 1),
                        "revealed": r.get("revealed", False)})
    attempts = collections.Counter(r["attempt"] for r in results)

    def rank(r):  # best first: passed without the answer, passed with it, then the latest failure
        return (r["status"] != "correct", r["revealed"], -r["attempt"] if r["status"] != "correct"
                else r["attempt"])
    best = {}
    for r in sorted(results, key=rank):
        best.setdefault(r["id"], r)
    results = sorted(best.values(), key=lambda r: r["id"])
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w") as f:
        f.writelines(json.dumps(r) + "\n" for r in results)

    print(f"{sum(attempts.values())} programs over attempts {dict(sorted(attempts.items()))}; "
          f"best per problem:")
    passed_at = collections.Counter((r["attempt"], r["revealed"]) for r in results
                                    if r["status"] == "correct")
    print("  passed at (attempt, revealed): " + ", ".join(
        f"{k}: {v}" for k, v in sorted(passed_at.items())))
    for name in ("train", "val"):
        part = [r for r in results if r["split"] == name]
        if not part:
            continue
        count = collections.Counter(r["status"] for r in part)
        n = len(part)
        print(f"{name}: {n} programs: "
              + ", ".join(f"{k} {v} ({v / n:.0%})" for k, v in count.most_common()))
        answered = count["correct"] + count["constant"] + count["wrong"]
        if answered:
            right = count["correct"] + count["constant"]
            print(f"  precision when it answers: {right}/{answered} = {right / answered:.0%}"
                  f" ({count['constant']} of the right ones only return a constant)")
    by_level = collections.defaultdict(collections.Counter)
    for r in results:
        by_level[r["level"]][r["status"] == "correct"] += 1
    print("correct by level: " + ", ".join(
        f"L{lv} {c[True]}/{c[True] + c[False]}" for lv, c in sorted(by_level.items())))
    ok = [r["program_chars"] for r in results if r["status"] == "correct"]
    if ok:
        print(f"verified program length: median {sorted(ok)[len(ok) // 2]} chars, max {max(ok)}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("generate")
    g.add_argument("--problems", nargs="+", required=True)
    g.add_argument("--topics", required=True, help="data/topics/topics.jsonl")
    g.add_argument("--out", required=True)
    g.add_argument("--model", default="sonnet")
    g.add_argument("--limit", type=int, default=0, help="an evenly spread sample of N candidates")
    g.add_argument("--batch", type=int, default=5)
    g.add_argument("--workers", type=int, default=4)
    g.add_argument("--timeout", type=int, default=600)
    g.set_defaults(fn=generate)
    t = sub.add_parser("retry", help="ask again, with feedback, for unverified training problems")
    t.add_argument("--problems", nargs="+", required=True)
    t.add_argument("--verified", required=True, help="output of verify")
    t.add_argument("--out", required=True, help="the programs file to append to")
    t.add_argument("--max-attempts", type=int, default=3)
    t.add_argument("--reveal", action="store_true",
                   help="tell Claude the correct option; rows are marked revealed")
    t.add_argument("--model", default="sonnet")
    t.add_argument("--batch", type=int, default=5)
    t.add_argument("--workers", type=int, default=4)
    t.add_argument("--timeout", type=int, default=600)
    t.set_defaults(fn=retry)
    v = sub.add_parser("verify")
    v.add_argument("--problems", nargs="+", required=True)
    v.add_argument("--programs", required=True)
    v.add_argument("--out", required=True)
    v.add_argument("--seconds", type=int, default=2, help="CPU limit per program")
    v.add_argument("--workers", type=int, default=8)
    v.set_defaults(fn=verify)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
