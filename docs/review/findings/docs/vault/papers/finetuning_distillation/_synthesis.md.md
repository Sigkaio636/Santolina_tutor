# Findings: docs/vault/papers/finetuning_distillation/_synthesis.md

Open findings of `/docs-review`. Schema: `.claude/skills/doc-authoring/references/findings-schema.md`.

## S1 audit (2026-11-14)

Weight: heavy (explanation). Paper figures were checked for arithmetic and against other notes only: the PDFs are gitignored.

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| F1 | docs/vault/papers/finetuning_distillation/_synthesis.md | 20-23, 81, 293-298 | 5 broken links | paper refs are `[[<slug>.pdf\|...]]` wikilinks | `mkdocs.yml:39-40` no wikilink support (literal text); `*.pdf` excluded (14) and gitignored | verified | breaks | - |
| F2 | docs/vault/papers/finetuning_distillation/_synthesis.md | 14, 224 | 7 terminology | "tutor" | `GLOSSARY.md:7-9` Copilot | verified | cosmetic | - |
| F3 | docs/vault/papers/finetuning_distillation/_synthesis.md | 160, 217 | 8 contradictions | 5 tok/s × 60 s ≈ 300 output tokens | reading the problem takes 7-25 s (`BOARD_SETUP.md:499`); `jev/_synthesis.md:92` 150-250 tokens | verified | misleading | - |
| F4 | docs/vault/papers/finetuning_distillation/_synthesis.md | 81 | 8 contradictions | "Check in Gemma 3 report" for the 270M tokenizer | `surveys/_synthesis.md:85,128`: the report does not cover 270M | verified | misleading | - |
| F5 | docs/vault/papers/finetuning_distillation/_synthesis.md | 253 | 8 contradictions | Llama-3.2-1B Δ −1.9 | the row's cells give −2.0 (rounding possible) — S3: Li 2025 Table 2 prints −1.9 (Table 7: −1.93) | dismissed | cosmetic | - |
| F6 | docs/vault/papers/finetuning_distillation/_synthesis.md | 266, 275 | 8 contradictions | Llama 8B/70B are teachers (266) and "students" (275) | internal inconsistency — S3: both roles exist in Li 2025; only fix: line 275 label is Llama3.1, not Llama-3.2 | dismissed | cosmetic | - |
| F7 | docs/vault/papers/finetuning_distillation/_synthesis.md | 51-54, 114-121, 183-200 | 10 formatting | 2-space nested bullets, tables inside list items | Python-Markdown needs 4-space nesting — S3: 2-space nesting flattens; 159 raw "- " lines | verified | cosmetic | - |
| F8 | docs/vault/papers/finetuning_distillation/_synthesis.md | 72-78, 141-151, 216-226 | 11 type-mixing | explanation note with how-to recipes | - — S3 Q4 (user): no split; the lede states the type and steps go to a final "What to try" section | verified | cosmetic | - |

## S2 critique (2026-11-14)

Type: explanation, heavy. 15 findings (0 breaks, 4 misleading, 11 cosmetic).

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| C1 | docs/vault/papers/finetuning_distillation/_synthesis.md | 8-14 | readability/1 lede | opens with a "Changes to the proposed junctions" blockquote | purpose first at 14; no audience | verified | misleading | - |
| C2 | docs/vault/papers/finetuning_distillation/_synthesis.md | 6, 16 | readability/5 jargon | "junction" in title and headings | defined only in `docs/vault/papers/README.md:10` | verified | misleading | - |
| C3 | docs/vault/papers/finetuning_distillation/_synthesis.md | 14 | readability/4 sentences | 38 words, 4 ideas | rule 4 | verified | cosmetic | - |
| C4 | docs/vault/papers/finetuning_distillation/_synthesis.md | 14 | readability/4 sentences | about 40 words, 3 clauses | rule 4 | verified | cosmetic | - |
| C5 | docs/vault/papers/finetuning_distillation/_synthesis.md | 9, 14, 20, 38 | readability/5 jargon | "logits", "forward vs reverse KL", "on-policy", "RL-style" | never explained | verified | misleading | - |
| C6 | docs/vault/papers/finetuning_distillation/_synthesis.md | 14, 20-21 | readability/5 jargon | SFT, LoRA, BF16, GGUF in the lede | none expanded | verified | misleading | - |
| C7 | docs/vault/papers/finetuning_distillation/_synthesis.md | 22, 90 | readability/5 jargon | "CoT", "NF4" | defined only at 163, 110 | verified | cosmetic | - |
| C8 | docs/vault/papers/finetuning_distillation/_synthesis.md | 50-129 | readability/5 jargon | GLUE, ECE, SST2, Rouge-L, WikiSQL, MNLI, MMLU | no gloss | verified | cosmetic | - |
| C9 | docs/vault/papers/finetuning_distillation/_synthesis.md | 14, 42, 75, 282 | readability/5 jargon | four names for token-level distillation | no canonical term — S3 Q9 (user): glossary: Copilot (tutor only in the papers' sense), Validation set (no dev/hold-out set), UNO Q = whole board, logit distillation, M3Kang, Token, Junction, Organizers/hidden test | verified | cosmetic | - |
| C10 | docs/vault/papers/finetuning_distillation/_synthesis.md | 99, 125, 195, 281 | readability/5 jargon | α = LoRA scale and α = mix weight | one symbol, two meanings | verified | cosmetic | - |
| C11 | docs/vault/papers/finetuning_distillation/_synthesis.md | 59, 64 | readability/5 jargon | "exposure bias", "length normalisation", "teacher-mixed sampling" | not explained | verified | cosmetic | - |
| C12 | docs/vault/papers/finetuning_distillation/_synthesis.md | 217 | readability/5 jargon | "the brief's numbers" | no repo doc is "the brief" — S3: S3 Q23b (user): "the brief" is CHALLENGE_CONTEXT.md | verified | cosmetic | - |
| C13 | docs/vault/papers/finetuning_distillation/_synthesis.md | 76, 151, 297 | readability/9 links | repo docs as code spans | not links | verified | cosmetic | - |
| C14 | docs/vault/papers/finetuning_distillation/_synthesis.md | 21, 87 | readability/11 claims | "an 8 GB RTX 4060" training GPU | no source in the repo — S3: S3 Q16 (user): the RTX 4060 is a team member's laptop; add "Team hardware" to CHALLENGE_CONTEXT and link it | verified | cosmetic | - |
| C15 | docs/vault/papers/finetuning_distillation/_synthesis.md | 48, 214 | readability/11 claims | "about 1,000 Kangaroo items" | no source (and S1: 1,747) | verified | cosmetic | - |
