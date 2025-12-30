"""
SVG Icon Helper Module
======================
Centralized SVG icons for Streamlit dashboard.
Based on Heroicons (MIT) - https://heroicons.com

Usage:
    from WEBAPP.components.ui.icons import icon, IconSize

    # Basic usage
    st.markdown(icon("arrow-up"), unsafe_allow_html=True)

    # With custom size and color
    st.markdown(icon("chart-bar", size=32, color="#8B5CF6"), unsafe_allow_html=True)

    # With wrapper (centered, padded)
    st.markdown(icon_box("info", "No data available"), unsafe_allow_html=True)

Rules (UI/UX Pro Max):
- NO emojis - use SVG icons only
- Consistent sizing: 16, 20, 24, 32, 48
- Consistent stroke width: 2 (outline) or fill (solid)
- Color from design system palette
"""

from enum import IntEnum
from typing import Optional


# =============================================================================
# ICON SIZE PRESETS
# =============================================================================

class IconSize(IntEnum):
    """Standard icon sizes."""
    XS = 16   # Inline text icons
    SM = 20   # Button icons
    MD = 24   # Default
    LG = 32   # Card headers
    XL = 48   # Empty states


# =============================================================================
# COLOR PALETTE (from UI/UX Pro Max)
# =============================================================================

class IconColor:
    """Standard icon colors from design system."""
    # Status colors
    SUCCESS = "#22C55E"  # Green - positive, buy
    WARNING = "#F59E0B"  # Amber - hold, caution
    ERROR = "#EF4444"    # Red - negative, sell
    INFO = "#3B82F6"     # Blue - information

    # Brand colors
    PRIMARY = "#8B5CF6"  # Purple - primary accent
    SECONDARY = "#00C9AD"  # Teal - secondary accent

    # Neutral
    MUTED = "#94A3B8"    # Gray - muted/disabled
    DEFAULT = "#E8E8E8"  # Light gray - default


# =============================================================================
# ICON LIBRARY (Heroicons-based)
# =============================================================================

