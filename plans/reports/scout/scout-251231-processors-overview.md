# PROCESSORS Directory Scout Report
**Date:** 2025-12-31 | **Focus:** Pipeline scripts, calculators, data flow

---

## 1. PIPELINE SCRIPTS (Master Orchestration)

### Main Entry Point
**File:** `PROCESSORS/pipelines/run_all_daily_updates.py` (630 lines)

- **Purpose:** Master orchestrator for ALL daily data updates
- **Execution:** Runs 6-step pipeline in sequence with error handling & progress tracking
- **Output:** Comprehensive logging to `logs/daily_update_YYYYMMDD.log`

**Pipeline Sequence:**
1. OHLCV Data Update (`daily_ohlcv_update.py`)
2. Technical Analysis (`daily_ta_complete.py`)
3. Macro & Commodity (`daily_macro_commodity.py`)
4. Stock Valuation (`daily_valuation.py`)
5. Sector Analysis (`daily_sector_analysis.py`)
6. BSC Forecast Update (`daily_bsc_forecast.py`)

**Features:**
- Skip individual steps: `--skip-ohlcv`, `--skip-ta`, etc.
- Force specific date: `--date 2025-12-26`
- Run only one step: `--only valuation`
- File verification after each step
- Data integrity report at end (checks latest dates, record counts)

### Individual Daily Scripts
| Script | Purpose | Key Output |
|--------|---------|-----------|
| `daily_ohlcv_update.py` | Fetch market data (OHLC) | `DATA/raw/ohlcv/OHLCV_mktcap.parquet` |
| `daily_ta_complete.py` | Full TA pipeline (MA, RSI, MACD, alerts, breadth, money flow) | `DATA/processed/technical/basic_data.parquet`, alerts/, breadth/ |
| `daily_macro_commodity.py` | Macro-economic & commodity data | `DATA/processed/macro_commodity/macro_commodity_unified.parquet` |
| `daily_valuation.py` | Stock PE/PB/EV-EBITDA + VN-Index | `DATA/processed/valuation/pe/historical/`, pb/, ps/, ev_ebitda/ |
| `daily_sector_analysis.py` | Sector aggregation & scoring | `DATA/processed/sector/sector_fundamental_metrics.parquet`, sector_valuation_metrics.parquet, sector_combined_scores.parquet |
| `daily_bsc_forecast.py` | Update BSC forecast from Excel | `DATA/processed/forecast/bsc/bsc_individual.parquet`, bsc_sector_valuation.parquet, bsc_combined.parquet |
| `daily_rs_rating.py` | RS Rating (auxiliary) | `DATA/processed/technical/rs_rating/stock_rs_rating_daily.parquet` |

---

## 2. FUNDAMENTAL CALCULATOR MODULES

### Main Calculator
**File:** `PROCESSORS/fundamental/calculators/run_all_calculators.py` (250+ lines)

- **Purpose:** Unified script for ALL entity-type calculations
- **Input:** `*_full.parquet` files (long format with METRIC_CODE)
- **Process:** Pivot → Calculate → Output
- **Entities:** COMPANY, BANK, INSURANCE, SECURITY

**Class:** `EntityCalculator(ABC)` - Base class with:
- `load_and_pivot()` - Load long format, pivot to wide
- `calculate_metrics()` - Abstract method (entity-specific)
- `save_output()` - Save to parquet with compression

**Usage:**
```bash
python3 PROCESSORS/fundamental/calculators/run_all_calculators.py
python3 PROCESSORS/fundamental/calculators/run_all_calculators.py --entity bank
```

**Output Files:**
```
DATA/processed/fundamental/
├── company/company_financial_metrics.parquet
├── bank/bank_financial_metrics.parquet
├── insurance/insurance_financial_metrics.parquet
└── security/security_financial_metrics.parquet
```

### Formula Modules

**Base Formulas:** `PROCESSORS/fundamental/formulas/_base_formulas.py`
- `calculate_roe()` - Net Income / Equity
- `calculate_roa()` - Net Income / Assets
- `calculate_roic()` - NOPAT / Invested Capital
- `calculate_*_margin()` - Margin calculations (gross, operating, net, ebit, ebitda)
- `calculate_*_ratio()` - Liquidity/solvency (current, quick, cash, debt-to-equity)
- `calculate_*_turnover()` - Efficiency metrics (asset, inventory, receivables)
- `calculate_yoy_growth()`, `calculate_qoq_growth()` - Growth rates
- `calculate_ttm_sum()` - Trailing Twelve Months

