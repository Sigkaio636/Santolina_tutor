# Santolina tutor

Santolina is a math tutor that runs entirely on an Arduino UNO Q 4 GB, with no network. It is our entry to the Qualcomm challenge "Math on the Edge" of [Datathon FME 2026](BOARD_SETUP.md#the-challenge). The challenge asks for a copilot that does two jobs on the board:

- **Teach.** Each student gets a board. The board makes its own Wi-Fi, and the student opens the tutor on a phone. A fine-tuned Qwen3.5 0.8B guides the student through Kangaroo problems with short questions. Code blocks any reply that gives the answer away. A teacher app on a laptop loads homework onto the boards and unloads what each student did, over USB.
- **Reason.** For the organizers' hidden test, `predict.py` answers each problem with one letter, A to E, in under 60 seconds.

This site is the project's documentation, for the team and for anyone who wants to rebuild the copilot on a board. The [README](https://github.com/Sigkaio636/Santolina_tutor#readme) is the submission page.

!!! info "What `main` ships"
    `config.env` sets `SOLVER=prior`: a fixed rule on the option values, with no model call. It scored 16 of 100 on the organizers' practice set. `SOLVER=letter` scored 22. Our best pipeline, a Qwen2.5-Math program with Catalan translated first, scored 55 of 100 on the laptop, but it is on a branch. See [Experiments › Solving](experiments/solving/index.md).

## Start here

| I want to… | Go to |
| --- | --- |
| Rebuild the shipped build on a fresh board | [Tutorials](tutorials/index.md): five steps, each with a check at the end |
| Do one task: back up a board, try a model, read the options | [How-to guides](how-to/index.md) |
| Look up a fact about the board, the apps or the models | [Reference](reference/index.md) |
| See what we tried, what worked and what we decided | [Experiments](experiments/index.md), by topic |
| Check what the challenge asks and what is still open | [What the challenge asks](GOAL_MUSTS.md) |
| Change the code or the docs | [Develop the project](DEVELOPING.md) |

## Where each deliverable is

The challenge asks for a README with set sections ([checklist 1.3](GOAL_MUSTS.md#13-readme-in-this-order)). This site holds the detail behind each one:

| README section | Detail on this site |
| --- | --- |
| [What it does](https://github.com/Sigkaio636/Santolina_tutor#what-it-does) | [Use the student app](how-to/use-student-app.md), [Run the teacher app](how-to/run-teacher-app.md) |
| [Architecture](https://github.com/Sigkaio636/Santolina_tutor#architecture) | [UNO Q board reference](UNO_Q_BOARD_REFERENCE.md), [Board data contract](reference/board-data-contract.md), [Models](models/index.md) |
| [How to replicate it](https://github.com/Sigkaio636/Santolina_tutor#how-to-replicate-it) | [Tutorials](tutorials/index.md) |
| [Results](https://github.com/Sigkaio636/Santolina_tutor#results) and [error analysis](https://github.com/Sigkaio636/Santolina_tutor#error-analysis) | [Solving](experiments/solving/index.md), [Practice set and hidden test](PRACTICE_SET.md) |
| [What didn't work](https://github.com/Sigkaio636/Santolina_tutor#what-didnt-work-and-what-we-would-try-next) | [Experiments](experiments/index.md#what-didnt-work) |
| [The team](https://github.com/Sigkaio636/Santolina_tutor#the-team) | — |

## M3Kang

The copilot works with the [M3Kang dataset](https://huggingface.co/datasets/qualcomm/M3Kang) (Torres-Camps et al., 2026, [arXiv:2601.16218](https://arxiv.org/abs/2601.16218)). The dataset is for research use only. Except for one example record in the organizers' setup guide, this site holds no M3Kang problem text. The experiment reports give problem IDs and scores only.

## Research

The [paper vault](vault/papers/README.md) (`docs/vault/`) holds the research papers we read, with one synthesis note per topic. You can also open it in [Obsidian](https://obsidian.md), a Markdown note-taking app. To read the papers as text, see [Extract papers with MinerU](how-to/mineru-ocr-papers.md).
