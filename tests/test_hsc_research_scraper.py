"""
HSC Research Scraper - Extract forecast data from research.hsc.com.vn

Data extracted:
- NPAMI (Net Profit After Minority Interest) forecasts 2024-2027
- EPS, BVPS, P/E, P/B, ROE forecasts
- Analyst ratings (Buy/Hold/Sell)
- Price goals (TP)

Output files:
- DATA/processed/forecast/hsc/hsc_all_forecast.parquet
- DATA/processed/forecast/hsc/hsc_summary.parquet
- DATA/processed/forecast/hsc/hsc_entity_mapping.json

Usage:
    python tests/test_hsc_research_scraper.py

Credentials required:
    HSC_USERNAME and HSC_PASSWORD environment variables
    OR credentials.json in the same directory
"""

import os
import re
import json
import time
from pathlib import Path

import requests
import pandas as pd
from bs4 import BeautifulSoup


class HSCResearchScraper:
    """Scraper for HSC Research portal."""

    BASE_URL = "https://research.hsc.com.vn"
    LOGIN_URL = f"{BASE_URL}/en/user/login"
    COMPANY_LIST_URL = f"{BASE_URL}/en/company"

    def __init__(self, username: str = None, password: str = None):
        self.username = username or os.getenv("HSC_USERNAME")
        self.password = password or os.getenv("HSC_PASSWORD")
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
            "Accept-Language": "vi,en-US;q=0.9,en;q=0.8",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
        })
        self._logged_in = False
        self.entities = {}

    def login(self) -> bool:
        """Authenticate with HSC Research portal."""
        if not self.username or not self.password:
            print("Missing HSC credentials. Set HSC_USERNAME and HSC_PASSWORD env vars.")
            return False

        # Get CSRF token from login page
        response = self.session.get(self.LOGIN_URL)
        if response.status_code != 200:
            print(f"Failed to load login page: {response.status_code}")
            return False

        soup = BeautifulSoup(response.text, "html.parser")
        csrf_input = soup.find("input", {"name": "csrf_login_token"})

        if not csrf_input:
            print("CSRF token not found on login page")
            return False

        csrf_token = csrf_input.get("value")

        # Submit login form
        login_data = {
            "_username": self.username,
            "_password": self.password,
            "csrf_login_token": csrf_token,
            "MYTIMEZONE": "Asia/Ho_Chi_Minh",
        }

        response = self.session.post(self.LOGIN_URL, data=login_data)

        # Check if login successful
        if "login" in response.url.lower() and "credentials" in response.text.lower():
            print("Login failed - invalid credentials")
            return False

        self._logged_in = True
        print("Successfully logged in to HSC Research")
        return True

    def get_entity_list(self) -> dict:
        """Get list of all companies with entity IDs."""
        if not self._logged_in:
            print("Not logged in. Call login() first.")
            return {}

        response = self.session.get(self.COMPANY_LIST_URL)
        soup = BeautifulSoup(response.text, "html.parser")

        # Find all company links
        links = soup.find_all("a", href=re.compile(r"ID_ENTITY=\d+"))

        for link in links:
            href = link.get("href", "")
            title = link.get("title", "") or link.get_text(strip=True)
            match = re.search(r"ID_ENTITY=(\d+)", href)

            if match and title:
                entity_id = match.group(1)
                # Extract ticker from title (last word after " - ")
                ticker_match = re.search(r"-\s*([A-Z0-9]{3,4})\s*$", title)
                if ticker_match:
                    ticker = ticker_match.group(1)
                    company_name = title.rsplit("-", 1)[0].strip()
                    self.entities[entity_id] = {
                        "ticker": ticker,
                        "company_name": company_name,
                        "entity_id": entity_id,
                    }

        print(f"Found {len(self.entities)} companies")
        return self.entities

    def _parse_number(self, s: str) -> float | None:
        """Parse number from string."""
        if not s:
            return None
        s = s.replace(",", "").replace("%", "").strip()
        try:
            return float(s)
        except ValueError:
            return None

    def _extract_tp_rating(self, soup: BeautifulSoup) -> tuple[float | None, str | None]:
        """Extract price goal and rating from page."""
        text = soup.get_text()

        # Extract price goal
        tp = None
        # Look for pattern after "Target" word
        price_div = soup.find(class_=lambda x: x and "price" in x.lower() if x else False)
        if price_div:
            tp_match = re.search(r"(\d{1,3}(?:,\d{3})*)\s*VND", price_div.get_text())
            if tp_match:
                tp = self._parse_number(tp_match.group(1))

        # Extract rating
        rating = None
        for r in ["Buy", "Hold", "Sell", "Outperform", "Underperform", "Neutral"]:
            if r in text:
                rating = r
                break

        return tp, rating

    def scrape_company(self, entity_id: str) -> dict:
        """Scrape forecast data for a single company."""
        if not self._logged_in:
            return {}

        url = f"{self.BASE_URL}/en/company?ID_ENTITY={entity_id}"
        response = self.session.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        tp, rating = self._extract_tp_rating(soup)

        # Find forecast table
        forecasts = []
        tables = soup.find_all("table")

        for table in tables:
            rows = table.find_all("tr")
            if len(rows) < 5:
                continue

            header_row = rows[0]
            headers = [c.get_text(strip=True) for c in header_row.find_all(["th", "td"])]

            if "2025E" in headers or "2026E" in headers:
                for row in rows[1:]:
                    cells = row.find_all(["th", "td"])
                    if len(cells) >= 5:
                        metric = cells[0].get_text(strip=True)
                        forecasts.append({
                            "metric": metric,
                            "2024": self._parse_number(cells[1].get_text(strip=True)),
                            "2025E": self._parse_number(cells[2].get_text(strip=True)),
                            "2026E": self._parse_number(cells[3].get_text(strip=True)),
                            "2027E": self._parse_number(cells[4].get_text(strip=True)),
                        })
                break

        return {
            "tp": tp,
            "rating": rating,
            "forecasts": forecasts,
        }

    def scrape_all(self, output_dir: str = "DATA/processed/forecast/hsc") -> tuple[pd.DataFrame, pd.DataFrame]:
        """Scrape all companies and save to parquet files."""
        if not self._logged_in:
            if not self.login():
                return pd.DataFrame(), pd.DataFrame()

        if not self.entities:
            self.get_entity_list()

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Save entity mapping
        with open(output_path / "hsc_entity_mapping.json", "w", encoding="utf-8") as f:
            json.dump(self.entities, f, indent=2, ensure_ascii=False)

        all_forecasts = []
        all_summary = []

        print(f"Scraping {len(self.entities)} companies...")

        for i, (entity_id, info) in enumerate(self.entities.items()):
            ticker = info["ticker"]

            try:
                data = self.scrape_company(entity_id)

                for forecast in data["forecasts"]:
                    all_forecasts.append({
                        "ticker": ticker,
                        "entity_id": entity_id,
                        **forecast,
                    })

                all_summary.append({
                    "ticker": ticker,
                    "entity_id": entity_id,
                    "company_name": info["company_name"],
                    "tp": data["tp"],
                    "rating": data["rating"],
                    "has_forecast": len(data["forecasts"]) > 0,
                })

                if (i + 1) % 10 == 0:
                    print(f"  {i + 1}/{len(self.entities)} done...")

                time.sleep(0.2)  # Rate limiting

            except Exception as e:
                print(f"  Error on {ticker}: {e}")

        # Create DataFrames
        forecast_df = pd.DataFrame(all_forecasts)
        summary_df = pd.DataFrame(all_summary)

        # Save to parquet
        forecast_df.to_parquet(output_path / "hsc_all_forecast.parquet", index=False)
        summary_df.to_parquet(output_path / "hsc_summary.parquet", index=False)

        print(f"\nSaved:")
        print(f"  - {output_path}/hsc_all_forecast.parquet ({len(forecast_df)} rows)")
        print(f"  - {output_path}/hsc_summary.parquet ({len(summary_df)} rows)")

        return forecast_df, summary_df


