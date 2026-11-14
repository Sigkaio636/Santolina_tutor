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
defines row, empty row, coverage and text-only. In short:

- **OCR** (optical character recognition) reads the text in an image.
- **Box**: a region of the image that the OCR returns, with the text it read.
- **Row**: one problem in one language. A **text-only** row has `text_only` set to true
  in M3Kang: its question needs no figure.
- **CER** (character error rate): the edit distance between the OCR text and the
  reference text, divided by the length of the reference. The edit distance is the
  number of characters to insert, delete or change to turn one text into the other.
- **WER** (word error rate): the same, counted in words.
- **Clean rows**: text-only rows whose reference has no LaTeX and no answer options.
  The others are **flagged rows**.

## Summary

- **Use PP-OCRv5 for the question text, and PP-OCRv4 only as a fallback.** We did not
  test the combination of the two for the question. In 203 of 2,236 clean rows,
  PP-OCRv4 reaches 70 % of the reference length and PP-OCRv5 does not.
- **PP-OCRv5 reads the question better in all three languages.** On 2,236 clean rows
  (of 2,277 text-only rows in English, Catalan and Spanish), the mean CER with spaces
  ignored is 9.5 % for PP-OCRv5 and 21.6 % for PP-OCRv4. With spaces counted, it is
  9.5 % and 31.1 %. PP-OCRv5 has the lower CER in 1,565 rows, PP-OCRv4 in 351, and
  320 rows have the same CER. We did not measure whether lost spaces matter for the
  copilot.
