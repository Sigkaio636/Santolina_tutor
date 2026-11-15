# Santolina tutor

Santolina tutor is a math copilot that runs entirely on the Arduino UNO Q 4 GB,
for the Qualcomm challenge of [Datathon FME 2026](BOARD_SETUP.md#the-challenge). It works with the
[M3Kang dataset](https://huggingface.co/datasets/qualcomm/M3Kang). The dataset
is for research use only. Except for one example record in the organizers'
setup guide, this site has no M3Kang problem text.

This site is the project's documentation, for the team and for anyone who
wants to run the copilot on a board. Read the pages under "Start here" in order.

## The project

Each student gets a board. The board makes its own Wi-Fi, and the student
opens the tutor on a phone. A fine-tuned Qwen3.5 0.8B guides the student
through Kangaroo problems with short questions, and code blocks any reply that
gives the answer away. A teacher app on a laptop loads homework onto the boards
and unloads what each student did, over USB. For the organizers' hidden test,
`predict.py` answers one letter per problem: by default with a fixed rule on
the option values (`SOLVER=prior`), or with one letter from Qwen3.5 0.8B
(`SOLVER=letter`).

The [README](https://github.com/Sigkaio636/Santolina_tutor#readme) is the
project's submission page. It holds these sections:

- [What it does](https://github.com/Sigkaio636/Santolina_tutor#what-it-does)
- [Architecture](https://github.com/Sigkaio636/Santolina_tutor#architecture),
  with how we use M3Kang
- [How to replicate it](https://github.com/Sigkaio636/Santolina_tutor#how-to-replicate-it)
- [Results](https://github.com/Sigkaio636/Santolina_tutor#results) and
  [error analysis](https://github.com/Sigkaio636/Santolina_tutor#error-analysis)
  by language and level
- [What didn't work](https://github.com/Sigkaio636/Santolina_tutor#what-didnt-work-and-what-we-would-try-next)
- [The team](https://github.com/Sigkaio636/Santolina_tutor#the-team)

## Start here

1. [Board setup](BOARD_SETUP.md), steps 0 to 12: the organizers' guide to
   prepare the board, the M3Kang files on your laptop (step 9) and the
   retrieval index (step 12). It also defines the `predict.py` contract.
2. [How to deploy the copilot on the UNO Q](how-to/deploy-copilot-on-board.md):
   put the code and data on the board and check it.
3. [Use the student app](how-to/use-student-app.md): install the student app,
   the LED app and the tutor model on the board, and use them from a phone.
4. [Run the teacher app](how-to/run-teacher-app.md): set up boards, load
   homework and unload what students did.
5. [How to use the copilot on the UNO Q](how-to/use-copilot-on-board.md):
   answer problems with `predict.py`, measure results, and use retrieval.

Developers: see [Develop the project](DEVELOPING.md) for the repository layout
and its rules.

## Background

- [UNO Q board reference](UNO_Q_BOARD_REFERENCE.md): the board's hardware and
  limits. This is the canonical page for the board specs.
- [What the challenge asks](GOAL_MUSTS.md): the only checklist of what the team
  must deliver.
- [Challenge context](CHALLENGE_CONTEXT.md): the team's planning notes and research
  for the challenge.
- [Summary of the setup video](RESUMEN_QUALCOMM_UNO_Q.md): a summary of the
  organizers' setup video. The
  [video transcript](https://github.com/Sigkaio636/Santolina_tutor/blob/main/docs/UPC%20Datathon%20-%20Qualcomm%20Challenge%20step%20by%20step%20Arduino%20UNO%20Q%20setup.txt)
  is on GitHub only, not on this site.
- [UNO Q constraints guide](GUIA_RESTRICCIONES_UNOQ.html): an HTML page with the
  challenge constraints and a summary of the board specs. The board reference
  above is the full copy.

## Paper vault

The paper vault is the folder `docs/vault/`: research papers and our notes on
them. You can also open it in [Obsidian](https://obsidian.md), a Markdown
note-taking app.

- [Papers](vault/papers/README.md): the reading list. Its topics are benchmarks,
  surveys and model reports, on-device inference, quantization, pruning, fine-tuning and
  distillation, math tutoring and pedagogy, and Jev decision models.
- [Extract papers to Markdown with MinerU](how-to/mineru-ocr-papers.md):
  MinerU converts PDFs to Markdown. This guide converts the vault papers, so
  you can read and search them.
