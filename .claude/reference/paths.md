# Canonical v4.0.0 Paths Reference

Complete reference for all data paths in the Vietnam Dashboard project.

**STATUS:** ✅ Path migration complete (100% compliance)

---

## Directory Structure

```
Vietnam_dashboard/
├── DATA/
│   ├── raw/                    # Input data (READ from here)
│   │   ├── ohlcv/
│   │   ├── fundamental/csv/
│   │   ├── commodity/
│   │   └── macro/
│   │
│   ├── processed/              # Output data (WRITE to here)
│   │   ├── fundamental/
│   │   ├── technical/
│   │   ├── valuation/
│   │   ├── commodity/
│   │   ├── macro/
│   │   └── forecast/
│   │
│   └── metadata/               # Registry & lookup data
│       ├── metric_registry.json
│       └── sector_industry_registry.json
│
├── PROCESSORS/                 # Data processing code
│   ├── fundamental/
│   ├── technical/
│   ├── valuation/
│   └── pipelines/
│
├── WEBAPP/                     # Streamlit dashboard
│   ├── main_app.py
│   ├── pages/
│   ├── services/
│   └── components/
│
├── config/                     # Configuration & registries
│   ├── registries/
│   ├── schema_registry/
│   └── metadata_registry/
│
└── .claude/                    # AI documentation
    ├── rules/
    ├── guides/
    └── reference/
```

---

## Raw Data Paths (Input)

### OHLCV Data

```python
# Primary OHLCV file (all tickers, all dates, market cap)
DATA/raw/ohlcv/OHLCV_mktcap.parquet

# Usage:
ohlcv_df = pd.read_parquet("DATA/raw/ohlcv/OHLCV_mktcap.parquet")
```

### Fundamental Data (CSV)

```python
# Company financial statements
DATA/raw/fundamental/csv/company/{ticker}_financial.csv
# Example: DATA/raw/fundamental/csv/company/VCB_financial.csv

# Bank financial statements
DATA/raw/fundamental/csv/bank/{ticker}_financial.csv
# Example: DATA/raw/fundamental/csv/bank/ACB_financial.csv

# Insurance financial statements
DATA/raw/fundamental/csv/insurance/{ticker}_financial.csv

# Security/brokerage financial statements
DATA/raw/fundamental/csv/security/{ticker}_financial.csv
```

### Commodity & Macro Data

```python
# Commodity prices (gold, oil, steel, rubber)
DATA/raw/commodity/commodity_prices.parquet

# Macro indicators (interest rates, FX, bond yields)
DATA/raw/macro/macro_indicators.parquet
```

---

## Processed Data Paths (Output)

### Fundamental Metrics

```python
# Company financial metrics (all companies, all periods)
DATA/processed/fundamental/company/company_financial_metrics.parquet

# Bank metrics (NIM, NPL, CAR, CASA, etc.)
DATA/processed/fundamental/bank/bank_financial_metrics.parquet

# Insurance metrics
DATA/processed/fundamental/insurance/insurance_financial_metrics.parquet

# Security/brokerage metrics
DATA/processed/fundamental/security/security_financial_metrics.parquet
```

### Technical Indicators

```python
# Basic technical data (MA, RSI, MACD, Bollinger, etc.)
DATA/processed/technical/basic_data.parquet

# Technical alerts (latest)
DATA/processed/technical/alerts/daily/breakout_latest.parquet
DATA/processed/technical/alerts/daily/ma_crossover_latest.parquet
DATA/processed/technical/alerts/daily/volume_spike_latest.parquet
DATA/processed/technical/alerts/daily/patterns_latest.parquet
DATA/processed/technical/alerts/daily/combined_latest.parquet

# Technical alerts (historical)
DATA/processed/technical/alerts/historical/breakout_history.parquet
DATA/processed/technical/alerts/historical/ma_crossover_history.parquet
DATA/processed/technical/alerts/historical/volume_spike_history.parquet
DATA/processed/technical/alerts/historical/patterns_history.parquet
DATA/processed/technical/alerts/historical/combined_history.parquet

# Market breadth indicators
DATA/processed/technical/market_breadth/market_breadth_daily.parquet

# Sector breadth indicators
DATA/processed/technical/sector_breadth/sector_breadth_daily.parquet

# Money flow indicators
DATA/processed/technical/money_flow/individual_money_flow.parquet
DATA/processed/technical/money_flow/sector_money_flow_1d.parquet
DATA/processed/technical/money_flow/sector_money_flow_1w.parquet
DATA/processed/technical/money_flow/sector_money_flow_1m.parquet

# RS rating
DATA/processed/technical/rs_rating/stock_rs_rating_daily.parquet

# VN-Index indicators
DATA/processed/technical/vnindex/vnindex_indicators.parquet

# Market regime
DATA/processed/technical/market_regime/market_regime_history.parquet
```

