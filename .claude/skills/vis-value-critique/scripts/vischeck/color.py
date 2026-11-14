"""Color maths: parsing, luminance, WCAG contrast, Lab distance, CVD simulation.

CVD simulation uses the Machado, Oliveira & Fernandes (2009) matrices at full
severity, applied in linear RGB. Distances are CIE76 Delta-E in CIELAB (D65).
"""
from __future__ import annotations

import colorsys
import math
import re

try:
    import numpy as np
except Exception:  # numpy is optional for the scalar helpers
    np = None

# ----------------------------------------------------------------------------
# parsing

CSS_NAMED = {
    "black": "#000000", "white": "#ffffff", "red": "#ff0000", "green": "#008000",
    "lime": "#00ff00", "blue": "#0000ff", "yellow": "#ffff00", "cyan": "#00ffff",
    "magenta": "#ff00ff", "gray": "#808080", "grey": "#808080", "orange": "#ffa500",
    "purple": "#800080", "brown": "#a52a2a", "pink": "#ffc0cb", "navy": "#000080",
    "teal": "#008080", "olive": "#808000", "maroon": "#800000", "silver": "#c0c0c0",
    "gold": "#ffd700", "crimson": "#dc143c", "steelblue": "#4682b4",
    "darkblue": "#00008b", "darkgreen": "#006400", "darkred": "#8b0000",
    "lightblue": "#add8e6", "lightgreen": "#90ee90", "lightgray": "#d3d3d3",
    "lightgrey": "#d3d3d3", "darkgray": "#a9a9a9", "darkgrey": "#a9a9a9",
    "salmon": "#fa8072", "tomato": "#ff6347", "coral": "#ff7f50", "indigo": "#4b0082",
    "violet": "#ee82ee", "turquoise": "#40e0d0", "tan": "#d2b48c", "khaki": "#f0e68c",
    "firebrick": "#b22222", "forestgreen": "#228b22", "seagreen": "#2e8b57",
    "royalblue": "#4169e1", "dodgerblue": "#1e90ff", "skyblue": "#87ceeb",
    "orchid": "#da70d6", "plum": "#dda0dd", "chocolate": "#d2691e",
    "darkorange": "#ff8c00", "goldenrod": "#daa520", "slategray": "#708090",
    "slategrey": "#708090", "dimgray": "#696969", "dimgrey": "#696969",
    "whitesmoke": "#f5f5f5", "gainsboro": "#dcdcdc", "lavender": "#e6e6fa",
    "beige": "#f5f5dc", "ivory": "#fffff0", "aqua": "#00ffff", "fuchsia": "#ff00ff",
    "darkviolet": "#9400d3", "mediumseagreen": "#3cb371", "limegreen": "#32cd32",
    "yellowgreen": "#9acd32", "greenyellow": "#adff2f", "springgreen": "#00ff7f",
    "deepskyblue": "#00bfff", "cornflowerblue": "#6495ed", "midnightblue": "#191970",
    "hotpink": "#ff69b4", "deeppink": "#ff1493", "palevioletred": "#db7093",
    "sienna": "#a0522d", "peru": "#cd853f", "wheat": "#f5deb3", "linen": "#faf0e6",
}

# matplotlib single-letter and tableau names
MPL_NAMED = {
    "b": "#0000ff", "g": "#008000", "r": "#ff0000", "c": "#00bfbf", "m": "#bf00bf",
    "y": "#bfbf00", "k": "#000000", "w": "#ffffff",
    "tab:blue": "#1f77b4", "tab:orange": "#ff7f0e", "tab:green": "#2ca02c",
    "tab:red": "#d62728", "tab:purple": "#9467bd", "tab:brown": "#8c564b",
    "tab:pink": "#e377c2", "tab:gray": "#7f7f7f", "tab:grey": "#7f7f7f",
    "tab:olive": "#bcbd22", "tab:cyan": "#17becf",
    "C0": "#1f77b4", "C1": "#ff7f0e", "C2": "#2ca02c", "C3": "#d62728",
    "C4": "#9467bd", "C5": "#8c564b", "C6": "#e377c2", "C7": "#7f7f7f",
    "C8": "#bcbd22", "C9": "#17becf",
}


