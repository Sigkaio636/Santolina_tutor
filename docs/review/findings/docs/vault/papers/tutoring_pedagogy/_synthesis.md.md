# Findings: docs/vault/papers/tutoring_pedagogy/_synthesis.md

Open findings of `/docs-review`. Schema: `.claude/skills/doc-authoring/references/findings-schema.md`.

## S1 audit (2026-11-14)

Weight: heavy. Paper figures were checked for arithmetic and against other notes only: the PDFs are gitignored.

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| F1 | docs/vault/papers/tutoring_pedagogy/_synthesis.md | 20-21, 278-280 | 5 broken links | PDF wikilinks | gitignored, excluded | verified | breaks | - |
| F2 | docs/vault/papers/tutoring_pedagogy/_synthesis.md | 194 | 8 contradictions | 8081/8082 could host a solver and a tutor | 8082 is the embedding service (`config.env:25-30`, `copilot/embed.py:7`) | verified | misleading | - |
| F3 | docs/vault/papers/tutoring_pedagogy/_synthesis.md | 129 | 8 contradictions | "GSM8K −7.5 (86.8 → 79.5)" | the difference is 7.3 — S3: the paper's Table 3 prints −7.5 | dismissed | misleading | - |
| F4 | docs/vault/papers/tutoring_pedagogy/_synthesis.md | 155 | 8 contradictions | "SFT cost 7.5-9.4 points" | repeats F3 — S3: same source as F3 | dismissed | cosmetic | F3 |
| F5 | docs/vault/papers/tutoring_pedagogy/_synthesis.md | 14 | 8 contradictions | only MathDial tested models under 1B | line 138: Bridge fine-tuned Flan-T5 and GODEL — S3: Bridge fine-tuned Flan-T5 and GODEL but reported no numbers: "only MathDial reported results under 1B" | verified | cosmetic | - |
| F6 | docs/vault/papers/tutoring_pedagogy/_synthesis.md | 12 | 8 contradictions | MRBench from Bridge and MathDial, cited to two docs | `docs/vault/papers/README.md:133` names Bridge only | verified | cosmetic | - |
| F7 | docs/vault/papers/tutoring_pedagogy/_synthesis.md | 149, 154 | 8 contradictions | LoRA SFT on Gemma 3 as the deployed model | `config.env:12-15` Qwen3.5 0.8B — S3 Q2 (user): the fine-tune base is not chosen yet; say Qwen3.5 0.8B is deployed and Gemma 3 is one option being explored | verified | misleading | - |
| F8 | docs/vault/papers/tutoring_pedagogy/_synthesis.md | 9, 168, 193-196 | 7 terminology | "tutor model" as a component of the copilot | `GLOSSARY.md:7-9` does not cover a tutoring component — S3 Q9 (user): glossary: Copilot (tutor only in the papers' sense), Validation set (no dev/hold-out set), UNO Q = whole board, logit distillation, M3Kang, Token, Junction, Organizers/hidden test | verified | cosmetic | - |
| F9 | docs/vault/papers/tutoring_pedagogy/_synthesis.md | 8-12 | 6 placeholder | blockquote "Changes to the proposed junctions" | meta text — S3 Q8 (user): delete the "Changes to the proposed junctions" blocks; VERIFY markers go to a final "Open questions" list | verified | cosmetic | - |
| F10 | docs/vault/papers/tutoring_pedagogy/_synthesis.md | 36-43, 93-97, 206-211 (repeats) | 10 formatting | lists with no blank line; 2-space nesting | Python-Markdown — S3: 138 raw "- " lines | verified | cosmetic | - |
| F11 | docs/vault/papers/tutoring_pedagogy/_synthesis.md | 148-158, 260-264 | 11 type-mixing | how-to steps in an explanation note | `diataxis` — S3 Q4 (user): no split; the lede states the type and steps go to a final "What to try" section | verified | cosmetic | F7 |

## S2 critique (2026-11-14)

Type: explanation, heavy. 13 findings (0 breaks, 4 misleading, 9 cosmetic).

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| C1 | docs/vault/papers/tutoring_pedagogy/_synthesis.md | 14 | readability/1 lede | starts "Three tutoring corpora exist..." | no purpose or reader | verified | misleading | F9 |
| C2 | docs/vault/papers/tutoring_pedagogy/_synthesis.md | 6, 16 | readability/5 jargon | "junction" | defined only in `docs/vault/papers/README.md:10` | verified | misleading | - |
| C3 | docs/vault/papers/tutoring_pedagogy/_synthesis.md | 14 | readability/4 sentences | 29 words, 3 ideas | rule 4 | verified | cosmetic | - |
| C4 | docs/vault/papers/tutoring_pedagogy/_synthesis.md | 14, 96 | readability/5 jargon | SFT, RL, RLHF | never expanded | verified | misleading | - |
| C5 | docs/vault/papers/tutoring_pedagogy/_synthesis.md | 120-127 | readability/5 jargon | "Δ solve 36.2%, leak 89.5%" | defined only at 229-230 | verified | misleading | - |
| C6 | docs/vault/papers/tutoring_pedagogy/_synthesis.md | 118, 123, 163 | readability/5 jargon | GRPO, MDPO, DPO | not expanded | verified | cosmetic | - |
| C7 | docs/vault/papers/tutoring_pedagogy/_synthesis.md | 51-234 | readability/5 jargon | κ, METEOR, sBLEU, BERTScore, Likert, FERPA, Prolific | no gloss | verified | cosmetic | - |
| C8 | docs/vault/papers/tutoring_pedagogy/_synthesis.md | 127 | readability/5 jargon | "Ped-RM micro: 4.4" | explained only at 209, 257 | verified | cosmetic | - |
| C9 | docs/vault/papers/tutoring_pedagogy/_synthesis.md | 28, 99, 112, 131 | readability/5 jargon | SocraticLM vs SocraticLLM vs SocraticMATH | same system or typo? — S3: SocraticLLM (Ding 2024) and SocraticLM (Liu 2024) are two systems; SocraticLM is not in the vault | verified | cosmetic | - |
| C10 | docs/vault/papers/tutoring_pedagogy/_synthesis.md | 20-21, 32, 89 | readability/3 headings | headings differ from the table rows that name them | rule 3 | verified | cosmetic | - |
| C11 | docs/vault/papers/tutoring_pedagogy/_synthesis.md | 56 | readability/9 links | bare `github.com/...` URLs | not links | verified | cosmetic | - |
| C12 | docs/vault/papers/tutoring_pedagogy/_synthesis.md | 23-266 | readability/9 links | `CHALLENGE_CONTEXT.md` §6-§8 | not links | verified | cosmetic | - |
| C13 | docs/vault/papers/tutoring_pedagogy/_synthesis.md | 48-56 | readability/8 form | table cells of 2-3 sentences | hard to scan | verified | cosmetic | - |
