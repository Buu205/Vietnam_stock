# FINANCIAL METRICS CALCULATION FLOW - DESIGN & IMPLEMENTATION PLAN
## Vietnamese Stock Market Dashboard - Complete Metrics Pipeline

---

**Ngày tạo:** 2025-12-11
**Tác giả:** Claude Code (Senior Developer + Senior Finance Analyst)
**Ưu tiên:** CRITICAL - Core calculation engine cho toàn bộ dashboard
**Thời gian ước tính:** 2-3 tuần
**Trạng thái hiện tại:** 70% hoàn thành, cần standardize và fix gaps

---

## EXECUTIVE SUMMARY

Dựa trên phân tích chi tiết các dashboard files (bank_dashboard.py, company_dashboard_pyecharts.py), calculators (company_calculator.py, bank_calculator.py), và formulas (company_formulas.py, bank_formulas.py), tôi đề xuất một **standardized flow** để:

1. **Đảm bảo tất cả metrics cần thiết được tính toán đúng**
2. **Standardize formula layer với docstrings tiếng Việt**
3. **Eliminate duplication và gaps giữa calculation và display**
4. **Create clear data flow từ raw data → calculators → Streamlit**

---

## 1. CURRENT STATE ANALYSIS

### 1.1 Metrics Requirements Analysis

#### Dashboard Requirements (Metrics cần hiển thị)

**BANK DASHBOARD (`bank_dashboard.py`):**

| Metric Group | Metrics Required | Current Status |
|--------------|------------------|----------------|
| **Profitability** | NIM, ROEA, ROAA, NII, TOI, NOII | ✅ Calculated |
| **Efficiency** | CIR (Cost-to-Income Ratio) | ✅ Calculated |
| **Asset Quality** | NPL Ratio, LLCR, Group 2 ratio | ✅ Calculated |
| **Liquidity** | CASA Ratio, LDR (pure & regulated) | ✅ Calculated |
| **Growth** | Revenue growth, NII growth | ⚠️ Partially calculated |
| **Valuation** | P/B Ratio, BVPS | ✅ Calculated |

**COMPANY DASHBOARD (`company_dashboard_pyecharts.py`):**

| Metric Group | Metrics Required | Current Status |
|--------------|------------------|----------------|
| **Profitability** | ROE, ROA, Gross Margin, Net Margin, EBITDA Margin | ✅ Calculated |
| **Revenue** | Net Revenue, Revenue Growth (QoQ, YoY) | ✅ Calculated |
| **Profit** | Gross Profit, EBITDA, NPATMI, Profit Growth | ✅ Calculated |
| **Margins** | Gross, Operating, EBITDA, Net Margins | ✅ Calculated |
| **Balance Sheet** | Total Assets, Equity, Debt-to-Equity | ✅ Calculated |
| **Cash Flow** | Operating CF, FCF | ✅ Calculated |
| **Efficiency** | Asset Turnover, Inventory Turnover | ⚠️ Needs formula |
| **Valuation** | P/E, P/B, EPS | ✅ Calculated |

### 1.2 Current Calculation Flow

```
RAW DATA (parquet files)
    ↓
DATA/raw/fundamental/[entity]/[entity]_full.parquet
    ↓
CALCULATORS (entity-specific)
├── company_calculator.py  →  40+ metrics
├── bank_calculator.py     →  35+ metrics
├── insurance_calculator.py →  30+ metrics
└── security_calculator.py  →  28+ metrics
    ↓
FORMULAS (pure functions)
├── _base_formulas.py      →  24 universal formulas
├── company_formulas.py    →  9 company-specific (có duplicate)
└── bank_formulas.py       →  8 bank-specific
    ↓
OUTPUT (parquet files)
DATA/processed/fundamental/[entity]/[entity]_financial_metrics.parquet
    ↓
STREAMLIT DASHBOARDS
├── bank_dashboard.py      →  Load & display bank metrics
└── company_dashboard_pyecharts.py  →  Load & display company metrics
```

### 1.3 Identified Gaps & Issues

| # | Issue | Severity | Impact | Location |
|---|-------|----------|--------|----------|
| 1 | **Formula duplication** | 🟡 MEDIUM | ROE, ROA, gross_margin có trong cả _base_formulas và company_formulas | formulas/ |
| 2 | **Missing efficiency formulas** | 🟡 MEDIUM | Asset turnover, inventory turnover chưa có trong formulas/ | company_formulas.py |
| 3 | **Growth calculation inconsistency** | 🟡 MEDIUM | QoQ vs YoY growth logic không consistent | calculators/ |
| 4 | **Metric name mismatch** | 🟡 MEDIUM | Dashboard expects `net_revenue_gr` nhưng calculator output `net_revenue_growth` | calculators vs dashboard |
| 5 | **No Vietnamese docstrings** | 🟢 LOW | Tất cả formulas thiếu docstrings tiếng Việt | formulas/ |
| 6 | **Schema validation missing** | 🟡 MEDIUM | Output không được validate against schema | calculators/ |
| 7 | **TTM calculation gaps** | 🟡 MEDIUM | Một số metrics cần TTM nhưng chưa được calculate | calculators/ |

