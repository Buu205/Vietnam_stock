#!/usr/bin/env python3
"""
HSC Research Scraper Runner

Loads credentials from credentials.json (gitignored) and runs the scraper.
After scraping, updates hcm.json with the new forecast data.

Usage:
    python PROCESSORS/forecast/hsc/run_hsc_scraper.py

Schedule monthly with cron:
    0 8 1 * * cd /Users/buuphan/Dev/Vietnam_dashboard && python3 PROCESSORS/forecast/hsc/run_hsc_scraper.py
"""

import json
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.registries import SectorRegistry
from tests.test_hsc_research_scraper import HSCResearchScraper, get_npami_table, print_npami_table


def load_credentials() -> tuple[str, str]:
    """Load credentials from JSON file."""
    cred_file = Path(__file__).parent / "credentials.json"

    if not cred_file.exists():
        print(f"ERROR: Credentials file not found: {cred_file}")
        print("Create it with:")
        print('  {"username": "your_email", "password": "your_password"}')
        sys.exit(1)

    with open(cred_file) as f:
        creds = json.load(f)

    return creds["username"], creds["password"]


def update_hcm_json():
    """
    Update hcm.json with data from HSC parquet files.

    Reads:
    - DATA/processed/forecast/hsc/hsc_all_forecast.parquet
    - DATA/processed/forecast/hsc/hsc_summary.parquet

    Writes:
    - DATA/processed/forecast/sources/hcm.json
    """
    forecast_path = PROJECT_ROOT / "DATA/processed/forecast/hsc/hsc_all_forecast.parquet"
    summary_path = PROJECT_ROOT / "DATA/processed/forecast/hsc/hsc_summary.parquet"
    output_path = PROJECT_ROOT / "DATA/processed/forecast/sources/hcm.json"

    if not forecast_path.exists() or not summary_path.exists():
        print("ERROR: HSC parquet files not found. Run scraper first.")
        return False

    # Load data
    forecast_df = pd.read_parquet(forecast_path)
    summary_df = pd.read_parquet(summary_path)

    # Get sector registry for sector/entity_type lookup
    try:
        sector_reg = SectorRegistry()
    except Exception:
        sector_reg = None

    # Pivot forecast data to get metrics by ticker
    # Extract NPAMI (Reported net profit)
    npami_df = forecast_df[
        forecast_df["metric"].str.contains("Reported net profit|Net profit", case=False, na=False)
    ].copy()
    npami_df = npami_df[["ticker", "2025E", "2026E", "2027E"]].rename(columns={
        "2025E": "npatmi_2025f",
        "2026E": "npatmi_2026f",
        "2027E": "npatmi_2027f",
    })

    # Extract EPS
    eps_df = forecast_df[forecast_df["metric"] == "EPS"].copy()
    eps_df = eps_df[["ticker", "2025E", "2026E", "2027E"]].rename(columns={
        "2025E": "eps_2025f",
        "2026E": "eps_2026f",
        "2027E": "eps_2027f",
    })

    # Extract P/E
    pe_df = forecast_df[forecast_df["metric"] == "P/E (x)"].copy()
    pe_df = pe_df[["ticker", "2025E", "2026E", "2027E"]].rename(columns={
        "2025E": "pe_2025f",
        "2026E": "pe_2026f",
        "2027E": "pe_2027f",
    })

    # Merge all data
    merged_df = summary_df[["ticker", "company_name", "tp", "rating"]].merge(
        npami_df, on="ticker", how="left"
    ).merge(
        eps_df, on="ticker", how="left"
    ).merge(
        pe_df, on="ticker", how="left"
    )

    # Build stocks list
    stocks = []
    for _, row in merged_df.iterrows():
        ticker = row["ticker"]

        # Get sector and entity_type from registry
        sector = ""
        entity_type = "COMPANY"
        if sector_reg:
            try:
                info = sector_reg.get_ticker(ticker)
                if info:
                    sector = info.get("sector", "")
                    entity_type = info.get("entity_type", "COMPANY")
            except Exception:
                pass

        stock = {
            "symbol": ticker,
            "sector": sector,
            "entity_type": entity_type,
            "target_price": row["tp"] if pd.notna(row["tp"]) else None,
            "current_price": None,
            "rating": row["rating"] if pd.notna(row["rating"]) else None,
            "npatmi_2025f": round(row["npatmi_2025f"], 2) if pd.notna(row.get("npatmi_2025f")) else 0.0,
            "npatmi_2026f": round(row["npatmi_2026f"], 2) if pd.notna(row.get("npatmi_2026f")) else 0.0,
            "npatmi_2027f": round(row["npatmi_2027f"], 2) if pd.notna(row.get("npatmi_2027f")) else 0.0,
            "eps_2025f": round(row["eps_2025f"], 2) if pd.notna(row.get("eps_2025f")) else None,
            "eps_2026f": round(row["eps_2026f"], 2) if pd.notna(row.get("eps_2026f")) else None,
            "eps_2027f": round(row["eps_2027f"], 2) if pd.notna(row.get("eps_2027f")) else None,
            "pe_2025f": round(row["pe_2025f"], 2) if pd.notna(row.get("pe_2025f")) else None,
            "pe_2026f": round(row["pe_2026f"], 2) if pd.notna(row.get("pe_2026f")) else None,
            "pe_2027f": round(row["pe_2027f"], 2) if pd.notna(row.get("pe_2027f")) else None,
            "notes": "",
        }
        stocks.append(stock)

    # Sort by symbol
    stocks.sort(key=lambda x: x["symbol"])

    # Build output JSON
    output = {
        "source": "hcm",
        "updated_at": datetime.now().strftime("%d/%m/%y"),
        "schema_version": "2025-2027",
        "stocks": stocks,
    }

    # Write to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Updated {output_path}")
    print(f"  - {len(stocks)} stocks")
    print(f"  - Updated at: {output['updated_at']}")

    return True


def main():
    """Run HSC scraper with credentials from file."""
    print("=" * 60)
    print("HSC Research Scraper")
    print("=" * 60)

    # Load credentials
    username, password = load_credentials()
    print(f"Loaded credentials for: {username}")

    # Initialize scraper
    scraper = HSCResearchScraper(username=username, password=password)

    # Run full scrape
    forecast_df, summary_df = scraper.scrape_all()

    if forecast_df.empty:
        print("ERROR: No data scraped")
        sys.exit(1)

    # Print NPAMI table
    print("\n")
    npami = get_npami_table()
    print_npami_table(npami)

    # Update hcm.json
    print("\n" + "=" * 60)
    print("Updating hcm.json...")
    print("=" * 60)
    update_hcm_json()

    print("\n" + "=" * 60)
    print("Scrape completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
