#!/usr/bin/env python3
"""Read stacked fractions and exponents in the answer options from OCR geometry.

Experiment: docs/experiments/2026-11-math-layout.md (not written yet)

Input: one record of `laptop/ocr_boxes.py dump --engine v5 --chars`:
    {"key", "boxes": [[quad, text, score], ...],
     "chars": [[[c, x0, x1, ink_top, ink_bottom], ...] per box],   # c: non-space chars of text
     "bars":  [None | {"y", "ratio", "halves": [top, bottom] | None} per box]}

Three layouts, each a pure rule on stored measurements (no GPU):
  A  stacked pair   two boxes in one option, one above the other, x overlapping:
                    "7" over "10" -> "7/10" (reading order alone gives "10 7")
  B  tall box       one box holding numerator and denominator, split at a bar:
                    halves ["7", "10"] -> "7/10"
  E  exponent       a char whose ink sits above the baseline of its box:
                    "n3 - 2" with a raised 3 -> "n^3 - 2"; Unicode "cm³" -> "cm^3"

Output format (ASCII): a/b, with parentheses around a part that holds an operator
or a space, (p+3q)/4; x^2, 2016^15, a longer non-digit exponent as x^(n+1).

parse_options_math(rec, fractions=..., tall=..., exponents=...) mirrors
parse_options of laptop/prepare_m3kang.py; with all rules off it returns exactly
what parse_options returns (checked by `check`).

Usage:
    python laptop/math_layout.py --selftest
    python laptop/math_layout.py check data/interim/optx/boxes_all_v5_chars.jsonl
"""
import argparse
import json
import os
import re
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from prepare_m3kang import LETTERS, is_marker, parse_options  # noqa: E402

# --- Rules (frozen after tuning on dev; see the report) ----------------------
STACK_OVERLAP = 0.5   # x-overlap / narrower width, for a stacked pair
STACK_DY = 0.5        # |center y difference| / smaller height, for a stacked pair
STACK_MAXLEN = 12     # longest operand of a stacked pair, in characters
BAR_RATIO = 0.35      # share of the box width that the bar row must cover (the box has margins)
BAR_SWALLOW = 1.25    # a denominator box this much taller than its numerator holds the bar
SAME_RANGE = 0.7      # x-overlap of two chars' ranges above which they share one column
SUP_RAISE = 0.25      # (baseline - char bottom) / reference ink height, for a superscript
SUP_SMALL = 0.8       # char ink height / reference ink height, for a superscript
BOX_SUP_SMALL = 0.75  # box height / previous box height, for a superscript in its own box

SUPERSCRIPTS = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻", "0123456789+-")
SUP_RUN = re.compile(r"[⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻]+")
BASELINE_CHARS = re.compile(r"[0-9A-PR-Za-fhik-or-xz]")  # no descenders (g j p q y) or Q
BASE_BEFORE = re.compile(r"[0-9A-Za-zπα-ω)\]]")
SUP_CHAR = re.compile(r"[0-9A-Za-z]")
SUP_SIGN = re.compile(r"[+\-−]")      # a sign counts only inside a raised run: x^-1
OPERAND = re.compile(r"^[0-9A-Za-zπ√.,+\-−×·()|\s]+$")  # "|": a bar read into a part


# --- Items: boxes in reading order, with their row and measurements -----------

def items_of(rec):
    """reading_order of prepare_m3kang.py, keeping row index and measurements."""
    chars = rec.get("chars") or [None] * len(rec["boxes"])
    comps = rec.get("comps") or [None] * len(rec["boxes"])
    bars = rec.get("bars") or [None] * len(rec["boxes"])
    items = []
    for i, ((box, text, _score), ch, cp, bar) in enumerate(zip(rec["boxes"], chars, comps, bars)):
        ys = [pt[1] for pt in box]
        xs = [pt[0] for pt in box]
        items.append({"i": i, "x": min(xs), "x1": max(xs), "y": (min(ys) + max(ys)) / 2,
                      "y0": min(ys), "y1": max(ys), "h": max(ys) - min(ys), "text": text,
                      "chars": ch, "comps": cp, "bar": bar})
    items.sort(key=lambda it: it["y"])
    rows, current = [], []
    for it in items:
        if current and abs(it["y"] - current[-1]["y"]) > 0.6 * max(it["h"], current[-1]["h"]):
            rows.append(current)
            current = []
        current.append(it)
    if current:
        rows.append(current)
    out = []
    for r, row in enumerate(rows):
        for it in sorted(row, key=lambda it: it["x"]):
            it["row"] = r
            out.append(it)
    return out


