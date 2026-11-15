# Design: The base Qwen-Math loses 48% of M3Kang problems before its program runs, against 32% of the practice set (English)

| Decision record | p-compare-two-keys--where-each-solver-setup-loses-20261115 v1 · new · status declared |
|---|---|
| Library / host | Altair 6.3.0 + vl_convert (project.yaml: altair) · script writing one offline HTML file, a .vl.json and a PNG |
| Data | `data/solver_rows.csv` from `build_solver_data.py`: 1,379 rows, 22 grid runs (13 practice, 9 M3Kang), signature `table\|k:categorical:some+k:ordinal:few\|v:quantitative:share` |
| Outputs | `solver_dashboard.py`, `.html`, `.vl.json`, `.png`; `test_interaction.py` (8 browser checks); `inspect/` (CVD and grayscale renders) |
| Language | dialogue en, code en |

## 1. Domain problem characterization

- **Reader:** our team first (`data-analyst`: high literacy, sustained time, laptop), the judges of the datathon's "best dashboard" side challenge second. Every view has a computed or explicit title and a one-line reading guide for the second reader.
- **Mode:** analysis.
- **Main question:** where does each solver setup lose problems, on the practice set and on M3Kang?
- **Follow-up questions:** what do the board speeds change, and is M3Kang a fair stand-in for the practice set?
- **Medium:** a local interactive HTML page. It must be shareable, so it holds no problem statement, option or program: only IDs, levels, lengths, token counts and outcomes. This keeps the M3Kang licence and the organizers' rule for the practice set.
- **Rejected readings:** "what do the board speeds change" and "is M3Kang a fair proxy" as the main question. Both became the linked views.
- **Validation (threat: wrong problem):** restatement confirmed by the user on 2026-11-15. Not done: watching the team or a judge use it.

## 2. Data and task abstraction

| attribute | type | role | levels/range | notes |
|---|---|---|---|---|
| run (setup · input · dataset) | categorical | key | 22 | setup = model + prompt; input = eng, cat, cat → eng (NMT) |
| outcome | ordinal | key | 5 | the furthest funnel step |
| share | quantitative (share) | value | 0–1 | derived |
| read_tokens, written_tokens, budget | quantitative | value | 0–300 | from `grid.py` |
| extra_s | quantitative | value | 0 or 3 | NMT translation charged before the request |
| level, length band, option kind, figure | ordinal / categorical | keys of the proxy view | 8 / 3 / 3 / 2 | |

- **Derived data:**
  - `outcome` = cut at the cap if written ≥ token cap; else crashed if the program raised; else no option matched; else wrong or right.
  - `share` = problems of the run at the outcome / problems of the run.
  - `board seconds` = extra_s + read_tokens / read speed + written_tokens / write speed + 1, against the 57 s limit (the same formula as `grid.py`).
  - `rate` = programs right / problems, per slice.
- **Tasks:** why discover / browse / compare; low level: compare, find-extremum, characterize-distribution, retrieve-value; Shneiderman: overview, filter, details on demand.
- **Rejected abstractions:**
  - Raw counts: practice runs have 50 problems and M3Kang runs 80–83.
  - "Final right" (after the letter and prior) as the main measure: it hides where the program failed. It is in the tooltip instead.
- **Validation (threat: wrong abstraction):** confirmed by the user. The run totals in the CSV match the grid summaries (base Qwen-Math 29 / 26 on practice, for example).

## 3. Visual encoding and interaction

- **Idiom:** `heatmap` (the stored project idiom, reused for this new key) as the overview. A `scatterplot` and a `dot_plot` are the linked detail views.

| attribute | mark + channel | expressiveness check |
|---|---|---|
| run | rect, position-y | nominal on a position: ok |
| outcome | rect, position-x | ordinal in funnel order: ok |
| share | luminance (blues for losses, oranges for right) + % text | sequential, fixed domain 0–80 %: ok |
| picked run | dark outline (containment) | highlight only |
| read and write seconds | point, x and y on 0–60 s | quantitative on a common scale: ok |
| outcome in the scatter | color + shape | redundant second cue |

