#!/usr/bin/env python3
"""Measure the copilot on M3Kang figure problems (text_only False) with the image.

Same loop, sample order and CSV columns as eval.py, plus has_image. The image of
each problem is read from the txto_no parquet written by laptop/split_text_only.py,
and sent to a llama-server started with --mmproj. Each answer is graded against the
problem's "label" column.

    python3 laptop/eval_vision.py --limit 5 --name smoke
    python3 laptop/eval_vision.py --limit 0 --name vision-img128

The per-row CSV and the line in results/ablations.csv stay out of Git (M3Kang rule).
"""
import argparse
import base64
import csv
import json
import os
import random
import statistics
import sys
import time
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from copilot.client import get  # noqa: E402
from copilot.config import CONFIG  # noqa: E402
from copilot.pipeline import solve  # noqa: E402
from eval import git_commit, table  # noqa: E402


def load_images(path, wanted):
    import pyarrow.parquet as pq

    t = pq.read_table(path, columns=["id", "language", "image"])
    images = {}
    for pid, lang, img in zip(*(t.column(c).to_pylist() for c in ("id", "language", "image"))):
        if (pid, lang) in wanted:
            images[(pid, lang)] = img["bytes"]
    return images


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--input", default="data/val.jsonl")
    p.add_argument("--parquet", default="data/raw_txto_no/high_quality-00000-of-00004.parquet")
    p.add_argument("--languages", default="eng,cat,esp")
    p.add_argument("--limit", type=int, default=0, help="0 means every problem")
    p.add_argument("--name", default="vision")
    p.add_argument("--time-limit", type=float, default=float(CONFIG["TIME_LIMIT_SECONDS"]))
    p.add_argument("--url", default=f"http://127.0.0.1:{CONFIG['VISION_PORT']}/v1/chat/completions")
    p.add_argument("--ids", help="JSON file with rows of {id, label}: keep only ids labelled 'logic'")
    p.add_argument("--no-image", action="store_true", help="blind run: same server, image not sent")
    args = p.parse_args()

    base = args.url.split("/v1/")[0]
    try:
        vision = get(base + "/props").get("modalities", {}).get("vision")
    except OSError as error:
        sys.exit(f"No server at {base}: {error}")
    if not vision:
        sys.exit(f"The server at {base} can't see images. Start it with --mmproj.")

    languages = set(filter(None, args.languages.split(",")))
    with open(args.input) as f:
        problems = [json.loads(line) for line in f if line.strip()]
    problems = [x for x in problems if not x["text_only"] and (not languages or x["language"] in languages)]
    if args.ids:
        with open(args.ids) as f:
            keep = {r["id"] for r in json.load(f)["rows"] if r["label"] == "logic"}
        problems = [x for x in problems if x["id"] in keep]
    random.Random(42).shuffle(problems)
    if args.limit:
        problems = problems[:args.limit]

    images = load_images(args.parquet, {(x["id"], x["language"]) for x in problems})
    missing = [x for x in problems if (x["id"], x["language"]) not in images]
    if missing:
        sys.exit(f"{len(missing)} problems have no image in {args.parquet}, e.g. {missing[0]['id']}")

    os.makedirs("results", exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    detail_path = f"results/eval-{stamp}-{args.name}.csv"
    rows = []
    with open(detail_path, "w", newline="") as out:
        writer = csv.writer(out)
        writer.writerow(["id", "language", "level", "has_options", "label", "answer",
                         "correct", "seconds", "status", "prompt_tokens", "retrieved", "has_image"])
        for n, problem in enumerate(problems, 1):
            b64 = None if args.no_image else base64.b64encode(images[(problem["id"], problem["language"])]).decode()
            result = solve(problem, image_b64=b64, llm_url=args.url, time_limit=args.time_limit)
            correct = result["answer"].strip().upper() == problem["label"].strip().upper()
            row = {**problem, **result, "correct": correct, "has_options": bool(problem.get("options"))}
            rows.append(row)
            writer.writerow([problem["id"], problem["language"], problem["level"], row["has_options"],
                             problem["label"], result["answer"], int(correct), result["seconds"],
                             result["status"], result["prompt_tokens"], result["retrieved"], int(b64 is not None)])
            out.flush()
            running = 100 * sum(r["correct"] for r in rows) / len(rows)
            print(f"[{n}/{len(problems)}] {result['answer']} (label {problem['label']}) "
                  f"{result['seconds']:.1f} s, {result['prompt_tokens']} tokens, "
                  f"running accuracy {running:.1f}%", flush=True)

    hits = [r["correct"] for r in rows]
    seconds = [r["seconds"] for r in rows]
    over = sum(s > float(CONFIG["TIME_LIMIT_SECONDS"]) for s in seconds)
    accuracy = 100 * sum(hits) / len(hits)
    truth = Counter(r["label"] for r in rows)
    best, count = truth.most_common(1)[0]

    print("\n" + "=" * 60)
    print(f"Accuracy against label: {sum(hits)}/{len(hits)} = {accuracy:.1f}%")
    print(f"  best one-letter floor (always {best}): {100 * count / len(rows):.1f}%   random guess: 20.0%")
    print(f"Latency: mean {statistics.mean(seconds):.1f} s, median {statistics.median(seconds):.1f} s, "
          f"worst {max(seconds):.1f} s, over {CONFIG['TIME_LIMIT_SECONDS']} s: {over}")
    print(f"Status: {dict(Counter(r['status'] for r in rows))}")
    for field, title in (("language", "By language"), ("level", "By level"),
                         ("has_options", "By whether OCR found the options")):
        groups = defaultdict(list)
        for r in rows:
            groups[r[field]].append(r["correct"])
        table(title, groups)
    predicted = Counter(r["answer"] for r in rows)
    print("\nLetters   " + "  ".join(f"{x}:{predicted[x]:>3}/{truth[x]:<3}" for x in "ABCDE"))

    log = "results/ablations.csv"
    new = not os.path.exists(log)
    with open(log, "a", newline="") as f:
        writer = csv.writer(f)
        if new:
            writer.writerow(["time", "name", "commit", "input", "languages", "n", "rag_k",
                             "accuracy", "mean_s", "worst_s", "over_limit"])
        writer.writerow([stamp, args.name, git_commit(),
                         args.input + (" (figure, blind)" if args.no_image else " (figure, image)"),
                         args.languages or "all", len(rows), 0, f"{accuracy:.1f}",
                         f"{statistics.mean(seconds):.1f}", f"{max(seconds):.1f}", over])
    print(f"\nDetails: {detail_path}\nAblation log: {log}")


if __name__ == "__main__":
    main()
