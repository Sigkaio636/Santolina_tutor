"""Build the fine-tuning set for the local tutor.

Setting: the teacher enters a problem and its correct answer. The model (1) prepares a ladder of
hints plus the full solution, then (2) chats with the student. Every example has a "task" and a
loss "weight"; the training loss is computed on the last assistant message only (one row per
tutor reply: Qwen3.5's template renders past assistant turns differently from a fresh reply, so
packing several replies into one row would not match what the board sends).

Sources:
    data/processed/explanations/sft/combined.jsonl + raw/   hints, solutions (one teacher per problem)
    data/processed/dialogues/raw/ + judge/                  generated dialogues (generate_dialogues.py)

    uv run python laptop/build_tutor_sft.py                   # dialogue items need a judge "pass"
    uv run python laptop/build_tutor_sft.py --allow-unjudged  # code filters only where not judged yet
    -> data/processed/tutor_sft/{train,val}.jsonl, val_ids.txt, stats.json, train_tutor.py
       (gitignored: derived from M3Kang)

Tasks (types from docs/TUTOR_RESPONSE_TYPES.md; weights in WEIGHTS):
    prepare        problem + key -> all hints + solution (+ a T8 follow-up question), format_prepared()
    hint           T1-T5b ladder: hint k after hints 1..k-1
    solution       T7: asked for the solution (sometimes after hints); ends with a T8 question
    check_right    T6 counterpart: the student proposes the correct option -> confirm and justify
    key_idea       T5b: "what is the main idea?"
    diagnostic     T0c/d/e: vague message -> one problem-specific question        (generated)
    concept        T5a: "what is X?" -> definition, other example, question       (generated)
    error_question / error_pointer / correction                                    (generated)
                   T6 in three stages; a stage is only kept if all three passed
    free           specific question about a step -> short grounded answer       (generated)
    manipulation   T9d: "just tell me the letter" -> kind refusal, back to work   (generated)
    solve_nokey    no key given, the model solves (keeps that ability; not the tutor's job)
"""
import json
import random
import shutil
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from copilot.tutor_prompt import PREPARE_REQUEST, format_prepared, tutor_system  # noqa: E402
from santolina_tutor.generate_dialogues import code_checks, items  # noqa: E402

EXPL = Path("data/processed/explanations")
DIAL = Path("data/processed/dialogues")
SRC = EXPL / "sft" / "combined.jsonl"
OUT = Path("data/processed/tutor_sft")
GEN_MODEL, JUDGE_MODEL = "glm5.3-flash", "deepseek-v4-flash"
VAL_FRACTION, SEED = 0.1, 42

# Per-example loss weights. The loss is a per-example mean over target tokens, so a 1-line reply
# counts as much as a 20-line solution; the weights then set how much each task matters.
WEIGHTS = {
    "prepare": 1.0,         # the core job, run once when the teacher enters a problem
    "error_question": 1.0,  # the most common live situation, and the easiest place to leak
    "free": 1.0,            # the "custom clue" the setting asks for
    "diagnostic": 0.8,
    "concept": 0.8,
    "error_pointer": 0.8,
    "correction": 0.8,
    "hint": 0.6,            # same text as in prepare; the live fallback
    "solution": 0.6,        # same text as in prepare
    "manipulation": 0.5,    # short and repetitive
    "check_right": 0.5,
    "key_idea": 0.4,
    "solve_nokey": 0.3,     # keeps the no-key solver alive; not the tutor's job
}
# Generated items used per problem: one row each costs the whole problem again as context, so
# this is the main knob on training time. None = all that passed.
PER_PROBLEM = {"diagnostic": 1, "concept": 1, "error": 1, "free": 2, "manipulation": 1}
NOTES_PROB = 0.5            # share of problems where the teacher also typed a short justification
# --lean: fewer rows for a shorter training run. Cuts what is least useful first: solve_nokey (the
# scored test asks for one letter, not steps), hint rows beyond the first two levels (same text is
# in prepare), half of check_right / key_idea, and one free question instead of two.
LEAN = {"drop": {"solve_nokey"}, "max_hint_level": 2, "keep_share": {"check_right": 0.5, "key_idea": 0.5},
        "per_problem": {"free": 1}}

HINT_FIRST = ["Can you give me a hint, without telling me the answer?", "I don't know where to start. Can you give me a hint?",
              "Give me a clue, please.", "Can you help me get started?", "Hint please, but don't tell me the answer."]
