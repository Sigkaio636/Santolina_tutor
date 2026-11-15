# student_app/

The student app: the web interface that the board serves to the student's
phone over the hotspot, with no internet. It runs on the board and uses only
the standard library. The board runs a copy in `~/santolina/lib/`, which the
teacher app updates at setup and each time the board is plugged in.

## Files

| File | What it does |
|---|---|
| `server.py` | The web server (port 80 on the board). Serves `static/` and the JSON API. |
| `state.py` | What happens in a session, without HTTP: login with the student code, exercises, answers, clues, chat, events. |
| `catalog.py` | The exercises on this board: exercise packs, assignments, practice topics. |
| `planner.py` | The learning path of free mode: which problem comes next. No model. |
| `tutor.py` | Chat replies, clues and solutions from the tutor model, with a leak check, a clue ladder and fixed texts when the model does not answer. |
| `router.py` | Labels each chat message (STUCK, CONCEPT, ATTEMPT, SOLUTION, OTHER), so the tutor can choose how to answer. The intent router plugs in here. |
| `llm.py` | Streaming client for the tutor model (port 8084, or `SANTOLINA_TUTOR_URL`). |
| `jobs.py` | Runs the slow model calls one at a time; the phone polls for the result. |
| `easy_read.py` | Easy read: the problem text one sentence per line, with the question last. |
| `board_state.py` | Is the hotspot on, and is a phone connected? The LED matrix app reads it. |
| `strings.py` | Every text the student sees, in Catalan (default), English and Spanish. |
| `__init__.py` | Package marker. |
| `static/` | The page: `index.html`, `app.js`, `app.css`, the icon and the Atkinson Hyperlegible fonts (OFL licence). |

The student app reads and writes the files of the
[board data contract](../docs/reference/board-data-contract.md) through the
`classroom/` package.

## Install and run

On the board, from the repository folder, once per board:

```bash
./board/06_install_student_app.sh
```

It installs `santolina-student.service`, which runs
`python3 -m student_app.server` from `~/santolina/lib/` at every boot. The
tutor model needs `./board/08_install_tutor.sh`.

On the laptop, with no board, the teacher app's demo starts a student app on
simulated boards:

```bash
uv run --group teacher python -m teacher_app demo
```

Tests: `make test` (see [`tests/`](../tests/README.md)).

## Docs

- [Use the student app](../docs/how-to/use-student-app.md): install, use and stop it.
- [Use the decider-2b router](../docs/how-to/use-decider-2b-router.md): the intent router.
- [Tutor response types](../docs/TUTOR_RESPONSE_TYPES.md) and [Student data privacy](../docs/explanation/student-data-privacy.md).
- Terms: [GLOSSARY.md](../GLOSSARY.md) (Student app, Tutor model, Intent router, Free mode, Learning path, Clue, Hotspot).
