# MCP Server Inventory Report

**Date:** January 4, 2026
**Status:** Complete
**Server Count:** 1
**Total Tools:** 28

---

## Overview

Vietnam Dashboard has **1 primary MCP server** configured: **BSC MCP Server** with **28 tools** across 7 categories.

### Configuration Location
- **Project Config:** `.mcp.json`
- **Example Config:** `.claude/.mcp.json.example`
- **Server Implementation:** `MCP_SERVER/bsc_mcp/`

---

## MCP Server Details

### Server: BSC (Vietnam Stock Market Data)

**Status:** Active
**Type:** stdio (Python-based)
**Command:** `python3 -m bsc_mcp.server`
**CWD:** `MCP_SERVER/`

**Environment Variables:**
- `PYTHONPATH`: Project root + MCP_SERVER directory
- `DATA_ROOT`: `DATA/` directory (processed data)

---

## Tool Categories & Inventory

### 1. Discovery Tools (5 tools)

Tools for discovering tickers, sectors, and metadata.

| Tool | Purpose | Key Parameters |
|------|---------|-----------------|
| `bsc_list_tickers` | List available tickers with filtering | `entity_type`, `sector`, `limit` |
| `bsc_get_ticker_info` | Get detailed info for a ticker | `ticker` |
| `bsc_list_sectors` | List all sectors | `entity_type` |
| `bsc_search_tickers` | Search tickers by keyword | `query`, `limit` |
| `bsc_get_peers` | Get peer companies in same sector | `ticker`, `limit`, `exclude_self` |

**Use Cases:**
- Find all banks: `bsc_list_tickers(entity_type="BANK")`
- Get banking sector tickers: `bsc_list_tickers(sector="Ngân hàng")`
- Find peers for ACB: `bsc_get_peers("ACB")`
- Search for tech stocks: `bsc_search_tickers("công nghệ")`

---

### 2. Fundamental Tools (5 tools)

Tools for querying company financial metrics (ROE, profit margins, growth rates).

| Tool | Purpose | Key Parameters |
|------|---------|-----------------|
| `bsc_get_company_financials` | Get financials for any entity type | `ticker`, `period`, `limit` |
| `bsc_get_bank_financials` | Get bank-specific metrics | `ticker`, `period`, `limit` |
| `bsc_get_latest_fundamentals` | Get latest quarter data | `ticker` |
| `bsc_compare_fundamentals` | Compare metrics across tickers | `tickers`, `metrics` |
| `bsc_screen_fundamentals` | Screen stocks by criteria | `roe_min`, `roe_max`, `pe_max`, `sector`, `entity_type` |

**Supported Periods:** "Quarterly" (default) or "Yearly"

**Data Points:**
- Companies: revenue, net_income, roe, roa, gross_margin, net_margin
- Banks: nii, ppop, npatmi, roe, roa, nim, npl_ratio, casa_ratio, cir, car
- Insurance: net_revenue, npatmi, roe, roa, combined_ratio, claims_ratio
- Securities: net_revenue, npatmi, roe, roa, asset_ratios

**Use Cases:**
- Get VNM quarterly data: `bsc_get_company_financials("VNM")`
- Get VCB yearly data: `bsc_get_company_financials("VCB", period="Yearly")`
- Compare 4 banks: `bsc_compare_fundamentals("VCB,ACB,TCB,MBB")`
- Find stocks with ROE > 20%: `bsc_screen_fundamentals(roe_min=20)`

---

### 3. Technical Tools (6 tools)

Tools for OHLCV data, technical indicators, and trading alerts.

| Tool | Purpose | Key Parameters |
|------|---------|-----------------|
| `bsc_get_technical_indicators` | Get OHLCV + indicators (SMA, EMA, RSI, MACD, BB, OBV) | `ticker`, `limit`, `indicators` |
| `bsc_get_latest_technicals` | Snapshot of latest indicator values | `ticker` |
| `bsc_get_technical_alerts` | Trading alerts (breakouts, MA crossovers, volume) | `ticker`, `alert_type`, `limit` |
| `bsc_get_market_breadth` | Market breadth (Advance/Decline, McClellan) | `date` |
| `bsc_get_candlestick_patterns` | Candlestick pattern detection | `ticker`, `pattern`, `signal`, `limit` |
| `bsc_get_ohlcv_raw` | Raw OHLCV data for external analysis | `ticker`, `limit`, `include_value` |

