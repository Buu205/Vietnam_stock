# Phase 2: Dual-Axis Charts

**Priority:** High
**Effort:** 3 hours
**Risk:** Medium

---

## Context

Current dashboard shows single indicators or basic pairs. Need grouped dual-axis charts for:
1. Deposit rates (3 tenors on same axis - same unit %)
2. Interbank rates by tenor (same axis - same unit %)
3. Exchange rates (official vs free market)
4. Commodity VN vs Global pairs

## Overview

Enhance chart logic to support:
- Multi-series single-axis (same unit, e.g., interest rates %)
- True dual-axis (different units, e.g., VND vs USD)

## Requirements

1. Interest rate groups render on shared Y-axis with distinct colors
2. Exchange rate pairs show spread clearly (already works, enhance labels)
3. Commodity pairs use dual Y-axes for VN (VND) vs Global (USD)
4. Legend visibility and color contrast for multi-series

## Related Code Files

### `fx_commodities_dashboard.py` - Macro Tab (lines 273-342)
```python
# CURRENT: Simple loop adding traces, no grouping logic
for i, symbol in enumerate(target_symbols):
    series = filter_series_by_days(macro_loader.get_series(symbol), days)
    if not series.empty and 'value' in series.columns:
        label = macro_labels.get(symbol, symbol)
        fig_macro.add_trace(go.Scatter(...))
```

### `fx_commodities_dashboard.py` - Exchange Rate Pairs (lines 98-222)
Already has dual-pair logic but uses single axis since same VND unit.

### `fx_commodities_dashboard.py` - Commodity Pairs (lines 384-498)
Has dual-axis implementation for VN vs Global pairs.

## Implementation Steps

### Step 1: Define Interest Rate Chart Groups (ADD)
Add after symbol mapping section (line ~120):

```python
# Interest Rate Groupings (shared Y-axis, % unit)
INTEREST_RATE_GROUPS = {
    "💰 Lãi suất huy động (3 kỳ hạn)": {
        'symbols': ['ls_huy_dong_1_3_thang', 'ls_huy_dong_6_9_thang', 'ls_huy_dong_13_thang'],
        'colors': ['#8B5CF6', '#06B6D4', '#F59E0B'],  # Purple, Cyan, Amber
        'unit': '%',
        'title': 'Deposit Interest Rates by Tenor'
    },
    "🏦 Lãi suất liên ngân hàng": {
        'symbols': ['ls_qua_dem_lien_ngan_hang', 'ls_lien_ngan_hang_ky_han_1_tuan', 'ls_lien_ngan_hang_ky_han_2_tuan'],
        'colors': ['#10B981', '#3B82F6', '#EC4899'],  # Green, Blue, Pink
        'unit': '%',
        'title': 'Interbank Interest Rates'
    }
}
```

### Step 2: Create Multi-Series Chart Function (ADD)
Add helper function for grouped charts:

```python
def create_multi_series_chart(
    loader: MacroCommodityLoader,
    symbols: list,
    colors: list,
    days: int,
    unit: str = '%',
    height: int = 450
) -> go.Figure:
    """
    Create multi-series chart with shared Y-axis.

    Args:
        loader: MacroCommodityLoader instance
        symbols: List of canonical symbol names
        colors: List of color hex codes (same length as symbols)
        days: Number of days to filter
        unit: Y-axis unit label
        height: Chart height
    """
    fig = go.Figure()

    for symbol, color in zip(symbols, colors):
        actual_symbol = get_actual_symbol(symbol)
        series = filter_series_by_days(loader.get_series(actual_symbol), days)

        if not series.empty and 'value' in series.columns:
            label = get_label(symbol)
            fig.add_trace(go.Scatter(
                x=series['date'],
                y=series['value'],
                name=label,
                mode='lines',
                line=dict(color=color, width=2.5),
                hovertemplate=f'<b>{label}</b><br>%{{x|%d/%m/%Y}}<br>%{{y:.2f}}{unit}<extra></extra>'
            ))

    # Apply layout
    layout = get_chart_layout(height=height)
    layout['showlegend'] = True
    layout['legend'] = dict(
        orientation='h',
        yanchor='bottom',
        y=1.02,
        xanchor='center',
        x=0.5,
        font=dict(size=11, color='#E8E8E8')
    )
    layout['yaxis']['title'] = unit
    layout['xaxis'] = dict(
        tickformat='%b %Y',
        tickmode='auto',
        nticks=8,
        tickangle=0,
        tickfont=dict(size=10, color='#CBD5E1'),
        showgrid=False,
        zeroline=False,
        showline=True,
        linecolor='rgba(255,255,255,0.2)'
    )
    fig.update_layout(**layout)

    return fig
```

### Step 3: Refactor Macro Tab - Interest Rates (MODIFY lines 272-342)
Replace simple loop with grouped chart logic:

