# Hướng dẫn sử dụng AI trong Cursor với MCP Server

Hướng dẫn chi tiết cách sử dụng MongoDB MCP Server với AI trong Cursor.

## ✅ Kiểm tra kết nối MCP

### Bước 1: Kiểm tra MCP Server đã được cấu hình

1. **Mở Cursor Settings:**
   - Nhấn `Cmd + ,` (Mac) hoặc `Ctrl + ,` (Windows/Linux)
   - Hoặc: `Cursor` → `Settings`

2. **Tìm MCP Settings:**
   - Tìm kiếm: `mcp` hoặc `Model Context Protocol`
   - Hoặc vào: `Features` → `MCP` → `Servers`

3. **Kiểm tra server có trong danh sách:**
   - Bạn sẽ thấy `mongodb-finance-metrics` trong danh sách
   - Status phải là "Connected" hoặc "Running"

### Bước 2: Kiểm tra MCP Server Status

1. **Mở Command Palette:**
   - `Cmd + Shift + P` (Mac) hoặc `Ctrl + Shift + P` (Windows/Linux)

2. **Tìm lệnh:**
   - `MCP: List Servers` - Xem danh sách servers
   - `MCP: Show Server Status` - Xem status chi tiết
   - `MCP: Restart Server` - Restart server nếu cần

3. **Kiểm tra logs:**
   - Mở MCP panel (thường ở bottom hoặc sidebar)
   - Xem logs để biết server có chạy không

## 🚀 Cách sử dụng AI với MCP Server

### Cách 1: Hỏi trực tiếp trong Chat

Mở chat với AI trong Cursor và hỏi:

#### Ví dụ 1: Query dữ liệu
```
Query company_metrics for symbol HPG
```

#### Ví dụ 2: Lấy top symbols
```
Get top 10 companies by gross margin from company_metrics
```

#### Ví dụ 3: So sánh metrics
```
Compare ROE for HPG, VCB, and POW from company_metrics
```

#### Ví dụ 4: Lấy schema
```
Show me the schema for company_metrics collection
```

#### Ví dụ 5: List collections
```
List all collections in MongoDB database
```

### Cách 2: Sử dụng @mention để reference context

1. **Trong chat, gõ `@` để xem các options:**
   - `@mongodb-finance-metrics` - Reference MCP server
   - `@Files` - Reference files
   - `@Code` - Reference code

2. **Sau đó hỏi:**
   ```
   @mongodb-finance-metrics Query latest metrics for HPG
   ```

### Cách 3: Sử dụng Commands

1. **Mở Command Palette:** `Cmd + Shift + P`
2. **Tìm:**
   - `MCP: Query Collection` - Query MongoDB collection
   - `MCP: Get Schema` - Lấy schema của collection
   - `MCP: List Collections` - List tất cả collections

## 📝 Ví dụ câu hỏi chi tiết

### Query dữ liệu cơ bản

```
# Lấy metrics mới nhất
"Get latest metrics for HPG from company_metrics"

# Lấy metrics theo năm/quý
"Get metrics for HPG in year 2024, quarter 3 from company_metrics"

# Lấy time series
"Show me gross margin time series for HPG from company_metrics"
```

### Top/Bottom queries

```
# Top symbols
"Get top 10 companies by gross margin from company_metrics"
"Get top 5 banks by ROE from bank_metrics"

# Bottom symbols
"Get bottom 10 companies by net margin from company_metrics"
```

### So sánh

```
# So sánh nhiều symbols
"Compare gross margin for HPG, VCB, POW from company_metrics"
"Compare ROE for top 5 banks from bank_metrics"
```

### Schema và metadata

```
# Lấy schema
"Show schema for company_metrics"
"What fields are available in bank_metrics?"

# Collection info
"List all collections in MongoDB"
"Show statistics for company_metrics collection"
```

### Filter queries

```
# Filter theo giá trị
"Get companies with gross margin > 30% from company_metrics"
"Find banks with ROE between 10% and 20% from bank_metrics"

# Filter theo date range
"Get metrics for HPG from 2024-01-01 to 2024-12-31"
```

## 🔧 Troubleshooting

### MCP Server không hiển thị

1. **Kiểm tra cấu hình:**
   - Xem file `.cursor/settings.json` hoặc `.cursor/mcp.json`
   - Đảm bảo có cấu hình `mongodb-finance-metrics`

2. **Restart Cursor:**
   - Đóng hoàn toàn Cursor (`Cmd + Q`)
   - Mở lại

3. **Kiểm tra Python path:**
   - Đảm bảo Python path đúng trong settings
   - Test: `which python3` hoặc `which python`

### Lỗi "Module not found"

```bash
# Cài đặt dependencies
pip install mcp pymongo python-dotenv
```

### Lỗi "Connection failed"

1. **Kiểm tra MongoDB URI:**
   - Xem file `.env` hoặc settings
   - Test connection: `python -c "from mongodb.config import get_mongodb_client; get_mongodb_client()"`

2. **Kiểm tra network:**
   - Đảm bảo có internet
   - Kiểm tra MongoDB Atlas IP whitelist

### AI không hiểu query

1. **Be specific:**
   - Rõ ràng về collection name: `company_metrics`, `bank_metrics`
   - Rõ ràng về metric field: `gross_margin`, `roe`, `net_margin`

2. **Use examples:**
   - "Query company_metrics collection for symbol HPG"
   - Thay vì: "Get HPG data"

## 💡 Tips

### 1. Sử dụng natural language
AI hiểu natural language, bạn không cần syntax chính xác:
- ✅ "Get top companies by margin"
- ✅ "Show me HPG metrics"
- ✅ "Compare these stocks: HPG, VCB, POW"

### 2. Be specific về collection
Luôn chỉ rõ collection bạn muốn query:
- ✅ "from company_metrics"
- ✅ "in bank_metrics"
- ❌ Không nói collection → AI sẽ hỏi lại

### 3. Sử dụng @mention
Khi cần reference MCP server cụ thể:
```
@mongodb-finance-metrics Query HPG metrics
```

### 4. Combine queries
Bạn có thể kết hợp nhiều queries:
```
"Get top 10 companies by gross margin, then compare their ROE"
```

## 📊 Example Workflow

### Workflow 1: Phân tích một symbol

```
1. "Get latest metrics for HPG from company_metrics"
2. "Show me gross margin time series for HPG"
3. "Compare HPG's ROE with industry average"
```

### Workflow 2: Tìm top performers

```
1. "Get top 10 companies by gross margin from company_metrics"
2. "Now show me their ROE"
3. "Compare their net margins"
```

### Workflow 3: So sánh ngành

```
1. "Get all bank metrics from bank_metrics"
2. "Compare ROE for top 5 banks"
3. "Show me their NPL ratios"
```

## 🎯 Best Practices

1. **Always specify collection:** `company_metrics`, `bank_metrics`, etc.
2. **Be clear about metrics:** `gross_margin`, `roe`, `net_margin`
3. **Use specific symbols:** `HPG`, `VCB`, `POW` (uppercase)
4. **Ask follow-up questions:** "Now show me their ROE"
5. **Use filters:** "with gross margin > 30%"

## 📞 Help

Nếu gặp vấn đề:
1. Xem [MCP_TROUBLESHOOTING.md](./MCP_TROUBLESHOOTING.md)
2. Kiểm tra MCP logs trong Cursor
3. Test connection: `python -m mcp_server.server`

