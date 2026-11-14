# Findings: docs/RESUMEN_QUALCOMM_UNO_Q.md

Open findings of `/docs-review`. Schema: `.claude/skills/doc-authoring/references/findings-schema.md`.

## S1 audit (2026-11-14)

Weight: heavy. Language: Spanish.

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| F1 | docs/RESUMEN_QUALCOMM_UNO_Q.md | 4-6 | 3 renamed | note on branch docs-skills-orchestrator and where the files live | origin/main has both files in docs/ | verified | cosmetic | - |
| F2 | docs/RESUMEN_QUALCOMM_UNO_Q.md | 40-42, 95, 144 | 8 contradictions | the Qualcomm README and its URL are not available | `BOARD_SETUP.md:3-5` is that README, with its URL | verified | misleading | - |
| F3 | docs/RESUMEN_QUALCOMM_UNO_Q.md | 50, 145 | 8 contradictions | embedding model "VGA small", to verify | `config.env:25-28` bge-small-en-v1.5 | verified | cosmetic | F2 |
| F4 | docs/RESUMEN_QUALCOMM_UNO_Q.md | 54, 145 | 8 contradictions | service names "mac lm" / "mac embed", to verify | `board/systemd/math-llm.service`, `math-embed.service` | verified | cosmetic | F2 |
| F5 | docs/RESUMEN_QUALCOMM_UNO_Q.md | 97, 145 | 8 contradictions | "Marel Rob", probably Marcelo Rovai | `BOARD_SETUP.md:50,1268` Marcelo Rovai | verified | cosmetic | F2 |
| F6 | docs/RESUMEN_QUALCOMM_UNO_Q.md | 147 | 8 contradictions | board variant 2 or 4 GB unknown | `BOARD_SETUP.md:29,73`, `UNO_Q_BOARD_REFERENCE.md:1,25` 4 GB, ABX00173 | verified | misleading | F2 |
| F7 | docs/RESUMEN_QUALCOMM_UNO_Q.md | 146 | 8 contradictions | 108 vs 106 languages, ~2,000 problems open | `BOARD_SETUP.md:715` 1,747 problems, 108 languages | verified | misleading | F2 |
| F8 | docs/RESUMEN_QUALCOMM_UNO_Q.md | 136 | 8 contradictions | CHALLENGE_CONTEXT's server is the LLM Brick on 9999 | `CHALLENGE_CONTEXT.md:53,57` own llama-server on 8081/8082 | verified | misleading | - |
| F9 | docs/RESUMEN_QUALCOMM_UNO_Q.md | 47 | 8 contradictions | connect with ADB, SSH as alternative | `BOARD_SETUP.md:129-141` SSH first, adb as fallback | verified | cosmetic | - |
| F10 | docs/RESUMEN_QUALCOMM_UNO_Q.md | 57 | 1 stale | retrieval mode `rag1` | `predict.py:26` flag is `--rag K` | verified | cosmetic | - |
| F11 | docs/RESUMEN_QUALCOMM_UNO_Q.md | 56 | 8 contradictions | laptop: venv + pip install (as in the video) | `BOARD_SETUP.md:11-13,728-736` uses `uv run --no-project` — S3: S3 Q20 (user): keep "the video says" and add a note with the repo rule (uv run) | verified | cosmetic | F2 |
| F12 | docs/RESUMEN_QUALCOMM_UNO_Q.md | 92, 119 | 8 contradictions | microphone, webcam, USB hub on request (as in the video) | `BOARD_SETUP.md:1160` no external modules, LED matrix only — S3: S3 Q20 (user): keep "the video says" and add a note: BOARD_SETUP allows no external modules | verified | misleading | - |
| F13 | docs/RESUMEN_QUALCOMM_UNO_Q.md | 84 | 8 contradictions | model size limits open | `BOARD_SETUP.md:1099` | verified | cosmetic | F2 |
| F14 | docs/RESUMEN_QUALCOMM_UNO_Q.md | 52 | 8 contradictions | step 7 statement omitted because it was a real Kangaroo problem | the video's prompt is the toy arithmetic example of `BOARD_SETUP.md:512`, not M3Kang — S3: S3 Q20 (user): say the step-7 example was a toy arithmetic question, without copying it | verified | cosmetic | - |
| F15 | docs/RESUMEN_QUALCOMM_UNO_Q.md | 104-113 | 8 duplication | second deliverables checklist | `GOAL_MUSTS.md:3` claims to be the single list — S3 Q3 (user): canonical-copy rule (how-to/ for our flow, UNO_Q_BOARD_REFERENCE for specs, CLAUDE.md for the red line, GOAL_MUSTS for the checklist, README for credits); the other copy links to it | verified | cosmetic | - |
| F16 | docs/RESUMEN_QUALCOMM_UNO_Q.md | 1-147 | 11 type-mixing | video summary mixed with a how-to checklist (§5) | - — S3 Q4 (user): no split; the lede states the type and steps go to a final "What to try" section | verified | cosmetic | F15 |

Incidental: the video transcript `docs/UPC Datathon - Qualcomm Challenge step by step Arduino UNO Q setup.txt` is tracked and served; only parts were checked for M3Kang text.

## S2 critique (2026-11-14)

