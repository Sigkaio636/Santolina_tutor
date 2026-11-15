# InternVL3.5-1B: performance record

This page records the performance of InternVL3.5-1B in this project, with one row per run.
Add a row to the [performance log](#performance-log) after each new run, and link its report.
Each report keeps the design and the limitations of its run. This page keeps only the numbers and the current verdict.

Last updated: 2026-11-15.

## Identity

| | |
|---|---|
| Model | [OpenGVLab/InternVL3_5-1B](https://huggingface.co/OpenGVLab/InternVL3_5-1B) (the non-`-HF` release, which llama.cpp's converter reads) |
| What it is | A chat vision-language model: InternViT-300M vision tower plus a Qwen3-0.6B language model, about 1.1B parameters in total |
| Scores reported by its authors | MathVista 59.3, MathVision 27.3, MathVerse (vision-only) 37.8, LogicVista 29.3 ([arXiv 2508.18265](https://arxiv.org/html/2508.18265v2), Table 3; read through a summary, not checked in the table) |
| License | Apache-2.0 (model card) |

## Files

Converted by us from revision `2f71cf52542334823e48a46ffba0e2bc9add3446` with llama.cpp `2cbe0ec`
(`convert_hf_to_gguf.py`, then `llama-quantize`). The converter needs `sentencepiece` for this model.

| File | Size | SHA256 | Status |
|---|---|---|---|
| `InternVL3_5-1B-Q8_0.gguf` | 805 MB | `3af25fcc443426c656500ba63c59cec19a3f3f0ca461ca95f2c147c45e89c1d9` | Used in every run below |
| `mmproj-InternVL3_5-1B-1tile-f16.gguf` | 621 MB | `6521d80c260e89cb714440ff5885d7cda49fe62ac311c2ffbe8e426e7f59f1d3` | Used in every run below. Converted with `max_dynamic_patch: 1` (one 448 px tile, 256 image tokens) |
| `mmproj-InternVL3_5-1B-f16.gguf` | 621 MB | `c24844c7259b39a225c1f733d9e28dce314d90882597e3f3bda8df84d4d5a9e8` | Default config, up to 12 tiles. Smoke test only: about 1,400 prompt tokens per row |

The files go in `models/`, which Git ignores (`*.gguf`).

## How to run it

- `llama-server` with `--mmproj`, same flags as the [decider report](../experiments/2026-11-decider-2b-vision-figure-logic.md#reproduce).
  `--image-max-tokens` does **not** limit InternVL in this llama.cpp build. To cap the image, use the one-tile projector.
- Client: the copilot's default chat prompt (`copilot/llm.py`), with `SOLVER=letter` so the model is always called.
- Evaluation: `laptop/eval_vision.py`. Use `--no-image` for a blind run on the same server.

## Resources

| Measure | Value | Where |
|---|---|---|
| Server RAM (RSS), one-tile projector | 1.68 GB after the image run | Laptop, 2026-11-15 |
| Prompt tokens per row | 560–690 with one tile, about 1,400 with the default projector | Laptop runs below |
| Time per row, laptop CPU, 4 threads | 6.9 s with one tile, 0.3 s blind | Laptop runs below |
| Time per row on the UNO Q | **Not measured.** Estimated above 60 s: its vision tower is about three times Qwen3.5-0.8B's | — |

## Performance log

Accuracy against the M3Kang `label`, one letter under the grammar `root ::= [A-E]`, temperature 0,
seed 42, 95 % Wilson interval from `laptop/compare_runs.py`. "Floor" is the best score you get by
answering the same letter every time on the same rows.

| Date | Run | Rows | Input | Accuracy | Floor | s/row (laptop) | Report |
|---|---|---|---|---|---|---|---|
| 2026-11-15 | `txno-ivl-img` | 175, stratified sample of the 440 figure rows, eng/cat/esp | image, one tile | 17.1 % [12.3–23.4] | 25.1 % (D) | 6.9 | [InternVL3.5-1B vs decider](../experiments/2026-11-internvl35-1b-vs-decider-2b-vision-txto-no.md) |
| 2026-11-15 | `txno-ivl-blind` | same 175 | no image | 19.4 % [14.2–25.9] | 25.1 % (D) | 0.3 | [InternVL3.5-1B vs decider](../experiments/2026-11-internvl35-1b-vs-decider-2b-vision-txto-no.md) |

Paired test (exact McNemar): image against blind, 15 / 19 rows, p = 0.61.

## Verdict so far

**Not adopted.** With the image it scores below the fixed-letter floor, and the image does not help it.
It almost never answers B or C. It would also very likely go over 60 s per problem on the board.

Write no problem text, ids or images on this page: M3Kang is for research use only (see the
[dataset card](https://huggingface.co/datasets/qualcomm/M3Kang)).
