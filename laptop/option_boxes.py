"""Find the boxes of the five answer options (A-E) in an M3Kang image with OpenCV only.

Experiment: docs/experiments/2026-11-option-boxes-intermediate-rec.md

Arms:
  B0  the detector of notebooks/option_crops_opencv.ipynb, unchanged (closing 41x3 + repair)
  B1  anchored on the labels: the templates "A)".."E)" are matched at 21 scales, the best
      A..E sequence in reading order wins, and every ink component goes to one option
      (same line, over or under a fraction bar, or a line that continues below).
      detect_b1 falls back to B0 when it finds no labels; option_rec.read_row does not.

Commands (run from the repo root, e.g. `.venv/bin/python -I laptop/option_boxes.py pick`):
  pick       draw the quick sample (gold / dev / hard)  -> data/interim/optrec/sample.json
             needs: options_gold3.json and the v4 and v5 box files of ocr_boxes.py
  templates  build the label templates "A)".."E)"       -> data/interim/optrec/label_templates.npz
             needs: sample.json (its rows are left out) and the v5 box file
  detect     write the boxes of one arm  -> data/interim/optrec/boxes_<arm>_<scope>.jsonl
  score      compare the arms with the PP-OCRv5 reference boxes (after detect)
  sheets     draw the boxes on the images, for review by eye -> data/interim/optrec/sheets/<name>/

Input: the eng/cat/esp rows of data/raw_txto_yes/*.parquet. Usage guide:
docs/OPTION_READER_GUIDE.md. Everything it writes stays under data/interim/ (M3Kang
data, never in Git).
"""
import argparse
import glob
import json
import os
import random
import re
import sys
from collections import Counter, defaultdict

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from prepare_m3kang import LETTERS, is_marker, parse_options, reading_order  # noqa: E402

LANGS = ("eng", "cat", "esp")
PARQUETS = "data/raw_txto_yes/*.parquet"
OUT = "data/interim/optrec"
SAMPLE = f"{OUT}/sample.json"
GOLD3 = "data/interim/optx/options_gold3.json"
V5 = "data/interim/ocr_boxes_txto_yes_v5.jsonl"
V4 = "data/interim/ocr_boxes_txto_yes.jsonl"
TWO_NUMBERS = re.compile(r"^\s*\d+\s+\d+\s*$")
cv2.setNumThreads(1)  # small images: OpenCV threads only add cost


# --- Data -------------------------------------------------------------------

def load_rows(keys=None, images=True):
    """key 'id|lang' -> {lang, level, image bytes} for the eng/cat/esp text-only rows."""
    import pyarrow.parquet as pq
    rows = {}
    for path in sorted(glob.glob(PARQUETS)):
        t = pq.read_table(path, columns=["id", "language", "level"])
        ids, langs, levels = (t.column(c).to_pylist() for c in ("id", "language", "level"))
        keep = [i for i, (pid, lang) in enumerate(zip(ids, langs))
                if lang in LANGS and (keys is None or f"{pid}|{lang}" in keys)]
        if not keep:
            continue
        imgs = pq.read_table(path, columns=["image"]).take(keep).column("image").to_pylist() if images else None
        for n, i in enumerate(keep):
            rows[f"{ids[i]}|{langs[i]}"] = {"lang": langs[i], "level": levels[i],
                                            "image": imgs[n]["bytes"] if images else None}
    return rows


def load_boxes(path):
    return {r["key"]: r["boxes"] for r in map(json.loads, open(path))}


def gray(image):
    return cv2.imdecode(np.frombuffer(image, np.uint8), cv2.IMREAD_GRAYSCALE)


def sample_keys(strata=None):
    s = json.load(open(SAMPLE))
    return [k for name, keys in s["strata"].items() if strata is None or name in strata for k in keys]


# --- Geometry ---------------------------------------------------------------

