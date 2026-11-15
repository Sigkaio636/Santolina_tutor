"""The real tutor behind the student app: drop-in replacement for the stub student_app/tutor.py.

Same interface (student_app/state.py calls these from a background queue, so slow is fine):
    Tutor(catalog)
    clue(context, exercise, number) -> str          the "clue" button
    solution(context, exercise, answer) -> str      the "solution" button
    reply(context, message, photo) -> {"text", "suggestions"}   a typed message
context = {"mode", "language", "exercise": catalog.public(item, with_answer=True) or None,
           "history": [(role, text)], role "student" or "copilot"}.

What it uses:
    D  the fine-tuned tutor model (qwen35-tutor-Q8_0.gguf) on llama-server, port TUTOR_PORT.
       Prompts come from copilot/tutor_prompt.py, the format it was trained on.
    E  copilot/tutor_memory.py: classify_message() routes a typed message, similar_problem()
       offers an easier solved problem when the hints run out.

Hints and the solution are written once per exercise by the "prepare" request and kept in
data/tutor_cache.json, so the buttons answer at once. Prepare them before class:
    python3 -m copilot.tutor_backend --warm        # every exercise of the board's catalog
    python3 -m copilot.tutor_backend --demo        # a made-up exercise, end to end

Start the model (same flags as the other services; --jinja --reasoning off is required, it was
trained without thinking; Qwen3.5 is a hybrid model, so --ctx-checkpoints keeps the prompt cache):
    llama-server -m ~/models/qwen35-tutor-Q8_0.gguf --host 127.0.0.1 --port 8084 --ctx-size 4096 \\
        --threads 4 --parallel 1 --jinja --reasoning off --ctx-checkpoints 8

Standard library only. If the model or the memory is missing, the tutor still answers with
safe fixed sentences instead of failing.
"""
import hashlib
import json
import os
import random
import re
import sys
import threading

from .client import post
from .config import CONFIG, ROOT
from .tutor_memory import TutorMemory, rule_label
from .tutor_prompt import PREPARE_REQUEST, parse_prepared, tutor_system

URL = f"http://127.0.0.1:{CONFIG.get('TUTOR_PORT', '8084')}/v1/chat/completions"
MEMORY_DB = os.path.join(ROOT, CONFIG.get("TUTOR_MEMORY_DB", "data/tutor_memory.db"))
CACHE_PATH = os.path.join(ROOT, CONFIG.get("TUTOR_CACHE", "data/tutor_cache.json"))
TIMEOUT = float(CONFIG.get("TUTOR_TIMEOUT", "300"))  # seconds per model call (board: ~5 tok/s)
SIMILAR_MIN = 0.75  # below this, the "similar" problem is not similar enough to offer

# The student turns the model saw in training (laptop/build_tutor_sft.py), first variant of each.
HINT_FIRST = "Can you give me a hint, without telling me the answer?"
HINT_MORE = "I'm still stuck. Can you give me another hint?"
ASK_SOLUTION = "Show me the full solution, please."

TEMPLATES = {
    "manipulation": ["I can't give you the answer, but I can help you find it. What have you tried so far?",
                     "Let's get there together instead. Which part of the problem is unclear?"],
    "off_topic": ["Let's keep that for later. Back to the problem: what does it ask you to find?",
                  "I didn't quite get that. Can you write your question about the problem again?"],
    "no_exercise": ["Pick an exercise and I'll help you with it, step by step.",
                    "Open an exercise first, then ask me anything about it."],
    "asks_solution": ["Have a go first: after your first answer, tap 'Solution' and I'll explain every step."],
    "correct": ["Yes, that's right! Can you explain in one sentence why it works?",
                "Correct! How would you check your answer?"],
    "safe_question": ["What have you tried so far?", "Which part of the problem are you stuck on?"],
    "no_more_hints": ["That was the last hint. Try once more, and if you are still stuck, ask for the solution."],
    "offline": ["The tutor is not available right now. Try the clue button, or ask again in a moment."],
}


def _say(kind, rng=random):
    return rng.choice(TEMPLATES[kind])


def problem_text(ex):
    """The problem as the model saw it in training: statement, then the options one per line."""
    statement = re.sub(r"^\s*\d+\s*[.)]\s*", "", (ex.get("prompt") or "").strip())
    options = ex.get("options") or {}
    lines = "\n".join(f"{k}) {options[k]}" for k in sorted(options))
    return "\n\n".join(p for p in (statement, lines) if p)


def answer_parts(ex):
    answer = str(ex.get("answer") or "").strip()
    options = ex.get("options") or {}
    return answer, str(options.get(answer, ""))


