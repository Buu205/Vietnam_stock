"""
Dashboard Styles - Crypto Terminal Glassmorphism
=================================================

Modern fintech/crypto dashboard with glassmorphism effects.
OLED-optimized dark theme with purple/cyan accent colors.

Design Direction:
- Aesthetic: CRYPTO TERMINAL - Deep purple-black with glassmorphism
- Primary: Electric Purple #8B5CF6
- Secondary: Cyan #06B6D4
- Accent: Amber #F59E0B
- Typography: Space Grotesk (display) + DM Sans (body) + JetBrains Mono (data)

Usage:
    from WEBAPP.core.styles import get_page_style, get_chart_layout

Created: 2025-12-16
Updated: 2025-12-21 - Fintech/Crypto Glassmorphism redesign
"""

from WEBAPP.core.theme import (
    DARK_THEME, CHART_PALETTE, TRADING_COLORS,
    SEMANTIC, TYPOGRAPHY, SPACING, RADIUS, SHADOWS,
    GLASS, PURPLE, CYAN, AMBER, Z_INDEX
)


def get_page_style() -> str:
    """
    Get premium page-level CSS styling.

    Design: Crypto Terminal with Glassmorphism
    - Background: Deep purple-black OLED gradient
    - Cards: Glassmorphism with blur effects
    - Accents: Purple/Cyan neon glow
    - Charts: Trading terminal colors

    Returns:
        Complete CSS string for Streamlit markdown injection
    """
    return """
<style>
    /* ============================================================
       FONTS - Tech Terminal Typography
       ============================================================ */
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

    :root {
        /* ========== CRYPTO TERMINAL COLORS ========== */
        --purple-primary: #8B5CF6;
        --purple-dark: #7C3AED;
        --purple-light: #A78BFA;
        --purple-pale: #C4B5FD;
        --purple-glow: rgba(139, 92, 246, 0.4);

        --cyan-primary: #06B6D4;
        --cyan-dark: #0891B2;
        --cyan-light: #22D3EE;
        --cyan-glow: rgba(6, 182, 212, 0.4);

        --amber-primary: #F59E0B;
        --amber-light: #FBBF24;

        /* ========== BACKGROUNDS (OLED Optimized) ========== */
        --bg-void: #0F0B1E;
        --bg-deep: #1A1625;
        --bg-surface: #252033;
        --bg-elevated: #2D2640;
        --bg-hover: #352E4D;

        /* ========== TEXT - HIGH CONTRAST ========== */
        --text-white: #F8FAFC;
        --text-bright: #F1F5F9;
        --text-primary: #E2E8F0;
        --text-secondary: #94A3B8;
        --text-accent: #C4B5FD;
        --text-muted: #64748B;

        /* ========== SEMANTIC COLORS ========== */
        --positive: #10B981;
        --positive-light: #34D399;
        --negative: #EF4444;
        --negative-light: #F87171;
        --warning: #F59E0B;
        --info: #8B5CF6;

        /* ========== GLASSMORPHISM ========== */
        --glass-bg: rgba(255, 255, 255, 0.03);
        --glass-bg-hover: rgba(255, 255, 255, 0.05);
        --glass-border: rgba(255, 255, 255, 0.08);
        --glass-border-hover: rgba(139, 92, 246, 0.3);
        --glass-blur: blur(12px);
        --glass-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        --glass-shadow-hover: 0 8px 32px rgba(139, 92, 246, 0.15);
        --glass-inner: inset 0 1px 0 rgba(255, 255, 255, 0.05);

        /* ========== NEON GLOW EFFECTS ========== */
        --glow-purple: 0 0 20px rgba(139, 92, 246, 0.3);
        --glow-cyan: 0 0 20px rgba(6, 182, 212, 0.3);
        --glow-amber: 0 0 15px rgba(245, 158, 11, 0.25);

        /* ========== TYPOGRAPHY ========== */
        --font-display: 'Space Grotesk', -apple-system, BlinkMacSystemFont, sans-serif;
        --font-body: 'DM Sans', -apple-system, sans-serif;
        --font-mono: 'JetBrains Mono', 'SF Mono', monospace;

        /* ========== Z-INDEX SCALE ========== */
        --z-base: 1;
        --z-dropdown: 100;
        --z-sticky: 150;
        --z-modal: 200;
        --z-toast: 300;
        --z-tooltip: 400;
    }

    /* ============================================================
       BASE - OLED VOID BACKGROUND
       ============================================================ */
    .stApp {
        background: linear-gradient(170deg,
            var(--bg-void) 0%,
            var(--bg-deep) 50%,
            var(--bg-surface) 100%
        );
        min-height: 100vh;
    }

    /* ========== CHART-FIRST: TIGHTER CONTAINER ========== */
    .block-container {
        padding: 0.5rem 1.5rem 1.5rem 1.5rem !important;  /* Reduced from 2.5rem */
        max-width: 100% !important;  /* Full width, no 1800px cap */
        margin-top: 0 !important;
    }

    /* ========== HEADER ========== */
    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    .stDeployButton,
    [data-testid="stStatusWidget"],
    [data-testid="stToolbar"] > div:not(:first-child),
    .viewerBadge_container__r5tak,
    .styles_viewerBadge__CvC9N,
    [data-testid="stDecoration"] {
        display: none !important;
    }

    footer,
    .stAppViewBlockContainer > footer {
        display: none !important;
    }

    .main .block-container,
    .stApp > .main > .block-container {
        padding-top: 0.75rem !important;
        margin-top: 0 !important;
    }

    * {
        font-family: var(--font-body);
    }

    /* ============================================================
       TYPOGRAPHY - SPACE GROTESK DISPLAY
       ============================================================ */
    h1, h2, h3, .stTitle, .stSubheader {
        font-family: var(--font-display) !important;
        font-weight: 600 !important;
        letter-spacing: -0.025em;
    }

    /* Page Title - Purple/Cyan Gradient */
    h1 {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        color: var(--text-white) !important;
        background: linear-gradient(135deg,
            var(--text-white) 0%,
            var(--purple-primary) 50%,
            var(--cyan-primary) 100%
        );
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0 0 0.25rem 0 !important;
        padding: 0 !important;
        line-height: 1.2 !important;
        text-shadow: 0 0 80px rgba(139, 92, 246, 0.4);
    }

    /* Section Headers - Compact Tech Style */
    h3 {
        font-size: 0.75rem !important;  /* Reduced from 0.8rem */
        font-weight: 600 !important;
        color: var(--text-accent) !important;
        text-transform: uppercase;
        letter-spacing: 0.1em;  /* Reduced from 0.12em */
        margin: 0.75rem 0 0.5rem 0 !important;  /* Reduced from 1rem 0 0.75rem */
        padding-bottom: 0.4rem;  /* Reduced from 0.5rem */
        border-bottom: 1px solid var(--glass-border);
        position: relative;
    }

    h3::after {
        content: '';
        position: absolute;
        bottom: -1px;
        left: 0;
        width: 40px;
        height: 2px;
        background: linear-gradient(90deg, var(--purple-primary), var(--cyan-primary));
    }

    p, span, div {
        color: var(--text-primary);
    }

    .stMarkdown p:first-child {
        font-size: 0.95rem;
        color: var(--text-secondary);
        font-weight: 400;
        margin: 0 0 0.5rem 0 !important;
        line-height: 1.5 !important;
    }

    strong, b {
        color: var(--text-bright);
        font-weight: 600;
    }

    /* ============================================================
       METRIC CARDS - COMPACT GLASSMORPHISM
       ============================================================ */
    [data-testid="stMetric"] {
        background: var(--glass-bg);
        backdrop-filter: var(--glass-blur);
        -webkit-backdrop-filter: var(--glass-blur);
        border: 1px solid var(--glass-border);
        border-radius: 12px;  /* Reduced from 16px */
        padding: 1rem 1.25rem !important;  /* Reduced from 1.5rem 1.75rem */
        transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        position: relative;
        overflow: hidden;
        box-shadow: var(--glass-shadow), var(--glass-inner);
    }

    /* Top accent bar - Purple gradient */
    [data-testid="stMetric"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, var(--purple-primary), var(--cyan-primary));
        opacity: 0.6;
    }

    /* Corner glow - Purple */
    [data-testid="stMetric"]::after {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 100%;
        height: 100%;
        background: radial-gradient(circle, rgba(139, 92, 246, 0.08) 0%, transparent 70%);
        pointer-events: none;
    }

    [data-testid="stMetric"]:hover {
        border-color: var(--glass-border-hover);
        box-shadow: var(--glass-shadow-hover), var(--glow-purple);
        transform: translateY(-4px);
        background: var(--glass-bg-hover);
    }

    [data-testid="stMetric"]:hover::before {
        opacity: 1;
    }

    /* Metric Label - Compact */
    [data-testid="stMetricLabel"] {
        font-family: var(--font-body) !important;
        font-size: 0.7rem !important;  /* Reduced from 0.75rem */
        font-weight: 600 !important;
        color: var(--text-secondary) !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;  /* Reduced from 0.1em */
    }

    /* Metric Value - Compact monospace */
    [data-testid="stMetricValue"] {
        font-family: var(--font-mono) !important;
        font-size: 1.75rem !important;  /* Reduced from 2rem */
        font-weight: 600 !important;
        color: var(--text-white) !important;
        letter-spacing: -0.02em;
        text-shadow: 0 0 40px rgba(255, 255, 255, 0.1);
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
       SIDEBAR - GLASS PANEL
       ============================================================ */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg,
            var(--bg-deep) 0%,
            var(--bg-surface) 100%
        ) !important;
        border-right: 1px solid var(--glass-border);
    }

    [data-testid="stSidebar"]::before {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 1px;
        height: 100%;
        background: linear-gradient(180deg, var(--purple-primary), transparent);
        opacity: 0.3;
    }

    /* ========== COLLAPSED SIDEBAR OPTIMIZATION ========== */
    [data-testid="stSidebar"][aria-expanded="false"] {
        width: 0px !important;
        min-width: 0px !important;
        transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    [data-testid="stSidebar"][aria-expanded="true"] {
        width: 280px !important;
        min-width: 280px !important;
        transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    /* Sidebar toggle button styling */
    [data-testid="stSidebar"] button[kind="header"],
    [data-testid="collapsedControl"] {
        background: rgba(139, 92, 246, 0.15) !important;
        border: 1px solid rgba(139, 92, 246, 0.3) !important;
        color: var(--purple-light) !important;
        transition: all 0.2s ease !important;
    }

    [data-testid="stSidebar"] button[kind="header"]:hover,
    [data-testid="collapsedControl"]:hover {
        background: rgba(139, 92, 246, 0.25) !important;
        border-color: var(--purple-primary) !important;
        box-shadow: var(--glow-purple) !important;
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

    /* ============================================================
       STICKY FILTER BAR - TOP HORIZONTAL FILTERS
       ============================================================ */
    .filter-bar-container {
        position: sticky;
        top: 0;
        z-index: var(--z-sticky);
        background: linear-gradient(180deg, var(--bg-void) 0%, var(--bg-deep) 100%);
        padding: 0.75rem 0;
        margin: -0.5rem 0 1rem 0;
        border-bottom: 1px solid var(--glass-border);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
    }

    /* Compact filter inputs in top bar */
    .filter-bar-container .stSelectbox > div > div,
    .filter-bar-container .stTextInput > div > div {
        min-height: 36px !important;
        font-size: 13px !important;
        background: var(--bg-elevated) !important;
        border: 1px solid var(--glass-border) !important;
    }

    .filter-bar-container .stSelectbox > div > div:hover,
    .filter-bar-container .stTextInput > div > div:hover {
        border-color: var(--purple-primary) !important;
    }

    .filter-bar-container .stButton > button {
        min-height: 36px !important;
        padding: 0.4rem 1rem !important;
        font-size: 13px !important;
        background: var(--glass-bg) !important;
        border: 1px solid var(--glass-border) !important;
        color: var(--text-primary) !important;
    }

    .filter-bar-container .stButton > button:hover {
        background: var(--bg-hover) !important;
        border-color: var(--purple-primary) !important;
        color: var(--purple-light) !important;
    }

    /* Pill-style radio buttons for inline filters */
    .filter-bar-container .stRadio > div {
        gap: 0.5rem;
        flex-wrap: nowrap;
    }

    .filter-bar-container .stRadio > div > label {
        padding: 0.35rem 0.75rem;
        font-size: 12px;
        white-space: nowrap;
    }

    /* Sidebar inputs */
    [data-testid="stSidebar"] .stSelectbox > div > div,
    [data-testid="stSidebar"] .stTextInput > div > div {
        background: var(--bg-elevated) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 8px;
        color: #FFFFFF !important;
        font-size: 13px !important;
        min-height: 38px !important;
    }

    [data-testid="stSidebar"] .stTextInput input,
    [data-testid="stSidebar"] .stTextInput input::placeholder {
        color: #FFFFFF !important;
        opacity: 1 !important;
    }

    [data-testid="stSidebar"] .stTextInput input::placeholder {
        color: var(--text-muted) !important;
    }

    [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] span,
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div {
        font-size: 13px !important;
        color: #FFFFFF !important;
    }

    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stTextInput label,
    [data-testid="stSidebar"] .stSlider label {
        font-size: 12px !important;
        color: var(--text-muted) !important;
        margin-bottom: 0.25rem !important;
    }

    [data-testid="stSidebar"] .stSelectbox > div > div:hover,
    [data-testid="stSidebar"] .stTextInput > div > div:hover {
        border-color: var(--purple-primary) !important;
    }

    [data-testid="stSidebar"] .stSelectbox > div > div:focus-within {
        border-color: var(--purple-primary) !important;
        box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.2);
    }

    /* Slider - Purple accent */
    [data-testid="stSidebar"] .stSlider > div > div > div {
        background: var(--purple-primary) !important;
    }

    [data-testid="stSidebar"] .stSlider > div > div > div > div {
        background: var(--purple-light) !important;
    }

    /* ============================================================
       NAVIGATION
       ============================================================ */
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

    [data-testid="stSidebar"] a,
    [data-testid="stSidebar"] [data-testid="stSidebarNavLink"],
    [data-testid="stSidebar"] nav a,
    [data-testid="stSidebar"] nav a span,
    [data-testid="stSidebarNavLink"] span {
        color: var(--text-primary) !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        padding: 0.5rem 0.75rem !important;
        border-radius: 8px;
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

    /* Active navigation link - Purple highlight */
    [data-testid="stSidebar"] a[aria-current="page"],
    [data-testid="stSidebar"] [data-testid="stSidebarNavLink"][aria-current="page"],
    [data-testid="stSidebar"] a[aria-current="page"] span,
    [data-testid="stSidebarNavLink"][aria-current="page"] span {
        color: var(--purple-light) !important;
        background: rgba(139, 92, 246, 0.15) !important;
        font-weight: 600 !important;
    }

    [data-testid="stSidebar"] nav {
        padding: 0.25rem 0;
    }

    [data-testid="stSidebar"] nav ul {
        gap: 2px !important;
    }

    [data-testid="stSidebar"] [data-testid="stSidebarNavLink"] svg,
    [data-testid="stSidebar"] nav a svg,
    [data-testid="stSidebarNavLink"] [data-testid="stIconMaterial"],
    [data-testid="stSidebar"] a [data-testid="stIconMaterial"] {
        width: 16px !important;
        height: 16px !important;
        min-width: 16px !important;
        margin-right: 8px !important;
        flex-shrink: 0 !important;
    }

    [data-testid="stSidebarNavLink"] {
        display: flex !important;
        align-items: center !important;
        overflow: visible !important;
        white-space: nowrap !important;
        min-height: 36px !important;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: var(--text-secondary) !important;
        font-size: 13px !important;
    }

    /* ============================================================
       TABS - COMPACT GLASS SEGMENTED CONTROL
       ============================================================ */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--glass-bg);
        backdrop-filter: var(--glass-blur);
        border-radius: 10px;  /* Reduced from 12px */
        padding: 4px;  /* Reduced from 5px */
        gap: 3px;  /* Reduced from 4px */
        border: 1px solid var(--glass-border);
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border-radius: 6px;  /* Reduced from 8px */
        padding: 0.5rem 1.25rem;  /* Reduced from 0.65rem 1.75rem */
        font-family: var(--font-body);
        font-weight: 500;
        font-size: 0.8rem;  /* Reduced from 0.875rem */
        color: var(--text-secondary);
        transition: all 0.25s ease;
        border: none;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: var(--text-primary);
        background: var(--bg-hover) !important;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--purple-primary), var(--purple-dark)) !important;
        color: var(--text-white) !important;
        font-weight: 600;
        box-shadow: var(--glow-purple);
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
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        border-radius: 8px;
        padding: 0.5rem 1rem;
        cursor: pointer;
        transition: all 0.2s ease;
    }

    .stRadio > div > label:hover {
        border-color: var(--purple-primary);
        background: var(--bg-hover);
    }

    .stRadio > div > label[data-checked="true"] {
        background: var(--purple-primary);
        border-color: var(--purple-primary);
        color: var(--text-white);
    }

    /* ============================================================
       BUTTONS - GRADIENT
       ============================================================ */
    .stButton > button {
        background: linear-gradient(135deg, var(--purple-primary), var(--purple-dark)) !important;
        border: none !important;
        border-radius: 10px;
        font-family: var(--font-body);
        font-weight: 600;
        font-size: 0.9rem;
        padding: 0.7rem 1.75rem;
        color: var(--text-white) !important;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.25);
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(139, 92, 246, 0.35), var(--glow-purple);
    }

    .stButton > button:active {
        transform: translateY(0);
    }

    /* Download Button - Outlined */
    .stDownloadButton > button {
        background: transparent !important;
        border: 1px solid var(--glass-border) !important;
        color: var(--text-primary) !important;
    }

    .stDownloadButton > button:hover {
        background: var(--bg-hover) !important;
        border-color: var(--purple-primary) !important;
        color: var(--purple-light) !important;
    }

    /* ============================================================
       DATAFRAMES - GLASS DATA GRID
       ============================================================ */
    .stDataFrame {
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid var(--glass-border);
        box-shadow: var(--glass-shadow);
    }

    .stDataFrame [data-testid="stDataFrameResizable"] {
        background: var(--bg-deep);
    }

    .stDataFrame th {
        background: var(--bg-surface) !important;
        font-family: var(--font-body) !important;
        font-weight: 600 !important;
        font-size: 0.75rem !important;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--purple-light) !important;
        padding: 1.1rem 1.25rem !important;
        border-bottom: 1px solid var(--glass-border) !important;
    }

    .stDataFrame td {
        font-family: var(--font-mono) !important;
        font-size: 0.875rem !important;
        color: var(--text-primary) !important;
        padding: 0.9rem 1.25rem !important;
        border-bottom: 1px solid var(--glass-border) !important;
    }

    .stDataFrame tr:hover td {
        background: var(--bg-hover) !important;
    }

    .stDataFrame tbody tr:nth-child(even) td {
        background: rgba(26, 22, 37, 0.5);
    }

    /* ============================================================
       CHARTS - MINIMAL GLASS CONTAINER
       ============================================================ */
    .stPlotlyChart {
        background: var(--glass-bg);
        backdrop-filter: var(--glass-blur);
        border-radius: 12px;  /* Reduced from 16px */
        padding: 0.5rem;  /* Reduced from 1rem */
        border: 1px solid var(--glass-border);
        box-shadow: var(--glass-shadow);
        width: 100% !important;
        max-width: 100% !important;
        overflow: hidden;
    }

    .stPlotlyChart > div {
        width: 100% !important;
        max-width: 100% !important;
    }

    .stPlotlyChart .js-plotly-plot,
    .stPlotlyChart .plotly,
    .stPlotlyChart .plot-container {
        width: 100% !important;
        max-width: 100% !important;
    }

    [data-testid="column"] .stPlotlyChart {
        min-width: 0;
    }

    .stPlotlyChart .modebar-container {
        position: absolute !important;
        right: 5px !important;
        top: 5px !important;
    }

    .stPlotlyChart .legend text,
    .stPlotlyChart .legendtext,
    .stPlotlyChart g.legend text,
    .stPlotlyChart .legend .legendtext {
        fill: #FFFFFF !important;
        color: #FFFFFF !important;
    }

    /* ============================================================
       INFO/WARNING/ERROR BOXES
       ============================================================ */
    .stAlert {
        border-radius: 12px;
        border-left-width: 4px;
        background: var(--glass-bg);
        backdrop-filter: var(--glass-blur);
    }

    .stAlert[data-baseweb="notification"][kind="info"] {
        background: rgba(139, 92, 246, 0.1);
        border-left-color: var(--purple-primary);
    }

    .stAlert[data-baseweb="notification"][kind="success"] {
        background: rgba(16, 185, 129, 0.1);
        border-left-color: var(--positive);
    }

    .stAlert[data-baseweb="notification"][kind="warning"] {
        background: rgba(245, 158, 11, 0.1);
        border-left-color: var(--warning);
    }

    .stAlert[data-baseweb="notification"][kind="error"] {
        background: rgba(239, 68, 68, 0.1);
        border-left-color: var(--negative);
    }

    /* ============================================================
       SELECTBOX & MULTISELECT
       ============================================================ */
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        background: var(--bg-elevated) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 10px;
        color: var(--text-primary);
    }

    .stSelectbox > div > div:hover,
    .stMultiSelect > div > div:hover {
        border-color: var(--purple-primary) !important;
    }

    .stMultiSelect [data-baseweb="tag"] {
        background: var(--purple-primary) !important;
        border-radius: 6px;
        color: var(--text-white);
    }

    /* Dropdown Menu - Dark Theme */
    [data-baseweb="popover"],
    [data-baseweb="popover"] > div,
    div[data-baseweb="popover"] {
        background: var(--bg-surface) !important;
        background-color: var(--bg-surface) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 10px !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6) !important;
    }

    [data-baseweb="menu"],
    [data-baseweb="listbox"],
    ul[role="listbox"],
    div[data-baseweb="menu"],
    div[data-baseweb="listbox"] {
        background: var(--bg-surface) !important;
        background-color: var(--bg-surface) !important;
        border-radius: 10px !important;
    }

    [data-baseweb="menu"] li,
    [data-baseweb="listbox"] li,
    [role="option"],
    ul[role="listbox"] li,
    div[data-baseweb="select"] li {
        background: var(--bg-surface) !important;
        background-color: var(--bg-surface) !important;
        color: var(--text-primary) !important;
        font-family: var(--font-body) !important;
        padding: 0.75rem 1rem !important;
        transition: all 0.15s ease !important;
    }

    [data-baseweb="menu"] li:hover,
    [data-baseweb="listbox"] li:hover,
    [role="option"]:hover,
    ul[role="listbox"] li:hover,
    div[data-baseweb="select"] li:hover {
        background: var(--bg-hover) !important;
        background-color: var(--bg-hover) !important;
        color: #FFFFFF !important;
    }

    [data-baseweb="menu"] li[aria-selected="true"],
    [data-baseweb="listbox"] li[aria-selected="true"],
    [role="option"][aria-selected="true"],
    [data-highlighted="true"],
    ul[role="listbox"] li[aria-selected="true"] {
        background: var(--purple-primary) !important;
        background-color: var(--purple-primary) !important;
        color: #FFFFFF !important;
        font-weight: 500 !important;
    }

    div[data-baseweb="select"] ul,
    div[data-baseweb="select"] > div > div {
        background: var(--bg-surface) !important;
        background-color: var(--bg-surface) !important;
    }

    [data-baseweb="menu"] > div,
    [data-baseweb="listbox"] > div {
        background: var(--bg-surface) !important;
    }

    /* ============================================================
       HORIZONTAL RULE - GRADIENT FADE (COMPACT)
       ============================================================ */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg,
            transparent 0%,
            var(--glass-border) 20%,
            var(--purple-primary) 50%,
            var(--glass-border) 80%,
            transparent 100%
        );
        margin: 0.75rem 0 1rem 0;  /* Reduced from 1rem 0 1.25rem */
        opacity: 0.6;
    }

    /* ============================================================
       FOOTER CAPTION
       ============================================================ */
    .stCaption {
        font-family: var(--font-mono) !important;
        font-size: 0.75rem !important;
        color: var(--text-muted) !important;
        letter-spacing: 0.03em;
    }

    /* ============================================================
       ANIMATIONS
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
        0%, 100% { box-shadow: 0 0 20px rgba(139, 92, 246, 0.1); }
        50% { box-shadow: 0 0 30px rgba(139, 92, 246, 0.2); }
    }

    @keyframes neonPulse {
        0%, 100% { text-shadow: 0 0 10px var(--purple-glow); }
        50% { text-shadow: 0 0 20px var(--purple-glow), 0 0 30px var(--cyan-glow); }
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
       DATA TABLE / DATAFRAME - GLASS STYLING
       ============================================================ */
    [data-testid="stDataFrame"],
    .stDataFrame {
        background: linear-gradient(180deg, var(--bg-surface) 0%, var(--bg-deep) 100%) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 12px !important;
        overflow: hidden !important;
        box-shadow: var(--glass-shadow) !important;
        padding: 0 !important;
    }

    [data-testid="stDataFrame"] > div,
    .stDataFrame > div {
        background: transparent !important;
        border-radius: 12px !important;
    }

    [data-testid="stDataFrame"] iframe,
    .stDataFrame iframe {
        background: var(--bg-surface) !important;
        border: none !important;
        border-radius: 10px !important;
    }

    [data-testid="glideDataEditor"],
    .dvn-scroller,
    .dvn-underlay {
        background: var(--bg-surface) !important;
    }

    [data-testid="stDataFrameResizable"] {
        background: linear-gradient(180deg, var(--bg-surface) 0%, var(--bg-deep) 100%) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 10px !important;
        overflow: hidden !important;
    }

    [data-testid="stDataFrameToolbar"],
    [data-testid="stElementToolbar"] {
        background: rgba(26, 22, 37, 0.9) !important;
        border-bottom: 1px solid var(--glass-border) !important;
    }

    [data-testid="stDataFrameToolbar"] button,
    [data-testid="stElementToolbar"] button {
        color: var(--purple-primary) !important;
        background: transparent !important;
        border: none !important;
    }

    [data-testid="stDataFrameToolbar"] button:hover,
    [data-testid="stElementToolbar"] button:hover {
        color: var(--purple-light) !important;
        background: rgba(139, 92, 246, 0.15) !important;
    }

    .stDataFrame [class*="header"],
    .dvn-scroll-inner [class*="header"] {
        background: rgba(139, 92, 246, 0.1) !important;
        color: var(--purple-light) !important;
        font-family: var(--font-body) !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.03em !important;
    }

    .stDataFrame [class*="cell"],
    .dvn-scroll-inner [class*="cell"] {
        color: var(--text-primary) !important;
        font-family: var(--font-mono) !important;
    }

    [data-testid="stDataFrameToolbar"] input {
        background: rgba(26, 22, 37, 0.95) !important;
        border: 1px solid var(--glass-border) !important;
        color: var(--text-primary) !important;
        border-radius: 6px !important;
    }

    [data-testid="stDataFrameToolbar"] input::placeholder {
        color: var(--text-muted) !important;
    }

    /* Scrollbar */
    [data-testid="stDataFrame"] ::-webkit-scrollbar,
    .stDataFrame ::-webkit-scrollbar {
        width: 8px !important;
        height: 8px !important;
    }

    [data-testid="stDataFrame"] ::-webkit-scrollbar-track,
    .stDataFrame ::-webkit-scrollbar-track {
        background: var(--bg-deep) !important;
    }

    [data-testid="stDataFrame"] ::-webkit-scrollbar-thumb,
    .stDataFrame ::-webkit-scrollbar-thumb {
        background: rgba(139, 92, 246, 0.4) !important;
        border-radius: 4px !important;
    }

    [data-testid="stDataFrame"] ::-webkit-scrollbar-thumb:hover,
    .stDataFrame ::-webkit-scrollbar-thumb:hover {
        background: rgba(139, 92, 246, 0.6) !important;
    }

    [data-testid="stDataFrame"][data-fullscreen="true"],
    .stDataFrame[data-fullscreen="true"] {
        background: var(--bg-deep) !important;
        border: 2px solid var(--purple-primary) !important;
    }

    [data-testid="stDataFrame"] [data-testid="stSpinner"],
    .stDataFrame [data-testid="stSpinner"] {
        color: var(--purple-primary) !important;
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
        background: var(--glass-border);
        border-radius: 3px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-muted);
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

    /* ============================================================
       ACCESSIBILITY - REDUCED MOTION
       ============================================================ */
    @media (prefers-reduced-motion: reduce) {
        *, ::before, ::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
            scroll-behavior: auto !important;
        }
    }

    /* ============================================================
       INTERACTIVE ELEMENTS - CURSOR POINTER
       ============================================================ */
    [data-testid="stMetric"]:hover,
    .stTabs [data-baseweb="tab"],
    .stButton > button,
    .stDownloadButton > button,
    .stSelectbox > div > div,
    .stMultiSelect > div > div,
    [data-testid="stSidebarNavLink"],
    [role="option"] {
        cursor: pointer;
    }

    /* ============================================================
       LOADING STATES
       ============================================================ */
    [data-testid="stSpinner"],
    .stSpinner > div {
        color: var(--purple-primary) !important;
        border-color: var(--purple-primary) transparent transparent transparent !important;
    }

    /* ============================================================
       LIVE INDICATOR (Real-time pulse)
       ============================================================ */
    .live-indicator {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--positive);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .live-indicator::before {
        content: '';
        width: 8px;
        height: 8px;
        background: var(--positive);
        border-radius: 50%;
        animation: livePulse 1.5s ease-in-out infinite;
    }

    @keyframes livePulse {
        0%, 100% {
            opacity: 1;
            box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4);
        }
        50% {
            opacity: 0.6;
            box-shadow: 0 0 0 6px rgba(16, 185, 129, 0);
        }
    }

</style>
"""


