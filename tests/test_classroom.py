import json
import os
import time

import pytest

from classroom import paths, status
from classroom.events import EventWriter, is_closed, read_events
from classroom.packs import list_packs, read_pack
from classroom.schemas import (
    ContractError,
    Identity,
    Mode,
    Roster,
    from_dict,
    now_iso,
    read_json,
    to_dict,
    write_json,
)
from teacher_app.simulate import demo_pack


def _identity(root):
    write_json(
        root / paths.IDENTITY,
        Identity("SER1", "Board 1", None, now_iso(), 1, str(root / "none.db")),
    )


def test_round_trip_and_unknown_fields(tmp_path):
    mode = Mode("student", now_iso())
    data = to_dict(mode) | {"future_field": 1}
    assert from_dict(Mode, data) == mode


def test_validation():
    with pytest.raises(ContractError):
        from_dict(Mode, {"mode": "admin", "changed_at": now_iso()})
    with pytest.raises(ContractError):
        from_dict(Roster, {"group_id": 1, "codes": ["bad code"], "updated_at": now_iso()})
    with pytest.raises(ContractError):
        from_dict(Mode, {"schema_version": 99, "mode": "student", "changed_at": now_iso()})


def test_event_writer_and_closed(tmp_path):
    _identity(tmp_path)
    writer = EventWriter.from_root(tmp_path)
    s = writer.start_session("K7M2", client_ts="2026-01-01T10:00:00+00:00")
    s.log("answer_submitted", exercise_id="e1", correct=True)
    assert not is_closed(s.path)
    assert is_closed(s.path, now=time.time() + paths.SESSION_IDLE_SECONDS + 1)
    s.end()
    assert is_closed(s.path)
    events = read_events(s.path)
    assert [e.seq for e in events] == [0, 1, 2]
    assert events[0].payload["client_ts"].startswith("2026-01-01")


def test_truncated_line_is_skipped(tmp_path):
    _identity(tmp_path)
    s = EventWriter.from_root(tmp_path).start_session("K7M2")
    with open(s.path, "a") as f:
        f.write('{"schema_version": 1, "event_id": "x", "sess')
    assert len(read_events(s.path)) == 1


def test_writer_needs_identity(tmp_path):
    with pytest.raises(ContractError):
        EventWriter.from_root(tmp_path)


def test_packs(tmp_path):
    folder = demo_pack(tmp_path / paths.EXERCISES, n=5)
    manifest, exercises = read_pack(folder)
    assert manifest.count == 5 and len(exercises) == 5
    assert [m.pack_id for m in list_packs(tmp_path)] == ["demo-arithmetic"]


def test_status_reads_rag_index(tmp_path):
    from teacher_app.simulate import _fake_index

    _fake_index(tmp_path / "index.db", rows=6)
    _identity(tmp_path)
    write_json(
        tmp_path / paths.IDENTITY,
        read_json(tmp_path / paths.IDENTITY) | {"rag_index_path": str(tmp_path / "index.db")},
    )
    before = os.path.getmtime(tmp_path / "index.db")
    data = status.collect(tmp_path, check_services=False)
    assert data["rag"]["rows"] == 6
    assert data["rag"]["languages"] == {"cat": 3, "eng": 3}
    assert os.path.getmtime(tmp_path / "index.db") == before
    json.dumps(data)  # it must be JSON


def test_find_rag_index_falls_back_to_the_organizers_copy(tmp_path, monkeypatch):
    from classroom import paths

    monkeypatch.setenv("HOME", str(tmp_path))
    assert paths.find_rag_index() == paths.DEFAULT_RAG_INDEX  # none exists: the default
    other = tmp_path / "datathon-UPC-maths-qualcomm-arduino-unoq" / "data" / "index.db"
    other.parent.mkdir(parents=True)
    other.write_bytes(b"")
    assert paths.find_rag_index() == paths.RAG_INDEX_CANDIDATES[1]
