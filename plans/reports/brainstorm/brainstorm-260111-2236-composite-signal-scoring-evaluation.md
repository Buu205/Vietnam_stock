# Brainstorm: Composite Signal Scoring Logic Evaluation

**Date:** 2025-01-11
**Type:** Plan Review & UI/UX Analysis
**Status:** Complete

---

## 1. Problem Statement

User yêu cầu đánh giá plan `composite_signal_scoring_logic.md` về:
1. Pros & Cons của logic scoring 6 factors
2. Các điểm chưa chặt chẽ trong logic
3. UI hiện tại không khớp với phần Score Breakdown của plan
4. Đề xuất cải thiện UI theo flow: Nhóm tín hiệu → Chọn mã → Chi tiết điểm

---

## 2. Logic Analysis: Composite Signal Scoring

### 2.1 Overall Assessment

**Scoring System (100 pts total):**

| Factor | Weight | Logic Quality |
|--------|--------|---------------|
| Candlestick Pattern | 15% | ✅ Solid (tiered by reliability) |
| VSA (Volume Spread Analysis) | 25% | ⚠️ Complex, có edge cases |
| Trend Alignment | 20% | ✅ Clear matrix |
| S/R Proximity | 15% | ⚠️ Fib calculation cần validate |
| RS Rating | 15% | ✅ Good (percentile-based) |
| Liquidity | 10% | ✅ Simple, effective |

### 2.2 PROS

1. **Multi-dimensional approach**: 6 factors cover technical, relative strength, và liquidity
2. **Clear weight distribution**: VSA (25%) + Trend (20%) = 45% - đúng với quan điểm "follow the smart money + trend"
3. **Built-in conflict detection**: VSA alignment bonus/penalty (-5 to +3) penalize conflicting signals
4. **Quality tiering**: EXCELLENT/GOOD/MODERATE/WEAK/AVOID với thresholds rõ ràng
5. **Direction classification**: BUY/SELL/PULLBACK/BOUNCE giúp trader hiểu context
6. **Vietnamese action labels**: MUA MẠNH, CÂN NHẮC MUA, CHỜ XÁC NHẬN - dễ hiểu với user VN

### 2.3 CONS & Logic Gaps

#### Gap 1: VSA Score Can Be Negative (Clipped)

```python
# close_score có thể = -2, vsa_bonus có thể = -5
# raw_total = volume_score + spread_score + close_score + vsa_bonus
# → Có thể = 10 + 5 + (-2) + (-5) = 8 → clip to 0-25
```

**Issue:** Khi signal bị conflict mạnh, VSA score = 8/25 (32%) vẫn còn cao. Nên có multiplier penalty thay vì cộng trừ tuyến tính.

**Recommendation:** Thêm conflict flag và multiplier:
```python
if vsa_bonus < 0:
    raw_total = raw_total * 0.7  # 30% penalty for conflict
```

#### Gap 2: S/R Proximity Depends on Fib Calculation Quality

**Issue:** Fib retracement từ 30-day range không always meaningful:
- Sideways market: Fib levels cluster (không có swing rõ)
- Strong trend: 23.6% và 38.2% có thể quá xa để làm support

**Recommendation:** Add validation:
- Skip Fib nếu `fib_range < ATR * 5` (quá hẹp)
- Prefer swing high/low over Fib khi conflict

#### Gap 3: RS Rating 5-Day Momentum Có Noise

**Issue:** RS rating thay đổi 5d ago có thể do market-wide rotation, không phải stock-specific strength.

**Recommendation:**
- Add sector-relative RS (stock RS vs sector RS)
- Weight momentum score thấp hơn (1 pt thay vì 3 pts max)

#### Gap 4: Liquidity Score Favors Large Caps Too Much

**Issue:** Trading value ≥ 100 tỷ = 8/8 pts. Điều này favor VN30 quá mức, mid-cap có signal tốt nhưng bị penalty.

**Recommendation:**
- Lower threshold: 50 tỷ = 8 pts (was 100 tỷ)
- Add sector-adjusted liquidity (bank sector naturally higher liquidity)

#### Gap 5: Missing Time-of-Day Context

**Issue:** Signal vào ATO/ATC session khác vs mid-session. ATO breakout kèm volume spike đáng tin hơn.

**Recommendation:** (Future enhancement) Add session_type factor.

#### Gap 6: Pattern Score Doesn't Account for Context

**Issue:** Morning star có 15 pts regardless of where it appears. Morning star SAU downtrend mạnh hơn morning star trong sideways.

**Recommendation:** Add context multiplier:
```python
if pattern in ['morning_star', 'hammer'] and trend == 'STRONG_DOWN':
    pattern_score *= 1.2  # Bonus for reversal in strong trend
```

