# Experiment: the prior solver on the board

This report gives the board results of the prior solver (`copilot/prior.py`, commit `5915b3c`). It follows steps 1 to 4 of [How to try the prior solver on the board](../how-to/try-prior-solver.md). It is for the author of that guide, so he can compare the board with the laptop. Board run, 2026-11-14.

All numbers are aggregates. The per-row result files stay on the board, because they come from [M3Kang](https://huggingface.co/datasets/qualcomm/M3Kang) problems.

## Summary

- **The contract check (step 2) gives the expected output.** Five rows, letters C, B, C, C, C, status `ok`, 0.0 s each.
- **The prior scores 27.4 % on the board's validation set** (154 of 562 rows, 95 % Wilson interval 23.9–31.2 %). The best fixed letter on this set is D, at 23.1 %. The whole interval is above it.
- **English agrees with the laptop (28.1 % against 27.8 %). Catalan does not (26.7 % against 28.1 %).** The board's `data/val.jsonl` is not the laptop's file (see [Why the numbers differ](#why-the-numbers-differ)).
- **The Spanish run stops with an error,** because the board's file has no Spanish rows (see [A bug in eval.py](#a-bug-in-evalpy)).

## Setup

| Item | Value |
|---|---|
| Board | Arduino UNO Q 4 GB, Debian 13 |
| Code | `origin/main` at `5915b3c`, copied to a new folder on the board (the board has no internet) |
| Settings | `config.env` unchanged: `SOLVER=prior`, `FALLBACK_ANSWER=D` |
| Data | `data/val.jsonl` of the board: 562 rows, English 281 and Catalan 281, no Spanish. Prepared on a laptop CPU with RapidOCR (PP-OCRv4) and the `parse_options` of `main`, before the C and A label fixes |
| Rows with five options | 339 of 562 (60.3 %) |

## Step 3: the lines in `results/ablations.csv`

```text
time,name,commit,input,languages,n,rag_k,accuracy,mean_s,worst_s,over_limit
20261114-220914,prior,,data/val.jsonl,all,562,0,27.4,0.0,0.0,0
20261114-220915,prior-cat,,data/val.jsonl,cat,281,0,26.7,0.0,0.0,0
20261114-220915,prior-eng,,data/val.jsonl,eng,281,0,28.1,0.0,0.0,0
```

| Language | Rows | Board | Laptop (the guide) | Difference |
|---|---|---|---|---|
| English | 281 | 28.1 % | 27.8 % | +0.3 pp |
| Catalan | 281 | 26.7 % | 28.1 % | −1.4 pp |
| Spanish | 0 | no run | 28.2 % | — |
| All | 562 | 27.4 % | — | — |

## Where the gain comes from

| Rows | n | Prior | Best fixed letter | Letters that the prior answers |
|---|---|---|---|---|
| With five options | 339 | 28.3 % | A, 21.8 % | C 159, D 112, B 35, A 19, E 14 |
| Without options | 223 | 26.0 % | D, 26.0 % | D 223 |
| All | 562 | 27.4 % | D, 23.1 % | — |

The rule adds accuracy only where the options are there. Without options it answers D, the fallback letter, so it scores the same as always D.

## The same 50 problems as the model runs

Step 11 of the board guide uses 50 validation problems (`eval.py --limit 50`). We ran three other solvers on the same 50 problems. The model runs used the code of branch `exp/decider-0.8b` at `b219ba5`. Its default path is the same as on `main` before `5915b3c`.

| Solver | Right answers | Mean time |
|---|---|---|
| Qwen3.5-0.8B Q8_0, forced letter (the earlier baseline) | 10 of 50 (20.0 %) | 9.4 s |
| Qwen3.5-0.8B with the decider prompt | 10 of 50 (20.0 %) | 9.8 s |
| decider-0.8b Q8_0 | 11 of 50 (22.0 %) | 9.7 s |
| **Prior** | **14 of 50 (28.0 %)** | 0.0 s |

Exact McNemar, prior against the baseline: the prior alone is right on 11 problems and the baseline alone on 7, p = 0.48. With 50 problems, this is no evidence of a difference. The full set above is the better test.

The baseline gave the same 50 letters as an earlier run with the organizers' code, so the board's results repeat.

## Why the numbers differ

Step 4 of the guide says that a difference means another `data/val.jsonl`. That is the case here:

- The board has no Spanish rows. The laptop file has 789 rows, with 227 in Spanish.
- Both files have 281 English rows and 281 Catalan rows. So they probably hold the same problems, with different option text.
- The board's file comes from the OCR on a CPU and from the parser before the C and A label fixes of branch `exp/decider-0.8b`. A problem with no options, or with other option values, can get another letter from the prior.

We did not compare the two files row by row. To do that, compare the problem ids and the option values of the two `val.jsonl` files on a laptop. Do not commit them.

## A bug in `eval.py`

`python3 eval.py --limit 0 --languages esp --name prior-esp` stops with `ZeroDivisionError` at `accuracy = 100 * sum(hits) / len(hits)`, because no row matches the language. The script could print "no problems for language esp" and stop.
