#!/usr/bin/env python3
"""Score ways to read the five answer options, checked across languages.

Experiment: docs/experiments/2026-11-option-extraction-consensus.md

Every M3Kang problem (`id`) is in many languages, and the correct letter (`label`) is
the same in all of them, so the order A..E is the same. A number, a formula or a
unit does not change with the language. So the option "C" of one row should match
the option "C" of the same problem in the other languages, after a normalization
(decimal comma, minus sign, superscripts, thousands separators, units).

pilot        parse success per language for one box file.
gold-pick    choose the gold sample (fixed seed) and write option-band sheets to
             transcribe by hand. It prints no option value.
score        score the arms: coverage, format checks, agreement with the other
             languages, and accuracy on the gold sample.
repair       write the options of arm 7 (cross-language repair) as JSONL.
by-level     coverage, format checks and likely fractions per difficulty level
             (lvl-0 is grade 5), and accuracy on the gold sample per level.

It prints counts only: M3Kang is research-use only, so the box files, the gold
file and every output stay under data/ (gitignored).

Usage (the .venv of the repository: pyarrow and Pillow):
    python laptop/option_consensus.py --selftest
    python laptop/option_consensus.py score
"""
import argparse
import glob
import io
import json
import math
import os
import random
import re
import sys
import unicodedata
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from prepare_m3kang import LETTERS, is_marker, parse_options  # noqa: E402

DIR = "data/interim/optx"
BOXES = {"v4": f"{DIR}/boxes_all_v4.jsonl", "v5": f"{DIR}/boxes_all_v5.jsonl"}
PARQUETS = "data/raw_txto_yes/*.parquet"
GOLD_PICK = f"{DIR}/gold_pick.json"
GOLD = f"{DIR}/options_gold.json"
NON_LATIN = {"zho", "jpn", "kor", "arb"}
MAX_LEN = 40

# --- Normalization ----------------------------------------------------------

SUPER = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻", "0123456789+-")
SUPER_RUN = re.compile(r"[⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻]+")
DASHES = str.maketrans({"−": "-", "–": "-", "—": "-", "‐": "-", "‑": "-"})
UNITS = ["km", "cm", "mm", "dm", "m", "kg", "g", "ml", "l", "min", "h", "s", "€", "$", "%", "°",
         "euros", "euro", "eur"]
UNIT_RE = re.compile(r"(?<![a-z])(" + "|".join(re.escape(u) for u in UNITS) + r")(\^?[23])?(?![a-z])")
THOUSANDS = re.compile(r"^-?\d{1,3}([ .,'  ])\d{3}(\1\d{3})*$")
TWO_NUMBERS = re.compile(r"^\s*\d+\s+\d+\s*$")  # two bare numbers: a stacked fraction?


def basic(value):
    """Superscripts to ^n, NFKC, one kind of dash, lower case, single spaces."""
    value = SUPER_RUN.sub(lambda m: "^" + m.group(0).translate(SUPER), value)
    value = unicodedata.normalize("NFKC", value).translate(DASHES)
    return re.sub(r"\s+", " ", value).strip().lower()


def canon(value):
    """Language-free form of an option, or None when it holds words.

    Returns (strict, tolerant): tolerant reads a fraction a/b or a stacked pair "a b"
    as the unordered pair {a, b}, because OCR sometimes swaps the two numbers.
    """
    v = basic(value)
    v = UNIT_RE.sub(" ", v).strip()
    if THOUSANDS.match(v):
        v = re.sub(r"[ .,'  ]", "", v)
    v = re.sub(r"(?<=\d),(?=\d)", ".", v)  # decimal comma
    pair = re.fullmatch(r"(\d+)\s*/\s*(\d+)|(\d+) (\d+)", v)
    strict = v.replace(" ", "")
    if not strict or not re.search(r"\d", strict) and not re.fullmatch(r"[a-z]([-+*/^][a-z0-9]+)+", strict):
        return None
    if re.search(r"[a-z]{2,}", strict.replace("π", "")):  # a word, not a variable
        return None
    if not re.fullmatch(r"[0-9a-z+\-*/^().=×·:√π<>≤≥,]+", strict):
        return None
    tolerant = strict
    if pair:
        a, b = (pair.group(1), pair.group(2)) if pair.group(1) else (pair.group(3), pair.group(4))
        tolerant = "{" + ",".join(sorted([a, b])) + "}"
    return strict, tolerant


def kind(value):
    v = basic(value)
    if canon(value) is not None:
        return "math"
    if re.search(r"[a-zà-ÿ]{2,}", v):
        return "text"
    return "other"


# --- Format checks ----------------------------------------------------------

LABEL_INSIDE = re.compile(r"(?:^|\s)[A-E]\s?[\)）\]](?:\s|$)|^[A-E][:.]\s")
GREEK_CYR = re.compile(r"[Ͱ-ορ-ϿЀ-ӿ]")  # Greek without π, Cyrillic


