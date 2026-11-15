# Experiment: Tesseract against PP-OCRv4 and PP-OCRv5 on text-only problems

This report compares Tesseract, a classic open-source OCR engine, with the two engines we
tested before, PP-OCRv4 and PP-OCRv5. It measures two things: how well each engine reads the
question text, and how well it reads the five answer options. It also sets the measured
Tesseract figures against the figures that Tesseract's authors and others publish for clean
printed text. It is for the team and the datathon judges. Laptop run, 2026-11-15, branch
`exp/decider-0.8b`.

[M3Kang](https://huggingface.co/datasets/qualcomm/M3Kang) is the dataset of Kangaroo maths
problems that the copilot answers. Each problem has the question as text and as an image. The
five answer options, A to E, are only in the image. The
[OCR text against the annotated question](2026-11-ocr-text-vs-annotation.md) report scored
PP-OCRv4 and PP-OCRv5 on the question. This report adds Tesseract to the same scoring, and adds
a score for the options.

## Terms used here

The [earlier report](2026-11-ocr-text-vs-annotation.md#terms-used-here) defines OCR, box,
reference, row, text-only row, CER and clean rows. The same meanings hold here. New terms:

- **Tesseract**: the OCR engine of the [tesseract-ocr](https://github.com/tesseract-ocr/tesseract)
  project, version 5.5.0, with its LSTM recognizer (a neural network that reads a whole text
  line). It runs on the CPU.
- **tessdata_best**: the most accurate family of Tesseract language models. Tesseract also ships
  a faster, less accurate family (`tessdata_fast`).
- **Option gold** (gold3): 60 rows whose five options Claude, the coding agent of this project,
  wrote down from the image. Each value it wrote is a **gold value**. No person checked them.
- **Parser**: `parse_options` in `laptop/prepare_m3kang.py`. It finds the labels `A)` to `E)` in
  the OCR boxes and takes the value after each one.
- **Format checks**: the automatic checks of the
  [option extraction report](2026-11-option-extraction-consensus.md#format-checks): no empty
  option, no label inside a value, no duplicate, no stray characters, one kind of option.
- **v5>v4**: the current way to read the options. Take the PP-OCRv5 options, and the PP-OCRv4
  options when PP-OCRv5 reads none.

## Summary

- **For the question text, Tesseract is clearly better than both PP-OCR engines.** On the 2,236
  clean rows, its mean CER with spaces ignored is 2.3 %, against 9.5 % for PP-OCRv5 and 21.6 % for
  PP-OCRv4. It is lower in each language, and the 95 % range of the difference stays below zero in
  each language.
- **The gain comes from lines that PP-OCR loses, not from better reading of each character.**
  Tesseract's text is short (under 70 % of the reference) in 1 row. PP-OCRv5's is short in 330
  rows, and Tesseract reads at least 70 % of the reference in all 330 of them. Row by row, the two
  engines are close: Tesseract has the lower CER in 779 rows, PP-OCRv5 in 743, and 714 tie. So the
  question lines that PP-OCR misses are in the image. This points to the PP-OCR text detector,
  which the earlier report left open.
- **For the five options, Tesseract is clearly worse.** It reads five options in 75.5 % of the
  2,277 rows, against 93.5 % for PP-OCRv5. On the 60-row option gold, all five options are right
  in 39 rows for Tesseract and 55 for PP-OCRv5. An exact McNemar test gives p < 0.001. Most of
  Tesseract's errors are missing options: it misreads the typeset labels, so the parser does not
  find them. For example, the Spanish model reads `C)` as `Cc)` or `Ce)` in 153 of the 655
  Spanish rows.
- **Using Tesseract as the fallback adds nothing.** "PP-OCRv5, then Tesseract" has all five
  options right in 56 of 60 gold rows, the same as today's "PP-OCRv5, then PP-OCRv4". It reads
  five options in fewer rows (97.4 % against 98.5 %).
- **The Catalan model cannot write a question mark.** The character list of the `tessdata_best`
  Catalan model has 90 entries, and `?`, `+`, `=`, `%`, `×` and `·` are not among them. In 742 of the 785 Catalan
  questions that end in `?`, Tesseract writes a digit instead. This is why its Catalan CER (3.8 %)
  is higher than its English and Spanish CER (1.4 %).
- **On the CPU, Tesseract is about 5 to 7 times faster and uses far less memory.** On the laptop,
  it takes about 0.45 s per image against 2–3 s for PP-OCRv4 and PP-OCRv5, with 1 or 4 threads.
  Its peak memory is 60 MB, against about 0.9 GB. The board run is prepared but not done yet (see
  [Speed](#speed)). [Accuracy against speed and memory](#accuracy-against-speed-and-memory) puts
  these figures next to the accuracy results.
- **The published figures** (see [Published Tesseract figures](#published-tesseract-figures)) are
  measured on other data, under other conditions. Our question-text figure is close to them. The
  option figure is not, because the options are typeset maths with labels that the models misread.
- **How sure we are.** The question-text result is large and consistent in all three languages.
  The option result rests on 60 gold rows that an AI agent wrote, plus automatic counts on 2,277
  rows that point the same way. We tested one Tesseract setup, with no preprocessing and no parser
  changes. A parser that accepts Tesseract's label misreads could change the option result.

**Decision.** Keep PP-OCRv5 (with the PP-OCRv4 fallback) for the options. If the pipeline needs
the question text from the image, Tesseract is the better engine for it, except that the Catalan
model loses `?` and some maths signs.

## Why we ran it

The earlier report found that PP-OCRv5 reads the typical question almost perfectly, but loses
whole lines in about one row in seven. Tesseract is the usual baseline for printed text, and its
authors publish error rates for clean print. We wanted to know two things: whether these images
are "clean print" for Tesseract, and whether Tesseract reads the question or the options better
than the PP-OCR engines.

## What we compared

**Data.** The same 2,277 text-only rows as the earlier report: English (811), Catalan (811) and
Spanish (655), all from the first `high_quality` file of M3Kang. The question text is scored on
the 2,236 clean rows. The options are scored on all 2,277 rows.

**Engines.**

| Name | Software | Models | Device |
|---|---|---|---|
| PP-OCRv4 | `rapidocr_onnxruntime` 1.4.4 | its default models | GPU |
| PP-OCRv5 | `rapidocr` 3.10 | mobile text detector, recognizer for Latin scripts | GPU |
| Tesseract | `tesseract` 5.5.0 (leptonica 1.86.0) | `tessdata_best` eng, cat and spa | CPU |

We reused the PP-OCR boxes of the earlier report and did not run those engines again.

**The Tesseract setup, fixed before the run.**

- LSTM recognizer (`--oem 1`), automatic page layout (`--psm 3`, the default).
- No preprocessing: the image bytes from the dataset go to Tesseract unchanged.
- One model per language: `eng` for English, `cat` for Catalan, `spa` for Spanish. All three come
  from the same commit of `tessdata_best`. The distro package installs only English, probably from
  the `fast` family, so we downloaded all three, so that no language uses a different model family.
- `laptop/ocr_boxes.py dump --engine tess` saves one box per word in the same format as the
  PP-OCR boxes. The question scoring and the option parser then run unchanged on all three engines.
  We used word boxes rather than line boxes: a line box such as `A) 3 B) 4 C) 5` would hide the `B)`
  label from the cut that removes the options from the question text.

**Scoring.**

- Question text: `laptop/ocr_vs_text.py`, as in the earlier report: reading order, cut before the
  `A)` label, normalization, edit distance. The main figure is the mean CER with spaces ignored, with
  a 95 % bootstrap range (2,000 draws by problem, seed 0).
- Options: `laptop/option_consensus.py engines`.
  - On all 2,277 rows: the rows with five options, the rows that also pass the format checks, and
    the language-free options (numbers and formulas) that equal the same engine's option for the same
    problem in the other two languages.
  - On the option gold: rows with all five options right, and options right, with the
    normalization of the existing gold (`gold_norm`).

**The option gold.** `option_consensus.py gold3-pick` drew 20 rows per language at random (seed
31) from the 2,277 rows, leaving out the rows of the older gold. We drew it before we scored any
engine on options. Claude wrote the options from a crop of each image (the option band, from just
above the `A)` label) without seeing what any engine read. None of the 60 rows has picture options.
The [older gold](2026-11-option-extraction-consensus.md#what-we-compared) has 11 rows in these
languages, chosen partly as hard cases. They are reported apart.

**How we judged the result.** Fixed before the run:

- Question text: "Tesseract reads better than engine X" if its mean CER is lower in every language
  and the 95 % range of the difference stays below zero.
- Options: "Tesseract reads better than PP-OCRv5" if it has more gold rows with all five options
  right, with an exact McNemar test p < 0.05. Otherwise the result is "worse" or "no difference".

## Question text

Mean CER with spaces ignored, clean rows, with the 95 % bootstrap range.

| Language | Clean rows | PP-OCRv4 | PP-OCRv5 | Tesseract | Tesseract minus PP-OCRv5, points |
|---|---|---|---|---|---|
| English | 793 | 19.5 % [17.5, 21.5] | 10.3 % [8.7, 11.9] | 1.4 % [0.9, 2.0] | −8.9 [−10.6, −7.2] |
| Catalan | 803 | 23.4 % [21.5, 25.5] | 8.9 % [7.5, 10.3] | 3.8 % [3.2, 4.5] | −5.0 [−6.5, −3.5] |
| Spanish | 640 | 22.0 % [20.1, 24.1] | 9.4 % [7.8, 11.1] | 1.4 % [1.0, 1.9] | −8.1 [−9.8, −6.3] |
| All | 2,236 | 21.6 % [20.3, 22.9] | 9.5 % [8.5, 10.5] | 2.3 % [1.9, 2.7] | −7.2 [−8.3, −6.2] |

Tesseract minus PP-OCRv4 is −19.4 points [−20.7, −18.0] over all rows. The PP-OCR figures equal
those of the earlier report: the same rows, boxes and draws.

Other measures, clean rows, all languages (2,236):

| Measure | PP-OCRv4 | PP-OCRv5 | Tesseract |
|---|---|---|---|
| Median CER, no spaces | 4.5 % | 0.4 % | 0.0 % |
| CER, spaces included | 31.1 % | 9.5 % | 2.4 % |
| Word error rate | 81.3 % | 11.3 % | 6.5 % |
| Rows with CER (no spaces) under 5 % | 52.5 % | 82.9 % | 91.4 % |
| Numbers match | 67.7 % | 86.1 % | 60.6 % |

- **Numbers match** is low for Tesseract only because of Catalan: 92.9 % in English, 91.1 % in
  Spanish and 4.5 % in Catalan. In Catalan, the final `?` comes out as a digit, which adds one
  number to almost every question (see [The Catalan model](#the-catalan-model)).
- **Row by row**, Tesseract has the lower CER (no spaces) in 779 rows and PP-OCRv5 in 743, and 714
  rows tie. Against PP-OCRv4, Tesseract is lower in 1,518 rows and PP-OCRv4 in 252.
- **Verdict:** by the rule fixed before the run, Tesseract reads the question text better than both
  PP-OCR engines.

### Rows where the OCR text is much shorter

As in the earlier report, a row is short when the OCR text has under 70 % of the reference
characters, spaces deleted.

| Clean rows (of 2,236) | Count |
|---|---|
| PP-OCRv4 short | 714 |
| PP-OCRv5 short | 330 |
| Tesseract short | 1 |
| PP-OCRv5 short, Tesseract not | 330 |
| Neither PP-OCR engine reaches 70 %, Tesseract does | 127 |
| No engine reaches 70 % | 0 |

The short rows give 89 % of PP-OCRv5's summed CER. Tesseract reads at least 70 % of the reference in
every one of them, from the same image. On these 330 rows its mean CER (no spaces) is 2.3 % and its
median 0.0 %, and 305 of them are under 5 %. On the 127 rows where neither PP-OCR engine reaches
70 %, its mean CER is 1.1 %. The CER filter here depends on PP-OCRv5, not on Tesseract, so it does
not favour Tesseract. In 21 of the 330 rows Tesseract's `A)` cut failed, which raises its CER there. So the question lines that PP-OCRv5 misses are in the image,
and readable. Tesseract finds text lines with its own layout analysis, not with a neural text
detector. This supports the idea that the PP-OCR text detector drops the lines. We did not test the
detector itself.

### The A) cut

The question score depends on cutting the options off at the `A)` label. If the cut fails, the
options stay in the OCR text and raise the CER for a reason that has nothing to do with reading the
question. The cut fired in 2,147 rows for PP-OCRv4, 2,237 for PP-OCRv5 and 2,102 for Tesseract, out
of 2,277. Tesseract misreads more labels (see [The five options](#the-five-options)), so more of its
rows keep the options. This raises Tesseract's CER. Its question figure is therefore, if anything,
a little too high.

### The Catalan model

The character list of the `tessdata_best` Catalan model (`cat.traineddata`) has 90 entries. The Catalan
references use characters that are not among them. In this list, each character is followed by the
number of Catalan rows that use it: `?` 788, `’` 527, `ü` 92, `+` 42, `=` 37, `;` 37, `·` 34, `%`
30, `−` 25, `×` 19.
Tesseract writes none of them in Catalan. It wrote no `?` in any of the 811 Catalan rows, and in 742
of the 785 questions that end in `?`, it wrote a digit there instead. The English and Spanish models
write `?` (and Spanish `¿`) normally. For the question text, this costs about one character per row.
For maths, the missing `+`, `=`, `%` and `×` matter more.

## The five options

All 2,277 rows. Each engine's boxes go through the same parser.

| Engine | Five options read | Five options, pass format checks |
|---|---|---|
| PP-OCRv4 | 89.2 % | 87.3 % |
| PP-OCRv5 | 93.5 % | 91.0 % |
| Tesseract | 75.5 % | 72.9 % |
| PP-OCRv5, then PP-OCRv4 (today) | 98.5 % | 95.8 % |
| PP-OCRv5, then Tesseract | 97.4 % | 94.6 % |

By language, Tesseract reads five options in 78.7 % of the English rows, 84.3 % of the Catalan rows
and 60.6 % of the Spanish rows. The PP-OCRv5 figure (93.5 %) and the "then PP-OCRv4" figure
(98.5 %) equal those of the [OCR failure modes page](../OCR_FAILURE_MODES.md#pp-ocrv5-compared-with-pp-ocrv4),
which checks that the boxes and the parser are the same.

Language-free options that equal the same engine's option for the same problem in the other two
languages: PP-OCRv4 97.4 % (9,558 of 9,817), PP-OCRv5 98.6 % (10,124 of 10,272), Tesseract 90.4 %
(6,874 of 7,608). The [option extraction report](2026-11-option-extraction-consensus.md#summary)
found that this check misses most errors, so we use it only as a second signal.

**Option gold, 60 rows (20 per language):**

| Engine | Rows with all five right | Options right |
|---|---|---|
| PP-OCRv4 | 48 of 60 | 259 of 300 |
| PP-OCRv5 | 55 of 60 | 286 of 300 |
| Tesseract | 39 of 60 | 213 of 300 |
| PP-OCRv5, then PP-OCRv4 (today) | 56 of 60 | 291 of 300 |
| PP-OCRv5, then Tesseract | 56 of 60 | 291 of 300 |

- **Tesseract against PP-OCRv5:** only Tesseract right in 2 rows, only PP-OCRv5 right in 18. Exact
  McNemar test, p < 0.001 (0.0004).
- **Tesseract against PP-OCRv4:** 6 against 15, p = 0.078.
- **The two fallbacks** are right on the same 56 rows.
- **Verdict:** by the rule fixed before the run, Tesseract reads the options worse than PP-OCRv5.

Wrong options on the gold, by kind:

| Engine | Missing | Stacked fraction read as two numbers | Exponent lost | Other |
|---|---|---|---|---|
| PP-OCRv4 | 20 | 0 | 0 | 21 |
| PP-OCRv5 | 5 | 0 | 1 | 8 |
| Tesseract | 70 | 0 | 5 | 12 |

Most of Tesseract's wrong options are missing: the parser found no value for them. The labels are
typeset in a different font from the question, and Tesseract misreads them. The most common
misreads, counted over all 2,277 rows:

- the Spanish model reads `C)` as `Cc)` (135 times) or `Ce)` (18 times);
- the English model reads `C)` as `Cc)` or `CQ)` (9 times each);
- labels without the parenthesis, or with a comma.

The parser expects `C)` and gives up on the row. The options that Tesseract does return are also
wrong more often: 17 of 230 (7 %), against 9 of 295 (3 %) for PP-OCRv5.

On the 11 rows of the older gold in these languages, all five options are right in 3 rows for
PP-OCRv4, 6 for PP-OCRv5 and 7 for Tesseract. These rows were chosen partly as hard cases for the
PP-OCR engines, so they are not a fair sample. With 11 rows, they show nothing either way (Tesseract
against PP-OCRv5: p = 1.0).

## Published Tesseract figures

These are the figures that the Tesseract project and others publish for printed text. We took
them from primary sources only. They were measured on other data, so they are reference points,
not a ceiling or a target. None of them covers Catalan, and we found no primary CER figure for
Tesseract 5.

| Source | Version, model | Test data | What the engine had to find | CER |
|---|---|---|---|---|
| [UNLV test reports](https://github.com/tesseract-ocr/test/tree/main/unlvtests/reports) (`4_fast_eng`, `4_best_spa`) | 4.0.0-beta (2018), LSTM | ISRI scans at 300 dpi: English business letters, DOE, magazine and newspaper pages; Spanish newspaper | Text inside hand-drawn zones (no column or reading-order errors) | English 1.2–2.0 % (`fast`); Spanish 0.8 % (`best`) |
| [Smith, DAS 2016 tutorial](https://github.com/tesseract-ocr/docs/blob/main/das_tutorial2016/7Building%20a%20Multi-Lingual%20OCR%20Engine.pdf), part 7, slide 12 | 2016 LSTM pre-release, with dictionary | About 1,000 lines per language from old Google Books | Single text lines | English 1.76 %; Spanish 2.31 % |
| [Smith 2007, ICDAR](https://tesseract-ocr.github.io/docs/tesseracticdar2007.pdf), Table 1 | 2.0, legacy engine | Same ISRI sets as the first row, English | Zones, as in the first row | 1.6–2.2 % |
| [Rice, Jenkins and Nartker 1995](https://tesseract-ocr.github.io/docs/AT-1995.pdf), Table 3 | Tesseract's ancestor (HP Labs OCR) | Same ISRI sets, English | Zones, as in the first row | 1.3–2.5 % |

The ISRI figures count spaces and line ends as characters. The DAS slide does not say. The
[OmniDocBench](https://github.com/opendatalab/OmniDocBench) table gives Tesseract 5.5 a normalised
edit distance of 0.096 on English text blocks of mixed PDF pages. That is a different measure, so
it is not in the table.

**Our figures, set against these.** With spaces counted, Tesseract's CER on the clean rows is
1.6 % in English and 1.7 % in Spanish. In English this is within the published range. In Spanish
it is above the 0.8 % of the newspaper test and below the 2.3 % of the old-book lines. In Catalan
(3.6 % with spaces) it is higher than any published figure, for the reason in
[The Catalan model](#the-catalan-model). So, for the question text, these images behave like
"clean print": Tesseract reaches about its published accuracy.

**Why the figures differ, and why the options do not reach them.**

- **What the engine has to find.** The published figures give the engine the text zones or the
  lines. Our run makes Tesseract find the lines itself (page level). It still loses almost nothing:
  1 short row of 2,236.
- **Maths is left out of the published tests.** The 1995 ISRI test leaves equations and text inside
  figures out of its zones. The options of a maths problem are typeset maths in another font (the
  labels and values look like LaTeX output). Most of Tesseract's option errors are there: missed
  labels such as `C)` read as `Cc)`. No published figure measures this.
- **Resolution.** The tessdoc
  [ImproveQuality](https://tesseract-ocr.github.io/tessdoc/ImproveQuality.html) page recommends at
  least 300 dpi. Our images are 1,653–1,700 px wide (median height 179 px, sample of 228 images)
  and carry no dpi tag. Tesseract estimated 258 dpi for the one image we checked. The
  [old FAQ](https://tesseract-ocr.github.io/tessdoc/tess3/FAQ-Old.html) gives about 20 px as the
  typical x-height (the height of a lower-case `x`). It says that accuracy is poor below 10 px.
  Tesseract's word boxes here are 20 px tall at the median (15–26 px from the 10th to the 90th
  percentile). A word box includes the tall and low parts of letters, so the x-height is smaller.
  We did not measure the x-height, but these sizes are not far from the recommended range. This
  fits the question result. We did not test whether scaling the images up would help with the
  labels.
- **Character set.** The published figures use models that can write every character of the
  test. The Catalan model here cannot write `?` or several maths signs.

## Speed

The board has no GPU, so we timed all three engines on the CPU, on the same 100 images, with 1 and
4 threads. 4 is the board's core count. Laptop run, 2026-11-15. The board run is
[not done yet](#run-the-speed-test-on-the-board).

**Setup, fixed before the run.**

- **Images.** 100 images drawn at random (seed 41) from the 2,277 text-only rows: 34 English, 33
  Catalan, 33 Spanish. `laptop/ocr_speed.py pick` writes them as files.
- **Engines.** The same engine settings as the accuracy runs, with the GPU off. The onnxruntime
  thread count (`intra_op_num_threads`) or Tesseract's (`OMP_THREAD_LIMIT`) is set to 1 or 4.
- **Cores.** Each run is pinned with `taskset` to 1 or 4 separate performance cores of the
  i7-13700H. These are cores 0, 1, 4 and 5, all with a 4.8 GHz maximum. Laptop on AC power, CPU
  governor `powersave` (the default).
- **What is timed.** 3 warm-up images first, then each image one at a time. **Load** is the time to
  start the engine. For PP-OCR, it is building the engine object. For Tesseract, it is one command
  call on a blank image. Tesseract runs through its command line, one call per image, so each call
  loads the model again. This is what the copilot would pay per problem.
- **Repeats.** Each configuration ran twice. If the two medians differed by more than 10 %, it ran a
  third time. This happened for PP-OCRv4 and Tesseract with 1 thread.
- **Check.** Each engine found five options in as many images as in the accuracy run on the same 100
  images: PP-OCRv4 93, PP-OCRv5 92, Tesseract 71. So the CPU runs read the same way as before.

**Laptop results.** Seconds per image. Each cell gives the range over the runs.

| Engine | Threads | Runs | Median | 90th percentile | Load | Peak memory |
|---|---|---|---|---|---|---|
| PP-OCRv4 | 1 | 3 | 2.68–3.03 s | 4.8–5.8 s | 0.3–0.5 s | 0.9–1.0 GB |
| PP-OCRv4 | 4 | 2 | 2.28–2.44 s | 3.3–3.5 s | 0.6–0.8 s | 0.9–1.0 GB |
| PP-OCRv5 | 1 | 2 | 2.75–3.01 s | 5.1–5.2 s | 0.7–0.8 s | 0.86 GB |
| PP-OCRv5 | 4 | 2 | 2.12–2.17 s | 2.9–3.0 s | 0.8 s | 0.86 GB |
| Tesseract | 1 | 3 | 0.41–0.47 s | 0.6–0.7 s | 0.3 s | 60 MB |
| Tesseract | 4 | 2 | 0.44 s | 0.6–0.7 s | 0.3 s | 60 MB |

- **Tesseract is about 5 to 7 times faster per image.** This holds with both thread counts.
- **More threads help little.** Going from 1 to 4 threads cuts PP-OCRv5's median by about 25 % and
  PP-OCRv4's by about 20 %. It does not change Tesseract's. For PP-OCR, the 90th percentile drops
  more: the large images gain the most.
- **Model loading is a small share for Tesseract.** One call on a list of the 100 images, where the
  model loads once, takes 0.30–0.36 s per image, against about 0.45 s with one call per image.
- **Memory.** PP-OCR peaks at 0.86–1.0 GB, Tesseract at 60 MB. The PP-OCR environments on the laptop
  also hold the GPU build of onnxruntime. Part of their memory may come from that, and the
  CPU-only build on the board could use less. We did not measure this.

**What it means for the board.** The 60 s budget per problem must cover the OCR and the language
model. The language model alone takes 5 to 10 s per problem without examples, and about 30 s
with 2 RAG examples ([board guide](../BOARD_SETUP.md#start-the-explorer)). The board's Arm cores are much
slower than these laptop cores, so both OCR times will grow. By how much, only the board run can
tell. PP-OCR's peak memory of about 1 GB also matters on a board with 3.6 GB, which already holds
the two model servers.

The old figures from the full accuracy runs used other hardware and other settings, so they are
not comparable to the table:
- Tesseract: 2,277 images in 139 s, 16 threads in parallel on the laptop CPU.
- PP-OCRv5: about 8 minutes on the laptop GPU ([PP-FormulaNet report](2026-11-ppformulanet.md#summary)).

### Run the speed test on the board

Not run yet: the board was not connected. `board/ocr_speed.sh` runs the same 6 configurations, twice
each, with the model services running as in real use. It records free RAM before and after, and
any out-of-memory kill.

The board needs, each to be approved when the board is connected:

1. Tesseract: `sudo apt install tesseract-ocr` (needs the sudo password).
2. A separate Python environment, so that the copilot's own stays untouched:
   ```bash
   python3 -m venv ~/venvs/ocr-speed
   ```
   ```bash
   ~/venvs/ocr-speed/bin/pip install onnxruntime rapidocr==3.10.0 rapidocr_onnxruntime==1.4.4 pillow
   ```
3. Copy from the laptop (on the laptop, with the board's IP):
   - the Tesseract models: `data/external/tessdata/*.traineddata` to the same folder on the board;
   - the PP-OCR models, so both machines use the same files: `rapidocr/models/` (43 MB) and
     `rapidocr_onnxruntime/models/` (16 MB), from the laptop environments to the same place in
     `~/venvs/ocr-speed`;
   - the 100 test images and the key list: `data/interim/speed/images/` and
     `data/interim/speed/keys.txt`.
4. On the board, from `~/Santolina_tutor`: first check what is missing, then run the test.
   ```bash
   bash board/ocr_speed.sh --check-only
   ```
   ```bash
   bash board/ocr_speed.sh
   ```
5. Copy `data/interim/speed/board-*.json` back to the laptop, then delete
   `data/interim/speed/images` on the board (the images are M3Kang, for research use only).

## Accuracy against speed and memory

This table puts the accuracy figures from above next to the laptop CPU speed and memory. Nothing in
it is new, except the two estimated rows.

| Engine | Question CER (no spaces) | Rows with 5 options | Gold rows, all 5 right | Seconds per image, 1 thread (4 threads) | Peak memory |
|---|---|---|---|---|---|
| PP-OCRv4 | 21.6 % | 89.2 % | 48 of 60 | 2.7–3.0 (2.3–2.4) | 0.9–1.0 GB |
| PP-OCRv5 | 9.5 % | 93.5 % | 55 of 60 | 2.8–3.0 (2.1–2.2) | 0.86 GB |
| Tesseract | 2.3 % | 75.5 % | 39 of 60 | 0.41–0.47 (0.44) | 60 MB |
| PP-OCRv5, then PP-OCRv4 (today) | — | 98.5 % | 56 of 60 | about 3.1, estimated | about 1.9 GB if both stay loaded, estimated |
| PP-OCRv5, then Tesseract | — | 97.4 % | 56 of 60 | about 2.9, estimated | about 0.9 GB, estimated |

**How the estimates are made.** The second engine runs only on the rows where PP-OCRv5 reads no
options, about 6.5 % of them.
- **Time:** the PP-OCRv5 median (2.9 s), plus 6.5 % of the second engine's median.
- **Memory:** both engines loaded at the same time. Loading the second engine only when it is
  needed uses less memory, but adds its load time to those rows.

We did not measure either combination.

- **Tesseract trades the options for speed and memory.** It is about 6 times faster than PP-OCRv5
  and needs about 15 times less memory. But it gets all five options right in 16 fewer gold rows
  (39 against 55 of 60). The options matter more than the question, because only the image has them.
- **Tesseract as the fallback keeps today's accuracy for less memory.** "PP-OCRv5, then Tesseract"
  gets the same 56 gold rows right as "PP-OCRv5, then PP-OCRv4". It needs about 1 GB less, if the
  fallback engine stays loaded. The cost: it reads five options in fewer rows (97.4 % against
  98.5 %).
- **For the question text, Tesseract is better on all three measures:** error rate, time and
  memory.
- **These are laptop figures.** The board run, prepared but not done, will show whether PP-OCR fits
  the 60 s budget and the 3.6 GB of RAM next to the two model servers. That decides whether its
  better options are worth its cost on the board.

## Limitations

- **One Tesseract setup.** We used no preprocessing (scaling, binarization, cropping) and the
  default page layout. Another setup could read the labels better.
- **The parser is tuned to PP-OCR.** Its label rules come from PP-OCR output. A rule that accepts
  `Cc)` as `C)` would likely recover many Tesseract rows. We did not write one: it would be fitted
  to this test.
- **An AI agent wrote the option gold.** No person checked it. Claude wrote it without seeing any
  engine output, so this is not a bias towards an engine.
- **60 gold rows.** The Tesseract–PP-OCRv5 gap on the gold is large (18 against 2), but small
  differences, such as between the two fallbacks, cannot be seen at this size. A few gold rows are
  the same problem in two languages, and the McNemar test treats them as independent. At 18 against
  2 this does not change the verdict.
- **One file, three languages, text-only rows.** Rows with a figure are not measured.
- **The reading order and the cut are shared.** Both may hurt an engine whose boxes differ in
  shape. The cut fired less often for Tesseract, which raises its question CER.

## Next steps

- **Find why PP-OCR drops lines.** Tesseract shows the lines are readable. Compare the PP-OCRv5
  detector boxes with Tesseract's line boxes on a few short rows. Try a larger detector input.
- **If the question text comes from the image:** test Tesseract for the question and PP-OCRv5 for
  the options. For Catalan, test `cat+eng` (two models at once), which can write `?` and the maths
  signs.
- **A Tesseract-aware parser** only with a new gold sample, so that it is not tuned to this one.

## Appendix: reproducibility

| Item | Value |
|---|---|
| Tesseract | 5.5.0, leptonica 1.86.0, `--oem 1 --psm 3`, no preprocessing |
| Models | `tessdata_best` commit `e12c65a915945e4c28e237a9b52bc4a8f39a0cec`, in `data/external/tessdata/` (not in Git) |
| SHA256 `eng.traineddata` | `8280aed0782fe27257a68ea10fe7ef324ca0f8d85bd2fd145d1c2b560bcb66ba` |
| SHA256 `cat.traineddata` | `dbddfce4cc65e5b127566d85243fe4422ef321f028b74ccf8db5c253f227a61a` |
| SHA256 `spa.traineddata` | `e2c1ffdad8b30f26c45d4017a9183d3a7f9aa69e59918be4f88b126fac99ab2c` |
| Boxes | `data/interim/ocr_boxes_txto_yes_tess.jsonl` (Tesseract), and the PP-OCR boxes of the earlier report. Not in Git: M3Kang is for research use only |
| Option gold | `data/interim/optx/gold3_pick.json` and `options_gold3.json`. Not in Git |
| Code | `laptop/ocr_boxes.py` (`--engine tess`), `laptop/ocr_vs_text.py` (`--tess`), `laptop/option_consensus.py` (`gold3-pick`, `engines`) |
| Output | the printed figures, and `data/interim/ocr_vs_text_tess.csv`: one row per problem, language and engine, with no problem text |
| Speed | `laptop/ocr_speed.py` (`pick`, `run`, `report`) and `board/ocr_speed.sh`. Images and results in `data/interim/speed/` (not in Git) |

Get the models (from the repository root):

```bash
mkdir -p data/external/tessdata
```

```bash
for l in eng cat spa; do curl -fsSL -o data/external/tessdata/$l.traineddata https://raw.githubusercontent.com/tesseract-ocr/tessdata_best/e12c65a915945e4c28e237a9b52bc4a8f39a0cec/$l.traineddata; done
```

Run Tesseract on the text-only rows:

```bash
.venv/bin/python -I laptop/ocr_boxes.py dump --engine tess --workers 16 --languages eng,cat,esp --out data/interim/ocr_boxes_txto_yes_tess.jsonl data/raw_txto_yes/*.parquet
```

Score the question text and the options:

```bash
.venv/bin/python -I laptop/ocr_vs_text.py --tess data/interim/ocr_boxes_txto_yes_tess.jsonl
```

```bash
.venv/bin/python -I laptop/option_consensus.py engines
```

Time the engines on the laptop CPU (repeat for each engine, 1 and 4 threads, with `taskset -c 0,2,8,10`
for 4 threads; PP-OCRv4 runs in `~/.venvs/ocr-v4`, Tesseract in `.venv`):

```bash
.venv/bin/python -I laptop/ocr_speed.py pick
```

```bash
taskset -c 0 ~/.venvs/ocr-v5/bin/python -I laptop/ocr_speed.py run --engine v5 --threads 1 --out data/interim/speed/laptop-v5-t1-r1.json
```

```bash
.venv/bin/python -I laptop/ocr_speed.py report data/interim/speed/laptop-*.json
```

Without `--tess`, `ocr_vs_text.py` prints the same figures as before and writes the same
`data/interim/ocr_vs_text.csv`. We checked this with a byte-for-byte diff. `gold3-pick` (seed 31)
draws the same 60 rows again and writes the option-band sheets that the gold was written from.
