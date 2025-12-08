# MongoDB & MCP Quick Reference

Tài liệu tham khảo nhanh cho MongoDB và MCP Server.

## 🔗 Connection String

```
mongodb+srv://buuphanquoc_db:Quocbuu123@cluster0.m6tqpie.mongodb.net/?appName=Cluster0
```

**Database:** `mydb`

## 📦 Collections

- `company_metrics` - Financial metrics cho companies
- `bank_metrics` - Financial metrics cho banks
- `insurance_metrics` - Financial metrics cho insurance
- `security_metrics` - Financial metrics cho securities

## 🚀 Quick Commands

### Upload Data
```bash
# Upload tất cả collections
python -m mongodb.uploader

# Upload một collection
python -m mongodb.uploader --collection company_metrics \
  --parquet calculated_results/fundamental/company/company_financial_metrics.parquet
```

### Test Connection
```bash
# Test MongoDB
python -c "from mongodb.config import get_mongodb_client; get_mongodb_client()"

# Test MCP Server
python -m mcp_server.server
```

### Query Examples
```python
from mongodb.config import get_database
from mongodb.queries import get_latest_metrics, get_top_symbols_by_metric

db = get_database()
company_collection = db['company_metrics']

# Latest metrics
latest = get_latest_metrics(company_collection, symbol='HPG', limit=5)

# Top symbols
top = get_top_symbols_by_metric(company_collection, 'gross_margin', limit=10)
```

## 🔧 Cursor MCP Config

Thêm vào Cursor Settings (`Cmd + ,`):

```json
{
  "mcp.servers": {
    "mongodb-finance-metrics": {
      "command": "/usr/local/bin/python3",
      "args": ["-m", "mcp_server.server"],
      "cwd": "${workspaceFolder}",
      "env": {
        "MONGODB_URI": "mongodb+srv://buuphanquoc_db:Quocbuu123@cluster0.m6tqpie.mongodb.net/?appName=Cluster0",
        "MONGODB_DB_NAME": "mydb"
      }
    }
  }
}
```

## 📝 Environment Variables

File `.env` ở root:

```env
MONGODB_URI=mongodb+srv://buuphanquoc_db:Quocbuu123@cluster0.m6tqpie.mongodb.net/?appName=Cluster0
MONGODB_DB_NAME=mydb
OPENAI_API_KEY=your_key_here
```

## 🛠️ Dependencies

```bash
pip install pymongo python-dotenv mcp openai
```

Hoặc:
```bash
pip install -r streamlit_app/requirements.txt
```

## 📚 Documentation Files

- [README.md](./README.md) - Index tổng hợp
- [INDEX.md](./INDEX.md) - Chi tiết từng file
- [MONGODB_SETUP.md](./MONGODB_SETUP.md) - Setup guide
- [MONGODB_CONNECTION.md](./MONGODB_CONNECTION.md) - Connection guide
- [CURSOR_MCP_SETUP.md](./CURSOR_MCP_SETUP.md) - Cursor setup
- [MCP_TROUBLESHOOTING.md](./MCP_TROUBLESHOOTING.md) - Troubleshooting

## 🎯 Common Tasks

### 1. Setup MongoDB
1. Tạo `.env` file
2. `pip install pymongo python-dotenv`
3. `python -m mongodb.uploader`

### 2. Setup MCP Server
1. `pip install mcp`
2. Thêm config vào Cursor Settings
3. Restart Cursor

### 3. Test Everything
```bash
# Test MongoDB
python -c "from mongodb.config import get_mongodb_client; get_mongodb_client()"

# Test MCP
python -m mcp_server.server
```

## 🐛 Quick Fixes

### ModuleNotFoundError
```bash
pip install mcp pymongo python-dotenv
```

### SSL Certificate Error
Đã được fix trong `mcp_server/config.py` và `mongodb/config.py` với `tlsAllowInvalidCertificates=True`

### Connection Timeout
- Kiểm tra MongoDB URI
- Kiểm tra network
- Kiểm tra MongoDB Atlas IP whitelist

## 📞 Help

Xem [MCP_TROUBLESHOOTING.md](./MCP_TROUBLESHOOTING.md) để biết thêm chi tiết.

