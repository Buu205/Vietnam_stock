"""
Metric Code Mappings for Sector Aggregation
===========================================

Centralized mapping of raw metric codes (CIS_XX, BBS_XX, SBS_XX) to business metric names.
Used by FA Aggregator to pivot raw data into analyzable format.

Source: formula_migration_plan.md

Author: Claude Code
Date: 2025-12-15
Version: 2.0.0
"""

# ==============================================================================
# COMPANY METRICS (Entity Type: COMPANY)
# ==============================================================================

COMPANY_INCOME_STATEMENT = {
    # Revenue & Costs
    'CIS_10': 'net_revenue',              # Doanh thu thuần
    'CIS_20': 'gross_profit',             # Lợi nhuận gộp
    'CIS_11': 'cogs',                     # Giá vốn hàng bán

    # Operating Performance
    'CIS_30': 'operating_profit',         # Lợi nhuận từ HĐKD (EBIT) ✅
    'CIS_50': 'pbt',                      # Lợi nhuận trước thuế ✅
    'CIS_21': 'financial_income',         # Thu nhập tài chính
    'CIS_22': 'financial_expenses',       # Chi phí tài chính

    # Final Profit
    'CIS_61': 'npatmi',                   # Lợi nhuận sau thuế công ty mẹ ✅
    'CIS_70': 'eps',                      # Lãi cơ bản trên cổ phiếu
}

COMPANY_BALANCE_SHEET = {
    # Assets
    'CBS_270': 'total_assets',            # TỔNG CỘNG TÀI SẢN (270 = 100 + 200) ✅
    'CBS_100': 'current_assets',          # Tài sản ngắn hạn
    'CBS_200': 'long_term_assets',        # Tài sản dài hạn
    'CBS_110': 'cash',                    # Tiền và tương đương tiền
    'CBS_130': 'receivables',             # Các khoản phải thu
    'CBS_140': 'inventory',               # Hàng tồn kho

    # Liabilities & Equity
    'CBS_300': 'total_liabilities',       # C - NỢ PHẢI TRẢ ✅
    'CBS_400': 'total_equity',            # D - VỐN CHỦ SỞ HỮU ✅
    'CBS_310': 'short_term_debt',         # Nợ ngắn hạn
    'CBS_320': 'long_term_debt',          # Nợ dài hạn
}

# Combine all company mappings
COMPANY_MAPPINGS = {**COMPANY_INCOME_STATEMENT, **COMPANY_BALANCE_SHEET}

# ==============================================================================
# BANK METRICS (Entity Type: BANK)
# Source: formula_migration_plan.md:438-504
# ==============================================================================

BANK_SIZE = {
    'BBS_300': 'total_assets',            # Tổng tài sản
    'BBS_161': 'customer_loans',          # Tổng dư nợ cho vay KH
    'BBS_330': 'customer_deposits',       # Tổng tiền gửi KH
    'BBS_500': 'total_equity',            # Vốn chủ sở hữu
    'BBS_400': 'total_liabilities',       # Tổng nợ phải trả ✅ FIXED
}

BANK_INCOME = {
    'BIS_1': 'interest_income',           # Thu nhập lãi
    'BIS_2': 'interest_expense',          # Chi phí lãi
    'BIS_3': 'nii',                       # Thu nhập lãi thuần (NII)
    'BIS_14A': 'toi',                     # Tổng thu nhập hoạt động (TOI)
    'BIS_14': 'opex',                     # Chi phí hoạt động (số âm!)
    'BIS_15': 'ppop',                     # Lợi nhuận trước dự phòng
    'BIS_16': 'provision_expenses',       # Chi phí dự phòng
    'BIS_17': 'pbt',                      # Lợi nhuận trước thuế
    'BIS_22A': 'npatmi',                  # Lợi nhuận sau thuế
}

BANK_ASSET_QUALITY = {
    # NPL Components
    'BNOT_4': 'total_loans_classified',   # Tổng dư nợ (phân loại)
    'BNOT_4_2': 'npl_group2',             # Nợ nhóm 2
    'BNOT_4_3': 'npl_group3',             # Nợ nhóm 3
    'BNOT_4_4': 'npl_group4',             # Nợ nhóm 4
    'BNOT_4_5': 'npl_group5',             # Nợ nhóm 5

    # Provisions
    'BBS_169': 'loan_loss_provision',     # Dự phòng rủi ro tín dụng
    'BBS_252': 'accrued_interest',        # Lãi dự thu
}