def parse_color(c) -> tuple[float, float, float] | None:
    """Return (r, g, b) in 0..1 or None if unparseable."""
    if c is None:
        return None
    if isinstance(c, (tuple, list)):
        if len(c) >= 3 and all(isinstance(v, (int, float)) for v in c[:3]):
            vals = c[:3]
            if max(vals) > 1.0:
                vals = [v / 255 for v in vals]
            return tuple(float(v) for v in vals)
        return None
    s = str(c).strip()
    if s.lower() in CSS_NAMED:
        s = CSS_NAMED[s.lower()]
    elif s in MPL_NAMED:
        s = MPL_NAMED[s]
    m = re.fullmatch(r"#?([0-9a-fA-F]{6})([0-9a-fA-F]{2})?", s)
    if m:
        h = m.group(1)
        return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    m = re.fullmatch(r"#?([0-9a-fA-F]{3})", s)
    if m:
        h = m.group(1)
        return tuple(int(ch * 2, 16) / 255 for ch in h)
    m = re.fullmatch(r"rgba?\(([^)]+)\)", s, flags=re.I)
    if m:
        parts = [p.strip() for p in m.group(1).split(",")]
        try:
            vals = [float(p.rstrip("%")) for p in parts[:3]]
        except ValueError:
            return None
        if max(vals) > 1.0:
            vals = [v / 255 for v in vals]
        return tuple(vals)
    return None


def to_hex(rgb) -> str:
    r, g, b = (max(0, min(1, v)) for v in rgb)
    return "#%02x%02x%02x" % (round(r * 255), round(g * 255), round(b * 255))


# ----------------------------------------------------------------------------
# luminance and contrast (WCAG 2.1)

def _lin(v: float) -> float:
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def _delin(v: float) -> float:
    v = max(0.0, min(1.0, v))
    return 12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055


def relative_luminance(rgb) -> float:
    r, g, b = (_lin(v) for v in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(rgb1, rgb2) -> float:
    l1, l2 = relative_luminance(rgb1), relative_luminance(rgb2)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


# ----------------------------------------------------------------------------
# CIELAB

def rgb_to_lab(rgb) -> tuple[float, float, float]:
    r, g, b = (_lin(v) for v in rgb)
    x = (0.4124564 * r + 0.3575761 * g + 0.1804375 * b) / 0.95047
    y = (0.2126729 * r + 0.7151522 * g + 0.0721750 * b) / 1.00000
    z = (0.0193339 * r + 0.1191920 * g + 0.9503041 * b) / 1.08883

    def f(t):
        return t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116

    fx, fy, fz = f(x), f(y), f(z)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def delta_e(rgb1, rgb2) -> float:
    a, b = rgb_to_lab(rgb1), rgb_to_lab(rgb2)
    return math.sqrt(sum((p - q) ** 2 for p, q in zip(a, b)))


# ----------------------------------------------------------------------------
# color vision deficiency simulation (Machado et al. 2009, severity 1.0)

CVD_MATRICES = {
    "protanopia": [[0.152286, 1.052583, -0.204868],
                   [0.114503, 0.786281, 0.099216],
                   [-0.003882, -0.048116, 1.051998]],
    "deuteranopia": [[0.367322, 0.860646, -0.227968],
                     [0.280085, 0.672501, 0.047413],
                     [-0.011820, 0.042940, 0.968881]],
    "tritanopia": [[1.255528, -0.076749, -0.178779],
                   [-0.078411, 0.930809, 0.147602],
                   [0.004733, 0.691367, 0.303900]],
}


def simulate_cvd(rgb, kind="deuteranopia"):
    m = CVD_MATRICES[kind]
    lin = [_lin(v) for v in rgb]
    out = [sum(m[i][j] * lin[j] for j in range(3)) for i in range(3)]
    return tuple(_delin(v) for v in out)


def simulate_cvd_image(arr, kind="deuteranopia"):
    """arr: numpy uint8 HxWx3. Returns uint8 HxWx3."""
    if np is None:
        raise RuntimeError("numpy required")
    x = arr.astype(np.float64) / 255.0
    lin = np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)
    m = np.array(CVD_MATRICES[kind])
    sim = lin @ m.T
    sim = np.clip(sim, 0, 1)
    srgb = np.where(sim <= 0.0031308, 12.92 * sim, 1.055 * sim ** (1 / 2.4) - 0.055)
    return (np.clip(srgb, 0, 1) * 255).round().astype(np.uint8)


