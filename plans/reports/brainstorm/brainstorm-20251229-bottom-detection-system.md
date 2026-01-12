# Brainstorm: Bottom Detection System

**Date:** 2025-12-29
**Status:** ✅ Implemented
**Topic:** Market bottom detection & trend reversal signals

---

## Problem Statement

Current Signal Matrix lacks detection for:
1. Market bottom formation during extreme oversold conditions
2. Early reversal signals when all breadth indicators are at bottom and starting to rise
3. Vietnam market has fast turnover rate → need early signals

---

## Decisions

| Item | Decision |
|------|----------|
| **New Signals** | 2 signals: `ACCUMULATING`, `EARLY_BUY` |
| **Indicator** | Separate "Bottom Formation Stage" indicator |
| **Confirmation period** | 5 sessions |

---

## Design: Signal Matrix v2

### New Signals

```python
'ACCUMULATING': {
    'label': 'ACCUMULATING',
    'subtitle': 'Smart Money Entering',
    'action': 'Theo dõi sát. Smart money đang tích lũy.',
    'color': '#6366F1',  # Indigo
    'bg': 'rgba(99, 102, 241, 0.15)',
},
'EARLY_BUY': {
    'label': 'EARLY BUY',
    'subtitle': 'Early Reversal',
    'action': 'Test mua 10-20%. Stop-loss chặt dưới đáy.',
    'color': '#22D3EE',  # Cyan
    'bg': 'rgba(34, 211, 238, 0.15)',
},
```

### Updated Signal Logic

```
UPTREND (MA50 >= 50 AND MA100 >= 50):
├── MA20 < 20      → STRONG_BUY
├── MA20 < 40      → BUY
├── MA20 > 80      → WARNING
└── else           → HOLD

DOWNTREND/SIDEWAYS:
├── MA20 > 70                        → SELL
├── MA50 < 30 AND MA20 < 20          → DANGER
├── ALL MAs < 30 AND MA20 rising 5d  → ACCUMULATING ⭐
├── MA20 >= 25 AND rising 5d         → EARLY_BUY ⭐
│   AND MA50 starting to rise
└── else                             → WAIT
```

---

## Design: Bottom Formation Stage Indicator

### Stages

| Stage | Condition | Display |
|-------|-----------|---------|
| CAPITULATION | ALL MAs < 25, not rising | "Capitulation - Extreme Fear" (Dark Red) |
| ACCUMULATING | ALL MAs < 30, MA20 rising 5d | "Accumulating - Smart Money Entering" (Indigo) |
| EARLY_REVERSAL | MA20 >= 25, rising 5d, MA50 flattening | "Early Reversal - Trend Changing" (Cyan) |
| CONFIRMED | MA50 >= 50, entering uptrend | Hidden (normal signals take over) |

### UI Layout

```
┌─────────────────────────────────────────────────────┐
│  🔄 BOTTOM STAGE: ACCUMULATING                      │
│  ━━━━━━━━━━━━━━━○───────────                        │
│  CAPIT.  ACCUM.  EARLY   CONFIRMED                  │
│                                                      │
│  MA20 rising: 5/5 days ✓                            │
│  MA50 trend: Flattening                             │
└─────────────────────────────────────────────────────┘
```

---

## Data Requirements

### MarketState additions

```python
prev_breadth_ma50_pct: Optional[float] = None
ma20_rising_days: int = 0
ma50_rising_days: int = 0
bottom_stage: Optional[str] = None
```

---

## Implementation Files

| File | Changes |
|------|---------|
| `WEBAPP/core/models/market_state.py` | Add new fields |
| `WEBAPP/pages/technical/services/ta_dashboard_service.py` | Calculate rising days, bottom stage |
| `WEBAPP/pages/technical/components/market_overview.py` | Add signals, add bottom indicator UI |

---

## Detection Logic

```python
def detect_bottom_stage(state, history_5d):
    ma20 = state.breadth_ma20_pct
    ma50 = state.breadth_ma50_pct
    ma100 = state.breadth_ma100_pct

    ma20_rising = count_rising_days(history_5d, 'ma20')
    ma50_rising = count_rising_days(history_5d, 'ma50')

    all_oversold = ma20 < 30 and ma50 < 30 and ma100 < 30
    extreme_oversold = ma20 < 25 and ma50 < 25 and ma100 < 25

    if extreme_oversold and ma20_rising < 2:
        return 'CAPITULATION'

    if all_oversold and ma20_rising >= 5:
        return 'ACCUMULATING'

    if ma20 >= 25 and ma20_rising >= 5 and ma50_rising >= 2:
        return 'EARLY_REVERSAL'

    return None
```

---

## Next Steps

1. Update MarketState model with new fields
2. Update TADashboardService to calculate rising days and bottom stage
3. Add new signals to SIGNAL_MATRIX constant
4. Update signal detection logic in _render_breadth_gauges()
5. Add Bottom Formation Stage indicator UI component
6. Test with historical data

---

## Success Criteria

1. ACCUMULATING signal triggers when all MAs < 30 and MA20 rising for 5 days
2. EARLY_BUY signal triggers when MA20 >= 25, rising 5d, MA50 starting to rise
3. Bottom Formation Stage indicator shows progression visually
4. No false positives during normal downtrend (not at bottom)
