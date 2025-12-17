"""
Historical P/S (Price-to-Sales) Calculator
==========================================
Calculates daily P/S ratio time series for all stocks.

P/S Ratio = Market Cap / TTM Revenue
Where:
- Market Cap = Close Price * Shares Outstanding
- TTM Revenue = Rolling 4-quarter sum of Net Revenue (CIS_10 for COMPANY)

Usage:
    python3 PROCESSORS/valuation/calculators/historical_ps_calculator.py
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import logging
import sys
import warnings

# PROJECT_ROOT = stock_dashboard directory (3 levels up)
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Add project root to path
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from typing import Dict, List, Optional

warnings.filterwarnings('ignore')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HistoricalPSCalculator:
    """
    Calculate P/S (Price-to-Sales) ratio daily time series.

    P/S = Market Cap / TTM Revenue

    Revenue metric codes by entity type:
    - COMPANY: CIS_10 (Doanh thu thuần)
    - BANK: BIS_1 (Thu nhập lãi)
    - INSURANCE: IIS_1 (Doanh thu phí bảo hiểm)
    - SECURITY: SIS_1 (Doanh thu)
    """

    # Revenue metric codes by entity type
    REVENUE_CODES = {
        'COMPANY': 'CIS_10',    # Doanh thu thuần về bán hàng và cung cấp dịch vụ
        'BANK': 'BIS_1',        # Thu nhập lãi và các khoản thu nhập tương tự
        'INSURANCE': 'IIS_1',   # Doanh thu hoạt động bảo hiểm
        'SECURITY': 'SIS_1'     # Doanh thu hoạt động môi giới
    }

    def __init__(self):
        self.base_path = PROJECT_ROOT
        self.output_path = self.base_path / 'DATA' / 'processed' / 'valuation' / 'ps' / 'historical'
        self.ohlcv_path = self.base_path / 'DATA' / 'raw' / 'ohlcv' / 'OHLCV_mktcap.parquet'

        self.fundamental_data = None
        self.ohlcv_data = None
        self.raw_revenue_df = None
        self.daily_market_data = None
        self.symbol_entity_types = {}

        # Load metadata
        self.metadata = self._load_metadata()

    def _load_metadata(self) -> pd.DataFrame:
        """Load ticker metadata from ticker_details.json"""
        import json

        metadata_path = self.base_path / 'config' / 'metadata' / 'ticker_details.json'

        if not metadata_path.exists():
            logger.warning(f"Metadata file not found: {metadata_path}")
            return pd.DataFrame(columns=['symbol', 'entity_type'])

        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            df = pd.DataFrame.from_dict(data, orient='index').reset_index()
            df.rename(columns={'index': 'symbol', 'entity': 'entity_type'}, inplace=True)

            df['symbol'] = df['symbol'].str.upper().str.strip()
            if 'entity_type' in df.columns:
                df['entity_type'] = df['entity_type'].str.upper().str.strip()
            else:
                df['entity_type'] = 'COMPANY'

            # Populate symbol_entity_types dict
            for _, row in df.iterrows():
                self.symbol_entity_types[row['symbol']] = row['entity_type']

            return df[['symbol', 'entity_type']]

        except Exception as e:
            logger.error(f"Error loading metadata: {e}")
            return pd.DataFrame(columns=['symbol', 'entity_type'])

    def load_data(self):
        """Load all required data (Fundamental, OHLCV)"""
        logger.info("⏳ Loading data for P/S calculation...")

        # 1. Load Fundamental Data
        fundamental_dfs = []
        entity_types = ['company', 'bank', 'insurance', 'security']

        for entity in entity_types:
            file_path = self.base_path / 'DATA' / 'processed' / 'fundamental' / f'{entity}_full.parquet'
            if file_path.exists():
                logger.info(f"   Loading {entity} data from {file_path.name}")
                try:
                    df = pd.read_parquet(file_path)
                    if 'ENTITY_TYPE' not in df.columns:
                        df['ENTITY_TYPE'] = entity.upper()
                    if 'REPORT_DATE' in df.columns:
                        df['REPORT_DATE'] = pd.to_datetime(df['REPORT_DATE'])
                    fundamental_dfs.append(df)
                except Exception as e:
                    logger.error(f"   Error loading {file_path.name}: {e}")
            else:
                logger.warning(f"   ⚠️ File not found: {file_path}")

        if fundamental_dfs:
            self.fundamental_data = pd.concat(fundamental_dfs, ignore_index=True)
            if 'SECURITY_CODE' in self.fundamental_data.columns:
                self.fundamental_data.rename(columns={'SECURITY_CODE': 'symbol'}, inplace=True)
            logger.info(f"   Combined fundamental data: {len(self.fundamental_data):,} records")
        else:
            raise FileNotFoundError("No fundamental data files found.")

        # 2. Load OHLCV Data
        if self.ohlcv_path.exists():
            logger.info(f"   Loading OHLCV data from {self.ohlcv_path}")
            self.ohlcv_data = pd.read_parquet(self.ohlcv_path)
            if 'date' in self.ohlcv_data.columns:
                self.ohlcv_data['date'] = pd.to_datetime(self.ohlcv_data['date'])
            logger.info(f"   Loaded {len(self.ohlcv_data):,} OHLCV records")
        else:
            raise FileNotFoundError(f"OHLCV data not found at {self.ohlcv_path}")

        # Pre-process data
        self._preprocess_data()

    def _preprocess_data(self):
        """Pre-process and prepare data for optimization"""
        logger.info("⚡ Pre-processing data for P/S calculation...")

        # 1. Get Revenue codes for all entity types
        all_revenue_codes = set(self.REVENUE_CODES.values())

        # Filter for quarterly frequency
        if 'FREQ_CODE' in self.fundamental_data.columns:
            logger.info("   Filtering for 'Q' frequency...")
            self.fundamental_data = self.fundamental_data[self.fundamental_data['FREQ_CODE'] == 'Q']

        # Filter revenue data
        revenue_data = self.fundamental_data[
            self.fundamental_data['METRIC_CODE'].isin(all_revenue_codes)
        ].copy()

        if not revenue_data.empty:
            # Map entity type to expected revenue code
            revenue_data['expected_metric'] = revenue_data['ENTITY_TYPE'].str.upper().map(self.REVENUE_CODES)

            # Filter rows where metric code matches expected
            valid_mask = revenue_data['METRIC_CODE'] == revenue_data['expected_metric']
            revenue_df = revenue_data[valid_mask][['symbol', 'REPORT_DATE', 'METRIC_VALUE']].copy()

            if not revenue_df.empty:
                # Remove duplicates
                revenue_df = revenue_df.groupby(['symbol', 'REPORT_DATE'], as_index=False)['METRIC_VALUE'].first()
                self.raw_revenue_df = revenue_df.sort_values(['symbol', 'REPORT_DATE'])
                logger.info(f"   Prepared revenue data with {len(self.raw_revenue_df):,} records")
            else:
                logger.warning("   No valid revenue data after filtering")
                self.raw_revenue_df = pd.DataFrame()
        else:
            logger.warning("   No revenue data found")
            self.raw_revenue_df = pd.DataFrame()

        # 2. Pre-compute daily market data
        logger.info("   Pre-computing daily market data...")
        self.daily_market_data = self.ohlcv_data.copy()

        # Calculate shares outstanding
        self.daily_market_data['shares_outstanding'] = np.where(
            self.daily_market_data['close'] > 0,
            self.daily_market_data['market_cap'] / self.daily_market_data['close'],
            np.nan
        )

        self.daily_market_data = self.daily_market_data.sort_values(['symbol', 'date'])
        logger.info("✅ Pre-processing completed!")

    def calculate_ps_timeseries(self, symbols: List[str],
                                start_date: datetime,
                                end_date: datetime) -> pd.DataFrame:
        """
        Calculate P/S ratio for multiple symbols.

        Args:
            symbols: List of stock symbols
            start_date: Start date
            end_date: End date

        Returns:
            DataFrame with columns: symbol, date, close_price, market_cap,
                                   ttm_revenue_billion_vnd, ps_ratio, sector
        """
        logger.info(f"🚀 Calculating P/S timeseries for {len(symbols)} symbols...")

        # 1. Filter Market Data
        market_subset = self.daily_market_data[
            (self.daily_market_data['date'] >= start_date) &
            (self.daily_market_data['date'] <= end_date) &
            (self.daily_market_data['symbol'].isin(symbols))
        ].copy()

        if market_subset.empty:
            logger.warning("No market data found.")
            return pd.DataFrame()

        # 2. Prepare TTM Revenue
        if self.raw_revenue_df is None or self.raw_revenue_df.empty:
            logger.warning("No revenue data available")
            return pd.DataFrame()

        revenue_subset = self.raw_revenue_df[self.raw_revenue_df['symbol'].isin(symbols)].copy()
        revenue_subset = revenue_subset.sort_values(['symbol', 'REPORT_DATE'])

        # Calculate Rolling 4Q Sum (TTM Revenue)
        revenue_subset['ttm_revenue'] = revenue_subset.groupby('symbol')['METRIC_VALUE'].transform(
            lambda x: x.rolling(window=4, min_periods=4).sum()
        )

        valid_ttm = revenue_subset.dropna(subset=['ttm_revenue']).copy()
        valid_ttm = valid_ttm.rename(columns={'REPORT_DATE': 'report_date'})
        valid_ttm = valid_ttm.sort_values('report_date')

        if valid_ttm.empty:
            logger.warning("No valid TTM revenue data")
            return pd.DataFrame()

        # 3. Merge Market Data with TTM Revenue
        market_subset = market_subset.sort_values('date')

        merged_data = pd.merge_asof(
            market_subset,
            valid_ttm[['symbol', 'report_date', 'ttm_revenue']],
            left_on='date',
            right_on='report_date',
            by='symbol',
            direction='backward'
        )

        # 4. Compute P/S Ratio
        # P/S = Market Cap / TTM Revenue
        merged_data['ps_ratio'] = np.where(
            (merged_data['ttm_revenue'] > 0) & (merged_data['market_cap'] > 0),
            merged_data['market_cap'] / merged_data['ttm_revenue'],
            np.nan
        )

        # Add metadata
        merged_data['ttm_revenue_billion_vnd'] = merged_data['ttm_revenue'] / 1e9
        merged_data['sector'] = merged_data['symbol'].map(self.symbol_entity_types).fillna('COMPANY')

        # Final formatting
        result_cols = ['symbol', 'date', 'close', 'market_cap',
                       'ttm_revenue_billion_vnd', 'ps_ratio', 'sector']

        result_df = merged_data[result_cols].copy()
        result_df = result_df.rename(columns={'close': 'close_price'})

        logger.info(f"✅ Calculated P/S for {result_df['symbol'].nunique()} symbols")
        return result_df

    def save_results(self, df: pd.DataFrame, filename: str = None):
        """Save results to parquet file"""
        if df.empty:
            logger.warning("No data to save")
            return

        self.output_path.mkdir(parents=True, exist_ok=True)

        if filename is None:
            filename = "historical_ps.parquet"

        output_file = self.output_path / filename
        df.to_parquet(output_file, index=False)
        logger.info(f"💾 Saved {len(df):,} records to {output_file}")

    def run_full_backfill(self, start_year: int = 2018):
        """Run full historical backfill for all symbols"""
        logger.info("=" * 60)
        logger.info("Starting P/S Historical Backfill")
        logger.info("=" * 60)

        # Load data
        self.load_data()

        # Get all unique symbols from OHLCV
        all_symbols = self.ohlcv_data['symbol'].unique().tolist()
        logger.info(f"Total symbols in OHLCV: {len(all_symbols)}")

        # Date range
        start_date = datetime(start_year, 1, 1)
        end_date = datetime.now()

        # Calculate P/S for all symbols
        result_df = self.calculate_ps_timeseries(all_symbols, start_date, end_date)

        if not result_df.empty:
            # Clean up: remove extreme outliers
            logger.info("🧹 Cleaning outliers...")
            initial_count = len(result_df)

            # P/S should be positive and typically < 50 for most stocks
            result_df = result_df[
                (result_df['ps_ratio'] > 0) &
                (result_df['ps_ratio'] < 100)  # More lenient threshold
            ]

            removed = initial_count - len(result_df)
            logger.info(f"   Removed {removed:,} outlier records")

            # Save results
            self.save_results(result_df, "historical_ps.parquet")

            # Summary
            logger.info("=" * 60)
            logger.info("P/S Backfill Complete!")
            logger.info(f"   Total records: {len(result_df):,}")
            logger.info(f"   Unique symbols: {result_df['symbol'].nunique()}")
            logger.info(f"   Date range: {result_df['date'].min()} to {result_df['date'].max()}")
            logger.info(f"   P/S range: {result_df['ps_ratio'].min():.2f} - {result_df['ps_ratio'].max():.2f}")
            logger.info("=" * 60)
        else:
            logger.error("❌ No P/S data calculated!")


def main():
    """Main entry point"""
    calculator = HistoricalPSCalculator()
    calculator.run_full_backfill(start_year=2018)


if __name__ == "__main__":
    main()
