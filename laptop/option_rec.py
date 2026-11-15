"""Read the five answer options with a text recognizer run inside the OpenCV boxes.

Experiment: docs/experiments/2026-11-option-boxes-intermediate-rec.md

The boxes come from laptop/option_boxes.py (arm B1). No text detector runs: the value
of each option goes straight to a CTC recognizer (ONNX Runtime, CPU).

Recognizers (--rec), in data/external/ocr_models/:
  R0  latin_PP-OCRv5_rec_mobile   1.95 M parameters (the recognizer in use today)
  R1  PP-OCRv6_rec_small          5.2 M
  R2  PP-OCRv6_rec_medium         19 M
Input (--input), t = Otsu's threshold of the whole image:
  I0  the gray crop                       I1  binary at t (ink black, rest white)
  I2  gray ink, white above (t + 255) / 2 I3  binary at (t + 255) / 2
Mode (--mode):
  line  one read per text line of the value
  2d    OpenCV splits a stacked fraction and a raised exponent first; each part is read
        on its own and the value is written on one line: a/b, x^2

Commands (repo root, `.venv/bin/python -I laptop/option_rec.py ...`):
  run        read the sample with every arm asked for -> data/interim/optrec/read_B1-<rec>-<input>-<mode>.jsonl
             --all: every eng/cat/esp text-only row     -> data/interim/optrec/readall_B1-<...>.jsonl
  score      compare every read_*.jsonl with today's pipelines on the gold rows and the sample;
             --selective <arm> adds P4: today's options, with the new read where OpenCV saw a
             fraction or an exponent, or where today's option fails a format check
  score-all  the same without gold, on every eng/cat/esp text-only row (after `run --all`)
  granite    the reference: granite-docling-258M on the value crops of the gold rows
             (GPU; needs torch and transformers, which pyproject.toml does not declare)
  speed      time each recognizer on the crops of the dev rows, at 1 and 4 threads

Needs: data/interim/optrec/label_templates.npz (option_boxes.py templates) and the ONNX
files above. score and score-all also need the box files of ocr_boxes.py and the crop
OCR of the OpenCV crops experiment (option_crops/manifest.jsonl, ocr_boxes_crops_v5.jsonl).

To read one image from Python, see read_row and docs/OPTION_READER_GUIDE.md. With no
labels found, read_row returns no options and why="no_labels" (there is no B0 fallback).

It never prints problem text. Everything it writes stays under data/interim/.
"""
import argparse
import glob
import json
import math
import os
import re
import sys
import time
from collections import Counter, defaultdict

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import option_boxes as ob  # noqa: E402
from option_boxes import LETTERS, OUT  # noqa: E402

MODELS = {"R0": "latin_PP-OCRv5_rec_mobile.onnx", "R1": "PP-OCRv6_rec_small.onnx", "R2": "PP-OCRv6_rec_medium.onnx"}
MODEL_DIR = "data/external/ocr_models"
INPUTS = ("I0", "I1", "I2", "I3")
PAD = 4            # px of context kept around a crop
BORDER = 6         # px of white added around it
GOLDS = {"gold": ob.GOLD3, "gold_hard": f"{OUT}/options_gold_hard.json"}


# --- Recognizer -------------------------------------------------------------

class Rec:
    """A PaddleOCR CTC recognizer exported to ONNX; the characters are in its metadata."""

    def __init__(self, name, threads=4):
        import onnxruntime as ort
        opt = ort.SessionOptions()
        opt.intra_op_num_threads = threads
        opt.log_severity_level = 3
        self.session = ort.InferenceSession(os.path.join(MODEL_DIR, MODELS[name]), opt, providers=["CPUExecutionProvider"])
        chars = self.session.get_modelmeta().custom_metadata_map["character"].splitlines()
        self.chars = ["", *chars, " "]   # index 0 is the CTC blank; PaddleOCR adds the space last
        self.input = self.session.get_inputs()[0].name
        self.seconds, self.calls = 0.0, 0

    def read(self, img):
        """Text and mean confidence of one gray text-line image."""
        h, w = img.shape[:2]
        nw = max(8, math.ceil(48 * w / h))
        x = cv2.resize(cv2.cvtColor(img, cv2.COLOR_GRAY2BGR), (nw, 48)).astype(np.float32)
        x = ((x / 255 - 0.5) / 0.5).transpose(2, 0, 1)
        batch = np.zeros((1, 3, 48, max(320, nw)), np.float32)   # as PaddleOCR: zero padding on the right
        batch[0, :, :, :nw] = x
        t0 = time.perf_counter()
        p = self.session.run(None, {self.input: batch})[0][0]
        self.seconds += time.perf_counter() - t0
        self.calls += 1
        idx, prob = p.argmax(1), p.max(1)
        out, conf, last = [], [], 0
        for i, pr in zip(idx, prob):
            if i != last and i != 0:
                out.append(self.chars[i])
                conf.append(float(pr))
            last = i
        return "".join(out).strip(), float(np.mean(conf)) if conf else 0.0


