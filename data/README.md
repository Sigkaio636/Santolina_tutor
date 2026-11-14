# Data

This folder holds the problem files. In Git it has only this README and `sample_problems.jsonl`. That file holds five made-up problems in the [M3Kang](../GLOSSARY.md) format, for smoke tests (quick checks that the copilot runs end to end).

You create the M3Kang files only on your machine (see [Local files](#local-files)). Don't commit them. The M3Kang license allows research use only. See the [dataset card](https://huggingface.co/datasets/qualcomm/M3Kang). To create them, follow [step 9 of the board setup](../docs/BOARD_SETUP.md#step-9-prepare-m3kang-on-your-laptop).

Each line holds one problem. Here the example uses three lines, so that it is easy to read. In the file it is one line:

```json
{"id": "lvl-0_2015_13", "language": "eng", "level": 0, "year": 2015, "text_only": true,
 "text": "13. For 3 days, the cat Joy has been catching mice. ...",
 "options": {"A": "12", "B": "15", "C": "18", "D": "20", "E": "24"}, "label": "C"}
```

OCR (optical character recognition) reads the options as text from the problem image. `options` is `{}` when OCR couldn't read five text options, for example when the options are pictures. Then the language model sees only the question. The [`m3kang-copilot` skill](../.claude/skills/m3kang-copilot/SKILL.md) has more on how the copilot uses this data.

## Fields

`laptop/prepare_m3kang.py` writes these fields, in this order.

| Field | Type | What it holds |
| --- | --- | --- |
| `id` | string | The problem ID, such as `lvl-0_2015_13`. The translations of a problem share its `id`, so `id` and `language` together identify one row. |
| `language` | string | The M3Kang language code, such as `eng` or `cat`. |
| `level` | integer | One of the 8 difficulty levels. Level 0 is grade 5. |
| `year` | integer | The year of the problem, taken from the second part of `id`. |
| `text_only` | boolean | The `text_only` flag, copied from M3Kang. |
| `text` | string | The question, without the options. In M3Kang the options are only in the image. |
| `options` | object | The options `A` to `E` that OCR read from the image, or `{}`. |
| `label` | string | The correct answer: one letter, A to E. |

## Local files

These files are in `data/` on your machine. `.gitignore` keeps them out of Git.

| File | Written by | What it holds |
| --- | --- | --- |
| `train.jsonl`, `val.jsonl` | `laptop/prepare_m3kang.py` | The training problems and the validation set, split by problem ID |
| `.ocr_cache.jsonl` | `laptop/prepare_m3kang.py` | The options already read by OCR, so a second run does not read them again |
| `images/` | `laptop/prepare_m3kang.py --save-images` | One PNG per problem, for the explorer (`explorer/server.py`) |
| `index.db` | `build_index.py` | The retrieval index of `train.jsonl` |
| `raw/` | No script in this repository writes it | The M3Kang parquet shards that `santolina_tutor/dataset.py` reads |
| `interim/m3kang/` | `santolina_tutor/dataset.py` (`make data`) | `problems.jsonl` and the problem images, extracted from `raw/` |
