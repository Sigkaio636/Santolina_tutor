# Provenance -- unoq-board

Vendored-in skill. Not authored here; fixes go upstream and return as a re-sync.

| Field | Value |
|---|---|
| Upstream | https://github.com/mpous/datathon-UPC-maths-qualcomm-arduino-unoq (`.skills/unoq-board/`) |
| Commit | `d6e3f1b0c28a7dc47db3143c17e1e609006cd0a4` |
| Branch | `main` |
| Vendored | 2026-11-14 |
| Licence | None declared: the upstream repository has no LICENSE file. |

## Divergences from upstream

Exhaustive. A new one is added here in the same commit that introduces it,
otherwise the next re-sync reverts it silently.

1. **Board folder.** `~/datathon-UPC-maths-qualcomm-arduino-unoq` -> `~/Santolina_tutor` (lines 15 and 18), because this repository is the one cloned on the board.

No other line is modified.

`.skills/README.md` upstream is not vendored: its symlink setup doesn't apply,
because skills here live directly in `.claude/skills/`. Its skills table is in
the root `README.md`.

## Re-syncing

```bash
git clone --depth 1 https://github.com/mpous/datathon-UPC-maths-qualcomm-arduino-unoq.git /tmp/unoq
diff /tmp/unoq/.skills/unoq-board/SKILL.md .claude/skills/unoq-board/SKILL.md
```

Read every hunk, re-apply the divergences above, and update the commit row.
The board code (`board/`, `copilot/`, `predict.py`, ...) comes from the same
commit; re-sync it together.

## Review notes

Checked at vendoring time for hidden injection, since this is third-party
content landing inside the trust boundary:

- No zero-width or bidi control characters.
- No HTML comments, `data:text/html` or `base64,` payloads, no
  `ANTHROPIC_BASE_URL` or `enableAllProjectMcpServers`.
- Shell commands in the skill (`ssh`, `scp`, `adb`, `systemctl`, `curl` to
  `127.0.0.1`) are the documented board operations, aimed at the user's own
  UNO Q, and only run when Claude follows the skill on request.
