# MongoDB Support Module

Module hỗ trợ upload và query dữ liệu financial metrics lên MongoDB Atlas.

## Cấu trúc

```
mongodb/
├── __init__.py          # Module exports
├── config.py            # MongoDB connection với ServerApi
├── uploader.py          # Main upload script
├── utils.py             # Helper functions
├── queries.py           # Query examples
└── README.md            # Documentation
```

## Cài đặt

1. **Cài đặt dependencies:**
```bash
pip install pymongo python-dotenv
```

2. **Tạo file .env ở root directory:**
```bash
cp mongodb/.env.example .env
```

3. **Cập nhật .env với credentials:**
```env
MONGODB_URI=mongodb+srv://buuphanquoc_db:Quocbuu123@cluster0.m6tqpie.mongodb.net/?appName=Cluster0
MONGODB_DB_NAME=mydb
```

## Collections

Các collections được upload từ parquet files:

- `company_metrics` ← `calculated_results/fundamental/company/company_financial_metrics.parquet`
- `bank_metrics` ← `calculated_results/fundamental/bank/bank_financial_metrics.parquet`
- `insurance_metrics` ← `calculated_results/fundamental/insurance/insurance_financial_metrics.parquet`
- `security_metrics` ← `calculated_results/fundamental/security/security_financial_metrics.parquet`

## Unique Index

Mỗi collection có unique index trên:
- `(symbol, report_date, year, quarter)`

## Sử dụng

### Upload dữ liệu

**Upload tất cả collections:**
```python
from mongodb.uploader import upload_all_collections

results = upload_all_collections()
print(results)
```

**Upload một collection cụ thể:**
```python
from mongodb.uploader import upload_parquet_to_mongodb

stats = upload_parquet_to_mongodb(
    parquet_path='calculated_results/fundamental/company/company_financial_metrics.parquet',
    collection_name='company_metrics'
)
print(f"Inserted: {stats['inserted']}, Updated: {stats['updated']}")
```

**Command line:**
```bash
# Upload tất cả
python -m mongodb.uploader

# Upload một collection
python -m mongodb.uploader --collection company_metrics --parquet calculated_results/fundamental/company/company_financial_metrics.parquet
```

### Query dữ liệu

```python
from mongodb.config import get_database
from mongodb.queries import get_latest_metrics, get_top_symbols_by_metric

db = get_database()
company_collection = db['company_metrics']

# Lấy metrics mới nhất cho một symbol
latest = get_latest_metrics(company_collection, symbol='HPG', limit=5)

# Lấy top symbols theo metric
top_margin = get_top_symbols_by_metric(
    company_collection,
    metric_field='gross_margin',
    limit=10
)
```

## Query Examples

Xem file `queries.py` để biết thêm các query examples:
- `get_latest_metrics()` - Lấy metrics mới nhất
- `get_metrics_by_period()` - Filter theo period
- `get_metrics_by_value_range()` - Filter theo giá trị
- `get_top_symbols_by_metric()` - Top symbols theo metric
- `get_metric_timeseries()` - Time series data
- `compare_symbols_metrics()` - So sánh nhiều symbols

## Notes

- Dùng upsert logic: update nếu đã có, insert nếu chưa có
- Unique index đảm bảo không có duplicate records
- Tự động normalize symbol (uppercase, strip whitespace)
- Convert NaN/None values để MongoDB compatible

