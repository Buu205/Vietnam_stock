# Phase 5: Integration + Cleanup

**Goal:** Integrate all tabs into unified dashboard, cleanup old code

---

## 0. Review Fixes Applied (2025-12-25)

> Based on [review-report.md](review-report.md), the following fixes have been applied:

| Issue | Fix | Location |
|-------|-----|----------|
| Service instantiation repeated | Singleton pattern with `get_ta_service()` | phase-01, here |
| No caching strategy | `@st.cache_data(ttl=300/60)` decorators | phase-01 |
| Filters not synced | Session state for shared filters | Section 1.1 below |
| Quadrant logic duplicated | Extracted to `quadrant.py` | phase-01 |
| Calculations scattered | TA Indicator base classes | phase-01 |

---

## 1. Main Dashboard Structure (Updated)

> **Updated 2025-12-25**: Added singleton service + session state filters

```python
# File: WEBAPP/pages/technical/technical_dashboard.py

import streamlit as st
from .components.market_overview import render_market_overview
from .components.sector_rotation import render_sector_rotation
from .components.stock_scanner import render_stock_scanner
from .components.trading_lists import render_trading_lists
from .services.ta_dashboard_service import get_ta_service  # Singleton!

st.set_page_config(
    page_title="Technical Dashboard",
    page_icon="📊",
    layout="wide"
)

def init_session_state():
    """Initialize shared filters in session state"""
    if 'ta_selected_sector' not in st.session_state:
        st.session_state.ta_selected_sector = "All"
    if 'ta_selected_signal' not in st.session_state:
        st.session_state.ta_selected_signal = "All"
    if 'ta_search_symbol' not in st.session_state:
        st.session_state.ta_search_symbol = ""


def main():
    st.title("📊 Technical Dashboard")
    st.caption("Market → Sector → Stock | 3-Layer Systematic Trading")

    # Initialize session state for shared filters
    init_session_state()

    # Get singleton service - pass to ALL components
    service = get_ta_service()

    # Quick market status header
    render_market_status_header(service)

    st.markdown("---")

    # Create tabs (Tab 4 deferred to Phase 2)
    tab1, tab2, tab3 = st.tabs([
        "🏛️ Market Overview",
        "🔄 Sector Rotation",
        "🔍 Stock Scanner"
    ])

    # IMPORTANT: Pass service to all components
    with tab1:
        render_market_overview(service)

    with tab2:
        render_sector_rotation(service)

    with tab3:
        render_stock_scanner(service)


def render_market_status_header(service: TADashboardService):
    """Quick status bar at top of page"""

    market_state = service.get_market_state()

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "VN-Index",
            f"{market_state.vnindex_close:,.0f}",
            f"{market_state.vnindex_change_pct:+.2f}%"
        )

    with col2:
        regime_color = {
            'BULLISH': '🟢',
            'NEUTRAL': '🟡',
            'BEARISH': '🔴'
        }.get(market_state.regime, '⚪')
        st.metric("Regime", f"{regime_color} {market_state.regime}")

    with col3:
        st.metric(
            "Breadth MA20",
            f"{market_state.breadth_ma20_pct:.1f}%"
        )

    with col4:
        st.metric(
            "Exposure",
            f"{market_state.exposure_level}%"
        )

    with col5:
        signal_color = {
            'RISK_ON': '🟢',
            'CAUTION': '🟡',
            'RISK_OFF': '🔴'
        }.get(market_state.signal, '⚪')
        st.metric("Signal", f"{signal_color} {market_state.signal}")


if __name__ == "__main__":
    main()
```

---

## 1.1 Filter Sync Pattern (NEW)

> **Added 2025-12-25**: Sync filters across all tabs using session state

