"""Santolina dashboard: one page in three parts (data, progress, results).

Decision record: see santolina_dashboard_design.md  ·  Library: Altair 5.5 (Vega-Lite 5)
Fuses reports/tukey-dashboard (results), reports/m3kang-dashboard (EDA, aggregates only) and
reports/solver-dashboard (progress funnel). Inputs: data/*.csv written by build_data.py and
../tukey-dashboard/data/*.csv. Aggregates, ids and outcomes only: no problem text.

Run:  uv run --no-project --with altair==5.5.0 --with vl-convert-python==1.7.0 --with pandas \
          python santolina_dashboard.py
"""
from __future__ import annotations

import json
import math
import os
import sys

import altair as alt
import pandas as pd

_HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(_HERE, "data")
TUKEY = os.path.join(_HERE, "..", "tukey-dashboard")
sys.path.insert(0, TUKEY)
import tukey_dashboard as T  # noqa: E402  (results views and statistics)

# ---------------------------------------------------------------- PALETTE (one meaning per colour)
BOARD, LAPTOP, REF = T.BOARD, T.LAPTOP, T.NEUTRAL   # blue = board, orange = laptop, grey = chance
M3K, PRACT = "#cc79a7", "#1b1f24"                    # dataset: reddish purple = M3Kang, ink = practice set
RIGHT = "#009e73"                                    # outcome "right" (bluish green)
LIMIT = "#d55e00"                                    # hard limits only (60 s, free RAM)
INK = "#1b1f24"
T.SEQUENTIAL = "greys"                               # commit counts: neutral
T.ACCENT = "#8c8c8c"                                 # timeline phase band and activity markers: neutral
DATASET = alt.Scale(domain=["M3Kang", "practice set"], range=[M3K, PRACT])
DATASET_SHAPE = alt.Scale(domain=["M3Kang", "practice set"], range=["square", "circle"])
OUTCOMES = ["cut at the token cap", "crashed", "no option matched", "wrong option", "right"]
OUTCOME_COLORS = ["#d9d9d9", "#b0b0b0", "#7f7f7f", "#4d4d4d", RIGHT]
OUTCOME_SHAPES = ["triangle-up", "cross", "square", "diamond", "circle"]
LIMIT_S, RUN_S = 57.0, 1.0                           # grid.py deadline and program run allowance
PICK0 = {"setup": "Qwen-Math · examples prompt", "input": "eng"}


def csv(name: str, folder: str = DATA) -> pd.DataFrame:
    df = pd.read_csv(os.path.join(folder, name))
    assert len(df) > 0, f"empty {name}"
    return df


def _y(field, order=None, title=None, limit=260):
    return alt.Y(field, sort=order, title=title, axis=alt.Axis(ticks=False, domain=False, labelLimit=limit))


# ================================================================ PART 1 · DATA
def eda_year():
    d = csv("eda_level_year.csv")
    years = sorted(d["year"].unique())
    x = alt.X("year:O", sort=years, title=None,
              axis=alt.Axis(labelAngle=0, labelExpr="'’' + substring(datum.label, 2)"))
    y = alt.Y("level:O", title="Level", axis=alt.Axis(ticks=False, domain=False))
    rect = alt.Chart(d).mark_rect(stroke="white", strokeWidth=1).encode(
        x=x, y=y, color=alt.Color("n:Q", scale=alt.Scale(scheme="purples", domain=[0, d["n"].max()]), legend=None),
        tooltip=["level:O", "year:O", alt.Tooltip("n:Q", title="Problems")])
    txt = alt.Chart(d).mark_text(fontSize=10.5).encode(
        x=x, y=y, text="n:Q", color=alt.condition("datum.n > 22", alt.value("white"), alt.value(INK)))
    return alt.layer(rect, txt).properties(
        width=460, height=alt.Step(22),
        title=alt.Title("M3Kang problems per level and year", anchor="start",
                        subtitle=f"English · shard 0 · {d['n'].sum():,} problems · empty = no problems"))


