"""The Kangaroo library: copy a board's index and topics, browse, make a pack, give homework.

All problems here are made up. No M3Kang text.
"""

from array import array
import json
import shutil
import sqlite3

from fastapi.testclient import TestClient

import classroom
from classroom import paths
from classroom.packs import read_pack
from teacher_app import config, kangaroo
from teacher_app.links import FakeLink
from teacher_app.simulate import create_fake_boards
from teacher_app.web.main import create_app

PROBLEMS = [
    # (id, language, level, options, text_only, label)
    ("lvl-1_2015_1", "cat", 1, {"A": "1", "B": "2", "C": "3", "D": "4", "E": "5"}, True, "B"),
    ("lvl-1_2015_1", "eng", 1, {"A": "1", "B": "2", "C": "3", "D": "4", "E": "5"}, True, "B"),
    ("lvl-1_2015_2", "cat", 1, {"A": "7", "B": "8", "C": "9", "D": "10", "E": "11"}, True, "D"),
    ("lvl-2_2016_5", "cat", 2, {"A": "x", "B": "y", "C": "z", "D": "w", "E": "v"}, True, "A"),
    ("lvl-2_2016_6", "cat", 2, {}, True, "C"),  # options in a picture: not usable
    ("lvl-3_2017_9", "cat", 3, {"A": "1", "B": "2", "C": "3", "D": "4", "E": "5"}, False, "E"),
]
TOPICS = {
    "lvl-1_2015_1": "arithmetic",
    "lvl-1_2015_2": "arithmetic",
    "lvl-2_2016_5": "logic",
    "lvl-2_2016_6": "logic",
    "lvl-3_2017_9": "geometry",
}


def make_board(tmp_path, with_topics=True):
    """A simulated board whose index holds PROBLEMS, set up enough for status()."""
    (folder,) = create_fake_boards(tmp_path / "boards", n=1)
    link = FakeLink(folder)
    db = sqlite3.connect(link.default_rag_index_path)
    db.execute("DELETE FROM problems")
    for pid, lang, level, options, text_only, label in PROBLEMS:
        problem = {
            "id": pid,
            "language": lang,
            "level": level,
            "year": 2015,
            "text_only": text_only,
            "text": f"Problem {pid} in {lang}.",
            "options": options,
            "label": label,
        }
        db.execute(
            "INSERT INTO problems VALUES (?, ?, ?)",
            (f"{pid}|{lang}", json.dumps(problem), array("f", [1.0, 0.0]).tobytes()),
        )
    db.commit()
    db.close()
    (link.root / "lib").mkdir(parents=True, exist_ok=True)
    shutil.copytree(classroom.__path__[0], link.root / "lib" / "classroom")
    if with_topics:
        lines = [json.dumps({"id": i, "topic": t}) for i, t in TOPICS.items()]
        (link.root / paths.TOPICS).write_text("\n".join(lines) + "\n")
    return link


def test_refresh_copies_index_and_topics(tmp_path):
    link = make_board(tmp_path)
    got = kangaroo.refresh(link, tmp_path / "home")
    assert got == {"problems": 6, "with_topic": 6, "topics_file": True}
    problems = kangaroo.load(tmp_path / "home")
    assert {p["key"] for p in problems if not p["usable"]} == {
        "lvl-2_2016_6|cat",
        "lvl-3_2017_9|cat",
    }


def test_without_topics_the_problems_have_none(tmp_path):
    got = kangaroo.refresh(make_board(tmp_path, with_topics=False), tmp_path / "home")
    assert got["with_topic"] == 0 and got["topics_file"] is False


def test_grid_counts_only_usable_problems_of_a_language(tmp_path):
    kangaroo.refresh(make_board(tmp_path), tmp_path / "home")
    rows = {r["topic"]: r for r in kangaroo.grid(kangaroo.load(tmp_path / "home"), "cat")}
    assert rows["arithmetic"]["cells"][1] == 2 and rows["logic"]["cells"][2] == 1
    assert "geometry" not in rows  # its only problem needs a picture


def test_select_filters(tmp_path):
    kangaroo.refresh(make_board(tmp_path), tmp_path / "home")
    problems = kangaroo.load(tmp_path / "home")
    assert [p["key"] for p in kangaroo.select(problems, "arithmetic", 1, "cat", "2015_2")] == [
        "lvl-1_2015_2|cat"
    ]


def test_a_library_pack_keeps_id_topic_and_answer(tmp_path):
    kangaroo.refresh(make_board(tmp_path), tmp_path / "home")
    problems = kangaroo.load(tmp_path / "home")
    folder = kangaroo.make_pack(
        problems, ["lvl-1_2015_1|cat", "lvl-2_2016_6|cat"], tmp_path / "out", "k1", "Mine"
    )
    manifest, exercises = read_pack(folder)
    assert manifest.count == 1  # the picture-only problem is left out
    e = exercises[0]
    assert e.answer == "B" and e.meta["m3kang_id"] == "lvl-1_2015_1"
    assert e.meta["topic"] == "arithmetic" and e.language == "cat"


def test_library_pages_and_pack_to_homework(tmp_path):
    link = make_board(tmp_path)
    settings = config.Settings(
        home=tmp_path / "home", port=0, fake_boards=tmp_path / "boards", adb="adb-not-installed"
    )
    client = TestClient(create_app(settings))
    assert "is empty" in client.get("/library").text

    r = client.post("/library/refresh", data={"serial": link.serial})
    assert "Copied 6 problems, 6 with a topic." in r.text
    page = client.get("/library?language=cat").text
    assert "arithmetic" in page and "level=1" in page and "Selected for the pack: 0" in page

    page = client.get("/library?language=cat&topic=arithmetic&level=1").text
    assert "lvl-1_2015_2|cat" in page and "lvl-2_2016_5|cat" not in page

    client.post("/groups", data={"name": "3B"})
    r = client.post(
        "/library/pack",
        data={
            "title": "Arithmetic L1",
            "group_id": "1",
            "keys": ["lvl-1_2015_1|cat", "lvl-1_2015_2|cat"],
        },
        follow_redirects=False,
    )
    assert r.status_code == 303 and r.headers["location"].startswith("/assignments/new?pack_id=")
    homework = client.get(r.headers["location"]).text
    assert "Arithmetic L1" in homework and "lvl-1_2015_2_cat" in homework

    r = client.post("/library/pack", data={"title": "", "keys": []})
    assert "Give a title" in r.text


# ---------------------------------------------------------------- no downgrade of board code
def test_an_older_teacher_app_never_replaces_newer_board_code(tmp_path, monkeypatch):
    import student_app
    from teacher_app.services import boards

    link = make_board(tmp_path)
    assert boards.push_lib(link) == "copied"
    assert boards.push_lib(link) == "same"
    assert boards.board_release(link) == student_app.RELEASE

    # The same board plugged into a laptop with older code (no RELEASE, like the stub)
    monkeypatch.setattr(student_app, "RELEASE", 0)
    monkeypatch.setattr(boards, "lib_version", lambda: "older-code")
    before = link.read_text(paths.VERSION)
    assert boards.push_lib(link) == "kept_newer"
    assert link.read_text(paths.VERSION) == before
