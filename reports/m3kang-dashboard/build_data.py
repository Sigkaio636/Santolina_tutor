"""Flatten the M3Kang parquet shard into a per-row metadata CSV and extract images.

Run with the venv that has pyarrow + Pillow:
    uv run --no-project --with pandas --with pyarrow --with pillow --with huggingface_hub python build_data.py
Without --parquet it downloads high_quality shard 0 from Hugging Face (cached after the first time).
Outputs (local only, research-only licence, never commit; .gitignore covers them):
    data/m3kang_rows.csv   one row per (problem id, language), no images
    img/eng/<id>.png       English problem images (with the drawn options A-E)
"""
import argparse
import io
import os

import pandas as pd
import pyarrow.compute as pc
import pyarrow.parquet as pq
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SHARD = "data/high_quality-00000-of-00004.parquet"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parquet", help="local shard; default: download qualcomm/M3Kang " + SHARD)
    ap.add_argument("--image-languages", default="eng", help="comma list; '' to skip images")
    args = ap.parse_args()

    if not args.parquet:
        from huggingface_hub import hf_hub_download
        args.parquet = hf_hub_download("qualcomm/M3Kang", SHARD, repo_type="dataset")
    t = pq.read_table(args.parquet)
    d = t.drop(["image"]).to_pandas()
    images = t["image"].to_pylist()
    sizes = [Image.open(io.BytesIO(x["bytes"])).size for x in images]
    d["img_w"] = [w for w, _ in sizes]
    d["img_h"] = [h for _, h in sizes]
    d["img_kb"] = [len(x["bytes"]) // 1024 for x in images]

    parts = d["id"].str.extract(r"lvl-(\d)_(\d{4})_(\d+)").astype(int)
    assert (parts[0] == d["level"]).all(), "level in id disagrees with level column"
    d["year"], d["qnum"] = parts[1], parts[2]
    d["text"] = d["text"].str.strip()
    d["text_chars"] = d["text"].str.len()
    d["text_words"] = d["text"].str.split().str.len()
    d["n_languages"] = d.groupby("id")["language"].transform("size")

    out_csv = os.path.join(HERE, "data", "m3kang_rows.csv")
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    d.to_csv(out_csv, index=False)
    print(f"wrote {out_csv}: {d.shape[0]} rows, {d['id'].nunique()} problems")

    for lang in filter(None, args.image_languages.split(",")):
        sub = t.filter(pc.equal(t["language"], lang))
        folder = os.path.join(HERE, "img", lang)
        os.makedirs(folder, exist_ok=True)
        for pid, im in zip(sub["id"].to_pylist(), sub["image"].to_pylist()):
            with open(os.path.join(folder, f"{pid}.png"), "wb") as f:
                f.write(im["bytes"])
        print(f"wrote {sub.num_rows} images to {folder}")


if __name__ == "__main__":
    main()
