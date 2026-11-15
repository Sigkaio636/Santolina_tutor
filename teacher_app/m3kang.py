"""Turn prepared M3Kang problems (laptop/prepare_m3kang.py output) into an exercise pack.

M3Kang is licensed for research use only: use these packs only within that licence
(e.g. the datathon), and write them outside the Git repository (the default is the
teacher app's own folder).
"""

import json
from pathlib import Path
import shutil

from classroom.packs import write_pack
from classroom.schemas import Exercise, PackManifest, now_iso


def exercise_from(p: dict, media=None) -> Exercise:
    """One prepared M3Kang problem as a pack exercise."""
    return Exercise(
        exercise_id=f"{p['id']}_{p['language']}",
        kind="multiple_choice",
        language=p.get("language", ""),
        level=p.get("level"),
        prompt=p.get("text", ""),
        options=p.get("options") or None,
        answer=p.get("label"),
        media=media,
        meta={
            **({"topic": p["topic"]} if p.get("topic") else {}),
            "source": "m3kang",
            "m3kang_id": p["id"],
            "year": p.get("year"),
            "text_only": p.get("text_only"),
        },
    )


def manifest_for(exercises: list, pack_id: str, title: str, version: int = 1) -> PackManifest:
    return PackManifest(
        pack_id=pack_id,
        title=title,
        version=version,
        language=",".join(sorted({e.language for e in exercises})),
        created_at=now_iso(),
        count=len(exercises),
        description="From M3Kang (research use only).",
    )


def convert(
    source: Path,
    out_dir: Path,
    pack_id: str,
    title: str,
    languages: set | None = None,
    levels: set | None = None,
    limit: int | None = None,
    only_with_options: bool = True,
    images: Path | None = None,
    version: int = 1,
) -> Path:
    exercises = []
    with open(source, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            p = json.loads(line)
            if languages and p.get("language") not in languages:
                continue
            if levels and p.get("level") not in levels:
                continue
            if only_with_options and not p.get("options"):
                continue
            exercise_id = f"{p['id']}_{p['language']}"
            media = None
            if images:
                image = Path(images) / f"{exercise_id}.png"
                if image.exists():
                    media = [f"media/{image.name}"]
            if p.get("text_only") is False and not media:
                continue  # the statement needs its picture, and we don't have it
            exercises.append(exercise_from(p, media))
            if limit and len(exercises) >= limit:
                break
    manifest = manifest_for(exercises, pack_id, title, version)
    folder = write_pack(Path(out_dir) / pack_id, manifest, exercises)
    for e in exercises:
        for m in e.media or []:
            dest = folder / m
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(Path(images) / Path(m).name, dest)
    return folder
