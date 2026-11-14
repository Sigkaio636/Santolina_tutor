# Findings: CLAUDE.md

Open findings of `/docs-review`. Schema: `.claude/skills/doc-authoring/references/findings-schema.md`.

## S1 audit (2026-11-14)

Weight: light.

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| F1 | CLAUDE.md | 13-17 | 1 stale | m3kang-guard blocks any git/gh call carrying "problem images" | `.claude/hooks/m3kang-guard.py:31-36` has no image pattern; images are caught only under data/ — S3: no image pattern; PNGs outside data/ pass the hook | verified | misleading | - |

## S2 critique (2026-11-14)

Type: reference (agent instructions), light. 11 findings (0 breaks, 4 misleading, 7 cosmetic).

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| C1 | CLAUDE.md | 1-3 | readability/1 lede | no lede before "Red lines" | does not say these are standing agent instructions | verified | cosmetic | - |
| C2 | CLAUDE.md | 9-14 | readability/8 form | a 40-word sentence mixes globs with nouns without a path | real paths: data/images/, data/.ocr_cache.jsonl (laptop/prepare_m3kang.py:145,152) | verified | misleading | S1 F1 |
| C3 | CLAUDE.md | 10-11 | readability/4 sentences | "anything derived from them" is open-ended | line 22 allows results CSVs without problem text — S3 Q10 (user): CLAUDE.md defines problem text and derived data, the validated rule and the full board map | verified | misleading | - |
| C4 | CLAUDE.md | 11-12 | readability/4 sentences | `*.jsonl` after the data/ exception seems to ban sample_problems.jsonl | the guard exempts it (.claude/hooks/m3kang-guard.py:37-38) | verified | cosmetic | - |
| C5 | CLAUDE.md | 19-20 | readability/4 sentences | "stop": the push or the whole task? passive hides who rewrites | - | verified | cosmetic | - |
| C6 | CLAUDE.md | 21 | readability/5 jargon | "problem text" not defined (options, solutions?) | README.md:182 uses it undefined too — S3 Q10 (user): CLAUDE.md defines problem text and derived data, the validated rule and the full board map | verified | cosmetic | - |
| C7 | CLAUDE.md | 29-31 | readability/10 duplication | board-side list leaves out eval.py, build_index.py, explorer/ | README.md:92-97,109-111 — S3 Q10 (user): CLAUDE.md defines problem text and derived data, the validated rule and the full board map | verified | misleading | - |
| C8 | CLAUDE.md | 30-31 | readability/8 form | skills given as a glob plus bare names | give all as paths | verified | cosmetic | - |
| C9 | CLAUDE.md | 36-37 | readability/4 sentences | "Only the user marks a stage validated" can read as forbidding the agent's `set ... validated` after the user's answer | .claude/skills/docs-review/SKILL.md:47,54-55 — S3 Q10 (user): CLAUDE.md defines problem text and derived data, the validated rule and the full board map | verified | misleading | - |
| C10 | CLAUDE.md | 38-39 | readability/10 duplication | the predict.py rule | README.md:106-108 (same decision as README C30) — S3 Q3 (user): canonical-copy rule (how-to/ for our flow, UNO_Q_BOARD_REFERENCE for specs, CLAUDE.md for the red line, GOAL_MUSTS for the checklist, README for credits); the other copy links to it | verified | cosmetic | - |
| C11 | CLAUDE.md | 9 | readability/5 jargon | "M3Kang" with no glossary entry | GLOSSARY.md:3 | verified | cosmetic | - |
