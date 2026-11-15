# Use the student app

Each student gets a board. The board makes its own Wi-Fi, and the student uses it from a phone (or a laptop) with no internet and no app to install. Everything the student does is saved on the board. The teacher unloads it later with the [teacher app](run-teacher-app.md).

## Prepare a board (teacher, once per board)

1. **Get the board ready.** Follow [the board setup guide](../BOARD_SETUP.md): the copilot with its model services and the retrieval index.
2. **Install the student app at boot.** On the board, from the repository folder:

    ```bash
    ./board/06_install_student_app.sh
    ```

    It asks for the `sudo` password once. It makes every web address on the board's Wi-Fi lead to the board, and starts the student app on port 80 at every boot.

3. **Show the Wi-Fi status on the LED matrix** (optional). While the board still has internet:

    ```bash
    ./board/07_install_led_app.sh
    ```

    It installs a small App Lab app that starts at every boot. While the board's Wi-Fi waits for a phone, the matrix shows a Wi-Fi symbol whose waves grow from the dot. Once a phone is connected, a check mark draws itself and bounces for a few seconds, then a happy face stays, blinking now and then. With the Wi-Fi off, the matrix stays dark. The first start downloads App Lab's Python image, which is why it needs internet.

4. **Set the board up in the teacher app.** Plug it in and click **Set up this board**. Setup copies the student app, creates the board's Wi-Fi (`Santolina-<board name>`, with its own password) and sends the group's student codes.
5. **Print the sticker.** On the board page, click **Print the sticker** and stick it on the board's case. It shows the board's name, a QR code that joins the Wi-Fi, the password (for laptops) and the address `http://10.42.0.1`.
6. **Restart the board.** The Wi-Fi starts at boot. From then on the board no longer joins other Wi-Fi networks; the teacher app still reaches it over USB.

## What the student does

1. **Turn the board on.** It takes about a minute: the board starts in about 30 seconds, and the models need a little longer.
2. **Scan the QR code** on the sticker with the phone camera, and accept joining the network. The phone opens the app by itself. If it doesn't, open the browser and type `http://10.42.0.1`.
3. **Type their code** (for example `K7M2`). The app asks for it on every visit.
4. **Pick what to do:**
    - **Continue**: the last exercise left unfinished.
    - **Homework**: what the teacher assigned, with what is done and what is left.
    - **Practice**: every exercise on the board, grouped by topic (or by level when a pack has no topics).
    - **Free mode**: a conversation. Problems appear in it one by one, the student can ask anything, and the copilot can suggest other problems.

On an exercise the student taps an option and sees at once whether it's right. A wrong option is greyed out, and they can try again. **Clue** gives a hint. **Show the solution** appears after the first wrong answer: it gives the right letter, with the pack's worked solution when there is one, and the exercise counts as "done with help". Below, they can ask questions about the problem, with a photo if they want.

**Aa**, at the top of every screen, opens two reading switches. Both are off at first, and each works without the other:

- **Easy-to-read font**: a larger, more spaced font (Atkinson Hyperlegible) in which similar characters such as 0 and O are hard to confuse. The board serves the font, so it needs no internet.
- **Easy read**: the problem text with one sentence per line and the question last. The words and numbers don't change.

The phone remembers the switches. The board doesn't save them, so the teacher can't see who uses them.

**Tell the students:** turn mobile data off while using the board. Otherwise some phones leave the board's Wi-Fi because it has no internet.

## What is saved

Every action is saved on the board as events: answers (which option, which try, how long), clues, solutions, questions and the copilot's replies, problems left unfinished, and time spent in other apps. Photos are not saved, only their size. The full list is in [the board data contract](../reference/board-data-contract.md).

The teacher unloads it by plugging the board in. Each session has a timeline on the student's page in the teacher app.

## The copilot

Clues, solutions and chat replies come from `student_app/tutor.py`. It runs the fine-tuned tutor model (Qwen3.5 0.8B, `qwen35-tutor-Q8_0.gguf`) as `math-tutor.service` on port 8084. The model answers with one short question that guides the student, in the language of the visit.

To install it on a board:

1. On the laptop: `adb push qwen35-tutor-Q8_0.gguf /home/arduino/models/`
2. On the board, from the repository: `./board/08_install_tutor.sh`. It starts the service and asks the model for one clue.

What each request does:

| Request | What the student gets | Model call |
| --- | --- | --- |
| Clue 1 | Where to start | Yes |
| Clue 2 | A more concrete hint, and a similar easier problem from the retrieval index when there is one | Yes |
| Clue 3 and later | The next step | Yes |
| A chat message | A guiding reply. `student_app/router.py` first labels the message `STUCK`, `CONCEPT`, `ATTEMPT`, `SOLUTION` or `OTHER` | Yes |
| A message that names an option ("is it D?") | A request to send it with the answer button, which counts the attempt | No |
| An empty or unreadable message | A request to talk about the problem | No |
| "Another problem" in free mode | A problem the student has not opened in this visit | No |
| Show the solution | The pack's `meta.solution` when it has one, else the right option and a request to explain it back | No |

