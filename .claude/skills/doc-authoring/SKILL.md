---
name: doc-authoring
description: Orchestrates documentation work end to end. Route "author" writes a heavy document (README, anything under docs/, any non-reference doc). Route "maintain" audits and repairs existing docs with user decisions settled by grilling. Use for "write a guide", "rewrite the README", "bring the docs up to date".
---

# Documentation orchestrator

This skill orders the docs skills. It does not restate them. Each concept has
one owner:

| need | owner |
|---|---|
| type, weight, outline | `diataxis` |
| drift categories | `references/drift-taxonomy.md` |
| findings contract | `references/findings-schema.md` |
| find drift, change nothing | `docsauditor` (forked, read-only) |
| questions to the user | `grilling` |
| terms and decisions | `domain-modeling` (`GLOSSARY.md`, `docs/adr/`) |
| plan for a large repair | `structured-planning` |
| fix drift | `docsjanitor` |
| diagrams | `mermaid-artist` |
| language pass | `asd-ste100` |
| hostile review | `devils-advocate:adversarial-review` |

**Orchestrated mode.** You set the scope once, in M1 or A1. When this skill
calls another skill, pass the scope and the findings in the arguments. The
called skill does not ask for them again.

## Choose the route

- **author**: the user wants a new document, or a rewrite of a heavy one.
- **maintain**: the user wants existing docs brought up to date.

A light reference document needs neither route. Use `diataxis` to write it,
then `docsauditor` and `docsjanitor`.

## Route maintain

1. **M1 Scope.** Name the files. Default: the top-level `README.md`. State the
   scope to the user once.
2. **M2 Audit.** Invoke `docsauditor` with the scope. It returns findings in
   the schema and does not load the code into this context.
3. **M3 Grill.** Resolve every `suspected` finding yourself first (look in the
   repo, or dispatch a subagent). Put the frontier of `decision` findings to
   the user as `grilling` rounds. When a term is settled, `domain-modeling`
   writes it to `GLOSSARY.md` at that moment. Offer an ADR only when its three
   criteria hold. The step ends when the frontier is empty and the user
   confirms.
4. **M4 Plan.** Only if there are more than 10 verified findings or more than
   3 files: a `structured-planning` plan with one step per file. Wait for the
   user's go.
5. **M5 Repair.** Invoke `docsjanitor` with the verified findings, including
   the ones the user settled. It does not audit again and does not grill again.
6. **M6 Re-audit.** Invoke `docsauditor` on the changed files, with `lines:`
   set to the changed ranges. New findings go back to M3. **At most 2
   re-audits.** After that, report what is still open.

## Route author

1. **A1 Classify.** `diataxis`: type and weight. State both to the user. If
   the request mixes types, split the document or cross-link.
2. **A2 Gaps.** One `grilling` round for audience, goal and scope (this is
   step 2 of `diataxis`). Check every term against `GLOSSARY.md` with
   `domain-modeling`.
3. **A3 Outline.** `diataxis` proposes the outline. Wait for approval.
4. **A4 Write.** Take each claim from the code or config. Link to the source
   instead of copying numbers, because a copy goes stale. Use `mermaid-artist`
   for diagrams, and render every diagram: a diagram that only parses has not
   been checked. Write file text with the `Write` tool, never with a shell
   heredoc. A backticked command in an unquoted heredoc runs.
5. **A5 Maintain.** Run M2-M6 on the new file.
6. **A6 Language.** Apply `asd-ste100` to the text you wrote.
7. **A7 Review.** `devils-advocate:adversarial-review` on the file, with at
   most three lenses chosen by risk:
   - `methodologist` for claims and what a result means,
   - `slop-hunter` for padding and copied text,
   - `popular-science` when the readers are not specialists.

   Read the cited line before you act on a finding: a reviewer can be wrong.
   Fix what is real, then run one confirming round. **At most 2 rounds.** If
   an edit comes after the last round, run M6 on it.

## Rules

- **Never commit.** A commit happens when the user asks.
- **Say what did not run.** Never claim a check that did not run.
- **Leave other people's changes alone.** Name an untracked file that is not
  yours. Do not stage it.
- **Do not sweep.** Fix the lines in scope and no others.

## Not this skill

- A change to `.claude/` itself: use `anthropic-skills:skill-creator`.
- Code comments, commit messages, answers in chat: just answer.
