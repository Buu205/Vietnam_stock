# Scout Report: Valuation Candlestick Chart Implementation

**Date:** 2025-12-21  
**Task:** Find files and patterns for implementing PE forward/trailing candlestick chart  
**Status:** COMPLETE - All files located and patterns identified

---

## I. Core Chart Building Files

### A. Plotly Chart Builders (MAIN)
**File:** `/Users/buuphan/Dev/Vietnam_dashboard/WEBAPP/components/charts/plotly_builders.py`

**Key Class:** `PlotlyChartBuilder` (v2.0.0)

**Existing Candlestick Method** (lines 347-415):
```python
@staticmethod
def candlestick_chart(
    df: pd.DataFrame,
    title: str,
    height: int = 400,
    show_rangeslider: bool = False
) -> go.Figure:
    """
    Build candlestick chart (for PE/PB valuation or price).
    
    Required columns: date, open, high, low, close
    Returns: Plotly Figure with candlestick
    """
    required_cols = ['date', 'open', 'high', 'low', 'close']
    # ... builds go.Candlestick with dark theme
```

**Color Palette** (lines 42-62):
- primary: `#8B5CF6` (Electric Purple - MAIN)
- secondary: `#06B6D4` (Cyan)
- accent: `#F59E0B` (Amber Gold)
- positive: `#10B981` (Emerald Green - bullish)
- negative: `#EF4444` (Red - bearish)

**Layout Template**:
- Template: `plotly_dark`
- Paper BG: `rgba(0,0,0,0)` (transparent)
- Plot BG: `rgba(0,0,0,0)` (transparent)
- Grid color: `rgba(255, 255, 255, 0.05)` (subtle)
- Font: `JetBrains Mono, monospace` + `#94A3B8` color
- Hovermode: `x unified`

**Convenience Function** (line 696):
```python
def pe_candlestick_chart(df: pd.DataFrame, symbol: str) -> go.Figure:
    """Pre-configured PE candlestick chart."""
    return PlotlyChartBuilder.candlestick_chart(
        df=df,
        title=f'PE Ratio Candlestick - {symbol}'
    )
```

---

### B. Valuation Dashboard Usage (REFERENCE)
**File:** `/Users/buuphan/Dev/Vietnam_dashboard/WEBAPP/pages/valuation/valuation_dashboard.py`

**Candlestick Implementation** (lines 169-236):
```python
# Create candlestick chart showing distribution
fig_candle = go.Figure()

for data in candle_data:
    # Add candlestick (body = P25-P75, whiskers = Min-Max)
    fig_candle.add_trace(go.Candlestick(
        x=[data['symbol']],
        open=[round(data['p25'], 2)],
        high=[round(data.get('max', data['p95']), 2)],
        low=[round(data.get('min', data['p5']), 2)],
        close=[round(data['p75'], 2)],
        name=data['symbol'],
        showlegend=False,
        increasing_line_color='lightgrey',
        decreasing_line_color='lightgrey',
        increasing_fillcolor='rgba(200, 200, 200, 0.3)',
        decreasing_fillcolor='rgba(200, 200, 200, 0.3)',
    ))
    
    # Add current value marker (colored circle)
    fig_candle.add_trace(go.Scatter(
        x=[data['symbol']],
        y=[data['current']],
        mode='markers',
        marker=dict(size=8, color=marker_color, symbol='circle'),
        name=f"{data['symbol']} Current",
    ))
```

---

## II. Data Source Files

### A. PE Historical Data
**Location:** `/Users/buuphan/Dev/Vietnam_dashboard/DATA/processed/valuation/pe/historical/historical_pe.parquet`

**Data Structure:**
- Shape: 789,611 rows × 8 columns
- Date range: 2018-01-02 to 2025-12-17
- Unique symbols: 458

**Columns:**
```
symbol                              object (ticker code)
date                       datetime64[ns] (daily timestamp)
close_price                       float64 (stock price in VND)
ttm_earning_billion_vnd           float64 (TTM earnings in billions)
shares_outstanding                float64 (shares count)
eps                               float64 (earnings per share)
pe_ratio                          float64 (TTM P/E ratio)
sector                             object (entity type: COMPANY, BANK, etc)
```

**Sample Data (ACB stock):**
```
2025-12-17: close_price=24,000 VND, pe_ratio=7.091, ttm_earning_billion_vnd=3,386B
2025-12-16: close_price=24,000 VND, pe_ratio=7.091, ttm_earning_billion_vnd=3,386B
...monthly aggregation for candlestick: open=7.475, high=7.475, low=7.150, close=7.165
```

### B. Related Valuation Data Files
- **PB (Price-to-Book):** `/DATA/processed/valuation/pb/historical/historical_pb.parquet`
- **EV/EBITDA:** `/DATA/processed/valuation/ev_ebitda/historical/historical_ev_ebitda.parquet`
- **P/S (Price-to-Sales):** `/DATA/processed/valuation/ps/historical/historical_ps.parquet`
- **VNINDEX:** `/DATA/processed/valuation/vnindex/vnindex_valuation_refined.parquet`

