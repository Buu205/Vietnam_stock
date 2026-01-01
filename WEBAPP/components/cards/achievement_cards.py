"""
Achievement Cards Component
===========================
3 clickable action cards for 9M Achievement filtering.

Categories (Wall Street style):
- BEAT:  Achievement% > 85%  (Beating expectations)
- MEET:  Achievement% 65-85% (Meeting expectations)
- MISS:  Achievement% < 65%  (Missing expectations)

Design: Dark theme with teal/gold/red accent colors
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Optional, Tuple

# Achievement thresholds
BEAT_THRESHOLD = 0.85  # > 85%
MEET_THRESHOLD = 0.65  # 65-85%
# MISS: < 65%

# Card styling
CARD_COLORS = {
    'beat': {
        'bg': 'rgba(0, 201, 173, 0.15)',
        'border': 'rgba(0, 201, 173, 0.4)',
        'text': '#00C9AD',
        'icon': '▲',
        'label': 'BEAT',
        'desc': 'Beating expectations'
    },
    'meet': {
        'bg': 'rgba(255, 193, 50, 0.15)',
        'border': 'rgba(255, 193, 50, 0.4)',
        'text': '#FFC132',
        'icon': '═',
        'label': 'MEET',
        'desc': 'Meeting expectations'
    },
    'miss': {
        'bg': 'rgba(239, 68, 68, 0.15)',
        'border': 'rgba(239, 68, 68, 0.4)',
        'text': '#EF4444',
        'icon': '▼',
        'label': 'MISS',
        'desc': 'Missing expectations'
    }
}

ACHIEVEMENT_CARDS_STYLE = """
<style>
.achievement-cards-container {
    display: flex;
    gap: 16px;
    margin-bottom: 20px;
    flex-wrap: wrap;
}

.achievement-card {
    flex: 1;
    min-width: 200px;
    padding: 16px 20px;
    border-radius: 12px;
    cursor: pointer;
    transition: all 200ms ease;
    border: 1px solid;
    position: relative;
}

.achievement-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.achievement-card.active {
    border-width: 2px;
    box-shadow: 0 0 16px rgba(139, 92, 246, 0.3);
}

.achievement-card-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 8px;
}

.achievement-card-icon {
    font-size: 18px;
    font-weight: bold;
}

.achievement-card-label {
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 0.05em;
}

.achievement-card-count {
    font-size: 28px;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
    margin-bottom: 4px;
}

.achievement-card-desc {
    font-size: 11px;
    color: #94A3B8;
    margin-bottom: 8px;
}

.achievement-card-stats {
    display: flex;
    gap: 16px;
    font-size: 11px;
    color: #64748B;
    margin-bottom: 8px;
}

