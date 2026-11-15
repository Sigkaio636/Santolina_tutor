# teacher_app/

The teacher app: a local web app on the teacher's Linux laptop. It sets up
boards, loads exercise packs and assignments, unloads student data into the
teacher store and shows statistics. It talks to boards over USB with `adb` and
serves its pages on `127.0.0.1` only.

## Files

| Path | What it does |
|---|---|
| `__main__.py` | Command line: `serve`, `demo`, `install-shortcut`, `fake-boards`, `simulate`, `demo-pack`, `import-pack`, `m3kang-pack`. |
| `config.py` | Settings, each one changeable with an environment variable (`SANTOLINA_TEACHER_HOME`, `SANTOLINA_TEACHER_PORT`, `SANTOLINA_FAKE_BOARDS`, `SANTOLINA_ADB`). |
| `db.py` | The teacher store (SQLite), centred on students. |
| `strings.py` | Every text the teacher sees. |
| `demo.py` | A complete demo on the laptop, with no hardware. |
| `simulate.py` | Synthetic boards, packs and sessions, for tests and demos. |
| `kangaroo.py` | The Kangaroo library: the solved problems of a board's retrieval index, by topic and level. |
| `m3kang.py` | Turns prepared M3Kang problems (`laptop/prepare_m3kang.py` output) into an exercise pack. |
| `shortcut.py` | Writes a desktop shortcut that starts the app. |
| `links/` | How the app reaches a board: `adb.py` (a real board over USB), `fake.py` (a simulated board in a local folder), `base.py` (the shared interface). |
| `services/` | One module per task: `setup.py` (set up a new board), `boards.py`, `packs.py`, `assignments.py`, `hotspot.py` (hotspot and sticker), `unload.py`. |
| `widgets/` | Statistics on the dashboard and on the group, student and board pages: `base.py` (registry), `starter.py`, `learning.py`. |
| `web/` | FastAPI pages (`main.py`), Jinja templates (`templates/`) and static files (`static/`, vendored libraries listed in `VENDOR.md`). |
| `__init__.py` | Package marker. |

Exercise packs made from M3Kang hold problem text: keep them out of Git (see
[`CLAUDE.md`](../CLAUDE.md)).

## Run

On the laptop, from the repository folder (needs [uv](https://docs.astral.sh/uv/)):

```bash
make teacher
```

It runs `uv run --group teacher python -m teacher_app serve` and opens
http://127.0.0.1:8010. A demo with simulated boards and no hardware:

```bash
uv run --group teacher python -m teacher_app demo
```

`uv run --group teacher python -m teacher_app --help` lists every command.
Tests: `make test` (see [`tests/`](../tests/README.md)).

## Docs

- [Run the teacher app](../docs/how-to/run-teacher-app.md).
- [Use the student app](../docs/how-to/use-student-app.md) and [Back up and restore a board](../docs/how-to/back-up-and-restore-a-board.md).
- [Board data contract](../docs/reference/board-data-contract.md) and [Student data privacy](../docs/explanation/student-data-privacy.md).
- Terms: [GLOSSARY.md](../GLOSSARY.md) (Teacher app, Teacher store, Exercise pack, Assignment, Unload, Group, Student code, Sticker).