def piece(item, text):
    """A part of an option: the text, and the item it comes from (text is a suffix of item text)."""
    nonspace = len(item["text"].replace(" ", ""))
    offset = nonspace - len(text.replace(" ", ""))  # chars before this suffix
    chs = item["chars"][offset:] if item["chars"] and len(item["chars"]) == nonspace else None
    x0, x1 = (chs[0][1], chs[-1][2]) if chs else (item["x"], item["x1"])
    return {"text": text, "item": item, "chars": chs, "x0": x0, "x1": x1,
            "y": item["y"], "h": item["h"], "row": item["row"]}


# --- Parser with pieces --------------------------------------------------------

def parse_options_math(rec, fractions=False, tall=False, exponents=False):
    items = items_of(rec)
    strict_starts = [i for i, it in enumerate(items) if is_marker(it["text"], "A", strict=True) is not None]
    loose_starts = [i for i, it in enumerate(items)
                    if i not in strict_starts and is_marker(it["text"], "A", strict=False) is not None]
    for strict_a, starts in ((True, strict_starts), (False, loose_starts)):
        for start in reversed(starts):
            options = read_sequence_pieces(items, start, strict_a, fractions)
            if len(options) == 5:
                cleaned = {k: render(v, fractions, tall, exponents) for k, v in options.items()}
                if all(cleaned.values()):
                    return cleaned
                return {}
    return {}


def read_sequence_pieces(items, start, strict_a, fractions):
    """read_sequence of prepare_m3kang.py, with pieces instead of strings."""
    options, current = {}, None
    expected = iter(LETTERS)
    letter = next(expected)
    for item in items[start:]:
        text = item["text"]
        rest = is_marker(text, letter, strict=(strict_a and letter == "A")) if letter else None
        if rest is None and letter == "C":
            d_rest = is_marker(text, "D", strict=False)
            values = [p for p in options.get("B", []) if p["text"].strip()]
            groups = group_stacks(values) if fractions else [[p] for p in values]
            if d_rest is not None and len(groups) == 2:
                options["B"], options["C"] = groups[0], groups[1]
                letter, rest = "D", d_rest
                next(expected)
        if rest is not None:
            current = letter
            options[current] = [piece(item, rest)]
            letter = next(expected, None)
        elif current:
            options[current].append(piece(item, text))
    return options


# --- Layout A: stacked pairs ----------------------------------------------------

def stacked(a, b):
    """True when piece b sits right above or below piece a, x overlapping: a fraction."""
    if not a["text"].strip() or not b["text"].strip():
        return False
    width = min(a["x1"] - a["x0"], b["x1"] - b["x0"])
    overlap = min(a["x1"], b["x1"]) - max(a["x0"], b["x0"])
    if width <= 0 or overlap < STACK_OVERLAP * width:
        return False
    if abs(a["y"] - b["y"]) <= STACK_DY * min(a["h"], b["h"]):
        return False
    short = all(len(p["text"].strip()) <= STACK_MAXLEN and OPERAND.match(p["text"].strip()) for p in (a, b))
    return bool(short)


BAR_TEXT = re.compile(r"^[\-−–—_|]+$")


