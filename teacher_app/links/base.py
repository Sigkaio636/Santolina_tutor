"""How the teacher app talks to a board. Paths are relative to the board root (~/santolina).

AdbLink talks to a real board over USB. FakeLink uses a local folder, for tests and demos.
A HotspotLink (the laptop joins the board's Wi-Fi) can implement the same interface later.
"""

from pathlib import Path
from typing import Protocol


class LinkError(RuntimeError):
    """The board didn't do what we asked."""


class BoardLink(Protocol):
    serial: str
    kind: str  # "adb", "fake"

    def is_uno_q(self) -> bool:
        """True when the device is an Arduino UNO Q."""

    def read_text(self, rel: str) -> str | None:
        """The text of a file, or None when it doesn't exist."""

    def write_text(self, rel: str, text: str) -> None:
        """Write a file atomically, creating its folder."""

    def push_dir(self, local: Path, rel: str) -> None:
        """Replace the folder `rel` with a copy of the local folder."""

    def pull(self, rel: str, local: Path) -> None:
        """Copy one file from the board to the laptop."""

    def move(self, rel_src: str, rel_dst: str) -> None:
        """Move a file on the board, creating the destination folder."""

    def remove(self, rel: str) -> None:
        """Delete a file or folder on the board. Missing is fine."""

    def mkdirs(self, *rels: str) -> None:
        """Create folders on the board."""

    def status(self) -> dict:
        """The output of classroom.status on the board (needs lib/ pushed first)."""
