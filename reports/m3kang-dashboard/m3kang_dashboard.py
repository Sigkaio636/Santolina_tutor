"""M3Kang exploration dashboard (shard 0, high_quality, English problems)

Decision records (.claude/vis-decisions/, one per panel; composition on the first):
  p-matrix-pattern-two-keys--exam-completeness-per-level-20261114
  p-compare-two-keys--translated-share-per-language-20261114
  p-compare-two-keys--correct-letter-share-per-level-20261114
  p-compare-two-keys--share-of-problems-needing-the-20261114
  p-distribution-compare-groups--problem-length-per-level-and-20261114
Design document: m3kang_dashboard_design.md
Library: Altair / Vega-Lite (coordinated views) + a small JS problem browser
Generated: 2026-11-14
Questions: Where is the dataset thin (level x year, language)? How biased is the answer
key? How much does each level depend on the image? How long are the problems?
Composition: juxtapose (multiform); links: level picker -> highlight in every view;
coverage cell / letter cell / block dot / length brush -> filter the problem browser.

Run with any Python that has altair + vl_convert + pandas:
    python3 m3kang_dashboard.py            # writes m3kang_dashboard.html next to this file
The CSV comes from build_data.py. Nothing here leaves the machine.
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
DATA_PATH = os.path.join(_HERE, "data", "m3kang_rows.csv")
OUT_DIR = _HERE
SLUG = "m3kang_dashboard"
LANG = "en"
IMG_DIR_REL = "img/eng"           # relative to the HTML file
COLUMNS = {"id": "id", "language": "language", "level": "level", "year": "year", "qnum": "qnum",
           "label": "label", "text_only": "text_only", "words": "text_words", "text": "text"}
PARSE = {"sep": ",", "decimal": ".", "encoding": "utf-8"}

EXAM_SIZE = {0: 24, 1: 24}            # questions per exam; every other level has 30
DEFAULT_EXAM_SIZE = 30
TOKENS_PER_WORD = 1.35               # rough English estimate for the Qwen tokenizer
BOARD_READ_TOK_S = 11                # prompt reading speed measured on the UNO Q (README)
CHANCE = 0.20
BASELINE_ACC = 0.225                 # official baseline accuracy (README)
SOURCE = ("Source: qualcomm/M3Kang, high_quality shard 0. Research-only licence: "
          "do not share outside the datathon.")

# ---------------------------------------------------------------- PALETTE
NEUTRAL, ACCENT = "#9a9a9a", "#d55e00"      # one highlight colour (Okabe-Ito vermillion)
SEQUENTIAL = "blues"
DIVERGING = "blueorange"
FIGURE_COLORS = {"needs image": "#0072b2", "text only": "#56b4e9"}
BLOCK_COLORS = ["#9ecae1", "#4292c6", "#08306b"]   # 3 / 4 / 5 points, light -> dark
FADED = 0.22


def load(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, sep=PARSE["sep"], decimal=PARSE["decimal"], encoding=PARSE["encoding"])
    missing = [c for c in COLUMNS.values() if c not in df.columns]
    assert not missing, f"missing columns: {missing}"
    assert len(df) > 0, "empty dataset"
    print(f"loaded {len(df)} rows from {path}")
    return df


def wilson(k: float, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    den = 1 + z * z / n
    mid = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0.0, mid - half), min(1.0, mid + half))


def derive(df: pd.DataFrame) -> dict:
    """All derived tables (design document, section 2). Returns a dict of frames."""
    eng = df[df["language"] == "eng"].copy()
    eng["exam_size"] = eng["level"].map(EXAM_SIZE).fillna(DEFAULT_EXAM_SIZE).astype(int)
    eng["points"] = 3 + (eng["qnum"] - 1) // (eng["exam_size"] // 3)
    eng["figure"] = eng["text_only"].map({True: "text only", False: "needs image"})
    eng["words"] = eng["text_words"]
    eng["est_tokens"] = (eng["words"] * TOKENS_PER_WORD).round().astype(int)
    eng["read_s"] = (eng["est_tokens"] / BOARD_READ_TOK_S).round(1)
    eng["snippet"] = eng["text"].str.slice(0, 140)
    assert eng["points"].between(3, 5).all(), "question number outside its exam"

    # 1 problems per level (picker)
    per_level = eng.groupby("level").agg(n=("id", "size"), first_year=("year", "min")).reset_index()

    # 2 completeness per level x year (every cell of the grid, blanks where no exam)
    grid = pd.MultiIndex.from_product([sorted(eng["level"].unique()), sorted(eng["year"].unique())],
                                      names=["level", "year"]).to_frame(index=False)
    cov = eng.groupby(["level", "year"]).agg(n=("id", "size"), qs=("qnum", lambda s: set(s))).reset_index()
    cov = grid.merge(cov, on=["level", "year"], how="left")
    cov["exam_size"] = cov["level"].map(EXAM_SIZE).fillna(DEFAULT_EXAM_SIZE).astype(int)
    cov["n"] = cov["n"].fillna(0).astype(int)
    cov["completeness"] = cov["n"] / cov["exam_size"]
    cov["missing_q"] = [
        "no exam in dataset" if not isinstance(q, set) else
        ", ".join(str(i) for i in range(1, size + 1) if i not in q)
        for q, size in zip(cov["qs"], cov["exam_size"])]
    cov = cov.drop(columns="qs")
    cov = cov[cov["n"] > 0].copy()          # blank cell = no exam; said in the subtitle
    cov["light_text"] = cov["completeness"] > 0.6

    # 3 translated share per language x level
    n_eng = eng.groupby("level")["id"].size().rename("n_eng")
    lang = df.groupby(["language", "level"])["id"].size().rename("n").reset_index()
    lang = lang.merge(n_eng, on="level")
    lang["share"] = lang["n"] / lang["n_eng"]
    order = (df.groupby("language")["id"].size() / len(eng)).sort_values(ascending=False)
    lang["lang_total_share"] = lang["language"].map(order)
    lang["light_text"] = lang["share"] > 0.6

    # 4 letter share per level, and best constant guess per level with a 95% Wilson interval
    bias = eng.groupby(["level", "label"]).size().rename("n").reset_index()
    bias = bias.merge(eng.groupby("level").size().rename("level_n"), on="level")
    bias["share"] = bias["n"] / bias["level_n"]
    bias["light_text"] = (bias["share"] - CHANCE).abs() > 0.11
    bias_ci = [wilson(k, n) for k, n in zip(bias["n"], bias["level_n"])]
    bias["lo"], bias["hi"] = [c[0] for c in bias_ci], [c[1] for c in bias_ci]
    bias["clear"] = (bias["lo"] > CHANCE) | (bias["hi"] < CHANCE)   # 95% interval excludes chance
    bias["cell_label"] = [f"{s:.0%}" + (" •" if c else "") for s, c in zip(bias["share"], bias["clear"])]
    best = bias.loc[bias.groupby("level")["share"].idxmax()].copy()
    ci = [wilson(k, n) for k, n in zip(best["n"], best["level_n"])]
    best["lo"], best["hi"] = [c[0] for c in ci], [c[1] for c in ci]

    # 5 share needing the image per level x points block
    fig = eng.groupby(["level", "points"]).agg(n=("id", "size"),
                                               needs=("text_only", lambda s: int((~s).sum()))).reset_index()
    fig["rate"] = fig["needs"] / fig["n"]

    # 6 per-problem table (strip + browser)
    probs = eng[["id", "level", "year", "qnum", "points", "label", "figure", "words",
                 "est_tokens", "read_s", "snippet"]].sort_values(["level", "year", "qnum"])
    med = eng.groupby("level").agg(median_words=("words", "median"), n=("id", "size")).reset_index()

    browser = eng[["id", "level", "year", "qnum", "points", "label", "figure", "words",
                   "est_tokens", "read_s", "text"]].sort_values(["level", "year", "qnum"])
    return {"eng": eng, "per_level": per_level, "cov": cov, "lang": lang, "lang_order": list(order.index),
            "bias": bias, "best": best, "fig": fig, "probs": probs, "med": med, "browser": browser}


def takeaway(d: dict) -> dict:
    """Titles computed from the data (never a literal number)."""
    eng, pl = d["eng"], d["per_level"]
    hi_share = pl.loc[pl["level"] >= 4, "n"].sum() / pl["n"].sum()
    low_first = int(pl.loc[pl["level"] <= 3, "first_year"].min())
    cov = d["cov"]
    lang = d["lang"].groupby("language")["n"].sum() / len(eng)
    full = [l for l, s in lang.items() if s >= 0.999]
    rest = lang.drop(full).sort_values(ascending=False)
    overall = eng["label"].value_counts(normalize=True)
    best = d["best"].sort_values("share", ascending=False).iloc[0]
    fig = eng.groupby("level")["text_only"].apply(lambda s: (~s).mean())
    med = eng["words"].median()
    tok = med * TOKENS_PER_WORD
    return {
        "picker": f"Levels 4–7 hold {hi_share:.0%} of the {len(eng):,} problems; levels 0–3 start in {low_first}",
        "cov": f"The dataset keeps {cov['completeness'].mean():.0%} of each exam on average",
        "lang": f"Only {' and '.join(full)} cover every problem; next is {rest.index[0]} with {rest.iloc[0]:.0%}",
        "bias": (f"Always answering {overall.index[0]} scores {overall.iloc[0]:.0%}; the best letter per "
                 f"level reaches {best['share']:.0%} ({best['label']} at level {int(best['level'])})"),
        "fig": f"{fig.loc[0]:.0%} of level-0 problems need the image, {fig.loc[7]:.0%} at level 7",
        "strip": (f"Median problem: {med:.0f} words, about {tok:.0f} tokens or "
                  f"{tok / BOARD_READ_TOK_S:.0f} s of reading on the board"),
    }


def selections() -> dict:
    return {
        "level": alt.selection_point(name="sel_level", fields=["level"], toggle="true"),
        "cell": alt.selection_point(name="sel_cell", fields=["level", "year"]),
        "letter": alt.selection_point(name="sel_letter", fields=["level", "label"]),
        "block": alt.selection_point(name="sel_block", fields=["level", "points"]),
        "brush": alt.selection_interval(name="sel_brush", encodings=["x"]),
    }


def _fade(sel):
    return alt.when(sel).then(alt.value(1.0)).otherwise(alt.value(FADED))


def _ring(sel):
    return alt.when(sel, empty=False).then(alt.value(ACCENT)).otherwise(alt.value("transparent"))


LEVEL_Y = alt.Y("level:O", title="Level (0 = grade 5)", sort="ascending")
HINT = "click selects · shift-click adds · double-click clears"


def build_views(d: dict, sel: dict, t: dict) -> dict:
    lvl = sel["level"]
    views = {}

    # picker: problems per level, the control view for the level highlight
    base = alt.Chart(d["per_level"])
    bars = base.mark_bar().encode(
        x=alt.X("level:O", title="Level (0 = grade 5)", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("n:Q", title="Problems", scale=alt.Scale(zero=True)),
        color=alt.when(lvl, empty=False).then(alt.value(ACCENT)).otherwise(alt.value(NEUTRAL)),
        tooltip=[alt.Tooltip("level:O", title="Level"), alt.Tooltip("n:Q", title="Problems"),
                 alt.Tooltip("first_year:Q", title="First year")],
    ).add_params(lvl)
    labels = base.mark_text(dy=-6, baseline="bottom", fontSize=12).encode(
        x="level:O", y="n:Q", text="n:Q")
    views["picker"] = (bars + labels).properties(
        width=900, height=110,
        title=alt.Title(t["picker"], subtitle=["Problems per level. Click a level to highlight it in every panel "
                                               "(shift-click adds, double-click clears)."]))

    # coverage heatmap: level x year, completeness
    cov = alt.Chart(d["cov"])
    rect = cov.mark_rect(strokeWidth=2.5).encode(
        x=alt.X("year:O", title="Exam year", axis=alt.Axis(labelAngle=0, labelExpr="'’' + slice(datum.label, 2)")),
        y=LEVEL_Y,
        color=alt.Color("completeness:Q", title="% of exam", scale=alt.Scale(scheme=SEQUENTIAL, domain=[0, 1]),
                        legend=alt.Legend(format=".0%", orient="bottom", gradientLength=160)),
        opacity=_fade(lvl), stroke=_ring(sel["cell"]),
        tooltip=[alt.Tooltip("level:O", title="Level"), alt.Tooltip("year:O", title="Year"),
                 alt.Tooltip("n:Q", title="Problems kept"), alt.Tooltip("exam_size:Q", title="Exam size"),
                 alt.Tooltip("completeness:Q", title="Completeness", format=".0%"),
                 alt.Tooltip("missing_q:N", title="Missing question numbers")],
    ).add_params(sel["cell"])
    txt = cov.mark_text(fontSize=11).encode(
        x="year:O", y=LEVEL_Y, text="n:Q", opacity=_fade(lvl),
        color=alt.when(alt.datum.light_text).then(alt.value("white")).otherwise(alt.value("black")))
    views["cov"] = (rect + txt).properties(
        width=520, height=230,
        title=alt.Title(t["cov"], subtitle=["Share of each exam's questions kept (24 for levels 0–1, 30 otherwise);",
                                            "number = problems kept. Blank = no exam that year. Click a cell to list it.",
                                            "Scope: high_quality shard 0; the standard split was not checked."]))

    # language coverage heatmap
    lang = alt.Chart(d["lang"])
    lrect = lang.mark_rect().encode(
        x=alt.X("level:O", title="Level", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("language:N", title="Language (ISO 639-3)", sort=d["lang_order"]),
        color=alt.Color("share:Q", title="% of problems", scale=alt.Scale(scheme=SEQUENTIAL, domain=[0, 1]),
                        legend=None),
        opacity=_fade(lvl),
        tooltip=[alt.Tooltip("language:N", title="Language"), alt.Tooltip("level:O", title="Level"),
                 alt.Tooltip("n:Q", title="Problems"), alt.Tooltip("n_eng:Q", title="English problems"),
                 alt.Tooltip("share:Q", title="Share", format=".0%")],
    )
    ltxt = lang.mark_text(fontSize=10).encode(
        x="level:O", y=alt.Y("language:N", sort=d["lang_order"]), text=alt.Text("share:Q", format=".0%"),
        opacity=_fade(lvl),
        color=alt.when(alt.datum.light_text).then(alt.value("white")).otherwise(alt.value("black")))
    views["lang"] = (lrect + ltxt).properties(
        width=300, height=270,
        title=alt.Title(t["lang"], subtitle=["Problems available per language, as a share of the English set",
                                            "(same colour scale as the left panel). Sorted by total coverage.",
                                            "Shard 0 only: shards 1–3 hold more languages."]))

    # answer-key bias: diverging heatmap around chance
    bias = alt.Chart(d["bias"])
    brect = bias.mark_rect(strokeWidth=2.5).encode(
        x=alt.X("label:N", title="Correct letter", axis=alt.Axis(labelAngle=0, orient="top")),
        y=LEVEL_Y,
        color=alt.Color("share:Q", title="Share of level",
                        scale=alt.Scale(scheme=DIVERGING, domain=[0, 0.4], domainMid=CHANCE, clamp=True),
                        legend=alt.Legend(format=".0%", orient="bottom", gradientLength=140,
                                          values=[0, 0.1, 0.2, 0.3, 0.4])),
        opacity=_fade(lvl), stroke=_ring(sel["letter"]),
        tooltip=[alt.Tooltip("level:O", title="Level"), alt.Tooltip("label:N", title="Letter"),
                 alt.Tooltip("n:Q", title="Problems"), alt.Tooltip("level_n:Q", title="Problems in level"),
                 alt.Tooltip("share:Q", title="Share", format=".0%"),
                 alt.Tooltip("lo:Q", title="95% low", format=".0%"), alt.Tooltip("hi:Q", title="95% high", format=".0%")],
    ).add_params(sel["letter"])
    btxt = bias.mark_text(fontSize=11).encode(
        x="label:N", y=LEVEL_Y, text="cell_label:N", opacity=_fade(lvl),
        color=alt.when(alt.datum.light_text).then(alt.value("white")).otherwise(alt.value("black")))
    heat = (brect + btxt).properties(width=220, height=230)

    best = alt.Chart(d["best"])
    ref = alt.Chart(pd.DataFrame({"x": [CHANCE, BASELINE_ACC], "what": ["chance", "baseline"],
                                  "align": ["right", "left"], "dx": [-3, 3]}))
    rules = ref.mark_rule(strokeDash=[4, 3], color="#555").encode(x="x:Q")
    rule_txt = alt.layer(*[
        ref.transform_filter(alt.datum.what == w).mark_text(
            dy=-4, dx=dx, align=a, fontSize=10, color="#555", baseline="bottom").encode(
            x="x:Q", y=alt.value(0), text="what:N")
        for w, a, dx in [("chance", "right", -3), ("baseline", "left", 3)]])
    err = best.mark_rule(color=NEUTRAL, strokeWidth=2).encode(
        x=alt.X("lo:Q", title="Accuracy of the best constant guess", scale=alt.Scale(domain=[0, 0.6]),
                axis=alt.Axis(format=".0%")),
        x2="hi:Q", y=LEVEL_Y, opacity=_fade(lvl))
    dots = best.mark_point(filled=True, size=70, color="#333").encode(
        x="share:Q", y=LEVEL_Y, opacity=_fade(lvl),
        tooltip=[alt.Tooltip("level:O", title="Level"), alt.Tooltip("label:N", title="Best letter"),
                 alt.Tooltip("share:Q", title="Accuracy", format=".0%"),
                 alt.Tooltip("lo:Q", title="95% low", format=".0%"), alt.Tooltip("hi:Q", title="95% high", format=".0%")])
    dlab = best.mark_text(dx=10, align="left", fontSize=11).encode(
        x="hi:Q", y=LEVEL_Y, text="label:N", opacity=_fade(lvl))
    guess = alt.layer(rules, rule_txt, err, dots, dlab).properties(width=230, height=230)
    views["bias"] = alt.hconcat(heat, guess, spacing=12).properties(
        title=alt.Title(t["bias"], subtitle=[
            "Left: share of each correct letter per level; orange = more than chance (20%), blue = less.",
            "• = 95% Wilson interval excludes 20%. With ~100–340 problems per level, gaps under ~5–8 points are noise.",
            "Right: the most common letter per level and its accuracy, with a 95% Wilson interval. In-sample:",
            "picking the letter on the same data flatters it. Click a cell to list those problems."]))

    # figure dependence: connected dot plot
    fig = alt.Chart(d["fig"])
    line = fig.mark_line(color="#bbbbbb").encode(
        x="rate:Q", y=LEVEL_Y, detail="level:O", order="points:O", opacity=_fade(lvl))
    pts = fig.mark_point(filled=True, size=90, strokeWidth=2).encode(
        x=alt.X("rate:Q", title="Problems that need the image", scale=alt.Scale(domain=[0, 1]),
                axis=alt.Axis(format=".0%")),
        y=LEVEL_Y,
        color=alt.Color("points:O", title="Question block",
                        scale=alt.Scale(domain=[3, 4, 5], range=BLOCK_COLORS),
                        legend=alt.Legend(orient="bottom", labelExpr="datum.label + ' points'")),
        shape=alt.Shape("points:O", scale=alt.Scale(domain=[3, 4, 5], range=["circle", "square", "triangle-up"]),
                        legend=None),
        opacity=_fade(lvl), stroke=_ring(sel["block"]),
        tooltip=[alt.Tooltip("level:O", title="Level"), alt.Tooltip("points:O", title="Points"),
                 alt.Tooltip("needs:Q", title="Need the image"), alt.Tooltip("n:Q", title="Problems"),
                 alt.Tooltip("rate:Q", title="Share", format=".0%")],
    ).add_params(sel["block"])
    views["fig"] = (line + pts).properties(
        width=330, height=230,
        title=alt.Title(t["fig"], subtitle=["Share with text_only = false per level and question block",
                                            "(3 / 4 / 5 points = first / middle / last third of the exam).",
                                            "Click a dot to list those problems."]))

    # length strip + median
    probs = alt.Chart(d["probs"])
    ticks = probs.mark_tick(thickness=1.5, size=11).encode(
        x=alt.X("words:Q", title="Words in the English statement", scale=alt.Scale(zero=True)),
        y=LEVEL_Y,
        yOffset=alt.YOffset("figure:N", sort=list(FIGURE_COLORS)),
        color=alt.Color("figure:N", title="Problem",
                        scale=alt.Scale(domain=list(FIGURE_COLORS), range=list(FIGURE_COLORS.values())),
                        legend=alt.Legend(orient="bottom")),
        opacity=alt.when(lvl & sel["cell"] & sel["letter"] & sel["block"] & sel["brush"])
        .then(alt.value(0.45)).otherwise(alt.value(0.06)),
        tooltip=[alt.Tooltip("id:N", title="Problem"), alt.Tooltip("words:Q", title="Words"),
                 alt.Tooltip("est_tokens:Q", title="≈ tokens"), alt.Tooltip("read_s:Q", title="≈ s to read on board"),
                 alt.Tooltip("label:N", title="Answer"), alt.Tooltip("snippet:N", title="Text")],
    ).add_params(sel["brush"])
    med = alt.Chart(d["med"])
    mtick = med.mark_tick(color="black", thickness=3, size=26).encode(
        x="median_words:Q", y=LEVEL_Y,
        tooltip=[alt.Tooltip("level:O", title="Level"), alt.Tooltip("median_words:Q", title="Median words"),
                 alt.Tooltip("n:Q", title="n")])
    ntxt = med.mark_text(align="left", dx=6, fontSize=11, color="#555").encode(
        x=alt.value(905), y=LEVEL_Y, text=alt.Text("n:Q", format="d"))
    views["strip"] = alt.layer(ticks, mtick, ntxt).properties(
        width=900, height=250,
        title=alt.Title(t["strip"], subtitle=[
            "One tick per problem (no jitter); upper sub-row = needs image, lower = text only; "
            "black = median per level, n at the right.",
            ""
            f"Tokens ≈ {TOKENS_PER_WORD} × words; reading at ≈ {BOARD_READ_TOK_S} tok/s.",
            "Every selection above fades the ticks it excludes. Drag horizontally to select a length range."]))
    return views


def compose(views: dict, d: dict):
    row2 = alt.hconcat(views["cov"], views["lang"], spacing=40).resolve_scale(color="shared")
    row3 = alt.hconcat(views["bias"], views["fig"], spacing=40).resolve_scale(color="independent")
    n = len(d["eng"])
    chart = alt.vconcat(views["picker"], row2, row3, views["strip"], spacing=34).resolve_scale(
        color="independent", opacity="independent", stroke="independent", shape="independent")
    return chart.properties(
        title=alt.Title(f"M3Kang at a glance: {n:,} problems, {d['eng']['year'].min()}–{d['eng']['year'].max()}",
                        subtitle=[SOURCE, HINT], fontSize=20, anchor="start"),
    ).configure_view(stroke=None).configure_axis(
        labelFontSize=12, titleFontSize=12, gridColor="#eeeeee", domainColor="#bbbbbb", tickColor="#bbbbbb",
    ).configure_title(fontSize=14, subtitleFontSize=12, subtitleColor="#555", anchor="start"
    ).configure_legend(labelFontSize=12, titleFontSize=12)


def build_chart(d: dict):
    return compose(build_views(d, selections(), takeaway(d)), d)


def _js_json(obj) -> str:
    return json.dumps(obj, ensure_ascii=False).replace("</", "<\\/")


def write_page(chart, d: dict, out_dir: str, slug: str) -> str:
    import vl_convert as vlc
    bundle = vlc.javascript_bundle().replace("</script", "<\\/script")
    rows = d["browser"].to_dict(orient="records")
    page = PAGE.format(
        bundle=bundle, spec=_js_json(chart.to_dict()), rows=_js_json(rows), img_dir=IMG_DIR_REL,
        source=SOURCE, n=len(rows))
    path = os.path.join(out_dir, f"{slug}.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(page)
    return path


def save(chart, d: dict, out_dir: str, slug: str) -> list[str]:
    os.makedirs(out_dir, exist_ok=True)
    written = [write_page(chart, d, out_dir, slug)]
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


PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>M3Kang Dataset Explorer</title>
<style>
:root {{ --bg:#ffffff; --fg:#1d1d1f; --muted:#5f6368; --line:#e3e3e3; --accent:#d55e00; --panel:#f7f7f8; }}
body {{ margin:0; background:var(--bg); color:var(--fg); font:14px/1.45 system-ui, sans-serif; }}
main {{ max-width:1240px; margin:0 auto; padding:24px 16px 48px; }}
#vis {{ overflow-x:auto; }}
#vis .mark-text {{ pointer-events:none; }}  /* value labels must not swallow clicks on cells */
h2 {{ font-size:18px; margin:36px 0 4px; }}
.muted {{ color:var(--muted); }}
.bar {{ display:flex; gap:12px; align-items:center; flex-wrap:wrap; margin:8px 0 12px; }}
input[type=search] {{ padding:6px 10px; border:1px solid var(--line); border-radius:6px; min-width:280px; font:inherit; }}
.chips span {{ display:inline-block; background:#fbe9df; color:#8a3a00; border-radius:12px; padding:2px 10px; margin:2px 4px 2px 0; font-size:12px; }}
.wrap {{ display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1fr); gap:16px; }}
@media (max-width:900px) {{ .wrap {{ grid-template-columns:1fr; }} }}
.tablebox {{ max-height:560px; overflow:auto; border:1px solid var(--line); border-radius:8px; }}
table {{ border-collapse:collapse; width:100%; font-size:13px; }}
th, td {{ text-align:left; padding:5px 8px; border-bottom:1px solid var(--line); vertical-align:top; }}
th {{ position:sticky; top:0; background:var(--panel); }}
td.num, th.num {{ text-align:right; font-variant-numeric:tabular-nums; }}
tr:hover {{ background:#fafafa; cursor:pointer; }}
tr.on {{ background:#fbe9df; }}
#detail {{ border:1px solid var(--line); border-radius:8px; padding:12px; background:var(--panel); min-height:200px; }}
#detail img {{ width:100%; height:auto; background:#fff; border:1px solid var(--line); border-radius:4px; }}
#detail .meta {{ font-size:13px; margin:8px 0; }}
#detail .answer {{ font-weight:600; color:var(--accent); }}
footer {{ margin-top:32px; font-size:12px; color:var(--muted); }}
</style></head>
<body><main>
<div id="vis"></div>

<h2>Problem browser</h2>
<div class="muted">Shows the problems that match every active selection above (level, coverage cell, letter cell,
question block, length range) and the search box. Click a row to see the image with its options.</div>
<div class="bar">
  <input id="q" type="search" placeholder="Search text or id (e.g. 'triangle', 'lvl-3_2019')">
  <span id="count" class="muted"></span>
  <span id="chips" class="chips"></span>
</div>
<div class="wrap">
  <div class="tablebox"><table>
    <thead><tr><th>id</th><th class="num">lvl</th><th class="num">year</th><th class="num">q</th><th class="num">pts</th>
    <th>ans</th><th>figure</th><th class="num">words</th><th>text</th></tr></thead>
    <tbody id="rows"></tbody></table></div>
  <div id="detail"><span class="muted">Select a problem.</span></div>
</div>
<footer>{source} English rows only, n = {n}. Images load from {img_dir}/ next to this file.</footer>
</main>
<script type="module">{bundle}</script>
<script type="module">
const spec = {spec};
const ROWS = {rows};
const IMG = "{img_dir}";
const SELS = ["sel_level", "sel_cell", "sel_letter", "sel_block", "sel_brush"];
const LIMIT = 400;
const esc = s => String(s).replace(/[&<>"]/g, c => ({{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}})[c]);
let view = null, active = null;

function predicates() {{
  const preds = [], chips = [];
  for (const name of SELS) {{
    let store = [];
    try {{ store = view.data(name + "_store") || []; }} catch (e) {{ continue; }}
    if (!store.length) continue;
    const fields = store[0].fields.map(f => f.field);
    if (store[0].fields[0].type === "R") {{
      const [lo, hi] = store[0].values[0];
      preds.push(r => r[fields[0]] >= lo && r[fields[0]] <= hi);
      chips.push(`${{fields[0]}} ${{Math.round(lo)}}–${{Math.round(hi)}}`);
    }} else {{
      const tuples = store.map(s => s.values);
      preds.push(r => tuples.some(v => fields.every((f, i) => r[f] === v[i])));
      chips.push(tuples.map(v => fields.map((f, i) => `${{f}}=${{v[i]}}`).join(" ")).join(" | "));
    }}
  }}
  const q = document.getElementById("q").value.trim().toLowerCase();
  if (q) {{ preds.push(r => r.id.toLowerCase().includes(q) || r.text.toLowerCase().includes(q)); chips.push(`"${{q}}"`); }}
  return [preds, chips];
}}

function render() {{
  const [preds, chips] = view ? predicates() : [[], []];
  const hits = ROWS.filter(r => preds.every(p => p(r)));
  document.getElementById("count").textContent =
    `${{hits.length}} of ${{ROWS.length}} problems` + (hits.length > LIMIT ? ` (first ${{LIMIT}} shown)` : "");
  document.getElementById("chips").innerHTML = chips.map(c => `<span>${{esc(c)}}</span>`).join("");
  document.getElementById("rows").innerHTML = hits.slice(0, LIMIT).map(r =>
    `<tr data-id="${{esc(r.id)}}" class="${{r.id === active ? "on" : ""}}"><td>${{esc(r.id)}}</td><td class="num">${{r.level}}</td>
     <td class="num">${{r.year}}</td><td class="num">${{r.qnum}}</td><td class="num">${{r.points}}</td><td>${{r.label}}</td>
     <td>${{r.figure === "needs image" ? "yes" : ""}}</td><td class="num">${{r.words}}</td>
     <td>${{esc(r.text.slice(0, 90))}}${{r.text.length > 90 ? "…" : ""}}</td></tr>`).join("");
}}

function show(id) {{
  const r = ROWS.find(x => x.id === id); if (!r) return;
  active = id;
  document.getElementById("detail").innerHTML = `
    <img src="${{IMG}}/${{encodeURIComponent(r.id)}}.png" alt="Problem ${{esc(r.id)}}"
         onerror="this.replaceWith(Object.assign(document.createElement('div'),{{className:'muted',textContent:'Image not found in ${{IMG}}/'}}))">
    <div class="meta"><b>${{esc(r.id)}}</b> · level ${{r.level}} · ${{r.year}} · question ${{r.qnum}} (${{r.points}} points)
      · ${{esc(r.figure)}} · ${{r.words}} words ≈ ${{r.est_tokens}} tokens ≈ ${{r.read_s}} s on the board</div>
    <div class="meta">Correct answer: <span class="answer">${{r.label}}</span></div>
    <div style="white-space:pre-wrap">${{esc(r.text)}}</div>`;
  render();
}}

document.getElementById("rows").addEventListener("click", e => {{
  const tr = e.target.closest("tr"); if (tr) show(tr.dataset.id);
}});
document.getElementById("q").addEventListener("input", render);

window.vegaEmbed("#vis", spec, {{renderer: "svg", actions: {{export: true, source: false, compiled: false, editor: false}}}})
  .then(res => {{
    view = res.view;
    for (const name of SELS) {{
      try {{ view.addDataListener(name + "_store", () => render()); }} catch (e) {{ console.warn("no store", name, e); }}
    }}
    render();
  }})
  .catch(err => {{ document.getElementById("vis").textContent = "Chart failed: " + err; render(); }});
render();
</script>
</body></html>
"""


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=DATA_PATH)
    ap.add_argument("--out-dir", default=OUT_DIR)
    ap.add_argument("--no-show", action="store_true")
    args, _unknown = ap.parse_known_args(argv)  # tolerate a foreign argv (inspectors)
    d = derive(load(args.data))
    chart = build_chart(d)
    for f in save(chart, d, args.out_dir, SLUG):
        print("wrote", f)
    return chart


if __name__ == "__main__":
    chart = main()
