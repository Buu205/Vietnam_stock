# BSC MCP Server - Vietnamese Stock Market Data

MCP Server cho phép AI agents (Claude, Cursor, etc.) tra cứu dữ liệu chứng khoán Việt Nam.

## 📊 Tính năng

- **30 Tools** cho tra cứu dữ liệu toàn diện
- **Fundamental Analysis**: ROE, ROA, margins, EPS, NIM, NPL...
- **Technical Analysis**: RSI, MACD, Bollinger Bands, alerts...
- **Valuation**: PE/PB historical, percentiles, z-scores
- **BSC Forecasts**: Target prices, ratings, EPS forecasts
- **Sector Analysis**: FA/TA scores, signals
- **Macro Data**: Interest rates, FX, commodities

## 🚀 Cài đặt

### 1. Cài dependencies

```bash
cd MCP_SERVER
pip install -r requirements.txt
```

### 2. Cấu hình cho AI Agent

#### Claude Code / Claude Desktop

File: `~/.mcp.json` hoặc `.mcp.json` trong project root

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

#### Cursor AI

1. Mở **Cursor Settings** → **MCP Servers**
2. Thêm cấu hình:
   - **Name**: `bsc`
   - **Command**: `python3`
   - **Args**: `-m bsc_mcp.server`
   - **Working Directory**: `/Users/buuphan/Dev/Vietnam_dashboard/MCP_SERVER`
3. Thêm Environment Variables:
   - `PYTHONPATH`: `/Users/buuphan/Dev/Vietnam_dashboard:/Users/buuphan/Dev/Vietnam_dashboard/MCP_SERVER`
   - `DATA_ROOT`: `/Users/buuphan/Dev/Vietnam_dashboard/DATA`

#### Claude Desktop App

