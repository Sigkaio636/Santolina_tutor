# Chart types: what each idiom is for, where it breaks, what to use instead

Vocabulary (Munzner 2014): **key** = independent attribute (category, time,
identifier); **value** = dependent measured attribute; **mark** = point, line, area;
**channel** = position, length, angle, area, color (hue, luminance, saturation), shape,
size, texture, connection, containment. Scalability limits are Munzner's order-of-magnitude
figures; treat them as rules of thumb, not thresholds.

Use this file after identifying the idiom. For each, check: does the data shape match?
Is the task one the idiom supports? Is it within scale? Then apply the idiom's
must/must-not list and consider the alternative.

## Quantities

### Bar chart (1 key, 1 value; mark: line; channel: length on a common baseline)
- Tasks: compare, look up; extremum and sort are immediate if sorted. Scales to
  hundreds (readable: dozens).
- Must: start at zero; horizontal bars for long labels (rotate bars, not labels);
  order by value (value search) or alphabetically (label search); neutral single color
  plus one accent; light gridlines only if precision matters.
- Must not: hundreds of bars; time as the key when the task is trend (use a line);
  different hue per bar with a legend; log scale; 3D; means of a distribution without
  the data (see Wilmer & Kerns).
- Alternatives: dot plot / lollipop (small differences, no zero needed), line (time),
  table (few values with precision).

### Grouped / paired bar chart (2 keys, 1 value; length + hue + spatial region)
- Tasks: compare within a group (easy), among groups (hard), look up. ≈ one dozen
  secondary keys.
- Must: zero baseline, consistent hue per secondary key, group gap larger than bar gap
  (proximity).
- Must not: one key is time (use lines or small multiples); more than ~5 bars per group.

### Stacked bar chart (2 keys, 1 value; length + hue)
- Tasks: totals per group (easy), composition (rough); comparing segments within or
  across groups is hard: only the bottom segment has a common baseline.
- Must: additive quantities whose total makes sense; few categories (≤ 5–6); sorted
  and consistent segment order; zero baseline.
- Must not: non-additive values (temperatures, rates), negative values, dozens of
  categories (flight delays by destination: unreadable).
- Alternatives: grouped bars, small multiples, line chart of each category, normalized
  stacked bars (if proportions), heatmap (many categories).

### Normalized (100 %) stacked bar
- Works with two categories (one aligned at each end) and a 50 % reference line
  (Disney dialogue chart). With many categories only the two ends are comparable.

### Dot plot / lollipop (1 key, 1 value; mark: point; channel: position)
- Does not need a zero baseline; suitable for small differences that bars would hide.
- Must: ordered by value ("the opposite makes the chart difficult to read"); labeled
  axis if values matter; lollipop stems add little.

### Radar / spider chart
- Angle and radius encode values; polygons' areas mislead; axis order arbitrary; does
  not scale. Prefer small bars, dot plot or parallel coordinates. Acceptable only for a
  holistic "shape" impression of 1–3 profiles.

### Gauge vs bullet chart
- Gauge: angle, wastes space, usually needs the number anyway. Bullet: length against
  a background reference, space efficient, multiple references. Prefer bullet.

## Distributions

### Histogram (binned continuous variable; bar area ∝ frequency)
- Must: contiguous bars (no gaps), bin edges readable, several bin sizes explored
  (different distributions can appear), units. Count axis from zero. Label the axis as
  "Number of X", not "Count of Records".
- Must not: be confused with a bar chart of categories; one arbitrary bin width;
  stacked by dozens of categories.

### Box plot
- Shows median, quartiles, whiskers, outliers; good for several distributions side by
  side. Hides multimodality and sample size. State n; pair with points or a violin when
  shape matters.

### Box plot whiskers
- Whiskers mean min–max, 1.5 × IQR or percentiles depending on the tool: state which
  (DAT-10). A box's area draws the eye away from the whiskers; the same five numbers
  fit very different distributions.

### Violin / strip / beeswarm / Wilkinson dot plot / ridge
- Strip: every value at its true position (ticks, hollow or translucent points);
  overplots, which is tolerable when a shape layer carries the density. Random jitter
  spreads points but draws a different picture each render and invents structure
  (EXP-21): prefer a beeswarm or Wilkinson dot plot (deterministic, countable, but
  points leave their true position and packing breaks at large n), or a seeded offset.