def option_flags(value):
    """Format checks that one option fails (a set of names)."""
    flags = set()
    if not value.strip():
        flags.add("empty")
    if LABEL_INSIDE.search(value):
        flags.add("label_inside")
    if len(value) > MAX_LEN:
        flags.add("too_long")
    if "$" in value and not re.search(r"\d\s*\$|\$\s*\d", value) or re.search(r"(?<![\d\s])°|^°", value) \
            or re.search(r"\d", value) and GREEK_CYR.search(value):
        flags.add("junk")
    return flags


def row_flags(opts):
    """Format checks that a row fails. {} counts as 'incomplete' only."""
    if len(opts) != 5 or not all(opts.get(k, "").strip() for k in LETTERS):
        return {"incomplete"}
    flags = set()
    for k in LETTERS:
        flags |= option_flags(opts[k])
    normed = [basic(opts[k]).replace(" ", "") for k in LETTERS]
    if len(set(normed)) < 5:
        flags.add("duplicate")
    kinds = Counter(kind(opts[k]) for k in LETTERS)
    if kinds.most_common(1)[0][1] < 4:
        flags.add("mixed_kind")
    return flags


# --- Parsers ----------------------------------------------------------------

def rows_order(boxes):
    """reading_order of prepare_m3kang.py, keeping the row index of each box."""
    items = []
    for box, text, _score in boxes:
        ys = [pt[1] for pt in box]
        xs = [pt[0] for pt in box]
        items.append({"x": min(xs), "y": (min(ys) + max(ys)) / 2, "h": max(ys) - min(ys), "text": text})
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


def parse_lines(boxes):
    """parse_options, but a value takes only boxes on its label's row or the row below."""
    items = rows_order(boxes)
    strict = [i for i, it in enumerate(items) if is_marker(it["text"], "A", strict=True) is not None]
    loose = [i for i, it in enumerate(items)
             if i not in strict and is_marker(it["text"], "A", strict=False) is not None]
    for strict_a, starts in ((True, strict), (False, loose)):
        for start in reversed(starts):
            options = read_sequence_lines(items, start, strict_a)
            if len(options) == 5:
                cleaned = {k: " ".join(v).strip().lstrip(")）] ").strip() for k, v in options.items()}
                if all(cleaned.values()):
                    return cleaned
                return {}
    return {}


def read_sequence_lines(items, start, strict_a):
    """read_sequence of prepare_m3kang.py with a row limit on the values."""
    options, current, label_row = {}, None, None
    expected = iter(LETTERS)
    letter = next(expected)
    for item in items[start:]:
        text = item["text"]
        rest = is_marker(text, letter, strict=(strict_a and letter == "A")) if letter else None
        if rest is None and letter == "C":
            d_rest = is_marker(text, "D", strict=False)
            values = [v for v in options.get("B", []) if v.strip()]
            if d_rest is not None and len(values) == 2:
                options["B"], options["C"] = [values[0]], [values[1]]
                letter, rest = "D", d_rest
                next(expected)
        if rest is not None:
            current, label_row = letter, item["row"]
            options[current] = [rest]
            letter = next(expected, None)
        elif current and item["row"] <= label_row + 1:
            options[current].append(text)
    return options


# --- Data -------------------------------------------------------------------

def load_meta():
    import pyarrow.parquet as pq
    meta = {}
    for path in sorted(glob.glob(PARQUETS)):
        t = pq.read_table(path, columns=["id", "language", "label"])
        for i, lang, label in zip(*(t.column(c).to_pylist() for c in ("id", "language", "label"))):
            meta[f"{i}|{lang}"] = {"id": i, "lang": lang, "label": label, "path": path}
    return meta


def load_boxes(path):
    return {r["key"]: r["boxes"] for r in map(json.loads, open(path))}


def build_arms(boxes, keys):
    """Arms 1-5: one dict key -> options each. None of them looks at other languages."""
    p = {e: {k: parse_options(boxes[e].get(k, [])) for k in keys} for e in ("v4", "v5")}
    pl = {e: {k: parse_lines(boxes[e].get(k, [])) for k in keys} for e in ("v4", "v5")}
    arms = {
        "1 v4": p["v4"],
        "2 v5": p["v5"],
        "3 v5>v4 (baseline)": {k: p["v5"][k] or p["v4"][k] for k in keys},
        "4a v4 lines": pl["v4"],
        "4b v5 lines": pl["v5"],
        "4c v5>v4 lines": {k: pl["v5"][k] or pl["v4"][k] for k in keys},
        "5 v5>v4 format fusion": {k: format_fusion(p["v5"][k], p["v4"][k]) for k in keys},
    }
    return arms, p


