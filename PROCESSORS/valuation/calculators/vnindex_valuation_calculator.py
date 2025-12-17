"""
VNINDEX Valuation Calculator
============================
Calculates market-wide P/E and P/B ratios for VNINDEX (or any custom index).
Methodology: Market-Cap Weighted Aggregation.
Formula:
    Index PE = Sum(Market Cap) / Sum(Earnings TTM)
    Index PB = Sum(Market Cap) / Sum(Total Equity)

Supports dynamic exclusion of specific symbols (e.g., VIC, VHM) to analyze market excluding impacts of large conglomerates.
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import datetime
import logging
import sys
import warnings

# PROJECT_ROOT
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Import DateFormatter
try:
    from PROCESSORS.core.shared.date_formatter import DateFormatter
except ImportError:
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.append(str(PROJECT_ROOT))
    from PROCESSORS.core.shared.date_formatter import DateFormatter

# Import Metric Loader
from PROCESSORS.valuation.formulas.metric_mapper import MetricRegistryLoader

# Import SectorRegistry for sector processing
from config.registries import SectorRegistry

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)

class VNIndexValuationCalculator:
    def __init__(self):
        self.base_path = PROJECT_ROOT

        # Paths
        self.METADATA_PATH = self.base_path / 'config' / 'metadata' / 'ticker_details.json' # Updated to JSON
        self.ohlcv_path = self.base_path / 'DATA' / 'raw' / 'ohlcv' / 'OHLCV_mktcap.parquet'
        self.output_path = self.base_path / 'DATA' / 'processed' / 'valuation' / 'vnindex'

        self.date_formatter = DateFormatter()
        self.mapper = MetricRegistryLoader()

        # Sector Registry
        self.sector_reg = SectorRegistry()

        # Caches
        self.fundamental_data = None
        self.ohlcv_data = None
        self.metadata = None
        self.symbol_entity_types = {}

        # Processed State
        self.financial_data = None
        self.daily_market_data = None

        # Initialize Metadata
        self.metadata = self.load_metadata() 

    def load_metadata(self):
        """
        Load ticker metadata from ticker_details.json
        Returns: DataFrame with ['symbol', 'entity_type']
        """
        if not self.METADATA_PATH.exists():
            raise FileNotFoundError(f"Metadata file not found: {self.METADATA_PATH}")
            
        try:
            with open(self.METADATA_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convert nested dict to DataFrame
            df = pd.DataFrame.from_dict(data, orient='index').reset_index()
            # Rename columns
            df.rename(columns={'index': 'symbol', 'entity': 'entity_type'}, inplace=True)
            
            # Normalize
            df['symbol'] = df['symbol'].str.upper().str.strip()
            
            if 'entity_type' in df.columns:
                df['entity_type'] = df['entity_type'].str.upper().str.strip()
            else:
                logger.warning("Entity type missing in metadata, defaulting to COMPANY")
                df['entity_type'] = 'COMPANY'
                
            return df # Return all columns including sector
            
        except Exception as e:
            logger.error(f"Error loading metadata: {e}")
            return pd.DataFrame(columns=['symbol', 'entity_type'])

    def load_data(self):
        """Load all tickers, full fundamental data (all entities), and OHLCV."""
        logger.info("⏳ Loading data for VNINDEX Valuation...")
        
        # 1. Load Metadata
        # Metadata is already loaded in __init__
        # Map symbol -> entity_type
        for _, row in self.metadata.iterrows():
            self.symbol_entity_types[row['symbol']] = str(row.get('entity_type', 'COMPANY')).upper()
            
        # 2. Load Fundamental Data (All Types)
        dfs = []
        for entity in ['company', 'bank', 'insurance', 'security']:
            f_path = self.base_path / 'DATA' / 'processed' / 'fundamental' / f'{entity}_full.parquet'
            if f_path.exists():
                try:
                    df = pd.read_parquet(f_path)
                    if 'ENTITY_TYPE' not in df.columns:
                        df['ENTITY_TYPE'] = entity.upper()
                    if 'REPORT_DATE' in df.columns:
                        df['REPORT_DATE'] = pd.to_datetime(df['REPORT_DATE'])
                    dfs.append(df)
                    logger.info(f"   Loaded {entity} data.")
                except Exception as e:
                    logger.error(f"   Error loading {entity}: {e}")
        
        if dfs:
            self.fundamental_data = pd.concat(dfs, ignore_index=True)
            if 'SECURITY_CODE' in self.fundamental_data.columns:
                self.fundamental_data.rename(columns={'SECURITY_CODE': 'symbol'}, inplace=True)
        else:
            raise FileNotFoundError("No fundamental data found.")
            
        # 3. Load OHLCV
        if self.ohlcv_path.exists():
            self.ohlcv_data = pd.read_parquet(self.ohlcv_path)
            if 'date' in self.ohlcv_data.columns:
                self.ohlcv_data['date'] = pd.to_datetime(self.ohlcv_data['date'])
            logger.info(f"   Loaded {len(self.ohlcv_data):,} OHLCV records.")
        else:
            raise FileNotFoundError("OHLCV data not found.")
            
        self._preprocess_financials()

    def _preprocess_financials(self):
        """
        Pre-calculate Earnings TTM and Equity for all symbols.
        Result: self.financial_data dataframe with columns [symbol, report_date, earnings_ttm, equity]
        """
        logger.info("⚡ Pre-processing financials (Earnings & Equity)...")
        
        # 0. Filter for Target Frequency ONLY
        target_freq = self.mapper.get_target_frequency()
        if 'FREQ_CODE' in self.fundamental_data.columns:
            logger.info(f"   Filtering for '{target_freq}' frequency...")
            self.fundamental_data = self.fundamental_data[self.fundamental_data['FREQ_CODE'] == target_freq]
        else:
            logger.warning("   ⚠️ FREQ_CODE column missing! Assuming all data is valid (Risky).")
        
        # 1. Map Metrics
        # We need Code Map for (Entity, NetIncome) and (Entity, Equity)
        net_income_map = {}
        equity_map = {}
        
        for entity in ['COMPANY', 'BANK', 'INSURANCE', 'SECURITY']:
            ni_code = self.mapper.get_metric_code('net_income', entity)
            eq_code = self.mapper.get_metric_code('total_equity', entity)
            if ni_code: net_income_map[(entity, ni_code)] = 'net_income'
            if eq_code: equity_map[(entity, eq_code)] = 'equity'
            
        logger.info(f"   Mapped {len(net_income_map)} Net Income codes and {len(equity_map)} Equity codes.")
            
        # 2. Filter & Pivot
        # Create tuple index for mapping
        self.fundamental_data['entity_code_pair'] = list(zip(
            self.fundamental_data['ENTITY_TYPE'], 
            self.fundamental_data['METRIC_CODE']
        ))
        
        # Map using two maps
        def map_metric_type(pair):
            if pair in net_income_map: return 'net_income'
            if pair in equity_map: return 'equity'
            return None
            
        self.fundamental_data['metric_type'] = self.fundamental_data['entity_code_pair'].map(map_metric_type)
        valid_fin = self.fundamental_data.dropna(subset=['metric_type']).copy()
        
        # PIVOT STRATEGY: 
        # Report dates for Income and Equity might differ slightly or be recorded differently.
        # We pivot first. If multiple records for same day, take last.
        pivot_df = valid_fin.pivot_table(
            index=['symbol', 'REPORT_DATE'],
            columns='metric_type',
            values='METRIC_VALUE',
            aggfunc='last' 
        ).reset_index()
        
        if 'net_income' not in pivot_df.columns: pivot_df['net_income'] = 0
        if 'equity' not in pivot_df.columns: pivot_df['equity'] = np.nan # Use NaN to distinguish missing
        
        # Sort for filling
        pivot_df = pivot_df.sort_values(['symbol', 'REPORT_DATE'])
        
        # FORWARD FILL EQUITY
        # Equity is a Balance Sheet item, safe to forward fill for quarterly gaps if report dates slightly misaligned
        pivot_df['equity'] = pivot_df.groupby('symbol')['equity'].ffill()
        
        # 3. Calculate TTM Earnings
        # Net Income is flow, do not fill. Valid 0 is fine.
        pivot_df['net_income'] = pivot_df['net_income'].fillna(0)
        
        pivot_df['earnings_ttm'] = pivot_df.groupby('symbol')['net_income'].transform(
            lambda x: x.rolling(window=4, min_periods=4).sum()
        )
        
        # Filter valid records
        self.financial_data = pivot_df[['symbol', 'REPORT_DATE', 'earnings_ttm', 'equity']].copy()
        self.financial_data.rename(columns={'REPORT_DATE': 'report_date'}, inplace=True)
        self.financial_data = self.financial_data.sort_values('report_date')
        
        logger.info(f"   Processed financials for {self.financial_data['symbol'].nunique()} symbols.")

    def load_bsc_forecast_data(self):
        """
        Load BSC Forecast data from parquet file.
        Returns: DataFrame [symbol, 2025_npat, 2026_npat]
        """
        # Use new parquet file (generated by bsc_forecast_processor.py)
        path = self.base_path / 'DATA' / 'processed' / 'forecast' / 'bsc' / 'bsc_individual.parquet'
        if not path.exists():
            logger.warning(f"⚠️ BSC Forecast file not found at {path}")
            return None

        try:
            df = pd.read_parquet(path)

            # Map columns: npatmi_2025f -> 2025_npat, npatmi_2026f -> 2026_npat
            if 'npatmi_2025f' not in df.columns or 'npatmi_2026f' not in df.columns:
                logger.warning("Forecast file missing required columns (npatmi_2025f, npatmi_2026f)")
                return None

            forecast_df = df[['symbol', 'npatmi_2025f', 'npatmi_2026f']].copy()
            forecast_df.rename(columns={
                'npatmi_2025f': '2025_npat',
                'npatmi_2026f': '2026_npat'
            }, inplace=True)

            # Normalize symbol
            forecast_df['symbol'] = forecast_df['symbol'].str.upper().str.strip()

            # Values are already in billion VND, convert to VND (for consistency with market_cap)
            forecast_df['2025_npat'] = forecast_df['2025_npat'] * 1e9
            forecast_df['2026_npat'] = forecast_df['2026_npat'] * 1e9

            logger.info(f"   Loaded BSC forecast for {len(forecast_df)} symbols")
            return forecast_df

        except Exception as e:
            logger.error(f"Error loading BSC forecast: {e}")
            return None

    def calculate_scope_valuation(self, scope_name: str, 
                                  subset_symbols: list = None, 
                                  excluded_symbols: list = None,
                                  bsc_forecast_df: pd.DataFrame = None,
                                  start_date: datetime = None,
                                  end_date: datetime = None) -> pd.DataFrame:
        """
        Calculate valuation metrics for a specific scope.
        Args:
            scope_name: Label for the scope (VNINDEX, VNINDEX_EXCLUDE, BSC_INDEX)
            subset_symbols: If provided, ONLY use these symbols (Whitelist).
            excluded_symbols: If provided, EXCLUDE these symbols (Blacklist).
            bsc_forecast_df: Optional DF with [symbol, 2025_npat, 2026_npat] for Forward PE.
            start_date: Optional start date for calculation.
            end_date: Optional end date for calculation.
        """
        logger.info(f"🚀 Calculating Metrics for Scope: {scope_name}")
        
        # 1. Filter Symbols in OHLCV
        market_data = self.ohlcv_data.copy()
        
        # Whitelist (e.g. for BSC Index)
        if subset_symbols is not None:
            subset_symbols = [s.upper() for s in subset_symbols]
            market_data = market_data[market_data['symbol'].isin(subset_symbols)]
            
        # Blacklist (e.g. for Excluded)
        if excluded_symbols is not None:
            excluded_symbols = [s.upper() for s in excluded_symbols]
            market_data = market_data[~market_data['symbol'].isin(excluded_symbols)]
            
        if start_date:
            market_data = market_data[market_data['date'] >= start_date]
        if end_date:
            market_data = market_data[market_data['date'] <= end_date]
            
        market_data = market_data.sort_values('date')
        
        if market_data.empty:
            logger.warning(f"⚠️ No market data found for scope {scope_name} in requested period.")
            return pd.DataFrame()
        
        # 2. Merge Financials (TTM & Equity)
        merged_data = pd.merge_asof(
            market_data,
            self.financial_data,
            left_on='date',
            right_on='report_date',
            by='symbol',
            direction='backward'
        )
        
        # 3. Aggregation - Trailing Metrics
        # PE TTM
        pe_valid = merged_data.dropna(subset=['earnings_ttm', 'market_cap'])
        # Filter negative earnings? Usually for Index PE, we sum inputs. 
        # Sum(MC) / Sum(Earnings). If Total Earnings < 0, PE is negative/undefined.
        pe_agg = pe_valid.groupby('date').agg(
            total_mc_pe=('market_cap', 'sum'),
            total_earnings=('earnings_ttm', 'sum')
        )
        pe_agg['pe_ttm'] = pe_agg['total_mc_pe'] / pe_agg['total_earnings']
        
        # PB
        pb_valid = merged_data.dropna(subset=['equity', 'market_cap'])
        pb_agg = pb_valid.groupby('date').agg(
            total_mc_pb=('market_cap', 'sum'),
            total_equity=('equity', 'sum')
        )
        pb_agg['pb'] = pb_agg['total_mc_pb'] / pb_agg['total_equity']
        
        # Combine
        result_df = pd.concat([pe_agg[['pe_ttm']], pb_agg[['pb']]], axis=1).reset_index()
        result_df['scope'] = scope_name
        
        # 4. Forward PE Logic (Only if Forecast Data Provided)
        if bsc_forecast_df is not None:
            # Merge Forecast into Daily Market Data (use filtered market_data)
            # Forecast is STATIC per symbol.
            fwd_merged = market_data.merge(bsc_forecast_df, on='symbol', how='inner')
            
            # Group by Date
            # FWD PE 2025 = Sum(MC) / Sum(NPAT 2025)
            # FWD PE 2026 = Sum(MC) / Sum(NPAT 2026)
            
            # 2025
            fwd25_valid = fwd_merged.dropna(subset=['2025_npat', 'market_cap'])
            fwd25_agg = fwd25_valid.groupby('date').agg(
                mc=('market_cap', 'sum'),
                npat25=('2025_npat', 'sum')
            )
            fwd25_agg['pe_fwd_2025'] = fwd25_agg['mc'] / fwd25_agg['npat25']
            
            # 2026
            fwd26_valid = fwd_merged.dropna(subset=['2026_npat', 'market_cap'])
            fwd26_agg = fwd26_valid.groupby('date').agg(
                mc=('market_cap', 'sum'),
                npat26=('2026_npat', 'sum')
            )
            fwd26_agg['pe_fwd_2026'] = fwd26_agg['mc'] / fwd26_agg['npat26']
            
            # Merge back to result
            result_df = result_df.merge(fwd25_agg[['pe_fwd_2025']], on='date', how='left')
            result_df = result_df.merge(fwd26_agg[['pe_fwd_2026']], on='date', how='left')
        else:
            result_df['pe_fwd_2025'] = np.nan
            result_df['pe_fwd_2026'] = np.nan
            
        return result_df

    def process_all_scopes(self, exclude_list: list = None, start_date: datetime = None, end_date: datetime = None):
        """
        Run valuation for VNINDEX, VNINDEX_EXCLUDE, and BSC_INDEX.
        Args:
            start_date: Start date for incremental update.
            end_date: End date for incremental update.
        """
        if exclude_list is None: exclude_list = ['VIC', 'VHM', 'VRE', 'MSN'] # Default
        
        forecast_df = self.load_bsc_forecast_data()
        bsc_symbols = forecast_df['symbol'].tolist() if forecast_df is not None else []
        
        # 1. VNINDEX
        df1 = self.calculate_scope_valuation(scope_name='VNINDEX', start_date=start_date, end_date=end_date)
        
        # 2. VNINDEX EXCLUDE
        df2 = self.calculate_scope_valuation(scope_name='VNINDEX_EXCLUDE', excluded_symbols=exclude_list, start_date=start_date, end_date=end_date)
        
        # 3. BSC INDEX
        if bsc_symbols:
            df3 = self.calculate_scope_valuation(scope_name='BSC_INDEX', 
                                                 subset_symbols=bsc_symbols,
                                                 bsc_forecast_df=forecast_df,
                                                 start_date=start_date, end_date=end_date)
        else:
            logger.warning("Skipping BSC_INDEX due to missing forecast data.")
            df3 = pd.DataFrame()
            
        # Combine
        final_df = pd.concat([df1, df2, df3], ignore_index=True)
        if not final_df.empty:
            final_df = final_df.sort_values(['scope', 'date'])
        
        return final_df

    def process_all_scopes_with_sectors(
        self,
        exclude_list: list = None,
        include_sectors: bool = True,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> pd.DataFrame:
        """
        Run valuation for VNINDEX, VNINDEX_EXCLUDE, BSC_INDEX, and ALL SECTORS.

        This is the unified method that combines market-wide and sector-level valuations.

        Args:
            exclude_list: Symbols to exclude from VNINDEX_EXCLUDE (default: VIC, VHM, VRE, MSN)
            include_sectors: If True, calculate PE/PB for all 19 sectors
            start_date: Start date for incremental update
            end_date: End date for incremental update

        Returns:
            Combined DataFrame with columns:
            [date, scope, scope_type, pe_ttm, pb, pe_fwd_2025, pe_fwd_2026,
             total_mc_pe, total_mc_pb, total_earnings, total_equity]

            scope_type values:
            - 'MARKET' for VNINDEX, VNINDEX_EXCLUDE, BSC_INDEX
            - 'SECTOR' for sector scopes

        Examples:
            date       | scope              | scope_type | pe_ttm | pb
            -----------|--------------------|-----------:|-------:|----
            2024-12-15 | VNINDEX            | MARKET     | 15.2   | 2.1
            2024-12-15 | VNINDEX_EXCLUDE    | MARKET     | 17.3   | 2.3
            2024-12-15 | BSC_INDEX          | MARKET     | 14.5   | 2.0
            2024-12-15 | SECTOR:Banking     | SECTOR     | 8.2    | 1.3
            2024-12-15 | SECTOR:RealEstate  | SECTOR     | 22.1   | 2.8
        """
        logger.info("=" * 80)
        logger.info("🚀 PROCESSING ALL SCOPES (MARKET + SECTORS)")
        logger.info("=" * 80)

        results = []

        # STEP 1: Process market scopes (VNINDEX, VNINDEX_EXCLUDE, BSC_INDEX)
        logger.info("\n[1/2] Processing market scopes...")
        market_df = self.process_all_scopes(
            exclude_list=exclude_list,
            start_date=start_date,
            end_date=end_date
        )

        if not market_df.empty:
            market_df['scope_type'] = 'MARKET'
            results.append(market_df)
            logger.info(f"  ✅ Market scopes: {market_df['scope'].nunique()} scopes, {len(market_df)} records")

        # STEP 2: Process all sectors
        if include_sectors:
            logger.info("\n[2/2] Processing sector scopes...")
            sectors = self.sector_reg.get_all_sectors()
            logger.info(f"  Found {len(sectors)} sectors")

            forecast_df = self.load_bsc_forecast_data()
            sector_results = []

            for i, sector in enumerate(sectors, 1):
                # Get tickers for this sector
                tickers = self.sector_reg.get_tickers_by_sector(sector)
                if not tickers:
                    logger.warning(f"  ⚠️  Sector {sector} has no tickers")
                    continue

                logger.info(f"  ({i}/{len(sectors)}) Processing sector: {sector} ({len(tickers)} tickers)")

                # Calculate valuation for this sector
                sector_df = self.calculate_scope_valuation(
                    scope_name=f"SECTOR:{sector}",
                    subset_symbols=tickers,
                    bsc_forecast_df=forecast_df,
                    start_date=start_date,
                    end_date=end_date
                )

                if not sector_df.empty:
                    sector_results.append(sector_df)

            if sector_results:
                sector_combined = pd.concat(sector_results, ignore_index=True)
                sector_combined['scope_type'] = 'SECTOR'
                results.append(sector_combined)
                logger.info(f"  ✅ Sector scopes: {len(sectors)} sectors, {len(sector_combined)} records")
        else:
            logger.info("\n[2/2] Skipping sector processing (include_sectors=False)")

        # STEP 3: Combine all results
        if not results:
            logger.warning("⚠️  No results generated!")
            return pd.DataFrame()

        final_df = pd.concat(results, ignore_index=True)
        final_df = final_df.sort_values(['scope_type', 'scope', 'date'])

        logger.info("\n" + "=" * 80)
        logger.info("✅ PROCESSING COMPLETE")
        logger.info("=" * 80)
        logger.info(f"\nTotal records: {len(final_df)}")
        logger.info(f"Market scopes: {len(final_df[final_df['scope_type']=='MARKET'])}")
        logger.info(f"Sector scopes: {len(final_df[final_df['scope_type']=='SECTOR'])}")
        logger.info(f"Date range: {final_df['date'].min()} to {final_df['date'].max()}")
        logger.info(f"Unique scopes: {final_df['scope'].nunique()}")
        logger.info("=" * 80)

        return final_df

    def save_results(self, df: pd.DataFrame, filename: str):
        self.output_path.mkdir(parents=True, exist_ok=True)
        path = self.output_path / filename
        df.to_parquet(path, index=False)
        logger.info(f"Saved to {path}")

def main():
    logging.basicConfig(level=logging.INFO)
    calc = VNIndexValuationCalculator()
    calc.load_data()
    
    # 1. Full Market
    df_full = calc.calculate_index_valuation()
    print("Full Index PE (Latest):", df_full.iloc[-1]['index_pe'])
    
    # 2. Exclude VinGroup
    df_excl = calc.calculate_index_valuation(excluded_symbols=['VIC', 'VHM', 'VRE', 'VPL'])
    print("Excl. Vin PE (Latest):", df_excl.iloc[-1]['index_pe'])
    
    calc.save_results(df_full, "vnindex_valuation_full.parquet")
    calc.save_results(df_excl, "vnindex_valuation_excl_vin.parquet")

if __name__ == "__main__":
    main()
