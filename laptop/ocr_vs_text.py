#!/usr/bin/env python3
"""Score OCR engines against the annotated question text of M3Kang.

M3Kang gives the question as text (column `text`) and the same question inside
the image. This script compares the OCR text of the image with that text and
reports the character error rate (CER) and word error rate (WER) per language
and engine. It does not run OCR: it reads the boxes saved by ocr_boxes.py dump.

For each row:
- OCR text = the boxes in reading order, cut before the first "A)" label
  (the options are not in `text`),
- both sides are normalized: NFC, spaces collapsed, leading problem number removed.

Metrics (edit distance divided by the length of the reference):
    cer        with spaces
    cer_ns     with no spaces (main figure: PP-OCRv4 often loses spaces)
    cer_na     with no spaces and no accents (cer_ns - cer_na = cost of accents)
    wer        words
    nums       share of rows whose numbers (digit runs) equal the reference

Rows whose reference has LaTeX or the options inside `text` are not clean
comparisons. They are scored but reported apart.

It prints counts and percentages only. M3Kang is research-use only: the CSV
holds no problem text, and it belongs under data/ (gitignored).

Usage:
    python3 laptop/ocr_vs_text.py
    python3 laptop/ocr_vs_text.py --v4 data/interim/ocr_boxes_txto_yes.jsonl \\
        --v5 data/interim/ocr_boxes_txto_yes_v5.jsonl --out data/interim/ocr_vs_text.csv \\
        data/raw_txto_yes/*.parquet
"""
import argparse
import csv
import glob
import json
import os
import re
import statistics
import sys
import unicodedata
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from prepare_m3kang import is_marker, reading_order  # noqa: E402

LANGS = ("eng", "cat", "esp")
LATEX = re.compile(r"\$|\\\(|\\frac|\\\\")
OPTIONS_IN_TEXT = re.compile(r"(^|\s)\(?[A-E][\)\.]\s")
NUMBER = re.compile(r"\d+")
NUMBERING = re.compile(r"^\s*\d+\s*\.\s*")
PARTIAL = 0.7  # OCR text shorter than this share of the reference: question lines are missing


def lev(a, b):
    """Levenshtein distance (Myers/Hyyro bit-vector, a is the pattern)."""
    if not a:
        return len(b)
    if not b:
        return len(a)
    m = len(a)
    mask, top = (1 << m) - 1, 1 << (m - 1)
    peq = {}
    for i, c in enumerate(a):
        peq[c] = peq.get(c, 0) | (1 << i)
    pv, mv, score = mask, 0, m
    for c in b:
        eq = peq.get(c, 0)
        xv = eq | mv
        xh = ((((eq & pv) + pv) & mask) ^ pv) | eq
        ph = (mv | ~(xh | pv)) & mask
        mh = pv & xh
        if ph & top:
            score += 1
        elif mh & top:
            score -= 1
        ph = ((ph << 1) | 1) & mask
        mh = (mh << 1) & mask
        pv = (mh | ~(xv | ph)) & mask
        mv = ph & xv
    return score


def normalize(text):
    text = unicodedata.normalize("NFC", text)
    text = re.sub(r"\s+", " ", text).strip()
    return NUMBERING.sub("", text)


def strip_accents(text):
    return "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn")


def ocr_text(boxes):
    """Boxes in reading order as one string, cut before the first A) label."""
    items = reading_order(boxes)
    cut = len(items)
    for i, it in enumerate(items):
        if i > 0 and is_marker(it["text"], "A", strict=True) is not None and any(
                is_marker(j["text"], "B", strict=False) is not None for j in items[i + 1:]):
            cut = i
            break
    return " ".join(it["text"] for it in items[:cut])


def words_to_chars(ref, hyp):
    ids = {}
    enc = lambda ws: "".join(chr(0x100 + ids.setdefault(w, len(ids))) for w in ws)  # noqa: E731
    return enc(ref.split()), enc(hyp.split())


def score(ref, hyp):
    ref, hyp = normalize(ref), normalize(hyp)
    ns = lambda s: s.replace(" ", "")  # noqa: E731
    na = lambda s: strip_accents(ns(s))  # noqa: E731
    wr, wh = words_to_chars(ref, hyp)
    return {
        "cer": lev(ref, hyp) / max(1, len(ref)),
        "cer_ns": lev(ns(ref), ns(hyp)) / max(1, len(ns(ref))),
        "cer_na": lev(na(ref), na(hyp)) / max(1, len(na(ref))),
        "wer": lev(wr, wh) / max(1, len(wr)),
        "nums": float(NUMBER.findall(ns(ref)) == NUMBER.findall(ns(hyp))),
        "ref_len": len(ref),
        "len_ratio": len(ns(hyp)) / max(1, len(ns(ref))),
    }