---

## 2. PROPOSED FLOW DESIGN

### 2.1 Standardized 4-Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 1: RAW DATA (Input)                                 │
│  ✅ Parquet files from BSC/vnstock                         │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│  LAYER 2: FORMULAS (Pure Functions)                        │
│  📐 Single source of truth for all calculations            │
│  ✅ Vietnamese docstrings                                  │
│  ✅ Unit tested                                             │
│                                                              │
│  formulas/                                                   │
│  ├── _base_formulas.py        (Universal: ROE, ROA, etc.)  │
│  ├── company_formulas.py      (Company-specific only)      │
│  ├── bank_formulas.py         (Bank-specific: NIM, CIR)    │
│  ├── insurance_formulas.py    (NEW: Insurance-specific)    │
│  ├── security_formulas.py     (NEW: Security-specific)     │
│  └── utils.py                 (Helpers: safe_divide, etc.)│
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│  LAYER 3: CALCULATORS (Orchestration)                      │
│  🔧 Entity-specific metric calculation                     │
│  ✅ Use formulas from Layer 2                              │
│  ✅ Output schema validation                                │
│  ✅ Error handling & logging                                │
│                                                              │
│  calculators/                                                │
│  ├── base_financial_calculator.py  (Template method)       │
│  ├── company_calculator.py         (COMPANY entity)        │
│  ├── bank_calculator.py            (BANK entity)           │
│  ├── insurance_calculator.py       (INSURANCE entity)      │
│  └── security_calculator.py        (SECURITY entity)       │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│  LAYER 4: OUTPUT & DISPLAY                                 │
│  📊 Formatted metrics for Streamlit                        │
│  ✅ Schema-validated parquet files                          │
│  ✅ Ready for dashboard consumption                         │
│                                                              │
│  Output:  DATA/processed/fundamental/[entity]/             │
│  Display: WEBAPP/pages/[dashboard].py                      │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Formula Layer Design (Layer 2) - Thiết kế chi tiết

#### Principle 1: Single Source of Truth

**`_base_formulas.py`** - Universal formulas (dùng cho tất cả entity types)

```python
#!/usr/bin/env python3
"""
Base Financial Formulas - Công thức tài chính cơ bản
===================================================

Các công thức tài chính phổ quát áp dụng cho tất cả loại hình doanh nghiệp.
Tất cả formulas là pure functions, không có side effects.

Tác giả: Claude Code
Ngày cập nhật: 2025-12-11
"""

from typing import Optional
import pandas as pd
from .utils import safe_divide


# ============================================================================
# PROFITABILITY RATIOS - Tỷ suất sinh lời
# ============================================================================

def calculate_roe(net_income: float, total_equity: float) -> Optional[float]:
    """
    Tính ROE (Return on Equity) - Tỷ suất sinh lời trên vốn chủ sở hữu

    ROE = (Lợi nhuận sau thuế / Vốn chủ sở hữu) × 100

    ROE đo lường hiệu quả sử dụng vốn của cổ đông. Cao hơn là tốt hơn.
    Benchmark: >15% (Excellent), >10% (Good), >5% (Average)

    Args:
        net_income: Lợi nhuận sau thuế (VND)
        total_equity: Tổng vốn chủ sở hữu (VND)

    Returns:
        ROE dưới dạng phần trăm, hoặc None nếu không hợp lệ

    Ví dụ:
        >>> calculate_roe(100_000_000_000, 500_000_000_000)
        20.0  # ROE = 20%
    """
    result = safe_divide(net_income, total_equity)
    return round(result * 100, 2) if result is not None else None


def calculate_roa(net_income: float, total_assets: float) -> Optional[float]:
    """
    Tính ROA (Return on Assets) - Tỷ suất sinh lời trên tổng tài sản

    ROA = (Lợi nhuận sau thuế / Tổng tài sản) × 100

    ROA đo lường hiệu quả sử dụng tài sản để tạo ra lợi nhuận.
    Benchmark: >10% (Excellent), >5% (Good), >2% (Average)

    Args:
        net_income: Lợi nhuận sau thuế (VND)
        total_assets: Tổng tài sản (VND)

    Returns:
        ROA dưới dạng phần trăm, hoặc None nếu không hợp lệ

    Ví dụ:
        >>> calculate_roa(100_000_000_000, 1_000_000_000_000)
        10.0  # ROA = 10%
    """
    result = safe_divide(net_income, total_assets)
    return round(result * 100, 2) if result is not None else None


def calculate_gross_margin(revenue: float, cogs: float) -> Optional[float]:
    """
    Tính biên lợi nhuận gộp (Gross Profit Margin)

    Gross Margin = ((Doanh thu - Giá vốn) / Doanh thu) × 100

    Đo lường khả năng kiểm soát giá vốn hàng bán.
    Benchmark: >40% (High margin), >25% (Moderate), >15% (Low)

    Args:
        revenue: Doanh thu thuần (VND)
        cogs: Giá vốn hàng bán (VND)

    Returns:
        Biên lợi nhuận gộp (%), hoặc None nếu không hợp lệ

    Ví dụ:
        >>> calculate_gross_margin(1_000_000_000_000, 600_000_000_000)
        40.0  # Gross Margin = 40%
    """
    gross_profit = revenue - cogs
    result = safe_divide(gross_profit, revenue)
    return round(result * 100, 2) if result is not None else None


# ============================================================================
# EFFICIENCY RATIOS - Tỷ số hiệu quả
# ============================================================================

def calculate_asset_turnover(revenue: float, avg_total_assets: float) -> Optional[float]:
    """
    Tính vòng quay tài sản (Asset Turnover Ratio)

    Asset Turnover = Doanh thu / Tổng tài sản bình quân

    Đo lường hiệu quả sử dụng tài sản để tạo ra doanh thu.
    Cao hơn nghĩa là hiệu quả hơn.

    Args:
        revenue: Doanh thu thuần (VND)
        avg_total_assets: Tổng tài sản bình quân (VND)

    Returns:
        Vòng quay tài sản (lần), hoặc None nếu không hợp lệ

    Ví dụ:
        >>> calculate_asset_turnover(1_200_000_000_000, 800_000_000_000)
        1.5  # Asset Turnover = 1.5 lần
    """
    result = safe_divide(revenue, avg_total_assets)
    return round(result, 2) if result is not None else None


# ... More formulas with Vietnamese docstrings
```

