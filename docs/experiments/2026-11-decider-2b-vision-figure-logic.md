# Experiment: decider-2b-vision on simple figure logic problems

This report records whether a small vision model that sees the problem image does
better than the same model without it, on the easiest kind of Kangaroo figure
problem. It is for the team and the datathon judges. Laptop run, 2026-11-15, branch
`exp/decider-0.8b`.

The task: pick the right letter (A–E) for multiple-choice maths problems from the
Kangaroo competition ([M3Kang](https://huggingface.co/datasets/qualcomm/M3Kang)). This
report uses only problems whose question needs a figure (`text_only` false in M3Kang).

## Summary

- **Decision: no vision model is adopted.** Seeing the image does not change the score.
  decider-2b-vision gets 24.4 % with the image (at most about 128 image tokens) and
  23.8 % without it, on the same 160 rows. Exact McNemar: p = 1.0. Qwen3.5-0.8B gets
  24.4 % with the image and 22.5 % without it.
- **No run reaches the fixed-letter floor.** Answering D every time gets 30.0 % on
  this subset. Every run is below it, and every 95 % interval contains it.
- **The image size does not explain it.** With no image token limit (median 600 prompt
  tokens against 213), decider-2b-vision gets 26.2 %: 19 rows right only with the image, 15 only
  without it, p = 0.61. It also takes 21 s per row on the laptop, against 8 s.
- **This was the most favourable case we could build.** Low levels (0–2), logic and
  spatial problems only, and a model trained on similar image tasks (Raven, IconQA,
  AI2D). If vision does not help here, it is unlikely to help on harder figure problems
  on the board, where it would also cost RAM and most of the 60 s budget.

## Why we tried it

More than half of the M3Kang rows need a figure (440 of 789 in our validation set), and
the copilot is text-only, so it guesses on them
([decider-0.8b report](2026-11-decider-0.8b.md#the-ocr-limitation)).
[Mapika/decider-2b-vision](https://huggingface.co/Mapika/decider-2b-vision) is a
one-pass decision model built from the Qwen3.5-2B vision-language model. Its model card
reports 0.80 on Raven (abstract figure puzzles), 0.94 on IconQA and 0.93 on AI2D
(diagrams). These are close to the simplest Kangaroo figure problems, so we tested it there
first. It is English-only by its model card.

## What we compared

**Subset.** From the English figure rows of levels 0–2 in `data/train.jsonl` and
`data/val.jsonl` (292 problems; decider was never trained on M3Kang, so the training
split is fair to use), shuffled with seed 42, Claude, the coding agent of this project,
looked at each image in that order. It marked each one `logic` (patterns, sequences,
counting, spatial views, folding, paths, puzzles) or `other` (geometry with measures,
arithmetic drawn as a picture), and stopped at 60 logic problems. That took 84 problems.
**No person checked these labels.** The same 60 problems were then taken in Catalan (60
rows) and Spanish (40 rows): 160 rows. 25 of the 60 problems are level 0, 14 level 1 and
21 level 2. OCR read all five options as text in 60 of the 160 rows. In the others, the
options are only in the image. The ids stay in `data/interim/` (not in Git).

**Runs.** All on the laptop CPU, llama.cpp `2cbe0ec`, one letter under the grammar
`root ::= [A-E]`, temperature 0, seed 42.

| Run | Model | Image | Prompt |
|---|---|---|---|
| dec-blind | decider-2b-vision Q8_0 | no | decider plain layout |
| dec-img128 | decider-2b-vision Q8_0 + mmproj f16 | yes, `--image-max-tokens 128` (as on the board) | decider plain layout, image first |
| dec-imgfull | the same | yes, no token limit | the same |
| qwen-img | Qwen3.5-0.8B Q8_0 + mmproj f16 | yes, `--image-max-tokens 128` | chat |
| qwen-blind | the same | no | chat |

decider puts the image before its plain text prompt, with no chat template
(`decider/vision/model.py` in its repository). We send it the same way to llama.cpp's
`/completion`. When the options are missing from the text, the prompt lists them as
`figure A` to `figure E`, as decider's own Raven training data does.

Weights: `mradermacher/decider-2b-vision-GGUF`, revision
`13555b9be92e1502f7d89d303a8e4e450f3c5b4a`. SHA256 of `decider-2b-vision.Q8_0.gguf`:
`11e07e4c6a56856e05ec5b4c98308a8e869607bfaad9e70b94c9a6439c595b9c`. SHA256 of
`decider-2b-vision.mmproj-f16.gguf`:
`4bbc8f570ad52331cd5594f252db37b5d473d507ef9a3d9b108c024e256dcc18`. These GGUFs carry
the text weights of decider-2b **v5**, not the newer v12.

## Results

Accuracy with a 95 % Wilson interval, from `laptop/compare_runs.py`. Floor: always D,
30.0 % over all rows.

| Run | All (n = 160) | English (60) | Catalan (60) | Spanish (40) | Mean prompt tokens | Mean s per row |
|---|---|---|---|---|---|---|
| dec-blind | 23.8 % [17.8–30.9] | 21.7 % | 25.0 % | 25.0 % | 95 (median) | 3.2 |
| dec-img128 | 24.4 % [18.4–31.6] | 25.0 % | 20.0 % | 30.0 % | 213 (median) | 8.2 |
| dec-imgfull | 26.2 % [20.0–33.6] | 23.3 % | 28.3 % | 27.5 % | 600 (median) | 21.1 |
| qwen-img | 24.4 % [18.4–31.6] | 18.3 % | 31.7 % | 22.5 % | 196 (median) | 1.4 |
| qwen-blind | 22.5 % [16.7–29.6] | 20.0 % | 23.3 % | 25.0 % | 87 (median) | 0.5 |

The per-language groups are small: no difference between them is significant.

**Image against no image, same model (exact McNemar).** decider: 18 rows right only with
the image, 17 only without it, p = 1.0. In the rows where the options are only in the image
(n = 100), 23 % with the image against 24 % without it.

With no image token limit, the rows where OCR read the five options (n = 60) show the
largest gap in this report: 31.7 % with the image against 23.3 % without it, with 7 rows
right only with the image and 2 only without it (p = 0.18). This is not significant. We
looked at this group after the run and did not plan it, so treat it as a lead at most.
In the rows with no options, the result is 23 % with or without the image.

**How the answers spread.** With the image, Qwen3.5-0.8B answers E in 105 of 160 rows.
Without it, it answers B in 83. The image moves its default letter but does not make it read the
figure. decider spreads its answers more evenly (with the image: A 12, B 35, C 32, D 47,
E 34), but it is not more often right.

**By level.** decider with the image: 10/67 at level 0, 19/38 at level 1, 10/55 at
level 2. Without it: 12/67, 14/38, 12/55. The level 1 gain is 5 rows out of 38, from a single run.
We did not test it, and the problems are not the same across levels.

## Limitations

- **One labeller, not checked.** The `logic` labels are Claude's. A different person
  could draw the line between logic and geometry elsewhere.
- **Small sample.** 60 problems, 160 rows. A real gain of 5 to 10 points could go
  unseen. The test can rule out a large effect, not a small one.
- **Laptop CPU only.** No board timing. On the board, Qwen3.5-0.8B with a 128-token image
  takes 28 to 38 s ([BOARD_SETUP.md](../BOARD_SETUP.md)). decider-2b-vision is about 2.5
  times larger and has a vision tower about three times larger (668 MB against 205 MB),
  so it would very likely go over 60 s on the board.
- **llama.cpp, not the authors' code.** decider's model card uses its own Python
  readout on a GPU. We use llama.cpp's one-token grammar, which picks the same top letter if
  the conversion is faithful. We did not compare the two.
- **Old text weights.** The vision GGUF uses decider-2b v5. The newer v12 sees images only
  through the authors' Python library.

## Decision and what would reopen it

Do not spend board RAM or time on a vision model of this size for figure problems. The
text-only copilot loses nothing measurable by not seeing them.

We would reopen it if:

- a vision model of at most about 1B parameters, with a llama.cpp mmproj, reports a
  score on a diagram-maths benchmark (MathVerse, MathVision) well above chance, or
- a run on a larger subset (all 440 figure rows of the validation set) shows an image
  gain with p < 0.05.

## Reproduce

```bash
# server (llama.cpp 2cbe0ec), image-128 run; drop --image-max-tokens for dec-imgfull
llama-server -m models/decider-2b-vision.Q8_0.gguf \
  --mmproj models/decider-2b-vision.mmproj-f16.gguf --image-max-tokens 128 \
  --threads 4 --ctx-size 4096 --parallel 1 --cache-ram 0 --ctx-checkpoints 2 \
  --jinja --reasoning off --reasoning-budget 0 --host 127.0.0.1 --port 8083
```

```bash
LLM_PROMPT=decider .venv/bin/python laptop/eval_vision.py \
  --input data/interim/figure_logic.jsonl --ids data/interim/figure_logic_ids.json \
  --languages eng,cat,esp --name fl-decider2bv-img
```

Add `--no-image` for the blind runs, and leave out `LLM_PROMPT=decider` for Qwen3.5-0.8B.
`data/interim/` and `results/` stay out of Git (M3Kang rule).