**Indicators Available:**
- Moving Averages: SMA (20/50/200), EMA (20/50)
- Momentum: RSI (14), MACD
- Volatility: Bollinger Bands
- Volume: OBV, CMF, MFI

**Patterns Detected:**
- doji, hammer, hanging_man, engulfing, three_white_soldiers, evening_star, inverted_hammer, shooting_star

**Alert Types:**
- breakout (price breakout above resistance)
- ma_crossover (golden cross / death cross)
- volume_spike (unusual volume activity)
- patterns (candlestick formations)

**Use Cases:**
- Get FPT technical data with all indicators: `bsc_get_technical_indicators("FPT")`
- Get VNM RSI and MACD only: `bsc_get_technical_indicators("VNM", indicators="rsi,macd")`
- Get all breakout alerts: `bsc_get_technical_alerts(alert_type="breakout")`
- Get latest FPT technicals: `bsc_get_latest_technicals("FPT")`

---

### 4. Valuation Tools (5 tools)

Tools for PE, PB, PS, EV/EBITDA valuation metrics.

| Tool | Purpose | Key Parameters |
|------|---------|-----------------|
| `bsc_get_ticker_valuation` | Historical valuation data | `ticker`, `metric`, `limit` |
| `bsc_get_valuation_stats` | Valuation statistics (mean, percentile, z-score) | `ticker`, `metric`, `years` |
| `bsc_get_sector_valuation` | Sector-level valuation comparison | `sector`, `metric` |
| `bsc_compare_valuations` | Compare valuations across tickers | `tickers`, `metric` |
| `bsc_get_vnindex_valuation` | VN-Index valuation with historical bands | `limit` |

**Metrics:** PE, PB, PS, EV_EBITDA

**Assessment:** Valuation statistics include cheap/expensive assessment based on historical percentiles.

**Use Cases:**
- Get ACB PE history: `bsc_get_ticker_valuation("ACB")`
- Get VNM PB history: `bsc_get_ticker_valuation("VNM", metric="PB")`
- Compare bank valuations: `bsc_compare_valuations("VCB,ACB,TCB,MBB")`
- Get banking sector valuation: `bsc_get_sector_valuation(sector="Ngân hàng")`
- Get ACB PE statistics (5-year): `bsc_get_valuation_stats("ACB", years=5)`

---

### 5. Forecast Tools (3 tools)

Tools for BSC analyst forecasts and upside potential.

| Tool | Purpose | Key Parameters |
|------|---------|-----------------|
| `bsc_get_bsc_forecast` | Get BSC analyst forecast for ticker | `ticker` |
| `bsc_list_bsc_forecasts` | List all stocks with forecasts | `rating`, `sector`, `sort_by`, `limit` |
| `bsc_get_top_upside_stocks` | Get stocks with highest upside potential | `n`, `sector`, `min_upside` |

**Data Returned:**
- Target price
- Rating (BUY/HOLD/SELL)
- EPS forecasts
- Growth estimates
- Upside percentage

**Sorting Options:** "upside" (default), "pe", "ticker"

**Use Cases:**
- Get ACB forecast: `bsc_get_bsc_forecast("ACB")`
- Get all BUY recommendations: `bsc_list_bsc_forecasts(rating="BUY")`
- Get top 5 banking stocks by upside: `bsc_get_top_upside_stocks(n=5, sector="Ngân hàng")`
- Get stocks with >20% upside: `bsc_get_top_upside_stocks(min_upside=20)`

---

### 6. Sector Tools (3 tools)

Tools for sector-level FA/TA scores and signals.

| Tool | Purpose | Key Parameters |
|------|---------|-----------------|
| `bsc_get_sector_scores` | Get FA/TA scores and trading signals | `sector`, `signal` |
| `bsc_get_sector_history` | Historical sector scores over time | `sector`, `limit` |
| `bsc_compare_sectors` | Compare metrics across sectors | `sectors`, `metrics` |

**Signals:** "MUA" (BUY), "BÁN" (SELL), "GIỮ" (HOLD)

**Metrics Available:**
- fa_score (Fundamental Analysis score)
- ta_score (Technical Analysis score)
- combined_score
- pe_ratio, pb_ratio

**Use Cases:**
- Get all sector scores: `bsc_get_sector_scores()`
- Get only BUY signals: `bsc_get_sector_scores(signal="MUA")`
- Get banking sector history (30 days): `bsc_get_sector_history("Ngân hàng", limit=30)`
- Compare banking vs real estate: `bsc_compare_sectors(sectors="Ngân hàng,Bất động sản")`

