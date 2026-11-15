#!/usr/bin/env python3
"""Run an OCR engine on M3Kang images and compare engines (docs/OCR_FAILURE_MODES.md).

dump     runs OCR on the rows of the given parquet files and saves the raw boxes,
         one {"key": "id|lang", "boxes": [[box, text, score], ...]} per line.
         It resumes: keys already in --out are skipped.
compare  parses two box files with parse_options (laptop/prepare_m3kang.py) and
         prints counts per language. It never prints problem text.

Engines:
    v4  rapidocr_onnxruntime (PP-OCRv4), the engine of prepare_m3kang.py
    v5  rapidocr >= 3 with PP-OCRv5: mobile detector, latin recognizer
    tess  Tesseract 5 CLI, LSTM (--oem 1), automatic layout (--psm 3), on the CPU.
          One box per word. Needs tessdata_best eng/cat/spa in --tessdata-dir
          (docs/experiments/2026-11-tesseract-text-only.md). --workers runs images in parallel.

Each engine needs its own environment (both use onnxruntime-gpu on CUDA).
M3Kang is research-use only: the box files hold problem text, so keep them
under data/ (gitignored).

Usage:
    python laptop/ocr_boxes.py dump --engine v5 --languages eng,cat,esp \\
        --out data/interim/ocr_boxes_txto_yes_v5.jsonl data/raw_txto_yes/*.parquet
    python laptop/ocr_boxes.py compare data/interim/ocr_boxes_txto_yes.jsonl \\
        data/interim/ocr_boxes_txto_yes_v5.jsonl
    python laptop/ocr_boxes.py dump --engine tess --workers 16 --languages eng,cat,esp \\
        --out data/interim/ocr_boxes_txto_yes_tess.jsonl data/raw_txto_yes/*.parquet
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from prepare_m3kang import parse_options  # noqa: E402


TESS_LANG = {"eng": "eng", "cat": "cat", "esp": "spa"}   # M3Kang language -> Tesseract model


def make_tesseract(tessdata, threads=1):
    """Tesseract on the image bytes; returns word boxes in the rapidocr format."""
    # One thread by default: --workers runs images in parallel. ocr_speed.py times more threads.
    env = dict(os.environ, OMP_THREAD_LIMIT=str(threads))

    def run(image, lang):
        out = subprocess.run(
            ["tesseract", "stdin", "stdout", "--tessdata-dir", tessdata, "-l", TESS_LANG[lang],
             "--oem", "1", "--psm", "3", "-c", "tessedit_create_tsv=1"],
            input=image, capture_output=True, env=env, check=True).stdout.decode("utf-8")
        return tsv_boxes(out)
    return run


def tsv_boxes(tsv):
    """Word rows (level 5) of Tesseract TSV as [[4 points], text, conf / 100]."""
    boxes = []
    for line in tsv.splitlines()[1:]:
        f = line.split("\t", 11)
        if len(f) < 12 or f[0] != "5" or not f[11].strip() or float(f[10]) < 0:
            continue
        x, y, w, h = (float(v) for v in f[6:10])
        boxes.append([[[x, y], [x + w, y], [x + w, y + h], [x, y + h]], f[11].strip(), float(f[10]) / 100])
    return boxes


def make_engine(name, chars=False):
    import onnxruntime
    onnxruntime.preload_dlls()  # find the pip-installed CUDA and cuDNN
    if name == "v4":
        from rapidocr_onnxruntime import RapidOCR
        ocr = RapidOCR(det_use_cuda=True, cls_use_cuda=True, rec_use_cuda=True)

        def run(image):
            boxes, _ = ocr(image)
            return boxes or []
        return run
    from rapidocr import EngineType, LangDet, LangRec, ModelType, OCRVersion, RapidOCR
    ocr = RapidOCR(params={
        "Global.log_level": "warning",
        "EngineConfig.onnxruntime.use_cuda": True,
        "EngineConfig.onnxruntime.cuda_ep_cfg.cudnn_conv_algo_search": "HEURISTIC",
        # The server detector runs out of memory on an 8 GB GPU; mobile matches v4.
        "Det.engine_type": EngineType.ONNXRUNTIME, "Det.lang_type": LangDet.CH,
        "Det.model_type": ModelType.MOBILE, "Det.ocr_version": OCRVersion.PPOCRV5,
        "Rec.engine_type": EngineType.ONNXRUNTIME, "Rec.lang_type": LangRec.LATIN,
        "Rec.model_type": ModelType.MOBILE, "Rec.ocr_version": OCRVersion.PPOCRV5,
    })

    def run(image):
        r = ocr(image)
        if r.boxes is None:
            return []
        return list(zip(r.boxes.tolist(), r.txts, r.scores))

    def run_chars(image):
        # rapidocr keeps call options between calls, and bar_search turns det off: set all.
        r = ocr(image, use_det=True, use_cls=True, use_rec=True,
                return_word_box=True, return_single_char_box=True)
        if r.boxes is None:
            return [], {}
        boxes = list(zip(r.boxes.tolist(), r.txts, r.scores))
        return boxes, measure(image, r.boxes.tolist(), r.word_results, ocr)
    return run_chars if chars else run


# --- Measurements for math layout (report not written yet) -----
#
# Stored raw, so the rules in laptop/math_layout.py can change without another
# GPU run. The char x-ranges come from rapidocr's CTC columns; their y is the
# whole line, so the vertical ink extent of each char is measured on the image.

INK = 140          # gray level below which a pixel is ink
TALL = 1.5         # a box taller than TALL x the median box height gets a bar search


def measure(image, boxes, word_results, ocr):
    import cv2
    import numpy as np

    img = cv2.imdecode(np.frombuffer(image, np.uint8), cv2.IMREAD_GRAYSCALE)
    ink = img < INK
    H, W = ink.shape
    heights = [max(p[1] for p in b) - min(p[1] for p in b) for b in boxes]
    median_h = float(np.median(heights)) if heights else 0.0
    chars, comps, bars = [], [], []
    for box, words, h in zip(boxes, word_results, heights):
        y0 = max(0, int(min(p[1] for p in box) - 0.15 * h))
        y1 = min(H, int(max(p[1] for p in box) + 0.15 * h) + 1)
        row = []
        bx0 = max(0, int(min(p[0] for p in box)))
        bx1 = min(W, int(max(p[0] for p in box)) + 1)
        for c, _score, cbox in words or ():
            x0, x1 = min(p[0] for p in cbox), max(p[0] for p in cbox)
            # Central third: ink in the middle columns only.
            a, b = int(x0 + (x1 - x0) / 3), int(x1 - (x1 - x0) / 3) + 1
            cols = ink[y0:y1, max(0, a):min(W, max(a + 1, b))]
            ys = np.where(cols.any(axis=1))[0]
            mid = [float(y0 + ys[0]), float(y0 + ys[-1])] if len(ys) else [None, None]
            row.append([c, float(x0), float(x1), *mid])
        comps.append(components(ink[y0:y1, bx0:bx1], bx0, y0))
        chars.append(row)
        bars.append(bar_search(img, ink, box, ocr) if median_h and h > TALL * median_h else None)
    return {"chars": chars, "comps": comps, "bars": bars}


def components(crop, ox, oy):
    """Ink blobs of a crop as [x0, x1, top, bottom] in image coordinates; specks dropped."""
    import cv2
    import numpy as np

    if crop.size == 0:
        return []
    n, _labels, stats, cents = cv2.connectedComponentsWithStats(crop.astype(np.uint8), connectivity=8)
    out = []
    for k in range(1, n):
        x, y, w, h, area = stats[k]
        if area >= 3:
            out.append([float(ox + x), float(ox + x + w - 1), float(oy + y), float(oy + y + h - 1)])
    return out


def bar_search(img, ink, box, ocr):
    """Best horizontal-bar row in the middle half of a tall box, and the text above and below it."""
    import numpy as np

    x0, x1 = int(min(p[0] for p in box)), int(max(p[0] for p in box)) + 1
    y0, y1 = int(min(p[1] for p in box)), int(max(p[1] for p in box)) + 1
    crop = ink[y0:y1, x0:x1]
    h = crop.shape[0]
    if h < 8 or crop.shape[1] < 4:
        return None
    ratio = crop.mean(axis=1)
    lo, hi = h // 4, 3 * h // 4
    r = int(lo + np.argmax(ratio[lo:hi]))
    out = {"y": float(y0 + r), "ratio": round(float(ratio[r]), 3), "halves": None}
    if ratio[r] > 0.3:
        top, bottom = img[y0:y0 + max(1, r - 1), x0:x1], img[y0 + r + 2:y1, x0:x1]
        halves = []
        for part in (top, bottom):
            if part.shape[0] < 4:
                halves.append("")
                continue
            res = ocr(np.dstack([part] * 3), use_det=False, use_cls=False)
            halves.append(res.txts[0] if getattr(res, "txts", None) else "")
        out["halves"] = halves
    return out


def dump(args):
    import pyarrow as pa
    import pyarrow.compute as pc
    import pyarrow.parquet as pq

    done = set()
    keys = {line.strip() for line in open(args.keys_file)} if args.keys_file else None
    if os.path.exists(args.out):
        done = {json.loads(line)["key"] for line in open(args.out)}
    if args.chars and args.engine != "v5":
        sys.exit("--chars needs --engine v5")
    tess = args.engine == "tess"
    run = make_tesseract(args.tessdata_dir) if tess else make_engine(args.engine, chars=args.chars)
    pool = None
    if tess:
        from concurrent.futures import ThreadPoolExecutor  # threads are enough: each runs a subprocess
        pool = ThreadPoolExecutor(args.workers)
    languages = None if args.languages == "all" else pa.array(args.languages.split(","))
    exclude = pa.array(args.exclude_languages.split(",")) if args.exclude_languages else None
    n, t0 = 0, time.time()
    with open(args.out, "a") as f:
        for path in args.parquet:
            table = pq.read_table(path)
            if languages is not None:
                table = table.filter(pc.is_in(table.column("language"), value_set=languages))
            if exclude is not None:
                table = table.filter(pc.invert(pc.is_in(table.column("language"), value_set=exclude)))
            todo = []
            for i in range(table.num_rows):
                key = f"{table.column('id')[i].as_py()}|{table.column('language')[i].as_py()}"
                if key not in done and (keys is None or key in keys):
                    todo.append((i, key))
            image = lambda i: table.column("image")[i].as_py()["bytes"]  # noqa: E731
            if tess:
                outs = pool.map(lambda ik: run(image(ik[0]), ik[1].split("|")[1]), todo)
            else:
                outs = (run(image(i)) for i, _ in todo)
            for (i, key), out in zip(todo, outs):
                boxes, extra = out if args.chars else (out, {})
                boxes = [[[[float(x), float(y)] for x, y in box], text, float(score)]
                         for box, text, score in boxes]
                f.write(json.dumps({"key": key, "boxes": boxes, **extra}, ensure_ascii=False) + "\n")
                n += 1
                if n % 200 == 0:
                    print(f"  {n} rows, {n / (time.time() - t0):.1f} rows/s", flush=True)
    if n:
        dt = time.time() - t0
        print(f"{n} rows in {dt:.0f} s ({n / dt:.1f} rows/s"
              + (f", {args.workers} workers: about {dt * args.workers / n:.2f} CPU-thread s per image)" if tess else ")"))


def norm(value):
    return re.sub(r"[\s,.]", "", value)


def compare(args):
    def load(path):
        return {r["key"]: parse_options(r["boxes"]) for r in map(json.loads, open(path))}

    a, b = load(args.a), load(args.b)
    keys = sorted(a.keys() & b.keys())
    stats = defaultdict(Counter)
    for key in keys:
        s = stats[key.split("|")[1]]
        oa, ob = a[key], b[key]
        s["rows"] += 1
        s["a5"] += bool(oa)
        s["b5"] += bool(ob)
        s["only_b"] += bool(ob) and not oa
        s["only_a"] += bool(oa) and not ob
        if oa and ob:
            s["both"] += 1
            s["differ"] += any(norm(oa[k]) != norm(ob[k]) for k in oa)
    print(f"A = {args.a}\nB = {args.b}\n{len(keys)} rows in both files")
    print(f"{'lang':6}{'rows':>6}{'A 5/5':>7}{'B 5/5':>7}{'only B':>8}{'only A':>8}{'both':>6}{'differ':>8}")
    total = Counter()
    for lang in sorted(stats) + ["total"]:
        s = stats[lang] if lang != "total" else total
        if lang != "total":
            total.update(s)
        print(f"{lang:6}{s['rows']:>6}{s['a5']:>7}{s['b5']:>7}{s['only_b']:>8}{s['only_a']:>8}"
              f"{s['both']:>6}{s['differ']:>8}")
    print(f"coverage A {100 * total['a5'] / total['rows']:.1f}%, B {100 * total['b5'] / total['rows']:.1f}%")
    print("differ: rows with 5 options in both whose values differ beyond spaces and , .")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("dump")
    d.add_argument("--engine", choices=["v4", "v5", "tess"], required=True)
    d.add_argument("--tessdata-dir", default="data/external/tessdata", help="tess only: traineddata folder")
    d.add_argument("--workers", type=int, default=1, help="tess only: images run in parallel")
    d.add_argument("--languages", default="eng,cat,esp", help='comma list, or "all"')
    d.add_argument("--exclude-languages", default="", help="comma list of languages to skip")
    d.add_argument("--keys-file", help='only these keys, one "id|lang" per line')
    d.add_argument("--chars", action="store_true",
                   help="v5 only: also store per-char x-ranges with ink extent, and bars in tall boxes")
    d.add_argument("--out", required=True)
    d.add_argument("parquet", nargs="+")
    c = sub.add_parser("compare")
    c.add_argument("a")
    c.add_argument("b")
    args = p.parse_args()
    dump(args) if args.cmd == "dump" else compare(args)


if __name__ == "__main__":
    main()
