# How to try the prior solver on the board

This guide runs the first evaluation build on the Arduino UNO Q and measures it on the validation set. The build answers each problem from a rule about the options, without calling the language model, so a full run takes seconds.

## What the build does

`copilot/prior.py` picks a letter from the options alone:

- When the five options are distinct numbers, it answers the median value. Kangaroo distractors sit around the right value, so the smallest and the largest option are rarely correct.
- In every other case (text options, fewer than five options, no options) it answers `FALLBACK_ANSWER` from `config.env`, which is D.

`copilot/pipeline.py` reads the new setting `SOLVER` in `config.env`:

| Value | What `solve()` does |
| --- | --- |
| `prior` (the default) | Returns the prior's letter. No model call. |
| `letter` | The earlier baseline: one forced letter from the model. The prior's letter is the answer if the model fails or is too slow. |

`predict.py` is unchanged. The rule needs no data file on the board.

We chose this as the first build because of a laptop run on 300 English training problems with options, with the same model file and llama.cpp commit as the board. The model's forced letter scored 21.7%, always D scored 25.0%, and the prior scored 27.3%.

## Before you start

- The board is set up to [step 10 of the board guide](../BOARD_SETUP.md#step-10-copy-the-data-to-the-board): the repository is cloned and `data/val.jsonl` is on the board.
- You can reach the board with `ssh` or `adb` ([step 0](../BOARD_SETUP.md#step-0-connect-to-the-board)).

## 1. Get the build

On the board, in the repository folder:

```bash
cd ~/Santolina_tutor
git status --short
git pull
```

If `git status` lists `config.env` as changed, keep your changes and add this line by hand after the pull:

```bash
SOLVER=prior
```

Without internet on the board, copy the three files from a laptop that has pulled `main`:

```bash
scp copilot/prior.py copilot/pipeline.py arduino@192.168.1.131:~/Santolina_tutor/copilot/
scp config.env arduino@192.168.1.131:~/Santolina_tutor/
```

Use your board's address or user if they differ.

## 2. Check the contract

```bash
mkdir -p results
python3 predict.py --input data/sample_problems.jsonl --output results/check.csv
cat results/check.csv
```

You should see five rows. Each `answer` is one letter from A to E, each `status` is `ok`, and each `seconds` value is close to 0:

```text
id,language,answer,seconds,status
sample-1,eng,C,0.0,ok
sample-2,eng,B,0.0,ok
sample-3,eng,C,0.0,ok
sample-4,cat,C,0.0,ok
sample-5,cat,C,0.0,ok
```

## 3. Measure it on the validation set

```bash
python3 eval.py --limit 0 --name prior
python3 eval.py --limit 0 --languages cat --name prior-cat
python3 eval.py --limit 0 --languages esp --name prior-esp
```

What the laptop measured on the same validation set:

| Language | Problems | Prior | Always D |
| --- | --- | --- | --- |
| English | 281 | 27.8% | 23.1% |
| Catalan | 281 | 28.1% | 23.1% |
| Spanish | 227 | 28.2% | 21.6% |

The board should print the same accuracies, because the rule uses no model and no random number. Almost all of the gain comes from problems whose numeric options are listed out of order, about 19% of the set. On those the median value is right 36% to 38% of the time.

## 4. Report the result

Send the three lines that `eval.py` added to `results/ablations.csv`, and say if any accuracy differs from the table above. A difference means the board's `data/val.jsonl` is not the file the laptop used, and we need to know that before the next build.

## 5. Compare with the model's letter (optional)

To run the earlier baseline without editing any file:

```bash
SOLVER=letter python3 eval.py --limit 50 --name letter-check
```

This one calls the model, so it takes about 9 seconds per problem.

## Go back to the baseline

Set `SOLVER=letter` in `config.env`. The services don't need a restart: the setting is read by the Python code, and the model servers are the same.

## If you work with Claude on the board

Give it this request:

> Read docs/how-to/try-prior-solver.md and follow steps 1 to 4 on the board. Use the unoq-board skill to connect. Don't change any code. Report the three new lines of results/ablations.csv and any accuracy that differs from the guide's table.
