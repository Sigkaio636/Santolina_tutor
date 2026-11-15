"""A retrieval index in SQLite: one solved M3Kang problem per row."""
import json
import os
import sqlite3
from array import array

from .embed import embed
from .llm import format_problem

SCHEMA = """
CREATE TABLE IF NOT EXISTS problems (
    key TEXT PRIMARY KEY,   -- id|language
    problem TEXT NOT NULL,  -- the full problem as JSON
    vec BLOB NOT NULL       -- float32 vector
)"""


def build(db_path, problems, batch=16):
    db = sqlite3.connect(db_path)
    db.execute(SCHEMA)
    for i in range(0, len(problems), batch):
        chunk = problems[i:i + batch]
        vectors = embed([format_problem(p) for p in chunk])
        db.executemany("INSERT OR REPLACE INTO problems VALUES (?, ?, ?)", [
            (f"{p['id']}|{p['language']}", json.dumps(p, ensure_ascii=False), array("f", v).tobytes())
            for p, v in zip(chunk, vectors)])
        db.commit()
        yield min(i + batch, len(problems))
    db.close()


def check(db_path):
    """Return why db_path can't be read as an index, or None if it can."""
    if not os.path.exists(db_path):
        return f"{db_path} not found. Build it first: python3 build_index.py"
    if os.path.getsize(db_path) == 0:
        return f"{db_path} is empty (0 bytes). Build it again: python3 build_index.py"
    return None


class Index:
    """Loads every vector into memory once, so each search is a plain loop."""

    def __init__(self, db_path):
        problem = check(db_path)
        if problem:
            raise FileNotFoundError(problem)
        self.path = db_path
        # Read-only, so a wrong path can never leave an empty index.db behind
        db = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        self.rows = []
        for key, problem, blob in db.execute("SELECT key, problem, vec FROM problems"):
            vec = array("f")
            vec.frombytes(blob)
            self.rows.append((key, json.loads(problem), vec))
        db.close()

    def search(self, problem, k=1, exclude_id=None):
        """Return up to k (score, problem) pairs, most similar first.

        exclude_id skips the same problem in other languages, so validation
        never retrieves its own translation.
        """
        query = embed([format_problem(problem)], query=True)[0]
        if self.rows and len(query) != len(self.rows[0][2]):
            raise ValueError(
                f"the embedding service returns {len(query)} dimensions, but {self.path} "
                f"holds {len(self.rows[0][2])}. Build the index again with the current "
                f"embedding model: python3 build_index.py")
        scored = []
        for _key, stored, vec in self.rows:
            if exclude_id and stored["id"] == exclude_id:
                continue
            scored.append((sum(a * b for a, b in zip(query, vec)), stored))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return scored[:k]
