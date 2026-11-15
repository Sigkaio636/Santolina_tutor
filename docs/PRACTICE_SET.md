# The organizers' practice set and what it says about the hidden test

On 2026-11-14 the organizers sent every team a practice set and described the [hidden test](https://github.com/Sigkaio636/Santolina_tutor/blob/main/GLOSSARY.md). This page is for team members who prepare the copilot for that test. It records what the organizers said, how to load and score the practice set, and what we measured on it. For the rest of what the challenge asks, see [the challenge musts](GOAL_MUSTS.md). Terms such as row, text-only row and coverage are in the [glossary](https://github.com/Sigkaio636/Santolina_tutor/blob/main/GLOSSARY.md).

The practice file is not in this repository. The repository is public, the file's license is "other", and the organizers sent it to the teams only. Get `demo-00000-of-00001.parquet` from the organizers' message, or from a teammate, and put it at `data/demo-00000-of-00001.parquet`. Git ignores `data/`.

## What the organizers said

The organizers' dataset card comes with the practice file (`data/demo-README.md`, not in this repository). It says:

- The practice set has 50 new Kangaroo-style problems, each in English and Catalan: 100 rows. The organizers wrote the problems for the datathon. They are not M3Kang problems.
- The hidden test has 20 different problems, at levels 0 to 7. Each problem comes in one language. Four of the 20 have a figure.
- The organizers run the hidden test with our `predict.py`, after the last call at 12:00 on Sunday 15 November 2026.
- At most 60 seconds per problem, and no network. These are rules of the [contract](https://github.com/Sigkaio636/Santolina_tutor/blob/main/GLOSSARY.md).

The card does not say what file `predict.py` receives. It also does not say if the options arrive as text or only in the image. It does not name the languages of the hidden test.

## The columns of the practice file

The practice file has the same columns as M3Kang:

| Column | Content |
| --- | --- |
| `id` | `lvl-<level>_2026_<number>`. Translations share the `id`. |
| `level` | 0 to 7. The organizers write that level 0 is grade 5. |
| `language` | `eng` or `cat` |
| `text_only` | `false` if the problem needs its figure (see "Text-only row" in the glossary) |
| `image` | The full problem: statement, figure if any, and the options A) to E) |
| `text` | `"<number>. <statement>"`, without the options |
| `label` | The correct letter |

As in M3Kang, the options are only in the image. `laptop/prepare_m3kang.py` reads them with OCR (optical character recognition).

## How to load and score it

You need [uv](https://docs.astral.sh/uv/) on your laptop, as in [step 9.1 of the board guide](BOARD_SETUP.md#91-install-the-requirements).

1. On your laptop, read the options with OCR and write the rows to `data/demo/train.jsonl`:

    ```bash
    uv run --no-project --python 3.12 --with-requirements laptop/requirements.txt \
      python laptop/prepare_m3kang.py --parquet data/demo-00000-of-00001.parquet \
      --languages eng,cat --val-fraction 0 --out data/demo
    ```

    `--val-fraction 0` puts all 100 rows in `data/demo/train.jsonl`. Add `--save-images` to also save each problem image as a PNG under `data/demo/`.

    **Check:** the summary at the end gives `train cat: 50` and `train eng: 50`, and `wc -l data/demo/train.jsonl` gives 100, and the line `Options read from the image:` gives `100/100`.

2. On your laptop, score the [prior solver](https://github.com/Sigkaio636/Santolina_tutor/blob/main/GLOSSARY.md) on the 50 English rows. The prior solver is today's default (`SOLVER=prior` in `config.env`). It calls no model, so no model server is necessary:

    ```bash
    python3 eval.py --input data/demo/train.jsonl --languages eng --limit 0 --name demo-prior
    ```

    `--limit 0` scores every row. Without it, `eval.py` scores only 50 rows.

    **Check:** the `Accuracy:` line counts 50 rows (`<correct>/50`). The script writes one CSV file per run to `results/` and adds one line to `results/ablations.csv`.

3. On the board, score the [baseline](https://github.com/Sigkaio636/Santolina_tutor/blob/main/GLOSSARY.md) (`SOLVER=letter`): the language model gives one letter per problem. This step needs the `math-llm` service on port 8081 ([step 7 of the board guide](BOARD_SETUP.md#step-7-run-both-models-as-services)). First, on your laptop, copy the file to the board. Use your board's address, as in [step 10](BOARD_SETUP.md#step-10-copy-the-data-to-the-board):

    ```bash
    ssh arduino@192.168.1.131 mkdir -p Santolina_tutor/data/demo
    scp data/demo/train.jsonl arduino@192.168.1.131:~/Santolina_tutor/data/demo/
    ```

    Or over USB:

    ```bash
    adb shell mkdir -p /home/arduino/Santolina_tutor/data/demo
    adb push data/demo/train.jsonl /home/arduino/Santolina_tutor/data/demo/
    ```

    Then, on the board:

    ```bash
    cd ~/Santolina_tutor
    systemctl is-active math-llm
    SOLVER=letter python3 eval.py --input data/demo/train.jsonl --languages eng --limit 0 --name demo-letter
    ```

    `systemctl` must print `active`. The variable `SOLVER=letter` overrides `config.env` for this command only.

    **Check:** the `Status:` line gives `{'ok': 50}`. A `timeout` or `error` count means that the model did not answer those rows, and they got the fallback letter D.

## What we measured on 2026-11-14

!!! note "Dated record"
    We measured these values on the laptop on 2026-11-14, before commit `f72d3e8` (15 November 2026). Since that commit, the prior solver answers D on every figure row, so the prior solver score below is for the earlier rule. We did not measure again, and we did not keep a results file.

| Measure | Value |
| --- | --- |
| Rows | 100: 50 English, 50 Catalan |
| Text-only rows | 80 (40 problems). The other 20 rows (10 problems) need a figure. |
| Coverage (all five options read by OCR) | 100 of 100 rows, figure rows included |
| Correct letter | Each of A to E is correct 20 times |
| Options that are five distinct numbers in increasing order | 90 of 100 rows |
| Statement length | Median 128 characters, longest 299 |
| Problems per level, 0 to 7 | 8, 8, 7, 6, 6, 5, 5, 5 |

Scores on the 50 English rows:

| Solver | Correct |
| --- | --- |
| One letter for all rows | 10 of 50 (20%) |
| The prior solver (`SOLVER=prior`), rule before `f72d3e8` | 8 of 50 (16%) |
| The baseline letter from Qwen3.5 0.8B (`SOLVER=letter`) | 12 of 50 (24%). It answered D 36 times. |

## What we conclude

- `SOLVER=prior` is today's default. We recommend that the final build does not keep it. On M3Kang the prior solver scored more than the model's letter ([try the prior solver](how-to/try-prior-solver.md)). Almost all of its gain over always D came from numeric options listed out of order. In the practice set, the numeric options are in increasing order (90 of 100 rows, table above). On 2026-11-14 the prior solver scored 8 of 50, no better than one letter for all rows (10 of 50).
- The problems are new. A search for the same problem in M3Kang or in past papers will not find them.
- Most options are numbers (90 of 100 rows), and the statements are short. The next work is solvers that compute the value: written steps, or a short program in a sandbox. We also test larger models that still answer in 60 seconds.
- With 20 problems in the hidden test, one answer is 5 percentage points. Small differences between solvers on the practice set are noise. Compare solvers on all 50 problems. To score the Catalan rows, run steps 2 and 3 with `--languages cat`, and report that score apart. The Catalan rows are translations of the same 50 problems. The scores above are for the English rows only.