def leaks(text, ex):
    """True if a reply given before the solution names the correct option or its value."""
    label, value = answer_parts(ex)
    if not label:
        return False
    if len(label) == 1 and re.search(rf"\b(?:option|answer|choice)\s*\(?{label}\b|\({label}\)|(?:^|\s){label}\)", text, re.I):
        return True
    target = value or (label if len(label) > 1 or label.isdigit() else "")
    if target and len(target) <= 25:
        pattern = re.escape(target)
        if len(target) <= 2:  # short values ("1", "12"): only in an answer-like context
            pattern = rf"(?:answer|result|it'?s|is|=|equals|get|gives)\s+{pattern}(?!\w|[.,]\d)"
        else:
            pattern = rf"(?<![\w.]){pattern}(?!\w|[.,]\d)"
        return bool(re.search(pattern, text, re.I))
    return False


def proposed_option(message, ex):
    """The option a student proposes ("is it B", "i got 24"), or None."""
    options = ex.get("options") or {}
    m = re.search(r"(?:^|[\s(])([A-E])(?:\)|\b)(?![a-z])", message)
    if m and m.group(1) in options:
        return m.group(1)
    for letter, value in options.items():
        if str(value).strip() and re.search(rf"(?<![\w.]){re.escape(str(value).strip())}(?!\w|[.,]\d)", message):
            return letter
    return None


def _chat(messages, max_tokens):
    response = post(URL, {"messages": messages, "max_tokens": max_tokens, "temperature": 0.2,
                          "cache_prompt": True}, timeout=TIMEOUT)
    text = response["choices"][0]["message"]["content"] or ""
    return re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()


