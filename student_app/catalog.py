"""The exercises on this board: packs, homework assignments, practice topics.

Reloads by itself when the teacher app changes the packs or the assignments.
Answers stay here: `public()` is what the phone may see.
"""

from dataclasses import dataclass
from pathlib import Path
import threading

from classroom import paths
from classroom.packs import read_assignments, read_pack
from classroom.progress import DONE, status
from classroom.schemas import ContractError, Exercise, PackManifest


@dataclass
class Item:
    key: str  # "<pack_id>/<exercise_id>"
    pack: PackManifest
    exercise: Exercise

    @property
    def topic(self):
        return self.exercise.meta.get("topic") if self.exercise.meta else None

    def context(self) -> dict:
        return {
            "pack_id": self.pack.pack_id,
            "exercise_id": self.exercise.exercise_id,
            "level": self.exercise.level,
            "topic": self.topic,
        }


class Catalog:
    def __init__(self, root):
        self.root = paths.board_root(root)
        self._lock = threading.Lock()
        self._signature = None
        self.items: dict = {}
        self.assignments: list = []

    def _current_signature(self):
        files = [self.root / paths.ASSIGNMENTS]
        folder = self.root / paths.EXERCISES
        if folder.is_dir():
            for pack in sorted(folder.iterdir()):
                files += [pack / "manifest.json", pack / "exercises.json"]
        return tuple((str(f), f.stat().st_mtime) if f.exists() else (str(f), 0) for f in files)

    def refresh(self) -> None:
        signature = self._current_signature()
        if signature == self._signature:
            return
        with self._lock:
            items = {}
            folder = self.root / paths.EXERCISES
            if folder.is_dir():
                for pack_dir in sorted(folder.iterdir()):
                    try:
                        manifest, exercises = read_pack(pack_dir)
                    except (ContractError, ValueError, OSError):
                        continue
                    for e in exercises:
                        k = f"{manifest.pack_id}/{e.exercise_id}"
                        items[k] = Item(k, manifest, e)
            self.items = items
            self.assignments = read_assignments(self.root)
            self._signature = signature

    def get(self, key: str) -> Item | None:
        self.refresh()
        return self.items.get(key)

    def media_path(self, pack_id: str, name: str) -> Path | None:
        """A media file only when an exercise of that pack lists it."""
        self.refresh()
        wanted = f"media/{name}"
        for item in self.items.values():
            if item.pack.pack_id == pack_id and wanted in (item.exercise.media or []):
                path = self.root / paths.EXERCISES / pack_id / wanted
                return path if path.is_file() else None
        return None

    def public(self, item: Item, with_answer: bool = False) -> dict:
        e = item.exercise
        data = {
            "key": item.key,
            "pack_id": item.pack.pack_id,
            "pack_title": item.pack.title,
            "exercise_id": e.exercise_id,
            "kind": e.kind,
            "language": e.language,
            "level": e.level,
            "topic": item.topic,
            "prompt": e.prompt,
            "options": e.options or {},
            "images": [f"/media/{item.pack.pack_id}/{m.split('/', 1)[-1]}" for m in e.media or []],
        }
        if with_answer:
            data["answer"] = e.answer
        return data

    def summary(self, item: Item, progress: dict) -> dict:
        prompt = item.exercise.prompt.strip().replace("\n", " ")
        return {
            "key": item.key,
            "title": prompt[:90] + ("…" if len(prompt) > 90 else ""),
            "level": item.exercise.level,
            "topic": item.topic,
            "status": status(progress, item.pack.pack_id, item.exercise.exercise_id),
        }

    def homework(self, progress: dict) -> list:
        self.refresh()
        out = []
        for a in self.assignments:
            keys = (
                [f"{a.pack_id}/{x}" for x in a.exercise_ids]
                if a.exercise_ids
                else [k for k, i in self.items.items() if i.pack.pack_id == a.pack_id]
            )
            exercises = [self.summary(self.items[k], progress) for k in keys if k in self.items]
            pending = sum(1 for x in exercises if x["status"] not in DONE)
            out.append(
                {
                    "assignment_id": a.assignment_id,
                    "title": a.title,
                    "due": a.due,
                    "exercises": exercises,
                    "pending": pending,
                }
            )
        out.sort(key=lambda x: (x["pending"] == 0, x["due"] or "9999"))
        return out

    def topics(self, progress: dict, level_label: str = "Level {level}") -> list:
        """Practice groups: by meta.topic, then by level for exercises without a topic."""
        self.refresh()
        groups: dict = {}
        for item in self.items.values():
            if item.topic:
                name, sort = item.topic, (0, item.topic.lower())
            else:
                level = item.exercise.level
                name = level_label.format(level=level if level is not None else "?")
                sort = (1, level if level is not None else 99)
            group = groups.setdefault(name, {"topic": name, "sort": sort, "exercises": []})
            group["exercises"].append(self.summary(item, progress))
        out = sorted(groups.values(), key=lambda g: g["sort"])
        for g in out:
            del g["sort"]
            g["exercises"].sort(key=lambda x: x["level"] if x["level"] is not None else 99)
            g["done"] = sum(1 for x in g["exercises"] if x["status"] in DONE)
        return out