def group_stacks(pieces):
    """Group consecutive pieces into stacked pairs; other pieces stay alone.

    Three pieces where the middle one is the bar read as a dash ("1", "–", "π")
    form one pair of numerator and denominator.
    """
    groups, i = [], 0
    while i < len(pieces):
        if i + 2 < len(pieces) and BAR_TEXT.match(pieces[i + 1]["text"].strip()) \
                and stacked(pieces[i], pieces[i + 2]):
            groups.append([pieces[i], pieces[i + 2]])
            i += 3
        elif i + 1 < len(pieces) and stacked(pieces[i], pieces[i + 1]):
            groups.append([pieces[i], pieces[i + 1]])
            i += 2
        else:
            groups.append([pieces[i]])
            i += 1
    return groups


def strip_bar(den, lower, upper):
    """Drop the fraction bar that OCR read into the denominator: "|6", or "15" for 5
    when the denominator box is much taller than the numerator box."""
    d = den.strip()
    if d[:1] == "|" and len(d) > 1:
        return d[1:].strip()
    if d[:1] in "1—–-" and len(d) > 1 and lower["h"] > BAR_SWALLOW * upper["h"]:
        chs = lower["chars"]
        if chs and len(chs) >= 2:
            # A bar end has no recognizer column of its own: its "1" shares the next
            # char's x-range. A real leading digit has its own range.
            a, b = chs[0], chs[1]
            overlap = min(a[2], b[2]) - max(a[1], b[1])
            if overlap > SAME_RANGE * min(a[2] - a[1], b[2] - b[1]):
                return d[1:].strip()
        else:
            # No chars (v4): a real leading digit widens the box; a bar end does not.
            per_char = (upper["x1"] - upper["x0"]) / max(len(upper["text"].replace(" ", "")), 1)
            if lower["x1"] - lower["x0"] < (len(d.replace(" ", "")) - 0.5) * per_char:
                return d[1:].strip()
    return den


def frac(num, den):
    def wrap(s):
        s = s.strip()
        return f"({s})" if re.search(r"[\s+\-−×·*/=]", s) else s
    return f"{wrap(num)}/{wrap(den)}"


# --- Layout E: exponents ---------------------------------------------------------

MERGED = 1.6  # a component wider than MERGED x the char width spans two glyphs


SPECK = 0.25   # components shorter than SPECK x the tallest in the box are dropped
PAD = 2        # pixels of slack around a char's x-range
MAIN = 0.3     # a piece must hold MAIN of a char's ink area (a neighbour's leg does not)


def char_ink(chs, comps):
    """[c, x0, x1, top, bottom] per char, from the ink components of its box.

    Binarizing breaks thin glyphs ("5") into pieces, and rapidocr's char x-ranges
    are shifted by a few pixels, so:
      1. drop specks (shorter than SPECK x the tallest component of the box);
      2. a char takes the union of the pieces that lie inside its x-range (+-PAD)
         and the pieces whose centre is nearer to it than to any other char (a
         cut-off range at the end of a box);
      3. keep the pieces that hold at least MAIN of that ink area (a slice of a
         neighbouring glyph inside a shifted range holds less);
      4. a piece wider than MERGED x the char spans two glyphs (a superscript
         touching its base): use the central-third measure instead.
    """
    if not comps or not chs:
        return [[c[0], c[1], c[2], c[3], c[4]] for c in chs]
    hmax = max(k[3] - k[2] + 1 for k in comps)
    kept = [k for k in comps if k[3] - k[2] + 1 >= SPECK * hmax]
    centres = [(c[1] + c[2]) / 2 for c in chs]
    nearest = [[] for _ in chs]
    for k in kept:
        cx = (k[0] + k[1]) / 2
        nearest[min(range(len(chs)), key=lambda i: abs(centres[i] - cx))].append(k)
    out = []
    for c, near in zip(chs, nearest):
        width = max(c[2] - c[1], 1)
        inside = [k for k in kept if k[0] >= c[1] - PAD and k[1] <= c[2] + PAD]
        ks = inside + [k for k in near if k not in inside]
        area = lambda k: (k[1] - k[0] + 1) * (k[3] - k[2] + 1)
        total = sum(area(k) for k in ks)
        ks = [k for k in ks if area(k) >= MAIN * total]  # pieces that carry the glyph
        if ks and all(k[1] - k[0] <= MERGED * width for k in ks):
            out.append([c[0], c[1], c[2], min(k[2] for k in ks), max(k[3] for k in ks)])
        else:
            out.append([c[0], c[1], c[2], c[3], c[4]])
    return out