# --- Crops ------------------------------------------------------------------

def variant(crop, t, kind):
    soft = (t + 255) / 2
    if kind == "I1":
        crop = np.where(crop < t, 0, 255)
    elif kind == "I2":
        crop = np.where(crop < soft, crop, 255)
    elif kind == "I3":
        crop = np.where(crop < soft, 0, 255)
    crop = crop.astype(np.uint8)
    return cv2.copyMakeBorder(crop, BORDER, BORDER, BORDER, BORDER, cv2.BORDER_CONSTANT, value=255)


def rect_crop(g, box):
    H, W = g.shape
    return g[max(0, box[1] - PAD):min(H, box[3] + PAD + 1), max(0, box[0] - PAD):min(W, box[2] + PAD + 1)]


def render(g, comps):
    """Only these components, on white: nothing else that falls in their box is read."""
    x0, y0, x1, y1 = ob.union(comps)
    out = np.full((y1 - y0 + 1 + 2 * PAD, x1 - x0 + 1 + 2 * PAD), 255, np.uint8)
    H, W = g.shape
    for c in comps:
        a, b, cc, d = max(0, c[0] - 1), max(0, c[1] - 1), min(W - 1, c[2] + 1), min(H - 1, c[3] + 1)
        out[b - y0 + PAD:d - y0 + PAD + 1, a - x0 + PAD:cc - x0 + PAD + 1] = g[b:d + 1, a:cc + 1]
    return out


# --- Structure of one value (OpenCV only) -----------------------------------

def fractions(comps, h):
    """[(bar, numerator comps, denominator comps)]: a bar with glyphs over and under it.
    A minus or an equals sign has nothing on one side; the dots of a division sign are
    too small to be a numerator."""
    out = []
    for b in comps:
        if not ob.is_bar(b, h):
            continue
        inside = [c for c in comps if c is not b and b[0] - 3 <= (c[0] + c[2]) / 2 <= b[2] + 3]
        num = [c for c in inside if c[3] < b[1]]
        den = [c for c in inside if c[1] > b[3]]
        if any(c[3] - c[1] + 1 >= 0.3 * h for c in num) and any(c[3] - c[1] + 1 >= 0.3 * h for c in den):
            out.append((b, num, den))
    return out


def text_rows(comps, h):
    """Components grouped into text lines, top to bottom (an option that continues below).
    Two lines are at least 0.8 x the label height apart; anything closer is one line
    (the dot of an "i", an accent, an exponent)."""
    rows = []
    for c in sorted(comps, key=lambda c: c[1]):
        if rows and c[1] <= max(r[3] for r in rows[-1]) + 0.1 * h:
            rows[-1].append(c)
        else:
            rows.append([c])

    def centre(r):
        return (min(c[1] for c in r) + max(c[3] for c in r)) / 2

    merged = [rows[0]] if rows else []
    for r in rows[1:]:
        small = max(c[3] - c[1] + 1 for c in r) < 0.3 * h or max(c[3] - c[1] + 1 for c in merged[-1]) < 0.3 * h
        if small or centre(r) - centre(merged[-1]) < 0.8 * h:
            merged[-1] = merged[-1] + r
        else:
            merged.append(r)
    return merged


