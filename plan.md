# MCP Server Plan: Vietnamese Stock Market Data Query

## Mục tiêu

Xây dựng MCP server (`vnstock_mcp`) cho phép AI agents tra cứu thông tin doanh nghiệp Việt Nam từ:
1. **Structured Data** - Parquet files trong `/Users/buuphan/Dev/Vietnam_dashboard/DATA`
2. **Research Reports** - Báo cáo phân tích từ Google Drive hoặc local files (mở rộng)

---

## User Preferences

| Setting | Choice | Notes |
|---------|--------|-------|
| **Target AI** | Claude Code/Desktop | Sử dụng stdio transport |
| **Response Format** | Markdown (default) | Human-readable tables |
| **Macro Data** | Có | Thêm tools cho interest rates, FX, commodities |
| **Report Reading** | Có (Phase 2) | Google Drive hoặc local files |

---

## Tổng quan Data Sources

### 1. Structured Data (Parquet Files)

| Category | File | Records | Key Metrics |
|----------|------|---------|-------------|
| **Fundamental** | `company_financial_metrics.parquet` | 37,145 | ROE, ROA, margins, EPS, BVPS |
| | `bank_financial_metrics.parquet` | 1,051 | NIM, NPL, CASA, CAR |
| | `insurance_financial_metrics.parquet` | 418 | Combined ratio, claims ratio |
| | `security_financial_metrics.parquet` | 2,811 | Brokerage revenue, trading income |
| **Valuation** | `historical_pe.parquet` | 790,067 | PE TTM (1997-2025) |
| | `historical_pb.parquet` | 790,067 | PB TTM (1997-2025) |
| | `historical_ps.parquet` | 674,832 | PS TTM |
| | `historical_ev_ebitda.parquet` | 669,300 | EV/EBITDA |
| | `vnindex_valuation_refined.parquet` | 5,784 | VN-Index PE/PB |
| **Technical** | `basic_data.parquet` | 89,837 | OHLCV + 30+ indicators |
| | `market_breadth_daily.parquet` | - | Advance/Decline, McClellan |
| | `individual_money_flow.parquet` | 89,837 | CMF, MFI, OBV per ticker |
| **Forecast** | `bsc_individual.parquet` | 93 | Target price, rating, upside |
| | `bsc_sector_valuation.parquet` | 15 | Sector PE/PB Forward |
| **Sector** | `sector_combined_scores.parquet` | 380 | FA/TA scores, BUY/SELL signals |
| | `sector_fundamental_metrics.parquet` | 589 | Aggregated sector FA |
| **Macro** | `macro_commodity_unified.parquet` | 24,226 | Gold, oil, FX, rates |

**Coverage:** 457 tickers, 315 liquid stocks, 19 sectors (ICB L2 Vietnamese)

### 2. Research Reports (Mở rộng - Phase 2)

| Source | Format | Content |
|--------|--------|---------|
| **Local Files** | PDF, DOCX, TXT | Báo cáo phân tích từ các CTCK |
| **Google Drive** | PDF, Docs, Sheets | Báo cáo được chia sẻ/sync |

**Use Cases:**
- Tra cứu quan điểm của analyst về một cổ phiếu
- Tìm kiếm báo cáo theo ticker, sector, thời gian
- Tổng hợp consensus từ nhiều nguồn

---

## Cấu trúc Project

```
/Users/buuphan/Dev/Vietnam_dashboard/MCP_SERVER/
│
├── vnstock_mcp/                      # Main package
│   ├── __init__.py
│   ├── server.py                     # FastMCP server entry point
│   ├── config.py                     # Configuration & constants
│   │
│   ├── models/                       # Pydantic input/output schemas
│   │   ├── __init__.py
│   │   ├── base.py                   # Enums: ResponseFormat, EntityType, Period
│   │   ├── fundamental.py            # CompanyFinancialsInput, BankFinancialsInput
│   │   ├── technical.py              # TechnicalIndicatorsInput, AlertsInput
│   │   ├── valuation.py              # ValuationInput, ValuationStatsInput
│   │   ├── forecast.py               # BSCForecastInput
│   │   ├── sector.py                 # SectorScoresInput
│   │   ├── macro.py                  # MacroDataInput, CommodityInput
│   │   └── reports.py                # ReportSearchInput (Phase 2)
│   │
│   ├── tools/                        # Tool implementations (by domain)
│   │   ├── __init__.py               # Register all tools
│   │   ├── discovery_tools.py        # Ticker/sector lookup (5 tools)
│   │   ├── fundamental_tools.py      # Company/bank financials (5 tools)
│   │   ├── technical_tools.py        # OHLCV, indicators, alerts (4 tools)
│   │   ├── valuation_tools.py        # PE/PB/EV-EBITDA (5 tools)
│   │   ├── forecast_tools.py         # BSC forecasts (3 tools)
│   │   ├── sector_tools.py           # Sector scores (3 tools)
│   │   ├── macro_tools.py            # Macro/commodity data (3 tools)
│   │   └── report_tools.py           # Report search/read (Phase 2)
│   │
│   ├── services/                     # Data access layer
│   │   ├── __init__.py
│   │   ├── data_loader.py            # Parquet loading + LRU caching
│   │   ├── registry_service.py       # Wrapper for SectorRegistry
│   │   └── report_service.py         # Google Drive/local file access (Phase 2)
│   │
│   └── utils/                        # Shared utilities
│       ├── __init__.py
│       ├── formatters.py             # Markdown/JSON response formatters
│       ├── validators.py             # Input validation helpers
│       └── errors.py                 # Error handling & messages
│
├── reports/                          # Local reports storage (Phase 2)
│   ├── bsc/                          # BSC reports
│   ├── ssi/                          # SSI reports
│   ├── vnd/                          # VND reports
│   └── other/                        # Other sources
│
├── tests/
│   ├── __init__.py
│   ├── test_discovery_tools.py
│   ├── test_fundamental_tools.py
│   ├── test_valuation_tools.py
│   └── evaluation.xml                # MCP evaluation questions
│
├── pyproject.toml                    # Package configuration
├── requirements.txt                  # Dependencies
├── .mcp.json                         # MCP configuration for Claude Code
└── README.md                         # Documentation
```

---

## Tools Design (31 tools)

### 1. Discovery Tools (5 tools)

Dùng để tra cứu ticker, sector, tìm kiếm và lấy thông tin cơ bản.

| Tool | Description | Input | Output |
|------|-------------|-------|--------|
| `vnstock_list_tickers` | List tất cả tickers có sẵn | `entity_type?`, `sector?`, `limit?` | List tickers với basic info |
| `vnstock_get_ticker_info` | Lấy metadata chi tiết của ticker | `ticker` | Entity type, sector, exchange, industry code |
| `vnstock_list_sectors` | List 19 sectors với ticker counts | `entity_type?` | Sector names + counts |
| `vnstock_search_tickers` | Tìm kiếm ticker theo name/keyword | `query`, `limit?` | Matching tickers |
| `vnstock_get_peers` | Lấy danh sách peers cùng ngành | `ticker`, `limit?`, `exclude_self?` | List peer tickers |

**Example Usage:**
```
User: "Cho tôi danh sách các ngân hàng"
AI calls: vnstock_list_tickers(entity_type="BANK")
Returns: ACB, VCB, TCB, MBB, VPB, TPB, ... (24 banks)

User: "Các công ty cùng ngành với VNM là gì?"
AI calls: vnstock_get_peers(ticker="VNM", limit=10)
Returns: MSN, SAB, QNS, ... (Food & Beverage sector)
```

---

### 2. Fundamental Tools (5 tools)

Tra cứu chỉ số tài chính doanh nghiệp theo quý/năm.

| Tool | Description | Input | Output |
|------|-------------|-------|--------|
| `vnstock_get_company_financials` | Lấy financial metrics cho company | `ticker`, `period`, `table_type?`, `limit?` | Income, Balance, CF, Ratios |
| `vnstock_get_bank_financials` | Lấy metrics đặc thù ngân hàng | `ticker`, `period`, `limit?` | NIM, NPL, CASA, CAR, CIR |
| `vnstock_get_latest_fundamentals` | Lấy data quý gần nhất | `ticker` | Dict với tất cả metrics |
| `vnstock_compare_fundamentals` | So sánh nhiều tickers | `tickers[]`, `metrics?` | Comparison table |
| `vnstock_screen_fundamentals` | Lọc cổ phiếu theo criteria | `filters{}`, `sector?`, `limit?` | Filtered list |

**Key Metrics Available:**

| Entity | Metrics |
|--------|---------|
| **Company** | net_revenue, gross_profit, npatmi, roe, roa, gross_margin, net_margin, eps, bvps, current_ratio, debt_to_equity |
| **Bank** | nii (net interest income), nim, npl_ratio, casa_ratio, ldr, car, cir |
| **Insurance** | combined_ratio, claims_ratio, underwriting_profit |
| **Security** | brokerage_revenue, trading_income, proprietary_profit |

**Example Usage:**
```
User: "ROE của VCB 4 quý gần nhất là bao nhiêu?"
AI calls: vnstock_get_bank_financials(ticker="VCB", period="Quarterly", limit=4)
Returns:
| Quarter | ROE | NIM | NPL Ratio |
|---------|-----|-----|-----------|
| Q3 2024 | 19.5% | 3.12% | 1.23% |
| Q2 2024 | 19.2% | 3.08% | 1.25% |
| ...

User: "Lọc các công ty có ROE > 20% trong ngành Thực phẩm"
AI calls: vnstock_screen_fundamentals(filters={"roe": {"gt": 20}}, sector="Thực phẩm đồ uống")
```

---

### 3. Technical Tools (4 tools)

Tra cứu OHLCV, technical indicators, trading alerts.

| Tool | Description | Input | Output |
|------|-------------|-------|--------|
| `vnstock_get_technical_indicators` | Lấy OHLCV + 30+ indicators | `ticker`, `limit?`, `indicators?` | OHLCV + MA, RSI, MACD, BB, etc. |
| `vnstock_get_latest_technicals` | Snapshot kỹ thuật mới nhất | `ticker` | Latest indicators dict |
| `vnstock_get_technical_alerts` | Các tín hiệu giao dịch | `ticker?`, `alert_type?`, `limit?` | Breakout, MA crossover, volume spike |
| `vnstock_get_market_breadth` | Breadth indicators của thị trường | `date?` | Advance/Decline, McClellan Oscillator |

**Technical Indicators Available:**

| Category | Indicators |
|----------|------------|
| **Moving Averages** | SMA(20,50,100,200), EMA(20,50) |
| **Momentum** | RSI(14), MACD, MACD_signal, MACD_hist, Stochastic(K,D) |
| **Volatility** | Bollinger Bands (upper/middle/lower/width), ATR(14) |
| **Volume** | OBV, A/D Line, CMF(20), MFI(14) |
| **Trend** | ADX(14), CCI(20) |
| **Relative** | price_vs_sma20, price_vs_sma50, price_vs_sma200 |

