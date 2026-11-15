"""Where each solver setup loses problems

Decision record: p-compare-two-keys--where-each-solver-setup-loses-20261115  ·  Design document: solver_dashboard_design.md
Library: Altair / Vega-Lite (coordinated views)  ·  Generated: 2026-11-15
Question: Where does each solver setup lose problems (cut at the token cap, crashed, no option
matched, wrong option), on the practice set and on M3Kang?
Composition: three linked views (multiform); links: pick (setup + input) from the funnel heatmap
to the board-time scatter and the proxy panel; read/write speed sliders drive the scatter.

No problem text, options or programs: ids, levels, lengths, token counts and outcomes only.
"""
from __future__ import annotations

import argparse
import os
import sys

import altair as alt
import pandas as pd

# ---------------------------------------------------------------- CONFIG
_HERE = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(_HERE, "data/solver_rows.csv")   # from build_solver_data.py
OUT_DIR = _HERE
SLUG = "solver_dashboard"
LANG = "en"
COLUMNS = {"run": "setup", "input": "input", "dataset": "dataset", "outcome": "stage",
           "read": "read_tokens", "written": "written_tokens", "extra": "extra_s"}
PARSE = {"sep": ",", "decimal": "."}
LIMIT_S = 57.0          # grid.py: the board deadline after the 3 s margin is LIMIT + 2
RUN_S = 1.0             # grid.py: 0.5 s to run the program + 0.5 s of slack
DEFAULT_PICK = {"setup": "Qwen-Math · examples prompt", "input": "eng"}
DEFAULT_READ, DEFAULT_WRITE = 5.2, 3.0   # Qwen-Math board estimate, tokens/s
SOURCE = ("Source: laptop grid runs (llama.cpp 2cbe0ec, board commit), board time estimated from token counts; "
          "practice set = organizers' 50 problems, M3Kang = 83 eng + 80 cat held-out problems. "
          "No problem text is shown.")

# ---------------------------------------------------------------- PALETTE
OKABE_ITO = ["#e69f00", "#56b4e9", "#009e73", "#f0e442", "#0072b2", "#d55e00", "#cc79a7", "#000000"]
NEUTRAL, ACCENT = "#9a9a9a", "#d55e00"          # project accent: Okabe-Ito vermillion
OUTCOMES = ["1 cut at the token cap", "2 crashed", "3 no option matched", "4 wrong option", "5 right"]
OUTCOME_LABEL = {o: o[2:] for o in OUTCOMES}
OUTCOME_COLORS = ["#8fbbe0", "#4a90c8", "#1f5f9e", "#08244f", ACCENT]   # losses light→dark blues, right = accent
DATASET_COLORS = {"practice": "#000000", "M3Kang": "#56b4e9"}


def load(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, sep=PARSE["sep"], decimal=PARSE["decimal"], encoding="utf-8")
    missing = [c for c in COLUMNS.values() if c not in df.columns]
    assert not missing, f"missing columns: {missing}"
    assert len(df) > 0, "empty dataset"
    print(f"loaded {len(df)} rows from {path}")
    return df