def superscripts(comps, h, label):
    """Components that sit raised and are smaller than a digit. The size of a digit and
    the baseline come from the label (a capital is 0.65 x the label height and stands
    0.69 x below its top), so a value of low letters only, such as a pi, has them too."""
    D, base = 0.65 * h, label[1] + 0.69 * h
    sup = []
    for c in comps:
        hc = c[3] - c[1] + 1
        left = [o for o in comps if o is not c and o[2] < c[0] + 2 and c[0] - o[2] <= 0.6 * D and o[3] >= base - 0.2 * D]
        if 0.35 * D <= hc <= 0.9 * D and c[3] <= base - 0.35 * D and left:
            sup.append(c)
    return sup


def segments(comps, h, label):
    """The value as runs in reading order: ("base" | "sup", comps) or ("frac", num, den)."""
    fr = fractions(comps, h)
    used = {id(c) for b, num, den in fr for c in [b, *num, *den]}
    rest = [c for c in comps if id(c) not in used]
    sup = {id(c) for c in superscripts(rest, h, label)}
    items = [((b[0] + b[2]) / 2, "frac", (num, den)) for b, num, den in fr]
    items += [((c[0] + c[2]) / 2, "sup" if id(c) in sup else "base", c) for c in rest]
    out = []
    for _x, kind, v in sorted(items, key=lambda it: it[0]):
        if kind == "frac":
            out.append(("frac", *v))
        elif out and out[-1][0] == kind:
            out[-1][1].append(v)
        else:
            out.append((kind, [v]))
    return out


SIMPLE = re.compile(r"^[0-9a-zA-Zπ.,]+$")


def paren(s):
    return s if SIMPLE.match(s) else f"({s})"


def join_lines(lines):
    out = ""
    for s in lines:
        if out.endswith("-") and s[:1].islower():
            out = out[:-1] + s      # a word cut at the end of the line
        else:
            out = (out + " " + s).strip()
    return out


def read_value(rec, g, t, comps, h, label, inp, mode):
    """Text of one option value, the lowest confidence of its reads, and what OpenCV saw."""
    confs = []

    def read(img):
        s, c = rec.read(variant(img, t, inp))
        confs.append(c)
        return s

    fr = fractions(comps, h)
    rows = text_rows(comps, h) if not fr else [comps]
    if len(rows) > 1:   # words on several lines: one read per line, in both modes
        return join_lines([read(rect_crop(g, ob.union(r))) for r in rows]), min(confs), "lines"
    if mode == "line":
        return read(rect_crop(g, ob.union(comps))), min(confs), "frac" if fr else ""
    segs = segments(comps, h, label)
    kinds = {s[0] for s in segs}
    if kinds == {"base"}:
        return read(rect_crop(g, ob.union(comps))), min(confs), ""
    out = ""
    for s in segs:
        if s[0] == "frac":
            out += f"{paren(read(render(g, s[1])))}/{paren(read(render(g, s[2])))}"
        elif s[0] == "sup":
            c = ob.union(s[1])
            txt = read(render(g, s[1]))
            round_one = len(s[1]) == 1 and (c[2] - c[0] + 1) >= 0.85 * (c[3] - c[1] + 1)
            if round_one and txt in ("o", "O", "0", "°", "º"):
                out += "°"
            elif re.fullmatch(r"[0-9a-zA-Z+\-−]+", txt):
                out += "^" + txt
            else:
                out += txt
        else:
            txt = read(render(g, s[1]))
            # "2^90 3^20": without the space the exponent would run into the next base.
            out += (" " if re.search(r"\^[0-9a-zA-Z+\-−]+$", out) and txt[:1].isalnum() else "") + txt
    return out, min(confs), "+".join(sorted(kinds - {"base"}))


def read_row(recs, g, arms):
    """One row with every arm (rec, input, mode); the boxes are found once."""
    a = ob.assign(g)
    out = {arm: {"options": {}, "why": "no_labels"} for arm in arms}
    if a is None:
        return out
    labels, comps, owner, _m, h = a
    t, _ = ob.otsu(g)
    vals = [ob.value_comps(labels, comps, owner, i) for i in range(5)]
    if not all(vals):
        return {arm: {"options": {}, "why": "empty_value"} for arm in arms}
    for arm in arms:
        name, inp, mode = arm
        opts, conf, seen = {}, {}, {}
        for L, val, label in zip(LETTERS, vals, labels):
            opts[L], conf[L], seen[L] = read_value(recs[name], g, t, val, h, label, inp, mode)
        out[arm] = {"options": opts, "conf": conf, "seen": seen, "why": ""}
    return out


