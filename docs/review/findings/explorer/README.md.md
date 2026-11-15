# Findings: explorer/README.md

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

docsjanitor: every other S1 and S2 finding is fixed and deleted here. All findings fixed. "Prior solver" is not in the committed GLOSSARY yet (main session).

No open finding.

## S6 adversarial (2026-11-15)

Method (user choice): three hand-spawned devils-advocate adversarial reviewers (popular-science, slop-hunter, architect), each over the eight folder READMEs, one round; the scripted adversarial-review loop and the adjudicator agent did not run (adjudicated in the main thread). Verdicts: popular-science SHIP, slop-hunter SHIP, architect DO-NOT-SHIP (2 MAJOR, fixed).

Fixed in this README (S4/S5 pass after S6): **Ask the model** label quoted.

Rejected: -
