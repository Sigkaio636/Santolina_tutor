"""The teacher app's web pages, served on localhost only."""

from datetime import UTC, datetime
import json
from pathlib import Path
import tempfile
from urllib.parse import quote

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from classroom.packs import read_pack

from .. import config, db, links
from ..services import assignments, boards, hotspot, packs, setup, unload
from ..simulate import demo_pack
from ..strings import S
from ..widgets import render_all

HERE = Path(__file__).parent


def _bytes(n) -> str:
    n = float(n or 0)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
    return ""


def _when(value) -> str:
    if value in (None, ""):
        return S.never
    if isinstance(value, (int, float)):
        value = datetime.fromtimestamp(value, UTC).isoformat()
    return str(value)[:16].replace("T", " ")


def create_app(settings: config.Settings | None = None) -> FastAPI:
    settings = settings or config.load()
    db.connect(settings.db_path).close()  # create or migrate the database once
    app = FastAPI(title=S.app_name, docs_url=None, redoc_url=None)
    app.mount("/static", StaticFiles(directory=HERE / "static"), name="static")
    templates = Jinja2Templates(directory=HERE / "templates")
    templates.env.globals.update(S=S, demo_url=settings.demo_student_url, demo_qr=None)
    if settings.demo_student_url:
        templates.env.globals["demo_qr"] = hotspot.qr_svg(settings.demo_student_url, scale=4)
    templates.env.filters.update(bytes=_bytes, when=_when, tojson_compact=json.dumps)

    def get_conn():
        conn = db.connect(settings.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def page(request, name, **ctx):
        ctx.setdefault("msg", request.query_params.get("msg"))
        ctx.setdefault("err", request.query_params.get("err"))
        return templates.TemplateResponse(request, name, ctx)

    def back(url, msg=None, err=None):
        if msg:
            url += ("&" if "?" in url else "?") + "msg=" + quote(msg)
        if err:
            url += ("&" if "?" in url else "?") + "err=" + quote(err)
        return RedirectResponse(url, status_code=303)

    def link_or_404(serial):
        link = links.find(settings, serial)
        if link is None:
            raise HTTPException(409, S.board_not_connected)
        return link

    def groups_list(conn):
        return conn.execute("SELECT * FROM groups ORDER BY name").fetchall()

    # ---------------------------------------------------------------- dashboard
    @app.get("/", response_class=HTMLResponse)
    def dashboard(request: Request, conn=Depends(get_conn)):
        return page(request, "dashboard.html", widgets=render_all(conn, "global"))

    @app.get("/fragments/connected", response_class=HTMLResponse)
    def connected(request: Request, conn=Depends(get_conn)):
        items = []
        for c in links.connected(settings):
            board = boards.get_board(conn, c.serial)
            items.append({"c": c, "board": board})
        return page(request, "_connected.html", items=items)

    # ---------------------------------------------------------------- groups
    @app.get("/groups", response_class=HTMLResponse)
    def groups_page(request: Request, conn=Depends(get_conn)):
        rows = conn.execute(
            "SELECT g.*, (SELECT COUNT(*) FROM students s WHERE s.group_id = g.id) n_students, "
            "(SELECT COUNT(*) FROM boards b WHERE b.group_id = g.id) n_boards "
            "FROM groups g ORDER BY g.name"
        ).fetchall()
        return page(request, "groups.html", groups=rows)

    @app.post("/groups")
    def groups_add(name: str = Form(...), conn=Depends(get_conn)):
        name = name.strip()
        if not name:
            return back("/groups", err=S.groups_name)
        with conn:
            conn.execute("INSERT OR IGNORE INTO groups (name) VALUES (?)", (name,))
        return back("/groups")

    @app.get("/groups/{group_id}", response_class=HTMLResponse)
    def group_page(request: Request, group_id: int, conn=Depends(get_conn)):
        group = conn.execute("SELECT * FROM groups WHERE id = ?", (group_id,)).fetchone()
        if not group:
            raise HTTPException(404)
        return page(
            request, "group.html", group=group, widgets=render_all(conn, "group", group_id)
        )

    # ---------------------------------------------------------------- students
    @app.get("/students", response_class=HTMLResponse)
    def students_page(request: Request, conn=Depends(get_conn)):
        rows = conn.execute(
            "SELECT s.*, g.name group_name, "
            "(SELECT COUNT(*) FROM sessions x WHERE x.student_id = s.id) n_sessions "
            "FROM students s LEFT JOIN groups g ON g.id = s.group_id "
            "ORDER BY g.name, s.display_name"
        ).fetchall()
        return page(request, "students.html", students=rows, groups=groups_list(conn))

    @app.post("/students")
    def students_add(
        display_name: str = Form(...),
        group_id: str = Form(""),
        notes: str = Form(""),
        conn=Depends(get_conn),
    ):
        if not display_name.strip():
            return back("/students", err=S.students_name)
        with conn:
            conn.execute(
                "INSERT INTO students (group_id, display_name, code, notes) VALUES (?, ?, ?, ?)",
                (
                    int(group_id) if group_id else None,
                    display_name.strip(),
                    db.new_student_code(conn),
                    notes.strip(),
                ),
            )
        return back("/students")

    @app.get("/students/{student_id}", response_class=HTMLResponse)
    def student_page(request: Request, student_id: int, conn=Depends(get_conn)):
        student = conn.execute(
            "SELECT s.*, g.name group_name FROM students s "
            "LEFT JOIN groups g ON g.id = s.group_id WHERE s.id = ?",
            (student_id,),
        ).fetchone()
        if not student:
            raise HTTPException(404)
        sessions = conn.execute(
            "SELECT x.*, b.name board_name, "
            "(SELECT COUNT(*) FROM events e WHERE e.session_id = x.session_id "
            " AND e.type = 'answer_submitted') answers "
            "FROM sessions x LEFT JOIN boards b ON b.board_id = x.board_id "
            "WHERE x.student_id = ? ORDER BY x.started_at DESC LIMIT 100",
            (student_id,),
        ).fetchall()
        return page(
            request,
            "student.html",
            student=student,
            sessions=sessions,
            groups=groups_list(conn),
            widgets=render_all(conn, "student", student_id),
        )

    @app.get("/sessions/{session_id}", response_class=HTMLResponse)
    def session_page(request: Request, session_id: str, conn=Depends(get_conn)):
        session = conn.execute(
            "SELECT x.*, b.name board_name, s.display_name, s.id sid FROM sessions x "
            "LEFT JOIN boards b ON b.board_id = x.board_id "
            "LEFT JOIN students s ON s.id = x.student_id WHERE x.session_id = ?",
            (session_id,),
        ).fetchone()
        if not session:
            raise HTTPException(404)
        rows = conn.execute(
            "SELECT * FROM events WHERE session_id = ? ORDER BY seq", (session_id,)
        ).fetchall()
        timeline = [
            {"ts": r["ts_corrected"], "type": r["type"], "p": json.loads(r["payload_json"])}
            for r in rows
        ]
        return page(request, "session.html", session=session, timeline=timeline)

    @app.post("/students/{student_id}/group")
    def student_group(student_id: int, group_id: str = Form(""), conn=Depends(get_conn)):
        with conn:
            conn.execute(
                "UPDATE students SET group_id = ? WHERE id = ?",
                (int(group_id) if group_id else None, student_id),
            )
        return back(f"/students/{student_id}")

    @app.post("/students/{student_id}/delete")
    def student_delete(student_id: int, conn=Depends(get_conn)):
        with conn:
            conn.execute(
                "UPDATE sessions SET student_id = NULL WHERE student_id = ?", (student_id,)
            )
            conn.execute("UPDATE events SET student_id = NULL WHERE student_id = ?", (student_id,))
            conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
        return back("/students")

    # ---------------------------------------------------------------- boards
    @app.get("/boards", response_class=HTMLResponse)
    def boards_page(request: Request, conn=Depends(get_conn)):
        rows = conn.execute(
            "SELECT b.*, g.name group_name, (SELECT MAX(at) FROM syncs y "
            "WHERE y.board_id = b.board_id) last_sync FROM boards b "
            "LEFT JOIN groups g ON g.id = b.group_id ORDER BY b.name"
        ).fetchall()
        return page(request, "boards.html", boards=rows)

    @app.get("/boards/{serial}", response_class=HTMLResponse)
    def board_page(request: Request, serial: str, conn=Depends(get_conn)):
        board = boards.get_board(conn, serial)
        if not board:
            if links.find(settings, serial):
                return back(f"/setup/{serial}")
            raise HTTPException(404)
        link = links.find(settings, serial)
        live, live_error = None, None
        if link:
            try:
                live = boards.refresh(conn, link)
                packs.sync_records(conn, serial, live.get("packs", []))
                live["offset"] = live["board_time"] - datetime.now(UTC).timestamp()
                live["waiting"] = [f for f in live["outbox"] if f["closed"]]
                live["open"] = [f for f in live["outbox"] if not f["closed"]]
            except Exception as e:  # noqa: BLE001  (show the board error on the page)
                live_error = f"{type(e).__name__}: {e}"
        syncs = conn.execute(
            "SELECT * FROM syncs WHERE board_id = ? ORDER BY id DESC LIMIT 20", (serial,)
        ).fetchall()
        loaded = conn.execute(
            "SELECT bp.*, p.title FROM board_packs bp LEFT JOIN packs p "
            "ON p.pack_id = bp.pack_id AND p.version = bp.version WHERE bp.board_id = ?",
            (serial,),
        ).fetchall()
        return page(
            request,
            "board.html",
            board=boards.get_board(conn, serial),
            connected=link is not None,
            live=live,
            live_error=live_error,
            syncs=syncs,
            loaded=loaded,
            library=packs.latest(conn),
            groups=groups_list(conn),
            widgets=render_all(conn, "board", serial),
        )

    def board_action(serial, fn, ok_msg):
        try:
            result = fn()
        except HTTPException:
            raise
        except Exception as e:  # noqa: BLE001  (show the error to the teacher)
            return back(f"/boards/{serial}", err=f"{type(e).__name__}: {e}")
        return back(f"/boards/{serial}", msg=ok_msg(result) if callable(ok_msg) else ok_msg)

    @app.post("/boards/{serial}/mode")
    def board_mode(serial: str, mode: str = Form(...), conn=Depends(get_conn)):
        link = link_or_404(serial)
        return board_action(serial, lambda: boards.set_mode(conn, link, mode), f"Mode: {mode}")

    @app.post("/boards/{serial}/group")
    def board_group(serial: str, group_id: str = Form(""), conn=Depends(get_conn)):
        link = link_or_404(serial)
        gid = int(group_id) if group_id else None
        return board_action(serial, lambda: boards.set_group(conn, link, gid), "Group changed")

    @app.post("/boards/{serial}/unload")
    def board_unload(serial: str, conn=Depends(get_conn)):
        link = link_or_404(serial)

        def message(r):
            text = f"{r.sessions} sessions, {r.events_imported} new events unloaded."
            if r.open_sessions:
                text += f" {r.open_sessions} still open, left on the board."
            if r.errors:
                text += " Problems: " + "; ".join(r.errors)
            return text

        return board_action(serial, lambda: unload.unload(conn, link, settings.raw_dir), message)

    @app.post("/boards/{serial}/clear")
    def board_clear(serial: str):
        link = link_or_404(serial)
        return board_action(serial, lambda: unload.clear_archive(link), "Unloaded data deleted")

    @app.post("/boards/{serial}/packs")
    def board_pack_load(serial: str, pack_id: str = Form(...), conn=Depends(get_conn)):
        link = link_or_404(serial)
        return board_action(
            serial, lambda: packs.load_on_board(conn, link, pack_id), f"Pack {pack_id} loaded"
        )

    @app.post("/boards/{serial}/packs/{pack_id}/remove")
    def board_pack_remove(serial: str, pack_id: str, conn=Depends(get_conn)):
        link = link_or_404(serial)
        return board_action(
            serial,
            lambda: packs.remove_from_board(conn, link, pack_id),
            f"Pack {pack_id} removed",
        )

    @app.get("/boards/{serial}/sticker", response_class=HTMLResponse)
    def board_sticker(request: Request, serial: str, conn=Depends(get_conn)):
        board = boards.get_board(conn, serial)
        if not board or not board["hotspot_ssid"]:
            raise HTTPException(404, "Set up the board first")
        qr = hotspot.qr_svg(
            hotspot.wifi_qr_payload(board["hotspot_ssid"], board["hotspot_password"])
        )
        return page(request, "sticker.html", board=board, qr=qr, address=hotspot.ADDRESS)

    # ---------------------------------------------------------------- assignments
    def push_assignments(conn, group_id):
        """Send the group's homework to its boards that are plugged in now."""
        sent = 0
        for c in links.connected(settings):
            board = boards.get_board(conn, c.serial)
            if c.link and board and board["group_id"] == group_id:
                assignments.push(conn, c.link)
                sent += 1
        return sent

    @app.get("/assignments", response_class=HTMLResponse)
    def assignments_page(request: Request, conn=Depends(get_conn)):
        rows = conn.execute(
            "SELECT a.*, g.name group_name, p.title pack_title FROM assignments a "
            "JOIN groups g ON g.id = a.group_id LEFT JOIN (SELECT pack_id, title FROM packs "
            "GROUP BY pack_id) p ON p.pack_id = a.pack_id "
            "ORDER BY g.name, COALESCE(a.due, '9999')"
        ).fetchall()
        items = [
            dict(r)
            | {"n": len(json.loads(r["exercise_ids_json"])) if r["exercise_ids_json"] else None}
            for r in rows
        ]
        return page(
            request,
            "assignments.html",
            assignments=items,
            groups=groups_list(conn),
            library=packs.latest(conn),
            widgets=render_all(conn, "global", None, only=("homework_completion",)),
        )

    @app.get("/assignments/new", response_class=HTMLResponse)
    def assignment_new(
        request: Request,
        pack_id: str,
        group_id: int,
        title: str = "",
        due: str = "",
        conn=Depends(get_conn),
    ):
        row = next((p for p in packs.latest(conn) if p["pack_id"] == pack_id), None)
        if row is None:
            raise HTTPException(404)
        _, exercises = read_pack(Path(row["path"]))
        return page(
            request,
            "assignment_new.html",
            pack=row,
            exercises=exercises,
            group_id=group_id,
            title=title,
            due=due,
        )

    @app.post("/assignments")
    async def assignment_create(request: Request, conn=Depends(get_conn)):
        form = await request.form()
        title = (form.get("title") or "").strip()
        if not title or not form.get("group_id") or not form.get("pack_id"):
            return back("/assignments", err=S.assignments_missing)
        chosen = form.getlist("exercise_ids")
        group_id = int(form["group_id"])
        assignments.create(
            conn, group_id, title, form["pack_id"], chosen or None, form.get("due") or None
        )
        n = push_assignments(conn, group_id)
        return back("/assignments", msg=S.assignments_created.format(n=n))

    @app.post("/assignments/{assignment_id}/delete")
    def assignment_delete(assignment_id: str, conn=Depends(get_conn)):
        row = conn.execute(
            "SELECT group_id FROM assignments WHERE assignment_id = ?", (assignment_id,)
        ).fetchone()
        assignments.delete(conn, assignment_id)
        if row:
            push_assignments(conn, row["group_id"])
        return back("/assignments")

    # ---------------------------------------------------------------- setup
    @app.get("/setup/{serial}", response_class=HTMLResponse)
    def setup_page(request: Request, serial: str, conn=Depends(get_conn)):
        link = link_or_404(serial)
        identity = boards.read_identity(link)
        return page(
            request,
            "setup.html",
            serial=serial,
            kind=link.kind,
            identity=identity,
            groups=groups_list(conn),
            steps=setup.STEPS,
            req=None,
            ok=None,
        )

    @app.post("/setup/{serial}", response_class=HTMLResponse)
    def setup_run(
        request: Request,
        serial: str,
        name: str = Form(""),
        group_id: str = Form(""),
        conn=Depends(get_conn),
    ):
        link = link_or_404(serial)
        req = setup.SetupRequest(name=name.strip(), group_id=int(group_id) if group_id else None)
        ok = setup.run(conn, link, req)
        return page(
            request,
            "setup.html",
            serial=serial,
            kind=link.kind,
            identity=None,
            groups=groups_list(conn),
            steps=setup.STEPS,
            req=req,
            ok=ok,
        )

    # ---------------------------------------------------------------- packs
    @app.get("/packs", response_class=HTMLResponse)
    def packs_page(request: Request, conn=Depends(get_conn)):
        rows = conn.execute(
            "SELECT p.*, (SELECT COUNT(*) FROM board_packs bp WHERE bp.pack_id = p.pack_id "
            "AND bp.version = p.version) n_boards FROM packs p ORDER BY p.title, p.version DESC"
        ).fetchall()
        return page(request, "packs.html", packs=rows)

    @app.post("/packs/import")
    def packs_import(folder: str = Form(...), conn=Depends(get_conn)):
        try:
            m = packs.import_pack(conn, Path(folder).expanduser(), settings.packs_dir)
        except Exception as e:  # noqa: BLE001  (show the error to the teacher)
            return back("/packs", err=f"{type(e).__name__}: {e}")
        return back("/packs", msg=f"Imported {m.title} (v{m.version}, {m.count} exercises)")

    @app.post("/packs/demo")
    def packs_demo(conn=Depends(get_conn)):
        with tempfile.TemporaryDirectory() as tmp:
            m = packs.import_pack(conn, demo_pack(Path(tmp)), settings.packs_dir)
        return back("/packs", msg=f"Imported {m.title}")

    # ---------------------------------------------------------------- unassigned
    @app.get("/unassigned", response_class=HTMLResponse)
    def unassigned_page(request: Request, conn=Depends(get_conn)):
        rows = conn.execute(
            "SELECT COALESCE(student_code, '') code, COUNT(*) n, MIN(started_at) first, "
            "MAX(started_at) last, GROUP_CONCAT(DISTINCT b.name) boards "
            "FROM sessions x LEFT JOIN boards b ON b.board_id = x.board_id "
            "WHERE x.student_id IS NULL GROUP BY code ORDER BY n DESC"
        ).fetchall()
        students = conn.execute(
            "SELECT s.id, s.display_name, s.code, g.name group_name FROM students s "
            "LEFT JOIN groups g ON g.id = s.group_id ORDER BY g.name, s.display_name"
        ).fetchall()
        return page(request, "unassigned.html", rows=rows, students=students)

    @app.post("/unassigned/assign")
    def unassigned_assign(
        code: str = Form(""), student_id: int = Form(...), conn=Depends(get_conn)
    ):
        n = unload.assign_code(conn, code, student_id)
        return back("/unassigned", msg=f"{n} sessions assigned")

    return app