### 2.4 Expected Score Distribution Reality Check

Plan claims:
| Score Range | Expected % |
|-------------|------------|
| 90-100 | 2-5% |
| 75-89 | 10-15% |
| 60-74 | 25-30% |

**Reality check cần:** Với current signals (screenshot shows nhiều score = 100), distribution này chưa đạt. Cần validate sau khi implement.

---

## 3. UI Analysis: Current vs Proposed

### 3.1 Current UI (from stock_scanner.py code analysis)

**Layout Structure:**
```
┌─────────────────────────────────────────────────────────────────┐
│ [Single Stock Analysis] - Input ticker, show trend + S/R        │
├─────────────────────────────────────────────────────────────────┤
│ [Quick Filters] - Tìm mã, Ngành, Xu hướng, Thời gian            │
├─────────────────────────────────────────────────────────────────┤
│ [Advanced Filters] - Loại tín hiệu, Hướng, Điểm min, GTGD       │
├─────────────────────────────────────────────────────────────────┤
│ [Signal Summary] - st.metric: Tổng | MUA | BÁN | CHỜ            │
├─────────────────────────────────────────────────────────────────┤
│  MUA (Trend-aligned)  │  BÁN (Trend-aligned)  │  PULLBACK/BOUNCE │
│  ─────────────────────  ─────────────────────   ────────────────  │
│  MÃ  Trend  MẪU HÌNH  ĐIỂM │ MÃ  Trend MẪU HÌNH ĐIỂM │ ...      │
│  BID  ⬆⬆   Breakout↑  100  │ CEO  ⬇⬇  Breakdown↓ 100 │ ...      │
│  PHR  ⬆⬆   Breakout↑  100  │ HTN  ⬇⬇  Breakdown↓ 100 │ ...      │
│  ...                       │ ...                      │          │
├─────────────────────────────────────────────────────────────────┤
│ [Hướng dẫn giải thích mẫu hình] - Expander                      │
└─────────────────────────────────────────────────────────────────┘
```

**Table Columns (from `_render_signal_table_compact`):**
- Mã (ticker) - monospace font
- Trend - icon badges (⬆⬆, ⬆, ↔, ⬇, ⬇⬇)
- Mẫu hình (pattern name) - e.g., "Breakout ↑", "engulfing"
- Điểm (score) - progress bar + number

**Current Score Source:**
```python
strength = row.get('strength', 0)
if strength <= 1:
    strength = int(strength * 100)  # Convert 0-1 to 0-100
```
→ Score = `strength` từ signals data = pattern strength, **KHÔNG** phải composite 6-factor score

**Issues Identified:**

| Issue | Detail | Impact |
|-------|--------|--------|
| Score = pattern strength | Breakout/Breakdown luôn = 100 | Không phân biệt được signal quality |
| Không có composite scoring | 6 factors trong plan chưa implement | User không biết WHY signal tốt/xấu |
| Không có breakdown | Chỉ hiện tổng điểm | Thiếu transparency |
| Single Stock tách biệt | Phải nhập ticker riêng để xem S/R | UX fragmented |
| Click không có action | Table chỉ view-only | Miss opportunity cho detail view |

### 3.2 Plan's Proposed UI (from Appendix)

```
┌─────────────────────────────────────────────────────────┐
│ VCB - Morning Star                      SCORE: 87/100   │
├─────────────────────────────────────────────────────────┤
│  Pattern    ████████████████░░░░  15/15                │
│  VSA        ████████████████████░░░░░  20/25           │
│  Trend      ████████████████░░░░  17/20                │
│  S/R        ████████████░░░░░░░░  12/15                │
│  RS Rating  █████████████░░░░░░░  13/15                │
│  Liquidity  ████████████████████  10/10                │
│                                                         │
│  Quality: EXCELLENT ⭐⭐⭐⭐⭐                            │
│  Action: MUA MẠNH                                       │
│                                                         │
│  VSA: Demand Coming In (Vol 2.3x, Close High)          │
│  RS: 85 (+7 vs 5d ago) - Top 15%                       │
│  S/R: 2.1% above support, R:R = 2.5:1                  │
└─────────────────────────────────────────────────────────┘
```

**This is DETAIL VIEW** - không phải overview list.

### 3.3 Mismatch Analysis

| Aspect | Current UI | Plan Proposed | Gap |
|--------|------------|---------------|-----|
| Overview | 3-column lists | Not specified | Need both |
| Score source | Pattern strength | 6-factor composite | Missing |
| Breakdown | None | 6-bar breakdown | Missing |
| Detail trigger | None | On select | Missing |
| VSA info | None | Signal name + details | Missing |
| S/R info | In Single Stock only | Per-signal | Partial |

