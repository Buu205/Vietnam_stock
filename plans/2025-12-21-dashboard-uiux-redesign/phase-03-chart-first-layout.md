# Phase 3: Chart-First Layout

**Goal:** Maximize chart viewport, reduce whitespace, compact UI elements
**Effort:** 1 day | **Risk:** Low

---

## Current Layout Issues

1. **Excessive padding:** `block-container` has 2.5rem horizontal padding
2. **Large metric cards:** 1.5rem+ padding inside cards
3. **Tall tabs:** Default tab padding too generous
4. **Chart margins:** Plotly charts have extra wrapper padding

---

## CSS Changes to styles.py

### 1. Reduce Block Container Padding

**Replace existing block-container rules (lines 130-134):**

```css
/* ========== CHART-FIRST: TIGHTER CONTAINER ========== */
.block-container {
    padding: 0.5rem 1.5rem 1.5rem 1.5rem !important;  /* Reduced from 2.5rem */
    max-width: 100% !important;  /* Full width, no 1800px cap */
    margin-top: 0 !important;
}

.main .block-container,
.stApp > .main > .block-container {
    padding-top: 0.5rem !important;
    margin-top: 0 !important;
}
```

### 2. Compact Metric Cards

**Replace metric card padding (lines 236-247):**

```css
/* ============================================================
   METRIC CARDS - COMPACT GLASSMORPHISM
   ============================================================ */
[data-testid="stMetric"] {
    background: var(--glass-bg);
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    border: 1px solid var(--glass-border);
    border-radius: 12px;  /* Reduced from 16px */
    padding: 1rem 1.25rem !important;  /* Reduced from 1.5rem 1.75rem */
    transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    position: relative;
    overflow: hidden;
    box-shadow: var(--glass-shadow), var(--glass-inner);
}

/* Smaller metric value */
[data-testid="stMetricValue"] {
    font-family: var(--font-mono) !important;
    font-size: 1.75rem !important;  /* Reduced from 2rem */
    font-weight: 600 !important;
    color: var(--text-white) !important;
    letter-spacing: -0.02em;
}

/* Smaller metric label */
[data-testid="stMetricLabel"] {
    font-size: 0.7rem !important;  /* Reduced from 0.75rem */
    font-weight: 600 !important;
    color: var(--text-secondary) !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;  /* Reduced from 0.1em */
}
```

### 3. Compact Tabs

**Replace tabs section (lines 482-518):**

```css
/* ============================================================
   TABS - COMPACT GLASS SEGMENTED CONTROL
   ============================================================ */
.stTabs [data-baseweb="tab-list"] {
    background: var(--glass-bg);
    backdrop-filter: var(--glass-blur);
    border-radius: 10px;  /* Reduced from 12px */
    padding: 4px;  /* Reduced from 5px */
    gap: 3px;  /* Reduced from 4px */
    border: 1px solid var(--glass-border);
}

.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 6px;  /* Reduced from 8px */
    padding: 0.5rem 1.25rem;  /* Reduced from 0.65rem 1.75rem */
    font-family: var(--font-body);
    font-weight: 500;
    font-size: 0.8rem;  /* Reduced from 0.875rem */
    color: var(--text-secondary);
    transition: all 0.25s ease;
    border: none;
}
```

### 4. Tighter Chart Containers

**Replace chart section (lines 630-656):**

```css
/* ============================================================
   CHARTS - MINIMAL GLASS CONTAINER
   ============================================================ */
.stPlotlyChart {
    background: var(--glass-bg);
    backdrop-filter: var(--glass-blur);
    border-radius: 12px;  /* Reduced from 16px */
    padding: 0.5rem;  /* Reduced from 1rem */
    border: 1px solid var(--glass-border);
    box-shadow: var(--glass-shadow);
    width: 100% !important;
    max-width: 100% !important;
    overflow: hidden;
}

/* Remove extra Plotly wrapper padding */
.stPlotlyChart > div {
    width: 100% !important;
    max-width: 100% !important;
    padding: 0 !important;
}
```

### 5. Compact Headers

**Replace h3 section (lines 194-214):**

```css
/* Section Headers - Compact Tech Style */
h3 {
    font-size: 0.75rem !important;  /* Reduced from 0.8rem */
    font-weight: 600 !important;
    color: var(--text-accent) !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;  /* Reduced from 0.12em */
    margin: 0.75rem 0 0.5rem 0 !important;  /* Reduced from 1rem 0 0.75rem */
    padding-bottom: 0.4rem;  /* Reduced from 0.5rem */
    border-bottom: 1px solid var(--glass-border);
}
```

### 6. Reduce Horizontal Rule Margins

**Replace hr section (lines 793-805):**

```css
hr {
    border: none;
    height: 1px;
    background: linear-gradient(90deg,
        transparent 0%,
        var(--glass-border) 20%,
        var(--purple-primary) 50%,
        var(--glass-border) 80%,
        transparent 100%
    );
    margin: 0.75rem 0 1rem 0;  /* Reduced from 1rem 0 1.25rem */
    opacity: 0.6;
}
```

---

## get_chart_layout() Updates

**File:** styles.py, function `get_chart_layout()` (lines 1085-1145)

**Update margins:**
```python
def get_chart_layout(title: str = "", height: int = 400) -> dict:
    return {
        ...
        'margin': {'l': 40, 'r': 20, 't': 40, 'b': 40, 'pad': 2},  # Reduced from l=50, r=30, t=50, b=50, pad=4
        ...
    }
```

---

## Implementation Steps

1. **Backup styles.py**
   ```bash
   cp WEBAPP/core/styles.py WEBAPP/core/styles.py.bak
   ```

2. **Apply CSS changes**
   - Update block-container padding
   - Update metric card sizing
   - Update tab sizing
   - Update chart container padding
   - Update header margins

3. **Update get_chart_layout()**
   - Reduce Plotly margins

4. **Test**
   - Run `streamlit run WEBAPP/main_app.py`
   - Check all pages render correctly
   - Verify charts have more viewport space
   - Confirm no visual regressions

---

## Before/After Metrics

| Element | Before | After | Savings |
|---------|--------|-------|---------|
| Container padding | 2.5rem (40px) | 1.5rem (24px) | 32px total |
| Metric card padding | 1.5rem | 1rem | 16px |
| Chart wrapper | 1rem | 0.5rem | 16px |
| Tab padding | 0.65rem | 0.5rem | 4.8px |
| **Total vertical savings** | - | - | ~70px |

---

## Validation Checklist
- [ ] Charts use more viewport space
- [ ] Metric cards still readable
- [ ] Tabs still functional and styled
- [ ] No overflow or clipping issues
- [ ] Mobile responsive (768px breakpoint)
- [ ] Dark theme colors unchanged
- [ ] Animations still work

---

## Rollback
```bash
cp WEBAPP/core/styles.py.bak WEBAPP/core/styles.py
streamlit run WEBAPP/main_app.py
```
