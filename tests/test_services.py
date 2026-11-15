import json

from classroom import paths
from classroom.events import EventWriter
from teacher_app.services import boards, packs, setup, unload
from teacher_app.simulate import demo_pack, simulate_sessions
from teacher_app.widgets import render_all


def _setup(conn, link, group_id):
    req = setup.SetupRequest(name="Board 7", group_id=group_id)
    ok = setup.run(conn, link, req)
    return ok, req


def test_setup_writes_layout_and_registers(conn, fake, group_with_students):
    ok, req = _setup(conn, fake, group_with_students)
    assert ok, req.results
    assert [r.status for r in req.results].count("skipped") == 1
    hotspot = json.loads(fake.read_text(paths.HOTSPOT))
    assert hotspot["ssid"] == "Santolina-Board-7" and len(hotspot["password"]) == 10
    assert boards.get_board(conn, fake.serial)["hotspot_password"] == hotspot["password"]
    assert (fake.root / "lib" / "student_app" / "server.py").exists()
    assert fake.read_text(paths.VERSION).strip() == boards.lib_version()
    identity = json.loads(fake.read_text(paths.IDENTITY))
    assert identity["name"] == "Board 7"
    assert json.loads(fake.read_text(paths.MODE))["mode"] == "student"
    assert len(json.loads(fake.read_text(paths.ROSTER))["codes"]) == 3
    assert (fake.root / "lib" / "classroom" / "status.py").exists()
    assert boards.get_board(conn, fake.serial)["name"] == "Board 7"


def test_setup_fails_when_not_ready(conn, fake, group_with_students):
    (fake.folder / "fake.json").write_text(json.dumps({"services_up": False}))
    ok, req = _setup(conn, fake, group_with_students)
    assert not ok
    assert req.results[-1].key == "check_ready"
    assert boards.get_board(conn, fake.serial) is None


def test_setup_fails_without_rag_index(conn, fake, group_with_students):
    (fake.folder / "index.db").unlink()
    ok, req = _setup(conn, fake, group_with_students)
    assert not ok and "retrieval index" in req.results[-1].message


def test_setup_again_keeps_the_wifi_password(conn, fake, group_with_students):
    _setup(conn, fake, group_with_students)
    first = json.loads(fake.read_text(paths.HOTSPOT))["password"]
    _setup(conn, fake, group_with_students)
    assert json.loads(fake.read_text(paths.HOTSPOT))["password"] == first


def test_assignments_reach_the_board_with_their_pack(conn, fake, group_with_students, tmp_path):
    from teacher_app.services import assignments

    _setup(conn, fake, group_with_students)
    packs.import_pack(conn, demo_pack(tmp_path / "src", n=4), tmp_path / "library")
    assignments.create(
        conn, group_with_students, "Week 1", "demo-arithmetic", ["e01"], "2026-12-01"
    )
    assert assignments.push(conn, fake) == 1
    data = json.loads(fake.read_text(paths.ASSIGNMENTS))
    assert data["assignments"][0]["exercise_ids"] == ["e01"]
    assert [p["pack_id"] for p in fake.status()["packs"]] == ["demo-arithmetic"]


def test_wifi_qr_payload_escapes():
    from teacher_app.services.hotspot import make_ssid, wifi_qr_payload

    assert make_ssid("Pissarra 3ª B") == "Santolina-Pissarra-3a-B"
    assert wifi_qr_payload("a;b", 'p:"x') == 'WIFI:T:WPA;S:a\\;b;P:p\\:\\"x;;'


def test_setup_keeps_student_data(conn, fake, group_with_students):
    _setup(conn, fake, group_with_students)
    simulate_sessions(fake.root, sessions=2, seed=1)
    _setup(conn, fake, group_with_students)
    assert len(list((fake.root / paths.OUTBOX).glob("*.jsonl"))) == 2


def test_mode_switch(conn, fake, group_with_students):
    _setup(conn, fake, group_with_students)
    boards.set_mode(conn, fake, "professor")
    assert json.loads(fake.read_text(paths.MODE))["mode"] == "professor"
    assert boards.get_board(conn, fake.serial)["mode"] == "professor"


def test_packs_load_and_remove(conn, fake, group_with_students, tmp_path):
    _setup(conn, fake, group_with_students)
    source = demo_pack(tmp_path / "src", n=4)
    packs.import_pack(conn, source, tmp_path / "library")
    packs.load_on_board(conn, fake, "demo-arithmetic")
    assert [p["pack_id"] for p in fake.status()["packs"]] == ["demo-arithmetic"]
    packs.remove_from_board(conn, fake, "demo-arithmetic")
    assert fake.status()["packs"] == []


