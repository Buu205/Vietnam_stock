"""
UI Components Package
=====================
Reusable UI components for Streamlit dashboard.

Modules:
    icons: SVG icon helper functions
"""

from WEBAPP.components.ui.icons import (
    # Main functions
    icon,
    icon_with_text,
    icon_box,
    status_icon,
    rating_icon,
    consensus_icon,

    # Shorthand helpers
    arrow_up,
    arrow_down,
    check,
    x_mark,
    info_icon,
    warning_icon,

    # Constants
    IconSize,
    IconColor,
    ICONS,
)

__all__ = [
    # Main functions
    "icon",
    "icon_with_text",
    "icon_box",
    "status_icon",
    "rating_icon",
    "consensus_icon",

    # Shorthand helpers
    "arrow_up",
    "arrow_down",
    "check",
    "x_mark",
    "info_icon",
    "warning_icon",

    # Constants
    "IconSize",
    "IconColor",
    "ICONS",
]
