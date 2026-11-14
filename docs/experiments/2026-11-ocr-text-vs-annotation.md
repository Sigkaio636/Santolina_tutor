# Experiment: OCR text against the annotated question

This report measures how close the text that two OCR engines read from the problem
images is to the question text that the dataset gives us as data. The engines are
PP-OCRv4 and PP-OCRv5. It is for the team and the datathon judges, to help them
choose the engine. Laptop run, 2026-11-14, branch `exp/decider-0.8b`.

[M3Kang](https://huggingface.co/datasets/qualcomm/M3Kang) is the dataset of Kangaroo
maths problems that the copilot answers. Each problem has the question as text and as
an image. The five answer options, A to E, are only in the image. The
[OCR failure modes page](../OCR_FAILURE_MODES.md) measures how many options the OCR
reads, and it has no annotated text to compare against. This report adds that
comparison for the question.

## Terms used here

The [OCR failure modes page](../OCR_FAILURE_MODES.md#background-how-the-options-are-read)
defines the terms for the options. The terms for this report:

- **OCR** (optical character recognition) reads the text in an image.
- **Box**: a region of the image that the OCR returns, with the text it read.
- **Reference** (also called the annotation): the question text in the `text` column of
  M3Kang.
- **Row**: one problem in one language. A **text-only** row has `text_only` set to true
  in M3Kang: its question needs no figure.
- **CER** (character error rate): the edit distance between the OCR text and the
  reference, divided by the length of the reference. The edit distance is the number of
  characters to insert, delete or change to turn one text into the other.
- **Clean rows**: text-only rows whose reference has no LaTeX (maths markup) and no
  answer options. The others are **flagged rows**.

## Summary

- **Use PP-OCRv5 (`rapidocr` 3.10) for the question text.** Keep PP-OCRv4 only as a
  fallback, but we did not define or test the fallback. The 70 % rule below needs the
  reference, so it cannot run on a new problem. PP-OCRv5 reaches 70 % of the reference
  length in 587 clean rows where PP-OCRv4 does not. PP-OCRv4 does so in 203 rows where
  PP-OCRv5 does not. We did not test the combination of the two for the question.
- **PP-OCRv5 reads the question better in all three languages.** On 2,236 clean rows
  (of 2,277 text-only rows in English, Catalan and Spanish), the mean CER with spaces
  ignored is 9.5 % for PP-OCRv5 and 21.6 % for PP-OCRv4. With spaces counted, it is
  9.5 % and 31.1 %. A lower CER is better: 10 % is about one wrong character in ten.
  The digits match the reference in 86.1 % of rows for PP-OCRv5 and 67.7 % for
  PP-OCRv4. We did not measure whether lost spaces matter for the copilot. The two
  runs also differ in package (`rapidocr` 3.10 against `rapidocr_onnxruntime` 1.4.4),
  so the gap is between two setups, not only two model versions.
- **The OCR reads the typical row well, but the mean is mostly missing text.** The
  median CER is 0.4 % for PP-OCRv5 and 4.5 % for PP-OCRv4. A row is short when the OCR
  text is under 70 % of the reference length. That is 330 of 2,236 rows for PP-OCRv5
  and 714 for PP-OCRv4. They give 89 % and 84 % of the summed CER. On the other rows
  the mean CER is 1.2 % and 5.3 %. We do not know why the texts are short (see
  [Rows where the OCR text is much shorter](#rows-where-the-ocr-text-is-much-shorter)).
- **How sure we are.** The result is strong for the question text of text-only rows,
  from one file. It says nothing yet about the options, which matter more because only
  the image has them. The cause of the short texts is unknown. We checked 4 lists of
  boxes and 2 images by hand, and no person looked at them. If the hidden test gives
  the question as text, the pipeline does not need OCR for the question.

## Why we ran it

The question is the only part of the image that has a reference text. We use it as a
**proxy**: it shows how each engine reads this kind of image. How far the proxy holds
for the options is not tested. The proxy is useful whatever the hidden test contains.
The format of the hidden test is a working hypothesis:
[`GOAL_MUSTS.md`](../GOAL_MUSTS.md) says that no source supports it.

## What we compared

**Data.** The text-only rows of M3Kang in English (811 rows), Catalan (811) and
Spanish (655): 2,277 rows. All come from the first of the four `high_quality` files.
The other three files have no rows in these languages.

**Engines.** Each engine ran on the whole image, with no crop. We reused the boxes that
`laptop/ocr_boxes.py dump` saved, and did not run OCR again.

| Name | Package | Models |
|---|---|---|
| PP-OCRv4 | `rapidocr_onnxruntime` 1.4.4 | its default models |
| PP-OCRv5 | `rapidocr` 3.10 | mobile text detector, recognizer for Latin scripts |

The two runs differ in the package and in the detector setup, not only in the model
version. We cannot say which of these causes the gap. The versions come from the
[OCR failure modes page](../OCR_FAILURE_MODES.md), which gives them with one sentence
on how we made the boxes.

**Scoring** (`laptop/ocr_vs_text.py`):

1. Sort the boxes into lines, top to bottom and left to right, with the reading order
   of `laptop/prepare_m3kang.py`.
2. Cut the OCR text before the first `A` label that has a `B` label after it. The
   options are not in `text`.
3. Normalize both texts: Unicode NFC (one fixed form for accented letters), collapse
   spaces and line breaks, delete the problem number at the start.
4. Compute the edit distance and divide it by the length of the reference.

| Measure | What it counts |
|---|---|
| CER | characters, spaces included |
| CER, no spaces | characters, with all spaces deleted. This is the main figure |
| CER, no spaces or accents | as above, with accents deleted, to price the accents |
| Numbers match | share of rows where the digit sequences are equal, with all spaces deleted (so `1 10` and `110` are equal) |

PP-OCRv4 often drops the space between words. Counting spaces, PP-OCRv4 trails
PP-OCRv5 by 21.6 points. Ignoring spaces, it trails by 12.1. So lost spaces cause under
half of the gap. The main figure ignores spaces so that they do not hide how well the
engine reads the characters. The Summary gives both figures.

**Clean and flagged rows.** 41 of the 2,277 rows have LaTeX or the answer options inside
`text`. Their reference is not a clean question, so we score them but report them
apart. The other 2,236 are the clean rows.

**How we judged the result.** We set no threshold before the run. Afterwards we used
two criteria: the engine has the lower mean CER in every language, and it has the lower
CER in more rows than the other engine does.

## Error rates by engine and language

Mean CER with spaces ignored, clean rows. The brackets show the likely range of the
mean. They are a 95 % bootstrap interval: we drew problems with replacement 2,000
times (803 problems with at least one clean row, seed 0), and kept the same problem in
three languages together.

| Language | Clean rows | PP-OCRv4 | PP-OCRv5 | PP-OCRv4 minus PP-OCRv5, percentage points |
|---|---|---|---|---|
| English | 793 | 19.5 % [17.5, 21.5] | 10.3 % [8.7, 11.9] | 9.2 [6.6, 11.8] |
| Catalan | 803 | 23.4 % [21.5, 25.5] | 8.9 % [7.5, 10.3] | 14.6 [12.3, 17.0] |
| Spanish | 640 | 22.0 % [20.1, 24.1] | 9.4 % [7.8, 11.1] | 12.6 [10.2, 15.2] |
| All | 2,236 | 21.6 % [20.3, 22.9] | 9.5 % [8.5, 10.5] | 12.1 [10.5, 13.6] |

In each language the ranges of the two engines do not overlap, and the range of the
difference stays above zero. The ranges do not include the effect of how we cut the
options off at the `A` label, or the manual checks below. The rows of one problem in
three languages are not independent, which is why the draw is by problem.

Median CER with spaces ignored, clean rows:

| Language | PP-OCRv4 | PP-OCRv5 |
|---|---|---|
| English | 0.4 % | 0.0 % |
| Catalan | 4.5 % | 0.7 % |
| Spanish | 6.0 % | 0.0 % |
| All | 4.5 % | 0.4 % |

Other measures, clean rows, all languages (2,236):

| Measure | PP-OCRv4 | PP-OCRv5 |
|---|---|---|
| CER, spaces included | 31.1 % | 9.5 % |
| CER, no spaces or accents | 20.5 % | 9.5 % |
| Rows with CER (no spaces) under 5 % | 52.5 % | 82.9 % |
| Numbers match | 67.7 % | 86.1 % |

- **PP-OCRv5 has the lower CER (no spaces) in 1,565 of 2,236 rows**, PP-OCRv4 in 351,
  and 320 rows have the same CER.
- **Accents.** Ignoring accents lowers the mean CER by 0.1 points or less, except for
  PP-OCRv4 on Catalan (1.2 points) and Spanish (2.5 points). We did not test single
  characters such as `ç` or `ñ`.

## Rows where the OCR text is much shorter

The mean CER is much higher than the median. In many rows the OCR text is much shorter
than the reference. We counted the clean rows where the OCR text has under 70 % of the
reference length, with all spaces deleted. The 70 % is a round number that we did not
tune.

| Rows (of 2,236) | Count |
|---|---|
| PP-OCRv4 under 70 % | 714 |
| PP-OCRv5 under 70 % | 330 |
| PP-OCRv4 reaches 70 %, PP-OCRv5 does not | 203 |
| PP-OCRv5 reaches 70 %, PP-OCRv4 does not | 587 |
| Neither reaches 70 % | 127 |

The short rows give 89 % of the summed CER for PP-OCRv5 and 84 % for PP-OCRv4. On the
other rows the mean CER is 1.2 % for PP-OCRv5 (1,906 rows) and 5.3 % for PP-OCRv4
(1,522 rows). The script prints these figures.

A short OCR text is a sign of missing lines, not proof. A wrong read, or option text
left in the OCR text, also changes the length.

**What we know.** Two manual checks, on different rows, by Claude, the coding agent of
this project. No person looked at the images. They are anecdotes: the choice of rows is
not saved in the repository.

- We looked at the PP-OCRv5 boxes of 4 rows. They are the rows ranked 41 to 44, from
  the highest PP-OCRv5 CER down, among the clean rows with a CER over 5 %. The boxes
  hold only the last line of the question and the options.
- We drew 3 rows at random (seed 1) from the 203 rows where only PP-OCRv4 reaches 70 %,
  and opened the images of 2 of them. The full question is in both images.

So for 2 rows we know that the engine skipped lines of a question that is in the image.
We did not run an engine again to see whether the text detector loses the lines. Two
images show that this happens, not how often or why.

**A figure we do not use.** If we score only the rows where an engine's own text reaches
70 % of the reference length, that engine looks much better. The filter depends on the
engine under test and favors it, so we report no such figure.

## Previous OCR experiments

Earlier experiments measured the parser fixes for missing `C)` and `A` labels, and
PP-OCRv5 against PP-OCRv4 on how many rows have all five options. The
[OCR failure modes page](../OCR_FAILURE_MODES.md) has the method and the figures.

## Limitations

- **The reference covers the question, not the options.** In the 2 images we opened, the
  options use a different font. The question scores may not carry over to the options.
  There is still no annotated reference for the options.
- **One file, three languages, text-only rows.** Rows with a figure are not measured.
- **The reading order may hurt both engines.** We joined the boxes with the same rule
  that the option parser uses. A question in two columns, or with a figure beside the
  text, may be put in a wrong order. We did not measure this.
- **The edit distance is our own code.** The package `rapidfuzz` could not be installed.
  A self-test in the script compares our distance with a plain textbook method on 300
  random pairs.

## Next steps

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
| Boxes | `data/interim/ocr_boxes_txto_yes.jsonl` (PP-OCRv4) and `data/interim/ocr_boxes_txto_yes_v5.jsonl` (PP-OCRv5), made by `laptop/ocr_boxes.py dump`. Not in Git: M3Kang is for research use only |
| Reference | `text` column of `data/raw_txto_yes/*.parquet` |
| Code | `laptop/ocr_boxes.py` (commit `a3b89a5`) and `laptop/ocr_vs_text.py` (first in commit `41f17f7`, extended in later commits: see `git log`) |
| Output | the printed figures, and `data/interim/ocr_vs_text.csv`: one row per problem, language and engine, with no problem text |

To reproduce the numbers, run from the repository root, with the `.venv` of the
repository (it holds pyarrow, the only package the script needs):

```bash
.venv/bin/python -I laptop/ocr_vs_text.py --selftest
```

```bash
.venv/bin/python -I laptop/ocr_vs_text.py
```

The first command prints `selftest ok`. The second prints the figures of this report and
writes `data/interim/ocr_vs_text.csv`. It reads the boxes and the reference from the
paths in the table.
