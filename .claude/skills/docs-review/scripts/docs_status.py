#!/usr/bin/env python3
"""Validation ledger for the /docs-review skill.

The ledger (docs/review/status.yml) records, for every document in scope,
the status of each review stage. The page docs/review/index.md is generated
from it for the MkDocs site.

Run from the repo root, with the `docs` uv group (MkDocs and PyYAML):

    uv run --group docs python .claude/skills/docs-review/scripts/docs_status.py check
    ... table
    ... set README.md audit done --note "12 findings, 3 decisions"
    ... reopen README.md critique     # see SKILL.md, Arguments
    ... findings README.md            # path of the document's findings file
    ... text docs/GUIDE.html          # visible text, for ste-lint.py
    ... sync [--yes]

Scope: documents committed to Git. Only the user validates. The skill writes
`validated` only after the user says so in the same turn.
"""

from __future__ import annotations

import argparse
import functools
import hashlib
from html.parser import HTMLParser
from pathlib import Path
import subprocess
import sys

from mkdocs.config import load_config
from mkdocs.structure.files import get_files
import yaml

ROOT = Path(__file__).resolve().parents[4]
LEDGER = ROOT / "docs" / "review" / "status.yml"
PAGE = ROOT / "docs" / "review" / "index.md"
FINDINGS = ROOT / "docs" / "review" / "findings"
MKDOCS = ROOT / "mkdocs.yml"

STAGES = ["audit", "critique", "decisions", "repair", "language", "adversarial", "signoff"]
STATUSES = ["pending", "done", "validated", "n/a"]
ICON = {"pending": "⏳", "done": "🟡", "validated": "✅", "n/a": "–"}
ROOT_DOCS = [
    "README.md", "data/README.md", "CLAUDE.md", "mkdocs.yml",
    # Folder READMEs (decision X7 of the 2026-11-15 review)
    "board/README.md", "copilot/README.md", "laptop/README.md", "student_app/README.md",
    "teacher_app/README.md", "classroom/README.md", "explorer/README.md", "tests/README.md",
]

# Review order when /docs-review gets no path: lower comes first.
PRIORITY = {"README.md": 0, "docs/BOARD_SETUP.md": 1, "CLAUDE.md": 2, "mkdocs.yml": 9}


def priority(path: str) -> tuple[int, str]:
    if path in PRIORITY:
        return PRIORITY[path], path
    return (5 if path.startswith("docs/vault/") else 3), path


