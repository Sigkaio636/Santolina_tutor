# Handoff: plug the decision model into the tutor

Written on 2026-11-15 for Eki, who takes board B1 to plug in the decision model (the intent router). `CLAUDE.md` applies in full, above all the M3Kang red line. Delete this file when the work below is done.

## Before you start: which branch

B1 runs the code of PR #10 (branch `feat/demo-feedback`): faster replies, free mode from the index, homework progress and the LED spinner. That code is release 2. If #10 is merged, start from `main`. If it is not, branch from `feat/demo-feedback`.

Don't work from a `main` without #10. It is still release 1, and a teacher app never replaces a board's code with a lower release: it would leave B1 as it is and show a warning. Your change would also start from the older tutor.

## Where things are

| Part | File | State |
| --- | --- | --- |
| Tutor: clues, chat, solutions | `student_app/tutor.py` | Works on B1 |
| Message labels | `student_app/router.py` | A keyword rule. The decision model goes here |
| Streaming client for the tutor model | `student_app/llm.py` | Works, and feeds the LED "thinking" bar |
| Free mode: next problem | `student_app/planner.py` | Draws from the board's index, never from a loaded pack |
| Teacher app and Kangaroo library | `teacher_app/` | Works. Run it from the branch above |

How it all works for a user is in `docs/how-to/use-student-app.md` (section "The copilot") and `docs/how-to/run-teacher-app.md`.

## How to plug in the decision model

`student_app/router.py` has one function to replace:

```python
classify(problem: str, last_tutor_move: str, message: str) -> str  # one of LABELS
```

`LABELS` are the five of `docs/TOOL_CALLER_PROMPT.md`: `STUCK`, `CONCEPT`, `ATTEMPT`, `SOLUTION` and `OTHER`. The decider-2b guide (`docs/how-to/use-decider-2b-router.md`) writes them in lowercase and calls `OTHER` `not_productive`. Map one set to the other, or change `LABELS` and the tutor together.

`Tutor.reply` in `student_app/tutor.py` handles a chat message like this:

1. A message that names one option ("és la C?") never reaches `classify`. It goes to the answer button, because the tutor model said yes to wrong guesses.
2. `classify` labels the message.
3. `SOLUTION` counts only when the keyword rule `asks_for_solution` agrees, so the model alone never unlocks the solution.
4. `OTHER` gets a fixed redirect. Every other label goes to the tutor model.

So far the label changes the reply only for `OTHER` and `SOLUTION`. The next step is to turn each label into its response type (T0 to T9 in `docs/TUTOR_RESPONSE_TYPES.md`), for example `CONCEPT` into an explanation and `ATTEMPT` into a correction.

Keep these rules:

- Standard library only. The student app runs on the board's Python, without pip.
- `student_app/jobs.py` runs every copilot call in a queue of one, so a router call adds its time to every chat reply. Measure that time on the board.
- When the router's model is down or slow, fall back to the keyword rule. The page must keep working.
- The tutor model reuses its cache only when each prompt extends the previous one (see `Tutor.messages`). If the label goes into the tutor's prompt, add it at the end, never into earlier turns.
- After a change that boards must keep, raise `RELEASE` in `student_app/__init__.py` by one.

## Board B1

| What | Where |
| --- | --- |
| Tutor model | `math-tutor.service`, port 8084, starts at boot |
| Base model and embeddings | `math-llm` (8081) and `math-embed` (8082). Setup in the teacher app checks that both answer |
| Retrieval index | `~/datathon-UPC-maths-qualcomm-arduino-unoq/data/index.db`, problems from 2015 to 2024 |
| Topic labels | `~/santolina/topics.jsonl` |
| Student app | `~/santolina/lib`, port 80, release 2 |
| LED app | App Lab app `user:santolina-leds` |

- The fine-tuned tutor model `qwen35-tutor-Q8_0.gguf` (812 MB) is not on GitHub or Hugging Face. B1 has a copy in `~/models/`. For another board, copy it from B1 (`adb pull /home/arduino/models/qwen35-tutor-Q8_0.gguf`), push it to the new board's `~/models/`, and run `board/08_install_tutor.sh` there.
- Port 8084 is the tutor's. Run the router on 8085; the decider-2b guide now says so.
- With all services running, B1 had 2.6 GB of RAM available. decider-2b Q4_K_M is about 1.3 GB and is not on the board yet: only `decider-0.8b-Q8_0.gguf` is in `~/models`. Check `free -m` after you start it.
- The board asks for a sudo password. Ask Ferran for it, and never guess it.
- B1 restarts when its USB power drops. The services start again by themselves; anything you started by hand does not.
- B1's class (group "3r B", one student) lives in Ferran's teacher store. On your laptop B1 shows up as **New board**. Setting it up again is fine: it keeps the student data on the board and replaces the student codes.

## Try your change without the board

```bash
uv run --group teacher pytest -q tests        # 127 pass on feat/demo-feedback
```

`tests/test_tutor.py` has a `FakeChat`, and shows how to replace `router.classify` with `monkeypatch`. To run the real student app on a laptop against a tutor model there, start the model and set `SANTOLINA_TUTOR_URL` (see "The copilot" in `docs/how-to/use-student-app.md`).

To put new code on B1, open B1's page in the teacher app: it copies the student app when the code changed. Or `adb push` it into `~/santolina/lib` and change `~/santolina/lib/VERSION`. Either way the student app restarts with the new code.

## Known problems

- The tutor model sometimes states a wrong fact ("la suma de les xifres de 200820082008 és 2008"), and the leak check can't catch that. One idea for later is to check the numbers in a reply against the verified programs.
- On B1 the first word comes after 2.5 to 7 s. A whole reply takes 8 to 18 s, because the board writes about 5.7 tokens per second.
- Problems that are not in the index (for example from 2026) get no similar-problem suggestions.
