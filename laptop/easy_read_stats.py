"""Readability numbers for easy read, before and after, over a local problems file.

It prints numbers only, never problem text:

    python3 laptop/easy_read_stats.py data/val.jsonl

"Before" is the text as written (its own line breaks). "After" is the easy-read layout.
A long word has 7 letters or more.
"""

import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from student_app.easy_read import easy_read, sentences

LONG = 7


def lines_of(text: str) -> list:
    return [line for line in text.splitlines() if line.strip()]


def measure(texts: list) -> dict:
    lines = [line for text in texts for line in lines_of(text)]
    words = [re.findall(r"\w+", line) for line in lines]
    return {
        "lines per problem": len(lines) / len(texts),
        "words per line": sum(len(w) for w in words) / len(lines),
        "longest line (words)": max(len(w) for w in words),
        "long words per line": sum(len(x) >= LONG for w in words for x in w) / len(lines),
    }


def main(path: str) -> None:
    rows = [
        json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line
    ]
    for language in ("cat", "eng"):
        before = [r["text"] for r in rows if r.get("language") == language and r.get("text")]
        if not before:
            continue
        after = [easy_read(t) for t in before]
        changed = sum(a != b for a, b in zip(after, before, strict=True))
        moved = sum(_question_moves(t) for t in before)
        print(
            f"{language}: {len(before)} problems, {changed} changed, {moved} with the question moved"
        )
        m_before, m_after = measure(before), measure(after)
        for key in m_before:
            print(f"  {key:22} {m_before[key]:6.1f} -> {m_after[key]:6.1f}")


def _question_moves(text: str) -> bool:
    parts = sentences(text) or []
    questions = [k for k, part in enumerate(parts) if part.endswith("?")]
    return bool(questions) and questions[-1] != len(parts) - 1


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/val.jsonl")
