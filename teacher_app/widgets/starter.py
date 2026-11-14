"""The first statistics. They rely on the payload fields the contract recommends:
answer_submitted carries exercise_id, level, correct and attempt; hint_requested carries
exercise_id. Students may retry, so accuracy counts first tries only (attempt 1).
"""

import json

from .base import event_filter, widget

CORRECT = "json_extract(e.payload_json, '$.correct')"
LEVEL = "json_extract(e.payload_json, '$.level')"
FIRST_TRY = "COALESCE(json_extract(e.payload_json, '$.attempt'), 1) = 1"
EXERCISE = (
    "COALESCE(json_extract(e.payload_json, '$.pack_id') || '/', '') || "
    "json_extract(e.payload_json, '$.exercise_id')"
)


def _empty(message="No data yet. Unload a board to see this."):
    return {"kind": "empty", "message": message}


@widget("counts", "Overview", order=10)
def counts(conn, scope, ref):
    where, params = event_filter(scope, ref)
    row = conn.execute(
        f"SELECT COUNT(DISTINCT e.session_id) sessions, "
        f"SUM(e.type = 'answer_submitted') answers, "
        f"SUM(e.type = 'answer_submitted' AND {FIRST_TRY}) first_tries, "
        f"SUM(e.type = 'answer_submitted' AND {FIRST_TRY} AND {CORRECT} = 1) correct, "
        f"SUM(e.type = 'hint_requested') hints, "
        f"SUM(e.type = 'solution_requested') solutions, "
        f"SUM(e.type = 'question_asked') questions, "
        f"COUNT(DISTINCT e.board_id) boards "
        f"FROM events e WHERE {where}",
        params,
    ).fetchone()
    answers = row["answers"] or 0
    first = row["first_tries"] or 0
    items = [
        {"label": "Sessions", "value": row["sessions"] or 0},
        {"label": "Answers", "value": answers},
        {
            "label": "Right first time",
            "value": f"{100 * (row['correct'] or 0) / first:.0f}%" if first else "–",
        },
        {"label": "Clues", "value": row["hints"] or 0},
        {"label": "Solutions shown", "value": row["solutions"] or 0},
        {"label": "Questions", "value": row["questions"] or 0},
    ]
    if scope == "global":
        students = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
        boards = conn.execute("SELECT COUNT(*) FROM boards").fetchone()[0]
        items = [
            {"label": "Students", "value": students},
            {"label": "Boards", "value": boards},
        ] + items
    elif scope == "student":
        items.append({"label": "Boards used", "value": row["boards"] or 0})
    return {"kind": "kpis", "items": items}


@widget("activity", "Answers per day", order=20)
def activity(conn, scope, ref):
    where, params = event_filter(scope, ref)
    rows = conn.execute(
        f"SELECT substr(e.ts_corrected, 1, 10) day, COUNT(*) n, SUM({CORRECT} = 1) ok "
        f"FROM events e WHERE e.type = 'answer_submitted' AND {where} "
        f"GROUP BY day ORDER BY day",
        params,
    ).fetchall()
    if not rows:
        return _empty()
    return {
        "kind": "line",
        "labels": [r["day"] for r in rows],
        "series": [
            {"label": "Answers", "data": [r["n"] for r in rows]},
            {"label": "Correct", "data": [r["ok"] or 0 for r in rows]},
        ],
    }


@widget("accuracy_by_level", "Right first time, by level", order=30)
def accuracy_by_level(conn, scope, ref):
    where, params = event_filter(scope, ref)
    rows = conn.execute(
        f"SELECT {LEVEL} level, COUNT(*) n, SUM({CORRECT} = 1) ok FROM events e "
        f"WHERE e.type = 'answer_submitted' AND {FIRST_TRY} AND {where} "
        f"GROUP BY level ORDER BY level",
        params,
    ).fetchall()
    if not rows:
        return _empty()
    return {
        "kind": "bar",
        "unit": "%",
        "labels": [f"Level {r['level']}" if r["level"] is not None else "No level" for r in rows],
        "series": [
            {"label": "% correct", "data": [round(100 * (r["ok"] or 0) / r["n"]) for r in rows]}
        ],
        "notes": [f"{r['n']} answers" for r in rows],
    }


@widget("most_missed", "Most missed exercises", scopes=("global", "group", "board"), order=40)
def most_missed(conn, scope, ref):
    where, params = event_filter(scope, ref)
    rows = conn.execute(
        f"SELECT {EXERCISE} exercise, COUNT(*) n, SUM({CORRECT} = 1) ok FROM events e "
        f"WHERE e.type = 'answer_submitted' AND {FIRST_TRY} AND {where} GROUP BY exercise "
        f"HAVING n >= 2 ORDER BY (1.0 * ok / n), n DESC LIMIT 10",
        params,
    ).fetchall()
    if not rows:
        return _empty()
    return {
        "kind": "table",
        "columns": ["Exercise", "First tries", "% right first time"],
        "rows": [[r["exercise"], r["n"], f"{100 * (r['ok'] or 0) / r['n']:.0f}%"] for r in rows],
    }


@widget("hints_per_exercise", "Exercises with the most hints", order=50)
def hints_per_exercise(conn, scope, ref):
    where, params = event_filter(scope, ref)
    rows = conn.execute(
        f"SELECT {EXERCISE} exercise, COUNT(*) n, COUNT(DISTINCT e.session_id) sessions "
        f"FROM events e WHERE e.type = 'hint_requested' AND {where} "
        f"GROUP BY exercise ORDER BY n DESC LIMIT 10",
        params,
    ).fetchall()
    if not rows:
        return _empty("No hints asked yet.")
    return {
        "kind": "table",
        "columns": ["Exercise", "Hints", "Sessions"],
        "rows": [[r["exercise"], r["n"], r["sessions"]] for r in rows],
    }


