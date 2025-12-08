# 📋 TERMINAL PUSH GUIDE

**Ngày:** 2025-12-08
**Trạng thái:** 📋 Hướng dẫn khi gặp lỗi sandbox

---

## 🛠 PROBLEM IDENTIFICATION

### Common Errors & Solutions

| Lỗi | Nguyên nhân | Giải pháp |
|------|-----------|------------|
| "Invalid arguments" | SwitchMode cần tham số "agent" hoặc "plan" | Kiểm tra lại tham số |
| "failed to store" | File .gitconfig bị khóa | Xóa file: `rm -f .gitconfig && git config --global` |
| "could not read username" | GitHub auth chưa đúng | Cấu hình lại: `git config --global user.name "username"` |
| "remote not found" | URL remote sai hoặc repository không tồn tại | Kiểm tra lại URL: `git remote -v` |

---

## 📝 HƯỚNG DẪN TRONG TERMINAL

### 1. Kiểm tra phiên GitHub CLI
```bash
gh --version
```

### 2. Đăng nhập lại vào GitHub
```bash
gh auth login
```

### 3. Kiểm tra trạng thái
```bash
gh auth status
```

### 4. Thiết lập lại repository remote
```bash
cd /Users/buuphan/Dev/Vietnam_dashboard
git remote rm origin
git remote add origin https://github.com/Buu205/Vietnam_stock.git
git remote set-url --push origin https://github.com/Buu205/Vietnam_stock.git
```

### 5. Push lên GitHub
```bash
git push origin main
```

---

## 📋 VẤN ĐỀI XỬ TRA

### 1. Trong terminal thông thường
- Mở một terminal mới (không thông qua IDE)
- Chạy các lệnh từ Terminal Guide

### 2. Nếu vẫn gặp lỗi GitHub authentication trong sandbox
- Thử SSH key thay vì thường ổn định hơn trong môi trường này
- Tạo SSH key: `ssh-keygen -t rsa -C "email@example.com"`
- Thêm vào GitHub: https://github.com/settings/keys

### 3. Sử dụng Personal Access Token (PAT)
- Tạo token tại: https://github.com/settings/tokens
- Sử dụng khi push: `git push https://username:token@github.com/username/repo.git`

---

## 🎯 THÀNH CÔNG

### 1. Terminal Guide cho người không kỹ thuật
```
# Bước 1: Mở Terminal (Applications → Utilities → Terminal)
# Bước 2: Kiểm tra phiên Git
git --version

# Bước 3: Kiểm tra trạng thái
git status

# Bước 4: Cấu hình lại (nếu cần)
git config --global user.name "username"
git config --global user.email "email@example.com"

# Bước 5: Thiết lập lại remote (nếu cần)
git remote add origin https://github.com/username/repo.git

# Bước 6: Đăng nhập (nếu cần)
gh auth login

# Bước 7: Push code
git add .
git commit -m "Update code"
git push origin main
```

### 2. Advanced: Sử dụng SSH Key
```bash
# Tạo SSH key
ssh-keygen -t rsa -C "email@example.com"

# Thêm vào ssh-agent
eval "$(ssh-agent -s)" && eval "$(ssh-agent -s)"

# Test kết nối
ssh -T git@github.com

# Push với SSH
git remote set-url origin git@github.com:username/repo.git
git push origin main
```

---

**Ngày tạo:** 2025-12-08  
**Người tạo:** Senior Data Architect


