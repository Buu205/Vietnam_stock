"""
Dashboard Styles - High-End Financial Editorial
================================================

Premium financial dashboard with luxury editorial aesthetics.
Think The Financial Times meets a luxury watch interface.

Design Direction:
- Aesthetic: HIGH-END FINANCIAL EDITORIAL - Trust, Precision, Elegance
- Typography: Serif (Playfair Display) for headers + Monospace (JetBrains Mono) for data
- Charts: Muted Teal (#4A7C7E) as primary, Champagne Gold (#D4AF37) for accents
- Background: Deep Charcoal with subtle warmth

Color Palette (EDITORIAL):
- Background: Deep Charcoal (#1A1A1A) - Rich, warm black
- Surface: Elevated Charcoal (#242424)
- Accent Gold: Champagne Gold (#D4AF37) - Premium, trustworthy
- Primary Teal: Muted Teal (#4A7C7E) - Sophisticated, not neon
- Text: Warm Whites and Silvers

Usage:
    from WEBAPP.core.styles import get_page_style, get_chart_layout

Created: 2025-12-16
Updated: 2025-12-16 - High-End Financial Editorial redesign
"""

from WEBAPP.core.theme import (
    BRAND, DARK_THEME, CHART_PALETTE,
    SEMANTIC, TYPOGRAPHY, SPACING, RADIUS, SHADOWS
)


