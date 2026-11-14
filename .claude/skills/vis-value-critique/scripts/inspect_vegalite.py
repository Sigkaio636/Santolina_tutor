#!/usr/bin/env python3
"""Deterministic checks on an Altair / Vega-Lite visualization.

Input: a Vega-Lite .json (chart.save('c.json') or chart.to_json()), an Altair-saved
.html, or a .py script that builds Altair charts (needs altair installed; Streamlit
calls are stubbed so `st.altair_chart(c)` charts are captured too).

Usage:
    python3 inspect_vegalite.py chart.json [--render out.png] [--data data.csv]

Output: JSON report on stdout (findings carry rule IDs from references/rules-catalog.md
and references/papers.md). Never raises on strange specs: emits warnings instead.
"""
from __future__ import annotations

import argparse
import copy
import csv
import itertools
import json
import os
import re
import sys
import types

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vischeck.findings import (Report, looks_like_raw_name, has_units,  # noqa: E402
                               looks_non_additive, looks_like_raw_count,
                               looks_temporal)
from vischeck.color import parse_color, palette_report, to_hex  # noqa: E402
from vischeck.palettes import classify_scheme, scheme_colors  # noqa: E402

LENGTH_MARKS = {"bar", "area", "rect"}  # rect only when used as bar-like
POINT_MARKS = {"point", "circle", "square", "tick"}
LINE_MARKS = {"line", "trail", "area"}
CONCAT_KEYS = ("hconcat", "vconcat", "concat")
MAX_LINES = 12  # superimposed lines in one panel (Munzner 2014); hue alone separates ~7


# ----------------------------------------------------------------------------
# loading

def load_spec(path: str, report: Report) -> list[dict]:
    """Return a list of top-level specs found in the file."""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".json":
        with open(path, encoding="utf-8") as fh:
            spec = json.load(fh)
        return [spec]
    if ext in (".html", ".htm"):
        return specs_from_html(path, report)
    if ext == ".py":
        return specs_from_python(path, report)
    report.warn(f"Unknown extension {ext}; trying JSON")
    with open(path, encoding="utf-8") as fh:
        return [json.load(fh)]


def specs_from_html(path, report):
    text = open(path, encoding="utf-8", errors="replace").read()
    specs = []
    dec = json.JSONDecoder()
    for m in re.finditer(r"(?:spec\s*=\s*|vegaEmbed\([^,]+,\s*)(\{)", text):
        start = m.start(1)
        try:
            obj, _ = dec.raw_decode(text[start:])
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and ("$schema" in obj or "mark" in obj or
                                      "layer" in obj or "hconcat" in obj or
                                      "vconcat" in obj or "concat" in obj or
                                      "facet" in obj or "repeat" in obj):
            specs.append(obj)
    for m in re.finditer(r'<script type="application/json"[^>]*>(.*?)</script>',
                         text, flags=re.S):
        try:
            obj = json.loads(m.group(1))
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and "$schema" in obj and "vega" in obj["$schema"]:
            specs.append(obj)
    if not specs:
        report.warn("No Vega-Lite spec found in the HTML. If it is a Streamlit page or "
                    "custom JS, open it in the browser and screenshot it instead.")
    return specs


class _StRecorder:
    """Minimal Streamlit stand-in that records chart objects passed to it."""

    captured: list = []

    def __init__(self, name="st"):
        self._name = name

    def __getattr__(self, item):
        return _StRecorder(f"{self._name}.{item}")

    def __call__(self, *args, **kwargs):
        for a in list(args) + list(kwargs.values()):
            _collect_alt(a, _StRecorder.captured)
        leaf = self._name.rsplit(".", 1)[-1]
        # decorators (@st.cache_data, @st.cache_data(ttl=...), @st.fragment) return the function
        if leaf in ("cache_data", "cache_resource", "cache", "fragment", "dialog",
                    "cache_data()", "cache_resource()", "cache()", "fragment()", "dialog()"):
            if len(args) == 1 and callable(args[0]) and not kwargs:
                return args[0]
        # input widgets return their default value, so the default state of the app is built
        opts = kwargs.get("options", args[1] if len(args) > 1 else None)
        if leaf in ("radio", "selectbox", "segmented_control", "pills", "select_slider"):
            try:
                opts = list(opts)
                if opts:
                    return opts[int(kwargs.get("index") or 0)]
            except Exception:
                pass
        if leaf == "multiselect":
            try:
                return list(kwargs.get("default") or opts or [])
            except Exception:
                return []
        if leaf in ("slider", "number_input"):
            for k in ("value", "min_value"):
                if kwargs.get(k) is not None:
                    return kwargs[k]
            if len(args) > 3:
                return args[3]
            if len(args) > 1:
                return args[1]
        if leaf in ("text_input", "text_area"):
            return kwargs.get("value", "")
        if leaf in ("checkbox", "toggle"):
            return True  # open optional sections so their charts are captured
        if "columns" in self._name or "tabs" in self._name:
            n = args[0] if args and isinstance(args[0], int) else \
                (len(args[0]) if args and isinstance(args[0], (list, tuple)) else 2)
            return [_StRecorder(f"{self._name}[{i}]") for i in range(n)]
        return _StRecorder(self._name + "()")

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def __iter__(self):
        return iter([_StRecorder(self._name + "[0]"), _StRecorder(self._name + "[1]")])

    def __getitem__(self, k):
        return _StRecorder(f"{self._name}[{k}]")

    def __bool__(self):
        # truthy, so charts inside `if st.button(...):` / `if st.checkbox(...):` are captured
        return True


def _collect_alt(obj, out):
    try:
        import altair as alt
    except Exception:
        return
    if isinstance(obj, alt.TopLevelMixin):
        out.append(obj)
    elif isinstance(obj, (list, tuple)):
        for o in obj:
            _collect_alt(o, out)


def specs_from_python(path, report):
    try:
        import altair as alt
    except Exception:
        report.warn("altair is not installed here: cannot execute the script. Save the "
                    "chart with chart.save('chart.json') and pass the JSON instead.")
        return []
    _StRecorder.captured = []
    stub = _StRecorder()
    sys.modules.setdefault("streamlit", types.ModuleType("streamlit"))
    sys.modules["streamlit"].__dict__.update({"__getattr__": lambda n: getattr(stub, n)})
    path = os.path.abspath(path)
    ns = {"__name__": "__main__", "__file__": path}
    cwd = os.getcwd()
    os.chdir(os.path.dirname(path) or ".")
    sys.path.insert(0, os.path.dirname(path))
    try:
        code = open(path, encoding="utf-8").read()
        # neutralize interactive/saving calls
        code = re.sub(r"\.show\(\)", ".to_dict()", code)
        exec(compile(code, path, "exec"), ns)
    except SystemExit:
        pass
    except Exception as e:  # keep going with whatever was built
        report.warn(f"Script raised {type(e).__name__}: {e}")
    finally:
        os.chdir(cwd)
    charts = list(_StRecorder.captured)
    for v in ns.values():
        if isinstance(v, alt.TopLevelMixin) and v not in charts:
            charts.append(v)
    specs = []
    for c in charts:
        try:
            specs.append(c.to_dict())
        except Exception as e:
            report.warn(f"to_dict failed on a chart: {e}")
    if not specs:
        report.warn("No Altair chart objects found in the script namespace.")
    return specs