**Alert Types:**
- `breakout` - Price breakout above resistance
- `ma_crossover` - Golden cross / Death cross
- `volume_spike` - Unusual volume
- `patterns` - Candlestick patterns

**Example Usage:**
```
User: "RSI và MACD của FPT hiện tại là bao nhiêu?"
AI calls: vnstock_get_latest_technicals(ticker="FPT")
Returns:
| Indicator | Value | Signal |
|-----------|-------|--------|
| RSI(14) | 62.5 | Neutral |
| MACD | 1.23 | Bullish |
| Price vs SMA50 | +5.2% | Above |

User: "Có cổ phiếu nào đang breakout không?"
AI calls: vnstock_get_technical_alerts(alert_type="breakout")
```

---

### 4. Valuation Tools (5 tools)

Tra cứu định giá PE, PB, EV/EBITDA historical và so sánh.

| Tool | Description | Input | Output |
|------|-------------|-------|--------|
| `vnstock_get_ticker_valuation` | Lịch sử PE/PB/EV-EBITDA | `ticker`, `metric?`, `limit?` | Time series valuation |
| `vnstock_get_valuation_stats` | Thống kê định giá | `ticker`, `metric?` | Current, mean, percentile, z-score |
| `vnstock_get_sector_valuation` | So sánh định giá các ngành | `sector?`, `date?` | Sector PE/PB comparison |
| `vnstock_compare_valuations` | So sánh định giá nhiều tickers | `tickers[]`, `metric?` | Comparison table |
| `vnstock_get_vnindex_valuation` | Định giá VN-Index | `limit?` | VN-Index PE/PB with bands |

**Example Usage:**
```
User: "PE của ACB đang ở percentile bao nhiêu so với 5 năm?"
AI calls: vnstock_get_valuation_stats(ticker="ACB", metric="PE")
Returns:
| Metric | Value |
|--------|-------|
| Current PE | 7.05 |
| 5Y Mean | 8.23 |
| 5Y Percentile | 25th |
| Z-Score | -0.72 |
| Assessment | Undervalued vs history |

User: "So sánh PE của các ngân hàng lớn"
AI calls: vnstock_compare_valuations(tickers=["VCB", "ACB", "TCB", "MBB"], metric="PE")
```

---

### 5. Forecast Tools (3 tools)

Tra cứu dự báo từ BSC Research (93 cổ phiếu).

| Tool | Description | Input | Output |
|------|-------------|-------|--------|
| `vnstock_get_bsc_forecast` | Dự báo chi tiết cho ticker | `ticker` | Target price, rating, upside, EPS forecast |
| `vnstock_list_bsc_forecasts` | List tất cả 93 stocks có dự báo | `rating?`, `sector?`, `sort_by?` | Forecast summary list |
| `vnstock_get_top_upside_stocks` | Top cổ phiếu có upside cao nhất | `n?`, `sector?` | Sorted by upside% |

**BSC Forecast Data:**

| Field | Description |
|-------|-------------|
| `target_price` | Giá mục tiêu (VND) |
| `current_price` | Giá hiện tại |
| `upside_pct` | % upside potential |
| `rating` | BUY / HOLD / SELL |
| `eps_2025f`, `eps_2026f` | EPS dự báo |
| `pe_fwd_2025`, `pe_fwd_2026` | Forward PE |
| `rev_growth_yoy_2025` | Revenue growth forecast |
| `npatmi_achievement_pct` | YTD achievement vs full-year |

**Example Usage:**
```
User: "BSC đánh giá ACB như thế nào?"
AI calls: vnstock_get_bsc_forecast(ticker="ACB")
Returns:
## ACB - Asia Commercial Bank
**Rating:** BUY
**Target Price:** 28,400 VND (+19.08% upside)

| Metric | 2025F | 2026F |
|--------|-------|-------|
| EPS | 3,491 | 3,912 |
| PE Forward | 6.83 | 6.10 |
| Revenue Growth | +7.65% | +11.22% |

User: "Top 10 cổ phiếu có upside cao nhất theo BSC"
AI calls: vnstock_get_top_upside_stocks(n=10)
```

---

### 6. Sector Tools (3 tools)

Tra cứu phân tích ngành với FA/TA scores và tín hiệu.

| Tool | Description | Input | Output |
|------|-------------|-------|--------|
| `vnstock_get_sector_scores` | FA/TA scores và signals | `sector?`, `date?` | Scores + BUY/SELL/HOLD signal |
| `vnstock_get_sector_history` | Lịch sử scores của ngành | `sector`, `limit?` | Historical FA/TA scores |
| `vnstock_compare_sectors` | So sánh nhiều ngành | `sectors?`, `metrics?` | Comparison table |

**Sector Analysis Data:**

| Score Component | Description |
|-----------------|-------------|
| `fa_score` | Fundamental Analysis score (0-100) |
| `ta_score` | Technical Analysis score (0-100) |
| `growth_score` | Revenue/profit growth |
| `profitability_score` | ROE, margins |
| `valuation_score` | PE/PB percentile |
| `momentum_score` | Price momentum |
| `signal` | MUA (BUY) / BÁN (SELL) / GIỮ (HOLD) |
| `signal_strength` | 1-5 scale |

**Example Usage:**
```
User: "Ngành nào đang có tín hiệu MUA?"
AI calls: vnstock_get_sector_scores()
Returns:
| Sector | FA Score | TA Score | Signal | Strength |
|--------|----------|----------|--------|----------|
| Ngân hàng | 72 | 68 | MUA | 4/5 |
| Thực phẩm | 65 | 71 | GIỮ | 3/5 |
| BĐS | 45 | 52 | BÁN | 2/5 |
```

---

### 7. Macro/Commodity Tools (3 tools)

Tra cứu dữ liệu macro và giá hàng hóa.

| Tool | Description | Input | Output |
|------|-------------|-------|--------|
| `vnstock_get_macro_data` | Interest rates, FX, bond yields | `indicator?`, `limit?` | Time series data |
| `vnstock_get_commodity_prices` | Giá vàng, dầu, thép, cao su | `commodity?`, `limit?` | Price history |
| `vnstock_get_macro_overview` | Tổng quan macro hiện tại | - | Summary of key indicators |

**Macro Indicators:**
- `deposit_rate` - Lãi suất tiền gửi
- `lending_rate` - Lãi suất cho vay
- `usd_vnd` - Tỷ giá USD/VND
- `gov_bond_10y` - Lợi suất TPCP 10 năm
- `cpi` - Chỉ số giá tiêu dùng

**Commodities:**
- `gold` - Giá vàng
- `oil_brent` - Dầu Brent
- `steel` - Thép
- `rubber` - Cao su

---

### 8. Report Tools (3 tools) - Phase 2 Extension

Tra cứu và đọc báo cáo phân tích từ local files hoặc Google Drive.

| Tool | Description | Input | Output |
|------|-------------|-------|--------|
| `vnstock_search_reports` | Tìm kiếm báo cáo | `ticker?`, `sector?`, `source?`, `date_from?` | List matching reports |
| `vnstock_read_report` | Đọc nội dung báo cáo | `report_id` hoặc `path` | Report content (extracted text) |
| `vnstock_get_report_summary` | Tóm tắt báo cáo | `report_id` | Key points, recommendation |

**Report Sources:**

| Source | Path/Config | Formats |
|--------|-------------|---------|
| **Local** | `MCP_SERVER/reports/` | PDF, DOCX, TXT |
| **Google Drive** | OAuth + Folder ID | PDF, Docs, Sheets |

**Implementation Options:**

#### Option A: Local Files Only (Simpler)
```python
# Config
REPORTS_PATH = Path("/Users/buuphan/Dev/Vietnam_dashboard/MCP_SERVER/reports")

# Structure
reports/
├── bsc/
│   ├── ACB_20241215.pdf
│   ├── VCB_20241210.pdf
│   └── ...
├── ssi/
│   └── ...
└── metadata.json  # Index of reports
```

#### Option B: Google Drive Integration
```python
# Config (in .env or config.py)
GOOGLE_DRIVE_FOLDER_ID = "1abc..."
GOOGLE_CREDENTIALS_PATH = "credentials.json"

# Dependencies
google-api-python-client
google-auth-oauthlib
PyPDF2 or pdfplumber  # PDF text extraction
python-docx           # DOCX text extraction
```

**Example Usage:**
```
User: "Có báo cáo nào về VCB gần đây không?"
AI calls: vnstock_search_reports(ticker="VCB", date_from="2024-11-01")
Returns:
| Report | Source | Date | Type |
|--------|--------|------|------|
| VCB_Q3_2024_Analysis.pdf | BSC | 2024-11-15 | Quarterly Review |
| VCB_Strategy_2025.pdf | SSI | 2024-12-01 | Strategy Note |

User: "Đọc báo cáo BSC về VCB"
AI calls: vnstock_read_report(path="bsc/VCB_Q3_2024_Analysis.pdf")
Returns: [Extracted text content from PDF]
```

---

## Implementation Approach

### 1. Data Loading Strategy

```python
# Lazy loading with LRU caching
from functools import lru_cache
from pathlib import Path
import pandas as pd
import time

class DataLoader:
    """Centralized data loading with 5-minute TTL caching."""

    def __init__(self, data_root: Path):
        self.data_root = data_root
        self._cache = {}
        self._cache_ts = {}
        self._ttl = 300  # 5 minutes

    def _load_cached(self, key: str, path: str) -> pd.DataFrame:
        now = time.time()
        if key in self._cache and (now - self._cache_ts[key]) < self._ttl:
            return self._cache[key]

        df = pd.read_parquet(self.data_root / path)
        self._cache[key] = df
        self._cache_ts[key] = now
        return df

    def get_company_fundamentals(self) -> pd.DataFrame:
        return self._load_cached(
            "company_fundamentals",
            "processed/fundamental/company/company_financial_metrics.parquet"
        )

    # ... more loaders
```

### 2. Response Formatters

```python
# formatters.py
def format_dataframe_markdown(df: pd.DataFrame, title: str = None) -> str:
    """Convert DataFrame to Markdown table."""
    lines = []
    if title:
        lines.append(f"## {title}\n")

    # Header
    headers = " | ".join(df.columns)
    separator = " | ".join(["---"] * len(df.columns))
    lines.append(f"| {headers} |")
    lines.append(f"| {separator} |")

    # Rows
    for _, row in df.iterrows():
        values = " | ".join(str(v) for v in row)
        lines.append(f"| {values} |")

    return "\n".join(lines)

def format_metrics_dict(data: dict, title: str = None) -> str:
    """Convert metrics dict to Markdown."""
    lines = []
    if title:
        lines.append(f"## {title}\n")

    for key, value in data.items():
        if isinstance(value, float):
            value = f"{value:,.2f}"
        lines.append(f"- **{key}**: {value}")

    return "\n".join(lines)
```

### 3. Error Handling

