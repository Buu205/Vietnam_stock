# Command Reference

Complete reference of all CLI commands for the Vietnam Dashboard project.

---

## Daily Update Pipelines

### Unified Daily Update (Recommended)

```bash
# Run complete daily update - runs everything in correct order
python3 PROCESSORS/pipelines/run_all_daily_updates.py

# Updates:
#   - OHLCV data (price, volume, market cap)
#   - Technical indicators (MA, RSI, MACD, etc.)
#   - Market breadth indicators
#   - Technical alerts (breakouts, crossovers, volume spikes)
#   - Valuation ratios (PE, PB, EV/EBITDA)
#   - VN-Index PE/PB
#   - Sector PE/PB
#   - Macro & commodity data

# Execution time: ~45 minutes
```

### Individual Pipeline Updates

```bash
# Valuation pipeline (PE, PB, EV/EBITDA)
python3 PROCESSORS/valuation/daily_full_valuation_pipeline.py
# Time: ~15-20 minutes

# OHLCV data update
python3 PROCESSORS/technical/daily_ohlcv_update.py
# Time: ~5-10 minutes

# Macro & commodity data
python3 PROCESSORS/technical/daily_macro_commodity_update.py
# Time: ~5 minutes

# News data pipeline
python3 PROCESSORS/news/news_pipeline.py
# Time: ~10 minutes

# BSC forecast update (weekly, manual trigger)
python3 PROCESSORS/Bsc_forecast/run_bsc_auto_update.py
# Time: ~10 minutes
```

---

## Fundamental Data Processing

### Company Calculators

```bash
# Process company financial data
python3 PROCESSORS/fundamental/calculators/company_calculator.py
# Input: DATA/raw/fundamental/csv/company/*.csv
# Output: DATA/processed/fundamental/company/company_financial_metrics.parquet

# Process bank financial data (includes NIM, NPL, CAR, CASA)
python3 PROCESSORS/fundamental/calculators/bank_calculator.py
# Input: DATA/raw/fundamental/csv/bank/*.csv
# Output: DATA/processed/fundamental/bank/bank_financial_metrics.parquet

# Process insurance financial data
python3 PROCESSORS/fundamental/calculators/insurance_calculator.py
# Input: DATA/raw/fundamental/csv/insurance/*.csv
# Output: DATA/processed/fundamental/insurance/insurance_financial_metrics.parquet

# Process security/brokerage financial data
python3 PROCESSORS/fundamental/calculators/security_calculator.py
# Input: DATA/raw/fundamental/csv/security/*.csv
# Output: DATA/processed/fundamental/security/security_financial_metrics.parquet
```

---

## Technical Analysis

### Indicator Calculations

```bash
# Calculate basic technical indicators (MA, RSI, MACD, Bollinger, etc.)
python3 PROCESSORS/technical/indicators/basic_indicators.py
# Output: DATA/processed/technical/basic_data.parquet

# Detect technical alerts (breakouts, crossovers, volume spikes)
python3 PROCESSORS/technical/indicators/alert_detector.py
# Output: DATA/processed/technical/alerts/*.parquet

# Calculate market breadth (advance/decline, McClellan)
python3 PROCESSORS/technical/indicators/market_breadth.py
# Output: DATA/processed/technical/market_breadth/*.parquet

# Calculate sector breadth
python3 PROCESSORS/technical/indicators/sector_breadth.py
# Output: DATA/processed/technical/sector_breadth/*.parquet
```

---

## Valuation Calculations

### PE Ratio Calculators

```bash
# Calculate VN-Index PE ratio
python3 PROCESSORS/valuation/calculators/vnindex_pe_calculator_optimized.py
# Output: DATA/processed/valuation/pe/vnindex_pe.parquet

# Calculate sector PE ratios
python3 PROCESSORS/valuation/calculators/sector_pe_calculator.py
# Output: DATA/processed/valuation/pe/sector_pe.parquet

# Calculate individual stock PE ratios
python3 PROCESSORS/valuation/calculators/stock_pe_calculator.py
# Output: DATA/processed/valuation/pe/historical_pe.parquet
```

### PB Ratio Calculators

```bash
# Calculate VN-Index PB ratio
python3 PROCESSORS/valuation/calculators/vnindex_pb_calculator_optimized.py
# Output: DATA/processed/valuation/pb/vnindex_pb.parquet

# Calculate individual stock PB ratios
python3 PROCESSORS/valuation/calculators/stock_pb_calculator.py
# Output: DATA/processed/valuation/pb/historical_pb.parquet
```

### EV/EBITDA Calculators

```bash
# Calculate EV/EBITDA ratios
python3 PROCESSORS/valuation/calculators/ev_ebitda_calculator_optimized.py
# Output: DATA/processed/valuation/ev_ebitda/historical_ev_ebitda.parquet
```

---

## Registry & Mapping Tools

### Building Registries

```bash
# Build metric registry from BSC Excel templates
python3 config/registries/builders/build_metric_registry.py
# Input: PROCESSORS/Bsc_forecast/BSC Master File Equity Pro.xlsm
# Output: DATA/metadata/metric_registry.json

# Build sector/industry registry from ticker metadata
python3 config/registries/builders/build_sector_registry.py
# Input: DATA/metadata/ticker_metadata.parquet
# Output: DATA/metadata/sector_industry_registry.json
```

