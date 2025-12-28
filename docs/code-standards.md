# Code Standards

**Project:** Vietnam Stock Dashboard
**Python Version:** 3.13
**Last Updated:** 2025-12-28

---

## 1. Naming Conventions

### Files & Modules
```python
# snake_case for files
company_calculator.py
sector_service.py
unified_mapper.py

# Descriptive names (self-documenting)
historical_pe_calculator.py  # NOT: pe_calc.py
ohlcv_daily_updater.py       # NOT: updater.py
```

### Classes
```python
# CamelCase
class CompanyCalculator:
class SectorRegistry:
class UnifiedTickerMapper:
```

### Functions & Variables
```python
# snake_case
def calculate_roe(net_income, equity):
def get_sector_peers(ticker):

# DataFrame variables with _df suffix
price_df = pd.read_parquet(...)
pe_ratio_df = calculate_pe(...)
sector_metrics_df = aggregate_by_sector(...)
```

### Constants
```python
# UPPER_SNAKE_CASE
MAX_RETRY_COUNT = 3
DEFAULT_CACHE_TTL = 3600
ENTITY_TYPES = ["COMPANY", "BANK", "INSURANCE", "SECURITY"]
```

---

## 2. Path Conventions (v4.0.0)

### Canonical Paths

```python
# CORRECT: Use DATA/ structure
input_path = Path("DATA/raw/ohlcv/OHLCV_mktcap.parquet")
output_path = Path("DATA/processed/valuation/pe/historical_pe.parquet")

# WRONG: Deprecated paths (95% files still using these - needs migration)
input_path = "data_warehouse/raw/..."      # NO
output_path = "calculated_results/..."      # NO
output_path = "DATA/refined/..."            # NO
```

### Using get_data_path()

```python
from PROCESSORS.core.config.paths import get_data_path

# Recommended
input_path = get_data_path("raw", "ohlcv", "OHLCV_mktcap.parquet")
output_path = get_data_path("processed", "valuation", "pe", "historical_pe.parquet")
```

### Directory Structure

```
DATA/
├── raw/                    # READ from here
│   ├── ohlcv/
│   ├── fundamental/csv/
│   ├── commodity/
│   └── macro/
└── processed/              # WRITE to here
    ├── fundamental/
    ├── technical/
    ├── valuation/
    ├── sector/
    └── forecast/
```

---

## 3. Registry Usage (CRITICAL)

### Import Pattern (Canonical)

```python
# CORRECT: Import from config/ (as of 2025-12-10)
from config.registries import MetricRegistry, SectorRegistry
from config.schema_registry import SchemaRegistry

# WRONG: Old paths (deprecated, will fail)
from PROCESSORS.core.registries.metric_lookup import MetricRegistry  # NO
from PROCESSORS.core.registries.schema_registry import SchemaRegistry  # NO
```

### MetricRegistry

```python
metric_reg = MetricRegistry()

# Get metric info
metric = metric_reg.get_metric("CIS_62", "COMPANY")

# Get calculated formula
roe_formula = metric_reg.get_calculated_metric_formula("roe")

# Search metrics
matches = metric_reg.search("revenue", entity_type="COMPANY")
```

### SectorRegistry

```python
sector_reg = SectorRegistry()

# Get ticker info
info = sector_reg.get_ticker("ACB")
# Returns: {ticker, entity_type, sector, industry}

# Get sector peers
peers = sector_reg.get_peers("ACB")
# Returns: ["TCB", "VCB", "MBB", ...]

# Get all tickers in sector
banking = sector_reg.get_tickers_by_sector("Ngân hàng")
```

### SchemaRegistry

```python
schema_reg = SchemaRegistry()

# Format values for display
formatted_price = schema_reg.format_price(25750.5)    # "25,750.50đ"
formatted_pct = schema_reg.format_percent(0.1523)      # "15.23%"
formatted_mcap = schema_reg.format_market_cap(1.5e12) # "1.5T"
```

---

## 4. Session State (CRITICAL for WEBAPP)

### Initialize Page State

```python
# CRITICAL: Call at the top of EVERY dashboard page
from WEBAPP.core.session_state import init_page_state

# Initialize page state (prevents widget interaction page resets)
init_page_state('company')  # or 'bank', 'technical', etc.
```

### Available Page States

```python
# Global state (all pages)
'global_ticker_search', 'quick_search_ticker', 'search_select'

# Company page
'selected_ticker', 'company_timeframe', 'company_active_tab'

# Bank page
'selected_bank', 'bank_timeframe', 'bank_metric', 'bank_active_tab'

# Technical page (3 tabs)
'ta_active_tab', 'ta_selected_sector', 'ta_selected_signal',
'ta_search_symbol', 'ta_timeframe', 'breadth_tf', 'rs_heatmap_top_n',
'rrg_mode', 'rrg_trail', 'money_flow_timeframe'

# Forecast page
'forecast_sector', 'forecast_rating', 'forecast_active_tab'
```

---

## 5. Data Handling

### Loading Processed Data

```python
# CORRECT: Load from processed/
company_df = pd.read_parquet("DATA/processed/fundamental/company/company_financial_metrics.parquet")
bank_df = pd.read_parquet("DATA/processed/fundamental/bank/bank_financial_metrics.parquet")
technical_df = pd.read_parquet("DATA/processed/technical/basic_data.parquet")
```

