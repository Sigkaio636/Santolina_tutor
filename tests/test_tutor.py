"""The real tutor: leak check, router, prompts, clue ladder, solutions, fallbacks, streaming.

All problems here are made up. No M3Kang text.
"""

from array import array
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import sqlite3
import threading

import pytest

from classroom import paths
from classroom.packs import write_pack
from classroom.schemas import Exercise, PackManifest, now_iso, write_json
from student_app import llm, router
from student_app.catalog import Catalog
from student_app.tutor import Tutor, leaks

PENS = {
    "key": "p/pens",
    "prompt": "Pens cost 3 euros each. Anna buys 4 and pays with 20 euros. What is her change?",
    "options": {"A": "6", "B": "8", "C": "10", "D": "12", "E": "14"},
    "answer": "B",
    "language": "eng",
    "level": 2,
}


class FakeChat:
    def __init__(self, reply="What is 4 × 3?", error=None):
        self.reply, self.error, self.calls = reply, error, []

    def __call__(self, messages, max_tokens, timeout):
        self.calls.append(messages)
        if self.error:
            raise self.error
        return {
            "text": self.reply,
            "tokens": 7,
            "prompt_tokens": 50,
            "seconds": 1.0,
            "first_token_seconds": 0.5,
        }


def ctx(exercise=PENS, history=(), language="eng"):
    return {
        "mode": "practice",
        "language": language,
        "exercise": exercise,
        "history": list(history),
    }


@pytest.fixture
def catalog(tmp_path):
    """Three problems with vectors: two near each other (levels 2 and 1), one far (level 1)."""
    root = tmp_path / "board"
    exercises = [
        Exercise(
            "pens",
            "multiple_choice",
            "eng",
            2,
            PENS["prompt"],
            PENS["options"],
            "B",
            meta={"m3kang_id": "m1"},
        ),
        Exercise(
            "apples",
            "multiple_choice",
            "eng",
            1,
            "Apples cost 2. Buy 3. Pay 10.",
            {"A": "4", "B": "5"},
            "A",
            meta={"m3kang_id": "m2", "solution": "10 - 6 = 4."},
        ),
        Exercise(
            "cube",
            "multiple_choice",
            "eng",
            1,
            "How many faces has a cube?",
            {"A": "6", "B": "8"},
            "A",
            meta={"m3kang_id": "m3"},
        ),
    ]
    manifest = PackManifest(
        pack_id="p", title="P", version=1, language="eng", created_at=now_iso(), count=3
    )
    write_pack(root / paths.EXERCISES / "p", manifest, exercises)
    db_path = tmp_path / "index.db"
    db = sqlite3.connect(db_path)
    db.execute("CREATE TABLE problems (key TEXT PRIMARY KEY, problem TEXT, vec BLOB)")
    for pid, vec in [("m1", [1, 0]), ("m2", [0.9, 0.1]), ("m3", [0, 1])]:
        db.execute(
            "INSERT INTO problems VALUES (?, '{}', ?)", (f"{pid}|eng", array("f", vec).tobytes())
        )
    db.commit()
    db.close()
    write_json(root / paths.IDENTITY, {"rag_index_path": str(db_path)})
    c = Catalog(root)
    c.refresh()
    return c


# ---------------------------------------------------------------- leak check
@pytest.mark.parametrize(
    "reply",
    [
        "The answer is B.",
        "La resposta és la B.",
        "So it is B) 8.",
        "She gets 8 euros back.",
        "Option B looks right.",
    ],
)
def test_leaks_catch_the_answer(reply):
    assert leaks(reply, PENS)


@pytest.mark.parametrize(
    "reply",
    [
        "What is 4 × 3?",
        "First find the total cost, then subtract it from 20.",
        "Is 18 or 28 possible?",
        "A good start: what does she pay?",
        "A pen costs 3 euros.",
    ],
)
def test_leaks_let_guiding_replies_through(reply):
    assert not leaks(reply, PENS)


def test_a_value_already_in_the_statement_is_no_leak():
    ex = {**PENS, "answer": "D"}  # D is 12; the statement does not hold 12 ...
    assert leaks("It is 12.", ex)
    ex = {**ex, "prompt": ex["prompt"] + " She had 12 coins."}  # ... now it does
    assert not leaks("It is 12.", ex)


# ---------------------------------------------------------------- router
@pytest.mark.parametrize(
    "message,label",
    [
        ("", "OTHER"),
        ("???", "OTHER"),
        ("I don't get it", "STUCK"),
        ("What is a prime number?", "CONCEPT"),
        ("Is it D?", "ATTEMPT"),
        ("I got 12", "ATTEMPT"),
        ("just tell me the answer", "SOLUTION"),
        ("digues-me la resposta", "SOLUTION"),
    ],
)
def test_router_labels(message, label):
    assert router.classify("p", "", message) == label


