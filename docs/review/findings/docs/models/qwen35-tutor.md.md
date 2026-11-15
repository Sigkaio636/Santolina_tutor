# Findings: docs/models/qwen35-tutor.md

Review round 2026-11-15 (teammate's record, untracked; X30).

## Open findings after S4 (2026-11-15)

S1 (19 findings) and S2 (25 findings) were validated by the user on
2026-11-15. S4 fixed and deleted every other finding. What stays open:

| id | line | category | claim | evidence | status | severity |
|---|---|---|---|---|---|---|
| QT7 | Hints and solutions | 8 contradictions | 3 hints x 1,553 = 4,659, not 4,670 hint examples | kept "as reported" with a note on the page | decision (teammate) | cosmetic |
| QT8 | Tutor dialogues | 8 contradictions | `free` 4,111+245+313 = 4,669 (not 4,672); `manipulation` 1,547 (not 1,549) | kept "as reported" with a note | decision (teammate) | cosmetic |
| QT9 | Tutor dialogues | 8 contradictions | set built 04:55 and report 06:05 with no time zone; training started 04:04 UTC | kept with a note; CET (UTC+1) would resolve it | decision (teammate) | misleading |
| QT12 | Results of the short run | 8 contradictions | 18 s per step vs 24.1 s (4,293 s / 178; 16 / 0.663); 4,293 s > 70 min | kept "as reported" with a note | decision (teammate) | misleading |
| CQT24 | Tutor dialogues | 9 links | link to `../TUTOR_RESPONSE_TYPES.md` (Spanish, T-names) | `docs/reference/tutor-response-types.md` does not exist yet; relink when it does | open (main session) | cosmetic |
| CQT22 | several | 4 sentences | sentences over 25 words | S5 scope | open (S5) | cosmetic |

Resolved in S4 by evidence, not by the S3 "as reported" note: QT10 and QT11.
`build_tutor_sft.py` at 64e56f5 applies `--sample` to each example after the
split (`rng.random() < sample`), not to problems. So "290 problems" was the
count of `prepare` examples, and the per-task counts need not follow the
`--lean` per-problem rules. The page now says so; the counts stay.

Other S4 evidence: the local copy `qwen35-tutor-Q8_0.gguf` (repo root,
ignored) has the page's size and SHA256 (QT15). `generate_explanations.py`
defaults to `text_only=True`, so the rerun command needs `--no-text-only` to
sample all 1,747 English problems (QT6). The `math-tutor.service` link to
`main` is kept: the file exists on `origin/main` (QT2).

## S3 decisions (2026-11-15, user)

- QT3, QT4 -> replace the sentence at 124-129 with the user's text (adapt "The accuracy and leak figures above" to what the page reports — validation losses — and confirm the wording with the user in S4):

  > The system prompt holds the problem, the teacher's answer and the tutor's rules. [`copilot/tutor_prompt.py`](…/64e56f5…/copilot/tutor_prompt.py) builds it, and [`copilot/tutor_backend.py`](…/64e56f5…/copilot/tutor_backend.py) uses it at inference. Both exist only on the `feat/tutor-finetune` branch, which is not merged.
  >
  > The student app on the board does not use this prompt yet. `student_app/tutor.py` sends a shorter one: "You are a Socratic math tutor.", the reply language and the problem, without the answer or the rules. So the model sees a different prompt on the board than in training. The accuracy and leak figures above were measured with the training prompt, not with the board's prompt.

  Line 15 ("The teacher gives it the problem and the correct answer") follows: say that is the training prompt.
- QT6 -> "all 1,747 English problems (811 text-only, the rest with a figure)". QT13 -> the lowest loss is `check_right`. QT14 -> the pack's solution only when the pack has one; otherwise the right option and an explain-back question.
- QT7, QT8, QT9, QT10, QT11, QT12 -> keep the numbers "as reported by the run log" and add a short note per table where a sum does not add up (or the timezone is unknown). List them for the teammate in the final message.
- QT16, QT17, QT18, CQT1, CQT2, CQT6, CQT19 -> "training examples" (not rows), "held-out problems (not `data/val.jsonl`)", "data models" vs "the classroom teacher", one name for the answer key.
- X31 -> the common model-record template (Identity, Files, How to run it, Resources, Verdict, Run log, How to add a run with numbered, checked steps for "Train it again"), and the strict "no problem text, ids or images on this page" rule (CQT10).
- CQT11 (X28) -> use-student-app owns the board behaviour numbers; this page links them. CQT24 -> TUTOR_RESPONSE_TYPES is being translated and split: link `docs/reference/tutor-response-types.md` once it exists, else the current file. QT1 -> state that the code lives on the unmerged branch.

S3 validated by the user on 2026-11-15 (side session). In S4 the user chose:
the last sentence of the prompt paragraph says "The validation losses on this
page" (the page has no accuracy or leak figures), and "the answer key"
replaces "the teacher's answer".
