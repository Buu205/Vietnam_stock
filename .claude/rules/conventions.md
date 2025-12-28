# Code Conventions

Standard coding conventions and style guide for the Vietnam Dashboard project.

---

## File & Module Naming

```python
# Files and modules
my_module.py                 # ✅ snake_case
my-module.py                 # ❌ kebab-case (Python doesn't support)
MyModule.py                  # ❌ PascalCase

# Classes
class MetricRegistry:        # ✅ PascalCase
class metric_registry:       # ❌ snake_case

# Functions and variables
def calculate_roe():         # ✅ snake_case
def calculateROE():          # ❌ camelCase

# DataFrame variables (descriptive + _df suffix)
price_df = pd.DataFrame()    # ✅ Clear and descriptive
df1 = pd.DataFrame()         # ❌ Not descriptive
priceData = pd.DataFrame()   # ❌ Not snake_case
```

---

## Import Standards

### Import Order

```python
# 1. Standard library
import os
from pathlib import Path
from datetime import datetime

# 2. Third-party packages
import pandas as pd
import numpy as np
import streamlit as st

# 3. Local application imports
from config.registries import MetricRegistry, SectorRegistry
from PROCESSORS.transformers.financial import roe, gross_margin
```

### Canonical Import Locations

```python
# ✅ CORRECT (as of 2025-12-10)
from config.registries import MetricRegistry, SectorRegistry
from config.schema_registry import SchemaRegistry
from PROCESSORS.core.config.paths import get_data_path

# ❌ DEPRECATED (will fail)
from PROCESSORS.core.registries.metric_lookup import MetricRegistry
from PROCESSORS.core.registries.schema_registry import SchemaRegistry
```

---

## Path Resolution Standards

### Using Centralized Path Helper

```python
from PROCESSORS.core.config.paths import get_data_path

# ✅ RECOMMENDED: Use helper function
input_path = get_data_path("raw", "ohlcv", "OHLCV_mktcap.parquet")
output_path = get_data_path("processed", "valuation", "pe", "pe_historical.parquet")
```

### Manual Path Construction

```python
from pathlib import Path

# ✅ ACCEPTABLE: Manual but correct
data_path = Path("DATA") / "processed" / "fundamental" / "company"
input_file = Path("DATA/raw/ohlcv/OHLCV_mktcap.parquet")

# ❌ WRONG: Deprecated paths
data_path = Path("calculated_results/fundamental/company")
input_file = Path("data_warehouse/raw/ohlcv/OHLCV_mktcap.parquet")
```

---

## DataFrame Conventions

### Naming DataFrames

```python
# ✅ GOOD: Descriptive names with _df suffix
company_metrics_df = pd.read_parquet(...)
pe_ratio_df = pd.read_parquet(...)
price_history_df = pd.read_parquet(...)

# ❌ BAD: Generic or unclear names
df = pd.read_parquet(...)
data = pd.read_parquet(...)
temp_df = pd.read_parquet(...)
```

### Column Naming

```python
# ✅ GOOD: snake_case, descriptive
df.columns = ['ticker', 'date', 'close_price', 'market_cap', 'pe_ratio']

# ❌ BAD: Inconsistent casing
df.columns = ['Ticker', 'Date', 'closePrice', 'MarketCap', 'PE']
```

---

## Function & Class Documentation

### Docstrings (Google Style)

```python
def calculate_sector_roe(sector: str, period: str = "Quarterly") -> float:
    """Calculate average ROE for a sector.

    Args:
        sector: Sector name (Vietnamese, e.g., "Ngân hàng")
        period: "Quarterly" or "Yearly" (default: Quarterly)

    Returns:
        Average ROE as decimal (e.g., 0.15 for 15%)

    Raises:
        ValueError: If sector not found

    Example:
        >>> calculate_sector_roe("Ngân hàng", "Yearly")
        0.156
    """
    pass
```

### Type Hints

