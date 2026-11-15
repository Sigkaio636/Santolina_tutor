"""The learning path of free mode: which problem comes next. No language model: one step is fast.

The rule looks at how the last problem went and picks the level and the topic of the next:

    last problem                           level   topic    reason
    -------------------------------------  ------  -------  -----------------------
    none yet                               start   any      start
    solved, no wrong answer, no clue       +1      same     harder_after_solve
    ... MASTERY_STREAK times in a row      same    other    new_topic_after_mastery
    solved after a wrong answer or a clue  same    same     same_level_after_help
    failed (2 wrong, or solution asked)    -1      same     easier_after_fail
    skipped                                same    other    other_topic_after_skip

"Same topic" is the nearest problem on the map: the vectors of the retrieval index
(build_index.py), found through meta.m3kang_id. "Other topic" is the problem farthest from
the last ones. An exercise without a vector falls back to meta.topic, then to chance.
The start level is the highest level the student solved at the first try on this board,
else the middle level of the packs.
"""

from array import array
from pathlib import Path
import random
import sqlite3
import statistics

from classroom import paths
from classroom.progress import DONE
from classroom.schemas import read_json

MASTERY_STREAK = 3  # this many clean solves in a row: the topic is mastered
RECENT = 5  # "other topic" means far from this many last problems
NEW_TOPIC = "new_topic_after_mastery"


def load_vectors(path) -> dict:
    """M3Kang id -> vector, from the retrieval index. {} when there is no usable index.

    The English row wins: the embedding model is English, and a problem and its
    translation are the same point on the map.
    """
    path = Path(path).expanduser()
    if not path.is_file():
        return {}
    vectors = {}
    try:
        db = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        try:
            for key, blob in db.execute("SELECT key, vec FROM problems"):
                problem_id, _, language = key.rpartition("|")
                if language == "eng" or problem_id not in vectors:
                    vec = array("f")
                    vec.frombytes(blob)
                    vectors[problem_id] = vec
        finally:
            db.close()
    except (sqlite3.Error, ValueError):
        return {}
    return vectors


def problem_id(item) -> str:
    """The same for a problem and its translations."""
    return (item.exercise.meta or {}).get("m3kang_id") or item.key


class PathPlanner:
    def __init__(self, catalog, vectors: dict | None = None, rng=None):
        self.catalog = catalog
        self.rng = rng or random.Random()
        self._given = vectors
        self._loaded: dict = {}

    def vectors(self) -> dict:
        if self._given is not None:
            return self._given
        if not self._loaded:  # retried until an index exists
            try:
                identity = read_json(self.catalog.root / paths.IDENTITY) or {}
            except (ValueError, OSError):
                identity = {}
            self._loaded = load_vectors(identity.get("rag_index_path") or paths.find_rag_index())
        return self._loaded

    def next(self, history: list, last: dict | None, progress=None, language=None) -> tuple:
        """Returns (key, reason): the next exercise and why (see the table above).

        history: this visit's free-mode problems, oldest first:
            [{"key", "outcome": "solved" | "failed" | "skipped", "reason", "wrong", "hints"}]
        last: history[-1]. progress: the student's classroom.progress data.
        language: the visit's language; exercises in it are preferred.
        """
        self.catalog.refresh()
        items = self.catalog.items
        if not items:
            return None, "empty"
        pool = self._pool(items, history, progress or {}, language)
        last_item = items.get(last["key"]) if last else None
        if last_item is None:
            start = self._start_level(items, pool, progress or {})
            return self.rng.choice(self._at_level(pool, start)).key, "start"

        outcome = last.get("outcome")
        near = True
        if outcome == "failed":
            step, reason = -1, "easier_after_fail"
        elif outcome == "solved" and self._clean(last):
            if self._streak(history) >= MASTERY_STREAK:
                step, reason, near = 0, NEW_TOPIC, False
            else:
                step, reason = 1, "harder_after_solve"
        elif outcome == "solved":
            step, reason = 0, "same_level_after_help"
        else:
            step, reason, near = 0, "other_topic_after_skip", False

        level = last_item.exercise.level
        candidates = self._at_level(pool, None if level is None else level + step)
        if near:
            scores = [self._similarity(c, last_item) for c in candidates]
            best = max(scores)
        else:
            recent = [items[h["key"]] for h in history[-RECENT:] if h["key"] in items]
            scores = [max(self._similarity(c, r) for r in recent) for c in candidates]
            best = min(scores)
        ties = [c for c, s in zip(candidates, scores) if s == best]
        return self.rng.choice(ties).key, reason

    @staticmethod
    def _clean(entry: dict) -> bool:
        return (
            entry.get("outcome") == "solved" and not entry.get("wrong") and not entry.get("hints")
        )

    def _streak(self, history: list) -> int:
        """Clean solves in a row, counted from the last change of topic."""
        n = 0
        for entry in reversed(history):
            if not self._clean(entry):
                break
            n += 1
            if entry.get("reason") == NEW_TOPIC:
                break
        return n

    @staticmethod
    def _pool(items: dict, history: list, progress: dict, language) -> list:
        """Problems not done yet (nor their translations), in the visit's language if any."""
        seen = {h["key"] for h in history}
        done = {k for k, e in progress.get("exercises", {}).items() if e.get("status") in DONE}
        pool = []
        for used_keys in (seen | done, seen, set()):  # when all are done, allow repeats
            used = {problem_id(items[k]) for k in used_keys if k in items}
            pool = [i for i in items.values() if problem_id(i) not in used]
            if pool:
                break
        return [i for i in pool if i.exercise.language == language] or pool

    @staticmethod
    def _start_level(items: dict, pool: list, progress: dict):
        solved = [
            items[k].exercise.level
            for k, e in progress.get("exercises", {}).items()
            if e.get("first_try_correct") and k in items and items[k].exercise.level is not None
        ]
        if solved:
            return max(solved)
        levels = [i.exercise.level for i in pool if i.exercise.level is not None]
        return statistics.median_low(levels) if levels else None

    @staticmethod
    def _at_level(pool: list, target) -> list:
        """The problems of the level nearest to target (the easier one on a tie)."""
        levels = {i.exercise.level for i in pool if i.exercise.level is not None}
        if target is None or not levels:
            return pool
        level = min(levels, key=lambda x: (abs(x - target), x))
        return [i for i in pool if i.exercise.level == level]

    def _similarity(self, a, b) -> float:
        vectors = self.vectors()
        va, vb = vectors.get(problem_id(a)), vectors.get(problem_id(b))
        if va is not None and vb is not None and len(va) == len(vb):
            return sum(x * y for x, y in zip(va, vb))
        if a.topic and b.topic:
            return 1.0 if a.topic == b.topic else 0.0
        return 0.0