**Company-Specific:** `PROCESSORS/fundamental/formulas/company_formulas.py`
- `CompanyFormulas.calculate_revenue_growth()`
- `CompanyFormulas.calculate_profit_growth()`
- `CompanyFormulas.calculate_free_cash_flow()`

**Bank-Specific:** `PROCESSORS/fundamental/formulas/bank_formulas.py`
- `BankFormulas.calculate_nim()` - Net Interest Margin
- `BankFormulas.calculate_car()` - Capital Adequacy Ratio
- `BankFormulas.calculate_casa_ratio()` - CASA Ratio
- `BankFormulas.calculate_ldr()` - Loan-to-Deposit Ratio
- `BankFormulas.calculate_npl()` - Non-Performing Loan
- `BankFormulas.calculate_llcr()` - Loan Loss Coverage Ratio

**Registry:** `PROCESSORS/fundamental/formulas/registry.py`
- `FormulaRegistry` class manages all formulas
- Methods: `get_formula()`, `list_formulas()`, `register_formula()`

**Utilities:** `PROCESSORS/fundamental/formulas/utils.py`
- `safe_divide()` - Handles zero division
- `to_percentage()` - Convert to percentage format

---

## 3. VALUATION CALCULATOR MODULES

### PE Calculator
**File:** `PROCESSORS/valuation/calculators/historical_pe_calculator.py`
- Calculates P/E ratio = Market Cap / Net Income
- Outputs: `DATA/processed/valuation/pe/historical/historical_pe.parquet`

### PB Calculator
**File:** `PROCESSORS/valuation/calculators/historical_pb_calculator.py`
- Calculates P/B ratio = Market Cap / Total Equity
- Outputs: `DATA/processed/valuation/pb/historical/historical_pb.parquet`

### PS Calculator
**File:** `PROCESSORS/valuation/calculators/historical_ps_calculator.py`
- Calculates P/S ratio = Market Cap / Revenue
- Outputs: `DATA/processed/valuation/ps/historical/historical_ps.parquet`

### EV/EBITDA Calculator
**File:** `PROCESSORS/valuation/calculators/historical_ev_ebitda_calculator.py`
- Calculates EV/EBITDA ratio
- Outputs: `DATA/processed/valuation/ev_ebitda/historical/historical_ev_ebitda.parquet`

### VN-Index Valuation
**File:** `PROCESSORS/valuation/calculators/vnindex_valuation_calculator.py`
- Aggregates PE/PB/EV-EBITDA at VN-Index level
- Outputs: `DATA/processed/valuation/vnindex/vnindex_valuation_refined.parquet`

### Backfill Script
**File:** `PROCESSORS/valuation/calculators/run_full_backfill.py`
- One-time script to backfill historical valuation data
- Run manually when needed (not part of daily pipeline)

### Metric Mapper
**File:** `PROCESSORS/valuation/formulas/metric_mapper.py`
- Maps valuation concepts to source metrics
- Used by calculators to resolve which columns contain needed values

---

## 4. SECTOR ANALYSIS MODULES

### Main Orchestrator
**File:** `PROCESSORS/sector/sector_processor.py` (100+ lines)

- **Purpose:** Orchestrate complete sector analysis pipeline
- **Class:** `SectorProcessor` - manages workflow
- **Pipeline:**
  1. Load registries (MetricRegistry, SectorRegistry)
  2. Run FAAggregator → sector fundamental metrics
  3. Run TAAggregator → sector valuation metrics
  4. Run FAScorer → FA scores
  5. Run TAScorer → TA scores
  6. Run SignalGenerator → combined scores + signals

**Output Files:**
```
DATA/processed/sector/
├── sector_fundamental_metrics.parquet    (FA metrics)
├── sector_valuation_metrics.parquet      (TA/valuation metrics)
└── sector_combined_scores.parquet        (BUY/SELL/HOLD signals)
```

