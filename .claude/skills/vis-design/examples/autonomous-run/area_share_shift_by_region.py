"""Reparto de la superficie (AREA_HA) entre regiones: inicio (2015-2017) vs final (2022-2024)

Decision record: p-rank-change-two-points--area-share-shift-by-region-20261107 (status candidate, assumed)  ·  Design document: out/area_share_shift_by_region_design.md
Library: matplotlib  ·  Generated: 2026-11-07 (autonomous run; assumptions in the design document)
Question: ¿Ha cambiado el reparto de la superficie (AREA_HA) entre regiones entre el inicio
y el final del periodo de events.csv?
"""
from __future__ import annotations

import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
import pandas as pd  # noqa: E402

# ---------------------------------------------------------------- CONFIG
DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "events.csv")  # relative to this script
OUT_DIR = "out"
SLUG = "area_share_shift_by_region"
LANG = "es"
COLUMNS = {"date": "EVENT_DATE", "region": "REGION", "measure": "AREA_HA"}
PARSE = {"sep": ",", "decimal": ".", "encoding": "utf-8",
         "code_columns": ["REGION_CODE"], "dates": {"EVENT_DATE": "%d/%m/%Y"},
         "numeric": ["AREA_HA"], "sentinels": None}
# Period definition (assumption S2.derive): first three and last three calendar years of the data.
PERIOD_YEARS = 3
PERIOD_LABELS = {"inicio": None, "final": None}  # filled by derive() from the data
HIGHLIGHT_PP = 2.0  # |delta| in percentage points from which a region gets the accent colour

# ---------------------------------------------------------------- PALETTE
OKABE_ITO = ["#e69f00", "#56b4e9", "#009e73", "#f0e442", "#0072b2", "#d55e00", "#cc79a7", "#000000"]
NEUTRAL, ACCENT = "#8c8c8c", "#0072b2"   # neutral grey; accent blue = gain
ACCENT_LOSS = "#d55e00"                  # Okabe-Ito vermillion = loss (blue/vermillion is deuteranopia-safe)
START_DOT, END_DOT = "#bdbdbd", "#4d4d4d"  # first period light, last period dark (luminance = order)
TEXT = "#222222"
GRID = "#dddddd"


def load(path: str) -> pd.DataFrame:
    dtype = {c: str for c in PARSE.get("code_columns", [])}
    df = pd.read_csv(path, sep=PARSE.get("sep", ","), decimal=PARSE.get("decimal", "."),
                     dtype=dtype, encoding=PARSE.get("encoding", "utf-8"))
    for col, fmt in PARSE.get("dates", {}).items():
        df[col] = pd.to_datetime(df[col], format=fmt, errors="coerce")
    for col in PARSE.get("numeric", []):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    if PARSE.get("sentinels"):
        df = df.replace(PARSE["sentinels"], pd.NA)
    needed = [c for c in COLUMNS.values() if c]
    missing = [c for c in needed if c not in df.columns]
    assert not missing, f"missing columns: {missing}"
    assert len(df) > 0, "empty dataset"
    bad = df[COLUMNS["date"]].isna().sum() + df[COLUMNS["measure"]].isna().sum()
    if bad:
        print(f"dropping {bad} rows with unparseable date or area")
        df = df.dropna(subset=[COLUMNS["date"], COLUMNS["measure"]])
    print(f"loaded {len(df)} rows from {path}")
    return df


