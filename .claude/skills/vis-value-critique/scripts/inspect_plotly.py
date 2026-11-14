#!/usr/bin/env python3
"""Deterministic checks on a Plotly figure.

Input: fig.write_json() output (.json), an HTML file produced by fig.write_html() or
Dash/Streamlit static export containing Plotly.newPlot(...), or a .py script that
builds plotly figures (plotly must be importable; st.plotly_chart is stubbed).

Usage:
    python3 inspect_plotly.py figure.json
    python3 inspect_plotly.py page.html
    python3 inspect_plotly.py app.py

Output: JSON report on stdout with rule IDs from references/rules-catalog.md.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import types

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vischeck.findings import (Report, looks_like_raw_name, has_units,  # noqa: E402
                               looks_non_additive, looks_like_raw_count, looks_temporal)
from vischeck.color import parse_color, palette_report, is_neutral, to_hex  # noqa: E402
from vischeck.palettes import classify_scheme  # noqa: E402

THREED = {"scatter3d", "surface", "mesh3d", "cone", "streamtube", "volume", "isosurface"}
BAR_TYPES = {"bar", "histogram", "funnel", "waterfall"}


# ----------------------------------------------------------------------------
# loading

def figs_from_html(path, report):
    text = open(path, encoding="utf-8", errors="replace").read()
    dec = json.JSONDecoder()
    figs = []
    for m in re.finditer(r"Plotly\.(?:newPlot|react|plot)\(", text):
        i = m.end()
        # skip the div id argument
        j = text.find(",", i)
        if j < 0:
            continue
        k = j + 1
        while k < len(text) and text[k] in " \n\r\t":
            k += 1
        try:
            data, n = dec.raw_decode(text[k:])
        except json.JSONDecodeError:
            continue
        k2 = k + n
        while k2 < len(text) and text[k2] in " \n\r\t,":
            k2 += 1
        layout = {}
        try:
            layout, _ = dec.raw_decode(text[k2:])
        except json.JSONDecodeError:
            pass
        if isinstance(data, list):
            figs.append({"data": data, "layout": layout if isinstance(layout, dict) else {}})
    if not figs:
        report.warn("No Plotly.newPlot call with inline JSON found in the HTML.")
    return figs


class _StRecorder:
    captured: list = []

    def __init__(self, name="st"):
        self._name = name

    def __getattr__(self, item):
        return _StRecorder(f"{self._name}.{item}")

    def __call__(self, *a, **k):
        for v in list(a) + list(k.values()):
            if hasattr(v, "to_plotly_json"):
                _StRecorder.captured.append(v)
        if "columns" in self._name or "tabs" in self._name:
            n = a[0] if a and isinstance(a[0], int) else \
                (len(a[0]) if a and isinstance(a[0], (list, tuple)) else 2)
            return [_StRecorder() for _ in range(n)]
        return _StRecorder()

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def __iter__(self):
        return iter([_StRecorder(), _StRecorder()])

    def __getitem__(self, k):
        return _StRecorder()

    def __bool__(self):
        return False


def figs_from_python(path, report):
    try:
        import plotly.graph_objects as go
        import plotly.io as pio
    except Exception:
        report.warn("plotly not importable; save the figure with fig.write_json().")
        return []
    pio.renderers.default = "json"
    _StRecorder.captured = []
    rec = _StRecorder()
    st = types.ModuleType("streamlit")
    st.__getattr__ = lambda n: getattr(rec, n)  # type: ignore[attr-defined]
    sys.modules["streamlit"] = st
    go.Figure.show = lambda self, *a, **k: None
    ns = {"__name__": "__main__", "__file__": os.path.abspath(path)}
    src = open(path, encoding="utf-8").read()
    cwd = os.getcwd()
    os.chdir(os.path.dirname(os.path.abspath(path)) or ".")
    try:
        exec(compile(src, path, "exec"), ns)
    except SystemExit:
        pass
    except Exception as e:
        report.warn(f"Script raised {type(e).__name__}: {e}")
    finally:
        os.chdir(cwd)
    figs = list(_StRecorder.captured)
    for v in ns.values():
        if isinstance(v, go.Figure) and v not in figs:
            figs.append(v)
    out = []
    for f in figs:
        try:
            out.append(json.loads(f.to_json()))
        except Exception as e:
            report.warn(f"to_json failed: {e}")
    if not out:
        report.warn("No plotly Figure found in the script namespace.")
    return out, src


def load(path, report):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".json":
        with open(path, encoding="utf-8") as fh:
            d = json.load(fh)
        if isinstance(d, dict) and "data" in d:
            return [d], ""
        if isinstance(d, list):
            return [{"data": d, "layout": {}}], ""
        report.warn("JSON does not look like a plotly figure")
        return [], ""
    if ext in (".html", ".htm"):
        return figs_from_html(path, report), ""
    if ext == ".py":
        r = figs_from_python(path, report)
        return r if isinstance(r, tuple) else (r, "")
    report.warn("unknown extension")
    return [], ""


# ----------------------------------------------------------------------------
# helpers

def axis_of(layout, name):
    return layout.get(name) or {}


def axis_title(ax):
    t = ax.get("title")
    if isinstance(t, dict):
        return t.get("text")
    return t


def is_string_list(v):
    return isinstance(v, list) and v and all(isinstance(x, str) for x in v[:20])


def is_time_list(v):
    if not isinstance(v, list) or not v:
        return False
    return all(isinstance(x, str) and re.match(r"^\d{4}(-\d{2})?(-\d{2})?", x) for x in v[:10])


def nums(v):
    out = []
    if not isinstance(v, list):
        return out
    for x in v:
        if isinstance(x, (int, float)) and x == x:
            out.append(float(x))
    return out


# ----------------------------------------------------------------------------
# checks

def check_fig(fig, report, src, idx):
    where = f"fig{idx}"
    data = fig.get("data", []) or []
    layout = fig.get("layout", {}) or {}
    types_ = [t.get("type", "scatter") for t in data]
    report.summary.setdefault("figures", []).append(
        {"where": where, "n_traces": len(data), "types": types_,
         "title": axis_title(layout) if isinstance(layout.get("title"), dict) else layout.get("title")})

    # title
    t = layout.get("title")
    ttext = t.get("text") if isinstance(t, dict) else t
    if not ttext:
        report.add("TXT-01", "major", "No chart title (TEXT-1).", "", where=where, kind="SEMI")
    elif looks_like_raw_name(ttext):
        report.add("TXT-01", "minor", "Title is a bare name, not a message.",
                   f"'{ttext}'", where=where, kind="SEMI")

    # 3D
    if any(tp in THREED for tp in types_) or "scene" in layout:
        report.add("EFF-03", "crit", "3D trace for abstract data.",
                   f"types={sorted(set(types_) & THREED)}", where=where,
                   exception="inherently 3D spatial data")
    # dual axes
    for k, v in layout.items():
        if re.fullmatch(r"yaxis\d+", k) and isinstance(v, dict) and v.get("overlaying"):
            report.add("EXP-11", "crit", "Secondary y axis overlaying the first (dual "
                       "axes): arbitrary alignment, meaningless crossings.",
                       f"{k}.overlaying={v.get('overlaying')}", where=where)
        if re.fullmatch(r"xaxis\d+", k) and isinstance(v, dict) and v.get("overlaying"):
            report.add("EXP-11", "major", "Secondary x axis overlaying the first.", k,
                       where=where)
    # subplots: several y axes side by side, each with its own range
    used = {tr.get("yaxis", "y") for tr in data if tr.get("type", "scatter") not in ("pie", "table")}
    keys = {"yaxis" + a[1:] for a in used if isinstance(a, str) and a.startswith("y")}
    panels = [k for k in sorted(keys) if not (layout.get(k) or {}).get("overlaying")]
    if len(panels) > 1 and not any((layout.get(k) or {}).get("matches") for k in panels):
        ranges = {json.dumps((layout.get(k) or {}).get("range")) for k in panels}
        if len(ranges) > 1 or ranges == {"null"}:
            report.add("SCL-08", "minor", f"{len(panels)} subplots with independent y "
                       "scales: equal heights do not mean equal values. Use shared_yaxes "
                       "/ matches, or say that each panel has its own scale.",
                       f"axes={panels}; no `matches`", where=where, kind="SEMI",
                       exception="panels show different measures, each titled with its unit")
    # distribution traces: whiskers, bins, bandwidth
    for i, tr in enumerate(data):
        tp = tr.get("type")
        if tp == "box":
            report.add("DAT-10", "minor", "Box trace: say in the chart what the whiskers "
                       "mean (Plotly default: 1.5 × IQR) (RAIN-6).", f"trace {i}",
                       where=where, kind="SEMI", exception="the caption defines the whiskers")
        if tp == "violin" and tr.get("bandwidth") is None:
            report.add("EXP-15", "minor", "Violin with the default bandwidth: choose it "
                       "and state it (RAIN-4).", f"trace {i}", where=where, kind="SEMI")
        if tp == "histogram" and not any(k in tr for k in ("nbinsx", "nbinsy", "xbins", "ybins")):
            report.add("EXP-15", "minor", "Histogram with the default bin count: choose "
                       "the bin width and try another (RAIN-4).", f"trace {i}", where=where,
                       kind="SEMI")
    # axes titles / types / ranges
    xa, ya = axis_of(layout, "xaxis"), axis_of(layout, "yaxis")
    bars = [tr for tr in data if tr.get("type") in BAR_TYPES]
    pies = [tr for tr in data if tr.get("type") in ("pie", "sunburst", "funnelarea")]
    scatters = [tr for tr in data if tr.get("type", "scatter") in ("scatter", "scattergl")]
    heat = [tr for tr in data if tr.get("type") in ("heatmap", "heatmapgl", "contour",
                                                     "choropleth", "choroplethmapbox",
                                                     "densitymapbox", "histogram2d")]
    for nm, ax in (("x", xa), ("y", ya)):
        if pies and not bars and not scatters:
            break
        title = axis_title(ax)
        if ax.get("visible") is False:
            continue
        if not title:
            report.add("SCL-06", "major", f"{nm} axis has no title.", "", where=where,
                       exception="categorical axis whose labels are self-explanatory")
        elif looks_like_raw_name(title):
            report.add("SCL-06", "major", f"{nm} axis title is a raw variable name.",
                       f"'{title}'", where=where)
        elif not has_units(title) and ax.get("type") not in ("category", "date"):
            report.add("SCL-06", "minor", f"No units detected in the {nm} axis title.",
                       f"'{title}'", where=where, kind="SEMI")
        if ax.get("tickangle") not in (None, 0, "auto") and abs(float(ax.get("tickangle"))) >= 30 \
                and bars and nm == "x":
            report.add("SCL-12", "minor", "Rotated category labels: use horizontal bars.",
                       f"tickangle={ax.get('tickangle')}", where=where)
        fs = (ax.get("tickfont") or {}).get("size")
        if isinstance(fs, (int, float)) and fs < 10:
            report.add("ACC-05", "major", f"{nm} tick font {fs}px below legibility.", "",
                       where=where)
    # bars
    for i, tr in enumerate(bars):
        horiz = tr.get("orientation") == "h"
        qax = xa if horiz else ya
        rng = qax.get("range")
        vals = nums(tr.get("x") if horiz else tr.get("y"))
        if qax.get("type") == "log":
            report.add("EXP-20", "crit", "Bars on a log axis.", f"trace {i}", where=where)
        elif isinstance(rng, list) and len(rng) == 2 and vals and min(vals) > 0:
            try:
                lo = float(rng[0])
            except (TypeError, ValueError):
                lo = 0
            if lo > 0:
                report.add("EXP-08", "crit", "Bar axis range does not start at zero "
                           "(TRUNC-1).", f"trace {i} range={rng}", where=where,
                           exception="deviation bars from a drawn, labeled reference")
        if tr.get("base") not in (None, 0) and tr.get("type") == "bar":
            report.add("EXP-08", "major", "Bars with a non-zero base.",
                       f"trace {i} base={tr.get('base')}", where=where, kind="SEMI",
                       exception="waterfall/floating-bar idiom used deliberately")
        cat = tr.get("y") if horiz else tr.get("x")
        if is_time_list(cat) and len(cat) > 6 and tr.get("type") == "bar":
            report.add("EXP-04", "major", "Bars over dates: a line chart is typically "
                       "better for trend.", f"trace {i}, {len(cat)} dates", where=where,
                       kind="SEMI")
        if vals and len(vals) > 100:
            report.add("EFF-19", "major", f"{len(vals)} bars in one trace.", "", where=where)
        mc = (tr.get("marker") or {}).get("color")
        if isinstance(mc, list) and len(set(map(str, mc))) > 2 and \
                len(set(map(str, mc))) >= len(mc) - 1 and len(mc) > 3 and \
                all(isinstance(c, str) for c in mc):
            report.add("COL-03", "major", "A different hue per bar although position "
                       "identifies the category.", f"trace {i}: {len(set(mc))} colors",
                       where=where)
        if vals and len(bars) == 1 and is_string_list(cat) and len(vals) > 3 and \
                vals != sorted(vals) and vals != sorted(vals, reverse=True) and \
                not any(looks_temporal(c) for c in cat[:3]):
            report.add("CMP-01", "minor", "Bars not sorted by value.", f"trace {i}",
                       where=where, kind="SEMI",
                       exception="natural category order or name lookup")
        if tr.get("error_y") or tr.get("error_x"):
            report.add("DAT-03", "major", "Error bars present: their meaning (SD/SE/CI) "
                       "must be stated (MEANBAR-4).", f"trace {i}", where=where, kind="SEMI")
    if len(bars) > 1 and layout.get("barmode") == "stack":
        if len(bars) > 6:
            report.add("IDM-STACK", "major", f"{len(bars)} stacked series.", "", where=where)
        for i, tr in enumerate(bars):
            vals = nums(tr.get("x") if tr.get("orientation") == "h" else tr.get("y"))
            if vals and min(vals) < 0:
                report.add("EXP-06", "crit", "Stacked bars with negative values.",
                           f"trace {i} min={min(vals)}", where=where)
            nm = str(tr.get("name", ""))
            if looks_non_additive(nm):
                report.add("EXP-06", "major", "Stacking a quantity that looks "
                           "non-additive.", f"trace '{nm}'", where=where, kind="SEMI")
    if src and bars and re.search(r"\.mean\(\)|estimator|histfunc\s*=\s*['\"]avg", src):
        report.add("EXP-16", "major", "Bars may encode means (MEANBAR-1): show the "
                   "distribution.", "source mentions mean/avg near bars", where=where,
                   kind="SEMI")
    # pies
    for i, tr in enumerate(pies):
        labels = tr.get("labels") or []
        n = len(labels) if isinstance(labels, list) else 0
        if n > 5:
            report.add("IDM-PIE", "crit", f"Pie with {n} slices.", f"trace {i}", where=where)
        if tr.get("sort") is False:
            report.add("CMP-01", "minor", "Pie slices not sorted.", f"trace {i}", where=where)
        if tr.get("pull"):
            report.add("IDM-PIE", "major", "Exploded pie.", f"trace {i} pull={tr.get('pull')}",
                       where=where)
        vals = nums(tr.get("values"))
        if vals and min(vals) < 0:
            report.add("EXP-05", "crit", "Pie with negative values.", f"trace {i}", where=where)
        if tr.get("rotation") not in (None, 0):
            report.add("IDM-PIE", "minor", "Pie not starting at 12 o'clock.", f"trace {i}",
                       where=where)
    # scatters
    nlines = 0
    for i, tr in enumerate(scatters):
        mode = tr.get("mode", "lines" if tr.get("type") != "scattergl" else "markers")
        xs = tr.get("x")
        if "lines" in str(mode):
            nlines += 1
            if is_string_list(xs) and not is_time_list(xs) and \
                    not all(re.fullmatch(r"\d{4}|Q[1-4].*|[A-Z][a-z]{2}", x) for x in xs[:8]):
                report.add("EXP-03", "crit", "Line over nominal categories (TRUNC-10).",
                           f"trace {i} x={xs[:5]}", where=where,
                           exception="ordinal categories with a natural order")
        if "markers" in str(mode):
            n = len(xs) if isinstance(xs, list) else 0
            op = tr.get("opacity", (tr.get("marker") or {}).get("opacity"))
            if n > 2000 and (op is None or float(op) >= 0.9):
                report.add("EFF-16", "major", f"{n} opaque markers: overplotting.",
                           f"trace {i}", where=where, kind="SEMI")
            m = tr.get("marker") or {}
            if isinstance(m.get("size"), list) and m.get("sizemode", "diameter") != "area":
                report.add("EFF-04", "major", "Bubble sizes scale the diameter, not the "
                           "area: large values are exaggerated.",
                           f"trace {i} sizemode={m.get('sizemode', 'diameter')}", where=where)
            cs = m.get("colorscale")
            if cs and isinstance(cs, str):
                cls = classify_scheme(cs)
                if cls == "rainbow":
                    report.add("COL-02", "crit", "Rainbow colorscale.", f"trace {i} {cs}",
                               where=where)
                if cls == "redgreen":
                    report.add("COL-05", "crit", "Red–green colorscale.", f"trace {i} {cs}",
                               where=where)
        yvals = nums(tr.get("y"))
        yr = ya.get("range")
        if "lines" in str(mode) and yvals and isinstance(yr, list) and len(yr) == 2:
            try:
                lo, hi = float(yr[0]), float(yr[1])
                span = hi - lo
                if span > 0 and lo <= 0 < min(yvals) and (max(yvals) - min(yvals)) / span < 0.15:
                    report.add("SCL-04", "major", "Line forced to zero while data vary in a "
                               "narrow band (TRUNC-5).", f"trace {i}", where=where, kind="SEMI")
            except (TypeError, ValueError):
                pass
    if nlines > 12:
        report.add("EFF-16", "major", f"{nlines} line traces (spaghetti, more than about a "
                   "dozen): highlight a few against grey or facet.", "", where=where)
    # heatmaps / maps
    for i, tr in enumerate(heat):
        cs = tr.get("colorscale")
        if isinstance(cs, str):
            cls = classify_scheme(cs)
            if cls == "rainbow":
                report.add("COL-02", "crit", "Rainbow colorscale.", f"trace {i} {cs}", where=where)
            if cls == "redgreen":
                report.add("COL-05", "crit", "Red–green colorscale.", f"trace {i} {cs}", where=where)
            if cls == "qualitative":
                report.add("EXP-02", "crit", "Qualitative palette on continuous values.",
                           f"trace {i} {cs}", where=where, kind="SEMI")
        if tr.get("showscale") is False:
            report.add("TXT-03", "major", "Color scale hidden: values unexplained.",
                       f"trace {i}", where=where)
        if tr.get("type", "").startswith("choropleth"):
            nm = str(tr.get("name") or (tr.get("colorbar") or {}).get("title") or "")
            if looks_like_raw_count(nm):
                report.add("EXP-12", "major", "Choropleth of a raw count/total.",
                           f"trace {i} '{nm}'", where=where, kind="SEMI")
            else:
                report.add("EXP-12", "minor", "Choropleth: verify the variable is "
                           "normalized (rate, per capita).", f"trace {i}", where=where,
                           kind="SEMI")
    # colors across traces
    cols = []
    for tr in data:
        m = tr.get("marker") or {}
        ln = tr.get("line") or {}
        for c in (m.get("color"), ln.get("color"), tr.get("fillcolor")):
            if isinstance(c, str):
                p = parse_color(c)
                if p and not is_neutral(p):
                    cols.append(p)
    tmpl_cols = ((layout.get("template") or {}).get("layout") or {}).get("colorway")
    cw = layout.get("colorway") or tmpl_cols
    if not cols and len(data) > 1:
        from vischeck.palettes import scheme_colors
        base = cw if isinstance(cw, list) else scheme_colors("plotly")
        cols = [parse_color(c) for c in base[:len(data)]]
        cols = [c for c in cols if c]
    seen, uniq = set(), []
    for c in cols:
        h = to_hex(c)
        if h not in seen:
            seen.add(h)
            uniq.append(c)
    if len(uniq) >= 2:
        pr = palette_report(uniq[:16])
        report.summary.setdefault("palettes", []).append({"where": where, **pr})
        if pr["has_red_and_green"]:
            report.add("COL-05", "major", "Red and green both used for data marks.",
                       f"{pr['hex'][:10]}", where=where, kind="SEMI")
        for p in pr["confusable_deuteranopia"][:4]:
            report.add("COL-05", "major", "Two trace colors merge under deuteranopia.",
                       f"{p['a']} vs {p['b']} ΔE sim={p['dE_simulated']}", where=where)
    if len(data) > 8 and (bars or scatters) and len(pies) == 0:
        report.add("COL-04", "major", f"{len(data)} traces / colors in one figure.",
                   "", where=where, kind="SEMI")
    # legend count
    if len(data) > 7 and layout.get("showlegend", True) is not False:
        report.add("EFF-11", "major", f"Legend with ~{len(data)} entries.", "", where=where)
    # fonts / background
    fsz = (layout.get("font") or {}).get("size")
    if isinstance(fsz, (int, float)) and fsz < 10:
        report.add("ACC-05", "major", f"Base font size {fsz}px.", "", where=where)
    bg = layout.get("plot_bgcolor") or ((layout.get("template") or {}).get("layout") or {}).get("plot_bgcolor")
    bgc = parse_color(bg) if isinstance(bg, str) else None
    if bgc and not is_neutral(bgc):
        report.add("CLT-01", "minor", "Colored plot background.", f"{bg}", where=where)
    # annotations
    ann = layout.get("annotations") or []
    report.summary["n_annotations"] = len(ann)
    for a in ann:
        t = str(a.get("text", "")).strip()
        if re.fullmatch(r"(max|min|peak|maximum|minimum|high|low)\.?", t, flags=re.I):
            report.add("TXT-06", "minor", "Annotation restates the obvious (TEXT-4).",
                       f"'{t}'", where=where, kind="SEMI")
    if layout.get("updatemenus") or layout.get("sliders"):
        report.summary["has_controls"] = True
    if any(tr.get("hovertemplate") or tr.get("hoverinfo") not in (None, "skip", "none")
           for tr in data):
        report.summary["has_tooltip"] = True


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path")
    args = ap.parse_args()
    report = Report(args.path, "plotly")
    try:
        figs, src = load(args.path, report)
    except Exception as e:
        report.warn(f"load failed: {e}")
        figs, src = [], ""
    for i, f in enumerate(figs):
        try:
            check_fig(f, report, src, i)
        except Exception as e:
            report.warn(f"fig{i}: check failed: {type(e).__name__}: {e}")
    report.dump()


if __name__ == "__main__":
    main()
