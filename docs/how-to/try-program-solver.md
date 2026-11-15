# How to try the program solver on the board

This guide runs the program solver with Noema-2B on the Arduino UNO Q and measures it on the organizers' practice set. Follow it after [How to time a 2B model on the board](time-2b-model-on-board.md): you need Noema-2B in `~/models` on the board and the speeds from [the Noema-2B timing report](../experiments/2026-11-noema-2b-board-timing.md).

## What the solver does

With `SOLVER=program`, `copilot/pipeline.py` hands each problem to `solve_board()` in `copilot/program_head.py`:

1. The model writes a short Python `solve()` for the problem. The prompt asks for brute force with loops, at most 12 lines and no comments, and shows two made-up worked examples.
2. Python runs the program in a separate process, for at most 2 seconds, and compares its value with the five options.
3. If the value equals exactly one option, that letter is the answer.
4. If not, and about 7 seconds are still left, the model gives one letter in the same conversation, right after its program. Only the question is new to the server, about 25 tokens.
5. Otherwise the answer is the prior's letter (`copilot/prior.py`), which costs no time. If a request fails, it's `FALLBACK_ANSWER` (D).

The time limit decides how long the model writes. The request sets `t_max_predict_ms`, so the server stops writing 1 second before the limit, which leaves time to run the program. The program comes before the letter because correct programs need 40 to 80 tokens, and the letter is right only about one time in four.

The system prompt and the two examples are the same for every problem, about 290 tokens. The server reads them once, before the first problem (`warm_up()`), and keeps them in its prompt cache. After that, a problem costs only its own tokens of reading, about 50. The warm-up happens before the first problem's clock starts, and it takes about a minute on the board.

## What the laptop measured

Practice set (`data/demo/train.jsonl`), 50 problems per language, same model file and llama.cpp commit as the board. Writing budgets are worked out from the board speeds (4.86 tokens/s reading, 2.42 tokens/s writing).

| Solver | English | Catalan |
| --- | --- | --- |
| Any fixed letter | 10 | 10 |
| Qwen3.5 0.8B, one letter (`SOLVER=letter`) | 12 | 9 |
| Noema-2B, one letter | 13 | not measured |
| Noema-2B, program, then letter or prior (`SOLVER=program`) | 19 | 15 |

How the program solver answered:

| | English | Catalan |
| --- | --- | --- |
| Program value matched one option | 25 (16 right) | 19 (9 right) |
| Letter after the program | 9 | 16 |
| Prior's letter (no time left) | 16 | 15 |
| Estimated board time per problem | median 48 s, worst 57 s | median 44 s, worst 57 s |

The number to watch is how many programs are right. The letter and the prior are close to a guess on this set.

These are laptop numbers. The board must confirm them, mainly the time per problem.

## Before you start

- The board has `~/models/Noema-2B-Q4_K_M.gguf` (SHA256 `e39e79c6…b762`) from the timing run.
- The practice set is on the board at `data/demo/train.jsonl`, prepared as in [The organizers' practice set](../PRACTICE_SET.md).
- The board is idle. A practice run takes about 40 minutes per language.

## 1. Get the build

On the board, in the repository folder:

```bash
cd ~/Santolina_tutor
git fetch
git checkout exp/program-solver
```

Without internet on the board, copy the four files from a laptop that has the branch:

```bash
scp copilot/program_head.py copilot/pipeline.py arduino@192.168.1.131:~/Santolina_tutor/copilot/
scp config.env eval.py arduino@192.168.1.131:~/Santolina_tutor/
```

Use your board's address or user if they differ. `config.env` still says `SOLVER=prior`. The commands below set the solver and the port for each run, so you don't edit any file.

## 2. Start Noema-2B (terminal 1)

```bash
sudo systemctl stop math-llm
~/llama.cpp/build/bin/llama-server \
  -m ~/models/Noema-2B-Q4_K_M.gguf \
  --host 127.0.0.1 --port 8090 \
  --threads 4 --ctx-size 4096 \
  --parallel 1 --cache-ram 0 --ctx-checkpoints 8 \
  --jinja --reasoning off --reasoning-budget 0
```

The options are the ones from the timing guide, except `--ctx-checkpoints 8` in place of 2. Noema-2B is a hybrid model: the server can go back to an earlier point of the prompt only at a saved checkpoint. With 2 checkpoints, the requests of one problem push out the checkpoint at the end of the fixed prompt. The next problem then reads all of its roughly 330 tokens again, about 70 seconds on the board. On the laptop, 8 checkpoints kept each program request at 50 to 135 tokens read and each letter request at 24. They cost 19 MB each, about 155 MB in total.

Leave the server running. It's ready when it prints `server is listening`.

## 3. Check the contract (terminal 2)

```bash
cd ~/Santolina_tutor
mkdir -p results
SOLVER=program LLM_PORT=8090 python3 predict.py --input data/sample_problems.jsonl --output results/check.csv
cat results/check.csv
```

You should see five rows, each with one letter from A to E and the status `ok`. The first problem waits about a minute for the warm-up before its clock starts. Every `seconds` value must be under 60.

## 4. Measure it on the practice set

```bash
SOLVER=program LLM_PORT=8090 python3 eval.py --input data/demo/train.jsonl --limit 0 --languages eng --name program-noema-eng
SOLVER=program LLM_PORT=8090 python3 eval.py --input data/demo/train.jsonl --limit 0 --languages cat --name program-noema-cat
```

While it runs, check that the cache works. Each problem's `prompt_tokens` in the `results/eval-…-program-noema-eng.csv` file should be about 50 to 140. Values of 330 or more mean the server reads the whole fixed prompt for every problem. In that case, stop the run and report it, because every problem will be close to the limit.

## 5. Report the result

For each language, send:

- the accuracy line and the latency line (mean, median, worst, over 60 s)
- the table "By how it answered": how many problems the program answered and how many the letter answered, with the accuracy of each
- the median of the `prompt_tokens` column
- the server's RSS during the run (`ps -o rss= -C llama-server`)

Don't send problem text or images. Aggregates and problem IDs are enough.

## Go back to the default

Stop the server with `Ctrl+C` in terminal 1. Then:

```bash
sudo systemctl start math-llm
curl -s http://127.0.0.1:8081/health
```

## Known limits

- The input must carry the options. `predict.py` reads a JSONL file, and the options come from OCR of the image. The organizers' README and `laptop/requirements.txt` point to OCR on a laptop with `prepare_m3kang.py` before the run, since the board has no OCR. Without options, the program's value has nothing to match, and every answer is a guess.
- Problems with a figure go through the same path, with the statement and the OCR'd options only. The model doesn't see the figure.
- Catalan problems are solved in Catalan. On the laptop that costs a lot of accuracy. Translating the statement first is the next experiment.
- The warm-up runs before the first problem's clock. If the jury times the whole `predict.py` run per problem, the first problem may count it.
- `READ_TPS` in `config.env` (4.86) estimates how long the board takes to read. If the board reads slower than that, the program request can run past the limit. It then times out, and the answer is D.

## If you work with Claude on the board

Give it this request:

> Read docs/how-to/try-program-solver.md and follow steps 1 to 5 on the board. Use the unoq-board skill to connect. Don't change any code. Report the numbers that step 5 asks for, per language.
