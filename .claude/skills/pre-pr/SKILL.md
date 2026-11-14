---
name: pre-pr
description: Prepare a change for a pull request in any repo - a simplify pass the user reviews, the documentation the change affects, and a draft PR with What and Why. Use before running gh pr create or gh pr ready, and whenever the user asks to open, send or submit a PR.
---

# Before a pull request

The user may not know git or GitHub well. Do these steps yourself, explain
each one in plain words, and ask only what needs their decision.

## 1. Simplify, then show it

Run the bundled `/simplify` skill on the change (reuse, simplification,
efficiency). If it is not available, review the diff for the same three
things yourself.

Then show the user what it changed, file by file, in one or two lines
each, and ask whether to keep it. Revert what they do not want. Never
delete a feature, page or domain to make the code shorter.

## 2. Documentation

If the change touches code, update the documentation it affects: the
README, files under `docs/`, the CHANGELOG, docstrings of public
functions. `/docsjanitor` can help when it is installed.

If no document is affected, say so to the user and write the reason
under Why in the PR body. Then end the gh command with the shell comment
`# pr-gate: no-docs <reason>`, for example
`gh pr create --draft --fill # pr-gate: no-docs only renames a test helper`.
The pr-gate hook reads that comment; gh ignores it. Do not put anything
before `gh`, or the user may get an extra permission prompt.

## 3. Open the PR

Ask the user before creating it. Create it as a draft
(`gh pr create --draft`), with a title in Conventional Commits form and
this body, in English:

```markdown
## What
Describe changes.

## Why
Explain the reason.
```

`--body`, `--body-file` and `--fill` skip the repo's PR template, so
write both sections yourself and never leave the placeholder text.

If the pr-gate hook blocks the command, fix what its message lists and
run the command again. Do not hand the message to the user as a task.
