"""
BSC vs Consensus Comparison Tab (Redesigned)
=============================================
Two sub-tabs:
1. Summary Table - NPATMI 2026F focus with clean comparison
2. Ticker Lookup - Search and view detailed comparison

Design: Midnight Financial Terminal
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

from WEBAPP.components.styles.comparison_styles import (
    get_comparison_styles,
    format_insight_badge,
    render_legend_bar,
    render_summary_cards,
    SOURCE_MARKERS,
    INSIGHT_CONFIG,
    COLORS,
)
from WEBAPP.components.filters.forecast_filter_bar import WATCHLIST_PRESETS

# Data paths
FORECAST_SOURCES_PATH = Path("DATA/processed/forecast/sources")
UNIFIED_PARQUET_PATH = Path("DATA/processed/forecast/unified.parquet")


@st.cache_data(ttl=300)  # Cache 5 minutes for fresh data
def load_comparison_data() -> pd.DataFrame:
    """Load comparison data from mixed sources.

    JSON sources (fresh): bsc.json, hcm.json, vci.json
    Parquet source (SSI): unified.parquet
    """
    import json
    from datetime import datetime

    # Load JSON sources (BSC, HCM, VCI)
    sources = {}
    for source in ['bsc', 'hcm', 'vci']:
        path = FORECAST_SOURCES_PATH / f"{source}.json"
        if path.exists():
            with open(path, encoding='utf-8') as f:
                data = json.load(f)
                sources[source] = {s['symbol']: s for s in data.get('stocks', [])}

    # Load SSI from unified.parquet
    ssi_data = {}
    if UNIFIED_PARQUET_PATH.exists():
        unified_df = pd.read_parquet(UNIFIED_PARQUET_PATH)
        for _, row in unified_df.iterrows():
            symbol = row['symbol']
            ssi_data[symbol] = {
                'symbol': symbol,
                'sector': row.get('sector', ''),  # Include sector for non-BSC stocks
                'target_price': row.get('ssi_tp'),
                'npatmi_2026f': row.get('ssi_npatmi_26'),
                'npatmi_2027f': row.get('ssi_npatmi_27'),
            }
    sources['ssi'] = ssi_data

    if not sources.get('bsc'):
        return pd.DataFrame()

    # Build unified dataframe from BSC as base
    rows = []
    all_symbols = set()
    for src_data in sources.values():
        all_symbols.update(src_data.keys())

    for symbol in all_symbols:
        bsc = sources.get('bsc', {}).get(symbol, {})
        hcm = sources.get('hcm', {}).get(symbol, {})
        vci = sources.get('vci', {}).get(symbol, {})
        ssi = sources.get('ssi', {}).get(symbol, {})

        # Get base info from any available source
        base = bsc or hcm or vci or ssi

        row = {
            'symbol': symbol,
            'sector': base.get('sector', ''),
            'entity_type': base.get('entity_type', 'COMPANY'),
            'current_price': bsc.get('current_price') or hcm.get('current_price') or vci.get('current_price') or ssi.get('current_price'),
            # BSC data
            'bsc_tp': bsc.get('target_price'),
            'bsc_npatmi_26': bsc.get('npatmi_2026f'),
            'bsc_npatmi_27': bsc.get('npatmi_2027f'),
            'rating': bsc.get('rating'),
            # HCM (HSC) data
            'hcm_tp': hcm.get('target_price'),
            'hcm_npatmi_26': hcm.get('npatmi_2026f'),
            'hcm_npatmi_27': hcm.get('npatmi_2027f'),
            # VCI data
            'vci_tp': vci.get('target_price'),
            'vci_npatmi_26': vci.get('npatmi_2026f'),
            'vci_npatmi_27': vci.get('npatmi_2027f'),
            # SSI data
            'ssi_tp': ssi.get('target_price'),
            'ssi_npatmi_26': ssi.get('npatmi_2026f'),
            'ssi_npatmi_27': ssi.get('npatmi_2027f'),
        }
        rows.append(row)

    df = pd.DataFrame(rows)

    # Calculate consensus metrics
    def calc_consensus(row, metric_prefix):
        vals = [row.get(f'{src}_{metric_prefix}') for src in ['bsc', 'vci', 'hcm', 'ssi']]
        vals = [v for v in vals if pd.notna(v) and v > 0]
        if not vals:
            return None, None, None
        mean_val = np.mean(vals)
        spread = (max(vals) - min(vals)) / mean_val * 100 if mean_val > 0 else 0
        bsc_val = row.get(f'bsc_{metric_prefix}')
        dev = ((mean_val - bsc_val) / bsc_val * 100) if pd.notna(bsc_val) and bsc_val > 0 else None
        return mean_val, dev, spread

    # Add consensus columns
    for _, row in df.iterrows():
        # NPATMI 2026
        mean_26, dev_26, spread_26 = calc_consensus(row, 'npatmi_26')
        df.loc[df['symbol'] == row['symbol'], 'npatmi_26_cons_mean'] = mean_26
        df.loc[df['symbol'] == row['symbol'], 'npatmi_26_dev_pct'] = dev_26
        df.loc[df['symbol'] == row['symbol'], 'npatmi_26_spread_pct'] = spread_26

        # TP consensus
        tp_mean, tp_dev, tp_spread = calc_consensus(row, 'tp')
        df.loc[df['symbol'] == row['symbol'], 'tp_cons_mean'] = tp_mean
        df.loc[df['symbol'] == row['symbol'], 'tp_dev_pct'] = tp_dev
        df.loc[df['symbol'] == row['symbol'], 'tp_spread_pct'] = tp_spread

    # Calculate insight
    def get_insight(row):
        dev = row.get('npatmi_26_dev_pct')
        if pd.isna(dev):
            return 'no_data'
        if dev <= -10:
            return 'bullish_gap'
        elif dev >= 10:
            return 'bearish_gap'
        elif -5 <= dev <= 5:
            return 'aligned'
        elif dev < 0:
            return 'slight_bull'
        else:
            return 'slight_bear'

    df['insight'] = df.apply(get_insight, axis=1)

    # Source count
    df['source_count'] = df.apply(
        lambda r: sum(1 for src in ['bsc', 'vci', 'hcm', 'ssi'] if pd.notna(r.get(f'{src}_npatmi_26'))),
        axis=1
    )

    df['build_timestamp'] = datetime.now().isoformat()

    return df


def format_npatmi_t(val) -> str:
    """Format NPATMI in nghìn tỷ (T)."""
    if pd.isna(val) or val == 0:
        return '—'
    # Convert to nghìn tỷ (trillion = 1000 billion)
    t_val = val / 1000
    if t_val >= 10:
        return f"{t_val:.1f}T"
    elif t_val >= 1:
        return f"{t_val:.2f}T"
    else:
        # Less than 1T, show in B
        return f"{val:.0f}B"


def format_price(val) -> str:
    """Format price value."""
    if pd.isna(val) or val == 0:
        return '—'
    return f"{val:,.0f}"


def format_deviation(val, show_bar: bool = False) -> str:
    """Format deviation percentage with soft neon bull/bear colors.

    Note: Uses Teal (#5EEAD4) for bullish and Rose (#FB7185) for bearish.
    Softer neon colors that are easier on the eyes in dark mode.
    """
    if pd.isna(val):
        return '<span style="color:#64748B;font-family:JetBrains Mono,monospace;">—</span>'

    sign = '+' if val >= 0 else ''

    # Soft neon semantic colors: Bullish = Teal, Bearish = Rose
    # Note: Positive deviation = BSC < Cons = Bearish for BSC
    #       Negative deviation = BSC > Cons = Bullish for BSC
    if val <= -5:
        color = '#5EEAD4'  # Teal 300 - BSC bullish (higher than consensus)
        bar_color = '#5EEAD4'
        glow = 'rgba(94, 234, 212, 0.25)'
    elif val >= 5:
        color = '#FB7185'  # Rose 400 - BSC bearish (lower than consensus)
        bar_color = '#FB7185'
        glow = 'rgba(251, 113, 133, 0.25)'
    else:
        color = '#A1A1AA'  # Zinc 400 - Aligned
        bar_color = '#71717A'
        glow = 'none'

    text = f'<span style="color:{color};font-weight:600;font-family:JetBrains Mono,monospace;text-shadow:0 0 8px {glow};">{sign}{val:.1f}%</span>'

    if show_bar:
        # Add visual bar with glow
        bar_width = min(abs(val), 30) * 2  # Max 60px
        bar_dir = 'right' if val >= 0 else 'left'
        text += f'''
        <div style="height:4px;width:{bar_width}px;background:{bar_color};border-radius:2px;margin-top:3px;margin-{bar_dir}:auto;box-shadow:0 0 6px {glow};"></div>
        '''

    return text


def get_insight_simple(val) -> str:
    """Get simple insight label."""
    config = INSIGHT_CONFIG.get(val, INSIGHT_CONFIG['no_data'])
    return f'<span style="color:{config["color"]};font-weight:500;">{config["icon"]} {config["label"]}</span>'


def calculate_summary_stats(df: pd.DataFrame) -> dict:
    """Calculate summary statistics."""
    return {
        'total': len(df),
        'overlap': ((df['bsc_npatmi_26'].notna()) & (df['source_count'] > 0)).sum(),
        'strong_bullish': (df['insight'] == 'strong_bullish').sum(),
        'bullish_gap': (df['insight'] == 'bullish_gap').sum(),
        'aligned': (df['insight'] == 'aligned').sum(),
        'high_variance': (df['insight'] == 'high_variance').sum(),
        'bearish_gap': (df['insight'] == 'bearish_gap').sum(),
        'strong_bearish': (df['insight'] == 'strong_bearish').sum(),
    }


# =============================================================================
# SUB-TAB 1: SUMMARY TABLE
# =============================================================================
def render_summary_table(df: pd.DataFrame, full_df: pd.DataFrame = None):
    """Render clean summary table focused on NPATMI 2026F.

    Args:
        df: Filtered DataFrame based on toggle
        full_df: Full DataFrame with all stocks (for sector filter)
    """
    if full_df is None:
        full_df = df

    st.markdown("#### NPATMI 2026F Consensus Comparison")
    st.caption("Compare BSC forecasts with market consensus (VCI, HCM, SSI)")

    # Filters row - 5 columns with ticker search and watchlist
    col1, col2, col3, col4, col5 = st.columns([2, 2, 1.5, 1.5, 1.5])

    with col1:
        ticker_search = st.text_input("Search Ticker", placeholder="VCB, ACB...", key="cons_ticker")

    with col2:
        # Use full_df for sector list to show all available sectors
        # Filter out empty strings and NaN values
        sectors = ['All'] + sorted([s for s in full_df['sector'].dropna().unique() if s and s.strip()])
        sector_filter = st.selectbox("Sector", sectors, key="cons_sector")

    with col3:
        # Watchlist preset filter
        watchlist_options = list(WATCHLIST_PRESETS.keys())
        watchlist_filter = st.selectbox("Watchlist", watchlist_options, key="cons_watchlist")

    with col4:
        min_sources = st.selectbox("Min Sources", [1, 2, 3], index=0, key="cons_min_src")

    with col5:
        insight_options = ['All'] + list(INSIGHT_CONFIG.keys())
        insight_filter = st.selectbox(
            "Insight",
            insight_options,
            format_func=lambda x: INSIGHT_CONFIG.get(x, {}).get('label', x) if x != 'All' else 'All',
            key="cons_insight"
        )

    # Apply filters
    # When sector is selected, show ALL stocks in that sector (use full_df)
    if sector_filter != 'All':
        filtered_df = full_df[full_df['sector'] == sector_filter].copy()
    else:
        filtered_df = df.copy()

    # Watchlist filter - apply before other filters
    if watchlist_filter != 'All':
        watchlist_tickers = WATCHLIST_PRESETS.get(watchlist_filter, [])
        if watchlist_tickers:
            filtered_df = filtered_df[filtered_df['symbol'].isin(watchlist_tickers)].copy()

    # Ticker search filter
    if ticker_search:
        ticker_search = ticker_search.upper().strip()
        filtered_df = filtered_df[filtered_df['symbol'].str.contains(ticker_search, case=False, na=False)]

    filtered_df = filtered_df[filtered_df['source_count'] >= min_sources]

    if insight_filter != 'All':
        filtered_df = filtered_df[filtered_df['insight'] == insight_filter]

    # Sort by sector first, then by deviation within each sector
    # Handle None/NaN values in abs calculation
    filtered_df['abs_dev'] = filtered_df['npatmi_26_dev_pct'].fillna(0).abs()
    filtered_df = filtered_df.sort_values(['sector', 'abs_dev'], ascending=[True, False], na_position='last')

    st.markdown(f"**{len(filtered_df)} stocks** with ≥{min_sources} consensus sources")

    if filtered_df.empty:
        st.info("No stocks match the selected filters.")
        return

    # Note about columns
    # Compact legend - no separate cards
    st.html('''
    <div style="background:rgba(26,22,37,0.8);border-radius:8px;padding:10px 14px;margin-bottom:12px;font-size:11px;color:#94A3B8;border:1px solid rgba(255,255,255,0.05);font-family:DM Sans,sans-serif;">
        <span style="font-weight:600;color:#00C9AD;">NPATMI 2026F</span> (nghìn tỷ) |
        <span style="color:#8B5CF6;">B</span><span style="color:#EC4899;">V</span><span style="color:#06B6D4;">H</span><span style="color:#F59E0B;">S</span> markers on spread |
        <span style="color:#5EEAD4;">▲ Bullish</span> (BSC &gt; Cons) •
        <span style="color:#FB7185;">▼ Bearish</span> (BSC &lt; Cons)
    </div>
    ''')

    # Build HTML table
    table_html = build_summary_table_html(filtered_df)
    st.html(table_html)

    # Legend
    st.html(render_legend_bar())


def build_range_chart_inline(bsc_val, vci_val, hcm_val, ssi_val) -> str:
    """Build range chart with min/max labels and glowing markers.

    Column order: BSC, VCI, HCM, SSI
    Uses non-semantic source colors:
    - BSC: Purple #8B5CF6
    - VCI: Pink #EC4899
    - HCM: Cyan #06B6D4
    - SSI: Amber #F59E0B
    """
    values = {
        'BSC': bsc_val,
        'HCM': hcm_val,
        'SSI': ssi_val,
        'VCI': vci_val,
    }

    # Filter valid values
    valid = {k: v for k, v in values.items() if pd.notna(v) and v > 0}

    if len(valid) < 2:
        return '<span style="color:#64748B;font-family:JetBrains Mono,monospace;">—</span>'

    min_val = min(valid.values())
    max_val = max(valid.values())
    range_val = max_val - min_val

    if range_val == 0:
        # All same value - show clustered markers with glow
        val_label = format_npatmi_t(min_val)
        markers = ''.join(
            f'''<span style="display:inline-flex;align-items:center;justify-content:center;
                width:14px;height:14px;border-radius:50%;background:{SOURCE_MARKERS[k]["color"]};
                margin:0 2px;font-size:8px;font-weight:700;color:#fff;
                box-shadow:0 0 6px {SOURCE_MARKERS[k].get("glow", "rgba(0,0,0,0.3)")};">
                {SOURCE_MARKERS[k]["short"]}</span>'''
            for k in valid.keys()
        )
        return f'<div style="display:flex;align-items:center;gap:4px;"><span style="font-size:9px;color:#64748B;font-family:JetBrains Mono,monospace;">{val_label}</span>{markers}</div>'

    # Calculate positions (8-92% to leave padding for markers)
    def pos(v):
        return int(8 + (v - min_val) / range_val * 84)

    # Build markers HTML with glow effects
    markers_html = ""
    for source, val in valid.items():
        p = pos(val)
        color = SOURCE_MARKERS[source]['color']
        short = SOURCE_MARKERS[source]['short']
        glow = SOURCE_MARKERS[source].get('glow', 'rgba(0,0,0,0.3)')
        val_t = format_npatmi_t(val)
        markers_html += f'''
        <span style="position:absolute;left:{p}%;top:50%;transform:translate(-50%,-50%);
                     width:20px;height:20px;border-radius:50%;background:{color};
                     display:flex;align-items:center;justify-content:center;
                     font-size:10px;font-weight:700;color:#fff;z-index:2;
                     box-shadow:0 2px 6px {glow};cursor:help;
                     transition:all 0.2s ease;font-family:JetBrains Mono,monospace;"
             title="{source}: {val_t}">{short}</span>
        '''

    min_label = format_npatmi_t(min_val)
    max_label = format_npatmi_t(max_val)

    return f'''
    <div style="display:flex;align-items:center;gap:4px;">
        <span style="font-size:10px;color:#64748B;min-width:30px;text-align:right;font-family:JetBrains Mono,monospace;">{min_label}</span>
        <div style="flex:1;height:10px;background:linear-gradient(180deg,rgba(15,11,30,0.8) 0%,rgba(26,22,37,0.6) 100%);border-radius:5px;position:relative;min-width:70px;border:1px solid rgba(255,255,255,0.05);">
            <div style="position:absolute;left:8%;right:8%;top:50%;height:2px;background:linear-gradient(90deg,rgba(6,182,212,0.3) 0%,rgba(139,92,246,0.3) 100%);transform:translateY(-50%);border-radius:1px;"></div>
            {markers_html}
        </div>
        <span style="font-size:10px;color:#64748B;min-width:30px;font-family:JetBrains Mono,monospace;">{max_label}</span>
    </div>
    '''


def build_summary_table_html(df: pd.DataFrame) -> str:
    """Build HTML for summary table with NPATMI 2026F columns and range chart.

    Uses new non-semantic source colors:
    - BSC: Purple #8B5CF6
    - HCM: Cyan #06B6D4
    - SSI: Amber #F59E0B
    - VCI: Pink #EC4899

    Note: Schema updated to use 2026F (current year forecast) as primary.
    """

    # Header - 14px data fonts, 12px headers
    header = '''
    <table style="width:100%;border-collapse:collapse;font-size:14px;background:linear-gradient(180deg, #0F0B1E 0%, #1A1625 100%);border-radius:12px;overflow:hidden;border:1px solid rgba(255,255,255,0.08);">
    <thead>
        <tr style="background:linear-gradient(180deg, #1A1625 0%, #0F0B1E 100%);border-bottom:2px solid rgba(139,92,246,0.3);">
            <th style="text-align:left;padding:12px 10px;color:#C4B5FD;font-size:12px;font-weight:600;width:60px;font-family:Space Grotesk,sans-serif;letter-spacing:0.08em;">SYMBOL</th>
            <th style="text-align:right;padding:12px 8px;color:#94A3B8;font-size:12px;font-weight:600;width:60px;font-family:Space Grotesk,sans-serif;">PRICE</th>
            <th style="text-align:right;padding:12px 8px;color:#8B5CF6;font-size:12px;font-weight:600;width:60px;font-family:Space Grotesk,sans-serif;">BSC TP</th>
            <th style="text-align:right;padding:12px 8px;color:#8B5CF6;font-size:12px;font-weight:600;width:55px;font-family:Space Grotesk,sans-serif;">BSC</th>
            <th style="text-align:right;padding:12px 8px;color:#EC4899;font-size:12px;font-weight:600;width:55px;font-family:Space Grotesk,sans-serif;">VCI</th>
            <th style="text-align:right;padding:12px 8px;color:#06B6D4;font-size:12px;font-weight:600;width:55px;font-family:Space Grotesk,sans-serif;">HCM</th>
            <th style="text-align:right;padding:12px 8px;color:#F59E0B;font-size:12px;font-weight:600;width:55px;font-family:Space Grotesk,sans-serif;">SSI</th>
            <th style="text-align:right;padding:12px 8px;color:#00C9AD;font-size:12px;font-weight:600;width:55px;font-family:Space Grotesk,sans-serif;">CONS</th>
            <th style="text-align:center;padding:12px 8px;color:#C4B5FD;font-size:12px;font-weight:600;width:150px;font-family:Space Grotesk,sans-serif;">SPREAD</th>
            <th style="text-align:center;padding:12px 8px;color:#C4B5FD;font-size:12px;font-weight:600;width:90px;font-family:Space Grotesk,sans-serif;">BSC vs CONS</th>
        </tr>
    </thead>
    <tbody>
    '''

    rows = ""
    for idx, row in df.iterrows():
        symbol = row.get('symbol', '')
        sector = row.get('sector', '')

        # Values - using 2026F (current year forecast) as primary
        current_price = row.get('current_price')
        bsc_tp = row.get('bsc_tp')
        bsc_npatmi = row.get('bsc_npatmi_26')
        vci_npatmi = row.get('vci_npatmi_26')
        hcm_npatmi = row.get('hcm_npatmi_26')
        ssi_npatmi = row.get('ssi_npatmi_26')
        cons_mean = row.get('npatmi_26_cons_mean')
        dev_pct = row.get('npatmi_26_dev_pct')
        insight = row.get('insight', 'no_data')

        # Row background based on deviation (BSC vs Cons)
        # Soft neon colors: Teal for bullish, Rose for bearish
        if pd.notna(dev_pct):
            if dev_pct <= -5:
                row_bg = 'rgba(94, 234, 212, 0.05)'  # Teal tint - BSC bullish
            elif dev_pct >= 5:
                row_bg = 'rgba(251, 113, 133, 0.05)'  # Rose tint - BSC bearish
            else:
                row_bg = 'transparent'
        else:
            row_bg = 'transparent'

        # Build range chart with labels
        range_chart = build_range_chart_inline(bsc_npatmi, vci_npatmi, hcm_npatmi, ssi_npatmi)

        # Combined DEV + INSIGHT cell
        insight_config = INSIGHT_CONFIG.get(insight, INSIGHT_CONFIG['no_data'])
        dev_insight_html = build_dev_insight_cell(dev_pct, insight_config)

        # Row with 14px data fonts
        rows += f'''
        <tr style="background:{row_bg};border-bottom:1px solid rgba(255,255,255,0.05);transition:all 0.2s ease;">
            <td style="padding:10px;" title="{sector or 'N/A'}">
                <span style="font-weight:700;color:#00C9AD;font-family:'JetBrains Mono',monospace;font-size:14px;cursor:help;">{symbol}</span>
            </td>
            <td style="text-align:right;padding:10px 8px;font-family:'JetBrains Mono',monospace;color:#94A3B8;font-size:14px;">{format_price(current_price)}</td>
            <td style="text-align:right;padding:10px 8px;font-family:'JetBrains Mono',monospace;color:#C4B5FD;font-size:14px;">{format_price(bsc_tp)}</td>
            <td style="text-align:right;padding:10px 8px;font-family:'JetBrains Mono',monospace;color:#8B5CF6;font-size:14px;">{format_npatmi_t(bsc_npatmi)}</td>
            <td style="text-align:right;padding:10px 8px;font-family:'JetBrains Mono',monospace;color:#EC4899;font-size:14px;">{format_npatmi_t(vci_npatmi)}</td>
            <td style="text-align:right;padding:10px 8px;font-family:'JetBrains Mono',monospace;color:#06B6D4;font-size:14px;">{format_npatmi_t(hcm_npatmi)}</td>
            <td style="text-align:right;padding:10px 8px;font-family:'JetBrains Mono',monospace;color:#F59E0B;font-size:14px;">{format_npatmi_t(ssi_npatmi)}</td>
            <td style="text-align:right;padding:10px 8px;font-family:'JetBrains Mono',monospace;color:#00C9AD;font-size:14px;font-weight:600;">{format_npatmi_t(cons_mean)}</td>
            <td style="padding:10px;">{range_chart}</td>
            <td style="text-align:center;padding:10px;">{dev_insight_html}</td>
        </tr>
        '''

    return header + rows + '</tbody></table>'


def build_dev_insight_cell(dev_pct, insight_config) -> str:
    """Build combined DEV + INSIGHT cell with semantic colors."""
    if pd.isna(dev_pct):
        return '<span style="color:#64748B;font-family:JetBrains Mono,monospace;">—</span>'

    # Semantic colors for deviation (distinct from source markers)
    if dev_pct <= -5:
        dev_color = '#10B981'  # Emerald - BSC bullish
        glow = 'rgba(16, 185, 129, 0.3)'
    elif dev_pct >= 5:
        dev_color = '#EF4444'  # Red - BSC bearish
        glow = 'rgba(239, 68, 68, 0.3)'
    else:
        dev_color = '#94A3B8'  # Slate - Neutral
        glow = 'none'

    sign = '+' if dev_pct >= 0 else ''

    return f'''
    <div style="display:flex;flex-direction:column;align-items:center;gap:4px;">
        <span style="font-family:'JetBrains Mono',monospace;font-size:14px;font-weight:600;color:{dev_color};text-shadow:0 0 8px {glow};">{sign}{dev_pct:.1f}%</span>
        <span style="font-size:11px;color:{insight_config['color']};font-family:'DM Sans',sans-serif;">{insight_config['icon']} {insight_config['label']}</span>
    </div>
    '''


# =============================================================================
# SUB-TAB 2: TICKER LOOKUP
# =============================================================================
def render_ticker_lookup(df: pd.DataFrame):
    """Render ticker lookup with detailed comparison."""

    # Compact header with inline search
    st.markdown(
        '<p style="font-size:14px;font-weight:600;color:#C4B5FD;margin-bottom:8px;font-family:Space Grotesk,sans-serif;">Ticker Lookup</p>',
        unsafe_allow_html=True
    )

    # Compact search input - wider input, smaller button
    col1, col2 = st.columns([5, 1])

    with col1:
        ticker_input = st.text_input(
            "Enter Ticker",
            placeholder="ACB, VCB, FPT...",
            key="ticker_lookup_input",
            label_visibility="collapsed"
        ).strip().upper()

    with col2:
        search_clicked = st.button("Search", use_container_width=True, type="secondary")

    if not ticker_input:
        st.info("Enter a ticker symbol above to view detailed comparison.")
        # Show available tickers
        st.markdown("**Available tickers with consensus data:**")
        available = df[df['source_count'] > 0]['symbol'].sort_values().tolist()
        st.caption(", ".join(available[:50]) + ("..." if len(available) > 50 else ""))
        return

    # Find ticker
    ticker_row = df[df['symbol'] == ticker_input]

    if ticker_row.empty:
        st.error(f"Ticker '{ticker_input}' not found in comparison data.")
        # Suggest similar
        similar = df[df['symbol'].str.contains(ticker_input[:2], case=False, na=False)]['symbol'].head(5).tolist()
        if similar:
            st.caption(f"Did you mean: {', '.join(similar)}")
        return

    row = ticker_row.iloc[0]

    # Stock header
    symbol = row.get('symbol', '')
    sector = row.get('sector', '')
    current_price = row.get('current_price')

    st.html(f'''
    <div style="background:#1E293B;border-radius:8px;padding:16px;margin:16px 0;border:1px solid #334155;">
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <div>
                <div style="font-size:24px;font-weight:700;color:#F8FAFC;font-family:'Space Mono',monospace;">{symbol}</div>
                <div style="font-size:13px;color:#64748B;">{sector or 'N/A'}</div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:11px;color:#64748B;">Current Price</div>
                <div style="font-size:20px;font-weight:700;font-family:'Space Mono',monospace;color:#00C9AD;">{format_price(current_price)} VND</div>
            </div>
        </div>
    </div>
    ''')

    # Comparison table
    st.html(build_detail_table_html(row))

    # Range visualization
    st.html(build_range_visual_html(row))

    # Insight summary (using NPATMI 2026F as primary - current year forecast)
    insight = row.get('insight', 'no_data')
    config = INSIGHT_CONFIG.get(insight, INSIGHT_CONFIG['no_data'])
    dev_26 = row.get('npatmi_26_dev_pct')

    # dev_26 = (Consensus - BSC) / BSC
    # Positive = Consensus > BSC = BSC conservative (bearish)
    # Negative = Consensus < BSC = BSC optimistic (bullish)
    insight_text = ""
    if pd.notna(dev_26):
        if dev_26 <= -5:
            # BSC higher than consensus = BSC optimistic
            insight_text = f"BSC lạc quan hơn consensus {abs(dev_26):.1f}% cho NPATMI 2026F"
        elif dev_26 >= 5:
            # BSC lower than consensus = BSC conservative
            insight_text = f"BSC bảo thủ hơn consensus {dev_26:.1f}% cho NPATMI 2026F"
        else:
            insight_text = f"BSC và consensus gần nhau ({dev_26:+.1f}%) cho NPATMI 2026F"

    st.html(f'''
    <div style="background:{config['color']}15;border:1px solid {config['color']}40;border-radius:8px;padding:16px;margin-top:16px;">
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
            <span style="font-size:18px;">{config['icon']}</span>
            <span style="font-weight:700;color:{config['color']};">{config['label']}</span>
        </div>
        <div style="color:#94A3B8;font-size:13px;">{insight_text}</div>
    </div>
    ''')


def build_detail_table_html(row: pd.Series) -> str:
    """Build detailed comparison table HTML.

    Note: Schema updated to 2026F/2027F as of Jan 2026.
    """

    metrics = [
        ('Target Price', 'tp', format_price),
        ('NPATMI 2026F', 'npatmi_26', format_npatmi_t),
        ('NPATMI 2027F', 'npatmi_27', format_npatmi_t),
    ]

    rows_html = ""
    for label, key, formatter in metrics:
        bsc_val = row.get(f'bsc_{key}')
        hcm_val = row.get(f'hcm_{key}')
        ssi_val = row.get(f'ssi_{key}')
        vci_val = row.get(f'vci_{key}')
        cons_mean = row.get(f'{key}_cons_mean')

        # Calculate deviations from BSC
        def calc_dev(val):
            if pd.isna(bsc_val) or bsc_val == 0 or pd.isna(val):
                return None
            return (val - bsc_val) / bsc_val * 100

        hcm_dev = calc_dev(hcm_val)
        ssi_dev = calc_dev(ssi_val)
        vci_dev = calc_dev(vci_val)
        cons_dev = calc_dev(cons_mean)

        rows_html += f'''
        <tr style="border-bottom:1px solid #334155;">
            <td style="padding:12px;font-weight:500;color:#94A3B8;">{label}</td>
            <td style="padding:12px;text-align:center;">
                <div style="font-family:'Space Mono',monospace;color:#F8FAFC;font-weight:600;">{formatter(bsc_val)}</div>
            </td>
            <td style="padding:12px;text-align:center;">
                <div style="font-family:'Space Mono',monospace;color:#F8FAFC;">{formatter(hcm_val)}</div>
                <div style="font-size:11px;">{format_deviation(hcm_dev)}</div>
            </td>
            <td style="padding:12px;text-align:center;">
                <div style="font-family:'Space Mono',monospace;color:#F8FAFC;">{formatter(ssi_val)}</div>
                <div style="font-size:11px;">{format_deviation(ssi_dev)}</div>
            </td>
            <td style="padding:12px;text-align:center;">
                <div style="font-family:'Space Mono',monospace;color:#F8FAFC;">{formatter(vci_val)}</div>
                <div style="font-size:11px;">{format_deviation(vci_dev)}</div>
            </td>
            <td style="padding:12px;text-align:center;background:rgba(0,201,173,0.05);">
                <div style="font-family:'Space Mono',monospace;color:#00C9AD;font-weight:600;">{formatter(cons_mean)}</div>
                <div style="font-size:11px;">{format_deviation(cons_dev)}</div>
            </td>
        </tr>
        '''

    # Non-semantic source colors: Purple, Cyan, Amber, Pink
    return f'''
    <table style="width:100%;border-collapse:collapse;font-size:13px;background:linear-gradient(180deg, #0F0B1E 0%, #1A1625 100%);border-radius:12px;overflow:hidden;margin-top:16px;border:1px solid rgba(255,255,255,0.08);">
    <thead>
        <tr style="background:linear-gradient(180deg, #1A1625 0%, #0F0B1E 100%);border-bottom:2px solid rgba(139,92,246,0.3);">
            <th style="text-align:left;padding:12px;color:#C4B5FD;font-size:10px;font-weight:600;font-family:Space Grotesk,sans-serif;letter-spacing:0.08em;">METRIC</th>
            <th style="text-align:center;padding:12px;color:#8B5CF6;font-size:10px;font-weight:600;font-family:Space Grotesk,sans-serif;">
                <span style="display:inline-flex;align-items:center;justify-content:center;width:14px;height:14px;border-radius:50%;background:#8B5CF6;margin-right:5px;font-size:8px;color:#fff;font-family:JetBrains Mono,monospace;">B</span>BSC
            </th>
            <th style="text-align:center;padding:12px;color:#06B6D4;font-size:10px;font-weight:600;font-family:Space Grotesk,sans-serif;">
                <span style="display:inline-flex;align-items:center;justify-content:center;width:14px;height:14px;border-radius:50%;background:#06B6D4;margin-right:5px;font-size:8px;color:#fff;font-family:JetBrains Mono,monospace;">H</span>HCM
            </th>
            <th style="text-align:center;padding:12px;color:#F59E0B;font-size:10px;font-weight:600;font-family:Space Grotesk,sans-serif;">
                <span style="display:inline-flex;align-items:center;justify-content:center;width:14px;height:14px;border-radius:50%;background:#F59E0B;margin-right:5px;font-size:8px;color:#fff;font-family:JetBrains Mono,monospace;">S</span>SSI
            </th>
            <th style="text-align:center;padding:12px;color:#EC4899;font-size:10px;font-weight:600;font-family:Space Grotesk,sans-serif;">
                <span style="display:inline-flex;align-items:center;justify-content:center;width:14px;height:14px;border-radius:50%;background:#EC4899;margin-right:5px;font-size:8px;color:#fff;font-family:JetBrains Mono,monospace;">V</span>VCI
            </th>
            <th style="text-align:center;padding:12px;color:#00C9AD;font-size:10px;font-weight:600;background:rgba(0,201,173,0.08);font-family:Space Grotesk,sans-serif;">CONSENSUS</th>
        </tr>
    </thead>
    <tbody>{rows_html}</tbody>
    </table>
    '''


def build_range_visual_html(row: pd.Series) -> str:
    """Build visual range comparison HTML."""

    def build_range_bar(label: str, bsc_val, vci_val, hcm_val, ssi_val, formatter) -> str:
        """Build single range bar. Column order: BSC, VCI, HCM, SSI"""
        values = {
            'BSC': bsc_val,
            'VCI': vci_val,
            'HCM': hcm_val,
            'SSI': ssi_val,
        }
        valid = {k: v for k, v in values.items() if pd.notna(v) and v > 0}

        if len(valid) < 2:
            return ""

        min_val = min(valid.values())
        max_val = max(valid.values())
        range_val = max_val - min_val

        if range_val == 0:
            return ""

        def pos(v):
            return int((v - min_val) / range_val * 100)

        markers_html = ""
        for source, val in valid.items():
            p = pos(val)
            color = SOURCE_MARKERS[source]['color']
            short = SOURCE_MARKERS[source]['short']
            markers_html += f'''
            <span style="position:absolute;left:{p}%;top:50%;transform:translate(-50%,-50%);
                         width:20px;height:20px;border-radius:50%;background:{color};
                         display:flex;align-items:center;justify-content:center;
                         font-size:9px;font-weight:700;color:#fff;z-index:2;">{short}</span>
            '''

        min_label = formatter(min_val)
        max_label = formatter(max_val)

        return f'''
        <div style="margin:8px 0;">
            <div style="font-size:11px;color:#64748B;margin-bottom:4px;">{label}</div>
            <div style="display:flex;align-items:center;gap:8px;">
                <span style="font-size:10px;color:#64748B;width:50px;text-align:right;">{min_label}</span>
                <div style="flex:1;height:8px;background:#1E293B;border-radius:4px;position:relative;">
                    {markers_html}
                </div>
                <span style="font-size:10px;color:#64748B;width:50px;">{max_label}</span>
            </div>
        </div>
        '''

    # Build range bars
    tp_range = build_range_bar(
        "Target Price",
        row.get('bsc_tp'), row.get('vci_tp'), row.get('hcm_tp'), row.get('ssi_tp'),
        format_price
    )

    npatmi_26_range = build_range_bar(
        "NPATMI 2026F",
        row.get('bsc_npatmi_26'), row.get('vci_npatmi_26'), row.get('hcm_npatmi_26'), row.get('ssi_npatmi_26'),
        format_npatmi_t
    )

    if not tp_range and not npatmi_26_range:
        return ""

    return f'''
    <div style="background:#0F172A;border-radius:8px;padding:16px;margin-top:16px;border:1px solid #334155;">
        <div style="font-size:12px;font-weight:600;color:#94A3B8;margin-bottom:12px;">VISUAL RANGE</div>
        {tp_range}
        {npatmi_26_range}
    </div>
    '''


# =============================================================================
# MAIN RENDER FUNCTION
# =============================================================================
def render_bsc_vs_consensus_tab():
    """Main render function for BSC vs Consensus tab."""
    # Inject styles
    st.html(get_comparison_styles())

    # Load data
    df = load_comparison_data()

    if df.empty:
        st.warning("No comparison data available. Please run the comparison pipeline first.")
        st.code("python3 PROCESSORS/forecast/create_comparison_table.py", language="bash")
        return

    # Data view toggle - BSC only or All stocks with consensus
    col_title, col_toggle = st.columns([4, 2])

    with col_toggle:
        show_all = st.checkbox("Include non-BSC stocks", value=False, key="show_all_consensus")

    # Filter: show all stocks with ANY NPATMI data from any source
    # (stocks without NPATMI from all 4 sources are excluded)
    has_any_npatmi = (
        df['bsc_npatmi_26'].notna() |
        df['vci_npatmi_26'].notna() |
        df['hcm_npatmi_26'].notna() |
        df['ssi_npatmi_26'].notna()
    )
    df = df[has_any_npatmi].copy()

    # Filter based on toggle
    if show_all:
        # All stocks with at least 1 source (including non-BSC)
        overlap_df = df[df['source_count'] > 0].copy()
    else:
        # Only BSC covered stocks with consensus
        overlap_df = df[(df['bsc_npatmi_26'].notna()) & (df['source_count'] > 0)].copy()

    # Count non-BSC stocks
    non_bsc_count = len(df[(df['bsc_npatmi_26'].isna()) & (df['source_count'] > 0)])

    # Summary stats
    stats = calculate_summary_stats(overlap_df)

    # Compact header with stats inline
    bullish_count = stats['strong_bullish'] + stats['bullish_gap']
    bearish_count = stats['bearish_gap'] + stats['strong_bearish']

    with col_title:
        title_suffix = " (All Sources)" if show_all else ""
        st.html(f'''
        <div style="display:flex;align-items:center;gap:20px;padding:8px 0;">
            <h3 style="margin:0;font-size:18px;font-weight:700;color:#F8FAFC;font-family:Space Grotesk,sans-serif;">
                BSC vs Consensus{title_suffix}
            </h3>
            <div style="display:flex;gap:16px;font-family:JetBrains Mono,monospace;font-size:12px;">
                <span style="color:#00C9AD;"><strong>{stats['overlap']}</strong> overlap</span>
                <span style="color:#10B981;"><strong>{bullish_count}</strong> bullish</span>
                <span style="color:#94A3B8;"><strong>{stats['aligned']}</strong> aligned</span>
                <span style="color:#EF4444;"><strong>{bearish_count}</strong> bearish</span>
                {f'<span style="color:#F59E0B;"><strong>{non_bsc_count}</strong> non-BSC</span>' if not show_all else ''}
            </div>
        </div>
        ''')

    # Compact sub-tabs
    sub_tab = st.radio(
        "View",
        ["Summary Table", "Ticker Lookup"],
        horizontal=True,
        label_visibility="collapsed",
        key="consensus_subtab"
    )

    if sub_tab == "Summary Table":
        render_summary_table(overlap_df, full_df=df)
    else:
        render_ticker_lookup(df)


# Alias for backward compatibility
def render_consensus_comparison_tab():
    """Alias for render_bsc_vs_consensus_tab."""
    render_bsc_vs_consensus_tab()