def format_fusion(o5, o4):
    """v5 per option; take v4's option where v5's fails a format check and v4's passes."""
    if not o5:
        return o4
    if not o4:
        return o5
    out = dict(o5)
    for k in LETTERS:
        if option_flags(out[k]) and not option_flags(o4[k]):
            out[k] = o4[k]
    normed = [basic(out[k]).replace(" ", "") for k in LETTERS]
    for k, n in zip(LETTERS, normed):
        if normed.count(n) > 1:
            alt = basic(o4[k]).replace(" ", "")
            if alt not in normed and not option_flags(o4[k]):
                out[k] = o4[k]
                normed = [basic(out[x]).replace(" ", "") for x in LETTERS]
    return out


# --- Cross-language reference -----------------------------------------------

def votes_by_problem(p, meta, keys, which=1):
    """id -> letter -> lang -> set of canon values (both engines vote); which: 0 strict, 1 tolerant."""
    votes = defaultdict(lambda: defaultdict(dict))
    for k in keys:
        m = meta[k]
        for letter in LETTERS:
            vals = set()
            for e in ("v4", "v5"):
                v = p[e][k].get(letter)
                c = canon(v) if v else None
                if c:
                    vals.add(c[which])
            if vals:
                votes[m["id"]][letter][m["lang"]] = vals
    return votes


def reference(votes, pid, letter, lang, min_others=3):
    """Leave-one-language-out: (support Counter, number of other languages) or None."""
    others = {l: v for l, v in votes[pid][letter].items() if l != lang}
    if len(others) < min_others:
        return None
    support = Counter(x for vals in others.values() for x in vals)
    return support, len(others)


def check_row(opts, votes, meta_k, which=1):
    """Per option: 'agree', 'disagree' or None (words, or too few other languages)."""
    out = {}
    for letter in LETTERS:
        v = opts.get(letter)
        c = canon(v) if v else None
        ref = reference(votes, meta_k["id"], letter, meta_k["lang"]) if c else None
        if ref is None:
            out[letter] = None
            continue
        support, _ = ref
        top = max(support.values())
        out[letter] = "agree" if support.get(c[which], 0) == top else "disagree"
    return out


def strict_only_agree(opts, votes, votes_strict, meta_k):
    """Options that agree with the pair tolerance and disagree without it."""
    tolerant = check_row(opts, votes, meta_k, 1)
    strict = check_row(opts, votes_strict, meta_k, 0)
    return sum(tolerant[x] == "agree" and strict[x] == "disagree" for x in LETTERS)


# --- Arms 6 and 7: they use the other languages, score them on gold only ----

def consensus_select(p, votes, meta, keys):
    out = {}
    for k in keys:
        best, best_score = p["v5"][k] or p["v4"][k], -1
        for e in ("v5", "v4"):  # ties keep v5
            o = p[e][k]
            if not o:
                continue
            score = sum(x == "agree" for x in check_row(o, votes, meta[k]).values())
            if score > best_score:
                best, best_score = o, score
        out[k] = best
    return out


