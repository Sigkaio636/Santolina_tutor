# Design: M3Kang at a glance (exploration dashboard)

| Decision records | 5 new, status declared (2026-11-14). Composition stored on `p-matrix-pattern-two-keys--exam-completeness-per-level-20261114`. |
|---|---|
| Library / host | Altair 6.3.0 + vl_convert 1.9.0 (project.yaml: altair) · script writing one offline HTML file |
| Data | `data/m3kang_rows.csv` (from `build_data.py`): 10,155 rows, 1,747 English problems, years 2007–2024, qualcomm/M3Kang high_quality shard 0 |
| Outputs | `m3kang_dashboard.py`, `.html` (self-contained, Vega inlined), `.vl.json`, `.png`; `test_interaction.py`; `m3kang_dashboard_critique.md` |
| Language | dialogue en, code en |

## 1. Domain problem characterization
- **Reader:** our datathon team (`data-analyst`). Comfortable with heatmaps and strip plots, has time, works on a
  laptop. Wants to decide the RAG, fine-tuning and tutor design.
- **Mode:** exploration.
- **Questions:**
  1. Where is the data thin, by level, year and language?
  2. How biased is the answer key, and which constant guess beats the 22.5% baseline?
  3. How much does each level and question block need the image?
  4. How long are the problems against the board's reading budget?
  5. Which concrete problems sit behind each pattern?
- **Medium:** a local HTML file. M3Kang is licensed for research only, so nothing is published and problem
  text and images stay on disk.
- **Rejected readings:** jury or Project Hub (explanatory, static) and teachers (no statistics). Both were
  offered and declined. They come later as separate decisions.
- **Validation:** restatement confirmed by the user on 2026-11-14. Not done: observing the team use it.

## 2. Data and task abstraction
| attribute | type | role | levels/range | notes |
|---|---|---|---|---|
| level | ordinal | key | 0–7 | 0 = grade 5. Levels 0–3 only from 2015. |
| year | temporal (year) | key | 2007–2024 | parsed from `id` |
| language | categorical | key | 14 | ISO 639-3 |
| label | categorical | key | A–E | correct letter |
| qnum | ordinal | key | 1–24 / 1–30 | parsed from `id` |
| text_only | boolean | key | — | false = the problem needs the image |
| text_words | quantitative | value | 5–120 | English statement only |

- **Derived data:**
  - `exam_size` = 24 for levels 0–1, 30 otherwise
  - `completeness` = problems per (level, year) / `exam_size`
  - `points` = 3 + (qnum − 1) // (exam_size / 3), the official 3/4/5-point blocks
  - `share` = n(level, label) / n(level), with a 95% Wilson interval
  - `rate` = needs image / n per (level, points)
  - `est_tokens` = words × 1.35
  - `read_s` = est_tokens / 11
  - language `share` = n in language / n English, per level
- **Tasks:**
  - why: discover / browse / compare-identify
  - low level: find-anomalies, find-extremum, compare, characterize-distribution, compute-derived (best guess),
    retrieve-value
  - temporal: existence, pattern
  - Shneiderman: overview, filter, details-on-demand
- **Rejected abstractions:**
  - Raw counts per exam: exams have 24 or 30 questions (DAT-02).
  - The maximum question number seen as the exam size: understates exams whose last questions are missing.
  - Characters instead of words.
  - Raw question number: not comparable between 24- and 30-question exams.
- **Validation:** confirmed by the user. Every term of the questions maps to an attribute or a derived one. No
  topic attribute exists yet, so topic panels wait for the enrichment step.

## 3. Visual encoding and interaction

| view | idiom | encoding (attribute → channel) |
|---|---|---|
| picker | bar_chart | level → x; problems → length from zero; selected level → accent hue |
| cov | heatmap | year → x; level → y; completeness → luminance (blues 0–100%); count → text |
| lang | heatmap | language → y (sorted by coverage); level → x; share → luminance (same scale); % → text |
| bias | heatmap + dot/interval | letter → x; level → y; share → diverging luminance (blue–orange, midpoint 20%); % and "•" → text. Best guess: accuracy → x position, 95% Wilson → rule, chance and baseline → reference rules |
| fig | dot_plot | rate → x (0–100%); level → y; block → luminance + shape; level → connecting line |
| strip | strip_plot | words → x from zero; level → y; figure → yOffset sub-row + hue; median → black tick; n → text |
| browser | data_table (JS) | rows matching every active selection plus the text search; a click shows the image |

- **Ordering and scales:**
  - Levels ascend everywhere, years run in order, languages go by coverage.
  - Shares use fixed domains (0–100%, and 0–40% for the bias heatmap) that do not move when you select
    (DAT-14).
  - Bars start at zero.
- **Colour plan:**
  - Sequential blues for completeness and coverage.
  - Diverging blue–orange around chance for letter bias.
  - Luminance plus shape for blocks.
  - One highlight colour everywhere, vermillion `#d55e00`. Non-selected marks fade to 22% opacity, and selected
    cells get the accent stroke.
  - CVD check: `colorcheck.py` OK. The deuteranopia and protanopia renders were inspected.
