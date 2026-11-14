# Santolina_turor
Repo amd la solució del Qualcomm repte 

## Project Organization

```
├── LICENSE            <- Apache 2.0 license
├── Makefile           <- Makefile with convenience commands like `make data` or `make train`
├── README.md          <- The top-level README for developers using this project.
├── data
│   ├── external       <- Data from third party sources.
│   ├── interim        <- Intermediate data that has been transformed.
│   ├── processed      <- The final, canonical data sets for modeling.
│   └── raw            <- The original, immutable data dump.
│
├── docs               <- Project documentation
│
├── models             <- Trained and serialized models, model predictions, or model summaries
│
├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
│                         the creator's initials, and a short `-` delimited description, e.g.
│                         `1.0-jqp-initial-data-exploration`.
│
├── pyproject.toml     <- Project configuration file with package metadata for 
│                         santolina_tutor and configuration for tools like ruff
│
├── references         <- Data dictionaries, manuals, and all other explanatory materials.
│
├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures        <- Generated graphics and figures to be used in reporting
│
└── santolina_tutor   <- Source code for use in this project.
    │
    ├── __init__.py             <- Makes santolina_tutor a Python module
    │
    ├── config.py               <- Store useful variables and configuration
    │
    ├── dataset.py              <- Scripts to download or generate data
    │
    ├── features.py             <- Code to create features for modeling
    │
    ├── modeling                
    │   ├── __init__.py 
    │   ├── predict.py          <- Code to run model inference with trained models          
    │   └── train.py            <- Code to train models
    │
    └── plots.py                <- Code to create visualizations
```

--------

## Pull requests

When Claude Code opens a pull request in this repo, a hook in
`.claude/hooks/pr-gate.sh` (wired in `.claude/settings.json`) checks two
rules before `gh pr create`, `gh pr new` or `gh pr ready` runs:

1. **Draft.** `gh pr create` carries `--draft`, unless `--web` hands the PR
   to the browser.
2. **Documentation red flag.** If the change touches code but no `*.md`,
   `docs/`, README or CHANGELOG file, the PR waits for documentation.
   Tests, lockfiles and `.github/` do not count as code. When no document
   is affected, end the command with the shell comment
   `# pr-gate: no-docs <reason>` and give the reason in the PR body.

The `pre-pr` skill in `.claude/skills/pre-pr/` prepares the PR: a
`/simplify` pass you review, the affected documentation, and a draft PR
with What and Why.

The hook only checks commands the agent runs. A PR opened from the GitHub
website, from an app button or by hand is not checked. When the hook
cannot decide (no `origin` default branch, unreadable input, `--repo`
aimed at another repo) it lets the command through.


--------

## Arduino UNO Q