def cmd_run(args):
    keys = sorted(ob.load_rows(images=False)) if args.all else ob.sample_keys(args.strata)
    rows = ob.load_rows(set(keys))
    arms = [(r, i, m) for r in args.rec for i in args.input for m in args.mode]
    recs = {r: Rec(r, args.threads) for r in args.rec}
    prefix = "readall" if args.all else "read"
    files = {arm: open(f"{OUT}/{prefix}_B1-{'-'.join(arm)}.jsonl", "w") for arm in arms}
    seen = Counter()
    for k in keys:
        res = read_row(recs, ob.gray(rows[k]["image"]), arms)
        seen.update(v for v in res[arms[-1]].get("seen", {}).values() if v)
        for arm, r in res.items():
            files[arm].write(json.dumps({"key": k, **r}, ensure_ascii=False) + "\n")
    for f in files.values():
        f.close()
    print(f"{len(keys)} rows x {len(arms)} arms; structures seen by OpenCV: {dict(seen)}")
    for r, rec in recs.items():
        print(f"{r}: {rec.calls} reads, {1000 * rec.seconds / max(1, rec.calls):.1f} ms per read ({args.threads} threads)")


# --- Today's pipelines on the same rows -------------------------------------

def strip_label(texts, L):
    rest = ob.is_marker(texts[0], L, strict=False)
    return " ".join(([rest] if rest is not None else texts[:1]) + texts[1:]).strip().lstrip(")）] ").strip()


def by_opencv_boxes(boxes, rects):
    """The fallback of the OpenCV experiment: each OCR box goes to the B0 region that holds its centre."""
    if not boxes or not rects:
        return {}
    groups = defaultdict(list)
    for box, text, _score in boxes:
        cx, cy = sum(p[0] for p in box) / 4, sum(p[1] for p in box) / 4
        for L, (x0, y0, x1, y1) in zip(LETTERS, rects):
            if x0 <= cx <= x1 and y0 <= cy <= y1:
                groups[L].append((box, text, 1.0))
                break
    groups = {L: [it["text"] for it in ob.reading_order(v)] for L, v in groups.items()}
    out = {L: strip_label(groups[L], L) for L in LETTERS if groups.get(L)}
    return out if len(out) == 5 and all(out.values()) else {}


def baselines(keys):
    v5, v4 = ob.load_boxes(ob.V5), ob.load_boxes(ob.V4)
    o5 = {k: ob.parse_options(v5.get(k, [])) for k in keys}
    o4 = {k: ob.parse_options(v4.get(k, [])) for k in keys}
    masked, rects = {}, {}
    for r in map(json.loads, open("data/interim/ocr_boxes_crops_v5.jsonl")):
        if r["kind"] == "region_mask" and r["key"] in o5:
            masked[r["key"]] = r["boxes"]
    for m in map(json.loads, open("data/interim/option_crops/manifest.jsonl")):
        if m["kind"] == "region_mask" and m["key"] in o5:
            rects[m["key"]] = m["options"]
    return {
        "P0 v5>v4 (today)": {k: o5[k] or o4[k] for k in keys},
        "P1 v5>masked+OpenCV": {k: o5[k] or by_opencv_boxes(masked.get(k), rects.get(k)) for k in keys},
        "v5 alone": o5,
    }


def load_arm(path):
    return {r["key"]: r for r in map(json.loads, open(path))}


def selective(p0, new):
    """P4: today's options; the new read replaces an option where OpenCV saw a fraction
    or an exponent, or where today's value fails a format check; and the whole row
    where today's pipeline gives no options."""
    import option_consensus as oc
    out = {}
    for k, r in new.items():
        base = p0.get(k) or {}
        if len(base) != 5 or not r["options"]:
            out[k] = r["options"] or base
            continue
        o = dict(base)
        for L in LETTERS:
            if r["seen"].get(L) in ("frac", "sup", "frac+sup") or oc.option_flags(base[L]) or oc.TWO_NUMBERS.match(base[L]):
                o[L] = r["options"][L]
        out[k] = o
    return out