def derive(df: pd.DataFrame) -> dict:
    """Tidy frames for the three views (design document, section 2)."""
    df = df.copy()
    df["outcome"] = df["stage"].map(OUTCOME_LABEL)
    df["run"] = df["dataset"] + " · " + df["setup"] + " · " + df["input"]
    df["length"] = pd.cut(df["chars"], [0, 150, 300, 10_000], labels=["≤ 150 chars", "151–300", "> 300"]).astype(str)
    df["figure"] = df["text_only"].map({True: "text only", False: "needs the figure"})

    # view 1: share of the run's problems at each outcome (every cell present, zeros included)
    n = df.groupby("run").size().rename("n")
    cells = (df.groupby(["run", "outcome"]).size().unstack(fill_value=0)
             .reindex(columns=[OUTCOME_LABEL[o] for o in OUTCOMES], fill_value=0)
             .stack().rename("count").reset_index())
    meta = df.groupby("run").agg(dataset=("dataset", "first"), setup=("setup", "first"), input=("input", "first"),
                                 final_right=("final_right", "sum")).join(n).reset_index()
    cells = cells.merge(meta, on="run")
    cells["share"] = cells["count"] / cells["n"]
    cells["label"] = (cells["share"] * 100).round().astype(int).astype(str) + "%"
    cells["is_right"] = cells["outcome"] == "right"
    right = cells[cells["is_right"]].set_index("run")["share"]
    meta["right_share"] = meta["run"].map(right)
    order = (meta.assign(ds=meta["dataset"].map({"practice": 0, "M3Kang": 1}))
             .sort_values(["ds", "right_share"], ascending=[True, False])["run"].tolist())
    cells["row"] = cells["setup"] + " · " + cells["input"]

    # view 3: how the problems differ (one row per distinct problem of each dataset) and how the
    # picked setup does per slice
    probs = df[(df["setup"] == DEFAULT_PICK["setup"]) & df["input"].isin(["eng", "cat"])]
    shift = []
    for factor in ["level", "length", "option_kind", "figure"]:
        g = probs.groupby(["dataset", factor]).size().rename("count").reset_index()
        g["share"] = g["count"] / g.groupby("dataset")["count"].transform("sum")
        shift.append(g.rename(columns={factor: "slice"}).assign(factor=factor, slice=lambda x: x["slice"].astype(str)))
    shift = pd.concat(shift, ignore_index=True)
    rates = []
    for factor in ["level", "length", "option_kind", "figure"]:
        g = df.groupby(["setup", "input", "dataset", factor]).agg(
            n=("program_right", "size"), right=("program_right", "sum")).reset_index()
        rates.append(g.rename(columns={factor: "slice"}).assign(factor=factor, slice=lambda x: x["slice"].astype(str)))
    rates = pd.concat(rates, ignore_index=True)
    rates["rate"] = rates["right"] / rates["n"]
    slice_order = {
        "level": [str(i) for i in range(8)], "length": ["≤ 150 chars", "151–300", "> 300"],
        "option_kind": [k for k in ["numbers, sorted", "numbers, unsorted", "words", "missing"]
                        if k in set(df["option_kind"])],
        "figure": ["text only", "needs the figure"]}

    points = df[["run", "dataset", "setup", "input", "id", "level", "outcome", "read_tokens", "written_tokens",
                 "budget", "extra_s", "program_right"]].copy()
    return {"rows": df, "cells": cells, "order": order, "meta": meta, "points": points,
            "shift": shift, "rates": rates, "slice_order": slice_order}


def takeaway(d: dict) -> str:
    c = d["cells"]
    base = c[c["setup"] == DEFAULT_PICK["setup"]]
    def lost_early(ds, inp):
        s = base[(base["dataset"] == ds) & (base["input"] == inp)]
        return round(100 * s[s["outcome"].isin(["cut at the token cap", "crashed"])]["share"].sum())
    return (f"The base Qwen-Math loses {lost_early('M3Kang', 'eng')}% of M3Kang problems before its program runs, "
            f"against {lost_early('practice', 'eng')}% of the practice set (English)")


def selections() -> dict:
    pick = alt.selection_point(name="pick", fields=["setup", "input"], value=[DEFAULT_PICK],
                               empty=False, toggle=False)
    read = alt.param(name="read_tps", value=DEFAULT_READ,
                     bind=alt.binding_range(min=2, max=12, step=0.1, name="board reading speed (tokens/s) "))
    write = alt.param(name="write_tps", value=DEFAULT_WRITE,
                      bind=alt.binding_range(min=1, max=8, step=0.1, name="board writing speed (tokens/s) "))
    return {"pick": pick, "read": read, "write": write}


def outcome_scale():
    return alt.Scale(domain=[OUTCOME_LABEL[o] for o in OUTCOMES], range=OUTCOME_COLORS)


