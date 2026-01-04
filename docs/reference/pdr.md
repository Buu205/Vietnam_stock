# Project Overview & PDR

**Project:** Vietnam Stock Dashboard
**Version:** 4.0.0
**Last Updated:** 2025-12-31

---

## 1. Executive Summary

Vietnamese stock market financial data dashboard providing comprehensive analysis for 457 stocks across 19 sectors. Built with Streamlit frontend and Python data processing pipelines.

### Key Capabilities
- **Fundamental Analysis** - Company, Bank, Insurance, Security financial metrics (4 entity types)
- **Technical Analysis** - OHLCV, 15+ TA indicators (MA, RSI, MACD, Bollinger, ATR, ADX), market regime detection
- **Valuation Metrics** - PE, PB, PS, EV/EBITDA (TTM & Forward) with historical percentiles
- **Sector Analysis** - FA+TA scoring with Buy/Sell/Hold signals, sector breadth, money flow
- **BSC Forecast** - Analyst forecasts for 93 stocks with target prices
- **RS Rating** - IBD-style Relative Strength Rating (1-99 scale)
- **Pattern Detection** - Candlestick pattern scoring with win rates & context confirmation

---

## 2. Target Users

| User Type | Primary Use Case |
|-----------|------------------|
| Retail Investors | Stock screening, valuation comparison, pattern alerts |
| Financial Analysts | Sector analysis, fundamental research, regime detection |
| Portfolio Managers | Sector rotation, money flow tracking, RS rating |
| Quant Developers | Data pipeline via MCP API (30 tools), TA indicators |

---

## 3. Technology Stack

### Frontend
- **Streamlit** 1.36+ (multi-page navigation with st.navigation)
- **Plotly** (interactive charts - candlestick, OHLC, heatmap, RRG)
- **Pydantic** (data validation with BaseModels)
- **Crypto Terminal Glassmorphism Theme** (dark mode, OLED-optimized)

### Backend/Processing
- **Python** 3.13 (system installation, no virtualenv)
- **Pandas/NumPy** (data manipulation, 89K+ TA records)
- **TA-Lib** (technical indicators - 15+ indicators)
- **Parquet** (data storage, 789K+ valuation records)

### Data Sources
| Source | Data Type |
|--------|-----------|
| VNStock | OHLCV, market cap, fundamental data |
| WiChart | Exchange rates (USD/VND), commodities (gold, oil, steel) |
| Simplize | Vietnamese economic data (CPI, GDP, interest rates) |
| BSC Research | Analyst forecasts (93 stocks, 2025-2026 targets) |
| Fireant | News data, events |

### Deployment
- **Streamlit Cloud** (production: vietnamstock.streamlit.app)
- **GitHub** (source control, data storage)

---

## 4. Project Metrics

| Metric | Value |
|--------|-------|
| Total Tickers | 457 |
| Sectors | 19 (ICB L2 Vietnamese) |
| Entity Types | 4 (COMPANY, BANK, INSURANCE, SECURITY) |
| Financial Metrics | 2,099 mapped (Vietnamese to English) |
| Calculated Formulas | 40+ (roe, gross_margin, yoy_growth, etc.) |
| Python Files | 223 (110 PROCESSORS + 113 WEBAPP) |
| Data Storage | ~500 MB (Parquet files) |
| MCP Tools | 30 (ticker, fundamental, technical, valuation, forecast, macro) |
| Daily Pipeline Steps | 6 (OHLCV, TA, Alerts, Valuation, Sector, Regime) |

---

## 5. Feature Roadmap

### Completed (v4.0.0)
- [x] **Data Mapping Registry** (v1.0.0) - Zero-hardcoded-paths design with YAML config (data_sources, services, pipelines, dashboards)
- [x] Registry system (MetricRegistry: 2,099 metrics, SectorRegistry: 457 tickers, SchemaRegistry)
- [x] Financial calculators (4 entity types with 56-59 columns output)
- [x] Technical indicators pipeline (15+ TA-Lib indicators)
- [x] Valuation calculators (PE/PB/PS/EV-EBITDA, VN-Index, Sector)
- [x] Daily update pipelines (6-step orchestration)
- [x] BSC forecast integration (93 stocks)
- [x] MCP Server (30 tools, FastMCP)
- [x] Session state management (CRITICAL for page stability)
- [x] Crypto Terminal Glassmorphism theme
- [x] Market regime detection (5 regimes: BUBBLE, EUPHORIA, NEUTRAL, FEAR, BOTTOM)
- [x] RS Rating (IBD-style, 1-99 percentile rank)
- [x] Candlestick pattern scoring (3-metric system: win_rate, context_score, composite_score)
- [x] Sector breadth analysis (4 MA periods: 20/50/100/200)
- [x] Money flow analysis (CMF, MFI, OBV, AD, VPT)
- [x] Sector money flow (1D, 1W, 1M aggregations)

### In Progress
- [ ] Path migration to v4.0.0 canonical structure (95% files using wrong paths)
- [ ] FA+TA Sector Analysis orchestration layer
- [ ] Unified sector dashboard

### Planned
- [ ] Configuration UI for FA/TA weights
- [ ] Real-time data updates (WebSocket)
- [ ] Alert notifications (email/webhook)
- [ ] Mobile-responsive design optimization

---

## 6. Data Coverage

### Fundamental Data
| Entity | Tickers | Records | Key Metrics |
|--------|---------|---------|-------------|
| Company | 1,633 | 37,145 | ROE, ROA, EPS, margins, growth |
| Bank | 46 | 1,033 | NIM, CIR, NPL, LDR, CAR, CASA |
| Insurance | 18 | 418 | Combined ratio, claims ratio |
| Security | 146 | 2,811 | Brokerage revenue, commission |