def repair(base, p, votes, meta, keys, share=0.8, min_others=5):
    """Replace an option that disagrees with a clear majority of the other languages."""
    raw = defaultdict(Counter)  # (id, letter, tolerant canon) -> raw forms seen
    for k in keys:
        for e in ("v4", "v5"):
            for letter, v in p[e][k].items():
                c = canon(v)
                if c:
                    raw[(meta[k]["id"], letter, c[1])][v.strip()] += 1
    out, changed = {}, 0
    for k in keys:
        o = dict(base[k])
        for letter in list(o):
            c = canon(o[letter])
            if not c:
                continue
            ref = reference(votes, meta[k]["id"], letter, meta[k]["lang"], min_others)
            if not ref:
                continue
            support, n = ref
            ranked = sorted(support.items(), key=lambda kv: (-kv[1], kv[0]))
            value, top = ranked[0]
            if len(ranked) > 1 and ranked[1][1] == top:
                continue  # a tie: no clear majority
            if top / n >= share and c[1] != value:
                forms = raw[(meta[k]["id"], letter, value)]
                o[letter] = sorted(forms.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
                changed += 1
        out[k] = o
    return out, changed


# --- Statistics -------------------------------------------------------------

def cluster_ci(values, clusters, n_boot=1000, seed=0):
    """95% bootstrap interval of a mean, resampling whole problems."""
    by = defaultdict(list)
    for v, c in zip(values, clusters):
        by[c].append(v)
    groups = list(by.values())
    rng = random.Random(seed)
    means = []
    for _ in range(n_boot):
        s = n = 0
        for g in (groups[rng.randrange(len(groups))] for _ in groups):
            s += sum(g)
            n += len(g)
        means.append(s / n)
    means.sort()
    return means[int(0.025 * n_boot)], means[int(0.975 * n_boot) - 1]


def mcnemar(a, b):
    """Exact two-sided McNemar p-value for paired booleans."""
    n01 = sum(x and not y for x, y in zip(a, b))
    n10 = sum(y and not x for x, y in zip(a, b))
    n = n01 + n10
    if n == 0:
        return n01, n10, 1.0
    k = min(n01, n10)
    p = 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return n01, n10, min(1.0, p)


# --- Gold -------------------------------------------------------------------

def gold_norm(value):
    v = basic(value or "").replace(" ", "")
    return re.sub(r"(?<=\d),(?=\d)", ".", v)


def gold_lenient(value):
    """Value without unit; one sign for products (×, ·, *, x between digits)."""
    c = canon(value or "")
    v = c[0] if c else gold_norm(value)
    return re.sub(r"(?<=\d)x(?=\d)", "*", v.replace("×", "*").replace("·", "*"))


def gold_scores(arm, gold, lenient=False):
    same = (lambda a, b: gold_lenient(a) == gold_lenient(b)) if lenient else \
        (lambda a, b: gold_norm(a) == gold_norm(b))
    rows = opts = rows_ok = opts_ok = 0
    for k, g in gold.items():
        o = arm.get(k, {})
        rows += 1
        ok = 0
        for letter in LETTERS:
            opts += 1
            ok += bool(o.get(letter)) and same(o.get(letter), g[letter])
        opts_ok += ok
        rows_ok += ok == 5
    return rows_ok, rows, opts_ok, opts


# --- Commands ---------------------------------------------------------------

def cmd_pilot(args):
    boxes = load_boxes(args.boxes)
    ok, n = Counter(), Counter()
    for k, b in boxes.items():
        lang = k.split("|")[1]
        n[lang] += 1
        ok[lang] += bool(parse_options(b))
    print(f"{sum(ok.values())} of {sum(n.values())} rows have five options, {len(n)} languages")
    print("languages with a failure:", ", ".join(f"{l} {n[l] - ok[l]}/{n[l]}" for l in sorted(n) if ok[l] < n[l]))


def cmd_gold_pick(args):
    from PIL import Image, ImageDraw
    import pyarrow.parquet as pq

    meta = load_meta()
    boxes = {e: load_boxes(path) for e, path in BOXES.items()}
    keys = sorted(k for k in meta if k in boxes["v4"] and k in boxes["v5"])
    p = {e: {k: parse_options(boxes[e][k]) for k in keys} for e in ("v4", "v5")}
    rng = random.Random(args.seed)
    by_lang = defaultdict(list)
    for k in keys:
        by_lang[meta[k]["lang"]].append(k)
    langs = sorted(by_lang)
    rng.shuffle(langs)
    pick = [(rng.choice(by_lang[l]), "random") for l in langs[:args.random]]
    taken = {k for k, _ in pick}
    differ = [k for k in keys if p["v4"][k] and p["v5"][k] and k not in taken
              and any(gold_norm(p["v4"][k][x]) != gold_norm(p["v5"][k][x]) for x in LETTERS)]
    fallback = [k for k in keys if p["v4"][k] and not p["v5"][k] and k not in taken]
    pick += [(k, "v4_v5_differ") for k in rng.sample(differ, args.differ)]
    pick += [(k, "v4_fallback") for k in rng.sample(fallback, args.fallback)]
    rng.shuffle(pick)
    json.dump([{"n": n, "key": k, "stratum": s} for n, (k, s) in enumerate(pick)], open(GOLD_PICK, "w"), indent=1)
    print(f"{len(pick)} rows: {Counter(s for _, s in pick)}; strata sizes: differ {len(differ)}, fallback {len(fallback)}")

    # Sheets: the bottom part of each image, where the options are. No engine text.
    os.makedirs(f"{DIR}/gold_sheets", exist_ok=True)
    wanted = defaultdict(list)
    for n, (k, _) in enumerate(pick):
        wanted[meta[k]["path"]].append((n, k))
    crops = {}
    for path, items in wanted.items():
        t = pq.read_table(path, columns=["id", "language", "image"])
        index = {f"{i}|{l}": j for j, (i, l) in enumerate(zip(t.column("id").to_pylist(), t.column("language").to_pylist()))}
        for n, k in items:
            img = Image.open(io.BytesIO(t.column("image")[index[k]].as_py()["bytes"])).convert("RGB")
            w, h = img.size
            # Top of the last "A" label, minus room for a stacked fraction above it.
            labels = [(min(pt[1] for pt in b), max(pt[1] for pt in b)) for e in ("v5", "v4")
                      for b, txt, _ in boxes[e][k] if is_marker(txt, "A", strict=False) is not None]
            if labels:
                y0, y1 = max(labels)
                top = max(0, int(y0 - max(0.04 * h, 2.5 * (y1 - y0))))
            else:
                top = 0
            crop = img.crop((0, top, w, h))
            if crop.width > 1400:
                crop = crop.resize((1400, int(crop.height * 1400 / crop.width)))
            crops[n] = crop
    for s in range(0, len(pick), args.per_sheet):
        group = [crops[n] for n in range(s, min(s + args.per_sheet, len(pick)))]
        width = max(c.width for c in group)
        sheet = Image.new("RGB", (width, sum(c.height + 40 for c in group)), "white")
        y = 0
        draw = ImageDraw.Draw(sheet)
        for j, c in enumerate(group):
            draw.rectangle((0, y, width, y + 36), fill=(255, 230, 150))
            draw.text((8, y + 8), f"#{s + j}", fill="black")
            sheet.paste(c, (0, y + 40))
            y += c.height + 40
        sheet.save(f"{DIR}/gold_sheets/sheet_{s // args.per_sheet:02d}.png")
    print(f"sheets in {DIR}/gold_sheets")


def summarize(name, arm, keys, meta, votes, flags_cache, show_fmt=True):
    valid, verified, checkable, fmt_ok, cov = [], 0, 0, 0, 0
    agree = disagree = 0
    for k in keys:
        o = arm[k]
        f = flags_cache.setdefault((name, k), row_flags(o))
        complete = "incomplete" not in f
        cov += complete
        fmt_ok += not f
        chk = check_row(o, votes, meta[k]) if complete else {}
        a = sum(x == "agree" for x in chk.values())
        d = sum(x == "disagree" for x in chk.values())
        agree += a
        disagree += d
        checkable += (a + d) > 0
        verified += a == 5
        valid.append(not f and d == 0)
    return {"cov": cov, "fmt_ok": fmt_ok, "valid": valid, "verified": verified,
            "checkable": checkable, "agree": agree, "disagree": disagree}


def cmd_score(args):
    meta = load_meta()
    boxes = {e: load_boxes(path) for e, path in BOXES.items()}
    keys = sorted(k for k in meta if k in boxes["v4"] and k in boxes["v5"])
    if args.languages:
        keys = [k for k in keys if meta[k]["lang"] in args.languages.split(",")]
    if args.shard0:
        keys = [k for k in keys if meta[k]["path"].endswith("00000-of-00004.parquet")]
    strata = {"latin": [k for k in keys if meta[k]["lang"] not in NON_LATIN],
              "non-latin": [k for k in keys if meta[k]["lang"] in NON_LATIN]}
    print(f"{len(keys)} rows with boxes from both engines (of {len(meta)} in txto_yes); "
          f"latin {len(strata['latin'])}, non-latin {len(strata['non-latin'])}; "
          f"{len({meta[k]['id'] for k in keys})} problems")

    arms, p = build_arms(boxes, keys)
    votes = votes_by_problem(p, meta, keys)  # fixed reference for every arm
    arms["6 consensus select"] = consensus_select(p, votes, meta, keys)
    arms["7 repair (on 3)"], changed = repair(arms["3 v5>v4 (baseline)"], p, votes, meta, keys)
    uses_consensus = {"6 consensus select", "7 repair (on 3)"}

    # Share of options that the cross-language check can cover (latin rows).
    lat = strata["latin"]
    votes_strict = votes_by_problem(p, meta, keys, which=0)
    inv = sum(1 for k in lat for v in arms["3 v5>v4 (baseline)"][k].values() if canon(v))
    tot = sum(len(arms["3 v5>v4 (baseline)"][k]) for k in lat)
    print(f"latin, baseline: {inv} of {tot} options ({100 * inv / max(tot, 1):.1f}%) are language-free "
          f"(numbers, formulas, units) and can be checked; repair changed {changed} options")

    base = "3 v5>v4 (baseline)"
    flags_cache = {}
    results = {}
    for sname, skeys in strata.items():
        if not skeys:
            continue
        clusters = [meta[k]["id"] for k in skeys]
        print(f"\n== {sname}: {len(skeys)} rows ==")
        print(f"{'arm':24}{'5 opts':>8}{'format ok':>10}{'checkable':>10}{'opt agree':>10}"
              f"{'5/5 agree':>10}{'VALID':>8}{'95% CI':>16}{'vs base':>18}")
        for name, arm in arms.items():
            results[(sname, name)] = summarize(name, arm, skeys, meta, votes, flags_cache)
        for name, arm in arms.items():
            s = results[(sname, name)]
            n = len(skeys)
            if name in uses_consensus:
                print(f"{name:24}{100 * s['cov'] / n:7.1f}%{100 * s['fmt_ok'] / n:9.1f}%"
                      f"{'(scored on gold only)':>40}")
                continue
            lo, hi = cluster_ci([float(v) for v in s["valid"]], clusters)
            n01, n10, pv = mcnemar(s["valid"], results[(sname, base)]["valid"])
            ag = s["agree"] / max(s["agree"] + s["disagree"], 1)
            print(f"{name:24}{100 * s['cov'] / n:7.1f}%{100 * s['fmt_ok'] / n:9.1f}%"
                  f"{100 * s['checkable'] / n:9.1f}%{100 * ag:9.1f}%{100 * s['verified'] / n:9.1f}%"
                  f"{100 * sum(s['valid']) / n:7.1f}%  [{100 * lo:5.1f},{100 * hi:5.1f}]"
                  f"  +{n01:<4}-{n10:<4}p={pv:.3f}")

    # Format checks: share of complete baseline rows that fail each.
    print("\nformat checks failed, latin rows with five options (a row can fail several):")
    for name in ("1 v4", "2 v5", base, "4c v5>v4 lines", "5 v5>v4 format fusion"):
        fl = Counter(x for k in lat for x in flags_cache[(name, k)] if "incomplete" not in flags_cache[(name, k)])
        n5 = sum("incomplete" not in flags_cache[(name, k)] for k in lat)
        multi = sum(len(flags_cache[(name, k)]) > 1 for k in lat if "incomplete" not in flags_cache[(name, k)])
        print(f"  {name:24}rows {n5}  " + "  ".join(f"{f} {fl[f]} ({100 * fl[f] / max(n5, 1):.1f}%)"
                                         for f in ("empty", "label_inside", "too_long", "junk", "duplicate", "mixed_kind"))
              + f"  2+ checks {multi}")
    pair = re.compile(r"^\s*\d+\s+\d+\s*$")
    for name in (base, "5 v5>v4 format fusion"):
        n = sum(any(pair.match(v) and not THOUSANDS.match(basic(v)) for v in arms[name][k].values()) for k in lat)
        print(f"post-hoc, latin: {name}: {n} rows with an option that is two bare numbers (a stacked fraction?)")
    lens = sorted(len(v) for k in lat for v in arms[base][k].values())
    if lens:
        print(f"option length, latin, baseline: p99 {lens[int(0.99 * len(lens))]}, max {lens[-1]} (limit {MAX_LEN})")
    tol = sum(strict_only_agree(arms[base][k], votes, votes_strict, meta[k]) for k in lat)
    print(f"latin, baseline options that agree with the pair rule and disagree without it: {tol}")

    # Sensitivity (post-hoc): VALID with "two bare numbers" as a format failure,
    # and VALID without the unordered-pair fraction tolerance.
    print("\nsensitivity, latin rows (post-hoc):")
    for name in (base, "5 v5>v4 format fusion"):
        v = results[("latin", name)]["valid"]
        no_pair = [ok and not any(pair.match(x) and not THOUSANDS.match(basic(x)) for x in arms[name][k].values())
                   for ok, k in zip(v, lat)]
        strict = [not flags_cache[(name, k)] and "disagree" not in check_row(arms[name][k], votes_strict, meta[k], 0).values()
                  for k in lat]
        print(f"  {name:24} VALID {100 * sum(v) / len(lat):.1f}%  pair flag counted {100 * sum(no_pair) / len(lat):.1f}%"
              f"  no pair tolerance {100 * sum(strict) / len(lat):.1f}%  both {100 * sum(a and b for a, b in zip(no_pair, strict)) / len(lat):.1f}%")

    # What arm 5 changed (latin rows), checked against the other languages.
    sw = Counter()
    for k in lat:
        a, b = arms[base][k], arms["5 v5>v4 format fusion"][k]
        if not a:
            continue
        chk = check_row(b, votes, meta[k])
        for letter in LETTERS:
            if a[letter] != b[letter]:
                sw["swapped"] += 1
                sw[str(chk[letter])] += 1
    print(f"latin: arm 5 swapped {sw['swapped']} options: agree {sw['agree']}, disagree {sw['disagree']}, not checkable {sw['None']}")

    # Per language (latin), baseline and best non-consensus arms.
    if args.per_language:
        print("\nVALID by language (latin):")
        names = ("2 v5", base, "4c v5>v4 lines", "5 v5>v4 format fusion")
        print(f"{'lang':6}{'rows':>6}" + "".join(f"{n[:14]:>16}" for n in names))
        by = defaultdict(list)
        for k in strata["latin"]:
            by[meta[k]["lang"]].append(k)
        idx = {k: i for i, k in enumerate(strata["latin"])}
        for lang in sorted(by, key=lambda l: -len(by[l])):
            ks = by[lang]
            cells = []
            for name in names:
                v = results[("latin", name)]["valid"]
                cells.append(100 * sum(v[idx[k]] for k in ks) / len(ks))
            print(f"{lang:6}{len(ks):>6}" + "".join(f"{c:15.1f}%" for c in cells))

    # Gold.
    if os.path.exists(GOLD):
        gold = {g["key"]: g["options"] for g in json.load(open(GOLD)) if g.get("options")}
        strata_of = {g["key"]: g["stratum"] for g in json.load(open(GOLD_PICK))}
        print(f"\ngold: {len(gold)} rows, {len({meta[k]['id'] for k in gold})} distinct problems, "
              f"{len({meta[k]['lang'] for k in gold})} languages (Claude, blind to the engines; no person checked)")
        for name in (base, "5 v5>v4 format fusion"):
            ks = list(gold)
            okv = [float(gold_scores(arms[name], {k: gold[k]})[0]) for k in ks]
            lo, hi = cluster_ci(okv, [meta[k]["id"] for k in ks])
            print(f"  {name}: rows fully right {100 * sum(okv) / len(ks):.0f}%, 95% CI by problem [{100 * lo:.0f}, {100 * hi:.0f}]")
        touched = Counter()
        rep = arms["7 repair (on 3)"]
        for k, g in gold.items():
            for letter in LETTERS:
                a, b = arms[base][k].get(letter), rep[k].get(letter)
                if a != b:
                    ra = bool(a) and gold_norm(a) == gold_norm(g[letter])
                    rb = bool(b) and gold_norm(b) == gold_norm(g[letter])
                    touched[f"{'right' if ra else 'wrong'}->{'right' if rb else 'wrong'}"] += 1
        print(f"  repair touched {sum(touched.values())} gold options: {dict(touched)}")
        print(f"{'arm':24}{'rows 5/5':>14}{'options':>16}{'lenient rows':>14}"
              + "".join(f"{s:>16}" for s in ("random", "v4_v5_differ", "v4_fallback")))
        for name, arm in arms.items():
            r_ok, r, o_ok, o = gold_scores(arm, gold)
            l_ok = gold_scores(arm, gold, lenient=True)[0]
            cells = []
            for s in ("random", "v4_v5_differ", "v4_fallback"):
                sub = {k: v for k, v in gold.items() if strata_of.get(k) == s}
                a, b, _, _ = gold_scores(arm, sub)
                cells.append(f"{a}/{b}")
            print(f"{name:24}{f'{r_ok}/{r}':>8} {100 * r_ok / r:4.0f}%{f'{o_ok}/{o}':>10} {100 * o_ok / o:4.0f}%"
                  f"{f'{l_ok}/{r}':>14}" + "".join(f"{c:>16}" for c in cells))
        # Does the cross-language check agree with gold? On the baseline.
        tp = fp = fn = tn = 0
        for k, g in gold.items():
            o = arms[base].get(k, {})
            if not o:
                continue
            chk = check_row(o, votes, meta[k])
            for letter in LETTERS:
                if chk[letter] is None:
                    continue
                right = gold_norm(o[letter]) == gold_norm(g[letter])
                if chk[letter] == "agree":
                    tp += right
                    fp += not right
                else:
                    fn += right
                    tn += not right
        print(f"cross-language check vs gold (baseline, checkable options): agree&right {tp}, "
              f"agree&wrong {fp}, disagree&right {fn}, disagree&wrong {tn}")


def cmd_repair(args):
    meta = load_meta()
    boxes = {e: load_boxes(path) for e, path in BOXES.items()}
    keys = sorted(k for k in meta if k in boxes["v4"] and k in boxes["v5"])
    arms, p = build_arms(boxes, keys)
    votes = votes_by_problem(p, meta, keys)
    out, changed = repair(arms["3 v5>v4 (baseline)"], p, votes, meta, keys)
    with open(args.out, "w") as f:
        for k in keys:
            f.write(json.dumps({"key": k, "options": out[k]}, ensure_ascii=False) + "\n")
    print(f"{len(keys)} rows, {changed} options repaired -> {args.out}")


def cmd_by_level(args):
    """Counts per level, all text-only rows: is OCR worse on harder problems, and why?"""
    meta = load_meta()
    boxes = {e: load_boxes(path) for e, path in BOXES.items()}
    keys = sorted(k for k in meta if k in boxes["v4"] and k in boxes["v5"])
    arms, _ = build_arms(boxes, keys)
    level = lambda k: int(re.match(r"lvl-(\d+)", k).group(1))
    levels = sorted({level(k) for k in keys})
    two = lambda v: bool(TWO_NUMBERS.match(v)) and not THOUSANDS.match(basic(v))
    for name in ("3 v5>v4 (baseline)", "5 v5>v4 format fusion"):
        arm = arms[name]
        print(f"\n== {name}, all {len(keys)} rows ==")
        print(f"{'level':>5}{'rows':>7}{'probs':>6}{'5 opts':>9}{'format ok':>10}{'math opts':>10}"
              f"{'text opts':>10}{'two nums':>10}{'%':>6}")
        tot = 0
        for lv in levels:
            ks = [k for k in keys if level(k) == lv]
            five = [k for k in ks if row_flags(arm[k]) != {"incomplete"}]
            ok = sum(not row_flags(arm[k]) for k in five)
            kinds = Counter(kind(v) for k in ks for v in arm[k].values() if v)
            n_opts = max(sum(kinds.values()), 1)
            n_two = sum(any(two(v) for v in arm[k].values()) for k in ks)
            tot += n_two
            print(f"{lv:>5}{len(ks):>7}{len({meta[k]['id'] for k in ks}):>6}{100 * len(five) / len(ks):8.1f}%"
                  f"{100 * ok / len(ks):9.1f}%{100 * kinds['math'] / n_opts:9.1f}%{100 * kinds['text'] / n_opts:9.1f}%"
                  f"{n_two:>10}{100 * n_two / len(ks):5.1f}%")
        print(f"rows with two bare numbers, all levels: {tot}")
    if os.path.exists(GOLD):
        gold = {g["key"]: g["options"] for g in json.load(open(GOLD)) if g.get("options")}
        print(f"\ngold, {len(gold)} rows (Claude, no person checked; 40 rows chosen as hard cases)")
        print(f"{'level':>5}{'rows':>6}{'base 5/5':>10}{'arm5 5/5':>10}{'fraction':>10}{'exponent':>10}")
        for lv in levels:
            g = {k: v for k, v in gold.items() if level(k) == lv}
            if not g:
                continue
            frac = sum(any("/" in v and not v.lstrip().startswith("{") for v in o.values()) for o in g.values())
            expo = sum(any("^" in basic(v) for v in o.values()) for o in g.values())
            print(f"{lv:>5}{len(g):>6}{gold_scores(arms['3 v5>v4 (baseline)'], g)[0]:>10}"
                  f"{gold_scores(arms['5 v5>v4 format fusion'], g)[0]:>10}{frac:>10}{expo:>10}")


def selftest():
    # Made-up values only.
    assert canon("1,5") == canon("1.5") == ("1.5", "1.5")
    assert canon("−3")[0] == canon("-3")[0] == "-3"
    assert canon("x²")[0] == "x^2" and canon("2⁷")[0] == "2^7"
    assert canon("1 000")[0] == canon("1.000")[0] == canon("1,000")[0] == canon("1'000")[0] == "1000"
    assert canon("12 cm")[0] == canon("12cm")[0] == canon("12")[0] == "12"
    assert canon("20 €")[0] == "20" and canon("45°")[0] == "45" and canon("6 cm²")[0] == "6"
    assert canon("1/14")[1] == canon("14 1")[1] == "{1,14}" and canon("1/14")[0] != canon("14 1")[0]
    assert canon("x + 3")[0] == "x+3" and canon("2π")[0] == "2π"
    assert canon("Anna") is None and canon("b or c") is None and canon("") is None
    assert row_flags({}) == {"incomplete"}
    assert row_flags(dict(zip(LETTERS, ["1", "2", "3", "4", "5"]))) == set()
    assert "duplicate" in row_flags(dict(zip(LETTERS, ["1", "2", "2", "4", "5"])))
    assert "label_inside" in row_flags(dict(zip(LETTERS, ["1", "2 C) 3", "3", "4", "5"])))
    assert "too_long" in row_flags(dict(zip(LETTERS, ["1", "2", "3", "4", "5" * 41])))
    assert "junk" in row_flags(dict(zip(LETTERS, ["1", "2", "15°$", "4", "5"])))
    assert "junk" in row_flags(dict(zip(LETTERS, ["1", "2", "3", "4", "5ω"])))
    assert "junk" not in row_flags(dict(zip(LETTERS, ["π", "2π", "3π", "4π", "5π"])))
    assert "mixed_kind" in row_flags(dict(zip(LETTERS, ["1", "2", "Anna", "Bob", "Carl"])))
    assert "mixed_kind" not in row_flags(dict(zip(LETTERS, ["1", "2", "3", "4", "Anna"])))
    # parse_lines drops a box two rows below the options, parse_options keeps it.
    def b(x, y, t):
        return [[[x, y], [x + 30, y], [x + 30, y + 10], [x, y + 10]], t, 1.0]
    boxes = [b(0, 0, "A) 1"), b(50, 0, "B) 2"), b(100, 0, "C) 3"), b(150, 0, "D) 4"), b(200, 0, "E) 5"),
             b(0, 20, "x"), b(0, 40, "99")]
    assert parse_options(boxes)["E"] == "5 x 99" and parse_lines(boxes)["E"] == "5 x"
    assert mcnemar([1, 1, 0], [1, 0, 0])[:2] == (1, 0)
    assert gold_lenient("3x3") == gold_lenient("3×3") and gold_lenient("12") == gold_lenient("12 €")
    assert gold_norm("{2,3, 5,7}") == gold_norm("{2,3,5,7}")
    assert gold_norm("7,5 m") == gold_norm("7.5m") and gold_norm("cm³") == gold_norm("cm^3")
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selftest", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    s = sub.add_parser("pilot")
    s.add_argument("boxes")
    s = sub.add_parser("gold-pick")
    s.add_argument("--seed", type=int, default=7)
    s.add_argument("--random", type=int, default=60)
    s.add_argument("--differ", type=int, default=20)
    s.add_argument("--fallback", type=int, default=20)
    s.add_argument("--per-sheet", type=int, default=5)
    s = sub.add_parser("score")
    s.add_argument("--languages", help="only these languages (comma list)")
    s.add_argument("--shard0", action="store_true", help="only the first parquet file")
    s.add_argument("--per-language", action="store_true")
    s = sub.add_parser("repair")
    s.add_argument("--out", default=f"{DIR}/options_repaired.jsonl")
    sub.add_parser("by-level")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    {"pilot": cmd_pilot, "gold-pick": cmd_gold_pick, "score": cmd_score, "repair": cmd_repair,
     "by-level": cmd_by_level}[args.cmd](args)


if __name__ == "__main__":
    main()
