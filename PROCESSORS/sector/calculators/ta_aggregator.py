"""
TA Aggregator - Technical Analysis & Valuation Sector Aggregation
==================================================================

Tổng hợp dữ liệu định giá và kỹ thuật theo ngành.
Aggregate valuation and technical metrics by sector.

This module loads market data (OHLCV), valuation data (PE/PB/PS), and calculates
sector-level valuation multiples using market-cap weighted averages.

Key Features:
- Load OHLCV data for price and market cap
- Load existing PE/PB/EV_EBITDA historical data
- Calculate sector-level PE/PB/PS using market-cap weighted formulas
- Calculate cross-sectional distribution statistics
- Calculate historical percentiles (5-year rolling window)
- Calculate momentum and breadth metrics

Output: DATA/processed/sector/sector_valuation_metrics.parquet

Author: Claude Code
Date: 2025-12-15
Version: 1.0.0
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from PROCESSORS.sector.calculators.base_aggregator import BaseAggregator

# Import VNIndexValuationCalculator for PE/PB calculation
from PROCESSORS.valuation.calculators.vnindex_valuation_calculator import VNIndexValuationCalculator

logger = logging.getLogger(__name__)


class TAAggregator(BaseAggregator):
    """
    Technical Analysis & Valuation Aggregator.

    Tổng hợp dữ liệu định giá và kỹ thuật theo ngành, sử dụng
    trung bình gia quyền theo vốn hóa.

    Aggregates valuation and technical data by sector using
    market-cap weighted averages.

    UPDATED (2025-12-15): Now uses VNIndexValuationCalculator for PE/PB calculation
    instead of loading from historical files. This ensures consistency with market-wide
    valuation metrics.
    """

    def __init__(self, config_manager, sector_registry):
        """
        Initialize TA Aggregator.

        Args:
            config_manager: ConfigManager instance (for TA weights/preferences)
            sector_registry: SectorRegistry instance (for ticker-sector mapping)
        """
        super().__init__(config_manager, sector_registry, metric_registry=None)

        # Initialize VNIndex Valuation Calculator for PE/PB calculation
        self.vnindex_calc = VNIndexValuationCalculator()

        # Set input paths (legacy paths kept for backward compatibility)
        self.valuation_path = self.processed_path / "valuation"
        self.pe_path = self.valuation_path / "pe" / "historical" / "historical_pe.parquet"
        self.pb_path = self.valuation_path / "pb" / "historical" / "historical_pb.parquet"
        self.ev_ebitda_path = self.valuation_path / "ev_ebitda" / "historical" / "historical_ev_ebitda.parquet"
        self.ohlcv_path = self.data_root / "raw" / "ohlcv" / "OHLCV_mktcap.parquet"

        # Check if technical data exists (for momentum/breadth metrics)
        self.technical_path = self.processed_path / "technical"

        # Path to FA sector data (for P/S calculation)
        self.fa_sector_path = self.sector_output_path / "sector_fundamental_metrics.parquet"

        logger.info("TAAggregator initialized")
        logger.info(f"  Using VNIndexValuationCalculator for PE/PB calculation")
        logger.info(f"  OHLCV data: {self.ohlcv_path}")
        logger.info(f"  FA sector data: {self.fa_sector_path}")

    def aggregate_sector_valuation_v2(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        NEW VERSION (v2) - Use VNIndexValuationCalculator for PE/PB calculation.

        This method uses the unified vnindex calculator to calculate sector PE/PB
        instead of loading from historical files. This ensures consistency with
        market-wide valuation metrics.

        Args:
            start_date: Start date for range (YYYY-MM-DD)
            end_date: End date for range (YYYY-MM-DD)

        Returns:
            DataFrame with sector valuation metrics including:
            - sector_code, date
            - sector_pe, sector_pb (from vnindex calculator)
            - sector_market_cap, avg_price, volume
            - ticker_count
            - calculation_date

        Schema matches output from aggregate_sector_valuation() for compatibility.
        """
        logger.info("=" * 80)
        logger.info("STARTING TA SECTOR AGGREGATION (V2 - Using VNIndex Calculator)")
        logger.info("=" * 80)

        # Step 1: Load data into vnindex calculator
        logger.info("\n[1/3] Loading data into VNIndex Calculator...")
        self.vnindex_calc.load_data()

        # Step 2: Calculate PE/PB for all sectors using vnindex calculator
        logger.info("\n[2/3] Calculating sector PE/PB...")

        # Convert dates to datetime if provided
        start_dt = pd.to_datetime(start_date) if start_date else None
        end_dt = pd.to_datetime(end_date) if end_date else None

        # Use vnindex calculator to get sector PE/PB
        valuation_df = self.vnindex_calc.process_all_scopes_with_sectors(
            include_sectors=True,
            start_date=start_dt,
            end_date=end_dt
        )

        # Filter for sector scopes only
        sector_val_df = valuation_df[valuation_df['scope_type'] == 'SECTOR'].copy()

        # Extract sector code from scope (remove 'SECTOR:' prefix)
        sector_val_df['sector_code'] = sector_val_df['scope'].str.replace('SECTOR:', '', regex=False)

        # Rename columns to match expected schema
        rename_map = {
            'pe_ttm': 'sector_pe',
            'pb': 'sector_pb',
            'total_mc_pe': 'sector_market_cap',  # Use market cap from PE calculation
            'total_earnings': 'total_earnings_ttm',
            'total_equity': 'total_equity'
        }
        sector_val_df = sector_val_df.rename(columns=rename_map)

        # Step 3: Add additional metrics (ticker count, avg_price, volume)
        logger.info("\n[3/3] Adding supplementary metrics...")
        sector_val_df = self._add_supplementary_metrics(sector_val_df, start_date, end_date)

        # Add metadata
        sector_val_df['calculation_date'] = pd.Timestamp.now()

        # Add placeholder percentile columns (will be calculated with historical data)
        sector_val_df['pe_percentile_5y'] = np.nan
        sector_val_df['pb_percentile_5y'] = np.nan

        # Select final columns
        final_cols = [
            'sector_code', 'date', 'sector_pe', 'sector_pb', 'sector_market_cap',
            'ticker_count', 'avg_price', 'total_volume',  # Changed from 'volume' to 'total_volume'
            'total_earnings_ttm', 'total_equity',
            'pe_fwd_2025', 'pe_fwd_2026',  # Include forward PE if available
            'pe_percentile_5y', 'pb_percentile_5y',  # Percentile columns (placeholder for now)
            'calculation_date'
        ]

        # Keep only columns that exist
        available_cols = [col for col in final_cols if col in sector_val_df.columns]
        sector_val_df = sector_val_df[available_cols]

        logger.info("=" * 80)
        logger.info(f"✅ TA AGGREGATION V2 COMPLETE: {len(sector_val_df)} records generated")
        logger.info(f"   Sectors: {sector_val_df['sector_code'].nunique()}")
        logger.info(f"   Date range: {sector_val_df['date'].min()} to {sector_val_df['date'].max()}")
        logger.info("=" * 80)

        return sector_val_df

    def _add_supplementary_metrics(
        self,
        sector_val_df: pd.DataFrame,
        start_date: Optional[str],
        end_date: Optional[str]
    ) -> pd.DataFrame:
        """
        Add supplementary metrics (ticker_count, avg_price, volume) from OHLCV data.

        Args:
            sector_val_df: DataFrame with sector PE/PB data
            start_date: Start date filter
            end_date: End date filter

        Returns:
            DataFrame with added metrics
        """
        # Load OHLCV data
        ohlcv_df = self._load_ohlcv_data()
        if ohlcv_df is None:
            logger.warning("OHLCV data not available for supplementary metrics")
            sector_val_df['ticker_count'] = 0
            sector_val_df['avg_price'] = 0
            sector_val_df['volume'] = 0
            return sector_val_df

        # Filter by date
        if start_date or end_date:
            ohlcv_df = self._filter_by_date(ohlcv_df, date_col='date', start_date=start_date, end_date=end_date)

        # Add sector mapping
        ohlcv_df = self._add_sector_mapping(ohlcv_df)
        ohlcv_df = ohlcv_df[ohlcv_df['sector_code'].notna()].copy()

        # Aggregate by sector and date
        agg_metrics = ohlcv_df.groupby(['sector_code', 'date']).agg(
            ticker_count=('symbol', 'nunique'),
            avg_price=('close', 'mean'),
            total_volume=('volume', 'sum')  # Renamed to total_volume to match scorer expectation
        ).reset_index()

        # Merge with sector valuation data
        sector_val_df = sector_val_df.merge(
            agg_metrics,
            on=['sector_code', 'date'],
            how='left'
        )

        # Fill missing values
        sector_val_df['ticker_count'] = sector_val_df['ticker_count'].fillna(0).astype(int)
        sector_val_df['avg_price'] = sector_val_df['avg_price'].fillna(0)
        sector_val_df['total_volume'] = sector_val_df['total_volume'].fillna(0)

        return sector_val_df

    def aggregate_sector_valuation(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Main aggregation function - Hàm tổng hợp chính.

        Aggregate valuation metrics by sector from market data.

        Args:
            start_date: Start date for range (YYYY-MM-DD)
            end_date: End date for range (YYYY-MM-DD)

        Returns:
            DataFrame with sector valuation metrics

        Schema:
            - sector_code: str
            - date: date
            - sector_market_cap: float (VND)
            - avg_price: float (VND)
            - total_volume: int
            - sector_pe: float (market-cap weighted)
            - sector_pb: float (market-cap weighted)
            - sector_ps: float (market-cap weighted)
            - sector_ev_ebitda: float (market-cap weighted)
            - pe_median: float (cross-sectional)
            - pe_mean: float
            - pe_std: float
            - pe_q25: float
            - pe_q75: float
            - pe_min: float
            - pe_max: float
            - [Similar stats for PB]
            - pe_percentile_5y: float (historical rank)
            - pb_percentile_5y: float
            - ps_percentile_5y: float
            - ticker_count: int
            - calculation_date: timestamp
        """
        logger.info("=" * 80)
        logger.info("STARTING TA SECTOR AGGREGATION")
        logger.info("=" * 80)

        # Step 1: Load market data
        logger.info("\n[1/7] Loading market data...")
        ohlcv_df = self._load_ohlcv_data()
        pe_df = self._load_pe_data()
        pb_df = self._load_pb_data()
        ev_ebitda_df = self._load_ev_ebitda_data()

        # Load FA sector data for P/S calculation
        fa_sector_df = self._load_fa_sector_data()

        if ohlcv_df is None:
            logger.error("OHLCV data is required but not found!")
            return pd.DataFrame()

        # Step 2: Filter by date if specified
        if start_date or end_date:
            logger.info(f"\n[2/7] Filtering date range: {start_date} to {end_date}")
            ohlcv_df = self._filter_by_date(ohlcv_df, date_col='date', start_date=start_date, end_date=end_date)
            if pe_df is not None:
                pe_df = self._filter_by_date(pe_df, date_col='date', start_date=start_date, end_date=end_date)
            if pb_df is not None:
                pb_df = self._filter_by_date(pb_df, date_col='date', start_date=start_date, end_date=end_date)
            if ev_ebitda_df is not None:
                ev_ebitda_df = self._filter_by_date(ev_ebitda_df, date_col='date', start_date=start_date, end_date=end_date)
        else:
            logger.info("\n[2/7] No date filter applied - using all available data")

        # Step 3: Merge all data sources
        logger.info("\n[3/7] Merging data sources...")
        merged_df = self._merge_market_data(ohlcv_df, pe_df, pb_df, ev_ebitda_df)

        # Step 4: Add sector mapping
        logger.info("\n[4/7] Mapping tickers to sectors...")
        merged_df = self._add_sector_mapping(merged_df)

        # Remove unmapped tickers
        merged_df = merged_df[merged_df['sector_code'].notna()].copy()
        logger.info(f"  → {len(merged_df)} rows after sector mapping")

        # Step 5: Aggregate by sector and date
        logger.info("\n[5/7] Aggregating by sector and date...")
        results = self._aggregate_all_sectors_by_date(merged_df, fa_sector_df)

        if not results:
            logger.warning("No aggregation results generated!")
            return pd.DataFrame()

        # Convert to DataFrame
        sector_val_df = pd.DataFrame(results)

        # Step 6: Calculate historical percentiles
        logger.info("\n[6/7] Calculating historical percentiles...")
        sector_val_df = self._calculate_historical_percentiles(sector_val_df)

        # Add metadata
        sector_val_df['calculation_date'] = pd.Timestamp.now()

        logger.info("=" * 80)
        logger.info(f"✅ TA AGGREGATION COMPLETE: {len(sector_val_df)} records generated")
        logger.info(f"   Sectors: {sector_val_df['sector_code'].nunique()}")
        logger.info(f"   Date range: {sector_val_df['date'].min()} to {sector_val_df['date'].max()}")
        logger.info("=" * 80)

        return sector_val_df

    def _load_ohlcv_data(self) -> Optional[pd.DataFrame]:
        """
        Load OHLCV data with market cap.

        Returns:
            DataFrame with columns: symbol, date, close, volume, market_cap
        """
        df = self._load_parquet(self.ohlcv_path)
        if df is not None:
            # Convert date to datetime
            df['date'] = pd.to_datetime(df['date'])

            # Select relevant columns
            required_cols = ['symbol', 'date', 'close', 'volume', 'market_cap']
            available_cols = [col for col in required_cols if col in df.columns]
            df = df[available_cols].copy()

            logger.info(f"  ✅ OHLCV: {len(df)} rows, {df['symbol'].nunique()} tickers")
            logger.info(f"     Date range: {df['date'].min()} to {df['date'].max()}")
        return df

    def _load_pe_data(self) -> Optional[pd.DataFrame]:
        """
        Load historical PE data.

        Returns:
            DataFrame with columns: symbol, date, pe_ratio, ttm_earning_billion_vnd, eps
        """
        df = self._load_parquet(self.pe_path)
        if df is not None:
            # Convert date to datetime
            df['date'] = pd.to_datetime(df['date'])

            # Rename columns for consistency
            if 'pe_ratio' in df.columns:
                df = df.rename(columns={'pe_ratio': 'pe'})

            logger.info(f"  ✅ PE: {len(df)} rows, {df['symbol'].nunique()} tickers")
        return df

    def _load_pb_data(self) -> Optional[pd.DataFrame]:
        """
        Load historical PB data.

        Returns:
            DataFrame with columns: symbol, date, pb_ratio, book_value
        """
        df = self._load_parquet(self.pb_path)
        if df is not None:
            # Convert date to datetime
            df['date'] = pd.to_datetime(df['date'])

            # Rename columns for consistency
            if 'pb_ratio' in df.columns:
                df = df.rename(columns={'pb_ratio': 'pb'})

            # Calculate book_value from equity_billion_vnd
            if 'equity_billion_vnd' in df.columns and 'book_value' not in df.columns:
                df['book_value'] = df['equity_billion_vnd'] * 1e9  # Convert to VND

            logger.info(f"  ✅ PB: {len(df)} rows, {df['symbol'].nunique()} tickers")
        return df

    def _load_ev_ebitda_data(self) -> Optional[pd.DataFrame]:
        """
        Load historical EV/EBITDA data.

        Returns:
            DataFrame with columns: symbol, date, ev_ebitda
        """
        df = self._load_parquet(self.ev_ebitda_path)
        if df is not None:
            # Convert date to datetime
            df['date'] = pd.to_datetime(df['date'])
            logger.info(f"  ✅ EV/EBITDA: {len(df)} rows, {df['symbol'].nunique()} tickers")
        return df

    def _load_fa_sector_data(self) -> Optional[pd.DataFrame]:
        """
        Load FA sector fundamental data for P/S calculation.

        Returns:
            DataFrame with columns: sector_code, report_date, total_revenue
        """
        if not self.fa_sector_path.exists():
            logger.warning(f"  ⚠️ FA sector data not found: {self.fa_sector_path}")
            logger.warning("  → P/S calculation will be skipped")
            return None

        df = self._load_parquet(self.fa_sector_path)
        if df is not None:
            # Convert report_date to datetime
            df['report_date'] = pd.to_datetime(df['report_date'])

            # Filter for valid revenue data
            if 'total_revenue' in df.columns:
                df = df[df['total_revenue'].notna() & (df['total_revenue'] > 0)].copy()
                logger.info(f"  ✅ FA Sector: {len(df)} records, {df['sector_code'].nunique()} sectors")
                logger.info(f"     Date range: {df['report_date'].min()} to {df['report_date'].max()}")
            else:
                logger.warning("  ⚠️ FA sector data missing 'total_revenue' column")
                return None

        return df

    def _merge_market_data(
        self,
        ohlcv_df: pd.DataFrame,
        pe_df: Optional[pd.DataFrame],
        pb_df: Optional[pd.DataFrame],
        ev_ebitda_df: Optional[pd.DataFrame]
    ) -> pd.DataFrame:
        """
        Merge all market data sources.

        Args:
            ohlcv_df: OHLCV data (required)
            pe_df: PE data (optional)
            pb_df: PB data (optional)
            ev_ebitda_df: EV/EBITDA data (optional)

        Returns:
            Merged DataFrame
        """
        # Start with OHLCV as base
        merged = ohlcv_df.copy()

        # Merge PE data
        if pe_df is not None:
            pe_cols = ['symbol', 'date', 'pe', 'ttm_earning_billion_vnd', 'eps']
            pe_available = [col for col in pe_cols if col in pe_df.columns]
            merged = merged.merge(
                pe_df[pe_available],
                on=['symbol', 'date'],
                how='left'
            )
            logger.info(f"  → After PE merge: {len(merged)} rows")

        # Merge PB data
        if pb_df is not None:
            pb_cols = ['symbol', 'date', 'pb', 'book_value']
            pb_available = [col for col in pb_cols if col in pb_df.columns]
            merged = merged.merge(
                pb_df[pb_available],
                on=['symbol', 'date'],
                how='left'
            )
            logger.info(f"  → After PB merge: {len(merged)} rows")

        # Merge EV/EBITDA data
        if ev_ebitda_df is not None:
            ev_cols = ['symbol', 'date', 'ev_ebitda']
            ev_available = [col for col in ev_cols if col in ev_ebitda_df.columns]
            merged = merged.merge(
                ev_ebitda_df[ev_available],
                on=['symbol', 'date'],
                how='left'
            )
            logger.info(f"  → After EV/EBITDA merge: {len(merged)} rows")

        return merged

    def _aggregate_all_sectors_by_date(
        self,
        merged_df: pd.DataFrame,
        fa_sector_df: Optional[pd.DataFrame] = None
    ) -> List[Dict[str, Any]]:
        """
        Aggregate all sectors across all dates.

        Args:
            merged_df: Merged market data with sector mapping
            fa_sector_df: FA sector data for P/S calculation (optional)

        Returns:
            List of sector aggregation dictionaries
        """
        results = []

        # Get all unique dates and sectors
        all_dates = sorted(merged_df['date'].unique())
        all_sectors = sorted(merged_df['sector_code'].unique())

        logger.info(f"  Processing {len(all_sectors)} sectors × {len(all_dates)} dates")

        # Aggregate each sector for each date
        for date in all_dates:
            date_df = merged_df[merged_df['date'] == date]

            for sector in all_sectors:
                sector_data = self._calculate_sector_valuation_at_date(
                    sector=sector,
                    date=date,
                    df=date_df,
                    fa_sector_df=fa_sector_df
                )

                if sector_data is not None:
                    results.append(sector_data)

        logger.info(f"  ✅ Generated {len(results)} sector-date records")
        return results

    def _calculate_sector_valuation_at_date(
        self,
        sector: str,
        date,
        df: pd.DataFrame,
        fa_sector_df: Optional[pd.DataFrame] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Calculate sector valuation metrics for one date.

        This is the core calculation function that implements market-cap weighted
        sector PE/PB/PS formulas.

        Formula:
            Sector PE = Σ(Market Cap) / Σ(TTM Earnings)
            Sector PB = Σ(Market Cap) / Σ(Book Value)
            Sector PS = Σ(Market Cap) / Σ(TTM Revenue)

        Args:
            sector: Sector code
            date: Date to aggregate
            df: DataFrame filtered to this date
            fa_sector_df: FA sector data for P/S calculation (optional)

        Returns:
            Dictionary with aggregated sector metrics or None if no data
        """
        # Filter for this sector
        sector_df = df[df['sector_code'] == sector].copy()

        if len(sector_df) == 0:
            return None

        # Filter valid data (positive market cap, non-negative multiples)
        valid_df = sector_df[
            (sector_df['market_cap'] > 0) &
            (sector_df['market_cap'].notna())
        ].copy()

        if len(valid_df) == 0:
            return None

        # Calculate total market cap
        total_market_cap = valid_df['market_cap'].sum()

        # Calculate sector PE (market-cap weighted)
        sector_pe = np.nan
        if 'ttm_earning_billion_vnd' in valid_df.columns:
            # Filter for positive earnings
            pe_valid = valid_df[
                (valid_df['ttm_earning_billion_vnd'] > 0) &
                (valid_df['ttm_earning_billion_vnd'].notna())
            ]
            if len(pe_valid) > 0:
                total_earnings = pe_valid['ttm_earning_billion_vnd'].sum()
                if total_earnings > 0:
                    # Market cap is in VND, earnings in billions VND
                    sector_pe = total_market_cap / (total_earnings * 1e9)

        # Calculate sector PB (market-cap weighted)
        sector_pb = np.nan
        if 'book_value' in valid_df.columns:
            # Filter for positive book value
            pb_valid = valid_df[
                (valid_df['book_value'] > 0) &
                (valid_df['book_value'].notna())
            ]
            if len(pb_valid) > 0:
                total_book_value = pb_valid['book_value'].sum()
                if total_book_value > 0:
                    sector_pb = total_market_cap / total_book_value

        # Calculate sector PS (P/S = Total Market Cap / Total Revenue)
        sector_ps = np.nan
        if fa_sector_df is not None:
            # Find most recent FA revenue data for this sector (report_date <= date)
            fa_sector = fa_sector_df[fa_sector_df['sector_code'] == sector].copy()

            if not fa_sector.empty:
                # Filter for reports up to current date
                valid_fa = fa_sector[fa_sector['report_date'] <= pd.to_datetime(date)]

                if not valid_fa.empty:
                    # Get most recent report
                    latest_fa = valid_fa.sort_values('report_date', ascending=False).iloc[0]
                    revenue = latest_fa['total_revenue']

                    if revenue > 0:
                        # P/S = Market Cap / Revenue (both in VND)
                        sector_ps = total_market_cap / revenue

        # Calculate sector EV/EBITDA (if available)
        sector_ev_ebitda = np.nan
        if 'ev_ebitda' in valid_df.columns:
            # Use market-cap weighted average for EV/EBITDA
            ev_valid = valid_df[
                (valid_df['ev_ebitda'] > 0) &
                (valid_df['ev_ebitda'].notna()) &
                (valid_df['market_cap'] > 0)
            ]
            if len(ev_valid) > 0:
                weights = ev_valid['market_cap'] / ev_valid['market_cap'].sum()
                sector_ev_ebitda = (ev_valid['ev_ebitda'] * weights).sum()

        # Calculate cross-sectional distribution statistics
        pe_stats = self._calculate_distribution_stats(valid_df, 'pe')
        pb_stats = self._calculate_distribution_stats(valid_df, 'pb')

        # Calculate average price and total volume
        avg_price = valid_df['close'].mean() if 'close' in valid_df.columns else None
        total_volume = valid_df['volume'].sum() if 'volume' in valid_df.columns else 0
        
        # Calculate total trading value (Close * Volume)
        total_trading_value = 0.0
        if 'close' in valid_df.columns and 'volume' in valid_df.columns:
            total_trading_value = (valid_df['close'] * valid_df['volume']).sum()

        # Build result dictionary
        result = {
            "sector_code": sector,
            "date": pd.to_datetime(date),
            "sector_market_cap": total_market_cap,
            "avg_price": avg_price,
            "total_volume": int(total_volume),
            "total_trading_value": total_trading_value,
            "sector_pe": sector_pe,
            "sector_pb": sector_pb,
            "sector_ps": sector_ps,
            "sector_ev_ebitda": sector_ev_ebitda,
            "ticker_count": len(valid_df)
        }

        # Add PE distribution stats
        result.update(pe_stats)

        # Add PB distribution stats
        result.update(pb_stats)

        return result

    def _calculate_distribution_stats(
        self,
        df: pd.DataFrame,
        metric: str
    ) -> Dict[str, float]:
        """
        Calculate cross-sectional distribution statistics for a metric.

        Args:
            df: DataFrame with metric column
            metric: Metric name (e.g., 'pe', 'pb')

        Returns:
            Dictionary with median, mean, std, q25, q75, min, max
        """
        if metric not in df.columns:
            return {
                f"{metric}_median": np.nan,
                f"{metric}_mean": np.nan,
                f"{metric}_std": np.nan,
                f"{metric}_q25": np.nan,
                f"{metric}_q75": np.nan,
                f"{metric}_min": np.nan,
                f"{metric}_max": np.nan
            }

        # Filter valid data (positive, non-null)
        valid = df[
            (df[metric] > 0) &
            (df[metric].notna())
        ][metric]

        if len(valid) == 0:
            return {
                f"{metric}_median": np.nan,
                f"{metric}_mean": np.nan,
                f"{metric}_std": np.nan,
                f"{metric}_q25": np.nan,
                f"{metric}_q75": np.nan,
                f"{metric}_min": np.nan,
                f"{metric}_max": np.nan
            }

        return {
            f"{metric}_median": valid.median(),
            f"{metric}_mean": valid.mean(),
            f"{metric}_std": valid.std(),
            f"{metric}_q25": valid.quantile(0.25),
            f"{metric}_q75": valid.quantile(0.75),
            f"{metric}_min": valid.min(),
            f"{metric}_max": valid.max()
        }

    def _calculate_historical_percentiles(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Calculate where current value sits in 5-year history.

        For each sector + date, look back 5 years and calculate percentile rank
        of current PE/PB/PS.

        Logic:
        - Rolling 5-year window (~1260 trading days)
        - Percentile rank = (number of values < current) / total values * 100

        Args:
            df: DataFrame with sector valuation metrics

        Returns:
            DataFrame with added percentile columns:
            - pe_percentile_5y
            - pb_percentile_5y
            - ps_percentile_5y
        """
        # Ensure sorted by sector and date
        df = df.sort_values(['sector_code', 'date']).copy()

        # Calculate percentiles for each metric
        for metric in ['pe', 'pb', 'ps']:
            sector_col = f'sector_{metric}'
            percentile_col = f'{metric}_percentile_5y'

            if sector_col not in df.columns:
                df[percentile_col] = np.nan
                continue

            # Calculate percentile for each sector
            df[percentile_col] = (
                df.groupby('sector_code')[sector_col]
                .transform(lambda x: self._calculate_rolling_percentile(x, window=1260))
            )

        return df

    def _calculate_rolling_percentile(
        self,
        series: pd.Series,
        window: int = 1260
    ) -> pd.Series:
        """
        Calculate rolling percentile rank for each value.

        Args:
            series: Time series of values
            window: Rolling window size (default: 1260 days ≈ 5 years)

        Returns:
            Series with percentile ranks (0-100)
        """
        def percentile_rank(x):
            if len(x) < 2 or pd.isna(x.iloc[-1]):
                return np.nan

            current = x.iloc[-1]
            # Percentile = % of values less than current
            return (x < current).sum() / len(x) * 100

        return series.rolling(window=window, min_periods=20).apply(percentile_rank, raw=False)

    def run(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Path:
        """
        Convenience method to run aggregation and save output.

        Args:
            start_date: Optional start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD)

        Returns:
            Path to saved output file
        """
        logger.info("Running TA aggregation...")

        # Run aggregation
        sector_val_df = self.aggregate_sector_valuation(
            start_date=start_date,
            end_date=end_date
        )

        # Save output
        output_path = self._save_output(
            sector_val_df,
            filename="sector_valuation_metrics.parquet",
            index=False
        )

        logger.info(f"✅ TA aggregation complete: {output_path}")
        return output_path


# Main execution for testing
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Import registries
    from config.registries import SectorRegistry

    # Mock ConfigManager (will be replaced with real one later)
    class MockConfigManager:
        def __init__(self):
            self.ta_weights = {}

    # Initialize
    sector_reg = SectorRegistry()
    config = MockConfigManager()

    # Create aggregator
    agg = TAAggregator(config, sector_reg)

    # Run aggregation (last 1 year for faster testing)
    from datetime import datetime, timedelta
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')

    output_path = agg.run(start_date=start_date, end_date=end_date)

    print(f"\n{'=' * 80}")
    print(f"✅ SUCCESS: TA aggregation complete")
    print(f"   Output: {output_path}")
    print(f"{'=' * 80}")
