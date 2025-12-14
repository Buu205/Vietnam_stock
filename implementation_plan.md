
# Implementation Plan - Brokerage Financial Formulas

The goal is to implement calculations for financial metrics found in the `Brokerage Masterfile.xlsx` (Master sheet) to allow comparison and tracking of brokerage firms. Since the Excel file uses value lookups, we will implement standard financial formulas for these metrics using the existing raw data (`CIS`, `CBS`) defined in `metric_registry.json`.

## User Review Required
> [!IMPORTANT]
> The `Brokerage Masterfile.xlsx` "Input" sheet appears to contain pre-calculated values for ratios. I will implement live formulas for these based on standard definitions (e.g., `%YTD`, `TTM`). Please review the proposed formulas below.

## Proposed Changes

### Configuration
#### [MODIFY] [metric_registry.json](file:///Users/buuphan/Dev/Vietnam_dashboard/config/metadata/metric_registry.json)
- Add new `DERIVED` metrics for Brokerage (`COMPANY` entity type).
- Categories: `GROWTH`, `PROFITABILITY`, `CAPITAL`, `VALUATION`.
- Each metric will have `is_calculated: true`.

### Proposed Formulas

| Code | Name | Formula Description | Technical Formula (Variables) |
|------|------|---------------------|-------------------------------|
| **MT.100** | FVTPL Growth (%YTD) | (Current FVTPL - Start of Year FVTPL) / Start of Year FVTPL | `(CBS_121 - CBS_121_StartYear) / CBS_121_StartYear` |
| **MT.103** | Total Loans Growth (%YTD) | Growth of Loans (Margin + Advances) | `(CBS_135 + CBS_136_Loans) ...` (Need to verify Loan codes) |
| **MT.127** | Revenue Growth (%Q YoY) | (Revenue Q Current - Revenue Q Same Period Last Year) / ... | `(CIS_01 + CIS_21 - ...)` (Need precise Revenue def) |
| **MT.36** | ROAA (TTM) | Net Income (Rolling 4Q) / Average Total Assets (5 quarters) | `Sum(CIS_60, 4Q) / Avg(CBS_270, 5Q)` |
| **MT.37** | ROAE (TTM) | Net Income (Rolling 4Q) / Average Equity (5 quarters) | `Sum(CIS_60, 4Q) / Avg(CBS_400, 5Q)` |
| **MT.52** | Gross Profit Margin | Gross Profit / Revenue | `CIS_20 / CIS_10` (or `CIS_TotalOperatingProfit / Revenue`) |

*Note: I will verify exact codes for "Total Loans", "Total Investments" from `metric_registry.json`.*

### Logic Implementation
#### [NEW] [brokerage_calculator.py](file:///Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/valuation/calculators/brokerage_calculator.py)
- Create a calculator class that takes a DataFrame of raw metrics (`CIS`, `CBS`) and computes the derived `MT` metrics.
- Support `TTM` (Trailing Twelve Months), `Q YoY` (Quarter on Year), and `YTD` (Year to Date) transformations.

## Verification Plan
### Automated Tests
- Run `brokerage_calculator.py` with sample data and compare against manual calculations.
- Check if all new metrics are generated in the output.

### Manual Verification
- Generate a sample report for a specific company (e.g. SSI, VND) and compare values with the user's `Brokerage Masterfile.xlsx` (visual check).
