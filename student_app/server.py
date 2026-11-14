"""The student web server (standard library only).

    python3 -m student_app.server --root ~/santolina --port 80 --public-host 10.42.0.1

--public-host turns on the captive portal: a request for any other host name (phones check
"is there internet?" with their own addresses) is sent to http://<public-host>/, so the
phone opens the page by itself when it joins the board's Wi-Fi.
"""

import argparse
import base64
import binascii
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
from pathlib import Path
import threading
import time
from urllib.parse import parse_qs, urlsplit

from classroom import paths

from .state import Board, Expired, Refused
from .strings import LANGUAGES, strings

STATIC = Path(__file__).parent / "static"
MAX_BODY = 8 * 1024 * 1024  # a phone photo, downscaled by the page, fits easily
CAPTIVE_PROBES = {
    "/generate_204",
    "/gen_204",
    "/hotspot-detect.html",
    "/library/test/success.html",
    "/connecttest.txt",
    "/ncsi.txt",
    "/redirect",
    "/canonical.html",
    "/success.txt",
}
LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}


class Handler(BaseHTTPRequestHandler):
    server_version = "Santolina"
    board: Board = None  # set by make_server
    public_host: str | None = None
    log_requests = False

    def log_message(self, fmt, *args):  # quiet unless asked: the events are the log that matters
        if self.log_requests:
            super().log_message(fmt, *args)

    # ------------------------------------------------------------------ helpers
    def _send(self, status, body: bytes, ctype: str, extra=None):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _json(self, data, status=HTTPStatus.OK):
        self._send(status, json.dumps(data, ensure_ascii=False).encode(), "application/json")

    def _redirect(self, location):
        self._send(HTTPStatus.FOUND, b"", "text/plain", {"Location": location})

    def _file(self, path: Path):
        ctype = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        if ctype.startswith("text/") or ctype == "application/javascript":
            ctype += "; charset=utf-8"
        self._send(HTTPStatus.OK, path.read_bytes(), ctype)

    def _body(self) -> dict:
        length = int(self.headers.get("Content-Length") or 0)
        if length > MAX_BODY:
            raise Refused("too large")
        raw = self.rfile.read(length) if length else b"{}"
        try:
            data = json.loads(raw or b"{}")
        except json.JSONDecodeError as e:
            raise Refused("bad json") from e
        if not isinstance(data, dict):
            raise Refused("bad json")
        return data

    def _visit(self):
        return self.board.check(self.headers.get("X-Session", ""))

    def _captive(self) -> bool:
        """Send phones that probe for internet to our page."""
        if not self.public_host:
            return False
        host = (self.headers.get("Host") or "").rsplit(":", 1)[0].strip("[]").lower()
        path = urlsplit(self.path).path
        if host not in LOCAL_HOSTS | {self.public_host} or path in CAPTIVE_PROBES:
            self._redirect(f"http://{self.public_host}/")
            return True
        return False

    # ------------------------------------------------------------------ routing
    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        if self._captive():
            return
        url = urlsplit(self.path)
        q = {k: v[0] for k, v in parse_qs(url.query).items()}
        try:
            if url.path in ("/", "/index.html"):
                return self._file(STATIC / "index.html")
            if url.path.startswith("/static/"):
                return self._static(url.path[len("/static/") :])
            if url.path.startswith("/media/"):
                return self._media(url.path[len("/media/") :])
            if url.path.startswith("/api/"):
                return self._json(self._get_api(url.path[5:], q))
        except Expired:
            return self._json({"error": "expired"}, HTTPStatus.UNAUTHORIZED)
        except Refused as e:
            return self._json({"error": str(e)}, HTTPStatus.BAD_REQUEST)
        self._send(HTTPStatus.NOT_FOUND, b"not found", "text/plain")

    def do_POST(self):
        if self._captive():
            return
        url = urlsplit(self.path)
        try:
            if not url.path.startswith("/api/"):
                raise Refused("not found")
            return self._json(self._post_api(url.path[5:], self._body()))
        except Expired:
            return self._json({"error": "expired"}, HTTPStatus.UNAUTHORIZED)
        except Refused as e:
            return self._json({"error": str(e)}, HTTPStatus.BAD_REQUEST)

    def _static(self, name: str):
        path = (STATIC / name).resolve()
        if not path.is_relative_to(STATIC.resolve()) or not path.is_file():
            return self._send(HTTPStatus.NOT_FOUND, b"not found", "text/plain")
        return self._file(path)

    def _media(self, rest: str):
        pack_id, _, name = rest.partition("/")
        path = self.board.catalog.media_path(pack_id, name) if name and "/" not in name else None
        if path is None:
            return self._send(HTTPStatus.NOT_FOUND, b"not found", "text/plain")
        return self._file(path)

    # ------------------------------------------------------------------ API
    def _get_api(self, name: str, q: dict):
        b = self.board
        if name == "info":
            return {
                "board_name": b.board_name(),
                "professor": b.mode() == "professor",
                "languages": LANGUAGES,
                "address": f"http://{self.public_host}" if self.public_host else None,
            }
        if name == "strings":
            return strings(q.get("lang", "cat"))
        v = self._visit()
        if name == "home":
            return b.home(v)
        if name == "homework":
            return b.homework(v)
        if name == "practice":
            return b.practice(v)
        if name == "exercise":
            return b.open_exercise(
                v,
                q.get("key", ""),
                q.get("mode", "practice"),
                q.get("assignment_id") or None,
                q.get("path_reason") or None,
            )
        if name == "reply":
            return b.jobs.get(q.get("ticket", ""))
        raise Refused("not found")

    def _post_api(self, name: str, d: dict):
        b = self.board
        if name == "login":
            v = b.login(
                d.get("code", ""),
                d.get("client_ts"),
                d.get("language", "cat"),
                bool(d.get("teacher")),
            )
            return {"token": v.token, "code": v.code, "teacher": v.teacher}
        v = self._visit()
        if name == "logout":
            b.logout(v.token)
            return {"ok": True}
        if name == "answer":
            return b.answer(v, d.get("key", ""), d.get("answer", ""))
        if name == "clue":
            return {"ticket": b.clue(v, d.get("key", ""))}
        if name == "solution":
            return {"ticket": b.solution(v, d.get("key", ""))}
        if name == "ask":
            photo = None
            if d.get("photo_b64"):
                try:
                    photo = base64.b64decode(d["photo_b64"], validate=True)
                except (binascii.Error, ValueError) as e:
                    raise Refused("bad photo") from e
            return {
                "ticket": b.ask(
                    v, d.get("key") or None, d.get("text", ""), photo, d.get("photo_type")
                )
            }
        if name == "free/next":
            return b.free_next(v)
        if name == "event":
            b.client_event(v, d.get("type", ""), d)
            return {"ok": True}
        raise Refused("not found")


