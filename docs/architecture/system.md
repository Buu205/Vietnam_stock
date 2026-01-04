# System Architecture

**Project:** Vietnam Stock Dashboard
**Architecture Version:** 4.0.0
**Last Updated:** 2025-12-31

---

## 1. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                            │
│                      (Streamlit Cloud)                           │
│                  Crypto Terminal Glassmorphism Theme             │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │
│  │Company  │ │ Bank    │ │ Sector  │ │Valuation│ │Technical│   │
│  │Dashboard│ │Dashboard│ │Overview │ │Dashboard│ │Dashboard│   │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘   │
│  ┌────┴────┐ ┌────┴────┐ ┌────┴────┐ ┌────┴────┐ ┌────┴────┐   │
│  │Security │ │Forecast │ │   FX &   │ │         │ │         │   │
│  │Dashboard│ │Dashboard│ │Commodities│  │         │ │         │   │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘   │
│       └───────────┴──────────┬┴──────────┴───────────┘          │
│                              ▼                                   │
│                    ┌─────────────────┐                          │
│                    │ Service Layer   │                          │
│                    │ (8 services)    │                          │
│                    │ Session State   │                          │
│                    │ (CRITICAL)      │                          │
│                    └────────┬────────┘                          │
└─────────────────────────────┼───────────────────────────────────┘
                              │
┌─────────────────────────────┼───────────────────────────────────┐
│                        DATA LAYER                                │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    DATA/processed/                        │   │
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌──────────┐ │   │
│  │  │fundamental│ │ technical │ │ valuation │ │  sector  │ │   │
│  │  │(4 entities)│ │(TA,alerts)│ │(PE/PB/PS) │ │(FA+TA)   │ │   │
│  │  └───────────┘ └───────────┘ └───────────┘ └──────────┘ │   │
│  │  ┌───────────┐ ┌───────────┐                            │   │
│  │  │  forecast │ │macro/comm.│                            │   │
│  │  │  (BSC)    │ │ (FX,comm) │                            │   │
│  │  └───────────┘ └───────────┘                            │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              ▲                                   │
│                              │                                   │
│                    ┌─────────┴─────────┐                        │
│                    │ PROCESSORS        │                        │
│                    │ (Daily Pipelines) │                        │
│                    │ (110 Python files) │                        │
│                    └─────────┬─────────┘                        │
│                              │                                   │
│  ┌───────────────────────────┼───────────────────────────────┐  │
│  │                    DATA/raw/                               │  │
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐               │  │
│  │  │   ohlcv   │ │fundamental│ │   macro   │               │  │
│  │  │ (457 tkr) │ │  (20 CSV) │ │           │               │  │
│  │  └───────────┘ └───────────┘ └───────────┘               │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ▲
┌─────────────────────────────┼───────────────────────────────────┐
│                     EXTERNAL SOURCES                             │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐      │
│  │ VNStock │    │ WiChart │    │Simplize │    │ Fireant │      │
│  │  (API)  │    │  (API)  │    │  (API)  │    │  (API)  │      │
│  │ OHLCV   │    │FX,Comm  │    │ Macro   │    │  News   │      │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘      │
│  ┌─────────┐    ┌─────────┐                                    │
│  │Vietcap  │    │   BSC   │                                    │
│  │  (API)  │    │ (Excel) │                                    │
│  └─────────┘    └─────────┘                                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Registry System (v4.0.0 Canonical)

