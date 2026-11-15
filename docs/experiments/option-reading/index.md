# Reading the options

**Question:** how do we read the five answer options, A to E, and the question text, from the problem image?

**Why it matters:** M3Kang and the practice set give the options only inside the image. A solver that gets no options can only guess a letter.

**Where it lives:** `laptop/prepare_m3kang.py` reads the options with OCR (optical character recognition) and a parser that finds the labels `A)` to `E)`. The scripts of each experiment are in `laptop/`. All runs are on the laptop, on M3Kang rows. Most use the 2,277 text-only rows in English, Catalan and Spanish.

## How far coverage got

Rows with all five options read, of the 2,277 text-only rows ([OCR failure modes](../../OCR_FAILURE_MODES.md#what-this-means-for-improving-option-reading)):

| Step | Rows with five options |
| --- | --- |
| Old parser, PP-OCRv4 | 1,725 (75.8 %) |
| Fix for a missing `C)` label | 1,984 (87.1 %) |
| Fix for an `A` label with no sign | 2,032 (89.2 %) |
| PP-OCRv5 | 2,130 (93.5 %) |
| PP-OCRv5, then PP-OCRv4 when v5 reads no options (today) | 2,243 (98.5 %) |
| Label-anchored reader (candidate) | 2,277 (100 %) |

Coverage says that five options were found, not that they are right. The gold samples in the reports check that.

## Reports

| Date | Report | What it measured | Result | Verdict |
| --- | --- | --- | --- | --- |
| 2026-11-14 | [OCR failure modes](../../OCR_FAILURE_MODES.md) | Why rows reach the model with no options | Most empty rows lack the `C)` label. Two parser fixes and PP-OCRv5 raise coverage from 75.8 % to 98.5 %. | Adopted: the two fixes, PP-OCRv5 with the v4 fallback |
| 2026-11-14 | [OCR text vs annotation](../2026-11-ocr-text-vs-annotation.md) | Question text: PP-OCRv5 against PP-OCRv4 | Mean character error rate (CER) 9.5 % against 21.6 % | PP-OCRv5 for the question text |
| 2026-11-14 | [PP-FormulaNet](../2026-11-ppformulanet.md) | A LaTeX OCR for the options | 16 of 20 options against 15 for PP-OCRv5, p = 1.0. About 1.43 s per option. | Not adopted |
| 2026-11-14 | [Checked across languages](../2026-11-option-extraction-consensus.md) | Are the options right? A check between languages, on 20,798 rows | 81 of 100 gold rows fully right. The check misses 40 of 46 wrong options. | Format fusion recommended. Weak evidence. |
| 2026-11-15 | [Tesseract vs PP-OCR](../2026-11-tesseract-text-only.md) | Tesseract for the question and the options | Question CER 2.3 %. Five options in 75.5 % of rows, against 93.5 %. | Keep PP-OCRv5 for the options |
| 2026-11-15 | [Option crops with OpenCV](../2026-11-option-crops-opencv.md) | Crop the five option regions before OCR | Whole image first, then the OpenCV regions: 99.1 %. The recovered rows are less reliable. | Fallback measured. Correctness not measured. |
| 2026-11-15 | [Label-anchored boxes](../2026-11-option-boxes-intermediate-rec.md) | OpenCV boxes from the labels, a 2-D split of fractions and a small recognizer | 60 of 60 gold rows against 56, 40 of 40 hard rows against 7 | Candidate to replace today's reader |

## Current decision

- **Today:** PP-OCRv5, then PP-OCRv4 when v5 reads no options, with the two label fixes. 98.5 % of text-only rows get five options.
- **Candidate:** the label-anchored reader. It is better on every measure we have. It is not in `prepare_m3kang.py` yet. To run it, see [Read the answer options](../../OPTION_READER_GUIDE.md).
- **The main remaining error is maths layout.** OCR reads a stacked fraction as two numbers and an exponent as a normal digit. The 2-D split of the new reader is the step that fixes it.

## Open

- The label-anchored reader is tested on Latin-script text-only rows only. Rows with a figure and other scripts are not tested.
- Most gold samples were written by Claude, the coding agent, and no person checked them.
- The options of the practice set and the hidden test may come only in the image. On the board, `predict.py` on `main` reads no image (see [Solving](../solving/index.md#current-decision)).
