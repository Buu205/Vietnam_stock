# Bank Dashboard Specification
# Dashboard Phân Tích Ngân Hàng

> **Page:** `WEBAPP/pages/2_bank_dashboard.py`
> **Service:** `BankService` (TO CREATE)
> **Data:** `DATA/processed/fundamental/bank/bank_financial_metrics.parquet`
> **Status:** To Rebuild from Scratch
> **Priority:** 🟡 MEDIUM (After Company Dashboard)

---

## 1. Page Overview

### Purpose
Specialized fundamental analysis for banking sector with bank-specific metrics

### Key Metrics (Banking-Specific)
- **NII (Net Interest Income)** - Core lending income
- **NIM (Net Interest Margin)** - Profitability of lending (%)
- **NPL Ratio** - Non-Performing Loan ratio (lower is better)
- **CAR (Capital Adequacy Ratio)** - Capital buffer (>9% regulatory)
- **CIR (Cost-to-Income Ratio)** - Operational efficiency (lower is better)
- **ROA, ROE** - Return metrics

---

## 2. Layout Structure

```
┌─────────────────────────────────────────────────────────────┐
│ 🏦 Bank Financial Analysis                                  │
├─────────────────────────────────────────────────────────────┤
│ SECTION 1: Key Banking Metrics (4 cards)                   │
│ [NII] [NIM] [NPL Ratio] [CAR]                             │
├─────────────────────────────────────────────────────────────┤
│ SECTION 2: Net Interest Income Trends                      │
│ [Line chart: NII over time]                                 │
├─────────────────────────────────────────────────────────────┤
│ SECTION 3: Asset Quality       │ SECTION 4: Efficiency     │
│ [NPL Ratio trend]               │ [CIR trend]               │
│ [Provision coverage ratio]      │ [ROA/ROE]                 │
├─────────────────────────────────────────────────────────────┤
│ SECTION 5: Loan Portfolio Breakdown                        │
│ [Stacked area: Corporate, Retail, SME loans]               │
├─────────────────────────────────────────────────────────────┤
│ SECTION 6: Capital Structure                               │
│ [Bar chart: CAR, Tier 1, Tier 2 capital over time]        │
├─────────────────────────────────────────────────────────────┤
│ SECTION 7: Peer Comparison                                 │
│ [Horizontal bars: NIM, NPL, CAR comparison]                │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Key Sections

### SECTION 1: Key Metrics (4 Cards)

**Metrics:**
1. **Net Interest Income (NII)** - Billions VND, QoQ/YoY growth
2. **Net Interest Margin (NIM)** - Percentage, 2 decimals
3. **NPL Ratio** - Percentage (lower is better, inverse delta)
4. **CAR** - Percentage (higher is better, minimum 9%)

**Color Coding:**
- NII: Brand teal (#009B87)
- NIM: Brand blue (#295CA9)
- NPL: Red if >3%, Yellow if 2-3%, Green if <2%
- CAR: Green if >12%, Yellow if 9-12%, Red if <9%

---

### SECTION 2: Net Interest Income Trends

**Chart:** Multi-line chart
**Metrics:**
- Net Interest Income (NII) - Brand teal
- Non-Interest Income - Brand blue
- Total Operating Income - Brand gold

**Frontend-Design Prompt:**
```
Thiết kế "Banking Income Trends" chart cho Bank Dashboard.

