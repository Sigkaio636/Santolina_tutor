#!/usr/bin/env python3
"""Build a local HTML dashboard of how well OCR read the options A to E.

Reads data/train.jsonl and data/val.jsonl (written by prepare_m3kang.py) and
writes data/interim/ocr_dashboard.html. The page holds only counts and
percentages, never problem text or option values: M3Kang is research-use
only, and data/ is gitignored. Don't publish the page.

Usage:
    python3 laptop/ocr_report.py
    python3 laptop/ocr_report.py --data data --out data/interim/ocr_dashboard.html
"""
import argparse
import html
import json
import os
from collections import defaultdict

# Reference run documented in docs/BOARD_SETUP.md (section 9.2), English only.
BASELINE = {"label": "Ejecución documentada (BOARD_SETUP.md, eng)",
            "with": 1078, "total": 1747, "to_with": 601, "to_total": 811}


def load(data):
    rows = []
    for split in ("train", "val"):
        with open(os.path.join(data, f"{split}.jsonl")) as f:
            for line in f:
                r = json.loads(line)
                r["split"] = split
                rows.append(r)
    return rows


def coverage(rows, key):
    d = defaultdict(lambda: [0, 0])
    for r in rows:
        k = key(r)
        d[k][0] += bool(r["options"])
        d[k][1] += 1
    return [(k, a, b) for k, (a, b) in sorted(d.items())]


def pct(a, b):
    return 100 * a / b if b else 0


def bar_chart(title, data, note=""):
    """Horizontal bars of coverage %, one series. data: [(label, ok, total)]."""
    row_h, label_w, w = 26, 150, 560
    h = row_h * len(data) + 24
    plot_w = w - label_w - 60
    parts = []
    for i, (label, ok, total) in enumerate(data):
        y = i * row_h
        bw = max(plot_w * pct(ok, total) / 100, 1)
        tip = f"{label}: {ok}/{total} ({pct(ok, total):.1f}%)"
        parts.append(
            f'<g class="mark" data-tip="{html.escape(tip)}">'
            f'<rect x="0" y="{y}" width="{w}" height="{row_h}" fill="transparent"/>'
            f'<text x="{label_w - 8}" y="{y + 17}" text-anchor="end" class="lbl">{html.escape(str(label))}</text>'
            f'<rect x="{label_w}" y="{y + 5}" width="{bw:.1f}" height="{row_h - 10}" rx="4" class="bar"/>'
            f'<text x="{label_w + bw + 6:.1f}" y="{y + 17}" class="val">{pct(ok, total):.0f}%</text></g>')
    grid = "".join(
        f'<line x1="{label_w + plot_w * t / 100}" x2="{label_w + plot_w * t / 100}" y1="0" y2="{h - 20}" class="grid"/>'
        f'<text x="{label_w + plot_w * t / 100}" y="{h - 6}" text-anchor="middle" class="axis">{t}%</text>'
        for t in (0, 25, 50, 75, 100))
    rows_html = "".join(f"<tr><td>{html.escape(str(l))}</td><td>{o}</td><td>{t}</td><td>{pct(o, t):.1f}%</td></tr>"
                        for l, o, t in data)
    return (f'<section class="card"><h2>{title}</h2>'
            + (f'<p class="note">{note}</p>' if note else "")
            + f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{html.escape(title)}">{grid}{"".join(parts)}</svg>'
            f'<details><summary>Ver tabla</summary><table><tr><th></th><th>Con opciones</th><th>Total</th><th>%</th></tr>'
            f'{rows_html}</table></details></section>')