**`bank_formulas.py`** - Bank-specific formulas ONLY

```python
#!/usr/bin/env python3
"""
Bank Financial Formulas - Công thức tài chính ngân hàng
=======================================================

Các công thức đặc thù cho ngân hàng thương mại.
Chỉ chứa formulas KHÔNG CÓ trong _base_formulas.py.

Tác giả: Claude Code
Ngày cập nhật: 2025-12-11
"""

from typing import Optional
from .utils import safe_divide


def calculate_nim(net_interest_income: float, avg_interest_earning_assets: float) -> Optional[float]:
    """
    Tính NIM (Net Interest Margin) - Biên lãi ròng

    NIM = (Thu nhập lãi thuần / Tài sản sinh lãi bình quân) × 100

    NIM là chỉ số quan trọng nhất đo lường hiệu quả hoạt động tín dụng của ngân hàng.
    Benchmark: >4% (Excellent), >3% (Good), >2% (Average)

    Args:
        net_interest_income: Thu nhập lãi thuần (VND) - BIS_3
        avg_interest_earning_assets: Tài sản sinh lãi bình quân (VND) - BBS_120

    Returns:
        NIM dưới dạng phần trăm, hoặc None nếu không hợp lệ

    Ví dụ:
        >>> calculate_nim(10_000_000_000_000, 250_000_000_000_000)
        4.0  # NIM = 4%

    Lưu ý:
        - NIM cao = ngân hàng kiếm lãi tốt
        - NIM thấp = cạnh tranh khốc liệt hoặc hiệu quả kém
    """
    result = safe_divide(net_interest_income, avg_interest_earning_assets)
    return round(result * 100, 2) if result is not None else None


def calculate_cir(operating_expenses: float, total_operating_income: float) -> Optional[float]:
    """
    Tính CIR (Cost-to-Income Ratio) - Tỷ lệ chi phí trên thu nhập

    CIR = (Chi phí hoạt động / Tổng thu nhập hoạt động) × 100

    CIR đo lường hiệu quả quản lý chi phí. Thấp hơn là tốt hơn.
    Benchmark: <40% (Excellent), <50% (Good), <60% (Average)

    Args:
        operating_expenses: Tổng chi phí hoạt động (VND) - BIS_14
        total_operating_income: Tổng thu nhập hoạt động (VND) - BIS_14A (TOI)

    Returns:
        CIR dưới dạng phần trăm, hoặc None nếu không hợp lệ

    Ví dụ:
        >>> calculate_cir(5_000_000_000_000, 12_000_000_000_000)
        41.67  # CIR = 41.67%

    Lưu ý:
        - CIR thấp = ngân hàng quản lý chi phí tốt
        - CIR cao = chi phí hoạt động lớn so với thu nhập
    """
    result = safe_divide(operating_expenses, total_operating_income)
    return round(result * 100, 2) if result is not None else None


def calculate_casa_ratio(
    current_deposits: float,
    savings_deposits: float,
    total_deposits: float
) -> Optional[float]:
    """
    Tính CASA Ratio - Tỷ lệ tiền gửi không kỳ hạn + tiết kiệm

    CASA Ratio = ((Tiền gửi không kỳ hạn + Tiền gửi tiết kiệm) / Tổng tiền gửi) × 100

    CASA ratio cao = nguồn vốn rẻ, lợi nhuận cao hơn.
    Benchmark: >40% (Excellent), >30% (Good), >20% (Average)

    Args:
        current_deposits: Tiền gửi không kỳ hạn (VND) - BNOT_26_1
        savings_deposits: Tiền gửi tiết kiệm (VND) - Derived
        total_deposits: Tổng tiền gửi khách hàng (VND) - BNOT_26

    Returns:
        CASA Ratio dưới dạng phần trăm, hoặc None nếu không hợp lệ

    Ví dụ:
        >>> calculate_casa_ratio(50_000_000_000_000, 30_000_000_000_000, 200_000_000_000_000)
        40.0  # CASA = 40%
    """
    casa_amount = current_deposits + savings_deposits
    result = safe_divide(casa_amount, total_deposits)
    return round(result * 100, 2) if result is not None else None
```

