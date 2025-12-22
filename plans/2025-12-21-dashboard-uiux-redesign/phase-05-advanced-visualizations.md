# Phase 5: Advanced Visualizations & Chart Types

**Goal:** Implement professional financial chart types for enhanced data presentation
**Effort:** 5-7 days | **Risk:** Medium-High (new components)

---

## Current Chart Types (Existing)

| Chart Type | Used In | Library |
|-----------|---------|---------|
| Line with bands | Valuation time series | Plotly |
| Candlestick distribution | Sector PE/PB | Plotly |
| Box plot | Valuation comparisons | Plotly |
| Histogram | Distribution analysis | Plotly |
| Bar charts | Category comparisons | Plotly |
| Metric cards | KPI display | Streamlit native |

---

## Recommended New Chart Types

### 1. Heatmap - Sector Correlation Matrix

**Use Case:** Show correlation between sectors or between metrics

**Color Scheme (Dark Theme):**
- Positive correlation: `#06B6D4` (cyan) → `#8B5CF6` (purple)
- Negative correlation: `#F59E0B` (amber) → `#EF4444` (red)
- Neutral: `#1A1625` (background)

**Implementation:**
```python
import plotly.express as px

def sector_correlation_heatmap(correlation_matrix: pd.DataFrame):
    """Sector correlation heatmap with dark theme."""
    fig = px.imshow(
        correlation_matrix,
        color_continuous_scale=[
            [0.0, '#EF4444'],    # -1: Strong negative
            [0.25, '#F59E0B'],   # -0.5: Weak negative
            [0.5, '#1A1625'],    # 0: Neutral
            [0.75, '#06B6D4'],   # 0.5: Weak positive
            [1.0, '#8B5CF6'],    # 1: Strong positive
        ],
        aspect='auto',
        zmin=-1, zmax=1
    )
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='#0F0B1E',
        font_color='#94A3B8',
        height=500
    )
    return fig
```

**Placement:** Sector Dashboard → New "Correlation" tab

---

### 2. Treemap - Market Cap Distribution

**Use Case:** Visualize market cap distribution by sector → industry → ticker

**Color Scheme:**
- Parent sectors: Distinct hues from theme palette
- Children: Lighter shades (15-20% lighter per level)
- White borders: 2px

**Implementation:**
```python
import plotly.express as px

def market_cap_treemap(df: pd.DataFrame):
    """Treemap showing market cap hierarchy."""
    fig = px.treemap(
        df,
        path=['sector', 'industry', 'ticker'],
        values='market_cap',
        color='pct_change',
        color_continuous_scale=['#EF4444', '#1A1625', '#22C55E'],
        color_continuous_midpoint=0
    )
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=30, b=0)
    )
    return fig
```

**Placement:** Sector Dashboard → "Distribution" tab (alternative view)

---

### 3. Waterfall Chart - P&L Breakdown

**Use Case:** Show how revenue flows to net income (Revenue → Costs → EBIT → Net Income)

**Color Scheme:**
- Increases: `#22C55E` (green)
- Decreases: `#EF4444` (red)
- Totals: `#8B5CF6` (purple)

**Implementation:**
```python
import plotly.graph_objects as go

def pnl_waterfall(items: list, values: list):
    """Waterfall chart for P&L breakdown."""
    fig = go.Figure(go.Waterfall(
        orientation='v',
        measure=['absolute'] + ['relative'] * (len(items) - 2) + ['total'],
        x=items,
        y=values,
        decreasing={'marker': {'color': '#EF4444'}},
        increasing={'marker': {'color': '#22C55E'}},
        totals={'marker': {'color': '#8B5CF6'}},
        textposition='outside',
        text=[f'{v:,.0f}' for v in values]
    ))
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='#0F0B1E',
        showlegend=False
    )
    return fig
```

**Placement:** Company Dashboard → "Financials" tab

---

### 4. Bullet Chart - Performance vs Target

**Use Case:** Compare actual metrics vs targets/benchmarks (e.g., ROE vs sector average)

**Color Scheme:**
- Poor range: `#FFCDD2` (light red) at 20% opacity
- Acceptable range: `#FFF9C4` (light yellow) at 20% opacity
- Good range: `#C8E6C9` (light green) at 20% opacity
- Actual: `#8B5CF6` (purple bar)
- Target: Black marker line

