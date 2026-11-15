# Design: glm5.3-flash is cheapest and fastest (median 943 tokens, 11 s); all models are usable on 9/10 problems

| | |
|---|---|
| Decision record | `p-distribution-compare-groups--teacher-models-cost-vs-20261114` v1 · new · status declared |
| Library / host | Altair 5 / Vega-Lite (`project.yaml`) · Streamlit app (`app.py`) |
| Data | `data/processed/explanations/metrics.csv` (git-ignored), 40 rows = 4 models × 10 problems, signature `table\|k:categorical:few+k:ordinal:some\|v:quantitative:amount+v:quantitative:amount+v:quantitative:share` |
| Outputs | `teacher_cost_quality.py`, `app.py`, `out/teacher_cost_quality.{png,html,vl.json}` (git-ignored: the HTML embeds per-call data) |
| Language | dialogue en, code en |

The title is computed from the data and changes when the metrics table changes. It is quoted here as rendered on 2026-11-14.

## 1. Domain problem characterization

- **Reader:** data analyst, the team member who runs the teacher models. Reads distributions and strip plots without help. Uses the dashboard at a laptop to decide which model to run at scale.
- **Mode:** analysis.
- **Question:** how do output tokens and seconds per problem compare across the teacher models, and how often does each one produce a usable record?
- **Medium:** a local web app (Streamlit). Interaction is allowed, and the data stays on the laptop.
- **Rejected readings:**
  - "Token distributions only" leaves out quality, and the reader must trade cost against quality.
  - "Difficulty effect by level" is too sparse at 10 problems (1–2 per level).
- **Validation (threat: wrong problem):** the user confirmed the restatement on 2026-11-14. Not done: watching how the dashboard is used after deployment.

## 2. Data and task abstraction

| Attribute | Type | Role | Levels / range | Notes |
|---|---|---|---|---|
| `teacher` | categorical | key | 4 | Model ID |
| `id` + `language` → `problem` | categorical | key | 10 | `id` alone is not unique (translations) |
| `level` | ordinal | key | 0–7 | Problem difficulty band |
| `completion_tokens` | quantitative, amount | value | 570–12,985 tokens | From API usage |
| `reasoning_tokens` | quantitative, amount | value | Reported only by glm5.3-flash and deepseek-v4-flash | Empty means not reported, not zero |
| `seconds` | quantitative, amount | value | 0.3–357.5 s | Wall time per call, including retries. Values under 1 s come from parallel calls, not real speed |
| `usable` | boolean | value | — | See derived data |

**Derived data**
- `usable` = the model reached the key, gave 5 options, and did not dispute the key, **and** the problem is trusted. A problem is trusted when a strict majority of the teachers that answered reached the key. This is the same rule as the fine-tuning filter in `generate_explanations.build_sft`.
- `status` = "usable" or "not usable".
- `median_tokens` and `median_seconds` per model are rounded half up, so the title and the labels show the same number.
- `total_tokens_k` = sum of `completion_tokens` / 1000 per model.
- `usable_pct` = 100 × `n_usable` / `n_calls`.
- `tokens_per_s` = `completion_tokens` / `seconds`.
- Fixed axis domains are computed from the full data. No normalisation.

**Tasks**
- Why: discover, browse, compare.
- Low-level tasks: characterize distribution, compare, find anomalies, determine range.
- Shneiderman: overview, details on demand.

