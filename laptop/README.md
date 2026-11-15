# laptop/

Python scripts that run on the laptop (`ocr_speed.py` also runs on the board,
through `board/ocr_speed.sh`): M3Kang preparation,
OCR and option-reading studies, model measurements and the intent router
bake-off. They read M3Kang files under `data/`, which stay out of Git (see
[`CLAUDE.md`](../CLAUDE.md)).

## Install and run

[`requirements.txt`](requirements.txt) covers `prepare_m3kang.py`, the script
every team needs (board setup guide, step 9):

```bash
uv run --no-project --python 3.12 --with-requirements laptop/requirements.txt \
  python laptop/prepare_m3kang.py --languages eng,cat
```

The OCR and option scripts need more packages (OpenCV, SciPy, RapidOCR,
PaddleOCR, PyTorch or Transformers, depending on the script) that
`requirements.txt` does not list: check the script's imports. Every script except
`compare_runs.py` and `easy_read_stats.py` prints its options with `--help`;
those two print their usage in their docstring.

## Scripts

Status: **in use** means a guide uses the script; **experiment** means only a
report in [`docs/experiments/`](../docs/experiments/) uses it; **no doc** means
no document uses it.

| File | What it does | Status | Doc |
|---|---|---|---|
| `prepare_m3kang.py` | Downloads M3Kang, reads the options A to E with OCR, splits train and validation by problem ID, writes JSONL files for the board. | in use | [Board setup](../docs/BOARD_SETUP.md) step 9, [Practice set](../docs/PRACTICE_SET.md) |
| `requirements.txt` | Packages for `prepare_m3kang.py`. | in use | [Board setup](../docs/BOARD_SETUP.md) step 9 |
| `compare_runs.py` | Compares `eval.py` runs on the same validation file. | in use | [decider-2b vision](../docs/models/decider-2b-vision.md), [InternVL3.5 1B](../docs/models/internvl3.5-1b.md) |
| `eval_vision.py` | Measures the copilot on figure rows, with the image. | in use | [decider-2b vision](../docs/models/decider-2b-vision.md), [InternVL3.5 1B](../docs/models/internvl3.5-1b.md) |
| `router_bakeoff.py` | Labels student messages with a llama-server model, to compare intent router candidates. | in use | [Use the decider-2b router](../docs/how-to/use-decider-2b-router.md) |
| `router_messages.json`, `router_messages_r2.json` | Invented student messages, labelled by one author, for the bake-off. No M3Kang text. | in use | [Use the decider-2b router](../docs/how-to/use-decider-2b-router.md) |
| `ocr_boxes.py` | Runs an OCR engine on M3Kang images and compares engines. | in use | [OCR failure modes](../docs/OCR_FAILURE_MODES.md), [Option reader guide](../docs/OPTION_READER_GUIDE.md) |
| `option_consensus.py` | Scores ways to read the five options, checked across languages. | in use | [OCR failure modes](../docs/OCR_FAILURE_MODES.md), [Option reader guide](../docs/OPTION_READER_GUIDE.md) |
| `ocr_failure_modes.py` | Measures why OCR fails to read the options. | in use | [OCR failure modes](../docs/OCR_FAILURE_MODES.md) |
| `option_boxes.py` | Finds the boxes of the five options with OpenCV (label-anchored option reader). | in use | [Option reader guide](../docs/OPTION_READER_GUIDE.md) |
| `option_rec.py` | Reads the five options with a text recognizer inside those boxes (label-anchored option reader). | in use | [Option reader guide](../docs/OPTION_READER_GUIDE.md) |
| `split_text_only.py` | Splits the M3Kang parquet shards by the `text_only` flag. | in use | [Option reader guide](../docs/OPTION_READER_GUIDE.md) |
| `ocr_crops.py` | Runs PP-OCRv5 on option crops made by a notebook. | in use | [Option reader guide](../docs/OPTION_READER_GUIDE.md) |
| `router_messages_check.py` | Checks the router message files before a run. | experiment | [Router messages method](../docs/experiments/2026-11-router-messages-method.md) |
| `ocr_vs_text.py` | Scores OCR engines against the annotated question text. | experiment | [OCR text vs annotation](../docs/experiments/2026-11-ocr-text-vs-annotation.md) |
| `ocr_speed.py` | Times the OCR engines on the laptop CPU (`board/ocr_speed.sh` runs it on the board). | experiment | [Tesseract text-only](../docs/experiments/2026-11-tesseract-text-only.md) |
| `formula_trial.py` | Tries PP-FormulaNet (LaTeX OCR) on single options. | experiment | [PP-FormulaNet](../docs/experiments/2026-11-ppformulanet.md) |
| `prior_txto_no.py` | Measures no-model letter rules on figure rows. | experiment | [Figure-row heuristics](../docs/experiments/2026-11-txto-no-heuristics.md) |
| `sample_txto_no.py` | Draws a stratified sample of figure rows for a time-boxed run. | experiment | [InternVL3.5 1B vs decider-2b vision](../docs/experiments/2026-11-internvl35-1b-vs-decider-2b-vision-txto-no.md) |
| `math_layout.py` | Reads stacked fractions and exponents in the options from OCR geometry. `option_consensus.py` imports it. | no doc | |
| `ocr_report.py` | Builds a local HTML dashboard of how well OCR read the options. | no doc | |
| `easy_read_stats.py` | Readability numbers for the student app's easy read, before and after. | no doc | |

`OCR_FAILURE_MODES.md` will be split into one document per type; its links here
will change then.

Terms: [GLOSSARY.md](../GLOSSARY.md) (Row, Text-only row, Coverage,
Label-anchored option reader, Intent router).