def get_npami_table() -> pd.DataFrame:
    """Get NPAMI forecast table from saved data."""
    forecast_path = Path("DATA/processed/forecast/hsc/hsc_all_forecast.parquet")
    summary_path = Path("DATA/processed/forecast/hsc/hsc_summary.parquet")

    if not forecast_path.exists():
        print("Forecast data not found. Run scrape_all() first.")
        return pd.DataFrame()

    forecast = pd.read_parquet(forecast_path)
    summary = pd.read_parquet(summary_path)

    # Filter NPAMI (Reported net profit)
    npami = forecast[
        forecast["metric"].str.contains("Reported net profit|Net profit", case=False, na=False)
    ].copy()

    # Merge with summary
    npami = npami.merge(summary[["ticker", "tp", "rating"]], on="ticker", how="left")

    # Calculate growth rates
    npami["growth_26_vs_25"] = ((npami["2026E"] - npami["2025E"]) / npami["2025E"] * 100).round(1)
    npami["growth_27_vs_26"] = ((npami["2027E"] - npami["2026E"]) / npami["2026E"] * 100).round(1)

    return npami.sort_values("ticker")


def print_npami_table(npami: pd.DataFrame) -> None:
    """Print formatted NPAMI table."""
    print("=" * 100)
    print("HSC FORECAST - NPAMI (Net Profit After Minority Interest) - Unit: Billion VND")
    print("=" * 100)
    print(f'{"Ticker":<8} {"Rating":<6} {"2024":>10} {"2025E":>10} {"2026E":>10} {"2027E":>10} {"G.26/25":>8} {"G.27/26":>8}')
    print("-" * 100)

    for _, row in npami.iterrows():
        rating = str(row["rating"]) if row["rating"] else "-"
        print(
            f'{row["ticker"]:<8} {rating:<6} '
            f'{row["2024"]:>10,.1f} {row["2025E"]:>10,.1f} {row["2026E"]:>10,.1f} {row["2027E"]:>10,.1f} '
            f'{row["growth_26_vs_25"]:>7.1f}% {row["growth_27_vs_26"]:>7.1f}%'
        )

    print("=" * 100)
    print(f"\nTotal: {len(npami)} companies")


