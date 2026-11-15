# How to install decider-0.8b on the board

This guide replaces the copilot's language model with [Mapika/decider-0.8b](https://huggingface.co/Mapika/decider-0.8b) on the Arduino UNO Q. Use it to repeat or extend the [decider-0.8b experiment](experiments/2026-11-decider-0.8b.md). That experiment did not adopt the model, so the default in `config.env` stays Qwen3.5-0.8B.

To use decider-2b as the tutor's intent router instead, see [How to install and use decider-2b as the intent router](how-to/use-decider-2b-router.md).

Mapika publishes decider-0.8b only as Hugging Face weights, not as a GGUF file, the model format that llama.cpp reads. So you convert it on your laptop, copy the GGUF to the board, and point `config.env` at it.

## Before you start

- The board is set up up to [step 7 of the board guide](BOARD_SETUP.md#step-7-run-both-models-as-services): llama.cpp is built, and the services run.
- On your laptop: Git, CMake, a C++ compiler, Python 3.10 or later, and about 4 GB of free disk space.
- You can reach the board with `ssh` or `adb` ([step 0](BOARD_SETUP.md#step-0-connect-to-the-board)).

## 1. Build the conversion tools on your laptop

Use the same llama.cpp commit as the board (`LLAMA_CPP_REF` in `config.env`):

```bash
git clone https://github.com/ggml-org/llama.cpp ~/llama.cpp-laptop
cd ~/llama.cpp-laptop
git checkout 2cbe0ec429b849a88664e0f62388fc92a5abd699
cmake -B build
cmake --build build -j --target llama-quantize
python3 -m venv .venv-convert
.venv-convert/bin/pip install -r requirements/requirements-convert_hf_to_gguf.txt
```

The last command installs PyTorch for the CPU, about 1 GB.

## 2. Download and convert the model

Download the pinned revision of the weights, convert them to GGUF in bf16, then quantize to Q8_0, the same quantization as the default model:

```bash
cd ~/llama.cpp-laptop
.venv-convert/bin/hf download Mapika/decider-0.8b \
  --revision a0a01d6f8135298f400a8c856b355793012ae971 \
  --local-dir ~/decider-0.8b-hf
.venv-convert/bin/python convert_hf_to_gguf.py ~/decider-0.8b-hf \
  --outtype bf16 --outfile decider-0.8b-bf16.gguf
build/bin/llama-quantize decider-0.8b-bf16.gguf decider-0.8b-Q8_0.gguf Q8_0
sha256sum decider-0.8b-Q8_0.gguf
```

The checksum must be:

```text
f0707b86fd1c5bbb4fd8ea39f21046ef6f1a4cebdea4251fe568aa94fe84b007  decider-0.8b-Q8_0.gguf
```

We checked on 2026-11-14 that these commands give this checksum. If yours differs, check the llama.cpp commit and the revision of the weights. The file is 812 MB. You can delete `decider-0.8b-bf16.gguf`.

## 3. Copy the GGUF to the board

With `ssh`:

```bash
scp decider-0.8b-Q8_0.gguf arduino@192.168.1.131:~/models/
```

With `adb`:

```bash
adb push decider-0.8b-Q8_0.gguf /home/arduino/models/
```

Use your board's address or user if they differ.

## 4. Point the copilot at the model

On the board, in `~/Santolina_tutor/config.env`, change these four lines:

```bash
LLM_FILE=decider-0.8b-Q8_0.gguf
LLM_SHA256=f0707b86fd1c5bbb4fd8ea39f21046ef6f1a4cebdea4251fe568aa94fe84b007
LLM_ALIAS=decider-0.8b
LLM_PROMPT=decider
```

`LLM_PROMPT=decider` makes the copilot send decider-0.8b's own plain-text prompt to `/completion`, instead of the chat prompt. Leave `LLM_REPO` and `LLM_REVISION` as they are. `03_download_models.sh` skips the download when the file is already in `~/models` with the right checksum.

## 5. Check the file and restart the service

On the board:

```bash
cd ~/Santolina_tutor
./board/03_download_models.sh
./board/04_install_services.sh
```

`03_download_models.sh` must print `already downloaded and verified` for `decider-0.8b-Q8_0.gguf`. `04_install_services.sh` writes the service with the new model and restarts it.

## 6. Test it

Ask the server for one letter, as the copilot does:

```bash
curl -s http://127.0.0.1:8081/completion \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Context:\nWhat is 7 times 8?\n\nQuestion: Which option is the correct answer?\nOptions:\n(A) 54\n(B) 56\n(C) 58\n(D) 64\n(E) 72\nAnswer: (", "grammar": "root ::= [A-E]", "n_predict": 1, "temperature": 0}'
```

The `content` field of the answer holds one letter. Then measure it on the validation set as in [step 11 of the board guide](BOARD_SETUP.md#step-11-measure-the-baseline).

## Go back to the default model

Set the four lines of step 4 back to the values in the repository (`git diff config.env` shows them), and run `./board/04_install_services.sh` again.
