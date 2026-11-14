# OCR failure modes: expected and measured

This page explains why many M3Kang problems reach the model without their answer options. It compares the failures that the board guide expects with the failures we measured. It is for team members who want the model to see more answer options.

The main result: in most empty rows (rows with no options), the text that OCR returns has no `C)` label in front of option C. The guide does not list this failure. A parser change now rebuilds the missing C. On the 2,277 text-only rows in English, Catalan and Spanish, it raises coverage from 75.8% to 87.1% and empties no row that had options (see [The fix, measured](#the-fix-measured)). A second fix for an `A` label with no sign brings it to 89.2%. The newer PP-OCRv5 OCR models, with PP-OCRv4 as a fallback, bring it to 98.5% (see [What this means](#what-this-means-for-improving-option-reading)).

For how well the two engines read the question text, scored against the annotated text of M3Kang, see the [experiment report](experiments/2026-11-ocr-text-vs-annotation.md).

## Background: how the options are read

[M3Kang](https://huggingface.co/datasets/qualcomm/M3Kang) is the dataset of Kangaroo maths problems that the copilot (our tutoring app on the Arduino UNO Q) answers. Each problem has a question as text and an image. The five answer options, A to E, are only in the image. The board guide explains this in [step 9](BOARD_SETUP.md#step-9-prepare-m3kang-on-your-laptop).

`laptop/prepare_m3kang.py` reads the options in two parts:

- **OCR** (optical character recognition). [RapidOCR](https://github.com/RapidAI/RapidOCR) finds the text boxes in the image and reads the text in each one.
- **The parser**, the function `parse_options`. It sorts the boxes by line, top to bottom, and left to right inside a line. Then it looks for the labels `A)` to `E)` in that order. It takes the text after each label as the value of that option.

The label can end in `)`, `）`, `]`, `:` or `.`. For B to E, the parser also accepts a letter alone, or a letter followed by a number.

Some words on this page:

- A **row** is one problem in one language. A problem in English, Catalan and Spanish gives three rows.
- An **empty row** has no options (`"options": {}`), because the OCR or the parser failed. The model then sees only the question.
- **Coverage** is the share of rows that have all five options.
- A **text-only** problem has `text_only` set to true in M3Kang: its question needs no figure to solve.
- The **validation set** is the part of the rows that `prepare_m3kang.py` keeps apart to score models locally, in `data/val.jsonl`. The rest is the training set, `data/train.jsonl`.

## What the guide expects

[Section 9.3 of the board guide](BOARD_SETUP.md#93-what-the-ocr-gets-wrong) names three failure modes, with no counts:

1. The options are pictures: shapes, graphs or figures.
2. Fractions and formulas are read wrong, for example `1/2` read as `12`.
3. Two options come out the same.

For improvement, the guide says to look at the empty rows with `--save-images` (section 9.3). [Section 13.3](BOARD_SETUP.md#133-ideas-to-reason) suggests improving the OCR, or cropping the bottom of the image before OCR.

## How we measured

The data came from a run of `prepare_m3kang.py --languages eng,cat,esp --gpu` on 2026-11-14:

- input: the first of the four files of the `high_quality` part of M3Kang
- languages: English (`eng`), Catalan (`cat`) and Spanish (`esp`)
- OCR on a GPU
- result: 4,862 rows. That is 1,747 problems, each in English and in Catalan, and 1,368 of them also in Spanish.

Coverage is 63.4%: 3,083 rows have five options and 1,779 are empty. No row has between one and four options. By language, coverage is 61.8% in English, 64.4% in Catalan and 64.2% in Spanish. The guide reports 62% for an English-only run, so our English figure agrees with it.

We measured three things:

- **Why rows are empty.** We ran OCR again on 300 empty rows, chosen at random with a fixed seed (0), so the same 300 rows come out each time. For each row, we recorded where the parser stops.
- **Errors in rows with options.** 823 problems have options in all three languages. A number should be the same in every language, apart from format (spaces, decimal comma). So if a numeric option differs by more than its format, at least one of the rows has an error. A difference in words can also come from translation, so it is a weaker sign.
- **Coverage in the validation set**, split by text-only problems and problems with a figure.

Except for the guide's 62% and the [manual review](#manual-review-of-a-sample-by-claude), every number on this page comes from `laptop/ocr_failure_modes.py`. It reads `data/train.jsonl`, `data/val.jsonl`, and the dataset file that `prepare_m3kang.py` read. Pass that file with `--parquet`: `prepare_m3kang.py` downloads it to the Hugging Face cache. The script needs the packages in `laptop/requirements.txt`. With `--gpu` it also needs `onnxruntime-gpu`; without it, OCR runs on the CPU, more slowly.

The script prints counts only. M3Kang is for research use only, so this page shows no problem text and no real option values. Every example below is made up.

## Expected and measured, side by side

Failures that leave a row empty, from the sample of 300 empty rows:

| Failure | In the guide? | Rows of 300 | Verdict |
| --- | --- | --- | --- |
| The parser stops after B: no `C)` label in the OCR text | No | 195 (65%) | Main failure, not in the guide |
| Five labels, at least one with no value after it | Yes, mode 1 (pictures) | 52 (17%) | Picture options land here, but so can text options (see the manual review) |
| No `A)` label that the parser accepts | No | 48 (16%) | Second failure not in the guide |
| The parser stops after A or after C | No | 4 (1%) | Rare |
| Five labels now, but the stored result is empty | No | 1 | See the limits |

Errors in rows that have options:

| Failure | In the guide? | Measured | Source | Verdict |
| --- | --- | --- | --- | --- |
| Two options are the same | Yes, mode 3 | 18 of 3,083 rows | Script | Confirmed, rare |
| A numeric option has a different length in another language | No | 58 options | Script | Not in the guide |
| A fraction differs between languages | Yes, mode 2 | 1 option | Script | Seen once (see the limits) |
| A superscript exponent becomes a normal digit | No (close to mode 2) | 1 of 15 rows | Manual review | Seen in the manual review |

## No `C)` label in the OCR text

In 194 of the 195 rows where the parser stops after B, the OCR text has no C label at all: not as a box of its own, and not inside another box. So the OCR itself loses the label. Without it, the parser adds whatever follows B to option B. Then it waits for a C that never comes, and it returns no options.

The value of option C can still be in the OCR output, as a box of its own. A made-up example: the OCR returns `A) 10`, `B) 20`, `30`, `D) 40`, `E) 50`. Here `30` is option C.

81 of the 195 rows are text-only problems.

**A parser fix:** when B is followed by D, accept that the C label is missing and rebuild C from the boxes between B and D. We measured a strict form of this rule: it needs the A, B, D and E labels written as a letter followed by a sign such as `)`. For the 195 rows:

| Boxes between the B and D labels | Rows | Result |
| --- | --- | --- |
| Exactly two values (B and C) | 87 | Recoverable with no guess |
| Fewer or more than two values | 68 | Ambiguous: the box positions are needed to split them |
| A, B, D or E not written as a letter followed by a sign | 40 | Not fixed by the strict rule |

The 87 recoverable rows are 29% of the sample. If the same share holds for all 1,779 empty rows, about 516 more rows would have options. Coverage would go from 63.4% to about 74.0%. We computed a 95% interval with the normal approximation on the sample share: 72.1% to 75.9%. This is an extrapolation from the sample, made before the fix was written.

### The fix, measured

`parse_options` in `laptop/prepare_m3kang.py` now applies the rule. It acts only when the parser waits for C and finds a D label, with exactly two values after the B label. In the version measured here the D label needed a sign such as `)`; the [fix for the `A)` label](#no-a-label) later also accepts a D without a sign. The first value becomes B and the second becomes C. With any other number of values, the row stays empty, as before. Unlike the strict rule above, it does not ask for a sign after B or E.

We measured it on the text-only rows (`text_only` true) of the first `high_quality` file, in English, Catalan and Spanish: 2,277 rows. We ran OCR on the GPU again for all of them and parsed the same OCR output with the old and the new parser. The other three files have no rows in these languages.

| Language | Rows | 5 options, old parser | 5 options, new parser | Recovered | Lost | Changed |
| --- | --- | --- | --- | --- | --- | --- |
| Catalan | 811 | 624 | 713 | 89 | 0 | 0 |
| English | 811 | 599 | 697 | 98 | 0 | 0 |
| Spanish | 655 | 502 | 574 | 72 | 0 | 0 |
| All | 2,277 | 1,725 (75.8%) | 1,984 (87.1%) | 259 | 0 | 0 |

- **Recovered:** empty with the old parser, five options with the new one. That is 259 of the 552 empty rows (47%), more than the 29% estimated from the sample above. The sample mixed text-only rows and rows with a figure, so the two shares are not directly comparable.
- **Lost or changed:** no row with five options lost them or got a different value.
- **Check between languages.** For each recovered row, we compared B and C with the same problem in the other languages. Where all versions are numbers, B agrees in 171 of 173 cases and C in 185 of 186. The 3 differences can come from this row or from the other language; we did not check them. Options in words cannot be compared this way, because of translation.

The old parser on the new OCR output gives 1,725 rows with options, 2 fewer than the 1,727 in the OCR cache for the same rows. This is the same cache difference as in [the limits](#limits-of-these-numbers).

Rows with a figure are not measured yet. The `data/train.jsonl` and `data/val.jsonl` files keep the old options until `prepare_m3kang.py` runs again without the old OCR cache, because the cache stores options already parsed.

## No `A)` label

In 48 of the 300 sampled rows, the parser finds no `A)` label that it accepts. Two causes are possible:

- The OCR drops the label.
- The label is there but in a form the parser rejects. For A, the parser requires one of the signs listed above after the letter.

The script does not tell these two causes apart. To know which one applies, look at the images of these rows.

### Which cause, measured

After the C fix, 293 of the 2,277 text-only rows (English, Catalan, Spanish) are still empty. With no accepted `A)` label is the largest group, 76 rows. We looked at the OCR boxes of these 76 rows:

| What the OCR returns | Rows |
| --- | --- |
| A box with the letter A alone, no sign | 48 |
| A box with A and a number, no sign | 4 |
| No A at all: the OCR drops it | 24 |

So in most of these rows the label is there and the parser rejects it. 65 of the 76 rows have a `B)` label.

In 20 of the 48 rows with a bare A, the D label also has no sign and the C label is missing, for example (made up) `A`, `10`, `B) 20`, `30`, `D`, `40`, `E) 50`. The C fix asked for a D with a sign, so it did not apply.

### The A fix, measured

`parse_options` now tries the labels in two passes:

1. First, as before, it starts only at an `A` followed by a sign.
2. Only if no sequence A to E completes, it also starts at an A without a sign: the A alone, or the A followed by a number. This is the rule the parser already used for B to E.

A row that the first pass reads cannot change. A figure label "A" is accepted only if B to E follow it. The C fix now also accepts a D without a sign.

Measured on the same OCR output as the C fix (2,277 text-only rows):

| Language | Rows | 5 options before | 5 options after | Recovered | Lost | Changed |
| --- | --- | --- | --- | --- | --- | --- |
| Catalan | 811 | 713 | 729 | 16 | 0 | 0 |
| English | 811 | 697 | 717 | 20 | 0 | 0 |
| Spanish | 655 | 574 | 586 | 12 | 0 | 0 |
| All | 2,277 | 1,984 (87.1%) | 2,032 (89.2%) | 48 | 0 | 0 |

Check between languages: in the recovered rows, 128 of 135 numeric options agree with the same problem in the other languages. The 7 differences are stacked fractions, read for example (made up) as `1 14` in one language and `14` in another. This is the [numeric option of a different length](#a-numeric-option-has-a-different-length-in-another-language), not an error of the new rule.

## PP-OCRv5 compared with PP-OCRv4

`prepare_m3kang.py` uses `rapidocr_onnxruntime`, which runs the PP-OCRv4 models. We ran the newer PP-OCRv5 models on the same 2,277 text-only rows and parsed both outputs with the same parser (with the C and A fixes).

- **PP-OCRv4:** `rapidocr_onnxruntime` 1.4.4, its default models.
- **PP-OCRv5:** `rapidocr` 3.10, mobile text detector and the recognizer for Latin scripts (it reads accents). The server detector ran out of memory on an 8 GB GPU.
- Both on the GPU with `onnxruntime-gpu`. PP-OCRv5 ran at about 5 rows per second.

`laptop/ocr_boxes.py` runs each engine and saves the raw OCR boxes under `data/interim/`; its `compare` command gives the counts below.

| Language | Rows | 5 options, v4 | 5 options, v5 | Only v5 | Only v4 | Both | Both, values differ |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Catalan | 811 | 729 | 760 | 71 | 40 | 689 | 109 |
| English | 811 | 717 | 760 | 82 | 39 | 678 | 98 |
| Spanish | 655 | 586 | 610 | 58 | 34 | 552 | 83 |
| All | 2,277 | 2,032 (89.2%) | 2,130 (93.5%) | 211 | 113 | 1,919 | 290 |

"Values differ" ignores spaces, `,` and `.`. 6 of the 290 rows differ only in the minus sign (`-` or `−`).

**Check between languages.** Over all rows with five options, 98.5% of the numeric options of PP-OCRv4 agree with the other languages (2,876 of 2,920), against 99.4% for PP-OCRv5 (3,015 of 3,034).

**What differs.** In the rows that both engines read, PP-OCRv5 keeps superscripts, units and signs that PP-OCRv4 drops or turns into digits. For example (made up), `x²` instead of `x2`, `20 €` instead of `20`, `0` instead of the letter `O`. It also adds fewer stray digits, such as `1 10` for `10`. Its own errors: stray characters (`15°$`), the two numbers of a stacked fraction in the other order, and, once, Greek letters for digits.

**Manual review (by Claude).** We looked at 20 images, chosen at random with seed 1, and compared each engine's options with the image:

| Sample | Rows | Result |
| --- | --- | --- |
| Both read five options, values differ | 12 | v5 closer to the image in 6, v4 in 3, both wrong in 3. All five right: v5 in 4 rows, v4 in 3 |
| Only v5 reads five options | 4 | v5 right in 3; the fourth has stacked fractions, read wrong |
| Only v4 reads five options | 4 | v4 right in 3; the fourth has one wrong option |

With 20 rows this shows the kinds of difference, not exact rates.

**Combining the engines.** Taking the PP-OCRv5 options when it reads five, and the PP-OCRv4 options otherwise, gives five options in 2,243 of the 2,277 rows: **98.5%** (Catalan 98.6%, English 98.5%, Spanish 98.3%). The 113 rows that only PP-OCRv4 reads are mostly right, so dropping PP-OCRv4 would lose them.

## A numeric option has a different length in another language

58 numeric options have a different length in one language than in the others. For example (made-up values), `17` in one language and `1 17` in another.

One likely cause is in the parser. It takes every box after a label until the next label, even boxes from other lines, such as labels in a figure. Another cause is an OCR misread that adds or drops a digit. The script does not tell these apart.

These errors do not empty the row. They give the model a wrong option value.

## All differences between languages

Of the 823 problems with options in all three languages, 609 (74.0%) have the same options in every language. The other 214 problems differ in 427 options:

| Kind of difference | Options | Error? |
| --- | --- | --- |
| Text in all languages | 299 | Not known: translation or OCR |
| A number with a different length | 58 | Yes, in at least one language |
| A number in one language, text in another | 53 | Not known |
| Only spaces or the decimal comma | 14 | No: a format difference |
| A number with the same length but different digits | 2 | Yes, in at least one language |
| A number with a `/` in at least one language | 1 | Yes |

We did not check the 299 text differences one by one. Some are translations and some can be OCR errors.

## Coverage in the validation set, by stratum

The validation set has 789 rows: 281 problems, each in up to three languages. We use it to score models locally. The official score comes from a hidden test set (see [section 13.3 of the guide](BOARD_SETUP.md#133-ideas-to-reason)).

Coverage in the validation set is 60.8% (480 of 789 rows), lower than the 63.4% of all rows. Here too, a row has all five options or none.

The table splits the rows into four strata (groups): text-only or with a figure, and with options or empty.

| Validation rows | With the 5 options | Empty | Total |
| --- | --- | --- | --- |
| Text-only | 256 | 93 | 349 |
| With a figure | 224 | 216 | 440 |
| All | 480 | 309 | 789 |

The clean stratum is **text-only rows with all five options** (256 rows). In these rows, the prompt holds what the model needs: the full question and the five options. A model that is better than guessing should show it here first. In the other strata, a wrong answer can come from a missing option or a missing figure, not from the model. The manual review below shows that some rows of the clean stratum still have wrong options.

## Manual review of a sample (by Claude)

The validation table was first reported by another Claude agent that checked the OCR results earlier on 2026-11-14. To confirm it and the script counts, we reviewed a sample image by image, not by script. The reviewer was Claude, the coding agent of this project, reading each image. No person checked the images.

**The validation table.** We counted the strata again by a second path. That path reads the dataset file and the OCR cache (`data/.ocr_cache.jsonl`) directly and applies the train and validation split rule of `prepare_m3kang.py` again. It gives the same counts as the table above: 256, 93, 224 and 216 rows, 789 in total.

**15 rows of the clean stratum.** We chose 15 text-only validation rows with all five options at random (seed 1). We compared the five stored options with the image.

| Result | Rows | Wrong options |
| --- | --- | --- |
| All five options match the image | 12 | 0 |
| An extra digit in front of a value, not in the image | 1 | 2 |
| A box from another option added to a value | 1 | 1 |
| Superscript exponents read as normal digits | 1 | 5 |
| Total | 15 | 8 of 75 |

A made-up example of the last kind: a power such as 2⁷ stored as `27`.

So 12 of 15 clean rows (80%) give the model the right options, and 67 of 75 options (89%) are right. A wrong option can make a correct answer impossible to pick. The clean stratum is therefore not fully clean: about one row in five has at least one wrong option. With 15 rows, this estimate is rough.

**5 empty text-only rows.** We chose 5 text-only validation rows with no options at random (seed 1). This sample is separate from the 300 rows above. We ran OCR on them again to see where the parser stops.

| Where the parser stops | Rows | What the image shows |
| --- | --- | --- |
| After B (no C label) | 2 | Plain text options, one with formulas |
| No `A)` label | 1 | Stacked fractions |
| After D | 1 | Plain numbers |
| Five labels, at least one with no value | 1 | Plain numbers, not pictures |

None of the 5 rows has picture options. The last row matters: it shows that the "five labels, at least one with no value" class can hold rows with text options. So the 52 rows of that class are not an exact count of picture options. Picture options can also fall into the other classes, for example when the OCR finds no `A)` label.

The images of the reviewed rows are in `data/interim/manual_review/`, which Git ignores.

## What this means for improving option reading

On the text-only rows in English, Catalan and Spanish (2,277 rows), the measured steps add up:

| Step | Rows with five options |
| --- | --- |
| Old parser, PP-OCRv4 | 1,725 (75.8%) |
| [C fix](#the-fix-measured) | 1,984 (87.1%) |
| [A fix](#the-a-fix-measured) | 2,032 (89.2%) |
| [PP-OCRv5](#pp-ocrv5-compared-with-pp-ocrv4) | 2,130 (93.5%) |
| PP-OCRv5, PP-OCRv4 when v5 reads no options | 2,243 (98.5%) |

The two parser fixes need no new model. PP-OCRv5 also reads the option values better (see the check between languages and the manual review). None of these steps is measured yet on rows with a figure, or in `data/train.jsonl` and `data/val.jsonl`.

The other improvements are not measured yet:

- **Take only boxes on the label's line**, or on the line just below it. This can fix some of the 58 numeric options of different length.
- **Read stacked fractions.** Both engines read a fraction as two numbers, and PP-OCRv5 sometimes swaps them.
- **Crop the image before OCR**, as the guide suggests. This removes figure text that can be added to an option.

A LaTeX OCR, PP-FormulaNet, was tested on options with words, units and simple formulas, not on fractions, and was not adopted: see the [experiment report](experiments/2026-11-ppformulanet.md).

## Limits of these numbers

- One file of the dataset and three languages. Other files or languages can fail differently.
- The empty-row results come from a sample of 300, not from all 1,779 empty rows.
- There is no correct list of options to compare against. The comparison between languages misses an error that is the same in all three languages. So the fraction mode (one case) can be more common than it looks.
- The manual review covers 20 images. It shows the kinds of error, not their exact rates.
- `prepare_m3kang.py` reuses the OCR cache, `data/.ocr_cache.jsonl`. Rows cached by an earlier run keep that run's result, which can come from the CPU or from an older parser.
- One sampled row reaches all five labels when we run OCR again, but its stored result is empty. We ran the script three times on the GPU and got the same counts each time, so this difference most likely comes from the cache, not from the OCR.
