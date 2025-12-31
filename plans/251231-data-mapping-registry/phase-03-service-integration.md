# Phase 3: Service Integration (Interface Adapters)

**Est. Time:** 4 hours | **Priority:** High | **Dependencies:** Phase 2 complete

## Context

With registry operational, update existing services to use `DataMappingRegistry` instead of hardcoded paths. This is the Interface Adapters layer - bridging Use Cases to external frameworks.

## Overview

1. Create `BaseService` with registry integration
2. Update `BankService`, `CompanyService`, etc. to extend `BaseService`
3. Remove hardcoded paths from all services
4. Add schema validation before data load

## Requirements

1. Backward compatible - existing code must work unchanged
2. Services get paths from registry, not hardcoded strings
3. Schema validation warns (not fails) on missing columns
4. Services declare their data dependencies explicitly

## Architecture

```
WEBAPP/services/
├── base_service.py      # NEW: BaseService with registry
├── bank_service.py      # UPDATED: extends BaseService
├── company_service.py   # UPDATED: extends BaseService
├── valuation_service.py # UPDATED: extends BaseService
└── ...
```

## Implementation Steps

### Step 1: Create BaseService

**File:** `WEBAPP/services/base_service.py`

```python
"""
Base Service with Registry Integration
=======================================

All services extend this base class to get:
- Automatic path resolution via DataMappingRegistry
- Schema validation on data load
- Cache TTL from config
- Consistent error handling

Usage:
    class BankService(BaseService):
        DATA_SOURCE = "bank_metrics"

        def get_data(self):
            df = self.load_data()  # Uses registry path
            return df
"""

import pandas as pd
from pathlib import Path
from typing import Optional, Type
from abc import ABC
import logging

logger = logging.getLogger(__name__)


class BaseService(ABC):
    """
    Abstract base service with registry integration.

    Subclasses should define:
        DATA_SOURCE: str - Name of data source in registry
        ENTITY_TYPE: str - Entity type (bank, company, insurance, security)
    """

    DATA_SOURCE: str = ""  # Override in subclass
    ENTITY_TYPE: str = ""  # Override in subclass

    def __init__(self, data_root: Optional[Path] = None):
        """
        Initialize service with optional data root override.

        Args:
            data_root: Override DATA directory (for testing)
        """
        self._registry = None
        self._resolver = None
        self._data_root = data_root
        self._cached_path: Optional[Path] = None

    @property
    def registry(self):
        """Lazy load registry."""
        if self._registry is None:
            from config.data_mapping import get_registry
            self._registry = get_registry()
        return self._registry

    @property
    def resolver(self):
        """Lazy load path resolver."""
        if self._resolver is None:
            from config.data_mapping import PathResolver
            self._resolver = PathResolver(self.registry)
        return self._resolver

    def get_data_path(self) -> Path:
        """
        Get path to data file via registry.

        Returns:
            Path to data file

        Raises:
            ValueError: If DATA_SOURCE not defined
            KeyError: If source not in registry
        """
        if not self.DATA_SOURCE:
            raise ValueError(
                f"{self.__class__.__name__} must define DATA_SOURCE"
            )

        if self._cached_path is None:
            if self._data_root:
                # Use override path for testing
                relative = self.registry.get_path(self.DATA_SOURCE)
                # relative is like DATA/processed/...
                # Strip DATA/ prefix and join with custom root
                relative_str = str(relative).replace("DATA/", "")
                self._cached_path = self._data_root / relative_str
            else:
                self._cached_path = self.resolver.resolve(
                    self.DATA_SOURCE, validate=False
                )

        return self._cached_path

    def get_schema(self) -> tuple[str, ...]:
        """Get expected columns for this service's data source."""
        if not self.DATA_SOURCE:
            return ()
        return self.registry.get_schema(self.DATA_SOURCE)

    def get_cache_ttl(self) -> int:
        """Get cache TTL in seconds."""
        if not self.DATA_SOURCE:
            return 3600
        return self.registry.get_cache_ttl(self.DATA_SOURCE)

    def load_data(
        self,
        columns: Optional[list[str]] = None,
        validate_schema: bool = True
    ) -> pd.DataFrame:
        """
        Load data from parquet file.

        Args:
            columns: Optional list of columns to load (for efficiency)
            validate_schema: If True, warn on missing expected columns

        Returns:
            DataFrame with data

        Raises:
            FileNotFoundError: If data file doesn't exist
        """
        path = self.get_data_path()

        if not path.exists():
            raise FileNotFoundError(
                f"Data file not found: {path}\n"
                f"Service: {self.__class__.__name__}\n"
                f"Data Source: {self.DATA_SOURCE}"
            )

        # Load data
        df = pd.read_parquet(path, columns=columns)

        # Validate schema
        if validate_schema:
            self._validate_schema(df)

        return df

    def _validate_schema(self, df: pd.DataFrame) -> None:
        """
        Validate DataFrame has expected columns.

        Logs warning for missing columns (doesn't raise).
        """
        expected = set(self.get_schema())
        if not expected:
            return

        actual = set(df.columns.tolist())
        missing = expected - actual

        if missing:
            logger.warning(
                f"{self.__class__.__name__}: Missing expected columns: {missing}"
            )

    def validate_data_exists(self) -> bool:
        """Check if data file exists."""
        try:
            path = self.get_data_path()
            return path.exists()
        except Exception:
            return False
```

