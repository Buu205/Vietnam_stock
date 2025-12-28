# Data Flow Architecture

Understanding how data flows through the Vietnam Dashboard system.

---

## Overview

Data flows through 3 main stages:
1. **Ingestion** - Fetch raw data from APIs/Excel
2. **Processing** - Calculate metrics, indicators, ratios
3. **Presentation** - Display in Streamlit dashboards

```
API/Excel → Raw Data → Processors → Processed Data → Services → Dashboard
```

---

## Stage 1: Data Ingestion

### Sources

| Source | Type | Data | Frequency |
|--------|------|------|-----------|
| **vnstock_data** | Python API | OHLCV, Fundamental | Daily |
| **BSC Excel** | Excel file | Analyst forecasts | Weekly |
| **Market Data** | API | Macro, Commodity | Daily |

### Raw Data Storage

```
DATA/raw/
├── ohlcv/
│   └── OHLCV_mktcap.parquet               # Price + Market cap (all tickers, all dates)
├── fundamental/csv/
│   ├── company/{ticker}_financial.csv      # Company financial statements
│   ├── bank/{ticker}_financial.csv         # Bank financial statements
│   └── ...
├── commodity/
│   └── commodity_prices.parquet
└── macro/
    └── macro_indicators.parquet
```

---

## Stage 2: Data Processing

### Processing Pipeline

```
Raw Data
    │
    ├─> Fundamental Calculators
    │   ├─> CompanyCalculator → company_financial_metrics.parquet
    │   ├─> BankCalculator → bank_financial_metrics.parquet
    │   ├─> InsuranceCalculator → insurance_financial_metrics.parquet
    │   └─> SecurityCalculator → security_financial_metrics.parquet
    │
    ├─> Technical Indicators
    │   ├─> BasicIndicators → basic_data.parquet
    │   ├─> AlertDetector → alerts/*.parquet
    │   └─> MarketBreadth → market_breadth/*.parquet
    │
    └─> Valuation Calculators
        ├─> PECalculator → pe/historical_pe.parquet
        ├─> PBCalculator → pb/historical_pb.parquet
        └─> EVEBITDACalculator → ev_ebitda/historical_ev_ebitda.parquet
```

### Fundamental Processing Flow

```python
# 1. Load raw CSV
raw_df = pd.read_csv("DATA/raw/fundamental/csv/company/VCB_financial.csv")

# 2. Apply metric registry (Vietnamese → English)
metric_reg = MetricRegistry()
raw_df = metric_reg.translate_columns(raw_df, entity_type="COMPANY")

# 3. Calculate derived metrics using transformers
from PROCESSORS.transformers.financial import roe, roa, gross_margin

df['roe'] = roe(df['net_income'], df['equity'])
df['roa'] = roa(df['net_income'], df['assets'])
df['gross_margin'] = gross_margin(df['gross_profit'], df['revenue'])

# 4. Save processed data
df.to_parquet("DATA/processed/fundamental/company/company_financial_metrics.parquet")
```

### Technical Processing Flow

```python
# 1. Load OHLCV data
ohlcv_df = pd.read_parquet("DATA/raw/ohlcv/OHLCV_mktcap.parquet")

# 2. Calculate indicators (per ticker)
import ta

df['sma_20'] = ta.trend.sma_indicator(df['close'], window=20)
df['rsi_14'] = ta.momentum.rsi(df['close'], window=14)
df['macd'] = ta.trend.macd(df['close'])

# 3. Detect alerts
alerts = detect_breakouts(df)
alerts = detect_ma_crossovers(df)

# 4. Save processed data
df.to_parquet("DATA/processed/technical/basic_data.parquet")
alerts.to_parquet("DATA/processed/technical/alerts/breakout_latest.parquet")
```

### Valuation Processing Flow

```python
# 1. Load OHLCV + Fundamental data
ohlcv_df = pd.read_parquet("DATA/raw/ohlcv/OHLCV_mktcap.parquet")
fundamental_df = pd.read_parquet("DATA/processed/fundamental/company/company_financial_metrics.parquet")

# 2. Calculate PE ratio
# PE = Market Cap / TTM Earnings
pe_df = calculate_pe_ratio(ohlcv_df, fundamental_df)

# 3. Calculate sector PE (aggregate)
sector_reg = SectorRegistry()
sector_pe_df = calculate_sector_pe(pe_df, sector_reg)

# 4. Save processed data
pe_df.to_parquet("DATA/processed/valuation/pe/historical_pe.parquet")
sector_pe_df.to_parquet("DATA/processed/valuation/pe/sector_pe.parquet")
```

---

## Stage 3: Data Presentation

### Dashboard Service Layer

Services abstract data access for dashboards:

```python
# WEBAPP/services/company_service.py
class CompanyService:
    def __init__(self):
        self.data_path = Path("DATA/processed/fundamental/company")

    @st.cache_data(ttl=3600)
    def get_company_metrics(self, ticker: str) -> pd.DataFrame:
        """Load company metrics for a ticker."""
        df = pd.read_parquet(self.data_path / "company_financial_metrics.parquet")
        return df[df['ticker'] == ticker]

    @st.cache_data(ttl=3600)
    def get_sector_comparison(self, sector: str) -> pd.DataFrame:
        """Load all companies in a sector."""
        sector_reg = SectorRegistry()
        tickers = sector_reg.get_tickers_by_sector(sector)

        df = pd.read_parquet(self.data_path / "company_financial_metrics.parquet")
        return df[df['ticker'].isin(tickers)]
```

