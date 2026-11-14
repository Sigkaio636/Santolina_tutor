# Use the student app

Each student gets a board. The board makes its own Wi-Fi, and the student uses it from a phone (or a laptop) with no internet and no app to install. Everything the student does is saved on the board. The teacher unloads it later with the [teacher app](run-teacher-app.md).

## Prepare a board (teacher, once per board)

1. **Get the board ready.** Follow [the board setup guide](../BOARD_SETUP.md): the copilot with its model services and the retrieval index.
2. **Install the student app at boot.** On the board, from the repository folder:

    ```bash
    ./board/06_install_student_app.sh
    ```

    It asks for the `sudo` password once. It makes every web address on the board's Wi-Fi lead to the board, and starts the student app on port 80 at every boot.

3. **Set the board up in the teacher app.** Plug it in and click **Set up this board**. Setup copies the student app, creates the board's Wi-Fi (`Santolina-<board name>`, with its own password) and sends the group's student codes.
4. **Print the sticker.** On the board page, click **Print the sticker** and stick it on the board's case. It shows the board's name, a QR code that joins the Wi-Fi, the password (for laptops) and the address `http://10.42.0.1`.
5. **Restart the board.** The Wi-Fi starts at boot. From then on the board no longer joins other Wi-Fi networks; the teacher app still reaches it over USB.

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

```bash
export SANTOLINA_FAKE_BOARDS=/tmp/fake-boards
uv run --group teacher python -m teacher_app fake-boards --dir $SANTOLINA_FAKE_BOARDS --n 1
make teacher          # set FAKE0001 up, add students, a pack and some homework
uv run python -m student_app.server --root /tmp/fake-boards/FAKE0001/santolina --port 8080 --host 0.0.0.0
```

Open `http://localhost:8080` on the laptop, or `http://<laptop IP>:8080` on a phone on the same Wi-Fi. Log in with a student code from the teacher app. Then unload FAKE0001 in the teacher app to see the session.
