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

Each engine needs its own environment (both use onnxruntime-gpu on CUDA).
M3Kang is research-use only: the box files hold problem text, so keep them
under data/ (gitignored).

Usage:
    python laptop/ocr_boxes.py dump --engine v5 --languages eng,cat,esp \\
        --out data/interim/ocr_boxes_txto_yes_v5.jsonl data/raw_txto_yes/*.parquet
    python laptop/ocr_boxes.py compare data/interim/ocr_boxes_txto_yes.jsonl \\
        data/interim/ocr_boxes_txto_yes_v5.jsonl
"""
import argparse
import json
import os
import re
import sys
import time
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from prepare_m3kang import parse_options  # noqa: E402


def make_engine(name):
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
    return run


def dump(args):
    import pyarrow as pa
    import pyarrow.compute as pc
    import pyarrow.parquet as pq

    done = set()
    keys = {line.strip() for line in open(args.keys_file)} if args.keys_file else None
    if os.path.exists(args.out):
        done = {json.loads(line)["key"] for line in open(args.out)}
    run = make_engine(args.engine)
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
            for i in range(table.num_rows):
                key = f"{table.column('id')[i].as_py()}|{table.column('language')[i].as_py()}"
                if key in done or (keys is not None and key not in keys):
                    continue
                boxes = run(table.column("image")[i].as_py()["bytes"])
                boxes = [[[[float(x), float(y)] for x, y in box], text, float(score)]
                         for box, text, score in boxes]
                f.write(json.dumps({"key": key, "boxes": boxes}, ensure_ascii=False) + "\n")
                n += 1
                if n % 200 == 0:
                    print(f"  {n} rows, {n / (time.time() - t0):.1f} rows/s", flush=True)
    if n:
        print(f"{n} rows in {time.time() - t0:.0f} s ({n / (time.time() - t0):.1f} rows/s)")


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
    d.add_argument("--engine", choices=["v4", "v5"], required=True)
    d.add_argument("--languages", default="eng,cat,esp", help='comma list, or "all"')
    d.add_argument("--exclude-languages", default="", help="comma list of languages to skip")
    d.add_argument("--keys-file", help='only these keys, one "id|lang" per line')
    d.add_argument("--out", required=True)
    d.add_argument("parquet", nargs="+")
    c = sub.add_parser("compare")
    c.add_argument("a")
    c.add_argument("b")
    args = p.parse_args()
    dump(args) if args.cmd == "dump" else compare(args)


if __name__ == "__main__":
    main()
