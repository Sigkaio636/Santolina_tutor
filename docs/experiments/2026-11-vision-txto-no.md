# Experiment: Qwen3.5-0.8B with the problem image, on figure problems

Status: **pre-registered on 2026-11-14, before the full run.** Results are added
below the line "Results" after the runs. Laptop run, branch `exp/decider-0.8b`.

The task: pick the right letter (A–E) for multiple-choice maths problems from the
Kangaroo competition ([M3Kang](https://huggingface.co/datasets/qualcomm/M3Kang)).
This experiment uses only the problems that come with a figure (`text_only` is
false, "txto_no"), and grades each answer against the dataset's `label` column.

## Why

The M3Kang paper (Torres-Camps et al., 2026, §4.4) finds that every capable model
does worse on figure problems than on text-only ones. Our copilot never sees the
figure: it gets the problem text and, in about half the rows, the options read by
OCR. Qwen3.5-0.8B can see images through its vision projector (mmproj, +205 MB),
and the board runs it at 28–38 s per problem with `--image-max-tokens 128`
([BOARD_SETUP](../BOARD_SETUP.md), Explorer section). Before this run we had only
two problems tried by hand, both answered wrong.

## Data

- `high_quality` shard 0, validation split of `laptop/prepare_m3kang.py`
  (by problem id), languages eng, cat and esp, `text_only` false:
  **440 rows** (eng 158, cat 158, esp 124). OCR found the five options in 224 rows
  and none in 216.
- Images come from the same shard, split by `laptop/split_text_only.py`
  (`data/raw_txto_no/`), matched by problem id and language.

## Runs

| Run | Model input | Source |
|---|---|---|
| `baseline` | problem text + OCR options, no image | existing `laptop-baseline` run (789 rows), restricted to the 440 figure rows |
| `vision-img128` | image (≤128 image tokens) + problem text + OCR options | `laptop/eval_vision.py` |

Same model file, llama.cpp commit, server flags, grammar `root ::= [A-E]`,
temperature 0 and seed 42 as the [decider-0.8b report](2026-11-decider-0.8b.md).
The vision server adds `--mmproj` and `--image-max-tokens 128`. Two 50-row vision
runs gave identical letters.

## Decision rule (fixed before the full run)

Send the image for figure problems only if all three hold:

1. On the 440 rows, `vision-img128` accuracy is above the best one-letter floor
   (always answering the most common letter of these rows), with the lower end of
   its 95 % Wilson interval above that floor.
2. It beats `baseline` on the same 440 rows, with an exact McNemar test p < 0.05.
3. On the board, 20 of 20 rows finish in under 60 s.

Otherwise the result is recorded as negative and the copilot stays text-only.
We also report the "figure, no options" stratum separately: it is where the image
could help most, because the text alone has no options there.

## Results

Laptop run, 2026-11-14. Accuracy against `label`, 95 % Wilson interval, exact
McNemar test against `baseline` paired by problem id and language.

| Rows | n | Best one-letter floor | `baseline` (text) | `vision-img128` | McNemar (only baseline right / only vision right) |
|---|---|---|---|---|---|
| All | 440 | 25.2 % (D) | 22.5 % [18.8–26.6] | **17.3 %** [14.0–21.1] | 76 / 53, p = 0.052 |
| Figure, 5 OCR options | 224 | 26.3 % (B) | 21.9 % [17.0–27.7] | 15.2 % [11.1–20.5] | 34 / 19, p = 0.053 |
| Figure, no OCR options | 216 | 29.6 % (D) | 23.1 % [18.0–29.2] | 19.4 % [14.7–25.2] | 42 / 34, p = 0.422 |
| eng | 158 | 25.9 % (D) | 22.8 % | 13.3 % | 27 / 12, p = 0.024 |
| cat | 158 | 25.9 % (D) | 24.7 % | 17.7 % | 31 / 20, p = 0.161 |
| esp | 124 | 23.4 % (B, D) | 19.4 % | 21.8 % | 18 / 21, p = 0.749 |

Letters answered by `vision-img128` (answered / true): A 95/75, **B 0/99**,
C 6/95, D 169/111, **E 170/60**. With the image the model never answers B and gives
E almost three times as often as it is right. The text baseline has the opposite
skew (B 161, E 12). Both runs mostly track a letter preference, not the problem.

Latency on the laptop: mean 2.0 s, worst 3.2 s, no timeouts. Prompts were 230–290
tokens with the image.

### Decision

**Not adopted. The copilot stays text-only for figure problems.**

1. Floor: fails. 17.3 % is below the 25.2 % of always answering D, and the whole
   interval lies below it.
2. Better than `baseline`: fails. The image run is worse (−5.2 pp, p = 0.052).
   It is significantly worse in English (p = 0.024).
3. Board timing: not run. Rules 1 and 2 already fail, so the board test can't
   change the decision.

In the stratum where the image should help most (no OCR options), it does not:
19.4 % against 23.1 % for the text baseline.

### Limits

- **128 image tokens.** The board needs this cap to stay under 60 s. When it
  loads the projector, llama.cpp warns that Qwen-VL models need at least 1024
  image tokens for grounding tasks. At 128 tokens the model may not read the
  figure, or the option labels, well. A laptop-only run without the cap would
  show how much of the loss comes from the cap. The result would not be
  deployable: by the BOARD_SETUP measurements, more image tokens take 68–185 s
  on the board.
- **One model, one prompt.** The prompt is the copilot's standard one
  (`copilot/llm.py`, image before text). We tuned nothing for the image.
- **Laptop only.** Board latency for this exact run is not measured.
- 440 rows, three languages, shard 0 only.

### Follow-up: no image-token cap (laptop only)

This run checks whether the 128-token cap explains the loss. It uses the same 440
rows, model and prompt, and starts the server without `--image-max-tokens`.
Prompts grew from 230–290 tokens to 327–1001. The laptop limit was 300 s per row.
This setup can't be deployed: by BOARD_SETUP, images of this size take 68–185 s on
the board.

| Rows | n | `baseline` (text) | `vision-img128` | `vision-imgdefault` | McNemar baseline vs imgdefault |
|---|---|---|---|---|---|
| All | 440 | 22.5 % | 17.3 % | **16.6 %** [13.4–20.4] | 77 / 51, p = 0.027 |
| Figure, 5 OCR options | 224 | 21.9 % | 15.2 % | 16.1 % | 35 / 22, p = 0.111 |
| Figure, no OCR options | 216 | 23.1 % | 19.4 % | 17.1 % | 42 / 29, p = 0.154 |
| eng | 158 | 22.8 % | 13.3 % | 15.8 % | 26 / 15, p = 0.117 |
| cat | 158 | 24.7 % | 17.7 % | 15.8 % | 32 / 18, p = 0.065 |
| esp | 124 | 19.4 % | 21.8 % | 18.5 % | 19 / 18, p = 1.000 |

The capped and uncapped runs don't differ: 16 rows only the capped run got right,
13 only the uncapped one, p = 0.711. The letter skew stays the same (A 90, B 2,
C 8, D 148, E 192, against true counts 75/99/95/111/60). Laptop latency: mean
4.2 s, worst 10.9 s, no timeouts.

**Reading:** the cap is not the bottleneck. With up to about 1000 image tokens,
the model still does worse than the text baseline, and significantly worse
overall (p = 0.027). Qwen3.5-0.8B doesn't use the Kangaroo figures to choose the
letter. The decision stays "not adopted".

## Reproduce

Data: [M3Kang](https://huggingface.co/datasets/qualcomm/M3Kang) `high_quality`
shard 0, prepared as in the decider-0.8b report, then split with
`python3 laptop/split_text_only.py`. Vision projector:
`bartowski/Qwen_Qwen3.5-0.8B-GGUF` @ `f36b1ea4`, `mmproj-Qwen_Qwen3.5-0.8B-f16.gguf`,
SHA256 `1dc1351c82e41b48edb55fd6ddfa7ca60fb5a16b3d5abf3ce7054880dd022847`. Start the
server as in BOARD_SETUP (Explorer section), with the model path on your machine.

```bash
python3 laptop/eval_vision.py --limit 0 --name vision-img128
```

`compare_runs.py` needs a validation file restricted to the 440 figure rows
(`text_only` false, eng/cat/esp), here `data/interim/val_txto_no.jsonl`. It stays
out of Git like the rest of `data/`:

```bash
python3 laptop/compare_runs.py data/interim/val_txto_no.jsonl \
    baseline=results/eval-<time>-laptop-baseline.csv \
    vision=results/eval-<time>-vision-img128.csv
```