def make_server(root, host="0.0.0.0", port=80, public_host=None, board=None, log_requests=False):
    board = board or Board(root)
    handler = type(
        "BoundHandler",
        (Handler,),
        {"board": board, "public_host": public_host, "log_requests": log_requests},
    )
    server = ThreadingHTTPServer((host, port), handler)
    server.daemon_threads = True
    server.board = board
    return server


def _watch(server, root: Path, interval: float):
    """Close idle visits, and stop when the teacher app pushed new code (systemd restarts us)."""
    version_file = root / paths.VERSION

    def read_version():
        return version_file.read_text().strip() if version_file.exists() else ""

    start = read_version()
    while True:
        time.sleep(interval)
        server.board.close_idle()
        if read_version() != start:
            with server.board.lock:
                if server.board.visit:
                    server.board._end(server.board.visit, "restart")
            server.shutdown()
            return


def main():
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--root", default=None, help="board root (default ~/santolina)")
    p.add_argument("--host", default="0.0.0.0")
    p.add_argument("--port", type=int, default=80)
    p.add_argument(
        "--public-host", default=None, help="e.g. 10.42.0.1 (turns on the captive portal)"
    )
    p.add_argument("--log-requests", action="store_true", help="print every request (debugging)")
    args = p.parse_args()
    root = paths.board_root(args.root)
    server = make_server(
        root, args.host, args.port, args.public_host, log_requests=args.log_requests
    )
    threading.Thread(target=_watch, args=(server, root, 10), daemon=True).start()
    print(f"Student app on http://{args.public_host or args.host}:{args.port} (board {root})")
    try:
        server.serve_forever()
    finally:
        server.board.jobs.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