def eda_language():
    d = csv("eda_language.csv").sort_values("n", ascending=False)
    y = _y("language:N", list(d["language"]))
    bars = alt.Chart(d).mark_bar(color=M3K, height=14).encode(
        x=alt.X("n:Q", title="Problems", scale=alt.Scale(domain=[0, 1900])), y=y,
        tooltip=["language:N", "n:Q"])
    t = alt.Chart(d).mark_text(align="left", dx=4, fontSize=11).encode(x="n:Q", y=y, text=alt.Text("n:Q", format=","))
    return alt.layer(bars, t).properties(
        width=300, height=alt.Step(17),
        title=alt.Title("Problems per language", anchor="start", subtitle="M3Kang shard 0 · ISO 639-3"))


def eda_letters():
    d = csv("eda_letters.csv")
    tot = d.groupby(["dataset", "label"])["n"].sum().reset_index()
    tot["share"] = 100 * tot["n"] / tot.groupby("dataset")["n"].transform("sum")
    tot["N"] = tot.groupby("dataset")["n"].transform("sum")
    lo, hi = zip(*[T.wilson(k, n, 1.96) for k, n in zip(tot["n"], tot["N"])])
    tot["lo"], tot["hi"] = lo, hi
    x = alt.X("label:N", title="Correct letter", axis=alt.Axis(labelAngle=0))
    err = alt.Chart(tot).mark_rule(strokeWidth=2, opacity=0.45).encode(
        x=x, y="lo:Q", y2="hi:Q", xOffset="dataset:N", color=alt.Color("dataset:N", scale=DATASET, legend=None))
    pts = alt.Chart(tot).mark_point(size=70, filled=True).encode(
        x=x, xOffset="dataset:N",
        y=alt.Y("share:Q", title="Share of problems (%)", scale=alt.Scale(domain=[0, 40])),
        color=alt.Color("dataset:N", scale=DATASET, legend=alt.Legend(orient="top", title=None)),
        shape=alt.Shape("dataset:N", scale=DATASET_SHAPE, legend=None),
        tooltip=["dataset:N", "label:N", "n:Q", alt.Tooltip("share:Q", format=".1f")])
    ch = alt.Chart(pd.DataFrame({"y": [20]})).mark_rule(color=REF, strokeDash=[4, 3]).encode(y="y:Q")
    return alt.layer(ch, err, pts).properties(
        width=250, height=200,
        title=alt.Title("Answer key", anchor="start", subtitle="95% interval · dashed: 20%"))


def eda_figure():
    d = csv("eda_figure.csv")
    d["share"] = 100 * d["needs_figure"] / d["n"]
    lo, hi = zip(*[T.wilson(k, n, 1.96) for k, n in zip(d["needs_figure"], d["n"])])
    d["lo"], d["hi"] = lo, hi
    x = alt.X("level:O", title="Level", axis=alt.Axis(labelAngle=0))
    err = alt.Chart(d).mark_rule(strokeWidth=2, opacity=0.45).encode(
        x=x, xOffset="dataset:N", y="lo:Q", y2="hi:Q", color=alt.Color("dataset:N", scale=DATASET, legend=None))
    pts = alt.Chart(d).mark_point(size=70, filled=True).encode(
        x=x, xOffset="dataset:N",
        y=alt.Y("share:Q", title="Needs the figure (%)", scale=alt.Scale(domain=[0, 100])),
        color=alt.Color("dataset:N", scale=DATASET, legend=alt.Legend(orient="top", title=None)),
        shape=alt.Shape("dataset:N", scale=DATASET_SHAPE, legend=None),
        tooltip=["dataset:N", "level:O", "n:Q", alt.Tooltip("needs_figure:Q", title="Needs figure"),
                 alt.Tooltip("share:Q", format=".0f")])
    return alt.layer(err, pts).properties(
        width=250, height=200,
        title=alt.Title("Problems that need the figure", anchor="start", subtitle="English · 95% interval"))