---

## 4. UI/UX Recommendations

### 4.1 Proposed Information Architecture

```
┌─────────────────────────────────────────────────────────┐
│ [Level 1: Signal Overview - 3 columns]                 │
│                                                         │
│  MUA (30)  │  BÁN (30)  │  PULLBACK (28)               │
│  ─────────   ─────────    ──────────────               │
│  VCB ⬆⬆ 87  │  CEO ⬇⬇ 85  │  KCB ⬆⬆ engulf 62       │
│  BID ⬆  82  │  HTN ⬇⬇ 78  │  GSP ⬆  shooting 61      │
│  ...        │  ...        │  ...                        │
│                                                         │
│  [Click on ticker → expands detail panel below]        │
│                                                         │
├─────────────────────────────────────────────────────────┤
│ [Level 2: Signal Detail - expanded on select]          │
│                                                         │
│  ┌─ VCB - Breakout ↑ ────────────────── SCORE: 87/100 │
│  │                                                      │
│  │  Pattern   ██████████████░░  14/15                  │
│  │  VSA       ████████████████░░░░░  18/25             │
│  │  Trend     ████████████████  20/20                  │
│  │  S/R       ██████████░░░░░░  10/15                  │
│  │  RS        █████████████░░░  13/15                  │
│  │  Liquidity ████████████████  10/10                  │
│  │                                                      │
│  │  VSA: Demand Coming In (Vol 2.3x, Close High)       │
│  │  Nearest Support: 82,000 (Fib 38.2%) -2.1%         │
│  │  Target Resistance: 88,500 (Swing High) +5.7%      │
│  │  R:R = 2.7:1                                        │
│  │                                                      │
│  │  [Action] MUA MẠNH ✅                               │
│  └──────────────────────────────────────────────────── │
└─────────────────────────────────────────────────────────┘
```

### 4.2 Design Specifications (Financial Dashboard Style)

#### Color Palette

| Element | Light Mode | Dark Mode (Current) |
|---------|------------|---------------------|
| BUY/Profit | #22C55E | #10B981 |
| SELL/Loss | #EF4444 | #F87171 |
| Neutral/Hold | #64748B | #94A3B8 |
| Accent (Primary) | #8B5CF6 | #A78BFA |
| Background | #FFFFFF | #1A1625 |
| Card BG | #F8FAFC | rgba(26, 22, 37, 0.8) |

#### Progress Bar Breakdown

```python
# Factor score bar colors (gradient by contribution)
FACTOR_COLORS = {
    'candlestick': '#A78BFA',  # Purple (pattern)
    'vsa': '#22D3EE',          # Cyan (volume)
    'trend': '#10B981',        # Green (direction)
    'sr': '#F59E0B',           # Amber (price level)
    'rs': '#8B5CF6',           # Purple (relative)
    'liquidity': '#64748B',    # Gray (secondary)
}
```

#### Interaction Flow

1. **Default:** Show 3-column overview with composite scores
2. **Hover:** Highlight row, show mini tooltip with quality label
3. **Click:** Expand detail panel below table (NOT modal)
4. **Selected state:** Row highlighted, detail panel visible
5. **Click another:** Collapse previous, expand new

### 4.3 Component Breakdown

#### New Component: ScoreBreakdownCard

```python
def render_score_breakdown(signal_data: dict) -> str:
    """
    Render 6-factor score breakdown card.

    signal_data contains:
    - composite_score: int (0-100)
    - quality: str (EXCELLENT/GOOD/MODERATE/WEAK)
    - candlestick_score: int (0-15)
    - vsa_score: int (0-25)
    - trend_score: int (0-20)
    - sr_score: int (0-15)
    - rs_score: int (0-15)
    - liquidity_score: int (0-10)
    - vsa_details: dict
    - sr_details: dict
    """
```

#### Modified: _render_split_tables()

Add click handler và detail expansion:
- Use `st.session_state.selected_signal` to track selection
- Render detail card below columns when selected

### 4.4 Two UI Options

#### Option A: Click-to-Expand (Recommended)

