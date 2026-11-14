# Critique: quarterly sales by product line, bars with growth overlay (+ market-share pie)

**Input**: `examples/bad_sales_chart.py` (matplotlib). Figure 1: 8 product lines (nominal
key) × sales in k€ (quantitative) as bars, with growth % and a "target" series overlaid
on a second y axis. Figure 2: pie of market share, 8 slices.
**Assumed purpose**: explanatory, for a management audience; task: compare sales across
product lines and see which ones grow. The user did not state a purpose; the overlay of
growth on sales suggests the intended message is "which lines sell most and which are
growing".

## Verdict

The chart answers neither question honestly. Sales differ by at most 8 % (390–421 k€),
but a y axis cut at 385 draws Gizmos as five times taller than Thingamajigs, so the
first thing a reader sees is a difference that does not exist in the data. The growth
series on a second axis crosses the bars at points that mean nothing, the eight-hue
rainbow forces a legend that merely repeats the x axis, and nothing in the figure says
what, when or in what units. A sorted dot plot of sales with the growth figures printed
beside each product (or a two-panel small multiple) would answer both questions in one
glance; a table of 8 × 2 numbers would already beat this figure. The pie adds nothing
the sorted list does not show better.

## Value scorecard (V = T + I + E + C)

| Component | Score | Why |
|---|---|---|
| T · Time | 1/3 | Extremum (largest sales) needs a serial comparison of bars of nearly equal height on a truncated scale; retrieving a value needs the grid and a rotated label; correlating growth with sales is impossible because the two scales are arbitrary; sort/range need mental work. |
| I · Insight | 0/3 | The only "insight" the picture offers (large sales differences, growth tracking sales) is an artifact of the truncated axis and the dual scale. The real insight (sales are flat across lines, growth varies a lot) is hidden. |
| E · Essence | 0/3 | The five-second impression (tall vs short bars, a zig-zag line) is wrong. No title to anchor it. |
| C · Confidence | 0/3 | No units, no period, no source, raw field names (`sales_k`, `growth`), an unexplained "target". A skeptical reader distrusts it on sight. |

Expressive: **no** (truncated length marks, line over nominal categories, decorative hue).
Effective: **no** (eight hues + legend, dual axis, rotated labels, dark grid competing with
data). Appropriate: **no** (a 2-column table outperforms it).

## Findings

### Critical
- **[EXP-08 / TRUNC-1]** Bar axis starts at 385 k€. Evidence: `ax.set_ylim(385, 425)`,
  bar values 390–421. Consequence: Gizmos (421) is drawn ~7× taller than Thingamajigs
  (390) for an 8 % difference; the lie factor is about 90. Fix: bars from zero (and then
  the bars become useless because the differences vanish, which is the honest picture),
  or switch to a sorted dot plot whose axis may start at 380 with the baseline stated
  (SCL-02).
- **[EXP-11]** Growth and "target" on a second y axis over the bars. Evidence: `twinx()`,
  left axis 385–425, right axis −1.2–3.2. Consequence: the points where the line crosses
  the bars, and which bar the line "sits on", are artifacts of two arbitrary ranges;
  readers read co-movement that is not in the data. Fix: separate panel for growth
  (aligned small multiples sharing the product order) or print growth as a label next to
  each product.
- **[EXP-03 / TRUNC-10]** Lines connect nominal products. Evidence: `ax2.plot(products,
  …)`. Consequence: the zig-zag suggests a trajectory from Widgets to Sprockets; there is
  no order among products. Fix: points or labels, not connected lines.

### Major
- **[COL-03, EFF-11]** One hue per bar (jet colormap) and a legend that repeats the x
  axis. Evidence: `color=plt.cm.jet(...)`, legend with 8 entries. Consequence: the reader
  matches hue ↔ legend ↔ bar three times for nothing; the legend covers the top-right
  bars. Fix: one neutral grey, one accent on the line of interest, no legend.
