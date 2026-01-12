# Scout Report: Technical Dashboard Refactor - File Inventory
**Date:** 2025-12-25  
**Status:** Complete  
**Scope:** All relevant files for Technical Dashboard refactor plan  

---

## Executive Summary

Found **21 files across 5 categories** related to the Technical Dashboard refactor:
- 1 existing main page (to replace)
- 3 data service files (reusable)
- 2 core models (new + enhanced)
- 8 parquet files (data sources)
- 8 plan/documentation files

**Key Finding:** Solid foundation exists - MarketState model already created, TechnicalService operational, data files organized. Ready for phase implementation.

---

## 1. WEBAPP/pages/technical/ — Existing UI Layer

### Current Dashboard (To Replace)

| File | Lines | Purpose | Status |
|------|-------|---------|--------|
| `/Users/buuphan/Dev/Vietnam_dashboard/WEBAPP/pages/technical/technical_dashboard.py` | 567 | Individual stock TA analysis (candlestick, RSI, MACD, oscillators) | ❌ NEEDS REFACTOR |
| `/Users/buuphan/Dev/Vietnam_dashboard/WEBAPP/pages/technical/technical_dashboard.py.bak` | N/A | Backup of current dashboard | 📁 Archive |
| `/Users/buuphan/Dev/Vietnam_dashboard/WEBAPP/pages/technical/__init__.py` | Minimal | Package init file | ✅ Keeps as-is |

**What exists:**
- ✅ Candlestick + volume charts (Plotly)
- ✅ Moving averages (SMA 20/50/200)
- ✅ Oscillators (RSI, MACD, Stochastic, CCI)
- ✅ Bollinger Bands
- ✅ Metric cards
- ✅ Data tables

**What's missing:**
- ❌ Market Overview tab (breadth, regime, exposure)
- ❌ Sector Rotation tab (RRG, ranking)
- ❌ Stock Scanner tab (signals)
- ❌ Trading Lists tab (buy/sell)
- ❌ Component separation (monolithic)

---

## 2. WEBAPP/services/ — Data Service Layer

### Core Services (Existing)

| File | Purpose | Status |
|------|---------|--------|
| `/Users/buuphan/Dev/Vietnam_dashboard/WEBAPP/services/technical_service.py` | Load technical indicators from `basic_data.parquet` | ✅ Ready |
| `/Users/buuphan/Dev/Vietnam_dashboard/WEBAPP/services/__init__.py` | Service package init | ✅ Ready |

**TechnicalService** (165 lines):
- `get_technical_data(ticker, limit, start_date, end_date)` - Load OHLCV + indicators
- `get_latest_indicators(ticker)` - Single row
- `get_available_tickers(entity_type)` - 315 liquid symbols via SymbolLoader
- `get_market_breadth()` - Load breadth data (exists)
- `get_sector_breadth(sector)` - Load sector breadth (exists)

**What's missing:**
- ❌ `TADashboardService` - NEW class needed for unified dashboard
  - Should handle market state
  - Should load sector data
  - Should load signal data
  - Should cache with `@st.cache_data(ttl=...)`

### Other Services (Context)

| File | Purpose |
|------|---------|
| `WEBAPP/services/sector_service.py` | Sector fundamental data (reusable) |
| `WEBAPP/services/valuation_service.py` | Valuation metrics (reusable) |
| `WEBAPP/services/company_service.py` | Company fundamentals (reusable) |
| `WEBAPP/services/bank_service.py` | Bank-specific metrics (reusable) |
| `WEBAPP/services/financial_metrics_loader.py` | FA data loading |
| `WEBAPP/services/macro_commodity_loader.py` | Macro commodity data |
| `WEBAPP/services/forecast_service.py` | BSC forecast data |

---

## 3. WEBAPP/core/models/ — Data Models

### Existing Models