**Implementation:**
```python
import plotly.graph_objects as go

def bullet_chart(metric: str, actual: float, target: float, ranges: list):
    """Bullet chart for metric vs target."""
    fig = go.Figure()

    # Background ranges
    colors = ['rgba(200,230,201,0.2)', 'rgba(255,249,196,0.2)', 'rgba(255,205,210,0.2)']
    for i, (r, c) in enumerate(zip(ranges, colors)):
        fig.add_shape(type='rect', x0=0, x1=r, y0=-0.2, y1=0.2,
                     fillcolor=c, line_width=0)

    # Actual bar
    fig.add_trace(go.Bar(x=[actual], y=[metric], orientation='h',
                        marker_color='#8B5CF6', width=0.3))

    # Target marker
    fig.add_shape(type='line', x0=target, x1=target, y0=-0.3, y1=0.3,
                 line=dict(color='white', width=3))

    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        height=80,
        margin=dict(l=100, r=20, t=10, b=10),
        xaxis=dict(range=[0, max(ranges)], showgrid=False),
        yaxis=dict(showticklabels=True)
    )
    return fig
```

**Placement:** Company/Bank Dashboard → KPI section (inline with cards)

---

### 5. Radar Chart - Multi-Variable Comparison

**Use Case:** Compare a ticker across multiple fundamental metrics vs sector average

**Axes (Example for Bank):**
- NIM, ROE, ROA, NPL Ratio, CAR, CASA, CIR

**Color Scheme:**
- Ticker line: `#8B5CF6` with 20% fill
- Sector average line: `#06B6D4` dashed

**Implementation:**
```python
import plotly.graph_objects as go

def radar_comparison(ticker_values: list, sector_values: list, categories: list):
    """Radar chart comparing ticker vs sector."""
    fig = go.Figure()

    # Ticker
    fig.add_trace(go.Scatterpolar(
        r=ticker_values + [ticker_values[0]],  # Close the polygon
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor='rgba(139, 92, 246, 0.2)',
        line_color='#8B5CF6',
        name='Ticker'
    ))

    # Sector average
    fig.add_trace(go.Scatterpolar(
        r=sector_values + [sector_values[0]],
        theta=categories + [categories[0]],
        line=dict(color='#06B6D4', dash='dash'),
        name='Sector Avg'
    ))

    fig.update_layout(
        template='plotly_dark',
        polar=dict(
            bgcolor='#0F0B1E',
            radialaxis=dict(visible=True, range=[0, 100])
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=True,
        height=400
    )
    return fig
```

**Placement:** Company/Bank Dashboard → New "Profile" tab or side panel

---

### 6. Gauge Chart - Single Metric Focus

**Use Case:** Highlight key metric with visual target indicator (e.g., RSI, PE percentile)

**Color Scheme:**
- Below target: `#EF4444` (red)
- Near target: `#F59E0B` (amber)
- At/above target: `#22C55E` (green)

**Implementation:**
```python
import plotly.graph_objects as go

def gauge_chart(value: float, title: str, min_val=0, max_val=100, target=50):
    """Gauge chart with target marker."""
    fig = go.Figure(go.Indicator(
        mode='gauge+number',
        value=value,
        title={'text': title, 'font': {'color': '#94A3B8', 'size': 14}},
        gauge={
            'axis': {'range': [min_val, max_val], 'tickcolor': '#64748B'},
            'bar': {'color': '#8B5CF6'},
            'bgcolor': '#1A1625',
            'borderwidth': 0,
            'steps': [
                {'range': [min_val, target * 0.7], 'color': 'rgba(239,68,68,0.3)'},
                {'range': [target * 0.7, target * 1.0], 'color': 'rgba(245,158,11,0.3)'},
                {'range': [target * 1.0, max_val], 'color': 'rgba(34,197,94,0.3)'}
            ],
            'threshold': {
                'line': {'color': 'white', 'width': 2},
                'thickness': 0.8,
                'value': target
            }
        },
        number={'font': {'color': '#F1F5F9', 'size': 28}}
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        height=200,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig
```