@widget("students_table", "Students", scopes=("global", "group"), order=60)
def students_table(conn, scope, ref):
    group_clause = "WHERE s.group_id = ?" if scope == "group" else ""
    rows = conn.execute(
        f"SELECT s.display_name, s.code, "
        f"(SELECT COUNT(*) FROM events e WHERE e.student_id = s.id "
        f" AND e.type = 'answer_submitted') n, "
        f"(SELECT SUM({CORRECT} = 1) FROM events e WHERE e.student_id = s.id "
        f" AND e.type = 'answer_submitted') ok, "
        f"(SELECT MAX(e.ts_corrected) FROM events e WHERE e.student_id = s.id) last "
        f"FROM students s {group_clause} ORDER BY s.display_name",
        (ref,) if scope == "group" else (),
    ).fetchall()
    if not rows:
        return _empty("No students yet.")
    return {
        "kind": "table",
        "columns": ["Student", "Code", "Answers", "% correct", "Last activity"],
        "rows": [
            [
                r["display_name"],
                r["code"],
                r["n"],
                f"{100 * (r['ok'] or 0) / r['n']:.0f}%" if r["n"] else "–",
                (r["last"] or "–")[:16].replace("T", " "),
            ]
            for r in rows
        ],
    }


@widget("boards_sync", "Boards and last unload", scopes=("global", "group"), order=70)
def boards_sync(conn, scope, ref):
    group_clause = "WHERE b.group_id = ?" if scope == "group" else ""
    rows = conn.execute(
        f"SELECT b.name, b.board_id, b.mode, "
        f"(SELECT MAX(at) FROM syncs y WHERE y.board_id = b.board_id) last_sync, "
        f"(SELECT COUNT(*) FROM sessions x WHERE x.board_id = b.board_id) sessions "
        f"FROM boards b {group_clause} ORDER BY b.name",
        (ref,) if scope == "group" else (),
    ).fetchall()
    if not rows:
        return _empty("No boards yet.")
    return {
        "kind": "table",
        "columns": ["Board", "Serial", "Mode", "Last unload", "Sessions"],
        "rows": [
            [
                r["name"],
                r["board_id"],
                r["mode"],
                (r["last_sync"] or "never")[:16].replace("T", " "),
                r["sessions"],
            ]
            for r in rows
        ],
    }


@widget("help_per_exercise", "Questions and solutions per exercise", order=55)
def help_per_exercise(conn, scope, ref):
    where, params = event_filter(scope, ref)
    rows = conn.execute(
        f"SELECT {EXERCISE} exercise, SUM(e.type = 'question_asked') questions, "
        f"SUM(e.type = 'solution_requested') solutions, COUNT(DISTINCT e.session_id) sessions "
        f"FROM events e WHERE e.type IN ('question_asked', 'solution_requested') "
        f"AND json_extract(e.payload_json, '$.exercise_id') IS NOT NULL AND {where} "
        f"GROUP BY exercise ORDER BY questions + solutions DESC LIMIT 10",
        params,
    ).fetchall()
    if not rows:
        return _empty("No questions or solutions asked yet.")
    return {
        "kind": "table",
        "columns": ["Exercise", "Questions", "Solutions shown", "Sessions"],
        "rows": [[r["exercise"], r["questions"], r["solutions"], r["sessions"]] for r in rows],
    }


@widget("homework_completion", "Homework done", scopes=("global", "group", "student"), order=15)
def homework_completion(conn, scope, ref):
    """Per assignment: students who solved every exercise, alone or with help."""
    group_clause = {
        "group": "WHERE a.group_id = ?",
        "student": "WHERE a.group_id = (SELECT group_id FROM students WHERE id = ?)",
    }.get(scope, "")
    rows = conn.execute(
        f"SELECT a.*, g.name group_name, (SELECT COUNT(*) FROM students s "
        f"WHERE s.group_id = a.group_id) n_students FROM assignments a "
        f"JOIN groups g ON g.id = a.group_id {group_clause} "
        f"ORDER BY COALESCE(a.due, '9999')",
        (ref,) if group_clause else (),
    ).fetchall()
    if not rows:
        return _empty("No homework assigned yet.")
    out = []
    for a in rows:
        solved = conn.execute(
            "SELECT e.student_id, COUNT(DISTINCT json_extract(e.payload_json, '$.exercise_id')) n "
            "FROM events e WHERE json_extract(e.payload_json, '$.assignment_id') = ? "
            "AND e.student_id IS NOT NULL AND ((e.type = 'answer_submitted' AND "
            "json_extract(e.payload_json, '$.correct') = 1) OR e.type = 'solution_requested') "
            "GROUP BY e.student_id",
            (a["assignment_id"],),
        ).fetchall()
        if a["exercise_ids_json"]:
            total = len(json.loads(a["exercise_ids_json"]))
        else:
            total = conn.execute(
                "SELECT count FROM packs WHERE pack_id = ? ORDER BY version DESC LIMIT 1",
                (a["pack_id"],),
            ).fetchone()
            total = total[0] if total else 0
        done = {r["student_id"]: r["n"] for r in solved}
        if scope == "student":
            n = done.get(ref, 0)
            out.append([a["title"], a["due"] or "–", f"{n}/{total} exercises"])
        else:
            complete = sum(1 for n in done.values() if total and n >= total)
            out.append(
                [a["title"], a["group_name"], a["due"] or "–", f"{complete}/{a['n_students']}"]
            )
    columns = (
        ["Homework", "Due", "Done"]
        if scope == "student"
        else ["Homework", "Group", "Due", "Students finished"]
    )
    return {"kind": "table", "columns": columns, "rows": out}
