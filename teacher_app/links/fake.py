"""A simulated board: a local folder that looks like a board's home.

<fake_boards>/<serial>/fake.json       {"model": ..., "services_up": true}
<fake_boards>/<serial>/santolina/      the board root
<fake_boards>/<serial>/index.db        a small retrieval index (synthetic)
"""

import json
import os
from pathlib import Path
import shutil

from classroom import status as board_status

from .base import LinkError

UNO_Q_MODEL = "Arduino SA,Imola"


class FakeLink:
    kind = "fake"

    def __init__(self, folder: Path):
        self.folder = Path(folder)
        self.serial = self.folder.name
        self.root = self.folder / "santolina"
        self.default_rag_index_path = str(self.folder / "index.db")

    def _settings(self) -> dict:
        path = self.folder / "fake.json"
        return json.loads(path.read_text()) if path.exists() else {}

    def _path(self, rel: str) -> Path:
        path = (self.root / rel).resolve()
        if not path.is_relative_to(self.root.resolve()):
            raise LinkError(f"path outside the board root: {rel}")
        return path

    def is_uno_q(self) -> bool:
        return self._settings().get("model", UNO_Q_MODEL) == UNO_Q_MODEL

    def read_text(self, rel):
        path = self._path(rel)
        return path.read_text(encoding="utf-8") if path.exists() else None

    def write_text(self, rel, text):
        path = self._path(rel)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_text(text, encoding="utf-8")
        os.replace(tmp, path)

    def push_dir(self, local, rel):
        path = self._path(rel)
        if path.exists():
            shutil.rmtree(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(local, path, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))

    def pull(self, rel, local):
        src = self._path(rel)
        if not src.exists():
            raise LinkError(f"{rel} not found on {self.serial}")
        Path(local).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, local)

    def pull_index(self, path, local):
        src = Path(path).expanduser()
        if not src.is_file():
            raise LinkError(f"{path} not found on {self.serial}")
        Path(local).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, local)

    def move(self, rel_src, rel_dst):
        dst = self._path(rel_dst)
        dst.parent.mkdir(parents=True, exist_ok=True)
        os.replace(self._path(rel_src), dst)

    def remove(self, rel):
        path = self._path(rel)
        if path.is_dir():
            shutil.rmtree(path)
        elif path.exists():
            path.unlink()

    def mkdirs(self, *rels):
        for rel in rels:
            self._path(rel).mkdir(parents=True, exist_ok=True)

    def status(self):
        if not (self.root / "lib" / "classroom").is_dir():
            raise LinkError("classroom is not installed on the board yet")
        data = board_status.collect(self.root, check_services=False)
        identity = data.get("identity") or {}
        if not identity.get("rag_index_path"):
            data["rag"] = board_status.rag_status(self.default_rag_index_path)
        up = self._settings().get("services_up", True)
        data["services"] = {"llm": up, "embed": up}
        return data

    def configure_hotspot(self, ssid, password):
        return f"hotspot {ssid} (simulated)"


def discover(folder: Path) -> list:
    if not folder or not Path(folder).is_dir():
        return []
    return [FakeLink(p) for p in sorted(Path(folder).iterdir()) if (p / "fake.json").exists()]
