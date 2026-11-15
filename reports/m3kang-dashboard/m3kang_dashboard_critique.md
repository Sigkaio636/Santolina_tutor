# Critique: M3Kang exploration dashboard (6 views + JS problem browser)

**Input**: `m3kang_dashboard.vl.json` + render `m3kang_dashboard.png`; idioms: bar (level picker), two
sequential heatmaps, diverging heatmap + dot-with-interval, connected dot plot, tick strip; data: 1,747
English problems (keys level 8, year 18, letter 5, points block 3, language 14), shard 0 of `high_quality`.
**Assumed purpose**: exploration; reader: the team (data analysts); tasks: where the data is thin, how biased
the answer key is, how much each level depends on the image, how long problems are, then drill into problems.

## Verdict

The dashboard earns its space. With nothing selected, each panel answers its question, and every title states
a computed fact a table would make you dig for: 55% exam completeness, levels 0–3 starting in 2015, D at 33–36%
for levels 0–1, 80% vs 44% image dependence. It loses value in two places. First, it presents in-sample letter
shares with a diverging colour scale and no uncertainty, so noise of ±8 pp at n≈120 reads as signal. Second, the
detail selections (cell, letter, block, brush) only reach the external browser: the other views do not react,
so the multiform linking the page promises is half done. The cheapest large gain is to let the strip, which
has one tick per problem, highlight the problems matching every active selection.

## Value scorecard (V = T + I + E + C)
| Component | Score | Why |
|---|---|---|
| T · Time | 3/3 | Extremum, range, distribution and lookup are immediate. Value labels sit in the cells and the strip shows raw items. Filtering to problems takes one click. |
| I · Insight | 2/3 | It shows that exams are half missing, the D bias at low levels, and image dependence falling with level. It hides whether the bias in a given cell is real. |
| E · Essence | 2/3 | The five-second read is "thin low levels, half-kept exams, D bias". Correct, but four colour legends compete. |
| C · Confidence | 2/3 | Source, n and definitions are present. Scope is ambiguous: "the dataset keeps 55%" is only shard 0 of the high_quality split. Letter-share cells carry no interval. |

Expressive: yes (ordinal keys on position, rates on position or luminance, nominal letters on position).
Effective: mostly (the bias heatmap puts its main value on colour, rescued by printed labels).
Appropriate: yes, for analysts in exploration mode.

## Findings

### Major
- **[DAT-03]** The letter-share cells have no uncertainty. Evidence: level 2 "B 25%" is drawn orange with
  n=146; its 95% interval (≈18–33%) contains chance. Consequence: the reader will chase letter biases that are
  noise, and only the best-guess column shows intervals. Fix: put the Wilson interval in the tooltip and mark
  with "•" the cells whose interval excludes 20%. Give the noise scale in the subtitle.
- **[INT-04][CMP-09]** The detail selections (`sel_cell`, `sel_letter`, `sel_block`, `sel_brush`) change
  nothing in the other views. Evidence: each is read only by its own `stroke` ring and by external JS. The
  inspector reports INT-09 for `sel_brush`, which is correct for the spec alone. Consequence: "which of the
  level-1 D answers need the image, and how long are they?" takes a trip through the table. Fix: the strip
  (fields level, year, label, points, words) reads all of them and keeps matching ticks opaque while fading
  the rest.
- **[TXT-08]** The scope behind the coverage claims is ambiguous. Evidence: the titles "keeps 55% of each exam" and
  "Only cat and eng cover every problem" do not name the split. The missing questions may sit in the
  `standard` split or in shards 1–3, which were not checked. Consequence: the team may conclude that the
  questions do not exist at all. Fix: name "high_quality shard 0" in both subtitles and say the other splits
  were not checked.

### Minor
- **[EFF-11]** Four colour legends (completeness, letter share, block, figure). Each sits next to its panel,
  and the two sequential heatmaps share one. Acceptable for analysts, no change.
- **[INT-08]** A level can only be picked in the top bar chart. Clicking a level row elsewhere does nothing.
  The hint text covers it.

## Deterministic check log
- `inspect_vegalite.py`: 17 major / 5 minor.
  - SCL-06 ×18, dismissed. They come from secondary layers (text, rules) that carry no title. Vega-Lite takes
    the explicit title from the primary layer, and the render shows "Exam year", "Level (0 = grade 5)", etc.
    No raw name appears in the PNG.
  - SCL-05 ×2, dismissed: an exception applies. The accuracy axis is fixed to 0–60% because zero is meaningful
    for a rate and the chance/baseline references must be on scale. The words axis starts at 0 with data from
    5, so the span ratio is fine.
  - INT-09 `sel_brush`, accepted and fixed together with INT-04.
  - EFF-11, see Minor.
- `inspect_image.py`: COL-05 "two salient colours merge under deuteranopia". These are the two strip blues,
  which are already separated by sub-row (`yOffset`). The deuteranopia and protanopia renders stay readable:
  the diverging scale becomes blue–yellow, and the blocks differ by luminance and shape.
- `run_check.py`: script ran headless, blocking findings: none.

## What to preserve
- Takeaway titles computed from the data, with n at each strip row.
- Completeness normalised by exam size, not raw counts.
- Diverging midpoint at 20% (chance), with chance and baseline references on the guess plot.
- One tick per problem with no jitter, and the medians.
- A single accent colour (vermillion) for selection everywhere.

## Redesign (applied)
- Bias heatmap: tooltip gains the 95% Wilson interval, "•" marks cells whose interval excludes 20%, and the
  subtitle states the noise scale.
- Strip: tick opacity reads `sel_level & sel_cell & sel_letter & sel_block & sel_brush`, so every selection
  shows its problems in the strip as well as in the browser.
- Coverage and language subtitles name the split and shard.
