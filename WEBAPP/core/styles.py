"""
Dashboard Styles - Midnight Financial Terminal
===============================================

Premium financial dashboard with brand-aligned aesthetics.

Design Direction:
- Aesthetic: MIDNIGHT TERMINAL - Deep navy/black with high contrast
- Charts: Brand Teal (#009B87) as primary chart color
- Typography: Geist (display) + IBM Plex Sans (body) + IBM Plex Mono (data)
- Accents: Brand colors only - Blue #295CA9, Teal #009B87, Gold #FFC132

Brand Colors (OFFICIAL):
- Primary Blue: #295CA9 (R:41 G:92 B:169)
- Accent Teal: #009B87 (R:0 G:155 B:135) - PRIMARY CHART COLOR
- Warning Gold: #FFC132 (R:255 G:193 B:50)

Usage:
    from WEBAPP.core.styles import get_page_style, get_chart_layout

Created: 2025-12-16
Updated: 2025-12-16 - Brand alignment redesign
"""

from WEBAPP.core.theme import (
    BRAND, DARK_THEME, CHART_PALETTE,
    SEMANTIC, TYPOGRAPHY, SPACING, RADIUS, SHADOWS
)


def get_page_style() -> str:
    """
    Get premium page-level CSS styling.

    Design: Midnight Terminal
    - Background: Deep black-navy gradient
    - Text: High contrast whites and silvers
    - Charts: Brand teal (#009B87)
    - Accents: Gold for highlights, Blue for secondary

    Returns:
        Complete CSS string for Streamlit markdown injection
    """
    return """
<style>
    /* ============================================================
       FONTS - Financial Terminal Typography
       ============================================================ */
    @import url('https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600;700&family=IBM+Plex+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

    :root {
        /* ========== BRAND COLORS (OFFICIAL) ========== */
        --brand-blue: #295CA9;
        --brand-teal: #009B87;
        --brand-gold: #FFC132;

        /* ========== EXTENDED BRAND PALETTE ========== */
        --teal-light: #00C9AD;
        --teal-dark: #007A6B;
        --blue-light: #4A7BC8;
        --blue-dark: #1E4580;
        --gold-light: #FFD666;
        --gold-dark: #E6A000;

        /* ========== MIDNIGHT THEME ========== */
        --bg-void: #04080F;
        --bg-deep: #0A1118;
        --bg-surface: #101820;
        --bg-elevated: #182028;
        --bg-hover: #1E2830;

        /* ========== TEXT - HIGH CONTRAST (WCAG AA Compliant) ========== */
        --text-white: #FFFFFF;      /* 18.1:1 contrast */
        --text-bright: #F0F4F8;     /* 15.2:1 contrast */
        --text-primary: #E2E8F0;    /* 12.8:1 contrast */
        --text-secondary: #CBD5E1;  /* 8.9:1 contrast - was #A0AEC0 */
        --text-muted: #94A3B8;      /* 5.6:1 contrast - was #718096 */
        --text-dim: #64748B;        /* 4.0:1 contrast - was #4A5568 */

        /* ========== SEMANTIC COLORS ========== */
        --positive: #009B87;
        --positive-light: #00C9AD;
        --negative: #E53E3E;
        --negative-light: #FC8181;
        --warning: #FFC132;
        --info: #295CA9;

        /* ========== BORDERS & EFFECTS ========== */
        --border-subtle: rgba(160, 174, 192, 0.08);
        --border-medium: rgba(160, 174, 192, 0.15);
        --border-accent: rgba(0, 155, 135, 0.4);
        --glow-teal: 0 0 30px rgba(0, 155, 135, 0.2);
        --glow-gold: 0 0 20px rgba(255, 193, 50, 0.15);

        /* ========== TYPOGRAPHY ========== */
        --font-display: 'Geist', -apple-system, BlinkMacSystemFont, sans-serif;
        --font-body: 'IBM Plex Sans', -apple-system, sans-serif;
        --font-mono: 'IBM Plex Mono', 'SF Mono', monospace;
    }

    /* ============================================================
       BASE - MIDNIGHT VOID BACKGROUND
       ============================================================ */
    .stApp {
        background: linear-gradient(170deg,
            var(--bg-void) 0%,
            var(--bg-deep) 30%,
            var(--bg-surface) 100%
        );
        min-height: 100vh;
    }

    .block-container {
        padding: 2.5rem 4rem 5rem 4rem !important;
        max-width: 1800px;
    }

    * {
        font-family: var(--font-body);
    }

    /* ============================================================
       TYPOGRAPHY - CRISP & READABLE
       ============================================================ */
    h1, h2, h3, .stTitle, .stSubheader {
        font-family: var(--font-display) !important;
        font-weight: 600 !important;
        letter-spacing: -0.025em;
    }

    /* Page Title - Brand Gradient */
    h1 {
        font-size: 2.75rem !important;
        font-weight: 700 !important;
        color: var(--text-white) !important;
        background: linear-gradient(135deg,
            var(--text-white) 0%,
            var(--brand-teal) 50%,
            var(--teal-light) 100%
        );
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.25rem !important;
        text-shadow: 0 0 60px rgba(0, 155, 135, 0.3);
    }

    /* Section Headers - Uppercase Terminal Style */
    h3 {
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        color: var(--text-bright) !important;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin-bottom: 1.25rem !important;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid var(--border-subtle);
        position: relative;
    }

    h3::after {
        content: '';
        position: absolute;
        bottom: -1px;
        left: 0;
        width: 40px;
        height: 2px;
        background: var(--brand-teal);
    }

    /* Body Text */
    p, span, div {
        color: var(--text-primary);
    }

    /* Subtitle Enhancement */
    .stMarkdown p:first-child {
        font-size: 1.1rem;
        color: var(--text-secondary);
        font-weight: 400;
    }

    /* Strong text - Gold accent */
    strong, b {
        color: var(--text-bright);
        font-weight: 600;
    }

    /* ============================================================
       METRIC CARDS - GLASS MORPHISM
       ============================================================ */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg,
            rgba(16, 24, 32, 0.9) 0%,
            rgba(24, 32, 40, 0.8) 100%
        );
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid var(--border-subtle);
        border-radius: 16px;
        padding: 1.5rem 1.75rem !important;
        transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        position: relative;
        overflow: hidden;
    }

    /* Top accent bar */
    [data-testid="stMetric"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, var(--brand-teal), var(--teal-light));
        opacity: 0.6;
    }

    /* Corner glow */
    [data-testid="stMetric"]::after {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 100%;
        height: 100%;
        background: radial-gradient(circle, rgba(0, 155, 135, 0.08) 0%, transparent 70%);
        pointer-events: none;
    }

    [data-testid="stMetric"]:hover {
        border-color: var(--border-accent);
        box-shadow: var(--glow-teal);
        transform: translateY(-4px);
    }

    [data-testid="stMetric"]:hover::before {
        opacity: 1;
    }

    /* Metric Label - Secondary uppercase (improved contrast) */
    [data-testid="stMetricLabel"] {
        font-family: var(--font-body) !important;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        color: var(--text-secondary) !important;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }

    /* Metric Value - Large monospace */
    [data-testid="stMetricValue"] {
        font-family: var(--font-mono) !important;
        font-size: 2rem !important;
        font-weight: 600 !important;
        color: var(--text-white) !important;
        letter-spacing: -0.02em;
        text-shadow: 0 0 30px rgba(255, 255, 255, 0.1);
    }

    /* Metric Delta - Color coded */
    [data-testid="stMetricDelta"] {
        font-family: var(--font-mono) !important;
        font-size: 0.85rem !important;
        font-weight: 500;
    }

    [data-testid="stMetricDelta"] svg {
        stroke-width: 3;
    }

    /* ============================================================
       SIDEBAR - COMMAND PANEL
       ============================================================ */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg,
            var(--bg-deep) 0%,
            var(--bg-surface) 100%
        ) !important;
        border-right: 1px solid var(--border-subtle);
    }

    [data-testid="stSidebar"]::before {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 1px;
        height: 100%;
        background: linear-gradient(180deg, var(--brand-teal), transparent);
        opacity: 0.3;
    }

    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2 {
        font-size: 12px !important;
        font-weight: 600 !important;
        color: var(--text-muted) !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.5rem;
    }

    /* Sidebar inputs - compact */
    [data-testid="stSidebar"] .stSelectbox > div > div,
    [data-testid="stSidebar"] .stTextInput > div > div {
        background: var(--bg-elevated) !important;
        border: 1px solid var(--border-medium) !important;
        border-radius: 6px;
        color: var(--text-primary);
        font-size: 13px !important;
        min-height: 36px !important;
    }

    /* Sidebar selectbox text */
    [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] span,
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div {
        font-size: 13px !important;
    }

    /* Sidebar labels */
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stTextInput label,
    [data-testid="stSidebar"] .stSlider label {
        font-size: 12px !important;
        color: var(--text-muted) !important;
        margin-bottom: 0.25rem !important;
    }

    [data-testid="stSidebar"] .stSelectbox > div > div:hover,
    [data-testid="stSidebar"] .stTextInput > div > div:hover {
        border-color: var(--brand-teal) !important;
    }

    [data-testid="stSidebar"] .stSelectbox > div > div:focus-within {
        border-color: var(--brand-teal) !important;
        box-shadow: 0 0 0 2px rgba(0, 155, 135, 0.2);
    }

    /* Slider - Teal accent */
    [data-testid="stSidebar"] .stSlider > div > div > div {
        background: var(--brand-teal) !important;
    }

    [data-testid="stSidebar"] .stSlider > div > div > div > div {
        background: var(--teal-light) !important;
    }

    /* ============================================================
       NAVIGATION - COMPACT & UNIFIED (13px base font)
       ============================================================ */
    /* Navigation section headers (Fundamental, Analysis) */
    [data-testid="stSidebar"] [data-testid="stSidebarNavSeparator"],
    [data-testid="stSidebar"] span[data-testid="stSidebarNavSeparator"] {
        color: var(--text-muted) !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        padding: 0.4rem 0 0.2rem 0;
        margin-top: 0.5rem;
    }

    /* Navigation links (page names) - COMPACT & READABLE */
    [data-testid="stSidebar"] a,
    [data-testid="stSidebar"] [data-testid="stSidebarNavLink"],
    [data-testid="stSidebar"] nav a,
    [data-testid="stSidebar"] nav a span,
    [data-testid="stSidebarNavLink"] span {
        color: #E2E8F0 !important;
        font-size: 13px !important;  /* Unified 13px */
        font-weight: 500 !important;
        padding: 0.4rem 0.6rem !important;  /* Compact padding */
        border-radius: 6px;
        transition: all 0.15s ease;
        text-decoration: none !important;
        line-height: 1.3 !important;
    }

    [data-testid="stSidebar"] a:hover,
    [data-testid="stSidebar"] [data-testid="stSidebarNavLink"]:hover,
    [data-testid="stSidebar"] nav a:hover {
        color: #FFFFFF !important;
        background: var(--bg-hover) !important;
    }

    /* Active navigation link - Teal highlight */
    [data-testid="stSidebar"] a[aria-current="page"],
    [data-testid="stSidebar"] [data-testid="stSidebarNavLink"][aria-current="page"],
    [data-testid="stSidebar"] a[aria-current="page"] span,
    [data-testid="stSidebarNavLink"][aria-current="page"] span {
        color: #00C9AD !important;
        background: rgba(0, 155, 135, 0.12) !important;
        font-weight: 600 !important;
    }

    /* Navigation container - tighter spacing */
    [data-testid="stSidebar"] nav {
        padding: 0.25rem 0;
    }

    [data-testid="stSidebar"] nav ul {
        gap: 2px !important;
    }

    /* Navigation icons - compact 14px */
    [data-testid="stSidebar"] [data-testid="stSidebarNavLink"] svg,
    [data-testid="stSidebar"] nav a svg,
    [data-testid="stSidebarNavLink"] [data-testid="stIconMaterial"],
    [data-testid="stSidebar"] a [data-testid="stIconMaterial"] {
        width: 14px !important;
        height: 14px !important;
        min-width: 14px !important;
        margin-right: 6px !important;
        flex-shrink: 0 !important;
    }

    /* Navigation link emoji icons - compact 12px */
    [data-testid="stSidebar"] [data-testid="stSidebarNavLink"] span[data-testid="stIconEmoji"],
    [data-testid="stSidebar"] nav a span:first-child {
        font-size: 12px !important;
        margin-right: 6px !important;
        flex-shrink: 0 !important;
        line-height: 1 !important;
    }

    /* Ensure nav link layout */
    [data-testid="stSidebarNavLink"] {
        display: flex !important;
        align-items: center !important;
        overflow: visible !important;
        white-space: nowrap !important;
        min-height: 32px !important;  /* Consistent height */
    }

    /* Navigation separator text */
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: var(--text-secondary) !important;
        font-size: 13px !important;
    }

    /* ============================================================
       TABS - SEGMENTED CONTROL
       ============================================================ */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--bg-elevated);
        border-radius: 12px;
        padding: 5px;
        gap: 4px;
        border: 1px solid var(--border-subtle);
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border-radius: 8px;
        padding: 0.65rem 1.75rem;
        font-family: var(--font-body);
        font-weight: 500;
        font-size: 0.875rem;
        color: var(--text-secondary);
        transition: all 0.25s ease;
        border: none;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: var(--text-primary);
        background: var(--bg-hover) !important;
    }

    .stTabs [aria-selected="true"] {
        background: var(--brand-teal) !important;
        color: var(--bg-void) !important;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(0, 155, 135, 0.3);
    }

    .stTabs [data-baseweb="tab-highlight"],
    .stTabs [data-baseweb="tab-border"] {
        display: none;
    }

    /* ============================================================
       RADIO BUTTONS - PILL STYLE
       ============================================================ */
    .stRadio > div {
        gap: 0.5rem;
    }

    .stRadio > div > label {
        background: var(--bg-elevated);
        border: 1px solid var(--border-subtle);
        border-radius: 8px;
        padding: 0.5rem 1rem;
        cursor: pointer;
        transition: all 0.2s ease;
    }

    .stRadio > div > label:hover {
        border-color: var(--brand-teal);
        background: var(--bg-hover);
    }

    .stRadio > div > label[data-checked="true"] {
        background: var(--brand-teal);
        border-color: var(--brand-teal);
        color: var(--bg-void);
    }

    /* ============================================================
       BUTTONS - BRAND GRADIENT
       ============================================================ */
    .stButton > button {
        background: linear-gradient(135deg, var(--brand-teal), var(--teal-dark)) !important;
        border: none !important;
        border-radius: 10px;
        font-family: var(--font-body);
        font-weight: 600;
        font-size: 0.9rem;
        padding: 0.7rem 1.75rem;
        color: var(--text-white) !important;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        box-shadow: 0 4px 12px rgba(0, 155, 135, 0.25);
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 155, 135, 0.35), var(--glow-teal);
    }

    .stButton > button:active {
        transform: translateY(0);
    }

    /* Download Button - Outlined */
    .stDownloadButton > button {
        background: transparent !important;
        border: 1px solid var(--border-medium) !important;
        color: var(--text-primary) !important;
    }

    .stDownloadButton > button:hover {
        background: var(--bg-hover) !important;
        border-color: var(--brand-teal) !important;
        color: var(--brand-teal) !important;
    }

    /* ============================================================
       DATAFRAMES - DATA GRID
       ============================================================ */
    .stDataFrame {
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid var(--border-subtle);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }

    .stDataFrame [data-testid="stDataFrameResizable"] {
        background: var(--bg-surface);
    }

    .stDataFrame th {
        background: var(--bg-deep) !important;
        font-family: var(--font-body) !important;
        font-weight: 600 !important;
        font-size: 0.75rem !important;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--text-secondary) !important;
        padding: 1.1rem 1.25rem !important;
        border-bottom: 1px solid var(--border-medium) !important;
    }

    .stDataFrame td {
        font-family: var(--font-mono) !important;
        font-size: 0.875rem !important;
        color: var(--text-primary) !important;
        padding: 0.9rem 1.25rem !important;
        border-bottom: 1px solid var(--border-subtle) !important;
    }

    .stDataFrame tr:hover td {
        background: var(--bg-hover) !important;
    }

    /* Alternate row coloring */
    .stDataFrame tbody tr:nth-child(even) td {
        background: rgba(10, 17, 24, 0.5);
    }

    /* ============================================================
       CHARTS - ELEVATED CONTAINER WITH PROPER SIZING
       ============================================================ */
    .stPlotlyChart {
        background: linear-gradient(135deg,
            var(--bg-surface) 0%,
            var(--bg-elevated) 100%
        );
        border-radius: 16px;
        padding: 1rem;
        border: 1px solid var(--border-subtle);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        width: 100% !important;
        max-width: 100% !important;
        overflow: hidden;
    }

    /* Fix Plotly chart container to fit parent */
    .stPlotlyChart > div {
        width: 100% !important;
        max-width: 100% !important;
    }

    /* Ensure SVG and main-svg scale correctly */
    .stPlotlyChart .js-plotly-plot,
    .stPlotlyChart .plotly,
    .stPlotlyChart .plot-container {
        width: 100% !important;
        max-width: 100% !important;
    }

    /* Fix chart responsiveness in columns */
    [data-testid="column"] .stPlotlyChart {
        min-width: 0;  /* Allow shrinking in flex container */
    }

    /* Ensure modebar doesn't overflow */
    .stPlotlyChart .modebar-container {
        position: absolute !important;
        right: 5px !important;
        top: 5px !important;
    }

    /* ============================================================
       INFO/WARNING/ERROR BOXES
       ============================================================ */
    .stAlert {
        border-radius: 12px;
        border-left-width: 4px;
    }

    /* Info - Blue */
    .stAlert[data-baseweb="notification"][kind="info"] {
        background: rgba(41, 92, 169, 0.1);
        border-left-color: var(--brand-blue);
    }

    /* Success - Teal */
    .stAlert[data-baseweb="notification"][kind="success"] {
        background: rgba(0, 155, 135, 0.1);
        border-left-color: var(--brand-teal);
    }

    /* Warning - Gold */
    .stAlert[data-baseweb="notification"][kind="warning"] {
        background: rgba(255, 193, 50, 0.1);
        border-left-color: var(--brand-gold);
    }

    /* Error - Red */
    .stAlert[data-baseweb="notification"][kind="error"] {
        background: rgba(229, 62, 62, 0.1);
        border-left-color: var(--negative);
    }

    /* ============================================================
       SELECTBOX & MULTISELECT
       ============================================================ */
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        background: var(--bg-elevated) !important;
        border: 1px solid var(--border-medium) !important;
        border-radius: 10px;
        color: var(--text-primary);
    }

    .stSelectbox > div > div:hover,
    .stMultiSelect > div > div:hover {
        border-color: var(--brand-teal) !important;
    }

    .stMultiSelect [data-baseweb="tag"] {
        background: var(--brand-teal) !important;
        border-radius: 6px;
        color: var(--bg-void);
    }

    /* Dropdown Menu (Popover) - CRITICAL FIX FOR WHITE BACKGROUND */
    [data-baseweb="popover"],
    [data-baseweb="popover"] > div,
    div[data-baseweb="popover"] {
        background: #101820 !important;
        background-color: #101820 !important;
        border: 1px solid rgba(160, 174, 192, 0.15) !important;
        border-radius: 10px !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6) !important;
    }

    /* Dropdown List Container */
    [data-baseweb="menu"],
    [data-baseweb="listbox"],
    ul[role="listbox"],
    div[data-baseweb="menu"],
    div[data-baseweb="listbox"] {
        background: #101820 !important;
        background-color: #101820 !important;
        border-radius: 10px !important;
    }

    /* Dropdown Options - ALL VARIATIONS */
    [data-baseweb="menu"] li,
    [data-baseweb="listbox"] li,
    [role="option"],
    ul[role="listbox"] li,
    div[data-baseweb="select"] li,
    .st-emotion-cache-1n76uvr,
    .st-emotion-cache-r421ms {
        background: #101820 !important;
        background-color: #101820 !important;
        color: #E2E8F0 !important;
        font-family: var(--font-body) !important;
        padding: 0.75rem 1rem !important;
        transition: all 0.15s ease !important;
    }

    /* Dropdown Option Hover */
    [data-baseweb="menu"] li:hover,
    [data-baseweb="listbox"] li:hover,
    [role="option"]:hover,
    ul[role="listbox"] li:hover,
    div[data-baseweb="select"] li:hover {
        background: #1E2830 !important;
        background-color: #1E2830 !important;
        color: #FFFFFF !important;
    }

    /* Dropdown Option Selected/Highlighted */
    [data-baseweb="menu"] li[aria-selected="true"],
    [data-baseweb="listbox"] li[aria-selected="true"],
    [role="option"][aria-selected="true"],
    [data-highlighted="true"],
    ul[role="listbox"] li[aria-selected="true"] {
        background: #009B87 !important;
        background-color: #009B87 !important;
        color: #04080F !important;
        font-weight: 500 !important;
    }

    /* Fix for BaseWeb select dropdown */
    div[data-baseweb="select"] ul,
    div[data-baseweb="select"] > div > div {
        background: #101820 !important;
        background-color: #101820 !important;
    }

    /* Override any white backgrounds in dropdowns */
    .stSelectbox [data-baseweb="popover"] *,
    .stMultiSelect [data-baseweb="popover"] * {
        background-color: inherit;
    }

    /* Force dark background on option wrapper */
    [data-baseweb="menu"] > div,
    [data-baseweb="listbox"] > div {
        background: #101820 !important;
    }

    /* ============================================================
       HORIZONTAL RULE - GRADIENT FADE
       ============================================================ */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg,
            transparent 0%,
            var(--border-medium) 20%,
            var(--brand-teal) 50%,
            var(--border-medium) 80%,
            transparent 100%
        );
        margin: 2.5rem 0;
        opacity: 0.5;
    }

    /* ============================================================
       FOOTER CAPTION - Improved contrast
       ============================================================ */
    .stCaption {
        font-family: var(--font-mono) !important;
        font-size: 0.75rem !important;
        color: var(--text-muted) !important;
        letter-spacing: 0.03em;
    }

    /* ============================================================
       ANIMATIONS - SUBTLE ENTRANCE
       ============================================================ */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(24px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes glowPulse {
        0%, 100% { box-shadow: 0 0 20px rgba(0, 155, 135, 0.1); }
        50% { box-shadow: 0 0 30px rgba(0, 155, 135, 0.2); }
    }

    /* Staggered entrance */
    [data-testid="stMetric"]:nth-child(1) { animation: fadeInUp 0.6s ease 0.1s both; }
    [data-testid="stMetric"]:nth-child(2) { animation: fadeInUp 0.6s ease 0.2s both; }
    [data-testid="stMetric"]:nth-child(3) { animation: fadeInUp 0.6s ease 0.3s both; }
    [data-testid="stMetric"]:nth-child(4) { animation: fadeInUp 0.6s ease 0.4s both; }

    .stPlotlyChart {
        animation: fadeInUp 0.7s ease 0.4s both;
    }

    .stDataFrame {
        animation: fadeInUp 0.7s ease 0.5s both;
    }

    /* ============================================================
       DATA TABLE / DATAFRAME - PROFESSIONAL STYLING
       Targets Streamlit's Glide Data Grid (canvas-based)
       ============================================================ */

    /* Main DataFrame container wrapper */
    [data-testid="stDataFrame"],
    .stDataFrame {
        background: linear-gradient(180deg, #101820 0%, #0A1118 100%) !important;
        border: 1px solid rgba(0, 155, 135, 0.3) !important;
        border-radius: 12px !important;
        overflow: hidden !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4) !important;
        padding: 0 !important;
    }

    /* Inner iframe/div container */
    [data-testid="stDataFrame"] > div,
    .stDataFrame > div {
        background: transparent !important;
        border-radius: 12px !important;
    }

    /* Glide Data Grid container - the canvas wrapper */
    [data-testid="stDataFrame"] iframe,
    .stDataFrame iframe {
        background: #101820 !important;
        border: none !important;
        border-radius: 10px !important;
    }

    /* Target the inner glide-data-grid element */
    [data-testid="glideDataEditor"],
    .dvn-scroller,
    .dvn-underlay {
        background: #101820 !important;
    }

    /* DataFrame resizable container */
    [data-testid="stDataFrameResizable"] {
        background: linear-gradient(180deg, #101820 0%, #0A1118 100%) !important;
        border: 1px solid rgba(0, 155, 135, 0.25) !important;
        border-radius: 10px !important;
        overflow: hidden !important;
    }

    /* Toolbar (search, fullscreen buttons) */
    [data-testid="stDataFrameToolbar"],
    [data-testid="stElementToolbar"] {
        background: rgba(16, 24, 32, 0.9) !important;
        border-bottom: 1px solid rgba(0, 155, 135, 0.2) !important;
    }

    [data-testid="stDataFrameToolbar"] button,
    [data-testid="stElementToolbar"] button {
        color: #009B87 !important;
        background: transparent !important;
        border: none !important;
    }

    [data-testid="stDataFrameToolbar"] button:hover,
    [data-testid="stElementToolbar"] button:hover {
        color: #00C9AD !important;
        background: rgba(0, 155, 135, 0.15) !important;
    }

    /* Column headers in Glide Data Grid - injected via CSS variables */
    .stDataFrame [class*="header"],
    .dvn-scroll-inner [class*="header"] {
        background: rgba(0, 155, 135, 0.1) !important;
        color: #009B87 !important;
        font-family: 'Geist', 'Inter', sans-serif !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.03em !important;
    }

    /* Cell styling - Glide Data Grid uses canvas, limited CSS options */
    .stDataFrame [class*="cell"],
    .dvn-scroll-inner [class*="cell"] {
        color: #E2E8F0 !important;
        font-family: 'IBM Plex Mono', monospace !important;
    }

    /* Search input in toolbar */
    [data-testid="stDataFrameToolbar"] input {
        background: rgba(16, 24, 32, 0.95) !important;
        border: 1px solid rgba(0, 155, 135, 0.3) !important;
        color: #E2E8F0 !important;
        border-radius: 6px !important;
    }

    [data-testid="stDataFrameToolbar"] input::placeholder {
        color: #64748B !important;  /* text-dim for placeholders */
    }

    /* Scrollbar inside DataFrame */
    [data-testid="stDataFrame"] ::-webkit-scrollbar,
    .stDataFrame ::-webkit-scrollbar {
        width: 8px !important;
        height: 8px !important;
    }

    [data-testid="stDataFrame"] ::-webkit-scrollbar-track,
    .stDataFrame ::-webkit-scrollbar-track {
        background: #0A1118 !important;
    }

    [data-testid="stDataFrame"] ::-webkit-scrollbar-thumb,
    .stDataFrame ::-webkit-scrollbar-thumb {
        background: rgba(0, 155, 135, 0.4) !important;
        border-radius: 4px !important;
    }

    [data-testid="stDataFrame"] ::-webkit-scrollbar-thumb:hover,
    .stDataFrame ::-webkit-scrollbar-thumb:hover {
        background: rgba(0, 155, 135, 0.6) !important;
    }

    /* Fullscreen mode styling */
    [data-testid="stDataFrame"][data-fullscreen="true"],
    .stDataFrame[data-fullscreen="true"] {
        background: #0A1118 !important;
        border: 2px solid #009B87 !important;
    }

    /* Loading state */
    [data-testid="stDataFrame"] [data-testid="stSpinner"],
    .stDataFrame [data-testid="stSpinner"] {
        color: #009B87 !important;
    }

    /* ============================================================
       SCROLLBAR - MINIMAL
       ============================================================ */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }

    ::-webkit-scrollbar-track {
        background: var(--bg-deep);
    }

    ::-webkit-scrollbar-thumb {
        background: var(--border-medium);
        border-radius: 3px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-dim);
    }

    /* ============================================================
       RESPONSIVE
       ============================================================ */
    @media (max-width: 768px) {
        .block-container {
            padding: 1.5rem 1rem !important;
        }

        h1 {
            font-size: 2rem !important;
        }

        [data-testid="stMetricValue"] {
            font-size: 1.5rem !important;
        }
    }
</style>
"""