### 2.3 Calculator Layer Design (Layer 3) - Updated

#### Update `company_calculator.py` to use consolidated formulas:

```python
# ❌ CŨ (duplicate)
from PROCESSORS.fundamental.formulas.company_formulas import calculate_roe, calculate_gross_margin

# ✅ MỚI (single source)
from PROCESSORS.fundamental.formulas._base_formulas import (
    calculate_roe,
    calculate_roa,
    calculate_gross_margin,
    calculate_net_margin,
    calculate_asset_turnover
)
from PROCESSORS.fundamental.formulas.company_formulas import (
    calculate_inventory_turnover,  # Company-specific only
    calculate_receivables_turnover  # Company-specific only
)
```

#### Standard Calculation Method Pattern:

```python
def calculate_profitability_ratios(self, df: pd.DataFrame) -> pd.DataFrame:
    """
    Tính các tỷ suất sinh lời cho COMPANY

    Args:
        df: DataFrame với các metrics đã tính

    Returns:
        DataFrame với các tỷ suất sinh lời đã thêm
    """
    try:
        result_df = df.copy()

        # ROE - sử dụng formula từ _base_formulas
        if 'npatmi' in df.columns and 'total_equity' in df.columns:
            result_df['roe'] = df.apply(
                lambda row: calculate_roe(
                    net_income=row['npatmi'] * 1e9,  # Convert từ billions
                    total_equity=row['total_equity'] * 1e9
                ),
                axis=1
            )
        else:
            logger.warning("Missing npatmi or total_equity for ROE calculation")
            result_df['roe'] = np.nan

        # ROA - sử dụng formula từ _base_formulas
        if 'npatmi' in df.columns and 'total_assets' in df.columns:
            result_df['roa'] = df.apply(
                lambda row: calculate_roa(
                    net_income=row['npatmi'] * 1e9,
                    total_assets=row['total_assets'] * 1e9
                ),
                axis=1
            )
        else:
            logger.warning("Missing npatmi or total_assets for ROA calculation")
            result_df['roa'] = np.nan

        return result_df

    except Exception as e:
        logger.error(f"Error calculating profitability ratios: {e}", exc_info=True)
        # Return DataFrame with NaN values rather than failing
        return df
```

---

## 3. IMPLEMENTATION PHASES

### PHASE 1: Formula Consolidation & Documentation (3 ngày)

**Goal:** Single source of truth cho tất cả formulas với Vietnamese docstrings

#### Phase 1.1: Audit & Mapping (1 ngày)

**Task:** Tạo comprehensive mapping của tất cả formulas

**File:** `docs/formula_audit.md`

