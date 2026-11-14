# Rules catalog

Each rule: **ID** (kind, severity) statement. *Source.* Exception.

- Kind **DET**: checkable mechanically from the spec, code, data or pixels. The
  inspectors in `scripts/` implement the ones marked ⚙ (others are DET in principle but
  need data or measurement the script may not have).
- Kind **SEMI**: deterministic trigger, judgment verdict (check the exception).
- Kind **JUDG**: needs reasoning about purpose, reader, task or domain.
- Severity: **crit** (misleads or blocks the main task), **major** (slows the task,
  hides insight, loses readers), **minor** (small time or trust cost).

Sources (short names used below):
MUNZNER = Munzner, *Visualization Analysis and Design*, 2014 ·
TUFTE = Tufte, *The Visual Display of Quantitative Information*, 1983/2001, and
*Envisioning Information*, 1990 · WARE = Ware, *Information Visualization: Perception
for Design*, 3rd ed. 2013 · FEW = Few, *Show Me the Numbers*, 2004, *Now You See It*,
2009 · WILKE = Wilke, *Fundamentals of Data Visualization*, 2019 · CAIRO = Cairo, *The
Functional Art*, 2013, *How Charts Lie*, 2019 · SCHWABISH = Schwabish, *Better Data
Visualizations*, 2021 · DO-NO-HARM = Schwabish & Feng, *Do No Harm Guide*, Urban
Institute 2021 · BERTIN = Bertin, *Semiology of Graphics*, 1967/1983 · CARD = Card,
Mackinlay & Shneiderman, *Readings in Information Visualization*, 1999; Card 2008 ·
MACKINLAY = Mackinlay 1986 · CLEVELAND = Cleveland & McGill 1984; Cleveland 1993 ·
STEVENS = Stevens 1957 · WEBER = Weber's law (Fechner) · HEALEY = Healey & Enns 2012 ·
PALMER = Palmer & Rock 1994 · GARNER = Garner 1974 · SHNEIDERMAN = Shneiderman 1996 ·
AMAR = Amar, Eagan & Stasko 2005 · STASKO = Stasko, EuroVis 2014 capstone / BELIV 2014 ·
YI = Yi, Kang, Stasko & Jacko 2007 · VAN WIJK = van Wijk 2005 · KOSARA = Kosara &
Skau 2016 (pies) · HEER = Heer & Bostock 2010 · BORKIN = Borkin et al. 2013, 2016 ·
KONG = Kong, Liu & Karahalios 2018 (titles) · NIELSEN = Nielsen 1993 (response times) ·
WCAG = WCAG 2.1 · BREWER = Brewer, ColorBrewer · OKABE = Okabe & Ito 2008 · MUTH =
Muth, Datawrapper blog (colorblindness, fonts) · FLANNERY = Flannery 1971 · ANSCOMBE =
Anscombe 1973; Matejka & Fitzmaurice 2017 (Datasaurus) · HOLDER = Holder & Xiong 2022
(dispersion vs disparity, deficit framing) · DIMARA = Dimara, Bezerianos & Dragicevic
2017 (attraction effect) · EVERGREEN = Evergreen, "Break the rules" (outliers) ·
CORRELL = Correll, Bertini & Franconeri 2020 · STOKES = Stokes & Hearst 2022 ·
WILMER = Wilmer & Kerns 2022 · RAINCLOUD = Correll 2023 ("Teru Teru Bōzu: Defensive
Raincloud Plots") (see `papers.md` for the last four) · PADILLA = Padilla, Kay &
Hullman 2021 (uncertainty visualization) · KAY = Kay et al. 2016 (quantile dotplots) ·
LEX = Lex et al. 2014 (UpSet) · ROBERTS = Roberts 2007 (coordinated multiple views) ·
GLEICHER = Gleicher et al. 2011 (visual comparison) · SUN = Sun et al. 2022 (link
design across views) · WILLETT = Willett, Heer & Agrawala 2007 (scented widgets) ·
COCKBURN = Cockburn, Karlson & Bederson 2009.

Contents

1. PUR — purpose and value
2. EXP — expressiveness (data ↔ task)
3. EFF — effectiveness (data ↔ user), channels and perception
4. SCL — scales, axes, baselines
5. COL — color
6. TXT — titles, labels, annotation, text
7. CLT — clutter, data-ink, density, consistency
8. CMP — comparison, ordering, multiple views
9. IDM — idiom-specific (pointer to chart-types.md)
10. INT — interaction and animation
11. DAT — data honesty, uncertainty, bias and ethics
12. ACC — accessibility and medium

---

## 1. PUR — purpose and value

- **PUR-01** (JUDG, crit) The chart answers an identifiable question for an identifiable
  reader. If no task can be named, the chart is decoration. *MUNZNER ("help people carry
  out tasks more effectively"), STASKO (identify the purpose first).*
- **PUR-02** (JUDG, crit) If the task is a single calculation or a precisely known
  lookup, a number, a sentence or a small table beats the chart. Say so. *MUNZNER (no vis
  needed when a trusted automatic solution exists), STASKO ("if you can formulate
  precisely what you want, visualization is probably not the best approach").* Exception:
  the number must be compared to context the reader does not have (then a bullet chart
  or reference line is warranted).
- **PUR-03** (JUDG, major) Mode is identified (explanatory / analysis / exploratory)
  and the chart is judged against that mode's goals. Explanatory charts need a message;
  exploratory tools need overview → filter → details. *STASKO (presentation vs analysis),
  SCHWABISH, Tukey (EDA).*
- **PUR-04** (SEMI, major) Explanatory chart has a takeaway message, ideally in the
  title. Trigger ⚙: no title, or title is a variable/file name. *KONG (titles drive
  recall), STOKES TEXT-1/2, Knaflic "Storytelling with Data".* Exception:
  exploratory/reference dashboards with neutral descriptive titles.
- **PUR-05** (JUDG, major) Exploratory artifact supports Shneiderman's mantra: overview
  first (no details), zoom and filter, details on demand; plus relate, history, extract
  where relevant. *SHNEIDERMAN.*
- **PUR-06** (JUDG, major) The ten low-level tasks relevant to the purpose are fast
  (T component). Name which are immediate, which need work, which are impossible.
  *STASKO, AMAR.*
- **PUR-07** (JUDG, major) Insight: the chart shows something a summary table would
  hide (distribution, outliers, trend breaks, clusters, correlation). Re-encoding a
  handful of printed numbers is not insight. *ANSCOMBE, STASKO (I), North 2006.*
- **PUR-08** (JUDG, major) Essence: a five-second glance yields the intended gist, not
  a distractor. *STASKO (E), FEW (focus and emphasis).*
- **PUR-09** (JUDG, major) Confidence: source, date, n, aggregation, normalization and
  missing data are visible or stated. *STASKO (C), CAIRO (honesty).*
- **PUR-10** (JUDG, crit) Not visualization: random/irrelevant data charted; dataset
  "thrown" at a chart type; too much or irrelevant information encoded. *WILKE (ugly, bad,
  wrong), CAIRO.*
- **PUR-11** (JUDG, major) Appropriateness: space and reading time spent are proportional
  to the value delivered (information-rich AND informative). A large chart for 3–5
  numbers is low data density; a 50-line spaghetti chart for a trend is unreadable.
  *TUFTE (data density, "the greatest number of ideas in the shortest time with the least
  ink in the smallest space"), VAN WIJK (cost–value), MUNZNER (appropriateness).* A
  quick measure: data density = number of data entries shown / area of the graphic;
  compare it with a table of the same numbers.
- **PUR-12** (JUDG, major) Effective = novel or faster than the existing workflow. If
  the chart is neither, it has no value over what the reader already had. *MUNZNER.*
- **PUR-13** (JUDG, major) Audience fit: data literacy (can they read a PCP, a horizon
  graph, a log axis?), domain knowledge, device, context of use. *FEW, WARE (pattern
  learning), MUNZNER (domain situation).*
- **PUR-14** (JUDG, major) Uncertainty encoding not matched to the reader: intervals,
  gradients or ensembles shown to a lay audience with no sentence saying what they mean
  (readers may conclude the data is flawed, or read an interval as a hard limit); or
  uncertainty left out for experts who need it. Frequency framings (quantile dot plot,
  icon array, "3 in 10") read best for lay readers. *PADILLA, KAY, Hullman et al. 2019.*

## 2. EXP — expressiveness (data ↔ task)

- **EXP-01** (DET ⚙, crit) Nominal attribute encoded with an ordered channel
  (lightness, saturation, size, sequential colormap, ordered position) implies an order
  that does not exist. *MACKINLAY (expressiveness), MUNZNER (channel–attribute type
  match).* Exception: the order is meaningful and stated (e.g. sorted by value, then
  position order is the value, not the category).
- **EXP-02** (DET ⚙, crit) Ordered, quantitative or temporal attribute encoded with an
  unordered channel (categorical hue palette, shape) loses the order; years as `:N`
  with `category10`. *MACKINLAY, MUNZNER, BREWER (qualitative vs sequential).* Exception:
  a handful (≤3) of ordered levels with direct labels, or the order is carried by another
  channel (x position) and color is only for identification.
- **EXP-03** (DET ⚙, crit) Line/area connecting nominal categories implies continuity
  between unrelated items. *WILKE, CORRELL TRUNC-10, WARE (connectedness).* Exception:
  ordinal categories with a natural order (dose levels, Likert), labeled as such.
- **EXP-04** (SEMI ⚙, major) Bars (grouped bars especially) used for an ordered/temporal
  key where the task is trend: a line chart is typically better. *FEW, WILKE, SCHWABISH.*
  Exception: few discrete totals (sales per year) where the task is comparing amounts,
  not trend.
- **EXP-05** (DET ⚙, crit) Pie/donut/normalized stack whose parts do not sum to a
  meaningful whole: do not add to 100 %, mixed units, overlapping categories, totals
  that exceed 100 % because of rounding. *FEW, WILKE, CAIRO.*
- **EXP-06** (DET ⚙, crit) Stacked bars/areas/streamgraphs with negative values or
  non-additive quantities (temperatures, rates, percentages of different bases).
  *WILKE, Byron & Wattenberg 2008 (streamgraphs).*
- **EXP-07** (DET, crit) Geometry does not change as the data does: lie factor outside
  0.95–1.05. Causes: truncated bar axis, icons scaled in 2D/3D, perspective, unequal
  bar widths, radius-scaled circles. Measure with `lie_factor.py`. *TUFTE (lie factor;
  fuel-economy chart ≈ 14.8), CAIRO.*
- **EXP-08** (DET ⚙, crit) Bar, column, histogram, area or any length/area mark whose
  quantitative axis does not start at zero. *TUFTE, FEW, CORRELL TRUNC-1.* Exception:
  deviation/index bars from an explicit, drawn and labeled non-zero reference.
- **EXP-09** (DET ⚙, crit) Forced scale domain or `clip` that cuts data out of the
  plotting area; filters that silently drop rows; channels the library silently ignores
  for that mark (e.g. `shape` on a non-point mark in Vega-Lite). *CAIRO ("tell the whole
  story"), TUFTE (show the data).*
- **EXP-10** (JUDG, major) Decorative variation: color, size or shape varies without
  encoding data. Readers look for a meaning and find none. *TUFTE (chartjunk), FEW ("data
  informs variation"), BERTIN.*
- **EXP-11** (DET ⚙, crit) Dual y-axes: arbitrary alignment and scaling makes
  crossings and relative heights meaningless; spurious correlation. *FEW, Isenberg et
  al. 2011 (dual-scale charts), SCHWABISH.* Exception: if kept, color-match axes to
  series, both axes honest (zero or full range), different mark types, label units;
  still prefer juxtaposed charts, index chart or connected scatterplot.
- **EXP-12** (JUDG, crit) Choropleth of raw counts or totals where a rate/per-capita
  value is needed; large regions dominate; absolute vs relative mapping and class breaks
  change the story. *MUNZNER (choropleth idiom), Slocum et al. (thematic cartography),
  WILKE.*
- **EXP-13** (JUDG, crit) Cherry-picked window or subset (random months, a time range
  that hides the trend reversal, top-N only) or, conversely, extra data added to dilute
  the message. "Tell the whole story: omitting data may be misleading, but extra data can
  also be misleading." *CAIRO (How Charts Lie), TUFTE (context).*
- **EXP-14** (DET, crit) Missing values encoded as sentinel numbers (−9999) that enter
  scales and statistics; or missingness not shown at all. *WILKE, Kim & Gleicher (missing
  data vis).*
- **EXP-15** (SEMI ⚙, major) Histogram: bin edges not labeled, ticks not matching bins,
  gaps between bars, a single bin size tried. The same holds for the bandwidth of a
  density or violin: too wide merges modes, too narrow invents spikes and gaps; a
  library default is a choice nobody made (Sturges, Freedman–Diaconis, Silverman are
  starting points, not answers). Trigger ⚙: binned or density mark with no explicit bin
  or bandwidth parameter. *WILKE, FEW, RAINCLOUD RAIN-4.*
- **EXP-16** (DET ⚙, crit) Bar height encodes a mean/median of a distribution (bar of
  means) without raw points or dispersion. *WILMER MEANBAR-1/2/3, Weissgerber et al.
  2015.* Exception: bars of counts, sums or proportions.
- **EXP-17** (JUDG, major) Segmented color scales / choropleth class breaks (equal
  interval vs quantile vs natural breaks) chosen without stating them; different breaks
  yield different maps. *Slocum et al., BREWER.*
- **EXP-18** (JUDG, major) Animated or interpolated values that do not exist in the data
  (bar chart race tweening, smoothing presented as data). *Robertson et al. 2008
  (animated trend vis), WILKE.*
- **EXP-19** (JUDG, major) Aggregation level / temporal granularity hides the
  phenomenon (yearly bins merging two events; daily noise hiding the trend). Explore
  several granularities. *Aigner et al. 2011 (time-oriented data), WILKE.*
- **EXP-20** (DET ⚙, major) Log scale on bars (no zero, lengths meaningless) or log
  scale unlabeled. *WILKE, FEW.* Exception: dot/line charts with a clearly labeled log
  axis for a literate audience.
- **EXP-21** (SEMI ⚙, major) Random jitter: points displaced by unseeded random noise
  draw a different picture on every render, invent clusters and gaps, and can hide or
  fake a difference between groups. Trigger ⚙: a random offset on the categorical axis.
  Use a strip (ticks, hollow or translucent points at the true position), a beeswarm or
  Wilkinson dot plot (deterministic, but they move points too), or a seeded, stated
  offset. *RAINCLOUD RAIN-2, Few ("carpet bombing").* Exception: seeded jitter that is
  disclosed, with a shape layer (density) carrying the distribution.
- **EXP-22** (SEMI, major) Smooth density, violin or ridge drawn over discrete, rounded
  or heaped values (integers, Likert, ages in years), or extending beyond the possible
  range (negative counts, > 100 %): the curve shows values that cannot occur. Use a
  histogram or dot plot on the real support and clip the density. *RAINCLOUD RAIN-5,
  WILKE.*

## 3. EFF — effectiveness (data ↔ user)

- **EFF-01** (JUDG, crit) The most important attribute is on the most accurate channel.
  Quantitative: position (common scale) > position (unaligned) > length > angle/slope >
  area > volume > color luminance/saturation > hue. Nominal: position > hue > texture >
  connection > containment > shape. *MACKINLAY, CLEVELAND, HEER, MUNZNER.*
- **EFF-02** (SEMI ⚙, major) Angle or area used for a precise comparison task when
  length/position was available (pie, bubble, treemap, gauge, hearts). *CLEVELAND,
  STEVENS, FEW.* Exception: the task is part-to-whole with 2–3 parts and simple
  fractions (KOSARA), or hierarchy (treemap) where area is the only option.
- **EFF-03** (DET ⚙, crit) 3D for abstract data: perspective distortion, occlusion,
  depth judgments (exponent ≈ 0.67), tilted text, the nearest bar looks larger.
  *MUNZNER ("no unjustified 3D"), WARE, TUFTE.* Exception: inherently 3D spatial data
  that is still 3D after abstraction.
- **EFF-04** (DET, major) Proportional symbols scaled by radius/diameter instead of
  area; pictograms scaled in two dimensions. *STEVENS, FLANNERY, TUFTE (lie factor).*
- **EFF-05** (JUDG, major) Weber/JND: small differences between large values (980 vs
  1000) are invisible; add references (common baseline, adjacency, light gridlines,
  framing) or plot the difference / use a dot plot that zooms in. *WEBER, WARE, FEW.*
- **EFF-06** (SEMI ⚙, major) Comparison without a common baseline: stacked segments
  above the first, floating bars, unaligned small multiples. *CLEVELAND (position on
  common vs unaligned scales), WILKE.*
- **EFF-07** (JUDG, major) Items to be compared are far apart or interleaved; distances
  and positions matter (pie slices on opposite sides, countries separated by other
  series). *FEW, WARE (proximity).*
- **EFF-08** (DET ⚙, major) Highlight implemented as a conjunction (color AND shape)
  or with no single pop-out channel; or more distinct levels than a channel supports
  (hues > 7–8, shapes > 4, sizes > 4–5, textures > 3–4; heatmap color levels > ~10).
  *HEALEY, WARE (preattentive features, conjunction search), MUNZNER (discriminability).*
- **EFF-09** (JUDG, major) Salience does not match pertinence: saturated color, thick
  strokes or motion on unimportant marks; the important mark is grey. Pop-out is
  asymmetric and distractors weaken it. *WARE, FEW (focus and emphasis), HEALEY.*
- **EFF-10** (JUDG, major) Motion/flicker/animation that is not an alert or a controlled
  transition; it always captures attention. *WARE, HEALEY.* Exception: motion that
  encodes the data itself (flow direction and speed in a wind or current map,
  hypothetical outcome plots), with a legend for what speed means.
- **EFF-11** (SEMI ⚙, major) Working-memory load: more than 3–4 chunks to hold (three
  legends, two axes, 11 hue→category mappings, a color code to remember across panels).
  Trigger ⚙: legend entries > 7, legends > 2, dual axes. *WARE (visual working memory),
  HEALEY.*
- **EFF-12** (JUDG, major) Gestalt misuse: proximity grouping that contradicts the
  data (equal gaps between grouped bars), connectedness implying relations (lines
  between unrelated items), common region/frames that split related items, similarity
  (same color) across unrelated series. *WARE, PALMER, Wertheimer.*
- **EFF-13** (JUDG, major) Figure/ground inverted: background, frame, gridlines or
  decoration compete with data for salience. *WARE, TUFTE, FEW.*
- **EFF-14** (JUDG, minor) Glyph channels not perceptually separable when analytic
  reading is needed (width × height of rectangles are integral), or separable when a
  holistic impression was wanted. *GARNER, WARE.*
- **EFF-15** (JUDG, major) Layout not organized large → small with structure at each
  level; the reader's visual search has no entry point (principle of focal point).
  *WARE (visual search hierarchy).*
- **EFF-16** (SEMI ⚙, major) Overplotting/clutter: thousands of opaque points, more than
  about a dozen superimposed lines in one panel (fewer when hue alone tells them apart), hundreds of bars, labels colliding, dozens of stacked segments.
  Remedies: opacity (a bit), binning/density, filtering, small multiples, highlighting
  one series against grey. *WILKE, MUNZNER (reduce: filter, aggregate), FEW.*
- **EFF-17** (JUDG, major) Unfamiliar idiom for this audience without legend/explanation
  (PCP, horizon graph, streamgraph, Sankey, matrix); pattern learning takes time. *WARE
  (pattern learning), MUNZNER.*
- **EFF-18** (DET ⚙, major) Illegible marks or text: features < 0.1 mm at 30 cm;
  more than ~500 intervals across 216 mm; thin/tiny fonts; text rotated or tilted;
  labels overlapping. *WARE (acuity ≈ 50 cycles/degree), Krzywinski & Wong (Nature
  Methods "Points of View"), MUTH (fonts).*
- **EFF-19** (SEMI ⚙, major) Idiom used beyond its scalability (bars: hundreds max;
  grouped/stacked: ~12 secondary keys; pie: 3–5; SPLOM: ~12 attributes; PCP: ~12 axes,
  hundreds of items; slope chart: dozens; heatmap: ~10 color levels). See
  chart-types.md. *MUNZNER (idiom scalability).*
- **EFF-20** (JUDG, major) Eyes beat memory: comparisons that require remembering a
  previous view, frame, page or tab instead of side-by-side views. *MUNZNER ("eyes beat
  memory"), WARE (change blindness).*

## 4. SCL — scales, axes, baselines

- **SCL-01** (DET ⚙, crit) = EXP-08. Bars/areas/histograms from zero.
- **SCL-02** (SEMI ⚙, major) Dot plots, lines, scatterplots may start off zero, but
  the truncation must be visible (tick labels at the start, stated reference) and the
  exaggeration still happens, cues or not. Judge the axis range against the magnitude
  of a *meaningful* difference in the domain. *CORRELL TRUNC-2/4/6/7, WILKE (dot plots).*
- **SCL-03** (DET, major) Broken axis, gradient base or "torn" baseline does not earn
  back any severity; it only makes the truncation visible. *CORRELL TRUNC-3.*
- **SCL-04** (SEMI ⚙, major) Zero baseline that flattens meaningful variation when zero
  is arbitrary for the quantity (°C, index, dates, scores) — the opposite failure.
  Trigger ⚙: data span / axis span < 15 % on a line chart. *CORRELL TRUNC-5, TUFTE.*
- **SCL-05** (SEMI ⚙, major) Axis extended far beyond the data (data span / axis span <
  50 %) without reason: compresses the cloud, inflates perceived correlation, wastes
  space (scatterplot x from 0 when data start at 40). *CORRELL TRUNC-11, CLEVELAND
  (scale expansion and correlation), TUFTE.* Exception: shared scales across small
  multiples; headroom to an annotated limit.
- **SCL-06** (DET ⚙, major) Axis titles missing, raw variable names (`life_expect`,
  `count()`), or no units where units matter. *FEW, SCHWABISH, Krzywinski & Wong.*
- **SCL-07** (DET ⚙, major) Non-standard axes: time not left→right (years top→bottom in
  a bar chart), values not increasing upward, inverted axes without a reason, categorical
  axis where a quantitative one was expected. *WARE (conventions), CAIRO (the inverted
  "gun deaths" chart), FEW.*
- **SCL-08** (DET ⚙, major) Small multiples / facets with independent scales where
  comparison is the task (or shared scales where each panel's own variation is the task,
  stated). *TUFTE (small multiples), WILKE, MUNZNER (juxtapose, shared encoding).*
  Concatenated views get independent position scales by default in Vega-Lite: two
  panels of the same measure must share the scale explicitly. Exception: panels that
  show different measures or units, each axis titled with its unit.
- **SCL-09** (DET ⚙, crit) = EXP-11 dual axes.
- **SCL-10** (JUDG, minor) Index chart baseline choice and loss of absolute values not
  stated. *WILKE, Heer & Bostock & Ogievetsky 2010 (index charts).*
- **SCL-11** (DET ⚙, minor) Awkward truncated start (25 on a 0–100 scale) instead of a
  round anchor or a meaningful reference; too few gridlines for value reading when
  precision matters; heavy gridlines when it does not. *CORRELL TRUNC-8, FEW.*
- **SCL-12** (DET ⚙, minor) Rotated or vertical category labels: rotate the bars
  (horizontal bar chart), not the labels. *FEW, SCHWABISH, WILKE.*
- **SCL-13** (SEMI, minor) Aspect ratio: slopes squeezed in a narrow panel, or a wide
  panel flattening a trend; tiny panels in facets. *CLEVELAND (banking to 45°), WILKE.*
- **SCL-14** (DET ⚙, major) Tick labels do not match bin edges or data granularity
  (5-year ticks while annual events are discussed). *STOKES TEXT-12, FEW.*

## 5. COL — color

- **COL-01** (JUDG, major) Color is used for one of three purposes (distinguish
  categories, encode values, highlight) or not at all. Color without purpose is noise.
  *WARE, FEW, WILKE (color as a tool).*
- **COL-02** (DET ⚙, crit) Palette type matches data type: nominal → qualitative;
  ordered without neutral → sequential; ordered with a meaningful midpoint → diverging.
  Rainbow/jet/turbo/sinebow for quantities: no (no perceptual order, false boundaries).
  *BREWER, Borland & Taylor 2007 ("Rainbow color map (still) considered harmful"),
  WARE, Rogowitz & Treinish.*
- **COL-03** (DET ⚙, major) Redundant hue: a different color per bar/category when
  position already identifies it, forcing a legend that duplicates the axis. Use one
  neutral color plus one accent. *FEW, SCHWABISH, Knaflic.* Exception: the same colors
  identify the categories in other panels of a dashboard (consistency).
- **COL-04** (DET ⚙, major) Too many hues: > 7–8 categorical colors cannot be told
  apart or matched to a legend; palettes that wrap (category10 for 11 years). *WARE
  (≈ 6–12 distinguishable), HEALEY, MUNZNER.*
- **COL-05** (DET ⚙, crit) Not colorblind-safe: red–green, red–brown–green,
  purple–blue, pink–turquoise–grey pairs; a deuteranopia/protanopia simulation merges
  categories; no second cue (shape, texture, stroke, direct label). ≈ 8 % of men. *MUTH
  (Datawrapper colorblindness series), OKABE, BREWER (colorblind-safe schemes),
  Machado et al. 2009 (simulation).*
- **COL-06** (DET ⚙, major) Insufficient contrast: non-text elements < 3:1 against
  adjacent colors (WCAG 2.1), text < 4.5:1; similar luminance pairs; dark teal on dark
  blue; thin grey text. Simultaneous contrast between adjacent pure colors. *WCAG,
  WARE, Elavsky (Chartability).*
- **COL-07** (DET ⚙, major) Non-data elements (gridlines, frames, axes, backgrounds)
  drawn with high salience instead of light grey. *FEW, TUFTE (erase non-data ink).*
- **COL-08** (JUDG, major) The most important attribute is not readable in luminance
  alone ("get it right in black and white"); hue and saturation carry it. *WARE
  (luminance channel carries form), Krzywinski & Wong.*
- **COL-09** (JUDG, major) Inconsistent color meaning across charts of one
  dashboard/report, or violated conventions (blue cold / red hot; party colors; red =
  negative/alert used for neutral labels). *FEW (consistency), WARE (conventions),
  SCHWABISH.*
- **COL-10** (SEMI ⚙, major) Opacity/transparency: overlapping translucent fills create
  mixed colors (purple from red+blue) that read as a third category; elements with
  opacity 0; laciness lost. *WARE (transparency and laciness), WILKE.*
- **COL-11** (JUDG, minor) Field size: small marks and thin lines need stronger,
  more saturated colors than large areas; pastel palettes on 2-px lines vanish. *WARE,
  Stone (field-size effects).*
- **COL-12** (DET ⚙, major) Diverging palette whose midpoint is not a meaningful
  reference value (zero, mean, target), or a sequential palette where a reference
  matters. *BREWER, WILKE.*
- **COL-13** (JUDG, major) Stereotyped or loaded colors: baby pink/blue for genders,
  skin-tone or racial color coding, light→dark sequential palettes for demographic
  groups. *DO-NO-HARM.*
- **COL-14** (DET ⚙, minor) Palette from an undependable source; prefer ColorBrewer,
  Tableau, Viridis-family, Okabe-Ito. *BREWER, OKABE, Smith & van der Walt (viridis).*

## 6. TXT — titles, labels, annotation, text

- **TXT-01** (DET ⚙, major) No title, or title that is a variable/file name. Readers
  treat a missing title as a schema violation. *STOKES TEXT-1, KONG, BORKIN (title is the
  most recalled element).* Exception: one shared title over small multiples; a caption
  that does the title's job.
- **TXT-02** (JUDG, major) Explanatory title does not state the takeaway, or states a
  takeaway the data does not support (slanted title). *KONG, STOKES TEXT-2, Knaflic.*
- **TXT-03** (DET ⚙, major) Axes, legends or color scales unlabeled; no units;
  inconsistent names; legend in title case rather than sentence case. *FEW, SCHWABISH,
  Krzywinski & Wong.*
- **TXT-04** (SEMI ⚙, major) Legend far from the data when direct labeling was possible
  (label lines at their ends, label bars with values, label the highlighted item). If
  values are labeled, the axis may go. *FEW, SCHWABISH, TUFTE (multi-functioning
  elements), WARE (proximity).*
- **TXT-05** (JUDG, major) Notable features (spikes, dips, outliers, breaks, DST jumps,
  gaps) left unexplained in an explanatory chart. Readers want external context (why),
  not restated values. *STOKES TEXT-3, EVERGREEN ("the outlier needs to lie out"),
  Knaflic.*
- **TXT-06** (SEMI ⚙, minor) Annotations that restate the obvious ("Maximum", "peak",
  an arrow in the trend's direction) without a value, date or reason. *STOKES
  TEXT-4/5/8.*
- **TXT-07** (JUDG, major) Encodings not explained: non-standard color/shape/size use,
  derived variables, what counts as a "speaker" or an "achievement". *FEW, CAIRO,
  MUNZNER (explain the abstraction).*
- **TXT-08** (DET ⚙, major) No source, date, sample size or definition of the measure
  (C component). *CAIRO, STASKO (C), WILMER MEANBAR-6, TUFTE (documentation).*
- **TXT-09** (JUDG, minor) Over-labeling: every point labeled, every value printed and
  the axis kept, redundant increments. Minimum text that still gives context; but do not
  confuse informative annotation with clutter. *FEW, TUFTE, STOKES TEXT-7.*
- **TXT-10** (DET ⚙, major) Text illegible: tilted/vertical/3D text, thin fonts, text
  over busy backgrounds, low contrast, labels inside tiny circles. *MUTH (fonts), WARE,
  WCAG.*
- **TXT-11** (JUDG, minor) Fonts chosen against legibility: serif body text, non-lining
  or proportional numbers in tables, too narrow/wide, uppercase everywhere, bold
  everywhere. (Legibility, not taste.) *MUTH, Hoefler ("fonts for complex data"),
  Krzywinski & Wong.*
- **TXT-12** (JUDG, minor) Steering text: a single annotation that looks like
  cherry-picking, or narrative that "thinks for the reader"; separate observation from
  causal claim and attribute it. *STOKES TEXT-6/10.*
- **TXT-13** (JUDG, minor) Numbers shown with false or lost precision (39,419 vs
  40,000); numbers not right-aligned in tables. *FEW (table design), TUFTE.*
- **TXT-14** (JUDG, minor) The chart plus its text cannot be read as a coherent story
  (what, when, why); write the text-only version as a check. *STOKES TEXT-11, Lundgard
  & Satyanarayan 2022 (semantic levels of text).*

## 7. CLT — clutter, data-ink, density, consistency

- **CLT-01** (DET ⚙, major) Low data-ink ratio: heavy frames, backgrounds, gradients,
  textures, 3D effects, shadows, decorative images, speech bubbles. Erase non-data ink
  and redundant data ink, within reason. *TUFTE (data-ink ratio, chartjunk), FEW.*
  Exception: light gridlines, labels and annotations are useful non-data ink (Bateman
  et al. 2010 on memorable chartjunk does not make it readable).
- **CLT-02** (JUDG, major) Clutter: too many callouts, emphasized elements, colors,
  lines; no white space; the reader cannot find an entry point. *FEW, WARE, Knaflic
  (declutter).*
- **CLT-03** (JUDG, major) Density off the sweet spot: wasted space (sparse) or
  overwhelming (dense). Tufte: greatest number of useful ideas in the shortest time with
  the least ink in the smallest space. *TUFTE, MUNZNER (display capacity), Rosenholtz
  (clutter measures).*
- **CLT-04** (SEMI ⚙, minor) Redundancy without purpose: values printed AND axis AND
  increments; two encodings of the same attribute without a highlighting goal. *TUFTE
  (redundant data ink), FEW.* Exception: deliberate redundant coding to speed up a task
  (WARE) or to cover colorblindness.
- **CLT-05** (JUDG, major) Inconsistency: same category in different colors, different
  orders, different scales or different chart types across panels/pages without reason.
  *FEW, SCHWABISH, Qu & Hullman 2018 (consistency across multiples).*
- **CLT-06** (JUDG, minor) Misalignment: panels, axes, labels not aligned; related
  things far apart, unrelated things adjacent. *FEW, WARE (proximity), Knaflic.*
- **CLT-07** (SEMI ⚙, major) Legend with dozens of entries, or a legend that is the
  largest element of the figure. *FEW, WILKE.*
- **CLT-08** (JUDG, minor) Remove to improve: every element should survive the question
  "what is lost if I delete it?" *TUFTE, Knaflic.*

## 8. CMP — comparison, ordering, multiple views

- **CMP-01** (DET ⚙, major) Order not purposeful. Bars/dots sorted by value for value
  tasks, alphabetically only for name lookup, by time if temporal, by hierarchy/magnitude
  otherwise (Wurman's LATCH). Dot plots and lollipops must be sorted by value. Pies: from
  12 o'clock, largest first clockwise. *FEW, WILKE, SCHWABISH, Wurman 1989.*
- **CMP-02** (JUDG, major) Among correct encodings, the one with the lowest time, space
  and cognitive cost is not chosen (pie where sorted bars would do; table where a chart
  would reveal; chart where a table would do). *MUNZNER (effectiveness), FEW, CLEVELAND.*
- **CMP-03** (JUDG, major) Elements to compare are not adjacent, aligned or on a shared
  scale. *CLEVELAND, FEW, Gleicher et al. 2011 (visual comparison).*
- **CMP-04** (JUDG, crit) Whole story not told: missing context period, missing
  comparison group, missing baseline, missing denominator. *CAIRO, TUFTE (context).*
- **CMP-05** (SEMI ⚙, major) Multiple views: juxtaposed views with different scales,
  encodings or sizes; superposed layers that cannot be told apart or too many layers;
  small multiples not aligned, not equally sized, not logically arranged. *MUNZNER
  (facet: juxtapose, partition, superimpose), TUFTE (small multiples), Gleicher.*
- **CMP-06** (JUDG, major) Large/multivariate data without overview + detail or focus +
  context; or detail shown where an overview was needed. *SHNEIDERMAN, Cockburn, Karlson
  & Bederson 2009 (overview+detail, zooming, focus+context), MUNZNER.*
- **CMP-07** (JUDG, major) Partitioning for small multiples uses the wrong attribute or
  order, hiding the pattern that another split would reveal (trellis ordering). *Becker,
  Cleveland & Shyu 1996 (trellis), MUNZNER.*
- **CMP-08** (JUDG, major) Animation or sequential pages used where side-by-side
  comparison was needed (eyes beat memory; change blindness). *MUNZNER, Robertson et al.
  2008, WARE.*
- **CMP-09** (SEMI ⚙, major) Multiform views (the same items in different encodings:
  a map and a bar chart, a scatterplot and a histogram) with no linked highlighting:
  the reader cannot find an item of one view in the other. Trigger ⚙: concatenated
  views with different marks over the same data and no selection shared between them.
  *MUNZNER (multiform needs linking), ROBERTS, Becker & Cleveland 1987.* Exception:
  static media, where shared order, color and direct labels must do the linking.
- **CMP-10** (SEMI ⚙, major) Too many superimposed layers: more than two layers of
  filled area marks (three with care), or layers whose channel ranges overlap so
  foreground and background cannot be told apart. Lines stand about a dozen; many
  layers work only when each has few marks. *MUNZNER (superimpose), WARE (layering
  and transparency).*
- **CMP-11** (JUDG, major) Views that share neither data nor encoding nor a selection
  are placed together as one dashboard: no comparison is enabled, the reader pays the
  space and attention for unrelated charts. *MUNZNER (data shared × encoding shared),
  FEW (dashboard design).*
- **CMP-12** (JUDG, major) Two states, periods or alternatives are shown as two charts
  to be subtracted by eye when the task is the difference: encode the difference
  explicitly (difference bars, a diverging map of the change, change arrows), alone or
  beside the originals. *GLEICHER (juxtapose, superimpose, explicit encoding).*
- **CMP-13** (JUDG, minor) Space trade-off not considered: juxtaposed views cost about
  twice the area and shrink each view below legibility where one view changed by
  interaction, a popup or a superimposed layer would do; or the opposite, a single
  view that forces the reader to remember the previous state. *MUNZNER, COCKBURN.*

## 9. IDM — idiom-specific

See `chart-types.md`. Headline anti-patterns the inspectors flag ⚙:

- **IDM-PIE** (crit) > 5 slices, unsorted, 3D/exploded, not starting at 12, values not
  a whole, several pies to compare. *FEW, KOSARA, WILKE.*
- **IDM-STACK** (major) many categories, comparison within/among groups needed,
  non-additive, only bottom segment readable. *WILKE, CLEVELAND.*
- **IDM-LINE** (crit) nominal x; (major) more than about a dozen superimposed lines, or
  more than ~7 told apart only by hue with neither direct labels nor a highlight-on-grey
  design; missing points interpolated. *WILKE, FEW, MUNZNER (superimposed line charts).*
- **IDM-BAR** (crit) truncated; (major) hundreds of bars, time on a categorical axis,
  unsorted, rainbow. *TUFTE, FEW, SCHWABISH.*
- **IDM-SCATTER** (major) overplotting; axis from 0 far from data; size by radius;
  > 8 hues; no trend/annotation when correlation is the task. *WILKE, CLEVELAND.*
- **IDM-HEATMAP** (major) categorical palette for values; > 10 levels; unordered rows/
  columns; cells too small. *BERTIN (reorderable matrix), MUNZNER, WILKE.*
- **IDM-MAP** (crit) raw counts choropleth; (major) rainbow; too many classes; symbols
  overlapping; projection unsuited. *Slocum et al., BREWER, MUNZNER.*
- **IDM-3D** (crit) 3D bars/pies/surfaces for abstract data. *MUNZNER, TUFTE.*
- **IDM-WORDCLOUD** (major) area ∝ word length; rotated words; random color. *Viégas &
  Wattenberg (Wordle), Harris ("word clouds considered harmful").*
- **IDM-RADAR/GAUGE** (major) angle/radius for values; use bars/bullets. *FEW (bullet
  graphs), WILKE.*
- **IDM-DUAL** (crit) dual axes. *FEW, Isenberg et al. 2011.*
- **IDM-TABLE** (minor) vertical lines, lines between rows, misaligned numbers; but
  remember a table may be the right answer (precision, heterogeneity, compactness).
  *FEW (Show Me the Numbers), TUFTE.*
- **IDM-VENN** (major) Venn/Euler diagram with more than 3 sets (n sets need 2ⁿ
  regions), or region areas that are not proportional while the reader is asked to
  compare sizes: use intersection bars over a membership matrix (UpSet). *LEX,
  Alsallakh et al. 2016 (set visualization).*
- **IDM-SANKEY** (major) too many nodes or links to follow; node order that maximizes
  crossings; weak flows not grouped into "other"; widths not proportional to the flow;
  a flow diagram where a table or stacked bar of the same two keys would do. *Riehmann
  et al. 2005, MUNZNER.*
- **IDM-RAINCLOUD** (major) raincloud made of a default density, randomly jittered
  points and an undefined box plot: each part fails silently and none covers the
  others. Prefer density (or histogram for discrete data) + strip at true positions +
  median with a labeled quantile interval. *RAINCLOUD RAIN-1, Allen et al. 2019.*

## 10. INT — interaction and animation

- **INT-01** (JUDG, major) Interaction limited to tooltips when the data size or
  dimensionality needs filtering, zooming, reconfiguring (sort/reorder), encoding
  changes or linked views. *STASKO (interaction as the power source), YI (seven
  intents), MUNZNER (manipulate, facet, reduce).*
- **INT-02** (JUDG, major) Default state does not answer the main question; the reader
  must interact before seeing anything useful; too many interactions to solve a task.
  *SHNEIDERMAN (overview first), Nielsen (defaults), STASKO (T).*
- **INT-03** (JUDG, major) The key insight only appears on hover: the overview fails
  (T, E). *STASKO, SHNEIDERMAN.*
- **INT-04** (JUDG, major) Views not coordinated (selection in one view not reflected in
  others) where comparison across views is the task; inconsistent highlight color.
  *Becker & Cleveland 1987 (brushing), Roberts 2007 (coordinated multiple views),
  MUNZNER.*
- **INT-05** (JUDG, minor) No history/undo or extract where exploration is multi-step.
  *SHNEIDERMAN (history, extract), Heer, Mackinlay et al. 2008 (graphical histories).*
- **INT-06** (DET, major) Latency: feedback > 0.1 s without cue; filtering > 100 ms;
  > 1 s without progress indication; > 10 s. *NIELSEN, SHNEIDERMAN (dynamic queries),
  Liu & Heer 2014 (latency and exploration).*
- **INT-07** (JUDG, major) Animation without play/pause/scrub, with many simultaneous
  changes, or used for comparison across time instead of small multiples; rescaling
  axes mid-animation. *Robertson et al. 2008, Heer & Robertson 2007 (animated
  transitions), Tversky, Morrison & Bétrancourt 2002.*
- **INT-08** (JUDG, minor) Affordances unclear: interactive elements do not look
  interactive; no instructions for non-obvious interactions. *Norman (affordances),
  Boy et al. 2016 (suggested interactivity).*
- **INT-09** (DET ⚙, major) A selection (brush, click, legend selection) is declared
  but drives nothing: no condition, filter or scale domain in any view reads it; or it
  only changes the view it was made in while other views show the same items. *ROBERTS,
  MUNZNER (linked highlighting).* Exception: a pan/zoom selection bound to scales.
- **INT-10** (SEMI ⚙, minor) Linked highlighting uses a different highlight color (or
  a different meaning for the same color) in different views. One highlight color with
  one meaning in all views. *ROBERTS, Becker & Cleveland 1987, WARE (consistency).*
- **INT-11** (JUDG, major) Filtering used where highlighting was needed: the selected
  subset is shown alone, so its relation to the rest (share, rank, position in the
  distribution) is lost; or highlighting used where the context only clutters. State
  which the task needs. *MUNZNER (reduce vs manipulate), Yi (filter vs select).*
- **INT-12** (JUDG, minor) Filter widgets without scent: sliders, checkboxes and menus
  that do not show how much data each choice holds, so the reader filters blind and
  lands on empty views. *WILLETT, Shneiderman (dynamic queries).*
- **INT-13** (JUDG, minor) Linked navigation missing where views share an axis: zoom or
  pan in one view leaves its sibling on another range, so positions no longer
  correspond. *ROBERTS, MUNZNER (shared navigation).*

## 11. DAT — data honesty, uncertainty, bias and ethics

- **DAT-01** (JUDG, crit) Data not checked: wrong units (1,026 billion speakers),
  duplicates, stale data, undefined categories (N/A, "undefined" in the final chart),
  totals that do not add up. *CAIRO (How Charts Lie), TUFTE (integrity).*
- **DAT-02** (JUDG, crit) Normalization missing or wrong: totals where rates are needed
  (population, area, base), percentages of different bases compared. *CAIRO, Slocum et
  al., WILKE.*
- **DAT-03** (JUDG, major) Uncertainty hidden where it matters (intervals, n, missing
  data), or shown without definition (unlabeled error bars; SE bars understating
  variation). *WILMER MEANBAR-4/6, Hullman et al. 2019 (uncertainty vis), Correll &
  Gleicher 2014 (error bars considered harmful).*
- **DAT-04** (JUDG, major) Selection/survivorship bias in the data shown (only returned
  planes; only top-N; only items under a threshold). *Wald 1943 (survivorship), CAIRO.*
- **DAT-05** (JUDG, major) Deficit framing: between-group differences emphasized while
  within-group variation and context are hidden, inviting stereotyping and victim
  blaming; the fix is more data (distributions) and context, not less. *HOLDER,
  DO-NO-HARM, WILMER.*
- **DAT-06** (JUDG, major) Equity language and labels: not people-first; labels copied
  from the data in a biased order; missing groups unmentioned; "Other" as a catch-all
  without explanation; stereotyped icons. *DO-NO-HARM.*
- **DAT-07** (JUDG, minor) Decision support that invites the attraction (decoy) effect
  without highlighting non-dominated options. *DIMARA.*
- **DAT-08** (JUDG, major) Privacy: personal data mapped or named without need (the
  2012 Journal News gun-permit map). *CAIRO, DO-NO-HARM.*
- **DAT-09** (JUDG, major) Content not de-politicized: loaded title, selective context,
  persuasive framing presented as neutral. *CAIRO, STOKES TEXT-10, Pandey et al. 2014
  (persuasive power of vis).* Includes altered official graphics presented as the
  original: say who drew what, and when.
- **DAT-10** (SEMI ⚙, minor) Box plot whose whisker rule is not stated (min–max, 1.5 ×
  IQR, percentiles): the same data draws different boxes, and readers cannot tell an
  outlier from an extreme. Trigger ⚙: box-plot mark with no stated extent and no note.
  *RAINCLOUD RAIN-6, WILMER MEANBAR-4, Wickham & Stryjewski 2011 (40 years of boxplots).*
- **DAT-11** (JUDG, crit) Uncertainty envelope that reads as something else: a forecast
  cone taken for the size of the storm or the edge of the danger zone, an interval band
  taken for the range of possible values, a widening band taken for growth. Say in the
  graphic what the envelope is (and is not) and that outcomes fall outside it. *PADILLA,
  Ruginski et al. 2016 (hurricane cone), Broad et al. 2007.*
- **DAT-12** (JUDG, major) Ensemble / spaghetti plot whose members are not comparable:
  different model types mixed, stale runs beside current ones, members unlabeled, one
  outlying run given the same weight as the consensus. *PADILLA, Liu et al. 2017.*
- **DAT-13** (JUDG, major) The interval or summary drawn does not match the analysis
  reported (a box plot beside a t-test, an SD bar beside a credible interval) or
  invites inference by eye that the test does not support (overlapping CIs read as "no
  difference"). Draw what was computed; otherwise a plain mean or median marker.
  *RAINCLOUD RAIN-7, Cumming & Finch 2005 (inference by eye), Belia et al. 2005.*
- **DAT-14** (JUDG, major) Renormalization: in filtered, animated or updating views the
  axis, color domain, bins or density rescale to the current subset, so the same
  height or color means different values from one state to the next, or sibling
  components rebin out of step. Fix domains and bins across states, or say that they
  change. *RAINCLOUD RAIN-8, Heer & Robertson 2007.*

## 12. ACC — accessibility and medium

- **ACC-01** (DET ⚙, crit) = COL-05 colorblind safety; needs a second cue. *MUTH,
  OKABE.*
- **ACC-02** (DET ⚙, major) = COL-06 contrast; also glare, low-quality monitors,
  elderly readers (half of people over 50 have some low-vision condition). *WCAG,
  Elavsky (Chartability).*
- **ACC-03** (JUDG, major) Device mismatch: tiny text for a projector; dashboard that
  needs several screens of scrolling; hover-only interactions on touch devices.
  *FEW (dashboard design), Nielsen (mobile), SCHWABISH.*
- **ACC-04** (JUDG, minor) Not printable / not readable in grayscale when the medium
  may be print. *WARE (luminance), Krzywinski & Wong.*
- **ACC-05** (DET ⚙, major) Minimum sizes: text ≥ ~8–9 pt on screen (≈ 12 px), marks ≥
  2–3 px, lines ≥ 1 px with contrast; nothing below 0.1 mm at 30 cm. *WARE (acuity),
  WCAG, Krzywinski & Wong.*
- **ACC-06** (JUDG, minor) No text alternative (caption/alt-text) for a chart that
  carries the key message. *STOKES TEXT-11, Lundgard & Satyanarayan 2022, WCAG.*