def get_chart_layout(title: str = "", height: int = 400) -> dict:
    """
    Get consistent Plotly chart layout - Crypto Terminal theme.

    Charts use #8B5CF6 (Electric Purple) as primary color.
    Trading colors: #10B981 (bullish), #EF4444 (bearish).

    Args:
        title: Chart title
        height: Chart height in pixels

    Returns:
        Plotly layout dict
    """
    return {
        'title': {
            'text': title,
            'font': {'family': 'Space Grotesk, sans-serif', 'size': 14, 'color': '#C4B5FD'},
            'x': 0,
            'xanchor': 'left'
        },
        'height': height,
        'autosize': True,
        'margin': {'l': 40, 'r': 20, 't': 40, 'b': 40, 'pad': 2},  # Reduced margins
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'font': {
            'family': 'JetBrains Mono, monospace',
            'size': 11,
            'color': '#94A3B8'
        },
        'xaxis': {
            'gridcolor': 'rgba(255, 255, 255, 0.05)',
            'zerolinecolor': 'rgba(255, 255, 255, 0.1)',
            'tickfont': {'size': 10, 'color': '#64748B'},
            'linecolor': 'rgba(255, 255, 255, 0.08)',
            'tickangle': -45,
            'automargin': True,
            'type': 'category',
            'categoryorder': 'array',
            'nticks': 10,
        },
        'yaxis': {
            'gridcolor': 'rgba(255, 255, 255, 0.05)',
            'zerolinecolor': 'rgba(255, 255, 255, 0.1)',
            'tickfont': {'size': 11, 'color': '#64748B'},
            'linecolor': 'rgba(255, 255, 255, 0.08)',
            'automargin': True,
            'fixedrange': False,
        },
        'legend': {
            'font': {'size': 11, 'color': '#FFFFFF'},
            'bgcolor': 'rgba(0,0,0,0)',
            'bordercolor': 'rgba(0,0,0,0)',
        },
        'hoverlabel': {
            'bgcolor': '#1A1625',
            'bordercolor': '#8B5CF6',
            'font': {'family': 'JetBrains Mono', 'size': 12, 'color': '#F8FAFC'}
        }
    }


