# Findings: docs/reference/board-data-contract.md

Review round 2026-11-15. Cross-cutting decisions: `docs/review/findings/_cross-cutting.md`.

S4 (2026-11-15) fixed and deleted every finding of S1 and S2 except the one below.
CDC10 and CDC11 were confirmed (`classroom/__init__.py:8`, `classroom/schemas.py:14,57`) and fixed.
CDC15 needs no edit here: the classroom/README.md review owns the duplicates and links to this page.

## Open

| id | line | category | claim | evidence | status | severity |
|---|---|---|---|---|---|---|
| DC3 | 93 | 2 snippets | `copilot_reply` tutor fields omit `router` (which part labelled the message: rule or decider-2b) | student_app/tutor.py `out["log"]["router"]`, uncommitted on 2026-11-15 (X26: left open until the router work is committed) | verified | misleading |

## S6 adversarial, round 1 (2026-11-15; architect 16, popular-science 18, slop-hunter 13; reviewers spawned by hand, plugin toolchain FATAL (PEP 668), adjudicator not run: merged by root cause here)

| id | line | category | claim | evidence | status | severity |
|---|---|---|---|---|---|---|
| A1 | 15 | 8 contradictions | `assignments.json` shown flat; the file is `{"assignments": [...]}` (3 lenses) | classroom/packs.py:79; teacher_app/services/assignments.py:68 | fixed | breaks |
| A2 | 17 | 8 contradictions | `progress/` row hides the `exercises` map and its key (3 lenses) | classroom/progress.py:6-9 | fixed | misleading |
| A3 | 107 | 2 snippets | `media` "paths inside the pack"; only `media/<file>` is served | student_app/catalog.py:171-175,192 | fixed | breaks |
| A4 | 22 | 8 contradictions | "readers ignore unknown fields" hides that a higher `schema_version` is rejected (3 lenses); `contract_version` read by nothing | schemas.py:64-66; state.py:98-105; status.py:87 | fixed | breaks |
| A5 | 31 | 8 contradictions | lib/ copy "at every connection": only at setup and when the board's page opens | teacher_app/web/main.py:248; setup.py:57 | fixed | misleading |
| A6 | 49 | 8 contradictions | professor mode "follows the mode": the answer gate depends on the teacher visit | state.py:302,419 | fixed | misleading |
| A7 | 55 | 8 contradictions | the 2 h closed rule is computed by classroom.status on the board, not the teacher app | events.py:115-121; unload.py:113 | fixed | misleading |
| A8 | 47 | 8 contradictions | the student app also reads identity.json and lib/VERSION | events.py:71; server.py:265 | fixed | misleading |
| A9 | 113 | 11 claims | "retrieval may find a pack exercise; leaks() keeps the answer out": free_items drops pack problems; leaks() checks only the current exercise | catalog.py:156-166; tutor.py:80-95 | fixed | misleading |
| A10 | 3-13 | 1 lede | lib/ mechanics before the layout; RELEASE "why" missing | student_app/__init__.py:11-13 | fixed | cosmetic |
| A11 | various | 5 jargon | `name` of identity, "unloaded", "visit", `new_login`, `page_hidden` "nothing", `path_reason` null, "Which pack is active", `rag_index_path` default, `kangaroo-index` virtual, `board_time` in status, `closed` flag, M3Kang link, $SANTOLINA_ROOT, Optional fields of copilot_reply, schemas.py pointer | reviewers' evidence | fixed | cosmetic |
| R1 | 28 | - | delete the `exp/program-solver` branch note | X4 keeps it (user decision) | rejected | cosmetic |
| R2 | 125 | - | name config.env ports instead of 8081/8082/8084 | classroom/status.py:22 checks literal ports, so the page states what status checks | rejected | cosmetic |
| R3 | 51 | - | add read_events half-line rule, ISO/UUID details | detail for a validator writer; the schemas.py pointer covers it | rejected | cosmetic |

Incidental (code, X8 docstring track): `classroom/schemas.py:22-34` payload comments (no `restart`) and `classroom/events.py:5-10` example (`student_finished`) duplicate this page; `classroom/status.py:22` and `student_app/llm.py:16` repeat the config.env ports; a manifest without `count`, or an exercise without `kind`/`language`/`level`, raises an uncaught TypeError (packs.py:72, catalog.py:124).

## S6 adversarial, round 2 (confirming, architect; A1-A3, A5-A8, A10 confirmed; 5 new claims from round-1 fixes were false)

| id | line | category | claim | evidence | status | severity |
|---|---|---|---|---|---|---|
| N1 | 22 | 11 claims | effect of a higher `schema_version` per file (identity.json stops every login; progress/ is never checked) | events.py:71; state.py:96-99,124; server.py:146-149 | fixed | misleading |
| N2 | 20, 22 | 11 claims | required fields come from the dataclass defaults, not `check()`; `contract_version` is required | schemas.py:68,103,135-139 | fixed | misleading |
| N3 | 113 | 11 claims | free mode exclusion matches `meta.m3kang_id`; with no index it uses the packs | catalog.py:160,166 | fixed | cosmetic |
| N4 | 81 | 11 claims | `view_opened` and `session_end` carry no exercise context | state.py:151-155,195 | fixed | cosmetic |
| N5 | 125 | 11 claims | `board_time` is Unix seconds, not ISO 8601 | status.py:80,88 | fixed | cosmetic |

Round cap reached (2): the N1-N5 fixes were checked against the code by the main session, not by a third reviewer round.

## Incidental (not this document)

- `classroom/events.py:10` docstring example uses `reason="student_finished"`; `classroom/schemas.py:23` comment lacks `restart` (X8 docstring track).

## S3 decisions (2026-11-15, user)

- DC7 -> add `topics.jsonl` and `index.db` to the board layout as "read by the apps, not part of the contract: copied by hand / built on the board" (X4 for topics.py). DC6 follows.
- DC14 -> state the rules as facts ("the outbox is append-only for the student app"); keep the code example, corrected (DC1/CDC1, DC2/CDC3).
- CDC15 -> the classroom/README.md review owns the duplicates (C7, C14, C15); this page stays canonical for the contract and the README links here.
- DC3 (X26 commit check), DC4, DC5/CDC5 (tutor model), DC8-DC13, CDC2, CDC4, CDC6-CDC14 -> fixed.
