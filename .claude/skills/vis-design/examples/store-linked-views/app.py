"""Streamlit host for store_sales_linked (decision correlation-two-quantities--linked-scatter-and-bars).

The two views are linked inside one Altair chart, so no Streamlit callback is needed.
"""
import os
import sys

import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import store_sales_linked as chart_module  # noqa: E402

st.set_page_config(page_title="Which stores turn visits into sales?", layout="wide")


@st.cache_data
def _load(path: str):
    return chart_module.derive(chart_module.load(path))


df = _load(chart_module.DATA_PATH)
st.altair_chart(chart_module.build_chart(df), width="content")
st.caption("Drag on the left chart to restrict the bars; click a bar to highlight that store's weeks. "
           "Source: synthetic example data.")