# ----------------------------------------------------------------------------
# spec walking

def mark_type(mark):
    if isinstance(mark, str):
        return mark
    if isinstance(mark, dict):
        return mark.get("type", "?")
    return "?"


def mark_props(mark):
    return mark if isinstance(mark, dict) else {}


def enc_field(enc, ch):
    e = enc.get(ch) if enc else None
    if not isinstance(e, dict):
        return None
    return e


def ftype(e):
    if not e:
        return None
    t = e.get("type")
    if t:
        return t[0].lower()  # q, n, o, t
    if "aggregate" in e or "bin" in e:
        return "q"
    if "timeUnit" in e:
        return "t"
    return None


def field_name(f):
    """A field may be a string or a {"repeat": "column"} reference."""
    if isinstance(f, dict):
        return f"repeat({f.get('repeat')})"
    return None if f is None else str(f)


def fname(e):
    if not e:
        return None
    if "field" in e:
        agg = e.get("aggregate")
        f = field_name(e["field"])
        return f"{agg}({f})" if agg else f
    if "aggregate" in e:
        return f"{e['aggregate']}()"
    if "value" in e:
        return f"value={e['value']}"
    return None


def resolve_data(spec, datasets, base_dir, report):
    """Return list of row dicts if inline data is reachable, else None."""
    data = spec.get("data")
    if not isinstance(data, dict):
        return None
    if "values" in data and isinstance(data["values"], list):
        return data["values"]
    if "name" in data and data["name"] in datasets:
        v = datasets[data["name"]]
        return v if isinstance(v, list) else None
    url = data.get("url")
    if isinstance(url, str) and not url.startswith("http"):
        p = os.path.join(base_dir, url)
        if os.path.exists(p):
            try:
                if p.lower().endswith(".csv"):
                    with open(p, newline="", encoding="utf-8") as fh:
                        return list(csv.DictReader(fh))
                if p.lower().endswith(".json"):
                    with open(p, encoding="utf-8") as fh:
                        d = json.load(fh)
                    return d if isinstance(d, list) else None
            except Exception as e:
                report.warn(f"Could not read data {url}: {e}")
    if url:
        report.warn(f"Data is external ({url}); category counts and ranges unknown.")
    return None


def walk(spec, ctx, units, datasets, base_dir, report, path="root"):
    """Collect unit specs with inherited data/title/resolve context."""
    ctx = dict(ctx)
    if "datasets" in spec:
        datasets.update(spec["datasets"])
    if "data" in spec:
        ctx["data"] = resolve_data(spec, datasets, base_dir, report)
        ctx["data_desc"] = spec["data"]
    if "title" in spec:
        ctx["title"] = spec["title"]
    if "encoding" in spec and "mark" not in spec:
        ctx["shared_encoding"] = spec["encoding"]
    if "resolve" in spec:
        ctx["resolve"] = spec["resolve"]
    if "params" in spec:
        ctx.setdefault("params", []).extend(spec["params"])
    if "selection" in spec:
        ctx.setdefault("params", []).extend(list(spec["selection"].values()))
    if "width" in spec:
        ctx["width"] = spec["width"]
    if "height" in spec:
        ctx["height"] = spec["height"]
    if "transform" in spec:
        ctx.setdefault("transforms", []).extend(spec["transform"])

    if "mark" in spec:
        enc = dict(ctx.get("shared_encoding", {}))
        enc.update(spec.get("encoding", {}))
        units.append({"path": path, "mark": spec["mark"], "encoding": enc,
                      "ctx": ctx, "spec": spec})
        return
    for key in ("layer", "hconcat", "vconcat", "concat"):
        if key in spec:
            ctx2 = dict(ctx)
            ctx2["composition"] = key
            ctx2["siblings"] = len(spec[key])
            for i, sub in enumerate(spec[key]):
                walk(sub, ctx2, units, datasets, base_dir, report, f"{path}.{key}[{i}]")
            return
    if "repeat" in spec and "spec" in spec:
        ctx2 = dict(ctx)
        ctx2["composition"] = "repeat"
        ctx2["repeat"] = spec["repeat"]
        combos = repeat_combos(spec["repeat"])
        if len(combos) > 24:
            report.warn(f"{path}: {len(combos)} repeated panels; inspecting the first 24")
            combos = combos[:24]
        ctx2["siblings"] = len(combos)
        for combo in combos:
            sub = substitute_repeat(copy.deepcopy(spec["spec"]), combo)
            label = ",".join(str(v) for v in combo.values())
            walk(sub, ctx2, units, datasets, base_dir, report, f"{path}.repeat[{label}]")
        return
    if "facet" in spec and "spec" in spec:
        ctx2 = dict(ctx)
        ctx2["composition"] = "facet"
        ctx2["facet"] = spec["facet"]
        walk(spec["spec"], ctx2, units, datasets, base_dir, report, f"{path}.facet")
        return
    report.warn(f"Unrecognized spec node at {path}")


def repeat_combos(rep):
    """All {repeater: field} assignments of a repeat definition."""
    if isinstance(rep, list):
        return [{"repeat": f} for f in rep]
    if isinstance(rep, dict):
        keys = [k for k in ("row", "column", "layer") if isinstance(rep.get(k), list)]
        return [dict(zip(keys, vals)) for vals in itertools.product(*(rep[k] for k in keys))] or [{}]
    return [{}]


def substitute_repeat(node, combo):
    """Replace {"repeat": "column"} field references with the concrete field name."""
    if isinstance(node, dict):
        if set(node) == {"repeat"} and isinstance(node["repeat"], str) and node["repeat"] in combo:
            return combo[node["repeat"]]
        return {k: substitute_repeat(v, combo) for k, v in node.items()}
    if isinstance(node, list):
        return [substitute_repeat(v, combo) for v in node]
    return node


def iter_nodes(spec, path="root"):
    """Yield (node, path) for the spec and every nested composite or unit node."""
    yield spec, path
    for key in ("layer",) + CONCAT_KEYS:
        if isinstance(spec.get(key), list):
            for i, sub in enumerate(spec[key]):
                if isinstance(sub, dict):
                    yield from iter_nodes(sub, f"{path}.{key}[{i}]")
    if isinstance(spec.get("spec"), dict):
        for key in ("facet", "repeat"):
            if key in spec:
                yield from iter_nodes(spec["spec"], f"{path}.{key}")
                break


def under(upath, npath):
    """True if unit path `upath` lies inside node path `npath`."""
    return upath == npath or upath.startswith(npath + ".") or upath.startswith(npath + "[")


def view_of(path):
    """The view a path belongs to: its deepest concat child, else the top-level spec."""
    m = list(re.finditer(r"\.(?:h|v)?concat\[\d+\]", path))
    return path[:m[-1].end()] if m else path.split(".")[0]


def _own(node):
    """A node without its children, data and parameter definitions (for reference search)."""
    return {k: v for k, v in node.items()
            if k not in ("layer", "spec", "params", "selection", "datasets", "data") + CONCAT_KEYS}


