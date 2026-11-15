# Findings: README.md

Open findings of `/docs-review`. Schema: `.claude/skills/doc-authoring/references/findings-schema.md`.

## S1 audit (2026-11-14)

Weight: heavy.

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|

Incidental: lines 2-3 are Catalan, the rest English. The "other skills" table (164) leaves out `docs-review`.

## S2 critique (2026-11-14)

Type: explanation (project landing page), heavy. 32 findings (0 breaks, 6 misleading, 26 cosmetic).

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| C31 | README.md | 191-198 | readability/10 duplication | the credits list | docs/BOARD_SETUP.md:1261-1267 — S3 Q3 (user): canonical-copy rule (how-to/ for our flow, UNO_Q_BOARD_REFERENCE for specs, CLAUDE.md for the red line, GOAL_MUSTS for the checklist, README for credits); the other copy links to it — S3: README is the canonical copy (Q3); the other copy is BOARD_SETUP.md, read-only (Q1) | wontfix | cosmetic | - |

## Round 2026-11-15 (diff since sign-off b9c84d2 only, X5)

S1 docsauditor: 0 findings (link target exists; "not in prepare_m3kang.py yet" is true, laptop/prepare_m3kang.py:174).

S2 docs-critic: 5 findings (R1-R5, all cosmetic). S3: R5 settled by X15.

S4 (2026-11-15): R1-R5 fixed. The `laptop/` row is one phrase again; the
label-anchored option reader has its own row that links to
docs/OPTION_READER_GUIDE.md. No open finding in this round.

### S6 adversarial, round 1 (2026-11-15)

Lenses popular-science, slop-hunter, architect: all SHIP. Adjudicator: 3 MINOR, none material, plan empty.

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| A1 | README.md | 80 | 9 form | one description for two files | OPTION_READER_GUIDE.md:18-23 gives the split; one click away | wontfix | cosmetic | - |
| A2 | README.md | 79-80 | 10 duplication | both rows "read the options" | telling them apart needs the status X15 keeps in the guide | wontfix | cosmetic | - |
| A4 | README.md | 80 | 1 stale | guide path will move | docs/review/status.yml: OPTION_READER_GUIDE S3 "move to how-to/read-answer-options.md"; GLOSSARY.md:76 already names that path | open | misleading | - |

S6 fixes (user, 2026-11-15): A3 fixed (term links to GLOSSARY.md, X16). A4: keep today's path. The OPTION_READER_GUIDE session changes this one link target when it moves the guide (main session, 2026-11-15).

### S6 adversarial, round 2 (confirming, popular-science)

SHIP. A3 closed. Two new MINOR findings, out of bar, deferred (round cap reached):

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| A5 | GLOSSARY.md | 76 | 1 stale | the glossary entry the README links names `docs/how-to/read-answer-options.md`, which does not exist yet | `ls docs/how-to/`; closes when the guide moves (A4). GLOSSARY belongs to the main session | open | cosmetic | A4 |
| A6 | README.md | 80 | 9 links | the GLOSSARY.md link has no anchor; the term is at line 75 | GLOSSARY uses bold terms, no headings; same pattern as README.md:7 (X16) | wontfix | cosmetic | - |
