"""Where things live under the board root (~/santolina/ on a real board)."""

import os
from pathlib import Path

IDENTITY = "identity.json"
MODE = "mode.json"
ROSTER = "roster.json"
EXERCISES = "exercises"
OUTBOX = "outbox"
ARCHIVE = "archive"
LIB = "lib"
ASSIGNMENTS = "assignments.json"
HOTSPOT = "hotspot.json"
PROGRESS = "progress"
VERSION = "lib/VERSION"  # changes when the teacher app pushes new code; the student app restarts

# The copilot's retrieval index, built on the board by build_index.py (see docs/BOARD_SETUP.md).
DEFAULT_RAG_INDEX = "~/Santolina_tutor/data/index.db"
# Where else a board may keep it: the organizers' copy of the repository.
RAG_INDEX_CANDIDATES = (
    DEFAULT_RAG_INDEX,
    "~/datathon-UPC-maths-qualcomm-arduino-unoq/data/index.db",
)


def find_rag_index() -> str:
    """The first retrieval index that exists on this board, else the default path."""
    for candidate in RAG_INDEX_CANDIDATES:
        if Path(candidate).expanduser().is_file():
            return candidate
    return DEFAULT_RAG_INDEX


# A session file that has not changed for this long counts as abandoned, so closed.
SESSION_IDLE_SECONDS = 2 * 60 * 60


def board_root(root=None) -> Path:
    """The board root: an explicit path, $SANTOLINA_ROOT, or ~/santolina."""
    if root is not None:
        return Path(root).expanduser()
    return Path(os.environ.get("SANTOLINA_ROOT", "~/santolina")).expanduser()
