# Design System Guide - Vietnam Dashboard

**Version:** 1.0
**Created:** 2025-12-30
**Skills:** UI/UX Pro Max, Frontend Design Pro

---

## Overview

Hướng dẫn áp dụng design system thống nhất cho toàn bộ Vietnam Dashboard.
Dựa trên UI/UX Pro Max skill và Financial Dashboard style.

---

## 1. Icon System

### Location
```
WEBAPP/components/ui/icons.py
```

### Usage

```python
from WEBAPP.components.ui import icon, icon_with_text, icon_box, status_icon
from WEBAPP.components.ui import IconSize, IconColor

# Basic icon
st.markdown(icon("chart-bar", size=24, color="#8B5CF6"), unsafe_allow_html=True)

# Icon with text
st.markdown(icon_with_text("check", "Completed", color="#22C55E"), unsafe_allow_html=True)

# Empty state box
st.markdown(icon_box("inbox", "No data available"), unsafe_allow_html=True)

# Status icon (auto color)
st.markdown(status_icon("buy"), unsafe_allow_html=True)  # Green trending-up
st.markdown(status_icon("sell"), unsafe_allow_html=True)  # Red trending-down
```

### Available Icons (47 total)

| Category | Icons |
|----------|-------|
| **Directional** | arrow-up, arrow-down, arrow-left, arrow-right, chevron-up, chevron-down, trending-up, trending-down |
| **Charts** | chart-bar, chart-pie, chart-line, presentation |
| **Status** | check, check-circle, x-mark, x-circle, exclamation, exclamation-triangle, info, question |
| **Finance** | currency-dollar, banknotes, building-office, scale |
| **Rating** | star, star-solid, thumb-up, thumb-down |
| **Actions** | filter, search, refresh, download, eye, eye-slash |
| **UI** | bars-3, plus, minus, cog, table-cells |
| **Empty** | inbox, document, folder, calendar, clock |

### Icon Sizes

| Size | Value | Use Case |
|------|-------|----------|
| `IconSize.XS` | 16px | Inline text |
| `IconSize.SM` | 20px | Buttons |
| `IconSize.MD` | 24px | Default |
| `IconSize.LG` | 32px | Card headers |
| `IconSize.XL` | 48px | Empty states |

---

## 2. Color Palette

### Primary Colors (From Financial Dashboard Style)

| Token | Hex | Use |
|-------|-----|-----|
| `#8B5CF6` | Purple | Primary accent, headers |
| `#00C9AD` | Teal | Secondary accent, positive highlight |
| `#22C55E` | Green | Success, profit, buy |
| `#EF4444` | Red | Error, loss, sell |
| `#F59E0B` | Amber | Warning, hold, caution |
| `#3B82F6` | Blue | Info, links |

### Neutral Colors

| Token | Hex | Use |
|-------|-----|-----|
| `#1A1625` | Dark purple | Background |
| `#E8E8E8` | Light gray | Primary text |
| `#94A3B8` | Muted gray | Secondary text |
| `#64748B` | Slate | Disabled text |

### Semantic Colors

```python
# Import from icons module
from WEBAPP.components.ui import IconColor

IconColor.SUCCESS  # #22C55E
IconColor.WARNING  # #F59E0B
IconColor.ERROR    # #EF4444
IconColor.INFO     # #3B82F6
IconColor.PRIMARY  # #8B5CF6
IconColor.SECONDARY  # #00C9AD
IconColor.MUTED    # #94A3B8
```

---

## 3. Table Design Patterns

### Unified Table Pattern

```python
# Reference: WEBAPP/components/tables/unified_forecast_table.py

UNIFIED_TABLE_STYLE = """
<style>
.unified-table {
    width: 100%;
    border-collapse: collapse;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    background: rgba(26, 22, 37, 0.5);
    border-radius: 8px;
}

.unified-table th {
    background: rgba(139, 92, 246, 0.15);  /* Purple tint */
    color: #E8E8E8;
    padding: 10px 8px;
    font-weight: 600;
    font-size: 11px;
}

.unified-table td {
    padding: 8px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    color: #94A3B8;
}

.unified-table tr:hover {
    background: rgba(139, 92, 246, 0.1);
    cursor: pointer;
}
</style>
"""
```

### Column Group Colors

