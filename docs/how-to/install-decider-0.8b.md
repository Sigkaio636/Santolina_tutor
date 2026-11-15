# How to install decider-0.8b on the board

[decider-0.8b](https://huggingface.co/Mapika/decider-0.8b) is an open model from the Hugging Face account Mapika. It picks the letter of a multiple-choice answer in one pass, without writing out its reasoning. It is fine-tuned from Qwen3.5-0.8B-Base. This guide puts it on the Arduino UNO Q in place of the copilot's default language model, and measures it there. The [decider-0.8b experiment report](../experiments/2026-11-decider-0.8b.md) measured it on a laptop and did not adopt it, so `config.env` does not use it.

Mapika publishes decider-0.8b only in the Hugging Face file format, not as a GGUF file, the model format that llama.cpp reads. So you convert it on your laptop, copy the GGUF to the board, and point `config.env` at it.

## Before you start

- You finished [step 10 of the board guide](../BOARD_SETUP.md#step-10-copy-the-data-to-the-board). So the services run, the repository is in `~/Santolina_tutor`, and `data/val.jsonl` is on the board.
- On your laptop: Git, CMake, a C++ compiler, and Python 3.10 or later. On Debian or Ubuntu, also the `python3-venv` package.
- On your laptop, at least 6 GB of free disk space. The llama.cpp clone and build take about 0.8 GB, and the downloaded weights 1.5 GB. The bf16 GGUF takes about 1.5 GB too, and the Q8_0 file takes 812 MB. PyTorch and the other Python packages add to that.
- On the board, `df -h ~/models` shows at least `2.1G` available. The file takes 812 MB, and `03_download_models.sh` (step 5) stops if less than 1.2 GiB is free after the copy.
- You can reach the board with `ssh` or `adb` ([step 0](../BOARD_SETUP.md#step-0-connect-to-the-board)).

## 1. Build the conversion tools on your laptop

Use this exact llama.cpp commit, because the checksum in step 2 depends on it. It is the `LLAMA_CPP_REF` of `config.env` as of 2026-11-14.

1. Get the source at that commit. If `~/llama.cpp-laptop` already exists, skip the `git clone`.

    ```bash
    git clone https://github.com/ggml-org/llama.cpp ~/llama.cpp-laptop
    cd ~/llama.cpp-laptop
    git checkout 2cbe0ec429b849a88664e0f62388fc92a5abd699
    ```

2. Build the quantization tool:

    ```bash
    cmake -B build
    cmake --build build -j --target llama-quantize
    ```

3. Install the Python conversion tools in their own environment:

    ```bash
    python3 -m venv .venv-convert
    .venv-convert/bin/pip install -r requirements/requirements-convert_hf_to_gguf.txt
    ```

    This installs PyTorch for the CPU, and `hf`, the Hugging Face command-line tool.

**Check:** `ls build/bin/llama-quantize .venv-convert/bin/hf` shows both files.

## 2. Download and convert the model

In `~/llama.cpp-laptop`:

1. Download the pinned revision of the weights.
2. Convert them to a GGUF file in bf16 (16-bit numbers).
3. Quantize it to Q8_0: each weight takes about 8 bits, so the file is smaller.

```bash
cd ~/llama.cpp-laptop
.venv-convert/bin/hf download Mapika/decider-0.8b \
  --revision a0a01d6f8135298f400a8c856b355793012ae971 \
  --local-dir ~/decider-0.8b-hf
.venv-convert/bin/python convert_hf_to_gguf.py ~/decider-0.8b-hf \
  --outtype bf16 --outfile decider-0.8b-bf16.gguf
build/bin/llama-quantize decider-0.8b-bf16.gguf decider-0.8b-Q8_0.gguf Q8_0
```

**Check** the file:

```bash
sha256sum --check <<'EOF'
f0707b86fd1c5bbb4fd8ea39f21046ef6f1a4cebdea4251fe568aa94fe84b007  decider-0.8b-Q8_0.gguf
EOF
```

You should see `decider-0.8b-Q8_0.gguf: OK`. The [reproducibility appendix](../experiments/2026-11-decider-0.8b.md#appendix-reproducibility) of the report gives the same SHA256.

If you see `FAILED`, check the llama.cpp commit. `git -C ~/llama.cpp-laptop rev-parse HEAD` must print `2cbe0ec429b849a88664e0f62388fc92a5abd699`. Then check the `--revision` of the download. If both are right, delete `~/decider-0.8b-hf` and do step 2 again.

You need only the Q8_0 file. To free the disk space, delete the other two:

```bash
rm -r ~/decider-0.8b-hf ~/llama.cpp-laptop/decider-0.8b-bf16.gguf
```

## 3. Copy the GGUF to the board

On your laptop, in `~/llama.cpp-laptop`. The commands use the user `arduino` and the address `192.168.1.131`. Use your board's user and address ([step 0.2](../BOARD_SETUP.md#02-find-the-boards-ip-address)) if they differ.

With `ssh`:

```bash
scp decider-0.8b-Q8_0.gguf arduino@192.168.1.131:~/models/
```

With `adb`:

```bash
adb push decider-0.8b-Q8_0.gguf /home/arduino/models/
```

Step 5 checks the copy.

## 4. Point the copilot at the model

On the board, open `~/Santolina_tutor/config.env` in an editor, for example `nano ~/Santolina_tutor/config.env`. Change these five lines:

```text
LLM_FILE=decider-0.8b-Q8_0.gguf
LLM_SHA256=f0707b86fd1c5bbb4fd8ea39f21046ef6f1a4cebdea4251fe568aa94fe84b007
LLM_ALIAS=decider-0.8b
LLM_PROMPT=decider
SOLVER=letter
```

- decider-0.8b expects its own plain-text layout, not chat messages. `LLM_PROMPT=decider` makes the copilot send that layout to the server's `/completion` endpoint. The default, `chat`, sends chat messages to `/v1/chat/completions`.
- `SOLVER=letter` makes the copilot ask the language model for the letter. With the default `SOLVER=prior`, the copilot uses a fixed rule for a problem without an image. It does not call the language model, so it does not use decider-0.8b.
- Leave `LLM_REPO` and `LLM_REVISION` as they are. `03_download_models.sh` does not download a file that is already in `~/models` with the right checksum.

Until you go back (end of this guide), `predict.py` also uses decider-0.8b. Before a `git pull` on the board, go back first. `config.env` is a file in Git, so your changes can block the pull.

**Check:**

```bash
grep -E '^(LLM_FILE|LLM_SHA256|LLM_ALIAS|LLM_PROMPT|SOLVER)=' ~/Santolina_tutor/config.env
```

It prints the five lines above.

## 5. Check the file and restart the services

On the board:

```bash
cd ~/Santolina_tutor
./board/03_download_models.sh
./board/04_install_services.sh
```

- `03_download_models.sh` must print `already downloaded and verified` for `decider-0.8b-Q8_0.gguf`. If the script stops after the line with the file name, the file is not in `~/models` or its checksum is wrong. The script then tried to download the file, and the download failed. Copy the file again (step 3).
- `04_install_services.sh` asks for your `sudo` password. It writes `math-llm.service` with the new model, in place of the service file of board step 7. Then it restarts `math-llm.service` and `math-embed.service`. It must print `LLM server ready on 127.0.0.1:8081`.

## 6. Check the server and measure the model

On the board, ask the server for one letter, with the prompt layout and the grammar that the copilot uses:

```bash
curl -s http://127.0.0.1:8081/completion \
  -H "Content-Type: application/json" \
  -d '{
        "prompt": "Context:\nWhat is 7 times 8?\n\nQuestion: Which option is the correct answer?\nOptions:\n(A) 54\n(B) 56\n(C) 58\n(D) 64\n(E) 72\nAnswer: (",
        "grammar": "root ::= [A-E]",
        "n_predict": 1,
        "temperature": 0
      }' | jq -r '.content'
```

It prints one letter, A to E. Any letter shows that the server answers. The right answer is B, but a small model can give a wrong letter.

Check which model the server runs:

```bash
curl -s http://127.0.0.1:8081/v1/models | jq -r '.data[0].id'
```

It must print `decider-0.8b`, the `LLM_ALIAS` of step 4.

Then measure the model on 50 problems of the validation set, with its own name in `results/ablations.csv`:

```bash
cd ~/Santolina_tutor
python3 eval.py --limit 50 --name decider-0.8b
```

[Step 11.2 of the board guide](../BOARD_SETUP.md#112-run-the-evaluation) explains what `eval.py` prints. The `Status:` line must show only `'ok'`. A `timeout` or `error: ...` status means that the copilot used `FALLBACK_ANSWER`, the fixed letter in `config.env`, for that problem.

`results/ablations.csv` does not record `SOLVER`. Compare this row only with a run that also used `SOLVER=letter`. To measure the default model the same way, go back to it, then run `SOLVER=letter python3 eval.py --limit 50 --name default-letter`.

## Go back to the default model

On the board:

1. Put back the repository values of the five lines of step 4. This makes `SOLVER` equal to `prior` again. Use one of these two methods:
    - If you did not change other lines of `config.env`: `git -C ~/Santolina_tutor restore config.env`.
    - Otherwise: `git -C ~/Santolina_tutor diff config.env` shows the repository values on the lines that start with `-`. Copy them into `config.env`.
2. **Check:** `git -C ~/Santolina_tutor diff config.env` prints nothing for these five lines.
3. Run `./board/04_install_services.sh` again, from `~/Santolina_tutor`. It must print `LLM server ready on 127.0.0.1:8081`.
4. **Check:** `curl -s http://127.0.0.1:8081/v1/models | jq -r '.data[0].id'` prints the value after `LLM_ALIAS=` in `~/Santolina_tutor/config.env`.
5. Delete the file: `rm ~/models/decider-0.8b-Q8_0.gguf`.

This guide does not cover decider-2b, a different model. decider-2b can be the intent router of the student app: it labels the student's message. See [How to install and use decider-2b as the intent router](use-decider-2b-router.md).
