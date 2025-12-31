"""
Achievement Tab
===============
Tab 2: 9M Achievement tracking with clickable action cards.

Features:
- 3 achievement cards: BEAT, MEET, MISS
- Clickable cards filter the table
- Achievement stats (avg upside, avg ach%)
"""

import streamlit as st
import pandas as pd

from WEBAPP.components.cards.achievement_cards import (
    render_achievement_cards_interactive,
    calculate_achievement_stats,
    classify_achievement,
    BEAT_THRESHOLD,
    MEET_THRESHOLD
)
from WEBAPP.core.styles import render_styled_table


def format_achievement(val) -> str:
    """Format achievement percentage with color coding."""
    if pd.isna(val):
        return '-'
    pct = val * 100 if abs(val) < 10 else val
    if pct >= 85:
        color = '#00C9AD'  # Green - BEAT
    elif pct >= 65:
        color = '#FFC132'  # Yellow - MEET
    else:
        color = '#EF4444'  # Red - MISS
    return f'<span style="color: {color}; font-weight: 600;">{pct:.1f}%</span>'


def format_billions(val) -> str:
    """Format value in billions VND."""
    if pd.isna(val) or val == 0:
        return '-'
    if val >= 1000:
        return f"{val/1000:,.1f}T"
    return f"{val:,.0f}B"


def format_rating_badge(rating: str) -> str:
    """Format rating as colored badge HTML."""
    rating_class = {
        'STRONG BUY': 'rating-strong-buy',
        'BUY': 'rating-buy',
        'HOLD': 'rating-hold',
        'SELL': 'rating-sell',
        'STRONG SELL': 'rating-strong-sell',
        'N/A': 'rating-na',
    }.get(rating, 'rating-na')
    return f'<span class="rating-badge {rating_class}">{rating}</span>'


def render_achievement_tab(df: pd.DataFrame, service):
    """
    Render Achievement tab with cards and filtered table.

    Args:
        df: Individual stocks DataFrame with achievement data
        service: ForecastService instance
    """
    st.markdown("### 9M 2025 Achievement Tracker")
    st.markdown("*Track forecast achievement with dynamic thresholds (Expected: 75%)*")

    # Filter stocks with achievement data
    ach_col = 'npatmi_achievement_pct'
    if ach_col not in df.columns:
        # Try alternative column name
        ach_col = 'achievement_pct'

    if ach_col not in df.columns:
        st.warning("Achievement data not available. Please ensure 9M actual data is loaded.")
        return

    achievement_df = df[df[ach_col].notna()].copy()

    if achievement_df.empty:
        st.info("No stocks with achievement data available.")
        return

    # Rename column for component compatibility
    if ach_col != 'achievement_pct':
        achievement_df['achievement_pct'] = achievement_df[ach_col]

    # Render achievement cards with interactive filtering
    current_filter, filtered_df = render_achievement_cards_interactive(
        achievement_df,
        key_prefix='forecast'
    )

    st.markdown("---")

    # Show current filter status
    if current_filter != 'all':
        filter_labels = {'beat': 'BEAT (>85%)', 'meet': 'MEET (65-85%)', 'miss': 'MISS (<65%)'}
        st.markdown(f"**Filtered by:** {filter_labels.get(current_filter, current_filter)}")

    st.markdown(f"**Showing {len(filtered_df)} stocks**")

    # Sort options
    sort_col = st.radio(
        "Sort by",
        ["Achievement % (High to Low)", "Achievement % (Low to High)", "Sector"],
        horizontal=True,
        key="ach_sort"
    )

    if sort_col == "Achievement % (High to Low)":
        filtered_df = filtered_df.sort_values('achievement_pct', ascending=False)
    elif sort_col == "Achievement % (Low to High)":
        filtered_df = filtered_df.sort_values('achievement_pct', ascending=True)
    else:
        filtered_df = filtered_df.sort_values(['sector', 'achievement_pct'], ascending=[True, False])

    # Create achievement display table
    ach_display = pd.DataFrame()
    ach_display['Symbol'] = filtered_df['symbol']
    ach_display['Sector'] = filtered_df['sector']

    # Revenue columns
    if 'rev_2025f' in filtered_df.columns:
        ach_display['Rev 25F'] = filtered_df['rev_2025f'].apply(format_billions)
    if 'rev_ytd_2025' in filtered_df.columns:
        ach_display['Rev 9M'] = filtered_df['rev_ytd_2025'].apply(format_billions)
    if 'rev_achievement_pct' in filtered_df.columns:
        ach_display['Rev %'] = filtered_df['rev_achievement_pct'].apply(format_achievement)

    # Profit columns
    if 'npatmi_2025f' in filtered_df.columns:
        ach_display['NPATMI 25F'] = filtered_df['npatmi_2025f'].apply(format_billions)
    if 'npatmi_ytd_2025' in filtered_df.columns:
        ach_display['NPATMI 9M'] = filtered_df['npatmi_ytd_2025'].apply(format_billions)

    ach_display['Profit %'] = filtered_df['achievement_pct'].apply(format_achievement)

    if 'rating' in filtered_df.columns:
        ach_display['Rating'] = filtered_df['rating'].apply(format_rating_badge)

    st.markdown(render_styled_table(ach_display, highlight_first_col=True), unsafe_allow_html=True)

    # Legend
    st.markdown("---")
    st.markdown("""
    **Achievement Categories (Wall Street Style):**
    - **BEAT** (>85%): Exceeding expectations, potential upgrade
    - **MEET** (65-85%): On track to meet forecast
    - **MISS** (<65%): Below expectations, potential downgrade

    *Dynamic threshold: 25% per quarter = 75% expected at 9M*
    """)
