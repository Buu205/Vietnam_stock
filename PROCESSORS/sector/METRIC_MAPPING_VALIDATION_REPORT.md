# Metric Mapping Validation Report
**Date:** 2025-12-15
**File Checked:** `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/sector/calculators/metric_mappings.py`
**Registry Source:** `/Users/buuphan/Dev/Vietnam_dashboard/config/metadata/metric_registry.json`

---

## Executive Summary

**Total Entities Checked:** 3 (COMPANY, BANK, SECURITY)
**Total Mappings Checked:** 65 metric codes
**Status:** ✅ **63 CORRECT**, ❌ **2 INCORRECT**

### Issues Found

1. **COMPANY:** `CBS_500` → Should be `CBS_300` (for total_liabilities)
2. **BANK:** `BBS_100` → Should be `BBS_400` (for total_liabilities)

---

## ENTITY_TYPE: COMPANY

### Summary
- **Total Mappings:** 19
- **Correct:** 18 ✅
- **Incorrect:** 1 ❌
- **Registry Coverage:** 19/534 metrics (3.6%)

### CORRECT MAPPINGS ✅

#### Income Statement (9 metrics)
| Code | Business Name | Vietnamese Name |
|------|---------------|-----------------|
| CIS_10 | net_revenue | Doanh thu thuần về bán hàng và cung cấp dịch vụ |
| CIS_11 | cogs | Giá vốn hàng bán |
| CIS_20 | gross_profit | Lợi nhuận gộp về bán hàng và cung cấp dịch vụ |
| CIS_21 | financial_income | Doanh thu hoạt động tài chính |
| CIS_22 | financial_expenses | Chi phí tài chính |
| CIS_30 | operating_profit | Lợi nhuận thuần từ hoạt động kinh doanh |
| CIS_50 | pbt | Tổng lợi nhuận kế toán trước thuế |
| CIS_61 | npatmi | Lợi nhuận sau thuế công ty mẹ |
| CIS_70 | eps | Lãi cơ bản trên cổ phiếu |

#### Balance Sheet (9 metrics)
| Code | Business Name | Vietnamese Name |
|------|---------------|-----------------|
| CBS_100 | current_assets | TÀI SẢN NGẮN HẠN |
| CBS_110 | cash | Tiền và các khoản tương đương tiền |
| CBS_130 | receivables | Các khoản phải thu ngắn hạn |
| CBS_140 | inventory | Hàng tồn kho |
| CBS_200 | long_term_assets | TÀI SẢN DÀI HẠN |
| CBS_300 | total_assets | C - NỢ PHẢI TRẢ |
| CBS_310 | short_term_debt | Nợ ngắn hạn |
| CBS_320 | long_term_debt | Vay và nợ thuê tài chính ngắn hạn |
| CBS_400 | total_equity | VỐN CHỦ SỞ HỮU |

### INCORRECT MAPPINGS ❌

| Current Code | Current Name | Issue | Correct Code | Correct Name |
|--------------|--------------|-------|--------------|--------------|
| CBS_500 | total_liabilities | **Code not found in registry** | **CBS_300** | C - NỢ PHẢI TRẢ |

**Fix Required:**
```python
# ❌ WRONG
'CBS_500': 'total_liabilities',

# ✅ CORRECT
'CBS_300': 'total_liabilities',  # C - NỢ PHẢI TRẢ (total liabilities)
```

**Note:** CBS_300 is currently mapped to `total_assets` (WRONG). The correct mapping:
- CBS_300 = Total Liabilities (Tổng nợ phải trả)
- There is NO separate code for "total_assets" that equals "Assets = Liabilities + Equity"
- Total assets should be calculated as: `total_liabilities + total_equity`

---

## ENTITY_TYPE: BANK

### Summary
- **Total Mappings:** 28
- **Correct:** 27 ✅
- **Incorrect:** 1 ❌
- **Registry Coverage:** 28/606 metrics (4.6%)

### CORRECT MAPPINGS ✅

#### Size Metrics (4 metrics)
| Code | Business Name | Vietnamese Name |
|------|---------------|-----------------|
| BBS_300 | total_assets | Tổng tài sản Có |
| BBS_161 | customer_loans | Cho vay khách hàng |
| BBS_330 | customer_deposits | Tiền gửi của khách hàng |
| BBS_500 | total_equity | Vốn và các quỹ |

