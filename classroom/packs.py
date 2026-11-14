"""Exercise packs: a folder with manifest.json, exercises.json and optional media/.

exercises/<pack_id>/manifest.json   PackManifest
exercises/<pack_id>/exercises.json  {"schema_version": 1, "exercises": [Exercise, ...]}
exercises/<pack_id>/media/...       files that exercises list in "media"
"""

from pathlib import Path

from . import paths
from .schemas import (
    SCHEMA_VERSION,
    ContractError,
    Exercise,
    PackManifest,
    from_dict,
    read_json,
    to_dict,
    write_json,
)

MANIFEST = "manifest.json"
EXERCISES = "exercises.json"


def write_pack(folder, manifest: PackManifest, exercises: list) -> Path:
    folder = Path(folder)
    manifest.count = len(exercises)
    manifest.check()
    ids = [e.exercise_id for e in exercises]
    if len(ids) != len(set(ids)):
        raise ContractError("exercise_id must be unique within a pack")
    write_json(
        folder / EXERCISES,
        {"schema_version": SCHEMA_VERSION, "exercises": [to_dict(e) for e in exercises]},
    )
    write_json(folder / MANIFEST, manifest)
    return folder


def read_manifest(folder) -> PackManifest:
    manifest = read_json(Path(folder) / MANIFEST, PackManifest)
    if manifest is None:
        raise ContractError(f"{folder}: no {MANIFEST}")
    return manifest


def read_pack(folder):
    """Return (manifest, exercises) and check that they agree."""
    folder = Path(folder)
    manifest = read_manifest(folder)
    data = read_json(folder / EXERCISES)
    if data is None:
        raise ContractError(f"{folder}: no {EXERCISES}")
    exercises = [from_dict(Exercise, e) for e in data.get("exercises", [])]
    if len(exercises) != manifest.count:
        raise ContractError(
            f"{folder}: manifest says {manifest.count} exercises, found {len(exercises)}"
        )
    return manifest, exercises


def list_packs(root=None) -> list:
    """The manifests of the packs on a board, skipping folders that aren't valid packs."""
    folder = paths.board_root(root) / paths.EXERCISES
    manifests = []
    if folder.is_dir():
        for child in sorted(folder.iterdir()):
            try:
                manifests.append(read_manifest(child))
            except (ContractError, ValueError, OSError):
                continue
    return manifests
