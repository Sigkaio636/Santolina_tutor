import pytest

from teacher_app import db
from teacher_app.links import FakeLink
from teacher_app.simulate import create_fake_boards


@pytest.fixture
def conn(tmp_path):
    c = db.connect(tmp_path / "home" / "teacher.sqlite3")
    yield c
    c.close()


@pytest.fixture
def fake(tmp_path):
    (folder,) = create_fake_boards(tmp_path / "boards", n=1)
    return FakeLink(folder)


@pytest.fixture
def group_with_students(conn):
    with conn:
        gid = conn.execute("INSERT INTO groups (name) VALUES ('3B')").lastrowid
        for name in ("Ada", "Biel", "Carla"):
            conn.execute(
                "INSERT INTO students (group_id, display_name, code) VALUES (?, ?, ?)",
                (gid, name, db.new_student_code(conn)),
            )
    return gid
