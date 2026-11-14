"""A desktop shortcut (freedesktop .desktop file) that starts the teacher app.

Works on KDE Plasma, GNOME and other Linux desktops. The shortcut runs the app from
this repository with uv, so it keeps working after a `git pull`.
"""

import os
from pathlib import Path
import shutil
import subprocess

REPO = Path(__file__).resolve().parent.parent
ICON = Path(__file__).resolve().parent / "web" / "static" / "icon.svg"
NAME = "santolina-teacher.desktop"


def desktop_dir() -> Path:
    try:
        out = subprocess.run(
            ["xdg-user-dir", "DESKTOP"], capture_output=True, text=True, check=False
        ).stdout.strip()
        if out:
            return Path(out)
    except OSError:
        pass
    return Path.home() / "Desktop"


def _arg(value: str) -> str:
    """Quote one Exec argument as the desktop entry spec asks (double quotes only)."""
    if not any(c in value for c in " \t\n\"'\\><~|&;$*?#()`"):
        return value
    return '"' + "".join("\\" + c if c in '"`$\\' else c for c in value) + '"'


def entry(uv: str) -> str:
    state = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state"))
    args = [
        uv,
        "--directory",
        str(REPO),
        "run",
        "--group",
        "teacher",
        "python",
        "-m",
        "teacher_app",
        "serve",
        "--log-file",
        str(state / "santolina-teacher.log"),
    ]
    exec_line = " ".join(_arg(a) for a in args).replace("%", "%%")
    return "\n".join(
        [
            "[Desktop Entry]",
            "Type=Application",
            "Version=1.0",
            "Name=Santolina Teacher",
            "Comment=Set up the class boards, load exercises and see the students' progress",
            f"Exec={exec_line}",
            f"Icon={ICON}",
            "Terminal=false",
            "Categories=Education;",
            "StartupNotify=false",
            "",
        ]
    )


def install() -> list:
    uv = shutil.which("uv")
    if not uv:
        raise SystemExit("uv was not found. Install it first: https://docs.astral.sh/uv/")
    text = entry(uv)
    targets = [Path.home() / ".local" / "share" / "applications" / NAME, desktop_dir() / NAME]
    written = []
    for path in targets:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        path.chmod(0o755)  # desktops only launch executable shortcuts
        # GNOME asks for this before it runs a shortcut from the desktop. Elsewhere it's a no-op.
        if shutil.which("gio"):
            subprocess.run(
                ["gio", "set", str(path), "metadata::trusted", "true"],
                capture_output=True,
                check=False,
            )
        written.append(path)
    return written