### FA Aggregator
**File:** `PROCESSORS/sector/calculators/fa_aggregator.py`
- Aggregates company fundamental metrics by sector
- Calculates average ROE, ROA, margins, growth rates per sector
- Input: Company-level FA metrics
- Output: Sector-level FA metrics

### TA Aggregator
**File:** `PROCESSORS/sector/calculators/ta_aggregator.py`
- Aggregates technical/valuation metrics by sector
- Calculates sector PE, PB, EV/EBITDA (weighted)
- Aggregates momentum, breadth indicators
- Input: Stock valuation + TA metrics
- Output: Sector-level valuation & TA metrics

### Base Aggregator
**File:** `PROCESSORS/sector/calculators/base_aggregator.py`
- Abstract base class for all aggregators
- Common methods for loading, calculating, saving

### Metric Mappings
**File:** `PROCESSORS/sector/calculators/metric_mappings.py`
- Defines which columns to aggregate per sector
- Maps source columns to output metric names

### FA Scorer
**File:** `PROCESSORS/sector/scoring/fa_scorer.py`
- Scores sectors based on FA metrics (ROE, margins, growth)
- Produces FA score (0-100 or similar)

### TA Scorer
**File:** `PROCESSORS/sector/scoring/ta_scorer.py`
- Scores sectors based on TA metrics (momentum, breadth, valuation)
- Produces TA score (0-100 or similar)

### Signal Generator
**File:** `PROCESSORS/sector/scoring/signal_generator.py`
- Combines FA + TA scores → BUY/SELL/HOLD signals
- Configurable weighting (FA weight vs TA weight)

---

## 5. DATA MAPPING & REGISTRY RELATIONSHIP

### Metric Registry Integration
**File:** `PROCESSORS/fundamental/formulas/registry.py`

The `FormulaRegistry` class provides:
- Centralized formula lookup by name
- Entity-specific formula registration (COMPANY, BANK, INSURANCE, SECURITY)
- Dynamic formula discovery

**Connection to Data Mapping:**
- `MetricRegistryLoader` (`PROCESSORS/valuation/formulas/metric_mapper.py`) maps business concepts to metric codes
- Example: `net_income` → `CIS_61` (COMPANY), `BIS_22A` (BANK)
- Formulas use metric codes to resolve which columns contain source data

**Flow:**
```
metric_registry.json (metadata)
    ↓
MetricRegistryLoader / FormulaRegistry
    ↓
Calculators (company_calculator.py, bank_calculator.py)
    ↓
*_financial_metrics.parquet (output)
```

### Unified Mapper
**File:** `PROCESSORS/core/shared/unified_mapper.py`
- Provides unified ticker → sector → entity type mapping
- Used by all processors to validate symbols and resolve sectors

---

## 6. CORE UTILITY MODULES

### Path Configuration
**File:** `PROCESSORS/core/config/paths.py`
- Centralized path definitions
- Function: `get_data_path()` - resolves paths dynamically
- Ensures all processors use canonical `DATA/processed/` and `DATA/raw/` paths

### Data Validators
**Files:**
- `PROCESSORS/core/validators/input_validator.py` - Validates input data
- `PROCESSORS/core/validators/output_validator.py` - Validates output files
- `PROCESSORS/core/validators/bsc_csv_adapter.py` - BSC CSV conversion

### Shared Utilities
| File | Purpose |
|------|---------|
| `unified_mapper.py` | Ticker → sector → entity mapping |
| `symbol_loader.py` | Load symbols from metadata |
| `data_validator.py` | Data quality checks |
| `date_formatter.py` | Consistent date formatting |
| `backup_logger.py` | Backup & logging utilities |
| `technical_data_retention.py` | Manage technical data retention |

### AI-Powered Formula Generation (Experimental)
**Files:**
- `PROCESSORS/core/ai/formula_ai_assistant.py` - LLM-based formula generation
- `PROCESSORS/core/ai/nlp_formula_parser.py` - Parse business concepts
- `PROCESSORS/core/ai/metric_registry_resolver.py` - Resolve metrics
- `PROCESSORS/core/ai/formula_code_generator.py` - Generate Python code

---

## 7. TECHNICAL ANALYSIS MODULES