ICONS = {
    # Directional
    "arrow-up": '<path stroke-linecap="round" stroke-linejoin="round" d="M12 19V5M5 12l7-7 7 7"/>',
    "arrow-down": '<path stroke-linecap="round" stroke-linejoin="round" d="M12 5v14M5 12l7 7 7-7"/>',
    "arrow-right": '<path stroke-linecap="round" stroke-linejoin="round" d="M5 12h14M12 5l7 7-7 7"/>',
    "arrow-left": '<path stroke-linecap="round" stroke-linejoin="round" d="M19 12H5M12 19l-7-7 7-7"/>',
    "chevron-up": '<path stroke-linecap="round" stroke-linejoin="round" d="M5 15l7-7 7 7"/>',
    "chevron-down": '<path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/>',
    "trending-up": '<path stroke-linecap="round" stroke-linejoin="round" d="M2 17l6-6 4 4 8-8M14 3h7v7"/>',
    "trending-down": '<path stroke-linecap="round" stroke-linejoin="round" d="M2 7l6 6 4-4 8 8M14 21h7v-7"/>',

    # Charts & Data
    "chart-bar": '<path stroke-linecap="round" stroke-linejoin="round" d="M12 20V10M6 20V4M18 20v-6"/>',
    "chart-pie": '<path stroke-linecap="round" stroke-linejoin="round" d="M10.5 6a7.5 7.5 0 1 0 7.5 7.5h-7.5V6z"/><path stroke-linecap="round" stroke-linejoin="round" d="M13.5 3.5a7.5 7.5 0 0 1 7 7h-7v-7z"/>',
    "chart-line": '<path stroke-linecap="round" stroke-linejoin="round" d="M3 15l4-4 4 4 10-10"/>',
    "presentation": '<path stroke-linecap="round" stroke-linejoin="round" d="M3 3v18h18V3H3zm0 6h18M12 15v-4"/>',

    # Status & Feedback
    "check": '<path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>',
    "check-circle": '<circle cx="12" cy="12" r="10"/><path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4"/>',
    "x-mark": '<path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>',
    "x-circle": '<circle cx="12" cy="12" r="10"/><path stroke-linecap="round" stroke-linejoin="round" d="M15 9l-6 6M9 9l6 6"/>',
    "exclamation": '<path stroke-linecap="round" stroke-linejoin="round" d="M12 9v4m0 4h.01"/>',
    "exclamation-triangle": '<path stroke-linecap="round" stroke-linejoin="round" d="M12 9v4m0 4h.01M12 2L2 22h20L12 2z"/>',
    "info": '<circle cx="12" cy="12" r="10"/><path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4m0 4h.01"/>',
    "question": '<circle cx="12" cy="12" r="10"/><path stroke-linecap="round" stroke-linejoin="round" d="M9 9.5a3 3 0 0 1 5.12 2.13c0 1.63-2.12 2.37-2.12 4.37m0 3h.01"/>',

    # Finance & Business
    "currency-dollar": '<path stroke-linecap="round" stroke-linejoin="round" d="M12 6v12m-3-2.5c.84.47 1.83.74 3 .74 2.21 0 4-1.12 4-2.5s-1.79-2.5-4-2.5-4 1.12-4 2.5m4-7.74c-1.17 0-2.16.27-3 .74"/>',
    "banknotes": '<path stroke-linecap="round" stroke-linejoin="round" d="M2 7h20v10H2V7zm5 5a3 3 0 1 0 6 0 3 3 0 0 0-6 0zm8-2v4"/>',
    "building-office": '<path stroke-linecap="round" stroke-linejoin="round" d="M2 21h20M3 7l9-4 9 4M4 7v14M20 7v14M8 11h2m-2 4h2m4-4h2m-2 4h2m-4-8v12"/>',
    "scale": '<path stroke-linecap="round" stroke-linejoin="round" d="M12 3v3m0 12v3M3 12h3m12 0h3m-4.5-6.5L18 3m-6 6L6 3m6 6l6 6m-6-6l-6 6"/>',

    # Rating & Ranking
    "star": '<path stroke-linecap="round" stroke-linejoin="round" d="M12 2l2.94 6.26L22 9.27l-5 5.14L18.18 22 12 18.27 5.82 22 7 14.41l-5-5.14 7.06-1.01L12 2z"/>',
    "star-solid": '<path fill="currentColor" d="M12 2l2.94 6.26L22 9.27l-5 5.14L18.18 22 12 18.27 5.82 22 7 14.41l-5-5.14 7.06-1.01L12 2z"/>',
    "thumb-up": '<path stroke-linecap="round" stroke-linejoin="round" d="M14 9V5a3 3 0 0 0-6 0v4H4v10h12a3 3 0 0 0 3-3v-4a3 3 0 0 0-3-3h-2z"/>',
    "thumb-down": '<path stroke-linecap="round" stroke-linejoin="round" d="M10 15v4a3 3 0 0 0 6 0v-4h4V5H8a3 3 0 0 0-3 3v4a3 3 0 0 0 3 3h2z"/>',

    # Actions
    "filter": '<path stroke-linecap="round" stroke-linejoin="round" d="M3 4h18l-7 8.5V19l-4 2v-8.5L3 4z"/>',
    "search": '<path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-4.35-4.35M10 17a7 7 0 1 0 0-14 7 7 0 0 0 0 14z"/>',
    "refresh": '<path stroke-linecap="round" stroke-linejoin="round" d="M4 4v6h6M20 20v-6h-6M20 9a9 9 0 0 0-15.64-3M4 15a9 9 0 0 0 15.64 3"/>',
    "download": '<path stroke-linecap="round" stroke-linejoin="round" d="M4 16v4h16v-4M12 4v12m-5-5l5 5 5-5"/>',
    "eye": '<path stroke-linecap="round" stroke-linejoin="round" d="M12 5c-7 0-10 7-10 7s3 7 10 7 10-7 10-7-3-7-10-7z"/><circle cx="12" cy="12" r="3"/>',
    "eye-slash": '<path stroke-linecap="round" stroke-linejoin="round" d="M3 3l18 18M10.5 10.5a3 3 0 0 0 4.24 4.24M12 5c-7 0-10 7-10 7s1 2.5 4 4.5m3.5 1.5c.8.2 1.6.3 2.5.3 7 0 10-7 10-7s-.5-1-1.5-2"/>',

    # UI Elements
    "bars-3": '<path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16"/>',
    "plus": '<path stroke-linecap="round" stroke-linejoin="round" d="M12 5v14M5 12h14"/>',
    "minus": '<path stroke-linecap="round" stroke-linejoin="round" d="M5 12h14"/>',
    "cog": '<circle cx="12" cy="12" r="3"/><path stroke-linecap="round" stroke-linejoin="round" d="M12 2v2m0 16v2M4.93 4.93l1.41 1.41m11.32 11.32l1.41 1.41M2 12h2m16 0h2M6.34 17.66l-1.41 1.41m12.73-12.73l1.41-1.41"/>',
    "table-cells": '<path stroke-linecap="round" stroke-linejoin="round" d="M3 3h18v18H3V3zm0 6h18M3 15h18M9 9v12M15 9v12"/>',

    # Empty states
    "inbox": '<path stroke-linecap="round" stroke-linejoin="round" d="M3 12l3-9h12l3 9M3 12h6l2 2h2l2-2h6M3 12v6h18v-6"/>',
    "document": '<path stroke-linecap="round" stroke-linejoin="round" d="M6 2h8l6 6v12a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2zm8 0v6h6"/>',
    "folder": '<path stroke-linecap="round" stroke-linejoin="round" d="M3 7h6l2-2h10v14H3V7z"/>',
    "calendar": '<path stroke-linecap="round" stroke-linejoin="round" d="M3 6h18v14H3V6zm0 4h18M8 2v4M16 2v4"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6l4 2"/>',

    # Comparison
    "arrows-expand": '<path stroke-linecap="round" stroke-linejoin="round" d="M4 8V4h4M20 8V4h-4M4 16v4h4M20 16v4h-4"/>',
    "scale-balance": '<path stroke-linecap="round" stroke-linejoin="round" d="M12 3v18M3 9l3 6h12l3-6M6 9l-3 6M18 9l3 6"/>',
    "compare": '<path stroke-linecap="round" stroke-linejoin="round" d="M8 4v16M16 4v16M4 8h4M4 16h4M16 8h4M16 16h4"/>',
}


