# Findings: mkdocs.yml

Open findings of `/docs-review`. Schema: `.claude/skills/doc-authoring/references/findings-schema.md`.

## S1 audit (2026-11-14)

Weight: light.

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| F2 | mkdocs.yml | 3 | 5 broken links | nothing handles the 7 links from docs/ to `../.claude/skills/*/SKILL.md` | `mkdocs build --strict` aborts on them; `.claude/skills/docs-site/SKILL.md:28-29` drops `--strict` — S3: S3 Q11 (user): build without --strict; record the 6 known BOARD_SETUP warnings in the docs-site skill; fix only GOAL_MUSTS link | wontfix | misleading | - |

Incidental: no `pymdownx.tasklist` (`- [ ]` renders as text) and no callout support (`> [!warning]` in the mineru guide). `make docs-build` runs without `--strict`. `docs-site` SKILL.md:28 names only BOARD_SETUP.md as the source of the warnings.

## S2 critique (2026-11-14)

The navigation as a reader sees it (no `nav:` key; read from the MkDocs source, not a build). 12 findings (0 breaks, 2 misleading, 10 cosmetic).

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|

## Round 2026-11-15 — S1 audit (main session: `mkdocs build` into a scratch dir, exclude_docs/theme/extensions checked)

Scope: the user's priority (2026-11-15) puts the whole nav in scope (the 2026-11-14 sign-off covered an older nav); X5 diff-only applies to the 5 new nav lines, which are still in nav.

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| M1 | mkdocs.yml | 8-39 | 9 orphaned | 29 pages build but are not in nav | `mkdocs build` INFO list: 4 root docs (OCR_FAILURE_MODES, OPTION_READER_GUIDE, TOOL_CALLER_PROMPT, TUTOR_RESPONSE_TYPES), 17 experiments (one untracked: 2026-11-option-pipeline-speed.md), explanation/student-data-privacy, 4 how-tos (back-up-and-restore, install-decider-0.8b, run-teacher-app, use-student-app), models/ (2), reference/board-data-contract | verified | misleading | - |
| M2 | mkdocs.yml | 20 | 5 broken links | nav page LED_MATRIX_DESIGN.md links `../.claude/skills/...` | build WARNING (target not among documentation files); fixed by the LED repair | verified | cosmetic | - |
| M3 | mkdocs.yml | 8-39 | 1 stale | nav titles name pages that are being renamed or split (LED_MATRIX_DESIGN -> planned design + reference/led-matrix.md; INSTALL_DECIDER moved to how-to/install-decider-0.8b.md; OPTION_READER_GUIDE -> how-to/read-answer-options.md; OCR_FAILURE_MODES split) | review decisions of 2026-11-15 | verified | misleading | M1 |
| M4 | mkdocs.yml | 41-51 | - | exclude_docs, theme, plugins, extensions | all patterns match existing paths; the only build warnings are BOARD_SETUP's 6 known ones (wontfix, organizers' copy) and M2 | verified | cosmetic | - |

## Round 2026-11-15 — S2 critique (docs-critic, 28 findings: 5 misleading, 23 cosmetic; 11 decisions, 2 suspected)

Correction to M4: `exclude_docs` patterns `.gitkeep` and `vault/.trash/` match no file today (N23, harmless Obsidian guards).
Note: the 2026-11-14 "S2 critique" section claims 12 findings but its table has no rows.

| id | line | claim | status | severity |
|---|---|---|---|---|
| N1 | 7-39 | 29 orphan pages now, 33 after the decided renames/splits (= M1) | verified | misleading |
| N2 | 11-26 | no place for the student and teacher apps (5 orphan pages) | verified | misleading |
| N3 | 16 | intent router how-to filed under the copilot (X22) | verified | misleading |
| N4 | 16 | label omits "install" (H1 "How to install and use ...") | verified | cosmetic |
| N5 | 9-39 | top level mixes Diátaxis sections, topic sections and loose pages; no Explanation section | decision | cosmetic |
| N6 | 22-26 | "The challenge" after How-to/Reference; GOAL_MUSTS is the deliverables checklist | decision | cosmetic |
| N7 | 21 | one page, four names (GUIA_RESTRICCIONES_UNOQ) | verified | cosmetic |
| N8 | 21 | limits page under Reference next to the board reference it summarises | verified | cosmetic |
| N9 | 21, 27 | .html pages open without the site menu; label does not warn | suspected | cosmetic |
| N10 | 20 | LED design under Reference; split decided | verified | misleading |
| N11 | 24 | "final test" -> Hidden test | verified | cosmetic |
| N12 | 38 | "Jev" not in GLOSSARY | verified | cosmetic |
| N13 | 30 | "Questions across folders" vs H1 "Cross-folder junctions" | verified | cosmetic |
| N14 | 33 | "Inference on the board" narrows the folder | verified | cosmetic |
| N15 | 17 | MinerU how-to under How-to in nav, under Paper vault on index.md | decision | cosmetic |
| N16 | 9-39 | index.md is a second menu with other sections ("Start here"); signed | decision | cosmetic |
| N17 | - | no experiments section; H1 styles differ; call it "Experiment reports" (X19) | verified | cosmetic |
| N18 | 57 | 20 reports need topic groups (+ optional experiments/index.md) | decision | cosmetic |
| N19 | - | models/ records orphaned: Reference > Model records? | decision | cosmetic |
| N20 | - | TOOL_CALLER_PROMPT superseded: label it or leave out | decision | misleading |
| N21 | - | TUTOR_RESPONSE_TYPES (Spanish, unreviewed) | decision | cosmetic |
| N22 | 10-27 | UPPERCASE root files and Spanish file names; moving breaks links and signed docs | decision | cosmetic |
| N23 | 42, 44 | exclude_docs patterns that match nothing | verified | cosmetic |
| N24 | 57 | navigation.indexes may absorb "Vault index" | suspected | cosmetic |
| N25 | 3 | GLOSSARY.md outside docs_dir: 16 pages link to GitHub | decision | cosmetic |
| N26 | 10 | "Set up the board" hides that it is the organizers' guide with the rules | verified | cosmetic |
| N27 | 27, 39 | team pages (Skills guide, Review status) as top-level peers | decision | cosmetic |
| N28 | - | install-decider-0.8b needs a "not adopted" label | verified | cosmetic |

