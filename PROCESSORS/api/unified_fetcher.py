"""
Unified Data Fetcher
====================

Unified fetcher using new API clients for commodity and macro data.
Replaces the old macro_commodity_fetcher.py logic with centralized API management.
"""

import logging
from datetime import date
from typing import Optional
from pathlib import Path

import pandas as pd
import numpy as np

from PROCESSORS.api.clients import WiChartClient, SimplizeClient, VNStockClient
from PROCESSORS.api.monitoring import HealthChecker

logger = logging.getLogger(__name__)


class UnifiedDataFetcher:
    """
    Unified fetcher for commodity and macro data.

    Uses the new centralized API clients with proper retry logic,
    error handling, and health monitoring.

    Usage:
        fetcher = UnifiedDataFetcher()
        df_commodity = fetcher.fetch_commodities()
        df_macro = fetcher.fetch_macro()
        df_all = fetcher.fetch_all()
    """

    def __init__(self):
        """Initialize unified fetcher with API clients."""
        self.wichart = WiChartClient()
        self.simplize = SimplizeClient()
        self.vnstock = VNStockClient()

        logger.info("UnifiedDataFetcher initialized with all API clients")

    def _standardize_df(
        self,
        df: pd.DataFrame,
        category: str,
        symbol: str,
        name: str,
        source: str,
        unit: str,
    ) -> pd.DataFrame:
        """Standardize DataFrame to unified schema."""
        if df.empty:
            return pd.DataFrame()

        # Ensure standard columns exist
        df = df.copy()
        df["category"] = category
        df["symbol"] = symbol
        df["name"] = name
        df["source"] = source
        df["unit"] = unit

        # Standardize date - always convert to datetime (not date)
        if "date" not in df.columns and "time" in df.columns:
            df["date"] = pd.to_datetime(df["time"])
        elif "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])

        # Standardize value
        if "value" not in df.columns:
            if "close" in df.columns:
                df["value"] = df["close"]
            elif "sell" in df.columns:
                df["value"] = df["sell"]
            elif "price" in df.columns:
                df["value"] = df["price"]
            else:
                df["value"] = np.nan

        # Select and order columns
        cols = ["date", "symbol", "category", "name", "value", "open", "high", "low", "close", "unit", "source"]

        for col in cols:
            if col not in df.columns:
                df[col] = np.nan

        return df[cols]

    def fetch_commodities(self, start_date: str = "2015-01-01") -> pd.DataFrame:
        """
        Fetch all commodity data from all sources.

        Args:
            start_date: Start date (YYYY-MM-DD)

        Returns:
            Combined DataFrame with all commodity data
        """
        all_dfs = []
        end_date = date.today().strftime("%Y-%m-%d")

        logger.info("=== Fetching COMMODITY Data ===")

        # 1. VNStock commodities (gold, oil, steel, agriculture)
        logger.info("Fetching from VNStock...")
        try:
            df_vnstock = self.vnstock.get_all_commodities(start_date, end_date)
            if not df_vnstock.empty:
                all_dfs.append(df_vnstock)
                logger.info(f"  ✅ VNStock: {len(df_vnstock)} records")
        except Exception as e:
            logger.error(f"  ❌ VNStock error: {e}")

        # 2. WiChart commodities (steel_coated, PVC)
        logger.info("Fetching from WiChart...")
        try:
            # Steel coated
            df_steel = self.wichart.get_steel_coated()
            if not df_steel.empty:
                std_df = self._standardize_df(
                    df_steel, "commodity", "steel_coated", "Tôn lạnh màu HSG", "wichart", "VND/kg"
                )
                all_dfs.append(std_df)
                logger.info(f"  ✅ Steel coated: {len(std_df)} records")

            # PVC
            df_pvc = self.wichart.get_pvc()
            if not df_pvc.empty:
                std_df = self._standardize_df(
                    df_pvc, "commodity", "pvc", "Nhựa PVC Trung Quốc", "wichart", "CNY/tấn"
                )
                all_dfs.append(std_df)
                logger.info(f"  ✅ PVC: {len(std_df)} records")

            # Pork Vietnam (heo hơi)
            df_pork = self.wichart.get_pork_vn()
            if not df_pork.empty:
                std_df = self._standardize_df(
                    df_pork, "commodity", "pork_vn_wichart", "Heo hơi Việt Nam", "wichart", "VND/kg"
                )
                all_dfs.append(std_df)
                logger.info(f"  ✅ Pork VN: {len(std_df)} records")

            # Oil WTI (replaces oil_brent from vnstock)
            df_oil_wti = self.wichart.get_oil_wti()
            if not df_oil_wti.empty:
                std_df = self._standardize_df(
                    df_oil_wti, "commodity", "oil_wti", "Dầu WTI", "wichart", "USD/thùng"
                )
                all_dfs.append(std_df)
                logger.info(f"  ✅ Oil WTI: {len(std_df)} records")
        except Exception as e:
            logger.error(f"  ❌ WiChart error: {e}")

        # 3. Simplize commodities (rubber, WMP milk)
        logger.info("Fetching from Simplize...")
        try:
            df_simplize = self.simplize.get_all_commodities()
            if not df_simplize.empty:
                all_dfs.append(df_simplize)
                logger.info(f"  ✅ Simplize commodities: {len(df_simplize)} records")
        except Exception as e:
            logger.error(f"  ❌ Simplize error: {e}")

        if not all_dfs:
            return pd.DataFrame()

        combined = pd.concat(all_dfs, ignore_index=True)
        combined = combined.sort_values(["symbol", "date"]).reset_index(drop=True)

        logger.info(f"Total commodity records: {len(combined)}")
        return combined

    def fetch_macro(self) -> pd.DataFrame:
        """
        Fetch all macro data (exchange rates, interest rates, bonds).

        Returns:
            Combined DataFrame with all macro data
        """
        all_dfs = []

        logger.info("=== Fetching MACRO Data ===")

        # 1. WiChart macro (exchange rates, interest rates, deposit rates)
        logger.info("Fetching from WiChart...")
        try:
            df_wichart = self.wichart.get_all_macro()
            if not df_wichart.empty:
                all_dfs.append(df_wichart)
                logger.info(f"  ✅ WiChart macro: {len(df_wichart)} records")
        except Exception as e:
            logger.error(f"  ❌ WiChart error: {e}")

        # 2. Simplize macro (government bonds)
        logger.info("Fetching from Simplize...")
        try:
            df_simplize = self.simplize.get_all_macro()
            if not df_simplize.empty:
                all_dfs.append(df_simplize)
                logger.info(f"  ✅ Simplize macro: {len(df_simplize)} records")
        except Exception as e:
            logger.error(f"  ❌ Simplize error: {e}")

        if not all_dfs:
            return pd.DataFrame()

        combined = pd.concat(all_dfs, ignore_index=True)
        combined = combined.sort_values(["symbol", "date"]).reset_index(drop=True)

        logger.info(f"Total macro records: {len(combined)}")
        return combined

    def fetch_all(self, start_date: str = "2015-01-01") -> pd.DataFrame:
        """
        Fetch all data (commodity + macro).

        Args:
            start_date: Start date for commodity data

        Returns:
            Combined DataFrame with all data
        """
        df_commodity = self.fetch_commodities(start_date)
        df_macro = self.fetch_macro()

        # Filter macro by start_date
        if not df_macro.empty:
            df_macro["date"] = pd.to_datetime(df_macro["date"])
            df_macro = df_macro[df_macro["date"] >= pd.to_datetime(start_date)]

        combined = pd.concat([df_commodity, df_macro], ignore_index=True)

        if combined.empty:
            return pd.DataFrame()

        combined = combined.sort_values(["category", "symbol", "date"]).reset_index(drop=True)

        logger.info(f"=== Total combined records: {len(combined)} ===")
        return combined

    def health_check(self) -> dict:
        """
        Run health check on all APIs.

        Returns:
            Dictionary with health status for each API
        """
        checker = HealthChecker()
        return checker.check_all()


def main():
    """CLI entry point for testing the unified fetcher."""
    import argparse

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    parser = argparse.ArgumentParser(description="Unified Data Fetcher")
    parser.add_argument("--type", choices=["commodity", "macro", "all"], default="all",
                       help="Type of data to fetch")
    parser.add_argument("--start", default="2015-01-01", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--output", help="Output parquet file path")
    parser.add_argument("--health", action="store_true", help="Run health check only")
    args = parser.parse_args()

    fetcher = UnifiedDataFetcher()

    if args.health:
        from PROCESSORS.api.monitoring import HealthChecker
        checker = HealthChecker()
        checker.check_all()
        checker.print_report()
        return

    if args.type == "commodity":
        df = fetcher.fetch_commodities(args.start)
    elif args.type == "macro":
        df = fetcher.fetch_macro()
    else:
        df = fetcher.fetch_all(args.start)

    print(f"\nFetched {len(df)} records")

    if not df.empty:
        print("\nSample data:")
        print(df.head(10))
        print("\nSymbols:")
        print(df.groupby("symbol").size().sort_values(ascending=False))

    if args.output and not df.empty:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(output_path, index=False)
        print(f"\nSaved to {output_path}")


if __name__ == "__main__":
    main()
