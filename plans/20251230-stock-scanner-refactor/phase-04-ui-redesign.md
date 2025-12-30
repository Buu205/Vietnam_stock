# Phase 4: UI Redesign - Split Tables

**Priority:** P1 (High)
**Status:** Pending
**Estimated Changes:** ~200 lines

## Design System

### Style: Dark Mode (OLED) + Fintech Terminal

Based on UI/UX Pro Max analysis:

| Element | Value |
|---------|-------|
| Background | `#0F172A` (slate-900) |
| Card BG | `#1A1625` (custom dark purple) |
| Primary | `#8B5CF6` (violet-500) |
| Buy/MUA | `#10B981` (emerald-500) |
| Sell/BÁN | `#EF4444` (red-500) |
| Text Primary | `#F8FAFC` (slate-50) |
| Text Secondary | `#94A3B8` (slate-400) |
| Border | `#334155` (slate-700) |

### Typography

| Element | Font | Size | Weight |
|---------|------|------|--------|
| Table Header | DM Sans | 0.7rem | 600 |
| Ticker Symbol | JetBrains Mono | 0.85rem | 600 |
| Pattern Name | DM Sans | 0.8rem | 500 |
| Score Number | JetBrains Mono | 0.85rem | 700 |

---

## Layout Design

### Split Tables Layout

```
┌────────────────────────────────────────────────────────────────────────┐
│  [Quick Filters: Search | Sector | Days]                               │
├────────────────────────────────────────────────────────────────────────┤
│  [Advanced Filters: Score ≥50 | GTGD ≥2 tỷ]                           │
├─────────────────────────────┬──────────────────────────────────────────┤
│                             │                                          │
│  ┌─────────────────────────┐│  ┌─────────────────────────────────────┐ │
│  │ 🟢 TÍN HIỆU MUA (125)   ││  │ 🔴 TÍN HIỆU BÁN (48)               │ │
│  ├─────────────────────────┤│  ├─────────────────────────────────────┤ │
│  │ MÃ    │ MẪU HÌNH │ ĐIỂM ││  │ MÃ    │ MẪU HÌNH │ ĐIỂM           │ │
│  ├───────┼──────────┼──────┤│  ├───────┼──────────┼─────────────────┤ │
│  │ TCI   │ morning  │ ████ ││  │ HLD   │ hanging  │ ████            │ │
│  │       │ _star    │ 85   ││  │       │ _man     │ 66              │ │
│  ├───────┼──────────┼──────┤│  ├───────┼──────────┼─────────────────┤ │
│  │ FPT   │ hammer   │ ███  ││  │ VIC   │ shooting │ ███             │ │
│  │       │          │ 72   ││  │       │ _star    │ 62              │ │
│  └─────────────────────────┘│  └─────────────────────────────────────┘ │
│                             │                                          │
└─────────────────────────────┴──────────────────────────────────────────┘
```

### Compact Table Design (3 Columns Only)

| Column | Width | Content |
|--------|-------|---------|
| MÃ | 60px | Ticker symbol (bold, white) |
| MẪU HÌNH | flex | Pattern name (purple accent) |
| ĐIỂM | 100px | Progress bar + score number |

**Removed columns:** Date, Giải thích, Hành động (simplified)

---

## Component Specifications

### 1. Table Header Card

```html
<!-- MUA Header -->
<div style="
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(16, 185, 129, 0.05) 100%);
    border: 1px solid rgba(16, 185, 129, 0.3);
    border-radius: 12px 12px 0 0;
    padding: 12px 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
">
    <span style="color: #10B981; font-weight: 600; font-size: 0.85rem;">
        TÍN HIỆU MUA
    </span>
    <span style="
        background: rgba(16, 185, 129, 0.2);
        color: #10B981;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-family: 'JetBrains Mono', monospace;
    ">125</span>
</div>
```

### 2. Compact Table Row

```html
<tr style="background: rgba(26, 22, 37, 0.6); transition: all 0.15s;">
    <!-- Ticker -->
    <td style="
        padding: 10px 12px;
        color: #FFFFFF;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
    ">TCI</td>

    <!-- Pattern -->
    <td style="
        padding: 10px 12px;
        color: #C4B5FD;
        font-size: 0.8rem;
    ">morning_star</td>

    <!-- Score with Progress Bar -->
    <td style="padding: 10px 12px;">
        <div style="display: flex; align-items: center; gap: 8px;">
            <div style="
                flex: 1;
                height: 6px;
                background: rgba(100,116,139,0.2);
                border-radius: 3px;
                overflow: hidden;
            ">
                <div style="
                    width: 85%;
                    height: 100%;
                    background: linear-gradient(90deg, #10B981, #22C55E);
                    border-radius: 3px;
                "></div>
            </div>
            <span style="
                color: #22C55E;
                font-weight: 700;
                font-size: 0.85rem;
                min-width: 24px;
                text-align: right;
                font-family: 'JetBrains Mono', monospace;
            ">85</span>
        </div>
    </td>
</tr>
```

