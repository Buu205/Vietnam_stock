# 📋 GIT STRATEGY FOR LARGE FILES (>100MB)

**Ngày:** 2025-12-08
**Mục đích:** Quản lý file lớn trong Vietnam Dashboard

---

## 🎯 PHÂN TÍCH HIỆN TẠI

### 1. Dung lượng hiện tại
```
Tổng dung lượng: 3.4GB
- DATA/: 338MB
  - Lớn nhất: trading_values_full.parquet (40MB)
  - Top 3 file lớn:
    1. trading_values_full.parquet: 40MB
    2. ev_ebitda_historical_all_symbols_final.parquet: 17MB
    3. pb_historical_all_symbols_final.parquet: 7.3MB
```

### 2. Files đang track bởi git
```
PROCESSORS/technical/calculated_results/technical/ma_screening_latest.parquet
convert_parquet_to_excel.py
```
**Đáng chú ý:**
- Git đang track rất ít file parquet
- Các file lớn trong DATA/processed/ không có trong git
- Điều này cho thấy đã có .gitignore hiệu quả

---

## 🛠 GIẢI PHÁP ĐỀ XUẤT

### 1. Tùy chọn A: Giữ nguyên trạng thái (Khuyến nghị)

**Ưu điểm:**
- Giữ đầy đủ history cho development
- Dễ dàng debug và reproduce
- Không cần thay đổi workflow

**Hành động:**
```bash
# 1. Kiểm tra file lớn trong git
git ls-files | grep parquet
# -> Chỉ có 2 file nhỏ trong git

# 2. Kiểm tra .gitignore đã hiệu quả
grep "DATA/" .gitignore
# -> Đã ignore DATA/processed/

# 3. Commit chỉ file code và documentation
git add PROCESSORS/ WEBAPP/ CONFIG/ docs/ scripts/
git commit -m "Update code and documentation
```

### 2. Tùy chọn B: Xóa file lớn không cần thiết

**Khi nào cần:**
- File backup trùng lặp
- File cache có thể tái tạo
- File test/data demo

**Hành động:**
```bash
# Xóa các file backup trùng lặp
find DATA/processed/ -name "*backup*" -delete
find DATA/processed/ -name "*_20*" -delete

# Xóa file cũ (giữ 3 phiên bản gần nhất)
find DATA/processed/fundamental -name "*.parquet" | \
  sort -r | head -n -4 | xargs rm -f
```

### 3. Tùy chọn C: Dùng Git LFS (cho production)

**Khi nào cần:**
- Phải version control cho file lớn
- Team nhiều người cần cùng làm việc

**Hành động:**
```bash
# 1. Cài Git LFS
git lfs install

# 2. Chọn file lớn cần LFS
echo "*.parquet filter=lfs diff=lfs merge=lfs -text" >> .gitattributes

# 3. Import file lớn vào LFS
git lfs track "DATA/processed/technical/trading_values_full.parquet"
git add .gitattributes
git commit -m "Add LFS tracking for large parquet files"
```

---

## 🎯 ĐỀ XUẤT KHUYÊN NGHIỆN

### 1. **Không xóa file quan trọng**
```bash
# TRƯỚC KIỂM TRA:
du -sh DATA/processed/technical/trading_values_full.parquet
# -> 40MB (QUAN TRỌNG CHO TECHNICAL ANALYSIS)

# SAU KIỂM MỚI:
git status
# -> Không có trong git -> Đã được ignore

# NẾU CHỈ CẦN LÀM:
# Giữ nguyên file này, chỉ đảm bảo .gitignore đúng
```

### 2. **Tối ưu .gitignore**
```gitignore
# Thêm vào cuối file:
# Generated parquet files (keep locally, version control schemas only)
DATA/processed/**/*.parquet

# But allow small metadata files
!DATA/processed/**/schema.json
!DATA/processed/**/metadata.json
```

### 3. **Dùng Git LFS cho future**
```bash
# Tạo .gitattributes
echo "*.parquet filter=lfs diff=lfs merge=lfs -text" >> .gitattributes

# Import file lớn nhất
git lfs track "DATA/processed/technical/trading_values_full.parquet"
git lfs track "DATA/processed/valuation/ev_ebitda/ev_ebitda_historical_all_symbols_final.parquet"
git lfs track "DATA/processed/valuation/pb/pb_historical_all_symbols_final.parquet"
```

---

## 📋 RECOMMENDATION

### Khuyến nghị hiện tại:
1. **Giữ nguyên trạng thái** - .gitignore đã hoạt động tốt
2. **Chỉ commit code và docs** - Không commit file data lớn
3. **Tạo script cleanup** - Xóa file backup trùng lặp
4. **Document quy trình** - Ghi rõ cách xử lý file lớn

### Trong tương lai (khi cần):
1. **Cân nhắc Git LFS** - Khi cần version control cho file data
2. **Consider Data Lake** - Cho file rất lớn (>500MB)
3. **Use CI/CD pipeline** - Tự động xử lý file lớn

---

## 📞 QUICK CHECKLIST

Trước khi commit:
- [ ] Kiểm tra `git status` có file lớn không?
- [ ] Kiểm tra `du -sh DATA/processed/technical/` để xác định file lớn
- [ ] Chạy `find DATA/ -name "*backup*" -delete` để dọn dẹp

Sau khi commit:
- [ ] Kiểm tra repository size trên GitHub
- [ ] Test clone trên máy khác để đảm bảo không lỗi
- [ ] Kiểm tra CI/CD pipeline có hoạt động

---

**File này nên được cập nhật khi:**
- Thêm file parquet lớn mới vào LFS tracking
- Quy trình cleanup được tự động hóa
- Có thay đổi về storage requirements

---

**Ngày tạo:** 2025-12-08  
**Người tạo:** Senior Data Architect