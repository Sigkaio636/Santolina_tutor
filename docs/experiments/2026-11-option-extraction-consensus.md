# Experiment: reading the five options, checked across languages

This report records which way of reading the answer options A to E gives the most rows with all five options right, and how far a check between languages can tell right options from wrong ones. It is for the team and the datathon judges. Laptop run, 2026-11-14, branch `exp/decider-0.8b`.

The answer options of a Kangaroo maths problem ([M3Kang](https://huggingface.co/datasets/qualcomm/M3Kang)) are only in the problem image. We read them with OCR (optical character recognition: it reads text from an image) and a parser that finds the labels `A)` to `E)`. [OCR failure modes](../OCR_FAILURE_MODES.md) explains this pipeline and how many rows it reads. This report asks whether what it reads is right.

Some words on this page:

- A **row** is one problem in one language. A **problem** is one `id`. The same problem is in up to 100 languages.
- **v4** and **v5** are the two OCR engines, PP-OCRv4 and PP-OCRv5, described in [PP-OCRv5 compared with PP-OCRv4](../OCR_FAILURE_MODES.md#pp-ocrv5-compared-with-pp-ocrv4).
- An **arm** is one way of reading the options: an engine, a parser, and a rule to combine them.
- The **baseline** is the best arm before this experiment: v5, and v4 when v5 reads no options.
- A **language-free option** is a number, a formula or a value with a unit, such as (made up) `12 cm` or `x + 3`. It should be the same in every language. An option in words is translated, so it is not language-free.
- The **gold sample** is 100 rows whose options Claude, the coding agent of this project, wrote down from the image. No person checked them.

## Summary

- **About 4 rows in 5 have all five options right.** On the gold sample, the baseline is right on all five options in 81 of 100 rows (95% interval 72% to 90%, by problem). The best arm is right in 82.
- **The check between languages misses most errors.** The option lines are typeset the same way in every language, so OCR makes the same misreading in every language. Of the 46 wrong language-free options in the gold sample, 40 agree with the other languages. The check flags 6. So agreement between languages is not proof that an option is right.
- **The main remaining errors are maths layout.** 11 of the 15 problems with a wrong option in the gold sample have a stacked fraction read as two numbers, or an exponent read as a normal digit. In the full data, 711 rows have an option that is two bare numbers, a likely fraction.
- **Decision: adopt the format fusion (arm 5).** It takes the v5 option, and the v4 option instead where the v5 option fails a format check and the v4 option passes. It cannot change a row that passes the checks. It changes 142 options in 21,181 rows, and gains 1 row on the gold sample. The gain is small.
- **Not adopted:** the parser that takes only boxes on the label's line (it changes no row), the choice of engine by the other languages, and the repair of options by the other languages (on the gold sample it fixes 2 options and breaks 2).
- **The fallback to v4 is safe.** In 19 of 20 gold rows that only v4 reads, all five options are right. When both engines read five options and disagree, v5 is right in 13 of 20 rows and v4 in 2.
- **Coverage holds over 104 languages.** In the 20,798 rows in a Latin script, the baseline reads five options in 98.9%. Before, it was measured only in English, Catalan and Spanish (98.5%).

## Why we ran it

Earlier work counted the rows with five options: coverage. Coverage does not say whether the options are right. Only 4 of the 113 rows that come from the v4 fallback were checked against the image.

Every M3Kang problem is in many languages. In the rows with `text_only` true, a problem is in 2 to 100 languages, 24 at the median. The correct letter, `label`, is the same in every language for all 811 problems, so the order A to E does not change between languages. A number or a formula does not change either. So option C of one row should match option C of the same problem in other languages. We tested how far this check can replace a reading of the image.

## Question and decision rule

**Question:** which arm gives the most rows with five options that are right and well formed, in the text-only rows of M3Kang?

We fixed the rule before the run.

**Valid row.** A row is valid when it meets all three conditions:

1. it has five options;
2. it passes all format checks (below);
3. every language-free option agrees with the other languages of the same problem.

For condition 3, only the other languages count; the row itself does not vote. An option counts only when at least 3 other languages have a language-free value for it. The value with the most votes wins. Both engines vote, so the reference is the same for every arm.

**Rule.** An arm replaces the baseline when it meets both conditions:

1. More valid rows than the baseline. Either the two 95% intervals do not overlap, or an exact McNemar test on the paired rows gives p < 0.05.
2. On the gold sample, at most 2 points lower than the baseline.

Arms that use the other languages to pick or repair options (arms 6 and 7) are scored on the gold sample only. Scoring them by agreement with the other languages would reward them for the signal they use.

**Format checks.** A row fails when:

- an option is empty;
- a value holds another label, such as (made up) `20 C) 30`;
- two options are the same;
- the five options are not of the same kind (number or formula, or words), with one exception allowed;
- a value has more than 40 characters, a sign of question text in an option;
- a value has stray characters: a `$` with no number beside it, a lone `°`, or a Greek or Cyrillic letter (other than π) in a number.

**Normalization between languages.** Before two options are compared:

- superscripts become `^` (`x²` is `x^2`);
- all dashes become `-`;
- a decimal comma equals a decimal point;
- thousands separators are removed (`1 000`, `1.000`, `1'000`);
- units are removed (cm, m, km, kg, g, ml, l, h, min, s, €, $, %, °).

A fraction `a/b`, or two numbers `a b`, is read as the pair {a, b} in either order, because v5 sometimes swaps the two numbers of a stacked fraction.

## What we compared

**Data.** All 21,181 rows of the four `high_quality` files of M3Kang that have `text_only` true: 811 problems in 108 languages. We report rows in a Latin script (20,798 rows, 104 languages) apart from Chinese, Japanese, Korean and Arabic (383 rows).

**Engines.** We ran both engines on every row, on the GPU, with the same versions as before:

- v4: `rapidocr_onnxruntime` 1.4.4;
- v5: `rapidocr` 3.10.0, mobile text detector, recognizer for Latin scripts (also on the non-Latin rows).

We re-ran both engines on 50 rows that were already done. The text, the box positions and the parsed options were identical. So the new rows and the old rows come from the same engines.

**Pilot.** We ran v5 on 3 rows per language (322 rows). 290 of them had five options. The failures were spread over the languages. No row had a label form that the parser does not accept, such as `a)`, `(A)` or `①`. So the parser was not changed for other languages.

**Arms.**

| # | Arm | Uses other languages |
| --- | --- | --- |
| 1 | v4, current parser (with the C and A fixes) | no |
| 2 | v5, current parser | no |
| 3 | **Baseline:** v5, and v4 when v5 reads no options | no |
| 4 | Line parser: a value takes only boxes on its label's line or the line below (4a v4, 4b v5, 4c v5 then v4) | no |
| 5 | Format fusion: arm 3, then per option the v4 value where the v5 value fails a format check and the v4 value passes | no |
| 6 | Choice by the other languages: per row, the engine whose options agree more with the other languages | yes |
| 7 | Repair: arm 3, then an option that disagrees with at least 80% of at least 5 other languages takes the majority value | yes |

**Gold sample.** 100 rows, chosen with a fixed seed before any arm was scored:

- 60 rows, one in each of 60 languages chosen at random. This is not a random draw of rows: it spreads the sample over languages.
- 20 rows where both engines read five options and disagree.
- 20 rows that only v4 reads.

The 100 rows are 81 distinct problems in 74 languages. A problem that appears twice often has the same error twice. So the intervals below resample whole problems.

Claude wrote each option from a crop of the image: the bottom part, from just above the `A)` label. It did not see what either engine read. An option is right when it equals the gold value after these steps: remove spaces, treat a superscript as `^`, treat a decimal comma as a point. A stacked fraction read as (made up) `4 9` is wrong. Its gold value is `4/9`.

## Results

### Rows in a Latin script (20,798)

| Arm | 5 options | Pass format | Options that agree | Valid | 95% interval | vs baseline |
| --- | --- | --- | --- | --- | --- | --- |
| 1 v4 | 89.7% | 86.9% | 97.1% | 79.5% | 76.6–82.3 | +458 / −2,974 |
| 2 v5 | 93.6% | 90.5% | 98.8% | 86.9% | 84.4–89.4 | +0 / −981 |
| 3 Baseline | 98.9% | 95.5% | 98.8% | 91.6% | 89.4–93.5 | — |
| 4c Line parser | 98.9% | 95.5% | 98.8% | 91.6% | 89.4–93.5 | +0 / −0 |
| **5 Format fusion** | **98.9%** | **96.1%** | **98.8%** | **92.0%** | **89.9–93.9** | **+85 / −0, p < 0.001** |

"Options that agree" counts the language-free options that the check can test. "vs baseline" gives the rows valid only in this arm and the rows valid only in the baseline.

- **96.6% of the options are language-free**, so the check covers almost all options of these text-only rows.
- **The line parser changes no row.** Over 42,362 parses (both engines), it gives the same options as the current parser. The stray boxes that end up in a value are on the label's own line, not on other lines.
- **The rule picks arm 5, but its p-value is weak evidence.** Arm 5 only swaps an option that fails a format check. A valid row cannot fail one, so the −0 holds by construction. The format checks are part of the valid-row test, so the +85 is partly built in. The independent evidence is this:
  - of the 142 options it swaps, 105 agree with the other languages, 32 disagree, and 5 cannot be checked;
  - on the gold sample it gains 1 row (see below).
- **Valid is an upper bound on right rows.** The gold sample shows rows that pass every check and are still wrong.

Format checks that fail, among rows with five options (baseline):

| Check | Rows | Share |
| --- | --- | --- |
| Not of the same kind | 368 | 1.8% |
| Two options the same | 201 | 1.0% |
| Stray characters | 107 | 0.5% |
| Over 40 characters | 58 | 0.3% |
| Another label in a value | 0 | 0% |

The 99th percentile of option length is 13 characters, so the limit of 40 catches only long leaks. Arm 5 brings the stray characters down from 107 rows to 3, and the repeated options from 201 to 174.

### Rows in another script (383)

The baseline reads five options in 96.6% of these rows, and 86.4% are valid. Here v4 reads five options more often than v5 (94.0% against 90.1%). We ran v5 with its Latin recognizer on these rows; a recognizer for each script was not tested.

### Gold sample (100 rows)

| Arm | All 5 right | Options right | Random rows (60) | Engines disagree (20) | Only v4 reads (20) |
| --- | --- | --- | --- | --- | --- |
| 1 v4 | 64 | 385 of 500 | 43 | 2 | 19 |
| 2 v5 | 58 | 326 of 500 | 45 | 13 | 0 |
| 3 Baseline | 81 | 441 of 500 | 49 | 13 | 19 |
| 4c Line parser | 81 | 441 of 500 | 49 | 13 | 19 |
| **5 Format fusion** | **82** | **442 of 500** | **49** | **14** | **19** |
| 6 Choice by other languages | 82 | 441 of 500 | 49 | 14 | 19 |
| 7 Repair | 82 | 441 of 500 | 49 | 14 | 19 |

- **95% intervals, by problem:** baseline 72% to 90%, arm 5 73% to 91%.
- **Arm 7, the repair, touched 7 gold options.** It fixed 2, broke 2, and left 3 wrong. It changes 863 options in the full data, and the gold sample cannot vouch for them. It is not adopted.
- **A looser score changes little.** It compares values without units and treats `×`, `·` and `*` as the same sign. The baseline then has all five options right in 82 rows.

### What the check between languages catches

For the baseline, on the language-free options of the gold sample that the check can test:

| | Right in the image | Wrong in the image |
| --- | --- | --- |
| Agrees with the other languages | 428 | 40 |
| Disagrees | 2 | 6 |

When an option disagrees, it is wrong in 6 of 8 cases. But only 6 of the 46 wrong options disagree. 40 wrong options agree, because the same misreading happens in every language: the option line is typeset alike.

The pair rule for fractions accepts a fraction read as two numbers. 1,748 options of the baseline agree only because of this rule. Two post-hoc checks on the rows in a Latin script, not part of the fixed rule:

| | Baseline valid | Arm 5 valid |
| --- | --- | --- |
| As fixed before the run | 91.6% | 92.0% |
| Two bare numbers counted as a format failure | 89.8% | 90.2% |
| Without the pair rule for fractions | 91.0% | 91.4% |

An exponent read as a normal digit, such as (made up) `y3` for y³, passes every check. Only the gold sample finds it.

### Why rows are wrong on the gold sample

The 19 wrong rows of the baseline are 15 distinct problems:

| Error | Problems | Rows |
| --- | --- | --- |
| Stacked fraction read as two numbers, sometimes swapped, such as (made up) `9 4` for 4/9 | 6 | 8 |
| Exponent read as a normal digit, such as (made up) `x3` for x³ | 5 | 6 |
| No options: neither engine finds all labels | 1 | 2 |
| Stray digit in front of a value, such as (made up) `4 25 m` | 1 | 1 |
| Stray character after a value, such as (made up) `15°$` | 1 | 1 |
| A product sign dropped, such as (made up) `√2 √3` for √2·√3 | 1 | 1 |

Arm 5 fixes the stray character.

## Decision

We adopt arm 5, the format fusion, in place of the baseline. It meets the rule, it cannot break a row that passes the checks, and on the gold sample it gains 1 row. The gain is small: 85 rows in 20,798.

We do not adopt:

- the line parser: it changes no row;
- the choice of engine by the other languages: on the gold sample it does no better than arm 5;
- the repair by the other languages: on the gold sample it fixes as many options as it breaks.

`laptop/prepare_m3kang.py` still reads with PP-OCRv4 only. Moving it to arm 5 means running both engines in data preparation. That is a separate change.

## Next step

**Read fractions and exponents from the box positions.** Both errors are layout: a fraction is two boxes, one above the other, and an exponent is a small box raised to the right of a digit. Both engines return the box positions, so a parser rule can join them as `a/b` or `x^n`. The gold sample and the post-hoc count of two bare numbers (711 rows) can measure such a rule. [PP-FormulaNet](2026-11-ppformulanet.md) was too slow and was not tested on fractions.

## Limitations

- **The gold sample is 100 rows, by Claude.** No person checked it. With 100 rows, a gain of 1 row is not a measured difference.
- **The gold sample was scored three times.** The decision rule and the arms did not change between runs, but these did:
  1. The first crops cut off the top of stacked fractions. We widened them before writing any gold value. The rows did not change.
  2. A bug in the gold normalization read the commas of a set, such as (made up) `{1,4,6,8}`, as decimal commas, so one right row scored as wrong. Fixing it moved the baseline from 80 to 81.
  3. The repair broke ties between two equal majorities by chance. It now skips a tie. This moved arm 7 from 79 to 82, so its gold score is not evidence for it.
- **Agreement between languages is not correctness.** See [What the check between languages catches](#what-the-check-between-languages-catches).
- **Text-only rows only.** Rows with a figure are not measured.
- **One recognizer for all scripts.** v5 used its Latin recognizer on Chinese, Japanese, Korean and Arabic rows too.
- **Fixed format limits.** The limit of 40 characters and the list of units were fixed before the run, not tuned.

## Appendix: reproducibility

| Item | Value |
| --- | --- |
| Date and branch | 2026-11-14, `exp/decider-0.8b`; parser as in commit `b8e5358` |
| Data | M3Kang `high_quality`, the 4 files, rows with `text_only` true: `data/raw_txto_yes/*.parquet`, 21,181 rows |
| Environments | `~/.venvs/ocr-v4` and `~/.venvs/ocr-v5`, Python 3.12, `onnxruntime-gpu` 1.32.0; versions in `data/interim/optx/freeze_v4.txt` and `freeze_v5.txt` |
| Boxes | `data/interim/optx/boxes_all_v4.jsonl` and `boxes_all_v5.jsonl` |
| Gold sample | `data/interim/optx/gold_pick.json` (seed 7) and `options_gold.json` |
| Code | `laptop/ocr_boxes.py` (boxes), `laptop/option_consensus.py` (everything else) |
| Output | `data/interim/optx/score_all.txt`: counts only, no problem text |

Everything under `data/` holds M3Kang text, which is for research use only, and Git ignores it.

```bash
~/.venvs/ocr-v5/bin/python laptop/ocr_boxes.py dump --engine v5 --languages all \
    --out data/interim/optx/boxes_all_v5.jsonl data/raw_txto_yes/*.parquet
~/.venvs/ocr-v4/bin/python laptop/ocr_boxes.py dump --engine v4 --languages all \
    --out data/interim/optx/boxes_all_v4.jsonl data/raw_txto_yes/*.parquet
python laptop/option_consensus.py --selftest
python laptop/option_consensus.py gold-pick      # then write options_gold.json by hand
python laptop/option_consensus.py score --per-language
```

The check that reruns 50 rows uses `ocr_boxes.py dump --keys-file`. The pilot uses `option_consensus.py pilot`.