```python
# =============================================
# INTEREST RATES: Grouped multi-series charts
# =============================================
if macro_type in ["💰 Lãi suất huy động", "🏦 Lãi suất liên ngân hàng"]:
    # Find matching group
    group_key = None
    for key in INTEREST_RATE_GROUPS:
        if macro_type.split()[1] in key:  # Match by first words
            group_key = key
            break

    if group_key and group_key in INTEREST_RATE_GROUPS:
        group = INTEREST_RATE_GROUPS[group_key]
        fig_macro = create_multi_series_chart(
            loader=macro_loader,
            symbols=group['symbols'],
            colors=group['colors'],
            days=days,
            unit=group['unit'],
            height=500
        )
        st.plotly_chart(fig_macro, use_container_width=True)

        # Latest values table
        st.markdown("### Latest Values")
        latest_data = []
        for symbol in group['symbols']:
            actual_symbol = get_actual_symbol(symbol)
            series = macro_loader.get_series(actual_symbol)
            if not series.empty and 'value' in series.columns:
                latest = series.iloc[-1]
                latest_data.append({
                    'Indicator': get_label(symbol),
                    'Value': f"{latest['value']:.2f}%",
                    'Date': latest['date'].strftime('%Y-%m-%d') if pd.notna(latest['date']) else '-'
                })

        if latest_data:
            latest_df = pd.DataFrame(latest_data)
            st.markdown(render_styled_table(latest_df), unsafe_allow_html=True)
    else:
        st.info("No data available for selected category")
```

### Step 4: Enhance Exchange Rate Pair Labels (MODIFY lines 98-104)
Update pair definitions with clearer labels:

```python
exchange_dual_axis_pairs = {
    "💱 USD: Chính thức vs Tự do": (
        'ty_gia_usd_trung_tam', 'ty_gia_usd_tu_do_ban_ra',
        'Trung tâm (SBV)', 'Tự do (Thị trường)'
    ),
    "🏦 USD: Ngân hàng vs Tự do": (
        'ty_gia_usd_nhtm_ban_ra', 'ty_gia_usd_tu_do_ban_ra',
        'NHTM bán ra', 'Tự do bán ra'
    ),
    "📊 Tỷ giá: Sàn vs Trần": (
        'ty_gia_san', 'ty_gia_tran',
        'Giá sàn', 'Giá trần'
    ),
}
```

### Step 5: Update Commodity Dual-Axis Pairs (MODIFY lines 384-389)
Verify and enhance commodity pairs:

```python
# Verified working dual-axis commodity pairs
dual_axis_pairs = {
    "🐷 Heo hơi: VN vs Trung Quốc": (
        'pork_vn_wichart', 'pork_china',
        'VND/kg', 'CNY/kg'
    ),
    "🔩 Thép: HRC vs D10": (
        'steel_hrc', 'steel_d10',
        '$/ton', '$/ton'  # Same unit, single axis works
    ),
    "🛢️ Dầu: WTI vs Brent": (
        'oil_wti', 'oil_crude',
        '$/bbl', '$/bbl'  # Same unit
    ),
}
```

### Step 6: Add Chart Type Detection Logic
Modify dual-axis pair rendering to detect same/different units:

```python
# Inside dual-axis pair rendering block
if unit1 == unit2:
    # Same unit - use single Y-axis for better comparison
    fig = go.Figure()
    # Add both traces to same axis
    fig.add_trace(go.Scatter(x=series1['date'], y=series1[value_col1], name=label1, ...))
    fig.add_trace(go.Scatter(x=series2['date'], y=series2[value_col2], name=label2, ...))
else:
    # Different units - use dual Y-axes
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(...), secondary_y=False)
    fig.add_trace(go.Scatter(...), secondary_y=True)
```

## Success Criteria

1. [ ] Deposit rates show 3 lines on single chart with distinct colors
2. [ ] Interbank rates show 3 lines on single chart
3. [ ] Exchange rate pairs show clear spread gap
4. [ ] Commodity VN vs Global pairs use dual-axis where units differ
5. [ ] Legend is readable with all series visible
6. [ ] Colors match codebase design system (purple/cyan/amber)

## Testing Steps

1. Navigate to Macro tab
2. Select "Lãi suất huy động" - verify 3 tenor lines render
3. Select "Lãi suất liên ngân hàng" - verify overnight/1W/2W lines render
4. Select "Tỷ giá USD" - verify spread visible between pair lines
5. Switch to Commodities tab
6. Select "Heo hơi VN vs TQ" - verify dual-axis with VND left, CNY right

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Missing data for some tenors | Medium | Medium | Check series.empty, show warning |
| Color contrast issues | Low | Low | Use tested design palette |
| Legend overflow on mobile | Medium | Low | Use horizontal legend, abbreviate |

## Dependencies

- Phase 1 must be complete (symbol mapping fixes)
- `styles.py` CHART_COLORS dict (line 1248) - already available
