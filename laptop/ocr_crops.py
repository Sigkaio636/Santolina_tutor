#!/usr/bin/env python3
"""Run PP-OCRv5 on the option crops made by notebooks/option_crops_opencv.ipynb.

The notebook writes data/interim/option_crops/manifest.jsonl, one line per crop:
{"key": "id|lang", "kind": "region" | "region_mask" | "A".."E", "path": "<png under option_crops/>", ...}.
"region_mask" is the masked image; its line also holds "options", the five OpenCV regions.
This script reads each crop, adds a white border (the text detector misses text that
touches the edge), runs make_engine("v5") from ocr_boxes.py and appends
{"key", "kind", "boxes"} to --out. It resumes: (key, kind) pairs already in --out are
skipped. It never prints problem text.

M3Kang is research-use only: crops and boxes hold problem content, so both stay
under data/ (gitignored).

Usage (the ocr-v5 environment, GPU):
    ~/.venvs/ocr-v5/bin/python laptop/ocr_crops.py
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ocr_boxes import make_engine  # noqa: E402

BORDER = 16  # px of white added around each crop before OCR


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--crops", default="data/interim/option_crops")
    p.add_argument("--out", default="data/interim/ocr_boxes_crops_v5.jsonl")
    args = p.parse_args()

    import cv2

    manifest = [json.loads(line) for line in open(os.path.join(args.crops, "manifest.jsonl"))]
    done = set()
    if os.path.exists(args.out):
        done = {(r["key"], r["kind"]) for r in map(json.loads, open(args.out))}
    todo = [m for m in manifest if (m["key"], m["kind"]) not in done]
    print(f"{len(manifest)} crops in the manifest, {len(todo)} to run", flush=True)
    run = make_engine("v5")
    t0 = time.time()
    with open(args.out, "a") as f:
        for n, m in enumerate(todo, 1):
            img = cv2.imread(os.path.join(args.crops, m["path"]), cv2.IMREAD_COLOR)
            img = cv2.copyMakeBorder(img, BORDER, BORDER, BORDER, BORDER, cv2.BORDER_CONSTANT,
                                     value=(255, 255, 255))
            ok, png = cv2.imencode(".png", img)
            boxes = run(png.tobytes()) if ok else []
            # Back to crop coordinates (without the border).
            boxes = [[[[float(x) - BORDER, float(y) - BORDER] for x, y in box], text, float(score)]
                     for box, text, score in boxes]
            f.write(json.dumps({"key": m["key"], "kind": m["kind"], "boxes": boxes}, ensure_ascii=False) + "\n")
            if n % 500 == 0:
                print(f"  {n} crops, {n / (time.time() - t0):.1f} crops/s", flush=True)
    if todo:
        print(f"{len(todo)} crops in {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