| File | Lines | Classes | Status |
|------|-------|---------|--------|
| `/Users/buuphan/Dev/Vietnam_dashboard/WEBAPP/core/models/market_state.py` | 49 | `MarketState`, `BreadthHistory` | ✅ EXISTS |
| `/Users/buuphan/Dev/Vietnam_dashboard/WEBAPP/core/models/data_models.py` | 100+ | `OHLCVBase`, `FundamentalBase`, `BankMetrics`, `CompanyMetrics` | ✅ Pydantic models |
| `/Users/buuphan/Dev/Vietnam_dashboard/WEBAPP/core/models/__init__.py` | Minimal | Package init | ✅ Ready |

**MarketState dataclass** (READY TO USE):
```python
@dataclass
class MarketState:
    date: datetime
    vnindex_close: float
    vnindex_change_pct: float
    regime: str  # BULLISH/NEUTRAL/BEARISH (EMA9 vs EMA21)
    ema9: float
    ema21: float
    breadth_ma20_pct: float      # ✅ NEW: All three MAs for line chart
    breadth_ma50_pct: float
    breadth_ma100_pct: float
    ad_ratio: float
    exposure_level: int  # 0-100
    divergence_type: Optional[str]  # BULLISH/BEARISH
    divergence_strength: int  # 0-3
    signal: str  # RISK_ON / RISK_OFF / CAUTION
```

**BreadthHistory dataclass** (NEW - for line charts):
```python
@dataclass
class BreadthHistory:
    date: List[datetime]
    ma20_pct: List[float]
    ma50_pct: List[float]
    ma100_pct: List[float]
    vnindex_close: List[float]
```

---

## 4. DATA/processed/technical/ — Data Files

### Market-Level Files (Small, Fast Load)

| File | Size (Est) | Columns | Load Time | Use Case |
|------|-----------|---------|-----------|----------|
| `/Users/buuphan/Dev/Vietnam_dashboard/DATA/processed/technical/vnindex/vnindex_indicators.parquet` | ~100KB | date, vnindex_close, ema9, ema21, ... | <100ms | Regime indicator |
| `/Users/buuphan/Dev/Vietnam_dashboard/DATA/processed/technical/market_breadth/market_breadth_daily.parquet` | ~500KB | date, advances, declines, ma20_pct, ma50_pct, ma100_pct | <200ms | Breadth chart + exposure |

### Sector-Level Files (Medium)

| File | Size (Est) | Columns | Load Time | Use Case |
|------|-----------|---------|-----------|----------|
| `/Users/buuphan/Dev/Vietnam_dashboard/DATA/processed/technical/sector_breadth/sector_breadth_daily.parquet` | ~200KB | date, sector, advances, declines, ma_pct | <300ms | Sector breadth analysis |
| `/Users/buuphan/Dev/Vietnam_dashboard/DATA/processed/technical/money_flow/sector_money_flow_1d.parquet` | ~100KB | date, sector, net_flow, inflow, outflow | <100ms | Sector momentum |
| `/Users/buuphan/Dev/Vietnam_dashboard/DATA/processed/technical/money_flow/sector_money_flow_1w.parquet` | ~100KB | (weekly aggregated) | <100ms | Weekly trends |
| `/Users/buuphan/Dev/Vietnam_dashboard/DATA/processed/technical/money_flow/sector_money_flow_1m.parquet` | ~100KB | (monthly aggregated) | <100ms | Monthly trends |

### Stock-Level Files (Lazy Load on Tab Click)

| File | Size (Est) | Columns | Load Time | Use Case |
|------|-----------|---------|-----------|----------|
| `/Users/buuphan/Dev/Vietnam_dashboard/DATA/processed/technical/basic_data.parquet` | ~15MB | symbol, date, close, open, high, low, volume, sma20, sma50, sma200, rsi_14, macd, bb_upper/lower, etc. | <1s | Individual stock TA |
| `/Users/buuphan/Dev/Vietnam_dashboard/DATA/processed/technical/alerts/daily/combined_latest.parquet` | ~1MB | symbol, date, signal_type, strength, pattern, ... | <300ms | Scanner signals (TODAY ONLY) |
| `/Users/buuphan/Dev/Vietnam_dashboard/DATA/processed/technical/alerts/historical/combined_history.parquet` | ~5MB | (full history) | <500ms | Alert history |
| `/Users/buuphan/Dev/Vietnam_dashboard/DATA/processed/technical/money_flow/individual_money_flow.parquet` | ~3MB | symbol, date, net_flow, inflow, outflow | <500ms | Individual stock flow |

