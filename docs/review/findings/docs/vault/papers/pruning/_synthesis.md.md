# Findings: docs/vault/papers/pruning/_synthesis.md

Open findings of `/docs-review`. Schema: `.claude/skills/doc-authoring/references/findings-schema.md`.

## S1 audit (2026-11-14)

Weight: heavy. Paper figures were checked for arithmetic and against other notes only: the PDFs are gitignored.

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| F1 | docs/vault/papers/pruning/_synthesis.md | 22-28, 415-420 | 5 broken links | PDF wikilinks | gitignored (.gitignore:207), excluded (mkdocs.yml:14) | verified | breaks | - |
| F2 | docs/vault/papers/pruning/_synthesis.md | 417, 419 | 5 broken links | note wikilinks `[[.../_synthesis\|...]]` | targets exist; no wikilink support, literal brackets on the site — S3 Q6 (user): convert wikilinks: PDFs to arXiv links, notes to relative links that cross-reference where needed | verified | misleading | - |
| F3 | docs/vault/papers/pruning/_synthesis.md | 263, 293, 317 | 8 contradictions | XSum drop tagged "25% layer removal" and "27.1% layers removed" | line 225 calls ~27% a share of parameters — S3: ShortGPT Table 6: 27.1% is a parameter share; 263, 293, 317 mislabel it as layers | verified | misleading | - |
| F4 | docs/vault/papers/pruning/_synthesis.md | 121, 301 | 8 contradictions | Phi-2 "2.8B" and "2.7B" | no note settles it — S3: each paper gives its own figure (SliceGPT 2.8B, Gromov 2.7B) | dismissed | cosmetic | - |
| F5 | docs/vault/papers/pruning/_synthesis.md | 89 | 8 contradictions | decode is memory-bound | `inference/_synthesis.md:76`, `quantization/_synthesis.md:79` say maybe compute-bound — S3: S3 Q15 (user): move to "Open questions": not measured on our board | verified | misleading | - |
| F6 | docs/vault/papers/pruning/_synthesis.md | 16, 203, 270-271, 343 | 8 contradictions | plans around Gemma 3 270M/1B as the deployed model | `config.env:12-15` Qwen3.5 0.8B Q8_0 — S3 Q2 (user): the fine-tune base is not chosen yet; say Qwen3.5 0.8B is deployed and Gemma 3 is one option being explored | verified | misleading | - |
| F7 | docs/vault/papers/pruning/_synthesis.md | 16, 269 | 7 terminology | "tutor" | `GLOSSARY.md:7-9` | verified | cosmetic | - |
| F8 | docs/vault/papers/pruning/_synthesis.md | 8-14 | 6 placeholder | blockquote "Changes to the proposed junctions" (process notes) | meta text, not research content — S3 Q8 (user): delete the "Changes to the proposed junctions" blocks; VERIFY markers go to a final "Open questions" list | verified | cosmetic | - |
| F9 | docs/vault/papers/pruning/_synthesis.md | 55-58, 97-101, 106-113 (repeats) | 10 formatting | lists with no blank line before; 2-space nesting | Python-Markdown needs both — S3: 213 raw "- " lines | verified | cosmetic | - |
| F10 | docs/vault/papers/pruning/_synthesis.md | 204-208 | 11 type-mixing | how-to recipe in an explanation note | `diataxis` — S3 Q4 (user): no split; the lede states the type and steps go to a final "What to try" section | verified | cosmetic | F6 |

## S2 critique (2026-11-14)

Type: explanation, heavy. 12 findings (0 breaks, 5 misleading, 7 cosmetic).

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| C1 | docs/vault/papers/pruning/_synthesis.md | 16 | readability/1 lede | starts "this folder mostly argues against pruning" | no purpose or reader | verified | misleading | F8 |
| C2 | docs/vault/papers/pruning/_synthesis.md | 6, 18 | readability/5 jargon | "junction" | defined only in `docs/vault/papers/README.md:10` | verified | misleading | - |
| C3 | docs/vault/papers/pruning/_synthesis.md | 16 | readability/4 sentences | 38 words, 3 claims | rule 4 | verified | cosmetic | - |
| C4 | docs/vault/papers/pruning/_synthesis.md | 16 | readability/4 sentences | about 43 words, nested conditions | rule 4 | verified | cosmetic | - |
| C5 | docs/vault/papers/pruning/_synthesis.md | 284, 330, 334, 338 | readability/5 jargon | "Martí's warning", "Martí's priority order" | never introduced (`CHALLENGE_CONTEXT.md:4`) | verified | misleading | - |
| C6 | docs/vault/papers/pruning/_synthesis.md | 16, 22, 53 | readability/5 jargon | "unstructured", "structured", "N:M", "2:4" | core taxonomy never defined | verified | misleading | - |
| C7 | docs/vault/papers/pruning/_synthesis.md | 16, 63 | readability/5 jargon | "FFN", "perplexity" | the main metric never explained | verified | misleading | - |
| C8 | docs/vault/papers/pruning/_synthesis.md | 57-171 | readability/5 jargon | Hessian, CSR, PCA, Taylor importance, RMSNorm, Lagrangian | no gloss | verified | cosmetic | - |
| C9 | docs/vault/papers/pruning/_synthesis.md | 11-356 | readability/5 jargon | RFT, "logit KD", mC4, QA/QG, Ans-F1 | not expanded | verified | cosmetic | - |
| C10 | docs/vault/papers/pruning/_synthesis.md | 28, 381 | readability/3 headings | "J7: Foundations" | does not say what it gives | verified | cosmetic | - |
| C11 | docs/vault/papers/pruning/_synthesis.md | 83-333 | readability/9 links | `CHALLENGE_CONTEXT.md` §2, "finetuning note, J2" | not links | verified | cosmetic | - |
| C12 | docs/vault/papers/pruning/_synthesis.md | 202 | readability/11 claims | "8 GB RTX 4060 (finetuning note, J2)" | circular; no source — S3: S3 Q16 (user): link CHALLENGE_CONTEXT "Team hardware" | verified | cosmetic | - |
