# MongoDB & MCP Server Documentation

Tài liệu tổng hợp về MongoDB support và MCP Server cho VN Finance Dashboard.

## 📚 Tài liệu có sẵn

### 🚀 Quick Start
- **[MONGODB_SETUP.md](./MONGODB_SETUP.md)** - Hướng dẫn setup MongoDB từ đầu đến cuối
- **[MONGODB_CONNECTION.md](./MONGODB_CONNECTION.md)** - Connection string và cấu hình kết nối

### 🔧 Cấu hình
- **[CURSOR_MCP_SETUP.md](./CURSOR_MCP_SETUP.md)** - Hướng dẫn cấu hình MCP Server trong Cursor
- **[MCP_TROUBLESHOOTING.md](./MCP_TROUBLESHOOTING.md)** - Khắc phục sự cố MCP Server

### 📖 Module Documentation
- **[mongodb/README.md](./mongodb_README.md)** - MongoDB module documentation
- **[mcp_server/README.md](./mcp_server_README.md)** - MCP Server documentation

## 📁 Cấu trúc Code

```
stock_dashboard/
├── mongodb/                    # MongoDB module
│   ├── config.py              # MongoDB connection config
│   ├── uploader.py            # Upload parquet to MongoDB
│   ├── queries.py             # Query examples
│   └── utils.py               # Helper functions
│
├── mcp_server/                 # MCP Server
│   ├── server.py              # Main MCP server
│   ├── config.py              # MongoDB config for MCP
│   ├── tools/                 # MCP tools
│   ├── handlers/              # Request handlers
│   └── resources/             # MCP resources
│
├── streamlit_app/
│   ├── services/               # LLM services
│   │   ├── llm_service.py     # LLM API wrapper
│   │   ├── query_builder.py   # NL to MongoDB query
│   │   ├── response_formatter.py
│   │   └── chat_manager.py   # Chat manager
│   └── ai/                    # AI prompts & schemas
│       ├── prompts.py
│       ├── schemas.py
│       └── validators.py
│
└── docs/mongodb_mcp/          # Documentation (folder này)
    ├── README.md              # File này
    ├── MONGODB_SETUP.md
    ├── MONGODB_CONNECTION.md
    ├── CURSOR_MCP_SETUP.md
    └── MCP_TROUBLESHOOTING.md
```

## 🎯 Quick Links

### Setup MongoDB
1. Đọc [MONGODB_SETUP.md](./MONGODB_SETUP.md)
2. Tạo file `.env` với MongoDB credentials
3. Upload data: `python -m mongodb.uploader`

### Setup MCP Server trong Cursor
1. Đọc [CURSOR_MCP_SETUP.md](./CURSOR_MCP_SETUP.md)
2. Thêm cấu hình vào Cursor Settings
3. Restart Cursor

### Troubleshooting
- Xem [MCP_TROUBLESHOOTING.md](./MCP_TROUBLESHOOTING.md)
- Kiểm tra connection: [MONGODB_CONNECTION.md](./MONGODB_CONNECTION.md)

## 🔗 Connection String

```
mongodb+srv://buuphanquoc_db:Quocbuu123@cluster0.m6tqpie.mongodb.net/?appName=Cluster0
```

Database: `mydb`

## 📝 Collections

- `company_metrics` - Financial metrics cho companies
- `bank_metrics` - Financial metrics cho banks
- `insurance_metrics` - Financial metrics cho insurance
- `security_metrics` - Financial metrics cho securities

## ✅ Checklist

- [ ] Đã cài đặt dependencies (`pymongo`, `mcp`, `python-dotenv`)
- [ ] Đã tạo file `.env` với MongoDB credentials
- [ ] Đã upload data lên MongoDB
- [ ] Đã cấu hình MCP Server trong Cursor
- [ ] Đã test MCP Server hoạt động

## 🆘 Hỗ trợ

Nếu gặp vấn đề:
1. Xem [MCP_TROUBLESHOOTING.md](./MCP_TROUBLESHOOTING.md)
2. Kiểm tra logs trong Cursor MCP panel
3. Test connection: `python -m mongodb.config`
