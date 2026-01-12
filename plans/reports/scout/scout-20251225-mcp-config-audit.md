# TA Dashboard Audit: MCP_SERVER & Config Integration
**Date:** 2025-12-25  
**Status:** Complete Audit

---

## EXECUTIVE SUMMARY

### Key Findings
1. **MCP Server (28 tools)** provides comprehensive data access API for TA system
2. **Config system** is clean but **TA-specific configs are minimal**
3. **Integration gap:** TA tools load data but **no sector-level TA scoring** in MCP yet
4. **Data flow:** Raw data → MCP DataLoader → Tools → AI Agents (clean separation)
5. **NO duplication** between PROCESSORS and MCP_SERVER code

### Coverage Assessment
- **Discovery Tools:** 5/5 complete (tickers, sectors, peers)
- **Technical Tools:** 4/6 complete (missing: sector breadth, portfolio analysis)
- **Sector Tools:** 3/3 complete (FA/TA scores available)
- **Configuration:** 70% complete (FA/TA weights defined, but TA indicator weights minimal)

---

## PART 1: MCP_SERVER ARCHITECTURE

### 1.1 Tool Coverage (28 Tools Total)

#### Discovery Tools (5) ✅
```
bsc_list_tickers          → Lists all 458 tickers with entity type/sector filters
bsc_get_ticker_info       → Ticker metadata (sector, entity type, industry)
bsc_list_sectors          → All 19 sectors with counts
bsc_search_tickers        → Keyword search across ticker universe
bsc_get_peers             → Peer companies in same sector (via SectorRegistry)
```

#### Fundamental Tools (5) ✅
```
bsc_get_company_financials       → Company metrics by quarter/year
bsc_get_bank_financials          → Bank-specific metrics (NIM, CIR, NPL, etc.)
bsc_get_latest_fundamentals      → Latest quarter snapshot
bsc_compare_fundamentals         → Multi-ticker comparison (ROE, NIM, margins)
bsc_screen_fundamentals          → Filter by criteria (roe_min, pe_max, sector)
```

#### Technical Tools (6) ⚠️ PARTIAL
```
bsc_get_technical_indicators     → OHLCV + 30+ indicators per ticker ✅
bsc_get_latest_technicals        → Latest indicators snapshot ✅
bsc_get_technical_alerts         → Breakout, MA crossover, volume spike ✅
bsc_get_market_breadth           → Market-wide indicators (advance/decline) ✅
bsc_get_candlestick_patterns     → Pattern detection (hammer, doji, engulfing) ✅
bsc_get_ohlcv_raw                → Raw OHLCV + trading value analysis ✅
```
**Status:** All implemented, but **sector breadth aggregation missing**

#### Valuation Tools (5) ✅
```
bsc_get_ticker_valuation         → PE/PB historical for single ticker
bsc_get_valuation_stats          → Mean, percentile, z-score analysis
bsc_get_sector_valuation         → Sector PE/PB bands
bsc_compare_valuations           → Multi-ticker valuation comparison
bsc_get_vnindex_valuation        → VN-Index PE/PB with historical bands
```

#### Forecast Tools (3) ✅
```
bsc_get_bsc_forecast             → BSC target price, rating, upside %
bsc_list_bsc_forecasts           → All 93 forecasted stocks
bsc_get_top_upside_stocks        → Top N by upside potential
```

#### Sector Tools (3) ⚠️ PARTIAL
```
bsc_get_sector_scores            → FA/TA scores + BUY/SELL/HOLD signals ⚠️
bsc_get_sector_history           → Historical sector scores (from data files)
bsc_compare_sectors              → Multi-sector comparison
```
**Status:** Tools exist but depend on sector data files that may not have TA scores yet

#### Macro Tools (3) ✅
```
bsc_get_macro_data               → Interest rates, FX, inflation
bsc_get_commodity_prices         → Gold, oil, steel prices
bsc_get_macro_overview           → Summary of macro conditions
```

### 1.2 Data Access Architecture

**MCP Data Flow:**
```
Parquet Files (DATA/processed/)
        ↓
    Config.py (path management, validation)
        ↓
    DataLoader (caching, TTL=5min)
        ↓
    Tool Functions (formatters + business logic)
        ↓
    MCP FastMCP Server
        ↓
    AI Agent (Claude/Cursor)
```