def grayscale_image(arr):
    if np is None:
        raise RuntimeError("numpy required")
    x = arr.astype(np.float64) / 255.0
    lin = np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)
    y = 0.2126 * lin[..., 0] + 0.7152 * lin[..., 1] + 0.0722 * lin[..., 2]
    srgb = np.where(y <= 0.0031308, 12.92 * y, 1.055 * y ** (1 / 2.4) - 0.055)
    g = (np.clip(srgb, 0, 1) * 255).round().astype(np.uint8)
    return np.stack([g, g, g], axis=-1)


# ----------------------------------------------------------------------------
# hue classification

def hue_deg(rgb) -> float:
    h, s, v = colorsys.rgb_to_hsv(*rgb)
    return h * 360


def saturation(rgb) -> float:
    return colorsys.rgb_to_hsv(*rgb)[1]


def value(rgb) -> float:
    return colorsys.rgb_to_hsv(*rgb)[2]


def is_reddish(rgb) -> bool:
    h, s, v = colorsys.rgb_to_hsv(*rgb)
    hd = h * 360
    return s > 0.35 and v > 0.25 and (hd <= 22 or hd >= 335)


def is_greenish(rgb) -> bool:
    h, s, v = colorsys.rgb_to_hsv(*rgb)
    hd = h * 360
    return s > 0.3 and v > 0.2 and 75 <= hd <= 165


def is_neutral(rgb, s_thresh=0.12) -> bool:
    return saturation(rgb) < s_thresh


# ----------------------------------------------------------------------------
# palette analysis

def cvd_confusable_pairs(colors, kind="deuteranopia", threshold=20.0):
    """Pairs of colors whose Delta-E after simulation falls below threshold.

    threshold 20 ~ hard to tell apart on small marks; 12 ~ practically identical.
    Returns list of (i, j, dE_original, dE_simulated).
    """
    out = []
    sims = [simulate_cvd(c, kind) for c in colors]
    for i in range(len(colors)):
        for j in range(i + 1, len(colors)):
            d0 = delta_e(colors[i], colors[j])
            d1 = delta_e(sims[i], sims[j])
            if d1 < threshold:
                out.append((i, j, round(d0, 1), round(d1, 1)))
    return out


def palette_report(colors):
    """Summarize a categorical palette: red-green risk, CVD confusions, low-contrast
    pairs. colors: list of (r,g,b)."""
    rep = {"n": len(colors), "hex": [to_hex(c) for c in colors]}
    rep["has_red_and_green"] = any(is_reddish(c) for c in colors) and \
        any(is_greenish(c) for c in colors)
    for kind in ("deuteranopia", "protanopia", "tritanopia"):
        pairs = cvd_confusable_pairs(colors, kind)
        rep[f"confusable_{kind}"] = [
            {"a": to_hex(colors[i]), "b": to_hex(colors[j]), "dE_normal": d0,
             "dE_simulated": d1} for i, j, d0, d1 in pairs]
    # pairs that are already close for normal vision
    close = []
    for i in range(len(colors)):
        for j in range(i + 1, len(colors)):
            d = delta_e(colors[i], colors[j])
            if d < 15:
                close.append({"a": to_hex(colors[i]), "b": to_hex(colors[j]),
                              "dE": round(d, 1)})
    rep["close_for_normal_vision"] = close
    # contrast vs white background
    rep["low_contrast_on_white"] = [
        to_hex(c) for c in colors if contrast_ratio(c, (1, 1, 1)) < 3.0]
    return rep
