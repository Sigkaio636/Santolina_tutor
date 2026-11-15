"""Flatten data/processed/explanations/raw/<model>.jsonl into one tidy metrics table.

    uv run python -m santolina_tutor.explanation_metrics

One row per (teacher, id, language). Only numbers, flags and metadata: no problem text,
so the table can feed a dashboard. It still stays in data/ (git-ignored), next to the raw files.
"""

import csv
import json
from pathlib import Path

from loguru import logger
import typer

from santolina_tutor.config import PROCESSED_DATA_DIR

app = typer.Typer()

FIELDS = [
    "teacher", "id", "language", "level", "label", "final_answer", "ok", "answer_matches_label",
    "agrees_with_key", "has_5_options", "needs_figure", "topic", "n_hints", "n_steps",
    "n_mistakes", "solution_chars", "hints_chars", "seconds", "prompt_tokens", "image_tokens",
    "completion_tokens", "reasoning_tokens", "total_tokens", "error", "trusted_problem", "usable",
]


def flatten(record: dict) -> dict:
    out = record.get("output") or {}
    checks = record.get("checks") or {}
    usage = record.get("usage") or {}
    details = usage.get("completion_tokens_details") or {}
    prompt_details = usage.get("prompt_tokens_details") or {}
    image = (prompt_details.get("multimodal_tokens") or {}).get("image") or prompt_details.get("image_tokens")
    steps = out.get("solution_steps") or []
    hints = out.get("hints") or []
    match = checks.get("answer_matches_label")
    return {
        "teacher": record["teacher"],
        "id": record["id"],
        "language": record["language"],
        "level": record["level"],
        "label": record["label"],
        "final_answer": str(out.get("final_answer", "") or "")[:1],
        # ok = usable: answered, reached the key, all five options, did not dispute the key
        "ok": bool(match and checks.get("has_5_options") and out.get("agrees_with_key") is not False),
        "answer_matches_label": match,
        "agrees_with_key": out.get("agrees_with_key"),
        "has_5_options": checks.get("has_5_options"),
        "needs_figure": out.get("needs_figure"),
        "topic": out.get("topic"),
        "n_hints": len(hints),
        "n_steps": len(steps),
        "n_mistakes": len(out.get("common_mistakes") or []),
        "solution_chars": sum(len(s) for s in steps),
        "hints_chars": sum(len(h) for h in hints),
        "seconds": record.get("seconds"),
        "prompt_tokens": usage.get("prompt_tokens"),
        "image_tokens": image or None,
        "completion_tokens": usage.get("completion_tokens"),
        # Only some providers report it; empty means "not reported", not zero.
        "reasoning_tokens": details.get("reasoning_tokens") or None,
        "total_tokens": usage.get("total_tokens"),
        "error": record.get("error") or "",
    }


@app.command()
def main(
    input_dir: Path = PROCESSED_DATA_DIR / "explanations" / "raw",
    output_path: Path = PROCESSED_DATA_DIR / "explanations" / "metrics.csv",
):
    rows = []
    for path in sorted(input_dir.glob("*.jsonl")):
        with open(path, encoding="utf-8") as f:
            rows += [flatten(json.loads(line)) for line in f]
    # Same rule as the SFT filter in generate_explanations.build_sft: a problem is trusted
    # when a strict majority of the teachers that answered reached the official key.
    votes: dict[tuple, list] = {}
    for r in rows:
        if not r["error"]:
            votes.setdefault((r["id"], r["language"]), []).append(bool(r["answer_matches_label"]))
    for r in rows:
        v = votes.get((r["id"], r["language"]), [])
        r["trusted_problem"] = bool(v) and sum(v) * 2 > len(v)
        r["usable"] = r["ok"] and r["trusted_problem"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    logger.success(f"Wrote {len(rows)} rows to {output_path}")


if __name__ == "__main__":
    app()
