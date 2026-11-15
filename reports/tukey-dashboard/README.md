# Tukey side-challenge dashboard

This folder holds the team's dashboard for the Tukey side challenge of Datathon FME 2026. The challenge asks for a dashboard that helps decide on the main challenge. Here the decision is which solver the root `predict.py` ships for the final test: 20 problems, English or Catalan, 60 s each, on the Arduino UNO Q.

The dashboard is one HTML page. A Python script builds it from small CSV files, with Altair (Vega-Lite) charts.

Published copy (private, owner only): <https://claude.ai/artifact/2aGz9HNXDeYBkwxekEHiiL>. Share it from the page's Share menu.

## What the page shows

| View (`specs/<id>.vl.json`) | Question it answers | Data file |
|---|---|---|
| `core`: four linked columns, one row per solver | Which solver beats chance, its predicted score out of 20, English vs Catalan, seconds against the 60 s limit. Click a row to highlight it in all four columns | `data/solvers.csv` |
| `progress` | Accuracy of every recorded run over the 21 hours, with the best board result so far | `data/progress.csv` |
| `paths` | How the program solver produced each answer, and how many were right | `data/paths.csv` |
| `levels` | Program solver accuracy by Kangaroo level | `data/levels.csv` |
| `ram` | Memory of the model servers against the free RAM | `data/ram.csv` |
| `ocr` | Share of rows with all five options read, after each OCR change | `data/ocr.csv` |
| `router` | Accuracy of the tutor's message router | `data/router.csv` |
| `activity` | Commits per hour by area | `data/commits.csv` |

A numbers row opens the page, and a decisions table closes it. Both live in `page_template.html`.

## Rebuild the page

Altair is not a project dependency, so run the script with `uv`:

```bash
cd reports/tukey-dashboard
uv run --no-project --with altair==5.5.0 --with vl-convert-python==1.7.0 --with pandas python tukey_dashboard.py
```

It writes `tukey_dashboard.html` and `specs/*.vl.json`, and `specs/*.png` previews that Git ignores. The PNGs have no text, because the headless renderer lacks the web fonts. Check the HTML in a browser instead. For a headless screenshot:

```bash
firefox --headless --no-remote --profile /tmp/ff-tukey --window-size=1280,3900 \
  --screenshot /tmp/tukey.png "file://$PWD/tukey_dashboard.html"
```

## Add or change a result

1. Find the number in a team report (`docs/experiments/`, `docs/how-to/`, `docs/UNO_Q_BOARD_REFERENCE.md`, also on the `exp/*` branches).
2. Add a row to the matching CSV, with the report in its `source` column where the file has one.
3. Rebuild. The header numbers and the decisions table fill from the data (`{{…}}` placeholders in `page_template.html`, set by `kpis()`). The script fails if a placeholder stays unfilled.
4. Look at the page. Then republish it (see `CLAUDE.md`).

`data/commits.csv` comes from `git log --all --no-merges --numstat`. `CLAUDE.md` gives the area rule.

## How the numbers are computed

- The practice set asks 50 problems in English and Catalan: 100 rows. The two answers to one problem are not independent. So intervals count problems, not rows: right_eff = accuracy × 50, n = 50 (column `problems`).
- Wilson intervals at 50, 80 and 95%, drawn as solid tints.
- Predicted score for 20 new problems: Beta(1 + right_eff, 1 + n − right_eff), then binomial. The grey chance row is the exact binomial(20, 0.2).
- Colour means the same in every view: blue = measured on the board, orange = laptop estimate, grey = chance reference. Shape repeats it: circle, diamond, square.

## Files

| File | What it is |
|---|---|
| `tukey_dashboard.py` | Builds every view and the page: `load`, `derive`, `core_views`, one function per panel, `kpis`, `save` |
| `page_template.html` | Page layout, CSS tokens (light and dark), header, decisions table, method notes, and the vega-embed loader |
| `tukey_dashboard.html` | The built page. It is generated, so do not edit it by hand |
| `data/*.csv` | Inputs: aggregates only |
| `specs/*.vl.json` | Vega-Lite spec of each view, for the critique inspector |
| `tukey_dashboard_design.md` | Design document (vis-design skill): reader, question, abstraction, encoding, rejected options |
| `tukey_dashboard_critique.md` | Two critique passes (vis-value-critique skill) and the fixes that came from them |
| `answers.json`, `record.json` | Inputs of the vis-design decision record. The record itself is `.claude/vis-decisions/p-uncertainty-of-estimate-or-forecast--which-solver-to-ship-for-the-20261115-2.yaml` |

## Data rules

Every file here holds aggregates: counts, accuracies, seconds and megabytes. It holds no problem text, no option, no image and no problem ID. That keeps the folder inside the M3Kang red line in the root `CLAUDE.md`. The organizers sent the practice set to the teams only, so the same rule applies to it.