Type: explanation (video summary), heavy, Spanish. 24 findings (0 breaks, 4 misleading, 20 cosmetic).

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| C1 | docs/RESUMEN_QUALCOMM_UNO_Q.md | 3-9 | readability/1 lede | provenance and conventions first | never says who it is for | verified | cosmetic | - |
| C2 | docs/RESUMEN_QUALCOMM_UNO_Q.md | 19 | readability/9 links | "(ver §4)" | §4 is resources; the open questions are §7 | verified | misleading | - |
| C3 | docs/RESUMEN_QUALCOMM_UNO_Q.md | 39, 58, 60, 115 | readability/3 headings | "paso 13" means two things | BOARD_SETUP's Step 13 is a third | verified | misleading | - |
| C4 | docs/RESUMEN_QUALCOMM_UNO_Q.md | 106 | readability/6 steps | "Completar el setup (pasos 1-10)" | which numbering? | verified | misleading | F2 |
| C5 | docs/RESUMEN_QUALCOMM_UNO_Q.md | 44-60 | readability/10 duplication | §2 step table | re-tells `BOARD_SETUP.md:78-98` with other numbers — S3 Q3 (user): canonical-copy rule (how-to/ for our flow, UNO_Q_BOARD_REFERENCE for specs, CLAUDE.md for the red line, GOAL_MUSTS for the checklist, README for credits); the other copy links to it | verified | cosmetic | F2 |
| C6 | docs/RESUMEN_QUALCOMM_UNO_Q.md | 115-120 | readability/10 duplication | speaker's ideas | `BOARD_SETUP.md:1032-1100` — S3 Q3 (user): canonical-copy rule (how-to/ for our flow, UNO_Q_BOARD_REFERENCE for specs, CLAUDE.md for the red line, GOAL_MUSTS for the checklist, README for credits); the other copy links to it | verified | cosmetic | - |
| C7 | docs/RESUMEN_QUALCOMM_UNO_Q.md | 19, 72, 84, 113, 142, 143 | readability/10 duplication | "no hay criterios", "fecha ambigua" 3-4 times | keep in §7 | verified | cosmetic | - |
| C8 | docs/RESUMEN_QUALCOMM_UNO_Q.md | 3-5 | readability/9 links | the `.txt` transcript is not linked | it is in docs/ | verified | cosmetic | F1 |
| C9 | docs/RESUMEN_QUALCOMM_UNO_Q.md | 81, 130, 132 | readability/9 links | `CHALLENGE_CONTEXT.md` as code span | not clickable | verified | cosmetic | - |
| C10 | docs/RESUMEN_QUALCOMM_UNO_Q.md | 97 | readability/8 form | three references in one cell, no links | `BOARD_SETUP.md:50-51` has them | verified | cosmetic | F5 |
| C11 | docs/RESUMEN_QUALCOMM_UNO_Q.md | 81 | readability/8 form | four metric groups in one sentence | a list | verified | cosmetic | - |
| C12 | docs/RESUMEN_QUALCOMM_UNO_Q.md | 18 | readability/5 jargon | "lee a ~11 tok/s y escribe a ~5 tok/s" | tok/s and the metaphor not explained | verified | cosmetic | - |
| C13 | docs/RESUMEN_QUALCOMM_UNO_Q.md | 50, 56, 97 | readability/5 jargon | "SLM" | never expanded | verified | cosmetic | - |
| C14 | docs/RESUMEN_QUALCOMM_UNO_Q.md | 53, 57 | readability/5 jargon | "Base del RAG", "índice RAG" | not explained | verified | cosmetic | - |
| C15 | docs/RESUMEN_QUALCOMM_UNO_Q.md | 47-92 | readability/5 jargon | ADB, systemd, "projector file", "estado zombi", "40 TOPS" | not explained | verified | cosmetic | - |
| C16 | docs/RESUMEN_QUALCOMM_UNO_Q.md | 51 | readability/5 jargon | "Fija el baseline de velocidad." | `GLOSSARY.md:31-33` Baseline is accuracy | verified | cosmetic | - |
| C17 | docs/RESUMEN_QUALCOMM_UNO_Q.md | 15-128 | readability/7 language | "copilot" in Spanish text | `GOAL_MUSTS.md:20` uses "copiloto" — S3 Q5 (user): English with US spelling, so "1,747" and "copilot" are correct | dismissed | cosmetic | - |
| C18 | docs/RESUMEN_QUALCOMM_UNO_Q.md | 130, 135 | readability/7 language | "afinar/podar/cuantizar" vs "Fine-tune, poda" | mixed | verified | cosmetic | - |
| C19 | docs/RESUMEN_QUALCOMM_UNO_Q.md | 13 | readability/3 headings | "TL;DR" | "Resumen" | verified | cosmetic | - |
| C20 | docs/RESUMEN_QUALCOMM_UNO_Q.md | 28 | readability/5 jargon | "M3Kang, modelo/dataset" | it is a dataset | verified | cosmetic | - |
| C21 | docs/RESUMEN_QUALCOMM_UNO_Q.md | 32-33 | readability/11 claims | "(inferido)" on what line 75 quotes as speech | tag misused | verified | misleading | - |
| C22 | docs/RESUMEN_QUALCOMM_UNO_Q.md | 130 | readability/4 sentences | about 35 words, semicolon, parenthesis | rule 4 | verified | cosmetic | - |
| C23 | docs/RESUMEN_QUALCOMM_UNO_Q.md | 16 | readability/4 sentences | "se fallan" hides who fails | rule 4 | verified | cosmetic | - |
| C24 | docs/RESUMEN_QUALCOMM_UNO_Q.md | 63 | readability/6 steps | "localizarlo con `ps` y matarlo" | no command; link `BOARD_SETUP.md:164-170` | verified | cosmetic | - |