### 3. Score Progress Bar Colors

| Score Range | Color | Gradient |
|-------------|-------|----------|
| 80-100 | Green | `#10B981 → #22C55E` |
| 60-79 | Cyan | `#06B6D4 → #22D3EE` |
| 45-59 | Purple | `#8B5CF6 → #A78BFA` |
| <45 | Gray | `#64748B → #94A3B8` |

---

## Implementation

### File: `WEBAPP/pages/technical/components/stock_scanner.py`

### New Function: `_render_split_tables()`

```python
def _render_split_tables(signals: pd.DataFrame) -> None:
    """Render MUA and BÁN tables side by side."""

    # Split by direction
    buy_signals = signals[signals['direction'].isin(['BUY', 'BULLISH'])].copy()
    sell_signals = signals[signals['direction'].isin(['SELL', 'BEARISH'])].copy()

    # Sort by strength descending
    buy_signals = buy_signals.sort_values('strength', ascending=False)
    sell_signals = sell_signals.sort_values('strength', ascending=False)

    # Limit to top 50 each
    buy_signals = buy_signals.head(50)
    sell_signals = sell_signals.head(50)

    # Two columns layout
    col1, col2 = st.columns(2)

    with col1:
        _render_signal_table_compact(
            buy_signals,
            title="TÍN HIỆU MUA",
            accent_color="#10B981",
            is_buy=True
        )

    with col2:
        _render_signal_table_compact(
            sell_signals,
            title="TÍN HIỆU BÁN",
            accent_color="#EF4444",
            is_buy=False
        )
```

### New Function: `_render_signal_table_compact()`

```python
def _render_signal_table_compact(
    df: pd.DataFrame,
    title: str,
    accent_color: str,
    is_buy: bool = True
) -> None:
    """Render compact signal table with progress bars."""

    count = len(df)

    # Header
    header_bg = f"rgba({_hex_to_rgb(accent_color)}, 0.15)"
    header_border = f"rgba({_hex_to_rgb(accent_color)}, 0.3)"

    header_html = f'''
    <div style="
        background: linear-gradient(135deg, {header_bg} 0%, rgba(0,0,0,0) 100%);
        border: 1px solid {header_border};
        border-radius: 12px 12px 0 0;
        padding: 12px 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    ">
        <span style="color: {accent_color}; font-weight: 600; font-size: 0.85rem;">
            {title}
        </span>
        <span style="
            background: rgba({_hex_to_rgb(accent_color)}, 0.2);
            color: {accent_color};
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-family: 'JetBrains Mono', monospace;
        ">{count}</span>
    </div>
    '''

    # Table
    table_html = '''
    <div style="
        background: rgba(26, 22, 37, 0.8);
        border: 1px solid rgba(255,255,255,0.08);
        border-top: none;
        border-radius: 0 0 12px 12px;
        max-height: 500px;
        overflow-y: auto;
    ">
    <table style="width: 100%; border-collapse: collapse;">
    <thead>
        <tr style="background: rgba(139, 92, 246, 0.1);">
            <th style="padding: 10px 12px; text-align: left; color: #8B5CF6; font-size: 0.7rem; font-weight: 600; text-transform: uppercase;">Mã</th>
            <th style="padding: 10px 12px; text-align: left; color: #8B5CF6; font-size: 0.7rem; font-weight: 600; text-transform: uppercase;">Mẫu hình</th>
            <th style="padding: 10px 12px; text-align: right; color: #8B5CF6; font-size: 0.7rem; font-weight: 600; text-transform: uppercase;">Điểm</th>
        </tr>
    </thead>
    <tbody>
    '''

    for _, row in df.iterrows():
        symbol = row.get('symbol', '-')
        pattern = row.get('type_label', row.get('pattern_name', '-'))
        strength = row.get('strength', 0)
        if strength <= 1:
            strength = int(strength * 100)

        # Progress bar color
        bar_color = _get_score_gradient(strength, is_buy)
        text_color = _get_score_text_color(strength, is_buy)

        row_html = f'''
        <tr style="background: rgba(26, 22, 37, 0.6); transition: background 0.15s;"
            onmouseover="this.style.background='rgba(139, 92, 246, 0.1)'"
            onmouseout="this.style.background='rgba(26, 22, 37, 0.6)'">
            <td style="padding: 10px 12px; color: #FFFFFF; font-weight: 600; font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; border-bottom: 1px solid rgba(255,255,255,0.05);">
                {symbol}
            </td>
            <td style="padding: 10px 12px; color: #C4B5FD; font-size: 0.8rem; border-bottom: 1px solid rgba(255,255,255,0.05);">
                {pattern}
            </td>
            <td style="padding: 10px 12px; border-bottom: 1px solid rgba(255,255,255,0.05);">
                <div style="display: flex; align-items: center; gap: 8px; justify-content: flex-end;">
                    <div style="flex: 1; max-width: 60px; height: 6px; background: rgba(100,116,139,0.2); border-radius: 3px; overflow: hidden;">
                        <div style="width: {strength}%; height: 100%; background: {bar_color}; border-radius: 3px;"></div>
                    </div>
                    <span style="color: {text_color}; font-weight: 700; font-size: 0.85rem; min-width: 24px; text-align: right; font-family: 'JetBrains Mono', monospace;">
                        {strength}
                    </span>
                </div>
            </td>
        </tr>
        '''
        table_html += row_html

    table_html += '</tbody></table></div>'

    st.html(header_html + table_html)


def _hex_to_rgb(hex_color: str) -> str:
    """Convert hex to RGB string for rgba()."""
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return f"{r}, {g}, {b}"


def _get_score_gradient(score: int, is_buy: bool) -> str:
    """Get gradient color based on score."""
    if score >= 80:
        return "linear-gradient(90deg, #10B981, #22C55E)" if is_buy else "linear-gradient(90deg, #EF4444, #F87171)"
    elif score >= 60:
        return "linear-gradient(90deg, #06B6D4, #22D3EE)"
    elif score >= 45:
        return "linear-gradient(90deg, #8B5CF6, #A78BFA)"
    else:
        return "linear-gradient(90deg, #64748B, #94A3B8)"


def _get_score_text_color(score: int, is_buy: bool) -> str:
    """Get text color based on score."""
    if score >= 80:
        return "#22C55E" if is_buy else "#F87171"
    elif score >= 60:
        return "#22D3EE"
    elif score >= 45:
        return "#A78BFA"
    else:
        return "#94A3B8"
```

