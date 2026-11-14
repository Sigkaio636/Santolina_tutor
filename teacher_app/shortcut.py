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


SHORTCUTS = {
    # file name: (command, name, comment, log file)
    "santolina-teacher.desktop": (
        "serve",
        "Santolina Teacher",
        "Set up the class boards, load exercises and see the students' progress",
        "santolina-teacher.log",
    ),
    "santolina-teacher-demo.desktop": (
        "demo",
        "Santolina Demo",
        "Try the teacher and student apps with a made-up class and simulated boards",
        "santolina-demo.log",
    ),
}


def entry(uv: str, command: str, name: str, comment: str, log: str) -> str:
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
        command,
        "--log-file",
        str(state / log),
    ]
    exec_line = " ".join(_arg(a) for a in args).replace("%", "%%")
    return "\n".join(
        [
            "[Desktop Entry]",
            "Type=Application",
            "Version=1.0",
            f"Name={name}",
            f"Comment={comment}",
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
    written = []
    for file_name, spec in SHORTCUTS.items():
        text = entry(uv, *spec)
        for folder in (Path.home() / ".local" / "share" / "applications", desktop_dir()):
            path = folder / file_name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            path.chmod(0o755)  # desktops only launch executable shortcuts
            # GNOME asks for this before it runs a desktop shortcut. Elsewhere it's a no-op.
            if shutil.which("gio"):
                subprocess.run(
                    ["gio", "set", str(path), "metadata::trusted", "true"],
                    capture_output=True,
                    check=False,
                )
            written.append(path)
    return written
