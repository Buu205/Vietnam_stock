# Phase 2: Sector Layer Implementation

**Goal:** Identify leading/lagging sectors for rotation strategy
**Updated:** 2025-12-25 (Simplified IBD-style ranking)

---

## Design Philosophy

| Purpose | Method | Rationale |
|---------|--------|-----------|
| **Ranking** | IBD-style (Returns) | Money flows to winners. Returns = objective measure |
| **Validation** | Breadth Filter | Flag "weak internal" sectors (top rank but low participation) |
| **Visualization** | Mansfield RS | Visual trend vs VN-Index |

**Key Change:** Removed complex TA+Volume weighted formula. Returns-based ranking is simpler, more transparent, less prone to overfitting.

---

## 1. Sector Ranking (IBD-style Returns)

### Formula

```python
# Simple, transparent, VN market optimized (fast rotation T+10, T+20)
Sector_Score = (0.5 × Return_1M) + (0.3 × Return_3M) + (0.2 × Return_1W)
```

### Weight Rationale

| Period | Weight | Reason |
|--------|--------|--------|
| 1 Week | 20% | Capture very recent momentum |
| 1 Month | 50% | Primary signal (VN rotation ~T+20) |
| 3 Month | 30% | Medium-term trend confirmation |

### Implementation

```python
import pandas as pd
import numpy as np

def calculate_sector_returns(ohlcv_df: pd.DataFrame, sector_map: dict) -> pd.DataFrame:
    """
    Calculate sector returns for different periods

    Args:
        ohlcv_df: OHLCV data with 'symbol', 'date', 'close'
        sector_map: Dict mapping symbol -> sector_code

    Returns:
        DataFrame with [date, sector_code, ret_1w, ret_1m, ret_3m]
    """
    df = ohlcv_df.copy()
    df['sector_code'] = df['symbol'].map(sector_map)

    # Calculate individual stock returns
    df = df.sort_values(['symbol', 'date'])
    df['ret_1w'] = df.groupby('symbol')['close'].pct_change(5) * 100   # 5 trading days
    df['ret_1m'] = df.groupby('symbol')['close'].pct_change(21) * 100  # 21 trading days
    df['ret_3m'] = df.groupby('symbol')['close'].pct_change(63) * 100  # 63 trading days

    # Aggregate to sector level (equal-weighted average)
    sector_returns = df.groupby(['date', 'sector_code']).agg({
        'ret_1w': 'mean',
        'ret_1m': 'mean',
        'ret_3m': 'mean'
    }).reset_index()

    return sector_returns


def calculate_sector_score(sector_returns_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate IBD-style sector score from returns

    Formula: Score = 0.5×ret_1m + 0.3×ret_3m + 0.2×ret_1w

    Returns:
        DataFrame with [date, sector_code, score, rank, action]
    """
    df = sector_returns_df.copy()

    # IBD-style weighted score
    df['score'] = (
        0.5 * df['ret_1m'] +
        0.3 * df['ret_3m'] +
        0.2 * df['ret_1w']
    )

    # Rank within each date (1 = best)
    df['rank'] = df.groupby('date')['score'].rank(ascending=False).astype(int)

    # Action based on rank
    df['action'] = df['rank'].apply(
        lambda x: 'OVERWEIGHT' if x <= 5 else ('NEUTRAL' if x <= 12 else 'UNDERWEIGHT')
    )

    return df[['date', 'sector_code', 'ret_1w', 'ret_1m', 'ret_3m', 'score', 'rank', 'action']]
```

---

## 2. Breadth Validation (Filter, NOT Score Component)

### Purpose
Flag sectors with "weak internal" strength - high rank but low participation.

### Logic