- Violin / density: shape depends on the bandwidth (EXP-15), suggests values outside
  the data range, hides n; mirroring adds nothing (a half violin frees room for the
  points). Not for discrete or rounded data (EXP-22). Ridge plots allow many
  distributions, no accurate values.
- Use these, not bars of means, to compare groups on a measured variable.

### Raincloud (shape + raw values + summary)
- Three parts: a "cloud" (density, histogram, quantile dot plot), "rain" (the
  observations) and "lightning" (a summary with an interval). The usual recipe, default
  density + randomly jittered points + box plot, is the weak one (IDM-RAINCLOUD): each
  part fails silently (bandwidth, random positions, undefined whiskers).
- Must: parts whose weaknesses differ (RAIN-1), e.g. density or histogram + strip at
  true positions + median with a labeled quantile interval; bandwidth or bins stated;
  the summary matches the analysis reported (DAT-13); n per group.
- Must not: beeswarm + violin (both draw the same shape); a quantile dot plot beside
  raw-data dots (which dots are data?); use it where one value per item is all there is.

### Uncertainty encodings
- Intervals (error bars, box plots, line ranges): compact; read as hard limits and hide
  the shape; must say what they are (SD, SE, CI, credible, prediction).
- Distributions (violin, gradient plot, density + interval): show that values near the
  center are likelier; a gradient has no sharp edge to misread.
- Frequency framings (quantile dot plot, icon array, hypothetical outcome plots,
  ensemble / spaghetti plot): countable outcomes, best for lay readers and decisions;
  ensembles need comparable, current, labeled members (DAT-12).
- Maps and forecasts: a cone or band is not the size of the phenomenon nor a safety
  boundary (DAT-11); uncertainty grows with lead time, say so.
- Always: a sentence telling the reader what the uncertainty mark means (PUR-14).

## Proportions

### Pie / donut (1 key, 1 value; mark: area; channel: angle)
- Task: part-to-whole for 2–5 parts, especially simple fractions (¼, ½, ¾).
- Must: parts sum to 100 %; start at 12 o'clock; sort large → small clockwise; direct
  labels; few categories.
- Must not: > 5 slices; similar slices; comparing between pies; 3D, exploded,
  perspective, tilted (whistle); two alternating colors with leader lines; non-additive
  data. Donuts are about as good as pies (Kosara 2016).
- Alternative: sorted bar chart (comparison), normalized stacked bar (two parts),
  waffle (counts of people).

### Polar area / stacked polar
- Radius encodes value (Nightingale); stacked polar has the stacked-bar problems or
  worse. Rarely the best choice.

### Treemap (hierarchy; area + containment + color)
- Good for part-to-whole in large hierarchies, space efficient. Area comparisons are
  imprecise; depth hard to read; thin rectangles (use squarified); labels in small cells
  unreadable. Sunburst: angle + depth, labels hard, deep slices exaggerated. Circle
  packing: shows grouping, wastes space, poor value comparison.

## Relationships

### Scatterplot (2 values, 0 keys; point; position)
- Tasks: correlation, clusters, outliers, distribution shape. Axis need not include
  zero; include the data range with modest margin (not from 0 when data start at 40;
  not expanded far beyond the data, which inflates perceived correlation).
- Watch: overplotting (opacity a bit, smaller marks, binning, density, sampling),
  trend line and annotation if correlation is the message, units on both axes.

### Bubble chart (scatter + size [+ color])
- Size by area (never radius); size legend; small bubbles vanish, big ones occlude;
  color for ≤ 7 categories or an ordered palette for a quantity; opacity to alleviate
  overlap, only a bit.

### Scatterplot matrix (SPLOM)
- All pairwise correlations; ≈ one dozen attributes, dozens to hundreds of items.
  Quadratic space, repeated upper/lower triangles (use one for correlation values),
  empty diagonal (use for names or histograms). Needs brushing & linking to be useful.

### Heat map (2 keys, 1 value; area; color)
- Tasks: clusters, patterns, outliers, overview of large tables. ~1 M cells, hundreds
  of categories, but only ~10 distinguishable color levels; exact values need tooltips.
- Must: ordered (sequential/diverging) colormap, meaningful row/column order
  (reorderable matrix: sort or cluster), cell size readable, legend with units, consistent
  scale across heatmaps compared.
