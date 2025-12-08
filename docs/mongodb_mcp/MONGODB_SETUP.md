# MongoDB Support - Hướng dẫn Setup

Tài liệu hướng dẫn setup và sử dụng MongoDB support cho VN Finance Dashboard.

## 📋 Tổng quan

Hệ thống MongoDB support bao gồm:
1. **MongoDB Module** (`mongodb/`): Upload và query dữ liệu financial metrics
2. **MCP Server** (`mcp_server/`): MCP server cho Claude/ChatGPT integration
3. **Streamlit LLM Integration** (`streamlit_app/services/`, `streamlit_app/ai/`): AI Chat interface

## 🚀 Quick Start

### 1. Cài đặt Dependencies

```bash
pip install pymongo python-dotenv openai google-generativeai mcp
```

Hoặc từ requirements.txt:
```bash
pip install -r streamlit_app/requirements.txt
```

### 2. Cấu hình MongoDB

1. **Tạo file `.env` ở root directory:**
```bash
cp .env.example .env
```

2. **Cập nhật `.env` với credentials:**
```env
MONGODB_URI=mongodb+srv://buuphanquoc_db:Quocbuu123@cluster0.m6tqpie.mongodb.net/?appName=Cluster0
MONGODB_DB_NAME=mydb

# Optional: LLM API Keys
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Upload Dữ liệu

**Upload tất cả collections:**
```bash
python -m mongodb.uploader
```

**Upload một collection cụ thể:**
```bash
python -m mongodb.uploader --collection company_metrics --parquet calculated_results/fundamental/company/company_financial_metrics.parquet
```

**Hoặc dùng Python:**
```python
from mongodb.uploader import upload_all_collections

results = upload_all_collections()
print(results)
```

## 📁 Cấu trúc Collections

Các collections được upload từ parquet files:

| Collection | Source File |
|------------|-------------|
| `company_metrics` | `calculated_results/fundamental/company/company_financial_metrics.parquet` |
| `bank_metrics` | `calculated_results/fundamental/bank/bank_financial_metrics.parquet` |
| `insurance_metrics` | `calculated_results/fundamental/insurance/insurance_financial_metrics.parquet` |
| `security_metrics` | `calculated_results/fundamental/security/security_financial_metrics.parquet` |

### Unique Index

Mỗi collection có unique index trên:
- `(symbol, report_date, year, quarter)`

## 🔧 Sử dụng MongoDB Module

### Query Examples

```python
from mongodb.config import get_database
from mongodb.queries import (
    get_latest_metrics,
    get_top_symbols_by_metric,
    get_metric_timeseries
)

db = get_database()
company_collection = db['company_metrics']

# Lấy metrics mới nhất cho HPG
latest = get_latest_metrics(company_collection, symbol='HPG', limit=5)

# Top 10 symbols theo gross margin
top_margin = get_top_symbols_by_metric(
    company_collection,
    metric_field='gross_margin',
    limit=10
)

# Time series của gross margin cho HPG
timeseries = get_metric_timeseries(
    company_collection,
    symbol='HPG',
    metric_field='gross_margin'
)
```

Xem thêm trong `mongodb/queries.py` và `mongodb/README.md`.

## 🤖 MCP Server

MCP Server cho phép Claude/ChatGPT query MongoDB qua Model Context Protocol.

### Chạy MCP Server

```bash
python -m mcp_server.server
```

### Tools Available

1. **query_collection**: Query với filters
2. **get_collection_schema**: Lấy schema information
3. **list_collections**: Liệt kê collections
4. **get_collection_stats**: Lấy statistics

Xem thêm trong `mcp_server/README.md`.

## 💬 Streamlit AI Chat

AI Chat interface cho phép query dữ liệu bằng natural language.

### Chạy Streamlit App

```bash
streamlit run streamlit_app/main_app.py
```

Sau đó truy cập page "AI Chat" hoặc:
```bash
streamlit run streamlit_app/pages/ai_chat.py
```

### Ví dụ câu hỏi

- "Lấy metrics mới nhất của HPG"
- "Top 10 công ty có gross margin cao nhất"
- "So sánh ROE của HPG, VCB, POW"
- "Time series của gross margin cho HPG"

### Cấu hình

- Chọn collection: company_metrics, bank_metrics, etc.
- Chọn LLM provider: OpenAI hoặc Gemini
- Cần set API key trong `.env` file

## 📝 Notes

### Security

- **KHÔNG commit file `.env`** vào Git
- File `.env.example` là template, không chứa credentials thực
- MongoDB password được lưu trong `.env` file

### Performance

- Unique index đảm bảo không có duplicate records
- Upsert logic: update nếu đã có, insert nếu chưa có
- Batch processing với batch_size=1000 mặc định

### Data Format

- Symbol được normalize: uppercase + strip whitespace
- NaN/None values được convert để MongoDB compatible
- Date columns được convert sang ISO format strings

## 🐛 Troubleshooting

### Connection Error

```
Failed to connect to MongoDB: ...
```

**Giải pháp:**
1. Kiểm tra MongoDB URI trong `.env`
2. Kiểm tra network connection
3. Kiểm tra MongoDB Atlas IP whitelist

### Import Error

```
ModuleNotFoundError: No module named 'pymongo'
```

**Giải pháp:**
```bash
pip install pymongo python-dotenv
```

### LLM API Error

```
OPENAI_API_KEY not found
```

**Giải pháp:**
1. Set `OPENAI_API_KEY` hoặc `GEMINI_API_KEY` trong `.env`
2. Hoặc set environment variable:
```bash
export OPENAI_API_KEY=your_key_here
```

## 📚 Tài liệu tham khảo

- [MongoDB Python Driver](https://pymongo.readthedocs.io/)
- [MCP Protocol](https://modelcontextprotocol.io/)
- [OpenAI API](https://platform.openai.com/docs)
- [Google Gemini API](https://ai.google.dev/docs)

## ✅ Checklist

- [ ] Đã cài đặt dependencies
- [ ] Đã tạo file `.env` với MongoDB credentials
- [ ] Đã upload dữ liệu lên MongoDB
- [ ] Đã test MongoDB connection
- [ ] (Optional) Đã set LLM API keys cho AI Chat
- [ ] (Optional) Đã test MCP server
- [ ] (Optional) Đã test Streamlit AI Chat

