# Three empirical papers, as critique rules

Rule IDs here (TRUNC-n, TEXT-n, MEANBAR-n) are cited alongside the catalog IDs.

## Correll, Bertini & Franconeri, "Truncating the Y-Axis: Threat or Menace?" (CHI 2020)

What they found. Three crowd-sourced experiments rated the perceived severity of a
difference under y-axes starting at 0 %, 25 % and 50 %. Truncation inflates perceived
severity monotonically and strongly. There was **no significant difference between bar
and line charts**: the exaggeration is a property of the axis range, not of the mark.
Designs meant to flag truncation (broken axis with broken bars; a gradient at the bar
base) **did not reduce the inflation at all**; they only make the truncation visible.
The bias is visual, not numeric: participants read the values correctly and still rated
truncated charts as more severe; wording ("look at the trend" vs "values") changed
ratings negligibly (0.07 vs 0.36 per truncation step). The authors reject a binary
honest/dishonest rule and Huff's "always start at zero": a zero baseline can itself
deceive by flattening meaningful change (global temperature in °F from 0), and whole
genres (control charts, index charts, stock charts, anomaly charts) legitimately use
non-zero references. Recommendation: choose the axis range by the **scale of the
meaningful effect size** in the domain; the responsibility cannot be delegated to a
chart type or a visual cue. Also: converting categorical bars to a line to "allow"
truncation adds a false continuity metaphor; over-expanding axes far beyond the data
also distorts (inflates perceived correlation, flattens trends).

Rules.
- **TRUNC-1** (DET, crit) Length/area marks (bars, columns, stacked bars, histogram
  bars, areas) whose quantitative axis does not start at zero: bar-height ratio ≠ value
  ratio (Fox chart: 1.13 value ratio drawn as 6×). Exception: deviation/index bars from
  an explicit, drawn, labeled reference.
- **TRUNC-2** (DET, crit) Quantify the exaggeration: (visual difference / visual span)
  ÷ (data difference / data magnitude); report the factor; flag above ~1.5× when the
  message is the magnitude of a difference. Exception: a small but consequential change
  is the stated point (stock, CO₂, process deviation) → then apply TRUNC-4/5.
- **TRUNC-3** (DET, crit) A broken-axis glyph, bar break, gradient or torn baseline earns
  back nothing; judge the chart by its axis range as if the cue were absent. It is still
  better for transparency (TRUNC-7).
- **TRUNC-4** (JUDG, crit) Ask what magnitude is meaningful in this domain and whether
  the axis makes that magnitude look as important as it is: meaningful differences must
  not look trivial, trivial ones must not look dramatic. Exception: analyst-controlled
  interactive zoom.
- **TRUNC-5** (SEMI, major) Zero baseline that compresses the meaningful variation into
  a flat line when zero is arbitrary (°C/°F, indices, dates, bounded scores) or small
  changes matter. Trigger: data span / axis span < 15 % on a line chart. Exception: the
  message is the absolute level or share.
- **TRUNC-6** (JUDG, crit) Lines, areas and dot plots are not exempt: apply TRUNC-2/4 to
  them too; the mark type gives no license.
- **TRUNC-7** (DET, major) A non-zero baseline must be explicit: visible tick labels at
  the axis start plus a caption/annotation stating the baseline and why. Exception: index
  or anomaly charts with the reference line drawn and labeled in the plot.
- **TRUNC-8** (DET, minor) Truncated axes should start at an easy anchor (round number
  or meaningful reference) with enough gridlines; starting at 25 on a 0–100 scale raised
  value-reading errors.
- **TRUNC-9** (JUDG, major) Build non-zero-baseline charts around an explicit reference
  quantity (expected value, index base, target, control limit) drawn as a line, so the
  reader compares deviation from it rather than height from an arbitrary cut.
- **TRUNC-10** (DET, major) Do not turn categorical bars into a line to legitimize a
  non-zero baseline; lines imply continuity. Exception: ordinal categories, labeled.
- **TRUNC-11** (DET, major) Axes extended far beyond the data (data span / axis span <
  ~50 %) compress the cloud and distort judgments. Exception: shared scales in small
  multiples; annotated headroom to a limit.
- **TRUNC-12** (JUDG, minor) Caption wording does not neutralize a visually exaggerated
  range; fix the range or add a full-range companion view.

## Stokes & Hearst, "Why More Text is (Often) Better" (IEEE VIS 2022)

