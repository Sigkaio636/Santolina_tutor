# Perception facts used by the critique

Sources: Ware, *Information Visualization: Perception for Design* (3rd ed., 2013);
Healey & Enns 2012 (attention and visual memory); Mackinlay 1986 and Cleveland & McGill
1984 (channel accuracy); Palmer & Rock 1994 (connectedness); Garner 1974 (integral and
separable dimensions); Stevens 1957 (power law); Weber's law; Munzner 2014; Tufte 1983;
Few 2004/2009; Brewer (ColorBrewer); Okabe & Ito 2008; Datawrapper's colorblindness
series (Muth); WCAG 2.1; Borkin et al. 2013/2016 (memorability); Nielsen 1993 (response
times). Each fact ends with the rule IDs it supports.

## Channel effectiveness ranking (Mackinlay 1986; Cleveland & McGill)

Quantitative: position on a common scale > position on unaligned scales > length >
angle / slope > area > volume > luminance / saturation > hue > (texture, shape not
applicable).
Ordinal: position > luminance > saturation > hue > texture > connection > containment >
length > angle > slope > area > volume > shape.
Nominal: position > hue > texture > connection > containment > luminance > shape >
length > angle > slope > area > volume.

Consequence: put the most important attribute on the highest-ranked channel for its
data type; pies (angle), bubbles (area), 3D (volume), color-coded quantities are
measurably worse for precise comparison. → EFF-01, EFF-02, COL-02.

## Stevens' power law

Perceived magnitude S = k·Iⁿ. Length n ≈ 1 (linear); area n ≈ 0.7; volume n ≈ 0.6;
3D depth ≈ 0.67; brightness ≈ 0.33–0.5. Areas and volumes are systematically
underestimated, and more so the larger they are. Scale symbols by area, never by radius;
consider Flannery compensation (exponent ≈ 0.57) for proportional circles; avoid 3D bars
and 2D/3D-scaled icons (lie factor). → EFF-02, EFF-03, EFF-04, EXP-07.

## Weber's law and just-noticeable differences

ΔI/I = k: the detectable difference is a fixed proportion of the stimulus. Two long bars
of 980 and 1000 look equal; two short bars of 20 and 40 do not. Remedies: common
baseline, adjacency, light gridlines, framing (the enclosed white region above the bars
is a much larger relative difference), tick marks, plotting the difference itself, dot
plots that zoom into the relevant range. Color scales: adjacent steps must exceed a
JND, which caps the number of levels (~10 for heat maps). → EFF-05, SCL-02, COL-04.

## Preattentive processing (Healey; Ware)

A three-stage model: iconic memory (< 1 s, massively parallel, automatic =
preattentive), working memory (seconds, 3–4 chunks, attentive), long-term memory.
Preattentive detection takes < 200–250 ms (an eye movement needs 200 ms to start).
Preattentive features: line orientation, length, width, size, curvature, shape,
spatial grouping, added marks, enclosure (form); hue, intensity (color); flicker,
direction (motion); 2D position, stereo depth, convexity (spatial). Ware's basic
pop-out channels: color, elementary shape, motion, spatial grouping.

Rules of use: one unique feature pops out; a conjunction (red AND circle) does not and
needs a serial search whose time grows with the distractors. Pop-out is asymmetric (a
sloped line among vertical ones pops out; the reverse does not). Heterogeneous
distractors weaken pop-out. It works when the viewer knows what to look for. Training
does not help. Movement always captures attention: animated banners are highly
distracting. Design: highlight with a single channel (one accent color on grey),
limit distinct levels per channel, use motion only for alerts. → EFF-08, EFF-09,
EFF-10, COL-03.

## Working memory and attention

3–4 chunks held for a few seconds; a coherent pattern can be one chunk. Change
blindness: large changes go unnoticed when attention is elsewhere. Vigilance degrades
within minutes. Consequences: every legend, second axis, color code or remembered frame
is a chunk; eyes beat memory (side-by-side views over animation or paging); label
directly; keep comparisons within one view. → EFF-11, EFF-20, CMP-08, INT-07.

## Gestalt laws (Palmer & Rock; Ware)

Prägnanz (simplest figure), closure (incomplete contours completed: L-shaped axes read
as a frame), proximity (small spacing changes flip rows/columns; grouped bars), spatial
concentration (regions of similar density group), similarity (same color/shape groups),
continuity (elements on a line/curve belong together), common fate (same motion),
parallelism, connectedness (lines between elements group them more strongly than
proximity, color, size or shape: node-link, line charts, slope charts, leader lines),
symmetry, common region (enclosure, frames, background panels), past experience
(conventions, familiarity), focal point (a point of difference captures attention and is
the entry point), figure/ground (data must be figure; backgrounds, frames and gridlines
must recede). Misuse creates false groups or false relations. → EFF-12, EFF-13,
EFF-15, EXP-03, CLT-01.

## Visual search hierarchy (Ware)