- **Ordering and scales:** practice above M3Kang; runs sorted by share right; outcomes in funnel order; fixed domains (0–60 s, 0–100 %) that do not move with a selection (CMP-01, SCL-08).
- **Colour plan:** blues for loss outcomes, the project accent (#d55e00) for right, the same mapping in the heatmap and the scatter. Datasets are black circles and light-blue squares (COL-02/04/05).
- **Text plan:** the title is computed from the data; the subtitle gives the source and n; each view has a one-line reading guide; the scatter shows "fits in time" and "right programs still in time", recomputed live (TXT-01/04/08).
- **Composition:** juxtaposed, multiform.

| view | idiom | role |
|---|---|---|
| funnel (practice and M3Kang panels) | heatmap | overview |
| board_time (practice and M3Kang panels) | scatterplot | detail |
| proxy (distribution and rate per slice) | dot_plot | detail |

| link | type | selection |
|---|---|---|
| funnel → board_time | filter | `pick` (setup + input; picks both datasets) |
| funnel → proxy (right half) | filter | `pick` |
| sliders → board_time | reconfigure | `read_tps`, `write_tps` |

- **Interaction plan:** the default state picks the base Qwen-Math in English at 5.2 / 3.0 tokens/s, so the page answers the main question before any click. The sliders stay pinned at the top of the page.
- **Rejected idioms:**

| idiom | reason | rule |
|---|---|---|
| stacked_bar_graph | middle outcomes compare by length only, with no common baseline | EXP-05 |
| dot_plot per outcome | a run's whole picture spread over five panels | CMP-09 |

- **Validation (threat: wrong idiom):**
  - a. **Rule checklist** (`run_check.py`): no blocking findings. Remaining majors:
    - SCL-06: categorical heatmap axes have no title on purpose.
    - EFF-08: five outcome shapes back up colour, they don't replace it.
    - EFF-11: six legends.
    - COL-05: two colours merge under deuteranopia; the shapes and % text are the second cue.
  - b. **Task-time:**
    - Biggest loss per run: immediate.
    - Two runs compared: immediate.
    - Effect of a speed: immediate (live counts).
    - Proxy fit per slice: takes work.
  - c. **Render inspected:** PNG, grayscale and three CVD renders in `inspect/`. The browser test (`test_interaction.py`) checks:
    - the default counts;
    - the sliders at 3.0 tokens/s reading;
    - a row click (Noema-2B);
    - the sliders staying in view;
    - no page errors.
  - d. **Critique:** not run.
  - e. **Reader acceptance:** accepted with one change (sticky sliders), 2026-11-15.

## 4. Algorithm

- Pipeline `build_solver_data.py` (grid JSONL + problem sources → CSV, no text) → `solver_dashboard.py` `load → derive → build_chart → save`.
- 1,379 rows in; the build takes about 8 s with the PNG export.
- **Fixes during the build:**
  - Vega-Lite aggregates take fields, not expressions: flags are computed first.
  - Labels caught clicks: the top outline layer gets an invisible fill.
  - The embed's own CSS beat the sticky rule: `.chart-wrapper` became a flex column.
- **Limit:** programs cut at the token cap needed more tokens than recorded, so faster speeds in the what-if do not show them recovered.
- **Rejected:**
  - Plotly: no PNG export, and linking across figures needs custom JS.
  - Streamlit: not installed, and it needs a server.
- **Validation (threat: wrong algorithm):** `run_check.py` ok, inspector ran the script; the browser test passes 8 of 8.

## 5. Decision record

Saved as `.claude/vis-decisions/p-compare-two-keys--where-each-solver-setup-loses-20261115.yaml` (source: `record.json`).

## 6. Assumptions and open points

- The board speeds of Qwen-Math are estimates (5.2 / 3.0 tokens/s) until Pau measures them; move the sliders when he does.
- The run-to-run noise of `--parallel 4` (15 against 19 programs right on the same M3Kang rows) is not shown.
- Possible next view: a problem × setup matrix (idea 4 of the brainstorm).
