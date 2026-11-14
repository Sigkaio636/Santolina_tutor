# Run the teacher app

The teacher app runs on the teacher's laptop. With it you set up boards, load exercise packs onto them, unload what the students did, and see statistics per class, per student and per board.

During class a board works on its own. Students use it from a phone, and no computer is attached. You plug a board into the laptop with its USB-C cable only to set it up, load exercises or unload data.

## Before you start

- **Linux laptop** with [uv](https://docs.astral.sh/uv/) and `adb` (`sudo dnf install android-tools` on Fedora). See the udev rule in [the board reference](../UNO_Q_BOARD_REFERENCE.md) if `adb devices` shows the board as `no permissions`.
- **A ready board.** App Lab first setup is done, and the copilot is installed with the scripts in `board/`: the model services answer, and the retrieval index `~/Santolina_tutor/data/index.db` exists (Step 12 of [the board setup guide](../BOARD_SETUP.md)). Setup in the app stops with a clear message if any of this is missing.

## Start the app

```bash
make teacher
```

The app opens at <http://127.0.0.1:8010>. It listens on this computer only, and works without internet.

To start it with a double click instead, add a **Santolina Teacher** shortcut (a graduation cap icon) to the desktop and the applications menu, once:

```bash
uv run --group teacher python -m teacher_app install-shortcut
```

The shortcut opens the app in the browser. If the app is already running, it only opens the browser. Messages go to `~/.local/state/santolina-teacher.log`. The app keeps running until you log out. If you move the repository, run the command again.

Your data goes to `~/.local/share/santolina-teacher/`: the teacher store (`teacher.sqlite3`), a raw copy of every file unloaded from a board (`raw/`) and the exercise pack library (`packs/`). Set `SANTOLINA_TEACHER_HOME` to use another folder. It is outside the repository, so it never goes into Git.

## Set up a new board

1. Add a **group** (for example "3r ESO B") and its **students** in the app. Each student gets a code, such as `K7M2`. Students type this code on the board. The board never sees their names.
2. Plug the board in. After up to a minute, it appears in **Connected boards** as *New board*.
3. Click **Set up this board**, give it a name (for example "Board 7") and pick the group.
4. Write the name on a sticker on the board.

Setup copies the board module to `~/santolina/lib/`, checks that the board is ready, writes the board's files, sets **student mode**, and sends the group's student codes.

## Load exercises

1. On **Exercise packs**, import a pack folder, or click **Create a demo pack** to try with synthetic exercises.
2. Open the connected board, pick the pack and click **Load pack**.

To build a pack from M3Kang (research use only, written outside the repository):

```bash
uv run --group teacher python -m teacher_app m3kang-pack \
  --source data/val.jsonl --pack-id kangaroo-l0 --title "Kangaroo level 0" \
  --languages eng,cat --levels 0 --limit 30
```

## Unload student data

Open the connected board and click **Unload student data**. The app copies every finished session, adds it to the teacher store, and moves the files on the board to its archive. Sessions still in progress stay on the board for the next time. Unloading twice never counts anything twice.

Sessions whose code doesn't match a student appear in **Unassigned**. Pick the student they belong to there.

**Delete unloaded data from the board** empties the board's archive. The data is already on the laptop.

## Lock and unlock a board

On the board page, **Unlock (professor mode)** and **Lock (student mode)** switch the mode. Only the app changes it, so plugging the board into your laptop is the key.

## Try it without a board

```bash
export SANTOLINA_FAKE_BOARDS=/tmp/fake-boards SANTOLINA_TEACHER_HOME=/tmp/teacher-demo
uv run --group teacher python -m teacher_app fake-boards --dir $SANTOLINA_FAKE_BOARDS --n 3
make teacher
```

The simulated boards appear as connected. After you set one up in the app, write synthetic student sessions on it, then unload them:

```bash
uv run --group teacher python -m teacher_app simulate --dir $SANTOLINA_FAKE_BOARDS FAKE0001
```

## Add a statistic

Statistics are widgets in `teacher_app/widgets/`. Write one function that queries the teacher store and returns `kpis`, `bar`, `line` or `table` data, and decorate it with `@widget(...)`. It appears on the pages whose scope it lists (`global`, `group`, `student`, `board`). See `teacher_app/widgets/base.py`.
