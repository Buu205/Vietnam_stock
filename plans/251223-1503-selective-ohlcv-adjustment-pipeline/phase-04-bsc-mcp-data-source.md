# Phase 04: BSC MCP Data Source Update

## Objective

Ensure BSC MCP reads updated data after OHLCV adjustment refresh.

---

## Current State

```python
# MCP_SERVER/bsc_mcp/services/data_loader.py
class DataLoader:
    def get_technical_basic(self) -> pd.DataFrame:
        """Returns cached basic_data.parquet"""
        return pd.read_parquet(self.paths['technical_basic'])
        # Reads: DATA/processed/technical/basic_data.parquet
```

**Problem:** After selective OHLCV refresh, basic_data.parquet is updated. But BSC MCP might have cached old data.

---

## Solution A: Cache Invalidation (Recommended)

After selective cascade, BSC MCP should reload data on next request.

**Current behavior:** DataLoader uses `@lru_cache` or stores in-memory cache.

**Solution:** Add method to clear cache after updates.

### Add to DataLoader

```python
def clear_cache(self):
    """Clear all cached DataFrames. Call after data updates."""
    self._cache = {}
    logger.info("DataLoader cache cleared")

def get_technical_basic(self, force_reload: bool = False) -> pd.DataFrame:
    """
    Get technical indicators data.

    Args:
        force_reload: Force reload from disk (bypass cache)
    """
    cache_key = 'technical_basic'

    if force_reload or cache_key not in self._cache:
        self._cache[cache_key] = pd.read_parquet(self.paths['technical_basic'])

    return self._cache[cache_key]
```

---

## Solution B: Add Raw OHLCV Reader (Optional)

For real-time access to OHLCV without waiting for pipeline:

### Add to DataLoader

```python
def get_ohlcv_raw(
    self,
    ticker: str = None,
    limit: int = 60
) -> pd.DataFrame:
    """
    Read directly from raw OHLCV parquet.

    Args:
        ticker: Optional ticker filter
        limit: Number of recent days to return

    Returns:
        DataFrame with raw OHLCV data
    """
    ohlcv_path = self.base_path / "raw" / "ohlcv" / "OHLCV_mktcap.parquet"

    if not ohlcv_path.exists():
        logger.warning(f"OHLCV file not found: {ohlcv_path}")
        return pd.DataFrame()

    df = pd.read_parquet(ohlcv_path)
    df['date'] = pd.to_datetime(df['date'])

    if ticker:
        df = df[df['symbol'] == ticker.upper()]

    # Get most recent N days
    if not df.empty:
        df = df.sort_values('date', ascending=False).head(limit * (df['symbol'].nunique() if not ticker else 1))
        df = df.sort_values(['symbol', 'date'])

    return df
```

### Add MCP Tool (Optional)

```python
# MCP_SERVER/bsc_mcp/tools/technical_tools.py

@mcp.tool()
def bsc_get_ohlcv_raw(
    ticker: str,
    limit: int = 60
) -> str:
    """
    Get raw OHLCV data directly (bypasses processed pipeline).

    Use when: Need most recent OHLCV after adjustment refresh.

    Args:
        ticker: Stock symbol (e.g., "VCB")
        limit: Number of days to return (default: 60)

    Returns:
        Markdown table with OHLCV data
    """
    df = data_loader.get_ohlcv_raw(ticker=ticker, limit=limit)

    if df.empty:
        return f"No OHLCV data found for {ticker}"

    # Format output
    df = df[['date', 'open', 'high', 'low', 'close', 'volume', 'market_cap']]
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')

    return df.tail(limit).to_markdown(index=False)
```

---

## Implementation Steps

### Step 1: Update DataLoader

File: `MCP_SERVER/bsc_mcp/services/data_loader.py`

1. Add `_cache` dict to `__init__`
2. Add `clear_cache()` method
3. Add `force_reload` param to data getter methods
4. Add `get_ohlcv_raw()` method

### Step 2: Update ohlcv_adjustment_detector.py

After selective cascade, trigger cache clear:

```python
def _cascade_refresh_selective(self, symbols: List[str], n_sessions: int = 500):
    ...
    # At end:
    self._notify_mcp_cache_clear()

def _notify_mcp_cache_clear(self):
    """Signal MCP server to clear cache."""
    # Option 1: Write marker file
    marker = Path("DATA/.cache_invalidated")
    marker.touch()
    logger.info("Cache invalidation marker created")

    # Option 2: Direct import (if in same process)
    # try:
    #     from MCP_SERVER.bsc_mcp.services.data_loader import data_loader
    #     data_loader.clear_cache()
    # except ImportError:
    #     pass
```

### Step 3: MCP DataLoader reads marker

```python
def get_technical_basic(self) -> pd.DataFrame:
    marker = self.base_path / ".cache_invalidated"

    if marker.exists():
        self.clear_cache()
        marker.unlink()
        logger.info("Cache invalidated by external update")

    return self._get_cached('technical_basic')
```

---

## Validation Checklist

- [ ] After selective refresh, BSC MCP returns updated data
- [ ] Cache invalidation marker works across processes
- [ ] `get_ohlcv_raw()` returns correct ticker data
- [ ] No stale data returned after OHLCV refresh

---

## Test Commands

```bash
# 1. Run selective refresh
python ohlcv_adjustment_detector.py --symbols CTG --refresh --cascade-selective

# 2. Check cache invalidation marker
ls -la DATA/.cache_invalidated

# 3. Query MCP tool (should return updated data)
# Via Claude Code with BSC MCP connected:
# bsc_get_technical_indicators("CTG")
```

---

## Dependencies

- Phase 03: Orchestrator integration complete
- BSC MCP server accessible
