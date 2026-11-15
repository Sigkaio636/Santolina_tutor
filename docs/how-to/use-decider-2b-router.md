# How to install and use decider-2b as the intent router

This guide sets up [Mapika/decider-2b](https://huggingface.co/Mapika/decider-2b-GGUF) as the tutor's intent router and shows how to ask it for one label. The router reads the student's message and gives it one of five labels: `stuck`, `concept`, `attempt`, `solution` or `not_productive`. They are the English names of the labels that [TUTOR_RESPONSE_TYPES.md](../TUTOR_RESPONSE_TYPES.md) proposes in Spanish (PRODUCTIVA_ATASCO, PRODUCTIVA_CONCEPTO, INTENTO, PIDE_SOLUCIÓN, NO_PRODUCTIVA). Rules then pick the tutor's response type.

[Round 3 of the router bake-off](../experiments/2026-11-router-bakeoff-3.md) chose decider-2b Q4_K_M, with the `plain` prompt format and the canonical option order, to replace decider-0.8b as the router to try on the board. The router is not part of the copilot yet: nothing in `copilot/`, `predict.py` or the board services calls it. You run it by hand, on its own port.

## Before you start

- A clone of this repository, and Python 3.10 or later. Run every command from the repository root.
- `llama-server` built from llama.cpp commit `2cbe0ec`, the `LLAMA_CPP_REF` of `config.env`. The bake-off used this build. If you don't have it on your laptop:

    ```bash
    git clone https://github.com/ggml-org/llama.cpp ~/llama.cpp-laptop
    cd ~/llama.cpp-laptop
    git checkout 2cbe0ec429b849a88664e0f62388fc92a5abd699
    cmake -B build -DCMAKE_BUILD_TYPE=Release
    cmake --build build -j --target llama-server
    ```

    If `~/llama.cpp-laptop` already exists from [INSTALL_DECIDER.md](../INSTALL_DECIDER.md), skip the `git clone` and run the other commands in it.

    On the board, `llama-server` is already built after [step 3 of the board guide](../BOARD_SETUP.md#step-3-build-llamacpp).

- 1.3 GB of free disk space.

## 1. Get the model file

The router uses one file, `decider-2b-v12-Q4_K_M.gguf` (1.27 GB). Mapika publishes it as a GGUF, so there is nothing to convert.

**First, ask a teammate to share the file with you** (USB stick, shared drive or `scp`). Several of us already have it, and a copy is faster than the download. Put it in `models/` in the repository.

Only if nobody can share it, download it from the pinned revision:

```bash
mkdir -p models
wget --continue -P models https://huggingface.co/Mapika/decider-2b-GGUF/resolve/0df001b8fe4e5298c5dd45d875d3795fcdaea0ab/decider-2b-v12-Q4_K_M.gguf
```

If the download breaks, run the same `wget` again.

Either way, check the file:

```bash
sha256sum --check <<'EOF'
e6d3a7534a3abc3a723f8263dc694b86f533214a5bf761474113c66d44018340  models/decider-2b-v12-Q4_K_M.gguf
EOF
```

You should see `models/decider-2b-v12-Q4_K_M.gguf: OK`. If you see `FAILED`, the copy is damaged or is another version: get it again.

You don't need the Q8_0 file (2.0 GB). In round 3 it was right on as many messages as Q4_K_M in the `plain` format, and it does not fit on the board.

## 2. Start the server

In a terminal of its own:

```bash
~/llama.cpp-laptop/build/bin/llama-server \
  -m models/decider-2b-v12-Q4_K_M.gguf \
  --host 127.0.0.1 --port 8090 \
  --threads 4 --ctx-size 4096 --parallel 1 \
  --alias decider-2b
```

Port 8090 is the default of `laptop/router_bakeoff.py`. Leave the server running. It is ready when it prints `listening on http://127.0.0.1:8090`. Check it from another terminal:

```bash
curl -s http://127.0.0.1:8090/health
```

The answer is `{"status":"ok"}`.

## 3. Ask it for one label

The router does not generate text. It reads the probability of the next token after `Answer: (` for the letters A to E, and the letter with the highest probability gives the label. Use the prompt and the readout of `laptop/router_bakeoff.py`, so that your results are comparable with the experiments. Save this as a script **outside the repository** (for example `~/label_one.py`), so a problem you paste into it never ends up in a commit. Run it from the repository root with `python3 ~/label_one.py`:

```python
import sys

sys.path.insert(0, "laptop")
from router_bakeoff import LABELS, letter_probs, plain_prompt

URL = "http://127.0.0.1:8090"
problem = "What is 7 times 8? (A) 54 (B) 56 (C) 58 (D) 64 (E) 72"
tutor_move = "none (first message)"
message = "no sé por dónde empezar"

prompt = plain_prompt(problem, tutor_move, message, LABELS)
probs, ms = letter_probs(URL, prompt)
mass = sum(probs.values())
if not mass:
    sys.exit("no letter A-E in the top 50 tokens")
by_label = {label: probs.get(letter, 0.0) / mass for letter, label in zip("ABCDE", LABELS)}
print(max(by_label, key=by_label.get), f"{ms:.0f} ms")
print({label: round(p, 3) for label, p in by_label.items()})
```

It prints the label and the time of the call, then the probability of each label:

```text
stuck 2215 ms
{'stuck': 0.999, 'concept': 0.0, 'attempt': 0.0, 'solution': 0.0, 'not_productive': 0.0}
```

Your time will differ. Things to keep:

- **`LABELS` is the canonical order**, the order of the round-3 decision. Pass it as it is.
- **`plain_prompt`** writes the five labels with their descriptions (`DESCRIPTIONS` in the same script). Change a description and you leave the conditions of the experiment.
- **`tutor_move`** is a short description of the tutor's last message. The bake-off used the values of `moves` in `laptop/router_messages.json`, such as `none (first message)` or `asked the student a question`.
- Write problems and messages yourself. Never put M3Kang problem text in a file you commit.

## 4. Check that you get the experiment's numbers

To repeat round 3 on the 250 invented messages, label both message files and compare with decider-0.8b. Each `run` makes four calls per message, about 20 to 30 minutes per file on a laptop:

```bash
python3 laptop/router_bakeoff.py run --name decider2b-q4 --out results/router-decider2b-q4.csv
```

```bash
python3 laptop/router_bakeoff.py run --name decider2b-q4 --messages laptop/router_messages_r2.json --out results/router2-decider2b-q4.csv
```

The comparison also needs the decider-0.8b files `results/router-decider.csv` and `results/router2-decider.csv`. `results/` is not in Git, so ask the teammate who ran the bake-off for them, or make them yourself: get `decider-0.8b-Q8_0.gguf` with steps 1 and 2 of [INSTALL_DECIDER.md](../INSTALL_DECIDER.md) (not the board steps), serve it on port 8090 as in step 2 of this guide, and run the two commands above with `--name decider` and the output files `results/router-decider.csv` and `results/router2-decider.csv`. Then:

```bash
python3 laptop/router_bakeoff.py summary --ref decider/plain results/router{,2}-decider.csv results/router{,2}-decider2b-q4.csv
```

In the block `decider2b-q4 / plain`, the line `canonical` must show `87.6% [82.9-91.1]  219/250`, as in the round-3 report.

## 5. Try it on the board

This step is not measured yet: RAM and time per call on the board are the open test of round 3. It changes nothing in the copilot. The router runs by hand on port 8084, next to the two services. The board must be set up to [step 8.1 of the board guide](../BOARD_SETUP.md#81-clone-this-repository-on-the-board): the services run, and the repository is in `~/Santolina_tutor`.

1. Copy the file to the board. Again, a teammate's copy saves you the download. With `ssh`:

    ```bash
    scp models/decider-2b-v12-Q4_K_M.gguf arduino@192.168.1.131:~/models/
    ```

    With `adb`:

    ```bash
    adb push models/decider-2b-v12-Q4_K_M.gguf /home/arduino/models/
    ```

    Use your board's address or user if they differ. Check it on the board, from your home directory:

    ```bash
    cd ~
    sha256sum --check <<'EOF'
    e6d3a7534a3abc3a723f8263dc694b86f533214a5bf761474113c66d44018340  models/decider-2b-v12-Q4_K_M.gguf
    EOF
    ```

2. On the board, write down the free RAM, then start the router with the memory options of the services:

    ```bash
    free -m
    ~/llama.cpp/build/bin/llama-server \
      -m ~/models/decider-2b-v12-Q4_K_M.gguf \
      --host 127.0.0.1 --port 8084 \
      --threads 4 --ctx-size 4096 \
      --parallel 1 --cache-ram 0 --ctx-checkpoints 2 \
      --alias decider-2b
    ```

    `--cache-ram 0 --ctx-checkpoints 2` keep the prompt cache from filling the 3.6 GB of RAM ([step 5 of the board guide](../BOARD_SETUP.md#step-5-hello-world-with-the-language-model)).

3. In a second terminal, run `free -m` again, and copy the script of step 3 to the board's home directory, set `URL = "http://127.0.0.1:8084"`, and run it from `~/Santolina_tutor` with `python3 ~/label_one.py`.

Don't put the router file in `LLM_FILE` of `config.env`: that would replace the model that answers the problems, not add a router. Stop the router with Ctrl+C when you are done.

## Limits

- **The two rules are still needed.** No model tested separates a message with several letters (`A? B? C?`) from an attempt: decider-2b labels it `attempt`. The keyword rule for "asks for the solution" and the pattern rule for several letters must run before the model ([conclusion](../experiments/2026-11-router-0.8b-conclusion.md#decision)). Neither rule is written yet.
- **English-only model card.** decider-2b is still right on 65 of the 80 Catalan messages, and on 11 of 16 Catalan "solution" messages.
- **Slower than decider-0.8b.** On the laptop, each call took 1.5 to 2.2 times as long. On the board it is not measured.
- **Invented data.** One author (Claude) wrote and labelled the 250 messages. No real student message was used.

## Experiments behind this guide

| Report | What it showed |
|---|---|
| [Router bake-off, round 1](../experiments/2026-11-router-bakeoff.md) | Three 0.8B classifiers on 100 messages: decider-0.8b in `plain` is far ahead (84 %) |
| [Router bake-off, round 2](../experiments/2026-11-router-bakeoff-2.md) | 150 new messages: decider-0.8b holds (78.7 %), but is weak on "solution" in Catalan and Spanish |
| [Router conclusion (0.8B)](../experiments/2026-11-router-0.8b-conclusion.md) | The team adopts decider-0.8b with two rules in front |
| [Router bake-off, round 3](../experiments/2026-11-router-bakeoff-3.md) | decider-2b Q4_K_M passes its rule: 87.6 % against 80.8 %, McNemar p = 0.009; the gain is on "solution" messages |
| [decider-0.8b as the solver](../experiments/2026-11-decider-0.8b.md) | The other use of the family: answering the problems, not routing |
| [Tutor response types](../TUTOR_RESPONSE_TYPES.md) | The five labels and the rules that turn them into the tutor's response |

For each option of the bake-off script, run `python3 laptop/router_bakeoff.py run --help`.