def otsu(g):
    t, m = cv2.threshold(g, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return t, m


def ink_mask(g):
    """Ink mask with a threshold halfway between Otsu's and white. Thin strokes are
    anti-aliased to about Otsu's level (the stem of a "5" is 130-150 on a 255
    background), so Otsu alone breaks glyphs into pieces."""
    t, _m = otsu(g)
    return ((g < (t + 255) / 2) * 255).astype(np.uint8)


def union(rects):
    return (min(r[0] for r in rects), min(r[1] for r in rects), max(r[2] for r in rects), max(r[3] for r in rects))


def tighten(mask, r):
    """Shrink a box to the ink inside it."""
    x0, y0, x1, y1 = (int(round(v)) for v in r)
    H, W = mask.shape
    x0, y0, x1, y1 = max(0, x0), max(0, y0), min(W, x1 + 1), min(H, y1 + 1)
    ys, xs = np.nonzero(mask[y0:y1, x0:x1])
    if not len(xs):
        return (x0, y0, x1 - 1, y1 - 1)
    return (int(x0 + xs.min()), int(y0 + ys.min()), int(x0 + xs.max()), int(y0 + ys.max()))


def components(mask, min_area=4):
    _n, _lab, stats, _c = cv2.connectedComponentsWithStats(mask, connectivity=8)
    return [(int(x), int(y), int(x + w - 1), int(y + h - 1)) for x, y, w, h, a in stats[1:] if a >= min_area]


def runs(flags):
    """[(start, end)] of the True runs of a boolean vector."""
    f = np.concatenate(([False], np.asarray(flags, bool), [False]))
    d = np.flatnonzero(f[1:] != f[:-1])
    return [(int(a), int(b) - 1) for a, b in zip(d[::2], d[1::2])]


def text_lines(mask, min_h=6):
    """Horizontal ink bands (row projection): [(y0, y1), ...]."""
    return [(a, b) for a, b in runs(mask.any(axis=1)) if b - a + 1 >= min_h]


# --- B0: the notebook detector, unchanged -----------------------------------

def pick_five(mask, boxes, repair=True):
    """The boxes of the last text line, left to right (or of the last lines, for a grid or
    a vertical list). With repair: join the nearest neighbours while there are more than
    five; split the widest box at its widest empty column while there are fewer."""
    lines = text_lines(mask)
    if not lines:
        return None
    W = mask.shape[1]

    def in_line(y0, y1):
        return sorted(b for b in boxes if y0 <= (b[1] + b[3]) / 2 <= y1)

    line = in_line(*lines[-1])
    if len(line) < 5:
        acc = list(line)
        for y0, y1 in reversed(lines[:-1]):
            above = in_line(y0, y1)
            if not above or any(b[2] - b[0] > W / 2 for b in above):
                break
            acc = above + acc
            if len(acc) >= 5:
                break
        if len(acc) == 5:
            return acc
    if not repair:
        return line if len(line) == 5 else None
    while len(line) > 5:
        gaps = [line[i + 1][0] - line[i][2] for i in range(len(line) - 1)]
        i = int(np.argmin(gaps))
        line[i:i + 2] = [union(line[i:i + 2])]
    while 0 < len(line) < 5:
        j = max(range(len(line)), key=lambda i: line[i][2] - line[i][0])
        x0, by0, x1, by1 = line[j]
        gaps = [(b - a + 1, a, b) for a, b in runs(~mask[by0:by1 + 1, x0:x1 + 1].any(axis=0))]
        if not gaps:
            return None
        _w, a, b = max(gaps)
        left, right = (x0, by0, x0 + a - 1, by1), (x0 + b + 1, by0, x1, by1)
        line[j:j + 1] = [tighten(mask, left), tighten(mask, right)]
    return line if len(line) == 5 else None


def detect_b0(g, kw=41, kh=3):
    _t, m = otsu(g)
    closed = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (kw, kh)))
    five = pick_five(closed, components(closed))
    return {"boxes": [list(map(int, b)) for b in five] if five else None, "why": "" if five else "no_five"}


# --- B1: anchored on the labels "A)".."E)" ------------------------------------
#
# The labels are typeset in one font and one size, so a template of each finds them
# (cv2.matchTemplate). Every ink component is then given to one label:
#   - on the label's line: to the nearest label on its left;
#   - above or below the line, over or under a fraction bar: to the option of that bar;
#   - on later lines (an option that continues on a second line): to the option whose
#     first line is nearest in x.
# That covers what B0 misses: options closer than its 41 px kernel, options on two
# lines, and a stacked fraction that splits the text line. B0 is the fallback.

TEMPLATES = f"{OUT}/label_templates.npz"
MATCH = 0.70       # minimum template score for a label
TPL_H = 40         # height of the stored templates; they are only ever scaled down
SCALES = [round(0.50 + 0.025 * i, 3) for i in range(21)]   # label heights 20..40 px
_tpl = {}


