# How to use the copilot on the UNO Q

This how-to guide is for a team member who deployed the copilot on the Arduino UNO Q. It shows how to answer problems, measure the result, and compare experiments. All commands run on the board, from `~/Santolina_tutor`, unless the text says "on your laptop".

The organizers of the Qualcomm challenge (Datathon FME 2026) wrote the [board setup](../BOARD_SETUP.md). This guide repeats some of its steps for our copilot, and links each step that it replaces.

The code calls the project the *copilot*. See the [glossary](https://github.com/Sigkaio636/Santolina_tutor/blob/main/GLOSSARY.md).

## Before you start

- You deployed the copilot. If not, follow [How to deploy the copilot on the UNO Q](deploy-copilot-on-board.md).
- Both model services answer:

  ```bash
  curl http://127.0.0.1:8081/health; echo
  curl http://127.0.0.1:8082/health; echo
  ```

  You should see `{"status":"ok"}` twice. If not, run `sudo systemctl start math-llm math-embed`.
- `data/val.jsonl` is on the board. For retrieval, and for the similar problems in the explorer, `data/index.db` must exist too.
- On your laptop, the variable `BOARD_IP` holds the board's IP address. See step 1 of the [deploy guide](deploy-copilot-on-board.md#1-set-the-boards-ip-address).

## Answer a file of problems

This section replaces [step 11.1](../BOARD_SETUP.md#111-how-the-baseline-works) of the board setup.

`predict.py` is the program that the organizers run on the hidden test. The hidden test is their own set of problems, which the team never sees.

```bash
python3 predict.py --input data/val.jsonl --output results/predictions.csv
```

This command answers every problem in `data/val.jsonl`. For a quick try, use `--input data/sample_problems.jsonl`.

While it runs, you should see one line per problem, in the form `[n/total] <id> -> <letter> in <seconds> s (<status>)`.

The output is a CSV file with one row per problem:

| Column | Meaning |
| --- | --- |
| `id` | The problem ID from the input |
| `language` | The language from the input |
| `answer` | One letter, A to E |
| `seconds` | The time the problem took |
| `status` | `ok`, `timeout`, or `error: <reason>` |

If the request times out, or a model service is down or returns an error, the answer is `D`, and the `status` tells you why.

**The [contract](https://github.com/Sigkaio636/Santolina_tutor/blob/main/GLOSSARY.md).** Keep these rules in every change you make:

- One letter, A to E, for every problem.
- At most 60 seconds per problem. The code keeps 3 seconds free for Python and for writing the answer.
- No network. Only the services on `127.0.0.1`.
- The same answers every time: temperature 0 and the `SEED` from [`config.env`](https://github.com/Sigkaio636/Santolina_tutor/blob/main/config.env).

`config.env` sets the time limit in `TIME_LIMIT_SECONDS` and the fallback letter in `FALLBACK_ANSWER`.

## Measure the result

This section replaces [step 11.2](../BOARD_SETUP.md#112-run-the-evaluation) of the board setup.

`eval.py` answers problems from the validation set and compares the answers with the labels:

```bash
python3 eval.py --limit 50 --name baseline
```

| Option | What it does |
| --- | --- |
| `--limit N` | Use N problems. The default is 50. `0` means every problem |
| `--languages eng,cat` | Use only these languages |
| `--rag K` | Add K similar solved problems to each prompt |
| `--name <label>` | A label for this experiment in the results file |
| `--input <file>` | Use another problem file. The default is `data/val.jsonl` |

The report shows:

- **Accuracy**, next to two numbers to beat: always answering `D`, and random guessing (20%).
- **Latency**: mean, median, worst, and how many problems exceeded the limit.
- Accuracy by language, by level, and with or without options.
- **Letter counts**, predicted against true. A model that picks one letter far too often shows here.

Each experiment writes two files in `results/`:

- `results/eval-<time>-<name>.csv`: one row per problem.
- `results/ablations.csv`: one line per experiment, with the Git commit. Take every result that you report in the [root README](https://github.com/Sigkaio636/Santolina_tutor/blob/main/README.md) from this file.

With `--languages eng,cat` in step 9, `data/val.jsonl` holds about 281 English and 281 Catalan problems. The organizers measured about 45 minutes for 281 problems ([step 11.2](../BOARD_SETUP.md#112-run-the-evaluation)). An experiment on the whole file takes longer. Use `--limit` for fast checks.

Say how many problems a number comes from. The [publish-project skill](https://github.com/Sigkaio636/Santolina_tutor/blob/main/.claude/skills/publish-project/SKILL.md) asks you to say so when a result comes from 50 problems or fewer. Such a result is weak evidence.

## Use retrieval

This section replaces [step 12.2](../BOARD_SETUP.md#122-use-it) of the board setup.

Retrieval adds similar solved problems, with their answers, to the prompt of the language model. Build the index first (step 5 of the [deploy guide](deploy-copilot-on-board.md#5-build-the-retrieval-index-optional)). Then:

```bash
python3 eval.py --limit 50 --rag 1 --name rag1
python3 predict.py --input data/val.jsonl --output results/predictions-rag1.csv --rag 1
```

`--rag 1` adds the most similar training problem, with its answer. `--rag 2` adds two. `eval.py` never retrieves the problem it answers, so the score stays honest.

Each example makes the prompt longer. On our board the language model reads about 10.1 tokens per second ([UNO Q board reference, §14.3](../UNO_Q_BOARD_REFERENCE.md#143-speed)). So every example adds seconds. Compare the latency columns, not only the accuracy.

## View the problems in a browser

This section replaces the [optional explorer step](../BOARD_SETUP.md#optional-explore-the-problems-in-your-browser) of the board setup.

The explorer shows each validation problem, with its image and the options that optical character recognition (OCR) read. You can answer it yourself, or ask the language model. If `data/index.db` exists, it also shows the three most similar training problems.

The explorer needs the problem images. On your laptop, from the repository folder, make them again with the command of step 9.2 plus `--save-images`. `prepare_m3kang.py` caches the OCR results, so the second run is quicker:

```bash
uv run --no-project --python 3.12 --with-requirements laptop/requirements.txt \
  python laptop/prepare_m3kang.py --languages eng,cat --save-images
```

Then copy `data/images` to the board. On your laptop:

```bash
scp -r data/images arduino@"$BOARD_IP":~/Santolina_tutor/data/
```

Or, over USB:

```bash
adb push data/images /home/arduino/Santolina_tutor/data/
```

The images are M3Kang data: do not commit them.

On the board:

```bash
python3 explorer/server.py
```

You should see three lines. The first counts the problems, the images, and the problems in the retrieval index. The second should say `language model up, embeddings up`. The third says `Open http://127.0.0.1:8000 (Ctrl+C to stop)`.

The explorer listens only on the board, on port 8000. The board setup starts it with `--host 0.0.0.0`, which opens it to your whole network. The tunnel below does not need that option.

To open it on your laptop, forward the port. On your laptop, in a second terminal, set `BOARD_IP` again. Then run:

```bash
ssh -L 8000:127.0.0.1:8000 arduino@"$BOARD_IP"
```

Or, over USB:

```bash
adb forward tcp:8000 tcp:8000
```

Keep the `ssh` terminal open while you use the explorer. Then open <http://127.0.0.1:8000>. Press Ctrl+C on the board to stop the explorer.

Port 8001 belongs to the documentation site on your laptop. Do not use it for the explorer.

## Free the ports for a hand-started server

The board has 3.6 GiB of RAM. The two model services use about 920 MiB ([UNO Q board reference, §14.4](../UNO_Q_BOARD_REFERENCE.md#144-build-and-services)).

To start a server by hand with other options, stop both model services first. Only one program can use a port:

```bash
sudo systemctl stop math-llm math-embed
systemctl is-active math-llm math-embed
```

You should see `inactive` twice.

Start the services again when you finish:

```bash
sudo systemctl start math-llm math-embed
systemctl is-active math-llm math-embed
```

You should see `active` twice.

Do not leave a hand-started server running. If teammates share the board with you, do not stop servers that they started.

## Prepare the demo

This section replaces part of [step 14.5](../BOARD_SETUP.md#145-prepare-the-demo-and-the-pitch) of the board setup.

The organizers see the copilot work on the board, with the Wi-Fi off.

- Both services start at boot. Check with `systemctl is-enabled math-llm math-embed`: both say `enabled`.
- Nothing in your code may download data at run time.
- If a web page runs on your laptop, connect over USB and use `adb forward`, as above.
- Choose the demo problems in advance. Run them on the board on the day of the demo. Time each one.
- Before you unplug the board, run `sudo poweroff` on the board.

## Not covered yet

The challenge asks the copilot to *Teach*: to guide the student without revealing the answer ([the challenge](../BOARD_SETUP.md#the-challenge)). This part (hints, a web page, the LED matrix) does not exist yet. The team chooses the idea in [step 13 of the board setup](../BOARD_SETUP.md#step-13-brainstorm-your-idea). This guide will cover it when it exists. Until then, `predict.py`, `eval.py`, retrieval and the explorer are all that the copilot offers.

## See also

- [Board setup](../BOARD_SETUP.md): the organizers' guide.
- [UNO Q board reference](../UNO_Q_BOARD_REFERENCE.md): the board's hardware, limits, and measured speeds.
