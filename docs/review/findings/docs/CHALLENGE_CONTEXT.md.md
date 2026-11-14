# Findings: docs/CHALLENGE_CONTEXT.md

Open findings of `/docs-review`. Schema: `.claude/skills/doc-authoring/references/findings-schema.md`.

## S1 audit (2026-11-14)

Weight: heavy.

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| F1 | docs/CHALLENGE_CONTEXT.md | 19, 157 | 8 contradictions | about 1000 Kangaroo problems | `BOARD_SETUP.md:715` 1,747 problems | verified | misleading | - |
| F2 | docs/CHALLENGE_CONTEXT.md | 23, 205 | 8 contradictions | data language unknown, "likely Catalan" | `BOARD_SETUP.md:715` 108 languages; :747 all problems in eng and cat | verified | misleading | - |
| F3 | docs/CHALLENGE_CONTEXT.md | 21 | 8 contradictions | must explain pedagogically, not only give the letter | `BOARD_SETUP.md:35-38` Teach or Reason; Reason = choose the letter | verified | misleading | - |
| F4 | docs/CHALLENGE_CONTEXT.md | 22, 206 | 8 contradictions | evaluation is a pedagogical benchmark; eval script unknown | `BOARD_SETUP.md:38,696,1091` jury runs predict.py on a hidden test set; `predict.py:2-11` | verified | misleading | F3 |
| F5 | docs/CHALLENGE_CONTEXT.md | 212 | 8 contradictions | allowed models / size open | `BOARD_SETUP.md:1099` any GGUF that fits in RAM, in time, with a usable license | verified | cosmetic | - |
| F6 | docs/CHALLENGE_CONTEXT.md | 80 | 8 contradictions | Qwen 3.5 0.8B Q4_0 runs on the board | `config.env:15` Q8_0; `GLOSSARY.md:20` | verified | misleading | - |
| F7 | docs/CHALLENGE_CONTEXT.md | 65, 80, 186 | 7 terminology | "baseline" = Gemma/Qwen Q4_0 runs and tok/s | `GLOSSARY.md:31-33` Baseline = organizers' copilot, 22.5% on 40 problems | verified | cosmetic | - |
| F8 | docs/CHALLENGE_CONTEXT.md | 27-30, 75, 186 | 8 contradictions | plan uses a Gemma base model, Qwen only to compare | `GLOSSARY.md:19-21`, `config.env:13-15` Qwen3.5 0.8B; `RESUMEN_QUALCOMM_UNO_Q.md:130` calls it a team decision — S3 Q2 (user): the fine-tune base is not chosen yet; say Qwen3.5 0.8B is deployed and Gemma 3 is one option being explored | verified | misleading | - |
| F9 | docs/CHALLENGE_CONTEXT.md | 61, 103, 178 | 1 stale | benchmark with llama-bench | `board/02_build_llama_cpp.sh:27` builds only llama-server and llama-cli | verified | breaks | - |
| F10 | docs/CHALLENGE_CONTEXT.md | 1, 23, 199 | 7 terminology | "tutor", "LLM" | `GLOSSARY.md:7-9,21` | verified | cosmetic | - |
| F11 | docs/CHALLENGE_CONTEXT.md | 64 | 7 terminology | "the two servers" | `GLOSSARY.md:15-17` Model services | verified | cosmetic | - |
| F12 | docs/CHALLENGE_CONTEXT.md | 185 | 10 formatting | bare code fence | no language tag | verified | cosmetic | - |
| F13 | docs/CHALLENGE_CONTEXT.md | 1-248 | 11 type-mixing | explanation with how-to (102-104, 174-179), open-question checklist (§9), glossary (§10) | - — S3 Q4 (user): no split; the lede states the type and steps go to a final "What to try" section | verified | cosmetic | - |

Incidental: external links (229-248) not checked.

## S2 critique (2026-11-14)