- Must not: categorical palette for values; rainbow; alphabetical order hiding
  structure; cells too small to see.

### Parallel coordinates (several keys/values; polylines across parallel axes)
- Tasks: many dimensions at once, correlation between adjacent axes (parallel =
  positive, crossing = negative), clusters, outliers; with brushing.
- Limits: ~12 axes, hundreds of items (thousands = hairball; use opacity, bundling,
  density). Only adjacent axes compare; axis order matters; per-axis scales mislead;
  needs training.

### Slope chart (two time points per item; connected points)
- Dozens of items; highlight the anomaly with color + thickness, grey the rest; direct
  labels at both ends; wide enough panel so slopes are readable; same units.

### Connected scatterplot / dumbbell / range plot
- Show change between two states per item; connectedness makes the change obvious.
  Range plot = dot plot with two values.

## Time series

### Line chart (ordered key, value; points connected; position)
- Tasks: trend, rate of change, seasonality, peaks, comparing a few series. Zero
  baseline not required, but the range must be chosen for the meaningful effect size
  and made visible (Correll). Time left→right.
- Must: up to about a dozen superimposed lines, and beyond ~7 only with direct labels
  or a few highlighted against grey (hue alone separates ~7); direct labels at line ends;
  gaps for missing data rather than interpolation; annotate events (DST, policy).
- Must not: nominal x; dozens of similar hues; dual y-axes.

### Area / stacked area / streamgraph
- Stacked area has the stacked-bar problems (only the bottom layer has a baseline).
  Streamgraph: wiggling baseline, emphasizes continuity and rise/fall of many
  categories; no negative values, no non-additive data, no exact reading, hard to read
  at curve tops; scales to hundreds of time steps and dozens of categories.
- Alternatives: small multiples of lines/areas with shared axes; horizon graphs for many
  series in little space (need learning).

### Index chart
- Percentage change from a chosen base point; good for relative changes across
  series of different magnitude; loses absolute values; the base choice changes the
  picture. State the base.

### Waterfall
- Cumulative contributions to a net change; floating bars; increases/decreases
  colored consistently; totals anchored at zero; few steps.

### Small multiples (any idiom repeated over a partition)
- Must: same axes/scales, same encoding, equal size, aligned, logical order of panels,
  shared legend. Eyes beat memory: prefer over animation for comparison.
- Must not: independent scales without saying so; too many tiny panels; inconsistent
  colors across panels.

### Calendar heatmap, punch card
- Two keys (month × weekday) with size or color; size by area hard to compare; a
  heatmap is the usual alternative.

### Horizon graph
- Area chart folded into bands and mirrored for negatives; very space-efficient for
  many series; needs learning; no exact values.

### Sparkline
- A word-sized line with no axes, inside a table, a sentence or a dashboard tile: shape
  and recent direction only. Needs a consistent scale rule across rows (shared, or
  stated as per-row), an end-point value, and a marked reference (min/max or normal
  band) to be more than decoration.

### Difference view (two states compared)
- When the task is the change, draw the change: bars or a diverging heatmap of B − A,
  alone or beside the two originals; "current + faded previous" works for one step.
  Two full charts to subtract by eye is CMP-12. State the direction of the difference.

### Animation / bar chart race
- Engaging; shows rank changes; but change blindness, no comparison across frames,
  interpolated values, rescaling axes, no control of pace unless controls exist. For
  analysis use line charts, bump charts, small multiples, heatmaps.

## Geospatial

### Choropleth (ordinal/quantitative area data; color per region)
- Must: normalized data (rates, per capita, density) unless the task is explicitly about
  totals; sequential (or diverging) segmented colormap with ~5–7 classes; class-break
  method stated; legend with units; projection suited to the task.
- Must not: raw counts (large regions dominate; "land doesn't vote"); rainbow; too many
  classes; hues for quantities; low contrast on dark basemaps.
- Alternatives: graduated symbol map (symbol size independent of area), cartogram
  (contiguous, Dorling, tile), dot density map.

### Graduated / proportional symbol map
- Symbol area ∝ value (Flannery compensation optional); overlap and clutter; symbols
  hide boundaries; legend of sizes.

### Dot map / pixel map
- One dot per phenomenon (or per n); overplotting in dense areas, emptiness in sparse
  ones; pixel maps reposition points to avoid overlap.

### Flow / line maps, network maps
- Width/color for flow; bundling to reduce clutter; direction cues.