### Using Transformer Functions

```python
from PROCESSORS.transformers.financial import roe, gross_margin, yoy_growth

# Pure functions for calculations
sector_roe = roe(total_net_income, total_equity)
growth = yoy_growth(current_revenue, previous_revenue)
```

### Streamlit Caching

```python
import streamlit as st

@st.cache_data(ttl=3600)
def load_company_data():
    return pd.read_parquet("DATA/processed/fundamental/company/company_financial_metrics.parquet")

@st.cache_data(ttl=300)
def get_sector_scores():
    return pd.read_parquet("DATA/processed/sector/sector_combined_scores.parquet")
```

---

## 6. Error Handling

### Standard Pattern

```python
import logging

logger = logging.getLogger(__name__)

def process_data(ticker: str) -> pd.DataFrame:
    try:
        data = load_data(ticker)
        result = calculate_metrics(data)
        return result
    except FileNotFoundError:
        logger.warning(f"Data file not found for {ticker}")
        return pd.DataFrame()
    except ValueError as e:
        logger.error(f"Invalid data for {ticker}: {e}")
        raise
```

### API Retry Pattern

```python
from PROCESSORS.api.core.retry_handler import RetryHandler, RetryConfig

config = RetryConfig(max_retries=3, base_delay=1.0)
handler = RetryHandler(config)

@handler.with_retry
def fetch_data(ticker: str) -> dict:
    return api_client.get(f"/stock/{ticker}")
```

---

## 7. Type Hints

```python
from typing import Optional, List, Dict
import pandas as pd

def get_sector_metrics(
    sector: str,
    metrics: Optional[List[str]] = None,
    period: str = "Quarterly"
) -> pd.DataFrame:
    """
    Get aggregated metrics for a sector.

    Args:
        sector: Sector name (Vietnamese)
        metrics: List of metric codes to include
        period: "Quarterly" or "Yearly"

    Returns:
        DataFrame with sector-level metrics
    """
    ...
```

---

## 8. Docstrings

### Function Docstring

```python
def calculate_pe_ratio(
    market_cap: float,
    ttm_earnings: float
) -> float:
    """
    Calculate Price-to-Earnings ratio.

    PE = Market Cap / TTM Earnings

    Args:
        market_cap: Market capitalization in VND
        ttm_earnings: Trailing 12-month earnings in VND

    Returns:
        PE ratio (dimensionless)

    Raises:
        ValueError: If ttm_earnings is zero or negative
    """
    if ttm_earnings <= 0:
        raise ValueError("TTM earnings must be positive")
    return market_cap / ttm_earnings
```

### Class Docstring

```python
class SectorProcessor:
    """
    Orchestrates sector-level analysis pipeline.

    Pipeline steps:
        1. Load registries (Metric, Sector)
        2. Aggregate fundamental metrics by sector
        3. Aggregate valuation metrics by sector
        4. Score FA and TA metrics
        5. Generate Buy/Sell/Hold signals

    Attributes:
        metric_registry: MetricRegistry instance
        sector_registry: SectorRegistry instance
        output_dir: Path for output files
    """
```

---

## 9. Import Order

```python
# 1. Standard library
import os
import logging
from pathlib import Path
from typing import Optional, List

# 2. Third-party
import pandas as pd
import numpy as np
import streamlit as st

# 3. Local - config
from config.registries import MetricRegistry, SectorRegistry
from config.schema_registry import SchemaRegistry

# 4. Local - processors
from PROCESSORS.core.shared.unified_mapper import UnifiedTickerMapper
from PROCESSORS.transformers.financial import roe, gross_margin
```

---

## 10. Unit Standards

### Storage Layer (Raw Values)

```python
# Store in original units - NO conversion
revenue_vnd = 2_500_000_000_000  # VND (not billions)
roe_decimal = 0.1523              # Decimal (not %)
eps_vnd = 15234                   # VND/share
pe_ratio = 15.23                  # Times (x)
```

### Display Layer (Formatted)

```python
# UI handles formatting
schema_reg = SchemaRegistry()

display_revenue = schema_reg.format_market_cap(revenue_vnd)  # "2.5T VND"
display_roe = schema_reg.format_percent(roe_decimal)         # "15.23%"
display_eps = schema_reg.format_price(eps_vnd)               # "15,234đ"
display_pe = f"{pe_ratio:.2f}x"                              # "15.23x"
```

---

## 11. Git Commit Messages

```bash
# Format: type(scope): description

# Types
feat:     New feature
fix:      Bug fix
docs:     Documentation
refactor: Code refactoring
test:     Tests
chore:    Maintenance

# Examples
feat(api): Add WiChart client for commodity data
fix(valuation): Handle zero TTM earnings in PE calculation
docs: Update system architecture diagram
refactor(sector): Extract scoring logic to separate module
```

---

## Related Documents

- [Project Overview](project-overview-pdr.md)
- [Codebase Summary](codebase-summary.md)
- [System Architecture](system-architecture.md)
- [CLAUDE.md](../CLAUDE.md) - AI/Developer guidelines (CRITICAL)
