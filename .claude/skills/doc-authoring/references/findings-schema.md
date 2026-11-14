# Findings schema

The contract between `docsauditor` (writes findings), `grilling` (resolves
decisions) and `docsjanitor` (applies fixes). Every finding has these fields:

| field | value |
|---|---|
| `id` | `F1`, `F2`, ... unique within one audit |
| `file` | path relative to the repo root |
| `line` | line number or range, e.g. `12` or `12-18` |
| `category` | number and name from `drift-taxonomy.md`, e.g. `3 renamed` |
| `claim` | what the document says, quoted or paraphrased in one line |
| `evidence` | what the ground truth says, with its path:line |
| `status` | `verified`, `suspected` or `decision` |
| `severity` | `breaks` (a reader following it fails), `misleading` or `cosmetic` |
| `depends_on` | ids that must be resolved first, or `-` |

## Status and who resolves it

| status | meaning | resolved by |
|---|---|---|
| `verified` | the doc is wrong and the evidence gives the correct fact | `docsjanitor` applies the fix |
| `suspected` | the doc looks wrong but the correct fact is not confirmed | the agent looks again (a subagent, not the user). Still open: it becomes `decision` |
| `decision` | the code cannot settle it: a canonical term, which of two docs is right, a type split, a claim only a person knows | the user, in a `grilling` round |

Never promote `suspected` to `verified` without new evidence. Never ask the
user for a fact the repo can answer: that is `suspected`, not `decision`.

## From findings to a grilling round

The frontier is every `decision` finding whose `depends_on` ids are all
resolved. Ask the whole frontier in one round, in the `grilling` format: one
numbered question per finding, with a recommended answer, so that "yes"
accepts it. Example: decide the canonical term (F4) before the sections that
use it (F7, F9, which list `depends_on: F4`).

A resolved answer becomes a `verified` finding, and the user's answer is its
evidence. When the answer fixes a term, `domain-modeling` writes it to
`GLOSSARY.md` at that moment.

## Example (hypothetical paths)

```
F3 | README.md | 41 | 2 snippets | `pkg.run(cfg)` | pkg/core.py:18 defines `evaluate(cfg)`, no `run` | verified | breaks | -
F4 | README.md, docs/intro.md | 12, 5 | 7 terminology | "learner" vs "student" | no GLOSSARY.md entry | decision | misleading | -
F7 | docs/intro.md | 20-30 | 11 type-mixing | how-to steps inside an explanation | - | decision | cosmetic | F4
```
