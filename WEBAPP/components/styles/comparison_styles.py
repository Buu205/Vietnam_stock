"""
BSC vs Consensus Comparison Table Styles
========================================
Premium Crypto Terminal design with:
- OLED-optimized dark theme
- Glassmorphism effects
- Non-semantic source markers (Purple/Cyan/Amber/Pink)
- Semantic insight badges (Green=Bull, Red=Bear)
- Sparkline spread visualization

Design: Crypto Terminal Glassmorphism
Theme: Purple #8B5CF6 / Cyan #06B6D4 / Amber #F59E0B
Font: Space Grotesk (display), DM Sans (body), JetBrains Mono (data)

Updated: 2026-01-04 - Redesigned color system to avoid HCM/Bull & VCI/Bear confusion
"""

# Color palette - Crypto Terminal Theme
COLORS = {
    # Backgrounds (OLED optimized)
    'bg_void': '#0F0B1E',           # Deep purple-black
    'bg_primary': '#0F172A',        # Slate 900
    'bg_secondary': '#1E293B',      # Slate 800
    'bg_surface': '#1A1625',        # Card surface
    'bg_elevated': '#252033',       # Elevated cards
    'bg_card': '#1E293B',           # Card background
    'bg_hover': '#2D2640',          # Hover state (purple tint)

    # Borders
    'border': 'rgba(255, 255, 255, 0.08)',
    'border_hover': 'rgba(139, 92, 246, 0.3)',
    'border_solid': '#334155',

    # Text
    'text_primary': '#F8FAFC',      # Slate 50
    'text_secondary': '#94A3B8',    # Slate 400
    'text_muted': '#64748B',        # Slate 500
    'text_accent': '#C4B5FD',       # Purple pale

    # Brand colors
    'brand_teal': '#00C9AD',        # Brand teal (kept for compatibility)
    'brand_teal_bg': 'rgba(0, 201, 173, 0.15)',
    'brand_purple': '#8B5CF6',      # Primary accent
    'brand_cyan': '#06B6D4',        # Secondary accent
    'brand_amber': '#F59E0B',       # Tertiary accent

    # Semantic colors (Bull/Bear) - DISTINCT from source markers
    'bullish_strong': '#10B981',    # Emerald 500 - Strong Bull
    'bullish': '#34D399',           # Emerald 400 - Bull
    'bullish_light': '#6EE7B7',     # Emerald 300 - Light Bull
    'bearish_strong': '#EF4444',    # Red 500 - Strong Bear
    'bearish': '#F87171',           # Red 400 - Bear
    'bearish_light': '#FCA5A5',     # Red 300 - Light Bear
    'aligned': '#64748B',           # Slate 500 - Neutral
    'divergent': '#FB923C',         # Orange 400 - High variance

    # Legacy (kept for compatibility)
    'bullish_moderate': '#34D399',
    'bearish_moderate': '#F87171',
    'purple': '#8B5CF6',
    'amber': '#F59E0B',
}

# =============================================================================
# SOURCE MARKERS - Non-semantic colors (NOT green/red)
# =============================================================================
# Design principle: Sources should be visually distinct but NOT carry
# bullish/bearish meaning. Green/Red are reserved for insight signals.
SOURCE_MARKERS = {
    'BSC': {
        'color': '#8B5CF6',         # Electric Purple (Primary)
        'color_light': '#A78BFA',
        'label': 'BSC',
        'short': 'B',
        'glow': 'rgba(139, 92, 246, 0.4)',
    },
    'HCM': {
        'color': '#06B6D4',         # Cyan (Secondary) - NOT green anymore
        'color_light': '#22D3EE',
        'label': 'HCM',
        'short': 'H',
        'glow': 'rgba(6, 182, 212, 0.4)',
    },
    'SSI': {
        'color': '#F59E0B',         # Amber (Tertiary)
        'color_light': '#FBBF24',
        'label': 'SSI',
        'short': 'S',
        'glow': 'rgba(245, 158, 11, 0.4)',
    },
    'VCI': {
        'color': '#EC4899',         # Pink/Magenta - NOT red anymore
        'color_light': '#F472B6',
        'label': 'VCI',
        'short': 'V',
        'glow': 'rgba(236, 72, 153, 0.4)',
    },
}


