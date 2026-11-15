# teacher_app/

The teacher app: a local web app on the teacher's Linux laptop. It sets up
boards, loads exercise packs and assignments, unloads student data into the
teacher store and shows statistics. This README is for people who change its
code. Teachers start with [Run the teacher app](../docs/how-to/run-teacher-app.md).
It talks to boards over USB with `adb` (Android Debug Bridge). Its pages open
only on the laptop itself (`127.0.0.1`).

## Files

| Path | What it does |
|---|---|
| `__main__.py` | Command line: `serve`, `demo`, `install-shortcut`, `fake-boards`, `simulate`, `demo-pack`, `import-pack`, `m3kang-pack`. |
| `config.py` | Settings. Most can be changed with an environment variable (`SANTOLINA_TEACHER_HOME`, `SANTOLINA_TEACHER_PORT`, `SANTOLINA_FAKE_BOARDS`, `SANTOLINA_ADB`, `XDG_DATA_HOME`). |
| `db.py` | The teacher store (SQLite), centred on students. |
| `strings.py` | Every text the teacher sees. |
| `demo.py` | A complete demo on the laptop, with no hardware. |
| `simulate.py` | Synthetic boards, packs and sessions, for tests and demos. |
| `kangaroo.py` | The Kangaroo library page: the solved M3Kang problems of a board's Index, by topic and level ([Choose Kangaroo problems by topic](../docs/how-to/run-teacher-app.md#choose-kangaroo-problems-by-topic)). |
| `m3kang.py` | Turns prepared [M3Kang](../GLOSSARY.md) problems (`laptop/prepare_m3kang.py` output) into an exercise pack. |
| `shortcut.py` | Writes a desktop shortcut that starts the app. |
| `links/` | How the app reaches a board: `adb.py` (a real board over USB), `fake.py` (a simulated board in a local folder), `base.py` (the shared interface). |
| `services/` | One module per task: `setup.py` (set up a new board), `boards.py` (read and change a connected board), `packs.py` (exercise packs), `assignments.py` (homework), `hotspot.py` (hotspot and sticker), `unload.py` (unload student data). |
| `widgets/` | Statistics on the dashboard and on the group, student and board pages: `base.py` (registry), `starter.py` (first statistics), `learning.py` (learning progress). |
| `web/` | The web pages: `main.py` (FastAPI routes), `templates/` (Jinja HTML templates), `static/` (CSS, JavaScript, and third-party libraries listed in `VENDOR.md`). |
| `__init__.py` | Package marker. |

Exercise packs made from M3Kang hold problem text: keep them out of Git (see
[`CLAUDE.md`](../CLAUDE.md)).

## Run

On the laptop, from the repository folder. It needs [uv](https://docs.astral.sh/uv/),
and `adb` for real boards (setup and the udev rule:
[Before you start](../docs/how-to/run-teacher-app.md#before-you-start)).

```bash
make teacher
```

It runs `uv run --group teacher python -m teacher_app serve` and opens
`http://127.0.0.1:8010` in the browser. A demo with simulated boards and no
hardware (teacher app on port 8012, a student app on port 8081):

```bash
uv run --group teacher python -m teacher_app demo
```

`uv run --group teacher python -m teacher_app --help` lists every command.
Tests: see [`tests/`](../tests/README.md).

## Docs

- [Run the teacher app](../docs/how-to/run-teacher-app.md): every task, step by step.
- [Use the student app](../docs/how-to/use-student-app.md): prepare a board and try the demo.
- [Back up and restore a board](../docs/how-to/back-up-and-restore-a-board.md).
- [Board data contract](../docs/reference/board-data-contract.md): the files the app reads and writes on a board.
- [Student data privacy](../docs/explanation/student-data-privacy.md): what is stored and why.
- Terms: [GLOSSARY.md](../GLOSSARY.md) (Teacher app, Teacher store, M3Kang, Index, Exercise pack, Assignment, Unload, Group, Hotspot, Sticker).
