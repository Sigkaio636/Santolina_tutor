# Models

This page lists every model the project uses or tested, its role, and whether the shipped build runs it. `config.env` pins each public model of the shipped build by repository, revision, file and SHA256. It pins llama.cpp by commit (`2cbe0ec`).

## In the shipped build

| Model | Role | Service and port | Pinned in `config.env` | Record |
| --- | --- | --- | --- | --- |
| Qwen3.5 0.8B, Q8_0 (`bartowski/Qwen_Qwen3.5-0.8B-GGUF`) | One letter per problem when `SOLVER=letter` | `math-llm`, 8081 | `LLM_REPO`, `LLM_REVISION`, `LLM_FILE`, `LLM_SHA256` | [Board setup 11.3](../BOARD_SETUP.md#113-what-we-measured) |
| bge-small-en-v1.5, Q8_0 (`CompendiumLabs/bge-small-en-v1.5-gguf`) | Embeddings for the retrieval index | `math-embed`, 8082 | `EMBED_REPO`, `EMBED_REVISION`, `EMBED_FILE`, `EMBED_SHA256` | [Board setup step 12](../BOARD_SETUP.md#step-12-try-retrieval-rag) |
| `qwen35-tutor`, Q8_0: our LoRA fine-tune of Qwen3.5 0.8B | Clues and chat replies in the student app | `math-tutor`, 8084 | `TUTOR_FILE` only. The model is private. Its SHA256 is in the README. | [Fine-tune record](qwen35-tutor.md) |

With the default `SOLVER=prior`, `predict.py` calls no model.

## Tested, not in the shipped build

| Model | Tested for | Result | Record or report |
| --- | --- | --- | --- |
| decider-0.8b (`Mapika/decider-0.8b`) | One letter per problem | 24.0 % against 22.4 % on 789 M3Kang rows, p = 0.50. 15 of 100 on the practice set. Not adopted. | [Experiment](../experiments/2026-11-decider-0.8b.md), [install guide](../how-to/install-decider-0.8b.md) |
| decider-2b, Q4_K_M (`Mapika/decider-2b-GGUF`) | Intent router | 87.6 % on 250 messages. The router to try on the board. | [Round 3](../experiments/2026-11-router-bakeoff-3.md), [guide](../how-to/use-decider-2b-router.md) |
| Intern-Decision-0.8B | Intent router | 51 % in round 1. Not adopted. | [Round 1](../experiments/2026-11-router-bakeoff.md) |
| decider-2b-vision | Figure problems | 24.4 % with the image, below always D. Not adopted. | [Record](decider-2b-vision.md) |
| InternVL3.5-1B | Figure problems | 17.1 % with the image, below always D. Not adopted. | [Record](internvl3.5-1b.md) |
| Qwen2.5-Math-1.5B-Instruct, Q4_K_M | Writes a Python program for each problem | 55 of 100 on the practice set, laptop at board speeds. On a branch. | [Solving](../experiments/solving/index.md) |
| softcatala/translate-cat-eng (CTranslate2) | Translates Catalan to English before the program | Catalan from 14 to 26 of 50 on the practice set | [Solving](../experiments/solving/index.md) |
| Noema-2B | Program writer and one letter | 37 of 100 (program) and 24 of 100 (letter) on the board | [Solving](../experiments/solving/index.md) |

## How a record page works

A record page keeps one row per run, with the date, the rows, the input, the accuracy, the floor and a link to the report. It also keeps the current verdict. The reports keep the design and the limits of each run.

To add a record, copy the layout of [decider-2b-vision](decider-2b-vision.md), and add the page to `nav:` in `mkdocs.yml`.