### Testing Registries

```bash
# Test unified ticker mapper integration
python3 PROCESSORS/core/test_unified_mapper.py

# Test metric registry
python3 -c "from config.registries import MetricRegistry; mr = MetricRegistry(); print(mr.get_metric('CIS_62', 'COMPANY'))"

# Test sector registry
python3 -c "from config.registries import SectorRegistry; sr = SectorRegistry(); print(sr.get_ticker('ACB'))"
```

---

## Streamlit Dashboard

### Running Dashboard

```bash
# Start Streamlit dashboard (default loads Company Dashboard)
streamlit run WEBAPP/main_app.py

# Dashboard will open at http://localhost:8501
```

### Streamlit Options

```bash
# Run on different port
streamlit run WEBAPP/main_app.py --server.port 8502

# Run on specific address
streamlit run WEBAPP/main_app.py --server.address 0.0.0.0

# Disable file watcher (for production)
streamlit run WEBAPP/main_app.py --server.fileWatcherType none
```

---

## Data Inspection

### Check Data Files

```bash
# List all processed fundamental data
ls -lh DATA/processed/fundamental/**/*.parquet

# List technical data
ls -lh DATA/processed/technical/*.parquet

# List valuation data
ls -lh DATA/processed/valuation/**/*.parquet

# Check file size
du -sh DATA/processed/
```

### Inspect Parquet Files

```bash
# View parquet file structure
python3 -c "import pandas as pd; df = pd.read_parquet('DATA/processed/fundamental/company/company_financial_metrics.parquet'); print(df.info())"

# View first 5 rows
python3 -c "import pandas as pd; df = pd.read_parquet('DATA/processed/fundamental/company/company_financial_metrics.parquet'); print(df.head())"

# Count rows
python3 -c "import pandas as pd; df = pd.read_parquet('DATA/processed/fundamental/company/company_financial_metrics.parquet'); print(f'Rows: {len(df)}')"
```

---

## Maintenance Commands

### Clean Processed Data

```bash
# Remove all processed data (will be regenerated)
rm -rf DATA/processed/**/*.parquet

# Remove specific category
rm -rf DATA/processed/fundamental/**/*.parquet
rm -rf DATA/processed/technical/**/*.parquet
rm -rf DATA/processed/valuation/**/*.parquet
```

### Rebuild Everything

```bash
# 1. Rebuild registries
python3 config/registries/builders/build_metric_registry.py
python3 config/registries/builders/build_sector_registry.py

# 2. Rebuild fundamental data
python3 PROCESSORS/fundamental/calculators/company_calculator.py
python3 PROCESSORS/fundamental/calculators/bank_calculator.py
python3 PROCESSORS/fundamental/calculators/insurance_calculator.py
python3 PROCESSORS/fundamental/calculators/security_calculator.py

# 3. Run daily update pipeline
python3 PROCESSORS/pipelines/run_all_daily_updates.py
```

---

## Development Utilities

### Python REPL with Imports

```bash
# Start Python REPL with registries loaded
python3 << EOF
from config.registries import MetricRegistry, SectorRegistry
from config.schema_registry import SchemaRegistry
import pandas as pd
from pathlib import Path

metric_reg = MetricRegistry()
sector_reg = SectorRegistry()

print("Registries loaded. Try:")
print("  metric_reg.get_metric('CIS_62', 'COMPANY')")
print("  sector_reg.get_ticker('ACB')")
EOF
```

### Check Dependencies

```bash
# Check Python version
python3 --version

# Check installed packages
pip list | grep -E 'vnstock|streamlit|pandas|plotly|ta'

# Check vnstock_data
python3 -c "import vnstock_data; print('vnstock_data version:', vnstock_data.__version__)"
```

---

## Git Workflows

### Check Status

```bash
# View current status
git status

# View recent commits
git log --oneline -10

# View current branch
git branch
```

### Create Commits

```bash
# Stage all changes
git add .

# Commit with conventional commit format
git commit -m "feat(dashboard): add new sector comparison view"
git commit -m "fix(calculator): correct ROE calculation for banks"
git commit -m "docs(claude): restructure CLAUDE.md into modular system"

# Push to remote
git push origin main
```

---

## Quick Reference

| Task | Command |
|------|---------|
| **Run dashboard** | `streamlit run WEBAPP/main_app.py` |
| **Daily update** | `python3 PROCESSORS/pipelines/run_all_daily_updates.py` |
| **Company metrics** | `python3 PROCESSORS/fundamental/calculators/company_calculator.py` |
| **Bank metrics** | `python3 PROCESSORS/fundamental/calculators/bank_calculator.py` |
| **Rebuild metric registry** | `python3 config/registries/builders/build_metric_registry.py` |
| **Check data files** | `ls -lh DATA/processed/**/*.parquet` |
| **Inspect parquet** | `python3 -c "import pandas as pd; pd.read_parquet('path').info()"` |
