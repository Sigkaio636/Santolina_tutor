"""What each student has done on this board: progress/<code>.json. Codes only, never names.

The student app keeps it, so homework badges and "Continue" survive when the teacher
clears the board's archive. The teacher app never needs it: its truth is the events.

    {"schema_version": 1, "code": "K7M2", "updated_at": "...",
     "exercises": {"<pack_id>/<exercise_id>": {"status": "done" | "with_help" | "tried",
                                               "attempts": 2, "first_try_correct": false}},
     "last": {"mode": "homework", "pack_id": ..., "exercise_id": ..., "assignment_id": ...} | null}
"""

from pathlib import Path

from . import paths
from .schemas import SCHEMA_VERSION, STUDENT_CODE_RE, ContractError, now_iso, read_json, write_json

DONE = ("done", "with_help")


def key(pack_id: str, exercise_id: str) -> str:
    return f"{pack_id}/{exercise_id}"


def _path(root, code: str) -> Path:
    if not STUDENT_CODE_RE.match(code):
        raise ContractError(f"invalid student code {code!r}")
    return paths.board_root(root) / paths.PROGRESS / f"{code}.json"


def load(root, code: str) -> dict:
    data = read_json(_path(root, code))
    if not data:
        data = {"schema_version": SCHEMA_VERSION, "code": code, "exercises": {}, "last": None}
    data.setdefault("exercises", {})
    data.setdefault("last", None)
    return data


def save(root, code: str, data: dict) -> None:
    data["updated_at"] = now_iso()
    write_json(_path(root, code), data)


def record_answer(data: dict, pack_id: str, exercise_id: str, correct: bool) -> dict:
    """Update one exercise after an answer. Returns its entry."""
    entry = data["exercises"].setdefault(
        key(pack_id, exercise_id), {"status": "tried", "attempts": 0, "first_try_correct": False}
    )
    entry["attempts"] += 1
    if correct and entry["attempts"] == 1:
        entry["first_try_correct"] = True
    if correct and entry["status"] == "tried":
        entry["status"] = "done"
    return entry


def record_solution(data: dict, pack_id: str, exercise_id: str) -> dict:
    """The student asked for the solution: the exercise counts as solved with help."""
    entry = data["exercises"].setdefault(
        key(pack_id, exercise_id), {"status": "tried", "attempts": 0, "first_try_correct": False}
    )
    if entry["status"] != "done":
        entry["status"] = "with_help"
    return entry


def status(data: dict, pack_id: str, exercise_id: str) -> str | None:
    entry = data["exercises"].get(key(pack_id, exercise_id))
    return entry["status"] if entry else None
