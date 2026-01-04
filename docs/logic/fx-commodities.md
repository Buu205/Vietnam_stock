# FX & Commodities Dashboard Logic Reference

Pure business logic for macro/FX/commodity tracking. No code.

---

## Overview

**Purpose:** Track macro economic indicators, exchange rates, commodities
**Key Features:** Multi-series charts, dual-axis comparisons, performance tables
**Data Source:** `DATA/processed/commodity/`, `DATA/processed/macro/`

---

## Tab 0: Macro & FX

### Categories

| Category | Symbols | Unit |
|----------|---------|------|
| Lãi suất huy động | 1-3 tháng, 6-9 tháng, 13 tháng | % |
| Lãi suất liên ngân hàng | Qua đêm, 1 tuần, 2 tuần | % |
| Tỷ giá USD | Trung tâm, NHTM, Tự do, Sàn, Trần | VND |
| Trái phiếu CP | Lợi suất TPCP 5 năm | % |

### Interest Rate Groups (Multi-Series)

**Lãi suất huy động:**
| Symbol | Label | Color |
|--------|-------|-------|
| `ls_huy_dong_1_3_thang` | LS huy động 1-3 tháng | Primary |
| `ls_huy_dong_6_9_thang` | LS huy động 6-9 tháng | Secondary |
| `ls_huy_dong_13_thang` | LS huy động 13 tháng | Tertiary |

**Lãi suất liên ngân hàng:**
| Symbol | Label | Color |
|--------|-------|-------|
| `ls_qua_dem_lien_ngan_hang` | LS qua đêm liên NH | Positive |
| `ls_lien_ngan_hang_ky_han_1_tuan` | LS liên NH 1 tuần | Primary |
| `ls_lien_ngan_hang_ky_han_2_tuan` | LS liên NH 2 tuần | Secondary |

### Exchange Rate Pairs

| View | Symbol 1 | Symbol 2 |
|------|----------|----------|
| Chính thức vs Tự do | `ty_gia_usd_trung_tam` | `ty_gia_usd_tu_do_ban_ra` |
| Ngân hàng vs Tự do | `ty_gia_usd_nhtm_ban_ra` | `ty_gia_usd_tu_do_ban_ra` |
| Sàn vs Trần | `ty_gia_san` | `ty_gia_tran` |

### Spread Calculation

```
Spread = Symbol2 - Symbol1
Spread % = (Spread / Symbol1) × 100
```

---

## Tab 1: Commodities

### Dual-Axis Pairs (VN vs Global)

| Pair | Symbol 1 (VN) | Symbol 2 (Global) | Unit 1 | Unit 2 |
|------|---------------|-------------------|--------|--------|
| Vàng | `gold_vn` | `gold_global` | VND/lượng | $/oz |
| Heo hơi | `pork_vn_wichart` | `pork_china` | VND/kg | CNY/kg |
| Dầu | `oil_wti` | `oil_crude` | $/bbl | $/bbl |
| Ure DPM | `ure_vn_dpm` | `fertilizer_ure` | VND/kg | $/ton |
| Ure DCM | `ure_vn_dcm` | `fertilizer_ure` | VND/kg | $/ton |
| Thép | `steel_hrc` | `steel_d10` | $/ton | $/ton |

### Individual Commodities

| Symbol | Label |
|--------|-------|
| `gold_global` | Vàng thế giới |
| `gas_natural` | Khí thiên nhiên |
| `coke` | Than cốc |
| `steel_d10` | Thép D10 |
| `steel_hrc` | Thép HRC |
| `steel_coated` | Tôn mạ |
| `iron_ore` | Quặng sắt |
| `fertilizer_ure` | Ure (Trung Đông) |
| `soybean` | Đậu tương |
| `corn` | Ngô |
| `sugar` | Đường |
| `cao_su` | Cao su |
| `pvc` | PVC |
| `sua_bot_wmp` | Sữa bột WMP |

---

## Performance Table

### Period Changes Calculated

| Period | Days Back |
|--------|-----------|
| 1D | 1 |
| 1W | 7 |
| 1M | 30 |
| 3M | 90 |
| 6M | 180 |
| 1Y | 365 |

### Change Formula

```
change % = (current - previous) / previous × 100
```

---

## Chart Types

### Single Series (Area Fill)

- Use for individual indicator tracking
- Fill to zero with 10% opacity

### Multi-Series (Lines)

- Shared Y-axis when same unit
- Legend at top, horizontal
- Date format: %b %Y

### Dual-Axis (Comparison)

- Left Y: VN price (local unit)
- Right Y: Global price (USD/international unit)
- Different line colors for distinction

---

## Color Reference

| State | Hex | Fill (10% opacity) |
|-------|-----|---------------------|
| Primary | #8B5CF6 | rgba(139, 92, 246, 0.1) |
| Secondary | #06B6D4 | rgba(6, 182, 212, 0.1) |
| Tertiary | #F59E0B | rgba(245, 158, 11, 0.1) |
| Positive | #10B981 | rgba(16, 185, 129, 0.1) |
| Negative | #EF4444 | rgba(239, 68, 68, 0.1) |

---

## File Locations

| Component | Location |
|-----------|----------|
| Dashboard | `WEBAPP/pages/fx_commodities/fx_commodities_dashboard.py` |
| Service | `WEBAPP/services/macro_commodity_loader.py` |
| Performance Table | `WEBAPP/components/tables/performance_table.py` |
| Filter Bar | `WEBAPP/components/filters/fx_filter_bar.py` |
| Macro Data | `DATA/processed/macro/` |
| Commodity Data | `DATA/processed/commodity/` |
