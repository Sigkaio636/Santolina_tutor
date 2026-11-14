# How to deploy the copilot on the UNO Q

This how-to guide is for a team member who prepared an Arduino UNO Q 4 GB with the board setup. It shows how to deploy our copilot on that board. It puts the copilot code and the data on the board, which already runs the two model services. At the end, the smoke test passes.

The organizers of the Qualcomm challenge (Datathon FME 2026) wrote the [board setup](../BOARD_SETUP.md). This guide repeats some of its steps for our copilot, and links each step that it replaces.

The code calls the project the *copilot*. See the [glossary](https://github.com/Sigkaio636/Santolina_tutor/blob/main/GLOSSARY.md).

To use the copilot after you deploy it, see [How to use the copilot on the UNO Q](use-copilot-on-board.md).

## Before you start

- You finished steps 0 to 8 of the [board setup](../BOARD_SETUP.md). The board has llama.cpp, two verified models, and the model services `math-llm` and `math-embed`. [Step 8.1](../BOARD_SETUP.md#81-clone-this-repository-on-the-board) already cloned this repository into `~/Santolina_tutor`.
- You can open a shell on the board, with SSH or with `adb shell`. `adb shell` opens a shell on the board over the USB-C cable (see [step 0.4](../BOARD_SETUP.md#04-if-ssh-doesnt-work-connect-over-usb-with-adb-fallback)).
- You have the [M3Kang](https://huggingface.co/datasets/qualcomm/M3Kang) files `train.jsonl` and `val.jsonl` on your laptop. They come from [step 9](../BOARD_SETUP.md#step-9-prepare-m3kang-on-your-laptop) of the board setup.

## 1. Set the board's IP address

On your laptop, in the terminal that you use for this guide, set a variable with the board's IP address:

```bash
BOARD_IP=192.168.1.131
```

Replace `192.168.1.131` with your board's address. [Step 0.2](../BOARD_SETUP.md#02-find-the-boards-ip-address) of the board setup shows how to find it. The variable exists only in this terminal. Set it again in each new terminal.

Check:

```bash
ssh arduino@"$BOARD_IP" hostname
```

You should see the name of your board. If you use only `adb`, skip this step.

## 2. Check the board

On the board, from `~/Santolina_tutor`:

```bash
cd ~/Santolina_tutor
./board/00_check_board.sh
```

This script only reads. It changes nothing. The last line must say `The board looks healthy.` If it reports a problem, fix it first (see [If something fails](#if-something-fails)).

## 3. Check the repository on the board

This step replaces [step 8.1](../BOARD_SETUP.md#81-clone-this-repository-on-the-board) of the board setup. Step 8.1 already cloned the repository, so do not clone it again.

On the board:

```bash
cd ~/Santolina_tutor
git log -1 --oneline
```

You should see the latest commit of the repository. To get newer code, see [Update the board later](#update-the-board-later).

**If the board has no internet.** Copy a fresh clone from your laptop. A fresh clone holds only the committed files. It has no `data/`, `.venv`, or `models/` folder. On your laptop, from the repository folder:

```bash
git clone . ~/board-copy/Santolina_tutor
scp -r ~/board-copy/Santolina_tutor arduino@"$BOARD_IP":~/
```

Or, over USB:

```bash
git clone . ~/board-copy/Santolina_tutor
adb push ~/board-copy/Santolina_tutor /home/arduino/
```

Then check the board as in step 2. Step 4 copies the data that the board needs.

**If an older copy exists.** The board can hold the organizers' copy (`~/datathon-UPC-maths-qualcomm-arduino-unoq`). The model services do not depend on the repository folder: they use the llama.cpp build and the model files. You can keep both copies. Run the commands in the folder that holds the code you want to test.

The code needs no `pip` packages on the board (see [step 8.1](../BOARD_SETUP.md#81-clone-this-repository-on-the-board)).

## 4. Copy the data

This step replaces [step 10](../BOARD_SETUP.md#step-10-copy-the-data-to-the-board) of the board setup.

M3Kang is for research use only. **Do not put these files in Git**: `train.jsonl`, `val.jsonl`, the images, `index.db`, and `.ocr_cache.jsonl`. The `.gitignore` excludes `data/`. A Claude Code hook blocks Claude from staging them. The hook does not block your own `git add`. The full rule is in [CLAUDE.md](https://github.com/Sigkaio636/Santolina_tutor/blob/main/CLAUDE.md).

On your laptop, from the repository folder:

```bash
scp data/train.jsonl data/val.jsonl arduino@"$BOARD_IP":~/Santolina_tutor/data/
```

Or, over USB:

```bash
adb push data/train.jsonl data/val.jsonl /home/arduino/Santolina_tutor/data/
```

Check on the board, from `~/Santolina_tutor`:

```bash
wc -l data/train.jsonl data/val.jsonl
```

Each line is one problem. `prepare_m3kang.py` printed one count per split and language, such as `train eng` and `train cat`. The line count of `train.jsonl` must equal the sum of the `train` counts. The line count of `val.jsonl` must equal the sum of the `val` counts.

## 5. Build the retrieval index (optional)

This step replaces [step 12.1](../BOARD_SETUP.md#121-build-the-index) of the board setup.

Do this step only if you want retrieval: the `--rag` option of `predict.py` and `eval.py`. The explorer also needs the index to show similar problems. The index finds solved problems that look like a new one. It uses the embedding service on port 8082.

On the board, from `~/Santolina_tutor`:

```bash
python3 build_index.py --input data/train.jsonl --db data/index.db --only-with-options
```

- `--only-with-options` skips the problems whose five options optical character recognition (OCR) could not read.
- `--languages eng` keeps one language.

While it runs, the script shows how many problems it embedded, and its speed. When it ends, you should see `Wrote data/index.db (… MB) in … s`.

The result is one SQLite file, `data/index.db`. It is M3Kang data too. Do not commit it.

## 6. Check the result

On the board, from `~/Santolina_tutor`:

```bash
./board/05_smoke_test.sh
```

The script checks both model services, makes one embedding, and answers the five sample problems in `data/sample_problems.jsonl`. On our board it printed the lines below. The output below omits the five lines that `predict.py` prints, one per problem.

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

Your times can differ by a second or two. `predict.py` prints each problem as `[n/5] <id> -> <letter> in <seconds> s (<status>)`. The same values are in `results/smoke.csv`:

```bash
cat results/smoke.csv
```

Check these points:

- Each answer is one letter from A to E.
- Each `status` is `ok`.
- The worst time is well under 60 seconds.

A score of 0 out of 5 is normal. The test checks that the pipeline runs, not that the answers are right.

## Update the board later

On the board, from `~/Santolina_tutor`:

```bash
git pull
```

If the board has no internet, delete the old copy on your laptop with `rm -rf ~/board-copy/Santolina_tutor`. Then copy a fresh clone again, as in step 3.

[`config.env`](https://github.com/Sigkaio636/Santolina_tutor/blob/main/config.env) holds the settings that the Python code and the scripts in `board/` read. It pins the llama.cpp commit and each model: repository, revision, file, and SHA256 checksum. The checksum proves that the file is complete and has the right content. It also holds the ports and the time limit per problem (60 seconds).

| What changed | What to do |
| --- | --- |
| Python code (`copilot/`, `predict.py`, `eval.py`) | Nothing. Each command starts a new Python process, which uses the new code |
| `config.env` or `board/systemd/` | `./board/04_install_services.sh` |
| A model in `config.env` | `./board/03_download_models.sh`, then `./board/04_install_services.sh` |
| The training data | Copy it again (step 4), then build the index again (step 5) |

`04_install_services.sh` writes the two service files, reloads systemd, restarts the model services, and waits until both answer. You should see:

```text
  OK    LLM server ready on 127.0.0.1:8081
  OK    embedding server ready on 127.0.0.1:8082
```

The script stops with an error if you started a `llama-server` by hand on port 8081 or 8082. The error gives the PID and the command to stop that server, such as `Stop it with: kill 1234`. Run that command. Then run the script again.

## If something fails

This table replaces the [troubleshooting section](../BOARD_SETUP.md#troubleshooting) of the board setup for these symptoms.

| Symptom | Fix |
| --- | --- |
| `couldn't bind HTTP server socket` | Another `llama-server` uses the port. Run `pgrep -a llama-server`. The model services also appear there: `systemctl show -p MainPID --value math-llm math-embed` gives their PIDs. Stop only the server that you started by hand, with `kill` and its PID |
| A `llama-server` disappears. `journalctl -k` shows `Out of memory` | Keep `--parallel 1 --cache-ram 0` in the service files. Stop the servers that you started by hand: press Ctrl+C in their terminal, or `kill` their PID. Do not use `pkill llama-server`: it also stops both model services |
| A model service is not active | `systemctl status math-llm math-embed`, then `journalctl -u math-llm -n 50 --no-pager`. For the embedding service, use `-u math-embed` |
| The smoke test says a server is down | `sudo systemctl start math-llm math-embed` |
| `sha256sum` says `FAILED` | Run `./board/03_download_models.sh`. It downloads the file again and checks it. If the check fails, it deletes the partial download and stops. Then run it again |
| `ssh: connect to host … port 22: Connection refused` | The SSH host keys are empty. Connect with `adb shell`. Then run `sudo rm -f /etc/ssh/ssh_host_* && sudo ssh-keygen -A && sudo systemctl restart ssh` |
| `REMOTE HOST IDENTIFICATION HAS CHANGED` | On your laptop: `ssh-keygen -R "$BOARD_IP"` |

More fixes are in the [board setup](../BOARD_SETUP.md#troubleshooting). Board facts and limits are in the [UNO Q board reference](../UNO_Q_BOARD_REFERENCE.md).
