"""
BSC Forecast Processor - Excel to Parquet Pipeline
===================================================

Processes BSC Research Forecast Excel file into structured parquet files
with calculated metrics for Streamlit dashboard.

Output files:
- bsc_individual.parquet: Individual stock forecasts (92 stocks)
- bsc_sector_valuation.parquet: Sector PE/PB FWD aggregates (19 sectors)
- bsc_combined.parquet: Merged individual + sector metrics

Updated: 2025-12-17
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BSCForecastProcessor:
    """
    Processor for BSC Research Forecast data.

    Converts Excel forecast data to parquet with calculated metrics:
    - PE/PB Forward 2025-2026
    - YoY Growth rates
    - YTD Achievement percentages
    - Rating recommendations
    - Sector aggregates
    """

    # BSC sector to Vietnamese sector mapping
    BSC_TO_VN_SECTOR = {
        'Bank': 'Ngân hàng',
        'Broker': 'Dịch vụ tài chính',
        'Const': 'Xây dựng và Vật liệu',
        'IP': 'Hàng & Dịch vụ Công nghiệp',
        'Material': 'Tài nguyên Cơ bản',
        'RE': 'Bất động sản',
        'Auto': 'Ô tô và phụ tùng',
        'Chemicals': 'Hóa chất',
        'Fertilizer': 'Hóa chất',  # Fertilizer maps to Chemicals
        'O&G': 'Dầu khí',
        'Utilities': 'Điện, nước & xăng dầu khí đốt',
        'Aviation': 'Hàng & Dịch vụ Công nghiệp',
        'Fishery': 'Thực phẩm và đồ uống',
        'Tyre': 'Ô tô và phụ tùng',
        'Logistics': 'Hàng & Dịch vụ Công nghiệp',
        'Retail': 'Bán lẻ',
        'Tech': 'Công nghệ Thông tin',
        'Textile': 'Hàng cá nhân & Gia dụng',
    }

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize BSCForecastProcessor.

        Args:
            project_root: Project root directory (defaults to auto-detect)
        """
        if project_root is None:
            project_root = Path(__file__).resolve().parents[2]

        self.project_root = project_root
        self.excel_path = project_root / "DATA" / "processed" / "forecast" / "BSC Forecast.xlsx"
        self.output_dir = project_root / "DATA" / "processed" / "forecast" / "bsc"

        # Data source paths
        self.ohlcv_path = project_root / "DATA" / "raw" / "ohlcv" / "OHLCV_mktcap.parquet"
        self.ticker_details_path = project_root / "config" / "metadata" / "ticker_details.json"
        self.fundamental_dir = project_root / "DATA" / "processed" / "fundamental"

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Load ticker details
        self._ticker_details = None

    @property
    def ticker_details(self) -> Dict:
        """Lazy load ticker details."""
        if self._ticker_details is None:
            with open(self.ticker_details_path, 'r') as f:
                self._ticker_details = json.load(f)
        return self._ticker_details

    def load_excel_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Load BSC Forecast Excel data.

        Returns:
            Tuple of (individual_df, sector_df)
        """
        logger.info(f"Loading Excel from: {self.excel_path}")

        # Read raw Excel
        df_raw = pd.read_excel(self.excel_path, sheet_name='Sheet1', header=None)

        # Parse individual stocks (columns 1-12, rows 2 onwards)
        individual_cols = {
            1: 'symbol',
            2: 'target_price',
            3: 'rev_2025f',
            4: 'rev_2026f',
            5: 'npatmi_2025f',
            6: 'npatmi_2026f',
            7: 'eps_2025f',
            8: 'eps_2026f',
            9: 'roa_2025f',
            10: 'roa_2026f',
            11: 'roe_2025f',
            12: 'roe_2026f',
        }

        individual_df = df_raw.iloc[2:, list(individual_cols.keys())].copy()
        individual_df.columns = list(individual_cols.values())
        individual_df = individual_df.dropna(subset=['symbol'])
        individual_df = individual_df.reset_index(drop=True)

        # Convert numeric columns
        numeric_cols = ['target_price', 'rev_2025f', 'rev_2026f', 'npatmi_2025f', 'npatmi_2026f',
                       'eps_2025f', 'eps_2026f', 'roa_2025f', 'roa_2026f', 'roe_2025f', 'roe_2026f']
        for col in numeric_cols:
            individual_df[col] = pd.to_numeric(individual_df[col], errors='coerce')

        logger.info(f"Loaded {len(individual_df)} individual stocks from Excel")

        # Parse sector aggregates (columns 14-19, rows 2-21)
        sector_cols = {
            14: 'bsc_sector',
            15: 'rev_2025f',
            16: 'rev_2026f',
            17: 'npatmi_2025f',
            18: 'npatmi_2026f',
            19: 'yoy_growth',
        }

        sector_df = df_raw.iloc[2:22, list(sector_cols.keys())].copy()
        sector_df.columns = list(sector_cols.values())
        sector_df = sector_df.dropna(subset=['bsc_sector'])
        sector_df = sector_df[sector_df['bsc_sector'] != 'Total']  # Remove total row
        sector_df = sector_df.reset_index(drop=True)

        # Convert numeric columns
        sector_numeric = ['rev_2025f', 'rev_2026f', 'npatmi_2025f', 'npatmi_2026f', 'yoy_growth']
        for col in sector_numeric:
            sector_df[col] = pd.to_numeric(sector_df[col], errors='coerce')

        logger.info(f"Loaded {len(sector_df)} BSC sectors from Excel")

        return individual_df, sector_df

    def load_market_data(self) -> pd.DataFrame:
        """
        Load latest market cap and price from OHLCV.

        Returns:
            DataFrame with symbol, current_price, market_cap
        """
        logger.info(f"Loading OHLCV from: {self.ohlcv_path}")

        ohlcv = pd.read_parquet(self.ohlcv_path)
        ohlcv['date'] = pd.to_datetime(ohlcv['date'])

        # Get latest data per symbol
        latest_date = ohlcv['date'].max()
        latest = ohlcv[ohlcv['date'] == latest_date][['symbol', 'close', 'market_cap']].copy()
        latest = latest.rename(columns={'close': 'current_price'})

        # Convert market_cap to billions VND
        latest['market_cap'] = latest['market_cap'] / 1e9

        logger.info(f"Loaded market data for {len(latest)} symbols (date: {latest_date.date()})")

        return latest

    def load_fundamental_data(self) -> pd.DataFrame:
        """
        Load TTM fundamental data (total_equity, total_assets, npatmi_ttm).

        Returns:
            DataFrame with symbol, total_equity, total_assets, npatmi_ttm
        """
        logger.info("Loading fundamental data...")

        all_data = []
        entity_files = {
            'company': 'company_financial_metrics.parquet',
            'bank': 'bank_financial_metrics.parquet',
            'insurance': 'insurance_financial_metrics.parquet',
            'security': 'security_financial_metrics.parquet',
        }

        for entity, filename in entity_files.items():
            file_path = self.fundamental_dir / entity / filename
            if file_path.exists():
                df = pd.read_parquet(file_path)

                # Get latest quarter data per symbol
                if 'year_period' in df.columns:
                    df = df.sort_values('year_period', ascending=False)
                    df = df.groupby('symbol').first().reset_index()
                elif 'year' in df.columns and 'quarter' in df.columns:
                    df = df.sort_values(['year', 'quarter'], ascending=[False, False])
                    df = df.groupby('symbol').first().reset_index()

                # Select relevant columns
                cols_to_keep = ['symbol']
                if 'total_equity' in df.columns:
                    cols_to_keep.append('total_equity')
                if 'total_assets' in df.columns:
                    cols_to_keep.append('total_assets')
                if 'npatmi_ttm' in df.columns:
                    cols_to_keep.append('npatmi_ttm')
                elif 'npatmi' in df.columns:
                    df['npatmi_ttm'] = df['npatmi']
                    cols_to_keep.append('npatmi_ttm')

                all_data.append(df[cols_to_keep])
                logger.info(f"  - Loaded {len(df)} {entity} records")

        if not all_data:
            return pd.DataFrame(columns=['symbol', 'total_equity', 'total_assets', 'npatmi_ttm'])

        combined = pd.concat(all_data, ignore_index=True)

        # Remove duplicates - keep first (latest quarter)
        combined = combined.drop_duplicates(subset=['symbol'], keep='first')

        # Convert to billions VND if needed
        for col in ['total_equity', 'total_assets', 'npatmi_ttm']:
            if col in combined.columns:
                # Check if already in billions (values typically < 1000 for large companies)
                median_val = combined[col].median()
                if median_val > 10000:  # Likely in millions or raw VND
                    combined[col] = combined[col] / 1e9

        logger.info(f"Combined fundamental data: {len(combined)} unique symbols")

        return combined

    def _detect_latest_year_quarters(self) -> tuple:
        """
        Detect the latest year and available quarters from fundamental data.

        Returns:
            Tuple of (year, list of quarters, quarter_count)
            e.g., (2025, [1, 2, 3], 3) for 9M data
        """
        # Check company data as reference (largest dataset)
        file_path = self.fundamental_dir / "company" / "company_financial_metrics.parquet"

        if not file_path.exists():
            return (2025, [1, 2, 3], 3)  # Default fallback

        df = pd.read_parquet(file_path, columns=['year', 'quarter', 'freq_code'])

        # Only quarterly data
        if 'freq_code' in df.columns:
            df = df[df['freq_code'] == 'Q']

        # Get latest year with data
        latest_year = int(df['year'].max())

        # Get available quarters for latest year
        year_data = df[df['year'] == latest_year]
        available_quarters = sorted(year_data['quarter'].unique().tolist())

        quarter_count = len(available_quarters)

        return (latest_year, available_quarters, quarter_count)

    def load_ytd_data(self) -> pd.DataFrame:
        """
        Load YTD revenue and profit data from quarterly results.

        Dynamically detects the latest year and available quarters.
        For example, if Q1, Q2, Q3 data exists, it calculates 9M achievement.

        Returns:
            DataFrame with symbol, rev_ytd_{year}, npatmi_ytd_{year}, ytd_quarters
        """
        # Detect latest year and quarters
        year, quarters, quarter_count = self._detect_latest_year_quarters()
        months = quarter_count * 3  # 3 months per quarter

        logger.info(f"Loading YTD data: Year={year}, Quarters={quarters} ({months}M)")

        all_data = []
        entity_files = {
            'company': ('company_financial_metrics.parquet', 'net_revenue'),
            'bank': ('bank_financial_metrics.parquet', 'total_operating_income'),
            'insurance': ('insurance_financial_metrics.parquet', 'total_revenue'),
            'security': ('security_financial_metrics.parquet', 'total_revenue'),
        }

        for entity, (filename, rev_col) in entity_files.items():
            file_path = self.fundamental_dir / entity / filename
            if file_path.exists():
                df = pd.read_parquet(file_path)

                # Filter quarterly data for detected year
                if 'year' in df.columns and 'quarter' in df.columns:
                    if 'freq_code' in df.columns:
                        df = df[df['freq_code'] == 'Q']

                    # Filter to detected year and available quarters
                    df_year = df[(df['year'] == year) & (df['quarter'].isin(quarters))].copy()

                    if not df_year.empty:
                        entity_quarters = sorted(df_year['quarter'].unique())
                        logger.info(f"  - {entity}: Found Q{entity_quarters} ({len(df_year)} records)")

                        # Determine revenue column
                        actual_rev_col = rev_col if rev_col in df_year.columns else 'net_revenue'
                        if actual_rev_col not in df_year.columns:
                            rev_candidates = [c for c in df_year.columns if 'revenue' in c.lower() or 'income' in c.lower()]
                            actual_rev_col = rev_candidates[0] if rev_candidates else None

                        # Sum revenue and profit by symbol
                        agg_dict = {}
                        if actual_rev_col and actual_rev_col in df_year.columns:
                            agg_dict[actual_rev_col] = 'sum'
                        if 'npatmi' in df_year.columns:
                            agg_dict['npatmi'] = 'sum'

                        # Also track which quarters each symbol has
                        agg_dict['quarter'] = lambda x: list(sorted(x.unique()))

                        if agg_dict:
                            ytd = df_year.groupby('symbol').agg(agg_dict).reset_index()

                            # Rename columns
                            rename_map = {'quarter': 'ytd_quarters'}
                            if actual_rev_col and actual_rev_col in ytd.columns:
                                rename_map[actual_rev_col] = 'rev_ytd_2025'
                            if 'npatmi' in ytd.columns:
                                rename_map['npatmi'] = 'npatmi_ytd_2025'

                            ytd = ytd.rename(columns=rename_map)
                            all_data.append(ytd)

        if not all_data:
            logger.warning("No YTD data found!")
            return pd.DataFrame(columns=['symbol', 'rev_ytd_2025', 'npatmi_ytd_2025', 'ytd_quarters'])

        combined = pd.concat(all_data, ignore_index=True)

        # Ensure columns exist
        for col in ['rev_ytd_2025', 'npatmi_ytd_2025', 'ytd_quarters']:
            if col not in combined.columns:
                combined[col] = np.nan if col != 'ytd_quarters' else None

        # Convert to billions VND if needed
        for col in ['rev_ytd_2025', 'npatmi_ytd_2025']:
            if col in combined.columns and combined[col].notna().any():
                median_val = combined[col].median()
                if pd.notna(median_val) and median_val > 1e10:
                    combined[col] = combined[col] / 1e9
                    logger.info(f"  - Converted {col} to billions")

        # Store metadata about YTD period
        self._ytd_year = year
        self._ytd_quarters = quarters
        self._ytd_months = months

        logger.info(f"Loaded YTD {months}M data for {len(combined)} symbols (Year {year}, Q{quarters})")

        return combined

    def load_historical_data(self) -> pd.DataFrame:
        """
        Load previous year actual revenue and profit for YoY growth calculation.

        Dynamically detects the year based on YTD data year - 1.

        Returns:
            DataFrame with symbol, rev_2024_actual, npatmi_2024_actual
        """
        # Get previous year (YTD year - 1)
        ytd_year = getattr(self, '_ytd_year', 2025)
        prev_year = ytd_year - 1

        logger.info(f"Loading {prev_year} historical data (for YoY growth)...")

        all_data = []
        entity_files = {
            'company': ('company_financial_metrics.parquet', 'net_revenue'),
            'bank': ('bank_financial_metrics.parquet', 'total_operating_income'),
            'insurance': ('insurance_financial_metrics.parquet', 'total_revenue'),
            'security': ('security_financial_metrics.parquet', 'total_revenue'),
        }

        for entity, (filename, rev_col) in entity_files.items():
            file_path = self.fundamental_dir / entity / filename
            if file_path.exists():
                df = pd.read_parquet(file_path)

                # Filter previous year quarterly data
                if 'year' in df.columns and 'quarter' in df.columns:
                    if 'freq_code' in df.columns:
                        df = df[df['freq_code'] == 'Q']

                    df_prev = df[df['year'] == prev_year].copy()

                    if not df_prev.empty:
                        # Determine revenue column
                        actual_rev_col = rev_col if rev_col in df_prev.columns else 'net_revenue'
                        if actual_rev_col not in df_prev.columns:
                            rev_candidates = [c for c in df_prev.columns if 'revenue' in c.lower() or 'income' in c.lower()]
                            actual_rev_col = rev_candidates[0] if rev_candidates else None

                        # Sum full year
                        agg_dict = {}
                        if actual_rev_col and actual_rev_col in df_prev.columns:
                            agg_dict[actual_rev_col] = 'sum'
                        if 'npatmi' in df_prev.columns:
                            agg_dict['npatmi'] = 'sum'

                        if agg_dict:
                            yearly = df_prev.groupby('symbol').agg(agg_dict).reset_index()

                            rename_map = {}
                            if actual_rev_col and actual_rev_col in yearly.columns:
                                rename_map[actual_rev_col] = 'rev_2024_actual'
                            if 'npatmi' in yearly.columns:
                                rename_map['npatmi'] = 'npatmi_2024_actual'

                            yearly = yearly.rename(columns=rename_map)
                            all_data.append(yearly)
                            logger.info(f"  - {entity}: Loaded {len(yearly)} symbols")

        if not all_data:
            return pd.DataFrame(columns=['symbol', 'rev_2024_actual', 'npatmi_2024_actual'])

        combined = pd.concat(all_data, ignore_index=True)

        # Ensure columns exist
        for col in ['rev_2024_actual', 'npatmi_2024_actual']:
            if col not in combined.columns:
                combined[col] = np.nan

        # Convert to billions VND if needed
        for col in ['rev_2024_actual', 'npatmi_2024_actual']:
            if col in combined.columns and combined[col].notna().any():
                median_val = combined[col].median()
                if pd.notna(median_val) and median_val > 1e10:
                    combined[col] = combined[col] / 1e9

        logger.info(f"Loaded {prev_year} data for {len(combined)} symbols")

        return combined

    @staticmethod
    def calculate_rating(upside_pct: float) -> str:
        """
        Calculate rating based on upside percentage.

        Rating Logic:
        - STRONG BUY:  upside > 25%
        - BUY:         upside > 10% & <= 25%
        - HOLD:        upside >= -10% & <= 10%
        - SELL:        upside > -20% & < -10%
        - STRONG SELL: upside <= -20%
        """
        if pd.isna(upside_pct):
            return "N/A"

        if upside_pct > 0.25:
            return "STRONG BUY"
        elif upside_pct > 0.10:
            return "BUY"
        elif upside_pct >= -0.10:
            return "HOLD"
        elif upside_pct > -0.20:
            return "SELL"
        else:
            return "STRONG SELL"

    def calculate_individual_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate individual stock metrics.

        Metrics calculated:
        - upside_pct, rating
        - pe_fwd_2025, pe_fwd_2026
        - pb_fwd_2025, pb_fwd_2026
        - rev_growth_yoy_2025, rev_growth_yoy_2026
        - npatmi_growth_yoy_2025, npatmi_growth_yoy_2026
        - rev_achievement_pct, npatmi_achievement_pct
        """
        logger.info("Calculating individual metrics...")

        # Get list of BSC symbols from Excel
        bsc_symbols = df['symbol'].unique().tolist()
        logger.info(f"Processing {len(bsc_symbols)} BSC symbols")

        # Load additional data
        market_data = self.load_market_data()
        fundamental_data = self.load_fundamental_data()
        ytd_data = self.load_ytd_data()
        historical_data = self.load_historical_data()

        # Filter to only BSC symbols
        market_data = market_data[market_data['symbol'].isin(bsc_symbols)]
        fundamental_data = fundamental_data[fundamental_data['symbol'].isin(bsc_symbols)]
        ytd_data = ytd_data[ytd_data['symbol'].isin(bsc_symbols)]
        historical_data = historical_data[historical_data['symbol'].isin(bsc_symbols)]

        # Merge market data
        df = df.merge(market_data, on='symbol', how='left')

        # Merge fundamental data
        df = df.merge(fundamental_data, on='symbol', how='left')

        # Merge YTD data
        df = df.merge(ytd_data, on='symbol', how='left')

        # Merge historical data
        df = df.merge(historical_data, on='symbol', how='left')

        # Calculate upside and rating
        df['upside_pct'] = (df['target_price'] / df['current_price']) - 1
        df['rating'] = df['upside_pct'].apply(self.calculate_rating)

        # Calculate PE Forward
        df['pe_fwd_2025'] = df['market_cap'] / df['npatmi_2025f']
        df['pe_fwd_2026'] = df['market_cap'] / df['npatmi_2026f']

        # Calculate PB Forward (equity grows by retained earnings)
        df['equity_2025f'] = df['total_equity'] + df['npatmi_2025f']
        df['equity_2026f'] = df['equity_2025f'] + df['npatmi_2026f']
        df['pb_fwd_2025'] = df['market_cap'] / df['equity_2025f']
        df['pb_fwd_2026'] = df['market_cap'] / df['equity_2026f']

        # Calculate YoY Growth
        df['rev_growth_yoy_2025'] = (df['rev_2025f'] / df['rev_2024_actual']) - 1
        df['rev_growth_yoy_2026'] = (df['rev_2026f'] / df['rev_2025f']) - 1
        df['npatmi_growth_yoy_2025'] = (df['npatmi_2025f'] / df['npatmi_2024_actual']) - 1
        df['npatmi_growth_yoy_2026'] = (df['npatmi_2026f'] / df['npatmi_2025f']) - 1

        # Calculate YTD Achievement
        df['rev_achievement_pct'] = df['rev_ytd_2025'] / df['rev_2025f']
        df['npatmi_achievement_pct'] = df['npatmi_ytd_2025'] / df['npatmi_2025f']

        # Add sector info from ticker_details
        df['vn_sector'] = df['symbol'].apply(
            lambda x: self.ticker_details.get(x, {}).get('sector', 'Unknown')
        )
        df['entity_type'] = df['symbol'].apply(
            lambda x: self.ticker_details.get(x, {}).get('entity', 'COMPANY')
        )

        # Add BSC sector mapping (based on ticker to BSC sector lookup)
        # For now, use vn_sector reverse mapping
        vn_to_bsc = {v: k for k, v in self.BSC_TO_VN_SECTOR.items()}
        df['bsc_sector'] = df['vn_sector'].apply(lambda x: vn_to_bsc.get(x, 'Other'))

        # Add timestamp
        df['updated_at'] = datetime.now()

        # Select and order columns
        output_cols = [
            'symbol', 'target_price', 'current_price', 'upside_pct', 'rating',
            'rev_2025f', 'rev_2026f', 'npatmi_2025f', 'npatmi_2026f',
            'eps_2025f', 'eps_2026f', 'roe_2025f', 'roe_2026f', 'roa_2025f', 'roa_2026f',
            'rev_growth_yoy_2025', 'rev_growth_yoy_2026',
            'npatmi_growth_yoy_2025', 'npatmi_growth_yoy_2026',
            'rev_ytd_2025', 'npatmi_ytd_2025',
            'rev_achievement_pct', 'npatmi_achievement_pct',
            'market_cap', 'total_equity',
            'pe_fwd_2025', 'pe_fwd_2026', 'pb_fwd_2025', 'pb_fwd_2026',
            'bsc_sector', 'vn_sector', 'entity_type', 'updated_at'
        ]

        # Ensure all columns exist
        for col in output_cols:
            if col not in df.columns:
                df[col] = np.nan

        df = df[output_cols]

        logger.info(f"Calculated metrics for {len(df)} stocks")

        return df

    def calculate_sector_aggregates(self, individual_df: pd.DataFrame, excel_sector_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate BSC sector aggregates with PE/PB FWD.

        Uses Excel sector data as base and calculates PE/PB FWD.
        """
        logger.info("Calculating sector aggregates...")

        # Group individual stocks by BSC sector
        sector_agg = individual_df.groupby('bsc_sector').agg({
            'symbol': 'count',
            'market_cap': 'sum',
            'npatmi_2025f': 'sum',
            'npatmi_2026f': 'sum',
            'total_equity': 'sum',
            'upside_pct': 'mean',
            'roe_2025f': 'mean',
            'roe_2026f': 'mean',
        }).reset_index()

        sector_agg = sector_agg.rename(columns={
            'symbol': 'symbol_count',
            'market_cap': 'total_market_cap',
            'npatmi_2025f': 'total_npatmi_2025f',
            'npatmi_2026f': 'total_npatmi_2026f',
            'total_equity': 'total_equity_ttm',
            'upside_pct': 'avg_upside_pct',
            'roe_2025f': 'avg_roe_2025f',
            'roe_2026f': 'avg_roe_2026f',
        })

        # Calculate forward equity
        sector_agg['total_equity_2025f'] = sector_agg['total_equity_ttm'] + sector_agg['total_npatmi_2025f']
        sector_agg['total_equity_2026f'] = sector_agg['total_equity_2025f'] + sector_agg['total_npatmi_2026f']

        # Calculate PE/PB Forward
        sector_agg['pe_fwd_2025'] = sector_agg['total_market_cap'] / sector_agg['total_npatmi_2025f']
        sector_agg['pe_fwd_2026'] = sector_agg['total_market_cap'] / sector_agg['total_npatmi_2026f']
        sector_agg['pb_fwd_2025'] = sector_agg['total_market_cap'] / sector_agg['total_equity_2025f']
        sector_agg['pb_fwd_2026'] = sector_agg['total_market_cap'] / sector_agg['total_equity_2026f']

        # Add VN sector mapping
        sector_agg['vn_sector'] = sector_agg['bsc_sector'].apply(
            lambda x: self.BSC_TO_VN_SECTOR.get(x, x)
        )

        # Add timestamp
        sector_agg['updated_at'] = datetime.now()

        # Select and order columns
        output_cols = [
            'bsc_sector', 'vn_sector', 'symbol_count',
            'total_market_cap', 'total_npatmi_2025f', 'total_npatmi_2026f',
            'total_equity_2025f', 'total_equity_2026f',
            'pe_fwd_2025', 'pe_fwd_2026', 'pb_fwd_2025', 'pb_fwd_2026',
            'avg_upside_pct', 'avg_roe_2025f', 'avg_roe_2026f', 'updated_at'
        ]

        for col in output_cols:
            if col not in sector_agg.columns:
                sector_agg[col] = np.nan

        sector_agg = sector_agg[output_cols]

        logger.info(f"Calculated aggregates for {len(sector_agg)} sectors")

        return sector_agg

    def create_combined_data(self, individual_df: pd.DataFrame, sector_df: pd.DataFrame) -> pd.DataFrame:
        """
        Merge individual data with sector metrics.

        Adds sector-level PE/PB FWD to each stock for comparison.
        """
        logger.info("Creating combined data...")

        # Select sector columns to merge
        sector_cols = sector_df[['bsc_sector', 'pe_fwd_2025', 'pe_fwd_2026', 'pb_fwd_2025', 'pb_fwd_2026']].copy()
        sector_cols = sector_cols.rename(columns={
            'pe_fwd_2025': 'sector_pe_fwd_2025',
            'pe_fwd_2026': 'sector_pe_fwd_2026',
            'pb_fwd_2025': 'sector_pb_fwd_2025',
            'pb_fwd_2026': 'sector_pb_fwd_2026',
        })

        # Merge
        combined = individual_df.merge(sector_cols, on='bsc_sector', how='left')

        # Calculate premium/discount vs sector
        combined['pe_premium_2025'] = (combined['pe_fwd_2025'] / combined['sector_pe_fwd_2025']) - 1
        combined['pe_premium_2026'] = (combined['pe_fwd_2026'] / combined['sector_pe_fwd_2026']) - 1

        logger.info(f"Created combined data for {len(combined)} stocks")

        return combined

    def export_parquet(self, individual_df: pd.DataFrame, sector_df: pd.DataFrame, combined_df: pd.DataFrame):
        """Export all dataframes to parquet files."""

        individual_path = self.output_dir / "bsc_individual.parquet"
        sector_path = self.output_dir / "bsc_sector_valuation.parquet"
        combined_path = self.output_dir / "bsc_combined.parquet"

        individual_df.to_parquet(individual_path, index=False)
        sector_df.to_parquet(sector_path, index=False)
        combined_df.to_parquet(combined_path, index=False)

        logger.info(f"Exported parquet files:")
        logger.info(f"  - {individual_path} ({len(individual_df)} rows)")
        logger.info(f"  - {sector_path} ({len(sector_df)} rows)")
        logger.info(f"  - {combined_path} ({len(combined_df)} rows)")

    def generate_readme(self, individual_df: pd.DataFrame, sector_df: pd.DataFrame):
        """Generate README.md with schema documentation."""

        readme_content = f"""# BSC Forecast Data Structure

## Overview
Dữ liệu dự báo BSC Research đã xử lý, bao gồm PE/PB forward và các metrics tính toán.

**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Source:** BSC Research Forecast Excel
**Symbols:** {len(individual_df)} mã | **Sectors:** {len(sector_df)} ngành

---

## Files

### 1. bsc_individual.parquet ({len(individual_df)} rows)
Individual stock forecast với calculated metrics.

| Column | Type | Description |
|--------|------|-------------|
| symbol | str | Mã cổ phiếu |
| target_price | float | Giá mục tiêu BSC (VND) |
| current_price | float | Giá hiện tại (VND) |
| upside_pct | float | % tăng giá kỳ vọng |
| rating | str | Khuyến nghị (STRONG BUY/BUY/HOLD/SELL/STRONG SELL) |
| rev_2025f | float | Doanh thu forecast 2025 (tỷ VND) |
| rev_2026f | float | Doanh thu forecast 2026 (tỷ VND) |
| npatmi_2025f | float | LNST forecast 2025 (tỷ VND) |
| npatmi_2026f | float | LNST forecast 2026 (tỷ VND) |
| eps_2025f | float | EPS forecast 2025 (VND) |
| eps_2026f | float | EPS forecast 2026 (VND) |
| roe_2025f | float | ROE forecast 2025 (%) |
| roe_2026f | float | ROE forecast 2026 (%) |
| roa_2025f | float | ROA forecast 2025 (%) |
| roa_2026f | float | ROA forecast 2026 (%) |
| rev_growth_yoy_2025 | float | Tăng trưởng DT 2024→2025 (%) |
| rev_growth_yoy_2026 | float | Tăng trưởng DT 2025→2026 (%) |
| npatmi_growth_yoy_2025 | float | Tăng trưởng LN 2024→2025 (%) |
| npatmi_growth_yoy_2026 | float | Tăng trưởng LN 2025→2026 (%) |
| rev_ytd_2025 | float | Doanh thu YTD 2025 (tỷ VND) |
| npatmi_ytd_2025 | float | LNST YTD 2025 (tỷ VND) |
| rev_achievement_pct | float | % hoàn thành DT forecast |
| npatmi_achievement_pct | float | % hoàn thành LN forecast |
| market_cap | float | Vốn hóa hiện tại (tỷ VND) |
| total_equity | float | Vốn chủ sở hữu TTM (tỷ VND) |
| pe_fwd_2025 | float | PE forward 2025 |
| pe_fwd_2026 | float | PE forward 2026 |
| pb_fwd_2025 | float | PB forward 2025 |
| pb_fwd_2026 | float | PB forward 2026 |
| bsc_sector | str | Ngành theo BSC |
| vn_sector | str | Ngành chuẩn hóa (ticker_details.json) |
| entity_type | str | Loại DN: BANK/COMPANY/SECURITY/INSURANCE |
| updated_at | datetime | Thời gian cập nhật |

### 2. bsc_sector_valuation.parquet ({len(sector_df)} rows)
Sector aggregation với PE/PB forward 2025-2026.

| Column | Type | Description |
|--------|------|-------------|
| bsc_sector | str | Ngành theo BSC (Bank, Broker, etc.) |
| vn_sector | str | Ngành chuẩn hóa |
| symbol_count | int | Số mã trong ngành |
| total_market_cap | float | Tổng vốn hóa (tỷ VND) |
| total_npatmi_2025f | float | Tổng LNST forecast 2025 (tỷ VND) |
| total_npatmi_2026f | float | Tổng LNST forecast 2026 (tỷ VND) |
| total_equity_2025f | float | Tổng VCSH forecast 2025 (tỷ VND) |
| total_equity_2026f | float | Tổng VCSH forecast 2026 (tỷ VND) |
| pe_fwd_2025 | float | Sector PE forward 2025 |
| pe_fwd_2026 | float | Sector PE forward 2026 |
| pb_fwd_2025 | float | Sector PB forward 2025 |
| pb_fwd_2026 | float | Sector PB forward 2026 |
| avg_upside_pct | float | Upside trung bình ngành (%) |
| avg_roe_2025f | float | ROE trung bình 2025 (%) |
| avg_roe_2026f | float | ROE trung bình 2026 (%) |
| updated_at | datetime | Thời gian cập nhật |

### 3. bsc_combined.parquet ({len(individual_df)} rows)
Individual + sector metrics merged.

Bao gồm tất cả columns từ bsc_individual.parquet + thêm:
| Column | Type | Description |
|--------|------|-------------|
| sector_pe_fwd_2025 | float | PE FWD 2025 của ngành |
| sector_pe_fwd_2026 | float | PE FWD 2026 của ngành |
| sector_pb_fwd_2025 | float | PB FWD 2025 của ngành |
| sector_pb_fwd_2026 | float | PB FWD 2026 của ngành |
| pe_premium_2025 | float | PE stock / PE sector - 1 (premium/discount) |
| pe_premium_2026 | float | PE stock / PE sector - 1 |

---

## Formulas

### PE Forward
```
PE FWD 2025 = market_cap / npatmi_2025f
PE FWD 2026 = market_cap / npatmi_2026f
```

### PB Forward
```
equity_2025f = total_equity_ttm + npatmi_2025f
equity_2026f = equity_2025f + npatmi_2026f

PB FWD 2025 = market_cap / equity_2025f
PB FWD 2026 = market_cap / equity_2026f
```

### Upside & Rating
```
upside_pct = (target_price / current_price) - 1

Rating Logic:
- STRONG BUY:  upside > 25%
- BUY:         upside > 10% & <= 25%
- HOLD:        upside >= -10% & <= 10%
- SELL:        upside > -20% & < -10%
- STRONG SELL: upside <= -20%
```

### YTD Achievement
```
rev_achievement_pct = rev_ytd_2025 / rev_2025f
npatmi_achievement_pct = npatmi_ytd_2025 / npatmi_2025f
```

### Growth YoY
```
rev_growth_yoy_2025 = (rev_2025f / rev_2024_actual) - 1
npatmi_growth_yoy_2025 = (npatmi_2025f / npatmi_2024_actual) - 1
```

---

## Data Refresh

### Daily Auto-Update (via daily pipeline)
Cập nhật market_cap, current_price, PE/PB FWD từ OHLCV data.

```bash
python3 PROCESSORS/pipelines/run_all_daily_updates.py
```

### Manual Excel Re-read
Khi BSC cập nhật forecast mới trong Excel:

```bash
python3 PROCESSORS/forecast/update_bsc_excel.py
```

---

## Usage Example

```python
import pandas as pd

# Load individual stocks
df = pd.read_parquet("DATA/processed/forecast/bsc/bsc_individual.parquet")

# Filter by rating
strong_buys = df[df['rating'] == 'STRONG BUY']

# Load sector valuation
sectors = pd.read_parquet("DATA/processed/forecast/bsc/bsc_sector_valuation.parquet")

# Compare PE FWD by sector
print(sectors[['bsc_sector', 'pe_fwd_2025', 'pe_fwd_2026']].sort_values('pe_fwd_2025'))
```

---

## BSC Sector Mapping

| BSC Sector | VN Sector |
|------------|-----------|
| Bank | Ngân hàng |
| Broker | Dịch vụ tài chính |
| Const | Xây dựng và Vật liệu |
| IP | Hàng & Dịch vụ Công nghiệp |
| Material | Tài nguyên Cơ bản |
| RE | Bất động sản |
| Auto | Ô tô và phụ tùng |
| Chemicals | Hóa chất |
| Fertilizer | Hóa chất |
| O&G | Dầu khí |
| Utilities | Điện, nước & xăng dầu khí đốt |
| Aviation | Hàng & Dịch vụ Công nghiệp |
| Fishery | Thực phẩm và đồ uống |
| Tyre | Ô tô và phụ tùng |
| Logistics | Hàng & Dịch vụ Công nghiệp |
| Retail | Bán lẻ |
| Tech | Công nghệ Thông tin |
| Textile | Hàng cá nhân & Gia dụng |
"""

        readme_path = self.output_dir / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)

        logger.info(f"Generated README.md at {readme_path}")

    def run(self, generate_readme: bool = True) -> Dict[str, pd.DataFrame]:
        """
        Run the full BSC Forecast processing pipeline.

        Args:
            generate_readme: Whether to generate README.md documentation

        Returns:
            Dict with 'individual', 'sector', 'combined' DataFrames
        """
        logger.info("=" * 60)
        logger.info("BSC Forecast Processor - Starting Pipeline")
        logger.info("=" * 60)

        # Step 1: Load Excel data
        individual_df, sector_df_excel = self.load_excel_data()

        # Step 2: Calculate individual metrics
        individual_df = self.calculate_individual_metrics(individual_df)

        # Step 3: Calculate sector aggregates
        sector_df = self.calculate_sector_aggregates(individual_df, sector_df_excel)

        # Step 4: Create combined data
        combined_df = self.create_combined_data(individual_df, sector_df)

        # Step 5: Export parquet files
        self.export_parquet(individual_df, sector_df, combined_df)

        # Step 6: Generate README
        if generate_readme:
            self.generate_readme(individual_df, sector_df)

        logger.info("=" * 60)
        logger.info("BSC Forecast Processor - Pipeline Complete")
        logger.info("=" * 60)

        return {
            'individual': individual_df,
            'sector': sector_df,
            'combined': combined_df
        }


def main():
    """Run BSC Forecast Processor as standalone script."""
    processor = BSCForecastProcessor()
    result = processor.run(generate_readme=True)

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    individual = result['individual']
    sector = result['sector']

    print(f"\nIndividual Stocks: {len(individual)}")
    print(f"Rating Distribution:")
    print(individual['rating'].value_counts().to_string())

    print(f"\nSectors: {len(sector)}")
    print("\nSector PE/PB FWD 2025:")
    print(sector[['bsc_sector', 'pe_fwd_2025', 'pb_fwd_2025']].to_string())


if __name__ == "__main__":
    main()
