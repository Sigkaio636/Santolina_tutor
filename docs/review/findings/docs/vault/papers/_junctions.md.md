# Findings: docs/vault/papers/_junctions.md

Open findings of `/docs-review`. Schema: `.claude/skills/doc-authoring/references/findings-schema.md`.

## S1 audit (2026-11-14)

Weight: heavy. Paper figures were checked for arithmetic and against other notes only: the PDFs are gitignored.

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| F1 | docs/vault/papers/_junctions.md | 15-22 | 5 broken links | note wikilinks in the folder table | no wikilink support | verified | breaks | - |
| F2 | docs/vault/papers/_junctions.md | 115-118, 128 | 8 contradictions | 60 s at 5 tok/s ≈ 300 tokens; 576 is "twice our budget" | prefill dominates (X3, 100-101); `jev/_synthesis.md:92` 150-250 tokens | verified | misleading | - |
| F3 | docs/vault/papers/_junctions.md | 115-116 | 8 contradictions | "force the final letter with a GBNF grammar" as work to do | `copilot/llm.py:45-46` already does it | verified | misleading | - |
| F4 | docs/vault/papers/_junctions.md | 10 | 8 contradictions | "2-4 GB RAM" | 4 GB | verified | misleading | - |
| F5 | docs/vault/papers/_junctions.md | 9-10, 78-79 | 8 contradictions | target is Gemma 3 270M/1B; X1 decides to fine-tune Gemma 3 1B | `config.env:12-15` Qwen3.5 0.8B — S3 Q2 (user): the fine-tune base is not chosen yet; say Qwen3.5 0.8B is deployed and Gemma 3 is one option being explored | verified | misleading | - |
| F6 | docs/vault/papers/_junctions.md | 9, 119 | 7 terminology | "UNO Q math tutor" and "the copilot" | `GLOSSARY.md:7-9` | verified | cosmetic | - |
| F7 | docs/vault/papers/_junctions.md | 71-72 | 8 contradictions | M3Kang authors blame "output format, not reasoning" | `benchmarks/_synthesis.md:97` also "limited reasoning training" | verified | cosmetic | - |

## S2 critique (2026-11-14)

Type: explanation, heavy. 20 findings (0 breaks, 3 misleading, 17 cosmetic).

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| C1 | docs/vault/papers/_junctions.md | 8-11 | readability/1 lede | no reader, no way to use the note | "What to read first" (186) not mentioned | verified | cosmetic | - |
| C2 | docs/vault/papers/_junctions.md | 8-10 | readability/4 sentences | about 40 words: definition plus five specs | rule 4 | verified | cosmetic | F4, F5 |
| C3 | docs/vault/papers/_junctions.md | 35-47 | readability/5 jargon | labels X1-X8 | never said to mean cross-folder junction | verified | cosmetic | - |
| C4 | docs/vault/papers/_junctions.md | 30 | readability/3 headings | "## Map" | does not say what it maps | verified | cosmetic | - |
| C5 | docs/vault/papers/_junctions.md | 68-75 | readability/5 jargon | QAT, KV cache, GSM8K | not defined | verified | cosmetic | F5 |
| C6 | docs/vault/papers/_junctions.md | 87-94 | readability/5 jargon | importance matrix, FFN-width, logit distillation, 2:4, dense | not defined | verified | cosmetic | - |
| C7 | docs/vault/papers/_junctions.md | 74, 96-109 | readability/5 jargon | prefill/decode, "tied output layer", `--cache-ram 0` | X3 depends on them | verified | cosmetic | - |
| C8 | docs/vault/papers/_junctions.md | 100 | readability/11 claims | "about 11 tok/s prefill, 6 tok/s decode" | no link to `BOARD_SETUP.md:1023` | verified | cosmetic | - |
| C9 | docs/vault/papers/_junctions.md | 100-101 | readability/4 sentences | "reads X as:" with a nested parenthesis | hides the claim | verified | cosmetic | - |
| C10 | docs/vault/papers/_junctions.md | 107 | readability/4 sentences | "(inference J6, our inference)" | folder vs deduction | verified | misleading | - |
| C11 | docs/vault/papers/_junctions.md | 117, 138 | readability/5 jargon | "small students" (distilled models) | `GLOSSARY.md:8` uses "student" for the learner | verified | misleading | - |
| C12 | docs/vault/papers/_junctions.md | 115-124 | readability/5 jargon | GBNF, SFT, "batch verification", "letter logits" | not defined | verified | cosmetic | F3 |
| C13 | docs/vault/papers/_junctions.md | 134-136 | readability/4 sentences | "it is also the recovery method Minitron uses" | "it" reads as Salamandra | verified | misleading | - |
| C14 | docs/vault/papers/_junctions.md | 143 | readability/9 links | "(see below)" | target 213-214, no anchor | verified | cosmetic | - |
| C15 | docs/vault/papers/_junctions.md | 171 | readability/5 jargon | CoT, "N" on failure | explained only in benchmarks note | verified | cosmetic | - |
| C16 | docs/vault/papers/_junctions.md | 181-184 | readability/4 sentences | about 40 words, 2 parentheses; "unoq-board skill" | rule 4 | verified | cosmetic | - |
| C17 | docs/vault/papers/_junctions.md | 194 | readability/5 jargon | "the RTX 4060" | whose GPU is never said | verified | cosmetic | - |
| C18 | docs/vault/papers/_junctions.md | 202, 205 | readability/5 jargon | "VERIFY items", "pp and tg" | not explained | verified | cosmetic | - |
| C19 | docs/vault/papers/_junctions.md | 66-198 | readability/9 links | about 40 "pruning J6" references, plain text | depends on the wikilink fix | verified | cosmetic | F1 |
| C20 | docs/vault/papers/_junctions.md | 8, 11, 183, 215 | readability/7 language | British spellings ("organisers") | `GLOSSARY.md:28` US "organizers" — S3 Q5 (user): everything in English except the transcript and original sources; US spelling | verified | cosmetic | - |
