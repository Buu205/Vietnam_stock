"""
Base Aggregator for Sector Analysis
===================================

Shared utilities and base class for FA and TA aggregators.

Author: Claude Code
Date: 2025-12-15
Version: 1.0.0
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import pandas as pd
from datetime import datetime

logger = logging.getLogger(__name__)


class BaseAggregator:
    """
    Base class for sector aggregators.

    Provides common functionality for loading data, sector mapping,
    and data validation.
    """

    def __init__(self, config_manager, sector_registry, metric_registry=None):
        """
        Initialize base aggregator.

        Args:
            config_manager: ConfigManager instance
            sector_registry: SectorRegistry instance
            metric_registry: MetricRegistry instance (optional)
        """
        self.config = config_manager
        self.sector_reg = sector_registry
        self.metric_reg = metric_registry

        # Set paths
        self.project_root = Path(__file__).resolve().parents[3]
        self.data_root = self.project_root / "DATA"
        self.processed_path = self.data_root / "processed"
        self.sector_output_path = self.processed_path / "sector"
        self.sector_output_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"BaseAggregator initialized. Output path: {self.sector_output_path}")

    def _add_sector_mapping(self, df: pd.DataFrame, ticker_col: str = 'symbol') -> pd.DataFrame:
        """
        Add sector_code column to DataFrame by mapping ticker to sector.

        Args:
            df: DataFrame with ticker column
            ticker_col: Name of ticker column (default: 'symbol')

        Returns:
            DataFrame with added 'sector_code' and 'sector_name' columns
        """
        if ticker_col not in df.columns:
            logger.warning(f"Ticker column '{ticker_col}' not found in DataFrame")
            return df

        # Map tickers to sectors
        sector_mapping = []
        for ticker in df[ticker_col].unique():
            ticker_info = self.sector_reg.get_ticker(ticker)
            if ticker_info:
                sector_mapping.append({
                    ticker_col: ticker,
                    'sector_code': ticker_info.get('sector'),
                    'sector_name': ticker_info.get('sector'),  # Vietnamese name
                    'industry': ticker_info.get('industry'),
                    'entity_type': ticker_info.get('entity_type')
                })

        if not sector_mapping:
            logger.warning("No sector mappings found")
            return df

        sector_df = pd.DataFrame(sector_mapping)
        result = df.merge(sector_df, on=ticker_col, how='left')

        # Log unmapped tickers
        unmapped = result[result['sector_code'].isna()][ticker_col].unique()
        if len(unmapped) > 0:
            logger.warning(f"Unmapped tickers: {unmapped[:10]}... ({len(unmapped)} total)")

        return result

    def _load_parquet(self, file_path: Path) -> Optional[pd.DataFrame]:
        """
        Load parquet file with error handling.

        Args:
            file_path: Path to parquet file

        Returns:
            DataFrame or None if file not found/error
        """
        try:
            if not file_path.exists():
                logger.warning(f"File not found: {file_path}")
                return None

            df = pd.read_parquet(file_path)
            logger.info(f"Loaded {len(df)} rows from {file_path.name}")
            return df

        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            return None

    def _filter_by_date(
        self,
        df: pd.DataFrame,
        date_col: str = 'report_date',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Filter DataFrame by date range.

        Args:
            df: DataFrame with date column
            date_col: Name of date column
            start_date: Start date (YYYY-MM-DD) or None
            end_date: End date (YYYY-MM-DD) or None

        Returns:
            Filtered DataFrame
        """
        if df is None or df.empty:
            return df

        if date_col not in df.columns:
            logger.warning(f"Date column '{date_col}' not found")
            return df

        # Convert to datetime if needed
        if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
            df[date_col] = pd.to_datetime(df[date_col])

        # Apply filters
        if start_date:
            df = df[df[date_col] >= pd.to_datetime(start_date)]
        if end_date:
            df = df[df[date_col] <= pd.to_datetime(end_date)]

        logger.info(f"Filtered to {len(df)} rows by date range")
        return df

    def _safe_sum(self, series_list: List[pd.Series]) -> pd.Series:
        """
        Safely sum multiple pandas Series, handling None/empty.

        Args:
            series_list: List of pandas Series

        Returns:
            Summed Series
        """
        valid_series = [s for s in series_list if s is not None and not s.empty]
        if not valid_series:
            return pd.Series(0)

        return sum(valid_series)

    def _save_output(
        self,
        df: pd.DataFrame,
        filename: str,
        index: bool = False
    ) -> Path:
        """
        Save DataFrame to parquet file.

        Args:
            df: DataFrame to save
            filename: Output filename
            index: Whether to save index

        Returns:
            Path to saved file
        """
        output_path = self.sector_output_path / filename
        df.to_parquet(output_path, index=index)

        logger.info(f"Saved {len(df)} rows to {output_path}")
        return output_path
