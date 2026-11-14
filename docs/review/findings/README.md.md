# Findings: README.md

Open findings of `/docs-review`. Schema: `.claude/skills/doc-authoring/references/findings-schema.md`.

## S1 audit (2026-11-14)

Weight: heavy.

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| F1 | README.md | 36-51 | 3 renamed | tree puts `features.py`, `modeling/`, `plots.py` under `santolina_tutor/` | they are in `santolina_tutor/templates/`; README.md:107 uses that path | verified | misleading | - |
| F2 | README.md | 42 | 6 placeholder | `dataset.py`: "Scripts to download or generate data" (cookiecutter) | `santolina_tutor/dataset.py:1-7` extracts the M3Kang parquet shards | verified | misleading | - |
| F3 | README.md | 11, 15-34 | 6 placeholder | cookiecutter boilerplate (data/external..raw, notebooks, references/, reports/) | models/, notebooks/, references/, reports/ hold only .gitkeep — S3: S3 Q22 (user): trim the tree to used folders; one line for the empty template folders | verified | cosmetic | - |
| F4 | README.md | 86-87 | 8 contradictions | copied files keep their upstream paths, so the skills work unchanged | upstream `.skills/` became `.claude/skills/` (`.claude/skills/unoq-board/PROVENANCE.md:7`); upstream README became docs/BOARD_SETUP.md | verified | misleading | - |
| F5 | README.md | 94 | 7 terminology | "the model servers" | `GLOSSARY.md:15-17` Model services; README.md:152 uses it | verified | cosmetic | - |
| F6 | README.md | 74-77 | 1 stale | when pr-gate cannot decide it lets the command through | `.claude/hooks/pr-gate.sh:52,94` skip only the docs check; the draft check (72-81) still blocks | verified | misleading | - |
| F7 | README.md | 120-124 | 8 contradictions | red-line list leaves out problem images | `CLAUDE.md:13` lists them; `.claude/hooks/m3kang-guard.py:31-36` catches images only under data/ — S3: S3 Q21 (user): text only: README and CLAUDE.md say the hook catches images only under data/; no hook change | verified | cosmetic | - |
| F8 | README.md | 169 | 3 renamed | "Vendored skills keep their upstream LICENSE in their folder" | unoq-board, m3kang-copilot, unoq-hardware-ui, publish-project have PROVENANCE.md, no LICENSE — S3: the 4 vendored skills have only PROVENANCE.md ("Licence: None declared"); asd-ste100 has LICENSE | verified | cosmetic | - |
| F9 | README.md | 1-199 | 11 type-mixing | reference (tree, paths), how-to (docs commands) and explanation (red line, PR rules) in one file | - — S3 Q4 (user): no split; the lede states the type and steps go to a final "What to try" section | verified | cosmetic | F3 |

Incidental: lines 2-3 are Catalan, the rest English. The "other skills" table (164) leaves out `docs-review`.

## S2 critique (2026-11-14)