def funnel(d: dict, sel: dict, dataset: str) -> alt.Chart:
    cells = d["cells"][d["cells"]["dataset"] == dataset]
    rows = [r.split(" · ", 1)[1] for r in d["order"] if r.startswith(dataset + " ")]
    cols = [OUTCOME_LABEL[o] for o in OUTCOMES]
    base = alt.Chart(cells).encode(
        x=alt.X("outcome:N", sort=cols, title=None, axis=alt.Axis(orient="top", labelAngle=0, labelFontWeight="bold")),
        y=alt.Y("row:N", sort=rows, title=None, axis=alt.Axis(labelLimit=320)),
        tooltip=[alt.Tooltip("setup:N"), alt.Tooltip("input:N"), alt.Tooltip("outcome:N"),
                 alt.Tooltip("count:Q", title="problems"), alt.Tooltip("n:Q", title="problems in the run"),
                 alt.Tooltip("share:Q", format=".0%"),
                 alt.Tooltip("final_right:Q", title="right after letter + prior")])
    loss = base.transform_filter("!datum.is_right").mark_rect().encode(
        color=alt.Color("share:Q", scale=alt.Scale(scheme="blues", domain=[0, 0.8], clamp=True),
                        legend=alt.Legend(title="share lost", format=".0%", orient="bottom", gradientLength=160)))
    win = base.transform_filter("datum.is_right").mark_rect().encode(
        color=alt.Color("share:Q", scale=alt.Scale(scheme="oranges", domain=[0, 0.8], clamp=True),
                        legend=alt.Legend(title="share right", format=".0%", orient="bottom", gradientLength=160)))
    text = base.mark_text(fontSize=12).encode(
        text="label:N",
        color=alt.condition("datum.share > 0.4", alt.value("white"), alt.value("#1d1d1f")))
    outline = base.mark_rect(fill="#ffffff", fillOpacity=0, strokeWidth=2.5, cursor="pointer").encode(
        stroke=alt.when(sel["pick"]).then(alt.value("#1d1d1f")).otherwise(alt.value("transparent")),
        opacity=alt.value(1)).add_params(sel["pick"])
    n = int(cells["n"].iloc[0]) if dataset == "practice" else "80–83"
    return alt.layer(loss, win, text, outline).resolve_scale(color="independent").properties(
        width=560, height=alt.Step(24),
        title=alt.Title(f"{dataset}: share of each run's problems at each outcome (n = {n} per run)",
                        subtitle="A program is cut at the cap, crashes, matches no option, matches a wrong one, "
                                 "or is right. Click a row to follow it below."))