---

## III. Valuation Service Layer

**File:** `/Users/buuphan/Dev/Vietnam_dashboard/WEBAPP/services/valuation_service.py`

**Key Methods:**
```python
class ValuationService:
    def _load_pe_data(self) -> pd.DataFrame:
        """Load PE historical data (cached)."""
        # Loads from DATA/processed/valuation/pe/historical/historical_pe.parquet
        
    def get_valuation_data(self, scope="VNINDEX") -> pd.DataFrame:
        """Get PE/PB/EV-EBITDA data by scope."""
        
    def get_ticker_valuation(self, ticker: str) -> pd.DataFrame:
        """Get single stock valuation time series."""
        
    def get_industry_candle_data(self, industry: str, metric: str, start_year: int):
        """Get candlestick distribution data for industry."""
```

**Outlier Rules** (lines 47-68):
```python
OUTLIER_RULES = {
    'PE': {
        'max_value': 100,           # PE > 100 = outlier
        'min_value': 0,             # PE must be positive
        'multiplier_limit': 5,      # Max 5x median
    },
    'PB': {
        'max_value': 20,
        'min_value': 0,
        'multiplier_limit': 4,
    },
    # ... similar for PS, EV_EBITDA
}
```

---

## IV. Statistical Calculation Patterns

### A. Percentile Calculation (from sector_dashboard.py)
```python
# Calculate percentile for current value within distribution
clean_data = metric_data[metric_data.notna()]
percentile = np.sum(clean_data <= current_val) / len(clean_data) * 100
```

### B. Mean & Standard Deviation
```python
mean_val = metric_data.mean()
std_val = metric_data.std()

# Create bands (already implemented in line_with_bands)
upper_band = mean_val + (num_std * std_val)
lower_band = mean_val - (num_std * std_val)
```

### C. Percentile-Based Candlestick Body
```python
# Body = P25-P75 (interquartile range)
# Whiskers = Min-Max or P5-P95
data['p25'] = metric_data.quantile(0.25)
data['p75'] = metric_data.quantile(0.75)
data['median'] = metric_data.median()
data['min'] = metric_data.min()
data['max'] = metric_data.max()
```

### D. Status Classification (Valuation Dashboard)
```python
# Classify current value status based on percentile
if percentile < 25:
    status = "Very Cheap"
elif percentile < 40:
    status = "Cheap"
elif percentile < 60:
    status = "Fair"
elif percentile < 75:
    status = "Expensive"
else:
    status = "Very Expensive"
```

---

## V. BSC Forecast Data Integration

**File:** `/Users/buuphan/Dev/Vietnam_dashboard/WEBAPP/services/forecast_service.py`

**PE Forward Data Available:**
```python
class ForecastService:
    def get_individual_stocks(self) -> pd.DataFrame:
        # Loads bsc_individual.parquet (92 stocks)
        # Contains: pe_fwd_2025, pe_fwd_2026, pb_fwd_2025, pb_fwd_2026
        
    def get_sector_valuation(self) -> pd.DataFrame:
        # Loads bsc_sector_valuation.parquet (15 sectors)
        # Contains: pe_fwd_2025, pe_fwd_2026, pb_fwd_2025, pb_fwd_2026
```

**Data Location:** `/DATA/processed/forecast/bsc/`
- `bsc_individual.parquet` (92 stocks with forward valuations)
- `bsc_sector_valuation.parquet` (15 sectors with forward valuations)

---

## VI. Forecast Dashboard Reference

**File:** `/Users/buuphan/Dev/Vietnam_dashboard/WEBAPP/pages/forecast/forecast_dashboard.py`

**PE Forward Comparison Chart** (lines 650-730):
```python
# PE TTM vs Forward - Compare current valuation vs forward
sector_pe_df = service.get_sector_with_pe_pb_ttm()

fig = go.Figure()

# PE TTM bars (Gold)
fig.add_trace(go.Bar(
    x=chart_df['sector'],
    y=chart_df['sector_pe_ttm'],
    name='PE TTM',
    marker_color='#FFC132',
))

# PE FWD 2025 bars (Purple)
fig.add_trace(go.Bar(
    x=chart_df['sector'],
    y=chart_df['pe_fwd_2025'],
    name='PE FWD 2025',
    marker_color='#8B5CF6',
))

# PE FWD 2026 bars (Cyan)
fig.add_trace(go.Bar(
    x=chart_df['sector'],
    y=chart_df['pe_fwd_2026'],
    name='PE FWD 2026',
    marker_color='#06B6D4',
))
```

---

## VII. Implementation Checklist for Candlestick

### Data Preparation
- [ ] Load PE historical data: `historical_pe.parquet`
- [ ] Aggregate to candlestick OHLC by time period (daily/weekly/monthly)
  - `open` = first PE ratio in period
  - `high` = max PE ratio in period
  - `low` = min PE ratio in period
  - `close` = last PE ratio in period
- [ ] Load PE forward data from BSC forecast files
- [ ] Merge historical + forward data for comparison

