"""Palette checks. Uses the sibling vis-value-critique's vischeck when installed,
otherwise the vendored copy in vendor/."""
from __future__ import annotations

import importlib.util
import os
import sys


def _load_sibling():
    here = os.path.dirname(os.path.abspath(__file__))
    skills_dir = os.path.abspath(os.path.join(here, "..", "..", ".."))
    candidates = [os.path.join(skills_dir, "vis-value-critique", "scripts"),
                  os.path.expanduser("~/.claude/skills/vis-value-critique/scripts")]
    env = os.environ.get("CLAUDE_SKILLS_DIR")
    if env:
        candidates.insert(0, os.path.join(env, "vis-value-critique", "scripts"))
    for c in candidates:
        if os.path.isdir(os.path.join(c, "vischeck")):
            if c not in sys.path:
                sys.path.insert(0, c)
            try:
                from vischeck import color, palettes  # type: ignore
                return color, palettes, c
            except Exception:
                continue
    return None


_sib = _load_sibling()
if _sib:
    color, palettes, SOURCE = _sib
else:
    from .vendor import color, palettes  # type: ignore
    SOURCE = "vendored"

OKABE_ITO = ["#e69f00", "#56b4e9", "#009e73", "#f0e442", "#0072b2", "#d55e00", "#cc79a7", "#000000"]
NEUTRAL = "#8c8c8c"
ACCENT = "#0072b2"
SEQUENTIAL = {"altair": "viridis", "matplotlib": "viridis", "plotly": "Viridis"}
DIVERGING = {"altair": "blueorange", "matplotlib": "RdBu", "plotly": "RdBu"}


def check_palette(hex_colors: list[str]) -> dict:
    cols = [color.parse_color(c) for c in hex_colors]
    cols = [c for c in cols if c]
    rep = color.palette_report(cols) if len(cols) >= 2 else {"n": len(cols), "hex": hex_colors}
    rep["source"] = SOURCE
    rep["ok_for_cvd"] = not rep.get("has_red_and_green") and not rep.get("confusable_deuteranopia")
    return rep


def suggest(palette_type: str, n: int, library: str) -> dict:
    if palette_type == "neutral-accent":
        return {"neutral": NEUTRAL, "accent": ACCENT}
    if palette_type == "qualitative":
        return {"colors": OKABE_ITO[:max(2, min(n, 8))], "name": "okabe-ito"}
    if palette_type == "sequential":
        return {"scheme": SEQUENTIAL.get(library, "viridis")}
    if palette_type == "diverging":
        return {"scheme": DIVERGING.get(library, "RdBu"), "note": "set the midpoint to the reference value"}
    return {}
