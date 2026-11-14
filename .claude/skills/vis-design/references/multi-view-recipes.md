# Multi-view recipes (Altair, Streamlit)

Read this in stage 3 when the answer needs more than one view, and in stage 4 when the
decision has a `solution.composition` block. Theory: `encoding-essentials.md` (Multiple
views). Template: `templates/dashboard_altair.py.tmpl`.

## 1. Decide the composition (stage 3)

| The reader must… | Composition `type` | `relation` | Needs |
|---|---|---|---|
| see one thing, changed on demand | `single` (+ widget or tooltip) | n/a | default state answers the task (INT-02) |
| compare series or a value against a reference in one frame | `superimpose` | n/a | ≤ 2 area layers, ≤ ~12 lines, distinguishable layers (CMP-10) |
| compare the same chart across a category | `small-multiples` | small-multiples | shared scales, panels ordered by a statistic (SCL-08, CMP-07) |
| find the same items in two encodings (map + ranking, scatter + histogram) | `juxtapose` | multiform | linked highlight both ways (CMP-09, INT-10) |
| read a long axis or a large set in detail | `overview-detail` | overview-detail | brush on the overview drives the detail (INT-09) |
| keep the surroundings while enlarging a part | `focus-context` | overview-detail | accept distortion, or use a highlighted cue |
| see alternative encodings of one question, one at a time | `tabs` | redundant / multiform | never when the tabs must be compared (EFF-20) |

Record the choice in `solution.composition`:

```yaml
composition:
  type: juxtapose
  relation: multiform
  data_sharing: all            # all | subset | none
  encoding_sharing: different  # same | different
  views:
    - {id: scatter, idiom: scatterplot, role: focus}
    - {id: bars, idiom: bar_chart, role: context}
  links:
    - {from: scatter, to: bars, type: filter}
    - {from: bars, to: scatter, type: highlight}
```

Views that share neither data nor encoding nor a link do not belong in one composition
(CMP-11): design them as separate decisions. Two views cost about twice the area: check
each is still legible at half width before choosing `juxtapose` (CMP-13). If the task is
the change between two states, add a `difference` view rather than two charts to
subtract by eye (CMP-12).

## 2. Altair recipes

All recipes assume one tidy frame `df` passed to every view, so the views share the data
and selections resolve across them. Give every selection a `name` and explicit `fields`
or `encodings` (Streamlit and the inspector both rely on them).

**Linked highlight (multiform).** One point selection, one highlight color, read by both
views; unselected marks turn neutral, they do not disappear.

```python
pick = alt.selection_point(name="pick", fields=[KEY], empty=True)
hl = alt.condition(pick, alt.value(ACCENT), alt.value(NEUTRAL))
a = alt.Chart(df).mark_point().encode(x=X, y=Y, color=hl).add_params(pick)
b = alt.Chart(df).mark_bar().encode(y=alt.Y(KEY, sort="-x"), x=TOTAL, color=hl)
chart = alt.hconcat(a, b)          # add_params once; the other view only reads it
```

**Cross-filter.** A brush in one view filters the other. Keep the full data as a grey
layer underneath so the context survives (INT-11).

```python
brush = alt.selection_interval(name="brush", encodings=["x"])
a = alt.Chart(df).mark_point().encode(x=X, y=Y).add_params(brush)
base = alt.Chart(df).mark_bar(color=NEUTRAL).encode(y=KEY, x="count()")
sel = base.mark_bar(color=ACCENT).transform_filter(brush)
chart = alt.hconcat(a, base + sel)
```

**Overview + detail.** The overview is small and aggregated; its brush sets the detail's
x domain. The overview shows where the detail is.

```python
brush = alt.selection_interval(name="window", encodings=["x"])
detail = alt.Chart(df).mark_line().encode(
    x=alt.X(T, scale=alt.Scale(domain=brush), title=None), y=alt.Y(V, title=V_TITLE))
overview = alt.Chart(df).mark_area(color=NEUTRAL).encode(
    x=alt.X(T, title=T_TITLE), y=alt.Y(V, title=None, axis=None)
).properties(height=60).add_params(brush)
chart = alt.vconcat(detail, overview)
```

**Linked navigation.** Zoom and pan shared by the views that show the same axis.

```python
zoom = alt.selection_interval(name="zoom", bind="scales", encodings=["x"])
chart = alt.vconcat(a.add_params(zoom), b.add_params(zoom)).resolve_scale(x="shared")
```

**Highlight layer on small multiples.** Every panel shows all series in grey and its own
in the accent color: comparison without a dozen hues.

```python
bg = alt.Chart(df).mark_line(color=NEUTRAL, opacity=0.4).encode(x=T, y=V, detail=SERIES)
fg = alt.Chart(df).mark_line(color=ACCENT).encode(x=T, y=V)
chart = alt.layer(bg, fg).facet(alt.Facet(SERIES, sort=ORDER_BY_MEDIAN), columns=4)
# bg must ignore the facet filter: build it from a frame crossed with the facet key
```

**Explicit difference.** Derive `delta = b - a` in `derive()`; draw it on a diverging
scale around zero, beside the two originals only if their level matters.

**Shared scales.** Concatenated views do NOT share position scales by default. For two
panels of the same measure: `alt.hconcat(a, b).resolve_scale(y="shared")`, or pass the
same `alt.Scale(domain=[lo, hi])` to both. Panels of different measures keep their own
scale and say the unit in each axis title. A layer with a background `mark_rect` band
needs the same explicit x domain on every layer.

**Color.** One mapping per field for the whole composition (same `scale=` object in
every view), one highlight color, legends merged (`resolve_legend(color="shared")`) or
replaced by direct labels.

## 3. Streamlit

- One Altair chart with selections inside it is linked in the browser, with no rerun:
  prefer it. `st.altair_chart(chart, width="content")` (older Streamlit:
  `use_container_width=True`).
- Linking an Altair chart to another Streamlit element (a table, a second chart, a
  metric): `event = st.altair_chart(chart, on_select="rerun", selection_mode="pick",
  key="main")`; read `event.selection["pick"]` (a list of dicts with the selection
  `fields`), filter the frame, render the other element. Selections need explicit
  `fields` or `encodings`.
- Widgets (`st.radio`, `st.select_slider`, `st.multiselect`): defaults are the state that
  answers the main question; keep their value in `st.session_state` via `key=`; put the
  count of rows behind each option in its label or draw a small histogram above a
  slider (scent, INT-12).
- A widget that filters must not silently rescale the charts (DAT-14): compute scale
  domains from the full data in `derive()` and pass them explicitly, or say in the
  subtitle that the scale follows the selection.
- `st.tabs` hides views: use it for alternative encodings, `st.columns` for views that
  must be compared.

## 4. Validation of a composition (stage 3)

1. Name the relation of every pair of views (redundant / multiform / overview-detail /
   small multiples); a pair with none is removed or redesigned.
2. Trace each stage-2 task: start view → selection → answer view; count interactions.
3. Run the sibling inspector on the saved `.vl.json`: no INT-09 (dead selection), no
   CMP-09 (unlinked multiform), no SCL-08 on a shared measure, no INT-10.
4. Open the rendered HTML and perform each selection once; the default state with
   nothing selected must already answer the main question.