```markdown
# Formula Audit & Mapping

## Universal Formulas (_base_formulas.py)

| Formula | Used By | Current Location | Action |
|---------|---------|------------------|--------|
| calculate_roe() | COMPANY, BANK, INSURANCE, SECURITY | _base_formulas.py, company_formulas.py (dup) | ✅ Keep in _base, remove from company |
| calculate_roa() | COMPANY, BANK, INSURANCE, SECURITY | _base_formulas.py, company_formulas.py (dup) | ✅ Keep in _base, remove from company |
| calculate_gross_margin() | COMPANY | _base_formulas.py, company_formulas.py (dup) | ✅ Keep in _base, remove from company |

## Company-Specific Formulas (company_formulas.py)

| Formula | Purpose | Status |
|---------|---------|--------|
| calculate_inventory_turnover() | Vòng quay hàng tồn kho | ✅ Keep (company-specific) |
| calculate_receivables_turnover() | Vòng quay khoản phải thu | ✅ Keep (company-specific) |
| calculate_working_capital_turnover() | Vòng quay vốn lưu động | ⚠️ Need to add |

## Bank-Specific Formulas (bank_formulas.py)

| Formula | Purpose | Status |
|---------|---------|--------|
| calculate_nim() | Net Interest Margin | ✅ Complete |
| calculate_cir() | Cost-to-Income Ratio | ✅ Complete |
| calculate_casa_ratio() | CASA Ratio | ✅ Complete |
| calculate_ldr() | Loan-to-Deposit Ratio | ✅ Complete |
| calculate_npl_ratio() | Non-Performing Loan Ratio | ✅ Complete |
```

**Script:** `scripts/audit_formulas.py`

```python
#!/usr/bin/env python3
"""
Script tự động audit tất cả formulas và tạo mapping report
"""

import ast
import inspect
from pathlib import Path
from typing import Dict, List, Tuple

def extract_functions_from_file(file_path: Path) -> List[Tuple[str, int]]:
    """Extract all function names and line numbers from a Python file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read())

    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if node.name.startswith('calculate_'):
                functions.append((node.name, node.lineno))

    return functions

def find_formula_usage(formula_name: str, search_dirs: List[Path]) -> List[Path]:
    """Find all files that import or use a specific formula"""
    # Implementation...
    pass

def generate_audit_report():
    """Generate comprehensive formula audit report"""
    # Implementation...
    pass

if __name__ == "__main__":
    generate_audit_report()
```

#### Phase 1.2: Remove Duplicates (1 ngày)

**Actions:**

1. **Update `company_formulas.py`** - Remove ROE, ROA, gross_margin

```python
# Xóa các functions duplicate
# - calculate_roe() → Moved to _base_formulas.py
# - calculate_roa() → Moved to _base_formulas.py
# - calculate_gross_margin() → Moved to _base_formulas.py

# Chỉ giữ company-specific formulas
def calculate_inventory_turnover(cogs: float, avg_inventory: float) -> Optional[float]:
    """
    Tính vòng quay hàng tồn kho (Inventory Turnover)

    Inventory Turnover = Giá vốn hàng bán / Hàng tồn kho bình quân

    Đo lường tần suất bán hàng tồn kho. Cao hơn nghĩa là hiệu quả hơn.
    Benchmark: Tùy ngành (F&B: >50, Retail: >10, Manufacturing: >5)

    Args:
        cogs: Giá vốn hàng bán (VND) - CIS_11
        avg_inventory: Hàng tồn kho bình quân (VND) - CBS_140

    Returns:
        Vòng quay hàng tồn kho (lần/năm), hoặc None nếu không hợp lệ

    Ví dụ:
        >>> calculate_inventory_turnover(800_000_000_000, 100_000_000_000)
        8.0  # Inventory turnover = 8 lần/năm
    """
    result = safe_divide(cogs, avg_inventory)
    return round(result, 2) if result is not None else None
```

2. **Update all calculator imports**

```bash
# Find all files importing duplicated formulas
grep -r "from.*company_formulas import.*calculate_roe" PROCESSORS/
grep -r "from.*company_formulas import.*calculate_roa" PROCESSORS/

# Update imports using script
python scripts/update_formula_imports.py
```

#### Phase 1.3: Add Vietnamese Docstrings (1 ngày)

**Template for all formulas:**

```python
def calculate_[metric_name]([params]) -> Optional[float]:
    """
    Tính [tên metric bằng tiếng Việt]

    [Công thức]

    [Mô tả ý nghĩa và cách sử dụng]
    Benchmark: [Giá trị tham khảo]

    Args:
        [param]: [Mô tả] ([Đơn vị]) - [Metric code nếu có]

    Returns:
        [Mô tả kết quả], hoặc None nếu không hợp lệ

    Ví dụ:
        >>> calculate_[metric_name]([example params])
        [expected result]  # [Giải thích]

    Lưu ý:
        - [Các lưu ý quan trọng]
        - [Edge cases]
    """
    # Implementation
```

**Action:** Apply template to ALL formulas in:
- `_base_formulas.py` (24 formulas)
- `company_formulas.py` (4 formulas after cleanup)
- `bank_formulas.py` (8 formulas)
- `insurance_formulas.py` (NEW - 7 formulas)
- `security_formulas.py` (NEW - 6 formulas)

---

### PHASE 2: Calculator Updates (4 ngày)

