# laptop/

Python scripts that run on the laptop: [M3Kang](../GLOSSARY.md) preparation
for the board, studies of how OCR (optical character recognition) reads the
answer options, model measurements, and the intent router comparison. Most of
them read M3Kang files under `data/`, which stay out of Git (see
[`CLAUDE.md`](../CLAUDE.md)).

## Run prepare_m3kang.py

`eval.py`, retrieval and the explorer need the files that `prepare_m3kang.py` writes
([board setup guide, step 9](../docs/BOARD_SETUP.md#step-9-prepare-m3kang-on-your-laptop),
which has the expected output). It needs [uv](https://docs.astral.sh/uv/).
From the repository folder:

```bash
uv run --no-project --python 3.12 --with-requirements laptop/requirements.txt \
  python laptop/prepare_m3kang.py --languages eng,cat
```

[`requirements.txt`](requirements.txt) covers only this script. The OCR and
option scripts also need some of these packages: `opencv-python`, `numpy`,
`pillow`, `pyarrow`, `scipy`, `onnxruntime`, `rapidocr`, `paddleocr`, and (only `option_rec.py granite`) `torch`
with `transformers`. Some imports are inside functions, so check the whole script. The
`tesseract` engine also needs the system program `tesseract`.

Most scripts print their options with `--help`. `compare_runs.py` prints its
usage when it gets too few arguments. `easy_read_stats.py` takes one file path
(default `data/val.jsonl`). Its usage is in its docstring.

## Files

Status: **guide** means a guide in [`docs/`](../docs/) uses the script.
**report** means only a report in [`docs/experiments/`](../docs/experiments/)
uses it. **none** means no document uses it. "Guide" does not mean the copilot
uses the script.

| File | What it does | Status | Doc |
|---|---|---|---|
| `prepare_m3kang.py` | Downloads M3Kang and reads the options A to E with OCR. Splits train and validation by problem ID. Writes the JSONL files (one Row per line) for the board. | guide | [Board setup](../docs/BOARD_SETUP.md#step-9-prepare-m3kang-on-your-laptop), [Practice set](../docs/PRACTICE_SET.md) |
| `requirements.txt` | Packages for `prepare_m3kang.py`. | guide | [Board setup](../docs/BOARD_SETUP.md#step-9-prepare-m3kang-on-your-laptop) |
| `compare_runs.py` | Compares the result files of `eval.py` Experiments on the same validation set. | guide | [decider-2b vision](../docs/models/decider-2b-vision.md), [InternVL3.5 1B](../docs/models/internvl3.5-1b.md) |
| `eval_vision.py` | Measures the copilot on figure rows, with the image. | guide | [decider-2b vision](../docs/models/decider-2b-vision.md), [InternVL3.5 1B](../docs/models/internvl3.5-1b.md) |
| `router_bakeoff.py` | Labels student messages with a model on a llama.cpp server, to compare intent router candidates. | guide | [Use the decider-2b router](../docs/how-to/use-decider-2b-router.md) |
| `router_messages.json`, `router_messages_r2.json` | Invented student messages, labelled by one author, for the bake-off. No M3Kang text. | guide | [Use the decider-2b router](../docs/how-to/use-decider-2b-router.md) |
| `ocr_boxes.py` | Runs an OCR engine on M3Kang images and compares engines. | guide | [OCR failure modes](../docs/OCR_FAILURE_MODES.md), [Option reader guide](../docs/OPTION_READER_GUIDE.md) |
| `option_consensus.py` | Scores ways to read the five options, and checks each reading against the other languages of the same problem. | guide | [OCR failure modes](../docs/OCR_FAILURE_MODES.md), [Option reader guide](../docs/OPTION_READER_GUIDE.md) |
| `ocr_failure_modes.py` | Measures why OCR fails to read the options. | guide | [OCR failure modes](../docs/OCR_FAILURE_MODES.md) |
| `option_boxes.py` | Finds the boxes of the five options with OpenCV (Label-anchored option reader). | guide | [Option reader guide](../docs/OPTION_READER_GUIDE.md) |
| `option_rec.py` | Reads the five options with a text recognizer inside those boxes (Label-anchored option reader). | guide | [Option reader guide](../docs/OPTION_READER_GUIDE.md) |
| `split_text_only.py` | Splits the M3Kang parquet files by the `text_only` flag. | guide | [Option reader guide](../docs/OPTION_READER_GUIDE.md) |
| `ocr_crops.py` | Runs PP-OCRv5 on the option crops made by the notebook `notebooks/option_crops_opencv.ipynb` (not in Git). | guide | [Option reader guide](../docs/OPTION_READER_GUIDE.md) |
| `router_messages_check.py` | Checks the router message files before a run. | report | [Router messages method](../docs/experiments/2026-11-router-messages-method.md) |
| `ocr_vs_text.py` | Scores OCR engines against the annotated question text. | report | [OCR text vs annotation](../docs/experiments/2026-11-ocr-text-vs-annotation.md) |
| `ocr_speed.py` | Times the OCR engines on the CPU. `board/ocr_speed.sh` runs it on the board. | report | [Tesseract text-only](../docs/experiments/2026-11-tesseract-text-only.md) |
| `formula_trial.py` | Tries PP-FormulaNet (LaTeX OCR) on single options. | report | [PP-FormulaNet](../docs/experiments/2026-11-ppformulanet.md) |
| `prior_txto_no.py` | Measures no-model letter heuristics on figure rows. | report | [Figure-row heuristics](../docs/experiments/2026-11-txto-no-heuristics.md) |
| `sample_txto_no.py` | Draws a sample of figure rows, with each language and OCR outcome in proportion, for a run with a time limit. | report | [InternVL3.5 1B vs decider-2b vision](../docs/experiments/2026-11-internvl35-1b-vs-decider-2b-vision-txto-no.md) |
| `math_layout.py` | Reads stacked fractions and exponents in the options from OCR geometry. `option_consensus.py` imports it. | none | |
| `ocr_report.py` | Builds a local HTML dashboard of how well OCR read the options. | none | |
| `easy_read_stats.py` | Readability numbers for the student app's easy-read layout, compared with the text as written. | none | |

Terms: [GLOSSARY.md](../GLOSSARY.md) (M3Kang, Copilot, Row, Text-only row,
Validation set, Experiment, Label-anchored option reader, Intent router).
