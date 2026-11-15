"""Unload student data from a board into the teacher's database.

1. Measure the board's clock against the laptop's.
2. Pull every closed session file from outbox/ into <home>/raw/<board>/<sync>/.
3. Import its events. An event already in the database is skipped (by event_id),
   so unloading twice imports nothing new.
4. Move the file to archive/ on the board. Nothing is deleted on the board here.

Times: the board's clock can be wrong. A session whose session_start carries the phone's
time (client_ts) is corrected with the phone's offset. Otherwise the offset measured at
this sync is used, and the session is marked 'sync_estimate'.
"""

from dataclasses import dataclass, field
from datetime import timedelta
import json
from pathlib import Path
import time

from classroom import paths
from classroom.events import read_events
from classroom.schemas import now_iso, parse_iso

from . import boards


@dataclass
class UnloadResult:
    sync_id: int
    files_pulled: int = 0
    events_imported: int = 0
    sessions: int = 0
    open_sessions: int = 0
    errors: list = field(default_factory=list)


def _shift(ts: str, offset_s: float) -> str:
    return (parse_iso(ts) - timedelta(seconds=offset_s)).isoformat(timespec="milliseconds")


def session_offset(events, sync_offset: float):
    """(offset in seconds, quality) for one session."""
    for e in events:
        if e.type == "session_start" and e.payload.get("client_ts"):
            try:
                delta = parse_iso(e.ts) - parse_iso(e.payload["client_ts"])
                return delta.total_seconds(), "phone"
            except (ValueError, TypeError):
                break
    return sync_offset, "sync_estimate"


def import_session_file(conn, path: Path, board_id: str, sync_id: int, sync_offset: float):
    """Import one session file. Returns the number of new events."""
    events = read_events(path)
    if not events:
        return 0
    offset, quality = session_offset(events, sync_offset)
    session_id = events[0].session_id
    code = next((e.student_code for e in events if e.student_code), None)
    row = (
        conn.execute("SELECT id FROM students WHERE code = ?", (code,)).fetchone()
        if code
        else None
    )
    student_id = row["id"] if row else None
    started = _shift(events[0].ts, offset)
    ended = _shift(events[-1].ts, offset) if events[-1].type == "session_end" else None
    new = 0
    with conn:
        conn.execute(
            "INSERT INTO sessions (session_id, board_id, student_id, student_code, started_at, "
            "ended_at, time_quality, sync_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(session_id) DO NOTHING",
            (session_id, board_id, student_id, code, started, ended, quality, sync_id),
        )
        for e in events:
            cur = conn.execute(
                "INSERT OR IGNORE INTO events (event_id, session_id, board_id, student_id, seq, "
                "type, ts_raw, ts_corrected, payload_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    e.event_id,
                    session_id,
                    board_id,
                    student_id,
                    e.seq,
                    e.type,
                    e.ts,
                    _shift(e.ts, offset),
                    json.dumps(e.payload, ensure_ascii=False),
                ),
            )
            new += cur.rowcount
    return new


def unload(conn, link, raw_dir: Path) -> UnloadResult:
    board_id = link.serial
    if not boards.get_board(conn, board_id):
        raise ValueError(f"board {board_id} is not registered: set it up first")
    laptop_ts = time.time()
    status = link.status()
    board_ts = status["board_time"]
    offset = board_ts - laptop_ts
    with conn:
        sync_id = conn.execute(
            "INSERT INTO syncs (board_id, at, laptop_ts, board_ts, offset_s) VALUES (?,?,?,?,?)",
            (board_id, now_iso(), laptop_ts, board_ts, offset),
        ).lastrowid
    result = UnloadResult(sync_id=sync_id)
    target = Path(raw_dir) / board_id / f"sync-{sync_id:05d}"
    for item in status.get("outbox", []):
        if not item.get("closed"):
            result.open_sessions += 1
            continue
        name = item["name"]
        local = target / name
        try:
            link.pull(f"{paths.OUTBOX}/{name}", local)
            result.files_pulled += 1
            result.events_imported += import_session_file(conn, local, board_id, sync_id, offset)
            result.sessions += 1
            link.move(f"{paths.OUTBOX}/{name}", f"{paths.ARCHIVE}/{name}")
        except Exception as e:  # noqa: BLE001  (the file stays in outbox/ for the next unload)
            result.errors.append(f"{name}: {type(e).__name__}: {e}")
    with conn:
        conn.execute(
            "UPDATE syncs SET files_pulled = ?, events_imported = ?, raw_dir = ? WHERE id = ?",
            (result.files_pulled, result.events_imported, str(target), sync_id),
        )
    boards.touch(conn, board_id)
    return result


def assign_session(conn, session_id: str, student_id: int) -> None:
    """Link an unassigned session (and its events) to a student."""
    with conn:
        conn.execute(
            "UPDATE sessions SET student_id = ? WHERE session_id = ?", (student_id, session_id)
        )
        conn.execute(
            "UPDATE events SET student_id = ? WHERE session_id = ?", (student_id, session_id)
        )


def assign_code(conn, code: str, student_id: int) -> int:
    """Link every unassigned session with this code to a student. Returns how many."""
    rows = conn.execute(
        "SELECT session_id FROM sessions WHERE student_id IS NULL AND "
        "COALESCE(student_code, '') = ?",
        (code,),
    ).fetchall()
    for r in rows:
        assign_session(conn, r["session_id"], student_id)
    return len(rows)


def clear_archive(link) -> None:
    """Delete the unloaded files on the board. Only on the teacher's explicit request."""
    link.remove(paths.ARCHIVE)
    link.mkdirs(paths.ARCHIVE)
