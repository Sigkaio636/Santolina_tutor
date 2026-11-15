# decider-2b-vision: model record

This page records decider-2b-vision in this project: its files, how to run it, what it
needs, and one row per run. It is for team members who want to run the model again or add
a run. **Verdict: not adopted** ([why](#verdict)).

Each run's report keeps its design and its limitations. This page keeps the numbers and
the verdict.

Last updated: 2026-11-15.

## Identity

| | |
|---|---|
| Model | [Mapika/decider-2b-vision](https://huggingface.co/Mapika/decider-2b-vision) |
| What it is | A vision version of Mapika's decider-2b. It reads an image and a question with lettered options, and gives one letter in one pass. It is not a chat model. It is also not the [intent router](https://github.com/Sigkaio636/Santolina_tutor/blob/main/GLOSSARY.md): that is the text-only decider-2b v12. |
| Base | Qwen3.5-2B vision-language model, with the text weights of decider-2b **v5** (not the newer v12) |
| Trained on (model card) | Game frames, multiple-choice image tasks from The Cauldron (A-OKVQA, AI2D, ScienceQA, IconQA, TQA, Raven), and text |
| Scores reported by its authors | Raven 0.80, IconQA 0.94, AI2D 0.93, Visual7W 0.89 (held out). No score on a math-diagram benchmark. |
| Languages | English only, by its model card |
| License | Apache-2.0 |
| Code | [github.com/Mapika/decider](https://github.com/Mapika/decider) (`decider/vision/`) |

## Files

From [`mradermacher/decider-2b-vision-GGUF`](https://huggingface.co/mradermacher/decider-2b-vision-GGUF),
revision `13555b9be92e1502f7d89d303a8e4e450f3c5b4a`. The `mmproj` file is the vision
projector: llama.cpp needs it to read images.

| File | Size | SHA256 | Status |
|---|---|---|---|
| `decider-2b-vision.Q8_0.gguf` | 2,012 MB | `11e07e4c6a56856e05ec5b4c98308a8e869607bfaad9e70b94c9a6439c595b9c` | Used in every run below |
| `decider-2b-vision.mmproj-f16.gguf` | 668 MB | `4bbc8f570ad52331cd5594f252db37b5d473d507ef9a3d9b108c024e256dcc18` | Used in every run below |
| `decider-2b-vision.Q4_K_M.gguf` | 1,274 MB | not recorded | Not tested |
| `decider-2b-vision.mmproj-Q8_0.gguf` | 365 MB | not recorded | Not tested |

The files go in `models/`, which Git ignores (`*.gguf`).

## How to run it

On the laptop, from the repository root. You need `llama-server` built from llama.cpp
`2cbe0ec` (the commit pinned in `config.env`). If you do not have it, build it as in
[the intent router guide](../how-to/use-decider-2b-router.md#before-you-start), and use
the path of that build in step 1.

1. Start the server on port 8083 (`VISION_PORT`). Leave out `--image-max-tokens 128` for a
   run at the model's default image size.

   ```bash
   llama-server -m models/decider-2b-vision.Q8_0.gguf \
     --mmproj models/decider-2b-vision.mmproj-f16.gguf --image-max-tokens 128 \
     --threads 4 --ctx-size 4096 --parallel 1 --cache-ram 0 --ctx-checkpoints 2 \
     --jinja --reasoning off --reasoning-budget 0 --host 127.0.0.1 --port 8083
   ```

   Check:
   - `llama-server --version` names commit `2cbe0ec`.
   - `curl -s http://127.0.0.1:8083/health` prints `{"status":"ok"}`.

2. In a second terminal, run the evaluation on a rows file, with `SOLVER=letter` and
   `LLM_PROMPT=decider`:

   ```bash
   SOLVER=letter LLM_PROMPT=decider .venv/bin/python laptop/eval_vision.py \
     --input <rows.jsonl> --languages eng,cat,esp --name <run-name>
   ```

   Add `--no-image` for a blind run on the same server. The rows file of each run below is
   in the Reproduce section of its report. Take only the file names from there: keep
   `SOLVER=letter` and `LLM_PROMPT=decider` from the command above. The rows files stay in
   `data/interim/`, out of Git.

   Check:
   - Each progress line shows more than 0 tokens. 0 tokens means that no model answered
     that row.
   - The `Status:` line at the end shows only `ok`. A failed or timed-out call gives the
     letter D, with the status `error` or `timeout`.

   If every row has 0 tokens and the status `ok`, the run measured the
   [prior solver](https://github.com/Sigkaio636/Santolina_tutor/blob/main/GLOSSARY.md)
   (`SOLVER=prior`, the default in `config.env`), not this model. No check shows that you
   set `LLM_PROMPT=decider`: without it, the model gets the chat prompt and still
   answers. The logs do not record `SOLVER` or `LLM_PROMPT`.

What the two settings do:

- `SOLVER=letter` makes the copilot call the model for every row. With the default
  `SOLVER=prior`, a blind row gets the prior solver's letter and no model call.
- `LLM_PROMPT=decider` makes `copilot/llm.py` send decider's plain prompt to
  `/completion`, with no chat template. The image goes **before** the prompt, as in
  `decider/vision/model.py`. The image placeholder comes from the server's `/props`
  (`media_marker`), because this llama.cpp build picks a random one. For each option that
  OCR did not find, the prompt gives `figure A` (and so on) in an image run, and `option A`
  in a blind run.

## Resources

| Measure | Value | Where |
|---|---|---|
| Server resident memory (RSS), image at most 128 tokens | 2.71 GB idle, 2.77 GB after one image, 2.86 GB after the 175-row run | Laptop, 2026-11-15, `/proc/<pid>/status`. 175-row run: [InternVL report](../experiments/2026-11-internvl35-1b-vs-decider-2b-vision-txto-no.md#results) |
| Server resident memory (RSS), default image size | 2.79 GB idle, peak 2.84 GB | Laptop, 2026-11-15 |
| Prompt tokens per row (median) | Blind: 95. Image, 128 tokens: 213 (`fl-decider2bv-img`) and 218 (`txno-dec-img128`). Image, default size: 600 | [Run log](#run-log) |
| Time per row, laptop CPU, 4 threads (mean) | Blind: 3.2 s. Image, 128 tokens: 8.2 s (`fl-decider2bv-img`) and 3.2 s (`txno-dec-img128`). Image, default size: 21.1 s (worst 45.7 s) | [Run log](#run-log) |
| Time per row on the UNO Q | **Not measured** | — |

The two runs with a 128-token image used the same server flags on the same laptop, but not
the same rows or the same commit. Other jobs wrote files on the laptop during the `fl-` image
runs, so they probably used the CPU too, and these times may be too high. Read every laptop time as a guide only.

We measured memory with `Q8_0`, mmproj `f16` and `--ctx-size 4096`. With only the language
model and embedding services up, the board has about 2.7 GiB (2.9 GB) available
([board reference, 14.4](../UNO_Q_BOARD_REFERENCE.md#144-build-and-services)). This
server uses 2.7 to 2.9 GB, about all of it, and the student app adds the tutor model and
intent router services. So this setup does not fit next to our services.

**Estimate, not measured:** on the board, Qwen3.5-0.8B with a 128-token image took 28 to
38 s per row, on two problems
([BOARD_SETUP.md](../BOARD_SETUP.md#let-the-model-see-the-image-experiment)). On the laptop,
with a 128-token image, decider-2b-vision took 3.2 to 8.2 s per row and Qwen3.5-0.8B 1.4 s
([report](../experiments/2026-11-decider-2b-vision-figure-logic.md#results)): about 2 to 6
times longer. decider-2b-vision is also larger in both parts: 2,012 MB against 835 MB for
the language model (Q8_0), and 668 MB against 205 MB for the projector (f16). So it would
probably take 60 s or more per problem, the limit (`TIME_LIMIT_SECONDS` in `config.env`).

## Verdict

**Not adopted.**

- On the figure logic rows, the image has no effect that the runs can detect. These runs
  cannot rule out a gain of 5 to 10 points.
- No run is above the fixed-letter floor, and every interval contains the floor.
- It does not fit on the board next to our services, and it would probably take 60 s or
  more per problem.

Reopen only if a run on more problems, with one row per problem (for example the 158
English rows among the 440 figure rows of the validation set), shows all of these:

1. The image run beats the blind run: in the McNemar test, a is larger than b, and
   p < 0.05. On about 160 rows, this needs a gain of about 8 points or more. A pass also
   includes the prompt change of the `figure A` / `option A` wording (see the
   [run log](#run-log)).
2. The lower end of the image run's interval is above the floor. On figure rows, the prior
   solver answers D, so this also beats the prior solver.
3. A board measurement shows that it fits in memory and answers in 60 s.

A newer decider vision release, with v12 or later text weights and a llama.cpp mmproj,
must pass the same three tests.

## Run log

Each run asks for one letter, A to E: a grammar (`root ::= [A-E]`) allows no other reply.
Temperature 0, seed 42. "Accuracy" counts the rows where the letter matches M3Kang's answer
(`label`). The interval is a 95 % Wilson interval from `laptop/compare_runs.py`. The
"floor" is the score of the best fixed letter: the highest value on the `floors:` line of
`compare_runs.py`. A run is above the floor only if its whole interval lies above it.

A [row](https://github.com/Sigkaio636/Santolina_tutor/blob/main/GLOSSARY.md) is one problem
in one language (English, Catalan, Spanish). The three languages of one problem are not
independent, so the intervals and the p-values below are narrower and smaller than the
data supports. Read them as a guide only.

| Date | Run | Commit | Rows | Input | Accuracy | Floor | s/row (laptop) | Report |
|---|---|---|---|---|---|---|---|---|
| 2026-11-15 | `fl-decider2bv-blind` | `474f99c` + changes | 160: figure logic rows | no image | 23.8 % [17.8–30.9] | 30.0 % (D) | 3.2 | [figure logic](../experiments/2026-11-decider-2b-vision-figure-logic.md) |
| 2026-11-15 | `fl-decider2bv-img` | `474f99c` + changes | same 160 | image, at most 128 tokens | 24.4 % [18.4–31.6] | 30.0 % (D) | 8.2 | [figure logic](../experiments/2026-11-decider-2b-vision-figure-logic.md) |
| 2026-11-15 | `fl-decider2bv-imgfull` | `474f99c` + changes (log: `9107889`) | same 160 | image, default size | 26.2 % [20.0–33.6] | 30.0 % (D) | 21.1 | [figure logic](../experiments/2026-11-decider-2b-vision-figure-logic.md) |
| 2026-11-15 | `txno-dec-img128` | `401a20a` | 175: a stratified sample of the 440 figure rows of the validation set | image, at most 128 tokens | 22.3 % [16.8–29.0] | 25.1 % (D) | 3.2 | [InternVL3.5-1B vs decider](../experiments/2026-11-internvl35-1b-vs-decider-2b-vision-txto-no.md) |

- "+ changes": changes to `copilot/llm.py` and `laptop/eval_vision.py` that were not
  committed when the run started. They are in commit `5566a4e`.
- `results/ablations.csv` gives `9107889` for `fl-decider2bv-imgfull`: that commit came
  during the run and changed only OCR tools.
- The figure logic rows are 60 problems in English, Catalan and Spanish, at levels 0 to 2.
  Claude labelled their figures as logic or spatial puzzles, and no person checked the
  labels. The report tells
  [how Claude picked them](../experiments/2026-11-decider-2b-vision-figure-logic.md#what-we-compared).
- A figure row is a row that is not a
  [text-only row](https://github.com/Sigkaio636/Santolina_tutor/blob/main/GLOSSARY.md).
- The reports use short names: `dec-blind`, `dec-img128` and `dec-imgfull` in the figure
  logic report, and `dec-img` for `txno-dec-img128` in the InternVL report.

Paired tests on the same rows use the exact McNemar test. "a / b" counts the rows that only
the image run got right, then the rows that only the blind run got right:

- Image (128 tokens) against blind: 18 / 17 rows, p = 1.0.
- Image (default size) against blind: 19 / 15 rows, p = 0.61.

The two runs of a pair differ in two ways, not one. In the 100 rows where OCR did not
find all five options, the prompt also changes: `figure A` with the image, `option A` without it.

## How to add a run

1. Commit your changes under `copilot/` and `laptop/` first: the logs record the commit,
   not uncommitted changes. The log reads the commit at the end of the run, so do not
   commit while a run is going. Then run the model as in [How to run it](#how-to-run-it), with a
   new `--name`: once with the image and once with `--no-image`, on the same rows.
   Check: `results/ablations.csv` ends with one line for each run, with your names.
2. Compare the two runs. Put the image run first:

   ```bash
   .venv/bin/python laptop/compare_runs.py <rows.jsonl> \
     img=results/eval-<time>-<img-name>.csv blind=results/eval-<time>-<blind-name>.csv
   ```

   `<rows.jsonl>` is the `--input` file of step 1. It must hold only the rows of the runs.
   `eval_vision.py` writes one CSV per run, `results/eval-<time>-<name>.csv`.
   Check: the first block, which starts with `== all`, gives the number of rows of your
   runs, the floors, the interval of each run and the McNemar test. If a row of the file is
   not in a CSV, the script stops with `validation rows missing`.
3. Add one row per run to the [run log](#run-log), with its commit. If a setting differs
   from [How to run it](#how-to-run-it), write it in the Input column. Update
   [Resources](#resources) if you measured something new.
4. Link the report of the run. Write no problem text, ids or images on this page: M3Kang is
   for research use only (see the
   [dataset card](https://huggingface.co/datasets/qualcomm/M3Kang)).