```python
# Pattern for synced filters in each component

def render_sector_filter(service: TADashboardService) -> str:
    """
    Render sector filter that syncs across tabs.
    Call this in any component that needs sector filter.
    """
    sector_list = ["All"] + service._load_sector_list()

    # Get current value from session state
    current = st.session_state.ta_selected_sector

    # Find index (handle if sector no longer exists)
    try:
        idx = sector_list.index(current)
    except ValueError:
        idx = 0

    # Render selectbox - updates session state automatically via key
    selected = st.selectbox(
        "Ngành",
        options=sector_list,
        index=idx,
        key="sector_filter_widget"  # Unique key per widget
    )

    # Update session state
    st.session_state.ta_selected_sector = selected

    return selected


def render_symbol_search() -> str:
    """
    Render symbol search that syncs across tabs.
    """
    return st.text_input(
        "Tìm mã",
        value=st.session_state.ta_search_symbol,
        key="symbol_search_widget",
        placeholder="VD: ACB, VCB...",
        on_change=lambda: setattr(
            st.session_state,
            'ta_search_symbol',
            st.session_state.symbol_search_widget
        )
    )


# Usage in components:
# ─────────────────────────────────────────────────────────────────

# In sector_rotation.py
def render_sector_rotation(service: TADashboardService):
    col1, col2 = st.columns([1, 3])

    with col1:
        sector = render_sector_filter(service)

    # Use sector for filtering
    if sector != "All":
        data = data[data['sector_code'] == sector]


# In stock_scanner.py
def render_stock_scanner(service: TADashboardService):
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        sector = render_sector_filter(service)  # Same filter, synced!

    with col2:
        symbol = render_symbol_search()

    # Use sector + symbol for filtering
    signals = service.get_signals()
    if sector != "All":
        signals = signals[signals['sector_code'] == sector]
    if symbol:
        signals = signals[signals['symbol'].str.contains(symbol.upper())]
```

**Session State Keys:**
| Key | Type | Default | Used In |
|-----|------|---------|---------|
| `ta_selected_sector` | str | "All" | Tab 2, Tab 3 |
| `ta_selected_signal` | str | "All" | Tab 3 |
| `ta_search_symbol` | str | "" | Tab 3 |

---

## 2. Final File Structure

```
WEBAPP/pages/technical/
├── __init__.py
├── technical_dashboard.py          # Main entry point (refactored)
├── components/
│   ├── __init__.py
│   ├── market_overview.py          # Tab 1: Regime, breadth, exposure
│   ├── sector_rotation.py          # Tab 2: RRG, ranking, money flow
│   ├── stock_scanner.py            # Tab 3: Signal scanner
│   └── trading_lists.py            # Tab 4: Buy/sell lists
└── services/
    ├── __init__.py
    └── ta_dashboard_service.py     # Unified data service

WEBAPP/core/models/
└── market_state.py                 # MarketState, BreadthHistory dataclasses
```

---

## 3. Files to Delete (Cleanup)

After successful integration, remove:

```bash
# Old individual stock TA page (replaced by unified dashboard)
# BACKUP FIRST if needed

# Review these files - may be deprecated:
# WEBAPP/pages/technical/technical_dashboard.py (old version - REPLACE, don't delete)
```

**Note:** The current `technical_dashboard.py` will be REPLACED, not deleted. Keep backup if needed.

---

## 4. Init Files

### WEBAPP/pages/technical/__init__.py
```python
from .technical_dashboard import main as technical_dashboard

__all__ = ['technical_dashboard']
```

### WEBAPP/pages/technical/components/__init__.py
```python
from .market_overview import render_market_overview
from .sector_rotation import render_sector_rotation
from .stock_scanner import render_stock_scanner
# from .trading_lists import render_trading_lists  # Deferred to Phase 2

__all__ = [
    'render_market_overview',
    'render_sector_rotation',
    'render_stock_scanner',
    # 'render_trading_lists'  # Deferred
]
```

### Component Signatures (Updated)

> **All components now receive service as parameter**

```python
# market_overview.py
def render_market_overview(service: TADashboardService) -> None:
    """Tab 1: Market regime, breadth chart, exposure gauge"""
    ...

# sector_rotation.py
def render_sector_rotation(service: TADashboardService) -> None:
    """Tab 2: RRG chart, sector ranking, money flow"""
    ...

# stock_scanner.py
def render_stock_scanner(service: TADashboardService) -> None:
    """Tab 3: Signal scanner with filters"""
    ...
```

### WEBAPP/pages/technical/services/__init__.py
```python
from .ta_dashboard_service import TADashboardService, get_ta_service

__all__ = ['TADashboardService', 'get_ta_service']
```

### WEBAPP/core/models/__init__.py (update)
```python
# Add to existing __init__.py
from .market_state import MarketState, BreadthHistory

__all__ = [
    # ... existing exports ...
    'MarketState',
    'BreadthHistory'
]
```

---

## 5. Integration Testing

### 5.1 Data Pipeline Check

Before running dashboard, verify data files exist:

```python
# Test script: test_ta_dashboard_data.py

from pathlib import Path

DATA_ROOT = Path("DATA/processed/technical")

required_files = [
    "market_breadth/market_breadth_daily.parquet",
    "vnindex/vnindex_indicators.parquet",
    "sector_breadth/sector_breadth_daily.parquet",
    "money_flow/sector_money_flow_1d.parquet",
    "alerts/daily/combined_latest.parquet",
]

for file in required_files:
    path = DATA_ROOT / file
    if path.exists():
        print(f"✅ {file}")
    else:
        print(f"❌ {file} - MISSING")
```

### 5.2 Service Test

```python
# Test TADashboardService methods

from WEBAPP.pages.technical.services import TADashboardService

service = TADashboardService()

# Test each method
market_state = service.get_market_state()
print(f"Market Regime: {market_state.regime}")
print(f"Exposure: {market_state.exposure_level}%")

breadth_history = service.get_breadth_history(days=30)
print(f"Breadth history: {len(breadth_history.date)} days")

sector_ranking = service.get_sector_ranking()
if sector_ranking is not None:
    print(f"Top sector: {sector_ranking.iloc[0]['sector_code']}")

signals = service.get_signals()
if signals is not None:
    print(f"Signals today: {len(signals)}")
```

### 5.3 UI Test

```bash
# Run dashboard
streamlit run WEBAPP/main_app.py

# Navigate to Technical Dashboard
# Test each tab:
# 1. Market Overview - Check breadth chart renders
# 2. Sector Rotation - Check RRG and ranking table
# 3. Stock Scanner - Test filters
# 4. Trading Lists - Check position sizing
```

---

## 6. Performance Requirements

| Metric | Target | Notes |
|--------|--------|-------|
| Page load | < 3 seconds | Use caching |
| Tab switch | < 500ms | Lazy loading |
| Filter apply | < 1 second | Pre-computed data |

### Caching Strategy

```python
# Add caching to service methods

import streamlit as st

class TADashboardService:

    @st.cache_data(ttl=300)  # 5 min cache
    def get_market_state(_self):
        # ... implementation

    @st.cache_data(ttl=300)
    def get_breadth_history(_self, days: int = 180):
        # ... implementation

    @st.cache_data(ttl=60)  # 1 min cache for signals
    def get_signals(_self, **filters):
        # ... implementation
```

---

## 7. Implementation Checklist

### Phase 5.1: Setup Structure
- [ ] Create `WEBAPP/pages/technical/components/` directory
- [ ] Create `WEBAPP/pages/technical/services/` directory
- [ ] Create `WEBAPP/core/models/market_state.py`
- [ ] Create all `__init__.py` files

### Phase 5.2: Implement Service
- [ ] Implement `TADashboardService` with all methods
- [ ] Add caching decorators
- [ ] Test data loading

### Phase 5.3: Implement Components
- [ ] Implement `market_overview.py`
- [ ] Implement `sector_rotation.py`
- [ ] Implement `stock_scanner.py`
- [ ] Implement `trading_lists.py`

### Phase 5.4: Integrate Main Dashboard
- [ ] Refactor `technical_dashboard.py`
- [ ] Add tab structure
- [ ] Add status header
- [ ] Test all tabs

### Phase 5.5: Testing & Cleanup
- [ ] Run data pipeline check
- [ ] Run service tests
- [ ] Run UI tests
- [ ] Verify page load < 3 seconds
- [ ] Backup and remove deprecated files

---

## 8. Rollback Plan

If issues arise after deployment:

1. **Restore old dashboard:**
   ```bash
   # If backup was made
   cp WEBAPP/pages/technical/technical_dashboard.py.bak \
      WEBAPP/pages/technical/technical_dashboard.py
   ```

2. **Check logs:**
   ```bash
   # Streamlit logs
   streamlit run WEBAPP/main_app.py 2>&1 | tee app.log
   ```

3. **Verify data files:**
   ```bash
   # Check parquet files are not corrupted
   python -c "import pandas as pd; pd.read_parquet('DATA/processed/technical/market_breadth/market_breadth_daily.parquet')"
   ```

---

## 9. Success Criteria

- [ ] Single page with 4 functional tabs
- [ ] Market breadth chart shows MA20/50/100 lines with VN-Index overlay
- [ ] RRG chart renders sectors in correct quadrants
- [ ] Scanner filters work correctly
- [ ] Buy/sell lists show position sizing
- [ ] Page load < 3 seconds
- [ ] No console errors
- [ ] Old technical pages removed/deprecated