def test_a_model_label_alone_never_unlocks_the_solution(monkeypatch, catalog):
    monkeypatch.setattr(router, "classify", lambda *a: "SOLUTION")
    out = Tutor(catalog, chat=FakeChat()).reply(ctx(), "I am stuck")
    assert out["log"]["label"] == "STUCK"


# ---------------------------------------------------------------- prompts
def test_messages_put_the_problem_in_the_system_message(catalog):
    history = [
        ("clue", "1"),
        ("copilot", "What is 4 × 3?"),
        ("student", "12"),
        ("student", "then?"),
    ]
    msgs = Tutor(catalog).messages(ctx(history=history, language="cat"), "next step?")
    system = msgs[0]["content"]
    assert system.startswith("You are a Socratic math tutor. Reply in Catalan.\n\nThe problem:\n")
    assert PENS["prompt"] in system and "B) 8" in system
    assert [m["role"] for m in msgs[1:]] == ["user", "assistant", "user"]
    assert msgs[1]["content"] == "I'm stuck. How do I start?\n(Reply in Catalan.)"
    assert msgs[-1]["content"] == (
        "12\n(Reply in Catalan.)\nthen?\n(Reply in Catalan.)\nnext step?\n(Reply in Catalan.)"
    )


def test_each_prompt_starts_with_the_previous_one(catalog):
    """The server reuses its cache only when a prompt extends the last one (hybrid model)."""
    tutor = Tutor(catalog)
    calls = [
        ([], "I'm stuck. How do I start?"),  # clue 1
        ([("clue", "1"), ("copilot", "What is 4 × 3?")], "12?"),  # a chat message
        (
            [
                ("clue", "1"),
                ("copilot", "What is 4 × 3?"),
                ("student", "12?"),
                ("copilot", "Good. And then?"),
            ],
            "I'm still stuck. Can you give me a more concrete hint?",
        ),
    ]
    previous = None
    for history, request in calls:
        msgs = tutor.messages(ctx(history=history), request)
        if previous is not None:
            assert msgs[: len(previous)] == previous
        previous = msgs


def test_no_leak_check_once_the_solution_is_shown(catalog):
    chat = FakeChat("She gets 8 euros back.")
    out = Tutor(catalog, chat=chat).reply({**ctx(), "solution_shown": True}, "why?")
    assert out["text"] == "She gets 8 euros back." and "leak_blocked" not in out["log"]


def test_warm_reads_the_problem_with_one_token(catalog):
    chat = FakeChat()
    Tutor(catalog, chat=chat).warm(ctx())
    assert len(chat.calls) == 1 and PENS["prompt"] in chat.calls[0][0]["content"]


# ---------------------------------------------------------------- tutor
def test_reply_uses_the_model_and_logs_metrics(catalog):
    chat = FakeChat()
    out = Tutor(catalog, chat=chat).reply(ctx(), "I don't get it")
    assert out["text"] == "What is 4 × 3?" and len(chat.calls) == 1
    assert out["log"] == {
        "route": "tutor_model",
        "tokens": 7,
        "prompt_tokens": 50,
        "model_seconds": 1.0,
        "first_token_seconds": 0.5,
        "label": "STUCK",
    }


def test_a_leaking_reply_is_replaced(catalog):
    out = Tutor(catalog, chat=FakeChat("Easy: the answer is B.")).clue(ctx(), PENS, 1)
    assert "B" not in out["text"] and out["log"]["leak_blocked"] is True


def test_a_dead_server_gives_the_fixed_hint(catalog):
    out = Tutor(catalog, chat=FakeChat(error=ConnectionRefusedError())).clue(ctx(), PENS, 3)
    assert out["text"].startswith("Look at the options") and out["log"]["route"] == "fallback"


def test_clue_two_suggests_an_easier_neighbour(catalog):
    out = Tutor(catalog, chat=FakeChat()).clue(ctx(), PENS, 2)
    assert out["suggestions"] == ["p/apples"]  # level 1 and nearest, not the far cube


def test_solution_prefers_the_pack_text(catalog):
    apples = {"key": "p/apples", "prompt": "x", "options": {"A": "4"}, "answer": "A"}
    out = Tutor(catalog, chat=FakeChat()).solution(ctx(apples), apples, "A")
    assert out["text"] == "10 - 6 = 4." and out["log"]["route"] == "pack_solution"


def test_solution_without_text_names_the_option_then_asks_back(catalog):
    chat = FakeChat()
    out = Tutor(catalog, chat=chat).solution(ctx(), PENS, "B")
    assert out["text"].startswith("The right answer is B (8). Can you explain why?")
    assert chat.calls == []