def templates():
    if not _tpl:
        z = np.load(TEMPLATES)
        _tpl.update({L: z[L] for L in LETTERS})
    return _tpl


def label_rect(m, box):
    """The label inside a reference box: its first component (the letter) and the
    parenthesis after it. None when they are joined or do not look like a label."""
    x0, y0, x1, y1 = box
    cs = sorted((c[0] + x0, c[1] + y0, c[2] + x0, c[3] + y0) for c in components(m[y0:y1 + 1, x0:x1 + 1]))
    if len(cs) < 2:
        return None
    a, b = cs[0], cs[1]
    ha, wb, hb = a[3] - a[1] + 1, b[2] - b[0] + 1, b[3] - b[1] + 1
    if hb < ha or wb > 0.6 * hb or b[0] - a[2] > 0.5 * ha:
        return None
    return union([a, b])


def find_labels(g, tpl=None):
    """Best A..E label sequence: [(x0, y0, x1, y1, score)] x 5, or None.

    The label size changes from image to image, so the templates (height TPL_H) are
    tried at several scales; the scale with the best sum of the five scores wins."""
    tpl = tpl or templates()

    def match(img, s, f=1.0):
        maps, total = {}, 0.0
        for L in LETTERS:
            t = cv2.resize(tpl[L], None, fx=s * f, fy=s * f, interpolation=cv2.INTER_AREA)
            if img.shape[0] < t.shape[0] or img.shape[1] < t.shape[1]:
                return None
            r = cv2.matchTemplate(img, t, cv2.TM_CCOEFF_NORMED)
            r[~np.isfinite(r)] = 0
            maps[L] = (r, t.shape)
            total += float(r.max())
        return total, maps

    # Coarse: every scale on the half-size image. Fine: the best three at full size.
    half = cv2.resize(g, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
    coarse = sorted(((m[0], s) for s in SCALES if (m := match(half, s, 0.5))), reverse=True)
    fine = [m for _score, s in coarse[:3] if (m := match(g, s))]
    best = max(fine, key=lambda m: m[0]) if fine else None
    if best is None:
        return None
    cands = []
    for L, (r, shape) in best[1].items():
        for _ in range(6):  # a few peaks per letter
            _mn, mx, _l, (x, y) = cv2.minMaxLoc(r)
            if mx < MATCH:
                break
            cands.append((L, x, y, x + shape[1] - 1, y + shape[0] - 1, float(mx)))
            r[max(0, y - shape[0]):y + shape[0], max(0, x - shape[1]):x + shape[1]] = 0
    if not cands:
        return None
    th = max(c[4] - c[2] + 1 for c in cands)
    # Reading order: lines of labels by y, then x.
    cands.sort(key=lambda c: c[2])
    line, last = 0, cands[0][2]
    ordered = []
    for c in cands:
        if c[2] - last > 0.6 * th:
            line += 1
        last = c[2]
        ordered.append((line, c[1], c))
    ordered.sort(key=lambda o: (o[0], o[1]))
    seq = [o[2] for o in ordered]
    # Every A followed, in order, by B, C, D and E (the best-scoring one of each); the
    # chain with the best total wins, so a value that is itself a letter ("A) A") loses
    # to the real label, which has its parenthesis.
    chains = []
    for i in [i for i, c in enumerate(seq) if c[0] == "A"]:
        chain, pos = [seq[i]], i
        for L in LETTERS[1:]:
            nxt = [(c[5], j) for j, c in enumerate(seq) if j > pos and c[0] == L]
            if not nxt:
                break
            pos = max(nxt)[1]
            chain.append(seq[pos])
        if len(chain) == 5:
            chains.append((sum(c[5] for c in chain), i, chain))
    return [c[1:] for c in max(chains)[2]] if chains else None


def is_bar(c, h):
    w, hh = c[2] - c[0] + 1, c[3] - c[1] + 1
    return w >= 0.45 * h and hh <= max(3, 0.14 * h) and w >= 4 * hh


def assign(g, tpl=None):
    """Labels and the ink components of each option: (labels, comps, owner, mask, h),
    where owner maps a component index to an option index 0..4. None without labels."""
    labels = find_labels(g, tpl)
    if labels is None:
        return None
    m = ink_mask(g)
    comps = components(m)
    h = float(np.median([b[3] - b[1] + 1 for b in labels]))  # label height
    # Lines of labels.
    lines = []
    for i, b in enumerate(labels):
        if lines and abs(b[1] - labels[lines[-1][-1]][1]) <= 0.6 * h:
            lines[-1].append(i)
        else:
            lines.append([i])
    band = [(min(labels[i][1] for i in ln), max(labels[i][3] for i in ln)) for ln in lines]
    owner = {}
    # 1. Components on a label line go to the nearest label on their left.
    for ci, c in enumerate(comps):
        cy, cx = (c[1] + c[3]) / 2, (c[0] + c[2]) / 2
        for ln, (y0, y1) in zip(lines, band):
            if y0 - 0.1 * h <= cy <= y1 + 0.1 * h and c[3] - c[1] + 1 <= 2.2 * h:
                left = [i for i in ln if labels[i][0] - 2 <= cx]
                if left:
                    owner[ci] = max(left, key=lambda i: labels[i][0])
                break
    on_line = set(owner)
    # 2. Numerators and denominators: over or under a bar that is on a line.
    bars = [(ci, o) for ci, o in owner.items() if is_bar(comps[ci], h)]
    for ci, c in enumerate(comps):
        if ci in owner:
            continue
        for bi, o in bars:
            b = comps[bi]
            gap = b[1] - c[3] if c[3] < b[1] else c[1] - b[3]   # numerator or denominator
            if -1 <= gap <= 0.45 * h and c[0] >= b[0] - 3 and c[2] <= b[2] + 3:
                owner[ci] = o
                break
    #    A thin stroke can break a glyph in two (the top of a "5"): a piece that touches
    #    a numerator or denominator belongs with it.
    frac = {ci for ci in owner if ci not in on_line}
    grown = True
    while grown:
        grown = False
        for ci, c in enumerate(comps):
            if ci in owner:
                continue
            for fi in frac:
                f = comps[fi]
                if c[0] <= f[2] + 2 and c[2] >= f[0] - 2 and c[1] <= f[3] + 0.2 * h and c[3] >= f[1] - 0.2 * h:
                    owner[ci] = owner[fi]
                    frac.add(ci)
                    grown = True
                    break
    # 3. What is left below a label line continues an option of that line.
    extent = {}
    for ci, o in owner.items():
        c = comps[ci]
        e = extent.get(o)
        extent[o] = (min(e[0], c[0]), max(e[1], c[2])) if e else (c[0], c[2])
    for i, b in enumerate(labels):
        extent.setdefault(i, (b[0], b[2]))
    for ci, c in enumerate(comps):
        if ci in owner:
            continue
        cy, cx = (c[1] + c[3]) / 2, (c[0] + c[2]) / 2
        above = [n for n, (y0, y1) in enumerate(band) if cy > y1]
        if not above:
            continue  # the question, over the first label line
        n = above[-1]
        if cy - band[n][1] > 4.0 * h:
            continue
        dist = {i: max(extent[i][0] - cx, cx - extent[i][1], 0) for i in lines[n]}
        o = min(dist, key=dist.get)
        if dist[o] <= 3.0 * h:
            owner[ci] = o
    return labels, comps, owner, m, h


def value_comps(labels, comps, owner, i):
    """The components of option i that are not its label."""
    b = labels[i]
    return [c for ci, c in enumerate(comps) if owner.get(ci) == i and ((c[0] + c[2]) / 2 > b[2] or c[1] > b[3])]


def detect_b1(g, tpl=None):
    a = assign(g, tpl)
    if a is None:
        d = detect_b0(g)
        return {**d, "why": "fallback_b0" if d["boxes"] else "no_labels"}
    labels, comps, owner, m, _h = a
    boxes, values, lab = [], [], []
    for i, b in enumerate(labels):
        mine = [comps[ci] for ci, o in owner.items() if o == i]
        lr = (b[0], b[1], b[2], b[3])
        val = value_comps(labels, comps, owner, i)
        boxes.append(list(map(int, union(mine + [tighten(m, lr)]))))
        values.append(list(map(int, union(val))) if val else None)
        lab.append([int(v) for v in lr])
    why = "" if all(values) else "empty_value"
    return {"boxes": boxes, "values": values, "labels": lab,
            "scores": [round(b[4], 3) for b in labels], "why": why}


ARMS = {"B0": detect_b0, "B1": detect_b1}


# --- Reference boxes and scoring (as in the notebook) -----------------------

def _items(boxes):
    geo = {}
    for box, text, _s in boxes:
        xs, ys = [p[0] for p in box], [p[1] for p in box]
        geo[(min(xs), (min(ys) + max(ys)) / 2, text)] = (min(xs), min(ys), max(xs), max(ys))
    return [{**it, "rect": geo[(it["x"], it["y"], it["text"])]} for it in reading_order(boxes)]


def reference_boxes(boxes):
    """{letter: box} along the A..E sequence that parse_options picks, or None."""
    if len(parse_options(boxes)) != 5:
        return None
    items = _items(boxes)
    strict = {i for i, it in enumerate(items) if is_marker(it["text"], "A", strict=True) is not None}
    loose = {i for i, it in enumerate(items) if i not in strict and is_marker(it["text"], "A", strict=False) is not None}
    for start in sorted(strict, reverse=True) + sorted(loose, reverse=True):
        groups, letter_i, current = {}, 0, None
        for it in items[start:]:
            letter = LETTERS[letter_i] if letter_i < 5 else None
            if letter and is_marker(it["text"], letter, strict=(letter == "A" and start in strict)) is not None:
                current = letter
                groups[current] = [it["rect"]]
                letter_i += 1
            elif current:
                groups[current].append(it["rect"])
        if len(groups) == 5:
            return {k: union(v) for k, v in groups.items()}
    return None


def reference_ink(g, boxes):
    ref = reference_boxes(boxes)
    if ref is None:
        return None
    _t, m = otsu(g)
    return {L: tighten(m, r) for L, r in ref.items()}


PAD = 4


def area(r):
    return max(0, r[2] - r[0] + 1) * max(0, r[3] - r[1] + 1)


def inter(a, b):
    return area((max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])))


