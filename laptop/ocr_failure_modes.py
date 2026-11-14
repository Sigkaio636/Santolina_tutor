#!/usr/bin/env python3
"""Measure why OCR fails to read the options A to E (docs/OCR_FAILURE_MODES.md).

Two measurements, both on the output of prepare_m3kang.py:

1. Empty rows: run OCR again on a seeded random sample of the rows whose
   options are empty, and report where parsing stops.
2. Parsed rows: compare the options of the same problem across languages,
   and count duplicate options.

It prints counts only. M3Kang is research-use only: --dump writes the raw OCR
text of the sample, so keep it under data/ (gitignored).

Usage:
    python3 laptop/ocr_failure_modes.py --gpu
    python3 laptop/ocr_failure_modes.py --sample 300 --seed 0 --dump data/interim/ocr_fail_sample.json
"""
import argparse
import json
import os
import random
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from prepare_m3kang import LETTERS, is_marker, reading_order  # noqa: E402

PARQUET = "data/raw/high_quality-00000-of-00004.parquet"
STOP_AFTER_B = "sequence stops after 2 letter(s)"
C_ANYWHERE = re.compile(r"(^|[^A-Za-z])[Cc]\s*[\)）\]:.]")  # a C label inside any box
NUMBER = re.compile(r"[-−+]?[\d.,\s/]+")


def marker(letter):
    return re.compile(rf"^\s*{letter}\s*[\)）\]:.]\s*(.*)$")


def load(data):
    return [dict(json.loads(line), split=split) for split in ("train", "val")
            for line in open(os.path.join(data, f"{split}.jsonl"))]


def longest_run(items):
    """Replay parse_options: the most letters reached, and whether 5 markers had empty values."""
    best, empty_values = 0, False
    starts = [i for i, it in enumerate(items) if is_marker(it["text"], "A", strict=True) is not None]
    for start in starts:
        options, current, letters = {}, None, iter(LETTERS)
        letter = next(letters)
        for it in items[start:]:
            rest = is_marker(it["text"], letter, strict=(letter == "A")) if letter else None
            if rest is not None:
                current, options[letter] = letter, rest
                letter = next(letters, None)
            elif current:
                options[current] = (options[current] + " " + it["text"]).strip()
        best = max(best, len(options))
        if len(options) == 5 and not all(v.lstrip(")）] ").strip() for v in options.values()):
            empty_values = True
    return best, empty_values


def failure_stage(texts, items):
    if not texts:
        return "no text detected"
    if not any(is_marker(t, "A", strict=True) is not None for t in texts):
        return "no 'A)' marker"
    best, empty_values = longest_run(items)
    if empty_values:
        return "5 markers, at least one empty value"
    return f"sequence stops after {best} letter(s)"


def c_recovery(texts):
    """For a run without 'C)': can C be rebuilt from the boxes between B and D?"""
    starts = [i for i, t in enumerate(texts) if marker("A").match(t)]
    if not starts:
        return "A), B), D) or E) not found"
    texts = texts[starts[-1]:]
    pos, after = {}, -1
    for letter in "ABDE":
        found = [i for i, t in enumerate(texts) if i > after and marker(letter).match(t)]
        if not found:
            return "A), B), D) or E) not found"
        pos[letter] = after = found[0]
    between = texts[pos["B"]:pos["D"]]
    if any(marker("C").match(t) for t in between):
        return "C present"
    b_value = marker("B").match(between[0]).group(1).strip()
    values = ([b_value] if b_value else []) + between[1:]
    return "recoverable (exactly 2 values between B and D)" if len(values) == 2 else "ambiguous"


def measure_empty(rows, args):
    import pyarrow.parquet as pq
    if args.gpu:
        import onnxruntime
        onnxruntime.preload_dlls()
    from rapidocr_onnxruntime import RapidOCR

    empty = {f"{r['id']}|{r['language']}": r for r in rows if not r["options"]}
    random.seed(args.seed)
    sample = set(random.sample(sorted(empty), min(args.sample, len(empty))))
    keys = pq.read_table(args.parquet, columns=["id", "language"]).to_pylist()
    wanted = [i for i, k in enumerate(keys) if f"{k['id']}|{k['language']}" in sample]
    table = pq.read_table(args.parquet).take(wanted)
    ocr = RapidOCR(det_use_cuda=args.gpu, cls_use_cuda=args.gpu, rec_use_cuda=args.gpu)

    results = []
    for i in range(table.num_rows):
        key = f"{table.column('id')[i].as_py()}|{table.column('language')[i].as_py()}"
        boxes, _ = ocr(table.column("image")[i].as_py()["bytes"])
        items = reading_order(boxes or [])
        texts = [it["text"] for it in items]
        stage = failure_stage(texts, items)
        results.append({"key": key, "stage": stage, "text_only": empty[key]["text_only"],
                        "c_marker": any(is_marker(t, "C", strict=False) is not None for t in texts),
                        "c_anywhere": any(C_ANYWHERE.search(t) for t in texts),
                        "c_recovery": c_recovery(texts) if stage == STOP_AFTER_B else None,
                        "texts": texts})
    return len(empty), results