```python
def validate_sector_breadth(
    sector_scores_df: pd.DataFrame,
    sector_breadth_df: pd.DataFrame,
    market_breadth_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Add breadth validation to sector ranking

    Rule: If Sector Breadth (% > MA50) < Market Breadth → "WEAK_INTERNAL"

    Returns:
        DataFrame with added 'breadth_status' column
    """
    df = sector_scores_df.merge(
        sector_breadth_df[['date', 'sector_code', 'pct_above_ma50']],
        on=['date', 'sector_code'],
        how='left'
    )

    # Get market breadth for comparison
    df = df.merge(
        market_breadth_df[['date', 'above_ma50_pct']].rename(
            columns={'above_ma50_pct': 'market_breadth'}
        ),
        on='date',
        how='left'
    )

    # Validation: sector breadth vs market breadth
    df['breadth_status'] = np.where(
        df['pct_above_ma50'] < df['market_breadth'],
        'WEAK_INTERNAL',  # Top rank but participation below market avg
        'VALID'
    )

    # Warning for top-ranked sectors with weak breadth
    df['warning'] = np.where(
        (df['rank'] <= 5) & (df['breadth_status'] == 'WEAK_INTERNAL'),
        '⚠️ Kéo trụ - Nội lực yếu',
        ''
    )

    return df
```

### Interpretation Table

| Rank | Breadth Status | Interpretation |
|------|----------------|----------------|
| Top 5 | VALID | ✅ Strong sector, safe to overweight |
| Top 5 | WEAK_INTERNAL | ⚠️ "Kéo trụ" - few stocks driving gains |
| 6-12 | VALID | Hold, normal conditions |
| 6-12 | WEAK_INTERNAL | Caution, narrow participation |
| 13-19 | Any | Underweight/Avoid |

---

## 3. Mansfield RS (Visualization Only)

### Purpose
Visual chart showing sector trend vs VN-Index (not for ranking).

### Formula

```python
def calculate_mansfield_rs(
    sector_prices_df: pd.DataFrame,
    vnindex_df: pd.DataFrame,
    sma_period: int = 52  # weeks (or 260 days)
) -> pd.DataFrame:
    """
    Calculate Mansfield Relative Strength for charting

    Formula:
    1. RS_Ratio = Sector_Price / VNIndex_Price
    2. RS_SMA = SMA(RS_Ratio, 52 weeks)
    3. Mansfield_RS = ((RS_Ratio / RS_SMA) - 1) × 10

    Interpretation:
    - Above 0: Stronger than market
    - Below 0: Weaker than market
    """
    df = sector_prices_df.merge(
        vnindex_df[['date', 'close']].rename(columns={'close': 'vnindex'}),
        on='date'
    )

    # RS Ratio
    df['rs_ratio'] = df['sector_price'] / df['vnindex']

    # SMA of ratio (260 days = ~52 weeks)
    df['rs_sma'] = df.groupby('sector_code')['rs_ratio'].transform(
        lambda x: x.rolling(260, min_periods=60).mean()
    )

    # Mansfield RS (normalized around 0)
    df['mansfield_rs'] = ((df['rs_ratio'] / df['rs_sma']) - 1) * 10

    return df[['date', 'sector_code', 'rs_ratio', 'mansfield_rs']]
```

---

## 4. RRG Quadrant (With SMA Smoothing)

### Problem Solved
Daily median changes cause whipsaw (sectors jump between quadrants).

### Solution
Apply SMA smoothing to RS inputs before quadrant assignment.

### Formula