```
┌─────────────────────────────────────────────────────────────────┐
│                      REGISTRY LAYER                              │
│                     (config/ directory)                          │
│                     (41 files: 5 Python + 36 JSON)               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌───────────────────┐    ┌───────────────────┐                 │
│  │   MetricRegistry  │    │  SectorRegistry   │                 │
│  │  (metric_lookup)  │    │ (sector_lookup)   │                 │
│  ├───────────────────┤    ├───────────────────┤                 │
│  │ • 2,099 metrics   │    │ • 457 tickers     │                 │
│  │ • VN ↔ EN mapping │    │ • 19 sectors      │                 │
│  │ • Formula registry│    │ • 4 entity types  │                 │
│  │ • Calculated defs │    │ • Peer lookup     │                 │
│  │ • (770 KB JSON)   │    │ • Sector mapping  │                 │
│  └─────────┬─────────┘    └─────────┬─────────┘                 │
│            │                        │                            │
│            └──────────┬─────────────┘                            │
│                       ▼                                          │
│            ┌───────────────────┐                                │
│            │  SchemaRegistry   │                                │
│            │ (schema_registry) │                                │
│            ├───────────────────┤                                │
│            │ • Format prices   │                                │
│            │ • Format %        │                                │
│            │ • Format mcap     │                                │
│            │ • Color schemes   │                                │
│            │ • Chart configs   │                                │
│            └───────────────────┘                                │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │      DataMappingRegistry (v1.0.0 - NEW)                 │   │
│  │          Zero-Hardcoded-Paths Design                    │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │ • 5 Python modules (entities, registry, resolver, etc)  │   │
│  │ • 4 YAML configs (data_sources, services, pipelines)    │   │
│  │ • Single source of truth for all data mappings          │   │
│  │ • Services (BankService, etc.) → BaseService            │   │
│  │ • DependencyResolver: impact analysis (what breaks?)    │   │
│  │ • SchemaValidator: data quality checks                  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                          │                                       │
│                          ▼                                       │
│         ┌─────────────────────────────┐                          │
│         │   Services (BankService,    │                          │
│         │   CompanyService, etc.)     │                          │
│         │   Extend BaseService        │                          │
│         │   Auto registry path lookup │                          │
│         └─────────────────────────────┘                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
         ┌─────────┐    ┌─────────┐    ┌─────────┐
         │ WEBAPP  │    │PROCESSORS│   │MCP_SERVER│
         │(113 files│    │(110 files│   │ (30 tools│
         │services)│    │calculat.)│  │  FastMCP)│
         └─────────┘    └─────────┘    └─────────┘
```

---

## 3. Data Mapping Registry Architecture (v1.0.0)