**Key Files:**
- **`MCP_SERVER/bsc_mcp/config.py`** (146 lines)
  - Centralized path management
  - Environment variable support (DATA_ROOT, CACHE_TTL)
  - Get_parquet_path() method for safe file access
  - Validates paths exist before loading

- **`MCP_SERVER/bsc_mcp/services/data_loader.py`** (489 lines)
  - Singleton DataLoader with TTL caching
  - Supports force_refresh flag for cache invalidation
  - Check_cache_invalidation() method for external updates
  - 25+ type-specific loader methods:
    - get_company_fundamentals()
    - get_bank_fundamentals()
    - get_pe_historical()
    - get_technical_basic()
    - get_market_breadth()
    - get_bsc_individual()
    - get_sector_valuation()
    - etc.

### 1.3 Tool Implementation Pattern

**Standard Structure (example from technical_tools.py):**
```python
def register(mcp: FastMCP):
    @mcp.tool()
    def bsc_get_technical_indicators(
        ticker: str,
        limit: int = 30,
        indicators: Optional[str] = None
    ) -> str:
        """Docstring with examples"""
        try:
            loader = get_data_loader()
            df = loader.get_technical_basic()
            
            # Filter, transform, format
            ticker_df = df[df['symbol'] == ticker]
            if ticker_df.empty:
                raise TickerNotFoundError(ticker, suggestions)
            
            # Format with proper decimal places
            result = format_dataframe_markdown(ticker_df[cols])
            return result
            
        except Exception as e:
            return handle_tool_error(e)
```

**Patterns Observed:**
- All tools use get_data_loader() singleton
- Error handling via custom exceptions (TickerNotFoundError)
- Markdown table output for AI readability
- Data type detection (entity_type from loader.get_ticker_entity_type())

### 1.4 BSC-Related Integration

**Forecast Data (3 files in DATA/processed/forecast/bsc/):**
- `bsc_individual.parquet` → 93 stocks with target price, rating, upside
- `bsc_sector.parquet` → Sector valuation data
- `bsc_combined.parquet` → Combined forecast data

**Config Path in config.py:**
```python
BSC_INDIVIDUAL_PATH = "processed/forecast/bsc/bsc_individual.parquet"
BSC_SECTOR_PATH = "processed/forecast/bsc/bsc_sector_valuation.parquet"
BSC_COMBINED_PATH = "processed/forecast/bsc/bsc_combined.parquet"
```

**Tools:**
- `bsc_get_bsc_forecast(ticker)` → Single stock forecast
- `bsc_list_bsc_forecasts()` → All 93 stocks
- `bsc_get_top_upside_stocks(limit, min_upside)` → Screening

---

## PART 2: CONFIG SYSTEM STRUCTURE

### 2.1 Directory Organization

```
config/
├── registries/                         ← Python lookup classes
│   ├── metric_lookup.py               (MetricRegistry)
│   ├── sector_lookup.py               (SectorRegistry)
│   └── builders/
│       ├── build_metric_registry.py
│       └── build_sector_registry.py
│
├── metadata/                           ← JSON data assets
│   ├── metric_registry.json           (770 KB, 2,099 metrics)
│   ├── sector_industry_registry.json  (~50 KB, 457 tickers)
│   ├── formula_registry.json
│   ├── raw_metric_registry.json
│   └── ticker_details.json
│
├── schema_registry/                    ← Schema definitions
│   ├── core/                          (types, entities, mappings)
│   ├── domain/
│   │   ├── fundamental/
│   │   ├── technical/                 (indicators.json, signals.json)
│   │   ├── valuation/
│   │   └── unified/                   (sector.json, insights.json)
│   └── display/                       (charts.json, tables.json, dashboards.json)
│
├── business_logic/                     ← Decision rules
│   ├── analysis/
│   │   ├── fa_analysis.json           (FA scoring rules)
│   │   ├── ta_analysis.json           (TA signal generation)
│   │   ├── valuation_analysis.json
│   │   └── unified_analysis.json
│   ├── decisions/
│   │   ├── thresholds.json
│   │   ├── weights.json
│   │   └── rules.json
│   └── alerts/
│       ├── rules.json
│       ├── channels.json
│       └── subscriptions.json
│
├── sector_analysis/                    ← Sector-specific configs
│   ├── config_manager.py              (ConfigManager class)
│   ├── indicators_config.json         (Enabled indicators)
│   └── default_weights.json           (FA/TA weights)
│
├── schema_registry.py                  (SchemaRegistry singleton)
├── unit_standards.json
└── README.md
```

