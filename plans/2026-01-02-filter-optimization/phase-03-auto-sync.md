# Phase 3: Auto-Sync Integration

**Effort:** 1-2 days
**Dependencies:** Phase 2 (fundamental pages set sync state)
**Files to modify:** 3

---

## Objectives

1. Forecast page: Highlight synced ticker row in tables
2. Technical page: Pre-fill Single Stock Analysis input
3. Add visual indicators for sync state

---

## Task 3.1: Forecast Sync Integration

**File:** `WEBAPP/pages/forecast/forecast_dashboard.py` (MODIFY)

### Add sync indicator after header:

```python
from WEBAPP.core.session_state import get_synced_ticker, get_synced_entity, clear_synced_ticker, has_synced_ticker

# After title and metrics, before tabs:
st.title("BSC Forecast Analysis")
# ... metric cards ...

# Sync indicator
synced_ticker = None
if has_synced_ticker():
    synced_ticker = get_synced_ticker()
    entity = get_synced_entity()
    entity_label = {'BANK': 'Bank', 'COMPANY': 'Company', 'SECURITY': 'Security'}.get(entity, entity)

    col1, col2 = st.columns([6, 1])
    with col1:
        st.info(f"📍 Viewing: **{synced_ticker}** (from {entity_label} page)")
    with col2:
        if st.button("Clear", key="forecast_clear_sync"):
            clear_synced_ticker()
            st.rerun()
```

### Highlight row in tables:

In `render_bsc_universal_tab` and other tab functions, add row highlighting:

```python
def highlight_synced_row(df: pd.DataFrame, synced_ticker: str) -> pd.DataFrame:
    """Apply background highlight to synced ticker row."""
    if not synced_ticker or synced_ticker not in df['ticker'].values:
        return df

    def highlight_row(row):
        if row['ticker'] == synced_ticker:
            return ['background-color: rgba(0, 201, 173, 0.15)'] * len(row)
        return [''] * len(row)

    return df.style.apply(highlight_row, axis=1)
```

Usage in tab rendering:
```python
# When displaying table
if synced_ticker and synced_ticker in filtered_df['ticker'].values:
    # Scroll to row or highlight
    st.markdown(f"<script>document.querySelector('[data-ticker=\"{synced_ticker}\"]')?.scrollIntoView()</script>", unsafe_allow_html=True)
```

---

## Task 3.2: Technical Sync Integration

**File:** `WEBAPP/pages/technical/components/stock_scanner.py` (MODIFY)

### Pre-fill Single Stock Analysis:

Find the Single Stock Analysis section (~line 925-1166) and add:

```python
from WEBAPP.core.session_state import get_synced_ticker, has_synced_ticker

def render_single_stock_analysis(service):
    """Render single stock analysis section."""

    # Check for synced ticker
    default_ticker = ""
    synced_indicator = ""
    if has_synced_ticker():
        default_ticker = get_synced_ticker()
        synced_indicator = "(synced from Fundamental)"

    # Ticker input with pre-filled value
    col1, col2 = st.columns([3, 1])
    with col1:
        ticker_input = st.text_input(
            "Enter Ticker",
            value=default_ticker,
            placeholder="VCB, ACB, FPT...",
            key="single_stock_ticker"
        )
    with col2:
        if synced_indicator:
            st.caption(synced_indicator)

    # Rest of analysis...
```

---

## Task 3.3: Update Stock Scanner Filter State

**File:** `WEBAPP/pages/technical/components/stock_scanner.py` (MODIFY)

Also update the quick search to show synced ticker:

```python
# In quick search section:
if has_synced_ticker():
    synced = get_synced_ticker()
    if not st.session_state.get('scanner_quick_search'):
        st.session_state['scanner_quick_search'] = synced
```

---

## Verification Checklist

- [ ] Navigate to Company → select VNM → go to Forecast → see "Viewing: VNM"
- [ ] Forecast table highlights VNM row (if exists in data)
- [ ] Clear button removes sync indicator
- [ ] Navigate to Bank → select ACB → go to Technical → Single Stock Analysis pre-filled with ACB
- [ ] Stock Scanner quick search shows synced ticker

---

## Visual Indicator Styles

Add to page styles if needed:

```css
/* Sync indicator style */
.sync-indicator {
    background: rgba(0, 201, 173, 0.1);
    border-left: 3px solid #00C9AD;
    padding: 8px 16px;
    border-radius: 0 8px 8px 0;
    margin-bottom: 16px;
}

/* Highlighted row */
.synced-row {
    background: rgba(0, 201, 173, 0.15) !important;
}
```

---

## Files Changed

| File | Action | Lines |
|------|--------|-------|
| `WEBAPP/pages/forecast/forecast_dashboard.py` | MODIFY | +30 |
| `WEBAPP/pages/technical/components/stock_scanner.py` | MODIFY | +20 |
| `WEBAPP/pages/forecast/tabs/bsc_universal_tab.py` | MODIFY | +15 |

**Net change:** +65 lines
