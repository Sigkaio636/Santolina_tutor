# Provenance -- asd-ste100

Vendored-in skill. Not authored here; fixes go upstream and return as a re-sync.

| Field | Value |
|---|---|
| Upstream | https://github.com/danyuchn/asd-ste100-skill |
| Commit | `7d4a135a199a5d7447c4886bcd7ffe742a627bc9` |
| Branch | `master` |
| Vendored | 2026-09-29 |
| Licence | MIT, (c) 2026 Dustin Yuchen Teng -- see `LICENSE` |

## Divergences from upstream

Exhaustive. A new one is added here in the same commit that introduces it,
otherwise the next re-sync reverts it silently.

1. **ASCII transliteration**, required by `.claude/rules/general/style.md`
   ("No em dashes ... or arrows"). Applied to every `.md` and `.py` file:
   `U+2014` -> `--`, `U+2192` -> `->`, `U+2264` -> `<=`. Prose only; no
   identifier, regex or test assertion in `scripts/ste-lint.py` contains a
   non-ASCII character, so the change is comment- and docs-only there.
   `python3 scripts/ste-lint.py --selftest` passes after the edit.
2. **`README.md` dropped.** It is the upstream GitHub landing page and
   duplicates `SKILL.md`. This file replaces it.

No other file is modified. `SKILL.md`, `references/`, `examples/`,
`scripts/` and `LICENSE` are otherwise byte-identical to the commit above.

## Re-syncing

```bash
git clone --depth 1 https://github.com/danyuchn/asd-ste100-skill.git /tmp/ste
diff -r --exclude=.git /tmp/ste .claude/skills/asd-ste100
```

Read every hunk, re-apply the divergences above, update the commit row, then
re-run `python3 .claude/skills/asd-ste100/scripts/ste-lint.py --selftest`.

## Review notes

Checked at vendoring time for hidden injection in skills and rules, since this
is third-party content landing inside the trust boundary:

- No zero-width or bidi control characters.
- No HTML comments, `<script>`, `data:text/html` or `base64,` payloads.
- No `curl`/`wget`/`nc`/`scp`/`ssh`, no `enableAllProjectMcpServers`, no
  `ANTHROPIC_BASE_URL`.
- `scripts/ste-lint.py` is stdlib-only (`json`, `re`, `sys`). It opens only
  the paths given as arguments and reads stdin. No network, no subprocess,
  no writes. It therefore adds nothing to `pyproject.toml`.
