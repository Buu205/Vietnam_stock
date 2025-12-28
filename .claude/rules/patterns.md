# Technical Patterns (MUST FOLLOW)

Design patterns and best practices for common tasks in the Vietnam Dashboard project.

---

## Pattern 1: ALWAYS Use Registries

The registry system is the **single source of truth** for metrics, sectors, and tickers.

### MetricRegistry Pattern

```python
from config.registries import MetricRegistry

# Initialize registry (singleton)
metric_reg = MetricRegistry()

# Get raw metric info (Vietnamese name → English name)
metric = metric_reg.get_metric("CIS_62", "COMPANY")
# Returns: {
#     "vietnamese_name": "Lợi nhuận sau thuế",
#     "english_name": "Net Income After Tax",
#     "unit": "billion_vnd",
#     "category": "profitability"
# }

# Get calculated metric formula
roe_formula = metric_reg.get_calculated_metric_formula("roe")
# Returns formula and dependencies

# Search metrics
profit_metrics = metric_reg.search_metrics("profit", entity_type="COMPANY")
```

### SectorRegistry Pattern

```python
from config.registries import SectorRegistry

# Initialize registry
sector_reg = SectorRegistry()

# Get ticker information
ticker_info = sector_reg.get_ticker("ACB")
# Returns: {
#     "ticker": "ACB",
#     "company_name": "Ngân hàng TMCP Á Châu",
#     "entity_type": "BANK",
#     "sector": "Ngân hàng",
#     "industry": "Ngân hàng thương mại"
# }

# Get peer companies (same sector)
peers = sector_reg.get_peers("ACB", limit=10)
# Returns: ["VCB", "BID", "CTG", "MBB", "TCB", ...]

# Get all tickers in a sector
banking_tickers = sector_reg.get_tickers_by_sector("Ngân hàng")

# Validate ticker exists
if sector_reg.is_valid_ticker("XYZ"):
    process_ticker("XYZ")
```

### SchemaRegistry Pattern

```python
from config.schema_registry import SchemaRegistry

# Initialize registry (singleton)
schema_reg = SchemaRegistry()

# Get schema
ohlcv_schema = schema_reg.get_schema('ohlcv')
fundamental_schema = schema_reg.get_schema('fundamental', entity_type='company')

# Format values using schema
formatted_price = schema_reg.format_price(25750.5)  # "25,750.50đ"
formatted_percent = schema_reg.format_percent(0.156)  # "15.60%"
formatted_number = schema_reg.format_number(1234567890)  # "1,234,567,890"
```

---

## Pattern 2: Use Existing Calculators (Don't Duplicate)

**NEVER reimplement existing calculations.** Always check if calculator exists first.

### Loading Calculated Results

```python
import pandas as pd
from pathlib import Path

# ✅ GOOD: Load existing calculated results
def get_company_metrics() -> pd.DataFrame:
    path = Path("DATA/processed/fundamental/company/company_financial_metrics.parquet")
    return pd.read_parquet(path)

def get_bank_metrics() -> pd.DataFrame:
    path = Path("DATA/processed/fundamental/bank/bank_financial_metrics.parquet")
    return pd.read_parquet(path)

def get_technical_data(ticker: str) -> pd.DataFrame:
    path = Path("DATA/processed/technical/basic_data.parquet")
    df = pd.read_parquet(path)
    return df[df['ticker'] == ticker]
```

### Available Calculators

| Calculator | Location | Purpose |
|------------|----------|---------|
| **CompanyCalculator** | `PROCESSORS/fundamental/calculators/company_calculator.py` | Company financials (ROE, margins, growth) |
| **BankCalculator** | `PROCESSORS/fundamental/calculators/bank_calculator.py` | Bank metrics (NIM, NPL, CAR, CASA) |
| **InsuranceCalculator** | `PROCESSORS/fundamental/calculators/insurance_calculator.py` | Insurance metrics |
| **SecurityCalculator** | `PROCESSORS/fundamental/calculators/security_calculator.py` | Brokerage metrics |
| **PECalculator** | `PROCESSORS/valuation/calculators/vnindex_pe_calculator_optimized.py` | PE ratios (VN-Index, sectors, stocks) |
| **PBCalculator** | `PROCESSORS/valuation/calculators/vnindex_pb_calculator_optimized.py` | PB ratios |
| **EVEBITDACalculator** | `PROCESSORS/valuation/calculators/ev_ebitda_calculator_optimized.py` | EV/EBITDA ratios |

