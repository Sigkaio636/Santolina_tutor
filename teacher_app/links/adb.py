"""A real board over USB, through adb. `adb shell` logs in as `arduino` with no password."""

import json
from pathlib import Path
import shlex
import shutil
import subprocess
import tempfile

from classroom import paths

from .base import LinkError

UNO_Q_MARKERS = ("Imola", "arduino,imola")


def list_devices(adb: str = "adb") -> list:
    """[(serial, state)] from `adb devices`. State is 'device' when the board is usable."""
    if not shutil.which(adb):
        return []
    try:
        out = subprocess.run(
            [adb, "devices"], capture_output=True, text=True, timeout=10, check=False
        ).stdout
    except (OSError, subprocess.TimeoutExpired):
        return []
    devices = []
    for line in out.splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 2:
            devices.append((parts[0], parts[1]))
    return devices


class AdbLink:
    kind = "adb"
    default_rag_index_path = paths.DEFAULT_RAG_INDEX

    def __init__(self, serial: str, adb: str = "adb"):
        self.serial = serial
        self.adb = adb
        self._root = None

    def _run(self, *args, timeout=120, check=True) -> subprocess.CompletedProcess:
        try:
            result = subprocess.run(
                [self.adb, "-s", self.serial, *args],
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
        except subprocess.TimeoutExpired as e:
            raise LinkError(f"adb timed out: {' '.join(args)}") from e
        if check and result.returncode != 0:
            raise LinkError(f"adb {args[0]} failed: {(result.stderr or result.stdout).strip()}")
        return result

    def _sh(self, command: str, timeout=120, check=True) -> subprocess.CompletedProcess:
        return self._run("shell", command, timeout=timeout, check=check)

    @property
    def root(self) -> str:
        if self._root is None:
            home = self._sh("echo $HOME").stdout.strip()
            if not home.startswith("/"):
                raise LinkError(f"unexpected home folder on the board: {home!r}")
            self._root = f"{home}/santolina"
        return self._root

    def _abs(self, rel: str) -> str:
        if rel.startswith("/") or ".." in Path(rel).parts:
            raise LinkError(f"path outside the board root: {rel}")
        return f"{self.root}/{rel}" if rel else self.root

    def is_uno_q(self) -> bool:
        out = self._sh(
            "cat /proc/device-tree/model /sys/firmware/devicetree/base/compatible 2>/dev/null",
            check=False,
        ).stdout
        return any(marker in out for marker in UNO_Q_MARKERS)

    def read_text(self, rel):
        q = shlex.quote(self._abs(rel))
        result = self._sh(f"if [ -f {q} ]; then cat {q}; else exit 3; fi", check=False)
        if result.returncode == 3:
            return None
        if result.returncode != 0:
            raise LinkError(f"cannot read {rel}: {result.stderr.strip()}")
        return result.stdout

    def write_text(self, rel, text):
        dst = self._abs(rel)
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as f:
            f.write(text)
            local = f.name
        try:
            self._sh(f"mkdir -p {shlex.quote(str(Path(dst).parent))}")
            self._run("push", local, dst + ".tmp")
            self._sh(f"mv -f {shlex.quote(dst + '.tmp')} {shlex.quote(dst)}")
        finally:
            Path(local).unlink(missing_ok=True)

    def push_dir(self, local, rel):
        dst = self._abs(rel)
        tmp = dst + ".incoming"
        with tempfile.TemporaryDirectory() as staging:
            clean = Path(staging) / Path(dst).name
            shutil.copytree(local, clean, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            self._sh(f"mkdir -p {shlex.quote(str(Path(dst).parent))} && rm -rf {shlex.quote(tmp)}")
            self._run("push", str(clean), tmp, timeout=600)
        self._sh(f"rm -rf {shlex.quote(dst)} && mv {shlex.quote(tmp)} {shlex.quote(dst)}")

    def pull(self, rel, local):
        Path(local).parent.mkdir(parents=True, exist_ok=True)
        self._run("pull", self._abs(rel), str(local), timeout=600)

    def move(self, rel_src, rel_dst):
        src, dst = self._abs(rel_src), self._abs(rel_dst)
        self._sh(
            f"mkdir -p {shlex.quote(str(Path(dst).parent))} && "
            f"mv -f {shlex.quote(src)} {shlex.quote(dst)}"
        )

    def remove(self, rel):
        if not rel:
            raise LinkError("refusing to remove the board root")
        self._sh(f"rm -rf {shlex.quote(self._abs(rel))}")

    def mkdirs(self, *rels):
        self._sh("mkdir -p " + " ".join(shlex.quote(self._abs(r)) for r in rels))

    def status(self):
        root = shlex.quote(self.root)
        result = self._sh(
            f"cd {root}/lib && python3 -B -m classroom.status --root {root}",
            timeout=60,
            check=False,
        )
        if result.returncode != 0:
            raise LinkError(f"board status failed: {result.stderr.strip()[-500:]}")
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as e:
            raise LinkError(f"board status gave no JSON: {result.stdout[:200]!r}") from e
