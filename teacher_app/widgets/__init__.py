"""Statistics shown on the dashboard and on the group, student and board pages."""

from . import learning, starter  # noqa: F401  (registers the widgets)
from .base import PERIODS, REGISTRY, Widget, for_scope, render_all, widget

__all__ = ["PERIODS", "REGISTRY", "Widget", "for_scope", "render_all", "widget"]
