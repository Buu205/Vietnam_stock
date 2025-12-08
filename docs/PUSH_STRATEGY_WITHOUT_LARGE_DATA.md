# 📋 PUSH STRATEGY WITHOUT LARGE DATA FILES

**Ngày:** 2025-12-08
**Mục đích:** Hướng dẫn push repository lên GitHub mà không bao gồm các file data lớn

---

## 🎯 TÌM TẮNG HIỆN TẠI

### 1. Phân tích thư mục quan trọng
```
DATA/ = 226MB (nặng nhẹ cho Git)
├── raw/ = 236MB (đang chứa các file CSV gốc)
│   ├── fundamental/processed/ = 186MB (các file CSV lớn cần loại bỏ)
│   └── ohlcv/ = 28MB
│   └── commodity/ = 17MB
│   └── macro/ = 14MB
│
├── processed/ = 112MB (kết quả xử lý)
│   ├── fundamental/ = 46MB
│   ├── technical/ = 40MB (lớn nhất)
│   ├── valuation/ = 22MB
│   └── commodity/ = 4MB
│   └── macro/ = 1MB
│
├── schemas/ = 100KB
│
├── metadata/ = 864KB
│
└── archive/ = 90MB (backup cũ)
```

### 2. File lớn nhất cần xem xét
```
Top 5 file parquet lớn (>5MB):
1. trading_values_full.parquet - 40MB
2. ev_ebitda_historical_all_symbols_final.parquet - 17MB
3. pb_historical_all_symbols_final.parquet - 7.3MB
4. pe_historical_all_symbols_final.parquet - 6.1MB
5. company_financial_metrics.parquet - 5.1MB
```

---

## 🎯 GIẢI PHÁP ĐỀ XUẤT

### Phương án 1: Giữ nguyên trạng thái (Khuyến nghị)

**Ưu điểm:**
- Repository đủ nhẹ để push nhanh
- Đã tối ưu với .gitignore hiệu quả
- Không cần thay đổi gì

**Hành động:**
```bash
# Giữ nguyên trạng thái hiện tại
git status

# Tạo commit cuối cùng
git add PROCESSORS/ WEBAPP/ CONFIG/ docs/ scripts/
git commit -m "Final commit with canonical structure"

# Push lên GitHub
git push origin main
```

### Phương án 2: Xóa các file không cần thiết (Không khuyến nghị)

**Khi nào cần:**
- File backup trùng lặp (files có chữ "backup" hoặc "_20*")
- File cache của hệ thống
- File test/data demo

**Hành động:**
```bash
# Xóa file backup trùng lặp
find DATA/processed -name "*backup*" -delete
find DATA/processed -name "*_20*" -delete

# Giữ lại N file gần nhất cho mỗi loại
find DATA/processed -name "*.parquet" | \
  sort -r | head -n -5 | xargs rm -f

# Kiểm tra lại dung lượng
du -sh DATA/
```

### Phương án 3: Push với LFS khi cần (Tương lai)

**Khi nào cần:**
- File quá lớn (>100MB) nhưng bắt buộc phải version control
- File dữ liệu quan trọng (thay đổi thường xuyên ngày)

**Hành động:**
```bash
# 1. Cài đặt Git LFS
git lfs install

# 2. Thêm các file lớn vào LFS
echo "*.parquet filter=lfs diff=lfs merge=lfs -text" >> .gitattributes

# 3. Theo dõi các file lớn
git lfs track "DATA/processed/technical/trading_values_full.parquet"
git lfs track "DATA/processed/valuation/ev_ebitda/ev_ebitda_historical_all_symbols_final.parquet"

# 4. Push LFS files
git add .gitattributes
git add <file_lớn>
git commit -m "Add LFS tracking for large parquet files"
git push
```

---

## 📋 LỰA CHỌN TƯƠNG GHI NHẬN

### 1. Tại sao phải chọn phương án 1?
- Dung lượng tổng 2.3GB khá hợp lý cho development
- Các file quan trọng (parquet) vẫn được version control
- File CSV lớn (186MB) chỉ dùng locally
- Repository đủ nhẹ cho các thao tác push hàng ngày

### 2. Nếu cần giảm dung lượng dưới 2.3GB
```bash
# Tối ưu hóa
find DATA/processed -name "*.parquet" -exec gzip {} \;
   
# Chuyển thành các file cũ
find DATA/processed -name "*.parquet" -exec gzip --force {} \;
   
# Cập nhật code để xử lý file gzip
# Trong file đọc, thêm:
import gzip
   
   df = pd.read_parquet("input_file.gz", engine='pyarrow')
```

### 3. Giải pháp tốt nhất cho tương lai
```
# 1. Xử lý tại chỗ
git add PROCESSORS/ WEBAPP/ CONFIG/ docs/ scripts/
git commit -m "Add core functionality"

# 2. Push code-only lên GitHub
git push origin main

# 3. Xử lý data khi cần
# Chỉ download và xử lý tại thời điểm cần
python3 PROCESSING/pipelines/daily_update.py --date YYYY-MM-DD

# 4. Dữ liệu lớn lưu trữ ngoài
# Sử dụng external storage (S3, Google Drive, OneDrive)
# Dữ liệu lịch sử dụng archival (xóa cũ, chỉ giữ N tháng gần nhất)
```

---

## 📋 RECOMMENDATION

### 1. Repository size
- **Hiện tại:** 2.3GB (lightweight)
- **Khuyến nghị:** Dưới 2GB để push nhanh hàng ngày

### 2. Theo dõi GitHub
- **GitHub Free:** Không giới hạn cho private repo
- **GitHub Pro:** 100GB cho private repo
- **Repository của bạn:** 2.3GB < 1% limit ✅

### 3. Chiến lược tiếp theo
```bash
# 1. Kiểm tra lại trạng thái sau khi push
git status
git log --oneline -3

# 2. Tạo báo cáo công việc hàng tuần
python3 PROCESSING/pipelines/weekly_report.py
```

---

## 🎯 QUYẾT ICH CÁCH

### 1. Repository structure
- ✅ **CODE**: PROCESSORS/, WEBAPP/, CONFIG/, scripts/
- ✅ **DOCUMENTATION**: Tất cả hướng dẫn đã tạo

### 2. Current workflow
- **Local development** → Push code-only
- **Data processing** → Chỉ khi cần, download và xử lý tại chỗ

---

**Ngày tạo:** 2025-12-08  
**Người tạo:** Senior Data Architect