**Goal:** Standardize all calculators to use consolidated formulas

#### Phase 2.1: Update Imports (1 ngày)

**Pattern for all calculators:**

```python
# At top of calculator file
from PROCESSORS.fundamental.formulas._base_formulas import (
    # Profitability
    calculate_roe,
    calculate_roa,
    calculate_roic,
    calculate_gross_margin,
    calculate_operating_margin,
    calculate_net_margin,
    calculate_ebit_margin,
    calculate_ebitda_margin,

    # Efficiency
    calculate_asset_turnover,

    # Leverage
    calculate_debt_to_equity,
    calculate_debt_to_assets,
    calculate_current_ratio,
    calculate_quick_ratio,

    # Valuation
    calculate_eps,
    calculate_book_value_per_share,
    calculate_pe_ratio,
    calculate_pb_ratio
)

# Entity-specific imports
if entity_type == "COMPANY":
    from PROCESSORS.fundamental.formulas.company_formulas import (
        calculate_inventory_turnover,
        calculate_receivables_turnover
    )
elif entity_type == "BANK":
    from PROCESSORS.fundamental.formulas.bank_formulas import (
        calculate_nim,
        calculate_cir,
        calculate_casa_ratio,
        calculate_ldr,
        calculate_npl_ratio
    )
```

#### Phase 2.2: Add Schema Validation (1 ngày)

**Update `base_financial_calculator.py`:**

```python
from config.schema_manager import SchemaManager  # Updated after rename

class BaseFinancialCalculator:
    def __init__(self, data_path: Optional[str] = None):
        # ... existing init
        self.schema_manager = SchemaManager()

    def validate_output_schema(self, df: pd.DataFrame) -> bool:
        """
        Validate output DataFrame against entity-specific schema

        Args:
            df: Calculated results DataFrame

        Returns:
            True nếu validation pass, False nếu có lỗi
        """
        entity_type = self.get_entity_type().lower()

        try:
            # Load expected schema
            schema = self.schema_manager.get_domain_schema(
                'fundamental',
                f'{entity_type}_output'
            )

            required_cols = schema.get('required_columns', [])
            missing = set(required_cols) - set(df.columns)

            if missing:
                logger.error(f"Missing required columns: {missing}")
                return False

            # Validate data types
            for col, expected_type in schema.get('column_types', {}).items():
                if col in df.columns:
                    actual_type = str(df[col].dtype)
                    # Type checking logic...

            logger.info(f"✅ Output schema validation passed for {entity_type}")
            return True

        except Exception as e:
            logger.warning(f"Schema validation skipped: {e}")
            return True  # Don't fail if schema not found

    def calculate_all_metrics(self) -> pd.DataFrame:
        """Main orchestration with schema validation"""
        # ... existing logic

        result = self.postprocess_results(result)

        # Validate before returning
        if not self.validate_output_schema(result):
            logger.warning("Output schema validation failed, but continuing...")

        return result
```

#### Phase 2.3: Standardize Error Handling (1 ngày)

**Pattern for all calculation methods:**

```python
def calculate_profitability_ratios(self, df: pd.DataFrame) -> pd.DataFrame:
    """
    Tính các tỷ suất sinh lời

    Args:
        df: DataFrame với income statement và balance sheet metrics

    Returns:
        DataFrame với profitability ratios đã được thêm vào
    """
    try:
        result_df = df.copy()

        # ROE calculation with validation
        if self._has_required_columns(df, ['npatmi', 'total_equity']):
            result_df['roe'] = df.apply(
                lambda row: calculate_roe(
                    net_income=row['npatmi'] * 1e9,
                    total_equity=row['total_equity'] * 1e9
                ),
                axis=1
            )
            logger.debug(f"Calculated ROE for {len(result_df)} rows")
        else:
            logger.warning("Missing columns for ROE: setting to NaN")
            result_df['roe'] = np.nan

        # More ratios...

        return result_df

    except Exception as e:
        logger.error(f"Error in calculate_profitability_ratios: {e}", exc_info=True)
        # Return original df with NaN columns rather than crashing
        return self._add_nan_columns(df, ['roe', 'roa', 'gross_margin'])
```

#### Phase 2.4: Fix Growth Calculations (1 ngày)

**Standardize growth calculation logic:**

