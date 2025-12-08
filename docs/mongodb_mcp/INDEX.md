# MongoDB & MCP Documentation Index

## 📑 Danh sách tài liệu

### 1. [MONGODB_SETUP.md](./MONGODB_SETUP.md)
**Mục đích:** Hướng dẫn setup MongoDB từ đầu đến cuối
**Nội dung:**
- Cài đặt dependencies
- Cấu hình MongoDB
- Upload dữ liệu
- Sử dụng MongoDB module
- Query examples

### 2. [MONGODB_CONNECTION.md](./MONGODB_CONNECTION.md)
**Mục đích:** Connection string và cấu hình kết nối
**Nội dung:**
- Connection string
- Cấu hình cho MongoDB Plugin
- Test connection
- Security notes

### 3. [CURSOR_MCP_SETUP.md](./CURSOR_MCP_SETUP.md)
**Mục đích:** Hướng dẫn cấu hình MCP Server trong Cursor
**Nội dung:**
- Cách thêm vào Cursor Settings
- Kiểm tra cấu hình
- Test MCP Server
- Troubleshooting

### 4. [MCP_TROUBLESHOOTING.md](./MCP_TROUBLESHOOTING.md)
**Mục đích:** Khắc phục sự cố MCP Server
**Nội dung:**
- Các lỗi thường gặp
- Giải pháp
- Checklist
- Test connection

### 5. [mongodb_README.md](./mongodb_README.md)
**Mục đích:** MongoDB module documentation
**Nội dung:**
- Cấu trúc module
- Sử dụng uploader
- Query examples
- API reference

### 6. [mcp_server_README.md](./mcp_server_README.md)
**Mục đích:** MCP Server documentation
**Nội dung:**
- Cấu trúc MCP Server
- Tools available
- Integration với Cursor
- Examples

## 🗂️ Cấu trúc Code

### MongoDB Module
- `mongodb/config.py` - MongoDB connection
- `mongodb/uploader.py` - Upload data
- `mongodb/queries.py` - Query functions
- `mongodb/utils.py` - Helper functions

### MCP Server
- `mcp_server/server.py` - Main server
- `mcp_server/config.py` - Config
- `mcp_server/tools/` - Tools
- `mcp_server/handlers/` - Handlers
- `mcp_server/resources/` - Resources

### Streamlit Services
- `streamlit_app/services/llm_service.py` - LLM wrapper
- `streamlit_app/services/query_builder.py` - NL to query
- `streamlit_app/services/chat_manager.py` - Chat manager
- `streamlit_app/ai/` - AI prompts & schemas

## 🚀 Quick Start

1. **Setup MongoDB:**
   ```bash
   # Đọc MONGODB_SETUP.md
   pip install pymongo python-dotenv
   # Tạo .env file
   python -m mongodb.uploader
   ```

2. **Setup MCP Server:**
   ```bash
   # Đọc CURSOR_MCP_SETUP.md
   pip install mcp
   # Cấu hình trong Cursor Settings
   # Restart Cursor
   ```

3. **Test:**
   ```bash
   # Test MongoDB
   python -c "from mongodb.config import get_mongodb_client; get_mongodb_client()"
   
   # Test MCP Server
   python -m mcp_server.server
   ```

## 📞 Liên hệ

Nếu cần hỗ trợ, xem:
- [MCP_TROUBLESHOOTING.md](./MCP_TROUBLESHOOTING.md)
- [MONGODB_CONNECTION.md](./MONGODB_CONNECTION.md)
