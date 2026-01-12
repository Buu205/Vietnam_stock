#!/usr/bin/env python3
"""
Test Vietstock Events API
Fetches corporate events (dividends, AGM, etc.) from Vietstock.

API Endpoint: https://finance.vietstock.vn/data/eventstypedata

Event Types:
- eventTypeID=1: Cổ tức (Dividends)
- eventTypeID=2: ĐHCĐ (Annual General Meeting)
- eventTypeID=3: Phát hành (Issuance)
- eventTypeID=4: Niêm yết (Listing)
- eventTypeID=5: Khác (Other)

Note: Cookie and RequestVerificationToken may expire. Update from browser if 403/401.
"""
import requests
import json
from datetime import datetime
from pathlib import Path


def fetch_vietstock_events(
    event_type_id: int = 1,
    from_date: str = None,
    to_date: str = None,
    page: int = 1,
    page_size: int = 50
) -> dict:
    """
    Fetch events from Vietstock API.

    Args:
        event_type_id: 1=Dividends, 2=AGM, 3=Issuance, 4=Listing, 5=Other
        from_date: Start date (YYYY-MM-DD)
        to_date: End date (YYYY-MM-DD)
        page: Page number
        page_size: Results per page (max 50)

    Returns:
        API response as dict
    """
    # Default to current month
    if from_date is None:
        from_date = datetime.now().strftime('%Y-%m-01')
    if to_date is None:
        to_date = datetime.now().strftime('%Y-%m-%d')

    url = "https://finance.vietstock.vn/data/eventstypedata"

    # Note: Token and cookie may need refresh from browser
    payload = (
        f"eventTypeID={event_type_id}&channelID=0&code=&catID=-1"
        f"&fDate={from_date}&tDate={to_date}"
        f"&page={page}&pageSize={page_size}"
        f"&orderBy=Date1&orderDir=DESC"
        f"&__RequestVerificationToken=YjrOqkfTp-7e3bSY_zKaCvJ2xErVx6tf7-uDTqf0xcMmhTBW2nPonZuJ5J-eBz4PnsSg3GPPrQzciXr1hnMs7U0V9g2f4DS_QOWj3Y6A8rs1"
    )

    headers = {
        'Accept': '*/*',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://finance.vietstock.vn',
        'Referer': 'https://finance.vietstock.vn/lich-su-kien.htm?page=1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'Cookie': (
            '_cc_id=c46db549a0ec0e2f953a621a21d1434; language=vi-VN; Theme=Light; '
            'AnonymousNotification=; vst_usr_lg_token=/l4XWStttEmi1tcBi6BxnQ==; '
            'ASP.NET_SessionId=npo31zgvr3rempqidwjocogx; '
            '__RequestVerificationToken=6OP-kfj8zJri5OJuWIsZp9HDIXjnKEofhuGtxzboMz3YgrcrKveajEWK7TtxUb_-wqEFf6R6F87lSIjPm1l4c-47Y9fTwy9-BWXU5AcVQ8Q1'
        )
    }

    response = requests.post(url, headers=headers, data=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def parse_vietstock_date(date_str: str) -> str:
    """Convert /Date(timestamp)/ to YYYY-MM-DD."""
    if not date_str or '/Date(' not in date_str:
        return None
    timestamp = int(date_str.replace('/Date(', '').replace(')/', '')) / 1000
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')


def main():
    """Test the API and print results."""
    print("=" * 60)
    print("VIETSTOCK EVENTS API TEST")
    print("=" * 60)

    # Test: Fetch dividend events for Jan 2025
    data = fetch_vietstock_events(
        event_type_id=1,  # Dividends
        from_date='2025-01-01',
        to_date='2025-01-15'
    )

    # Parse response
    if isinstance(data, list) and len(data) >= 2:
        events = data[0]  # First element is events list
        total_count = data[1]  # Second element is total count

        print(f"\nTotal events: {total_count}")
        print(f"Events returned: {len(events)}")

        print(f"\n{'Code':<8} {'Ex-Date':<12} {'Type':<30} {'Note'}")
        print("-" * 80)

        for event in events[:10]:  # Show first 10
            code = event.get('Code', '')
            ex_date = parse_vietstock_date(event.get('GDKHQDate', ''))
            name = event.get('Name', '')[:28]
            note = event.get('Note', '')[:40]
            print(f"{code:<8} {ex_date:<12} {name:<30} {note}")

        # Save sample to JSON
        output_dir = Path(__file__).parent
        output_file = output_dir / 'vietstock_events_sample.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n✅ Sample saved: {output_file.name}")

    else:
        print("❌ Unexpected response format")
        print(json.dumps(data, indent=2, ensure_ascii=False)[:500])


if __name__ == '__main__':
    main()
