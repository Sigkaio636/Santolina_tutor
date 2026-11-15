# Findings: docs/experiments/2026-11-ocr-text-vs-annotation.md

S1 audit, S2 critique and S3 decisions produced 35 findings. S4 fixed all of them. S5
(asd-ste100, ste-lint.py) ended with 0 violations.

S6 adversarial review (hand-spawned `devils-advocate:adversarial-reviewer`, one per
lens, because the user declined the plugin toolchain install, so the scripted loop did
not run): round 1 with methodologist (SHIP, 5 minor), popular-science (DO-NOT-SHIP, 3
major) and slop-hunter (MINOR); one `devils-advocate:adjudicator` ruling; round 2, a
confirming round with popular-science (SHIP, 4 minor) and methodologist (SHIP, 2
minor). The adjudicator's plan and the round 2 wording fixes were applied. The page
then ended with an STE linter run of 0 violations. Slop-hunter did not run in round 2:
the page got shorter, not longer. The edits after round 2 are wording only and had no
third round (at most 2 rounds).

Two adjudicator proposals were not applied because they overrode user decisions: the
mention of PP-OCRv4 as a fallback stays (S3 C1), and the row-selection rule of the two
manual checks stays (S3 F4), now with the note that the choice of rows is not saved.

Open or deferred (no change to the page):

id | file | line | category | claim | evidence | status | severity | depends_on
---|---|---|---|---|---|---|---|---
D-1 | docs/experiments/2026-11-ocr-text-vs-annotation.md | 160-190 | 11 claims | Cause of the short OCR texts is unknown (missing lines, text-detector loss, reading order, the cut at A, or a reference that differs from the image text) | methodologist: in the 127 rows where neither engine reaches 70 %, both have median length ratio about 0.50; nobody opened enough images | deferred | misleading | -
D-2 | docs/experiments/2026-11-ocr-text-vs-annotation.md | 78-83 | 11 claims | The gap is between two setups (package and detector), so it is not isolated to the model version | table of engines; laptop/ocr_boxes.py:40-56 | deferred | misleading | -
D-3 | docs/experiments/2026-11-ocr-text-vs-annotation.md | 187-215 | 11 claims | The question scores may not carry over to the options | adjudicator: a hand-transcribed option reference (Next steps) is the test | deferred | misleading | -
D-4 | docs/experiments/2026-11-ocr-text-vs-annotation.md | 56-60 | 8 contradictions | Whether the hidden test needs OCR for the question is unknown | docs/GOAL_MUSTS.md:121-123 | deferred | cosmetic | -
D-5 | docs/experiments/2026-11-ocr-text-vs-annotation.md | 99-107 | 11 claims | Whether lost spaces matter for the copilot is not measured | page says so in the Summary | deferred | cosmetic | -
D-6 | docs/experiments/2026-11-ocr-text-vs-annotation.md | 181-190 | 11 claims | The two manual checks (4 box lists, 2 images, by an agent) are not reproducible from the repo; the row choice is not saved | methodologist round 1; page calls them anecdotes | deferred | cosmetic | -
D-7 | docs/experiments/2026-11-ocr-text-vs-annotation.md | - | readability/visual | No figure: a dot-and-bracket chart, a per-row CER histogram and an error-example panel were suggested | adjudicator: each adds a file to keep; an example panel risks problem text in a committed file (CLAUDE.md red line 1) | deferred | cosmetic | -
D-8 | docs/experiments/2026-11-ocr-text-vs-annotation.md | - | readability/context | The 1,319 rows where both engines reach 70 % (PP-OCRv4 5.6 %, PP-OCRv5 1.1 %) are not on the page | methodologist; the choice does not need it | deferred | cosmetic | -
