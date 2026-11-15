"""Which kind of help a student message needs. THE PLACE TO PLUG IN THE DECISION MODEL.

The labels are the five of docs/TOOL_CALLER_PROMPT.md (the student-message classifier):

    STUCK     asks for help, does not know how to start          -> Socratic question (T0)
    CONCEPT   asks what a word, formula or method means           -> Socratic reply (T5a)
    ATTEMPT   gives a number, an option or a step                 -> Socratic reply (T6)
    SOLUTION  explicitly asks for the answer                       -> Socratic reply, and the
                                                                   solution button (T7 after a try)
    OTHER     empty, off topic, unreadable                         -> redirect (T9)

Today `classify` is a keyword rule, so the tutor works without the decision model. To use
the model, replace `classify` (same arguments, same five labels) or set
`student_app.router.classify = my_function` at start-up. `student_app/tutor.py` turns
each label into a response, in `Tutor.reply`.

Safety rule from the classifier doc: the model alone must never unlock the solution. A
SOLUTION label only counts when `asks_for_solution` (keywords) agrees.
"""

import re

LABELS = ("STUCK", "CONCEPT", "ATTEMPT", "SOLUTION", "OTHER")

_SOLUTION = re.compile(
    r"\b(answer|solution|solve it|tell me|resposta|soluci[oó]|digues|d[ií]ga?me|"
    r"respuesta|resu[eé]lve|dime)\b",
    re.IGNORECASE,
)
_CONCEPT = re.compile(
    r"\b(what is|what's|what are|what does|mean|meaning|qu[eè] (és|vol dir|significa)|"
    r"qu[eé] es|qu[eé] significa|com es fa|c[oó]mo se)\b",
    re.IGNORECASE,
)
# An option letter on its own ("D", "is it C?", "la B") or a number in the message
_ATTEMPT = re.compile(r"(\b[A-E]\b(?!')|\d)")


_ANOTHER = re.compile(
    r"\b(another|next|other|new|more)\b.*\b(problem|exercise|one|question)s?\b|"
    r"\bgive me (another|more)\b|\b(un altre|un altro|otro|otra|altre|seg[uü]ent|siguiente)\b",
    re.IGNORECASE,
)


def asks_for_problem(message: str) -> bool:
    """The student wants another problem: no model needed, the tutor suggests one."""
    return bool(_ANOTHER.search(message or ""))


def asks_for_solution(message: str) -> bool:
    return bool(_SOLUTION.search(message or ""))


def classify(problem: str, last_tutor_move: str, message: str) -> str:
    """One of LABELS for the student's message. A rule today; the decision model later."""
    text = (message or "").strip()
    if not re.search(r"\w", text):
        return "OTHER"
    if asks_for_solution(text):
        return "SOLUTION"
    if _ATTEMPT.search(text):
        return "ATTEMPT"
    if _CONCEPT.search(text):
        return "CONCEPT"
    return "STUCK"
