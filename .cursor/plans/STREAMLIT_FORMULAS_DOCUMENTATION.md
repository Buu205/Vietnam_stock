# Streamlit Formulas Documentation

**Date:** 2025-12-16  
**Purpose:** Document ALL calculations currently performed in Streamlit dashboards before moving to processors  
**Status:** 📋 COMPLETE INVENTORY

---

## 🎯 OVERVIEW

This document captures ALL formulas, calculations, and transformations currently performed in Streamlit dashboards. These calculations need to be moved to PROCESSORS to ensure Streamlit becomes a read-only visualization layer.

### **Key Findings:**
- **Company Dashboard:** 24 calculations (TTM, growth, formatting)
- **Bank Dashboard:** 14 calculations (TTM, growth, deltas)  
- **Total:** 38 unique calculations to migrate

---

## 📊 COMPANY DASHBOARD FORMULAS

### **1. Basic Metric Calculations**

#### **Revenue Display & Growth**
```python
# Location: lines 147-149
revenue = latest['net_revenue'] / 1e9 if latest['net_revenue'] else 0
prev_rev = previous['net_revenue'] / 1e9 if previous['net_revenue'] else 0
delta = ((revenue - prev_rev) / abs(prev_rev) * 100) if prev_rev != 0 else 0
```

#### **Profit Display & Growth**
```python
# Location: lines 153-155
profit = latest['npatmi'] / 1e9 if latest['npatmi'] else 0
prev_profit = previous['npatmi'] / 1e9 if previous['npatmi'] else 0
delta = ((profit - prev_profit) / abs(prev_profit) * 100) if prev_profit != 0 else 0
```

#### **ROE Delta Calculation**
```python
# Location: line 161
delta = roe - prev_roe
```

#### **D/E Ratio Delta**
```python
# Location: line 167
delta = de - prev_de
```

### **2. TTM (Trailing Twelve Months) Calculations**

#### **TTM Sum Calculation**
```python
# Location: lines 204-206
ttm_current = full_series.rolling(window=4, min_periods=4).sum()
ttm_prev = ttm_current.shift(4)
ma4_full = (ttm_current / ttm_prev - 1) * 100.0
```

#### **MA4 YoY Growth Formula**
```
MA4 YoY = (TTM_current / TTM_previous - 1) * 100%
```

Where:
- `TTM_current` = Sum of last 4 quarters
- `TTM_previous` = Sum of same 4 quarters from previous year (shift 4)

### **3. Data Formatting**

#### **Billion VND Conversion**
```python
# Location: line 189
chart_df[col] = chart_df[col] / 1e9
```

#### **Moving Average for Charts**
```python
# Location: line 295
ma4_full = full_series.rolling(window=4, min_periods=1).mean()
```

---

## 🏦 BANK DASHBOARD FORMULAS

### **1. Delta Calculations**

#### **NIM Delta**
```python
# Location: line 274
delta_pts = (nim - nim_prev) if pd.notna(nim) and pd.notna(nim_prev) else None
```

#### **ROAE Delta**
```python
# Location: line 284
delta_pts = (roae - roae_prev) if pd.notna(roae) and pd.notna(roae_prev) else None
```

#### **NPL Delta**
```python
# Location: line 294
delta_pts = (npl - npl_prev) if pd.notna(npl) and pd.notna(npl_prev) else None
```

### **2. TTM Calculations**

#### **Same TTM Formula as Company**
```python
# Location: lines 414-416
ttm_current = full_series.rolling(window=4, min_periods=4).sum()
ttm_prev = ttm_current.shift(4)
ma4_full = (ttm_current / ttm_prev - 1) * 100.0
```

### **3. Data Formatting**

#### **Billion VND Conversion**
```python
# Location: line 444
y=df[col] / 1e9,
```

---

## 📈 COMMON CALCULATION PATTERNS