# ============================================================
# CHART COLORS - CRYPTO TERMINAL
# ============================================================

# Chart text colors
CHART_TEXT_COLORS = {
    'title': '#C4B5FD',       # Purple pale - Chart titles
    'axis_label': '#64748B',  # Muted - Axis tick labels
    'legend': '#FFFFFF',      # White for max visibility
    'annotation': '#94A3B8',  # Secondary - Chart annotations
    'tooltip': '#F8FAFC',     # White - Tooltip text
    'grid': 'rgba(255, 255, 255, 0.05)',  # Grid lines
}

# Primary chart colors
CHART_COLORS = {
    'primary': '#8B5CF6',       # Electric Purple - MAIN CHART COLOR
    'secondary': '#06B6D4',     # Cyan
    'tertiary': '#F59E0B',      # Amber
    'quaternary': '#A78BFA',    # Purple Light
    'quinary': '#22D3EE',       # Cyan Light
    'positive': '#10B981',      # Emerald
    'negative': '#EF4444',      # Red
    'neutral': '#6B7280',       # Gray
    'warning': '#F59E0B',       # Amber
    'danger': '#EF4444',        # Red
    'success': '#10B981',       # Emerald
    'info': '#8B5CF6',          # Purple
}

# Sequential palette for multi-series charts
BAR_COLORS = [
    '#8B5CF6',  # Electric Purple
    '#06B6D4',  # Cyan
    '#F59E0B',  # Amber
    '#10B981',  # Emerald
    '#EC4899',  # Pink
    '#3B82F6',  # Blue
    '#A78BFA',  # Purple Light
    '#22D3EE',  # Cyan Light
]

