"""Build the head-B dataset: problem + options -> a verified solve() program.

Training: every training problem whose best program passed without the answer
being revealed, in each language (eng, cat, esp). The program doesn't depend on
the language, but the OCR options do, so it is re-matched against each language's
options and kept only where it lands on the label.

Validation: every val candidate in each language, with its options and label but
no program. The fine-tuned model writes the program; the Kaggle script runs it.

The prompt is copilot/program_head.py's build_messages, the one the board uses,
and that file is copied next to the data so the Kaggle script can import it.

    uv run python -m santolina_tutor.finetune.program_data \
        --problems data/train.jsonl data/val.jsonl \
        --verified data/programs/verified.jsonl --topics data/topics/topics.jsonl \
        --out data/finetune/programs

Each row also carries text, options and topic, so the Kaggle script can embed
the problems and pick a similar solved problem (retrieval-augmented head B).

Output is derived from M3Kang (research use only): it stays under data/.
"""
import argparse
import collections
import json
import os
import shutil

from copilot import program_head
from copilot.program_head import build_messages, matches, run_program

LETTERS = "ABCDE"


def read_jsonl(path):
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--problems", nargs="+", required=True)
    ap.add_argument("--verified", required=True, help="output of programs.py verify")
    ap.add_argument("--topics", help="topics.py output, adds a topic to every row")
    ap.add_argument("--out", required=True)
    ap.add_argument("--languages", default="eng,cat,esp")
    ap.add_argument("--with-revealed", action="store_true",
                    help="also train on programs written after the answer was revealed")
    args = ap.parse_args()

    langs = set(args.languages.split(","))
    versions = collections.defaultdict(list)  # id -> the problem in each language
    for path in args.problems:
        for p in read_jsonl(path):
            if p["language"] in langs and set(p.get("options") or {}) == set(LETTERS):
                versions[p["id"]].append(p)
    verified = read_jsonl(args.verified)
    topic = {t["id"]: t["topic"] for t in read_jsonl(args.topics)} if args.topics else {}

    def row(p, **extra):
        return {"id": p["id"], "language": p["language"], "level": p["level"],
                "topic": topic.get(p["id"]), "text": p["text"], "options": p["options"],
                "messages": build_messages(p), **extra}

    train, val, dropped = [], [], collections.Counter()
    for r in verified:
        if r["split"] == "val":
            val += [row(p, label=p["label"]) for p in versions[r["id"]]]
            continue
        if r["status"] != "correct" or (r["revealed"] and not args.with_revealed):
            continue
        value, error = run_program(r["program"])
        for p in versions[r["id"]]:
            hits = matches(value, p["options"]) if error is None else []
            if hits != [p["label"]]:
                dropped[p["language"]] += 1  # this language's OCR options disagree
                continue
            train.append(row(p, label=p["label"], program=r["program"]))

    os.makedirs(args.out, exist_ok=True)
    for name, rows in (("train", train), ("val", val)):
        with open(os.path.join(args.out, f"{name}.jsonl"), "w") as f:
            f.writelines(json.dumps(x, ensure_ascii=False) + "\n" for x in rows)
        print(f"{name}: {len(rows)} rows from {len({x['id'] for x in rows})} problems, "
              f"languages {dict(collections.Counter(x['language'] for x in rows))}")
    print(f"dropped (program no longer matches that language's options): {dict(dropped)}")
    shutil.copy(program_head.__file__, os.path.join(args.out, "program_head.py"))


if __name__ == "__main__":
    main()