def _refs(obj, name, key=None):
    """Does obj read the parameter `name`? ({"param": name}, v4 {"selection": name}, or an expression)."""
    if isinstance(obj, dict):
        for k in ("param", "selection"):
            v = obj.get(k)
            if v == name:
                return True
            if isinstance(v, dict) and name in json.dumps(v):
                return True
        return any(_refs(v, name, k) for k, v in obj.items())
    if isinstance(obj, list):
        return any(_refs(v, name, key) for v in obj)
    if isinstance(obj, str) and key in ("expr", "test", "filter", "calculate", "signal"):
        return re.search(rf"(?<![\w.]){re.escape(name)}(?![\w])", obj) is not None
    return False


def collect_params(spec, rootpath):
    """Selections and widget parameters of a spec, with where they are defined and read."""
    nodes = list(iter_nodes(spec, rootpath))
    names = {n["name"]: p for n, p in nodes if isinstance(n.get("name"), str)}
    out = []
    for node, p in nodes:
        for prm in node.get("params") or []:
            if not isinstance(prm, dict) or "name" not in prm:
                continue
            views = [names[v] for v in prm.get("views", []) if isinstance(v, str) and v in names] or [p]
            sel = prm.get("select")
            out.append({"name": prm["name"], "select": sel.get("type") if isinstance(sel, dict) else sel,
                        "bind": prm.get("bind"), "defined_in": views})
        if isinstance(node.get("selection"), dict):
            for nm, d in node["selection"].items():
                d = d if isinstance(d, dict) else {}
                out.append({"name": nm, "select": d.get("type", "point"), "bind": d.get("bind"),
                            "defined_in": [p]})
    for prm in out:
        prm["read_in"] = [p for node, p in nodes if _refs(_own(node), prm["name"])]
    return out


# ----------------------------------------------------------------------------
# data helpers

def distinct(rows, field):
    if rows is None or field is None:
        return None
    vals = set()
    for r in rows:
        if isinstance(r, dict) and field in r:
            vals.add(str(r[field]))
    return vals


def numeric_range(rows, field):
    if rows is None or field is None:
        return None
    vals = []
    for r in rows:
        v = r.get(field) if isinstance(r, dict) else None
        if v is None or v == "":
            continue
        try:
            vals.append(float(v))
        except (TypeError, ValueError):
            return None
    if not vals:
        return None
    return min(vals), max(vals), len(vals)


def strip_agg(e):
    return field_name(e.get("field")) if e else None


# ----------------------------------------------------------------------------
# checks

