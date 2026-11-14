# Multiple views and dashboards

Read this when the artifact has more than one view: concatenated or layered charts,
small multiples, a dashboard, a Streamlit app with several charts, or one chart with
selections. It backs the rules CMP-05…13, INT-04, INT-09…13, SCL-08, CLT-05, COL-09.
Sources: Munzner 2014 (ch. 11–14: manipulate, facet, reduce, embed); Roberts 2007
(coordinated multiple views); Gleicher et al. 2011 (visual comparison); Cockburn,
Karlson & Bederson 2009 (overview+detail, zooming, focus+context); Becker & Cleveland
1987 (brushing); Becker, Cleveland & Shyu 1996 (trellis); Sun et al. 2022 (links across
views); Willett, Heer & Agrawala 2007 (scented widgets); Few 2006 (dashboards).

## 1. Why several views, and what they cost

Eyes beat memory: two things seen side by side are compared with eye movements, two
things seen one after the other with working memory (3–4 chunks, change blindness).
The cost is space (two juxtaposed views get half the area each), attention (where to
look first) and consistency (every difference between views is something to learn).

The three ways to show more than one thing, cheapest first:

| Option | Gains | Costs | Fails when |
|---|---|---|---|
| One view changed by interaction (filter, re-encode, popup) | full area per state | memory between states | the task is comparing states (EFF-20, CMP-08) |
| Superimpose (layers in one frame) | shared space, direct comparison | clutter, occlusion | > 2 area layers, > ~12 lines, layers not distinguishable (CMP-10) |
| Juxtapose (views side by side) | each view clean, eyes compare | ≈ 2× area, small views | views too small, scales differ, nothing links them (CMP-05, CMP-13) |

For comparison specifically (Gleicher): juxtapose, superimpose, or encode the
difference explicitly. When the task is the change, the third is usually the answer
(CMP-12).

## 2. What two views share (Munzner)

Ask of every pair of views: do they show the same items, and with the same encoding?

| | Same encoding | Different encoding |
|---|---|---|
| **All data shared** | redundant (rarely worth the space) | **multiform**: needs linked highlighting (CMP-09) |
| **Subset shared** | **overview and detail**: needs linked navigation | multiform overview and detail |
| **No data shared** | **small multiples**: needs shared scales and order | **no linkage**: not a dashboard (CMP-11) |

Then check what else is shared: scales (SCL-08), color meaning (COL-09, CLT-05),
ordering, the highlight color (INT-10), navigation (INT-13).

## 3. Partitioning (small multiples, trellis)

- Which attribute splits the data, into how many panels, in what order, in what grid.
  The pattern that one split hides another reveals (CMP-07): try the other split.
- Order panels by a statistic of the data (median, total), not alphabetically; a panel
  out of line with its neighbours is how anomalies are found.
- Same scales, same encoding, equal size, aligned, one shared legend; a few dozen
  panels at most. Small panels are the point; do not flag them for being small, flag
  them when the marks or labels inside are no longer legible.
- Grouped marks in one panel (compare across the inner key) vs one panel per level
  (compare within each level): choose by which comparison the task needs.

## 4. Coordination

- **Linked highlighting (brushing)**: a selection in one view marks the same items in
  the others, with the same color everywhere. The backbone of multiform views.
- **Linked filtering (cross-filtering)**: the other views show only the selection.
  Loses the context: shares, ranks and the rest of the distribution disappear
  (INT-11). Often the right design is highlight on top of a grey full-data layer.
- **Linked navigation**: zoom or pan one view and the views sharing that axis follow
  (INT-13). Overview and detail is the asymmetric case: a brush on the overview sets
  the detail's range, and the overview shows where the detail is.
- **Details on demand**: tooltip or a detail table driven by the selection; the
  default state must still answer the main question (INT-02, INT-03).
- **Links drawn across views** (Sun et al.): between items, between views or both;
  by shared color, connecting lines, bundling or enclosure. Lines across views cost
  clutter: use them for few items.
- A selection that changes nothing in another view is dead weight (INT-09).

## 5. Overview, detail, focus and context (Cockburn et al.)

- **Overview + detail**: two views, spatially separate; the overview must be an
  overview (aggregated, no detail) and show the detail's extent.
- **Zooming**: one view, temporally separate; geometric zoom magnifies, semantic zoom
  changes what is drawn at each level (labels appear, marks split).
- **Focus + context**: one view, the focus enlarged inside its context (fisheye,
  lenses, hyperbolic trees); distortion breaks length and position comparisons, so
  it suits topology and lookup, not magnitude reading.
- **Cues**: the context stays, the focus is highlighted (the cheapest option).

## 6. Controls

- Dynamic queries: sliders and checkboxes update the view at once (< 100 ms, INT-06).
- Scented widgets: the control shows the distribution behind it (a histogram on a
  slider, counts beside checkboxes), so the reader does not filter into emptiness
  (INT-12).
- Tabs and view switchers hide views behind memory: fine for alternative encodings of
  the same question, wrong when the reader must compare the tabs (EFF-20).
- Filters change the denominator: scales, color domains and bins must either stay
  fixed across states or say they changed (DAT-14).

## 7. Dashboard pass (run it after the per-view critique)

1. List the views and, for each pair that sits together, name the relation in the §2
   table. A pair with no relation is CMP-11.
2. For each stated task, trace the reader's path: where do they start, what do they
   select, where does the answer appear? Count the interactions (INT-02).
3. Check every selection has an effect elsewhere (INT-09) and one highlight color
   (INT-10); check filter vs highlight against the task (INT-11).
4. Check consistency: same field → same color, same order, same scale, same name in
   every view (CLT-05, COL-09, SCL-08).
5. Check the space budget: is each view legible at the size it gets; would a layer or
   an interaction have done the job of a view (CMP-13)? Does it fit one screen
   (ACC-03)?
6. Check the default state: with nothing selected, is the main question answered?

What the inspectors can and cannot see: `inspect_vegalite.py` reports selections that
no view reads, multiform concatenations with no shared selection, concatenated panels
of the same measure on independent scales, differing highlight colors and superimposed
area layers. Whether the linking serves the task, and anything wired in application
code (Streamlit callbacks, session state), you must establish by running it.