def get_marker_html(source: str, size: int = 10, with_glow: bool = False) -> str:
    """Generate HTML for a colored circle marker with optional glow effect."""
    config = SOURCE_MARKERS.get(source.upper(), {'color': '#64748B', 'short': '?', 'glow': 'none'})
    glow_style = f'box-shadow: 0 0 8px {config.get("glow", "none")};' if with_glow else ''
    return f'''<span style="display:inline-block;width:{size}px;height:{size}px;border-radius:50%;
        background:{config["color"]};{glow_style}"></span>'''


def get_marker_with_label(source: str, with_glow: bool = False) -> str:
    """Generate HTML for marker with label and optional glow effect."""
    config = SOURCE_MARKERS.get(source.upper(), {'color': '#64748B', 'label': source, 'glow': 'none'})
    glow_style = f'box-shadow: 0 0 6px {config.get("glow", "none")};' if with_glow else ''
    return f'''
    <span style="display:inline-flex;align-items:center;gap:6px;">
        <span style="display:inline-flex;align-items:center;justify-content:center;
            width:18px;height:18px;border-radius:50%;background:{config['color']};{glow_style}
            font-size:9px;font-weight:700;color:#fff;">
            {config.get('short', '?')}
        </span>
        <span style="font-size:12px;color:{config['color']};font-weight:600;
            font-family:'JetBrains Mono',monospace;">{config['label']}</span>
    </span>
    '''

# =============================================================================
# INSIGHT CONFIG - Semantic colors (Green=Bull, Red=Bear)
# =============================================================================
# Design principle: Insights carry semantic meaning about BSC vs Consensus.
# These colors are clearly distinct from source markers above.
INSIGHT_CONFIG = {
    'strong_bullish': {
        'label': 'Strong Bull',
        'color': '#10B981',         # Emerald 500 - Clear bullish signal
        'bg': 'rgba(16, 185, 129, 0.15)',
        'border': 'rgba(16, 185, 129, 0.4)',
        'icon': '▲▲',
        'icon_svg': '<svg viewBox="0 0 24 24" fill="currentColor" width="14" height="14"><path d="M12 2L2 14h7v8h6v-8h7L12 2z"/></svg>',
    },
    'bullish_gap': {
        'label': 'Bullish',
        'color': '#34D399',         # Emerald 400 - Moderate bullish
        'bg': 'rgba(52, 211, 153, 0.12)',
        'border': 'rgba(52, 211, 153, 0.35)',
        'icon': '▲',
        'icon_svg': '<svg viewBox="0 0 24 24" fill="currentColor" width="12" height="12"><path d="M12 4L3 15h18L12 4z"/></svg>',
    },
    'aligned': {
        'label': 'Aligned',
        'color': '#94A3B8',         # Slate 400 - Neutral
        'bg': 'rgba(148, 163, 184, 0.1)',
        'border': 'rgba(148, 163, 184, 0.25)',
        'icon': '●',
        'icon_svg': '<svg viewBox="0 0 24 24" fill="currentColor" width="10" height="10"><circle cx="12" cy="12" r="6"/></svg>',
    },
    'high_variance': {
        'label': 'Divergent',
        'color': '#FB923C',         # Orange 400 - Warning/Divergent
        'bg': 'rgba(251, 146, 60, 0.12)',
        'border': 'rgba(251, 146, 60, 0.35)',
        'icon': '◆',
        'icon_svg': '<svg viewBox="0 0 24 24" fill="currentColor" width="12" height="12"><path d="M12 2L22 12L12 22L2 12L12 2z"/></svg>',
    },
    'bearish_gap': {
        'label': 'Bearish',
        'color': '#F87171',         # Red 400 - Moderate bearish
        'bg': 'rgba(248, 113, 113, 0.12)',
        'border': 'rgba(248, 113, 113, 0.35)',
        'icon': '▼',
        'icon_svg': '<svg viewBox="0 0 24 24" fill="currentColor" width="12" height="12"><path d="M12 20L3 9h18L12 20z"/></svg>',
    },
    'strong_bearish': {
        'label': 'Strong Bear',
        'color': '#EF4444',         # Red 500 - Clear bearish signal
        'bg': 'rgba(239, 68, 68, 0.15)',
        'border': 'rgba(239, 68, 68, 0.4)',
        'icon': '▼▼',
        'icon_svg': '<svg viewBox="0 0 24 24" fill="currentColor" width="14" height="14"><path d="M12 22L2 10h7V2h6v8h7L12 22z"/></svg>',
    },
    'no_data': {
        'label': 'N/A',
        'color': '#475569',         # Slate 600 - No data
        'bg': 'rgba(71, 85, 105, 0.1)',
        'border': 'rgba(71, 85, 105, 0.2)',
        'icon': '—',
        'icon_svg': '<svg viewBox="0 0 24 24" fill="currentColor" width="12" height="12"><rect x="4" y="11" width="16" height="2" rx="1"/></svg>',
    },
}