```python
# errors.py
class TickerNotFoundError(Exception):
    """Raised when ticker doesn't exist."""
    def __init__(self, ticker: str, suggestions: list = None):
        self.ticker = ticker
        self.suggestions = suggestions or []
        msg = f"Ticker '{ticker}' not found."
        if suggestions:
            msg += f" Did you mean: {', '.join(suggestions)}?"
        super().__init__(msg)

def handle_tool_error(error: Exception, tool_name: str) -> str:
    """Format error for MCP response."""
    if isinstance(error, TickerNotFoundError):
        return str(error)
    if isinstance(error, FileNotFoundError):
        return f"Data file not found. Please run: python3 PROCESSORS/pipelines/run_all_daily_updates.py"
    return f"Error in {tool_name}: {str(error)}"
```

---

## Configuration

### Claude Code Configuration (`.mcp.json`)

Đặt file này tại project root: `/Users/buuphan/Dev/Vietnam_dashboard/.mcp.json`

```json
{
  "mcpServers": {
    "vnstock": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "vnstock_mcp.server"],
      "cwd": "/Users/buuphan/Dev/Vietnam_dashboard/MCP_SERVER",
      "env": {
        "PYTHONPATH": "/Users/buuphan/Dev/Vietnam_dashboard",
        "DATA_ROOT": "/Users/buuphan/Dev/Vietnam_dashboard/DATA"
      }
    }
  }
}
```

### Claude Desktop Configuration

File: `~/.claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "vnstock": {
      "command": "python",
      "args": ["-m", "vnstock_mcp.server"],
      "cwd": "/Users/buuphan/Dev/Vietnam_dashboard/MCP_SERVER",
      "env": {
        "PYTHONPATH": "/Users/buuphan/Dev/Vietnam_dashboard",
        "DATA_ROOT": "/Users/buuphan/Dev/Vietnam_dashboard/DATA"
      }
    }
  }
}
```

### Google Drive Configuration (Phase 2)

File: `MCP_SERVER/.env`

```bash
# Google Drive API
GOOGLE_DRIVE_ENABLED=true
GOOGLE_DRIVE_FOLDER_ID=1abc123xyz...
GOOGLE_CREDENTIALS_PATH=/path/to/credentials.json

# Local Reports
REPORTS_LOCAL_PATH=/Users/buuphan/Dev/Vietnam_dashboard/MCP_SERVER/reports
```

---

## Dependencies

### Core Dependencies

```txt
# requirements.txt

# MCP Framework
mcp>=1.0.0
fastmcp>=0.4.0

# Data Processing
pandas>=2.0.0
pyarrow>=14.0.0
numpy>=1.24.0

# Validation
pydantic>=2.0.0

# Environment
python-dotenv>=1.0.0
```

### Phase 2 Dependencies (Reports)

```txt
# Additional for report reading
PyPDF2>=3.0.0           # PDF text extraction
pdfplumber>=0.10.0      # Better PDF tables
python-docx>=1.0.0      # DOCX reading

# Google Drive (optional)
google-api-python-client>=2.100.0
google-auth-oauthlib>=1.1.0
```

---

## Implementation Phases

### Phase 1: Foundation & Core Tools (Week 1-2)

**Goals:** Working MCP server với data querying tools

- [ ] **1.1** Create project structure (`MCP_SERVER/vnstock_mcp/`)
- [ ] **1.2** Implement `config.py` with data paths
- [ ] **1.3** Implement `DataLoader` service with caching
- [ ] **1.4** Implement `RegistryService` (wrapper for SectorRegistry)
- [ ] **1.5** Create base Pydantic models (`models/base.py`)
- [ ] **1.6** Set up FastMCP server entry point (`server.py`)
- [ ] **1.7** Implement Discovery Tools (5 tools)
- [ ] **1.8** Implement Fundamental Tools (5 tools)
- [ ] **1.9** Create response formatters (`utils/formatters.py`)
- [ ] **1.10** Test with Claude Code

**Deliverables:**
- Working MCP server với 10 tools
- `.mcp.json` configuration
- Basic README

### Phase 2: Technical, Valuation & Sector Tools (Week 2-3)

**Goals:** Complete data querying capabilities

- [ ] **2.1** Implement Technical Tools (4 tools)
- [ ] **2.2** Implement Valuation Tools (5 tools)
- [ ] **2.3** Implement Forecast Tools (3 tools)
- [ ] **2.4** Implement Sector Tools (3 tools)
- [ ] **2.5** Implement Macro Tools (3 tools)
- [ ] **2.6** Add error handling utilities
- [ ] **2.7** Comprehensive testing

**Deliverables:**
- All 28 data tools working
- Error handling complete
- Updated documentation

### Phase 3: Report Integration (Week 3-4) - Extension

**Goals:** Add report search/reading capability

- [ ] **3.1** Design report metadata schema
- [ ] **3.2** Create `reports/` folder structure
- [ ] **3.3** Implement local file report indexing
- [ ] **3.4** Implement PDF/DOCX text extraction
- [ ] **3.5** Implement Report Tools (3 tools)
- [ ] **3.6** (Optional) Google Drive OAuth setup
- [ ] **3.7** (Optional) Google Drive file listing/reading
- [ ] **3.8** Test report search & reading

**Deliverables:**
- 31 total tools (28 data + 3 report)
- Local report reading working
- (Optional) Google Drive integration

### Phase 4: Testing & Documentation (Week 4)

**Goals:** Production-ready với documentation

- [ ] **4.1** Create `evaluation.xml` với 10+ test questions
- [ ] **4.2** Write comprehensive README
- [ ] **4.3** Add usage examples
- [ ] **4.4** Performance optimization
- [ ] **4.5** Final testing with Claude Desktop

**Deliverables:**
- Complete documentation
- Evaluation suite
- Production-ready MCP server

---

## Critical Files to Create

| Priority | File | Purpose |
|----------|------|---------|
| **P0** | `MCP_SERVER/vnstock_mcp/__init__.py` | Package init |
| **P0** | `MCP_SERVER/vnstock_mcp/server.py` | FastMCP entry point |
| **P0** | `MCP_SERVER/vnstock_mcp/config.py` | Configuration |
| **P0** | `MCP_SERVER/vnstock_mcp/services/data_loader.py` | Data access layer |
| **P0** | `MCP_SERVER/vnstock_mcp/tools/discovery_tools.py` | First tools to implement |
| **P1** | `MCP_SERVER/vnstock_mcp/tools/fundamental_tools.py` | Financial queries |
| **P1** | `MCP_SERVER/vnstock_mcp/models/base.py` | Shared enums/types |
| **P1** | `MCP_SERVER/vnstock_mcp/utils/formatters.py` | Response formatting |
| **P2** | `MCP_SERVER/.mcp.json` | Claude Code config |
| **P2** | `MCP_SERVER/requirements.txt` | Dependencies |

---

## Existing Files to Reuse

| File | Reuse For |
|------|-----------|
| [WEBAPP/services/company_service.py](WEBAPP/services/company_service.py) | Data loading patterns, column groups |
| [config/registries/sector_lookup.py](config/registries/sector_lookup.py) | Ticker/sector registry lookups |
| [WEBAPP/core/models/data_models.py](WEBAPP/core/models/data_models.py) | Pydantic model patterns |
| [WEBAPP/services/valuation_service.py](WEBAPP/services/valuation_service.py) | Valuation statistics logic |
| [WEBAPP/services/forecast_service.py](WEBAPP/services/forecast_service.py) | BSC forecast data loading |

---

## Usage Examples

### Example 1: Phân tích cơ bản

```
User: "Phân tích tài chính VNM 4 quý gần nhất"

AI uses tools:
1. vnstock_get_ticker_info("VNM") → Entity type: COMPANY, Sector: Thực phẩm đồ uống
2. vnstock_get_company_financials("VNM", "Quarterly", limit=4)
3. vnstock_get_valuation_stats("VNM", "PE")

AI Response:
## VNM - Vinamilk - Phân tích tài chính

### Kết quả kinh doanh (4 quý gần nhất)
| Quý | Doanh thu | LNST | ROE | Net Margin |
|-----|-----------|------|-----|------------|
| Q3/24 | 15,234 tỷ | 2,156 tỷ | 18.5% | 14.2% |
| ... |

### Định giá
- PE hiện tại: 18.5x (percentile 45%, fair value)
- So với ngành: Cao hơn 10% vs trung vị ngành
```

### Example 2: So sánh ngân hàng

```
User: "So sánh ROE và NIM của 4 ngân hàng lớn nhất"

AI uses tools:
1. vnstock_compare_fundamentals(
     tickers=["VCB", "TCB", "MBB", "ACB"],
     metrics=["roe", "nim", "npl_ratio"]
   )

AI Response:
## So sánh ngân hàng Big 4

| Bank | ROE | NIM | NPL Ratio |
|------|-----|-----|-----------|
| VCB | 19.5% | 3.12% | 1.23% |
| TCB | 17.8% | 3.45% | 1.15% |
| MBB | 21.2% | 3.78% | 1.45% |
| ACB | 19.9% | 3.25% | 1.18% |

**Nhận xét:**
- MBB có ROE và NIM cao nhất
- VCB có NPL thấp nhất (chất lượng tài sản tốt nhất)
```

### Example 3: Tìm cơ hội đầu tư

```
User: "Tìm cổ phiếu có upside > 20% theo BSC và PE < 10"

AI uses tools:
1. vnstock_list_bsc_forecasts(sort_by="upside_pct")
2. vnstock_screen_fundamentals(filters={"pe": {"lt": 10}})
3. Cross-reference results

AI Response:
## Cơ hội đầu tư: Upside > 20% & PE < 10

| Ticker | Sector | PE | Upside | Rating |
|--------|--------|------|--------|--------|
| ACB | Ngân hàng | 7.05 | +19.08% | BUY |
| STB | Ngân hàng | 8.23 | +25.5% | BUY |
| ... |
```

---

## Notes

### Performance Considerations

1. **Caching**: 5-minute TTL phù hợp cho daily data
2. **Lazy Loading**: Chỉ load file khi cần
3. **Column Selection**: Load chỉ columns cần thiết cho queries lớn

### Security

1. **Local files only** (Phase 1): Không cần authentication
2. **Google Drive** (Phase 2): OAuth 2.0, chỉ read-only access
3. **No sensitive data** in responses: Không trả về full file paths

### Future Extensions

1. **Real-time data**: Integrate với vnstock API cho live prices
2. **Watchlist**: Lưu và theo dõi danh sách cổ phiếu
3. **Alerts**: Notify khi có tín hiệu mới
4. **Charts**: Generate chart images (nếu MCP support)

---

## Hướng dẫn chi tiết cho Beginner

### MCP là gì?

**MCP (Model Context Protocol)** là một giao thức chuẩn để kết nối AI (như Claude) với các nguồn dữ liệu bên ngoài.