| Group | Background | Border |
|-------|------------|--------|
| **Core** | `rgba(139, 92, 246, 0.15)` | Purple |
| **Valuation** | `rgba(0, 155, 135, 0.15)` | Teal |
| **Earnings** | `rgba(255, 193, 50, 0.15)` | Amber |
| **Extended** | `rgba(59, 130, 246, 0.15)` | Blue |

### Sticky Columns Pattern

```css
/* Z-Index Scale: z-0 base, z-10 sticky cols, z-20 header, z-30 corners */

/* Sticky first column */
.table th:nth-child(1),
.table td:nth-child(1) {
    position: sticky;
    left: 0;
    background: rgba(26, 22, 37, 0.98);
    z-index: 10;
}

/* Sticky second column with shadow */
.table th:nth-child(2),
.table td:nth-child(2) {
    position: sticky;
    left: 70px;
    background: rgba(26, 22, 37, 0.98);
    z-index: 10;
    box-shadow: 2px 0 8px rgba(0, 0, 0, 0.3);
}

/* Corner cells (header + sticky) */
.table thead th:nth-child(1),
.table thead th:nth-child(2) {
    z-index: 30;
}
```

---

## 4. Badge Patterns

### Rating Badge

```python
def format_rating_badge(rating: str) -> str:
    colors = {
        'STRONG BUY': ('rgba(0, 201, 173, 0.2)', '#00C9AD', 'rgba(0, 201, 173, 0.4)'),
        'BUY': ('rgba(34, 197, 94, 0.2)', '#22C55E', 'rgba(34, 197, 94, 0.4)'),
        'HOLD': ('rgba(255, 193, 50, 0.2)', '#FFC132', 'rgba(255, 193, 50, 0.4)'),
        'SELL': ('rgba(249, 115, 22, 0.2)', '#F97316', 'rgba(249, 115, 22, 0.4)'),
        'STRONG SELL': ('rgba(239, 68, 68, 0.2)', '#EF4444', 'rgba(239, 68, 68, 0.4)'),
    }
    bg, text, border = colors.get(rating, ('rgba(100, 116, 139, 0.2)', '#94A3B8', 'rgba(100, 116, 139, 0.4)'))
    return f'''<span style="
        display: inline-block;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.7rem;
        background: {bg};
        color: {text};
        border: 1px solid {border};
    ">{rating}</span>'''
```

### Consensus Badge

```python
def format_consensus_badge(status: str) -> str:
    badges = {
        'ALIGNED': ('[=]', '#00C9AD'),    # Teal
        'BSC_BULL': ('[B]', '#3B82F6'),   # Blue
        'VCI_BULL': ('[V]', '#F59E0B'),   # Orange
        'DIVERGENT': ('[!]', '#EF4444'),  # Red
    }
    label, color = badges.get(status, ('[-]', '#94A3B8'))
    return f'<span style="color: {color}; font-weight: 600;">{label} {status}</span>'
```

---

## 5. Empty State Pattern

```python
from WEBAPP.components.ui import icon_box

# Standard empty state
st.markdown(icon_box("inbox", "No data available"), unsafe_allow_html=True)

# With custom colors
st.markdown(icon_box(
    "chart-bar",
    "No chart data for this period",
    icon_color="#F59E0B",
    bg_color="rgba(245, 158, 11, 0.08)",
    border_color="rgba(245, 158, 11, 0.2)"
), unsafe_allow_html=True)
```

---

## 6. Card Patterns

### Metric Card

```python
def metric_card(title: str, value: str, delta: str = None, icon_name: str = None) -> str:
    from WEBAPP.components.ui import icon, IconColor

    icon_html = icon(icon_name, size=24, color=IconColor.PRIMARY) if icon_name else ""
    delta_html = f'<div style="color: {"#22C55E" if delta.startswith("+") else "#EF4444"}; font-size: 0.85rem;">{delta}</div>' if delta else ""

    return f'''
    <div style="
        background: rgba(26, 22, 37, 0.8);
        border: 1px solid rgba(139, 92, 246, 0.2);
        border-radius: 12px;
        padding: 16px;
        cursor: pointer;
        transition: all 0.2s ease;
    ">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
            {icon_html}
            <span style="color: #94A3B8; font-size: 0.85rem;">{title}</span>
        </div>
        <div style="font-size: 1.5rem; font-weight: 700; color: #E8E8E8;">{value}</div>
        {delta_html}
    </div>
    '''
```

