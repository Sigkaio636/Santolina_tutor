#!/usr/bin/env python3
"""Deterministic checks on matplotlib / seaborn figures built by a Python script.

The script is executed headless (Agg backend); plt.show() is a no-op and figures are
kept open so every Figure can be inspected. Each figure is saved as PNG in --out-dir.

Usage:
    python3 inspect_matplotlib.py plot.py [--out-dir DIR]

Output: JSON report on stdout with rule IDs from references/rules-catalog.md.
"""
from __future__ import annotations

import argparse
import math
import os
import re
import sys
import tempfile
import types

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vischeck.findings import (Report, looks_like_raw_name, has_units,  # noqa: E402
                               looks_temporal)
from vischeck.color import (parse_color, palette_report, relative_luminance,  # noqa: E402
                            to_hex, is_neutral, contrast_ratio)
from vischeck.palettes import classify_scheme  # noqa: E402

os.environ["MPLBACKEND"] = "Agg"
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.container import BarContainer, ErrorbarContainer  # noqa: E402
from matplotlib.patches import Wedge, Rectangle  # noqa: E402
from matplotlib.collections import PathCollection, QuadMesh  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.text import Annotation  # noqa: E402
from matplotlib.image import AxesImage  # noqa: E402


# ----------------------------------------------------------------------------
# run the script

class _StRecorder:
    def __init__(self, name="st"):
        self._name = name

    def __getattr__(self, item):
        return _StRecorder(f"{self._name}.{item}")

    def __call__(self, *a, **k):
        if "columns" in self._name or "tabs" in self._name:
            n = a[0] if a and isinstance(a[0], int) else \
                (len(a[0]) if a and isinstance(a[0], (list, tuple)) else 2)
            return [_StRecorder(f"{self._name}[{i}]") for i in range(n)]
        return _StRecorder(self._name + "()")

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


def run_script(path, report):
    st = types.ModuleType("streamlit")
    rec = _StRecorder()
    st.__getattr__ = lambda n: getattr(rec, n)  # type: ignore[attr-defined]
    sys.modules["streamlit"] = st
    plt.show = lambda *a, **k: None
    real_close = plt.close
    plt.close = lambda *a, **k: None  # keep figures alive
    ns = {"__name__": "__main__", "__file__": os.path.abspath(path)}
    src = open(path, encoding="utf-8").read()
    cwd = os.getcwd()
    os.chdir(os.path.dirname(os.path.abspath(path)) or ".")
    try:
        exec(compile(src, path, "exec"), ns)
    except SystemExit:
        pass
    except Exception as e:
        report.warn(f"Script raised {type(e).__name__}: {e}; inspecting figures built "
                    "before the error.")
    finally:
        os.chdir(cwd)
        plt.close = real_close
    figs = [plt.figure(n) for n in plt.get_fignums()]
    return figs, src


# ----------------------------------------------------------------------------
# helpers

def is_categorical_axis(axis):
    try:
        conv = axis.get_converter() if hasattr(axis, "get_converter") else axis.converter
    except Exception:
        conv = None
    if conv is not None and "StrCategory" in type(conv).__name__:
        return True
    try:
        from matplotlib.ticker import FixedFormatter
        if isinstance(axis.get_major_formatter(), FixedFormatter):
            labels = [t.get_text() for t in axis.get_majorticklabels()]
            return any(l and not re.fullmatch(r"[-+\d.,eE%\s]+", l) for l in labels)
    except Exception:
        pass
    return False


def data_lines(ax):
    """Line2D artists that look like data series (≥3 points, visible, not ref lines)."""
    out = []
    for ln in ax.lines:
        if not ln.get_visible():
            continue
        try:
            xd = ln.get_xdata(orig=False)
            n = len(xd)
        except Exception:
            continue
        if n < 3:
            continue
        if ln.get_linestyle() in ("None", "none", "", " ") and ln.get_marker() in ("None", "", None):
            continue
        out.append(ln)
    return out