What they found. 302 participants ranked six variants of a univariate time-series line
chart: chart only, + title, + 1 annotation, + 2 annotations, + 3–6-annotation narrative,
and text only; 2,115 free-text comments were coded. More-annotated charts were preferred
(the narrative version first, two annotations second, chart-only last); even a plain
paragraph beat the bare chart. The dominant theme was **context**: readers want to be
informed even at the cost of simplicity ("too busy, but the most informative"); clutter
and simplicity were rarely the reason for a ranking. The **kind** of text matters:
annotations that restate the visible (labeling the obvious maximum, arrows in the trend
direction) were called redundant; annotations with external context (why the spike,
which policy) and concrete data (the exact date next to "minimum") were valued. A missing
title was treated as a schema violation. Text-only was uniquely read as a narrative
(order, causation); annotated charts almost never were. Suspicion of bias concentrated on
annotated charts: one annotation looked like cherry-picking, two felt like being led,
the full narration like "thinking for the reader"; bare charts felt unbiased but
uninformative. Caveats: preference, not measured comprehension; line charts of time
series only; stand-alone charts without surrounding text.

Rules.
- **TEXT-1** (DET, major) A title that says what is shown (measure, unit, population,
  period); not a variable or file name. Exception: a shared title over small multiples
  or an explicit caption.
- **TEXT-2** (JUDG, major) The title (or subtitle) carries the takeaway or the frame,
  and the data supports it; flag slanted or misaligned titles (readers recall the title's
  message over the data). Exception: neutral titles for exploratory dashboards.
- **TEXT-3** (JUDG, major) Explanatory charts annotate notable features with external
  context (why). Exception: analyst-facing views; features explained in adjacent text.
- **TEXT-4** (SEMI, minor) Annotations that only restate the visible ("Maximum",
  "Peak", "goes up") without value, date or reason. Exception: alt-text/accessibility;
  values unreadable from the axes.
- **TEXT-5** (DET, minor) Callouts state concrete data (value and date/category), not
  just a label. Exception: value already printed as a data label.
- **TEXT-6** (SEMI, minor) Prefer two or more annotations (or a short narrative) to a
  lone one, which reads as cherry-picking. Exception: exactly one notable feature;
  sparklines.
- **TEXT-7** (JUDG, major) Do not penalize informative text as clutter; penalize only
  redundant text or text that occludes data. Minimalism that strips title, annotations
  and context lowers value.
- **TEXT-8** (DET, minor) Decorative or redundant annotation glyphs (arrows along an
  obvious slope, duplicate markers, pointless leader lines).
- **TEXT-9** (JUDG, major) Explanatory text sits next to the feature it explains, not
  only in a detached caption. Exception: very dense charts with numbered markers.
- **TEXT-10** (JUDG, minor) Context must be evidence-backed, observation separated from
  causal interpretation, causal claims attributed; avoid steering with selective
  context. Exception: declared editorial pieces.
- **TEXT-11** (JUDG, minor) Chart + text tell a coherent story; as a check, write the
  text-only version and verify the title and annotations cover its sentences; reuse it
  as caption/alt-text.
- **TEXT-12** (DET, minor) Tick granularity fine enough for the questions the chart
  invites (yearly ticks if annual events are discussed); units stated.
- **TEXT-13** (JUDG, minor) A bare chart reads as unbiased but "not even trying"; only
  justified in genuinely exploratory settings, and then say so.

## Wilmer & Kerns, "What's really wrong with bar graphs of mean values" (2022)

What they found. 133 participants sketched 20 plausible data points per bar for four
real textbook mean-bar graphs. On all three dimensions (mean location, variation and
overlap, distribution shape) the sketches showed large systematic errors and huge
between-person variability. Common fallacies: **Bar-Tip Limit Error** (22–32 %: points
drawn inside the bar as if the tip were a maximum; the "within-the-bar bias" from
confusing mean bars with single-value bars), **Dichotomization Fallacy** (23–52 %: group
distributions barely overlap, so effect sizes are massively overestimated; median drawn
effects exceeded even d = 2.08, 75th-percentile up to ~15× the real one), **Uniformity
Fallacy** (22–26 %: flat spreads with no tails). 58–87 % of drawings per graph showed
at least one fallacy; rates barely depended on education, statistics training, age,
gender or country; people were consistent across graphs; the error types were
independent. Bidirectional bars (diverging from a central baseline) increased
dichotomization because tips are farther apart. Bars are a best practice for single
numbers (counts, amounts, percents on a common baseline); a mean bar hides a
distribution; "simple for novices" is not supported (these graphs were designed for
novices and failed). Alternatives: dot/strip/beeswarm/sina plots (jitter, opacity,
hollow markers; but see RAIN-2: random jitter redraws differently every time, so
seed it or use a deterministic layout), box plots or violins at least, quantile dotplots and hypothetical
outcome plots for uncertainty. Error bars are often omitted, ignored or misread even by
experts. Axis-range bias (Correll) compounds all this.

