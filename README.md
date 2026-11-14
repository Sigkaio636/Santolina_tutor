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