def iou(a, b):
    i = inter(a, b)
    return i / (area(a) + area(b) - i) if i else 0.0


def score(pred, refd):
    from scipy.optimize import linear_sum_assignment
    refs = [refd[L] for L in LETTERS]
    if pred is None:
        return {"found": 0, "contained": 0, "pure": 0, "iou": 0.0, "row_ok": 0, "order_ok": 0, "why": "no_five"}
    M = np.array([[iou(p, r) for r in refs] for p in pred])
    pi, ri = linear_sum_assignment(-M)
    cont = pure = 0
    for p_i, r_i in zip(pi, ri):
        p = pred[p_i]
        big = (p[0] - PAD, p[1] - PAD, p[2] + PAD, p[3] + PAD)
        cont += inter(big, refs[r_i]) == area(refs[r_i])
        pure += all(inter(p, refs[o]) <= 0.1 * area(refs[o]) for o in range(5) if o != r_i)
    order = list(ri[np.argsort(pi)]) == list(range(5))
    ok = int(cont == 5 and pure == 5 and order)
    why = "" if ok else "joined" if pure < 5 else "cut" if cont < 5 else "order"
    return {"found": 1, "contained": int(cont), "pure": int(pure), "iou": float(M[pi, ri].mean()),
            "row_ok": ok, "order_ok": int(order), "why": why}