def derive(df: pd.DataFrame) -> pd.DataFrame:
    """Derived data exactly as in the design document, section 2.

    period      = 'inicio' for the first PERIOD_YEARS calendar years, 'final' for the last ones
    area_period = sum(AREA_HA) per (period, REGION)
    share_pct   = 100 * area_period / sum(AREA_HA) per period
    delta_pp    = share_pct(final) - share_pct(inicio)
    n_events    = events per (period, REGION)
    Regions absent from a period get share 0 (and n 0) so that both periods sum to 100 %.
    """
    year = df[COLUMNS["date"]].dt.year
    y_min, y_max = int(year.min()), int(year.max())
    first = list(range(y_min, y_min + PERIOD_YEARS))
    last = list(range(y_max - PERIOD_YEARS + 1, y_max + 1))
    assert first[-1] < last[0], "the two periods overlap: reduce PERIOD_YEARS"
    PERIOD_LABELS["inicio"] = f"{first[0]}-{first[-1]}"
    PERIOD_LABELS["final"] = f"{last[0]}-{last[-1]}"
    period = pd.Series(pd.NA, index=df.index, dtype="object")
    period[year.isin(first)] = "inicio"
    period[year.isin(last)] = "final"
    sub = df.assign(period=period).dropna(subset=["period"])
    print(f"rows in the two periods: {len(sub)} of {len(df)} "
          f"({PERIOD_LABELS['inicio']}: {(sub.period == 'inicio').sum()}, "
          f"{PERIOD_LABELS['final']}: {(sub.period == 'final').sum()})")

    g = (sub.groupby(["period", COLUMNS["region"]])[COLUMNS["measure"]]
            .agg(area_period="sum", n_events="size").reset_index())
    g["share_pct"] = 100 * g["area_period"] / g.groupby("period")["area_period"].transform("sum")
    wide = g.pivot(index=COLUMNS["region"], columns="period",
                   values=["share_pct", "n_events", "area_period"]).fillna(0)
    out = pd.DataFrame({
        "region": wide.index,
        "share_inicio": wide[("share_pct", "inicio")].values,
        "share_final": wide[("share_pct", "final")].values,
        "n_inicio": wide[("n_events", "inicio")].astype(int).values,
        "n_final": wide[("n_events", "final")].astype(int).values,
        "area_inicio": wide[("area_period", "inicio")].values,
        "area_final": wide[("area_period", "final")].values,
    })
    out["delta_pp"] = out["share_final"] - out["share_inicio"]
    out = out.sort_values("delta_pp", ascending=False).reset_index(drop=True)
    # bookkeeping for the title and footer (period totals, events) kept as attrs, not columns
    out.attrs["total_rows"] = len(df)
    out.attrs["total_area"] = {p: float(sub.loc[sub.period == p, COLUMNS["measure"]].sum()) for p in ("inicio", "final")}
    out.attrs["n_events"] = {p: int((sub.period == p).sum()) for p in ("inicio", "final")}
    out.attrs["years"] = {"inicio": first, "final": last, "excluded": [y for y in range(y_min, y_max + 1) if y not in first + last]}
    print(f"rows after derivation: {len(out)} regions")
    return out


def _fmt(x: float, nd: int = 1) -> str:
    return f"{x:.{nd}f}".replace(".", ",")


def top10_share(df: pd.DataFrame, col: str) -> float:
    return float(df[col].sort_values(ascending=False).head(10).sum())


def takeaway(df: pd.DataFrame) -> str:
    """Title computed from the data (never a literal number)."""
    t0, t1 = top10_share(df, "share_inicio"), top10_share(df, "share_final")
    gain = df.iloc[0]
    loss = df.iloc[-1]
    n_big = int((df["delta_pp"].abs() >= HIGHLIGHT_PP).sum())
    conc = ("se mantiene" if abs(t1 - t0) < 2.5 else ("aumenta" if t1 > t0 else "disminuye"))
    line1 = (f"El reparto global de la superficie {conc}: las 10 regiones con más superficie "
             f"pasan del {_fmt(t0, 0)} % al {_fmt(t1, 0)} % del total")
    line2 = (f"pero {n_big} de {len(df)} regiones cambian ≥ {_fmt(HIGHLIGHT_PP, 0)} puntos: "
             f"{gain['region']} gana más (+{_fmt(gain['delta_pp'])} pp) y {loss['region']} pierde más (−{_fmt(abs(loss['delta_pp']))} pp)")
    return line1 + "\n" + line2