def get_chart_layout(title: str = "", height: int = 400) -> dict:
    """
    Get consistent Plotly chart layout - Brand Teal theme.

    Charts use #009B87 (Brand Teal) as primary color.
    WCAG AA compliant text colors for readability.

    Args:
        title: Chart title
        height: Chart height in pixels

    Returns:
        Plotly layout dict
    """
    return {
        'title': {
            'text': title,
            'font': {'family': 'Geist, sans-serif', 'size': 15, 'color': '#CBD5E1'},  # Improved contrast
            'x': 0,
            'xanchor': 'left'
        },
        'height': height,
        'autosize': True,  # Enable responsive auto-sizing
        'margin': {'l': 50, 'r': 30, 't': 50, 'b': 50, 'pad': 4},
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'font': {
            'family': 'IBM Plex Mono, monospace',
            'size': 11,
            'color': '#CBD5E1'  # Improved contrast
        },
        'xaxis': {
            'gridcolor': 'rgba(160, 174, 192, 0.08)',
            'zerolinecolor': 'rgba(160, 174, 192, 0.15)',
            'tickfont': {'size': 10, 'color': '#94A3B8'},  # Improved contrast
            'linecolor': 'rgba(160, 174, 192, 0.1)',
            'tickangle': -45,  # Rotate labels to prevent overlap
            'automargin': True,  # Auto adjust margins for labels
            'type': 'category',  # Treat as categorical to preserve order
            'categoryorder': 'array',  # Use array order
            'nticks': 10,  # Limit number of ticks shown
        },
        'yaxis': {
            'gridcolor': 'rgba(160, 174, 192, 0.08)',
            'zerolinecolor': 'rgba(160, 174, 192, 0.15)',
            'tickfont': {'size': 11, 'color': '#94A3B8'},  # Improved contrast
            'linecolor': 'rgba(160, 174, 192, 0.1)',
            'automargin': True,  # Auto adjust margins for labels
            'fixedrange': False,  # Allow zoom/pan
        },
        'legend': {
            'font': {'size': 11, 'color': '#E2E8F0'},  # Primary text for readability
            'bgcolor': 'rgba(0,0,0,0)',
            'bordercolor': 'rgba(0,0,0,0)',
        },
        'hoverlabel': {
            'bgcolor': '#101820',
            'bordercolor': '#009B87',
            'font': {'family': 'IBM Plex Mono', 'size': 12, 'color': '#F0F4F8'}
        }
    }


