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

# The copilot's retrieval index, built on the board by build_index.py (see docs/BOARD_SETUP.md).
DEFAULT_RAG_INDEX = "~/Santolina_tutor/data/index.db"

# A session file that has not changed for this long counts as abandoned, so closed.
SESSION_IDLE_SECONDS = 2 * 60 * 60


def board_root(root=None) -> Path:
    """The board root: an explicit path, $SANTOLINA_ROOT, or ~/santolina."""
    if root is not None:
        return Path(root).expanduser()
    return Path(os.environ.get("SANTOLINA_ROOT", "~/santolina")).expanduser()
