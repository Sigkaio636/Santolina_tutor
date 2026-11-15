# Findings: data/README.md

Open findings of `/docs-review`. Schema: `.claude/skills/doc-authoring/references/findings-schema.md`.

## S1 audit (2026-11-14)

Weight: light.

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| F1 | data/README.md | 10-12 | 12 M3Kang red line | the example row is an M3Kang problem record (not quoted here) | same record as `docs/BOARD_SETUP.md:782-784` (BOARD_SETUP F9); the samples use `sample-N` ids — S3 (user): leave the organizers' example record; no history rewrite | wontfix | breaks | - |

Incidental: line 5 leaves out `.ocr_cache.jsonl` and `images/`, which `laptop/prepare_m3kang.py:152,176` also write to data/.

## S2 critique (2026-11-14)

Type: reference, light. 10 findings (0 breaks, 2 misleading, 8 cosmetic).

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| C7 | data/README.md | 3 | readability/10 duplication | the sample file description | docs/BOARD_SETUP.md:696 — S3: S3 Q23c (user): data/README.md is the canonical copy of the data format — S3: data/README is canonical (Q23c); the other copy is BOARD_SETUP.md, read-only (Q1) | wontfix | cosmetic | - |
| C8 | data/README.md | 5-13 | readability/10 duplication | the format block and its note | docs/BOARD_SETUP.md:777-787 — S3: S3 Q23c (user): data/README.md is the canonical copy of the data format — S3: data/README is canonical (Q23c); the other copy is BOARD_SETUP.md, read-only (Q1) | wontfix | cosmetic | S1 F1 |

S3 note (2026-11-14): the user settled F1: leave the record as it is (the organizers' own example). No history rewrite.
