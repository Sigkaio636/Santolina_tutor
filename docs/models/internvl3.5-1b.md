# InternVL3.5-1B: model record

This page records InternVL3.5-1B in this project: its files, how to run it, what it
needs, and one row per run. It is for team members who want to run the model again or add
a run. **Verdict: not adopted** ([why](#verdict)).

Each run's report keeps its design and its limitations. This page keeps the numbers and
the verdict.

Last updated: 2026-11-15.

## Identity

| | |
|---|---|
| Model | [OpenGVLab/InternVL3_5-1B](https://huggingface.co/OpenGVLab/InternVL3_5-1B). We used the release without `-HF` in its name, because llama.cpp's converter reads that one. |
| What it is | A chat vision-language model: the InternViT-300M vision tower plus the Qwen3-0.6B language model, about 1.1B parameters in total |
| Scores reported by its authors | MathVista (mini) 59.3, MathVision 27.3, MathVerse (vision-only) 37.8, LogicVista 29.3. Source: [arXiv 2508.18265](https://arxiv.org/html/2508.18265v2), Table 3, the InternVL3.5-1B row without parallel thinking, checked on 2026-11-15. |
| License | Apache-2.0 (model card) |

## Files

We converted the model ourselves from revision `2f71cf52542334823e48a46ffba0e2bc9add3446`,
with llama.cpp `2cbe0ec` (the commit pinned in `config.env`). The `mmproj` file is the
vision projector: llama.cpp needs it to read images.

| File | Size | SHA256 | Status |
|---|---|---|---|
| `InternVL3_5-1B-Q8_0.gguf` | 805 MB | `3af25fcc443426c656500ba63c59cec19a3f3f0ca461ca95f2c147c45e89c1d9` | Used in every run below |
| `mmproj-InternVL3_5-1B-1tile-f16.gguf` | 621 MB | `6521d80c260e89cb714440ff5885d7cda49fe62ac311c2ffbe8e426e7f59f1d3` | Used in every run below. One 448 px tile: about 510 prompt tokens per image |
| `mmproj-InternVL3_5-1B-f16.gguf` | 621 MB | `c24844c7259b39a225c1f733d9e28dce314d90882597e3f3bda8df84d4d5a9e8` | Default config, up to 12 tiles. Smoke test only |

The files go in `models/`, which Git ignores (`*.gguf`).

To make the files again, you need a llama.cpp checkout at `2cbe0ec` (below,
`<llama.cpp>`), with `llama-quantize` built in it as well as `llama-server`. Make a separate
Python environment, not the project's `.venv`: the converter's requirements pin another
version of torch. Install in it
`<llama.cpp>/requirements/requirements-convert_hf_to_gguf.txt`, and run the commands below
with that environment active, from the repository root:

1. Download the model folder:

   ```bash
   hf download OpenGVLab/InternVL3_5-1B --revision 2f71cf52542334823e48a46ffba0e2bc9add3446 \
     --local-dir models/hf-InternVL3_5-1B
   ```

2. Convert the language model, and quantize it to Q8_0:

   ```bash
   python3 <llama.cpp>/convert_hf_to_gguf.py models/hf-InternVL3_5-1B --outtype bf16 \
     --outfile models/InternVL3_5-1B-bf16.gguf
   <llama.cpp>/build/bin/llama-quantize models/InternVL3_5-1B-bf16.gguf \
     models/InternVL3_5-1B-Q8_0.gguf Q8_0
   ```

3. Copy the model folder to `models/ivl-1tile`. In the copy's `config.json`, set
   `"max_dynamic_patch": 1` and `"min_dynamic_patch": 1`. Then make both projectors:

   ```bash
   python3 <llama.cpp>/convert_hf_to_gguf.py models/ivl-1tile --mmproj --outtype f16 \
     --outfile models/mmproj-InternVL3_5-1B-1tile-f16.gguf
   python3 <llama.cpp>/convert_hf_to_gguf.py models/hf-InternVL3_5-1B --mmproj --outtype f16 \
     --outfile models/mmproj-InternVL3_5-1B-f16.gguf
   ```

   The converter writes the folder name into the file, so the copy must be named
   `ivl-1tile` to give our SHA256.

   Check: `sha256sum models/InternVL3_5-1B-Q8_0.gguf models/mmproj-InternVL3_5-1B-*f16.gguf`
   gives the three SHA256 values in the table. If they differ, the conversion is not the
   same as ours.

## How to run it

On the laptop, from the repository root. You need `llama-server` built from llama.cpp
`2cbe0ec`. If you do not have it, build it as in
[the intent router guide](../how-to/use-decider-2b-router.md#before-you-start), and use
the path of that build in step 1.

1. Start the server on port 8083 (`VISION_PORT`):

   ```bash
   llama-server -m models/InternVL3_5-1B-Q8_0.gguf \
     --mmproj models/mmproj-InternVL3_5-1B-1tile-f16.gguf \
     --threads 4 --ctx-size 4096 --parallel 1 --cache-ram 0 --ctx-checkpoints 2 \
     --jinja --reasoning off --reasoning-budget 0 --host 127.0.0.1 --port 8083
   ```

   `--image-max-tokens` does **not** limit InternVL in this llama.cpp build. To limit the
   image, use the one-tile projector.

   Check:
   - The same binary with `--version` names commit `2cbe0ec`.
   - `curl -s http://127.0.0.1:8083/health` prints `{"status":"ok"}`.

2. In a second terminal, run the evaluation on a rows file, with `SOLVER=letter`. Do not
   set `LLM_PROMPT`: InternVL uses the copilot's default chat prompt (`copilot/llm.py`).

   ```bash
   SOLVER=letter .venv/bin/python laptop/eval_vision.py \
     --input <rows.jsonl> --languages eng,cat,esp --name <run-name>
   ```

   Add `--no-image` for a blind run on the same server. The rows file of the runs below,
   `data/interim/txto_no_s175.jsonl`, comes from `laptop/sample_txto_no.py --n 175` (see the
   [run log](#run-log)). `eval_vision.py` reads the images from the figure-rows parquet that
   `laptop/split_text_only.py` writes. Its `--parquet` option names the file. The default
   is the first of the four parquet files. These files stay in `data/`,
   out of Git.

   Check:
   - Each progress line shows more than 0 tokens. 0 tokens means that no model answered
     that row.
   - The `Status:` line at the end shows only `ok`. A failed or timed-out call gives the
     letter D, with the status `error` or `timeout`.

   If every row has 0 tokens and the status `ok`, the run measured the
   [prior solver](https://github.com/Sigkaio636/Santolina_tutor/blob/main/GLOSSARY.md)
   (`SOLVER=prior`, the default in `config.env`), not this model. With `SOLVER=letter`,
   the copilot calls the model for every row. The logs do not record `SOLVER` or
   `LLM_PROMPT`.

## Resources

| Measure | Value | Where |
|---|---|---|
| Server resident memory (RSS), one-tile projector | 1.68 GB after the image run | Laptop, 2026-11-15 |
| New prompt tokens per row (llama-server `prompt_n`, without the cached system prompt) | 543 to 691 with one tile, about 1,400 with the default projector | Laptop runs below and smoke test |
| Prompt tokens for one image, one tile | About 510: image run minus blind run, on the rows with the same text | [Run log](#run-log) |
| Time per row, laptop CPU, 4 threads (mean) | Image, one tile: 6.9 s. Blind: 0.3 s | [Run log](#run-log) |
| Time per row on the UNO Q | **Not measured** | — |

Other jobs were running on the laptop during the runs (load average about 4), so read the
times as a guide only.

**Estimate, not measured:** on the board, Qwen3.5-0.8B with a 128-token image took 28 to
38 s per row, on two problems
([BOARD_SETUP.md](../BOARD_SETUP.md#let-the-model-see-the-image-experiment)). On the laptop,
the same setting took 2.0 s per row
([report](../experiments/2026-11-vision-txto-no.md)), so the board was about 14 to 19 times
slower. InternVL took 6.9 s per row on the laptop. At the same ratio it would take about
100 to 130 s per row on the board. So it would very likely go over the limit of 60 s per problem (`TIME_LIMIT_SECONDS` in
`config.env`). Its projector file is also larger: 621 MB in f16, against 205 MB for
Qwen3.5-0.8B's.

## Verdict

**Not adopted.**

- With the image, its whole interval lies below the fixed-letter floor (25.1 %, always D).
  Against always D on the same rows, the paired test gives 26 / 40, p = 0.11: the run does
  not show that it is worse than D, only that it is not better.
- The image has no effect on accuracy that the run can detect. On 175 rows, the run cannot
  rule out a difference of about 10 points. The image does change the answers: it moves
  them from A to E.
- It almost never answers B or C: with the image, 2 B and 1 C in 175 rows, where 79 of the
  right answers are B or C.
- It would very likely go over 60 s per problem on the board.

## Run log

Each run asks for one letter, A to E: a grammar (`root ::= [A-E]`) allows no other reply.
Temperature 0, seed 42. "Accuracy" counts the rows where the letter matches M3Kang's answer
(`label`). The interval is a 95 % Wilson interval from `laptop/compare_runs.py`. The
"floor" is the score of the best fixed letter: the highest value on the `floors:` line of
`compare_runs.py`. A run is above the floor only if its whole interval lies above it.

A [row](https://github.com/Sigkaio636/Santolina_tutor/blob/main/GLOSSARY.md) is one problem
in one language (English, Catalan, Spanish). The three languages of one problem are not
independent, so the intervals and the p-values below are narrower and smaller than the
data supports. Read them as a guide only.

| Date | Run | Commit | Rows | Input | Accuracy | Floor | s/row (laptop) | Report |
|---|---|---|---|---|---|---|---|---|
| 2026-11-15 | `txno-ivl-img` | `401a20a` | 175: a stratified sample of the 440 figure rows of the validation set | image, one tile | 17.1 % [12.3–23.4] | 25.1 % (D) | 6.9 | [InternVL3.5-1B vs decider](../experiments/2026-11-internvl35-1b-vs-decider-2b-vision-txto-no.md) |
| 2026-11-15 | `txno-ivl-blind` | `401a20a` | same 175 | no image | 19.4 % [14.2–25.9] | 25.1 % (D) | 0.3 | [InternVL3.5-1B vs decider](../experiments/2026-11-internvl35-1b-vs-decider-2b-vision-txto-no.md) |

- A figure row is a row that is not a
  [text-only row](https://github.com/Sigkaio636/Santolina_tutor/blob/main/GLOSSARY.md).
- `laptop/sample_txto_no.py --n 175` draws the sample from `data/interim/val_txto_no.jsonl`
  with seed 42. No script in this repository writes that file: the
  [txto_no report](../experiments/2026-11-vision-txto-no.md) defines it as the figure rows
  of the validation split in English, Catalan and Spanish. The sample is drawn in proportion
  to each group of language and OCR result. In these rows, OCR found either all five
  options (89 rows) or none (86 rows).
- The report calls the runs `ivl-img` and `ivl-blind`.
- decider-2b-vision ran on the same 175 rows: see its
  [model record](decider-2b-vision.md#run-log).

The paired test on the same rows uses the exact McNemar test. "a / b" counts the rows that
only the image run got right, then the rows that only the blind run got right. Image
against blind: 15 / 19 rows, p = 0.61.

The two runs differ in two ways, not one. In the 86 rows where OCR found no options, the
prompt also changes. The image run's prompt says that the options are in the picture. The
blind run's prompt says that the model cannot see the picture. In the 89 rows with five
options, the prompt is the same, and image against blind gives 8 / 9 rows, p = 1.0 (the
`figure, 5 options` block of `compare_runs.py`).

## How to add a run

1. Commit every change to tracked files first, `config.env` included: the logs record the
   commit, not uncommitted changes. The log reads the commit at the end of the run, so do
   not commit while a run is going. Then run the model as in [How to run it](#how-to-run-it), with a
   new `--name`: once with the image and once with `--no-image`, on the same rows.
   Check: `results/ablations.csv` ends with one line for each run, with your names.
2. Compare the two runs. Put the image run first:

   ```bash
   .venv/bin/python laptop/compare_runs.py <rows.jsonl> \
     img=results/eval-<time>-<img-name>.csv blind=results/eval-<time>-<blind-name>.csv
   ```

   `<rows.jsonl>` is the `--input` file of step 1. It must hold only the rows of the runs.
   `eval_vision.py` writes one CSV per run, `results/eval-<time>-<name>.csv`.
   Check: the first block, which starts with `== all`, gives the number of rows of your
   runs, the floors, the interval of each run and the McNemar test. If a row of the file is
   not in a CSV, the script stops with `validation rows missing`.
3. Add one row per run to the [run log](#run-log), with its commit. If a setting differs
   from [How to run it](#how-to-run-it), write it in the Input column. Update
   [Resources](#resources) if you measured something new.
4. Link the report of the run. Write no problem text, ids or images on this page: M3Kang is
   for research use only (see the
   [dataset card](https://huggingface.co/datasets/qualcomm/M3Kang)).
