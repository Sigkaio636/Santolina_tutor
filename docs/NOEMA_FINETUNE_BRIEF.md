# Brief for the Noema-2B fine-tune: board facts, results and recommendations

This page is for Ferran and for the Claude session that works with him on the Noema-2B fine-tune. It collects what we measured on the board on 2026-11-14 and 2026-11-15, and what the team tried. It also gives what the literature says, and our recommendations for the fine-tune and the pipeline around it. Pau has the board and runs the final tests on it. Ferran tests on his laptop first.

**If you are a Claude session reading this page:** treat the numbers in [Board facts](#1-board-facts-measured) as the limits of the design. Do not change `config.env`, `predict.py` or the board services. Prepare the items in [What to send Pau](#7-what-to-send-pau-for-the-board-test), and Pau runs the board test. M3Kang data and the practice parquet never go into Git (see `CLAUDE.md`).

## Summary

- **A forced letter does not work at this size.** On the organizers' practice set, every solver scores between 15 % and 24 %. Any fixed letter scores 20 %. Each model answers mostly one letter.
- **The answer must be computed.** The best evidence for small models is code that the model writes and Python runs. For Qwen2.5-Math-1.5B, code execution gives 79.9 on MATH, against 75.8 for written reasoning.
- **The board limits Noema-2B to about 65–80 written tokens per problem.** It reads 4.86 tokens/s and writes 2.42 tokens/s. So the fine-tune target must be **short code that prints the value**, not an explanation.
- **Python on the board has the standard library only.** No numpy, no SymPy, no pip, no internet. Generated code must use the standard library (`math`, `fractions`, `itertools`) unless we copy a pure-Python package to the board.
- **Code then gives a free check.** If the computed value matches exactly one option, the answer is probably right. If no option matches, use a fallback.

## 1. Board facts (measured)

Arduino UNO Q 4 GB, 4 × Cortex-A53, CPU only, llama.cpp commit `2cbe0ec`. All numbers come from `docs/how-to/time-2b-model-on-board.md`, run by Pau on the board.

| Measure | Noema-2B Q4_K_M | Qwen3.5-0.8B Q8_0 (default) |
|---|---|---|
| File | 1.27 GB | 835 MB |
| RAM of the server (RSS) | 1,382 MB | about 900 MB |
| RAM still available with the model loaded | about 2.8 GB | about 2.8 GB |
| Load time | 6 s | — |
| Reading speed (prompt) | 4.86 tokens/s | about 10–11 tokens/s |
| Writing speed | 2.42 tokens/s | about 4.8 tokens/s |
| One forced letter, practice set, mean / slowest | 17.7 s / 28.1 s | 7.6 s / 13.6 s |
| 74-token program, whole request | 51.5 s | — |
| 132 tokens of worked steps, whole request | 81.1 s (over the limit) | — |

**The time budget.** `predict.py` stops at 60 s, and `copilot/pipeline.py` keeps a margin of 3 s. Plan for 55 s:

```text
new prompt tokens / 4.86  +  written tokens / 2.42  +  code run time  <=  55 s
```

**The server keeps the start of the prompt.** A second run of the same request read only 4 tokens. So the fixed part of the prompt (system prompt, examples) costs time only once per server start. Each problem pays only for its own tokens. A practice problem with its options is about 110 tokens: about 23 s of reading. That leaves about 30 s, or **about 70 written tokens**. Put few-shot examples in the fixed prefix, never after the problem.

**Server options of the service** (keep them in every test, laptop and board):

```text
--threads 4 --ctx-size 4096 --parallel 1 --cache-ram 0 --ctx-checkpoints 2 --jinja --reasoning off --reasoning-budget 0
```

## 2. What the team tried, and the results

### On the organizers' practice set (100 rows: 50 problems, English and Catalan)

| Solver | Right | English | Catalan | Letters answered |
|---|---|---|---|---|
| Noema-2B, forced letter | 24 % | 12/50 | 12/50 | C 84 |
| Qwen3.5-0.8B, forced letter (baseline) | 22 % | 12/50 | 10/50 | D 73 |
| Prior solver | 16 % | 8/50 | 8/50 | C 90 |
| decider-0.8b | 15 % | 9/50 | 6/50 | D 42 |
| Any fixed letter | 20 % | | | |

No difference from the baseline is significant (exact McNemar: Noema p = 0.88, prior p = 0.42, decider p = 0.26). The board gives the same baseline and prior scores as Ferran's laptop. Details: `docs/experiments/2026-11-practice-set-on-board.md` and `docs/experiments/2026-11-noema-2b-board-timing.md` on branch `exp/noema-2b-board-timing`.

### On M3Kang (earlier)

| What | Result |
|---|---|
| Baseline, 50 validation problems | 20 % |
| Retrieval of one solved example (`--rag 1`) | 14 %, 2 × slower |
| One line of reasoning (organizers, `BOARD_SETUP.md` §11.3) | 17.5 %, 26 s per problem |
| Vision model reading the image | 28–38 s per problem, wrong on the 2 problems tried |
| decider-0.8b (Eki, laptop, 789 rows) | 24.0 % against 22.4 %, p = 0.50 |
| Prior solver (board, 562 rows) | 27.4 %, but 16 % on the practice set |
| OCR parser fixes and PP-OCRv5 (Eki) | Options found on 76 % → 98.5 % of text-only rows |

**What this tells us.** The options are no longer the main problem: OCR reads them on all 100 practice rows. The models cannot compute the answer. On M3Kang, step-by-step reasoning gives only about 30 % for Qwen2.5-3B and about 40 % for Qwen2.5-7B (M3Kang paper, Table 2). A letter with no reasoning from a 0.8B–2B model is close to chance.

## 3. Recommendations for the fine-tune

1. **Train the model to write a short program that prints the value.** Example of the target format (a made-up problem):

    ```python
    n = sum(1 for k in range(1, 201) if k % 3 == 0 and k % 5 != 0)
    print(n)
    ```

    - At most about **70 tokens** of output. Count tokens with the Noema tokenizer, and drop training examples above the limit.
    - No explanation, no markdown fence, no `def` or `if __name__` unless they are short. One `print` of the final value.
    - Standard library only: `math`, `fractions`, `itertools`. The board has no SymPy or numpy.
    - Where the problem is "which of these options…", let the program test each option and print the letter. Use this format only for problems that have no single value to compute.

2. **Keep only programs that are right.** Generate programs with a larger teacher, and run each one. Keep a program only if its value matches the labelled option. This is rejection sampling, as in Li 2025. TinyGSM did not check correctness, and used a verifier at test time instead. We have the label, so filter.

3. **Use the same program for the English and the Catalan text of a problem.** The final test has both languages, one each problem. The model then learns to read Catalan without a translation step. Noema-2B's model card lists English only, so check Catalan separately in every evaluation.

4. **Short beats long for small models.** Li 2025: for Qwen2.5-1.5B, short CoT training scored 34.2 against 27.0 for long CoT. Our budget makes short code the only option anyway.

5. **Split by problem id, not by row.** The same problem exists in several languages. A Catalan copy in training and the English copy in evaluation is a leak.

6. **Keep the practice set for evaluation only.** It has 50 problems. Tuning prompts or data on it overfits. Use M3Kang problems with options for training, and the practice set to measure.

7. **Sampling.** The Noema-2B model card says not to use greedy decoding (temperature 0). The challenge rule says the same answers every time (`BOARD_SETUP.md` §11.1): temperature 0 and a fixed seed. Test both on the laptop. If a temperature above 0 is better, keep a fixed seed and check that two runs give the same answers.

## 4. The pipeline around the model

This is what turns a program into a letter. It is pure Python, so it can be tested on the laptop with no model.

1. **Prompt.** Fixed prefix (instruction and few-shot examples), then the problem text and the options `A) … E)`. Cap the output with `n_predict` at the token limit.
2. **Run the code in a sandbox.** `subprocess.run([sys.executable, "-I", "-c", code], timeout=...)`, with a time limit of a few seconds and `resource.setrlimit` on memory. Allow only standard-library imports. The board is offline, so network access is no risk.
3. **Match the value to the options.** Parse each option as a number (decimal comma, fractions such as `3/4`, units such as `12 cm`). Compare with a small tolerance. A letter that the program printed counts directly.
4. **Decide.**
    - The value matches exactly one option: answer that letter.
    - It matches none or several, the code fails, or the time is short: use the fallback.
5. **Fallback.** The forced letter of the model, with the letter bias removed. PriDe does this: it estimates the prior of each letter by shuffling the options on a few problems, then divides it out. Every model we tried leans to one letter, so this matters for the fallback.
6. **Time guard.** Measure time from the start of `solve()`. Never call the model again if the remaining time cannot hold a full request.

Where the code goes: a new `SOLVER` value in `copilot/pipeline.py` (for example `SOLVER=program`), next to `prior` and `letter`. `predict.py` stays as it is: it is the organizers' contract.

## 5. Test on the laptop first

The laptop is much faster than the board, so laptop seconds mean nothing for the 60-second limit. **Measure tokens on the laptop, and convert them to board time.**

1. Build `llama-server` at the board's commit:

    ```bash
    git clone https://github.com/ggml-org/llama.cpp ~/llama.cpp-laptop
    cd ~/llama.cpp-laptop && git checkout 2cbe0ec429b849a88664e0f62388fc92a5abd699
    cmake -B build && cmake --build build -j --target llama-server llama-quantize
    ```

2. Run the model with the service options of [section 1](#1-board-facts-measured).
3. For each practice problem, record `prompt_n` and `predicted_n` from the response's `timings`. Then estimate the board time:

    ```text
    board seconds ≈ prompt_n / 4.86 + predicted_n / 2.42 + code run time
    ```

    For the 0.8B model, use 10 and 4.8 tokens/s.

4. **Check these before you send anything to Pau:**
    - The estimated board time of the slowest practice problem is 50 s or less. Use the first run, which reads the whole prompt.
    - Accuracy on all 100 practice rows, by language, against the baseline of 22 %. Report the exact McNemar test too.
    - The share of rows where the value matches exactly one option, and the accuracy on those rows.
    - Two runs give the same 100 answers.

## 6. Make the GGUF reproducible

- **Pass `--model-name` to `convert_hf_to_gguf.py`.** Without it, the converter writes the name of the input folder into the file. Two conversions of the same weights from two folder names gave the same tensors and two different SHA256s (decider-0.8b, `docs/experiments/2026-11-practice-set-on-board.md`).
- Quantize to **Q4_K_M**. That is the quantization we timed. Another one changes the speeds of [section 1](#1-board-facts-measured), so tell Pau if you change it.
- Record the SHA256 of the final file.
- Keep the file out of Git (`*.gguf` is in `.gitignore`).

## 7. What to send Pau for the board test

1. **The GGUF file** (a shared drive or USB, not Git) and its SHA256.
2. **The branch and commit** with the pipeline code.
3. **The settings** to use on the board. Send the `config.env` lines: `LLM_FILE`, `LLM_SHA256`, `LLM_ALIAS`, `SOLVER`, and any new ones. Send the server options too if they differ from [section 1](#1-board-facts-measured).
4. **The laptop results** of [section 5](#5-test-on-the-laptop-first): accuracy by language, the estimated board time of the slowest problem, and the match rate.
5. **The exact command** for the board, for example:

    ```bash
    python3 eval.py --input data/demo/train.jsonl --limit 0 --name <name>
    ```

The board has no internet while its own Wi-Fi is on. Pau copies files to it with `adb`, so a large file takes about 35 s per GB.

## 8. Ideas to try if there is time

| Idea | Evidence | On the board |
|---|---|---|
| Equations for the solver instead of a full program (SymPy) | Equal to program-writing on GSM8K, +20 points on harder algebra (He-Yueya 2023) | SymPy and mpmath are pure Python: Pau can copy them to the board. Shorter output than a program |
| Two short programs, and keep the value they agree on | Answers that a program checks beat plain majority votes. Agreement between 2 samples is a strong signal | Probably too slow for Noema-2B. Possible for the 0.8B model |
| Speculative decoding: Qwen3.5-0.8B drafts tokens for Noema-2B | They share the Qwen3.5 tokenizer. Reported 1.7–2 × on code on other CPUs | Not measured on the A53. The two models share 4 cores. Both fit in RAM. Pau can test it in about 15 minutes |
| Qwen2.5-Math-1.5B-Instruct as the base | 79.9 on MATH with code execution | No official GGUF of the Instruct model. Same size class as Noema-2B, so about the same speed |

**Not worth the time:**

- Ensembles of small models: strong models fail on the same problems (Igualde-Sáez 2025).
- Retrieval: the practice problems are new.
- Long reasoning: too slow.
- Images: the figure problems are 4 of 20. Accept the loss.

## 9. Open risks

- **The input of the final test is not known yet.** `predict.py` reads JSONL with `options` "when available". The organizers' files are parquet with the options only in the image. Ask them. Eki works on OpenCV crops to OCR as little as possible. The board has no OpenCV, numpy or PIL, so his tool must come with offline packages.
- **Catalan.** Noema-2B is English only per its model card. It got 12 of 50 in both languages with a forced letter, but code from a Catalan statement is not tested.
- **20 problems in the final test.** One answer is 5 points. Compare solvers on all 100 practice rows, not on a few.

## Sources

- Qwen2.5-Math technical report: <https://arxiv.org/abs/2409.12122>, and the [model card](https://huggingface.co/Qwen/Qwen2.5-Math-1.5B-Instruct)
- Intel DeepMath, a small model with a Python sandbox: <https://huggingface.co/blog/intel-deepmath>
- TinyGSM: <https://arxiv.org/abs/2312.09241>. Li 2025, small models and long reasoning: <https://arxiv.org/abs/2502.12143>. Both are in `docs/vault/papers/finetuning_distillation/_synthesis.md`
- He-Yueya et al. 2023, equations and SymPy: <https://arxiv.org/abs/2304.09102>
- Program-aided reasoners and calibration: <https://arxiv.org/abs/2311.09553>. Programs as verifiers of votes: <https://arxiv.org/abs/2410.12608>
- PriDe, letter bias in multiple choice: <https://arxiv.org/abs/2309.03882>
- llama.cpp speculative decoding: <https://github.com/ggml-org/llama.cpp/blob/master/docs/speculative.md>
- M3Kang: <https://arxiv.org/abs/2601.16218>. Igualde-Sáez Kangaroo benchmark: <https://arxiv.org/abs/2506.07418>
- Noema-2B: <https://huggingface.co/NoemaAI-labs/Noema-2B>