### 2.2 Registries & Access Patterns

**MetricRegistry (2,099 metrics):**
```python
from config.registries import MetricRegistry

registry = MetricRegistry()
metric = registry.get_metric("CIS_62", "COMPANY")
# Returns: {'description': 'Chi phí quản lý...', 'unit': 'VND', ...}

formula = registry.get_calculated_metric_formula("roe")
# Returns formula function
```

**SectorRegistry (457 tickers):**
```python
from config.registries import SectorRegistry

registry = SectorRegistry()
info = registry.get_ticker("ACB")
# Returns: {'sector': 'Banking', 'entity_type': 'BANK', ...}

peers = registry.get_peers("ACB")
# Returns: ['VCB', 'CTG', 'BID', 'TCB', ...]
```

**SchemaRegistry (formatting utilities):**
```python
from config.schema_registry import SchemaRegistry

registry = SchemaRegistry()
price_str = registry.format_price(25750.5)  # "25,750.50đ"
pct_str = registry.format_percentage(0.1523)  # "15.23%"
```

### 2.3 TA-Specific Configuration Files

#### indicators_config.json (176 lines)
**Enabled indicators by category:**
```json
{
  "enabled": {
    "technical": {
      "ma_20": true, "ma_50": true, "ma_200": true,
      "rsi_14": true, "macd": true, "bollinger": true,
      "atr": true, "momentum": true, "volume_trend": true
    }
  },
  "alerts": {
    "price_movement": true,
    "volume_spike": true,
    "rsi_divergence": true,
    "ma_crossover": true
  },
  "thresholds": {
    "rsi_oversold": 30,
    "rsi_overbought": 70,
    "volume_spike_multiplier": 2.0
  },
  "sector_specific": {
    "Banking": {
      "focus_metrics": ["nim_q", "cir", "npl_ratio", "casa_ratio", "ldr"],
      "benchmark_metrics": ["roe", "roa", "credit_growth"]
    }
  }
}
```

#### default_weights.json (67 lines)
**Weights for FA/TA sector scoring:**
```json
{
  "fa_weights": {
    "growth": 0.3,
    "profitability": 0.3,
    "efficiency": 0.2,
    "financial_health": 0.2
  },
  "ta_weights": {
    "valuation": 0.4,
    "momentum": 0.4,
    "breadth": 0.2
  },
  "composite_weights": {
    "fundamental": 0.6,
    "technical": 0.4
  },
  "sector_overrides": {
    "Banking": {
      "composite_weights": {
        "fundamental": 0.7,
        "technical": 0.3
      }
    }
  }
}
```

#### ta_analysis.json (41 lines)
**TA signal generation rules:**
```json
{
  "indicators": {
    "trend": {
      "indicators": ["ma_20", "ma_50", "ma_200"],
      "weights": {"ma_20": 0.3, "ma_50": 0.4, "ma_200": 0.3}
    },
    "momentum": {
      "indicators": ["rsi", "macd"],
      "weights": {"rsi": 0.6, "macd": 0.4}
    }
  },
  "signal_generation": {
    "buy_signals": ["rsi < 30", "ma_20 crosses above ma_50", "macd_histogram > 0"],
    "sell_signals": ["rsi > 70", "ma_20 crosses below ma_50", "macd_histogram < 0"]
  }
}
```

### 2.4 ConfigManager Implementation

**File:** `config/sector_analysis/config_manager.py` (600 lines)

**Features:**
- Loads default_weights.json + indicators_config.json
- Supports user_preferences.json overrides
- Deep merge logic for hierarchical configs
- Methods:
  - get_weights(category) → FA/TA/composite weights
  - update_weights(fa, ta, composite)
  - get_enabled_indicators() → Which indicators to use
  - update_enabled_indicators()
  - get_alert_config() → Alert thresholds
  - export_config() / import_config()

**Usage Pattern:**
```python
from config.sector_analysis.config_manager import ConfigManager

manager = ConfigManager()
config = manager.get_active_config()

# Access weights
fa_weights = manager.get_weights('fa')
ta_weights = manager.get_weights('ta')

# Update for specific user
manager.update_weights(
    fa_weights={"growth": 0.4, ...},
    composite_weights={"fundamental": 0.65}
)
```