```
┌─────────────────────────────────────────────────────────────────┐
│  MUA (30)           │  BÁN (30)          │  PULLBACK (28)       │
│  ─────────────────────────────────────────────────────────────  │
│  VCB ⬆⬆ Breakout 87 │  CEO ⬇⬇ Breakdown 85 │ KCB ⬆⬆ engulf 62  │
│  BID ⬆  Breakout 82 │  HTN ⬇⬇ Breakdown 78 │ GSP ⬆  shooting 61 │
│  [CLICK VCB]        │                       │                    │
├─────────────────────────────────────────────────────────────────┤
│ ▼ VCB - Breakout ↑                              SCORE: 87/100   │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  Pattern   ██████████████░░  14/15  (Breakout)          │   │
│   │  VSA       ████████████████░░░░░  18/25  (Demand)       │   │
│   │  Trend     ████████████████████  20/20  (STRONG_UP)     │   │
│   │  S/R       ██████████░░░░░░  10/15  (-2.1% to support)  │   │
│   │  RS        █████████████░░░  13/15  (RS: 78)            │   │
│   │  Liquidity ████████████████  10/10  (45.2 tỷ)           │   │
│   ├─────────────────────────────────────────────────────────┤   │
│   │  S: 82,000 (Fib 38.2%)  |  R: 88,500 (Swing High)       │   │
│   │  R:R = 2.7:1  |  Action: MUA MẠNH ✅                     │   │
│   └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

**Pros:** Seamless UX, không rời context
**Cons:** Complex implementation với st.session_state

#### Option B: Modal/Dialog Approach

```
┌─────────────────────────────────────────────────────────────────┐
│  [3-column tables as current]                                   │
│  Click ticker → Opens modal dialog with breakdown               │
└─────────────────────────────────────────────────────────────────┘
```

**Pros:** Simpler implementation (st.dialog)
**Cons:** Breaks flow, user phải close modal

#### Option C: Merge với Single Stock Analysis

```
┌─────────────────────────────────────────────────────────────────┐
│ [Single Stock Analysis] - ENHANCED                              │
│  - Dropdown chọn từ signals list (thay vì input tự do)          │
│  - Show composite score breakdown                               │
│  - Show S/R + Strategy                                          │
├─────────────────────────────────────────────────────────────────┤
│ [3-column tables] - Click ticker → auto-fill Single Stock       │
└─────────────────────────────────────────────────────────────────┘
```

**Pros:** Reuse existing component, simple
**Cons:** Single Stock ở TOP, user scroll up/down

### 4.5 Recommended Approach: Option A + C Hybrid

1. **Keep Single Stock Analysis** ở top (cho manual lookup)
2. **Add click-to-expand** cho 3-column tables
3. **Wire click** để auto-populate Single Stock
4. **Add breakdown panel** trong expanded row

```python
# Implementation sketch
if st.session_state.get('selected_signal_ticker'):
    ticker = st.session_state.selected_signal_ticker
    # Render breakdown panel below tables
    render_score_breakdown_panel(ticker, signals_df)
```

---

## 5. Implementation Priority

### Phase 1: Logic (Must Have)
1. Implement `calculate_composite_score()` function
2. Add columns to signals DataFrame: composite_score, quality, factor scores
3. Replace strength with composite_score in display

### Phase 2: UI Basic
1. Update progress bar to show composite_score
2. Add quality badge (EXCELLENT/GOOD/etc.)
3. Add VSA signal name column

### Phase 3: UI Detail View
1. Add clickable rows with `st.session_state`
2. Render ScoreBreakdownCard on selection
3. Include S/R context và R:R ratio

### Phase 4: Polish
1. Smooth transitions (CSS)
2. Mobile responsive (collapse to single column)
3. Loading states

---

## 6. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Composite score calculation slow | Medium | Cache per ticker, batch compute |
| Score distribution not as expected | High | Validate với historical data trước deploy |
| UI expansion breaks layout | Medium | Test responsive, use fixed height containers |
| Missing data (RS, volume) | Medium | Default values với fallback scoring |

---

## 7. Success Metrics

1. **Score variance:** Standard deviation > 15 (currently ~0 với fixed 100)
2. **Distribution match:** 80% signals trong expected ranges
3. **User engagement:** Click-through to detail view > 30%
4. **Actionability:** Clear MUA/BÁN recommendations với confidence

---

## 8. Conclusion

### Logic Assessment: 7/10
- Strong foundation với 6-factor approach
- Cần fix: VSA conflict handling, Fib validation, liquidity threshold
- Missing: Time context, pattern position context

### UI Assessment: 5/10
- Current UI = good overview, missing detail
- Plan mockup = good detail, missing overview
- Solution: Combine both với expansion pattern

### Recommended Next Steps

1. **Implement composite scoring** (ta_dashboard_service.py)
2. **Add ScoreBreakdownCard** component
3. **Wire up click-to-expand** interaction
4. **Validate score distribution** với real data
5. **Iterate UI** based on user feedback

---

## Unresolved Questions

1. **Cache strategy:** S/R calculation expensive - cache per ticker or per session?
2. **RS Rating source:** Current data có RS 5d ago hay cần compute?
3. **Mobile view:** Single column với modal detail hay keep 3 columns?
4. **Realtime update:** Signals refresh khi user viewing detail?

---

*Report generated by brainstormer agent*
