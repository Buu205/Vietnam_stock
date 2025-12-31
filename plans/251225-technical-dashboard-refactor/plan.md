# Technical Dashboard Refactor Plan

**Date:** 2025-12-25
**Updated:** 2025-12-31 (Registry Integration)
**Status:** Ready for Implementation
**Reference:** [TA Systematic Trading System](../251224-ta-systematic-trading-system/plan.md)
**Dependency:** [Data Mapping Registry](../251231-data-mapping-registry/plan.md) ✅ Completed

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
└── __init__.py

# Service layer (centralized - DO NOT create page-specific services)
WEBAPP/services/
└── technical_service.py       # ✅ Already has all methods for 4 tabs
    # Methods available:
    # - get_market_state()      → Tab 1
    # - get_market_breadth()    → Tab 1
    # - get_market_regime()     → Tab 1
    # - get_sector_ranking()    → Tab 2
    # - get_sector_rrg()        → Tab 2
    # - get_money_flow()        → Tab 2
    # - get_rs_rating()         → Tab 3
    # - get_alerts()            → Tab 3
    # - get_buy_list()          → Tab 4
    # - get_sell_list()         → Tab 4
```

> **IMPORTANT:** Use `TechnicalService` from `WEBAPP/services/`.
> DO NOT create `ta_dashboard_service.py` - all methods already exist.

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

### Data Files (Registry-Managed)

All paths are managed via `DataMappingRegistry` in `config/data_mapping/configs/data_sources.yaml`.

| Registry Key | Path | Tab | Status |
|--------------|------|-----|--------|
| `market_state_latest` | `processed/technical/market/market_state_latest.parquet` | 1 | 🔨 Need pipeline |
| `market_breadth` | `processed/technical/market_breadth/market_breadth_daily.parquet` | 1 | ✅ Exists |
| `vnindex_indicators` | `processed/technical/vnindex/vnindex_indicators.parquet` | 1 | ✅ Exists |
| `market_regime` | `processed/technical/market_regime/market_regime_history.parquet` | 1 | ✅ Exists |
| `sector_ranking_latest` | `processed/technical/sector/ranking_latest.parquet` | 2 | 🔨 Need pipeline |
| `sector_rrg_latest` | `processed/technical/sector/rrg_latest.parquet` | 2 | 🔨 Need pipeline |
| `sector_money_flow_1d` | `processed/technical/money_flow/sector_money_flow_1d.parquet` | 2 | ✅ Exists |
| `sector_breadth` | `processed/technical/sector_breadth/sector_breadth_daily.parquet` | 2 | ✅ Exists |
| `stock_rs_rating` | `processed/technical/rs_rating/stock_rs_rating_daily.parquet` | 3 | ✅ Exists |
| `rs_rating_history` | `processed/technical/rs_rating/rs_rating_history_30d.parquet` | 3 | 🔨 Need pipeline |
| `combined_alerts_latest` | `processed/technical/alerts/daily/combined_latest.parquet` | 3 | ✅ Exists |
| `buy_list_latest` | `processed/technical/lists/buy_list_latest.parquet` | 4 | 🔨 Need pipeline |
| `sell_list_latest` | `processed/technical/lists/sell_list_latest.parquet` | 4 | 🔨 Need pipeline |

### Service Usage

```python
from WEBAPP.services import TechnicalService

@st.cache_resource
def get_service():
    return TechnicalService()

# Tab 1: Market Overview
service = get_service()
market_state = service.get_market_state()
breadth = service.get_market_breadth()
regime = service.get_market_regime()

# Tab 2: Sector Rotation
ranking = service.get_sector_ranking()
rrg = service.get_sector_rrg()
money_flow = service.get_money_flow(scope="sector")

# Tab 3: Stock Scanner
rs_data = service.get_rs_rating()
alerts = service.get_alerts(latest_only=True)

# Tab 4: Trading Lists
buy_list = service.get_buy_list()
sell_list = service.get_sell_list()
```

### Load Strategy

| Tab | TechnicalService Methods | Est. Size | Load Time |
|-----|--------------------------|-----------|-----------|
| Market Overview | `get_market_state()`, `get_market_breadth()`, `get_market_regime()` | ~500KB | <200ms |
| Sector Rotation | `get_sector_ranking()`, `get_sector_rrg()`, `get_money_flow()` | ~2MB | <500ms |
| Stock Scanner | `get_rs_rating()`, `get_alerts()` | ~1MB | <300ms |
| Trading Lists | `get_buy_list()`, `get_sell_list()` | ~100KB | <100ms |
