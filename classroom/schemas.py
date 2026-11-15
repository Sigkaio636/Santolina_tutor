"""The records of the board data contract.

Every JSON file and every event carries `schema_version`. Readers ignore fields they
don't know, so a newer writer doesn't break an older reader.
"""

from dataclasses import asdict, dataclass, field, fields
from datetime import UTC, datetime
import json
import os
from pathlib import Path
import re

SCHEMA_VERSION = 1

MODES = ("student", "professor")

# Event types the contract names today. Other types are allowed: payloads are free-form.
# Most events also carry the context: mode (homework | practice | free), assignment_id,
# pack_id, exercise_id, level, topic.
EVENT_TYPES = (
    "session_start",  # client_ts (the phone's clock, ISO 8601), language
    "session_end",  # reason: logout | idle | new_login
    "view_opened",  # view: home | homework | practice | free | exercise
    "exercise_shown",  # path_reason (free mode: see student_app/planner.py, or "suggested")
    "answer_submitted",  # answer, correct (bool), attempt, seconds_since_shown, with_help
    "hint_requested",  # hint_number
    "solution_requested",  # attempts_before
    "question_asked",  # text, has_photo, photo_bytes, photo_type
    "copilot_reply",  # text, seconds, kind: chat | clue | solution, suggestions
    "exercise_left",  # seconds, attempts (left without solving)
    "page_hidden",  # the student switched to another app
    "page_visible",  # seconds_hidden
    "language_changed",  # language
)

PACK_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
STUDENT_CODE_RE = re.compile(r"^[A-Z0-9]{3,12}$")


class ContractError(ValueError):
    """A file on the board doesn't follow the contract."""


def now_iso() -> str:
    """The current time in UTC, ISO 8601, to the millisecond."""
    return datetime.now(UTC).isoformat(timespec="milliseconds")


def parse_iso(value: str) -> datetime:
    """Parse an ISO 8601 time. A time without a zone is taken as UTC."""
    dt = datetime.fromisoformat(value)
    return dt if dt.tzinfo else dt.replace(tzinfo=UTC)


def to_dict(record) -> dict:
    return {"schema_version": SCHEMA_VERSION, **asdict(record)}


def from_dict(cls, data: dict):
    """Build a record from a dict, checking the version and the required fields."""
    if not isinstance(data, dict):
        raise ContractError(f"{cls.__name__}: expected an object")
    version = data.get("schema_version", 1)
    if not isinstance(version, int) or version > SCHEMA_VERSION:
        raise ContractError(f"{cls.__name__}: unsupported schema_version {version!r}")
    known = {f.name for f in fields(cls)}
    record = cls(**{k: v for k, v in data.items() if k in known})
    check = getattr(record, "check", None)
    if check:
        check()
    return record


def write_json(path, record_or_dict) -> None:
    """Write JSON atomically: a temporary file, fsync, then rename."""
    data = record_or_dict if isinstance(record_or_dict, dict) else to_dict(record_or_dict)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def read_json(path, cls=None):
    """Read a JSON file. Returns None when it doesn't exist."""
    path = Path(path)
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return from_dict(cls, data) if cls else data


@dataclass
class Identity:
    board_id: str  # the adb serial
    name: str  # the friendly name written on the board's label
    group_id: int | None
    setup_at: str
    contract_version: int
    rag_index_path: str

    def check(self):
        if not self.board_id or not self.name:
            raise ContractError("Identity: board_id and name are required")


@dataclass
class Mode:
    mode: str
    changed_at: str

    def check(self):
        if self.mode not in MODES:
            raise ContractError(f"Mode: {self.mode!r} is not one of {MODES}")


@dataclass
class Roster:
    group_id: int | None
    codes: list
    updated_at: str

    def check(self):
        bad = [c for c in self.codes if not STUDENT_CODE_RE.match(str(c))]
        if bad:
            raise ContractError(f"Roster: invalid student codes {bad}")


@dataclass
class Exercise:
    exercise_id: str
    kind: str  # e.g. "multiple_choice", "numeric", "open"
    language: str
    level: int | None
    prompt: str
    options: dict | None = None  # {"A": "...", ...}
    answer: str | None = None
    media: list | None = None  # paths relative to the pack folder
    meta: dict = field(default_factory=dict)

    def check(self):
        if not self.exercise_id or not self.prompt:
            raise ContractError("Exercise: exercise_id and prompt are required")


@dataclass
class PackManifest:
    pack_id: str
    title: str
    version: int
    language: str
    created_at: str
    count: int
    description: str = ""

    def check(self):
        if not PACK_ID_RE.match(self.pack_id):
            raise ContractError(f"PackManifest: invalid pack_id {self.pack_id!r}")
        if not isinstance(self.version, int) or self.version < 1:
            raise ContractError("PackManifest: version must be a positive integer")


@dataclass
class Assignment:
    assignment_id: str
    title: str
    pack_id: str
    exercise_ids: list | None  # None: the whole pack
    due: str | None  # ISO date, optional
    created_at: str

    def check(self):
        if not self.assignment_id or not self.pack_id:
            raise ContractError("Assignment: assignment_id and pack_id are required")


@dataclass
class Hotspot:
    ssid: str
    password: str  # WPA2, at least 8 characters

    def check(self):
        if not self.ssid or len(self.password) < 8:
            raise ContractError("Hotspot: ssid and a password of 8+ characters are required")


@dataclass
class Event:
    event_id: str
    board_id: str
    session_id: str
    seq: int
    student_code: str | None
    ts: str  # the board's clock, which can be wrong
    type: str
    payload: dict = field(default_factory=dict)

    def check(self):
        if not self.event_id or not self.session_id or not self.type:
            raise ContractError("Event: event_id, session_id and type are required")