def style(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(labelsize=10)


def build_chart(df: pd.DataFrame):
    """Encodings as in the design document, section 3. Returns the Figure."""
    n = len(df)
    fig, ax = plt.subplots(figsize=(10, 0.28 * n + 3.2))
    y = list(range(n))[::-1]  # first row (largest gain) on top
    big = df["delta_pp"].abs() >= HIGHLIGHT_PP
    seg_color = [ (ACCENT if d > 0 else ACCENT_LOSS) if b else NEUTRAL for d, b in zip(df["delta_pp"], big) ]

    # connection: one segment per region, length = |delta_pp|
    ax.hlines(y, df["share_inicio"], df["share_final"], color=seg_color, linewidth=[2.6 if b else 1.6 for b in big], zorder=1)
    # first period: open circle, light; last period: filled circle, dark
    ax.scatter(df["share_inicio"], y, s=46, facecolor="white", edgecolor=START_DOT, linewidth=1.8, zorder=2)
    ax.scatter(df["share_final"], y, s=46, facecolor=[c if b else END_DOT for c, b in zip(seg_color, big)],
               edgecolor="none", zorder=3)
    # delta label at the row end (right of the larger value)
    xmax = float(max(df["share_inicio"].max(), df["share_final"].max()))
    for yi, (d, b, s0, s1) in enumerate(zip(df["delta_pp"], big, df["share_inicio"], df["share_final"])):
        ax.text(max(s0, s1) + 0.15, y[yi], f"{'+' if d >= 0 else '−'}{_fmt(abs(d))} pp",
                va="center", ha="left", fontsize=9, color=(seg_color[yi] if b else "#666666"),
                fontweight="bold" if b else "normal")

    ax.set_yticks(y)
    ax.set_yticklabels(df["region"], fontsize=10)
    for lab, b in zip(ax.get_yticklabels(), big):
        if b:
            lab.set_fontweight("bold")
    ax.set_xlim(0, xmax + 1.6)
    ax.set_ylim(-0.8, n - 0.2)
    ax.set_xlabel("Cuota de la superficie del periodo (% de la suma de AREA_HA del periodo)", fontsize=10)
    ax.set_ylabel("Región (ordenadas por cambio de cuota, pp)", fontsize=10)
    ax.xaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(axis="y", length=0)
    style(ax)
    ax.spines["left"].set_color(GRID)

    # period cue drawn once, as direct labels, instead of a legend
    p0, p1 = PERIOD_LABELS["inicio"], PERIOD_LABELS["final"]
    handles = [Line2D([0], [0], marker="o", color="white", markerfacecolor="white", markeredgecolor=START_DOT,
                      markeredgewidth=1.8, markersize=7, label=f"{p0} (inicio)"),
               Line2D([0], [0], marker="o", color="white", markerfacecolor=END_DOT, markersize=7, label=f"{p1} (final)"),
               Line2D([0], [0], color=ACCENT, linewidth=2.6, label=f"gana ≥ {_fmt(HIGHLIGHT_PP, 0)} pp"),
               Line2D([0], [0], color=ACCENT_LOSS, linewidth=2.6, label=f"pierde ≥ {_fmt(HIGHLIGHT_PP, 0)} pp")]
    ax.legend(handles=handles, loc="lower right", frameon=False, fontsize=9, title="Lectura de cada fila", title_fontsize=9)

    title = takeaway(df)
    ne = df.attrs["n_events"]
    ta = df.attrs["total_area"]
    excluded = df.attrs["years"]["excluded"]
    subtitle = (f"Cuota de cada región en la suma de AREA_HA de cada periodo. Inicio = {p0} "
                f"({ne['inicio']} eventos, {_fmt(ta['inicio'], 0)} ha); final = {p1} ({ne['final']} eventos, {_fmt(ta['final'], 0)} ha); "
                f"años {excluded[0]}-{excluded[-1]} no incluidos.\n"
                f"Filas ordenadas por el cambio en puntos porcentuales (pp); la cifra de cada fila es final − inicio.")
    fig.suptitle(title, x=0.01, y=0.985, ha="left", fontsize=13, fontweight="bold", color=TEXT)
    ax.set_title(subtitle, loc="left", fontsize=9.5, color="#444444", pad=10)

    med0 = int(df["n_inicio"].median()); med1 = int(df["n_final"].median())
    fig.text(0.01, 0.005,
             f"Fuente: events.csv (n = {df.attrs['total_rows']} eventos, {len(df)} regiones). "
             f"Mediana de eventos por región: {med0} en {p0}, {med1} en {p1}; con tan pocos eventos, "
             f"cambios pequeños pueden ser ruido muestral.",
             fontsize=8.5, color="#555555", ha="left")
    fig.tight_layout(rect=(0, 0.02, 1, 0.965))
    return fig


def save(fig, out_dir: str, slug: str) -> list[str]:
    os.makedirs(out_dir, exist_ok=True)
    png = os.path.join(out_dir, f"{slug}.png")
    fig.savefig(png, dpi=200, bbox_inches="tight")
    svg = os.path.join(out_dir, f"{slug}.svg")
    fig.savefig(svg, bbox_inches="tight")
    return [png, svg]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=DATA_PATH)
    ap.add_argument("--out-dir", default=OUT_DIR)
    ap.add_argument("--no-show", action="store_true")
    args, _unknown = ap.parse_known_args(argv)  # tolerate a foreign argv (inspectors)
    df = derive(load(args.data))
    fig = build_chart(df)
    print("title:", takeaway(df).replace("\n", " / "))
    for f in save(fig, args.out_dir, SLUG):
        print("wrote", f)
    return fig


if __name__ == "__main__":
    fig = main()