File: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "bsc": {
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

## 💬 Hướng dẫn sử dụng với AI Agent

### Cách hỏi đơn giản (Natural Language)

AI Agent sẽ tự động chọn tool phù hợp khi bạn hỏi:

```
# Tra cứu thông tin cơ bản
"VCB là ngân hàng gì? Có những chỉ số tài chính nào?"
"Danh sách các ngân hàng trên sàn"
"Tìm các công ty cùng ngành với VNM"

# Phân tích cơ bản
"ROE của ACB 4 quý gần nhất?"
"So sánh ROE, NIM của VCB, ACB, TCB, MBB"
"Lọc các công ty có ROE > 15%"

# Định giá
"PE hiện tại của ACB so với 5 năm lịch sử?"
"So sánh PE của các ngân hàng lớn"
"PE của VN-Index hiện tại đang ở vùng nào?"

# Kỹ thuật
"RSI và MACD của FPT hiện tại?"
"Có cổ phiếu nào đang breakout không?"
"Market breadth hôm nay thế nào?"

# Mẫu hình nến (Candlestick Patterns)
"Có cổ phiếu nào đang có mẫu hình hammer?"
"Liệt kê các mẫu hình nến bearish hôm nay"
"FPT có mẫu hình nến nào không?"
"Cho tôi OHLCV raw của VNM 100 ngày"

# BSC Forecast
"BSC đánh giá ACB như thế nào?"
"Top 10 cổ phiếu có upside cao nhất theo BSC"
"Có những cổ phiếu nào được BSC khuyến nghị MUA?"

# Ngành
"Ngành nào đang có tín hiệu MUA?"
"So sánh các ngành theo FA/TA scores"

# Macro
"Tổng quan macro hiện tại?"
"Giá vàng và dầu gần đây?"
```

### Ví dụ conversations

#### Ví dụ 1: Phân tích ngân hàng

```
User: "So sánh 4 ngân hàng lớn nhất"

AI sẽ tự động gọi:
→ bsc_compare_fundamentals(tickers="VCB,ACB,TCB,MBB")
→ bsc_compare_valuations(tickers="VCB,ACB,TCB,MBB")

Kết quả: Bảng so sánh ROE, NIM, NPL, PE, PB
```

#### Ví dụ 2: Tìm cơ hội đầu tư

```
User: "Tìm cổ phiếu có upside > 20% theo BSC và PE < 15"

AI sẽ gọi:
→ bsc_get_top_upside_stocks(min_upside=20)
→ Lọc thêm theo PE

Kết quả: Danh sách cổ phiếu phù hợp với target price và rating
```

#### Ví dụ 3: Check kỹ thuật nhanh

```
User: "FPT đang thế nào về mặt kỹ thuật?"

AI sẽ gọi:
→ bsc_get_latest_technicals(ticker="FPT")

Kết quả:
- RSI: 43.39 (Neutral)
- MACD: Bearish
- Trend: Downtrend
- Support/Resistance levels
```

#### Ví dụ 4: Phân tích mẫu hình nến

```
User: "Có cổ phiếu nào đang có mẫu hình hammer không?"

AI sẽ gọi:
→ bsc_get_candlestick_patterns(pattern="hammer")

Kết quả:
### Pattern Summary
- Bullish patterns: 30
- Bearish patterns: 0

| symbol | pattern_name | signal | strength | price |
| VIC | hammer | BULLISH | 100 | 142,700 VND |
| MWG | hammer | BULLISH | 100 | 81,600 VND |
...
```

#### Ví dụ 5: Phân tích dòng tiền

```
User: "Cho tôi OHLCV và thanh khoản của VCB 10 ngày gần nhất"

AI sẽ gọi:
→ bsc_get_ohlcv_raw(ticker="VCB", limit=10)

Kết quả:
### Trading Value Analysis (tỷ VND)
| Latest Trading Value | 174.71 tỷ |
| Avg Trading Value (10d) | 200.16 tỷ |
| Value vs Avg | -12.72% |

| date | open | high | low | close | volume | value_bn |
| 2025-12-18 | 57,200 | 57,500 | 56,700 | 56,800 | 3,075,800 | 174.71 |
...
```

## 📋 Danh sách Tools (30 tools)

### Discovery Tools (5)
| Tool | Mô tả |
|------|-------|
| `bsc_list_tickers` | Danh sách tickers theo loại/ngành |
| `bsc_get_ticker_info` | Thông tin chi tiết ticker |
| `bsc_list_sectors` | Danh sách 19 ngành |
| `bsc_search_tickers` | Tìm kiếm ticker |
| `bsc_get_peers` | Công ty cùng ngành |

### Fundamental Tools (5)
| Tool | Mô tả |
|------|-------|
| `bsc_get_company_financials` | Chỉ số tài chính theo quý/năm |
| `bsc_get_bank_financials` | Metrics đặc thù ngân hàng |
| `bsc_get_latest_fundamentals` | Snapshot quý gần nhất |
| `bsc_compare_fundamentals` | So sánh nhiều tickers |
| `bsc_screen_fundamentals` | Lọc theo criteria |

### Technical Tools (6)
| Tool | Mô tả |
|------|-------|
| `bsc_get_technical_indicators` | OHLCV + 30+ indicators |
| `bsc_get_latest_technicals` | Snapshot kỹ thuật |
| `bsc_get_technical_alerts` | Breakout, MA crossover, etc. |
| `bsc_get_market_breadth` | Advance/Decline, McClellan |
| `bsc_get_candlestick_patterns` | Candlestick patterns (ta-lib) |
| `bsc_get_ohlcv_raw` | OHLCV + Trading Value (tỷ VND) |

### Valuation Tools (5)
| Tool | Mô tả |
|------|-------|
| `bsc_get_ticker_valuation` | PE/PB historical |
| `bsc_get_valuation_stats` | Mean, percentile, z-score |
| `bsc_get_sector_valuation` | So sánh ngành |
| `bsc_compare_valuations` | So sánh nhiều tickers |
| `bsc_get_vnindex_valuation` | VN-Index PE/PB bands |

### Forecast Tools (3)
| Tool | Mô tả |
|------|-------|
| `bsc_get_bsc_forecast` | Forecast chi tiết |
| `bsc_list_bsc_forecasts` | Danh sách 93 stocks |
| `bsc_get_top_upside_stocks` | Top upside potential |

### Sector Tools (3)
| Tool | Mô tả |
|------|-------|
| `bsc_get_sector_scores` | FA/TA scores + signals |
| `bsc_get_sector_history` | Lịch sử scores |
| `bsc_compare_sectors` | So sánh nhiều ngành |

### Macro Tools (3)
| Tool | Mô tả |
|------|-------|
| `bsc_get_macro_data` | Interest rates, FX |
| `bsc_get_commodity_prices` | Gold, oil, steel |
| `bsc_get_macro_overview` | Tổng quan macro |

## 🔍 Chi tiết sử dụng từng Tool

### Technical Tools - Chi tiết

#### `bsc_get_candlestick_patterns`
Phát hiện mẫu hình nến (candlestick patterns) sử dụng ta-lib.

**Các mẫu hình hỗ trợ:**
- `doji` - Nến Doji (do dự)
- `hammer` - Búa (đảo chiều tăng)
- `hanging_man` - Người treo cổ (đảo chiều giảm)
- `engulfing` - Nhấn chìm
- `three_white_soldiers` - Ba lính trắng (tăng mạnh)
- `evening_star` - Sao hôm (đảo chiều giảm)
- `inverted_hammer` - Búa ngược
- `shooting_star` - Sao băng (giảm)

**Cách dùng:**
```
# Tất cả mẫu hình hôm nay
bsc_get_candlestick_patterns()

# Lọc theo mẫu hình
bsc_get_candlestick_patterns(pattern="hammer")

# Lọc theo tín hiệu
bsc_get_candlestick_patterns(signal="BULLISH")
bsc_get_candlestick_patterns(signal="BEARISH")

# Lọc theo ticker
bsc_get_candlestick_patterns(ticker="FPT")
```

#### `bsc_get_ohlcv_raw`
Lấy dữ liệu OHLCV và Trading Value để phân tích dòng tiền.

**Output bao gồm:**
- OHLCV: Open, High, Low, Close, Volume
- Trading Value (tỷ VND)
- So sánh thanh khoản vs trung bình

**Cách dùng:**
```
# OHLCV + Trading Value 60 ngày (mặc định)
bsc_get_ohlcv_raw("FPT")

# Chỉ định số ngày
bsc_get_ohlcv_raw("VCB", limit=100)

# Chỉ OHLCV (không có trading value)
bsc_get_ohlcv_raw("ACB", include_value=False)
```

**Ứng dụng:**
- So sánh thanh khoản giữa các mã
- Phát hiện phiên giao dịch đột biến
- Phân tích dòng tiền theo ngày

### Valuation Tools - Chi tiết

#### `bsc_get_ticker_valuation`
Lấy lịch sử PE/PB của một ticker.

```
# PE/PB lịch sử
bsc_get_ticker_valuation("ACB", years=5)
```

#### `bsc_get_valuation_stats`
Thống kê định giá: mean, percentile, z-score.

```
# Phân tích định giá so với lịch sử
bsc_get_valuation_stats("VCB")
```

### Screening & Filtering

#### `bsc_screen_fundamentals`
Lọc cổ phiếu theo tiêu chí tài chính.

```
# Lọc công ty có ROE > 15%
bsc_screen_fundamentals(roe_min=15)

# Lọc ngân hàng có NIM > 3%
bsc_screen_fundamentals(entity_type="BANK", nim_min=3)

# Lọc theo nhiều tiêu chí
bsc_screen_fundamentals(roe_min=15, pe_max=15, sector="Ngân hàng")
```

#### `bsc_get_top_upside_stocks`
Top cổ phiếu có upside cao nhất theo BSC.

```
# Top 10 upside
bsc_get_top_upside_stocks(limit=10)

# Upside > 20%
bsc_get_top_upside_stocks(min_upside=20)
```

## 📊 Data Coverage

- **458 tickers** (315 liquid stocks)
- **19 sectors** (ICB L2 Vietnamese)
- **Entity types**: COMPANY, BANK, INSURANCE, SECURITY
- **Historical data**: From 1997 (PE/PB)
- **BSC forecasts**: 93 stocks with target prices

## 🔧 Troubleshooting

### MCP Server không khởi động

```bash
# Test trực tiếp
cd /Users/buuphan/Dev/Vietnam_dashboard/MCP_SERVER
PYTHONPATH="/Users/buuphan/Dev/Vietnam_dashboard:/Users/buuphan/Dev/Vietnam_dashboard/MCP_SERVER" \
DATA_ROOT="/Users/buuphan/Dev/Vietnam_dashboard/DATA" \
python3 -c "from bsc_mcp.server import mcp; print('OK')"
```

### Data not found

```bash
# Kiểm tra data files
ls -la /Users/buuphan/Dev/Vietnam_dashboard/DATA/processed/

# Chạy pipeline cập nhật data
python3 PROCESSORS/daily_sector_complete_update.py
```

### Import errors

```bash
# Kiểm tra PYTHONPATH
echo $PYTHONPATH

# Test import
python3 -c "import bsc_mcp; print('OK')"
```

## 📝 Notes

- Data được cache 5 phút để tối ưu performance
- Restart AI agent sau khi thay đổi `.mcp.json`
- Log files tại stderr của MCP process

## 📄 License

Internal use only - Buu Phan
