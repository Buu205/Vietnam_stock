# MCP Server Troubleshooting Guide

## ✅ Đã khắc phục: ModuleNotFoundError

Package `mcp` đã được cài đặt thành công. Nếu vẫn gặp lỗi, làm theo các bước sau:

## 🔧 Các bước khắc phục

### 1. Cài đặt đầy đủ dependencies

```bash
# Cài đặt tất cả dependencies cần thiết
pip install mcp pymongo python-dotenv

# Hoặc từ requirements file
pip install -r streamlit_app/requirements.txt
```

### 2. Kiểm tra Python path trong Cursor Settings

Đảm bảo Python path đúng trong `.cursor/settings.json`:

```json
{
  "mcp.servers": {
    "mongodb-finance-metrics": {
      "command": "/usr/local/bin/python3",  // ← Kiểm tra path này
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

**Tìm Python path của bạn:**
```bash
which python3
# Hoặc
which python
```

### 3. Restart Cursor

Sau khi cài đặt dependencies và cập nhật settings:
1. **Đóng hoàn toàn Cursor** (Cmd + Q trên Mac)
2. **Mở lại Cursor**
3. **Kiểm tra MCP server status**

### 4. Kiểm tra MCP Server Status

1. Mở Command Palette: `Cmd + Shift + P` (Mac) hoặc `Ctrl + Shift + P` (Windows)
2. Tìm: `MCP: List Servers` hoặc `MCP: Show Server Status`
3. Bạn sẽ thấy `mongodb-finance-metrics` trong danh sách

### 5. Test MCP Server thủ công

```bash
cd /Users/buuphan/Dev/stock_dashboard
python3 -m mcp_server.server
```

Nếu có lỗi, bạn sẽ thấy thông báo cụ thể.

## 🐛 Các lỗi thường gặp

### Lỗi: "ModuleNotFoundError: No module named 'mcp'"

**Giải pháp:**
```bash
pip install mcp
```

### Lỗi: "ModuleNotFoundError: No module named 'pymongo'"

**Giải pháp:**
```bash
pip install pymongo
```

### Lỗi: "Failed to connect to MongoDB"

**Giải pháp:**
1. Kiểm tra MongoDB URI trong `.env` hoặc settings
2. Kiểm tra network connection
3. Kiểm tra MongoDB Atlas IP whitelist

### Lỗi: "Command not found: /usr/local/bin/python3"

**Giải pháp:**
1. Tìm Python path: `which python3`
2. Cập nhật `command` trong settings với path đúng

### Lỗi: "Request timed out"

**Giải pháp:**
1. Kiểm tra MCP server có đang chạy không
2. Restart Cursor
3. Kiểm tra logs trong Cursor MCP panel

## ✅ Checklist

- [ ] Đã cài đặt `mcp` package
- [ ] Đã cài đặt `pymongo` package  
- [ ] Đã cài đặt `python-dotenv` package
- [ ] Python path đúng trong settings
- [ ] File `.env` tồn tại với MongoDB credentials
- [ ] Đã restart Cursor
- [ ] MCP server hiển thị trong Cursor

## 📝 Test Connection

Sau khi setup xong, test trong Cursor chat:

```
Query company_metrics for symbol HPG
```

Hoặc:

```
List all collections in MongoDB
```

Nếu MCP server hoạt động, AI sẽ có thể query MongoDB và trả về kết quả.

## 🔗 Tài liệu tham khảo

- [MCP Documentation](https://modelcontextprotocol.io/)
- [MongoDB Python Driver](https://pymongo.readthedocs.io/)
- Xem `CURSOR_MCP_SETUP.md` để biết cách setup ban đầu