```
┌─────────────────────────────────────────────────────────────────┐
│                   DATA MAPPING REGISTRY                          │
│              (config/data_mapping/ - 5 modules)                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────┐        │
│  │           YAML Configuration Files                   │        │
│  ├─────────────────────────────────────────────────────┤        │
│  │ • data_sources.yaml (18 sources: bank_metrics, etc)│        │
│  │ • services.yaml (8 services → data sources)         │        │
│  │ • pipelines.yaml (14 pipelines + dependencies)      │        │
│  │ • dashboards.yaml (8 dashboards → sources)          │        │
│  └─────────────────────────────────────────────────────┘        │
│                          │                                       │
│  ┌───────────────────────▼───────────────────────────┐          │
│  │         DataMappingRegistry (Singleton)           │          │
│  │              registry.py                          │          │
│  ├──────────────────────────────────────────────────┤          │
│  │ • Load YAML configs on init                       │          │
│  │ • Lookup methods:                                 │          │
│  │   - get_path(source_name)                         │          │
│  │   - get_sources_for_dashboard()                   │          │
│  │   - get_sources_for_service()                     │          │
│  └──────────────────────────────────────────────────┘          │
│     │                       │                                    │
│     ▼                       ▼                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │PathResolver  │  │DependencyRe- │  │SchemaVali-   │          │
│  │(validation)  │  │solver        │  │dator         │          │
│  │              │  │(impact       │  │(validation)  │          │
│  │Validates     │  │analysis)     │  │              │          │
│  │paths exist   │  │What depends  │  │Validates     │          │
│  │& accessible  │  │on this?      │  │schemas       │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │        Usage Pattern: Zero-Hardcoded-Paths             │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │                                                          │  │
│  │  Simple:  path = get_data_path("bank_metrics")         │  │
│  │                                                          │  │
│  │  Full:    registry = get_registry()                     │  │
│  │           sources = registry.get_sources_for_dashboard()│  │
│  │                                                          │  │
│  │  Analysis: resolver = DependencyResolver()             │  │
│  │            impact = resolver.get_impact_chain()        │  │
│  │                                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │     BaseService: Services Extend This For Auto Registry │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │                                                          │  │
│  │  class BankService(BaseService):                        │  │
│  │      DATA_SOURCE = "bank_metrics"  # Just define this  │  │
│  │                                                          │  │
│  │      def get_data(self):                                │  │
│  │          df = self.load_data()  # Uses registry path   │  │
│  │          return df                                      │  │
│  │                                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Data Processing Pipeline (6 Steps)

```
┌─────────────────────────────────────────────────────────────────┐
│                    DAILY UPDATE PIPELINE                         │
│              (PROCESSORS/pipelines/run_all_daily_updates.py)     │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ 1. OHLCV      │    │ 2. Technical  │    │ 3. Macro      │
│    Update     │    │    Analysis   │    │    Commodity  │
├───────────────┤    │ (9 steps)     │    ├───────────────┤
│ VNStock API   │    │ ├─VN-Index(500)│   │ WiChart API   │
│      ↓        │    │ ├─TA Ind(200) │   │ Simplize API  │
│ OHLCV_mktcap  │    │ ├─Alerts      │   │      ↓        │
│   .parquet    │    │ ├─Money Flow  │   │ macro_data    │
│ (457 tickers) │    │ ├─Breadth     │   │   .parquet    │
│               │    │ ├─Regime      │   │ (gold,oil,FX) │
│               │    │ ├─RS Rating   │   └───────────────┘
│               │    │ └─Sect Flow   │
│               │    └───────────────┘
│               │    │ basic_data    │
│               │    │ alerts/       │
│               │    │ breadth/      │
│               │    │ regime/       │
│               │    │ rs_rating/    │
│               └───────────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              ▼
        ┌─────────────────────────────────────────┐
        │            4. Valuation                  │
        ├─────────────────────────────────────────┤
        │ ┌─────────┐ ┌─────────┐ ┌─────────┐    │
        │ │   PE    │ │   PB    │ │EV/EBITDA│    │
        │ │Calculator│ │Calculator│ │Calculator│   │
        │ │(789K rec)│ │(789K rec)│ │(789K rec)│   │
        │ └────┬────┘ └────┬────┘ └────┬────┘    │
        │      └───────────┼───────────┘          │
        │                  ▼                      │
        │         historical_*.parquet            │
        │         (PE/PB/PS/EV historical)        │
        └─────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │            5. Sector Analysis           │
        ├─────────────────────────────────────────┤
        │                                         │
        │  ┌────────────┐    ┌────────────┐      │
        │  │FA Aggregator│   │TA Aggregator│      │
        │  │(ROE, margins)│ │(PE/PB, momentum)│   │
        │  └─────┬──────┘    └─────┬──────┘      │
        │        ▼                  ▼             │
        │  ┌────────────┐    ┌────────────┐      │
        │  │ FA Scorer  │    │ TA Scorer  │      │
        │  │(40 metrics)│  │(10 metrics)│      │
        │  └─────┬──────┘    └─────┬──────┘      │
        │        └──────────┬──────┘              │
        │                   ▼                     │
        │         ┌────────────────┐             │
        │         │Signal Generator│             │
        │         │FA*0.5 + TA*0.5  │             │
        │         │      ↓          │             │
        │         │ BUY / SELL / HOLD│            │
        │         └─────────────────┘             │
        │                 ▼                       │
        │    sector_combined_scores.parquet       │
        │    (19 sectors × FA+TA scores)          │
        └─────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │            6. Unified Update           │
        │         (Recommended: Single command)   │
        ├─────────────────────────────────────────┤
        │ run_all_daily_updates.py                │
        │ → Runs all 5 steps above                │
        │ → ~2 minutes total                      │
        └─────────────────────────────────────────┘