Move-and-scan loop (biased by the target feature), eye-movement loop (1–3 saccades per
second, the brain keeps ~5–6 recently visited regions), pattern-testing loop (~50 ms per
test). Organize layouts large → small with structure at each level; give the search an
entry point. → EFF-15.

## Integral vs separable dimensions (Garner)

Integral: cannot attend to one without the other (width × height of a rectangle, hue ×
saturation). Separable: can be read independently (size and color, size and
orientation). Use integral pairs for holistic judgments, separable pairs for analytic
reading of each attribute. Redundant size speeds classification; redundant color does not
help length judgments. → EFF-14.

## Color

Four uses: distinguish (categorical, qualitative palette), encode values (sequential
without a neutral; diverging with a meaningful midpoint), highlight (one accent), and
no use (neutral greys). Factors: distinctness, unique hues (red, green, blue, yellow,
black, white are the most distinct), contrast with the background, number of levels vs
difference between them, field size (small marks need stronger colors), color blindness,
conventions (blue cold / red hot; political; traffic-light).

Colorblindness: red–green deficiency in ≈ 8 % of European men, 4–5 % of Asian men;
6–7 % color weak, 2–3 % color blind; women ≈ 0.5 %. Problem pairs: red–green,
red–brown–green, pink–turquoise–grey, purple–blue. Safe bets: blue–orange, blue–red
with luminance difference, Okabe-Ito, ColorBrewer colorblind-safe schemes, viridis
family. Defensive design: avoid problem pairs, add a second cue (shape, texture, stroke,
direct labels), use a chart that does not need color, test with a simulator (Coblis).
Low vision: 4 % of the population; half of people over 50; everyone over 40 needs
correction for small text: contrast and size are not optional.

Contrast: poor when two colors have similar luminance; WCAG 2.1 non-text contrast ≥ 3:1
against adjacent colors, text ≥ 4.5:1 (large text ≥ 3:1). Simultaneous contrast
between adjacent pure colors shifts perceived hues. Reading on screens is slower than
on paper and worse on mobile; glare and cheap monitors amplify low contrast.

"Get it right in black and white": encode the most important attribute in luminance so
the chart survives grayscale printing and most deficiencies; hue and saturation are
secondary. Non-data elements (axes, grids, frames) just visible: light grey. Start
with greys, add one accent, stop. Rainbow/jet: no perceptual order, false boundaries,
unequal steps. → COL-*, ACC-*.

## Legibility and display

Eye resolution ≈ 50 cycles per degree: features smaller than 0.1 mm at 30 cm are not
resolved; rule of thumb: no more than 500 intervals per 216 mm; 1 pt = 1/72 in = 0.353
mm ≈ 4 px on a 1920-px-wide display at typical size, 2 px on a projector. Fonts:
sans-serif, lining and tabular figures, multiplexed weights, no thin faces, uppercase
sparingly, bold only for emphasis, neither condensed nor extended. Tilted/3D text loses
legibility fast. More pixels per inch do not add usable information: acuity, screen
size, viewing distance and cognition are the bottleneck; density must balance clutter
and wasted space. → EFF-18, ACC-05, TXT-10, TXT-11.

## 3D

Depth is one axis with poor accuracy (0.67), occlusion hides data, perspective breaks
size comparison, shadows add clutter, text tilts, static scenes give weak depth cues
and navigation takes time. Benefits only for inherently 3D shapes. → EFF-03.

## Ensemble perception and proxies

Readers judge the mean or spread of a cloud of points without counting, using
shortcuts: the densest region, the outline of the cloud, the extremes. Estimates are
fast but biased by outliers, by mark size and opacity, and by whatever shape encloses
the points (a box or bar "contains" them). Hence: an explicit mark for the center, a
shape layer for the density, and no filled container around raw points.
→ RAIN-10, MEANBAR-11, EXP-16.

## Data-ink and signal-to-noise

Data-ink ratio = data ink / total ink. Maximize it, erase non-data ink and redundant
data ink, within reason (light grids, labels and annotations are useful ink; "be fair").
Signal-to-noise: keep the design simple, enhance with deliberate redundancy and
highlighting, remove noise. Multi-functioning elements (range frames, direct labels,
stem-and-leaf, sparklines, a filter widget that shows the distribution it filters)
raise the ratio. Data density = number of data entries / area of the graphic: low
density is wasted space, very high density needs an overview. → CLT-01, CLT-03,
CLT-04, CLT-08, PUR-11, INT-12.

## Memory for charts (Borkin et al. 2013, 2016)

Text is the most memorable part of a visualization; the title is among the most
important elements for recall; redundancy between data and text helps recognition and
recall; text that refers to relevant parts of the chart is easier to recall; more text
seems better. → TXT-01, TXT-02, TXT-05.

## Latency (Nielsen 1993; Shneiderman 1996 dynamic queries)

0.1 s: feels instantaneous; 1 s: flow uninterrupted but delay noticed, give feedback;
> 10 s: user switches task. Filtering with dynamic queries should update under 100 ms.
Tooltips must be immediate; a detail window may take slightly longer. → INT-06.
