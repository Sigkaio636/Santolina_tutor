---
name: docs-review
description: Full human-readability review of one document of this repo (MkDocs site pages, README.md, data/README.md, CLAUDE.md, mkdocs.yml) through seven stages - audit, critique, decisions, repair, language, devil's-advocate adversarial review, sign-off - asking the user at each stage and recording in docs/review/status.yml which stages the user validated. Use for "review the docs", "docs-review", "validate this document", "what is the review status of the docs", or before publishing the docs.
---

# Documentation review with sign-off

Goal: every document reads well for a person who has never seen this repo,
and every text has been reviewed and **validated by the user**. The ledger
`docs/review/status.yml` records, per document, the status of each stage. The
site page `docs/review/index.md` shows it.

This skill only orders other skills. Each one owns its rules:

| stage | ledger key | owner |
|---|---|---|
| S1 | `audit` | `docsauditor` (forked, read-only, agent `docs-auditor`) |
| S2 | `critique` | agent `docs-critic` (read-only) + `diataxis` for type and weight |
| S3 | `decisions` | `grilling` (questions to the user) + `domain-modeling` (`GLOSSARY.md`) |
| S4 | `repair` | `docsjanitor` (+ `mermaid-artist` for diagrams) |
| S5 | `language` | `asd-ste100` |
| S6 | `adversarial` | `devils-advocate:adversarial-review` + `devils-advocate:adjudicator` |
| S7 | `signoff` | the user |

Findings follow `.claude/skills/doc-authoring/references/findings-schema.md`
and `drift-taxonomy.md`. Pass findings from stage to stage in the arguments.
A called skill does not audit or ask again.

**The findings file.** `findings <path>` gives the document's findings file
(for example `docs/review/findings/docs__BOARD_SETUP_md.md`). It keeps the
findings between sessions:

- After S1, S2 and S6, write every finding into it as one findings-schema
  table, with its status.
- S3 updates the status of each finding that the user settles. S4 marks each
  fixed finding `fixed`.
- When a run continues a review, read this file. Do not run a validated stage
  again to get its findings back.
- The file goes to Git. A finding about M3Kang problem text cites the line
  (`path:line`) only, never the text.

## The ledger script

Run from the repo root:

```bash
S=".claude/skills/docs-review/scripts/docs_status.py"
uv run --group docs python $S check          # ledger vs docs in scope, stale sign-offs
uv run --group docs python $S table          # status table
uv run --group docs python $S set <path> <stage> <status> --note "<one line>"
uv run --group docs python $S reopen <path> <stage>   # this stage and later ones to pending
uv run --group docs python $S findings <path>         # path of the findings file
uv run --group docs python $S text <path>             # visible text of an HTML page
uv run --group docs python $S sync --yes     # add new docs as pending, drop deleted ones
```

Statuses: `pending`, `done` (the agent finished the stage), `validated` (the
user approved it), `n/a` (the stage does not apply; the note says why).
`set` and `reopen` regenerate the site page.

What the script enforces:

- **Scope.** Only documents committed to Git are in scope. Commit a new
  document before you review it.
- **Order.** `set` refuses `done` or `validated` while an earlier stage is
  `pending`. `signoff validated` needs every earlier stage `validated` or `n/a`.
- **Stale.** A document whose file changes after `signoff: validated` is
  stale and fails `check`.
- **Changed outside the review.** Each `set` and `reopen` stores the file's
  hash. If the file changes later while a review is open, `check` fails. The
  change came from someone else, not from S4.

## Arguments

- `[path]`: the document to review. No path: run `sync` (dry run first), then
  take the first document in the ledger that is not fully validated. The
  ledger is in priority order.
- `--stage <name>`: redo one stage of the document. Run
  `reopen <path> <name>`: that stage and every later stage go back to
  `pending` (`n/a` stays), because their input changed.
- `--status`: run `check` and `table`, show the result, stop.

## Flow (one document per run)

0. **Start.** Run `check`. State the document, its current stage statuses and
   which stages will run. Skip a stage that is already `validated`. Read the
   findings file if it exists. If `check` says the document **changed outside
   the review**, show `git diff` / `git log` for it and ask the user: reopen
   from `audit` (`reopen <path> audit`), or accept the change (`set` the
   current stage again with the same status).
