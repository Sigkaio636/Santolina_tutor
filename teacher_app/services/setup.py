"""Set up a new board for the classroom, as an ordered list of steps.

The board must already be "ready": App Lab first setup done, and the copilot installed
with board/0*_*.sh (models, services, retrieval index). Steps that would do that from
here are listed but skipped for now, so they can be filled in later.
"""

from dataclasses import dataclass, field

import classroom
from classroom import paths
from classroom.schemas import Identity, now_iso

from . import assignments, boards, hotspot

MIN_FREE_BYTES = 500 * 1024 * 1024


@dataclass
class StepResult:
    key: str
    title: str
    status: str  # "ok", "skipped", "failed"
    message: str = ""


@dataclass
class SetupRequest:
    name: str
    group_id: int | None
    results: list = field(default_factory=list)
    status: dict | None = None
    hotspot: object = None


class StepFailed(Exception):
    pass


def check_device(conn, link, req):
    if not link.is_uno_q():
        raise StepFailed("This device is not an Arduino UNO Q.")
    return f"Arduino UNO Q, serial {link.serial}"


def install_software(conn, link, req):
    return None  # later: install llama.cpp, the models and the services from the laptop


def configure_hotspot(conn, link, req):
    req.hotspot, message = hotspot.ensure(link, req.name)
    return message


def install_contract(conn, link, req):
    boards.push_lib(link)
    return f"contract v{classroom.CONTRACT_VERSION} and student app copied to ~/santolina/lib"


def check_ready(conn, link, req):
    status = link.status()
    req.status = status
    problems = []
    services = status.get("services", {})
    for name in ("llm", "embed"):
        if not services.get(name):
            problems.append(f"the {name} model service does not answer")
    rag = status.get("rag", {})
    if not rag.get("exists"):
        problems.append(f"the retrieval index is missing ({rag.get('path')})")
    elif not rag.get("rows"):
        problems.append("the retrieval index is empty")
    if status.get("disk", {}).get("free", 0) < MIN_FREE_BYTES:
        problems.append("less than 500 MB of free disk")
    if problems:
        raise StepFailed(
            "The board is not ready: " + "; ".join(problems) + ". See docs/BOARD_SETUP.md."
        )
    return f"models up, retrieval index with {rag['rows']} problems"


def write_layout(conn, link, req):
    link.mkdirs(paths.OUTBOX, paths.ARCHIVE, paths.EXERCISES)
    old = boards.read_identity(link)
    boards.write_identity(
        link,
        Identity(
            board_id=link.serial,
            name=req.name,
            group_id=req.group_id,
            setup_at=now_iso(),
            contract_version=classroom.CONTRACT_VERSION,
            rag_index_path=(old.rag_index_path if old else link.default_rag_index_path),
        ),
    )
    return "~/santolina/ written (existing student data kept)"


def register(conn, link, req):
    with conn:
        conn.execute(
            "INSERT INTO boards (board_id, name, group_id, mode, registered_at, last_seen_at, "
            "hotspot_ssid, hotspot_password) VALUES (?, ?, ?, 'student', ?, ?, ?, ?) "
            "ON CONFLICT(board_id) DO UPDATE SET name = excluded.name, "
            "group_id = excluded.group_id, last_seen_at = excluded.last_seen_at, "
            "hotspot_ssid = excluded.hotspot_ssid, hotspot_password = excluded.hotspot_password",
            (
                link.serial,
                req.name,
                req.group_id,
                now_iso(),
                now_iso(),
                req.hotspot.ssid if req.hotspot else None,
                req.hotspot.password if req.hotspot else None,
            ),
        )
    boards.set_mode(conn, link, "student")
    codes = boards.push_roster(conn, link)
    assignments.push(conn, link)
    return f"registered, student mode, {len(codes)} student codes sent"


STEPS = [
    ("check_device", "Check the device", check_device),
    ("install_software", "Install the copilot (later)", install_software),
    ("install_contract", "Copy the board module and the student app", install_contract),
    ("check_ready", "Check the board is ready", check_ready),
    ("write_layout", "Write the board's files", write_layout),
    ("configure_hotspot", "Set up the students' Wi-Fi", configure_hotspot),
    ("register", "Register the board", register),
]


def run(conn, link, req: SetupRequest) -> bool:
    """Run every step in order and stop at the first failure. True when all passed."""
    if not req.name.strip():
        req.results.append(StepResult("input", "Board name", "failed", "Give the board a name."))
        return False
    for key, title, step in STEPS:
        try:
            message = step(conn, link, req)
        except StepFailed as e:
            req.results.append(StepResult(key, title, "failed", str(e)))
            return False
        except Exception as e:  # noqa: BLE001  (a broken board: show the error, keep the app up)
            req.results.append(StepResult(key, title, "failed", f"{type(e).__name__}: {e}"))
            return False
        status = "skipped" if message is None else "ok"
        req.results.append(StepResult(key, title, status, message or ""))
    return True
