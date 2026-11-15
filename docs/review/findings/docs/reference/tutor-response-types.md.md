# Findings: docs/reference/tutor-response-types.md

Review round 2026-11-15. Cross-cutting decisions: `docs/review/findings/_cross-cutting.md`.

This file also holds the findings of the two other documents split from the
same source: `docs/explanation/tutor-response-types-evidence.md` and
`docs/explanation/tutor-response-policy.md`.

## History

The three documents come from `docs/TUTOR_RESPONSE_TYPES.md` (Spanish, 822
lines, deleted on 2026-11-15). Its S1 audit (TR1-TR21), S2 critique
(CTR1-CTR17) and S3 decisions were validated by the user on 2026-11-15. S3
decided: translate to English, split into a reference (cards and a
built-vs-proposed table), an explanation (evidence) and a design record
(policy, marked proposal); fix every verified finding. S4 fixed all of them,
so they are deleted here. The old findings file was never committed.

Checks in S4: MathDial Table 2 and §4.2 (κ 0.60 / 0.49 / 0.34, merged 0.67 /
0.75 / 0.55; Focus 37%; opener "usually generic"), Bridge §4.2.2 and §7.1
(+76% prefer, +80% useful on gpt-4), parsed text in the vault. `_SOLUTION`
regex run on 2026-11-15: "dímelo", "la solución", "resuélvelo" give `False`.
Tutor speed: `docs/models/qwen35-tutor.md:269`.

## Open

| id | file | line | category | claim | evidence | status | severity |
|---|---|---|---|---|---|---|---|
| TRS1 | docs/reference/tutor-response-types.md | What is built | 11 claims | the decider-2b step of `router.route` and `math-router.service` | uncommitted in the working tree (X26); `git log student_app/router.py` ends at 6c28125 without it | verified | misleading if the work is dropped |

## Reported to the main session (not edited here)

- Signed docs that still link the deleted path: `docs/TOOL_CALLER_PROMPT.md:22`,
  `student_app/README.md:57`. Also `HANDOFF.md:40` (not in the ledger).
- Edited links in docs with an open review: `docs/how-to/use-decider-2b-router.md:3,191`
  (S3 done: its stored hash changes); four router reports (all stages pending).
- `docs/models/qwen35-tutor.md:86` (session docs-review-s4-s7-qwen35, CQT24).
- `docs/vault/papers/tutoring_pedagogy/_synthesis.md:71`: same κ error (TR2), user approved a reopen.
- X8: `student_app/router.py:3` cites TOOL_CALLER_PROMPT for the labels; `_SOLUTION` regex misses
  "dímelo", "solución", "resuélvelo" (`\b` after a non-ASCII letter); `tutor.py:3` "copilot".
- Nav (X27): the three new pages replace "TUTOR_RESPONSE_TYPES (in Spanish)" under Explanation;
  the reference page goes under Reference.
