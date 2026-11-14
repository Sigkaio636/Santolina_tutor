"""A complete demo on the laptop, with no hardware: `python -m teacher_app demo`.

It builds a consistent classroom in its own folder (never your real data):
a group with students, three simulated boards set up for that group, a pack, homework,
and some past sessions already unloaded. Then it starts the teacher app and the student
app of Board 1, which a phone on the same Wi-Fi can open.
"""

from datetime import date, timedelta
import os
from pathlib import Path
import shutil
import socket
import tempfile
import threading
import time
import webbrowser

from . import config, db
from .links import FakeLink
from .services import assignments, packs, setup, unload
from .simulate import create_fake_boards, demo_pack, simulate_sessions

STUDENTS = ["Laia", "Pau", "Marc", "Júlia", "Nil"]
GROUP = "Demo 3B"
BOARDS = 3


def default_home() -> Path:
    base = os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share"
    return Path(base) / "santolina-teacher-demo"


def lan_ip() -> str:
    """This computer's address on the local network (what a phone types)."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            s.connect(("192.0.2.1", 9))  # no packet is sent: this only picks the route
            return s.getsockname()[0]
        except OSError:
            return "127.0.0.1"


def seed(home: Path) -> None:
    """Build the demo classroom from scratch."""
    home.mkdir(parents=True, exist_ok=True)
    conn = db.connect(home / "teacher.sqlite3")
    with conn:
        group_id = conn.execute("INSERT INTO groups (name) VALUES (?)", (GROUP,)).lastrowid
        for name in STUDENTS:
            conn.execute(
                "INSERT INTO students (group_id, display_name, code) VALUES (?, ?, ?)",
                (group_id, name, db.new_student_code(conn)),
            )
    links = [FakeLink(f) for f in create_fake_boards(home / "boards", BOARDS)]
    for i, link in enumerate(links, start=1):
        req = setup.SetupRequest(name=f"Board {i}", group_id=group_id)
        if not setup.run(conn, link, req):
            raise RuntimeError(f"demo setup failed: {req.results[-1]}")
    with tempfile.TemporaryDirectory() as tmp:
        packs.import_pack(conn, demo_pack(Path(tmp), n=15), home / "packs")
    due = (date.today() + timedelta(days=7)).isoformat()
    assignments.create(
        conn, group_id, "Week 1", "demo-arithmetic", ["e01", "e02", "e03", "e04", "e05"], due
    )
    for i, link in enumerate(links, start=1):
        assignments.push(conn, link)  # also loads the pack
        simulate_sessions(link.root, sessions=6, unknown_rate=0.1, seed=i)
        unload.unload(conn, link, home / "raw")
    conn.close()


def student_codes(home: Path) -> list:
    conn = db.connect(home / "teacher.sqlite3")
    rows = conn.execute("SELECT display_name, code FROM students ORDER BY id").fetchall()
    conn.close()
    return [(r["display_name"], r["code"]) for r in rows]


def _port_open(port: int) -> bool:
    with socket.socket() as s:
        s.settimeout(0.3)
        return s.connect_ex(("127.0.0.1", port)) == 0


def run_student_app(root: Path, port: int) -> None:
    """Serve Board 1's student app; start again when the teacher app updates its code."""
    from student_app.server import _watch, make_server

    while True:
        server = make_server(root, "0.0.0.0", port, log_requests=True)
        threading.Thread(target=_watch, args=(server, root, 5), daemon=True).start()
        server.serve_forever()
        server.board.jobs.shutdown()
        server.server_close()
        time.sleep(0.5)


def run(home: Path, reset: bool, teacher_port: int, student_port: int, open_browser: bool):
    import uvicorn

    from .web.main import create_app

    if reset and home.exists():
        shutil.rmtree(home)
    if not (home / "teacher.sqlite3").exists():
        print(f"Building the demo classroom in {home} ...")
        seed(home)

    teacher_url = f"http://127.0.0.1:{teacher_port}"
    student_url = f"http://{lan_ip()}:{student_port}"
    if _port_open(teacher_port) or _port_open(student_port):
        print(f"The demo is already running: {teacher_url} and {student_url}")
        if open_browser:
            webbrowser.open(teacher_url)
        return

    board1 = home / "boards" / "FAKE0001" / "santolina"
    threading.Thread(target=run_student_app, args=(board1, student_port), daemon=True).start()

    print(f"\nTeacher app (demo data): {teacher_url}")
    print(f"Student app of Board 1:  {student_url}  (phone: same Wi-Fi as this computer)")
    print("Student codes: " + ", ".join(f"{n} {c}" for n, c in student_codes(home)))
    if open_browser:

        def open_when_up():
            for _ in range(100):
                if _port_open(teacher_port):
                    webbrowser.open(teacher_url)
                    return
                time.sleep(0.1)

        threading.Thread(target=open_when_up, daemon=True).start()

    settings = config.Settings(
        home=home,
        port=teacher_port,
        fake_boards=home / "boards",
        adb="",  # simulated boards only: a real board plugged in stays out of the demo
        demo_student_url=student_url,
    )
    uvicorn.run(create_app(settings), host="127.0.0.1", port=teacher_port, log_level="warning")
