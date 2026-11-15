"""The copilot behind the chat, the clues and the solutions.

It runs the fine-tuned tutor model (Qwen3.5 0.8B, `student_app/llm.py`), which answers a
problem with one short guiding question and does not give the answer away. Around it:

- `router.classify` labels each chat message (STUCK, CONCEPT, ATTEMPT, SOLUTION, OTHER).
  Today a keyword rule; the decision model replaces it later (see `student_app/router.py`).
- A leak check in code: a reply that names the right option, or its value when the
  statement does not contain it, is never shown. A fixed hint replaces it.
- The clue ladder: clue 1 asks where to start, clue 2 adds a similar easier problem from
  the retrieval index (T4), clue 3 and on ask for the next step.
- A message that names an option ("is it D?") gets no model reply: the model cannot check
  a guess (it said yes to wrong ones), and only the answer button counts an attempt.
- Solutions: `meta.solution` of the exercise when the pack has one (written ahead of
  time on the laptop). Otherwise the right option, then a request to explain it back (T8).
  The small models write wrong worked solutions, so none is generated.
- When the model server is down or slow, fixed texts keep the interface working.

The interface only depends on `reply`, `clue` and `solution`. The server runs them in a
queue of one (`student_app/jobs.py`), because the model has one slot.
"""

import random
import re

from classroom import paths
from classroom.schemas import read_json

from . import llm, router
from .planner import load_vectors, problem_id
from .strings import text

SYSTEM = "You are a Socratic math tutor."
LANGUAGE_NAMES = {"cat": "Catalan", "eng": "English", "esp": "Spanish"}
MAX_TOKENS = 90
HISTORY = 6  # earlier chat turns sent to the model; each costs prefill time on the board
TIMEOUT = 90

# What the student "says" when a button asks for help, by clue number (the model reads English)
CLUE_REQUESTS = {
    1: "I'm stuck. How do I start?",
    2: "I'm still stuck. Can you give me a more concrete hint?",
}
NEXT_STEP_REQUEST = "I'm still stuck. What is the next step? Don't tell me the final answer."
BUTTON_REQUEST = "Can you give me a hint?"  # stands in for a button press inside the history
ANSWER_WORDS = r"(?i:answer|option|letter|choice|resposta|opci[oó]|lletra|respuesta|letra)"


def format_problem(exercise: dict) -> str:
    lines = [(exercise.get("prompt") or "").strip()]
    for letter, value in sorted((exercise.get("options") or {}).items()):
        lines.append(f"{letter}) {value}")
    return "\n".join(lines)


def option_text(exercise: dict) -> str:
    """'B (8)' for a multiple-choice answer, else the answer as it is."""
    answer = exercise.get("answer") or ""
    value = (exercise.get("options") or {}).get(answer)
    return f"{answer} ({value})" if value not in (None, "") else answer


def _has_value(value: str, s: str) -> bool:
    """`value` as a whole token of `s`: '8' is in '8 euros', not in '28' nor in '8.5'."""
    value = re.sub(r"\s+", " ", value).strip().lower()
    s = re.sub(r"\s+", " ", s).lower()
    return bool(value) and re.search(rf"(?<![\w.,]){re.escape(value)}(?!\w|[.,]\d)", s) is not None


def names_an_option(s: str) -> bool:
    """A message or reply that points at an option: "is it D?", "la B", "option C"."""
    return bool(
        re.search(rf"\b{ANSWER_WORDS}\b[^.?!\n]{{0,25}}\b[A-E]\b", s)
        or re.search(r"\b(?i:la|el|is it|és|es)\s+\(?[A-E]\b\)?(?!')", s)
        or re.fullmatch(r"\W*\(?[A-Ea-e]\)?\W*", s)
    )


