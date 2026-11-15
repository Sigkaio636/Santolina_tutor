# Experiment: the program solver and the figure path on the board

This report gives the board results of two tests that Ferran asked for. It is for Ferran and the Claude session that works with him. Pau ran both tests on the Arduino UNO Q on 2026-11-15.

- **Test 1:** the program solver with Noema-2B, as in [How to try the program solver on the board](../how-to/try-program-solver.md), steps 1 to 5.
- **Test 2:** the figure path with the 0.8B vision model, timed with `board/time_vision.py`.

All numbers are aggregates, and the 6 timing lines of test 2 have problem IDs only. The per-row result files stay on the board, because the practice set went to the teams only.

## Summary

- **The program solver is the first real gain on the practice set**. English 20 of 50 (40 %), Catalan 17 of 50 (34 %). Any fixed letter scores 10 of 50 (20 %). Every forced-letter model scored 15–24 %.
- **The board agrees with the laptop**. The laptop predicted 19 of 50 and 15 of 50.
- **The prompt cache works with `--ctx-checkpoints 8`**. The median of `prompt_tokens` is 70.5 (English) and 77.5 (Catalan), and the maximum is 132.
- **No problem goes over 60 s**. The worst problem took 57.1 s.
- **17 of 100 rows end in `timeout`**. A timeout gives `D`.
- **The figure path fits in time, but the answers are wrong**. On 6 figure problems, the mean is 45.4 s and the worst is 48.9 s. The program was right on 1 of 6.
- **The vision server and Noema-2B fit in RAM together**. With both running, 2,359 MB stay available.

## Test 1: the program solver

### Setup

| Item | Value |
|---|---|
| Code | Branch `exp/program-solver` at `aa9fa17`, copied to a new folder on the board. No file changed |
| Model | `Noema-2B-Q4_K_M.gguf`, SHA256 `e39e79c6…b762`: `OK` |
| Server | Port 8090, the options of the guide, with `--ctx-checkpoints 8`. `math-llm` stopped |
| Data | The organizers' practice set, prepared as in [The organizers' practice set](../PRACTICE_SET.md). OCR read the options on 100 of 100 rows |
| Commands | `SOLVER=program LLM_PORT=8090 python3 eval.py --input data/demo/train.jsonl --limit 0 --languages eng` (then `cat`) |

Step 3 of the guide (the contract check with `predict.py` on `data/sample_problems.jsonl`) gave five rows, each with one letter and the status `ok`. The time per problem was 19.8 to 32.6 s.

### Results

| | English | Catalan |
|---|---|---|
| Accuracy | **20/50 (40 %)** | **17/50 (34 %)** |
| Laptop (the guide) | 19/50 | 15/50 |
| Mean time | 43.3 s | 43.3 s |
| Median time | 46.1 s | 44.7 s |
| Slowest | 57.1 s | 57.1 s |
| Over 60 s | 0 | 0 |
| Status `ok` / `timeout` | 42 / 8 | 41 / 9 |
| Median `prompt_tokens` | 70.5 | 77.5 |
| Maximum `prompt_tokens` | 113 | 132 |
| `prompt_tokens` of the first problem | 84 | 98 |

"By how it answered", from `eval.py`:

| Answered by | English | Catalan |
|---|---|---|
| Program | 14 of 23 right (61 %) | 10 of 20 right (50 %) |
| Letter after the program | 3 of 15 (20 %) | 3 of 17 (18 %) |
| `none` | 0 of 4 | 1 of 4 |

The other rows are the timeouts: 8 in English and 9 in Catalan. They get `D`.

Letters answered against the true letters (each letter is right 10 times per language):

| | A | B | C | D | E |
|---|---|---|---|---|---|
| English | 10 | 6 | 16 | 12 | 6 |
| Catalan | 8 | 9 | 14 | 15 | 4 |

Accuracy by level, English and Catalan together:

| Level | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|---|
| Right | 4/16 | 7/16 | 5/14 | 3/12 | 6/12 | 4/10 | 1/10 | 7/10 |

