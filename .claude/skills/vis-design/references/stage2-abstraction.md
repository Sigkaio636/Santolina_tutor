# Stage 2 · Data and task abstraction

Goal: translate the domain question into generic data and generic tasks, so the idiom can
be chosen from the catalog and the decision can be matched against stored ones.

## Data abstraction

Run `scripts/profile_data.py <file>` first. It infers per column: type (categorical,
ordinal, quantitative, temporal, identifier, geo-code, text, boolean), distinct levels and
their band (one 1 · few 2–7 · some 8–30 · many 31–200 · huge > 200), missing share,
range, date format, and a role suggestion (key, value, identifier, drop). It also proposes
ready-made abstractions ("count per year × region", "sum of X per category", "distribution
of X").

Vocabulary (Munzner):

- **Dataset type**: table (items × attributes), network (nodes + links), tree, field
  (samples of a continuous domain), geometry (regions/points with shapes), text.
- **Key** = independent attribute that indexes items (time, category, location, node).
  **Value** = dependent attribute measured per key combination (count, amount, rate,
  share, score, position, duration, delta, weight).
- **Derived data**: anything computed before encoding: counts per key combination, sums,
  rates (value / denominator), shares (part / whole), deltas between periods, ranks,
  bins, normalisations, clusters. Every derived attribute gets a name and a formula in the
  design document, and the code's `derive()` uses the same names.
- **Granularity**: the temporal grain (day, month, year) and the aggregation level change
  what is visible (yearly bins merge events; daily noise hides trends). State the choice.
- **Items band** after derivation (tiny < 50, small < 1k, medium < 100k, large): decides
  whether overplotting, binning or pre-aggregation is needed.

The **signature** `dataset|k:type:band+…|v:type:semantics+…` is computed from this block
and is part of the decision key.

## Task abstraction

Three vocabularies, all in `profiles/vocab.yaml`:

- **Why** (Brehmer & Munzner): goal present / discover / enjoy / produce; search lookup /
  locate / browse / explore; query identify / compare / summarize.
- **Low-level tasks** (Amar, Eagan & Stasko): retrieve-value, filter, compute-derived,
  find-extremum, sort, determine-range, characterize-distribution, find-anomalies,
  cluster, correlate; plus compare, trend and gist as the explicit forms the profiles use.
  Rank them: which must be immediate, which may take work.
- **Temporal tasks** (Aigner et al.) when a key is temporal: existence, temporal-location,
  interval, pattern, rate-of-change, sequence, synchronization.
- **Shneiderman** when interaction exists: overview, zoom, filter, details-on-demand,
  relate, history, extract.

The archetype's `default_tasks` are the starting point; the user confirms or edits.

## Validation (threat: wrong abstraction)

- Every term of the domain question maps to an attribute or a derived attribute. If one
  is missing (the question mentions "cause" and no column carries it), stop: report the
  gap, propose where the attribute could come from, and do not force a chart on the
  attributes that exist. This is the most common upstream error and the cheapest to catch.
- The tasks are sufficient to answer the question (a "which region worsened" question
  needs rate-of-change, not only retrieve-value).
- The aggregation does not erase the phenomenon (a yearly total cannot show seasonality).
- Normalisation: totals by region or group almost always need a denominator (area,
  population, number of items); say explicitly when they do not.

## What stage 2 hands to stage 3

`answers.tasks`, `answers.data` (with signature), confirmed `answers.problem.archetype`.
Then run `scripts/match_decision.py answers.json`: its `defaults` block (from the matching
decision) and `catalog_candidates` feed the stage-3 options.
