# 📘 HƯỚNG DẪN TÙY CHỈNH FORMULAS & DATA

**Ngày tạo:** 2025-12-08
**Mục đích:** Hướng dẫn chi tiết cách sửa đổi, thêm mới công thức và lưu data

---

## 📑 MỤC LỤC

1. [Cấu trúc hiện tại](#cấu-trúc-hiện-tại)
2. [Sửa đổi công thức hiện có](#1-sửa-đổi-công-thức-hiện-có)
3. [Thêm công thức mới](#2-thêm-công-thức-mới)
4. [Lưu data vào Parquet](#3-lưu-data-vào-parquet)
5. [Công thức riêng cho từng ngành](#4-công-thức-riêng-cho-từng-ngành)
6. [Testing & Validation](#5-testing--validation)
7. [Examples thực tế](#6-examples-thực-tế)

---

## CẤU TRÚC HIỆN TẠI

```
Vietnam_dashboard/
├── PROCESSORS/
│   ├── transformers/
│   │   └── financial/
│   │       ├── formulas.py          # 30+ công thức chung
│   │       └── tests/
│   │           └── test_formulas.py # Tests
│   │
│   ├── fundamental/
│   │   └── calculators/
│   │       ├── company_calculator.py    # Dùng formulas
│   │       ├── bank_calculator.py       # Dùng formulas
│   │       ├── insurance_calculator.py  # Dùng formulas
│   │       └── security_calculator.py   # Dùng formulas
│   │
│   └── core/
│       └── registries/
│           └── sector_lookup.py    # Phân loại ngành
│
└── DATA/
    └── processed/
        └── fundamental/
            ├── company/
            │   └── company_financial_metrics.parquet
            ├── bank/
            │   └── bank_financial_metrics.parquet
            ├── insurance/
            │   └── insurance_financial_metrics.parquet
            └── security/
                └── security_financial_metrics.parquet
```

---

## 1. SỬA ĐỔI CÔNG THỨC HIỆN CÓ

### Bước 1: Tìm công thức cần sửa

**File:** `PROCESSORS/transformers/financial/formulas.py`

**Ví dụ:** Bạn muốn sửa công thức ROE

```python
# Công thức hiện tại
def roe(
    net_income: Optional[float],
    total_equity: Optional[float]
) -> Optional[float]:
    """
    Calculate Return on Equity (ROE).

    Formula: (Net Income / Total Equity) * 100
    """
    ratio = safe_divide(net_income, total_equity)
    return ratio * 100 if ratio is not None else None
```

### Bước 2: Sửa đổi công thức

**Giả sử:** Bạn muốn ROE dùng average equity thay vì ending equity

```python
def roe(
    net_income: Optional[float],
    total_equity: Optional[float],
    previous_equity: Optional[float] = None
) -> Optional[float]:
    """
    Calculate Return on Equity (ROE).

    Formula: (Net Income / Average Equity) * 100

    Args:
        net_income: Net income after tax
        total_equity: Current total equity
        previous_equity: Previous period equity (optional)

    Returns:
        ROE percentage
    """
    # Nếu có previous equity, dùng average
    if previous_equity is not None:
        avg_equity = (total_equity + previous_equity) / 2
        ratio = safe_divide(net_income, avg_equity)
    else:
        # Fallback to current equity
        ratio = safe_divide(net_income, total_equity)

    return ratio * 100 if ratio is not None else None
```

### Bước 3: Update test

**File:** `PROCESSORS/transformers/financial/tests/test_formulas.py`

```python
def test_roe_with_average_equity(self):
    """Test ROE with average equity"""
    # ROE = 100 / ((200 + 180)/2) = 100/190 = 52.63%
    assert roe(100, 200, 180) == pytest.approx(52.63, rel=1e-2)

    # ROE with only current equity (backward compatible)
    assert roe(100, 500) == 20.0
```

### Bước 4: Chạy test

```bash
# Install pytest nếu chưa có
pip install pytest

# Run test
pytest PROCESSORS/transformers/financial/tests/test_formulas.py::TestProfitabilityRatios::test_roe_with_average_equity -v
```

### Bước 5: Update calculator (nếu cần)

**File:** `PROCESSORS/fundamental/calculators/company_calculator.py`

```python
def calculate_profitability_ratios(self, df: pd.DataFrame) -> pd.DataFrame:
    """Calculate ROE with average equity"""
    result_df = df.copy()

    # Sort by ticker and date
    df = df.sort_values(['ticker', 'year', 'quarter'])

    # Get previous equity
    df['prev_equity'] = df.groupby('ticker')['total_equity'].shift(1)

    # Calculate ROE with average equity
    result_df['roe'] = df.apply(
        lambda row: roe(
            net_income=row['npatmi'] * 1e9,
            total_equity=row['total_equity'] * 1e9,
            previous_equity=row['prev_equity'] * 1e9 if pd.notna(row['prev_equity']) else None
        ),
        axis=1
    )

    return result_df
```

---

## 2. THÊM CÔNG THỨC MỚI

### Ví dụ: Thêm công thức ROIC (Return on Invested Capital) mới

### Bước 1: Thêm vào formulas.py

**File:** `PROCESSORS/transformers/financial/formulas.py`

**Tìm section Profitability Ratios (khoảng dòng 200-250):**

```python
# =============================================================================
# PROFITABILITY RATIOS
# =============================================================================

# ... (các công thức ROE, ROA hiện có)

def roic_advanced(
    nopat: Optional[float],
    debt: Optional[float],
    equity: Optional[float],
    cash: Optional[float] = None
) -> Optional[float]:
    """
    Calculate Return on Invested Capital (ROIC) - Advanced version.

    Formula: NOPAT / (Debt + Equity - Cash)

    Args:
        nopat: Net Operating Profit After Tax
        debt: Total debt
        equity: Total equity
        cash: Cash and cash equivalents (optional, default=0)

    Returns:
        ROIC percentage

    Examples:
        >>> roic_advanced(100, 300, 500, 50)  # NOPAT=100, Invested Capital=750
        13.33

        >>> roic_advanced(100, 300, 500)  # No cash adjustment
        12.5
    """
    if nopat is None or debt is None or equity is None:
        return None

    # Calculate invested capital
    cash_amount = cash if cash is not None else 0
    invested_capital = debt + equity - cash_amount

    # Calculate ROIC
    ratio = safe_divide(nopat, invested_capital)
    return ratio * 100 if ratio is not None else None
```

### Bước 2: Export công thức mới

**File:** `PROCESSORS/transformers/financial/__init__.py`

**Thêm vào danh sách imports:**

```python
from .formulas import (
    # ... (các imports hiện có)

    # Profitability
    roe,
    roa,
    roic,
    roic_advanced,  # ← THÊM MỚI

    # ... (các imports khác)
)

__all__ = [
    # ... (các exports hiện có)

    # Profitability
    "roe",
    "roa",
    "roic",
    "roic_advanced",  # ← THÊM MỚI
]
```

### Bước 3: Thêm test

**File:** `PROCESSORS/transformers/financial/tests/test_formulas.py`

**Thêm vào class TestProfitabilityRatios:**

```python
class TestProfitabilityRatios:
    # ... (các tests hiện có)

    def test_roic_advanced(self):
        """Test ROIC advanced calculation"""
        # ROIC = 100 / (300 + 500 - 50) = 100/750 = 13.33%
        assert roic_advanced(100, 300, 500, 50) == pytest.approx(13.33, rel=1e-2)

        # ROIC without cash = 100 / (300 + 500) = 12.5%
        assert roic_advanced(100, 300, 500) == 12.5

    def test_roic_advanced_edge_cases(self):
        """Test ROIC advanced edge cases"""
        assert roic_advanced(None, 300, 500) is None
        assert roic_advanced(100, None, 500) is None
        assert roic_advanced(100, 300, None) is None
```

### Bước 4: Test công thức mới

```bash
# Test specific function
python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
from PROCESSORS.transformers.financial import roic_advanced

result = roic_advanced(100, 300, 500, 50)
print(f'ROIC Advanced: {result:.2f}%')  # Should print: 13.33%
"
```

### Bước 5: Sử dụng trong calculator

**File:** `PROCESSORS/fundamental/calculators/company_calculator.py`

```python
from PROCESSORS.transformers.financial import roic_advanced

def calculate_profitability_ratios(self, df: pd.DataFrame) -> pd.DataFrame:
    """Calculate profitability ratios including ROIC"""
    result_df = df.copy()

    # ... (các tính toán khác)

    # Calculate ROIC Advanced
    result_df['roic_advanced'] = df.apply(
        lambda row: roic_advanced(
            nopat=row['nopat'] * 1e9 if 'nopat' in row else None,
            debt=(row['st_debt'] + row['lt_debt']) * 1e9,
            equity=row['total_equity'] * 1e9,
            cash=row['cash'] * 1e9
        ),
        axis=1
    )

    return result_df
```

---

## 3. LƯU DATA VÀO PARQUET

### Cách 1: Thêm cột mới vào Parquet hiện có

**Scenario:** Bạn vừa thêm công thức mới và muốn lưu kết quả vào parquet

**File:** `PROCESSORS/fundamental/calculators/company_calculator.py`

```python
def calculate_all_metrics(self):
    """
    Calculate all metrics and save to parquet.
    """
    # 1. Load data
    df = self.load_fundamental_data()

    # 2. Calculate existing metrics
    df = self.calculate_income_statement(df)
    df = self.calculate_balance_sheet(df)
    df = self.calculate_profitability_ratios(df)  # ← Includes new ROIC

    # 3. Save to parquet
    output_path = DATA_ROOT / "processed" / "fundamental" / "company" / "company_financial_metrics.parquet"

    # Create backup first (important!)
    if output_path.exists():
        backup_path = output_path.parent / f"backup_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.parquet"
        import shutil
        shutil.copy(output_path, backup_path)
        print(f"✅ Backup created: {backup_path}")

    # Save new data
    df.to_parquet(output_path, index=False)
    print(f"✅ Saved {len(df)} rows to {output_path}")

    return df
```

**Run calculator:**

```bash
python3 PROCESSORS/fundamental/calculators/company_calculator.py
```

### Cách 2: Merge cột mới vào parquet hiện có

**Scenario:** Bạn chỉ muốn thêm 1 cột mới mà không tính lại tất cả

```python
import pandas as pd
from pathlib import Path

# 1. Load existing parquet
parquet_path = Path("DATA/processed/fundamental/company/company_financial_metrics.parquet")
df_existing = pd.read_parquet(parquet_path)

print(f"Existing columns: {list(df_existing.columns)}")
print(f"Existing rows: {len(df_existing)}")

# 2. Calculate new column
from PROCESSORS.transformers.financial import roic_advanced

df_existing['roic_advanced'] = df_existing.apply(
    lambda row: roic_advanced(
        nopat=row.get('nopat', 0) * 1e9,
        debt=(row.get('st_debt', 0) + row.get('lt_debt', 0)) * 1e9,
        equity=row.get('total_equity', 0) * 1e9,
        cash=row.get('cash', 0) * 1e9
    ),
    axis=1
)

# 3. Backup & Save
backup_path = parquet_path.parent / f"backup_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.parquet"
df_existing.to_parquet(backup_path, index=False)
print(f"✅ Backup: {backup_path}")

df_existing.to_parquet(parquet_path, index=False)
print(f"✅ Updated: {parquet_path}")
print(f"New columns: {list(df_existing.columns)}")
```

**Run script:**

```bash
python3 -c "
# Paste code above
"
```

### Cách 3: Tạo parquet mới cho metrics riêng

**Scenario:** Bạn muốn tạo parquet riêng cho sector-specific metrics

```python
import pandas as pd
from pathlib import Path

def save_sector_metrics(sector_name: str, df: pd.DataFrame):
    """
    Save sector-specific metrics to separate parquet file.

    Args:
        sector_name: Sector name (e.g., 'banking', 'real_estate')
        df: DataFrame with sector metrics
    """
    # Create sector directory
    sector_dir = Path("DATA/processed/fundamental/sectors")
    sector_dir.mkdir(parents=True, exist_ok=True)

    # Save to parquet
    output_path = sector_dir / f"{sector_name}_metrics.parquet"
    df.to_parquet(output_path, index=False)

    print(f"✅ Saved {len(df)} rows to {output_path}")
    print(f"Columns: {list(df.columns)}")

    return output_path

# Example usage
banking_df = pd.DataFrame({
    'ticker': ['ACB', 'VCB', 'CTG'],
    'nim': [2.5, 2.8, 2.6],
    'cir': [40.0, 35.0, 38.0],
    'npl_ratio': [1.2, 0.8, 1.0]
})

save_sector_metrics('banking', banking_df)
```

---

## 4. CÔNG THỨC RIÊNG CHO TỪNG NGÀNH

### Cách 1: Tạo file formulas riêng cho ngành

**Tạo:** `PROCESSORS/transformers/financial/sector_formulas.py`

```python
#!/usr/bin/env python3
"""
Sector-Specific Financial Formulas
===================================

Công thức tài chính đặc thù cho từng ngành.

Author: Your Name
Date: 2025-12-08
"""

from typing import Optional
from .formulas import safe_divide


# =============================================================================
# NGÂN HÀNG (BANKING)
# =============================================================================

def loan_to_deposit_ratio(
    total_loans: Optional[float],
    total_deposits: Optional[float]
) -> Optional[float]:
    """
    Tỷ lệ cho vay trên huy động (LDR - Loan to Deposit Ratio).

    Formula: (Total Loans / Total Deposits) * 100

    Ý nghĩa:
    - < 80%: Ngân hàng dư thừa thanh khoản
    - 80-90%: Mức tối ưu
    - > 90%: Ngân hàng thiếu thanh khoản

    Args:
        total_loans: Tổng dư nợ cho vay
        total_deposits: Tổng tiền gửi khách hàng

    Returns:
        LDR percentage
    """
    ratio = safe_divide(total_loans, total_deposits)
    return ratio * 100 if ratio is not None else None


def casa_ratio(
    casa_deposits: Optional[float],
    total_deposits: Optional[float]
) -> Optional[float]:
    """
    Tỷ lệ tiền gửi không kỳ hạn (CASA Ratio).

    CASA = Current Account + Saving Account

    Formula: (CASA Deposits / Total Deposits) * 100

    Ý nghĩa:
    - > 30%: Tốt (chi phí vốn thấp)
    - 20-30%: Trung bình
    - < 20%: Kém

    Args:
        casa_deposits: Tiền gửi không kỳ hạn + tiết kiệm
        total_deposits: Tổng tiền gửi

    Returns:
        CASA ratio percentage
    """
    ratio = safe_divide(casa_deposits, total_deposits)
    return ratio * 100 if ratio is not None else None


# =============================================================================
# BẤT ĐỘNG SẢN (REAL ESTATE)
# =============================================================================

def inventory_to_equity(
    inventory: Optional[float],
    total_equity: Optional[float]
) -> Optional[float]:
    """
    Tỷ lệ tồn kho trên vốn chủ sở hữu.

    Formula: (Inventory / Total Equity) * 100

    Ý nghĩa:
    - < 200%: An toàn
    - 200-300%: Cảnh báo
    - > 300%: Rủi ro cao

    Args:
        inventory: Hàng tồn kho (bất động sản chưa bán)
        total_equity: Vốn chủ sở hữu

    Returns:
        Inventory/Equity percentage
    """
    ratio = safe_divide(inventory, total_equity)
    return ratio * 100 if ratio is not None else None


def presale_coverage(
    cash: Optional[float],
    presale_deposits: Optional[float],
    construction_payables: Optional[float]
) -> Optional[float]:
    """
    Khả năng thanh toán từ tiền ứng trước.

    Formula: (Cash + Presale Deposits) / Construction Payables

    Args:
        cash: Tiền mặt
        presale_deposits: Tiền ứng trước khách hàng
        construction_payables: Phải trả nhà thầu xây dựng

    Returns:
        Coverage ratio
    """
    numerator = (cash or 0) + (presale_deposits or 0)
    return safe_divide(numerator, construction_payables)


# =============================================================================
# BÁN LẺ (RETAIL)
# =============================================================================

def same_store_sales_growth(
    current_sales: Optional[float],
    previous_sales: Optional[float]
) -> Optional[float]:
    """
    Tăng trưởng doanh thu cửa hàng cùng kỳ (SSSG).

    Formula: ((Current - Previous) / Previous) * 100

    Args:
        current_sales: Doanh thu kỳ hiện tại
        previous_sales: Doanh thu cùng kỳ năm trước

    Returns:
        SSSG percentage
    """
    if current_sales is None or previous_sales is None:
        return None

    if previous_sales == 0:
        return None

    return ((current_sales - previous_sales) / previous_sales) * 100


def sales_per_square_meter(
    total_sales: Optional[float],
    total_area_sqm: Optional[float]
) -> Optional[float]:
    """
    Doanh thu trên mét vuông.

    Formula: Total Sales / Total Area (sqm)

    Args:
        total_sales: Tổng doanh thu
        total_area_sqm: Tổng diện tích (m²)

    Returns:
        Sales per sqm
    """
    return safe_divide(total_sales, total_area_sqm)


# =============================================================================
# SẢN XUẤT (MANUFACTURING)
# =============================================================================

def capacity_utilization(
    actual_production: Optional[float],
    max_capacity: Optional[float]
) -> Optional[float]:
    """
    Tỷ lệ sử dụng công suất.

    Formula: (Actual Production / Max Capacity) * 100

    Args:
        actual_production: Sản lượng thực tế
        max_capacity: Công suất tối đa

    Returns:
        Utilization percentage
    """
    ratio = safe_divide(actual_production, max_capacity)
    return ratio * 100 if ratio is not None else None


# =============================================================================
# DEMO
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("SECTOR-SPECIFIC FORMULAS DEMO")
    print("=" * 60)

    # Banking
    print("\n🏦 NGÂN HÀNG:")
    ldr = loan_to_deposit_ratio(800, 1000)
    casa = casa_ratio(350, 1000)
    print(f"  LDR: {ldr:.1f}%")
    print(f"  CASA Ratio: {casa:.1f}%")

    # Real Estate
    print("\n🏢 BẤT ĐỘNG SẢN:")
    inv_equity = inventory_to_equity(500, 200)
    print(f"  Inventory/Equity: {inv_equity:.1f}%")

    # Retail
    print("\n🛒 BÁN LẺ:")
    sssg = same_store_sales_growth(120, 100)
    sales_sqm = sales_per_square_meter(1000, 500)
    print(f"  SSSG: {sssg:.1f}%")
    print(f"  Sales/m²: {sales_sqm:.1f}")

    print("\n✅ All sector formulas working!")
```

### Bước 2: Export sector formulas

**File:** `PROCESSORS/transformers/financial/__init__.py`

```python
from .sector_formulas import (
    # Banking
    loan_to_deposit_ratio,
    casa_ratio,

    # Real Estate
    inventory_to_equity,
    presale_coverage,

    # Retail
    same_store_sales_growth,
    sales_per_square_meter,

    # Manufacturing
    capacity_utilization,
)

__all__ = [
    # ... (existing exports)

    # Sector-specific
    "loan_to_deposit_ratio",
    "casa_ratio",
    "inventory_to_equity",
    "presale_coverage",
    "same_store_sales_growth",
    "sales_per_square_meter",
    "capacity_utilization",
]
```

### Cách 2: Sử dụng sector formulas trong calculator

**Tạo:** `PROCESSORS/fundamental/calculators/sector_calculator.py`

```python
#!/usr/bin/env python3
"""
Sector-Specific Calculator
===========================

Tính toán metrics đặc thù cho từng ngành.
"""

import pandas as pd
from typing import Dict, List
from pathlib import Path

from PROCESSORS.transformers.financial import (
    # Banking
    loan_to_deposit_ratio,
    casa_ratio,
    # Real Estate
    inventory_to_equity,
    # Retail
    same_store_sales_growth,
)

from PROCESSORS.core.registries.sector_lookup import SectorRegistry


class SectorCalculator:
    """
    Calculate sector-specific metrics.
    """

    def __init__(self):
        self.sector_registry = SectorRegistry()

    def calculate_banking_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate banking-specific metrics.

        Args:
            df: DataFrame with banking data

        Returns:
            DataFrame with banking metrics added
        """
        result_df = df.copy()

        # LDR
        result_df['ldr'] = df.apply(
            lambda row: loan_to_deposit_ratio(
                total_loans=row.get('total_loans', 0) * 1e9,
                total_deposits=row.get('total_deposits', 0) * 1e9
            ),
            axis=1
        )

        # CASA Ratio
        result_df['casa_ratio'] = df.apply(
            lambda row: casa_ratio(
                casa_deposits=row.get('casa_deposits', 0) * 1e9,
                total_deposits=row.get('total_deposits', 0) * 1e9
            ),
            axis=1
        )

        return result_df

    def calculate_real_estate_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate real estate metrics"""
        result_df = df.copy()

        result_df['inventory_equity_ratio'] = df.apply(
            lambda row: inventory_to_equity(
                inventory=row.get('inventory', 0) * 1e9,
                total_equity=row.get('total_equity', 0) * 1e9
            ),
            axis=1
        )

        return result_df

    def calculate_by_sector(self, df: pd.DataFrame, sector: str) -> pd.DataFrame:
        """
        Calculate metrics based on sector.

        Args:
            df: Input DataFrame
            sector: Sector name ('Ngân hàng', 'Bất động sản', etc.)

        Returns:
            DataFrame with sector-specific metrics
        """
        if sector == "Ngân hàng":
            return self.calculate_banking_metrics(df)
        elif sector == "Bất động sản":
            return self.calculate_real_estate_metrics(df)
        else:
            # Return original df if no specific metrics
            return df


# Usage example
if __name__ == "__main__":
    calculator = SectorCalculator()

    # Example: Banking data
    banking_df = pd.DataFrame({
        'ticker': ['ACB', 'VCB'],
        'total_loans': [500, 800],  # billions
        'total_deposits': [600, 900],
        'casa_deposits': [200, 350],
    })

    result = calculator.calculate_banking_metrics(banking_df)
    print("\n🏦 Banking Metrics:")
    print(result[['ticker', 'ldr', 'casa_ratio']])
```

---

## 5. TESTING & VALIDATION

### Test công thức mới

```bash
# Test specific formula
python3 -c "
from PROCESSORS.transformers.financial import loan_to_deposit_ratio
result = loan_to_deposit_ratio(800, 1000)
print(f'LDR: {result}%')  # Should be 80.0
"
```

### Validate data trong parquet

```python
import pandas as pd

# Load parquet
df = pd.read_parquet("DATA/processed/fundamental/company/company_financial_metrics.parquet")

# Check new column
print(f"Columns: {list(df.columns)}")
print(f"\nNew column 'roic_advanced' stats:")
print(df['roic_advanced'].describe())

# Check for NaN
print(f"\nNaN count: {df['roic_advanced'].isna().sum()}")

# Sample data
print(f"\nSample data:")
print(df[['ticker', 'year', 'quarter', 'roic_advanced']].head(10))
```

---

## 6. EXAMPLES THỰC TẾ

### Example 1: Thêm công thức Dupont ROE

**Step 1: Thêm vào formulas.py**

```python
def dupont_roe(
    net_margin: Optional[float],
    asset_turnover: Optional[float],
    equity_multiplier: Optional[float]
) -> Optional[float]:
    """
    DuPont ROE Analysis.

    Formula: ROE = Net Margin × Asset Turnover × Equity Multiplier

    Args:
        net_margin: Net Income / Revenue
        asset_turnover: Revenue / Assets
        equity_multiplier: Assets / Equity

    Returns:
        ROE percentage
    """
    if net_margin is None or asset_turnover is None or equity_multiplier is None:
        return None

    roe_value = net_margin * asset_turnover * equity_multiplier
    return roe_value * 100
```

**Step 2: Sử dụng trong calculator**

```python
def calculate_dupont_analysis(self, df: pd.DataFrame) -> pd.DataFrame:
    """Calculate DuPont ROE breakdown"""
    result_df = df.copy()

    # Calculate components
    result_df['net_margin_ratio'] = df['npatmi'] / df['net_revenue']
    result_df['asset_turnover_ratio'] = df['net_revenue'] / df['total_assets']
    result_df['equity_multiplier'] = df['total_assets'] / df['total_equity']

    # Calculate DuPont ROE
    result_df['dupont_roe'] = df.apply(
        lambda row: dupont_roe(
            net_margin=row['net_margin_ratio'],
            asset_turnover=row['asset_turnover_ratio'],
            equity_multiplier=row['equity_multiplier']
        ),
        axis=1
    )

    return result_df
```

### Example 2: Công thức riêng cho ngành thép

```python
# In sector_formulas.py

def steel_ebitda_per_ton(
    ebitda: Optional[float],
    production_volume_tons: Optional[float]
) -> Optional[float]:
    """
    EBITDA trên tấn thép (Steel sector).

    Formula: EBITDA / Production Volume

    Args:
        ebitda: EBITDA (billions VND)
        production_volume_tons: Sản lượng (tấn)

    Returns:
        EBITDA per ton (million VND/ton)
    """
    if ebitda is None or production_volume_tons is None:
        return None

    if production_volume_tons == 0:
        return None

    # Convert to million VND per ton
    ebitda_million = ebitda * 1000  # billions → millions
    return ebitda_million / production_volume_tons
```

### Example 3: Lưu metrics cho nhiều ngành

```python
from PROCESSORS.fundamental.calculators.sector_calculator import SectorCalculator
from PROCESSORS.core.registries.sector_lookup import SectorRegistry
import pandas as pd

# Initialize
calculator = SectorCalculator()
registry = SectorRegistry()

# Load all companies
df_all = pd.read_parquet("DATA/processed/fundamental/company/company_financial_metrics.parquet")

# Get unique sectors
sectors = registry.get_all_sectors()

# Calculate for each sector
for sector in sectors:
    # Filter companies in this sector
    tickers = registry.get_tickers_by_sector(sector)
    df_sector = df_all[df_all['ticker'].isin(tickers)]

    if len(df_sector) == 0:
        continue

    # Calculate sector-specific metrics
    df_sector = calculator.calculate_by_sector(df_sector, sector)

    # Save to sector-specific parquet
    output_path = f"DATA/processed/fundamental/sectors/{sector}_metrics.parquet"
    df_sector.to_parquet(output_path, index=False)

    print(f"✅ {sector}: {len(df_sector)} rows saved to {output_path}")
```

---

## 📝 CHECKLIST KHI THÊM CÔNG THỨC MỚI

- [ ] Thêm function vào `formulas.py` hoặc `sector_formulas.py`
- [ ] Viết docstring đầy đủ (Formula, Args, Returns, Examples)
- [ ] Add type hints (Optional[float])
- [ ] Handle None/NaN cases
- [ ] Export trong `__init__.py`
- [ ] Viết test case trong `test_formulas.py`
- [ ] Run test: `pytest ... -v`
- [ ] Test thực tế với data sample
- [ ] Update calculator để sử dụng formula mới
- [ ] Backup parquet trước khi save
- [ ] Validate kết quả sau khi save
- [ ] Commit code với message rõ ràng
- [ ] Update documentation

---

## 🎯 BEST PRACTICES

### 1. Luôn backup trước khi sửa

```bash
# Backup manual
cp DATA/processed/fundamental/company/company_financial_metrics.parquet \
   DATA/processed/fundamental/company/backup_$(date +%Y%m%d_%H%M%S).parquet
```

### 2. Test trên subset trước khi apply toàn bộ

```python
# Test on 10 rows first
df_test = df.head(10)
df_test['new_metric'] = df_test.apply(lambda row: new_formula(...), axis=1)
print(df_test[['ticker', 'new_metric']])
```

### 3. Validate kết quả

```python
# Check for infinities, NaN
assert not df['new_metric'].isin([float('inf'), float('-inf')]).any()
assert df['new_metric'].notna().sum() > 0  # At least some values
```

### 4. Document formulas bằng tiếng Việt

```python
def custom_ratio(...):
    """
    Tỷ lệ đặc biệt cho ngành ABC.

    Công thức: (A + B) / C

    Ý nghĩa:
    - > 1.5: Tốt
    - 1.0-1.5: Trung bình
    - < 1.0: Kém
    """
```

---

## 🆘 TROUBLESHOOTING

### Lỗi: Import không tìm thấy function

```python
# Fix: Check __init__.py exports
from PROCESSORS.transformers.financial import your_new_function

# If error, add to __init__.py:
__all__ = [
    "your_new_function",  # ← Add here
]
```

### Lỗi: Parquet bị corrupt sau save

```bash
# Restore từ backup
cp DATA/processed/fundamental/company/backup_20251208_*.parquet \
   DATA/processed/fundamental/company/company_financial_metrics.parquet
```

### Lỗi: Formula trả về NaN nhiều

```python
# Debug: Check input values
df['debug_input_a'] = df['column_a']
df['debug_input_b'] = df['column_b']
df['debug_result'] = df.apply(lambda row: formula(row['column_a'], row['column_b']), axis=1)

print(df[df['debug_result'].isna()][['ticker', 'debug_input_a', 'debug_input_b', 'debug_result']])
```

---

## 📚 TÀI LIỆU THAM KHẢO

- **Transformers Layer Guide:** `/docs/TRANSFORMERS_LAYER_GUIDE.md`
- **Week 4 Report:** `/docs/WEEK4_COMPLETION_REPORT.md`
- **Formula Source:** `/PROCESSORS/transformers/financial/formulas.py`
- **Test Examples:** `/PROCESSORS/transformers/financial/tests/test_formulas.py`
- **CLAUDE.md:** Project documentation

---

**Tạo bởi:** Claude Code
**Ngày:** 2025-12-08
**Version:** 1.0
