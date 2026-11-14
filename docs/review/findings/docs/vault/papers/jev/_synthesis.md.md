# Findings: docs/vault/papers/jev/_synthesis.md

Open findings of `/docs-review`. Schema: `.claude/skills/doc-authoring/references/findings-schema.md`.

## S1 audit (2026-11-14)

Weight: heavy (explanation). Paper figures were checked for arithmetic and against other notes only: the PDFs are gitignored.

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| F1 | docs/vault/papers/jev/_synthesis.md | 21-24, 31-35, 191, 195-198 | 5 broken links | `[[<slug>.pdf\|...]]` wikilinks | no wikilink support; PDFs excluded and gitignored | verified | breaks | - |
| F2 | docs/vault/papers/jev/_synthesis.md | 18, 101, 122 | 7 terminology | "tutor" next to "our copilot" | `GLOSSARY.md:7-9` | verified | cosmetic | - |
| F3 | docs/vault/papers/jev/_synthesis.md | 61, 120, 121 | 7 terminology | "dev set" / "dev split" | `GLOSSARY.md:43-45` Validation set; maybe a separate split — S3 Q9 (user): glossary: Copilot (tutor only in the papers' sense), Validation set (no dev/hold-out set), UNO Q = whole board, logit distillation, M3Kang, Token, Junction, Organizers/hidden test | verified | cosmetic | - |
| F4 | docs/vault/papers/jev/_synthesis.md | 91 | 8 contradictions | `cache_prompt: True` avoids recomputing the prefix | `inference/_synthesis.md:119-121,127` marks reuse under `--cache-ram 0` as VERIFY; no measurement — S3: S3 Q15 (user): move to "Open questions": not measured on our board | verified | misleading | - |
| F5 | docs/vault/papers/jev/_synthesis.md | 18, 90-93, 96 | 8 contradictions | a short reasoning pass is the main lever; gain for a small model open | `BOARD_SETUP.md:867`: one line of reasoning scored 17.5% vs the 22.5% baseline (n=40) — S3: S3 Q15 (user): cite BOARD_SETUP.md:867: one line of reasoning gave 17.5% (7/40) vs the 22.5% baseline | verified | misleading | - |
| F6 | docs/vault/papers/jev/_synthesis.md | 54, 65, 125, 150, 157 | 8 contradictions | the board model treated as Gemma 3 1B/270M | `config.env:12-15`, `GLOSSARY.md:19-21` Qwen3.5 0.8B Q8_0 — S3 Q2 (user): the fine-tune base is not chosen yet; say Qwen3.5 0.8B is deployed and Gemma 3 is one option being explored | verified | misleading | - |
| F7 | docs/vault/papers/jev/_synthesis.md | 59-62, 93, 120-122, 181 | 11 type-mixing | explanation with how-to procedures | - — S3 Q4 (user): no split; the lede states the type and steps go to a final "What to try" section | verified | cosmetic | - |

## S2 critique (2026-11-14)

Type: explanation, heavy. 14 findings (0 breaks, 4 misleading, 10 cosmetic).

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| C1 | docs/vault/papers/jev/_synthesis.md | 8-14 | readability/1 lede | opens with a junction change log | what Jev is comes only at 16 | verified | misleading | - |
| C2 | docs/vault/papers/jev/_synthesis.md | 6, 28 | readability/5 jargon | "junction" | defined only in `docs/vault/papers/README.md:10` | verified | misleading | - |
| C3 | docs/vault/papers/jev/_synthesis.md | 16 | readability/5 jargon | "System One", "Noul" | never explained | verified | misleading | - |
| C4 | docs/vault/papers/jev/_synthesis.md | 18, 44, 59 | readability/5 jargon | "next-token logits", "renormalize", "softmax", "argmax" | the core technique, never explained | verified | misleading | - |
| C5 | docs/vault/papers/jev/_synthesis.md | 51, 106-110, 140 | readability/5 jargon | PMI, ECE, AUROC, τ, "S=0.35" | not defined | verified | cosmetic | - |
| C6 | docs/vault/papers/jev/_synthesis.md | 26, 82, 141, 182 | readability/5 jargon | MinerU, KV cache, SGLang, mmproj | no gloss | verified | cosmetic | - |
| C7 | docs/vault/papers/jev/_synthesis.md | 18 | readability/4 sentences | about 55 words with two list items | rule 4 | verified | cosmetic | - |
| C8 | docs/vault/papers/jev/_synthesis.md | 18 | readability/4 sentences | 36 words, code and two clauses | rule 4 | verified | cosmetic | - |
| C9 | docs/vault/papers/jev/_synthesis.md | 18 | readability/8 form | 9-sentence lede paragraph | split into a list | verified | cosmetic | - |
| C10 | docs/vault/papers/jev/_synthesis.md | 92 | readability/4 sentences | about 38 words, 4 figures; "a 80" | rule 4 | verified | cosmetic | - |
| C11 | docs/vault/papers/jev/_synthesis.md | 166 | readability/9 links | bare `github.com/...` with no scheme | not a link | verified | cosmetic | - |
| C12 | docs/vault/papers/jev/_synthesis.md | 59, 92, 195 | readability/9 links | "benchmarks synthesis J3", "BOARD_SETUP §5.5" | no path, no link | verified | cosmetic | - |
| C13 | docs/vault/papers/jev/_synthesis.md | 16 | readability/11 claims | "early access since September 2026, version jev-1.13.0" | no source — S3: S3 Q17 (user): no public link; label "(team note, no public source)" | verified | cosmetic | - |
| C14 | docs/vault/papers/jev/_synthesis.md | 173 | readability/11 claims | "The awesome-jev list says so" | not linked — S3: S3 Q17 (user): no public link; label "(team note, no public source)" | verified | cosmetic | - |
