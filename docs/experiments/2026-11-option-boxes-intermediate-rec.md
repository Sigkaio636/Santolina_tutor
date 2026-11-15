# Experiment: label-anchored option boxes and a mid-size recognizer inside them

This report tests a new way to read the five answer options (A to E) of text-only M3Kang
problems. OpenCV finds the box of each option from its label, splits stacked fractions and
exponents, and a small text recognizer reads each piece. No text detector runs.

It follows the [OpenCV crops experiment](2026-11-option-crops-opencv.md) and the
[OCR failure modes](../OCR_FAILURE_MODES.md) page. It is for the team and the datathon judges.
Laptop run, 2026-11-15, branch `exp/decider-0.8b`.

[M3Kang](https://huggingface.co/datasets/qualcomm/M3Kang) is the dataset of Kangaroo maths
problems that the copilot answers. The five answer options are only in the image. This report
shows no problem text and no images; every example value is made up.

## Terms used here

The [OCR failure modes](../OCR_FAILURE_MODES.md#background-how-the-options-are-read) page defines
row, text-only row, coverage and the parser. The
[OpenCV crops experiment](2026-11-option-crops-opencv.md#terms-used-here) defines mask, Otsu
threshold, closing, component, reference box and row OK. New terms:

- **Label**: the letter and parenthesis that start an option, such as `A)`.
- **Value**: what follows the label. It is the part the recognizer reads.
- **Label anchor**: the position of a label, found with a template of the label
  (`cv2.matchTemplate`).
- **Recognizer**: the model that turns one text-line image into characters. It is the second
  half of an OCR engine; the first half, the detector, finds the lines. This experiment uses the
  recognizer alone.
- **2-D split**: OpenCV separates the numerator and denominator of a stacked fraction, and a
  raised exponent, before the recognizer runs. Each piece is read on its own and the value is
  written on one line, for example `3/4` or `x^2`.
- **Gold**: the five options of a row, transcribed from the image. Both gold sets here were
  written by Claude and no person has checked them.

Arms:

| Name | What it is |
|---|---|
| B0 | The box detector of the OpenCV crops experiment: closing 41×3 and repair |
| B1 | The new box detector, anchored on the labels |
| R0 | `latin_PP-OCRv5_rec_mobile`, 1.95 M parameters, the recognizer in use today |
| R1 | `PP-OCRv6_rec_small`, 5.2 M parameters |
| R2 | `PP-OCRv6_rec_medium`, 19 M parameters |
| I0 | Input: the gray crop |
| I1 | Input: binary at Otsu's threshold `t` |
| I2 | Input: gray ink, white above `(t + 255) / 2` |
| I3 | Input: binary at `(t + 255) / 2` |
| line | One read per text line of the value |
| 2d | The 2-D split, then one read per piece |
| P0 | Today's pipeline: PP-OCRv5 on the whole image, PP-OCRv4 if it reads no options |
| P1 | P0 with the masked-region fallback of the OpenCV crops experiment |
| P4 | P0, with the new read for an option where OpenCV saw a fraction or an exponent, or where P0's option fails a format check (`score --selective`) |

## Summary

**Decision: the new pipeline B1 + R1 + 2d on the gray crop reads the options better than today's
pipeline on every measure we have, and it is the candidate to replace it.** It is not in
`prepare_m3kang.py` yet. To run it, see the [option reader guide](../OPTION_READER_GUIDE.md).

| Measure | Today (P0) | New (B1 + R1 + I0 + 2d) |
|---|---|---|
| Gold, 60 rows: rows with all five options right | 56 | 60 |
| Hard gold, 40 rows: rows with all five options right | 7 | 40 |
| All 2,277 rows: rows with five options | 2,243 | 2,277 |
| All 2,277 rows: rows that pass the format checks | 2,181 | 2,251 |

- **The 2-D split is the step that matters.** Without it the same recognizer gets 57 of 60 and
  15 of 40. Almost every remaining error of today's pipeline on the hard rows is a stacked
  fraction.
- **A mid-size recognizer is enough.** R1 (5.2 M) reads every symbol the options use. R2 (19 M)
  is not better and is about 40 times slower. R0 (1.95 M) with the 2-D split reaches 59 to
  60 of 60 and 33 to 38 of 40; it lacks some symbols.
- **Binarizing the crop with Otsu does not help.** Thin strokes sit at about the Otsu level, so a
  hard threshold breaks them. With R1 the binary input loses two options on the hard gold.
  Whitening only the background (I2) gives the same result as the gray crop.
- **Label anchors find five boxes in all 2,277 rows.** B0 finds them in 2,267.
- **Independent check.** We looked at 30 random options where the new pipeline and today's
  disagree, outside the development sample. The new one was right in 28. In the other 2 the
  characters were right and the form was ambiguous. Today's pipeline was wrong in all 30.
- **The hard gold is not a clean test.** Two rules were fixed after looking at its errors. The
  60-row gold and the 30-option check were not used that way.

## Why we ran it

Four measured problems were open:

1. **Boxes.** B0 fails when options are closer than its 41 px kernel, when an option continues
   on a second line, and when a stacked fraction splits the text line. It does not look at the
   labels: it gives the letters A to E by position.
2. **Characters.** The recognizer in use (R0) knows only the superscripts ¹ ² ³. The PP-OCRv4
   recognizer has no `−`, `³` or `€`.
3. **Layout.** A recognizer reads one line. It returns a stacked fraction as two numbers and an
   exponent as a normal digit. In the
   [consensus experiment](2026-11-option-extraction-consensus.md) 695 rows had an option made of
   two bare numbers.
4. **Input.** Every image is a gray JPEG. No experiment had given the OCR a binarized image.

The first idea was to run granite-docling-258M inside each box. It has about 50 times the
parameters of R1 and 130 times those of R0, so it stays here as a reference only. The option
values are short and simple. What they need is a character set with the maths symbols, and
something that handles the two layouts a line recognizer cannot read.

## What we compared

**Data.** The 2,277 text-only rows in English, Catalan and Spanish. For quick runs, a sample
drawn by problem with a fixed seed (53):

| Stratum | Rows | What it is |
|---|---|---|
| gold | 60 | The rows of `options_gold3.json`, 20 per language |
| dev | 174 | 8 problems per level (0 to 7) in the three languages; none is in the gold |
| hard | 60 | Rows where today's pipeline is weak (see below) |

The hard stratum holds 15 rows where P0 reads no options, 20 where PP-OCRv5 gives an option of
two bare numbers, 15 where it gives a non-ASCII character or `^`, and 10 where only PP-OCRv4
reads the options.

**Hard gold.** The gold has few maths layouts: 3 % of its options are fractions and 1.7 % have
an exponent. So 40 rows of the hard stratum were transcribed from sheets of the option band: 20
two-number rows, 10 non-ASCII rows, 5 rows with no options and 5 PP-OCRv4-only rows. The
transcription was done before any engine output on those rows was looked at. Fractions are
written `a/b`, exponents `x^2`, and a numerator of several terms goes in parentheses.

**Scoring.**

- Boxes: row OK against the PP-OCRv5 reference boxes, as in the OpenCV crops experiment, on the
  2,123 rows that have a reference.
- Reading, on the gold sets: rows with all five options right and options right, after the
  normalization of `option_consensus.gold_norm` (superscripts become `^n`, spaces are ignored).
  An error is counted by the kind of the gold value: missing, fraction, exponent, symbol
  (non-ASCII) or other.
- Reading, without gold: rows with five options, rows that pass the format checks
  (`option_consensus.row_flags`), and options that differ from P0.
- Paired comparisons use the exact McNemar test on rows.

**Rule fixed before the run.** Adopt the smallest pipeline that (a) loses no gold row against P0
(at least 56 of 60), (b) makes fewer fraction, exponent and symbol errors on the hard gold, and
(c) keeps five options in at least 98.5 % of the dev rows. Prefer R2 to R1 only if it wins 3 rows
or more. Adopt a binarized input only if it is worse in no stratum.

## Finding the boxes

### What B0 gets wrong

B0 fails the reference check in 19 rows and finds no five boxes in 10 rows; 27 rows in all. We
looked at every one:

| What happens | Rows |
|---|---|
| Options closer together than the 41 px kernel: all five join into one box | 7 |
| The option continues on a second line: only the last line is kept | 3 |
| A stacked fraction: the row profile takes the denominator as the last text line | 3 |
| B0 is right; the reference box is wrong (grid, vertical list, question text touching) | 14 |

### How B1 works

1. **Find the labels.** A template of each label `A)` to `E)` is matched on the gray image. The
   label height changes from image to image (26 to 36 px), so each template is tried at 21
   scales. All scales run on the half-size image; the best three run at full size. The scale
   with the best sum of the five scores wins.
2. **Pick the sequence.** Among the matches, take an A followed in reading order by B, C, D and
   E. If several sequences exist, the one with the best total score wins. That keeps the label
   `A)` when the value of an option is itself the letter A.
3. **Give every ink component to one option.** A component on a label line goes to the nearest
   label on its left. A component over or under a fraction bar goes to the option of that bar.
   A component below a label line goes to the option whose first line is nearest in x; that is
   an option that continues below.
4. **Split label and value.** The value is every component of the option that is not its label.

The components come from a mask with the threshold `(t + 255) / 2`, where `t` is Otsu's. With
Otsu's threshold alone, thin strokes break a glyph into pieces: the stem of a digit can be as
light as 130 to 150 on a white background of 255, and the median Otsu threshold is 142.

The templates are the mean of the label crops of 200 rows that have a PP-OCRv5 reference. No row
of the sample is among them.

### Results

| Measure | B0 | B1 |
|---|---|---|
| Five boxes found, of 2,277 rows | 2,267 | 2,277 |
| Row OK against the reference, of 2,123 rows | 2,104 (99.11 %) | 2,105 (99.15 %) |
| Row OK here and not with the other detector | 1 | 2 |

The reference check cannot tell the two apart, because most of what it counts as a failure is an
error of the reference. The 13 real failures of B0 above are all right with B1, checked by eye.
B1 fails the reference check in 18 rows; the 11 we looked at are errors of the reference.

Finding the labels takes about 0.24 s of CPU per image. B0 takes about 0.01 s.

## Recognizer and input

Rows with all five options right. Every arm uses the B1 boxes.

**Line mode (no 2-D split):**

| Recognizer | Input | Gold (of 60) | Hard gold (of 40) |
|---|---|---|---|
| P0, today | whole image | 56 | 7 |
| P1 | whole image, masked fallback | 55 | 7 |
| R0 | I0 gray | 56 | 12 |
| R0 | I1 Otsu binary | 56 | 10 |
| R0 | I2 clean background | 57 | 13 |
| R0 | I3 soft binary | 57 | 13 |
| R1 | I0 gray | 57 | 15 |
| R1 | I1 Otsu binary | 57 | 14 |
| R1 | I2 clean background | 57 | 15 |
| R1 | I3 soft binary | 57 | 13 |
| R2 | I0 gray | 57 | 15 |

**With the 2-D split:**

| Recognizer | Input | Gold (of 60) | Hard gold (of 40) | Hard gold, options (of 200) |
|---|---|---|---|---|
| R0 | I0 gray | 59 | 37 | 193 |
| R0 | I1 Otsu binary | 58 | 33 | 183 |
| R0 | I2 clean background | 60 | 38 | 194 |
| R0 | I3 soft binary | 60 | 36 | 192 |
| R1 | I0 gray | 60 | 40 | 200 |
| R1 | I1 Otsu binary | 60 | 38 | 198 |
| R1 | I2 clean background | 60 | 40 | 200 |
| R1 | I3 soft binary | 60 | 38 | 198 |
| R2 | I0 gray | 60 | 40 | 200 |
| P0 where it is trusted, else R1 + I0 + 2d | | 60 | 39 | 197 |

What the tables show:

- **Recognizer.** In line mode R1 beats today's pipeline on the hard gold (15 against 7 rows,
  McNemar p = 0.008): the direct read of a tight box avoids the detector errors and R1 has the
  symbols. R0 with the 2-D split loses 6 to 13 options of the hard gold to symbols it reads
  wrong. R2 gives the same counts as R1.
- **Input.** Otsu's binary (I1) is the worst input for both recognizers. It costs R0 ten options
  on the hard gold and R1 two. The soft binary (I3) is in between. Whitening the background and
  keeping the gray ink (I2) helps R0 by one option and changes nothing for R1. The noise that
  binarizing removes is small; the anti-aliasing it removes is what the recognizers were trained
  on.
- **Selective use.** The last row keeps today's value and takes the new one only where OpenCV
  saw a fraction or an exponent, or where today's value fails a format check. It is not better
  than the new pipeline alone, so there is no reason to keep both.

## The 2-D split

The split runs on the components of one value:

- **Fraction.** A thin, wide component (the bar) with a glyph over it and a glyph under it. A
  minus sign has nothing on one side. The dots of a division sign are too small to count. The
  numerator and the denominator are read apart and joined as `a/b`; a part with an operator goes
  in parentheses, as in `(a+2b)/3`.
- **Exponent.** A component smaller than a digit that sits above the baseline and has a glyph on
  its left. The digit size and the baseline come from the label, so a value of low letters has
  them too. It is read apart and written `^n`. A single round raised component that reads as
  `o` or `0` is written `°`.
- **Everything else** is read as one line. A square root is left to the recognizer, which has
  `√`.

On the 2,277 rows OpenCV saw a fraction in 461 option values, an exponent in 251, both in 3, and
a value on several lines in 15.

| | Gold (of 60) | Hard gold (of 40) | Hard gold errors by kind |
|---|---|---|---|
| R1 + I0, line | 57 | 15 | 109 fractions, 1 exponent |
| R1 + I0, 2d | 60 | 40 | none |

## All rows and the blind check

The winning arm, B1 + R1 + I0 + 2d, on the 2,277 rows:

| Measure | P0 | P1 | New |
|---|---|---|---|
| Rows with five options | 2,243 | 2,256 | 2,277 |
| Rows that pass the format checks | 2,181 | 2,189 | 2,251 |
| Options that differ from P0, of 11,215 | 0 | 77 of 11,170 | 663 |

The 26 rows of the new arm that fail a format check are 20 with options of mixed kinds and 6
with a duplicate. Of the 663 options that differ from P0, OpenCV saw a fraction in 413 and an
exponent in 146; 86 are plain values.

**Cross-language agreement is not evidence here.** The three languages of a problem agree in
every option with the new arm (3,275 of 3,275, against 97.4 % for P0). But the option band of
the three images is almost the same picture, and the new arm reads the band alone. It would
agree with itself when wrong. The number says the read is stable, not that it is right.

**Blind check.** We drew 30 of the options that differ from P0, one per problem, from the 54
problems that are not in the sample (seed 97), and compared both reads with the image:

| | Options (of 30) |
|---|---|
| New read right | 28 |
| New read: characters right, form ambiguous | 2 |
| P0 right | 0 |

The two ambiguous reads were a product of powers written without a separator, which the code now
writes with a space, and a subscript written on the line, which is still open.

On the dev stratum the new arm differs from P0 in 21 options of 860. We checked all 21 against
the image and the new read is right in each.

## Speed

Laptop CPU (Intel Core i7-13700H), ONNX Runtime, one read at a time: `option_rec.py speed` on
300 option crops of the dev rows, after 20 warm-up reads. A llama.cpp server and other jobs were
using the CPU during the run, so these times are upper bounds.

| Step | Time |
|---|---|
| Find the five labels (B1) | 0.24 s per image, one thread |
| R0, one option | 29 ms (1 thread), 16 ms (4 threads) |
| R1, one option | 31 ms (1 thread), 13 ms (4 threads) |
| R2, one option | 1,498 ms (1 thread), 550 ms (4 threads) |

A row with the 2-D split needs 5.4 reads on average (12,344 reads for 2,277 rows). Finding the
labels is the slow step and has not been optimized: it matches 5 templates at 21 scales.

## Reference: granite-docling-258M

granite-docling-258M has about 50 times the parameters of R1. It ran on the value crops of the
40 hard-gold rows with the prompt `Convert formula to LaTeX.` (`option_rec.py granite`), on the
laptop GPU (RTX 4060, bfloat16, greedy decoding, at most 64 new tokens). It gets the whole
value, with no 2-D split: it reads the layout itself and answers in LaTeX, which `latex_canon`
writes on one line.

| | Hard gold, rows (of 40) | Options (of 200) | Time per option |
|---|---|---|---|
| R1 + I0 + 2d | 40 | 200 | 13 ms, CPU, 4 threads |
| granite-docling, formula prompt | 39 | 198 | 5.3 s, GPU |

Its two errors are in one row: a digit dropped from a long number of repeated digits. So a
model that reads the layout itself gives no more than OpenCV plus a small recognizer on these
values, and it is several hundred times slower.

Limits of this reference:

- One prompt, and the hard gold only. It did not run on the 60-row gold.
- The conversion from LaTeX was fixed after looking at its output. The first version did not
  remove the end token or the spaces the model writes between digits, and scored every option
  wrong.
- The time is an upper bound: other jobs used the GPU and the CPU during the run.
- A first attempt with two prompts and crops enlarged three times ran at about 3 minutes per
  row and was stopped.
- It needs `torch` and `transformers`, which `pyproject.toml` does not declare.

## Decision and what would reopen it

The rule fixed before the run is met by B1 + R1 + I0 + 2d:

- (a) Gold: 60 of 60, against 56 for P0.
- (b) Hard gold: no fraction, exponent or symbol error, against 115 for P0.
- (c) Dev: five options in 100 % of rows, against 98.9 %.
- R2 does not win 3 rows over R1, so R1 stays. No binarized input is adopted: I1 and I3 are
  worse on the hard gold, and I2 is equal at more cost.

What would reopen it:

- A gold checked by a person that disagrees with these counts.
- Languages with another script. The label templates are Latin letters; the options of Chinese,
  Japanese, Korean and Arabic rows were not tried.
- Rows with a figure. The component rules assume the options are text.

## Limitations

- **The hard gold was used during development.** Two rules changed after looking at its errors:
  how components are grouped into text lines, and where the baseline for exponents comes from.
  Its 40 of 40 is an upper estimate. The 60-row gold and the 30-option blind check were not used
  to change the code.
- **Both gold sets were written by Claude** and no person has checked them.
- **Small samples.** 60 and 40 rows show large differences only.
- **Three languages, text-only rows.**
- **Subscripts are written on the line.** A value such as "f, subscript 2, of x" comes out as
  `f2(x)`.
- **The templates come from the data.** They are built from rows where PP-OCRv5 gives the label
  position, and the labels of all rows are in one typeface.
- **The hard gold has no row where B1 itself fails.** B1 found five labels in every row, so no
  fallback was needed; `detect_b1` falls back to B0 when it finds no labels, and that path was
  not exercised. The reading path (`option_rec.read_row`) has no fallback: with no labels it
  returns no options. On the 2,277 rows this did not happen.
- **Not timed on the UNO Q.** `predict.py` receives no image, so this pipeline serves the data
  preparation on the laptop.

## Next steps

1. Have a person check the two gold sets, or a sample of them.
2. Run the new pipeline on the 108 languages and compare with the consensus experiment.
3. Make the label search faster: estimate the scale once, or search only the lower part of the
   image.
4. Put it in `prepare_m3kang.py` behind an option, and rebuild `train.jsonl` and `val.jsonl`
   without the OCR cache.
5. Handle subscripts.

## Appendix: reproducibility

| Item | Value |
|---|---|
| Commit the run started from | `1271701` (the two scripts are not committed yet) |
| Scripts | `laptop/option_boxes.py`, `laptop/option_rec.py` |
| Python environment | `.venv` (`uv sync`): onnxruntime 1.32.0, opencv-python-headless, scipy |
| Sample | `data/interim/optrec/sample.json`, SHA256 `cfe4dfa9258721bf…` |
| Gold | `data/interim/optx/options_gold3.json`, SHA256 `1b556037f7a4118b…` |
| Hard gold | `data/interim/optrec/options_gold_hard.json`, SHA256 `688cb05e11b91e07…` |
| R0 | `latin_PP-OCRv5_rec_mobile.onnx`, SHA256 `b20bd37c168a570f…` |
| R1 | `PP-OCRv6_rec_small.onnx`, SHA256 `6f327246b50388f3…` |
| R2 | `PP-OCRv6_rec_medium.onnx`, SHA256 `eef444829dbbe18d…` |

The three recognizers are the ONNX files that RapidOCR 3.10 publishes. R0 and R1 were copied from
the `ocr-v5` environment and R2 was downloaded; all three are in `data/external/ocr_models/`.
Everything the scripts write stays under `data/interim/optrec/`, which Git ignores.

Besides the files above, the commands need the box files of `laptop/ocr_boxes.py` and, for
`score` and `score-all`, the crop OCR of the OpenCV crops experiment. The
[option reader guide](../OPTION_READER_GUIDE.md#before-you-start) lists each file and what makes it.

From the repository root:

```bash
.venv/bin/python -I laptop/option_boxes.py pick
```

```bash
.venv/bin/python -I laptop/option_boxes.py templates
```

Boxes on every row, and their score against the reference:

```bash
.venv/bin/python -I laptop/option_boxes.py detect --arm B0 --scope all
```

```bash
.venv/bin/python -I laptop/option_boxes.py detect --arm B1 --scope all
```

```bash
.venv/bin/python -I laptop/option_boxes.py score --arms B0 B1 --scope all
```

The grid on the sample, then R2 on the gold rows (R2 is slow):

```bash
.venv/bin/python -I laptop/option_rec.py run --rec R0 R1 --input I0 I1 I2 I3 --mode line 2d
```

```bash
.venv/bin/python -I laptop/option_rec.py run --rec R2 --input I0 --mode line 2d --strata gold hard
```

```bash
.venv/bin/python -I laptop/option_rec.py score --selective B1-R1-I0-2d
```

The winning arm on every row:

```bash
.venv/bin/python -I laptop/option_rec.py run --all --rec R1 --input I0 --mode 2d
```

```bash
.venv/bin/python -I laptop/option_rec.py score-all
```

Speed, and the granite-docling reference (GPU):

```bash
.venv/bin/python -I laptop/option_rec.py speed
```

```bash
.venv/bin/python -I laptop/option_rec.py granite
```

The hard gold is not reproducible by a command: it was transcribed by hand from sheets of the
option band of 40 rows of the hard stratum.