def test_unload_is_idempotent_and_student_centred(conn, fake, group_with_students, tmp_path):
    _setup(conn, fake, group_with_students)
    simulate_sessions(fake.root, sessions=8, unknown_rate=0.25, open_sessions=1, seed=3)
    first = unload.unload(conn, fake, tmp_path / "raw")
    assert first.sessions == 8 and first.open_sessions == 1 and not first.errors
    assert first.events_imported > 0
    assert len(list((fake.root / paths.ARCHIVE).glob("*.jsonl"))) == 8
    assert len(list((tmp_path / "raw" / fake.serial).rglob("*.jsonl"))) == 8
    # A second unload imports nothing, even if the archived files came back to the outbox.
    for f in (fake.root / paths.ARCHIVE).glob("*.jsonl"):
        f.rename(fake.root / paths.OUTBOX / f.name)
    second = unload.unload(conn, fake, tmp_path / "raw")
    assert second.events_imported == 0
    total = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    assert total == first.events_imported
    # Every session with a known code is linked to a student.
    assert (
        conn.execute(
            "SELECT COUNT(*) FROM sessions s JOIN students t ON t.code = s.student_code "
            "WHERE s.student_id IS NULL"
        ).fetchone()[0]
        == 0
    )


def test_phone_clock_corrects_times(conn, fake, group_with_students, tmp_path):
    _setup(conn, fake, group_with_students)
    code = json.loads(fake.read_text(paths.ROSTER))["codes"][0]
    s = EventWriter.from_root(fake.root).start_session(code, client_ts="2026-03-02T09:00:00+00:00")
    s.end()
    unload.unload(conn, fake, tmp_path / "raw")
    row = conn.execute("SELECT started_at, time_quality FROM sessions").fetchone()
    assert row["time_quality"] == "phone"
    assert row["started_at"].startswith("2026-03-02T09:00")


def test_no_phone_clock_uses_sync_offset(conn, fake, group_with_students, tmp_path):
    _setup(conn, fake, group_with_students)
    EventWriter.from_root(fake.root).start_session(None).end()
    unload.unload(conn, fake, tmp_path / "raw")
    row = conn.execute("SELECT time_quality, student_id FROM sessions").fetchone()
    assert row["time_quality"] == "sync_estimate" and row["student_id"] is None


def test_assign_unknown_code(conn, fake, group_with_students, tmp_path):
    _setup(conn, fake, group_with_students)
    EventWriter.from_root(fake.root).start_session("QQQQ").end()
    unload.unload(conn, fake, tmp_path / "raw")
    student_id = conn.execute("SELECT id FROM students LIMIT 1").fetchone()[0]
    assert unload.assign_code(conn, "QQQQ", student_id) == 1
    assert conn.execute("SELECT COUNT(*) FROM events WHERE student_id IS NULL").fetchone()[0] == 0


def test_widgets_render_in_every_scope(conn, fake, group_with_students, tmp_path):
    _setup(conn, fake, group_with_students)
    packs.import_pack(conn, demo_pack(tmp_path / "src"), tmp_path / "library")
    packs.load_on_board(conn, fake, "demo-arithmetic")
    simulate_sessions(fake.root, sessions=10, seed=5)
    unload.unload(conn, fake, tmp_path / "raw")
    student_id = conn.execute("SELECT id FROM students LIMIT 1").fetchone()[0]
    for scope, ref in [
        ("global", None),
        ("group", group_with_students),
        ("student", student_id),
        ("board", fake.serial),
    ]:
        for w, data in render_all(conn, scope, ref):
            assert "Error" not in data.get("message", ""), (w.id, data)


def test_m3kang_converter_skips_problems_missing_their_image(tmp_path):
    from classroom.packs import read_pack
    from teacher_app.m3kang import convert

    rows = [
        {
            "id": "a",
            "language": "eng",
            "level": 0,
            "text": "t",
            "options": {"A": "1"},
            "label": "A",
            "text_only": True,
        },
        {
            "id": "b",
            "language": "eng",
            "level": 0,
            "text": "t",
            "options": {"A": "1"},
            "label": "A",
            "text_only": False,
        },
        {
            "id": "c",
            "language": "eng",
            "level": 1,
            "text": "t",
            "options": {"A": "1"},
            "label": "A",
            "text_only": False,
            "topic": "geometry",
        },
    ]
    source = tmp_path / "rows.json"  # synthetic rows; JSON lines in a .json name
    source.write_text("\n".join(json.dumps(r) for r in rows))
    images = tmp_path / "images"
    images.mkdir()
    (images / "c_eng.png").write_bytes(b"\x89PNG fake")
    folder = convert(source, tmp_path / "out", "kang", "Kangaroo", images=images)
    _, exercises = read_pack(folder)
    assert [e.exercise_id for e in exercises] == ["a_eng", "c_eng"]
    assert exercises[1].media == ["media/c_eng.png"] and exercises[1].meta["topic"] == "geometry"
    assert (folder / "media" / "c_eng.png").exists()
