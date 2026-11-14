# Findings: docs/how-to/deploy-copilot-on-board.md

Open findings of `/docs-review`. Schema: `.claude/skills/doc-authoring/references/findings-schema.md`.

## S1 audit (2026-11-14)

Weight: heavy.

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| F1 | docs/how-to/deploy-copilot-on-board.md | 5 | 7 terminology | "tutor" given as a synonym of copilot | `GLOSSARY.md:9` avoid "tutor" — S3 Q9 (user): glossary: Copilot (tutor only in the papers' sense), Validation set (no dev/hold-out set), UNO Q = whole board, logit distillation, M3Kang, Token, Junction, Organizers/hidden test | verified | cosmetic | - |
| F2 | docs/how-to/deploy-copilot-on-board.md | 11, 19-23 | 8 contradictions | prerequisite steps 0-8 done, then step 1 clones into ~/Santolina_tutor | `docs/BOARD_SETUP.md:684-688` (8.1) already clones there; the second clone fails | verified | breaks | - |
| F3 | docs/how-to/deploy-copilot-on-board.md | 29-39 | 8 contradictions | `scp -r` / `adb push` the folder, then "do not copy data/ this way" | both commands copy data/, .venv, models/; .gitignore does not filter them | verified | misleading | - |
| F4 | docs/how-to/deploy-copilot-on-board.md | 76 | 1 stale | "a hook blocks `git add` for them" | the hook is a Claude Code hook (`.claude/hooks/m3kang-guard.py:11-14`); a person's own git add is not blocked | verified | misleading | - |
| F5 | docs/how-to/deploy-copilot-on-board.md | 96 | 1 stale | `wc -l` must match the counts prepare_m3kang.py printed | `laptop/prepare_m3kang.py:223-224` prints per split and language; the reader must add them | verified | cosmetic | - |
| F6 | docs/how-to/deploy-copilot-on-board.md | 117 | 7 terminology | "both servers" | `GLOSSARY.md:15-17` Model services | verified | cosmetic | - |
| F7 | docs/how-to/deploy-copilot-on-board.md | 119-132 | 2 snippets | sample smoke-test output | `predict.py:48-49` prints one line per problem; `board/05_smoke_test.sh:38` adds "Next: ..." | verified | misleading | - |
| F8 | docs/how-to/deploy-copilot-on-board.md | 134-138 | 2 snippets | check each answer A-E and status ok | the shown output has neither; they are in predict.py stderr and results/smoke.csv | verified | misleading | F7 |
| F9 | docs/how-to/deploy-copilot-on-board.md | 162 | 1 stale | `pkill llama-server` for hand-started servers | also kills the services (`board/systemd/math-llm.service:9`); 65-69 use `kill <pid>` — S3: both units run llama-server (board/common.sh:10); pkill stops them and they stay down | verified | misleading | - |
| F10 | docs/how-to/deploy-copilot-on-board.md | 165 | 1 stale | 03_download_models.sh deletes the bad file and downloads again | `board/03_download_models.sh:17-25` deletes the bad .part and exits; run it again | verified | cosmetic | - |
| F11 | docs/how-to/deploy-copilot-on-board.md | 166 | 8 contradictions | empty host keys: `sudo ssh-keygen -A && sudo systemctl restart ssh` | `board/00_check_board.sh:31` deletes the empty keys first — S3: ssh-keygen -A skips existing empty files; fix is rm -f /etc/ssh/ssh_host_* first (board/00_check_board.sh:31) | verified | misleading | - |

## S2 critique (2026-11-14)

Type: how-to, heavy. 21 findings (0 breaks, 4 misleading, 17 cosmetic).

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| C1 | docs/how-to/deploy-copilot-on-board.md | 3 | readability/1 lede | does not say who the guide is for | rule 1 | verified | cosmetic | - |
| C2 | docs/how-to/deploy-copilot-on-board.md | 12, 30, 81 | readability/6 steps | `<board-ip>` inside pasteable commands | bash reads `<` as a redirect; how to find the IP (`BOARD_SETUP.md:119`) not linked | verified | misleading | - |
| C3 | docs/how-to/deploy-copilot-on-board.md | 12 | readability/5 jargon | "`adb shell`" not explained | `BOARD_SETUP.md:139` explains it | verified | cosmetic | - |
| C4 | docs/how-to/deploy-copilot-on-board.md | 13 | readability/5 jargon | "the M3Kang files", no link | CLAUDE.md asks for the dataset card link | verified | cosmetic | - |
| C5 | docs/how-to/deploy-copilot-on-board.md | 15-51 | readability/6 steps | step 1 bundles clone, offline copy, older copy, a note and a health check | one action per step | verified | misleading | - |
| C6 | docs/how-to/deploy-copilot-on-board.md | 45-51 | readability/6 steps | the read-only board check comes after the clone | should be the first step | verified | cosmetic | - |
| C7 | docs/how-to/deploy-copilot-on-board.md | 30, 36 | readability/6 steps | `scp -r` / `adb push Santolina_tutor` "on your laptop" | work only from the repo's parent folder | verified | misleading | - |
| C8 | docs/how-to/deploy-copilot-on-board.md | 41 | readability/5 jargon | "the organizers' copy" | the guide never introduces the organizers | verified | cosmetic | - |
| C9 | docs/how-to/deploy-copilot-on-board.md | 53-72 | readability/3 headings | step 2 is upkeep, numbered as a first-deploy step | 57-60, 72 repeat the table at 152-153 | verified | cosmetic | - |
| C10 | docs/how-to/deploy-copilot-on-board.md | 63 | readability/6 steps | `04_install_services.sh` with no check | the script prints "ready on 127.0.0.1:<port>" (`board/04_install_services.sh:39-43`) | verified | cosmetic | - |
| C11 | docs/how-to/deploy-copilot-on-board.md | 67-69 | readability/6 steps | `pgrep -a llama-server`, then `kill <pid>` | pgrep also lists service PIDs; the script prints the exact kill command | verified | misleading | - |
| C12 | docs/how-to/deploy-copilot-on-board.md | 55 | readability/5 jargon | "pins", SHA256, "the 60-second limit" | not explained | verified | cosmetic | - |
| C13 | docs/how-to/deploy-copilot-on-board.md | 25, 78, 167 | readability/6 steps | "every later command runs from ~/Santolina_tutor" | step 3 and row 167 run on the laptop; 2, 4, 5 do not say which machine | verified | cosmetic | - |
| C14 | docs/how-to/deploy-copilot-on-board.md | 100 | readability/5 jargon | "if you want to use `--rag`" | which program takes it? | verified | cosmetic | - |
| C15 | docs/how-to/deploy-copilot-on-board.md | 106 | readability/5 jargon | "OCR" not expanded | `BOARD_SETUP.md:717` expands it | verified | cosmetic | - |
| C16 | docs/how-to/deploy-copilot-on-board.md | 103 | readability/6 steps | `build_index.py` with no check or duration | it prints "Wrote data/index.db ... in N s" (`build_index.py:40`) | verified | cosmetic | - |
| C17 | docs/how-to/deploy-copilot-on-board.md | 163 | readability/6 steps | the fix names only `math-llm` | `math-embed` needs the same | verified | cosmetic | - |
| C18 | docs/how-to/deploy-copilot-on-board.md | 19-25, 43 | readability/10 duplication | clone and stdlib note | `BOARD_SETUP.md:684-692` — S3 Q3 (user): canonical-copy rule (how-to/ for our flow, UNO_Q_BOARD_REFERENCE for specs, CLAUDE.md for the red line, GOAL_MUSTS for the checklist, README for credits); the other copy links to it | verified | cosmetic | F2 |
| C19 | docs/how-to/deploy-copilot-on-board.md | 78-94 | readability/10 duplication | copy train/val and `wc -l` | `BOARD_SETUP.md:793-813` — S3 Q3 (user): canonical-copy rule (how-to/ for our flow, UNO_Q_BOARD_REFERENCE for specs, CLAUDE.md for the red line, GOAL_MUSTS for the checklist, README for credits); the other copy links to it | verified | cosmetic | F5 |
| C20 | docs/how-to/deploy-copilot-on-board.md | 102-109 | readability/10 duplication | `build_index.py` | `BOARD_SETUP.md:881-885` — S3 Q3 (user): canonical-copy rule (how-to/ for our flow, UNO_Q_BOARD_REFERENCE for specs, CLAUDE.md for the red line, GOAL_MUSTS for the checklist, README for credits); the other copy links to it | verified | cosmetic | - |
| C21 | docs/how-to/deploy-copilot-on-board.md | 159-167 | readability/10 duplication | the fix table | `BOARD_SETUP.md:1251-1259` — S3 Q3 (user): canonical-copy rule (how-to/ for our flow, UNO_Q_BOARD_REFERENCE for specs, CLAUDE.md for the red line, GOAL_MUSTS for the checklist, README for credits); the other copy links to it | verified | cosmetic | F9, F11 |
