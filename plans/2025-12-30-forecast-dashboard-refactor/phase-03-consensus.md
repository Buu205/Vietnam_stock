# Phase 3: Consensus Tab (Tab 3)

**Duration:** Day 2-3
**Priority:** P2 (Medium Impact)
**Parent Plan:** [plan.md](plan.md) | **Design:** [design-system-guide.md](design-system-guide.md)

---

## Objectives

1. BSC vs VCI comparison by ticker (not sector)
2. Verdict status for each stock
3. Scatter/bar charts for visualization

---

## Scope

**Tab 3: Consensus** compares BSC forecast with VCI (Vietcap IQ):
- Comparison by TICKER (sector mapping NOT needed)
- Priority metrics: NPATMI > Target Price > PE/PB
- Verdict format: ALIGNED / BSC_BULL / VCI_BULL / DIVERGENT

---

## Task 3.1: VCI Data Loading

**File:** `WEBAPP/services/forecast_service.py`

```python
def load_vci_forecast() -> pd.DataFrame:
    """Load VCI coverage universe data."""
    path = Path("DATA/processed/forecast/vci/vci_coverage_universe.parquet")
    if path.exists():
        return pd.read_parquet(path)
    return pd.DataFrame()
```

---

## Task 3.2: BSC-VCI Merge Function

**File:** `WEBAPP/services/forecast_service.py`

```python
def merge_bsc_vci(bsc_df: pd.DataFrame, vci_df: pd.DataFrame) -> pd.DataFrame:
    """
    Merge BSC and VCI forecasts by ticker.

    Args:
        bsc_df: BSC forecast data
        vci_df: VCI coverage universe data

    Returns:
        Merged DataFrame with columns from both sources

    Note: Use BSC sector as standard. No sector mapping needed.
    """
    # Standardize column names
    vci_clean = vci_df.rename(columns={
        'ticker': 'symbol',
        'targetPrice': 'vci_target_price',
        'npatmi_2025F': 'vci_npatmi_2025',
        'pe_2025F': 'vci_pe_2025',
    })

    # Merge on ticker
    merged = bsc_df.merge(
        vci_clean[['symbol', 'vci_target_price', 'vci_npatmi_2025', 'vci_pe_2025']],
        on='symbol',
        how='left'
    )

    return merged
```

---

## Task 3.3: Consensus Status Calculation

**File:** `WEBAPP/services/forecast_service.py`

```python
def calculate_consensus_status(row: pd.Series) -> str:
    """
    Calculate consensus status between BSC and VCI.

    Thresholds:
    - ALIGNED: diff < 5%
    - BSC_BULL: BSC > VCI by >5%
    - VCI_BULL: VCI > BSC by >5%
    - DIVERGENT: diff > 20%
    """
    bsc_npatmi = row.get('npatmi_2025f', 0)
    vci_npatmi = row.get('vci_npatmi_2025', 0)

    if pd.isna(vci_npatmi) or vci_npatmi == 0:
        return 'NO_VCI_DATA'

    diff_pct = (bsc_npatmi - vci_npatmi) / vci_npatmi * 100

    if abs(diff_pct) > 20:
        return 'DIVERGENT'
    elif diff_pct > 5:
        return 'BSC_BULL'
    elif diff_pct < -5:
        return 'VCI_BULL'
    else:
        return 'ALIGNED'
```

---

## Task 3.4: Consensus Comparison Table

**File:** `WEBAPP/components/tables/consensus_table.py`

### Columns

| Column | Source | Format |
|--------|--------|--------|
| Symbol | BSC | Bold |
| BSC NPATMI 25F | BSC | Billions |
| VCI NPATMI 25F | VCI | Billions |
| NPATMI Diff | Calc | % |
| BSC Target | BSC | Price |
| VCI Target | VCI | Price |
| TP Diff | Calc | % |
| Consensus | Calc | Badge |

### Consensus Badge Colors

**Using SVG icons from `WEBAPP/components/ui/icons`:**

