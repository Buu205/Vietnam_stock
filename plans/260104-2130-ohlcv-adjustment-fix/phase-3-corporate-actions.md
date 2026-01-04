# Phase 3: Corporate Actions Registry

**File:** `DATA/processed/metadata/corporate_actions.csv`
**Effort:** 1h
**Dependencies:** None (can be done in parallel with Phase 1-2)

## Objective

Create a manual registry of known corporate actions to:
1. Skip API refresh for verified actions (already adjusted in source)
2. Provide reference data for spike classification
3. Enable future automation (scrape announcements)

## Schema

```csv
ticker,date,action_type,ratio,verified,source,notes
CSV,2025-06-04,STOCK_SPLIT,4.7,YES,manual_review,"373.7% return detected"
CTG,2025-12-17,SHARE_DIVIDEND,1.4463658403,YES,vietstock,"100:44.63658403 bonus"
HDB,2025-12-17,SHARE_DIVIDEND,1.0469,YES,vietstock,"100:4.69 bonus"
```

## Field Definitions

| Field | Type | Description |
|-------|------|-------------|
| `ticker` | string | Stock symbol (uppercase) |
| `date` | date | Ex-date of corporate action (YYYY-MM-DD) |
| `action_type` | enum | `STOCK_SPLIT`, `SHARE_DIVIDEND`, `CASH_DIVIDEND`, `RIGHTS_ISSUE` |
| `ratio` | float | Split/bonus ratio (e.g., 2.0 for 2:1 split) |
| `verified` | bool | `YES` if manually verified, `NO` if auto-detected |
| `source` | string | Data source: `manual_review`, `vietstock`, `hose_announcement` |
| `notes` | string | Optional notes for context |

## Usage in Spike Detector

```python
def load_corporate_actions() -> pd.DataFrame:
    """Load verified corporate actions."""
    path = Path("DATA/processed/metadata/corporate_actions.csv")
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, parse_dates=['date'])

def is_known_corporate_action(symbol: str, date: date) -> bool:
    """Check if spike is a known corporate action."""
    actions = load_corporate_actions()
    if actions.empty:
        return False

    match = actions[
        (actions['ticker'] == symbol) &
        (actions['date'] == pd.Timestamp(date))
    ]
    return not match.empty

def classify_spike_with_registry(row: pd.Series) -> str:
    """
    Enhanced classification using corporate actions registry.
    """
    # Check registry first
    if is_known_corporate_action(row['symbol'], row['date']):
        actions = load_corporate_actions()
        action = actions[
            (actions['ticker'] == row['symbol']) &
            (actions['date'] == pd.Timestamp(row['date']))
        ].iloc[0]
        return action['action_type']

    # Fall back to algorithmic detection
    if row['split_ratio'] is not None:
        return 'SPLIT'
    elif 0.05 <= abs(row['daily_return']) <= 0.15 and row['volume_spike']:
        return 'DIVIDEND'
    else:
        return 'UNKNOWN'
```

## Initial Population

Known corporate actions to add immediately:

| Ticker | Date | Action | Ratio | Source |
|--------|------|--------|-------|--------|
| CSV | 2025-06-04 | STOCK_SPLIT | 4.7 | User report |
| CTG | 2025-12-17 | SHARE_DIVIDEND | 1.45 | Vietstock |
| HDB | 2025-12-17 | SHARE_DIVIDEND | 1.05 | Vietstock |

## Data Sources for Future Entries

1. **Vietstock Announcements**: https://en.vietstock.vn/vietnam-companies/dividend-963.htm
2. **HOSE Official**: https://www.hsx.vn/Modules/Listed/Web/StockDividend
3. **HNX Official**: https://www.hnx.vn/cophieu-etf/co-phieu-nieem-yet.html

## File Location

```
DATA/
└── processed/
    └── metadata/
        └── corporate_actions.csv   # NEW
```

Create directory if not exists:
```bash
mkdir -p DATA/processed/metadata
```

## Maintenance Workflow

1. **On spike detection with `UNKNOWN` type**:
   - Human reviews announcement
   - Adds entry to `corporate_actions.csv`
   - Sets `verified=YES`

2. **Quarterly review**:
   - Scrape Vietstock for new announcements
   - Add unverified entries (`verified=NO`)
   - Manual verification cycle

## Deliverables

- [ ] Create `DATA/processed/metadata/` directory
- [ ] Create `corporate_actions.csv` with schema
- [ ] Populate with CSV, CTG, HDB known actions
- [ ] Add `load_corporate_actions()` helper function
- [ ] Integrate with spike detector classification