```
┌─────────────────┐     MCP Protocol      ┌─────────────────┐
│                 │ ◄──────────────────► │                 │
│   Claude AI     │     (JSON-RPC 2.0)   │   MCP Server    │
│   (Client)      │                       │   (vnstock_mcp) │
│                 │                       │                 │
└─────────────────┘                       └────────┬────────┘
                                                   │
                                                   ▼
                                          ┌─────────────────┐
                                          │   Data Files    │
                                          │   (Parquet)     │
                                          └─────────────────┘
```

**Tại sao cần MCP?**
- Claude không thể đọc file trực tiếp từ máy bạn
- MCP server đóng vai trò "cầu nối" giữa Claude và data của bạn
- Claude gọi "tools" trong MCP server để query data

### Cách MCP Server hoạt động

```
1. Bạn hỏi Claude: "ROE của VCB là bao nhiêu?"

2. Claude nhận ra cần data → gọi tool: vnstock_get_latest_fundamentals("VCB")

3. MCP Server nhận request:
   - Load file bank_financial_metrics.parquet
   - Filter row có symbol = "VCB"
   - Lấy giá trị ROE
   - Trả về kết quả

4. Claude nhận kết quả → trả lời bạn: "ROE của VCB là 19.5%"
```

---

## Hướng dẫn cài đặt từng bước

### Bước 1: Kiểm tra Python

```bash
# Kiểm tra Python version (cần 3.10+)
python3 --version
# Output: Python 3.13.x

# Kiểm tra pip
pip3 --version
```

### Bước 2: Tạo thư mục project

```bash
# Di chuyển đến thư mục Vietnam_dashboard
cd /Users/buuphan/Dev/Vietnam_dashboard

# Tạo thư mục MCP_SERVER
mkdir -p MCP_SERVER/vnstock_mcp/{models,tools,services,utils}
mkdir -p MCP_SERVER/reports/{bsc,ssi,vnd,other}
mkdir -p MCP_SERVER/tests

# Kiểm tra cấu trúc
tree MCP_SERVER -L 2
```

### Bước 3: Cài đặt dependencies

```bash
# Di chuyển vào thư mục MCP_SERVER
cd MCP_SERVER

# Tạo file requirements.txt (copy nội dung từ plan)
# Cài đặt
pip3 install -r requirements.txt
```

### Bước 4: Tạo các file cơ bản

Tôi sẽ hướng dẫn chi tiết từng file:

---

## Code Templates với Docstrings đầy đủ

### 1. `__init__.py` - Package Initialization

```python
"""
vnstock_mcp - MCP Server for Vietnamese Stock Market Data
=========================================================

This package provides an MCP (Model Context Protocol) server that enables
AI agents like Claude to query Vietnamese stock market data.

Features:
---------
- Query company/bank/insurance/security financial metrics
- Get historical PE/PB/EV-EBITDA valuation data
- Access technical indicators (RSI, MACD, Bollinger Bands, etc.)
- Search BSC analyst forecasts and ratings
- Analyze sector FA/TA scores and signals
- Read macro/commodity data (gold, oil, FX, interest rates)

Quick Start:
-----------
1. Configure .mcp.json in your project root
2. Start Claude Code in the project directory
3. Ask questions like "ROE của VCB là bao nhiêu?"

Example:
--------
>>> # This runs automatically when Claude calls the server
>>> # You don't need to run this directly
>>> from vnstock_mcp.server import mcp
>>> mcp.run()

Author: Buu Phan
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Buu Phan"

# Export main components for easy access
from vnstock_mcp.server import mcp

__all__ = ["mcp", "__version__"]
```

### 2. `config.py` - Configuration

```python
"""
Configuration Module
====================

Centralized configuration for the vnstock_mcp server.
All paths, constants, and settings are defined here.

Environment Variables:
---------------------
- DATA_ROOT: Path to DATA directory (default: auto-detect)
- REPORTS_PATH: Path to reports directory (default: MCP_SERVER/reports)
- CACHE_TTL: Cache time-to-live in seconds (default: 300)

Usage:
------
>>> from vnstock_mcp.config import Config
>>> config = Config()
>>> print(config.DATA_ROOT)
PosixPath('/Users/buuphan/Dev/Vietnam_dashboard/DATA')
"""

import os
from pathlib import Path
from typing import Optional


def find_project_root() -> Path:
    """
    Find the project root directory by looking for known markers.

    The function walks up the directory tree from the current file
    looking for directories named 'Vietnam_dashboard' or 'stock_dashboard'.

    Returns:
        Path: The project root directory path

    Example:
        >>> root = find_project_root()
        >>> print(root)
        PosixPath('/Users/buuphan/Dev/Vietnam_dashboard')
    """
    current = Path(__file__).resolve()

    # Walk up the directory tree
    while current.parent != current:
        if current.name in ['Vietnam_dashboard', 'stock_dashboard']:
            return current
        current = current.parent

    # Fallback: assume MCP_SERVER is in project root
    return Path(__file__).resolve().parent.parent.parent


class Config:
    """
    Configuration class for vnstock_mcp server.

    This class manages all configuration settings including paths,
    cache settings, and feature flags.

    Attributes:
        PROJECT_ROOT (Path): Root directory of the Vietnam_dashboard project
        DATA_ROOT (Path): Path to DATA directory containing parquet files
        MCP_SERVER_ROOT (Path): Path to MCP_SERVER directory
        REPORTS_PATH (Path): Path to reports storage directory
        CACHE_TTL (int): Cache time-to-live in seconds

    Example:
        >>> config = Config()
        >>>
        >>> # Access paths
        >>> print(config.DATA_ROOT)
        >>> print(config.get_parquet_path("company_fundamentals"))
        >>>
        >>> # Check if data exists
        >>> if config.DATA_ROOT.exists():
        ...     print("Data directory found!")
    """

    def __init__(self):
        """
        Initialize configuration with auto-detected or environment paths.

        Priority:
        1. Environment variables (DATA_ROOT, etc.)
        2. Auto-detected paths based on project structure
        """
        # Project root (auto-detect)
        self.PROJECT_ROOT = find_project_root()

        # Data root (from env or default)
        data_root_env = os.environ.get("DATA_ROOT")
        if data_root_env:
            self.DATA_ROOT = Path(data_root_env)
        else:
            self.DATA_ROOT = self.PROJECT_ROOT / "DATA"

        # MCP Server root
        self.MCP_SERVER_ROOT = self.PROJECT_ROOT / "MCP_SERVER"

        # Reports path
        reports_env = os.environ.get("REPORTS_PATH")
        if reports_env:
            self.REPORTS_PATH = Path(reports_env)
        else:
            self.REPORTS_PATH = self.MCP_SERVER_ROOT / "reports"

        # Cache settings
        self.CACHE_TTL = int(os.environ.get("CACHE_TTL", 300))  # 5 minutes

        # Validate paths exist
        self._validate_paths()

    def _validate_paths(self):
        """
        Validate that required directories exist.

        Raises:
            FileNotFoundError: If DATA_ROOT doesn't exist
        """
        if not self.DATA_ROOT.exists():
            raise FileNotFoundError(
                f"DATA directory not found: {self.DATA_ROOT}\n"
                f"Please ensure the DATA directory exists with parquet files.\n"
                f"You can set DATA_ROOT environment variable to override."
            )

    # =========================================================================
    # Parquet File Paths
    # =========================================================================

    # Fundamental Data Paths
    COMPANY_FUNDAMENTALS_PATH = "processed/fundamental/company/company_financial_metrics.parquet"
    BANK_FUNDAMENTALS_PATH = "processed/fundamental/bank/bank_financial_metrics.parquet"
    INSURANCE_FUNDAMENTALS_PATH = "processed/fundamental/insurance/insurance_financial_metrics.parquet"
    SECURITY_FUNDAMENTALS_PATH = "processed/fundamental/security/security_financial_metrics.parquet"

    # Valuation Data Paths
    PE_HISTORICAL_PATH = "processed/valuation/pe/historical/historical_pe.parquet"
    PB_HISTORICAL_PATH = "processed/valuation/pb/historical/historical_pb.parquet"
    PS_HISTORICAL_PATH = "processed/valuation/ps/historical/historical_ps.parquet"
    EV_EBITDA_HISTORICAL_PATH = "processed/valuation/ev_ebitda/historical/historical_ev_ebitda.parquet"
    VNINDEX_VALUATION_PATH = "processed/valuation/vnindex/vnindex_valuation_refined.parquet"

    # Technical Data Paths
    TECHNICAL_BASIC_PATH = "processed/technical/basic_data.parquet"
    MARKET_BREADTH_PATH = "processed/technical/market_breadth/market_breadth_daily.parquet"
    MONEY_FLOW_PATH = "processed/technical/money_flow/individual_money_flow.parquet"

    # Forecast Data Paths
    BSC_INDIVIDUAL_PATH = "processed/forecast/bsc/bsc_individual.parquet"
    BSC_SECTOR_PATH = "processed/forecast/bsc/bsc_sector_valuation.parquet"

    # Sector Analysis Paths
    SECTOR_SCORES_PATH = "processed/sector/sector_combined_scores.parquet"
    SECTOR_FUNDAMENTALS_PATH = "processed/sector/sector_fundamental_metrics.parquet"

    # Macro Data Paths
    MACRO_COMMODITY_PATH = "processed/macro_commodity/macro_commodity_unified.parquet"

    # Metadata Paths
    SECTOR_REGISTRY_PATH = "metadata/sector_industry_registry.json"

    def get_parquet_path(self, name: str) -> Path:
        """
        Get full path to a parquet file by name.

        Args:
            name: Name of the data file (e.g., "company_fundamentals")

        Returns:
            Path: Full path to the parquet file

        Raises:
            ValueError: If name is not recognized

        Example:
            >>> config = Config()
            >>> path = config.get_parquet_path("company_fundamentals")
            >>> print(path)
            PosixPath('/Users/.../DATA/processed/fundamental/company/company_financial_metrics.parquet')
        """
        path_mapping = {
            "company_fundamentals": self.COMPANY_FUNDAMENTALS_PATH,
            "bank_fundamentals": self.BANK_FUNDAMENTALS_PATH,
            "insurance_fundamentals": self.INSURANCE_FUNDAMENTALS_PATH,
            "security_fundamentals": self.SECURITY_FUNDAMENTALS_PATH,
            "pe_historical": self.PE_HISTORICAL_PATH,
            "pb_historical": self.PB_HISTORICAL_PATH,
            "ps_historical": self.PS_HISTORICAL_PATH,
            "ev_ebitda_historical": self.EV_EBITDA_HISTORICAL_PATH,
            "vnindex_valuation": self.VNINDEX_VALUATION_PATH,
            "technical_basic": self.TECHNICAL_BASIC_PATH,
            "market_breadth": self.MARKET_BREADTH_PATH,
            "money_flow": self.MONEY_FLOW_PATH,
            "bsc_individual": self.BSC_INDIVIDUAL_PATH,
            "bsc_sector": self.BSC_SECTOR_PATH,
            "sector_scores": self.SECTOR_SCORES_PATH,
            "sector_fundamentals": self.SECTOR_FUNDAMENTALS_PATH,
            "macro_commodity": self.MACRO_COMMODITY_PATH,
        }

        if name not in path_mapping:
            raise ValueError(
                f"Unknown data file: '{name}'\n"
                f"Available options: {list(path_mapping.keys())}"
            )

        return self.DATA_ROOT / path_mapping[name]


# Global config instance (singleton pattern)
_config: Optional[Config] = None


def get_config() -> Config:
    """
    Get the global configuration instance.

    Uses singleton pattern to ensure only one Config instance exists.

    Returns:
        Config: The global configuration instance

    Example:
        >>> from vnstock_mcp.config import get_config
        >>> config = get_config()
        >>> print(config.DATA_ROOT)
    """
    global _config
    if _config is None:
        _config = Config()
    return _config
```

