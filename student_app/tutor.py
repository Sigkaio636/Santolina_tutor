"""The copilot behind the chat, the clues and the solutions. A STUB for now.

Replace `Tutor` with the real back layer (language model, retrieval, leak check). Keep the
method signatures: the interface only depends on them. Calls may be slow (tens of seconds):
the server runs them in a background queue and the phone polls for the result.
"""

import random
import time

from .strings import text

# How long the stub "thinks", so the waiting indicator can be seen.
STUB_DELAY_SECONDS = 0.6


class Tutor:
    def __init__(self, catalog):
        self.catalog = catalog

    def reply(self, context: dict, message: str, photo: bytes | None = None) -> dict:
        """Answer a question. context: {mode, language, exercise: dict | None, history: [...]}.

        Returns {"text": str, "suggestions": [exercise keys]}. Suggestions appear as tappable
        exercise cards, so the copilot can steer the student to another problem.
        """
        time.sleep(STUB_DELAY_SECONDS)
        lang = context.get("language", "cat")
        suggestions = []
        if context.get("mode") == "free" or not context.get("exercise"):
            keys = list(self.catalog.items)
            if keys:
                suggestions = [random.choice(keys)]
        reply = text(lang, "stub_reply")
        if photo:
            reply += " " + text(lang, "stub_photo")
        return {"text": reply, "suggestions": suggestions}

    def clue(self, context: dict, exercise: dict, number: int) -> str:
        """The clue number `number` (1, 2, ...) for an exercise. Must not give the answer away."""
        time.sleep(STUB_DELAY_SECONDS)
        return text(context.get("language", "cat"), "stub_clue").format(n=number)

    def solution(self, context: dict, exercise: dict, answer: str) -> str:
        """An explanation of the solution. The interface shows the right letter next to it."""
        time.sleep(STUB_DELAY_SECONDS)
        return text(context.get("language", "cat"), "stub_solution").format(answer=answer)