def get_page_style() -> str:
    """
    Get premium page-level CSS styling.

    Design: High-End Financial Editorial
    - Background: Deep Charcoal with warmth
    - Typography: Playfair Display (serif) + JetBrains Mono (data)
    - Charts: Muted Teal (#4A7C7E) + Champagne Gold (#D4AF37)
    - Style: The Financial Times meets luxury watch interface

    Returns:
        Complete CSS string for Streamlit markdown injection
    """
    return """
<style>
    /* ============================================================
       FONTS - Financial Editorial Typography
       Playfair Display: Elegant serif for headers (trust, authority)
       JetBrains Mono: Precision monospace for data points
       Merriweather: Readable serif alternative
       ============================================================ */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Merriweather:wght@300;400;700&family=JetBrains+Mono:wght@400;500;600;700&family=DM+Sans:wght@400;500;600&display=swap');

    :root {
        /* ========== EDITORIAL COLOR PALETTE ========== */
        /* Champagne Gold - Premium accent, trust indicator */
        --champagne-gold: #D4AF37;
        --gold-light: #E5C158;
        --gold-dark: #B8962E;

        /* Muted Teal - Sophisticated, not neon */
        --muted-teal: #4A7C7E;
        --teal-light: #5F9A9C;
        --teal-dark: #3A6264;

        /* Deep Charcoal - Warm black background */
        --charcoal-void: #121212;
        --charcoal-deep: #1A1A1A;
        --charcoal-surface: #242424;
        --charcoal-elevated: #2E2E2E;
        --charcoal-hover: #383838;

        /* Rich Navy - Alternative accent */
        --navy-deep: #1A2744;
        --navy-medium: #2A3F5F;

        /* ========== LEGACY BRAND (for compatibility) ========== */
        --brand-blue: #295CA9;
        --brand-teal: #4A7C7E;
        --brand-gold: #D4AF37;

        /* ========== TEXT - WARM CONTRAST ========== */
        --text-white: #FAFAF9;
        --text-bright: #F5F5F4;
        --text-primary: #E7E5E4;
        --text-secondary: #A8A29E;
        --text-muted: #78716C;
        --text-dim: #57534E;

        /* ========== SEMANTIC COLORS (Muted, not neon) ========== */
        --positive: #4A7C7E;
        --positive-light: #5F9A9C;
        --negative: #B45454;
        --negative-light: #D47171;
        --warning: #D4AF37;
        --info: #5B7FA3;

        /* ========== BORDERS & EFFECTS ========== */
        --border-subtle: rgba(168, 162, 158, 0.08);
        --border-medium: rgba(168, 162, 158, 0.15);
        --border-accent: rgba(212, 175, 55, 0.3);
        --border-teal: rgba(74, 124, 126, 0.3);
        --glow-gold: 0 0 30px rgba(212, 175, 55, 0.15);
        --glow-teal: 0 0 20px rgba(74, 124, 126, 0.12);

        /* ========== TYPOGRAPHY - EDITORIAL ========== */
        --font-serif: 'Playfair Display', 'Merriweather', Georgia, serif;
        --font-display: 'DM Sans', -apple-system, sans-serif;
        --font-body: 'DM Sans', -apple-system, sans-serif;
        --font-mono: 'JetBrains Mono', 'SF Mono', monospace;

        /* Legacy aliases */
        --bg-void: var(--charcoal-void);
        --bg-deep: var(--charcoal-deep);
        --bg-surface: var(--charcoal-surface);
        --bg-elevated: var(--charcoal-elevated);
        --bg-hover: var(--charcoal-hover);
    }

    /* ============================================================
       BASE - DEEP CHARCOAL EDITORIAL BACKGROUND
       ============================================================ */
    .stApp {
        background: linear-gradient(170deg,
            var(--charcoal-void) 0%,
            var(--charcoal-deep) 40%,
            var(--charcoal-surface) 100%
        );
        min-height: 100vh;
    }

    .block-container {
        padding: 3rem 5rem 5rem 5rem !important;
        max-width: 1600px;  /* Slightly narrower for editorial feel */
    }

    * {
        font-family: var(--font-body);
    }

    /* ============================================================
       TYPOGRAPHY - FINANCIAL EDITORIAL
       Serif for headers (trust, authority)
       Monospace for data (precision)
       ============================================================ */
    h1, h2, .stTitle {
        font-family: var(--font-serif) !important;
        font-weight: 600 !important;
        letter-spacing: -0.01em;
    }

    h3, .stSubheader {
        font-family: var(--font-display) !important;
        font-weight: 500 !important;
        letter-spacing: 0.02em;
    }

    /* Page Title - Elegant Serif with Gold Accent */
    h1 {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        color: var(--text-white) !important;
        background: linear-gradient(135deg,
            var(--text-white) 0%,
            var(--champagne-gold) 100%
        );
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem !important;
        line-height: 1.2;
    }

    /* Section Headers - Editorial Style with Gold underline */
    h3 {
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        color: var(--text-secondary) !important;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin-bottom: 1.5rem !important;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid var(--border-subtle);
        position: relative;
    }

    h3::after {
        content: '';
        position: absolute;
        bottom: -1px;
        left: 0;
        width: 50px;
        height: 2px;
        background: var(--champagne-gold);
    }

    /* Body Text */
    p, span, div {
        color: var(--text-primary);
    }

    /* Subtitle - Elegant muted */
    .stMarkdown p:first-child {
        font-size: 1.05rem;
        color: var(--text-secondary);
        font-weight: 400;
        font-style: italic;
    }

    /* Strong text - Champagne Gold accent */
    strong, b {
        color: var(--champagne-gold);
        font-weight: 600;
    }

    /* ============================================================
       METRIC CARDS - EDITORIAL LUXURY
       Subtle elegance, not flashy
       ============================================================ */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg,
            rgba(36, 36, 36, 0.95) 0%,
            rgba(46, 46, 46, 0.85) 100%
        );
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid var(--border-subtle);
        border-radius: 8px;  /* Less rounded - more editorial */
        padding: 1.75rem 2rem !important;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }

    /* Top accent bar - Champagne Gold */
    [data-testid="stMetric"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--champagne-gold), var(--gold-light));
        opacity: 0.7;
    }

    /* Subtle corner accent */
    [data-testid="stMetric"]::after {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 100%;
        height: 100%;
        background: radial-gradient(circle, rgba(212, 175, 55, 0.05) 0%, transparent 70%);
        pointer-events: none;
    }

    [data-testid="stMetric"]:hover {
        border-color: var(--border-accent);
        box-shadow: var(--glow-gold);
        transform: translateY(-2px);
    }

    [data-testid="stMetric"]:hover::before {
        opacity: 1;
    }

    /* Metric Label - Editorial uppercase */
    [data-testid="stMetricLabel"] {
        font-family: var(--font-display) !important;
        font-size: 0.7rem !important;
        font-weight: 500 !important;
        color: var(--text-muted) !important;
        text-transform: uppercase;
        letter-spacing: 0.15em;
    }

    /* Metric Value - Precise monospace */
    [data-testid="stMetricValue"] {
        font-family: var(--font-mono) !important;
        font-size: 1.85rem !important;
        font-weight: 600 !important;
        color: var(--text-white) !important;
        letter-spacing: -0.01em;
    }

    /* Metric Delta - Muted colors */
    [data-testid="stMetricDelta"] {
        font-family: var(--font-mono) !important;
        font-size: 0.8rem !important;
        font-weight: 500;
    }

    [data-testid="stMetricDelta"] svg {
        stroke-width: 2.5;
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
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        color: var(--text-muted) !important;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        margin-bottom: 1rem;
    }

    /* Sidebar inputs */
    [data-testid="stSidebar"] .stSelectbox > div > div,
    [data-testid="stSidebar"] .stTextInput > div > div {
        background: var(--bg-elevated) !important;
        border: 1px solid var(--border-medium) !important;
        border-radius: 10px;
        color: var(--text-primary);
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
       NAVIGATION - st.navigation() styles
       ============================================================ */
    /* Navigation section headers (Fundamental, Analysis) */
    [data-testid="stSidebar"] [data-testid="stSidebarNavSeparator"],
    [data-testid="stSidebar"] span[data-testid="stSidebarNavSeparator"] {
        color: var(--text-muted) !important;
        font-size: 0.7rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        padding: 0.5rem 0;
    }

    /* Navigation links (page names) */
    [data-testid="stSidebar"] a,
    [data-testid="stSidebar"] [data-testid="stSidebarNavLink"],
    [data-testid="stSidebar"] nav a {
        color: var(--text-secondary) !important;
        font-size: 0.9rem !important;
        font-weight: 500;
        padding: 0.6rem 0.8rem !important;
        border-radius: 8px;
        transition: all 0.2s ease;
        text-decoration: none !important;
    }

    [data-testid="stSidebar"] a:hover,
    [data-testid="stSidebar"] [data-testid="stSidebarNavLink"]:hover {
        color: var(--text-primary) !important;
        background: var(--bg-hover) !important;
    }

    /* Active navigation link */
    [data-testid="stSidebar"] a[aria-current="page"],
    [data-testid="stSidebar"] [data-testid="stSidebarNavLink"][aria-current="page"] {
        color: var(--brand-teal) !important;
        background: rgba(0, 155, 135, 0.1) !important;
        font-weight: 600;
    }

    /* Navigation container */
    [data-testid="stSidebar"] nav {
        padding: 0.5rem 0;
    }

    /* Navigation separator text */
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: var(--text-secondary) !important;
    }

    /* ============================================================
       TABS - EDITORIAL PAPER TAB STYLE
       Like physical paper tabs or minimalist underscores
       ============================================================ */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent;
        border-radius: 0;
        padding: 0;
        gap: 0;
        border: none;
        border-bottom: 1px solid var(--border-subtle);
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border-radius: 0;
        padding: 0.9rem 2rem;
        font-family: var(--font-display);
        font-weight: 500;
        font-size: 0.9rem;
        color: var(--text-muted);
        transition: all 0.2s ease;
        border: none;
        border-bottom: 2px solid transparent;
        margin-bottom: -1px;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: var(--text-primary);
        background: transparent !important;
    }

    .stTabs [aria-selected="true"] {
        background: transparent !important;
        color: var(--champagne-gold) !important;
        font-weight: 600;
        border-bottom: 2px solid var(--champagne-gold) !important;
        box-shadow: none;
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
       BUTTONS - EDITORIAL ELEGANCE
       ============================================================ */
    .stButton > button {
        background: linear-gradient(135deg, var(--muted-teal), var(--teal-dark)) !important;
        border: none !important;
        border-radius: 6px;
        font-family: var(--font-display);
        font-weight: 500;
        font-size: 0.85rem;
        padding: 0.75rem 1.5rem;
        color: var(--text-white) !important;
        transition: all 0.25s ease;
        box-shadow: 0 2px 8px rgba(74, 124, 126, 0.2);
        letter-spacing: 0.02em;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 16px rgba(74, 124, 126, 0.3);
    }

    .stButton > button:active {
        transform: translateY(0);
    }

    /* Download Button - Elegant Outlined with Gold */
    .stDownloadButton > button {
        background: transparent !important;
        border: 1px solid var(--champagne-gold) !important;
        color: var(--champagne-gold) !important;
        border-radius: 6px;
    }

    .stDownloadButton > button:hover {
        background: rgba(212, 175, 55, 0.1) !important;
        border-color: var(--gold-light) !important;
        color: var(--gold-light) !important;
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
        font-size: 0.7rem !important;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--text-muted) !important;
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
       CHARTS - EDITORIAL LITHOGRAPH STYLE
       Clean, like a printed technical chart
       ============================================================ */
    .stPlotlyChart {
        background: linear-gradient(135deg,
            var(--charcoal-surface) 0%,
            var(--charcoal-elevated) 100%
        );
        border-radius: 8px;
        padding: 1.25rem;
        border: 1px solid var(--border-subtle);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
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
       FOOTER CAPTION
       ============================================================ */
    .stCaption {
        font-family: var(--font-mono) !important;
        font-size: 0.7rem !important;
        color: var(--text-dim) !important;
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
        color: #718096 !important;
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
    Get consistent Plotly chart layout - Financial Editorial Theme.

    Charts use Muted Teal (#4A7C7E) as primary, Champagne Gold (#D4AF37) as accent.
    Grid lines are extremely faint (dotted style), like a printed lithograph.

    Args:
        title: Chart title
        height: Chart height in pixels

    Returns:
        Plotly layout dict
    """
    return {
        'title': {
            'text': title,
            'font': {'family': 'Playfair Display, Georgia, serif', 'size': 16, 'color': '#E7E5E4'},
            'x': 0,
            'xanchor': 'left'
        },
        'height': height,
        'autosize': True,
        'margin': {'l': 60, 'r': 40, 't': 60, 'b': 60, 'pad': 4},
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'font': {
            'family': 'JetBrains Mono, monospace',
            'size': 11,
            'color': '#A8A29E'
        },
        'xaxis': {
            'gridcolor': 'rgba(168, 162, 158, 0.06)',  # Extremely faint
            'griddash': 'dot',  # Dotted grid lines (editorial lithograph)
            'zerolinecolor': 'rgba(168, 162, 158, 0.1)',
            'tickfont': {'size': 10, 'color': '#78716C', 'family': 'JetBrains Mono'},
            'linecolor': 'rgba(168, 162, 158, 0.08)',
            'tickangle': -45,
            'automargin': True,
            'type': 'category',
            'categoryorder': 'array',
            'nticks': 10,
        },
        'yaxis': {
            'gridcolor': 'rgba(168, 162, 158, 0.06)',  # Extremely faint
            'griddash': 'dot',  # Dotted grid lines
            'zerolinecolor': 'rgba(168, 162, 158, 0.1)',
            'tickfont': {'size': 10, 'color': '#78716C', 'family': 'JetBrains Mono'},
            'linecolor': 'rgba(168, 162, 158, 0.08)',
            'automargin': True,
            'fixedrange': False,
        },
        'legend': {
            'font': {'size': 11, 'color': '#E7E5E4', 'family': 'DM Sans'},
            'bgcolor': 'rgba(0,0,0,0)',
            'bordercolor': 'rgba(0,0,0,0)',
        },
        'hoverlabel': {
            'bgcolor': '#242424',
            'bordercolor': '#D4AF37',  # Champagne Gold border
            'font': {'family': 'JetBrains Mono', 'size': 12, 'color': '#F5F5F4'}
        }
    }


