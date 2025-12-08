"""
Forecast Data Loading Module
===========================

Load and process forecast data from Excel file, merge with current market data
for comprehensive analysis.

Updated: 2025-11-11 - Using centralized DataPaths configuration
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, List
import logging
from pathlib import Path
from datetime import datetime
import streamlit as st
from streamlit_app.core.utils import get_data_path
from streamlit_app.core.data_paths import DataPaths, get_valuation_path, get_fundamental_path

logger = logging.getLogger(__name__)

class ForecastDataLoader:
    """Load and process forecast data"""
    
    def __init__(self, excel_path: str = None):
        """Initialize with Excel file path"""
        if excel_path is None:
            # Default path to forecast Excel file - Updated path
            self.excel_path = Path(get_data_path('data_processor/Bsc_forecast/Database Forecast BSC.xlsx'))
        else:
            self.excel_path = Path(excel_path)
        
        # Data paths - Using centralized configuration
        self.pe_path = get_valuation_path('pe')
        self.pb_path = get_valuation_path('pb')
        self.ohlcv_path = DataPaths.raw_ohlcv()
        self.company_fund_path = get_fundamental_path('company')
        self.bank_fund_path = get_fundamental_path('bank')
    
    @st.cache_data(ttl=3600, max_entries=8)  # Cache for 1 hour, max 8 entries
    def load_forecast_excel(_self) -> pd.DataFrame:
        """Load forecast data from Excel file - Codedata sheet"""
        try:
            if not _self.excel_path.exists():
                logger.warning(f"Forecast file not found: {_self.excel_path}")
                return pd.DataFrame()
            
            # Read the "Codedata" sheet which has the structured forecast data
            df = pd.read_excel(_self.excel_path, sheet_name='Codedata')
            logger.info(f"Loaded forecast data: {df.shape}")
            
            # Clean column names
            df.columns = df.columns.str.strip()
            
            # Standardize ticker column
            if 'ticker' in df.columns:
                df['ticker'] = df['ticker'].str.strip().str.upper()
            
            # Remove rows with NaN ticker
            df = df.dropna(subset=['ticker'])
            
            logger.info(f"Forecast data after cleaning: {df.shape}")
            return df
            
        except Exception as e:
            logger.error(f"Error loading forecast Excel: {e}")
            return pd.DataFrame()
    
    @st.cache_data(ttl=1800, max_entries=16)  # Cache for 30 minutes, max 16 entries
    def load_current_market_data(_self) -> Dict[str, pd.DataFrame]:
        """Load current market data for comparison"""
        try:
            current_data = {}
            
            # Load PE data (latest only - optimized)
            if _self.pe_path.exists():
                pe_df = pd.read_parquet(_self.pe_path)
                pe_df['date'] = pd.to_datetime(pe_df['date'])
                # Get latest PE for each symbol - more efficient
                latest_pe = pe_df.loc[pe_df.groupby('symbol')['date'].idxmax()]
                current_data['pe'] = latest_pe
            
            # Load PB data (latest only - optimized)
            if _self.pb_path.exists():
                pb_df = pd.read_parquet(_self.pb_path)
                pb_df['date'] = pd.to_datetime(pb_df['date'])
                # Get latest PB for each symbol - more efficient
                latest_pb = pb_df.loc[pb_df.groupby('symbol')['date'].idxmax()]
                current_data['pb'] = latest_pb
            
            # Load current prices (latest only - optimized)
            if _self.ohlcv_path.exists():
                ohlcv_df = pd.read_parquet(_self.ohlcv_path)
                ohlcv_df['date'] = pd.to_datetime(ohlcv_df['date'])
                # Get latest prices - more efficient
                latest_prices = ohlcv_df.loc[ohlcv_df.groupby('symbol')['date'].idxmax()]
                current_data['prices'] = latest_prices
            
            # Load actual fundamental data for 2025
            current_data['actual_fund'] = _self.load_actual_fundamental_data_2025()
            
            return current_data
            
        except Exception as e:
            logger.error(f"Error loading current market data: {e}")
            return {}
    
    @st.cache_data(ttl=3600, max_entries=16)  # Cache for 1 hour, max 16 entries
    def load_actual_fundamental_data_2025(_self) -> pd.DataFrame:
        """Load actual YTD (Year-to-Date) revenue and profit from full_database.parquet for forecast symbols only"""
        try:
            # First, get forecast symbols to filter
            forecast_df = _self.load_forecast_excel()
            if forecast_df.empty:
                logger.warning("No forecast data available for filtering")
                return pd.DataFrame()
            
            forecast_symbols = set(forecast_df['ticker'].str.upper())
            logger.info(f"Loading YTD data for {len(forecast_symbols)} forecast symbols")
            
            # Load full database - use get_data_path for consistency
            full_db_path = get_data_path('data_warehouse/raw/fundamental/full_database.parquet')
            df = pd.read_parquet(full_db_path)
            
            # Filter early to reduce memory usage - only load forecast symbols and current year
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
            
            # Filter for target metrics only (already filtered by symbols and year above)
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
                ytd_revenue, quarters_count = _self._calculate_ytd(symbol_data, metrics['revenue'])
                ytd_profit, _ = _self._calculate_ytd(symbol_data, metrics['profit'])
                
                if ytd_revenue is not None and ytd_profit is not None:
                    ytd_data.append({
                        'symbol': symbol,
                        'entity_type': entity_type,
                        'ytd_revenue': ytd_revenue,
                        'ytd_profit': ytd_profit,
                        'quarters_available': quarters_count
                    })
            
            result_df = pd.DataFrame(ytd_data)
            logger.info(f"Loaded YTD data: {len(result_df)} symbols")
            return result_df
            
        except Exception as e:
            logger.error(f"Error loading actual TTM data: {e}")
            return pd.DataFrame()
    
    def _calculate_ytd(self, symbol_data: pd.DataFrame, metric_code: str) -> tuple:
        """Calculate YTD (Year-to-Date) for a specific metric - sum from Q1 to current quarter"""
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
        """Create comprehensive forecast table with all metrics"""
        try:
            # Load forecast and current data
            forecast_df = self.load_forecast_excel()
            current_data = self.load_current_market_data()
            
            if forecast_df.empty:
                logger.warning("No forecast data available")
                return pd.DataFrame()
            
            logger.info(f"Processing {len(forecast_df)} forecast records")
            
            # Create result dataframe
            result_rows = []
            
            for _, forecast_row in forecast_df.iterrows():
                symbol = str(forecast_row['ticker']).upper().strip()
                
                if pd.isna(symbol) or symbol == '':
                    continue
                
                row_data = {'symbol': symbol}
                
                # Rating (move to position 2)
                rating = forecast_row.get('Rating')
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
                
                # Current price
                current_price = self.get_current_price(symbol, current_data.get('prices'))
                row_data['current_price'] = current_price
                
                # Target price and upside
                target_price = forecast_row.get('target_price')
                if target_price and current_price and pd.notna(target_price) and pd.notna(current_price):
                    target_price = float(target_price)
                    current_price = float(current_price)
                    # Upside = ((target_price / current_price) - 1) * 100
                    upside = ((target_price / current_price) - 1) * 100
                    row_data['target_price'] = target_price
                    row_data['upside_pct'] = upside
                else:
                    row_data['target_price'] = target_price if pd.notna(target_price) else None
                    row_data['upside_pct'] = None
                
                # Current PE/PB (TTM)
                current_pe = self.get_current_pe(symbol, current_data.get('pe'))
                current_pb = self.get_current_pb(symbol, current_data.get('pb'))
                row_data['pe_ttm'] = current_pe
                row_data['pb_ttm'] = current_pb
                
                # Forward PE/PB from forecast
                # Calculate forward PE from EPS and target price
                eps_2025 = forecast_row.get('2025_eps')
                eps_2026 = forecast_row.get('2026_eps')
                
                if target_price and eps_2025 and pd.notna(target_price) and pd.notna(eps_2025):
                    pe_fwd_2025 = target_price / eps_2025
                    row_data['pe_fwd_2025'] = pe_fwd_2025
                else:
                    row_data['pe_fwd_2025'] = None
                
                if target_price and eps_2026 and pd.notna(target_price) and pd.notna(eps_2026):
                    pe_fwd_2026 = target_price / eps_2026
                    row_data['pe_fwd_2026'] = pe_fwd_2026
                else:
                    row_data['pe_fwd_2026'] = None
                
                # Forward PB from BV and target price
                bv_2025 = forecast_row.get('2025_bv')
                bv_2026 = forecast_row.get('2026_bv')
                
                if target_price and bv_2025 and pd.notna(target_price) and pd.notna(bv_2025):
                    pb_fwd_2025 = target_price / bv_2025
                    row_data['pb_fwd_2025'] = pb_fwd_2025
                else:
                    row_data['pb_fwd_2025'] = None
                
                if target_price and bv_2026 and pd.notna(target_price) and pd.notna(bv_2026):
                    pb_fwd_2026 = target_price / bv_2026
                    row_data['pb_fwd_2026'] = pb_fwd_2026
                else:
                    row_data['pb_fwd_2026'] = None
                
                # Remove PE/PB change calculations as requested
                
                # Business performance metrics from forecast
                rev_2025 = forecast_row.get('2025_rev')
                npat_2025 = forecast_row.get('2025_npat')
                rev_2026 = forecast_row.get('2026_rev')
                npat_2026 = forecast_row.get('2026_npat')
                
                # Store forecast values with new column names
                row_data['2025_rev'] = rev_2025 if pd.notna(rev_2025) else None
                row_data['2026_rev'] = rev_2026 if pd.notna(rev_2026) else None
                row_data['2025_npat'] = npat_2025 if pd.notna(npat_2025) else None
                row_data['2026_npat'] = npat_2026 if pd.notna(npat_2026) else None
                
                # Keep old column names for backward compatibility
                row_data['rev_forecast_2025'] = rev_2025 if pd.notna(rev_2025) else None
                row_data['profit_forecast_2025'] = npat_2025 if pd.notna(npat_2025) else None
                
                # Revenue growth rate
                if rev_2025 and rev_2026 and pd.notna(rev_2025) and pd.notna(rev_2026) and rev_2025 > 0:
                    rev_growth = ((rev_2026 - rev_2025) / rev_2025) * 100
                    row_data['revenue_growth_pct'] = rev_growth
                else:
                    row_data['revenue_growth_pct'] = None
                
                # Profit growth rate
                if npat_2025 and npat_2026 and pd.notna(npat_2025) and pd.notna(npat_2026) and npat_2025 > 0:
                    profit_growth = ((npat_2026 - npat_2025) / npat_2025) * 100
                    row_data['profit_growth_pct'] = profit_growth
                else:
                    row_data['profit_growth_pct'] = None
                
                # Get actual TTM data for achievement calculation
                actual_fund = current_data.get('actual_fund')
                actual_symbol_data = None
                if actual_fund is not None and not actual_fund.empty:
                    actual_symbol_data = actual_fund[actual_fund['symbol'] == symbol]
                    if not actual_symbol_data.empty:
                        actual_symbol_data = actual_symbol_data.iloc[0]  # TTM data should be unique per symbol
                
                # Calculate achievement rates using YTD data
                if actual_symbol_data is not None:
                    # YTD data is already in billions VND
                    ytd_revenue = actual_symbol_data.get('ytd_revenue', 0)
                    ytd_profit = actual_symbol_data.get('ytd_profit', 0)
                    
                    row_data['rev_2025F'] = ytd_revenue  # YTD revenue (Q1+Q2+...)
                    row_data['profit_2025F'] = ytd_profit  # YTD profit (Q1+Q2+...)
                    
                    # Revenue achievement rate: YTD / Forecast 2025 * 100%
                    if rev_2025 and pd.notna(rev_2025) and rev_2025 > 0:
                        rev_achievement = (ytd_revenue / rev_2025) * 100
                        row_data['rev_achievement_pct'] = rev_achievement
                        row_data['%_rev_ach'] = rev_achievement  # YTD vs 2025 forecast
                    else:
                        row_data['rev_achievement_pct'] = None
                        row_data['%_rev_ach'] = None
                    
                    # Profit achievement rate: YTD / Forecast 2025 * 100%
                    if npat_2025 and pd.notna(npat_2025) and npat_2025 > 0:
                        profit_achievement = (ytd_profit / npat_2025) * 100
                        row_data['profit_achievement_pct'] = profit_achievement
                        row_data['%_profit_ach'] = profit_achievement  # YTD vs 2025 forecast
                    else:
                        row_data['profit_achievement_pct'] = None
                        row_data['%_profit_ach'] = None
                        
                    # Set quarters available (count available quarters)
                    row_data['quarters_available'] = actual_symbol_data.get('quarters_available', 2)
                else:
                    row_data['rev_2025F'] = None
                    row_data['profit_2025F'] = None
                    row_data['rev_achievement_pct'] = None
                    row_data['profit_achievement_pct'] = None
                    row_data['%_rev_ach'] = None
                    row_data['%_profit_ach'] = None
                    row_data['quarters_available'] = None
                
                # ROE and ROA from forecast (convert from decimal to percentage)
                roe_2025 = forecast_row.get('2025_roe')
                roe_2026 = forecast_row.get('2026_roe')
                roa_2025 = forecast_row.get('2025_roa')
                roa_2026 = forecast_row.get('2026_roa')
                
                # Convert decimal to percentage (0.16 -> 16.0)
                row_data['roe_2025'] = roe_2025 * 100 if pd.notna(roe_2025) else None
                row_data['roe_2026'] = roe_2026 * 100 if pd.notna(roe_2026) else None
                row_data['roa_2025'] = roa_2025 * 100 if pd.notna(roa_2025) else None
                row_data['roa_2026'] = roa_2026 * 100 if pd.notna(roa_2026) else None
                
                # Determine sector based on symbol
                bank_symbols = ['VCB', 'BID', 'CTG', 'TCB', 'VPB', 'ACB', 'MBB', 'HDB', 'STB', 'TPB', 'VIB', 'MSB', 'SHB', 'OCB', 'NAB', 'EIB']
                if symbol in bank_symbols:
                    row_data['sector'] = 'BANK'
                else:
                    row_data['sector'] = 'COMPANY'
                
                # Last update
                row_data['last_update'] = datetime.now().strftime('%Y-%m-%d')
                
                result_rows.append(row_data)
            
            result_df = pd.DataFrame(result_rows)
            
            # Sort by sector first, then by symbol alphabetically
            result_df = result_df.sort_values(['sector', 'symbol'], ascending=[True, True])
            
            logger.info(f"Created comprehensive forecast table with {len(result_df)} records")
            return result_df
            
        except Exception as e:
            logger.error(f"Error creating comprehensive forecast table: {e}")
            return pd.DataFrame()
    
    def get_current_price(self, symbol: str, prices_df: Optional[pd.DataFrame]) -> Optional[float]:
        """Get current price for symbol"""
        if prices_df is None or prices_df.empty:
            return None
        
        symbol_data = prices_df[prices_df['symbol'] == symbol]
        if symbol_data.empty:
            return None
        
        return symbol_data.iloc[0].get('close')
    
    def get_current_pe(self, symbol: str, pe_df: Optional[pd.DataFrame]) -> Optional[float]:
        """Get current PE for symbol"""
        if pe_df is None or pe_df.empty:
            return None
        
        symbol_data = pe_df[pe_df['symbol'] == symbol]
        if symbol_data.empty:
            return None
        
        return symbol_data.iloc[0].get('pe_ratio')
    
    def get_current_pb(self, symbol: str, pb_df: Optional[pd.DataFrame]) -> Optional[float]:
        """Get current PB for symbol"""
        if pb_df is None or pb_df.empty:
            return None
        
        symbol_data = pb_df[pb_df['symbol'] == symbol]
        if symbol_data.empty:
            return None
        
        return symbol_data.iloc[0].get('pb_ratio')


@st.cache_data(ttl=1800, max_entries=16)  # Cache for 30 minutes, max 16 entries
def load_comprehensive_forecast_data() -> pd.DataFrame:
    """Main function to load comprehensive forecast data"""
    loader = ForecastDataLoader()
    return loader.create_comprehensive_forecast_table()


def get_forecast_symbols() -> List[str]:
    """Get list of symbols with forecast data"""
    loader = ForecastDataLoader()
    forecast_df = loader.load_forecast_excel()
    
    if forecast_df.empty:
        return []
    
    return forecast_df['ticker'].dropna().unique().tolist()
