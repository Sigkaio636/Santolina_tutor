# Drift taxonomy

The one list of drift categories. `docsauditor` uses it to find drift.
`docsjanitor` uses it to fix drift. No other file restates it.

Weight comes from `diataxis`. For a **light** document, check only claims
that the code can confirm or refute: categories 1-5. For a **heavy** document,
check all 11.

1. **Stale instructions**: install, setup or build steps, CLI flags, config
   keys or env vars that no longer work or no longer exist.
2. **Outdated code snippets**: examples whose signatures, imports or output no
   longer match the current API.
3. **Renamed or removed references**: mentions of files, modules, functions or
   features that were renamed or deleted.
4. **Version drift**: version numbers, badges, dependency pins or "requires
   X.Y" lines that lag the real state.
5. **Broken links**: dead internal links (moved or removed files) and dead
   external links.
6. **Placeholder cruft**: leftover `TODO`, `FIXME`, `XXX`, lorem ipsum or
   copied template text.
7. **Terminology drift**: one concept named in more than one way. The
   canonical term is the one in `GLOSSARY.md`. If there is no glossary entry,
   the finding is a `decision`, not a guess.
8. **Contradictions and duplication**: the same thing documented two ways, or
   two documents that disagree. Which one is right is a `decision` unless the
   code settles it.
9. **Orphaned docs**: sections that document features that no longer exist.
10. **Formatting rot**: broken Markdown, inconsistent heading levels, malformed
    tables, code fences without a language tag.
11. **Type-mixing**: one document that has become a mix of tutorial, how-to,
    reference and explanation (see `diataxis`). Always a `decision`: the fix is
    a split, and a split is not a repair.

**Outside the list.** A problem that fits no category (a prose typo, the
document's language, a coverage gap) is not a finding. Report it in one line
under "Incidental", and never give it an id.

## Ground truth, in order

1. The code, the config and the repo itself.
2. `GLOSSARY.md` (or the file that `GLOSSARY-MAP.md` points to) for terms.
3. `docs/adr/` for why a thing is the way it is.

When none of these settles a claim, the finding is `suspected` or `decision`.
Never `verified`.
