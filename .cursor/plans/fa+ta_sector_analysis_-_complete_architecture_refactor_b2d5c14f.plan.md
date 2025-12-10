---
name: FA+TA Sector Analysis - Complete Architecture Refactor
overview: |
  Refactor toàn bộ architecture sector analysis để tạo một hệ thống thống nhất, module hóa, và dễ mở rộng.
  Tạo single source of truth cho FA+TA data, design modular components, và implement configuration-driven approach.

  **CURRENT STATUS: ~40% Complete**
  - ✅ Foundation: Registries, calculators, transformers, schemas (100%)
  - ❌ Orchestration: SectorAnalyzer, UnifiedDataService (0%)
  - ❌ Configuration: Weights, indicators config (0%)
  - ❌ Dashboard: Unified sector analysis UI (20%)
todos:
  - id: audit-existing-components
    content: Audit và document tất cả existing components đã có sẵn
    status: completed
  - id: fa-aggregator
    content: Triển khai FADataAggregator class để aggregate fundamental metrics
    status: pending
  - id: ta-aggregator
    content: Triển khai TADataAggregator class để aggregate technical indicators
    status: pending
  - id: sector-analyzer-core
    content: Triển khai SectorAnalyzer class làm main orchestrator (sử dụng existing registries)
    status: pending
  - id: unified-data-service
    content: Triển khai UnifiedDataService class (integrate với existing calculators)
    status: pending
  - id: unified-schema
    content: Tạo unified sector schema (merge existing fundamental/technical/valuation schemas)
    status: pending
  - id: config-system
    content: Tạo CONFIG/sector_analysis/ với default_weights.json và indicators_config.json
    status: pending
  - id: fa-ta-combiner
    content: Triển khai FATACombiner class để merge FA+TA scores
    status: pending
  - id: signal-generator
    content: Triển khai SignalGenerator class cho trading signals
    status: pending
  - id: cache-manager
    content: Triển khai CacheManager cho performance optimization
    status: pending
  - id: modular-dashboard
    content: Xây dựng sector_analysis_dashboard.py với tabs (Overview, FA, TA, Combined)
    status: pending
  - id: sector-charts
    content: Tạo WEBAPP/components/sector_charts.py (modular chart components)
    status: pending
  - id: sector-service
    content: Tạo WEBAPP/services/sector_service.py (single API cho sector data)
    status: pending
  - id: migration-scripts
    content: Tạo migration scripts để generate unified sector parquet files
    status: pending
  - id: unified-tests
    content: Tạo comprehensive test suite cho unified system
    status: pending
---

# FA+TA SECTOR ANALYSIS - COMPLETE ARCHITECTURE REFACTOR

## 1. TỔNG TRẠNG HIỆN TẠI

### 1.1 Vấn đề hiện tại

- **FA và TA tách biệt**: Không có cái nhìn tổng quan khi xem sector
- **Data trùng lặp**: Fundamental và technical data lưu ở nhiều nơi khác nhau
- **Code bị phân tán**: Logic calculation lẫn lẫn với data loading
- **Khó thể debug**: Không có centralized error handling
- **Khó thể tùy chỉnh**: Weights và indicators hardcode
- **Khó thể mở rộng**: Adding new indicators cần sửa nhiều files

### 1.2 Mục tiêu cần đạt

1. **Single Source of Truth**: Một API duy nhất để query tất cả FA và TA data
2. **Unified Data Model**: Schema chuẩn cho cả FA và TA data
3. **Modular Components**: Components có thể tái sử dụng
4. **Configuration-Driven**: Weights và features có thể tùy chỉnh qua UI
5. **Clear Data Flow**: Pipeline rõ ràng từ Raw → Processing → Storage
6. **Easy Testing**: Mỗi component có thể test độc lập
7. **Performance Optimization**: Caching và batch processing
8. **Vietnam Market Specific**: Indicators đặc thù cho thị trường Việt Nam

---

## 1.3 EXISTING COMPONENTS AUDIT (✅ 40% Complete)

### ✅ **COMPLETED COMPONENTS** (Có sẵn và hoạt động tốt)

#### **A. Registries & Mappers** (100% Complete)

| Component | File Path | Status | Lines | Capabilities |

|-----------|-----------|--------|-------|--------------|

| **SectorRegistry** | `PROCESSORS/core/registries/sector_lookup.py` | ✅ Complete | 1,661 | 457 tickers × 19 sectors × 4 entity types |

| **MetricRegistry** | `DATA/metadata/metric_registry.json` | ✅ Complete | 2,099 metrics | Vietnamese → English metric mapping |

| **UnifiedTickerMapper** | `PROCESSORS/core/shared/unified_mapper.py` | ✅ Complete | 504 | Ticker info, peers, metric validation |

**Usage Examples:**

```python
# Get sector info
from PROCESSORS.core.registries import SectorRegistry
registry = SectorRegistry()
sector_info = registry.get_sector("Ngân hàng")  # Returns all bank tickers

# Unified mapper (MUST USE for new features)
from PROCESSORS.core.shared import UnifiedTickerMapper
mapper = UnifiedTickerMapper()
info = mapper.get_complete_info("ACB")  # Complete ticker information
peers = mapper.get_peer_tickers("ACB")  # Same sector tickers
```

#### **B. Data Models** (80% Complete)

| Model | File | Status | Description |

|-------|------|--------|-------------|

| **OHLCVBase** | `WEBAPP/core/models/data_models.py` | ✅ | Price & volume data |

| **FundamentalBase** | `WEBAPP/core/models/data_models.py` | ✅ | Financial statements |

| **BankMetrics** | `WEBAPP/core/models/data_models.py` | ✅ | Bank-specific metrics |

| **CompanyMetrics** | `WEBAPP/core/models/data_models.py` | ✅ | Company metrics |

| **TechnicalIndicators** | `WEBAPP/core/models/data_models.py` | ✅ | MA, RSI, MACD, Bollinger |

| **ValuationMetrics** | `WEBAPP/core/models/data_models.py` | ✅ | PE, PB, EV/EBITDA |

**Missing Models:**

- ❌ `SectorData` - Unified FA+TA container
- ❌ `SectorMetrics` - Aggregated sector metrics
- ❌ `SectorSignals` - Combined trading signals
- ❌ `SectorCompositeScore` - Unified scoring

#### **C. Schemas** (70% Complete)

| Schema | File | Status | Size |

|--------|------|--------|------|

| **OHLCV Schema** | `config/schemas/data/ohlcv_schema.json` | ✅ | 2.1KB |

| **Fundamental Schema** | `config/schemas/data/fundamental_schema.json` | ✅ | 7.4KB |

| **Technical Schema** | `config/schemas/data/technical_schema.json` | ✅ | 8.1KB |

| **Valuation Schema** | `config/schemas/data/valuation_calculated_schema.json` | ✅ | 8.6KB |

| **Master Schema** | `config/schemas/master_schema.json` | ✅ | 5.9KB |

**Missing:**

- ❌ `DATA/schemas/unified/sector_schema.json` - Unified FA+TA sector schema

#### **D. Financial Calculators** (100% Complete - Phase 0.2)

| Calculator | File | Status | Purpose |

|------------|------|--------|---------|

| **BaseFinancialCalculator** | `PROCESSORS/fundamental/calculators/` | ✅ | Abstract base |

| **CompanyFinancialCalculator** | `PROCESSORS/fundamental/calculators/company_calculator.py` | ✅ | Company metrics |

| **BankFinancialCalculator** | `PROCESSORS/fundamental/calculators/bank_calculator.py` | ✅ | Bank metrics (NIM, CIR, NPL) |

| **InsuranceFinancialCalculator** | `PROCESSORS/fundamental/calculators/insurance_calculator.py` | ✅ | Insurance metrics |

| **SecurityFinancialCalculator** | `PROCESSORS/fundamental/calculators/security_calculator.py` | ✅ | Securities metrics |

**Can Reuse:** All calculators output standardized parquet files ready for aggregation.