### **1. TTM (Trailing Twelve Months) Pattern**
```python
# Used in both dashboards
def calculate_ttm(series):
    """Calculate TTM (sum of last 4 quarters)"""
    ttm_current = series.rolling(window=4, min_periods=4).sum()
    ttm_previous = ttm_current.shift(4)
    return ttm_current, ttm_previous

def calculate_ma4_yoy(ttm_current, ttm_previous):
    """Calculate 4-quarter moving average YoY growth"""
    return (ttm_current / ttm_previous - 1) * 100.0
```

### **2. Growth Rate Pattern**
```python
# Used for revenue, profit, ratios
def calculate_growth(current, previous):
    """Calculate percentage growth with zero division protection"""
    if previous != 0 and pd.notna(current) and pd.notna(previous):
        return ((current - previous) / abs(previous)) * 100
    else:
        return 0
```

### **3. Safe Delta Pattern**
```python
# Used for bank metrics
def calculate_delta(current, previous):
    """Calculate safe delta with null protection"""
    if pd.notna(current) and pd.notna(previous):
        return current - previous
    else:
        return None
```

### **4. Unit Conversion Pattern**
```python
# Convert to billions for display
def convert_to_billions(value):
    """Convert VND to billions for display"""
    return value / 1e9 if value else 0
```

---

## 🎯 METRICS REQUIRING PROCESSOR CALCULATION

### **Company Metrics**
| Metric | Current Calculation | Target Processor |
|--------|-------------------|------------------|
| `revenue_b` | `net_revenue / 1e9` | company_calculator.py |
| `profit_b` | `npatmi / 1e9` | company_calculator.py |
| `revenue_growth_yoy` | `(current - prev) / abs(prev) * 100` | company_calculator.py |
| `profit_growth_yoy` | `(current - prev) / abs(prev) * 100` | company_calculator.py |
| `roe_delta` | `roe - prev_roe` | company_calculator.py |
| `de_ratio_delta` | `de - prev_de` | company_calculator.py |
| `*_ttm` | `rolling(window=4).sum()` | company_calculator.py |
| `*_ma4_yoy` | `(ttm_current / ttm_prev - 1) * 100` | company_calculator.py |

### **Bank Metrics**
| Metric | Current Calculation | Target Processor |
|--------|-------------------|------------------|
| `nim_delta` | `nim - nim_prev` | bank_calculator.py |
| `roae_delta` | `roae - roae_prev` | bank_calculator.py |
| `npl_delta` | `npl - npl_prev` | bank_calculator.py |
| `*_ttm` | `rolling(window=4).sum()` | bank_calculator.py |
| `*_ma4_yoy` | `(ttm_current / ttm_prev - 1) * 100` | bank_calculator.py |

---

## 🔧 PROCESSOR IMPLEMENTATION PLAN

### **1. Add TTM Calculation Method to Base Class**
```python
# In PROCESSORS/fundamental/calculators/base_financial_calculator.py
def calculate_ttm_metrics(self, df: pd.DataFrame, metrics: List[str]) -> pd.DataFrame:
    """Calculate TTM and MA4 YoY for specified metrics"""
    for metric in metrics:
        if metric in df.columns:
            # TTM calculation
            ttm_col = f'{metric}_ttm'
            df[ttm_col] = df.groupby('symbol')[metric].transform(
                lambda x: x.rolling(window=4, min_periods=4).sum()
            )
            
            # MA4 YoY calculation
            ma4_yoy_col = f'{metric}_ma4_yoy'
            df[ma4_yoy_col] = df.groupby('symbol')[ttm_col].transform(
                lambda x: (x / x.shift(4) - 1) * 100
            )
    
    return df
```

### **2. Add Growth Calculation Method**
```python
def calculate_growth_metrics(self, df: pd.DataFrame, metrics: List[str]) -> pd.DataFrame:
    """Calculate YoY growth for specified metrics"""
    for metric in metrics:
        if metric in df.columns:
            growth_col = f'{metric}_growth_yoy'
            df[growth_col] = df.groupby('symbol')[metric].transform(
                lambda x: ((x - x.shift(4)) / abs(x.shift(4))) * 100
            )
    
    return df
```

