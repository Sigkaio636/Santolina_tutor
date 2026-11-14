#!/usr/bin/env python3
"""Red line: M3Kang data never enters Git -- not the index, a commit, the
history, a push or a pull request.

M3Kang (huggingface.co/datasets/qualcomm/M3Kang) is licensed for research use
only. Nothing derived from its problems may be committed: train/val JSONL,
problem images, the OCR cache, the RAG index (*.db), parquet shards.

Two modes, one rule set (FORBIDDEN / ALLOWED below):

  Hook mode (default). A Claude Code PreToolUse hook on Bash. Reads the tool
  call as JSON on stdin. When the command stages, commits, pushes or opens a
  PR, it lists every file that would land in Git and exits 2 (block, reason
  on stderr) if any is M3Kang data. Every other command passes with exit 0.

  CI mode:  m3kang-guard.py --range <base> <head>
  Checks every file touched by any commit in base..head, and the tree at
  head. An empty or all-zero base checks the whole history of head. Exit 1 on a hit. Used by .github/workflows/m3kang-guard.yml so a PR
  opened from the website or by hand is checked too.

Python standard library only.
"""
import json
import os
import re
import shlex
import subprocess
import sys

# A path is M3Kang data if it matches FORBIDDEN and not ALLOWED.
FORBIDDEN = [
    (re.compile(r"^data(/|$)"), "everything under data/ is M3Kang or derived from it"),
    (re.compile(r"\.(jsonl|parquet|db|sqlite3?)$", re.I), "problem sets, shards and the RAG index"),
    (re.compile(r"(^|/)\.?ocr_cache", re.I), "OCR output of M3Kang images"),
    (re.compile(r"(^|/)(train|val|test)\.(json|csv|tsv)$", re.I), "train/val/test splits"),
]
ALLOWED = [
    re.compile(r"^data/sample_problems\.jsonl$"),  # 5 hand-written samples
    re.compile(r"^data/README\.md$"),
    re.compile(r"(^|/)\.gitkeep$"),
]

SEPARATORS = re.compile(r"&&|\|\||;|\||\n")
GIT_OPTS_WITH_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace"}


def reason_for(path):
    path = path.strip().strip('"')
    if not path or any(a.search(path) for a in ALLOWED):
        return None
    for pattern, why in FORBIDDEN:
        if pattern.search(path):
            return why
    return None


def git(top, *args):
    out = subprocess.run(["git", "-C", top, *args], capture_output=True, text=True)
    if out.returncode != 0:
        return []
    return [line for line in out.stdout.splitlines() if line.strip()]


def history_files(top, *rev_args):
    return git(top, "log", "--name-only", "--format=", *rev_args)


def segments(command):
    for raw in SEPARATORS.split(command):
        try:
            tokens = shlex.split(raw, comments=True)
        except ValueError:
            tokens = raw.split()
        while tokens and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", tokens[0]):
            tokens = tokens[1:]  # VAR=value prefixes
        if tokens:
            yield tokens


def git_subcommand(tokens):
    """['git', '-C', 'x', 'commit', '-a'] -> ('x' or None, 'commit', ['-a'])."""
    where, i = None, 1
    while i < len(tokens) and tokens[i].startswith("-"):
        if tokens[i] in GIT_OPTS_WITH_VALUE and i + 1 < len(tokens):
            if tokens[i] == "-C":
                where = tokens[i + 1]
            i += 2
        else:
            i += 1
    if i >= len(tokens):
        return where, None, []
    return where, tokens[i], tokens[i + 1:]


def default_base(top):
    for ref in git(top, "symbolic-ref", "-q", "--short", "refs/remotes/origin/HEAD") + ["origin/main", "origin/master"]:
        if git(top, "rev-parse", "-q", "--verify", ref + "^{commit}"):
            return ref
    return None


def to_top(top, here, path):
    """A path as typed in `here` -> a path relative to the repository top."""
    full = path if os.path.isabs(path) else os.path.join(here, path)
    return os.path.relpath(os.path.normpath(full), top)


def short_flags(args, letter, value_letters="mFCcten"):
    """True if a short-option cluster such as -am sets `letter` before a value."""
    for a in args:
        if a == "--":
            break
        if a.startswith("-") and not a.startswith("--"):
            for ch in a[1:]:
                if ch == letter:
                    return True
                if ch in value_letters:
                    break
    return False


