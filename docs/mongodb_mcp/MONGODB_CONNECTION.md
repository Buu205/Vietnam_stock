# MongoDB Connection String - Hướng dẫn kết nối

## 🔗 Connection String

Connection string của bạn để kết nối với MongoDB Atlas:

```
mongodb+srv://buuphanquoc_db:Quocbuu123@cluster0.m6tqpie.mongodb.net/?appName=Cluster0
```

## 📋 Thông tin kết nối

- **Username**: `buuphanquoc_db`
- **Password**: `Quocbuu123`
- **Cluster**: `cluster0.m6tqpie.mongodb.net`
- **Database Name**: `mydb`
- **App Name**: `Cluster0`

## 🔧 Cấu hình cho MCP Server Plugin

### Option 1: Sử dụng file .env (Đã được cấu hình)

File `.env` đã được tạo với connection string. MCP server sẽ tự động đọc từ file này.

### Option 2: Cấu hình trong Cursor Settings

Nếu bạn đang dùng MongoDB plugin trong Cursor, cấu hình như sau:

1. **Mở Cursor Settings** (Cmd/Ctrl + ,)
2. **Tìm "MCP Servers"** hoặc "Model Context Protocol"
3. **Thêm cấu hình:**

```json
{
  "mcpServers": {
    "mongodb-finance-metrics": {
      "command": "python",
      "args": ["-m", "mcp_server.server"],
      "env": {
        "MONGODB_URI": "mongodb+srv://buuphanquoc_db:Quocbuu123@cluster0.m6tqpie.mongodb.net/?appName=Cluster0",
        "MONGODB_DB_NAME": "mydb"
      }
    }
  }
}
```

### Option 3: Sử dụng file mcp_config.json

File `mcp_server/mcp_config.json` đã được tạo sẵn. Bạn có thể tham khảo hoặc import vào Cursor settings.

## 🧪 Test Connection

### Test bằng Python:

```python
from mongodb.config import get_mongodb_client

try:
    client = get_mongodb_client()
    print("✅ Connected successfully!")
    print(f"Databases: {client.list_database_names()}")
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

### Test bằng MongoDB Compass:

1. Mở MongoDB Compass
2. Paste connection string:
   ```
   mongodb+srv://buuphanquoc_db:Quocbuu123@cluster0.m6tqpie.mongodb.net/?appName=Cluster0
   ```
3. Click "Connect"

## 📝 Collections Available

Sau khi upload dữ liệu, các collections sẽ có:

- `company_metrics` - Financial metrics cho companies
- `bank_metrics` - Financial metrics cho banks  
- `insurance_metrics` - Financial metrics cho insurance companies
- `security_metrics` - Financial metrics cho securities companies

## 🔒 Security Notes

⚠️ **QUAN TRỌNG:**
- Connection string chứa password, **KHÔNG commit** vào Git
- File `.env` đã được thêm vào `.gitignore`
- Chỉ share connection string với người được phép

## 🐛 Troubleshooting

### Lỗi SSL Certificate

Nếu gặp lỗi SSL certificate, có thể cần:
1. Cài đặt certificates cho Python
2. Hoặc thêm `tlsAllowInvalidCertificates=true` vào connection string (không khuyến nghị cho production)

### Connection Timeout

1. Kiểm tra network connection
2. Kiểm tra MongoDB Atlas IP whitelist
3. Tăng timeout trong config nếu cần

### Authentication Failed

1. Kiểm tra username/password
2. Kiểm tra database user permissions trong MongoDB Atlas

## 📚 Tài liệu tham khảo

- [MongoDB Connection String Format](https://www.mongodb.com/docs/manual/reference/connection-string/)
- [MongoDB Atlas Connection](https://www.mongodb.com/docs/atlas/connect-to-cluster/)
- [MCP Server Documentation](https://modelcontextprotocol.io/)

