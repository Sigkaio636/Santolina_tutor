"""Read and change the state of a connected board."""

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


def push_lib(link) -> None:
    """Copy this laptop's classroom package to the board, so both sides share one contract."""
    link.push_dir(Path(classroom.__file__).parent, f"{paths.LIB}/classroom")


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
    push_lib(link)
    if get_board(conn, link.serial):
        push_roster(conn, link)
        touch(conn, link.serial)
    return link.status()