def get_comparison_styles() -> str:
    """Return CSS for comparison table with Crypto Terminal Glassmorphism theme."""
    return f"""
<style>
/* Google Fonts Import - Crypto Terminal Typography */
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=DM+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* CSS Variables for Crypto Terminal Theme */
:root {{
    --ct-purple: #8B5CF6;
    --ct-purple-light: #A78BFA;
    --ct-purple-glow: rgba(139, 92, 246, 0.4);
    --ct-cyan: #06B6D4;
    --ct-cyan-light: #22D3EE;
    --ct-cyan-glow: rgba(6, 182, 212, 0.4);
    --ct-amber: #F59E0B;
    --ct-pink: #EC4899;
    --ct-emerald: #10B981;
    --ct-red: #EF4444;
    --ct-bg-void: #0F0B1E;
    --ct-bg-surface: #1A1625;
    --ct-bg-elevated: #252033;
    --ct-glass-bg: rgba(255, 255, 255, 0.03);
    --ct-glass-border: rgba(255, 255, 255, 0.08);
    --ct-glass-blur: blur(12px);
}}

/* Comparison Container - Glassmorphism */
.comparison-container {{
    font-family: 'DM Sans', -apple-system, sans-serif;
    background: linear-gradient(180deg, {COLORS['bg_void']} 0%, {COLORS['bg_surface']} 100%);
    border-radius: 16px;
    overflow: hidden;
    border: 1px solid {COLORS['border']};
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
}}

/* Filter Bar - Glass Effect */
.filter-bar {{
    display: flex;
    gap: 12px;
    padding: 16px 20px;
    background: rgba(255, 255, 255, 0.03);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-bottom: 1px solid {COLORS['border']};
    flex-wrap: wrap;
    align-items: center;
}}

.filter-item {{
    display: flex;
    flex-direction: column;
    gap: 4px;
}}

.filter-label {{
    font-size: 11px;
    font-weight: 600;
    color: {COLORS['text_accent']};
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-family: 'Space Grotesk', sans-serif;
}}

/* Legend Bar - Purple accent */
.legend-bar {{
    display: flex;
    gap: 20px;
    padding: 14px 20px;
    background: linear-gradient(90deg, rgba(139, 92, 246, 0.08) 0%, rgba(6, 182, 212, 0.05) 100%);
    border-bottom: 1px solid {COLORS['border']};
    align-items: center;
    flex-wrap: wrap;
}}

.legend-title {{
    font-size: 11px;
    font-weight: 600;
    color: {COLORS['text_accent']};
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-family: 'Space Grotesk', sans-serif;
    margin-right: 12px;
}}

.legend-item {{
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    color: {COLORS['text_secondary']};
    font-family: 'JetBrains Mono', monospace;
    position: relative;
    transition: all 0.2s ease;
}}

.legend-item:hover {{
    color: {COLORS['text_primary']};
}}

.legend-dot {{
    width: 20px;
    height: 20px;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    position: relative;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    transition: all 0.2s ease;
}}

.legend-dot:hover {{
    transform: scale(1.1);
}}

.legend-dot::after {{
    content: attr(data-letter);
    font-size: 9px;
    font-weight: 700;
    color: #fff;
    font-family: 'JetBrains Mono', monospace;
}}

/* Comparison Table - Crypto Terminal Style */
.comparison-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
    font-family: 'DM Sans', sans-serif;
}}

.comparison-table thead {{
    position: sticky;
    top: 0;
    z-index: 10;
}}

.comparison-table th {{
    background: linear-gradient(180deg, {COLORS['bg_surface']} 0%, {COLORS['bg_void']} 100%);
    color: {COLORS['text_accent']};
    font-weight: 600;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    padding: 14px 16px;
    text-align: left;
    border-bottom: 2px solid rgba(139, 92, 246, 0.3);
    white-space: nowrap;
    font-family: 'Space Grotesk', sans-serif;
}}

/* Column header colors - match source markers */
.comparison-table th.col-bsc {{ color: #8B5CF6; }}
.comparison-table th.col-hcm {{ color: #06B6D4; }}
.comparison-table th.col-ssi {{ color: #F59E0B; }}
.comparison-table th.col-vci {{ color: #EC4899; }}
.comparison-table th.col-cons {{ color: #00C9AD; }}

.comparison-table th.center {{
    text-align: center;
}}

.comparison-table th.right {{
    text-align: right;
}}

.comparison-table tbody tr {{
    border-bottom: 1px solid {COLORS['border']};
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
}}

.comparison-table tbody tr:hover {{
    background: {COLORS['bg_hover']};
    border-left: 3px solid #8B5CF6;
}}

.comparison-table tbody tr:nth-child(even) {{
    background: rgba(26, 22, 37, 0.5);
}}

.comparison-table tbody tr:nth-child(even):hover {{
    background: {COLORS['bg_hover']};
}}

.comparison-table td {{
    padding: 12px 16px;
    color: {COLORS['text_primary']};
    vertical-align: middle;
    font-family: 'JetBrains Mono', monospace;
}}

.comparison-table td.center {{
    text-align: center;
}}

.comparison-table td.right {{
    text-align: right;
}}

/* Ticker Cell - Enhanced */
.ticker-cell {{
    display: flex;
    align-items: center;
    gap: 12px;
}}

.expand-arrow {{
    color: {COLORS['text_muted']};
    font-size: 10px;
    transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}}

.expand-arrow.expanded {{
    transform: rotate(90deg);
    color: #8B5CF6;
}}

.ticker-symbol {{
    font-weight: 700;
    color: {COLORS['brand_teal']};
    font-family: 'JetBrains Mono', monospace;
    font-size: 14px;
    letter-spacing: 0.02em;
    transition: all 0.2s ease;
}}

.ticker-symbol:hover {{
    color: #00E5C5;
    text-shadow: 0 0 12px rgba(0, 201, 173, 0.4);
}}

.ticker-sector {{
    font-size: 10px;
    color: {COLORS['text_muted']};
    font-family: 'DM Sans', sans-serif;
    max-width: 100px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}}

/* Price Cells */
.price-value {{
    font-family: 'Space Mono', monospace;
    font-weight: 500;
}}

.price-current {{
    color: {COLORS['text_secondary']};
}}

.price-bsc {{
    color: {COLORS['text_primary']};
    font-weight: 600;
}}

/* Sparkline Spread - Premium Terminal Style */
.sparkline-container {{
    display: flex;
    align-items: center;
    gap: 6px;
    min-width: 160px;
}}

.sparkline-bar {{
    flex: 1;
    height: 28px;
    background: linear-gradient(180deg, rgba(15, 11, 30, 0.8) 0%, rgba(26, 22, 37, 0.6) 100%);
    border-radius: 6px;
    position: relative;
    border: 1px solid {COLORS['border']};
    min-width: 120px;
    overflow: visible;
}}

.sparkline-marker {{
    position: absolute;
    top: 50%;
    transform: translate(-50%, -50%);
    width: 20px;
    height: 20px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 2;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 2px 8px rgba(0,0,0,0.4);
    cursor: help;
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px;
    font-weight: 700;
    color: #fff;
}}

.sparkline-marker:hover {{
    transform: translate(-50%, -50%) scale(1.25);
    z-index: 10;
    box-shadow: 0 0 12px var(--marker-glow, rgba(139, 92, 246, 0.5));
}}

/* Marker glow colors - match source markers */
.sparkline-marker[data-source="BSC"] {{ --marker-glow: rgba(139, 92, 246, 0.6); }}
.sparkline-marker[data-source="HCM"] {{ --marker-glow: rgba(6, 182, 212, 0.6); }}
.sparkline-marker[data-source="SSI"] {{ --marker-glow: rgba(245, 158, 11, 0.6); }}
.sparkline-marker[data-source="VCI"] {{ --marker-glow: rgba(236, 72, 153, 0.6); }}

.sparkline-range {{
    position: absolute;
    top: 50%;
    height: 4px;
    background: linear-gradient(90deg, rgba(6, 182, 212, 0.4) 0%, rgba(139, 92, 246, 0.4) 100%);
    transform: translateY(-50%);
    border-radius: 2px;
    opacity: 0.6;
}}

/* Max Deviation Badge */
.max-dev-badge {{
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 8px;
    border-radius: 6px;
    font-family: 'Space Mono', monospace;
    font-size: 12px;
    font-weight: 600;
    white-space: nowrap;
}}

.max-dev-positive {{
    background: rgba(34, 197, 94, 0.15);
    color: #22C55E;
    border: 1px solid rgba(34, 197, 94, 0.3);
}}

.max-dev-negative {{
    background: rgba(239, 68, 68, 0.15);
    color: #EF4444;
    border: 1px solid rgba(239, 68, 68, 0.3);
}}

/* Insight Badge - Premium Glassmorphism */
.insight-badge {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    white-space: nowrap;
    font-family: 'DM Sans', sans-serif;
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    transition: all 0.2s ease;
}}

.insight-badge:hover {{
    transform: scale(1.02);
}}

/* Heatmap Colors - Semantic Bull/Bear (NEW: Clear distinction from source markers) */
/* Bull colors: Emerald family (#10B981 base) */
.heatmap-strong-bullish {{
    background: rgba(16, 185, 129, 0.2);
    color: #10B981;
    border: 1px solid rgba(16, 185, 129, 0.35);
}}
.heatmap-bullish {{
    background: rgba(52, 211, 153, 0.15);
    color: #34D399;
    border: 1px solid rgba(52, 211, 153, 0.3);
}}
.heatmap-light-bullish {{
    background: rgba(110, 231, 183, 0.1);
    color: #6EE7B7;
    border: 1px solid rgba(110, 231, 183, 0.25);
}}

/* Neutral/Aligned */
.heatmap-aligned {{
    background: rgba(148, 163, 184, 0.1);
    color: #94A3B8;
    border: 1px solid rgba(148, 163, 184, 0.2);
}}

/* Bear colors: Red family (#EF4444 base) */
.heatmap-light-bearish {{
    background: rgba(252, 165, 165, 0.12);
    color: #FCA5A5;
    border: 1px solid rgba(252, 165, 165, 0.25);
}}
.heatmap-bearish {{
    background: rgba(248, 113, 113, 0.15);
    color: #F87171;
    border: 1px solid rgba(248, 113, 113, 0.3);
}}
.heatmap-strong-bearish {{
    background: rgba(239, 68, 68, 0.2);
    color: #EF4444;
    border: 1px solid rgba(239, 68, 68, 0.35);
}}

/* Expanded Detail Row */
.expanded-detail {{
    background: {COLORS['bg_primary']};
    padding: 0;
}}

.detail-container {{
    background: linear-gradient(135deg, {COLORS['bg_secondary']} 0%, rgba(30, 41, 59, 0.8) 100%);
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    margin: 8px 16px 16px 40px;
    overflow: hidden;
}}

.detail-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    background: rgba(0, 201, 173, 0.05);
    border-bottom: 1px solid {COLORS['border']};
}}

.detail-title {{
    font-weight: 700;
    font-size: 16px;
    color: {COLORS['text_primary']};
}}

.detail-subtitle {{
    font-size: 13px;
    color: {COLORS['text_muted']};
}}

/* Detail Table */
.detail-table {{
    width: 100%;
    border-collapse: collapse;
}}

.detail-table th {{
    background: {COLORS['bg_primary']};
    color: {COLORS['text_muted']};
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    padding: 10px 14px;
    text-align: center;
    border-bottom: 1px solid {COLORS['border']};
}}

.detail-table th:first-child {{
    text-align: left;
    width: 120px;
}}

.detail-table td {{
    padding: 12px 14px;
    text-align: center;
    border-bottom: 1px solid {COLORS['border']};
    font-family: 'Space Mono', monospace;
}}

.detail-table td:first-child {{
    text-align: left;
    font-family: 'IBM Plex Sans', sans-serif;
    font-weight: 500;
    color: {COLORS['text_secondary']};
}}

.detail-table tr:last-child td {{
    border-bottom: none;
}}

.detail-value {{
    font-weight: 500;
    color: {COLORS['text_primary']};
}}

.detail-deviation {{
    font-size: 11px;
    margin-top: 2px;
}}

.dev-positive {{
    color: #22C55E;
}}

.dev-negative {{
    color: #EF4444;
}}

.dev-neutral {{
    color: {COLORS['text_muted']};
}}

/* Range Chart */
.range-chart {{
    padding: 16px 20px;
    border-top: 1px solid {COLORS['border']};
}}

.range-row {{
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;
}}

.range-label {{
    width: 80px;
    font-size: 12px;
    font-weight: 500;
    color: {COLORS['text_secondary']};
}}

.range-bar {{
    flex: 1;
    height: 8px;
    background: {COLORS['bg_primary']};
    border-radius: 4px;
    position: relative;
    overflow: visible;
}}

.range-fill {{
    position: absolute;
    height: 100%;
    background: linear-gradient(to right, {COLORS['brand_teal']}, #22C55E);
    border-radius: 4px;
    opacity: 0.6;
}}

.range-marker {{
    position: absolute;
    top: 50%;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    transform: translate(-50%, -50%);
    border: 2px solid {COLORS['text_primary']};
}}

.range-marker-bsc {{
    background: #3B82F6;
}}

.range-marker-consensus {{
    background: #22C55E;
}}

/* Summary Cards */
.summary-cards {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 12px;
    padding: 16px 20px;
    background: {COLORS['bg_secondary']};
    border-bottom: 1px solid {COLORS['border']};
}}

.summary-card {{
    background: {COLORS['bg_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 14px 16px;
    text-align: center;
}}

.summary-card-value {{
    font-size: 28px;
    font-weight: 700;
    font-family: 'Space Mono', monospace;
    line-height: 1.2;
}}

.summary-card-label {{
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-top: 4px;
    color: {COLORS['text_muted']};
}}

.summary-card-desc {{
    font-size: 10px;
    color: {COLORS['text_muted']};
    margin-top: 2px;
}}

/* No Data State */
.no-data {{
    text-align: center;
    padding: 40px 20px;
    color: {COLORS['text_muted']};
}}

/* Responsive */
@media (max-width: 768px) {{
    .comparison-table {{
        font-size: 12px;
    }}

    .comparison-table td,
    .comparison-table th {{
        padding: 10px 12px;
    }}

    .sparkline-container {{
        min-width: 100px;
    }}

    .detail-container {{
        margin: 8px;
    }}
}}

/* Scroll container */
.table-scroll {{
    overflow-x: auto;
    max-height: 600px;
    overflow-y: auto;
}}
</style>
"""