---

## Implementation Steps

- [ ] Add helper functions (`_hex_to_rgb`, `_get_score_gradient`, `_get_score_text_color`)
- [ ] Add `_render_signal_table_compact()` function
- [ ] Add `_render_split_tables()` function
- [ ] Update `render_stock_scanner()` to use split tables
- [ ] Test responsive layout on different screen sizes
- [ ] Verify hover states work correctly

---

## Success Criteria

- [ ] MUA and BÁN tables side by side (50/50 width)
- [ ] Tables have max-height with scroll
- [ ] Progress bars colored by score range
- [ ] Hover effect on rows
- [ ] Count badge in header
- [ ] Compact 3-column design (no date, no action button)

---

## Mobile Responsive (Future)

For mobile, consider stacking tables vertically:

```python
# Mobile detection (future enhancement)
if st.session_state.get('is_mobile', False):
    # Stack vertically
    _render_signal_table_compact(buy_signals, ...)
    _render_signal_table_compact(sell_signals, ...)
else:
    # Side by side
    col1, col2 = st.columns(2)
    ...
```

---

## Visual Preview

```
┌─────────────────────────┐ ┌─────────────────────────┐
│ TÍN HIỆU MUA      [125] │ │ TÍN HIỆU BÁN       [48] │
├───────┬─────────┬───────┤ ├───────┬─────────┬───────┤
│ MÃ    │MẪU HÌNH │ ĐIỂM  │ │ MÃ    │MẪU HÌNH │ ĐIỂM  │
├───────┼─────────┼───────┤ ├───────┼─────────┼───────┤
│ TCI   │morning_ │███ 85 │ │ HLD   │hanging_ │███ 66 │
│ FPT   │hammer   │██▓ 72 │ │ VIC   │shooting │██▓ 62 │
│ VCB   │engulf   │██░ 68 │ │ MWG   │evening  │██░ 58 │
│ HPG   │inverted │█▓░ 54 │ │ DXG   │engulf   │█▓░ 52 │
│ ...   │...      │...    │ │ ...   │...      │...    │
└───────┴─────────┴───────┘ └───────┴─────────┴───────┘
     Green bars                  Red bars
```