```python
from WEBAPP.components.ui import consensus_icon

# In table formatter:
def format_consensus_cell(status: str) -> str:
    return consensus_icon(status)

# Returns SVG icons:
# ALIGNED   -> check-circle (teal #00C9AD)
# BSC_BULL  -> trending-up (blue #3B82F6)
# VCI_BULL  -> trending-up (orange #F59E0B)
# DIVERGENT -> exclamation-triangle (red #EF4444)
```

---

## Task 3.5: Dashboard Integration

**File:** `WEBAPP/pages/forecast/forecast_dashboard.py`

```python
# Tab 3: Consensus
if active_tab == 3:
    st.markdown("### BSC vs VCI Consensus")
    st.markdown("*Comparing NPATMI and Target Price forecasts*")

    # Load and merge data
    bsc_df = load_bsc_forecast()
    vci_df = load_vci_forecast()
    consensus_df = merge_bsc_vci(bsc_df, vci_df)

    # Add consensus status
    consensus_df['consensus'] = consensus_df.apply(
        calculate_consensus_status, axis=1
    )

    # Filter options
    status_filter = st.selectbox(
        "Consensus Status",
        ["All", "ALIGNED", "BSC_BULL", "VCI_BULL", "DIVERGENT"]
    )

    if status_filter != "All":
        consensus_df = consensus_df[consensus_df['consensus'] == status_filter]

    # Render table
    html = consensus_table(consensus_df)
    st.markdown(html, unsafe_allow_html=True)
```

---

## Task 3.6: VCI Snapshot Hook (Data Pipeline)

**File:** `PROCESSORS/api/vietcap/fetch_vci_forecast.py`

Add auto-snapshot when fetching VCI data:

```python
def fetch_and_save():
    """Fetch coverage universe and save parquet."""
    # ... existing fetch code ...

    # Auto-snapshot for history tracking
    snapshot_vci_forecast(df)

    return True


def snapshot_vci_forecast(current_df: pd.DataFrame):
    """Append snapshot to history file."""
    from datetime import datetime

    history_path = Path("DATA/processed/forecast/vci/history/forecast_history.parquet")
    today = datetime.now().strftime('%Y-%m-%d')

    snapshot_df = current_df.copy()
    snapshot_df['snapshot_date'] = today
    snapshot_df['source'] = 'VCI'

    if history_path.exists():
        history = pd.read_parquet(history_path)
        if today not in history['snapshot_date'].values:
            history = pd.concat([history, snapshot_df], ignore_index=True)
            history.to_parquet(history_path, index=False)
            print(f"[OK] VCI Snapshot saved: {len(snapshot_df)} rows for {today}")
        else:
            print(f"[!] VCI Snapshot for {today} already exists, skipping")
    else:
        history_path.parent.mkdir(parents=True, exist_ok=True)
        snapshot_df.to_parquet(history_path, index=False)
        print(f"[OK] VCI History created: {len(snapshot_df)} rows for {today}")
```

---

## Files to Create/Modify

| File | Action | Notes |
|------|--------|-------|
| `WEBAPP/services/forecast_service.py` | MODIFY | Add VCI loading, merge, status functions |
| `WEBAPP/components/tables/consensus_table.py` | CREATE | BSC vs VCI comparison table |
| `WEBAPP/pages/forecast/forecast_dashboard.py` | MODIFY | Add Tab 3 |
| `PROCESSORS/api/vietcap/fetch_vci_forecast.py` | MODIFY | Add snapshot hook |

---

## Testing Checklist

- [ ] VCI data loads correctly
- [ ] Merge works with ticker matching
- [ ] Consensus status calculates correctly
- [ ] Table shows all comparison columns
- [ ] Status filter works
- [ ] Snapshot hook saves to history

---

## Dependencies

- VCI parquet data exists at `DATA/processed/forecast/vci/vci_coverage_universe.parquet`
- BSC forecast data loaded
