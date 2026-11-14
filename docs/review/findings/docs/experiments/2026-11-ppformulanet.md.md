# Findings: docs/experiments/2026-11-ppformulanet.md

S1 audit (docs-review): 0 findings. Written with doc-authoring route author
before the review (A5 audit and 2 re-audits, A6 language, A7 two adversarial
rounds), so the earlier findings are already fixed.

S2 critique (docs-critic): 36 findings C1-C36. S3 settled C22 ("reference
value" and "right"). S4 fixed C1-C35 and the appendix part of C36.

S6 adversarial (hand-spawned; plugin toolkit gate FATAL: PEP 668): round 1
with methodologist, popular-science and slop-hunter, 19 findings; the
adjudicator kept 3 changes (A summary context, B claims vs commands incl.
`pick` printing the no-kind count, C duplicate "Right"), refuted 7 and
deferred 2 (P4, P7). Round 2: SHIP from all three lenses, 4 MINOR left open.
Open findings stay below.

id | file | line | category | claim | evidence | status | severity | depends_on
---|---|---|---|---|---|---|---|---
C36 | docs/experiments/2026-11-ppformulanet.md | 114 | readability/9 links | UniMERNet, GOT-OCR2.0 and Qwen2.5-VL have no links (a one-line description was added) | S4 did not add URLs it could not check | verified | cosmetic | -
R2-1 | docs/experiments/2026-11-ppformulanet.md | 18, 75 | slop-hunter | "about 5 rows per second" stated twice | S6 round 2, taste | verified | cosmetic | -
R2-2 | docs/experiments/2026-11-ppformulanet.md | 21, 49 | slop-hunter | "none of the 20 options is one" stated twice | S6 round 2 | verified | cosmetic | -
R2-3 | docs/experiments/2026-11-ppformulanet.md | 56, 153 | slop-hunter | "Claude wrote the reference value(s)" twice (crop source vs file) | S6 round 2, borderline | verified | cosmetic | -
R2-4 | docs/experiments/2026-11-ppformulanet.md | 18 | methodologist | "about 8 minutes" is derived from the throughput, not timed | S6 round 2, wording | verified | cosmetic | -
