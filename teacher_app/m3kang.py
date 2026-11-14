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
            exercises.append(
                Exercise(
                    exercise_id=exercise_id,
                    kind="multiple_choice",
                    language=p.get("language", ""),
                    level=p.get("level"),
                    prompt=p.get("text", ""),
                    options=p.get("options") or None,
                    answer=p.get("label"),
                    media=media,
                    meta={
                        "source": "m3kang",
                        "m3kang_id": p["id"],
                        "year": p.get("year"),
                        "text_only": p.get("text_only"),
                    },
                )
            )
            if limit and len(exercises) >= limit:
                break
    langs = sorted({e.language for e in exercises})
    manifest = PackManifest(
        pack_id=pack_id,
        title=title,
        version=version,
        language=",".join(langs),
        created_at=now_iso(),
        count=len(exercises),
        description="From M3Kang (research use only).",
    )
    folder = write_pack(Path(out_dir) / pack_id, manifest, exercises)
    for e in exercises:
        for m in e.media or []:
            dest = folder / m
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(Path(images) / Path(m).name, dest)
    return folder
