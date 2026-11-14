#!/usr/bin/env python3
"""Trial of PP-FormulaNet (LaTeX OCR) on single answer options (docs/experiments/2026-11-ppformulanet.md).

Steps, each writing under data/interim/ (gitignored: the files hold M3Kang text):

pick   choose options of Catalan and Spanish text-only rows, by kind (words,
       units, formulas with letters), with a fixed seed. Reads the PP-OCRv5
       boxes that laptop/ocr_boxes.py wrote.
crop   cut each option out of its image, using the PP-OCRv5 box of its label.
       --wide keeps a large margin; the default keeps a tight one.
run    run PP-FormulaNet on the crops and record the time and the output of
       each crop. Needs paddleocr 3.x and paddlex[ocr].
score  compare outputs with a reference file written by hand from the crops
       ({"00.png": "x + 1", ...}). It prints counts only.

Usage (from the repo root):
    python laptop/formula_trial.py pick
    python laptop/formula_trial.py crop --wide --out data/interim/formula_crops
    python laptop/formula_trial.py crop --out data/interim/formula_crops_tight
    python laptop/formula_trial.py run --model PP-FormulaNet_plus-M --crops data/interim/formula_crops_tight
    python laptop/formula_trial.py score
"""
import argparse
import io
import json
import os
import random
import re
import sys
import time
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from prepare_m3kang import parse_options  # noqa: E402

INTERIM = "data/interim"
BOXES_V5 = f"{INTERIM}/ocr_boxes_txto_yes_v5.jsonl"
BOXES_V4 = f"{INTERIM}/ocr_boxes_txto_yes.jsonl"
PICK = f"{INTERIM}/formula_pick.json"
TIMING = f"{INTERIM}/formula_timing.json"
GOLD = f"{INTERIM}/formula_gold.json"
SHARD = "data/raw_txto_yes/high_quality-00000-of-00004.parquet"


def load_boxes(path):
    return {r["key"]: r["boxes"] for r in map(json.loads, open(path))}


def kind(value):
    if re.search(r"[A-Za-z]{3,}", value) and not re.search(r"\d", value) or re.search(r"\b(o|y|i)\b", value):
        return "words"
    if re.search(r"(\d\s*(cm|km|dm|mm|ml|kg|m|g|l|h|min)\b)|°|€|%", value):
        return "units"
    if re.search(r"[a-z]", value) and re.search(r"[=<>+×·√²³−-]", value):
        return "formula"
    return None


def pick(args):
    v5, v4 = load_boxes(BOXES_V5), load_boxes(BOXES_V4)
    found = defaultdict(list)
    for key, boxes in v5.items():
        if key.split("|")[1] not in ("cat", "esp"):
            continue
        options = parse_options(boxes) or parse_options(v4[key])
        for letter, value in options.items():
            k = kind(value)
            if k:
                found[k].append((key, letter, value))
    random.seed(args.seed)
    chosen = random.sample(found["words"], 8) + random.sample(found["units"], 6) + random.sample(found["formula"], 6)
    json.dump(chosen, open(PICK, "w"), ensure_ascii=False)
    print({k: len(v) for k, v in found.items()}, "->", len(chosen), "options in", PICK)


def is_label(text, letter):
    return re.match(rf"^\s*{letter}\s*([\)）\]:.]|$|[-+−\d])", text)


def crop(args):
    import pyarrow.parquet as pq
    from PIL import Image

    os.makedirs(args.out, exist_ok=True)
    v5 = load_boxes(BOXES_V5)
    table = pq.read_table(SHARD, columns=["id", "language", "image"])
    index = {f"{i}|{lang}": n for n, (i, lang) in
             enumerate(zip(table.column("id").to_pylist(), table.column("language").to_pylist()))}
    for n, (key, letter, _) in enumerate(json.load(open(PICK))):
        img = Image.open(io.BytesIO(table.column("image")[index[key]].as_py()["bytes"])).convert("RGB")
        width, height = img.size
        boxes = [(min(p[0] for p in b), min(p[1] for p in b), max(p[0] for p in b), max(p[1] for p in b), t)
                 for b, t, _ in v5[key]]
        x0, y0, x1, y1, _ = max((b for b in boxes if is_label(b[4], letter)), key=lambda b: b[1])
        h, yc = y1 - y0, (y0 + y1) / 2
        right = [b[0] for b in boxes if letter != "E" and is_label(b[4], chr(ord(letter) + 1))
                 and abs((b[1] + b[3]) / 2 - yc) < h]
        xr = min(right) - 4 if right else width
        if args.wide:
            box = (x0 - 1.6 * h, y0 - 1.2 * h, xr, y1 + 2.2 * h)
        else:
            # A second line of the same option: a box just below, in this column.
            below = [b for b in boxes if y1 < b[1] < y1 + 1.5 * h and x0 - 2 * h < b[0] < xr]
            left = min([x0] + [b[0] for b in below])
            box = (left - 2, y0 - 0.35 * h, xr, (max(b[3] for b in below) if below else y1) + 0.35 * h)
        box = (max(0, int(box[0])), max(0, int(box[1])), min(width, int(box[2])), min(height, int(box[3])))
        img.crop(box).save(os.path.join(args.out, f"{n:02d}.png"))
    print("crops in", args.out)


