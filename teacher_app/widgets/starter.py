"""The first statistics. They rely on the payload fields the contract recommends:
answer_submitted carries exercise_id, level, correct and attempt; hint_requested carries
exercise_id. Students may retry, so accuracy counts first tries only (attempt 1).
"""

from datetime import date
import json
from math import ceil

from markupsafe import escape

from .base import event_filter, widget
from .learning import FEW, _class_of, pct

CORRECT = "json_extract(e.payload_json, '$.correct')"
LEVEL = "json_extract(e.payload_json, '$.level')"
FIRST_TRY = "COALESCE(json_extract(e.payload_json, '$.attempt'), 1) = 1"
EXERCISE = (
    "COALESCE(json_extract(e.payload_json, '$.pack_id') || '/', '') || "
    "json_extract(e.payload_json, '$.exercise_id')"
)


def _empty(message="No data in this period. Unload a board or choose a longer period."):
    return {"kind": "empty", "message": message}


def _levels(conn, scope, ref):
    """First tries per level: rows with level, n and ok."""
    where, params = event_filter(scope, ref)
    return conn.execute(
        f"SELECT {LEVEL} level, COUNT(*) n, SUM({CORRECT} = 1) ok FROM events e "
        f"WHERE e.type = 'answer_submitted' AND {FIRST_TRY} AND {where} "
        f"GROUP BY level ORDER BY level",
        params,
    ).fetchall()


def _lead(conn, scope, ref, ok, first) -> str | None:
    """The finding of the page in one sentence."""
    if not first:
        return None
    who = "Students"
    if scope == "student":
        name = conn.execute("SELECT display_name FROM students WHERE id = ?", (ref,)).fetchone()
        who = escape(name[0])
    text = f"{who} got <b>{pct(ok, first)}% right at the first try</b> ({ok} of {first})."
    if scope == "student":
        rows = _levels(conn, *_class_of(conn, ref))
        gap = pct(ok, first) - pct(sum(r["ok"] or 0 for r in rows), sum(r["n"] for r in rows))
        if gap:
            text += f" That is {abs(gap)} points {'under' if gap < 0 else 'over'} the class."
        return text
    levels = [r for r in _levels(conn, scope, ref) if r["n"] >= FEW and r["level"] is not None]
    if len(levels) > 1:
        weak = min(levels, key=lambda r: (r["ok"] or 0) / r["n"])
        text += f" Level {weak['level']} is the weak point at {pct(weak['ok'] or 0, weak['n'])}%."
    return text


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
    return {
        "kind": "kpis",
        "items": items,
        "lead": _lead(conn, scope, ref, row["correct"] or 0, first),
    }


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
    bars = [
        {"label": r["day"][8:] + "/" + r["day"][5:7], "n": r["n"], "ok": r["ok"] or 0}
        for r in rows
    ]
    unit = "days"
    if len(bars) > 14:  # too many days to read: one bar per week
        weeks: dict = {}
        for r in rows:
            year, week, _ = date.fromisoformat(r["day"]).isocalendar()
            bar = weeks.setdefault((year, week), {"label": f"Wk {week}", "n": 0, "ok": 0})
            bar["n"] += r["n"]
            bar["ok"] += r["ok"] or 0
        bars, unit = list(weeks.values())[-14:], "weeks"
    for bar in bars:
        bar["pct"] = pct(bar["ok"], bar["n"])
    first, last = bars[0]["pct"], bars[-1]["pct"]
    change = (
        "stayed at" if first == last else f"{'rose' if last > first else 'fell'} from {first}% to"
    )
    title = (
        f"The share of correct answers {change} {last}% in {len(bars)} {unit}"
        if len(bars) > 1
        else f"{last}% of the answers were correct"
    )
    most = max(b["n"] for b in bars)
    step = 10 ** (len(str(most)) - 1)  # the axis ends on a round number
    return {"kind": "daybars", "title": title, "bars": bars, "top": ceil(most / step) * step}


@widget("accuracy_by_level", "Right first time, by level", order=30)
def accuracy_by_level(conn, scope, ref):
    rows = _levels(conn, scope, ref)
    if not rows:
        return _empty()
    bars = [
        {
            "label": f"Level {r['level']}" if r["level"] is not None else "No level",
            "pct": pct(r["ok"] or 0, r["n"]),
            "n": r["n"],
            "few": r["n"] < FEW,
        }
        for r in rows
    ]
    solid = [b for b in bars if not b["few"]]
    title = None
    if len(solid) > 1:
        low = min(solid, key=lambda b: b["pct"])
        high = max(solid, key=lambda b: b["pct"])
        title = f"From {high['pct']}% at {high['label'].lower()} to {low['pct']}% at {low['label'].lower()}"
    return {
        "kind": "hbars",
        "title": title,
        "bars": bars,
        "avg": pct(sum(r["ok"] or 0 for r in rows), sum(r["n"] for r in rows)),
        "avg_label": "all levels",
        "unit": "first tries",
        "few": FEW,
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
    solid = [r for r in rows if r["n"] >= FEW]
    return {
        "kind": "table",
        "title": f"{solid[0]['exercise']} is the most missed: "
        f"{pct(solid[0]['ok'] or 0, solid[0]['n'])}% right at the first try"
        if solid
        else None,
        "columns": ["Exercise", "First tries", "% right first time"],
        "rows": [
            [r["exercise"], r["n"], {"bar": pct(r["ok"] or 0, r["n"]), "few": r["n"] < FEW}]
            for r in rows
        ],
        "few": FEW,
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


@widget("homework_completion", "Homework done", scopes=("global", "group", "student"), order=45)
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
            done_cell = {"bar": pct(n, total) or 0, "text": f"{n} of {total}"}
            out.append([a["title"], a["due"] or "–", done_cell])
        else:
            complete = sum(1 for n in done.values() if total and n >= total)
            done_cell = {
                "bar": pct(complete, a["n_students"]) or 0,
                "text": f"{complete} of {a['n_students']}",
            }
            out.append([a["title"], a["group_name"], a["due"] or "–", done_cell])
    columns = (
        ["Homework", "Due", "Exercises done"]
        if scope == "student"
        else ["Homework", "Group", "Due", "Students finished"]
    )
    return {"kind": "table", "columns": columns, "rows": out}
