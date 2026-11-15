# How-to guides

Each guide does one task, for a reader who already has a working board or laptop setup. To build the shipped build from the start, follow the [tutorials](../tutorials/index.md) instead.

The last column says if a guide changes what the board runs. "No" means that the guide runs by hand, or on a spare port, and puts the shipped build back at the end.

## The board

| I want to… | Guide | Runs on | Changes the shipped build? |
| --- | --- | --- | --- |
| Save a working board before a change, and go back to it | [Back up and restore a board](back-up-and-restore-a-board.md) | Laptop and board | No |
| Know if a 2B model answers inside 60 seconds | [Time a 2B model](time-2b-model-on-board.md) | Board | No: a spare port, and the default services come back |

## Solvers for `predict.py`

| I want to… | Guide | Runs on | Changes the shipped build? |
| --- | --- | --- | --- |
| Measure the prior solver, the default `SOLVER=prior` | [Try the prior solver](try-prior-solver.md) | Board | No: it is the default |
| Run decider-0.8b in place of Qwen3.5 0.8B | [Install decider-0.8b](install-decider-0.8b.md) | Laptop (convert), then board | Yes, `config.env`. The [experiment](../experiments/2026-11-decider-0.8b.md) did not adopt it. |

## The tutor

| I want to… | Guide | Runs on | Changes the shipped build? |
| --- | --- | --- | --- |
| Label a student message with the decider-2b router | [Use decider-2b as router](use-decider-2b-router.md) | Laptop, then board, on its own port | No: the student app uses a keyword rule today |

## Data and research

| I want to… | Guide | Runs on | Changes the shipped build? |
| --- | --- | --- | --- |
| Read the five answer options with the label-anchored reader | [Read the answer options](../OPTION_READER_GUIDE.md) | Laptop | No: `prepare_m3kang.py` does not use it yet |
| Read or search the vault papers as text | [Extract papers with MinerU](mineru-ocr-papers.md) | Laptop | No |
| Load and score the organizers' practice set | [Practice set and hidden test](../PRACTICE_SET.md#how-to-load-and-score-it) | Laptop, then board | No |