def artist_colors(ax):
    cols = []
    for ln in data_lines(ax):
        c = parse_color(matplotlib.colors.to_hex(ln.get_color()))
        if c:
            cols.append(c)
    for cont in ax.containers:
        if isinstance(cont, BarContainer):
            for p in cont.patches:
                c = parse_color(matplotlib.colors.to_hex(p.get_facecolor()))
                if c:
                    cols.append(c)
    for p in ax.patches:
        if isinstance(p, (Wedge, Rectangle)) and p.get_visible():
            try:
                c = parse_color(matplotlib.colors.to_hex(p.get_facecolor()))
            except Exception:
                c = None
            if c:
                cols.append(c)
    for coll in ax.collections:
        if isinstance(coll, PathCollection):
            fcs = coll.get_facecolors()
            for fc in fcs[:50]:
                c = parse_color(matplotlib.colors.to_hex(fc))
                if c:
                    cols.append(c)
    # distinct
    seen, out = set(), []
    for c in cols:
        h = to_hex(c)
        if h not in seen:
            seen.add(h)
            out.append(c)
    return out


def twin_axes(fig):
    pairs = []
    axes = [a for a in fig.axes if a.get_visible()]
    for i in range(len(axes)):
        for j in range(i + 1, len(axes)):
            a, b = axes[i], axes[j]
            if a.get_position().bounds == b.get_position().bounds and \
                    (a.get_shared_x_axes().joined(a, b) or a.get_shared_y_axes().joined(a, b)):
                pairs.append((a, b))
    return pairs


def src_has(src, *patterns):
    return [p for p in patterns if re.search(p, src)]


# ----------------------------------------------------------------------------
# checks

