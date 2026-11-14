---
name: vis-design
description: Design and generate a data visualization by walking Munzner's four-stage nested design process (domain problem characterization → data and task abstraction → visual encoding and interaction design → algorithm design), each stage validated, using stored reader profiles, problem archetypes, an 89-chart catalog (datavizcatalogue.com + Munzner/Wilke idioms) and a decision memory that proposes the same declared solution whenever the same problem, reader, task and data shape recur. Produces a design document plus runnable Altair, matplotlib or Plotly code (optionally a Streamlit app). Use it whenever the user wants a chart, plot, figure, dashboard panel, map or visualization made, designed, chosen or planned from a dataset or a question ("which chart should I use", "make me a visualization of", "diseña un gráfico", "how should I show X by Y"), even without the word "design"; also when they want to record or reuse a visualization decision. Not for critiquing an existing chart, which is the job of vis-value-critique.
---

# vis-design

You design a visualization the way the theory says it must be designed: as four nested
levels, each validated before the next is opened. The result is a **design document**
(the reasoning of all four stages, with rejected alternatives and validations) and
**runnable code** in the library the user picks. Decisions are remembered, so the same
problem for the same reader gets the same solution next time unless the user overrides it.

Read these before acting (Read tool, not shell cat):

| File | When |
|---|---|
| `references/design-process.md` | Always: the four stages, their threats and validations. |
| `references/questionnaire.md` | Always: the five calls, their questions, options, defaults and the autonomous rules. |
| `references/stage1-domain.md` … `stage4-algorithm.md` | While working each stage. |
| `references/task-mapping.md` | When the user types a free-text question. |
| `references/user-profiles.md`, `references/problem-archetypes.md` | To present reader and problem options; generated from `profiles/`. |
| `references/chart-catalog.md` | When presenting idiom candidates (fits, limits, scale, rules per chart). |
| `references/encoding-essentials.md` | Stage 3 and its validation; the rule ids cited everywhere. |
| `references/code-requirements.md`, `templates/` | Stage 4 code generation. |
| `references/multi-view-recipes.md` | When the answer needs several views (linked views, overview + detail, small multiples, a dashboard): choosing the composition, Altair and Streamlit recipes, its validation. |
| `references/design-doc-template.md`, `references/decision-schema.md`, `references/answers-schema.md` | When writing the document and the record. |

## Workflow

**0. Preflight (no questions).** Detect the user's language (dialogue and document in it;
file names, identifiers and record enumerations in English). Locate the data file and run
`python3 scripts/profile_data.py <file>` (attribute types, bands, date format, suggested
abstractions). Find the project store: `python3 scripts/record_decision.py` with no
arguments prints `project_dir` and `project.yaml` (library remembered). Run
`python3 scripts/find_sibling.py` (optional critique skill). Check which libraries import
(`altair`, `matplotlib`, `plotly`, `vl_convert`, `kaleido`, `streamlit`). Decide whether
you are in **autonomous mode** (the prompt says not to ask or the user is away, or
`AskUserQuestion` is unavailable): then every question takes its default and the document
gets an "Assumptions" section.

**1. Call 1 · domain.** Reader profile, mode, the question (three candidates generated from
the profile, "Other" mapped with `task-mapping.md`), medium. Write `answers.json`
(stages 1–2 so far) to the output folder.

**2. Call 2 · validate 1, abstract.** Restate stage 1 for confirmation; ask the abstract
task bundle, the keys/values/grain, the derived data and normalisation. If the question
needs an attribute the data lacks, say so, write the document with stage 2 marked FAILED
and stop: never force a chart on the wrong abstraction. Otherwise run
`python3 scripts/match_decision.py answers.json`: it returns the tier (EXACT / REUSE /
ADAPT / NONE), the stored decision to offer as default, and ranked catalog candidates.

**3. Call 3 · validate 2, encode.** Restate stage 2; ask idiom (stored decision first,
labelled with its id and date), color plan, interaction. Build the `solution` block from
the chosen options plus the stored record's details; list every candidate not chosen under
`rejected_alternatives` with the rule that rejects it. Check the palette with
`scripts/visdesign/colorcheck.py`.