# =============================================================================
# MAIN FUNCTIONS
# =============================================================================

def icon(
    name: str,
    size: int = IconSize.MD,
    color: str = IconColor.DEFAULT,
    stroke_width: float = 2,
    class_name: str = ""
) -> str:
    """
    Generate inline SVG icon HTML.

    Args:
        name: Icon name from ICONS dictionary
        size: Icon size in pixels (default: 24)
        color: Stroke/fill color (default: light gray)
        stroke_width: SVG stroke width (default: 2)
        class_name: Optional CSS class name

    Returns:
        SVG HTML string

    Example:
        >>> icon("arrow-up", size=32, color="#22C55E")
        '<svg width="32" height="32" ...>...</svg>'
    """
    if name not in ICONS:
        # Fallback to question mark for unknown icons
        name = "question"

    path = ICONS[name]
    class_attr = f' class="{class_name}"' if class_name else ''

    return f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{stroke_width}"{class_attr}>{path}</svg>'''


def icon_with_text(
    name: str,
    text: str,
    size: int = IconSize.SM,
    color: str = IconColor.DEFAULT,
    gap: int = 6,
    text_color: Optional[str] = None
) -> str:
    """
    Generate icon + text inline HTML.

    Args:
        name: Icon name
        text: Text to display after icon
        size: Icon size (default: 20)
        color: Icon color
        gap: Gap between icon and text in pixels
        text_color: Text color (default: same as icon)

    Returns:
        HTML string with icon and text

    Example:
        >>> icon_with_text("check", "Completed", color="#22C55E")
    """
    text_color = text_color or color
    return f'''<span style="display: inline-flex; align-items: center; gap: {gap}px;">
        {icon(name, size=size, color=color)}
        <span style="color: {text_color};">{text}</span>
    </span>'''


def icon_box(
    name: str,
    message: str,
    icon_size: int = IconSize.LG,
    icon_color: str = IconColor.PRIMARY,
    bg_color: str = "rgba(139, 92, 246, 0.08)",
    border_color: str = "rgba(139, 92, 246, 0.2)",
    text_color: str = IconColor.MUTED
) -> str:
    """
    Generate centered icon box for empty states.

    Args:
        name: Icon name
        message: Message text below icon
        icon_size: Icon size (default: 32)
        icon_color: Icon stroke color
        bg_color: Box background color
        border_color: Box border color
        text_color: Message text color

    Returns:
        HTML string with styled box

    Example:
        >>> st.markdown(icon_box("inbox", "No data available"), unsafe_allow_html=True)
    """
    return f'''
    <div style="background: {bg_color}; border: 1px solid {border_color}; border-radius: 12px; padding: 24px; text-align: center;">
        {icon(name, size=icon_size, color=icon_color)}
        <div style="color: {text_color}; font-size: 0.9rem; margin-top: 8px;">{message}</div>
    </div>
    '''


