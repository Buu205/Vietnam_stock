"""
Fireant API Client
==================

Client for Fireant API (restv2.fireant.vn) - Vietnamese stock data.

Data available:
- Share outstanding (fundamental data)
- Financial statements
- Company profiles
"""

import logging
from typing import Dict, Optional, List
from datetime import datetime, date

import pandas as pd

from PROCESSORS.api.core.base_client import BaseAPIClient, APIResponse
from PROCESSORS.api.config.api_config import get_api_config, APIConfig

logger = logging.getLogger(__name__)


class FireantClient(BaseAPIClient):
    """
    Fireant API client for Vietnamese stock data.

    Features:
    - Share outstanding data
    - Fundamental data
    - Financial statements

    Usage:
        client = FireantClient()
        shares = client.get_share_outstanding("VNM")
        fundamentals = client.get_fundamentals("VNM")
    """

    def __init__(self, config: APIConfig = None):
        """
        Initialize Fireant client.

        Args:
            config: API configuration. Uses global config if not provided.
        """
        self._config = config or get_api_config()
        endpoint_config = self._config.get_endpoint_config("fireant")
        credentials = self._config.get_credentials("fireant")

        # Get bearer token
        self._bearer_token = credentials.get("bearer_token") if credentials else None

        super().__init__(
            name="fireant",
            base_url=endpoint_config.base_url if endpoint_config else "https://restv2.fireant.vn",
            timeout=endpoint_config.timeout_seconds if endpoint_config else 15,
            max_retries=endpoint_config.max_retries if endpoint_config else 3,
        )

        if not self._bearer_token:
            logger.warning("[fireant] No bearer token configured. API calls will fail.")

    def get_headers(self) -> Dict[str, str]:
        """Return headers with authentication for Fireant."""
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "https://fireant.vn",
            "Referer": "https://fireant.vn/",
        }

        if self._bearer_token:
            headers["Authorization"] = f"Bearer {self._bearer_token}"

        return headers

    def validate_credentials(self) -> bool:
        """Check if bearer token is configured."""
        return self._bearer_token is not None

    def get_share_outstanding(self, ticker: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        Fetch share outstanding data for a ticker.

        Args:
            ticker: Stock symbol (e.g., "VNM", "VCB")
            start_date: Start date string (YYYY-MM-DD). Defaults to 1 year ago.
            end_date: End date string (YYYY-MM-DD). Defaults to today.

        Returns:
            DataFrame with share outstanding data
        """
        ticker = ticker.upper().strip()

        # Default date range
        if not end_date:
            end_date = date.today().strftime("%Y-%m-%d")
        if not start_date:
            from datetime import timedelta
            start = date.today() - timedelta(days=365)
            start_date = start.strftime("%Y-%m-%d")

        endpoint = f"/symbols/{ticker}/fundamental?startDate={start_date}&endDate={end_date}"

        try:
            response = self.get(endpoint)

            if not response.success or not response.data:
                logger.warning(f"[fireant] Empty response for {ticker} share outstanding")
                return pd.DataFrame()

            # Parse response - Fireant returns list of objects
            data = response.data
            if not isinstance(data, list):
                data = [data]

            if not data:
                return pd.DataFrame()

            df = pd.DataFrame(data)

            # Standardize column names
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"])
            elif "reportDate" in df.columns:
                df["date"] = pd.to_datetime(df["reportDate"])

            # Extract share outstanding (look for common column names)
            share_cols = ["sharesOutstanding", "shares_outstanding", "shareOutstanding"]
            for col in share_cols:
                if col in df.columns:
                    df["shares_outstanding"] = df[col]
                    break

            df["ticker"] = ticker
            logger.info(f"[fireant] Fetched {len(df)} records for {ticker}")
            return df

        except Exception as e:
            logger.error(f"[fireant] Error fetching share outstanding for {ticker}: {e}")
            return pd.DataFrame()

    def get_fundamentals(
        self,
        ticker: str,
        start_date: str = None,
        end_date: str = None
    ) -> pd.DataFrame:
        """
        Fetch fundamental data for a ticker.

        Args:
            ticker: Stock symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            DataFrame with fundamental data
        """
        return self.get_share_outstanding(ticker, start_date, end_date)

    def get_fundamentals_batch(
        self,
        tickers: List[str],
        start_date: str = None,
        end_date: str = None
    ) -> pd.DataFrame:
        """
        Fetch fundamental data for multiple tickers.

        Args:
            tickers: List of stock symbols
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            Combined DataFrame with fundamental data for all tickers
        """
        all_dfs = []

        for ticker in tickers:
            try:
                df = self.get_fundamentals(ticker, start_date, end_date)
                if not df.empty:
                    all_dfs.append(df)
            except Exception as e:
                logger.error(f"[fireant] Error fetching {ticker}: {e}")
                continue

        if not all_dfs:
            return pd.DataFrame()

        return pd.concat(all_dfs, ignore_index=True)

    def get_company_profile(self, ticker: str) -> Optional[Dict]:
        """
        Fetch company profile information.

        Args:
            ticker: Stock symbol

        Returns:
            Dictionary with company profile data
        """
        ticker = ticker.upper().strip()
        endpoint = f"/symbols/{ticker}/profile"

        try:
            response = self.get(endpoint)

            if not response.success or not response.data:
                logger.warning(f"[fireant] Empty response for {ticker} profile")
                return None

            return response.data

        except Exception as e:
            logger.error(f"[fireant] Error fetching profile for {ticker}: {e}")
            return None

    def get_financial_statements(
        self,
        ticker: str,
        statement_type: str = "incomestatement",
        period: str = "quarterly"
    ) -> pd.DataFrame:
        """
        Fetch financial statements for a ticker.

        Args:
            ticker: Stock symbol
            statement_type: Type of statement ("incomestatement", "balancesheet", "cashflow")
            period: Period type ("quarterly" or "yearly")

        Returns:
            DataFrame with financial statement data
        """
        ticker = ticker.upper().strip()

        # Map period to Fireant parameter
        period_param = "Q" if period.lower() in ["quarterly", "q"] else "Y"

        endpoint = f"/symbols/{ticker}/financial-reports/{statement_type}?type={period_param}&count=20"

        try:
            response = self.get(endpoint)

            if not response.success or not response.data:
                logger.warning(f"[fireant] Empty response for {ticker} {statement_type}")
                return pd.DataFrame()

            data = response.data
            if not isinstance(data, list):
                return pd.DataFrame()

            df = pd.DataFrame(data)
            df["ticker"] = ticker
            df["statement_type"] = statement_type
            df["period_type"] = period

            logger.info(f"[fireant] Fetched {len(df)} {statement_type} records for {ticker}")
            return df

        except Exception as e:
            logger.error(f"[fireant] Error fetching {statement_type} for {ticker}: {e}")
            return pd.DataFrame()

    def get_income_statement(self, ticker: str, period: str = "quarterly") -> pd.DataFrame:
        """Fetch income statement."""
        return self.get_financial_statements(ticker, "incomestatement", period)

    def get_balance_sheet(self, ticker: str, period: str = "quarterly") -> pd.DataFrame:
        """Fetch balance sheet."""
        return self.get_financial_statements(ticker, "balancesheet", period)

    def get_cash_flow(self, ticker: str, period: str = "quarterly") -> pd.DataFrame:
        """Fetch cash flow statement."""
        return self.get_financial_statements(ticker, "cashflow", period)

    def health_check(self) -> bool:
        """Check if Fireant API is healthy."""
        try:
            # Try fetching VNM profile (common stock)
            response = self.get("/symbols/VNM/profile")
            return response.success and response.data is not None
        except Exception as e:
            logger.error(f"[fireant] Health check failed: {e}")
            return False
