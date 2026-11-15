# Solver dashboard

This dashboard shows where each solver setup loses problems, on the practice set and on held-out M3Kang rows. Each
problem ends at one of five steps: cut at the token cap, crashed, no option matched, wrong option, or right. It covers
22 grid runs of Noema-2B and Qwen-Math, base and fine-tuned, in English, Catalan, and Catalan translated to English.
Three linked views: a funnel heatmap per setup, board time against the 60 s limit with read and write speed
sliders, and accuracy by problem factor.

`solver_dashboard.html` is the built page, so you can open it without rebuilding anything. It holds problem IDs,
levels, token counts, seconds and outcomes. It has no problem text, options or programs.

## Rebuild it

The inputs are local files that stay out of Git:

| Input | Where it comes from |
|---|---|
| `data/grid/<run>.jsonl` | `santolina_tutor/grid.py` runs. The run names are in `RUNS` in `build_solver_data.py` |
| `data/demo/train.jsonl` | The practice set, see `docs/PRACTICE_SET.md` |
| `data/finetune/noema-programs/val.jsonl` | Held-out rows of the Noema programs fine-tune |
| `data/train.jsonl`, `data/val.jsonl` | `laptop/prepare_m3kang.py` (pass `--ocr-dir` if yours are elsewhere) |

```bash
python3 -I reports/solver-dashboard/build_solver_data.py   # writes data/solver_rows.csv here
cd reports/solver-dashboard
uv run --no-project --with altair==6.3.0 --with vl-convert-python==1.9.0 --with pandas python solver_dashboard.py
```

`python test_interaction.py` (needs Playwright) checks the selections and saves screenshots to `check/`.

## Files

| File | What it is |
|---|---|
| `build_solver_data.py` | Joins the grid runs into `data/solver_rows.csv`: one row per setup, problem and language |
| `solver_dashboard.py` | Builds the three linked views into `solver_dashboard.html` |
| `solver_dashboard.html` | The built page. It is generated, so do not edit it by hand |
| `test_interaction.py` | Browser test of the selections |
| `solver_dashboard_design.md` | Design document (vis-design skill) |