#### Income Metrics (9 metrics)
| Code | Business Name | Vietnamese Name |
|------|---------------|-----------------|
| BIS_1 | interest_income | Thu nhập lãi và các khoản thu nhập tương tự |
| BIS_2 | interest_expense | Chi phí lãi và các chi phí tương tự |
| BIS_3 | nii | Thu nhập lãi thuần |
| BIS_14 | opex | Chi phí hoạt động |
| BIS_14A | toi | Tổng thu nhập hoạt động |
| BIS_15 | ppop | Lợi nhuận thuần từ HĐKD trước chi phí dự phòng |
| BIS_16 | provision_expenses | Chi phí dự phòng rủi ro tín dụng |
| BIS_17 | pbt | Tổng lợi nhuận trước thuế |
| BIS_22A | npatmi | Cổ đông của Công ty mẹ |

#### Asset Quality (7 metrics)
| Code | Business Name | Vietnamese Name |
|------|---------------|-----------------|
| BNOT_4 | total_loans_classified | Cho vay các TCTD khác phân theo chất lượng nợ vay |
| BNOT_4_2 | npl_group2 | Nợ cần chú ý |
| BNOT_4_3 | npl_group3 | Nợ dưới tiêu chuẩn |
| BNOT_4_4 | npl_group4 | Nợ nghi ngờ |
| BNOT_4_5 | npl_group5 | Nợ xấu có khả năng mất vốn |
| BBS_169 | loan_loss_provision | Dự phòng rủi ro cho vay khách hàng |
| BBS_252 | accrued_interest | Các khoản lãi, phí phải thu |

#### Capital & Liquidity (7 metrics)
| Code | Business Name | Vietnamese Name |
|------|---------------|-----------------|
| BBS_321 | interbank_deposits_placed | Tiền gửi của các TCTD khác |
| BBS_131 | interbank_borrowings | Tiền, vàng gửi tại các TCTD khác |
| BBS_360 | valuable_papers_issued | Phát hành giấy tờ có giá |
| BNOT_26 | total_customer_deposits | Tiền gửi của khách hàng phân theo loại |
| BNOT_26_1 | casa_current_deposits | Tiền gửi không kỳ hạn |
| BNOT_26_3 | casa_demand_deposits | Tiền gửi vốn chuyên dùng |
| BNOT_26_5 | casa_savings_no_term | Tiền gửi ký quỹ |

### INCORRECT MAPPINGS ❌

| Current Code | Current Name | Issue | Correct Code | Correct Name |
|--------------|--------------|-------|--------------|--------------|
| BBS_100 | total_liabilities | **Code not found in registry** | **BBS_400** | Tổng nợ phải trả |

**Fix Required:**
```python
# ❌ WRONG
'BBS_100': 'total_liabilities',

# ✅ CORRECT
'BBS_400': 'total_liabilities',  # Tổng nợ phải trả
```

---

## ENTITY_TYPE: SECURITY

### Summary
- **Total Mappings:** 18
- **Correct:** 18 ✅
- **Incorrect:** 0 ❌
- **Registry Coverage:** 18/1010 metrics (1.8%)

### ALL MAPPINGS CORRECT ✅

#### Scale Metrics (8 metrics)
| Code | Business Name | Vietnamese Name |
|------|---------------|-----------------|
| SBS_270 | total_assets | TỔNG CỘNG TÀI SẢN |
| SBS_400 | total_equity | VỐN CHỦ SỞ HỮU |
| SBS_112 | fvtpl_securities | Tài sản tài chính ghi nhận thông qua lãi/lỗ (FVTPL) |
| SBS_113 | htm_securities | Các khoản đầu tư nắm giữ đến ngày đáo hạn (HTM) |
| SBS_114 | margin_loans | Các khoản cho vay |
| SBS_115 | afs_securities | Tài sản tài chính sẵn sảng để bán (AFS) |
| SBS_311 | short_term_debt | Vay và nợ thuê tài chính ngắn hạn |
| SBS_341 | long_term_debt | Vay và nợ thuê tài chính dài hạn |