def eda_tokens():
    d = csv("eda_tokens.csv")
    d["level"] = d["level"].astype(str)
    order = [str(i) for i in range(8)]
    y = alt.Y("level:N", sort=order, title="Level", axis=alt.Axis(ticks=False, domain=False))
    x = alt.X("tokens:Q", title="Statement length (estimated tokens)", scale=alt.Scale(domain=[0, 220], clamp=True))
    m = alt.Chart(d[d.dataset == "M3Kang"]).mark_tick(color=M3K, opacity=0.25, thickness=1.2, size=14).encode(
        x=x, y=y, tooltip=[alt.Tooltip("tokens:Q", title="Tokens")])
    p = alt.Chart(d[d.dataset == "practice set"]).mark_point(color=PRACT, size=26, filled=False, strokeWidth=1.2,
                                                             yOffset=9).encode(x=x, y=y)
    med = d.groupby(["dataset", "level"])["tokens"].median().reset_index()
    md = alt.Chart(med).mark_tick(thickness=3, size=18).encode(
        x="tokens:Q", y=y, color=alt.Color("dataset:N", scale=DATASET, legend=alt.Legend(orient="top", title=None)),
        tooltip=["dataset:N", "level:N", alt.Tooltip("tokens:Q", title="Median tokens")])
    return alt.layer(m, p, md).properties(
        width=250, height=alt.Step(26),
        title=alt.Title("Statement length", anchor="start",
                        subtitle=["tick: one problem · circle: practice problem", "thick: median · 1.35 tokens per word"]))


def eda_shift():
    d = csv("solver_shift.csv")
    d["dataset"] = d["dataset"].replace({"practice": "practice set"})
    names = {"level": "Level", "length": "Statement length", "option_kind": "Options", "figure": "Figure"}
    order = {"level": [str(i) for i in range(8)], "length": ["≤ 150 chars", "151–300", "> 300"],
             "option_kind": ["numbers, sorted", "numbers, unsorted", "words", "missing"],
             "figure": ["text only", "needs the figure"]}
    panels = []
    for f, title in names.items():
        s = d[d["factor"] == f].copy()
        s["slice"] = s["slice"].astype(str)
        o = [v for v in order[f] if v in set(s["slice"])]
        panels.append(alt.Chart(s).mark_point(size=60, filled=True).encode(
            x=alt.X("share:Q", title="Share of the set's problems" if f == "figure" else None,
                    axis=alt.Axis(format="%"), scale=alt.Scale(domain=[0, 1])),
            y=alt.Y("slice:N", sort=o, title=title, axis=alt.Axis(ticks=False, domain=False)),
            color=alt.Color("dataset:N", scale=DATASET, legend=alt.Legend(orient="top", title=None) if f == "level" else None),
            shape=alt.Shape("dataset:N", scale=DATASET_SHAPE, legend=None),
            tooltip=["dataset:N", "slice:N", "count:Q", alt.Tooltip("share:Q", format=".0%")]
        ).properties(width=300, height=alt.Step(15)))
    return alt.vconcat(*panels, spacing=8).properties(
        title=alt.Title("M3Kang held-out rows and the practice set", anchor="start",
                        subtitle="problems used in the grid runs"))


# ================================================================ PART 2 · PROGRESS
def solver_frames():
    cells = csv("solver_cells.csv")
    pts = csv("solver_points.csv")
    rates = csv("solver_rates.csv")
    for f in (cells, pts, rates):
        f["dataset"] = f["dataset"].replace({"practice": "practice set"})
    right = cells[cells["outcome"] == "right"].set_index(["dataset", "row"])["share"]
    order = {ds: [r for (d_, r), _ in right.sort_values(ascending=False).items() if d_ == ds]
             for ds in ["practice set", "M3Kang"]}
    return cells, pts, rates, order


def selections():
    pick = alt.selection_point(name="run", fields=["setup", "input"], value=[PICK0], empty=False, toggle=False)
    read = alt.param(name="read_tps", value=5.2,
                     bind=alt.binding_range(min=2, max=12, step=0.1, name="Board reading speed (tokens/s) "))
    write = alt.param(name="write_tps", value=3.0,
                      bind=alt.binding_range(min=1, max=8, step=0.1, name="Board writing speed (tokens/s) "))
    return pick, read, write


