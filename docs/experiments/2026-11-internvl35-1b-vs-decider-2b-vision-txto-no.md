# Experiment: InternVL3.5-1B against decider-2b-vision on figure problems

This report records whether InternVL3.5-1B, the only vision model of about 1B with a
published MathVision score and llama.cpp support that we found, picks the right letter
on Kangaroo figure problems better than decider-2b-vision. It is for the team and the
datathon judges. Laptop run, 2026-11-15, branch `exp/decider-0.8b`, commit `401a20a`.

The task: pick the right letter (A–E) for multiple-choice maths problems from the
Kangaroo competition ([M3Kang](https://huggingface.co/datasets/qualcomm/M3Kang)). This
report uses only problems that come with a figure (`text_only` false, "txto_no").

## Summary

- **Decision: InternVL3.5-1B is not adopted.** With the image it gets 17.1 %
  [12.3–23.4] on 175 rows, below always answering D (25.1 %). The image does not help
  it: 19.4 % without the image, exact McNemar p = 0.61.
- **decider-2b-vision is not better than the text baseline either.** It gets 22.3 %
  [16.8–29.0], against 21.1 % for the text-only copilot (p = 0.90). The difference with
  InternVL (5.2 points) is not significant (p = 0.33).
- **The best answer on these rows needs no model.** The letter prior
  (`copilot/prior.py`, `SOLVER=prior`, no `data/prior.json`) gets 29.1 % [22.9–36.3].
  It is significantly better than InternVL with the image (p = 0.022). It is not
  significantly better than decider (p = 0.13) or the text baseline (p = 0.14).
- **InternVL follows letters, not figures.** With the image it answers A 88 times and
  E 63 times (true counts 29 and 23), and B and C three times in total (true 79).
  Without the image it answers A 131 times.

## Why we tried it

Two earlier runs showed that the image does not help a small model on figure problems:
Qwen3.5-0.8B ([txto_no report](2026-11-vision-txto-no.md)) and decider-2b-vision
([figure logic report](2026-11-decider-2b-vision-figure-logic.md)). The decider report
set a condition to reopen the question: a vision model of about 1B, with a llama.cpp
mmproj, that scores well above chance on a diagram-maths benchmark.
InternVL3.5-1B is the closest match we found. Its paper reports MathVision 27.3,
MathVerse (vision-only) 37.8 and LogicVista 29.3
([arXiv 2508.18265](https://arxiv.org/html/2508.18265v2), Table 3; we read these
numbers through a summary and did not check them in the table). llama.cpp `2cbe0ec`
has its converter (`conversion/internvl.py`) and its vision graph
(`tools/mtmd/models/internvl.cpp`).

## What we compared

**Rows.** A stratified sample of 175 of the 440 figure rows of the validation split
(`data/interim/val_txto_no.jsonl`, eng/cat/esp). `laptop/sample_txto_no.py --n 175`
draws it by language × "OCR found the five options", proportionally, seed 42:

| Language | Options found | Population | Sample |
|---|---|---|---|
| cat | no | 77 | 31 |
| cat | yes | 81 | 32 |
| eng | no | 77 | 30 |
| eng | yes | 81 | 32 |
| esp | no | 62 | 25 |
| esp | yes | 62 | 25 |
| **total** | | **440** | **175** |

The size comes from a budget of 40 minutes for the runs (smoke test: 3.3 s per row for
decider, 7.1 s for InternVL with the image, 0.3 s blind). The runs took 30.5 min.

**Runs.** Laptop CPU, llama.cpp `2cbe0ec`, 4 threads, one server at a time, the same
server flags as the earlier reports, one letter under the grammar `root ::= [A-E]`,
temperature 0, seed 42. `SOLVER=letter` for the model runs, so the model is always
called. If a call fails, the prior gives the letter. No call failed or timed out.

| Run | Model | Image | Prompt |
|---|---|---|---|
| `dec-img` | decider-2b-vision Q8_0 + mmproj f16 | yes, `--image-max-tokens 128` (as on the board) | decider plain layout, image first |
| `ivl-img` | InternVL3.5-1B Q8_0 + mmproj f16 (1 tile) | yes, one 448 px tile (256 image tokens) | copilot chat prompt |
| `ivl-blind` | the same | no | copilot chat prompt |
| `prior` | no model | no | — |
| `baseline` | Qwen3.5-0.8B (existing `laptop-baseline` run) | no | copilot chat prompt |

**The InternVL image cap.** `--image-max-tokens` does not limit InternVL in this
llama.cpp build. By default the projector cuts the image into up to 12 tiles of 448 px.
In the first smoke test, prompts were about 1,400 tokens and took about 50 s per row on a
busy laptop. So we converted the projector a second time with `max_dynamic_patch: 1` in
the model config: one tile, 256 image tokens, prompts of 560 to 690 tokens. That is
close to the 128-token setting used for decider and Qwen on the board.

**Weights.** InternVL3.5-1B from `OpenGVLab/InternVL3_5-1B` (the non-`-HF` release),
revision `2f71cf52542334823e48a46ffba0e2bc9add3446`, converted with
`convert_hf_to_gguf.py` at `2cbe0ec` (bf16, then `llama-quantize` Q8_0). SHA256 of
`InternVL3_5-1B-Q8_0.gguf`:
`3af25fcc443426c656500ba63c59cec19a3f3f0ca461ca95f2c147c45e89c1d9`. SHA256 of
`mmproj-InternVL3_5-1B-1tile-f16.gguf`:
`6521d80c260e89cb714440ff5885d7cda49fe62ac311c2ffbe8e426e7f59f1d3`. decider-2b-vision
files as in its [model record](../models/decider-2b-vision.md#files).

## Decision rule (fixed before the run)

InternVL3.5-1B goes on to a board test only if both hold:

1. The lower end of its 95 % Wilson interval is above the best one-letter floor of
   the 175 rows.
2. It beats `ivl-blind` or the text baseline with an exact McNemar p < 0.05 (the image
   adds something).

The comparison with decider is reported either way, but it does not decide on its own.

## Results

Accuracy with a 95 % Wilson interval, from `laptop/compare_runs.py`. Best one-letter
floor on the 175 rows: always D, 25.1 %.

| Run | All (n = 175) | eng (62) | cat (63) | esp (50) | 5 OCR options (89) | No options (86) | s per row | Server RSS |
|---|---|---|---|---|---|---|---|---|
| `dec-img` | 22.3 % [16.8–29.0] | 29.0 % | 17.5 % | 20.0 % | 25.8 % | 18.6 % | 3.2 | 2.86 GB |
| `ivl-img` | 17.1 % [12.3–23.4] | 11.3 % | 22.2 % | 18.0 % | 21.3 % | 12.8 % | 6.9 | 1.68 GB |
| `ivl-blind` | 19.4 % [14.2–25.9] | 22.6 % | 19.0 % | 16.0 % | 22.5 % | 16.3 % | 0.3 | (same server) |
| `baseline` | 21.1 % [15.7–27.8] | 21.0 % | 22.2 % | 20.0 % | 21.3 % | 20.9 % | — | — |
| `prior` | **29.1 %** [22.9–36.3] | 35.5 % | 28.6 % | 22.0 % | 29.2 % | 29.1 % | 0.0 | none |

The groups by language and by options are small (50 to 89 rows). Read their
differences as noise unless a test says otherwise.

**Paired tests (exact McNemar, 175 rows).** "a / b" counts the rows only the first run
got right, then the rows only the second got right.

| Comparison | a / b | p |
|---|---|---|
| `ivl-img` vs `dec-img` | 29 / 38 | 0.328 |
| `ivl-img` vs `ivl-blind` | 15 / 19 | 0.608 |
| `ivl-img` vs `baseline` | 22 / 29 | 0.401 |
| `ivl-img` vs `prior` | 28 / 49 | **0.022** |
| `dec-img` vs `baseline` | 32 / 30 | 0.899 |
| `dec-img` vs `prior` | 20 / 32 | 0.126 |
| `prior` vs `baseline` | 45 / 31 | 0.135 |

In English, InternVL with the image is worse than decider (7 / 18, p = 0.043) and worse
than without its image (1 / 8, p = 0.039). We looked at these groups after the run, and
we ran many tests, so treat them as a lead at most.

**How the answers spread** (answered, out of 175; true counts A 29, B 39, C 40, D 44,
E 23):

| Run | A | B | C | D | E |
|---|---|---|---|---|---|
| `dec-img` | 9 | 42 | 34 | 50 | 40 |
| `ivl-img` | 88 | 2 | 1 | 21 | 63 |
| `ivl-blind` | 131 | 4 | 0 | 37 | 3 |
| `prior` | 0 | 7 | 34 | 131 | 3 |

InternVL almost never answers B or C, which are 45 % of the true answers. The image moves
part of its answers from A to E. The same pattern showed up with Qwen3.5-0.8B: the image
changes the default letter, and the model does not read the figure. decider spreads its
answers like the true labels, but it is not right more often. The prior answers D when
it has no numeric options (every row without OCR options) and the median value
otherwise.

## Decision

**Not adopted. The copilot stays text-only for figure problems.**

1. Floor: fails. 17.1 % is below 25.1 %, and the whole interval lies below it.
2. The image adds something: fails. Against `ivl-blind` p = 0.61, against the text
   baseline p = 0.40. Both point the wrong way.

Board test: not run. The rule fails on the laptop. It would also be slow: InternVL's
vision tower (InternViT-300M, 621 MB in f16) is about three times Qwen3.5-0.8B's
(205 MB). Qwen takes 28 to 38 s per row on the board with a 128-token image
([BOARD_SETUP.md](../BOARD_SETUP.md)), so InternVL with a 256-token tile would very
likely take over 60 s. This is an estimate, not a measurement.

**What this adds.** On figure rows, the letter prior is the strongest answer we have
measured, with no model call: 29.1 %, against 17 to 22 % for the three vision runs and
the text baseline. It is not yet significantly better than decider or the text baseline
on 175 rows. It should be measured on all 440 figure rows before the pipeline relies on
it.

## Limitations

- **175 rows.** The McNemar test can only see differences of about 10 points or more.
  A real gap of 5 points between decider and InternVL could go unseen.
- **Different prompts.** decider uses its own plain layout, and InternVL uses the
  copilot's chat prompt. Neither prompt was tuned.
- **InternVL at one tile.** We capped InternVL at one 448 px tile, so it can run on the
  board. Its authors use dynamic tiling (up to 12 tiles). A full-resolution run might
  do better, but it could not run on the board in time.
- **Laptop CPU only**, and the laptop was not fully idle: the load was about 4 during
  the runs. Times are a guide only.
- **llama.cpp, not the authors' code.** We did not compare InternVL's answers in
  llama.cpp with its reference implementation.
- **The baseline run is from 2026-11-14** (Qwen3.5-0.8B, text only), restricted to the
  same 175 rows. It is the same run as in the [txto_no report](2026-11-vision-txto-no.md).

## Reproduce

```bash
python3 laptop/sample_txto_no.py --n 175
```

InternVL3.5-1B, converted with llama.cpp `2cbe0ec`. For the one-tile projector, copy
the model folder and set `"max_dynamic_patch": 1` and `"min_dynamic_patch": 1` in its
`config.json` before you convert it with `--mmproj`.
`convert_hf_to_gguf.py` needs `sentencepiece` for this model.

```bash
python3 convert_hf_to_gguf.py models/hf-InternVL3_5-1B --outtype bf16 \
  --outfile models/InternVL3_5-1B-bf16.gguf
llama-quantize models/InternVL3_5-1B-bf16.gguf models/InternVL3_5-1B-Q8_0.gguf Q8_0
python3 convert_hf_to_gguf.py <copy-with-1-tile-config> --mmproj --outtype f16 \
  --outfile models/mmproj-InternVL3_5-1B-1tile-f16.gguf
```

Servers on port 8083, one at a time, with the flags of the
[decider report](2026-11-decider-2b-vision-figure-logic.md#reproduce) (decider adds
`--image-max-tokens 128`). Then:

```bash
LLM_PROMPT=decider SOLVER=letter python3 laptop/eval_vision.py \
  --input data/interim/txto_no_s175.jsonl --name txno-dec-img128
SOLVER=letter python3 laptop/eval_vision.py --input data/interim/txto_no_s175.jsonl --name txno-ivl-img
SOLVER=letter python3 laptop/eval_vision.py --input data/interim/txto_no_s175.jsonl --no-image --name txno-ivl-blind
python3 laptop/eval_vision.py --input data/interim/txto_no_s175.jsonl --no-image --name txno-prior
python3 laptop/compare_runs.py data/interim/txto_no_s175.jsonl ivl_img=<csv> dec_img=<csv> \
  ivl_blind=<csv> baseline=results/eval-<time>-laptop-baseline.csv prior=<csv>
```

`data/interim/` and `results/` stay out of Git (M3Kang rule).
