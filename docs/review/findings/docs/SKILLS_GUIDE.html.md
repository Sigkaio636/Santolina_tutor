# Findings: docs/SKILLS_GUIDE.html

Open findings of `/docs-review`. Schema: `.claude/skills/doc-authoring/references/findings-schema.md`.

## S1 audit (2026-11-14)

Weight: heavy. Lines are HTML source lines.

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| F1 | docs/SKILLS_GUIDE.html | 116 | 8 contradictions | "26 project skills" | `.claude/skills/` has 27; the A to Z (574-627) lists 27 | verified | misleading | - |
| F2 | docs/SKILLS_GUIDE.html | 116 | 8 contradictions | the repo ships one agent, docs-auditor | `.claude/agents/` also has docs-critic (named at 388, 588) | verified | misleading | - |
| F3 | docs/SKILLS_GUIDE.html | 220 | 3 renamed | `santolina_tutor/modeling/predict.py` | `santolina_tutor/templates/modeling/predict.py` (`CLAUDE.md:38-39`) | verified | misleading | - |
| F4 | docs/SKILLS_GUIDE.html | 164, 202 | 8 contradictions | the guard checks git add/commit/push and gh pr | `.claude/hooks/m3kang-guard.py:191` also checks git send-pack | verified | cosmetic | - |
| F5 | docs/SKILLS_GUIDE.html | 381 | 8 contradictions | docs-review calls the module 7 skills, one per stage | `.claude/skills/docs-review/SKILL.md:19,22,23`: S3 uses module 3, S6 module 5, S7 is the user | verified | cosmetic | - |
| F6 | docs/SKILLS_GUIDE.html | 142 | 7 terminology | "the test set leaked into the prompt examples" | `GLOSSARY.md:43-45` Validation set; avoid "test set" | verified | misleading | - |
| F7 | docs/SKILLS_GUIDE.html | 137, 226 | 7 terminology | "per run" | `GLOSSARY.md:47-49` Experiment | verified | cosmetic | - |
| F8 | docs/SKILLS_GUIDE.html | 217 | 7 terminology | "the model" | `GLOSSARY.md:19-21` | verified | cosmetic | - |
| F9 | docs/SKILLS_GUIDE.html | 108-622 (plugin rows) | 3 renamed | plugin commands, agents and 13 lenses (v1.8.14) | `.claude/settings.json:10-14` enables the plugins; their files are user-level, outside the repo; the cache matches — S3: plugin cache v1.8.14 matches | dismissed | cosmetic | - |
| F10 | docs/SKILLS_GUIDE.html | 481 | 3 renamed | grounding, validate, update, process and pdf OCR need Python 3.12 exactly | only the grounding SKILL.md (user-level cache) says 3.12 — S3: grounding SKILL.md:62: every document-processing subcommand needs Python 3.12 | dismissed | misleading | - |
| F11 | docs/SKILLS_GUIDE.html | 118-119, 184, 339, 345-347, 414, 493, 500-505 | 3 renamed | built-in and account skills (code-review levels, simplify, dataviz, ...) | not in the repo; cannot be confirmed from it — S3: the session's skill list matches every row | dismissed | cosmetic | - |
| F12 | docs/SKILLS_GUIDE.html | 70-637 | 11 type-mixing | tutorial, reference tables and an A to Z index in one page | one document, one type (`diataxis`) — S3 Q4 (user): no split; the lede states the type and steps go to a final "What to try" section | verified | cosmetic | - |

Incidental: the 2026-11-14 claim of no branch protection (197) was not checked (needs gh).

## S2 critique (2026-11-14)

