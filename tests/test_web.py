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
