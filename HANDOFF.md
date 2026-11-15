# Handoff: continue on the laptop with the board

Written on 2026-11-15 on branch `full-interface`, updated when it was merged into `main`
together with the real tutor. Everything now lives on `main`: run the teacher app from a
checkout of `main` on every laptop. Read this first, then delete the file when the work
below is done. `CLAUDE.md` still applies in full, above all the M3Kang red line.

## Where the work stands

| Part | State | File |
| --- | --- | --- |
| Student app: login, homework, practice, free mode, chat, events | Works | `student_app/` |
| Free mode: which problem comes next | Works, tested only on a synthetic map | `student_app/planner.py` |
| Clues, solutions, chat replies | Works with the fine-tuned tutor model: 14 to 17 s per clue on board B1 | `student_app/tutor.py`, `llm.py`, `router.py` |
| Retrieval index | Built on board B1 (`~/datathon-UPC-maths-qualcomm-arduino-unoq/data/index.db`, 2015 to 2024 problems) | `copilot/rag.py`, `build_index.py` |
| Teacher app: boards, packs, unload, learning widgets | Works | `teacher_app/` |
| Kangaroo library: choose indexed problems by topic and level | Works on board B1 | `teacher_app/kangaroo.py` |

## What is left, in order

1. **Plug in the decision model** in `student_app/router.py`: replace `classify`, keep the
   five labels of `docs/TOOL_CALLER_PROMPT.md`.
2. **Check the planner on real problems.** The planner reads the index by itself, through
   `rag_index_path` in the board's `identity.json`. Run a simulated student (see
   `tests/test_planner.py`, function `walk`) over a real pack and look at two things:
   does the path stay on topic, and does it settle at the student's level? Also time one
   step on the board: one step is a pure-Python dot product against one level of the pack.
3. **Every other board** needs the tutor model (copy `qwen35-tutor-Q8_0.gguf` to
   `~/models/`, run `board/08_install_tutor.sh`) and the topic labels
   (`~/santolina/topics.jsonl`, see `docs/how-to/run-teacher-app.md`). B1 has both.
4. **Make a pack's problems findable when they are not in the index** (for example 2026
   problems): embed the pack's exercises when it is loaded, so clue 2 and free mode find
   neighbours for any pack.

## How the planner decides

The rule and its `path_reason` values are in the docstring of `student_app/planner.py`
and in `docs/how-to/use-student-app.md`. Things the code does not say out loud:

- M3Kang has no topic field. "Same topic" is the nearest vector in the index, and
  "other topic" is the problem farthest from the last five.
- A pack exercise finds its vector through `meta.m3kang_id`. The index holds only
  `train.jsonl` problems, so a pack made from other problems gets no neighbours. It then
  falls back to `meta.topic`, then to chance at the right level.
- Both languages of a problem use the English vector, because bge-small is an English
  model. If Catalan neighbours look wrong, this is the first place to look.
- The student profile is the existing `progress/<code>.json`. There is no separate
  SQLite profile. The start level is the highest level solved at the first try.
- A topic counts as mastered after 3 clean solves in a row (`MASTERY_STREAK`). A student
  who alternates right and wrong stays on one topic until its problems run out. A cap on
  the length of a topic run is a possible addition; it is not there today.

## Design decisions from Pau that the code does not explain

- During class a board runs alone: it has power, its own Wi-Fi hotspot, and the student
  uses it from a phone. The teacher's laptop connects only over USB (adb).
- One board per student. The code is asked on every visit, on purpose.
- The teacher store is centred on students, not boards. Boards hold codes, never names.
- The RAG index may retrieve the exact exercise and its answer **on purpose**. A separate
  leak-check layer handles leaks. Do not add exclude rules to the retrieval.
- The guiding rule for the student side: as little friction as possible. Log as many
  metrics as possible.
- Ask Pau before any big download (models, datasets). Look for a local copy first.

## Things that will surprise you

- **`tests/test_pipeline.py` has 14 failures** with the committed `config.env`
  (`SOLVER=prior`). They pass with `SOLVER=letter uv run pytest tests/test_pipeline.py`.
  The tests expect the letter solver's fallback. Nobody has decided yet which side to fix.
- **The data is not in Git** and must never be. On a new laptop, `data/train.jsonl` and
  `data/val.jsonl` come from `laptop/prepare_m3kang.py` (ask before the download) or from
  a copy of another laptop's `data/` folder.
- The other tests: `uv run pytest -q tests`. Try the whole classroom without a board:
  `uv run --group teacher python -m teacher_app demo`.
