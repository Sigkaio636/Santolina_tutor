#!/usr/bin/env python3
"""Time the OCR engines on the CPU: PP-OCRv4, PP-OCRv5, Tesseract and the new option reader.

Experiments: docs/experiments/2026-11-tesseract-text-only.md (section Speed) and
docs/experiments/2026-11-option-pipeline-speed.md (old against new option pipeline).

pick    draw the test images (fixed seed) from the eng/cat/esp text-only rows and
        write them as files with keys.txt. Needs pyarrow (the .venv of the repository).
        --all writes every eng/cat/esp text-only row (images_all/, keys_all.txt).
run     time one engine with N threads on those files: load time, per-image time,
        peak memory, and how many images give five options. Writes a JSON file, and
        with --rows-out one JSON line per image (time and options).
        Needs only the engine's own package (and Pillow for tess), so it runs on the board.
report  print a table from the JSON files.
compare old pipeline (v5, v4 where v5 reads no options) against new, from the --rows-out
        files: time per row and per problem, paired difference, quality on the gold sets.

Each engine runs in its own environment:
    v4    rapidocr_onnxruntime 1.4.4 (~/.venvs/ocr-v4)
    v5    rapidocr 3.10, mobile detector, latin recognizer (~/.venvs/ocr-v5)
    tess  tesseract CLI, tessdata_best, --oem 1 --psm 3 (any Python with Pillow)
    new   label boxes (OpenCV) + 2-D split + PP-OCRv6_rec_small, R1/I0/2d of
          laptop/option_rec.py (the .venv of the repository)

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
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ocr_boxes import TESS_LANG, make_tesseract, tsv_boxes  # noqa: E402
from prepare_m3kang import parse_options  # noqa: E402

DIR = "data/interim/speed"
IMAGES = f"{DIR}/images"
IMAGES_ALL = f"{DIR}/images_all"
WARMUP = 3
LANGS = ("eng", "cat", "esp")


def cmd_pick(args):
    import pyarrow.parquet as pq
    boxes = {json.loads(line)["key"] for line in open("data/interim/ocr_boxes_txto_yes_v5.jsonl")}
    if args.all:
        pick = sorted(k for k in boxes if k.split("|")[1] in LANGS)
        random.Random(args.seed).shuffle(pick)   # run order: no level drifts with time
        images_dir, keys_file = IMAGES_ALL, f"{DIR}/keys_all.txt"
    else:
        rng = random.Random(args.seed)
        pick = []
        for lang, n in (("eng", 34), ("cat", 33), ("esp", 33)):
            pick += rng.sample(sorted(k for k in boxes if k.endswith("|" + lang)), n)
        images_dir, keys_file = IMAGES, f"{DIR}/keys.txt"
    os.makedirs(images_dir, exist_ok=True)
    wanted = set(pick)
    for path in sorted(glob.glob("data/raw_txto_yes/*.parquet")):
        t = pq.read_table(path, columns=["id", "language", "image"])
        for i, (pid, lang) in enumerate(zip(t.column("id").to_pylist(), t.column("language").to_pylist())):
            key = f"{pid}|{lang}"
            if key in wanted:
                with open(f"{images_dir}/{file_name(key)}", "wb") as f:
                    f.write(t.column("image")[i].as_py()["bytes"])
    with open(keys_file, "w") as f:
        f.write("\n".join(pick) + "\n")
    print(f"{len(pick)} images in {images_dir} -> {keys_file}, {len(os.listdir(images_dir))} files")


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


def make_new(threads):
    """The new option pipeline: B1 label boxes, 2-D split, R1 on the gray crop (I0).
    The label templates and the recognizer load here, once."""
    import option_boxes as ob
    import option_rec as orec
    ob.templates()
    rec = orec.Rec("R1", threads)
    arm = ("R1", "I0", "2d")

    def run(image):
        r = orec.read_row({"R1": rec}, ob.gray(image), [arm])[arm]
        return r["options"], {"seen": r.get("seen", {})}
    return run, rec


def versions(engine):
    from importlib import metadata
    if engine == "tess":
        return subprocess.run(["tesseract", "--version"], capture_output=True, text=True).stdout.split("\n")[0]
    pkg = {"v4": "rapidocr_onnxruntime", "v5": "rapidocr", "new": "opencv-python-headless"}[engine]
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
    keys = [k for k in open(args.keys_file).read().split() if k]
    if args.limit:
        keys = keys[:args.limit]
    images = [(k, open(f"{args.images}/{file_name(k)}", "rb").read()) for k in keys]
    rec = None
    t0 = time.perf_counter()
    if args.engine == "tess":
        tess = make_tesseract(args.tessdata_dir, threads=args.threads)
        blank = blank_png()
        tess(blank, "eng")  # one call on a blank image: process start and model load

        def read(image, lang):
            return parse_options(_boxes(tess(image, lang))), {}
    elif args.engine == "new":
        new, rec = make_new(args.threads)

        def read(image, lang):
            return new(image)
    else:
        pp = make_ppocr(args.engine, args.threads)

        def read(image, lang):
            return parse_options(_boxes(pp(image))), {}
    load = time.perf_counter() - t0
    for k, image in images[:WARMUP]:
        read(image, k.split("|")[1])
    if rec:
        rec.seconds, rec.calls = 0.0, 0
    rows_out = open(args.rows_out, "w") if args.rows_out else None
    secs, five = [], 0
    start = time.perf_counter()
    for k, image in images:
        calls0, rsec0 = (rec.calls, rec.seconds) if rec else (0, 0.0)
        t = time.perf_counter()
        opts, extra = read(image, k.split("|")[1])   # the whole pipeline: engine and parser
        sec = time.perf_counter() - t
        secs.append(sec)
        five += len(opts) == 5
        if rows_out:
            row = {"key": k, "sec": sec, "t": t - start, "options": opts, **extra}
            if rec:
                row["reads"], row["rec_sec"] = rec.calls - calls0, rec.seconds - rsec0
            rows_out.write(json.dumps(row, ensure_ascii=False) + "\n")
    if rows_out:
        rows_out.close()
    out = {
        "engine": args.engine, "threads": args.threads, "label": args.label, "n": len(secs),
        "load_s": load, "secs": secs, "five_options": five,
        "peak_rss_mb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024,
        "peak_rss_child_mb": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss / 1024,
        "host": {"machine": platform.machine(), "cpu": cpu_model(), "cores": os.cpu_count(),
                 "affinity": sorted(os.sched_getaffinity(0)), "node": platform.node(),
                 "governor": governor()},
        "versions": versions(args.engine),
    }
    if args.engine == "tess":
        out["batch"] = tess_batch(images, args)
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    json.dump(out, open(args.out, "w"), indent=1)
    print(f"{args.engine} t{args.threads}: load {load:.2f} s, mean {statistics.mean(secs):.3f} s, "
          f"median {statistics.median(secs):.3f} s, five options {five}/{len(secs)} -> {args.out}")


def _boxes(boxes):
    return [[[[float(x), float(y)] for x, y in b], txt, float(sc)] for b, txt, sc in boxes]


def governor():
    try:
        return open("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor").read().strip()
    except OSError:
        return "unknown"


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


# --- Old against new option pipeline -----------------------------------------

def load_rows_file(path):
    return {r["key"]: r for r in map(json.loads, open(path))} if os.path.exists(path) else {}


def cmd_fallback(args):
    v5 = load_rows_file(args.v5)
    keys = [k for k, r in v5.items() if not r["options"]]
    with open(args.out, "w") as f:
        f.write("".join(k + "\n" for k in keys))
    print(f"{len(keys)} of {len(v5)} rows without options from v5 -> {args.out}")


def time_stats(secs):
    s = sorted(secs)
    q = lambda f: s[min(len(s) - 1, int(f * len(s)))]  # noqa: E731
    return (f"{statistics.mean(s):7.3f} {statistics.median(s):7.3f} {q(0.9):7.3f} {q(0.99):7.3f} "
            f"{sum(s):8.0f} {60 * len(s) / sum(s):8.1f}")


def ratio_ci(old, new, clusters, n_boot=2000, seed=0):
    """95% bootstrap interval of mean(old) / mean(new), resampling whole problems."""
    by = defaultdict(lambda: [0.0, 0.0, 0])
    for o, n, c in zip(old, new, clusters):
        by[c][0] += o
        by[c][1] += n
        by[c][2] += 1
    groups = list(by.values())
    rng = random.Random(seed)
    out = []
    for _ in range(n_boot):
        so = sn = 0.0
        for _g in groups:
            g = groups[rng.randrange(len(groups))]
            so += g[0]
            sn += g[1]
        out.append(so / sn)
    out.sort()
    return out[int(0.025 * n_boot)], out[int(0.975 * n_boot) - 1]


def cmd_compare(args):
    import option_boxes as ob
    import option_consensus as oc
    import option_rec as orec
    v5, v4, new = load_rows_file(args.v5), load_rows_file(args.v4), load_rows_file(args.new)
    keys = sorted(set(v5) & set(new))
    missing = [k for k in keys if not v5[k]["options"] and k not in v4]
    if missing:
        sys.exit(f"{len(missing)} rows need the v4 fallback and have no v4 row: run `fallback` and v4 first")
    old_sec, old_opt = {}, {}
    for k in keys:
        fb = not v5[k]["options"]
        old_sec[k] = v5[k]["sec"] + (v4[k]["sec"] if fb else 0.0)
        old_opt[k] = v5[k]["options"] or (v4[k]["options"] if fb else {})
    new_sec = {k: new[k]["sec"] for k in keys}
    new_opt = {k: new[k]["options"] for k in keys}
    pid = {k: k.split("|")[0] for k in keys}
    print(f"{len(keys)} rows, {len(set(pid.values()))} problems")

    print("\nTime per row (s)          mean  median     p90     p99  total s  rows/min")
    print(f"{'old (v5, v4 fallback)':22} {time_stats([old_sec[k] for k in keys])}")
    print(f"{'new (B1 + R1 + 2d)':22} {time_stats([new_sec[k] for k in keys])}")
    by_p = defaultdict(lambda: [0.0, 0.0])
    for k in keys:
        by_p[pid[k]][0] += old_sec[k]
        by_p[pid[k]][1] += new_sec[k]
    print(f"Per problem (sum of its languages, mean over {len(by_p)}): "
          f"old {statistics.mean(v[0] for v in by_p.values()):.3f} s, "
          f"new {statistics.mean(v[1] for v in by_p.values()):.3f} s")
    diff = [old_sec[k] - new_sec[k] for k in keys]
    lo, hi = oc.cluster_ci(diff, [pid[k] for k in keys])
    rlo, rhi = ratio_ci([old_sec[k] for k in keys], [new_sec[k] for k in keys], [pid[k] for k in keys])
    ratio = sum(old_sec.values()) / sum(new_sec.values())
    print(f"Paired old - new: {statistics.mean(diff):.3f} s per row (95% CI {lo:.3f} to {hi:.3f}); "
          f"old / new = {ratio:.2f} (95% CI {rlo:.2f} to {rhi:.2f}); new faster in "
          f"{sum(d > 0 for d in diff)}/{len(diff)} rows")

    fb = [k for k in keys if not v5[k]["options"]]
    print(f"\nOld: v5 mean {statistics.mean(v5[k]['sec'] for k in keys):.3f} s; v4 fallback on {len(fb)} rows, "
          f"{sum(v4[k]['sec'] for k in fb):.1f} s in all "
          f"({100 * sum(v4[k]['sec'] for k in fb) / sum(old_sec.values()):.1f} % of the old total)")
    if all("rec_sec" in new[k] for k in keys):
        rec = [new[k]["rec_sec"] for k in keys]
        print(f"New: {statistics.mean(new[k]['reads'] for k in keys):.2f} reads per row; recognizer "
              f"{statistics.mean(rec):.3f} s, the rest (decode, labels, components, split) "
              f"{statistics.mean(new_sec[k] - r for k, r in zip(keys, rec)):.3f} s per row; "
              f"{1000 * sum(rec) / sum(new[k]['reads'] for k in keys):.1f} ms per read")

    print("\nBy level          rows   old mean  new mean")
    levels = defaultdict(list)
    for k in keys:
        levels[pid[k].split("_")[0]].append(k)
    for lv in sorted(levels):
        ks = levels[lv]
        print(f"{lv:16} {len(ks):5}   {statistics.mean(old_sec[k] for k in ks):7.3f}  "
              f"{statistics.mean(new_sec[k] for k in ks):7.3f}")
    print("By what OpenCV saw in the options")
    groups = defaultdict(list)
    for k in keys:
        seen = {v for v in new[k].get("seen", {}).values() if v}
        groups["fraction or exponent" if seen & {"frac", "sup", "frac+sup"} else "plain"].append(k)
    for g, ks in sorted(groups.items()):
        print(f"{g:22} {len(ks):5}   {statistics.mean(old_sec[k] for k in ks):7.3f}  "
              f"{statistics.mean(new_sec[k] for k in ks):7.3f}")

    print("\nDrift: median of the first and last 10 % of rows in run order")
    for name, rows in (("v5", v5), ("new", new)):
        order = sorted(rows.values(), key=lambda r: r["t"])
        n = max(1, len(order) // 10)
        a = statistics.median(r["sec"] for r in order[:n])
        b = statistics.median(r["sec"] for r in order[-n:])
        print(f"  {name:4} {a:.3f} -> {b:.3f} s ({100 * (b - a) / a:+.1f} %)")

    print("\nQuality in the same run      five   valid   gold rows (opts)   hard gold rows (opts)")
    golds = {n: {g["key"]: g["options"] for g in json.load(open(p))} for n, p in orec.GOLDS.items()}
    for name, arm in (("old", old_opt), ("new", new_opt)):
        five = [k for k in keys if len(arm[k]) == 5 and all(arm[k].values())]
        valid = [k for k in five if not oc.row_flags(arm[k])]
        cells = []
        for gname in ("gold", "gold_hard"):
            g = {k: v for k, v in golds[gname].items() if k in arm}
            r_ok, n, o_ok, o_n = oc.gold_scores(arm, g)
            cells.append(f"{r_ok}/{n} ({o_ok}/{o_n})")
        print(f"{name:26} {len(five):6} {len(valid):7}   {cells[0]:18} {cells[1]}")

    print("\nSame options as the stored reads (GPU v5 boxes, readall_B1-R1-I0-2d)")
    gpu5 = ob.load_boxes(ob.V5)
    same5 = sum(oc.gold_norm(str(v5[k]["options"])) == oc.gold_norm(str(ob.parse_options(gpu5.get(k, [])))) for k in keys)
    stored = orec.load_arm(f"{orec.OUT}/readall_B1-R1-I0-2d.jsonl")
    samen = sum(new_opt[k] == stored.get(k, {}).get("options") for k in keys)
    print(f"  v5 on the CPU = v5 on the GPU: {same5}/{len(keys)} rows")
    print(f"  new now = new stored:          {samen}/{len(keys)} rows")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("pick")
    s.add_argument("--seed", type=int, default=41)
    s.add_argument("--all", action="store_true", help="every eng/cat/esp text-only row")
    s = sub.add_parser("run")
    s.add_argument("--engine", choices=["v4", "v5", "tess", "new"], required=True)
    s.add_argument("--threads", type=int, default=1)
    s.add_argument("--images", default=IMAGES)
    s.add_argument("--keys-file", default=f"{DIR}/keys.txt")
    s.add_argument("--limit", type=int, default=0, help="only the first N keys")
    s.add_argument("--rows-out", help="one JSON line per image: key, time, options")
    s.add_argument("--tessdata-dir", default="data/external/tessdata")
    s.add_argument("--label", default="laptop")
    s.add_argument("--out", required=True)
    s = sub.add_parser("report")
    s.add_argument("files", nargs="+")
    s = sub.add_parser("fallback")
    s.add_argument("--v5", required=True, help="rows file of v5")
    s.add_argument("--out", required=True, help="keys where v5 reads no options (v4 runs on them)")
    s = sub.add_parser("compare")
    s.add_argument("--v5", required=True, help="rows file of v5 on every row")
    s.add_argument("--v4", required=True, help="rows file of v4 on the rows where v5 reads no options")
    s.add_argument("--new", required=True, help="rows file of the new pipeline")
    args = p.parse_args()
    {"pick": cmd_pick, "run": cmd_run, "report": cmd_report, "fallback": cmd_fallback,
     "compare": cmd_compare}[args.cmd](args)


if __name__ == "__main__":
    main()