### Valuation Ratios

```python
# PE Ratio
DATA/processed/valuation/pe/historical_pe.parquet              # Individual stocks
DATA/processed/valuation/pe/vnindex_pe.parquet                 # VN-Index PE
DATA/processed/valuation/pe/sector_pe.parquet                  # Sector PE

# PB Ratio
DATA/processed/valuation/pb/historical_pb.parquet              # Individual stocks
DATA/processed/valuation/pb/vnindex_pb.parquet                 # VN-Index PB
DATA/processed/valuation/pb/sector_pb.parquet                  # Sector PB

# EV/EBITDA
DATA/processed/valuation/ev_ebitda/historical_ev_ebitda.parquet

# PS Ratio
DATA/processed/valuation/ps/historical_ps.parquet

# VN-Index valuation (combined)
DATA/processed/valuation/vnindex/vnindex_valuation_refined.parquet
```

### Sector Metrics

```python
# Sector fundamental metrics
DATA/processed/sector/sector_fundamental_metrics.parquet

# Sector valuation metrics
DATA/processed/sector/sector_valuation_metrics.parquet
```

### Forecast Data

```python
# BSC analyst forecasts (individual stocks)
DATA/processed/forecast/bsc/bsc_individual.parquet

# BSC forecasts (combined with current data)
DATA/processed/forecast/bsc/bsc_combined.parquet

# BSC sector valuation
DATA/processed/forecast/bsc/bsc_sector_valuation.parquet
```

### Macro & Commodity

```python
# Unified macro & commodity data
DATA/processed/macro_commodity/macro_commodity_unified.parquet
```

---

## Metadata & Registry Paths

```python
# Metric registry (Vietnamese → English mapping)
DATA/metadata/metric_registry.json

# Sector/industry registry (ticker → sector mapping)
DATA/metadata/sector_industry_registry.json

# Ticker metadata
DATA/metadata/ticker_metadata.parquet
```

---

## Configuration Paths

```python
# Registry classes
config/registries/metric_lookup.py
config/registries/sector_lookup.py

# Schema registry
config/schema_registry.py

# Schema definitions
config/schema_registry/core/*.json
config/schema_registry/domain/**/*.json
config/schema_registry/display/*.json
```

---

## Path Resolution Patterns

### Using Centralized Helper (Recommended)

```python
from PROCESSORS.core.config.paths import get_data_path

# Get processed data path
company_path = get_data_path("processed", "fundamental", "company")
# Returns: Path("DATA/processed/fundamental/company")

# Get specific file
pe_file = get_data_path("processed", "valuation", "pe", "historical_pe.parquet")
# Returns: Path("DATA/processed/valuation/pe/historical_pe.parquet")

# Get raw data path
ohlcv_path = get_data_path("raw", "ohlcv", "OHLCV_mktcap.parquet")
# Returns: Path("DATA/raw/ohlcv/OHLCV_mktcap.parquet")
```

### Manual Path Construction

```python
from pathlib import Path

# ✅ CORRECT: Use Path objects
data_root = Path("DATA")
input_path = data_root / "raw" / "ohlcv" / "OHLCV_mktcap.parquet"
output_path = data_root / "processed" / "fundamental" / "company" / "company_financial_metrics.parquet"

# ✅ ACCEPTABLE: String paths (but prefer Path)
input_path = "DATA/raw/ohlcv/OHLCV_mktcap.parquet"
output_path = "DATA/processed/fundamental/company/company_financial_metrics.parquet"
```

### Create Output Directories

```python
from pathlib import Path

# Always create parent directories before writing
output_path = Path("DATA/processed/valuation/pe/historical_pe.parquet")
output_path.parent.mkdir(parents=True, exist_ok=True)
df.to_parquet(output_path)
```

---

## Deprecated Paths (DO NOT USE)

**These paths were removed in v4.0.0 path migration:**

```python
# ❌ WRONG (deprecated)
calculated_results/                     → Use: DATA/processed/
data_warehouse/raw/                     → Use: DATA/raw/
DATA/refined/                           → Use: DATA/processed/
```

**Migration Status:** ✅ Complete (100% compliance)

---

## Path Validation

### Check Path Exists

```python
from pathlib import Path

path = Path("DATA/processed/fundamental/company/company_financial_metrics.parquet")

if not path.exists():
    raise FileNotFoundError(f"File not found: {path}")

# Or use assert
assert path.exists(), f"File not found: {path}"
```

