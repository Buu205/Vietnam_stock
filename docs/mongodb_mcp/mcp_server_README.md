# MCP Server for MongoDB Financial Metrics

MCP (Model Context Protocol) server cho phép Claude/ChatGPT query MongoDB financial metrics qua protocol.

## Cấu trúc

```
mcp_server/
├── __init__.py
├── server.py                # Main MCP server
├── config.py                # MongoDB configuration
├── tools/
│   ├── query_tool.py        # Query MongoDB tool
│   ├── aggregate_tool.py    # Aggregation tool
│   └── schema_tool.py       # Get schema tool
├── handlers/
│   ├── query_handler.py    # Query request handler
│   └── result_formatter.py  # Result formatting
├── resources/
│   ├── collections.py       # Collections resource
│   └── metrics.py           # Metrics resource
└── README.md
```

## Cài đặt

1. **Cài đặt dependencies:**
```bash
pip install pymongo mcp python-dotenv
```

2. **Cấu hình .env:**
```env
MONGODB_URI=mongodb+srv://buuphanquoc_db:Quocbuu123@cluster0.m6tqpie.mongodb.net/?appName=Cluster0
MONGODB_DB_NAME=mydb
```

## Sử dụng

### Chạy MCP Server

```bash
python -m mcp_server.server
```

### Tools Available

1. **query_collection**: Query MongoDB collection với filters
   - query_type: symbol, latest, top, timeseries, compare
   - collection_name: company_metrics, bank_metrics, etc.
   - symbol, year, quarter, metric_field, limit, etc.

2. **get_collection_schema**: Lấy schema information
   - collection_name: Tên collection

3. **list_collections**: Liệt kê tất cả collections

4. **get_collection_stats**: Lấy statistics cho collection

### Ví dụ sử dụng với Claude/ChatGPT

Khi kết nối MCP server, bạn có thể hỏi:
- "Query company_metrics for symbol HPG"
- "Get top 10 symbols by gross_margin"
- "Show me the schema for bank_metrics"
- "Compare ROE for HPG, VCB, and POW"

## Integration với Cursor/Claude

1. Cấu hình MCP server trong Cursor settings
2. Kết nối đến MongoDB Atlas
3. Sử dụng tools để query dữ liệu financial metrics

## Notes

- Server sử dụng MongoDB Atlas connection với ServerApi
- Tự động convert ObjectId thành string cho JSON serialization
- Hỗ trợ multiple query types: symbol, latest, top, timeseries, compare

