# Experiment: find and crop the five options with OpenCV before OCR

This report tests one idea from the
[OCR failure modes](../OCR_FAILURE_MODES.md#what-this-means-for-improving-option-reading) page:
crop the image before OCR. It has two parts:

1. Can OpenCV find the five answer options (A to E) in the image as bounding boxes, and how much
   does each step help? The steps are a binary Otsu threshold, a Gaussian blur and a morphological
   closing.
2. Does PP-OCRv5 read the options better inside the crop than on the whole image?

It is for the team and the datathon judges. Laptop run, 2026-11-15, branch `exp/decider-0.8b`.

[M3Kang](https://huggingface.co/datasets/qualcomm/M3Kang) is the dataset of Kangaroo maths
problems that the copilot answers. The five answer options are only in the image. This report shows
no problem text and no images.

## Terms used here

The [OCR failure modes](../OCR_FAILURE_MODES.md#background-how-the-options-are-read) page defines
row, text-only row, coverage and the parser (`parse_options`). New terms:

- **Mask**: a black-and-white image. Ink is white (255) and the background is black (0).
- **Otsu threshold**: a gray level that splits the image into ink and background. OpenCV finds it
  from the histogram (`cv2.THRESH_OTSU`).
- **Closing**: a dilation followed by an erosion with a rectangle of `kw × kh` pixels (the
  **kernel**). It fills gaps narrower than the kernel, so the letters of one option join into one
  blob.
- **Component**: a connected blob of white pixels in the mask. Its bounding box is one candidate
  region.
- **Reference box**: where an option really is. It is the union of the PP-OCRv5 boxes from label X
  up to the next label, shrunk to the ink inside it.
- **Contained**: the reference box fits inside the found box, with 4 px of slack. Nothing of the
  option is cut off.
- **Pure**: the found box covers at most 10 % of any other option's reference box.
- **Row OK**: all five options contained and pure, in the order A to E.
- **Repair**: a rule that runs after the morphology to get exactly five boxes. It joins the two
  nearest boxes, or splits the widest box at its widest empty column.
- **Masked image**: the whole image, painted white outside the option region.
- **Cross-language agreement**: for problems read in English, Catalan and Spanish, the share of
  options whose normalized value is the same in all three. It needs no reference. It undercounts,
  because options with words change from one language to the next. It is only good for comparing
  methods with each other.

## Summary

- **OpenCV finds the five option regions in most rows.** Otsu followed by a 41×3 closing finds five
  regions in 99.3 % of the 2,123 rows that have a reference, with no extra rule. With the repair
  rule, 99.1 % of those rows are fully right (row OK). In the 154 rows where the parser finds no
  five options on the whole image, the ones the fallback is for, five regions come out in 146
  (95 %). These rows have no reference, so we cannot check the boxes there.
- **A binary mask is required. The Gaussian blur does not help. The closing makes the regions
  without a count rule.** Without a closing, every letter is its own component. The morphology alone
  then never gives five regions. The kernel width decides the result: row OK is 0 % at 9 px,
  89–92 % at 25 px, 98–99 % at 41 px, and 97 % at 61 px, where neighbouring options start to merge.
  With the repair rule on, the closing adds about one row: Otsu alone reaches 99.06 % row OK against
  99.11 %. We binarized only with Otsu, so this run does not compare Otsu with a fixed threshold.
- **Giving the parser a crop makes coverage worse.** The parser reads five options in 91.4 % of rows
  from the tight crop and in 91.3 % from the masked image, against 93.5 % from the whole image.
  The likely cause is that the OCR misreads more labels without the rest of the image. We did not
  test this.
- **Letting OpenCV assign the letter raises coverage.** We give each OCR box of the masked image to
  the OpenCV region that holds its centre, so the parser does not have to find the labels. This
  reads five options in 96.7 % of rows.
- **Highest coverage: the whole image first; if the parser does not find five options there, the
  masked image with the OpenCV regions.** This reads five options in **99.1 %** of the 2,277 rows,
  and recovers 126 rows. It loses no row, but this is by design: rows the whole image reads keep that
  read. Today's fallback (PP-OCRv5, then PP-OCRv4) reaches 98.5 %, and needs a second OCR model.
- **The recovered rows are less reliable.** Of the 126, 38 have at least one option (53 in all)
  whose first token is not a label the parser accepts, so the value can keep a misread label.
  Cross-language agreement is 90.7 % on the 56 problems that use a fallback row, against 97.9 % on
  the 590 problems read from the whole image. This run measures coverage, not correctness.

## Why we ran it

Board guide [section 13.3](../BOARD_SETUP.md#133-ideas-to-reason) suggests cropping the image
before OCR. The [OCR failure modes](../OCR_FAILURE_MODES.md#what-this-means-for-improving-option-reading)
page lists the idea as not yet measured. Classic image clean-up (blur, threshold) is meant for
photos and scans. M3Kang images are clean renders. So the real question was whether OpenCV helps
to *locate* the options, not to clean the image.

## What we compared

**Data.** The 2,277 text-only rows in English, Catalan and Spanish, from `data/raw_txto_yes/`.
These are the same rows as in the [Tesseract report](2026-11-tesseract-text-only.md). The
whole-image PP-OCRv5 boxes come from `data/interim/ocr_boxes_txto_yes_v5.jsonl`, the same file the
earlier reports used.

**Reference.** The parser reads five options from the whole-image boxes in 2,130 rows (93.5 %). In
2,123 of them, each label has a box of its own, so we can build a reference box. In the other 7,
the parser rebuilt a missing `C)`. In 2,114 of the 2,123 rows the options are on one line, in 6
rows on two lines (3 + 2), and in 3 rows on five lines.

**Pipeline.** The notebook `notebooks/option_crops_opencv.ipynb` runs these steps on each image:

1. Gray scale, then an optional `cv2.GaussianBlur`.
2. `cv2.threshold` with `THRESH_BINARY_INV + THRESH_OTSU`.
3. An optional `cv2.morphologyEx(MORPH_CLOSE)` with a `kw × kh` rectangle.
4. `cv2.connectedComponentsWithStats`: components of 4 px or more give the bounding boxes.
5. **Choosing five boxes.** Find the text lines from the row profile of the mask, and take the
   boxes of the last line. If that line has fewer than five boxes, add the lines above it until
   there are five. Stop at a line with a box wider than half the image, which is a question line.
   With repair, join or split boxes until there are five.

**Variants.** These four variants and their kernel sizes give 114 settings. Each runs on all 2,123
rows, with and without repair:

- A: Otsu.
- B: Gaussian blur and Otsu.
- C: Otsu and closing.
- D: Gaussian blur, Otsu and closing.

The kernel sizes are kw ∈ {5, 9, 15, 25, 41, 61}, kh ∈ {1, 3, 5} and blur ∈ {0, 3×3, 5×5}. The main
figure is row OK **without** repair, because it measures the OpenCV steps alone.

**OCR on the crops.** For the chosen variant (Otsu and a 41×3 closing, no blur, with repair), the
notebook writes these files for each row to `data/interim/option_crops/`:

- one tight crop of the option region (+8 px);
- five tight crops A to E (+4 px);
- one masked image.

`laptop/ocr_crops.py` runs the same PP-OCRv5 engine as `ocr_boxes.py` on each file. It first adds a
16 px white border. We compared seven ways to read the options:

| Method | What it does |
|---|---|
| Whole image | Parser on the existing whole-image boxes (today's PP-OCRv5 path) |
| Region | Parser on the tight crop of the region |
| Per option | Text of each A to E crop, with the label taken off by `is_marker` |
| Masked region | Parser on the masked image |
| Masked + OpenCV regions | OCR boxes of the masked image, each given to the OpenCV region that holds its centre |
| Whole → masked | Whole image; masked region when the parser does not find five options there |
| Whole → OpenCV regions | Whole image; masked + OpenCV regions when the parser does not find five options there |

## Finding the options

The chosen variant on the 2,123 rows with a reference:

| Measure | Morphology alone | With repair |
|---|---|---|
| Five regions found | 99.25 % | 99.91 % |
| Options contained | 98.93 % | 99.59 % |
| Options pure | 99.25 % | 99.91 % |
| Mean IoU | 0.997 | 0.997 |
| Row OK | 98.45 % | 99.11 % |

With repair, row OK is 98.5–99.3 % in each language, and 98.1–100 % in each level (level 7: 99.0 %).
Of the 19 rows that fail, 17 have an option cut off and 2 do not give five regions. The failure
gallery in the notebook shows three kinds of failure:

- an option text that runs onto a second line;
- a tight vertical list;
- a reference box that includes part of the question, because one OCR box covers both.

The third kind is an error in the reference, not in OpenCV.

Over all 2,277 rows, including the rows with no reference, the chosen variant gives five regions in
2,267 rows.

## What each step adds

Row OK without repair, by kernel size:

| kw (kernel width) | 5 | 9 | 15 | 25 | 41 | 61 |
|---|---|---|---|---|---|---|
| No blur, kh = 1–5 | 0 % | 0 % | 9–10 % | 89–92 % | 97.6–98.6 % | 97 % |
| Blur 5×5, kh = 1–5 | 0 % | 0 % | 10–11 % | 92–94 % | 98.0–98.3 % | 97 % |

- **Otsu threshold.** A binary mask is required: without one there are no components. Every
  variant uses Otsu, so this run does not show that Otsu beats a fixed threshold. The images are clean
  renders, and their histogram has one large peak for the background and a small one for the ink.
  On 300 images, the median Otsu threshold is 142.
- **Gaussian blur.** It does not help. There is no noise to remove. The blur lightens thin
  strokes, so the Otsu threshold rises (median 142 → 170 with 3×3). It also spreads the ink. Mean IoU is 0.997 with no
  blur, 0.95 with 3×3 and 0.93 with 5×5, but this drop is expected by construction: the reference is
  shrunk with the unblurred mask. So we judge the blur on row OK. At kw = 25 it adds 1–3 points of
  row OK, because thicker ink closes gaps. A wider closing
  does the same job without making the boxes larger. The best setting with blur (5×5, 41×5:
  98.30 %) is below the best setting without blur (41×5: 98.59 %).
- **Closing.** This is the step that turns letters into options. Without it (variants A and B),
  the morphology gives five regions in 0 % of rows. The kernel must be wider than the gap between a
  label and its value, and narrower than the gap between two options. On 500 one-line rows, the gap
  between options is 46 px at the 1st percentile and 176 px at the median. This is why 41 px works
  and 61 px starts to merge options. The kernel height matters little: kh = 3–5 gives up to one
  point more than kh = 1, probably because it joins accents and fraction bars to their line.
- **Repair.** It does by hand what the closing does. With repair, even Otsu alone reaches 99.06 %
  row OK. But the repair needs to know that there are exactly five options. The closing does not.
  All the variants with repair are between 99.06 % and 99.15 % row OK, that is, within 2 rows of
  each other.

Mean IoU near 1 is partly circular: the reference is shrunk with the same Otsu mask. It shows that
the boxes group the right characters. It does not show accuracy to the pixel.

## OCR on the crops

All 2,277 rows. "Agreement with whole" counts only the rows where both methods read five options.

| Method | Five options | Agreement with whole | Recovered | Lost | Cross-language agreement (problems) |
|---|---|---|---|---|---|
| Whole image | 93.5 % | — | — | — | 97.9 % (590) |
| Region | 91.4 % | 96.4 % | 85 | 134 | 100 % (599) |
| Per option | 89.2 % | 62.5 % | 116 | 216 | 97.7 % (585) |
| Masked region | 91.3 % | 96.3 % | 90 | 140 | 99.9 % (600) |
| Masked + OpenCV regions | 96.7 % | 95.2 % | 126 | 55 | 99.8 % (633) |
| Whole → masked | 97.5 % | 100 % | 90 | 0 | 97.6 % (630) |
| **Whole → OpenCV regions** | **99.1 %** | 100 % | 126 | 0 | 97.3 % (646) |

**Recovered** means the whole image gave no five options and the method did. **Lost** means the
opposite.

- **The parser on a crop is worse than on the whole image.** Region and masked region lose more rows
  than they recover. In the rows they lose, the OCR misreads a label in a way the parser does not
  accept: for example, `E)` read as `(3`. The masked image keeps the scale of the whole image and
  loses about as many rows as the tight crop (140 against 134). So the loss most likely comes from
  the missing context, not from the scale. We did not test this further.
- **Per-option crops are the worst.** The labels come out as other characters (`A)` as `4`, `y` or
  `Y`), so `is_marker` does not remove them and they stay in the value. That is why agreement with
  the whole image is only 62.5 %. A likely cause is the RapidOCR text detector: it scales the short
  side of an image up to 736 px (`limit_type: min` in its config), so a crop of about 40 px high
  is enlarged many times. We did not test this.
- **Masked + OpenCV regions has the highest coverage of the single methods.** OpenCV gives the
  letter, so the parser does not have to find the label. But a misread label stays in the value:
  `strip_label` keeps the first token when `is_marker` does not accept it. It loses 55 rows. We did not count why. The likely causes are one OCR box that
  spans two options (its centre falls in one region and the other region stays empty), and an
  option region with no OCR box.
- **Whole → OpenCV regions** keeps every whole-image row and adds 126: 99.1 % coverage. In each
  language it is 98.8–99.4 %, and in level 7 (fractions) it is 97.8 %, against 90.5 % for the whole
  image. "Lost 0" and "agreement with whole 100 %" hold by design, not by measurement. The pooled
  cross-language agreement (97.3 %) hides a gap: 97.9 % on the 590 problems read from the whole
  image, and 90.7 % on the 56 problems that use a fallback row. In 38 of the 126 recovered rows, at
  least one option (53 in all) starts with a token that the parser does not accept as a label. The
  rows the fallback adds are therefore less reliable than the rest.

## Speed

On the laptop GPU (RTX 4060, 8 GB), PP-OCRv5 read 10.3 tight crops per second (9,443 in 921 s).
The OpenCV export of all 2,277 rows took about 20 s on one CPU thread, including PNG decoding and
writing. The full notebook, with the 114-setting sweep, takes about 4 minutes. On the board, the fallback
costs one more OCR call, and only for the about 6.5 % of rows where the whole image fails. We did
not time it on the board.

## Limitations

- **The reference comes from the same OCR.** It exists only where the parser already works on the
  whole image (2,123 of 2,277 rows), so the geometry figures leave out the hardest rows. On those
  rows OpenCV is judged only through the OCR coverage.
- **Coverage is not correctness.** Agreement with the whole image does not tell which of the two
  reads is right. Cross-language agreement misses an error that is the same in all three languages.
  We did not score the methods against the option gold of the
  [Tesseract report](2026-11-tesseract-text-only.md#what-we-compared).
- **Text-only rows, three languages.** The rows with a figure (`text_only` false) are not measured.
  There, a figure can sit next to the options, and the "box wider than half the image" rule may not
  stop at it.
- **One run, one seed** for the sample figures. The sweep is deterministic.
- **Not in the pipeline yet.** `laptop/prepare_m3kang.py` does not use this fallback.
- **The notebook is not in Git.** Its outputs show M3Kang images, so it is listed in
  `.gitignore`. To reproduce the run, you need the notebook file itself.

## Next steps

- Clean the values of the recovered rows: drop a first token that is a misread label, then run the
  format checks of the [option extraction report](2026-11-option-extraction-consensus.md#format-checks).
- Score the fallback against the option gold of the Tesseract report, to measure correctness and
  not only coverage. Only a few gold rows fall in the recovered set, so a larger gold sample drawn
  from those rows would be needed.
- Only then add "whole → OpenCV regions" to `prepare_m3kang.py`, and measure it on
  `data/train.jsonl` and `data/val.jsonl`.
- Add a fixed-threshold arm, to compare Otsu with a plain threshold.
- Run it on the rows with a figure.
- Keep a copy of the notebook in Git with its outputs cleared, so it can be reproduced.

## Appendix: reproducibility

From the repository root. Run the notebook up to section 7. It writes the crops and the sweep table
to `data/interim/` (both gitignored):

```bash
.venv/bin/jupyter lab notebooks/option_crops_opencv.ipynb
```

Run PP-OCRv5 on the crops (ocr-v5 environment, GPU). It resumes when stopped:

```bash
~/.venvs/ocr-v5/bin/python laptop/ocr_crops.py
```

Then run section 8 of the notebook. To run all of it without the browser, once the OCR file
exists:

```bash
.venv/bin/jupyter nbconvert --to notebook --execute --inplace notebooks/option_crops_opencv.ipynb
```

The sweep uses 4 worker processes. With 8, a 12 GB laptop ran out of memory.