# ============================================================
# CHART COLORS - BRAND ALIGNED
# ============================================================

# Chart text colors - WCAG AA compliant for dark backgrounds
CHART_TEXT_COLORS = {
    'title': '#CBD5E1',       # 8.9:1 contrast - Chart titles
    'axis_label': '#94A3B8',  # 5.6:1 contrast - Axis tick labels
    'legend': '#E2E8F0',      # 12.8:1 contrast - Legend text
    'annotation': '#94A3B8',  # 5.6:1 contrast - Chart annotations
    'tooltip': '#F0F4F8',     # 15.2:1 contrast - Tooltip text
    'grid': 'rgba(148, 163, 184, 0.12)',  # Grid lines
}

# Primary chart color: Brand Teal
CHART_COLORS = {
    'primary': '#009B87',       # Brand Teal - MAIN CHART COLOR
    'secondary': '#295CA9',     # Brand Blue
    'tertiary': '#FFC132',      # Brand Gold
    'quaternary': '#00C9AD',    # Teal Light
    'quinary': '#4A7BC8',       # Blue Light
    'positive': '#009B87',      # Brand Teal
    'negative': '#E53E3E',      # Red
    'neutral': '#94A3B8',       # Improved gray (was #718096)
    # Semantic aliases (for backward compatibility)
    'warning': '#FFC132',       # Yellow/Gold - warnings, fair value
    'danger': '#E53E3E',        # Red - danger, losses
    'success': '#009B87',       # Teal/Green - success, profits
    'info': '#295CA9',          # Blue - informational
}

