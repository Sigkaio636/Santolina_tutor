from fastapi.testclient import TestClient

from teacher_app import config
from teacher_app.simulate import create_fake_boards, simulate_sessions
from teacher_app.web.main import create_app


def test_full_flow_on_a_simulated_board(tmp_path):
    boards_dir = tmp_path / "boards"
    create_fake_boards(boards_dir, n=2)
    settings = config.Settings(
        home=tmp_path / "home", port=0, fake_boards=boards_dir, adb="adb-not-installed"
    )
    client = TestClient(create_app(settings))

    assert client.get("/").status_code == 200
    strip = client.get("/fragments/connected").text
    assert "FAKE0001" in strip and "/setup/FAKE0001" in strip

    client.post("/groups", data={"name": "3B"})
    for name in ("Ada", "Biel"):
        client.post("/students", data={"display_name": name, "group_id": "1"})
    client.post("/packs/demo")

    r = client.post("/setup/FAKE0001", data={"name": "Board 1", "group_id": "1"})
    assert r.status_code == 200 and "Board 1" in r.text and "failed" not in r.text
    assert "/boards/FAKE0001" in client.get("/fragments/connected").text

    r = client.post("/boards/FAKE0001/packs", data={"pack_id": "demo-arithmetic"})
    assert r.status_code == 200 and "loaded" in r.text

    simulate_sessions(boards_dir / "FAKE0001" / "santolina", sessions=6, unknown_rate=0.3, seed=2)
    r = client.post("/boards/FAKE0001/unload")
    assert "6 sessions" in r.text

    r = client.post("/boards/FAKE0001/mode", data={"mode": "professor"})
    assert "professor" in r.text

    for url in (
        "/",
        "/students",
        "/students/1",
        "/groups",
        "/groups/1",
        "/boards",
        "/boards/FAKE0001",
        "/packs",
        "/unassigned",
    ):
        assert client.get(url).status_code == 200, url

    # An unknown board sends you to setup.
    assert client.get("/boards/FAKE0002", follow_redirects=False).status_code == 303


def test_homework_sticker_and_session_pages(tmp_path):
    import json

    from classroom import paths

    boards_dir = tmp_path / "boards"
    create_fake_boards(boards_dir, n=1)
    settings = config.Settings(
        home=tmp_path / "home", port=0, fake_boards=boards_dir, adb="adb-not-installed"
    )
    client = TestClient(create_app(settings))
    client.post("/groups", data={"name": "3B"})
    client.post("/students", data={"display_name": "Ada", "group_id": "1"})
    client.post("/packs/demo")
    client.post("/setup/FAKE0001", data={"name": "Board 1", "group_id": "1"})

    # Homework: choose two exercises; the plugged-in board gets it, and its pack.
    r = client.get(
        "/assignments/new",
        params={
            "pack_id": "demo-arithmetic",
            "group_id": 1,
            "title": "Week 1",
            "due": "2026-12-01",
        },
    )
    assert r.status_code == 200 and 'value="e01"' in r.text
    r = client.post(
        "/assignments",
        data={
            "title": "Week 1",
            "group_id": "1",
            "pack_id": "demo-arithmetic",
            "due": "2026-12-01",
            "exercise_ids": ["e01", "e02"],
        },
    )
    assert "1 connected boards" in r.text
    board_root = boards_dir / "FAKE0001" / "santolina"
    sent = json.loads((board_root / paths.ASSIGNMENTS).read_text())["assignments"]
    assert sent[0]["exercise_ids"] == ["e01", "e02"]
    assert (board_root / paths.EXERCISES / "demo-arithmetic" / "manifest.json").exists()

    # Sticker: QR code, network and password.
    r = client.get("/boards/FAKE0001/sticker")
    hotspot = json.loads((board_root / paths.HOTSPOT).read_text())
    assert "<svg" in r.text and hotspot["password"] in r.text and "Santolina-Board-1" in r.text

    # Simulated sessions, unloaded, then every page renders, including a session timeline.
    simulate_sessions(board_root, sessions=5, seed=4)
    client.post("/boards/FAKE0001/unload")
    from teacher_app import db

    conn = db.connect(settings.db_path)
    session_id = conn.execute("SELECT session_id FROM sessions LIMIT 1").fetchone()[0]
    conn.close()
    for url in (
        "/",
        "/assignments",
        "/students/1",
        "/groups/1",
        "/boards/FAKE0001",
        f"/sessions/{session_id}",
    ):
        r = client.get(url)
        assert r.status_code == 200, url
        assert "Error:" not in r.text, url


def test_students_added_after_setup_reach_the_board(tmp_path):
    import json

    from classroom import paths

    boards_dir = tmp_path / "boards"
    create_fake_boards(boards_dir, n=1)
    settings = config.Settings(
        home=tmp_path / "home", port=0, fake_boards=boards_dir, adb="adb-not-installed"
    )
    client = TestClient(create_app(settings))
    client.post("/groups", data={"name": "Demo"})
    client.post("/setup/FAKE0001", data={"name": "Board 1", "group_id": "1"})
    roster = boards_dir / "FAKE0001" / "santolina" / paths.ROSTER

    def codes():
        return json.loads(roster.read_text())["codes"]

    assert codes() == []
    client.post("/students", data={"display_name": "Ada", "group_id": "1"})
    assert len(codes()) == 1
    client.post("/students/1/group", data={"group_id": ""})
    assert codes() == []
    client.post("/students/1/group", data={"group_id": "1"})
    client.post("/students/1/delete")
    assert codes() == []
