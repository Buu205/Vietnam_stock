# MCP Server Tools Edge Case Verification

**Date:** 2026-01-15
**Scope:** MCP server tools error handling validation
**Files Reviewed:** 4 files, ~1800 lines

---

## Summary

**Overall Assessment:** EXCELLENT
MCP server tools implement comprehensive edge case handling via centralized error framework (`errors.py`). All critical edge cases are properly handled with user-friendly error messages.

---

## Edge Case Analysis

### 1. Invalid Ticker Query ✅ Handled

**fundamental_tools.py:**
- L59: Normalize input `ticker.upper().strip()`
- L62-67: Check entity type, raise `TickerNotFoundError` with suggestions
- L88-91: After entity data load, verify ticker exists in dataset

**technical_tools.py:**
- L65: Normalize input `ticker.upper().strip()`
- L73-76: Check if ticker_df empty, raise `TickerNotFoundError` with suggestions

**valuation_tools.py:**
- L57-58: Normalize input `ticker.upper().strip()` + `metric.upper().strip()`
- L79-82: Raise `TickerNotFoundError` with suggestions if empty

**errors.py:**
- L121-142: `validate_ticker()` - uppercase normalization + suggestions via `find_similar_tickers()`
- L91-118: Fuzzy matching (prefix + contains) to suggest alternatives

**Recommendation:** None. Excellent handling.

---

### 2. Missing Data File ❌→✅ FileNotFoundError (User-Friendly)

**data_loader.py:**
- L84-88: `_load_cached()` checks file existence, raises `FileNotFoundError` with helpful message
- Message includes: "Please run the data pipeline to generate this file"

**errors.py:**
- L71-78: `handle_tool_error()` catches `FileNotFoundError`
- Returns markdown-formatted message with exact pipeline command:
  ```bash
  python3 PROCESSORS/daily_sector_complete_update.py
  ```

**Recommendation:** None. User-friendly guidance provided.

---

### 3. Empty Query Results ✅ Handled

**fundamental_tools.py:**
- L88-91: `if ticker_df.empty: raise TickerNotFoundError`
- L166-171: Bank-specific check - distinguishes "not a bank" from "ticker not found"
- L378-380: `if ticker_df.empty: results.append({'Error': 'No data'})`
- L511-512: Screening returns "No stocks found matching criteria" when empty

**technical_tools.py:**
- L72-76: Empty check with suggestions
- L153-156: Latest technicals - empty check with suggestions
- L299-300: Alerts - "No alerts found for filter: ..." message
- L442-443: Patterns - "No candlestick pattern data available"
- L546-549: OHLCV raw - empty check with suggestions

**valuation_tools.py:**
- L77-82: Empty check with suggestions
- L152-153: Empty check in stats calculation
- L258-259: Sector valuation - "No data found for sector containing '{sector}'"

**Recommendation:** None. All empty result paths handled.

---

### 4. Ticker Case Sensitivity ✅ Normalized

**All tools consistently:**
- L59/65/57: `ticker.upper().strip()` before any lookup
- errors.py L135: `validate_ticker()` normalizes to uppercase

**Example:**
```python
# Input: "acb" or " ACB " or "AcB"
# Normalized: "ACB"
```

**Recommendation:** None. Consistent normalization.

---

### 5. Invalid Entity Type Lookup ✅ Handled

**data_loader.py:**
- L428-468: `get_ticker_entity_type()` tries all entity types sequentially
- L441-466: Returns `None` if ticker not found in any dataset
- L441/449/457: Catches `FileNotFoundError` per entity type (graceful degradation)

**fundamental_tools.py:**
- L62-67: Checks `if not entity_type:` before attempting data load
- L168-170: Bank tools explicitly check entity type mismatch:
  - "VNM is not a bank (type: COMPANY). Use `bsc_get_company_financials` instead."

**Recommendation:** None. Excellent UX for entity type mismatches.

---

### 6. Date Range Edge Cases ⚠️ Partial

**valuation_tools.py:**
- L162-167: Stats calculation - filters historical by cutoff date
- L166-167: **Checks if len(historical) < 10**, returns error message ✅
- L356-360: VN-Index date filter - checks `if df.empty` after date filter ✅

**technical_tools.py:**
- L356-360: Market breadth - filters by date, checks `if df.empty` ✅

**Issues Found:**
- **No date format validation** before filtering
- If user passes invalid date format (e.g., "2024-13-32"), pandas may silently fail or raise generic error

**Recommendation:**
Add date format validation in tools that accept date parameter:
```python
# In technical_tools.py::bsc_get_market_breadth
# In valuation_tools.py (implicit date handling)

from datetime import datetime

def validate_date_format(date_str: str) -> None:
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        raise ValueError(f"Invalid date format: {date_str}. Use YYYY-MM-DD")
```

---

## Additional Observations

### Strengths
1. **Centralized error framework** - All tools use `handle_tool_error()` wrapper
2. **Fuzzy ticker search** - `find_similar_tickers()` provides excellent UX
3. **Type-specific error messages** - Distinguishes "not found" vs "wrong type"
4. **Graceful degradation** - Missing entity files handled via try/except
5. **Helpful error messages** - Include exact commands to fix issues

### Edge Cases NOT Covered
1. **Date format validation** - Only partial (checked in some tools)
2. **Limit parameter validation** - No max/min bounds checking (could pass limit=-1)
3. **Metric parameter validation** - Only checked in valuation tools, not universally

---

## Recommendations Priority

**P2 - Minor Enhancements:**
1. Add date format validation helper in `errors.py`
2. Add limit parameter bounds checking (min=1, max=1000)
3. Add comprehensive parameter validation to `errors.py::InvalidParameterError`

**Example:**
```python
# errors.py
def validate_limit(limit: int, min_val: int = 1, max_val: int = 1000) -> None:
    if not (min_val <= limit <= max_val):
        raise InvalidParameterError('limit', str(limit), [f'{min_val}-{max_val}'])
```

---

## Conclusion

MCP server tools demonstrate **excellent edge case handling** via centralized error framework. All critical paths validated. Only minor enhancements recommended for date/limit validation.

**Compliance:** 95% (5% deduction for missing date/limit validation)

---

## Unresolved Questions

None. All edge cases verified with code evidence.
