"""Export what the tutor memory needs (copilot/tutor_memory.py) from the generated data.

    uv run python laptop/export_tutor_memory.py
    -> data/processed/tutor_memory/problems.jsonl     solved problems with hints and solution (T4)
       data/processed/tutor_memory/messages.jsonl     labelled student messages, the classifier's examples
       data/processed/tutor_memory/heldout.jsonl      labelled messages of other problems, to measure it
    (gitignored: derived from M3Kang). Copy the folder to the board and run build_tutor_memory.py.

Message labels come from the dialogue item the message belongs to (generate_dialogues.py):
    diagnostic student -> stuck          error attempt -> attempt          concept -> concept
    free -> step_question              manipulation -> manipulation     (retries in error dialogues are left out: half-attempts)
plus short written examples for what the dialogues do not contain: asking for a hint, asking for the
solution, and off-topic or noise messages.
"""
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from laptop.build_tutor_sft import ASK_SOLUTION, HINT_FIRST, HINT_MORE  # noqa: E402

EXPL = Path("data/processed/explanations")
DIAL = Path("data/processed/dialogues")
OUT = Path("data/processed/tutor_memory")
PER_LABEL = 700      # classifier examples per label kept for the board (search is pure Python)
SEED = 42
NON_LATIN = re.compile(r"[Ѐ-ӿ؀-ۿ　-鿿가-힯]")

WRITTEN = {
    "asks_hint": HINT_FIRST + HINT_MORE + [
        "hint pls", "can i have a clue", "give me a hint but dont tell me", "help me a little bit",
        "another clue?", "one more hint please", "a small hint?", "can u give me a tip",
        "i need a hint", "hint?", "what should i do first, just a hint", "more help pls",
        "pista please", "can you help me without saying the answer", "give me a nudge"],
    "asks_solution": ASK_SOLUTION + [
        "just show me how to do it", "explain the whole thing", "i give up, show me",
        "solve it pls", "how do you solve this one", "can you do it step by step for me",
        "show the answer and explain", "whats the solution", "tell me how to get the answer, i quit",
        "i want to see the full solution", "can you walk me through all of it", "do it for me please"],
    "off_topic": [
        "do you like football", "whats your name", "im hungry", "lol", "asdfgh", "ok", "hmmm",
        "who made you", "can we play a game", "tell me a joke", "what time is it", "i like pizza",
        "are you a robot", "my friend is annoying", "is it going to rain", "bored", "...", "hello",
        "what's the weather today", "do you have a pet", "can i go to the toilet", "jajaja",
        "this is boring can we stop", "what music do you like", "123 test"],
}


def load(path):
    return [json.loads(line) for line in open(path, encoding="utf-8")] if Path(path).exists() else []


def main():
    rng = random.Random(SEED)
    rows = load(EXPL / "sft" / "combined.jsonl")
    raw = {}
    for path in (EXPL / "raw").glob("*.jsonl"):
        for r in load(path):
            if r.get("output"):
                raw[(r["id"], r["language"], path.stem)] = r
    hints = {}
    for r in rows:
        if r["task"] == "hint":
            hints.setdefault(r["id"], {})[r["hint_level"]] = r["messages"][-1]["content"]

    problems = []
    for r in rows:
        if r["task"] != "solution":
            continue
        rec = raw.get((r["id"], r["language"], r["teacher"]))
        o = rec["output"] if rec else {}
        problems.append({"id": r["id"], "level": r["level"], "language": r["language"],
                         "topic": o.get("topic", ""), "key_idea": o.get("key_idea", ""),
                         "problem": r["messages"][1]["content"],
                         "hints": [h for _, h in sorted(hints.get(r["id"], {}).items())],
                         "solution": r["messages"][2]["content"]})

    # Held-out problems for measuring the classifier: the same validation ids as the fine-tune.
    val_ids = set((Path("data/processed/tutor_sft") / "val_ids.txt").read_text().split())
    verdicts = {r["id"]: {v.get("n"): v for v in r["output"].get("items", [])}
                for r in load(DIAL / "judge" / "deepseek-v4-flash.jsonl") if r.get("output")}
    from santolina_tutor.generate_dialogues import items  # flattening shared with the judge

    kind_label = {"diagnostic": "stuck", "concept": "concept", "error_question": "attempt",
                  "free": "step_question",  # retries inside error dialogues are half-attempts: left out
                  "manipulation": "manipulation"}
    found = []
    for g in load(DIAL / "raw" / "glm5.3-flash.jsonl"):
        if not g.get("output"):
            continue
        v = verdicts.get(g["id"], {})
        for n, (kind, student, _tutor) in enumerate(items(g["output"]), 1):
            if kind not in kind_label or not isinstance(student, str) or not student.strip():
                continue
            if v.get(n, {}).get("student_ok") is False or NON_LATIN.search(student):
                continue
            found.append({"text": student.strip(), "label": kind_label[kind], "id": g["id"]})

    written = [{"text": t, "label": lab, "id": f"written-{i}"} for lab, ts in WRITTEN.items() for i, t in enumerate(ts)]
    rng.shuffle(written)
    # Written examples: 80% to the store, 20% held out (they have no problem id to split on).
    cut = int(len(written) * 0.8)
    store_pool = [m for m in found if m["id"] not in val_ids] + written[:cut]
    heldout = [m for m in found if m["id"] in val_ids] + written[cut:]

    by_label = {}
    for m in store_pool:
        by_label.setdefault(m["label"], []).append(m)
    messages = []
    for lab, ms in by_label.items():
        rng.shuffle(ms)
        messages += ms[:PER_LABEL]

    OUT.mkdir(parents=True, exist_ok=True)
    for name, part in (("problems", problems), ("messages", messages), ("heldout", heldout)):
        with open(OUT / f"{name}.jsonl", "w", encoding="utf-8") as f:
            f.writelines(json.dumps(x, ensure_ascii=False) + "\n" for x in part)
    print(f"problems {len(problems)}; messages {len(messages)} {dict(Counter(m['label'] for m in messages))}; "
          f"heldout {len(heldout)} {dict(Counter(m['label'] for m in heldout))}")


if __name__ == "__main__":
    main()
