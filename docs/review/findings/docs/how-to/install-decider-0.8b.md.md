# Findings: docs/how-to/install-decider-0.8b.md

Review round 2026-11-15. Cross-cutting decisions: `docs/review/findings/_cross-cutting.md`.

Moved from `docs/INSTALL_DECIDER.md` in S4 (decision C4). S1-S3 were validated
under the old path on 2026-11-15 and carried over. S4 fixed and deleted F1-F5
and C1-C4, C6-C8, C10-C13, C15-C32. The findings below stay.

## Open or settled without an edit

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| C5 | docs/how-to/install-decider-0.8b.md | 19-36, 79-93 | 10 duplication | llama.cpp clone/build and scp/adb block duplicate how-to/use-decider-2b-router.md | S3: each how-to stays self-contained | wontfix | cosmetic | - |
| C9 | GLOSSARY.md | - | 5 jargon | decider-0.8b, decider-2b, Mapika, llama.cpp, bf16, intent router are not in GLOSSARY.md | GLOSSARY.md belongs to the main session; reported there | open | cosmetic | - |
| C14 | docs/how-to/install-decider-0.8b.md | 28 | 6 steps | `cmake -B build` without build type | llama.cpp CMakeLists.txt:30-31 at 2cbe0ec sets `CMAKE_BUILD_TYPE=Release` when none is given (GitHub, read 2026-11-15) | no change needed | - | - |

## Out of scope, reported to the main session

- `docs/BOARD_SETUP.md` step 11.1 says `predict.py` calls the model; stale under `SOLVER=prior` (X11).
- `docs/how-to/try-prior-solver.md` "Go back to the baseline" tells the reader to set `SOLVER=letter` in `config.env`; X11 keeps `prior` as the default.
- Nav entry for `how-to/install-decider-0.8b.md` in `mkdocs.yml`.

## S6 adversarial (2 rounds; lenses analyst, popular-science, slop-hunter)

Reviewers spawned by hand: the devils-advocate toolchain gate failed (`pip install --user` refused by PEP 668), so the scripted loop and `review-tools` did not run, and no adjudicator was used.

- Round 1: 32 findings (2 MAJOR: board free disk for `03_download_models.sh`; the measurement had no comparable reference). Fixed in the guide.
- Round 2 (confirming): 17 findings (1 MAJOR shared by the three lenses: the uncommitted `config.env` in the working tree swaps the default model to Qwen2.5-Math-1.5B, which made the guide's Qwen3.5-0.8B lines false). The guide now names no default model; the MINOR findings were fixed. Round cap reached.

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| A1 | config.env | 12-22 | 8 contradictions | Uncommitted `LLM_*` hunk swaps the default model (`LLM_REPO=` empty, `LLM_FILE=Qwen2.5-Math-1.5B-Instruct-Q4_K_M.gguf`); not part of this review | `git diff config.env`; docs/BOARD_SETUP.md still documents Qwen3.5-0.8B | open (main session / user) | major | - |
| A2 | docs/how-to/install-decider-0.8b.md | 31 | 6 steps | `cmake --build build -j` sets no job limit | same command in docs/how-to/use-decider-2b-router.md:17 | wontfix (taste) | minor | - |
| A3 | docs/how-to/install-decider-0.8b.md | 49-51 | 10 duplication | Step-2 list restates the three commands | S2 C16 asked for the list | wontfix | minor | - |
