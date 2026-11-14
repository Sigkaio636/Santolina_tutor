# Experiment: PP-FormulaNet (LaTeX OCR) for the answer options

Should we read the answer options of M3Kang problems with PP-FormulaNet, an OCR model that writes LaTeX? This report is for the team and the datathon judges. Laptop run, 2026-11-14, branch `exp/decider-0.8b`.

The task: read the five answer options, A to E, from the image of each Kangaroo maths problem ([M3Kang](https://huggingface.co/datasets/qualcomm/M3Kang)). The options are only in the image. [OCR failure modes](../OCR_FAILURE_MODES.md) explains how we read them today and where that fails.

## Summary

- **Decision: PP-FormulaNet is not adopted.**
- **It is slow.** With the best settings we tested, the medium model needs 1.4 s for one option on the laptop CPU. For all the options of the 2,277 text-only rows in English, Catalan and Spanish, that is about 4.5 hours. It also runs after PP-OCRv5, which finds the option labels it crops from, so its time adds to the time of PP-OCRv5.
- **It shows no gain.** On 20 options it reads 16 exactly, against 15 for PP-OCRv5. It is right on 2 options where PP-OCRv5 is wrong, and wrong on 1 where PP-OCRv5 is right. An exact McNemar test on these 3 options gives p = 1.0. This is no evidence of a difference.
- **The test does not cover the main case.** We chose the options from what PP-OCRv5 reads. So options that PP-OCRv5 misreads as plain numbers, such as stacked fractions, rarely enter the sample. See [Decision and what would reopen it](#decision-and-what-would-reopen-it).

## Why we tried a LaTeX OCR

After the parser fixes and PP-OCRv5, OCR reads five options for 98.5% of the text-only rows in English, Catalan and Spanish (see [What this means](../OCR_FAILURE_MODES.md#what-this-means-for-improving-option-reading)). Some of those options are still wrong. The errors cluster in maths layout: stacked fractions come out as two numbers, exponents become normal digits, and stray characters appear. A model trained on formulas, with LaTeX as output, could read this layout better.

PP-FormulaNet is the formula recognizer of PaddleOCR. It takes the image of one formula and returns LaTeX. It comes in three sizes: S, M and L (the `_plus` versions). L reads the image at 768 × 768 pixels, M and S at 384 × 384.

## What we compared

**The options.** We took the text-only rows (`text_only` true) of the first `high_quality` file of M3Kang in Catalan and Spanish: 1,466 rows (811 Catalan, 655 Spanish). A simple text rule (`kind()` in `laptop/formula_trial.py`) sorts the options that PP-OCRv5 reads. We chose 20 at random (seed 4):

| Kind | Options available | Chosen |
| --- | --- | --- |
| Words, such as names or `b or c` | 38 | 8 |
| A number with a unit, such as `12 cm` or `5 €` | 751 | 6 |
| A formula with letters, such as `x + 3` | 132 | 6 |

The examples are short generic values. Some match options in the sample. The kinds are rough. 3 of the 8 "words" options are letter sequences or a ratio, not words. 2 of the 6 "formula" options are a number with a unit and an exponent.

We chose the hard kinds on purpose and left out plain numbers, most of the options. The rule reads the PP-OCRv5 value, not the image. A stacked fraction that PP-OCRv5 reads as two bare numbers matches no kind. It can enter only with a unit or a sign such as `€` after it. An exponent read as a normal digit enters only in some forms. So the rule makes stacked fractions rare in the sample, and none of the 20 options is one. None of the 20 options has a letter with an accent.

**The crops.** PP-FormulaNet reads one formula, not a page. For each option, we cut a crop out of the image, from its label (`A)`) to the next label on the same line. PP-OCRv5 gives the position of the labels. We made two kinds of crop:

- **Wide:** a large margin around the option. It often holds a piece of the question or the end of the next option.
- **Tight:** a small margin, extended down and to the left when the option continues on a second line.

**The reference.** Claude, the coding agent of this project, wrote the right value of each option from its crop.

**The score.** An option counts as right when the output equals the reference after a normalization. The normalization removes the label, spaces, LaTeX wrappers such as `\text{}` and `$`, and line breaks inside a word. So `A)$x+1$` and `x + 1` are equal.

**The runs.** PP-OCRv5 values come from its parsed output. `pick` falls back to PP-OCRv4 when PP-OCRv5 reads no options, but all 20 values came from PP-OCRv5 (see [PP-OCRv5 compared with PP-OCRv4](../OCR_FAILURE_MODES.md#pp-ocrv5-compared-with-pp-ocrv4)). PP-FormulaNet ran on the CPU (Intel Core i7-13700H), with PaddlePaddle 3.3.1, PaddleOCR 3.7.0 and PaddleX 3.7.2. The first prediction of each run is a warm-up and is not timed.

## Results

| Run | Crop | CPU threads | Mean s per option | Max s | Right (of 20) |
| --- | --- | --- | --- | --- | --- |
| PP-OCRv5 (parsed) | none: whole image | — | — | — | 15 |
| PP-FormulaNet M | wide | 10 | 10.65 | 87.14 | 3 |
| **PP-FormulaNet M** | **tight** | **10** | **1.43** | **2.32** | **16** |
| PP-FormulaNet M | tight | 20 | 1.81 | 2.87 | 16 |
| PP-FormulaNet L | tight | 10 | 6.89 | 9.02 | 15 |
| PP-FormulaNet S | tight | 10 | 0.40 | 0.79 | 4 |

PP-OCRv5 ran on the GPU, over the whole image, so it has no time per option.

What the outputs of model M show:

- **Better than PP-OCRv5:** exponents, such as `x^{4}` where PP-OCRv5 reads `x4`, and options on two lines, which PP-OCRv5 mixes across columns.
- **Worse than PP-OCRv5:** the euro sign comes out as `\textcircled{e}`, and it misreads letters in names.

## What controls the time

From the largest effect to the smallest:

1. **The crop.** With wide crops, 2 of the 20 outputs ran away. The model repeated one symbol until it stopped, after 86 s and 87 s. These two crops took 81% of the time of the run. In both, the crop held text from outside the option, which is the likely cause. Tight crops gave no runaway output, and the mean time went from 10.65 s to 1.43 s, 7 times faster.
2. **The model size.** M is the best trade-off. L is about 5 times slower and is not more accurate here. S is 3.5 times faster, but it adds false accents (`\hat{1}`, `\tilde{4}`) and drops digits.
3. **CPU threads.** 10 threads, the default, was faster than 20, in one run each. This CPU has 6 performance cores and 8 efficiency cores, 20 threads in total.
4. **MKL-DNN.** PaddleX turns off this CPU acceleration for PP-FormulaNet by default. PaddleX has a setting that overrides this. We did not try it.
5. **The GPU.** Not measured. It needs PaddlePaddle 3 with CUDA, which is not on PyPI (PyPI has only version 2.6.2, too old for PaddleOCR 3). PaddleX also offers no ONNX, TensorRT or OpenVINO path for this model. This is the one large speed-up we did not test.

Running PP-FormulaNet only on the options that need it would cut the total time. But to choose those options we would need a rule, and a rule on the PP-OCRv5 output misses the fractions that PP-OCRv5 misreads.

## Decision and what would reopen it

We do not adopt PP-FormulaNet. On the laptop CPU it adds hours of work to PP-OCRv5, and on this sample it shows no gain.

We would test it again if both of these are true:

- in one GPU run that times both models, PP-FormulaNet adds no more time per row than PP-OCRv5 takes.
- on a new reference set, PP-FormulaNet reads more options right than PP-OCRv5, with an exact McNemar test at p < 0.05. We must choose the options of this set from the images or the reference values, not from the PP-OCRv5 output. Then it can include stacked fractions.

Other OCR models that write LaTeX can use the same crops and reference: UniMERNet (also in PaddleOCR), GOT-OCR2.0, and vision-language models such as Qwen2.5-VL. We did not test them.

## Limitations

- **20 options.** A difference of one or two options means nothing at this size. The test can show a large gain or a large loss, not a small one.
- **The reference is by Claude, and it can lean toward PP-OCRv5.** No person checked it. Claude saw the PP-OCRv5 value of each option while it wrote the reference. When a crop is hard to read, this can favour PP-OCRv5.
- **Selection by PP-OCRv5.** The sample has no plain numbers, so it does not stand for all options.
- **Crop errors.** One tight crop still cuts the start of a second line. This costs PP-FormulaNet that option, and the crop rule may need work on other layouts.
- **Crop rule tuned on the sample.** We set the tight-crop rule while we looked at these same 20 crops. This can only favour PP-FormulaNet.
- **CPU only**, one laptop, one file of the dataset, two languages.
- **Different tasks.** PP-OCRv5 reads a whole image on the GPU. PP-FormulaNet reads one crop on the CPU. The times show the cost of each path as we ran it, not a like-for-like speed test.

## Appendix: reproducibility

All the steps are in `laptop/formula_trial.py`. They need both box files from `laptop/ocr_boxes.py` (PP-OCRv4: `data/interim/ocr_boxes_txto_yes.jsonl`, PP-OCRv5: `data/interim/ocr_boxes_txto_yes_v5.jsonl`) and the file `data/raw_txto_yes/high_quality-00000-of-00004.parquet` from `laptop/split_text_only.py`. `crop` reads only this first file. This works because all the Catalan and Spanish rows are in it: the other three files have no rows in these languages. The steps write under `data/interim/`, which Git ignores: the files hold M3Kang text, which is for research use only.

```bash
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

`run` needs PaddleOCR 3 and `paddlex[ocr]`. We used a separate environment for them. Claude wrote the reference file, `data/interim/formula_gold.json`, by hand. The script does not produce it.