### Arrow (shift) map and spike map
- Arrow map: one arrow per region, direction and length = change between two periods,
  color = sign or category. Shows where and how much things moved; arrows overlap in
  dense areas; needs a legend for direction and length, and a rate, not a raw count.
- Spike map: thin spikes anchored at locations, height = value. Length is read better
  than circle area and spikes overlap less than bubbles; tall spikes cross their
  neighbours and hide what is behind; height legend required.

### Cartogram, tile and hex maps
- Each unit drawn with a size set by the data (population, seats) or with equal tiles
  arranged by rough geography: removes the land-area bias of a choropleth. Shape and
  adjacency are lost, so label the tiles; non-contiguous and Dorling variants keep
  position better than contiguous ones.

### Vector-field, streamline and isarithmic maps
- Continuous fields (wind, currents, temperature): streamlines or arrows for direction
  and speed, contours or filled isolines for a scalar. Animated streamlines are a case
  where motion is the data (EFF-10 exception); they need a speed legend, a timestamp
  and the source of the forecast.

## Hierarchies and networks

- **Node-link tree**: topology and depth clear; space hungry for wide trees; radial
  variant for compactness. **Indented tree**: rapid label scanning, poor multiscale.
  **Treemap / sunburst / circle packing**: size, not structure.
- **Node-link graph**: familiar; crossings and occlusion in dense graphs; force-directed
  layouts are non-deterministic and lengths are meaningless; circular layouts tidy but
  long edges. **Adjacency matrix**: no crossings, scales to dense graphs, clusters as
  blocks when well ordered; paths hard; needs learning; order is everything (finding
  a good order, seriation, is itself a hard problem: say which order was used). Color
  cells rather than print numbers.
- **Circular layout / chord**: tidy, nodes can be ordered and an outer ring can carry
  extra attributes; but edges are long and collinear, and the regular shape hides
  clusters. **Arc diagram**: nodes on one line, arcs for links; the node order decides
  what shows; room for attributes beside the nodes.
- **Dendrogram**: a tree with all leaves on one level and branch height = merge
  distance (clustering); read cut heights, not left–right order, which is arbitrary.
  **Icicle / adjacency (partition) diagram**: space-filling tree where node length
  carries a value and depth is a row; easier to compare than a sunburst.
- **Indented tree** also carries attribute columns beside each row (a file explorer);
  it costs a lot of vertical space.
- **Sankey / alluvial** (IDM-SANKEY): width ∝ flow; shows the dominant flows. Order
  nodes to minimize crossings, group weak flows into "other", keep few stages; many
  thin links become unreadable.
- **Venn / Euler vs UpSet** (IDM-VENN): n sets need 2ⁿ regions; beyond 3 sets (4 at
  most) regions become unreadable and areas cannot be made proportional. UpSet: bars
  of intersection size over a membership matrix, sortable, with room for attributes
  per intersection.
- Labels: label only regions or on demand; the hairball with 2,000 labels is not a
  visualization.

## Text

- **Word cloud**: font size ∝ frequency, but area depends on word length; rotated
  words unreadable; position and color meaningless; duplicates. Use a sorted bar chart
  of the top terms for comparison; the cloud is at most an overview teaser.
- Word tree, arc diagram, chromogram, themescapes: each needs an explanation and a
  task (context of a term, repetition, long sequences, topic strength).

## Glyphs and multivariate

- Glyphs (stars, whiskers, Chernoff faces) map attributes to properties of one shape;
  integral vs separable dimensions; faces have high interpretation variance; need
  learning. Prefer small multiples, PCP, SPLOM or a table for analytic reading.

## Tables and text

Tables may beat a chart when: precision matters (39,419 vs 40,000), the data is
heterogeneous (numbers + categories + text), there are few values, or compactness is
required. Design: no vertical lines, horizontal lines only under the header and around
the table, text left-aligned, numbers right-aligned with equal decimals, headers aligned
with data, light shading for groups. A sentence may beat both for one or two numbers.

## Dual axes (any idiom)

Arbitrary scale alignment makes crossings, overlaps and relative heights meaningless;
gridlines fit only one axis; readers compare heights directly. If kept: color-match each
axis to its series, honest ranges on both, different mark types, units on both. Prefer
two aligned juxtaposed charts, an index chart (state the base) or a connected
scatterplot.