### Main TA Processor
**File:** `PROCESSORS/technical/indicators/technical_processor.py`
- Calculates all TA indicators (MA, RSI, MACD, BBANDS, etc.)
- Outputs: `DATA/processed/technical/basic_data.parquet`

### Indicator Processors
| File | Purpose | Output |
|------|---------|--------|
| `alert_detector.py` | Buy/sell signal alerts | `technical/alerts/*.parquet` |
| `sector_breadth.py` | Sector breadth indicators | `technical/sector_breadth/` |
| `money_flow.py` | Money flow analysis (individual) | `technical/` |
| `sector_money_flow.py` | Money flow by sector | `technical/` |
| `vnindex_analyzer.py` | VN-Index specific analysis | `technical/vnindex/` |
| `market_regime.py` | Market regime detection | `technical/` |
| `rs_rating.py` | Relative strength rating | `technical/rs_rating/` |

### OHLCV Management
**File:** `PROCESSORS/technical/ohlcv/ohlcv_daily_updater.py`
- Fetches daily OHLCV data
- Detects price adjustments
- Manages data quality

**File:** `PROCESSORS/technical/ohlcv/ohlcv_adjustment_detector.py`
- Detects stock splits, dividends, adjustments

### Macro/Commodity Fetcher
**File:** `PROCESSORS/technical/macro_commodity/macro_commodity_fetcher.py`
- Fetches macro-economic & commodity data
- Outputs: `DATA/processed/macro_commodity/macro_commodity_unified.parquet`

---

## 8. FORECAST MODULES

### BSC Forecast Processor
**File:** `PROCESSORS/forecast/bsc_forecast_processor.py`
- Reads BSC Research Excel file
- Converts to parquet with stock prices updated
- Outputs:
  - `DATA/processed/forecast/bsc/bsc_individual.parquet`
  - `DATA/processed/forecast/bsc/bsc_sector_valuation.parquet`
  - `DATA/processed/forecast/bsc/bsc_combined.parquet`

### Update BSC Excel
**File:** `PROCESSORS/forecast/update_bsc_excel.py`
- Re-reads Excel file when BSC updates forecast
- Can be run independently

---

## 9. API LAYER (Data Fetching)

### Unified Fetcher
**File:** `PROCESSORS/api/unified_fetcher.py`
- Abstracts all data sources (vnstock, wichart, fireant, simplize)
- Provides single interface for data fetching

### Clients
| Client | Purpose |
|--------|---------|
| `vnstock_client.py` | vnstock API data |
| `wichart_client.py` | wichart chart data |
| `fireant_client.py` | fireant fundamental data |
| `simplize_client.py` | simplize simplification data |

### VietCap Integration
**Files:**
- `vietcap_auth.py` - Authentication handling
- `vietcap_client.py` - VietCap API client
- `fetch_vci_forecast.py` - Fetch VCI forecast

### Monitoring
**Files:**
- `monitoring/metrics_logger.py` - API call metrics
- `monitoring/health_checker.py` - Health monitoring

---

## 10. KEY OUTPUT FILES BY PROCESSOR

### Fundamental Metrics
```
DATA/processed/fundamental/
├── company/company_financial_metrics.parquet
│   └── Columns: ticker, date, year, quarter, revenue, net_income, equity, roe, roa, ...
├── bank/bank_financial_metrics.parquet
│   └── Columns: ticker, date, nim, car, casa_ratio, ldr, npl, llcr, ...
├── insurance/insurance_financial_metrics.parquet
└── security/security_financial_metrics.parquet
```

### Technical Analysis
```
DATA/processed/technical/
├── basic_data.parquet
│   └── Columns: symbol, date, open, high, low, close, ma20, ma50, rsi, macd, ...
├── alerts/
│   └── buy_alerts.parquet, sell_alerts.parquet
├── rs_rating/stock_rs_rating_daily.parquet
│   └── Columns: symbol, date, rs_rating
├── sector_breadth/sector_breadth_daily.parquet
│   └── Columns: sector, date, breadth_pct
└── vnindex/vnindex_analysis.parquet
    └── VN-Index specific indicators
```