def get_heatmap_class(dev_pct: float) -> str:
    """Return CSS class for heatmap coloring based on deviation percentage."""
    if dev_pct is None:
        return "heatmap-aligned"

    if dev_pct >= 15:
        return "heatmap-strong-bullish"
    elif dev_pct >= 10:
        return "heatmap-bullish"
    elif dev_pct >= 5:
        return "heatmap-light-bullish"
    elif dev_pct <= -15:
        return "heatmap-strong-bearish"
    elif dev_pct <= -10:
        return "heatmap-bearish"
    elif dev_pct <= -5:
        return "heatmap-light-bearish"
    else:
        return "heatmap-aligned"


def format_insight_badge(insight: str) -> str:
    """Generate HTML for insight badge with glassmorphism effect."""
    config = INSIGHT_CONFIG.get(insight, INSIGHT_CONFIG['no_data'])
    bg = config.get('bg', f"rgba({config['color']}, 0.15)")
    border = config.get('border', f"rgba({config['color']}, 0.4)")

    return f'''
    <span class="insight-badge" style="background:{bg};color:{config['color']};border:1px solid {border};">
        <span style="font-size:13px;">{config['icon']}</span>
        <span style="font-family:'DM Sans',sans-serif;">{config['label']}</span>
    </span>
    '''