CAP = re.compile(r"[0-9A-Z]")
XHEIGHT_GREEK = re.compile(r"[παβγδεθλμνστω]")


def raised(chs):
    """Indexes of chars whose ink sits above the box baseline (superscripts).

    Baseline and reference height come from the option letter when the box starts
    with one ("A)"), else from the median of the chars without descenders.
    """
    m = chs  # already measured by char_ink
    size_test = True
    if len(m) >= 2 and m[0][0] in LETTERS and m[1][0] in ")）]" and m[0][3] is not None:
        baseline, ref = m[0][4], m[0][4] - m[0][3]
    else:
        base = [c for c in m if (BASELINE_CHARS.match(c[0]) or XHEIGHT_GREEK.match(c[0])) and c[3] is not None]
        if len(base) < 2:
            return set()
        baseline = statistics.median(c[4] for c in base)
        tol = 0.15 * statistics.median(c[4] - c[3] for c in base)
        near = [c for c in base if abs(c[4] - baseline) <= tol]
        caps = [c for c in near if CAP.match(c[0])]
        if caps:
            ref = statistics.median(c[4] - c[3] for c in caps)
        elif near:  # no digit or capital on the baseline: x-height reference, no size test
            ref, size_test = statistics.median(c[4] - c[3] for c in near), False
        else:
            return set()
    if ref <= 0:
        return set()
    small = (lambda c: (c[4] - c[3]) < SUP_SMALL * ref) if size_test else (lambda c: True)
    out = set()
    for j, c in enumerate(m):
        if j == 0 or c[3] is None or not SUP_CHAR.match(c[0]):
            continue
        if not BASE_BEFORE.match(m[j - 1][0]) and j - 1 not in out:
            continue
        if baseline - c[4] > SUP_RAISE * ref and small(c):
            out.add(j)
    # A sign right before a raised char, itself above the baseline, joins the run.
    for j, c in enumerate(m):
        if j + 1 in out and SUP_SIGN.match(c[0]) and c[3] is not None and j > 0 \
                and BASE_BEFORE.match(m[j - 1][0]) and baseline - c[4] > SUP_RAISE * ref:
            out.add(j)
    return out


def with_exponents(p):
    """Text of piece p with raised chars written as ^exp."""
    text, chs = p["text"], p["chars"]
    if not chs:
        return text
    full = char_ink(p["item"]["chars"], p["item"]["comps"])  # the whole box: steadier baseline
    shift = len(full) - len(chs)
    up = {j - shift for j in raised(full) if j > shift}  # never the option's first char
    if not up:
        return text
    out, k, run = [], 0, []
    for ch in text:
        if ch == " ":
            if run:
                out.append(sup(run))
                run = []
            out.append(ch)
            continue
        if k in up:
            run.append(ch)
        else:
            if run:
                out.append(sup(run))
                run = []
            out.append(ch)
        k += 1
    if run:
        out.append(sup(run))
    return "".join(out)


def sup(chars):
    e = "".join(chars)
    return "^" + (e if len(e) == 1 or e.isdigit() or re.fullmatch(r"[-−]\d+", e) else f"({e})")


def unicode_sup(text):
    return SUP_RUN.sub(lambda m: sup(list(m.group(0).translate(SUPERSCRIPTS))), text)


def box_superscript(prev, p):
    """Piece p is a small raised box right after prev: an exponent in its own box."""
    if not prev["text"].strip() or not re.fullmatch(r"[0-9a-z+\-−]{1,3}", p["text"].strip()):
        return False
    if not (0 <= p["x0"] - prev["x1"] <= 0.5 * prev["h"]):
        return False
    return p["h"] < BOX_SUP_SMALL * prev["h"] and p["item"]["y1"] < prev["item"]["y1"] - 0.25 * prev["h"]


# --- Rendering an option -----------------------------------------------------------

