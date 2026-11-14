"""vis-design support library.

vocab     enumerations from profiles/vocab.yaml and band helpers
shape     data-shape signatures and similarity
records   decision-record validation, keys, ids, YAML I/O
store     seed and project stores, precedence, project.yaml
scoring   similarity scoring between a query and stored decisions
catalog   chart catalog loading and candidate ranking
colorcheck palette checks (sibling vischeck if present, else vendored copy)
"""
import os

SKILL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def skill_path(*parts):
    return os.path.join(SKILL_DIR, *parts)
