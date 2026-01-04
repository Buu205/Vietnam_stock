#!/usr/bin/env python3
"""
Vietcap Auto Login với Playwright
Tự động đăng nhập và lấy Bearer token
"""

import json
import os
import asyncio
from pathlib import Path
from datetime import datetime, timedelta

# Token cache file
TOKEN_FILE = Path(__file__).parent / "vietcap_token.json"
CREDENTIALS_FILE = Path(__file__).parent / "credentials.json"


async def login_and_get_token(username: str, password: str, headless: bool = True) -> dict | None:
    """
    Auto login Vietcap và lấy Bearer token

    Args:
        username: Email đăng nhập
        password: Mật khẩu (plaintext)
        headless: True = chạy ngầm, False = hiện browser

    Returns:
        Dict với token và refresh_token hoặc None nếu thất bại
    """
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("❌ Cần cài playwright: pip install playwright && playwright install chromium")
        return None

    result = None

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context()
        page = await context.new_page()

        # Intercept login response
        async def handle_response(response):
            nonlocal result
            if "authentication/login" in response.url and response.status == 200:
                try:
                    data = await response.json()
                    if data.get("successful") and "data" in data:
                        token_data = data["data"]
                        if "token" in token_data:
                            result = {
                                "token": token_data["token"],
                                "refresh_token": token_data.get("refreshToken"),
                                "exp": token_data.get("exp"),
                            }
                            print("✅ Đã bắt được token!")
                except:
                    pass

        page.on("response", handle_response)

        print("🔄 Đang mở trang...")
        await page.goto("https://trading.vietcap.com.vn/home")
        await asyncio.sleep(2)

        # Click "Đăng nhập" button
        print("🔘 Click Đăng nhập...")
        await page.locator("text=Đăng nhập").first.click()
        await asyncio.sleep(2)

        # Click Email option (cho tài khoản email)
        print("📧 Chọn loại tài khoản Email...")
        await page.locator("text=Email").first.click()
        await asyncio.sleep(1)

        # Fill form
        print("📝 Đang điền thông tin...")
        await page.locator('input[placeholder="Nhập tên đăng nhập"]').fill(username)
        await page.locator('input[placeholder="Nhập mật khẩu"]').fill(password)

        # Submit
        print("🔐 Đang đăng nhập...")
        await page.locator('button:has-text("Đăng nhập")').last.click()

        await asyncio.sleep(5)

        # Fallback: lấy từ cookies
        if not result:
            cookies = await context.cookies()
            for c in cookies:
                if c["name"] == "access_token":
                    result = {"token": c["value"]}
                    print("✅ Lấy token từ cookie!")
                    break

        await browser.close()

    return result


def save_token(token_data: dict, expires_days: int = 7):
    """Lưu token vào file với thời hạn"""
    data = {
        "token": token_data.get("token"),
        "refresh_token": token_data.get("refresh_token"),
        "created_at": datetime.now().isoformat(),
        "expires_at": (datetime.now() + timedelta(days=expires_days)).isoformat()
    }
    TOKEN_FILE.write_text(json.dumps(data, indent=2))
    print(f"💾 Đã lưu token vào: {TOKEN_FILE}")


def load_token() -> str | None:
    """Load token từ cache, trả về None nếu hết hạn"""
    if not TOKEN_FILE.exists():
        return None

    try:
        data = json.loads(TOKEN_FILE.read_text())
        expires_at = datetime.fromisoformat(data["expires_at"])

        if datetime.now() < expires_at:
            return data["token"]
        else:
            print("⚠️ Token đã hết hạn")
            return None
    except:
        return None


def get_token(username: str = None, password: str = None, force_refresh: bool = False) -> str | None:
    """
    Lấy token - dùng cache nếu còn hạn, login mới nếu cần

    Args:
        username: Email (hoặc dùng env VIETCAP_USER)
        password: Password (hoặc dùng env VIETCAP_PASS)
        force_refresh: True = bắt buộc login mới

    Returns:
        Bearer token
    """
    # Thử load từ cache trước
    if not force_refresh:
        cached = load_token()
        if cached:
            print("✅ Dùng token từ cache")
            return cached

    # Lấy credentials từ: args > credentials.json > env
    if not username or not password:
        # Try credentials.json first
        if CREDENTIALS_FILE.exists():
            try:
                creds = json.loads(CREDENTIALS_FILE.read_text())
                username = username or creds.get("username")
                password = password or creds.get("password")
                print("📁 Loaded credentials from credentials.json")
            except:
                pass

        # Fallback to env
        username = username or os.getenv("VIETCAP_USER")
        password = password or os.getenv("VIETCAP_PASS")

    if not username or not password:
        print("❌ Cần credentials trong credentials.json hoặc VIETCAP_USER/VIETCAP_PASS env")
        return None

    # Login mới
    print("🔄 Đang login để lấy token mới...")
    result = asyncio.run(login_and_get_token(username, password, headless=True))

    if result and result.get("token"):
        save_token(result)
        return result["token"]

    return None


# ============ Test ============
if __name__ == "__main__":
    import sys

    # Cách 1: Truyền trực tiếp
    if len(sys.argv) >= 3:
        token = get_token(sys.argv[1], sys.argv[2], force_refresh=True)

    # Cách 2: Dùng .env
    else:
        # Load .env nếu có
        env_file = Path(__file__).parent.parent.parent / ".env"
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                if "=" in line and not line.startswith("#"):
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip().strip('"\'')

        token = get_token(force_refresh="--refresh" in sys.argv)

    if token:
        print(f"\n🎉 Token (truncated): {token[:50]}...")
    else:
        print("\n❌ Không lấy được token")