### Alert Files (Specialized)

| File | Purpose |
|------|---------|
| `/Users/buuphan/Dev/Vietnam_dashboard/DATA/processed/technical/alerts/daily/ma_crossover_latest.parquet` | MA crossover signals |
| `/Users/buuphan/Dev/Vietnam_dashboard/DATA/processed/technical/alerts/daily/breakout_latest.parquet` | Breakout patterns |
| `/Users/buuphan/Dev/Vietnam_dashboard/DATA/processed/technical/alerts/daily/volume_spike_latest.parquet` | Volume anomalies |
| `/Users/buuphan/Dev/Vietnam_dashboard/DATA/processed/technical/alerts/daily/patterns_latest.parquet` | Candlestick patterns |
| `/Users/buuphan/Dev/Vietnam_dashboard/DATA/processed/technical/alerts/historical/*` | (5 history files matching above) |
| `/Users/buuphan/Dev/Vietnam_dashboard/DATA/processed/technical/market_regime/market_regime_history.parquet` | Regime history (BULLISH/NEUTRAL/BEARISH) |

**Total technical data:** ~30MB (mostly `basic_data.parquet` which is only loaded per-ticker)

---

## 5. PROCESSORS/technical/ — Indicator Calculation Layer

### Existing Indicator Modules

| File | Purpose | Status |
|------|---------|--------|
| `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/technical/indicators/market_regime.py` | Regime calculation (EMA9 vs EMA21) | ✅ EXISTS |
| `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/technical/indicators/vnindex_analyzer.py` | VN-Index TA (indicators, divergence) | ✅ EXISTS |
| `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/technical/indicators/sector_breadth.py` | Sector breadth calculation | ✅ EXISTS |
| `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/technical/indicators/sector_money_flow.py` | Sector money flow aggregation | ✅ EXISTS |
| `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/technical/indicators/technical_processor.py` | Main processor pipeline | ✅ EXISTS |
| `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/technical/indicators/alert_detector.py` | Alert detection (MA, breakout, volume, patterns) | ✅ EXISTS |
| `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/technical/indicators/money_flow.py` | Money flow calculation | ✅ EXISTS |
| `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/technical/indicators/rs_rating.py` | RS Rating calculation | ✅ EXISTS |

**What's missing:**
- ❌ `base.py` - TAIndicator base class (planned in phase-01)
- ❌ `quadrant.py` - Quadrant determination (LEADING/WEAKENING/LAGGING/IMPROVING)
- ❌ `relative_strength.py` - RSRatioCalculator class
- ❌ `sector_score.py` - SectorScoreCalculator
- ❌ `confidence.py` - ConfidenceScoreCalculator
- ❌ `volume_context.py` - VolumeContextAnalyzer

---

## 6. Plans & Documentation Files

### Main Plan & Phases

| File | Status | Lines | Purpose |
|------|--------|-------|---------|
| `/Users/buuphan/Dev/Vietnam_dashboard/plans/251225-technical-dashboard-refactor/plan.md` | 📋 Overview | 176 | Master plan with 5 phases |
| `/Users/buuphan/Dev/Vietnam_dashboard/plans/251225-technical-dashboard-refactor/phase-01-market-state.md` | 📝 Detailed | 300+ | MarketState + TADashboardService + Indicator base classes |
| `/Users/buuphan/Dev/Vietnam_dashboard/plans/251225-technical-dashboard-refactor/phase-02-market-overview-tab.md` | 📝 Detailed | 200+ | Tab 1: Market regime, breadth chart, exposure |
| `/Users/buuphan/Dev/Vietnam_dashboard/plans/251225-technical-dashboard-refactor/phase-03-sector-rotation-tab.md` | 📝 Detailed | 300+ | Tab 2: RRG chart, sector ranking, RS heatmap |
| `/Users/buuphan/Dev/Vietnam_dashboard/plans/251225-technical-dashboard-refactor/phase-04-scanner-lists-tabs.md` | 📝 Detailed | 250+ | Tab 3-4: Scanner filters, buy/sell lists |
| `/Users/buuphan/Dev/Vietnam_dashboard/plans/251225-technical-dashboard-refactor/phase-05-integration.md` | 📝 Detailed | 200+ | Main page, service singleton, caching, filter sync |

