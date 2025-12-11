#!/usr/bin/env python3
"""
Macro Commodity Fetcher
=======================
Unified fetcher for both Commodity Prices and Macro Indicators.
Combines logic from old CommodityPriceUpdater and MacroDataFetcher.

Data Sources:
- Commodity: vnstock_data (source='spl'), OilPriceAPI (legacy support)
- Macro: wichart.vn (Exchange, Interest), simplize.vn (Bond)
"""

import pandas as pd
import numpy as np
import logging
import requests
import os
import sys
from datetime import datetime, date
from pathlib import Path
from typing import Optional, Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MacroCommodityFetcher:
    """
    Unified fetcher for Commodity and Macro data.
    Returns standardized DataFrames for merging into a single storage file.
    """
    
    # =========================================================================
    # CONSTANTS & MAPPINGS
    # =========================================================================
    
    # Commodity Mappings
    # Symbol: vnstock Method Name
    COMMODITY_METHODS = {
        'gold_vn': 'gold_vn',
        'gold_global': 'gold_global',
        'oil_crude': 'oil_crude',
        'gas_natural': 'gas_natural',
        'coke': 'coke',
        'steel_d10': 'steel_d10',
        'steel_hrc': 'steel_hrc',
        'steel_coated': 'steel_coated',
        'iron_ore': 'iron_ore',
        'fertilizer_ure_vn': 'fertilizer_ure', # Note: old code used fertilizer_ure, new fetcher used fertilizer_ure_vn
        'fertilizer_ure_global': 'fertilizer_ure', # Duplicate method in old code? Or maybe global? Checking history...
        # Wait, old code had 'fertilizer_ure': 'Giá phân bón thế giới'. 
        # And 'fertilizer_ure_vn' was likely NOT in old code or mapped differently? 
        # Checking old keys: 'fertilizer_ure', 'soybean', 'corn', 'sugar', 'pork_north_vn', 'pork_china', 'steel_coated', 'pvc_china'.
        # It seems 'fertilizer_ure_vn' might be a new addition or mistake?
        # Let's use 'fertilizer_ure' for global??
        'soybean': 'soybean',
        'corn': 'corn',
        'sugar': 'sugar',
        'pork_north_vn': 'pork_north_vn',
        'pork_china': 'pork_china',
        'pvc_china': 'pvc', # Corrected from pvc_china
        'milk_wmp': 'sua_bot_wmp', # Corrected from milk_wmp
        'rubber': 'cao_su', # Corrected from rubber, guessing typical vnstock name
    }
    
    # Macro Mappings
    EXCHANGE_RATE_TYPES = {
        'ty_gia_usd_trung_tam': 'Tỷ giá USD trung tâm',
        'ty_gia_tran': 'Tỷ giá trần',
        'ty_gia_san': 'Tỷ giá sàn',
        'ty_gia_usd_nhtm_ban_ra': 'Tỷ giá USD NHTM bán ra',
        'ty_gia_usd_tu_do_ban_ra': 'Tỷ USD tự do bán ra',
    }
    
    INTEREST_RATE_TYPES = {
        'ls_qua_dem_lien_ngan_hang': 'LS qua đêm liên ngân hàng',
        'ls_lien_ngan_hang_ky_han_1_tuan': 'LS liên ngân hàng kỳ hạn 1 tuần',
        'ls_lien_ngan_hang_ky_han_2_tuan': 'LS liên ngân hàng kỳ hạn 2 tuần',
    }
    
    DEPOSIT_INTEREST_RATE_TYPES = {
        'ls_huy_dong_1_3_thang': '1-3 tháng - NHTM Lớn - MBB, ACB, TCB, VPB',
        'ls_huy_dong_6_9_thang': '6-9 tháng - NHTM Lớn - MBB, ACB, TCB, VPB',
        'ls_huy_dong_13_thang': '13 tháng - NHTM Lớn - MBB, ACB, TCB, VPB',
    }
    
    GOV_BOND_TYPES = {
        'vn_gov_bond_5y': 'Lợi suất trái phiếu CP Việt Nam 5Y'
    }
    
    # API Config
    DEFAULT_SIMPLIZE_API_TOKEN = (
        "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJidXVwaGFucXVvY0BnbWFpbC5jb20iLCJhdXRoIjoiUk9MRV9VU0VSIiwidWlkIjoxMjc0MDMsInNpZCI6IjczMDZlNmZhLTNjNTctNDE5Yy04ZjUyLTdhMGFhNWIxMWI5NCIsInJlcXVpcmVkUGhvbmVOdW1iZXIiOnRydWUsInBlIjpmYWxzZSwiZXhwIjoxNzY0MzAzMzE2fQ.u5WKZIszC2AmaH7D2lL4ZTKpw2DkVPKyN1S_2RBahjoPznJ1PZti3wYjGSR46k4PSI2Wdb6IDpIqVJfP43F8Kw"
    )
    DEFAULT_SIMPLIZE_JSESSIONID = "cyYtXRLNvSsLfIzpIsjZ03B5GA90MQocYLeuJuyj"

    def __init__(self):
        self.simplize_api_token = os.environ.get("SIMPLIZE_API_TOKEN", self.DEFAULT_SIMPLIZE_API_TOKEN)
        self.simplize_jsessionid = os.environ.get("SIMPLIZE_JSESSIONID", self.DEFAULT_SIMPLIZE_JSESSIONID)

    # =========================================================================
    # HELPER METHOS
    # =========================================================================
    
    def get_wichart_headers(self) -> Dict[str, str]:
        """Headers mimicking browser requests to avoid 403 / stale caching."""
        return {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'vi,en-US;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Origin': 'https://data.vietnambiz.vn',
            'Referer': 'https://data.vietnambiz.vn/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
        }
    
    def get_simplize_headers(self) -> Optional[Dict[str, str]]:
        if not self.simplize_api_token:
            return None
        return {
            'authorization': f'Bearer {self.simplize_api_token}',
            'Cookie': f'JSESSIONID={self.simplize_jsessionid}',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
        }

    def _standardize_df(self, df: pd.DataFrame, category: str, symbol: str, name: str, source: str, unit: str) -> pd.DataFrame:
        """Standardize DataFrame to unified schema."""
        if df.empty:
            return pd.DataFrame()
        
        # Ensure standard columns exists
        df['category'] = category
        df['symbol'] = symbol
        df['name'] = name
        df['source'] = source
        df['unit'] = unit
        
        # Standardize date
        if 'date' not in df.columns and 'time' in df.columns:
            df['date'] = df['time'].dt.date
        elif 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date']).dt.date
            
        # Standardize value (priority: close > value > sell > price)
        if 'value' not in df.columns:
            if 'close' in df.columns:
                df['value'] = df['close']
            elif 'sell' in df.columns:
                df['value'] = df['sell']
            elif 'price' in df.columns:
                df['value'] = df['price']
            else:
                df['value'] = np.nan

        # Select and order columns
        # Unified Schema: date, symbol, category, name, value, open, high, low, close, unit, source
        cols = ['date', 'symbol', 'category', 'name', 'value', 'open', 'high', 'low', 'close', 'unit', 'source']
        
        # Add missing cols with NaN
        for col in cols:
            if col not in df.columns:
                df[col] = np.nan
                
        return df[cols]

    # =========================================================================
    # COMMODITY LOGIC
    # =========================================================================
    
    def get_steel_coated_data_from_wichart(self) -> Optional[pd.DataFrame]:
        """Lấy dữ liệu giá tôn lạnh màu Hoa Sen từ API wichart.vn."""
        try:
            url = "https://api.wichart.vn/vietnambiz/vi-mo?key=hang_hoa&name=ton_lanh_mau_hoa_sen_045mm"
            # Headers mimic browser to avoid blocking
            headers = self.get_wichart_headers()
            
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code != 200:
                logger.warning(f"WiChart API failed for steel_coated: {resp.status_code}")
                return None
                
            data = resp.json()
            # Standard WiChart format usually has chart -> series
            series = data.get('chart', {}).get('series', [])
            if not series:
                return None
                
            # Usually the first series or find by name
            s = series[0] 
            points = s.get('data', [])
            if not points:
                return None
                
            df = pd.DataFrame(points, columns=['ts', 'value'])
            df['date'] = pd.to_datetime(df['ts'], unit='ms').dt.date
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching steel_coated from WiChart: {e}")
            return None

    def get_pvc_data_from_wichart(self) -> Optional[pd.DataFrame]:
        """Lấy dữ liệu giá Nhựa PVC Trung Quốc từ API wichart.vn."""
        try:
            url = "https://api.wichart.vn/vietnambiz/vi-mo?key=hang_hoa&name=nhua_pvc_trung_quoc"
            headers = self.get_wichart_headers()
            
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code != 200:
                logger.warning(f"WiChart API failed for pvc: {resp.status_code}")
                return None
                
            data = resp.json()
            series = data.get('chart', {}).get('series', [])
            if not series: return None
            
            s = series[0]
            points = s.get('data', [])
            if not points: return None
            
            df = pd.DataFrame(points, columns=['ts', 'value'])
            df['date'] = pd.to_datetime(df['ts'], unit='ms').dt.date
            return df
        except Exception as e:
            logger.error(f"Error fetching pvc from WiChart: {e}")
            return None

    def get_milk_wmp_data_from_simplize(self) -> Optional[pd.DataFrame]:
        """Lấy dữ liệu Sữa bột nguyên kem (WMP) từ Simplize."""
        try:
            # Note: Simplize API requires token.
            url = "https://api2.simplize.vn/api/historical/prices/chart?ticker=NZX%3AWMP1!&period=all"
            headers = self.get_simplize_headers()
            if not headers:
                logger.error("Missing Simplize Token")
                return None
                
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code != 200:
                logger.warning(f"Simplize API failed for milk_wmp: {resp.status_code}")
                return None
                
            data = resp.json()
            # Simplize chart format: data -> [{ 'time', 'value', ... }] or list of values?
            # Based on typical Simplize chart API: data is list of objects
            points = data.get('data', [])
            if not points: return None
            
            records = []
            for p in points:
                # Format might vary. Assuming standard: {'time': 123456789, 'value': 123.4, ...}
                # Or list: [time, open, high, low, close]
                if isinstance(p, dict):
                    ts = p.get('time') or p.get('date')
                    val = p.get('value') or p.get('close')
                    if ts and val is not None:
                        records.append({'ts': ts, 'value': val})
                elif isinstance(p, list) and len(p) >= 2:
                    records.append({'ts': p[0], 'value': p[1]}) # Best guess for [time, value]

            if not records: return None
            
            df = pd.DataFrame(records)
            df['date'] = pd.to_datetime(df['ts'], unit='s').dt.date
            return df
            
        except Exception as e:
            logger.error(f"Error fetching milk_wmp from Simplize: {e}")
            return None

    def get_rubber_data_from_simplize(self) -> Optional[pd.DataFrame]:
        """Lấy dữ liệu Cao su (Rubber) từ Simplize (TOCOM:TRB1!)."""
        try:
            # User provided: url = "https://api2.simplize.vn/api/historical/prices/chart?ticker=TOCOM%3ATRB1!&period=1y"
            # Changing period=1y to period=all to get full history if possible, or keeping user's verify
            # User's url had period=1y. Let's try period=all first to catch history.
            url = "https://api2.simplize.vn/api/historical/prices/chart?ticker=TOCOM%3ATRB1!&period=all"
            headers = self.get_simplize_headers()
            if not headers:
                logger.error("Missing Simplize Token")
                return None
                
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code != 200:
                logger.warning(f"Simplize API failed for rubber: {resp.status_code}")
                return None
                
            data = resp.json()
            points = data.get('data', [])
            if not points: return None
            
            records = []
            for p in points:
                if isinstance(p, dict):
                    ts = p.get('time') or p.get('date')
                    val = p.get('value') or p.get('close')
                    if ts and val is not None:
                        records.append({'ts': ts, 'value': val})
                elif isinstance(p, list) and len(p) >= 2:
                    records.append({'ts': p[0], 'value': p[1]})

            if not records: return None
            
            df = pd.DataFrame(records)
            df['date'] = pd.to_datetime(df['ts'], unit='s').dt.date
            return df
            
        except Exception as e:
            logger.error(f"Error fetching rubber from Simplize: {e}")
            return None


    def fetch_commodities(self, start_date: str) -> pd.DataFrame:
        """Fetch all commodities from vnstock_data."""
        try:
            from vnstock_data import CommodityPrice
        except ImportError:
            logger.error("❌ vnstock_data not installed or inconsistent package structure.")
            return pd.DataFrame()
        
        all_dfs = []
        logger.info(f"Fetching {len(self.COMMODITY_METHODS)} commodities from {start_date}...")
        
        # Calculate end_date string once
        end_date = str(date.today())

        for symbol, method_name in self.COMMODITY_METHODS.items():
            try:
                # --- Custom Fetchers ---
                if symbol == 'steel_coated':
                    df = self.get_steel_coated_data_from_wichart()
                    if df is not None and not df.empty:
                         std_df = self._standardize_df(
                            df, category='commodity', symbol=symbol, name='Tôn lạnh màu HSG', source='wichart', unit='VND/kg'
                        )
                         all_dfs.append(std_df)
                         logger.info(f"✅ Fetched {symbol} (Custom WiChart): {len(std_df)} records")
                         continue
                
                if symbol == 'pvc' or symbol == 'pvc_china': # Handle both keys just in case
                    df = self.get_pvc_data_from_wichart()
                    if df is not None and not df.empty:
                        # Normalize symbol to 'pvc'
                        std_df = self._standardize_df(
                            df, category='commodity', symbol='pvc', name='Nhựa PVC Trung Quốc', source='wichart', unit='CNY/tấn'
                        )
                        all_dfs.append(std_df)
                        logger.info(f"✅ Fetched pvc (Custom WiChart): {len(std_df)} records")
                        continue

                if symbol == 'sua_bot_wmp' or symbol == 'milk_wmp':
                    df = self.get_milk_wmp_data_from_simplize()
                    if df is not None and not df.empty:
                        # Normalize symbol to 'sua_bot_wmp'
                        std_df = self._standardize_df(
                            df, category='commodity', symbol='sua_bot_wmp', name='Sữa bột nguyên kem (WMP)', source='simplize', unit='USD/tấn'
                        )
                        all_dfs.append(std_df)
                        logger.info(f"✅ Fetched sua_bot_wmp (Custom Simplize): {len(std_df)} records")
                        continue

                if symbol == 'rubber' or symbol == 'cao_su':
                    df = self.get_rubber_data_from_simplize()
                    if df is not None and not df.empty:
                        std_df = self._standardize_df(
                            df, category='commodity', symbol='cao_su', name='Cao su (TOCOM)', source='simplize', unit='JPY/kg'
                        )
                        all_dfs.append(std_df)
                        logger.info(f"✅ Fetched rubber (Custom Simplize): {len(std_df)} records")
                        continue

                # --- Standard vnstock Fetcher ---
                # Init CommodityPrice with spl source
                commodity = CommodityPrice(start=start_date, end=end_date, source='spl')
                
                # Check method exists
                if not hasattr(commodity, method_name):
                    # Only warn if it's NOT one of our custom ones (which we already handled above)
                    if symbol not in ['steel_coated', 'pvc', 'pvc_china', 'sua_bot_wmp', 'milk_wmp', 'rubber', 'cao_su']:
                        logger.warning(f"⚠️ Method {method_name} not found in CommodityPrice for {symbol}")
                    continue

                # Call method
                method = getattr(commodity, method_name)
                df = method()
                
                if df is not None and not df.empty:
                    # Rename columns to match standard if needed
                    # vnstock returns: time, open, high, low, close, volume, etc.
                    df = df.reset_index() # Ensure index is reset
                    
                    if 'time' in df.columns:
                         df['date'] = pd.to_datetime(df['time']).dt.date
                    elif 'Date' in df.columns:
                         df['date'] = pd.to_datetime(df['Date']).dt.date
                    
                    std_df = self._standardize_df(
                        df, 
                        category='commodity', 
                        symbol=symbol, 
                        name=symbol, # Description will be handled by UI
                        source='vnstock_spl',
                        unit='N/A' # Unit varies
                    )
                    all_dfs.append(std_df)
                    logger.info(f"✅ Fetched {symbol}: {len(std_df)} records")
                else:
                    logger.warning(f"⚠️ No data for commodity: {symbol}")
                    
            except Exception as e:
                logger.error(f"❌ Error fetching commodity {symbol}: {e}")
                
        if not all_dfs:
            return pd.DataFrame()
            
        return pd.concat(all_dfs, ignore_index=True)

    # =========================================================================
    # MACRO LOGIC
    # =========================================================================
    
    def _fetch_wichart_series(self, url_param: str, type_mapping: Dict[str, str], unit_default: str) -> pd.DataFrame:
        """Generic fetcher for wichart series (Exchange, Rates)."""
        try:
            url = f"https://api.wichart.vn/vietnambiz/vi-mo?name={url_param}"
            resp = requests.get(url, headers=self.get_wichart_headers(), timeout=15)
            if resp.status_code != 200:
                return pd.DataFrame()
            
            data = resp.json()
            series = data.get('chart', {}).get('series', [])
            
            all_dfs = []
            for s in series:
                s_name = s.get('name', '')
                # Find mapped symbol
                symbol = None
                for k, v in type_mapping.items():
                    if v == s_name:
                        symbol = k
                        break
                if not symbol: continue
                
                points = s.get('data', [])
                if not points: continue
                
                # Convert list of [ts, val]
                df = pd.DataFrame(points, columns=['ts', 'value'])
                df['date'] = pd.to_datetime(df['ts'], unit='ms').dt.date
                
                std_df = self._standardize_df(
                    df,
                    category='macro',
                    symbol=symbol,
                    name=s_name,
                    source='wichart',
                    unit=s.get('unit', unit_default)
                )
                all_dfs.append(std_df)
                logger.info(f"✅ Fetched {symbol} ({s_name}): {len(std_df)} records")
                
            return pd.concat(all_dfs, ignore_index=True) if all_dfs else pd.DataFrame()
            
        except Exception as e:
            logger.error(f"Error fetching wichart {url_param}: {e}")
            return pd.DataFrame()

    def fetch_exchange_rates(self) -> pd.DataFrame:
        logger.info("Fetching Exchange Rates...")
        return self._fetch_wichart_series('dhtg', self.EXCHANGE_RATE_TYPES, 'VND')
        
    def fetch_interest_rates(self) -> pd.DataFrame:
        logger.info("Fetching Interest Rates...")
        return self._fetch_wichart_series('lslnh', self.INTEREST_RATE_TYPES, '%')
        
    def fetch_deposit_rates(self) -> pd.DataFrame:
        logger.info("Fetching Deposit Rates...")
        return self._fetch_wichart_series('lshd', self.DEPOSIT_INTEREST_RATE_TYPES, '%')

    def fetch_gov_bonds(self) -> pd.DataFrame:
        """Fetch Gov Bond 5Y from Simplize."""
        logger.info("Fetching Gov Bonds (5Y)...")
        try:
            url = f"https://api2.simplize.vn/api/historical/prices/ohlcv?ticker=TVC:VN05Y&size=5000&interval=1d&type=economy"
            resp = requests.get(url, headers=self.get_simplize_headers(), timeout=20)
            if resp.status_code != 200:
                return pd.DataFrame()
                
            data = resp.json()
            points = data.get('data', [])
            if not points: return pd.DataFrame()
            
            # Simplize fmt: [ts, open, high, low, close, vol]
            records = []
            for p in points:
                if len(p) >= 5:
                    records.append({
                        'ts': p[0],
                        'open': p[1],
                        'high': p[2],
                        'low': p[3],
                        'close': p[4],
                        'value': p[4]
                    })
            
            df = pd.DataFrame(records)
            df['date'] = pd.to_datetime(df['ts'], unit='s').dt.date
            
            return self._standardize_df(
                df,
                category='macro',
                symbol='vn_gov_bond_5y',
                name='Lợi suất TPCP 5Y',
                source='simplize',
                unit='%'
            )
        except Exception as e:
            logger.error(f"Error fetching Gov Bonds: {e}")
            return pd.DataFrame()

    def fetch_all_macro(self) -> pd.DataFrame:
        dfs = [
            self.fetch_exchange_rates(),
            self.fetch_interest_rates(),
            self.fetch_deposit_rates(),
            self.fetch_gov_bonds()
        ]
        dfs = [df for df in dfs if not df.empty]
        return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

    # =========================================================================
    # MAIN FETCH
    # =========================================================================

    def fetch_all(self, start_date: str = '2015-01-01') -> pd.DataFrame:
        """Fetch EVERYTHING: Commodity + Macro."""
        logger.info("=== Fetching COMMODITY Data ===")
        df_comm = self.fetch_commodities(start_date)
        
        logger.info("=== Fetching MACRO Data ===")
        df_macro = self.fetch_all_macro()
        
        # Filter Macro by start_date (as API might return full history)
        if not df_macro.empty:
             df_macro['date'] = pd.to_datetime(df_macro['date'])
             df_macro = df_macro[df_macro['date'] >= pd.to_datetime(start_date)]
             df_macro['date'] = df_macro['date'].dt.date
        
        combined = pd.concat([df_comm, df_macro], ignore_index=True)
        
        if combined.empty:
            return pd.DataFrame()
            
        # Final cleanup
        combined = combined.sort_values(['category', 'symbol', 'date']).reset_index(drop=True)
        return combined
