# Phase 1: Foundation

**Effort:** 1-2 days
**Dependencies:** None
**Files to modify:** 3

---

## Objectives

1. Create centralized filter constants
2. Add sync state keys to session_state
3. Remove useless global ticker search from sidebar

---

## Task 1.1: Create Filter Constants

**File:** `WEBAPP/components/filters/constants.py` (NEW)

```python
"""
Filter Constants
================
Centralized constants for all dashboard filters.
Single source of truth - import from here, don't redefine.
"""

# Timeframe options (used by Technical, Sector, FX)
TIMEFRAME_OPTIONS = {
    "30D": 30,
    "60D": 60,
    "90D": 90,
    "180D": 180,
    "1Y": 252,
    "2Y": 504,
}

# Period options (used by Fundamental pages)
PERIOD_OPTIONS = ["Quarterly", "Yearly"]

# Default number of periods to show
DEFAULT_NUM_PERIODS = 8
MAX_NUM_PERIODS = 20
MIN_NUM_PERIODS = 4

# Signal types (used by Technical)
SIGNAL_TYPES = {
    "all": "All Signals",
    "ma_crossover": "MA Cross",
    "volume_spike": "Volume",
    "breakout": "Breakout",
    "patterns": "Patterns",
}

# Trend options (used by Stock Scanner)
TREND_OPTIONS = {
    "all": "All Trends",
    "uptrend": "Uptrend",
    "downtrend": "Downtrend",
    "sideways": "Sideways",
}

# Direction options (used by Stock Scanner)
DIRECTION_OPTIONS = {
    "all": "All Directions",
    "buy": "BUY",
    "sell": "SELL",
    "pullback": "Pullback",
    "bounce": "Bounce",
}

# Entity configurations (for fundamental_filter_bar)
ENTITY_CONFIGS = {
    "company": {
        "default_ticker": "VNM",
        "ticker_key": "selected_ticker",
        "period_key": "company_timeframe",
    },
    "bank": {
        "default_ticker": "VCB",
        "ticker_key": "selected_bank",
        "period_key": "bank_timeframe",
    },
    "security": {
        "default_ticker": "SSI",
        "ticker_key": "selected_security",
        "period_key": "security_timeframe",
    },
}

# Sort options (used by Forecast)
FORECAST_SORT_OPTIONS = {
    "upside_desc": "Upside % (High to Low)",
    "upside_asc": "Upside % (Low to High)",
    "pe_asc": "PE FWD 2025 (Low to High)",
    "pe_desc": "PE FWD 2025 (High to Low)",
    "mcap_desc": "Market Cap (High to Low)",
    "growth_desc": "Profit Growth 26F (High to Low)",
}

# Rating options (used by Forecast)
RATING_OPTIONS = ["STRONG BUY", "BUY", "HOLD", "SELL", "N/A"]
```

**Verify:**
```bash
python3 -c "from WEBAPP.components.filters.constants import TIMEFRAME_OPTIONS, ENTITY_CONFIGS; print('OK')"
```

---

## Task 1.2: Add Sync State Keys

**File:** `WEBAPP/core/session_state.py` (MODIFY)

Add new sync keys to `PAGE_STATE_DEFAULTS['global']`:

```python
PAGE_STATE_DEFAULTS: Dict[str, Dict[str, Any]] = {
    'global': {
        'global_ticker_search': '',
        'quick_search_ticker': None,
        'search_select': None,
        # NEW: Cross-page sync state
        'sync_last_ticker': None,       # "ACB"
        'sync_last_entity': None,       # "BANK"
        'sync_last_sector': None,       # "Ngân hàng"
        'sync_timestamp': None,         # datetime when set
    },
    # ... rest unchanged
}
```

Add helper functions at end of file:

```python
# ============================================================================
# CROSS-PAGE SYNC HELPERS
# ============================================================================

def set_synced_ticker(ticker: str, entity_type: str, sector: str = None) -> None:
    """
    Set the synced ticker for cross-page navigation.
    Called when user selects a ticker in Fundamental pages.

    Args:
        ticker: Stock symbol (e.g., "ACB")
        entity_type: Entity type ("BANK", "COMPANY", "SECURITY")
        sector: Optional sector name
    """
    from datetime import datetime
    st.session_state['sync_last_ticker'] = ticker
    st.session_state['sync_last_entity'] = entity_type
    st.session_state['sync_last_sector'] = sector
    st.session_state['sync_timestamp'] = datetime.now()


def get_synced_ticker() -> Optional[str]:
    """Get the last synced ticker, or None if not set."""
    return st.session_state.get('sync_last_ticker')


def get_synced_entity() -> Optional[str]:
    """Get the entity type of synced ticker."""
    return st.session_state.get('sync_last_entity')


def clear_synced_ticker() -> None:
    """Clear the synced ticker state."""
    st.session_state['sync_last_ticker'] = None
    st.session_state['sync_last_entity'] = None
    st.session_state['sync_last_sector'] = None
    st.session_state['sync_timestamp'] = None


def has_synced_ticker() -> bool:
    """Check if there's a synced ticker."""
    return st.session_state.get('sync_last_ticker') is not None
```

---

## Task 1.3: Remove Global Ticker Search

**File:** `WEBAPP/main_app.py` (MODIFY)

Find and remove the global ticker search section in sidebar. Look for:
- `quick_search_ticker`
- `global_ticker_search`
- Search input + dropdown combo

Replace with simpler navigation-only sidebar:

```python
# In sidebar section, REMOVE:
# - st.text_input for ticker search
# - st.selectbox for search results
# - Any logic that sets quick_search_ticker

# KEEP:
# - Page navigation buttons
# - Theme toggle (if any)
# - About/Info section (if any)
```

**Expected removal:** ~20-30 lines related to global search.

---

## Verification Checklist

- [ ] `constants.py` created and importable
- [ ] `session_state.py` has new sync keys
- [ ] `main_app.py` sidebar no longer shows ticker search
- [ ] Dashboard loads without errors: `streamlit run WEBAPP/main_app.py`
- [ ] All existing pages still work

---

## Files Changed

| File | Action | Lines |
|------|--------|-------|
| `WEBAPP/components/filters/constants.py` | CREATE | ~80 |
| `WEBAPP/core/session_state.py` | MODIFY | +40 |
| `WEBAPP/main_app.py` | MODIFY | -25 |

**Net change:** +95 lines (mostly new constants file)
