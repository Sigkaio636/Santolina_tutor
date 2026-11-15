"""Streamlit host for teacher_cost_quality (decision p-distribution-compare-groups--teacher-models-cost-vs-20261114).

    uv run --with streamlit --with altair streamlit run reports/dashboard/app.py

Widgets map one-to-one to the interaction plan of the design document; their defaults
(everything selected) are the state that answers the main question. Scale domains come from
the full data (derive), so filtering never silently rescales the charts.
"""

import os
import sys

import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import teacher_cost_quality as chart_module  # noqa: E402

st.set_page_config(page_title="Teacher models: cost vs quality", layout="wide")
st.title("Teacher models: cost vs quality")


@st.cache_data
def _load(path: str):
    df = chart_module.load(path)
    return df, chart_module.derive(df)


raw, full = _load(chart_module.DATA_PATH)


def _label(col, value):
    return f"{value} ({int((full[col] == value).sum())} calls)"


# ---- widgets (one per interaction intent: filter) --------------------------
c1, c2, c3 = st.columns(3)
models = c1.multiselect("Models", full.attrs["order"], default=full.attrs["order"], key="models",
                        format_func=lambda v: _label("teacher", v))
langs = sorted(full["language"].unique())
languages = c2.multiselect("Language", langs, default=langs, key="languages",
                           format_func=lambda v: _label("language", v))
lo, hi = int(full["level"].min()), int(full["level"].max())
levels = c3.slider("Problem level", lo, hi, (lo, hi), key="levels")

mask = (raw["teacher"].isin(models) & raw["language"].isin(languages)
        & raw["level"].between(*levels))
if not mask.any():
    st.warning("No calls match these filters.")
    st.stop()

# Re-derive on the filtered rows (medians and usable rate follow the filter), but keep
# the full-data domains so the axes do not jump.
df = chart_module.derive(raw[mask])
df.attrs["domains"] = full.attrs["domains"]
df.attrs["order"] = [m for m in full.attrs["order"] if m in set(df["teacher"])]

# ---- chart ------------------------------------------------------------------
st.altair_chart(chart_module.build_chart(df), use_container_width=False)

# ---- details on demand --------------------------------------------------------
st.subheader("Calls")
cols = ["teacher", "id", "language", "level", "label", "final_answer", "status", "n_hints",
        "n_steps", "completion_tokens", "reasoning_tokens", "seconds", "tokens_per_s", "error"]
st.dataframe(df[cols].sort_values(["teacher", "level"]), hide_index=True,
             use_container_width=True)
st.caption(f"{chart_module.SOURCE}. Metrics table: data/processed/explanations/metrics.csv "
           f"({len(df)} of {len(full)} calls shown). Rebuild it with "
           "`python -m santolina_tutor.explanation_metrics` after a new generation run.")
