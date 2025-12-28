# Development Guide

Complete guide to setting up and developing the Vietnam Dashboard project.

---

## Development Environment

### Python Setup

**Python Version:** 3.13 (system Python)

**Python Binary:**
- Primary: `/Library/Frameworks/Python.framework/Versions/3.13/bin/python3`
- Alias: `python3`

**No Virtual Environment:**
- Project uses global Python 3.13 installation
- All dependencies installed globally

### Key Dependencies

**Core:**
- `vnstock_data` - Vietnamese stock market data API (required globally)
- `streamlit` - Web dashboard framework
- `pandas` - Data manipulation
- `plotly` - Interactive charts

**Technical Analysis:**
- `ta` - Technical analysis indicators
- `numpy` - Numerical operations

**Data Storage:**
- `pyarrow` - Parquet file support

---

## Installation

### 1. Install Dependencies

```bash
# Streamlit app dependencies
pip install -r WEBAPP/requirements.txt

# OHLCV pipeline dependencies (if working with technical data)
pip install -r PROCESSORS/technical/ohlcv/requirements_ohlcv.txt
```

### 2. Verify Installation

```bash
# Check Python version
python3 --version
# Expected: Python 3.13.x

# Check vnstock_data
python3 -c "import vnstock_data; print('vnstock_data installed')"

# Check streamlit
streamlit --version
```

### 3. Verify Data Structure

```bash
# Check DATA directory exists
ls -la DATA/

# Should see:
# DATA/
# ├── raw/
# ├── processed/
# └── metadata/
```

---

## Running the Application

### Start Streamlit Dashboard

```bash
# From project root
streamlit run WEBAPP/main_app.py

# Dashboard will open at http://localhost:8501
```

### Available Dashboards

Access via sidebar menu:
- **Company Dashboard** - Company financial analysis
- **Bank Dashboard** - Bank-specific metrics (NIM, NPL, CAR)
- **Sector Dashboard** - Sector comparison and analysis
- **Forecast Dashboard** - BSC analyst forecasts
- **Technical Dashboard** - Technical indicators and alerts
- **FX & Commodities** - Macro and commodity data

---

## Development Workflow

### 1. Before Making Changes

```bash
# Read critical rules
cat .claude/rules/critical.md

# Check active plan
cat plans/fa+ta_sector_analysis_-_complete_architecture_refactor_b2d5c14f.plan.md

# Check current branch
git branch
```

### 2. Development Process

```python
# 1. Import registries (ALWAYS)
from config.registries import MetricRegistry, SectorRegistry
from config.schema_registry import SchemaRegistry

# 2. Use canonical paths (ALWAYS)
from PROCESSORS.core.config.paths import get_data_path
data_path = get_data_path("processed", "fundamental", "company")

# 3. Don't duplicate calculators (NEVER)
# Load existing results
df = pd.read_parquet("DATA/processed/fundamental/company/company_financial_metrics.parquet")

# 4. Use transformers for new calculations
from PROCESSORS.transformers.financial import roe, roa
sector_roe = roe(total_net_income, total_equity)
```

### 3. Testing Changes

```bash
# Run specific calculator
python3 PROCESSORS/fundamental/calculators/company_calculator.py

# Run daily update pipeline
python3 PROCESSORS/pipelines/run_all_daily_updates.py

# Verify output
ls -lh DATA/processed/fundamental/company/
```

### 4. Code Style Check

```bash
# Follow conventions
# See: .claude/rules/conventions.md

# Check import order
# 1. Standard library
# 2. Third-party
# 3. Local

# Check naming
# Files: snake_case
# Classes: PascalCase
# Functions/vars: snake_case
```

---

## Common Development Tasks

### Adding a New Metric

1. **Check if metric exists in registry:**
   ```python
   from config.registries import MetricRegistry
   metric_reg = MetricRegistry()
   metric = metric_reg.search_metrics("your_metric_name")
   ```

2. **If not in registry, add to BSC Excel:**
   ```bash
   # Edit: PROCESSORS/Bsc_forecast/BSC Master File Equity Pro.xlsm
   # Rebuild registry:
   python3 config/registries/builders/build_metric_registry.py
   ```

3. **Add calculation in transformer:**
   ```python
   # Edit: PROCESSORS/transformers/financial/formulas.py
   def your_metric(param1: float, param2: float) -> float:
       """Calculate your metric.

       Args:
           param1: Description
           param2: Description

       Returns:
           Calculated value
       """
       return param1 / param2
   ```

4. **Use in calculator:**
   ```python
   from PROCESSORS.transformers.financial import your_metric
   df['your_metric'] = your_metric(df['param1'], df['param2'])
   ```

### Adding a New Dashboard Page

1. **Create page structure:**
   ```bash
   mkdir -p WEBAPP/pages/new_dashboard/{components,services}
   touch WEBAPP/pages/new_dashboard/new_dashboard_dashboard.py
   touch WEBAPP/pages/new_dashboard/services/new_dashboard_service.py
   ```

2. **Implement service layer:**
   ```python
   # WEBAPP/pages/new_dashboard/services/new_dashboard_service.py
   import streamlit as st
   import pandas as pd
   from pathlib import Path

   class NewDashboardService:
       @st.cache_data(ttl=3600)
       def load_data(self) -> pd.DataFrame:
           path = Path("DATA/processed/your_data.parquet")
           return pd.read_parquet(path)
   ```