### Valuation Data
| Metric | Records | Formula |
|--------|---------|---------|
| PE TTM | 789,611 | Market Cap / TTM Earnings |
| PB TTM | 789,611 | Market Cap / Book Value |
| PS TTM | 789,611 | Market Cap / TTM Revenue |
| EV/EBITDA | 789,611 | Enterprise Value / EBITDA |
| VN-Index PE | 60 days | Market-cap weighted aggregation |
| Sector PE/PB | 19 sectors | Sector aggregation |

### Technical Data
- **OHLCV:** 89,805 records (458 symbols, 200-session indicators)
- **Indicators:** SMA (20/50/100/200), EMA (20/50), RSI (14), MACD (12/26/9), Bollinger Bands (20/2), ATR (14), ADX (14), Stochastic (14/3/3), CCI (20)
- **Alerts:** MA crossover (4 periods), volume spike (multi-factor), breakout (20-day high/low), candlestick patterns (11 patterns with 3-metric scoring)
- **Market Regime:** 5 regimes with multi-factor scoring (valuation, breadth, volume, volatility, momentum)
- **Money Flow:** CMF, MFI, OBV, AD, VPT at individual & sector level
- **RS Rating:** IBD-style percentile (1-99) with 4-period weighting (3M: 40%, 6M: 20%, 9M: 20%, 12M: 20%)

---

## 6A. Registry Architecture (v1.0.0)

### Data Mapping Registry - Zero-Hardcoded-Paths Design

**Location:** `config/data_mapping/`

**Core Components:**
1. **entities.py** - Pure dataclasses: DataSource, PipelineOutput, DashboardConfig, ServiceBinding
2. **registry.py** - Singleton DataMappingRegistry with path/schema/dependency lookups
3. **resolver.py** - PathResolver (validation), DependencyResolver (impact analysis)
4. **validator.py** - SchemaValidator, HealthChecker for data quality
5. **configs/** - YAML files: data_sources, services, pipelines, dashboards

**Key Benefits:**
- Single source of truth for all data mappings (no hardcoded paths)
- Automatic schema validation on data load
- Dependency tracking for impact analysis (what breaks when source changes)
- Services (BankService, CompanyService, etc.) extend BaseService for automatic registry integration
- Config-driven extensibility via YAML

**Usage Patterns:**
```python
# Simple lookup
from config.data_mapping import get_data_path
path = get_data_path("bank_metrics")

# Full registry + impact analysis
from config.data_mapping import get_registry, DependencyResolver
registry = get_registry()
impact = DependencyResolver().get_impact_chain("ohlcv_raw")
```

---

## 7. Dashboard Pages (8 Pages)

| Page | Description | Key Features |
|------|-------------|--------------|
| Company Analysis | Non-financial company metrics | Charts, Tables (Income/Balance/CashFlow), Quarterly/Yearly |
| Bank Analysis | Bank-specific ratios | 27 banks, 5 metric categories (Size/Income/Growth/Quality/Efficiency) |
| Security Analysis | Brokerage company analysis | 18 securities, brokerage metrics |
| Sector Overview | FA+TA scoring by sector | VN-Index valuation, sector comparison, individual stock comparison |
| Valuation | PE/PB/EV historical | Historical percentiles, mean/std, z-score, status classification |
| Technical | 3 tabs: Market Overview, Sector Rotation, Stock Scanner | Regime detection, RRG charts, pattern scanner, RS heatmap |
| FX & Commodities | Macro & commodity data | Gold, oil, steel, rubber, USD/VND, bond yields, deposit/lending rates |
| BSC Forecast | Forward PE/PB 2025-2026 | Individual forecasts, sector breakdown, 9M analysis, target prices |

---

## 8. Success Criteria

### Performance
- Dashboard load time < 3 seconds
- Daily update pipeline < 2 minutes (6 steps)
- Data refresh lag < 1 trading day

### Data Quality
- 100% ticker coverage in registries (457 tickers)
- < 5% missing fundamental data
- Valuation metrics match external sources (BSC, Vietstock)

### User Experience
- Intuitive navigation (8 pages, multi-tab layouts)
- Session state persistence (prevents page resets)
- Interactive charts (Plotly, candlestick, heatmaps)
- Export to Excel/CSV

---

## 9. Constraints & Dependencies

### Technical Constraints
- Python 3.13 (system installation, no virtualenv)
- Global vnstock_data package
- TA-Lib requires system installation (brew install ta-lib)

### Data Dependencies
- BSC Excel file for forecast updates (manual process)
- VNStock API availability (rate limits: 60 req/min)
- WiChart/Simplize API rate limits

### Deployment
- Streamlit Cloud free tier limits (1GB RAM, 800MB CPU)
- Data files committed to repo (< 100 MB each)
- Session state size constraints

---

## 10. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| API rate limiting | Caching (@st.cache_data with TTL), retry with exponential backoff |
| Data quality issues | Validators at input/output (Pydantic models, data_validator.py) |
| Large file sizes | Parquet compression (snappy), chunked storage |
| Breaking changes | Registry versioning (metric_registry.json, sector_industry_registry.json) |
| Session state resets | Centralized init_page_state() for all pages |
| Widget interactions | Tab state persistence (0-based indices) |

---

## Related Documents

- [System Architecture](system-architecture.md) - Data flow, component interactions
- [Codebase Summary](codebase-summary.md) - Module structure, file inventory
- [Code Standards](code-standards.md) - Naming conventions, patterns
- [CLAUDE.md](../CLAUDE.md) - AI/Developer guidelines (CRITICAL)
