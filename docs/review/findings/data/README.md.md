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
| C1 | data/README.md | 3 | readability/1 lede | the first line describes one file, not the folder | the folder also receives local M3Kang outputs (5) | verified | cosmetic | - |
| C2 | data/README.md | 5 | readability/8 form | names only train.jsonl and val.jsonl as local files | prepare_m3kang.py:145,152 also writes images/ and .ocr_cache.jsonl; index.db lives here too | verified | misleading | - |
| C3 | data/README.md | 5 | readability/6 steps | "writes ... here" with no command or link | steps at docs/BOARD_SETUP.md:713 | verified | cosmetic | - |
| C4 | data/README.md | 7-13 | readability/8 form | the format is only an example row; no field table | once the S1 F1 row goes, nothing describes the format | verified | misleading | S1 F1 |
| C5 | data/README.md | 7, 9-13 | readability/8 form | "One problem per line" but the example spans three lines | copied, it is invalid JSONL | verified | cosmetic | S1 F1 |
| C6 | data/README.md | 3, 15 | readability/5 jargon | "smoke tests", "OCR", "M3Kang" not explained | no GLOSSARY.md entry | verified | cosmetic | - |
| C7 | data/README.md | 3 | readability/10 duplication | the sample file description | docs/BOARD_SETUP.md:696 — S3: S3 Q23c (user): data/README.md is the canonical copy of the data format | verified | cosmetic | - |
| C8 | data/README.md | 5-13 | readability/10 duplication | the format block and its note | docs/BOARD_SETUP.md:777-787 — S3: S3 Q23c (user): data/README.md is the canonical copy of the data format | verified | cosmetic | S1 F1 |
| C9 | data/README.md | 15 | readability/10 duplication | the empty-options rule | .claude/skills/m3kang-copilot/SKILL.md:51 — S3: S3 Q23c (user): data/README.md is the canonical copy; link the m3kang-copilot skill for the copilot behavior | verified | cosmetic | - |
| C10 | data/README.md | 15 | readability/4 sentences | does not say what the copilot does with empty options | SKILL.md:51: the model sees only the question | verified | cosmetic | - |

S3 note (2026-11-14): the user settled F1: leave the record as it is (the organizers' own example). No history rewrite.
