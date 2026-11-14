"""The first statistics. They rely on the payload fields the contract recommends:
answer_submitted carries exercise_id, level and correct; hint_requested carries exercise_id.
"""

from .base import event_filter, widget

CORRECT = "json_extract(e.payload_json, '$.correct')"
LEVEL = "json_extract(e.payload_json, '$.level')"
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
        f"SUM(e.type = 'answer_submitted' AND {CORRECT} = 1) correct, "
        f"SUM(e.type = 'hint_requested') hints, "
        f"COUNT(DISTINCT e.board_id) boards "
        f"FROM events e WHERE {where}",
        params,
    ).fetchone()
    answers = row["answers"] or 0
    items = [
        {"label": "Sessions", "value": row["sessions"] or 0},
        {"label": "Answers", "value": answers},
        {
            "label": "Correct",
            "value": f"{100 * (row['correct'] or 0) / answers:.0f}%" if answers else "–",
        },
        {"label": "Hints asked", "value": row["hints"] or 0},
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


@widget("accuracy_by_level", "Correct answers by level", order=30)
def accuracy_by_level(conn, scope, ref):
    where, params = event_filter(scope, ref)
    rows = conn.execute(
        f"SELECT {LEVEL} level, COUNT(*) n, SUM({CORRECT} = 1) ok FROM events e "
        f"WHERE e.type = 'answer_submitted' AND {where} GROUP BY level ORDER BY level",
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
        f"WHERE e.type = 'answer_submitted' AND {where} GROUP BY exercise "
        f"HAVING n >= 2 ORDER BY (1.0 * ok / n), n DESC LIMIT 10",
        params,
    ).fetchall()
    if not rows:
        return _empty()
    return {
        "kind": "table",
        "columns": ["Exercise", "Answers", "% correct"],
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