# --- Scoring ----------------------------------------------------------------

def error_kind(got, want):
    import option_consensus as oc
    if not got:
        return "missing"
    if "/" in want:
        return "fraction"
    if "^" in oc.basic(want):
        return "exponent"
    if re.search(r"[^\x00-\x7f]", want):
        return "symbol"
    return "other"


def cmd_score(args):
    import option_consensus as oc
    strata = json.load(open(ob.SAMPLE))["strata"]
    keys = [k for ks in strata.values() for k in ks]
    arms = baselines(keys)
    reads = {}
    for path in sorted(glob.glob(f"{OUT}/read_*.jsonl")):
        name = os.path.basename(path)[5:-6]
        reads[name] = load_arm(path)
        arms[name] = {k: r["options"] for k, r in reads[name].items()}
    for name in args.selective or []:
        arms[f"P4 P0+{name}"] = selective(arms["P0 v5>v4 (today)"], reads[name])
    golds = {n: {g["key"]: g["options"] for g in json.load(open(p))} for n, p in GOLDS.items() if os.path.exists(p)}
    p0 = arms["P0 v5>v4 (today)"]

    def ok_rows(arm, gold):
        return [all(arm.get(k, {}).get(L) and oc.gold_norm(arm[k][L]) == oc.gold_norm(g[L]) for L in LETTERS)
                for k, g in gold.items()]

    for gname, gold in golds.items():
        print(f"\n== {gname}: {len(gold)} rows, {5 * len(gold)} options ==")
        print(f"{'arm':34} rows5  opts  lenient  errors by kind                      vs P0 (lost/won, p)")
        for name, arm in arms.items():
            if not all(k in arm for k in gold):
                continue
            r_ok, n, o_ok, _o = oc.gold_scores(arm, gold)
            _r, _n, o_len, _ = oc.gold_scores(arm, gold, lenient=True)
            kinds = Counter(error_kind(arm[k].get(L), g[L]) for k, g in gold.items() for L in LETTERS
                            if not (arm[k].get(L) and oc.gold_norm(arm[k][L]) == oc.gold_norm(g[L])))
            n01, n10, pv = oc.mcnemar(ok_rows(p0, gold), ok_rows(arm, gold))
            print(f"{name:34} {r_ok:3}/{n}  {o_ok:4}  {o_len:4}    {str(dict(kinds)):36} {n01}/{n10} p={pv:.3f}")

    for sname in ("dev", "hard"):
        ks = strata[sname]
        print(f"\n== {sname}: {len(ks)} rows ==")
        print(f"{'arm':34} five%  valid%  agree3%  (n)   same as P0 %")
        for name, arm in arms.items():
            if not all(k in arm for k in ks):
                continue
            five = [k for k in ks if len(arm[k]) == 5 and all(arm[k].values())]
            valid = [k for k in five if not oc.row_flags(arm[k])]
            by = defaultdict(dict)
            for k in five:
                by[k.split("|")[0]][k.split("|")[1]] = arm[k]
            agree = tot = 0
            for langs in by.values():
                if len(langs) == 3:
                    for L in LETTERS:
                        tot += 1
                        agree += len({oc.gold_norm(o[L]) for o in langs.values()}) == 1
            both = [k for k in five if len(p0[k]) == 5]
            same = sum(oc.gold_norm(arm[k][L]) == oc.gold_norm(p0[k][L]) for k in both for L in LETTERS)
            print(f"{name:34} {100 * len(five) / len(ks):5.1f}  {100 * len(valid) / len(ks):5.1f}  "
                  f"{100 * agree / tot if tot else float('nan'):6.1f}  {tot // 5:3}   "
                  f"{100 * same / (5 * len(both)) if both else float('nan'):5.1f}")


