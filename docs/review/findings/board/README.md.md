# Findings: board/README.md

Open findings of `/docs-review`. Schema: `.claude/skills/doc-authoring/references/findings-schema.md`.

## S1-S2

S1 and S2 were validated by the user on 2026-11-15; their fixed findings are deleted (S4). Open ones are in the S4 table.

## S3 decisions (2026-11-15)

User answers (one round for the eight folder READMEs):

- Q1 scope of S4: fix every verified misleading finding; for cosmetic ones fix links, terms and checks, and explain jargon by a link (GLOSSARY or guide), not new text. Padding items become wontfix. READMEs stay short.
- Q2 Tutor model source: the fine-tuned Tutor model is not published; without it the student app uses fixed texts (board C15, student_app C15).
- Q3 uncommitted work of other sessions (board/09_install_router.sh, math-router.service, config.env LLM_REPO): describe HEAD only. No 09 rows; student_app says the keyword rule labels messages and links the router how-to (board A2/C9/C21, student_app C5/C16 -> wontfix for now, re-audit when committed).
- Q4 duplication: each README keeps one copyable command and links the canonical guide; docs/reference/board-data-contract.md owns the schema rules; tests/README uses Files, Run, Docs (copilot C20, laptop C10, explorer C13, classroom C7/C14/C15, tests C11).

GLOSSARY.md is owned by the main session: missing HEAD entries (Tutor model, Intent router, Prior solver) and the dead read-answer-options.md pointer are reported there, not fixed here.

## S4 repair (2026-11-15)

docsjanitor: every other S1 and S2 finding is fixed and deleted here. A2/C9 and C21 wait for other sessions' uncommitted work (config.env, 09_install_router.sh): re-audit when it is committed (S3 Q3). C2, C3, C8, C14 (systemd, App Lab, llama.cpp, adb): no GLOSSARY entry; the main session owns GLOSSARY (S3 Q1: jargon by link, no new text).

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| A2 | board/README.md | 19 | 1 stale | 03 downloads the language model | true at HEAD; the uncommitted config.env empties LLM_REPO, then 03 fails. Tracked in findings/docs/how-to/install-decider-0.8b.md.md A1 | decision | breaks | - |
| C9 | board/README.md | 19 | readability/11 claims | 03 downloads the language model | same as A2 | decision | breaks | A2 |
| C21 | board/README.md | 14-51 | readability/8 form | 09 and math-router.service left out | untracked; add rows once committed | decision | misleading | - |
| C2 | board/README.md | 4 | readability/5 jargon | "systemd units" | not in GLOSSARY | wontfix | cosmetic | - |
| C3 | board/README.md | 4 | readability/5 jargon | "App Lab" | not in GLOSSARY | wontfix | cosmetic | - |
| C8 | board/README.md | 17 | readability/5 jargon | "llama.cpp" first use | no GLOSSARY entry | wontfix | cosmetic | - |
| C14 | board/README.md | 24 | readability/5 jargon | adb | no GLOSSARY entry | wontfix | cosmetic | - |

## S6 adversarial (2026-11-15)

Method (user choice): three hand-spawned devils-advocate adversarial reviewers (popular-science, slop-hunter, architect), each over the eight folder READMEs, one round; the scripted adversarial-review loop and the adjudicator agent did not run (adjudicated in the main thread). Verdicts: popular-science SHIP, slop-hunter SHIP, architect DO-NOT-SHIP (2 MAJOR, fixed).

Fixed in this README (S4/S5 pass after S6): Tutor model file named; TUTOR_PORT is not read by the student app; App Lab python/main.py runs on the Linux side and also reports tutor-writing state; duplicate 06-before-07 rule dropped.

Rejected: -
