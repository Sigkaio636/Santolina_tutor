"""The copilot must answer every problem with one letter, even when a model service fails.

    python3 -m unittest discover -s tests -v      # or: make test

Standard library only, like the board code. Fake llama-server instances run on
127.0.0.1 in threads; no model and no M3Kang data are needed.
"""
import csv
import json
import os
import socket
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from copilot import pipeline, rag
from copilot.pipeline import FALLBACK, solve

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLES = os.path.join(ROOT, "data", "sample_problems.jsonl")
PROBLEM = {"id": "t1", "language": "eng", "text": "1 + 1 = ?",
           "options": {"A": "1", "B": "2", "C": "3", "D": "4", "E": "5"}}


def chat_reply(letter):
    return {"choices": [{"message": {"content": letter}}], "timings": {"prompt_n": 7}}


class FakeServer:
    """A fake model service. mode says how it answers a POST."""

    def __init__(self, mode):
        def handler_class(server_mode):
            class Handler(BaseHTTPRequestHandler):
                def log_message(self, *args):
                    pass

                def do_POST(self):
                    self.rfile.read(int(self.headers.get("Content-Length", 0)))
                    if server_mode == "close":  # drop the connection, send nothing
                        self.close_connection = True
                        return
                    if server_mode == "slow":
                        time.sleep(3)
                        body, code = json.dumps(chat_reply("B")).encode(), 200
                    elif server_mode == "bad-json":
                        body, code = b"{not json", 200
                    elif server_mode == "empty":
                        body, code = b"{}", 200
                    elif server_mode == "500":
                        body, code = b'{"error": "boom"}', 500
                    elif server_mode == "not-a-letter":
                        body, code = json.dumps(chat_reply("")).encode(), 200
                    else:
                        body, code = json.dumps(chat_reply("B")).encode(), 200
                    try:
                        self.send_response(code)
                        self.send_header("Content-Type", "application/json")
                        self.send_header("Content-Length", str(len(body)))
                        self.end_headers()
                        self.wfile.write(body)
                    except (BrokenPipeError, ConnectionResetError):
                        pass  # the client gave up first (the timeout case)
            return Handler

        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), handler_class(mode))
        self.httpd.daemon_threads = True
        self.port = self.httpd.server_address[1]
        self.url = f"http://127.0.0.1:{self.port}/v1/chat/completions"
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()

    def close(self):
        self.httpd.shutdown()
        self.httpd.server_close()


def tmpdir(test):
    """A temporary folder removed after the test (TestCase.enterContext needs 3.11)."""
    folder = tempfile.TemporaryDirectory()
    test.addCleanup(folder.cleanup)
    return folder.name


def free_port():
    """A port where nothing listens, so the connection is refused."""
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class SolveFallsBack(unittest.TestCase):
    # These tests check the model path; the default solver ("prior") never calls it.
    def setUp(self):
        original = pipeline.SOLVER
        pipeline.SOLVER = "letter"
        self.addCleanup(setattr, pipeline, "SOLVER", original)

    def ask(self, mode, time_limit=60):
        server = FakeServer(mode)
        self.addCleanup(server.close)
        return solve(PROBLEM, llm_url=server.url, time_limit=time_limit)

    def assert_fallback(self, result, status_start):
        self.assertEqual(result["answer"], FALLBACK)
        self.assertTrue(result["status"].startswith(status_start), result["status"])

    def test_good_server_answers(self):
        result = self.ask("ok")
        self.assertEqual((result["answer"], result["status"]), ("B", "ok"))

    def test_dropped_connection(self):
        self.assert_fallback(self.ask("close"), "error: RemoteDisconnected")

    def test_bad_json(self):
        self.assert_fallback(self.ask("bad-json"), "error: JSONDecodeError")

    def test_reply_without_choices(self):
        self.assert_fallback(self.ask("empty"), "error: KeyError")

    def test_http_500(self):
        self.assert_fallback(self.ask("500"), "error: HTTPError")

    def test_reply_not_a_letter(self):
        self.assert_fallback(self.ask("not-a-letter"), "error: ValueError")

    def test_connection_refused(self):
        url = f"http://127.0.0.1:{free_port()}/v1/chat/completions"
        self.assert_fallback(solve(PROBLEM, llm_url=url), "error: ConnectionRefusedError")

    def test_timeout(self):
        # time_limit below MARGIN gives the minimum 1 s timeout; the server needs 3 s
        self.assert_fallback(self.ask("slow", time_limit=1), "timeout")

    def test_retrieval_failure_falls_back(self):
        class BrokenIndex:
            def search(self, *args, **kwargs):
                raise ValueError("wrong dimensions")
        result = solve(PROBLEM, index=BrokenIndex(), k=1, llm_url="http://127.0.0.1:1/")
        self.assert_fallback(result, "error: ValueError: wrong dimensions")


