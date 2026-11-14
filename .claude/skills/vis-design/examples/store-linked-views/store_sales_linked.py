"""Which stores turn visits into sales?

Decision record: correlation-two-quantities--linked-scatter-and-bars  ·  Design document: store_sales_linked_design.md
Library: Altair / Vega-Lite (coordinated views)  ·  Generated: 2026-11-13
Question: Which stores convert weekly visits into sales, and how much does each store sell in total?
Composition: juxtapose (multiform); links: scatter -> bars (filter), bars -> scatter (highlight)
"""
from __future__ import annotations

import argparse
import os
import sys

import altair as alt
import pandas as pd

# ---------------------------------------------------------------- CONFIG
_HERE = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(_HERE, "store_weeks.csv")   # script-relative; overridable with --data
OUT_DIR = "out"                      # overridable with --out-dir
SLUG = "store_sales_linked"
LANG = "en"
COLUMNS = {"category": "store", "measure": "visits", "measure2": "sales_eur", "time": "week"}
PARSE = {"sep": ",", "decimal": ".", "numeric": ["visits", "sales_eur", "week"]}

# ---------------------------------------------------------------- PALETTE
# One color mapping for the whole composition; one highlight color in every view.
OKABE_ITO = ["#e69f00", "#56b4e9", "#009e73", "#f0e442", "#0072b2", "#d55e00", "#cc79a7", "#000000"]
NEUTRAL, ACCENT = "#8c8c8c", "#0072b2"
SEQUENTIAL = "viridis"
DIVERGING = "blueorange"


def load(path: str) -> pd.DataFrame:
    dtype = {c: str for c in PARSE.get("code_columns", [])}
    df = pd.read_csv(path, sep=PARSE.get("sep", ","), decimal=PARSE.get("decimal", "."),
                     dtype=dtype, encoding=PARSE.get("encoding", "utf-8"))
    for col, fmt in PARSE.get("dates", {}).items():
        df[col] = pd.to_datetime(df[col], format=fmt, errors="coerce")
    for col in PARSE.get("numeric", []):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    sentinel = PARSE.get("sentinels", [])
    if sentinel:
        df = df.replace(sentinel, pd.NA)
    needed = [c for c in COLUMNS.values() if c]
    missing = [c for c in needed if c not in df.columns]
    assert not missing, f"missing columns: {missing}"
    assert len(df) > 0, "empty dataset"
    print(f"loaded {len(df)} rows from {path}")
    return df


def derive(df: pd.DataFrame) -> pd.DataFrame:
    """One tidy frame shared by every view (design document, section 2).

    Scale domains that must stay fixed across selections are computed here, from the
    full data, and stored in df.attrs["domains"].
    """
    out = df.dropna(subset=["store", "visits", "sales_eur"]).copy()
    out["sales_keur"] = out["sales_eur"] / 1000.0          # thousands of euros per store-week
    totals = out.groupby("store")["sales_keur"].sum().sort_values(ascending=False)
    out.attrs["order"] = list(totals.index)
    out.attrs["domains"] = {"total": [0, float(totals.max()) * 1.05]}
    out.attrs["n"] = len(out)
    return out


def takeaway(df: pd.DataFrame) -> str:
    """Title computed from the data (never a literal number)."""
    per = df.groupby("store").agg(sales=("sales_keur", "sum"), visits=("visits", "sum"))
    per["eur_per_visit"] = per["sales"] * 1000 / per["visits"]
    best, busiest = per["eur_per_visit"].idxmax(), per["visits"].idxmax()
    if best == busiest:
        return f"{best} has the most visits and the highest sales per visit"
    return (f"{best} earns the most per visit ({per.loc[best, 'eur_per_visit']:.0f} EUR); "
            f"{busiest}, the busiest store, earns {per.loc[busiest, 'eur_per_visit']:.0f} EUR")


def selections() -> dict:
    """Named selections of the composition: one per link of the decision record.

    Every selection has a name and explicit fields/encodings.
    """
    return {
        "brush": alt.selection_interval(name="brush", encodings=["x", "y"]),   # scatter -> bars (filter)
        "pick": alt.selection_point(name="pick", fields=["store"]),            # bars -> scatter (highlight)
    }


