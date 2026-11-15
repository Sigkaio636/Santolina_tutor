# Findings: docs/TOOL_CALLER_PROMPT.md

Review round 2026-11-15. Cross-cutting decisions: `docs/review/findings/_cross-cutting.md`.
Audited against the working tree, where `student_app/router.py` and `student_app/tutor.py` had uncommitted changes and `board/systemd/math-router.service` was untracked (someone else's work in progress).

## S1 audit (docsauditor, 20 findings: 16 verified, 4 decision)

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| F2 | docs/TOOL_CALLER_PROMPT.md | 13-15 | 8 contradictions | Model: Qwen3.5-0.8B via /v1/chat/completions; "do not use decider-0.8b" | router.py:15-16,32,117-130 call decider-2b at 127.0.0.1:8085 `/completion`; board/systemd/math-router.service | wontfix | misleading | F1 |
| F3 | docs/TOOL_CALLER_PROMPT.md | 14-15, 121 | 8 contradictions | decider ignores instructions; chat format follows them | measured: Qwen intern 39%/36.7%, decider-0.8b plain 84%/78.7%, decider-2b 87.6% (conclusion:54-67; bakeoff-3:116) | wontfix | misleading | F1 |
| F4 | docs/TOOL_CALLER_PROMPT.md | 16, 61-68 | 2 snippets | grammar, max_tokens 6 | router.py:121-136: n_predict 1, n_probs 50, letter readout after "Answer: (" | wontfix | misleading | F1 |
| F5 | docs/TOOL_CALLER_PROMPT.md | 34-57 | 2 snippets | chat system prompt with tags | router.py:99-114 one plain-text prompt; same descriptions as laptop/router_bakeoff.py:33-40 | wontfix | misleading | F1 |
| F6 | docs/TOOL_CALLER_PROMPT.md | 72-103 | 2 snippets | OPTION_LINE, SOLUTION_RULE, clean, problem_stem, route(label, msg) | none exist; router.py has LABELS tuple, asks_for_solution, by_rule, prompt, ask_model, route(problem, last_tutor_move, message) | wontfix | breaks | F1 |
| F7 | docs/TOOL_CALLER_PROMPT.md | 19-20, 105-113, 123, 133-135 | 2 snippets | cleaning, tags, cuts 400/300 | router.py:68,100-107,141: tutor move cut to 150, problem not cut, message raw in quotes | wontfix | misleading | F1 |
| F8 | docs/TOOL_CALLER_PROMPT.md | 46-47 | 8 contradictions | ATTEMPT wins ties | keyword rule first gives SOLUTION (router.py:90-96,144-145) | wontfix | misleading | F1 |
| F9 | docs/TOOL_CALLER_PROMPT.md | 17-18, 96-102, 122 | 8 contradictions | SOLUTION needs model + rule; doubt/error -> STUCK | keywords alone give SOLUTION (router.py:144-145); error -> by_rule (:148-153); only an unknown label -> STUCK (tutor.py:126-129); regex differs (router.py:35-39) | wontfix | misleading | F1 |
| F10 | docs/TOOL_CALLER_PROMPT.md | 24-30 | 9 orphaned | label -> response table (T0, T5a, T6, T7, T9) | only OTHER branches (tutor.py:130-131); the rest share `_ask_model` (:132,219-225); SOLUTION adds the button text (:133-134); option-naming goes to the answer button first (:113-117) | wontfix | misleading | F1 |
| F11 | docs/TOOL_CALLER_PROMPT.md | 26-30 | 8 contradictions | label meanings | router.py:60-66 descriptions differ | wontfix | misleading | F1 |
| F12 | docs/TOOL_CALLER_PROMPT.md | 127-129 | 8 contradictions | rules catch rule-breaking and rudeness | no such rule (router.py:139-147); the model's not_productive covers them (:65) | wontfix | misleading | F1 |
| F13 | docs/TOOL_CALLER_PROMPT.md | 130-132 | 8 contradictions | several letters = ATTEMPT | `guesses_several_letters` -> OTHER (router.py:80-82,146-147) | wontfix | misleading | F1 |
| F14 | docs/TOOL_CALLER_PROMPT.md | 136-138 | 8 contradictions | narrow SOLUTION rule; an error gives the answer away | `_SOLUTION` is broad (router.py:35-39); chat never gives the answer (tutor.py:130-138,155-168) | wontfix | misleading | F1, F9 |
| F15 | docs/TOOL_CALLER_PROMPT.md | 119-123 | 8 contradictions | faults table (words not letters, chat, tags, cleaning) | router.py:105-114,131-136; tutor.py:50-54,71-77,113-125 | wontfix | misleading | F1, F3, F7 |
| F16 | docs/TOOL_CALLER_PROMPT.md | 148-150 | 9 orphaned | "we need ~150 made-up messages" | 250 exist (laptop/router_messages*.json; bakeoff-3:33-35); false-SOLUTION rate not reported | wontfix | misleading | F1 |
| F17 | docs/TOOL_CALLER_PROMPT.md | 37 | 7 terminology | "maths" inside the prompt | the code's prompt says "maths" (router.py:104); changing it leaves the measured condition (router.py:56-58) | wontfix | cosmetic | F1 |

Out of scope, reported: how-to/use-decider-2b-router.md:5 says nothing calls the router (tutor.py:125 now calls router.route; math-router.service exists, untracked); :177 says the several-letter rule is not written (router.py:80-82,146-147). Code (X8, suspected): router.py:35-39 `soluci[oó]\b` cannot match "solución"; "dame" missing; Catalan "resol" missing. router.py:3,20 and HANDOFF.md:31 cite this doc.

## S2 critique (diataxis: reference mixed with explanation/history and a backlog; docs-critic, 26 findings: 12 verified, 11 decision, 3 suspected)

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| T5 | docs/TOOL_CALLER_PROMPT.md | 3-6 | 1 lede | "five critical faults of the first version": first version not linked | - | wontfix | cosmetic | - |
| T6 | docs/TOOL_CALLER_PROMPT.md | 13 | 5 jargon | "default chat model" without server/port | GLOSSARY Language model (math-llm, 8081) | wontfix | cosmetic | T1 |
| T7 | docs/TOOL_CALLER_PROMPT.md | 13-15, 121 | 10 duplication | "Do not use decider-0.8b" | conclusion:12 adopts the decider family; router.py uses decider-2b | wontfix | misleading | T1 |
| T8 | docs/TOOL_CALLER_PROMPT.md | 14, 121 | 5 jargon | decider-0.8b unexplained | link how-to/install-decider-0.8b.md | wontfix | cosmetic | T1 |
| T9 | docs/TOOL_CALLER_PROMPT.md | 14-15 | 11 claims | decider trained to solve, not follow instructions: no source | - | wontfix | cosmetic | T1 |
| T10 | docs/TOOL_CALLER_PROMPT.md | 16, 63 | 5 jargon | "grammar" (GBNF) unexplained | - | wontfix | cosmetic | - |
| T12 | docs/TOOL_CALLER_PROMPT.md | 19-20 | 4 sentences | "the code cleans ... external text": which code | - | wontfix | cosmetic | T1 |
| T13 | docs/TOOL_CALLER_PROMPT.md | 28, 132 | 5 jargon | T0c, T1g unexplained | TUTOR_RESPONSE_TYPES.md:111,191 | wontfix | cosmetic | - |
| T14 | docs/TOOL_CALLER_PROMPT.md | 37 | 5 jargon | "maths" in prompt text | = F17 | wontfix | cosmetic | T1 |
| T15 | docs/TOOL_CALLER_PROMPT.md | 53-55 | 8 form | placeholders explained after the code | :105-111 | wontfix | cosmetic | - |
| T16 | docs/TOOL_CALLER_PROMPT.md | 72-103 | 10 duplication | doc's route/SOLUTION_RULE vs router.py | = F6, F9 | wontfix | misleading | T1 |
| T17 | docs/TOOL_CALLER_PROMPT.md | 122 | 11 claims | "D is also the most frequent M3Kang answer" + unshown first-version mapping | txto-no-heuristics.md (D 24.9%) | wontfix | cosmetic | - |
| T18 | docs/TOOL_CALLER_PROMPT.md | 121 | 4 sentences | "ignores the instruction in that line": which | - | wontfix | cosmetic | T1 |
| T19 | docs/TOOL_CALLER_PROMPT.md | 127-129 | 4 sentences | "Rules detect them": which rules | = F12 | wontfix | misleading | T1 |
| T20 | docs/TOOL_CALLER_PROMPT.md | 130-132 | 10 duplication | several letters = ATTEMPT | = F13 | wontfix | misleading | T1 |
| T21 | docs/TOOL_CALLER_PROMPT.md | 134-135 | 5 jargon | "prompt processing time on the UNO Q" | GLOSSARY Board, Token (prefill) | wontfix | cosmetic | - |
| T22 | docs/TOOL_CALLER_PROMPT.md | 133-134 | 11 claims | "this length is sufficient" stated as fact, untested | :8 | wontfix | cosmetic | T1 |
| T23 | docs/TOOL_CALLER_PROMPT.md | 148-150 | 10 duplication | "we need ~150 messages" | = F16 | wontfix | misleading | T1 |
| T24 | docs/TOOL_CALLER_PROMPT.md | 24-30 | 10 duplication | uppercase labels vs lowercase + not_productive in code/how-to | router.py:59; use-decider-2b-router.md:102; HANDOFF.md:31 | wontfix | cosmetic | T1 |
| T25 | docs/TOOL_CALLER_PROMPT.md | 125 | 3 headings | "## Decisions" | - | wontfix | cosmetic | - |

## S3 decisions (2026-11-15, user)

- F1, T1, T2, T3, F19 -> mark superseded: keep the file as a dated record of the discarded design. Add a short note at the top: it was a draft, never tested; the intent router that runs is decider-2b (GLOSSARY "Intent router", X22) in `student_app/router.py`, chosen in `docs/experiments/2026-11-router-0.8b-conclusion.md` and round 3; how to run it: `docs/how-to/use-decider-2b-router.md`. Do not rewrite the body (code is changing: uncommitted router integration in the checkout). Remove the three blank lines (F20).
- T4, T11, F18 -> use "intent router" and "tutor model" in the note (X22).
- F17, T14 -> keep prompt text verbatim (X23).
- Every other finding (F2-F16, T5-T26) -> wontfix: the body is a dated record of a superseded design (X1 style); the note tells the reader it is not today's design.
- Report to the docstring track (X8): `student_app/router.py:3,20` and `HANDOFF.md:31` cite this doc as the source of the labels and the safety rule; they must stop doing so once the router integration is committed.

## S4 repair (2026-11-15, docsjanitor)

- Fixed and removed from the tables: F1, T1, T2, T3, F19 (a "Superseded" warning note at the top: old draft, never tested; links to `student_app/router.py`, the 0.8B conclusion, round 3 and the decider-2b how-to); F18, T4, T11 (the note uses GLOSSARY "intent router" and "tutor model"); F20, T26 (three trailing blank lines removed).
- Every finding still in the tables is `wontfix` (S3): the body is a dated record of the draft, and the note says it does not describe the code. F17/T14 keep the prompt text verbatim (X23).
- Checks: link targets exist and render (`mkdocs build` into a scratch dir); `--strict` fails only on 7 warnings in other pages (BOARD_SETUP.md, LED_MATRIX_DESIGN.md links to `.claude/skills/`).

## S6 adversarial (2026-11-15; lenses ai-engineer, slop-hunter; scope: the note only)

The devils-advocate toolchain gate printed FATAL (`pip install --user` refused by PEP 668), so the scripted loop did not run. Reviewers were spawned by hand, one per lens. The adjudicator did not run: both lenses found the same root causes, and every cited line was checked by hand.

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| A1 | docs/TOOL_CALLER_PROMPT.md | 14 | 8 contradictions | "It does not describe the code" was false: the five labels and the safety rule are live | student_app/router.py:3,20,30; student_app/tutor.py:128-129 | fixed (round 1): the note names the two parts that still match | misleading | - |
| A2 | docs/TOOL_CALLER_PROMPT.md | 8-10 | 8 contradictions | "uses the label to choose how the tutor model replies" overstated | tutor.py:130-134 (OTHER -> fixed reply; the rest -> `_ask_model` without the label) | fixed (round 1): "with the tutor model or with a fixed reply" | misleading | - |
| A3 | docs/TOOL_CALLER_PROMPT.md | 4 | 11 claims | "Nobody tested it" too broad: Qwen3.5-0.8B was measured in round 1 with another prompt | docs/experiments/2026-11-router-bakeoff.md | fixed (round 1): "Nobody tested this prompt" | cosmetic | - |
| A4 | docs/TOOL_CALLER_PROMPT.md | 7-8 | 11 claims | "labels each chat message": some messages are answered before the router | tutor.py:111-123 | fixed (round 2): "labels chat messages" | cosmetic | - |
| A5 | docs/TOOL_CALLER_PROMPT.md | 5, 10 | 9 orphaned | GLOSSARY "Intent router" and "Tutor model", and decider-2b in `student_app/router.py`, exist only in uncommitted working-tree changes of other sessions; on `main` the links and the claim do not hold yet | `git show HEAD:GLOSSARY.md`, `git show main:student_app/router.py` | open: ship ordering, not a note edit (GLOSSARY and router commits must land with or before this note) | misleading | - |
| A6 | docs/how-to/use-decider-2b-router.md | 5, 177 | 8 contradictions | the linked how-to says no service runs the router and that the several-letter rule is not written | board/systemd/math-router.service (untracked); router.py:80 `guesses_several_letters` | open: out of scope, for the how-to's review | misleading | - |

Round 2 (confirming): both lenses SHIP; A1-A3 closed; A4 raised and fixed.

## 2026-11-15: link to the split TUTOR_RESPONSE_TYPES (main session, user approved)

The old file was split (13b59c1, 354cde7); the link now points to `docs/reference/tutor-response-types.md`. Link-only change.
