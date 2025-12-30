# Phase 1: Core UX Improvements

**Duration:** Day 1-2
**Priority:** P1 (High Impact)
**Parent Plan:** [plan.md](plan.md) | **Design:** [design-system-guide.md](design-system-guide.md)

---

## Objectives

1. Eliminate tab switching for stock data (unified table)
2. Add rating distribution badges in Tab 0 header (replaces chart)
3. Add quick action cards for 9M achievement (Tab 2)
4. Dynamic thresholds based on quarter

---

## Task 1.1: Unified Stock Table Component

**File:** `WEBAPP/components/tables/unified_forecast_table.py`

### Columns Design

| Group | Columns | Default Visible |
|-------|---------|-----------------|
| **Core** | Symbol, Price, Sector, Rating, Upside | ✅ Yes |
| **Valuation** | PE 25F, PE 26F, PB 25F, Δ PE | ✅ Yes |
| **Earnings** | NPATMI 25F, NPATMI 26F, Growth% | ✅ Yes |
| **Extended** | Rev 25F, Rev 26F, ROE, Target, MktCap | 🔲 Toggle |

### Sticky Columns Design (UX Critical)

**Problem:** Khi scroll sang xem Earnings/Extended columns, user quên mất đang xem mã nào.

**Solution:** Sticky first 2 columns (Symbol + Price)

| Column | Position | Sticky? | CSS `left` |
|--------|----------|---------|------------|
| Symbol | 1st | ✅ | `left: 0` |
| Price | 2nd | ✅ | `left: ~80px` (dynamic) |
| Others | 3rd+ | ❌ | scrollable |

**Implementation Notes:**
- CSS `position: sticky` với `z-index` layering
- Shadow effect khi scroll để visual separation
- Dynamic width calculation cho 2nd column offset
- Mobile: giảm xuống sticky 1 column (Symbol only)

### Implementation Pseudocode

```python
def unified_forecast_table(
    df: pd.DataFrame,
    show_extended: bool = False,
    highlight_first_col: bool = True
) -> str:
    """
    Single unified table replacing Valuation + Earnings tabs.

    Args:
        df: DataFrame with all BSC forecast columns
        show_extended: Show extended columns (Revenue, ROE, Target, MktCap)
        highlight_first_col: Highlight Symbol column

    Returns:
        HTML table string
    """

    # Sticky columns: Symbol + Price (first 2)
    core_cols = ['symbol', 'current_price', 'sector', 'rating', 'upside_pct']
    valuation_cols = ['pe_fwd_2025', 'pe_fwd_2026', 'pb_fwd_2025', 'pe_delta']
    earnings_cols = ['npatmi_2025f', 'npatmi_2026f', 'npatmi_growth_yoy_2026']
    extended_cols = ['rev_2025f', 'rev_2026f', 'roe_2025f', 'target_price', 'market_cap']

    if show_extended:
        all_cols = core_cols + valuation_cols + earnings_cols + extended_cols
    else:
        all_cols = core_cols + valuation_cols + earnings_cols

    # Build HTML table with column groups...
```

### Column Formatters

```python
COLUMN_FORMATTERS = {
    'symbol': lambda x: f'<b>{x}</b>',
    'current_price': format_price,         # 25,750 (sticky with Symbol)
    'upside_pct': format_upside,          # +12.5% green, -5.2% red
    'rating': format_rating_badge,         # Color-coded badge
    'pe_fwd_2025': lambda x: f'{x:.1f}x',
    'pe_fwd_2026': lambda x: f'{x:.1f}x',
    'pb_fwd_2025': lambda x: f'{x:.2f}x',
    'pe_delta': format_change,             # Delta with color
    'npatmi_2025f': format_billions,       # 17.8T
    'npatmi_2026f': format_billions,
    'npatmi_growth_yoy_2026': format_growth,
    'rev_2025f': format_billions,
    'rev_2026f': format_billions,
    'roe_2025f': lambda x: f'{x*100:.1f}%',
    'target_price': format_price,
    'market_cap': format_market_cap,
}
```

### Sticky Columns CSS

```css
/* Sticky Symbol column (1st) */
.unified-forecast-table th:nth-child(1),
.unified-forecast-table td:nth-child(1) {
    position: sticky;
    left: 0;
    background: rgba(26, 22, 37, 0.98);
    z-index: 2;
    min-width: 70px;
}

/* Sticky Price column (2nd) */
.unified-forecast-table th:nth-child(2),
.unified-forecast-table td:nth-child(2) {
    position: sticky;
    left: 70px; /* Symbol width */
    background: rgba(26, 22, 37, 0.98);
    z-index: 2;
    min-width: 80px;
    box-shadow: 2px 0 8px rgba(0, 0, 0, 0.3); /* Shadow để tách biệt */
}

/* Mobile: single sticky only */
@media (max-width: 768px) {
    .unified-forecast-table th:nth-child(2),
    .unified-forecast-table td:nth-child(2) {
        position: relative; /* Remove sticky */
        left: auto;
        box-shadow: none;
    }
}
```

