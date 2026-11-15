# student_app/

The student app: the web interface that the board serves to the student's
phone over the hotspot, with no internet. This README is for people who change
its code. Teachers start with [Use the student app](../docs/how-to/use-student-app.md).
It runs on the board and uses only the Python standard library.

The board runs a copy in `~/santolina/lib/`. `06_install_student_app.sh` makes it once from the board's checkout if it is missing. After that, only the teacher app replaces that copy
at setup and when the teacher opens the board's page with the board connected
([Keep the board's code up to date](../docs/how-to/run-teacher-app.md#keep-the-boards-code-up-to-date)).

## Files

| File | What it does |
|---|---|
| `__init__.py` | Holds `RELEASE`. Raise it by one with every change that boards must keep: the teacher app never replaces a board's code with a lower release. |
| `server.py` | The web server (port 80 on the board). Serves `static/` and the JSON API. |
| `state.py` | What happens in a session, without HTTP: login with the student code, exercises, answers, clues, chat, events. |
| `catalog.py` | The exercises on this board: exercise packs, assignments, practice topics. |
| `planner.py` | The learning path of free mode: which problem comes next. No model. |
| `tutor.py` | Chat replies and clues from the Tutor model. A pattern rule blocks replies that name the right option or its value. Solutions come from the exercise pack or fixed texts, not from a model. Fixed texts also replace the model when it does not answer. |
| `router.py` | Labels each chat message (STUCK, CONCEPT, ATTEMPT, SOLUTION, OTHER) with a keyword rule, so the tutor can choose how to answer. The intent router is meant to replace this rule. At this commit it runs only by hand ([Use the decider-2b router](../docs/how-to/use-decider-2b-router.md)). |
| `llm.py` | Streaming client for the Tutor model: port 8084, or the URL in the environment variable `SANTOLINA_TUTOR_URL`. |
| `jobs.py` | Runs the slow model calls one at a time. The phone asks again for the result. |
| `easy_read.py` | Easy read: the problem text one sentence per line, with the question last. |
| `board_state.py` | Is the hotspot on, and is a phone connected? The [LED matrix app](../board/README.md) reads it, and whether the Tutor model is writing, from `/api/board-state`. |
| `strings.py` | Every text the student sees, in Catalan (default), English and Spanish. |
| `static/` | The page: `index.html`, `app.js`, `app.css`, the icon and the Atkinson Hyperlegible fonts (SIL Open Font License, `static/fonts/OFL.txt`). |

The student app reads and writes the files of the
[board data contract](../docs/reference/board-data-contract.md) through the
[`classroom/`](../classroom/README.md) package.

## Install and run

On a board that runs the copilot, in `~/Santolina_tutor`, once per board:

```bash
./board/06_install_student_app.sh
```

It asks for the `sudo` password once, installs `santolina-student.service`
(`python3 -m student_app.server` from `~/santolina/lib/`, at every boot) and
prints `student app answers on port 80`. Phones reach it only after the
teacher app sets up the board's hotspot and the board restarts. The Tutor model needs
`./board/08_install_tutor.sh` (see [`board/`](../board/README.md)). All steps:
[Use the student app](../docs/how-to/use-student-app.md#prepare-a-board-teacher-once-per-board).

To try it on the laptop with no board, use the teacher app's demo:
[Try it on the laptop](../docs/how-to/use-student-app.md#try-it-on-the-laptop).

Tests: see [`tests/`](../tests/README.md).

## Docs

- [Use the student app](../docs/how-to/use-student-app.md): install, use and stop it.
- [Tutor response types](../docs/reference/tutor-response-types.md): how the tutor answers each kind of message.
- [Student data privacy](../docs/explanation/student-data-privacy.md): what is stored and why.
- Terms: [GLOSSARY.md](../GLOSSARY.md) (Student app, Hotspot, Student code, Session, Event, Exercise pack, Assignment, Free mode, Learning path, Clue, Tutor model, Intent router, Board data contract).