Data: report_date, net_interest_income, non_interest_income, total_income
Periods: 8 quarters
Chart: Multi-line, dark theme
Colors: NII (#009B87), Non-II (#295CA9), Total (#FFC132)
Y-axis: "VND Billions"
```

---

### SECTION 3: Asset Quality

**Charts:**
1. **NPL Ratio Trend** - Line chart with warning zones
   - Green zone: 0-2% (good)
   - Yellow zone: 2-3% (watch)
   - Red zone: >3% (poor)

2. **Provision Coverage Ratio** - Bar chart
   - Shows loan loss provisions vs NPLs
   - Minimum 100% coverage recommended

**Frontend-Design Prompt:**
```
Thiết kế "NPL Ratio Trend with Warning Zones" chart.

Data: report_date, npl_ratio (%)
Periods: 12 quarters
Chart: Line chart with colored background zones
- Background: Green (0-2%), Yellow (2-3%), Red (>3%)
- Line: White (#FFFFFF), width=3
- Markers: Circle, size=8
Style: Dark theme (#0A1E42)
```

---

### SECTION 4: Efficiency Metrics

**Charts:**
1. **CIR (Cost-to-Income Ratio)** - Lower is better (<40% is excellent)
2. **ROA/ROE Dual Axis** - Similar to Company Dashboard

---

### SECTION 5: Loan Portfolio Breakdown

**Chart:** Stacked area chart

**Loan Categories:**
- Corporate Loans (brand blue #295CA9)
- Retail Loans (brand teal #009B87)
- SME Loans (brand gold #FFC132)
- Other Loans (light blue #4A7BC8)

**Shows:** Loan mix evolution over time

---

### SECTION 6: Capital Structure

**Chart:** Grouped bar chart

**Metrics:**
- CAR (total)
- Tier 1 Capital Ratio
- Tier 2 Capital Ratio

**Regulatory Lines:**
- CAR minimum: 9% (red dashed line)
- CAR target: 12% (green dashed line)

---

### SECTION 7: Peer Comparison

**Compare banks on:**
- NIM (higher is better)
- NPL Ratio (lower is better)
- CAR (higher is better)
- ROE (higher is better)

**Use horizontal bar charts with current bank highlighted**

---

## 4. Service Layer (TO CREATE)

```python
# WEBAPP/services/bank_service.py

from pathlib import Path
from typing import Optional, List, Dict
import pandas as pd

class BankService:
    """Service layer for Bank financial data."""

    def __init__(self, data_root: Optional[Path] = None):
        if data_root is None:
            current_file = Path(__file__).resolve()
            project_root = current_file.parents[2]
            data_root = project_root / "DATA"

        self.data_path = data_root / "processed" / "fundamental" / "bank"

        if not self.data_path.exists():
            raise FileNotFoundError(f"Bank data path not found: {self.data_path}")

    def get_financial_data(
        self,
        ticker: str,
        period: str = "Quarterly",
        limit: Optional[int] = None
    ) -> pd.DataFrame:
        """Load financial data for a bank ticker."""
        parquet_file = self.data_path / "bank_financial_metrics.parquet"

        if not parquet_file.exists():
            raise FileNotFoundError(f"Bank metrics file not found: {parquet_file}")

        df = pd.read_parquet(parquet_file)
        df = df[df['symbol'] == ticker].copy()

        if df.empty:
            return pd.DataFrame()

        # Filter by period
        if period == "Quarterly":
            df = df[df['freq_code'] == 'Q']
        elif period == "Yearly":
            df = df[df['freq_code'] == 'Y']

        # Sort by date
        df = df.sort_values('report_date')

        # Convert dates
        if 'report_date' in df.columns:
            df['report_date'] = pd.to_datetime(df['report_date'])

        # Limit records
        if limit:
            df = df.tail(limit)

        return df

    def get_latest_metrics(self, ticker: str) -> Dict:
        """Get latest quarter metrics for a bank."""
        df = self.get_financial_data(ticker, "Quarterly", limit=1)
        return df.iloc[-1].to_dict() if not df.empty else {}

    def get_available_tickers(self) -> List[str]:
        """Get list of available bank tickers."""
        parquet_file = self.data_path / "bank_financial_metrics.parquet"

        if not parquet_file.exists():
            return []

        df = pd.read_parquet(parquet_file, columns=['symbol'])
        return sorted(df['symbol'].unique().tolist())

    def get_loan_breakdown(self, ticker: str, limit: int = 8) -> pd.DataFrame:
        """Get loan portfolio breakdown over time."""
        df = self.get_financial_data(ticker, "Quarterly", limit=limit)

        if df.empty:
            return pd.DataFrame()

        # Extract loan columns
        loan_cols = ['report_date', 'corporate_loans', 'retail_loans',
                     'sme_loans', 'other_loans']

        return df[loan_cols] if all(c in df.columns for c in loan_cols) else pd.DataFrame()
```

---

## 5. Implementation Checklist

- [ ] Create `BankService` class
- [ ] Test with bank tickers (ACB, VCB, TCB, MBB, VPB)
- [ ] Create bank-specific chart components
- [ ] Implement all 7 sections
- [ ] Add regulatory warning lines (CAR >9%, NPL <3%)
- [ ] Test with real banking data
- [ ] Validate banking-specific calculations

---

## 6. Banking-Specific Data Columns Required

```python
# Income Statement
net_interest_income        # NII
non_interest_income        # Fee income, trading income
total_operating_income     # NII + Non-II
operating_expenses         # Personnel, admin costs
provision_for_credit_loss  # Loan loss provisions
net_profit                 # Bottom line

# Balance Sheet
total_assets
total_liabilities
total_equity
total_loans                # Gross loans
corporate_loans            # Corporate lending
retail_loans               # Consumer lending
sme_loans                  # SME lending
customer_deposits          # Deposit base
borrowings                 # Interbank + other borrowings

# Asset Quality
npl_ratio                  # Non-Performing Loan ratio (%)
provision_coverage_ratio   # Provisions / NPL (%)

# Profitability
nim                        # Net Interest Margin (%)
cir                        # Cost-to-Income Ratio (%)
roe
roa

# Capital
car                        # Capital Adequacy Ratio (%)
tier1_ratio                # Tier 1 Capital Ratio (%)
tier2_ratio                # Tier 2 Capital Ratio (%)
```

---

**Status:** 📝 SPECIFICATION COMPLETE
**Next:** Implement after Company Dashboard is done
**Estimated Time:** 2-3 days
