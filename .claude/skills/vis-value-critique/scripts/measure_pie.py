#!/usr/bin/env python3
"""Measure a pie/donut chart in an image: slice count, angular spans, order, start angle,
exploded slices. Samples a ring around the pie centre and segments it by colour.

Usage:
    python3 measure_pie.py chart.png [--center X Y] [--radius R] [--ring 0.55]

Without --center/--radius the pie is located as the centroid and equivalent radius of
the chromatic (non-background, non-text) pixels; override them when the image holds
more than the pie (a legend, several pies). Angles are reported clockwise from
12 o'clock, the convention for pies. Compare the segment order with the labels to decide
whether slices run clockwise or counter-clockwise and whether they are sorted.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vischeck.color import to_hex, saturation, value  # noqa: E402

import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402


def load(path):
    im = Image.open(path).convert("RGBA")
    bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
    bg.paste(im, mask=im.split()[-1])
    return np.asarray(bg.convert("RGB")).astype(np.int16)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("image")
    ap.add_argument("--center", nargs=2, type=float)
    ap.add_argument("--radius", type=float)
    ap.add_argument("--ring", type=float, default=0.55,
                    help="sampling radius as a fraction of the pie radius")
    args = ap.parse_args()

    arr = load(args.image)
    h, w, _ = arr.shape
    # background = most common colour
    q = (arr // 8) * 8
    flat = q.reshape(-1, 3)
    vals, counts = np.unique(flat, axis=0, return_counts=True)
    bg = vals[counts.argmax()]
    dist = np.abs(arr - bg).sum(axis=2)
    mask = dist > 60
    # drop near-black (text, edges) from the localisation mask
    dark = arr.sum(axis=2) < 150
    mask &= ~dark
    ys, xs = np.nonzero(mask)
    if len(xs) < 100:
        print(json.dumps({"error": "no chromatic region found"}))
        return
    if args.center:
        cx, cy = args.center
    else:
        cx, cy = float(xs.mean()), float(ys.mean())
    if args.radius:
        r = args.radius
    else:
        r = math.sqrt(len(xs) / math.pi)
    ring = r * args.ring
    n = 3600
    samples = []
    for k in range(n):
        ang = 2 * math.pi * k / n  # clockwise from 12 o'clock
        x = int(round(cx + ring * math.sin(ang)))
        y = int(round(cy - ring * math.cos(ang)))
        if 0 <= x < w and 0 <= y < h:
            samples.append(tuple(int(v) for v in arr[y, x]))
        else:
            samples.append(tuple(int(v) for v in bg))

    def key(c):
        return tuple(v // 24 for v in c)

    # run-length segments, skipping dark edge pixels and background
    segs = []
    for k, c in enumerate(samples):
        is_edge = sum(c) < 150
        is_bg = sum(abs(a - b) for a, b in zip(c, bg)) < 60
        if is_edge:
            continue
        kk = ("bg",) if is_bg else key(c)
        if segs and segs[-1]["key"] == kk:
            segs[-1]["end"] = k
            segs[-1]["n"] += 1
            segs[-1]["sum"] = [s + v for s, v in zip(segs[-1]["sum"], c)]
        else:
            segs.append({"key": kk, "start": k, "end": k, "n": 1, "sum": list(c)})
    # merge wrap-around
    if len(segs) > 1 and segs[0]["key"] == segs[-1]["key"]:
        segs[-1]["end"] = segs[0]["end"] + n
        segs[-1]["n"] += segs[0]["n"]
        segs[-1]["sum"] = [s + v for s, v in zip(segs[-1]["sum"], segs[0]["sum"])]
        segs.pop(0)
    # drop slivers (< 2°): anti-aliasing, outlines, shadows of exploded slices
    segs = [s for s in segs if s["n"] >= n * 2 / 360]
    total = sum(s["n"] for s in segs if s["key"] != ("bg",))
    out = []
    for s in segs:
        if s["key"] == ("bg",):
            continue
        mean = tuple(v / s["n"] / 255 for v in s["sum"])
        start_deg = (s["start"] % n) * 360 / n
        span_deg = s["n"] * 360 / n
        # exploded? sample near the centre within this span
        mid = (s["start"] + s["n"] / 2) % n
        ang = 2 * math.pi * mid / n
        x = int(round(cx + 0.12 * r * math.sin(ang)))
        y = int(round(cy - 0.12 * r * math.cos(ang)))
        inner = tuple(int(v) for v in arr[y, x]) if 0 <= x < w and 0 <= y < h else tuple(bg)
        exploded = sum(abs(a - b) for a, b in zip(inner, bg)) < 60
        out.append({"hex": to_hex(mean), "start_deg_cw_from_12": round(start_deg, 1),
                    "span_deg": round(span_deg, 1),
                    "share_pct": round(100 * s["n"] / total, 1) if total else None,
                    "exploded_guess": bool(exploded),
                    "neutral": saturation(mean) < 0.15 or value(mean) < 0.2})
    out.sort(key=lambda s: s["start_deg_cw_from_12"])
    spans = [s["span_deg"] for s in out]
    cw_desc = ccw_desc = False
    if spans:
        i0 = spans.index(max(spans))
        cw = spans[i0:] + spans[:i0]
        ccw = [spans[i0]] + list(reversed(spans[:i0])) + list(reversed(spans[i0 + 1:]))
        cw_desc = cw == sorted(cw, reverse=True)
        ccw_desc = ccw == sorted(ccw, reverse=True)
    res = {
        "center_px": [round(cx, 1), round(cy, 1)], "radius_px": round(r, 1),
        "ring_px": round(ring, 1), "n_slices": len(out), "slices": out,
        "sorted_clockwise_desc": cw_desc,
        "sorted_counterclockwise_desc": ccw_desc,
        "first_slice_starts_at_12": bool(out) and (out[0]["start_deg_cw_from_12"] < 2 or
                                                     out[0]["start_deg_cw_from_12"] > 358),
        "min_span_deg": min(spans) if spans else None,
        "note": ("Compare slice colours with the labels to map segments to categories. "
                 "If the pie has a thick outline or a donut hole adjust --ring. "
                 "IDM-PIE fires above 5 slices; CMP-01 if not sorted large→small "
                 "clockwise from 12."),
    }
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
