# Design: Santolina solver results

| | |
|---|---|
| Decision record | `p-uncertainty-of-estimate-or-forecast--which-solver-to-ship-for-the-20261115-2` v2, supersedes v1 (`…-20261115`); v1 was adapted from seed `uncertainty-of-estimate-or-forecast--gradient-interval-expert` · status declared |
| Library / host | Altair 5.5.0 (Vega-Lite 5.20) run with `uv run --with altair==5.5.0 --with vl-convert-python==1.7.0`; one HTML page with vega-embed 6.26 |
| Data | `data/*.csv`: 8 solvers + 1 chance reference, 12 progress runs, 4 answer paths, 8 levels, 5 RAM configs, 5 OCR steps, 5 router runs, 132 commits. All aggregates copied from the repo's experiment reports; each row names its source |
| Outputs | `tukey_dashboard.py`, `page_template.html`, `tukey_dashboard.html`, `specs/*.vl.json`, `specs/*.png` (no text: the headless renderer lacks fonts; the HTML is the reference) |
| Language | dialogue en, code en |

## 1. Domain problem characterization

- Reader: Tukey side-challenge judges (statistics literate, a few minutes per dashboard) and the team (chooses what to ship before the 12:00 final test). Profile `scientist-reviewer`, modifier `cvd`.
- Mode: analysis, with an explanatory headline.
- Question: which solver should `predict.py` use for the 20-problem final test, given accuracy against chance, the 60 s limit, English vs Catalan and RAM? Second: how did 21 hours of work get there?
- Medium: one web page (claude.ai artifact), tooltips and one linked click; the default state answers the question.
- Rejected readings: "where the team spent its hours" first (kept as a supporting panel); "Teach vs Reason" (kept as the router panel).
- Validation: confirmed by the user in call 1 (2026-11-15).

## 2. Data and task abstraction

| attribute | type | role | range | notes |
|---|---|---|---|---|
| solver | nominal | key | 9 levels | label adds "· laptop" |
| measured_on | nominal | key 2 | board / laptop / reference | |
| right, n, problems | quantitative | measure | n = 100 rows = 50 problems | |
| eng_right, cat_right | quantitative | measure | of 50 | |
| mean_s, worst_s | quantitative | duration | 0–57.1 s | missing for laptop rows |

- Derived: accuracy = right / n; k_eff = accuracy × problems; Wilson 50/80/95% intervals on (k_eff, problems); posterior predictive of right answers in 20 problems, Beta(1 + k_eff, 1 + problems − k_eff) then binomial; chance row = exact binomial(20, 0.2).
- Tasks: compare, find extremum, determine range, retrieve value; overview + details on demand.
- Rejected abstraction: intervals on 100 independent rows (each problem appears twice; the critique pass moved to counting problems).
- Validation: confirmed by the user in call 2.

## 3. Visual encoding and interaction

- Idiom: gradient interval rows (`gradient_interval`), adapted from time to one row per solver.

| attribute | mark + channel | rank | expressiveness |
|---|---|---|---|
| accuracy | point, position x | 1 | quantitative on position |
| interval level | rect, luminance (solid tints) | ordinal on luminance | ordered on ordered channel |
| solver | position y, sorted by accuracy | nominal on position | ok |
| measured_on | hue + shape (circle/diamond/square) | nominal | ≤ 3 hues, second cue |

- Scales: accuracy 0–80%, final score 0–20, seconds 0–62: all from zero. Different measures keep separate x scales (SCL-08 exception); y order is shared.
- Color: blue `#0072b2` = board, orange `#e69f00` = laptop, grey = chance reference, on every view of the page. Dark mode swaps to lighter tints at embed time.
- Text (v2, after user feedback "too much text, looks AI-like"): descriptive titles ("Solvers on the organizers' practice set", "Accuracy", "Predicted score of 20", …), one short subtitle per view that only defines marks; no takeaway titles, no reading bullets, no interpretive annotations. Neutral labels kept: run names on the timeline, chance row and rule, 60 s limit, expected-at-chance tick on answer paths. Conclusions only in the closing decisions table. Source per row in tooltips; method in a three-line footnote.
- Composition: juxtapose, multiform on key `label`: accuracy | final-test score | English vs Catalan | seconds. One point selection `pick` (click; double-click clears) read by the four views; non-selected rows dim to 12–18%. Other panels (progress timeline, answer paths, RAM, levels, OCR, router, activity heatmap) are separate decisions on one page, each with its own takeaway.
- Rejected idioms: error bars (DAT-11, hard ends read as limits); quantile dot plot (PUR-14, needs a per-dot explanation); small multiples per solver (CMP-13).
- Validation:
  - a. Rules: EXP-08 pass (all length marks from zero); DAT-03 pass (intervals shown and defined); DAT-11 pass (graded bands); DAT-13 fixed (intervals by problem, not row); CMP-09 / INT-09 pass (one selection, four readers; inspector found no dead selection); TXT-07 pass (page key above the block).
  - b. Task-time: which solvers clear chance: immediate; best board solver: immediate; fits 60 s: immediate; Catalan gap: immediate; exact values: tooltip.
  - c. Render: Firefox headless screenshots at 1280 px; colour check by hue + shape.
  - d. Critique: `/vis-value-critique`, see `tukey_dashboard_critique.md`; the major findings are applied.
  - e. Reader acceptance: v1 accepted with changes (2026-11-15): less text, plain header, keep a short decisions table. v2 implements them.

## 4. Algorithm

- Pipeline: `load` → `derive` (intervals, predictive, chance row) → `core_views` + panel functions → `save` (vl.json, png, HTML from `page_template.html`).
- About 1 s per run. The page has no placeholder left (`{{` count 0).
- Rejected: Plotly (the user chose Altair); the Dashboard artifact type (it would replace the Altair specs the user asked for).

## 5. Assumptions and open points

- The final test resembles the practice set (balanced letters, sorted options). The predictive column depends on it.
- Laptop rows have no board timing: Qwen2.5-Math + translation can still fail the 60 s limit.
- Commit counts are a proxy for effort, not hours worked.