### When You Need NEW Calculations

If calculation doesn't exist, use transformer functions (pure functions):

```python
from PROCESSORS.transformers.financial import (
    roe,
    roa,
    gross_margin,
    net_margin,
    yoy_growth,
    debt_to_equity
)

# ✅ GOOD: Use pure transformer functions
sector_avg_roe = roe(total_net_income, total_equity)
sector_growth = yoy_growth(current_revenue, previous_revenue)
sector_margin = net_margin(net_income, revenue)
```

---

## Pattern 3: Transformer Functions (Pure Functions)

Transformers are **pure functions** that perform calculations without side effects.

### Transformer Pattern

```python
from PROCESSORS.transformers.financial.formulas import (
    roe,
    roa,
    gross_margin,
    net_margin,
    yoy_growth,
    qoq_growth
)

# ✅ GOOD: Pure function usage
def calculate_sector_metrics(sector_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate aggregated sector metrics from individual company data."""

    # Aggregate sector totals
    total_net_income = sector_df['net_income'].sum()
    total_equity = sector_df['equity'].sum()
    total_revenue = sector_df['revenue'].sum()

    # Calculate using pure functions
    sector_roe = roe(total_net_income, total_equity)
    sector_roa = roa(total_net_income, sector_df['assets'].sum())
    sector_margin = net_margin(total_net_income, total_revenue)

    return pd.DataFrame({
        'sector': [sector_df['sector'].iloc[0]],
        'roe': [sector_roe],
        'roa': [sector_roa],
        'net_margin': [sector_margin]
    })
```

### Available Transformer Functions

**Location:** `PROCESSORS/transformers/financial/formulas.py`

| Function | Formula | Returns |
|----------|---------|---------|
| `roe(net_income, equity)` | Net Income / Equity | Decimal (e.g., 0.15 for 15%) |
| `roa(net_income, assets)` | Net Income / Assets | Decimal |
| `gross_margin(gross_profit, revenue)` | Gross Profit / Revenue | Decimal |
| `net_margin(net_income, revenue)` | Net Income / Revenue | Decimal |
| `yoy_growth(current, previous)` | (Current - Previous) / Previous | Decimal |
| `qoq_growth(current, previous)` | (Current - Previous) / Previous | Decimal |
| `debt_to_equity(debt, equity)` | Debt / Equity | Ratio |

---

## Pattern 4: Data Loading Pipeline

Standard pattern for loading and processing data.

### Complete Pipeline Pattern

```python
from pathlib import Path
import pandas as pd
from config.registries import SectorRegistry

class DataLoader:
    """Standard data loading pattern."""

    def __init__(self):
        self.sector_reg = SectorRegistry()
        self.data_root = Path("DATA/processed")

    def load_fundamental_data(self, entity_type: str) -> pd.DataFrame:
        """Load fundamental data by entity type."""
        path = self.data_root / "fundamental" / entity_type.lower()
        filename = f"{entity_type.lower()}_financial_metrics.parquet"
        return pd.read_parquet(path / filename)

    def load_sector_data(self, sector: str) -> pd.DataFrame:
        """Load data for all tickers in a sector."""
        tickers = self.sector_reg.get_tickers_by_sector(sector)

        # Load company data
        company_df = self.load_fundamental_data("company")

        # Filter by sector tickers
        return company_df[company_df['ticker'].isin(tickers)]

    def load_technical_data(self, ticker: str, days: int = 252) -> pd.DataFrame:
        """Load technical data for a ticker."""
        path = self.data_root / "technical" / "basic_data.parquet"
        df = pd.read_parquet(path)

        # Filter and sort
        ticker_df = df[df['ticker'] == ticker].sort_values('date', ascending=False)
        return ticker_df.head(days)
```