Proposed nav (S2): Home; Start here (GOAL_MUSTS, BOARD_SETUP "organizers' guide", deploy, use copilot); The challenge (PRACTICE_SET "practice set and hidden test", GUIA_RESTRICCIONES "standalone HTML", RESUMEN, CHALLENGE_CONTEXT); How-to guides > The copilot (try-prior-solver, read-answer-options, time-2b, install-decider-0.8b "not adopted") and > The student and teacher apps (use-student-app, run-teacher-app, use-decider-2b-router "install and use", back-up-and-restore); Reference (UNO_Q_BOARD_REFERENCE, reference/led-matrix, board-data-contract, Model records: models/*); Explanation (OCR_FAILURE_MODES, student-data-privacy, TUTOR_RESPONSE_TYPES "in Spanish", LED_MATRIX_DESIGN "planned, not built"); Experiment reports > Reading the answer options (10) / Copilot models and figure problems (5) / Intent router (conclusion first, rounds 1-3, messages method, TOOL_CALLER_PROMPT "superseded draft"); Paper vault (README, MinerU how-to, junctions, 8 syntheses); For the team (SKILLS_GUIDE, Review status). Pending files are merged only after their repairs land.

### S3 decisions (2026-11-15, user)

- N5, N6, N15, N16, N18, N19, N20, N21, N22, N27 -> X27: the proposed nav is accepted as a whole (Start here with GOAL_MUSTS first; How-to in two groups; Reference with Model records; Explanation; Experiment reports in three groups; MinerU under Paper vault; TOOL_CALLER_PROMPT as "(superseded draft)" last in the router group; TUTOR_RESPONSE_TYPES labelled "(in Spanish)" until its review; root files keep their paths; "For the team" last). `docs/index.md` reopens to match the menu.
- N25 (GLOSSARY outside docs_dir) -> not asked yet; GitHub links stay for now.
- Labels follow the final titles of the repaired docs (try-prior-solver is being renamed "measure the prior solver"). Apply after the renamed/split files exist (S4 of mkdocs.yml in the main session).
- Update (2026-11-15, X30): add `models/qwen35-tutor.md` to Reference > Model records ("qwen35-tutor (tutor model)").

## Round 2026-11-15, teammate commit 25f82e5 (X33): diff only

The teammate's nav adds every orphan page in a flat layout (How-to, Reference with model records, Explanation, Experiments, "Develop the project"). It differs from the accepted X27 grouping (Start here; How-to in two groups; Experiment reports in three groups; "For the team").

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| M5 | mkdocs.yml | Reference | 5 broken links | nav entry `TUTOR_RESPONSE_TYPES.md` | the file was split and removed (13b59c1); `mkdocs build` WARNING; TOOL_CALLER_PROMPT.md also links it | verified | breaks | - |
| M6 | mkdocs.yml | whole nav | 7 terminology | "Experiments" section; "Student-message classifier prompt" label; "Model record: the tutor (Qwen3.5 0.8B fine-tune)" | X19 "Experiment reports"; GLOSSARY Intent router, Tutor model; TOOL_CALLER is a superseded draft | verified | misleading | - |
| M7 | mkdocs.yml | whole nav | 8 form | teammate's flat nav vs accepted X27 nav | which one wins | decision | cosmetic | - |
- 2026-11-15: M5 fixed (nav entry repointed to the three split files; user approved). Review otherwise paused (X34).