---

### 7. Macro Tools (3 tools)

Tools for macro-economic and commodity data.

| Tool | Purpose | Key Parameters |
|------|---------|-----------------|
| `bsc_get_macro_data` | Interest rates, FX, bond yields | `indicator`, `limit` |
| `bsc_get_commodity_prices` | Gold, oil, steel, rubber prices | `commodity`, `limit` |
| `bsc_get_macro_overview` | Summary of current macro indicators | None |

**Macro Indicators:**
- deposit_rate (bank deposit rates)
- lending_rate (lending rates)
- usd_vnd (USD/VND exchange rate)
- gov_bond_10y (10-year government bond yield)

**Commodities:**
- gold (gold prices)
- oil / oil_brent (Brent oil)
- steel (steel prices)
- rubber (rubber prices)

**Use Cases:**
- Get all macro data: `bsc_get_macro_data()`
- Get FX rates only: `bsc_get_macro_data(indicator="usd_vnd")`
- Get gold prices: `bsc_get_commodity_prices(commodity="gold")`
- Get macro summary: `bsc_get_macro_overview()`

---

## Data Sources & Locations

All tools read from `DATA/processed/` directory:

### Fundamental Data
- `DATA/processed/fundamental/company/company_financial_metrics.parquet`
- `DATA/processed/fundamental/bank/bank_financial_metrics.parquet`
- `DATA/processed/fundamental/insurance/insurance_financial_metrics.parquet`
- `DATA/processed/fundamental/security/security_financial_metrics.parquet`

### Technical Data
- `DATA/processed/technical/basic_data.parquet` (OHLCV + indicators)

### Valuation Data
- `DATA/processed/valuation/pe/pe_historical.parquet`
- `DATA/processed/valuation/pb/pb_historical.parquet`
- `DATA/processed/valuation/ps/ps_historical.parquet`
- `DATA/processed/valuation/ev_ebitda/ev_ebitda_historical.parquet`

### Forecast Data
- `DATA/processed/forecast/bsc/individual_forecast.parquet`

### Sector Analysis
- `DATA/processed/fundamental/sector_fundamentals.parquet`
- `DATA/processed/valuation/sector_valuation.parquet`

### Macro & Commodity
- `DATA/processed/macro/macro_commodity.parquet`

---

## Implementation Details

### Server Architecture
- **Framework:** FastMCP (Model Context Protocol)
- **Language:** Python 3.13
- **Entry Point:** `MCP_SERVER/bsc_mcp/server.py`
- **Tool Modules:** `MCP_SERVER/bsc_mcp/tools/` (7 modules)

### Tool Registration Pattern
```python
# Each tool module has a register() function
from bsc_mcp.tools import discovery_tools
discovery_tools.register(mcp)  # Registers all discovery tools
```

### Data Access Pattern
```python
# All tools use centralized DataLoader
from bsc_mcp.services.data_loader import get_data_loader
loader = get_data_loader()
df = loader.get_company_fundamentals()
```

### Error Handling
- TickerNotFoundError: Returns suggestions if ticker invalid
- FileNotFoundError: Graceful fallback to alternative data sources
- Format validation: All outputs as Markdown tables

---

## Quick Reference: Common Use Cases

### Investment Research
```
1. Discover: bsc_list_tickers(sector="Ngân hàng")
2. Fundamentals: bsc_get_company_financials("ACB", period="Yearly")
3. Valuation: bsc_get_ticker_valuation("ACB", metric="PE")
4. Forecast: bsc_get_bsc_forecast("ACB")
5. Technical: bsc_get_technical_indicators("ACB")
```

### Sector Analysis
```
1. Sector Scores: bsc_get_sector_scores()
2. Valuation: bsc_get_sector_valuation()
3. Compare: bsc_compare_sectors()
4. History: bsc_get_sector_history("Ngân hàng")
```

### Trading Signals
```
1. Technical Alerts: bsc_get_technical_alerts(alert_type="breakout")
2. Patterns: bsc_get_candlestick_patterns(signal="BULLISH")
3. Market Breadth: bsc_get_market_breadth()
4. Latest Technicals: bsc_get_latest_technicals("FPT")
```

### Screening
```
1. By Fundamentals: bsc_screen_fundamentals(roe_min=20, pe_max=10)
2. By Upside: bsc_get_top_upside_stocks(n=10, min_upside=15)
3. By Rating: bsc_list_bsc_forecasts(rating="BUY")
```