### RAM

| When | Server RSS |
|---|---|
| After the start, before any request | 1,404 MB |
| After 4 problems | 1,479 MB |
| After the 100 rows | 1,510 MB |

The guide expected about 155 MB more than with 2 checkpoints. The server grew by about 106 MB during the run.

### The warm-up

`eval.py` and `predict.py` start the clock of each problem after the warm-up. The first problem reported 23.6 s (English) and 33.0 s (Catalan), and 22.2 s in the contract check. We did not measure the warm-up alone.

### What to look at next

- **The timeouts are free points that we lose**. 17 of 100 rows end in `timeout` and get `D`. If the solver stopped the program earlier, the prior would answer these rows at no cost. A lower `READ_TPS` or a larger margin before the limit can do this. Check that the slowest problem stays under 57 s.
- **The program is the part that works**. Its answers are right 61 % (English) and 50 % (Catalan) of the time. The letter after the program is at chance (18–20 %). More rows that the program answers give more points.
- **Catalan is 6 points below English**. The program answers 20 Catalan rows against 23 English rows, and fewer of them are right.

## Test 2: the figure path

### Setup

| Item | Value |
|---|---|
| Code | Branch `exp/noema-finetune` at `4283b5a`, copied to a new folder on the board |
| Model | `Qwen_Qwen3.5-0.8B-Q8_0.gguf` with `mmproj-Qwen_Qwen3.5-0.8B-f16.gguf`, SHA256 `1dc1351c…2847`: `OK`. The board has no internet, so the projector came from a laptop with `adb push` |
| Server | Port 8083, the options of `docs/BOARD_SETUP.md` ("Let the model see the image"), with `--image-max-tokens 128`. Alone on the board, apart from the embedding server |
| Command | `python3 board/time_vision.py --input data/demo/train.jsonl --images data/demo/images --limit 6` |

### Results

```text
lvl-0_2026_3 eng: 48.2 s | read 174 tokens in 35.0 s | wrote 72 in 13.0 s | answer None (truth E)
lvl-0_2026_3 cat: 47.7 s | read 176 tokens in 35.1 s | wrote 68 in 12.3 s | answer None (truth E)
lvl-1_2026_2 eng: 40.7 s | read 185 tokens in 34.9 s | wrote 31 in 5.4 s | answer D (truth D)
lvl-1_2026_2 cat: 43.4 s | read 202 tokens in 36.1 s | wrote 39 in 7.0 s | answer A (truth D)
lvl-2_2026_2 eng: 43.3 s | read 194 tokens in 37.0 s | wrote 34 in 6.0 s | answer None (truth D)
lvl-2_2026_2 cat: 48.9 s | read 206 tokens in 38.0 s | wrote 59 in 10.7 s | answer E (truth D)

6 problems: mean 45.4 s, worst 48.9 s, over 57 s: 0, program right: 1
```

- **Reading takes most of the time:** 174–206 tokens in 35–38 s, about 5 tokens/s with the image. Text alone reads at about 10 tokens/s on the 0.8B model.
- **Writing:** 31–72 tokens in 5.4–13.0 s, about 5.5 tokens/s.
- **Answers:** the program was right on 1 of 6. Three programs gave no option.

### RAM

`free -m`, column `available`. The embedding server (`math-embed`) ran in all cases.

| What runs | Available | Server RSS |
|---|---|---|
| No language model (before the test) | 2,956 MB | — |
| Vision server alone, after the start | 2,642 MB | 1,159 MB |
| Vision server alone, after the 6 problems | 2,533 MB | 1,286 MB |
| **Vision server and Noema-2B together** | **2,359 MB** | vision 1,209 MB, Noema-2B 1,413 MB |

With both servers, swap held 106 MB. Noema-2B still answered a request correctly while the vision server ran. The two servers fit in RAM together. We did not time them together.

## Board state after the tests

`math-llm` serves Qwen3.5-0.8B again. Its service file is the same as before the tests. The student app, the LED app and `math-embed` run. No test server runs.