def cmd_score_all(args):
    """Every eng/cat/esp text-only row: no gold, so coverage, format and agreement of the
    three languages of a problem (the option values do not depend on the language)."""
    import option_consensus as oc
    keys = sorted(ob.load_rows(images=False))
    arms = baselines(keys)
    for path in sorted(glob.glob(f"{OUT}/readall_*.jsonl")):
        arms[os.path.basename(path)[8:-6]] = {k: r["options"] for k, r in load_arm(path).items()}
    p0 = arms["P0 v5>v4 (today)"]
    print(f"{len(keys)} rows")
    print(f"{'arm':28} five    valid   agree3 strict / language-free (options)   differs from P0")
    for name, arm in arms.items():
        five = [k for k in keys if len(arm.get(k, {})) == 5 and all(arm[k].values())]
        valid = [k for k in five if not oc.row_flags(arm[k])]
        by = defaultdict(dict)
        for k in five:
            by[k.split("|")[0]][k.split("|")[1]] = arm[k]
        agree = tot = agree_m = tot_m = 0
        for langs in by.values():
            if len(langs) == 3:
                for L in LETTERS:
                    vals = [o[L] for o in langs.values()]
                    tot += 1
                    agree += len({oc.gold_norm(v) for v in vals}) == 1
                    if all(oc.canon(v) for v in vals):   # numbers and expressions, no words
                        tot_m += 1
                        agree_m += len({oc.canon(v)[0] for v in vals}) == 1
        both = [k for k in five if len(p0[k]) == 5]
        diff = sum(oc.gold_norm(arm[k][L]) != oc.gold_norm(p0[k][L]) for k in both for L in LETTERS)
        print(f"{name:28} {len(five):4}    {len(valid):4}    {agree}/{tot} ({100 * agree / tot:.1f}%) / "
              f"{agree_m}/{tot_m} ({100 * agree_m / tot_m:.2f}%)   {diff}/{5 * len(both)}")


# --- Reference: granite-docling-258M on the same value crops ------------------
#
# 50 times the parameters of R1. It is here only to show how much a much larger model
# would add; it runs on the GPU with transformers, on the gold rows.

GRANITE = "ibm-granite/granite-docling-258M"
PROMPTS = {"G-formula": "Convert formula to LaTeX.", "G-page": "Convert this page to docling."}
LATEX = [(r"\\(?:d|t)?frac\s*\{([^{}]*)\}\s*\{([^{}]*)\}", lambda m: f"{paren(m.group(1))}/{paren(m.group(2))}"),
         (r"\\sqrt\s*\{([^{}]*)\}", r"√\1"), (r"\^\s*\{\s*°\s*\}|\^\s*°", "°"),
         (r"\^\s*\{([^{}]*)\}", r"^\1"), (r"\\(?:mathrm|text|mathbf|mathit|operatorname)\s*\{([^{}]*)\}", r"\1")]
SYMBOLS = {r"\cdot": "·", r"\times": "×", r"\div": "÷", r"\pi": "π", r"\infty": "∞", r"\leq": "≤", r"\le": "≤",
           r"\geq": "≥", r"\ge": "≥", r"\%": "%", r"\circ": "°", r"\colon": ":", r"\left": "", r"\right": "",
           r"\,": "", r"\;": "", r"\!": "", r"\ ": " ", r"\quad": " ", "$": ""}


def latex_canon(text):
    """DocTags or LaTeX of a simple expression as one line of text: a/b, x^2, √2."""
    t = re.sub(r"<loc_\d+>|<\|[a-z_]+\|>", "", text)
    t = re.sub(r"</?[a-z_]+>", " ", t)
    t = re.sub(r"\s+", "", t)   # the model writes a space between tokens: "1 1" is 11
    for k in sorted(SYMBOLS, key=len, reverse=True):
        t = t.replace(k, SYMBOLS[k])
    for _ in range(4):   # nested braces, from the inside out
        for pat, rep in LATEX:
            t = re.sub(pat, rep, t)
    return re.sub(r"\s+", " ", t.replace("{", "").replace("}", "")).strip()


