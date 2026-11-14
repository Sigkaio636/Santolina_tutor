"""The stats registry. A widget is one function that reads the database and returns data.

To add a statistic, write a function in a module of this package and decorate it:

    @widget("my_stat", "My statistic", scopes=("global", "student"))
    def my_stat(conn, scope, ref):
        where, params = event_filter(scope, ref)
        ...
        return {"kind": "bar", "labels": [...], "series": [{"label": "...", "data": [...]}]}

`scope` is where the widget is shown: "global" (dashboard), "group", "student" or "board".
`ref` is the id of that group, student or board (None for global).
The page draws the returned data by its "kind", so a new widget needs no HTML:
  {"kind": "kpis",  "items": [{"label": ..., "value": ...}]}
  {"kind": "bar" | "line", "labels": [...], "series": [{"label": ..., "data": [...]}], "unit": "%"}
  {"kind": "table", "columns": [...], "rows": [[...], ...]}
  {"kind": "empty", "message": ...}
"""

from collections.abc import Callable
from dataclasses import dataclass

SCOPES = ("global", "group", "student", "board")


@dataclass
class Widget:
    id: str
    title: str
    scopes: tuple
    compute: Callable
    order: int = 100


REGISTRY: dict = {}


def widget(id: str, title: str, scopes=SCOPES, order: int = 100):
    def register(fn):
        REGISTRY[id] = Widget(id=id, title=title, scopes=tuple(scopes), compute=fn, order=order)
        return fn

    return register


def for_scope(scope: str) -> list:
    return sorted((w for w in REGISTRY.values() if scope in w.scopes), key=lambda w: w.order)


def render_all(conn, scope: str, ref=None) -> list:
    """[(widget, data)] for one page. A widget that fails shows its error, not a crash."""
    out = []
    for w in for_scope(scope):
        try:
            data = w.compute(conn, scope, ref)
        except Exception as e:  # noqa: BLE001  (one broken widget must not break the page)
            data = {"kind": "empty", "message": f"Error: {type(e).__name__}: {e}"}
        out.append((w, data))
    return out


def event_filter(scope: str, ref, alias: str = "e"):
    """A WHERE clause and its parameters that limit events to the scope."""
    if scope == "group":
        return (f"{alias}.student_id IN (SELECT id FROM students WHERE group_id = ?)", (ref,))
    if scope == "student":
        return f"{alias}.student_id = ?", (ref,)
    if scope == "board":
        return f"{alias}.board_id = ?", (ref,)
    return "1 = 1", ()