3. **Implement dashboard:**
   ```python
   # WEBAPP/pages/new_dashboard/new_dashboard_dashboard.py
   import streamlit as st
   from .services.new_dashboard_service import NewDashboardService

   st.title("New Dashboard")

   service = NewDashboardService()
   df = service.load_data()

   st.dataframe(df)
   ```

4. **Add to navigation:**
   ```python
   # Edit: WEBAPP/main_app.py
   # Add page to sidebar menu
   ```

### Running Data Pipeline

```bash
# Complete daily update (recommended)
python3 PROCESSORS/pipelines/run_all_daily_updates.py

# Individual pipelines
python3 PROCESSORS/valuation/daily_full_valuation_pipeline.py  # Valuation
python3 PROCESSORS/technical/daily_ohlcv_update.py              # OHLCV
python3 PROCESSORS/technical/daily_macro_commodity_update.py    # Macro
python3 PROCESSORS/Bsc_forecast/run_bsc_auto_update.py         # Forecast

# Specific calculators
python3 PROCESSORS/fundamental/calculators/company_calculator.py
python3 PROCESSORS/fundamental/calculators/bank_calculator.py
```

### Building Registries

```bash
# Rebuild metric registry from BSC Excel
python3 config/registries/builders/build_metric_registry.py

# Rebuild sector registry from metadata
python3 config/registries/builders/build_sector_registry.py

# Test unified mapper
python3 PROCESSORS/core/test_unified_mapper.py
```

---

## Debugging

### Enable Logging

```python
import logging

# Set up logger
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info("Starting process...")
logger.debug(f"Data shape: {df.shape}")
```

### Check Data Files

```bash
# Check file exists
ls -lh DATA/processed/fundamental/company/company_financial_metrics.parquet

# Check file contents
python3 -c "import pandas as pd; df = pd.read_parquet('DATA/processed/fundamental/company/company_financial_metrics.parquet'); print(df.info())"

# Check file size
du -sh DATA/processed/**/*.parquet
```

### Streamlit Debugging

```python
# Print data to debug
st.write("Debug info:")
st.write(df.head())
st.write(df.info())

# Use st.expander for detailed debug
with st.expander("Debug Data"):
    st.dataframe(df)
    st.json(df.to_dict())
```

---

## Performance Tips

### Parquet Optimization

```python
# Use compression
df.to_parquet(path, compression='snappy')

# Read specific columns only
df = pd.read_parquet(path, columns=['ticker', 'date', 'roe'])

# Use filters
df = pd.read_parquet(path, filters=[('date', '>=', '2024-01-01')])
```

### Streamlit Caching

```python
# Cache data loading (TTL: 1 hour)
@st.cache_data(ttl=3600)
def load_company_metrics():
    return pd.read_parquet(path)

# Cache resource initialization (forever)
@st.cache_resource
def get_registries():
    return MetricRegistry(), SectorRegistry()
```

### DataFrame Operations

```python
# Use vectorized operations
df['roe'] = df['net_income'] / df['equity']  # ✅ Fast

# Avoid iterrows
for _, row in df.iterrows():  # ❌ Slow
    row['roe'] = row['net_income'] / row['equity']

# Use apply only when necessary
df['roe'] = df.apply(lambda row: roe(row['net_income'], row['equity']), axis=1)
```

---

## Important Notes

### Data Files
- **Expendable:** Files in `DATA/processed/` are generated artifacts
- **Can be regenerated:** Run calculators to rebuild
- **Don't commit:** Large Parquet files not in git

### Configuration Files
- **MongoDB credentials:** Store in `.env` file (never commit)
- **BSC Excel:** Keep latest version in `PROCESSORS/Bsc_forecast/`

### Streamlit
- **Caching:** Use `@st.cache_data` and `@st.cache_resource`
- **Redis:** App uses Redis for distributed caching (optional)
- **Port:** Default 8501, configurable in `.streamlit/config.toml`

---

## Troubleshooting

### Common Issues

**1. Import Error: `ModuleNotFoundError: No module named 'config.registries'`**
```bash
# Ensure you're in project root
pwd
# Should be: /Users/buuphan/Dev/Vietnam_dashboard

# Check PYTHONPATH
echo $PYTHONPATH
```

**2. File Not Found: `DATA/processed/...`**
```bash
# Run calculator to generate file
python3 PROCESSORS/fundamental/calculators/company_calculator.py
```

**3. Streamlit Not Loading Data**
```python
# Clear Streamlit cache
st.cache_data.clear()
st.cache_resource.clear()

# Or restart Streamlit
# Ctrl+C and restart: streamlit run WEBAPP/main_app.py
```

**4. vnstock_data API Error**
```python
# Check API availability
from vnstock_data import Stock
stock = Stock("VCB")
print(stock.quote.history())
```

---

## Next Steps

- **Read:** [Architecture Guide](.claude/guides/architecture.md)
- **Read:** [Data Flow Guide](.claude/guides/data-flow.md)
- **Reference:** [Commands Reference](.claude/reference/commands.md)
- **Active Plan:** `plans/fa+ta_sector_analysis_-_complete_architecture_refactor_b2d5c14f.plan.md`