**Placement:** Technical Dashboard → RSI indicator | Valuation Dashboard → PE percentile

---

### 7. Sparklines - Inline Trend Indicators

**Use Case:** Show mini trend charts inline with metric cards or tables

**Implementation:**
```python
import plotly.graph_objects as go

def sparkline(values: list, color='#8B5CF6', height=40, width=120):
    """Minimal sparkline chart."""
    fig = go.Figure(go.Scatter(
        y=values,
        mode='lines',
        line=dict(color=color, width=1.5),
        fill='tozeroy',
        fillcolor=f'rgba{tuple(int(color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)) + (0.1,)}'
    ))
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=height,
        width=width,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig
```

**Placement:** KPI cards (embed as HTML), Data tables (trend column)

---

### 8. Sunburst Chart - Hierarchical Proportions

**Use Case:** Show portfolio allocation or revenue breakdown by segment

**Implementation:**
```python
import plotly.express as px

def sunburst_allocation(df: pd.DataFrame):
    """Sunburst for hierarchical allocation."""
    fig = px.sunburst(
        df,
        path=['category', 'subcategory', 'item'],
        values='value',
        color='growth',
        color_continuous_scale=['#EF4444', '#1A1625', '#22C55E'],
        color_continuous_midpoint=0
    )
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=30, b=0)
    )
    return fig
```

**Placement:** Company Dashboard → Revenue breakdown | Sector Dashboard → Market share

---

## Chart Component File Structure

Create new file: `WEBAPP/components/charts/advanced_charts.py`

```python
"""
Advanced Chart Components
=========================
Professional financial visualization components.

Contents:
- sector_correlation_heatmap()
- market_cap_treemap()
- pnl_waterfall()
- bullet_chart()
- radar_comparison()
- gauge_chart()
- sparkline()
- sunburst_allocation()
"""

# All implementations above
```

---

## Dark Theme Constants

```python
# WEBAPP/core/chart_theme.py

DARK_THEME = {
    'bg_void': '#0F0B1E',
    'bg_deep': '#1A1625',
    'text_primary': '#F1F5F9',
    'text_secondary': '#94A3B8',
    'text_muted': '#64748B',
    'purple_primary': '#8B5CF6',
    'cyan_accent': '#06B6D4',
    'amber_warning': '#F59E0B',
    'green_positive': '#22C55E',
    'red_negative': '#EF4444',
    'glass_bg': 'rgba(139, 92, 246, 0.08)',
    'glass_border': 'rgba(139, 92, 246, 0.15)',
}

def get_plotly_layout(title: str = "", height: int = 400):
    """Standard Plotly layout for dark theme."""
    return {
        'template': 'plotly_dark',
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': DARK_THEME['bg_void'],
        'font': {'color': DARK_THEME['text_secondary']},
        'title': {'text': title, 'font': {'color': DARK_THEME['text_primary']}},
        'height': height,
        'margin': {'l': 40, 'r': 20, 't': 50, 'b': 40}
    }
```

---

## Implementation Priority

| Chart Type | Priority | Effort | Impact |
|-----------|----------|--------|--------|
| Heatmap (Correlation) | High | 2 days | Sector insights |
| Treemap (Market Cap) | High | 2 days | Visual market overview |
| Waterfall (P&L) | Medium | 1 day | Financial storytelling |
| Bullet Chart | Medium | 1 day | Benchmark comparison |
| Radar Chart | Low | 1 day | Multi-metric profiles |
| Gauge Chart | Low | 0.5 days | Single focus metrics |
| Sparklines | Low | 0.5 days | Inline trends |
| Sunburst | Low | 1 day | Hierarchical breakdown |

**Recommended order:** Heatmap → Treemap → Waterfall → Bullet → Others

---

## Validation Checklist

- [ ] All charts use consistent dark theme colors
- [ ] Charts are responsive (handle window resize)
- [ ] Hover tooltips show relevant data
- [ ] Chart heights are configurable
- [ ] Export functionality works (PNG/SVG)
- [ ] Performance: Charts render < 500ms
- [ ] Accessibility: Provide data table alternatives

---

## Rollback

If new charts cause performance issues, fallback to existing Plotly bar/line charts.
