"""WEBAPP Core module - styles, config, theme, and utilities."""

from WEBAPP.core.styles import (
    get_page_style,
    get_chart_layout,
    CHART_COLORS,
    BAR_COLORS,
    DISTRIBUTION_COLORS,
    ASSESSMENT_COLORS,
    BAND_COLORS,
    render_styled_table,
    get_table_style,
    render_valuation_legend,
    render_valuation_assessment,
)

from WEBAPP.core.theme import (
    DARK_THEME,
    CHART_PALETTE,
    TRADING_COLORS,
    SEMANTIC,
    TYPOGRAPHY,
    SPACING,
    RADIUS,
    SHADOWS,
    GLASS,
    PURPLE,
    CYAN,
    AMBER,
)

__all__ = [
    # Styles
    "get_page_style",
    "get_chart_layout",
    "CHART_COLORS",
    "BAR_COLORS",
    "DISTRIBUTION_COLORS",
    "ASSESSMENT_COLORS",
    "BAND_COLORS",
    "render_styled_table",
    "get_table_style",
    "render_valuation_legend",
    "render_valuation_assessment",
    # Theme
    "DARK_THEME",
    "CHART_PALETTE",
    "TRADING_COLORS",
    "SEMANTIC",
    "TYPOGRAPHY",
    "SPACING",
    "RADIUS",
    "SHADOWS",
    "GLASS",
    "PURPLE",
    "CYAN",
    "AMBER",
]
