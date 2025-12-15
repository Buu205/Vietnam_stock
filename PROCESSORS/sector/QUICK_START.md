# Quick Start Guide - Sector Analysis Pipeline

## Installation

No additional dependencies needed. All required modules are already installed.

## Basic Usage

### 1. Run Complete Pipeline

```bash
cd /Users/buuphan/Dev/Vietnam_dashboard
python3 PROCESSORS/sector/run_sector_analysis.py
```

This will:
- Load all available data
- Run FA + TA aggregation
- Calculate scores
- Generate signals
- Save 3 output files

### 2. Run for Specific Time Period

```bash
# Last 6 months
python3 PROCESSORS/sector/run_sector_analysis.py \
  --start-date 2024-06-01 \
  --end-date 2024-12-31

# Specific quarter
python3 PROCESSORS/sector/run_sector_analysis.py \
  --report-date 2024-09-30
```

### 3. Run with Verbose Logging

```bash
python3 PROCESSORS/sector/run_sector_analysis.py --verbose
```

## Python API Usage

```python
from PROCESSORS.sector.sector_processor import SectorProcessor

# Initialize
processor = SectorProcessor()

# Run pipeline
results = processor.run_full_pipeline(
    start_date='2024-01-01',
    end_date='2024-12-31'
)

# Access results
fa_metrics = results['fa_metrics']
ta_metrics = results['ta_metrics']
combined_scores = results['combined_scores']

# Check signals
print(combined_scores[['sector_code', 'combined_score', 'signal']].head(10))
```

## Output Files

All outputs saved to: `DATA/processed/sector/`

1. `sector_fundamental_metrics.parquet` - FA metrics by sector
2. `sector_valuation_metrics.parquet` - TA/valuation metrics
3. `sector_combined_scores.parquet` - Scores + signals

## View Results

```python
import pandas as pd

# Load latest signals
signals = pd.read_parquet('DATA/processed/sector/sector_combined_scores.parquet')

# Top sectors
top_sectors = signals.nlargest(5, 'combined_score')
print(top_sectors[['sector_code', 'combined_score', 'signal']])

# Buy signals only
buy_signals = signals[signals['signal'] == 'BUY']
print(f"BUY signals: {len(buy_signals)} sectors")
```

## Troubleshooting

### Import Error

```bash
# Make sure you're in the project root
cd /Users/buuphan/Dev/Vietnam_dashboard

# Check Python path
python3 -c "import sys; print(sys.path)"
```

### Missing Data

If you get "No data found" errors:

1. Check input files exist:
   - `DATA/processed/fundamental/company/*.parquet`
   - `DATA/processed/fundamental/bank/*.parquet`
   - `DATA/raw/ohlcv/OHLCV_mktcap.parquet`

2. Run fundamental calculators first (if needed):
   ```bash
   python3 PROCESSORS/fundamental/calculators/company_calculator.py
   python3 PROCESSORS/fundamental/calculators/bank_calculator.py
   ```

### Date Format Error

Dates must be in YYYY-MM-DD format:
- ✅ `2024-01-01`
- ❌ `01-01-2024`
- ❌ `2024/01/01`

## Help

```bash
python3 PROCESSORS/sector/run_sector_analysis.py --help
```

## Full Documentation

See `README_PHASE5.md` for complete documentation.
