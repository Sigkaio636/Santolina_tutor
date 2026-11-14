"""The learning path of free mode: which problem comes next. A STUB for now.

Replace `PathPlanner.next` with the real back layer. It gets the history of this visit and
returns an exercise key and a reason, which is logged so the teacher sees the path.
"""

import random


class PathPlanner:
    def __init__(self, catalog):
        self.catalog = catalog

    def next(self, history: list, last: dict | None) -> tuple:
        """history: [{"key", "outcome": "solved" | "failed" | "skipped"}], last: history[-1].

        Returns (key, reason). Reason: "random", or "easier_after_fail" after a failure
        (2 wrong answers or the solution asked).
        """
        self.catalog.refresh()
        items = self.catalog.items
        if not items:
            return None, "empty"
        seen = {h["key"] for h in history}
        if last and last.get("outcome") == "failed" and last["key"] in items:
            failed = items[last["key"]]
            level = failed.exercise.level
            candidates = [
                i
                for k, i in items.items()
                if k not in seen
                and level is not None
                and i.exercise.level is not None
                and i.exercise.level < level
                and (failed.topic is None or i.topic == failed.topic)
            ]
            if not candidates and level is not None:  # no easier one of that topic: any easier
                candidates = [
                    i
                    for k, i in items.items()
                    if k not in seen and i.exercise.level is not None and i.exercise.level < level
                ]
            if candidates:
                top = max(i.exercise.level for i in candidates)
                return random.choice([i for i in candidates if i.exercise.level == top]).key, (
                    "easier_after_fail"
                )
        fresh = [k for k in items if k not in seen] or list(items)
        return random.choice(fresh), "random"
