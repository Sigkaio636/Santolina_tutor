import json

from classroom import paths
from teacher_app import db, demo


def test_demo_classroom_is_consistent(tmp_path):
    demo.seed(tmp_path)
    codes = {c for _, c in demo.student_codes(tmp_path)}
    assert len(codes) == len(demo.STUDENTS)
    conn = db.connect(tmp_path / "teacher.sqlite3")
    assert conn.execute("SELECT COUNT(*) FROM boards").fetchone()[0] == demo.BOARDS
    assert conn.execute("SELECT COUNT(*) FROM sessions WHERE student_id IS NOT NULL").fetchone()[0]
    for board in sorted((tmp_path / "boards").iterdir()):
        root = board / "santolina"
        assert set(json.loads((root / paths.ROSTER).read_text())["codes"]) == codes
        assert json.loads((root / paths.ASSIGNMENTS).read_text())["assignments"]
        assert (root / paths.EXERCISES / "demo-arithmetic").is_dir()
    conn.close()
