# Cấu hình MCP Server trong Cursor

Hướng dẫn thêm MongoDB MCP Server vào Cursor settings.

## 🎯 Cách 1: Thêm trực tiếp vào Cursor Settings (Khuyến nghị)

1. **Mở Cursor Settings:**
   - Nhấn `Cmd + ,` (Mac) hoặc `Ctrl + ,` (Windows/Linux)
   - Hoặc: `Cursor` → `Settings` → `Settings`

2. **Tìm MCP Settings:**
   - Tìm kiếm: `mcp` hoặc `Model Context Protocol`
   - Hoặc vào: `Features` → `MCP` → `Servers`

3. **Thêm cấu hình:**

   Click vào `Edit in settings.json` và thêm đoạn sau:

```json
{
  "mcp.servers": {
    "mongodb-finance-metrics": {
      "command": "/usr/local/bin/python3",
      "args": [
        "-m",
        "mcp_server.server"
      ],
      "cwd": "${workspaceFolder}",
      "env": {
        "MONGODB_URI": "mongodb+srv://buuphanquoc_db:Quocbuu123@cluster0.m6tqpie.mongodb.net/?appName=Cluster0",
        "MONGODB_DB_NAME": "mydb"
      }
    }
  }
}
```

## 🎯 Cách 2: Sử dụng file cấu hình có sẵn

File `.cursor/mcp.json` đã được tạo sẵn. Nếu Cursor tự động đọc file này, bạn không cần làm gì thêm.

Nếu không, bạn có thể:
1. Mở file `.cursor/mcp.json`
2. Copy nội dung
3. Paste vào Cursor Settings như Cách 1

## 🎯 Cách 3: Thêm vào User Settings

1. **Mở Command Palette:**
   - `Cmd + Shift + P` (Mac) hoặc `Ctrl + Shift + P` (Windows/Linux)

2. **Tìm:** `Preferences: Open User Settings (JSON)`

3. **Thêm cấu hình tương tự như Cách 1**

## ✅ Kiểm tra cấu hình

Sau khi thêm cấu hình:

1. **Restart Cursor** (quan trọng!)
2. **Kiểm tra MCP Server:**
   - Mở Command Palette (`Cmd + Shift + P`)
   - Tìm: `MCP: List Servers` hoặc `MCP: Show Server Status`
   - Bạn sẽ thấy `mongodb-finance-metrics` trong danh sách

3. **Test connection:**
   - Trong chat với AI, thử hỏi: "Query company_metrics for symbol HPG"
   - Hoặc: "List all collections in MongoDB"

## 🔧 Troubleshooting

### MCP Server không hiển thị

1. **Kiểm tra Python path:**
   - Thay `/usr/local/bin/python3` bằng đường dẫn Python thực tế của bạn
   - Tìm path: `which python3` (Mac/Linux) hoặc `where python3` (Windows)

2. **Kiểm tra dependencies:**
```bash
pip install pymongo python-dotenv mcp
```

3. **Kiểm tra file .env:**
   - Đảm bảo file `.env` tồn tại ở root directory
   - Hoặc cấu hình env vars trực tiếp trong settings như trên

### Lỗi "Module not found"

```bash
# Cài đặt dependencies
pip install pymongo python-dotenv mcp

# Hoặc từ requirements
pip install -r streamlit_app/requirements.txt
```

### Lỗi "Command not found"

Thay đổi `command` trong settings:
- Mac: `/usr/local/bin/python3` hoặc `python3`
- Windows: `python` hoặc `py`
- Linux: `/usr/bin/python3` hoặc `python3`

## 📝 Notes

- **Workspace folder**: `${workspaceFolder}` sẽ tự động resolve thành đường dẫn project hiện tại
- **Environment variables**: Có thể đặt trong `env` hoặc dùng file `.env`
- **Restart required**: Sau khi thay đổi settings, cần restart Cursor

## 🚀 Sau khi setup

Bạn có thể sử dụng MCP server để:
- Query MongoDB collections qua natural language
- Lấy schema information
- So sánh metrics giữa các symbols
- Lấy time series data

Ví dụ câu hỏi:
- "Get latest metrics for HPG"
- "Top 10 companies by gross margin"
- "Compare ROE for HPG, VCB, POW"
- "Show schema for company_metrics"

