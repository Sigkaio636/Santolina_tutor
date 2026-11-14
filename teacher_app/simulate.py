"""Synthetic boards, packs and student sessions, for tests and demos without hardware.

Everything here is made up. No M3Kang content.
"""

from array import array
from datetime import UTC, datetime, timedelta
import json
from pathlib import Path
import random
import sqlite3

from classroom import paths
from classroom.events import EventWriter
from classroom.packs import list_packs, read_pack, write_pack
from classroom.schemas import Exercise, PackManifest, now_iso, read_json

QUESTIONS = [
    "I don't understand the question",
    "What does this word mean?",
    "Can you explain it with an example?",
    "Why is my answer wrong?",
    "Where do I start?",
]


def create_fake_boards(folder: Path, n: int = 3, start: int = 1) -> list:
    """Create n simulated boards, each with a small synthetic retrieval index."""
    folder = Path(folder)
    made = []
    for i in range(start, start + n):
        board = folder / f"FAKE{i:04d}"
        (board / "santolina").mkdir(parents=True, exist_ok=True)
        (board / "fake.json").write_text(
            json.dumps({"model": "Arduino SA,Imola", "services_up": True})
        )
        _fake_index(board / "index.db")
        made.append(board)
    return made


def _fake_index(path: Path, rows: int = 20) -> None:
    """Same table as copilot/rag.py, with made-up problems and zero vectors."""
    if path.exists():
        return
    db = sqlite3.connect(path)
    db.execute(
        "CREATE TABLE problems (key TEXT PRIMARY KEY, problem TEXT NOT NULL, vec BLOB NOT NULL)"
    )
    for i in range(rows):
        lang = "eng" if i % 2 else "cat"
        problem = {"id": f"synthetic-{i}", "language": lang, "text": f"Synthetic problem {i}"}
        db.execute(
            "INSERT INTO problems VALUES (?, ?, ?)",
            (f"synthetic-{i}|{lang}", json.dumps(problem), array("f", [0.0] * 384).tobytes()),
        )
    db.commit()
    db.close()


def demo_pack(folder: Path, pack_id: str = "demo-arithmetic", n: int = 12, version: int = 1):
    """A synthetic multiple-choice arithmetic pack."""
    rng = random.Random(pack_id)
    exercises = []
    for i in range(1, n + 1):
        a, b = rng.randint(2, 20 * (1 + i // 4)), rng.randint(2, 12)
        right = a * b
        wrong = {right + d for d in (-b, b, 1, -1, 10)} - {right}
        values = [right] + rng.sample(sorted(wrong), 4)
        rng.shuffle(values)
        letters = "ABCDE"
        exercises.append(
            Exercise(
                exercise_id=f"e{i:02d}",
                kind="multiple_choice",
                language="eng",
                level=min(5, i // 3),
                prompt=f"What is {a} × {b}?",
                options={letters[k]: str(v) for k, v in enumerate(values)},
                answer=letters[values.index(right)],
                meta={"source": "synthetic"},
            )
        )
    manifest = PackManifest(
        pack_id=pack_id,
        title="Demo: multiplication",
        version=version,
        language="eng",
        created_at=now_iso(),
        count=len(exercises),
        description="Synthetic exercises for trying the teacher app.",
    )
    return write_pack(Path(folder) / pack_id, manifest, exercises)


def simulate_sessions(
    root: Path,
    sessions: int = 10,
    unknown_rate: float = 0.1,
    open_sessions: int = 0,
    seed: int | None = None,
) -> int:
    """Write synthetic student sessions into a board's outbox, as the student UI would.

    Uses the roster and packs on the board. Some sessions use a code the teacher doesn't
    know, to fill the unassigned queue. Returns the number of sessions written.
    """
    rng = random.Random(seed)
    root = Path(root)
    writer = EventWriter.from_root(root)
    roster = read_json(root / paths.ROSTER) or {}
    codes = roster.get("codes") or []
    assignments = (read_json(root / paths.ASSIGNMENTS) or {}).get("assignments", [])
    exercises = []
    for manifest in list_packs(root):
        _, items = read_pack(root / paths.EXERCISES / manifest.pack_id)
        exercises += [(manifest.pack_id, e) for e in items]
    if not exercises:
        exercises = [("none", Exercise(f"x{i}", "open", "eng", i % 5, "?")) for i in range(5)]
    skill = {c: rng.uniform(0.3, 0.9) for c in codes}
    phone_skew = timedelta(seconds=rng.uniform(-3 * 86400, 3 * 86400))  # a wrong board clock
    for k in range(sessions + open_sessions):
        if codes and rng.random() > unknown_rate:
            code = rng.choice(codes)
        else:
            code = "ZZ" + "".join(rng.choice("ABCDEFGH") for _ in range(2))
        client = datetime.now(UTC) - timedelta(days=rng.randint(0, 13)) - phone_skew
        session = writer.start_session(code, client_ts=client.isoformat(timespec="seconds"))
        mode = rng.choice(["homework", "practice", "free"])
        homework = [a for a in assignments if a.get("pack_id")]
        assignment = rng.choice(homework) if mode == "homework" and homework else None
        if mode == "homework" and not assignment:
            mode = "practice"
        for pack_id, ex in rng.sample(exercises, min(len(exercises), rng.randint(2, 6))):
            ctx = {
                "mode": mode,
                "assignment_id": assignment["assignment_id"] if assignment else None,
                "pack_id": pack_id,
                "exercise_id": ex.exercise_id,
                "level": ex.level,
                "topic": (ex.meta or {}).get("topic"),
            }
            session.log("exercise_shown", **ctx)
            p = max(0.05, skill.get(code, 0.5) - 0.08 * (ex.level or 0))
            options = sorted((ex.options or {"A": ""}).keys())
            wrong, hints, helped, seconds = [], 0, False, 0.0
            for attempt in range(1, rng.randint(1, 4) + 1):
                if rng.random() < 0.3:
                    hints += 1
                    session.log("hint_requested", **ctx, hint_number=hints)
                    session.log("copilot_reply", **ctx, text="(clue)", seconds=1.2, kind="clue")
                if rng.random() < 0.15:
                    question = rng.choice(QUESTIONS)
                    session.log("question_asked", **ctx, text=question, has_photo=False)
                    session.log("copilot_reply", **ctx, text="(reply)", seconds=2.5, kind="chat")
                if attempt > 1 and not helped and rng.random() < 0.25:
                    helped = True
                    session.log("solution_requested", **ctx, attempts_before=attempt - 1)
                correct = helped or rng.random() < p
                left = [o for o in options if o not in wrong and o != ex.answer] or options
                answer = ex.answer if correct and ex.answer else rng.choice(left)
                seconds += rng.uniform(15, 90)
                session.log(
                    "answer_submitted",
                    **ctx,
                    answer=answer,
                    correct=bool(correct),
                    attempt=attempt,
                    seconds_since_shown=round(seconds, 1),
                    with_help=helped,
                )
                if correct:
                    break
                wrong.append(answer)
            else:
                session.log("exercise_left", **ctx, seconds=round(seconds, 1), attempts=attempt)
        if k < sessions:
            session.end(reason="logout")
    return sessions + open_sessions
