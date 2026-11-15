"""Join the grid runs into one table for the solver dashboard: one row per (setup, problem, language).

No problem text, options or programs leave this script: only ids, levels, lengths, option kinds,
token counts, board seconds and outcomes (M3Kang licence; the practice set is private).

    python3 -I reports/solver-dashboard/build_solver_data.py [--ocr-dir data]
"""
import argparse
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GRID = ROOT / "data/grid"
OUT = Path(__file__).resolve().parent / "data/solver_rows.csv"

# file stem -> (dataset, model, prompt, input language, translated, extra board seconds before the request)
RUNS = {
    "demo-program9-noema-opp-eng": ("practice", "Noema-2B", "examples", "eng", False, 0),
    "demo-program9-noema-opp-cat": ("practice", "Noema-2B", "examples", "cat", False, 0),
    "demo-program11-qmath-eng": ("practice", "Qwen-Math", "examples", "eng", False, 0),
    "demo-program11-qmath-cat": ("practice", "Qwen-Math", "examples", "cat", False, 0),
    "demo-program13-qmath-nmt-cat": ("practice", "Qwen-Math", "examples", "cat", True, 3),
    "demo-ft-qmath-zero_shot-eng": ("practice", "Qwen-Math FT", "examples", "eng", False, 0),
    "demo-ft-qmath-zero_shot-nmt-cat": ("practice", "Qwen-Math FT", "examples", "cat", True, 3),
    "demo-ft-qmath-tuned-eng": ("practice", "Qwen-Math FT", "short", "eng", False, 0),
    "demo-ft-qmath-tuned-nmt-cat": ("practice", "Qwen-Math FT", "short", "cat", True, 3),
    "demo-ft-noema-tuned-eng": ("practice", "Noema-2B FT", "short", "eng", False, 0),
    "demo-ft-noema-tuned-nmt-cat": ("practice", "Noema-2B FT", "short", "cat", True, 3),
    "demo-ft-noema-zs-eng": ("practice", "Noema-2B FT", "examples", "eng", False, 0),
    "demo-ft-noema-zs-nmt-cat": ("practice", "Noema-2B FT", "examples", "cat", True, 3),
    "m3-base-zero_shot-eng": ("M3Kang", "Qwen-Math", "examples", "eng", False, 0),
    "m3-base-zero_shot-cat": ("M3Kang", "Qwen-Math", "examples", "cat", False, 0),
    "m3-base-zero_shot-nmt-cat": ("M3Kang", "Qwen-Math", "examples", "cat", True, 3),
    "m3-ftqmath-tuned-eng": ("M3Kang", "Qwen-Math FT", "short", "eng", False, 0),
    "m3-ftqmath-tuned-cat": ("M3Kang", "Qwen-Math FT", "short", "cat", False, 0),
    "m3-ftqmath-tuned-nmt-cat": ("M3Kang", "Qwen-Math FT", "short", "cat", True, 3),
    "m3-ftqmath-zero_shot-eng": ("M3Kang", "Qwen-Math FT", "examples", "eng", False, 0),
    "m3-ftqmath-zero_shot-cat": ("M3Kang", "Qwen-Math FT", "examples", "cat", False, 0),
    "m3-ftqmath-zero_shot-nmt-cat": ("M3Kang", "Qwen-Math FT", "examples", "cat", True, 3),
}
SPEEDS = {"Noema-2B": (4.86, 2.42), "Noema-2B FT": (4.86, 2.42), "Qwen-Math": (5.2, 3.0), "Qwen-Math FT": (5.2, 3.0)}
SOURCES = [ROOT / "data/demo/train.jsonl", ROOT / "data/finetune/noema-programs/val.jsonl"]
NUM = re.compile(r"^\s*-?\d+(?:[.,]\d+)?(?:/\d+)?\s*[a-zA-Z²³°%]*\s*$")


def option_kind(options):
    if not options or len(options) < 5:
        return "missing"
    vals = [str(options[k]) for k in sorted(options)]
    if not all(NUM.match(v) for v in vals):
        return "words"
    try:
        xs = [float(eval(re.sub(r"[^\d./-]", "", v.replace(",", ".")))) for v in vals]  # digits, / . - only
    except Exception:  # noqa: BLE001
        return "numbers, unsorted"
    return "numbers, sorted" if xs in (sorted(xs), sorted(xs, reverse=True)) else "numbers, unsorted"


def stage(r):
    """The furthest step of the funnel the problem reached."""
    if r["predicted_n"] >= r["budget"]:
        return "1 cut at the token cap"
    if r["error"]:
        return "2 crashed"
    if not r["answer"]:
        return "3 no option matched"
    return "5 right" if r["answer"] == r["label"] else "4 wrong option"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ocr-dir", default=str(ROOT / "data"),
                    help="folder with train.jsonl / val.jsonl from laptop/prepare_m3kang.py")
    ocr_dir = Path(ap.parse_args().ocr_dir)
    problems = {}
    for path in SOURCES:
        for line in open(path, encoding="utf-8"):
            p = json.loads(line)
            problems[(p["id"], p["language"])] = {
                "chars": len(re.sub(r"^\s*\d+\.\s*", "", p["text"])),
                "option_kind": option_kind(p.get("options")),
                "text_only": p.get("text_only"),
            }
    for path in [ocr_dir / "train.jsonl", ocr_dir / "val.jsonl"]:
        for line in open(path, encoding="utf-8"):  # the fine-tune's val file has no text_only
            p = json.loads(line)
            key = (p["id"], p["language"])
            if key in problems and problems[key]["text_only"] is None:
                problems[key]["text_only"] = p.get("text_only")
    out = []
    for stem, (dataset, model, prompt, lang, translated, extra) in RUNS.items():
        read_tps, write_tps = SPEEDS[model]
        for line in open(GRID / f"{stem}.jsonl", encoding="utf-8"):
            r = json.loads(line)
            p = problems[(r["id"], r["language"])]
            final = r["answer"] or r.get("follow_letter") or r.get("prior")
            out.append({
                "setup": f"{model} · {prompt} prompt",
                "dataset": dataset, "model": model, "prompt": prompt, "language": lang,
                "input": "cat → eng (NMT)" if translated else lang,
                "id": r["id"], "level": r["level"], "text_only": p["text_only"],
                "chars": p["chars"], "option_kind": p["option_kind"],
                "read_tokens": r["prompt_n"], "written_tokens": r["predicted_n"], "budget": r["budget"],
                "extra_s": extra, "read_tps": read_tps, "write_tps": write_tps,
                "board_s": r["board_seconds"], "stage": stage(r),
                "program_right": int(r["answer"] == r["label"]),
                "final_right": int(final == r["label"]),
                "answered_by": "program" if r["answer"] else ("letter" if r.get("follow_letter") else "prior"),
            })
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(out[0]))
        writer.writeheader()
        writer.writerows(out)
    print(f"{OUT}: {len(out)} rows, {len(RUNS)} runs")


if __name__ == "__main__":
    main()