Type: explanation, heavy. 24 findings (0 breaks, 2 misleading, 22 cosmetic).

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| C1 | docs/CHALLENGE_CONTEXT.md | 19, 21, 157, 176, 205 | readability/5 jargon | "Kangaroo data/set"; M3Kang never named | `GLOSSARY.md:3`, `BOARD_SETUP.md:27` | verified | misleading | - |
| C2 | docs/CHALLENGE_CONTEXT.md | 35, 56, 73, 98 | readability/5 jargon | LoRA, GGUF, QAT, PTQ before definition | defined at 147, 217-219 | verified | cosmetic | - |
| C3 | docs/CHALLENGE_CONTEXT.md | 22-188 | readability/5 jargon | MCQ/MMLU, TOPS, KV cache, IT, IFEval, GQA, OBS, SFT | not explained | verified | cosmetic | - |
| C4 | docs/CHALLENGE_CONTEXT.md | 216-225 | readability/5 jargon | its own §10 glossary | not in `GLOSSARY.md`; move or link — S3: S3 Q23a (user): move §10 terms to GLOSSARY.md and link it | verified | cosmetic | - |
| C5 | docs/CHALLENGE_CONTEXT.md | 4-5 | readability/4 sentences | about 29 words, nested parentheses | rule 4 | verified | cosmetic | - |
| C6 | docs/CHALLENGE_CONTEXT.md | 6 | readability/4 sentences | aside plus instruction | rule 4 | verified | cosmetic | - |
| C7 | docs/CHALLENGE_CONTEXT.md | 7 | readability/4 sentences | "which rules" | idiom; "takes precedence" | verified | cosmetic | - |
| C8 | docs/CHALLENGE_CONTEXT.md | 57 | readability/4 sentences | about 40 words, nested parenthesis | rule 4 | verified | cosmetic | - |
| C9 | docs/CHALLENGE_CONTEXT.md | 61 | readability/4 sentences | three ideas, 27 words | rule 4 | verified | cosmetic | - |
| C10 | docs/CHALLENGE_CONTEXT.md | 158 | readability/4 sentences | 35 words, no subject | rule 4 | verified | cosmetic | - |
| C11 | docs/CHALLENGE_CONTEXT.md | 172 | readability/4 sentences | MRBench bullet, 35 words, two parentheses | rule 4 | verified | cosmetic | - |
| C12 | docs/CHALLENGE_CONTEXT.md | 86, 116, 144, 151 | readability/3 headings | headings name the source, not what the reader gets | rule 3 | verified | cosmetic | - |
| C13 | docs/CHALLENGE_CONTEXT.md | 118, 124, 129 | readability/3 headings | method names as bold paragraphs | missing from the TOC; make H4 | verified | cosmetic | - |
| C14 | docs/CHALLENGE_CONTEXT.md | 120 | readability/8 form | (1)(2)(3) inline | a numbered list | verified | cosmetic | - |
| C15 | docs/CHALLENGE_CONTEXT.md | 92 | readability/8 form | Q4_0, Q8_0, K-quants compared in prose | a table | verified | cosmetic | - |
| C16 | docs/CHALLENGE_CONTEXT.md | 185-197 | readability/8 form | prose pipeline in a code fence | a numbered list | verified | cosmetic | - |
| C17 | docs/CHALLENGE_CONTEXT.md | 61, 95, 98 | readability/6 steps | `llama-quantize --pure ...`, `llama-imatrix` | "..." not copyable; tools not built on the board | verified | misleading | F9 |
| C18 | docs/CHALLENGE_CONTEXT.md | 102-104 | readability/6 steps | "pick the smallest quant whose quality is acceptable" | no command, no threshold | verified | cosmetic | - |
| C19 | docs/CHALLENGE_CONTEXT.md | 210 | readability/6 steps | "swap the model file in config.env" | which keys? `BOARD_SETUP.md:1231` | verified | cosmetic | - |
| C20 | docs/CHALLENGE_CONTEXT.md | 7, 53, 57, 196, 210 | readability/9 links | repo docs as code spans | not links | verified | cosmetic | - |
| C21 | docs/CHALLENGE_CONTEXT.md | 118, 124 | readability/9 links | bare `github.com/...` | not links | verified | cosmetic | - |
| C22 | docs/CHALLENGE_CONTEXT.md | 41-64 | readability/10 duplication | §2 specs, CPU flags, ports | `UNO_Q_BOARD_REFERENCE.md:62-115,303-309`; which copy is canonical? — S3 Q3 (user): canonical-copy rule (how-to/ for our flow, UNO_Q_BOARD_REFERENCE for specs, CLAUDE.md for the red line, GOAL_MUSTS for the checklist, README for credits); the other copy links to it | verified | cosmetic | - |
| C23 | docs/CHALLENGE_CONTEXT.md | 65 | readability/11 claims | "reading speed 4-7 tok/s" | no source | verified | cosmetic | - |
| C24 | docs/CHALLENGE_CONTEXT.md | 64, 73, 74, 79 | readability/11 claims | "0.7-0.8 GB", "IFEval 51.2%", "815 MB" | no inline source — S3: 815/680 MB from the Pi 5 benchmark (Sources :240); IFEval 51.2 from the HF card google/gemma-3-270m, not in Sources | verified | cosmetic | - |