def format_max_dev_badge(source: str, dev_pct: float) -> str:
    """Generate HTML for max deviation badge with CSS styled marker."""
    if source is None or dev_pct is None:
        return '<span class="max-dev-badge" style="color: #64748B;">—</span>'

    config = SOURCE_MARKERS.get(source.upper(), {'color': '#64748B', 'short': '?'})
    color_class = 'max-dev-positive' if dev_pct >= 0 else 'max-dev-negative'
    sign = '+' if dev_pct >= 0 else ''

    marker_html = f'''
    <span style="display:inline-flex;align-items:center;justify-content:center;width:14px;height:14px;border-radius:50%;background:{config['color']};margin-right:4px;">
        <span style="font-size:8px;font-weight:700;color:#fff;">{config['short']}</span>
    </span>
    '''

    return f'''
    <span class="max-dev-badge {color_class}">
        {marker_html}{source.upper()} {sign}{dev_pct:.0f}%
    </span>
    '''


def render_sparkline(bsc_val: float, hcm_val: float, ssi_val: float, vci_val: float) -> str:
    """Render sparkline spread visualization with glowing markers."""
    values = {
        'BSC': bsc_val,
        'HCM': hcm_val,
        'SSI': ssi_val,
        'VCI': vci_val,
    }

    # Filter valid values
    valid = {k: v for k, v in values.items() if v is not None and v > 0}

    if len(valid) < 2:
        return '<span class="sparkline-container"><span style="color:#64748B;font-family:JetBrains Mono,monospace;">—</span></span>'

    min_val = min(valid.values())
    max_val = max(valid.values())
    range_val = max_val - min_val

    if range_val == 0:
        # All same value - clustered markers with glow
        markers = ''.join(
            f'''<span style="display:inline-flex;align-items:center;justify-content:center;
                width:18px;height:18px;border-radius:50%;background:{SOURCE_MARKERS[k]["color"]};
                margin:0 2px;font-size:8px;font-weight:700;color:#fff;
                box-shadow:0 0 8px {SOURCE_MARKERS[k].get("glow", "rgba(0,0,0,0.3)")};">
                {SOURCE_MARKERS[k]["short"]}</span>'''
            for k in valid.keys()
        )
        return f'<span class="sparkline-container" style="display:flex;align-items:center;gap:4px;">{markers}</span>'

    # Calculate positions (5-95% to prevent edge clipping)
    def pos(v):
        return int(5 + (v - min_val) / range_val * 90)

    markers_html = ""
    for source, val in valid.items():
        p = pos(val)
        color = SOURCE_MARKERS[source]['color']
        short = SOURCE_MARKERS[source]['short']
        glow = SOURCE_MARKERS[source].get('glow', 'rgba(139, 92, 246, 0.4)')
        # Glowing marker with data attribute for hover effects
        markers_html += f'''
        <span class="sparkline-marker" data-source="{source}"
              style="left:{p}%;background:{color};box-shadow:0 2px 6px {glow};"
              title="{source}: {val:,.0f}">
            {short}
        </span>
        '''

    # Range fill (from min to max consensus, excluding BSC)
    cons_vals = [v for k, v in valid.items() if k != 'BSC']
    if cons_vals:
        cons_min_pos = pos(min(cons_vals))
        cons_max_pos = pos(max(cons_vals))
        range_html = f'''
        <span class="sparkline-range" style="left:{cons_min_pos}%;width:{max(cons_max_pos - cons_min_pos, 4)}%;"></span>
        '''
    else:
        range_html = ""

    return f'''
    <div class="sparkline-container">
        <div class="sparkline-bar">
            {range_html}
            {markers_html}
        </div>
    </div>
    '''