### Achievement Card (Clickable)

```python
def achievement_card(
    label: str,
    count: int,
    threshold: str,
    status: str,  # 'revise_up', 'on_track', 'revise_down'
    is_active: bool = False
) -> str:
    colors = {
        'revise_up': ('#22C55E', 'rgba(34, 197, 94, 0.1)', 'rgba(34, 197, 94, 0.4)'),
        'on_track': ('#8B5CF6', 'rgba(139, 92, 246, 0.1)', 'rgba(139, 92, 246, 0.4)'),
        'revise_down': ('#EF4444', 'rgba(239, 68, 68, 0.1)', 'rgba(239, 68, 68, 0.4)'),
    }
    text, bg, border = colors.get(status, ('#94A3B8', 'transparent', 'rgba(148, 163, 184, 0.2)'))

    active_style = f"background: {bg};" if is_active else ""

    return f'''
    <div style="
        background: rgba(26, 22, 37, 0.8);
        border: 1px solid {border if is_active else 'rgba(255, 255, 255, 0.1)'};
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s ease;
        {active_style}
    ">
        <div style="color: {text}; font-size: 2rem; font-weight: 700;">{count}</div>
        <div style="color: #94A3B8; font-size: 0.85rem;">{label}</div>
        <div style="color: #64748B; font-size: 0.75rem; margin-top: 4px;">{threshold}</div>
    </div>
    '''
```

---

## 7. Typography

### Font Stack

```css
/* Monospace for data */
font-family: 'JetBrains Mono', 'SF Mono', Menlo, Monaco, monospace;

/* Sans-serif for UI */
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
```

### Font Sizes

| Token | Size | Use |
|-------|------|-----|
| `2xs` | 10px | Micro labels |
| `xs` | 11px | Table headers |
| `sm` | 12px | Table body |
| `base` | 14px | Body text |
| `lg` | 16px | Section headers |
| `xl` | 20px | Page titles |
| `2xl` | 24px | Hero numbers |

---

## 8. Rules Summary (UI/UX Pro Max)

### [+] DO

- Use SVG icons from `WEBAPP/components/ui/icons`
- Use consistent color tokens from design system
- Use sticky columns for wide tables
- Use z-index scale: 10, 20, 30
- Use `cursor: pointer` for clickable elements
- Use smooth transitions (200ms)

### [-] DON'T

- Use emojis as icons (use SVG)
- Hardcode colors (use tokens)
- Use scale transforms on hover (causes layout shift)
- Mix icon sizes randomly
- Skip empty states

---

## 9. Migration Checklist

Apply design system to each dashboard page:

### Forecast Dashboard (Current)
- [x] unified_forecast_table.py - sticky columns, z-index
- [ ] Tab 0: BSC Universal - rating badges with icons
- [ ] Tab 1: Sector - valuation matrix
- [ ] Tab 2: Achievement - clickable cards
- [ ] Tab 3: Consensus - consensus badges

### Technical Dashboard
- [ ] market_overview.py - migrate to icon helper
- [ ] sector_rotation.py - migrate to icon helper
- [ ] technical_dashboard.py - migrate empty state icons

### Other Dashboards
- [ ] Company Dashboard
- [ ] Bank Dashboard
- [ ] Sector Dashboard
- [ ] FX Commodities Dashboard
- [ ] Security Dashboard

---

## 10. Quick Reference

### Import Pattern

```python
# Icons
from WEBAPP.components.ui import icon, icon_with_text, icon_box
from WEBAPP.components.ui import status_icon, rating_icon, consensus_icon
from WEBAPP.components.ui import IconSize, IconColor

# Render in Streamlit
st.markdown(icon("chart-bar"), unsafe_allow_html=True)
```

### Common Use Cases

```python
# Positive value
st.markdown(icon_with_text("arrow-up", "+12.5%", color=IconColor.SUCCESS), unsafe_allow_html=True)

# Negative value
st.markdown(icon_with_text("arrow-down", "-5.2%", color=IconColor.ERROR), unsafe_allow_html=True)

# Buy rating
st.markdown(status_icon("buy"), unsafe_allow_html=True)

# Empty state
st.markdown(icon_box("inbox", "No data for this period"), unsafe_allow_html=True)

# Consensus status
st.markdown(consensus_icon("ALIGNED"), unsafe_allow_html=True)
```

---

**End of Design System Guide**