def check_unit(u, report, all_units):
    mark = mark_type(u["mark"])
    props = mark_props(u["mark"])
    enc = u["encoding"]
    ctx = u["ctx"]
    rows = ctx.get("data")
    where = u["path"]
    x, y = enc_field(enc, "x"), enc_field(enc, "y")
    color = enc_field(enc, "color") or enc_field(enc, "fill") or enc_field(enc, "stroke")
    shape = enc_field(enc, "shape")
    size = enc_field(enc, "size")
    theta = enc_field(enc, "theta")
    tx, ty = ftype(x), ftype(y)
    cat_axis, quant_axis, quant_ch = None, None, None
    if tx == "q" and ty in ("n", "o", "t", None):
        quant_axis, quant_ch, cat_axis = x, "x", y
    elif ty == "q" and tx in ("n", "o", "t", None):
        quant_axis, quant_ch, cat_axis = y, "y", x
    elif tx == "q" and ty == "q":
        quant_axis, quant_ch = y, "y"

    report.summary.setdefault("units", []).append({
        "where": where, "mark": mark,
        "x": fname(x), "x_type": tx, "y": fname(y), "y_type": ty,
        "color": fname(color), "color_type": ftype(color),
        "shape": fname(shape), "size": fname(size), "theta": fname(theta),
        "tooltip": "tooltip" in enc, "n_rows": len(rows) if rows else None,
    })

    # ---- marks hidden
    op = props.get("opacity", enc.get("opacity", {}).get("value") if isinstance(enc.get("opacity"), dict) else None)
    if op is not None and float(op) == 0:
        report.add("COL-10", "crit", "Mark opacity is 0: the data is invisible.",
                   f"mark={mark} opacity=0", where=where)

    # ---- zero baseline for length marks
    spans_range = (quant_ch == "x" and "x2" in enc) or (quant_ch == "y" and "y2" in enc)
    if mark in LENGTH_MARKS and quant_axis is not None and not spans_range:
        sc = quant_axis.get("scale", {}) or {}
        zero = sc.get("zero", True)
        dom = sc.get("domain")
        bad = False
        ev = ""
        if zero is False:
            bad, ev = True, "scale.zero=false"
        if isinstance(dom, list) and len(dom) == 2:
            try:
                lo, hi = float(dom[0]), float(dom[1])
                if lo > 0 or hi < 0:
                    bad, ev = True, f"scale.domain={dom}"
            except (TypeError, ValueError):
                pass
        if sc.get("type") == "log":
            report.add("EXP-20", "crit", "Log scale on a length mark: bar lengths "
                       "have no zero and no meaning.", f"mark={mark} scale.type=log",
                       where=where)
        if bad:
            report.add("EXP-08", "crit",
                       "Length/area mark whose quantitative axis does not start at "
                       "zero: bar ratios no longer equal value ratios (TRUNC-1).",
                       ev, where=where,
                       exception="deviation/index bars from an explicit, drawn and "
                                 "labeled non-zero reference")

    # ---- clipping / forced domains
    for ch, e in ((quant_ch, quant_axis), ("x", x), ("y", y)):
        if not e:
            continue
        sc = e.get("scale", {}) or {}
        dom = sc.get("domain")
        if isinstance(dom, list) and len(dom) == 2 and rows is not None:
            rng = numeric_range(rows, strip_agg(e))
            if rng:
                try:
                    lo, hi = float(dom[0]), float(dom[1])
                except (TypeError, ValueError):
                    continue
                if rng[0] < lo or rng[1] > hi:
                    sev = "crit" if props.get("clip") else "major"
                    report.add("EXP-09", sev,
                               "Forced scale domain narrower than the data; values "
                               "outside it are cut off or drawn outside the frame.",
                               f"{ch} domain={dom} data range=({rng[0]}, {rng[1]}) "
                               f"clip={props.get('clip', False)}", where=where)
    if props.get("clip") and not any(
            isinstance((e or {}).get("scale", {}).get("domain"), list) for e in (x, y)):
        report.add("EXP-09", "minor", "clip=true set; verify nothing is cut.",
                   "mark.clip=true", where=where, kind="SEMI")

    # ---- line over nominal
    if mark in ("line", "trail", "area") and tx == "n":
        report.add("EXP-03", "crit",
                   "Line/area connects nominal categories, implying a continuity and "
                   "order that do not exist (TRUNC-10).",
                   f"mark={mark} x={fname(x)}:nominal", where=where,
                   exception="ordinal categories with a natural order, labeled as such")
    if mark in ("line", "trail", "area") and tx == "o" and not looks_temporal(strip_agg(x)):
        report.add("EXP-03", "minor",
                   "Line over an ordinal x: acceptable only if the order is natural.",
                   f"x={fname(x)}:ordinal", where=where, kind="SEMI")

    # ---- bars over time
    if mark == "bar" and cat_axis is not None:
        cname = strip_agg(cat_axis)
        ct = ftype(cat_axis)
        if ct == "t" or (ct in ("o", "n") and looks_temporal(cname)):
            nvals = distinct(rows, cname)
            grouped = "xOffset" in enc or "yOffset" in enc or \
                (color and ftype(color) in ("n", "o") and
                 (props.get("stack") is None and enc.get("column")))
            sev = "major" if (nvals is None or len(nvals) > 6 or grouped) else "minor"
            report.add("EXP-04", sev,
                       "Bars over a temporal key: if the task is the trend, a line "
                       "chart is typically better; grouped bars with time are "
                       "discouraged.", f"{cname} ({ct}), {len(nvals) if nvals else '?'}"
                       f" time values, grouped={bool(grouped)}",
                       where=where, kind="SEMI",
                       exception="few discrete totals where amounts, not trend, are compared")

    # ---- bars: ordering, count, label angle, mean bars
    if mark == "bar" and cat_axis is not None:
        cname = strip_agg(cat_axis)
        nvals = distinct(rows, cname)
        if nvals is not None and len(nvals) > 100:
            report.add("EFF-19", "major", "Hundreds of bars exceed the idiom's "
                       "readable scale.", f"{len(nvals)} categories", where=where)
        if ftype(cat_axis) == "n" and "sort" not in cat_axis and \
                (nvals is None or len(nvals) > 3) and not looks_temporal(cname):
            report.add("CMP-01", "minor",
                       "Nominal bars are not explicitly sorted (default is alphabetical "
                       "by category): sort by value unless name lookup is the task.",
                       f"no `sort` on {cname}", where=where, kind="SEMI")
        ax = cat_axis.get("axis") or {}
        if quant_ch == "y" and ax.get("labelAngle") not in (None, 0) and \
                abs(float(ax.get("labelAngle") or 0)) >= 30:
            report.add("SCL-12", "minor", "Rotated category labels: rotate the bars "
                       "(horizontal bar chart) instead.",
                       f"labelAngle={ax.get('labelAngle')}", where=where)
        agg = (quant_axis or {}).get("aggregate")
        if agg in ("mean", "average", "median"):
            has_points = any(mark_type(o["mark"]) in POINT_MARKS and
                             o["ctx"].get("composition") == "layer" and
                             o["path"].rsplit(".", 1)[0] == where.rsplit(".", 1)[0]
                             for o in all_units)
            report.add("EXP-16", "crit" if not has_points else "major",
                       "Bar height encodes a mean/median of a distribution "
                       "(MEANBAR-1): readers assume the data live inside the bar.",
                       f"aggregate={agg} on {strip_agg(quant_axis)}; raw points layered="
                       f"{has_points}", where=where,
                       exception="bars of counts, sums or proportions")
    if mark in ("errorbar", "errorband"):
        extent = props.get("extent", "stderr")
        report.add("DAT-03", "minor" if extent != "stderr" else "major",
                   f"Interval mark with extent={extent}: it must be named in the "
                   "legend/caption (MEANBAR-4); stderr visually understates variation.",
                   f"mark={mark} extent={extent}", where=where, kind="SEMI")

    # ---- stacking / non-additive / negatives
    stacked = mark in ("bar", "area") and color is not None and \
        props.get("stack", quant_axis.get("stack", True) if quant_axis else True) \
        not in (False, None, "null")
    if stacked and quant_axis is not None:
        vname = strip_agg(quant_axis)
        rng = numeric_range(rows, vname)
        if rng and rng[0] < 0:
            report.add("EXP-06", "crit", "Stacked marks with negative values: the "
                       "stack has no meaning.", f"min({vname})={rng[0]}", where=where)
        if looks_non_additive(vname) and quant_axis.get("aggregate") not in ("count", "sum"):
            report.add("EXP-06", "major", "Stacking a quantity that looks non-additive "
                       "(a rate, temperature, mean, price): the total is meaningless.",
                       f"stacked value={fname(quant_axis)}", where=where, kind="SEMI")
        ncat = distinct(rows, strip_agg(color))
        if ncat is not None and len(ncat) > 6:
            report.add("IDM-STACK", "major", "Stacked chart with many categories: only "
                       "the bottom segment has a baseline; within/among-group comparison "
                       "is hard.", f"{len(ncat)} stacked categories", where=where)
        if mark == "area" and ncat and len(ncat) > 1:
            report.add("EFF-06", "minor", "Stacked area: only the bottom layer can be "
                       "read against a baseline; consider small multiples.",
                       f"{len(ncat)} layers", where=where, kind="SEMI")

    # ---- pie / arc
    if mark == "arc" and theta is not None:
        cfield = strip_agg(color)
        nvals = distinct(rows, cfield)
        if nvals is not None and len(nvals) > 5:
            report.add("IDM-PIE", "crit", "Pie with more than 5 slices: angles cannot "
                       "be compared; use a sorted bar chart.",
                       f"{len(nvals)} slices", where=where)
        elif nvals is None:
            report.add("IDM-PIE", "major", "Pie chart: verify ≤ 5 slices, parts sum to "
                       "100 %, sorted from 12 o'clock.", "arc mark with theta",
                       where=where, kind="SEMI")
        if "sort" not in (color or {}) and "order" not in enc and \
                "sort" not in theta:
            report.add("CMP-01", "minor", "Pie slices not explicitly sorted large→small.",
                       "no sort on theta/color/order", where=where, kind="SEMI")
        if looks_non_additive(strip_agg(theta)):
            report.add("EXP-05", "crit", "Pie of a quantity that is not a part of a whole.",
                       f"theta={fname(theta)}", where=where, kind="SEMI")
        rng = numeric_range(rows, strip_agg(theta))
        if rng and rng[0] < 0:
            report.add("EXP-05", "crit", "Pie with negative values.", f"min={rng[0]}",
                       where=where)

    # ---- color encoding
    if color is not None and "field" in color:
        ct = ftype(color)
        cname = color["field"]
        sc = color.get("scale") or {}
        scheme = sc.get("scheme")
        if isinstance(scheme, dict):
            scheme = scheme.get("name")
        cls = classify_scheme(scheme) if scheme else None
        rng_colors = sc.get("range")
        nvals = distinct(rows, cname)
        numeric = numeric_range(rows, cname)
        # declared nominal but looks ordered
        if ct == "n" and (looks_temporal(cname) or (numeric and numeric[2] > 0 and
                                                     nvals and len(nvals) > 3)):
            report.add("EXP-02", "crit",
                       "An ordered/temporal/numeric attribute is encoded with an "
                       "unordered categorical hue palette: the order is lost and the "
                       "palette may wrap.", f"color={cname}:nominal "
                       f"({len(nvals) if nvals else '?'} values)", where=where,
                       exception="≤3 levels with direct labels, or order carried by x")
        if ct in ("q", "o", "t") and cls == "qualitative":
            report.add("EXP-02", "crit", "Ordered data with a qualitative scheme.",
                       f"color={cname}:{ct} scheme={scheme}", where=where)
        if ct == "n" and cls in ("sequential", "diverging"):
            report.add("EXP-01", "crit", "Nominal data with an ordered color scheme "
                       "implies a false order.", f"color={cname}:nominal scheme={scheme}",
                       where=where, exception="categories do have a stated order")
        if cls == "rainbow":
            report.add("COL-02", "crit", "Rainbow-like scheme: no perceptual order, "
                       "false boundaries, unequal steps.", f"scheme={scheme}", where=where)
        if cls == "redgreen":
            report.add("COL-05", "crit", "Red–green scheme: unreadable for ≈8 % of men.",
                       f"scheme={scheme}", where=where)
        if ct == "q" and sc.get("domainMid") is None and cls == "diverging":
            report.add("COL-12", "minor", "Diverging scheme without an explicit "
                       "midpoint (domainMid): check that the center is meaningful.",
                       f"scheme={scheme}", where=where, kind="SEMI")
        if ct == "n" and nvals is not None:
            n = len(nvals)
            if n > 8:
                report.add("COL-04", "crit" if n > 15 else "major",
                           f"{n} categorical hues: beyond 7–8 they cannot be matched "
                           "to a legend; default palettes wrap after 10.",
                           f"color={cname} distinct={n}", where=where,
                           exception="color only identifies, with direct labels, and "
                                     "exact matching is not a task")
        # redundant color on bars
        if mark == "bar" and cat_axis is not None and cname == strip_agg(cat_axis) \
                and ct == "n" and not enc.get("xOffset") and not enc.get("yOffset"):
            report.add("COL-03", "major", "Each bar has its own hue although position "
                       "already identifies the category; the legend duplicates the "
                       "axis.", f"color={cname} == {quant_ch and 'category axis'}",
                       where=where,
                       exception="same hues identify categories in other panels")
        # CVD check on explicit ranges or known schemes
        cols = None
        if isinstance(rng_colors, list) and rng_colors and isinstance(rng_colors[0], str):
            cols = [parse_color(c) for c in rng_colors]
        elif scheme and scheme_colors(scheme):
            cols = [parse_color(c) for c in scheme_colors(scheme)]
        elif ct == "n" and scheme is None:
            cols = [parse_color(c) for c in scheme_colors("tableau10")]
            k = len(nvals) if nvals else len(cols)
            cols = cols[:max(2, min(k, len(cols)))]
        if cols:
            cols = [c for c in cols if c]
            pr = palette_report(cols)
            report.summary.setdefault("palettes", []).append({"where": where, **pr})
            if pr["has_red_and_green"]:
                report.add("COL-05", "major", "Palette mixes red and green hues; "
                           "colorblind readers may merge them.",
                           f"colors={pr['hex']}", where=where, kind="SEMI",
                           exception="the two categories are also separated by position, "
                                     "shape or direct labels")
            for p in pr["confusable_deuteranopia"][:5]:
                report.add("COL-05", "major", "Two palette colors become nearly identical "
                           "under deuteranopia.",
                           f"{p['a']} vs {p['b']}: ΔE normal={p['dE_normal']}, "
                           f"simulated={p['dE_simulated']}", where=where)
        if color.get("legend", "x") is None and mark != "text":
            layer_prefix = where.rsplit(".layer[", 1)[0] if ".layer[" in where else None
            labelled = layer_prefix is not None and any(
                (v.get("mark") if isinstance(v.get("mark"), str) else (v.get("mark") or {}).get("type")) == "text"
                and v["path"].startswith(layer_prefix)
                and (fname(v["encoding"].get("color")) == cname or fname(v["encoding"].get("text")) == cname)
                for v in all_units if v["path"] != where)
            if labelled:
                report.summary.setdefault("notes", []).append(
                    f"{where}: legend for {cname} removed but a text layer labels the marks directly")
            else:
                report.add("TXT-07", "major", "Color legend removed: the encoding is not "
                           "explained.", f"color={cname} legend=null", where=where,
                           exception="direct labels replace the legend")
        # geoshape of raw counts
        if mark == "geoshape" and ct == "q" and looks_like_raw_count(cname):
            report.add("EXP-12", "major", "Choropleth of a raw count/total: large "
                       "regions dominate; normalize (rate, per capita, density).",
                       f"color={cname}", where=where, kind="SEMI")
        if mark == "rect" and ct in ("q", "o") and cls == "qualitative":
            report.add("IDM-HEATMAP", "crit", "Heatmap values with a categorical "
                       "palette.", f"scheme={scheme}", where=where)
    elif color is not None and "value" in color:
        pass
    # channels silently dropped by Vega-Lite for this mark type
    if shape is not None and "field" in shape and mark != "point":
        report.add("EXP-09", "crit",
                   f"The shape channel is ignored for mark '{mark}' (only 'point' "
                   "supports shape): the attribute is not encoded at all, with no "
                   "warning in the rendered chart.",
                   f"shape={shape['field']} mark={mark}", where=where)
    if size is not None and "field" in size and mark in ("rect", "geoshape", "arc"):
        report.add("EXP-09", "major", f"The size channel is ignored for mark '{mark}'.",
                   f"size={size['field']}", where=where)
    for ch in ("x", "y"):
        e = enc_field(enc, ch)
        if e and mark == "arc" and "field" in e:
            pass
    # shape
    if shape is not None and "field" in shape and mark == "point":
        nvals = distinct(rows, shape["field"])
        if nvals is not None and len(nvals) > 4:
            report.add("EFF-08", "major", "More than 4 shape categories: shape is a weak "
                       "channel.", f"shape={shape['field']} distinct={len(nvals)}",
                       where=where)
        if color is not None and "field" in color and color["field"] != shape["field"]:
            report.add("EFF-08", "major", "Color and shape encode different attributes: "
                       "finding an item becomes a conjunction search.",
                       f"color={color['field']} shape={shape['field']}", where=where,
                       kind="SEMI", exception="the task never requires matching both")
    if size is not None and "field" in size and mark == "bar":
        report.add("EXP-10", "major", "Size channel on bars: bar width carries no "
                   "readable quantity.", f"size={size['field']}", where=where)

    # ---- lines: how many
    if mark in ("line", "trail"):
        key = color if (color and "field" in color) else enc_field(enc, "detail")
        if key and "field" in key:
            nvals = distinct(rows, key["field"])
            if nvals is not None and len(nvals) > MAX_LINES:
                report.add("EFF-16", "major", f"{len(nvals)} lines in one panel "
                           f"(spaghetti, more than about {MAX_LINES}): highlight a few "
                           "against grey, facet, or use a heatmap.",
                           f"series={key['field']}", where=where)
        if quant_axis is not None and rows is not None:
            rng = numeric_range(rows, strip_agg(quant_axis))
            sc = quant_axis.get("scale", {}) or {}
            if rng and sc.get("zero", False) is True and rng[0] > 0 and \
                    (rng[1] - rng[0]) / max(rng[1], 1e-9) < 0.15:
                report.add("SCL-04", "major", "Line chart forced to zero while the data "
                           "vary within a narrow band: the trend is flattened "
                           "(TRUNC-5).", f"data range {rng[0]}–{rng[1]} with zero=true",
                           where=where, kind="SEMI")

    # ---- points: overplotting, axis margins
    if mark in POINT_MARKS and rows is not None:
        n = len(rows)
        op = props.get("opacity")
        op_enc = enc.get("opacity")
        if n > 2000 and (op is None or float(op) >= 0.9) and op_enc is None:
            report.add("EFF-16", "major", f"{n} opaque points: overplotting hides "
                       "density; use opacity, binning, sampling or facets.",
                       f"rows={n} opacity={op}", where=where, kind="SEMI")
        for e, nm in ((x, "x"), (y, "y")):
            if e and ftype(e) == "q" and "bin" not in e:
                rng = numeric_range(rows, strip_agg(e))
                sc = e.get("scale", {}) or {}
                if rng and sc.get("zero", True) is not False and rng[0] > 0 and \
                        (rng[1] - rng[0]) / rng[1] < 0.5 and "domain" not in sc:
                    report.add("SCL-05", "major", f"Scatter {nm} axis includes zero "
                               "although the data start far from it: the cloud is "
                               "compressed and space wasted (TRUNC-11).",
                               f"{nm}={strip_agg(e)} range {rng[0]}–{rng[1]}, "
                               "scale.zero not false", where=where, kind="SEMI")
        if size is not None and "field" in size:
            sc = size.get("scale", {}) or {}
            if sc.get("type") in ("sqrt", "pow"):
                pass  # explicit, assume intentional
            report.add("EFF-02", "minor", "Bubble sizes (area) are read inaccurately "
                       "(Stevens ≈0.7); keep a size legend and avoid precise tasks on "
                       "size.", f"size={size['field']}", where=where, kind="SEMI")

    # ---- random jitter
    transforms = ctx.get("transforms") or []
    jit = {t.get("as") for t in transforms if isinstance(t, dict) and
           isinstance(t.get("calculate"), str) and
           re.search(r"\b(random|sampleNormal|sampleUniform)\s*\(", t["calculate"])}
    jit_ch = [ch for ch in ("x", "y", "xOffset", "yOffset")
              if (enc_field(enc, ch) or {}).get("field") in jit]
    if jit_ch:
        report.add("EXP-21", "major", "Marks are displaced by random noise: the picture "
                   "changes on every render and shows clusters and gaps that are not in "
                   "the data (RAIN-2). Use a strip at the true positions, a beeswarm, or "
                   "a seeded and stated offset.",
                   f"calculate with random() feeds {', '.join(jit_ch)}", where=where,
                   kind="SEMI", exception="seeded, disclosed jitter with a density layer "
                                          "carrying the distribution")

    # ---- bins and bandwidth nobody chose
    for e, nm in ((x, "x"), (y, "y")):
        b = (e or {}).get("bin")
        if b is True or (isinstance(b, dict) and not any(
                k in b for k in ("maxbins", "step", "steps", "extent", "binned"))):
            report.add("EXP-15", "minor", f"{nm} is binned with the library default: the "
                       "bin width shapes the distribution; choose it, state it and try "
                       "another (RAIN-4).", f"{nm}.bin={json.dumps(b)}", where=where,
                       kind="SEMI")
    for t in transforms:
        if isinstance(t, dict) and "density" in t and not t.get("bandwidth"):
            report.add("EXP-15", "minor", "Density estimate with the default bandwidth: "
                       "it can merge modes or invent them; choose it and state it "
                       "(RAIN-4). Not for discrete or rounded values (EXP-22).",
                       f"density of {t.get('density')} without bandwidth", where=where,
                       kind="SEMI")

    # ---- box plot whiskers
    if mark == "boxplot":
        extent = props.get("extent", 1.5)
        report.add("DAT-10", "minor", "Box plot: say in the chart what the whiskers "
                   f"mean ({'min–max' if extent == 'min-max' else str(extent) + ' × IQR'}"
                   f"{'' if 'extent' in props else ', the library default'}); a box hides "
                   "multimodality and n (RAIN-6).", f"mark=boxplot extent={extent}",
                   where=where, kind="SEMI", exception="the caption defines the whiskers")

    # ---- axis titles / units
    for e, nm in ((x, "x"), (y, "y")):
        if not e or "field" not in e and "aggregate" not in e:
            continue
        ax = e.get("axis", "x")
        if ax is None:
            if "text" not in mark and mark != "arc":
                report.add("SCL-06", "major", f"{nm} axis removed.", f"{nm}.axis=null",
                           where=where, kind="SEMI",
                           exception="values are directly labeled on the marks")
            continue
        title = e.get("title", (ax or {}).get("title") if isinstance(ax, dict) else None)
        removed = ("title" in e and e["title"] is None) or (isinstance(ax, dict) and "title" in ax and ax["title"] is None)
        if removed:
            if ftype(e) == "q" and "text" not in mark:
                report.add("SCL-06", "minor", f"{nm} axis title removed.", f"{nm}.title=null",
                           where=where, kind="SEMI",
                           exception="the quantity is self-evident (years) or named in the chart title")
            continue
        shown = title if title is not None else fname(e)
        if title is None and looks_like_raw_name(shown):
            report.add("SCL-06", "major", f"{nm} axis title is a raw variable name.",
                       f"{nm} title would render as '{shown}'", where=where)
        elif title is not None and looks_like_raw_name(title):
            report.add("SCL-06", "major", f"{nm} axis title looks like a raw name.",
                       f"{nm}.title='{title}'", where=where)
        if ftype(e) == "q" and not has_units(shown or ""):
            report.add("SCL-06", "minor", f"No units detected in the {nm} axis title.",
                       f"'{shown}'", where=where, kind="SEMI",
                       exception="the quantity is unitless (count, ratio)")
    # legend titles
    if color is not None and "field" in color and color.get("legend", "x") is not None:
        lt = color.get("title") or (color.get("legend") or {}).get("title") \
            if isinstance(color.get("legend"), dict) else color.get("title")
        if lt is None and looks_like_raw_name(color["field"]):
            report.add("TXT-03", "minor", "Legend title is a raw field name.",
                       f"color.field={color['field']}", where=where)

    # ---- tooltip / interaction info
    if "tooltip" in enc:
        report.summary["has_tooltip"] = True
    if ctx.get("params"):
        report.summary["n_params"] = len(ctx["params"])

    # ---- size of the panel
    w, h = ctx.get("width"), ctx.get("height")
    multiples = ctx.get("composition") in ("facet", "repeat") or ".facet" in where or \
        ".repeat" in where or any(k in enc for k in ("facet", "row", "column"))
    if not multiples and \
            (isinstance(w, (int, float)) and w < 150 or isinstance(h, (int, float)) and h < 100):
        report.add("EFF-18", "minor", "Very small panel.", f"width={w} height={h}",
                   where=where, kind="SEMI")


