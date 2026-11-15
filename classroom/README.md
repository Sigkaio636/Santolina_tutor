# classroom/

This package implements the [board data contract](../docs/reference/board-data-contract.md):
the files a board keeps under `~/santolina/` and their JSON formats. Read it
before you change what the student app writes or what the teacher app reads.
It uses only the Python standard library, so it runs on the board and on the
laptop. The student app (board) and the teacher app (laptop) both import it.
The teacher app copies it to `~/santolina/lib/classroom/` on each board (when:
see the reference).

## Files

| File | What it does |
|---|---|
| `__init__.py` | Package marker and `CONTRACT_VERSION`, the version of the board data contract that each board records. |
| `paths.py` | Where each file lives under the board root: `~/santolina/` on a board, any folder in tests and simulated boards (`--root`). |
| `schemas.py` | The records of the board data contract, and how readers treat versions and unknown fields. |
| `events.py` | Student activity: one session file per session in `~/santolina/outbox/`, one event per line. Lines are only ever added. |
| `packs.py` | Exercise packs: a folder with `manifest.json`, `exercises.json` and optional `media/`. |
| `progress.py` | What each student has done on this board, in `progress/<code>.json`. Student codes only, never names. |
| `status.py` | Prints the state of a board as one JSON line. It only reads. |

## Run

The teacher app runs `status.py` on the board over `adb`, after setup has
copied the package there:

```bash
cd ~/santolina/lib && python3 -B -m classroom.status --root ~/santolina
```

On the laptop, from the repository folder, add `--no-services` to skip the
model service checks: `python3 -m classroom.status --root <folder> --no-services`.

Tests: `uv run --group teacher pytest tests/test_classroom.py` (see [`tests/`](../tests/README.md)).

## Docs

- [Board data contract](../docs/reference/board-data-contract.md): every file and field, and the version rules.
- [Student data privacy](../docs/explanation/student-data-privacy.md).
- Terms: [GLOSSARY.md](../GLOSSARY.md) (Board data contract, Student app, Teacher app, Session, Event, Exercise pack, Student code).
