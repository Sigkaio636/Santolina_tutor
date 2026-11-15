"""Write the aggregate CSVs of the Santolina dashboard (data/*.csv). No problem text leaves this script.

Inputs (local only, never committed):
  --parquet   M3Kang high_quality shard 0 (high_quality-00000-of-00004.parquet)
  --practice  the organizers' practice set prepared by laptop/prepare_m3kang.py (data/demo/train.jsonl)
  --solver    the built solver dashboard (reports/solver-dashboard/solver_dashboard.html): its embedded
              frames already hold only ids, levels, token counts, seconds and outcomes

Outputs (aggregates, safe to commit under the M3Kang red line):
  data/eda_level_year.csv   English problems per level and year
  data/eda_language.csv     problems per language
  data/eda_letters.csv      correct-letter counts per dataset and level
  data/eda_figure.csv       problems needing the figure per dataset and level
  data/eda_tokens.csv       statement length in estimated tokens, one row per problem, no id
  data/solver_cells.csv, solver_points.csv, solver_shift.csv, solver_rates.csv

Run from the repository root:
  uv run --no-project --with pandas --with pyarrow python reports/santolina-dashboard/build_data.py \
      --parquet <shard> --practice data/demo/train.jsonl
"""
import argparse
import json
import os
import re

import pandas as pd
import pyarrow.parquet as pq

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
TOKENS_PER_WORD = 1.35   # same estimate as reports/m3kang-dashboard


def eda(parquet: str, practice: str, out: str) -> None:
    m = pq.read_table(parquet, columns=["id", "level", "language", "text_only", "label", "text"]).to_pandas()
    m["year"] = m["id"].str.extract(r"lvl-\d_(\d{4})_")[0].astype(int)
    eng = m[m["language"] == "eng"].copy()

    eng.groupby(["level", "year"]).size().rename("n").reset_index().to_csv(f"{out}/eda_level_year.csv", index=False)
    m.groupby("language")["id"].nunique().rename("n").reset_index().to_csv(f"{out}/eda_language.csv", index=False)

    p = pd.read_json(practice, lines=True)
    p = p[p["language"] == "eng"].copy()
    p["text_only"] = p["text_only"].astype(str).str.lower() == "true"
    frames = {"M3Kang": eng, "practice set": p}

    letters, figure, tokens = [], [], []
    for name, d in frames.items():
        d = d.copy()
        d["level"] = d["level"].astype(int)
        letters.append(d.groupby(["level", "label"]).size().rename("n").reset_index().assign(dataset=name))
        figure.append(d.groupby("level").agg(n=("id", "size"), needs_figure=("text_only", lambda s: int((~s).sum())))
                      .reset_index().assign(dataset=name))
        words = d["text"].str.strip().str.split().str.len()
        tokens.append(pd.DataFrame({"dataset": name, "level": d["level"].values,
                                    "tokens": (words * TOKENS_PER_WORD).round().astype(int).values}))
    pd.concat(letters).to_csv(f"{out}/eda_letters.csv", index=False)
    pd.concat(figure).to_csv(f"{out}/eda_figure.csv", index=False)
    pd.concat(tokens).sort_values(["dataset", "level", "tokens"]).to_csv(f"{out}/eda_tokens.csv", index=False)


def solver(html_path: str, out: str) -> None:
    """Pull the frames Altair embedded in the built solver dashboard."""
    html = open(html_path, encoding="utf-8").read()
    frames = []
    for m in re.finditer(r'"datasets":\s*\{', html):
        i, depth = m.end() - 1, 0
        for j in range(i, len(html)):
            depth += {"{": 1, "}": -1}.get(html[j], 0)
            if depth == 0:
                break
        frames += [pd.DataFrame(v) for v in json.loads(html[i:j + 1]).values()]
    pick = lambda cols: pd.concat([f for f in frames if set(cols) <= set(f.columns)], ignore_index=True)
    cells = pick(["outcome", "share", "final_right", "row"])
    points = pick(["read_tokens", "written_tokens", "program_right", "id"])
    shift = pick(["factor", "slice", "share", "count"])
    rates = pick(["factor", "slice", "rate", "setup"])
    shift = shift[~shift.columns.isin(["setup"])] if "setup" in shift else shift
    for name, f in {"cells": cells, "points": points, "shift": shift, "rates": rates}.items():
        f.drop_duplicates().to_csv(f"{out}/solver_{name}.csv", index=False)
        print(f"solver_{name}: {len(f.drop_duplicates())} rows")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parquet", required=True)
    ap.add_argument("--practice", default=os.path.join(REPO, "data", "demo", "train.jsonl"))
    ap.add_argument("--solver", default=os.path.join(REPO, "reports", "solver-dashboard", "solver_dashboard.html"))
    args = ap.parse_args()
    out = os.path.join(HERE, "data")
    os.makedirs(out, exist_ok=True)
    eda(args.parquet, args.practice, out)
    solver(args.solver, out)
    for f in sorted(os.listdir(out)):
        print("wrote", os.path.join("data", f))


if __name__ == "__main__":
    main()
