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
