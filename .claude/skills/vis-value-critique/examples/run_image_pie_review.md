# Critique: exploded 8-slice pie of market share by product

**Input**: `market_share.png` (750 × 750 px, no code or data available), idiom: pie (exploded,
with drop shadow). Data as read from the image: 1 nominal key (product, 8 categories:
Widgets, Gadgets, Gizmos, Doodads, Thingamajigs, Whatsits, Doohickeys, Sprockets) × 1
quantitative value (share, presumably % of a market). No values are printed anywhere; the
shares below are my own measurement of the slice angles (±1 pt).

**Assumed purpose**: explanatory, one slide, management / general business audience, projected
in a meeting room. Task(s), inferred because the user gave none: (1) *who leads the market and
by how much*, (2) *rank of the products*, (3) *rough share of each*. Nothing in the image says
which market, which period, which metric (revenue? units?) or whose products these are; I
critique as if it is "our 8 products' share of one market in one period".

## Verdict

The picture delivers a fraction of the value this data supports. The one thing it does say in
five seconds ("Widgets is the biggest piece, and someone wants you to look at it") is correct,
and that is where the value ends. Eight slices, five of them between 5 % and 11 %, are encoded
on angle, the channel people read worst after area and volume, so the ranking of the six
smaller products is guesswork; no number is printed, so no share can be retrieved; there is no
title, no period, no unit, no source, so the slide cannot be trusted or quoted. The explosion,
the drop shadow and the rainbow palette are pure cost: they occupy attention, break the
angle-reading the chart relies on, and for roughly 8 % of the men in the room red, green and
brown collapse into one olive tone. A **sorted horizontal bar chart with the percentages printed
and a takeaway title** would answer all three tasks immediately on the same slide area. That
single change recovers most of the lost value; if the slide really must keep "parts of a whole"
visible, a single 100 % stacked bar underneath, or "share, % of total" in the axis title, does
it without a pie.

## Value scorecard (V = T + I + E + C)

| Component | Score | Why |
|---|---|---|
| T · Time | 1/3 | Find extremum: immediate (Widgets, helped by size, position and explosion). Sort: work for the top 3, impossible beyond (Thingamajigs 8 %, Whatsits 6 %, Doohickeys 5 %, Sprockets 5 % cannot be ordered from angle). Retrieve value: impossible (no numbers, no axis). Compute derived value ("top 2 = half the market?", "the long tail = ?"): impossible without printed values. Filter/range: work. A table of eight numbers beats it on every task but "who is largest". |
| I · Insight | 1/3 | Re-encodes eight numbers that are not even shown; nothing a table would hide is revealed. The one potential insight, "two products hold ~half the market and six fight over the rest", is there but needs mental addition of angles. |
| E · Essence | 2/3 | The gist "Widgets leads" is right and fast, mostly because the slice is biggest, red, on top and pulled out. But the chart has no title, so the reader has to construct the message, and the rainbow pulls attention to every slice equally after the first glance. |
| C · Confidence | 0/3 | No title, no metric, no unit, no period, no market definition, no source, no total (n or currency). A grey slice for Sprockets reads like "other / not applicable" when it is a product. Shadow and explosion are the visual vocabulary of marketing decoration, which lowers trust further. Nothing can be checked or quoted from this slide. |

Expressive: **partly**. Angle for a part-to-whole is legitimate *if* the parts are a whole; here
the parts do sum to ~100 % (measured), so no false relation is drawn, but the explosion and
shadow add geometry that encodes nothing (decorative variation). Effective: **no**. Angle and
area for eight values, five of them within 6 points of each other; hue carries only category
identity that the direct labels already give; red/green/brown merge under CVD. Appropriate:
**no**. A 750 × 750 image, a third of the slide, for eight numbers that a sorted bar chart
would show more precisely in the same space, or a two-column table in a quarter of it.

## Findings

### Critical (misleads or blocks the main task)

