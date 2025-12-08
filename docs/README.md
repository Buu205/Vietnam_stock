# 📚 Stock Dashboard Documentation

**Last Updated:** 2025-12-07
**Version:** 3.0.0

---

## 🎯 BẮT ĐẦU TẠI ĐÂY

### 📖 Main Document (Đọc file này trước!)

**[`/CURRENT_STATUS.md`](../CURRENT_STATUS.md)** ⭐ **DOCUMENT DUY NHẤT CẦN ĐỌC**

File này có tất cả:
- ✅ Đã làm gì (Phase 0.1 → v3.0)
- 🔄 Đang làm gì (hiện tại)
- ⏳ Cần làm gì (next steps)
- 💡 Quick reference (how to use)

---

## 📂 FOLDER STRUCTURE

```
docs/
├── README.md                    ← File này (entry point)
├── VNSTOCK_TA_VIETNAM_FEATURES.md  (future reference)
├── mongodb_mcp/                 (MCP documentation - when ready)
├── troubleshooting/             (debug guides)
│   └── DEBUG_COMMODITY.md
└── archive/                     (old docs - không cần đọc)
    └── phase_0_history/         (28 archived files)
```

---

## 🚀 QUICK LINKS

### For Development
- **Current Status:** [`/CURRENT_STATUS.md`](../CURRENT_STATUS.md)
- **Usage Guide:** [`/CLAUDE.md`](../CLAUDE.md)
- **Structure:** [`/STRUCTURE_V3.md`](../STRUCTURE_V3.md)

### For MCP Integration (When Ready)
- **MCP Index:** [`mongodb_mcp/INDEX.md`](./mongodb_mcp/INDEX.md)
- **MCP Setup:** [`mongodb_mcp/MONGODB_SETUP.md`](./mongodb_mcp/MONGODB_SETUP.md)

### For Troubleshooting
- **Commodity Debug:** [`troubleshooting/DEBUG_COMMODITY.md`](./troubleshooting/DEBUG_COMMODITY.md)

---

## ℹ️ DOCUMENTATION POLICY

**Chỉ tạo MD file khi:**
- ✅ Có thay đổi MAJOR (như v3.0 reorganization)
- ✅ Cần reference dài hạn (architecture docs)
- ❌ KHÔNG tạo cho minor updates
- ❌ KHÔNG duplicate info

**Main document:** `/CURRENT_STATUS.md` - Update file này thay vì tạo file mới

---

## 📊 CURRENT STATE (Quick Summary)

### v3.0 Structure
```
stock_dashboard/
├── DATA/          1.1GB    # All data
├── PROCESSORS/    9.9MB    # All logic
├── WEBAPP/                 # Dashboard
├── CONFIG/                 # Configuration
└── logs/                   # Logs
```

### Status
- ✅ Phase 0.1-0.2 complete
- ✅ v3.0 reorganization complete
- ✅ Production ready
- ⏳ MCP integration (when ready)

**Details:** See `/CURRENT_STATUS.md`

---

## 🗂️ ARCHIVED DOCS

**28 old documents** archived to `archive/phase_0_history/`:
- Phase 0 planning docs (15 files): REORGANIZATION_*.md, PHASE*.md, etc.
- v3.0 cleanup docs (5 files): STRUCTURE_V3.md, NEXT_STEPS.md, etc.
- Architecture docs (8 files): DATA_STANDARDIZATION.md, ENHANCED_ROADMAP*.md, etc.

**Lý do archive:**
- All content consolidated into `/CURRENT_STATUS.md`
- v3.0 complete, planning docs no longer needed

**Có thể xóa sau:** 1 tháng (nếu không cần rollback)

---

**🎯 TL;DR:** Chỉ cần đọc [`/CURRENT_STATUS.md`](../CURRENT_STATUS.md)