def status_icon(status: str, size: int = IconSize.SM) -> str:
    """
    Get status icon based on status string.

    Args:
        status: One of "success", "warning", "error", "info", "neutral"
        size: Icon size

    Returns:
        SVG HTML with appropriate icon and color
    """
    status_map = {
        "success": ("check-circle", IconColor.SUCCESS),
        "warning": ("exclamation-triangle", IconColor.WARNING),
        "error": ("x-circle", IconColor.ERROR),
        "info": ("info", IconColor.INFO),
        "neutral": ("minus", IconColor.MUTED),
        # Aliases
        "buy": ("trending-up", IconColor.SUCCESS),
        "sell": ("trending-down", IconColor.ERROR),
        "hold": ("minus", IconColor.WARNING),
        "up": ("arrow-up", IconColor.SUCCESS),
        "down": ("arrow-down", IconColor.ERROR),
        "positive": ("arrow-up", IconColor.SUCCESS),
        "negative": ("arrow-down", IconColor.ERROR),
    }

    icon_name, color = status_map.get(status.lower(), ("question", IconColor.MUTED))
    return icon(icon_name, size=size, color=color)


def rating_icon(rating: str, size: int = IconSize.SM) -> str:
    """
    Get rating icon for BSC ratings.

    Args:
        rating: One of "STRONG BUY", "BUY", "HOLD", "SELL", "STRONG SELL"
        size: Icon size

    Returns:
        SVG HTML with appropriate icon and color
    """
    rating_map = {
        "STRONG BUY": ("star-solid", IconColor.SECONDARY),  # Teal
        "BUY": ("thumb-up", IconColor.SUCCESS),
        "HOLD": ("minus", IconColor.WARNING),
        "SELL": ("thumb-down", "#F97316"),  # Orange
        "STRONG SELL": ("x-circle", IconColor.ERROR),
    }

    icon_name, color = rating_map.get(rating.upper(), ("question", IconColor.MUTED))
    return icon(icon_name, size=size, color=color)


# =============================================================================
# CONSENSUS ICONS (for Phase 3)
# =============================================================================

def consensus_icon(status: str, size: int = IconSize.SM) -> str:
    """
    Get consensus status icon for BSC vs VCI comparison.

    Args:
        status: One of "ALIGNED", "BSC_BULL", "VCI_BULL", "DIVERGENT"
        size: Icon size

    Returns:
        SVG HTML with appropriate icon and color
    """
    consensus_map = {
        "ALIGNED": ("check-circle", "#00C9AD"),    # Teal
        "BSC_BULL": ("trending-up", "#3B82F6"),    # Blue
        "VCI_BULL": ("trending-up", "#F59E0B"),    # Orange
        "DIVERGENT": ("exclamation-triangle", "#EF4444"),  # Red
        "NO_VCI_DATA": ("question", IconColor.MUTED),
    }

    icon_name, color = consensus_map.get(status.upper(), ("question", IconColor.MUTED))
    return icon(icon_name, size=size, color=color)


# =============================================================================
# SHORTHAND HELPERS
# =============================================================================

def arrow_up(size: int = IconSize.SM, color: str = IconColor.SUCCESS) -> str:
    """Quick arrow up icon (green)."""
    return icon("arrow-up", size=size, color=color)


def arrow_down(size: int = IconSize.SM, color: str = IconColor.ERROR) -> str:
    """Quick arrow down icon (red)."""
    return icon("arrow-down", size=size, color=color)


def check(size: int = IconSize.SM, color: str = IconColor.SUCCESS) -> str:
    """Quick check icon (green)."""
    return icon("check", size=size, color=color)


def x_mark(size: int = IconSize.SM, color: str = IconColor.ERROR) -> str:
    """Quick x-mark icon (red)."""
    return icon("x-mark", size=size, color=color)


def info_icon(size: int = IconSize.SM, color: str = IconColor.INFO) -> str:
    """Quick info icon (blue)."""
    return icon("info", size=size, color=color)


def warning_icon(size: int = IconSize.SM, color: str = IconColor.WARNING) -> str:
    """Quick warning icon (amber)."""
    return icon("exclamation-triangle", size=size, color=color)