### Macro Monitoring
```
1. Macro Overview: bsc_get_macro_overview()
2. FX Rates: bsc_get_macro_data(indicator="usd_vnd")
3. Commodity Prices: bsc_get_commodity_prices()
```

---

## Summary

**Total Tools Available:** 28

| Category | Count | Status |
|----------|-------|--------|
| Discovery | 5 | Active |
| Fundamental | 5 | Active |
| Technical | 6 | Active |
| Valuation | 5 | Active |
| Forecast | 3 | Active |
| Sector | 3 | Active |
| Macro | 3 | Active |

**All tools are production-ready and actively used by the dashboard and Claude Code for stock market analysis.**

---

# BRAINSTORM: MCP Scale Up Plan

**Date:** January 4, 2026
**Status:** Draft - Pending Approval
**Author:** Claude Code Brainstormer

---

## Problem Statement

Current BSC MCP (28 tools) works well but needs:
1. **Performance** - Faster response, better caching, concurrent handling
2. **Data Coverage** - VCI forecast, consensus data, more sources
3. **New Tools** - AI analysis, backtesting, portfolio tracking
4. **Integration** - Deeper Claude Code/Cursor/Antigravity integration
5. **OneDrive Sync** - Auto-sync Excel/PDF files from corporate OneDrive

---

## Part A: BSC MCP Scale Up

### A1. Performance Optimization

**Current State:**
- TTL cache: 5 minutes (300s)
- Singleton DataLoader with in-memory cache
- No async processing
- No concurrent request handling

**Proposed Improvements:**

| Improvement | Effort | Impact | Priority |
|-------------|--------|--------|----------|
| Async data loading | Medium | High | P1 |
| Redis/file-based cache | Medium | High | P1 |
| Lazy loading per tool | Low | Medium | P2 |
| Connection pooling | Low | Medium | P2 |
| Response compression | Low | Low | P3 |

**Implementation Pattern:**
```python
# Async pattern for data loading
import asyncio
from functools import lru_cache

class AsyncDataLoader:
    async def get_fundamentals(self, ticker: str) -> pd.DataFrame:
        return await asyncio.to_thread(self._load_sync, ticker)
```

---

### A2. Data Coverage Expansion

**New Data Sources to Add:**

| Source | Data Type | Status | Priority |
|--------|-----------|--------|----------|
| VCI Forecast | Analyst forecasts | API exists in PROCESSORS | P1 |
| Consensus (HCM/SSI) | Multi-source consensus | PDF extraction needed | P2 |
| News/Events | Corporate events | vnstock API | P2 |
| Insider Trading | Ownership changes | vnstock API | P3 |
| ETF Holdings | ETF composition | vnstock API | P3 |

**New Tools Proposed:**

```
# Forecast expansion
bsc_get_vci_forecast(ticker)         # VCI analyst forecast
bsc_get_consensus_forecast(ticker)   # Multi-source consensus
bsc_compare_forecasts(ticker)        # BSC vs VCI vs Consensus

# Corporate events
bsc_get_corporate_events(ticker)     # Dividends, rights, AGM
bsc_get_insider_trading(ticker)      # Ownership changes
bsc_get_news(ticker, limit=10)       # Recent news

# ETF/Index
bsc_get_etf_holdings(etf_code)       # ETF composition
bsc_get_index_constituents(index)    # VN30, VN100 members
```

**Est. New Tools:** 8-10 tools

---

### A3. AI-Powered Tools (Future)

**New Category: Analysis Tools**

| Tool | Description | Dependencies |
|------|-------------|--------------|
| `bsc_analyze_ticker` | AI summary of ticker (fundamental + technical + valuation) | LLM integration |
| `bsc_generate_report` | Generate investment report | LLM + templates |
| `bsc_backtest_strategy` | Simple backtesting | Historical data |
| `bsc_portfolio_analysis` | Analyze portfolio performance | User input |

**Note:** Requires LLM integration (Claude API or local model).

---

### A4. Integration Enhancements

**Claude Code Integration:**

1. **MCP Resources** - Expose data as MCP resources (not just tools)
   ```json
   {
     "resources": [
       { "uri": "bsc://tickers/ACB", "name": "ACB Data" },
       { "uri": "bsc://sectors/banking", "name": "Banking Sector" }
     ]
   }
   ```

2. **MCP Prompts** - Pre-built prompts for common workflows
   ```json
   {
     "prompts": [
       { "name": "analyze-stock", "description": "Full stock analysis workflow" },
       { "name": "sector-comparison", "description": "Compare sectors" }
     ]
   }
   ```

