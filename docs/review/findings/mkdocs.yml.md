# Findings: mkdocs.yml

Open findings of `/docs-review`. Schema: `.claude/skills/doc-authoring/references/findings-schema.md`.

## S1 audit (2026-11-14)

Weight: light.

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| F2 | mkdocs.yml | 3 | 5 broken links | nothing handles the 7 links from docs/ to `../.claude/skills/*/SKILL.md` | `mkdocs build --strict` aborts on them; `.claude/skills/docs-site/SKILL.md:28-29` drops `--strict` — S3: S3 Q11 (user): build without --strict; record the 6 known BOARD_SETUP warnings in the docs-site skill; fix only GOAL_MUSTS link | wontfix | misleading | - |

Incidental: no `pymdownx.tasklist` (`- [ ]` renders as text) and no callout support (`> [!warning]` in the mineru guide). `make docs-build` runs without `--strict`. `docs-site` SKILL.md:28 names only BOARD_SETUP.md as the source of the warnings.

## S2 critique (2026-11-14)

The navigation as a reader sees it (no `nav:` key; read from the MkDocs source, not a build). 12 findings (0 breaks, 2 misleading, 10 cosmetic).

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
