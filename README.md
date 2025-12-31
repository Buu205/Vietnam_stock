# Vietnam Stock Dashboard

Vietnamese stock market financial data platform for 457 tickers across 19 sectors with fundamental, technical, valuation, and forecast analysis.

**Live:** [vietnamstock.streamlit.app](https://vietnamstock.streamlit.app)
**Repository:** [github.com/Buu205/Vietnam_stock](https://github.com/Buu205/Vietnam_stock)
**Version:** v4.0.0 (40% complete)

---

## 📊 Features

Multi-layered platform: 4 entity types, 457 tickers, 19 sectors, 6-stage daily pipeline

| Feature | Coverage | Details |
|---------|----------|---------|
| **Fundamental** | 4 types | Company, Bank, Insurance, Security metrics |
| **Technical** | 457 tickers | OHLCV, 10+ indicators, alerts, breadth |
| **Valuation** | PE/PB/PS/EV | TTM + Forward, 7+ years history |
| **Sector** | 19 sectors | FA+TA scoring with aggregation |
| **BSC Forecast** | 93 stocks | Target prices, ratings, EPS forecasts |

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

| Page | Focus | Key Metrics |
|------|-------|-------------|
| **Company** | Companies | Revenue, ROE, margins, growth |
| **Bank** | Banks (57) | NIM, CAR, NPL, CASA, LDR |
| **Security** | Brokerages (146) | Commission, AUM, ROE, leverage |
| **Sector** | 19 sectors | PE, PB, PS, EV/EBITDA valuation |
| **Valuation** | 457 stocks | PE/PB percentile, z-score bands |
| **Technical** | Price action | Breadth, regime, patterns, scanner |
| **Forecast** | 93 stocks | BSC targets, EPS, ratings |
| **FX & Commodities** | Macro | USD/VND, rates, oil, gold |

---

## 🎯 Technical Analysis Dashboard

Advanced market analysis with real-time signals and bottom detection:

### Market Health Scoring
**Weighted Market Score** = (MA50 breadth × 50%) + (MA20 breadth × 30%) + (MA100 breadth × 20%)
- ✅ **≥ 60:** Green - Healthy market
- ⚠️ **40-59:** Amber - Caution zone
- ❌ **< 40:** Red - Bearish

### Signal Matrix (9 Signals)
| Signal | Condition | Action |
|--------|-----------|--------|
| **STRONG_BUY** | Extreme oversold pullback in uptrend (MA20 < 20%) | Deploy capital aggressively |
| **BUY** | Normal pullback in uptrend (MA20 20-40%) | Scale in or new position |
| **HOLD** | Healthy uptrend (MA20 40-80%) | Maintain position, trend good |
| **WARNING** | Overbought conditions (MA20 > 80%) | Don't chase, take profits |
| **SELL** | Bull trap in downtrend (MA20 > 70%) | Reduce exposure |
| **DANGER** | Market crash (MA50 < 30%, MA20 < 20%, no higher low) | Stay in cash absolutely |
| **WAIT** | Sideways/no trend detected | Observe, no entry point |
| **ACCUMULATING** | Smart money entering (all MA < 30%, MA20 higher low forming) | Watch closely, prepare capital |
| **EARLY_BUY** | Early reversal confirmed (MA20 ≥ 25%, both MA20/MA50 higher lows) | Test buy 10-20%, tight stop |

### Bottom Detection System (3 Stages)
1. **CAPITULATION** - Extreme panic (all MA < 25%, no higher low yet)
2. **ACCUMULATING** - Smart money entering (all MA < 30%, MA20 forming higher low in 3-day window)
3. **EARLY_REVERSAL** - Reversal confirmed (MA20 ≥ 25%, MA50 forming higher low in 5-day window)

### Capital Allocation (Exposure Control)
Based on market regime + breadth strength:
- **0%** - Bearish regime (stay in cash)
- **20%** - Heavy pullback (breadth < 25%)
- **40%** - Conservative (breadth 25-40%)
- **60%** - Moderate (breadth 40-55%)
- **80%** - Heavy (breadth 55-70%)
- **100%** - Full deployment (breadth ≥ 70%)

### Components
- **Market Overview:** VN-Index, regime detection (EMA9 vs EMA21), breadth zones, market score
- **Sector Rotation:** RRG quadrants (LEADING/IMPROVING/WEAKENING/LAGGING), sector ranking, money flow
- **Stock Scanner:** Candlestick patterns (20+ types), MA crossovers, volume spikes, breakouts with volume context
- **Filter Bar:** Timeframe selector (30D-1Y), sector filter, signal type selector

See [`docs/ta-dashboard-logic.md`](docs/ta-dashboard-logic.md) for complete formulas and decision trees.

---

## 📊 Data Coverage

| Metric | Coverage | Details |
|--------|----------|---------|
| **Tickers** | 457 | All HNX, HSX stocks |
| **Sectors** | 19 | Financial, Real Estate, Tech, Consumer, Energy |
| **Raw Metrics** | 2,099+ | Vietnamese metric codes with 40+ calculated formulas |
| **Fundamentals** | 19.9M+ records | 2018-2025 quarterly by entity type |
| **Valuation** | 792K+ records | 2018-2025 daily PE/PB/PS/EV historical |
| **Technical** | 89K+ records | 2020-2025 daily indicators, alerts, breadth |
| **Forecast** | 93 stocks | BSC Research quarterly targets & EPS |

---

## 💾 Data Pipeline

3-layer architecture: Raw CSV (175 MB) → Processing → Parquet output (229 MB)

**Update Frequency:**
- OHLCV & Technical: Daily (overnight)
- Valuation & Sector: Daily (cascading)
- Fundamentals: Quarterly
- Macro/Commodity: Daily
- BSC Forecast: Quarterly

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

### Data Mapping Registry (v1.0.0 - NEW)

Clean architecture registry for zero-hardcoded-paths design:

```python
from config.data_mapping import get_registry, get_data_path, DependencyResolver

# Simple path lookup (recommended)
path = get_data_path("bank_metrics")  # Returns: DATA/processed/fundamental/bank/...

# Full registry access
registry = get_registry()
sources = registry.get_sources_for_dashboard("bank_dashboard")

# Impact analysis (dependency chain)
resolver = DependencyResolver()
impact = resolver.get_impact_chain("ohlcv_raw")  # Shows all dependent data
```

**Structure:** 5 Python modules + 4 YAML configs
- `entities.py` - Dataclasses (DataSource, PipelineOutput, etc.)
- `registry.py` - Singleton registry with lookup methods
- `resolver.py` - PathResolver, DependencyResolver for impact analysis
- `validator.py` - SchemaValidator, HealthChecker for data quality
- `configs/` - YAML files: data_sources, services, pipelines, dashboards

**Benefits:** Single source of truth for data mappings, schema validation, dependency tracking, automatic path resolution in services.

### Data Path Standards (v4.0.0)
```python
from pathlib import Path
from PROCESSORS.core.config.paths import get_data_path

# Standard: DATA/processed/ or DATA/raw/ paths
path = Path("DATA/processed/fundamental/company/company_financial_metrics.parquet")
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

| Doc | Purpose |
|-----|---------|
| [project-overview-pdr.md](docs/project-overview-pdr.md) | Goals, PDR, roadmap |
| [system-architecture.md](docs/system-architecture.md) | Data flow, components |
| [codebase-summary.md](docs/codebase-summary.md) | Code structure |
| [code-standards.md](docs/code-standards.md) | Style guide |
| [CLAUDE.md](CLAUDE.md) | AI guidelines |

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

## 💻 Tech Stack

**Frontend:** Streamlit (UI) + Plotly (charts)
**Backend:** Python 3.13 + Pandas + TA-Lib
**Storage:** Parquet (snappy compression)
**Deployment:** Streamlit Cloud

---

## 📖 Development Guidelines

Before coding: Read [`CLAUDE.md`](CLAUDE.md) + [`.claude/rules/critical.md`](.claude/rules/critical.md)

**Key Rules:**
- Use registries (MetricRegistry, SectorRegistry, SchemaRegistry)
- Use canonical paths (`DATA/raw/`, `DATA/processed/`)
- Reuse existing calculators, don't duplicate
- Don't create new markdown files (update existing)

---

## 📝 License & Attribution

**Private repository** - All rights reserved
**Maintained by:** Buu Phan
**Contact:** [GitHub Issues](https://github.com/Buu205/Vietnam_stock/issues)
**Data Sources:** VNStock, BSC Research, Vietnam Stock Exchange