- **Text plan:**
  - Each panel title is a takeaway computed from the data:
    - "Levels 4–7 hold 70% of the 1,747 problems; levels 0–3 start in 2015"
    - "The dataset keeps 55% of each exam on average"
    - "Only cat and eng cover every problem; next is fra with 82%"
    - "Always answering D scores 25%; the best letter per level reaches 36% (D at level 1)"
    - "80% of level-0 problems need the image, 44% at level 7"
    - "Median problem: 40 words, about 54 tokens or 5 s of reading on the board"
  - Subtitles give the definition, units, scope and how to interact. The page title names the source and the
    licence.

**Composition:** juxtapose, multiform, subset sharing.

| link | type | selection |
|---|---|---|
| picker → cov, lang, bias, fig, strip | highlight (fade) | `sel_level` |
| cov, bias, fig → strip | highlight (fade) | `sel_cell`, `sel_letter`, `sel_block` |
| picker, cov, bias, fig, strip → browser | filter (JS reads `*_store`) | all five |

The default state, with nothing selected, answers questions 1–4 (INT-02). Every selection changes another view
(INT-09 resolved after the critique).

**Rejected idioms:**

| idiom | reason | rule |
|---|---|---|
| grouped bars (stored seed) for bias | 40 bars in 5 hues, crowded | EFF-16 |
| 100% stacked bars for bias | only A and E share a baseline | EFF-06 |
| heatmap for figure dependence | luminance is weaker than position for rates | EFF-01 |
| violins (stored REUSE seed) for length | hide the individual problems the browser needs; bandwidth choice | EXP-22 |
| histogram per level | loses details on demand | INT-02 |
| bubble or small multiples for coverage | area is inaccurate; more space for the same task | EFF-02, CMP-13 |

**Validation (threat: wrong idiom):**
- a. **Rule checklist:**
  - EXP-08 pass: bars from zero.
  - COL-02 pass: sequential for quantities, diverging around a stated midpoint.
  - COL-05 pass: second cues are printed values, shape and sub-row.
  - EXP-21 pass: no jitter.
  - DAT-02 pass: completeness normalised by exam size.
  - DAT-03 pass after fix: Wilson intervals and the "•" marker.
  - TXT-08 pass after fix: scope named.
  - INT-09 and CMP-09 pass after fix: the strip reads every selection.
  - SCL-06: inspector findings dismissed, because the render shows explicit titles and the raw names belong
    to untitled secondary layers.
- b. **Task-time table:**
  - Immediate: gaps per exam, thinnest languages, over-represented letters, image dependence per level, median
    length.
  - Work: listing the problems behind a cell (one click).
  - Nothing is impossible.
- c. **Render inspected:** `m3kang_dashboard.png`, plus the deuteranopia and protanopia simulations in
  `check/inspect/`.
- d. **Critique:** see `m3kang_dashboard_critique.md`. Verdict: earns its space. Three major findings were
  applied (DAT-03, INT-04/CMP-09, TXT-08).
- e. **Reader acceptance:** accepted by the user on 2026-11-14.

## 4. Algorithm
- Pipeline: `load` → `derive` (pandas, 7 small tables) → `build_views`/`compose` (Altair vconcat/hconcat) →
  `write_page` (vl_convert JS bundle inlined + spec + browser rows as JSON) → `.vl.json`/`.png`.
- Rows in: 10,155. Largest view: 1,747 ticks. Build time ≈ 8 s. HTML ≈ 2.2 MB. Vega uses the SVG renderer so
  the marks carry aria-labels, and CSS turns off clicks on value labels.
- **Rejected:**
  - Plotly: cross-view linking needs Dash or custom JS.
  - matplotlib: static.
  - Streamlit: needs a server.
- **Validation:**
  - `run_check.py`: ok, no blocking findings, PNG rendered.
  - `test_interaction.py` (Playwright + system Chromium): 6/6 pass. Default 1,747 rows; level 1 → 106; level
    1 + D → 38; image loads; search; no page errors.

## 5. Decision records
Saved in `.claude/vis-decisions/`:
- `p-matrix-pattern-two-keys--exam-completeness-per-level-20261114` (carries `solution.composition`)
- `p-compare-two-keys--translated-share-per-language-20261114`
- `p-compare-two-keys--correct-letter-share-per-level-20261114`
- `p-compare-two-keys--share-of-problems-needing-the-20261114`
- `p-distribution-compare-groups--problem-length-per-level-and-20261114`

Source answers: `records/*.json`.

## 6. Assumptions and open points
- Tokens ≈ 1.35 × English words is a rough estimate. Measure it with the board's tokenizer once it arrives.
- 11 tok/s reading speed comes from the challenge README, not from our board.
- Only high_quality shard 0 was read. Whether the missing questions exist in the `standard` split is unchecked.
- Next panels after preprocessing:
  - topic × level
  - OCR or Haiku option success by level, topic and figure
  - the reasoning-model accuracy by topic and language

  Each will be a new decision added to the composition. The browser already has room for a topic column.
