"""Teacher models: cost vs quality of the generated explanations

Decision record: p-distribution-compare-groups--teacher-models-cost-vs-20261114  ·  Design document: teacher_cost_quality_design.md
Library: Altair / Vega-Lite (coordinated views)  ·  Generated: 2026-11-14
Question: How do output tokens and seconds per problem compare across the teacher models,
and how often does each produce a usable record?
Composition: juxtapose (multiform); links: model pick (summary -> every view),
problem pick (any per-call view -> every per-call view)

Data: data/processed/explanations/metrics.csv, built by
`python -m santolina_tutor.explanation_metrics` from raw/<model>.jsonl. Numbers only, no
problem text.
"""

from __future__ import annotations

import argparse
import os
import sys

import altair as alt
import pandas as pd

# ---------------------------------------------------------------- CONFIG
_HERE = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(_HERE, "..", "..", "data", "processed", "explanations", "metrics.csv")
OUT_DIR = os.path.join(_HERE, "out")
SLUG = "teacher_cost_quality"
LANG = "en"
COLUMNS = {
    "model": "teacher",
    "problem": "id",
    "language": "language",
    "level": "level",
    "tokens": "completion_tokens",
    "reasoning": "reasoning_tokens",
    "seconds": "seconds",
    "usable": "usable",
}
PARSE = {"sep": ",", "decimal": ".", "code_columns": ["id", "language", "label", "final_answer"]}
SOURCE = "Source: Helmcode API runs on M3Kang problems (data/processed/explanations/raw)"

# ---------------------------------------------------------------- PALETTE
# Status is the only hue: grey = usable, vermillion = not usable (second cue: shape).
# Selections never add a hue; they fade what is not selected (one highlight rule).
NEUTRAL, ACCENT = "#8c8c8c", "#d55e00"
STATUS = ["usable", "not usable"]
STATUS_SCALE = alt.Scale(domain=STATUS, range=[NEUTRAL, ACCENT])
SHAPE_SCALE = alt.Scale(domain=STATUS, range=["circle", "diamond"])
FADED = 0.15


