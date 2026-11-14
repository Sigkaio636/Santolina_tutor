# Santolina tutor

A math copilot that runs entirely on the Arduino UNO Q 4 GB, for the Qualcomm
challenge of [Datathon FME 2026](BOARD_SETUP.md#the-challenge). It works with the
[M3Kang dataset](https://huggingface.co/datasets/qualcomm/M3Kang). The dataset
is for research use only. Except for one example record in the organizers'
setup guide, this site has no M3Kang problem text.

This site is the project's documentation, for the team and for anyone who
wants to run the copilot on a board. Read the pages under "Start here" in order.

## Start here

1. [Board setup](BOARD_SETUP.md), steps 0 to 8: the organizers' guide to set up
   the board. It also defines the `predict.py` contract.
2. [How to deploy the copilot on the UNO Q](how-to/deploy-copilot-on-board.md):
   put the code and data on the board and check it.
3. [How to use the copilot on the UNO Q](how-to/use-copilot-on-board.md):
   answer problems, measure results, and use retrieval.

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

- [Papers](vault/papers/README.md): the reading list on benchmarks, surveys and
  model reports, on-device inference, quantization, pruning, fine-tuning and
  distillation, math tutoring and pedagogy, and Jev decision models.
- [Extract papers to Markdown with MinerU](how-to/mineru-ocr-papers.md):
  MinerU converts PDFs to Markdown. This guide converts the vault papers, so
  you can read and search them.
