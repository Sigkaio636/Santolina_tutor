---
name: docsjanitor
description: Fix existing documentation so it matches the current code -- READMEs, guides, reference. Applies the smallest correct edit per finding, verifies it, never invents a fact. Use when the user wants docs fixed, updated or tidied after code changes. For an audit with no edits, use docsauditor.
---

# Documentation janitor

You repair documentation that already exists. You do not write new documents
(that is `doc-authoring`) and you do not restructure them (a type split goes to
`diataxis`).

**Verify against ground truth. Never guess.** If you cannot confirm the
correct fact, you do not write it.

## Input

- **A findings list** in the schema of
  `.claude/skills/doc-authoring/references/findings-schema.md`, from
  `doc-authoring` or from a `docsauditor` report earlier in this conversation.
  Do not audit again. Go to step 2.
- **No findings list.** Invoke `docsauditor` with the scope, then go to step 2.
  The scope is the files the user named. If they named none, use the
  top-level `README.md` and say so.

## Procedure

1. **Get findings** as described in Input.
2. **Settle what is not verified.**
   - `suspected`: look again in the repo. With evidence, it becomes `verified`.
     Without evidence, it becomes `decision`.
   - `decision`: put the frontier to the user in a `grilling` round (see the
     findings schema). When an answer fixes a term, `domain-modeling` writes it
     to `GLOSSARY.md` at that moment. Offer an ADR only when `domain-modeling`'s
     three criteria hold.
   - Called from `doc-authoring`: it has already done this step. Skip it.
3. **Plan, if the scope is large.** More than 10 verified findings or more
   than 3 files: write a plan with `structured-planning`. One step per file,
   with the finding ids of each step and its check. Wait for the user's go.
4. **Fix.** Apply the smallest edit that corrects each verified finding.
   Group edits by file, with one writer per file. Keep the voice, terms and
   structure of the doc. Do not touch lines that no finding names.
5. **Verify each fix** with a check that cannot change anything:
   - links: the target file exists, or the external URL resolves;
   - snippets and APIs: `grep` the definition first. Use
     `python -c "import inspect, m; print(inspect.signature(m.f))"` only when
     grep cannot settle it, because an import runs the module's top-level code;
   - CLI commands and make targets: read the Makefile or run `--help`. **Never
     run a make target, an install, or a command that writes, deletes or
     downloads.**
   - if `mkdocs.yml` exists: `mkdocs build --strict --site-dir <a temp dir>`,
     so that the build output does not land in the repo;
   - the repo linter or formatter on the changed files, in check mode only.

   A fix that fails its check is reverted and becomes `suspected`.

## Category rules

The categories are in
`.claude/skills/doc-authoring/references/drift-taxonomy.md`. The weight rule is
in `diataxis`. Three categories have a janitor-specific rule:

- **Terminology (7):** align to `GLOSSARY.md`. Without a glossary entry, this
  is a `decision`. Never pick the term yourself.
- **Contradictions (8):** fix only the side the evidence proves wrong.
- **Type-mixing (11):** never fix it here. Report it and route it to `diataxis`.

## Hard rules

- **Never invent facts.** This rule outranks tidiness.
- **Smallest correct edit.** No restyling and no improvements beyond what the
  finding says.
- **Every edit traces to a finding id.**
- **Docs only.** A code bug goes under Incidental. Do not patch it.
- **No git.** Do not stage or commit. A commit happens when the user asks.
- **No external browsing**, except to check that a link already in the doc
  still resolves.

## Report

- **Fixed:** `id | file:line | change | check passed`, one line per finding.
- **Open:** `suspected` or `decision` findings that are still unresolved, with
  the reason.
- **Incidental:** real issues that are out of scope.
- **Not run:** any check that was skipped, with the reason.