def load_reference(paths):
    import pyarrow as pa
    import pyarrow.compute as pc
    import pyarrow.parquet as pq
    ref = {}
    for path in paths:
        t = pq.read_table(path, columns=["id", "language", "text"])
        t = t.filter(pc.is_in(t.column("language"), value_set=pa.array(LANGS)))
        for i, l, x in zip(t.column("id").to_pylist(), t.column("language").to_pylist(),
                           t.column("text").to_pylist()):
            ref[f"{i}|{l}"] = x or ""
    return ref


def load_boxes(path):
    with open(path) as f:
        return {r["key"]: r["boxes"] for r in map(json.loads, f)}


def pct(x):
    return f"{100 * x:5.1f}%"


def summarize(rows, title):
    print(f"\n{title}")
    print(f"{'lang':5}{'engine':>7}{'rows':>6}{'cer':>8}{'cer_ns':>8}{'med_ns':>8}{'cer_na':>8}{'wer':>8}"
          f"{'ns<2%':>8}{'ns<5%':>8}{'nums':>8}")
    for lang in LANGS + ("all",):
        for eng in ("v4", "v5"):
            rs = [r for r in rows if r["engine"] == eng and (lang == "all" or r["lang"] == lang)]
            if not rs:
                continue
            m = lambda k: statistics.mean(r[k] for r in rs)  # noqa: E731
            print(f"{lang:5}{eng:>7}{len(rs):>6}{pct(m('cer')):>8}{pct(m('cer_ns')):>8}"
                  f"{pct(statistics.median(r['cer_ns'] for r in rs)):>8}{pct(m('cer_na')):>8}{pct(m('wer')):>8}"
                  f"{pct(sum(r['cer_ns'] < 0.02 for r in rs) / len(rs)):>8}"
                  f"{pct(sum(r['cer_ns'] < 0.05 for r in rs) / len(rs)):>8}{pct(m('nums')):>8}")


def bootstrap(clean, times=2000, seed=0):
    """95 % interval of the mean cer_ns of each engine, and of v4 minus v5.

    Resamples problems, not rows: the same problem in three languages stays together.
    """
    import random
    by_problem = defaultdict(list)  # problem id -> [(lang, cer_v4, cer_v5)]
    cer = {(r["key"], r["engine"]): r["cer_ns"] for r in clean}
    for key in sorted({r["key"] for r in clean}):
        by_problem[key.split("|")[0]].append((key.split("|")[1], cer[key, "v4"], cer[key, "v5"]))
    ids = sorted(by_problem)
    rnd = random.Random(seed)
    print(f"\n95 % bootstrap interval of the mean CER (no spaces), {times} resamples of {len(ids)} problems, seed {seed}")
    print(f"{'lang':5}{'v4':>20}{'v5':>20}{'v4 minus v5 (points)':>30}")
    for lang in LANGS + ("all",):
        groups = [[row for row in by_problem[i] if lang in ("all", row[0])] for i in ids]
        groups = [g for g in groups if g]
        means = []
        for _ in range(times):
            sample = [row for g in (rnd.choice(groups) for _ in groups) for row in g]
            n = len(sample)
            means.append((sum(r[1] for r in sample) / n, sum(r[2] for r in sample) / n))
        rows = [row for g in groups for row in g]
        point = (statistics.mean(r[1] for r in rows), statistics.mean(r[2] for r in rows))

        def interval(values):
            values = sorted(values)
            return values[int(0.025 * times)], values[int(0.975 * times) - 1]

        lo4, hi4 = interval([m[0] for m in means])
        lo5, hi5 = interval([m[1] for m in means])
        lod, hid = interval([m[0] - m[1] for m in means])
        print(f"{lang:5}{f'{pct(point[0])} [{lo4 * 100:.1f}, {hi4 * 100:.1f}]':>20}"
              f"{f'{pct(point[1])} [{lo5 * 100:.1f}, {hi5 * 100:.1f}]':>20}"
              f"{f'{100 * (point[0] - point[1]):.1f} [{lod * 100:.1f}, {hid * 100:.1f}]':>30}")


