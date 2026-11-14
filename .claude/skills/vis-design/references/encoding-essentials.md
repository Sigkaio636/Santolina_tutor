# Encoding essentials (standalone excerpt)

The minimum perception and good-practice knowledge needed to design and validate an
encoding when the sibling skill `vis-value-critique` is not installed. When it is, read
its `references/perception.md` and `references/rules-catalog.md` for the full versions;
the rule IDs below are the same ones, so seeds and design documents cite one vocabulary.

## Channel effectiveness (Mackinlay 1986; Cleveland & McGill 1984)

- Quantitative: position on a common scale > position on unaligned scales > length >
  angle/slope > area > volume > luminance/saturation > hue.
- Ordinal: position > luminance > saturation > hue > texture > connection > containment.
- Nominal: position > hue > texture > connection > containment > shape.
- Put the attribute the main task depends on in the highest-ranked channel that fits its
  type (expressiveness: ordered data on ordered channels, nominal on nominal channels).
- Area is underestimated (Stevens exponent ≈ 0.7) and volume more so (≈ 0.6); size by
  area, never by radius; no 3D for abstract data.

## Baselines and scales

- Length marks (bars, areas, histograms) start at zero; position marks (dots, lines,
  scatter) may not, but a truncated axis still exaggerates differences for every mark
  type, cues or not (Correll et al. 2020): choose the range for the meaningful effect
  size and make the baseline visible.
- A zero baseline that flattens meaningful variation (temperatures, indices) is the
  opposite failure. Axes extended far beyond the data compress the cloud.
- Small multiples share scales unless each panel's own variation is the task, and then
  the document says so; panels in different units keep their own scale, each axis titled
  with its unit. Dual y-axes are discouraged (EXP-11): prefer two aligned panels or an
  index chart; the only tolerated cases are two units of the same quantity (°C/°F) or a
  second axis that is a fixed transform of the first, both labeled.

## Color

- Three uses only: distinguish (qualitative palette, ≤ 7 hues), encode a value
  (sequential; diverging when a meaningful midpoint exists), highlight (one neutral +
  one accent). Otherwise no color.
- Colorblind safety: avoid red–green, red–brown–green, purple–blue, pink–turquoise–grey;
  use Okabe-Ito, ColorBrewer safe schemes or viridis; add a second cue (direct label,
  shape, texture) for every hue-coded category; check a deuteranopia simulation.
- "Get it right in black and white": the primary attribute readable in luminance alone.
- Non-data ink (grids, frames, axes) light grey; marks ≥ 3:1 contrast against the
  background, text ≥ 4.5:1 (WCAG 2.1).

## Memory, attention, legibility

- Working memory holds 3–4 chunks: every legend, second axis or panel to remember is a
  chunk. Eyes beat memory: side-by-side views, not animation or paging.
- One pop-out feature for the highlight (color), never a conjunction (color AND shape).
- Multi-functioning elements (Tufte): let one mark do two jobs when it costs nothing (a
  value label that is also the bar end, a gridline that is also a reference value, a
  filter widget that also shows the distribution it filters).
- Text ≥ 12 px on screen, ≥ 18 pt on a projector; no rotated labels (rotate the bars).
- More than ~12 lines in a panel (fewer when told apart only by hue: label directly or
  grey out all but the highlighted ones), ~5 slices, ~12 bars per group, ~500 opaque points,
  ~40 panels: beyond the idiom's scale, change idiom.

## Text plan (Stokes & Hearst 2022; Kong et al. 2018; Borkin et al.)

- A title; for explanatory charts a takeaway title computed from the data.
- Axis titles with units; direct labels over legends; source, period, n and the
  definition of the measure.
- Annotate the features the reader will ask about (spikes, breaks, outliers) with the
  external context (why), not with restatements ("maximum").

## Distributions (Wilmer & Kerns 2022)

- Never bars of means: show the points, or a density/violin with n, and define any
  interval (SD, SE, CI). Sample size per group on the chart.

## Raw points and distribution shape (Correll 2023)

- Random jitter draws a different picture on every render and invents structure: use a
  strip (ticks or hollow/translucent points), a beeswarm or a seeded, documented offset.
- Density and violin shapes depend on the bandwidth, histograms on the bin width: state
  the choice, try more than one, and clip a density to the possible range. Discrete or
  rounded values get a histogram or dot plot, not a smooth density.
- A raincloud is only as good as its parts: pick a shape, raw values and a summary whose
  weaknesses differ (density + strip + median with a labeled quantile interval), not the
  default density + random jitter + box plot. State what box-plot whiskers mean.

## Uncertainty (Padilla, Kay & Hullman 2021)

- Intervals (error bars, box plots) hide the shape and are read as hard limits;
  distribution encodings (gradient, violin, density + interval) and frequency framings
  (quantile dot plot, icon array, hypothetical outcomes, ensembles) are read better.
- Match the encoding to the reader: lay readers may read uncertainty as "the data is
  wrong", so explain it in words; never let an uncertainty envelope look like the
  physical extent of the thing (the forecast-cone misreading).

## Multiple views (Munzner 2014 ch. 12)

- Decide in this order: one view changed by interaction, superimposed layers, or
  juxtaposed views (about twice the area, but eyes beat memory).
- Same data + same encoding = redundant; same data + different encoding = multiform
  (needs linked highlighting); subset + same encoding = overview and detail; different
  data + same encoding = small multiples; nothing shared = no linkage, not a dashboard.
- Superimpose at most two layers of area marks (three with care); line layers scale to
  about a dozen. Layers need distinguishable channel ranges (foreground vs background).