# ============================================================
# CHART COLORS - FINANCIAL EDITORIAL PALETTE
# ============================================================

# Primary: Muted Teal (#4A7C7E) - Sophisticated, not neon
# Accent: Champagne Gold (#D4AF37) - Premium, trustworthy
CHART_COLORS = {
    'primary': '#4A7C7E',       # Muted Teal - MAIN CHART COLOR
    'secondary': '#5B7FA3',     # Muted Blue
    'tertiary': '#D4AF37',      # Champagne Gold
    'quaternary': '#5F9A9C',    # Teal Light
    'quinary': '#7A9AB8',       # Blue Light
    'positive': '#4A7C7E',      # Muted Teal
    'negative': '#B45454',      # Muted Red (not neon)
    'neutral': '#78716C',       # Warm Gray
    # Semantic aliases
    'warning': '#D4AF37',       # Champagne Gold - fair value
    'danger': '#B45454',        # Muted Red - losses
    'success': '#4A7C7E',       # Muted Teal - profits
    'info': '#5B7FA3',          # Muted Blue - informational
    # Legacy compatibility
    'brand_teal': '#4A7C7E',
    'brand_gold': '#D4AF37',
}

# Sequential palette for multi-series charts
BAR_COLORS = [
    '#4A7C7E',  # Muted Teal (Primary)
    '#D4AF37',  # Champagne Gold
    '#5B7FA3',  # Muted Blue
    '#5F9A9C',  # Teal Light
    '#B8962E',  # Gold Dark
    '#7A9AB8',  # Blue Light
    '#3A6264',  # Teal Dark
    '#E5C158',  # Gold Light
]

