#!/usr/bin/env python3
"""Build data/tutor_memory.db for copilot/tutor_memory.py, and measure the message classifier.

    python3 build_tutor_memory.py                    # data/tutor_memory/*.jsonl -> data/tutor_memory.db
    python3 build_tutor_memory.py --eval             # also: accuracy on the held-out messages
    python3 build_tutor_memory.py --try "idk help"   # classify one message and exit

Needs the embedding server (port EMBED_PORT). Run it on the board after copying
data/processed/tutor_memory/ from the laptop to data/tutor_memory/ there.
"""
import argparse
import json
import os
import time
from collections import Counter, defaultdict

from copilot import tutor_memory


def load(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--src", default="data/tutor_memory")
    p.add_argument("--db", default="data/tutor_memory.db")
    p.add_argument("--eval", action="store_true", help="measure the classifier on heldout.jsonl")
    p.add_argument("--try", dest="message", help="classify one message with the existing db")
    args = p.parse_args()

    if args.message is None:
        problems, messages = load(os.path.join(args.src, "problems.jsonl")), load(os.path.join(args.src, "messages.jsonl"))
        if os.path.exists(args.db):
            os.remove(args.db)  # rebuild from scratch: no stale rows from an older export
        start = time.time()
        for done in tutor_memory.build(args.db, problems, messages):
            print(f"\r{done}/{len(problems) + len(messages)} embedded", end="", flush=True)
        print(f"\nbuilt {args.db}: {len(problems)} problems, {len(messages)} messages in {time.time() - start:.0f} s")

    memory = tutor_memory.TutorMemory(args.db)
    if args.message is not None:
        start = time.time()
        label, conf, doc = memory.classify_message(args.message)
        print(f"{label} ({doc}), confidence {conf:.2f}, {time.time() - start:.2f} s")
        return
    if args.eval:
        heldout = load(os.path.join(args.src, "heldout.jsonl"))
        confusion = defaultdict(Counter)
        start = time.time()
        for m in heldout:
            confusion[m["label"]][memory.classify_message(m["text"])[0]] += 1
        right = sum(c[lab] for lab, c in confusion.items())
        doc = tutor_memory.DOC_LABEL
        right_doc = sum(n for lab, c in confusion.items() for got, n in c.items() if doc.get(got) == doc.get(lab))
        print(f"accuracy {right}/{len(heldout)} = {right / len(heldout):.1%}; on the doc's 5 decider labels "
              f"{right_doc / len(heldout):.1%}  ({(time.time() - start) / len(heldout):.3f} s per message)")
        for lab in sorted(confusion):
            c = confusion[lab]
            print(f"  {lab:14} recall {c[lab] / sum(c.values()):.0%} of {sum(c.values()):4}   "
                  f"most confused with: {[(k, v) for k, v in c.most_common(3) if k != lab][:2]}")


if __name__ == "__main__":
    main()