```python
def calculate_growth_rates(self, df: pd.DataFrame) -> pd.DataFrame:
    """
    Tính tỷ lệ tăng trưởng QoQ (Quarter-over-Quarter) và YoY (Year-over-Year)

    Args:
        df: DataFrame với quarterly metrics

    Returns:
        DataFrame với growth rates
    """
    result_df = df.copy()

    # Ensure sorted by ticker and date
    result_df = result_df.sort_values(['symbol', 'report_date'])

    # Metrics to calculate growth for
    growth_metrics = {
        'net_revenue': 'net_revenue_growth',  # QoQ growth
        'npatmi': 'npatmi_growth',            # QoQ growth
        'gross_profit': 'gross_profit_growth' # QoQ growth
    }

    for metric, growth_col in growth_metrics.items():
        if metric in result_df.columns:
            # QoQ growth
            result_df[growth_col] = result_df.groupby('symbol')[metric].pct_change() * 100

            # YoY growth (compare with same quarter last year)
            result_df[f'{growth_col}_yoy'] = result_df.groupby('symbol')[metric].pct_change(periods=4) * 100

    return result_df
```

---

### PHASE 3: Dashboard Integration (2 ngày)

**Goal:** Ensure dashboards can consume calculated metrics correctly

#### Phase 3.1: Metric Name Standardization (1 ngày)

**Create mapping document:**

**File:** `docs/metric_name_mapping.md`

```markdown
# Metric Name Mapping - Calculator Output vs Dashboard Expectations

## Company Metrics

| Calculator Output | Dashboard Expects | Action |
|-------------------|-------------------|--------|
| `net_revenue_growth` | `net_revenue_gr` | ✅ Add alias in postprocess |
| `npatmi_growth` | `npatmi_gr` | ✅ Add alias |
| `gross_profit_growth` | `gross_profit_gr` | ✅ Add alias |

## Bank Metrics

| Calculator Output | Dashboard Expects | Action |
|-------------------|-------------------|--------|
| `nii` | `net_interest_income` | ✅ Both names supported |
| `nim` | `nim` | ✅ OK |
| `cir` | `cir` | ✅ OK |
```

**Update `postprocess_results()` to add aliases:**

```python
def postprocess_results(self, df: pd.DataFrame) -> pd.DataFrame:
    """
    Post-process results with column renaming and aliases

    Args:
        df: DataFrame with calculated metrics

    Returns:
        DataFrame ready for output
    """
    result = super().postprocess_results(df)

    # Add aliases for backward compatibility
    if 'net_revenue_growth' in result.columns:
        result['net_revenue_gr'] = result['net_revenue_growth']

    if 'npatmi_growth' in result.columns:
        result['npatmi_gr'] = result['npatmi_growth']

    return result
```

#### Phase 3.2: Test Dashboard Loading (1 ngày)

**Create integration test:**

```python
#!/usr/bin/env python3
"""
Test dashboard can load and display all required metrics
"""

import pandas as pd
from pathlib import Path

def test_company_dashboard_metrics():
    """Test company dashboard has all required metrics"""

    # Load output file
    data_path = Path("DATA/processed/fundamental/company/company_financial_metrics.parquet")
    df = pd.read_parquet(data_path)

    # Required metrics for company dashboard
    required_metrics = [
        'symbol', 'report_date', 'year', 'quarter',
        'net_revenue', 'net_revenue_growth', 'net_revenue_gr',  # Aliases
        'gross_margin', 'net_margin', 'ebitda_margin',
        'roe', 'roa', 'eps',
        'total_assets', 'total_equity', 'debt_to_equity'
    ]

    # Check all required columns exist
    missing = set(required_metrics) - set(df.columns)

    if missing:
        print(f"❌ Missing metrics: {missing}")
        return False
    else:
        print(f"✅ All {len(required_metrics)} required metrics present")
        return True

def test_bank_dashboard_metrics():
    """Test bank dashboard has all required metrics"""

    data_path = Path("DATA/processed/fundamental/bank/bank_financial_metrics.parquet")
    df = pd.read_parquet(data_path)

    required_metrics = [
        'symbol', 'report_date', 'year', 'quarter',
        'nim', 'roea', 'roaa',
        'cir', 'npl_ratio', 'casa_ratio', 'ldr_pure',
        'nii', 'toi', 'noii'
    ]

    missing = set(required_metrics) - set(df.columns)

    if missing:
        print(f"❌ Missing metrics: {missing}")
        return False
    else:
        print(f"✅ All {len(required_metrics)} required metrics present")
        return True

if __name__ == "__main__":
    print("Testing Dashboard Metric Requirements")
    print("=" * 60)

    test_company_dashboard_metrics()
    test_bank_dashboard_metrics()
```

---

### PHASE 4: Testing & Validation (3 ngày)

#### Phase 4.1: Unit Tests for Formulas (1 ngày)

**Pattern for all formula tests:**

