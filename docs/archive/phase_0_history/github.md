## Local Root Setup – stock_dashboard

**Root mới để phát triển:**

- `/Users/buuphan/Dev/stock_dashboard`
- Repo này được clone từ GitHub: `https://github.com/Buu205/stock_dashboard.git`
- Không còn phụ thuộc đường dẫn iCloud `.../Library/Mobile Documents/...` trong quá trình dev và git.

**Python & thư viện:**

- Dùng Python global 3.13:
  - Binary: `python3` (hoặc `/Library/Frameworks/Python.framework/Versions/3.13/bin/python3`)
- `vnstock_data` đã cài sẵn tại:
  - `/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/site-packages`
- Di chuyển/clone repo **không ảnh hưởng** tới `vnstock_data` và các package global khác.

**Chạy ứng dụng & scripts (local root):**

```bash
cd "/Users/buuphan/Dev/stock_dashboard"

# Chạy Streamlit dashboard
streamlit run streamlit_app/main_app.py

# Ví dụ chạy pipeline technical/valuation
python3 data_processor/technical/daily_full_technical_pipeline.py
python3 data_processor/valuation/daily_full_valuation_pipeline.py
```

**Chuẩn hóa đường dẫn dữ liệu (Data paths):**

- **Project root**: `/Users/buuphan/Dev/stock_dashboard`
- **Input dữ liệu gốc**:
  - `data_warehouse/raw/ohlcv/OHLCV_mktcap.parquet` (giá/khối lượng)
  - `data_warehouse/raw/fundamental/processed/...` (fundamental bank/company,…)
- **Output tính toán**:
  - `calculated_results/technical/...` (basic_data, MA/EMA, RSI, MACD, signals, breadth,…)
  - `calculated_results/fundamental/...` (bank/company metrics)
  - `calculated_results/valuation/...` (VNIndex PE, sector PE, BSC Universal,…)
- Các script trong `data_processor` **không dùng path iCloud**, mà tự resolve từ project root:
  - Input luôn đọc dưới `data_warehouse/...`
  - Output luôn ghi xuống `calculated_results/...`

**Quy trình git (commit + push) tại local root:**

```bash
cd "/Users/buuphan/Dev/stock_dashboard"

# Xem thay đổi
git status

# Commit nhanh tất cả file đã track
git commit -am "Mô tả ngắn gọn thay đổi"

# Đẩy lên GitHub
git push
```

Nếu cần commit chính xác vài file:

```bash
cd "/Users/buuphan/Dev/stock_dashboard"

git add streamlit_app/main_app.py data_processor/technical/daily_full_technical_pipeline.py
git commit -m "Mô tả thay đổi"
git push
```

**Ghi chú:**

- Bản cũ ở iCloud (`.../GitHub/stock_dashboard`) giữ như **backup**, không sửa nữa.
- Mọi chỉnh sửa code, path, pipeline mới sẽ thực hiện trong `/Users/buuphan/Dev/stock_dashboard`.