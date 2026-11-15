# How to try Qwen2.5-Math with Catalan translation on the board

This guide runs the program solver with Qwen2.5-Math-1.5B-Instruct on the Arduino UNO Q, with Catalan problems translated to English first by Softcatalà's translation model. It's the best setup on the laptop so far. Follow [How to try the program solver on the board](try-program-solver.md) first if you haven't: this guide changes the model and adds the translation, and the rest works the same way.

## What changes

- The model is [Qwen2.5-Math-1.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-Math-1.5B-Instruct) (Apache-2.0), trained to solve problems with Python. It's smaller than Noema-2B and a plain transformer, so the server caches the fixed prompt with no checkpoint settings.
- With `TRANSLATE=nmt`, `copilot/nmt.py` translates a Catalan statement, and any option with words, before the model writes its program. It uses [softcatala/translate-cat-eng](https://huggingface.co/softcatala/translate-cat-eng) (MIT, 71 MB), which runs with CTranslate2, not with llama.cpp. The translation runs inside the problem's clock. If the packages or the model are missing, the problem goes on in Catalan.

## What the laptop measured

Practice set (`data/demo/train.jsonl`), 50 problems per language, same files and llama.cpp commit as the board. The board speed of Qwen2.5-Math is an estimate (5.2 tokens/s reading, 3.0 writing): Noema-2B's board speed scaled by the laptop ratio of the two models. The translation is charged 3 seconds per Catalan problem; on the laptop it takes 0.24 s.

| Setup | English | Catalan |
| --- | --- | --- |
| Any fixed letter | 10 | 10 |
| Noema-2B, program solver | 19 | 15 |
| Qwen2.5-Math, program solver | 29 | 14 |
| Qwen2.5-Math, program solver, Catalan translated | 29 | 26 |

With the translation, 20 Catalan programs are right and 4 wrong, against 7 and 2 without it. On held-out M3Kang problems, Qwen2.5-Math without translation got 15 right programs out of 83 English problems and 0 out of 80 Catalan ones.

These are laptop numbers. The board must give the real speed of the model and of the translation.

## Files to bring to the board

Nothing here goes into Git. Copy the files with `adb push` or `scp`.

| What | Where on the board | Size |
| --- | --- | --- |
| `Qwen2.5-Math-1.5B-Instruct-Q4_K_M.gguf` from `bartowski/Qwen2.5-Math-1.5B-Instruct-GGUF`, revision `951ed2aea09c43e331c612e74d83e4a23ca98e3b` | `~/models/` | 986 MB |
| The five files of `softcatala/translate-cat-eng`, revision `e2b54a61dcf367f02cd7a1c041e4e8f553ae001e`: `config.json`, `model.bin`, `shared_vocabulary.json`, `sp_m.model`, `model_description.txt` | `~/models/softcatala-cat-eng/` | 73 MB |
| Four wheels for aarch64 and Python 3.13: `ctranslate2` 4.9.0, `numpy` 2.5.4, `pyyaml` 6.0.3, `sentencepiece` 0.2.3 | `~/nmt-wheels/` | 37 MB |

To get the wheels on a laptop with internet:

```bash
mkdir -p nmt-wheels
pip download --platform manylinux_2_28_aarch64 --platform manylinux_2_17_aarch64 --platform manylinux2014_aarch64 \
  --python-version 3.13 --only-binary=:all: --dest nmt-wheels \
  ctranslate2==4.9.0 sentencepiece==0.2.3 numpy pyyaml
```

SHA256 of each file:

```text
9614a50f03c897028920ca0dc4365da570bf587f9ee7768261216fe370b37e8e  Qwen2.5-Math-1.5B-Instruct-Q4_K_M.gguf
3f1a3cc20b961c1fe0e6007e8ca663730c4a8b82fa54073fde03edf1402c6726  config.json
a5f75d254a26051cedfb198a6aacb7aac58ac37f863a1a9c865d1e199819de92  model.bin
9c8a375f96f4747803b20e27ae59e04a99904e691827300ac51760d3b87e91e1  model_description.txt
c1ad5fcf48510e58683c6bc657411c1b7e1d66710cf25e8305700441325ef1b1  shared_vocabulary.json
873eb09ce354fdbf8d4b625211bc073f2dc3cd6d2cd2366dcb5670c6c8ecb69d  sp_m.model
0f8bb74a0268f08adfaf01ed74209949a344f01f86713421f12810b99e7d46c9  ctranslate2-4.9.0-cp313-cp313-manylinux_2_27_aarch64.manylinux_2_28_aarch64.whl
1c2e71b04c6cad90026e544501bbe0ab9290fa8a4d845e7e8c0d124fb429c988  numpy-2.5.4-cp313-cp313-manylinux_2_27_aarch64.manylinux_2_28_aarch64.whl
ee2922902c45ae8ccada2c5b501ab86c36525b883eff4255313a253a3160861c  pyyaml-6.0.3-cp313-cp313-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl
dfc31f9f133a2712d396efa94d666c2ad83d5611ce34f11339429c6831253014  sentencepiece-0.2.3-cp313-cp313-manylinux_2_27_aarch64.manylinux_2_28_aarch64.whl
```

## 1. Get the build

```bash
cd ~/Santolina_tutor
git fetch
git checkout exp/noema-finetune
python3 --version
```

The wheels are for Python 3.13. If `python3 --version` prints another version, stop and report it.

## 2. Unpack the translation packages

A wheel is a zip file, so no `pip` is needed. Unpack the four wheels into one folder:

```bash
mkdir -p ~/nmt-site
for w in ~/nmt-wheels/*.whl; do python3 -m zipfile -e "$w" ~/nmt-site; done
```

`copilot/nmt.py` adds `~/nmt-site` to Python's path itself (`NMT_SITE` in `config.env`), so a plain `python3 predict.py` finds the packages.

Check the translation and time it:

```bash
python3 - <<'EOF'
import time
import copilot.nmt as n
print("available:", n.available())
start = time.perf_counter()
print(n.translate(["Quants minuts hi ha en 3 hores?"]))
print(f"{time.perf_counter() - start:.2f} s")
EOF
```

You should see `available: True` and `['How many minutes are there in 3 hours?']`. Write down the time. The first call loads the model; run the block twice and keep the second time.

## 3. Time Qwen2.5-Math

Follow steps 2 to 5 of [How to time a 2B model on the board](time-2b-model-on-board.md) with `-m ~/models/Qwen2.5-Math-1.5B-Instruct-Q4_K_M.gguf`. Write down the reading speed, the writing speed and the server's RSS.

## 4. Start the server (terminal 1)

```bash
sudo systemctl stop math-llm
~/llama.cpp/build/bin/llama-server \
  -m ~/models/Qwen2.5-Math-1.5B-Instruct-Q4_K_M.gguf \
  --host 127.0.0.1 --port 8090 \
  --threads 4 --ctx-size 4096 \
  --parallel 1 --cache-ram 0 \
  --jinja --reasoning off --reasoning-budget 0
```

It's ready when it prints `server is listening`.

## 5. Check the contract and measure (terminal 2)

Replace `5.2` with the reading speed from step 3:

```bash
export SOLVER=program TRANSLATE=nmt READ_TPS=5.2 LLM_PORT=8090
python3 predict.py --input data/sample_problems.jsonl --output results/check.csv
cat results/check.csv
python3 eval.py --input data/demo/train.jsonl --limit 0 --languages eng --name program-qmath-eng
python3 eval.py --input data/demo/train.jsonl --limit 0 --languages cat --name program-qmath-nmt-cat
```

The contract check must give five rows with one letter each, the status `ok` and every `seconds` value under 60.

## 6. Report the result

For each language, send:

- the accuracy line and the latency line (mean, median, worst, over 60 s)
- the table "By how it answered"
- the median of the `prompt_tokens` column
- from steps 2 and 3: the translation time, the reading and writing speeds, and the server's RSS

Don't send problem text or images. Aggregates and problem IDs are enough.

## Go back to the default

Stop the server with `Ctrl+C` in terminal 1, then `sudo systemctl start math-llm`. The settings were environment variables, so no file changed.

## Known limits

- The speeds of the model and of the translation are laptop estimates until step 3 and step 2 give board numbers.
- If the translation takes much longer than 3 seconds on the board, Catalan problems get less time to write their program. Set `NMT_THREADS` in `config.env` to try fewer threads.
- Problems with a figure go through the same path, with the statement and the OCR'd options only.
- The model was not fine-tuned. Both program fine-tunes (Noema-2B and Qwen2.5-Math) scored lower on the practice set than this untuned model, so use this GGUF.