def run(args):
    from paddleocr import FormulaRecognition

    results = json.load(open(TIMING)) if os.path.exists(TIMING) else {}
    tag = f"{args.model}|{os.path.basename(args.crops.rstrip('/'))}|t{args.threads}"
    model = FormulaRecognition(model_name=args.model, device="cpu", cpu_threads=args.threads)
    files = sorted(f for f in os.listdir(args.crops) if f.endswith(".png"))
    model.predict(os.path.join(args.crops, files[0]))  # warm-up, not timed
    rows = {}
    for f in files:
        t0 = time.time()
        text = model.predict(os.path.join(args.crops, f))[0]["rec_formula"]
        rows[f] = {"s": round(time.time() - t0, 2), "len": len(text), "text": text}
    results[tag] = rows
    json.dump(results, open(TIMING, "w"), ensure_ascii=False, indent=1)
    times = sorted(r["s"] for r in rows.values())
    print(f"{tag}: mean {sum(times) / len(times):.2f} s/crop, median {times[len(times) // 2]:.2f}, "
          f"max {times[-1]:.2f}, outputs over 500 characters: {sum(r['len'] > 500 for r in rows.values())}")


UNICODE = {"−": "-", "–": "-", "—": "-", "≤": "\\leq", "≥": "\\geq", "∞": "\\infty", "²": "^2", "³": "^3",
           "⁴": "^4", "×": "\\times", "·": "\\cdot"}


def normalize(text):
    """Reduce a LaTeX or plain option to a bare string, so that equal options compare equal."""
    for a, b in UNICODE.items():
        text = text.replace(a, b)
    text = re.sub(r"\\(begin|end)\{[^}]*\}(\{[^}]*\})?", "", text)
    text = re.sub(r"\\textcircled\{[A-E]\}", "", text)
    text = re.sub(r"\\(text|mathrm|operatorname|mathsf|textit|mathit|mathbf|bf)\b", "", text)
    text = text.replace("\\%", "%")
    text = re.sub(r"\\(left|right)\b", "", text)
    text = re.sub(r"\\(quad|qquad|;|,|!| )|[$~&{}_]|\\\\", "", text)
    text = re.sub(r"\s+", "", text)
    text = re.sub(r"^\(?[A-E]\)", "", text)  # the option label
    text = re.sub(r"(?<=[A-Za-z])-(?=[a-z])", "", text)  # a word split over two lines
    return text.rstrip(".") if not text.endswith("..") else text


def score(args):
    gold = json.load(open(GOLD))
    picks = json.load(open(PICK))
    results = json.load(open(TIMING))
    v5 = {f"{n:02d}.png": p[2] for n, p in enumerate(picks)}
    runs = [("PP-OCRv5 (parsed)", v5)] + [(tag, {f: r["text"] for f, r in rows.items()})
                                          for tag, rows in results.items()]
    print(f"{len(gold)} options. Exact match after normalize().")
    for name, out in runs:
        hits = [f for f in sorted(gold) if normalize(out.get(f, "")) == normalize(gold[f])]
        print(f"  {name:48} {len(hits):>2}/{len(gold)}   missed: {' '.join(f[:2] for f in sorted(gold) if f not in hits)}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("pick")
    s.add_argument("--seed", type=int, default=4)
    s = sub.add_parser("crop")
    s.add_argument("--wide", action="store_true")
    s.add_argument("--out", required=True)
    s = sub.add_parser("run")
    s.add_argument("--model", default="PP-FormulaNet_plus-M")
    s.add_argument("--crops", required=True)
    s.add_argument("--threads", type=int, default=10)
    sub.add_parser("score")
    args = p.parse_args()
    {"pick": pick, "crop": crop, "run": run, "score": score}[args.cmd](args)


if __name__ == "__main__":
    main()
