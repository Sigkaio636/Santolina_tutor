"""Load the problems for predict.py and eval.py, with their images when there are any.

Two inputs:
- the organizers' parquet (M3Kang format: id, language, text, image, ...): the image
  bytes go in problem["image"]. Needs pyarrow (unpacked into NMT_SITE on the board).
- a JSONL file, one problem per line. problem["image"] is a file path when the line has an
  "image" field, or when <images>/<id>_<language>.png exists. <images> defaults to the
  "images" folder next to the JSONL, where laptop/prepare_m3kang.py --save-images puts them.
"""
import json
import os
import sys

from .config import CONFIG


def _parquet(path):
    site = os.path.expanduser(CONFIG.get("NMT_SITE", "~/nmt-site"))
    if os.path.isdir(site) and site not in sys.path:
        sys.path.insert(0, site)
    import pyarrow.parquet as pq
    problems = []
    for row in pq.read_table(path).to_pylist():
        image = row.pop("image", None)
        row["image"] = image.get("bytes") if isinstance(image, dict) else image
        row.setdefault("options", {})
        problems.append(row)
    return problems


def load(path, images=None):
    if path.endswith(".parquet"):
        return _parquet(path)
    with open(path) as f:
        problems = [json.loads(line) for line in f if line.strip()]
    folder = images or os.path.join(os.path.dirname(os.path.abspath(path)), "images")
    for problem in problems:
        given = problem.get("image")
        if isinstance(given, str):
            if not os.path.isabs(given) and not os.path.exists(given):
                given = os.path.join(folder, given)
            problem["image"] = given if os.path.exists(given) else None
        else:
            found = os.path.join(folder, f"{problem['id']}_{problem.get('language', '')}.png")
            problem["image"] = found if os.path.exists(found) else None
    return problems