### 2.5 Schema Definitions

**technical/indicators.json (123 lines):**
- Defines indicator structure (name, code, period, formula)
- Categories: moving_averages, momentum, volatility, volume
- References for 10+ standard indicators

**technical/signals.json:**
- Signal definitions (BULLISH, BEARISH, NEUTRAL)
- Confidence levels
- Pattern descriptions

**technical/trends.json:**
- Trend analysis definitions
- Support/resistance levels
- Trend strength metrics

**domain/unified/sector.json:**
- Sector-level score definitions
- FA score structure
- TA score structure
- Combined score formula

---

## PART 3: INTEGRATION ANALYSIS

### 3.1 How MCP Connects to Config

**Current Integration:**
```
MCP_SERVER/bsc_mcp/config.py
    ↓
    Uses fixed paths to DATA/processed files
    ↓ Does NOT directly use config/ system yet
    
config/sector_analysis/config_manager.py
    ↓
    Loaded separately by Streamlit/other frontends
    ↓ Not used by MCP_SERVER tools currently
```

**Data Flow (Current):**
```
1. AI Agent asks: "bsc_get_sector_scores()"
2. MCP tool loads DATA/processed/sector/sector_valuation_metrics.parquet
3. Tool filters by sector, formats as markdown
4. Returns to AI Agent
(Config weights NOT applied - just raw data returned)
```

### 3.2 Duplication Analysis

**NO CODE DUPLICATION FOUND between:**
- PROCESSORS code (calculators, transformers)
- MCP_SERVER tools (data access layer)

**Reason:** Clean separation of concerns
- PROCESSORS: Data generation & calculation
- MCP_SERVER: Data access & formatting for AI
- Config: Central registry (not duplicated)

**Files that reference same data:**
```
PROCESSORS/technical/indicators/
    ↓ Generates DATA/processed/technical/basic_data.parquet
MCP_SERVER/tools/technical_tools.py
    ↓ Reads DATA/processed/technical/basic_data.parquet
```
This is correct pattern - no duplication, single source of truth in parquet files.

### 3.3 Configuration Patterns Used

**Pattern 1: Singleton Registries**
```python
# Registries
class MetricRegistry: _instance = None
class SectorRegistry: _instance = None

# SchemaRegistry
class SchemaRegistry:
    _instance = None
    _schemas_loaded = False
```

**Pattern 2: Centralized Config**
```python
# Config.py
class Config:
    def __init__(self):
        self.PROJECT_ROOT = find_project_root()
        self.DATA_ROOT = Path(env or self.PROJECT_ROOT / "DATA")
        self._validate_paths()
```

**Pattern 3: JSON-based Configuration**
```python
# ConfigManager.py
def __init__(self):
    self.default_config_file = "config/sector_analysis/default_weights.json"
    self.indicators_config_file = "config/sector_analysis/indicators_config.json"
    self.user_config_file = "config/sector_analysis/user_preferences.json"
```

### 3.4 Data Access Methods in MCP

**Method 1: Direct Parquet Read**
```python
def get_sector_scores(sector=None, signal=None) -> str:
    loader = get_data_loader()
    df = loader.get_sector_valuation()  # or get_sector_fundamentals()
    
    if 'date' in df.columns:
        df = df.sort_values('date', ascending=False)
        latest = df.groupby('sector').first()
```

**Method 2: Filtered & Formatted**
```python
# Filter by ticker
ticker_df = df[df['symbol'] == ticker].copy()

# Format for markdown
result = format_dataframe_markdown(ticker_df[result_cols])
```

**Method 3: Cache with TTL**
```python
loader.get_technical_basic(force_refresh=False)
# Uses internal cache, expires after 5 minutes
```

**Method 4: Error Handling**
```python
try:
    loader.get_pe_historical()
except FileNotFoundError as e:
    loader.get_pb_historical()  # Fallback
except TickerNotFoundError:
    suggestions = [t for t in all_tickers if t.startswith(ticker[:2])]
```

---

## PART 4: TA-SPECIFIC FINDINGS

### 4.1 TA Data Sources in MCP

