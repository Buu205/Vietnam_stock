# Technical Dashboard Refactor Plan

**Date:** 2025-12-25
**Status:** Ready for Implementation
**Reference:** [TA Systematic Trading System](../251224-ta-systematic-trading-system/plan.md)

---

## 🚨 Development Rules

### Frontend Development
- **MUST use skills:** `ui-ux-pro-max` và `frontend-design-pro` cho tất cả UI/UX work, hay plugin /design
- Follow Streamlit best practices, use `st.cache_data` for data loading
- Components phải responsive, support dark/light mode
- Use Plotly for interactive charts (không dùng matplotlib)

### Data Architecture (Performance Critical)
- **KHÔNG dồn data vào 1 file parquet lớn** - Chẻ nhỏ theo:
  - Temporal: `daily/`, `historical/`, `latest/`
  - Entity: Per-ticker files khi cần (VD: `rs_rating/{symbol}.parquet`)
  - Aggregation level: `market/`, `sector/`, `stock/`
- Target: Mỗi file load < 500ms, total page load < 3s
- Use lazy loading: Chỉ load data khi tab được click

### File Naming
- Parquet files: `snake_case` (VD: `market_breadth_daily.parquet`)
- Python modules: `snake_case` (VD: `sector_rotation.py`)
- Components: Descriptive names (VD: `render_stock_rs_heatmap()`)

### Code Quality
- Follow YAGNI/KISS/DRY principles
- Type hints cho tất cả functions
- Docstrings cho public methods
- Error handling với user-friendly messages

---

## Overview

Consolidate 4 separate pages into 1 unified Technical Dashboard with tabs:
1. Market Overview (regime, breadth, exposure)
2. Sector Rotation (RRG, ranking)
3. Stock Scanner (signals)
4. Trading Lists (buy/sell with sizing)

---

## Current State

```
WEBAPP/pages/technical/
├── technical_dashboard.py  # EXISTS - Individual stock TA (REPLACE)
└── __init__.py
```

**Problem:** Current dashboard only shows individual stock analysis, missing market/sector/signals.

---

## Target State

```
WEBAPP/pages/technical/
├── technical_dashboard.py     # REFACTORED - Unified dashboard with 4 tabs
├── components/
│   ├── market_overview.py     # Tab 1: Market regime, breadth, exposure
│   ├── sector_rotation.py     # Tab 2: RRG chart, sector ranking
│   ├── stock_scanner.py       # Tab 3: Signal scanner
│   └── trading_lists.py       # Tab 4: Buy/Sell lists
├── services/
│   └── ta_dashboard_service.py  # Data service for all tabs
└── __init__.py
```

---

## Phases

| Phase | Name | Status | File |
|-------|------|--------|------|
| 1 | MarketState dataclass + service | ✅ Documented | [phase-01-market-state.md](phase-01-market-state.md) |
| 2 | Tab 1: Market Overview | ✅ Documented | [phase-02-market-overview-tab.md](phase-02-market-overview-tab.md) |
| 3 | Tab 2: Sector Rotation | ✅ Documented | [phase-03-sector-rotation-tab.md](phase-03-sector-rotation-tab.md) |
| 4 | Tab 3-4: Scanner + Lists | ✅ Documented | [phase-04-scanner-lists-tabs.md](phase-04-scanner-lists-tabs.md) |
| 5 | Integration + Cleanup | ✅ Documented | [phase-05-integration.md](phase-05-integration.md) |

---

## Key Changes

### MarketState Dataclass (Updated)

```python
@dataclass
class MarketState:
    date: datetime
    vnindex_close: float
    vnindex_change_pct: float
    regime: str  # BULLISH/NEUTRAL/BEARISH
    ema9: float
    ema21: float

    # Breadth - ALL THREE MAs
    breadth_ma20_pct: float
    breadth_ma50_pct: float
    breadth_ma100_pct: float  # ADDED

    ad_ratio: float
    exposure_level: int  # 0-100
    divergence_type: Optional[str]
    divergence_strength: int
    signal: str  # RISK_ON / RISK_OFF / CAUTION
```

### Breadth Line Chart Requirements

- 3 lines: MA20 (blue), MA50 (orange), MA100 (green)
- VN-Index overlay (secondary Y-axis)
- Overbought zone (80-100%) - red shade
- Oversold zone (0-20%) - green shade
- Historical: 6 months default

---

## Success Criteria

- [ ] Single page with 4 functional tabs
- [ ] Market breadth chart shows MA20/50/100 lines
- [ ] RRG chart renders correctly
- [ ] Scanner filters work
- [ ] Buy/sell lists generate correctly
- [ ] Page load < 3 seconds

---

## Dependencies

### Data Files (Optimized Structure)

```
DATA/processed/technical/
├── market/                          # Market-level (load first, small)
│   ├── market_state_latest.parquet  # Single row, current state
│   ├── breadth_daily.parquet        # 180 days for chart
│   └── vnindex_indicators.parquet   # VN-Index data
│
├── sector/                          # Sector-level (medium)
│   ├── ranking_latest.parquet       # Current ranking (19 rows)
│   ├── rrg_latest.parquet           # RRG coordinates (19 rows)
│   ├── money_flow_1d.parquet        # Daily flow (19 rows)
│   └── breadth_daily.parquet        # Sector breadth history
│
├── stock/                           # Stock-level (lazy load)
│   ├── signals/
│   │   └── combined_latest.parquet  # Today's signals only
│   ├── rs_rating/
│   │   ├── latest.parquet           # Current RS (all stocks, 1 day)
│   │   └── history_30d.parquet      # 30-day history for heatmap
│   └── lists/
│       ├── buy_list_latest.parquet  # Top 10 candidates
│       └── sell_list_latest.parquet # Exit signals
│
└── alerts/                          # Alerts (existing)
    └── daily/
        └── combined_latest.parquet
```

### Load Strategy

| Tab | Files Loaded | Est. Size | Load Time |
|-----|--------------|-----------|-----------|
| Market Overview | market/* | ~500KB | <200ms |
| Sector Rotation | sector/*, stock/rs_rating/* | ~2MB | <500ms |
| Stock Scanner | stock/signals/* | ~1MB | <300ms |
| Trading Lists | stock/lists/* | ~100KB | <100ms |
