# Experiment: no-model heuristics for figure problems (txto_no)

Status: **analysis done on 2026-11-15.** Laptop only, branch `exp/decider-0.8b`.
No model is called: every number here comes from the dataset labels.

The task: pick the right letter (A–E) for multiple-choice maths problems from the
Kangaroo competition ([M3Kang](https://huggingface.co/datasets/qualcomm/M3Kang)).
This page covers only the problems that come with a figure (`text_only` is false,
"txto_no"), and grades each answer against the dataset's `label` column.

## Summary

- Shipping a vision model for figure problems is not viable on the board. The
  three vision models we tried all score at or below the 25 % you get by always
  answering D, and the one that fits the board's time limit is the worst of them.
- So figure problems get a heuristic, not a model. We measured eight heuristics,
  each against always answering D. **None of them is measurably better than D**
  under the rule below.
- Decision: **answer D on every figure problem**, whatever the options look like.
  Expected accuracy: about 25 % (24.9 % on the 2,585 train and val rows).
- One candidate comes close: the median value when the options are numbers that are
  not listed in order (33 % against 22 % for D, p = 0.14). It stays a candidate. Reopen
  it when more labelled figure problems are available.

## Why a vision model is not viable

| Model | Rows | With the image | Always D on the same rows | Fits the board? | Report |
|---|---|---|---|---|---|
| Qwen3.5-0.8B (already on the board), image ≤128 tokens | 440 | 17.3 % | 25.2 % | Yes: 28–38 s per problem | [vision on txto_no](2026-11-vision-txto-no.md) |
| decider-2b-vision, image ≤128 tokens | 160 (figure logic) | 24.4 % | 30.0 % | No: 2.86 GB RAM, very likely over 60 s | [decider-2b-vision](2026-11-decider-2b-vision-figure-logic.md) |
| decider-2b-vision, image ≤128 tokens | 175 | 22.3 % | 25.1 % | No | [InternVL vs decider](2026-11-internvl35-1b-vs-decider-2b-vision-txto-no.md) |
| InternVL3.5-1B, one 448 px tile | 175 | 17.1 % | 25.1 % | Not measured; estimated over 60 s | [InternVL vs decider](2026-11-internvl35-1b-vs-decider-2b-vision-txto-no.md) |

No model beats always answering D. No model gains from the image against its own
run without the image. Qwen3.5-0.8B with the image does worse than the same model
on text only (22.5 %, p = 0.052). The vision models also have strong letter biases: Qwen never answers B,
and InternVL almost never answers B or C.

## Data

- **Train:** the figure rows of `data/train.jsonl`, 2,145 rows (778 problems).
- **Val:** `data/interim/val_txto_no.jsonl`, 440 rows (158 problems).
- Train and val share no problem id. Each problem appears in up to three languages
  (eng, cat, esp) with the same label. So the real sample is the number of problems,
  not rows, and the paired tests below use one row per problem.

## What the options look like

The copilot sees the problem text and, when OCR found them, the five options.
`kind()` in `copilot/prior.py` sorts each row into one of four cases:

| Case | What it is | Train rows (problems) | Val rows (problems) |
|---|---|---|---|
| `none` | OCR found no options. The options are pictures inside the figure (shapes, patterns, positions), or OCR failed. We can't tell which without the image. | 1,013 (404) | 216 (85) |
| `text` | Five options, but at least one is not a single number: expressions, two numbers, units, words. 94 % of these options contain a digit. Median length 4 characters. | 490 (204) | 86 (38) |
| `sorted` | Five distinct numbers, listed from smallest to largest (or the reverse) | 419 (163) | 80 (31) |
| `mixed` | Five distinct numbers, not listed in value order | 223 (89) | 58 (24) |

Rows with five numbers that are not all different (11 in train) count as `text`.

Label shares by case, train and val together:

| Case | A | B | C | D | E |
|---|---|---|---|---|---|
| `none` | 17.3 % | 18.0 % | 20.8 % | **26.0 %** | 17.8 % |
| `text` | 16.3 % | 20.0 % | 20.3 % | **21.9 %** | 21.5 % |
| `sorted` | 10.2 % | 23.6 % | **27.3 %** | **27.3 %** | 11.6 % |
| `mixed` | 19.9 % | 21.7 % | 13.9 % | 21.7 % | **22.8 %** |

D is the most common answer overall (24.9 %), and the most common or tied in three of
the four cases.

For numeric options, the answer is rarely the smallest or the largest value. Answer
position by value rank, 1 = smallest, train and val together:

| Case | 1 | 2 | 3 (median) | 4 | 5 |
|---|---|---|---|---|---|
| `sorted` | 9.6 % | 26.1 % | 27.3 % | 24.8 % | 12.2 % |
| `mixed` | 12.1 % | 21.4 % | 33.1 % | 24.2 % | 9.3 % |

So in the `sorted` case the middle three ranks are about equally likely. In the
`mixed` case the median stands out.

## Decision rule

A heuristic replaces D on a case only if both hold:

1. It gets more rows right than D on that case, in train **and** in val.
2. On train and val together, an exact McNemar test against D, with one row per
   problem, gives p < 0.05.

If no heuristic passes on a case, that case answers D.

This rule was written after a first look at the train and val numbers, not before.
That makes it weaker than a pre-registered rule, so a heuristic that passes it should
still be checked on new data.

## Results

Rows right with the heuristic and with D, and the paired test on train and val together:

| Case | Heuristic | Train | Val | Problems | Only the rule right / only D right | p | Passes? |
|---|---|---|---|---|---|---|---|
| `sorted` | median value | 25.1 / 28.2 % | 38.8 / 22.5 % | 194 | 54 / 55 | 1.00 | No |
| `sorted` | rank 2 | 27.4 / 28.2 % | 18.8 / 22.5 % | 194 | 39 / 45 | 0.59 | No |
| `sorted` | rank 4 | 25.3 / 28.2 % | 22.5 / 22.5 % | 194 | 6 / 10 | 0.45 | No |
| `sorted` | closest to the mean | 25.3 / 28.2 % | 35.0 / 22.5 % | 194 | 51 / 53 | 0.92 | No |
| `sorted` | has a neighbour (±1, ×2, ÷2) | 29.6 / 28.2 % | 26.2 / 22.5 % | 194 | 17 / 15 | 0.86 | No |
| `mixed` | **median value** | 32.7 / 22.4 % | 34.5 / 19.0 % | 113 | 28 / 17 | **0.14** | No (condition 2) |
| `mixed` | rank 2 | 21.1 / 22.4 % | 22.4 / 19.0 % | 113 | 21 / 24 | 0.77 | No |
| `mixed` | rank 4 | 22.9 / 22.4 % | 29.3 / 19.0 % | 113 | 22 / 19 | 0.76 | No |
| `mixed` | closest to the mean | 32.3 / 22.4 % | 27.6 / 19.0 % | 113 | 27 / 17 | 0.17 | No |
| `mixed` | has a neighbour | 32.7 / 22.4 % | 27.6 / 19.0 % | 113 | 19 / 9 | 0.087 | No |
| `text` | longest option | 23.7 / 22.0 % | 23.3 / 20.9 % | 242 | 40 / 38 | 0.91 | No |
| `text` | shortest option | 19.8 / 22.0 % | 20.9 / 20.9 % | 242 | 20 / 26 | 0.46 | No |
| `text` | most similar to the others | 20.2 / 22.0 % | 17.4 / 20.9 % | 242 | 39 / 40 | 1.00 | No |
| `text` | least similar to the others | 18.2 / 22.0 % | 18.6 / 20.9 % | 242 | 29 / 41 | 0.19 | No |

For the `none` case the copilot has no options to work with, so the only choice is a
letter. D is already the most common letter there.

We also looked at the level, the year and the problem number, which are only in the
problem `id` (`lvl-N_year_number`). Train and val do not agree on them. For example,
level 6 has A as its most common answer in train (24.6 %), but in val A drops to 11.7 %
and B rises to 43.3 %. The letter shares by year swing widely (D goes from 0 % to
35 % between train years), so we read them as noise. The test set may also use a different id format. None of these
signals is used.

Whole policy, all figure rows:

| Policy | Train (2,145 rows) | Val (440 rows) | Both (2,585 rows) |
|---|---|---|---|
| **Always D (decision)** | 24.8 % | 25.2 % | 24.9 % |
| Median on `mixed`, D elsewhere | 25.9 % | 27.3 % | 26.1 % |
| Median on `sorted` and `mixed`, D elsewhere (current `copilot/prior.py`) | 25.3 % | 30.2 % | 26.1 % |

The current prior's 30.2 % on val is mostly luck in the `sorted` case: the median
wins there in val (38.8 % against 22.5 %) and loses in train (25.1 % against 28.2 %).

## Decision

Answer **D** on every figure problem:

| What the options look like | What to answer | Why |
|---|---|---|
| The options are figures (OCR found no options) | D | Nothing to compare. D is the most common letter (26.0 %). |
| The options are text or expressions | D | No text heuristic beats D. |
| The options are numbers in value order | D | The median ties with D (27.3 % each). |
| The options are numbers in mixed order | D for now | The median looks better (33 % against 22 %), but p = 0.14. See below. |

**Candidate to reopen:** median value on `mixed` numeric options. It beats D in train
and in val by about 10 points. It is also the only heuristic that matches how Kangaroo
distractors are built (around the right value). With only 113 problems, the test can't
tell a 10-point gain from noise. Reopen it if a new set of labelled figure problems
(for example another M3Kang shard) brings the pooled test to p < 0.05.

**Applied:** `prior()` in `copilot/prior.py` returns the fallback letter
(`FALLBACK_ANSWER`, D) for every problem whose `text_only` is false. Problems without a
`text_only` field, and text-only problems, keep the old rule (median value on numeric
options, D otherwise). This analysis did not measure those.

## Limitations

- The decision rule was written after an exploratory look at the same train and val
  rows. Train and val together are 936 problems. A heuristic that passes the rule here
  still needs new data before we trust it.
- Accuracy depends on OCR. If OCR finds options more often, more rows move out of
  `none`, and the shares above change.
- The 2,145 train rows are the high-quality shard 0 of M3Kang, eng/cat/esp only.
  Other shards or languages may have different answer keys.
- Wilson intervals over rows would be too narrow, because each problem appears up to
  three times. That is why the tests use one row per problem.

## Reproduce

```bash
python3 laptop/prior_txto_no.py
```

It reads `data/train.jsonl` and `data/interim/val_txto_no.jsonl` (both out of Git,
made by `laptop/prepare_m3kang.py` and the split of the
[vision report](2026-11-vision-txto-no.md#reproduce)). It prints only counts and
percentages, never problem text.
