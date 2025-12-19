"""
VNStock Client
==============

Wrapper client for vnstock_data library.

Data available:
- OHLCV price data
- Commodity prices
- Market data
"""

import logging
from typing import Dict, Optional, List
from datetime import datetime, date

import pandas as pd

from PROCESSORS.api.core.base_client import BaseAPIClient, APIResponse

logger = logging.getLogger(__name__)


class VNStockClient(BaseAPIClient):
    """
    Wrapper client for vnstock_data library.

    This wraps the vnstock_data library to provide a consistent interface
    with other API clients, including error handling and logging.

    Features:
    - Commodity prices (gold, oil, steel, etc.)
    - Market data

    Usage:
        client = VNStockClient()
        gold = client.get_commodity("gold_vn")
        commodities = client.get_all_commodities()
    """

    # Commodity method mappings (symbol -> vnstock method name)
    # NOTE: Removed oil_brent (replaced by WiChart oil_wti)
    # NOTE: Removed pork_north_vn (replaced by WiChart heo_hoi with fresher data)
    COMMODITY_METHODS = {
        "gold_vn": "gold_vn",
        "gold_global": "gold_global",
        "oil_crude": "oil_crude",
        # "oil_brent": "oil_brent",  # Replaced by WiChart oil_wti
        "gas_natural": "gas_natural",
        "coke": "coke",
        "steel_d10": "steel_d10",
        "steel_hrc": "steel_hrc",
        "iron_ore": "iron_ore",
        "fertilizer_ure": "fertilizer_ure",
        "soybean": "soybean",
        "corn": "corn",
        "sugar": "sugar",
        # "pork_north_vn": "pork_north_vn",  # Replaced by WiChart heo_hoi
        "pork_china": "pork_china",
    }

    # Commodity metadata (symbol -> name, unit)
    COMMODITY_INFO = {
        "gold_vn": ("Vàng Việt Nam", "VND/lượng"),
        "gold_global": ("Vàng thế giới", "USD/oz"),
        "oil_crude": ("Dầu thô WTI", "USD/thùng"),
        "oil_brent": ("Dầu Brent", "USD/thùng"),
        "gas_natural": ("Khí tự nhiên", "USD/MMBtu"),
        "coke": ("Than cốc", "USD/tấn"),
        "steel_d10": ("Thép D10", "VND/kg"),
        "steel_hrc": ("Thép cuộn cán nóng", "USD/tấn"),
        "iron_ore": ("Quặng sắt", "USD/tấn"),
        "fertilizer_ure": ("Phân bón Ure", "USD/tấn"),
        "soybean": ("Đậu nành", "USD/bushel"),
        "corn": ("Ngô", "USD/bushel"),
        "sugar": ("Đường", "USD/lb"),
        "pork_north_vn": ("Heo hơi miền Bắc VN", "VND/kg"),
        "pork_china": ("Heo hơi Trung Quốc", "CNY/kg"),
    }

    def __init__(self, source: str = "spl"):
        """
        Initialize VNStock client.

        Args:
            source: Data source for vnstock_data ("spl" is default)
        """
        self._source = source
        self._commodity_price = None

        # Call parent init (no actual HTTP base URL needed for this wrapper)
        super().__init__(
            name="vnstock",
            base_url="",  # Not used - vnstock_data handles URLs
            timeout=30,
            max_retries=3,
        )

    def get_headers(self) -> Dict[str, str]:
        """Not used for vnstock wrapper."""
        return {}

    def validate_credentials(self) -> bool:
        """VNStock doesn't require credentials."""
        return True

    def _ensure_commodity_price(self, start_date: str, end_date: str):
        """Lazy-load CommodityPrice instance."""
        try:
            from vnstock_data import CommodityPrice
            self._commodity_price = CommodityPrice(start=start_date, end=end_date, source=self._source)
            return True
        except ImportError:
            logger.error("[vnstock] vnstock_data package not installed")
            return False
        except Exception as e:
            logger.error(f"[vnstock] Error initializing CommodityPrice: {e}")
            return False

    def _standardize_commodity_df(self, df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """Standardize commodity DataFrame to unified format."""
        if df is None or df.empty:
            return pd.DataFrame()

        df = df.reset_index()

        # Standardize date column
        if "time" in df.columns:
            df["date"] = pd.to_datetime(df["time"])
        elif "Date" in df.columns:
            df["date"] = pd.to_datetime(df["Date"])
        elif "date" not in df.columns:
            return pd.DataFrame()

        # Standardize value column
        if "close" in df.columns:
            df["value"] = df["close"]
        elif "value" not in df.columns:
            return pd.DataFrame()

        # Add metadata
        info = self.COMMODITY_INFO.get(symbol, (symbol, "N/A"))
        df["symbol"] = symbol
        df["category"] = "commodity"
        df["name"] = info[0]
        df["unit"] = info[1]
        df["source"] = f"vnstock_{self._source}"

        # Select columns
        columns = ["date", "symbol", "category", "name", "value", "unit", "source"]
        for col in ["open", "high", "low", "close"]:
            if col in df.columns:
                columns.append(col)

        return df[[c for c in columns if c in df.columns]]

    def get_commodity(
        self,
        symbol: str,
        start_date: str = "2015-01-01",
        end_date: str = None
    ) -> pd.DataFrame:
        """
        Fetch commodity price data.

        Args:
            symbol: Commodity symbol (e.g., "gold_vn", "oil_crude")
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD). Defaults to today.

        Returns:
            DataFrame with commodity price data
        """
        if end_date is None:
            end_date = date.today().strftime("%Y-%m-%d")

        method_name = self.COMMODITY_METHODS.get(symbol)
        if not method_name:
            logger.error(f"[vnstock] Unknown commodity symbol: {symbol}")
            return pd.DataFrame()

        if not self._ensure_commodity_price(start_date, end_date):
            return pd.DataFrame()

        try:
            if not hasattr(self._commodity_price, method_name):
                logger.error(f"[vnstock] Method {method_name} not found in CommodityPrice")
                return pd.DataFrame()

            method = getattr(self._commodity_price, method_name)
            df = method()

            std_df = self._standardize_commodity_df(df, symbol)

            if not std_df.empty:
                logger.info(f"[vnstock] Fetched {len(std_df)} records for {symbol}")

            return std_df

        except Exception as e:
            logger.error(f"[vnstock] Error fetching {symbol}: {e}")
            return pd.DataFrame()

    def get_all_commodities(
        self,
        start_date: str = "2015-01-01",
        end_date: str = None
    ) -> pd.DataFrame:
        """
        Fetch all available commodities.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            Combined DataFrame with all commodity data
        """
        if end_date is None:
            end_date = date.today().strftime("%Y-%m-%d")

        all_dfs = []
        logger.info(f"[vnstock] Fetching {len(self.COMMODITY_METHODS)} commodities...")

        for symbol in self.COMMODITY_METHODS.keys():
            try:
                df = self.get_commodity(symbol, start_date, end_date)
                if not df.empty:
                    all_dfs.append(df)
            except Exception as e:
                logger.error(f"[vnstock] Error fetching {symbol}: {e}")
                continue

        if not all_dfs:
            return pd.DataFrame()

        combined = pd.concat(all_dfs, ignore_index=True)
        combined = combined.sort_values(["symbol", "date"]).reset_index(drop=True)

        logger.info(f"[vnstock] Total: {len(combined)} records from {len(all_dfs)} commodities")
        return combined

    def get(self, endpoint: str, params: Dict = None) -> APIResponse:
        """
        Override get method - not used for vnstock wrapper.

        This client wraps vnstock_data library, not HTTP requests.
        """
        return APIResponse(success=False, error_message="Use commodity methods directly")

    def health_check(self) -> bool:
        """Check if vnstock_data is available and working."""
        try:
            from vnstock_data import CommodityPrice

            # Try to initialize with minimal date range
            today = date.today().strftime("%Y-%m-%d")
            yesterday = (date.today().replace(day=1)).strftime("%Y-%m-%d")

            cp = CommodityPrice(start=yesterday, end=today, source=self._source)

            # Check if at least one method exists
            return hasattr(cp, "gold_vn")

        except ImportError:
            logger.error("[vnstock] vnstock_data package not installed")
            return False
        except Exception as e:
            logger.error(f"[vnstock] Health check failed: {e}")
            return False

    def list_available_commodities(self) -> List[str]:
        """List all available commodity symbols."""
        return list(self.COMMODITY_METHODS.keys())

    def get_commodity_info(self, symbol: str) -> Optional[Dict]:
        """
        Get metadata about a commodity.

        Args:
            symbol: Commodity symbol

        Returns:
            Dictionary with name and unit, or None if not found
        """
        info = self.COMMODITY_INFO.get(symbol)
        if info:
            return {"symbol": symbol, "name": info[0], "unit": info[1]}
        return None
