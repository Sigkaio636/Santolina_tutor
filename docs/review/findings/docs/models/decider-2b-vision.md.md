# Findings: docs/models/decider-2b-vision.md

Review round 2026-11-15. Cross-cutting decisions: `docs/review/findings/_cross-cutting.md`.

## Open after S4 (2026-11-15)

S4 fixed and deleted the other S1 and S2 findings. These stay open: the fix is in the
document, but it rests on work that is not committed yet (X26).

| id | line | category | claim | evidence | status | severity |
|---|---|---|---|---|---|---|
| MD4, CMD5 | Resources | 8 contradictions | "the student app adds the tutor model and intent router services" | `board/systemd/math-router.service`, `board/09_install_router.sh` untracked; ROUTER_* in `config.env` uncommitted (X26) | open | cosmetic |
| CMD3 | Identity | 5 jargon | intent router = text-only decider-2b v12; GLOSSARY link | ROUTER_FILE in uncommitted `config.env`; GLOSSARY entries "Intent router", "Prior solver", "Row", "Text-only row" only in the working tree, link points to `main` | open | cosmetic |

## S6 adversarial (2026-11-15; reviewers spawned by hand, lenses methodologist, ai-engineer, slop-hunter; adjudicator not run, triage by the session; 2 rounds)

Round 1: 25 findings (2 major). Round 2 (methodologist): SHIP, 3 minor, fixed.

| id | lens | claim | status | severity |
|---|---|---|---|---|
| A1 | slop | run log has no Commit column; fl- commits unclear | fixed (Commit column, "+ changes") | breaks |
| A2 | method | reopen rule tests the image only; ignores floor, prior and board | fixed (3 tests, one row per problem, a > b) | misleading |
| A3 | method, slop | "floor" used four ways; "better than guessing" | fixed (one definition) | misleading |
| A4 | method | "does not change its score" from a non-significant test; floor inside every interval | fixed | misleading |
| A5 | method | image vs blind also differs in `figure X` / `option X` wording | fixed (stated) | misleading |
| A6 | ai-eng, method | 8.2 s vs 3.2 s: rows, commits and other CPU jobs differ | fixed (stated; board estimate as a 2-6x range) | misleading |
| A7 | ai-eng | bare `llama-server`; no check of the commit | fixed (build pointer, `--version`) | misleading |
| A8 | ai-eng, method | no check shows `LLM_PROMPT=decider` | fixed (limit stated; Input column note) | misleading |
| A9 | ai-eng, method | compare_runs order reverses a / b | fixed (img first) | cosmetic |
| A10 | ai-eng | "no image token limit" is the model's default size | fixed | cosmetic |
| A11 | ai-eng | filler is per missing option | fixed | cosmetic |
| A12 | ai-eng, method2 | log records HEAD at the end of the run (imgfull logged `9107889`) | fixed (row note, step 1) | cosmetic |
| A13 | slop | run names differ from the reports | fixed (short names listed) | cosmetic |
| A14 | slop | lede repeats the verdict; sample description; Qwen paragraph; `--ids` clause; `== all` literal; python3 vs .venv | fixed | cosmetic |
| A15 | method | board estimate on 2 problems | fixed (n = 2 stated) | cosmetic |
| A16 | ai-eng | `eval_vision.py` could log `LLM_PROMPT`/`SOLVER` and read the commit before the loop | open (code change, out of scope) | cosmetic |
| A17 | method | "peak 2.84 GB" with no source run | open (no source found) | cosmetic |

## S3 decisions (2026-11-15, user)

- CMD11, MD8, CMI8, CMI10, MI3, CQT13, CQT14, QT19 (X31) -> one template for the three model records: Identity, Files, How to run it, Resources, Verdict, Run log, How to add a run (numbered steps with checks). The per-record method paragraph may stay (X20).
- CMD12, CMI9, CQT10 (X31) -> keep the stricter local rule "no problem text, ids or images on this page" in all three.
- MD1, CMD1, MD2 -> step 1 sets `SOLVER=letter` and `LLM_PROMPT=decider` (X11). MD7, CMD2 -> give 3.2 s (the run log, InternVL report :108) unless the repair finds the 8.2 s source; say which run. MD6 (X3), MD4, MD3, MD5 and the rest of the verified findings are fixed.