def funnel(cells, order, pick, ds, legend=True):
    c = cells[cells["dataset"] == ds].copy()
    n = int(c["n"].min()), int(c["n"].max())
    base = alt.Chart(c).encode(
        x=alt.X("outcome:N", sort=OUTCOMES, title=None, axis=alt.Axis(orient="top", labelAngle=0)),
        y=_y("row:N", order[ds], limit=320),
        tooltip=["setup:N", "input:N", "outcome:N", alt.Tooltip("count:Q", title="Problems"),
                 alt.Tooltip("n:Q", title="Problems in the run"), alt.Tooltip("share:Q", format=".0%"),
                 alt.Tooltip("final_right:Q", title="Right after letter fallback")])
    lost = base.transform_filter("!datum.is_right").mark_rect().encode(
        color=alt.Color("share:Q", scale=alt.Scale(scheme="greys", domain=[0, 0.8], clamp=True),
                        legend=alt.Legend(title="Lost", format=".0%", orient="bottom", gradientLength=120) if legend else None))
    win = base.transform_filter("datum.is_right").mark_rect().encode(
        color=alt.Color("share:Q", scale=alt.Scale(scheme="greens", domain=[0, 0.8], clamp=True),
                        legend=alt.Legend(title="Right", format=".0%", orient="bottom", gradientLength=120) if legend else None))
    txt = base.mark_text(fontSize=11.5).encode(
        text="label:N", color=alt.condition("datum.share > 0.4", alt.value("white"), alt.value(INK)))
    ring = base.mark_rect(fill="#ffffff", fillOpacity=0, strokeWidth=2.5, cursor="pointer").encode(
        stroke=alt.condition(pick, alt.value(INK), alt.value("transparent"))).add_params(pick)
    nn = f"{n[0]}" if n[0] == n[1] else f"{n[0]}–{n[1]}"
    return alt.layer(lost, win, txt, ring).resolve_scale(color="independent").properties(
        width=520, height=alt.Step(22),
        title=alt.Title(f"Outcome of each program, {ds}", anchor="start",
                        subtitle=f"laptop grid runs · {nn} problems per run, one language · right = the program's own "
                                 "answer, before the letter fallback · click a row"))


def board_time(pts, pick, read, write, ds):
    p = pts[pts["dataset"] == ds]
    base = alt.Chart(p).transform_filter(pick).transform_calculate(
        read_s=f"datum.extra_s + datum.read_tokens / {read.name}",
        write_s=f"datum.written_tokens / {write.name}").transform_calculate(
        fits=f"datum.read_s + datum.write_s + {RUN_S} <= {LIMIT_S}")
    X = alt.X("read_s:Q", title="Seconds before writing", scale=alt.Scale(domain=[0, 60]))
    Y = alt.Y("write_s:Q", title="Seconds writing", scale=alt.Scale(domain=[0, 60]))
    dots = base.mark_point(size=55, filled=True, opacity=0.9).encode(
        x=X, y=Y,
        color=alt.Color("outcome:N", scale=alt.Scale(domain=OUTCOMES, range=OUTCOME_COLORS),
                        legend=alt.Legend(orient="bottom", title=None, columns=5)),
        shape=alt.Shape("outcome:N", scale=alt.Scale(domain=OUTCOMES, range=OUTCOME_SHAPES), legend=None),
        tooltip=["id:N", "level:O", "outcome:N", alt.Tooltip("read_tokens:Q", title="Tokens read"),
                 alt.Tooltip("written_tokens:Q", title="Tokens written"), alt.Tooltip("budget:Q", title="Token cap")])
    lim = alt.Chart(pd.DataFrame({"read_s": [0, LIMIT_S - RUN_S], "write_s": [LIMIT_S - RUN_S, 0]})).mark_line(
        color=LIMIT, strokeDash=[5, 3]).encode(x=X, y=Y)
    summary = base.transform_calculate(f1="datum.fits ? 1 : 0").transform_aggregate(
        n="count()", fit="sum(f1)").transform_calculate(t="datum.fit + ' of ' + datum.n + ' fit in 57 s'").mark_text(
        align="left", fontSize=11.5).encode(x=alt.value(4), y=alt.value(8), text="t:N")
    return alt.layer(dots, lim, summary).properties(
        width=300, height=260, title=alt.Title(f"Board time of the picked run, {ds}", anchor="start",
                                                subtitle="estimated from token counts · dashed: 57 s"))


