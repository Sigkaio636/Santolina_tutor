"""The student server over real HTTP, on a simulated board, then unloaded by the teacher app."""

import base64
import json
import threading
import time
import urllib.error
import urllib.request

import pytest

from classroom import paths
from classroom.events import read_events
from classroom.schemas import Assignment, now_iso, to_dict, write_json
from student_app import tutor
from student_app.server import make_server
from teacher_app.services import boards, packs, setup, unload
from teacher_app.simulate import demo_pack

tutor.STUB_DELAY_SECONDS = 0.05


class Client:
    def __init__(self, base, host=None):
        self.base = base
        self.token = None
        self.host = host

    def call(self, path, body=None):
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(self.base + path, data=data)
        req.add_header("Content-Type", "application/json")
        if self.token:
            req.add_header("X-Session", self.token)
        if self.host:
            req.add_header("Host", self.host)
        try:
            with urllib.request.urlopen(req, timeout=5) as r:
                return r.status, json.loads(r.read() or b"null")
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read() or b"null")

    def wait(self, ticket):
        for _ in range(100):
            _, r = self.call(f"/api/reply?ticket={ticket}")
            if r["status"] == "done":
                return r["result"]
            time.sleep(0.05)
        raise AssertionError("no reply")


@pytest.fixture
def board(conn, fake, group_with_students, tmp_path):
    req = setup.SetupRequest(name="Board 3", group_id=group_with_students)
    assert setup.run(conn, fake, req), req.results
    packs.import_pack(conn, demo_pack(tmp_path / "src", n=8), tmp_path / "library")
    packs.load_on_board(conn, fake, "demo-arithmetic")
    write_json(
        fake.root / paths.ASSIGNMENTS,
        {
            "schema_version": 1,
            "assignments": [
                to_dict(
                    Assignment(
                        "hw1", "Week 1", "demo-arithmetic", ["e01", "e02"], "2026-12-01", now_iso()
                    )
                )
            ],
        },
    )
    return fake


@pytest.fixture
def server(board):
    srv = make_server(board.root, "127.0.0.1", 0, public_host="10.42.0.1")
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield srv
    srv.shutdown()
    srv.server_close()


def _client(server):
    return Client(f"http://127.0.0.1:{server.server_address[1]}")


def _code(board):
    return json.loads(board.read_text(paths.ROSTER))["codes"][0]


def test_login_refuses_unknown_code(server):
    c = _client(server)
    assert c.call("/api/login", {"code": "NOPE"})[0] == 400
    assert c.call("/api/home")[0] == 401


def test_teacher_entry_only_in_professor_mode(server, board, conn):
    c = _client(server)
    assert c.call("/api/login", {"teacher": True})[0] == 400
    boards.set_mode(conn, board, "professor")
    status, r = c.call("/api/login", {"teacher": True})
    assert status == 200 and r["teacher"]
    c.token = r["token"]
    _, ex = c.call("/api/exercise?key=demo-arithmetic/e01&mode=practice")
    assert ex["answer"]  # the teacher sees answers


