"""Statistics shown on the dashboard and on the group, student and board pages."""

from . import starter  # noqa: F401  (registers the starter widgets)
from .base import REGISTRY, Widget, for_scope, render_all, widget

__all__ = ["REGISTRY", "Widget", "for_scope", "render_all", "widget"]
