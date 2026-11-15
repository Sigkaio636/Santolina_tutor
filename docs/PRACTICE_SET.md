# The organizers' practice set and what it says about the final test

On 2026-11-14 the organizers sent every team a practice set and described the final evaluation. This page records what they said, how to load the set, and what we measured on it. It replaces our earlier guesses about the hidden test, including the note on the expected test format on the `exp/decider-0.8b` branch. For the rest of what the challenge asks, see [the challenge musts](GOAL_MUSTS.md).

The practice file is not in this repository. The repository is public, the file's licence is "other", and the organizers sent it to the teams only. Get `demo-00000-of-00001.parquet` from the organizers' message, or from a teammate, and keep it under `data/`, which Git ignores.

## What the organizers said

- The practice set has 50 new Kangaroo-style problems, each in English and Catalan: 100 rows. Its README says they were written for the datathon and are not M3Kang problems.
- The final test has 20 different problems. Each one comes in one language, English or Catalan. Levels 0 to 7. Four of the 20 have a figure.
- They run it with our `predict.py` on the board, after the last call at 12:00.
- At most 60 seconds per problem, and everything runs locally on the board, with no network.

## The format

Same columns as M3Kang:

| Column | Content |
| --- | --- |
| `id` | `lvl-<level>_2026_<number>`. Translations share the `id`. |
| `level` | 0 to 7 (level 0 is grade 5) |
| `language` | `eng` or `cat` |
| `text_only` | `false` if the problem needs its figure |
| `image` | The full problem: statement, figure if any, and the options A) to E) |
| `text` | `"<number>. <statement>"`, without the options |
| `label` | The correct letter |

As in M3Kang, the options are only in the image. `prepare_m3kang.py` reads them with OCR.

## How to load it

On your laptop, with the OCR requirements installed ([step 9 of the board guide](BOARD_SETUP.md#step-9-prepare-m3kang-on-your-laptop)):

```bash
python3 laptop/prepare_m3kang.py --parquet data/demo-00000-of-00001.parquet --languages eng,cat --val-fraction 0 --out data/demo --save-images
python3 eval.py --input data/demo/train.jsonl --limit 0 --name demo
```

`--val-fraction 0` puts all 100 rows in `data/demo/train.jsonl`. Copy that file to the board to run `eval.py` there.

## What we measured on it

Laptop, 2026-11-14, after the command above.

| Measure | Value |
| --- | --- |
| Rows | 100: 50 English, 50 Catalan |
| Text-only rows | 80 (40 problems). The other 20 rows (10 problems) need a figure. |
| Rows where OCR read all five options | 100 of 100, figure problems included |
| Correct letter | Each of A to E is correct 20 times |
| Options that are five distinct numbers listed in order | 90 of 100 |
| Statement length | Median 128 characters, longest 299 |
| Problems per level, 0 to 7 | 8, 8, 7, 6, 6, 5, 5, 5 |

Scores on the 50 English problems:

| Solver | Correct |
| --- | --- |
| Any fixed letter | 10 of 50 (20%) |
| The prior solver (`SOLVER=prior`) | 8 of 50 (16%); the same on the Catalan rows |
| The baseline letter from Qwen3.5 0.8B (`SOLVER=letter`) | 12 of 50 (24%); it answered D 36 times |

## What this changes

- The prior solver does not work on this set. It gained on M3Kang because real Kangaroo papers rarely put the answer at the smallest or largest value, and often list the options out of order. Here the answer position is balanced and the options are sorted. `SOLVER=prior` should not be the final default.
- Problems arrive with their options, so the case "no options" matters much less than on M3Kang.
- The problems are new, so looking up the same problem in M3Kang or in past papers will not find them. The closest past problem to each practice problem shares about a third of its words.
- Most answers are numbers and the statements are short. Reading a statement takes about 5 seconds on the board, which leaves about 50 seconds to compute. The work now goes into solvers that compute the value (written steps, or a short program run in a sandbox) and into testing larger models that still fit in 60 seconds.
- With 20 test problems, one answer is 5 points. Small differences between solvers on the practice set are noise: compare solvers on all 50 problems, in both languages.
- No Spanish in the final test.