```

---

## 5. Session State Architecture (CRITICAL)

```
┌─────────────────────────────────────────────────────────────────┐
│                  SESSION STATE MANAGEMENT                        │
│             (WEBAPP/core/session_state.py)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  PURPOSE: Prevent widget interactions from causing page resets   │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │           init_page_state(page_name)                     │    │
│  │   ┌─────────────────────────────────────────────────┐   │    │
│  │   │ 1. Initialize global state (if not exists)       │   │    │
│  │   │    - global_ticker_search                        │   │    │
│  │   │    - quick_search_ticker                         │   │    │
│  │   │    - search_select                               │   │    │
│  │   │                                                   │   │    │
│  │   │ 2. Initialize page-specific state                 │   │    │
│  │   │    - selected_ticker, timeframe, active_tab      │   │    │
│  │   │                                                   │   │    │
│  │   │ 3. Set default values if keys don't exist        │   │    │
│  │   │    - Prevents KeyError on first load             │   │    │
│  │   │                                                   │   │    │
│  │   │ 4. Persist state across widget interactions      │   │    │
│  │   │    - st.session_state[key] = default_value       │   │    │
│  │   └─────────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  USAGE: Call at TOP of EVERY dashboard page                      │
│                                                                  │
│  AVAILABLE PAGES:                                                │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ 'company', 'bank', 'security', 'sector',                 │    │
│  │ 'valuation', 'technical', 'forecast', 'fx_commodities'  │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. Technical Analysis Pipeline (9 Steps)

```
┌─────────────────────────────────────────────────────────────────┐
│              TECHNICAL ANALYSIS PIPELINE (9 Steps)              │
│          (PROCESSORS/pipelines/daily/daily_ta_complete.py)       │
└─────────────────────────────────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────┐
│ Step 1: VN-Index Analysis (500 sessions)│
│ ├─ Indicators: SMA, RSI, MACD, BB     │
│ └─ Output: vnindex_indicators.parquet  │
└───────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────┐
│ Step 2: Technical Indicators (200 sessions)│
│ ├─ 15+ TA-Lib indicators              │
│ │  • SMA: 20, 50, 100, 200            │
│ │  • EMA: 20, 50                      │
│ │  • RSI: 14                          │
│ │  • MACD: 12/26/9                    │
│ │  • Bollinger Bands: 20/2             │
│ │  • ATR: 14                          │
│ │  • ADX: 14                          │
│ │  • Stochastic: 14/3/3               │
│ │  • CCI: 20                          │
│ └─ Output: basic_data.parquet (89K rows)│
└───────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────┐
│ Step 3: Alert Detection               │
│ ├─ MA Crossover (4 periods)           │
│ ├─ Volume Spike (multi-factor)        │
│ ├─ Breakout (20-day high/low)         │
│ └─ Candlestick Patterns (11 patterns) │
│    • 3-metric scoring system:         │
│      - win_rate (50-60%)              │
│      - context_score (0-100)          │
│      - composite_score (-100 to +100) │
│ └─ Output: alerts/daily/*.parquet     │
└───────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────┐
│ Step 4: Money Flow Calculation        │
│ ├─ CMF (Chaikin Money Flow)           │
│ ├─ MFI (Money Flow Index)             │
│ ├─ OBV (On-Balance Volume)            │
│ ├─ AD (Accumulation/Distribution)    │
│ └─ VPT (Volume Price Trend)           │
│ └─ Output: individual_money_flow.parquet│
└───────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────┐
│ Step 5: Sector Money Flow (1D, 1W, 1M)│
│ ├─ Aggregate individual money flow    │
│ ├─ By sector (19 sectors)             │
│ └─ Output: sector_money_flow_*d.parquet│
└───────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────┐
│ Step 6: Market Breadth                │
│ ├─ % stocks above MA20/50/100/200     │
│ ├─ Advance/Decline ratio              │
│ └─ Output: market_breadth_daily.parquet│
└───────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────┐
│ Step 7: Sector Breadth                │
│ ├─ Sector strength score (0-100)      │
│ ├─ Trend classification (5 levels)    │
│ └─ Output: sector_breadth_daily.parquet│
└───────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────┐
│ Step 8: Market Regime Detection       │
│ ├─ 5 regimes: BUBBLE, EUPHORIA,       │
│ │            NEUTRAL, FEAR, BOTTOM    │
│ ├─ Multi-factor scoring:              │
│ │  • Valuation (25%)                  │
│ │  • Breadth (25%)                    │
│ │  • Volume (15%)                     │
│ │  • Volatility (15%)                 │
│ │  • Momentum (20%)                   │
│ └─ Output: market_regime_history.parquet│
└───────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────┐
│ Step 9: RS Rating Calculation         │
│ ├─ IBD-style RS Rating (1-99)         │
│ ├─ 4-period weighting:                │
│ │  • 3M: 40%                         │
│ │  • 6M: 20%                         │
│ │  • 9M: 20%                         │
│ │  • 12M: 20%                        │
│ └─ Output: stock_rs_rating_daily.parquet│
└───────────────────────────────────────┘
```

