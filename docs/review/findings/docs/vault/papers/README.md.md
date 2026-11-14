# Findings: docs/vault/papers/README.md

Open findings of `/docs-review`. Schema: `.claude/skills/doc-authoring/references/findings-schema.md`.

## S1 audit (2026-11-14)

Weight: heavy. Paper figures were checked for arithmetic and against other notes only: the PDFs are gitignored.

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| F1 | docs/vault/papers/README.md | 18-163 (PDF column) | 5 broken links | PDF wikilinks | gitignored, excluded | verified | breaks | - |
| F2 | docs/vault/papers/README.md | 10, 14, 38, 67, 92, 106, 119, 128, 140 | 5 broken links | note wikilinks to `_junctions` and syntheses | no wikilink support | verified | breaks | - |
| F3 | docs/vault/papers/README.md | 8 | 8 contradictions | board has "2-4 GB RAM" | `GLOSSARY.md:12`, `CHALLENGE_CONTEXT.md:18` 4 GB | verified | misleading | - |
| F4 | docs/vault/papers/README.md | 113 | 8 contradictions | Gemma 3 is "our candidate base model family" | `config.env:12-15` Qwen3.5 0.8B — S3 Q2 (user): the fine-tune base is not chosen yet; say Qwen3.5 0.8B is deployed and Gemma 3 is one option being explored | verified | misleading | - |
| F5 | docs/vault/papers/README.md | 8 | 7 terminology | "a small math-tutor LLM on the Arduino UNO Q" | `GLOSSARY.md:7-21` | verified | cosmetic | - |
| F6 | docs/vault/papers/README.md | 3, 8 | 5 broken links | "See `CHALLENGE_CONTEXT.md`" without a path | it is docs/CHALLENGE_CONTEXT.md | verified | cosmetic | - |
| F7 | docs/vault/papers/README.md | 4 | 8 contradictions | names follow `<firstauthor><year>_...` | `papers.tsv:61,69` break the pattern | verified | cosmetic | - |
| F8 | docs/vault/papers/README.md | 142 | 11 type-mixing | "Main takeaway" paragraph in a reference index | repeats `jev/_synthesis.md:16-18` — S3 Q4 (user): no split; the lede states the type and steps go to a final "What to try" section | verified | cosmetic | - |

## S2 critique (2026-11-14)

Type: reference (vault index), heavy. 16 findings (0 breaks, 0 misleading, 16 cosmetic).

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| C1 | docs/vault/papers/README.md | 1 | readability/3 headings | title lists 5 topics | 8 folder sections | verified | cosmetic | - |
| C2 | docs/vault/papers/README.md | 3-4 | readability/1 lede | opens with download date and file-name pattern | purpose only at 8-10 | verified | cosmetic | - |
| C3 | docs/vault/papers/README.md | 3 | readability/4 sentences | over 30 words with an empty parenthetical | rule 4 | verified | cosmetic | - |
| C4 | docs/vault/papers/README.md | 3 | readability/11 claims | "each arXiv ID was checked against the arXiv API" | no script or log — S3: S3 Q18 (user): reword: IDs and titles were checked against arXiv when the PDFs were downloaded (2026-11-14) | verified | cosmetic | - |
| C5 | docs/vault/papers/README.md | 6 | readability/6 steps | "run ./download.sh in this folder" | folder not named; no check (it prints OK/FAIL) | verified | cosmetic | - |
| C6 | docs/vault/papers/README.md | 4 | readability/5 jargon | "opens the local copy in Obsidian" | tool never introduced | verified | cosmetic | F1 |
| C7 | docs/vault/papers/README.md | 24, 28 | readability/5 jargon | "Martí's top suggestion" | never introduced — S3: Martí is introduced at docs/CHALLENGE_CONTEXT.md:4; link it | verified | cosmetic | - |
| C8 | docs/vault/papers/README.md | 22-63 | readability/5 jargon | OBS, 2:4, LoRA, QLoRA, PTQ/QAT, W8A8, KV, imatrix | CHALLENGE_CONTEXT §10 not linked; some defined nowhere | verified | cosmetic | - |
| C9 | docs/vault/papers/README.md | 72-101 | readability/5 jargon | IO-aware, KV-cache, reverse KL, GSM8K, SFT | not explained | verified | cosmetic | - |
| C10 | docs/vault/papers/README.md | 132-136 | readability/5 jargon | SFT, MRBench, RL, MathTutorBench | not explained or linked | verified | cosmetic | - |
| C11 | docs/vault/papers/README.md | 142 | readability/5 jargon | "System One", "grammar-constrained answer call" | not explained | verified | cosmetic | F8 |
| C12 | docs/vault/papers/README.md | 142 | readability/11 claims | "early access since September 2026" | no source — S3: S3 Q17 (user): no public link; label "(team note, no public source)" | verified | cosmetic | F8 |
| C13 | docs/vault/papers/README.md | 142 | readability/4 sentences | about 38 words, 3 ideas | rule 4 | verified | cosmetic | F8 |
| C14 | docs/vault/papers/README.md | 147-158 | readability/5 jargon | letter-logit, MathQA, CLIP | not explained | verified | cosmetic | - |
| C15 | docs/vault/papers/README.md | 27 | readability/9 links | "(CHALLENGE_CONTEXT §3)" | no path | verified | cosmetic | - |
| C16 | docs/vault/papers/README.md | 168 | readability/5 jargon | "GGUF quantization formats (Q4_0, K-quants)" | first use, unexplained | verified | cosmetic | - |
