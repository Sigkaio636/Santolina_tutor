# Findings: docs/how-to/deploy-copilot-on-board.md

Open findings of `/docs-review`. Schema: `.claude/skills/doc-authoring/references/findings-schema.md`.

## S1 audit (2026-11-14)

Weight: heavy.

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|

## S2 critique (2026-11-14)

Type: how-to, heavy. 21 findings (0 breaks, 4 misleading, 17 cosmetic).

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| C16 | docs/how-to/deploy-copilot-on-board.md | 103 | readability/6 steps | `build_index.py` with no check or duration | it prints "Wrote data/index.db ... in N s" (`build_index.py:40`) — S3: S4: the check is added; no build_index.py duration is measured on our board, so none is written | wontfix | cosmetic | - |
