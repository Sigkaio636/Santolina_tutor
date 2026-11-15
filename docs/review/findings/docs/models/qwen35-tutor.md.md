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

Resolved in S4 by evidence, not by the S3 "as reported" note: QT10 and QT11.
`build_tutor_sft.py` at 64e56f5 applies `--sample` to each example after the
split (`rng.random() < sample`), not to problems. So "290 problems" was the
count of `prepare` examples, and the per-task counts need not follow the
`--lean` per-problem rules. The page now says so; the counts stay.

Other S4 evidence: the local copy `qwen35-tutor-Q8_0.gguf` (repo root,
ignored) has the page's size and SHA256 (QT15). `generate_explanations.py`
defaults to `text_only=True`, so the rerun command needs `--no-text-only` to
sample all 1,747 English problems (QT6). The `math-tutor.service` link to
`main` is kept: the file exists on `origin/main` (QT2). CQT24: the link now
points to `docs/reference/tutor-response-types.md` (the split of the deleted
`TUTOR_RESPONSE_TYPES.md`; untracked until its own review commits it).

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
- Update (X32b, user chose option 2): keep the user's replacement paragraph, and add that the short board prompt is on purpose (the tutor model never sees the answer; the leak check guards), that the quality effect is not measured, and the same point under "Known limits". Drop any wording that suggests the mismatch is a bug to fix.

## S6 adversarial, round 1 (2026-11-15; lenses methodologist, ai-engineer, slop-hunter)

The devils-advocate toolchain gate failed (PEP 668: `pip install --user` refused), so the
scripted loop did not run. Reviewers were spawned by hand, one per lens; no adjudicator
(triage by this session against the code). Verdicts: methodologist DO-NOT-SHIP (12),
ai-engineer SHIP (9), slop-hunter DO-NOT-SHIP (11). All fixed in round 1 unless listed here.

| id | line | category | claim | evidence | status | severity |
|---|---|---|---|---|---|---|
| ADV1 | Verdict, prompt | 11 claims | "the tutor model never sees the answer" (X32b wording) | after Show the solution the text with the right option enters the chat history the model gets (`student_app/tutor.py:155-168,188-203`, `state.py:386`) | fixed: "until the student asks for the solution"; tell the user | misleading |
| ADV2 | Files | 11 claims | "the converter kept the multi-token prediction head" | header nextn=1 but no blk.24/nextn tensors in the 320 | fixed | misleading |
| ADV3 | Run log | 11 claims | weighted val loss is mean(w x loss), not a cross-entropy; not comparable across sets | `train_tutor.py:135,167`; sum n*w*l/320 = 0.9692, unweighted 1.30 | fixed (note) | misleading |
| ADV4 | Trust rule | 11 claims | "on their own": every call gets the key | `generate_explanations.py:145` | fixed | misleading |
| ADV5 | Held-out | 11 claims | data/val.jsonl English problems and cat/esp versions are training problems | 1,466 + 281 = 1,747 English rows | fixed | misleading |
| ADV6 | Verdict | 11 claims | hand check used the merged HF model + training prompt, five examples | notebook cell 7 | fixed | misleading |
| ADV7 | How to add a run | 6 steps | `--tiebreak` takes one model; original vote not rebuildable; step 3 check proved only sampling; step 5 check only approximate; attach only that dataset; commit pin | `generate_explanations.py:266,306,497`; notebook cell 3 | fixed | misleading |
| ADV8 | several | 10 duplication | prompt mismatch x5, 70-min stop x4, readbacks of tables, filler | - | fixed | cosmetic |
| ADV9 | Training | 11 claims | code commits postdate the run; libraries unpinned; precision default; filter list incomplete; context 2048 < 3,072 training max | git log; `generate_dialogues.py:120,205-226`; `tutor_backend.py:24` | fixed | cosmetic |
| ADV10 | Tasks | 11 claims | near-duplicate problems may cross the split (15 groups) | `val_ids.txt` not local | open (deferred) | cosmetic |

## S6 adversarial, round 2 (confirming; one reviewer with the three lenses)

Verdict SHIP (5 MEDIUM, 0 MAJOR). Closure items 1-4, 6, 8 closed. Round-2 fixes applied (last round,
cap 2): `check_right` gives the justification (does not ask why); the 155 held-out ids are the only
ones "guaranteed" unseen; `tutor_backend.py` only documents a 4096 command; step 3 check is "a log
line"; unweighted mean computed with the held-out counts; five examples = one for each of five tasks.

| id | line | category | claim | evidence | status | severity |
|---|---|---|---|---|---|---|
| ADV11 | Training, Precision | 11 claims | "fp16 autocast (the T4 has no bf16)": `train_tutor.py:184-186` picks bf16 when `torch.cuda.is_bf16_supported()` is true, which recent PyTorch can report on a T4 | kept "as reported" with the selection rule; teammate checks the Papermill log | decision (teammate) | misleading |

CQT22 closed in S5 (ste-lint reports no sentence over the length limit). S7 signed off by the user on 2026-11-15.
