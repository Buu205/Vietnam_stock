"""Shared constants and defaults for Streamlit dashboards.

Keep domain-agnostic defaults here. Domain-specific overrides can live under
`streamlit_app/domains/<domain>/constants_<domain>.py` if needed.
"""

# =============================================================================
# CACHE TTL TIERS (seconds)
# =============================================================================
# Use these constants for @st.cache_data(ttl=...) to ensure consistency
CACHE_TTL_HOT = 60        # Real-time data (technical indicators, live prices)
CACHE_TTL_WARM = 300      # Frequently updated (news, intraday prices)
CACHE_TTL_COLD = 3600     # Infrequently updated (fundamentals, forecasts)
CACHE_TTL_STATIC = 86400  # Static data (symbols, sectors, metadata)

# Outlier thresholds (default)
OUTLIERS_DEFAULT = {
    'pe_ratio': 100.0,
    'pb_ratio': 10.0,
    'ev_ebitda_ratio': 100.0,
}

# Colors used across charts
COLORS = {
    'pe': '#1f77b4',
    'pb': '#ff7f0e',
    'ev_ebitda': '#2ca02c',
    'trend': '#555555',
}

# Summary thresholds for Overall Valuation classification
def classify_overall_label(percentile: float) -> str:
    """Return label from percentile value (0..100)."""
    if percentile is None:
        return 'N/A'
    try:
        p = float(percentile)
    except Exception:
        return 'N/A'
    if p >= 80:
        return 'Expensive'
    if p >= 50:
        return 'Above Avg'
    if p >= 30:
        return 'Below Avg'
    return 'Cheap'


