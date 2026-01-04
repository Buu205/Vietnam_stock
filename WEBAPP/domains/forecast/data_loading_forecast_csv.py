"""
Forecast Data Loading Module - CSV Version
==========================================

Load and process forecast data from CSV file (processed by BSC Auto Update),
merge with current market data for comprehensive analysis.

This replaces the Excel-based loader for better performance and automation.

Updated: 2025-11-11 - Using centralized DataPaths configuration
Updated: 2026-01-04 - Fixed caching with standalone cached functions
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, List, Tuple
import logging
from pathlib import Path
from datetime import datetime
import streamlit as st
from WEBAPP.core.utils import get_data_path
from WEBAPP.core.data_paths import DataPaths, get_valuation_path, get_fundamental_path
from WEBAPP.core.constants import CACHE_TTL_COLD

logger = logging.getLogger(__name__)


# =============================================================================
# STANDALONE CACHED FUNCTIONS (avoid class method caching issues)
# =============================================================================

@st.cache_data(ttl=CACHE_TTL_COLD, show_spinner=False)
def _cached_load_forecast_csv(csv_path: str) -> pd.DataFrame:
    """Cached: Load forecast data from CSV file"""
    try:
        path = Path(csv_path)
        if not path.exists():
            logger.warning(f"Forecast CSV file not found: {path}")
            return pd.DataFrame()

        df = pd.read_csv(path)
        logger.info(f"Loaded forecast CSV data: {df.shape}")

        if df.empty:
            return pd.DataFrame()

        # Normalize symbol column
        if 'Symbol' in df.columns:
            df['symbol'] = df['Symbol'].str.strip().str.upper()
        elif 'symbol' in df.columns:
            df['symbol'] = df['symbol'].str.strip().str.upper()
        else:
            logger.error("CSV file missing 'Symbol' or 'symbol' column")
            return pd.DataFrame()

        df = df.dropna(subset=['symbol'])
        df = df[df['symbol'] != '']

        logger.info(f"Forecast CSV data after cleaning: {df.shape}")
        return df

    except Exception as e:
        logger.error(f"Error loading forecast CSV: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=CACHE_TTL_COLD, show_spinner=False)
def _cached_load_pe_pb_latest(pe_path: str, pb_path: str, symbols: Tuple[str, ...]) -> Dict[str, Dict]:
    """Cached: Load latest PE/PB for given symbols"""
    pe_pb_data = {}
    symbols_set = set(symbols)

    try:
        # Load PE data
        pe_file = Path(pe_path)
        if pe_file.exists():
            pe_df = pd.read_parquet(pe_file)
            pe_df = pe_df[pe_df['symbol'].isin(symbols_set)]
            if not pe_df.empty:
                pe_df['date'] = pd.to_datetime(pe_df['date'])
                latest_pe = pe_df.loc[pe_df.groupby('symbol')['date'].idxmax()]
                for _, row in latest_pe.iterrows():
                    symbol = row['symbol']
                    pe_pb_data[symbol] = {'pe_ttm': row.get('pe_ratio')}

        # Load PB data
        pb_file = Path(pb_path)
        if pb_file.exists():
            pb_df = pd.read_parquet(pb_file)
            pb_df = pb_df[pb_df['symbol'].isin(symbols_set)]
            if not pb_df.empty:
                pb_df['date'] = pd.to_datetime(pb_df['date'])
                latest_pb = pb_df.loc[pb_df.groupby('symbol')['date'].idxmax()]
                for _, row in latest_pb.iterrows():
                    symbol = row['symbol']
                    if symbol not in pe_pb_data:
                        pe_pb_data[symbol] = {}
                    pe_pb_data[symbol]['pb_ttm'] = row.get('pb_ratio')

        logger.info(f"Loaded PE/PB TTM for {len(pe_pb_data)} symbols")

    except Exception as e:
        logger.error(f"Error loading PE/PB TTM: {e}")

    return pe_pb_data


@st.cache_data(ttl=CACHE_TTL_COLD, show_spinner=False)
def _cached_load_ohlcv_latest(ohlcv_path: str, symbols: Tuple[str, ...]) -> pd.DataFrame:
    """Cached: Load latest OHLCV data for given symbols"""
    try:
        path = Path(ohlcv_path)
        if not path.exists():
            return pd.DataFrame()

        ohlcv_df = pd.read_parquet(path, columns=['symbol', 'date', 'close', 'market_cap'])
        ohlcv_df = ohlcv_df[ohlcv_df['symbol'].isin(set(symbols))]

        if ohlcv_df.empty:
            return pd.DataFrame()

        ohlcv_df['date'] = pd.to_datetime(ohlcv_df['date'])
        latest_data = ohlcv_df.loc[ohlcv_df.groupby('symbol')['date'].idxmax()]

        logger.info(f"Loaded OHLCV for {len(latest_data)} symbols")
        return latest_data[['symbol', 'close', 'market_cap']]

    except Exception as e:
        logger.error(f"Error loading OHLCV: {e}")
        return pd.DataFrame()

class ForecastDataLoaderCSV:
    """Load and process forecast data from CSV files"""
    
    def __init__(self, csv_path: str = None):
        """Initialize with CSV file path"""
        if csv_path is None:
            # Default path to latest CSV file from auto processor
            self.csv_path = Path(get_data_path('DATA/processed/forecast/bsc/bsc_forecast_latest.csv'))
        else:
            self.csv_path = Path(csv_path)
        
        # Data paths for market data - Using centralized configuration
        self.pe_path = get_valuation_path('pe')
        self.pb_path = get_valuation_path('pb')
        self.ohlcv_path = DataPaths.raw_ohlcv()
        self.company_fund_path = get_fundamental_path('company')
        self.bank_fund_path = get_fundamental_path('bank')
    
    def load_forecast_csv(self) -> pd.DataFrame:
        """Load forecast data from CSV file (uses cached standalone function)"""
        return _cached_load_forecast_csv(str(self.csv_path))
    
    def load_current_market_data(self) -> Dict[str, pd.DataFrame]:
        """Load current market data for comparison (uses cached functions)"""
        current_data = {}

        # Get forecast symbols first
        forecast_df = self.load_forecast_csv()
        if forecast_df.empty:
            return {'pe': pd.DataFrame(), 'pb': pd.DataFrame(), 'prices': pd.DataFrame(), 'actual_fund': pd.DataFrame()}

        forecast_symbols = tuple(forecast_df['symbol'].str.upper().str.strip().unique())

        # Load prices from cached OHLCV
        prices_df = _cached_load_ohlcv_latest(str(self.ohlcv_path), forecast_symbols)
        current_data['prices'] = prices_df

        # PE/PB loaded via load_pe_pb_ttm_for_bsc_symbols (already cached)
        current_data['pe'] = pd.DataFrame()
        current_data['pb'] = pd.DataFrame()
        current_data['actual_fund'] = pd.DataFrame()

        return current_data
    
    def load_actual_fundamental_data_2025(self) -> pd.DataFrame:
        """Load actual YTD data for forecast symbols - same logic as Excel version"""
        try:
            # First, get forecast symbols to filter
            forecast_df = self.load_forecast_csv()
            if forecast_df.empty:
                logger.warning("No forecast data available for filtering")
                return pd.DataFrame()
            
            forecast_symbols = set(forecast_df['symbol'].str.upper())
            logger.info(f"Loading YTD data for {len(forecast_symbols)} forecast symbols")
            
            # Load full database
            full_db_path = get_data_path('DATA/raw/fundamental/full_database.parquet')
            df = pd.read_parquet(full_db_path)
            
            # Filter early to reduce memory usage
            current_year = pd.Timestamp.now().year
            df = df[
                (df['SECURITY_CODE'].isin(forecast_symbols)) &
                (df['YEAR'] == current_year) &
                (df['FREQ_CODE'] == 'Q')
            ].copy()
            
            # Define metric codes by entity type
            bank_metrics = {
                'revenue': 'BIS_1',      # Bank revenue
                'profit': 'BIS_22A'      # Bank profit (NPAT)
            }
            company_metrics = {
                'revenue': 'CIS_10',     # Company revenue  
                'profit': 'CIS_61'       # Company profit (NPAT)
            }
            
            # Filter for target metrics only
            current_data = df[
                df['METRIC_CODE'].isin(['BIS_1', 'BIS_22A', 'CIS_10', 'CIS_61'])
            ].copy()
            
            if current_data.empty:
                logger.warning(f"No current year data found for forecast symbols in {current_year}")
                return pd.DataFrame()
            
            logger.info(f"Found data for {current_data['SECURITY_CODE'].nunique()} forecast symbols")
            
            # Calculate YTD for each symbol and metric
            ytd_data = []
            
            for symbol in current_data['SECURITY_CODE'].unique():
                symbol_data = current_data[current_data['SECURITY_CODE'] == symbol]
                
                # Determine entity type (Bank vs Company)
                entity_type = 'BANK' if symbol_data['METRIC_CODE'].str.startswith('B').any() else 'COMPANY'
                metrics = bank_metrics if entity_type == 'BANK' else company_metrics
                
                # Calculate YTD for revenue and profit
                ytd_revenue, quarters_count = self._calculate_ytd(symbol_data, metrics['revenue'])
                ytd_profit, _ = self._calculate_ytd(symbol_data, metrics['profit'])
                
                if ytd_revenue is not None and ytd_profit is not None:
                    ytd_data.append({
                        'symbol': symbol,
                        'entity_type': entity_type,
                        'ytd_revenue': ytd_revenue,
                        'ytd_profit': ytd_profit,
                    })
            
            result_df = pd.DataFrame(ytd_data)
            logger.info(f"Loaded YTD data: {len(result_df)} symbols")
            return result_df
            
        except Exception as e:
            logger.error(f"Error loading actual YTD data: {e}")
            return pd.DataFrame()
    
    def _calculate_ytd(self, symbol_data: pd.DataFrame, metric_code: str) -> tuple:
        """Calculate YTD for a specific metric - same logic as Excel version"""
        try:
            metric_data = symbol_data[symbol_data['METRIC_CODE'] == metric_code].copy()
            
            if metric_data.empty:
                return None, 0
            
            # Sort by quarter
            metric_data = metric_data.sort_values('QUARTER')
            
            # Sum all available quarters from Q1 to current quarter
            ytd_value = metric_data['METRIC_VALUE'].sum()
            quarters_count = len(metric_data)
            
            # Convert to billions VND
            return ytd_value / 1e9, quarters_count
                
        except Exception as e:
            logger.error(f"Error calculating YTD for {metric_code}: {e}")
            return None, 0
    
    def create_comprehensive_forecast_table(self) -> pd.DataFrame:
        """Create comprehensive forecast table with all metrics - adapted for CSV input"""
        try:
            # Load forecast and current data
            forecast_df = self.load_forecast_csv()
            current_data = self.load_current_market_data()
            
            if forecast_df.empty:
                logger.warning("No forecast data available")
                return pd.DataFrame()
            
            logger.info(f"Processing {len(forecast_df)} forecast records from CSV")
            
            # Load PE/PB TTM for BSC symbols only
            bsc_symbols = forecast_df['symbol'].str.upper().str.strip().tolist()
            pe_pb_ttm_data = self.load_pe_pb_ttm_for_bsc_symbols(bsc_symbols)
            
            # Create result dataframe
            result_rows = []
            
            for _, forecast_row in forecast_df.iterrows():
                symbol = str(forecast_row['symbol']).upper().strip()
                
                if pd.isna(symbol) or symbol == '':
                    continue
                
                row_data = {'symbol': symbol}
                
                # Rating with emoji formatting
                rating = forecast_row.get('rating')
                if pd.notna(rating) and str(rating).strip() != '':
                    rating_clean = str(rating).strip().upper()
                    if rating_clean == 'BUY':
                        row_data['rating'] = f"🟢 {rating_clean}"
                    elif rating_clean == 'HOLD':
                        row_data['rating'] = f"🟡 {rating_clean}"
                    elif rating_clean == 'SELL':
                        row_data['rating'] = f"🔴 {rating_clean}"
                    else:
                        row_data['rating'] = f"⚪ {rating_clean}"
                else:
                    row_data['rating'] = '⚪ N/A'
                
                # Current price and market cap from market data
                prices_df = current_data.get('prices')
                current_price = self.get_current_price(symbol, prices_df)
                row_data['current_price'] = current_price
                
                # Get market cap from prices data
                market_cap = None
                if prices_df is not None and not prices_df.empty:
                    symbol_price_data = prices_df[prices_df['symbol'] == symbol]
                    if not symbol_price_data.empty:
                        market_cap = symbol_price_data.iloc[0].get('market_cap')
                        # Convert market cap to billions VND if it's in VND
                        if market_cap is not None and pd.notna(market_cap):
                            # Assuming market_cap is already in billions VND from OHLCV
                            # If it's in VND, divide by 1e9
                            if market_cap > 1000000:  # If > 1M, likely in VND, convert to billions
                                market_cap = market_cap / 1e9
                
                row_data['market_cap'] = market_cap if pd.notna(market_cap) else None
                
                # Target price and upside from CSV
                # VN: Tính giá mục tiêu và % tăng giá (upside)
                # Support both title case and lowercase
                target_price = forecast_row.get('Target_Price') or forecast_row.get('target_price')
                if target_price and current_price and pd.notna(target_price) and pd.notna(current_price):
                    target_price = float(target_price)
                    current_price = float(current_price)
                    # Upside % = (Target Price / Current Price - 1) × 100
                    upside = ((target_price / current_price) - 1) * 100
                    row_data['target_price'] = target_price
                    row_data['upside_pct'] = upside
                    
                    # ===== RECOMMENDATION LOGIC =====
                    # Tính toán khuyến nghị dựa trên % tăng giá (upside)
                    # 
                    # Rules (Quy tắc):
                    # - 🔥 STRONG BUY: upside >= 20%   (Tiềm năng tăng từ 20% trở lên)
                    # - 🟢 BUY:      10% <= upside < 20%  (Tiềm năng tăng từ 10-20%)
                    # - 🟡 HOLD:     -10% < upside < 10%  (Dao động trong khoảng ±10%)
                    # - 🔴 SELL:     -20% < upside <= -10%  (Giá hiện tại cao hơn mục tiêu 10-20%)
                    # - 🔥 STRONG SELL: upside <= -20%  (Giá hiện tại cao hơn mục tiêu >20%)
                    #
                    # Giải thích:
                    # - upside dương (+): Giá mục tiêu CAO HƠN giá hiện tại → Cơ hội mua
                    # - upside âm (-): Giá mục tiêu THẤP HƠN giá hiện tại → Cổ phiếu đắt
                    # - Ngưỡng ±10%: Buffer zone để tránh trading quá nhiều
                    # - Ngưỡng ±20%: Strong signal cho các cơ hội/risk lớn
                    if upside >= 20:
                        row_data['recommendation'] = '🔥 STRONG BUY'
                    elif upside >= 10:
                        row_data['recommendation'] = '🟢 BUY'
                    elif upside <= -20:
                        row_data['recommendation'] = '🔥 STRONG SELL'
                    elif upside <= -10:
                        row_data['recommendation'] = '🔴 SELL'
                    else:  # -10% < upside < 10%
                        row_data['recommendation'] = '🟡 HOLD'
                else:
                    row_data['target_price'] = target_price if pd.notna(target_price) else None
                    row_data['upside_pct'] = None
                    row_data['recommendation'] = '⚪ N/A'
                
                # Current PE/PB (TTM) from DATA/processed/valuation
                symbol_pe_pb = pe_pb_ttm_data.get(symbol, {})
                row_data['pe_ttm'] = symbol_pe_pb.get('pe_ttm')
                row_data['pb_ttm'] = symbol_pe_pb.get('pb_ttm')
                
                # Load forecast data from CSV - Support both lowercase and title case column names
                # Try title case first (new format), then lowercase (old format)
                rev_2025 = forecast_row.get('Rev_2025') or forecast_row.get('rev_2025')
                rev_2026 = forecast_row.get('Rev_2026') or forecast_row.get('rev_2026')
                npat_2025 = forecast_row.get('NPAT_2025') or forecast_row.get('npat_2025')
                npat_2026 = forecast_row.get('NPAT_2026') or forecast_row.get('npat_2026')
                bvps_2025 = forecast_row.get('BVPS_2025') or forecast_row.get('bvps_2025')
                bvps_2026 = forecast_row.get('BVPS_2026') or forecast_row.get('bvps_2026')
                
                # Forward PE/PB from CSV (already calculated by daily_update_all_valuations.py)
                # Use PE_2025, PB_2025 from CSV if available, otherwise calculate
                pe_fwd_2025 = forecast_row.get('PE_2025') or forecast_row.get('pe_fwd_2025') or forecast_row.get('pe_2025')
                pe_fwd_2026 = forecast_row.get('PE_2026') or forecast_row.get('pe_fwd_2026') or forecast_row.get('pe_2026')
                pb_fwd_2025 = forecast_row.get('PB_2025') or forecast_row.get('pb_fwd_2025') or forecast_row.get('pb_2025')
                pb_fwd_2026 = forecast_row.get('PB_2026') or forecast_row.get('pb_fwd_2026') or forecast_row.get('pb_2026')
                
                # If not in CSV, calculate from market cap and NPAT
                if pd.isna(pe_fwd_2025) and market_cap is not None and npat_2025 is not None and pd.notna(npat_2025) and npat_2025 > 0:
                    pe_fwd_2025 = market_cap / npat_2025
                if pd.isna(pe_fwd_2026) and market_cap is not None and npat_2026 is not None and pd.notna(npat_2026) and npat_2026 > 0:
                    pe_fwd_2026 = market_cap / npat_2026
                
                row_data['pe_fwd_2025'] = pe_fwd_2025 if pd.notna(pe_fwd_2025) else None
                row_data['pe_fwd_2026'] = pe_fwd_2026 if pd.notna(pe_fwd_2026) else None
                row_data['pb_fwd_2025'] = pb_fwd_2025 if pd.notna(pb_fwd_2025) else None
                row_data['pb_fwd_2026'] = pb_fwd_2026 if pd.notna(pb_fwd_2026) else None
                
                # Growth rates from CSV (already calculated by daily_update_all_valuations.py)
                # Use Rev_Gr_25, NPAT_Gr_25 from CSV if available, otherwise calculate
                rev_gr_25 = forecast_row.get('Rev_Gr_25') or forecast_row.get('rev_gr_25')
                rev_gr_26 = forecast_row.get('Rev_Gr_26') or forecast_row.get('rev_gr_26')
                npat_gr_25 = forecast_row.get('NPAT_Gr_25') or forecast_row.get('npat_gr_25')
                npat_gr_26 = forecast_row.get('NPAT_Gr_26') or forecast_row.get('npat_gr_26')
                
                # If not in CSV, calculate from rev_2025, rev_2026, npat_2025, npat_2026
                if pd.isna(rev_gr_25) and pd.notna(rev_2025) and pd.notna(rev_2026) and rev_2025 > 0:
                    rev_gr_25 = ((rev_2026 - rev_2025) / rev_2025) * 100
                
                if pd.isna(npat_gr_25) and pd.notna(npat_2025) and pd.notna(npat_2026) and npat_2025 > 0:
                    npat_gr_25 = ((npat_2026 - npat_2025) / npat_2025) * 100
                
                row_data['rev_gr_25'] = rev_gr_25 if pd.notna(rev_gr_25) else None
                row_data['rev_gr_26'] = rev_gr_26 if pd.notna(rev_gr_26) else None
                row_data['npat_gr_25'] = npat_gr_25 if pd.notna(npat_gr_25) else None
                row_data['npat_gr_26'] = npat_gr_26 if pd.notna(npat_gr_26) else None
                
                # Business performance metrics from CSV (already loaded above for growth calculation)
                # rev_2025, rev_2026, npat_2025, npat_2026 already loaded
                
                # Store forecast values
                row_data['2025_rev'] = rev_2025 if pd.notna(rev_2025) else None
                row_data['2026_rev'] = rev_2026 if pd.notna(rev_2026) else None
                row_data['2025_npat'] = npat_2025 if pd.notna(npat_2025) else None
                row_data['2026_npat'] = npat_2026 if pd.notna(npat_2026) else None
                
                # Keep old column names for backward compatibility
                row_data['rev_forecast_2025'] = rev_2025 if pd.notna(rev_2025) else None
                row_data['profit_forecast_2025'] = npat_2025 if pd.notna(npat_2025) else None
                
                # Growth rates
                if rev_2025 and rev_2026 and pd.notna(rev_2025) and pd.notna(rev_2026) and rev_2025 > 0:
                    rev_growth = ((rev_2026 - rev_2025) / rev_2025) * 100
                    row_data['revenue_growth_pct'] = rev_growth
                else:
                    row_data['revenue_growth_pct'] = None
                
                if npat_2025 and npat_2026 and pd.notna(npat_2025) and pd.notna(npat_2026) and npat_2025 > 0:
                    profit_growth = ((npat_2026 - npat_2025) / npat_2025) * 100
                    row_data['profit_growth_pct'] = profit_growth
                else:
                    row_data['profit_growth_pct'] = None
                
                # Get actual YTD data for achievement calculation
                actual_fund = current_data.get('actual_fund')
                actual_symbol_data = None
                if actual_fund is not None and not actual_fund.empty:
                    actual_symbol_data = actual_fund[actual_fund['symbol'] == symbol]
                    if not actual_symbol_data.empty:
                        actual_symbol_data = actual_symbol_data.iloc[0]
                
                # Calculate achievement rates using YTD data
                if actual_symbol_data is not None:
                    ytd_revenue = actual_symbol_data.get('ytd_revenue', 0)
                    ytd_profit = actual_symbol_data.get('ytd_profit', 0)
                    
                    row_data['rev_2025F'] = ytd_revenue
                    row_data['profit_2025F'] = ytd_profit
                    
                    # Achievement rates
                    if rev_2025 and pd.notna(rev_2025) and rev_2025 > 0:
                        rev_achievement = (ytd_revenue / rev_2025) * 100
                        row_data['rev_achievement_pct'] = rev_achievement
                        row_data['%_rev_ach'] = rev_achievement
                    else:
                        row_data['rev_achievement_pct'] = None
                        row_data['%_rev_ach'] = None
                    
                    if npat_2025 and pd.notna(npat_2025) and npat_2025 > 0:
                        profit_achievement = (ytd_profit / npat_2025) * 100
                        row_data['profit_achievement_pct'] = profit_achievement
                        row_data['%_profit_ach'] = profit_achievement
                    else:
                        row_data['profit_achievement_pct'] = None
                        row_data['%_profit_ach'] = None
                        
                else:
                    row_data['rev_2025F'] = None
                    row_data['profit_2025F'] = None
                    row_data['rev_achievement_pct'] = None
                    row_data['profit_achievement_pct'] = None
                    row_data['%_rev_ach'] = None
                    row_data['%_profit_ach'] = None
                
                # ROE and ROA from CSV (already converted to percentage by auto processor)
                # Support both title case and lowercase
                roe_2025 = forecast_row.get('ROE_2025') or forecast_row.get('roe_2025')
                roe_2026 = forecast_row.get('ROE_2026') or forecast_row.get('roe_2026')
                roa_2025 = forecast_row.get('ROA_2025') or forecast_row.get('roa_2025')
                roa_2026 = forecast_row.get('ROA_2026') or forecast_row.get('roa_2026')
                
                row_data['roe_2025'] = roe_2025 if pd.notna(roe_2025) else None
                row_data['roe_2026'] = roe_2026 if pd.notna(roe_2026) else None
                row_data['roa_2025'] = roa_2025 if pd.notna(roa_2025) else None
                row_data['roa_2026'] = roa_2026 if pd.notna(roa_2026) else None
                
                # Determine sector
                bank_symbols = ['VCB', 'BID', 'CTG', 'TCB', 'VPB', 'ACB', 'MBB', 'HDB', 'STB', 'TPB', 'VIB', 'MSB', 'SHB', 'OCB', 'NAB', 'EIB']
                if symbol in bank_symbols:
                    row_data['sector'] = 'BANK'
                else:
                    row_data['sector'] = 'COMPANY'
                
                # Last update from CSV or current time
                
                result_rows.append(row_data)
            
            result_df = pd.DataFrame(result_rows)
            
            # Sort by sector first, then by symbol alphabetically
            result_df = result_df.sort_values(['sector', 'symbol'], ascending=[True, True])
            
            logger.info(f"Created comprehensive forecast table with {len(result_df)} records from CSV")
            return result_df
            
        except Exception as e:
            logger.error(f"Error creating comprehensive forecast table from CSV: {e}")
            return pd.DataFrame()
    
    def get_current_price(self, symbol: str, prices_df: Optional[pd.DataFrame]) -> Optional[float]:
        """Get current price for symbol"""
        if prices_df is None or prices_df.empty:
            return None
        
        symbol_data = prices_df[prices_df['symbol'] == symbol]
        if symbol_data.empty:
            return None
        
        return symbol_data.iloc[0].get('close')
    
    def load_pe_pb_ttm_for_bsc_symbols(self, bsc_symbols: list) -> dict:
        """Load PE/PB TTM from DATA/processed for BSC symbols only (uses cached function)"""
        pe_path = get_data_path('DATA/processed/valuation/pe/pe_historical_all_symbols_final.parquet')
        pb_path = get_data_path('DATA/processed/valuation/pb/pb_historical_all_symbols_final.parquet')
        # Convert list to tuple for caching (lists are not hashable)
        return _cached_load_pe_pb_latest(pe_path, pb_path, tuple(bsc_symbols))
    
    def get_current_pe(self, symbol: str, pe_df: Optional[pd.DataFrame]) -> Optional[float]:
        """Get current PE for symbol - DEPRECATED, use load_pe_pb_ttm_for_bsc_symbols instead"""
        if pe_df is None or pe_df.empty:
            return None
        
        symbol_data = pe_df[pe_df['symbol'] == symbol]
        if symbol_data.empty:
            return None
        
        return symbol_data.iloc[0].get('pe_ratio')
    
    def get_current_pb(self, symbol: str, pb_df: Optional[pd.DataFrame]) -> Optional[float]:
        """Get current PB for symbol - DEPRECATED, use load_pe_pb_ttm_for_bsc_symbols instead"""
        if pb_df is None or pb_df.empty:
            return None
        
        symbol_data = pb_df[pb_df['symbol'] == symbol]
        if symbol_data.empty:
            return None
        
        return symbol_data.iloc[0].get('pb_ratio')


@st.cache_data(ttl=CACHE_TTL_COLD, show_spinner=False)
def load_comprehensive_forecast_data_csv() -> pd.DataFrame:
    """Main function to load comprehensive forecast data from CSV (cached)"""
    loader = ForecastDataLoaderCSV()
    return loader.create_comprehensive_forecast_table()


def get_forecast_symbols_csv() -> List[str]:
    """Get list of symbols with forecast data from CSV"""
    loader = ForecastDataLoaderCSV()
    forecast_df = loader.load_forecast_csv()
    
    if forecast_df.empty:
        return []
    
    return forecast_df['symbol'].dropna().unique().tolist()


def check_csv_data_freshness() -> Dict[str, str]:
    """Check freshness of CSV data"""
    csv_path = Path(get_data_path('DATA/processed/forecast/bsc/bsc_forecast_latest.csv'))
    
    if not csv_path.exists():
        return {
            'status': 'missing',
            'message': 'File CSV chưa được tạo. Chạy run_bsc_auto_update.py để tạo dữ liệu.',
        }
    
    try:
        # Get file modification time
        mod_time = datetime.fromtimestamp(csv_path.stat().st_mtime)
        time_diff = datetime.now() - mod_time
        
        if time_diff.days > 7:
            status = 'old'
            message = f'Dữ liệu cũ ({time_diff.days} ngày). Nên cập nhật bằng run_bsc_auto_update.py'
        elif time_diff.days > 1:
            status = 'stale'
            message = f'Dữ liệu hơi cũ ({time_diff.days} ngày)'
        else:
            status = 'fresh'
            message = 'Dữ liệu mới'
        
        return {
            'status': status,
            'message': message,
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Lỗi kiểm tra file: {e}',
        }