```python
# ✅ GOOD: Full type hints
def get_ticker_info(ticker: str) -> dict[str, Any]:
    pass

def calculate_pe(market_cap: float, earnings: float) -> float:
    pass

# ❌ BAD: No type hints
def get_ticker_info(ticker):
    pass
```

---

## Error Handling

### Specific Exceptions

```python
# ✅ GOOD: Catch specific exceptions
try:
    data = pd.read_parquet(path)
except FileNotFoundError:
    logger.error(f"File not found: {path}")
    raise
except pd.errors.ParserError:
    logger.error(f"Failed to parse: {path}")
    raise

# ❌ BAD: Catch all
try:
    data = pd.read_parquet(path)
except Exception as e:
    pass  # Silent failure
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

# ✅ GOOD: Structured logging
logger.info(f"Processing {len(tickers)} tickers")
logger.warning(f"Missing data for {ticker}")
logger.error(f"Failed to calculate PE: {e}", exc_info=True)

# ❌ BAD: Print statements
print("Processing tickers...")  # Not for production code
```

---

## Data Processing Patterns

### Parquet File I/O

```python
import pandas as pd
from pathlib import Path

# ✅ GOOD: Type-safe, uses Path
def save_metrics(df: pd.DataFrame, filename: str) -> None:
    output_path = Path("DATA/processed/fundamental/company") / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False, compression='snappy')

def load_metrics(filename: str) -> pd.DataFrame:
    input_path = Path("DATA/processed/fundamental/company") / filename
    if not input_path.exists():
        raise FileNotFoundError(f"File not found: {input_path}")
    return pd.read_parquet(input_path)
```

### Date Handling

```python
from datetime import datetime
import pandas as pd

# ✅ GOOD: Consistent date format
df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
latest_date = df['date'].max().strftime('%Y-%m-%d')

# Store dates as strings in parquet
df['date'] = df['date'].dt.strftime('%Y-%m-%d')
```

---

## Code Organization

### Module Structure

```python
# Top of file: Imports
import pandas as pd
from pathlib import Path

from config.registries import MetricRegistry
from PROCESSORS.transformers.financial import roe

# Constants
SECTORS = ["Ngân hàng", "Bất động sản", "Công nghệ"]
DEFAULT_PERIOD = "Quarterly"

# Classes
class SectorAnalyzer:
    pass

# Functions
def calculate_sector_metrics():
    pass

# Main execution
if __name__ == "__main__":
    pass
```

### File Size Guidelines

- Single module: < 500 lines
- If > 500 lines, consider splitting into multiple modules
- Use subdirectories to organize related modules

---

## Testing Conventions

### Test File Naming

```python
# Production code
PROCESSORS/fundamental/calculators/company_calculator.py

# Test file (same directory or tests/)
tests/fundamental/test_company_calculator.py

# Test function naming
def test_calculate_roe_with_valid_data():
    pass

def test_calculate_roe_with_zero_equity_raises_error():
    pass
```

---

## Constants & Configuration

```python
# ✅ GOOD: Use ALL_CAPS for constants
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30
SECTOR_WEIGHTS = {
    "Ngân hàng": 0.25,
    "Bất động sản": 0.15,
}

# ❌ BAD: Regular variables
max_retries = 3
defaultTimeout = 30
```

---

## Summary

| Convention | Standard | Example |
|------------|----------|---------|
| Files/Modules | `snake_case` | `company_calculator.py` |
| Classes | `PascalCase` | `MetricRegistry` |
| Functions/Variables | `snake_case` | `calculate_roe()` |
| Constants | `ALL_CAPS` | `MAX_RETRIES` |
| DataFrames | `snake_case_df` | `price_history_df` |
| Imports | Canonical locations | `from config.registries import...` |
| Paths | v4.0.0 standard | `DATA/processed/` |
| Docstrings | Google Style | See example above |
| Type Hints | Always | `def func(x: int) -> str:` |

**Consistency is key. Follow these conventions in ALL new code.**
