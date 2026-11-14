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

On an exercise the student taps an option and sees at once whether it's right. A wrong option is greyed out, and they can try again. **Clue** gives a hint. **Show the solution** appears after the first wrong answer: it gives the explanation and the right letter, and the exercise counts as "done with help". Below, they can ask questions about the problem, with a photo if they want.

**Tell the students:** turn mobile data off while using the board. Otherwise some phones leave the board's Wi-Fi because it has no internet.

## What is saved

Every action is saved on the board as events: answers (which option, which try, how long), clues, solutions, questions and the copilot's replies, problems left unfinished, and time spent in other apps. Photos are not saved, only their size. The full list is in [the board data contract](../reference/board-data-contract.md).

The teacher unloads it by plugging the board in. Each session has a timeline on the student's page in the teacher app.

## The copilot is not connected yet

Clues, solutions and chat replies come from a stand-in (`student_app/tutor.py`), and free mode picks problems with a simple rule (`student_app/planner.py`): a random one, or an easier one after a failure. Replace those two classes to connect the real copilot. The interface doesn't change.

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