# --- Commands ---------------------------------------------------------------

def cmd_pick(args):
    """Quick sample, by problem: gold (the 60 rows of gold3), dev (problems per level x 3
    languages) and hard (rows where today's pipeline is weak)."""
    rng = random.Random(args.seed)
    rows = load_rows(images=False)
    v5, v4 = load_boxes(V5), load_boxes(V4)
    gold = [g["key"] for g in json.load(open(GOLD3))]
    used = {k.split("|")[0] for k in gold}

    by_level = defaultdict(set)
    for k, r in rows.items():
        by_level[r["level"]].add(k.split("|")[0])
    dev = []
    for level in sorted(by_level):
        pids = sorted(by_level[level] - used)
        for pid in rng.sample(pids, min(args.per_level, len(pids))):
            used.add(pid)
            dev += [f"{pid}|{lang}" for lang in LANGS if f"{pid}|{lang}" in rows]

    o5 = {k: parse_options(v5.get(k, [])) for k in rows}
    o4 = {k: parse_options(v4.get(k, [])) for k in rows}
    pools = {
        "no_options": [k for k in rows if not o5[k] and not o4[k]],
        "two_numbers": [k for k in rows if any(TWO_NUMBERS.match(v) for v in o5[k].values())],
        "non_ascii": [k for k in rows if any(re.search(r"[^\x00-\x7f]|\^", v) for v in o5[k].values())],
        "v5_only_v4": [k for k in rows if not o5[k] and o4[k]],
    }
    quota = {"no_options": 15, "two_numbers": 20, "non_ascii": 15, "v5_only_v4": 10}
    hard, why = [], {}
    for name, pool in pools.items():
        pool = sorted(k for k in pool if k.split("|")[0] not in used and k not in why)
        for k in rng.sample(pool, min(quota[name], len(pool))):
            hard.append(k)
            why[k] = name
    os.makedirs(OUT, exist_ok=True)
    json.dump({"seed": args.seed, "strata": {"gold": gold, "dev": dev, "hard": hard}, "hard_why": why},
              open(SAMPLE, "w"), indent=1)
    print({"gold": len(gold), "dev": len(dev), "hard": len(hard)}, dict(Counter(why.values())))
    print("pool sizes:", {n: len(p) for n, p in pools.items()})