3. **Streaming Support** - Real-time data streaming for large queries

**Cursor/Antigravity:**
- Same MCP protocol, should work out-of-box
- May need custom prompts for each IDE

---

## Part B: OneDrive MCP Server (NEW)

### B1. Requirements

**User Story:**
> "Tôi muốn MCP có thể lấy data từ Excel/PDF trên OneDrive, auto-sync khi file thay đổi, và dùng AI agent phân tích."

**Scope:**
1. Auto-sync files from OneDrive → DATA/raw/
2. Read/query Excel/PDF directly
3. Future: AI analysis of documents

---

### B2. Architecture Options

**Option 1: File Watcher Daemon (Recommended)**
```
OneDrive (local sync) → File Watcher → Copy to DATA/raw/
                                     → Trigger processors
                                     → Update parquet
```

**Pros:** Simple, reliable, works offline
**Cons:** Requires OneDrive desktop app, local storage

**Option 2: OneDrive API Direct**
```
OneDrive Graph API → Download on-demand → Process → Cache
```

**Pros:** No local sync needed
**Cons:** Requires auth, network dependent, complex

**Recommendation:** Option 1 (File Watcher) for Phase 1

---

### B3. OneDrive MCP Tools Design

**Sync Tools:**
```
onedrive_sync_file(source_path, dest_path)    # Manual sync
onedrive_list_watched_files()                 # Show watched files
onedrive_get_sync_status()                    # Check sync status
onedrive_add_watch(pattern)                   # Add file/folder to watch
onedrive_remove_watch(pattern)                # Remove watch
```

**Read Tools:**
```
onedrive_read_excel(path, sheet=None)         # Read Excel to DataFrame
onedrive_read_pdf(path)                       # Extract text from PDF
onedrive_list_files(path, pattern="*.xlsx")   # List files
onedrive_get_file_info(path)                  # Get file metadata
```

**Query Tools (Future):**
```
onedrive_query_excel(path, query)             # Natural language query
onedrive_analyze_document(path, prompt)       # AI analysis
```

---

### B4. Implementation Plan

**Phase 1: Basic Sync (1-2 days)**
- [ ] Create `MCP_SERVER/onedrive_mcp/` structure
- [ ] Implement file watcher using `watchdog` library
- [ ] Config file for watched paths
- [ ] Basic sync tools: sync_file, list_watched, get_status

**Phase 2: Read Tools (1 day)**
- [ ] Excel reader (pandas)
- [ ] PDF reader (pypdf2 or pdfplumber)
- [ ] File listing and metadata

**Phase 3: Integration (1 day)**
- [ ] Add to `.mcp.json`
- [ ] Connect with BSC MCP (trigger data updates)
- [ ] Test with Claude Code

**Phase 4: AI Analysis (Future)**
- [ ] LLM integration for document analysis
- [ ] Natural language query interface

---

### B5. File Structure

```
MCP_SERVER/
├── bsc_mcp/              # Existing
└── onedrive_mcp/         # NEW
    ├── __init__.py
    ├── server.py         # FastMCP entry point
    ├── config.py         # Config (watched paths, OneDrive root)
    ├── services/
    │   ├── file_watcher.py   # Watchdog service
    │   ├── excel_reader.py   # Excel parsing
    │   └── pdf_reader.py     # PDF extraction
    ├── tools/
    │   ├── sync_tools.py     # Sync operations
    │   └── read_tools.py     # Read operations
    └── utils/
        └── path_utils.py     # OneDrive path helpers
```

---

### B6. Configuration Example

```json
// .mcp.json (updated)
{
  "mcpServers": {
    "bsc": { ... },
    "onedrive": {
      "type": "stdio",
      "command": "python3",
      "args": ["-m", "onedrive_mcp.server"],
      "cwd": "/Users/buuphan/Dev/Vietnam_dashboard/MCP_SERVER",
      "env": {
        "ONEDRIVE_ROOT": "~/Library/CloudStorage/OneDrive-BIDVSecuritiesJSC",
        "DATA_ROOT": "/Users/buuphan/Dev/Vietnam_dashboard/DATA"
      }
    }
  }
}
```

