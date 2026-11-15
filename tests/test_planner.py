"""The free-mode planner, with simulated students on a synthetic map."""

import math
import random
import time
from types import SimpleNamespace

from classroom.schemas import Exercise
from student_app.catalog import Item
from student_app.planner import PathPlanner

TOPICS = 4
LEVELS = 8
PER_CELL = 25
DIM = 16


class FakeCatalog:
    root = None

    def __init__(self, items):
        self.items = {i.key: i for i in items}

    def refresh(self):
        pass

    def free_items(self):
        return self.items


def item(key, level, language="eng", **meta):
    e = Exercise(
        exercise_id=key,
        kind="multiple_choice",
        language=language,
        level=level,
        prompt="?",
        meta=meta,
    )
    return Item(key, SimpleNamespace(pack_id="p"), e)


def synthetic_map():
    """Each topic is a direction; a problem is that direction plus a little noise."""
    rng = random.Random(0)
    items, vectors, topic_of = [], {}, {}
    for t in range(TOPICS):
        for level in range(LEVELS):
            for n in range(PER_CELL):
                key = f"t{t}-l{level}-{n}"
                vec = [rng.gauss(0, 0.15) for _ in range(DIM)]
                vec[t] += 1
                norm = math.sqrt(sum(x * x for x in vec))
                vectors[key] = [x / norm for x in vec]
                topic_of[key] = t
                items.append(item(key, level))
    return FakeCatalog(items), vectors, topic_of


def walk(planner, steps, outcome_of):
    """Answer `steps` problems; outcome_of(item) is the simulated student."""
    history, reasons = [], []
    for _ in range(steps):
        key, reason = planner.next(history, history[-1] if history else None)
        outcome = outcome_of(planner.catalog.items[key])
        history.append({"key": key, "outcome": outcome, "reason": reason, "wrong": 0, "hints": 0})
        reasons.append(reason)
    return history, reasons


def test_settles_at_the_student_level_and_stays_on_topic():
    catalog, vectors, topic_of = synthetic_map()
    planner = PathPlanner(catalog, vectors, random.Random(1))
    start = time.perf_counter()
    history, reasons = walk(planner, 30, lambda i: "solved" if i.exercise.level < 2 else "failed")
    per_step = (time.perf_counter() - start) / 30
    levels = [catalog.items[h["key"]].exercise.level for h in history]
    assert levels[0] == 3 and reasons[0] == "start"  # the middle level
    assert set(levels[3:]) == {1, 2}  # right at 1, wrong at 2
    assert len({topic_of[h["key"]] for h in history}) == 1
    assert len({h["key"] for h in history}) == 30  # never the same problem twice
    assert per_step < 0.5


def test_a_mastered_topic_changes():
    catalog, vectors, topic_of = synthetic_map()
    planner = PathPlanner(catalog, vectors, random.Random(1))
    history, reasons = walk(planner, 8, lambda i: "solved")
    assert reasons[:4] == [
        "start",
        "harder_after_solve",
        "harder_after_solve",
        "new_topic_after_mastery",
    ]
    topics = [topic_of[h["key"]] for h in history]
    levels = [catalog.items[h["key"]].exercise.level for h in history]
    assert topics[0] == topics[1] == topics[2] != topics[3]
    assert levels[:5] == [3, 4, 5, 5, 6]  # the new topic keeps the level, then goes up again
    assert reasons[6] == "new_topic_after_mastery"


def test_help_keeps_the_level_and_a_skip_changes_topic():
    catalog, vectors, topic_of = synthetic_map()
    planner = PathPlanner(catalog, vectors, random.Random(1))
    first, _ = planner.next([], None)
    entry = {"key": first, "outcome": "solved", "reason": "start", "wrong": 1, "hints": 0}
    key, reason = planner.next([entry], entry)
    assert reason == "same_level_after_help"
    assert catalog.items[key].exercise.level == 3 and topic_of[key] == topic_of[first]
    entry = {"key": first, "outcome": "skipped", "reason": "start", "wrong": 0, "hints": 0}
    key, reason = planner.next([entry], entry)
    assert reason == "other_topic_after_skip"
    assert catalog.items[key].exercise.level == 3 and topic_of[key] != topic_of[first]


def test_without_vectors_the_pack_topic_is_used():
    items = [
        item(f"{t}{level}{n}", level, topic=t)
        for t in ("Addition", "Division")
        for level in range(3)
        for n in range(3)
    ]
    planner = PathPlanner(FakeCatalog(items), {}, random.Random(1))
    entry = {"key": "Division20", "outcome": "failed", "reason": "start"}
    key, reason = planner.next([entry], entry)
    assert reason == "easier_after_fail" and key.startswith("Division1")


def test_language_progress_and_translations():
    items = [
        item(f"{n}_{lang}", 2, lang, m3kang_id=str(n)) for n in range(3) for lang in ("eng", "cat")
    ]
    planner = PathPlanner(FakeCatalog(items), {}, random.Random(1))
    progress = {"exercises": {"0_eng": {"status": "done", "first_try_correct": True}}}
    entry = {"key": "1_cat", "outcome": "solved", "reason": "start"}
    key, _ = planner.next([entry], entry, progress, "cat")
    assert key == "2_cat"  # 0 is done in English, 1 was just seen
    # Everything done: a problem comes back rather than nothing.
    history = [{"key": f"{n}_cat", "outcome": "solved", "reason": None} for n in range(3)]
    assert planner.next(history, history[-1], progress, "cat")[0].endswith("_cat")
