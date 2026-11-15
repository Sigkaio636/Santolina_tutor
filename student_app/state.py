"""What happens in a visit, without HTTP: login, exercises, answers, clues, chat, logging.

One board belongs to one student, so there is one visit at a time. A visit is one session
of the board data contract: every action is logged through classroom.events, so the
teacher app can unload it. A teacher visit (professor mode only) shows answers and logs
nothing.
"""

import secrets
import threading
import time

from classroom import paths, progress
from classroom.events import EventWriter
from classroom.schemas import ContractError, Mode, Roster, read_json

from .catalog import Catalog
from .jobs import Jobs
from .planner import PathPlanner
from .strings import DEFAULT, LANGUAGES
from .strings import text as tr
from .tutor import Tutor

IDLE_SECONDS = 30 * 60
FAIL_AFTER_WRONG = 2  # free mode: this many wrong answers count as a failure
CLIENT_EVENTS = ("view_opened", "page_hidden", "page_visible", "language_changed")
MODES = ("homework", "practice", "free")
MAX_QUESTION_CHARS = 2000


class Expired(Exception):
    """No visit with this token: the phone must ask for the code again."""


class Refused(Exception):
    """The request is not allowed (wrong code, unknown exercise...)."""


class ExerciseState:
    def __init__(self, mode, assignment_id, path_reason=None):
        self.mode = mode
        self.assignment_id = assignment_id
        self.path_reason = path_reason
        self.shown_at = time.monotonic()
        self.attempts = 0
        self.wrong: list = []
        self.hints = 0
        self.solution_shown = False
        self.solved = False

    def public(self) -> dict:
        return {
            "attempts": self.attempts,
            "wrong": self.wrong,
            "hints": self.hints,
            "solution_shown": self.solution_shown,
            "solved": self.solved,
            "can_show_solution": self.attempts > 0 and not self.solved,
        }


class Visit:
    def __init__(self, code, teacher, language, session):
        self.token = secrets.token_urlsafe(18)
        self.code = code
        self.teacher = teacher
        self.language = language
        self.session = session  # classroom.events.Session, None for a teacher
        self.last_activity = time.monotonic()
        self.exercises: dict = {}
        self.current = None  # key of the exercise on screen
        self.free_history: list = []
        self.chats: dict = {}  # thread key ("free" or an exercise key) -> [(role, text)]
        self.hidden_since = None


RESERVED_LOG = {"text", "seconds", "kind", "suggestions", "type", "item", "v"}


