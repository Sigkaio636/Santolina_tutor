# Findings: mkdocs.yml

Open findings of `/docs-review`. Schema: `.claude/skills/doc-authoring/references/findings-schema.md`.

## S1 audit (2026-11-14)

Weight: light.

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| F1 | mkdocs.yml | 39-56 | 5 broken links | the vault is published with no wikilink support | 243 Obsidian `[[...]]` links in 10 files under docs/vault/papers/; many point to PDFs excluded at line 14 — S3 Q6 (user): convert wikilinks: PDFs to arXiv links, notes to relative links that cross-reference where needed | verified | misleading | - |
| F2 | mkdocs.yml | 3 | 5 broken links | nothing handles the 7 links from docs/ to `../.claude/skills/*/SKILL.md` | `mkdocs build --strict` aborts on them; `.claude/skills/docs-site/SKILL.md:28-29` drops `--strict` — S3: S3 Q11 (user): build without --strict; record the 6 known BOARD_SETUP warnings in the docs-site skill; fix only GOAL_MUSTS link | wontfix | misleading | - |
| F3 | mkdocs.yml | 9-17 | 1 stale | `exclude_docs` keeps non-site files out | the video transcript `.txt` in docs/ and `docs/vault/papers/papers.tsv` are published, linked from nowhere — S3 Q7 (user): explicit default nav in reading order, both HTML pages in it, exclude .txt and papers.tsv, tasklist/tilde, callouts to admonitions, Review page explained | verified | misleading | - |

Incidental: no `pymdownx.tasklist` (`- [ ]` renders as text) and no callout support (`> [!warning]` in the mineru guide). `make docs-build` runs without `--strict`. `docs-site` SKILL.md:28 names only BOARD_SETUP.md as the source of the warnings.

## S2 critique (2026-11-14)

The navigation as a reader sees it (no `nav:` key; read from the MkDocs source, not a build). 12 findings (0 breaks, 2 misleading, 10 cosmetic).

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| C1 | mkdocs.yml | 7 | readability/8 form | with no `nav:`, pages are sorted by file name, not by the reading path | `index.md:10-16` gives another order — S3 Q7 (user): explicit default nav in reading order, both HTML pages in it, exclude .txt and papers.tsv, tasklist/tilde, callouts to admonitions, Review page explained | verified | misleading | - |
| C2 | docs/BOARD_SETUP.md | 1 | readability/3 headings | nav title "Datathon FME 2026: Qualcomm challenge" | `index.md:10` calls it "Board setup" — S3 Q7 (user): explicit default nav in reading order, both HTML pages in it, exclude .txt and papers.tsv, tasklist/tilde, callouts to admonitions, Review page explained | verified | misleading | - |
| C3 | docs/GOAL_MUSTS.md | 1 | readability/3 headings | nav title "GOAL_MUSTS: qué hay que cumplir" | the file name is the title — S3 Q5 (user): everything in English except the transcript and original sources; US spelling | verified | cosmetic | - |
| C4 | docs/GOAL_MUSTS.md, docs/RESUMEN_QUALCOMM_UNO_Q.md | 1 | readability/7 language | Spanish titles among English ones | which language is canonical? — S3 Q5 (user): everything in English except the transcript and original sources; US spelling | verified | cosmetic | - |
| C5 | docs/CHALLENGE_CONTEXT.md, docs/vault/papers/README.md, docs/RESUMEN_QUALCOMM_UNO_Q.md | 1 | readability/3 headings | nav titles of 10-14 words | differ from the index link text — S3 Q7 (user): explicit default nav in reading order, both HTML pages in it, exclude .txt and papers.tsv, tasklist/tilde, callouts to admonitions, Review page explained | verified | cosmetic | - |
| C6 | docs/vault/papers/*/ | - | readability/3 headings | one-page sections named after folders ("Jev", "Finetuning distillation") | the H1s say otherwise — S3 Q7 (user): explicit default nav in reading order, both HTML pages in it, exclude .txt and papers.tsv, tasklist/tilde, callouts to admonitions, Review page explained | verified | cosmetic | - |
| C7 | docs/vault/papers/*/_synthesis.md | 6 | readability/5 jargon | "synthesis by junction" in 9 nav titles | "junction" defined only in `_junctions.md:8` — S3 Q7+Q9 (user): nav titles and "junction" in the glossary | verified | cosmetic | - |
| C8 | docs/SKILLS_GUIDE.html | - | readability/9 links | orphan page: static HTML has no nav entry | only linked from `docs/review/index.md:19` — S3 Q7 (user): explicit default nav in reading order, both HTML pages in it, exclude .txt and papers.tsv, tasklist/tilde, callouts to admonitions, Review page explained | verified | cosmetic | - |
| C9 | docs/GUIA_RESTRICCIONES_UNOQ.html | - | readability/9 links | no nav entry, no sidebar or search | reachable only from `index.md:19` — S3 Q7 (user): explicit default nav in reading order, both HTML pages in it, exclude .txt and papers.tsv, tasklist/tilde, callouts to admonitions, Review page explained | verified | cosmetic | - |
| C10 | docs/review/index.md | 1-7 | readability/8 form | the internal review ledger is published | stage names not explained; publish or exclude? — S3 Q7 (user): explicit default nav in reading order, both HTML pages in it, exclude .txt and papers.tsv, tasklist/tilde, callouts to admonitions, Review page explained | verified | cosmetic | - |
| C11 | docs/vault/guides/mineru-ocr-papers.md | 1 | readability/8 form | a how-to under Vault > Guides | other how-tos are in docs/how-to/ — S3: S3 Q19 (user): move the MinerU guide to docs/how-to/ | verified | cosmetic | - |
| C12 | docs/vault/, docs/vault/guides/ | - | readability/3 headings | "Vault" and "Guides" sections have no index page | `navigation.indexes` (mkdocs.yml:23) shows nothing — S3 Q7 (user): explicit default nav in reading order, both HTML pages in it, exclude .txt and papers.tsv, tasklist/tilde, callouts to admonitions, Review page explained | verified | cosmetic | - |
