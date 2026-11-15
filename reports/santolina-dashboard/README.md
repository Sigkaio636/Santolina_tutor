# Santolina dashboard

This folder holds one page that fuses the team's three dashboards. It has three parts:

1. **Data.** M3Kang shard 0 and the organizers' practice set: coverage by level and year, languages, answer-key letters, figure need, statement length, option reading, and how the grid problems differ from the practice set.
2. **Progress.** Accuracy of every recorded run over the 21 hours, and the outcome funnel of the 22 laptop grid runs. The funnel is linked to board time (with speed sliders) and to accuracy per slice. A last view shows the paired effect of one change at a time (fine-tuning, Catalan translation).
3. **Results.** The solver block from the Tukey dashboard: accuracy, predicted score of 20, English vs Catalan, and seconds. Then answer paths, levels, RAM, the message router, commits, and the decisions table.

The three source dashboards stay where they are:

- `reports/tukey-dashboard/`: results, and the statistics this page imports.
- `reports/solver-dashboard/`: the funnel, which this page rebuilds from the frames embedded in its HTML.
- `reports/m3kang-dashboard/`: the EDA, which this page redoes from aggregates only.

Published copy (private, owner only): <https://claude.ai/artifact/2aGz9HNXDeYBkwxekEHiiL>.

## Rebuild

From the repository root:

```bash
# 1. Aggregates (only when the inputs change). Needs the local M3Kang shard and data/demo/train.jsonl.
uv run --no-project --with pandas --with pyarrow python reports/santolina-dashboard/build_data.py \
    --parquet <path>/high_quality-00000-of-00004.parquet
# 2. The page
cd reports/santolina-dashboard
uv run --no-project --with altair==5.5.0 --with vl-convert-python==1.7.0 --with pandas python santolina_dashboard.py
```

Step 2 needs only `data/*.csv` here and `../tukey-dashboard/data/*.csv`, which are both in Git.

## Colours

Each colour means one thing on the whole page. `page_template.html` shows the key in the header.

| Colour | Meaning |
|---|---|
| Blue `#0072b2` | Measured on the UNO Q board |
| Orange `#e69f00` | Laptop measurement or estimate |
| Grey | Chance or reference (fixed letter, zero line) |
| Reddish purple `#cc79a7`, square | M3Kang |
| Ink, circle | Practice set |
| Bluish green `#009e73` | Right answer (outcome funnel and board-time scatter) |
| Greys, light to dark | Ways a program is lost (cap, crash, no match, wrong) |
| Vermillion `#d55e00` | Hard limit (57/60 s, free RAM) |
| Purples (sequential) | Counts of M3Kang problems; greys for commits |

## Files

| File | What it is |
|---|---|
| `build_data.py` | Writes `data/*.csv`: aggregates from the shard and practice set, plus the solver frames pulled from `solver_dashboard.html` |
| `santolina_dashboard.py` | Builds the 16 views and the page. Part 3 calls functions of `../tukey-dashboard/tukey_dashboard.py` |
| `page_template.html` | Layout, colour tokens (light and dark), header, decisions table, notes |
| `santolina_dashboard.html` | The built page. It is generated, so do not edit it by hand |
| `specs/*.vl.json` | One Vega-Lite spec per view, for the critique inspector |
| `santolina_dashboard_design.md` | Design and critique record |

## Data rules

`data/*.csv` holds only counts, shares, token counts, levels, years, letters, problem ids and outcomes. It holds no statement, option, program or image. `eda_tokens.csv` has one length per problem and no id. This keeps the folder inside the M3Kang red line of the root `CLAUDE.md`. Ferran's problem browser (`reports/m3kang-dashboard`) stays local-only for that reason.
