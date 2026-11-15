# classroom/

The board data contract in code: the files a board keeps under `~/santolina/`
and their JSON formats. It uses only the standard library, so it runs on the
board and on the laptop. The student app (board) and the teacher app (laptop)
both import it. The teacher app copies it to `~/santolina/lib/classroom/` on
every board.

## Files

| File | What it does |
|---|---|
| `__init__.py` | Package marker and `CONTRACT_VERSION`. |
| `paths.py` | Where each file lives under the board root (`~/santolina/` on a real board). |
| `schemas.py` | The records of the contract. Every file and event carries `schema_version`; readers ignore fields they do not know. |
| `events.py` | Student activity as append-only event files, one file per session in `outbox/`. |
| `packs.py` | Exercise packs: a folder with `manifest.json`, `exercises.json` and optional `media/`. |
| `progress.py` | What each student has done on this board, in `progress/<code>.json`. Student codes only, never names. |
| `status.py` | Prints the state of a board as JSON. It only reads. |

## Run

The teacher app runs `status.py` on the board over `adb`:

```bash
cd ~/santolina/lib && python3 -m classroom.status --root ~/santolina
```

Nothing else here runs on its own. Tests: `make test` (see
[`tests/`](../tests/README.md)).

## Docs

- [Board data contract](../docs/reference/board-data-contract.md): every file and field.
- [Student data privacy](../docs/explanation/student-data-privacy.md).
- Terms: [GLOSSARY.md](../GLOSSARY.md) (Board data contract, Session, Event, Exercise pack, Student code, Mode).