.achievement-card-stocks {
    font-size: 10px;
    color: #64748B;
    padding-top: 8px;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.achievement-card-stocks span {
    font-weight: 600;
}

/* Beat card */
.card-beat {
    background: rgba(0, 201, 173, 0.1);
    border-color: rgba(0, 201, 173, 0.3);
}
.card-beat:hover { border-color: rgba(0, 201, 173, 0.6); }
.card-beat .achievement-card-icon,
.card-beat .achievement-card-label,
.card-beat .achievement-card-count { color: #00C9AD; }

/* Meet card */
.card-meet {
    background: rgba(255, 193, 50, 0.1);
    border-color: rgba(255, 193, 50, 0.3);
}
.card-meet:hover { border-color: rgba(255, 193, 50, 0.6); }
.card-meet .achievement-card-icon,
.card-meet .achievement-card-label,
.card-meet .achievement-card-count { color: #FFC132; }

/* Miss card */
.card-miss {
    background: rgba(239, 68, 68, 0.1);
    border-color: rgba(239, 68, 68, 0.3);
}
.card-miss:hover { border-color: rgba(239, 68, 68, 0.6); }
.card-miss .achievement-card-icon,
.card-miss .achievement-card-label,
.card-miss .achievement-card-count { color: #EF4444; }

/* Active state */
.achievement-card.active {
    border-width: 2px;
}
</style>
"""


def classify_achievement(ach_pct: float) -> str:
    """Classify achievement percentage into category."""
    if pd.isna(ach_pct):
        return 'meet'  # Default
    if ach_pct > BEAT_THRESHOLD:
        return 'beat'
    elif ach_pct >= MEET_THRESHOLD:
        return 'meet'
    else:
        return 'miss'


def calculate_achievement_stats(df: pd.DataFrame) -> Dict[str, Dict]:
    """
    Calculate achievement statistics from forecast data.

    Args:
        df: DataFrame with columns:
            - symbol: Stock ticker
            - achievement_pct: 9M actual / FY forecast (decimal, e.g., 0.79 for 79%)
            - upside_pct: Upside percentage (decimal)
            - sector: Sector name (optional)

    Returns:
        Dict with beat/meet/miss stats: count, avg_upside, avg_ach, stocks list
    """
    if df.empty:
        return {
            'beat': {'count': 0, 'avg_upside': 0, 'avg_ach': 0, 'stocks': []},
            'meet': {'count': 0, 'avg_upside': 0, 'avg_ach': 0, 'stocks': []},
            'miss': {'count': 0, 'avg_upside': 0, 'avg_ach': 0, 'stocks': []},
        }

    # Ensure achievement_pct column exists
    if 'achievement_pct' not in df.columns:
        return {
            'beat': {'count': 0, 'avg_upside': 0, 'avg_ach': 0, 'stocks': []},
            'meet': {'count': 0, 'avg_upside': 0, 'avg_ach': 0, 'stocks': []},
            'miss': {'count': 0, 'avg_upside': 0, 'avg_ach': 0, 'stocks': []},
        }

    # Classify each stock
    df = df.copy()
    df['ach_category'] = df['achievement_pct'].apply(classify_achievement)

    stats = {}
    for cat in ['beat', 'meet', 'miss']:
        cat_df = df[df['ach_category'] == cat]

        if cat_df.empty:
            stats[cat] = {'count': 0, 'avg_upside': 0, 'avg_ach': 0, 'stocks': []}
        else:
            # Get top stocks by upside (for display)
            top_stocks = cat_df.nlargest(5, 'upside_pct')['symbol'].tolist() if 'upside_pct' in cat_df.columns else cat_df.head(5)['symbol'].tolist()

            stats[cat] = {
                'count': len(cat_df),
                'avg_upside': cat_df['upside_pct'].mean() * 100 if 'upside_pct' in cat_df.columns else 0,
                'avg_ach': cat_df['achievement_pct'].mean() * 100,
                'stocks': top_stocks
            }

    return stats


def render_achievement_cards(
    stats: Dict[str, Dict],
    active_filter: str = 'all',
    key_prefix: str = 'ach'
) -> str:
    """
    Render 3 achievement cards as HTML.

    Args:
        stats: Dict from calculate_achievement_stats()
        active_filter: Current active filter ('all', 'beat', 'meet', 'miss')
        key_prefix: Prefix for session state keys

    Returns:
        HTML string for cards
    """
    html = ACHIEVEMENT_CARDS_STYLE
    html += '<div class="achievement-cards-container">'

    for cat in ['beat', 'meet', 'miss']:
        config = CARD_COLORS[cat]
        data = stats.get(cat, {'count': 0, 'avg_upside': 0, 'avg_ach': 0, 'stocks': []})

        active_class = 'active' if active_filter == cat else ''
        stocks_display = ' '.join(data['stocks'][:4]) if data['stocks'] else '-'

        html += f'''
        <div class="achievement-card card-{cat} {active_class}" data-category="{cat}">
            <div class="achievement-card-header">
                <span class="achievement-card-icon">{config['icon']}</span>
                <span class="achievement-card-label">{config['label']}</span>
            </div>
            <div class="achievement-card-count">{data['count']}</div>
            <div class="achievement-card-desc">{config['desc']}</div>
            <div class="achievement-card-stats">
                <span>Avg Upside: {data['avg_upside']:+.1f}%</span>
                <span>Avg Ach: {data['avg_ach']:.0f}%</span>
            </div>
            <div class="achievement-card-stocks">
                Top: <span>{stocks_display}</span>
            </div>
        </div>
        '''

    html += '</div>'
    return html


def render_achievement_cards_interactive(
    df: pd.DataFrame,
    key_prefix: str = 'forecast'
) -> Tuple[str, pd.DataFrame]:
    """
    Render interactive achievement cards with Streamlit buttons.

    Args:
        df: DataFrame with achievement data
        key_prefix: Session state key prefix

    Returns:
        Tuple of (selected_filter, filtered_df)
    """
    # Initialize session state
    filter_key = f'{key_prefix}_achievement_filter'
    if filter_key not in st.session_state:
        st.session_state[filter_key] = 'all'

    # Calculate stats
    stats = calculate_achievement_stats(df)

    # Render cards with buttons
    cols = st.columns([1, 1, 1, 0.5])

    categories = ['beat', 'meet', 'miss']
    for i, cat in enumerate(categories):
        config = CARD_COLORS[cat]
        data = stats.get(cat, {'count': 0, 'avg_upside': 0, 'stocks': []})

        with cols[i]:
            # Card container
            is_active = st.session_state[filter_key] == cat
            border_width = '2px' if is_active else '1px'

            st.markdown(f"""
            <div style="
                background: {config['bg']};
                border: {border_width} solid {config['border']};
                border-radius: 12px;
                padding: 16px;
                margin-bottom: 8px;
            ">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                    <span style="color: {config['text']}; font-size: 18px;">{config['icon']}</span>
                    <span style="color: {config['text']}; font-weight: 700;">{config['label']}</span>
                </div>
                <div style="color: {config['text']}; font-size: 28px; font-weight: 700; font-family: monospace;">
                    {data['count']}
                </div>
                <div style="color: #94A3B8; font-size: 11px; margin-bottom: 8px;">
                    {config['desc']}
                </div>
                <div style="color: #64748B; font-size: 11px;">
                    Avg Upside: {data['avg_upside']:+.1f}%
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Button for filter
            if st.button(
                f"Filter {config['label']}" if st.session_state[filter_key] != cat else "✓ Selected",
                key=f'{key_prefix}_btn_{cat}',
                width='stretch',
                type='primary' if is_active else 'secondary'
            ):
                st.session_state[filter_key] = cat
                st.rerun()

    # Clear filter button
    with cols[3]:
        st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)
        if st.button("Clear", key=f'{key_prefix}_clear_filter', width='stretch'):
            st.session_state[filter_key] = 'all'
            st.rerun()

    # Filter dataframe
    current_filter = st.session_state[filter_key]
    if current_filter != 'all' and 'achievement_pct' in df.columns:
        df = df.copy()
        df['ach_category'] = df['achievement_pct'].apply(classify_achievement)
        filtered_df = df[df['ach_category'] == current_filter]
    else:
        filtered_df = df

    return current_filter, filtered_df


def get_achievement_summary_from_service(service) -> Dict[str, Dict]:
    """
    Get achievement summary from ForecastService.

    Args:
        service: ForecastService instance

    Returns:
        Dict with beat/meet/miss stats
    """
    try:
        return service.get_achievement_summary()
    except Exception as e:
        return {
            'beat': {'count': 0, 'avg_upside': 0, 'avg_ach': 0, 'stocks': []},
            'meet': {'count': 0, 'avg_upside': 0, 'avg_ach': 0, 'stocks': []},
            'miss': {'count': 0, 'avg_upside': 0, 'avg_ach': 0, 'stocks': []},
        }