def check_axes(ax, fig, report, src, idx):
    where = f"fig{fig.number}.ax{idx}"
    summ = {"where": where, "title": ax.get_title(), "xlabel": ax.get_xlabel(),
            "ylabel": ax.get_ylabel()}
    # 3D
    if getattr(ax, "name", "") == "3d":
        report.add("EFF-03", "crit", "3D axes for abstract data: perspective, occlusion "
                   "and depth judgments destroy comparison.", "projection='3d'",
                   where=where, exception="inherently 3D spatial data")
        report.summary.setdefault("axes", []).append(summ)
        return

    bars = [c for c in ax.containers if isinstance(c, BarContainer)]
    errs = [c for c in ax.containers if isinstance(c, ErrorbarContainer)]
    wedges = [p for p in ax.patches if isinstance(p, Wedge)]
    lines = data_lines(ax)
    scatters = [c for c in ax.collections if isinstance(c, PathCollection)]
    images = [im for im in ax.images if isinstance(im, AxesImage)] + \
             [c for c in ax.collections if isinstance(c, QuadMesh)]
    texts = [t for t in ax.texts if t.get_text().strip()]
    annots = [t for t in ax.texts if isinstance(t, Annotation)]
    summ.update({"n_bar_containers": len(bars), "n_bars": sum(len(b) for b in bars),
                 "n_wedges": len(wedges), "n_lines": len(lines),
                 "n_scatter": len(scatters), "n_texts": len(texts),
                 "n_annotations": len(annots), "n_images": len(images)})
    xcat, ycat = is_categorical_axis(ax.xaxis), is_categorical_axis(ax.yaxis)
    xlim = tuple(float(v) for v in ax.get_xlim())
    ylim = tuple(float(v) for v in ax.get_ylim())
    summ["xlim"], summ["ylim"] = [round(v, 3) for v in xlim], [round(v, 3) for v in ylim]

    # ---- bars
    if bars:
        vertical = all(getattr(b, "orientation", "vertical") == "vertical" for b in bars)
        qlim = ylim if vertical else xlim
        qscale = ax.get_yscale() if vertical else ax.get_xscale()
        heights = []
        for b in bars:
            for p in b.patches:
                heights.append(float(p.get_height() if vertical else p.get_width()))
        pos = [h for h in heights if h > 0]
        if qscale == "log":
            report.add("EXP-20", "crit", "Bars on a log scale: no zero, lengths "
                       "meaningless.", f"{'y' if vertical else 'x'}scale=log", where=where)
        elif pos and (qlim[0] > 0 or (qlim[1] < 0 and not pos)):
            report.add("EXP-08", "crit", "Bars whose quantitative axis does not start at "
                       "zero (TRUNC-1): bar ratios no longer equal value ratios.",
                       f"{'ylim' if vertical else 'xlim'}={[round(v, 3) for v in qlim]}, "
                       f"min bar={min(pos):.3g}", where=where,
                       exception="deviation bars from a drawn, labeled reference")
        n = len(heights)
        if n > 100:
            report.add("EFF-19", "major", f"{n} bars: beyond readable scale.", "", where=where)
        # sorted?
        cat_axis = ax.xaxis if vertical else ax.yaxis
        if len(bars) == 1 and n > 3 and (xcat if vertical else ycat):
            hs = heights
            if hs != sorted(hs) and hs != sorted(hs, reverse=True):
                labels = [t.get_text() for t in cat_axis.get_majorticklabels()]
                if not any(looks_temporal(l) for l in labels[:3]):
                    report.add("CMP-01", "minor", "Bars not sorted by value (nor "
                               "obviously by a meaningful order).", f"heights={[
                                   round(h, 3) for h in hs[:12]]}", where=where,
                               kind="SEMI",
                               exception="categories have a natural order (time, size "
                                         "classes) or name lookup is the task")
        # colors per bar
        for b in bars:
            fcs = {matplotlib.colors.to_hex(p.get_facecolor()) for p in b.patches}
            if len(fcs) > 2 and len(fcs) >= len(b.patches) - 1 and len(b.patches) > 3:
                report.add("COL-03", "major", "A different hue per bar although position "
                           "already identifies the category.",
                           f"{len(fcs)} colors for {len(b.patches)} bars", where=where,
                           exception="same hues identify categories in other panels")
        # time on a categorical axis
        labels = [t.get_text() for t in cat_axis.get_majorticklabels()]
        if (xcat if vertical else ycat) and n >= 6 and \
                sum(1 for l in labels if re.fullmatch(r"(19|20)\d\d([-/]\d\d)?", l.strip())) >= max(3, len(labels) // 2):
            report.add("EXP-04", "major", "Bars over years: if the task is the trend, a "
                       "line chart is typically better.", f"tick labels={labels[:6]}",
                       where=where, kind="SEMI",
                       exception="few discrete totals where amounts are compared")
        # bar of means
        pats = src_has(src, r"sns\.barplot", r"\.mean\(\)[^\n]*\.plot(\.bar)?\(",
                       r"estimator\s*=", r"catplot\([^)]*kind\s*=\s*['\"]bar")
        if pats:
            has_points = bool(scatters) or any(
                ln.get_linestyle() in ("None", "none") for ln in ax.lines)
            report.add("EXP-16", "crit" if not has_points else "major",
                       "Bars appear to encode means of a distribution (MEANBAR-1); the "
                       "distribution is hidden.", f"source matches {pats}; raw points "
                       f"overlaid={has_points}", where=where, kind="SEMI",
                       exception="the bars are counts, sums or proportions")
        if errs or any(len(ln.get_xdata()) == 2 and ln.get_linestyle() not in ("None",)
                       and not ln.get_label().startswith("_child") for ln in ax.lines
                       if ln not in lines):
            alltext = " ".join([ax.get_title(), fig._suptitle.get_text() if fig._suptitle else ""]
                               + [t.get_text() for t in texts]).lower()
            if not any(k in alltext for k in ("ci", "confidence", "sd", "std", "se ",
                                              "error", "iqr", "interval", "±")):
                report.add("DAT-03", "major", "Error bars drawn but their meaning (SD, "
                           "SE, CI) is not stated anywhere (MEANBAR-4).",
                           "errorbar container present; no interval definition text",
                           where=where, kind="SEMI")
        # horizontal rotated labels
        if vertical:
            rots = [t.get_rotation() for t in ax.xaxis.get_majorticklabels()]
            if rots and max(abs(r) for r in rots) >= 30:
                report.add("SCL-12", "minor", "Rotated category labels: use horizontal "
                           "bars instead.", f"rotation={max(rots)}", where=where)
        # stacked bars with many containers
        if len(bars) > 6 and any(p.get_y() != 0 for b in bars for p in b.patches):
            report.add("IDM-STACK", "major", f"{len(bars)} stacked series: only the "
                       "bottom one has a baseline.", "", where=where)

    # ---- pie
    if wedges:
        n = len(wedges)
        if n > 5:
            report.add("IDM-PIE", "crit", f"Pie with {n} slices: angles cannot be "
                       "compared; use a sorted bar chart.", "", where=where)
        spans = [abs(w.theta2 - w.theta1) for w in wedges]
        if spans != sorted(spans, reverse=True) and n > 2:
            report.add("CMP-01", "minor", "Pie slices not ordered large→small.",
                       f"spans={[round(s, 1) for s in spans]}", where=where)
        if wedges and abs(((wedges[0].theta1 % 360) - 90)) > 1:
            report.add("IDM-PIE", "minor", "Pie does not start at 12 o'clock.",
                       f"startangle={wedges[0].theta1:.0f}", where=where)
        if any(abs(w.center[0]) > 1e-9 or abs(w.center[1]) > 1e-9 for w in wedges):
            report.add("IDM-PIE", "major", "Exploded pie: offsets distort area and angle "
                       "reading.", "explode used", where=where)
        if src_has(src, r"shadow\s*=\s*True"):
            report.add("CLT-01", "minor", "Pie shadow: chartjunk.", "shadow=True",
                       where=where)
        if min(spans) / 360 < 0.02:
            report.add("IDM-PIE", "major", "Slices thinner than 2 % are unreadable and "
                       "their labels collide.", f"min span={min(spans):.1f}°", where=where)

    # ---- lines
    if lines:
        n = len(lines)
        if n > 12:
            report.add("EFF-16", "major", f"{n} lines in one panel (spaghetti, more than "
                       "about a dozen): highlight a few against grey or facet.",
                       "", where=where)
        if xcat and n >= 1:
            labels = [t.get_text() for t in ax.xaxis.get_majorticklabels()]
            if not all(re.fullmatch(r"(19|20)?\d{2,4}|[A-Z][a-z]{2}|Q[1-4]|\d+", l.strip() or "x")
                       for l in labels):
                report.add("EXP-03", "crit", "Line over nominal categories implies "
                           "continuity (TRUNC-10).", f"x ticks={labels[:6]}", where=where,
                           exception="ordinal categories with a natural order")
        # flattened by zero
        ys = []
        for ln in lines:
            try:
                ys.extend(float(v) for v in ln.get_ydata(orig=True) if v is not None
                          and not (isinstance(v, float) and math.isnan(v)))
            except Exception:
                pass
        if ys and not bars:
            lo, hi = min(ys), max(ys)
            span = ylim[1] - ylim[0]
            if span > 0 and lo > 0 and ylim[0] <= 0 and (hi - lo) / span < 0.15:
                report.add("SCL-04", "major", "Line chart axis reaches zero while the "
                           "data vary in a narrow band: the trend is flattened "
                           "(TRUNC-5).", f"data {lo:.3g}–{hi:.3g}, ylim={[round(v, 3) for v in ylim]}",
                           where=where, kind="SEMI")
            if span > 0 and ylim[0] > 0 and (hi - lo) / span > 0.6:
                report.add("SCL-02", "minor", "Truncated y axis on a line chart: "
                           "legitimate, but the exaggeration persists; make the "
                           "baseline explicit and justify the range (TRUNC-2/4/7).",
                           f"ylim starts at {ylim[0]:.3g}", where=where, kind="SEMI")
        if n > 1 and ax.get_legend() is None and not texts:
            report.add("TXT-04", "major", f"{n} lines with neither legend nor direct "
                       "labels.", "", where=where)

    # ---- scatter
    for sc in scatters:
        try:
            npts = len(sc.get_offsets())
        except Exception:
            npts = 0
        alpha = sc.get_alpha()
        if npts > 2000 and (alpha is None or alpha >= 0.9):
            report.add("EFF-16", "major", f"{npts} opaque points: overplotting.",
                       f"alpha={alpha}", where=where, kind="SEMI")
        sizes = sc.get_sizes()
        if len(sizes) > 1 and max(sizes) > min(sizes) * 1.5:
            report.add("EFF-02", "minor", "Bubble sizes are read inaccurately; add a "
                       "size legend; check size ∝ area not radius.", "", where=where,
                       kind="SEMI")
        cmap = getattr(sc, "cmap", None)
        if cmap is not None and sc.get_array() is not None and len(sc.get_array()) > 0:
            cls = classify_scheme(cmap.name)
            if cls == "rainbow":
                report.add("COL-02", "crit", "Rainbow colormap.", f"cmap={cmap.name}",
                           where=where)
            if cls == "redgreen":
                report.add("COL-05", "crit", "Red–green colormap.", f"cmap={cmap.name}",
                           where=where)
            if cls == "qualitative":
                report.add("EXP-02", "crit", "Qualitative colormap on a numeric "
                           "array.", f"cmap={cmap.name}", where=where, kind="SEMI",
                           exception="the array holds category codes")
    # axis margins for scatter/line
    if (scatters or lines) and not bars and not xcat:
        for axis_name, lim, getter in (("x", xlim, lambda a: a.get_xdata(orig=True)),
                                       ("y", ylim, lambda a: a.get_ydata(orig=True))):
            vals = []
            for sc in scatters:
                try:
                    off = sc.get_offsets()
                    vals.extend(float(v) for v in (off[:, 0] if axis_name == "x" else off[:, 1]))
                except Exception:
                    pass
            for ln in lines:
                try:
                    vals.extend(float(v) for v in getter(ln))
                except Exception:
                    pass
            vals = [v for v in vals if not math.isnan(v)]
            if vals:
                lo, hi = min(vals), max(vals)
                span = lim[1] - lim[0]
                if span > 0 and (hi - lo) / span < 0.5 and lim[0] <= 0 < lo:
                    report.add("SCL-05", "major", f"{axis_name} axis includes zero far "
                               "from the data: the cloud is compressed (TRUNC-11).",
                               f"data {lo:.3g}–{hi:.3g}, lim={[round(v, 3) for v in lim]}",
                               where=where, kind="SEMI",
                               exception="shared axes across panels")

    # ---- images / heatmaps
    for im in images:
        cmap = im.get_cmap()
        cls = classify_scheme(cmap.name)
        if cls == "rainbow":
            report.add("COL-02", "crit", "Rainbow colormap on a heatmap/image.",
                       f"cmap={cmap.name}", where=where)
        if cls == "redgreen":
            report.add("COL-05", "crit", "Red–green colormap.", f"cmap={cmap.name}",
                       where=where)
        if cls == "qualitative":
            report.add("EXP-02", "crit", "Qualitative colormap for continuous values.",
                       f"cmap={cmap.name}", where=where, kind="SEMI")
        if not any(getattr(c, "ax", None) is not None for c in fig.axes if c is not ax) \
                and not src_has(src, r"colorbar\(", r"cbar"):
            report.add("TXT-03", "major", "Color-encoded values with no colorbar/legend.",
                       f"cmap={cmap.name}", where=where, kind="SEMI")

    # ---- labels and title
    for nm, lab, axis, cat in (("x", ax.get_xlabel(), ax.xaxis, xcat),
                               ("y", ax.get_ylabel(), ax.yaxis, ycat)):
        if wedges:
            break
        if not lab:
            if not cat:
                report.add("SCL-06", "major", f"{nm} axis has no title.", "", where=where)
        elif looks_like_raw_name(lab):
            report.add("SCL-06", "major", f"{nm} axis title is a raw variable name.",
                       f"'{lab}'", where=where)
        elif not cat and not has_units(lab):
            report.add("SCL-06", "minor", f"No units detected in the {nm} axis title.",
                       f"'{lab}'", where=where, kind="SEMI",
                       exception="unitless quantity")
    # legend
    leg = ax.get_legend()
    if leg is not None:
        n = len(leg.get_texts())
        if n > 7:
            report.add("EFF-11", "major", f"Legend with {n} entries exceeds working "
                       "memory and matching ability.", "", where=where)
        if bars and len(bars) == 1 and n >= len(bars[0].patches) > 3:
            report.add("COL-03", "major", "Legend duplicates the category axis.",
                       f"{n} entries", where=where)
    # gridlines
    for axis in (ax.xaxis, ax.yaxis):
        gl = axis.get_gridlines()
        if gl and gl[0].get_visible():
            c = parse_color(matplotlib.colors.to_hex(gl[0].get_color()))
            lw = gl[0].get_linewidth()
            if c and (relative_luminance(c) < 0.5 or lw > 1.2):
                report.add("COL-07", "major", "Gridlines drawn with high salience; "
                           "non-data ink should be light grey.",
                           f"color={to_hex(c)} lw={lw}", where=where)
    # background
    bg = parse_color(matplotlib.colors.to_hex(ax.get_facecolor()))
    if bg and not is_neutral(bg):
        report.add("CLT-01", "minor", "Colored plot background competes with data.",
                   f"facecolor={to_hex(bg)}", where=where)
    if bg and relative_luminance(bg) < 0.35:
        report.add("COL-06", "minor", "Dark background: check contrast of every mark "
                   "and label.", f"facecolor={to_hex(bg)}", where=where, kind="SEMI")
    # inverted axes
    if ax.yaxis_inverted() and not ycat:
        report.add("SCL-07", "minor", "Inverted y axis.", "", where=where, kind="SEMI")
    # font sizes
    fs = []
    for t in list(ax.texts) + ax.xaxis.get_majorticklabels() + ax.yaxis.get_majorticklabels() \
            + [ax.title, ax.xaxis.label, ax.yaxis.label]:
        if t.get_text().strip():
            fs.append(t.get_fontsize())
    if leg is not None:
        fs.extend(t.get_fontsize() for t in leg.get_texts())
    if fs and min(fs) < 8:
        report.add("ACC-05", "major", f"Text at {min(fs)} pt is below legibility "
                   "thresholds.", "", where=where)
    # annotations info
    if annots:
        report.summary.setdefault("annotations", []).extend(
            [a.get_text()[:60] for a in annots])
        for a in annots:
            if re.fullmatch(r"(max|min|peak|maximum|minimum|high|low|increase|decrease)\.?",
                            a.get_text().strip(), flags=re.I):
                report.add("TXT-06", "minor", "Annotation restates the obvious without a "
                           "value, date or reason (TEXT-4).", f"'{a.get_text()}'",
                           where=where, kind="SEMI")
    # palette CVD
    cols = [c for c in artist_colors(ax) if not is_neutral(c)]
    if len(cols) >= 2:
        pr = palette_report(cols[:16])
        report.summary.setdefault("palettes", []).append({"where": where, **pr})
        if pr["has_red_and_green"]:
            report.add("COL-05", "major", "Red and green both used for data marks.",
                       f"colors={pr['hex'][:10]}", where=where, kind="SEMI",
                       exception="also separated by position/shape/labels")
        for p in pr["confusable_deuteranopia"][:4]:
            report.add("COL-05", "major", "Two mark colors merge under deuteranopia.",
                       f"{p['a']} vs {p['b']} ΔE sim={p['dE_simulated']}", where=where)
        if len(cols) > 8 and not images:
            report.add("COL-04", "major", f"{len(cols)} distinct chromatic colors on data "
                       "marks.", "", where=where, kind="SEMI")
        if bg:
            low = [to_hex(c) for c in cols if contrast_ratio(c, bg) < 3.0]
            if low:
                report.add("COL-06", "major", "Mark colors below 3:1 contrast against the "
                           "plot background.", f"{low}", where=where)
    report.summary.setdefault("axes", []).append(summ)


def check_figure(fig, report, src, out_dir):
    where = f"fig{fig.number}"
    w, h = fig.get_size_inches()
    report.summary.setdefault("figures", []).append(
        {"where": where, "size_in": [round(w, 2), round(h, 2)], "dpi": fig.dpi,
         "n_axes": len(fig.axes)})
    twins = twin_axes(fig)
    twin_secondaries = {id(b) for a, b in twins}
    for a, b in twins:
        report.add("EXP-11", "crit", "Twin axes (dual y or x): arbitrary alignment makes "
                   "crossings and relative heights meaningless.",
                   f"{where}: axes share position; labels '{a.get_ylabel()}' / "
                   f"'{b.get_ylabel()}'", where=where,
                   exception="if kept: color-match axes, honest ranges, different marks")
    has_title = bool(fig._suptitle and fig._suptitle.get_text().strip()) or \
        any(a.get_title().strip() for a in fig.axes)
    if not has_title:
        report.add("TXT-01", "major", "No title anywhere in the figure (TEXT-1).", "",
                   where=where, kind="SEMI",
                   exception="an external caption does the title's job")
    for i, ax in enumerate(fig.axes):
        if ax.get_label() == "<colorbar>" or "colorbar" in str(type(ax)).lower():
            continue
        try:
            check_axes(ax, fig, report, src, i)
        except Exception as e:
            report.warn(f"{where}.ax{i}: check failed: {type(e).__name__}: {e}")
    # facets: shared scales?
    data_axes = [a for a in fig.axes if a.get_label() != "<colorbar>"
                 and id(a) not in twin_secondaries]
    if len(data_axes) > 1:
        ylims = {tuple(round(v, 6) for v in a.get_ylim()) for a in data_axes}
        if len(ylims) > 1 and all(not is_categorical_axis(a.yaxis) for a in data_axes):
            report.add("SCL-08", "major", "Several panels with different y ranges: "
                       "panels cannot be compared visually.", f"{len(ylims)} distinct ylims",
                       where=where, kind="SEMI",
                       exception="dual axes already flagged, or panels show unrelated "
                                 "quantities")
    png = os.path.join(out_dir, f"{where}.png")
    try:
        fig.savefig(png, dpi=150)
        report.artifacts.append(png)
    except Exception as e:
        report.warn(f"could not save {where}: {e}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("script")
    ap.add_argument("--out-dir", default=None)
    args = ap.parse_args()
    out_dir = args.out_dir or tempfile.mkdtemp(prefix="vischeck_mpl_")
    os.makedirs(out_dir, exist_ok=True)
    report = Report(args.script, "matplotlib")
    figs, src = run_script(args.script, report)
    if not figs:
        report.warn("No figures were created by the script.")
    for fig in figs:
        try:
            check_figure(fig, report, src, out_dir)
        except Exception as e:
            report.warn(f"figure check failed: {type(e).__name__}: {e}")
    # source-level hints
    if src_has(src, r"twinx\(|twiny\(") and not any(
            f.rule == "EXP-11" for f in report.findings):
        report.add("EXP-11", "crit", "twinx/twiny used (dual axes).", "source", where="source")
    # distribution plots: random jitter, undefined whiskers, default bins / bandwidth
    seeded = src_has(src, r"random\.seed\(", r"default_rng\(\s*\d", r"RandomState\(\s*\d",
                     r"random_state\s*=\s*\d")
    strip = [m for m in re.findall(r"stripplot\([^)]*\)", src, flags=re.S)
             if not re.search(r"jitter\s*=\s*(False|0\b)", m)]
    manual = src_has(src, r"jitter\w*\s*=\s*[^\n]*(random|rng)\.", r"\+\s*(np\.)?random\.\w+\(",
                     r"\+\s*rng\.(uniform|normal)\(")
    if strip or manual:
        report.add("EXP-21", "minor" if seeded else "major",
                   "Points are spread with random jitter"
                   + (" (seeded: say so in the caption)" if seeded else
                      ": the picture changes on every run and shows structure that is "
                      "not in the data (RAIN-2). Seed it, or use a swarm / strip at the "
                      "true positions"),
                   "seaborn stripplot jitters by default" if strip else f"source matches {manual}",
                   where="source", kind="SEMI",
                   exception="seeded, disclosed jitter with a density layer")
    if src_has(src, r"\.boxplot\(", r"\bboxplot\(") and not src_has(src, r"whis\s*="):
        report.add("DAT-10", "minor", "Box plot with the default whisker rule (1.5 × IQR): "
                   "say in the chart what the whiskers mean (RAIN-6).", "no `whis=` in source",
                   where="source", kind="SEMI", exception="the caption defines the whiskers")
    if src_has(src, r"(kdeplot|violinplot)\(") and not src_has(src, r"bw_(adjust|method)\s*=", r"\bbw\s*="):
        report.add("EXP-15", "minor", "Density / violin with the default bandwidth: it can "
                   "merge or invent modes; choose it and state it (RAIN-4).",
                   "no bw_adjust / bw_method in source", where="source", kind="SEMI")
    if src_has(src, r"\.hist\(", r"histplot\(") and not src_has(src, r"\bbins\s*=", r"binwidth\s*="):
        report.add("EXP-15", "minor", "Histogram with the default bin count: the bin width "
                   "shapes the distribution; choose it and try another (RAIN-4).",
                   "no bins= / binwidth= in source", where="source", kind="SEMI")
    hints = src_has(src, r"projection\s*=\s*['\"]3d['\"]", r"\.pie\(", r"cmap\s*=\s*['\"](jet|rainbow|hsv|turbo|gist_rainbow|nipy_spectral)",
                    r"ylim\(\s*[1-9]", r"set_ylim\(\s*[1-9]")
    if hints:
        report.summary["source_hints"] = hints
    report.dump()


if __name__ == "__main__":
    main()