- One highlight color with the same meaning in every view; a selection must change
  something in another view; filtering removes context, highlighting keeps it.
- Comparing two states: show the difference explicitly, not two charts to subtract by eye.

## Rule IDs used by the seeds and the design document

| ID | One-line meaning |
|---|---|
| PUR-01 | the chart answers an identifiable question for an identifiable reader |
| PUR-02 | a number, sentence or table beats the chart for this task |
| PUR-10 | not a data visualization (no measured attribute, random data) |
| EXP-01 | nominal data on an ordered channel |
| EXP-02 | ordered data on an unordered channel (categorical hue for years) |
| EXP-03 | line/area over nominal categories |
| EXP-04 | bars for a temporal key when the task is trend |
| EXP-05 | pie/stack whose parts are not a whole |
| EXP-06 | stacking negative or non-additive values |
| EXP-07 | geometry not proportional to data (lie factor) |
| EXP-08 | length mark not from zero |
| EXP-09 | forced domain/clip or silently dropped channel hides data |
| EXP-10 | decorative variation that encodes nothing |
| EXP-11 | dual axes |
| EXP-12 | choropleth of raw counts |
| EXP-13 | cherry-picked window or subset |
| EXP-15 | histogram bins unlabeled / single width |
| EXP-16 | bars of means without the distribution |
| EXP-17 | class breaks unstated |
| EXP-18 | animated/interpolated values that do not exist |
| EFF-01 | main attribute not on the most accurate channel |
| EFF-02 | angle/area for precise comparison |
| EFF-04 | symbols scaled by radius |
| EFF-05 | small differences invisible (Weber) |
| EFF-06 | comparison without a common baseline |
| EFF-09 | salience does not match pertinence |
| EFF-11 | working-memory overload (legends, axes) |
| EFF-16 | overplotting / spaghetti / clutter |
| EFF-17 | unfamiliar idiom for this audience |
| EFF-19 | idiom beyond its scalability |
| SCL-02 | truncated axis not signalled / not justified |
| SCL-04 | zero baseline flattening meaningful variation |
| SCL-05 | axis extended far beyond the data |
| SCL-06 | axis titles missing / raw names / no units |
| SCL-07 | non-standard axis direction |
| SCL-08 | panels with independent scales where comparison is the task |
| SCL-12 | rotated category labels |
| SCL-13 | aspect ratio squeezes slopes |
| COL-02 | palette type does not match data type (rainbow) |
| COL-03 | redundant hue per bar |
| COL-04 | too many hues |
| COL-05 | not colorblind-safe |
| COL-09 | inconsistent color meaning / stereotyped colors |
| COL-10 | opacity artefacts |
| COL-13 | stereotyped or loaded colors |
| TXT-01 | no title |
| TXT-02 | title without takeaway or unsupported |
| TXT-03 | axes/legends unlabeled |
| TXT-04 | legend where direct labels were possible |
| TXT-05 | notable features unexplained |
| TXT-07 | encodings not explained |
| TXT-08 | no source, date, n, definition |
| TXT-10 | illegible text (tilted, tiny) |
| TXT-13 | false/lost precision in numbers |
| CLT-03 | density off the sweet spot (wasted or overwhelming space) |
| CMP-01 | order not purposeful |
| CMP-05 | multiple views not comparable |
| CMP-08 | animation where side-by-side was needed |
| IDM-PIE | pie beyond 5 slices / unsorted / exploded |
| IDM-STACK | stacked chart beyond its limits |
| IDM-LINE | line chart with nominal x or too many lines |
| IDM-HEATMAP | categorical palette for values, unordered rows |
| IDM-MAP | map anti-patterns (raw counts, rainbow, overlap) |
| IDM-SCATTER | scatter anti-patterns (overplotting, axis from 0 far from data) |
| IDM-RADAR/GAUGE | angle/radius encodings; use bars/bullets |
| IDM-WORDCLOUD | word cloud for comparison |
| IDM-TABLE | table design faults; or a table was the right answer |
| INT-02 | default state does not answer the main task |
| DAT-02 | normalization missing |
| DAT-03 | uncertainty hidden or undefined |
| EXP-21 | random jitter: a different picture on every render |
| EXP-22 | smooth density over discrete/rounded data or beyond the possible range |
| PUR-14 | uncertainty encoding beyond the reader's literacy, unexplained |
| CMP-09 | multiform views of the same data without linked highlighting |
| CMP-10 | too many superimposed layers |
| CMP-11 | views with no linkage presented as one dashboard |
| CMP-12 | two states compared without an explicit difference |
| CMP-13 | views cost more space than the comparison they enable |
| INT-04 | coordinated views not linked |
| INT-09 | selection wired to nothing |
| INT-10 | highlight color inconsistent across views |
| INT-11 | filtering where highlighting would keep the context |
| INT-12 | filter widgets without scent |
| DAT-10 | box-plot whiskers undefined |
| DAT-11 | uncertainty envelope readable as physical extent or hard limit |
| DAT-12 | ensemble members not comparable, current or labeled |
| DAT-13 | interval or statistic does not match the analysis performed |
| DAT-14 | scales/bins renormalize or drift out of sync between views |
| IDM-VENN | Venn/Euler beyond 3 sets; use intersection bars (UpSet) |
| IDM-SANKEY | Sankey with too many links, crossings or unordered nodes |
| IDM-RAINCLOUD | raincloud built from random jitter and an undefined box plot |
| RAIN-1 | raincloud components must cover each other's failure modes |