The board side comes from the organizers' repository
[mpous/datathon-UPC-maths-qualcomm-arduino-unoq](https://github.com/mpous/datathon-UPC-maths-qualcomm-arduino-unoq),
copied at commit `d6e3f1b`. Its files keep their upstream paths at the root of
this repository, so its commands and its skills work unchanged.

| Path | Runs on | What it is |
| --- | --- | --- |
| [`docs/BOARD_SETUP.md`](docs/BOARD_SETUP.md) | | The step-by-step guide: from a new board to the baseline, then RAG, the explorer and the project |
| `board/` | Board | Setup scripts `00` to `05` (check, packages, llama.cpp, models, services, smoke test) and the systemd units |
| `config.env` | Both | Pinned llama.cpp commit, models (with SHA256), ports, time limit, seed |
| `copilot/` | Board | The copilot: retrieval, prompt, and the call to the model servers. Python standard library only |
| `predict.py` | Board | **The organizers' contract.** `python3 predict.py --input X.jsonl --output Y.csv`: one letter A to E per problem, at most 60 s each |
| `eval.py`, `build_index.py` | Board | Measure accuracy and latency (writes `results/`), and build the RAG index |
| `explorer/` | Board | A web page to try problems one by one (port 8000) |
| `laptop/` | Laptop | `prepare_m3kang.py`: download M3Kang and read the options with OCR |
| `data/sample_problems.jsonl` | Both | The only data file in Git |

Clone this repository on the board as `~/Santolina_tutor`, then follow
[`docs/BOARD_SETUP.md`](docs/BOARD_SETUP.md).

Rules that keep the two halves apart:

- **Two `predict.py` files.** The root `predict.py` is the one the organizers
  run. `santolina_tutor/modeling/predict.py` is cookiecutter scaffolding for
  laptop work. Don't merge them.
- **Nothing on the board imports `santolina_tutor`.** It needs `loguru` and
  `python-dotenv`, and the board has no `pip`. `copilot/`, `predict.py`,
  `eval.py`, `build_index.py` and `explorer/` use the standard library only.
- **Ruff only checks `santolina_tutor/`**, so `make format` never rewrites the
  upstream code.
- **M3Kang is for research use only.** `.gitignore` keeps everything in
  `data/` out of Git except `sample_problems.jsonl` and `README.md`, plus
  `*.gguf`, `*.db` and `results/`. The guard below enforces it.

### Red line: no M3Kang data in Git

M3Kang problems, and anything derived from them, must never be staged,
committed, pushed or sent in a PR, nor appear in any commit of the history.
That covers `data/` (except `sample_problems.jsonl` and `README.md`),
`*.jsonl`, `*.parquet`, `*.db`/`*.sqlite`, the OCR cache and train/val/test
splits. One script, `.claude/hooks/m3kang-guard.py`, holds the rules and
enforces them in two places:

| Where | When | What it does |
| --- | --- | --- |
| Claude Code hook (`.claude/settings.json`, PreToolUse on Bash) | Before the agent runs `git add`, `git commit`, `git push` or `gh pr create\|ready\|merge` | Lists every file the command would put in Git (staged files, forced adds, `-A`/`-a`, unpushed commits on any branch) and blocks the call if one is M3Kang data |
| GitHub Actions (`.github/workflows/m3kang-guard.yml`) | Every PR, and every push to `main` | Checks every commit in the range and the final tree, so a commit made by hand or a PR opened on the website is checked too |

The CI check only stops a merge once **m3kang-guard** is a required status
check in the branch protection rule for `main` (GitHub repository settings).
[`CLAUDE.md`](CLAUDE.md) states the rule for the agent. To check a range by
hand:

```bash
python3 .claude/hooks/m3kang-guard.py --range origin/main HEAD
```

If a file is already in a commit, removing it in a new commit isn't enough:
the history must be rewritten before anything is pushed.

### Skills for Claude

Four skills in `.claude/skills/` teach Claude how the board, this code and the
datathon work. Claude Code loads them when the request fits, or ask for one by
name.

| Skill | Use it to |
| --- | --- |
| [`unoq-board`](.claude/skills/unoq-board/SKILL.md) | Connect over SSH or adb, check the model services and the RAM, fix common problems |
| [`m3kang-copilot`](.claude/skills/m3kang-copilot/SKILL.md) | Change the copilot, run measured experiments, analyse the errors |
| [`unoq-hardware-ui`](.claude/skills/unoq-hardware-ui/SKILL.md) | Build an App Lab app with a web page and the LED matrix |
| [`publish-project`](.claude/skills/publish-project/SKILL.md) | Prepare the public repository and the Arduino Project Hub write-up |

Each skill has a `PROVENANCE.md` with the upstream commit and the local edits.
If the ports, models or rules change, change the skills too.

### Credits

- Board setup, copilot, scripts and skills: the UPC Datathon FME 2026
  Qualcomm challenge organizers, [mpous/datathon-UPC-maths-qualcomm-arduino-unoq](https://github.com/mpous/datathon-UPC-maths-qualcomm-arduino-unoq).
- **M3Kang**: Torres-Camps et al., 2026, [arXiv:2601.16218](https://arxiv.org/abs/2601.16218).
  [Dataset card and license](https://huggingface.co/datasets/qualcomm/M3Kang): research use only.
- [llama.cpp](https://github.com/ggml-org/llama.cpp) (MIT), Qwen3.5 0.8B and
  bge-small-en-v1.5 (see their model cards), RapidOCR (Apache 2.0).