### Validate Input/Output Paths

```python
def validate_paths(input_path: Path, output_path: Path) -> None:
    """Validate input exists and output directory can be created."""

    # Check input exists
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # Create output directory if needed
    output_path.parent.mkdir(parents=True, exist_ok=True)

# Usage
input_path = Path("DATA/raw/ohlcv/OHLCV_mktcap.parquet")
output_path = Path("DATA/processed/valuation/pe/historical_pe.parquet")
validate_paths(input_path, output_path)
```

---

## Quick Reference

| Category | Input Path | Output Path |
|----------|------------|-------------|
| **OHLCV** | `DATA/raw/ohlcv/OHLCV_mktcap.parquet` | `DATA/processed/technical/basic_data.parquet` |
| **Company** | `DATA/raw/fundamental/csv/company/{ticker}.csv` | `DATA/processed/fundamental/company/company_financial_metrics.parquet` |
| **Bank** | `DATA/raw/fundamental/csv/bank/{ticker}.csv` | `DATA/processed/fundamental/bank/bank_financial_metrics.parquet` |
| **PE Ratio** | OHLCV + Fundamental | `DATA/processed/valuation/pe/historical_pe.parquet` |
| **PB Ratio** | OHLCV + Fundamental | `DATA/processed/valuation/pb/historical_pb.parquet` |
| **Forecast** | BSC Excel | `DATA/processed/forecast/bsc/bsc_individual.parquet` |

---

## Deployment Data Files (Streamlit Cloud)

**IMPORTANT:** These parquet files MUST be committed to GitHub for Streamlit Cloud deployment.

### Required Files for Webapp

```bash
# Use this command to add all required webapp data:
git add -f DATA/processed/**/*.parquet

# Or selectively add specific categories:
git add -f DATA/processed/forecast/bsc/*.parquet
git add -f DATA/processed/forecast/VCI/*.parquet
git add -f DATA/processed/fundamental/**/*.parquet
git add -f DATA/processed/technical/**/*.parquet
git add -f DATA/processed/valuation/**/*.parquet
git add -f DATA/processed/sector/*.parquet
git add -f DATA/processed/macro_commodity/*.parquet
```

### Files by Category

| Category | Files | Required | Notes |
|----------|-------|----------|-------|
| **Forecast BSC** | `bsc_individual.parquet`, `bsc_combined.parquet`, `bsc_sector_valuation.parquet` | ✅ Yes | BSC analyst forecasts |
| **Forecast VCI** | `vci_coverage_universe.parquet` | ✅ Yes | VCI consensus data |
| **Fundamental** | `company_financial_metrics.parquet`, `bank_financial_metrics.parquet`, etc. | ✅ Yes | Financial metrics |
| **Technical** | All files in `technical/` | ✅ Yes | TA indicators, alerts, money flow |
| **Valuation** | `historical_pe.parquet`, `historical_pb.parquet`, etc. | ✅ Yes | PE/PB/EV ratios |
| **Sector** | `sector_valuation_metrics.parquet` | ✅ Yes | Sector aggregates |
| **Macro** | `macro_commodity_unified.parquet` | ✅ Yes | Macro indicators |

### Files NOT to Commit (Local Only)

```bash
# These are large database dumps - keep local only:
DATA/processed/fundamental/company_full.parquet    # ~85MB
DATA/processed/fundamental/bank_full.parquet       # ~40MB
DATA/processed/fundamental/insurance_full.parquet  # ~20MB
DATA/processed/fundamental/security_full.parquet   # ~15MB

# Test files:
DATA/processed/**/*_test.parquet
```

### Adding New Data Sources

When adding new data for webapp:

1. **Add to registry:** Update `config/data_mapping/configs/data_sources.yaml`
2. **Commit file:** `git add -f DATA/processed/path/to/new_file.parquet`
3. **Update this doc:** Add to table above

### Check Current Tracked Files

```bash
# List all tracked parquet files:
git ls-files DATA/processed/ | grep ".parquet"

# Check file sizes:
git ls-files DATA/processed/ | grep ".parquet" | xargs -I{} sh -c 'echo "$(du -h {} | cut -f1) {}"'
```

---

## Environment Variables

```bash
# Optional: Override data root
export VIETNAM_DASHBOARD_DATA_ROOT="/custom/path/to/DATA"

# Then in code:
import os
from pathlib import Path

data_root = Path(os.getenv("VIETNAM_DASHBOARD_DATA_ROOT", "DATA"))
```