# Trading chart colors
TRADING_CHART_COLORS = {
    'bullish': '#10B981',       # Green candles
    'bearish': '#EF4444',       # Red candles
    'volume_up': 'rgba(16, 185, 129, 0.4)',
    'volume_down': 'rgba(239, 68, 68, 0.4)',
    'ma_20': '#8B5CF6',
    'ma_50': '#06B6D4',
    'ma_200': '#F59E0B',
}

# Distribution chart colors
DISTRIBUTION_COLORS = {
    'body': '#8B5CF6',
    'body_fill': 'rgba(139, 92, 246, 0.4)',
    'whisker': '#8B5CF6',
    'current_dot': '#F59E0B',
    'median': '#F59E0B',
}

# Valuation assessment colors
ASSESSMENT_COLORS = {
    'undervalued': '#10B981',
    'fair': '#F59E0B',
    'expensive': '#EF4444',
}

# Line chart with bands colors
BAND_COLORS = {
    'main_line': '#8B5CF6',
    'median_line': '#F59E0B',
    'mean_line': '#06B6D4',
    'band_1sd': 'rgba(139, 92, 246, 0.15)',
    'band_2sd': 'rgba(6, 182, 212, 0.1)',
    'sd_line': '#A78BFA',
}


# ============================================================
# STYLED HTML TABLE FUNCTION
# ============================================================