def cmd_templates(args):
    """Label templates "A)".."E)": the mean of the label crops of rows where the
    PP-OCRv5 reference gives the label position. Rows of the sample are not used."""
    rng = random.Random(args.seed)
    v5 = load_boxes(V5)
    skip = set(sample_keys())
    keys = rng.sample(sorted(k for k in load_rows(images=False) if k in v5 and k not in skip), args.rows)
    rows = load_rows(set(keys))
    crops = defaultdict(list)
    for k in keys:
        g = gray(rows[k]["image"])
        ref = reference_ink(g, v5[k])
        if not ref:
            continue
        _t, m = otsu(g)
        for L, box in ref.items():
            r = label_rect(m, box)
            if r:
                crops[L].append(g[r[1] - 1:r[3] + 2, r[0] - 1:r[2] + 2])
    out = {}
    heights = Counter(c.shape[0] for L in LETTERS for c in crops[L])
    print("label heights (px, with 1 px margin):", sorted(heights.items()))
    for L in LETTERS:
        scaled = [cv2.resize(c, (round(c.shape[1] * TPL_H / c.shape[0]), TPL_H), interpolation=cv2.INTER_CUBIC)
                  for c in crops[L]]
        width, n = Counter(c.shape[1] for c in scaled).most_common(1)[0]
        same = [c for c in scaled if c.shape[1] == width]
        out[L] = np.mean(same, axis=0).round().astype(np.uint8)
        print(L, "crops", len(crops[L]), "-> template", out[L].shape, "from", n)
    np.savez(TEMPLATES, **out)


def scope_keys(args):
    return None if args.scope == "all" else set(sample_keys())


def _detect(job):
    arm, key, image = job
    return key, ARMS[arm](gray(image))


def cmd_detect(args):
    from concurrent.futures import ProcessPoolExecutor
    rows = load_rows(scope_keys(args))
    os.makedirs(OUT, exist_ok=True)
    path = f"{OUT}/boxes_{args.arm}_{args.scope}.jsonl"
    status = Counter()
    jobs = [(args.arm, k, r["image"]) for k, r in rows.items()]
    with ProcessPoolExecutor(args.workers) as ex, open(path, "w") as f:
        for k, d in ex.map(_detect, jobs, chunksize=16):
            status[d["why"] or "ok"] += 1
            f.write(json.dumps({"key": k, **d}) + "\n")
    print(path, dict(status))


def load_detect(arm, scope):
    return {r["key"]: r for r in map(json.loads, open(f"{OUT}/boxes_{arm}_{scope}.jsonl"))}


def cmd_score(args):
    rows = load_rows(scope_keys(args))
    v5 = load_boxes(V5)
    refs = {}
    for k, r in rows.items():
        ref = reference_ink(gray(r["image"]), v5[k]) if k in v5 else None
        if ref:
            refs[k] = ref
    print(f"{len(rows)} rows, {len(refs)} with a reference")
    out = {}
    for arm in args.arms:
        det = load_detect(arm, args.scope)
        sc = {k: score(det[k]["boxes"], refs[k]) for k in refs}
        out[arm] = sc
        n = len(sc)
        found_all = sum(1 for k in rows if det[k]["boxes"])
        print(f"{arm}: five boxes {found_all}/{len(rows)} of all rows | with reference: "
              f"found {sum(s['found'] for s in sc.values())}/{n}, row OK {sum(s['row_ok'] for s in sc.values())}/{n} "
              f"({100 * sum(s['row_ok'] for s in sc.values()) / n:.2f}%), "
              f"fails {dict(Counter(s['why'] for s in sc.values() if not s['row_ok']))}")
    json.dump({a: {k: s for k, s in sc.items() if not s["row_ok"]} for a, sc in out.items()},
              open(f"{OUT}/box_fails_{args.scope}.json", "w"), indent=1)
    if len(args.arms) == 2:
        a, b = args.arms
        print(f"{a} ok, {b} not:", sum(out[a][k]["row_ok"] and not out[b][k]["row_ok"] for k in refs),
              f"| {b} ok, {a} not:", sum(out[b][k]["row_ok"] and not out[a][k]["row_ok"] for k in refs))