- **[COL-05, ACC-01]** Growth (green) vs target (red), and jet's lime/amber bars, merge
  under deuteranopia. Evidence: simulated ΔE 7–12 for the red/green lines and for bars
  5–6. Consequence: ~8 % of male readers cannot tell growth from target. Fix: blue vs
  orange, plus different markers and direct labels at the line ends.
- **[TXT-01 / TEXT-1, TXT-08]** No title, no period, no source, no definition of
  "target". Consequence: the reader does not know what is being compared or when; C = 0.
  Fix: title with the takeaway ("Sales are flat across lines; Gizmos and Whatsits grow
  fastest, Q3 2025"), subtitle with units and source.
- **[SCL-06]** Axis titles are raw variable names without units (`product_name`,
  `sales_k`, `growth`). Fix: "Sales (k€)", "Growth vs. previous quarter (%)"; drop the
  category axis title.
- **[COL-07, CLT-01]** Black gridlines (lw 1.2) and a peach background compete with the
  data; four colored low-contrast bars fall under 3:1 against that background. Fix: white
  background, light grey gridlines only if values must be read.
- **[SCL-12]** Category labels rotated 60° and clipped. Fix: horizontal bars/dots with
  labels at the left.
- **[CMP-01]** Products are in an arbitrary order; with values within 8 % of each other
  the ranking is unreadable. Fix: sort by sales (or by growth, if that is the message).
- **[ACC-05]** Legend text at 7 pt.
- **[IDM-PIE, EFF-02]** Figure 2: 8 slices, exploded, shadowed, starting at 30°, with
  the Set1 red–green palette. Consequence: shares of 11, 8, 6, 5 and 3 % cannot be
  compared by angle; the explode and shadow distort areas. Fix: a sorted horizontal bar
  of share (same product order as figure 1 for consistency), or fold share into the
  product table.

### Minor
- **[CLT-04]** Two legends on one panel (bars and lines).
- **[TXT-07]** "target" is undefined (target growth? target sales?).

## Deterministic check log
- `inspect_matplotlib.py`: EXP-08 (ylim 385–425, min bar 390); EXP-11 (twin axes);
  EXP-03 (line over tick labels Widgets…); COL-03 (8 colors for 8 bars); EFF-11 (legend
  8 entries); COL-05 (red+green; deuteranopia ΔE 12.4 between `#b7ff40` and `#ffb900`);
  COL-06 (4 bar colors < 3:1 on `#ffe9c6`); COL-07 (black grid); SCL-06 ×3; SCL-12
  (rotation 60); CMP-01 (unsorted); ACC-05 (7 pt); TXT-01; IDM-PIE (8 slices, exploded,
  start 30°); CLT-01 (shadow, colored background).
- `inspect_image.py` on the render: red and green prominent; deuteranopia merges
  `#bc1001` with `#017e01` (ΔE 7.2); OCR found no title band, no units.
- `lie_factor.py --data 390 421 --visual 5 36` (bar heights in px above the 385
  baseline): lie factor ≈ 78 → EXP-07.
- Dismissed: SCL-08 (different y ranges across panels) is the dual axis already
  reported, not a facet problem.

## What to preserve
- The intent to show sales and growth together per product: keep both, side by side.
- Product names are short and readable; keep direct labeling.

## Redesign
- Idiom: two aligned horizontal panels (small multiples) sharing the product order:
  left, a dot plot of sales (k€) sorted descending, axis from 380 with the baseline
  labeled, or bars from zero if the message is "all lines sell about the same"; right, a
  dot plot of growth (%) with a reference line at 0 and the target drawn as a hollow
  marker on the same row.
- Encodings: product → vertical position (shared); sales → x position; growth → x
  position in panel 2; target → hollow marker, same row.
- Color plan: grey for all, one accent (blue) for the lines growing above target, or
  none at all; no legend.
- Text plan: title with the takeaway; subtitle "Q3 2025, k€ and % vs Q2, source: ERP";
  values printed at the dot ends; "target = plan growth" footnote.
- Market share: a third column of the same table-like layout ("share %"), sorted with
  the rest; no pie.
