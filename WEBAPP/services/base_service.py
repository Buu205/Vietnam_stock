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

Author: AI Assistant
Date: 2025-12-31
Version: 1.0.0
"""

import pandas as pd
from pathlib import Path
from typing import Optional
from abc import ABC
import logging

logger = logging.getLogger(__name__)


class BaseService(ABC):
    """
    Abstract base service with registry integration.

    Subclasses should define:
        DATA_SOURCE: str - Name of data source in registry
        ENTITY_TYPE: str - Entity type (bank, company, insurance, security)

    Usage:
        class BankService(BaseService):
            DATA_SOURCE = "bank_metrics"
            ENTITY_TYPE = "bank"

            def get_financial_data(self, ticker):
                df = self.load_data()
                return df[df['symbol'] == ticker]
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
        self._project_root: Optional[Path] = None

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

    @property
    def project_root(self) -> Path:
        """Get project root directory."""
        if self._project_root is None:
            current_file = Path(__file__).resolve()
            self._project_root = current_file.parents[2]
        return self._project_root

    @property
    def data_root(self) -> Path:
        """Get data root directory."""
        if self._data_root:
            return self._data_root
        return self.project_root / "DATA"

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

        # Validate empty DataFrame
        if df.empty:
            logger.warning(
                f"{self.__class__.__name__}: Loaded empty DataFrame from {path}"
            )

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

    def get_data_source_info(self) -> dict:
        """Get metadata about this service's data source."""
        if not self.DATA_SOURCE:
            return {}

        source = self.registry.get_data_source(self.DATA_SOURCE)
        if not source:
            return {}

        return {
            "name": source.name,
            "path": source.path,
            "entity_type": source.entity_type,
            "category": source.category,
            "update_freq": source.update_freq,
            "cache_ttl": source.cache_ttl,
        }