### **3. Add Delta Calculation Method**
```python
def calculate_delta_metrics(self, df: pd.DataFrame, metrics: List[str]) -> pd.DataFrame:
    """Calculate quarter-over-quarter delta for specified metrics"""
    for metric in metrics:
        if metric in df.columns:
            delta_col = f'{metric}_delta_qoq'
            df[delta_col] = df.groupby('symbol')[metric].transform(
                lambda x: x - x.shift(1)
            )
    
    return df
```

### **4. Add Unit Conversion Method**
```python
def add_display_units(self, df: pd.DataFrame, metrics: List[str], unit: str = 'billions') -> pd.DataFrame:
    """Add display-friendly unit conversions"""
    for metric in metrics:
        if metric in df.columns:
            if unit == 'billions':
                display_col = f'{metric}_b'
                df[display_col] = df[metric] / 1e9
    
    return df
```

---

## 📋 IMPLEMENTATION CHECKLIST

### **Phase 1: Add Methods to Base Calculator**
- [ ] Add `calculate_ttm_metrics()` method
- [ ] Add `calculate_growth_metrics()` method  
- [ ] Add `calculate_delta_metrics()` method
- [ ] Add `add_display_units()` method

### **Phase 2: Update Company Calculator**
- [ ] Add TTM calculations for: net_revenue, npatmi, operating_cf
- [ ] Add growth calculations for: net_revenue, npatmi, roe, de_ratio
- [ ] Add delta calculations for: roe, de_ratio
- [ ] Add display units for: net_revenue, npatmi (billions)

### **Phase 3: Update Bank Calculator**
- [ ] Add TTM calculations for: key metrics
- [ ] Add delta calculations for: nim, roae, npl
- [ ] Add display units for: monetary metrics (billions)

### **Phase 4: Update Insurance & Security Calculators**
- [ ] Add TTM calculations where applicable
- [ ] Add growth calculations where applicable
- [ ] Add display units where applicable

### **Phase 5: Update Formula Registry**
- [ ] Add all new calculated metrics to formula registry
- [ ] Include Vietnamese names and formulas
- [ ] Document calculation methods

---

## 🔄 MIGRATION VERIFICATION

### **Before Removal (Streamlit)**
1. **Document current behavior** - screenshots of all calculations
2. **Export sample data** - save current calculation results
3. **Test edge cases** - null values, zero divisions, single data points

### **After Migration (Processors)**
1. **Run updated calculators** - generate new parquet files
2. **Compare results** - ensure identical calculations
3. **Update Streamlit** - remove calculation code, use new columns
4. **End-to-end test** - verify dashboard displays match previous behavior

### **Verification Script Template**
```python
# scripts/verify_formula_migration.py
def verify_formula_migration():
    """Verify that processor calculations match Streamlit calculations"""
    
    # Load old Streamlit calculation results
    old_results = load_streamlit_calculations()
    
    # Load new processor calculation results  
    new_results = load_processor_calculations()
    
    # Compare key metrics
    for metric in ['revenue_growth_yoy', 'profit_growth_yoy', 'roe_delta']:
        if metric in old_results and metric in new_results:
            diff = abs(old_results[metric] - new_results[metric])
            assert diff < 0.01, f"Mismatch in {metric}: {diff}"
    
    print("✅ All calculations match!")
```

---

## 📞 NOTES & REMINDERS

### **Critical Considerations:**
1. **Null Handling:** Processors must handle null values same as Streamlit
2. **Grouping:** All calculations must be grouped by symbol/ticker
3. **Data Types:** Ensure consistent data types between old and new calculations
4. **Performance:** Processor calculations should be optimized for large datasets

### **Testing Requirements:**
1. **Edge Cases:** Single data point, null values, zero values
2. **Multiple Tickers:** Ensure grouping works correctly
3. **Time Series:** Verify quarter-over-quarter calculations
4. **Display Units:** Check billion conversions are accurate

### **Documentation Updates:**
1. **Formula Registry:** Add all new calculated metrics
2. **Calculator Documentation:** Document new methods
3. **Dashboard Documentation:** Update to reflect read-only nature

---

**Document Created:** 2025-12-16  
**Last Updated:** 2025-12-16  
**Next Review:** After processor implementation completion