def _axis_fields(units, npath, axis):
    """Quantitative fields drawn on `axis` by the units inside node `npath`."""
    out = {}
    for u in units:
        if not under(u["path"], npath) or mark_type(u["mark"]) == "text":
            continue  # text layers position labels, they do not draw the measure
        e = enc_field(u["encoding"], axis)
        if e and ftype(e) == "q" and "field" in e:
            out.setdefault(fname(e), []).append(e)
    return out


def check_views(units, roots, report):
    """Scales across panels, layers, selections and linking between views."""
    all_params, linked = [], set()
    for spec, rootpath in roots:
        nodes = list(iter_nodes(spec, rootpath))
        for node, p in nodes:
            sc = (node.get("resolve") or {}).get("scale") or {}
            # dual axes, at any depth
            if "layer" in node and sc.get("y") == "independent":
                fields = {fname(enc_field(l.get("encoding", {}), "y")) for l in node["layer"]
                          if isinstance(l, dict)}
                report.add("EXP-11", "crit", "Layered chart with independent y scales "
                           "(dual axes): alignment is arbitrary, crossings and relative "
                           "heights are meaningless.", f"resolve.scale.y=independent; y "
                           f"fields={sorted(f for f in fields if f)}", where=p)
            if "layer" in node and sc.get("x") == "independent":
                report.add("EXP-11", "major", "Layered chart with independent x scales.",
                           "resolve.scale.x=independent", where=p)
            # too many superimposed area layers
            if "layer" in node:
                areas = [l for l in node["layer"] if isinstance(l, dict) and
                         mark_type(l.get("mark")) == "area"]
                if len(areas) > 2:
                    report.add("CMP-10", "major", f"{len(areas)} superimposed area layers: "
                               "beyond two (three with care) filled layers occlude each "
                               "other and mix colors; use lines, small multiples or a "
                               "stacked design.", f"{len(areas)} area marks in one layer",
                               where=p, kind="SEMI")
            key = next((k for k in ("facet", "repeat") + CONCAT_KEYS if k in node), None)
            if key is None or (key in ("facet", "repeat") and "spec" not in node):
                continue
            for axis in ("x", "y"):
                fields = _axis_fields(units, p, axis)
                if sc.get(axis) == "independent":
                    types = {ftype(enc_field(u["encoding"], axis)) for u in units
                             if under(u["path"], p) and enc_field(u["encoding"], axis)}
                    if types and types <= {"n", "o"}:
                        report.add("SCL-08", "info", f"{key} with independent categorical "
                                   f"{axis} axes: fine when each panel lists its own "
                                   "categories; check that panels meant to align do.",
                                   f"resolve.scale.{axis}=independent on a nominal/"
                                   "ordinal axis", where=p, kind="SEMI")
                    elif len(fields) > 1 and key != "facet":
                        report.add("SCL-08", "info", f"{key} with independent {axis} "
                                   "scales over different measures: acceptable if every "
                                   "axis is titled with its unit.",
                                   f"resolve.scale.{axis}=independent; fields="
                                   f"{sorted(fields)}", where=p, kind="SEMI")
                    else:
                        report.add("SCL-08", "major", f"{key} with independent {axis} "
                                   "scales: panels cannot be compared.",
                                   f"resolve.scale.{axis}=independent", where=p,
                                   kind="SEMI",
                                   exception="each panel's own variation is the task "
                                             "and this is stated")
        # the same measure in several concatenated views, each on its own scale
        node_at = dict((p, n) for n, p in nodes)
        spec_views = sorted({view_of(u["path"]) for u in units if under(u["path"], rootpath)})
        for axis in ("x", "y"):
            per_view = {v: _axis_fields(units, v, axis) for v in spec_views}
            for f in sorted({f for d in per_view.values() for f in d}):
                holders = [v for v in spec_views if f in per_view[v]]
                if len(holders) < 2:
                    continue
                segs = [h.split(".") for h in holders]
                common = []
                for parts in zip(*segs):
                    if len(set(parts)) > 1:
                        break
                    common.append(parts[0])
                anc = node_at.get(".".join(common)) or {}
                if ((anc.get("resolve") or {}).get("scale") or {}).get(axis) in ("shared", "independent"):
                    continue  # shared on purpose, or independent and reported above
                encs = [e for h in holders for e in per_view[h][f]]
                if any(e.get("bin") for e in encs):
                    continue
                doms = [json.dumps((e.get("scale") or {}).get("domain"), sort_keys=True) for e in encs]
                if all(d != "null" for d in doms) and len(set(doms)) == 1:
                    continue  # same explicit domain everywhere
                if any('"param"' in d or '"selection"' in d for d in doms):
                    continue  # overview + detail: the detail rescales on purpose
                report.add("SCL-08", "minor", f"{len(holders)} concatenated views draw {f} "
                           f"on {axis}, each with its own scale (Vega-Lite's default for "
                           "concatenation): equal positions do not mean equal values. "
                           "Share the scale (resolve_scale) or set one domain.",
                           f"{axis}={f} in {', '.join(holders)}; no resolve.scale.{axis}=shared",
                           where=".".join(common) or rootpath, kind="SEMI",
                           exception="overview + detail, or each panel's own variation "
                                     "is the task and this is stated")
        params = collect_params(spec, rootpath)
        all_params.extend(params)
        for prm in params:
            dviews = {view_of(x) for x in prm["defined_in"]}
            rviews = {view_of(x) for x in prm["read_in"]}
            for a in dviews | rviews:
                for b in rviews:
                    if a != b:
                        linked.add(frozenset((a, b)))
            if prm["bind"] == "scales":
                continue  # pan / zoom
            if not prm["read_in"]:
                if prm["select"]:
                    report.add("INT-09", "major", f"Selection '{prm['name']}' "
                               f"({prm['select']}) is declared but nothing reads it: no "
                               "condition, filter or scale domain changes when the reader "
                               "selects.", f"defined in {', '.join(prm['defined_in'])}; "
                               "read nowhere", where=prm["defined_in"][0])
                elif prm["bind"]:
                    report.add("INT-09", "minor", f"Widget parameter '{prm['name']}' is "
                               "bound to an input but nothing reads it.",
                               f"bind={json.dumps(prm['bind'])[:80]}",
                               where=prm["defined_in"][0])
        # multiform views of the same data with no shared selection
        interactive = any(prm["select"] for prm in params)
        info = []
        for v in spec_views:
            us = [u for u in units if view_of(u["path"]) == v]
            marks = {mark_type(u["mark"]) for u in us} - {"text", "rule"}
            data = {json.dumps(u["ctx"].get("data_desc"), sort_keys=True, default=str)
                    for u in us if u["ctx"].get("data_desc") is not None}
            info.append((v, marks, data))
        pairs = [f"{pa} ({'+'.join(sorted(ma))}) / {pb} ({'+'.join(sorted(mb))})"
                 for (pa, ma, da), (pb, mb, db) in itertools.combinations(info, 2)
                 if ma and mb and ma != mb and (da & db)
                 and frozenset((pa, pb)) not in linked]
        if pairs:
            more = f"; and {len(pairs) - 4} more pairs" if len(pairs) > 4 else ""
            report.add("CMP-09", "major" if interactive else "minor",
                       "Views show the same data in different encodings with no "
                       "selection shared between them: an item of one view cannot be "
                       "found in the other.", "; ".join(pairs[:4]) + more, where=rootpath,
                       kind="SEMI", exception="static medium: shared order, color and "
                                              "direct labels do the linking")
        # highlight colors driven by selections
        hl = {}
        for u in units:
            if not under(u["path"], rootpath):
                continue
            for ch in ("color", "fill", "stroke"):
                e = u["encoding"].get(ch)
                conds = e.get("condition") if isinstance(e, dict) else None
                for c in (conds if isinstance(conds, list) else [conds]):
                    if isinstance(c, dict) and ("param" in c or "selection" in c) and \
                            isinstance(c.get("value"), str):
                        col = parse_color(c["value"])
                        hl.setdefault(to_hex(col) if col else c["value"].lower(),
                                      set()).add(view_of(u["path"]))
        if len(hl) > 1 and len({v for vs in hl.values() for v in vs}) > 1:
            report.add("INT-10", "minor", "Selections highlight with different colors in "
                       "different views: one highlight color with one meaning everywhere.",
                       "; ".join(f"{c} in {', '.join(sorted(v))}" for c, v in sorted(hl.items())),
                       where=rootpath, kind="SEMI",
                       exception="the colors mark different selections on purpose")
    if all_params:
        report.summary["params"] = [
            {"name": p["name"], "select": p["select"],
             "bind": p["bind"] if isinstance(p["bind"], str) else bool(p["bind"]),
             "defined_in": p["defined_in"], "read_in": p["read_in"]} for p in all_params]
    views = sorted({view_of(u["path"]) for u in units})
    report.summary["n_views"] = len(views)
    if len(views) > 1:
        report.summary["views"] = views
        report.summary["linked_views"] = sorted(sorted(x) for x in linked)


