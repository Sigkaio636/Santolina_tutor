"""Homework: exercises the teacher assigns to a group. Boards get them as assignments.json."""

import json
import secrets

from classroom import paths
from classroom.schemas import SCHEMA_VERSION, Assignment, to_dict

from . import packs


def create(conn, group_id: int, title: str, pack_id: str, exercise_ids=None, due=None) -> str:
    assignment_id = "hw-" + secrets.token_hex(4)
    with conn:
        conn.execute(
            "INSERT INTO assignments (assignment_id, group_id, title, pack_id, "
            "exercise_ids_json, due) VALUES (?, ?, ?, ?, ?, ?)",
            (
                assignment_id,
                group_id,
                title.strip(),
                pack_id,
                json.dumps(exercise_ids) if exercise_ids else None,
                due or None,
            ),
        )
    return assignment_id


def delete(conn, assignment_id: str) -> None:
    with conn:
        conn.execute("DELETE FROM assignments WHERE assignment_id = ?", (assignment_id,))


def for_group(conn, group_id) -> list:
    rows = conn.execute(
        "SELECT * FROM assignments WHERE group_id = ? ORDER BY COALESCE(due, '9999'), created_at",
        (group_id,),
    ).fetchall()
    return [
        Assignment(
            assignment_id=r["assignment_id"],
            title=r["title"],
            pack_id=r["pack_id"],
            exercise_ids=json.loads(r["exercise_ids_json"]) if r["exercise_ids_json"] else None,
            due=r["due"],
            created_at=r["created_at"],
        )
        for r in rows
    ]


def push(conn, link) -> int:
    """Send the homework of the board's group, loading any pack the board doesn't have yet."""
    row = conn.execute("SELECT group_id FROM boards WHERE board_id = ?", (link.serial,)).fetchone()
    items = for_group(conn, row["group_id"]) if row and row["group_id"] else []
    loaded = {
        r["pack_id"]
        for r in conn.execute(
            "SELECT pack_id FROM board_packs WHERE board_id = ?", (link.serial,)
        ).fetchall()
    }
    for pack_id in {a.pack_id for a in items} - loaded:
        try:
            packs.load_on_board(conn, link, pack_id)
        except ValueError:
            pass  # the pack left the library: the student app skips its exercises
    data = {"schema_version": SCHEMA_VERSION, "assignments": [to_dict(a) for a in items]}
    link.write_text(paths.ASSIGNMENTS, json.dumps(data, ensure_ascii=False, indent=2))
    return len(items)
