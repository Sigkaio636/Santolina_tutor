# Decision record schema

A decision record stores one declared solution for one problem: the same (archetype,
mode, reader profile, data-shape signature) always gets the same solution unless the user
overrides it, which creates a new version. Seeds live in `decisions/seed/` (read-only);
project records in `<repo>/.claude/vis-decisions/` and take precedence.

## Key and signature

```
key(record) = (problem.archetype, problem.mode, user.profile, data.signature)
signature   = dataset_type | sorted("k:<type>:<band>") joined by "+" | sorted("v:<type>[:<semantics>]")
```

Role names, grains, `items` band, modifiers, constraints and the library are **not** part
of the key: they modulate the solution, they do not define the problem.

## Fields

```yaml
schema_version: 1
id: <archetype>--<variant>                 # seeds; project: p-<archetype>--<slug>-<yyyymmdd>
status: declared | candidate | superseded | deprecated   # candidate = assumed, never confirmed
title: <one line>
problem:
  archetype: <profiles/problems id>
  catalog_functions: [<data/catalog-functions.json ids>]
  statement: "<question template or the user's question>"
  mode: explanatory | analysis | exploration
  domain_examples: [<≥ 2 for seeds>]
user:
  profile: <profiles/users id>
  modifiers: [cvd | low-vision | mobile | print-grayscale | projector | novice-interaction | non-native-language]
tasks:
  why: {goal: present|discover|enjoy|produce, search: lookup|locate|browse|explore, query: identify|compare|summarize}
  low_level: [<Amar ids + compare, trend, gist>]
  temporal: [<Aigner ids>]
  shneiderman: [<ids>]
data:
  dataset_type: table | network | tree | field | geometry | text
  keys:   [{role, type, cardinality: <band>, grain?: <temporal grain>}]
  values: [{role, type, semantics?, derived?: true, derivation?: "<formula>"}]
  items: tiny | small | medium | large
  signature: "<computed>"
constraints: [static-only | interactive-required | print-grayscale | mobile | small-space | exact-values | uncertainty | streamlit | few-categories-only | no-geometry-file]
solution:
  idiom: <data/chart-catalog.json id>
  family: <vocab idiom_families>
  mark: point | line | area | rect | arc | text | geoshape | glyph | arrow
  encodings: [{attribute: <a declared role | derived | highlight | none>, channel: <vocab channels>, scale?: <vocab scale_types>, sort?, zero?, note?}]
  derived_data: ["<formula>", ...]
  ordering: "<rule>"
  color: {purpose: distinguish|encode-value|highlight|none, palette_type: qualitative|sequential|diverging|neutral-accent, suggested: [...], cvd_safe: bool, second_cue?: "<cue>", midpoint?: "<reference>"}
  text: {title: takeaway|descriptive|minimal, axis_units: bool, direct_labels: bool, annotations: [...], source_line: bool}
  interaction: {level: none|optional|required, default_state_answers_task: bool, intents: [<Yi ids>]}
  layout: {small_multiples: bool, facet_by: <role|null>, aspect: wide|tall|square}
  composition:            # optional; absent = one view. Not part of the match key.
    type: single | juxtapose | superimpose | small-multiples | overview-detail | focus-context | tabs
    relation: redundant | multiform | overview-detail | small-multiples | no-linkage
    data_sharing: all | subset | none
    encoding_sharing: same | different
    views: [{id: <name>, idiom: <catalog id>, role: overview|detail|focus|context|facet|layer|control|alternative|difference}]
    links: [{from: <view id>, to: <view id>, type: highlight|filter|navigation|details}]
  rejected_alternatives: [{idiom: <catalog id>, reason: "<why>", rule: <rule id>}]
  validation: {stage3_checks: [<rule ids>], critique_skill: optional|required|skipped}
  library_notes: {altair: "<hint>", matplotlib: "<hint>", plotly: "<hint>"}
rationale: >
  <why this encoding serves these tasks for this reader>
confidence: high | medium | low
provenance:
  origin: seed | project
  author: <who>
  created: <date>
  updated: <date>
  times_used: <int>
  last_used: <date|null>
  supersedes: <id|null>
  sources: ["<references>"]
```

## Composition (multi-view decisions)

`solution.idiom` stays the idiom of the primary view (or `overview_detail` /
`difference_view` when the composition itself is the idiom); `solution.composition`
lists every view and how they are coordinated. `records.validate_composition` checks the
enumerations (`view_compositions`, `view_relations`, `data_sharing`, `encoding_sharing`,
`view_roles`, `link_types` in `vocab.yaml`), that every type other than `single` has at
least two views with unique ids and catalog idioms, and that every link joins declared
views. The block does not enter the key: a record with and one without it for the same
problem, reader and data shape are the same decision slot, and the newer supersedes.
How to choose and implement a composition: `multi-view-recipes.md`.

## Life cycle

- `record_decision.py record.json` validates (vocab, catalog ids, archetype and profile
  ids, rule ids, signature) and writes `<project>/p-….yaml`; it never overwrites a file.
- Accepting a stored decision unchanged → `--touch <id>` (project records: usage
  counters; seeds: nothing).
- Changing the solution for the same key → new record with `--supersede <old id>`; the
  old project record becomes `superseded`; a seed is simply shadowed by key.
- Changing stage 1–2 answers → different key → new record; the old one stays valid.
- `--assumed` writes `status: candidate`; the matcher ranks `declared` above it.
- `project.yaml` holds `library`, `host`, `output_dir`, `disabled_seeds` (seed ids this
  project does not want offered).

## Validation rules (what `record_decision.py` rejects)

Unknown enumeration values; idioms not in the catalog; encodings whose `attribute` is
not a declared role (or `derived`, `highlight`, `none`); a stated signature that differs
from the computed one; seeds with fewer than two domain examples; unknown rule ids when
`encoding-essentials.md` is present.
