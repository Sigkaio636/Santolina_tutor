# Findings: docs/GUIA_RESTRICCIONES_UNOQ.html

Open findings of `/docs-review`. Schema: `.claude/skills/doc-authoring/references/findings-schema.md`.

## S1 audit (2026-11-14)

Weight: heavy. Language: Spanish. Lines are HTML source lines.

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| F1 | docs/GUIA_RESTRICCIONES_UNOQ.html | 144, 281, 295, 325, 509-510 | 8 contradictions | limit is 60 s; the calculator turns red only above 60 s | `copilot/pipeline.py:15,35-36` MARGIN 3.0, the request times out at about 57 s | verified | misleading | - |
| F2 | docs/GUIA_RESTRICCIONES_UNOQ.html | 201, 403 | 8 contradictions | int8 CPU flags tagged "Verificar", listed as open | `docs/UNO_Q_BOARD_REFERENCE.md:309,466,501-509` measured: no asimddp, no i8mm | verified | misleading | - |
| F3 | docs/GUIA_RESTRICCIONES_UNOQ.html | 353 | 8 contradictions | 3-7B models near chance outside English | rows 475-476 and `docs/vault/papers/benchmarks/_synthesis.md:67`: only low-resource languages are near chance | verified | misleading | - |
| F4 | docs/GUIA_RESTRICCIONES_UNOQ.html | 190, 212-213, 234, 261 | 8 contradictions | BOARD_SETUP figures (3.1 GiB free, 1.1 GB used, 15 min OCR per language); Debian 13 "Inferido" | `docs/UNO_Q_BOARD_REFERENCE.md:492,494,532,557-558` measured other values; the conflicts table (385-392) omits them — S3: S3 Q14 (user): use our §14 measurements; BOARD_SETUP figures as the organizers' | verified | cosmetic | - |
| F5 | docs/GUIA_RESTRICCIONES_UNOQ.html | 277, 279 | 8 contradictions | index search in "milisegundos"; decode examples tagged Medido, citing BOARD_SETUP | `docs/BOARD_SETUP.md:1022,499-500` give rates, not these values — S3: 0.2 s, 7 s, 35-40 s are computed from rates: tag Calculado, not Medido | verified | cosmetic | - |
| F6 | docs/GUIA_RESTRICCIONES_UNOQ.html | 414-419 | 5 broken links | relative links to `*.md`, `../config.env`, `../predict.py` | the built page keeps `href="BOARD_SETUP.md"` etc.; the site has no `.md` files and `../` is outside the site | verified | breaks | - |
| F7 | docs/GUIA_RESTRICCIONES_UNOQ.html | 148, 190, 204, 213, 275, 390, 402 | 7 terminology | "LLM", "servidores", "el tutor" | `GLOSSARY.md:9,17,21` (English glossary, Spanish page) — S3 Q9 (user): glossary: Copilot (tutor only in the papers' sense), Validation set (no dev/hold-out set), UNO Q = whole board, logit distillation, M3Kang, Token, Junction, Organizers/hidden test | verified | cosmetic | - |
| F8 | docs/GUIA_RESTRICCIONES_UNOQ.html | 120-425 | 11 type-mixing | reference tables, explanation, a calculator and open questions on one page | one document, one type (`diataxis`) — S3 Q4 (user): no split; the lede states the type and steps go to a final "What to try" section | verified | cosmetic | - |

Incidental: SOTA rows (471-474) and some figures (356, 361, 374) cite gitignored PDFs and were not checked. The speed row (387) omits the team's 10.1/4.8 tok/s.

## S2 critique (2026-11-14)

Type: explanation + reference with a calculator, heavy, Spanish. 23 findings (0 breaks, 2 misleading, 21 cosmetic).

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| C1 | docs/GUIA_RESTRICCIONES_UNOQ.html | 123 | readability/1 lede | says what the page holds, not who reads it; 29 words, no verb | rule 1 | verified | cosmetic | - |
| C2 | docs/GUIA_RESTRICCIONES_UNOQ.html | 140-142, 302 | readability/3 headings | checklist has no heading; the calculator section has no number | rule 3 | verified | cosmetic | - |
| C3 | docs/GUIA_RESTRICCIONES_UNOQ.html | 248, 332, 371, 388 | readability/7 language | "Accuracy" vs "Acierto" | two words for one concept | verified | cosmetic | - |
| C4 | docs/GUIA_RESTRICCIONES_UNOQ.html | 133-406 | readability/7 language | "Checklist", "build oficial", "Throttling", "sparsity", "Speedup" | English in Spanish sentences, no gloss | verified | cosmetic | - |
| C5 | docs/GUIA_RESTRICCIONES_UNOQ.html | 148-225 | readability/5 jargon | App Lab, GGUF, SoC, NEON, SDOT/UDOT, I8MM, Bridge, OOM, mmproj | not explained | verified | cosmetic | - |
| C6 | docs/GUIA_RESTRICCIONES_UNOQ.html | 172, 261, 263 | readability/5 jargon | "high_quality", "pp", "IC 95 %" | not explained | verified | cosmetic | - |
| C7 | docs/GUIA_RESTRICCIONES_UNOQ.html | 295-297, 306 | readability/5 jargon | T_emb, RAG, "cache_prompt", "prompt_n" | not defined on the page | verified | cosmetic | - |
| C8 | docs/GUIA_RESTRICCIONES_UNOQ.html | 333-372 | readability/5 jargon | VLMs, resource tiers, TTFT, SFT, LoRA, imatrix, GSM8K | not explained | verified | cosmetic | - |
| C9 | docs/GUIA_RESTRICCIONES_UNOQ.html | 164, 333, 360, 421 | readability/5 jargon | "Cangur" and "Kangaroo" | never tied together | verified | cosmetic | - |
| C10 | docs/GUIA_RESTRICCIONES_UNOQ.html | 297 | readability/4 sentences | nested conditions; 3 ideas in one note | rule 4, 8 | verified | cosmetic | - |
| C11 | docs/GUIA_RESTRICCIONES_UNOQ.html | 354 | readability/4 sentences | 38 words, two ideas | rule 4 | verified | cosmetic | - |
| C12 | docs/GUIA_RESTRICCIONES_UNOQ.html | 202 | readability/4 sentences | the "Implicación" cell does not state the implication | rule 4 | verified | cosmetic | - |
| C13 | docs/GUIA_RESTRICCIONES_UNOQ.html | 227, 280, 291 | readability/9 links | source "BOARD_SETUP Explorer" | no such heading (`BOARD_SETUP.md:900`) | verified | misleading | - |
| C14 | docs/GUIA_RESTRICCIONES_UNOQ.html | 291, 448, 450 | readability/11 claims | the chart tags every bar "Medido" | "RAG × 2" is "Inferido" at 296; rewriting is an estimate | verified | cosmetic | - |
| C15 | docs/GUIA_RESTRICCIONES_UNOQ.html | 286-290, 448-461 | readability/8 form | legend misses red for >60 s; three values without a unit | rule 8 | verified | cosmetic | - |
| C16 | docs/GUIA_RESTRICCIONES_UNOQ.html | 305 | readability/6 steps | calculator input "Tokens del problema + instrucción" | no way to get the number | verified | cosmetic | - |
| C17 | docs/GUIA_RESTRICCIONES_UNOQ.html | 150, 172, 244, 250 | readability/11 claims | always-D: 25 % and 24.6 % | different sets (`config.env:40`), not said | verified | cosmetic | - |
| C18 | docs/GUIA_RESTRICCIONES_UNOQ.html | 182, 371, 385-392 | readability/11 claims | "el vídeo", "mischianti", "guía Arduino", "RESUMEN §6" | no link | verified | cosmetic | - |
| C19 | docs/GUIA_RESTRICCIONES_UNOQ.html | 188-260 | readability/11 claims | KPI tiles and items with no source location | e.g. 260 from `BOARD_SETUP.md:856` | verified | cosmetic | - |
| C20 | docs/GUIA_RESTRICCIONES_UNOQ.html | 333, 357, 374, 385 | readability/7 language | "1,747", "68,000" | comma reads as decimal in Spanish — S3 Q5 (user): English with US spelling, so "1,747" and "copilot" are correct | dismissed | cosmetic | - |
| C21 | docs/GUIA_RESTRICCIONES_UNOQ.html | 247-254, 367 | readability/10 duplication | baseline table, board speed | `BOARD_SETUP.md:865-867`, `CHALLENGE_CONTEXT.md:55` — S3 Q3 (user): canonical-copy rule (how-to/ for our flow, UNO_Q_BOARD_REFERENCE for specs, CLAUDE.md for the red line, GOAL_MUSTS for the checklist, README for credits); the other copy links to it | verified | cosmetic | - |
| C22 | docs/GUIA_RESTRICCIONES_UNOQ.html | 124-130, 199-216, 231 | readability/8 form | tag legend as one paragraph; "Oficial" used for datasheet values its definition excludes | rule 8 | verified | misleading | - |
| C23 | docs/GUIA_RESTRICCIONES_UNOQ.html | 260, 387 | readability/6 steps | "`eval.py --limit 0`", "`llama-bench`" | not copyable | verified | cosmetic | - |
