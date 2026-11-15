"""Exercise packs: a library on the laptop, and copies loaded on boards."""

from dataclasses import asdict
import json
from pathlib import Path
import shutil

from classroom import paths
from classroom.packs import read_pack
from classroom.schemas import now_iso


def import_pack(conn, source: Path, library: Path):
    """Check a pack folder and copy it into the library. Returns its manifest."""
    manifest, _ = read_pack(source)
    dest = Path(library) / manifest.pack_id / f"v{manifest.version}"
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(source, dest)
    with conn:
        conn.execute(
            "INSERT INTO packs (pack_id, version, title, language, count, manifest_json, path) "
            "VALUES (?, ?, ?, ?, ?, ?, ?) ON CONFLICT(pack_id, version) DO UPDATE SET "
            "title = excluded.title, language = excluded.language, count = excluded.count, "
            "manifest_json = excluded.manifest_json, path = excluded.path",
            (
                manifest.pack_id,
                manifest.version,
                manifest.title,
                manifest.language,
                manifest.count,
                json.dumps(asdict(manifest)),
                str(dest),
            ),
        )
    return manifest


def latest(conn):
    """The newest version of every pack in the library."""
    return conn.execute(
        "SELECT p.* FROM packs p JOIN (SELECT pack_id, MAX(version) v FROM packs "
        "GROUP BY pack_id) m ON m.pack_id = p.pack_id AND m.v = p.version ORDER BY p.title"
    ).fetchall()


def load_on_board(conn, link, pack_id: str, version: int | None = None) -> None:
    query = "SELECT * FROM packs WHERE pack_id = ? ORDER BY version DESC"
    rows = conn.execute(query, (pack_id,)).fetchall()
    row = next((r for r in rows if version is None or r["version"] == version), None)
    if row is None:
        raise ValueError(f"pack {pack_id} is not in the library")
    link.push_dir(Path(row["path"]), f"{paths.EXERCISES}/{pack_id}")
    with conn:
        conn.execute(
            "INSERT INTO board_packs (board_id, pack_id, version, loaded_at) VALUES (?,?,?,?) "
            "ON CONFLICT(board_id, pack_id) DO UPDATE SET version = excluded.version, "
            "loaded_at = excluded.loaded_at",
            (link.serial, pack_id, row["version"], now_iso()),
        )


def remove_from_board(conn, link, pack_id: str) -> None:
    link.remove(f"{paths.EXERCISES}/{pack_id}")
    with conn:
        conn.execute(
            "DELETE FROM board_packs WHERE board_id = ? AND pack_id = ?", (link.serial, pack_id)
        )


def sync_records(conn, board_id: str, board_packs: list) -> None:
    """Make board_packs match what the board reports (a pack may be added or removed by hand)."""
    on_board = {p["pack_id"]: p["version"] for p in board_packs}
    with conn:
        for row in conn.execute(
            "SELECT pack_id FROM board_packs WHERE board_id = ?", (board_id,)
        ).fetchall():
            if row["pack_id"] not in on_board:
                conn.execute(
                    "DELETE FROM board_packs WHERE board_id = ? AND pack_id = ?",
                    (board_id, row["pack_id"]),
                )
        for pack_id, version in on_board.items():
            conn.execute(
                "INSERT INTO board_packs (board_id, pack_id, version, loaded_at) "
                "VALUES (?, ?, ?, ?) ON CONFLICT(board_id, pack_id) DO UPDATE SET "
                "version = excluded.version WHERE version != excluded.version",
                (board_id, pack_id, version, now_iso()),
            )