### Step 2: Update BankService

**File:** `WEBAPP/services/bank_service.py` (UPDATED)

```python
"""
Bank Service - Data Loading Layer
=================================

Service for loading bank financial data from parquet files.
Now uses DataMappingRegistry for path resolution.

Usage:
    from WEBAPP.services.bank_service import BankService

    service = BankService()
    df = service.get_financial_data("ACB", "Quarterly")
"""

import pandas as pd
from pathlib import Path
from typing import Optional, Dict, List

from .base_service import BaseService


class BankService(BaseService):
    """Service layer for Bank financial data."""

    DATA_SOURCE = "bank_metrics"
    ENTITY_TYPE = "bank"

    def __init__(self, data_root: Optional[Path] = None):
        """
        Initialize BankService.

        Args:
            data_root: Root data directory (for testing, defaults to registry path)
        """
        super().__init__(data_root)
        self._master_symbols = None

    def _load_master_symbols(self) -> List[str]:
        """Load master symbols filtered list for BANK entity."""
        if self._master_symbols is not None:
            return self._master_symbols

        import json

        # Determine project root from data path
        data_path = self.get_data_path()
        project_root = data_path.parents[4]  # Go up to project root

        locations = [
            project_root / "config" / "metadata" / "master_symbols.json",
            project_root / "DATA" / "metadata" / "master_symbols.json",
        ]

        for master_file in locations:
            if master_file.exists():
                with open(master_file) as f:
                    data = json.load(f)
                self._master_symbols = data.get('symbols_by_entity', {}).get('BANK', [])
                return self._master_symbols

        self._master_symbols = []
        return self._master_symbols

    def get_financial_data(
        self,
        ticker: str,
        period: str = "Quarterly",
        limit: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Load financial data for a bank ticker.

        Args:
            ticker: Stock symbol (e.g., "ACB", "VCB", "TCB")
            period: "Quarterly" or "Yearly"
            limit: Maximum number of records to return (most recent)

        Returns:
            DataFrame with financial metrics sorted by date
        """
        # Use base class load_data() - gets path from registry
        df = self.load_data()

        # Filter by ticker
        df = df[df['symbol'] == ticker].copy()

        if df.empty:
            return pd.DataFrame()

        # Filter by period
        if period == "Quarterly":
            df = df[df['freq_code'] == 'Q']
        elif period == "Yearly":
            df = df[df['freq_code'] == 'Y']

        df = df.sort_values('report_date')

        if limit:
            df = df.tail(limit)

        return df

    def get_latest_metrics(self, ticker: str) -> Dict:
        """Get latest quarter metrics for a bank ticker."""
        df = self.get_financial_data(ticker, "Quarterly", limit=1)
        return df.iloc[-1].to_dict() if not df.empty else {}

    def get_available_tickers(self) -> List[str]:
        """Get list of available bank tickers (filtered by master_symbols for liquidity)."""
        df = self.load_data(columns=['symbol'])
        all_tickers = set(df['symbol'].unique().tolist())

        # Filter by master symbols (liquid tickers only)
        master_symbols = self._load_master_symbols()
        if master_symbols:
            filtered = [t for t in master_symbols if t in all_tickers]
            return sorted(filtered)

        return sorted(all_tickers)

    def get_peer_comparison(self, ticker: str) -> pd.DataFrame:
        """Get peer comparison data for banks."""
        try:
            from config.registries import SectorRegistry

            sector_reg = SectorRegistry()
            peers = sector_reg.get_peers(ticker)

            dfs = []
            for peer in peers:
                peer_df = self.get_financial_data(peer, "Quarterly", limit=1)
                if not peer_df.empty:
                    dfs.append(peer_df.iloc[-1])

            return pd.DataFrame(dfs) if dfs else pd.DataFrame()

        except Exception as e:
            print(f"Warning: Could not load peer comparison - {e}")
            return pd.DataFrame()
```