def load(path: str) -> pd.DataFrame:
    dtype = {c: str for c in PARSE["code_columns"]}
    df = pd.read_csv(path, sep=PARSE["sep"], decimal=PARSE["decimal"], dtype=dtype)
    for col in ("completion_tokens", "reasoning_tokens", "seconds", "prompt_tokens", "level"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    missing = [c for c in COLUMNS.values() if c not in df.columns]
    assert not missing, f"missing columns: {missing}"
    assert len(df) > 0, "empty dataset"
    print(f"loaded {len(df)} rows from {path}")
    return df


def derive(df: pd.DataFrame) -> pd.DataFrame:
    """One tidy frame shared by every view (design document, section 2).

    Per call: status, throughput, problem key. Per model (repeated on each row so every
    view reads the same frame): usable count, n, median tokens, median seconds, total
    tokens. Fixed domains and the model order are computed here, from the full data.
    """
    df = df.copy()
    df["usable"] = df["usable"].astype(str).str.lower().eq("true")
    df["status"] = df["usable"].map({True: "usable", False: "not usable"})
    df["problem"] = df["id"] + "/" + df["language"]
    df["tokens_per_s"] = (df["completion_tokens"] / df["seconds"]).round(0)
    g = df.groupby("teacher")
    df["n_calls"] = g["problem"].transform("size")
    df["n_usable"] = g["usable"].transform("sum")
    df["usable_pct"] = (100 * df["n_usable"] / df["n_calls"]).round(0)
    # Rounded half up here, so the title and the chart labels show the same number.
    df["median_tokens"] = (g["completion_tokens"].transform("median") + 0.5).astype(int)
    df["median_seconds"] = (g["seconds"].transform("median") + 0.5).astype(int)
    df["total_tokens_k"] = (g["completion_tokens"].transform("sum") / 1000).round(1)
    df["zero"] = 0  # baseline for the lollipop stems
    df["usable_label"] =df["n_usable"].astype(int).astype(str) + "/" + df["n_calls"].astype(str)
    # Best first: most usable, then the cheapest median output.
    summary = df.drop_duplicates("teacher").sort_values(
        ["usable_pct", "median_tokens"], ascending=[False, True]
    )
    df.attrs["order"] = summary["teacher"].tolist()
    df.attrs["domains"] = {
        "tokens": [0, float(df["completion_tokens"].max()) * 1.05],
        "seconds": [0, float(df["seconds"].max()) * 1.05],
    }
    return df


def takeaway(df: pd.DataFrame) -> str:
    """Title computed from the data (never a literal number)."""
    s = df.drop_duplicates("teacher").set_index("teacher")
    cheap = s["median_tokens"].idxmin()
    fast = s["median_seconds"].idxmin()
    if s["usable_pct"].nunique() == 1:
        quality = f"all models are usable on {s['usable_label'].iloc[0]} problems"
    else:
        best = s["usable_pct"].idxmax()
        quality = f"{best} is usable most often ({s.loc[best, 'usable_label']})"
    lead = (
        f"{cheap} is cheapest and fastest"
        if cheap == fast
        else f"{cheap} writes the fewest tokens, {fast} is fastest"
    )
    return (
        f"{lead} (median {int(s.loc[cheap, 'median_tokens'] + 0.5):,} tokens, "
        f"{int(s.loc[fast, 'median_seconds'] + 0.5)} s); {quality}"
    )


def selections() -> dict:
    """Named selections, one per link of the decision record."""
    return {
        "model": alt.selection_point(name="model", fields=["teacher"], empty=True),
        "problem": alt.selection_point(name="problem", fields=["problem"], empty=True,
                                       on="click", clear="dblclick"),
    }


def _tooltip():
    return [
        alt.Tooltip("teacher:N", title="model"),
        alt.Tooltip("problem:N", title="problem"),
        alt.Tooltip("level:O", title="level"),
        alt.Tooltip("status:N", title="status"),
        alt.Tooltip("label:N", title="key"),
        alt.Tooltip("final_answer:N", title="model answer"),
        alt.Tooltip("completion_tokens:Q", title="completion tokens", format=","),
        alt.Tooltip("reasoning_tokens:Q", title="reasoning tokens (if reported)", format=","),
        alt.Tooltip("seconds:Q", title="seconds", format=".1f"),
        alt.Tooltip("tokens_per_s:Q", title="tokens/s"),
        alt.Tooltip("n_steps:Q", title="solution steps"),
    ]


def build_views(df: pd.DataFrame, sel: dict) -> dict:
    order = df.attrs["order"]
    dom = df.attrs["domains"]
    y_model = alt.Y("teacher:N", sort=order, title=None)
    summary = df.drop_duplicates("teacher")
    fade_model = alt.condition(sel["model"], alt.value(1.0), alt.value(FADED))
    both = sel["model"] & sel["problem"]
    fade_both = alt.condition(both, alt.value(0.9), alt.value(FADED))

    def summary_panel(field, title, fmt, label_field, zero_domain=None, bar=False, param=None):
        # Rows align with the first panel (shared y); later panels keep the axis, without labels.
        y = y_model if param is not None else alt.Y(
            "teacher:N", sort=order, title=None,
            axis=alt.Axis(labels=False, ticks=False, domain=False))
        base = alt.Chart(summary).encode(
            y=y,
            x=alt.X(f"{field}:Q", title=title,
                    scale=alt.Scale(zero=True, domain=zero_domain) if zero_domain else alt.Scale(zero=True)),
            opacity=fade_model,
            tooltip=[alt.Tooltip("teacher:N", title="model"),
                     alt.Tooltip(f"{field}:Q", title=title, format=fmt)],
        )
        mark = base.mark_bar(color=NEUTRAL, height=14) if bar else base.mark_point(
            color="#333333", filled=True, size=90)
        if param is not None:
            mark = mark.add_params(param)
        # Lollipop stem from zero, so the dot's length reads from the baseline.
        rule = None if bar else base.mark_rule(color="#cccccc").encode(x2=alt.X2("zero:Q"))
        label = (alt.Text(f"{field}:Q", format=fmt) if label_field == field
                 else alt.Text(f"{label_field}:N"))
        text = base.mark_text(align="left", dx=6, fontSize=11, color="#333333").encode(text=label)
        layers = [layer for layer in (rule, mark, text) if layer is not None]
        return alt.layer(*layers).properties(width=170, height=26 * len(order))

    views = {
        "sum_tokens": summary_panel("median_tokens", "median completion tokens", ",.0f",
                                    "median_tokens", param=sel["model"]),
        "sum_seconds": summary_panel("median_seconds", "median seconds (s)", ".0f", "median_seconds"),
        "sum_total": summary_panel("total_tokens_k", "total completion tokens (thousands)", ".1f",
                                   "total_tokens_k", bar=True),
        "sum_usable": summary_panel("usable_pct", "usable records (%)", ".0f", "usable_label",
                                    [0, 100], bar=True),
    }

    def strip(field, title, domain, param=None):
        points = alt.Chart(df).mark_point(size=70, strokeWidth=1.5, filled=False).encode(
            y=y_model,
            yOffset=alt.YOffset("level:O", title=None),  # deterministic: stacked by level
            x=alt.X(f"{field}:Q", title=title, scale=alt.Scale(domain=domain, zero=True, nice=True)),
            color=alt.Color("status:N", scale=STATUS_SCALE, title="record"),
            shape=alt.Shape("status:N", scale=SHAPE_SCALE, title="record"),
            opacity=fade_both,
            tooltip=_tooltip(),
        )
        if param is not None:
            points = points.add_params(param)
        median = alt.Chart(summary).mark_tick(color="#000000", thickness=2, size=22).encode(
            y=y_model,
            x=alt.X(f"{'median_tokens' if field == 'completion_tokens' else 'median_seconds'}:Q",
                    title=title, scale=alt.Scale(domain=domain, zero=True, nice=True)),
            opacity=fade_model,
        )
        return alt.layer(points, median).properties(width=380, height=40 * len(order))

    views["strip_tokens"] = strip("completion_tokens", "completion tokens per call",
                                  dom["tokens"], param=sel["problem"])
    views["strip_seconds"] = strip("seconds", "seconds per call (s)", dom["seconds"])
    views["scatter"] = alt.Chart(df).mark_point(size=70, strokeWidth=1.5, filled=False).encode(
        x=alt.X("completion_tokens:Q", title="completion tokens per call",
                scale=alt.Scale(domain=dom["tokens"], zero=True, nice=True)),
        y=alt.Y("seconds:Q", title="seconds per call (s)",
                scale=alt.Scale(domain=dom["seconds"], zero=True, nice=True)),
        color=alt.Color("status:N", scale=STATUS_SCALE, title="record"),
        shape=alt.Shape("status:N", scale=SHAPE_SCALE, title="record"),
        opacity=fade_both,
        tooltip=_tooltip(),
    ).properties(width=380, height=260, title="Is a model slow because it writes more?")
    return views


def compose(views: dict, df: pd.DataFrame):
    n = int(df["n_calls"].max())
    headline = alt.hconcat(views["sum_tokens"], views["sum_seconds"].properties(),
                           views["sum_total"], views["sum_usable"], spacing=24).resolve_scale(y="shared")
    calls = alt.hconcat(views["strip_tokens"], views["strip_seconds"], spacing=24).resolve_scale(y="shared")
    return alt.vconcat(
        headline, calls, views["scatter"], spacing=28
    ).resolve_legend(color="shared", shape="shared").properties(
        title=alt.Title(
            takeaway(df),
            subtitle=[
                "Top: per-model aggregates (click a model to highlight it everywhere). "
                "Below: one mark per call; black tick = model median; within a row, marks are "
                "stacked by problem level (0 low to 7 high).",
                "Click a call in the token strip to highlight that problem in every view (double-click clears). "
                "'usable' = reached the key, 5 options, did not dispute the key, and most models agree with the key.",
                f"{SOURCE}; n = {len(df)} calls, {df['problem'].nunique()} problems, up to {n} per model. "
                "Reasoning tokens are reported only by some models. Times near 0 s are a timing artefact of parallel calls, not real speed.",
            ],
            anchor="start", fontSize=15, subtitleFontSize=11, subtitleColor="#555555",
        )
    ).configure_view(stroke=None).configure_axis(labelFontSize=11, titleFontSize=11)


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
        chart.save(png, scale_factor=2)  # the default (nothing selected) state
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