### Statistical Bands
- [ ] Calculate percentiles (P25, P50/median, P75)
- [ ] Calculate mean and std dev
- [ ] Create shaded bands (±1σ or ±2σ)

### Chart Building
- [ ] Use `PlotlyChartBuilder.candlestick_chart()` or extend it
- [ ] Set title: "PE Candlestick - [Symbol or Sector]"
- [ ] Add reference lines (mean, median)
- [ ] Color scheme: use PlotlyChartBuilder.COLORS palette
- [ ] Hovertemplate: show OHLC + percentile + status

### Integration Points
- [ ] Call from valuation dashboard or new forecast page
- [ ] Use ValuationService or ForecastService for data
- [ ] Style with get_page_style() and get_chart_layout()

---

## VIII. Key Code Snippets for Reference

### Monthly Candlestick Aggregation
```python
import pandas as pd

# Aggregate daily PE data to monthly OHLC
df = pd.read_parquet('DATA/processed/valuation/pe/historical/historical_pe.parquet')

# Filter single ticker
ticker_data = df[df['symbol'] == 'ACB'].sort_values('date')

# Resample to monthly
monthly_candle = ticker_data.set_index('date').groupby(pd.Grouper(freq='M')).agg({
    'pe_ratio': ['first', 'max', 'min', 'last']
}).reset_index()

monthly_candle.columns = ['date', 'open', 'high', 'low', 'close']
monthly_candle['date'] = monthly_candle['date'].dt.strftime('%Y-%m')

# Now use with candlestick_chart()
fig = PlotlyChartBuilder.candlestick_chart(
    df=monthly_candle,
    title=f'PE Monthly Candlestick - {ticker}'
)
```

### Percentile-Based Status
```python
# Calculate status based on historical distribution
historical_pe = df[df['symbol'] == 'ACB']['pe_ratio'].dropna()

current_pe = 7.091
percentile = (historical_pe <= current_pe).mean() * 100

if percentile < 25:
    status = "Very Cheap"
elif percentile < 40:
    status = "Cheap"
elif percentile < 60:
    status = "Fair"
elif percentile < 75:
    status = "Expensive"
else:
    status = "Very Expensive"
```

### PE Forward vs Trailing Comparison
```python
# Get TTM and Forward PE
ttm_pe = df[df['symbol'] == 'ACB']['pe_ratio'].iloc[-1]  # Latest TTM
fwd_2025_pe = 12.5  # From BSC forecast

# Build comparison candlestick
comparison_df = pd.DataFrame({
    'date': ['TTM', '2025F', '2026F'],
    'open': [ttm_pe, fwd_2025_pe, 11.8],
    'high': [ttm_pe + 0.5, fwd_2025_pe + 0.3, 12.2],
    'low': [ttm_pe - 0.5, fwd_2025_pe - 0.3, 11.4],
    'close': [ttm_pe, fwd_2025_pe, 12.0]
})

fig = PlotlyChartBuilder.candlestick_chart(
    df=comparison_df,
    title='ACB: PE Valuation - TTM vs 2025-2026 Forward'
)
```

---

## IX. File Summary Table

| Component | File Path | Type | Key Content |
|-----------|-----------|------|-------------|
| **Chart Builder** | `WEBAPP/components/charts/plotly_builders.py` | Main | `PlotlyChartBuilder` class + `candlestick_chart()` method |
| **PE Data** | `DATA/processed/valuation/pe/historical/historical_pe.parquet` | Data | 789K rows of daily PE ratios (2018-2025) |
| **Valuation Service** | `WEBAPP/services/valuation_service.py` | Service | Data loading + outlier rules |
| **Forecast Service** | `WEBAPP/services/forecast_service.py` | Service | BSC forward PE/PB data |
| **Valuation Dashboard** | `WEBAPP/pages/valuation/valuation_dashboard.py` | Page | Reference implementation of candlestick chart |
| **Forecast Dashboard** | `WEBAPP/pages/forecast/forecast_dashboard.py` | Page | PE TTM vs Forward bar charts |

---

## X. Recommendations

1. **For TTM Candlestick:**
   - Use `PlotlyChartBuilder.candlestick_chart()` directly
   - Aggregate `historical_pe.parquet` by time period
   - Add statistical bands (percentiles) using existing pattern

2. **For PE Forward Candlestick:**
   - Extend the builder to support sector-level forward PE
   - Use `ForecastService.get_sector_valuation()` for BSC forward data
   - Combine with TTM data for side-by-side comparison

3. **For Statistical Accuracy:**
   - Use `quantile()` for P25/P75/median
   - Use `.std()` and `.mean()` for bands
   - Filter outliers using OUTLIER_RULES from ValuationService

4. **For UI Integration:**
   - Add to forecast dashboard Tab 4 (Charts section)
   - Use existing color palette from PlotlyChartBuilder.COLORS
   - Follow hovertemplate pattern from valuation_dashboard.py

---

**Report Generated:** 2025-12-21  
**Token Efficiency:** Comprehensive scout using parallel Glob/Grep/Read tools  
**Status:** All files located and patterns documented
