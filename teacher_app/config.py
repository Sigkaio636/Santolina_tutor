"""Settings of the teacher app. Each one can be changed with an environment variable."""

from dataclasses import dataclass
import os
from pathlib import Path


def _default_home() -> Path:
    base = os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share"
    return Path(base) / "santolina-teacher"


@dataclass
class Settings:
    home: Path  # the database, raw pulls and the pack library live here, never in Git
    port: int
    fake_boards: Path | None  # a folder of simulated boards (tests and demos)
    adb: str  # the adb command

    @property
    def db_path(self) -> Path:
        return self.home / "teacher.sqlite3"

    @property
    def raw_dir(self) -> Path:
        return self.home / "raw"

    @property
    def packs_dir(self) -> Path:
        return self.home / "packs"


def load() -> Settings:
    home = Path(os.environ.get("SANTOLINA_TEACHER_HOME") or _default_home()).expanduser()
    fake = os.environ.get("SANTOLINA_FAKE_BOARDS")
    return Settings(
        home=home,
        port=int(os.environ.get("SANTOLINA_TEACHER_PORT", "8010")),
        fake_boards=Path(fake).expanduser() if fake else None,
        adb=os.environ.get("SANTOLINA_ADB", "adb"),
    )
