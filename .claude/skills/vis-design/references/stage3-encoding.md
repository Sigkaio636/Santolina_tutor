# Stage 3 · Visual encoding and interaction design

Goal: the `solution` block of a decision record: idiom, marks and channels per attribute,
ordering, scales, color plan, text plan, interaction plan, layout, and the alternatives
rejected with the rule behind each rejection.

## Choosing the idiom

1. Take `match_decision.py` output. Tier EXACT/REUSE: the stored solution is the
   recommended option; tier ADAPT: still recommended, but the differing slots are asked
   explicitly; tier NONE: use `catalog_candidates`.
2. Describe each candidate to the user as *mark + channels + which task becomes
   immediate + its main limit*, taken from `chart-catalog.md` (fits, limits, scalability,
   rules). Three or four options, the recommended one first.
3. Apply the archetype's `discouraged_idioms` and the profile's `avoid` /
   `needs_explanation` lists: an idiom the reader must learn is only acceptable for
   analysts and experts in analysis/exploration mode.
4. Constraints exclude: `static-only` excludes interaction-required idioms; `exact-values`
   excludes angle/area idioms; `no-geometry-file` excludes maps; `print-grayscale`
   requires luminance or position for the primary attribute.

## Encodings

One line per attribute in the design document: attribute → mark + channel → Mackinlay
rank for its type → expressiveness check. Rules of thumb from `encoding-essentials.md`:
the attribute the main task depends on gets position; ordered data on ordered channels;
nominal on hue or shape with ≤ 7 levels; size by area; no 3D; length marks from zero.

## Ordering, scales, layout

Purposeful order (by value for ranking, chronological for time, by total or clustering
for matrices); scales chosen for the meaningful effect size with a visible baseline;
small multiples with shared scales and equal panels, ordered by a statistic of the data
(median, total) rather than alphabetically; dual axes are discouraged (EXP-11): two
aligned panels or an index chart, unless the two axes are units of one quantity.

## Composition (one view or several)

Decide before the interaction plan, in this order: (1) one view, possibly changed by a
widget; (2) superimposed layers (at most two layers of area marks, about a dozen
lines, CMP-10); (3) juxtaposed views, which cost about twice the area but let eyes
compare (CMP-13). Then name what the views share: same data + different encoding is
multiform and needs linked highlighting (CMP-09); a subset in the same encoding is
overview + detail; different data in the same encoding is small multiples (which
attribute partitions, in what order, CMP-07); nothing shared is not one design
(CMP-11). When the task is the change between two states, plan an explicit difference
view (CMP-12). Record it as `solution.composition` (views, relation, links); recipes
and the validation of a composition are in `multi-view-recipes.md`.

## Color plan

Purpose first (distinguish / encode-value / highlight / none), then palette type
(qualitative ≤ 7 Okabe-Ito; sequential viridis-family; diverging with a stated midpoint;
neutral + accent for highlighting). Check with `scripts/visdesign/colorcheck.py`
(`check_palette`) that the chosen hues survive deuteranopia; always add a second cue.

## Text plan

Title (takeaway for explanatory, computed from the data in code), subtitle with period,
units and definition of the measure, axis titles with units, direct labels instead of
legends where possible, annotations with external context at the features the reader
will ask about, source and n in a footer.

## Interaction plan (Yi et al. intents)

`none` (static), `optional` (tooltips: abstract/elaborate), filter + select for
subsetting and highlighting, overview + detail with brushing and linked views for
exploration. Choose highlight or filter per link: highlighting keeps the context,
filtering removes it (INT-11). Every selection changes something in another view
(INT-09), with one highlight color everywhere (INT-10); views that share an axis share
zoom and pan; filter widgets show how much data each choice holds (INT-12); scales stay
fixed across selections or say that they move (DAT-14). The default state must already answer the main task (INT-02); the number of
interactions to answer the stated tasks is minimised; latency under 100 ms for filtering.
Animation is not a comparison tool; small multiples are.

## Validation (threat: wrong idiom)

Four checks, all recorded in the design document:

1. **Rule checklist**: every rule in the decision's `validation.stage3_checks` (and the
   idiom's `rules` in the catalog) marked pass/fail with evidence.
2. **Task-time table**: each task from stage 2 rated immediate / work / impossible with
   this encoding. A task the reader needs that is "impossible" sends the design back to
   step 1 of this stage. For a composition, also trace each task across the views
   (start view → selection → answer view) and count the interactions.
3. **Render inspection**: look at the rendered chart, its grayscale and its deuteranopia
   version (the sibling's `inspect_image.py` produces them when installed).
4. **Reader acceptance**: the user sees the render and accepts or asks for one change
   (one revision loop). Optional: run `/vis-value-critique` on the output and apply its
   Critical findings.

## Output

`solution` block as in `decision-schema.md`, plus `rejected_alternatives` with
`{idiom, reason, rule}` for every candidate the user saw and did not choose.
