# Experiment: OCR text against the annotated question

This report records how close the text that PP-OCRv4 and PP-OCRv5 read from the
M3Kang problem images is to the question text that M3Kang gives us as data. It is for
the team and the datathon judges, to help them choose the OCR engine. Laptop run,
2026-11-14, branch `exp/decider-0.8b`.

[M3Kang](https://huggingface.co/datasets/qualcomm/M3Kang) is the dataset of Kangaroo
maths problems that the copilot answers. Each row has the question as text and as an
image. The five answer options, A to E, are only in the image. The
[OCR failure modes page](../OCR_FAILURE_MODES.md) measures how many options the OCR
reads. It has no annotated text to compare against. This report adds that comparison.

## Summary

- **PP-OCRv5 reads the question better than PP-OCRv4 in all three languages.** On
  2,236 text-only rows in English, Catalan and Spanish, the character error rate (CER)
  with no spaces is 9.5 % for PP-OCRv5 and 21.6 % for PP-OCRv4. PP-OCRv5 has the lower
  error in 1,565 rows, PP-OCRv4 in 351, and 320 are tied.
- **The typical row is read well; the mean is high because of rows with lines missing.**
  The median CER is 0.4 % for PP-OCRv5 and 4.5 % for PP-OCRv4. In 330 rows for
  PP-OCRv5 and 714 rows for PP-OCRv4, the OCR text is under 70 % of the reference
  length. We do not know the cause (see
  [Lines missing from the OCR text](#lines-missing-from-the-ocr-text)).
- **The three languages score alike.** For PP-OCRv5 the means are 10.3 % (English),
  8.9 % (Catalan) and 9.4 % (Spanish). Accents add almost nothing for PP-OCRv5.
- **This does not yet say how well the options are read.** The annotation covers the
  question only. The options use another font and are short, so the rates may differ.

## Why we ran it

Earlier experiments measured how many rows have all five options after OCR, and how
often the options agree between languages. Neither compares the OCR text with a correct
text. The question is the only part of the image that has one.

The hidden test of the datathon gives the copilot the question as text (see
[`GOAL_MUSTS.md`](../GOAL_MUSTS.md)), so the pipeline does not need OCR for the
question. We use the question as a **proxy**: it shows how each engine reads this kind
of image. How far the proxy holds for the options is not tested.

## Question and decision rule

**Question:** how far is the OCR text of the image from the annotated question, per
engine and per language?

We did not set a decision rule before the run. We read the result with these two
criteria, chosen afterwards: the engine with the lower mean CER in every language, and
more rows won than lost in a paired count. PP-OCRv5 meets both.

## What we compared

**Data.** The rows of M3Kang that have `text_only` true, in English (811 rows),
Catalan (811) and Spanish (655): 2,277 rows, all from the first of the four
`high_quality` files. The other three files have no rows in these languages.

**Engines.** Each ran on the whole image, with no crop. We reused the boxes saved by
`laptop/ocr_boxes.py dump` and did not run OCR again.

| Name | Package | Models |
|---|---|---|
| PP-OCRv4 | `rapidocr_onnxruntime` 1.4.4 | its default models |
| PP-OCRv5 | `rapidocr` 3.10 | mobile text detector, recognizer for Latin scripts |

The versions come from the [OCR failure modes page](../OCR_FAILURE_MODES.md), which
describes how the boxes were made.

**Reference.** The `text` column of M3Kang.

**Scoring** (`laptop/ocr_vs_text.py`):

1. Sort the boxes into lines, top to bottom and left to right, with the reading order
   of `laptop/prepare_m3kang.py`.
2. Cut the OCR text before the first `A)` label, because the options are not in `text`.
3. Normalize both texts: Unicode NFC, collapse spaces and line breaks, remove the
   problem number at the start.
4. Compute the edit distance and divide it by the length of the reference.

| Measure | What it counts |
|---|---|
| CER | characters, spaces included |
| CER, no spaces | characters with all spaces removed. This is the main figure |
| CER, no spaces or accents | as above, with accents removed, to price the accents |
| WER | words |
| Numbers match | share of rows where the digit sequences are equal |

PP-OCRv4 often joins words with no space between them. That is a read the engine does
well in the characters and badly in the spaces, so the main figure ignores spaces.

**Clean and flagged rows.** 41 rows have LaTeX or the answer options inside `text`.
Their reference is not a clean question, so we score them but report them apart. The
other 2,236 rows are the clean rows.

## Results

CER with no spaces, clean rows:

| Language | Rows | PP-OCRv4 mean | PP-OCRv4 median | PP-OCRv5 mean | PP-OCRv5 median |
|---|---|---|---|---|---|
| English | 793 | 19.5 % | 0.4 % | 10.3 % | 0.0 % |
| Catalan | 803 | 23.4 % | 4.5 % | 8.9 % | 0.7 % |
| Spanish | 640 | 22.0 % | 6.0 % | 9.4 % | 0.0 % |
| All | 2,236 | 21.6 % | 4.5 % | 9.5 % | 0.4 % |

Other measures, clean rows, all languages:

| Measure | PP-OCRv4 | PP-OCRv5 |
|---|---|---|
| CER, spaces included | 31.1 % | 9.5 % |
| CER, no spaces or accents | 20.5 % | 9.5 % |
| WER | 81.3 % | 11.3 % |
| Rows with CER (no spaces) under 5 % | 52.5 % | 82.9 % |
| Numbers match | 67.7 % | 86.1 % |

- **PP-OCRv5 wins.** Lower CER (no spaces) in 1,565 rows, PP-OCRv4 in 351, tie in 320.
- **Spaces explain most of the PP-OCRv4 gap in WER and CER with spaces.** Without
  them its CER falls from 31.1 % to 21.6 %. The rest is real misreading and missing
  lines.
- **Accents.** For PP-OCRv4, removing accents lowers the CER by 1.2 points in Catalan
  and 2.4 in Spanish. For PP-OCRv5 the change is under 0.2 points. We did not test
  single characters such as `ç` or `ñ`.
- **Flagged rows (41).** The CER with no spaces is 24.5 % for PP-OCRv4 and 19.0 % for
  PP-OCRv5. With so few rows we draw no conclusion from them.

## Lines missing from the OCR text

The mean CER is much higher than the median. For many rows the OCR text is much
shorter than the reference. We counted the clean rows where the OCR text has under 70 %
of the reference length, with spaces removed:

| Rows (of 2,236) | Count |
|---|---|
| PP-OCRv4 under 70 % | 714 |
| PP-OCRv5 under 70 % | 330 |
| PP-OCRv4 reaches 70 %, PP-OCRv5 does not | 203 |
| PP-OCRv5 reaches 70 %, PP-OCRv4 does not | 587 |
| Neither reaches 70 % | 127 |

A short OCR text is a sign of missing lines, not proof: a wrong read can also change
the length.

**What we know.** Two small checks, on different rows:

- In 4 rows with a high PP-OCRv5 error, the PP-OCRv5 boxes hold only the last line of
  the question and the options.
- In 2 rows where PP-OCRv4 reads the full question and PP-OCRv5 does not, we opened the
  image. The full question is in both images.

So in some rows the engine skips the first lines of a question that is in the image.
We did not run an engine again to see whether the text detector loses them. Six rows
show that this happens, not how often or why.

**A figure we do not use.** If we score only the rows where the PP-OCRv5 text reaches
70 %, the PP-OCRv5 CER falls to between 0.9 % and 1.5 %. That filter depends on the
engine under test and favors it, so it is not a result.

## Previous OCR experiments

The [OCR failure modes page](../OCR_FAILURE_MODES.md) has the method and the
numbers. Rows with five options, on the same 2,277 text-only rows:

| Step | Rows with five options |
|---|---|
| Old parser, PP-OCRv4 | 1,725 (75.8 %) |
| Fix for a missing `C)` label | 1,984 (87.1 %) |
| Fix for an `A` label with no sign | 2,032 (89.2 %) |
| PP-OCRv5 | 2,130 (93.5 %) |
| PP-OCRv5, PP-OCRv4 when PP-OCRv5 reads no options | 2,243 (98.5 %) |

Over all rows with five options, the numeric options agree between languages in 98.5 %
of cases for PP-OCRv4 and 99.4 % for PP-OCRv5. This report agrees with that ranking
with a reference that does not depend on the other languages.

## Limitations

- **The reference covers the question, not the options.** In the images we opened,
  the options are short values in a serif font and the question is sans-serif text.
  The question scores may not carry over to the options. There is still no annotated
  reference for the options.
- **One file, three languages, text-only rows.** Rows with a figure are not measured.
- **The 70 % length rule is a sign.** We checked 6 rows (see above). We did not find
  the cause of the missing lines.
- **The reading order may hurt both engines.** We joined the boxes with the same rule
  that the option parser uses. A question with two columns or a figure beside the text
  may be put in a wrong order. We did not measure this.
- **No decision rule was fixed before the run.** The two criteria in this report were
  chosen after we saw the results.
- **The edit distance is our own code.** The package `rapidfuzz` could not be
  installed. A self-test in the script compares our distance with a plain dynamic
  program on 300 random pairs.
- **One reviewer, a coding agent.** No person checked the images.

## Next step

- **Find why lines are missing.** Run both engines again on a few rows with missing
  lines, and compare the text-detector boxes with the image. Check whether a larger
  detector input or a margin around the image helps.
- **Test the proxy.** Transcribe the options of a sample by hand, 50 to 100 images per
  language, to get a reference for the options.
- **Score the combination.** The OCR failure modes page combines the two engines for
  the options. Score the same combination for the question text.

## Appendix: reproducibility

| Item | Value |
|---|---|
| Date and branch | 2026-11-14, `exp/decider-0.8b` |
| Data | M3Kang `high_quality`, first file; rows with `text_only` true, `eng`, `cat`, `esp`; 2,277 rows |
| Boxes | `data/interim/ocr_boxes_txto_yes.jsonl` (PP-OCRv4) and `data/interim/ocr_boxes_txto_yes_v5.jsonl` (PP-OCRv5), made by `laptop/ocr_boxes.py dump`. Not in Git: M3Kang is for research use only |
| Reference | `text` column of `data/raw_txto_yes/*.parquet` |
| Code | `laptop/ocr_vs_text.py` (this report), `laptop/ocr_boxes.py` (boxes; not in Git when this report was written) |
| Command | `python3 laptop/ocr_vs_text.py`, after `python3 laptop/ocr_vs_text.py --selftest` |
| Output | printed tables and `data/interim/ocr_vs_text.csv`: one row per problem and engine, with no problem text |
| Python | the `.venv` of the repository; pyarrow only, no other package |