```python
def calculate_rrg_quadrant(
    sector_scores_df: pd.DataFrame,
    smooth_period: int = 3  # SMA 3 or 5 for smoothing
) -> pd.DataFrame:
    """
    Calculate RRG quadrant with smoothed inputs

    Args:
        sector_scores_df: DataFrame with 'score' column
        smooth_period: SMA period for smoothing (3 or 5 recommended)

    Returns:
        DataFrame with [rs_ratio_smooth, rs_momentum_smooth, quadrant]
    """
    df = sector_scores_df.copy().sort_values(['sector_code', 'date'])

    # Calculate raw RS ratio (score / market median)
    df['daily_median'] = df.groupby('date')['score'].transform('median')
    df['rs_ratio'] = df['score'] / df['daily_median']

    # RS Momentum (5-day change in score)
    df['rs_momentum'] = df.groupby('sector_code')['score'].diff(5)

    # Apply SMA smoothing to reduce whipsaw
    df['rs_ratio_smooth'] = df.groupby('sector_code')['rs_ratio'].transform(
        lambda x: x.rolling(smooth_period, min_periods=1).mean()
    )
    df['rs_momentum_smooth'] = df.groupby('sector_code')['rs_momentum'].transform(
        lambda x: x.rolling(smooth_period, min_periods=1).mean()
    )

    # Quadrant assignment using smoothed values
    conditions = [
        (df['rs_ratio_smooth'] > 1) & (df['rs_momentum_smooth'] > 0),
        (df['rs_ratio_smooth'] > 1) & (df['rs_momentum_smooth'] <= 0),
        (df['rs_ratio_smooth'] <= 1) & (df['rs_momentum_smooth'] <= 0),
        (df['rs_ratio_smooth'] <= 1) & (df['rs_momentum_smooth'] > 0)
    ]
    choices = ['LEADING', 'WEAKENING', 'LAGGING', 'IMPROVING']
    df['quadrant'] = np.select(conditions, choices, default='UNKNOWN')

    return df
```

### RRG Visualization

```
        RS Momentum (+)
              ↑
              │
   IMPROVING  │  LEADING
      ↗       │       ↘
              │
←─────────────┼─────────────→ RS Ratio
              │              1.0
      ↖       │       ↙
   LAGGING    │  WEAKENING
              │
              ↓
        RS Momentum (-)
```

### Rotation Cycle
```
LAGGING → IMPROVING → LEADING → WEAKENING → LAGGING
   ↑_______________________________________________|
```

---

## 5. Complete Sector Ranking Pipeline

```python
def run_sector_ranking_pipeline(
    ohlcv_df: pd.DataFrame,
    sector_map: dict,
    sector_breadth_df: pd.DataFrame,
    market_breadth_df: pd.DataFrame,
    vnindex_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Complete daily sector ranking pipeline

    Steps:
    1. Calculate returns (1W, 1M, 3M)
    2. Calculate IBD-style score
    3. Validate with breadth filter
    4. Calculate RRG quadrant (smoothed)
    5. Add Mansfield RS for charting
    """
    # Step 1: Returns
    sector_returns = calculate_sector_returns(ohlcv_df, sector_map)

    # Step 2: Score & Rank
    sector_scores = calculate_sector_score(sector_returns)

    # Step 3: Breadth Validation
    sector_validated = validate_sector_breadth(
        sector_scores, sector_breadth_df, market_breadth_df
    )

    # Step 4: RRG Quadrant (smoothed)
    sector_rrg = calculate_rrg_quadrant(sector_validated, smooth_period=3)

    # Step 5: Mansfield RS (for charting)
    # Note: Requires sector price index, implement separately if needed

    return sector_rrg


def get_sector_ranking_dashboard(df: pd.DataFrame, date: str = None) -> pd.DataFrame:
    """
    Get sector ranking for dashboard display
    """
    if date is None:
        date = df['date'].max()

    latest = df[df['date'] == date].sort_values('rank')

    return latest[[
        'rank', 'sector_code', 'score',
        'ret_1w', 'ret_1m', 'ret_3m',
        'quadrant', 'action',
        'breadth_status', 'warning'
    ]]
```

---

## 6. Output Schema

### SectorState Dataclass

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class SectorState:
    date: datetime
    sector_code: str

    # Returns
    ret_1w: float
    ret_1m: float
    ret_3m: float

    # Ranking
    score: float           # IBD-style weighted score
    rank: int              # 1-19
    action: str            # OVERWEIGHT/NEUTRAL/UNDERWEIGHT

    # RRG
    rs_ratio_smooth: float
    rs_momentum_smooth: float
    quadrant: str          # LEADING/WEAKENING/LAGGING/IMPROVING

    # Breadth Validation
    pct_above_ma50: float
    breadth_status: str    # VALID/WEAK_INTERNAL
    warning: Optional[str]

    # Mansfield (optional, for charting)
    mansfield_rs: Optional[float] = None
