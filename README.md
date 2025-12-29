# Vietnam Stock Dashboard

Vietnamese stock market financial data platform for 457 tickers across 19 sectors with fundamental, technical, valuation, and forecast analysis.

**Live:** [vietnamstock.streamlit.app](https://vietnamstock.streamlit.app)
**Repository:** [github.com/Buu205/Vietnam_stock](https://github.com/Buu205/Vietnam_stock)
**Version:** v4.0.0 (40% complete)

---

## 📊 Features

Multi-layered financial analysis platform with unified registry system, 6-stage daily pipeline, and comprehensive dashboards:

| Feature | Coverage | Details |
|---------|----------|---------|
| **Fundamental Analysis** | 4 entity types | Company (2,246), Bank (57), Insurance (34), Security (154) |
| **Technical Analysis** | 457 tickers | OHLCV, 10+ indicators, alerts, money flow, breadth |
| **Valuation** | PE, PB, PS, EV/EBITDA | TTM + Forward (2025-2026), 7+ years history |
| **Sector Analysis** | 19 sectors | FA+TA scoring with aggregated metrics |
| **BSC Forecast** | 93 stocks | Target prices, ratings, EPS/revenue forecasts |

---

## 🚀 Quick Start

```bash
# Clone & install
git clone https://github.com/Buu205/Vietnam_stock.git
cd Vietnam_dashboard
pip install -r WEBAPP/requirements.txt

# Run dashboard
streamlit run WEBAPP/main_app.py
# Opens at http://localhost:8501

# Daily data update (~45 minutes)
python3 PROCESSORS/pipelines/run_all_daily_updates.py
```

---

## 🏗️ Architecture Overview

### Frontend (WEBAPP/ - 113 files, 15K+ LOC)
- **8 Dashboards:** Company, Bank, Security, Sector, Valuation, Technical, Forecast, FX/Commodities
- **MVC Pattern:** Pages (view) → Services (data) → Components (UI) → Core (config)
- **Design:** Glassmorphism crypto terminal (purple/cyan/amber palette)
- **Session State:** Persistent widget state, TTL-based caching (3600s)

### Backend (PROCESSORS/ - 86+ files, 32K+ LOC)
- **6-Stage Daily Pipeline:**
  1. OHLCV Update (vnstock API)
  2. Technical Indicators (MA, RSI, MACD, Bollinger, Stochastic)
  3. Macro & Commodity (interest rates, FX, oil, gold)
  4. Valuation (PE, PB, PS, EV/EBITDA)
  5. Sector Analysis (FA+TA aggregation + scoring)
  6. BSC Forecast (Excel processing)

- **9 Major Modules:**
  - Pipelines: Daily orchestration & validation
  - Core: Shared utilities, registries, path management
  - Fundamental: 4 entity-type calculators (ROE, NIM, margins, growth)
  - Technical: 10+ indicators, alerts, money flow, breadth
  - Valuation: PE/PB/PS/EV calculators (historical + forward)
  - Sector: FA aggregator, TA aggregator, scorers
  - Forecast: BSC Excel processor
  - API: Data source integrations
  - Decision: Trading signal generation

### Data (DATA/ - 470 MB)
- **Raw Layer:** 175 MB CSV fundamentals, 56 MB OHLCV, metadata
- **Processed Layer:** 229 MB parquet (snappy compressed)
- **Coverage:** 19.9M+ fundamental records, 792K+ valuation records, 7+ years history
- **Format:** v4.0.0 canonical paths (`DATA/raw/`, `DATA/processed/`)

### Configuration (config/ - 38 JSON files)
- **MetricRegistry:** 2,099+ raw metrics + 40+ calculated formulas
- **SectorRegistry:** 457 tickers × 19 sectors × 4 entity types
- **SchemaRegistry:** Formatting rules, color schemes, type validation

---

## 📋 Dashboard Pages (8 Total)

| Page | Entity Focus | Key Metrics | Data Source |
|------|-------------|-----------|-------------|
| **Company** | Non-financial companies | Revenue, margins (ROE/ROA), growth, ratios | `company_financial_metrics.parquet` |
| **Bank** | 57 Vietnamese banks | NIM, CAR, NPL, CASA, LDR, CIR, LLCR | `bank_financial_metrics.parquet` |
| **Security** | Brokerages (146) | Commission, AUM, trading vol, ROE, leverage | `security_financial_metrics.parquet` |
| **Sector** | 19 sectors | PE, PB, PS, EV/EBITDA valuation by sector | `vnindex_valuation_*.parquet` |
| **Valuation** | 457 stocks | PE/PB percentile, historical bands, z-score | `valuation/{pe,pb,ps,ev_ebitda}/` |
| **Technical** | Price action | OHLC, MA, RSI, MACD, ADX, Stochastic, money flow | `technical/basic_data.parquet` |
| **Forecast** | 93 stocks | BSC targets, EPS/revenue forecasts, ratings | `forecast/bsc/bsc_individual.parquet` |
| **FX & Commodities** | Macro | USD/VND, interest rates, oil, gold prices | `macro_commodity_unified.parquet` |

---

## 📊 Key Statistics

| Metric | Value | Notes |
|--------|-------|-------|
| **Tickers** | 457 | All HNX, HSX stocks |
| **Sectors** | 19 | Financial, Real Estate, Tech, Consumer, Energy, etc. |
| **Entity Types** | 4 | COMPANY, BANK, INSURANCE, SECURITY |
| **Raw Metrics** | 2,099+ | Vietnamese metric codes (CIS_*, CBS_*, BIS_*, etc.) |
| **Calculated Metrics** | 40+ | ROE, ROA, margins, growth, ratios, NIM, NPL, CASA, etc. |
| **Fundamental Records** | 19.9M+ | 2018-2025 quarterly financials |
| **Valuation Records** | 792K+ | 2018-2025 daily PE/PB/PS/EV data |
| **Technical Records** | 89K+ | 2020-2025 daily OHLCV + indicators |
| **Historical Depth** | 7+ years | Quarterly fundamentals, daily technicals & valuations |
| **Forecast Coverage** | 93 stocks | BSC Research analyst forecasts |

---

## 💾 Data Architecture

### 3-Layer Design

```
INPUT LAYER (Raw)
  CSV fundamentals (175 MB) → OHLCV data (56 MB) → News/Metadata
       ↓
PROCESSING LAYER (Pipelines)
  Calculators (ROE, NIM, growth) → Indicators (MA, RSI, MACD)
  Valuations (PE, PB, PS, EV) → Sector aggregation → Scoring
       ↓
OUTPUT LAYER (Processed)
  Parquet files (229 MB) → Schema registry → Dashboards
       ↓
CONSUMPTION LAYER (Dashboards)
  8 Streamlit pages + Services layer + Components library
```

### Data Update Frequency

| Type | Frequency | Pipeline |
|------|-----------|----------|
| OHLCV / Technical | Daily (overnight) | `daily_ohlcv_update.py` → `technical_processor.py` |
| Valuation | Daily (after technicals) | `valuation/calculators/` |
| Sector Analysis | Daily (after valuation) | `sector_processor.py` (FA + TA aggregators) |
| Fundamentals | Quarterly (after statements released) | CSV → `run_all_calculators.py` |
| Macro/Commodity | Daily | `macro_commodity_fetcher.py` |
| BSC Forecast | Quarterly | Excel → `bsc_forecast_processor.py` |

---

## 🔧 Development Workflow

### Setup
```bash
# No virtual environment needed - uses global Python 3.13
python3 --version  # Python 3.13.x required

# Required packages already installed globally:
pip list | grep -E "pandas|streamlit|ta-lib|vnstock"
```

### Registry Pattern (Single Source of Truth)
```python
from config.registries import MetricRegistry, SectorRegistry
from config.schema_registry import SchemaRegistry

# Metric lookups
metric_reg = MetricRegistry()
metric = metric_reg.get_metric("CIS_62", "COMPANY")  # Net Income
formula = metric_reg.get_calculated_metric_formula("roe")

# Ticker/sector lookups
sector_reg = SectorRegistry()
ticker_info = sector_reg.get_ticker("ACB")  # Returns sector, entity type
peers = sector_reg.get_peers("ACB")  # Other banks

# Formatting via schema
schema_reg = SchemaRegistry()
formatted = schema_reg.format_price(25750.5)  # "25,750.50đ"
```

### Data Path Standards (v4.0.0)
```python
# Canonical paths - ALWAYS use these
from pathlib import Path

# ✅ Manual construction (standard)
path = Path("DATA/processed/fundamental/company/company_financial_metrics.parquet")
df = pd.read_parquet(path)

# ✅ Helper function (recommended)
from PROCESSORS.core.config.paths import get_data_path
path = get_data_path("processed", "fundamental", "company", "company_financial_metrics.parquet")
df = pd.read_parquet(path)
```

### Testing Pipeline Stages
```bash
# Individual module testing
python3 PROCESSORS/fundamental/calculators/run_all_calculators.py
python3 PROCESSORS/fundamental/calculators/run_all_calculators.py --entity bank
python3 PROCESSORS/technical/indicators/technical_processor.py
python3 PROCESSORS/valuation/calculators/historical_pe_calculator.py
python3 PROCESSORS/sector/sector_processor.py

# Full pipeline with options
python3 PROCESSORS/pipelines/run_all_daily_updates.py --skip-ohlcv --skip-ta
python3 PROCESSORS/pipelines/run_all_daily_updates.py --only valuation
```

---

## 📚 Documentation

Complete documentation structure in `./docs/`:

| Document | Purpose | Details |
|----------|---------|---------|
| [project-overview-pdr.md](docs/project-overview-pdr.md) | Vision & requirements | Project goals, PDR, roadmap |
| [system-architecture.md](docs/system-architecture.md) | System design | Data flow, components, integration |
| [codebase-summary.md](docs/codebase-summary.md) | Code structure | Module breakdown, key classes |
| [code-standards.md](docs/code-standards.md) | Style guide | Naming, imports, patterns |
| [CLAUDE.md](CLAUDE.md) | AI guidelines | Rules, patterns, workflows |

---

## 🔗 Data Sources

| Source | Data Type | Frequency | Coverage |
|--------|-----------|-----------|----------|
| **VNStock API** | OHLCV, market cap | Daily | 457 tickers |
| **BSC Research** | Analyst forecasts, targets | Quarterly | 93 stocks |
| **WiChart** | FX rates, commodities | Daily | Oil, gold, USD/VND |
| **Simplize** | Macro data | Daily | Interest rates, bonds |
| **Vietnamese Stock Exchange** | Fundamental data | Quarterly | 2,491 companies/banks |

---

## 💻 Technology Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Frontend** | Streamlit | 1.36+ | Dashboard UI |
| **Charts** | Plotly | Latest | Interactive visualizations |
| **Backend** | Python | 3.13 | Data processing |
| **Data Processing** | Pandas, NumPy | Latest | Analysis & transformations |
| **Technical Analysis** | TA-Lib | Compiled | Indicators (RSI, MACD, etc.) |
| **Fundamentals** | Custom calculators | v4.0.0 | Entity-specific metrics |
| **Storage** | Parquet (Snappy) | Columnar | Efficient data format |
| **Deployment** | Streamlit Cloud | Latest | Live dashboard hosting |

---

## 📊 Performance Metrics

- **Pipeline Duration:** ~45 minutes (full daily update)
- **Dashboard Load Time:** <3 seconds (cached data)
- **Data Compression:** 60-80% reduction (CSV → Parquet)
- **Total Data Size:** 470 MB (raw + processed)
- **Committed Data:** 83.2 MB (24 essential files for dashboard)

---

## 📖 Development Guidelines

**Before making code changes, read:**
1. [`CLAUDE.md`](CLAUDE.md) - AI developer guidelines (3 tiers: Rules, Guides, Reference)
2. [`.claude/rules/critical.md`](.claude/rules/critical.md) - Non-negotiable constraints
3. [`.claude/guides/architecture.md`](.claude/guides/architecture.md) - System design

**Key Principles:**
- ✅ Always use registries (MetricRegistry, SectorRegistry, SchemaRegistry)
- ✅ Use canonical paths (`DATA/raw/`, `DATA/processed/`)
- ✅ Reuse existing calculators (don't duplicate logic)
- ✅ Follow 3-tier documentation structure
- ❌ Don't create new markdown files (update existing ones)
- ❌ Don't use deprecated paths (data_warehouse, calculated_results)

---

## 🔍 Status & Roadmap

**Current Version:** v4.0.0 (40% complete)

**Completed:**
- ✅ Data pipeline (6-stage orchestration)
- ✅ Registry system (100% centralized lookups)
- ✅ PROCESSORS/ architecture (86+ files)
- ✅ WEBAPP/ dashboard (8 pages)
- ✅ Path migration (v4.0.0 standardization)

**In Progress:**
- 🔄 FA+TA sector analysis refactor
- 🔄 Advanced dashboard features

**Not Started:**
- ⏳ Mobile responsiveness
- ⏳ ML-based signals
- ⏳ Real-time streaming

---

## 📝 License & Attribution

**Private repository** - All rights reserved
**Maintained by:** Buu Phan
**Contact:** [GitHub Issues](https://github.com/Buu205/Vietnam_stock/issues)
**Data Sources:** VNStock, BSC Research, Vietnam Stock Exchange
