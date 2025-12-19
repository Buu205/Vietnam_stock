"""
Simplize API Client
====================

Client for Simplize API (api2.simplize.vn) - Vietnamese market data.

Data available:
- Government bonds (5Y, 10Y yields)
- Commodities (rubber, WMP milk)
- Historical price charts
"""

import logging
from typing import Dict, Optional, List
from datetime import datetime

import pandas as pd

from PROCESSORS.api.core.base_client import BaseAPIClient, APIResponse
from PROCESSORS.api.config.api_config import get_api_config, APIConfig

logger = logging.getLogger(__name__)


class SimplizeClient(BaseAPIClient):
    """
    Simplize API client for Vietnamese market data.

    Features:
    - Government bond yields (5Y, 10Y)
    - Commodities (rubber/TOCOM, WMP milk/NZX)
    - Historical OHLCV data
    - Chart data

    Usage:
        client = SimplizeClient()
        bonds = client.get_gov_bond_5y()
        rubber = client.get_rubber()
        wmp = client.get_wmp_milk()
    """

    # Government bond tickers
    GOV_BOND_TICKERS = {
        "5y": "TVC:VN05Y",
        "10y": "TVC:VN10Y",
    }

    # Commodity tickers
    COMMODITY_TICKERS = {
        "rubber": "TOCOM:TRB1!",
        "wmp_milk": "NZX:WMP1!",
    }

    def __init__(self, config: APIConfig = None):
        """
        Initialize Simplize client.

        Args:
            config: API configuration. Uses global config if not provided.
        """
        self._config = config or get_api_config()
        endpoint_config = self._config.get_endpoint_config("simplize")
        credentials = self._config.get_credentials("simplize")

        # Get credentials
        self._api_token = credentials.get("api_token") if credentials else None
        self._jsessionid = credentials.get("jsessionid") if credentials else None

        super().__init__(
            name="simplize",
            base_url=endpoint_config.base_url if endpoint_config else "https://api2.simplize.vn",
            timeout=endpoint_config.timeout_seconds if endpoint_config else 20,
            max_retries=endpoint_config.max_retries if endpoint_config else 3,
        )

        if not self._api_token:
            logger.warning("[simplize] No API token configured. Some endpoints may fail.")

    def get_headers(self) -> Dict[str, str]:
        """Return headers with authentication for Simplize."""
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
        }

        if self._api_token:
            headers["Authorization"] = f"Bearer {self._api_token}"

        if self._jsessionid:
            headers["Cookie"] = f"JSESSIONID={self._jsessionid}"

        return headers

    def validate_credentials(self) -> bool:
        """Check if API token is configured."""
        return self._api_token is not None

    def _parse_ohlcv_response(self, data: dict) -> pd.DataFrame:
        """
        Parse OHLCV response from Simplize.

        Simplize format: [timestamp, open, high, low, close, volume]

        Args:
            data: API response data

        Returns:
            DataFrame with OHLCV columns
        """
        points = data.get("data", [])
        if not points:
            return pd.DataFrame()

        records = []
        for p in points:
            if isinstance(p, list) and len(p) >= 5:
                records.append({
                    "date": datetime.fromtimestamp(p[0]),
                    "open": p[1],
                    "high": p[2],
                    "low": p[3],
                    "close": p[4],
                    "volume": p[5] if len(p) > 5 else None,
                    "value": p[4],  # Use close as value
                })

        if not records:
            return pd.DataFrame()

        df = pd.DataFrame(records)
        df["date"] = pd.to_datetime(df["date"])
        return df

    def _parse_chart_response(self, data: dict) -> pd.DataFrame:
        """
        Parse chart response from Simplize.

        Chart format can be dict or list: {'time': ..., 'value': ...} or [time, value]

        Args:
            data: API response data

        Returns:
            DataFrame with date and value columns
        """
        points = data.get("data", [])
        if not points:
            return pd.DataFrame()

        records = []
        for p in points:
            if isinstance(p, dict):
                ts = p.get("time") or p.get("date")
                val = p.get("value") or p.get("close")
                if ts is not None and val is not None:
                    records.append({"timestamp": ts, "value": val})
            elif isinstance(p, list) and len(p) >= 2:
                records.append({"timestamp": p[0], "value": p[1]})

        if not records:
            return pd.DataFrame()

        df = pd.DataFrame(records)
        df["date"] = pd.to_datetime(df["timestamp"], unit="s")
        return df[["date", "value"]]

    def get_gov_bond(self, tenor: str = "5y", size: int = 5000) -> pd.DataFrame:
        """
        Fetch government bond yield data.

        Args:
            tenor: Bond tenor ("5y" or "10y")
            size: Number of data points to fetch

        Returns:
            DataFrame with bond yield data
        """
        ticker = self.GOV_BOND_TICKERS.get(tenor.lower())
        if not ticker:
            logger.error(f"[simplize] Invalid tenor: {tenor}. Valid options: 5y, 10y")
            return pd.DataFrame()

        endpoint = f"/api/historical/prices/ohlcv?ticker={ticker}&size={size}&interval=1d&type=economy"

        try:
            response = self.get(endpoint)

            if not response.success or not response.data:
                logger.warning(f"[simplize] Empty response for gov_bond_{tenor}")
                return pd.DataFrame()

            df = self._parse_ohlcv_response(response.data)

            if df.empty:
                return df

            # Add metadata
            df["symbol"] = f"vn_gov_bond_{tenor}"
            df["category"] = "macro"
            df["name"] = f"Lợi suất TPCP {tenor.upper()}"
            df["unit"] = "%"
            df["source"] = "simplize"

            logger.info(f"[simplize] Fetched {len(df)} records for gov_bond_{tenor}")
            return df

        except Exception as e:
            logger.error(f"[simplize] Error fetching gov_bond_{tenor}: {e}")
            return pd.DataFrame()

    def get_gov_bond_5y(self) -> pd.DataFrame:
        """Fetch 5-year government bond yield."""
        return self.get_gov_bond("5y")

    def get_gov_bond_10y(self) -> pd.DataFrame:
        """Fetch 10-year government bond yield."""
        return self.get_gov_bond("10y")

    def get_commodity_chart(self, commodity: str, period: str = "all") -> pd.DataFrame:
        """
        Fetch commodity price chart data.

        Args:
            commodity: Commodity type ("rubber" or "wmp_milk")
            period: Time period ("1y", "all", etc.)

        Returns:
            DataFrame with commodity price data
        """
        ticker = self.COMMODITY_TICKERS.get(commodity.lower())
        if not ticker:
            logger.error(f"[simplize] Invalid commodity: {commodity}. Valid options: rubber, wmp_milk")
            return pd.DataFrame()

        # URL encode the ticker
        import urllib.parse
        encoded_ticker = urllib.parse.quote(ticker, safe="")
        endpoint = f"/api/historical/prices/chart?ticker={encoded_ticker}&period={period}"

        try:
            response = self.get(endpoint)

            if not response.success or not response.data:
                logger.warning(f"[simplize] Empty response for {commodity}")
                return pd.DataFrame()

            df = self._parse_chart_response(response.data)

            if df.empty:
                return df

            # Add metadata based on commodity
            if commodity.lower() == "rubber":
                df["symbol"] = "cao_su"
                df["name"] = "Cao su (TOCOM)"
                df["unit"] = "JPY/kg"
            elif commodity.lower() == "wmp_milk":
                df["symbol"] = "sua_bot_wmp"
                df["name"] = "Sữa bột nguyên kem (WMP)"
                df["unit"] = "USD/tấn"
            else:
                df["symbol"] = commodity
                df["name"] = commodity
                df["unit"] = "N/A"

            df["category"] = "commodity"
            df["source"] = "simplize"

            logger.info(f"[simplize] Fetched {len(df)} records for {commodity}")
            return df

        except Exception as e:
            logger.error(f"[simplize] Error fetching {commodity}: {e}")
            return pd.DataFrame()

    def get_rubber(self) -> pd.DataFrame:
        """Fetch rubber (TOCOM) prices."""
        return self.get_commodity_chart("rubber")

    def get_wmp_milk(self) -> pd.DataFrame:
        """Fetch WMP milk (NZX) prices."""
        return self.get_commodity_chart("wmp_milk")

    def get_all_commodities(self) -> pd.DataFrame:
        """
        Fetch all commodities from Simplize.

        Returns:
            Combined DataFrame with all commodity data
        """
        dfs = []

        # Rubber
        df_rubber = self.get_rubber()
        if not df_rubber.empty:
            dfs.append(df_rubber)

        # WMP Milk
        df_wmp = self.get_wmp_milk()
        if not df_wmp.empty:
            dfs.append(df_wmp)

        if not dfs:
            return pd.DataFrame()

        return pd.concat(dfs, ignore_index=True)

    def get_all_macro(self) -> pd.DataFrame:
        """
        Fetch all macro data from Simplize (government bonds).

        Returns:
            Combined DataFrame with all macro data
        """
        dfs = []

        # 5Y Bond
        df_5y = self.get_gov_bond_5y()
        if not df_5y.empty:
            dfs.append(df_5y)

        # 10Y Bond
        df_10y = self.get_gov_bond_10y()
        if not df_10y.empty:
            dfs.append(df_10y)

        if not dfs:
            return pd.DataFrame()

        return pd.concat(dfs, ignore_index=True)

    def health_check(self) -> bool:
        """Check if Simplize API is healthy."""
        try:
            # Try fetching 5Y bond with small size
            response = self.get("/api/historical/prices/ohlcv?ticker=TVC:VN05Y&size=10&interval=1d&type=economy")
            return response.success and response.data is not None
        except Exception as e:
            logger.error(f"[simplize] Health check failed: {e}")
            return False
