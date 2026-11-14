"""Report the state of a board as JSON. The teacher app runs this on the board:

    cd ~/santolina/lib && python3 -m classroom.status --root ~/santolina

It only reads. It opens the retrieval index read-only and never changes it.
"""

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import shutil
import sqlite3
import time
import urllib.request

from . import CONTRACT_VERSION, paths
from .events import is_closed
from .packs import list_packs
from .schemas import ContractError, Identity, Mode, Roster, read_json

DEFAULT_PORTS = {"llm": 8081, "embed": 8082}


def _read(path, cls):
    try:
        record = read_json(path, cls)
        return asdict(record) if record else None
    except (ContractError, ValueError, TypeError) as e:
        return {"error": str(e)}


def _files(folder: Path, now: float, with_closed: bool) -> list:
    if not folder.is_dir():
        return []
    out = []
    for p in sorted(folder.glob("*.jsonl")):
        st = p.stat()
        item = {"name": p.name, "size": st.st_size, "mtime": st.st_mtime}
        if with_closed:
            item["closed"] = is_closed(p, now=now)
        out.append(item)
    return out


def rag_status(index_path) -> dict:
    """Rows, languages, size and time of the retrieval index (copilot/rag.py)."""
    path = Path(index_path).expanduser()
    info = {"path": str(index_path), "exists": path.exists()}
    if not info["exists"]:
        return info
    st = path.stat()
    info.update(size=st.st_size, mtime=st.st_mtime)
    try:
        db = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        try:
            languages = {}
            for (key,) in db.execute("SELECT key FROM problems"):
                lang = key.rsplit("|", 1)[-1] if "|" in key else "?"
                languages[lang] = languages.get(lang, 0) + 1
        finally:
            db.close()
        info.update(rows=sum(languages.values()), languages=languages)
    except sqlite3.Error as e:
        info["error"] = str(e)
    return info


def service_up(port: int, timeout: float = 2.0) -> bool:
    """True when a llama.cpp server answers /health on localhost."""
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=timeout) as r:
            return r.status == 200
    except OSError:
        return False


def collect(root=None, rag_index_path=None, ports=None, check_services=True) -> dict:
    root = paths.board_root(root)
    now = time.time()
    identity = _read(root / paths.IDENTITY, Identity)
    if rag_index_path is None:
        rag_index_path = (identity or {}).get("rag_index_path") or paths.DEFAULT_RAG_INDEX
    disk = shutil.disk_usage(root if root.exists() else root.parent)
    ports = ports or DEFAULT_PORTS
    return {
        "contract_version": CONTRACT_VERSION,
        "board_time": now,
        "root": str(root),
        "identity": identity,
        "mode": _read(root / paths.MODE, Mode),
        "roster": _read(root / paths.ROSTER, Roster),
        "packs": [asdict(m) for m in list_packs(root)],
        "outbox": _files(root / paths.OUTBOX, now, with_closed=True),
        "archive": _files(root / paths.ARCHIVE, now, with_closed=False),
        "disk": {"free": disk.free, "total": disk.total},
        "rag": rag_status(rag_index_path),
        "services": (
            {name: service_up(port) for name, port in ports.items()} if check_services else {}
        ),
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", default=None, help="board root (default ~/santolina)")
    p.add_argument("--no-services", action="store_true", help="skip the model health checks")
    args = p.parse_args()
    print(json.dumps(collect(args.root, check_services=not args.no_services)))


if __name__ == "__main__":
    main()