def check_composition(units, specs, report):
    # chart title
    for spec in specs:
        t = spec.get("title")
        if t is None:
            # maybe the children have titles
            if not any(u["ctx"].get("title") for u in units):
                report.add("TXT-01", "major", "No chart title (TEXT-1). An explanatory "
                           "chart should carry its takeaway in the title.", "title "
                           "absent at every level", where="root", kind="SEMI",
                           exception="a caption in the surrounding document does the "
                                     "title's job")
        else:
            txt = t.get("text") if isinstance(t, dict) else t
            txt = " ".join(txt) if isinstance(txt, list) else str(txt)
            report.summary["title"] = txt
            if looks_like_raw_name(txt) or len(txt.split()) <= 2:
                report.add("TXT-01", "minor", "Title is a bare name, not a message.",
                           f"title='{txt}'", where="root", kind="SEMI")
    # legend count / memory: the same field on the same channel family in several views
    # (a linked dashboard) is one legend to remember, not one per view
    legends = set()
    for u in units:
        for ch in ("color", "fill", "stroke", "shape", "size", "opacity"):
            e = enc_field(u["encoding"], ch)
            if e and "field" in e and e.get("legend", "x") is not None:
                fam = "color" if ch in ("color", "fill", "stroke") else ch
                legends.add((fam, field_name(e["field"])))
    if len(legends) > 2:
        report.add("EFF-11", "major", f"{len(legends)} different legends to hold in "
                   "working memory (3–4 chunks).",
                   ", ".join(f"{f}:{n}" for f, n in sorted(legends)), where="root",
                   kind="SEMI")
    # text / annotation count
    ntext = sum(1 for u in units if mark_type(u["mark"]) == "text")
    report.summary["n_text_layers"] = ntext
    report.summary["n_units"] = len(units)
    marks = sorted({mark_type(u["mark"]) for u in units})
    report.summary["marks"] = marks
    if "errorbar" in marks or "errorband" in marks:
        pass
    # 3D not possible in Vega-Lite
    # font sizes
    for spec in specs:
        cfg = spec.get("config", {}) or {}
        for sec in ("axis", "legend", "title", "text"):
            fs = (cfg.get(sec) or {}).get("labelFontSize") or (cfg.get(sec) or {}).get("fontSize")
            if isinstance(fs, (int, float)) and fs < 9:
                report.add("ACC-05", "major", f"Font size {fs}px in config.{sec} is "
                           "below legibility thresholds.", f"config.{sec}", where="root")


