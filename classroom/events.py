"""Student activity as append-only event files: one file per session in outbox/.

The student interface writes events like this:

    from classroom.events import EventWriter
    writer = EventWriter.from_root()              # reads ~/santolina/identity.json
    session = writer.start_session("K7M2", client_ts="2026-11-14T09:30:00+01:00")
    session.log("exercise_shown", pack_id="demo", exercise_id="e1", level=2)
    session.log("answer_submitted", pack_id="demo", exercise_id="e1", answer="B", correct=True)
    session.end(reason="student_finished")

Each event is written and synced to disk at once, so a power cut loses at most the
line being written. The teacher app pulls only closed sessions: ones that ended, or
that haven't changed for SESSION_IDLE_SECONDS.
"""

import json
import os
from pathlib import Path
import time
import uuid

from . import paths
from .schemas import ContractError, Event, Identity, from_dict, now_iso, read_json, to_dict


class Session:
    def __init__(self, path: Path, board_id: str, session_id: str, student_code):
        self.path = path
        self.board_id = board_id
        self.session_id = session_id
        self.student_code = student_code
        self.seq = 0
        self.ended = False

    def log(self, type: str, **payload) -> Event:
        if self.ended:
            raise ContractError("the session has ended")
        event = Event(
            event_id=uuid.uuid4().hex,
            board_id=self.board_id,
            session_id=self.session_id,
            seq=self.seq,
            student_code=self.student_code,
            ts=now_iso(),
            type=type,
            payload=payload,
        )
        line = json.dumps(to_dict(event), ensure_ascii=False) + "\n"
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(line)
            f.flush()
            os.fsync(f.fileno())
        self.seq += 1
        return event

    def end(self, **payload) -> Event:
        event = self.log("session_end", **payload)
        self.ended = True
        return event


class EventWriter:
    def __init__(self, root, board_id: str):
        self.outbox = paths.board_root(root) / paths.OUTBOX
        self.board_id = board_id

    @classmethod
    def from_root(cls, root=None) -> "EventWriter":
        root = paths.board_root(root)
        identity = read_json(root / paths.IDENTITY, Identity)
        if identity is None:
            raise ContractError(f"{root / paths.IDENTITY} is missing: set up the board first")
        return cls(root, identity.board_id)

    def start_session(self, student_code=None, client_ts=None, **payload) -> Session:
        """Open a new session file and log session_start.

        client_ts is the time on the student's phone (ISO 8601). The board's clock can be
        wrong, so the teacher app uses it to correct the times of the session.
        """
        self.outbox.mkdir(parents=True, exist_ok=True)
        session_id = uuid.uuid4().hex
        session = Session(
            self.outbox / f"{session_id}.jsonl", self.board_id, session_id, student_code
        )
        session.log("session_start", client_ts=client_ts, **payload)
        return session


def read_events(path) -> list:
    """Read the events of one session file.

    A line that doesn't parse is skipped: a power cut can leave half a line at the end.
    """
    events = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(from_dict(Event, json.loads(line)))
            except (json.JSONDecodeError, ContractError, TypeError):
                continue
    return events


def last_event_type(path):
    """The type of the last readable event in a session file, or None."""
    events = read_events(path)
    return events[-1].type if events else None


def is_closed(path, now=None, idle_seconds=paths.SESSION_IDLE_SECONDS) -> bool:
    """A session is closed when it logged session_end or has been idle long enough."""
    path = Path(path)
    if last_event_type(path) == "session_end":
        return True
    now = time.time() if now is None else now
    return now - path.stat().st_mtime >= idle_seconds
