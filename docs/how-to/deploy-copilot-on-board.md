# How to deploy the copilot on the UNO Q

This guide puts the copilot code and the data on an Arduino UNO Q 4 GB that already runs the two model services. At the end, the smoke test passes.

The code calls the project the *copilot*. Some people say *tutor*. Both words mean the same thing here. See the [glossary](https://github.com/Sigkaio636/Santolina_tutor/blob/main/GLOSSARY.md).

To use the copilot after you deploy it, see [How to use the copilot on the UNO Q](use-copilot-on-board.md).

## Before you start

- You finished steps 0 to 8 of the [board setup](../BOARD_SETUP.md). The board has llama.cpp, two verified models, and the services `math-llm` and `math-embed`.
- You can open a shell on the board, with SSH (`ssh arduino@<board-ip>`) or with `adb shell`.
- You have the M3Kang files `train.jsonl` and `val.jsonl` on your laptop. They come from step 9 of the board setup.

## 1. Put the repository on the board

On the board:

```bash
cd ~
git clone https://github.com/Sigkaio636/Santolina_tutor.git
cd Santolina_tutor
```

Every later command runs from `~/Santolina_tutor`.

**If the board has no internet.** Copy the folder from your laptop. On your laptop:

```bash
scp -r Santolina_tutor arduino@<board-ip>:~/
```

Or, over USB:

```bash
adb push Santolina_tutor /home/arduino/
```

Do not copy your laptop's `data/` folder this way. Step 3 copies only the files that the board needs.

**If an older copy exists.** The board can hold the organizers' copy (`~/datathon-UPC-maths-qualcomm-arduino-unoq`). The services do not depend on the repository folder: they use the llama.cpp build and the model files. You can keep both copies. Run the commands in the folder that holds the code you want to test.

The code uses only the Python standard library. The board needs no `pip` packages.

Check the board before you change anything. This script only reads:

```bash
./board/00_check_board.sh
```

The last line must say `The board looks healthy.`

## 2. Keep the settings in sync

[`config.env`](https://github.com/Sigkaio636/Santolina_tutor/blob/main/config.env) holds the settings that the Python code and the scripts in `board/` read. It pins the llama.cpp commit, each model (repository, revision, file, SHA256), the ports, and the 60-second limit.

If you change `config.env`, or a file in `board/systemd/`, install the services again:

```bash
./board/04_install_services.sh
```

The script writes the two service files, reloads systemd, restarts the services, and waits until both answer.

It stops with an error if you started a `llama-server` by hand on port 8081 or 8082. Stop that server first:

```bash
pgrep -a llama-server
kill <pid>
```

A change in the Python code needs no restart. Each command starts a new Python process.

## 3. Copy the data

M3Kang is for research use only. **Do not put these files in Git**: `train.jsonl`, `val.jsonl`, the images, `index.db`, and `.ocr_cache.jsonl`. The `.gitignore` excludes `data/`, and a hook blocks `git add` for them.

On your laptop, from the repository folder:

```bash
scp data/train.jsonl data/val.jsonl arduino@<board-ip>:~/Santolina_tutor/data/
```

Or, over USB:

```bash
adb push data/train.jsonl data/val.jsonl /home/arduino/Santolina_tutor/data/
```

Check on the board:

```bash
wc -l data/train.jsonl data/val.jsonl
```

Each line is one problem. The line counts must match the counts that `prepare_m3kang.py` printed on your laptop.

## 4. Build the retrieval index (optional)

Do this step only if you want to use `--rag`. The index finds solved problems that look like a new one. It uses the embedding service on port 8082.

```bash
python3 build_index.py --input data/train.jsonl --db data/index.db --only-with-options
```

- `--only-with-options` skips the problems whose five options OCR could not read.
- `--languages eng` keeps one language.

The result is one SQLite file, `data/index.db`. It is M3Kang data too. Do not commit it.

## 5. Check the result

```bash
./board/05_smoke_test.sh
```

The script checks both servers, makes one embedding, and answers the five sample problems in `data/sample_problems.jsonl`. On our board it printed:

```text
==> Servers
  OK    LLM server answers on port 8081
  OK    embedding server answers on port 8082

==> One embedding
  384 dimensions in 0.18 s
  similar pair: 0.86   unrelated pair: 0.52
  OK    embeddings look right

==> Baseline on the 5 sample problems
  0/5 correct, worst latency 7.0 s
  OK    the minimum pipeline works. Next: answer problems with the copilot (docs/how-to/use-copilot-on-board.md)
```

Your times can differ by a second or two. Check these points:

- Each answer is one letter from A to E.
- Each `status` is `ok`.
- The worst time is well under 60 seconds.

A score of 0 out of 5 is normal. The test checks that the pipeline runs, not that the answers are right.

## 6. Update the board later

On the board, from `~/Santolina_tutor`:

```bash
git pull
```

| What changed | What to do |
| --- | --- |
| Python code (`copilot/`, `predict.py`, `eval.py`) | Nothing. The next command uses the new code |
| `config.env` or `board/systemd/` | `./board/04_install_services.sh` |
| A model in `config.env` | `./board/03_download_models.sh`, then `./board/04_install_services.sh` |
| The training data | Copy it again (step 3), then build the index again (step 4) |

## If something fails

| Symptom | Fix |
| --- | --- |
| `couldn't bind HTTP server socket` | Another `llama-server` uses the port. Run `pgrep -a llama-server`, then stop the one that you started by hand |
| A `llama-server` disappears. `journalctl -k` shows `Out of memory` | Keep `--parallel 1 --cache-ram 0` in the service files. Stop servers that you started by hand: `pkill llama-server` |
| A service is not active | `systemctl status math-llm`, then `journalctl -u math-llm -n 50 --no-pager` |
| The smoke test says a server is down | `sudo systemctl start math-llm math-embed` |
| `sha256sum` says `FAILED` | Run `./board/03_download_models.sh` again. It deletes the bad file and downloads it again |
| `ssh: connect to host … port 22: Connection refused` | The SSH host keys are empty. Connect with `adb shell`, then run `sudo ssh-keygen -A && sudo systemctl restart ssh` |
| `REMOTE HOST IDENTIFICATION HAS CHANGED` | On your laptop: `ssh-keygen -R <board-ip>` |

More fixes are in the [board setup](../BOARD_SETUP.md#troubleshooting). Board facts and limits are in the [UNO Q board reference](../UNO_Q_BOARD_REFERENCE.md).
