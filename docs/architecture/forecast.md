# Forecast Module Architecture

Guide for modifying forecast data, logic, and UI.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 1: SOURCE DATA (Manual Editing)                         │
│  Location: DATA/processed/forecast/sources/                    │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 2: BUILD LOGIC (Insight Rules, Calculations)            │
│  Location: PROCESSORS/forecast/unified/                        │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 3: UI/UX (Display, Formatting, Colors)                  │
│  Location: WEBAPP/pages/forecast/ + WEBAPP/components/styles/  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Layer 1: Source Data

**Purpose:** Raw forecast data from 4 sources. Edit directly to update forecasts.

**Unit:** Tỷ VND (billion VND) for all NPATMI values.

### Year Mapping Rules

**CRITICAL: Do NOT shift years. Keep original year labels from each source.**

| Source | 2026F Available | 2027F Available | Notes |
|--------|-----------------|-----------------|-------|
| BSC | ✅ Yes | ❌ No | Excel only has 2025F/2026F, no 2027F yet |
| VCI | ✅ Yes | ✅ Yes | API provides both 2026F and 2027F |
| HCM | Varies | Varies | Check PDF extraction |
| SSI | Varies | Varies | Check PDF extraction |

**Rule:** When a source doesn't have data for a year, set it to `null` (not shifted from another year).

| File | Source | Edit For |
|------|--------|----------|
| `DATA/processed/forecast/sources/bsc.json` | BSC Research | BSC target prices, NPATMI, ratings |
| `DATA/processed/forecast/sources/vci.json` | Vietcap API | VCI forecasts |
| `DATA/processed/forecast/sources/hcm.json` | HCM Securities | HCM extracted data |
| `DATA/processed/forecast/sources/ssi.json` | SSI Securities | SSI extracted data |

**JSON Schema:**
```
{
  "source": "bsc",
  "updated_at": "04/01/26",
  "schema_version": "2026-2027",
  "stocks": [
    {
      "symbol": "ACB",
      "sector": "Ngân hàng",
      "entity_type": "BANK",
      "target_price": 32000,
      "npatmi_2026f": 18500,    ← Tỷ VND
      "npatmi_2027f": 21000,    ← Tỷ VND
      "eps_2026f": 3200,
      "eps_2027f": 3650,
      "pe_2026f": 8.4,
      "pe_2027f": 7.4,
      "rating": "MUA"
    }
  ]
}
```

---

## Layer 2: Build Logic

**Purpose:** Calculate comparison metrics and assign insight categories.

| File | Purpose |
|------|---------|
| `PROCESSORS/forecast/unified/build_unified.py` | Main builder - insight rules, deviation calculations |
| `PROCESSORS/forecast/unified/init_source_jsons.py` | One-time migration from old parquets |

### Insight Thresholds (build_unified.py ~line 196-216)

| Insight | Condition | Meaning |
|---------|-----------|---------|
| `strong_bullish` | dev <= -15% | BSC much higher than consensus |
| `bullish_gap` | -15% < dev <= -5% | BSC moderately higher |
| `aligned` | -5% < dev < 5% | BSC ≈ consensus |
| `bearish_gap` | 5% <= dev < 15% | BSC moderately lower |
| `strong_bearish` | dev >= 15% | BSC much lower than consensus |
| `high_variance` | spread > 30% | Sources disagree significantly |
| `no_data` | No consensus data | Only BSC available |

**Deviation Formula:**
```
dev = (consensus_mean - bsc_value) / bsc_value × 100%
```
- Negative dev = BSC higher (bullish for BSC)
- Positive dev = BSC lower (bearish for BSC)

### Rebuild Command

After editing source JSONs or logic:
```bash
python3 PROCESSORS/forecast/unified/build_unified.py
```

---

## Layer 3: UI/UX

**Purpose:** Display formatting, colors, icons, table layout.

| File | Purpose |
|------|---------|
| `WEBAPP/pages/forecast/tabs/bsc_vs_consensus_tab.py` | Main comparison tab (Summary Table, Ticker Lookup) |
| `WEBAPP/components/styles/comparison_styles.py` | Colors, icons, badges, CSS styles |

### Insight Configuration (comparison_styles.py)

| Config | What to Edit |
|--------|--------------|
| `INSIGHT_CONFIG` | Colors, icons, labels for each insight type |
| `SOURCE_MARKERS` | Colors for BSC, VCI, HCM, SSI markers |
| `COLORS` | Theme colors (background, text, accents) |

### Formatting Functions (bsc_vs_consensus_tab.py)

| Function | Purpose |
|----------|---------|
| `format_npatmi_t()` | Format NPATMI values (B/T units) |
| `format_price()` | Format price values |
| `format_deviation()` | Format deviation with color coding |

---

## Data Flow

```
1. Edit JSON     →  2. Run build_unified.py  →  3. Streamlit reads unified.parquet
   (sources/)           (PROCESSORS/)               (WEBAPP/)
```

---

## Quick Reference

### Add/Update Stock Forecast
1. Edit `DATA/processed/forecast/sources/{source}.json`
2. Run `python3 PROCESSORS/forecast/unified/build_unified.py`

### Change Insight Thresholds
1. Edit `PROCESSORS/forecast/unified/build_unified.py` (line ~196-216)
2. Rebuild unified.parquet

### Change Colors/Icons
1. Edit `WEBAPP/components/styles/comparison_styles.py`
2. No rebuild needed (UI only)

### Change Table Layout
1. Edit `WEBAPP/pages/forecast/tabs/bsc_vs_consensus_tab.py`
2. No rebuild needed (UI only)

---

## Output Files

| File | Used By | Content |
|------|---------|---------|
| `DATA/processed/forecast/unified.parquet` | BSC vs Consensus tab | All comparison data |
| `DATA/processed/forecast/bsc/bsc_individual.parquet` | BSC Universal tab | BSC stock forecasts |
| `DATA/processed/forecast/bsc/bsc_sector_valuation.parquet` | Sector tab | Sector-level data |
