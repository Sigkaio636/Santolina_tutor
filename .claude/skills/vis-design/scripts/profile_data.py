#!/usr/bin/env python3
"""Profile a dataset for stage 2 (data abstraction).

    python3 profile_data.py data.csv [--sep ;] [--max-rows 200000]

Reads CSV/TSV with the standard library (delimiter sniffing, decimal-comma detection) or
xlsx/parquet through pandas when available. Prints JSON:

  columns[]: name, inferred_type (quantitative|categorical|ordinal|temporal|identifier|
             geo-code|text|boolean), n_distinct, band, missing_pct, range/examples,
             role_suggestion (key|value|identifier|drop), date_format, notes
  dataset:   n_rows, items_band, candidate_keys, temporal_grains, suggested_abstractions[]
             (ready-to-paste `data` blocks for answers.json)

Nothing here is specific to any dataset; heuristics are generic.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from visdesign.vocab import band_for, items_band  # noqa: E402

DATE_FORMATS = [("%Y-%m-%d", "year-month-day"), ("%d/%m/%Y", "day/month/year"), ("%m/%d/%Y", "month/day/year"),
                ("%Y/%m/%d", "year/month/day"), ("%d-%m-%Y", "day-month-year"), ("%Y-%m-%d %H:%M:%S", "datetime"),
                ("%d/%m/%Y %H:%M", "datetime dd/mm"), ("%Y-%m", "year-month"), ("%Y", "year")]
ID_HINTS = ("id", "code", "codi", "cod", "key", "ref", "number", "num", "nif", "zip", "postal")
GEO_HINTS = ("region", "comarca", "county", "province", "provincia", "municip", "country", "pais", "state",
             "city", "ciudad", "district", "distrito", "lat", "lon", "geo", "territ")


def sniff(path: str, sep: str | None):
    with open(path, "r", encoding="utf-8-sig", errors="replace", newline="") as fh:
        head = fh.read(20000)
    if sep:
        return sep
    try:
        return csv.Sniffer().sniff(head, delimiters=",;\t|").delimiter
    except csv.Error:
        return ","


def parse_number(s: str, decimal_comma: bool):
    t = s.strip().replace(" ", "")
    if not t:
        return None
    if decimal_comma:
        t = t.replace(".", "").replace(",", ".")
    try:
        return float(t)
    except ValueError:
        return None


def try_dates(samples: list[str]):
    for fmt, name in DATE_FORMATS:
        ok = 0
        for s in samples:
            try:
                dt.datetime.strptime(s.strip(), fmt)
                ok += 1
            except ValueError:
                pass
        if ok >= max(3, int(0.9 * len(samples))):
            return fmt, name
    return None, None


def profile_column(name: str, vals: list[str], n_rows: int) -> dict:
    nonempty = [v for v in vals if v is not None and str(v).strip() not in ("", "NA", "N/A", "null", "None", "nan")]
    missing = n_rows - len(nonempty)
    distinct = Counter(nonempty)
    n_distinct = len(distinct)
    col = {"name": name, "n_distinct": n_distinct, "band": band_for(n_distinct),
           "missing_pct": round(100 * missing / max(n_rows, 1), 1), "notes": []}
    lname = name.lower()
    samples = list(distinct.keys())[:200]
    # dates
    fmt, fmt_name = try_dates(samples[:50]) if samples else (None, None)
    if fmt and n_distinct > 1:
        col["inferred_type"] = "temporal"
        col["date_format"] = fmt
        col["date_format_name"] = fmt_name
        dates = []
        for s in samples:
            try:
                dates.append(dt.datetime.strptime(s.strip(), fmt))
            except ValueError:
                pass
        if dates:
            col["range"] = [min(dates).date().isoformat(), max(dates).date().isoformat()]
            years = {d.year for d in dates}
            col["years_covered"] = sorted(years)
            col["grain_detected"] = "year" if fmt == "%Y" else ("month" if fmt == "%Y-%m" else "day")
        col["role_suggestion"] = "key"
        return col
    # numbers
    decimal_comma = sum(1 for s in samples if re.fullmatch(r"-?\d{1,3}(\.\d{3})*,\d+", s.strip())) > len(samples) * 0.5
    nums = [parse_number(s, decimal_comma) for s in samples]
    numeric_share = sum(1 for x in nums if x is not None) / max(len(samples), 1)
    leading_zero = sum(1 for s in samples if re.fullmatch(r"0\d+", s.strip())) > 0
    if numeric_share >= 0.95 and not leading_zero:
        allvals = [parse_number(s, decimal_comma) for s in nonempty]
        allvals = [x for x in allvals if x is not None]
        col["range"] = [min(allvals), max(allvals)] if allvals else None
        col["decimal_comma"] = decimal_comma
        if any(h in lname for h in ID_HINTS) and n_distinct > 0.9 * len(nonempty):
            col["inferred_type"] = "identifier"
            col["role_suggestion"] = "identifier"
        elif n_distinct <= 7 and all(float(x).is_integer() for x in allvals[:500]):
            col["inferred_type"] = "ordinal"
            col["role_suggestion"] = "key"
            col["notes"].append("few integer levels: ordinal candidate (or a code)")
        else:
            col["inferred_type"] = "quantitative"
            col["role_suggestion"] = "value"
            zeros = sum(1 for x in allvals if x == 0)
            if zeros > 0.5 * len(allvals):
                col["notes"].append(f"{round(100*zeros/len(allvals))}% zeros")
            if all(float(x).is_integer() for x in allvals[:500]):
                col["semantics_hint"] = "count"
            if any(h in lname for h in ("pct", "percent", "%", "rate", "ratio", "share")):
                col["semantics_hint"] = "rate"
        return col
    # booleans
    low = {s.strip().lower() for s in samples}
    if low and low <= {"true", "false", "yes", "no", "si", "sí", "0", "1", "y", "n"}:
        col["inferred_type"] = "boolean"
        col["role_suggestion"] = "key"
        return col
    # identifiers / codes
    if leading_zero or (any(h in lname for h in ID_HINTS) and n_distinct > 0.5 * len(nonempty)):
        col["inferred_type"] = "identifier" if not any(h in lname for h in GEO_HINTS) else "geo-code"
        col["role_suggestion"] = "identifier"
        col["notes"].append("codes with leading zeros must stay strings")
        col["examples"] = samples[:5]
        return col
    # free text vs categorical
    avg_len = sum(len(s) for s in samples) / max(len(samples), 1)
    if n_distinct > 0.8 * len(nonempty) and avg_len > 30:
        col["inferred_type"] = "text"
        col["role_suggestion"] = "drop"
        col["examples"] = samples[:3]
        return col
    col["inferred_type"] = "geo-code" if any(h in lname for h in GEO_HINTS) else "categorical"
    col["role_suggestion"] = "key"
    col["examples"] = [k for k, _ in distinct.most_common(5)]
    col["top_share_pct"] = round(100 * distinct.most_common(1)[0][1] / len(nonempty), 1) if nonempty else None
    return col


def read_table(path: str, sep: str | None, max_rows: int):
    ext = os.path.splitext(path)[1].lower()
    if ext in (".xlsx", ".xls", ".parquet"):
        try:
            import pandas as pd
        except ImportError:
            raise SystemExit("pandas is needed for xlsx/parquet; export to CSV instead")
        df = pd.read_parquet(path) if ext == ".parquet" else pd.read_excel(path)
        df = df.head(max_rows)
        return list(df.columns.astype(str)), [[("" if v is None else str(v)) for v in row] for row in df.itertuples(index=False)], None
    delim = sniff(path, sep)
    rows = []
    with open(path, "r", encoding="utf-8-sig", errors="replace", newline="") as fh:
        reader = csv.reader(fh, delimiter=delim)
        header = next(reader)
        for i, r in enumerate(reader):
            if i >= max_rows:
                break
            rows.append(r)
    return [h.strip() for h in header], rows, delim


def suggest_abstractions(cols: list[dict]) -> list[dict]:
    keys = [c for c in cols if c["role_suggestion"] == "key"]
    temporal = [c for c in keys if c["inferred_type"] == "temporal"]
    cats = [c for c in keys if c["inferred_type"] in ("categorical", "geo-code", "ordinal", "boolean")]
    vals = [c for c in cols if c["role_suggestion"] == "value"]
    out = []

    def K(c, grain=None, role=None):
        t = c["inferred_type"]
        role = role or ("time" if t == "temporal" else ("location" if t == "geo-code" else "category"))
        k = {"role": role, "type": t, "source_column": c["name"]}
        if t == "temporal":
            k["grain"] = grain or "year"
            k["cardinality"] = len(c.get("years_covered", [])) if (grain or "year") == "year" else "many"
        else:
            k["cardinality"] = c["n_distinct"]
        return k

    if temporal and cats:
        t, c = temporal[0], cats[0]
        out.append({"label": f"count of rows per {t['name']} (year) × {c['name']}",
                    "dataset_type": "table", "keys": [K(t), K(c)],
                    "values": [{"role": "measure", "type": "quantitative", "semantics": "count", "derived": True,
                                "derivation": f"count rows per (year({t['name']}), {c['name']})"}]})
        for v in vals[:2]:
            out.append({"label": f"sum of {v['name']} per {t['name']} (year) × {c['name']}",
                        "dataset_type": "table", "keys": [K(t), K(c)],
                        "values": [{"role": "measure", "type": "quantitative", "semantics": "amount", "derived": True,
                                    "derivation": f"sum({v['name']}) per (year({t['name']}), {c['name']})"}]})
    if cats:
        c = cats[0]
        out.append({"label": f"count of rows per {c['name']}", "dataset_type": "table", "keys": [K(c)],
                    "values": [{"role": "measure", "type": "quantitative", "semantics": "count", "derived": True,
                                "derivation": f"count rows per {c['name']}"}]})
        for v in vals[:2]:
            out.append({"label": f"sum of {v['name']} per {c['name']}", "dataset_type": "table", "keys": [K(c)],
                        "values": [{"role": "measure", "type": "quantitative", "semantics": "amount", "derived": True,
                                    "derivation": f"sum({v['name']}) per {c['name']}"}]})
    if temporal:
        t = temporal[0]
        out.append({"label": f"count of rows per {t['name']} (month)", "dataset_type": "table",
                    "keys": [K(t, grain="month")],
                    "values": [{"role": "measure", "type": "quantitative", "semantics": "count", "derived": True,
                                "derivation": f"count rows per month({t['name']})"}]})
    for v in vals[:3]:
        out.append({"label": f"distribution of {v['name']} (one row = one item)", "dataset_type": "table", "keys": [],
                    "values": [{"role": "measure", "type": "quantitative", "semantics": v.get("semantics_hint", "amount"),
                                "source_column": v["name"]}]})
    if len(vals) >= 2:
        out.append({"label": f"{vals[0]['name']} vs {vals[1]['name']} per item", "dataset_type": "table", "keys": [],
                    "values": [{"role": "measure", "type": "quantitative", "source_column": vals[0]["name"]},
                               {"role": "measure2", "type": "quantitative", "source_column": vals[1]["name"]}]})
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path")
    ap.add_argument("--sep")
    ap.add_argument("--max-rows", type=int, default=200000)
    args = ap.parse_args()
    header, rows, delim = read_table(args.path, args.sep, args.max_rows)
    n = len(rows)
    cols = []
    for i, name in enumerate(header):
        vals = [r[i] if i < len(r) else "" for r in rows]
        cols.append(profile_column(name, vals, n))
    temporal = [c for c in cols if c["inferred_type"] == "temporal"]
    out = {
        "file": os.path.abspath(args.path), "delimiter": delim, "n_rows": n, "items_band": items_band(n),
        "columns": cols,
        "candidate_keys": [c["name"] for c in cols if c["role_suggestion"] == "key"],
        "candidate_values": [c["name"] for c in cols if c["role_suggestion"] == "value"],
        "identifiers": [c["name"] for c in cols if c["role_suggestion"] == "identifier"],
        "temporal_columns": [{"name": c["name"], "format": c.get("date_format"), "range": c.get("range"),
                              "years": c.get("years_covered")} for c in temporal],
        "suggested_abstractions": suggest_abstractions(cols),
        "warnings": [],
    }
    if n >= args.max_rows:
        out["warnings"].append(f"only the first {args.max_rows} rows were read")
    for c in cols:
        if c["missing_pct"] > 20:
            out["warnings"].append(f"{c['name']}: {c['missing_pct']}% missing")
    json.dump(out, sys.stdout, indent=2, ensure_ascii=False, default=str)
    print()


if __name__ == "__main__":
    main()