def draw(g, det, ref=None):
    vis = cv2.cvtColor(g, cv2.COLOR_GRAY2BGR)
    for b in (ref or {}).values():
        cv2.rectangle(vis, (int(b[0]), int(b[1])), (int(b[2]), int(b[3])), (0, 0, 255), 1)
    for i, b in enumerate(det.get("boxes") or []):
        cv2.rectangle(vis, (b[0] - 3, b[1] - 3), (b[2] + 3, b[3] + 3), (0, 160, 0), 2)
        cv2.putText(vis, LETTERS[i], (b[0], max(12, b[1] - 6)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 160, 0), 1)
    for b in det.get("values") or []:
        if b:
            cv2.rectangle(vis, (b[0], b[1]), (b[2], b[3]), (255, 120, 0), 1)
    return vis


def cmd_sheets(args):
    """Boxes drawn on the images: green = option, orange = value, red = PP-OCRv5 reference."""
    keys = json.load(open(args.keys)) if args.keys else sample_keys(args.strata)
    keys = keys[:args.limit]
    rows = load_rows(set(keys))
    det = load_detect(args.arm, args.scope)
    v5 = load_boxes(V5)
    outdir = f"{OUT}/sheets/{args.name}"
    os.makedirs(outdir, exist_ok=True)
    for n in range(0, len(keys), args.per_sheet):
        tiles = []
        for k in keys[n:n + args.per_sheet]:
            g = gray(rows[k]["image"])
            vis = draw(g, det[k], reference_ink(g, v5[k]) if k in v5 else None)
            if args.band:  # only the lower part, where the options are
                bx = det[k].get("boxes")
                top = max(0, min(b[1] for b in bx) - 60) if bx else max(0, g.shape[0] - 160)
                vis = vis[top:]
            tiles.append(cv2.copyMakeBorder(vis, 18, 4, 0, 1700 - vis.shape[1], cv2.BORDER_CONSTANT, value=(255, 255, 255)))
            cv2.putText(tiles[-1], f"#{n + len(tiles) - 1} {det[k]['why']}", (4, 13), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (120, 0, 120), 1)
        cv2.imwrite(f"{outdir}/sheet_{n // args.per_sheet:03d}.png", np.vstack(tiles))
    json.dump(keys, open(f"{outdir}/keys.json", "w"))
    print(outdir, len(keys), "rows")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("pick")
    s.add_argument("--seed", type=int, default=53)
    s.add_argument("--per-level", type=int, default=8)
    s = sub.add_parser("templates")
    s.add_argument("--seed", type=int, default=5)
    s.add_argument("--rows", type=int, default=200)
    s = sub.add_parser("detect")
    s.add_argument("--arm", default="B0", choices=sorted(ARMS))
    s.add_argument("--workers", type=int, default=8)
    s.add_argument("--scope", default="sample", choices=["sample", "all"])
    s = sub.add_parser("score")
    s.add_argument("--arms", nargs="+", default=["B0"])
    s.add_argument("--scope", default="sample", choices=["sample", "all"])
    s = sub.add_parser("sheets")
    s.add_argument("--arm", default="B0")
    s.add_argument("--scope", default="sample", choices=["sample", "all"])
    s.add_argument("--strata", nargs="*", default=None)
    s.add_argument("--keys", help="JSON list of keys, instead of the sample")
    s.add_argument("--name", default="review")
    s.add_argument("--limit", type=int, default=60)
    s.add_argument("--per-sheet", type=int, default=6)
    s.add_argument("--band", action="store_true")
    args = p.parse_args()
    {"pick": cmd_pick, "templates": cmd_templates, "detect": cmd_detect, "score": cmd_score, "sheets": cmd_sheets}[args.cmd](args)


if __name__ == "__main__":
    main()
