# Questionnaire

Five `AskUserQuestion` calls per run (a sixth in reserve). Each call validates the
previous stage and opens the next, so validations cost no extra round trip. Each call
holds up to four questions; each question up to four options plus the automatic "Other".
Render the question text in the user's language; keep the mapping tags in English.

## Presenting stored defaults

- **EXACT / REUSE match**: the stored answer is option 1, labelled `<answer> (Recommended)`,
  description `Stored decision <id> (<date>, used <n>×): "<title>"`. The next options are
  the best catalog candidates.
- **ADAPT match**: same, but the description adds `differs in: <fields>` and the
  recommended flag goes to the catalog's best candidate when the archetype disagrees.
- **NONE**: the catalog's best candidate is `(Recommended)`.
- Four options max: top-3 catalog candidates + the stored answer; if the stored answer is
  among them, show four candidates.
- Options are built from the data profile and the catalog; never from hard-coded names.

## Call 1 · Stage 1: domain characterization

| id | question | options → mapping | default |
|---|---|---|---|
| S1.reader | Who will read the visualization? | up to four profiles from `user-profiles.md` (one line each: literacy, time, what they do) → `user.profile` | stored, else inferred from the prompt (see stage1-domain.md) |
| S1.mode | What is the goal? | explanatory: one message, static · analysis: verify, compare · exploration: find the questions, interactive → `problem.mode` | stored, else by profile `default_mode` |
| S1.question | Which question must the reader answer? | 3 candidate questions generated from `profile_data.py → suggested_abstractions`, each pre-tagged with an archetype and tasks; "Other" = free text → `task-mapping.md` | stored question first |
| S1.medium | Where will it be seen? | report/slide (static, print-safe) · web/notebook (interactive ok) · projector (large text, few marks) · phone → `constraints`, modifiers | stored; else explanatory → static, exploration → interactive, analysis → interactive when the profile's `interaction_tolerance` is medium/high, static otherwise |

Free text in S1.question: apply `task-mapping.md`, keep the two best mappings and show
them as the first two options of S2.task.

## Call 2 · Validate stage 1 + Stage 2: abstraction

| id | question | options |
|---|---|---|
| V1.confirm | One-line restatement: "<reader> wants to <question> in a <mode> chart for <medium>. Correct?" | Correct (Recommended) · the reader is wrong · the question is wrong · Other (free correction). Anything but "Correct" re-opens only that field in call 6. |
| S2.task | Abstract task | up to 3 bundles "<archetype name>: <low-level tasks> (<temporal tasks>)" → `problem.archetype`, `tasks` |
| S2.data | Keys, values and granularity | 3 abstractions from the profile, e.g. "key <time> (year, n) × <category> (n levels); value count of rows" · "key <category>; value sum(<measure>)" · "each row is an item; value <measure>" → `data` |
| S2.derive | Derived data and scope | totals as they are (Recommended when no denominator exists) · normalise by <denominator column> · filter/threshold <…> · other time grain (month/year) → `data.values[].derivation`, filters, normalisation |

If the question needs an attribute the profile does not contain, S2.data's first option
is "The dataset lacks <attribute>: stop and report" and the run ends with a design
document that states the gap (stage 2 validation failed).

## Call 3 · Validate stage 2 + Stage 3: encoding

| id | question | options |
|---|---|---|
| V2.confirm | Restates tasks, keys/values, derived data | Correct (Recommended) · change tasks · change data · Other |
| S3.idiom | Idiom | candidates from `match_decision.py` (stored first) and the catalog, each as "<name>: <mark> with <channels>; <task> immediate; limit: <…>" → `solution.idiom` |
| S3.color | Color plan | neutral + one accent on the item the takeaway is about (Recommended for explanatory) · qualitative Okabe-Ito ≤ 7 · sequential viridis for a quantity · diverging around <reference> → `solution.color` |
| S3.interaction | Views and interaction | one static view (Recommended if static medium) · one view + tooltips or a filter widget on <key> · two linked views: <idiom A> + <idiom B> with highlight both ways (multiform) · overview + detail with a brush · small multiples by <key> → `solution.interaction`, `solution.composition` |

S3.interaction offers a multi-view option only when the stage-2 tasks need it: two
encodings of the same items (locate in one, compare in the other), a key too long to
read in one frame (overview + detail), or a comparison across a category (small
multiples). The option text names the views, the relation and the cost ("two views at
half width each"). Tier EXACT/REUSE decisions that carry a `composition` block are
offered as stored.

## Call 4 · Stage 4: algorithm

| id | question | options |
|---|---|---|
| S4.library | Plotting library (asked every run) | Altair/Vega-Lite · matplotlib · Plotly; the project's stored library is Recommended; each description states installed / not installed and PNG renderer yes/no → `project.yaml.library` |
| S4.host | Output form | script saving PNG + HTML/JSON (Recommended) · Streamlit app · notebook cell → `host` |
| S4.validate3 | How to validate the encoding | rule checklist + render inspection (Recommended) · also run vis-value-critique (only if the sibling exists) · skip, I will review → `validation3` |
| S4.output | Where to write and whether to record | `<out_dir>/<slug>.py` + `<slug>_design.md`, record the decision (Recommended) · write files only · Other (path) → `out_dir`, `persist` |

## Call 5 · Validate stage 3 with the reader's eyes

After generating, running and rendering: show the PNG (or screenshot) and ask V3.accept:
Accept (Recommended) · change idiom · change color/text · change interaction. One
revision loop at most; a remaining disagreement goes to "open points".

## Call 6 · reserve

Only for: a non-"Correct" validation answer; a low-confidence free-text mapping; a
missing library (install with pip / switch library / write files without running); a run
failure that needs a decision.

## Autonomous mode

Triggered when the prompt says the user is away or not to ask, or when `AskUserQuestion`
is unavailable or fails. Every question takes its default (stored answer, else the
Recommended option, else the archetype/profile default). One exception: a stored or
recommended idiom that fails the stage-3 rule checklist for *this* data (scale, label
collisions, missing geometry) is replaced by the next catalog candidate, and the document
lists the replaced idiom under rejected alternatives with the rule that failed. The design document gets a
mandatory "Assumptions" section listing each question id, the assumed answer and the
reason (`stored <id>` / `catalog default` / `inferred from prompt`). The record is saved
with `--assumed` (status `candidate`), so a later interactive run offers it as default
while flagging "assumed, never confirmed".
