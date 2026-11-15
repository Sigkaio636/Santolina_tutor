# Experiment: four solvers on the practice set, on the board

This report gives the scores of four solvers on the organizers' practice set, measured on the Arduino UNO Q. It is for the team, to choose what to build for the final test. Board run, 2026-11-15.

[The organizers' practice set](../PRACTICE_SET.md) describes the practice set and the final test. All numbers are aggregates: the per-row result files stay on the board.

## Summary

- **No solver is clearly better than a fixed letter.** Each letter is right 20 times, so any fixed letter scores 20 %. The best solver scores 24 %, with a 95 % interval of 17–33 %.
- **The board gives the same scores as the laptop** for the two solvers that the laptop measured. Qwen3.5-0.8B gets 12 of 50 in English, and the prior solver gets 8 of 50 in each language.
- **Each model answers mostly one letter.** Noema-2B answers C on 84 rows, Qwen3.5-0.8B answers D on 73, and decider-0.8b answers D on 42.
- **All solvers stay well inside 60 seconds** when they answer one forced letter. The slowest problem took 28.1 s, with Noema-2B.

## Results

100 rows: 50 problems, each in English and Catalan.

| Solver | Right | 95 % interval | English | Catalan | Mean time | Slowest | Letters answered |
|---|---|---|---|---|---|---|---|
| Noema-2B Q4_K_M, forced letter | 24 | 17–33 % | 12 | 12 | 17.7 s | 28.1 s | C 84, B 12, D 2, A 1, E 1 |
| Qwen3.5-0.8B Q8_0, forced letter (baseline) | 22 | 15–31 % | 12 | 10 | 7.6 s | 13.6 s | D 73, A 18, B 7, E 2 |
| Prior solver (`SOLVER=prior`) | 16 | 10–24 % | 8 | 8 | 0.0 s | 0.0 s | C 90, D 10 |
| decider-0.8b Q8_0, decider prompt | 15 | 9–23 % | 9 | 6 | 7.7 s | 12.0 s | D 42, C 29, B 13, E 9, A 7 |
| Any fixed letter | 20 | | 10 | 10 | | | |

Exact McNemar against the baseline, on the same 100 rows:

| Solver | Only the baseline right | Only this solver right | p |
|---|---|---|---|
| Noema-2B | 20 | 22 | 0.88 |
| Prior solver | 22 | 16 | 0.42 |
| decider-0.8b | 18 | 11 | 0.26 |

None of the differences is significant. With 100 rows, one answer is 1 point. In the final test, with 20 problems, one answer is 5 points.

## What this tells us

- **On this set, a forced letter from a small model is close to guessing.** All three models stay near 20 %. The set balances the letters, so a bias to one letter gains nothing. On M3Kang, the same bias could look like a gain.
- **The prior solver loses its gain.** The practice set lists its options in order, so the median value is always option C. C is right on 20 % of the rows.
- **decider-0.8b is the weakest model here,** mostly in Catalan (6 of 50). Its model card says that it is for English only.
- **A larger model alone does not help with a forced letter.** Noema-2B is 2.5 times slower than Qwen3.5-0.8B and scores 2 rows more. Its speed and the time budget for written answers are in [Noema-2B speed on the board](2026-11-noema-2b-board-timing.md).

## Setup

| Item | Value |
|---|---|
| Data | `demo-00000-of-00001.parquet` from the organizers, prepared on a laptop with `laptop/prepare_m3kang.py --languages eng,cat --val-fraction 0 --out data/demo`. OCR read all five options on 100 of 100 rows |
| Command | `python3 eval.py --input data/demo/train.jsonl --limit 0` |
| Baseline and prior solver | Code of `main` at `5915b3c`, with `SOLVER=letter` and `SOLVER=prior` |
| Noema-2B | The same code, `SOLVER=letter`, `LLM_PORT=8090`. The server runs by hand, as in [How to time a 2B model on the board](../how-to/time-2b-model-on-board.md). `math-llm` stopped |
| decider-0.8b | Code of branch `exp/decider-0.8b` at `b219ba5`, `LLM_PROMPT=decider`, installed as in `docs/INSTALL_DECIDER.md` on that branch |
| llama.cpp | The board build, commit `2cbe0ec` |
| Decoding | Grammar `root ::= [A-E]`, temperature 0, seed 42, one token |

After the runs, `math-llm` serves Qwen3.5-0.8B again. Its service file is the same as before the runs.

### The decider-0.8b file

We converted decider-0.8b ourselves, with the commands of `INSTALL_DECIDER.md`. Our file has SHA256 `bc187f9f…9e4b`, not the `f0707b86…b007` in that guide. The llama.cpp commit and the revision of the weights are the same as in the guide. The difference is in the metadata: `convert_hf_to_gguf.py` writes the name of the download folder into the file. Two conversions from two folder names gave the same tensors and different checksums. To get the same file on every computer, give the name with `--model-name`.
