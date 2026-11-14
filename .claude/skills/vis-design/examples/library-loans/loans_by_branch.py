"""Loans per branch, 2019-2024

Decision record: p-compare-values-across-categories--loans-per-branch-20261107  ·  Design document: loans_by_branch_design.md
Library: matplotlib  ·  Generated: 2026-11-07
Question: Which branches lend the most books over the whole period?
"""
from __future__ import annotations

import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

# ---------------------------------------------------------------- CONFIG
_HERE = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(_HERE, "loans.csv")   # script-relative
OUT_DIR = "out"
SLUG = "loans_by_branch"
LANG = "en"
COLUMNS = {"category": "branch", "date": "loan_date", "code": "branch_code"}
PARSE = {"sep": ",", "decimal": ".", "dates": {"loan_date": "%d/%m/%Y"}, "code_columns": ["branch_code"],
         "numeric": ["days_on_loan"], "sentinels": []}

# ---------------------------------------------------------------- PALETTE
OKABE_ITO = ["#e69f00", "#56b4e9", "#009e73", "#f0e442", "#0072b2", "#d55e00", "#cc79a7", "#000000"]
NEUTRAL, ACCENT = "#8c8c8c", "#0072b2"
SEQUENTIAL = "viridis"
DIVERGING = "RdBu"
GRID = "#dddddd"


def load(path: str) -> pd.DataFrame:
    dtype = {c: str for c in PARSE.get("code_columns", [])}
    df = pd.read_csv(path, sep=PARSE.get("sep", ","), decimal=PARSE.get("decimal", "."),
                     dtype=dtype, encoding=PARSE.get("encoding", "utf-8"))
    for col, fmt in PARSE.get("dates", {}).items():
        df[col] = pd.to_datetime(df[col], format=fmt, errors="coerce")
    for col in PARSE.get("numeric", []):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    if PARSE.get("sentinels"):
        df = df.replace(PARSE["sentinels"], pd.NA)
    needed = [c for c in COLUMNS.values() if c]
    missing = [c for c in needed if c not in df.columns]
    assert not missing, f"missing columns: {missing}"
    assert len(df) > 0, "empty dataset"
    print(f"loaded {len(df)} rows from {path}")
    return df


def derive(df: pd.DataFrame) -> pd.DataFrame:
    """Derived data exactly as in the design document, section 2."""
    period = (df[COLUMNS["date"]].min().year, df[COLUMNS["date"]].max().year)
    out = (df.groupby(COLUMNS["category"]).size().rename("loans").reset_index()
             .sort_values("loans", ascending=False).reset_index(drop=True))
    out["share"] = out["loans"] / out["loans"].sum()
    out.attrs["period"] = period
    out.attrs["n"] = int(len(df))
    return out


def takeaway(df: pd.DataFrame) -> str:
    """Title computed from the data (never a literal number)."""
    top = df.iloc[0]
    top3 = df["share"].head(3).sum()
    return (f"{top[COLUMNS['category']]} lends the most books ({top['loans']:,} loans); "
            f"the top three branches make {top3:.0%} of all loans")


def style(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(labelsize=10)


def build_chart(df: pd.DataFrame):
    """Encodings as in the design document, section 3. Returns the Figure."""
    d = df.iloc[::-1]  # barh draws bottom-up: reverse so the largest is on top
    colors = [ACCENT if i >= len(d) - 3 else NEUTRAL for i in range(len(d))]
    fig, ax = plt.subplots(figsize=(8, 5.2))
    bars = ax.barh(d[COLUMNS["category"]], d["loans"], color=colors)
    ax.bar_label(bars, labels=[f"{v:,}" for v in d["loans"]], padding=4, fontsize=9)
    ax.set_xlim(0, d["loans"].max() * 1.12)
    ax.set_xlabel("Loans (count)")
    ax.set_ylabel("")
    ax.xaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    style(ax)
    period = df.attrs.get("period", ("", ""))
    fig.suptitle(takeaway(df), x=0.01, ha="left", fontsize=13, fontweight="bold")
    ax.set_title(f"Loans per branch, {period[0]}–{period[1]}; the three largest branches highlighted",
                 loc="left", fontsize=10, color="#444444")
    fig.text(0.01, 0.005, f"Source: synthetic library system export; n = {df.attrs.get('n', 0):,} loans",
             fontsize=8, color="#666666")
    fig.tight_layout(rect=(0, 0.03, 1, 0.95))
    return fig


def save(fig, out_dir: str, slug: str) -> list[str]:
    os.makedirs(out_dir, exist_ok=True)
    png = os.path.join(out_dir, f"{slug}.png")
    fig.savefig(png, dpi=200, bbox_inches="tight")
    svg = os.path.join(out_dir, f"{slug}.svg")
    fig.savefig(svg, bbox_inches="tight")
    return [png, svg]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=DATA_PATH)
    ap.add_argument("--out-dir", default=OUT_DIR)
    ap.add_argument("--no-show", action="store_true")
    args, _unknown = ap.parse_known_args(argv)  # tolerate a foreign argv (inspectors)
    df = derive(load(args.data))
    fig = build_chart(df)
    for f in save(fig, args.out_dir, SLUG):
        print("wrote", f)
    return fig


if __name__ == "__main__":
    fig = main()