#### **E. Transformers Layer** (100% Complete - Phase 0.4)

| Component | File | Status | Functions |

|-----------|------|--------|-----------|

| **Financial Formulas** | `PROCESSORS/transformers/financial/formulas.py` | ✅ Complete | 30+ pure functions |

**Available Functions:**

- Utilities: `safe_divide`, `convert_to_billions`, `percentage_change`
- Margins: `gross_margin`, `net_margin`, `ebit_margin`, `ebitda_margin`
- Profitability: `roe`, `roa`, `roaa`, `roea`, `nim`, `cir`, `npl_ratio`
- Growth: `qoq_growth`, `yoy_growth`, `cagr`
- Valuation: `pe_ratio`, `pb_ratio`, `ev_ebitda`

**Usage:**

```python
from PROCESSORS.transformers.financial import roe, roa, gross_margin

company_roe = roe(net_income=15.0, total_equity=200.0)  # Returns 7.5
```

#### **F. Technical Indicators** (100% Complete)

| Processor | File | Status | Indicators |

|-----------|------|--------|------------|

| **TechnicalProcessor** | `PROCESSORS/technical/indicators/technical_processor.py` | ✅ | MA, EMA, RSI, MACD, Bollinger, ATR |

| **MarketBreadth** | `PROCESSORS/technical/indicators/market_breadth_processor.py` | ✅ | Advance/Decline, breadth |

| **StockScreener** | `PROCESSORS/technical/indicators/stock_screener.py` | ✅ | Technical screening |

#### **G. Valuation Calculators** (100% Complete)

| Calculator | File | Status | Output |

|------------|------|--------|--------|

| **PE Calculator** | `PROCESSORS/valuation/core/historical_pe_calculator.py` | ✅ | P/E ratios |

| **PB Calculator** | `PROCESSORS/valuation/core/historical_pb_calculator.py` | ✅ | P/B ratios |

| **EV/EBITDA Calculator** | `PROCESSORS/valuation/core/historical_ev_ebitda_calculator.py` | ✅ | EV/EBITDA |

| **Sector PE** | `PROCESSORS/valuation/core/sector_pe_calculator.py` | ✅ | Sector-level PE |

#### **H. Existing Dashboard** (20% Complete)

| Dashboard | File | Status | Coverage |

|-----------|------|--------|----------|

| **Valuation Sector Dashboard** | `WEBAPP/pages/valuation_sector_dashboard.py` | ⚠️ Partial | PE-only, no FA/TA integration |

**Current Features:**

- Load sector PE data (latest + historical)
- Display PE statistics (min, max, median, quartiles)
- Show PE trends by sector
- 15-minute cache

**Missing:**

- ❌ Fundamental analysis metrics
- ❌ Technical analysis integration
- ❌ Combined FA+TA scoring
- ❌ Interactive weight customization
- ❌ Multi-tab interface (Overview, FA, TA, Combined)

---

### ❌ **MISSING COMPONENTS** (Cần implement - 60%)

#### **A. Orchestration Layer** (0% Complete)

| Component | Target File | Status | Purpose |

|-----------|-------------|--------|---------|

| **SectorAnalyzer** | `PROCESSORS/sector_analysis/sector_analyzer.py` | ❌ Missing | Main orchestrator |

| **UnifiedDataService** | `PROCESSORS/sector_analysis/unified_data_service.py` | ❌ Missing | Single data API |

| **FADataAggregator** | `PROCESSORS/sector_analysis/fa_aggregator.py` | ❌ Missing | Aggregate fundamental metrics |

| **TADataAggregator** | `PROCESSORS/sector_analysis/ta_aggregator.py` | ❌ Missing | Aggregate technical metrics |

| **FATACombiner** | `PROCESSORS/sector_analysis/fa_ta_combiner.py` | ❌ Missing | Merge FA+TA scores |

| **SignalGenerator** | `PROCESSORS/sector_analysis/signal_generator.py` | ❌ Missing | Trading signals |

**Estimated LOC:** 2,500-3,500 lines total

#### **B. Configuration System** (0% Complete)

| Component | Target File | Status | Purpose |

|-----------|-------------|--------|---------|

| **Default Weights** | `config/sector_analysis/default_weights.json` | ❌ Missing | FA/TA weight defaults |

| **Indicators Config** | `config/sector_analysis/indicators_config.json` | ❌ Missing | Available indicators |

| **User Preferences** | `config/sector_analysis/user_preferences.json` | ❌ Missing | User customizations |

| **ConfigManager** | `config/sector_analysis/config_manager.py` | ❌ Missing | Config management class |

**Estimated LOC:** 300-500 lines

#### **C. Dashboard Components** (0% Complete)

| Component | Target File | Status | Purpose |

|-----------|-------------|--------|---------|

| **Sector Analysis Dashboard** | `WEBAPP/pages/sector_analysis_dashboard.py` | ❌ Missing | Main dashboard (replace valuation_sector_dashboard) |

| **Sector Charts** | `WEBAPP/components/sector_charts.py` | ❌ Missing | Modular chart components |

| **Unified Tables** | `WEBAPP/components/unified_tables.py` | ❌ Missing | Data tables |

| **Insights Panel** | `WEBAPP/components/insights_panel.py` | ❌ Missing | AI-like insights |

| **Sector Service** | `WEBAPP/services/sector_service.py` | ❌ Missing | Single API for sector data |

**Estimated LOC:** 1,500-2,000 lines

#### **D. Data Storage** (0% Complete)

| Storage | Target Path | Status | Purpose |

|---------|-------------|--------|---------|

| **Latest Unified Data** | `DATA/processed/unified/sector/latest/sector_data.parquet` | ❌ Missing | Latest unified FA+TA |

| **Sector Metrics** | `DATA/processed/unified/sector/latest/sector_metrics.parquet` | ❌ Missing | Aggregated metrics |

| **Sector Signals** | `DATA/processed/unified/sector/latest/sector_signals.parquet` | ❌ Missing | Trading signals |

| **Historical Data** | `DATA/processed/unified/sector/historical/` | ❌ Missing | Historical archive |

| **Cache** | `DATA/processed/unified/cache/computation_cache.parquet` | ❌ Missing | Performance cache |

---

### 📊 **IMPLEMENTATION COMPLETION MATRIX**

| Layer | Component | Status | Coverage |

|-------|-----------|--------|----------|

| **Foundation** | Registries (Sector, Metric, Mapper) | ✅ Complete | 100% |

| **Foundation** | Data Models (Pydantic) | ✅ Complete | 80% |

| **Foundation** | Schemas (OHLCV, FA, TA, Valuation) | ✅ Complete | 70% |

| **Processing** | Financial Calculators (4 entity types) | ✅ Complete | 100% |

| **Processing** | Transformers Layer (30+ formulas) | ✅ Complete | 100% |

| **Processing** | Technical Indicators | ✅ Complete | 100% |

| **Processing** | Valuation Calculators | ✅ Complete | 100% |

| **Orchestration** | SectorAnalyzer | ❌ Missing | 0% |

| **Orchestration** | UnifiedDataService | ❌ Missing | 0% |

| **Orchestration** | FA/TA Aggregators | ❌ Missing | 0% |

| **Orchestration** | FATACombiner | ❌ Missing | 0% |

| **Orchestration** | SignalGenerator | ❌ Missing | 0% |

| **Configuration** | Weights & Indicators Config | ❌ Missing | 0% |

| **Configuration** | ConfigManager | ❌ Missing | 0% |

| **Dashboard** | Unified Sector Dashboard | ❌ Missing | 0% |

| **Dashboard** | Modular Components | ❌ Missing | 0% |

| **Dashboard** | Sector Service | ❌ Missing | 0% |

| **Storage** | Unified Data Files | ❌ Missing | 0% |

**OVERALL COMPLETION: ~40%**

---

### 🎯 **KEY INTEGRATION POINTS**

#### **1. Use Existing Registries** (MUST DO)

