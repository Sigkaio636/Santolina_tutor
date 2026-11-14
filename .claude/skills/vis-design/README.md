# vis-design

A Claude Code skill that **designs and generates** a data visualization by walking
Munzner's nested design process: domain problem characterization → data and task
abstraction → visual encoding and interaction design → algorithm design, each stage
validated. It ships reader profiles (capabilities and cognitive tasks), problem
archetypes, an 89-chart catalog (60 from datavizcatalogue.com, 29 standard idioms the site
lacks) and a decision memory: once a (problem, reader, task, data shape) has a declared
solution, the same solution is proposed again. The sibling skill `vis-value-critique`
critiques charts; this one makes them.

## Install

Copy this folder to `<repo>/.claude/skills/vis-design/` (one project) or
`~/.claude/skills/vis-design/` (all projects). Nothing in it depends on the repository.
Trigger it by asking for a chart, plot, figure, map or dashboard panel to be designed or
made, or with `/vis-design`.

## Requirements

Python 3.10+ with **PyYAML** (records and profiles are YAML). Optional: `pandas`
(xlsx/parquet profiling and the generated code), `altair` + `vl_convert`, `matplotlib`,
`plotly` + `kaleido`, `streamlit`. The scripts say which are missing. No network access.

## How a run works

1. `scripts/profile_data.py data.csv` → attribute types, cardinality bands, date format,
   suggested abstractions.
2. Five `AskUserQuestion` calls (`references/questionnaire.md`), each validating the
   previous stage; stored decisions appear as the recommended option with their id.
3. `scripts/match_decision.py answers.json` → stored decision (project store beats seeds)
   and ranked catalog candidates.
4. Code from `templates/`, executed by `scripts/run_check.py` (headless run, outputs,
   optional sibling inspectors, Streamlit smoke test).
5. `scripts/record_decision.py` persists the decision under `<repo>/.claude/vis-decisions/`
   and the library choice in `project.yaml`.
6. The design document (`references/design-doc-template.md`) and the code are written.

## Decision memory

- Seeds: `decisions/seed/*.yaml` (42, at least one per archetype), read-only.
- Project records: `<repo>/.claude/vis-decisions/p-*.yaml`, precedence over seeds, versioned
  with `supersedes`; `project.yaml` keeps the library/host/output_dir and `disabled_seeds`.
- Key = (archetype, mode, profile, data-shape signature); see
  `references/decision-schema.md`.

## Layout

```
SKILL.md                     workflow
references/                  theory per stage, questionnaire, task mapping, essentials, schemas, templates of the document
profiles/vocab.yaml          every enumeration (types, bands, tasks, channels, constraints, …)
profiles/users/              8 reader profiles      profiles/modifiers.yaml   cross-cutting modifiers
profiles/problems/           32 problem archetypes
data/chart-catalog.json      89 charts with site facts, paraphrased summaries and our characterization
data/catalog-functions.json  16 functions → charts → archetypes
decisions/seed/              48 seed decisions      decisions/index.json      generated
scripts/                     profile_data, match_decision, record_decision, run_check, build_index, find_sibling
scripts/visdesign/           vocab, shape, records, store, scoring, catalog, colorcheck, vendor/ (color helpers)
scripts/tests/               unittest suite with synthetic fixtures
templates/                   chart_altair / chart_matplotlib / chart_plotly / app_streamlit skeletons
examples/                    library-loans (single chart), store-linked-views (two linked views), autonomous-run
evals/                       five cases in the `claude plugin eval` layout
```

## Maintaining

- Edit YAML/JSON sources, never the generated `references/user-profiles.md`,
  `problem-archetypes.md`, `chart-catalog.md` or `decisions/index.json`; then run
  `python3 scripts/build_index.py` (regenerate) and `python3 scripts/build_index.py --check`
  (validate cross-references, word caps, seeds).
- Add a seed: copy the closest one, keep the enumerations within `profiles/vocab.yaml`,
  make its key unique, run `--check`.
- Add a chart: add an entry to `data/chart-catalog.json` with the `ours` block; the site
  facts fields may be empty for a supplement entry.
- Run the tests: `python3 -m unittest discover -s scripts/tests`.
- Portability check: `grep -ri "<your dataset's column names>" SKILL.md references profiles
  decisions templates` must return nothing.
- Package: `python -m scripts.package_skill <this folder>` from the skill-creator skill.