1. **S1 audit.** Invoke `docsauditor` with the document as scope. For
   `mkdocs.yml`: check `exclude_docs`, theme and extensions against `docs/`
   and the docs build (`mkdocs build` into a scratch dir).
2. **S2 critique.** Invoke `diataxis` to state the type and weight. Spawn the
   `docs-critic` agent with the path and the type. Read the cited lines
   before you accept a finding. For `mkdocs.yml` the critique is the
   navigation as a reader sees it: section order, page titles, orphan pages.
3. **S3 decisions.** Resolve `suspected` findings yourself first. Put every
   `decision` finding from S1 and S2 to the user as `grilling` rounds. A
   settled term goes to `GLOSSARY.md` through `domain-modeling`.
4. **S4 repair.** Invoke `docsjanitor` with the verified findings, including
   the ones the user settled. Fix only this document (and a link target only
   when the finding names it).
5. **S5 language.** Scope: the text changed in S4 and any paragraph S2
   flagged for sentences or jargon. Keep the document's language. Never
   translate.
   - English: invoke `asd-ste100`, then run
     `.claude/skills/asd-ste100/scripts/ste-lint.py` on the document. For an
     HTML page, lint the output of `text <path>`.
   - Any other language (Spanish, Catalan): `asd-ste100` and its linter are
     English only. Apply its structural rules by hand: at most 25 words per
     sentence, one idea per sentence, active voice, a list for 3 or more steps,
     one term per concept. The note says `manual (<language>)`.
   - `mkdocs.yml`: `n/a`.
6. **S6 adversarial.** Invoke `devils-advocate:adversarial-review`, Mode 2,
   scoped to this one document. Lenses, at most three:
   - guides with steps (`BOARD_SETUP.md`, `vault/guides/`): `analyst`,
     `popular-science`, `slop-hunter`;
   - research notes (`vault/papers/`, `CHALLENGE_CONTEXT.md`): `methodologist`,
     `popular-science`, `slop-hunter`;
   - `README.md`, `index.md`, `CLAUDE.md`: `popular-science`, `slop-hunter`,
     `ai-engineer` (for `CLAUDE.md`) or `architect` (for the others);
   - `mkdocs.yml`: `ux-designer`, `architect`.
   Use `devils-advocate:adjudicator` when more than one lens reports. Fix what
   is real through S4 and S5 again. **At most 2 rounds**; then report what is
   still open. Before the first S6 of the session, ask the user before the
   plugin's toolchain gate runs, because it installs a Python package
   (`pip install --user stellars-claude-code-plugins`). If the user says no,
   spawn `devils-advocate:adversarial-reviewer` by hand, one per lens, and
   say that the scripted loop did not run.
7. **S7 sign-off.** Show the user the final diff of the document and the list
   of findings that stay open. Ask for the sign-off.

## After each stage: record and ask

1. `set <path> <stage> done --note "<what happened, counts>"`.
2. Show a summary of three lines at most: what the stage found or changed.
3. Ask with `AskUserQuestion`: **Validate** (recommended when nothing is open)
   or **Redo** (the user says what to change).
4. On Validate: `set <path> <stage> validated`. On Redo: keep `done`, add the
   user's note, redo the stage.

**Only the user validates.** Never write `validated` without the user's
answer in this turn. A stage that does not apply is `n/a` with a note, never
`validated`. When the user stops mid-way, leave the statuses as they are: the
next run continues from the first stage that is not validated.

## Rules

- **Never commit.** A commit happens when the user asks.
- **Say what did not run.** Never mark a stage `done` when its skill did not run.
- **M3Kang red line.** No document may contain M3Kang problem text
  (`CLAUDE.md`). A `breaks` finding of this kind stops the flow until the text
  is removed.
- **Leave other people's changes alone.** Do not stage or edit an untracked
  file that is not the document under review.
- **Do not sweep.** Fix the document in scope only.
- End the run with `check` and `table`, and report the document's statuses.
