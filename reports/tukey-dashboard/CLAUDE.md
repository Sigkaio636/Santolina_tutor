# Working on the Tukey dashboard

Read `README.md` in this folder first. The root `CLAUDE.md` still applies, above all the M3Kang red line.

## Rules for this dashboard

- **Edit the sources, never `tukey_dashboard.html`.** Change `data/*.csv`, `tukey_dashboard.py` or `page_template.html`, then rebuild with the command in `README.md`.
- **Keep text to a minimum.** Pau (the owner) rejected an earlier version as "too much text, looks AI-like". So:
  - Chart titles describe; they do not conclude. Write "Accuracy", not "Only X beats chance".
  - A subtitle only defines marks ("tick: mean · bar: to slowest").
  - Allowed labels are neutral facts: run names, the chance row, the 60 s limit, counts like "24 of 43 right".
  - Add no reading notes under the charts and no adjectives.
  - Conclusions go only in the decisions table at the end, as decision, evidence number and when.
- **Every number in the decisions table must be visible in a chart**, or the table must say where it comes from ("laptop report, not plotted"). Fill numbers from the data through `kpis()` and `{{placeholders}}`; do not type them in.
- **Colour has one meaning on the whole page**: blue `#0072b2` = board, orange `#e69f00` = laptop, grey = chance. A new view must keep that meaning. Dark mode swaps hex values at embed time (`DARK_SWAP` in `page_template.html`). If you add a colour, add its dark pair there.
- **Count intervals by problem, not by row** (column `problems`). Never use Wilson on 100 practice rows as if they were independent.
- **Aggregates only.** No problem text, option, image or problem ID in any file here. The M3Kang guard hook checks paths only, so this rule is yours to keep.

## Checks before you publish

1. Rebuild. The script must print no error, and `grep -c "{{\|NaN" tukey_dashboard.html` must print 0.
2. Take one headless screenshot (command in `README.md`) and look for overlapping labels and cut-off axes. The core block must fit 1180 px.
3. For a change to a chart, use the project skills: `/vis-design` to change a design (the decision record is in `.claude/vis-decisions/`) and `/vis-value-critique` to check it. Add the outcome to `tukey_dashboard_design.md` or `tukey_dashboard_critique.md`.

## Publish

The page is the claude.ai artifact <https://claude.ai/artifact/2aGz9HNXDeYBkwxekEHiiL>. Publish `tukey_dashboard.html` to that URL with the Artifact tool. From a new session, pass the URL as `url`, and read the artifact first. A publish without the URL creates a separate artifact.

## Commit area rule (for `data/commits.csv`)

Each non-merge commit on any branch gets the area where most of its added lines went. Lock files do not count. The paths map to areas as follows:

| Path | Area |
|---|---|
| `.claude/`, `.github/` | Tooling & skills |
| `docs/vault/` | Research vault |
| `docs/experiments/`, `docs/models/`, `docs/review/findings` | Experiments |
| Other `docs/`, `*.md`, `mkdocs.yml` | Docs |
| `student_app/`, `teacher_app/`, `classroom/`, `mockups/` | Classroom apps |
| `tests/` | Tests |
| `copilot/`, `board/`, `predict.py`, `eval.py`, `build_index.py`, `explorer/`, `config.env` | Solver & board |
| `laptop/`, `santolina_tutor/` | Data & training tools |

Record times in Europe/Madrid. Keep only the columns `hash,time,area`: no author names.