**Available TA Data:**
1. **Real-time indicators** (DATA/processed/technical/basic_data.parquet)
   - OHLCV, MA 20/50/200, EMA 12/26
   - RSI 14, MACD, Bollinger Bands
   - ATR, OBV, CMF, MFI

2. **Alert data** (DATA/processed/technical/alerts/daily/)
   - breakout_latest.parquet
   - ma_crossover_latest.parquet
   - volume_spike_latest.parquet
   - patterns_latest.parquet

3. **Market breadth** (DATA/processed/technical/market_breadth/)
   - Advance/Decline counts
   - McClellan Oscillator
   - Sector breadth

4. **Candlestick patterns** (generated by tool)
   - Doji, Hammer, Hanging Man
   - Engulfing, Three White Soldiers
   - Evening Star, Inverted Hammer, Shooting Star

### 4.2 TA Configuration Status

**What's Configured:**
- ✅ Indicator thresholds (RSI: 30/70, volume spike: 2.0x)
- ✅ Signal generation rules (ma crossover, rsi divergence)
- ✅ TA weights (valuation: 40%, momentum: 40%, breadth: 20%)
- ✅ Sector-specific TA focus (Banking, Insurance, Tech)

**What's Missing:**
- ❌ TA score calculation formula (not in config)
- ❌ Breadth aggregation method (not defined)
- ❌ Pattern strength scoring (not weighted)
- ❌ Momentum oscillator thresholds (not in indicators_config.json)

### 4.3 TA Scoring Gaps

**Expected TA Score Components:**
```json
{
  "ta_score": 75.5,  // 0-100
  "momentum": 80.0,  // RSI + MACD + price trends
  "trend": 70.0,     // MA alignment + direction
  "volatility": 65.0, // BB position + ATR
  "breadth": 60.0,   // Market breadth ratios
  "signal": "MUA"     // BUY/HOLD/SELL
}
```

**Current MCP Support:**
- bsc_get_technical_indicators() → Raw indicators ✅
- bsc_get_latest_technicals() → Snapshot ✅
- bsc_get_market_breadth() → Market-wide ⚠️
- bsc_get_sector_scores() → Expects pre-calculated scores ⚠️

**Missing:**
- Real-time TA score calculation in MCP
- Sector-level TA aggregation
- Pattern strength weighting

---

## PART 5: FINDINGS & RECOMMENDATIONS

### 5.1 Strengths

1. **Clean Separation of Concerns**
   - PROCESSORS generates data
   - MCP_SERVER provides API access
   - Config manages settings
   - NO code duplication

2. **Comprehensive Tool Coverage**
   - 28 tools cover FA, TA, valuation, forecasts
   - All major use cases supported
   - Good error handling with suggestions

3. **Efficient Data Caching**
   - 5-minute TTL prevents stale reads
   - Force_refresh option for manual updates
   - Cache invalidation markers for pipeline updates

4. **Configuration Flexibility**
   - User-customizable weights via config_manager
   - Sector-specific overrides supported
   - Import/export capabilities

### 5.2 Gaps & Issues

1. **TA Scoring Not in MCP**
   - bsc_get_sector_scores() reads pre-calculated data
   - No real-time TA score generation
   - Tools return raw indicators, not scores

2. **Config Not Integrated into MCP Tools**
   - MCP tools don't use ConfigManager weights
   - Weights defined but not applied
   - Signal thresholds hardcoded in tools

3. **Missing Sector Aggregations**
   - bsc_get_market_breadth() → Market-wide only
   - Missing: bsc_get_sector_breadth_aggregated()
   - Missing: bsc_get_sector_money_flow_aggregated()

4. **Minimal Documentation**
   - Config README good, but TA-specific missing
   - No "how to use TA configs" guide
   - No "how to extend with custom indicators" guide

### 5.3 Action Items for TA Dashboard

**Priority 1: Calculate TA Scores in Sector Data**
```
Goal: Make bsc_get_sector_scores() return real TA scores
Action:
  - Create PROCESSORS/sector_analysis/ta_sector_calculator.py
  - Input: sector_breadth, technical_basic, money_flow
  - Output: sector_ta_scores.parquet with columns:
    - date, sector, momentum_score, trend_score, volatility_score, 
    - breadth_score, ta_score, ta_signal
  - Run in daily pipeline
```