# Sequential palette for multi-series charts
BAR_COLORS = [
    '#009B87',  # Brand Teal (Primary)
    '#295CA9',  # Brand Blue
    '#FFC132',  # Brand Gold
    '#00C9AD',  # Teal Light
    '#4A7BC8',  # Blue Light
    '#FFD666',  # Gold Light
    '#007A6B',  # Teal Dark
    '#1E4580',  # Blue Dark
]

# Candlestick/Distribution chart colors
DISTRIBUTION_COLORS = {
    'body': '#009B87',                      # Brand Teal
    'body_fill': 'rgba(0, 155, 135, 0.4)',  # Teal transparent
    'whisker': '#009B87',                   # Brand Teal
    'current_dot': '#FFC132',               # Brand Gold (current value)
    'median': '#FFC132',                    # Brand Gold
}

# Valuation assessment colors
ASSESSMENT_COLORS = {
    'undervalued': '#009B87',     # Brand Teal - Good
    'fair': '#FFC132',            # Brand Gold - Neutral
    'expensive': '#E53E3E',       # Red - Warning
}

# Line chart with bands colors
BAND_COLORS = {
    'main_line': '#009B87',                 # Brand Teal
    'median_line': '#FFC132',               # Brand Gold
    'mean_line': '#295CA9',                 # Brand Blue
    'band_1sd': 'rgba(0, 155, 135, 0.15)',  # Teal band
    'band_2sd': 'rgba(41, 92, 169, 0.1)',   # Blue band
    'sd_line': '#4A7BC8',                   # Blue Light
}


