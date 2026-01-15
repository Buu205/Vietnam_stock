# Data Loading Edge Cases Verification

**Review Date:** 2026-01-15
**Reviewer:** Code Review Agent
**Files Reviewed:**
- `WEBAPP/services/base_service.py`
- `MCP_SERVER/bsc_mcp/services/data_loader.py`

---

## Edge Case Analysis

### 1. File Not Found

**WEBAPP/services/base_service.py:**
- ✅ **Handled** (Lines 161-166)
- Raises `FileNotFoundError` with informative message
- Includes service name, data source, file path
- Error message guides user to check configuration

**MCP_SERVER/bsc_mcp/services/data_loader.py:**
- ✅ **Handled** (Lines 84-88)
- Raises `FileNotFoundError` with path and remediation
- Message directs user to run data pipeline
- Special case for `get_ohlcv_raw()`: Returns empty DataFrame instead (lines 378-380)

**Recommendation:** MCP inconsistency - `get_ohlcv_raw()` returns empty DataFrame while other methods raise. Consider standardizing.

---

### 2. Empty DataFrame Returned

**WEBAPP/services/base_service.py:**
- ❌ **Unhandled**
- `pd.read_parquet()` succeeds on empty file (lines 169)
- No validation for `df.empty` after load
- Downstream code may fail on empty data

**MCP_SERVER/bsc_mcp/services/data_loader.py:**
- ❌ **Unhandled** (except `get_ohlcv_raw()`)
- `_load_cached()` doesn't check if DataFrame is empty after read (line 93)
- Logs row count (line 96) but doesn't validate > 0
- `get_ohlcv_raw()` handles empty case (lines 389-399)

**Recommendation:** Add empty DataFrame check with warning:
```python
if df.empty:
    logger.warning(f"Loaded empty DataFrame from {path}")
```

---

### 3. Missing Expected Columns

**WEBAPP/services/base_service.py:**
- ⚠️ **Partial** (Lines 177-193)
- Schema validation via `_validate_schema()`
- Only **logs warning**, doesn't raise
- Allows code to proceed with missing columns
- Warning message lists missing columns

**MCP_SERVER/bsc_mcp/services/data_loader.py:**
- ❌ **Unhandled**
- No schema validation after load
- Relies on upstream parquet file correctness
- Caller responsible for column validation

**Recommendation (MCP):** Add optional schema validation parameter to `_load_cached()`.

---

### 4. Cache TTL Expiration Race Condition

**WEBAPP/services/base_service.py:**
- ✅ **Not Applicable**
- No caching logic in base service
- Delegates caching to Streamlit's `@st.cache_data`

**MCP_SERVER/bsc_mcp/services/data_loader.py:**
- ✅ **Handled** (Lines 49-57)
- `_is_cache_valid()` checks both existence and timestamp
- Uses simple elapsed time comparison
- No TOCTOU issue (single-threaded MCP server)

**Note:** Single-threaded design prevents race conditions in current implementation.

---

### 5. Cache Key Collision

**WEBAPP/services/base_service.py:**
- ✅ **Not Applicable**
- No internal caching mechanism

**MCP_SERVER/bsc_mcp/services/data_loader.py:**
- ✅ **Handled** by design
- Each method uses unique hardcoded cache key (e.g., `"company_fundamentals"`, `"bank_fundamentals"`)
- Keys are string literals, not computed
- No dynamic key generation that could collide

**Note:** Cache keys are manually maintained. Risk if copy-paste error reuses key.

---

### 6. DATA_SOURCE Not Defined

**WEBAPP/services/base_service.py:**
- ✅ **Handled** (Lines 109-112)
- `get_data_path()` checks if `DATA_SOURCE` is empty string
- Raises `ValueError` with clear message
- Error includes service class name

**MCP_SERVER/bsc_mcp/services/data_loader.py:**
- ✅ **Not Applicable**
- Not using inheritance pattern
- All data sources hardcoded in config

---

## Summary by Severity

### Critical Issues (Fix Immediately)
None.

### High Priority
1. **Empty DataFrame handling** (both files)
   - Add validation after `pd.read_parquet()`
   - Log warning if empty
   - Consider raising exception for critical data sources

2. **MCP inconsistency** - `get_ohlcv_raw()` returns empty DataFrame, others raise
   - Standardize error handling across methods

### Medium Priority
1. **Missing columns handling** (MCP)
   - Add schema validation similar to WEBAPP base service
   - Make validation opt-in via parameter

2. **Cache key collision risk** (MCP)
   - Use Enum or constants for cache keys
   - Add runtime collision detection in `__init__`

### Low Priority
1. **Error message improvement** (both files)
   - Add suggestion for common fixes in FileNotFoundError

---

## Positive Observations

- WEBAPP base service has good error context (service name, data source)
- MCP uses informative logging with timing metrics
- Both handle file-not-found consistently
- MCP TTL cache logic is race-condition-free

---

## Recommended Actions

1. **Add empty DataFrame validation** (both files):
```python
df = pd.read_parquet(path)
if df.empty:
    logger.warning(f"Empty data loaded from {path}")
```

2. **Standardize MCP error handling**:
   - Make `get_ohlcv_raw()` behavior consistent
   - Or document why it's different

3. **Add schema validation to MCP**:
```python
def _load_cached(self, cache_key, relative_path, expected_columns=None):
    ...
    if expected_columns and not set(expected_columns).issubset(df.columns):
        missing = set(expected_columns) - set(df.columns)
        logger.warning(f"Missing columns in {cache_key}: {missing}")
```

4. **Use constants for cache keys** (MCP):
```python
class CacheKeys:
    COMPANY_FUNDAMENTALS = "company_fundamentals"
    BANK_FUNDAMENTALS = "bank_fundamentals"
    # ...
```

---

## Unresolved Questions

1. Should empty DataFrames raise exceptions or just log warnings?
2. Should MCP `get_ohlcv_raw()` match other methods' error behavior?
3. What is acceptable minimum row count for "valid" data?
