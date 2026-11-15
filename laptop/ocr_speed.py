#!/usr/bin/env python3
"""Time the OCR engines on the CPU: PP-OCRv4, PP-OCRv5 and Tesseract.

Experiment: docs/experiments/2026-11-tesseract-text-only.md (section Speed).

pick    draw the test images (fixed seed) from the eng/cat/esp text-only rows and
        write them as files with keys.txt. Needs pyarrow (the .venv of the repository).
run     time one engine with N threads on those files: load time, per-image time,
        peak memory, and how many images give five options. Writes a JSON file.
        Needs only the engine's own package (and Pillow for tess), so it runs on the board.
report  print a table from the JSON files.

Each engine runs in its own environment:
    v4    rapidocr_onnxruntime 1.4.4 (~/.venvs/ocr-v4)
    v5    rapidocr 3.10, mobile detector, latin recognizer (~/.venvs/ocr-v5)
    tess  tesseract CLI, tessdata_best, --oem 1 --psm 3 (any Python with Pillow)

The image files are M3Kang (research use only): keep them under data/ (gitignored).
It prints numbers only, never problem text.

Usage:
    .venv/bin/python -I laptop/ocr_speed.py pick
    taskset -c 0 ~/.venvs/ocr-v5/bin/python -I laptop/ocr_speed.py run --engine v5 --threads 1 \\
        --out data/interim/speed/laptop-v5-t1-r1.json
    .venv/bin/python -I laptop/ocr_speed.py report data/interim/speed/laptop-*.json
"""
import argparse
import glob
import json
import os
import platform
import random
import resource
import statistics
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ocr_boxes import TESS_LANG, make_tesseract, tsv_boxes  # noqa: E402
from prepare_m3kang import parse_options  # noqa: E402

DIR = "data/interim/speed"
IMAGES = f"{DIR}/images"
WARMUP = 3


def cmd_pick(args):
    import pyarrow.parquet as pq
    boxes = {json.loads(line)["key"] for line in open("data/interim/ocr_boxes_txto_yes_v5.jsonl")}
    rng = random.Random(args.seed)
    pick = []
    for lang, n in (("eng", 34), ("cat", 33), ("esp", 33)):
        pick += rng.sample(sorted(k for k in boxes if k.endswith("|" + lang)), n)
    os.makedirs(IMAGES, exist_ok=True)
    wanted = set(pick)
    for path in sorted(glob.glob("data/raw_txto_yes/*.parquet")):
        t = pq.read_table(path, columns=["id", "language", "image"])
        for i, (pid, lang) in enumerate(zip(t.column("id").to_pylist(), t.column("language").to_pylist())):
            key = f"{pid}|{lang}"
            if key in wanted:
                with open(f"{IMAGES}/{file_name(key)}", "wb") as f:
                    f.write(t.column("image")[i].as_py()["bytes"])
    with open(f"{DIR}/keys.txt", "w") as f:
        f.write("\n".join(pick) + "\n")
    print(f"{len(pick)} images in {IMAGES} (seed {args.seed}), {len(os.listdir(IMAGES))} files")


def file_name(key):
    return key.replace("|", "__") + ".img"


def make_ppocr(engine, threads):
    """The engine settings of ocr_boxes.make_engine, on the CPU with a fixed thread count."""
    if engine == "v4":
        from rapidocr_onnxruntime import RapidOCR
        ocr = RapidOCR(intra_op_num_threads=threads, inter_op_num_threads=1)

        def run(image):
            boxes, _ = ocr(image)
            return boxes or []
        return run
    from rapidocr import EngineType, LangDet, LangRec, ModelType, OCRVersion, RapidOCR
    ocr = RapidOCR(params={
        "Global.log_level": "warning",
        "EngineConfig.onnxruntime.use_cuda": False,
        "EngineConfig.onnxruntime.intra_op_num_threads": threads,
        "EngineConfig.onnxruntime.inter_op_num_threads": 1,
        "Det.engine_type": EngineType.ONNXRUNTIME, "Det.lang_type": LangDet.CH,
        "Det.model_type": ModelType.MOBILE, "Det.ocr_version": OCRVersion.PPOCRV5,
        "Rec.engine_type": EngineType.ONNXRUNTIME, "Rec.lang_type": LangRec.LATIN,
        "Rec.model_type": ModelType.MOBILE, "Rec.ocr_version": OCRVersion.PPOCRV5,
    })

    def run(image):
        r = ocr(image)
        return [] if r.boxes is None else list(zip(r.boxes.tolist(), r.txts, r.scores))
    return run


def versions(engine):
    from importlib import metadata
    if engine == "tess":
        return subprocess.run(["tesseract", "--version"], capture_output=True, text=True).stdout.split("\n")[0]
    pkg = "rapidocr_onnxruntime" if engine == "v4" else "rapidocr"
    out = f"{pkg} {metadata.version(pkg)}"
    for ort in ("onnxruntime", "onnxruntime-gpu"):
        try:
            out += f", {ort} {metadata.version(ort)}"
        except metadata.PackageNotFoundError:
            pass
    return out


