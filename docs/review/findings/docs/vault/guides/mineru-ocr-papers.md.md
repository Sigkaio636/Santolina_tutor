# Findings: docs/vault/guides/mineru-ocr-papers.md

Open findings of `/docs-review`. Schema: `.claude/skills/doc-authoring/references/findings-schema.md`.

## S1 audit (2026-11-14)

Weight: heavy.

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| F1 | docs/vault/guides/mineru-ocr-papers.md | 4, 137, 162, 169 | 1 stale | the PDFs in docs/vault/papers/ are already there | gitignored (`.gitignore:207`); they come from `docs/vault/papers/download.sh`, which the guide never runs | verified | breaks | - |
| F2 | docs/vault/guides/mineru-ocr-papers.md | 9-12, 73, 79, 82 | 3 renamed | follows DigestBooks at ~/Documents/Digestive | a path on one machine, outside the repo — S3: S3 Q19 (user): delete the DigestBooks references | verified | misleading | - |
| F3 | docs/vault/guides/mineru-ocr-papers.md | 43, 72, 106 | 10 formatting | Obsidian callouts `> [!warning]` / `> [!note]` | `mkdocs.yml:39-46` has admonition only; they render as quotes — S3: built HTML shows blockquotes with literal [!warning] | verified | cosmetic | - |

Incidental: `.claude/skills/academic-paper-summarizer/scripts/install_mineru.sh:16-18` does not match Option A. External links and MinerU behavior not checked.

## S2 critique (2026-11-14)

Type: how-to, heavy. 19 findings (0 breaks, 2 misleading, 17 cosmetic).

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| C1 | docs/vault/guides/mineru-ocr-papers.md | 3-7 | readability/1 lede | does not say who it is for | rule 1 | verified | cosmetic | - |
| C2 | docs/vault/guides/mineru-ocr-papers.md | 3-5 | readability/4 sentences | 26 words, three ideas | rule 4 | verified | cosmetic | - |
| C3 | docs/vault/guides/mineru-ocr-papers.md | 6-7 | readability/4 sentences | no GPU and offline in one sentence | rule 4 | verified | cosmetic | - |
| C4 | docs/vault/guides/mineru-ocr-papers.md | 3, 6, 141 | readability/5 jargon | "vault", "Obsidian", "`pipeline` backend", "academic-paper-summarizer skill" | used before explained | verified | cosmetic | - |
| C5 | docs/vault/guides/mineru-ocr-papers.md | 18-19 | readability/4 sentences | parenthetical in a two-idea sentence | rule 4 | verified | cosmetic | - |
| C6 | docs/vault/guides/mineru-ocr-papers.md | 18, 33, 147 | readability/11 claims | 6.3 GB, 50 min, 35-37 s "on our machine" | no machine, date or source — S3: S3 Q19 (user): label "measured on one laptop, 2026-11" | verified | cosmetic | - |
| C7 | docs/vault/guides/mineru-ocr-papers.md | 44-45 | readability/4 sentences | relative clause nested in a parenthesis | rule 4 | verified | cosmetic | - |
| C8 | docs/vault/guides/mineru-ocr-papers.md | 63 | readability/6 steps | one 190-character command with three inline env vars | split or export first (as at 116-119) | verified | cosmetic | - |
| C9 | docs/vault/guides/mineru-ocr-papers.md | 66-68 | readability/6 steps | ModelScope variant given as three prose edits | no copyable command | verified | misleading | - |
| C10 | docs/vault/guides/mineru-ocr-papers.md | 56-104 | readability/6 steps | no check after Option A, Option B or mineru.json | 103-104 list the folders to `ls` | verified | cosmetic | - |
| C11 | docs/vault/guides/mineru-ocr-papers.md | 56, 72-76 | readability/8 form | untested Option A comes before tested Option B | reorder or mark A untested — S3: S3 Q19 (user): move the guide to docs/how-to/ and put tested Option B before Option A | verified | cosmetic | F2 |
| C12 | docs/vault/guides/mineru-ocr-papers.md | 85-101 | readability/6 steps | "create mineru.json" with a `/ABSOLUTE/PATH/TO/` placeholder | no copyable way to write it | verified | misleading | - |
| C13 | docs/vault/guides/mineru-ocr-papers.md | 140-142 | readability/4 sentences | 33 words, three ideas | rule 4 | verified | cosmetic | - |
| C14 | docs/vault/guides/mineru-ocr-papers.md | 151-152 | readability/6 steps | "look at the title and the abstract" | what a correct result looks like is not said | verified | cosmetic | - |
| C15 | docs/vault/guides/mineru-ocr-papers.md | 154-173 | readability/6 steps | step 5 has no check | the output path is in the table at 177-181 | verified | cosmetic | - |
| C16 | docs/vault/guides/mineru-ocr-papers.md | 175 | readability/3 headings | "6. Find the output" numbered but no action | reference | verified | cosmetic | - |
| C17 | docs/vault/guides/mineru-ocr-papers.md | 188 | readability/3 headings | "## Options" | vague; clashes with "Option A/B" | verified | cosmetic | - |
| C18 | docs/vault/guides/mineru-ocr-papers.md | 199 | readability/3 headings | "## Problems" | in this repo "problems" means M3Kang problems | verified | cosmetic | - |
| C19 | docs/vault/guides/mineru-ocr-papers.md | 201-203 | readability/10 duplication | repeats the warning at 43-48; "Someone" hides the actor | rule 10 | verified | cosmetic | - |