### Step 3: Update CompanyService (Similar Pattern)

**File:** `WEBAPP/services/company_service.py` (UPDATED)

Key changes:
1. Extend `BaseService`
2. Define `DATA_SOURCE = "company_metrics"`
3. Replace `self.data_path / "company_financial_metrics.parquet"` with `self.load_data()`

```python
"""
Company Service - Data Loading Layer
====================================

Updated to use DataMappingRegistry.
"""

import pandas as pd
from pathlib import Path
from typing import Optional, Dict, List

from .base_service import BaseService

# Column groups for efficient data loading
COLUMN_GROUPS = {
    'meta': ['symbol', 'report_date', 'year', 'quarter', 'freq_code'],
    'income_statement': [
        'symbol', 'report_date', 'year', 'quarter', 'freq_code',
        'net_revenue', 'cogs', 'gross_profit', 'sga', 'ebit',
        'ebitda', 'ebt', 'npatmi', 'net_finance_income', 'depreciation',
        'gross_profit_margin', 'ebit_margin', 'ebitda_margin', 'net_margin',
    ],
    'balance_sheet': [
        'symbol', 'report_date', 'year', 'quarter', 'freq_code',
        'total_assets', 'total_liabilities', 'total_equity',
        'current_assets', 'current_liabilities', 'cash',
        'debt_to_equity', 'debt_to_assets',
    ],
    'cash_flow': [
        'symbol', 'report_date', 'year', 'quarter', 'freq_code',
        'operating_cf', 'investment_cf', 'financing_cf', 'capex',
        'depreciation', 'fcf',
    ],
    'ratios': [
        'symbol', 'report_date', 'year', 'quarter', 'freq_code',
        'roe', 'roa', 'asset_turnover', 'eps', 'bvps'
    ]
}


class CompanyService(BaseService):
    """Service layer for Company financial data."""

    DATA_SOURCE = "company_metrics"
    ENTITY_TYPE = "company"

    def __init__(self, data_root: Optional[Path] = None):
        super().__init__(data_root)
        self._master_symbols = None

    def _load_master_symbols(self) -> List[str]:
        """Load master symbols filtered list for COMPANY entity."""
        if self._master_symbols is not None:
            return self._master_symbols

        import json

        data_path = self.get_data_path()
        project_root = data_path.parents[4]

        locations = [
            project_root / "config" / "metadata" / "master_symbols.json",
            project_root / "DATA" / "metadata" / "master_symbols.json",
        ]

        for master_file in locations:
            if master_file.exists():
                with open(master_file) as f:
                    data = json.load(f)
                self._master_symbols = data.get('symbols_by_entity', {}).get('COMPANY', [])
                return self._master_symbols

        self._master_symbols = []
        return self._master_symbols

    def get_financial_data(
        self,
        ticker: str,
        period: str = "Quarterly",
        limit: Optional[int] = None,
        table_type: str = "all"
    ) -> pd.DataFrame:
        """Load financial data for a company ticker."""
        # Determine columns to load
        columns = None
        if table_type != "all" and table_type in COLUMN_GROUPS:
            columns = COLUMN_GROUPS[table_type]

        # Use base class - gets path from registry
        df = self.load_data(columns=columns)

        # Filter by ticker
        df = df[df['symbol'] == ticker].copy()

        if df.empty:
            return pd.DataFrame()

        # Filter by period
        if period == "Quarterly":
            df = df[df['freq_code'] == 'Q']
        elif period == "Yearly":
            df = df[df['freq_code'] == 'Y']

        df = df.sort_values('report_date')

        if limit:
            df = df.tail(limit)

        return df

    def get_latest_metrics(self, ticker: str) -> Dict:
        """Get latest quarter metrics for a ticker."""
        df = self.get_financial_data(ticker, "Quarterly", limit=1)
        return df.iloc[-1].to_dict() if not df.empty else {}

    def get_available_tickers(self) -> List[str]:
        """Get list of available company tickers."""
        df = self.load_data(columns=['symbol'])
        all_tickers = set(df['symbol'].unique().tolist())

        master_symbols = self._load_master_symbols()
        if master_symbols:
            filtered = [t for t in master_symbols if t in all_tickers]
            return sorted(filtered)

        return sorted(all_tickers)

    def get_peer_comparison(self, ticker: str) -> pd.DataFrame:
        """Get peer comparison data."""
        try:
            from config.registries import SectorRegistry

            sector_reg = SectorRegistry()
            peers = sector_reg.get_peers(ticker)

            dfs = []
            for peer in peers:
                peer_df = self.get_financial_data(peer, "Quarterly", limit=1)
                if not peer_df.empty:
                    dfs.append(peer_df.iloc[-1])

            return pd.DataFrame(dfs) if dfs else pd.DataFrame()

        except Exception as e:
            print(f"Warning: Could not load peer comparison - {e}")
            return pd.DataFrame()
```

