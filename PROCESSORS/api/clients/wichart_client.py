"""
WiChart API Client
==================

Client for WiChart API (api.wichart.vn) - Vietnamese macro data.

Data available:
- Exchange rates (USD/VND)
- Interest rates (interbank, deposit)
- Commodities (steel, PVC)
"""

import logging
from typing import Dict, Optional, List
from datetime import datetime

import pandas as pd

from PROCESSORS.api.core.base_client import BaseAPIClient, APIResponse
from PROCESSORS.api.config.api_config import get_api_config, APIConfig

logger = logging.getLogger(__name__)


class WiChartClient(BaseAPIClient):
    """
    WiChart API client for Vietnamese macro data.

    Features:
    - Exchange rates (central, ceiling, floor, bank, free market)
    - Interbank interest rates (overnight, 1w, 2w)
    - Deposit rates (1-3m, 6-9m, 13m)
    - Commodities (steel_coated, PVC)

    Usage:
        client = WiChartClient()
        rates = client.get_exchange_rates()
        interest = client.get_interest_rates()
    """

    # Mapping of data types to WiChart API params
    EXCHANGE_RATE_PARAM = "dhtg"
    INTEREST_RATE_PARAM = "lslnh"
    DEPOSIT_RATE_PARAM = "lshd"

    # Exchange rate type mapping
    EXCHANGE_RATE_TYPES = {
        "ty_gia_usd_trung_tam": "Tỷ giá trung tâm",
        "ty_gia_tran": "Tỷ giá trần",
        "ty_gia_san": "Tỷ giá sàn",
        "ty_gia_usd_nhtm_ban_ra": "Tỷ giá NHTM bán ra",
        "ty_gia_usd_tu_do_ban_ra": "Tỷ giá tự do bán ra",
    }

    # Interest rate type mapping
    INTEREST_RATE_TYPES = {
        "ls_qua_dem_lien_ngan_hang": "LS qua đêm liên ngân hàng",
        "ls_lien_ngan_hang_ky_han_1_tuan": "LS liên NH kỳ hạn 1 tuần",
        "ls_lien_ngan_hang_ky_han_2_tuan": "LS liên NH kỳ hạn 2 tuần",
    }

    # Deposit rate type mapping
    DEPOSIT_RATE_TYPES = {
        "ls_huy_dong_1_3_thang": "LS huy động 1-3 tháng",
        "ls_huy_dong_6_9_thang": "LS huy động 6-9 tháng",
        "ls_huy_dong_13_thang": "LS huy động 13 tháng",
    }

    def __init__(self, config: APIConfig = None):
        """
        Initialize WiChart client.

        Args:
            config: API configuration. Uses global config if not provided.
        """
        self._config = config or get_api_config()
        endpoint_config = self._config.get_endpoint_config("wichart")

        super().__init__(
            name="wichart",
            base_url=endpoint_config.base_url if endpoint_config else "https://api.wichart.vn",
            timeout=endpoint_config.timeout_seconds if endpoint_config else 15,
            max_retries=endpoint_config.max_retries if endpoint_config else 3,
        )

    def get_headers(self) -> Dict[str, str]:
        """Return browser-mimicking headers for WiChart."""
        return {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "https://data.vietnambiz.vn",
            "Referer": "https://data.vietnambiz.vn/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
        }

    def validate_credentials(self) -> bool:
        """WiChart doesn't require credentials."""
        return True

    def _fetch_wichart_series(
        self,
        url_param: str,
        type_mapping: Dict[str, str],
        unit: str,
    ) -> pd.DataFrame:
        """
        Generic fetcher for WiChart time series data.

        Args:
            url_param: API parameter (e.g., "dhtg", "lslnh")
            type_mapping: Dict mapping indicator codes to names
            unit: Unit of measurement

        Returns:
            DataFrame with standardized columns
        """
        endpoint = f"/vietnambiz/vi-mo?name={url_param}"

        try:
            response = self.get(endpoint)

            if not response.success or not response.data:
                logger.warning(f"[wichart] Empty response for {url_param}")
                return pd.DataFrame()

            # Parse response
            chart_data = response.data.get("chart", {})
            series_list = chart_data.get("series", [])

            if not series_list:
                logger.warning(f"[wichart] No series data for {url_param}")
                return pd.DataFrame()

            all_records = []

            for series in series_list:
                series_name = series.get("name", "")
                data_points = series.get("data", [])

                # Find matching indicator code
                indicator_code = None
                for code, name in type_mapping.items():
                    if name in series_name or series_name in name:
                        indicator_code = code
                        break

                if not indicator_code:
                    # Try to create code from name
                    indicator_code = series_name.lower().replace(" ", "_").replace("-", "_")

                for point in data_points:
                    if len(point) >= 2:
                        timestamp_ms = point[0]
                        value = point[1]

                        # Convert timestamp
                        date = datetime.fromtimestamp(timestamp_ms / 1000)

                        all_records.append({
                            "date": date,
                            "symbol": indicator_code,
                            "category": "macro",
                            "name": series_name,
                            "value": value,
                            "unit": unit,
                            "source": "wichart",
                        })

            if not all_records:
                return pd.DataFrame()

            df = pd.DataFrame(all_records)
            df["date"] = pd.to_datetime(df["date"])

            logger.info(f"[wichart] Fetched {len(df)} records for {url_param}")
            return df

        except Exception as e:
            logger.error(f"[wichart] Error fetching {url_param}: {e}")
            return pd.DataFrame()

    def get_exchange_rates(self) -> pd.DataFrame:
        """
        Fetch exchange rates (USD/VND).

        Returns:
            DataFrame with exchange rate data
        """
        return self._fetch_wichart_series(
            url_param=self.EXCHANGE_RATE_PARAM,
            type_mapping=self.EXCHANGE_RATE_TYPES,
            unit="USD/VNĐ",
        )

    def get_interest_rates(self) -> pd.DataFrame:
        """
        Fetch interbank interest rates.

        Returns:
            DataFrame with interest rate data
        """
        return self._fetch_wichart_series(
            url_param=self.INTEREST_RATE_PARAM,
            type_mapping=self.INTEREST_RATE_TYPES,
            unit="%",
        )

    def get_deposit_rates(self) -> pd.DataFrame:
        """
        Fetch bank deposit rates.

        Returns:
            DataFrame with deposit rate data
        """
        return self._fetch_wichart_series(
            url_param=self.DEPOSIT_RATE_PARAM,
            type_mapping=self.DEPOSIT_RATE_TYPES,
            unit="%",
        )

    def get_commodity(self, commodity_name: str) -> pd.DataFrame:
        """
        Fetch commodity data from WiChart.

        Args:
            commodity_name: Commodity name in WiChart (e.g., "thep_cuon_phu_mau", "nhua_pvc")

        Returns:
            DataFrame with commodity data
        """
        endpoint = f"/vietnambiz/vi-mo?key=hang_hoa&name={commodity_name}"

        try:
            response = self.get(endpoint)

            if not response.success or not response.data:
                return pd.DataFrame()

            chart_data = response.data.get("chart", {})
            series_list = chart_data.get("series", [])

            if not series_list:
                return pd.DataFrame()

            all_records = []
            series = series_list[0]  # Usually only one series

            for point in series.get("data", []):
                if len(point) >= 2:
                    timestamp_ms = point[0]
                    value = point[1]
                    date = datetime.fromtimestamp(timestamp_ms / 1000)

                    all_records.append({
                        "date": date,
                        "symbol": commodity_name,
                        "category": "commodity",
                        "name": series.get("name", commodity_name),
                        "value": value,
                        "unit": "VND/kg",
                        "source": "wichart",
                    })

            if not all_records:
                return pd.DataFrame()

            df = pd.DataFrame(all_records)
            df["date"] = pd.to_datetime(df["date"])

            logger.info(f"[wichart] Fetched {len(df)} records for {commodity_name}")
            return df

        except Exception as e:
            logger.error(f"[wichart] Error fetching commodity {commodity_name}: {e}")
            return pd.DataFrame()

    def get_steel_coated(self) -> pd.DataFrame:
        """Fetch steel coated (tôn lạnh màu HSG 0.45mm) prices."""
        return self.get_commodity("ton_lanh_mau_hoa_sen_045mm")

    def get_pvc(self) -> pd.DataFrame:
        """Fetch PVC China prices."""
        return self.get_commodity("nhua_pvc_trung_quoc")

    def get_pork_vn(self) -> pd.DataFrame:
        """Fetch pork prices Vietnam (heo hơi)."""
        return self.get_commodity("heo_hoi")

    def get_oil_wti(self) -> pd.DataFrame:
        """Fetch WTI oil prices (replaces oil_brent from vnstock)."""
        return self.get_commodity("dau_wti")

    def get_gold_vn(self) -> pd.DataFrame:
        """
        Fetch Vietnam gold prices (SJC buy/sell).

        Returns:
            DataFrame with gold buy and sell prices in VND/lượng
        """
        endpoint = "/vietnambiz/vi-mo?key=hang_hoa&name=vang"

        try:
            response = self.get(endpoint)

            if not response.success or not response.data:
                return pd.DataFrame()

            chart_data = response.data.get("chart", {})
            series_list = chart_data.get("series", [])

            if not series_list:
                return pd.DataFrame()

            all_records = []

            for series in series_list:
                series_name = series.get("name", "")
                data_points = series.get("data", [])

                # Map series name to symbol - use sell price for gold_vn
                if "bán ra" in series_name.lower():
                    symbol = "gold_vn"
                    name = "Vàng SJC bán ra"
                elif "mua vào" in series_name.lower():
                    symbol = "gold_vn_buy"
                    name = "Vàng SJC mua vào"
                else:
                    continue

                for point in data_points:
                    if len(point) >= 2:
                        timestamp_ms = point[0]
                        value = point[1]
                        date = datetime.fromtimestamp(timestamp_ms / 1000)

                        all_records.append({
                            "date": date,
                            "symbol": symbol,
                            "category": "commodity",
                            "name": name,
                            "value": value * 1000,  # Convert from nghìn đồng to VND
                            "unit": "VND/lượng",
                            "source": "wichart",
                        })

            if not all_records:
                return pd.DataFrame()

            df = pd.DataFrame(all_records)
            df["date"] = pd.to_datetime(df["date"])

            logger.info(f"[wichart] Fetched {len(df)} records for Gold VN")
            return df

        except Exception as e:
            logger.error(f"[wichart] Error fetching Gold VN: {e}")
            return pd.DataFrame()

    def get_ure_vn(self) -> pd.DataFrame:
        """
        Fetch Vietnam domestic Ure fertilizer prices (DPM & DCM).

        Returns:
            DataFrame with Ure Phú Mỹ (DPM) and Ure Cà Mau (DCM) prices
        """
        endpoint = "/vietnambiz/vi-mo?key=hang_hoa&name=phan_ure"

        try:
            response = self.get(endpoint)

            if not response.success or not response.data:
                return pd.DataFrame()

            chart_data = response.data.get("chart", {})
            series_list = chart_data.get("series", [])

            if not series_list:
                return pd.DataFrame()

            all_records = []

            for series in series_list:
                series_name = series.get("name", "")
                data_points = series.get("data", [])

                # Map series name to symbol
                if "Phú Mỹ" in series_name:
                    symbol = "ure_vn_dpm"
                    name = "Ure Phú Mỹ (DPM)"
                elif "Cà Mau" in series_name:
                    symbol = "ure_vn_dcm"
                    name = "Ure Cà Mau (DCM)"
                else:
                    continue

                for point in data_points:
                    if len(point) >= 2:
                        timestamp_ms = point[0]
                        value = point[1]
                        date = datetime.fromtimestamp(timestamp_ms / 1000)

                        all_records.append({
                            "date": date,
                            "symbol": symbol,
                            "category": "commodity",
                            "name": name,
                            "value": value,
                            "unit": "VND/kg",
                            "source": "wichart",
                        })

            if not all_records:
                return pd.DataFrame()

            df = pd.DataFrame(all_records)
            df["date"] = pd.to_datetime(df["date"])

            logger.info(f"[wichart] Fetched {len(df)} records for Ure VN (DPM + DCM)")
            return df

        except Exception as e:
            logger.error(f"[wichart] Error fetching Ure VN: {e}")
            return pd.DataFrame()

    def get_all_macro(self) -> pd.DataFrame:
        """
        Fetch all macro data (exchange rates + interest rates + deposit rates).

        Returns:
            Combined DataFrame with all macro data
        """
        dfs = []

        # Exchange rates
        df_fx = self.get_exchange_rates()
        if not df_fx.empty:
            dfs.append(df_fx)

        # Interest rates
        df_interest = self.get_interest_rates()
        if not df_interest.empty:
            dfs.append(df_interest)

        # Deposit rates
        df_deposit = self.get_deposit_rates()
        if not df_deposit.empty:
            dfs.append(df_deposit)

        if not dfs:
            return pd.DataFrame()

        return pd.concat(dfs, ignore_index=True)

    def health_check(self) -> bool:
        """Check if WiChart API is healthy."""
        try:
            response = self.get(f"/vietnambiz/vi-mo?name={self.EXCHANGE_RATE_PARAM}")
            return response.success and response.data is not None
        except Exception as e:
            logger.error(f"[wichart] Health check failed: {e}")
            return False
