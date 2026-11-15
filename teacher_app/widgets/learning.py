"""Learning-progress widgets: the class as a whole and each student.

They all read "episodes": one student working on one exercise in one session. An episode
comes from the events the boards already log (answer_submitted, hint_requested,
solution_requested), so no extra data is collected.
"""

from statistics import median

from .base import event_filter, widget

EXERCISE = (
    "COALESCE(json_extract(e.payload_json, '$.pack_id') || '/', '') || "
    "json_extract(e.payload_json, '$.exercise_id')"
)
# How a student got to the right answer, from most to least independent.
OUTCOMES = [
    "Right at the first try",
    "Right after another try",
    "Right with a clue",
    "After seeing the solution",
    "Not finished",
]
FIRST, RETRY, CLUE, SOLUTION, OPEN = range(5)
THIN = 3  # a cell with fewer first tries is shown, but marked as weak evidence
FEW = 10  # a bar with fewer first tries is hatched


def _empty(message="No data in this period. Unload a board or choose a longer period."):
    return {"kind": "empty", "message": message}


def pct(ok, n):
    return round(100 * ok / n) if n else None


def episodes(conn, scope, ref) -> list:
    """One dict per (session, exercise), oldest first.

    first_ok is None when the student asked for help but never answered.
    """
    where, params = event_filter(scope, ref)
    rows = conn.execute(
        f"SELECT e.student_id, e.session_id, e.type, e.ts_corrected ts, {EXERCISE} exercise, "
        f"json_extract(e.payload_json, '$.topic') topic, "
        f"json_extract(e.payload_json, '$.level') level, "
        f"json_extract(e.payload_json, '$.correct') correct, "
        f"json_extract(e.payload_json, '$.with_help') with_help "
        f"FROM events e WHERE e.type IN ('answer_submitted', 'hint_requested', "
        f"'solution_requested') AND json_extract(e.payload_json, '$.exercise_id') IS NOT NULL "
        f"AND {where} ORDER BY e.session_id, e.seq",
        params,
    ).fetchall()
    found: dict = {}
    for r in rows:
        ep = found.setdefault(
            (r["session_id"], r["exercise"]),
            {
                "student_id": r["student_id"],
                "session_id": r["session_id"],
                "exercise": r["exercise"],
                "topic": r["topic"],
                "level": r["level"],
                "ts": r["ts"],
                "first_ok": None,
                "outcome": OPEN,
                "_answers": 0,
                "_hints": 0,
                "_solution": False,
            },
        )
        if ep["outcome"] != OPEN:  # solved already: later events don't change the outcome
            continue
        if r["type"] == "hint_requested":
            ep["_hints"] += 1
        elif r["type"] == "solution_requested":
            ep["_solution"] = True
        else:
            ep["_answers"] += 1
            if ep["_answers"] == 1:
                ep["first_ok"] = bool(r["correct"])
            if r["correct"]:
                if ep["_solution"] or r["with_help"]:
                    ep["outcome"] = SOLUTION
                elif ep["_hints"]:
                    ep["outcome"] = CLUE
                else:
                    ep["outcome"] = FIRST if ep["_answers"] == 1 else RETRY
    return sorted(found.values(), key=lambda ep: ep["ts"])


def _columns(eps) -> tuple:
    """The columns of a per-topic view: topics when the exercises have one, else levels."""
    if any(ep["topic"] for ep in eps):
        return "topic", lambda ep: ep["topic"] or "No topic"
    return "level", lambda ep: "No level" if ep["level"] is None else f"Level {ep['level']}"


def _tally(eps, key) -> dict:
    """{key: [right at the first try, first tries]} over the answered episodes."""
    out: dict = {}
    for ep in eps:
        if ep["first_ok"] is None:
            continue
        cell = out.setdefault(key(ep), [0, 0])
        cell[0] += ep["first_ok"]
        cell[1] += 1
    return out


def _total(tally) -> tuple:
    return sum(c[0] for c in tally.values()), sum(c[1] for c in tally.values())


