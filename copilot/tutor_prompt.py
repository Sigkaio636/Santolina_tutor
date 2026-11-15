"""Prompt format of the fine-tuned tutor model. Single source of truth: the training data
(laptop/build_tutor_sft.py) and the board app must build prompts with these functions, or the
fine-tuned model sees inputs it was never trained on. Standard library only.

Conversation shape:
    system    tutor_system(problem, answer, notes)   problem + teacher's answer, rules
    user      PREPARE_REQUEST                         -> model writes hints + solution (format_prepared)
    -- or a live chat --
    user      "Can you give me a hint?" / "I got B, is that right?" / "Show me the solution" / ...
    assistant ...

On the board, run llama-server with --jinja --reasoning off (the model was trained without thinking).
"""
import re

TUTOR_RULES = (
    "You are a patient math tutor helping one student with one problem. The teacher gave you the "
    "problem and its correct answer.\n"
    "- When the student asks for a hint, give one short hint that moves them one step forward. "
    "Never reveal the correct option, the final number, or the full method in a hint.\n"
    "- When the student proposes an answer, say whether it is right. If it is wrong, point at the "
    "likely mistake without revealing the correct answer.\n"
    "- Only when the student asks for the solution, explain it step by step, show every "
    "calculation, and end with the correct option."
)

PREPARE_REQUEST = (
    "Prepare the tutoring material for this problem: hints from a gentle nudge to almost the "
    "method, then the full step-by-step solution."
)


def tutor_system(problem: str, answer_letter: str, answer_text: str = "", notes: str = "") -> str:
    """problem: statement, figure description and options A-E, as plain text."""
    answer = f"{answer_letter}) {answer_text}".strip() if answer_text else answer_letter
    parts = [TUTOR_RULES, f"## Problem\n{problem.strip()}", f"## Correct answer (from the teacher)\n{answer}"]
    if notes:
        parts.append(f"## Teacher's notes\n{notes.strip()}")
    return "\n\n".join(parts)


def format_prepared(hints: list[str], solution: str) -> str:
    blocks = [f"### Hint {i}\n{h.strip()}" for i, h in enumerate(hints, 1)]
    blocks.append(f"### Solution\n{solution.strip()}")
    return "\n\n".join(blocks)


def parse_prepared(text: str) -> dict:
    """Inverse of format_prepared: {"hints": [...], "solution": "..."}; tolerant of extra spaces."""
    hints, solution = [], ""
    for title, body in re.findall(r"^###\s*(Hint\s*\d+|Solution)\s*\n(.*?)(?=^###\s*(?:Hint\s*\d+|Solution)\s*$|\Z)",
                                  text, re.MULTILINE | re.DOTALL):
        if title.lower().startswith("hint"):
            hints.append(body.strip())
        else:
            solution = body.strip()
    return {"hints": hints, "solution": solution}
