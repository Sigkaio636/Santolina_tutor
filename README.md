# Santolina_tutor
This repository holds the solution to the Qualcomm challenge (Datathon FME
2026): a math copilot that runs on the Arduino UNO Q.

This page explains the layout of the repository and the rules that apply to it.
It is for developers who work on the project. The copilot uses the
[M3Kang](GLOSSARY.md) dataset of Kangaroo math problems. To prepare a board,
go to [What to try](#what-to-try) at the end.

## Project organization

```
├── LICENSE            <- Apache 2.0 license
├── Makefile           <- Convenience commands (`make help` lists them: requirements, lint,
│                         format, docs-serve, docs-build, ...)
├── README.md          <- The top-level README for developers who use this project.
├── mkdocs.yml         <- Docs site built from docs/ (see "Documentation site" below)
├── data               <- Only README.md and sample_problems.jsonl are in Git. The other
│                         files stay local (M3Kang stays out of Git).
│                         data/README.md lists them.
├── docs               <- Project documentation. docs/vault/ is the Obsidian paper vault
├── pyproject.toml     <- Project configuration file with package metadata for
│                         santolina_tutor and configuration for tools like ruff
├── models, notebooks, references, reports
│                      <- Empty cookiecutter folders (only .gitkeep files)
│
└── santolina_tutor    <- Source code for use in this project (laptop side).
    ├── __init__.py    <- Makes santolina_tutor a Python module
    ├── config.py      <- Store useful variables and configuration
    ├── dataset.py     <- Extracts the M3Kang parquet shards in data/raw/
    │                     into data/interim/m3kang/
    └── templates      <- Cookiecutter scaffolding that nothing uses yet: features.py,
                          plots.py, modeling/predict.py, modeling/train.py
```

## Pull requests

When Claude Code opens a pull request in this repo, a hook checks two rules.
The hook is `.claude/hooks/pr-gate.sh`, wired in `.claude/settings.json`. It
runs before `gh pr create`, `gh pr new` or `gh pr ready`:

1. **Draft.** `gh pr create` carries `--draft`, unless `--web` hands the PR
   to the browser.
2. **Documentation red flag.** If the change touches code but no `*.md`,
   `docs/`, README or CHANGELOG file, the hook blocks the command.
   Tests, lockfiles and `.github/` do not count as code. When the change
   affects no document, end the command with the shell comment
   `# pr-gate: no-docs <reason>` and give the reason in the PR body.

The `pre-pr` skill in `.claude/skills/pre-pr/` prepares the PR: a
`/simplify` pass you review, the affected documentation, and a draft PR
with What and Why. `/simplify` is a skill that comes with Claude Code. It
reviews the changed code for simplifications.

The hook only checks commands the agent runs. The hook does not check a PR
opened from the GitHub website, from an app button or by hand. When the hook
cannot read the command or find the Git repository, it allows the command.
When `origin` has no default branch, or `--repo` names another repo, the
hook skips only the documentation check. The draft check still applies.

## Where the code runs

The board side comes from the organizers' repository
[mpous/datathon-UPC-maths-qualcomm-arduino-unoq](https://github.com/mpous/datathon-UPC-maths-qualcomm-arduino-unoq),
copied at commit [`d6e3f1b`](https://github.com/mpous/datathon-UPC-maths-qualcomm-arduino-unoq/tree/d6e3f1b0c28a7dc47db3143c17e1e609006cd0a4).
Its files keep their upstream paths at the root of this repository, with two
exceptions. The upstream README is now `docs/BOARD_SETUP.md`. The upstream
`.skills/` folder is now `.claude/skills/`.

| Path | Runs on | What it is |
| --- | --- | --- |
| [`docs/BOARD_SETUP.md`](docs/BOARD_SETUP.md) | (a guide, not code) | The step-by-step guide: from a new board to the baseline, then retrieval (RAG), the problem explorer (`explorer/`) and the project |
| `board/` | Board | Setup scripts `00` to `05` (check, packages, llama.cpp, models, services, smoke test) and the systemd units |
| `config.env` | Both | Pinned llama.cpp commit, models (with SHA256), ports, time limit, seed |
| `copilot/` | Board | The copilot: retrieval, prompt, and the call to the model services. Python standard library only |
| `predict.py` | Board | **The organizers' contract.** `python3 predict.py --input X.jsonl --output Y.csv`: one letter A to E per problem, at most 60 s each |
| `eval.py`, `build_index.py` | Board | Measure accuracy and latency (writes `results/`), and build the RAG index |
| `explorer/` | Board | A web page to try problems one by one (port 8000) |
| `laptop/` | Laptop | `prepare_m3kang.py`: download M3Kang and read the options with OCR (optical character recognition: reading text from the problem images). New option reader, not in `prepare_m3kang.py` yet: [docs/OPTION_READER_GUIDE.md](docs/OPTION_READER_GUIDE.md) |
| `data/sample_problems.jsonl` | Both | The only data file in Git |

Rules that separate the two halves:

- **Two `predict.py` files.** Only the root one is the organizers' contract.
  Don't merge them (the rule is in [CLAUDE.md](CLAUDE.md)).
- **Nothing on the board imports `santolina_tutor`.** The `santolina_tutor`
  package needs `loguru` and `python-dotenv`, and the board has no `pip`.
  `copilot/`, `predict.py`, `eval.py`, `build_index.py` and `explorer/` use
  the standard library only.
- **Ruff only checks `santolina_tutor/`**, so `make format` never rewrites the
  upstream code.
- **M3Kang is for research use only.** `.gitignore` keeps everything in
  `data/` out of Git, except `sample_problems.jsonl` and `README.md`. It also
  excludes `*.gguf`, `*.db` and `results/`. The guard below enforces the red line.

## Red line: no M3Kang data in Git

No one may stage, commit, push or open a PR with an M3Kang problem, or
anything derived from one. A file already in a commit needs a history rewrite, not a new
commit that deletes it. [`CLAUDE.md`](CLAUDE.md) states the full rule and the
paths it covers.

One script, `.claude/hooks/m3kang-guard.py`, holds the rules and enforces them
in two places:

| Where | When | What it does |
| --- | --- | --- |
| Claude Code hook (`.claude/settings.json`, PreToolUse on Bash) | Before the agent runs `git add`, `git commit`, `git push` or `gh pr create\|ready\|merge` | Lists every file the command would put in Git: staged files, forced adds, `-A`/`-a`, unpushed commits on any branch. Blocks the call if one is M3Kang data |
| GitHub Actions (`.github/workflows/m3kang-guard.yml`) | Every PR, and every push to `main` | Checks every commit in the range and the final tree. So it also catches a commit made by hand or a PR opened on the website |

The script checks file paths, not file contents. It catches problem images
only under `data/`. An image saved anywhere else passes the check.

`main` has no branch protection (checked on 2026-11-14). So the CI check
warns, but it does not block a merge. It blocks merges only after
**m3kang-guard** becomes a required status check in a branch protection rule
for `main` (GitHub repository settings).

## Skills for Claude

`.claude/skills/` holds the project's skills. Claude Code loads a skill when
the request fits. You can also request one by name. Four of them come from the
organizers' repository. They teach Claude how the board, this code and the
datathon work.

| Skill | Use it to |
| --- | --- |
| [`unoq-board`](.claude/skills/unoq-board/SKILL.md) | Connect over SSH or adb, check the model services and the RAM, fix common problems |
| [`m3kang-copilot`](.claude/skills/m3kang-copilot/SKILL.md) | Change the copilot, run measured experiments, analyze the errors |
| [`unoq-hardware-ui`](.claude/skills/unoq-hardware-ui/SKILL.md) | Build an App Lab app with a web page and the LED matrix |
| [`publish-project`](.claude/skills/publish-project/SKILL.md) | Prepare the public repository and the Arduino Project Hub write-up |

Each of these four has a `PROVENANCE.md` with the upstream commit and the local
edits. If the ports, models or rules change, change the skills too.

The other skills are general tools:

| Skill | Use it to |
| --- | --- |
| [`doc-authoring`](.claude/skills/doc-authoring/SKILL.md) | Write a new document, or audit and fix existing ones, from start to end |
| [`diataxis`](.claude/skills/diataxis/SKILL.md) | Choose the document type (tutorial, how-to, reference, explanation) and structure a document |
| [`docsauditor`](.claude/skills/docsauditor/SKILL.md) | Find where the docs no longer match the code, without changing anything |
| [`docsjanitor`](.claude/skills/docsjanitor/SKILL.md) | Fix existing docs so they match the code |
| [`docs-site`](.claude/skills/docs-site/SKILL.md) | Serve, build or add a page to the MkDocs site |
| [`docs-review`](.claude/skills/docs-review/SKILL.md) | Review one document in seven stages, with your sign-off |
| [`mermaid-artist`](.claude/skills/mermaid-artist/SKILL.md) | Draw Mermaid diagrams for the docs |
| [`asd-ste100`](.claude/skills/asd-ste100/SKILL.md) | Rewrite text in Simplified Technical English, so it is hard to misread |
| [`grilling`](.claude/skills/grilling/SKILL.md) | Stress-test a plan or decision with hard questions |
| [`grill-with-docs`](.claude/skills/grill-with-docs/SKILL.md) | Stress-test a plan, and write ADRs and glossary entries as you go |
| [`domain-modeling`](.claude/skills/domain-modeling/SKILL.md) (Matt Pocock, MIT) | Keep `GLOSSARY.md` and the ADRs up to date |
| [`structured-planning`](.claude/skills/structured-planning/SKILL.md) | Write a plan with steps, checks, risks and open questions |
| [`pre-pr`](.claude/skills/pre-pr/SKILL.md) | Prepare a change for a pull request |
| [`ponytail`](.claude/skills/ponytail/SKILL.md) and the `ponytail-*` skills | Make the smallest change that solves a task. The others audit, review, list shortcuts, show savings or give help |
| [`academic-paper-summarizer`](.claude/skills/academic-paper-summarizer/SKILL.md) | Summarize a research paper |
| [`socratic-tutor`](.claude/skills/socratic-tutor/SKILL.md) | Be taught or quizzed on a topic |
| [`vis-design`](.claude/skills/vis-design/SKILL.md) | Design a chart or other visualization |
| [`vis-value-critique`](.claude/skills/vis-value-critique/SKILL.md) | Critique an existing chart |

Skills copied from other projects keep their upstream license file in their
folder: `asd-ste100`, `domain-modeling`, `grilling`, `grill-with-docs`, the
`ponytail` skills and `socratic-tutor`. The four skills from the organizers'
repository have no license file. Their `PROVENANCE.md` says the upstream
repository declares none.

## Documentation site

`mkdocs.yml` configures a browsable site (MkDocs + Material) built from
`docs/`. The site serves on port 8001, because the board explorer uses port
8000.

The site menu is the `nav:` list in `mkdocs.yml`. The `docs-site` skill explains
how to add a page and check the build. No new page may contain M3Kang problem
text. The only exception is the organizers' example record in
`docs/BOARD_SETUP.md`, which is a verbatim copy.

A document counts as `validated` only after a review. To review a document,
run `/docs-review` in Claude Code. It reviews one document per run in seven
stages (`audit`, `critique`, `decisions`, `repair`, `language`, `adversarial`,
`signoff`). It requests your sign-off at each stage. `docs/review/status.yml` records the
result, and the site's "Review status" page shows it. `make docs-status`
checks that file.

## Credits

- Board setup, copilot, scripts and skills: the UPC Datathon FME 2026
  Qualcomm challenge organizers, [mpous/datathon-UPC-maths-qualcomm-arduino-unoq](https://github.com/mpous/datathon-UPC-maths-qualcomm-arduino-unoq).
- **M3Kang**: Torres-Camps et al., 2026, [arXiv:2601.16218](https://arxiv.org/abs/2601.16218).
  [Dataset card and license](https://huggingface.co/datasets/qualcomm/M3Kang): research use only.
- [llama.cpp](https://github.com/ggml-org/llama.cpp) (MIT), Qwen3.5 0.8B and
  bge-small-en-v1.5 (see their model cards:
  [Qwen3.5 0.8B](https://huggingface.co/bartowski/Qwen_Qwen3.5-0.8B-GGUF),
  [bge-small-en-v1.5](https://huggingface.co/CompendiumLabs/bge-small-en-v1.5-gguf)),
  [RapidOCR](https://github.com/RapidAI/RapidOCR) (Apache 2.0).

## What to try

**Prepare a board and run the copilot.**

1. Follow steps 0 to 8 of [`docs/BOARD_SETUP.md`](docs/BOARD_SETUP.md) on the
   board, then step 9 on your laptop. The board then runs the two model
   services, and your laptop has `data/train.jsonl` and `data/val.jsonl`.
2. Follow [How to deploy the copilot on the UNO Q](docs/how-to/deploy-copilot-on-board.md).
   At the end, the smoke test passes.
3. Follow [How to use the copilot on the UNO Q](docs/how-to/use-copilot-on-board.md)
   to answer problems and measure the results.

**Check a range of commits for M3Kang data.** From the repository root:

```bash
python3 .claude/hooks/m3kang-guard.py --range origin/main HEAD
```

A clean range prints `m3kang-guard: clean (N paths checked)`. On a hit, the
script lists each file with the reason and exits with code 1.

**Serve the documentation site.** On the laptop, with
[uv](https://docs.astral.sh/uv/) (the Python package manager of this project):

```bash
uv sync --group docs
make docs-serve   # http://127.0.0.1:8001 (8000 is the board explorer)
```
