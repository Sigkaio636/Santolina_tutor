# Experiments

This section records each experiment we ran, what it measured, and what we decided. The topics follow the two jobs that the challenge asks for ([checklist 1.1](../GOAL_MUSTS.md#11-the-challenge)):

- **Reason:** `predict.py` answers a hidden-test problem with one letter.
- **Teach:** the student app guides a student through a problem.

Each topic page summarizes its reports and gives the current decision. The reports keep the full design, the tables and the limits.

## Topics

| Topic | Question | Headline result | Decision | Code in the repo |
| --- | --- | --- | --- | --- |
| **Reason** › [Solving the problem](solving/index.md) | Which solver gives the most right letters in 60 seconds on the board? | A Qwen2.5-Math program with Catalan translated first: 55 of 100 on the practice set (laptop, at board speeds). Any single forced letter from a small model: 15 to 24 of 100. | `main` ships `SOLVER=prior` (16 of 100). The program solver is on a branch. | `predict.py`, `copilot/` |
| **Reason** › [Figure problems](figure-problems/index.md) | Does a small vision model help on problems that need the figure? | No vision run beats always answering D (about 25 %). | Text only. The figure rows answer D. | `copilot/prior.py` |
| **Reason** › [Reading the options](option-reading/index.md) | How do we read the five options A to E from the problem image? | Five options read in 98.5 % of text-only rows (PP-OCRv5, then PP-OCRv4). A new reader gets 60 of 60 gold rows right, against 56. | PP-OCRv5 with the v4 fallback. The new reader is the candidate. | `laptop/` |
| **Teach** › [Intent router](intent-router/index.md) | Which small model labels a student message best? | decider-2b: 87.6 % on 250 messages, against 80.8 % for decider-0.8b (p = 0.009). | decider-2b is the router to try. The student app uses a keyword rule today. | `student_app/router.py` |

The tutor model itself is a fine-tune, not an experiment with a decision rule. Its record is in [Reference › Models](../models/qwen35-tutor.md).

## How we run and record an experiment

- **The decision rule comes first.** Most reports write the rule before the run ("pre-registered"). When a rule came after a first look at the data, the report says so.
- **Each report states its setup:** the date, the branch, laptop or board, the model files and the rows used. Laptop runs give no board latency, unless a report says that it charges the board's measured speeds.
- **Compare with the right floor.** The organizers' baseline is 22.5 % (9 of 40 English M3Kang problems whose options OCR read, [board setup 11.3](../BOARD_SETUP.md#113-what-we-measured)). A run must also beat the best fixed letter on the same rows. On the practice set, each letter is right on 20 of 100 rows.
- **Small sets are noisy.** On 50 problems, one answer is 2 points. The reports give a 95 % interval and use a paired exact McNemar test between two runs on the same rows.
- **No problem text.** M3Kang is for research use only. The reports give problem IDs and scores, never a statement, an option or an image.

## What didn't work

- **One forced letter from a small model.** Qwen3.5 0.8B, decider-0.8b and Noema-2B all scored 15 to 24 of 100 on the practice set, close to the 20 of a fixed letter. Each one mostly answers one letter ([solving](solving/index.md)).
- **The prior rule on the practice set.** It beat a fixed letter on M3Kang. The practice set lists its options in increasing order, so the rule picks C on 90 of 100 rows and scores 16 ([practice set](../PRACTICE_SET.md#what-we-conclude)).
- **Vision models for figure problems.** Qwen3.5 0.8B with the image, decider-2b-vision and InternVL3.5-1B all score at or below always D ([figure problems](figure-problems/index.md)).
- **A LaTeX OCR and Tesseract for the options.** PP-FormulaNet is slow and shows no gain. Tesseract reads the question text better but the options worse ([reading the options](option-reading/index.md)).
- **decider-0.8b as the router.** Recall on one label stayed under 60 %. decider-2b replaced it ([intent router](intent-router/index.md)).

The [README](https://github.com/Sigkaio636/Santolina_tutor#what-didnt-work-and-what-we-would-try-next) also lists what we would try next.
