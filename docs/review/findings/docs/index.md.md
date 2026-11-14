# Findings: docs/index.md

Open findings of `/docs-review`. Schema: `.claude/skills/doc-authoring/references/findings-schema.md`.

## S1 audit (2026-11-14)

Weight: heavy.

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| F1 | docs/index.md | 5-6 | 8 contradictions | "this site has no problem text" | `docs/BOARD_SETUP.md:782-784` (served, not excluded) holds a problem record; see BOARD_SETUP F9 | verified | misleading | BOARD_SETUP F9 |
| F2 | docs/index.md | 24-25 | 8 contradictions | Papers list: pruning, quantization, inference, tutoring | `docs/vault/papers/README.md:1` and the vault also have benchmarks, finetuning_distillation, surveys, jev | verified | cosmetic | - |

Incidental: all 9 links resolve. Not listed in index.md: GOAL_MUSTS.md, SKILLS_GUIDE.html, review/index.md, the vault `_junctions.md` and `_synthesis.md` pages, the organizers' `.txt`. GUIA_RESTRICCIONES_UNOQ.html is Spanish and line 19 does not say so.

## S2 critique (2026-11-14)

Type: landing page, heavy. 9 findings (0 breaks, 1 misleading, 8 cosmetic).

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| C1 | docs/index.md | 3-6 | readability/1 lede | describes the project, not who the site is for or what to read first | rule 1 | verified | cosmetic | - |
| C2 | docs/index.md | 8-20 | readability/3 headings | "Start here" lists 7 pages in no order | the path is BOARD_SETUP 0-8, then deploy, then use (`deploy-copilot-on-board.md:7,11`) | verified | misleading | - |
| C3 | docs/index.md | 12-14, 17-20 | readability/10 duplication | four overlapping board and challenge pages, none marked canonical | `CHALLENGE_CONTEXT.md:39-50`, `GUIA_RESTRICCIONES_UNOQ.html:199` — S3 Q3 (user): canonical-copy rule (how-to/ for our flow, UNO_Q_BOARD_REFERENCE for specs, CLAUDE.md for the red line, GOAL_MUSTS for the checklist, README for credits); the other copy links to it | verified | cosmetic | - |
| C4 | docs/index.md | 22 | readability/5 jargon | heading "Vault" | Obsidian term, not explained | verified | cosmetic | - |
| C5 | docs/index.md | 26 | readability/5 jargon | "MinerU" | not said what it is | verified | cosmetic | - |
| C6 | docs/index.md | 26 | readability/8 form | the only entry with no description | 10-25 each give one | verified | cosmetic | - |
| C7 | docs/index.md | 4 | readability/5 jargon | "Datathon FME 2026" | not explained or linked | verified | cosmetic | - |
| C8 | docs/index.md | 17-18 | readability/9 links | "summary of the setup video" | no link to the video or its transcript — S3: S3 Q23d (user): link RESUMEN and the transcript (GitHub URL, since Q7 excludes the .txt from the site) | verified | cosmetic | mkdocs.yml F3 |
| C9 | docs/index.md | 3-5 | readability/10 duplication | lede text | nearly the same as `GLOSSARY.md:3` — S3 Q3 (user): canonical-copy rule (how-to/ for our flow, UNO_Q_BOARD_REFERENCE for specs, CLAUDE.md for the red line, GOAL_MUSTS for the checklist, README for credits); the other copy links to it | wontfix | cosmetic | - |