Rules.
- **MEANBAR-1** (DET, crit) A bar whose height is a mean/median/other summary of a
  distribution rather than a count, sum or proportion (seaborn `barplot` default
  estimator, `groupby().mean().plot.bar()`, `mean()` aggregate on a bar mark). Exception:
  tolerable only with raw points overlaid (MEANBAR-2) and dispersion (MEANBAR-3).
- **MEANBAR-2** (DET, crit) Group comparisons on a measured variable show the
  individual observations (strip/dot/beeswarm/sina). Exception: very large n → violins,
  density, quantile dotplots or box plots with n stated; never a bare bar.
- **MEANBAR-3** (DET, crit) Variation and between-group overlap visible (distribution or
  at least SD/CI); means alone let readers invent far too little variation. Exception:
  quantities with no within-group variation.
- **MEANBAR-4** (DET, major) Any interval (error bar, band, whisker) is defined (SD, SE,
  95 % CI, IQR, min–max); unlabeled error bars are a defect; SE bars visually understate
  variation.
- **MEANBAR-5** (DET, major) Diverging/bidirectional mean bars from a central baseline
  widen the visual gap and increase dichotomization; prefer common-baseline dot/interval
  or distribution plots. Exception: diverging bars of raw signed single numbers.
- **MEANBAR-6** (DET, major) Sample size per group stated on the chart or caption.
  Exception: every point visible and countable.
- **MEANBAR-7** (SEMI, major) Show distribution shape (tails, skew, bimodality) with a
  geometry that reveals it (violin, density, quantile dotplot, histogram) rather than one
  that hides it (bar, mean ± SE). Exception: the task is only ranking centers and shapes
  are stated to be similar.
- **MEANBAR-8** (JUDG, crit) For group comparisons, make the effect size readable in
  distribution terms (visible overlap or annotated overlap/standardized effect) so the
  gap between summaries is not read as a categorical difference (d = 0.8 ≈ 69 % overlap).
  Exception: population totals where individual inference is not intended.
- **MEANBAR-9** (JUDG, major) "The audience are novices, so a simple bar is clearer" is
  not a justification: the simple mark does not produce accurate interpretation; novices
  need more explicit distribution display, not less.
- **MEANBAR-10** (DET, minor) When raw points are shown, control overplotting (strip or
  beeswarm, seeded jitter, transparency, hollow markers; not unseeded jitter, RAIN-2); flag opaque perfectly overlapping points. Exception:
  small n.
- **MEANBAR-11** (DET, major) If a summary mark is kept, it must not visually "contain"
  the data: a line or point with raw points extending above and below, not a filled bar
  with points only inside it.
- **MEANBAR-12** (DET, crit) Apply TRUNC rules to mean-comparison charts; truncation and
  mean-only display compound.
- **MEANBAR-13** (JUDG, minor) Decision-oriented charts of uncertain outcomes prefer
  uncertainty-literate encodings (quantile dotplots, hypothetical outcome plots, full
  distributions) over mean ± error bar. Exception: expert audiences with documented
  conventions. Do not place a quantile dot plot beside raw-data dots (RAIN-1).

## Correll, "Teru Teru Bōzu: Defensive Raincloud Plots" (EuroVis 2023)

