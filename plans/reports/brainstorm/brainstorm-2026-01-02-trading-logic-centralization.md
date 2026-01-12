# Brainstorm: Trading Logic Centralization

**Date:** 2026-01-02
**Scope:** Technical Dashboard + Forecast Dashboard
**Status:** Ready for implementation

---

## Problem Statement

Magic numbers và business logic đang phân tán trong UI components:
- Khó maintain khi cần tune parameters
- Khó migrate sang HTML/React sau này
- Không có single source of truth

---

## Current State Analysis

### Already Centralized (WEBAPP/core/)
| File | Content |
|------|---------|
| `constants.py` | Valuation thresholds (PE/PB outliers) |
| `styles.py` | Colors, typography, glassmorphism |
| `theme.py` | Dark theme, trading colors |

### Needs Extraction

#### Technical Dashboard (Priority 1)
| Constant | Location | Description |
|----------|----------|-------------|
| `MARKET_SCORE_WEIGHTS` | market_overview.py:52 | MA50=50%, MA20=30%, MA100=20% |
| `SIGNAL_MATRIX` | market_overview.py:59 | 8 signal types with actions |
| `BOTTOM_STAGES` | market_overview.py:127 | 3 stages for bottom detection |
| `MA20_WINDOW` | ta_dashboard_service.py:526 | 7 days (from backtest) |
| `MA50_WINDOW` | ta_dashboard_service.py:527 | 9 days (from backtest) |
| `OVERBOUGHT_THRESHOLD` | inline | 80% |
| `OVERSOLD_THRESHOLD` | inline | 20% |
| `PATTERN_VOLUME_MATRIX` | stock_scanner.py:128 | Pattern interpretations |
| `QUADRANT_COLORS` | sector_rotation.py:31 | RRG quadrant colors |

#### Forecast Dashboard (Priority 2)
| Constant | Location | Description |
|----------|----------|-------------|
| `RATING_COLORS` | forecast_dashboard.py:35 | BUY/HOLD/SELL colors |
| `ACHIEVEMENT_THRESHOLDS` | achievement_tab.py:30 | 85%, 65% thresholds |

---

## Proposed Solution

### File Structure
```
WEBAPP/core/
├── constants.py              # ✅ Existing (valuation)
├── styles.py                 # ✅ Existing (colors/theme)
│
├── trading_constants.py      # 🆕 Technical thresholds + windows
└── trading_rules.py          # 🆕 Signal matrix + state machines
```

### trading_constants.py (Draft)
```python
"""
Trading Constants - Single Source of Truth
==========================================
Backtest Period: 2023-2025 (3 years, 699 trading days)
Strategy: Swing Trading 4-8 weeks
"""

# =============================================================================
# BREADTH THRESHOLDS
# =============================================================================
OVERBOUGHT_THRESHOLD = 80  # % stocks above MA
OVERSOLD_THRESHOLD = 20
TREND_CONFIRMATION_THRESHOLD = 50  # MA50 >= 50 AND MA100 >= 50

# =============================================================================
# SWING DETECTION WINDOWS (Optimized from 3-year backtest)
# =============================================================================
MA20_HIGHER_LOW_WINDOW = 7   # Median cycle 14.5d / 2
MA50_HIGHER_LOW_WINDOW = 9   # Median cycle 19.0d / 2

# =============================================================================
# MARKET SCORE WEIGHTS (Swing Trading Strategy)
# =============================================================================
MARKET_SCORE_WEIGHTS = {
    'ma50': 0.5,   # Trend backbone (50%)
    'ma20': 0.3,   # Timing/Trigger (30%)
    'ma100': 0.2,  # Safety filter (20%)
}

# =============================================================================
# BOTTOM DETECTION THRESHOLDS
# =============================================================================
CAPITULATION_THRESHOLD = 25   # All MAs < 25%
ACCUMULATION_THRESHOLD = 30   # All MAs < 30%
```

### trading_rules.py (Draft)
```python
"""
Trading Rules - Signal Matrix & State Machines
==============================================
"""
from .trading_constants import *

SIGNAL_MATRIX = {
    'STRONG_BUY': {
        'condition': 'Uptrend + MA20 < 20%',
        'action': 'Giải ngân mạnh. Rũ bỏ hoàn hảo.',
        'color': '#059669',
    },
    'BUY': {
        'condition': 'Uptrend + MA20 < 40%',
        'action': 'Mua gia tăng hoặc mở vị thế mới.',
        'color': '#10B981',
    },
    # ... etc
}
```

---

## Implementation Plan

### Phase 1: Extract Technical Dashboard Constants (~2h)
1. Create `WEBAPP/core/trading_constants.py`
2. Create `WEBAPP/core/trading_rules.py`
3. Migrate constants from `market_overview.py`
4. Migrate constants from `ta_dashboard_service.py`
5. Update imports in components

### Phase 2: Extract Stock Scanner Constants (~1h)
1. Move `PATTERN_VOLUME_MATRIX` to trading_rules.py
2. Move `TREND_COLORS`, `ACTION_COLORS` to trading_rules.py
3. Update imports

### Phase 3: Extract Forecast Dashboard Constants (~1h)
1. Add forecast thresholds to constants
2. Move `RATING_COLORS` to appropriate file
3. Update imports

### Phase 4: Documentation (~30min)
1. Update `docs/TRADING_LOGIC.md` with all constants
2. Add rationale for each threshold

---

## Decision Log

| Question | Decision | Rationale |
|----------|----------|-----------|
| Config format | Python-only | Solo developer, no need YAML |
| Doc format | Manual + docstrings | Hybrid approach |
| Scope | Technical + Forecast first | Highest complexity |
| Location | WEBAPP/core/ | Existing pattern |

---

## Next Steps

1. ✅ User confirms approach
2. Create implementation plan file
3. Execute Phase 1 (Technical)
4. Execute Phase 3 (Forecast)
5. Test all dashboards
6. Update documentation

---

## Unresolved Questions

None - ready for implementation.