```

### Output File

```
DATA/processed/technical/sector_rotation/sector_ranking_daily.parquet
```

---

## 7. File Structure

```
PROCESSORS/technical/sector/
├── __init__.py
├── sector_ranking.py           # Main module (IBD-style)
│   ├── calculate_sector_returns()
│   ├── calculate_sector_score()
│   ├── validate_sector_breadth()
│   └── calculate_rrg_quadrant()
├── sector_mansfield.py         # Mansfield RS for charting
│   └── calculate_mansfield_rs()
└── daily_sector_ranking_update.py  # Daily pipeline
```

---

## 8. Dashboard Components

### 12_sector_rotation.py

```
┌─────────────────────────────────────────────────────────────────┐
│                     SECTOR ROTATION                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    RRG SCATTER PLOT                        │  │
│  │              (Using smoothed RS values)                    │  │
│  │          IMPROVING    │    LEADING                         │  │
│  │              ●CTG     │        ●VCB                        │  │
│  │         ●Securities   │    ●Banking                        │  │
│  │  ─────────────────────┼─────────────────────               │  │
│  │              ●Steel   │        ●Real Estate                │  │
│  │          LAGGING      │    WEAKENING                       │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              SECTOR RANKING TABLE (IBD-style)              │  │
│  │ Rank │ Sector      │ Score │ 1M%  │ 3M%  │ Breadth│ Action │  │
│  │ 1    │ Ngân hàng   │ 12.5  │ +15% │ +22% │ ✅ 72% │ OVERWEIGHT │
│  │ 2    │ Chứng khoán │ 10.2  │ +12% │ +18% │ ✅ 65% │ OVERWEIGHT │
│  │ 3    │ Thép        │  8.5  │ +10% │ +8%  │ ⚠️ 28% │ OVERWEIGHT* │
│  │ ...                                                        │  │
│  │ * Warning: Kéo trụ - Nội lực yếu                           │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 9. Trading Implications

### Combined Quadrant + Rank Table

| Quadrant | Rank 1-5 | Rank 6-12 | Rank 13-19 |
|----------|----------|-----------|------------|
| LEADING | **Strong Buy** | Hold | Take Profit |
| IMPROVING | Accumulate | Watch | Avoid |
| WEAKENING | Take Profit | Reduce | Avoid |
| LAGGING | Avoid | Avoid | **Strong Avoid** |

### Breadth Override

| Condition | Override Action |
|-----------|-----------------|
| Rank 1-5 + WEAK_INTERNAL | Reduce size by 50%, set tighter stops |
| Any Rank + Breadth < 20% | Avoid regardless of returns |

---

## 10. Implementation Checklist

### Core Functions
- [ ] `calculate_sector_returns()` - 1W, 1M, 3M returns
- [ ] `calculate_sector_score()` - IBD-style weighted score
- [ ] `validate_sector_breadth()` - Breadth filter
- [ ] `calculate_rrg_quadrant()` - With SMA smoothing
- [ ] `calculate_mansfield_rs()` - For charting (optional)

### Pipeline
- [ ] Create `daily_sector_ranking_update.py`
- [ ] Integrate into `run_all_daily_updates.py`
- [ ] Output: `sector_ranking_daily.parquet`

### Dashboard
- [ ] RRG scatter plot (smoothed values)
- [ ] Sector ranking table with breadth warnings
- [ ] Mansfield RS line chart (optional)

### Validation
- [ ] Verify returns calculation matches manual calc
- [ ] Test breadth filter catches "kéo trụ" scenarios
- [ ] Confirm RRG smoothing reduces whipsaw
- [ ] Compare ranking with market intuition

### Input Dependencies
- [x] OHLCV data - Already exists
- [x] sector_breadth_daily.parquet - Already exists
- [x] market_breadth_daily.parquet - Already exists
- [ ] Sector mapping (symbol → sector_code)