# ============================================================
# STYLED HTML TABLE FUNCTION
# ============================================================

def render_styled_table(df, highlight_first_col: bool = True) -> str:
    """
    Render a pandas DataFrame as a styled HTML table.

    Since Streamlit's st.dataframe() uses canvas-based rendering (Glide Data Grid)
    which cannot be styled with CSS, this function generates a pure HTML table
    that can be fully styled.

    Args:
        df: pandas DataFrame to render
        highlight_first_col: Whether to highlight the first column (scope/name)

    Returns:
        HTML string to be used with st.markdown(html, unsafe_allow_html=True)
    """
    # Generate table HTML
    html = '''
    <div class="styled-table-container">
        <table class="styled-table">
            <thead>
                <tr>
    '''

    # Header row
    for i, col in enumerate(df.columns):
        header_class = "header-first" if i == 0 and highlight_first_col else "header"
        html += f'<th class="{header_class}">{col}</th>'

    html += '''
                </tr>
            </thead>
            <tbody>
    '''

    # Data rows
    for idx, row in df.iterrows():
        html += '<tr>'
        for i, (col, val) in enumerate(row.items()):
            cell_class = "cell-first" if i == 0 and highlight_first_col else "cell"
            html += f'<td class="{cell_class}">{val}</td>'
        html += '</tr>'

    html += '''
            </tbody>
        </table>
    </div>
    '''

    return html


