"""Read and change the state of a connected board."""

import hashlib
import json
from pathlib import Path

import classroom
from classroom import paths
from classroom.schemas import (
    ContractError,
    Identity,
    Mode,
    Roster,
    from_dict,
    now_iso,
    to_dict,
)
import student_app

from .. import db


def _dump(record) -> str:
    return json.dumps(to_dict(record), ensure_ascii=False, indent=2)


def read_identity(link) -> Identity | None:
    """The identity a board carries, or None for a board that was never set up."""
    try:
        text = link.read_text(paths.IDENTITY)
        return from_dict(Identity, json.loads(text)) if text else None
    except (ContractError, ValueError, TypeError):
        return None


BOARD_PACKAGES = (classroom, student_app)


def lib_version() -> str:
    """A fingerprint of the code the board runs: it changes only when the code changes."""
    digest = hashlib.sha256()
    for package in BOARD_PACKAGES:
        folder = Path(package.__file__).parent
        for f in sorted(folder.rglob("*")):
            if f.is_file() and "__pycache__" not in f.parts:
                digest.update(str(f.relative_to(folder.parent)).encode())
                digest.update(f.read_bytes())
    return digest.hexdigest()[:16]


def push_lib(link) -> bool:
    """Copy the board packages (contract + student app) when they changed. True if copied.

    Writing lib/VERSION makes a running student app restart with the new code.
    """
    version = lib_version()
    if (link.read_text(paths.VERSION) or "").strip() == version:
        return False
    for package in BOARD_PACKAGES:
        folder = Path(package.__file__).parent
        link.push_dir(folder, f"{paths.LIB}/{folder.name}")
    link.write_text(paths.VERSION, version + "\n")
    return True


def write_identity(link, identity: Identity) -> None:
    link.write_text(paths.IDENTITY, _dump(identity))


def set_mode(conn, link, mode: str) -> None:
    record = Mode(mode=mode, changed_at=now_iso())
    record.check()
    link.write_text(paths.MODE, _dump(record))
    with conn:
        conn.execute("UPDATE boards SET mode = ? WHERE board_id = ?", (mode, link.serial))


def push_roster(conn, link) -> list:
    """Send the codes of the board's group (codes only, never names)."""
    row = conn.execute("SELECT group_id FROM boards WHERE board_id = ?", (link.serial,)).fetchone()
    group_id = row["group_id"] if row else None
    codes = db.group_codes(conn, group_id)
    link.write_text(
        paths.ROSTER, _dump(Roster(group_id=group_id, codes=codes, updated_at=now_iso()))
    )
    return codes


def set_group(conn, link, group_id) -> None:
    """Move a board to another group: update the database, the identity and the roster."""
    with conn:
        conn.execute("UPDATE boards SET group_id = ? WHERE board_id = ?", (group_id, link.serial))
    identity = read_identity(link)
    if identity:
        identity.group_id = group_id
        write_identity(link, identity)
    push_roster(conn, link)


def touch(conn, board_id: str) -> None:
    with conn:
        conn.execute(
            "UPDATE boards SET last_seen_at = ? WHERE board_id = ?", (now_iso(), board_id)
        )


def get_board(conn, board_id: str):
    return conn.execute(
        "SELECT b.*, g.name AS group_name FROM boards b "
        "LEFT JOIN groups g ON g.id = b.group_id WHERE b.board_id = ?",
        (board_id,),
    ).fetchone()


def refresh(conn, link) -> dict:
    """Update the board's copy of the contract and its roster, then return its status."""
    from . import assignments  # assignments uses packs, which doesn't need boards: no cycle

    push_lib(link)
    if get_board(conn, link.serial):
        push_roster(conn, link)
        assignments.push(conn, link)
        touch(conn, link.serial)
    return link.status()
