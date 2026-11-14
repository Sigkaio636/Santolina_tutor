# Back up and restore a working board

Use this page before you change the student app, the teacher app or the models of a board that works. It shows how to save the working state, and how to go back to it if something breaks.

## Know what changes the board

The **teacher app copies the laptop's code to the board.** This happens when you set up a board, or when you open the page of a board that you plugged in. The teacher app then copies `classroom/` and `student_app/` from your laptop's working tree to `~/santolina/lib` on the board. It deletes the old copy, and the student app restarts with the new code. Code that does not import stops the student app: systemd starts it again every 2 seconds, and it fails each time.

So, before you plug a board into the teacher app:

1. Commit your change, or stash it, so the working tree holds code that works.
2. Run the tests: `uv run --group teacher pytest`.
3. Try the change in the demo first: `uv run --group teacher python -m teacher_app demo` (see [Use the student app](use-student-app.md#try-it-on-the-laptop)).

Other things that change a board:

| Change | What it touches |
|---|---|
| `./board/04_install_services.sh` | The model services `math-llm` and `math-embed`. A different model in `config.env` replaces the model on port 8081 |
| **Set up this board** in the teacher app | The code, the Wi-Fi profile, the roster and `identity.json`. The student data stays |
| A different Wi-Fi network on the board | The board's own Wi-Fi goes off, and phones lose the board |

## Back up the working state

Do this on the laptop, with the board plugged in. Put the backup **outside the repository**: it holds student data, which never goes into Git.

```bash
B=~/Documents/DATATHON/backups/$(date +%F)-board-ok
mkdir -p "$B/board" "$B/teacher"

# The board: student data, the code it runs, the LED app, the services, the captive portal
adb pull /home/arduino/santolina "$B/board/"
adb pull /home/arduino/ArduinoApps/santolina-leds "$B/board/"
for f in /etc/systemd/system/santolina-student.service \
         /etc/systemd/system/math-llm.service \
         /etc/systemd/system/math-embed.service \
         /etc/NetworkManager/dnsmasq-shared.d/santolina-captive.conf; do
  adb pull "$f" "$B/board/"
done

# The teacher database: a consistent copy, safe while the teacher app runs
T=~/.local/share/santolina-teacher
python3 -c "import sqlite3,sys; s=sqlite3.connect(f'file:{sys.argv[1]}?mode=ro', uri=True); d=sqlite3.connect(sys.argv[2]); s.backup(d); d.close()" \
  "$T/teacher.sqlite3" "$B/teacher/teacher.sqlite3"
cp -r "$T/packs" "$T/raw" "$B/teacher/"

chmod -R go-rwx "$B"
```

`adb pull` of the LED app warns about three missing `python` links in `.cache/.venv`. You can ignore this: App Lab makes the `.cache` folder again.

Then mark the code that works with a Git tag, and push it:

```bash
git tag -a board-ok-$(date +%F) -m "What works on the board at this commit"
git push origin board-ok-$(date +%F)
```

The tag `board-ok-2026-11-14` marks the first state that worked from setup to exercises on a phone.

## Restore

Restore only the part that broke. In the commands, `$B` is the backup folder.

### The student app code

With the teacher app:

1. On the laptop, run `git checkout board-ok-2026-11-14` (or your newest `board-ok-` tag).
2. Start the teacher app and open the board's page. The teacher app copies that code to the board, and the student app restarts.
3. Go back to your branch with `git checkout -`. Do not open the board's page again before your code works.

Without the teacher app, from the backup:

```bash
adb push "$B/board/santolina/lib" /home/arduino/santolina/lib.restore
adb shell 'cd ~/santolina && rm -rf lib && mv lib.restore lib'
```

Then, in your own terminal on the board: `sudo systemctl restart santolina-student`.

### The student data

The files in `~/santolina` (roster, progress, sessions, exercises) come back with `adb push`. For example, for the progress of the students:

```bash
adb push "$B/board/santolina/progress/." /home/arduino/santolina/progress/
```

A session file pushed back into `outbox/` is safe to unload again: the teacher app skips the events it already has.

### The model services

Copy the saved service files to the board, then install them in your own terminal on the board:

```bash
adb push "$B/board/math-llm.service" "$B/board/math-embed.service" /home/arduino/
```

```bash
sudo cp ~/math-llm.service ~/math-embed.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl restart math-llm math-embed
```

The model files stay in `~/models`, so a restore downloads nothing.

### The board's Wi-Fi

If the board joined another network, turn its own Wi-Fi on again on the board with `nmcli connection up santolina-hotspot`, or restart the board. If the Wi-Fi profile is gone, run **Set up this board** again in the teacher app. It keeps the password in `~/santolina/hotspot.json`, so the printed sticker stays valid.

### The teacher database

Stop the teacher app first. Then:

```bash
cp "$B/teacher/teacher.sqlite3" ~/.local/share/santolina-teacher/teacher.sqlite3
```

## Check that it works again

On the board:

```bash
systemctl is-active santolina-student math-llm math-embed    # three times "active"
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1/api/info    # 200
arduino-app-cli app ps                                        # santolina-leds: running
```

Then join the board's Wi-Fi with a phone, log in with a student code and answer one exercise.