def get_table_style() -> str:
    """
    Get CSS styling for the styled HTML table.

    Returns:
        CSS string to inject into page
    """
    return '''
    <style>
    /* Styled Table Container */
    .styled-table-container {
        background: linear-gradient(180deg, #101820 0%, #0A1118 100%);
        border: 1px solid rgba(0, 155, 135, 0.3);
        border-radius: 12px;
        overflow-x: auto;
        overflow-y: hidden;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        margin: 1rem 0;
        max-width: 100%;
    }

    /* Custom scrollbar for table container */
    .styled-table-container::-webkit-scrollbar {
        height: 10px;
    }

    .styled-table-container::-webkit-scrollbar-track {
        background: #0A1118;
        border-radius: 5px;
    }

    .styled-table-container::-webkit-scrollbar-thumb {
        background: linear-gradient(90deg, #009B87, #00C9AD);
        border-radius: 5px;
    }

    .styled-table-container::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(90deg, #00C9AD, #009B87);
    }

    /* Table Base */
    .styled-table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'IBM Plex Mono', 'JetBrains Mono', monospace;
        font-size: 0.85rem;
    }

    /* Header Row */
    .styled-table thead tr {
        background: linear-gradient(135deg, rgba(0, 155, 135, 0.15) 0%, rgba(41, 92, 169, 0.1) 100%);
    }

    /* Header Cells */
    .styled-table th.header,
    .styled-table th.header-first {
        color: #009B87;
        font-family: 'Geist', 'Inter', -apple-system, sans-serif;
        font-weight: 600;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding: 14px 16px;
        border-bottom: 2px solid rgba(0, 155, 135, 0.3);
        text-align: left;
        white-space: nowrap;
    }

    .styled-table th.header-first {
        color: #FFC132;
        position: sticky;
        left: 0;
        z-index: 2;
        background: linear-gradient(135deg, rgba(16, 24, 32, 0.98) 0%, rgba(10, 17, 24, 0.98) 100%);
        box-shadow: 2px 0 8px rgba(0, 0, 0, 0.3);
    }

    /* Body Rows */
    .styled-table tbody tr {
        background: rgba(16, 24, 32, 0.6);
        transition: all 0.2s ease;
    }

    .styled-table tbody tr:nth-child(even) {
        background: rgba(20, 30, 40, 0.7);
    }

    .styled-table tbody tr:hover {
        background: rgba(0, 155, 135, 0.12);
    }

    /* Body Cells */
    .styled-table td.cell,
    .styled-table td.cell-first {
        color: #E2E8F0;
        padding: 12px 16px;
        border-bottom: 1px solid rgba(160, 174, 192, 0.08);
        vertical-align: middle;
        text-align: right;
    }

    .styled-table td.cell-first {
        color: #FFFFFF;
        font-weight: 500;
        font-family: 'IBM Plex Sans', -apple-system, sans-serif;
        text-align: left;
        position: sticky;
        left: 0;
        z-index: 1;
        background: rgba(16, 24, 32, 0.98);
        box-shadow: 2px 0 8px rgba(0, 0, 0, 0.3);
    }

    .styled-table tbody tr:nth-child(even) td.cell-first {
        background: rgba(20, 30, 40, 0.98);
    }

    .styled-table tbody tr:hover td.cell-first {
        background: rgba(0, 155, 135, 0.25);
    }

    /* Hover effect on cells */
    .styled-table tbody tr:hover td {
        color: #F0F4F8;
    }

    .styled-table tbody tr:hover td.cell-first {
        color: #00C9AD;
    }
    </style>
    '''
