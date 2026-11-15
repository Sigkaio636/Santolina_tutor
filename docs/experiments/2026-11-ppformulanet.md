# Experiment: PP-FormulaNet (LaTeX OCR) for the answer options

This report records whether we should read the answer options of M3Kang problems with PP-FormulaNet, and why we decided not to. PP-FormulaNet is an OCR model (optical character recognition: it reads text from an image) that writes LaTeX, a text format for maths formulas. The report is for the team and the datathon judges. Laptop run, 2026-11-14, branch `exp/decider-0.8b`.

The task: read the five answer options, A to E, from the image of each Kangaroo maths problem ([M3Kang](https://huggingface.co/datasets/qualcomm/M3Kang)). The options are only in the image, and the copilot model needs them to pick an answer. [OCR failure modes](../OCR_FAILURE_MODES.md) explains how we read them today and where that fails.

Some words on this page:

- A **row** is one problem in one language.
- A **text-only** row has `text_only` set to true in M3Kang: its question needs no figure.
- **PP-OCRv5** is the OCR model we now use to read the options. Its output goes through a parser that finds the labels `A)` to `E)` and the value after each one (see [PP-OCRv5 compared with PP-OCRv4](../OCR_FAILURE_MODES.md#pp-ocrv5-compared-with-pp-ocrv4)).
- A **stacked fraction** has its numerator above its denominator, with a bar between them.
- The **reference value** of an option is its value as written in the image. A run is **right** on an option when its output equals the reference value after normalization.

## Summary

- **Decision: PP-FormulaNet is not adopted.**
- **It is slow.** The medium-size model (M) needs 1.43 s for one option on the laptop CPU, with the best settings we tested. For the 2,277 text-only rows in English, Catalan and Spanish, that is 2,277 × 5 options × 1.43 s, about 4.5 hours. PP-OCRv5 reads the same rows in about 8 minutes on the GPU, at about 5 rows per second. The devices differ, so this is not a like-for-like test (see [Limitations](#limitations)). We timed only 20 hard options in Catalan and Spanish and assume the same time for all options.
- **Its time adds to PP-OCRv5.** PP-FormulaNet reads a crop of one option. PP-OCRv5 must run first to find where each option is.
- **It shows no gain.** On 20 options, PP-FormulaNet M is right on 16 and PP-OCRv5 on 15. The two disagree on only 3 options: PP-FormulaNet is right on 2 of them, PP-OCRv5 on 1. An exact McNemar test, a test for paired results that uses only these disagreements, gives p = 1.0. This is no evidence of a difference. Claude, the coding agent of this project, wrote the reference values with the PP-OCRv5 values in view. This can favour PP-OCRv5 (see [Limitations](#limitations)).
- **The test does not cover the main case.** We chose the 20 options with a rule that reads the PP-OCRv5 text, not the image. A stacked fraction that PP-OCRv5 reads as two plain numbers does not pass this rule, and none of the 20 options is one. See [Decision and what would reopen it](#decision-and-what-would-reopen-it).

## Why we tried a LaTeX OCR

The option parser has two fixes, for missing `C)` and `A)` labels. With these fixes and PP-OCRv5, OCR reads five options for 93.5% of the text-only rows in English, Catalan and Spanish. With PP-OCRv4 as a fallback when PP-OCRv5 reads no options, this goes to 98.5% (see [What this means](../OCR_FAILURE_MODES.md#what-this-means-for-improving-option-reading)). Some of those options are still wrong. The errors cluster in maths layout: stacked fractions come out as two numbers, exponents become normal digits, and stray characters appear. A model trained on formulas, with LaTeX as output, could read this layout better.

PP-FormulaNet is the formula recognizer of [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR). It takes the image of one formula and returns LaTeX. We used its newer `_plus` versions, in three sizes: small (S), medium (M) and large (L). L reads the image at 768 × 768 pixels, M and S at 384 × 384 (the `inference.yml` file of each model).

## What we compared

**The options.** M3Kang has four `high_quality` files. We took the first one, `high_quality-00000-of-00004.parquet`. From it we used the text-only rows in Catalan and Spanish: 1,466 rows (811 Catalan, 655 Spanish). A simple text rule (`kind()` in `laptop/formula_trial.py`) puts each option that OCR reads (PP-OCRv5, or PP-OCRv4 when PP-OCRv5 reads no options) into a kind. The `pick` step of that script then chose 20 options at random, with its default seed, 4.

Kinds of the 7,220 options that OCR reads in these rows:

| Kind | Options | Chosen |
| --- | --- | --- |
| Words, such as names or `b or c` | 38 | 8 |
| A number with a unit, such as `12 cm` or `5 €` | 751 | 6 |
| A formula with letters, such as `x + 3` | 132 | 6 |
| No kind, mostly plain numbers | 6,299 | 0 |

The examples are short generic values. Some match options in the sample. The kinds are rough. 3 of the 8 "words" options are letter sequences or a ratio, not words. 2 of the 6 "formula" options are a number with a unit and an exponent.

We chose the hard kinds on purpose and left out the plain numbers. The rule reads the PP-OCRv5 text, not the image:

- A stacked fraction that PP-OCRv5 reads as two plain numbers gets no kind. Such a fraction enters only when a unit or a sign such as `€` follows it.
- An exponent that PP-OCRv5 reads as a normal digit enters only in some forms. One example is a formula with a letter and an operator.

So the rule makes stacked fractions rare in the sample, and none of the 20 options is one. None of the 20 has a letter with an accent.

**The crops.** PP-FormulaNet reads one formula, not a page. For each option, the `crop` step cuts a part of the image, from the option's label (`A)`) to the next label on the same line. PP-OCRv5 gives the position of the labels. We made two kinds of crop, with margins in units of the label height:

- **Wide:** 1.6 to the left, 1.2 above and 2.2 below. The crop often holds a piece of the question or the end of the next option.
- **Tight:** 0.35 above and below, extended down and to the left when the option continues on a second line.

**The reference values.** Claude wrote the reference value of each option from its crop.

**The score.** Before the comparison, the normalization removes from both texts:

- the option label, such as `A)`,
- spaces,
- LaTeX wrappers such as `\text{}` and `$`,
- a hyphen between two letters, as in a word split over two lines.

So `A)$x+1$` and `x + 1` are equal.

**The runs.**

- PP-OCRv5: the options that the parser reads from its output. All 20 options came from PP-OCRv5.
- PP-FormulaNet: the CPU of the laptop (Intel Core i7-13700H), PaddlePaddle 3.3.1, PaddleOCR 3.7.0 and PaddleX 3.7.2.
- The first prediction of each PP-FormulaNet run is a warm-up and is not timed.

## Accuracy and time per run

PP-OCRv5 ran on the GPU over whole images, at about 5 rows per second. It reads all five options of a row at once, so it has no time per option.

| Run | Crop | CPU threads | Mean s per option | Max s | Right (of 20) |
| --- | --- | --- | --- | --- | --- |
| PP-OCRv5 | none: whole image | — | — | — | 15 |
| PP-FormulaNet M | wide | 10 | 10.65 | 87.14 | 3 |
| **PP-FormulaNet M** | **tight** | **10** | **1.43** | **2.32** | **16** |
| PP-FormulaNet M | tight | 20 | 1.81 | 2.87 | 16 |
| PP-FormulaNet L | tight | 10 | 6.89 | 9.02 | 15 |
| PP-FormulaNet S | tight | 10 | 0.40 | 0.79 | 4 |

What the outputs of model M show:

- **Better than PP-OCRv5:** exponents, such as `x^{4}` where PP-OCRv5 reads `x4`. Also options that wrap onto a second line: there PP-OCRv5 adds text from the next option.
- **Worse than PP-OCRv5:** the euro sign comes out as `\textcircled{e}` (a circled letter e), and it misreads letters in names.

## What controls the time

From the largest effect to the smallest:

1. **The crop.** With wide crops, 2 of the 20 outputs ran away. The model repeated one symbol for 86 s and 87 s, most likely until it reached its maximum output length (`max_seq_len`: 2560 in its `inference.yml`). These two crops took 81% of the time of the run. In both, the crop held text from outside the option, which is the likely cause. Tight crops gave no runaway output, and the mean time went from 10.65 s to 1.43 s, 7 times faster.
2. **The model size.** M is the best trade-off. L is about 5 times slower and is not more accurate here. S is 3.5 times faster, but it adds false accents (`\hat{1}`, `\tilde{4}`) and drops digits.
3. **CPU threads.** 10 threads, the default of `formula_trial.py run`, was faster than 20, in one run each. This CPU has 6 performance cores and 8 efficiency cores, 20 threads in total.
4. **MKL-DNN**, an Intel library that speeds up neural networks on the CPU. PaddleX turns it off for PP-FormulaNet by default. The environment variable `PADDLE_PDX_DISABLE_MKLDNN_MODEL_BL` overrides this. We did not try it.
5. **The GPU.** Not measured. It needs PaddlePaddle 3 built for CUDA, the NVIDIA GPU platform. On 2026-11-14, `uv pip install --dry-run paddlepaddle-gpu` resolved only version 2.6.2 on PyPI, the Python package index. That version is too old for PaddleOCR 3. PaddlePaddle 3 GPU builds are on Paddle's own package index, which we did not try. PaddleX also offers no faster runtime for this model (ONNX, TensorRT or OpenVINO). This is the one large speed-up we did not test.

Running PP-FormulaNet only on the options that need it would cut the total time. But to choose those options we would need a rule, and a rule on the PP-OCRv5 output misses the fractions that PP-OCRv5 misreads.

## Decision and what would reopen it

We do not adopt PP-FormulaNet. On the laptop CPU it adds hours of work to PP-OCRv5, and on this sample it shows no gain.

We would test it again if both of these are true:

- In one GPU run that times both models, PP-FormulaNet adds no more time per row than PP-OCRv5 takes.
- On a new set of reference values, PP-FormulaNet is right on more options than PP-OCRv5, with an exact McNemar test at p < 0.05.

For the new set, we must choose the options from the images or the reference values, not from the PP-OCRv5 output. Then it can include stacked fractions.

Other open models that write LaTeX can use the same crops and reference values. Examples are UniMERNet (also in PaddleOCR) and GOT-OCR2.0. Vision-language models, which read images and text together, are another option, for example Qwen2.5-VL. We did not test them.

## Limitations

- **20 options.** A difference of one or two options means nothing at this size. The test can show a large gain or a large loss, not a small one.
- **The reference values are by Claude, and they can lean toward PP-OCRv5.** No person checked them. Claude saw the PP-OCRv5 value of each option while it wrote the reference values. When a crop is hard to read, this can favour PP-OCRv5.
- **Selection by PP-OCRv5.** The sample has no plain numbers, so it does not stand for all options.
- **Crop errors.** One tight crop still cuts the start of a second line. This costs PP-FormulaNet that option, and the crop rule may need work on other layouts.
- **Crop rule tuned on the sample.** We set the tight-crop rule while we looked at these same 20 crops. This can only favour PP-FormulaNet.
- **CPU only**, one laptop, one file of the dataset, two languages.
- **Different tasks.** PP-OCRv5 reads a whole image on the GPU. PP-FormulaNet reads one crop on the CPU. The times show the cost of each path as we ran it, not a like-for-like speed test.

## Appendix: reproducibility

All the steps are in `laptop/formula_trial.py`. They write under `data/interim/`, which Git ignores: the files hold M3Kang text, which is for research use only.

The steps need three inputs:

- the text-only rows, from `laptop/split_text_only.py`, in `data/raw_txto_yes/`,
- the PP-OCRv4 boxes, `data/interim/ocr_boxes_txto_yes.jsonl`, from `laptop/ocr_boxes.py`,
- the PP-OCRv5 boxes, `data/interim/ocr_boxes_txto_yes_v5.jsonl`, from `laptop/ocr_boxes.py`.

`crop` reads only the first `high_quality` file. This works because all the Catalan and Spanish rows are in it. `laptop/ocr_boxes.py` needs `rapidocr_onnxruntime` for PP-OCRv4 and `rapidocr` 3 for PP-OCRv5. `run` needs PaddleOCR 3 and `paddlex[ocr]`. We used a separate environment for each.

```bash
python laptop/split_text_only.py
python laptop/ocr_boxes.py dump --engine v4 --languages eng,cat,esp --out data/interim/ocr_boxes_txto_yes.jsonl data/raw_txto_yes/*.parquet
python laptop/ocr_boxes.py dump --engine v5 --languages eng,cat,esp --out data/interim/ocr_boxes_txto_yes_v5.jsonl data/raw_txto_yes/*.parquet
python laptop/formula_trial.py pick
python laptop/formula_trial.py crop --wide --out data/interim/formula_crops
python laptop/formula_trial.py crop --out data/interim/formula_crops_tight
python laptop/formula_trial.py run --model PP-FormulaNet_plus-M --crops data/interim/formula_crops
python laptop/formula_trial.py run --model PP-FormulaNet_plus-M --crops data/interim/formula_crops_tight
python laptop/formula_trial.py run --model PP-FormulaNet_plus-M --crops data/interim/formula_crops_tight --threads 20
python laptop/formula_trial.py run --model PP-FormulaNet_plus-S --crops data/interim/formula_crops_tight
python laptop/formula_trial.py run --model PP-FormulaNet_plus-L --crops data/interim/formula_crops_tight
python laptop/formula_trial.py score
```

Claude wrote the reference values by hand, in `data/interim/formula_gold.json`. The script does not produce this file.