def board_time(d: dict, sel: dict, dataset: str) -> alt.Chart:
    pts = d["points"][d["points"]["dataset"] == dataset]
    base = alt.Chart(pts).transform_filter(sel["pick"]).transform_calculate(
        read_s=f"datum.extra_s + datum.read_tokens / {sel['read'].name}",
        write_s=f"datum.written_tokens / {sel['write'].name}",
    ).transform_calculate(
        total_s=f"datum.read_s + datum.write_s + {RUN_S}",
        fits=f"datum.read_s + datum.write_s + {RUN_S} <= {LIMIT_S}")
    dots = base.mark_point(size=60, filled=True, opacity=0.85).encode(
        x=alt.X("read_s:Q", title="seconds before writing (translation + reading)", scale=alt.Scale(domain=[0, 60])),
        y=alt.Y("write_s:Q", title="seconds writing the program", scale=alt.Scale(domain=[0, 60])),
        color=alt.Color("outcome:N", scale=outcome_scale(), title="outcome", legend=alt.Legend(orient="bottom")),
        shape=alt.Shape("outcome:N", scale=alt.Scale(domain=[OUTCOME_LABEL[o] for o in OUTCOMES],
                                                     range=["triangle-up", "cross", "square", "diamond", "circle"]),
                        title="outcome"),
        tooltip=[alt.Tooltip("id:N"), alt.Tooltip("level:O"), alt.Tooltip("outcome:N"),
                 alt.Tooltip("read_tokens:Q", title="tokens read"), alt.Tooltip("written_tokens:Q", title="tokens written"),
                 alt.Tooltip("budget:Q", title="token cap given"), alt.Tooltip("total_s:Q", format=".1f", title="board s")])
    limit = alt.Chart(pd.DataFrame({"x": [0, LIMIT_S - RUN_S], "y": [LIMIT_S - RUN_S, 0]})).mark_line(
        color="#1d1d1f", strokeDash=[5, 3]).encode(
        x=alt.X("x:Q", title="seconds before writing (translation + reading)"),
        y=alt.Y("y:Q", title="seconds writing the program"))
    label = alt.Chart(pd.DataFrame({"x": [2], "y": [LIMIT_S - RUN_S + 1.5], "t": [f"{LIMIT_S:.0f} s limit"]})).mark_text(
        align="left", fontSize=11).encode(
        x=alt.X("x:Q", title="seconds before writing (translation + reading)"),
        y=alt.Y("y:Q", title="seconds writing the program"), text="t:N")
    summary = base.transform_calculate(
        fit1="datum.fits ? 1 : 0", right_fit1="datum.fits && datum.program_right ? 1 : 0",
    ).transform_aggregate(
        n="count()", fit="sum(fit1)", right="sum(program_right)", right_fit="sum(right_fit1)",
    ).transform_calculate(
        t="'fits in time: ' + datum.fit + ' of ' + datum.n + '   ·   right programs still in time: ' "
          "+ datum.right_fit + ' of ' + datum.right"
    ).mark_text(align="left", fontSize=12, fontWeight="bold").encode(
        x=alt.value(0), y=alt.value(-8), text="t:N")
    return alt.layer(dots, limit, label, summary).properties(
        width=330, height=300, title=alt.Title(f"{dataset}: board time of the picked run", offset=18))


def proxy(d: dict, sel: dict) -> alt.VConcatChart:
    names = {"level": "level", "length": "statement length", "option_kind": "options", "figure": "figure"}
    shift_panels, rate_panels = [], []
    for factor, title in names.items():
        order = d["slice_order"][factor]
        s = d["shift"][d["shift"]["factor"] == factor]
        r = d["rates"][d["rates"]["factor"] == factor]
        y = alt.Y("slice:N", sort=order, title=title, scale=alt.Scale(domain=order))
        color = alt.Color("dataset:N", scale=alt.Scale(domain=list(DATASET_COLORS), range=list(DATASET_COLORS.values())),
                          legend=alt.Legend(orient="bottom", title="dataset"))
        shape = alt.Shape("dataset:N", scale=alt.Scale(domain=list(DATASET_COLORS), range=["circle", "square"]))
        shift_panels.append(alt.Chart(s).mark_point(size=70, filled=True).encode(
            x=alt.X("share:Q", title="share of the dataset's problems", axis=alt.Axis(format="%"),
                    scale=alt.Scale(domain=[0, 1])),
            y=y, color=color, shape=shape,
            tooltip=["dataset:N", "slice:N", alt.Tooltip("count:Q", title="problems"),
                     alt.Tooltip("share:Q", format=".0%")]).properties(width=260, height=alt.Step(16)))
        rate_panels.append(alt.Chart(r).transform_filter(sel["pick"]).mark_point(filled=True).encode(
            x=alt.X("rate:Q", title="programs right (share of the slice)", axis=alt.Axis(format="%"),
                    scale=alt.Scale(domain=[0, 1])),
            y=y, color=color, shape=shape,
            size=alt.Size("n:Q", title="problems in the slice", scale=alt.Scale(range=[20, 260], domain=[1, 200])),
            tooltip=["dataset:N", "slice:N", alt.Tooltip("right:Q", title="right"), alt.Tooltip("n:Q", title="problems"),
                     alt.Tooltip("rate:Q", format=".0%")]).properties(width=260, height=alt.Step(16)))
    left = alt.vconcat(*shift_panels, spacing=10).properties(
        title=alt.Title("How the problems differ", subtitle="share of each dataset's problems per slice"))
    right = alt.vconcat(*rate_panels, spacing=10).properties(
        title=alt.Title("How the picked run does on each slice",
                        subtitle="programs right / problems; dot size = problems in the slice"))
    return alt.hconcat(left, right, spacing=50)