---

## Pattern 5: Error Handling & Validation

Standard error handling patterns.

### Input Validation Pattern

```python
from config.registries import SectorRegistry

def validate_ticker(ticker: str) -> None:
    """Validate ticker exists."""
    sector_reg = SectorRegistry()

    if not sector_reg.is_valid_ticker(ticker):
        raise ValueError(f"Invalid ticker: {ticker}")

def validate_period(period: str) -> None:
    """Validate period parameter."""
    valid_periods = ["Quarterly", "Yearly"]
    if period not in valid_periods:
        raise ValueError(f"Period must be one of {valid_periods}, got: {period}")

def validate_date_format(date_str: str) -> None:
    """Validate date format."""
    from datetime import datetime

    try:
        datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        raise ValueError(f"Date must be in YYYY-MM-DD format, got: {date_str}")
```

### Data Validation Pattern

```python
def validate_financial_data(df: pd.DataFrame) -> pd.DataFrame:
    """Validate and clean financial data."""

    # Check required columns
    required_cols = ['ticker', 'date', 'revenue', 'net_income']
    missing_cols = set(required_cols) - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    # Remove invalid data
    df = df[
        (df['revenue'] > 0) &
        (df['net_income'].notna())
    ].copy()

    # Sort by date
    df = df.sort_values(['ticker', 'date'])

    return df
```

---

## Pattern 6: Caching & Performance

Standard caching patterns for performance optimization.

### Streamlit Caching Pattern

```python
import streamlit as st
import pandas as pd
from pathlib import Path

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_company_metrics() -> pd.DataFrame:
    """Load company metrics with caching."""
    path = Path("DATA/processed/fundamental/company/company_financial_metrics.parquet")
    return pd.read_parquet(path)

@st.cache_data(ttl=86400)  # Cache for 24 hours
def load_sector_mapping() -> dict:
    """Load sector mapping with long-term caching."""
    from config.registries import SectorRegistry
    sector_reg = SectorRegistry()
    return sector_reg.get_all_sectors()

@st.cache_resource
def get_registry() -> tuple:
    """Cache registry instances (singleton pattern)."""
    from config.registries import MetricRegistry, SectorRegistry
    return MetricRegistry(), SectorRegistry()
```

---

## Pattern 7: Logging Standards

Standard logging pattern.

### Logging Setup Pattern

```python
import logging
from pathlib import Path

def setup_logger(name: str, log_file: str = None) -> logging.Logger:
    """Set up logger with console and file handlers."""

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        log_path = Path("logs") / log_file
        log_path.parent.mkdir(exist_ok=True)
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(console_format)
        logger.addHandler(file_handler)

    return logger

# Usage
logger = setup_logger(__name__, "company_calculator.log")
logger.info("Starting calculation...")
logger.warning(f"Missing data for ticker: {ticker}")
logger.error(f"Failed to calculate metric: {e}", exc_info=True)
```

---

## Summary: Key Patterns

| Pattern | When to Use | Example |
|---------|-------------|---------|
| **Registry** | Looking up metrics, sectors, tickers | `MetricRegistry().get_metric("CIS_62")` |
| **Calculators** | Loading existing results | `pd.read_parquet("DATA/processed/...")` |
| **Transformers** | New calculations | `roe(net_income, equity)` |
| **Data Loading** | Standard data access | `DataLoader().load_sector_data("Ngân hàng")` |
| **Validation** | Input checking | `validate_ticker("ACB")` |
| **Caching** | Performance optimization | `@st.cache_data(ttl=3600)` |
| **Logging** | Debugging & monitoring | `logger.info("Processing...")` |

**Follow these patterns for consistency and maintainability.**