def measure_parsed(rows):
    by_id = defaultdict(dict)
    for r in rows:
        by_id[r["id"]][r["language"]] = r["options"]
    languages = sorted({r["language"] for r in rows})
    complete = [d for d in by_id.values() if len(d) == len(languages) and all(d.values())]
    agree = sum(1 for d in complete if all(o == d[languages[0]] for o in d.values()))
    kinds = Counter()
    for d in complete:
        for letter in LETTERS:
            values = {o[letter] for o in d.values()}
            if len(values) == 1:
                continue
            numeric = [NUMBER.fullmatch(v) is not None for v in values]
            if all(numeric):
                same = len({re.sub(r"\s", "", v).replace(",", ".") for v in values}) == 1
                if same:
                    kinds["number, only spaces or decimal comma differ"] += 1
                elif any("/" in v for v in values):
                    kinds["number, '/' lost (fraction)"] += 1
                elif len({len(re.sub(r"\s", "", v)) for v in values}) > 1:
                    kinds["number, different length (digits or tokens added or lost)"] += 1
                else:
                    kinds["number, same length, different digits"] += 1
            elif any(numeric):
                kinds["number in one language, text in another"] += 1
            else:
                kinds["text in all languages (translation or OCR)"] += 1
    duplicates = sum(1 for r in rows if r["options"] and len(set(r["options"].values())) < len(r["options"]))
    parsed = sum(1 for r in rows if r["options"])
    partial = sum(1 for r in rows if r["options"] and len(r["options"]) != 5)
    return {"languages": languages, "complete": len(complete), "agree": agree, "kinds": kinds,
            "duplicates": duplicates, "parsed": parsed, "partial": partial}


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--data", default="data", help="folder with train.jsonl and val.jsonl")
    p.add_argument("--parquet", default=PARQUET, help="the shard prepare_m3kang.py read")
    p.add_argument("--sample", type=int, default=300, help="empty rows to run OCR on again (0 to skip)")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--gpu", action="store_true", help="run OCR on CUDA (needs onnxruntime-gpu)")
    p.add_argument("--dump", help="write the raw OCR text of the sample here (keep it under data/)")
    args = p.parse_args()

    rows = load(args.data)
    print(f"Rows: {len(rows)}")

    s = measure_parsed(rows)
    print(f"\nParsed rows: {s['parsed']}/{len(rows)} ({100 * s['parsed'] / len(rows):.1f}%), "
          f"with fewer than 5 options: {s['partial']}")
    print(f"Duplicate options: {s['duplicates']} rows")
    print(f"Problems parsed in all of {', '.join(s['languages'])}: {s['complete']}, "
          f"identical options: {s['agree']} ({100 * s['agree'] / s['complete']:.1f}%)")
    print("Options that differ across languages, by kind:")
    for kind, n in s["kinds"].most_common():
        print(f"  {n:5}  {kind}")

    print("\nBy language:")
    for language in s["languages"]:
        part = [r for r in rows if r["language"] == language]
        k = sum(1 for r in part if r["options"])
        print(f"  {language}: {len(part)} rows ({len({r['id'] for r in part})} problems), "
              f"with options: {k} ({100 * k / len(part):.1f}%)")
    print(f"  all: {len({r['id'] for r in rows})} problems; "
          f"val: {len({r['id'] for r in rows if r['split'] == 'val'})} problems")

    for split in ("train", "val"):
        part = [r for r in rows if r["split"] == split]
        with_options = sum(1 for r in part if r["options"])
        print(f"\n{split}: {len(part)} rows, with options: {with_options} ({100 * with_options / len(part):.1f}%)")
        for text_only, name in ((True, "text-only"), (False, "with figure")):
            group = [r for r in part if r["text_only"] == text_only]
            k = sum(1 for r in group if r["options"])
            print(f"  {name:12} with options: {k:5}  empty: {len(group) - k:5}  total: {len(group):5}")

    if args.sample:
        n_empty, results = measure_empty(rows, args)
        n = len(results)
        print(f"\nEmpty rows: {n_empty}. OCR run again on {n} (seed {args.seed}).")
        print("Where parsing stops:")
        for stage, k in Counter(r["stage"] for r in results).most_common():
            text_only = sum(1 for r in results if r["stage"] == stage and r["text_only"])
            print(f"  {k:5}  {100 * k / n:4.0f}%  {stage}  (text-only: {text_only})")
        stop_b = [r for r in results if r["stage"] == STOP_AFTER_B]
        print(f"Rows where the sequence stops after B: {len(stop_b)}, "
              f"with a C marker the parser accepts: {sum(r['c_marker'] for r in stop_b)}, "
              f"with a C label anywhere inside a box: {sum(r['c_anywhere'] for r in stop_b)}")
        print("Those rows, if the parser may skip a missing C:")
        recovery = Counter(r["c_recovery"] for r in stop_b)
        for kind, k in recovery.most_common():
            print(f"  {k:5}  {kind}")
        # Extrapolate the recoverable share to all empty rows, with a 95% normal interval.
        k = recovery["recoverable (exactly 2 values between B and D)"]
        share = k / n
        half = 1.96 * (share * (1 - share) / n) ** 0.5
        cover = [(s["parsed"] + x * n_empty) / len(rows) for x in (share - half, share, share + half)]
        print(f"Recoverable: {k}/{n} = {100 * share:.1f}% of the sample, about {share * n_empty:.0f} of "
              f"{n_empty} empty rows. Rows with options would go from {100 * s['parsed'] / len(rows):.1f}% "
              f"to {100 * cover[1]:.1f}% (95% interval {100 * cover[0]:.1f}% to {100 * cover[2]:.1f}%).")
        if args.dump:
            with open(args.dump, "w") as f:
                json.dump(results, f, ensure_ascii=False)
            print(f"Wrote {args.dump}")


if __name__ == "__main__":
    main()
