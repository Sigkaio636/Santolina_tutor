# How to use the copilot on the UNO Q

This guide shows how to answer problems, measure the result, and compare experiments with the copilot on the Arduino UNO Q. All commands run on the board, from `~/Santolina_tutor`, unless the text says "on your laptop".

The code calls the project the *copilot*. Some people say *tutor*. Both words mean the same thing here. See the [glossary](https://github.com/Sigkaio636/Santolina_tutor/blob/main/GLOSSARY.md).

## Before you start

- You deployed the copilot. If not, follow [How to deploy the copilot on the UNO Q](deploy-copilot-on-board.md).
- Both model services answer:

  ```bash
  curl http://127.0.0.1:8081/health; echo
  curl http://127.0.0.1:8082/health; echo
  ```

  You should see `{"status":"ok"}` twice. If not, run `sudo systemctl start math-llm math-embed`.
- `data/val.jsonl` is on the board. For retrieval, `data/index.db` must exist too.

## Answer a file of problems

`predict.py` is the program that the organizers run on the hidden test set:

```bash
python3 predict.py --input data/val.jsonl --output results/predictions.csv
```

The output is a CSV file with one row per problem:

| Column | Meaning |
| --- | --- |
| `id` | The problem ID from the input |
| `language` | The language from the input |
| `answer` | One letter, A to E |
| `seconds` | The time the problem took |
| `status` | `ok`, `timeout`, or `error: <reason>` |

The program prints one line per problem while it runs. If the model is too slow, or fails, the answer is `D` and the `status` tells you why.

**The contract.** Keep these rules in every change you make:

- One letter, A to E, for every problem.
- At most 60 seconds per problem. The code keeps 3 seconds free for Python and for writing the answer.
- No network. Only the services on `127.0.0.1`.
- The same answers every time: temperature 0 and the `SEED` from [`config.env`](https://github.com/Sigkaio636/Santolina_tutor/blob/main/config.env).

The limits are in `TIME_LIMIT_SECONDS` and `FALLBACK_ANSWER` in `config.env`.

## Measure the result

`eval.py` answers problems from the validation set and compares the answers with the labels:

```bash
python3 eval.py --limit 50 --name baseline
```

| Option | What it does |
| --- | --- |
| `--limit N` | Use N problems. The default is 50. `0` means every problem |
| `--languages eng,cat` | Use only these languages |
| `--rag K` | Add K similar solved problems to each prompt |
| `--name <label>` | A label for this run in the results file |
| `--input <file>` | Use another problem file. The default is `data/val.jsonl` |

The report shows:

- **Accuracy**, next to two numbers to beat: always answering `D`, and random guessing (20%).
- **Latency**: mean, median, worst, and how many problems went over the limit.
- Accuracy by language, by level, and with or without options.
- **Letter counts**, predicted against true. A model that picks one letter far too often shows here.

Each run writes two files in `results/`:

- `results/eval-<time>-<name>.csv`: one row per problem.
- `results/ablations.csv`: one line per run, with the Git commit. Use this file for the results table in the README.

A run on all 281 validation problems takes about 45 minutes. Use `--limit` for fast checks. Say how many problems a number comes from. A result on 50 problems or fewer is weak evidence.

## Use retrieval

Retrieval shows the model solved problems that look like the new one. Build the index first (step 4 of the [deploy guide](deploy-copilot-on-board.md)). Then:

```bash
python3 eval.py --limit 50 --rag 1 --name rag1
python3 predict.py --input data/val.jsonl --output results/predictions.csv --rag 1
```

`--rag 1` adds the most similar training problem, with its answer. `--rag 2` adds two. `eval.py` never retrieves the problem it answers, so the score stays honest.

Each example makes the prompt longer. On our board the model reads about 10 tokens per second, so every example adds seconds. Compare the latency columns, not only the accuracy.

## Look at the problems in a browser

The explorer shows each validation problem, with its image and the options that OCR read. You can answer it yourself, ask the model, and see the three most similar training problems.

It needs the problem images. On your laptop, make them with `prepare_m3kang.py --save-images`, then copy `data/images` to the board. The images are M3Kang data: do not commit them.

On the board:

```bash
python3 explorer/server.py
```

The explorer listens only on the board, on port 8000. To open it on your laptop, forward the port. On your laptop, in a second terminal:

```bash
ssh -L 8000:127.0.0.1:8000 arduino@<board-ip>
```

Or, over USB:

```bash
adb forward tcp:8000 tcp:8000
```

Then open <http://127.0.0.1:8000>. Press Ctrl+C on the board to stop it.

Port 8001 belongs to the documentation site on your laptop. Do not use it for the explorer.

## Free memory for an experiment

The board has 3.6 GiB of RAM. The two services use about 1 GB. To start a server by hand with other options, stop the service first, because only one program can use a port:

```bash
sudo systemctl stop math-llm math-embed
```

Start the services again when you finish:

```bash
sudo systemctl start math-llm math-embed
```

Do not leave a hand-started server running. Do not stop servers that other people started.

## Prepare the demo

The jury sees the copilot work on the board, with the Wi-Fi off.

- Both services start at boot. Check with `systemctl is-enabled math-llm math-embed`: both say `enabled`.
- Nothing in your code may download data at run time.
- If a web page runs on your laptop, connect over USB and use `adb forward`, as above.
- Choose the demo problems in advance. Run them on the board on the day of the demo, and time each one.
- Shut the board down from the terminal before you unplug it: `sudo poweroff`.

## Not covered yet

The Teach interface (hints, a web page, the LED matrix) is not built. The team chooses the idea in step 13 of the [board setup](../BOARD_SETUP.md). This guide will cover it when it exists. Until then, `predict.py`, `eval.py`, retrieval and the explorer are all that the copilot offers.

## See also

- [Board setup](../BOARD_SETUP.md): the organizers' guide.
- [UNO Q board reference](../UNO_Q_BOARD_REFERENCE.md): the board's hardware, limits, and measured speeds.
