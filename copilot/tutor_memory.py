"""Tutor memory: two uses of the bge-small embeddings for the tutor (docs/TUTOR_RESPONSE_TYPES.md).

1. similar_problem(): T4, "a problem like yours". The nearest solved problem at the same level or
   easier, with its hints and solution written offline by large models. No generation on the board,
   so nothing to hallucinate and almost no time.
2. classify_message(): what the student's message is (stuck, concept question, attempt, asks for a
   hint or the solution, manipulation, off topic), by the labels of its nearest labelled examples.
   This is the "decider" of the doc without an extra model.

Both live in one SQLite file (data/tutor_memory.db, built by build_tutor_memory.py). Standard
library only, like the rest of the board code. Vectors come from the embedding server, so build the
file with the same embedding model that answers the queries.
"""
import json
import os
import re
import sqlite3
from array import array
from collections import defaultdict

from .embed import embed

SCHEMA = """
CREATE TABLE IF NOT EXISTS items (
    kind TEXT NOT NULL,      -- 'problem' or 'message'
    key TEXT NOT NULL,       -- problem id, or message number
    label TEXT,              -- message label; NULL for problems
    level INTEGER,           -- problem level; NULL for messages
    payload TEXT NOT NULL,   -- JSON
    vec BLOB NOT NULL,       -- float32, unit length
    PRIMARY KEY (kind, key)
)"""

# Message labels -> the decider labels proposed in docs/TUTOR_RESPONSE_TYPES.md
DOC_LABEL = {
    "stuck": "PRODUCTIVA_ATASCO", "asks_hint": "PRODUCTIVA_ATASCO", "step_question": "PRODUCTIVA_ATASCO",
    "concept": "PRODUCTIVA_CONCEPTO", "attempt": "INTENTO", "asks_solution": "PIDE_SOLUCIÓN",
    "manipulation": "NO_PRODUCTIVA", "off_topic": "NO_PRODUCTIVA",
}


# Rules first (doc: "T7 by request", T9b noise and T9d manipulation are rules, not a model).
# Checked in this order; the first match wins. Everything else goes to the nearest-neighbour vote.
RULES = [
    ("manipulation", re.compile(r"\b(ignore (your|the|all) (rules|instructions)|without (any )?rules|"
                                r"(just|only) (tell me |give me )?the (letter|answer)|teacher said (you|u) can)\b", re.I)),
    ("asks_solution", re.compile(r"\b(full |whole |the )?solution\b|\bsolve it for me\b|\bshow me how\b|"
                                 r"\bstep by step\b|\bi give up\b|\bi quit\b|\bdo it for me\b", re.I)),
    ("asks_hint", re.compile(r"\b(hint|clue|tip|nudge|pista)s?\b", re.I)),
    # T6: the student proposes a value or an option ("is it 24", "i got B", "my answer is 7").
    ("attempt", re.compile(r"\b(is it|i got|i get|i think it'?s|i think the answer|my answer|the answer is|"
                           r"i chose|it'?s|its|so it'?s)\s+(\(?[A-E]\)?(?![a-z])|-?\d)", re.I)),
]


def rule_label(text):
    stripped = text.strip()
    if len(re.sub(r"[^\w]", "", stripped)) < 2:  # empty, "...", "?"
        return "off_topic"
    for label, pattern in RULES:
        if pattern.search(stripped):
            return label
    return None


def problem_text(p):
    """What is embedded for a problem: statement (with figure description) and options."""
    return p["problem"]


def build(db_path, problems=(), messages=(), batch=32):
    """problems: dicts with id, level, problem (+ any payload). messages: dicts with text, label.
    Yields progress counts."""
    db = sqlite3.connect(db_path)
    db.execute(SCHEMA)
    rows = [("problem", p["id"], None, p["level"], p, problem_text(p)) for p in problems]
    rows += [("message", str(i), m["label"], None, m, m["text"]) for i, m in enumerate(messages)]
    for i in range(0, len(rows), batch):
        chunk = rows[i:i + batch]
        vectors = embed([r[5] for r in chunk])
        db.executemany("INSERT OR REPLACE INTO items VALUES (?, ?, ?, ?, ?, ?)", [
            (kind, key, label, level, json.dumps(payload, ensure_ascii=False), array("f", v).tobytes())
            for (kind, key, label, level, payload, _), v in zip(chunk, vectors)])
        db.commit()
        yield min(i + batch, len(rows))
    db.close()


def _dot(a, b):
    return sum(x * y for x, y in zip(a, b))


class TutorMemory:
    def __init__(self, db_path="data/tutor_memory.db"):
        if not os.path.exists(db_path) or os.path.getsize(db_path) == 0:
            raise FileNotFoundError(f"{db_path} not found or empty. Build it: python3 build_tutor_memory.py")
        db = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)  # read-only: never creates a file
        self.problems, self.messages = [], []
        for kind, key, label, level, payload, blob in db.execute("SELECT * FROM items"):
            vec = array("f")
            vec.frombytes(blob)
            if kind == "problem":
                self.problems.append((key, level, json.loads(payload), vec))
            else:
                self.messages.append((label, json.loads(payload)["text"], vec))
        db.close()

    def similar_problem(self, problem, level=None, exclude_id=None, k=1, min_score=0.0):
        """Up to k (score, problem) pairs, most similar first. With a level, only problems at that
        level or easier are considered (T4: an easier analogue); if none, any level."""
        query = embed([problem])[0]
        scored = [(_dot(query, vec), lvl, p) for key, lvl, p, vec in self.problems if key != exclude_id]
        easier = [s for s in scored if level is None or s[1] is None or s[1] <= level]
        pool = easier or scored
        pool.sort(key=lambda s: s[0], reverse=True)
        return [(score, p) for score, _, p in pool[:k] if score >= min_score]

    def classify_message(self, text, k=7):
        """(label, confidence, doc_label): weighted vote of the k nearest labelled messages.
        confidence is the winning label's share of the vote, 0 to 1 (1.0 when a rule decided)."""
        ruled = rule_label(text)
        if ruled:
            return ruled, 1.0, DOC_LABEL.get(ruled)
        query = embed([text])[0]
        near = sorted(((_dot(query, vec), label) for label, _, vec in self.messages), reverse=True)[:k]
        votes = defaultdict(float)
        for score, label in near:
            votes[label] += max(score, 0.0)
        if not votes:
            return None, 0.0, None
        label = max(votes, key=votes.get)
        total = sum(votes.values()) or 1.0
        return label, votes[label] / total, DOC_LABEL.get(label)