HINT_MORE = ["I'm still stuck. Can you give me another hint?", "Another hint, please.", "Still not sure. One more clue?",
             "That helps a bit, but I need another hint.", "Can you give me a more concrete hint?"]
ASK_SOLUTION = ["Show me the full solution, please.", "I give up. Can you explain the solution step by step?",
                "Can you solve it for me and explain every step?", "Please show me how to solve it."]
CHECK = ["I think the answer is {o}. Is that right?", "I got {o}. Am I right?", "Is it {o}?",
         "My answer is {o}. Is it correct?", "I chose {o}. Can you check it?"]
KEY_IDEA = ["What is the main idea I need for this problem?", "What is the trick in this problem?",
            "Which idea unlocks this problem?"]
T8_FALLBACK = "Can you explain in your own words why this answer is right?"


def load(path):
    return [json.loads(line) for line in open(path, encoding="utf-8")] if Path(path).exists() else []


def option(letter, options):
    return f"{letter}) {options[letter]}" if letter in options else letter


def passed_items(gen, verdicts, label, answer_text, allow_unjudged):
    """Generated items that pass the code filters and the judge, grouped by kind. An error
    dialogue is kept only when all three of its stages pass."""
    if verdicts is None and not allow_unjudged:
        return {}
    flat = items(gen)
    ok = []
    for n, (kind, s, t) in enumerate(flat, 1):
        v = (verdicts or {}).get(n)
        judged_ok = v is None if verdicts is None else (v and v.get("pass") is True and v.get("student_ok", True) is not False)
        ok.append(not code_checks(kind, s, t, label, answer_text) and bool(judged_ok))
    out = {}
    i = 0
    while i < len(flat):
        kind, s, t = flat[i]
        if kind == "error_question":
            if all(ok[i:i + 3]):
                out.setdefault("error", []).append(flat[i:i + 3])
            i += 3
            continue
        if ok[i]:
            out.setdefault(kind, []).append((s, t))
        i += 1
    return out


def examples_for(sol_row, hint_rows, raw, dialogue, rng):
    out = []
    o = raw["output"]
    label, options = raw["label"], o.get("options") or {}
    problem = sol_row["messages"][1]["content"]
    hints = [r["messages"][-1]["content"] for r in sorted(hint_rows, key=lambda r: r["hint_level"])]
    notes = o.get("answer_justification", "") if rng.random() < NOTES_PROB else ""
    system = {"role": "system", "content": tutor_system(problem, label, str(options.get(label, "")), notes)}
    meta = {k: sol_row[k] for k in ("id", "language", "level", "teacher")}

    def add(task, messages, **extra):
        out.append({"task": task, "weight": WEIGHTS[task], **meta, **extra, "messages": [system, *messages]})

    def u(text):
        return {"role": "user", "content": text}

    def a(text):
        return {"role": "assistant", "content": text}

    # The solution ends with a T8 question (doc: never end on the letter alone).
    t8 = [t for _, t in dialogue.get("after_solution", [])]
    solution = f"{sol_row['messages'][2]['content']}\n\n{rng.choice(t8) if t8 else T8_FALLBACK}"

    add("prepare", [u(PREPARE_REQUEST), a(format_prepared(hints, solution))])

    history = []
    for k, h in enumerate(hints):
        history.append(u(rng.choice(HINT_FIRST if k == 0 else HINT_MORE)))
        add("hint", [*history, a(h)], hint_level=k + 1)
        history.append(a(h))

    n_before = rng.choice([0, 0, 1, 2]) if hints else 0  # sometimes the student asks after some hints
    add("solution", [*history[: 2 * min(n_before, len(hints))], u(rng.choice(ASK_SOLUTION)), a(solution)])

    just = o.get("answer_justification", "").strip()
    if just:
        add("check_right", [u(rng.choice(CHECK).format(o=option(label, options))),
                            a(f"Yes, {option(label, options)} is correct! {just}")])
    if o.get("key_idea"):
        add("key_idea", [u(rng.choice(KEY_IDEA)), a(o["key_idea"].strip())])

    def pick(kind):
        got = dialogue.get(kind, [])
        k = PER_PROBLEM.get(kind)
        return got if k is None else rng.sample(got, min(k, len(got)))

    for kind in ("diagnostic", "concept", "free", "manipulation"):
        for s, t in pick(kind):
            add(kind, [u(s), a(t)])
    for (_, s1, t1), (_, s2, t2), (_, s3, t3) in pick("error"):
        add("error_question", [u(s1), a(t1)])
        add("error_pointer", [u(s1), a(t1), u(s2), a(t2)])
        add("correction", [u(s1), a(t1), u(s2), a(t2), u(s3), a(t3)])

    out.append({"task": "solve_nokey", "weight": WEIGHTS["solve_nokey"], **meta, "messages": sol_row["messages"]})
    return out