def test_captive_portal_redirects_other_hosts(server):
    c = Client(
        f"http://127.0.0.1:{server.server_address[1]}", host="connectivitycheck.gstatic.com"
    )
    req = urllib.request.Request(c.base + "/generate_204", headers={"Host": c.host})
    opener = urllib.request.build_opener(NoRedirect)
    with pytest.raises(urllib.error.HTTPError) as e:
        opener.open(req, timeout=5)
    assert e.value.code == 302 and e.value.headers["Location"] == "http://10.42.0.1/"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def test_full_student_visit_is_logged_and_unloaded(server, board, conn, tmp_path):
    c = _client(server)
    code = _code(board)
    status, r = c.call(
        "/api/login", {"code": code.lower(), "client_ts": now_iso(), "language": "eng"}
    )
    assert status == 200
    c.token = r["token"]

    _, home = c.call("/api/home")
    assert home["homework_pending"] == 2 and home["continue"] is None
    _, hw = c.call("/api/homework")
    assert [x["key"] for x in hw[0]["exercises"]] == ["demo-arithmetic/e01", "demo-arithmetic/e02"]
    _, topics = c.call("/api/practice")
    assert topics and topics[0]["exercises"]

    # Homework exercise: the answer never reaches the phone.
    _, ex = c.call("/api/exercise?key=demo-arithmetic/e01&mode=homework&assignment_id=hw1")
    assert "answer" not in ex and ex["state"]["can_show_solution"] is False
    assert ex["prompt_easy"] == ex["prompt"]  # a one-sentence problem: easy read keeps it
    exercise = board.root / paths.EXERCISES / "demo-arithmetic" / "exercises.json"
    right = json.loads(exercise.read_text())["exercises"][0]["answer"]
    wrong = next(k for k in ex["options"] if k != right)

    assert c.call("/api/solution", {"key": ex["key"]})[0] == 400  # try once first
    _, a = c.call("/api/answer", {"key": ex["key"], "answer": wrong})
    assert a["correct"] is False and a["state"]["wrong"] == [wrong]
    clue = c.wait(c.call("/api/clue", {"key": ex["key"]})[1]["ticket"])
    assert clue["kind"] == "clue"
    _, a = c.call("/api/answer", {"key": ex["key"], "answer": right})
    assert a["correct"] and a["status"] == "done"

    # Second homework exercise: ask the solution, then a right answer doesn't count.
    _, ex2 = c.call("/api/exercise?key=demo-arithmetic/e02&mode=homework&assignment_id=hw1")
    right2 = json.loads(exercise.read_text())["exercises"][1]["answer"]
    wrong2 = next(k for k in ex2["options"] if k != right2)
    c.call("/api/answer", {"key": ex2["key"], "answer": wrong2})
    sol = c.wait(c.call("/api/solution", {"key": ex2["key"]})[1]["ticket"])
    assert sol["answer"] == right2
    _, a = c.call("/api/answer", {"key": ex2["key"], "answer": right2})
    assert a["correct"] and a["counts"] is False and a["status"] == "with_help"

    # A question with a photo, about the exercise.
    photo = base64.b64encode(b"\xff\xd8fakejpeg").decode()
    reply = c.wait(
        c.call(
            "/api/ask",
            {"key": ex2["key"], "text": "Why?", "photo_b64": photo, "photo_type": "image/jpeg"},
        )[1]["ticket"]
    )
    assert reply["text"]

    # Practice: open one and leave it unsolved.
    c.call("/api/exercise?key=demo-arithmetic/e05&mode=practice")
    c.call("/api/event", {"type": "view_opened", "view": "home"})
    _, home = c.call("/api/home")
    assert home["homework_pending"] == 0
    assert home["continue"]["key"] == "demo-arithmetic/e05"

    # Free mode: next problem, open chat with a suggestion, page hidden and back.
    _, free = c.call("/api/free/next", {})
    assert free["mode"] == "free" and free["path_reason"] == "random"
    for _ in range(2):
        wrong_f = next(k for k in free["options"] if k not in free["state"]["wrong"])
        _, a = c.call("/api/answer", {"key": free["key"], "answer": wrong_f})
        free["state"] = a["state"]
    chat = c.wait(c.call("/api/ask", {"key": None, "text": "give me another"})[1]["ticket"])
    assert chat["suggestions"]
    c.call("/api/event", {"type": "page_hidden"})
    c.call("/api/event", {"type": "page_visible"})
    _, nxt = c.call("/api/free/next", {})
    assert nxt["key"]

    assert c.call("/api/logout", {})[0] == 200
    assert c.call("/api/home")[0] == 401

    files = list((board.root / paths.OUTBOX).glob("*.jsonl"))
    assert len(files) == 1
    types = [e.type for e in read_events(files[0])]
    for expected in (
        "session_start",
        "exercise_shown",
        "answer_submitted",
        "hint_requested",
        "copilot_reply",
        "solution_requested",
        "question_asked",
        "exercise_left",
        "page_hidden",
        "page_visible",
        "session_end",
    ):
        assert expected in types, expected
    events = read_events(files[0])
    asked = next(e for e in events if e.type == "question_asked")
    assert asked.payload["has_photo"] and asked.payload["photo_bytes"] > 0
    assert asked.payload["mode"] == "homework" and asked.payload["assignment_id"] == "hw1"
    assert "photo_b64" not in json.dumps([e.payload for e in events])  # photos aren't stored
    assert events[-1].payload["reason"] == "logout"

    # The teacher app unloads it and links it to the student.
    result = unload.unload(conn, board, tmp_path / "raw")
    assert result.sessions == 1 and not result.errors
    row = conn.execute("SELECT student_id, time_quality FROM sessions").fetchone()
    assert row["student_id"] is not None and row["time_quality"] == "phone"

    # The teacher's stats read the new events without errors.
    from teacher_app.widgets import render_all

    for scope, ref in [("global", None), ("student", row["student_id"]), ("board", board.serial)]:
        for w, data in render_all(conn, scope, ref):
            assert "Error" not in data.get("message", ""), (w.id, data)
    kpis = {
        i["label"]: i["value"]
        for i in render_all(conn, "student", row["student_id"])[0][1]["items"]
    }
    assert kpis["Solutions shown"] == 1 and kpis["Questions"] == 2 and kpis["Clues"] == 1


def test_new_login_ends_previous_session(server, board):
    a, b = _client(server), _client(server)
    code = _code(board)
    a.token = a.call("/api/login", {"code": code})[1]["token"]
    b.token = b.call("/api/login", {"code": code})[1]["token"]
    assert a.call("/api/home")[0] == 401 and b.call("/api/home")[0] == 200
    ended = [
        read_events(f)[-1]
        for f in (board.root / paths.OUTBOX).glob("*.jsonl")
        if read_events(f)[-1].type == "session_end"
    ]
    assert [e.payload["reason"] for e in ended] == ["new_login"]


def test_idle_visit_is_closed(server, board):
    c = _client(server)
    c.token = c.call("/api/login", {"code": _code(board)})[1]["token"]
    server.board.idle_seconds = 0
    time.sleep(0.01)
    assert c.call("/api/home")[0] == 401


def test_the_readable_font_is_served_by_the_board(server):
    c = _client(server)
    for weight in ("Regular", "Bold"):
        url = f"{c.base}/static/fonts/AtkinsonHyperlegible-{weight}.woff2"
        with urllib.request.urlopen(url, timeout=5) as r:
            assert r.headers["Content-Type"] == "font/woff2" and r.read(4) == b"wOF2"
    _, strings = c.call("/api/strings?lang=cat")
    assert strings["a11y_font"] and strings["a11y_easy"]


def test_static_and_media_are_confined(server):
    c = _client(server)
    with urllib.request.urlopen(c.base + "/", timeout=5) as r:
        assert b"app.js" in r.read()
    for bad in (
        "/static/../server.py",
        "/media/demo-arithmetic/../manifest.json",
        "/media/x/y.png",
    ):
        with pytest.raises(urllib.error.HTTPError):
            urllib.request.urlopen(c.base + bad, timeout=5)
