"""Similarity between a query (answers.json) and stored decisions."""
from __future__ import annotations

from .shape import shape_similarity, canonicalize

INCOMPATIBLE = [
    # (query constraint, predicate on record.solution) -> incompatible
    ("static-only", lambda s: (s.get("interaction", {}) or {}).get("level") == "required"),
    ("print-grayscale", lambda s: (s.get("color", {}) or {}).get("purpose") == "distinguish"
                                 and not (s.get("color", {}) or {}).get("second_cue")),
    ("exact-values", lambda s: s.get("family") in ("pie", "treemap", "proportional-area", "radial", "text")),
    ("no-geometry-file", lambda s: s.get("family", "").startswith("map-")),
    ("few-categories-only", lambda s: s.get("family") in ("heatmap", "parallel", "network")),
]


def jaccard(a, b) -> float:
    a, b = set(a or []), set(b or [])
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)


def incompatible(q: dict, rec: dict) -> str | None:
    s = rec.get("solution", {}) or {}
    for c, pred in INCOMPATIBLE:
        if c in (q.get("constraints") or []) and pred(s):
            return c
    return None


def score(q: dict, rec: dict, archetypes: dict, profiles: dict) -> tuple[float, dict]:
    qp, rp = q.get("problem", {}), rec.get("problem", {})
    qa, ra = qp.get("archetype"), rp.get("archetype")
    related = set((archetypes.get(qa) or {}).get("related_archetypes", []))
    s_arch = 1.0 if qa == ra else (0.6 if ra in related else 0.0)
    s_shape, diffs = shape_similarity(q.get("data", {}), rec.get("data", {}))
    qt, rt = q.get("tasks", {}) or {}, rec.get("tasks", {}) or {}
    s_tasks = 0.6 * jaccard(qt.get("low_level"), rt.get("low_level"))
    s_tasks += 0.2 * (1.0 if (qt.get("why") or {}).get("query") == (rt.get("why") or {}).get("query") else 0.0)
    has_temporal = any(k.get("type") == "temporal" for k in canonicalize(q.get("data", {}))["keys"])
    if has_temporal or qt.get("temporal") or rt.get("temporal"):
        s_tasks += 0.2 * jaccard(qt.get("temporal"), rt.get("temporal"))
    else:
        s_tasks += 0.2
    qu, ru = (q.get("user") or {}).get("profile"), (rec.get("user") or {}).get("profile")
    if qu == ru:
        s_user = 1.0
    else:
        lq = (profiles.get(qu) or {}).get("capabilities", {}).get("vis_literacy")
        lr = (profiles.get(ru) or {}).get("capabilities", {}).get("vis_literacy")
        s_user = 0.6 if lq and lq == lr else 0.3
    qm, rm = qp.get("mode"), rp.get("mode")
    s_mode = 1.0 if qm == rm else (0.5 if {qm, rm} <= {"analysis", "exploration"} else 0.2)
    total = 0.30 * s_arch + 0.30 * s_shape + 0.20 * s_tasks + 0.10 * s_user + 0.10 * s_mode
    pr = rec.get("provenance", {}) or {}
    bonus = 0.0
    if pr.get("origin") == "project":
        bonus += 0.03
    if rec.get("status") == "declared":
        bonus += 0.02
    if rec.get("confidence") == "low":
        bonus -= 0.10
    bonus += 0.01 * min(int(pr.get("times_used") or 0), 5) / 5
    total = round(min(1.0, total + bonus), 3)
    breakdown = {"archetype": s_arch, "shape": s_shape, "tasks": round(s_tasks, 3), "user": s_user,
                 "mode": s_mode, "bonus": round(bonus, 3), "shape_diffs": diffs}
    if qa != ra:
        breakdown["differs"] = breakdown.get("differs", []) + [f"archetype {ra}"]
    if qu != ru:
        breakdown["differs"] = breakdown.get("differs", []) + [f"profile {ru}"]
    if qm != rm:
        breakdown["differs"] = breakdown.get("differs", []) + [f"mode {rm}"]
    if diffs:
        breakdown["differs"] = breakdown.get("differs", []) + diffs
    return total, breakdown


def tier(total: float) -> str:
    if total >= 0.80:
        return "REUSE"
    if total >= 0.55:
        return "ADAPT"
    return "NONE"
