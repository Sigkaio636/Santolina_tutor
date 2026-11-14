# Design: Central lends the most books; the top three branches make 41 % of all loans

| Decision record | `p-compare-values-across-categories--loans-per-branch-20261107` · new, reusing seed `compare-values-across-categories--sorted-horizontal-bar` (REUSE tier, score 0.93) · status declared |
| Library / host  | matplotlib 3.10 (project.yaml) · script |
| Data            | `loans.csv`, 6,000 rows, signature `table|k:categorical:some|v:quantitative:count`, period 2019–2024 |
| Outputs         | `loans_by_branch.py`, `out/loans_by_branch.png`, `out/loans_by_branch.svg`, `out/run_check.json` |
| Language        | dialogue en, code en |

## 1. Domain problem characterization
- Reader: `executive` — decides in under a minute; wants the number, the ranking and the
  direction; literacy medium; no interaction expected; modifiers none.
- Mode: explanatory.
- Question, in the reader's words: "Which branches lend the most books over the whole period?"
- Medium and constraints: a static figure in a report (`static-only`).
- Rejected readings of the problem: "How has lending per branch evolved over the years?"
  (that is trend-many-series, a second figure) and "How are loan durations distributed?"
  (distribution-single, not asked).
- Validation (threat: wrong problem): restatement "an executive wants to know which
  branches lend most, as a static explanatory chart" confirmed in call 2. Not done:
  observing real readers; adoption.

## 2. Data and task abstraction
| attribute | type | role | levels/range | notes |
|---|---|---|---|---|
| loan_date | temporal | (unused here) | 2019-01-01 … 2024-12-30, dd/mm/yyyy | parsed with `%d/%m/%Y` |
| branch_code | identifier | drop | 12 codes with leading zeros | read as string |
| branch | categorical | key (category) | 12 levels (band `some`) | |
| genre | categorical | (unused) | 6 | |
| days_on_loan | quantitative | (unused) | 1 … 51 | |
| returned_late | boolean | (unused) | yes/no | |
- Derived data: `loans = count of rows per branch`; `share = loans / total loans`; no
  normalisation (the question is about absolute volume); no filter; whole period.
- Tasks: why present / lookup / compare; low-level compare, find-extremum, sort,
  retrieve-value (all must be immediate); temporal none; Shneiderman overview.
- Rejected abstractions: per-year counts (answers a different question); loans per
  capita of the branch's district (no denominator in the data).
- Validation (threat: wrong abstraction): every term of the question maps to an
  attribute ("branches" → branch, "lend the most" → count per branch, "whole period" →
  no time filter); confirmed in call 3.

## 3. Visual encoding and interaction
- Idiom: `bar_chart`, horizontal, sorted.
| attribute | mark + channel | rank (Mackinlay) | expressiveness |
|---|---|---|---|
| branch | line mark, position-y (ordinal, sorted by loans) | position: 1st for nominal | nominal on position, order carries the value ranking (stated) |
| loans | length from zero (linear) | length: 3rd for quantitative, best after position | zero baseline keeps ratios honest (EXP-08) |
| highlight (top 3) | color-hue, neutral + accent | — | one pop-out feature, no legend |
- Ordering, scales: branches by loans descending (CMP-01); x from 0 with light vertical
  grid for value reading; no facets.
- Color plan: purpose highlight; neutral `#8c8c8c` + accent `#0072b2` (Okabe-Ito blue);
  CVD-safe (blue vs grey survives deuteranopia, checked with `colorcheck`); second cue =
  the title names the highlighted branches and the values are printed.
- Text plan: takeaway title computed in `takeaway()` → rendered "Central lends the most
  books (1,118 loans); the top three branches make 41% of all loans"; subtitle with period
  and what is highlighted; x axis "Loans (count)"; direct value labels at bar ends; footer
  with source and n = 6,000.
- Interaction plan: none (static medium); the single view answers the task (INT-02).
- Rejected idioms:
| idiom | reason | rule |
|---|---|---|
| pie_chart | 12 parts; angle comparison fails beyond 3–5 | IDM-PIE |
| dot_plot | differences are large (237 → 1,118); bars from zero keep ratios honest and the executive profile prefers bars | EXP-08 |
| data_table | the ranking task is faster on bars; the table is the fallback for exact quoting | PUR-02 |
| radial_bar_chart | outer bars look longer | EXP-07 |
- Validation (threat: wrong idiom):
  a. Rule checklist: EXP-08 pass (x from 0); CMP-01 pass (sorted); COL-03 pass (one neutral
     hue, one accent, no legend); SCL-12 pass (horizontal bars, labels horizontal); TXT-01
     pass (computed takeaway title); SCL-06 pass (units in axis title); TXT-08 pass
     (source, n).
  b. Task-time table: find-extremum immediate (top bar, accent); sort immediate; compare
     immediate (common baseline); retrieve-value immediate (printed labels).
  c. Render inspected: `out/loans_by_branch.png`; the sibling inspectors reported no
     findings; grayscale and deuteranopia derivatives in `out/inspect/`.
  d. Critique: not run (optional).
  e. Reader acceptance: accepted in call 5 (example run).

## 4. Algorithm
- matplotlib 3.10, host script, pipeline `load → derive → build_chart → save`.
- Rows in 6,000; rows after derivation 12; run time 1.1 s; limits none at this size.
- Rejected alternatives: Altair (not installed in this environment; would render only to
  HTML without `vl_convert`); Plotly (interaction not needed for a static report).
- Validation (threat: wrong algorithm): `run_check.py` ok = true, outputs png + svg, no
  blocking findings; the render matches section 3 (sorted horizontal bars from zero,
  three accents, printed values, computed title).

## 5. Decision record
See `vis-decisions/p-compare-values-across-categories--loans-per-branch-20261107.yaml`
(written by `record_decision.py`; `vis-decisions/project.yaml` stores library matplotlib).

## 6. Assumptions and open points
None: every stage was confirmed in the example dialogue.