What it argues. A raincloud plot combines a distribution shape ("cloud": density,
histogram, quantile dot plot), the observations ("rain": strip, jitter, beeswarm,
Wilkinson dot plot) and a summary ("lightning": box plot, mean or median with an
interval). The paper tests each component with Algebraic Visualization Design
(Kindlmann & Scheidegger 2014), which asks two questions of any chart: does a change
in the data that matters produce a visible change, and does a change that does not
matter leave the picture alone? Four failures follow. **Hallucinator**: the same data
draws different pictures (random jitter differs on every render; a lineup of jitters
of one dataset looks like several datasets). **Confuser**: different data draws the
same picture (a box plot's five numbers fit unimodal and bimodal data alike; opaque
overplotted points). **Jumbler**: a small data change produces a large visual change
(bin edges, bandwidth, renormalized axes after one added value). **Misleader**: a
large data change produces a small visual change, or the picture suggests what is not
there (oversmoothed density hiding modes, density tails beyond the possible range,
integer data drawn as continuous). The canonical raincloud (default density + random
jitter + box plot) stacks three undefended components. The defensive recipe: choose
components whose failure modes differ so each exposes what another hides, for example
a density with a stated bandwidth, a strip of the values at their true positions and
a median with a labeled quantile interval. Rainclouds are not a cure-all: they cost
space and literacy, and are overkill for one value per item.

Rules.
- **RAIN-1** (JUDG, major) Mutual defence: the shape, the raw values and the summary
  must fail in different ways. Beeswarm + violin repeat the same shape; a quantile dot
  plot beside dot "rain" makes data and quantiles indistinguishable. Exception: a
  single component is enough when n is tiny and every value is visible.
- **RAIN-2** (SEMI, major) Unseeded random jitter is a hallucinator: redraw and the
  picture changes. Use a strip, a deterministic layout or a seeded and stated offset.
  (= EXP-21.)
- **RAIN-3** (DET, minor) Overplotted rain: opacity too low loses isolated points, too
  high hides density; hollow markers are the safer default. Exception: a shape layer
  already carries the density.
- **RAIN-4** (SEMI, major) Bandwidth and bin width are a bias–variance choice;
  defaults over- or under-smooth. State the value, show that the message survives a
  second value. (= EXP-15.)
- **RAIN-5** (SEMI, major) Discrete, rounded or bounded data: no smooth density over
  integers, no tails beyond the possible range; dot plots re-discretize and can make
  continuous data look discrete. (= EXP-22.)
- **RAIN-6** (SEMI, minor) Box-plot whiskers, notches and widths have several
  conventions; state the one used, and remember the box area biases the reading of the
  whiskers. (= DAT-10.)
- **RAIN-7** (JUDG, major) The summary shown is the summary analysed: a credible
  interval for a Bayesian estimate, a CI for a frequentist one, labeled; otherwise a
  plain mean or median marker. Inference by eye from overlapping intervals is
  unreliable. (= DAT-13.)
- **RAIN-8** (JUDG, major) Renormalization: adding data to the mode rescales a density,
  a heatmap's color domain or a histogram's count axis; components that rebin
  separately drift apart. Fix domains or say they move. (= DAT-14.)
- **RAIN-9** (JUDG, minor) Perturbation test, for any chart: name one change in the
  data that the reader must notice and check it is visible; name one that must not
  matter (row order, a re-render, a different seed) and check the picture is stable.
- **RAIN-10** (JUDG, minor) Readers estimate a group's center from points with
  perceptual shortcuts (the densest region, the outline): add an explicit mean or
  median mark instead of expecting the cloud to convey it.

Related works cited in the rules: Allen et al. 2019 (raincloud plots); Kay et al. 2016
(quantile dot plots: predictive distributions as countable dots); Padilla, Kay &
Hullman 2021 (uncertainty visualization: intervals, distributions, frequency
framings, hybrid forms such as the contour box plot); Hullman et al. 2015
(hypothetical outcome plots); Wickham et al. 2010 (lineups: hide the real chart among
charts of null data to test whether a pattern is real); Sun et al. 2022 (how links
between coordinated views are designed: between items, between views, or both; shown
by highlighting, drawn connections, bundling or enclosure); Willett, Heer & Agrawala
2007 (scented widgets: controls that show the data behind each choice).

## Meta-rule shared by the papers

The reader fills every gap with their own, usually wrong, assumptions. Value depends on
what the chart makes explicit: the baseline and reference (TRUNC), the context and
takeaway (TEXT), the underlying distribution (MEANBAR), the choices behind each
component of a distribution plot (RAIN). Caveats to keep the critic
accurate: TEXT results are preferences on line charts of time series, not measured
comprehension; TRUNC means a zero baseline can deceive as much as a truncated one;
MEANBAR concerns bars of distributions (behavioral data), not bars of counts.
