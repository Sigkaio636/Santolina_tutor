# Findings: docs/CHALLENGE_CONTEXT.md

Open findings of `/docs-review`. Schema: `.claude/skills/doc-authoring/references/findings-schema.md`.

## S1 audit (2026-11-14)

Weight: heavy.

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|

Incidental: external links (229-248) not checked.

## S2 critique (2026-11-14)

Type: explanation, heavy. 24 findings (0 breaks, 2 misleading, 22 cosmetic).

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|

## Round 2026-11-15 (diff since sign-off b9c84d2 only, X5): section "First results on the board", lines 242-248

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|

### S3 decisions (2026-11-15)

- H2, H3 -> verified (X13): replace the section with one or two lines: the conclusion (a 0.8B model is weak at picking the letter, which supports the **Teach** direction of §1), with the small-sample caveat, and a link to UNO_Q_BOARD_REFERENCE §14.6. H4-H7, H10, H11, H13 disappear with it.
- H1 -> verified (X11, X13): the dated note lives in §14.6, not here.
- H8 -> verified: say "Teach", not "tutor goal". H9: real links. H12: move line 248 back above the section.

### S4 repair (2026-11-15)

H1-H13 fixed or settled: the section is now "### Letter accuracy on the board", one paragraph with the conclusion, the small-sample caveat (50 rows), the **Teach** direction and a link to UNO_Q_BOARD_REFERENCE §14.6 (anchor checked in a scratch `mkdocs build`). The harness line is back above it. 0 open.

## S6 adversarial (2026-11-15)

Lenses: methodologist, popular-science, slop-hunter (hand-spawned reviewers with `review-tools prompt`; the scripted loop and the adjudicator did not run, because all material findings had one root cause). Round 1: 1 MAJOR + 7 MINOR. Round 2 (confirming): SHIP from both lenses, 2 MINOR.

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| A4 | docs/CHALLENGE_CONTEXT.md | 248 | 11 claims | "Today the default is" has no date; it goes stale when the default changes | the date is only in the §14.6 dated note | deferred (taste) | cosmetic | - |
| A5 | docs/CHALLENGE_CONTEXT.md | 245-246 | 11 claims | Strength of "weak" and why a weak letter supports Teach are not in the paragraph | X13 keeps the figures in §14.6 | deferred (X13) | cosmetic | - |
| A6 | docs/CHALLENGE_CONTEXT.md | 246 | 11 claims | Option text came from the parser before its fixes, a possible confound | UNO_Q_BOARD_REFERENCE.md §14.6 dated note records it | deferred (recorded in §14.6) | cosmetic | - |

Fixed in round 1-2 and deleted: A1 (MAJOR, paragraph did not say today's default is the prior solver), A2 ("first test" ignored the 0/5 smoke run in §14.4), A3 ("this run" when §14.6 has two runs).
