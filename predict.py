#!/usr/bin/env python3
"""Official entry point: answer every problem with one letter, A to E.

    python3 predict.py --input problems.jsonl --output predictions.csv
    python3 predict.py --input problems.jsonl --output predictions.csv --rag 1

Input: the organizers' parquet (with the image column), or one JSON object per line with
at least "id" and "text", plus "options" ({"A": ..., "E": ...}) and "language" when
available. A JSONL problem's image is <images>/<id>_<language>.png (default: the "images"
folder next to the input). With an image, the board reads the options itself
(copilot/options_ocr.py).
Output: a CSV with id, language, answer, seconds, status.

Rules: runs offline, at most 60 seconds per problem, deterministic.
"""
import argparse
import csv
import sys

from copilot.pipeline import solve
from copilot.problems import load


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--rag", type=int, default=0, metavar="K", help="add K similar solved problems")
    p.add_argument("--index", default="data/index.db")
    p.add_argument("--images", default=None, help="folder of <id>_<language>.png images")
    args = p.parse_args()

    index = None
    if args.rag:
        from copilot import rag
        problem = rag.check(args.index)
        if problem:
            sys.exit(problem)
        index = rag.Index(args.index)

    problems = load(args.input, args.images)

    with open(args.output, "w", newline="") as out:
        writer = csv.writer(out)
        writer.writerow(["id", "language", "answer", "seconds", "status"])
        for n, problem in enumerate(problems, 1):
            result = solve(problem, index=index, k=args.rag)
            writer.writerow([problem["id"], problem.get("language", ""), result["answer"],
                             result["seconds"], result["status"]])
            out.flush()
            print(f"[{n}/{len(problems)}] {problem['id']} -> {result['answer']} "
                  f"in {result['seconds']:.1f} s ({result['status']})", file=sys.stderr)


if __name__ == "__main__":
    main()
