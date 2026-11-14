# Findings: docs/UNO_Q_BOARD_REFERENCE.md

Open findings of `/docs-review`. Schema: `.claude/skills/doc-authoring/references/findings-schema.md`.

## S1 audit (2026-11-14)

Weight: heavy.

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| F1 | docs/UNO_Q_BOARD_REFERENCE.md | 9-14 | 8 contradictions | line 10: trust a board measurement; 12-14: BOARD_SETUP.md always wins | two precedence rules; a person picks one — S3: S3 Q12 (user): one rule: a measurement on our board > BOARD_SETUP > Arduino docs | verified | misleading | - |
| F2 | docs/UNO_Q_BOARD_REFERENCE.md | 138 | 6 placeholder | "⚠️ VERIFY" still on the board size | the doc settles it at 476 | verified | cosmetic | - |
| F3 | docs/UNO_Q_BOARD_REFERENCE.md | 299, 413 | 7 terminology | "tutor" for the project | `GLOSSARY.md:7-9` Copilot; avoid "tutor" | verified | cosmetic | - |
| F4 | docs/UNO_Q_BOARD_REFERENCE.md | 301, 413 | 7 terminology | "the LLM" / "LLM task" | `GLOSSARY.md:19-21` Language model; avoid "LLM" | verified | cosmetic | - |
| F5 | docs/UNO_Q_BOARD_REFERENCE.md | 422, 451 | 7 terminology | "model servers" / "Both servers" | `GLOSSARY.md:15-17` Model services | verified | cosmetic | - |
| F6 | docs/UNO_Q_BOARD_REFERENCE.md | 44, 197 | 7 terminology | "board" for the whole PCB with MCU | `GLOSSARY.md:11-13` "the board" is the Linux side — S3 Q9 (user): glossary: Copilot (tutor only in the papers' sense), Validation set (no dev/hold-out set), UNO Q = whole board, logit distillation, M3Kang, Token, Junction, Organizers/hidden test | verified | cosmetic | - |
| F7 | docs/UNO_Q_BOARD_REFERENCE.md | 334 | 3 renamed | LLM Brick row: "our measurements: see `unoq-board` skill" | `.claude/skills/unoq-board/SKILL.md:51-53` never measures the Brick | verified | misleading | - |
| F8 | docs/UNO_Q_BOARD_REFERENCE.md | 397 | 8 contradictions | labels 11 and 5-6 tok/s "Our measurement" | organizers' figures (`BOARD_SETUP.md:499-500`); the team's are 10.1/4.8 at 515-516 | verified | misleading | - |
| F9 | docs/UNO_Q_BOARD_REFERENCE.md | 449 | 1 stale | flag list stops at `--reasoning off` | `board/systemd/math-llm.service:8` also has `--reasoning-budget 0`, `--alias` | verified | misleading | - |
| F10 | docs/UNO_Q_BOARD_REFERENCE.md | 450 | 8 contradictions | "LLM Brick or own server?" cited as open | `docs/CHALLENGE_CONTEXT.md:53,57` settles it: own llama-server | verified | cosmetic | - |
| F11 | docs/UNO_Q_BOARD_REFERENCE.md | 455 | 8 contradictions | internet needed only for steps 2-4 | step 8.1 clones on the board (`BOARD_SETUP.md:686`); 224 offers scp — S3: step 8.1 clones on the board, so internet is needed after step 4 unless scp/adb push | verified | cosmetic | - |
| F12 | docs/UNO_Q_BOARD_REFERENCE.md | 460 | 8 contradictions | Debian 13 "trixie" marked "inferred" | §14.1 (492) measured it | verified | cosmetic | - |
| F13 | docs/UNO_Q_BOARD_REFERENCE.md | 466 | 8 contradictions | resolved CPU-flags row in the "still open" table | the row says Resolved (§14.2) | verified | cosmetic | - |
| F14 | docs/UNO_Q_BOARD_REFERENCE.md | 469-470 | 1 stale | "Run `llama-bench`" | the build makes only llama-server and llama-cli (`board/02_build_llama_cpp.sh:27`) | verified | breaks | - |
| F15 | docs/UNO_Q_BOARD_REFERENCE.md | 544-546 | 8 contradictions | the board uses the organizers' clone, not Santolina_tutor | `BOARD_SETUP.md:684-690`, `docs/how-to/deploy-copilot-on-board.md:15-25` use ~/Santolina_tutor; only a person knows the board's state — S3: S3 Q13 (user): the board now runs ~/Santolina_tutor; §14.5 becomes the history of the first setup | verified | misleading | F1 |
| F16 | docs/UNO_Q_BOARD_REFERENCE.md | 547 | 8 contradictions | "byte-identical for steps 0 to 8" | `BOARD_SETUP.md:10-14` lists local edits | verified | cosmetic | F15 |
| F17 | docs/UNO_Q_BOARD_REFERENCE.md | 557-558 | 8 contradictions | step 9 takes about 70 min for eng+cat | `BOARD_SETUP.md:739` about 15 min per language — S3: S3 Q14 (user): our §14 measurements are the reference; BOARD_SETUP figures quoted as the organizers' | verified | cosmetic | F1 |
| F18 | docs/UNO_Q_BOARD_REFERENCE.md | 46, 503 | 10 formatting | bare code fences | no language tag | verified | cosmetic | - |
| F19 | docs/UNO_Q_BOARD_REFERENCE.md | 301-309, 313-367, 371-401, 434-478, 537-558 | 11 type-mixing | reference with how-to steps (§7.1, §8, §9, §14.5) and explanation (§6.3, §13) | one document, one type (`diataxis`) — S3 Q4 (user): no split; the lede states the type and steps go to a final "What to try" section | verified | cosmetic | - |

Incidental: external links and datasheet figures not checked.

## S2 critique (2026-11-14)

Type: reference, heavy. 25 findings (0 breaks, 7 misleading, 18 cosmetic).

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| C1 | docs/UNO_Q_BOARD_REFERENCE.md | 7 | readability/11 claims | "facts are tagged with their source" | the §3.1-§8 tables (64-367) have no source column | verified | misleading | - |
| C2 | docs/UNO_Q_BOARD_REFERENCE.md | 93, 398 | readability/11 claims | "About 3.6 GB free" | 451, 494: 3.6 GiB is the total; 2.9-3.1 GiB available | verified | misleading | - |
| C3 | docs/UNO_Q_BOARD_REFERENCE.md | 162-163 | readability/6 steps | "Bridge two pins on JCTL" for host mode | which pins is not said (1.8 V header) — S3: Arduino host-mode guide: short GND (JCTL 1 or 7) with VOL_DOWN (JCTL 3) | verified | misleading | - |
| C4 | docs/UNO_Q_BOARD_REFERENCE.md | 263-266 | readability/11 claims | JMISC 28-42 audio and 37-52 GPIO | ranges overlap at 37-42 — S3: datasheet interleaves: audio 28-34 (not 35), 36, 38, 40, 42; GPIO 37, 39, 41, 43, 45-52 | verified | misleading | - |
| C5 | docs/UNO_Q_BOARD_REFERENCE.md | 542-543 | readability/6 steps | "run with nohup ... check ~/llama-build.log for BUILD_EXIT=0" | no command; nothing in the repo writes that log | verified | misleading | F19 |
| C6 | docs/UNO_Q_BOARD_REFERENCE.md | 554-556 | readability/6 steps | four Fedora actions in one sentence; a udev rule never given | no rule file, no check | verified | misleading | - |
| C7 | docs/UNO_Q_BOARD_REFERENCE.md | 553 | readability/6 steps | `tar -xf ... -C ~/Applications` | "..." not copyable | verified | cosmetic | - |
| C8 | docs/UNO_Q_BOARD_REFERENCE.md | 388-390 | readability/6 steps | runs a Q4_K_M model never downloaded | fails at 388 | verified | misleading | F19 |
| C9 | docs/UNO_Q_BOARD_REFERENCE.md | 453, 523 | readability/11 claims | BOARD_SETUP writing speed "5" and "5-6 tok/s" | `BOARD_SETUP.md:500,1024` about 6 | verified | cosmetic | F8 |
| C10 | docs/UNO_Q_BOARD_REFERENCE.md | 3-5 | readability/1 lede | does not say who reads it or when to use it instead of BOARD_SETUP | rule 1 | verified | cosmetic | F1 |
| C11 | docs/UNO_Q_BOARD_REFERENCE.md | 5 | readability/5 jargon | "SBC" expanded only at 572 | `GLOSSARY.md:13` avoid SBC | verified | cosmetic | - |
| C12 | docs/UNO_Q_BOARD_REFERENCE.md | 44-49 | readability/5 jargon | MPU, MCU never expanded | rule 5 | verified | cosmetic | - |
| C13 | docs/UNO_Q_BOARD_REFERENCE.md | 55 | readability/5 jargon | "App Lab apps" | explained only at 331 | verified | cosmetic | - |
| C14 | docs/UNO_Q_BOARD_REFERENCE.md | 373, 395, 518 | readability/5 jargon | Q4_K_M, Q8_0, GGUF, tok/s, "grammar-constrained" | never explained | verified | cosmetic | - |
| C15 | docs/UNO_Q_BOARD_REFERENCE.md | 28, 107, 172 | readability/5 jargon | TARIC, EIRP, PMIC, LDO | never expanded | verified | cosmetic | - |
| C16 | docs/UNO_Q_BOARD_REFERENCE.md | 436-437 | readability/4 sentences | "Each row below was a conflict ... and how BOARD_SETUP.md settles it." | ungrammatical, two ideas | verified | cosmetic | - |
| C17 | docs/UNO_Q_BOARD_REFERENCE.md | 321-322 | readability/4 sentences | 25 words, three ideas | rule 4 | verified | cosmetic | - |
| C18 | docs/UNO_Q_BOARD_REFERENCE.md | 449 | readability/4 sentences | "Default flags got the server killed" | hides the actor (the kernel OOM killer) | verified | cosmetic | F9 |
| C19 | docs/UNO_Q_BOARD_REFERENCE.md | 549 | readability/3 headings | "14.6 The laptop side" under "14. Measured on our board" | laptop content under a board heading | verified | cosmetic | - |
| C20 | docs/UNO_Q_BOARD_REFERENCE.md | 419-422 | readability/8 form | 11 hardening topics in one sentence | a list | verified | cosmetic | - |
| C21 | docs/UNO_Q_BOARD_REFERENCE.md | 254-257 | readability/8 form | §5.3 pin lists as prose | §5.1-5.2 use tables | verified | cosmetic | - |
| C22 | docs/UNO_Q_BOARD_REFERENCE.md | 466 | readability/8 form | "~~CPU flags~~" | no pymdownx.tilde; tildes render as text | verified | cosmetic | F13 |
| C23 | docs/UNO_Q_BOARD_REFERENCE.md | 9-10, 16, 375, 401 | readability/9 links | repo docs named as code spans, not links | readers cannot click through | verified | cosmetic | - |
| C24 | docs/UNO_Q_BOARD_REFERENCE.md | 198, 349, 361, 411, 567, 579-580 | readability/9 links | guides and URLs without links or scheme | rule 9 | verified | cosmetic | - |
| C25 | docs/UNO_Q_BOARD_REFERENCE.md | 64-75, 301-309, 507-509 | readability/10 duplication | specs and CPU-flag conclusions | `CHALLENGE_CONTEXT.md:42-50,60`, `GUIA_RESTRICCIONES_UNOQ.html:199-202`; which copy is canonical? — S3 Q3 (user): canonical-copy rule (how-to/ for our flow, UNO_Q_BOARD_REFERENCE for specs, CLAUDE.md for the red line, GOAL_MUSTS for the checklist, README for credits); the other copy links to it | verified | cosmetic | - |