def _cell(ok, n, avg) -> dict:
    """What the page needs to paint one cell by score and by gap to the class."""
    p = pct(ok, n)
    if p is None:
        return {"n": 0, "pct": None}
    gap = p - avg
    return {
        "n": n,
        "ok": ok,
        "pct": p,
        "thin": n < THIN,
        "score": round(8 + p * 0.82),
        "strength": round(min(1, abs(gap) / 40) * 82),
        "below": gap < 0,
    }


def _students(conn, scope, ref) -> list:
    clause, params = ("WHERE s.group_id = ?", (ref,)) if scope == "group" else ("", ())
    return conn.execute(
        f"SELECT s.id, s.display_name, s.code FROM students s {clause} ORDER BY s.display_name",
        params,
    ).fetchall()


def _class_of(conn, student_id) -> tuple:
    """The scope a student is compared with: their group, or everyone without a group."""
    row = conn.execute("SELECT group_id FROM students WHERE id = ?", (student_id,)).fetchone()
    return ("group", row["group_id"]) if row and row["group_id"] else ("global", None)


@widget("class_map", "Class map", scopes=("global", "group"), order=12)
def class_map(conn, scope, ref):
    students = _students(conn, scope, ref)
    eps = [ep for ep in episodes(conn, scope, ref) if ep["student_id"] is not None]
    if not students:
        return _empty("No students yet.")
    if not any(ep["first_ok"] is not None for ep in eps):
        return _empty()
    kind, key = _columns(eps)
    class_tally = _tally(eps, key)
    ok_all, n_all = _total(class_tally)
    avg = pct(ok_all, n_all)
    # Hardest column last, so the weak corner of the map is at the bottom right.
    columns = sorted(class_tally, key=lambda c: -class_tally[c][0] / class_tally[c][1])
    rows = []
    for s in students:
        mine = [ep for ep in eps if ep["student_id"] == s["id"]]
        tally = _tally(mine, key)
        ok, n = _total(tally)
        mix = [sum(ep["outcome"] == o for ep in mine) for o in range(len(OUTCOMES))]
        rows.append(
            {
                "id": s["id"],
                "name": s["display_name"],
                "code": s["code"],
                "cells": [_cell(*tally.get(c, (0, 0)), avg) for c in columns],
                "all": _cell(ok, n, avg),
                "mix": [round(100 * m / len(mine), 1) if mine else 0 for m in mix],
                "mix_text": ", ".join(f"{OUTCOMES[i]}: {m}" for i, m in enumerate(mix) if m),
                "last": max((ep["ts"] for ep in mine), default=""),
            }
        )
    rows.sort(key=lambda r: (r["all"]["pct"] is None, r["all"]["pct"] or 0, r["name"]))
    weakest = [r["name"] for r in rows if r["all"]["pct"] is not None][:3]
    return {
        "kind": "classmap",
        "title": f"{columns[-1]} is the weakest {kind} for the class "
        f"({pct(*class_tally[columns[-1]])}%). {', '.join(weakest)} "
        f"{'has' if len(weakest) == 1 else 'have'} the lowest results overall.",
        "columns": columns,
        "rows": rows,
        "footer": [pct(*class_tally[c]) for c in columns],
        "avg": avg,
        "n": n_all,
        "outcomes": OUTCOMES,
        "thin": THIN,
    }