class PredictKeepsGoing(unittest.TestCase):
    """predict.py writes one letter per problem even when every call fails."""

    def run_predict(self, mode, *extra):
        if mode == "refused":
            port = free_port()
        else:
            server = FakeServer(mode)
            self.addCleanup(server.close)
            port = server.port
        out = os.path.join(tmpdir(self), "x.csv")
        done = subprocess.run(
            [sys.executable, "predict.py", "--input", SAMPLES, "--output", out, *extra],
            cwd=ROOT, env={**os.environ, "LLM_PORT": str(port), "SOLVER": "letter"},
            capture_output=True, text=True, timeout=120)
        return done, out

    def test_every_failure_mode(self):
        with open(SAMPLES) as f:
            expected = [json.loads(line)["id"] for line in f if line.strip()]
        for mode in ("ok", "close", "bad-json", "empty", "500", "refused"):
            with self.subTest(mode=mode):
                done, out = self.run_predict(mode)
                self.assertEqual(done.returncode, 0, done.stderr)
                with open(out) as f:
                    rows = list(csv.DictReader(f))
                self.assertEqual([r["id"] for r in rows], expected)
                for r in rows:
                    self.assertIn(r["answer"], list("ABCDE"))
                    if mode != "ok":
                        self.assertEqual(r["answer"], FALLBACK)
                        self.assertTrue(r["status"].startswith("error: "), r["status"])

    def test_missing_index_creates_nothing(self):
        tmp = tmpdir(self)
        db = os.path.join(tmp, "index.db")
        done, _out = self.run_predict("ok", "--rag", "1", "--index", db)
        self.assertNotEqual(done.returncode, 0)
        self.assertIn("not found", done.stderr)
        self.assertFalse(os.path.exists(db))


class IndexChecks(unittest.TestCase):
    def setUp(self):
        self.tmp = tmpdir(self)
        self.db = os.path.join(self.tmp, "index.db")

    def test_missing_file(self):
        self.assertIn("not found", rag.check(self.db))
        with self.assertRaises(FileNotFoundError):
            rag.Index(self.db)
        self.assertFalse(os.path.exists(self.db), "Index() must not create the file")

    def test_empty_file(self):
        open(self.db, "w").close()
        self.assertIn("empty", rag.check(self.db))
        with self.assertRaises(FileNotFoundError):
            rag.Index(self.db)

    def build(self, dims):
        def fake_embed(texts, query=False, timeout=60):
            return [[1.0] + [0.0] * (dims - 1) for _ in texts]
        original = rag.embed
        rag.embed = fake_embed
        self.addCleanup(setattr, rag, "embed", original)
        list(rag.build(self.db, [dict(PROBLEM, id="s1", label="B")]))

    def test_search_works(self):
        self.build(4)
        hits = rag.Index(self.db).search(PROBLEM, k=1)
        self.assertEqual(hits[0][1]["id"], "s1")

    def test_dimension_mismatch(self):
        self.build(4)
        index = rag.Index(self.db)
        rag.embed = lambda texts, query=False, timeout=60: [[1.0, 0.0] for _ in texts]
        with self.assertRaisesRegex(ValueError, "2 dimensions.*holds 4"):
            index.search(PROBLEM, k=1)


if __name__ == "__main__":
    unittest.main()