def selftest():
    assert lev("kitten", "sitting") == 3 and lev("", "abc") == 3 and lev("abc", "") == 3
    assert lev("abc", "abc") == 0 and lev("flaw", "lawn") == 2
    import random
    rnd = random.Random(0)
    for _ in range(300):
        a = "".join(rnd.choice("abcd") for _ in range(rnd.randint(0, 12)))
        b = "".join(rnd.choice("abcd") for _ in range(rnd.randint(0, 12)))
        prev = list(range(len(b) + 1))
        for i, ca in enumerate(a, 1):
            cur = [i]
            for j, cb in enumerate(b, 1):
                cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
            prev = cur
        assert lev(a, b) == prev[-1], (a, b)
    s = score("Hola mundo 12", "Hola mundo 12")
    assert s["cer"] == 0 and s["wer"] == 0 and s["nums"] == 1.0
    assert score("Hola mundo", "")["cer"] == 1.0
    print("selftest ok")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--v4", default="data/interim/ocr_boxes_txto_yes.jsonl")
    p.add_argument("--v5", default="data/interim/ocr_boxes_txto_yes_v5.jsonl")
    p.add_argument("--out", default="data/interim/ocr_vs_text.csv")
    p.add_argument("--selftest", action="store_true", help="check the distance code and exit")
    p.add_argument("parquet", nargs="*", help="default: data/raw_txto_yes/*.parquet")
    args = p.parse_args()
    if args.selftest:
        return selftest()

    ref = load_reference(args.parquet or sorted(glob.glob("data/raw_txto_yes/*.parquet")))
    boxes = {"v4": load_boxes(args.v4), "v5": load_boxes(args.v5)}
    keys = sorted(ref.keys() & boxes["v4"].keys() & boxes["v5"].keys())
    print(f"reference {len(ref)} rows, v4 {len(boxes['v4'])}, v5 {len(boxes['v5'])}, in all three {len(keys)}")

    rows = []
    for key in keys:
        flags = [n for n, rx in (("latex", LATEX), ("opts_in_text", OPTIONS_IN_TEXT)) if rx.search(ref[key])]
        for eng in ("v4", "v5"):
            rows.append(dict(key=key, lang=key.split("|")[1], engine=eng, flags="+".join(flags),
                             **score(ref[key], ocr_text(boxes[eng][key]))))

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    cols = ["key", "lang", "engine", "cer", "cer_ns", "cer_na", "wer", "nums", "ref_len", "len_ratio", "flags"]
    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows({c: (round(r[c], 4) if isinstance(r[c], float) else r[c]) for c in cols} for r in rows)

    clean = [r for r in rows if not r["flags"]]
    print(f"clean rows (no LaTeX, no options in text): {len(clean) // 2} of {len(keys)}")
    summarize(clean, "CLEAN rows")
    summarize([r for r in rows if r["flags"]], "FLAGGED rows (LaTeX or options inside the reference)")

    by = defaultdict(dict)
    for r in clean:
        by[r["key"]][r["engine"]] = r["cer_ns"]
    better = {"v5": 0, "v4": 0, "tie": 0}
    for d in by.values():
        better["v5" if d["v5"] < d["v4"] else "v4" if d["v4"] < d["v5"] else "tie"] += 1
    print(f"\nclean rows, lower cer_ns: v5 {better['v5']}, v4 {better['v4']}, tie {better['tie']}")
    bootstrap(clean)

    # Rows where the OCR text is much shorter than the reference: lines of the question are missing.
    # The length ratio is a sign, not proof: it can also come from a wrong read.
    ratio = defaultdict(dict)
    for r in clean:
        ratio[r["key"]][r["engine"]] = r["len_ratio"]
    print(f"\nclean rows where the OCR text has under {PARTIAL:.0%} of the reference length (no spaces)")
    for eng in ("v4", "v5"):
        print(f"  {eng}: {sum(d[eng] < PARTIAL for d in ratio.values())}")
    print(f"  v4 reaches {PARTIAL:.0%} and v5 does not: {sum(d['v4'] >= PARTIAL > d['v5'] for d in ratio.values())}")
    print(f"  v5 reaches {PARTIAL:.0%} and v4 does not: {sum(d['v5'] >= PARTIAL > d['v4'] for d in ratio.values())}")
    print(f"  neither reaches it: {sum(max(d.values()) < PARTIAL for d in ratio.values())}")
    print(f"per-row CSV: {args.out}")


if __name__ == "__main__":
    main()