---

## Task 1.2-1.3: Refactor Tab 0 (Individual)

**File:** `WEBAPP/pages/forecast/forecast_dashboard.py`

### Current Code to Remove

```python
# REMOVE this sub-tab logic
if active_tab == 0:
    view_tab = render_persistent_tabs(
        ["Valuation View", "Earnings View"],
        "forecast_view_tab",
        style="secondary"
    )

    if view_tab == 0:
        # Valuation table...
    elif view_tab == 1:
        # Earnings table...
```

### New Code

```python
if active_tab == 0:
    st.markdown("### Stock Forecast Overview")
    st.markdown("*92 stocks with PE/PB Forward and Earnings 2025-2026*")

    # Column toggle
    show_extended = st.toggle("Show Extended Columns", value=False, key="stock_table_extended")

    # Unified table
    from WEBAPP.components.tables.unified_forecast_table import unified_forecast_table
    html = unified_forecast_table(filtered_df, show_extended=show_extended)
    st.markdown(html, unsafe_allow_html=True)
```

---

## Task 1.4: Achievement Cards Component

**File:** `WEBAPP/components/cards/achievement_cards.py`

### Dynamic Threshold Logic

```python
def get_achievement_thresholds(ytd_months: int = 9) -> dict:
    """
    Calculate dynamic thresholds based on YTD months.

    Formula: expected = (ytd_months / 12) = quarters_completed * 0.25

    Args:
        ytd_months: Number of months in YTD data (3, 6, 9, or 12)

    Returns:
        Dict with revise_up, on_track_min, on_track_max, revise_down thresholds
    """
    expected = ytd_months / 12  # 0.25, 0.50, 0.75, or 1.0

    # ±20% tolerance around expected
    tolerance = 0.20

    return {
        'expected': expected,
        'revise_up_threshold': expected + tolerance,     # >95% for 9M
        'on_track_min': expected - tolerance,            # 55% for 9M
        'on_track_max': expected + tolerance,            # 95% for 9M
        'revise_down_threshold': expected - tolerance,   # <55% for 9M
        'ytd_label': f'{ytd_months}M',
    }

def categorize_achievement(achievement_pct: float, thresholds: dict) -> str:
    """Categorize stock by achievement status."""
    if pd.isna(achievement_pct):
        return 'no_data'
    if achievement_pct >= thresholds['revise_up_threshold']:
        return 'revise_up'
    elif achievement_pct >= thresholds['on_track_min']:
        return 'on_track'
    else:
        return 'revise_down'
```

### Card Component

**Note:** Uses SVG icons from `WEBAPP/components/ui/icons` instead of emojis.

```python
from WEBAPP.components.ui import icon, IconColor

def render_achievement_cards(
    df: pd.DataFrame,
    ytd_months: int = 9,
    metric_col: str = 'npatmi_achievement_pct'
) -> tuple[int, int, int, str]:
    """
    Render 3 clickable achievement cards with SVG icons.

    Returns:
        Tuple of (revise_up_count, on_track_count, revise_down_count, selected_filter)
    """
    thresholds = get_achievement_thresholds(ytd_months)

    # Categorize all stocks
    df['_achievement_status'] = df[metric_col].apply(
        lambda x: categorize_achievement(x, thresholds)
    )

    # Count by category
    counts = df['_achievement_status'].value_counts()
    revise_up = counts.get('revise_up', 0)
    on_track = counts.get('on_track', 0)
    revise_down = counts.get('revise_down', 0)

    # Get current filter from session state
    current_filter = st.session_state.get('achievement_filter', 'all')

    # Card definitions with SVG icons
    cards = [
        {
            'key': 'revise_up',
            'icon': icon('trending-up', size=24, color=IconColor.SUCCESS),
            'label': 'REVISE UP',
            'count': revise_up,
            'threshold': f">{thresholds['revise_up_threshold']*100:.0f}%",
            'color': IconColor.SUCCESS,
            'border': 'rgba(34, 197, 94, 0.4)',
        },
        {
            'key': 'on_track',
            'icon': icon('check-circle', size=24, color=IconColor.PRIMARY),
            'label': 'ON TRACK',
            'count': on_track,
            'threshold': f"{thresholds['on_track_min']*100:.0f}-{thresholds['on_track_max']*100:.0f}%",
            'color': IconColor.PRIMARY,
            'border': 'rgba(139, 92, 246, 0.4)',
        },
        {
            'key': 'revise_down',
            'icon': icon('trending-down', size=24, color=IconColor.ERROR),
            'label': 'REVISE DOWN',
            'count': revise_down,
            'threshold': f"<{thresholds['revise_down_threshold']*100:.0f}%",
            'color': IconColor.ERROR,
            'border': 'rgba(239, 68, 68, 0.4)',
        },
    ]

    # Render cards
    cols = st.columns(3)
    for i, card in enumerate(cards):
        with cols[i]:
            is_active = current_filter == card['key']
            bg = f"rgba({card['color']}, 0.1)" if is_active else "rgba(26, 22, 37, 0.8)"
            border = card['border'] if is_active else "rgba(255, 255, 255, 0.1)"

            html = f'''
            <div class="achievement-card" data-filter="{card['key']}" style="
                background: {bg};
                border: 1px solid {border};
            ">
                {card['icon']}
                <div class="count" style="color: {card['color']};">{card['count']}</div>
                <div class="label">{card['label']}</div>
                <div class="threshold">{card['threshold']}</div>
            </div>
            '''
            st.markdown(html, unsafe_allow_html=True)

            # Hidden button for click handling
            if st.button(card['label'], key=f"btn_{card['key']}", type="secondary"):
                st.session_state['achievement_filter'] = card['key']
                st.rerun()

    return revise_up, on_track, revise_down, current_filter
```