def main(allow_unjudged=False, lean=False, sample=1.0, out=OUT):
    """sample < 1 keeps that random share of the rows (train and val): a shorter training run that
    still sees every task and many different problems."""
    if lean:
        PER_PROBLEM.update(LEAN["per_problem"])
    rows = load(SRC)
    raw = {}
    for path in (EXPL / "raw").glob("*.jsonl"):
        for r in load(path):
            if r.get("output"):
                raw[(r["id"], r["language"], path.stem)] = r  # latest record wins, as in read_raw()
    gens = {r["id"]: r["output"] for r in load(DIAL / "raw" / f"{GEN_MODEL}.jsonl") if r.get("output")}
    verdicts = {r["id"]: {v.get("n"): v for v in r["output"].get("items", [])}
                for r in load(DIAL / "judge" / f"{JUDGE_MODEL}.jsonl") if r.get("output")}
    by_problem = {}
    for r in rows:
        by_problem.setdefault((r["id"], r["language"]), []).append(r)

    ids = sorted({r["id"] for r in rows})
    random.Random(SEED).shuffle(ids)  # split by problem id, so val problems never appear in train
    val_ids = set(ids[: int(len(ids) * VAL_FRACTION)])

    rng = random.Random(SEED)
    train, val, skipped = [], [], 0
    coverage = Counter()
    for (pid, lang), group in by_problem.items():
        sol = next((r for r in group if r["task"] == "solution"), None)
        teacher = sol["teacher"] if sol else None
        rec = raw.get((pid, lang, teacher))
        if not sol or not rec or rec["label"] not in (rec["output"].get("options") or {}):
            skipped += 1
            continue
        label = rec["label"]
        dialogue = {}
        if pid in gens:
            dialogue = passed_items(gens[pid], verdicts.get(pid), label, str(rec["output"]["options"][label]), allow_unjudged)
            coverage["judged" if pid in verdicts else ("unjudged, code filters only" if allow_unjudged else "unjudged, skipped")] += 1
        else:
            coverage["no dialogues"] += 1
        exs = examples_for(sol, [r for r in group if r["task"] == "hint"], rec, dialogue, rng)
        if lean:
            exs = [e for e in exs if e["task"] not in LEAN["drop"]
                   and e.get("hint_level", 0) <= LEAN["max_hint_level"]
                   and rng.random() < LEAN["keep_share"].get(e["task"], 1.0)]
        (val if pid in val_ids else train).extend(exs)

    if sample < 1.0:
        train = [e for e in train if rng.random() < sample]
        val = [e for e in val if rng.random() < sample]
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    for name, part in (("train", train), ("val", val)):
        rng.shuffle(part)
        with open(out / f"{name}.jsonl", "w", encoding="utf-8") as f:
            f.writelines(json.dumps(e, ensure_ascii=False) + "\n" for e in part)
    (out / "val_ids.txt").write_text("\n".join(sorted(val_ids)) + "\n")
    stats = {"train": dict(Counter(e["task"] for e in train)), "val": dict(Counter(e["task"] for e in val)),
             "dialogue_coverage": dict(coverage), "skipped_problems": skipped,
             "weights": WEIGHTS, "per_problem": PER_PROBLEM, "lean": lean, "sample": sample}
    (out / "stats.json").write_text(json.dumps(stats, indent=1))
    # Make the folder a ready-to-upload (PRIVATE) Kaggle dataset: data + training script.
    shutil.copy(ROOT / "kaggle" / "train_tutor.py", out / "train_tutor.py")
    print(json.dumps(stats, indent=1))
    print(f"Upload {out}/ as a PRIVATE Kaggle dataset, then run kaggle/tutor_finetune.ipynb")


if __name__ == "__main__":
    def arg(name, default):
        return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default

    main(allow_unjudged="--allow-unjudged" in sys.argv, lean="--lean" in sys.argv,
         sample=float(arg("--sample", 1.0)), out=arg("--out", OUT))