- **The OCR reads the typical row well, but many rows come out short.** The median CER is
  0.4 % for PP-OCRv5 and 4.5 % for PP-OCRv4. The mean is much higher. In 330 of 2,236
  rows for PP-OCRv5 and 714 for PP-OCRv4, the OCR text is under 70 % of the reference
  length. We do not know the cause (see
  [Rows where the OCR text is much shorter](#rows-where-the-ocr-text-is-much-shorter)).
- **The three languages give similar results for PP-OCRv5.** The means are 10.3 %
  (English), 8.9 % (Catalan) and 9.4 % (Spanish). The languages share the same
  problems, so these are not three independent checks.
- **This does not say how well the OCR reads the options.** The annotation covers the
  question only.

## Why we ran it

Earlier experiments counted how many rows have all five options after OCR and how
often the options agree between languages. Neither compares the OCR text with a
reference text. The question is the only part of the image that has one.

We use the question as a **proxy**: it shows how each engine reads this kind of image.
How far the proxy holds for the options is not tested. The proxy is useful whatever
the hidden test contains. The format of the hidden test is a working hypothesis:
[`GOAL_MUSTS.md`](../GOAL_MUSTS.md) says that no source supports it. If the test gives
the question as text only, the pipeline does not need OCR for the question.

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

**Reference.** The `text` column of M3Kang.

**Scoring** (`laptop/ocr_vs_text.py`):

1. Sort the boxes into lines, top to bottom and left to right, with the reading order
   of `laptop/prepare_m3kang.py`.
2. Cut the OCR text before the first `A` label that has a `B` label after it. The
   options are not in `text`.
3. Normalize both texts: Unicode NFC, collapse spaces and line breaks, delete the
   problem number at the start.
4. Compute the edit distance and divide it by the length of the reference.

| Measure | What it counts |
|---|---|
| CER | characters, spaces included |
| CER, no spaces | characters, with all spaces deleted. This is the main figure |
| CER, no spaces or accents | as above, with accents deleted, to price the accents |
| WER | words |
| Numbers match | share of rows where the digit sequences are equal, with all spaces deleted (so `1 10` and `110` are equal) |

PP-OCRv4 often drops the space between words. Its CER falls by 9.5 points when we
ignore spaces. The main figure ignores spaces so that this does not hide how well the
engine reads the characters. The Summary gives both figures.

**Clean and flagged rows.** 41 of the 2,277 rows have LaTeX or the answer options inside
`text`. Their reference is not a clean question, so we score them but report them
apart. The other 2,236 are the clean rows.

**How we judged the result.** We set no threshold before the run. Afterwards we used
two criteria: the engine has the lower mean CER in every language, and it has the lower
CER in more rows than the other engine does. PP-OCRv5 meets both.

## Error rates by engine and language

Mean CER with spaces ignored, clean rows. The brackets are a 95 % bootstrap interval:
we drew problems with replacement 2,000 times (803 problems with at least one clean
row, seed 0), and kept the same problem in three languages together.

| Language | Clean rows | PP-OCRv4 | PP-OCRv5 | PP-OCRv4 minus PP-OCRv5, points |
|---|---|---|---|---|
| English | 793 | 19.5 % [17.5, 21.5] | 10.3 % [8.7, 11.9] | 9.2 [6.6, 11.8] |
| Catalan | 803 | 23.4 % [21.5, 25.5] | 8.9 % [7.5, 10.3] | 14.6 [12.3, 17.0] |
| Spanish | 640 | 22.0 % [20.1, 24.1] | 9.4 % [7.8, 11.1] | 12.6 [10.2, 15.2] |
| All | 2,236 | 21.6 % [20.3, 22.9] | 9.5 % [8.5, 10.5] | 12.1 [10.5, 13.6] |

The intervals do not include the choice to cut at `A` or the manual checks below. We
did not run a paired significance test. The rows of one problem in three languages are
not independent, which is why the draw is by problem.

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
| WER | 81.3 % | 11.3 % |
| Rows with CER (no spaces) under 5 % | 52.5 % | 82.9 % |
| Numbers match | 67.7 % | 86.1 % |

- **PP-OCRv5 has the lower CER (no spaces) in 1,565 of 2,236 rows**, PP-OCRv4 in 351,
  and 320 rows have the same CER.
- **Spaces explain 9.5 of the 21.6 points** that separate the two engines when spaces
  count (31.1 % against 9.5 %). That is 44 %. A gap of 12.1 points remains when we
  ignore spaces.
- **Accents.** Mean CER with spaces ignored, then with accents also ignored. The
  difference is the cost of the accents.

  | Language | PP-OCRv4 | PP-OCRv5 |
  |---|---|---|
  | English | 19.5 % → 19.5 % | 10.3 % → 10.3 % |
  | Catalan | 23.4 % → 22.2 % | 8.9 % → 8.8 % |
  | Spanish | 22.0 % → 19.6 % | 9.4 % → 9.4 % |

  We did not test single characters such as `ç` or `ñ`.
- **Flagged rows (41).** The CER with spaces ignored is 24.5 % for PP-OCRv4 and 19.0 %
  for PP-OCRv5. With so few rows we draw no conclusion from them.

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

A short OCR text is a sign of missing lines, not proof. A wrong read, or option text
left in the OCR text, also changes the length.

**What we know.** Two manual checks, on different rows, by Claude, the coding agent of
this project. No person looked at the images.

- We looked at the PP-OCRv5 boxes of 4 rows. They are the rows ranked 41 to 44 by
  PP-OCRv5 CER among the clean rows with a CER over 5 %. The boxes hold only the last
  line of the question and the options.
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
  options are short values in a serif font and the question is sans-serif text. The
  question scores may not carry over to the options. There is still no annotated
  reference for the options.
- **One file, three languages, text-only rows.** Rows with a figure are not measured.
- **The engines differ in more than the model version.** See the note under the table of
  engines.
- **The 70 % rule is a sign.** We found no cause for the short OCR texts.
- **The reading order may hurt both engines.** We joined the boxes with the same rule
  that the option parser uses. A question in two columns, or with a figure beside the
  text, may be put in a wrong order. We did not measure this.
- **The edit distance is our own code.** The package `rapidfuzz` could not be installed.
  A self-test in the script compares our distance with a plain dynamic program on 300
  random pairs.
- **An agent made the checks.** No person checked the images.

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
| Data | M3Kang `high_quality`, first file. Text-only rows in `eng`, `cat` and `esp`: 2,277 rows |
| Boxes | `data/interim/ocr_boxes_txto_yes.jsonl` (PP-OCRv4) and `data/interim/ocr_boxes_txto_yes_v5.jsonl` (PP-OCRv5), made by `laptop/ocr_boxes.py dump`. Not in Git: M3Kang is for research use only |
| Reference | `text` column of `data/raw_txto_yes/*.parquet` |
| Code | `laptop/ocr_boxes.py` (commit `a3b89a5`) and `laptop/ocr_vs_text.py` (commit `41f17f7`). A later commit added the bootstrap interval |
| Output | the printed tables, and `data/interim/ocr_vs_text.csv`: one row per problem and engine, with no problem text |

To reproduce the numbers, run from the repository root, with the `.venv` of the
repository (it holds pyarrow, the only package the script needs):

```bash
.venv/bin/python -I laptop/ocr_vs_text.py --selftest
```

```bash
.venv/bin/python -I laptop/ocr_vs_text.py
```

The first command prints `selftest ok`. The second prints the tables above, in the
order of this report, and writes `data/interim/ocr_vs_text.csv`. It reads the boxes and
the reference from the paths in the table.