def build(rows):
    n = len(rows)
    ok = sum(1 for r in rows if r["options"])
    partial = sum(1 for r in rows if r["options"] and len(r["options"]) != 5)
    dup = sum(1 for r in rows if r["options"] and len(set(r["options"].values())) < len(r["options"]))

    eng = [r for r in rows if r["language"] == "eng"]
    eng_ok = sum(1 for r in eng if r["options"])
    eng_to = [r for r in eng if r["text_only"]]
    eng_to_ok = sum(1 for r in eng_to if r["options"])

    by_id = defaultdict(dict)
    for r in rows:
        by_id[r["id"]][r["language"]] = r["options"]
    langs = sorted({r["language"] for r in rows})
    full = [d for d in by_id.values() if len(d) == len(langs) and all(d.values())]
    agree = sum(1 for d in full if len({json.dumps(v, sort_keys=True) for v in d.values()}) == 1)

    tiles = [
        ("Filas procesadas", f"{n}", ", ".join(f"{l}: {sum(1 for r in rows if r['language'] == l)}" for l in langs)),
        ("Con las 5 opciones", f"{pct(ok, n):.0f}%", f"{ok}/{n} · parciales: {partial}"),
        ("Opciones repetidas", f"{dup}", "filas con dos opciones iguales (lectura dudosa)"),
        ("Acuerdo entre idiomas", f"{pct(agree, len(full)):.0f}%",
         f"{agree}/{len(full)} problemas con opciones idénticas en {', '.join(langs)}"),
    ]
    tiles_html = "".join(f'<div class="tile"><div class="tl">{t}</div><div class="tv">{v}</div><div class="ts">{s}</div></div>'
                         for t, v, s in tiles)

    b = BASELINE
    compare = (
        '<section class="card"><h2>Comparación con la ejecución de referencia (solo eng)</h2>'
        '<p class="note">La referencia es la salida documentada en docs/BOARD_SETUP.md §9.2. '
        'No hay registro de con qué dispositivo se hizo.</p><table>'
        '<tr><th></th><th>Referencia</th><th>Esta ejecución</th><th>Diferencia</th></tr>'
        f'<tr><td>Con opciones</td><td>{b["with"]}/{b["total"]} ({pct(b["with"], b["total"]):.1f}%)</td>'
        f'<td>{eng_ok}/{len(eng)} ({pct(eng_ok, len(eng)):.1f}%)</td><td>{eng_ok - b["with"]:+d}</td></tr>'
        f'<tr><td>Solo texto con opciones</td><td>{b["to_with"]}/{b["to_total"]} ({pct(b["to_with"], b["to_total"]):.1f}%)</td>'
        f'<td>{eng_to_ok}/{len(eng_to)} ({pct(eng_to_ok, len(eng_to)):.1f}%)</td><td>{eng_to_ok - b["to_with"]:+d}</td></tr>'
        '</table></section>')

    charts = [
        bar_chart("Cobertura por idioma", coverage(rows, lambda r: r["language"])),
        bar_chart("Con figura vs. solo texto",
                  coverage(rows, lambda r: "solo texto" if r["text_only"] else "con figura"),
                  "Con figura, las opciones suelen ser dibujos y el OCR no las puede leer."),
        bar_chart("Cobertura por nivel", coverage(rows, lambda r: f"nivel {r['level']}")),
        bar_chart("Cobertura por año", coverage(rows, lambda r: r["year"]),
                  "La cobertura cae en los exámenes recientes: posible cambio de maquetación."),
        bar_chart("Cobertura por split", coverage(rows, lambda r: r["split"])),
    ]
    return PAGE.replace("{{TILES}}", tiles_html).replace("{{BODY}}", compare + "".join(charts))


PAGE = """<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Cobertura OCR M3Kang</title>
<style>
:root{--surface:#fcfcfb;--card:#ffffff;--text:#0b0b0b;--text2:#52514e;--muted:#8a8984;--grid:#e6e5e0;--bar:#2a78d6}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--surface:#1a1a19;--card:#232322;--text:#f0efec;--text2:#c3c2b7;--muted:#8f8e86;--grid:#363633;--bar:#3987e5}}
:root[data-theme="dark"]{--surface:#1a1a19;--card:#232322;--text:#f0efec;--text2:#c3c2b7;--muted:#8f8e86;--grid:#363633;--bar:#3987e5}
*{box-sizing:border-box}body{margin:0;background:var(--surface);color:var(--text);font:14px/1.45 system-ui,sans-serif}
main{max-width:1180px;margin:0 auto;padding:24px 16px}h1{font-size:22px;margin:0 0 4px}.sub{color:var(--text2);margin:0 0 20px}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin-bottom:16px}
.tile,.card{background:var(--card);border:1px solid var(--grid);border-radius:10px;padding:14px 16px}
.tl{color:var(--text2);font-size:12px}.tv{font-size:30px;font-weight:600;margin:2px 0}.ts{color:var(--muted);font-size:12px}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,520px),1fr));gap:12px}
.card{margin-bottom:12px}h2{font-size:15px;margin:0 0 6px}.note{color:var(--text2);font-size:12px;margin:0 0 8px}
svg{width:100%;height:auto;overflow:visible}.bar{fill:var(--bar)}.grid{stroke:var(--grid)}
.lbl{fill:var(--text2);font-size:12px}.val{fill:var(--text);font-size:12px}.axis{fill:var(--muted);font-size:11px}
.mark:hover .bar{opacity:.8}table{border-collapse:collapse;width:100%;font-size:13px;margin-top:6px}
th,td{text-align:left;padding:4px 8px;border-bottom:1px solid var(--grid)}th{color:var(--text2);font-weight:500}
details summary{cursor:pointer;color:var(--text2);font-size:12px;margin-top:6px}
#tip{position:fixed;pointer-events:none;background:var(--text);color:var(--surface);padding:4px 8px;border-radius:6px;font-size:12px;display:none}
</style></head><body><main>
<h1>Cobertura del OCR de opciones (M3Kang)</h1>
<p class="sub">Problemas cuyas cinco opciones A–E se leyeron de la imagen. Solo contiene recuentos: no publicar ni subir a Git.</p>
<div class="tiles">{{TILES}}</div>
<div class="grid2">{{BODY}}</div>
</main><div id="tip"></div>
<script>
const tip=document.getElementById('tip');
document.querySelectorAll('.mark').forEach(m=>{
 m.addEventListener('mousemove',e=>{tip.textContent=m.dataset.tip;tip.style.display='block';
  tip.style.left=Math.min(e.clientX+12,innerWidth-tip.offsetWidth-8)+'px';tip.style.top=(e.clientY+12)+'px'});
 m.addEventListener('mouseleave',()=>tip.style.display='none');});
</script></body></html>"""


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--data", default="data")
    p.add_argument("--out", default="data/interim/ocr_dashboard.html")
    args = p.parse_args()
    rows = load(args.data)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        f.write(build(rows))
    print(f"Wrote {args.out} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