### Card Styling

```css
/* Achievement card styles */
.achievement-card {
    background: rgba(26, 22, 37, 0.8);
    border-radius: 12px;
    padding: 16px;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s ease;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.achievement-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.achievement-card.revise-up {
    border-color: rgba(34, 197, 94, 0.4);
}

.achievement-card.on-track {
    border-color: rgba(139, 92, 246, 0.4);
}

.achievement-card.revise-down {
    border-color: rgba(239, 68, 68, 0.4);
}

.achievement-card .count {
    font-size: 2rem;
    font-weight: 700;
}

.achievement-card .label {
    font-size: 0.85rem;
    color: #94A3B8;
}
```

---

## Task 1.5-1.6: Integrate into Tab 2

**File:** `WEBAPP/pages/forecast/forecast_dashboard.py`

### New Achievement Tab Code

```python
elif active_tab == 2:
    st.markdown("### Achievement Tracker")

    # Detect YTD months from data (based on latest date in YTD columns)
    ytd_months = detect_ytd_months(achievement_df)  # Returns 3, 6, 9, or 12

    st.markdown(f"*{ytd_months}M 2025 Achievement - Dynamic thresholds: 25% per quarter*")

    # Render clickable cards
    from WEBAPP.components.cards.achievement_cards import render_achievement_cards

    revise_up, on_track, revise_down, active_filter = render_achievement_cards(
        achievement_df,
        ytd_months=ytd_months,
        metric_col='npatmi_achievement_pct'
    )

    # Show clear filter button if filter active
    if active_filter != 'all':
        if st.button("✕ Clear Filter", key="clear_achievement_filter"):
            st.session_state['achievement_filter'] = 'all'
            st.rerun()

    # Filter table based on selection
    if active_filter != 'all':
        filtered_achievement_df = achievement_df[
            achievement_df['_achievement_status'] == active_filter
        ]
        st.markdown(f"**Showing: {active_filter.replace('_', ' ').title()}**")
    else:
        filtered_achievement_df = achievement_df

    # Render filtered table
    # ... existing table rendering code ...
```

### Helper Function: Detect YTD Months

```python
def detect_ytd_months(df: pd.DataFrame) -> int:
    """
    Detect number of months in YTD data.

    Logic:
    - Check column names for clues (rev_ytd_2025, npatmi_ytd_2025)
    - Or infer from data freshness

    Returns:
        3, 6, 9, or 12
    """
    # For now, hardcode based on current data
    # TODO: Make dynamic based on fundamental data availability
    from datetime import datetime
    current_month = datetime.now().month

    if current_month <= 3:
        return 3  # Q1 data available
    elif current_month <= 6:
        return 6  # Q2 data available
    elif current_month <= 9:
        return 9  # Q3 data available
    else:
        return 12  # Full year data
```

---

## Testing Checklist

### Unified Table
- [ ] All 12+ columns render correctly
- [ ] Column toggle shows/hides extended columns
- [ ] **Sticky 2 columns works** (Symbol + Price fixed when scroll)
- [ ] Shadow effect visible khi scroll horizontally
- [ ] Mobile: single sticky column (Symbol only)
- [ ] Mobile horizontal scroll works
- [ ] Formatters apply correctly (billions, %, badges)

### Achievement Cards
- [ ] Cards show correct counts
- [ ] Card click updates session state
- [ ] Table filters correctly
- [ ] "Clear Filter" button works
- [ ] Dynamic thresholds calculate correctly for Q1/Q2/Q3/Q4

### Session State
- [ ] `forecast_active_tab` persists
- [ ] `achievement_filter` persists across interactions
- [ ] `stock_table_extended` toggle persists

---

## Estimated Time

| Task | Time |
|------|------|
| 1.1 Unified table component | 2h |
| 1.2-1.3 Refactor Tab 0 | 1.5h |
| 1.4 Achievement cards | 1.5h |
| 1.5-1.6 Integrate cards | 1h |
| Testing & polish | 1h |
| **Total** | **7h** |

---

## Deliverables

After Phase 1 completion:
- ✅ Single unified stock table (zero sub-tabs)
- ✅ 3 clickable achievement cards with dynamic thresholds
- ✅ Filter by achievement status
- ✅ "Clear Filter" functionality
