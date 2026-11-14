# Design: Harbour earns the most per visit; Station, the busiest store, earns far less

| Decision record | reused `correlation-two-quantities--linked-scatter-and-bars` (seed) · status declared |
| Library / host  | Altair 6 / Vega-Lite (coordinated views) · script + Streamlit (`app.py`) |
| Data            | `store_weeks.csv`, 156 rows (6 stores × 26 weeks), synthetic and seeded (`make_data.py`) |
| Outputs         | `store_sales_linked.py`, `out/store_sales_linked.png/.html/.vl.json`, `app.py` |
| Language        | dialogue en, code en |

## 1. Domain problem characterization
- Reader: data-analyst — reads scatterplots, has minutes, works on a desktop screen.
- Mode: exploration.
- Questions: "Which stores turn visits into sales?" and "How much does each store sell, in the weeks I am looking at?"
- Rejected readings: a weekly trend per store (that is `trend-few-series`).
- Validation (threat: wrong problem): assumed; this is a worked example, no reader was interviewed.

## 2. Data and task abstraction
| attribute | type | role | levels/range | notes |
|---|---|---|---|---|
| store | categorical | category | 6 | |
| week | ordinal | item id | 1–26 | each row is one store-week |
| visits | quantitative | measure | ≈ 260–780 | count per week |
| sales_eur | quantitative | measure2 | ≈ 2.5–14.6 thousand | derived `sales_keur = sales_eur / 1000` |
- Tasks: discover / explore / compare; low-level correlate, cluster, find-anomalies, compare.
- Validation (threat: wrong abstraction): both question terms map to attributes; assumed.

## 3. Visual encoding and interaction
- Idiom: `scatterplot` (primary) with a linked `bar_chart`.
- Composition: juxtapose, relation multiform (same store-weeks, different encodings).

| view | idiom | role |
|---|---|---|
| scatter | scatterplot: visits (x) × sales (y), one point per store-week | focus |
| bars | bar_chart: total sales per store, sorted, over a pale bar of all weeks | context |

| link | type | selection |
|---|---|---|
| scatter → bars | filter (bars total only the brushed weeks; the pale bar keeps the context) | `brush` (interval, x and y) |
| bars → scatter | highlight (the clicked store's weeks turn blue in both views) | `pick` (point, field `store`) |

- Scales: the two views draw different measures, so no shared scale; the bar axis has a fixed domain from the full data so brushing does not rescale it (DAT-14).
- Color plan: highlight only, one accent (#0072b2) on neutral grey in both views (INT-10); no hue per store.
- Text plan: computed takeaway title; each view says what it shows and how to interact.
- Rejected idioms: | six hues, one per store | a legend to match and no totals | COL-04, EFF-11 | · | small multiples of six scatterplots | comparison of clouds across panels is slow | CMP-13 |
- Validation (threat: wrong idiom):
  a. Rule checklist: CMP-09 pass (linked both ways), INT-09 pass (both selections are read by another view), INT-10 pass, INT-11 pass (filter keeps a context bar), EXP-08 pass (bars from zero).
  b. Task-time: correlate immediate; compare totals immediate; find one store's weeks one click.
  c. Render inspected: `out/store_sales_linked.png` (default state), and both selections exercised in the Streamlit app.
  d. Inspector: `inspect_vegalite.py` on the spec reports no findings and one linked pair of views.

## 4. Algorithm
- `templates/dashboard_altair.py.tmpl`: `selections()` → `build_views()` → `compose()`.
- Validation (threat: wrong algorithm): `out/run_check.json`: ok, no blocking findings, Streamlit smoke test without exceptions.

## 6. Assumptions and open points
Worked example on synthetic data: reader, tasks and acceptance are assumed.