```yaml
# onedrive_mcp/config.yaml
watched_files:
  - source: "Equity Team/General/BSC Forecast.xlsx"
    dest: "raw/forecast/bsc_excel/BSC Forecast.xlsx"
    on_change: "python3 PROCESSORS/forecast/bsc/bsc_forecast_processor.py"

  # Future expansion
  - source: "Equity Team/General/Sector Reports/*.pdf"
    dest: "raw/reports/sector/"
    on_change: null  # Just sync, no processing
```

---

## Part C: Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Claude Code / Cursor                      │
│                              ↓                                   │
├─────────────────────────────┬───────────────────────────────────┤
│      BSC MCP (28+ tools)    │     OneDrive MCP (8 tools)        │
│  ┌────────────────────────┐ │ ┌────────────────────────────┐    │
│  │ Discovery, Fundamental │ │ │ Sync, Read, Query          │    │
│  │ Technical, Valuation   │ │ │                            │    │
│  │ Forecast, Sector, Macro│ │ │                            │    │
│  └──────────┬─────────────┘ │ └──────────┬─────────────────┘    │
│             ↓               │            ↓                       │
│    DATA/processed/          │    DATA/raw/ ← OneDrive local     │
│    (parquet files)          │    (Excel, PDF)                   │
├─────────────────────────────┴───────────────────────────────────┤
│                        WEBAPP (Streamlit)                        │
│                    (Reads DATA/processed/ directly)              │
│                    (Independent, no MCP dependency)              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Part D: Effort Estimation

| Task | Effort | Complexity | Dependencies |
|------|--------|------------|--------------|
| **BSC MCP Performance** | 2-3 days | Medium | None |
| **BSC MCP Data Coverage** | 3-5 days | Medium | VCI API, PDF extractors |
| **BSC MCP AI Tools** | 5-7 days | High | LLM integration |
| **BSC MCP Integration** | 1-2 days | Low | FastMCP resources/prompts |
| **OneDrive MCP Phase 1** | 1-2 days | Low | watchdog lib |
| **OneDrive MCP Phase 2** | 1 day | Low | pandas, pypdf2 |
| **OneDrive MCP Phase 3** | 1 day | Low | .mcp.json config |
| **OneDrive MCP Phase 4** | 3-5 days | High | LLM integration |

**Total Estimated:** 17-26 days (if all features)

---

## Part E: Recommended Prioritization

**Phase 1 (Week 1-2): Foundation**
1. ✅ OneDrive MCP basic sync (BSC Forecast.xlsx)
2. ✅ BSC MCP performance (async, better caching)

**Phase 2 (Week 3-4): Data Expansion**
3. ✅ OneDrive MCP read tools
4. ✅ BSC MCP VCI forecast integration
5. ✅ BSC MCP consensus data

**Phase 3 (Week 5+): Advanced**
6. 🔄 BSC MCP AI analysis tools
7. 🔄 OneDrive MCP AI document analysis
8. 🔄 MCP resources/prompts for Claude Code

---

## Part F: BSC MCP Gap Analysis (CRITICAL)

**Total DATA parquet files:** 56
**BSC MCP config paths:** 22
**Gap:** 34 files (60%) chưa được MCP expose!

### F1. TECHNICAL DATA - Gap Analysis

| Data File | BSC MCP Config | BSC MCP Tool | WEBAPP Uses | Status |
|-----------|----------------|--------------|-------------|--------|
| `technical/basic_data.parquet` | ✅ | `bsc_get_technical_indicators` | ✅ | OK |
| `technical/alerts/daily/breakout_latest.parquet` | ✅ | `bsc_get_technical_alerts` | ✅ | OK |
| `technical/alerts/daily/ma_crossover_latest.parquet` | ✅ | `bsc_get_technical_alerts` | ✅ | OK |
| `technical/alerts/daily/volume_spike_latest.parquet` | ✅ | `bsc_get_technical_alerts` | ✅ | OK |
| `technical/alerts/daily/patterns_latest.parquet` | ✅ | `bsc_get_candlestick_patterns` | ✅ | OK |
| `technical/alerts/daily/combined_latest.parquet` | ✅ | ❌ None | ✅ | **MISSING** |
| `technical/alerts/historical/*.parquet` (5 files) | ❌ | ❌ None | ✅ | **MISSING** |
| `technical/market_breadth/market_breadth_daily.parquet` | ✅ | `bsc_get_market_breadth` | ✅ | OK |
| `technical/sector_breadth/sector_breadth_daily.parquet` | ✅ | ❌ None | ✅ | **MISSING** |
| `technical/money_flow/individual_money_flow.parquet` | ✅ | ❌ None | ✅ | **MISSING** |
| `technical/money_flow/sector_money_flow_*.parquet` (4 files) | ✅ 1d only | ❌ None | ✅ | **MISSING** |
| `technical/vnindex/vnindex_indicators.parquet` | ✅ | ❌ None | ✅ | **MISSING** |
| `technical/lists/buy_list_latest.parquet` | ❌ | ❌ None | ✅ | **MISSING** |
| `technical/lists/sell_list_latest.parquet` | ❌ | ❌ None | ✅ | **MISSING** |
| `technical/rs_rating/stock_rs_rating_daily.parquet` | ❌ | ❌ None | ✅ | **MISSING** |
| `technical/rs_rating/rs_rating_history_30d.parquet` | ❌ | ❌ None | ✅ | **MISSING** |
| `technical/market_regime/market_regime_history.parquet` | ❌ | ❌ None | ✅ | **MISSING** |
| `technical/sector/ranking_latest.parquet` | ❌ | ❌ None | ✅ | **MISSING** |
| `technical/sector/rrg_latest.parquet` | ❌ | ❌ None | ✅ | **MISSING** |
| `technical/market/market_state_latest.parquet` | ❌ | ❌ None | ✅ | **MISSING** |