### Dashboard UI Flow

```python
# WEBAPP/pages/company/company_dashboard.py
import streamlit as st
from WEBAPP.services.company_service import CompanyService

# 1. Initialize service
service = CompanyService()

# 2. User input
ticker = st.selectbox("Select Ticker", ["VCB", "ACB", "FPT", "VNM"])

# 3. Load data from service
df = service.get_company_metrics(ticker)

# 4. Display metrics
st.metric("ROE", f"{df['roe'].iloc[-1]:.2%}")
st.metric("Revenue Growth", f"{df['revenue_growth'].iloc[-1]:.2%}")

# 5. Display charts
st.line_chart(df.set_index('date')[['revenue', 'net_income']])
```

---

## Daily Update Flow

### Unified Daily Update Pipeline

```bash
# Run complete daily update
python3 PROCESSORS/pipelines/run_all_daily_updates.py
```

**Execution Order:**

1. **OHLCV Update** (5-10 min)
   - Fetch latest OHLCV data via vnstock_data
   - Update `DATA/raw/ohlcv/OHLCV_mktcap.parquet`

2. **Technical Indicators** (10-15 min)
   - Calculate MA, RSI, MACD, Bollinger Bands
   - Detect alerts (breakouts, crossovers, volume spikes)
   - Update `DATA/processed/technical/*.parquet`

3. **Valuation Ratios** (15-20 min)
   - Calculate PE, PB, EV/EBITDA for all tickers
   - Calculate VN-Index PE/PB
   - Calculate sector PE/PB
   - Update `DATA/processed/valuation/*.parquet`

4. **Macro & Commodity** (5 min)
   - Fetch macro indicators (interest rates, FX)
   - Fetch commodity prices (gold, oil, steel)
   - Update `DATA/processed/macro_commodity/*.parquet`

5. **BSC Forecast** (weekly, 10 min)
   - Parse BSC Excel file
   - Update target prices, ratings
   - Update `DATA/processed/forecast/bsc/*.parquet`

**Total Time:** ~45 minutes per day

---

## Data Dependencies

### Dependency Graph

```
OHLCV (raw)
    │
    ├─> Technical Indicators
    │   └─> Market Breadth
    │
    └─> Valuation Ratios
        ├─> Fundamental Data (TTM earnings, equity)
        └─> Sector Valuation

Fundamental (raw CSV)
    │
    └─> Financial Calculators
        ├─> Company Metrics
        ├─> Bank Metrics
        └─> ...
            └─> Valuation Ratios

BSC Excel
    │
    └─> Forecast Parser
        └─> Analyst Forecasts
```

### Critical Dependencies

| Processor | Depends On | Output |
|-----------|------------|--------|
| **BasicIndicators** | `DATA/raw/ohlcv/OHLCV_mktcap.parquet` | `DATA/processed/technical/basic_data.parquet` |
| **PECalculator** | OHLCV + Fundamental | `DATA/processed/valuation/pe/historical_pe.parquet` |
| **SectorPECalculator** | PECalculator + SectorRegistry | `DATA/processed/valuation/pe/sector_pe.parquet` |
| **MarketBreadth** | BasicIndicators | `DATA/processed/technical/market_breadth/*.parquet` |

---

## Data Refresh Strategy

### Real-time Data
- **Not supported** - All data is batch-processed daily

### Daily Updates
- **OHLCV:** Every trading day (8:00 AM)
- **Technical Indicators:** After OHLCV update
- **Valuation Ratios:** After fundamental + OHLCV update

### Weekly Updates
- **BSC Forecast:** Manual trigger when Excel file updated

### On-Demand Updates
- **Fundamental Data:** Run calculator manually when new quarterly reports published

---

## Data Validation

### Validation Checkpoints

1. **Raw Data Validation**
   ```python
   # Check OHLCV completeness
   assert df['close'].notna().all(), "Missing close prices"
   assert df['volume'].ge(0).all(), "Negative volume"
   ```

2. **Processing Validation**
   ```python
   # Check calculated metrics
   assert df['roe'].between(-1, 2).all(), "ROE out of range"
   assert df['pe_ratio'].ge(0).all(), "Negative PE"
   ```

3. **Output Validation**
   ```python
   # Check output file
   assert output_path.exists(), "Output file not created"
   assert len(df) > 0, "Empty output"
   ```

---

## Performance Optimization

### Parquet Format
- **Columnar storage** - Fast column reads
- **Compression** - ~10x smaller than CSV
- **Type preservation** - No parsing overhead

### Caching Strategy
```python
# Dashboard level
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_company_metrics():
    return pd.read_parquet(path)

# Registry level
@st.cache_resource  # Cache forever (singleton)
def get_registries():
    return MetricRegistry(), SectorRegistry()
```

### Incremental Updates
- Only process new/updated data
- Avoid reprocessing entire history
- Use date-based filtering

---

## Summary

**Key Principles:**
1. **Single source of truth** - Raw data in `DATA/raw/`
2. **Separation of concerns** - Calculators, transformers, services separate
3. **Registry-based lookups** - No hardcoded mappings
4. **Parquet everywhere** - Efficient storage and retrieval
5. **Caching at every layer** - Minimize redundant computation

**Data Flow:**
```
Raw → Process → Store → Cache → Display
```
