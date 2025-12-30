# Brainstorm: Trend → Signal UI Flow

**Date:** 2025-12-30
**Context:** User wants UI that shows TREND first, then daily signals

---

## Current Problem

Stock Scanner shows signals without clear trend context:
- PVD: STRONG UPTREND (+8.5% SMA20, +14.9% SMA50) but recent patterns are BEARISH
- User can't quickly see: "Is this stock trending? What's the signal?"

---

## Proposed UI: Stock Trend Card

### Design Concept

```
┌──────────────────────────────────────────────────────────────────┐
│  GAS        ⬆⬆ STRONG UPTREND                           75,100đ │
│  ─────────────────────────────────────────────────────────────── │
│  SMA20: +15.1%  │  SMA50: +19.3%  │  SMA200: +18.2%             │
│  ─────────────────────────────────────────────────────────────── │
│  📊 Patterns (9 days):                                          │
│  • 23/12: doji (indecision) → NEUTRAL                           │
│  ─────────────────────────────────────────────────────────────── │
│  💡 Kết luận: UPTREND mạnh, chờ tín hiệu xác nhận               │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  MWG        ⬆ UPTREND                                   87,100đ │
│  ─────────────────────────────────────────────────────────────── │
│  SMA20: +4.0%   │  SMA50: +5.9%   │  SMA200: +23.1%             │
│  ─────────────────────────────────────────────────────────────── │
│  📊 Patterns (9 days):                                          │
│  • 25/12: evening_star (bearish) → HOLD ⚠️ counter-trend        │
│  • 24/12: hanging_man (bearish) → HOLD ⚠️ counter-trend         │
│  • 22/12: three_white_soldiers → BUY ✅ trend-aligned           │
│  ─────────────────────────────────────────────────────────────── │
│  💡 Kết luận: Đang pullback trong uptrend, caution              │
└──────────────────────────────────────────────────────────────────┘
```

---

## Signal Interpretation by Trend

### UPTREND + Pattern

| Pattern | Signal | Action | Note |
|---------|--------|--------|------|
| Bullish (hammer, morning_star, engulfing) | BUY ✅ | Mua thêm | Trend-aligned |
| Bearish (hanging_man, evening_star) | HOLD ⚠️ | Chờ | Counter-trend, có thể pullback |
| Doji | NEUTRAL | Theo dõi | Indecision |

### DOWNTREND + Pattern

| Pattern | Signal | Action | Note |
|---------|--------|--------|------|
| Bearish (shooting_star, evening_star) | SELL ✅ | Bán/Short | Trend-aligned |
| Bullish (hammer, morning_star) | HOLD ⚠️ | Chờ | Counter-trend, risky reversal |
| Doji | NEUTRAL | Theo dõi | Indecision |

### SIDEWAYS + Pattern

| Pattern | Signal | Action | Note |
|---------|--------|--------|------|
| Bullish | BUY | Mua nhẹ | Follow pattern |
| Bearish | SELL | Bán nhẹ | Follow pattern |
| Doji | NEUTRAL | Range-bound | |

---

## UI Options

### Option A: Split Tables (Current)
```
┌─────────────────────┐  ┌─────────────────────┐
│ TÍN HIỆU MUA   [25] │  │ TÍN HIỆU BÁN   [18] │
├─────────────────────┤  ├─────────────────────┤
│ Mã   │ Pattern │ Đ  │  │ Mã   │ Pattern │ Đ  │
├─────────────────────┤  ├─────────────────────┤
│ MWG  │ 3ws     │100 │  │ VIC  │ evening │ 80 │
└─────────────────────┘  └─────────────────────┘
```

### Option B: Trend-First Cards (NEW)
```
┌────────────────────────────────────────────┐
│ ⬆⬆ STRONG UPTREND (5 stocks)              │
├────────────────────────────────────────────┤
│ GAS  +15% │ PVD  +8%  │ PVS  +8%          │
│ HDB  +8%  │ MWG  +4%  │                    │
├────────────────────────────────────────────┤
│ Actionable: MWG 22/12 three_white → BUY   │
│            PVS 26/12 engulfing → BUY      │
└────────────────────────────────────────────┘

┌────────────────────────────────────────────┐
│ ⬇⬇ STRONG DOWNTREND (8 stocks)            │
├────────────────────────────────────────────┤
│ ABC  -12% │ DEF  -8%  │ GHI  -7%          │
├────────────────────────────────────────────┤
│ Actionable: ABC 29/12 evening_star → SELL │
└────────────────────────────────────────────┘
```