**Technical Gap Summary:** 15/27 files missing (55%)

---

### F2. FORECAST DATA - Gap Analysis

| Data File | BSC MCP Config | BSC MCP Tool | WEBAPP Uses | Status |
|-----------|----------------|--------------|-------------|--------|
| `forecast/bsc/bsc_individual.parquet` | ✅ | `bsc_get_bsc_forecast` | ✅ | OK |
| `forecast/bsc/bsc_sector_valuation.parquet` | ✅ | ❌ None | ✅ | **MISSING** |
| `forecast/bsc/bsc_combined.parquet` | ✅ | ❌ None | ✅ | **MISSING** |
| `forecast/unified.parquet` | ❌ | ❌ None | ✅ | **MISSING** |
| `forecast/sources/*.parquet` (VCI, etc.) | ❌ | ❌ None | ✅ | **MISSING** |

**Forecast Gap Summary:** 4/5+ files missing (80%)

---

### F3. VALUATION DATA - Gap Analysis

| Data File | BSC MCP Config | BSC MCP Tool | WEBAPP Uses | Status |
|-----------|----------------|--------------|-------------|--------|
| `valuation/pe/historical/historical_pe.parquet` | ✅ | `bsc_get_ticker_valuation` | ✅ | OK |
| `valuation/pb/historical/historical_pb.parquet` | ✅ | `bsc_get_ticker_valuation` | ✅ | OK |
| `valuation/ps/historical/historical_ps.parquet` | ✅ | `bsc_get_ticker_valuation` | ✅ | OK |
| `valuation/ev_ebitda/historical/historical_ev_ebitda.parquet` | ✅ | `bsc_get_ticker_valuation` | ✅ | OK |
| `valuation/vnindex/vnindex_valuation_refined.parquet` | ✅ | `bsc_get_vnindex_valuation` | ✅ | OK |
| `stock_valuation/individual_pe.parquet` | ❌ | ❌ None | ✅ | **MISSING** |
| `stock_valuation/individual_pb.parquet` | ❌ | ❌ None | ✅ | **MISSING** |
| `stock_valuation/individual_ev_ebitda.parquet` | ❌ | ❌ None | ✅ | **MISSING** |

**Valuation Gap Summary:** 3/8 files missing (37%)

---

### F4. SECTOR DATA - Gap Analysis

| Data File | BSC MCP Config | BSC MCP Tool | WEBAPP Uses | Status |
|-----------|----------------|--------------|-------------|--------|
| `sector/sector_valuation_metrics.parquet` | ✅ | `bsc_get_sector_valuation` | ✅ | OK |
| `sector/sector_fundamental_metrics.parquet` | ✅ | `bsc_get_sector_scores` | ✅ | OK |
| `sector/sector_combined_scores.parquet` | ❌ | ❌ None | ✅ | **MISSING** |

**Sector Gap Summary:** 1/3 files missing (33%)

---

### F5. FUNDAMENTAL DATA - Gap Analysis

