# Findings: docs/vault/papers/quantization/_synthesis.md

Open findings of `/docs-review`. Schema: `.claude/skills/doc-authoring/references/findings-schema.md`.

## S1 audit (2026-11-14)

Weight: heavy. Paper figures were checked for arithmetic and against other notes only: the PDFs are gitignored.

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| F1 | docs/vault/papers/quantization/_synthesis.md | 19-52, 175, 222, 321, 333-340 | 5 broken links | PDF wikilinks | gitignored, excluded | verified | breaks | - |
| F2 | docs/vault/papers/quantization/_synthesis.md | 79, 121, 163, 222, 278, 317, 333-340 | 5 broken links | note wikilinks | no wikilink support — S3 Q6 (user): convert wikilinks: PDFs to arXiv links, notes to relative links that cross-reference where needed | verified | misleading | - |
| F3 | docs/vault/papers/quantization/_synthesis.md | 79 | 8 contradictions | A53 "reportedly" lacks SDOT/UDOT, VERIFY | `CHALLENGE_CONTEXT.md:60,209`, `UNO_Q_BOARD_REFERENCE.md:309,466` confirmed | verified | misleading | - |
| F4 | docs/vault/papers/quantization/_synthesis.md | 88, 119 | 8 contradictions | activations: one scale per block of 32 (CHALLENGE_CONTEXT §4) | `CHALLENGE_CONTEXT.md:92-93` gives 32 only for Q4_0 weights — S3: at 2cbe0ec activations use Q8_0 blocks of 32 only for Q4_0/Q8_0 weights; K-quants use Q8_K blocks of 256 | verified | cosmetic | - |
| F5 | docs/vault/papers/quantization/_synthesis.md | 11, 120 | 3 renamed | cites "the brief" | no repo doc is a brief; `CHALLENGE_CONTEXT.md:98` — S3: S3 Q23b (user): "the brief" is CHALLENGE_CONTEXT.md | verified | cosmetic | - |
| F6 | docs/vault/papers/quantization/_synthesis.md | 11, 48 | 8 contradictions | J3 evidence "over nine papers" | the J3 row lists ten — S3: the J3 row lists ten papers | verified | cosmetic | - |
| F7 | docs/vault/papers/quantization/_synthesis.md | 16, 161-162 | 8 contradictions | recommendations for Gemma 3; the shipped model not addressed | `config.env:12-15` Qwen3.5 0.8B Q8_0 — S3 Q2 (user): the fine-tune base is not chosen yet; say Qwen3.5 0.8B is deployed and Gemma 3 is one option being explored | verified | misleading | - |
| F8 | docs/vault/papers/quantization/_synthesis.md | 16 | 7 terminology | "UNO Q tutor" | `GLOSSARY.md:7-9` | verified | cosmetic | - |
| F9 | docs/vault/papers/quantization/_synthesis.md | 16, 77-78, 120-122, 161, 201-213, 241 | 6 placeholder | inline "VERIFY" markers | open questions the repo cannot settle — S3 Q8 (user): delete the "Changes to the proposed junctions" blocks; VERIFY markers go to a final "Open questions" list | verified | cosmetic | - |
| F10 | docs/vault/papers/quantization/_synthesis.md | 8-14 | 6 placeholder | blockquote "Changes to the proposed junctions" | meta text — S3 Q8 (user): delete the "Changes to the proposed junctions" blocks; VERIFY markers go to a final "Open questions" list | verified | cosmetic | - |
| F11 | docs/vault/papers/quantization/_synthesis.md | 59-60, 174-175, 182-183 (repeats) | 10 formatting | lists with no blank line before | Python-Markdown — S3: 147 raw "- " lines | verified | cosmetic | - |
| F12 | docs/vault/papers/quantization/_synthesis.md | 309-321 | 11 type-mixing | recipe and checklist in an explanation note | `diataxis` — S3 Q4 (user): no split; the lede states the type and steps go to a final "What to try" section | verified | cosmetic | F7 |

## S2 critique (2026-11-14)

Type: explanation, heavy. 12 findings (0 breaks, 4 misleading, 8 cosmetic).

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| C1 | docs/vault/papers/quantization/_synthesis.md | 16 | readability/1 lede | starts "For the UNO Q tutor, this folder says..." | no purpose or reader | verified | misleading | F10 |
| C2 | docs/vault/papers/quantization/_synthesis.md | 6, 42 | readability/5 jargon | "junction" | defined only in `docs/vault/papers/README.md:10` | verified | misleading | - |
| C3 | docs/vault/papers/quantization/_synthesis.md | 16 | readability/4 sentences | about 34 words | rule 4 | verified | cosmetic | - |
| C4 | docs/vault/papers/quantization/_synthesis.md | 16 | readability/4 sentences | about 45 words, 2 reasons + 2 recommendations | rule 4 | verified | cosmetic | - |
| C5 | docs/vault/papers/quantization/_synthesis.md | 12-13, 20, 46 | readability/5 jargon | PTQ, QAT | never expanded | verified | misleading | - |
| C6 | docs/vault/papers/quantization/_synthesis.md | 10, 47, 99, 109 | readability/5 jargon | W4A8, W8A8, W4A4KV4, A16W4 | notation never explained | verified | misleading | - |
| C7 | docs/vault/papers/quantization/_synthesis.md | 58, 77, 106 | readability/5 jargon | per-tensor/channel/token, "g128", "RTN" | g128 unexplained; RTN not tied to 65 | verified | cosmetic | - |
| C8 | docs/vault/papers/quantization/_synthesis.md | 16, 77, 120 | readability/5 jargon | `llama-imatrix`, Q4_K_M | explained only at 120, 77 | verified | cosmetic | - |
| C9 | docs/vault/papers/quantization/_synthesis.md | 64, 113, 262 | readability/5 jargon | mAP, MGSM, TPOT | not expanded | verified | cosmetic | - |
| C10 | docs/vault/papers/quantization/_synthesis.md | 34, 90, 187 | readability/5 jargon | "incoherent", "Hadamard", "E8 lattice", "Pareto-optimal" | no gloss | verified | cosmetic | - |
| C11 | docs/vault/papers/quantization/_synthesis.md | 10-212 | readability/9 links | "CHALLENGE_CONTEXT §4", "BOARD_SETUP §4" | no path, no link | verified | cosmetic | - |
| C12 | docs/vault/papers/quantization/_synthesis.md | 222 | readability/4 sentences | about 40 words, nested parentheses | rule 4 | verified | cosmetic | - |
