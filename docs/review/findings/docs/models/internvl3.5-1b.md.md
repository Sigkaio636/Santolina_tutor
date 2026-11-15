# Findings: docs/models/internvl3.5-1b.md

Review round 2026-11-15. Cross-cutting decisions: `docs/review/findings/_cross-cutting.md`.

## Open after S4 (2026-11-15)

S4 fixed and deleted the S1 and S2 findings. MI2: the paper's Table 3 (base InternVL3.5-1B
row) gives MathVista (mini) 59.3, so the score stays, now checked. This stays open:

| id | line | category | claim | evidence | status | severity |
|---|---|---|---|---|---|---|
| G1 | How to run it, Run log | 9 links | GLOSSARY links to `main` for "Prior solver", "Row", "Text-only row" | these entries are only in the uncommitted working-tree `GLOSSARY.md` (main session) | open | cosmetic |

Incidental (S1, for the InternVL report's own review): the report cites the old 29.1 % prior
(today's rule gives D on every figure row, 25.1 % here); the figure-logic report's
reproduce commands lack `SOLVER=letter`.

## S6 adversarial (2026-11-15; reviewers spawned by hand, lenses methodologist, ai-engineer, slop-hunter; adjudicator not run, triage by the session; 2 rounds)

Round 1: 18 findings (2 major). Round 2 (ai-engineer): SHIP, 3 findings, fixed.

| id | lens | claim | status | severity |
|---|---|---|---|---|
| B1 | ai-eng | one-tile SHA depends on the copy's folder name (written into the GGUF header) | fixed (`models/ivl-1tile`) | breaks |
| B2 | slop, ai-eng | conversion commands cannot run (paths, llama-quantize not built, no download step, environment) | fixed (download, `<llama.cpp>` paths, separate venv) | breaks |
| B3 | ai-eng | "same command on the original folder" overwrites the one-tile projector | fixed (explicit output name) | breaks |
| B4 | method | "256 image tokens": measured about 510; prompt range 543-691 (`prompt_n`) | fixed | misleading |
| B5 | method | "no effect" only on accuracy; answers move A to E; clean 89-row test 8 / 9, p = 1.0 | fixed | misleading |
| B6 | method | "below the floor" vs paired test against always D (26 / 40, p = 0.11) | fixed | misleading |
| B7 | method, slop, ai-eng2 | board estimate from file size; "still over 60 s" clause false | fixed (laptop-to-board ratio, 100-130 s) | misleading |
| B8 | slop, ai-eng | no warning against commits during a run; config.env is tracked | fixed | misleading |
| B9 | ai-eng | step-2 inputs (rows file, parquet) not named; `val_txto_no.jsonl` has no writer | fixed (pointers) | misleading |
| B10 | ai-eng | `--version` may test another binary | fixed | cosmetic |
| B11 | slop | projector / vision tower names; two names for the OCR split; duplicate 1,400 tokens; "load about 4" | fixed | cosmetic |
| B12 | ai-eng | `min_dynamic_patch` and `--languages` are no-ops | kept (S3 decision; parity with the decider record) | cosmetic |
| B13 | method | 1.68 GB RSS: no log records it | open (no source) | cosmetic |

## S3 decisions (2026-11-15, user)

- X31: the common template and the strict "no ids" rule (see decider-2b-vision decisions). CMI1, CMI3 -> point "How to run it" to this model's own report (Reproduce, …-txto-no.md:187-214), with both patch settings. MI1 (X3). MI2 -> check the paper's figure or drop "MathVista 59.3".
