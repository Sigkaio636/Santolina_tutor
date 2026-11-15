# decider-2b-vision: performance record

This page records the performance of decider-2b-vision in this project, with one row per run.
Add a row to the [performance log](#performance-log) after each new run, and link its report.
Each report keeps the design and the limitations of its run. This page keeps only the numbers and the current verdict.

Last updated: 2026-11-15.

## Identity

| | |
|---|---|
| Model | [Mapika/decider-2b-vision](https://huggingface.co/Mapika/decider-2b-vision) |
| What it is | A one-pass decision model. It reads an image and a question with lettered options, and gives a letter. It is not a chat model. |
| Base | Qwen3.5-2B vision-language model, with the text weights of decider-2b **v5** (not the newer v12) |
| Trained on (model card) | Game frames, multiple-choice image tasks from The Cauldron (A-OKVQA, AI2D, ScienceQA, IconQA, TQA, Raven), and text |
| Scores reported by its authors | Raven 0.80, IconQA 0.94, AI2D 0.93, Visual7W 0.89 (held out). No maths diagrams. |
| Languages | English only, by its model card |
| License | Apache-2.0 |
| Code | [github.com/Mapika/decider](https://github.com/Mapika/decider) (`decider/vision/`) |

## Files

From `mradermacher/decider-2b-vision-GGUF`, revision `13555b9be92e1502f7d89d303a8e4e450f3c5b4a`.

| File | Size | SHA256 | Status |
|---|---|---|---|
| `decider-2b-vision.Q8_0.gguf` | 2,012 MB | `11e07e4c6a56856e05ec5b4c98308a8e869607bfaad9e70b94c9a6439c595b9c` | Used in every run below |
| `decider-2b-vision.mmproj-f16.gguf` | 668 MB | `4bbc8f570ad52331cd5594f252db37b5d473d507ef9a3d9b108c024e256dcc18` | Used in every run below |
| `decider-2b-vision.Q4_K_M.gguf` | 1,274 MB | not recorded | Not tested |
| `decider-2b-vision.mmproj-Q8_0.gguf` | 365 MB | not recorded | Not tested |

The files go in `models/`, which Git ignores (`*.gguf`).

## How to run it

- llama.cpp `2cbe0ec` (the commit pinned in `config.env`), `llama-server` with `--mmproj`.
  Server flags as in the [decider-0.8b report](../experiments/2026-11-decider-0.8b.md), plus
  `--image-max-tokens 128` for the board setting.
- Client: `LLM_PROMPT=decider`. `copilot/llm.py` sends decider's plain prompt to
  `/completion`. The image goes **before** the prompt, with no chat template, as in
  `decider/vision/model.py`. The image placeholder comes from the server's `/props`
  (`media_marker`): this llama.cpp build picks a random one. When OCR found no options, the
  prompt lists them as `figure A` to `figure E`.
- Evaluation: `laptop/eval_vision.py`. Use `--no-image` for a blind run on the same server.
- The full commands are in the [experiment report](../experiments/2026-11-decider-2b-vision-figure-logic.md#reproduce).

## Resources

| Measure | Value | Where |
|---|---|---|
| Server RAM (RSS), image at most 128 tokens | 2.71 GB idle, 2.77 GB after one image | Laptop, 2026-11-15, `/proc/<pid>/status` |
| Server RAM (RSS), no image token limit | 2.79 GB idle, peak 2.84 GB | Laptop, 2026-11-15 |
| Prompt tokens per row (median) | 95 blind, 213 with a 128-token image, 600 with no limit | Laptop runs below |
| Time per row, laptop CPU, 4 threads | 3.2 s blind, 8.2 s with a 128-token image, 21.1 s with no limit (worst 45.7 s) | Laptop runs below |
| Time per row on the UNO Q | **Not measured** | — |

RAM measured with `Q8_0`, mmproj `f16` and `--ctx-size 4096`. A fresh board has about 3.1 GiB
available, and the two copilot servers already use about 1.1 GB
([board reference](../UNO_Q_BOARD_REFERENCE.md)). So this setup does not fit next to them.

**Estimate, not measured:** on the board, Qwen3.5-0.8B with a 128-token image takes 28 to 38 s
per row ([BOARD_SETUP.md](../BOARD_SETUP.md)). decider-2b-vision has a language model about 2.5
times larger and a vision tower about 3 times larger, so it would very likely go over the 60 s limit.

## Performance log

Accuracy against the M3Kang `label`, one letter under the grammar `root ::= [A-E]`, temperature 0,
seed 42, 95 % Wilson interval from `laptop/compare_runs.py`. "Floor" is the best score you get by
answering the same letter every time on the same rows. A run is better than guessing only if its
interval lies entirely above the floor.

| Date | Run | Rows | Input | Accuracy | Floor | s/row (laptop) | Report |
|---|---|---|---|---|---|---|---|
| 2026-11-15 | `fl-decider2bv-blind` | 160, figure logic, levels 0–2, eng/cat/esp | no image | 23.8 % [17.8–30.9] | 30.0 % (D) | 3.2 | [figure logic](../experiments/2026-11-decider-2b-vision-figure-logic.md) |
| 2026-11-15 | `fl-decider2bv-img` | same 160 | image, at most 128 tokens | 24.4 % [18.4–31.6] | 30.0 % (D) | 8.2 | [figure logic](../experiments/2026-11-decider-2b-vision-figure-logic.md) |
| 2026-11-15 | `fl-decider2bv-imgfull` | same 160 | image, no token limit | 26.2 % [20.0–33.6] | 30.0 % (D) | 21.1 | [figure logic](../experiments/2026-11-decider-2b-vision-figure-logic.md) |

Paired tests on the same rows (exact McNemar): image (128 tokens) against blind, p = 1.0; image (no token limit)
against blind, p = 0.61.

These runs used commits `474f99c` and `9107889`, plus the changes to `copilot/llm.py` and
`laptop/eval_vision.py` that were not committed yet when they ran. Those changes were committed later in
`5566a4e`.

The reference model on the same 160 rows is Qwen3.5-0.8B: 24.4 % with a 128-token image and 22.5 % blind.
It differs in size, vision tower, training and prompt, so compare it only with care. See the
[report](../experiments/2026-11-decider-2b-vision-figure-logic.md#results).

## Verdict so far

**Not adopted.** On the easiest figure problems, seeing the image does not change its score, at
either image size, and no run reaches the fixed-letter floor. It would also not fit on the board
next to the copilot's servers, and it would very likely go over 60 s per problem.

Reopen if a run on a larger set (for example all 440 figure rows of the validation set) shows an
image gain with p < 0.05, or if a newer decider vision release with v12 or later text weights comes
out with a llama.cpp mmproj.

## How to add a run

1. Run `laptop/eval_vision.py` with a new `--name`, once with the image and once with
   `--no-image` on the same rows.
2. Run `laptop/compare_runs.py <rows.jsonl> blind=<csv> img=<csv>` to get the interval, the floor
   and the McNemar test.
3. Add one row per run to the [performance log](#performance-log), and update
   [Resources](#resources) if you measured something new.
4. Link the report of the run. Write no problem text, ids or images on this page: M3Kang is for
   research use only (see the [dataset card](https://huggingface.co/datasets/qualcomm/M3Kang)).