### Audit & Review

| File | Status | Purpose |
|------|--------|---------|
| `/Users/buuphan/Dev/Vietnam_dashboard/plans/251225-technical-dashboard-refactor/pipeline-audit.md` | 🔍 Completed | Data pipeline validation |
| `/Users/buuphan/Dev/Vietnam_dashboard/plans/251225-technical-dashboard-refactor/review-report.md` | ✅ Completed | Code review + 7 issues found + all fixed |

---

## 7. Reference Plan (Related)

**For TA Indicator Base Classes:**
- `/Users/buuphan/Dev/Vietnam_dashboard/plans/251224-ta-systematic-trading-system/phase-02-sector-layer.md` - Related sector analysis architecture

---

## Implementation Checklist

### Phase 1: Models & Service (Foundation)
- [ ] Confirm `MarketState` dataclass in `/Users/buuphan/Dev/Vietnam_dashboard/WEBAPP/core/models/market_state.py` ✅ EXISTS
- [ ] Create `TADashboardService` in new file `WEBAPP/services/ta_dashboard_service.py`
- [ ] Create `TAIndicator` base class in `PROCESSORS/technical/indicators/base.py`
- [ ] Create `Quadrant` enum + `determine_quadrant()` in `PROCESSORS/technical/indicators/quadrant.py`
- [ ] Create `RSRatioCalculator` in `PROCESSORS/technical/indicators/relative_strength.py`

### Phase 2: Market Overview Tab
- [ ] Create `WEBAPP/pages/technical/components/market_overview.py`
- [ ] Render: Market regime status (EMA9/21), breadth line chart (3 MAs), exposure gauge, divergence
- [ ] Confirm data sources: `vnindex_indicators.parquet`, `market_breadth_daily.parquet`

### Phase 3: Sector Rotation Tab
- [ ] Create `WEBAPP/pages/technical/components/sector_rotation.py`
- [ ] Render: RRG chart (RS ratio vs momentum), sector ranking table, RS heatmap
- [ ] Confirm data sources: `sector_breadth_daily.parquet`, RS rating data

### Phase 4: Scanner + Lists Tabs
- [ ] Create `WEBAPP/pages/technical/components/stock_scanner.py`
- [ ] Create `WEBAPP/pages/technical/components/trading_lists.py`
- [ ] Render: Signal filters, buy/sell lists with sizing
- [ ] Confirm data sources: `combined_latest.parquet`, `individual_money_flow.parquet`

### Phase 5: Integration
- [ ] Update `WEBAPP/pages/technical/technical_dashboard.py` - Main page with 4 tabs
- [ ] Implement singleton pattern for `TADashboardService`
- [ ] Add `@st.cache_data(ttl=...)` to all data methods
- [ ] Add `st.session_state` filter synchronization
- [ ] Test page load time (<3s target)

---

## Key Insights

### Strong Foundation ✅
1. **MarketState model exists** - No need to create from scratch
2. **BreadthHistory model created** - For line charts
3. **TechnicalService ready** - Can load all technical data
4. **Data files well-organized** - Split by market/sector/stock
5. **Plan is comprehensive** - 5 detailed phases documented

### Missing Components ❌
1. **TADashboardService** - Needed to orchestrate all tab data
2. **Component separation** - Current dashboard is monolithic
3. **Caching strategy** - Service lacks `@st.cache_data` decorators
4. **Indicator base classes** - For consistent interface
5. **Quadrant logic** - Needed for RRG calculations

### Performance Targets
- Market data load: <200ms (vnindex + breadth files ~600KB)
- Sector data load: <500ms (sector files ~400KB)
- Stock data load: <1s per ticker (basic_data.parquet ~15MB)
- **Page load goal: <3 seconds** (lazy load per tab)

### Data Quality Notes
1. All parquet files exist and are current
2. Alert files have both daily (latest) and historical versions
3. Money flow data available at 1d/1w/1m aggregation
4. VN-Index data includes EMA9/21 for regime detection