def render_styled_table(df, highlight_first_col: bool = True, highlight_row: str = None) -> str:
    """
    Render a pandas DataFrame as a styled HTML table.

    Args:
        df: pandas DataFrame to render
        highlight_first_col: Whether to highlight the first column
        highlight_row: Value in first column to highlight as special row (e.g., 'BSC Universal')

    Returns:
        HTML string to be used with st.markdown(html, unsafe_allow_html=True)
    """
    html = '''
    <div class="styled-table-container">
        <table class="styled-table">
            <thead>
                <tr>
    '''

    for i, col in enumerate(df.columns):
        header_class = "header-first" if i == 0 and highlight_first_col else "header"
        html += f'<th class="{header_class}">{col}</th>'

    html += '''
                </tr>
            </thead>
            <tbody>
    '''

    # Get first column name for highlight row check
    first_col = df.columns[0] if len(df.columns) > 0 else None

    for idx, row in df.iterrows():
        # Check if this row should be highlighted
        is_highlight_row = highlight_row and first_col and str(row[first_col]) == highlight_row
        row_style = ' style="background: rgba(0, 201, 173, 0.15); border-top: 2px solid #00C9AD; border-bottom: 2px solid #00C9AD; font-weight: 600;"' if is_highlight_row else ''
        html += f'<tr{row_style}>'
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
        background: linear-gradient(180deg, #1A1625 0%, #0F0B1E 100%);
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 12px;
        overflow-x: auto;
        overflow-y: hidden;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        margin: 1rem 0;
        max-width: 100%;
    }

    .styled-table-container::-webkit-scrollbar {
        height: 10px;
    }

    .styled-table-container::-webkit-scrollbar-track {
        background: #0F0B1E;
        border-radius: 5px;
    }

    .styled-table-container::-webkit-scrollbar-thumb {
        background: linear-gradient(90deg, #8B5CF6, #06B6D4);
        border-radius: 5px;
    }

    .styled-table-container::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(90deg, #A78BFA, #22D3EE);
    }

    .styled-table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'JetBrains Mono', 'SF Mono', monospace;
        font-size: 0.85rem;
    }

    .styled-table thead tr {
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(6, 182, 212, 0.1) 100%);
    }

    .styled-table th.header,
    .styled-table th.header-first {
        color: #8B5CF6;
        font-family: 'DM Sans', -apple-system, sans-serif;
        font-weight: 600;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding: 14px 16px;
        border-bottom: 2px solid rgba(139, 92, 246, 0.3);
        text-align: left;
        white-space: nowrap;
    }

    .styled-table th.header-first {
        color: #F59E0B;
        position: sticky;
        left: 0;
        z-index: 2;
        background: linear-gradient(135deg, rgba(26, 22, 37, 0.98) 0%, rgba(15, 11, 30, 0.98) 100%);
        box-shadow: 2px 0 8px rgba(0, 0, 0, 0.3);
    }

    .styled-table tbody tr {
        background: rgba(26, 22, 37, 0.6);
        transition: all 0.2s ease;
    }

    .styled-table tbody tr:nth-child(even) {
        background: rgba(37, 32, 51, 0.7);
    }

    .styled-table tbody tr:hover {
        background: rgba(139, 92, 246, 0.12);
    }

    .styled-table td.cell,
    .styled-table td.cell-first {
        color: #E2E8F0;
        padding: 12px 16px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        vertical-align: middle;
        text-align: right;
    }

    .styled-table td.cell-first {
        color: #FFFFFF;
        font-weight: 500;
        font-family: 'DM Sans', -apple-system, sans-serif;
        text-align: left;
        position: sticky;
        left: 0;
        z-index: 1;
        background: rgba(26, 22, 37, 0.98);
        box-shadow: 2px 0 8px rgba(0, 0, 0, 0.3);
    }

    .styled-table tbody tr:nth-child(even) td.cell-first {
        background: rgba(37, 32, 51, 0.98);
    }

    .styled-table tbody tr:hover td.cell-first {
        background: rgba(139, 92, 246, 0.25);
    }

    .styled-table tbody tr:hover td {
        color: #F8FAFC;
    }

    .styled-table tbody tr:hover td.cell-first {
        color: #A78BFA;
    }

    /* ============================================================
       STATUS BADGES (Valuation Matrix)
       ============================================================ */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-family: 'DM Sans', -apple-system, sans-serif;
        font-weight: 600;
        font-size: 0.85rem;
        white-space: nowrap;
    }

    .status-very-cheap { color: #3B82F6 !important; }
    .status-cheap { color: #22C55E !important; }
    .status-fair { color: #FFD666 !important; }
    .status-expensive { color: #FF9F43 !important; }
    .status-very-expensive { color: #FF6B6B !important; }

    /* Valuation Legend - Colored Dots with Gradients */
    .valuation-legend {
        display: flex;
        gap: 16px;
        padding: 8px 0;
        flex-wrap: wrap;
        font-family: 'DM Sans', -apple-system, sans-serif;
        font-size: 0.8rem;
    }

    .legend-item {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        color: #E2E8F0;
    }

    .legend-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
    }

    .legend-dot.very-cheap { background: linear-gradient(135deg, #60A5FA 0%, #3B82F6 100%); }
    .legend-dot.cheap { background: linear-gradient(135deg, #4ADE80 0%, #22C55E 100%); }
    .legend-dot.fair { background: linear-gradient(135deg, #FDE047 0%, #FFD666 100%); }
    .legend-dot.expensive { background: linear-gradient(135deg, #FDBA74 0%, #FF9F43 100%); }
    .legend-dot.very-expensive { background: linear-gradient(135deg, #FCA5A5 0%, #FF6B6B 100%); }
    </style>
    '''


def render_valuation_legend() -> str:
    """
    Render HTML legend for valuation status colors (5-level percentile).

    Returns:
        HTML string with colored dots and labels for use with st.markdown(html, unsafe_allow_html=True)

    Example:
        >>> st.markdown(render_valuation_legend(), unsafe_allow_html=True)
    """
    return '''
    <div class="valuation-legend">
        <span class="legend-item"><span class="legend-dot very-cheap"></span><b>Rất Rẻ</b> (0-10%)</span>
        <span class="legend-item"><span class="legend-dot cheap"></span><b>Rẻ</b> (10-40%)</span>
        <span class="legend-item"><span class="legend-dot fair"></span><b>Hợp lý</b> (40-70%)</span>
        <span class="legend-item"><span class="legend-dot expensive"></span><b>Đắt</b> (70-90%)</span>
        <span class="legend-item"><span class="legend-dot very-expensive"></span><b>Rất Đắt</b> (90-100%)</span>
    </div>
    '''


def render_valuation_assessment(z_score: float) -> str:
    """
    Render valuation assessment text with colored dot (no emoji).

    Args:
        z_score: Z-score value

    Returns:
        HTML string with assessment text

    Example:
        >>> st.markdown(render_valuation_assessment(-1.5), unsafe_allow_html=True)
    """
    if z_score < -1:
        return '<span class="legend-item"><span class="legend-dot very-cheap"></span><b>Significantly Undervalued</b> - More than 1σ below mean</span>'
    elif z_score < 0:
        return '<span class="legend-item"><span class="legend-dot cheap"></span><b>Undervalued</b> - Below historical mean</span>'
    elif z_score < 1:
        return '<span class="legend-item"><span class="legend-dot fair"></span><b>Fair Value</b> - Near historical mean</span>'
    else:
        return '<span class="legend-item"><span class="legend-dot very-expensive"></span><b>Expensive</b> - More than 1σ above mean</span>'
