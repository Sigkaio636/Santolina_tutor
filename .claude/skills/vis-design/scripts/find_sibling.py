#!/usr/bin/env python3
"""Locate the optional sibling skill vis-value-critique. Prints its path or "absent".

Search order: $CLAUDE_SKILLS_DIR, the folder that holds this skill, ~/.claude/skills.
"""
import os
import sys


def find() -> str | None:
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cands = []
    if os.environ.get("CLAUDE_SKILLS_DIR"):
        cands.append(os.path.join(os.environ["CLAUDE_SKILLS_DIR"], "vis-value-critique"))
    cands.append(os.path.join(os.path.dirname(here), "vis-value-critique"))
    cands.append(os.path.expanduser("~/.claude/skills/vis-value-critique"))
    for c in cands:
        if os.path.exists(os.path.join(c, "SKILL.md")) and os.path.isdir(os.path.join(c, "scripts")):
            return c
    return None


if __name__ == "__main__":
    p = find()
    print(p or "absent")
    sys.exit(0 if p else 1)