| Data File | BSC MCP Config | BSC MCP Tool | WEBAPP Uses | Status |
|-----------|----------------|--------------|-------------|--------|
| `fundamental/company/company_financial_metrics.parquet` | ✅ | `bsc_get_company_financials` | ✅ | OK |
| `fundamental/bank/bank_financial_metrics.parquet` | ✅ | `bsc_get_bank_financials` | ✅ | OK |
| `fundamental/insurance/insurance_financial_metrics.parquet` | ✅ | `bsc_get_company_financials` | ✅ | OK |
| `fundamental/security/security_financial_metrics.parquet` | ✅ | `bsc_get_company_financials` | ✅ | OK |
| `fundamental/company_full.parquet` | ✅ | ❌ None | ✅ | **MISSING** |
| `fundamental/bank_full.parquet` | ❌ | ❌ None | ✅ | **MISSING** |
| `fundamental/insurance_full.parquet` | ❌ | ❌ None | ✅ | **MISSING** |
| `fundamental/security_full.parquet` | ❌ | ❌ None | ✅ | **MISSING** |
| `fundamental/macro/interest_rates.parquet` | ❌ | ❌ None | ✅ | **MISSING** |
| `fundamental/macro/deposit_interest_rates.parquet` | ❌ | ❌ None | ✅ | **MISSING** |
| `fundamental/macro/exchange_rates.parquet` | ❌ | ❌ None | ✅ | **MISSING** |
| `fundamental/macro/gov_bond_yields.parquet` | ❌ | ❌ None | ✅ | **MISSING** |

**Fundamental Gap Summary:** 8/12 files missing (67%)

---

### F6. PROPOSED NEW TOOLS (Priority Order)

**P0 - Critical (Dashboard parity):**

| New Tool | Data Source | Description |
|----------|-------------|-------------|
| `bsc_get_money_flow` | `money_flow/*.parquet` | Individual + sector money flow |
| `bsc_get_buy_sell_list` | `lists/*.parquet` | Daily buy/sell signals |
| `bsc_get_rs_rating` | `rs_rating/*.parquet` | Relative strength ranking |
| `bsc_get_market_state` | `market/market_state_latest.parquet` | Overall market condition |
| `bsc_get_sector_rotation` | `sector/rrg_latest.parquet` | RRG sector rotation |

**P1 - Important:**

| New Tool | Data Source | Description |
|----------|-------------|-------------|
| `bsc_get_sector_ranking` | `sector/ranking_latest.parquet` | Sector performance ranking |
| `bsc_get_vnindex_technicals` | `vnindex/vnindex_indicators.parquet` | VN-Index indicators |
| `bsc_get_sector_breadth` | `sector_breadth/sector_breadth_daily.parquet` | Sector advance/decline |
| `bsc_get_market_regime` | `market_regime/*.parquet` | Bull/bear regime detection |
| `bsc_get_alert_history` | `alerts/historical/*.parquet` | Historical alerts lookup |

**P2 - Nice to have:**

| New Tool | Data Source | Description |
|----------|-------------|-------------|
| `bsc_get_unified_forecast` | `forecast/unified.parquet` | Multi-source forecasts |
| `bsc_get_individual_valuation` | `stock_valuation/*.parquet` | Per-stock valuation history |
| `bsc_get_full_financials` | `*_full.parquet` | Complete raw financial data |
| `bsc_get_interest_rates` | `fundamental/macro/*.parquet` | Detailed macro breakdown |

**Total New Tools Proposed:** 14 tools

---

### F7. Updated Tool Count Projection

| Category | Current | Add | New Total |
|----------|---------|-----|-----------|
| Discovery | 5 | 0 | 5 |
| Fundamental | 5 | 2 | 7 |
| Technical | 6 | 8 | 14 |
| Valuation | 5 | 1 | 6 |
| Forecast | 3 | 1 | 4 |
| Sector | 3 | 2 | 5 |
| Macro | 3 | 1 | 4 |
| **Total** | **28** | **15** | **43** |

---

## Unresolved Questions

1. ~~**LLM Choice**: Claude API vs local model for AI analysis?~~ → Use Claude Code agents
2. ~~**OneDrive Auth**: Need Graph API for non-local scenarios?~~ → Local sync only
3. ~~**Real-time Sync**: How often should file watcher check?~~ → Manual trigger (không cần daemon)
4. **Error Handling**: What if OneDrive file locked by Excel?
5. **Tool Granularity**: Combine related tools or keep separate? (e.g., money_flow_individual vs money_flow_sector)

---

## Next Steps

1. **Approve plan** or provide feedback
2. **Create implementation plan** in `plans/260104-{slug}/plan.md`
3. **Start Phase 1**: OneDrive MCP basic sync

---

*Report generated by Claude Code Brainstormer*