Code checks every model reply for leaks. A fixed hint replaces any reply that names the right option, points at any option as the answer, or holds the right value when the statement does not. The same fixed hints keep the app working when the model service is down. Each `copilot_reply` event records how the reply was made: `route`, `label`, `tokens`, `prompt_tokens`, `model_seconds`, `first_token_seconds`, and `leak_blocked` when the check replaced a reply.

Limits to know before a demo:

- The model cannot check the student's arithmetic. It accepts a wrong intermediate step, and it sometimes gets a step wrong itself.
- It does not write worked solutions, and the base model writes wrong ones, so the app generates none. To show a worked solution, write it into the pack as `meta.solution` on the laptop.
- It cannot read photos. A photo gets a note that asks for the problem in words.
- The router is a keyword rule. The decision model will replace `router.classify` and keep the same five labels.
- The time per reply on the board is not measured yet. On a laptop it is 2 to 8 seconds.

While the model writes, `GET /api/board-state` returns `"thinking": {"tokens": n, "max": m}` and the LED matrix fills its "thinking" bar. The rest of the time `thinking` is `null`.

To try the copilot on the laptop, start the model on any free port and point the app at it with `SANTOLINA_TUTOR_URL`:

```bash
~/llama.cpp/build/bin/llama-server -m qwen35-tutor-Q8_0.gguf --port 8095 --ctx-size 2048 --jinja --reasoning off
SANTOLINA_TUTOR_URL=http://127.0.0.1:8095 uv run --group teacher python -m teacher_app demo
```

## How free mode picks the next problem

Free mode uses a fixed rule (`student_app/planner.py`). The rule uses no language model, so the next problem comes at once.

| The last problem | Level of the next | Topic of the next | `path_reason` |
| --- | --- | --- | --- |
| None yet | Start level | Any | `start` |
| Solved with no wrong answer and no clue | One level up | Same | `harder_after_solve` |
| The same, three times in a row | Same | Other | `new_topic_after_mastery` |
| Solved after a wrong answer or a clue | Same | Same | `same_level_after_help` |
| Failed: two wrong answers, or the solution shown | One level down | Same | `easier_after_fail` |
| Skipped | Same | Other | `other_topic_after_skip` |

The start level is the highest level that the student solved at the first try on this board. For a new student, it is the middle level of the packs.

The same topic means the nearest problem in the retrieval index (`build_index.py`). The other topic means the problem farthest from the last five problems. The rule finds a problem in the index by its M3Kang ID. An exercise that is not in the index uses the topic of its pack instead. If the pack gives no topic, the rule picks a problem of the correct level by chance.

The rule does not show a problem twice, and it prefers problems in the language of the visit.

## Stop, start and check the app on a board

The app on a board has two parts. Both start at every boot:

| Part | What it is | Name |
|---|---|---|
| Student app | the web page on port 80 (systemd service) | `santolina-student` |
| LED app | the Wi-Fi status on the LED matrix (App Lab app) | `user:santolina-leds` |

Run these commands on the board (`adb shell` or `ssh`). The `systemctl` commands that change a service need the `sudo` password. Run them in your own terminal.

**Check:**

```bash
systemctl is-active santolina-student    # prints "active" when it runs
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1/api/info    # prints 200
arduino-app-cli app ps                   # santolina-leds: running
```

**Stop** (for example, to free the CPU for a long test):

```bash
sudo systemctl stop santolina-student
arduino-app-cli app stop user:santolina-leds
```

**Start again:**

```bash
sudo systemctl start santolina-student
arduino-app-cli app start user:santolina-leds
```

`stop` does not disable the app: both parts start again at the next boot. To keep the student app off after a reboot as well, use `sudo systemctl disable --now santolina-student`, and `sudo systemctl enable --now santolina-student` to undo it.

Stopping the app deletes nothing. The student data stays in `~/santolina`, and the board's Wi-Fi stays on. The two model services (`math-llm`, `math-embed`) are separate and keep running. If the student app does not start, read its log with `journalctl -u santolina-student -n 50`.

## Try it on the laptop

Double-click **Santolina Demo** on the desktop, or run:

```bash
uv run --group teacher python -m teacher_app demo
```

It builds a made-up class in its own folder (`~/.local/share/santolina-teacher-demo`, apart from your real data): 5 students, 3 simulated boards set up for their group, a pack, homework, and some past sessions already unloaded. Then it starts:

- the **teacher app** with that data, at <http://127.0.0.1:8012>;
- the **student app of Board 1**, at `http://<this computer's address>:8081`.

The teacher app shows a banner with the student app's address and a QR code. On a phone, **join the same Wi-Fi as the computer**, scan the QR code, and log in with a code from **Students**. Then unload Board 1 in the teacher app to see the session.

`--reset` throws the demo data away and builds it again. Messages, including every request the student app receives, go to `~/.local/state/santolina-demo.log` when started from the shortcut.
