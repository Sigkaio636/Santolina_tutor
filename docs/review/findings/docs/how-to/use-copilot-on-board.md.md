# Findings: docs/how-to/use-copilot-on-board.md

Open findings of `/docs-review`. Schema: `.claude/skills/doc-authoring/references/findings-schema.md`.

## S1 audit (2026-11-14)

Weight: heavy.

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| F1 | docs/how-to/use-copilot-on-board.md | 5 | 7 terminology | "tutor" given as a synonym of copilot | `GLOSSARY.md:9` — S3 Q9 (user): glossary: Copilot (tutor only in the papers' sense), Validation set (no dev/hold-out set), UNO Q = whole board, logit distillation, M3Kang, Token, Junction, Organizers/hidden test | verified | cosmetic | - |
| F2 | docs/how-to/use-copilot-on-board.md | 38, 81, 90, 94 | 7 terminology | "the model" | `GLOSSARY.md:19-21` Language model | verified | cosmetic | - |
| F3 | docs/how-to/use-copilot-on-board.md | 62, 72, 75, 77 | 7 terminology | "run" alone | `GLOSSARY.md:47-49` Experiment | verified | cosmetic | - |
| F4 | docs/how-to/use-copilot-on-board.md | 77 | 8 contradictions | "all 281 validation problems" | 281 is English-only (`docs/BOARD_SETUP.md:760-761`); step 9 keeps eng,cat — S3: val.jsonl holds about 281 eng + 281 cat rows; 281 is English only | verified | misleading | - |
| F5 | docs/how-to/use-copilot-on-board.md | 90 | 8 contradictions | about 10 tok/s | `BOARD_SETUP.md:42,499,896` say 11-12; `UNO_Q_BOARD_REFERENCE.md:515` measured 10.1 — S3: S3 Q14 (user): 10.1 tok/s read, 4.8 tok/s write (UNO_Q_BOARD_REFERENCE §14) | verified | cosmetic | - |
| F6 | docs/how-to/use-copilot-on-board.md | 122 | 8 contradictions | the two services use about 1 GB | `BOARD_SETUP.md:663` about 1.1 GB — S3: S3 Q14 (user): about 920 MiB for the two services (UNO_Q_BOARD_REFERENCE §14) | verified | cosmetic | - |

## S2 critique (2026-11-14)

Type: how-to, heavy. 24 findings (0 breaks, 5 misleading, 19 cosmetic).

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| C1 | docs/how-to/use-copilot-on-board.md | 3 | readability/1 lede | does not say who it is for | rule 1 | verified | cosmetic | - |
| C2 | docs/how-to/use-copilot-on-board.md | 30-47, 57-63, 146-148 | readability/2 one type | contract rules, reference tables and a roadmap note inside a how-to | split or link `GLOSSARY.md:27-28` — S3 Q4 (user): no split; the lede states the type and steps go to a final "What to try" section | verified | cosmetic | - |
| C3 | docs/how-to/use-copilot-on-board.md | 25 | readability/6 steps | first command answers all of val.jsonl | no time warning (about 45 min) and no check | verified | misleading | - |
| C4 | docs/how-to/use-copilot-on-board.md | 85 | readability/6 steps | `--output results/predictions.csv` again | overwrites the line-25 output without warning | verified | cosmetic | - |
| C5 | docs/how-to/use-copilot-on-board.md | 47 | readability/4 sentences | "The limits are in TIME_LIMIT_SECONDS and FALLBACK_ANSWER" | the fallback is a letter, not a limit | verified | cosmetic | - |
| C6 | docs/how-to/use-copilot-on-board.md | 75 | readability/5 jargon | "the results table in the README" | which README? | verified | cosmetic | - |
| C7 | docs/how-to/use-copilot-on-board.md | 77 | readability/11 claims | "about 45 minutes"; "50 problems or fewer is weak evidence" | no source — S3: cite BOARD_SETUP step 11 (:856) for 45 min per 281 problems and the publish-project skill for the 50-problem rule | verified | cosmetic | F4 |
| C8 | docs/how-to/use-copilot-on-board.md | 81 | readability/4 sentences | "Retrieval shows the model solved problems that look like the new one." | garden path ("proves the model solved") | verified | cosmetic | - |
| C9 | docs/how-to/use-copilot-on-board.md | 94 | readability/5 jargon | "OCR" not expanded | - | verified | cosmetic | - |
| C10 | docs/how-to/use-copilot-on-board.md | 18, 94 | readability/6 steps | the explorer shows similar problems, but index.db is tied only to retrieval | without it the explorer shows none (`explorer/server.py:88,141`) | verified | misleading | - |
| C11 | docs/how-to/use-copilot-on-board.md | 96 | readability/6 steps | "make them with --save-images, then copy data/images" | two actions, no command | verified | misleading | - |
| C12 | docs/how-to/use-copilot-on-board.md | 101 | readability/6 steps | `python3 explorer/server.py` | no expected output | verified | cosmetic | - |
| C13 | docs/how-to/use-copilot-on-board.md | 107 | readability/6 steps | `ssh -L ... arduino@<board-ip>` | `<` is a redirect; the tunnel must stay open | verified | misleading | - |
| C14 | docs/how-to/use-copilot-on-board.md | 120 | readability/3 headings | "Free memory for an experiment" | the body frees a port | verified | cosmetic | - |
| C15 | docs/how-to/use-copilot-on-board.md | 122 | readability/4 sentences | two ideas; "the service" singular, the command stops both | rule 4 | verified | cosmetic | - |
| C16 | docs/how-to/use-copilot-on-board.md | 125 | readability/6 steps | `systemctl stop` with no check | `systemctl is-active` | verified | cosmetic | - |
| C17 | docs/how-to/use-copilot-on-board.md | 134 | readability/5 jargon | "servers that other people started" | never says the board may be shared | verified | cosmetic | - |
| C18 | docs/how-to/use-copilot-on-board.md | 22, 138, 152 | readability/5 jargon | "organizers", "hidden test set", "jury" | the datathon is never introduced | verified | cosmetic | - |
| C19 | docs/how-to/use-copilot-on-board.md | 148 | readability/5 jargon | "The Teach interface" | undefined; the step 13 link has no anchor | verified | cosmetic | - |
| C20 | docs/how-to/use-copilot-on-board.md | 22-47 | readability/10 duplication | predict.py, CSV columns, contract | `BOARD_SETUP.md:821-841` — S3 Q3 (user): canonical-copy rule (how-to/ for our flow, UNO_Q_BOARD_REFERENCE for specs, CLAUDE.md for the red line, GOAL_MUSTS for the checklist, README for credits); the other copy links to it | verified | cosmetic | - |
| C21 | docs/how-to/use-copilot-on-board.md | 51-77 | readability/10 duplication | eval.py usage | `BOARD_SETUP.md:845-856` — S3 Q3 (user): canonical-copy rule (how-to/ for our flow, UNO_Q_BOARD_REFERENCE for specs, CLAUDE.md for the red line, GOAL_MUSTS for the checklist, README for credits); the other copy links to it | verified | cosmetic | F4 |
| C22 | docs/how-to/use-copilot-on-board.md | 79-90 | readability/10 duplication | retrieval | `BOARD_SETUP.md:887-896` — S3 Q3 (user): canonical-copy rule (how-to/ for our flow, UNO_Q_BOARD_REFERENCE for specs, CLAUDE.md for the red line, GOAL_MUSTS for the checklist, README for credits); the other copy links to it | verified | cosmetic | F5 |
| C23 | docs/how-to/use-copilot-on-board.md | 92-118 | readability/10 duplication | explorer section | `BOARD_SETUP.md:936-969`; the copies already disagree on `--host` — S3 Q3 (user): canonical-copy rule (how-to/ for our flow, UNO_Q_BOARD_REFERENCE for specs, CLAUDE.md for the red line, GOAL_MUSTS for the checklist, README for credits); the other copy links to it | verified | misleading | - |
| C24 | docs/how-to/use-copilot-on-board.md | 136-144 | readability/10 duplication | demo checklist | `BOARD_SETUP.md:1180-1185` — S3 Q3 (user): canonical-copy rule (how-to/ for our flow, UNO_Q_BOARD_REFERENCE for specs, CLAUDE.md for the red line, GOAL_MUSTS for the checklist, README for credits); the other copy links to it | verified | cosmetic | - |
