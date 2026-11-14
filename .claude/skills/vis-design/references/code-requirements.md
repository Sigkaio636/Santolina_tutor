# Code requirements

What every generated chart script must contain, and the per-library rules. The templates
in `templates/` fix this structure; the skill fills `derive()` and `build_chart()` from
the decision record. `scripts/run_check.py` executes the result.

## Structure (all libraries)

1. **Docstring**: decision record id, path of the design document, library, date, the
   domain question in the user's language.
2. **`CONFIG`**: `DATA_PATH` resolved relative to the script file (`os.path.join(_HERE,
   "data.csv")`) or overridden by `--data`; column names used; `OUT_DIR`; `LANG`; `SLUG`. No
   absolute paths from the author's machine. The checker and the sibling inspectors run the
   script with cwd = its folder, so a path relative to the project root breaks them.
3. **`load(path)`**: explicit `sep`, `decimal`, `encoding`; dates parsed with the format
   `profile_data.py` detected (`format=` / `dayfirst`); code columns read as `str`
   (`dtype`); sentinel values (−9999, "N/A") turned into NaN and counted; `assert` that
   the needed columns exist and the frame is not empty; print rows loaded.
4. **`derive(df)`**: every derived attribute from design-document section 2, same names,
   same formulas; filters and normalisation applied here; returns the final small table.
5. **`takeaway(df)`**: returns the title text computed from the data (f-string with the
   extremum / share / change); the document quotes the rendered title.
6. **`PALETTE`**: constants for the color plan (Okabe-Ito list, `NEUTRAL`, `ACCENT`,
   sequential/diverging scheme names) from `scripts/visdesign/colorcheck.py`.
7. **`build_chart(df)`** → chart/figure: encodings as in section 3; axis titles with
   units; zero baseline for length marks; explicit sort; ≤ 7 hues; facets with shared
   scales; no dual axes; source/n footer; interaction from the plan.
8. **`save(chart, out_dir, slug)`**: per-library exports below.
9. **`main()`** with `argparse --data --out-dir --no-show`; module-level `chart` / `fig`
   left in the namespace after `main()` so the sibling inspectors can import them.

## Per library

**Altair** (`mark_*`, `encode`): `alt.X(..., title="… (unit)")`; `sort="-x"` or an
explicit list; `scale=alt.Scale(zero=True)` for bars; `alt.Color(scale=alt.Scale(range=
OKABE_ITO))` or `scheme="viridis"`; `alt.condition(...)` for neutral + accent; `tooltip`
list with units; selections via `alt.selection_point(bind="legend")`, `alt.param` with
`binding_select`, `alt.selection_interval()` for brushing; `facet` with
`resolve_scale(y="shared")`; `properties(title=alt.Title(text, subtitle=[...]))`.
Pre-aggregate in pandas; `alt.data_transformers.disable_max_rows()` only when stated.
Save: `chart.save(f"{slug}.html")`, `chart.save(f"{slug}.vl.json")`, and
`chart.save(f"{slug}.png", scale_factor=2)` inside `try/except` for a missing
`vl_convert`. Streamlit host: `st.altair_chart(chart, width="content")` (Streamlit
< 1.50: `use_container_width=True`).

**Altair, several views** (decision with `solution.composition`): use
`templates/dashboard_altair.py.tmpl`: `selections()` returns one named selection per
link, with explicit `fields`/`encodings`; `build_views()` returns one chart per view id,
each selection added to one view and read by the views it links; `compose()` lays them
out and resolves scales (`resolve_scale(y="shared")` for the same measure; concatenated
views are independent by default) and legends. One highlight color (`ACCENT` on
`NEUTRAL`) in every view; fixed domains computed in `derive()`. No random jitter: a
strip (`mark_tick`), or a seeded offset computed in `derive()`. Recipes:
`multi-view-recipes.md`.

**matplotlib**: `matplotlib.use("Agg")`; `fig, ax = plt.subplots(figsize=…)`; `barh` on a
sorted frame (pass the category strings, or call the template's `row_axis(ax, labels)`
for hlines/scatter row charts, so the axis is categorical and needs no title); `ax.bar_label` for direct labels; `ax.set_xlabel("… (unit)")`; spines top
and right off; light grey grid only if values must be read; `sharey=True` in small
multiples; `fig.text` for the source footer; `fig.savefig(png, dpi=200,
bbox_inches="tight")`; no interaction (an interaction plan other than `none` degrades to
small multiples and is recorded as a rejected alternative).

**Plotly**: `px.*` with `color_discrete_sequence=OKABE_ITO`, `category_orders`,
`template="simple_white"`; `hovertemplate` with units; `update_layout(title=…,
yaxis_title="… (unit)")`; `layout.yaxis.range` from zero for bars; `updatemenus` /
`sliders` only when the plan says filter; `fig.write_html`, `fig.write_json`, and
`fig.write_image(png)` inside `try/except` for a missing `kaleido`. Streamlit host:
`st.plotly_chart(fig, width="stretch")` (older: `use_container_width=True`).

**Streamlit app** (`app.py`): imports `load`, `derive`, `build_chart` from the chart
module; `st.set_page_config(layout="wide")`; one widget per interaction intent
(`st.selectbox` / `st.multiselect` for filter, `st.radio` for reconfigure); default widget
values = the state that answers the main question; `@st.cache_data` on `load`; no data
the chart does not use. Views linked inside one Altair chart need no Streamlit code;
linking a chart to another element uses `st.altair_chart(..., on_select="rerun",
key=...)` and the returned `selection`; views to compare go in `st.columns`, never in
`st.tabs`; option labels carry the row counts behind them.

## Rule IDs the generated code must respect (checked by the sibling inspectors)

EXP-01/02/03 (channel–type match), EXP-05/06 (parts and stacking), EXP-08 (bars from
zero), EXP-09 (no clipping / dropped channels), EXP-11 (no dual axes), COL-02/04/05
(palette type, ≤ 7 hues, CVD-safe), SCL-06 (axis titles with units), TXT-01 (title),
TXT-04 (direct labels), TXT-08 (source/n), CMP-01 (sorted), SCL-08 (shared scales in
facets and in concatenated panels of one measure), EXP-21 (no random jitter), EXP-15
(explicit bins / bandwidth), DAT-10 (whiskers defined), INT-09 (no dead selection),
CMP-09 (multiform views linked), INT-10 (one highlight color), CMP-10 (≤ 2 area
layers).