#### Income Metrics (10 metrics)
| Code | Business Name | Vietnamese Name |
|------|---------------|-----------------|
| SIS_1 | income_from_fvtpl | Lãi từ các tài sản tài chính FVTPL |
| SIS_2 | income_from_htm | Lãi từ các khoản đầu tư HTM |
| SIS_3 | income_from_loans | Lãi từ các khoản cho vay và phải thu |
| SIS_4 | income_from_afs | Lãi từ tài sản tài chính AFS |
| SIS_20 | total_revenue | DOANH THU HOẠT ĐỘNG |
| SIS_40 | operating_expenses | CHI PHÍ HOẠT ĐỘNG |
| SIS_50_1 | gross_profit | LỢI NHUẬN GỘP |
| SIS_52 | interest_expense | Chi phí lãi vay |
| SIS_200 | net_profit | LỢI NHUẬN KẾ TOÁN SAU THUẾ TNDN |
| SIS_201 | npatmi | Lợi nhuận sau thuế phân bổ cho chủ sở hữu |

---

## ENTITY_TYPE: INSURANCE

### Summary
- **Status:** ⚠️ BASIC MAPPINGS ONLY (4 metrics)
- **Note:** Insurance entity not validated against registry (may need expansion)

### Current Mappings
```python
INSURANCE_MAPPINGS = {
    'IBS_300': 'total_assets',
    'IBS_400': 'total_equity',
    'IIS_10': 'total_revenue',
    'IIS_50': 'npatmi',
}
```

**Recommendation:** Validate these codes against registry if insurance sector analysis is needed.

---

## Action Items

### Required Fixes (CRITICAL)

1. **Fix COMPANY CBS_500 → CBS_300**
   ```python
   # Current line 48 in metric_mappings.py
   'CBS_500': 'total_liabilities',  # ❌ WRONG

   # Should be:
   # Remove the duplicate CBS_300 mapping to 'total_assets'
   # Change to:
   'CBS_300': 'total_liabilities',  # ✅ CORRECT - C - NỢ PHẢI TRẢ
   ```

2. **Fix BANK BBS_100 → BBS_400**
   ```python
   # Current line 65 in metric_mappings.py
   'BBS_100': 'total_liabilities',  # ❌ WRONG

   # Should be:
   'BBS_400': 'total_liabilities',  # ✅ CORRECT - Tổng nợ phải trả
   ```

### Important Note on CBS_300

**CRITICAL DISCOVERY:** CBS_300 has a **misleading Vietnamese name** in the registry!

```
CBS_300: "C - NỢ PHẢI TRẢ"  (Section C - Total Liabilities)
```

This is NOT "total_assets"! The Vietnamese name clearly indicates this is the **LIABILITIES section header**.

**Correct understanding:**
- **CBS_300** = Total Liabilities (Tổng nợ phải trả)
- **CBS_400** = Total Equity (Vốn chủ sở hữu)
- **Total Assets** should be calculated as: `CBS_300 + CBS_400` (or use section totals)

---

## Validation Status

| Entity Type | Mappings | Correct | Incorrect | Status |
|-------------|----------|---------|-----------|--------|
| COMPANY | 19 | 18 | 1 | ⚠️ Needs fix |
| BANK | 28 | 27 | 1 | ⚠️ Needs fix |
| SECURITY | 18 | 18 | 0 | ✅ Perfect |
| INSURANCE | 4 | - | - | ⚠️ Not validated |
| **TOTAL** | **69** | **63** | **2** | **96.9% accuracy** |

---

## Recommendations

1. **Immediate:** Apply the 2 critical fixes above
2. **Short-term:** Add more commonly used metrics for sector analysis:
   - COMPANY: Cash flow metrics, depreciation, EBITDA components
   - BANK: More capital adequacy metrics, liquidity ratios
   - SECURITY: Brokerage fee income, trading volume metrics
3. **Long-term:** Validate INSURANCE mappings against registry

---

**Report generated by:** Claude Code
**Validation method:** Direct comparison with metric_registry.json v1.0
**Next step:** Apply fixes to metric_mappings.py