def cmd_granite(args):
    import torch
    from PIL import Image
    from transformers import AutoModelForVision2Seq, AutoProcessor

    proc = AutoProcessor.from_pretrained(GRANITE)
    model = AutoModelForVision2Seq.from_pretrained(GRANITE, torch_dtype=torch.bfloat16).to("cuda").eval()
    keys = [g["key"] for name in args.gold for g in json.load(open(GOLDS[name]))]
    rows = ob.load_rows(set(keys))
    prompts = {a: PROMPTS[a] for a in args.arms}
    files = {a: open(f"{OUT}/read_{a}.jsonl", "w") for a in prompts}
    secs = n = 0
    for k in keys:
        g = ob.gray(rows[k]["image"])
        labels, comps, owner, _m, _h = ob.assign(g)
        t, _ = ob.otsu(g)
        opts = {a: {} for a in prompts}
        raw = {a: {} for a in prompts}
        for i, L in enumerate(LETTERS):
            crop = variant(rect_crop(g, ob.union(ob.value_comps(labels, comps, owner, i))), t, "I0")
            crop = cv2.copyMakeBorder(crop, 12, 12, 12, 12, cv2.BORDER_CONSTANT, value=255)
            img = Image.fromarray(crop).convert("RGB")
            for a, prompt in prompts.items():
                msg = [{"role": "user", "content": [{"type": "image"}, {"type": "text", "text": prompt}]}]
                inputs = proc(text=proc.apply_chat_template(msg, add_generation_prompt=True), images=[img],
                              return_tensors="pt").to("cuda")
                t0 = time.perf_counter()
                with torch.no_grad():
                    out = model.generate(**inputs, max_new_tokens=64, do_sample=False)
                secs += time.perf_counter() - t0
                n += 1
                raw[a][L] = proc.batch_decode(out[:, inputs["input_ids"].shape[1]:], skip_special_tokens=False)[0]
                raw[a][L] = raw[a][L].replace("<end_of_utterance>", "").strip()
                opts[a][L] = latex_canon(raw[a][L])
        for a in prompts:
            files[a].write(json.dumps({"key": k, "options": opts[a], "raw": raw[a], "why": ""}, ensure_ascii=False) + "\n")
            files[a].flush()
    print(f"{len(keys)} rows, {n} generations, {1000 * secs / n:.0f} ms each on the GPU")


def cmd_speed(args):
    keys = ob.sample_keys(["dev"])[:args.rows]
    rows = ob.load_rows(set(keys))
    crops = []
    for k in keys:
        g = ob.gray(rows[k]["image"])
        a = ob.assign(g)
        if a is None:
            continue
        labels, comps, owner, _m, _h = a
        t, _ = ob.otsu(g)
        for i in range(5):
            val = ob.value_comps(labels, comps, owner, i)
            if val:
                crops.append(variant(rect_crop(g, ob.union(val)), t, "I0"))
    for name in args.rec:
        for threads in (1, 4):
            rec = Rec(name, threads)
            for c in crops[:20]:
                rec.read(c)   # warm-up
            rec.seconds, rec.calls = 0.0, 0
            for c in crops:
                rec.read(c)
            size = os.path.getsize(os.path.join(MODEL_DIR, MODELS[name])) / 1e6
            print(f"{name} ({size:.1f} MB) {threads} thread(s): {1000 * rec.seconds / rec.calls:.1f} ms per option, {len(crops)} crops")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("run")
    s.add_argument("--rec", nargs="+", default=["R1"], choices=sorted(MODELS))
    s.add_argument("--input", nargs="+", default=["I0"], choices=INPUTS)
    s.add_argument("--mode", nargs="+", default=["line", "2d"], choices=["line", "2d"])
    s.add_argument("--strata", nargs="*", default=None)
    s.add_argument("--threads", type=int, default=4)
    s.add_argument("--all", action="store_true", help="every eng/cat/esp text-only row, not the sample")
    s = sub.add_parser("score")
    s.add_argument("--selective", nargs="*", help="arms to combine with today's pipeline (P4)")
    sub.add_parser("score-all")
    s = sub.add_parser("granite")
    s.add_argument("--arms", nargs="+", default=["G-formula"], choices=sorted(PROMPTS))
    s.add_argument("--gold", nargs="+", default=["gold_hard"], choices=sorted(GOLDS))
    s = sub.add_parser("speed")
    s.add_argument("--rec", nargs="+", default=sorted(MODELS))
    s.add_argument("--rows", type=int, default=60)
    args = p.parse_args()
    {"run": cmd_run, "score": cmd_score, "score-all": cmd_score_all, "granite": cmd_granite, "speed": cmd_speed}[args.cmd](args)


if __name__ == "__main__":
    main()
