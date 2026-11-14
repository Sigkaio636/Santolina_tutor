#!/usr/bin/env python3
"""Deterministic checks on a rendered chart image (PNG/JPG/GIF/WebP/BMP).

Produces: a palette summary of salient chromatic colors, red–green risk, CVD
confusability of the palette, simulated deuteranopia/protanopia/tritanopia images,
a grayscale image ("get it right in black and white"), ink/background statistics,
and, when the `tesseract` CLI exists, OCR-based text-size statistics and the words
found in the title, left-margin and bottom-margin bands.

Usage:
    python3 inspect_image.py chart.png [--out-dir DIR] [--no-ocr]

Look at the derived images yourself: the script cannot judge whether categories are
still distinguishable, only whether the palette colors merge.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vischeck.findings import Report  # noqa: E402
from vischeck.color import (simulate_cvd_image, grayscale_image, palette_report,  # noqa: E402
                            relative_luminance, saturation, hue_deg, to_hex, value)

try:
    import numpy as np
    from PIL import Image
except Exception as e:  # pragma: no cover
    print('{"error": "numpy and Pillow are required: %s"}' % e)
    sys.exit(1)


def load(path):
    im = Image.open(path)
    if im.mode in ("RGBA", "LA", "P"):
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
        bg.paste(im.convert("RGBA"), mask=im.convert("RGBA").split()[-1])
        im = bg.convert("RGB")
    else:
        im = im.convert("RGB")
    return im


def salient_palette(arr, max_colors=24):
    """Quantize to 6 bits/channel, drop neutrals, cluster by hue/lightness bins."""
    h, w, _ = arr.shape
    total = h * w
    q = (arr >> 3) << 3  # 32 levels
    flat = q.reshape(-1, 3)
    # subsample for speed
    step = max(1, flat.shape[0] // 400_000)
    flat = flat[::step]
    cnt = Counter(map(tuple, flat))
    neutral_px = 0
    chroma = Counter()
    for (r, g, b), n in cnt.items():
        rgb = (r / 255, g / 255, b / 255)
        if saturation(rgb) < 0.2 or value(rgb) < 0.12:
            neutral_px += n
            continue
        # hue bin 20°, lightness bin 3 levels
        hb = int(hue_deg(rgb) // 20)
        lb = int(relative_luminance(rgb) * 3)
        chroma[(hb, lb)] += n
    sub_total = sum(cnt.values())
    # representative color per bin: weighted mean of members
    reps = {}
    sums = {}
    for (r, g, b), n in cnt.items():
        rgb = (r / 255, g / 255, b / 255)
        if saturation(rgb) < 0.2 or value(rgb) < 0.12:
            continue
        key = (int(hue_deg(rgb) // 20), int(relative_luminance(rgb) * 3))
        s = sums.setdefault(key, [0.0, 0.0, 0.0, 0])
        s[0] += rgb[0] * n
        s[1] += rgb[1] * n
        s[2] += rgb[2] * n
        s[3] += n
    for key, (r, g, b, n) in sums.items():
        reps[key] = (r / n, g / n, b / n)
    pal = []
    for key, n in chroma.most_common(max_colors):
        frac = n / sub_total
        if frac < 0.0015:
            break
        pal.append((reps[key], frac))
    # background: most common quantized color overall
    bg_rgb, bg_n = cnt.most_common(1)[0]
    bg = tuple(v / 255 for v in bg_rgb)
    return pal, bg, bg_n / sub_total, neutral_px / sub_total


def ocr(path, w, h):
    exe = shutil.which("tesseract")
    if not exe:
        return None
    try:
        out = subprocess.run([exe, path, "-", "--psm", "11", "tsv"],
                             capture_output=True, text=True, timeout=120)
    except Exception:
        return None
    words = []
    for line in out.stdout.splitlines()[1:]:
        parts = line.split("\t")
        if len(parts) < 12:
            continue
        try:
            conf = float(parts[10])
        except ValueError:
            continue
        text = parts[11].strip()
        if conf < 40 or not text or len(text) < 2:
            continue
        left, top, width, height = (int(parts[6]), int(parts[7]), int(parts[8]),
                                    int(parts[9]))
        if height < 4 or height > h * 0.3:
            continue
        words.append({"text": text, "x": left, "y": top, "w": width, "h": height,
                      "conf": conf})
    return words


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("image")
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--no-ocr", action="store_true")
    args = ap.parse_args()
    out_dir = args.out_dir or tempfile.mkdtemp(prefix="vischeck_img_")
    os.makedirs(out_dir, exist_ok=True)
    report = Report(args.image, "image")

    im = load(args.image)
    arr = np.asarray(im).astype(np.uint8)
    h, w, _ = arr.shape
    report.summary["size_px"] = [w, h]
    if w < 500:
        report.add("EFF-18", "minor", "Low-resolution image; details and text may be "
                   "illegible.", f"width={w}px", where="image", kind="SEMI")

    pal, bg, bg_frac, neutral_frac = salient_palette(arr)
    report.summary["background"] = {"hex": to_hex(bg), "fraction": round(bg_frac, 3),
                                    "luminance": round(relative_luminance(bg), 3)}
    report.summary["neutral_fraction"] = round(neutral_frac, 3)
    report.summary["chromatic_colors"] = [
        {"hex": to_hex(c), "fraction": round(f, 4)} for c, f in pal]
    ink = 1 - bg_frac
    report.summary["non_background_fraction"] = round(ink, 3)
    if relative_luminance(bg) < 0.35:
        report.add("COL-06", "minor", "Dark background: check contrast of every mark and "
                   "label (3:1 non-text, 4.5:1 text).", f"bg={to_hex(bg)}", where="image",
                   kind="SEMI")
    if ink > 0.75:
        report.add("CLT-02", "minor", "Over 75 % of pixels are non-background: dense or "
                   "cluttered; check for an entry point and white space.",
                   f"non-background={ink:.2f}", where="image", kind="SEMI")
    if ink < 0.05:
        report.add("CLT-03", "minor", "Under 5 % of pixels carry anything: very low data "
                   "density.", f"non-background={ink:.2f}", where="image", kind="SEMI")
    # chromatic colors covering > 15 % of the image are areas (backgrounds, fills),
    # not category marks
    report.summary["large_chromatic_areas"] = [to_hex(c) for c, f in pal if f > 0.15]
    cols = [c for c, f in pal if f <= 0.15]
    if len(cols) >= 2:
        pr = palette_report(cols)
        report.summary["palette"] = pr
        nsal = sum(1 for c, f in pal if 0.003 < f <= 0.15)
        if nsal > 8:
            report.add("COL-04", "major", f"About {nsal} salient chromatic colors: more "
                       "than readers can match to a legend.", "", where="image",
                       kind="SEMI",
                       exception="a sequential/diverging ramp rather than categories")
        if pr["has_red_and_green"]:
            report.add("COL-05", "major", "Red and green both prominent (colorblind "
                       "risk); confirm with the deuteranopia image.",
                       f"{pr['hex'][:8]}", where="image", kind="SEMI")
        for p in pr["confusable_deuteranopia"][:4]:
            report.add("COL-05", "major", "Two salient colors merge under deuteranopia.",
                       f"{p['a']} vs {p['b']} ΔE sim={p['dE_simulated']}", where="image",
                       kind="SEMI")
        if saturation(bg) > 0.25:
            report.add("CLT-01", "minor", "Saturated background color.", to_hex(bg),
                       where="image")

    base = os.path.splitext(os.path.basename(args.image))[0]
    for kind in ("deuteranopia", "protanopia", "tritanopia"):
        p = os.path.join(out_dir, f"{base}_{kind}.png")
        Image.fromarray(simulate_cvd_image(arr, kind)).save(p)
        report.artifacts.append(p)
    p = os.path.join(out_dir, f"{base}_grayscale.png")
    Image.fromarray(grayscale_image(arr)).save(p)
    report.artifacts.append(p)

    if not args.no_ocr:
        words = ocr(args.image, w, h)
        if words is None:
            report.warn("tesseract not available or failed: no text statistics.")
        else:
            report.summary["ocr_words"] = len(words)
            if not words:
                report.add("TXT-01", "major", "No readable text found: no title, axis "
                           "titles or labels (or text too small/rotated for OCR).",
                           "OCR found 0 words", where="image", kind="SEMI")
            else:
                hs = sorted(x["h"] for x in words)
                med = hs[len(hs) // 2]
                # normalize to a 1920-px-wide display
                scale = 1920 / w if w > 1920 else 1.0
                small = [x for x in words if x["h"] * scale < 11]
                report.summary["text_height_px"] = {"min": hs[0], "median": med,
                                                    "max": hs[-1]}
                if small and len(small) >= max(3, len(words) // 4):
                    report.add("ACC-05", "major", "A quarter or more of the text would be "
                               "under ~11 px on a 1920-px-wide display.",
                               f"{len(small)}/{len(words)} words; e.g. "
                               f"{[x['text'] for x in small[:5]]}", where="image",
                               kind="SEMI")
                top = [x["text"] for x in words if x["y"] < h * 0.12]
                left = [x["text"] for x in words if x["x"] < w * 0.08]
                bottom = [x["text"] for x in words if x["y"] > h * 0.9]
                big = [x["text"] for x in words if x["h"] >= med * 1.3 and x["y"] < h * 0.2]
                report.summary["text_bands"] = {"top": top[:25], "left": left[:25],
                                                "bottom": bottom[:25], "large_top": big[:15]}
                if not big and not top:
                    report.add("TXT-01", "major", "No title-like text at the top of the "
                               "image.", "", where="image", kind="SEMI",
                               exception="caption in the surrounding document")
                alltext = " ".join(x["text"] for x in words).lower()
                if not any(k in alltext for k in ("source", "font", "fuente", "data:",
                                                  "dades", "n=", "n =")):
                    report.add("TXT-08", "minor", "No source / n statement detected in "
                               "the text (C component).", "", where="image", kind="SEMI")
                units_like = any(ch in alltext for ch in ("%", "(", "€", "$", "°"))
                if not units_like:
                    report.add("SCL-06", "minor", "No unit-like token found in any label.",
                               "", where="image", kind="SEMI",
                               exception="unitless quantities")
    report.dump()


if __name__ == "__main__":
    main()