- **[IDM-PIE, EFF-19, EFF-02]** Eight slices on a pie. Evidence: 8 labeled wedges; measured
  shares ≈ 29, 22, 14, 11, 8, 6, 5, 5 %. The idiom's limit is 3–5 slices with clearly different
  sizes, and the exception for pies (2–3 parts with simple fractions) does not apply.
  Consequence: the rank and relative size of the six products below Gizmos cannot be read
  (Doohickeys vs Sprockets differ by well under the angle JND; Thingamajigs vs Whatsits by
  ~2 points); the "sort" and "compare" tasks that a market-share slide exists for are
  impossible. Fix: sorted horizontal bar chart (see Redesign).
- **[PUR-02, CMP-02]** No value is printed, and the chart cannot substitute for the values.
  Evidence: zero numerals in the image (OCR: 8 words, all category names). Consequence: nobody
  can retrieve or quote a share; the only honest statement a viewer can make after the slide is
  "Widgets is the largest". Eight printed numbers would beat this chart. Fix: print the share
  next to every bar (and, if the pie were kept, on every slice).

### Major (slows the task, hides insight, loses readers)

- **[TXT-01 / TEXT-1, TXT-02 / TEXT-2, PUR-04]** No title at all, let alone a takeaway.
  Evidence: inspector found no title band; the image is the wedge and its labels. Consequence:
  readers treat a missing title as a schema violation; the message ("Widgets and Gadgets hold
  half the market") has to be invented by each viewer, and the chart is unmemorable. Fix: title
  with the takeaway, subtitle with metric, market, period.
- **[TXT-08, PUR-09, SCL-06]** No metric, unit, period, market definition, total or source.
  Evidence: no text other than product names. Consequence: "market share" of what (revenue,
  units, customers), where, when, measured by whom? C = 0. Fix: subtitle "Share of 2025 revenue
  in <market>, total <X> M€, source: <team/report>, as of <date>".
- **[COL-05 / ACC-01]** Red–green–brown palette with no second cue. Evidence (deterministic):
  under deuteranopia ΔE between Widgets red and Gizmos green drops from 117 to 19.5, red vs
  Whatsits brown to 15.9, green vs brown to 14.4, blue vs purple to 13.0; under protanopia red
  vs brown ΔE = 2.7 (indistinguishable). The deuteranopia simulation shows Widgets, Gizmos and
  Whatsits as three olives. Consequence: for ~8 % of male viewers the colors stop identifying
  anything; they fall back on the direct labels, which fortunately exist, so the chart is
  degraded, not destroyed. Fix: drop hue as identifier entirely (one neutral colour + one
  accent), or a CVD-safe palette (Okabe-Ito / Tableau 10) if colour must be kept.
- **[CLT-01, EXP-10, EFF-03]** Exploded slice plus drop shadow. Evidence: Widgets is offset
  ~40 px from the centre; a grey shadow runs under Widgets and along the lower-left rim.
  Consequence: the explosion breaks the common vertex that angle reading depends on (the
  slice now reads as area, with Stevens exponent ~0.7), the shadow adds a grey rim that reads
  as a ninth, unlabeled slice at the bottom-left and makes the chart look 3D. These are the
  "decorative variation" readers scan for meaning and do not find. Fix: no explosion, no shadow,
  no 3D; emphasize with one accent colour and the title.
- **[CMP-01]** Wedges run **counter-clockwise** starting at about 1–2 o'clock. Evidence:
  Widgets (largest) spans ~30°–135° measured counter-clockwise from 3 o'clock; Sprockets ends
  at ~30°. The order *is* largest → smallest, which is right, but it runs the wrong way and
  starts at the wrong place (convention: from 12 o'clock, clockwise), so the reader's
  clockwise scan meets Sprockets, Doohickeys, Whatsits… before Widgets. Fix: in a bar chart
  this becomes "sort descending, top to bottom".
- **[COL-03, EFF-11, EXP-10]** One hue per product when the direct labels already identify
  them. Evidence: 7 chromatic colors + grey, all distinct. Consequence: no information is
  added, every slice competes for attention equally (no focal point beyond size), and the
  grey Sprockets slice violates the convention that grey means "other / non-data" (COL-09).
  Fix: single neutral colour, one accent on the product the title is about.
- **[COL-06 / ACC-02]** Yellow (#f8f830) and pink (#f080b8) on an off-white background.
  Evidence (deterministic): both flagged as low contrast on white; in grayscale the
  Thingamajigs wedge is the same tone as the background and the pie's outline there is a
  gap. Consequence: on a projector in a lit room the Thingamajigs slice washes out, and
  printed in black and white it disappears entirely (COL-08, ACC-04). Fix: covered by the
  single-colour plan.
- **[TXT-04, EFF-07]** Labels float around the rim with no leader lines, no values, and
  "Doohickeys" is cut at the right edge of the image. Evidence: label text touches x = 750;
  Sprockets' label sits above the Doohickeys wedge. Consequence: label–wedge matching for the
  three slivers on the right is ambiguous; a cut label on a slide looks careless and costs
  trust. Fix: horizontal bars put every label at the left of its bar, full width, no
  ambiguity.

### Minor

- **[PUR-11, CLT-03]** 750 × 750 px, 70 % of it background, for eight numbers. Data density is
  very low; the same information fits a 1:2 panel that leaves room for the message and a
  context line. Fix: landscape bar panel, roughly 900 × 450.
- **[ACC-03, ACC-05]** Labels are 16–20 px on a 750 px image (median 20 px, ~2.7 % of width).
  Fine on a laptop; on a projector at the back of a room they are at the limit, and the slide
  has no larger text to anchor it. Fix: title ≥ 28 px equivalent, labels ≥ 18 px, values in the
  same size as labels.

## Deterministic check log

Script: `python3 scripts/inspect_image.py market_share.png --out-dir <outputs>` (derived images
`market_share_grayscale.png`, `market_share_deuteranopia.png`, `market_share_protanopia.png`,
`market_share_tritanopia.png` saved alongside this review).

- Size 750 × 750 px; background #f8f8f8 covers 67 %; non-background ink 33 %.
- Palette: 7 chromatic colours (#db1f1f, #3078b8, #48a848, #9848a0, #f8f830, #a05028,
  #f080b8) + grey; `has_red_and_green = true`.
- COL-05 (major, SEMI) fired twice: red–green present; red vs green ΔE under deuteranopia
  19.5. Confirmed by eye on the deuteranopia image: Widgets / Gizmos / Whatsits are three
  shades of olive; blue / purple (Gadgets / Doodads) become two blues. Protanopia: red vs
  brown ΔE 2.7. Tritanopia: blue vs green ΔE 17.5. Kept, and raised in importance because
  there is no shape/texture cue; downgraded from crit to major only because direct labels
  survive.
- Low contrast on white: #f8f830 (yellow), #f080b8 (pink). Confirmed on the grayscale image
  (Thingamajigs merges with the background).
- TXT-01 (major, SEMI): no title-like text at top. Kept; the "caption in the surrounding
  document" exception cannot be assumed for a slide (the slide title, if any, is not in the
  file and the user asked about the chart as delivered).
- SCL-06 (minor): no unit token found. Kept, merged into the TXT-08 finding (the unit is the
  definition of the metric here).
- TXT-08 (minor): no source / n detected. Kept, raised to major because for a market-share
  slide the market definition and period *are* the data.
- OCR: 8 words, text height 16–20 px, median 20 px.
- Own measurement (pixel sampling on two rings around the pie centre, 3600 samples each):
  shares ≈ Widgets 29, Gadgets 22, Gizmos 14, Doodads 11, Thingamajigs 8, Whatsits 6,
  Doohickeys 5, Sprockets 5 (sum ≈ 100, so EXP-05 "parts are not a whole" does **not**
  fire). Direction: counter-clockwise, start ≈ 30° from 3 o'clock. Explosion offset of the
  Widgets slice ≈ 40 px. No lie-factor issue: wedge angles are proportional to the measured
  shares; the distortion is perceptual (angle/area), not geometric.
- No inspector rule fired for slice count, explosion, shadow, ordering or missing values: the
  image inspector cannot detect idiom features, so IDM-PIE, CLT-01, CMP-01 and PUR-02 are
  judgment findings based on reading the image.

## What to preserve

- Direct labels on the marks (no legend). This is the only reason the chart survives colour
  blindness; keep direct labelling in the redesign.
- Descending order by share. The sequence is right; only its direction and starting point are
  wrong.
- The emphasis on the leader. Whoever made this wanted the room to look at Widgets; the
  redesign keeps that intent, with a title and an accent colour instead of an explosion.
- Eight products, no "Other" bucket. Showing the whole long tail is honest; do not collapse
  it unless the slide's message is only about the top two.

## Redesign

- **Idiom**: horizontal bar chart, one bar per product, sorted descending top → bottom. If the
  "parts of a whole" reading must stay visible, add a slim 100 % stacked bar (one row,
  same order, same accent) under the title, or simply state the total in the subtitle;
  do not keep the pie.
- **Encodings**: product → position on the y axis (nominal, ordered by value); share →
  bar length from a zero baseline on a common x scale (0–30 %, or 0–100 % if the slide's
  point is "nobody dominates"); value → text label at the end of each bar ("28.6 %"); if
  the slide is about the top two, a light bracket or shaded band grouping Widgets + Gadgets
  with the annotation "together 51 %".
- **Ordering / scales**: descending by share; x axis from 0 with the % sign in the tick
  labels or in the axis title; with values printed, drop the tick labels and gridlines
  entirely (axis title "Share of <market>, %" is enough).
- **Colour plan**: one neutral mid-grey for all bars; one accent (a CVD-safe blue such as
  #0072B2, or the company colour if it is not red/green) on the bar(s) the title talks
  about. No hue-per-category, no legend. Check: the grayscale version must still show the
  accent as the darkest bar; deuteranopia/protanopia: blue vs grey is safe.
- **Text plan**: title = the takeaway ("Widgets and Gadgets hold half the market; six
  products share the rest"); subtitle = metric, market, period, total ("Share of 2025
  revenue, <market name>, total <X> M€"); bar labels = product names at the left,
  percentages at the right end of each bar, one decimal at most; footer = source and
  date ("Source: <internal sales report / analyst firm>, data as of <date>"). If a
  product's share changed notably vs the previous period, that is the one annotation
  worth adding (e.g. "+4 pts vs 2024"), with the previous value as a small hollow dot
  on the same row.
- **Layout / medium**: landscape panel (~2:1), labels ≥ 18 px, title ≥ 28 px at slide
  resolution; nothing rotated; no shadow, no 3D, no explosion.
- **Interaction**: none; a slide is static.

Sketch (matplotlib), assuming the measured shares:

```python
import matplotlib.pyplot as plt
products = ["Widgets","Gadgets","Gizmos","Doodads","Thingamajigs","Whatsits","Doohickeys","Sprockets"]
share    = [28.6, 22.2, 14.2, 11.0, 7.9, 6.1, 5.0, 5.0]   # replace with the real numbers
colors   = ["#0072B2" if p in ("Widgets","Gadgets") else "#9a9a9a" for p in products]
fig, ax = plt.subplots(figsize=(9, 4.5))
ax.barh(products[::-1], share[::-1], color=colors[::-1])
for y, v in enumerate(share[::-1]):
    ax.text(v + 0.4, y, f"{v:.1f} %", va="center", fontsize=12)
ax.set_xlim(0, 32); ax.set_xticks([]); ax.spines[["top","right","bottom"]].set_visible(False)
ax.set_title("Widgets and Gadgets hold half the market; six products share the rest",
             loc="left", fontsize=16, weight="bold")
fig.text(0.125, 0.90, "Share of 2025 revenue, <market>, total <X> M€", fontsize=11, color="#555")
fig.text(0.125, 0.01, "Source: <report>, data as of <date>", fontsize=9, color="#777")
plt.tight_layout(); plt.show()
```