def leaks(reply: str, exercise: dict | None) -> bool:
    """True when the reply gives the answer away: the right letter named as an answer or
    written as an option ("B)"), or the right value when the statement does not hold it."""
    if not exercise or not exercise.get("answer"):
        return False
    letter = re.escape(exercise["answer"].upper())
    if re.search(rf"\b{ANSWER_WORDS}\b[^.?!\n]{{0,25}}\b{letter}\b", reply) or re.search(
        rf"(^|\s)\(?{letter}\)", reply
    ):
        return True
    if names_an_option(reply):
        return True  # "Sí, la D": the model can't check a guess, so it never judges one
    value = (exercise.get("options") or {}).get(exercise["answer"])
    if value in (None, "") or _has_value(str(value), exercise.get("prompt") or ""):
        return False
    return _has_value(str(value), reply)


class Tutor:
    def __init__(self, catalog, chat=None):
        self.catalog = catalog
        self.chat = chat or llm.chat  # tests pass a fake
        self._vectors = None

    # ------------------------------------------------------------------ interface
    def reply(self, context: dict, message: str, photo: bytes | None = None) -> dict:
        """Answer a chat message. Returns {"text", "suggestions", "log"}."""
        lang = context.get("language", "cat")
        exercise = context.get("exercise")
        history = context.get("history") or []
        message = (message or "").strip()
        if photo and not message:
            return self._fixed(text(lang, "tutor_photo_only"), "photo")
        if exercise and names_an_option(message):
            # Only the answer button judges an option: it counts the attempt
            return self._fixed(
                text(lang, "tutor_use_answer_button"), "use_answer_button", label="ATTEMPT"
            )
        if not exercise and router.asks_for_problem(message):
            key = self.any_problem(lang, context.get("seen") or ())
            if key:
                out = self._fixed(text(lang, "tutor_try_this"), "suggest_problem")
                out["suggestions"] = [key]
                return out
        last_tutor = next((t for who, t in reversed(history) if who == "copilot"), "")
        label = router.classify((exercise or {}).get("prompt", ""), last_tutor, message)
        if label not in router.LABELS:
            label = "STUCK"
        if label == "SOLUTION" and not router.asks_for_solution(message):
            label = "STUCK"  # the model alone never unlocks the solution
        if label == "OTHER":
            return self._fixed(text(lang, "tutor_redirect"), "redirect", label=label)
        out = self._ask_model(context, message, fallback=text(lang, "tutor_hint_1"))
        if label == "SOLUTION" and exercise:
            out["text"] += " " + text(lang, "tutor_solution_button")
        if photo:
            out["text"] += " " + text(lang, "tutor_photo_note")
        out["log"]["label"] = label
        return out

    def clue(self, context: dict, exercise: dict, number: int) -> dict:
        """Clue `number` (1, 2, ...). Never gives the answer away."""
        lang = context.get("language", "cat")
        request = CLUE_REQUESTS.get(number, NEXT_STEP_REQUEST)
        fallback = text(lang, f"tutor_hint_{min(max(number, 1), 3)}")
        out = self._ask_model(context, request, fallback=fallback)
        if number == 2:
            similar = self.easier_neighbour(exercise)
            if similar:
                out["text"] += " " + text(lang, "tutor_similar")
                out["suggestions"] = [similar]
        out["log"]["clue_number"] = number
        return out

    def solution(self, context: dict, exercise: dict, answer: str) -> dict:
        """The interface shows the right letter next to this text."""
        lang = context.get("language", "cat")
        item = self.catalog.get(exercise.get("key", "")) if exercise else None
        written = (item.exercise.meta or {}).get("solution") if item else None
        if isinstance(written, dict):
            written = written.get(lang) or written.get(item.exercise.language)
        if written:
            return self._fixed(str(written), "pack_solution")
        # The small models write wrong worked solutions: name the option, then ask the
        # student to explain it back (T8). Instant, so no wait on the board either.
        exercise = {**exercise, "answer": answer or exercise.get("answer")}
        intro = text(lang, "tutor_solution_intro").format(answer=option_text(exercise))
        return self._fixed(f"{intro} {text(lang, 'tutor_explain_back')}", "solution_option")

    # ------------------------------------------------------------------ helpers
    def messages(self, context: dict, request: str) -> list:
        """System, then the problem with the first student turn, then the chat so far."""
        lang = context.get("language", "cat")
        exercise = context.get("exercise")
        system = f"{SYSTEM} Reply in {LANGUAGE_NAMES.get(lang, 'Catalan')}."
        turns = []  # (role, text), alternating, starting with the user
        for who, said in (context.get("history") or [])[-HISTORY:]:
            role = "user" if who == "student" else "assistant"
            if role == "assistant" and (not turns or turns[-1][0] == "assistant"):
                turns.append(("user", BUTTON_REQUEST))  # a clue button, not a typed message
            if role == "user" and turns and turns[-1][0] == "user":
                turns[-1] = ("user", turns[-1][1] + "\n" + said)
                continue
            turns.append((role, said))
        if turns and turns[-1][0] == "user":
            turns[-1] = ("user", turns[-1][1] + "\n" + request)
        else:
            turns.append(("user", request))
        if exercise:
            turns[0] = ("user", format_problem(exercise) + "\n" + turns[0][1])
        return [{"role": "system", "content": system}] + [
            {"role": r, "content": c} for r, c in turns
        ]

    def _ask_model(self, context, request, fallback, check_leak=True) -> dict:
        exercise = context.get("exercise")
        log = {"route": "tutor_model"}
        try:
            result = self.chat(
                self.messages(context, request), max_tokens=MAX_TOKENS, timeout=TIMEOUT
            )
        except Exception as error:  # noqa: BLE001  (a dead server must not break the page)
            log.update(route="fallback", error=f"{type(error).__name__}: {error}"[:200])
            return {"text": fallback, "suggestions": [], "log": log}
        log.update(
            tokens=result.get("tokens"),
            prompt_tokens=result.get("prompt_tokens"),
            model_seconds=result.get("seconds"),
            first_token_seconds=result.get("first_token_seconds"),
        )
        reply = _tidy(result.get("text", ""))
        if not reply:
            log["route"] = "fallback"
            reply = fallback
        elif check_leak and leaks(reply, exercise):
            log.update(route="fallback", leak_blocked=True)
            reply = fallback
        return {"text": reply, "suggestions": [], "log": log}

    @staticmethod
    def _fixed(reply, route, **log) -> dict:
        return {"text": reply, "suggestions": [], "log": {"route": route, **log}}

    def vectors(self) -> dict:
        if not self._vectors:  # retried until an index exists
            try:
                identity = read_json(self.catalog.root / paths.IDENTITY) or {}
            except (ValueError, OSError):
                identity = {}
            self._vectors = load_vectors(identity.get("rag_index_path") or paths.find_rag_index())
        return self._vectors

    def any_problem(self, language: str, seen=()) -> str | None:
        """A problem to try: not seen in this visit, in the student's language if possible."""
        self.catalog.refresh()
        items = list(self.catalog.items.values())
        for pool in (
            [i for i in items if i.key not in seen and i.exercise.language == language],
            [i for i in items if i.key not in seen],
            items,
        ):
            if pool:
                return random.choice(pool).key
        return None

    def easier_neighbour(self, exercise: dict | None) -> str | None:
        """The key of the nearest other problem on this board at a lower level (else the
        same level), in the exercise's language when possible. None without an index."""
        current = self.catalog.get(exercise.get("key", "")) if exercise else None
        vectors = self.vectors() if current else {}
        here = vectors.get(problem_id(current)) if current else None
        if here is None:
            return None
        level = current.exercise.level if current.exercise.level is not None else 99
        best = None
        for key, item in self.catalog.items.items():
            pid = problem_id(item)
            vec = vectors.get(pid)
            if vec is None or pid == problem_id(current) or item.exercise.level is None:
                continue
            if item.exercise.level > level:
                continue
            rank = (
                item.exercise.level < level,
                item.exercise.language == current.exercise.language,
                sum(a * b for a, b in zip(here, vec)),
            )
            if best is None or rank > best[0]:
                best = (rank, key)
        return best[1] if best else None


def _tidy(reply: str) -> str:
    """Drop markdown the phone would show as symbols, and cut a reply that ran out of tokens
    at its last full sentence."""
    reply = re.sub(r"\*\*|__|`|\$", "", reply or "").strip()
    if reply and reply[-1] not in '.?!…)»"' and re.search(r"[.?!]", reply):
        reply = reply[: max(reply.rfind(c) for c in ".?!") + 1]
    return reply
