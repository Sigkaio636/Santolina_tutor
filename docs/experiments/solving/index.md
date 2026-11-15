# Solving the problem

**Question:** which solver gives `predict.py` the most right letters, inside 60 seconds per problem, on the board?

**Where it lives:** `predict.py` (the organizers' contract) and `copilot/`. The setting `SOLVER` in `config.env` picks the solver:

- `SOLVER=prior` is the default. A fixed rule on the option values, with no model call (`copilot/prior.py`).
- Any other value runs the letter path: Qwen3.5 0.8B on `math-llm` (port 8081) gives one letter.

The program solvers below are on the branch [`exp/noema-finetune`](https://github.com/Sigkaio636/Santolina_tutor/tree/02d4e4c), not on `main`.

## Results on the organizers' practice set

50 new Kangaroo-style problems, each in English and Catalan: 100 rows. Each letter is right on 20 rows. Board runs, 2026-11-15, 60 s per problem. Source: the [README results](https://github.com/Sigkaio636/Santolina_tutor#results), which link the two board reports.

| Solver | On `main`? | Right of 100 | English, of 50 | Catalan, of 50 | Mean time | Worst time |
| --- | --- | --- | --- | --- | --- | --- |
| Noema-2B writes a program | No: branch | 37 | 20 | 17 | 43.3 s | 57.1 s |
| Noema-2B, one forced letter | No | 24 | 12 | 12 | 17.7 s | 28.1 s |
| Qwen3.5 0.8B, one forced letter | Yes, `SOLVER=letter` | 22 | 12 | 10 | 7.6 s | 13.6 s |
| Any fixed letter | | 20 | 10 | 10 | 0 s | 0 s |
| **Prior rule on the option values** | **Yes, the default** | **16** | 8 | 8 | 0 s | 0 s |
| decider-0.8b, one forced letter | No | 15 | 9 | 6 | 7.7 s | 12.0 s |

**The best pipeline so far** (laptop runs that charge the board's estimated speeds: 5.2 tokens/s reading, 3.0 tokens/s writing, 3 s per translation):

- Qwen2.5-Math-1.5B-Instruct (Q4_K_M, not fine-tuned) writes a Python `solve()`.
- A Catalan statement first goes through the softcatala/translate-cat-eng translation model.
- Score: **29 of 50 in English and 26 of 50 in Catalan**, 55 of 100. On held-out M3Kang problems: 36 of 83 in English and 29 of 80 in Catalan.

The [README](https://github.com/Sigkaio636/Santolina_tutor#our-best-pipeline-qwen25-math-writes-a-program-catalan-translated-first) has the diagram and the full table.

## Reports

| Date | Report | Setup | Rows | Result | Verdict |
| --- | --- | --- | --- | --- | --- |
| 2026-11-14 | [decider-0.8b vs the baseline](../2026-11-decider-0.8b.md) | Laptop, M3Kang validation set | 789 | 24.0 % against 22.4 %, +1.5 pp, p = 0.50 | Not adopted |
| 2026-11-14 | [Practice set: what we measured](../../PRACTICE_SET.md#what-we-measured-on-2026-11-14) | Laptop | 50 English | Prior rule 8 of 50, fixed letter 10, model letter 12 | Don't ship the prior rule |
| 2026-11-15 | Four solvers on the practice set ([report at `1049459`](https://github.com/Sigkaio636/Santolina_tutor/blob/1049459dfdcfb8c53a261844200a743204825206/docs/experiments/2026-11-practice-set-on-board.md)) | Board | 100 | Table above | Letter path above the prior rule |
| 2026-11-15 | Program solver on the board ([report at `b956cf0`](https://github.com/Sigkaio636/Santolina_tutor/blob/b956cf03dadb675bea796181dac01d2b77b1a38b/docs/experiments/2026-11-program-solver-and-vision-on-board.md)) | Board | 100 | 37 of 100 | Best on the board. Not merged. |

The two board reports are not on `main` yet. The links go to the commits that hold them.

## Current decision

- **`main` ships `SOLVER=prior`.** On the practice set it scores 16 of 100, below a fixed letter. It answers C on 90 rows, because the practice set lists numeric options in increasing order.
- **Open: the configuration for the hidden test.** `SOLVER=letter` scored 22 of 100. The program solver with translation is the strongest, but it needs its model server started by hand on port 8090 in place of `math-llm`.
- **Open: the input format.** A teammate's commit says the final test gives the image without the options as text ([practice set page](../../PRACTICE_SET.md#what-the-organizers-said)). `predict.py` on `main` reads JSONL only and reads no images.

## What we learned

- **One forced letter is close to chance** for every small model we tried. Each one leans on one letter.
- **A program helps when its value matches an option.** Then it is right 70 % to 83 % of the time. The other right answers come from the fallback.
- **The translation is what helps Catalan.** On the practice set, Catalan went from 14 to 26 of 50 with it.
- **Worked steps don't fit.** Noema-2B writes about 2.4 tokens per second on the board: 132 tokens took 81 s.
