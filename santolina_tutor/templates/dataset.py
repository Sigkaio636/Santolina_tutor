"""Extract the M3Kang parquet shards in data/raw into plain files.

    uv run python -m santolina_tutor.templates.dataset

Output, in data/interim/m3kang/ (git-ignored; M3Kang is research-use only):
    problems.jsonl      one row per (id, language): metadata, text, label, image file
    images/<lang>/<id>.jpg   the problem image (the answer options are only in the image)

The output is deterministic: rows keep the order of the shards, and the same
input gives byte-identical files. Re-running skips images that already exist.
Note that `id` alone is NOT unique: translations share it. The key is (id, language).
"""

import json
from pathlib import Path
import re

from loguru import logger
import pyarrow.parquet as pq
from tqdm import tqdm
import typer

from santolina_tutor.config import INTERIM_DATA_DIR, RAW_DATA_DIR

app = typer.Typer()

SCALAR_COLUMNS = ["id", "language", "level", "text_only", "text", "label"]


def safe_name(value: str) -> str:
    return re.sub(r"[^\w.-]", "_", value)


@app.command()
def main(
    input_dir: Path = RAW_DATA_DIR,
    output_dir: Path = INTERIM_DATA_DIR / "m3kang",
    no_images: bool = typer.Option(False, help="skip writing the image files"),
    limit: int = typer.Option(0, help="only process the first N rows (for testing)"),
):
    shards = sorted(input_dir.glob("*.parquet"))
    if not shards:
        raise typer.BadParameter(f"no .parquet files in {input_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)

    seen: set[tuple[str, str]] = set()
    n = 0
    with open(output_dir / "problems.jsonl", "w", encoding="utf-8") as out:
        for shard in shards:
            pf = pq.ParquetFile(shard)
            logger.info(f"{shard.name}: {pf.metadata.num_rows} rows")
            # Small batches: the image column makes rows large.
            for batch in tqdm(pf.iter_batches(batch_size=64), desc=shard.name):
                for row in batch.to_pylist():
                    key = (row["id"], row["language"])
                    if key in seen:
                        raise ValueError(f"duplicate (id, language): {key}")
                    seen.add(key)

                    record = {c: row[c] for c in SCALAR_COLUMNS}
                    record["source_image"] = row["image"]["path"]
                    record["image"] = None
                    if not no_images and row["image"]["bytes"]:
                        rel = Path("images") / row["language"] / f"{safe_name(row['id'])}.jpg"
                        path = output_dir / rel
                        if not path.exists():
                            path.parent.mkdir(parents=True, exist_ok=True)
                            path.write_bytes(row["image"]["bytes"])
                        record["image"] = rel.as_posix()

                    out.write(json.dumps(record, ensure_ascii=False) + "\n")
                    n += 1
                    if limit and n >= limit:
                        break
                if limit and n >= limit:
                    break
            if limit and n >= limit:
                break
    logger.success(f"Wrote {n} problems to {output_dir}")


if __name__ == "__main__":
    app()