@widget("spread", "Spread", scopes=("global", "group"), order=35)
def spread(conn, scope, ref):
    """One dot per student and column: is it hard for everyone, or only for some?"""
    eps = [ep for ep in episodes(conn, scope, ref) if ep["student_id"] is not None]
    kind, key = _columns(eps)
    per_student: dict = {}
    for ep in eps:
        if ep["first_ok"] is not None:
            cell = per_student.setdefault((key(ep), ep["student_id"]), [0, 0])
            cell[0] += ep["first_ok"]
            cell[1] += 1
    values: dict = {}
    for (column, _), (ok, n) in per_student.items():
        values.setdefault(column, []).append(pct(ok, n))
    if not values:
        return _empty()
    rows = []
    for column, vals in values.items():
        stack: dict = {}
        dots = []
        for v in sorted(vals):  # dots pile up in steps of 5 points: no random jitter
            step = min(19, v // 5)
            dots.append({"x": step * 5 + 2.5, "level": stack.get(step, 0)})
            stack[step] = stack.get(step, 0) + 1
        rows.append({"label": column, "median": round(median(vals)), "dots": dots, "n": len(vals)})
    rows.sort(key=lambda r: -r["median"])
    last = rows[-1]
    return {
        "kind": "strips",
        "title": f"In {last['label']}, half the students are under {last['median']}% "
        f"right at the first try",
        "by": kind,
        "rows": rows,
    }


@widget("progress_by_session", "Progress by session", scopes=("student",), order=12)
def progress_by_session(conn, scope, ref):
    eps = episodes(conn, scope, ref)
    sessions: dict = {}
    for ep in eps:
        if ep["first_ok"] is not None:
            s = sessions.setdefault(ep["session_id"], {"day": ep["ts"][:10], "ok": 0, "n": 0})
            s["ok"] += ep["first_ok"]
            s["n"] += 1
    points = [{**s, "pct": pct(s["ok"], s["n"])} for s in sessions.values()][-12:]
    if not points:
        return _empty()
    class_ok, class_n = _total(_tally(episodes(conn, *_class_of(conn, ref)), lambda ep: 0))
    half = len(points) // 2

    def share(part):
        return pct(sum(p["ok"] for p in part), sum(p["n"] for p in part))

    if half >= 2:
        title = (
            f"From {share(points[:half])}% in the first {half} sessions "
            f"to {share(points[-half:])}% in the last {half}"
        )
    else:
        title = f"{points[-1]['pct']}% right at the first try in the last session"
    return {
        "kind": "sessions",
        "title": title,
        "points": points,
        "class_avg": pct(class_ok, class_n),
        "few": FEW,
    }


@widget("topic_profile", "Against the class", scopes=("student",), order=13)
def topic_profile(conn, scope, ref):
    mine = episodes(conn, scope, ref)
    theirs = episodes(conn, *_class_of(conn, ref))
    kind, key = _columns(theirs or mine)
    me, them = _tally(mine, key), _tally(theirs, key)
    rows = [
        {
            "label": c,
            "pct": pct(*me[c]),
            "n": me[c][1],
            "thin": me[c][1] < THIN,
            "cls": pct(*them[c]),
        }
        for c in me
        if c in them
    ]
    if not rows:
        return _empty()
    rows.sort(key=lambda r: r["pct"] - r["cls"])
    worst = rows[0]
    return {
        "kind": "profile",
        "title": f"{worst['label']}: {worst['pct']}% against {worst['cls']}% for the class",
        "by": kind,
        "rows": rows,
        "thin": THIN,
    }


@widget("trace", "Last exercises, oldest first", scopes=("student",), order=14)
def trace(conn, scope, ref):
    eps = episodes(conn, scope, ref)[-48:]
    if not eps:
        return _empty()
    items, session = [], None
    for ep in eps:
        items.append(
            {
                "outcome": ep["outcome"],
                "text": f"{ep['exercise']}: {OUTCOMES[ep['outcome']].lower()}",
                "gap": session is not None and ep["session_id"] != session,
            }
        )
        session = ep["session_id"]
    half = len(items) // 2

    def alone(part):
        return pct(sum(i["outcome"] == FIRST for i in part), len(part))

    title = (
        f"Right at the first try in {alone(items[:half])}% of the first {half} "
        f"and {alone(items[half:])}% of the last {len(items) - half}"
        if half >= 3
        else f"{len(items)} exercises so far"
    )
    return {"kind": "trace", "title": title, "items": items, "outcomes": OUTCOMES}