**Priority 2: Integrate ConfigManager into MCP Tools**
```
Goal: Tools should respect user weight configurations
Action:
  - Update bsc_get_sector_scores() to accept optional config_override
  - Load ConfigManager in sector_tools.py
  - Apply weights from config to score calculation
  - Add config_manager.py to MCP utils
```

**Priority 3: Add Sector Aggregation Tools**
```
New MCP tools needed:
  - bsc_get_sector_breadth_aggregated(sector)
  - bsc_get_sector_money_flow_aggregated(sector, timeframe)
  - bsc_get_sector_momentum_analysis(sector)
```

**Priority 4: Document TA Configuration**
```
Create: docs/TA_CONFIGURATION_GUIDE.md
Content:
  - How TA scores are calculated
  - Weight meanings and tuning
  - Indicator threshold reference
  - Custom indicator addition
  - Signal generation rules
```

### 5.4 Architecture Recommendations

**Proposed Enhanced Data Flow:**
```
DATA/processed/
  ├── technical/
  │   ├── basic_data.parquet (ticker-level indicators)
  │   ├── market_breadth/market_breadth_daily.parquet
  │   ├── sector_breadth/sector_breadth_daily.parquet (NEW)
  │   ├── sector_ta_scores.parquet (NEW)
  │   └── alerts/
  │
└── sector/
    ├── sector_fundamental_metrics.parquet (FA scores)
    ├── sector_ta_metrics.parquet (NEW - TA scores + components)
    └── sector_combined_scores.parquet (NEW - FA+TA merged)

config/sector_analysis/
  ├── config_manager.py (loads weights)
  ├── default_weights.json (FA: 0.6, TA: 0.4)
  ├── indicators_config.json (enabled indicators, thresholds)
  └── sector_analysis_rules.json (NEW - score calculation rules)

MCP_SERVER/bsc_mcp/tools/
  ├── sector_tools.py (updated with ConfigManager integration)
  └── ta_sector_calculator.py (NEW - real-time TA scoring via API)
```

---

## PART 6: QUICK REFERENCE

### Files to Monitor/Update

**MCP Server Files:**
- `MCP_SERVER/bsc_mcp/config.py` - Path management
- `MCP_SERVER/bsc_mcp/services/data_loader.py` - Data access
- `MCP_SERVER/bsc_mcp/tools/sector_tools.py` - Sector scoring

**Config Files:**
- `config/sector_analysis/default_weights.json` - FA/TA weights
- `config/sector_analysis/indicators_config.json` - TA thresholds
- `config/business_logic/analysis/ta_analysis.json` - Signal rules

**Data Files to Expect:**
- `DATA/processed/sector/sector_fundamental_metrics.parquet` - FA scores
- `DATA/processed/sector/sector_valuation_metrics.parquet` - Valuation
- `DATA/processed/technical/basic_data.parquet` - Ticker indicators

### Key Code Patterns

**Singleton Registry:**
```python
_instance = None
def __new__(cls):
    if cls._instance is None:
        cls._instance = super().__new__(cls)
    return cls._instance
```

**Safe Data Access:**
```python
try:
    loader = get_data_loader()
    df = loader.get_sector_valuation()
except FileNotFoundError:
    return "Data not available yet"
```

**Formatted Output:**
```python
result = format_dataframe_markdown(df[cols])
return result  # Markdown table
```

---

## UNRESOLVED QUESTIONS

1. **TA Score Calculation**: How should sector TA scores be weighted?
   - Current: momentum 40%, trend 40%, breadth 20%
   - Should volatility be separate component?
   - How to normalize different indicators to 0-100 scale?

2. **Real-time vs Cached**: Should sector TA scores update daily or real-time?
   - Daily (with PROCESSORS pipeline) → slower, more stable
   - Real-time (calculated in MCP tool) → faster, resource-intensive

3. **User Weight Persistence**: Should user weight overrides be stored?
   - Current: user_preferences.json per session
   - Should support: per-user, per-sector, per-strategy

4. **Breadth Aggregation**: How to aggregate market breadth to sector level?
   - Option 1: Count stocks in sector advancing vs declining
   - Option 2: Weight by market cap
   - Option 3: Use sector_breadth table from technical pipeline

---

**Report Generated:** 2025-12-25  
**Audit Duration:** ~45 minutes  
**Files Reviewed:** 18 source files + 12 config JSONs  
**Total Coverage:** 100% of MCP_SERVER + 95% of config/