Type: tutorial (self-study guide), heavy. 24 findings (0 breaks, 2 misleading, 22 cosmetic).

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| C1 | docs/SKILLS_GUIDE.html | 72 | readability/1 lede | reads like a reference page | does not say it is a course or what the reader needs first | verified | cosmetic | - |
| C2 | docs/SKILLS_GUIDE.html | 192-497 | readability/3 headings | h3 "Predict" and "Reference" repeat in all 11 modules | rule 3 | verified | cosmetic | - |
| C3 | docs/SKILLS_GUIDE.html | 257, 355, 442 | readability/3 headings | "Review A/B/C" h3 nest under modules 3, 6, 9 | rule 3 | verified | cosmetic | - |
| C4 | docs/SKILLS_GUIDE.html | 75-181 | readability/3 headings | TOC labels differ from the headings | e.g. "7 Docs" vs "Documentation" | verified | cosmetic | - |
| C5 | docs/SKILLS_GUIDE.html | 99, 108, 139 | readability/5 jargon | "skill", "hook" used before defined; "agent", "plugin" never defined | rule 5 | verified | cosmetic | - |
| C6 | docs/SKILLS_GUIDE.html | 142-143 | readability/5 jargon | "with which lens?" | lenses explained at 317 | verified | cosmetic | - |
| C7 | docs/SKILLS_GUIDE.html | 116, 141, 142 | readability/5 jargon | "the CI job", "drift", "ablation table" | not explained | verified | cosmetic | - |
| C8 | docs/SKILLS_GUIDE.html | 168, 384 | readability/5 jargon | "ADR", "STE pass" | ADR never spelled out; STE only at 391 | verified | cosmetic | - |
| C9 | docs/SKILLS_GUIDE.html | 377-378 | readability/5 jargon | "the next `check`" | the script subcommand is not explained | verified | cosmetic | - |
| C10 | docs/SKILLS_GUIDE.html | 195, 202 | readability/5 jargon | "the split rule" | the table never names it | verified | cosmetic | - |
| C11 | docs/SKILLS_GUIDE.html | 100-107, 158 | readability/6 steps | Level 5 needs "the module's Trap" | "How to use" never mentions Traps | verified | cosmetic | - |
| C12 | docs/SKILLS_GUIDE.html | 231 | readability/5 jargon | "Keep a hold-out set." | `GLOSSARY.md:43-45`: val.jsonl already is — S3 Q9 (user): glossary: Copilot (tutor only in the papers' sense), Validation set (no dev/hold-out set), UNO Q = whole board, logit distillation, M3Kang, Token, Junction, Organizers/hidden test | verified | misleading | - |
| C13 | docs/SKILLS_GUIDE.html | 219 | readability/5 jargon | "Which file does the jury run" | `GLOSSARY.md:28` organizers' hidden test | verified | cosmetic | - |
| C14 | docs/SKILLS_GUIDE.html | 134, 518 | readability/5 jargon | "The model server", "The embeddings server" | `GLOSSARY.md:15-17` Model services | verified | cosmetic | - |
| C15 | docs/SKILLS_GUIDE.html | 166, 545 | readability/5 jargon | "the run" | `GLOSSARY.md:47-49` Experiment | verified | cosmetic | - |
| C16 | docs/SKILLS_GUIDE.html | 174 | readability/4 sentences | "It stops the command once" | `.claude/hooks/pr-gate.sh` blocks every try until fixed | verified | misleading | - |
| C17 | docs/SKILLS_GUIDE.html | 305-306 | readability/4 sentences | "the reviewer agent", "the skill" unnamed | named only at 313 | verified | cosmetic | - |
| C18 | docs/SKILLS_GUIDE.html | 102-105, 145 | readability/6 steps | placement and level rules unclear; no place to record a level | rule 6 | verified | cosmetic | - |
| C19 | docs/SKILLS_GUIDE.html | 165 | readability/6 steps | "Then run the evaluation." | no command; needs the board and data | verified | cosmetic | - |
| C20 | docs/SKILLS_GUIDE.html | 157, 355, 442 | readability/6 steps | Reviews skip modules 2 and 4; modules 9-11 have none | Level 4 unreachable | verified | cosmetic | - |
| C21 | docs/SKILLS_GUIDE.html | 214 | readability/9 links | organizers' repo name as plain text | `BOARD_SETUP.md:4` links it | verified | cosmetic | - |
| C22 | docs/SKILLS_GUIDE.html | 202-206 | readability/10 duplication | red-line note and guard rules | `CLAUDE.md:7-23` — S3 Q3 (user): canonical-copy rule (how-to/ for our flow, UNO_Q_BOARD_REFERENCE for specs, CLAUDE.md for the red line, GOAL_MUSTS for the checklist, README for credits); the other copy links to it | verified | cosmetic | - |
| C23 | docs/SKILLS_GUIDE.html | 218 | readability/10 duplication | "26 s vs 9 s, 22.5 % to 17.5 %" | `BOARD_SETUP.md:865-867` (8.7 s) and two more copies — S3 Q3 (user): canonical-copy rule (how-to/ for our flow, UNO_Q_BOARD_REFERENCE for specs, CLAUDE.md for the red line, GOAL_MUSTS for the checklist, README for credits); the other copy links to it | verified | cosmetic | - |
| C24 | docs/SKILLS_GUIDE.html | 543-551 | readability/8 form | answer chain aligned with spaces in a pre-wrap block | breaks on narrow screens | verified | cosmetic | - |