Type: explanation (project landing page), heavy. 32 findings (0 breaks, 6 misleading, 26 cosmetic).

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| C1 | README.md | 1-3 | readability/1 lede | the lede does not say who reads it or where to start | the entry point (docs/BOARD_SETUP.md) first appears at 101-102, after the tree | verified | misleading | - |
| C2 | README.md | 2-3 | readability/7 language | the lede is Catalan, the rest English | which language is canonical is the user's choice — S3 Q5 (user): everything in English except the transcript and original sources; US spelling | verified | cosmetic | - |
| C3 | README.md | 5 | readability/3 headings | "Project Organization" in Title Case | other headings use sentence case | verified | cosmetic | - |
| C4 | README.md | 82 | readability/3 headings | "## Arduino UNO Q" names hardware, not what the section gives | 82-169 hold a repo map, rules, red line and skills | verified | cosmetic | - |
| C5 | README.md | 118, 144 | readability/3 headings | "Red line" and "Skills for Claude" nested under "Arduino UNO Q" | both are repo-wide | verified | cosmetic | - |
| C6 | README.md | 191 | readability/3 headings | "### Credits" nested under "Documentation site" | credits are for the whole project | verified | cosmetic | - |
| C7 | README.md | 54, 80 | readability/8 form | `--------` rules before only 2 of 4 H2 sections | inconsistent separators | verified | cosmetic | - |
| C8 | README.md | 58-60 | readability/4 sentences | sentence of about 32 words with a parenthetical | 25-word rule | verified | cosmetic | - |
| C9 | README.md | 64-65 | readability/4 sentences | "the PR waits for documentation" | the hook blocks the command; nothing waits | verified | misleading | - |
| C10 | README.md | 70-71 | readability/5 jargon | "a `/simplify` pass you review" | not explained (it is a bundled skill, not in .claude/skills/) | verified | cosmetic | - |
| C11 | README.md | 91, 98 | readability/5 jargon | "the explorer" used before 97 defines it; "OCR" never explained | no GLOSSARY.md entry | verified | cosmetic | - |
| C12 | README.md | 91 | readability/8 form | empty "Runs on" cell for docs/BOARD_SETUP.md | a guide is not a runnable path | verified | cosmetic | - |
| C13 | README.md | 86 | readability/11 claims | "copied at commit `d6e3f1b`" has no link | docs/BOARD_SETUP.md:4 links it | verified | cosmetic | - |
| C14 | README.md | 101-102 | readability/6 steps | "Clone ... then follow BOARD_SETUP": no command, no check | the guide clones only at step 8.1 (docs/BOARD_SETUP.md:682-690) | verified | misleading | - |
| C15 | README.md | 109-110 | readability/4 sentences | "It needs `loguru` and `python-dotenv`" | "It" is ambiguous | verified | cosmetic | - |
| C16 | README.md | 114-116 | readability/4 sentences | "... plus `*.gguf`, `*.db` and `results/`" reads as kept in Git | .gitignore:8,12-13 excludes them | verified | misleading | - |
| C17 | README.md | 114-116, 120-124 | readability/10 duplication | two lists of excluded paths with different members | 115-116 vs 122-124 — S3 Q3 (user): canonical-copy rule (how-to/ for our flow, UNO_Q_BOARD_REFERENCE for specs, CLAUDE.md for the red line, GOAL_MUSTS for the checklist, README for credits); the other copy links to it | verified | misleading | S1 F7 |
| C18 | README.md | 120-121 | readability/4 sentences | 26-word passive sentence on the red line | passive hides who acts | verified | cosmetic | - |
| C19 | README.md | 129 | readability/8 form | a 30-word sentence in a table cell | rule 4/8 | verified | cosmetic | - |
| C20 | README.md | 132-133 | readability/11 claims | the CI check stops a merge only once it is a required check | the reader cannot tell if branch protection is on — S3: gh: main is not protected (2026-11-14), so the CI check does not block a merge | verified | misleading | - |
| C21 | README.md | 137-139 | readability/6 steps | `--range origin/main HEAD` has no expected output | .claude/hooks/m3kang-guard.py:217-222 prints "clean (N paths checked)" | verified | cosmetic | - |
| C22 | README.md | 146-147 | readability/4 sentences | statement and instruction in one sentence | subject changes | verified | cosmetic | - |
| C23 | README.md | 84, 147 | readability/5 jargon | "the organizers' repository" vs "the datathon repository" | two names for one repo | verified | cosmetic | - |
| C24 | README.md | 164-167 | readability/8 form | 18 skill names with no description or link | the table at 152-155 gives both | verified | cosmetic | - |
| C25 | README.md | 176-177 | readability/5 jargon | first use of uv, not explained | no GLOSSARY.md entry | verified | cosmetic | - |
| C26 | README.md | 185-186 | readability/4 sentences | "validate each one": document or stage? | it means each stage | verified | cosmetic | - |
| C27 | README.md | 189 | readability/5 jargon | "ledger" not defined | it is docs/review/status.yml (187) | verified | cosmetic | - |
| C28 | README.md | 197-198 | readability/9 links | model cards and RapidOCR without links | docs/BOARD_SETUP.md:1265-1267 has them | verified | cosmetic | - |
| C29 | README.md | 118-142 | readability/10 duplication | restates the red-line rule | CLAUDE.md:9-25 — S3 Q3 (user): canonical-copy rule (how-to/ for our flow, UNO_Q_BOARD_REFERENCE for specs, CLAUDE.md for the red line, GOAL_MUSTS for the checklist, README for credits); the other copy links to it | verified | cosmetic | - |
| C30 | README.md | 106-108 | readability/10 duplication | the "two predict.py" rule | CLAUDE.md:38-39; santolina_tutor/templates/README.md:7 — S3 Q3 (user): canonical-copy rule (how-to/ for our flow, UNO_Q_BOARD_REFERENCE for specs, CLAUDE.md for the red line, GOAL_MUSTS for the checklist, README for credits); the other copy links to it | verified | cosmetic | - |
| C31 | README.md | 191-198 | readability/10 duplication | the credits list | docs/BOARD_SETUP.md:1261-1267 — S3 Q3 (user): canonical-copy rule (how-to/ for our flow, UNO_Q_BOARD_REFERENCE for specs, CLAUDE.md for the red line, GOAL_MUSTS for the checklist, README for credits); the other copy links to it | verified | cosmetic | - |
| C32 | README.md | 13 | readability/5 jargon | "M3Kang" with no glossary entry | GLOSSARY.md:3 names it only in the lede | verified | cosmetic | - |
