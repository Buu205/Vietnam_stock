"""
Bank Classification Config
===========================
Bank tier classification for Vietnamese banking sector analysis.

Usage:
    from config.sector_analysis.bank_config import BANK_CLASSIFICATION, get_bank_tier

    tier = get_bank_tier('VCB')  # Returns 'SOCB'
    socb_tickers = BANK_CLASSIFICATION['SOCB']
"""

from typing import Dict, List, Optional


# Full bank list by tier (27 banks total)
# SOCBs (3) + Tier-1 (7) + Tier-2 (8) + Tier-3 (9) = 27 banks
ALL_LISTED_BANKS = [
    'BID', 'CTG', 'VCB',  # SOCBs (3)
    'MBB', 'TCB', 'VPB', 'ACB', 'STB', 'SHB', 'HDB',  # Tier-1 (7)
    'VIB', 'LPB', 'TPB', 'MSB', 'SSB', 'OCB', 'NAB', 'EIB',  # Tier-2 (8)
    'ABB', 'BAB', 'VBB', 'VAB', 'NVB', 'BVB', 'KLB', 'PGB', 'SGB',  # Tier-3 (9)
]

# Bank classification by tier
BANK_CLASSIFICATION: Dict[str, List[str]] = {
    # State-Owned Commercial Banks (Ngân hàng TMCP Nhà nước) - 3 banks
    'SOCB': ['BID', 'CTG', 'VCB'],

    # Tier-1 Private Commercial Banks (Ngân hàng TMCP tư nhân lớn) - 7 banks
    'Tier-1': ['MBB', 'TCB', 'VPB', 'ACB', 'STB', 'SHB', 'HDB'],

    # Tier-2 Private Commercial Banks (Ngân hàng TMCP tư nhân vừa) - 8 banks
    'Tier-2': ['VIB', 'LPB', 'TPB', 'MSB', 'SSB', 'OCB', 'NAB', 'EIB'],

    # Tier-3 Private Commercial Banks (Ngân hàng TMCP tư nhân nhỏ) - 9 banks
    'Tier-3': ['ABB', 'BAB', 'VBB', 'VAB', 'NVB', 'BVB', 'KLB', 'PGB', 'SGB'],
}

# All PCBs combined (for aggregation) - Tier-1 + Tier-2 + Tier-3
ALL_PCBS = BANK_CLASSIFICATION['Tier-1'] + BANK_CLASSIFICATION['Tier-2'] + BANK_CLASSIFICATION['Tier-3']

# All banks
ALL_BANKS = BANK_CLASSIFICATION['SOCB'] + ALL_PCBS


def get_bank_tier(ticker: str) -> str:
    """
    Get bank tier classification for a ticker.

    Args:
        ticker: Bank ticker (e.g., 'VCB', 'ACB')

    Returns:
        Tier name: 'SOCB', 'Tier-1', 'Tier-2', 'Tier-3', or 'Unknown'
    """
    ticker = ticker.upper().strip()
    for tier, banks in BANK_CLASSIFICATION.items():
        if ticker in banks:
            return tier
    return 'Unknown'


def get_banks_by_tier(tier: str) -> List[str]:
    """
    Get list of banks in a specific tier.

    Args:
        tier: Tier name ('SOCB', 'Tier-1', 'Tier-2', 'Tier-3')

    Returns:
        List of ticker symbols
    """
    return BANK_CLASSIFICATION.get(tier, [])


def get_all_pcbs() -> List[str]:
    """Get all private commercial bank tickers."""
    return ALL_PCBS


def is_socb(ticker: str) -> bool:
    """Check if ticker is a state-owned commercial bank."""
    return ticker.upper().strip() in BANK_CLASSIFICATION['SOCB']


def is_pcb(ticker: str) -> bool:
    """Check if ticker is a private commercial bank."""
    return ticker.upper().strip() in ALL_PCBS


# Tier display names (Vietnamese)
TIER_NAMES_VI: Dict[str, str] = {
    'SOCB': 'Ngân hàng TMCP Nhà nước',
    'Tier-1': 'NHTMCP Tư nhân Lớn',
    'Tier-2': 'NHTMCP Tư nhân Vừa',
    'Tier-3': 'NHTMCP Tư nhân Nhỏ',
}

# Tier display colors (for UI)
TIER_COLORS: Dict[str, str] = {
    'SOCB': '#06B6D4',    # Cyan
    'Tier-1': '#A78BFA',  # Purple
    'Tier-2': '#F59E0B',  # Amber
    'Tier-3': '#64748B',  # Slate
}
