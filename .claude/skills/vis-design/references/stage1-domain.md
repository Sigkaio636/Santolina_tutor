# Stage 1 · Domain problem characterization

Goal: a one-paragraph problem statement that a target reader would recognise as theirs.
It fixes four things; everything downstream depends on them.

## 1. Reader (user profile)

Pick one profile from `user-profiles.md` (ids in `profiles/vocab.yaml → user_profiles`)
and any modifiers from `profiles/modifiers.yaml`. The profile carries capabilities
(literacy, time, interaction tolerance, working-memory budget, idioms that need no
explanation) and cognitive tasks (what they actually do with a chart). It becomes part of
the decision key, so the same problem for an executive and for an analyst are two
decisions.

Inference hints when the user does not say: report/slide/press → `general-public` or
`executive`; "para analizar", "explorar", "dashboard" → `data-analyst`; paper/thesis/
reviewer → `scientist-reviewer`; course/learning → `student-learner`; monitoring/alerts →
`operator-monitoring`; "divulgación", "artículo" → `communicator-journalist`; otherwise
`domain-expert`.

## 2. Mode

- `explanatory`: the result is known; one message; few variables; static or lightly
  interactive; takeaway title.
- `analysis`: hypotheses to verify; many variables; comparison; overview + detail.
- `exploration`: nothing known; the reader looks for the questions; interaction is the
  power source (overview → zoom/filter → details).

## 3. The domain question

Written in the reader's own words, in the user's language. Generate three candidates
from the data profile (`profile_data.py → suggested_abstractions`) so the user picks
rather than types; keep "Other" for free text and map it with `task-mapping.md`.
Each candidate is pre-tagged with the archetype it maps to. Known ambiguity to surface as
two options: "distribution of X" can mean the spread of a numeric X
(`distribution-single`) or how X splits across categories
(`compare-values-across-categories` / `part-to-whole-single`).

## 4. Medium and constraints

`static-only` (report, slide, print), `print-grayscale`, `mobile`, `projector`,
`interactive-required` (notebook, web app), `small-space` (dashboard tile), `exact-values`
(numbers will be quoted), `uncertainty` (intervals matter), `streamlit` (host),
`no-geometry-file` (regions without shapes), `few-categories-only`. Constraints exclude
idioms in the matcher and in the catalog ranking.

## Validation (threat: wrong problem)

Restate reader, mode, question and medium in one line and have the user confirm it at
the start of the stage-2 call. In autonomous mode write the restatement in the
"Assumptions" section and mark the validation "assumed". Munzner's stronger validations
(observe target users, measure adoption) are listed in the design document as "not done".

## What stage 1 hands to stage 2

`answers.problem {archetype, mode, statement, catalog_functions}`, `answers.user
{profile, modifiers}`, `answers.constraints`. The archetype is provisional until stage 2
confirms the abstraction.