class Board:
    def __init__(
        self, root=None, tutor_cls=Tutor, planner_cls=PathPlanner, idle_seconds=IDLE_SECONDS
    ):
        self.root = paths.board_root(root)
        self.catalog = Catalog(self.root)
        self.tutor = tutor_cls(self.catalog)
        self.planner = planner_cls(self.catalog)
        self.jobs = Jobs()
        self.idle_seconds = idle_seconds
        self.lock = threading.RLock()
        self.visit: Visit | None = None

    # ------------------------------------------------------------------ board files
    def mode(self) -> str:
        try:
            m = read_json(self.root / paths.MODE, Mode)
            return m.mode if m else "student"
        except (ContractError, ValueError, TypeError):
            return "student"

    def roster(self) -> list:
        try:
            r = read_json(self.root / paths.ROSTER, Roster)
            return [c.upper() for c in r.codes] if r else []
        except (ContractError, ValueError, TypeError):
            return []

    def board_name(self) -> str:
        data = read_json(self.root / paths.IDENTITY) or {}
        return data.get("name", "")

    # ------------------------------------------------------------------ visits
    def login(self, code: str, client_ts=None, language=DEFAULT, teacher=False) -> Visit:
        language = language if language in LANGUAGES else DEFAULT
        with self.lock:
            if teacher:
                if self.mode() != "professor":
                    raise Refused("bad_code")
                code, session = None, None
            else:
                code = (code or "").strip().upper()
                if code not in self.roster():
                    raise Refused("bad_code")
                # The same student again (the Wi-Fi sign-in window, then the browser): share
                # the visit, so neither window throws the other out.
                self.close_idle()
                v = self.visit
                if v and not v.teacher and v.code == code:
                    v.last_activity = time.monotonic()
                    return v
                session = EventWriter.from_root(self.root).start_session(
                    code, client_ts=client_ts, language=language
                )
            if self.visit:
                self._end(self.visit, "new_login")
            self.visit = Visit(code, teacher, language, session)
            return self.visit

    def check(self, token: str) -> Visit:
        with self.lock:
            self.close_idle()
            v = self.visit
            if not v or not token or not secrets.compare_digest(v.token, token):
                raise Expired()
            v.last_activity = time.monotonic()
            return v

    def logout(self, token: str) -> None:
        with self.lock:
            self._end(self.check(token), "logout")

    def close_idle(self) -> None:
        with self.lock:
            v = self.visit
            if v and time.monotonic() - v.last_activity > self.idle_seconds:
                self._end(v, "idle")

    def _end(self, v: Visit, reason: str) -> None:
        self._leave_current(v)
        if v.session and not v.session.ended:
            try:
                v.session.end(reason=reason)
            except (ContractError, OSError):
                pass
        if self.visit is v:
            self.visit = None

    # ------------------------------------------------------------------ logging
    def log(self, v: Visit, type: str, item=None, **payload) -> None:
        if v.session is None:  # a teacher visit: nothing is saved
            return
        if item is not None:
            st = v.exercises.get(item.key)
            payload = (
                {
                    "mode": st.mode if st else None,
                    "assignment_id": st.assignment_id if st else None,
                }
                | item.context()
                | payload
            )
        with self.lock:
            try:
                v.session.log(type, **payload)
            except (ContractError, OSError):
                pass  # the visit ended meanwhile: drop it rather than fail the request

    def client_event(self, v: Visit, type: str, payload: dict) -> None:
        if type not in CLIENT_EVENTS:
            raise Refused("unknown event")
        clean = {k: payload[k] for k in ("view", "language") if k in payload}
        if type == "page_hidden":
            v.hidden_since = time.monotonic()
        if type == "page_visible" and v.hidden_since is not None:
            clean["seconds_hidden"] = round(time.monotonic() - v.hidden_since, 1)
            v.hidden_since = None
        if type == "language_changed" and clean.get("language") in LANGUAGES:
            v.language = clean["language"]
        if type == "view_opened" and clean.get("view") != "exercise":
            self._leave_current(v)
        item = self.catalog.get(v.current) if v.current else None
        self.log(v, type, item if type != "view_opened" else None, **clean)

    # ------------------------------------------------------------------ progress
    def _progress(self, v: Visit) -> dict:
        if v.teacher:
            return {"exercises": {}, "last": None}
        return progress.load(self.root, v.code)

    def _save_progress(self, v: Visit, data: dict) -> None:
        if not v.teacher:
            progress.save(self.root, v.code, data)

    def home(self, v: Visit) -> dict:
        prog = self._progress(v)
        homework = self.catalog.homework(prog)
        pending = sum(a["pending"] for a in homework)
        dues = sorted(a["due"] for a in homework if a["due"] and a["pending"])
        last = prog.get("last")
        cont = None
        if last:
            item = self.catalog.get(f"{last['pack_id']}/{last['exercise_id']}")
            if (
                item
                and progress.status(prog, last["pack_id"], last["exercise_id"])
                not in progress.DONE
            ):
                cont = {
                    **last,
                    "key": item.key,
                    "title": self.catalog.summary(item, prog)["title"],
                }
        return {
            "board_name": self.board_name(),
            "code": v.code,
            "teacher": v.teacher,
            "continue": cont,
            "homework_pending": pending,
            "homework_next_due": dues[0] if dues else None,
            "practice_topics": len(self.catalog.topics(prog)),
            "exercises": len(self.catalog.items),
        }

    def homework(self, v: Visit) -> list:
        return self.catalog.homework(self._progress(v))

    def practice(self, v: Visit) -> list:
        return self.catalog.topics(self._progress(v), tr(v.language, "level"))

    # ------------------------------------------------------------------ exercises
    def _item(self, key: str):
        item = self.catalog.get(key or "")
        if item is None:
            raise Refused("unknown exercise")
        return item

    def _leave_current(self, v: Visit) -> None:
        """Log exercise_left when the student moves away from an unsolved exercise."""
        if not v.current:
            return
        item = self.catalog.get(v.current)
        st = v.exercises.get(v.current)
        if item and st and not st.solved and not st.solution_shown:
            self.log(
                v,
                "exercise_left",
                item,
                seconds=round(time.monotonic() - st.shown_at, 1),
                attempts=st.attempts,
            )
        if st and st.mode == "free" and v.free_history and v.free_history[-1]["key"] == v.current:
            entry = v.free_history[-1]
            if entry["outcome"] == "open":
                entry["outcome"] = self._free_outcome(st)
                entry["wrong"], entry["hints"] = len(st.wrong), st.hints
        v.current = None

    @staticmethod
    def _free_outcome(st: ExerciseState) -> str:
        if st.solution_shown or len(st.wrong) >= FAIL_AFTER_WRONG:
            return "failed"
        return "solved" if st.solved else "skipped"

    def open_exercise(self, v: Visit, key: str, mode: str, assignment_id=None, path_reason=None):
        item = self._item(key)
        mode = mode if mode in MODES else "practice"
        if v.current and v.current != key:
            self._leave_current(v)
        st = v.exercises.get(key)
        if st is None or st.mode != mode:
            st = v.exercises[key] = ExerciseState(mode, assignment_id, path_reason)
        st.shown_at = time.monotonic()
        v.current = key
        if mode == "free" and (not v.free_history or v.free_history[-1]["key"] != key):
            v.free_history.append({"key": key, "outcome": "open", "reason": path_reason})
        self.log(v, "exercise_shown", item, path_reason=path_reason)
        warm = getattr(self.tutor, "warm", None)
        if warm and not (st.hints or st.solution_shown):  # read the problem while the student does
            thread = self._thread(v, item)
            self.jobs.submit(warm, self._context(v, item, thread))
        prog = self._progress(v)
        prog["last"] = {
            "mode": mode,
            "pack_id": item.pack.pack_id,
            "exercise_id": item.exercise.exercise_id,
            "assignment_id": assignment_id,
        }
        self._save_progress(v, prog)
        data = self.catalog.public(item, with_answer=v.teacher)
        data["state"] = st.public()
        data["status"] = progress.status(prog, item.pack.pack_id, item.exercise.exercise_id)
        data["mode"] = mode
        data["assignment_id"] = assignment_id
        data["path_reason"] = path_reason
        return data

    def _state(self, v: Visit, key: str) -> ExerciseState:
        st = v.exercises.get(key)
        if st is None:
            raise Refused("open the exercise first")
        return st

    def answer(self, v: Visit, key: str, letter: str) -> dict:
        item = self._item(key)
        st = self._state(v, key)
        letter = (letter or "").strip().upper()
        if letter not in (item.exercise.options or {}):
            raise Refused("unknown option")
        correct = letter == (item.exercise.answer or "").upper()
        st.attempts += 1
        with_help = st.solution_shown
        if correct:
            st.solved = True
        elif letter not in st.wrong:
            st.wrong.append(letter)
        self.log(
            v,
            "answer_submitted",
            item,
            answer=letter,
            correct=correct,
            attempt=st.attempts,
            seconds_since_shown=round(time.monotonic() - st.shown_at, 1),
            with_help=with_help,
        )
        prog = self._progress(v)
        if with_help:
            progress.record_solution(prog, item.pack.pack_id, item.exercise.exercise_id)
        else:
            progress.record_answer(prog, item.pack.pack_id, item.exercise.exercise_id, correct)
        self._save_progress(v, prog)
        return {
            "correct": correct,
            "counts": not with_help,
            "state": st.public(),
            "status": progress.status(prog, item.pack.pack_id, item.exercise.exercise_id),
        }

    def _context(self, v: Visit, item, thread: str) -> dict:
        return {
            "mode": v.exercises[item.key].mode if item and item.key in v.exercises else "free",
            "language": v.language,
            "exercise": self.catalog.public(item, with_answer=True) if item else None,
            "history": list(v.chats.get(thread, [])),
            "seen": list(v.exercises),  # keys opened in this visit
            "solution_shown": bool(
                item and item.key in v.exercises and v.exercises[item.key].solution_shown
            ),
        }

    def _thread(self, v: Visit, item) -> str:
        """Free mode is one conversation; otherwise each exercise has its own chat."""
        st = v.exercises.get(item.key) if item else None
        return item.key if item and st and st.mode != "free" else "free"

    def _reply_job(self, v: Visit, item, kind: str, thread: str, fn, *args):
        start = time.monotonic()
        result = fn(*args)
        reply = result if isinstance(result, dict) else {"text": result, "suggestions": []}
        seconds = round(time.monotonic() - start, 2)
        suggestions = [s for s in reply.get("suggestions", []) if self.catalog.get(s)]
        self.log(
            v,
            "copilot_reply",
            item,
            text=reply["text"],
            seconds=seconds,
            kind=kind,
            suggestions=suggestions,
            # How the tutor answered: route, label, tokens, model and first-token seconds
            **{k: v for k, v in (reply.get("log") or {}).items() if k not in RESERVED_LOG},
        )
        v.chats.setdefault(thread, []).append(("copilot", reply["text"]))
        out = {"text": reply["text"], "kind": kind, "suggestions": []}
        prog = self._progress(v)
        for s in suggestions:
            out["suggestions"].append(self.catalog.summary(self.catalog.get(s), prog))
        if kind == "solution":
            out["answer"] = item.exercise.answer
        return out

    def clue(self, v: Visit, key: str) -> str:
        item = self._item(key)
        st = self._state(v, key)
        st.hints += 1
        self.log(v, "hint_requested", item, hint_number=st.hints)
        thread = self._thread(v, item)
        ctx = self._context(v, item, thread)
        # The button press stays in the chat, so later prompts repeat it word for word
        v.chats.setdefault(thread, []).append(("clue", str(st.hints)))
        return self.jobs.submit(
            self._reply_job,
            v,
            item,
            "clue",
            thread,
            self.tutor.clue,
            ctx,
            ctx["exercise"],
            st.hints,
        )

    def solution(self, v: Visit, key: str) -> str:
        item = self._item(key)
        st = self._state(v, key)
        if st.attempts == 0 and not v.teacher:
            raise Refused("try once first")
        if not st.solution_shown:
            st.solution_shown = True
            self.log(v, "solution_requested", item, attempts_before=st.attempts)
            prog = self._progress(v)
            progress.record_solution(prog, item.pack.pack_id, item.exercise.exercise_id)
            self._save_progress(v, prog)
        thread = self._thread(v, item)
        ctx = self._context(v, item, thread)
        v.chats.setdefault(thread, []).append(("solution", ""))
        return self.jobs.submit(
            self._reply_job,
            v,
            item,
            "solution",
            thread,
            self.tutor.solution,
            ctx,
            ctx["exercise"],
            item.exercise.answer,
        )

    def ask(self, v: Visit, key, text: str, photo: bytes | None = None, photo_type=None) -> str:
        text = (text or "").strip()[:MAX_QUESTION_CHARS]
        if not text and not photo:
            raise Refused("empty question")
        item = self.catalog.get(key) if key else None
        thread = self._thread(v, item)
        self.log(
            v,
            "question_asked",
            item,
            text=text,
            has_photo=bool(photo),
            photo_bytes=len(photo) if photo else 0,
            photo_type=photo_type if photo else None,
            **({} if item else {"mode": "free"}),
        )
        ctx = self._context(v, item, thread)
        v.chats.setdefault(thread, []).append(("student", text))
        return self.jobs.submit(
            self._reply_job, v, item, "chat", thread, self.tutor.reply, ctx, text, photo
        )

    def free_next(self, v: Visit) -> dict:
        if v.current:
            self._leave_current(v)
        last = v.free_history[-1] if v.free_history else None
        key, reason = self.planner.next(v.free_history, last, self._progress(v), v.language)
        if key is None:
            raise Refused("no exercises")
        return self.open_exercise(v, key, "free", path_reason=reason)
