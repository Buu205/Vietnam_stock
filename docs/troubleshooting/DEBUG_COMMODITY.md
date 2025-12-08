# Debug Commodity Chart Not Showing Latest Data

## ✅ Code đã được fix và test thành công

Test results cho thấy:
```
✅ pork_north_vn: Latest 2025-12-03 @ 57,833.33 VND/kg
✅ pork_china:    Latest 2025-11-18 @ 12.50 CNY/kg
Caption: "Dữ liệu mới nhất: 2025-12-03"
```

## 🔍 Nếu UI vẫn hiển thị data cũ, nguyên nhân là CACHE

### Giải pháp 1: Clear Streamlit Cache (RECOMMENDED)

**Bước 1**: Vào Streamlit UI
- Mở tab **"📦 Commodity Prices"**
- Chọn **"Giá heo hơi"** từ dropdown

**Bước 2**: Click nút **"🔄 Reload Data"**
- Nút này ở ngay phía trên dropdown commodity selector (line 1020 trong technical_dashboard.py)
- Nút sẽ gọi `CommodityLoader.clear_cache()` và reload data

**Bước 3**: Check caption
- Sau khi reload, caption phải hiển thị: `Dữ liệu mới nhất: 2025-12-03`

### Giải pháp 2: Restart Streamlit App

```bash
# 1. Stop Streamlit (Ctrl+C)
# 2. Start lại
streamlit run streamlit_app/main_app.py
```

### Giải pháp 3: Clear Browser Cache

```
Chrome/Edge: Ctrl + Shift + R (Hard reload)
Firefox: Ctrl + Shift + R
Safari: Cmd + Shift + R
```

### Giải pháp 4: Force Clear Cache (Nuclear option)

Nếu vẫn không work, chạy script này để force clear:

```bash
cd /Users/buuphan/Dev/stock_dashboard

python3 -c "
import sys
sys.path.insert(0, '.')

from streamlit_app.services.commodity_loader import CommodityLoader
import streamlit as st

# Force clear cache
try:
    CommodityLoader.clear_cache()
    print('✅ Commodity cache cleared')
except Exception as e:
    print(f'⚠️  Cache clear failed: {e}')

# Also clear streamlit cache directory if exists
import shutil
from pathlib import Path

cache_dirs = [
    Path.home() / '.streamlit' / 'cache',
    Path('.streamlit') / 'cache',
]

for cache_dir in cache_dirs:
    if cache_dir.exists():
        try:
            shutil.rmtree(cache_dir)
            print(f'✅ Removed cache dir: {cache_dir}')
        except Exception as e:
            print(f'⚠️  Could not remove {cache_dir}: {e}')

print()
print('Cache cleared! Now restart Streamlit.')
"
```

## 🧪 Verify Fix is Working

Chạy test script để verify data đang load đúng:

```bash
python3 -c "
import sys
sys.path.insert(0, '.')

from streamlit_app.services.commodity_loader import CommodityLoader
import pandas as pd

loader = CommodityLoader()
CommodityLoader.clear_cache()

# Load pork data
end_date = pd.Timestamp.now()
start_date = end_date - pd.Timedelta(days=365)

df = loader.get_multiple_commodities(
    ['pork_north_vn', 'pork_china'],
    start_date=start_date.strftime('%Y-%m-%d'),
    end_date=end_date.strftime('%Y-%m-%d')
)

print('=== Data Summary ===')
print(f'Total rows: {len(df)}')
print(f'Date range: {df[\"date\"].min()} to {df[\"date\"].max()}')
print()

for commodity in ['pork_north_vn', 'pork_china']:
    cdf = df[df['commodity_type'] == commodity]
    if not cdf.empty:
        valid = cdf[cdf['close'].notna() & (cdf['close'] > 0)]
        if not valid.empty:
            latest = valid.iloc[-1]
            print(f'✅ {commodity:20} | Latest: {latest[\"date\"].strftime(\"%Y-%m-%d\")} | Price: {latest[\"close\"]:,.2f}')
        else:
            print(f'⚠️  {commodity}: No valid price data')
    else:
        print(f'❌ {commodity}: No data')
"
```

**Expected output:**
```
=== Data Summary ===
Total rows: 198
Date range: 2024-12-04 00:00:00 to 2025-12-03 00:00:00

✅ pork_north_vn        | Latest: 2025-12-03 | Price: 57,833.33
✅ pork_china           | Latest: 2025-11-18 | Price: 12.50
```

## 📸 Screenshot để debug

Nếu vẫn không work, chụp screenshot cho tôi thấy:
1. Caption hiển thị ngày nào? (ví dụ: "Dữ liệu mới nhất: 2025-XX-XX")
2. Chart có hiển thị data đến ngày nào?
3. Console có lỗi gì không? (F12 → Console tab)

## 🔧 Alternative: Force reload trong code

Nếu cần, có thể sửa code để force reload mỗi lần load page:

```python
# In streamlit_app/services/commodity_loader.py, line 105
def load_data(self, force_reload: bool = True):  # Change False → True
    if force_reload:
        _load_commodity_data_cached.clear()
```

Nhưng cách này sẽ làm app chậm hơn vì phải reload data mỗi lần.
