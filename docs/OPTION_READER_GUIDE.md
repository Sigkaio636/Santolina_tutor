# How to read the answer options with the label-anchored reader

This guide shows how to set up and run the new option reader on the laptop: it reads the five
answer options (A to E) of an M3Kang problem image. It is for team members who already run the
scripts in `laptop/`. Why this reader was chosen, and how well it reads, is in the
[experiment report](experiments/2026-11-option-boxes-intermediate-rec.md).

[M3Kang](https://huggingface.co/datasets/qualcomm/M3Kang) is research-use only. Every file this
guide makes stays under `data/`, which Git ignores. The example values below are made up.

## What you get

For one image, the reader returns the five option values as text. It finds the labels `A)` to
`E)` with OpenCV, cuts out the value of each option, and reads it with a small text recognizer
(`PP-OCRv6_rec_small`, run with ONNX Runtime on the CPU). It writes a stacked fraction as `3/4`,
`(p+3q)/4`, and an exponent as `x^2`.

Two scripts make up the reader:

| Script | What it does |
|---|---|
| `laptop/option_boxes.py` | Finds the labels and gives every ink blob to one option (arm B1) |
| `laptop/option_rec.py` | Reads each value with the recognizer, after splitting fractions and exponents (mode `2d`) |

The reader is not in `laptop/prepare_m3kang.py` yet, and it does not run on the UNO Q:
`predict.py` gets no image.

## Before you start

Run every command from the repository root, with the project environment:

```bash
uv sync
```

This installs `opencv-python-headless` and `onnxruntime`. `scipy` comes with `scikit-learn`.
`uv sync` removes the packages of dependency groups you leave out: if you use the MinerU tools,
run `uv sync --group ocr` instead.

The reader needs files that earlier steps of the project make. Check that you have them:

| File | Made by | Needed for |
|---|---|---|
| `data/raw_txto_yes/*.parquet` | `laptop/split_text_only.py` | every command |
| `data/external/ocr_models/*.onnx` | [Get the recognizers](#get-the-recognizers) | reading |
| `data/interim/ocr_boxes_txto_yes_v5.jsonl` | `laptop/ocr_boxes.py dump --engine v5` (GPU, `ocr-v5` environment) | `pick`, `templates`, `score` |
| `data/interim/ocr_boxes_txto_yes.jsonl` | `laptop/ocr_boxes.py dump --engine v4` | `pick`, `score` |
| `data/interim/optx/options_gold3.json` | `laptop/option_consensus.py gold3-pick`, then options typed in by hand | `pick`, `score` |
| `data/interim/optrec/sample.json` | `option_boxes.py pick` | `templates`, `run` without `--all`, `score` |
| `data/interim/optrec/label_templates.npz` | `option_boxes.py templates` | reading |
| `data/interim/option_crops/manifest.jsonl`, `data/interim/ocr_boxes_crops_v5.jsonl` | the notebook and `laptop/ocr_crops.py` of the [OpenCV crops experiment](experiments/2026-11-option-crops-opencv.md#appendix-reproducibility) | `score`, `score-all` only |

The reader itself needs only the parquets, the ONNX files and the templates. The other files
are there to build the templates once and to score the reader.

## Get the recognizers

The three recognizers are the ONNX files that RapidOCR 3.10 publishes. The reader uses R1; R0
and R2 are only for the comparison in the report. Put them in `data/external/ocr_models/`:

```bash
mkdir -p data/external/ocr_models
```

```bash
curl -L -o data/external/ocr_models/PP-OCRv6_rec_small.onnx https://www.modelscope.cn/models/RapidAI/RapidOCR/resolve/v3.10.0/onnx/PP-OCRv6/rec/PP-OCRv6_rec_small.onnx
```

```bash
curl -L -o data/external/ocr_models/latin_PP-OCRv5_rec_mobile.onnx https://www.modelscope.cn/models/RapidAI/RapidOCR/resolve/v3.10.0/onnx/PP-OCRv5/rec/latin_PP-OCRv5_rec_mobile.onnx
```

```bash
curl -L -o data/external/ocr_models/PP-OCRv6_rec_medium.onnx https://www.modelscope.cn/models/RapidAI/RapidOCR/resolve/v3.10.0/onnx/PP-OCRv6/rec/PP-OCRv6_rec_medium.onnx
```

If the `ocr-v5` environment is installed, R0 and R1 are already in
`~/.venvs/ocr-v5/lib/python3.12/site-packages/rapidocr/models/`, and you can copy them.

Check the files:

```bash
sha256sum data/external/ocr_models/*.onnx
```

| File | SHA256 |
|---|---|
| `PP-OCRv6_rec_small.onnx` | `6f327246b50388f3c176ae304bd95767ea6dc0c9ae92153ef8cbe210b3c14884` |
| `latin_PP-OCRv5_rec_mobile.onnx` | `b20bd37c168a570f583afbc8cd7925603890efbcdc000a59e22c269d160b5f5a` |
| `PP-OCRv6_rec_medium.onnx` | `eef444829dbbe18d7fea59a3f6eb75647518d2b3a9568d27c92e42940204894b` |

## Build the label templates

The reader finds the labels by matching a template of each label `A)` to `E)`. The templates
are the mean of label crops taken from 200 rows. Build them once.

1. Draw the sample. The template step leaves the sample rows out, so the sample must exist
   first:

    ```bash
    .venv/bin/python -I laptop/option_boxes.py pick
    ```

2. Build the templates:

    ```bash
    .venv/bin/python -I laptop/option_boxes.py templates
    ```

    It prints the label heights it found and writes
    `data/interim/optrec/label_templates.npz`.

Both steps use a fixed seed, so a second run gives the same files.

## Read one image

From Python, call `read_row` on a gray image. Save this as a script and run it from the
repository root with `.venv/bin/python -I`:

```python
import sys

import cv2

sys.path.insert(0, "laptop")
import option_rec

recognizers = {"R1": option_rec.Rec("R1")}
arm = ("R1", "I0", "2d")   # recognizer, input (the gray crop), mode (split fractions and exponents)
gray = cv2.imread("path/to/problem.png", cv2.IMREAD_GRAYSCALE)
result = option_rec.read_row(recognizers, gray, [arm])[arm]
print(result["why"] or "ok", result["options"])
```

To read a row of the parquets instead of a file, use `option_boxes.load_rows({key})[key]["image"]`
and `option_boxes.gray(...)`, where `key` is `"<id>|<language>"`.

`result` has these fields:

| Field | Value |
|---|---|
| `why` | `""` when it read five options; `"no_labels"` when it found no `A)` to `E)` sequence; `"empty_value"` when an option has no value |
| `options` | `{"A": "12", "B": "3/4", ...}`; empty when `why` is not `""` |
| `conf` | per option, the lowest recognizer confidence of its reads, from 0 to 1 |
| `seen` | per option, what OpenCV found: `""`, `"frac"`, `"sup"` (exponent), `"frac+sup"` or `"lines"` (a value on several lines) |

Load the recognizer once and reuse it for every image. One option takes about 30 ms on one
CPU thread of the laptop, and about 13 ms with 4 threads; finding the labels takes about 0.24 s
per image.

## Read every row

To read all English, Catalan and Spanish text-only rows:

```bash
.venv/bin/python -I laptop/option_rec.py run --all --rec R1 --input I0 --mode 2d
```

It writes `data/interim/optrec/readall_B1-R1-I0-2d.jsonl`, one line per row:
`{"key", "options", "conf", "seen", "why"}`. It prints how many fractions and exponents OpenCV
found, and the time per read.

## Check the result

To see the boxes on the images, find them and draw review sheets:

```bash
.venv/bin/python -I laptop/option_boxes.py detect --arm B1
```

```bash
.venv/bin/python -I laptop/option_boxes.py sheets --arm B1 --band
```

The sheets are PNG files in `data/interim/optrec/sheets/review/`. Green boxes are options,
orange boxes are values, red boxes are the PP-OCRv5 reference. Both commands work on the sample
rows. Add `--strata hard` to `sheets` for the hard rows only. For rows of your own, give
`sheets` a JSON list of keys with `--keys <file>`, and add `--scope all` to both commands.

To compare the reader with today's pipeline (PP-OCRv5, then PP-OCRv4), on the gold rows and the
sample, after `run` without `--all`:

```bash
.venv/bin/python -I laptop/option_rec.py score
```

After `run --all`, the same without gold, on every row:

```bash
.venv/bin/python -I laptop/option_rec.py score-all
```

Both print counts only, never an option value.

## Limits

- **No fallback when the labels are missing.** `read_row` returns no options and
  `why = "no_labels"`. The box detector `detect_b1` falls back to B0, but the reading path does
  not use it. On the 2,277 text-only rows this did not happen.
- **Latin labels only.** The templates are made from English, Catalan and Spanish rows. Other
  scripts were not tried.
- **Text-only rows.** The rules assume the options are text. Rows with a figure were not tried.
- **Subscripts are written on the line**: a value such as "g, subscript 4, of x" comes out as
  `g4(x)`.
- **The templates depend on the gold file**, through the sample that `templates` leaves out.

For each command and its options, run the script with `--help`.
