# Experiment: reading the five options, checked across languages

This report compares ways of reading the answer options A to E. It asks which way gives the most rows that pass automatic checks, and how many of those rows are right on a gold sample. The copilot model needs the options to pick an answer. The report also measures how well a check between languages tells right options from wrong ones. It is for the team and the datathon judges. Laptop run, 2026-11-14, branch `exp/decider-0.8b`.

[M3Kang](https://huggingface.co/datasets/qualcomm/M3Kang) is a dataset of problems from the Kangaroo maths contest, an international multiple-choice competition for school students. The five answer options of a problem are only in the problem image. We read them with OCR (optical character recognition: it reads text from an image) and a parser that finds the printed letters `A)` to `E)`. [OCR failure modes](../OCR_FAILURE_MODES.md) explains this pipeline and how many rows it reads. This report asks whether what it reads is right.

Some words on this page:

- A **row** is one problem in one language. A **problem** is one `id`. The same problem is in up to 100 languages.
- A **text-only** row has `text_only` set to true in M3Kang: its question needs no figure. Its options are still only in the image.
- **v4** and **v5** are the two OCR engines, PP-OCRv4 and PP-OCRv5, described in [PP-OCRv5 compared with PP-OCRv4](../OCR_FAILURE_MODES.md#pp-ocrv5-compared-with-pp-ocrv4).
- An **arm** is one way of reading the options: an engine, a parser, and a rule to combine them. [Arms](#arms) lists them.
- The **baseline** is the best arm before this experiment: v5, and v4 when v5 reads no options.
- **Coverage** is the share of rows with five options.
- A **language-free option** is a number, a formula or a value with a unit, such as (made up) `12 cm` or `x + 3`. It should be the same in every language. An option in words changes with the translation, so it is not language-free.
- The **check between languages** compares a language-free option with the same option of the same problem in the other languages.
- A **valid row** has five options that pass the [format checks](#format-checks) and the check between languages ([details](#valid-row)).
- A **stacked fraction** has its numerator above its denominator, with a bar between them.
- The **gold sample** is 100 rows whose options Claude, the coding agent of this project, wrote down from the image. Each value it wrote is a **gold value**. No person checked them.

## Summary

- **Recommendation: the format fusion (arm 5)**. It takes the v5 option, and the v4 option where the v5 option fails a [format check](#format-checks) and the v4 option passes. It changes 140 options in 130 of the 20,798 rows in a Latin script, all in rows that already fail a check. On the gold sample it raises the rows with all five options right from 81 to 82 of 100. The evidence is weak: [Decision](#decision) says why.
- **About 4 in 5 gold rows have all five options right**. In the 60 gold rows spread over 60 languages, the baseline is right on all five options in 49. Over all 100 gold rows it is right in 81. The other 40 come from two groups picked on purpose: 20 rows where the engines disagree and 20 rows that only v4 reads. So 81 of 100 is not a rate for all the data.
- **The check between languages misses most errors**. Of the 46 wrong options in the gold sample that the check can test, 40 agree with the other languages. The likely cause: the option lines look alike in every language, so OCR makes the same misreading in every language. So agreement between languages is not proof that an option is right.
- **The main remaining errors are maths layout**. In the gold sample, 15 problems have a wrong option. In 11 of them, OCR reads a stacked fraction as two numbers, or an exponent as a normal digit. In the rows in a Latin script, 695 of the 20,798 rows (3.3%) have an option that is two bare numbers, a likely fraction.
- **The v4 rows of the baseline are mostly right**. In 19 of 20 gold rows that only v4 reads, all five options are right. When both engines read five options and disagree, v5 is right in 13 of 20 rows and v4 in 2.
- **Coverage holds over 104 languages**. In the 20,798 rows in a Latin script, the baseline reads five options in 98.9%. Over the 72 languages with at least 50 rows, it ranges from 97.6% to 100%. Before, we measured it only in English, Catalan and Spanish ([98.5%](../OCR_FAILURE_MODES.md#pp-ocrv5-compared-with-pp-ocrv4)).

## Why we ran it

Earlier work measured coverage. Coverage does not say whether the options are right. In English, Catalan and Spanish, 113 rows come from the v4 fallback. An earlier review [checked only 4 of them](../OCR_FAILURE_MODES.md#pp-ocrv5-compared-with-pp-ocrv4) against the image.

Every M3Kang problem is in many languages. In the text-only rows, a problem is in 2 to 100 languages, 24 at the median. A number or a formula does not change with the language. So option C of one row should match option C of the same problem in other languages. This holds if the order A to E is the same. Two facts support it:

- the dataset field `label`, the right answer, has the same letter in every language for all 811 problems
- 98.8% of the options that the check can test agree letter by letter between languages.

We tested how far this check can replace a reading of the image.

## Question and decision rule

**Question:** which arm gives the most rows with five options that pass the checks below? And how many of its rows are right, on the gold sample?

We set the rule, the arms and the checks before the run.

### Arms

| # | Arm | Uses other languages |
| --- | --- | --- |
| 1 | v4, current parser (with the [C fix](../OCR_FAILURE_MODES.md#the-fix-measured) and the [A fix](../OCR_FAILURE_MODES.md#the-a-fix-measured)) | no |
| 2 | v5, current parser | no |
| 3 | **Baseline:** v5, and v4 when v5 reads no options | no |
| 4 | Line parser: a value takes only boxes on its label's line or the line below (4a v4, 4b v5, 4c v5 then v4) | no |
| 5 | Format fusion: arm 3, then the v4 option where the v5 option fails an option check and the v4 option passes (see [Format checks](#format-checks)) | no |
| 6 | Choice by the other languages: per row, the engine whose options agree more with the other languages | yes |
| 7 | Repair: arm 3, then an option takes the majority value of the other languages. Condition: at least 5 other languages have a value, and at least 80% of them vote for it | yes |

### Valid row

A row is valid when it meets all three conditions:

1. it has five options
2. it passes all format checks
3. no language-free option disagrees with the other languages of the same problem.

For condition 3, only the other languages count. The row itself does not vote. The check tests an option only when at least 3 other languages have a language-free value for it. An option that the check cannot test does not fail condition 3. In each other language, both engines vote: the language counts once for each value its engines give. Every value tied for the most languages is the majority. The option agrees when it equals the majority. Because both engines vote, the majority is the same for every arm.

### Rule

An arm replaces the baseline when it meets both conditions:

1. More valid rows than the baseline. Either the two 95% intervals do not overlap, or an exact McNemar test gives p < 0.05. This test compares two arms row by row and uses only the rows where they differ.
2. On the gold sample, its share of rows with all five options right is at most 2 percentage points below the baseline.

Arms 6 and 7 use the other languages to pick or repair options. Scoring them by agreement with the other languages would reward them for the signal they use, so we score them on the gold sample only. The rule set before the run therefore has no test for them. We judged them afterwards, against arm 5 on the gold sample (see [Limitations](#limitations)).

### Format checks

A row fails when:

- an option is empty
- a value holds another printed letter, such as (made up) `20 C) 30`
- two options are the same
- the five options are not of the same kind (number or formula, words, other). The check allows one option of another kind
- a value has more than 40 characters, a sign of question text in an option
- a value has stray characters. These are a `$` with no number beside it, a lone `°`, or a Greek or Cyrillic letter (other than π) in a number.

Arm 5 applies four of these checks to one option: empty, another printed letter, more than 40 characters, stray characters. It also replaces a repeated option with the v4 option when that option is not already in the row and passes those four checks.

### Normalization between languages

Before the check compares two options, it applies these steps:

- superscripts become `^` (`x²` is `x^2`)
- all dashes become `-`
- a decimal comma equals a decimal point
- it removes thousands separators (`1 000`, `1.000`, `1'000`)
- it removes units, with a squared or cubed mark after them. The units are mm, cm, dm, m, km, kg, g, ml, l, h, min, s, €, euro, euros, eur, $, %, °.

The check reads a fraction `a/b`, or two numbers `a b`, as the pair {a, b} in either order. The reason: v5 sometimes swaps the two numbers of a stacked fraction.

## What we compared

**Data.** All 21,181 text-only rows of the `high_quality` part of M3Kang (its 4 files): 811 problems in 108 languages. We report the rows in a Latin script (20,798 rows, 104 languages) separately from the rows in Chinese, Japanese, Korean and Arabic (383 rows). In each of the 104 languages, at least 98.8% of the letters in the questions are Latin.

**Engines.** We ran both engines on every row, on the GPU, with the [same versions as the earlier runs](../OCR_FAILURE_MODES.md#pp-ocrv5-compared-with-pp-ocrv4):

- v4: `rapidocr_onnxruntime` 1.4.4
- v5: `rapidocr` 3.10.0. Its mobile text detector finds the text boxes, and its recognizer for Latin scripts reads them. We used the Latin recognizer on the non-Latin rows too.

We re-ran both engines on 50 rows that were already done. The text, the box positions and the parsed options were identical. So the new rows and the old rows come from the same engines.

**Pilot.** We ran v5 on 3 rows per language, 322 rows (one language has a single row). 290 of them had five options. The failures were spread over the languages. A script searched the OCR text for label forms that the parser does not accept, such as `a)`, `(A)` or `①`, and found none. So the parser was not changed for other languages.

**Gold sample.** 100 rows. A script chose them with a fixed seed before we scored any arm:

- 60 spread rows: one row in each of 60 languages chosen at random. This is not a random draw of rows: it spreads the sample over languages.
- 20 rows where both engines read five options and disagree.
- 20 rows that only v4 reads.

The 100 rows are 81 distinct problems in 74 languages. A problem that appears twice often has the same error twice. So every 95% interval in this report comes from a bootstrap with 1,000 draws that resamples whole problems, not single rows.

Claude wrote each option from a crop of the image: the bottom part, from just above the `A)` letter. It did not see what either engine read. An option is right when it equals the gold value after these steps:

- Unicode normalization (NFKC)
- superscripts as `^`, and all dashes as `-`
- lower case, no spaces
- a decimal comma as a point.

A stacked fraction read as (made up) `4 9` is wrong. Its gold value is `4/9`.

## Results

### Rows in a Latin script (20,798)

| Arm | 5 options | 5 options, pass format | Options that agree | Valid | Valid, 95% interval | Rows valid only here / only in baseline |
| --- | --- | --- | --- | --- | --- | --- |
| 1 v4 | 89.7% | 86.9% | 97.1% | 79.5% | 76.6%–82.3% | +458 / −2,974 |
| 2 v5 | 93.6% | 90.5% | 98.8% | 86.9% | 84.4%–89.4% | +0 / −981 |
| 3 Baseline | 98.9% | 95.5% | 98.8% | 91.6% | 89.4%–93.5% | — |
| 4c Line parser | 98.9% | 95.5% | 98.8% | 91.6% | 89.4%–93.5% | +0 / −0 |
| **5 Format fusion** | **98.9%** | **96.1%** | **98.8%** | **92.0%** | **89.9%–93.9%** | **+85 / −0, p < 0.001** |

All columns but "Options that agree" are shares of the 20,798 rows. "Options that agree" is the share of the tested language-free options that agree with the other languages. Arms 4a and 4b equal arms 1 and 2 on every measure, so the table omits them. We score arms 6 and 7 on the gold sample only.

- **96.6% of the options are language-free** (99,368 of 102,830 in the baseline), so the check can cover almost all options of these rows.
- **The line parser changes no row**. Over 42,362 parses (both engines), it gives the same options as the current parser. So no stray box comes from two or more lines below the label. Boxes on the label's line or the next line can still be stray.
- **The rule picks arm 5, but the evidence is weak**. Arm 5 only swaps an option that fails a format check, and a valid row passes them all. So the −0 holds by construction and the +85 is partly built in. The p < 0.001 counts rows, but the 85 rows come from 7 problems, and 2 of them give 45. A check added after the run counts problems: 7 gain, and none can lose, for the same reason (exact sign test, p = 0.016). Condition 2 could not fail, because arm 5 changes only 2 gold rows. The independent evidence:
  - of the 140 options it swaps (130 rows, 13 problems), 104 agree with the other languages, 31 disagree, and the check cannot test 5
  - on the gold sample it gains 1 row (see below).

Format checks that fail, among the 20,566 baseline rows in a Latin script that have five options. A row can fail several checks (16 rows do):

| Check | Rows | Share |
| --- | --- | --- |
| Not of the same kind | 358 | 1.7% |
| Two options the same | 196 | 1.0% |
| Stray characters | 106 | 0.5% |
| Over 40 characters | 57 | 0.3% |
| Another printed letter in a value | 0 | 0% |
| An empty option | 0 | 0% |

The 99th percentile of option length is 13 characters, so the limit of 40 catches only long leaks. Arm 5 brings the stray characters down from 106 rows to 3, and the repeated options from 196 to 170.

695 baseline rows have an option that is two bare numbers, such as (made up) `4 9`: a likely stacked fraction. No format check set before the run catches it.

### Rows in another script (383)

The baseline reads five options in 96.6% of these rows, and 86.4% are valid. Here v4 reads five options more often than v5 (94.0% against 90.1%).

### Gold sample (100 rows)

Rows with all five options right, by group (the "Options right" column counts options, of 500):

| Arm | All 100 rows | Options right | Spread rows (60) | Engines disagree (20) | Only v4 reads (20) |
| --- | --- | --- | --- | --- | --- |
| 1 v4 | 64 | 385 of 500 | 43 | 2 | 19 |
| 2 v5 | 58 | 326 of 500 | 45 | 13 | 0 |
| 3 Baseline | 81 | 441 of 500 | 49 | 13 | 19 |
| 4c Line parser | 81 | 441 of 500 | 49 | 13 | 19 |
| **5 Format fusion** | **82** | **442 of 500** | **49** | **14** | **19** |
| 6 Choice by other languages | 82 | 441 of 500 | 49 | 14 | 19 |
| 7 Repair | 82 | 441 of 500 | 49 | 14 | 19 |

- **Arm 7, the repair, changed 7 gold options**. 2 went from wrong to right, 2 from right to wrong, and 3 from one wrong value to another. It changes 863 options in the full data, and the gold sample cannot vouch for them.
- **A looser score changes little**. It compares values without units, and treats `×`, `·`, `*` and a letter `x` between two digits as the same sign. The baseline then has all five options right in 82 rows.

### What the check between languages catches

For the baseline, on the language-free options of the gold sample that the check can test:

| | Right in the image | Wrong in the image |
| --- | --- | --- |
| Agrees with the other languages | 428 | 40 |
| Disagrees | 2 | 6 |

When an option disagrees, it is wrong in 6 of 8 cases. But 40 of the 46 wrong options agree, most likely because the same misreading happens in every language. They cluster in 15 rows of 12 problems. In the 60 spread rows alone, 21 wrong options agree and 3 disagree, about the same share as overall.

The pair rule for fractions accepts a fraction read as two numbers. In the rows in a Latin script, 145 baseline options agree with the pair rule and disagree without it. Two post-hoc checks (chosen after we saw the results, so not part of the rule):

| | Baseline valid | Arm 5 valid |
| --- | --- | --- |
| As set before the run | 91.6% | 92.0% |
| Two bare numbers counted as a format failure | 89.8% | 90.2% |
| Without the pair rule for fractions | 91.0% | 91.4% |

An exponent read as a normal digit, such as (made up) `y3` for y³, passes every check. Only the gold sample finds it.

### Why rows are wrong on the gold sample

The 19 wrong rows of the baseline are 15 distinct problems:

| Error | Problems | Rows |
| --- | --- | --- |
| Stacked fraction read as two numbers, sometimes swapped, such as (made up) `9 4` for 4/9 | 6 | 8 |
| Exponent read as a normal digit, such as (made up) `x3` for x³ | 5 | 6 |
| No options: neither engine finds all printed letters | 1 | 2 |
| Stray digit in front of a value, such as (made up) `4 25 m` | 1 | 1 |
| Stray character after a value, such as (made up) `15°$` | 1 | 1 |
| A product sign dropped, such as (made up) `√2 √3` for √2·√3 | 1 | 1 |

Arm 5 fixes the row with the stray character after a value. That is its 1-row gain on the gold sample.

## Decision

We recommend arm 5, the format fusion, in place of the baseline. It triggers the rule (we tested condition 1 on the rows in a Latin script). But the rule is weak evidence here: see [Results](#rows-in-a-latin-script-20798). It only changes rows that already fail a check. On the gold sample it changed 2 rows and fixed 1, and no row went from right to wrong.

We do not recommend:

- the line parser (arm 4): it changes no row
- the choice of engine by the other languages (arm 6): on the gold sample it ties with arm 5 at 82 of 100. It also needs the other languages, and arm 5 does not
- the repair by the other languages (arm 7): it also ties at 82, but it fixes as many gold options as it breaks.

`laptop/prepare_m3kang.py` still reads with PP-OCRv4 only. Moving it to arm 5 means running both engines in data preparation. That is a separate change.

## Limitations

- **The gold sample is 100 rows, by Claude**. No person checked it. With 100 rows, a gain of 1 row is not a measured difference.
- **Three things changed during the scoring**. The decision rule did not change.
  1. The first crops cut off the top of stacked fractions. We widened them before writing any gold value. The rows did not change.
  2. The gold normalization turned a decimal comma into a point before it removed spaces. So a set read with a space after a comma, such as (made up) `{1, 4,6}`, did not match its gold value `{1,4,6}`. Removing spaces first fixed it, and moved the baseline from 80 to 81.
  3. The repair broke ties between two equal majorities by chance. It now skips a tie. This moved arm 7 from 79 to 82, so its gold score is not evidence for it.
- **No rule for arms 6 and 7 before the run**. We rejected them by a comparison with arm 5 that we chose afterwards.
- **Agreement between languages is not correctness**. See [What the check between languages catches](#what-the-check-between-languages-catches).
- **Text-only rows only**. Rows with a figure are not measured.
- **One recognizer for all scripts**. v5 used its Latin recognizer on Chinese, Japanese, Korean and Arabic rows too.

## Next step

**Read fractions and exponents from the box positions.** Both errors are layout. A fraction is two boxes, one above the other. An exponent is a small box raised to the right of a digit. Both engines return the box positions, so a parser rule can join them as `a/b` or `x^n`. The gold sample and the 695 rows with two bare numbers can measure such a rule. [PP-FormulaNet](2026-11-ppformulanet.md) was too slow, and we did not test it on fractions.

## Appendix: reproducibility

| Item | Value |
| --- | --- |
| Date and branch | 2026-11-14, `exp/decider-0.8b`, parser as in commit `b8e5358` |
| Data | M3Kang `high_quality`, the 4 files, text-only rows: `data/raw_txto_yes/*.parquet`, 21,181 rows |
| Environments | `~/.venvs/ocr-v4` and `~/.venvs/ocr-v5`, Python 3.12, `onnxruntime-gpu` 1.32.0, versions in `data/interim/optx/freeze_v4.txt` and `freeze_v5.txt` |
| Boxes | `data/interim/optx/boxes_all_v4.jsonl` and `boxes_all_v5.jsonl` |
| Gold sample | `data/interim/optx/gold_pick.json` (seed 7) and `options_gold.json` |
| Code | `laptop/ocr_boxes.py` (boxes), `laptop/option_consensus.py` (everything else) |
| Output | `data/interim/optx/score_all.txt`: counts only, no problem text |

The files under `data/` hold M3Kang text, which is for research use only. Git ignores them, except `data/README.md` and `data/sample_problems.jsonl`.

Some numbers come from one-off queries, not from `score`:

- the coverage range per language, the number of languages per problem, the `label` check and the share of Latin letters
- the problems and rows behind the options arm 5 swaps and the rows it gains, and the problem-level sign test
- the rows and problems of the 40 wrong options that agree, and the split in the spread rows
- the 2 gold rows that arm 5 changes.
 `laptop/option_consensus.py` runs in the repository's `.venv`.

```bash
uv venv -p 3.12 ~/.venvs/ocr-v4
VIRTUAL_ENV=~/.venvs/ocr-v4 uv pip install rapidocr_onnxruntime==1.4.4 "onnxruntime-gpu[cuda,cudnn]" pyarrow
uv venv -p 3.12 ~/.venvs/ocr-v5
VIRTUAL_ENV=~/.venvs/ocr-v5 uv pip install "rapidocr==3.10.*" "onnxruntime-gpu[cuda,cudnn]" pyarrow
python laptop/split_text_only.py
~/.venvs/ocr-v5/bin/python laptop/ocr_boxes.py dump --engine v5 --languages all \
    --out data/interim/optx/boxes_all_v5.jsonl data/raw_txto_yes/*.parquet
~/.venvs/ocr-v4/bin/python laptop/ocr_boxes.py dump --engine v4 --languages all \
    --out data/interim/optx/boxes_all_v4.jsonl data/raw_txto_yes/*.parquet
.venv/bin/python laptop/option_consensus.py --selftest
.venv/bin/python laptop/option_consensus.py gold-pick
```

`gold-pick` writes image sheets in `data/interim/optx/gold_sheets/`. Claude read them and wrote `data/interim/optx/options_gold.json` by hand. No script produces that file. Then:

```bash
.venv/bin/python laptop/option_consensus.py score --per-language
```

The check that reruns 50 rows uses `ocr_boxes.py dump --keys-file`. The pilot reads its boxes with `.venv/bin/python laptop/option_consensus.py pilot data/interim/optx/pilot_v5.jsonl`.