```python
# tests/test_base_formulas.py

import pytest
from PROCESSORS.fundamental.formulas._base_formulas import (
    calculate_roe, calculate_roa, calculate_gross_margin
)

class TestProfitabilityFormulas:
    """Test profitability calculation formulas"""

    def test_roe_normal_case(self):
        """ROE tính toán đúng với giá trị hợp lệ"""
        result = calculate_roe(
            net_income=100_000_000_000,  # 100 tỷ
            total_equity=500_000_000_000  # 500 tỷ
        )
        assert result == 20.0, f"Expected ROE=20.0, got {result}"

    def test_roe_zero_equity(self):
        """ROE trả về None khi vốn chủ sở hữu = 0"""
        result = calculate_roe(100_000_000_000, 0)
        assert result is None

    def test_roe_negative_equity(self):
        """ROE trả về None khi vốn chủ sở hữu âm"""
        result = calculate_roe(100_000_000_000, -50_000_000_000)
        assert result is None
```

#### Phase 4.2: Integration Tests (1 ngày)

#### Phase 4.3: End-to-End Tests (1 ngày)

---

### PHASE 5: Documentation & Rollout (2 ngày)

#### Phase 5.1: Create Formula Reference Guide (1 ngày)

**File:** `docs/FORMULA_REFERENCE.md`

```markdown
# Formula Reference Guide - Hướng dẫn sử dụng công thức tài chính

## Cách sử dụng

### Import formulas

```python
# Universal formulas
from PROCESSORS.fundamental.formulas._base_formulas import (
    calculate_roe, calculate_roa, calculate_gross_margin
)

# Entity-specific formulas
from PROCESSORS.fundamental.formulas.bank_formulas import (
    calculate_nim, calculate_cir
)
```

### Sử dụng trong calculators

```python
# Trong calculator method
def calculate_profitability_ratios(self, df):
    # ROE calculation
    df['roe'] = df.apply(
        lambda row: calculate_roe(
            net_income=row['npatmi'] * 1e9,
            total_equity=row['total_equity'] * 1e9
        ),
        axis=1
    )
```

## Danh sách công thức

### Profitability (Sinh lời)

1. **ROE** - Return on Equity
2. **ROA** - Return on Assets
3. **ROI** - Return on Investment
4. **Gross Margin** - Biên lợi nhuận gộp
...
```

#### Phase 5.2: Rollout Plan (1 ngày)

---

## 4. SUCCESS METRICS

### Quantitative

- ✅ **100% formulas có Vietnamese docstrings**
- ✅ **0 duplicated formulas** (removed ~20%)
- ✅ **95%+ test coverage** for formulas
- ✅ **All dashboard metrics available** in calculator output
- ✅ **Schema validation** for all entity types

### Qualitative

- ✅ Clear data flow từ raw → formulas → calculators → display
- ✅ Easy to add new metrics (chỉ cần add formula và calculator usage)
- ✅ Maintainable codebase với clear separation of concerns
- ✅ Vietnamese documentation cho finance team

---

## 5. TIMELINE

| Week | Phase | Tasks | Output |
|------|-------|-------|--------|
| 1 | Phase 1 | Formula consolidation, Vietnamese docstrings | Single source formulas |
| 2 | Phase 2 | Calculator updates, schema validation | Standardized calculators |
| 3 | Phase 3-5 | Dashboard integration, testing, docs | Production-ready system |

**Total:** 3 tuần (có thể parallel nếu có 2 người)

---

## 6. RECOMMENDED EXECUTION ORDER

### Option A: Sequential (An toàn nhất)

```
Week 1: Phase 1 (Formula consolidation)
  ↓
Week 2: Phase 2 (Calculator updates)
  ↓
Week 3: Phase 3-5 (Integration, testing, docs)
```

### Option B: Parallel (Nhanh hơn)

```
Week 1:
├─ Phase 1.1-1.2 (Person 1: Formula audit & cleanup)
└─ Phase 2.1 (Person 2: Update calculator imports)

Week 2:
├─ Phase 1.3 + 2.2 (Person 1: Docstrings + Schema validation)
└─ Phase 2.3-2.4 (Person 2: Error handling + Growth calculations)

Week 3:
├─ Phase 3 (Person 1: Dashboard integration)
└─ Phase 4-5 (Person 2: Testing + Documentation)
```

---

## 7. NEXT STEPS - BẮT ĐẦU NGAY

**Để bắt đầu implementation, bạn cần:**

1. **Review & approve plan này**
2. **Chọn execution order** (Sequential hay Parallel?)
3. **Quyết định có cần naming restructure trước không?**
4. **Start với Phase 1.1** - Formula audit

**Câu hỏi cho bạn:**

1. Có metrics nào khác cần add vào không? (ví dụ: P/E, P/B, dividend yield?)
2. Có thay đổi nào về benchmark values không?
3. Bạn muốn tôi bắt đầu implement Phase 1.1 luôn không?

---

**Plan Status:** READY FOR REVIEW & APPROVAL
**Next Steps:** Review → Approve → Begin Phase 1.1