def slice_rates(rates, pick):
    rates = rates.copy()
    order = {"level": [str(i) for i in range(8)], "length": ["≤ 150 chars", "151–300", "> 300"],
             "option_kind": ["numbers, sorted", "numbers, unsorted", "words", "missing"],
             "figure": ["text only", "needs the figure"]}
    names = {"level": "Level", "length": "Statement length", "option_kind": "Options", "figure": "Figure"}
    panels = []
    for f, title in names.items():
        r = rates[rates["factor"] == f].copy()
        r["slice"] = r["slice"].astype(str)
        o = [v for v in order[f] if v in set(r["slice"])]
        panels.append(alt.Chart(r).transform_filter(pick).mark_point(filled=True).encode(
            x=alt.X("rate:Q", title="Programs right" if f == "figure" else None, axis=alt.Axis(format="%"),
                    scale=alt.Scale(domain=[0, 1])),
            y=alt.Y("slice:N", sort=o, title=title, axis=alt.Axis(ticks=False, domain=False)),
            color=alt.Color("dataset:N", scale=DATASET, legend=None),
            shape=alt.Shape("dataset:N", scale=DATASET_SHAPE, legend=None),
            size=alt.Size("n:Q", scale=alt.Scale(range=[15, 220], domain=[1, 200]),
                          legend=alt.Legend(title="Problems", orient="right") if f == "level" else None),
            tooltip=["dataset:N", "slice:N", "right:Q", "n:Q", alt.Tooltip("rate:Q", format=".0%")]
        ).properties(width=240, height=alt.Step(15)))
    grid = alt.hconcat(alt.vconcat(panels[0], panels[1], spacing=8), alt.vconcat(panels[2], panels[3], spacing=8),
                       spacing=40)
    return grid.properties(
        title=alt.Title("Picked run by slice", anchor="start", subtitle="dot size: problems in the slice"))


def progress_block():
    cells, pts, rates, order = solver_frames()
    pick, read, write = selections()
    top = alt.vconcat(funnel(cells, order, pick, "practice set", legend=False), funnel(cells, order, pick, "M3Kang"), spacing=24)
    times = alt.hconcat(board_time(pts, pick, read, write, "practice set"),
                        board_time(pts, pick, read, write, "M3Kang"), spacing=30)
    times = times.add_params(read, write).resolve_scale(color="shared", shape="shared")
    return alt.vconcat(top, times, slice_rates(rates, pick), spacing=36).resolve_scale(
        color="independent", shape="independent", size="independent")


