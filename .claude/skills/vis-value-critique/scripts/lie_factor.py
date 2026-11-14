#!/usr/bin/env python3
"""Tufte's lie factor from measured visual magnitudes and the data they encode.

    lie factor = (size of effect shown in the graphic) / (size of effect in the data)
    size of effect = |v2 - v1| / |v1|

Measure the visual magnitude in the same way the chart encodes it (bar length in px,
circle AREA in px², icon area, slice angle). Pairs are compared first-to-last and
consecutively. Acceptable range: 0.95–1.05.

    python3 lie_factor.py --data 18 27.5 --visual 0.6 5.3
    python3 lie_factor.py --data 100 200 --visual-radius 10 20   # circles scaled by radius
"""
import argparse
import json
import math


def effect(a, b):
    if a == 0:
        return math.inf if b != 0 else 0.0
    return abs(b - a) / abs(a)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", nargs="+", type=float, required=True)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--visual", nargs="+", type=float,
                   help="measured visual magnitudes (length, area, angle)")
    g.add_argument("--visual-radius", nargs="+", type=float,
                   help="measured radii; area = pi r^2 is used as the visual magnitude")
    args = ap.parse_args()
    vis = args.visual if args.visual else [math.pi * r * r for r in args.visual_radius]
    if len(vis) != len(args.data):
        raise SystemExit("data and visual lists must have the same length")
    out = {"pairs": [], "verdict": ""}
    pairs = [(0, len(vis) - 1)] + [(i, i + 1) for i in range(len(vis) - 1)]
    pairs = list(dict.fromkeys(pairs))
    worst = 1.0
    for i, j in pairs:
        if i == j:
            continue
        ed, ev = effect(args.data[i], args.data[j]), effect(vis[i], vis[j])
        lf = ev / ed if ed not in (0, math.inf) else (math.inf if ev else 1.0)
        worst = max(worst, lf, 1 / lf if lf else math.inf)
        out["pairs"].append({"i": i, "j": j, "data_effect": round(ed, 4),
                             "visual_effect": round(ev, 4), "lie_factor": round(lf, 3)})
    out["worst_lie_factor"] = round(worst, 3)
    if worst <= 1.05:
        out["verdict"] = "geometry proportional to data (lie factor within 0.95–1.05)"
        out["rule"] = None
    else:
        out["verdict"] = ("geometry distorts the data: EXP-07 crit "
                          "(lie factor outside 0.95–1.05)")
        out["rule"] = "EXP-07"
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