---

## 7. Fundamental Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                  FUNDAMENTAL DATA PIPELINE                       │
└─────────────────────────────────────────────────────────────────┘

BSC CSV Files (Q3/2025, 20 files)
├── COMPANY_BALANCE_SHEET.csv
├── COMPANY_INCOME.csv
├── BANK_BALANCE_SHEET.csv
├── BANK_INCOME.csv
├── INSURANCE_BALANCE_SHEET.csv
├── INSURANCE_INCOME.csv
├── SECURITY_BALANCE_SHEET.csv
├── SECURITY_INCOME.csv
└── ... (12 more files)
        │
        ▼
┌───────────────────────────────────────┐
│    csv_to_full_parquet.py             │
│    (Long format conversion)           │
├───────────────────────────────────────┤
│ ticker | period | METRIC_CODE | value │
│  VNM   | 2024Q3 | CIS_62      | 2.5T  │
└───────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────┐
│    Entity Calculators (4 types)       │
├───────────────────────────────────────┤
│ ┌─────────────────────────────────┐  │
│ │ CompanyCalculator               │  │
│ │ • 56-59 columns output          │  │
│ │ • 1,633 tickers                 │  │
│ │ • 37,145 records                │  │
│ └─────────────────────────────────┘  │
│ ┌─────────────────────────────────┐  │
│ │ BankCalculator                  │  │
│ │ • 56-59 columns output          │  │
│ │ • 46 banks                      │  │
│ │ • 1,033 records                 │  │
│ └─────────────────────────────────┘  │
│ ┌─────────────────────────────────┐  │
│ │ InsuranceCalculator             │  │
│ │ • 56-59 columns output          │  │
│ │ • 18 insurance                  │  │
│ │ • 418 records                   │  │
│ └─────────────────────────────────┘  │
│ ┌─────────────────────────────────┐  │
│ │ SecurityCalculator              │  │
│ │ • 56-59 columns output          │  │
│ │ • 146 securities                │  │
│ │ • 2,811 records                 │  │
│ └─────────────────────────────────┘  │
│              │                        │
│              ▼                        │
│ ┌─────────────────────────────────┐  │
│ │     FormulaRegistry             │  │
│ │ • 40+ pure functions            │  │
│ │ • roe(), gross_margin(), yoy()  │  │
│ │ • No side effects               │  │
│ └─────────────────────────────────┘  │
└───────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────┐
│    DATA/processed/fundamental/        │
├───────────────────────────────────────┤
│ company/company_financial_metrics.parquet │  (37,145 records)
│ bank/bank_financial_metrics.parquet       │  (1,033 records)
│ insurance/insurance_financial_metrics.parquet │ (418 records)
│ security/security_financial_metrics.parquet   │ (2,811 records)
└───────────────────────────────────────┘
```

---

## 8. Valuation Calculation

```
┌─────────────────────────────────────────────────────────────────┐
│                   VALUATION CALCULATION                          │
└─────────────────────────────────────────────────────────────────┘

