# Findings: docs/explanation/student-data-privacy.md

Review round 2026-11-15. Cross-cutting decisions: `docs/review/findings/_cross-cutting.md`.

S4 (2026-11-15) fixed and deleted every finding of S1 and S2 except the part of PV6 below.
CPV4 (unsourced postponement) and CPV7 (IP addresses) were confirmed and fixed: the date sentence now says only that it may change; the IP row names the student app's in-memory list (student_app/board_state.py:73-78) and the laptop demo's log (teacher_app/demo.py:91).

## Open

| id | line | category | claim | evidence | status | severity |
|---|---|---|---|---|---|---|
| PV6 | 52 | 8 contradictions | the label row names the committed keyword rule; with the router work the label comes from the intent router (decider-2b, `math-router.service`) and events add a `router` field | student_app/router.py, tutor.py uncommitted on 2026-11-15 (X26: left open until committed) | verified | cosmetic |

## S6 adversarial, round 1 (2026-11-15; methodologist 8, popular-science 18, slop-hunter 13; reviewers spawned by hand, plugin toolchain FATAL (PEP 668), adjudicator not run: merged by root cause here)

| id | line | category | claim | evidence | status | severity |
|---|---|---|---|---|---|---|
| S1 | 45-60 | 8 contradictions | table omits view_opened, language, session_end reason, event times (2 lenses) | state.py:181-195; events.py:44 | fixed (row added, verdict OK chosen by the user) | misleading |
| S2 | 45-60 | 5 jargon | verdict labels undefined (2 lenses) | - | fixed (one-line legend, user's choice) | misleading |
| S3 | 67-68 | 8 contradictions | retention/erasure omit laptop `raw/` copies and board `progress/` files (2 lenses) | unload.py:110-118; config.py:26-27; progress.py:1-4 | fixed | misleading |
| S4 | 59 | 11 claims | learning path "no model": topic comes from embedding vectors (2 lenses) | planner.py:1,14-16,119-123 | fixed ("no language model") | misleading |
| S5 | 53 | 11 claims | "not about the student" contradicts line 10 (2 lenses) | events.py:39-46 | fixed | cosmetic |
| S6 | 3 | 1 lede | the page never says what Santolina is physically | - | fixed | breaks |
| S7 | 61-71 | 8 contradictions | table's Reduce/Drop missing from the "missing" list | - | fixed (Data to cut bullet) | misleading |
| S8 | 27, 85 | 2 links | APDCAT deep link redirects to the homepage | curl: 301 -> apdcat.cat/ca | fixed (links the website, user's choice) | cosmetic |
| S9 | various | 10 duplication | deleted: Art. 83, 3(d) paraphrase, date hedge, repeated emotion ban, Strengths 76-78, unused Orientaciones source, demo IP sentence | reviewers' evidence | fixed | cosmetic |
| S10 | various | 5 jargon | "age of consent", BOE, apartado, sticker link, "international transfer", "data minimisation", DPIA source, token, "No." in the IP row, label "each" | reviewers' evidence | fixed | cosmetic |
| R1 | 60 | - | delete the "Any use outside class" row | keeps the consent point inside the comparison | rejected | cosmetic |
| R2 | end | - | add a closing sentence that answers the lede | adds text; the table and the missing list answer it | rejected | cosmetic |
| G1 | 51 | 7 terminology | the [tutor model] GLOSSARY link: "Tutor model" is not in GLOSSARY.md at HEAD (only in the uncommitted working tree) | git show HEAD:GLOSSARY.md | open (main session: commit GLOSSARY.md) | cosmetic |

## S6 adversarial, round 2 (confirming, methodologist; S1-S10 confirmed; 1 suspected finding)

| id | line | category | claim | evidence | status | severity |
|---|---|---|---|---|---|---|
| M2-1 | 57 | 11 claims | the IP row covers the app only: the board's hotspot (NetworkManager shared mode, dnsmasq) may keep a DHCP lease file with each phone's IP, MAC address and device name | teacher_app/links/adb.py:156-186 (`ipv4.method: shared`); not checked on a board. Check: `cat /var/lib/NetworkManager/dnsmasq-*.leases` on the board | suspected (cell now says "Not stored by the app") | misleading |

Round cap reached (2).

## S3 decisions (2026-11-15, user)

- PV4 -> the legal reading describes today: answers judged by letter comparison, the next problem by a fixed rule (GLOSSARY Learning path), no model decides; say what would move it toward Annex III 3(b) (a model that grades or decides). No new legal advice.
- PV6 -> add a row for the intent router's automatic label of each student message and the reply timings (X26 commit check). Validated with the nuance: the row describes the committed keyword rule; the decider-2b part stays open.
- PV1/CPV2, PV2/CPV1, CPV3, CPV4 and the rest of the verified findings -> fixed. CPV5: add an English gloss after each Spanish legal quote.
