# Findings: docs/PRACTICE_SET.md

Review round 2026-11-15. Cross-cutting decisions: `docs/review/findings/_cross-cutting.md`.

## S1 audit and S2 critique

S1 (docsauditor) found 10 findings (F1-F10), S2 (diataxis + docs-critic) 36
(P1-P36). S4 fixed or closed all of them; none is open. The full tables are in
the Git history of this file.

## S3 decisions (2026-11-15, user)

- P1, P2, F6, F7 -> one document; no split, no move. Fix the steps so they are true today (X2 for that section): `uv run --no-project --python 3.12 --with-requirements laptop/requirements.txt python laptop/prepare_m3kang.py ...` (F2), the parquet path `data/demo-00000-of-00001.parquet` (P6, X25), the prior run as is and the letter run with `SOLVER=letter` plus the math-llm server it needs, English rows with `--languages eng` (F3, P17, P18), checks (P16), `--limit 0` explained (P19), copy to the board via BOARD_SETUP step 10 (P20).
- F4, F5, P21, P27 -> the measurement section gets a dated note: measured on the laptop on 2026-11-14, before f72d3e8 (the prior now answers D on figure rows), not re-measured, no results file kept. Line 65 stays a recommendation for the final build ("`SOLVER=prior` is today's default; we recommend not keeping it for the final build because..."), linking GLOSSARY "Prior solver".
- P7, P8 -> cite the organizers' dataset card (in `data/demo-README.md`, not in Git, so no link). Last call: 12:00 on Sunday 15 November 2026 (X24). P12: keep the organizers' wording "level 0 is grade 5" as their statement.
- F8, P30 (X24) -> say the card does not state what file `predict.py` receives or whether options arrive as text; remove "Problems arrive with their options".
- P9 -> link GLOSSARY "Contract" and keep the organizers' line as their statement.
- P25, P31, P32, P35, F9 -> soften: say what was measured and what was not; "5 s" and "a third of its words" become unmeasured estimates or go.
- F1, P4 -> drop the branch reference; link `docs/experiments/2026-11-ocr-text-vs-annotation.md` only if it holds the note, otherwise drop the sentence.
- Terms: Hidden test (P5, F10), Text-only row and Coverage (X16), rows (X14), "license".

## S4 repair (2026-11-15, docsjanitor)

- Fixed and deleted: F1-F5, F7-F10, P3-P6, P8-P11, P13-P36, and "licence".
- Closed by S3 with no edit: P1, P2, F6 (one document, no split, no move), P7
  (card cited, not linked), P12 (organizers' wording kept).
- Removed rather than reworded: the branch sentence (F1, P4: the experiment
  report does not hold the test-format note), "Problems arrive with their
  options" (F8, P30), "about a third of its words" (P31), "5 s reading, 50 s
  to compute" (F9, P32), "No Spanish in the final test" (P36).
- Checked on the laptop: step 1 (prepare_m3kang.py on the practice parquet)
  and step 2 (prior run, 50 English rows). Not run: step 3
  (`SOLVER=letter` on the board; no llama-server on the laptop).
- For the main session: `docs/GOAL_MUSTS.md` still says no source supports the
  test format; the organizers' card is now that source. `main`'s GLOSSARY has
  no "Prior solver", "Text-only row" or "Coverage" yet (uncommitted on
  `repo-cleaning`).

## S6 adversarial (2026-11-15, 2 rounds)

The plugin's toolchain gate failed (`pip install --user`: PEP 668), so the
scripted loop did not run. With the user's approval, reviewers were spawned by
hand: round 1 analyst, methodologist, slop-hunter (19 findings, 4 MAJOR) and
`devils-advocate:adjudicator`; round 2 one confirming reviewer (SHIP, 2 MINOR,
both fixed after the round, not re-confirmed).

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| A1 | docs/PRACTICE_SET.md | 60 | 6 steps | step 3 copy to `data/demo/` that does not exist on the board | BOARD_SETUP.md:809; scp makes no parent folder | fixed (ssh mkdir + scp, adb route) | misleading | - |
| A2 | docs/PRACTICE_SET.md | 60-68 | 6 steps | step 3 had no check; a dead server prints 10/50 | copilot/pipeline.py:52-58 (fallback D) | fixed (`Status:` check) | misleading | - |
| A3 | docs/PRACTICE_SET.md | 95 | 11 claims | 8 vs 10 used as evidence; wrong cause of the M3Kang gain | try-prior-solver.md:88 | fixed | misleading | - |
| A4 | docs/PRACTICE_SET.md | 12 | 11 claims | "the card lists only English and Catalan" read as hidden-test languages | card names them for the practice set only | fixed | cosmetic | - |
| A5 | docs/PRACTICE_SET.md | 98 | 8 contradictions | pool Catalan rows vs English-only steps | Catalan rows are translations | fixed | cosmetic | - |
| A6 | docs/PRACTICE_SET.md | 48 | 6 steps | step 1 check blind to OCR failure | prepare_m3kang.py:250 | fixed | cosmetic | - |
| A7 | docs/PRACTICE_SET.md | 50 | 11 claims | `data/prior.json` would change the step 2 score | copilot/prior.py:62-69; X12 | not material (adjudicator) | cosmetic | - |
| A8 | docs/PRACTICE_SET.md | 56 | 4 sentences | `--limit 0` changes nothing with `--languages eng` | eval.py:53-58 | refuted (true, protects other runs) | cosmetic | - |
| A9 | docs/PRACTICE_SET.md | 82 | 11 claims | statement length includes the number prefix | dated record, not re-measured | not material | cosmetic | - |

For the main session: `docs/how-to/try-prior-solver.md:17-18` and the comment
at `copilot/pipeline.py:18` say a failed model call falls back to the prior's
letter; `pipeline.py:58` sets `FALLBACK_ANSWER` (D).