Inputs:
├── OHLCV_mktcap.parquet (market_cap, 457 tickers)
└── fundamental/*_financial_metrics.parquet (ttm_earnings, equity)
        │
        ▼
┌───────────────────────────────────────┐
│    Valuation Calculators              │
├───────────────────────────────────────┤
│                                       │
│ PE = Market Cap / TTM Earnings        │
│ PB = Market Cap / Total Equity        │
│ PS = Market Cap / TTM Revenue         │
│ EV/EBITDA = Enterprise Value / EBITDA │
│                                       │
│ VNINDEX PE = Sum(MCap) / Sum(Earnings)│
│ Sector PE = Sector Sum(MCap) / Sum(E) │
│                                       │
│ Historical Data (2018-2025)           │
│ • 789,611 records per metric          │
│ • Percentiles, mean, std, z-score    │
│ • Status classification               │
│                                       │
└───────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────┐
│    DATA/processed/valuation/          │
├───────────────────────────────────────┤
│ pe/historical/historical_pe.parquet   │  (789,611 records)
│ pb/historical/historical_pb.parquet   │  (789,611 records)
│ ps/historical/historical_ps.parquet   │  (789,611 records)
│ ev_ebitda/historical/historical_ev_ebitda.parquet │ (789,611 records)
│ vnindex/vnindex_valuation_refined.parquet │  (60 days)
│ sector_pe/sector_pe_pb_data.parquet   │  (19 sectors)
└───────────────────────────────────────┘
```

---

## 9. Sector Analysis

```
┌─────────────────────────────────────────────────────────────────┐
│                    SECTOR ANALYSIS PIPELINE                      │
│                    (SectorProcessor)                             │
└─────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 1: Load Registries                                          │
│ ┌───────────────────┐  ┌───────────────────┐                    │
│ │  MetricRegistry   │  │  SectorRegistry   │                    │
│ │ (2,099 metrics)   │  │ (457 tickers)     │                    │
│ │ • VN ↔ EN mapping │  │ • 19 sectors      │                    │
│ │ • Formula registry│  │ • 4 entity types  │                    │
│ └───────────────────┘  └───────────────────┘                    │
└─────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 2: FA Aggregation                                           │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ FAAggregator                                                 │ │
│ │ • Load fundamental metrics by entity type                   │ │
│ │ • Map tickers to sectors (457 → 19 sectors)                │ │
│ │ • Calculate sector averages: ROE, ROA, margins, growth      │ │
│ │ • Aggregate by sector: mean, median, weighted avg           │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                              ↓                                   │
│            sector_fundamental_metrics.parquet                    │
│            (19 sectors × 40+ metrics)                           │
└─────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 3: TA Aggregation                                           │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ TAAggregator                                                 │ │
│ │ • Load valuation metrics (PE, PB) from historical            │ │
│ │ • Calculate sector PE/PB (market-cap weighted)              │ │
│ │ • Momentum indicators: RS Rating, MA trend                 │ │
│ │ • Money flow: CMF, MFI by sector                            │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                              ↓                                   │
│            sector_valuation_metrics.parquet                      │
│            (19 sectors × PE, PB, momentum)                     │
└─────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 4: Scoring                                                  │
│ ┌─────────────────────┐  ┌─────────────────────┐               │
│ │     FAScorer        │  │     TAScorer        │               │
│ │ • ROE score (0-100) │  │ • PE score (0-100)  │               │
│ │ • Growth score      │  │ • PB score         │               │
│ │ • Margin score      │  │ • Momentum score    │               │
│ │ • 40 metrics total  │  │ • 10 metrics total  │               │
│ └─────────┬───────────┘  └─────────┬───────────┘               │
│           └──────────────┬─────────┘                            │
│                          ▼                                       │
│              ┌─────────────────────┐                            │
│              │   SignalGenerator   │                            │
│              │ FA*0.5 + TA*0.5     │                            │
│              │      ↓              │                            │
│              │ Combined Score      │                            │
│              │      ↓              │                            │
│              │ BUY / SELL / HOLD   │                            │
│              └─────────────────────┘                            │
└─────────────────────────────────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────┐
│ sector_combined_scores.parquet        │
├───────────────────────────────────────┤
│ sector | fa_score | ta_score | signal │
│ Ngân hàng | 72 | 68 | BUY            │
│ Bất động sản | 45 | 52 | HOLD       │
│ Công nghệ | 85 | 75 | BUY           │
│ ... (19 sectors total)                │
└───────────────────────────────────────┘
```

---

## 10. API Client Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      API CLIENT LAYER                            │
│                    (PROCESSORS/api/)                             │
│                    (5 API clients + unified fetcher)            │
└─────────────────────────────────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────────────────────────────┐
│                     BaseAPIClient                              │
│                    (Abstract Base)                             │
├───────────────────────────────────────────────────────────────┤
│ • HTTP session management                                      │
│ • Retry logic (exponential backoff, max 3 retries)            │
│ • Error handling                                               │
│ • Logging                                                      │
│ • Rate limiting                                                │
└───────────────────────────────────────────────────────────────┘
        │
        ├──────────────────┬──────────────────┬────────────────┬────────────┐
        ▼                  ▼                  ▼                ▼            ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐  ┌──────────┐ ┌──────────┐
│ WiChartClient │  │SimplizeClient │  │ VNStockClient │  │Fireant   │ │Vietcap   │
├───────────────┤  ├───────────────┤  ├───────────────┤  │Client    │ │Client    │
│ • FX rates    │  │ • Economic    │  │ • OHLCV       │  ├──────────┤ ├──────────┤
│ • Commodities │  │   indicators  │  │ • Market cap  │  │ • News   │ │ • Realtime│
│ • Bond yields │  │ • GDP, CPI    │  │ • Fundamental │  │ • Events │ │   data   │
│ (gold,oil,    │  │ • Interest    │  │ • Company info│  │          │ │          │
│  steel,rubber)│  │   rates       │  │               │  │          │ │          │
└───────────────┘  └───────────────┘  └───────────────┘  └──────────┘ └──────────┘
        │                  │                  │                │            │
        └──────────────────┴──────────────────┴────────────────┴────────────┘
                                   │
                                   ▼
                    ┌───────────────────────────┐
                    │    UnifiedDataFetcher     │
                    ├───────────────────────────┤
                    │ • Standardized schema     │
                    │ • Source abstraction      │
                    │ • Fallback logic          │
                    │ • Error recovery          │
                    └───────────────────────────┘
```

---

## 11. MCP Server Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      MCP SERVER                                  │
│                   (MCP_SERVER/bsc_mcp/)                         │
│                   (FastMCP, 30 tools)                           │
└─────────────────────────────────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────────────────────────────┐
│                     FastMCP Server                             │
│                      (server.py)                               │
├───────────────────────────────────────────────────────────────┤
│ • stdio transport                                              │
│ • 30 registered tools                                          │
│ • Logging configuration                                        │
│ • Error handling                                               │
└───────────────────────────────────────────────────────────────┘
        │
        ├────────────────┬────────────────┬────────────────┬────────────┐
        ▼                ▼                ▼                ▼            ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────┐ ┌──────────┐
│ Ticker Tools │  │Fundamental   │  │ Technical    │  │Valuation │ │Forecast  │
│    (5)       │  │   Tools (5)  │  │  Tools (8)   │  │Tools (6) │ │Tools (2) │
├──────────────┤  ├──────────────┤  ├──────────────┤  ├──────────┤ ├──────────┤
│ list_tickers │  │get_financials│  │get_indicators│  │get_pe_stats│ │list_bsc  │
│ get_info     │  │compare_funds │  │get_alerts    │  │get_pb_stats│ │get_bsc_fc│
│ search       │  │screen_funds  │  │get_patterns  │  │compare_val│ │get_upside│
│ get_peers    │  │get_latest_fund│ │market_breadth│  │sector_val │ │          │
│ list_sectors │  │              │  │get_technicals│  │get_val_stats│ │          │
└──────────────┘  └──────────────┘  └──────────────┘  └──────────┘ └──────────┘
        │                │                │                │            │
        └────────────────┴────────────────┴────────────────┴────────────┘
                                   │
                                   ▼
                    ┌───────────────────────────┐
                    │    DATA/processed/*       │
                    │    (Read-only access)     │
                    │    • fundamental/         │
                    │    • technical/           │
                    │    • valuation/           │
                    │    • sector/              │
                    │    • forecast/bsc/        │
                    └───────────────────────────┘
```

---

## 12. Component Interactions

```
┌─────────────────────────────────────────────────────────────────┐
│                    COMPONENT INTERACTION                         │
└─────────────────────────────────────────────────────────────────┘

User Request (Streamlit UI)
        │
        ▼
┌───────────────────────────────────────┐
│ WEBAPP/pages/sector/sector_dashboard.py│
│ (Dashboard Page)                       │
│ • init_page_state('sector')            │  ← CRITICAL
└───────────────────┬───────────────────┘
                    │ calls
                    ▼
┌───────────────────────────────────────┐
│ WEBAPP/services/sector_service.py     │
│ (Data Service)                        │
│ • Load sector scores                  │
│ • Load sector metrics                 │
│ • Format for display                  │
└───────────────────┬───────────────────┘
                    │ imports
        ┌───────────┴───────────┐
        ▼                       ▼
┌───────────────────────┐  ┌───────────────────────────┐
│config/registries      │  │DATA/processed/            │
│ • MetricRegistry      │  │sector/                    │
│ • SectorRegistry      │  │sector_combined_           │
│ • SchemaRegistry      │  │scores.parquet             │
│                       │  │sector_fundamental_        │
│                       │  │metrics.parquet            │
│                       │  │sector_valuation_          │
│                       │  │metrics.parquet            │
└───────────────────────┘  └───────────────────────────┘
```

---

## 13. Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     DEPLOYMENT ARCHITECTURE                      │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      STREAMLIT CLOUD                             │
│                  (vietnamstock.streamlit.app)                    │
│                  (Free tier: 1GB RAM, 800MB CPU)                │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   Streamlit Runtime                      │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │   │
│  │  │ main_app.py │  │  Services   │  │ Components  │     │   │
│  │  │(8 pages)    │  │ (8 modules) │  │(charts,etc)│     │   │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘     │   │
│  │         └─────────────────┼───────────────┘             │   │
│  │                           ▼                             │   │
│  │                ┌─────────────────┐                      │   │
│  │                │  @st.cache_data │                      │   │
│  │                │   (In-memory)   │                      │   │
│  │                │   • TTL: 3600s  │                      │   │
│  │                │   • 300s for TA │                      │   │
│  │                └────────┬────────┘                      │   │
│  │                         ▼                               │   │
│  │                ┌─────────────────┐                      │   │
│  │                │  DATA/ (static) │                      │   │
│  │                │  (~500 MB)      │                      │   │
│  │                │  (committed to  │                      │   │
│  │                │   GitHub repo)  │                      │   │
│  │                └─────────────────┘                      │   │
│  │                                                          │   │
│  │  ┌─────────────────────────────────────────────────┐    │   │
│  │  │ Session State (st.session_state)               │    │   │
│  │  │ • Prevents page resets on widget interactions  │    │   │
│  │  │ • Initialized via init_page_state()            │    │   │
│  │  │ • Persists across all 8 pages                 │    │   │
│  │  └─────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ git push
┌─────────────────────────────┴───────────────────────────────────┐
│                         GITHUB                                   │
│                (github.com/Buu205/Vietnam_stock)                │
├─────────────────────────────────────────────────────────────────┤
│ • Source code (WEBAPP/, PROCESSORS/, config/)                   │
│ • Data files (DATA/processed/*.parquet, ~500 MB)               │
│ • Documentation (docs/, README.md, CLAUDE.md)                   │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ daily update
┌─────────────────────────────┴───────────────────────────────────┐
│                    LOCAL DEVELOPMENT                             │
│                   (/Users/buuphan/Dev/)                         │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐                      │
│  │ Daily Pipelines │  │ Manual Updates  │                      │
│  │ (PROCESSORS/)   │  │ (BSC Excel)     │                      │
│  │ • 6 steps       │  │ • Forecast data │                      │
│  │ • ~2 minutes    │  │ • Manual commit │                      │
│  └────────┬────────┘  └────────┬────────┘                      │
│           └────────────────────┘                                │
│                       │                                          │
│                       ▼                                          │
│           ┌─────────────────────┐                               │
│           │ DATA/processed/     │                               │
│           │ (Updated parquet)   │                               │
│           │ • fundamental/      │                               │
│           │ • technical/        │                               │
│           │ • valuation/        │                               │
│           │ • sector/           │                               │
│           └─────────────────────┘                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## Related Documents

- [Project Overview](project-overview-pdr.md) - Vision, requirements, roadmap
- [Codebase Summary](codebase-summary.md) - Module structure, file inventory
- [Code Standards](code-standards.md) - Naming conventions, patterns
- [CLAUDE.md](../CLAUDE.md) - AI/Developer guidelines (CRITICAL)
- [Technical Module README](../WEBAPP/pages/technical/README.md) - Technical analysis documentation (658 lines)