```python
# ✅ CORRECT: Use UnifiedTickerMapper for ticker operations
from PROCESSORS.core.shared import UnifiedTickerMapper

mapper = UnifiedTickerMapper()
sector_tickers = mapper.get_peer_tickers("ACB")  # Get all banking tickers
entity_type = mapper.get_complete_info("ACB")["entity_type"]  # "BANK"
```

❌ **DON'T**: Hardcode sector mappings or duplicate registry logic

#### **2. Leverage Existing Calculators** (REUSE)

```python
# ✅ CORRECT: Load existing calculated results
import pandas as pd

# Fundamental data already calculated
company_metrics = pd.read_parquet("DATA/processed/fundamental/company/company_financial_metrics.parquet")
bank_metrics = pd.read_parquet("DATA/processed/fundamental/bank/bank_financial_metrics.parquet")

# Technical data already calculated
technical_data = pd.read_parquet("DATA/processed/technical/basic_data.parquet")
```

❌ **DON'T**: Re-calculate metrics from raw data

#### **3. Use Transformer Functions** (PURE FUNCTIONS)

```python
# ✅ CORRECT: Use existing formulas
from PROCESSORS.transformers.financial import roe, gross_margin, yoy_growth

# Calculate additional metrics
sector_avg_roe = roe(total_net_income, total_equity)
sector_growth = yoy_growth(current_revenue, previous_revenue)
```

❌ **DON'T**: Write duplicate calculation functions

#### **4. Extend Existing Schemas** (MERGE, NOT REPLACE)

```python
# ✅ CORRECT: Merge existing schemas
import json

# Load existing schemas
with open("config/schemas/data/fundamental_schema.json") as f:
    fa_schema = json.load(f)
with open("config/schemas/data/technical_schema.json") as f:
    ta_schema = json.load(f)

# Merge into unified sector schema
sector_schema = {
    "version": "1.0",
    "fundamental": fa_schema,
    "technical": ta_schema,
    "sector_aggregates": {...}  # Add new sector-level fields
}
```

❌ **DON'T**: Create completely new schema format

---

### ⚠️ **CRITICAL DEPENDENCIES**

These existing components are **REQUIRED** for the new orchestration layer:

1. **UnifiedTickerMapper** → Used by SectorAnalyzer to get sector tickers
2. **SectorRegistry** → Used by FADataAggregator to group tickers by sector
3. **Financial Calculators** → Output data used by FADataAggregator
4. **Technical Processors** → Output data used by TADataAggregator
5. **Transformer Functions** → Used by FATACombiner for scoring calculations
6. **Existing Schemas** → Merged into unified sector schema

**Implementation Strategy:**