def in_scope() -> list[str]:
    """Every committed document the review covers, as repo-relative paths.

    MkDocs decides which pages the site has (exclude_docs and its defaults).
    Git, not the disk: an untracked file of another session must not enter the
    committed ledger, or a fresh clone fails `check`.
    """
    config = load_config(str(MKDOCS))
    docs_dir = Path(config.docs_dir).relative_to(ROOT)
    review_dir = PAGE.parent.relative_to(ROOT)  # the review's own files
    site = {
        docs_dir / f.src_uri
        for f in get_files(config)
        if f.src_uri.endswith((".md", ".html"))
    }
    tracked = subprocess.run(
        ["git", "ls-files", "-z", "--", docs_dir.as_posix(), *ROOT_DOCS],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout.split("\0")
    found = [
        p for p in tracked
        if (p in ROOT_DOCS or (Path(p) in site and not Path(p).is_relative_to(review_dir)))
        and (ROOT / p).is_file()  # not deleted in the working tree
    ]
    return sorted(found, key=priority)


@functools.cache
def sha(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def load() -> dict:
    if not LEDGER.exists():
        return {"documents": {}}
    data = yaml.safe_load(LEDGER.read_text()) or {}
    data.setdefault("documents", {})
    return data


def save(data: dict) -> None:
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    header = (
        "# Documentation review ledger. Managed by .claude/skills/docs-review/scripts/docs_status.py\n"
        "# Stages: " + ", ".join(STAGES) + "\n"
        "# Statuses: pending | done (agent finished) | validated (the user approved) | n/a\n"
    )
    body = yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=100)
    LEDGER.write_text(header + body)
    PAGE.write_text(render(data))


def new_entry() -> dict:
    return {"stages": {s: "pending" for s in STAGES}, "validated_sha": None, "notes": {}}


def _entry(data: dict, path: str) -> dict | None:
    entry = data["documents"].get(path)
    if entry is None:
        print(f"not in ledger: {path}", file=sys.stderr)
    return entry


def is_stale(path: str, entry: dict) -> bool:
    return (
        entry["stages"].get("signoff") == "validated"
        and (ROOT / path).exists()
        and entry.get("validated_sha") != sha(path)
    )


def changed_outside(path: str, entry: dict) -> bool:
    """The file changed after the last `set`/`reopen` while a review is open.

    After sign-off this is `stale` instead. Entries written before `last_sha`
    existed have none and never trigger. The caller checks the file exists.
    """
    stages = entry["stages"]
    return (
        any(s != "pending" for s in stages.values())
        and stages.get("signoff") != "validated"
        and entry.get("last_sha") not in (None, sha(path))
    )


def order_error(entry: dict, stage: str, status: str) -> str | None:
    """Why `stage -> status` breaks the stage order, or None."""
    if status not in ("done", "validated"):
        return None
    earlier = STAGES[: STAGES.index(stage)]
    open_ = [s for s in earlier if entry["stages"].get(s, "pending") == "pending"]
    if open_:
        return f"earlier stage {open_[0]} is pending"
    if stage == "signoff" and status == "validated":
        unsigned = [s for s in earlier if entry["stages"].get(s) not in ("validated", "n/a")]
        if unsigned:
            return f"stage {unsigned[0]} is not validated"
    return None


def findings_path(path: str) -> Path:
    # Mirrors the tree: docs/BOARD_SETUP.md -> docs/review/findings/docs/BOARD_SETUP.md.md
    return FINDINGS / (path + ".md")


class _Text(HTMLParser):
    """Visible text of an HTML page: one block per line, <code> as `code`."""

    BLOCK = {"nav", "a", "p", "li", "td", "th", "h1", "h2", "h3", "h4", "summary", "tr",
             "div", "section", "header", "footer", "ol", "ul", "table", "details", "pre"}

    def __init__(self):
        super().__init__()
        self.lines, self.buf, self.skip = [], [], 0

    def flush(self):
        text = " ".join("".join(self.buf).split())
        if text:
            self.lines.append(text)
        self.buf = []

    def _tag(self, tag, step):
        if tag in ("style", "script"):
            self.skip += step
        elif tag == "code":
            self.buf.append("`")
        elif tag in self.BLOCK:
            self.flush()

    def handle_starttag(self, tag, attrs):
        self._tag(tag, 1)

    def handle_endtag(self, tag):
        self._tag(tag, -1)

    def handle_data(self, data):
        if not self.skip:
            self.buf.append(data)


def render(data: dict) -> str:
    docs = data["documents"]
    lines = [
        "# Review status",
        "",
        "Generated by `docs_status.py` from `docs/review/status.yml`. Do not edit by hand.",
        "",
        "This page shows which documents of this site a person on the team has reviewed and approved.",
        "The review has seven stages: audit (facts against the code), critique (readability),",
        "decisions, repair, language, adversarial review and the final sign-off.",
        "",
        "Each document goes through the `/docs-review` stages. ✅ validated by the user,",
        "🟡 done by the agent and waiting for validation, ⏳ pending, – does not apply.",
        "**stale**: the file changed after it was validated, so it needs a new sign-off.",
        "",
        "| Document | " + " | ".join(STAGES) + " |",
        "| --- |" + " :---: |" * len(STAGES),
    ]
    for path in sorted(docs, key=priority):
        entry = docs[path]
        # Site pages link to themselves (the page lives in docs/review/); paths wrap at "/".
        name = f"[{path}](../{path[5:]})" if path.startswith("docs/") else path
        name += " **stale**" if is_stale(path, entry) else ""
        cells = [ICON.get(entry["stages"].get(s, "pending"), "?") for s in STAGES]
        lines.append(f"| {name} | " + " | ".join(cells) + " |")
    total = len(docs)
    signed = sum(1 for e in docs.values() if e["stages"].get("signoff") == "validated")
    lines += ["", f"Signed off: {signed} of {total} documents.", ""]
    return "\n".join(lines)


def problems(data: dict) -> list[str]:
    errors = []
    docs = data["documents"]
    scope = set(in_scope())
    for path in sorted(scope - set(docs)):
        errors.append(f"missing from ledger: {path} (run `sync`)")
    for path in sorted(set(docs) - scope):
        errors.append(f"in ledger but not in scope: {path} (run `sync`)")
    for path, entry in docs.items():
        stages = entry.get("stages", {})
        for stage in STAGES:
            if stages.get(stage) not in STATUSES:
                errors.append(f"{path}: stage {stage} has invalid status {stages.get(stage)!r}")
        for stage in set(stages) - set(STAGES):
            errors.append(f"{path}: unknown stage {stage!r}")
        if path in scope:
            if is_stale(path, entry):
                errors.append(f"stale: {path} changed after sign-off")
            elif changed_outside(path, entry):
                errors.append(
                    f"changed outside the review: {path} (reopen it, or set its stage again"
                    " to accept the change)"
                )
    if not PAGE.exists() or PAGE.read_text() != render(data):
        errors.append("docs/review/index.md is out of date (run `set` or `sync`)")
    return errors


def cmd_check(_args) -> int:
    errors = problems(load())
    for e in errors:
        print(f"FAIL {e}")
    if not errors:
        print("OK ledger matches the docs in scope")
    return 1 if errors else 0


def cmd_table(_args) -> int:
    print(render(load()))
    return 0


def cmd_set(args) -> int:
    data = load()
    entry = _entry(data, args.path)
    if entry is None:
        return 1
    error = order_error(entry, args.stage, args.status)
    if error:
        print(f"refused: {args.path} {args.stage} -> {args.status}: {error}", file=sys.stderr)
        return 1
    entry["stages"][args.stage] = args.status
    if args.note:
        entry.setdefault("notes", {})[args.stage] = args.note
    # Two hashes: last_sha moves with every set; validated_sha stays at the
    # sign-off, so a later set cannot clear `stale`.
    if args.stage == "signoff":
        entry["validated_sha"] = sha(args.path) if args.status == "validated" else None
    entry["last_sha"] = sha(args.path)
    save(data)
    print(f"{args.path}: {args.stage} -> {args.status}")
    return 0


def cmd_reopen(args) -> int:
    data = load()
    entry = _entry(data, args.path)
    if entry is None:
        return 1
    reopened = []
    for stage in STAGES[STAGES.index(args.stage):]:
        if entry["stages"].get(stage) != "n/a":
            entry["stages"][stage] = "pending"
            reopened.append(stage)
    entry["validated_sha"] = None
    entry["last_sha"] = sha(args.path)
    save(data)
    print(f"{args.path}: back to pending: {', '.join(reopened)}")
    return 0


def cmd_findings(args) -> int:
    path = findings_path(args.path)
    path.parent.mkdir(parents=True, exist_ok=True)
    print(path.relative_to(ROOT).as_posix())
    return 0


def cmd_text(args) -> int:
    path = ROOT / args.path
    if path.suffix != ".html":
        print(path.read_text(), end="")
        return 0
    parser = _Text()
    parser.feed(path.read_text())
    parser.flush()
    print("\n".join(parser.lines))
    return 0


def cmd_sync(args) -> int:
    data = load()
    docs = data["documents"]
    scope = in_scope()
    added = [p for p in scope if p not in docs]
    removed = [p for p in docs if p not in scope]
    for p in added:
        print(f"add     {p}")
    for p in removed:
        print(f"remove  {p}")
    if not args.yes:
        print("dry run: pass --yes to write")
        return 0
    for p in added:
        docs[p] = new_entry()
    for p in removed:
        del docs[p]
    data["documents"] = {p: docs[p] for p in sorted(docs, key=priority)}
    save(data)
    print(f"ledger written: {len(docs)} documents")
    return 0


COMMANDS = {
    "check": cmd_check, "table": cmd_table, "set": cmd_set, "reopen": cmd_reopen,
    "findings": cmd_findings, "text": cmd_text, "sync": cmd_sync,
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    parsers = {name: sub.add_parser(name) for name in COMMANDS}
    for name in ("set", "reopen", "findings", "text"):
        parsers[name].add_argument("path")
    for name in ("set", "reopen"):
        parsers[name].add_argument("stage", choices=STAGES)
    parsers["set"].add_argument("status", choices=STATUSES)
    parsers["set"].add_argument("--note")
    parsers["sync"].add_argument("--yes", action="store_true")
    args = parser.parse_args()
    return COMMANDS[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