### Option C: Hybrid (Trend Filter + Split Tables)
```
┌─────────────────────────────────────────────────┐
│ 🔍 Filter by Trend:                             │
│ [All] [⬆⬆ Strong Up] [⬆ Up] [↔ Sideways] [⬇]  │
└─────────────────────────────────────────────────┘

┌─────────────────────┐  ┌─────────────────────┐
│ TÍN HIỆU MUA   [12] │  │ TÍN HIỆU BÁN    [5] │
│ (Only UPTREND)      │  │ (Only DOWNTREND)    │
├─────────────────────┤  ├─────────────────────┤
│ Mã   │Trend│Pattern │  │ Mã   │Trend│Pattern│
│ MWG  │⬆    │ 3ws    │  │ ABC  │⬇⬇  │evening│
└─────────────────────┘  └─────────────────────┘
```

---

## Recommendation

**Option C (Hybrid)** is best because:
1. Trend filter at top → User picks trend direction first
2. Split tables → Clear MUA/BÁN separation
3. Show trend badge on each row → Context visible
4. Only show aligned signals by default

---

## Implementation Changes

### 1. Add Trend Filter UI
```python
# In stock_scanner.py, add trend filter
trend_options = ['Tất cả', 'UPTREND', 'DOWNTREND', 'SIDEWAYS']
selected_trend = st.selectbox("Xu hướng", trend_options)
```

### 2. Add Trend Column to Table
```python
# In _render_signal_table_compact(), add trend badge
trend_badge = {
    'UPTREND': '⬆',
    'STRONG UP': '⬆⬆',
    'DOWNTREND': '⬇',
    'STRONG DOWN': '⬇⬇',
    'SIDEWAYS': '↔'
}
```

### 3. Update Filter Logic
```python
# Filter by trend
if selected_trend != 'Tất cả':
    if selected_trend == 'UPTREND':
        filtered = filtered[filtered['trend'].isin(['UPTREND', 'STRONG UP'])]
    elif selected_trend == 'DOWNTREND':
        filtered = filtered[filtered['trend'].isin(['DOWNTREND', 'STRONG DOWN'])]
```

---

---

## Feature: Single Stock Analysis (PVD Example)

### Use Case
User enters "PVD" → See full trend + signal analysis

### UI Mockup

```
┌──────────────────────────────────────────────────────────────────────┐
│  🔍 Nhập mã: [PVD____]  [Phân tích]                                  │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│  PVD - TỔNG CÔNG TY KHOAN & DỊCH VỤ KHOAN DẦU KHÍ                    │
│  Giá: 28,500đ  │  Thay đổi: +2.5%                                    │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  📈 XU HƯỚNG: STRONG UPTREND ⬆⬆                                      │
│  ───────────────────────────────────────────────────────────────     │
│  • SMA20:  +8.5% (above)                                             │
│  • SMA50:  +14.9% (above)                                            │
│  • SMA200: +31.9% (above)                                            │
│  • MACD:   Positive histogram                                        │
│                                                                      │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  🕯️ TÍN HIỆU GẦN ĐÂY (9 ngày):                                       │
│  ───────────────────────────────────────────────────────────────     │
│  23/12 │ engulfing   │ BEARISH │ Score 80 │ ⚠️ HOLD (counter-trend)  │
│  22/12 │ hanging_man │ BEARISH │ Score 100│ ⚠️ HOLD (counter-trend)  │
│                                                                      │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  💡 PHÂN TÍCH:                                                       │
│  ───────────────────────────────────────────────────────────────     │
│  ✅ Trend: STRONG UPTREND - Xu hướng tăng mạnh                       │
│  ⚠️ Signal: Bearish patterns gần đây (hanging_man, engulfing)        │
│  📊 Kết luận: ĐANG PULLBACK trong uptrend                            │
│                                                                      │
│  🎯 CHIẾN LƯỢC:                                                      │
│  • Nếu đang hold: GIỮ - Pullback bình thường                         │
│  • Nếu muốn mua: CHỜ - Đợi bullish reversal pattern xuất hiện       │
│  • Support gần: SMA20 (26,200đ) - Mua khi test support              │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Feature: Pullback Strategy

### Logic

```
UPTREND + Bearish Pattern = PULLBACK (not reversal)
Action: HOLD existing, WAIT to buy more at support

