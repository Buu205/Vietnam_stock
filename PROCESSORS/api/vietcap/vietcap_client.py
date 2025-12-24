#!/usr/bin/env python3
"""
Vietcap IQ API Client
Fetch coverage universe và forecast data từ Vietcap IQ
"""

import json
import requests
from pathlib import Path
from typing import Optional

# Base paths
BASE_DIR = Path(__file__).parent
TOKEN_FILE = BASE_DIR / "vietcap_token.json"

# API endpoints
BASE_URL = "https://iq.vietcap.com.vn/api/iq-insight-service/v1"
ENDPOINTS = {
    "coverage_universe": f"{BASE_URL}/coverage-universe",
    "top_stock": f"{BASE_URL}/top-stock",
    "stock_highest": f"{BASE_URL}/stock-highest",
}

# Default headers
DEFAULT_HEADERS = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive',
    'DNT': '1',
    'Origin': 'https://trading.vietcap.com.vn',
    'Referer': 'https://trading.vietcap.com.vn/',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"'
}


def load_token() -> Optional[str]:
    """Load token từ cache file"""
    if TOKEN_FILE.exists():
        try:
            with open(TOKEN_FILE) as f:
                return json.load(f).get("token")
        except:
            pass
    return None


def refresh_token() -> Optional[str]:
    """Refresh token bằng auto login"""
    from .vietcap_auth import get_token
    return get_token(force_refresh=True)


def get_headers(token: str) -> dict:
    """Tạo headers với token"""
    headers = DEFAULT_HEADERS.copy()
    headers['Authorization'] = f'Bearer {token}'
    return headers


def fetch_api(endpoint: str, token: str = None, auto_refresh: bool = True) -> Optional[dict]:
    """
    Fetch data từ Vietcap API

    Args:
        endpoint: API endpoint URL
        token: Bearer token (auto load nếu không truyền)
        auto_refresh: Tự động refresh token nếu hết hạn

    Returns:
        Response data hoặc None nếu lỗi
    """
    # Load token nếu chưa có
    if not token:
        token = load_token()

    if not token:
        if auto_refresh:
            print("🔄 Token không có, đang refresh...")
            token = refresh_token()
        if not token:
            print("❌ Không có token!")
            return None

    try:
        response = requests.get(endpoint, headers=get_headers(token), timeout=30)

        if response.status_code == 200:
            data = response.json()
            if data.get("successful"):
                return data
            elif data.get("code") == 100:  # Token expired
                if auto_refresh:
                    print("🔄 Token hết hạn, đang refresh...")
                    token = refresh_token()
                    if token:
                        return fetch_api(endpoint, token, auto_refresh=False)
                print("❌ Token hết hạn!")
                return None
            else:
                print(f"❌ API error: {data.get('msg')}")
                return None
        else:
            print(f"❌ HTTP {response.status_code}")
            return None

    except requests.exceptions.Timeout:
        print("⏰ Timeout!")
    except requests.exceptions.ConnectionError as e:
        print(f"🔌 Connection error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

    return None


def fetch_coverage_universe(token: str = None) -> Optional[list]:
    """
    Fetch coverage universe - danh sách mã và dự báo

    Returns:
        List các ticker với target price, rating, PE, PB, ROE, etc.
    """
    result = fetch_api(ENDPOINTS["coverage_universe"], token)
    if result:
        return result.get("data", [])
    return None


def fetch_top_stock(token: str = None) -> Optional[list]:
    """Fetch top stock data"""
    result = fetch_api(ENDPOINTS["top_stock"], token)
    if result:
        return result.get("data", [])
    return None


def fetch_stock_highest(token: str = None) -> Optional[list]:
    """Fetch stock highest data"""
    result = fetch_api(ENDPOINTS["stock_highest"], token)
    if result:
        return result.get("data", [])
    return None


# ============ CLI ============
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        endpoint = sys.argv[1]
        if endpoint == "coverage":
            data = fetch_coverage_universe()
        elif endpoint == "top":
            data = fetch_top_stock()
        elif endpoint == "highest":
            data = fetch_stock_highest()
        else:
            print(f"Unknown endpoint: {endpoint}")
            sys.exit(1)

        if data:
            print(f"✅ Got {len(data)} items")
            print(json.dumps(data[:2], indent=2, ensure_ascii=False))
    else:
        print("Usage: python vietcap_client.py [coverage|top|highest]")