BANK_CAPITAL_LIQUIDITY = {
    'BBS_321': 'interbank_deposits_placed',   # Tiền gửi tại NHNN & TCTD khác
    'BBS_131': 'interbank_borrowings',        # Tiền gửi của TCTD khác
    'BBS_360': 'valuable_papers_issued',      # Phát hành giấy tờ có giá

    # CASA Components
    'BNOT_26': 'total_customer_deposits',     # Tổng tiền gửi KH
    'BNOT_26_1': 'casa_current_deposits',     # Tiền gửi không kỳ hạn
    'BNOT_26_3': 'casa_demand_deposits',      # Tiền gửi thanh toán
    'BNOT_26_5': 'casa_savings_no_term',      # Tiền gửi tiết kiệm KKH
}

# Combine all bank mappings
BANK_MAPPINGS = {**BANK_SIZE, **BANK_INCOME, **BANK_ASSET_QUALITY, **BANK_CAPITAL_LIQUIDITY}

# ==============================================================================
# SECURITY METRICS (Entity Type: SECURITY)
# Source: formula_migration_plan.md:509-535
# ==============================================================================

SECURITY_SCALE = {
    'SBS_270': 'total_assets',            # Tổng tài sản
    'SBS_400': 'total_equity',            # Vốn chủ sở hữu
    'SBS_114': 'margin_loans',            # Cho vay margin

    # Investment Portfolio
    'SBS_112': 'fvtpl_securities',        # Chứng khoán FVTPL
    'SBS_113': 'htm_securities',          # Chứng khoán HTM
    'SBS_115': 'afs_securities',          # Chứng khoán AFS

    # Liabilities
    'SBS_311': 'short_term_debt',         # Nợ ngắn hạn
    'SBS_341': 'long_term_debt',          # Nợ dài hạn
}

SECURITY_INCOME = {
    'SIS_20': 'total_revenue',            # Doanh thu
    'SIS_40': 'operating_expenses',       # Chi phí hoạt động
    'SIS_50_1': 'gross_profit',           # Lợi nhuận gộp

    # Income Sources
    'SIS_1': 'income_from_fvtpl',         # Thu nhập từ CK FVTPL
    'SIS_2': 'income_from_htm',           # Thu nhập từ CK HTM
    'SIS_3': 'income_from_loans',         # Thu nhập từ cho vay
    'SIS_4': 'income_from_afs',           # Thu nhập từ CK AFS

    # Interest Costs
    'SIS_52': 'interest_expense',         # Chi phí lãi vay

    # Final Profit
    'SIS_200': 'net_profit',              # Lợi nhuận sau thuế
    'SIS_201': 'npatmi',                  # Lợi nhuận cổ đông mẹ
}

# Combine all security mappings
SECURITY_MAPPINGS = {**SECURITY_SCALE, **SECURITY_INCOME}

# ==============================================================================
# INSURANCE METRICS (Entity Type: INSURANCE)
# ==============================================================================

INSURANCE_MAPPINGS = {
    # Basic metrics (can be expanded later)
    'IBS_300': 'total_assets',
    'IBS_400': 'total_equity',
    'IIS_10': 'total_revenue',
    'IIS_50': 'npatmi',
}

# ==============================================================================
# MASTER MAPPING REGISTRY
# ==============================================================================

ENTITY_MAPPINGS = {
    'COMPANY': COMPANY_MAPPINGS,
    'BANK': BANK_MAPPINGS,
    'SECURITY': SECURITY_MAPPINGS,
    'INSURANCE': INSURANCE_MAPPINGS,
}


def get_mapping_for_entity(entity_type: str) -> dict:
    """
    Get metric code mapping for specific entity type.

    Args:
        entity_type: One of 'COMPANY', 'BANK', 'SECURITY', 'INSURANCE'

    Returns:
        Dictionary mapping metric_code to business_metric_name

    Example:
        >>> mapping = get_mapping_for_entity('COMPANY')
        >>> mapping['CIS_10']
        'net_revenue'
    """
    return ENTITY_MAPPINGS.get(entity_type.upper(), {})


def get_all_metric_codes() -> set:
    """Get set of all metric codes across all entity types."""
    all_codes = set()
    for mapping in ENTITY_MAPPINGS.values():
        all_codes.update(mapping.keys())
    return all_codes


def get_business_name(metric_code: str, entity_type: str = None) -> str:
    """
    Get business metric name for a metric code.

    Args:
        metric_code: Raw metric code (e.g., 'CIS_10')
        entity_type: Entity type to search in (optional)

    Returns:
        Business metric name or original code if not found
    """
    if entity_type:
        mapping = get_mapping_for_entity(entity_type)
        return mapping.get(metric_code, metric_code)

    # Search all entity types
    for mapping in ENTITY_MAPPINGS.values():
        if metric_code in mapping:
            return mapping[metric_code]

    return metric_code  # Return original if not found
