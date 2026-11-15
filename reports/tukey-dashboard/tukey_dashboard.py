"""Which solver should predict.py ship for the 20-problem final test?

Decision record: p-uncertainty-of-estimate-or-forecast--which-solver-to-ship-for-the-20261115-2  ·  Design document: tukey_dashboard_design.md
Library: Altair / Vega-Lite (coordinated views)  ·  Generated: 2026-11-15
Question: Which solver should predict.py use for the final test, given accuracy against
chance, the 60 s limit, English vs Catalan and RAM, and how did we get here in 21 hours?
Composition: juxtapose (multiform on key `solver`); links: click in any core view ->
highlight the same solver in the four core views.

Run:  uv run --with altair==5.5.0 --with vl-convert-python==1.7.0 python tukey_dashboard.py
All inputs are aggregates in data/*.csv; each row names the repo report it comes from.
No M3Kang or practice-set problem text is used.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys

import altair as alt
import pandas as pd

# ---------------------------------------------------------------- CONFIG
_HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(_HERE, "data")
DATA_PATH = os.path.join(DATA_DIR, "solvers.csv")
OUT_DIR = _HERE
SLUG = "tukey_dashboard"
LANG = "en"
COLUMNS = {"key": "solver", "n": "n", "right": "right"}
PARSE = {"sep": ",", "decimal": ".", "encoding": "utf-8"}
CHANCE = 20.0          # practice set: every letter is right on 20 of 100 rows
LIMIT_S, BUDGET_S = 60.0, 55.0
FINAL_N = 20           # problems in the final test

# ---------------------------------------------------------------- PALETTE
# Colour has one meaning on the whole page: where the number was measured.
OKABE_ITO = ["#e69f00", "#56b4e9", "#009e73", "#f0e442", "#0072b2", "#d55e00", "#cc79a7", "#000000"]
NEUTRAL, ACCENT = "#8c8c8c", "#0072b2"
BOARD, LAPTOP = ACCENT, "#e69f00"      # blue = on the UNO Q, orange = laptop estimate
REF = "#8a8f98"                         # reference rules, readable in both themes
SEQUENTIAL = "blues"
FONT = "Atkinson Hyperlegible"
# Solid tints for the 95 / 80 / 50% bands (no stacked opacity, which mixes hues).
TINTS = {"board": ["#cfe3f0", "#8cbfdf", "#3d8fc4"], "laptop": ["#f8e6c4", "#f0c878", "#e69f00"],
         "reference": ["#e4e6e9", "#c9cdd2", "#a3a9b1"]}
W = 190                                  # width of one core column


# ---------------------------------------------------------------- statistics
def wilson(k: int, n: int, z: float) -> tuple[float, float]:
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return 100 * max(0.0, c - h), 100 * min(1.0, c + h)


Z = {"95%": 1.959964, "80%": 1.281552, "50%": 0.674490}


def betabinom_quantiles(k: int, n: int, m: int, qs) -> dict:
    """Posterior predictive of the right answers in m new problems.

    Beta(1 + k, 1 + n - k) posterior on the accuracy (uniform prior), binomial on m.
    """
    a, b = 1 + k, 1 + n - k
    lb = math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)
    pmf = []
    for x in range(m + 1):
        lc = math.lgamma(m + 1) - math.lgamma(x + 1) - math.lgamma(m - x + 1)
        lbx = math.lgamma(x + a) + math.lgamma(m - x + b) - math.lgamma(m + a + b)
        pmf.append(math.exp(lc + lbx - lb))
    cdf, s = [], 0.0
    for v in pmf:
        s += v
        cdf.append(s)
    out = {q: next(x for x, c in enumerate(cdf) if c >= q) for q in qs}
    out["p_beat_chance"] = 1 - cdf[4]          # P(score >= 5), chance median is 4/20
    return out


# ---------------------------------------------------------------- load
def load(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, sep=PARSE["sep"], decimal=PARSE["decimal"], encoding=PARSE["encoding"])
    missing = [c for c in COLUMNS.values() if c not in df.columns]
    assert not missing, f"missing columns: {missing}"
    assert len(df) > 0, "empty dataset"
    print(f"loaded {len(df)} rows from {path}")
    return df


def side(name: str) -> pd.DataFrame:
    p = os.path.join(DATA_DIR, name)
    df = pd.read_csv(p)
    assert len(df) > 0, f"empty {name}"
    print(f"loaded {len(df)} rows from {p}")
    return df


# ---------------------------------------------------------------- derive
def derive(df: pd.DataFrame) -> pd.DataFrame:
    """Core frame: one row per solver (design document, section 2)."""
    df = df.copy()
    df["acc"] = 100 * df["right"] / df["n"]
    # The 100 rows are 50 problems asked in two languages: intervals count problems, not
    # rows (k_eff = accuracy x problems), which is the conservative choice.
    df["k_eff"] = df["right"] * df["problems"] / df["n"]
    for lvl, z in Z.items():
        lo, hi = zip(*[wilson(k, n, z) for k, n in zip(df["k_eff"], df["problems"])])
        df[f"lo{lvl}"], df[f"hi{lvl}"] = lo, hi
    pred = [betabinom_quantiles(k, n, FINAL_N, [0.05, 0.10, 0.25, 0.5, 0.75, 0.90, 0.95])
            for k, n in zip(df["k_eff"], df["problems"])]
    for q, name in [(0.05, "f05"), (0.10, "f10"), (0.25, "f25"), (0.5, "f50"),
                    (0.75, "f75"), (0.90, "f90"), (0.95, "f95")]:
        df[name] = [p[q] for p in pred]
    df["p_beat"] = [100 * p["p_beat_chance"] for p in pred]
    df["eng_pct"] = 2 * df["eng_right"]
    df["cat_pct"] = 2 * df["cat_right"]
    # Reference row: a fixed letter on a balanced test is exactly 20%; its final-test
    # spread is the plain binomial(20, 0.2).
    ref = {"solver": "Any fixed letter (chance)", "measured_on": "reference", "n": 100, "problems": 50,
           "right": 20, "eng_right": 10, "cat_right": 10, "acc": CHANCE, "k_eff": 10,
           "source": "docs/PRACTICE_SET.md: each letter is right on 20 rows"}
    for lvl in Z:
        ref[f"lo{lvl}"] = ref[f"hi{lvl}"] = CHANCE
    cdf, c = [], 0.0
    for x in range(FINAL_N + 1):
        c += math.comb(FINAL_N, x) * 0.2 ** x * 0.8 ** (FINAL_N - x)
        cdf.append(c)
    for q, name in [(0.05, "f05"), (0.10, "f10"), (0.25, "f25"), (0.5, "f50"),
                    (0.75, "f75"), (0.90, "f90"), (0.95, "f95")]:
        ref[name] = next(x for x, v in enumerate(cdf) if v >= q)
    ref["p_beat"] = 100 * (1 - cdf[4])
    df = pd.concat([df, pd.DataFrame([ref])], ignore_index=True)
    df["where"] = df["measured_on"].map({"board": "UNO Q board", "laptop": "Laptop estimate",
                                         "reference": "Chance reference"})
    df["label"] = df["solver"] + df["measured_on"].map({"board": "", "laptop": " · laptop", "reference": ""})
    df = df.sort_values(["acc", "measured_on"], ascending=[False, True]).reset_index(drop=True)
    df.attrs["order"] = list(df["label"])
    return df


def bands(df: pd.DataFrame) -> pd.DataFrame:
    """Long frame of nested intervals for the gradient-interval views."""
    rows = []
    for _, r in df.iterrows():
        for lvl, op in [("95%", 0), ("80%", 1), ("50%", 2)]:
            if r["measured_on"] == "reference":
                continue
            rows.append({"label": r["label"], "where": r["where"], "level": lvl,
                         "tint": TINTS[r["measured_on"]][op],
                         "lo": r[f"lo{lvl}"], "hi": r[f"hi{lvl}"], "acc": r["acc"]})
        for lvl, lo, hi, op in [("90%", "f05", "f95", 0), ("80%", "f10", "f90", 1),
                                ("50%", "f25", "f75", 2)]:
            rows.append({"label": r["label"], "where": r["where"], "level": "final " + lvl,
                         "tint": TINTS[r["measured_on"]][op], "lo": r[lo], "hi": r[hi], "acc": r["f50"]})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- takeaways
def takeaway(df: pd.DataFrame) -> str:
    board = df[df["measured_on"] == "board"].iloc[0]
    lap = df[df["measured_on"] == "laptop"].iloc[0]
    return (f"On the board only {board['solver']} beats chance ({board['acc']:.0f}% vs {CHANCE:.0f}%); "
            f"{lap['solver']} reaches {lap['acc']:.0f}% on the laptop")


def kpis(df: pd.DataFrame, prog: pd.DataFrame, paths: pd.DataFrame) -> dict:
    board = df[df["measured_on"] == "board"].iloc[0]
    lap = df[df["measured_on"] == "laptop"].iloc[0]
    prior = df[df["solver"].str.startswith("Prior")].iloc[0]
    prog_path = paths.iloc[0]
    return {
        "best_board": f"{board['acc']:.0f}%",
        "best_board_ci": f"95% interval {board['lo95%']:.0f}–{board['hi95%']:.0f}%, 50 problems × 2 languages",
        "best_board_name": board["solver"],
        "best_board_final": f"{int(board['f50'])} of {FINAL_N}",
        "best_lap": f"{lap['acc']:.0f}%",
        "best_lap_name": lap["solver"],
        "best_lap_ci": f"95% interval {lap['lo95%']:.0f}–{lap['hi95%']:.0f}%, board run pending",
        "prior": f"{prior['acc']:.0f}%",
        "worst": f"{board['worst_s']:.1f} s",
        "timeouts": int(board["timeouts"]),
        "prog_path_pct": f"{100 * prog_path['right'] / prog_path['rows']:.0f}%",
        "runs": len(prog),
        "prior_ci": f"{prior['lo95%']:.0f}–{prior['hi95%']:.0f}",
        "prog_ci": f"{board['lo95%']:.0f}–{board['hi95%']:.0f}",
        "lap_ci": f"{lap['lo95%']:.0f}–{lap['hi95%']:.0f}",
        "chance_f05": int(df[df.measured_on == "reference"].iloc[0]["f05"]),
        "chance_f95": int(df[df.measured_on == "reference"].iloc[0]["f95"]),
        "prog_f50": int(board["f50"]), "lap_f50": int(lap["f50"]),
    }


# ---------------------------------------------------------------- views
def selections() -> dict:
    return {"pick": alt.selection_point(name="pick", fields=["label"], on="click",
                                        clear="dblclick", empty=True)}


def _y(order, labels: bool):
    return alt.Y("label:N", sort=order, title=None,
                 axis=alt.Axis(labels=labels, ticks=False, domain=False, labelLimit=230,
                               labelFontSize=12.5) if labels else None)


WHERE_SCALE = alt.Scale(domain=["UNO Q board", "Laptop estimate", "Chance reference"],
                        range=[BOARD, LAPTOP, NEUTRAL])
FILL = alt.Fill("measured_on:N", scale=alt.Scale(domain=["board", "laptop", "reference"],
                                                 range=[BOARD, "white", NEUTRAL]), legend=None)
SHAPE = alt.Shape("where:N", scale=alt.Scale(domain=["UNO Q board", "Laptop estimate", "Chance reference"],
                                             range=["circle", "diamond", "square"]), legend=None)


def core_views(df: pd.DataFrame, sel: dict) -> dict:
    pick = sel["pick"]
    order = df.attrs["order"]
    bd = bands(df)
    dim = alt.condition(pick, alt.value(1.0), alt.value(0.18))
    h = alt.Step(30)

    # A: accuracy, gradient interval
    acc_b = bd[~bd["level"].str.startswith("final")]
    xa = alt.X("lo:Q", scale=alt.Scale(domain=[0, 75]), title="Right answers (% of 100 rows)")
    band_a = alt.Chart(acc_b).mark_bar(height=16).encode(
        x=xa, x2="hi:Q", y=_y(order, True),
        color=alt.Color("tint:N", scale=None),
        opacity=alt.condition(pick, alt.value(1.0), alt.value(0.12)),
        tooltip=[alt.Tooltip("label:N", title="Solver"), alt.Tooltip("level:N", title="Wilson interval"),
                 alt.Tooltip("lo:Q", format=".1f", title="from %"), alt.Tooltip("hi:Q", format=".1f", title="to %")],
    )
    pts = alt.Chart(df).mark_point(size=80, filled=False, strokeWidth=2, fillOpacity=1).encode(
        x="acc:Q", y=_y(order, True),
        color=alt.Color("where:N", scale=WHERE_SCALE, legend=None),
        fill=FILL, shape=SHAPE, opacity=dim,
        tooltip=[alt.Tooltip("label:N", title="Solver"), alt.Tooltip("right:Q", title="Right of 100"),
                 alt.Tooltip("acc:Q", format=".0f", title="Accuracy %"), alt.Tooltip("source:N", title="Source")],
    ).add_params(pick)
    lab = alt.Chart(df).mark_text(align="left", dx=8, fontSize=12, fontWeight="bold").encode(
        x="hi95%:Q", y=_y(order, True), text=alt.Text("acc:Q", format=".0f"), opacity=dim)
    chance = alt.Chart(pd.DataFrame({"x": [CHANCE]})).mark_rule(color=REF, strokeDash=[4, 3]).encode(x="x:Q")
    chance_t = alt.Chart(pd.DataFrame({"x": [CHANCE], "t": ["any fixed letter 20%"]})).mark_text(
        align="left", dx=4, dy=-6, fontSize=11, color=REF).encode(x="x:Q", y=alt.value(0), text="t:N")
    a = alt.layer(band_a, chance, chance_t, pts, lab).properties(
        width=W + 30, height=h, title=alt.Title("Accuracy", anchor="start",
                                                 subtitle="bands: 50 / 80 / 95% interval"))

    # B: predicted score in the 20-problem final test
    fin = bd[bd["level"].str.startswith("final")]
    xb = alt.X("lo:Q", scale=alt.Scale(domain=[0, FINAL_N]), title="Right answers out of 20")
    band_b = alt.Chart(fin).mark_bar(height=16).encode(
        x=xb, x2="hi:Q", y=_y(order, False),
        color=alt.Color("tint:N", scale=None),
        opacity=alt.condition(pick, alt.value(1.0), alt.value(0.12)),
        tooltip=[alt.Tooltip("label:N", title="Solver"), alt.Tooltip("level:N", title="Predictive interval"),
                 alt.Tooltip("lo:Q", title="from"), alt.Tooltip("hi:Q", title="to")],
    )
    med = alt.Chart(df).mark_tick(thickness=2.5, size=18).encode(
        x="f50:Q", y=_y(order, False), color=alt.Color("where:N", scale=WHERE_SCALE, legend=None),
        opacity=dim,
        tooltip=[alt.Tooltip("label:N", title="Solver"), alt.Tooltip("f50:Q", title="Median of 20"),
                 alt.Tooltip("p_beat:Q", format=".0f", title="P(5 or more right) %")]).add_params(pick)
    pb = alt.Chart(df).transform_calculate(
        pt="datum.p_beat > 99 ? '>99%' : format(datum.p_beat, '.0f') + '%'").mark_text(
        align="left", dx=6, fontSize=11.5, fontStyle="italic").encode(
        x="f95:Q", y=_y(order, False), text="pt:N", opacity=dim)
    ch_b = alt.Chart(pd.DataFrame({"x": [4]})).mark_rule(color=REF, strokeDash=[4, 3]).encode(x="x:Q")
    b = alt.layer(band_b, ch_b, med, pb).properties(
        width=W, height=h, title=alt.Title("Predicted score of 20", anchor="start",
                                            subtitle="tick: median · %: P(5 or more)"))

    # C: English vs Catalan (dumbbell)
    lang = df.melt(id_vars=["label", "where", "measured_on"], value_vars=["eng_pct", "cat_pct"],
                   var_name="lang", value_name="pct")
    lang["lang"] = lang["lang"].map({"eng_pct": "English", "cat_pct": "Catalan"})
    xc = alt.X("pct:Q", scale=alt.Scale(domain=[0, 65]), title="Right answers (%)")
    seg = alt.Chart(df).mark_rule(color=REF, strokeWidth=2).encode(
        x=alt.X("cat_pct:Q", scale=alt.Scale(domain=[0, 65])), x2="eng_pct:Q", y=_y(order, False), opacity=dim)
    dots = alt.Chart(lang).mark_point(size=70, strokeWidth=2, filled=False, fillOpacity=1).encode(
        x=xc, y=_y(order, False),
        shape=alt.Shape("lang:N", scale=alt.Scale(domain=["English", "Catalan"], range=["circle", "square"]),
                        legend=None),
        fill=alt.condition("datum.lang == 'English'", alt.value(NEUTRAL), alt.value("white")),
        color=alt.value(NEUTRAL), opacity=dim,
        tooltip=[alt.Tooltip("label:N", title="Solver"), alt.Tooltip("lang:N", title="Language"),
                 alt.Tooltip("pct:Q", format=".0f", title="Accuracy %")]).add_params(pick)
    ch_c = alt.Chart(pd.DataFrame({"x": [CHANCE]})).mark_rule(color=REF, strokeDash=[4, 3]).encode(x="x:Q")
    first = lang[lang["label"] == order[0]]
    keyt = alt.Chart(first).mark_text(dy=-14, fontSize=11).encode(
        x="pct:Q", y=_y(order, False), text="lang:N")
    c = alt.layer(ch_c, seg, dots).properties(
        width=W - 10, height=h, title=alt.Title("English ●  Catalan ▢", anchor="start",
                                                 subtitle="50 problems each"))

    # D: time per problem against the limit
    timed = df.dropna(subset=["mean_s"])
    untimed = df[df["mean_s"].isna() & (df["measured_on"] != "reference")]
    xd = alt.X("mean_s:Q", scale=alt.Scale(domain=[0, 62]), title="Seconds per problem")
    rng = alt.Chart(timed).mark_rule(strokeWidth=6, opacity=0.35).encode(
        x=xd, x2="worst_s:Q", y=_y(order, False),
        color=alt.Color("where:N", scale=WHERE_SCALE, legend=None))
    mean = alt.Chart(timed).mark_tick(thickness=2.5, size=18).encode(
        x="mean_s:Q", y=_y(order, False), color=alt.Color("where:N", scale=WHERE_SCALE, legend=None),
        opacity=dim,
        tooltip=[alt.Tooltip("label:N", title="Solver"), alt.Tooltip("mean_s:Q", title="Mean s"),
                 alt.Tooltip("worst_s:Q", title="Slowest s"), alt.Tooltip("timeouts:Q", title="Timeouts of 100")]
    ).add_params(pick)
    worst = alt.Chart(timed).mark_text(align="left", dx=5, fontSize=11.5).encode(
        x="worst_s:Q", y=_y(order, False), text=alt.Text("worst_s:Q", format=".1f"), opacity=dim)
    nt = alt.Chart(untimed).mark_text(align="left", fontSize=11, fontStyle="italic", color=REF).encode(
        x=alt.value(4), y=_y(order, False), text=alt.value("not timed on board"))
    lim = alt.Chart(pd.DataFrame({"x": [LIMIT_S], "t": ["60 s limit"]}))
    lim_r = lim.mark_rule(color="#d55e00", strokeWidth=1.5).encode(x="x:Q")
    lim_t = lim.mark_text(align="right", dx=-3, dy=-6, fontSize=11, color="#d55e00").encode(
        x="x:Q", y=alt.value(0), text="t:N")
    d = alt.layer(rng, lim_r, lim_t, mean, worst, nt).properties(
        width=W - 10, height=h, title=alt.Title("Seconds per problem", anchor="start",
                                                 subtitle="board · tick: mean · bar: to slowest"))
    return {"accuracy": a, "final": b, "language": c, "time": d}


def compose_core(views: dict):
    return alt.hconcat(views["accuracy"], views["final"], views["language"], views["time"],
                       spacing=18).resolve_scale(y="shared", color="shared", shape="independent")


def progress_view(prog: pd.DataFrame):
    prog = prog.copy()
    prog["short"] = prog["short"].fillna("")
    prog["acc"] = 100 * prog["right"] / prog["n"]
    lo, hi = zip(*[wilson(k * p / n, p, Z["95%"]) for k, n, p in zip(prog["right"], prog["n"], prog["problems"])])
    prog["lo"], prog["hi"] = lo, hi
    prog["where"] = prog["measured_on"].map({"board": "UNO Q board", "laptop": "Laptop estimate"})
    # best board-verified result so far within each evaluation set
    best = []
    for s, g in prog.sort_values("time").groupby("eval_set", sort=False):
        m = -1
        for _, r in g.iterrows():
            if r["measured_on"] == "board":
                m = max(m, r["acc"])
            if m >= 0:
                best.append({"time": r["time"], "eval_set": s, "best": m})
    best = pd.DataFrame(best)
    end = pd.DataFrame([{"time": "2026-11-15T06:40", "eval_set": "Practice set",
                         "best": best[best.eval_set == "Practice set"]["best"].max()}])
    best = pd.concat([best, end])
    x = alt.X("time:T", title="Time (Madrid), Saturday 14 → Sunday 15 November",
              scale=alt.Scale(domain=["2026-11-14T14:00", "2026-11-15T06:45"]),
              axis=alt.Axis(format="%H:%M", tickCount=10, labelFontSize=12))
    y = alt.Y("acc:Q", title="Right answers (%)", scale=alt.Scale(domain=[0, 70]))
    phase = alt.Chart(pd.DataFrame([{"a": "2026-11-14T23:41", "b": "2026-11-15T06:45"}])).mark_rect(
        opacity=0.07, color=ACCENT).encode(x="a:T", x2="b:T")
    phase_t = alt.Chart(pd.DataFrame([
        {"t": "2026-11-14T23:50", "txt": "practice set (from 23:41) · dashed: any fixed letter, 20%"},
        {"t": "2026-11-14T14:10", "txt": "M3Kang validation · dashed: always D, 23%"}])).mark_text(
        align="left", baseline="top", dy=4, fontSize=11.5, color=REF).encode(x="t:T", y=alt.value(0), text="txt:N")
    floors = alt.Chart(pd.DataFrame([
        {"a": "2026-11-14T14:00", "b": "2026-11-14T23:41", "y": 23.1, "t": "always D ≈ 23%"},
        {"a": "2026-11-14T23:41", "b": "2026-11-15T06:45", "y": 20.0, "t": "any fixed letter 20%"}]))
    fl = floors.mark_rule(color=REF, strokeDash=[4, 3]).encode(x="a:T", x2="b:T", y="y:Q")
    fl_t = floors.mark_text(align="right", dx=-4, dy=12, fontSize=11, color=REF).encode(x="b:T", y="y:Q", text="t:N")
    step = alt.Chart(best).mark_line(interpolate="step-after", color=BOARD, strokeWidth=2).encode(
        x="time:T", y="best:Q", detail="eval_set:N")
    err = alt.Chart(prog).mark_rule(strokeWidth=1.5, opacity=0.5).encode(
        x=x, y=alt.Y("lo:Q"), y2="hi:Q", color=alt.Color("where:N", scale=WHERE_SCALE, legend=None))
    pts = alt.Chart(prog).mark_point(size=80, strokeWidth=2, filled=False, fillOpacity=1).encode(
        x=x, y=y, color=alt.Color("where:N", scale=WHERE_SCALE,
                                  legend=alt.Legend(orient="top", title=None, offset=4)),
        shape=alt.Shape("where:N", scale=alt.Scale(domain=["UNO Q board", "Laptop estimate"],
                                                    range=["circle", "diamond"]), legend=None),
        fill=FILL,
        tooltip=[alt.Tooltip("run:N", title="Run"), alt.Tooltip("eval_set:N", title="Set"),
                 alt.Tooltip("time:T", format="%a %H:%M", title="When"),
                 alt.Tooltip("right:Q", title="Right"), alt.Tooltip("n:Q", title="Rows"),
                 alt.Tooltip("acc:Q", format=".1f", title="Accuracy %"),
                 alt.Tooltip("lo:Q", format=".0f", title="95% from"), alt.Tooltip("hi:Q", format=".0f", title="95% to"),
                 alt.Tooltip("source:N", title="Source")])
    names = alt.Chart(prog[prog["short"] != ""]).mark_text(
        align="left", dx=9, dy=-9, fontSize=11, color=REF).encode(x="time:T", y="acc:Q", text="short:N")
    return alt.layer(phase, phase_t, fl, step, err, pts, names).properties(
        width=880, height=300,
        title=alt.Title("Accuracy of every recorded run", anchor="start",
                        subtitle="95% interval · line: best board result so far"))


def paths_view(paths: pd.DataFrame):
    p = paths.copy()
    p["pct"] = 100 * p["right"] / p["rows"]
    p["txt"] = [f"{k} of {n} right ({100 * k / n:.0f}%)" for k, n in zip(p["right"].astype(int), p["rows"].astype(int))]
    order = list(p.sort_values("rows", ascending=False)["path"])
    y = alt.Y("path:N", sort=order, title=None, axis=alt.Axis(labelLimit=240, ticks=False, domain=False))
    tot = alt.Chart(p).mark_bar(color=NEUTRAL, opacity=0.3, height=20).encode(
        x=alt.X("rows:Q", title="Rows of 100 (bar) and right answers (filled)", scale=alt.Scale(domain=[0, 60])),
        y=y, tooltip=["path:N", "rows:Q", "right:Q", "note:N"])
    ok = alt.Chart(p).mark_bar(color=BOARD, height=20).encode(x="right:Q", y=y, tooltip=["path:N", "right:Q", "note:N"])
    t = alt.Chart(p).mark_text(align="left", dx=6, fontSize=12).encode(x="rows:Q", y=y, text="txt:N")
    p["chance"] = 0.2 * p["rows"]
    exp = alt.Chart(p).mark_tick(color="#1b1f24", thickness=2, size=26).encode(
        x="chance:Q", y=y, tooltip=[alt.Tooltip("chance:Q", format=".1f", title="Expected right at 20%")])
    return alt.layer(tot, ok, exp, t).properties(
        width=280, height=alt.Step(34),
        title=alt.Title("How the program solver answered", anchor="start",
                        subtitle="Noema-2B, board, 100 rows · filled: right · tick: expected at 20%"))


def levels_view(lv: pd.DataFrame):
    lv = lv.copy()
    lv["acc"] = 100 * lv["right"] / lv["n"]
    lo, hi = zip(*[wilson(k / 2, n / 2, Z["95%"]) for k, n in zip(lv["right"], lv["n"])])
    lv["lo"], lv["hi"] = lo, hi
    lv["txt"] = [f"{k}/{n}" for k, n in zip(lv["right"].astype(int), lv["n"].astype(int))]
    x = alt.X("level:O", title="Kangaroo level (0 = grade 5)", axis=alt.Axis(labelAngle=0))
    err = alt.Chart(lv).mark_rule(color=BOARD, strokeWidth=2, opacity=0.4).encode(x=x, y="lo:Q", y2="hi:Q")
    pt = alt.Chart(lv).mark_point(color=BOARD, filled=True, size=70).encode(
        x=x, y=alt.Y("acc:Q", title="Right answers (%)", scale=alt.Scale(domain=[0, 100])),
        tooltip=["level:O", "right:Q", "n:Q", alt.Tooltip("acc:Q", format=".0f")])
    t = alt.Chart(lv).mark_text(dy=-12, fontSize=11).encode(x=x, y="hi:Q", text="txt:N")
    ch = alt.Chart(pd.DataFrame({"y": [CHANCE]})).mark_rule(color=REF, strokeDash=[4, 3]).encode(y="y:Q")
    return alt.layer(ch, err, pt, t).properties(
        width=280, height=200,
        title=alt.Title("Program solver by level", anchor="start",
                        subtitle="both languages · 95% interval"))


def ram_view(ram: pd.DataFrame):
    avail = 2956
    order = list(ram["config"])
    y = alt.Y("config:N", sort=order, title=None, axis=alt.Axis(labelLimit=240, ticks=False, domain=False))
    bars = alt.Chart(ram).mark_bar(height=18).encode(
        x=alt.X("rss_mb:Q", title="Resident memory of the model servers (MB)", scale=alt.Scale(domain=[0, 3700])),
        y=y, color=alt.Color("measured:N", scale=alt.Scale(domain=["board", "estimate"], range=[BOARD, LAPTOP]),
                             legend=None),
        opacity=alt.condition("datum.measured == 'estimate'", alt.value(0.55), alt.value(1)),
        tooltip=["config:N", "rss_mb:Q", "note:N"])
    t = alt.Chart(ram).mark_text(align="left", dx=5, fontSize=12).encode(
        x="rss_mb:Q", y=y, text=alt.Text("rss_mb:Q", format=","))
    rl = alt.Chart(pd.DataFrame({"x": [avail], "t": ["free before a language model loads"]}))
    r = rl.mark_rule(color="#d55e00", strokeWidth=1.5).encode(x="x:Q")
    rt = rl.mark_text(align="right", dx=-4, dy=-8, fontSize=11, color="#d55e00").encode(x="x:Q", y=alt.value(0), text="t:N")
    return alt.layer(bars, r, rt, t).properties(
        width=280, height=alt.Step(34),
        title=alt.Title("Memory of the model servers", anchor="start",
                        subtitle="UNO Q 4 GB · orange: file size, not measured"))


def ocr_view(ocr: pd.DataFrame):
    order = list(ocr.sort_values("order")["step"])
    y = alt.Y("step:N", sort=order, title=None, axis=alt.Axis(labelLimit=240, ticks=False, domain=False))
    bars = alt.Chart(ocr).mark_bar(color=LAPTOP, height=18).encode(
        x=alt.X("coverage_pct:Q", title="Text-only rows with all five options read (%)", scale=alt.Scale(domain=[0, 100])),
        y=y, tooltip=["step:N", "coverage_pct:Q", "rows_with_options:Q"])
    t = alt.Chart(ocr).mark_text(align="right", dx=-5, fontSize=12, color="#1b1f24").encode(
        x="coverage_pct:Q", y=y, text=alt.Text("coverage_pct:Q", format=".1f"))
    return alt.layer(bars, t).properties(
        width=280, height=alt.Step(34),
        title=alt.Title("Rows with all five options read", anchor="start",
                        subtitle="2,277 M3Kang text-only rows, after each OCR change"))


def router_view(rt: pd.DataFrame):
    rt = rt.copy()
    rt["acc"] = 100 * rt["right"] / rt["n"]
    lo, hi = zip(*[wilson(k, n, Z["95%"]) for k, n in zip(rt["right"], rt["n"])])
    rt["lo"], rt["hi"] = lo, hi
    rt["row"] = rt["model"] + " · " + rt["round"].str.extract(r"^(Round \d)")[0]
    order = list(rt["row"])
    y = alt.Y("row:N", sort=order, title=None, axis=alt.Axis(labelLimit=240, ticks=False, domain=False))
    x = alt.X("acc:Q", title="Messages labelled right (%)", scale=alt.Scale(domain=[0, 100]))
    err = alt.Chart(rt).mark_rule(color=LAPTOP, strokeWidth=6, opacity=0.35).encode(x="lo:Q", x2="hi:Q", y=y)
    pt = alt.Chart(rt).mark_point(color=LAPTOP, shape="diamond", size=80, strokeWidth=2).encode(
        x=x, y=y, tooltip=["model:N", "round:N", "right:Q", "n:Q", alt.Tooltip("acc:Q", format=".1f")])
    t = alt.Chart(rt).mark_text(align="left", dx=8, fontSize=12).encode(x="hi:Q", y=y, text=alt.Text("acc:Q", format=".0f"))
    ch = alt.Chart(pd.DataFrame({"x": [CHANCE]})).mark_rule(color=REF, strokeDash=[4, 3]).encode(x="x:Q")
    return alt.layer(ch, err, pt, t).properties(
        width=280, height=alt.Step(30),
        title=alt.Title("Tutor message router", anchor="start",
                        subtitle="5 labels · laptop · 95% interval"))


def activity_view(cm: pd.DataFrame):
    cm = cm.copy()
    cm["t"] = pd.to_datetime(cm["time"], format="%Y-%m-%dT%H:%M")
    cm["hour"] = cm["t"].dt.floor("h")
    hours = pd.date_range("2026-11-14 10:00", "2026-11-15 06:00", freq="h")
    areas = list(cm["area"].value_counts().index)
    grid = pd.MultiIndex.from_product([areas, hours], names=["area", "hour"]).to_frame(index=False)
    cnt = cm.groupby(["area", "hour"]).size().rename("commits").reset_index()
    g = grid.merge(cnt, how="left").fillna({"commits": 0})
    g["h"] = g["hour"].dt.strftime("%a %H")
    tot = cm["area"].value_counts()
    g["area_l"] = g["area"].map(lambda a: f"{a} ({tot[a]})")
    order_h = [h.strftime("%a %H") for h in hours]
    order_a = [f"{a} ({tot[a]})" for a in areas]
    x = alt.X("h:O", sort=order_h, title="Hour (Madrid)", axis=alt.Axis(labelAngle=0, labelFontSize=10.5,
              labelExpr="split(datum.value, ' ')[1]"))
    y = alt.Y("area_l:N", sort=order_a, title=None, axis=alt.Axis(ticks=False, domain=False, labelLimit=220))
    rect = alt.Chart(g).mark_rect(cornerRadius=2, stroke="white", strokeWidth=0.5).encode(
        x=x, y=y,
        color=alt.condition("datum.commits == 0", alt.value("rgba(140,140,140,0.08)"),
                            alt.Color("commits:Q", scale=alt.Scale(scheme=SEQUENTIAL, domain=[0, 8]),
                                      legend=alt.Legend(title="Commits", orient="right", gradientLength=110))),
        tooltip=[alt.Tooltip("area:N", title="Area"), alt.Tooltip("h:N", title="Hour"),
                 alt.Tooltip("commits:Q", title="Commits")])
    txt = alt.Chart(g[g.commits > 0]).mark_text(fontSize=10.5).encode(
        x=x, y=y, text=alt.Text("commits:Q", format=".0f"),
        color=alt.condition("datum.commits >= 4", alt.value("white"), alt.value("#1b1f24")))
    marks = pd.DataFrame([{"h": "Sat 23", "t": "practice set"}, {"h": "Sun 03", "t": "program solver"}])
    mk = alt.Chart(marks).mark_text(dy=-8, fontSize=11, fontWeight="bold", color=ACCENT).encode(
        x=x, y=alt.value(0), text="t:N")
    return alt.layer(rect, txt, mk).properties(
        width=880, height=alt.Step(24),
        title=alt.Title("Commits per hour", anchor="start",
                        subtitle="all branches, merges excluded · Sat 10h to Sun 06h"))


# ---------------------------------------------------------------- page
def save(specs: dict, ctx: dict, out_dir: str, slug: str) -> list[str]:
    os.makedirs(os.path.join(out_dir, "specs"), exist_ok=True)
    written = []
    for k, ch in specs.items():
        p = os.path.join(out_dir, "specs", f"{k}.vl.json")
        ch.save(p)
        written.append(p)
        try:
            import vl_convert as vlc
            png = os.path.join(out_dir, "specs", f"{k}.png")
            spec = ch.to_json().replace(FONT, "DejaVu Sans")
            open(png, "wb").write(vlc.vegalite_to_png(spec, scale=2))
            written.append(png)
        except Exception as e:  # vl_convert missing
            print(f"PNG not rendered for {k} ({e})", file=sys.stderr)
    tpl = open(os.path.join(_HERE, "page_template.html"), encoding="utf-8").read()
    payload = {k: json.loads(ch.to_json()) for k, ch in specs.items()}
    html = tpl.replace("/*__SPECS__*/null", json.dumps(payload, separators=(",", ":")))
    for k, v in ctx.items():
        html = html.replace("{{" + k + "}}", str(v))
    assert "{{" not in html, "unfilled placeholder in page_template.html"
    p = os.path.join(out_dir, f"{slug}.html")
    open(p, "w", encoding="utf-8").write(html)
    written.append(p)
    return written


def theme() -> dict:
    return {"config": {
        "font": FONT, "background": None, "view": {"stroke": None},
        "axis": {"labelFontSize": 12, "titleFontSize": 12, "titleFontWeight": "normal",
                 "gridColor": "#e3e6ea", "domainColor": "#c7ccd2", "tickColor": "#c7ccd2"},
        "title": {"fontSize": 14.5, "fontWeight": 700, "subtitleFontSize": 12, "subtitlePadding": 4,
                  "offset": 12, "font": FONT, "subtitleFont": FONT},
        "legend": {"labelFontSize": 12}}}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=DATA_PATH)
    ap.add_argument("--out-dir", default=OUT_DIR)
    ap.add_argument("--no-show", action="store_true")
    args, _unknown = ap.parse_known_args(argv)
    alt.theme.register("tukey", enable=True)(theme)
    df = derive(load(args.data))
    prog, paths = side("progress.csv"), side("paths.csv")
    sel = selections()
    core = compose_core(core_views(df, sel)).properties(
        title=alt.Title("Solvers on the organizers' practice set", anchor="start", fontSize=17,
                        subtitle="50 problems × English and Catalan · click a row to highlight it, double-click to clear"))
    specs = {
        "core": core,
        "progress": progress_view(prog),
        "paths": paths_view(paths),
        "levels": levels_view(side("levels.csv")),
        "ram": ram_view(side("ram.csv")),
        "ocr": ocr_view(side("ocr.csv")),
        "router": router_view(side("router.csv")),
        "activity": activity_view(side("commits.csv")),
    }
    ctx = kpis(df, prog, paths)
    for f in save(specs, ctx, args.out_dir, SLUG):
        print("wrote", f)
    return specs["core"]


if __name__ == "__main__":
    chart = main()