- ✅ Build NEW orchestration layer ON TOP of existing components
- ✅ Reference existing parquet files (don't re-process)
- ✅ Use existing registries for ticker/sector mapping
- ❌ Don't modify existing calculators
- ❌ Don't duplicate calculation logic

## 1.4 VALUATION CALCULATION FORMULAS (Reference for Metrics)

### 📐 **PE Ratio Calculation Logic**

**Reference File:** `PROCESSORS/valuation/calculators/vnindex_pe_calculator_optimized.py`

#### **Core Formula:**

```python
# VN-Index PE = Total Market Cap (billions VND) / Total TTM Earnings (billions VND)
total_market_cap = sum(market_cap) / 1e9  # Convert to billions VND
total_ttm_earnings = sum(ttm_earning_billion_vnd)
pe_ratio = total_market_cap / total_ttm_earnings
```

#### **Data Requirements:**

```python
# Input data needed for each ticker:
{
    'symbol': str,              # Ticker code
    'date': datetime,           # Trading date
    'market_cap': float,        # Market capitalization (VND)
    'ttm_earning_billion_vnd': float,  # TTM earnings (billions VND)
    'pe_ratio': float          # Individual stock PE (optional)
}
```

#### **Validation Rules:**

```python
# Valid data criteria:
valid_data = data[
    (data['market_cap'] > 0) &                     # Market cap must be positive
    (data['ttm_earning_billion_vnd'].notna()) &    # TTM earnings must exist
    (data['ttm_earning_billion_vnd'] > 0)          # TTM earnings must be positive
]
```

#### **Output Schema:**

```python
{
    'date': str,                              # YYYY-MM-DD
    'pe_ratio': float,                        # Calculated PE ratio
    'total_market_cap_billion_vnd': float,    # Sum of all market caps
    'total_ttm_earnings_billion_vnd': float,  # Sum of all TTM earnings
    'valid_symbols_count': int,               # Number of valid tickers
    'invalid_symbols_count': int,             # Number of invalid tickers
    'total_symbols_processed': int,           # Total tickers processed
    'valid_symbols': List[str],               # List of valid tickers
    'invalid_symbols': List[str]              # List of invalid tickers
}
```

#### **Advanced Features:**

**1. Symbol Filtering (Current Implementation):**

```python
# Method 1: Specify exact symbols
calc = VNIndexPECalculatorOptimized()
result = calc.calculate_vnindex_pe(
    target_date="2024-12-09",
    symbols=['VCB', 'GAS', 'VNM', 'HPG']  # Only these tickers
)

# Method 2: Exclude symbols (manual workaround)
all_symbols = calc.symbols_list
exclude = ['VIC', 'VHM', 'VPB']
filtered = [s for s in all_symbols if s not in exclude]
result = calc.calculate_vnindex_pe(
    target_date="2024-12-09",
    symbols=filtered
)
```

**2. Time Series Calculation:**

```python
# Calculate PE for date range
timeseries_df = calc.calculate_vnindex_pe_timeseries(
    start_date="2024-01-01",
    end_date="2024-12-09",
    symbols=None,  # All symbols
    frequency='daily'  # Options: 'daily', 'weekly', 'monthly'
)
```

#### **Similar Formulas for Other Metrics:**

**PB Ratio:**

```python
# Price-to-Book Ratio
total_market_cap = sum(market_cap) / 1e9
total_book_value = sum(book_value_billion_vnd)
pb_ratio = total_market_cap / total_book_value
```

**EV/EBITDA:**

```python
# Enterprise Value to EBITDA
total_enterprise_value = sum(enterprise_value) / 1e9
total_ebitda = sum(ebitda_billion_vnd)
ev_ebitda = total_enterprise_value / total_ebitda
```

**Sector PE:**

```python
# Same formula as VN-Index PE but grouped by sector
for sector in sectors:
    sector_tickers = get_tickers_by_sector(sector)
    sector_pe = calculate_pe(sector_tickers, date)
```

---

## 1.5 🚨 CRITICAL: PATH MIGRATION NEEDED (95% Files Using Wrong Paths)

### **Architecture Compliance Audit Results**

**Current Status:** Only **4.7% (2/43 files)** following v4.0.0 canonical paths!

#### **❌ WRONG PATHS (Need immediate migration)**

| Category | Count | Files Affected | Priority |

|----------|-------|----------------|----------|

| **Valuation Calculators** | 9 | PE, PB, EV_EBITDA, Sector PE, VN-Index PE | 🔴 HIGH |

| **Technical Indicators** | 6 | MA, RSI, MACD, Bollinger, Market Breadth | 🔴 HIGH |

| **Forecast Pipeline** | 1 | BSC forecast | 🔴 HIGH |

| **Macro Processor** | 1 | Macro indicators | 🔴 HIGH |

| **Pipelines** | 1 | Quarterly report | 🔴 HIGH |

| **Input Paths** | 15+ | OHLCV, fundamental readers | 🟡 MEDIUM |

**Total files needing migration:** 35 files (81.4%)

#### **Architecture Compliance:**

**Canonical v4.0.0 Paths:**

```
DATA/
├── raw/                    # Input data (READ from here)
│   ├── ohlcv/
│   ├── fundamental/csv/
│   ├── commodity/
│   └── macro/
│
└── processed/              # Output data (WRITE to here)
    ├── fundamental/
    │   ├── company/
    │   ├── bank/
    │   ├── insurance/
    │   └── security/
    ├── technical/
    ├── valuation/
    │   ├── pe/
    │   ├── pb/
    │   ├── ev_ebitda/
    │   └── sector_pe/
    ├── commodity/
    ├── macro/
    └── forecast/bsc/
```

**Current (WRONG) Paths:**

```
❌ calculated_results/valuation/pe/          # Should be: DATA/processed/valuation/pe/
❌ calculated_results/technical/             # Should be: DATA/processed/technical/
❌ calculated_results/forecast/bsc/          # Should be: DATA/processed/forecast/bsc/
❌ data_warehouse/raw/ohlcv/                 # Should be: DATA/raw/ohlcv/
❌ DATA/refined/fundamental/                 # Should be: DATA/processed/fundamental/
```

#### **Fix Strategy:**

**Global Search & Replace:**

```bash
# In all PROCESSORS/*.py files:

# Fix output paths (20 files):
calculated_results/valuation/     → DATA/processed/valuation/
calculated_results/technical/     → DATA/processed/technical/
calculated_results/forecast/bsc/  → DATA/processed/forecast/bsc/
calculated_results/macro/          → DATA/processed/macro/
DATA/refined/fundamental/          → DATA/processed/fundamental/

# Fix input paths (15+ files):
data_warehouse/raw/ohlcv/          → DATA/raw/ohlcv/
data_warehouse/raw/fundamental/    → DATA/raw/fundamental/
data_warehouse/raw/metadata/       → DATA/metadata/
```

#### **Files Requiring Updates:**

**Priority 1 (HIGH - 20 files):**

```
PROCESSORS/pipelines/quarterly_report.py
PROCESSORS/technical/indicators/technical_processor.py
PROCESSORS/technical/indicators/market_breadth_processor.py
PROCESSORS/technical/indicators/ma_screening_processor.py
PROCESSORS/technical/macro/macro_data_fetcher.py
PROCESSORS/valuation/calculators/historical_pe_calculator.py
PROCESSORS/valuation/calculators/historical_pb_calculator.py
PROCESSORS/valuation/calculators/historical_ev_ebitda_calculator.py
PROCESSORS/valuation/calculators/vnindex_pe_calculator_optimized.py
PROCESSORS/valuation/calculators/bsc_universal_pe_calculator.py
PROCESSORS/valuation/sector_pe_calculator.py
PROCESSORS/valuation/daily_update_all_valuations.py
PROCESSORS/forecast/run_bsc_auto_update.py
... (+ 7 more in valuation/core/)
```

**Priority 2 (MEDIUM - 15+ files):**

All files reading from `data_warehouse/raw/` should use `DATA/raw/`

#### **Migration Checklist:**

- [ ] **Phase 0.5: Path Migration** (NEW - 3-5 days)
  - [x] Update all output paths in PROCESSORS/ (20 files)
  - [x] Update all input paths in PROCESSORS/ (15+ files)
  - [x] Move existing data files to new locations
  - [x] Update WEBAPP/ data loaders to read from new paths
  - [ ] Test all pipelines end-to-end
  - [ ] Update documentation (CLAUDE.md, architecture docs)

**Impact:**

- Code changes: 35 files
- Data migration: ~102 parquet files need to be moved
- Testing required: All daily pipelines + quarterly pipeline
- Estimated time: 3-5 days

---

## 2. KIẾN TRÚC ARCHITECTURE MỚI

### 2.1 CẤU TRÚC CHUẨN

```
Vietnam_Dashboard_v6/
├── DATA/                            # Data Layer (Không đổi)
│   ├── raw/                        # Raw data inputs
│   │   ├── fundamental/csv/         # BCTC từ BSC
│   │   ├── market/ohlcv/           # Giá khớp lệnh
│   │   └── macro/                   # Lãi suất, tỷ giá
│   │
│   └── processed/                  # Processed data outputs
│       ├── unified/              # NEW: Unified FA+TA data
│       │   ├── sector/
│       │   │   ├── latest/
│       │   │   │   ├── sector_data.parquet       # Latest unified data
│       │   │   │   ├── sector_metrics.parquet   # Sector aggregated metrics
│       │   │   │   └── sector_signals.parquet   # Combined signals
│       │   │   └── historical/
│       │   │       ├── 2024/
│       │   │       ├── 2024-Q[1-4]/
│       │   │       └── [fa_metrics, ta_metrics, fa_trends, ta_distributions]
│       │   └── cache/
│       │           └── [computation_cache.parquet]  # Performance cache
│       │
│       ├── fundamental/            # Existing (refined)
│       ├── technical/               # Existing (enhanced)
│       └── valuation/               # Existing
│
│   └── schemas/                 # Enhanced schemas
│       ├── unified/
│       │   └── sector_schema.json      # NEW: Unified FA+TA schema
│
├── PROCESSORS/                     # Processing Layer (Enhanced)
│   ├── core/                     # Existing utilities
│   │   ├── registries/           # Metric/sector registries
│   │   ├── cache/                # Performance cache
│   │   ├── config/               # Configuration management
│   │   └── validation/            # Enhanced validation
│   │
│   ├── sector_analysis/            # NEW: Main orchestrator
│   │   ├── __init__.py
│   │   ├── sector_analyzer.py      # Single source of truth
│   │   ├── fa_aggregator.py      # FA data collection
│   │   ├── ta_aggregator.py      # TA data collection
│   │   ├── fa_ta_combiner.py    # Data combination & scoring
│   │   ├── signal_generator.py   # Buy/sell signal generation
│   │   └── visualizer.py       # Chart data preparation
│   │
│   ├── unified/                 # NEW: Unified data processing
│   │   ├── __init__.py
│   │   ├── schema_validator.py    # Validate against unified schema
│   │   ├── data_loader.py          # Load and merge FA+TA data
│   │   ├── metrics_calculator.py   # Calculate unified metrics
│   │   ├── pipeline.py            # Orchestrate data processing
│   │   └── cache_manager.py       # Performance optimization
│   │
│   ├── fundamental/             # Existing (refactored to use unified)
│   │   └── calculators/
│   │       ├── base_unified_calculator.py  # Use unified data loader
│   │       ├── [company,bank,insurance,security]_calculator.py
│   │
│   ├── technical/               # Existing (enhanced)
│   │   └── calculators/
│   │       ├── base_technical_calculator.py  # Use unified data loader
│   │       ├── ma_calculator.py      # Enhanced MA calculation
│   │       ├── rsi_calculator.py     # Enhanced RSI calculation
│   │       ├── bollinger_calculator.py  # Enhanced Bollinger Bands
│   │       └── technical_aggregator.py  # NEW: Technical data aggregation
│   │
│   └── pipelines/               # Existing (refactored)
│       ├── unified/
│       │   ├── sector_analysis_pipeline.py  # NEW: Main sector pipeline
│       │   └── cache/
│       └── unified_pipeline.py        # NEW: Unified data processing pipeline
│
│
├── WEBAPP/                      # Presentation Layer (Enhanced)
│   ├── pages/
│   │   ├── sector_analysis_dashboard.py  # NEW: Main sector analysis page
│   │   └── [existing pages...]
│   ├── components/
│   │   ├── sector_charts.py           # NEW: Modular chart components
│   │   ├── unified_tables.py       # NEW: Unified data tables
│   │   └── insights_panel.py         # NEW: AI-like insights display
│   │
│   └── services/
│       ├── sector_service.py           # NEW: Single API for sector data
│       └── [existing services...]
│
│
├── CONFIG/                       # Configuration Layer (NEW)
│   └── sector_analysis/            # NEW: Sector analysis configuration
│       ├── default_weights.json     # Default FA/TA weights
│       ├── indicators_config.json   # Available indicators configuration
│       └── user_preferences.json    # User customizations
│
│
└── TESTS/                        # Test Infrastructure (NEW)
    ├── sector_analysis/
    │   ├── test_unified_schema.py
    │   ├── test_sector_analyzer.py
    │   ├── test_fa_aggregator.py
    │   └── test_ta_aggregator.py
    │
    └── integration/
        ├── test_end_to_end_pipeline.py
        └── test_sector_dashboard.py
```

## 3. UNIFIED DATA MODEL (Enhanced)

### 3.1 Unified Schema

```json
{
  "version": "1.0",
  "entities": {
    "companies": {
      "attributes": {
        "ticker": {"type": "string", "description": "Stock ticker"},
        "company_name": {"type": "string", "description": "Full company name"},
        "sector": {"type": "string", "description": "Industry sector"},
        "entity_type": {"type": "string", "description": "Company/Bank/Insurance/Security"}
      },
      "financial_metrics": {
        "period": {"type": "string", "description": "Reporting period (YYYY-QX)"},
        "revenue": {"type": "float", "description": "Total revenue (VND)"},
        "gross_profit": {"type": "float", "description": "Gross profit (VND)"},
        "net_income": {"type": "float", "description": "Net income after tax (VND)"},
        "gross_margin": {"type": "float", "description": "Gross profit margin (%)"},
        "operating_margin": {"type": "float", "description": "Operating profit margin (%)"},
        "sga": {"type": "float", "description": "SG&A expense (VND)"},
        "sga_ratio": {"type": "float", "description": "SG&A to revenue ratio (%)"},
        "ebit": {"type": "float", "description": "EBIT (VND)"},
        "ebitda": {"type": "float", "description": "EBITDA (VND)"},
        "ebitda_margin": {"type": "float", "description": "EBITDA margin (%)"},
        "roa": {"type": "float", "description": "Return on Assets (%)"},
        "roa": {"type": "float", "description": "Return on Equity (%)"},
        "total_assets": {"type": "float", "description": "Total assets (VND)"},
        "total_equity": {"type": "float", "description": "Total equity (VND)"},
        "debt_to_equity": {"type": "float", "description": "Debt to equity ratio"},
        "pe_ratio": {"type": "float", "description": "PE ratio"},
        "pb_ratio": {"type": "float", "description": "PB ratio"},
        "eps": {"type": "float", "description": "Earnings per share (VND)"},
        "bvps": {"type": "float", "description": "Book value per share (VND)"}
      }
    },
    "technical_metrics": {
      "price": {"type": "float", "description": "Closing price (VND)"},
      "volume": {"type": "float", "description": "Trading volume (shares)"},
      "trading_value": {"type": "float", "description": "Trading value (VND)"},
      "ma": {
        "ma20": {"type": "float", "description": "20-day moving average"},
        "ma50": {"type": "float", "description": "50-day moving average"},
        "ma100": {"type": "float", "description": "100-day moving average"},
        "ma200": {"type": "float", "description": "200-day moving average"}
      },
      "rsi": {"type": "float", "description": "14-day RSI"},
      "macd": {
        "macd": {"type": "float", "description": "MACD line"},
        "macd_signal": {"type": "float", "description": "MACD signal"},
        "macd_histogram": {"type": "object", "description": "MACD histogram"}
      },
      "bollinger": {
        "upper_band": {"type": "float", "description": "Upper Bollinger Band"},
        "middle_band": {"type": "float", "description": "Middle Bollinger Band"},
        "lower_band": {"type": "float", "description": "Lower Bollinger Band"},
        "bandwidth": {"type": "float", "description": "Bollinger Band width"},
        "percent_b": {"type": "float", "description": "Percent B (position relative to bands)"}
      },
      "atr": {"type": "float", "description": "Average True Range"}
      },
      "momentum_indicators": {
        "momentum_score": {"type": "float", "description": "Momentum score (0-1)"},
        "strength_score": {"type": "float", "description": "Strength score (0-1)"},
        "trend": {"type": "string", "description": "Trend direction (Up/Down/Sideways)"}
      },
      "sector_indicators": {
        "ma_alignment_count": {"type": "integer", "description": "Count of stocks above MA20"},
        "rsi_alignment_count": {"type": "integer", "description": "Count of stocks in RSI zones"},
        "volume_distribution": {"type": "object", "description": "Volume distribution by decile"},
        "pe_distribution": {"type": "object", "description": "PE distribution by quartile"},
        "sector_strength_score": {"type": "float", "description": "Overall sector strength score"},
        "sector_momentum": {"type": "float", "description": "Sector momentum score"},
        "rotation_signal": {"type": "string", "description": "Sector rotation signal"}
      }
    },
    "combined_metrics": {
      "fundamental_score": {"type": "float", "description": "Combined fundamental score (0-100)"},
      "technical_score": {"type": "float", "description": "Combined technical score (0-100)"},
      "composite_score": {"type": "float", "description": "Overall composite score (0-100)"},
      "rank": {"type": "integer", "description": "Rank within sector (1=best)"},
      "signal": {"type": "string", "description": "Trading signal (Buy/Sell/Hold)"},
      "confidence": {"type": "float", "description": "Signal confidence level (0-1)"}
    }
  }
}
```

## 4. CORE COMPONENTS (NEW)

### 4.1 SectorAnalyzer - Single Source of Truth

```python
class SectorAnalyzer:
    """Main orchestrator for unified sector analysis"""
    
    def __init__(self):
        self.fa_service = FinancialAnalysisService()
        self.ta_service = TechnicalAnalysisService()
        self.unified_service = UnifiedDataService()
        self.config = SectorAnalysisConfig()
        
    def analyze_sector(self, sector: str, timeframe: str = "latest"):
        """
        Complete sector analysis - returns unified FA+TA results
        """
        # 1. Load unified data
        data = self.unified_service.load_sector_data(sector, timeframe)
        
        # 2. Calculate metrics
        metrics = self.unified_service.calculate_sector_metrics(data)
        
        # 3. Generate insights
        insights = self.unified_service.generate_insights(data, metrics)
        
        # 4. Prepare visualizations
        charts = self.unified_service.prepare_visualizations(data, metrics)
        
        return {
            'sector': sector,
            'timeframe': timeframe,
            'data': data,
            'metrics': metrics,
            'insights': insights,
            'charts': charts,
            'last_updated': datetime.now().isoformat()
        }
    
    def get_available_sectors(self) -> List[str]:
        """Get list of sectors with data"""
        return self.unified_service.get_available_sectors()
    
    def get_sector_tickers(self, sector: str) -> List[str]:
        """Get all tickers in a sector"""
        return self.unified_service.get_sector_tickers(sector)
    
    def compare_sectors(self, sectors: List[str], timeframe: str = "latest"):
        """Compare multiple sectors"""
        return self.unified_service.compare_sectors(sectors, timeframe)
```

### 4.2 UnifiedDataService - Single Data API

```python
class UnifiedDataService:
    """Single source of truth for all FA+TA data"""
    
    def __init__(self):
        self.data_loader = DataLoader()
        self.schema_validator = SchemaValidator()
        self.metrics_calculator = MetricsCalculator()
        self.cache_manager = CacheManager()
        
    def load_sector_data(self, sector: str, timeframe: str):
        """Load all available data for a sector"""
        # 1. Load fundamental data
        fa_data = self.data_loader.load_financial_data(sector, timeframe)
        
        # 2. Load technical data
        ta_data = self.data_loader.load_technical_data(sector, timeframe)
        
        # 3. Validate and merge
        merged_data = self.schema_validator.validate_and_merge(fa_data, ta_data)
        
        # 4. Apply caching
        cache_key = f"{sector}_{timeframe}_{datetime.now().strftime('%Y%m%d')}"
        cached_result = self.cache_manager.get(cache_key)
        
        if cached_result is None:
            # Calculate metrics
            metrics = self.metrics_calculator.calculate_all(merged_data)
            self.cache_manager.set(cache_key, {
                'data': merged_data,
                'metrics': metrics
            })
        
        return self.cache_manager.get(cache_key)['data']
    
    def calculate_sector_metrics(self, data):
        """Calculate all metrics for sector data"""
        return self.metrics_calculator.calculate_all(data)
    
    def generate_insights(self, data, metrics):
        """Generate AI-like insights"""
        return InsightsGenerator().generate(data, metrics)
    
    def prepare_visualizations(self, data, metrics):
        """Prepare data for all chart types"""
        return ChartDataPreparer().prepare(data, metrics)
    
    def get_available_sectors(self):
        """Get sectors that have both FA and TA data"""
        return self.data_loader.get_available_sectors()
    
    def get_sector_tickers(self, sector):
        """Get all tickers for a sector"""
        return self.data_loader.get_sector_tickers(sector)
```

### 4.3 Modular Chart Components

```python
class SectorChartBuilder:
    """Build different chart types with unified data"""
    
    def __init__(self, chart_type: str):
        self.chart_type = chart_type
        
    def build_trend_chart(self, data, metrics):
        """Build FA trend charts"""
        return self._build_line_chart(data, metrics.trends)
        
    def build_technical_distribution_chart(self, data, metrics):
        """Build TA distribution charts"""
        return self._build_distribution_chart(data, metrics.technical_distributions)
        
    def build_composite_heatmap(self, data, metrics):
        """Build composite score heatmap"""
        return self._build_heatmap(data, metrics.composite_scores)
        
    def build_signal_table(self, data, metrics):
        """Build trading signals table"""
        return self._build_table(data, metrics.signals)
```

## 5. CONFIGURATION-DRIVEN APPROACH

### 5.1 Configuration System

```json
{
  "fa_weights": {
    "revenue_growth": 0.25,
    "gross_margin": 0.20,
    "roa": 0.25,
    "debt_to_equity": 0.15
    "profitability_trends": 0.20
  },
  "ta_weights": {
    "ma_alignment": 0.25,
    "rsi_momentum": 0.20,
    "volume_trend": 0.15,
    "sector_strength": 0.30,
    "momentum": 0.10
  },
  "composite_weights": {
    "fundamental": 0.60,
    "technical": 0.40,
    "combined": 1.0
  },
  "indicators": {
    "enabled": {
      "ma_20": true,
      "ma_50": true,
      "ma_100": true,
      "ma_200": true,
      "rsi": true,
      "macd": true,
      "bollinger": true,
      "atr": true,
      "momentum": true,
      "sector_strength": true,
      "sector_rotation": true
    },
    "alerts": {
      "price_movement": true,
      "volume_spike": true,
      "rsi_divergence": true,
      "ma_crossover": true,
      "sector_momentum_change": true
    }
  },
  "display": {
    "default_timeframe": "latest",
    "chart_height": 500,
    "chart_colors": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"],
    "show_data_labels": true,
    "animate_transitions": true
  }
}
```

### 5.2 Dynamic Configuration UI

```python
# CONFIG/sector_analysis_config_manager.py
class ConfigManager:
    """Manage user preferences for sector analysis"""
    
    def __init__(self):
        self.config_file = "CONFIG/sector_analysis/user_preferences.json"
        self.default_config = self.load_default_config()
        
    def load_user_config(self):
        """Load user customizations"""
        # User can override default weights
        return self._merge_configs(self.default_config, self._load_user_overrides())
    
    def save_user_config(self, config):
        """Save user preferences"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def get_active_config(self):
        """Get currently active configuration"""
        user_overrides = self._load_user_overrides()
        return self._merge_configs(self.default_config, user_overrides)
```

## 6. IMPLEMENTATION PHASES (UPDATED - Based on 40% Completion)

### ✅ Phase 0: Foundation (COMPLETED - v4.0.0)

**Status:** 100% Complete

**What's Already Done:**

1. ✅ SectorRegistry (457 tickers × 19 sectors × 4 entity types)
2. ✅ MetricRegistry (2,099 metrics mapped)
3. ✅ UnifiedTickerMapper (single API for ticker info)
4. ✅ Data Models (Pydantic models for all entities)
5. ✅ Schemas (OHLCV, Fundamental, Technical, Valuation)
6. ✅ Financial Calculators (4 entity types)
7. ✅ Transformers Layer (30+ pure functions)
8. ✅ Technical Indicators (MA, RSI, MACD, Bollinger, ATR)
9. ✅ Valuation Calculators (PE, PB, EV/EBITDA, Sector PE)

---

### 🔨 Phase 1: Orchestration Layer (Week 1-2) - **IN PROGRESS**

**Goal:** Build orchestrator classes that aggregate existing data

#### Week 1: Data Aggregators (3 files, ~900 LOC)

1. **FADataAggregator** (`PROCESSORS/sector_analysis/fa_aggregator.py`) - 300 LOC

   - Load existing fundamental parquet files
   - Group by sector using SectorRegistry
   - Calculate sector aggregates (median, mean, quartiles)

2. **TADataAggregator** (`PROCESSORS/sector_analysis/ta_aggregator.py`) - 300 LOC

   - Load existing technical parquet files
   - Group by sector
   - Calculate sector distributions

3. **Unified Sector Schema** (`DATA/schemas/unified/sector_schema.json`)

   - Merge existing fundamental/technical/valuation schemas

#### Week 2: Combiners & Orchestrator (3 files, ~1,050 LOC)

4. **FATACombiner** (`PROCESSORS/sector_analysis/fa_ta_combiner.py`) - 400 LOC

   - Merge FA + TA by ticker
   - Apply weights (FA: 60%, TA: 40%)
   - Calculate composite scores

5. **SignalGenerator** (`PROCESSORS/sector_analysis/signal_generator.py`) - 250 LOC

   - Generate Buy/Sell/Hold signals
   - Calculate confidence levels

6. **SectorAnalyzer** (`PROCESSORS/sector_analysis/sector_analyzer.py`) - 400 LOC

   - Main orchestrator
   - Use UnifiedTickerMapper
   - Call all aggregators/combiners

---

### 🎨 Phase 2: Configuration System (Week 3) - **PENDING**

**Goal:** Configuration-driven weights and indicators

**Files to Create:** (4 files, ~500 LOC)

1. `config/sector_analysis/default_weights.json`
2. `config/sector_analysis/indicators_config.json`
3. `config/sector_analysis/user_preferences.json`
4. `config/sector_analysis/config_manager.py` - 200 LOC

---

### 🎯 Phase 3: Dashboard & Service (Week 4-5) - **PENDING**

**Goal:** Unified sector dashboard with modular components

**Files to Create:** (5 files, ~1,700 LOC)

1. **SectorService** (`WEBAPP/services/sector_service.py`) - 300 LOC
2. **SectorCharts** (`WEBAPP/components/sector_charts.py`) - 400 LOC
3. **UnifiedTables** (`WEBAPP/components/unified_tables.py`) - 200 LOC
4. **Sector Dashboard** (`WEBAPP/pages/sector_analysis_dashboard.py`) - 600 LOC

   - Tab 1: Overview
   - Tab 2: Fundamental Analysis
   - Tab 3: Technical Analysis
   - Tab 4: Combined Scoring

5. **InsightsPanel** (`WEBAPP/components/insights_panel.py`) - 200 LOC

---

### 🚀 Phase 4: Data Storage & Migration (Week 6) - **PENDING**

**Goal:** Generate unified sector parquet files

**Files to Create:** (3 files, ~700 LOC)

1. **Migration Script** (`PROCESSORS/sector_analysis/migrations/generate_unified_data.py`) - 300 LOC
2. **CacheManager** (`PROCESSORS/sector_analysis/cache_manager.py`) - 200 LOC
3. **Unified Pipeline** (`PROCESSORS/pipelines/unified_sector_pipeline.py`) - 200 LOC

---

### ✅ Phase 5: Testing (Week 7) - **PENDING**

**Goal:** Comprehensive test coverage

**Files to Create:**

- `TESTS/sector_analysis/test_fa_aggregator.py`
- `TESTS/sector_analysis/test_ta_aggregator.py`
- `TESTS/sector_analysis/test_fa_ta_combiner.py`
- `TESTS/sector_analysis/test_sector_analyzer.py`
- `TESTS/integration/test_end_to_end_pipeline.py`

---

### 🎉 Phase 6: Deployment (Week 8) - **PENDING**

**Goal:** Production deployment

**Tasks:**

1. Performance profiling
2. Production deployment
3. User feedback collection

---

### 📊 **REVISED TIMELINE SUMMARY**

| Phase | Week | Status | Components | LOC | Completion |

|-------|------|--------|------------|-----|------------|

| Phase 0 | Pre-work | ✅ Complete | Foundation | - | 100% |

| Phase 1 | 1-2 | 🔨 In Progress | Orchestrators | 2,000 | 0% |

| Phase 2 | 3 | ⏳ Pending | Configuration | 500 | 0% |

| Phase 3 | 4-5 | ⏳ Pending | Dashboard | 1,700 | 0% |

| Phase 4 | 6 | ⏳ Pending | Data Storage | 700 | 0% |

| Phase 5 | 7 | ⏳ Pending | Testing | - | 0% |

| Phase 6 | 8 | ⏳ Pending | Deployment | - | 0% |

**Total Estimated LOC:** ~4,900 lines

**Timeline:** 8 weeks (40% → 100%)

**Current:** 40% complete

## 7. KEY BENEFITS

### 7.1 For Developers

- **Single Responsibility**: Mỗi class có nhiệm vụ rõ ràng
- **Easy Testing**: Có thể unit test từng component
- **No Code Duplication**: Unified data model eliminates duplication
- **Type Safety**: Full type hints và validation
- **Performance**: Caching và batch processing

### 7.2 For Users

- **Complete View**: FA và TA trong một interface
- **Customizable**: Weights và indicators có thể điều chỉnh
- **Rich Insights**: AI-like analysis từ unified data
- **Real-time**: Updates tự động cho data

### 7.3 For Business

- **Better Decisions**: Combined FA+TA scoring cho ranking tốt hơn
- **Risk Management**: Health indicators cho FA, timing indicators cho TA
- **Performance Tracking**: Metrics để evaluate chiến lược hiệu quả

### 7.4 Vietnam Market Specific

- **Sector Rotation**: Detect khi dòng tiền chuyển giữa các ngành
- **State-owned Adjustment**: Adjust scores cho các cổ phiếu nhà nước
- **Market Breadth Enhancement**: Comprehensive market analysis
- **Custom Indicators**: VN-specific momentum và strength scores

## 8. MIGRATION PATH

### 8.1 Phased Approach

```bash
# Week 1: Foundation
mv PROCESSORS/fundamental/ PROCESSORS/fundamental_legacy/
mv PROCESSORS/technical/ PROCESSORS/technical_legacy/
# Create PROCESSORS/unified/ with all new logic

# Week 2: Integration
# Implement data migration scripts
python PROCESSORS/unified/migrations/migrate_to_unified.py --from-legacy --to-unified

# Week 3: Dashboard
# Update existing pages to use new unified API
python scripts/update_dashboard_for_unified.py --apply-to-all-pages

# Week 4: Testing
# Run comprehensive test suite
python TESTS/integration/run_all_tests.py
```

### 8.2 Backward Compatibility

- Keep old APIs working during transition
- Provide migration scripts to convert existing data
- Gradual rollout of new features

### 8.3 Rollout Strategy

1. **Phase 1**: Internal testing và validation
2. **Phase 2**: Beta testing với selected users
3. **Phase 3**: Full production release

## 9. SUCCESS CRITERIA

### 9.1 Technical Metrics

- ✅ **Architecture Score**: 100% (modular, testable, maintainable)
- ✅ **Performance Score**: < 2s load time cho sector analysis
- ✅ **Coverage Score**: 95% (all sectors covered)
- ✅ **Extensibility Score**: 90% (easy to add new indicators)

### 9.2 User Experience Metrics

- ✅ **Load Time**: < 3s cho sector dashboard
- ✅ **Interaction Time**: < 1s cho chart interactions
- ✅ **Customization**: 100% (all features configurable)
- ✅ **Insight Quality**: AI-like insights với actionable recommendations

### 9.3 Business Value Metrics

- ✅ **Decision Quality**: 25% improvement in ranking accuracy
- ✅ **Risk Reduction**: Better risk-adjusted returns với combined FA+TA
- ✅ **Market Understanding**: Comprehensive sector health monitoring

This architecture provides a complete, maintainable, and extensible system for FA+TA sector analysis that addresses all your concerns while being easy to develop and customize.

```

### 10. FILES TO MODIFY/CREATE

### 10.1 Core Files (Priority 1)
1. `PROCESSORS/unified/__init__.py`
2. `PROCESSORS/unified/sector_analyzer.py` (300-400 lines)
3. `PROCESSORS/unified/unified_data_service.py` (400-600 lines)
4. `PROCESSORS/unified/schema_validator.py` (200-300 lines)
5. `PROCESSORS/unified/metrics_calculator.py` (500-800 lines)
6. `DATA/schemas/unified/sector_schema.json`

### 10.2 Configuration Files (Priority 2)
1. `CONFIG/sector_analysis/default_weights.json`
2. `CONFIG/sector_analysis/indicators_config.json`
3. `CONFIG/sector_analysis/config_manager.py`

### 10.3 Dashboard Files (Priority 3)
1. `WEBAPP/pages/sector_analysis_dashboard.py` (complete rewrite)
2. `WEBAPP/components/sector_charts.py`
3. `WEBAPP/components/unified_tables.py`
4. `WEBAPP/components/insights_panel.py`

### 10.4 Migration Scripts (Priority 4)
1. `PROCESSORS/unified/migrations/migrate_to_unified.py`
2. `scripts/update_dashboard_for_unified.py`

### 10.5 Test Files (Priority 5)
1. `TESTS/integration/test_unified_schema.py`
2. `TESTS/integration/test_sector_analyzer.py`
3. `TESTS/integration/test_end_to_end_pipeline.py`

This complete refactor will give you exactly what you asked for: a clean, unified, and extensible system that combines FA and TA analysis effectively while being easy to modify and extend.
```

### 11. NEXT STEPS

1. **Review and Approve**: Check the architecture design above
2. **Start Foundation**: Begin with Phase 1 - create unified schema
3. **Gradual Migration**: Move existing data to unified format
4. **Build Dashboard**: Create new sector analysis interface
5. **Test Thoroughly**: Ensure reliability and performance

This is a comprehensive solution that addresses all your current pain points and provides a solid foundation for future enhancements.

```

## 12. PRIORITY IMPLEMENTATION ORDER

### High Priority (Week 1-2)
1. ✅ Create unified schema (`DATA/schemas/unified/`)
2. ✅ Implement SectorAnalyzer core class
3. ✅ Create configuration system (`CONFIG/sector_analysis/`)
4. ✅ Refactor existing data loading to use unified service

### Medium Priority (Week 3-4)
1. ✅ Implement modular chart components
2. ✅ Build enhanced sector dashboard
3. ✅ Create migration scripts
4. ✅ Add comprehensive test coverage

### Low Priority (Week 5-6)
1. ✅ Performance optimization
2. ✅ Advanced analytics features
3. ✅ Documentation completion
4. ✅ User feedback integration

## 13. EXPECTED OUTCOMES

### 13.1 Technical Outcomes
- Single API call gets all FA+TA data: `SectorAnalyzer.analyze_sector("Ngân hàng", "latest")`
- Automatic data refresh with caching
- Modular components easy to extend
- Configuration changes apply instantly without code changes

### 13.2 Business Outcomes
- Complete sector view with FA trends, TA indicators, and combined signals
- Easy comparison between sectors
- AI-like insights for investment decisions
- Reduced development time for new features
- Better risk-adjusted portfolio construction

This architecture transforms your current separated FA and TA systems into a unified, powerful, and maintainable solution.
```

## 14. SAMPLE IMPLEMENTATION SNIPPETS

### 14.1 Single API Usage

```python
# ONE LINE to get complete sector analysis
from PROCESSORS.sector_analysis import SectorAnalyzer

analyzer = SectorAnalyzer()
result = analyzer.analyze_sector("Ngân hàng", "latest")

print(f"Top performer: {result['insights']['top_performers'][0]['ticker']}")
print(f"Insights: {result['insights']['sector_trends']}")
print(f"Trading signals: {result['unified_data'].head()[['signals']}")
```

### 14.2 Configuration-Driven Analysis

```python
# Adjust weights without code changes
from CONFIG.sector_analysis import ConfigManager

config = ConfigManager()
config.update_user_config({
    "fa_weights": {"revenue_growth": 0.3, "roa": 0.4},  # Customize for banking sector
    "ta_weights": {"ma_alignment": 0.4, "momentum": 0.2},  # Focus on momentum for growth sectors
})

analyzer = SectorAnalyzer(config=config)
result = analyzer.analyze_sector("Ngân hàng", "latest")
```

### 14.3 Easy Extension

```python
# Add new indicator without touching core
class VietnamMarketSentiment:
    """Vietnam-specific indicator"""
    @staticmethod
    def calculate(data):
        # Vietnam market logic
        return sentiment_score

# Register globally
from PROCESSORS.unified.registry import register_indicator
register_indicator("vietnam_sentiment", VietnamMarketSentiment)

# Now available in all calculations
```

## 15. ROLLBACK PLAN

### 15.1 Immediate (Week 1)

- Backup existing data and code
- Implement unified schema validation
- Create SectorAnalyzer with basic functionality

### 15.2 Parallel Development (Week 2-3)

- Develop UnifiedDataService
- Refactor existing calculators
- Build new dashboard components
- Create migration scripts

### 15.3 Cutover (Week 4)

- Run parallel old and new systems
- Validate data consistency
- Gradual user migration

### 15.4 Post-Cutover (Week 5)

- Remove old code
- Optimize performance
- Document new architecture
- Collect user feedback

This detailed plan provides a complete roadmap to transform your current separated system into a unified, efficient, and maintainable solution.

````

## 16. ANSWERS TO YOUR CONCERNS

### 16.1 "Modules khác nhau cần thay đổi"

✅ **Addressed**: Create unified modules (SectorAnalyzer, UnifiedDataService) that provide single API for all data

### 16.2 "Data chưa được standardization"

✅ **Addressed**: Implement unified schema (`DATA/schemas/unified/sector_schema.json`) that defines structure for both FA and TA data

### 16.3 "Code bị phân tán, calculators, transformers lẫn lộn"

✅ **Addressed**: Clear separation of concerns:

- Data loaders (unified service)
- Business logic (SectorAnalyzer)
- Calculation logic (transformers layer - already exists)
- Presentation layer (modular components)

### 16.4 "Khó thể theo dõi pipeline dữ liệu"

✅ **Addressed**: Implement orchestrated pipelines with caching and error handling

### 16.5 "Khó thể debug khi có lỗi"

✅ **Addressed**: Centralized validation and error handling in unified service

### 16.6 "Khó thể tùy chỉnh"

✅ **Addressed**: Configuration-driven system with UI for real-time adjustments

This architecture solves all your problems while being much more maintainable and extensible than the current approach.

```

## 17. FINAL ARCHITECTURE DECISION

**RECOMMENDATION**: Implement the unified architecture above as it provides:
- ✅ Single source of truth for all FA+TA data
- ✅ Clear separation of concerns
- ✅ Easy testing and debugging
- ✅ Configuration-driven flexibility
- ✅ Vietnam market specific features
- ✅ Maintainability and extensibility

This is the architecture you need to replace all current separated approaches.
```

## 18. FILES TO DELETE

### 18.1 Legacy Files (After Migration)

```
PROCESSORS/fundamental_legacy/        # REMOVE after migration
PROCESSORS/technical_legacy/         # REMOVE after migration
WEBAPP/pages/*_dashboard.py      # REPLACE with unified versions
```

## 19. IMPLEMENTATION TIMELINE (8 Weeks Total)

| Week | Tasks | Owner | Status |

|-------|--------|--------|--------|

| 1 | Unified schema, SectorAnalyzer core, Config system | Senior Dev | Planning |

| 2 | UnifiedDataService, refactored calculators | Mid Dev | Ready |

| 3 | Chart components, new dashboard | Frontend Dev | Ready |

| 4 | Migration scripts, comprehensive testing | Full Team | Ready |

| 5 | Performance optimization, documentation | QA Team | Ready |

| 6 | Rollout, user training | Product | Ready |

| 7 | Post-cutover cleanup | DevOps | Ready |

| 8 | Maintenance, enhancements | Team | Ready |

## 20. SUCCESS METRICS

### Technical Goals

- **Unified Data Access**: Single API call gets all FA+TA data
- **Modularity**: Each component has single responsibility
- **Testability**: 95%+ code coverage
- **Performance**: < 2s load time for complex sector analysis
- **Maintainability**: New features in < 1 week with no breaking changes

### Business Goals

- **Better Decisions**: 30% improvement in analysis accuracy
- **Complete View**: All FA and TA data in one interface
- **User Satisfaction**: 9/10 user experience rating

This architecture transforms your fragmented approach into a cohesive, powerful system for sector analysis.

```

## 21. NEXT STEP ACTION

**IMMEDIATE ACTION NEEDED**: Please review this comprehensive architecture plan and confirm:
1. Do you want me to begin implementing Phase 1 (foundation)?
2. Should I adjust any specific aspects of the design?
3. Are there particular requirements or constraints I should consider?

**READY TO IMPLEMENT**: When approved, I can start with creating the unified schema and SectorAnalyzer core class immediately.
```

This architecture provides exactly what you asked for - a clean, unified, and maintainable system that integrates FA and TA analysis seamlessly while being easy to customize and extend.

```

### 22. SUMMARY

✅ **Single Source of Truth**: SectorAnalyzer class
✅ **Unified Data Model**: Schema cho cả FA và TA
✅ **Modular Components**: Chart components dễ tái sử dụng
✅ **Configuration-Driven**: Weights và indicators có thể điều chỉnh
✅ **Vietnam Market Specific**: Indicators đặc thù cho thị trường Việt Nam
✅ **Clear Data Flow**: Pipeline từ Raw → Unified → Display
✅ **Easy Testing**: Mỗi component có thể test riêng
✅ **Maintainable Architecture**: Tách biệt, module hóa, dễ bảo trì
✅ **Implementation Timeline**: 8 weeks từ foundation đến production

Đây là kiến trúc hoàn chỉnh để giải quyết tất cả vấn đề của bạn, tạo một hệ thống thống nhất, hiệu quả và dễ mở rộng.
```

### 23. FINAL TECHNICAL SPECIFICATION

- **Architecture Pattern**: Repository Pattern với Domain Services
- **Data Access Layer**: UnifiedDataService (single API)
- **Business Logic Layer**: SectorAnalyzer (orchestrator)
- **Infrastructure Layer**: Configuration, caching, schema validation
- **Presentation Layer**: Modular components with unified API integration

This architecture provides the foundation for a world-class sector analysis system.

```

## 24. PRIORITY TODO LIST

### Critical Path (Week 1-2)

1. ✅ Create `DATA/schemas/unified/sector_schema.json` - Schema định nghĩa
2. ✅ Create `PROCESSORS/unified/schema_validator.py` - Validation logic
3. ✅ Create `PROCESSORS/unified/sector_analyzer.py` - Main orchestrator class
4. ✅ Create `PROCESSORS/unified/unified_data_service.py` - Data access layer
5. ✅ Create `CONFIG/sector_analysis/config_manager.py` - Configuration system

### Important Notes

- **Backward Compatibility**: Keep existing APIs working during transition
- **Incremental Migration**: Move data gradually to unified format
- **Testing Strategy**: Unit test each component independently
- **Performance Considerations**: Cache computed results, batch processing