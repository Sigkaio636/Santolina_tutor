---
name: doc-authoring
description: Use when you are about to write or substantially rewrite a document that a person will read and that must be precise -- a guide, a new file under docs/, the root README, a write-up for the team. Triggers: write a guide, write documentation, new document under docs, rewrite the README, heavy document, document for human readers. Runs the whole chain in order -- diataxis, write, docsauditor, docsjanitor, language pass, adversarial review with a confirming round, final audit. Not for light reference docs (docsauditor then asd-ste100 is enough), code comments, answers in chat, or files under .claude/ (use rules/skills/skill-acceptance.md).
---

# Workflow: author a heavy document

This skill orders the checks that a heavy document needs, so that none of them
waits for someone to ask. It calls the skills below and does not restate them.
`diataxis` classifies and writes. `docsauditor` checks and writes nothing. This skill is the order between them.

A document is **heavy** when it is the project `README.md`, anything under
`docs/`, or any document whose type is not reference. Start here before
you write the first line, not after the file exists.

## The chain

1. **Classify.** Run `diataxis`. One document has one type. State the type and
   the weight back to the user. If the request mixes types, say so and split it
   or cross-link.
2. **Write.** Take each claim from the code, the Makefile or the ROADMAP.
   Link to a package README instead of copying its numbers, because a copy goes
   stale. Draw diagrams with `mermaid-artist` and render them. A diagram that
   only parses has not been checked.
3. **Audit.** Run `docsauditor` on the file. It is read-only. Every finding is
   verified or suspected.
4. **Repair.** Run `docsjanitor` on the verified findings. Source or soften a
   suspected claim. Never invent a fact to close a finding.
5. **Language.** Follow `rules/docs/language.md`: American English in the text
   you wrote.
6. **Review.** Run `/adversarial-review` on the file. Never use the plugin's own
   pip gate. Pick lenses by where the risk lives, at most three:
   - `methodologist` for claims, caveats and what the document says a result means,
   - `slop-hunter` for padding and copied text,
   - `popular-science` when the readers are not specialists.

   Adjudicate each finding yourself. Read the cited line before you act,
   because a reviewer can be wrong. Fix what is real, then run a **confirming
   round** with the closure list. The review is clean only when the confirming
   round is clean.
7. **Check.** Re-run `docsauditor` on the final text.

## Rules for this chain

- **Never commit** from this skill. A commit happens when the user asks.
- **Say what did not run.** If an edit came after the last review round, run the
  check again or say in your report that it did not run. Never claim a check that did not run.
- **Write file text with the `Write` tool.** In an unquoted shell heredoc, a
  backticked command inside the text is executed by the shell. A backticked
  `make` line in a heredoc once started a real run.
- **Leave other people's changes alone.** Name an untracked file that is not
  yours, and do not stage it.
- **Do not sweep.** Fix the lines in scope and no others.

## Which skill owns what

| need | skill |
|---|---|
| type and weight | `diataxis` |
| find drift, change nothing | `docsauditor` |
| fix drift | `docsjanitor` |
| diagrams | `mermaid-artist` |
| hostile review | `/adversarial-review` |

## Not this skill

- A light reference document: run `docsauditor` on the file, then `asd-ste100`.
- A change to `.claude/` itself: follow `rules/skills/skill-acceptance.md`.
- A question in chat: answer it.