def render_legend_bar() -> str:
    """Render the legend bar HTML with glowing styled dots."""
    items = ""
    for key, config in SOURCE_MARKERS.items():
        glow = config.get('glow', 'rgba(0,0,0,0.3)')
        items += f'''
        <span class="legend-item">
            <span class="legend-dot" style="background:{config['color']};box-shadow:0 0 6px {glow};">
                <span style="font-size:9px;font-weight:700;color:#fff;font-family:'JetBrains Mono',monospace;">
                    {config['short']}
                </span>
            </span>
            <span style="color:{config['color']};font-weight:500;">{config['label']}</span>
        </span>
        '''

    # Add insight legend
    insight_items = ""
    for key, config in [
        ('strong_bullish', INSIGHT_CONFIG['strong_bullish']),
        ('aligned', INSIGHT_CONFIG['aligned']),
        ('strong_bearish', INSIGHT_CONFIG['strong_bearish']),
    ]:
        insight_items += f'''
        <span class="legend-item" style="margin-left:8px;">
            <span style="color:{config['color']};font-size:12px;">{config['icon']}</span>
            <span style="color:{config['color']};font-size:11px;">{config['label']}</span>
        </span>
        '''

    return f'''
    <div class="legend-bar">
        <span class="legend-title">Sources:</span>
        {items}
        <span style="width:1px;height:20px;background:rgba(255,255,255,0.1);margin:0 12px;"></span>
        <span class="legend-title">Signal:</span>
        {insight_items}
    </div>
    '''


