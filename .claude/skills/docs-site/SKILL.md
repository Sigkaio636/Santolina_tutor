---
name: docs-site
description: Serve, build or extend the project's MkDocs site (Material theme) built from docs/. Use when the user wants to launch, preview, serve or build the docs site, add a page to it, or check that the docs build cleanly.
---

# Docs site (MkDocs + Material)

The site is configured in `mkdocs.yml` at the repo root. It renders `docs/`.
The dependencies are in the uv group `docs` (`mkdocs<2`, `mkdocs-material`).

## Launch it

1. Install the group: `uv sync --group docs`.
2. Serve with live reload:
   - In the Claude desktop app: `preview_start` with the name `docs` (`.claude/launch.json`).
     It opens http://127.0.0.1:8001 in the browser pane. Port 8000 belongs to the board
     explorer (`explorer/server.py`, often forwarded to the laptop), so don't use it.
   - In a terminal: `make docs-serve` (or `uv run --group docs mkdocs serve`).
3. Stop it with `preview_stop`, or press Ctrl+C.

## Check the build

```bash
NO_MKDOCS_2_WARNING=1 uv run --group docs mkdocs build --site-dir <scratch dir>
```

- Build into a scratch dir. `site/` is ignored, but don't leave build output in the repo.
- Read every `WARNING`. Expected: `BOARD_SETUP.md` links to `../.claude/skills/...`.
  Those links are correct on GitHub, but they are outside `docs/`. That is why `--strict` is not used.
  Fix any other broken link in the source file.

## Add a page

- Put the `.md` file in `docs/` or a subfolder. Navigation follows the folders, and `mkdocs.yml` has no `nav:`.
- Link it from `docs/index.md` if it is a page to start from.
- Add it to the review ledger as `pending`:
  `uv run --group docs python .claude/skills/docs-review/scripts/docs_status.py sync --yes`.
  `make docs-status` fails until you do. The `docs-review` skill reviews it later.
- To keep a file out of the site, add it to `exclude_docs` in `mkdocs.yml`. Already excluded:
  `vault/.obsidian/`, `vault/papers/**/parsed/` (third-party paper text), `*.pdf`.
- Mermaid diagrams work in ```` ```mermaid ```` fences (see the `mermaid-artist` skill).

## Red line (CLAUDE.md)

No page may contain M3Kang problem text or anything derived from it. Link to the
[dataset card](https://huggingface.co/datasets/qualcomm/M3Kang) instead. Check this
before you add a page. Never commit `site/`. Don't publish the site (`mkdocs gh-deploy`)
without the user's OK.