**4. Call 4 · algorithm.** Library (always asked; the project's stored one is
Recommended; say whether each is installed and renders PNG), host, how to validate stage 3,
where to write and whether to record. Persist the library with
`python3 scripts/record_decision.py --set-library <lib> [--host …] [--output-dir …]`.

**5. Generate and run.** Fill the matching template in `templates/` (keep the structure;
write `derive()`, `takeaway()` and `build_chart()` from the record; the title is computed
from the data; `DATA_PATH` is script-relative because the checker and the inspectors run
the script with its own folder as cwd). Run `python3 scripts/run_check.py <slug>.py
--library <lib> --out-dir <dir> [--data …] [--streamlit app.py]` with absolute paths; if
its `inspector_ran_script` is false, the empty findings mean nothing: fix the path first. If it reports a missing module, ask in call 6
(install / switch / write only). If it reports blocking findings, fix the code and re-run
(twice at most). Look at the PNG, or serve the HTML (`python3 -m http.server`) and
screenshot it. No PNG renderer is not a failure: say what was rendered.

**6. Call 5 · validate 3 with the reader's eyes.** Show the render; accept or one change.

**7. Record and write.** Accepted stored decision unchanged → `record_decision.py --touch
<id>`. New or changed solution → complete the record (`solution`, `rationale`,
`confidence`) and run `record_decision.py record.json --dry-run` first: it returns the id
the record will get, so you can write it into the code docstring and the document before
the real save; then run it without `--dry-run` (`[--supersede <old>] [--assumed]`). Write
`<slug>_design.md` from `design-doc-template.md`.

## Rules that keep the design honest

- Validation folds into the next call; never more than six `AskUserQuestion` calls; never
  re-ask a confirmed field. Options come from the data profile and the catalog, never from
  hard-coded names.
- A stored decision is a default, not an order: the user sees it as "(Recommended)" with
  its id and can pick another option. Accepting it unchanged keeps the memory stable;
  changing it creates a new version that supersedes the old one for that key. If the
  default fails the stage-3 rule checklist for this data (too many items, colliding labels,
  no geometry), take the next catalog candidate and record the default as rejected with
  the rule, also in autonomous mode.
- Expressiveness before effectiveness: the data abstraction decides which channels are
  legal; the reader profile decides which idioms need no explanation; the rules in
  `encoding-essentials.md` decide what is rejected and why.
- Bars from zero, no dual axes, ≤ 7 hues, colorblind-safe with a second cue, sorted
  categories, titles with a computed takeaway, units, source and n. Never bars of means
  without the distribution; never random jitter; uncertainty in a form the reader can
  read, explained in words.
- Several views only when the task needs them, recorded as `solution.composition`:
  every selection changes another view, one highlight color everywhere, the same
  measure on a shared scale, the default state already answers the main question.
- Interaction only when the task needs it; the default state answers the main question.
- The code must run headless before the document claims it does; the document says what
  was validated by the user and what was assumed.

## Outputs

`<out_dir>/<slug>.py` (and `app.py` for Streamlit), the exported chart files,
`<out_dir>/<slug>_design.md`, `<out_dir>/answers.json`, and the project record under
`<repo>/.claude/vis-decisions/`. Quote the rendered title in the final message and name
the decision id (new, reused or superseding).

## Files

```
vis-design/
├── SKILL.md · README.md
├── references/   design-process, stage1–4, questionnaire, task-mapping, encoding-essentials,
│                 code-requirements, multi-view-recipes, answers-schema, decision-schema, design-doc-template,
│                 user-profiles (gen), problem-archetypes (gen), chart-catalog (gen)
├── profiles/     vocab.yaml, users/*.yaml (8), modifiers.yaml, problems/*.yaml (32)
├── data/         chart-catalog.json (89), catalog-functions.json (16), catalog-extraction.md
├── decisions/    README.md, index.json (gen), seed/*.yaml (48)
├── scripts/      profile_data.py, match_decision.py, record_decision.py, run_check.py,
│                 build_index.py, find_sibling.py, visdesign/ (library), tests/
├── templates/    chart_altair / dashboard_altair / chart_matplotlib / chart_plotly / app_streamlit
├── examples/     library-loans (a complete single-chart run), store-linked-views (two linked views),
│                 autonomous-run
└── evals/        five test cases
```