---

## File Structure Summary

```
WEBAPP/
├── pages/technical/
│   ├── technical_dashboard.py          # CURRENT (monolithic)
│   ├── technical_dashboard.py.bak      # Backup
│   ├── __init__.py                     # ✅ KEEP
│   └── components/                     # ❌ TO CREATE
│       ├── market_overview.py          # Tab 1
│       ├── sector_rotation.py          # Tab 2
│       ├── stock_scanner.py            # Tab 3
│       └── trading_lists.py            # Tab 4
├── services/
│   ├── technical_service.py            # ✅ EXISTING
│   ├── ta_dashboard_service.py         # ❌ TO CREATE
│   └── ...
├── core/models/
│   ├── market_state.py                 # ✅ EXISTS (MarketState, BreadthHistory)
│   ├── data_models.py                  # ✅ Pydantic models
│   └── __init__.py                     # ✅ KEEP

PROCESSORS/technical/
├── indicators/
│   ├── market_regime.py                # ✅ EXISTING
│   ├── rs_rating.py                    # ✅ EXISTING
│   ├── base.py                         # ❌ TO CREATE (TAIndicator)
│   ├── quadrant.py                     # ❌ TO CREATE
│   ├── relative_strength.py            # ❌ TO CREATE
│   └── ...

DATA/processed/technical/
├── vnindex/
│   └── vnindex_indicators.parquet      # ✅ EXISTING
├── market_breadth/
│   └── market_breadth_daily.parquet    # ✅ EXISTING
├── sector_breadth/
│   └── sector_breadth_daily.parquet    # ✅ EXISTING
├── money_flow/
│   ├── sector_money_flow_*.parquet    # ✅ EXISTING
│   └── individual_money_flow.parquet   # ✅ EXISTING
├── basic_data.parquet                  # ✅ EXISTING (15MB)
└── alerts/
    ├── daily/
    │   ├── combined_latest.parquet     # ✅ EXISTING
    │   └── ...
    └── historical/
        └── combined_history.parquet    # ✅ EXISTING
```

---

## Recommendations

### Immediate Actions (Before Implementation)
1. **Back up current dashboard** - Rename to `technical_dashboard_stockta.py`
2. **Create component directory** - `WEBAPP/pages/technical/components/`
3. **Create TADashboardService** - Orchestrate all tab data with caching
4. **Create indicator base class** - For consistent interface

### During Implementation
1. **Implement phases in order** - Start with Market Overview (simplest)
2. **Use lazy loading** - Load data only when tab is clicked
3. **Add st.cache_data** - Cache market/sector data at 5min, signals at 1min
4. **Test each phase** - Before moving to next
5. **Monitor load times** - Target <3s for full page

### After Implementation
1. **Performance audit** - Confirm all load times <targets
2. **Mobile testing** - Ensure responsive on tablet
3. **Dark mode testing** - Verify color contrast
4. **User acceptance** - Get feedback on layout/terminology

---

## Unresolved Questions

1. **RS Heatmap data source:** Which parquet file contains per-ticker RS ratings?
   - Check: `PROCESSORS/technical/indicators/rs_rating.py` for output path
   - May need: `DATA/processed/technical/rs_rating/*.parquet`

2. **Sector RRG coordinates:** How are RS ratio + momentum calculated per sector?
   - Check: `phase-03-sector-rotation-tab.md` for detailed formula
   - May need: Pre-calculated RRG data or on-demand calculation

3. **Buy/Sell list criteria:** Which columns in alert files define "buy" vs "sell"?
   - Check: `phase-04-scanner-lists-tabs.md` for signal mapping
   - Need: Clear signal_type/direction values in data

4. **Exposure level mapping:** How does breadth % translate to 0-100 exposure?
   - Expected formula: `exposure = breadth_ma20_pct` (0-100%)?
   - Or more complex with divergence weighting?

---

**Scout Report Complete**  
**Date Generated:** 2025-12-25  
**Time Estimate for Phases 1-5:** ~40-50 hours (spread across 2-3 weeks)