def render(pieces, fractions, tall, exponents):
    groups = group_stacks(pieces) if fractions else [[p] for p in pieces]
    parts, prev = [], None
    for g in groups:
        if len(g) == 2:
            upper, lower = sorted(g, key=lambda p: p["y"])
            num = with_exponents(upper) if exponents else upper["text"]
            den = with_exponents(lower) if exponents else lower["text"]
            parts.append(frac(num, strip_bar(den, lower, upper)))
            prev = None
            continue
        p = g[0]
        bar = p["item"]["bar"]
        if tall and bar and bar.get("halves") and bar["ratio"] > BAR_RATIO \
                and all(h.strip() and len(h.strip()) <= STACK_MAXLEN and OPERAND.match(h.strip()) for h in bar["halves"]) \
                and p["text"] == p["item"]["text"]:  # a whole box, never the rest of a label box
            parts.append(frac(*bar["halves"]))
        elif exponents and prev is not None and box_superscript(prev, p):
            parts[-1] = parts[-1] + sup(list(p["text"].strip()))
        else:
            parts.append(with_exponents(p) if exponents else p["text"])
        prev = p
    value = " ".join(parts).strip().lstrip(")）] ").strip()
    return unicode_sup(value) if exponents else value


# --- Commands ----------------------------------------------------------------------

def cmd_check(args):
    """With all rules off, parse_options_math must equal parse_options on every row."""
    n = same = 0
    for line in open(args.boxes):
        rec = json.loads(line)
        n += 1
        same += parse_options_math(rec) == parse_options(rec["boxes"])
    print(f"{same} of {n} rows: parse_options_math (rules off) == parse_options")
    return same == n


