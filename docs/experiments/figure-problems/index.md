# Figure problems

**Question:** on problems that need their figure (`text_only = false`), does a small vision model that sees the image pick the right letter more often than a text-only answer?

**Why it matters:** in our M3Kang validation set, 440 of 789 rows need a figure. Four of the 20 hidden-test problems have one. The copilot is text only, so it guesses on these rows.

**Where it lives:** `copilot/prior.py`. Since commit `f72d3e8` the prior solver answers D on every figure row. The vision runs used `laptop/compare_runs.py` and a llama.cpp server with each model's mmproj file.

## Reports

All runs are on the laptop, on M3Kang figure rows in English, Catalan and Spanish. "Floor" is the score of always answering the most common letter on the same rows.

| Date | Report | Model | Rows | With the image | Floor | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-11-14 | [Qwen3.5 0.8B with the image](../2026-11-vision-txto-no.md) | Qwen3.5 0.8B, image ≤ 128 tokens | 440 | 17.3 % | 25.2 % (D) | Not adopted. Below the text baseline (22.5 %), p = 0.052. |
| 2026-11-15 | [decider-2b-vision on figure logic](../2026-11-decider-2b-vision-figure-logic.md) | decider-2b-vision | 160, levels 0 to 2 | 24.4 % (26.2 % with no token limit) | 30.0 % (D) | Not adopted. The image changes nothing, p = 1.0. |
| 2026-11-15 | [InternVL3.5-1B vs decider-2b](../2026-11-internvl35-1b-vs-decider-2b-vision-txto-no.md) | InternVL3.5-1B and decider-2b-vision | 175 | 17.1 % and 22.3 % | 25.1 % (D) | Not adopted. The prior rule gets 29.1 % on the same rows. |
| 2026-11-15 | [Heuristics, no model](../2026-11-txto-no-heuristics.md) | Eight rules on the option values | 2,585 (train and val) | — | 24.9 % (D) | No rule passes. Answer D on every figure row. |

The model records hold every run of each vision model: [decider-2b-vision](../../models/decider-2b-vision.md) and [InternVL3.5-1B](../../models/internvl3.5-1b.md).

## Current decision

**The copilot stays text only. Every figure row answers D.** Expected accuracy: about 25 %.

- No vision run reaches the fixed-letter floor. Every model mostly follows a letter preference, not the figure. With the image, Qwen3.5 0.8B never answers B, and InternVL answers A or E on 151 of 175 rows.
- decider-2b-vision does not fit the board: 2.86 GB of RAM. Its time per problem on the board is very likely over 60 s.
- The figure logic subset was the most favourable case we could build: low levels, logic and spatial problems, and a model trained on similar image tasks.

## What would reopen it

- A vision model of about 1B parameters, with a llama.cpp mmproj, that reports a score well above chance on a diagram-maths benchmark (MathVerse, MathVision).
- A run on all 440 figure rows that shows an image gain with p < 0.05.
- The heuristic "median value when the numeric options are not in order" scores 33 % against 22 % for D (p = 0.14). Test it again when more labelled figure problems are available.