def build_views(d: dict, sel: dict) -> dict:
    return {"funnel_practice": funnel(d, sel, "practice"), "funnel_m3": funnel(d, sel, "M3Kang"),
            "time_practice": board_time(d, sel, "practice"), "time_m3": board_time(d, sel, "M3Kang"),
            "proxy": proxy(d, sel)}


def compose(views: dict, d: dict, sel: dict):
    row1 = alt.vconcat(views["funnel_practice"], views["funnel_m3"], spacing=26)
    row2 = alt.hconcat(views["time_practice"], views["time_m3"], spacing=40).add_params(sel["read"], sel["write"])
    hint = ("Sliders: board speeds in tokens/s (default: Qwen-Math estimate 5.2 / 3.0; Noema-2B measured 4.86 / 2.42). "
            "Points move with the speeds; a point above the dashed line no longer fits. "
            "Programs cut at the cap needed more tokens than shown, so faster speeds don't rescue them here.")
    return alt.vconcat(
        row1,
        row2.properties(title=alt.Title("1 · What the board speeds change", subtitle=hint)),
        views["proxy"].properties(title=alt.Title("2 · Is M3Kang a fair stand-in for the practice set?",
                                                  subtitle="If the picked run's rates match slice by slice, the gap "
                                                           "comes from the mix of problems, not from the slices.")),
        spacing=40,
    ).resolve_scale(color="independent", shape="independent", size="independent").properties(
        title=alt.Title(takeaway(d), subtitle=[SOURCE], fontSize=18, anchor="start"),
    ).configure_view(stroke=None).configure_axis(
        labelFontSize=12, titleFontSize=12, gridColor="#eeeeee", domainColor="#bbbbbb", tickColor="#bbbbbb",
    ).configure_title(fontSize=14, subtitleFontSize=12, subtitleColor="#555", anchor="start"
    ).configure_legend(labelFontSize=12, titleFontSize=12)


def build_chart(d: dict):
    sel = selections()
    return compose(build_views(d, sel), d, sel)


STICKY_CSS = """<style>
#vis.vega-embed .chart-wrapper { display: flex; flex-direction: column; }
#vis.vega-embed .vega-bindings { order: -1; position: sticky; top: 0; z-index: 10; background: #ffffffee;
  padding: 8px 12px; border-bottom: 1px solid #e3e3e3; font: 13px sans-serif; display: flex; gap: 28px; }
</style>
"""


def save(chart, out_dir: str, slug: str) -> list[str]:
    os.makedirs(out_dir, exist_ok=True)
    written = []
    html = os.path.join(out_dir, f"{slug}.html")
    chart.save(html, inline=True)      # offline: Vega bundled into the file
    with open(html, encoding="utf-8") as f:
        page = f.read()
    assert page.lstrip().lower().startswith("<!doctype html>") and "<head>" in page[:500], "unexpected HTML"
    with open(html, "w", encoding="utf-8") as f:   # keep the speed sliders in view while scrolling
        f.write(page.replace("<head>", "<head>\n" + STICKY_CSS, 1))
    written.append(html)
    spec = os.path.join(out_dir, f"{slug}.vl.json")
    chart.save(spec)
    written.append(spec)
    try:
        png = os.path.join(out_dir, f"{slug}.png")
        chart.save(png, scale_factor=2)   # the default state: base Qwen-Math, English picked
        written.append(png)
    except Exception as e:  # vl_convert missing
        print(f"PNG not rendered ({e}); open the HTML in a browser", file=sys.stderr)
    return written


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=DATA_PATH)
    ap.add_argument("--out-dir", default=OUT_DIR)
    ap.add_argument("--no-show", action="store_true")
    args, _unknown = ap.parse_known_args(argv)
    d = derive(load(args.data))
    chart = build_chart(d)
    for f in save(chart, args.out_dir, SLUG):
        print("wrote", f)
    return chart


if __name__ == "__main__":
    chart = main()
