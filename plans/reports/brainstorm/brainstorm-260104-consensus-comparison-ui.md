# Brainstorm: BSC vs Consensus Comparison UI

**Created:** 2026-01-03
**Updated:** 2026-01-04
**Status:** ✅ Implemented

---

## Problem Statement

- BSC: 92 stocks with TP, NPATMI 2025F, NPATMI 2026F
- Consensus: 234 records (115 unique) from HCM (92), SSI (58), VCI (84)
- Overlap: 75 stocks covered by both BSC and ≥1 consensus source
- Need: See individual company views side-by-side, focus on **NPATMI 2026F**

---

## Final Design: 2 Sub-tabs

### Structure

```
┌──────────────────────────────────────────────────────┐
│  [📊 Summary Table]  [🔍 Ticker Lookup]              │
└──────────────────────────────────────────────────────┘
```

### User Decisions ✅

1. **Summary table**: Giữ 1 cột BSC TP, focus vào NPATMI 2026F
2. **Sorting default**: Sort theo Deviation (NPATMI) - absolute value
3. **Ticker lookup**: Text input (không autocomplete)
4. **Format số**: 15.2T (nghìn tỷ)

---

## Sub-tab 1: Summary Table (NPATMI 2026F Focus)

```
┌────────┬────────┬────────┬────────┬────────┬────────┬──────────┬──────────┬─────────┐
│ TICKER │ BSC TP │  BSC   │  HCM   │  SSI   │  VCI   │CONSENSUS │BSC vs    │ INSIGHT │
│        │        │ 2026F  │ 2026F  │ 2026F  │ 2026F  │  MEAN    │CONS      │         │
├────────┼────────┼────────┼────────┼────────┼────────┼──────────┼──────────┼─────────┤
│ ACB    │ 28,400 │ 15.2T  │ 14.8T  │ 15.5T  │ 14.9T  │  15.1T   │  +0.7%   │ Aligned │
│ VCB    │ 73,200 │ 28.5T  │ 32.0T  │   —    │ 30.5T  │  31.3T   │  -8.8%   │ Bearish │
│ FPT    │109,800 │ 8.2T   │ 7.5T   │ 7.8T   │ 7.6T   │   7.6T   │  +7.4%   │ Bullish │
└────────┴────────┴────────┴────────┴────────┴────────┴──────────┴──────────┴─────────┘
```

**Features:**
- Row color tint based on deviation (green=bullish, red=bearish, none=aligned)
- Deviation bar visual
- Filters: Sector, Min Sources, Insight
- Sort: By absolute deviation (highest first)

---

## Sub-tab 2: Ticker Lookup

```
🔍 Enter ticker: [ACB______] [Search]

═══════════════════════════════════════════════════════
ACB - Ngân hàng TMCP Á Châu          Current: 25,400

┌──────────────┬────────┬────────┬────────┬────────┬──────────┐
│    METRIC    │  BSC   │  HCM   │  SSI   │  VCI   │CONSENSUS │
├──────────────┼────────┼────────┼────────┼────────┼──────────┤
│ Target Price │ 28,400 │ 32,300 │ 30,200 │ 29,800 │  30,767  │
│              │        │ +13.7% │  +6.3% │  +4.9% │   +8.3%  │
├──────────────┼────────┼────────┼────────┼────────┼──────────┤
│ NPATMI 2025F │ 14.2T  │ 13.8T  │ 14.5T  │ 13.5T  │  13.9T   │
│              │        │  -2.8% │  +2.1% │  -4.9% │   -1.9%  │
├──────────────┼────────┼────────┼────────┼────────┼──────────┤
│ NPATMI 2026F │ 15.2T  │ 14.8T  │ 15.5T  │ 14.9T  │  15.1T   │
│              │        │  -2.6% │  +2.0% │  -2.0% │   -0.9%  │
└──────────────┴────────┴────────┴────────┴────────┴──────────┘

VISUAL RANGE:
Target Price    V ── H ─── S ────── B
                29.8K      30.2K    32.3K

NPATMI 2026F    V ── H ──────────── B ── S
                14.8T              15.2T 15.5T

┌─────────────────────────────────────────────────────────┐
│ ● Aligned                                               │
│ BSC và consensus gần nhau (-0.9%) cho NPATMI 2026F     │
└─────────────────────────────────────────────────────────┘
```

---

## Color Scheme (Dark Mode)

```
Background:     #0F172A (Slate 900)
Card BG:        #1E293B (Slate 800)
Border:         #334155 (Slate 700)
Text Primary:   #F8FAFC (Slate 50)
Text Secondary: #94A3B8 (Slate 400)
Brand Teal:     #00C9AD

Source Colors:
- BSC:  #3B82F6 (Blue)
- HCM:  #22C55E (Green)
- SSI:  #F59E0B (Amber)
- VCI:  #EF4444 (Red)

Deviation Colors:
- BSC Higher:   #22C55E (Green) - BSC bullish
- BSC Lower:    #EF4444 (Red) - BSC bearish
- Aligned:      #94A3B8 (Gray) - ±5%
```

---

## Insight Logic

**Nguyên tắc:** BSC so với Consensus (không phải Consensus so với BSC)

```python
# dev_pct = (Consensus - BSC) / BSC
# - Positive = Consensus > BSC = BSC bảo thủ (bearish)
# - Negative = Consensus < BSC = BSC lạc quan (bullish)

def get_insight(dev_pct):
    if dev_pct <= -15:
        return "strong_bullish"   # ▲▲ BSC >> Consensus (BSC lạc quan)
    elif dev_pct <= -5:
        return "bullish_gap"      # ▲ BSC > Consensus
    elif dev_pct >= 15:
        return "strong_bearish"   # ▼▼ BSC << Consensus (BSC bảo thủ)
    elif dev_pct >= 5:
        return "bearish_gap"      # ▼ BSC < Consensus
    else:
        return "aligned"          # ● Within ±5%
```

---

## Implementation Files

1. **Data:** `DATA/processed/forecast/comparison/bsc_vs_consensus.parquet`
2. **Processor:** `PROCESSORS/forecast/create_comparison_table.py`
3. **Styles:** `WEBAPP/components/styles/comparison_styles.py`
4. **Tab:** `WEBAPP/pages/forecast/tabs/bsc_vs_consensus_tab.py`

---

## Number Format Function

```python
def format_npatmi_t(val) -> str:
    """Format NPATMI in nghìn tỷ (T)."""
    if pd.isna(val) or val == 0:
        return '—'
    t_val = val / 1000  # Convert to nghìn tỷ
    if t_val >= 10:
        return f"{t_val:.1f}T"  # 15.2T
    elif t_val >= 1:
        return f"{t_val:.2f}T"  # 1.23T
    else:
        return f"{val:.0f}B"    # 500B (dưới 1T)
```

---

## Archive

See original brainstorm files for detailed exploration of alternatives:
- Option A: Wide Table
- Option B: Grouped Metrics Tabs
- Option C: Expandable Rows (partially used)
- Option D: Card View

Previous implementation (emoji markers + expandable rows) archived at:
`WEBAPP/pages/forecast/tabs/archive_consensus_tab.py`
