# Experiment: Noema-2B speed on the board

This report gives the speed and RAM of [Noema-2B](https://huggingface.co/NoemaAI-labs/Noema-2B) on the Arduino UNO Q. It follows steps 1 to 5 of [How to time a 2B model on the board](../how-to/time-2b-model-on-board.md). It is for the author of that guide and the team, to decide if a 2B model fits in the 60-second limit. Board run, 2026-11-15.

**Status: provisional.** The timing of steps 2 to 4 is complete. The run on the organizers' practice set was at 92 of 100 rows when we wrote this report. Its accuracy can still change.

## Summary

- **Noema-2B fits in RAM.** The server takes 1.38 GB, and about 2.8 GB stays available.
- **It reads at 4.9 tokens/s and writes at 2.4 tokens/s.** That is about half the speed of Qwen3.5-0.8B on the same board.
- **One forced letter fits easily.** On the practice set, the slowest of 92 problems took 28.1 s. None took more than 55 s.
- **A short program only just fits.** 74 written tokens took 51.5 s for the whole request.
- **Worked steps do not fit.** 132 written tokens took 81.1 s.

## Setup

| Item | Value |
|---|---|
| Model file | `Noema-2B-Q4_K_M.gguf` from `NoemaAI-labs/Noema-2B-GGUF` at `66d96b1`, 1.27 GB. SHA256 `e39e79c6…cb762`: `OK` |
| Download | On a laptop, then `adb push`. The board has no internet while its own Wi-Fi is on |
| llama.cpp | The board build, commit `2cbe0ec` |
| Server | By hand on port 8090 with the options of the `math-llm` service (step 3 of the guide). `math-llm` stopped (step 2) |
| Requests | The three requests of step 4, with `temperature 0` as in the guide |

The model card of Noema-2B says not to use greedy decoding (`temperature 0`). For one forced letter this has no effect on speed. For written answers, other settings can change the length of the output.

## Step 5: the numbers

| What | Noema-2B Q4_K_M | Qwen3.5-0.8B Q8_0, same board |
|---|---|---|
| RAM that the server takes (RSS) | 1,382 MB | about 900 MB |
| Time to load | 6 s | — |
| Reading speed (4.1) | 4.86 tokens/s (134 tokens) | about 10–11 tokens/s |
| Writing speed (4.2 and 4.3) | 2.44 and 2.42 tokens/s | about 4.8 tokens/s |
| Whole request, short program (4.2) | 51.5 s (104 tokens read, 74 written) | — |
| Whole request, worked steps (4.3) | 81.1 s (132 tokens read, 132 written) | — |
| Answer, forced letter (4.1) | C, right | — |
| Answer, program (4.2) | Counts 1 to 200 divisible by 3 and not by 5: returns 53, right | — |
| Answer, worked steps (4.3) | 25 rolls, `Answer: C`, right | — |

All the numbers are from the first run of each request. A second run of the same request reads only 4 tokens, because the server keeps the start of the prompt.

**RAM.** The `available` column of `free -m` fell by only 139 MB when the server started. The model file was still in the page cache after the copy, so `available` counted those pages before and after. The server's RSS, 1,382 MB, is the real size.

## What fits in 55 seconds

The guide's rule is `prompt tokens / reading speed + written tokens / writing speed <= 55 s`.

| Prompt | Reading time | Written tokens that fit |
|---|---|---|
| 110 tokens (the guide's estimate) | 22.6 s | about 78 |
| 134 tokens (request 4.1) | 27.6 s | about 66 |

The measured speeds lie between two rows of the guide's table. One row is "4 tokens/s and 2 tokens/s, about 55 written tokens". The other is "5 tokens/s and 2.5 tokens/s, about 80 written tokens". So a short program fits, but with little margin. The time to run the program on the board is not in this budget.

## One forced letter on the practice set (provisional)

`LLM_PORT=8090 SOLVER=letter python3 eval.py --input data/demo/train.jsonl --limit 0`, code of `main` at `5915b3c`. The data is the organizers' practice set, prepared as in [The organizers' practice set](../PRACTICE_SET.md) (options read on 100 of 100 rows).

| Measure | Noema-2B, 92 of 100 rows | Qwen3.5-0.8B, 100 of 100 rows |
|---|---|---|
| Mean time per problem | 17.7 s | 7.6 s |
| Median | 16.4 s | — |
| 90th percentile | 21.8 s | — |
| Slowest | 28.1 s | 13.6 s |
| Problems over 55 s | 0 | 0 |
| Mean time, English | 16.7 s (47 rows) | — |
| Mean time, Catalan | 18.7 s (45 rows) | — |
| Accuracy | 26.1 % so far | 22 % (English 12/50, Catalan 10/50) |

On the board, the Qwen3.5-0.8B baseline gives the same English score as the laptop in [The organizers' practice set](../PRACTICE_SET.md): 12 of 50. The prior solver gives 8 of 50 in each language, also the same as the laptop.

The accuracy of Noema-2B is not final. With 100 rows, one answer is 1 point and the 95 % interval is about ±8 points. Do not compare it with the baseline before the run ends.

## Next steps

- Finish the practice run and report the accuracy by language.
- Test the program solver: let the model write `solve()`, run it in a sandbox, and pick the option with the same value. Measure the whole time per problem, the run included.
- Try shorter prompts. Reading takes 23 to 28 s of the budget at this speed.