### Step 4: Update Other Services

Apply same pattern to:
- `valuation_service.py` - DATA_SOURCE = "pe_historical" (or multiple)
- `technical_service.py` - DATA_SOURCE = "ohlcv_raw"
- `forecast_service.py` - DATA_SOURCE = "bsc_forecast"
- `security_service.py` - DATA_SOURCE = "security_metrics"

For services with multiple data sources, override `load_data()` or use helper methods.

### Step 5: Update services/__init__.py

**File:** `WEBAPP/services/__init__.py` (UPDATED)

```python
"""
Services Layer
==============

Data loading services using DataMappingRegistry.
"""

from .base_service import BaseService
from .bank_service import BankService
from .company_service import CompanyService
# ... other services

__all__ = [
    'BaseService',
    'BankService',
    'CompanyService',
    # ...
]
```

## Migration Checklist

| Service | DATA_SOURCE | Extends BaseService | Tested |
|---------|-------------|---------------------|--------|
| BankService | bank_metrics | [ ] | [ ] |
| CompanyService | company_metrics | [ ] | [ ] |
| ValuationService | pe_historical | [ ] | [ ] |
| TechnicalService | ohlcv_raw | [ ] | [ ] |
| ForecastService | bsc_forecast | [ ] | [ ] |
| SecurityService | security_metrics | [ ] | [ ] |
| InsuranceService | insurance_metrics | [ ] | [ ] |

## Success Criteria

- [ ] All services extend BaseService
- [ ] No hardcoded paths in service files
- [ ] Existing API unchanged (backward compatible)
- [ ] Schema validation logs warnings for missing columns
- [ ] All existing tests pass

## Test Script

```python
# tests/test_service_integration.py
from WEBAPP.services import BankService, CompanyService

def test_bank_service_uses_registry():
    service = BankService()
    path = service.get_data_path()
    assert "bank_financial_metrics.parquet" in str(path)

def test_company_service_backward_compatible():
    service = CompanyService()
    df = service.get_financial_data("VNM", "Quarterly", limit=1)
    assert not df.empty or service.validate_data_exists() is False

def test_service_schema_validation():
    service = BankService()
    schema = service.get_schema()
    assert "symbol" in schema
    assert "nim" in schema
```

## Rollback Plan

If issues arise:
1. Services can fall back to direct path construction
2. BaseService has `_data_root` override for testing
3. Original service code preserved in git history
