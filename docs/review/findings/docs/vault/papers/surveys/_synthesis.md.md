# Findings: docs/vault/papers/surveys/_synthesis.md

Open findings of `/docs-review`. Schema: `.claude/skills/doc-authoring/references/findings-schema.md`.

## S1 audit (2026-11-14)

Weight: heavy. Paper figures were checked for arithmetic and against other notes only: the PDFs are gitignored.

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| F1 | docs/vault/papers/surveys/_synthesis.md | 13-60, 121, 127, 159-165 | 5 broken links | PDF wikilinks | gitignored, excluded, no wikilink support | verified | breaks | - |
| F2 | docs/vault/papers/surveys/_synthesis.md | 24, 80, 114 | 8 contradictions | "2-4 GB RAM"; "on a 2 GB board" | 4 GB | verified | misleading | - |
| F3 | docs/vault/papers/surveys/_synthesis.md | 52, 65, 115 | 8 contradictions | decode is bandwidth-bound, as fact | `inference/_synthesis.md:71-76` says maybe compute-bound — S3: S3 Q15 (user): move to "Open questions": not measured on our board | verified | misleading | - |
| F4 | docs/vault/papers/surveys/_synthesis.md | 80, 117-119 | 8 contradictions | base model choice Gemma 3 1B vs Salamandra 2B | `config.env:12-15` Qwen3.5 0.8B, never considered — S3 Q2 (user): the fine-tune base is not chosen yet; say Qwen3.5 0.8B is deployed and Gemma 3 is one option being explored | verified | misleading | - |
| F5 | docs/vault/papers/surveys/_synthesis.md | 12-150 (15 places) | 10 formatting | paragraph runs into a list with no blank line | Python-Markdown — S3: 78 raw "- " lines | verified | cosmetic | - |
| F6 | docs/vault/papers/surveys/_synthesis.md | 24, 80 | 7 terminology | "math tutor" | `GLOSSARY.md:7-9` | verified | cosmetic | - |

## S2 critique (2026-11-14)

Type: explanation, heavy. 19 findings (0 breaks, 2 misleading, 17 cosmetic).

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| C1 | docs/vault/papers/surveys/_synthesis.md | 8 | readability/1 lede | opens with a 7-sentence changelog | the lede is at 10 | verified | misleading | - |
| C2 | docs/vault/papers/surveys/_synthesis.md | 10 | readability/5 jargon | GGUF, CPU decode, int4 QAT, KV cache, "junction" | not defined here | verified | cosmetic | - |
| C3 | docs/vault/papers/surveys/_synthesis.md | 8, 25, 134 | readability/5 jargon | QAT, PTQ | never expanded | verified | cosmetic | - |
| C4 | docs/vault/papers/surveys/_synthesis.md | 31 | readability/8 form | 13-sentence paragraph | split; a table | verified | cosmetic | - |
| C5 | docs/vault/papers/surveys/_synthesis.md | 31, 39-40 | readability/5 jargon | PEFT, MoE, "edge-cloud collaboration" | not expanded | verified | cosmetic | - |
| C6 | docs/vault/papers/surveys/_synthesis.md | 31 | readability/5 jargon | "the parsed version" | parsed/ never explained | verified | cosmetic | - |
| C7 | docs/vault/papers/surveys/_synthesis.md | 43-49 | readability/8 form | methods with "CoRR abs/..." IDs in prose | a table | verified | cosmetic | - |
| C8 | docs/vault/papers/surveys/_synthesis.md | 53-115 | readability/9 links | "CHALLENGE_CONTEXT §2", "BOARD_SETUP" | no path | verified | cosmetic | - |
| C9 | docs/vault/papers/surveys/_synthesis.md | 52-71 | readability/5 jargon | W8A8, MFU, roofline, PIM/PNM, TTFT, "MELT style" | not expanded | verified | cosmetic | - |
| C10 | docs/vault/papers/surveys/_synthesis.md | 86-92 | readability/5 jargon | GQA, QK-norm, SFP8, IT/PT, MGSM, HiddenMath, IFEval, ... | not expanded | verified | cosmetic | F4 |
| C11 | docs/vault/papers/surveys/_synthesis.md | 89 | readability/8 form | an 11-sentence bullet of memory figures | a table | verified | cosmetic | F4 |
| C12 | docs/vault/papers/surveys/_synthesis.md | 89 | readability/4 sentences | "That ... matches ... is our inference." | sentence-initial clause; "inference" ambiguous | verified | cosmetic | F4 |
| C13 | docs/vault/papers/surveys/_synthesis.md | 96-110 | readability/5 jargon | K/V heads, fertility, BPE, NFC, ChatML, Belebele, FLORES | not expanded | verified | cosmetic | F4 |
| C14 | docs/vault/papers/surveys/_synthesis.md | 100, 110 | readability/8 form | Salamandra vs Gemma-2 scores in prose | a table | verified | cosmetic | F4 |
| C15 | docs/vault/papers/surveys/_synthesis.md | 114 | readability/4 sentences | about 37 words in a 9-sentence bullet | rule 4 | verified | cosmetic | F2, F4 |
| C16 | docs/vault/papers/surveys/_synthesis.md | 86, 114 | readability/11 claims | "5 local per global" vs "1:3 local:global" | reads reversed — S3: Gemma 3 §2: 5 local per global; "1:3" means 3 local per global, line 114 reads reversed | verified | misleading | - |
| C17 | docs/vault/papers/surveys/_synthesis.md | 115 | readability/11 claims | "4-7 tok/s reading-speed target" | no source | verified | cosmetic | F3 |
| C18 | docs/vault/papers/surveys/_synthesis.md | 146 | readability/5 jargon | "Adreno OpenCL path" | not explained | verified | cosmetic | - |
| C19 | docs/vault/papers/surveys/_synthesis.md | 154-156 | readability/3 headings | "Papers not covered by any junction": "None." | empty section | verified | cosmetic | - |
