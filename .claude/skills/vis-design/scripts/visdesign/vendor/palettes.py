"""Named color schemes and their classification.

classify_scheme(name) -> one of "qualitative", "sequential", "diverging", "rainbow",
"redgreen", "unknown". scheme_colors(name) -> list of hex for the common qualitative
schemes (used for CVD checks when the spec names a scheme instead of listing colors).
"""
from __future__ import annotations

QUALITATIVE_COLORS = {
    # Vega / d3 / matplotlib share most of these (ColorBrewer and Tableau)
    "category10": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b",
                   "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"],
    "tableau10": ["#4c78a8", "#f58518", "#e45756", "#72b7b2", "#54a24b", "#eeca3b",
                  "#b279a2", "#ff9da6", "#9d755d", "#bab0ac"],
    "set1": ["#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "#ff7f00", "#ffff33",
             "#a65628", "#f781bf", "#999999"],
    "set2": ["#66c2a5", "#fc8d62", "#8da0cb", "#e78ac3", "#a6d854", "#ffd92f",
             "#e5c494", "#b3b3b3"],
    "set3": ["#8dd3c7", "#ffffb3", "#bebada", "#fb8072", "#80b1d3", "#fdb462",
             "#b3de69", "#fccde5", "#d9d9d9", "#bc80bd", "#ccebc5", "#ffed6f"],
    "dark2": ["#1b9e77", "#d95f02", "#7570b3", "#e7298a", "#66a61e", "#e6ab02",
              "#a6761d", "#666666"],
    "paired": ["#a6cee3", "#1f78b4", "#b2df8a", "#33a02c", "#fb9a99", "#e31a1c",
               "#fdbf6f", "#ff7f00", "#cab2d6", "#6a3d9a", "#ffff99", "#b15928"],
    "accent": ["#7fc97f", "#beaed4", "#fdc086", "#ffff99", "#386cb0", "#f0027f",
               "#bf5b17", "#666666"],
    "pastel1": ["#fbb4ae", "#b3cde3", "#ccebc5", "#decbe4", "#fed9a6", "#ffffcc",
                "#e5d8bd", "#fddaec", "#f2f2f2"],
    "pastel2": ["#b3e2cd", "#fdcdac", "#cbd5e8", "#f4cae4", "#e6f5c9", "#fff2ae",
                "#f1e2cc", "#cccccc"],
    "okabe-ito": ["#e69f00", "#56b4e9", "#009e73", "#f0e442", "#0072b2", "#d55e00",
                  "#cc79a7", "#000000"],
    # Plotly defaults
    "plotly": ["#636efa", "#ef553b", "#00cc96", "#ab63fa", "#ffa15a", "#19d3f3",
               "#ff6692", "#b6e880", "#ff97ff", "#fecb52"],
}
QUALITATIVE_COLORS["tab10"] = QUALITATIVE_COLORS["category10"]
QUALITATIVE_COLORS["d3"] = QUALITATIVE_COLORS["category10"]

QUALITATIVE_NAMES = set(QUALITATIVE_COLORS) | {
    "category20", "category20b", "category20c", "tableau20", "observable10",
    "tab20", "tab20b", "tab20c", "g10", "t10", "alphabet", "dark24", "light24",
    "antique", "bold", "pastel", "prism", "safe", "vivid",
}

SEQUENTIAL_NAMES = {
    # vega
    "blues", "greens", "greys", "oranges", "purples", "reds", "browns", "tealblues",
    "teals", "warmgreys", "bluegreen", "bluepurple", "greenblue", "orangered",
    "purplered", "purpleblue", "purplebluegreen", "redpurple", "yellowgreen",
    "yellowgreenblue", "yelloworangebrown", "yelloworangered", "goldgreen",
    "goldorange", "goldred", "lightgreyred", "lightgreyteal", "lightmulti",
    "lightorange", "lighttealblue", "darkblue", "darkgold", "darkgreen", "darkmulti",
    "darkred", "viridis", "magma", "inferno", "plasma", "cividis", "rocket", "mako",
    "flare", "crest",
    # matplotlib / plotly
    "ylgn", "ylgnbu", "ylorbr", "ylorrd", "bugn", "bupu", "gnbu", "orrd", "pubu",
    "pubugn", "purd", "rdpu", "copper", "bone", "gray", "grey", "binary", "gist_gray",
    "gist_yarg", "hot", "afmhot", "gist_heat", "wistia", "summer", "autumn", "winter",
    "spring", "cool", "pink", "sunset", "sunsetdark", "agsunset", "aggrnyl", "agsunset",
    "blackbody", "bluered", "electric", "emrld", "mint", "peach", "pinkyl", "purp",
    "purpor", "redor", "teal", "tealgrn", "darkmint", "brwnyl", "burg", "burgyl",
    "oryel", "magenta", "ice", "thermal", "solar", "haline", "matter", "speed", "amp",
    "tempo", "dense", "algae", "deep", "turbid",
}

DIVERGING_NAMES = {
    "blueorange", "brownbluegreen", "purplegreen", "pinkyellowgreen", "purpleorange",
    "redblue", "redgrey", "redyellowblue", "redyellowgreen", "spectral",
    "rdbu", "rdylbu", "rdylgn", "piyg", "prgn", "brbg", "puor", "rdgy", "coolwarm",
    "bwr", "seismic", "vlag", "icefire", "armyrose", "fall", "geyser", "temps",
    "tealrose", "tropic", "earth", "balance", "delta", "curl", "oxy", "picnic",
    "portland", "berlin", "managua", "vanimo",
}

RAINBOW_NAMES = {"rainbow", "sinebow", "jet", "hsv", "turbo", "gist_rainbow",
                 "nipy_spectral", "gist_ncar", "spectral", "cubehelix", "twilight",
                 "twilight_shifted", "phase", "edge", "hsv", "mrybm", "mygbm",
                 "gist_stern", "brg", "cmrmap", "prism", "flag", "ocean", "terrain",
                 "gist_earth", "gnuplot", "gnuplot2", "cmrmap"}

REDGREEN_NAMES = {"redyellowgreen", "rdylgn", "piyg", "prgn", "pinkyellowgreen",
                  "purplegreen", "redgreen", "rdgn", "greenred", "traffic"}


def _norm(name) -> str:
    return str(name).lower().replace("_r", "").replace("-", "").replace(" ", "")


def classify_scheme(name) -> str:
    if name is None:
        return "unknown"
    n = _norm(name)
    if n in REDGREEN_NAMES:
        return "redgreen"
    if n in RAINBOW_NAMES:
        return "rainbow"
    if n in QUALITATIVE_NAMES:
        return "qualitative"
    if n in SEQUENTIAL_NAMES:
        return "sequential"
    if n in DIVERGING_NAMES:
        return "diverging"
    # heuristics on name
    for key in ("category", "tableau", "set", "pastel", "dark2", "accent", "paired"):
        if n.startswith(key):
            return "qualitative"
    return "unknown"


def scheme_colors(name):
    n = _norm(name)
    return QUALITATIVE_COLORS.get(n)
