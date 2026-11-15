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
A table cell can be a dict to draw a bar: {"bar": 0-100, "text": ..., "few": bool}.
Any widget can add "title": one sentence with the finding, shown over the data.
The kinds in learning.py (classmap, daybars, hbars, strips, sessions, profile, trace) have
their own drawing in _widgets.html.

Widgets read events through event_filter(), which also applies the period the page asked for.
"""

from collections.abc import Callable
from contextvars import ContextVar
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

SCOPES = ("global", "group", "student", "board")


@dataclass
class Widget:
    id: str
    title: str
    scopes: tuple
    compute: Callable
    order: int = 100


REGISTRY: dict = {}

# The period of the page being drawn: (first day "YYYY-MM-DD" or None, its label).
PERIODS = {"7": ("Last 7 days", 7), "30": ("Last 30 days", 30), "all": ("All", None)}
_SINCE: ContextVar = ContextVar("since", default=None)


def since_day(period) -> str | None:
    days = PERIODS.get(str(period), PERIODS["all"])[1]
    return (datetime.now(UTC) - timedelta(days=days)).date().isoformat() if days else None


def widget(id: str, title: str, scopes=SCOPES, order: int = 100):
    def register(fn):
        REGISTRY[id] = Widget(id=id, title=title, scopes=tuple(scopes), compute=fn, order=order)
        return fn

    return register


def for_scope(scope: str) -> list:
    return sorted((w for w in REGISTRY.values() if scope in w.scopes), key=lambda w: w.order)


def render_all(conn, scope: str, ref=None, only=None, period="all") -> list:
    """[(widget, data)] for one page. A widget that fails shows its error, not a crash.

    `only` limits it to some widget ids (e.g. one widget embedded in another page).
    `period` is a key of PERIODS: events before it are left out.
    """
    out = []
    widgets = [REGISTRY[i] for i in only if i in REGISTRY] if only else for_scope(scope)
    token = _SINCE.set(since_day(period))
    try:
        for w in widgets:
            try:
                data = w.compute(conn, scope, ref)
            except Exception as e:  # noqa: BLE001  (one broken widget must not break the page)
                data = {"kind": "empty", "message": f"Error: {type(e).__name__}: {e}"}
            out.append((w, data))
    finally:
        _SINCE.reset(token)
    return out


def event_filter(scope: str, ref, alias: str = "e"):
    """A WHERE clause and its parameters that limit events to the scope and the period."""
    if scope == "group":
        where, params = (
            f"{alias}.student_id IN (SELECT id FROM students WHERE group_id = ?)",
            (ref,),
        )
    elif scope == "student":
        where, params = f"{alias}.student_id = ?", (ref,)
    elif scope == "board":
        where, params = f"{alias}.board_id = ?", (ref,)
    else:
        where, params = "1 = 1", ()
    since = _SINCE.get()
    if since:
        where, params = f"{where} AND {alias}.ts_corrected >= ?", (*params, since)
    return where, params