# === TESTS ===

def test_login():
    """Test HSC login."""
    scraper = HSCResearchScraper()
    if scraper.username and scraper.password:
        assert scraper.login(), "Login should succeed with valid credentials"
        print("Login test passed")
    else:
        print("Skipping login test - no credentials")


def test_entity_list():
    """Test entity list retrieval."""
    scraper = HSCResearchScraper()
    if not scraper.login():
        print("Skipping entity list test - login failed")
        return

    entities = scraper.get_entity_list()
    assert len(entities) > 0, "Should find at least one entity"
    print(f"Entity list test passed - found {len(entities)} companies")


def test_scrape_company():
    """Test single company scrape."""
    scraper = HSCResearchScraper()
    if not scraper.login():
        print("Skipping scrape test - login failed")
        return

    # Test with VCB (entity ID 1008)
    data = scraper.scrape_company("1008")
    assert len(data["forecasts"]) > 0, "VCB should have forecast data"
    print(f"Scrape test passed - VCB has {len(data['forecasts'])} forecast rows")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "scrape":
        # Full scrape mode
        scraper = HSCResearchScraper()
        forecast_df, summary_df = scraper.scrape_all()

        if not forecast_df.empty:
            npami = get_npami_table()
            print_npami_table(npami)
    else:
        # Test mode
        print("=" * 60)
        print("HSC Research Scraper Tests")
        print("=" * 60)

        print("\n1. Testing login...")
        test_login()

        print("\n2. Testing entity list...")
        test_entity_list()

        print("\n3. Testing company scrape...")
        test_scrape_company()

        print("\n" + "=" * 60)
        print("To run full scrape:")
        print("  python tests/test_hsc_research_scraper.py scrape")
        print("=" * 60)