def candidates_for(top, here, sub, args, gh_pr=False):
    """Every path, relative to top, that this git/gh call would put into Git."""
    if gh_pr:
        base = default_base(top)
        files = history_files(top, f"{base}..HEAD") if base else []
        return files + history_files(top, "HEAD", "--not", "--remotes")
    if sub in ("push", "send-pack"):
        # Every commit the remote doesn't have yet, on any local branch or tag.
        return history_files(top, "--branches", "--tags", "--not", "--remotes")

    if "--" in args:
        paths = args[args.index("--") + 1:]
    else:
        paths = [a for a in args if not a.startswith("-")]
    files = []
    if sub == "add":
        paths = [to_top(top, here, p) for p in paths]
        files += paths  # judged by name, even if the file doesn't exist yet
        listing = ["ls-files", "--full-name", "--others", "--modified"]
        if not (short_flags(args, "f") or "--force" in args):
            listing.append("--exclude-standard")
        if paths or short_flags(args, "A") or short_flags(args, "u") or "--all" in args or "--update" in args:
            files += git(top, *listing, "--", *(paths or ["."]))
    elif sub == "commit":
        files += git(top, "diff", "--cached", "--name-only")
        if short_flags(args, "a") or "--all" in args:
            files += git(top, "diff", "--name-only")
        if "--" in args:
            files += [to_top(top, here, p) for p in paths]
    return files


def block(top, hits, what):
    lines = "\n".join(f"  - {p}  ({why})" for p, why in sorted(hits.items())[:20])
    more = f"\n  ... and {len(hits) - 20} more" if len(hits) > 20 else ""
    sys.stderr.write(
        f"m3kang-guard: RED LINE. `{what}` would put M3Kang data into Git in "
        f"{os.path.basename(top)}:\n{lines}{more}\n"
        "M3Kang is licensed for research use only: it must never be staged, "
        "committed, pushed or sent in a PR, and must not appear anywhere in the "
        "history. Do not work around this check (no -f, no renames, no other "
        "path, no --no-verify). Unstage with `git restore --staged <path>`; if "
        "the file is already in a commit, stop and tell the user: the history "
        "must be rewritten before any push.\n"
    )
    sys.exit(2)


def hook():
    try:
        call = json.load(sys.stdin)
    except (ValueError, OSError):
        sys.exit(0)
    command = (call.get("tool_input") or {}).get("command") or ""
    cwd = call.get("cwd") or os.getcwd()
    if "git" not in command and "gh" not in command:
        sys.exit(0)

    for tokens in segments(command):
        if tokens[0] == "cd" and len(tokens) > 1:
            cwd = os.path.join(cwd, os.path.expanduser(tokens[1]))
            continue
        gh_pr = tokens[:2] == ["gh", "pr"] and len(tokens) > 2 and tokens[2] in ("create", "new", "ready", "merge")
        if gh_pr:
            if any(t in ("--repo", "-R") or t.startswith("--repo=") for t in tokens):
                continue  # another repository: the local tree says nothing about it
            where, sub, args = None, None, []
        elif tokens[0] == "git":
            where, sub, args = git_subcommand(tokens)
            if sub not in ("add", "commit", "push", "send-pack"):
                continue
        else:
            continue
        here = os.path.join(cwd, where) if where else cwd
        top_lines = git(here, "rev-parse", "--show-toplevel") if os.path.isdir(here) else []
        if not top_lines:
            continue
        top = top_lines[0]
        hits = {}
        for path in candidates_for(top, here, sub, args, gh_pr=gh_pr):
            why = reason_for(path)
            if why:
                hits[path] = why
        if hits:
            block(top, hits, " ".join(tokens[:3]) if gh_pr else f"git {sub}")
    sys.exit(0)


def ci(base, head):
    top = git(".", "rev-parse", "--show-toplevel")[0]
    # An empty or all-zero base (a new branch pushed to CI): the whole history.
    rng = head if not base.strip("0") else f"{base}..{head}"
    files = history_files(top, rng) + git(top, "ls-tree", "-r", "--name-only", head)
    hits = {p: reason_for(p) for p in set(files) if reason_for(p)}
    if hits:
        print(f"m3kang-guard: RED LINE. M3Kang data in the commits {rng} or in the tree at {head[:9]}:")
        for p, why in sorted(hits.items()):
            print(f"  - {p}  ({why})")
        print("Remove it and rewrite the branch history before this can merge.")
        sys.exit(1)
    print(f"m3kang-guard: clean ({len(set(files))} paths checked)")


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "--range":
        ci(sys.argv[2], sys.argv[3])
    else:
        hook()