**Rejected abstractions**
- *Aggregated only* (the user's first data choice): one row per model cannot show a distribution and hides the 357 s and 13k-token outliers. The user then chose "aggregated headline + calls" (call 6, reserve).
- *Model × level grid*: 1–2 calls per cell.

**Validation (threat: wrong abstraction)**
- Every term of the question maps to an attribute: tokens → `completion_tokens`, seconds → `seconds`, usable → `usable`.
- The user confirmed the conflict resolution.
- Remaining limit: *cost* is measured in tokens, not euros. The plan models are flat-rate, so this is a proxy.

## 3. Visual encoding and interaction

**Idiom:** `strip_plot` (strip plot with a median marker), from stored seed `distribution-compare-groups--strip-with-summary`. It was adapted from the scientist-reviewer profile to the data-analyst profile, and a headline row was added.

| Attribute | Mark + channel | Rank (Mackinlay) | Expressiveness |
|---|---|---|---|
| Model | position-y (row) | 1 for nominal grouping | ✓ |
| Tokens / seconds per call | point, position-x, zero baseline | 1 | ✓ quantitative |
| Model median | tick, position-x | 1 | ✓ |
| Status | color hue + shape | Hue: 2 for nominal | ✓, 2 levels with a second cue |
| Level | yOffset inside the row | Ordinal stacking | ✓ deterministic, no random jitter (EXP-21) |
| Selection | opacity (fade the rest) | — | One highlight rule, no extra hue (INT-10) |

- **Ordering:** models by usable rate (descending), then median tokens (ascending), the same in every view (CMP-01).
- **Scales:** zero baselines (EXP-08). Per-call views share fixed domains taken from the full data (SCL-08, DAT-14). The headline medians use their own zero-based scale (see 3a).
- **Color:** neutral grey `#8c8c8c` against vermillion `#d55e00` for "not usable". Shape (circle or diamond) is the second cue. `colorcheck`: ok for colour-blind readers, no confusable pairs (COL-02/04/05).
- **Text:**
  - Title: "glm5.3-flash is cheapest and fastest (median 943 tokens, 11 s); all models are usable on 9/10 problems".
  - The subtitle covers how to read and click the dashboard, the definition of "usable", the source, n, and the reasoning-token and timing caveats.
  - Axis titles carry units, and direct value labels sit in the headline row (TXT-01/04/08).

**Composition:** juxtapose, multiform, all data shared.

| View | Idiom | Role |
|---|---|---|
| `sum_tokens` | dot_plot (lollipop) | overview, holds the `model` selection |
| `sum_seconds` | dot_plot (lollipop) | overview |
| `sum_total` | bar_chart | overview |
| `sum_usable` | bar_chart | overview |
| `strip_tokens` | strip_plot | focus, holds the `problem` selection |
| `strip_seconds` | strip_plot | detail |
| `scatter` | scatterplot | context: tokens vs seconds |

| Link | Type | Selection |
|---|---|---|
| `sum_tokens` → every other view | highlight | `model` (click) |
| `strip_tokens` → `strip_seconds`, `scatter` | highlight | `problem` (click, double-click clears) |

**Interaction plan:**
- The Streamlit widgets filter by model, language and level. Each option label shows the number of calls behind it.
- With nothing selected, the dashboard already answers the main question (INT-02).

**Rejected idioms**

| Idiom | Reason | Rule |
|---|---|---|
| `box_plot` | About 10 calls per model: boxes hide n and the single outliers that matter | EXP-16 |
| `violin_plot` | A density estimate at n ≈ 10 shows bandwidth artefacts, not shape | EXP-15 |
| `bar_chart` of means | Hides the 357 s and 13k-token outliers | EXP-16 |
| Aggregated-only `dot_plot` | Cannot show per-call distributions; kept only as the headline row | EXP-16 |
| Shape per model in the scatter | Clashed with the status shape legend; model shown in the tooltip instead | COL-04 |

**Validation (threat: wrong idiom)**
- **a. Rule checklist:**
  - Pass: EXP-08, EXP-11 (no dual axes), EXP-21, COL-04, COL-05, TXT-01, TXT-08, CMP-01, INT-09 (both selections are read by other views), INT-10.
  - SCL-06 failed in the first render (raw field names in the median-tick axis titles, and a removed y axis) and was fixed.
  - SCL-08 minor, accepted: the headline median panels use their own scale, not the per-call scale. With a shared scale the medians were squeezed into the first 10% of the axis. They are a different measure (a median, not a call), and every one carries a direct value label.
- **b. Task-time table:**

| Task | Time |
|---|---|
| Cheapest or fastest model | Immediate (headline row) |
| Spread and outliers per model | Immediate (strips) |
| Is an outlier a hard problem or one model's failure? | One click |
| Do tokens explain time? | Immediate (scatter) |

- **c. Render inspected:** `out/teacher_cost_quality.png`. Grayscale and deuteranopia/protanopia/tritanopia simulations in `out/inspect/` keep the failures distinct by shape and lightness. `inspect_image`: no findings.
- **d. Critique:** the vis-value-critique inspectors ran through `run_check.py`. Findings are as listed in (a).
- **e. Reader acceptance:** accepted by the user on 2026-11-14.

## 4. Algorithm

- **Pipeline:** Altair (uv environment: `altair`, `vl-convert-python`, `pandas`). Streamlit host. `load` → `derive` → `build_chart` → `save`.
- **Size and speed:** 40 rows in, 40 rows after derivation (summary columns repeated per row so every view reads one frame). The run takes a few seconds.
- **Rejected alternatives:**
  - Plotly: linking two charts needs Streamlit reruns.
  - matplotlib: no interaction.
  - The system Python's Altair fails to import (`typing_extensions`), so the dashboard runs through `uv run --with …`.
- **Validation (threat: wrong algorithm):**
  - `run_check.py`: `ok: true`, no blocking findings, the inspectors ran the script.
  - Streamlit AppTest: 0 exceptions, 6 elements.
  - Two bugs were fixed during generation:
    - Selections must be added to a mark layer, not to a layer chart.
    - `alt.datum(0)` used as a lollipop stem breaks vl-convert; a `zero` column is used instead.
  - The render matches stage 3.

## 5. Decision record

Saved as `.claude/vis-decisions/p-distribution-compare-groups--teacher-models-cost-vs-20261114.yaml`. The source is `reports/dashboard/record.json`.

## 6. Assumptions and open points

- **Small sample:** 10 problems. The medians and the usable rate are fragile, and every model sits at 9/10 now. Re-run after `generate_explanations --n 50`:
  1. `python -m santolina_tutor.explanation_metrics`
  2. Reload the app.
- **Timings:** under parallel calls they are noisy, and values near 0 s are artefacts. Use them for rough comparison only.
- **Reasoning tokens:** only glm5.3-flash and deepseek-v4-flash report them. They appear in the tooltip and the table, not as a view.