### Valuation Metrics
```
DATA/processed/valuation/
├── pe/historical/historical_pe.parquet
│   └── Columns: ticker, date, pe_ratio
├── pb/historical/historical_pb.parquet
│   └── Columns: ticker, date, pb_ratio
├── ps/historical/historical_ps.parquet
│   └── Columns: ticker, date, ps_ratio
├── ev_ebitda/historical/historical_ev_ebitda.parquet
│   └── Columns: ticker, date, ev_ebitda
└── vnindex/vnindex_valuation_refined.parquet
    └── VN-Index PE/PB/EV-EBITDA
```

### Sector Analysis
```
DATA/processed/sector/
├── sector_fundamental_metrics.parquet
│   └── Columns: sector_code, date, avg_roe, avg_roa, avg_margin, ...
├── sector_valuation_metrics.parquet
│   └── Columns: sector_code, date, avg_pe, avg_pb, avg_ev_ebitda, ...
└── sector_combined_scores.parquet
    └── Columns: sector_code, date, fa_score, ta_score, signal (BUY/SELL/HOLD)
```

### Macro/Commodity
```
DATA/processed/macro_commodity/
└── macro_commodity_unified.parquet
    └── Columns: date, category, value (interest rates, inflation, oil prices, etc.)
```

### BSC Forecast
```
DATA/processed/forecast/bsc/
├── bsc_individual.parquet
│   └── Stock-level BSC forecasts + ratings
├── bsc_sector_valuation.parquet
│   └── Sector-level valuations
└── bsc_combined.parquet
    └── Combined forecast data
```

---

## 11. DATA FLOW DIAGRAM

```
RAW DATA
├── OHLCV_mktcap.parquet (vnstock)
├── fundamental/csv/Q*/ (company financials)
├── macro/ (economic data)
└── commodity/ (price data)

        ↓ PROCESSORS (Calculation)

PROCESSED DATA (1st Pass)
├── technical/basic_data.parquet (TA indicators)
├── fundamental/*_financial_metrics.parquet (FA metrics)
├── macro_commodity/macro_commodity_unified.parquet
└── valuation/pe/pb/ps/ev_ebitda/ (stock valuations)

        ↓ PROCESSORS (Aggregation)

PROCESSED DATA (2nd Pass - Sector Level)
├── sector/sector_fundamental_metrics.parquet
├── sector/sector_valuation_metrics.parquet
├── sector/sector_combined_scores.parquet
└── forecast/bsc/*.parquet

        ↓ WEBAPP (Visualization)

Streamlit Dashboards
```

---

## 12. EXECUTION FLOW (Daily Pipeline)

```
run_all_daily_updates.py (MASTER)
    ├─→ Step 1: daily_ohlcv_update.py
    │   └─ Output: OHLCV_mktcap.parquet
    │
    ├─→ Step 2: daily_ta_complete.py
    │   └─ Output: technical/basic_data.parquet, alerts/, breadth/
    │
    ├─→ Step 3: daily_macro_commodity.py
    │   └─ Output: macro_commodity_unified.parquet
    │
    ├─→ Step 4: daily_valuation.py
    │   └─ Output: valuation/pe/pb/ps/ev_ebitda/
    │
    ├─→ Step 5: daily_sector_analysis.py
    │   ├─ Runs: SectorProcessor
    │       ├─→ FAAggregator
    │       ├─→ TAAggregator
    │       ├─→ FAScorer
    │       ├─→ TAScorer
    │       └─→ SignalGenerator
    │   └─ Output: sector_*.parquet
    │
    └─→ Step 6: daily_bsc_forecast.py
        └─ Output: forecast/bsc/*.parquet

    ↓ Final: Data Integrity Report
```

---

## 13. UNRESOLVED QUESTIONS

1. **data_mapping registry location** - Where is the actual data_mapping.json or equivalent registry stored?
2. **AI formula generation** - Is the AI-powered formula generation currently in use or experimental only?
3. **BSC forecast source** - Is the Excel file updated manually or pulled from API?
4. **Sector weighting** - Where are FA/TA weight configurations stored (for sector scoring)?

---

**Total Processors:** 80+ files across 12 modules
**Main Pipeline:** 6 steps, ~45 minutes total execution
**Active Calculators:** 4 entity types (company, bank, insurance, security)
**Valuation Metrics:** PE, PB, P/S, EV/EBITDA (individual + VN-Index)
**Output Format:** Parquet (compressed with snappy)
