"""Data-shape signatures and similarity.

A `data` block has:
  dataset_type: table | network | tree | field | geometry | text
  keys:   [{role, type, cardinality(band) | n_levels(int), grain?}]
  values: [{role, type, semantics?, derived?, derivation?}]
  items:  band (optional)

signature(data) -> "table|k:temporal:few+k:categorical:many|v:quantitative:count"
Role names, grain and items are NOT part of the signature.
"""
from __future__ import annotations

from .vocab import band_for, band_distance

SLOT_ACCEPTS = {  # which query key types a catalog slot type accepts
    "categorical": {"categorical", "ordinal", "temporal", "geo-code", "identifier", "boolean"},
    "ordinal": {"ordinal", "temporal", "categorical"},
    "temporal": {"temporal", "ordinal"},
    "geo-code": {"geo-code", "categorical", "identifier"},
    "identifier": {"identifier", "categorical"},
    "boolean": {"boolean", "categorical"},
    "quantitative": {"quantitative"},
    "text": {"text", "categorical"},
}

TYPE_KIN = {  # types that may stand in for each other when pairing keys
    "categorical": {"categorical", "geo-code", "identifier", "boolean"},
    "ordinal": {"ordinal", "temporal", "categorical"},
    "temporal": {"temporal", "ordinal"},
    "geo-code": {"geo-code", "categorical"},
    "identifier": {"identifier", "categorical"},
    "boolean": {"boolean", "categorical"},
    "quantitative": {"quantitative"},
    "text": {"text"},
}


def canonicalize(data: dict) -> dict:
    """Fill cardinality bands from n_levels / cardinality ints, normalise lists."""
    d = dict(data or {})
    keys = []
    for k in d.get("keys", []) or []:
        k = dict(k)
        card = k.get("cardinality")
        if isinstance(card, int):
            k["n_levels"] = card
            k["cardinality"] = band_for(card)
        elif card is None and isinstance(k.get("n_levels"), int):
            k["cardinality"] = band_for(k["n_levels"])
        keys.append(k)
    d["keys"] = keys
    d["values"] = [dict(v) for v in (d.get("values", []) or [])]
    d.setdefault("dataset_type", "table")
    return d


def signature(data: dict) -> str:
    d = canonicalize(data)
    ks = sorted(f"k:{k.get('type','?')}:{k.get('cardinality','?')}" for k in d["keys"])
    vs = sorted(f"v:{v.get('type','?')}" + (f":{v['semantics']}" if v.get("semantics") else "")
                for v in d["values"])
    return f"{d['dataset_type']}|{'+'.join(ks)}|{'+'.join(vs)}"


def _key_score(a: dict, b: dict) -> float:
    ta, tb = a.get("type"), b.get("type")
    if ta == tb:
        type_s = 1.0
    elif tb in TYPE_KIN.get(ta, set()):
        type_s = 0.6
    else:
        return 0.0
    ca, cb = a.get("cardinality"), b.get("cardinality")
    if ca is None or cb is None:
        band_s = 0.7
    else:
        dist = band_distance(ca, cb)
        band_s = {0: 1.0, 1: 0.7}.get(dist, 0.3)
    return type_s * band_s


def shape_similarity(q: dict, r: dict) -> tuple[float, list[str]]:
    """0..1 similarity between two data blocks, plus human-readable differences."""
    q, r = canonicalize(q), canonicalize(r)
    diffs: list[str] = []
    if q["dataset_type"] != r["dataset_type"]:
        return 0.0, [f"dataset type {q['dataset_type']} vs {r['dataset_type']}"]
    # greedy pairing of keys
    qk, rk = list(q["keys"]), list(r["keys"])
    if not qk and not rk:
        key_s = 1.0
    else:
        total, pairs = 0.0, 0
        used = set()
        for a in qk:
            best, bi = 0.0, None
            for i, b in enumerate(rk):
                if i in used:
                    continue
                s = _key_score(a, b)
                if s > best:
                    best, bi = s, i
            if bi is not None:
                used.add(bi)
                if best < 1.0:
                    diffs.append(f"key {a.get('role') or a.get('type')} {a.get('type')}:{a.get('cardinality')} vs "
                                 f"{rk[bi].get('type')}:{rk[bi].get('cardinality')}")
            else:
                diffs.append(f"key {a.get('role') or a.get('type')} has no counterpart")
            total += best
            pairs += 1
        unmatched = len(rk) - len(used)
        if unmatched:
            diffs.append(f"{unmatched} stored key(s) without counterpart")
        key_s = total / max(pairs, len(rk), 1)
    # values
    qv, rv = q["values"], r["values"]
    if not qv and not rv:
        val_s = 1.0
    else:
        hits = 0.0
        for a in qv:
            m = [b for b in rv if b.get("type") == a.get("type")]
            if m:
                hits += 1.0
                sa, sb = a.get("semantics"), m[0].get("semantics")
                if sa and sb and sa != sb and {sa, sb} <= {"count", "amount", "rate", "share"}:
                    hits -= 0.2
                    diffs.append(f"value semantics {sa} vs {sb}")
            else:
                diffs.append(f"value {a.get('role') or a.get('type')} has no counterpart")
        val_s = max(0.0, hits / max(len(qv), len(rv), 1))
    return round(0.7 * key_s + 0.3 * val_s, 3), diffs


def shape_compatible(q: dict, slot: dict) -> bool:
    """True when the query data fits a catalog entry's data_shape slot."""
    q = canonicalize(q)
    if slot.get("dataset_type") and q["dataset_type"] != slot["dataset_type"]:
        # tables of events with coordinates can feed geometry idioms only with a geometry file
        return False
    sk = slot.get("keys", []) or []
    qk = q["keys"]
    if len(qk) < len([k for k in sk if k.get("required", True)]):
        return False
    used = set()
    for a in qk:
        ok = False
        for i, b in enumerate(sk):
            if i in used:
                continue
            if a.get("type") == b.get("type") or a.get("type") in SLOT_ACCEPTS.get(b.get("type", ""), set()):
                allowed = b.get("cardinality") or []
                if not allowed or a.get("cardinality") in allowed or a.get("cardinality") is None:
                    used.add(i)
                    ok = True
                    break
        if not ok:
            return False
    sv = slot.get("values", []) or []
    qv = q["values"]
    if len(qv) < len(sv):
        return False
    for b in sv:
        if not any(a.get("type") == b.get("type") for a in qv):
            return False
    return True
