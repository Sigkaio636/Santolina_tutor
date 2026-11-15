"""The learning-progress widgets: episodes, the class map and the period filter."""

from datetime import UTC, datetime, timedelta
import json

from fastapi.testclient import TestClient

from teacher_app import config
from teacher_app.simulate import create_fake_boards, simulate_sessions
from teacher_app.web.main import create_app
from teacher_app.widgets import render_all
from teacher_app.widgets.learning import CLUE, FIRST, OPEN, RETRY, SOLUTION, episodes


def _log(conn, student_id, session, exercise, steps, days_ago=0, topic="Fractions"):
    """Write one session with the events of `steps`: 'hint', 'solution', 'ok' or 'wrong'."""
    ts = (datetime.now(UTC) - timedelta(days=days_ago)).isoformat()
    with conn:
        conn.execute(
            "INSERT OR IGNORE INTO sessions (session_id, board_id, student_id, time_quality) "
            "VALUES (?, 'B1', ?, 'phone')",
            (session, student_id),
        )
        for seq, step in enumerate(steps):
            payload = {"pack_id": "p", "exercise_id": exercise, "topic": topic, "level": 1}
            kind = {"hint": "hint_requested", "solution": "solution_requested"}.get(
                step, "answer_submitted"
            )
            if kind == "answer_submitted":
                payload |= {"correct": step == "ok", "attempt": 1 + steps[:seq].count("wrong")}
            conn.execute(
                "INSERT INTO events VALUES (?, ?, 'B1', ?, ?, ?, ?, ?, ?)",
                (f"{session}-{exercise}-{seq}", session, student_id, seq, kind, ts, ts,
                 json.dumps(payload)),
            )  # fmt: skip


def test_an_episode_is_classified_by_how_the_student_got_there(conn, group_with_students):
    cases = {
        "e1": (["ok"], FIRST, True),
        "e2": (["wrong", "ok"], RETRY, False),
        "e3": (["hint", "ok"], CLUE, True),
        "e4": (["wrong", "solution", "ok"], SOLUTION, False),
        "e5": (["wrong"], OPEN, False),
        "e6": (["hint"], OPEN, None),
    }
    for exercise, (steps, _, _) in cases.items():
        _log(conn, 1, "s1", exercise, steps)
    found = {ep["exercise"]: ep for ep in episodes(conn, "student", 1)}
    for exercise, (_, outcome, first_ok) in cases.items():
        ep = found["p/" + exercise]
        assert (ep["outcome"], ep["first_ok"]) == (outcome, first_ok), exercise


def test_class_map_counts_first_tries_per_student_and_topic(conn, group_with_students):
    _log(conn, 1, "s1", "e1", ["ok"])
    _log(conn, 1, "s1", "e2", ["wrong", "ok"])
    _log(conn, 2, "s2", "e1", ["ok"], topic="Logic")
    (_, data), *_ = render_all(conn, "group", group_with_students, only=("class_map",))
    assert data["columns"] == ["Logic", "Fractions"]  # the hardest column is last
    rows = {r["name"]: r for r in data["rows"]}
    assert rows["Ada"]["all"]["pct"] == 50 and rows["Ada"]["cells"][1]["n"] == 2
    assert rows["Biel"]["all"]["pct"] == 100 and rows["Biel"]["cells"][1]["pct"] is None
    assert rows["Carla"]["all"]["pct"] is None  # no data: still listed
    assert data["avg"] == 67 and data["rows"][0]["name"] == "Ada"  # lowest first


def test_the_period_leaves_older_events_out(conn, group_with_students):
    _log(conn, 1, "old", "e1", ["wrong"], days_ago=20)
    _log(conn, 1, "new", "e2", ["ok"], days_ago=1)

    def answers(period):
        (_, data), *_ = render_all(conn, "student", 1, only=("counts",), period=period)
        return {i["label"]: i["value"] for i in data["items"]}["Answers"]

    assert (answers("7"), answers("30"), answers("all")) == (1, 2, 2)


def test_pages_draw_the_new_widgets_in_every_period(tmp_path):
    boards_dir = tmp_path / "boards"
    create_fake_boards(boards_dir, n=1)
    settings = config.Settings(home=tmp_path / "home", port=0, fake_boards=boards_dir, adb="")
    client = TestClient(create_app(settings))
    client.post("/groups", data={"name": "3B"})
    for name in ("Ada", "Biel"):
        client.post("/students", data={"display_name": name, "group_id": "1"})
    client.post("/packs/demo")
    client.post("/setup/FAKE0001", data={"name": "Board 1", "group_id": "1"})
    client.post("/boards/FAKE0001/packs", data={"pack_id": "demo-arithmetic"})
    simulate_sessions(boards_dir / "FAKE0001" / "santolina", sessions=12, unknown_rate=0, seed=3)
    client.post("/boards/FAKE0001/unload")
    for url in ("/", "/groups/1", "/students/1"):
        for period in ("7", "30", "all", "nonsense"):
            r = client.get(url, params={"period": period})
            assert r.status_code == 200 and "Error:" not in r.text, (url, period)
    dashboard = client.get("/?period=all").text
    assert 'class="cm gap"' in dashboard and "Multiplication" in dashboard
    missed = dashboard.split("Most missed exercises")[1].split("</section>")[0]
    assert "%</b>" in missed  # a bar cell shows its number
    student = client.get("/students/1?period=all").text
    assert "widget-sessions" in student and "widget-trace" in student
