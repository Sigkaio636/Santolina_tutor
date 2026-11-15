# Findings: docs/UNO_Q_BOARD_REFERENCE.md

Open findings of `/docs-review`. Schema: `.claude/skills/doc-authoring/references/findings-schema.md`.

## S1 audit (2026-11-14)

Weight: heavy.

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|

Incidental: external links and datasheet figures not checked.

## S2 critique (2026-11-14)

Type: reference, heavy. 25 findings (0 breaks, 7 misleading, 18 cosmetic).

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|

## Round 2026-11-15 (diff since sign-off b9c84d2 only, X5): §14 intro, §14.6, §15 bullet

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|

### S3 decisions (2026-11-15)

- U1, U2 -> verified (X11, X13): §14.6 owns the numbers. Add a dated note: these runs used the model letter (today `SOLVER=letter`; the default is now the prior solver) in the organizers' clone, before the parser fixes of `laptop/prepare_m3kang.py`; re-running the steps today does not reproduce them. Same note on the 63% in §15 (link OCR_FAILURE_MODES for current coverage).
- U3 -> verified (X14): count rows as rows (GLOSSARY "Row").
- U11 -> verified (X13): the strategy sentence leaves the reference; CHALLENGE_CONTEXT carries it. U12 follows: the lede announces measured accuracy.
- U15 suspected -> stays open unless the repair finds the run's flags; otherwise drop "with RapidOCR on our laptop" detail ambiguity by saying CPU/GPU is not recorded.

### S4 repair (2026-11-15)

Fixed and deleted: U1-U15. U15 evidence: the 0.8 rows/s line came in afc5494 (2026-11-14 13:49 UTC), before `--gpu` existed (b5d7b5c, 14:59 UTC), so the run used the CPU.

## S6 adversarial (2026-11-15)

Lenses: methodologist, popular-science, slop-hunter. Scripted loop (`adversarial-loop.js`), 2 rounds, status SHIP. Round 1: 3 findings (0 critical, 1 major, 2 minor); round 2 (confirm): 1 minor.

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| A3 | docs/UNO_Q_BOARD_REFERENCE.md | 458-466 | methodologist | Per-row-type accuracy (rows with options vs. empty rows, per run) not given, so §14.6 names the confound but not its size | needs the board CSVs (`eval-20261114-*.csv`, column `has_options`) | deferred | cosmetic | - |

Fixed and deleted: A1 (major, 22 of the 50 rows are empty rows, lopsided by language; both conclusions now say so), A2 (§15 link set 63% beside a figure on a different row set; added "not measured yet" for all rows), A4 (provenance sentence now names `--languages eng,cat`). Refuted: §14 intro vs. step 9 on the laptop (immaterial; §15 is headed "laptop").