def cpu_model():
    try:
        for line in open("/proc/cpuinfo"):
            if line.lower().startswith(("model name", "hardware")):
                return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or "unknown"


def cmd_run(args):
    keys = [k for k in open(f"{DIR}/keys.txt").read().split() if k]
    images = [(k, open(f"{args.images}/{file_name(k)}", "rb").read()) for k in keys]
    t0 = time.perf_counter()
    if args.engine == "tess":
        tess = make_tesseract(args.tessdata_dir, threads=args.threads)
        run = lambda image, lang: tess(image, lang)  # noqa: E731
        blank = blank_png()
        tess(blank, "eng")  # one call on a blank image: process start and model load
    else:
        pp = make_ppocr(args.engine, args.threads)
        run = lambda image, lang: pp(image)  # noqa: E731
    load = time.perf_counter() - t0
    for k, image in images[:WARMUP]:
        run(image, k.split("|")[1])
    secs, five = [], 0
    for k, image in images:
        t = time.perf_counter()
        boxes = run(image, k.split("|")[1])
        secs.append(time.perf_counter() - t)
        opts = parse_options([[[[float(x), float(y)] for x, y in b], txt, float(s)] for b, txt, s in boxes])
        five += len(opts) == 5
    out = {
        "engine": args.engine, "threads": args.threads, "label": args.label, "n": len(secs),
        "load_s": load, "secs": secs, "five_options": five,
        "peak_rss_mb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024,
        "peak_rss_child_mb": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss / 1024,
        "host": {"machine": platform.machine(), "cpu": cpu_model(), "cores": os.cpu_count(),
                 "affinity": sorted(os.sched_getaffinity(0)), "node": platform.node()},
        "versions": versions(args.engine),
    }
    if args.engine == "tess":
        out["batch"] = tess_batch(images, args)
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    json.dump(out, open(args.out, "w"), indent=1)
    print(f"{args.engine} t{args.threads}: load {load:.2f} s, median {statistics.median(secs):.3f} s, "
          f"five options {five}/{len(secs)} -> {args.out}")


def tess_batch(images, args):
    """One CLI call per language on a list file: the model loads once, not once per image."""
    total, n = 0.0, 0
    env = dict(os.environ, OMP_THREAD_LIMIT=str(args.threads))
    with tempfile.TemporaryDirectory() as tmp:
        for lang in ("eng", "cat", "esp"):
            mine = [k for k, _ in images if k.endswith("|" + lang)]
            lst = os.path.join(tmp, f"{lang}.txt")
            with open(lst, "w") as f:
                f.write("\n".join(os.path.abspath(f"{args.images}/{file_name(k)}") for k in mine) + "\n")
            t = time.perf_counter()
            subprocess.run(["tesseract", lst, os.path.join(tmp, lang), "--tessdata-dir", args.tessdata_dir,
                            "-l", TESS_LANG[lang], "--oem", "1", "--psm", "3", "-c", "tessedit_create_tsv=1"],
                           capture_output=True, env=env, check=True)
            total += time.perf_counter() - t
            n += len(mine)
    return {"total_s": total, "per_image_s": total / n, "n": n}


def blank_png():
    from PIL import Image
    import io
    buf = io.BytesIO()
    Image.new("L", (400, 100), 255).save(buf, "PNG")
    return buf.getvalue()


def cmd_report(args):
    rows = [json.load(open(p)) for p in args.files]
    print(f"{'label':8}{'engine':>7}{'thr':>4}{'load s':>8}{'median s':>10}{'p90 s':>8}{'total s':>9}"
          f"{'batch s/img':>12}{'peak MB':>9}{'5 opts':>8}")
    for r in sorted(rows, key=lambda r: (r["label"], r["engine"], r["threads"])):
        s = sorted(r["secs"])
        peak = max(r["peak_rss_mb"], r["peak_rss_child_mb"])
        batch = f"{r['batch']['per_image_s']:.3f}" if "batch" in r else "-"
        print(f"{r['label']:8}{r['engine']:>7}{r['threads']:>4}{r['load_s']:>8.2f}{statistics.median(s):>10.3f}"
              f"{s[int(0.9 * len(s)) - 1]:>8.3f}{sum(s):>9.1f}{batch:>12}{peak:>9.0f}{r['five_options']:>5}/{r['n']}")
    hosts = {(r["host"]["cpu"], r["host"]["machine"], r["versions"]) for r in rows}
    for h in sorted(hosts):
        print("  host:", " | ".join(h))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("pick")
    s.add_argument("--seed", type=int, default=41)
    s = sub.add_parser("run")
    s.add_argument("--engine", choices=["v4", "v5", "tess"], required=True)
    s.add_argument("--threads", type=int, default=1)
    s.add_argument("--images", default=IMAGES)
    s.add_argument("--tessdata-dir", default="data/external/tessdata")
    s.add_argument("--label", default="laptop")
    s.add_argument("--out", required=True)
    s = sub.add_parser("report")
    s.add_argument("files", nargs="+")
    args = p.parse_args()
    {"pick": cmd_pick, "run": cmd_run, "report": cmd_report}[args.cmd](args)


if __name__ == "__main__":
    main()