def changes():
    """Paired differences: same problems, one change at a time."""
    pts = csv("solver_points.csv")
    pts["dataset"] = pts["dataset"].replace({"practice": "practice set"})
    # same definition as the funnel: the furthest step reached is "right"
    pts["ok"] = (pts["outcome"] == "right").astype(int)
    key = pts.set_index(["dataset", "setup", "input", "id"])["ok"].sort_index()
    pairs = []
    for ds in ["practice set", "M3Kang"]:
        for model in ["Qwen-Math", "Noema-2B"]:
            for prompt in ["examples prompt", "short prompt"]:
                base, ft = f"{model} · {prompt}", f"{model} FT · {prompt}"
                for inp in ["eng", "cat", "cat → eng (NMT)"]:
                    pairs.append(("Fine-tuned", ds, (base, inp), (ft, inp), f"{model} · {inp}"))
                for s in [base, ft]:
                    pairs.append(("Catalan translated", ds, (s, "cat"), (s, "cat → eng (NMT)"),
                                  s.replace(" · examples prompt", "").replace(" · short prompt", " · short")))
    rows = []
    for kind, ds, a, b, label in pairs:
        try:
            x, y = key.loc[(ds, *a)], key.loc[(ds, *b)]
        except KeyError:
            continue
        j = pd.concat([x.rename("a"), y.rename("b")], axis=1, join="inner")
        n = len(j)
        gain, loss = int(((j.b == 1) & (j.a == 0)).sum()), int(((j.b == 0) & (j.a == 1)).sum())
        diff = (gain - loss) / n
        se = math.sqrt(max(gain + loss - (gain - loss) ** 2 / n, 0)) / n
        rows.append({"change": kind, "dataset": ds, "pair": label, "n": n, "gain": gain, "loss": loss,
                     "before": int(j.a.sum()), "after": int(j.b.sum()),
                     "diff": 100 * diff, "lo": 100 * (diff - 1.96 * se), "hi": 100 * (diff + 1.96 * se),
                     "row": f"{kind} · {label} · {ds}"})
    d = pd.DataFrame(rows).sort_values(["change", "dataset", "diff"], ascending=[False, True, False])
    y = _y("row:N", list(d["row"]), limit=330)
    x = alt.X("diff:Q", title="Change in programs right (percentage points)", scale=alt.Scale(domain=[-50, 50]))
    err = alt.Chart(d).mark_rule(color=LAPTOP, strokeWidth=6, opacity=0.3).encode(x="lo:Q", x2="hi:Q", y=y)
    pt = alt.Chart(d).mark_point(color=LAPTOP, shape="diamond", size=80, filled=True).encode(
        x=x, y=y, tooltip=["row:N", "n:Q", alt.Tooltip("before:Q", title="Right before"),
                           alt.Tooltip("after:Q", title="Right after"), alt.Tooltip("gain:Q", title="Newly right"),
                           alt.Tooltip("loss:Q", title="Newly wrong"), alt.Tooltip("diff:Q", format="+.0f")])
    t = alt.Chart(d).mark_text(align="left", dx=8, fontSize=11).encode(
        x="hi:Q", y=y, text=alt.Text("diff:Q", format="+.0f"))
    zero = alt.Chart(pd.DataFrame({"x": [0]})).mark_rule(color=REF).encode(x="x:Q")
    return alt.layer(zero, err, pt, t).properties(
        width=430, height=alt.Step(22),
        title=alt.Title("Effect of one change, same problems", anchor="start",
                        subtitle="paired difference · 95% interval · laptop"))


# ================================================================ PAGE
def theme():
    cfg = T.theme()
    cfg["config"]["title"]["font"] = T.FONT
    return cfg


def main():
    alt.theme.register("santolina", enable=True)(theme)
    df = T.derive(T.load(os.path.join(TUKEY, "data", "solvers.csv")))
    tk = lambda n: pd.read_csv(os.path.join(TUKEY, "data", n))
    prog, paths = tk("progress.csv"), tk("paths.csv")
    core = T.compose_core(T.core_views(df, T.selections())).properties(
        title=alt.Title("Solvers on the organizers' practice set", anchor="start", fontSize=16,
                        subtitle="50 problems × English and Catalan · click a row to highlight it, double-click to clear"))
    specs = {
        "e-year": eda_year(), "e-lang": eda_language(), "e-letters": eda_letters(), "e-figure": eda_figure(),
        "e-tokens": eda_tokens(), "e-ocr": T.ocr_view(tk("ocr.csv")), "e-shift": eda_shift(),
        "p-timeline": T.progress_view(prog), "p-block": progress_block(), "p-changes": changes(),
        "r-core": core, "r-paths": T.paths_view(paths), "r-levels": T.levels_view(tk("levels.csv")),
        "r-ram": T.ram_view(tk("ram.csv")), "r-router": T.router_view(tk("router.csv")),
        "r-activity": T.activity_view(tk("commits.csv")),
    }
    os.makedirs(os.path.join(_HERE, "specs"), exist_ok=True)
    for k, ch in specs.items():
        ch.save(os.path.join(_HERE, "specs", f"{k}.vl.json"))
    ctx = T.kpis(df, prog, paths)
    tpl = open(os.path.join(_HERE, "page_template.html"), encoding="utf-8").read()
    payload = {k: json.loads(ch.to_json()) for k, ch in specs.items()}
    html = tpl.replace("/*__SPECS__*/null", json.dumps(payload, separators=(",", ":")))
    for k, v in ctx.items():
        html = html.replace("{{" + k + "}}", str(v))
    assert "{{" not in html, "unfilled placeholder in page_template.html"
    out = os.path.join(_HERE, "santolina_dashboard.html")
    open(out, "w", encoding="utf-8").write(html)
    print("wrote", out, f"{len(html) / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
