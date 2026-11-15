# tests/

The automated tests of the copilot, the board data contract, the student app
and the teacher app. Run them before you change any of that code. They need no
board, no model services and no M3Kang data: the boards are simulated and the
problems are invented.

## Files

| File | What it tests |
|---|---|
| `conftest.py` | Shared pytest fixtures (objects that pytest passes to each test): a temporary teacher store, a simulated board, a group with students. |
| `test_pipeline.py` | `copilot/`: every problem gets one letter, even when a model service fails. Uses `unittest`, so it runs with `python3` alone. |
| `test_classroom.py` | `classroom/`: records, validation, session files, packs and the board status. |
| `test_student_app.py` | The student app over real HTTP on a simulated board, then an unload by the teacher app. |
| `test_tutor.py` | `student_app/tutor.py` and `router.py`: the answer leak check, message labels, prompts, clues, solutions, fixed texts when the model fails, streaming. |
| `test_planner.py` | The free-mode learning path, with simulated students. |
| `test_easy_read.py` | `student_app/easy_read.py`: one sentence per line, question last. |
| `test_board_state.py` | `student_app/board_state.py`: which phones are on the hotspot, and its web endpoint. |
| `test_services.py` | `teacher_app/services/`: setup, assignments, packs, unload, and the statistics widgets. |
| `test_web.py` | The teacher app's web pages, end to end on a simulated board. |
| `test_learning.py` | The learning-progress statistics of the teacher app. |
| `test_kangaroo.py` | The teacher app's Kangaroo library: copy a board's Index, browse, make a pack, give homework. |
| `test_demo.py` | `python -m teacher_app demo` builds a classroom whose data agrees across boards and the teacher store. |

Test files must not hold M3Kang problem text (see [`CLAUDE.md`](../CLAUDE.md)):
write invented examples.

## Run

From the repository folder. It needs [uv](https://docs.astral.sh/uv/). The
`teacher` dependency group in `pyproject.toml` adds pytest and the teacher app's
packages:

```bash
make test
```

It runs `uv run --group teacher pytest` on every file above and ends with
`N passed`. To run only the copilot tests, with `python3` alone (on the laptop
or the board):

```bash
make test-copilot
```

It ends with `OK`.

## Docs

- Code under test: [`copilot/`](../copilot/README.md), [`classroom/`](../classroom/README.md), [`student_app/`](../student_app/README.md), [`teacher_app/`](../teacher_app/README.md).
- Terms: [GLOSSARY.md](../GLOSSARY.md) (Copilot, Board data contract, Student app, Teacher app, Model services, Teacher store, Unload, Hotspot, Free mode, Learning path, Index).