### 3. `services/data_loader.py` - Data Access Layer

```python
"""
Data Loader Service
===================

Centralized data loading service with caching for efficient data access.
This service handles loading parquet files and provides caching to avoid
repeated disk reads.

Features:
---------
- Lazy loading: Files are only loaded when first accessed
- TTL caching: Data is cached for 5 minutes (configurable)
- Type-specific loaders: Separate methods for each data type
- Error handling: Clear error messages when files are missing

Architecture:
------------
```
┌─────────────────┐
│   MCP Tools     │
│ (discovery,     │
│  fundamental,   │
│  valuation...)  │
└────────┬────────┘
         │ calls
         ▼
┌─────────────────┐
│   DataLoader    │  ◄── Singleton instance
│   (caching)     │
└────────┬────────┘
         │ reads
         ▼
┌─────────────────┐
│  Parquet Files  │
│  (DATA/*.parquet│
└─────────────────┘
```

Usage:
------
>>> from vnstock_mcp.services.data_loader import get_data_loader
>>>
>>> loader = get_data_loader()
>>>
>>> # Load company fundamentals
>>> df = loader.get_company_fundamentals()
>>>
>>> # Filter by ticker
>>> vnm_data = df[df['symbol'] == 'VNM']

Author: Buu Phan
"""

import time
from pathlib import Path
from typing import Dict, Optional, Any
import pandas as pd
import logging

from vnstock_mcp.config import get_config, Config

# Set up logging
logger = logging.getLogger(__name__)


class DataLoader:
    """
    Centralized data loading service with TTL caching.

    This class provides methods to load various data files (parquet format)
    with built-in caching to improve performance. Each file is cached for
    a configurable time period (default 5 minutes).

    Attributes:
        config (Config): Configuration instance with paths
        _cache (Dict): Internal cache storage for DataFrames
        _cache_timestamps (Dict): Timestamps for cache entries

    Example:
        >>> loader = DataLoader()
        >>>
        >>> # First call: loads from disk
        >>> df1 = loader.get_company_fundamentals()
        >>>
        >>> # Second call within 5 minutes: returns from cache (faster!)
        >>> df2 = loader.get_company_fundamentals()
        >>>
        >>> # Force refresh cache
        >>> df3 = loader.get_company_fundamentals(force_refresh=True)

    Note:
        Use `get_data_loader()` to get the singleton instance instead of
        creating new instances directly.
    """

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize DataLoader with configuration.

        Args:
            config: Configuration instance. If None, uses global config.

        Example:
            >>> # Using default config (recommended)
            >>> loader = DataLoader()
            >>>
            >>> # Using custom config
            >>> from vnstock_mcp.config import Config
            >>> custom_config = Config()
            >>> loader = DataLoader(config=custom_config)
        """
        self.config = config or get_config()
        self._cache: Dict[str, pd.DataFrame] = {}
        self._cache_timestamps: Dict[str, float] = {}

        logger.info(f"DataLoader initialized with DATA_ROOT: {self.config.DATA_ROOT}")

    def _is_cache_valid(self, cache_key: str) -> bool:
        """
        Check if cached data is still valid (not expired).

        Args:
            cache_key: The key identifying the cached data

        Returns:
            bool: True if cache is valid, False if expired or missing

        Example:
            >>> loader = DataLoader()
            >>> loader._load_cached("test_key", "some/path.parquet")
            >>> loader._is_cache_valid("test_key")
            True
            >>> # After 5 minutes...
            >>> loader._is_cache_valid("test_key")
            False
        """
        if cache_key not in self._cache:
            return False

        cache_time = self._cache_timestamps.get(cache_key, 0)
        elapsed = time.time() - cache_time

        return elapsed < self.config.CACHE_TTL

    def _load_cached(
        self,
        cache_key: str,
        relative_path: str,
        force_refresh: bool = False
    ) -> pd.DataFrame:
        """
        Load data from cache or disk with caching logic.

        This is the core method that handles the caching mechanism.
        It checks if valid cached data exists, and if not, loads from disk.

        Args:
            cache_key: Unique key for this data in the cache
            relative_path: Path relative to DATA_ROOT
            force_refresh: If True, bypass cache and reload from disk

        Returns:
            pd.DataFrame: The loaded data

        Raises:
            FileNotFoundError: If the parquet file doesn't exist

        Example:
            >>> loader = DataLoader()
            >>> df = loader._load_cached(
            ...     cache_key="company_fundamentals",
            ...     relative_path="processed/fundamental/company/company_financial_metrics.parquet"
            ... )
        """
        # Check cache validity
        if not force_refresh and self._is_cache_valid(cache_key):
            logger.debug(f"Cache hit for {cache_key}")
            return self._cache[cache_key]

        # Load from disk
        full_path = self.config.DATA_ROOT / relative_path

        if not full_path.exists():
            raise FileNotFoundError(
                f"Data file not found: {full_path}\n"
                f"Please run the data pipeline to generate this file:\n"
                f"  python3 PROCESSORS/pipelines/run_all_daily_updates.py"
            )

        logger.info(f"Loading {cache_key} from disk: {full_path}")
        start_time = time.time()

        df = pd.read_parquet(full_path)

        elapsed = time.time() - start_time
        logger.info(f"Loaded {cache_key}: {len(df)} rows in {elapsed:.2f}s")

        # Update cache
        self._cache[cache_key] = df
        self._cache_timestamps[cache_key] = time.time()

        return df

    def clear_cache(self, cache_key: Optional[str] = None):
        """
        Clear cached data.

        Args:
            cache_key: Specific key to clear. If None, clears all cache.

        Example:
            >>> loader = DataLoader()
            >>>
            >>> # Clear specific cache
            >>> loader.clear_cache("company_fundamentals")
            >>>
            >>> # Clear all cache
            >>> loader.clear_cache()
        """
        if cache_key:
            self._cache.pop(cache_key, None)
            self._cache_timestamps.pop(cache_key, None)
            logger.info(f"Cleared cache for {cache_key}")
        else:
            self._cache.clear()
            self._cache_timestamps.clear()
            logger.info("Cleared all cache")

    # =========================================================================
    # Fundamental Data Loaders
    # =========================================================================

    def get_company_fundamentals(self, force_refresh: bool = False) -> pd.DataFrame:
        """
        Load company financial metrics data.

        Returns data for non-financial companies including:
        - Income statement: revenue, profit margins, EPS
        - Balance sheet: assets, liabilities, equity
        - Ratios: ROE, ROA, current ratio, debt-to-equity

        Args:
            force_refresh: If True, reload from disk ignoring cache

        Returns:
            pd.DataFrame: Company financial metrics with columns:
                - symbol: Stock ticker (e.g., 'VNM', 'FPT')
                - report_date: Report date
                - year, quarter: Period identifiers
                - net_revenue: Revenue in VND
                - npatmi: Net profit after tax
                - roe, roa: Return ratios
                - gross_margin, net_margin: Margin ratios
                - eps, bvps: Per-share metrics
                - ... (61 columns total)

        Example:
            >>> loader = get_data_loader()
            >>> df = loader.get_company_fundamentals()
            >>>
            >>> # Get VNM data
            >>> vnm = df[df['symbol'] == 'VNM']
            >>> print(vnm[['report_date', 'net_revenue', 'roe']].tail())
        """
        return self._load_cached(
            cache_key="company_fundamentals",
            relative_path=self.config.COMPANY_FUNDAMENTALS_PATH,
            force_refresh=force_refresh
        )

    def get_bank_fundamentals(self, force_refresh: bool = False) -> pd.DataFrame:
        """
        Load bank financial metrics data.

        Returns bank-specific metrics including:
        - NIM (Net Interest Margin)
        - NPL Ratio (Non-Performing Loans)
        - CASA Ratio
        - CAR (Capital Adequacy Ratio)
        - CIR (Cost-to-Income Ratio)

        Args:
            force_refresh: If True, reload from disk ignoring cache

        Returns:
            pd.DataFrame: Bank financial metrics (55 columns)

        Example:
            >>> loader = get_data_loader()
            >>> df = loader.get_bank_fundamentals()
            >>>
            >>> # Compare NIM across banks
            >>> latest = df.groupby('symbol').last()
            >>> print(latest[['nim', 'npl_ratio', 'casa_ratio']].sort_values('nim'))
        """
        return self._load_cached(
            cache_key="bank_fundamentals",
            relative_path=self.config.BANK_FUNDAMENTALS_PATH,
            force_refresh=force_refresh
        )

    # =========================================================================
    # Valuation Data Loaders
    # =========================================================================

    def get_pe_historical(self, force_refresh: bool = False) -> pd.DataFrame:
        """
        Load historical PE ratio data.

        Contains daily PE ratios for all tickers from 1997 to present.

        Args:
            force_refresh: If True, reload from disk ignoring cache

        Returns:
            pd.DataFrame: Historical PE data with columns:
                - symbol: Stock ticker
                - date: Trading date
                - close_price: Closing price
                - pe_ratio: PE ratio
                - ttm_earning_billion_vnd: TTM earnings
                - sector: Industry sector

        Example:
            >>> loader = get_data_loader()
            >>> df = loader.get_pe_historical()
            >>>
            >>> # Get ACB PE history for 2024
            >>> acb_pe = df[(df['symbol'] == 'ACB') & (df['date'].dt.year == 2024)]
            >>> print(acb_pe['pe_ratio'].describe())
        """
        return self._load_cached(
            cache_key="pe_historical",
            relative_path=self.config.PE_HISTORICAL_PATH,
            force_refresh=force_refresh
        )

    def get_pb_historical(self, force_refresh: bool = False) -> pd.DataFrame:
        """
        Load historical PB ratio data.

        Contains daily PB (Price-to-Book) ratios for all tickers.

        Args:
            force_refresh: If True, reload from disk ignoring cache

        Returns:
            pd.DataFrame: Historical PB data
        """
        return self._load_cached(
            cache_key="pb_historical",
            relative_path=self.config.PB_HISTORICAL_PATH,
            force_refresh=force_refresh
        )

    # =========================================================================
    # Technical Data Loaders
    # =========================================================================

    def get_technical_basic(self, force_refresh: bool = False) -> pd.DataFrame:
        """
        Load technical indicators data.

        Contains OHLCV data plus 30+ technical indicators:
        - Moving Averages: SMA(20,50,100,200), EMA(20,50)
        - Momentum: RSI(14), MACD, Stochastic
        - Volatility: Bollinger Bands, ATR(14)
        - Volume: OBV, CMF, MFI
        - Trend: ADX, CCI

        Args:
            force_refresh: If True, reload from disk ignoring cache

        Returns:
            pd.DataFrame: Technical data (40 columns)

        Example:
            >>> loader = get_data_loader()
            >>> df = loader.get_technical_basic()
            >>>
            >>> # Get latest RSI for all tickers
            >>> latest = df.sort_values('date').groupby('symbol').last()
            >>> oversold = latest[latest['rsi_14'] < 30]
            >>> print(f"Oversold stocks: {len(oversold)}")
        """
        return self._load_cached(
            cache_key="technical_basic",
            relative_path=self.config.TECHNICAL_BASIC_PATH,
            force_refresh=force_refresh
        )

    # =========================================================================
    # Forecast Data Loaders
    # =========================================================================

    def get_bsc_individual(self, force_refresh: bool = False) -> pd.DataFrame:
        """
        Load BSC analyst forecasts for individual stocks.

        Contains forecasts for 93 stocks including:
        - Target price and upside potential
        - Rating (BUY/HOLD/SELL)
        - EPS forecasts for 2025/2026
        - Revenue/profit growth forecasts
        - YTD achievement vs full-year targets

        Args:
            force_refresh: If True, reload from disk ignoring cache

        Returns:
            pd.DataFrame: BSC forecasts (32 columns)

        Example:
            >>> loader = get_data_loader()
            >>> df = loader.get_bsc_individual()
            >>>
            >>> # Find stocks with > 20% upside
            >>> high_upside = df[df['upside_pct'] > 20]
            >>> print(high_upside[['symbol', 'target_price', 'upside_pct', 'rating']])
        """
        return self._load_cached(
            cache_key="bsc_individual",
            relative_path=self.config.BSC_INDIVIDUAL_PATH,
            force_refresh=force_refresh
        )

    # =========================================================================
    # Sector Data Loaders
    # =========================================================================

    def get_sector_scores(self, force_refresh: bool = False) -> pd.DataFrame:
        """
        Load sector FA/TA scores and signals.

        Contains daily scores for 19 sectors:
        - FA Score (0-100): Fundamental analysis score
        - TA Score (0-100): Technical analysis score
        - Combined signal: MUA/BÁN/GIỮ (BUY/SELL/HOLD)
        - Signal strength (1-5)

        Args:
            force_refresh: If True, reload from disk ignoring cache

        Returns:
            pd.DataFrame: Sector scores (23 columns)

        Example:
            >>> loader = get_data_loader()
            >>> df = loader.get_sector_scores()
            >>>
            >>> # Get latest scores
            >>> latest = df.sort_values('date').groupby('sector_code').last()
            >>> buy_signals = latest[latest['signal'] == 'MUA']
            >>> print(f"Sectors with BUY signal: {list(buy_signals.index)}")
        """
        return self._load_cached(
            cache_key="sector_scores",
            relative_path=self.config.SECTOR_SCORES_PATH,
            force_refresh=force_refresh
        )

    # =========================================================================
    # Macro Data Loaders
    # =========================================================================

    def get_macro_commodity(self, force_refresh: bool = False) -> pd.DataFrame:
        """
        Load macro and commodity data.

        Contains unified macro/commodity data:
        - Interest rates (deposit, lending)
        - Exchange rates (USD/VND)
        - Government bond yields
        - Commodity prices (gold, oil, steel)

        Args:
            force_refresh: If True, reload from disk ignoring cache

        Returns:
            pd.DataFrame: Macro/commodity data
        """
        return self._load_cached(
            cache_key="macro_commodity",
            relative_path=self.config.MACRO_COMMODITY_PATH,
            force_refresh=force_refresh
        )


# =============================================================================
# Singleton Pattern
# =============================================================================

_data_loader: Optional[DataLoader] = None


def get_data_loader() -> DataLoader:
    """
    Get the global DataLoader singleton instance.

    This function ensures only one DataLoader instance exists throughout
    the application lifetime, which is important for efficient caching.

    Returns:
        DataLoader: The global DataLoader instance

    Example:
        >>> from vnstock_mcp.services.data_loader import get_data_loader
        >>>
        >>> # Get the singleton instance
        >>> loader = get_data_loader()
        >>>
        >>> # Use it to load data
        >>> df = loader.get_company_fundamentals()

    Note:
        Always use this function instead of creating DataLoader() directly
        to ensure caching works correctly across the application.
    """
    global _data_loader
    if _data_loader is None:
        _data_loader = DataLoader()
    return _data_loader
```

### 4. `server.py` - Main MCP Server Entry Point

```python
#!/usr/bin/env python3
"""
MCP Server Entry Point
======================

Main entry point for the vnstock_mcp MCP server.
This file initializes the FastMCP server and registers all tools.

How it works:
-------------
1. FastMCP creates an MCP server instance
2. Tools are registered from various tool modules
3. Server listens for requests from Claude via stdio
4. When Claude calls a tool, the server executes it and returns results

Running the server:
------------------
The server is typically started by Claude automatically based on .mcp.json config.
You can also run it manually for testing:

    $ python -m vnstock_mcp.server

Usage with Claude Code:
-----------------------
1. Create .mcp.json in your project root
2. Start Claude Code in the project directory
3. Ask questions about Vietnamese stocks
4. Claude will automatically use the tools

Example .mcp.json:
```json
{
  "mcpServers": {
    "vnstock": {
      "command": "python",
      "args": ["-m", "vnstock_mcp.server"],
      "cwd": "/path/to/MCP_SERVER"
    }
  }
}
```

Author: Buu Phan
"""

import logging
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =============================================================================
# Create FastMCP Server Instance
# =============================================================================

mcp = FastMCP(
    name="vnstock_mcp",
    version="1.0.0",
    description=(
        "MCP Server for Vietnamese Stock Market Data. "
        "Query company financials, valuations, technical indicators, "
        "analyst forecasts, sector analysis, and macro data."
    )
)

# =============================================================================
# Register Tools
# =============================================================================

# Import and register all tool modules
# Each module has a register(mcp) function that adds its tools

from vnstock_mcp.tools import discovery_tools
from vnstock_mcp.tools import fundamental_tools
from vnstock_mcp.tools import technical_tools
from vnstock_mcp.tools import valuation_tools
from vnstock_mcp.tools import forecast_tools
from vnstock_mcp.tools import sector_tools
from vnstock_mcp.tools import macro_tools

# Register all tools with the server
discovery_tools.register(mcp)
fundamental_tools.register(mcp)
technical_tools.register(mcp)
valuation_tools.register(mcp)
forecast_tools.register(mcp)
sector_tools.register(mcp)
macro_tools.register(mcp)

logger.info("All tools registered successfully")

# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    logger.info("Starting vnstock_mcp server...")
    mcp.run()
```

### 5. `tools/discovery_tools.py` - Example Tool Implementation

```python
"""
Discovery Tools
===============

Tools for discovering and searching tickers, sectors, and metadata.
These are the most basic tools that help users find what data is available.

Tools:
------
1. vnstock_list_tickers - List all available tickers
2. vnstock_get_ticker_info - Get detailed info for a ticker
3. vnstock_list_sectors - List all 19 sectors
4. vnstock_search_tickers - Search tickers by keyword
5. vnstock_get_peers - Get peer companies in same sector

Usage:
------
>>> # These tools are called by Claude, not directly
>>> # Example conversation:
>>>
>>> User: "List all banks"
>>> Claude calls: vnstock_list_tickers(entity_type="BANK")
>>> Returns: ACB, VCB, TCB, MBB, ...

Author: Buu Phan
"""

import json
from typing import Optional, List
from mcp.server.fastmcp import FastMCP

from vnstock_mcp.services.data_loader import get_data_loader
from vnstock_mcp.utils.formatters import format_list_markdown, format_dict_markdown
from vnstock_mcp.utils.errors import handle_tool_error


def register(mcp: FastMCP):
    """
    Register all discovery tools with the MCP server.

    This function is called from server.py to add discovery tools
    to the MCP server instance.

    Args:
        mcp: The FastMCP server instance
    """

    # =========================================================================
    # Tool 1: List Tickers
    # =========================================================================

    @mcp.tool(
        name="vnstock_list_tickers",
        annotations={
            "title": "List Available Tickers",
            "readOnlyHint": True,
            "idempotentHint": True
        }
    )
    async def vnstock_list_tickers(
        entity_type: Optional[str] = None,
        sector: Optional[str] = None,
        limit: int = 50
    ) -> str:
        """
        List all available stock tickers with optional filtering.

        This tool returns a list of ticker symbols that have data available
        in the system. You can filter by entity type (BANK, COMPANY, etc.)
        or by sector (Ngân hàng, Bất động sản, etc.).

        Args:
            entity_type: Filter by entity type. Options:
                - "BANK" - Banks (24 tickers)
                - "COMPANY" - Non-financial companies (261 tickers)
                - "INSURANCE" - Insurance companies (5 tickers)
                - "SECURITY" - Securities/brokerages (27 tickers)
                - None - All tickers (default)
            sector: Filter by sector name (Vietnamese). Examples:
                - "Ngân hàng"
                - "Bất động sản"
                - "Thực phẩm đồ uống"
                - None - All sectors (default)
            limit: Maximum number of tickers to return (default: 50)

        Returns:
            str: Markdown formatted list of tickers with basic info

        Examples:
            # List all banks
            >>> vnstock_list_tickers(entity_type="BANK")

            # List real estate companies
            >>> vnstock_list_tickers(sector="Bất động sản")

            # List top 10 companies
            >>> vnstock_list_tickers(entity_type="COMPANY", limit=10)
        """
        try:
            # Import SectorRegistry for ticker lookups
            import sys
            sys.path.insert(0, str(get_data_loader().config.PROJECT_ROOT))
            from config.registries import SectorRegistry

            registry = SectorRegistry()

            # Get tickers based on filters
            if entity_type:
                tickers = registry.get_tickers_by_entity_type(entity_type.upper())
            elif sector:
                tickers = registry.get_tickers_by_sector(sector)
            else:
                tickers = registry.get_all_tickers()

            # Apply limit
            tickers = tickers[:limit]

            # Build response
            result_lines = [
                f"## Available Tickers",
                f"**Count:** {len(tickers)}",
                f"**Filter:** entity_type={entity_type or 'All'}, sector={sector or 'All'}",
                "",
                "| # | Ticker | Entity Type | Sector |",
                "|---|--------|-------------|--------|"
            ]

            for i, ticker in enumerate(tickers, 1):
                info = registry.get_ticker(ticker) or {}
                etype = info.get('entity_type', 'N/A')
                sec = info.get('sector', 'N/A')
                result_lines.append(f"| {i} | {ticker} | {etype} | {sec} |")

            if len(tickers) == limit:
                result_lines.append("")
                result_lines.append(f"*Showing first {limit} results. Use `limit` parameter for more.*")

            return "\n".join(result_lines)

        except Exception as e:
            return handle_tool_error(e, "vnstock_list_tickers")

    # =========================================================================
    # Tool 2: Get Ticker Info
    # =========================================================================

    @mcp.tool(
        name="vnstock_get_ticker_info",
        annotations={
            "title": "Get Ticker Information",
            "readOnlyHint": True,
            "idempotentHint": True
        }
    )
    async def vnstock_get_ticker_info(ticker: str) -> str:
        """
        Get detailed information about a specific ticker.

        Returns metadata about the ticker including entity type,
        sector classification, exchange, and industry code.

        Args:
            ticker: Stock symbol (e.g., "VCB", "VNM", "FPT")
                   Case-insensitive (will be converted to uppercase)

        Returns:
            str: Markdown formatted ticker information including:
                - Entity type (BANK, COMPANY, etc.)
                - Sector (Vietnamese name)
                - Exchange (HOSE, HNX, UPCOM)
                - Industry code
                - Calculator class (for internal use)

        Examples:
            # Get info for Vietcombank
            >>> vnstock_get_ticker_info("VCB")

            # Get info for Vinamilk
            >>> vnstock_get_ticker_info("vnm")  # lowercase works too
        """
        try:
            # Import SectorRegistry
            import sys
            sys.path.insert(0, str(get_data_loader().config.PROJECT_ROOT))
            from config.registries import SectorRegistry

            registry = SectorRegistry()

            # Normalize ticker
            ticker = ticker.upper().strip()

            # Get ticker info
            info = registry.get_ticker(ticker)

            if not info:
                # Ticker not found - suggest alternatives
                all_tickers = registry.get_all_tickers()
                # Simple fuzzy match: find tickers starting with same letters
                suggestions = [t for t in all_tickers if t.startswith(ticker[:2])][:5]

                return (
                    f"## Ticker Not Found\n\n"
                    f"Ticker `{ticker}` was not found in the registry.\n\n"
                    f"**Did you mean:** {', '.join(suggestions) if suggestions else 'N/A'}\n\n"
                    f"Use `vnstock_list_tickers()` to see all available tickers."
                )

            # Build response
            result = f"""## {ticker} - Ticker Information

| Field | Value |
|-------|-------|
| **Symbol** | {ticker} |
| **Entity Type** | {info.get('entity_type', 'N/A')} |
| **Sector** | {info.get('sector', 'N/A')} |
| **Exchange** | {info.get('exchange', 'N/A')} |
| **Industry Code** | {info.get('industry_code', 'N/A')} |

**Available Data:**
- Fundamental metrics: Yes
- Valuation history: Yes
- Technical indicators: Yes
- BSC Forecast: {_check_bsc_coverage(ticker)}
"""
            return result

        except Exception as e:
            return handle_tool_error(e, "vnstock_get_ticker_info")

    # =========================================================================
    # Tool 3: List Sectors
    # =========================================================================

    @mcp.tool(
        name="vnstock_list_sectors",
        annotations={
            "title": "List All Sectors",
            "readOnlyHint": True,
            "idempotentHint": True
        }
    )
    async def vnstock_list_sectors(entity_type: Optional[str] = None) -> str:
        """
        List all 19 industry sectors with ticker counts.

        Returns the list of Vietnamese industry sectors (ICB L2 classification)
        along with how many tickers belong to each sector.

        Args:
            entity_type: Optional filter by entity type
                - "BANK" - Show only bank sectors
                - "COMPANY" - Show only company sectors
                - None - Show all sectors (default)

        Returns:
            str: Markdown table of sectors with:
                - Sector name (Vietnamese)
                - Entity type
                - Number of tickers
                - Key metrics tracked

        Examples:
            # List all sectors
            >>> vnstock_list_sectors()

            # List only company sectors
            >>> vnstock_list_sectors(entity_type="COMPANY")
        """
        try:
            import sys
            sys.path.insert(0, str(get_data_loader().config.PROJECT_ROOT))
            from config.registries import SectorRegistry

            registry = SectorRegistry()

            all_sectors = registry.get_all_sectors()

            result_lines = [
                "## Vietnamese Stock Market Sectors",
                "",
                "| # | Sector | Entity Type | Tickers | Key Metrics |",
                "|---|--------|-------------|---------|-------------|"
            ]

            i = 0
            for sector_name in all_sectors:
                sector_info = registry.get_sector(sector_name)
                if not sector_info:
                    continue

                etype = sector_info.get('entity_type', 'N/A')

                # Apply entity_type filter
                if entity_type and etype != entity_type.upper():
                    continue

                i += 1
                count = sector_info.get('count', 0)
                key_metrics = ", ".join(sector_info.get('key_metrics', [])[:3])

                result_lines.append(f"| {i} | {sector_name} | {etype} | {count} | {key_metrics} |")

            result_lines.append("")
            result_lines.append(f"**Total Sectors:** {i}")

            return "\n".join(result_lines)

        except Exception as e:
            return handle_tool_error(e, "vnstock_list_sectors")

    # =========================================================================
    # Tool 4: Search Tickers
    # =========================================================================

    @mcp.tool(
        name="vnstock_search_tickers",
        annotations={
            "title": "Search Tickers",
            "readOnlyHint": True,
            "idempotentHint": True
        }
    )
    async def vnstock_search_tickers(query: str, limit: int = 20) -> str:
        """
        Search for tickers by keyword or name pattern.

        Searches across ticker symbols and sector names to find
        matching stocks.

        Args:
            query: Search keyword (case-insensitive). Examples:
                - "bank" - Find banking-related stocks
                - "VN" - Find tickers starting with VN
                - "thực phẩm" - Find food sector stocks
            limit: Maximum results to return (default: 20)

        Returns:
            str: Markdown list of matching tickers with relevance

        Examples:
            >>> vnstock_search_tickers("ngân hàng")  # Search banks
            >>> vnstock_search_tickers("FPT")  # Search by symbol
            >>> vnstock_search_tickers("bất động sản")  # Search real estate
        """
        try:
            import sys
            sys.path.insert(0, str(get_data_loader().config.PROJECT_ROOT))
            from config.registries import SectorRegistry

            registry = SectorRegistry()
            query_lower = query.lower().strip()

            results = []

            # Search all tickers
            for ticker in registry.get_all_tickers():
                info = registry.get_ticker(ticker)
                if not info:
                    continue

                sector = info.get('sector', '').lower()

                # Match on ticker symbol or sector name
                if query_lower in ticker.lower() or query_lower in sector:
                    results.append({
                        'ticker': ticker,
                        'entity_type': info.get('entity_type'),
                        'sector': info.get('sector'),
                        'match': 'ticker' if query_lower in ticker.lower() else 'sector'
                    })

                    if len(results) >= limit:
                        break

            if not results:
                return (
                    f"## No Results Found\n\n"
                    f"No tickers found matching '{query}'.\n\n"
                    f"Try:\n"
                    f"- Different spelling\n"
                    f"- Sector name in Vietnamese (e.g., 'Ngân hàng')\n"
                    f"- `vnstock_list_sectors()` to see all sectors"
                )

            result_lines = [
                f"## Search Results for '{query}'",
                f"**Found:** {len(results)} tickers",
                "",
                "| Ticker | Entity Type | Sector | Match Type |",
                "|--------|-------------|--------|------------|"
            ]

            for r in results:
                result_lines.append(
                    f"| {r['ticker']} | {r['entity_type']} | {r['sector']} | {r['match']} |"
                )

            return "\n".join(result_lines)

        except Exception as e:
            return handle_tool_error(e, "vnstock_search_tickers")

    # =========================================================================
    # Tool 5: Get Peers
    # =========================================================================

    @mcp.tool(
        name="vnstock_get_peers",
        annotations={
            "title": "Get Peer Companies",
            "readOnlyHint": True,
            "idempotentHint": True
        }
    )
    async def vnstock_get_peers(
        ticker: str,
        limit: int = 10,
        exclude_self: bool = True
    ) -> str:
        """
        Get peer companies in the same sector.

        Returns a list of companies that are in the same industry sector
        as the given ticker. Useful for peer comparison analysis.

        Args:
            ticker: Stock symbol to find peers for
            limit: Maximum number of peers to return (default: 10)
            exclude_self: Whether to exclude the input ticker (default: True)

        Returns:
            str: Markdown list of peer tickers with sector info

        Examples:
            # Find peers for Vietcombank
            >>> vnstock_get_peers("VCB")  # Returns other banks

            # Find peers for Vinamilk
            >>> vnstock_get_peers("VNM")  # Returns other F&B companies
        """
        try:
            import sys
            sys.path.insert(0, str(get_data_loader().config.PROJECT_ROOT))
            from config.registries import SectorRegistry

            registry = SectorRegistry()
            ticker = ticker.upper().strip()

            # Get ticker info
            info = registry.get_ticker(ticker)
            if not info:
                return f"Ticker `{ticker}` not found. Use `vnstock_list_tickers()` to see available tickers."

            # Get peers
            peers = registry.get_peers(ticker, exclude_self=exclude_self)
            peers = peers[:limit]

            sector = info.get('sector', 'Unknown')

            result_lines = [
                f"## Peers for {ticker}",
                f"**Sector:** {sector}",
                f"**Total Peers:** {len(registry.get_peers(ticker))}",
                f"**Showing:** {len(peers)}",
                "",
                "| # | Ticker | Exchange |",
                "|---|--------|----------|"
            ]

            for i, peer in enumerate(peers, 1):
                peer_info = registry.get_ticker(peer) or {}
                exchange = peer_info.get('exchange', 'N/A')
                result_lines.append(f"| {i} | {peer} | {exchange} |")

            result_lines.append("")
            result_lines.append(
                f"*Use `vnstock_compare_fundamentals(tickers=['{ticker}', ...])` "
                f"to compare financial metrics with peers.*"
            )

            return "\n".join(result_lines)

        except Exception as e:
            return handle_tool_error(e, "vnstock_get_peers")


# =============================================================================
# Helper Functions
# =============================================================================

def _check_bsc_coverage(ticker: str) -> str:
    """Check if a ticker has BSC forecast coverage."""
    try:
        loader = get_data_loader()
        bsc_df = loader.get_bsc_individual()
        has_coverage = ticker.upper() in bsc_df['symbol'].values
        return "Yes" if has_coverage else "No"
    except:
        return "Unknown"
```

---

## Tổng kết

Plan file này bao gồm:

1. **Mục tiêu rõ ràng** - Xây dựng MCP server cho Vietnamese stock data
2. **Data overview** - Liệt kê tất cả parquet files có sẵn
3. **31 Tools** với mô tả chi tiết và examples
4. **Project structure** - Cấu trúc thư mục đầy đủ
5. **Code templates** - Code mẫu với docstrings chi tiết cho beginner
6. **Configuration** - Cấu hình cho Claude Code và Claude Desktop
7. **Implementation phases** - Chia thành 4 phases với tasks cụ thể
8. **Hướng dẫn beginner** - Giải thích MCP là gì và cách hoạt động
9. **Report extension** - Mở rộng đọc báo cáo từ local/Google Drive

---

## Implementation Status & Test Results (2025-12-19)

### Implementation Complete

**Package renamed:** `vnstock_mcp` → `bsc_mcp` (tránh conflict với vnstock_data)

**Structure:**
```
MCP_SERVER/
├── bsc_mcp/
│   ├── __init__.py
│   ├── config.py
│   ├── server.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── base.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── data_loader.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── discovery_tools.py    (5 tools)
│   │   ├── fundamental_tools.py  (5 tools)
│   │   ├── technical_tools.py    (4 tools)
│   │   ├── valuation_tools.py    (5 tools)
│   │   ├── forecast_tools.py     (3 tools)
│   │   ├── sector_tools.py       (3 tools)
│   │   └── macro_tools.py        (3 tools)
│   └── utils/
│       ├── __init__.py
│       ├── formatters.py
│       └── errors.py
├── requirements.txt
└── README.md
```

### Test Results

#### 1. Config & DataLoader Tests ✅

```
✅ Config loaded successfully
   PROJECT_ROOT: /Users/buuphan/Dev/Vietnam_dashboard
   DATA_ROOT: /Users/buuphan/Dev/Vietnam_dashboard/DATA
   CACHE_TTL: 300

✅ DataLoader initialized
✅ Technical data: 89,837 rows, 40 cols (0.09s)
✅ Company fundamentals: 37,145 rows (0.01s)
✅ Bank fundamentals: 1,051 rows (0.00s)
✅ PE historical: 790,067 rows (0.03s)
✅ BSC forecasts: 93 rows (0.00s)
✅ Available tickers: 458

Entity Type Detection:
   VCB: BANK
   VNM: COMPANY
   BVH: INSURANCE
   SSI: SECURITY
```

#### 2. Tool Registration Test ✅

```
✅ Package renamed to bsc_mcp successfully
✅ Total tools: 28

Tools list:
   - bsc_compare_fundamentals
   - bsc_compare_sectors
   - bsc_compare_valuations
   - bsc_get_bank_financials
   - bsc_get_bsc_forecast
   - bsc_get_commodity_prices
   - bsc_get_company_financials
   - bsc_get_latest_fundamentals
   - bsc_get_latest_technicals
   - bsc_get_macro_data
   - bsc_get_macro_overview
   - bsc_get_market_breadth
   - bsc_get_peers
   - bsc_get_sector_history
   - bsc_get_sector_scores
   - bsc_get_sector_valuation
   - bsc_get_technical_alerts
   - bsc_get_technical_indicators
   - bsc_get_ticker_info
   - bsc_get_ticker_valuation
   - bsc_get_top_upside_stocks
   - bsc_get_valuation_stats
   - bsc_get_vnindex_valuation
   - bsc_list_bsc_forecasts
   - bsc_list_sectors
   - bsc_list_tickers
   - bsc_screen_fundamentals
   - bsc_search_tickers
```

#### 3. Discovery Tools Test ✅

```
=== bsc_list_tickers(entity_type="BANK", limit=5) ===
## Available Tickers (5 found)

| Ticker | Type | Sector |
| --- | --- | --- |
| ABB | BANK | N/A |
| ACB | BANK | N/A |
| BID | BANK | N/A |
| BVB | BANK | N/A |
| CTG | BANK | N/A |
```

#### 4. Fundamental Tools Test ✅

```
=== bsc_get_latest_fundamentals("VCB") ===
## VCB
**Type:** BANK | **Sector:** N/A
### Latest Data: Q3/2025

| Metric | Value |
|--------|-------|
| **Net Interest Income** | 14,657.24 tỷ |
| **PPOP** | 12,014.69 tỷ |
| **Net Profit (NPATMI)** | 9,030.61 tỷ |
| **NPL Ratio** | 1.06% |
| **CASA Ratio** | 35.56% |
| **CIR** | 33.44% |


=== bsc_compare_fundamentals("VCB,ACB,TCB,MBB") ===
## Fundamental Comparison (4 tickers)

| Ticker | Type | ROE | ROA | NIM | NPL_RATIO | CASA_RATIO |
| --- | --- | --- | --- | --- | --- | --- |
| VCB | BANK | N/A | N/A | N/A | 1.06% | 35.56% |
| ACB | BANK | N/A | N/A | N/A | 1.10% | 21.99% |
| TCB | BANK | N/A | N/A | N/A | 1.18% | 38.35% |
| MBB | BANK | N/A | N/A | N/A | 1.90% | 36.96% |
```

#### 5. Valuation Tools Test ✅

```
=== bsc_get_valuation_stats("ACB", "PE", 5) ===
## ACB
**Type:** BANK
### PE Valuation Statistics (5Y History)

| Metric | Value |
|--------|-------|
| **Current PE** | 7.05 |
| **Date** | 2025-12-18 |
| **5Y Mean** | 6.72 |
| **5Y Median** | 6.58 |
| **5Y Std Dev** | 1.18 |
| **5Y Min** | 3.98 |
| **5Y Max** | 10.25 |

### Valuation Position
| Metric | Value |
|--------|-------|
| **Percentile** | 64.3th |
| **Z-Score** | 0.27 |
| **Assessment** | **Overvalued** vs history |
```

#### 6. Forecast Tools Test ✅

```
=== bsc_get_bsc_forecast("ACB") ===
## ACB
**Type:** BANK | **Sector:** Ngân hàng
### BSC Analyst Forecast

| Metric | Value |
|--------|-------|
| **Rating** | **BUY** |
| **Target Price** | 28,400 VND |
| **Current Price** | 23,850 VND |
| **Upside Potential** | 19.08% |

### EPS Forecasts
| Year | EPS | YoY Growth |
|------|-----|------------|
| **2025F** | 3,491.00 | N/A |
| **2026F** | 3,912.00 | N/A |

### Forward Valuations
| Metric | 2025F | 2026F |
|--------|-------|-------|
| **PE Forward** | 6.83 | 6.10 |
| **PB Forward** | 1.12 | 0.95 |


=== bsc_get_top_upside_stocks(n=5) ===
## Top 5 Upside Stocks (BSC Forecast)

| Rank | Ticker | Rating | Target | Current | Upside | Sector |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | NLG | STRONG BUY | 50,100 VND | 31,400 VND | 59.55% | Bất động sản |
| 2 | DXG | STRONG BUY | 27,200 VND | 17,250 VND | 57.68% | Bất động sản |
| 3 | PDR | STRONG BUY | 28,200 VND | 19,050 VND | 48.03% | Bất động sản |
| 4 | DGC | STRONG BUY | 107,800 VND | 74,900 VND | 43.93% | Hóa chất |
| 5 | VRE | STRONG BUY | 43,400 VND | 30,350 VND | 43.00% | Bất động sản |
```

#### 7. Technical Tools Test ✅

```
=== bsc_get_latest_technicals("FPT") ===
## FPT
**Type:** COMPANY
### Technical Snapshot (2025-12-18)

#### Price & Volume
| Metric | Value |
|--------|-------|
| **Close** | 94,400 VND |
| **Volume** | 4,115,500 |
| **Change** | 0.00% |

#### Trend Indicators
| Indicator | Value | Signal |
|-----------|-------|--------|
| **SMA 20** | 96,517.90 | Below |
| **SMA 50** | 96,571.94 | Below |
| **SMA 200** | 101,287.96 | Below |
| **Trend** | - | **Downtrend** |

#### Momentum Indicators
| Indicator | Value | Signal |
|-----------|-------|--------|
| **RSI (14)** | 43.39 | **Neutral** |
| **MACD** | -813.79 | **Bearish** |
| **MACD Signal** | -609.66 | - |
```

#### 8. Screening Tools Test ✅

```
=== bsc_screen_fundamentals(roe_min=15, entity_type="COMPANY", limit=10) ===
## Stock Screening Results (10 found)

**Filters:** ROE >= 15%, Type = COMPANY

| Ticker | Type | Sector | ROE | ROA | PE |
| --- | --- | --- | --- | --- | --- |
| ABA | COMPANY | N/A | 17.23% | -8.67% | N/A |
| APP | COMPANY | N/A | 54.92% | 23.70% | N/A |
| ASIAC | COMPANY | N/A | 18.35% | 11.95% | N/A |
| ATG | COMPANY | N/A | 97.09% | 31.78% | N/A |
| BDP | COMPANY | N/A | 33.91% | -2.47% | N/A |
| CTX | COMPANY | N/A | 17.41% | 9.61% | N/A |
| DAG | COMPANY | N/A | 213.35% | -20.65% | N/A |
| DFF | COMPANY | N/A | 77.75% | -13.07% | N/A |
| DNY | COMPANY | N/A | 133.91% | -3.94% | N/A |
| DSS | COMPANY | N/A | 23.35% | 4.83% | N/A |


=== bsc_screen_fundamentals(roe_min=10, pe_max=15, limit=10) ===
## Stock Screening Results (10 found)

**Filters:** ROE >= 10%, PE <= 15

| Ticker | Type | Sector | ROE | ROA | PE |
| --- | --- | --- | --- | --- | --- |
| BMP | COMPANY | N/A | 11.14% | 8.83% | 12.61 |
| CTX | COMPANY | N/A | 17.41% | 9.61% | 3.94 |
```

### Configuration Files Created

#### `.mcp.json` (Project root)
```json
{
  "mcpServers": {
    "bsc": {
      "type": "stdio",
      "command": "python3",
      "args": ["-m", "bsc_mcp.server"],
      "cwd": "/Users/buuphan/Dev/Vietnam_dashboard/MCP_SERVER",
      "env": {
        "PYTHONPATH": "/Users/buuphan/Dev/Vietnam_dashboard:/Users/buuphan/Dev/Vietnam_dashboard/MCP_SERVER",
        "DATA_ROOT": "/Users/buuphan/Dev/Vietnam_dashboard/DATA"
      }
    }
  }
}
```

### Known Issues & Notes

1. **ROE/ROA columns**: Một số metrics (ROE, ROA, NIM) hiển thị N/A cho banks - cần kiểm tra lại data pipeline
2. **Sector mapping**: Sector hiển thị N/A cho nhiều tickers - cần update sector registry
3. **Cache**: Data được cache 5 phút, restart Claude/Cursor để refresh config

### Next Steps (Phase 2)

- [ ] Fix missing ROE/ROA metrics trong bank data
- [ ] Thêm sector mapping cho tất cả tickers
- [ ] Implement Report Tools (đọc PDF/DOCX)
- [ ] Thêm Google Drive integration (optional)
- [ ] Performance optimization (lazy loading columns)
