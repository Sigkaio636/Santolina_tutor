"""Split the M3Kang parquet shards by the text_only flag.

data/raw/<shard>.parquet -> data/raw_txto_yes/<shard>.parquet (text_only True)
                            data/raw_txto_no/<shard>.parquet  (text_only False)
Also writes data/split_text_only.log with the language x text_only counts.
All outputs live under data/, which git ignores (M3Kang is research-only).
"""
import argparse
import collections
import glob
import os

import pyarrow.compute as pc
import pyarrow.parquet as pq


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--raw", default="data/raw")
    p.add_argument("--prefix", default="high_quality")
    p.add_argument("--out", default="data")
    args = p.parse_args()

    yes_dir = os.path.join(args.out, "raw_txto_yes")
    no_dir = os.path.join(args.out, "raw_txto_no")
    os.makedirs(yes_dir, exist_ok=True)
    os.makedirs(no_dir, exist_ok=True)

    counts = collections.Counter()
    for path in sorted(glob.glob(os.path.join(args.raw, args.prefix + "-*.parquet"))):
        table = pq.read_table(path)
        flag = table.column("text_only")
        yes = table.filter(flag)
        no = table.filter(pc.invert(flag))
        assert yes.num_rows + no.num_rows == table.num_rows
        name = os.path.basename(path)
        pq.write_table(yes, os.path.join(yes_dir, name))
        pq.write_table(no, os.path.join(no_dir, name))
        for lang, t in zip(table.column("language").to_pylist(), flag.to_pylist()):
            counts[(lang, t)] += 1
        print(f"{name}: yes={yes.num_rows} no={no.num_rows}")

    langs = sorted({lang for lang, _ in counts})
    lines = [f"{'idioma':<8}{'text_only=True':>16}{'text_only=False':>17}{'total':>8}"]
    for lang in langs:
        y, n = counts[(lang, True)], counts[(lang, False)]
        lines.append(f"{lang:<8}{y:>16}{n:>17}{y + n:>8}")
    ty = sum(counts[(l, True)] for l in langs)
    tn = sum(counts[(l, False)] for l in langs)
    lines.append(f"{'total':<8}{ty:>16}{tn:>17}{ty + tn:>8}")
    log = "\n".join(lines) + "\n"
    with open(os.path.join(args.out, "split_text_only.log"), "w") as f:
        f.write(log)
    print(log)


if __name__ == "__main__":
    main()