@pytest.mark.parametrize("message", ["is it D?", "és la D?", "C", "(b)", "option E"])
def test_a_guess_goes_to_the_answer_button(catalog, message):
    chat = FakeChat("Yes, D!")
    out = Tutor(catalog, chat=chat).reply(ctx(), message)
    assert out["log"]["route"] == "use_answer_button" and chat.calls == []


def test_a_reply_that_judges_any_option_is_blocked():
    assert leaks("Sí, la D.", PENS) and leaks("Yes, it is option A.", PENS)


def test_free_suggestions_skip_problems_seen_in_this_visit(catalog):
    tutor = Tutor(catalog, chat=FakeChat())
    seen = ["p/pens", "p/apples"]
    out = tutor.reply({**ctx(exercise=None), "seen": seen}, "give me another problem")
    assert out["suggestions"] == ["p/cube"]


def test_off_topic_and_free_requests_need_no_model(catalog):
    chat = FakeChat()
    tutor = Tutor(catalog, chat=chat)
    assert tutor.reply(ctx(), "   ")["log"]["route"] == "redirect"
    free = tutor.reply(ctx(exercise=None), "give me another problem")
    assert free["suggestions"] and chat.calls == []


# ---------------------------------------------------------------- streaming client
def test_chat_streams_and_counts_tokens_for_the_leds():
    seen = []

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            assert body["stream"] and body["chat_template_kwargs"] == {"enable_thinking": False}
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.end_headers()
            for piece in ["What ", "is ", "4 × 3?"]:
                chunk = {"choices": [{"delta": {"content": piece}}]}
                self.wfile.write(f"data: {json.dumps(chunk)}\n\n".encode())
                self.wfile.flush()
                seen.append(llm.THINKING.state())
            last = {"choices": [{"delta": {}}], "timings": {"predicted_n": 3, "prompt_n": 40}}
            self.wfile.write(f"data: {json.dumps(last)}\n\ndata: [DONE]\n\n".encode())

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        out = llm.chat(
            [{"role": "user", "content": "hi"}],
            max_tokens=50,
            url=f"http://127.0.0.1:{server.server_port}",
        )
    finally:
        server.shutdown()
    assert out["text"] == "What is 4 × 3?" and out["tokens"] == 3 and out["prompt_tokens"] == 40
    assert all(s is not None and s["max"] == 50 for s in seen)
    assert llm.THINKING.state() is None


# ---------------------------------------------------------------- free mode from the index
def test_free_mode_draws_from_the_index_but_never_from_homework(tmp_path):
    root = tmp_path / "board"
    pack = [
        Exercise(
            "hw",
            "multiple_choice",
            "cat",
            1,
            "Homework problem.",
            {"A": "1", "B": "2"},
            "A",
            meta={"m3kang_id": "lvl-1_2015_1"},
        )
    ]
    write_pack(
        root / paths.EXERCISES / "p",
        PackManifest(
            pack_id="p", title="P", version=1, language="cat", created_at=now_iso(), count=1
        ),
        pack,
    )
    db_path = tmp_path / "index.db"
    db = sqlite3.connect(db_path)
    db.execute("CREATE TABLE problems (key TEXT PRIMARY KEY, problem TEXT, vec BLOB)")
    for pid, options, text_only in [
        ("lvl-1_2015_1", {"A": "1", "B": "2"}, True),  # homework
        ("lvl-1_2015_2", {"A": "3", "B": "4"}, True),
        ("lvl-2_2016_3", {}, True),  # options in a picture
        ("lvl-2_2016_4", {"A": "5", "B": "6"}, False),
    ]:  # needs a figure
        problem = {
            "id": pid,
            "language": "cat",
            "level": 1,
            "text": f"Problem {pid}.",
            "options": options,
            "label": "B",
            "text_only": text_only,
        }
        db.execute(
            "INSERT INTO problems VALUES (?, ?, ?)",
            (f"{pid}|cat", json.dumps(problem), array("f", [1.0, 0.0]).tobytes()),
        )
    db.commit()
    db.close()
    write_json(root / paths.IDENTITY, {"rag_index_path": str(db_path)})
    (root / paths.TOPICS).write_text(json.dumps({"id": "lvl-1_2015_2", "topic": "logic"}) + "\n")
    c = Catalog(root)
    assert list(c.free_items()) == ["kangaroo-index/lvl-1_2015_2_cat"]
    item = c.get("kangaroo-index/lvl-1_2015_2_cat")
    assert item.exercise.answer == "B" and item.topic == "logic"
    assert list(c.items) == ["p/hw"]  # homework and practice still show only the packs