def selftest():
    def box(x, y, w, h):
        return [[x, y], [x + w, y], [x + w, y + h], [x, y + h]]

    def rec(entries):
        """entries: (x, y, w, h, text, chars or None, bar or None)."""
        return {"boxes": [[box(x, y, w, hh), t, 1.0] for x, y, w, hh, t, _, _ in entries],
                "chars": [c for *_, c, _ in entries], "bars": [b for *_, b in entries]}

    def chars_of(text, x, top, bottom, raised_idx=(), low_idx=()):
        out, k = [], 0
        for ch in text:
            if ch == " ":
                x += 6
                continue
            t, b = top, bottom
            if k in raised_idx:
                t, b = top - 8, bottom - 14   # small and high
            if k in low_idx:
                t, b = top + 10, bottom + 6   # small and low (subscript)
            out.append([ch, x, x + 10, t, b])
            x += 12
            k += 1
        return out

    row = [(0, 0, 20, 30, "A)", None, None), (100, 0, 20, 30, "B) 2", None, None),
           (200, 0, 20, 30, "C) 3", None, None), (300, 0, 20, 30, "D) 4", None, None),
           (400, 0, 20, 30, "E) 5", None, None)]
    # A: stacked pair "7" above "10" -> 7/10; rules off -> "10 7" like parse_options
    r = rec(row + [(30, 18, 24, 26, "10", None, None), (32, -16, 14, 26, "7", None, None)])
    assert parse_options_math(r)["A"] == parse_options(r["boxes"])["A"] == "10 7"
    assert parse_options_math(r, fractions=True)["A"] == "7/10"
    # the denominator box swallowed the bar: "15" for 5, box much taller than "8"
    r = rec(row + [(30, 14, 18, 40, "15", None, None), (32, -16, 14, 28, "8", None, None)])
    assert parse_options_math(r, fractions=True)["A"] == "8/5"
    r = rec(row + [(30, 14, 18, 40, "15", [["1", 30, 48, 0, 0], ["5", 30, 48, 0, 0]], None),
                   (32, -16, 14, 28, "8", None, None)])
    assert parse_options_math(r, fractions=True)["A"] == "8/5"
    r = rec(row + [(30, 14, 30, 40, "10", [["1", 30, 44, 0, 0], ["0", 44, 58, 0, 0]], None),
                   (32, -16, 28, 28, "7", None, None)])
    assert parse_options_math(r, fractions=True)["A"] == "7/10"
    r = rec(row + [(30, -10, 20, 28, "1", None, None), (30, 6, 20, 6, "–", None, None),
                   (30, 10, 20, 28, "π", None, None)])
    assert parse_options_math(r, fractions=True)["A"] == "1/π"
    # a real "10" under a "7": tall too, but twice as wide, so the 1 stays
    r = rec(row + [(30, 14, 30, 40, "10", None, None), (32, -16, 14, 28, "7", None, None)])
    assert parse_options_math(r, fractions=True)["A"] == "7/10"
    # a label box with nothing after it is never split as a tall box
    lab = {"y": 15, "ratio": 0.5, "halves": ["D)", ")"]}
    r = rec([(0, 0, 20, 30, "A) 1", None, None), (100, 0, 20, 30, "B) 2", None, None),
             (200, 0, 20, 30, "C) 3", None, None), (300, -20, 20, 70, "D)", None, lab),
             (330, 0, 20, 30, "4", None, None), (400, 0, 20, 30, "E) 5", None, None)])
    assert parse_options_math(r, tall=True)["D"] == "4"
    r = rec(row + [(30, 18, 24, 30, "18", None, None), (32, -16, 14, 28, "5", None, None)])
    assert parse_options_math(r, fractions=True)["A"] == "5/18"
    # two-line option: same x but long words -> not a fraction
    r = rec(row + [(30, 18, 200, 26, "the second line of words", None, None),
                   (30, -16, 200, 26, "first line of the option", None, None)])
    assert "/" not in parse_options_math(r, fractions=True)["A"]
    # B: tall box with a bar, and without
    bar = {"y": 15, "ratio": 0.9, "halves": ["p+3q", "4"]}
    r = rec(row + [(30, -20, 40, 70, "p+ 3q 4", None, bar)])
    assert parse_options_math(r, tall=True)["A"] == "(p+3q)/4"
    r = rec(row + [(30, -20, 40, 70, "p+ 3q 4", None, {"y": 15, "ratio": 0.2, "halves": None})])
    assert parse_options_math(r, tall=True)["A"] == "p+ 3q 4"
    # E: raised 3 after n -> n^3; label chars on the baseline help the baseline
    text = "A) n3 – 2"
    r = rec([(0, 0, 120, 30, text, chars_of(text, 0, 2, 28, raised_idx={3}), None)] + row[1:])
    assert parse_options_math(r, exponents=True)["A"] == "n^3 – 2"
    assert parse_options_math(r)["A"] == "n3 – 2"
    # multi-digit exponent and subscripts that must stay
    text = "A) 201615"
    r = rec([(0, 0, 120, 30, text, chars_of(text, 0, 2, 28, raised_idx={6, 7}), None)] + row[1:])
    assert parse_options_math(r, exponents=True)["A"] == "2016^15"
    text = "A) g5(x) = x2"
    r = rec([(0, 0, 160, 30, text, chars_of(text, 0, 2, 28, raised_idx={9}, low_idx={3}), None)] + row[1:])
    assert parse_options_math(r, exponents=True)["A"] == "g5(x) = x^2"
    # degree sign and a plain number are untouched; Unicode superscripts convert
    text = "A) 45°"
    r = rec([(0, 0, 80, 30, text, chars_of(text, 0, 2, 28, raised_idx={4}), None)] + row[1:])
    assert parse_options_math(r, exponents=True)["A"] == "45°"
    r = rec([(0, 0, 80, 30, "A) 6 cm²", None, None)] + row[1:])
    assert parse_options_math(r, exponents=True)["A"] == "6 cm^2"
    assert frac("1", "π") == "1/π" and frac("2p+q", "3") == "(2p+q)/3"
    assert sup(list("n+1")) == "^(n+1)" and sup(list("-1")) == "^-1"
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selftest", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    c = sub.add_parser("check")
    c.add_argument("boxes")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if args.cmd == "check":
        sys.exit(0 if cmd_check(args) else 1)


if __name__ == "__main__":
    main()