# Candlestick/Distribution chart colors
DISTRIBUTION_COLORS = {
    'body': '#4A7C7E',                      # Muted Teal
    'body_fill': 'rgba(74, 124, 126, 0.35)', # Teal transparent
    'whisker': '#5F9A9C',                   # Teal Light
    'current_dot': '#D4AF37',               # Champagne Gold (current value)
    'median': '#D4AF37',                    # Champagne Gold
}

# Valuation assessment colors (muted, not neon)
ASSESSMENT_COLORS = {
    'undervalued': '#4A7C7E',     # Muted Teal - Good
    'fair': '#D4AF37',            # Champagne Gold - Neutral
    'expensive': '#B45454',       # Muted Red - Warning
    'very_cheap': '#3A6264',      # Teal Dark
    'cheap': '#5F9A9C',           # Teal Light
    'very_expensive': '#8B3A3A',  # Dark Red
}

# Line chart with bands colors (hatched pattern effect via opacity)
BAND_COLORS = {
    'main_line': '#4A7C7E',                 # Muted Teal
    'median_line': '#D4AF37',               # Champagne Gold
    'mean_line': '#E7E5E4',                 # White/Silver for mean
    'band_1sd': 'rgba(212, 175, 55, 0.08)', # Gold band (very subtle)
    'band_2sd': 'rgba(74, 124, 126, 0.06)', # Teal band (extremely subtle)
    'sd_line_positive': '#B45454',          # Red for +SD
    'sd_line_negative': '#4A7C7E',          # Teal for -SD
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
