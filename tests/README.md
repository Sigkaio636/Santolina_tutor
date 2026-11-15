# tests/

The automatic tests of the copilot, the board data contract, the student app
and the teacher app. They run on the laptop, with no board, no model server
and no M3Kang data: the boards are simulated and the problems are invented.

## Run

From the repository folder:

```bash
make test
```

It runs `uv run --group teacher pytest`, every file below. Only the copilot
tests, with the standard library and no uv:

```bash
make test-copilot
```

## Files

| File | What it tests |
|---|---|
| `conftest.py` | Shared pytest fixtures: a temporary teacher store, a simulated board, a group with students. |
| `test_pipeline.py` | `copilot/`: every problem gets one letter, even when a model service fails. Uses `unittest`. |
| `test_classroom.py` | `classroom/`: records, validation, event files, packs and the board status. |
| `test_student_app.py` | The student app over real HTTP on a simulated board, then an unload by the teacher app. |
| `test_tutor.py` | `student_app/tutor.py`: leak check, router, prompts, clue ladder, solutions, fallbacks, streaming. |
| `test_planner.py` | The free-mode learning path, with simulated students. |
| `test_easy_read.py` | Easy read: one sentence per line, question last. |
| `test_board_state.py` | Hotspot and phone state, and its endpoint behind the captive portal. |
| `test_services.py` | Teacher app services: setup, assignments, packs, unload, widgets. |
| `test_web.py` | The teacher app's web pages, end to end on a simulated board. |
| `test_learning.py` | The learning-progress widgets: episodes, the class map, the period filter. |
| `test_kangaroo.py` | The Kangaroo library: copy a board's index, browse, make a pack, give homework. |
| `test_demo.py` | The laptop demo builds a consistent classroom. |

Test files must not hold M3Kang problem text (see [`CLAUDE.md`](../CLAUDE.md)):
write invented examples.

## Docs

- Code under test: [`copilot/`](../copilot/README.md), [`classroom/`](../classroom/README.md), [`student_app/`](../student_app/README.md), [`teacher_app/`](../teacher_app/README.md).