def render(spec, out_png, report):
    try:
        import vl_convert as vlc
        png = vlc.vegalite_to_png(json.dumps(spec), scale=2)
        with open(out_png, "wb") as fh:
            fh.write(png)
        report.artifacts.append(out_png)
        return
    except Exception as e:
        report.warn(f"vl_convert render failed or unavailable ({e}); writing an HTML "
                   "you can open in the browser instead.")
    html = out_png.rsplit(".", 1)[0] + ".html"
    with open(html, "w", encoding="utf-8") as fh:
        fh.write("""<!doctype html><html><head><meta charset="utf-8">
<script src="https://cdn.jsdelivr.net/npm/vega@5"></script>
<script src="https://cdn.jsdelivr.net/npm/vega-lite@5"></script>
<script src="https://cdn.jsdelivr.net/npm/vega-embed@6"></script>
</head><body><div id="vis"></div><script>
vegaEmbed('#vis', %s, {actions:false});
</script></body></html>""" % json.dumps(spec))
    report.artifacts.append(html)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path")
    ap.add_argument("--render", help="write a PNG (needs vl_convert) or HTML fallback")
    ap.add_argument("--data", help="CSV/JSON with the chart data when the spec uses a "
                    "URL the script cannot read")
    args = ap.parse_args()

    report = Report(args.path, "vegalite")
    try:
        specs = load_spec(args.path, report)
    except Exception as e:
        report.warn(f"Could not load spec: {e}")
        report.dump()
        return
    base_dir = os.path.dirname(os.path.abspath(args.path))
    ext_rows = None
    if args.data and os.path.exists(args.data):
        try:
            if args.data.lower().endswith(".csv"):
                with open(args.data, newline="", encoding="utf-8") as fh:
                    ext_rows = list(csv.DictReader(fh))
            else:
                with open(args.data, encoding="utf-8") as fh:
                    ext_rows = json.load(fh)
        except Exception as e:
            report.warn(f"--data unreadable: {e}")
    units = []
    for i, spec in enumerate(specs):
        datasets = {}
        ctx = {"data": ext_rows} if ext_rows else {}
        try:
            walk(spec, ctx, units, datasets, base_dir, report,
                 "root" if len(specs) == 1 else f"spec[{i}]")
        except Exception as e:
            report.warn(f"walk failed on spec {i}: {e}")
    for u in units:
        try:
            check_unit(u, report, units)
        except Exception as e:
            report.warn(f"check failed at {u['path']}: {type(e).__name__}: {e}")
    try:
        check_composition(units, specs, report)
    except Exception as e:
        report.warn(f"composition checks failed: {e}")
    try:
        roots = [(spec, "root" if len(specs) == 1 else f"spec[{i}]")
                 for i, spec in enumerate(specs)]
        check_views(units, roots, report)
    except Exception as e:
        report.warn(f"multi-view checks failed: {type(e).__name__}: {e}")
    if args.render and specs:
        render(specs[0], args.render, report)
    report.dump()


if __name__ == "__main__":
    main()