def render_summary_cards(stats: dict) -> str:
    """Render summary cards for insight distribution."""
    cards = ""

    # Note: Insight is BSC vs Consensus perspective
    # Bullish = BSC higher than Consensus (BSC optimistic)
    # Bearish = BSC lower than Consensus (BSC conservative)
    card_config = [
        ('overlap', 'Overlap', 'BSC + Consensus', COLORS['brand_teal']),
        ('strong_bullish', 'Strong Bullish', 'BSC >15% cao hơn', COLORS['bullish_strong']),
        ('bullish_gap', 'Bullish Gap', 'BSC cao hơn 5-15%', COLORS['bullish_moderate']),
        ('aligned', 'Aligned', 'Chênh lệch ±5%', COLORS['text_muted']),
        ('bearish_gap', 'Bearish Gap', 'BSC thấp hơn 5-15%', COLORS['bearish_moderate']),
        ('strong_bearish', 'Strong Bearish', 'BSC >15% thấp hơn', COLORS['bearish_strong']),
    ]

    for key, label, desc, color in card_config:
        value = stats.get(key, 0)
        cards += f'''
        <div class="summary-card">
            <div class="summary-card-value" style="color: {color};">{value}</div>
            <div class="summary-card-label">{label}</div>
            <div class="summary-card-desc">{desc}</div>
        </div>
        '''

    return f'<div class="summary-cards">{cards}</div>'
