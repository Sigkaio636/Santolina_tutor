# Findings: docs/GOAL_MUSTS.md

Open findings of `/docs-review`. Schema: `.claude/skills/doc-authoring/references/findings-schema.md`.

## S1 audit (2026-11-14)

Weight: heavy. Language: Spanish.

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| F1 | docs/GOAL_MUSTS.md | 9 | 5 broken links | link to `../.claude/skills/publish-project/SKILL.md` | `mkdocs.yml:3` docs_dir; target outside it, breaks on the site | verified | breaks | - |
| F2 | docs/GOAL_MUSTS.md | 25, 92 | 8 contradictions | the predict.py contract applies only if the team picks Reason | `BOARD_SETUP.md:1091` every team's predict.py is scored | verified | misleading | - |
| F3 | docs/GOAL_MUSTS.md | 115 | 8 contradictions | the Qualcomm repo URL is pending | `BOARD_SETUP.md:3-5` gives it, at commit d6e3f1b | verified | misleading | - |
| F4 | docs/GOAL_MUSTS.md | 113 | 3 renamed | response language cited to CHALLENGE_CONTEXT §7 | it is at `CHALLENGE_CONTEXT.md:23` (§1) and :207 (§9) | verified | cosmetic | - |
| F5 | docs/GOAL_MUSTS.md | 35 | 3 renamed | the `*.gguf` exclusion cited to CLAUDE.md red line 1 | `CLAUDE.md:9-14` does not list `*.gguf`; it is in `BOARD_SETUP.md:1208`, `.gitignore:12` | verified | cosmetic | - |

Incidental: `mkdocs.yml` has no `pymdownx.tasklist`, so the `- [ ]` lists render as literal text on the site.

## S2 critique (2026-11-14)

Type: reference (checklist), heavy, Spanish. 23 findings (0 breaks, 3 misleading, 20 cosmetic).

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| C1 | docs/GOAL_MUSTS.md | 3-4 | readability/1 lede | "Lista única de lo que el reto pide al equipo." | does not name the challenge or the reader | verified | cosmetic | - |
| C2 | docs/GOAL_MUSTS.md | 1 | readability/3 headings | H1 "GOAL_MUSTS: qué hay que cumplir" | file name as title | verified | cosmetic | - |
| C3 | docs/GOAL_MUSTS.md | 103-105 | readability/3 headings | "Fuera de alcance de esta lista" | content repeats line 12 | verified | cosmetic | - |
| C4 | docs/GOAL_MUSTS.md | 105 | readability/4 sentences | "Si el jurado publica una rúbrica, sustituye a la sección 2." | subject is "el jurado" | verified | cosmetic | - |
| C5 | docs/GOAL_MUSTS.md | 3, 38-81 | readability/11 claims | "Cada ítem cita su fuente" | items in 40-47, 52-60, 65-80 cite none | verified | misleading | - |
| C6 | docs/GOAL_MUSTS.md | 64-73 | readability/11 claims | pitch and demo items cite "Deliverables" | they come from `BOARD_SETUP.md:1169-1185` | verified | cosmetic | - |
| C7 | docs/GOAL_MUSTS.md | 91 | readability/11 claims | translated quote shown as verbatim | uncited (`BOARD_SETUP.md:40`) | verified | cosmetic | - |
| C8 | docs/GOAL_MUSTS.md | 98 | readability/11 claims | "El ponente valora la documentación..." as fact | it is an interpretation (`RESUMEN_QUALCOMM_UNO_Q.md:129`) | verified | misleading | - |
| C9 | docs/GOAL_MUSTS.md | 93, 94, 98, 112 | readability/5 jargon | "la charla", "el vídeo", "el ponente" | never introduced; not in Fuentes | verified | misleading | - |
| C10 | docs/GOAL_MUSTS.md | 33, 41, 53, 54 | readability/5 jargon | "App Lab", "Bridge" | not explained | verified | cosmetic | - |
| C11 | docs/GOAL_MUSTS.md | 78 | readability/5 jargon | "22,5 % ... con opciones por OCR" | OCR not explained | verified | cosmetic | - |
| C12 | docs/GOAL_MUSTS.md | 70 | readability/4 sentences | "... conexión por USB con `adb forward`." | no verb; not explained | verified | cosmetic | - |
| C13 | docs/GOAL_MUSTS.md | 94, 95 | readability/5 jargon | "RAG con embeddings", "arnés" | not explained; calque | verified | cosmetic | - |
| C14 | docs/GOAL_MUSTS.md | 42 | readability/9 links | "los pasos 0 a 12" | does not say BOARD_SETUP; no link | verified | cosmetic | - |
| C15 | docs/GOAL_MUSTS.md | 12-115 | readability/9 links | sources as code spans and section names | not clickable | verified | cosmetic | - |
| C16 | docs/GOAL_MUSTS.md | 8 | readability/11 claims | BOARD_SETUP source "(Deliverables, pasos 14 y 15)" | 20-24 cite "The challenge" too | verified | cosmetic | - |
| C17 | docs/GOAL_MUSTS.md | 38-47 | readability/10 duplication | §1.3 | copy of `.claude/skills/publish-project/SKILL.md:40-48` — S3 Q3 (user): canonical-copy rule (how-to/ for our flow, UNO_Q_BOARD_REFERENCE for specs, CLAUDE.md for the red line, GOAL_MUSTS for the checklist, README for credits); the other copy links to it | verified | cosmetic | - |
| C18 | docs/GOAL_MUSTS.md | 48-60 | readability/10 duplication | §1.4 | `SKILL.md:56-69`, `BOARD_SETUP.md:1212-1225` — S3 Q3 (user): canonical-copy rule (how-to/ for our flow, UNO_Q_BOARD_REFERENCE for specs, CLAUDE.md for the red line, GOAL_MUSTS for the checklist, README for credits); the other copy links to it | verified | cosmetic | - |
| C19 | docs/GOAL_MUSTS.md | 62-73 | readability/10 duplication | §1.5 | `BOARD_SETUP.md:1169-1185` — S3 Q3 (user): canonical-copy rule (how-to/ for our flow, UNO_Q_BOARD_REFERENCE for specs, CLAUDE.md for the red line, GOAL_MUSTS for the checklist, README for credits); the other copy links to it | verified | cosmetic | - |
| C20 | docs/GOAL_MUSTS.md | 75-81 | readability/10 duplication | §1.6 | `SKILL.md:50-54` — S3 Q3 (user): canonical-copy rule (how-to/ for our flow, UNO_Q_BOARD_REFERENCE for specs, CLAUDE.md for the red line, GOAL_MUSTS for the checklist, README for credits); the other copy links to it | verified | cosmetic | - |
| C21 | docs/GOAL_MUSTS.md | 109-115 | readability/10 duplication | §4 open points | `RESUMEN_QUALCOMM_UNO_Q.md:140-147`, `CHALLENGE_CONTEXT.md:203-212` — S3 Q3 (user): canonical-copy rule (how-to/ for our flow, UNO_Q_BOARD_REFERENCE for specs, CLAUDE.md for the red line, GOAL_MUSTS for the checklist, README for credits); the other copy links to it | verified | cosmetic | - |
| C22 | docs/GOAL_MUSTS.md | 65-73, 85-99 | readability/2 one type | suggestions inside a reference of obligations | split or mark as suggestions — S3 Q4 (user): no split; the lede states the type and steps go to a final "What to try" section | verified | cosmetic | - |
| C23 | docs/GOAL_MUSTS.md | 66-69 | readability/8 form | pitch segments as checkboxes | a table | verified | cosmetic | C19 |
