"""The teacher's local database (SQLite). It is centred on students.

A student belongs to a group and has a pseudonymous code. Boards only ever see the code.
Sessions and events come from boards, and are linked to a student through the code.
Migrations are numbered with PRAGMA user_version: add a new entry to MIGRATIONS,
never edit an old one.
"""

from pathlib import Path
import secrets
import sqlite3

MIGRATIONS = [
    """
    CREATE TABLE groups (
        id          INTEGER PRIMARY KEY,
        name        TEXT NOT NULL UNIQUE,
        created_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
    );
    CREATE TABLE students (
        id            INTEGER PRIMARY KEY,
        group_id      INTEGER REFERENCES groups(id) ON DELETE SET NULL,
        display_name  TEXT NOT NULL,
        code          TEXT NOT NULL UNIQUE,
        notes         TEXT NOT NULL DEFAULT '',
        created_at    TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
    );
    CREATE TABLE boards (
        board_id       TEXT PRIMARY KEY,
        name           TEXT NOT NULL,
        group_id       INTEGER REFERENCES groups(id) ON DELETE SET NULL,
        mode           TEXT NOT NULL DEFAULT 'student',
        registered_at  TEXT NOT NULL,
        last_seen_at   TEXT
    );
    CREATE TABLE syncs (
        id               INTEGER PRIMARY KEY,
        board_id         TEXT NOT NULL REFERENCES boards(board_id),
        at               TEXT NOT NULL,
        laptop_ts        REAL NOT NULL,
        board_ts         REAL NOT NULL,
        offset_s         REAL NOT NULL,   -- board clock minus laptop clock
        files_pulled     INTEGER NOT NULL DEFAULT 0,
        events_imported  INTEGER NOT NULL DEFAULT 0,
        raw_dir          TEXT
    );
    CREATE TABLE packs (
        pack_id        TEXT NOT NULL,
        version        INTEGER NOT NULL,
        title          TEXT NOT NULL,
        language       TEXT NOT NULL,
        count          INTEGER NOT NULL,
        manifest_json  TEXT NOT NULL,
        path           TEXT NOT NULL,
        imported_at    TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
        PRIMARY KEY (pack_id, version)
    );
    CREATE TABLE board_packs (
        board_id   TEXT NOT NULL REFERENCES boards(board_id) ON DELETE CASCADE,
        pack_id    TEXT NOT NULL,
        version    INTEGER NOT NULL,
        loaded_at  TEXT NOT NULL,
        PRIMARY KEY (board_id, pack_id)
    );
    CREATE TABLE sessions (
        session_id    TEXT PRIMARY KEY,
        board_id      TEXT NOT NULL,
        student_id    INTEGER REFERENCES students(id) ON DELETE SET NULL,
        student_code  TEXT,
        started_at    TEXT,              -- corrected time
        ended_at      TEXT,              -- corrected time
        time_quality  TEXT NOT NULL,     -- 'phone' or 'sync_estimate'
        sync_id       INTEGER REFERENCES syncs(id)
    );
    CREATE TABLE events (
        event_id      TEXT PRIMARY KEY,
        session_id    TEXT NOT NULL REFERENCES sessions(session_id),
        board_id      TEXT NOT NULL,
        student_id    INTEGER REFERENCES students(id) ON DELETE SET NULL,
        seq           INTEGER NOT NULL,
        type          TEXT NOT NULL,
        ts_raw        TEXT NOT NULL,     -- the board's clock
        ts_corrected  TEXT NOT NULL,
        payload_json  TEXT NOT NULL
    );
    CREATE INDEX events_student ON events(student_id, ts_corrected);
    CREATE INDEX events_board ON events(board_id, ts_corrected);
    CREATE INDEX events_type ON events(type);
    CREATE INDEX sessions_code ON sessions(student_code) WHERE student_id IS NULL;
    """,
]

# No 0/O or 1/I/L: codes are read aloud and typed on phones.
CODE_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
CODE_LENGTH = 4


def connect(path) -> sqlite3.Connection:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    migrate(conn)
    return conn


def migrate(conn: sqlite3.Connection) -> None:
    version = conn.execute("PRAGMA user_version").fetchone()[0]
    for number, script in enumerate(MIGRATIONS[version:], start=version + 1):
        with conn:
            conn.executescript(script)
            conn.execute(f"PRAGMA user_version = {number}")


def new_student_code(conn: sqlite3.Connection) -> str:
    while True:
        code = "".join(secrets.choice(CODE_ALPHABET) for _ in range(CODE_LENGTH))
        if not conn.execute("SELECT 1 FROM students WHERE code = ?", (code,)).fetchone():
            return code


def group_codes(conn: sqlite3.Connection, group_id) -> list:
    """The student codes of a group: what a board of that group receives as its roster."""
    if group_id is None:
        return []
    rows = conn.execute(
        "SELECT code FROM students WHERE group_id = ? ORDER BY code", (group_id,)
    ).fetchall()
    return [r["code"] for r in rows]