DOWNTREND + Bullish Pattern = BOUNCE (not reversal)
Action: HOLD shorts, WAIT to sell more at resistance
```

### Signal Classification

| Trend | Pattern | Signal | Strategy |
|-------|---------|--------|----------|
| STRONG UP | Bullish | **BUY** | Mua thêm, continuation |
| STRONG UP | Bearish | **PULLBACK** | Hold, chờ test support |
| UPTREND | Bullish | **BUY** | Mua, trend following |
| UPTREND | Bearish | **PULLBACK** | Hold, set stop loss |
| SIDEWAYS | Any | **RANGE** | Trade range, buy low sell high |
| DOWNTREND | Bearish | **SELL** | Bán, trend following |
| DOWNTREND | Bullish | **BOUNCE** | Hold shorts, wait resistance |
| STRONG DOWN | Bearish | **SELL** | Bán/Short, continuation |
| STRONG DOWN | Bullish | **BOUNCE** | Avoid buying |

### Implementation

```python
def get_strategy_signal(trend: str, pattern_signal: str) -> dict:
    """Get pullback strategy signal."""

    if trend in ['STRONG UP', 'UPTREND']:
        if pattern_signal == 'BULLISH':
            return {
                'action': 'BUY',
                'label': 'MUA',
                'color': '#10B981',
                'note': 'Trend continuation'
            }
        elif pattern_signal == 'BEARISH':
            return {
                'action': 'PULLBACK',
                'label': 'PULLBACK',
                'color': '#F59E0B',  # Orange/warning
                'note': 'Hold, wait for support'
            }

    elif trend in ['STRONG DOWN', 'DOWNTREND']:
        if pattern_signal == 'BEARISH':
            return {
                'action': 'SELL',
                'label': 'BÁN',
                'color': '#EF4444',
                'note': 'Trend continuation'
            }
        elif pattern_signal == 'BULLISH':
            return {
                'action': 'BOUNCE',
                'label': 'BOUNCE',
                'color': '#F59E0B',
                'note': 'Hold shorts, wait resistance'
            }

    else:  # SIDEWAYS
        if pattern_signal == 'BULLISH':
            return {
                'action': 'BUY_RANGE',
                'label': 'MUA NHẸ',
                'color': '#06B6D4',
                'note': 'Range trading'
            }
        elif pattern_signal == 'BEARISH':
            return {
                'action': 'SELL_RANGE',
                'label': 'BÁN NHẸ',
                'color': '#8B5CF6',
                'note': 'Range trading'
            }

    return {
        'action': 'NEUTRAL',
        'label': 'THEO DÕI',
        'color': '#64748B',
        'note': 'No signal'
    }
```

---

## Updated Direction Labels

| Old | New | Color | Meaning |
|-----|-----|-------|---------|
| BUY | MUA | Green | Strong buy signal |
| SELL | BÁN | Red | Strong sell signal |
| HOLD | PULLBACK/BOUNCE | Orange | Counter-trend, wait |
| NEUTRAL | THEO DÕI | Gray | No clear signal |

---

## Next Steps

1. [ ] Nới lỏng threshold: ±2% → ±5% cho SIDEWAYS rộng hơn
2. [ ] Add trend column to signals data
3. [ ] Add trend filter to UI
4. [ ] Add trend badge to table rows
5. [ ] Implement single stock analysis component
6. [ ] Implement pullback strategy logic
7. [ ] Update direction labels (HOLD → PULLBACK/BOUNCE)