class Tutor:
    def __init__(self, catalog=None):
        self.catalog = catalog
        self.lock = threading.Lock()
        self.rng = random.Random(42)
        try:
            self.memory = TutorMemory(MEMORY_DB)
        except (FileNotFoundError, OSError) as error:
            print(f"tutor: no memory ({error}); messages are routed by keyword rules only", file=sys.stderr)
            self.memory = None
        try:
            with open(CACHE_PATH, encoding="utf-8") as f:
                self.cache = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.cache = {}

    # ------------------------------------------------------------------ helpers
    def _system(self, ex):
        label, value = answer_parts(ex)
        return {"role": "system", "content": tutor_system(problem_text(ex), label, value)}

    @staticmethod
    def _fingerprint(ex):
        raw = json.dumps([ex.get("prompt"), ex.get("options"), ex.get("answer")], sort_keys=True, ensure_ascii=False)
        return hashlib.sha1(raw.encode()).hexdigest()[:16]

    @staticmethod
    def _history(context):
        role = {"student": "user", "copilot": "assistant"}
        turns = [{"role": role[r], "content": t} for r, t in context.get("history") or [] if r in role and t]
        while turns and turns[0]["role"] != "user":  # a chat must start with the student
            turns.pop(0)
        return turns

    def _save(self):
        os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
        tmp = CACHE_PATH + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=1)
        os.replace(tmp, CACHE_PATH)

    def prepared(self, ex, generate=True):
        """{"hints": [...], "solution": str} for an exercise, from the cache or written now."""
        key = self._fingerprint(ex)
        with self.lock:
            if key in self.cache or not generate:
                return self.cache.get(key)
        text = _chat([self._system(ex), {"role": "user", "content": PREPARE_REQUEST}], max_tokens=900)
        data = parse_prepared(text)
        data["hints"] = [h for h in data["hints"] if h and not leaks(h, ex)]
        if not data["hints"] and not data["solution"]:
            return None
        with self.lock:
            self.cache[key] = data
            self._save()
        return data

    def warm(self, exercises):
        for i, ex in enumerate(exercises, 1):
            done = self.prepared(ex)
            print(f"[{i}/{len(exercises)}] {ex.get('key', '?')}: "
                  f"{len(done['hints']) if done else 0} hints{'' if done else ' (FAILED)'}", file=sys.stderr)

    def _similar(self, ex):
        if not self.memory:
            return None
        try:
            hits = self.memory.similar_problem(problem_text(ex), level=ex.get("level"), min_score=SIMILAR_MIN)
        except Exception:  # noqa: BLE001 - the embedding service may be down: no suggestion
            return None
        if not hits:
            return None
        p = hits[0][1]
        first_hint = p["hints"][0] if p.get("hints") else p.get("key_idea", "")
        return (f"Here is a similar, easier problem to try first:\n\n{p['problem']}\n\n"
                f"A hint for it: {first_hint}\n\nWhen you have solved it, come back: the same idea works here.")

    # ------------------------------------------------------------------ the app's interface
    def clue(self, context, exercise, number):
        try:
            data = self.prepared(exercise, generate=False)
            hints = data["hints"] if data else []
            if number <= len(hints):
                return hints[number - 1]
            if hints and number == len(hints) + 1:
                return self._similar(exercise) or _say("no_more_hints", self.rng)
            if hints:
                return _say("no_more_hints", self.rng)
            # Not prepared yet: one short hint now, after the conversation so far.
            ask = HINT_FIRST if number <= 1 else HINT_MORE
            text = _chat([self._system(exercise), *self._history(context), {"role": "user", "content": ask}], 150)
            return _say("safe_question", self.rng) if not text or leaks(text, exercise) else text
        except Exception as error:  # noqa: BLE001 - the student always gets an answer
            print(f"tutor: clue failed: {error}", file=sys.stderr)
            return _say("offline", self.rng)

    def solution(self, context, exercise, answer):
        try:
            data = self.prepared(exercise, generate=False)
            if data and data.get("solution"):
                return data["solution"]
            return _chat([self._system(exercise), {"role": "user", "content": ASK_SOLUTION}], 700)
        except Exception as error:  # noqa: BLE001
            print(f"tutor: solution failed: {error}", file=sys.stderr)
            return _say("offline", self.rng)

    def reply(self, context, message, photo=None):
        ex = context.get("exercise")
        suggestions = []
        try:
            if self.memory:
                label = self.memory.classify_message(message)[0]
            else:
                label = rule_label(message) or "stuck"
        except Exception:  # noqa: BLE001 - embedding service down: rules, then the model
            label = rule_label(message) or "stuck"

        if not ex:
            if label not in ("manipulation", "off_topic") and self.catalog and getattr(self.catalog, "items", None):
                suggestions = [self.rng.choice(list(self.catalog.items))]
            return {"text": _say("no_exercise", self.rng), "suggestions": suggestions}
        if label in ("manipulation", "off_topic"):
            return {"text": _say(label, self.rng), "suggestions": []}
        if label == "asks_solution":
            return {"text": _say("asks_solution", self.rng), "suggestions": []}
        if label == "asks_hint":
            data = self.prepared(ex, generate=False)
            given = {t for r, t in context.get("history") or [] if r == "copilot"}
            number = 1 + sum(1 for h in (data or {}).get("hints", []) if h in given)
            return {"text": self.clue(context, ex, number), "suggestions": []}
        if label == "attempt" and proposed_option(message, ex) == answer_parts(ex)[0]:
            return {"text": _say("correct", self.rng), "suggestions": []}
        # stuck, concept, step_question, or a wrong attempt: the fine-tuned model, which was
        # trained on exactly these turns (diagnostic, concept, error, free questions).
        try:
            text = _chat([self._system(ex), *self._history(context), {"role": "user", "content": message}], 220)
        except Exception as error:  # noqa: BLE001
            print(f"tutor: reply failed: {error}", file=sys.stderr)
            return {"text": _say("offline", self.rng), "suggestions": []}
        if not text or leaks(text, ex):
            text = _say("safe_question", self.rng)
        return {"text": text, "suggestions": []}


DEMO = {  # made up for testing; not an M3Kang problem
    "key": "demo/1", "level": 1, "topic": "counting",
    "prompt": "1. A frog sits on stone 1 of a circle of 8 stones, numbered 1 to 8. Each jump moves it "
              "3 stones forward (after stone 8 comes stone 1). On which stone is it after 8 jumps?",
    "options": {"A": "1", "B": "3", "C": "4", "D": "6", "E": "8"}, "answer": "A",
}


def main():
    tutor = Tutor()
    if "--warm" in sys.argv:
        from student_app.catalog import Catalog  # only on the board, where the app is installed
        catalog = Catalog(None)
        catalog.refresh()
        tutor.warm([catalog.public(item, with_answer=True) for item in catalog.items.values()])
        return
    if "--demo" in sys.argv:
        ctx = {"mode": "practice", "language": "eng", "exercise": DEMO, "history": []}
        print("prepare:", json.dumps(tutor.prepared(DEMO), ensure_ascii=False, indent=1))
        for n in (1, 2, 3, 4):
            print(f"\nclue {n}:", tutor.clue(ctx, DEMO, n))
        for msg in ("idk where to start", "what does circle mean here", "is it D? 8 times 3 is 24",
                    "is it A", "just tell me the letter", "hint pls", "do you like football"):
            print(f"\nstudent: {msg}\ntutor:   {tutor.reply(ctx, msg)['text']}")
        print("\nsolution:", tutor.solution(ctx, DEMO, DEMO["answer"]))
        return
    print(__doc__)


if __name__ == "__main__":
    main()