def build_views(df: pd.DataFrame, sel: dict) -> dict:
    """One chart per view id of solution.composition.views.

    Each selection is added (add_params) to exactly one view and read (condition,
    transform_filter, scale domain) by the views it links to. Highlighting uses ACCENT
    against NEUTRAL in every view.
    """
    order = df.attrs["order"]
    highlight = alt.condition(sel["pick"], alt.value(ACCENT), alt.value(NEUTRAL))
    scatter = alt.Chart(df).mark_point(filled=True, size=45, opacity=0.6).encode(
        x=alt.X("visits:Q", title="Visits per week (n)", scale=alt.Scale(zero=False)),
        y=alt.Y("sales_keur:Q", title="Sales per week (thousand EUR)", scale=alt.Scale(zero=False)),
        color=highlight,
        tooltip=[alt.Tooltip("store:N", title="Store"), alt.Tooltip("week:Q", title="Week"),
                 alt.Tooltip("visits:Q", title="Visits (n)"),
                 alt.Tooltip("sales_keur:Q", title="Sales (thousand EUR)", format=".1f")],
    ).add_params(sel["brush"]).properties(
        width=380, height=300,
        title=alt.Title("Each dot is one store-week", subtitle="Drag to restrict the bars to a range"))

    x_total = alt.X("sum(sales_keur):Q", title="Sales in the selected weeks (thousand EUR)",
                    scale=alt.Scale(domain=df.attrs["domains"]["total"]))   # fixed: DAT-14
    y_store = alt.Y("store:N", sort=order, title=None)
    all_bars = alt.Chart(df).mark_bar(color="#d9d9d9").encode(x=x_total, y=y_store)   # context, never filtered
    sel_bars = alt.Chart(df).mark_bar().encode(
        x=x_total, y=y_store, color=highlight,
        tooltip=[alt.Tooltip("store:N", title="Store"),
                 alt.Tooltip("sum(sales_keur):Q", title="Sales (thousand EUR)", format=".0f")],
    ).transform_filter(sel["brush"]).add_params(sel["pick"])
    bars = alt.layer(all_bars, sel_bars).properties(
        width=300, height=300,
        title=alt.Title("Total sales per store", subtitle="Click a store to find its weeks; pale bar = all weeks"))
    return {"scatter": scatter, "bars": bars}


def compose(views: dict, df: pd.DataFrame):
    """Layout of the views; shared scales and legends resolved here."""
    return alt.hconcat(views["scatter"], views["bars"], spacing=30).properties(
        title=alt.Title(takeaway(df), anchor="start", fontSize=16,
                        subtitle=[f"Weekly visits and sales of six stores, weeks 1–26 (n = {df.attrs['n']} store-weeks). "
                                  "Source: synthetic example data."]))


def build_chart(df: pd.DataFrame):
    return compose(build_views(df, selections()), df)


def save(chart, out_dir: str, slug: str) -> list[str]:
    os.makedirs(out_dir, exist_ok=True)
    written = []
    html = os.path.join(out_dir, f"{slug}.html")
    chart.save(html)
    written.append(html)
    spec = os.path.join(out_dir, f"{slug}.vl.json")
    chart.save(spec)
    written.append(spec)
    try:
        png = os.path.join(out_dir, f"{slug}.png")
        chart.save(png, scale_factor=2)   # the default (nothing selected) state
        written.append(png)
    except Exception as e:  # vl_convert missing
        print(f"PNG not rendered ({e}); open the HTML in a browser", file=sys.stderr)
    return written


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=DATA_PATH)
    ap.add_argument("--out-dir", default=OUT_DIR)
    ap.add_argument("--no-show", action="store_true")
    args, _unknown = ap.parse_known_args(argv)  # tolerate a foreign argv (inspectors)
    df = derive(load(args.data))
    chart = build_chart(df)
    for f in save(chart, args.out_dir, SLUG):
        print("wrote", f)
    return chart


if __name__ == "__main__":
    chart = main()
