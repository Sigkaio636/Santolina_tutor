---
name: docsjanitor
description: Clean and update existing documentation -- READMEs, guides, reference -- so it matches the current code. Audit for drift first, fix surgically, verify. Never invent facts to fill a gap. Use when the user wants documentation actually changed/fixed after code changes, or on request to "tidy the docs". If the user only wants documentation analyzed/audited/reviewed with no changes applied, use the docsauditor skill instead.
---

# Workflow: Documentation janitor

Use this workflow to **maintain** existing documentation, not to author new docs
from scratch. The janitor's job is to find where the docs have drifted from
reality -- stale commands, renamed APIs, dead links, outdated versions -- and
close the gap with the smallest correct edit.

The governing discipline: **verify against ground truth, never guess.** When
you cannot verify a claim against the code, config, or repo, flag it -- never
fabricate a plausible-sounding fix.

---

## When this applies

- The user asks to clean up, tidy, refresh, or update docs / READMEs.
- Code changed and the docs need to catch up.
- A doc is suspected stale, inconsistent, or broken and needs an audit **that
  will be acted on** -- fixes are the point of running this workflow.

If the user wants a **new** document written from scratch, use the Diataxis
documentation workflow instead. This one maintains what already exists.

If the user only wants documentation analyzed with no changes applied, use
`docsauditor` instead -- same drift taxonomy, but it never edits.

## Procedure

1. **Establish scope.** Determine which docs are in play -- a single README, a
   `docs/` tree, everything. If unspecified, default to the repo's top-level
   README(s) and confirm before widening. State the scope back to the user.

2. **Audit for drift. Do not edit yet.** Read the docs against the actual repo
   and produce a categorized findings list (see *What counts as drift* below).
   Every finding names the file, the line/section, what's wrong, and the
   evidence -- the real signature, the current version, the renamed module.

3. **Separate verifiable from unverifiable.** Split findings into "can fix with
   confidence" (evidence in hand) and "needs a human" (can't confirm the
   current truth without the user's input). Never move an unverifiable item
   into the fix pile by guessing.

4. **Fix surgically, one finding at a time.** Apply the smallest edit that
   corrects each verifiable finding. Touch only what that finding concerns.
   Preserve the doc's existing voice and structure -- you are repairing, not
   rewriting.

5. **Verify each fix.** Re-check links resolve, code snippets and CLI commands
   actually run / match the current API, versions are current, the doc still
   builds (if there's a docs build), and the repo's linter/formatter passes on
   changed files. If a fix can't be verified, revert it and move it to the
   flag pile.

## What counts as drift

Scan for these categories -- this is the janitor's matcher:

- **Stale instructions**: install/setup/build steps, CLI flags, config keys,
  or env vars that no longer work or no longer exist.
- **Outdated code snippets**: examples whose signatures, imports, or output no
  longer match the current API.
- **Renamed or removed references**: mentions of files, modules, functions, or
  features that were renamed or deleted.
- **Version drift**: version numbers, badges, dependency pins, or "requires
  X.Y" lines that lag the real state.
- **Broken links**: dead internal links (moved/removed files) and dead external
  links.
- **Placeholder cruft**: leftover `TODO`, `FIXME`, `XXX`, lorem-ipsum, or
  copy-paste template text.
- **Terminology drift**: one concept named inconsistently across docs; pick the
  term the project actually uses and align to it.
- **Contradictions & duplication**: the same thing documented two ways, or two
  docs that disagree.
- **Orphaned docs**: sections documenting features that no longer exist.
- **Formatting rot**: broken Markdown, inconsistent heading levels, malformed
  tables, code fences without language tags.
- **Type-mixing** (light Diataxis check): a README section that has quietly
  become a tutorial-plus-reference-plus-explanation tangle. Flag it; when you
  consolidate, keep types separated and cross-link rather than blend.

## Hard rules

- **Never invent facts.** If you can't verify the current truth, flag it for
  the user -- do not write a confident guess. This rule outranks tidiness.
- **Audit before editing.** Produce and (for a large scope) get sign-off on the
  findings list before applying fixes. No silent mass rewrites.
- **Smallest correct edit.** Repair in place; preserve the doc's voice,
  terminology, and structure. Don't restyle or "improve" beyond the finding.
- **One finding, one edit.** Keep changes traceable to individual findings; do
  not fold unrelated fixes together.
- **Don't fix unrelated code.** The janitor edits docs. If you spot a genuine
  code bug, note it as an incidental finding -- don't patch it here.
- **Stop at git.** Prepare and surface the edits; do not run git actions from
  this skill. Commit only when the user asks.
- **Match the project's voice.** Mine surrounding docs for tone and
  terminology; do not copy content between files unless asked.
- **No external browsing** beyond checking that a link the doc already contains
  still resolves. Don't pull in outside content to "enrich" a doc.

## Output to the user

- The **audit**: findings grouped by category, each with file, location, the
  problem, and the evidence.
- The **fixes applied**: what was changed and why, one line per finding, with
  the verification that passed (link resolves / snippet runs / lint clean).
- The **flag pile**: findings you could not verify, stated as questions the
  user can answer so a second pass can resolve them.
- **Incidental findings**: real issues spotted but out of scope (e.g. a code
  bug, a missing doc for a new public API), listed for the user to triage.
- Anything skipped or partially done, with the reason.

## Example invocation

> We renamed `deconv.run()` to `deconv.evaluate()` and bumped to 2.0. Go
> through the README and `docs/` and clean up anything that's now wrong.

Here the scope is given (README + `docs/`) and part of the ground truth is
handed to you (the rename, the version bump) -- so those are verifiable fixes.
But you'd still audit first: find every `run(` reference, every `1.x` version
string, every snippet importing the old name, and any links to a moved page --
then apply the surgical fixes, verify the snippets still match the current
signature, and flag anything you can't confirm (e.g. a described behavior that
may or may not have changed with 2.0) rather than assuming.
