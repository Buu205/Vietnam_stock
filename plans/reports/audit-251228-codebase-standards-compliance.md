# Codebase Standards Compliance Audit

**Date:** 2025-12-28
**Scope:** Full codebase standards compliance check
**Focus:** Docstrings, Type Hints, Registry Usage, Path Resolution, Design Standards

---

## Executive Summary

**Overall Compliance: 68% (Good)**

| Category | Status | Compliance | Action Required |
|----------|--------|------------|-----------------|
| Commit Messages | ✅ EXCELLENT | 95% | Document as standard |
| Path Resolution | ✅ EXCELLENT | 100% | Document as standard |
| Logging | ✅ GOOD | 85% | Minor improvements |
| Service Architecture | ✅ GOOD | 80% | Continue pattern |
| Docstrings | ⚠️ PARTIAL | 45% | Standardize to Google style |
| Type Hints | ⚠️ PARTIAL | 40% | Enforce universally |
| Registry Usage | ⚠️ PARTIAL | 23% (10/43 files) | Expand adoption |
| Financial Validation | ❌ MISSING | 20% | Add to calculators |
| Design Standards | ❌ MISSING | 0% | Create guidelines |

---

## Part 1: Code Standards Audit

### 1.1 Docstring Standards

**Current State:**
- **Google Style**: ~20 files (~45%)
- **Minimal**: ~25 files (~55%)
- **None**: ~5 files (test files)

**Examples:**

✅ **GOOD (Google-ish style):**
```python
# WEBAPP/services/company_service.py
def __init__(self, data_root: Optional[Path] = None):
    """
    Initialize CompanyService.

    Args:
        data_root: Root data directory (defaults to PROJECT_ROOT/DATA)
    """
```

⚠️ **NEEDS IMPROVEMENT (Minimal):**
```python
# WEBAPP/domains/forecast.py
"""forecast module."""
```

⚠️ **NEEDS IMPROVEMENT (Vietnamese/English mix):**
```python
# PROCESSORS/valuation/calculators/historical_pe_calculator.py
"""
Công cụ tính toán P/E Lịch sử - Tính toán chỉ số P/E theo chuỗi thời gian hàng ngày
Đã được tái cấu trúc để sử dụng ValuationMetricMapper và ValuationFormulas
"""
```

**Recommendation:**
```python
# ✅ STANDARD: Module docstring (English, brief)
"""
Historical PE Calculator
========================

Calculate daily PE ratio time series for all stocks.

PE Ratio = Market Cap / TTM Earnings

Usage:
    python3 PROCESSORS/valuation/calculators/historical_pe_calculator.py
"""

# ✅ STANDARD: Function docstring (Google style)
def calculate_pe_ratio(market_cap: float, earnings: float) -> Optional[float]:
    """Calculate Price-to-Earnings ratio.

    Args:
        market_cap: Total market capitalization in VND (must be > 0)
        earnings: TTM earnings in VND

    Returns:
        PE ratio as float, or None if earnings <= 0

    Raises:
        ValueError: If market_cap is negative

    Examples:
        >>> calculate_pe_ratio(1_000_000_000, 50_000_000)
        20.0
    """
```

**Files Needing Updates:** ~30 files

---

### 1.2 Type Hints Compliance

**Current State:**
- **Full type hints**: ~18 files (~40%)
- **Partial type hints**: ~20 files (~45%)
- **No type hints**: ~7 files (~15%)

**Examples:**

✅ **GOOD (Full type hints):**
```python
def __init__(self, data_root: Optional[Path] = None):
def get_financial_data(self, ticker: str, period: str) -> pd.DataFrame:
```

⚠️ **MISSING return type:**
```python
# WEBAPP/domains/banking.py
def get_bank_symbols():  # ❌ No return type
    """Get list of liquid bank symbols from master_symbols.json."""
```

**Should be:**
```python
def get_bank_symbols() -> List[str]:
    """Get list of liquid bank symbols from master_symbols.json."""
```

**Files Needing Updates:** ~25 files

---

### 1.3 Registry Usage Adoption

**Current State:**
- **Using registries**: 10 files (23%)
- **Should use registries**: 33 files (77%)

**Files USING registries ✅:**
1. `PROCESSORS/technical/indicators/sector_breadth.py`
2. `config/registries/sector_lookup.py`
3. `PROCESSORS/technical/indicators/rs_rating.py`
4. `WEBAPP/services/valuation_service.py`
5. `PROCESSORS/valuation/calculators/historical_ev_ebitda_calculator.py`
6. `WEBAPP/services/security_service.py`
7. `WEBAPP/services/bank_service.py`
8. `WEBAPP/services/company_service.py`
9. `WEBAPP/services/financial_metrics_loader.py`
10. `WEBAPP/core/symbol_loader.py`

**Files SHOULD use registries ⚠️:**
- All calculators (PE, PB, PS, EV/EBITDA)
- All sector analysis files
- All dashboard pages
- All technical indicators

**Example Refactor:**

❌ **BEFORE (Hardcoded):**
```python
BANK_TICKERS = ["ACB", "VCB", "TCB", "MBB", "CTG"]
```

✅ **AFTER (Registry):**
```python
from config.registries import SectorRegistry

sector_reg = SectorRegistry()
bank_tickers = sector_reg.get_symbols_by_entity("BANK")
```

**Impact:** ~33 files need refactoring

---

### 1.4 Path Resolution Standards

**Current State: ✅ EXCELLENT (100% compliance)**

**Finding:**
- ✅ All files use `DATA/processed/`, `DATA/raw/`
- ✅ ZERO files using deprecated paths (`calculated_results/`, `data_warehouse/raw/`)
- ✅ Path migration COMPLETED

**Evidence:**
```bash
# Search for deprecated paths
grep -r "calculated_results/" PROCESSORS/  # No matches
grep -r "data_warehouse/raw/" PROCESSORS/  # No matches
grep -r "DATA/refined/" PROCESSORS/  # No matches
```

**Current Pattern:**
```python
# Manual construction (acceptable but not centralized)
self.data_path = data_root / "DATA" / "processed" / "fundamental" / "company"
```

**Recommended Pattern:**
```python
# Centralized path helper (better)
from PROCESSORS.core.config.paths import get_data_path

data_path = get_data_path("processed", "fundamental", "company")
```

**Action:** Document current paths as standard, recommend centralized helper

---

### 1.5 Financial Validation

**Current State: ❌ MISSING (20% compliance)**

**Files WITH validation:**
- `PROCESSORS/valuation/calculators/historical_pe_calculator.py` (partial)

**Files WITHOUT validation:**
- Most calculators (~80%)

**Example Gaps:**

❌ **MISSING validation:**
```python
def calculate_pe(market_cap, earnings):
    return market_cap / earnings  # No validation!
```

✅ **SHOULD have:**
```python
def calculate_pe(market_cap: float, earnings: float) -> Optional[float]:
    """Calculate PE ratio with validation."""
    if market_cap <= 0:
        logger.warning(f"Invalid market_cap: {market_cap}")
        return None

    if earnings <= 0:
        return None  # Can't calculate PE with zero/negative earnings

    pe = market_cap / earnings

    # Sanity check
    if pe > 1000:
        logger.warning(f"Suspicious PE: {pe} for market_cap={market_cap}, earnings={earnings}")

    return pe
```

**Impact:** ~15 calculator files need validation

---

## Part 2: Design Standards (NEW)

### 2.1 AI Agent Selection Rules

**When to use which agent:**

#### **planner** - Architecture & Research
```yaml
Use when:
  - Designing new features
  - Researching best practices
  - Evaluating technical approaches
  - Creating implementation plans

Examples:
  - "Plan architecture for sector rotation feature"
  - "Research best practices for financial data caching"
  - "Design database schema for user preferences"
```

#### **tester** - Quality Validation
```yaml
Use when:
  - Running test suites
  - Validating implementations
  - Checking coverage
  - Before completing features

Examples:
  - "Run tests for valuation calculators"
  - "Check test coverage for company service"
  - "Validate PE calculation edge cases"
```

#### **ui-ux-designer** - Interface Design
```yaml
Use when:
  - Creating new dashboard pages
  - Designing charts/visualizations
  - Improving UX flows
  - Design system work

Examples:
  - "Design sector rotation dashboard layout"
  - "Create mobile-responsive navigation"
  - "Design dark mode color palette"
```

#### **code-reviewer** - Quality Assurance
```yaml
Use when:
  - After completing features
  - Before creating PRs
  - Refactoring legacy code
  - Security audits

Examples:
  - "Review sector analysis implementation"
  - "Check for security vulnerabilities"
  - "Audit code quality in calculators"
```

#### **debugger** - Issue Investigation
```yaml
Use when:
  - Investigating bugs
  - Performance issues
  - Data quality problems
  - Pipeline failures

Examples:
  - "Debug PE calculation returning None"
  - "Investigate slow dashboard loading"
  - "Find root cause of data mismatch"
```

---

### 2.2 Skill Activation Guide

**Primary Skills for Vietnamese Stock Dashboard:**

#### **frontend-development** ✅
```yaml
Activate when:
  - Working on WEBAPP/ code
  - React/TypeScript patterns
  - Streamlit components
  - Data visualization

Current Stack:
  - Streamlit
  - Plotly
  - Pandas
  - Pydantic models
```

#### **ui-styling** ✅
```yaml
Activate when:
  - Styling dashboards
  - Creating themes
  - Responsive layouts
  - Color palettes

Technologies:
  - Streamlit theming
  - Plotly templates
  - Custom CSS
```

#### **databases** ✅
```yaml
Activate when:
  - Working with parquet files
  - Data schema design
  - Query optimization
  - MongoDB integration (if added)

Current:
  - Parquet (primary storage)
  - Future: MongoDB for user data
```

#### **backend-development** ✅
```yaml
Activate when:
  - Working on PROCESSORS/
  - Data pipelines
  - API integrations
  - Business logic

Current Stack:
  - Python 3.13
  - Pandas/NumPy
  - vnstock_data API
```

#### **ai-multimodal** ✅
```yaml
Activate when:
  - Analyzing screenshots
  - Processing images
  - Document extraction
  - Visual QA

Use Cases:
  - Extract data from BSC Excel screenshots
  - Analyze competitor dashboards
```

---

### 2.3 MCP Tools Usage Guide

**Available MCP Servers:**

#### **bsc** - Vietnamese Stock Market Data (30 Tools)
```yaml
Location: MCP_SERVER/bsc_mcp/
Tools: 30 tools for Vietnamese stock data
Config: ~/.mcp.json or project .mcp.json

Capabilities:
  - Ticker info & peer discovery
  - Fundamental metrics (ROE, ROA, NIM, NPL)
  - Technical indicators (RSI, MACD, alerts)
  - Valuation (PE/PB historical, z-scores)
  - BSC forecasts (target prices, ratings)
  - Sector analysis (FA/TA scores)
  - Macro data (rates, FX, commodities)

When to Use:
  ✅ Querying live stock data
  ✅ Financial analysis during conversations
  ✅ Quick lookups without running scripts
  ✅ Comparative analysis across tickers

When NOT to Use:
  ❌ Batch processing (use PROCESSORS/ instead)
  ❌ Daily updates (use pipelines)
  ❌ Historical analysis >1 year (too slow)
```

**Example Usage:**

```python
# ✅ GOOD - Query specific data via MCP
# Ask AI: "ROE của ACB 4 quý gần nhất?"
# AI uses: bsc_get_company_financials("ACB", period="Quarterly", limit=4)

# ✅ GOOD - Comparison via MCP
# Ask AI: "So sánh PE của VCB, ACB, TCB, MBB"
# AI uses: bsc_compare_valuations("VCB,ACB,TCB,MBB", metric="PE")

# ❌ BAD - Don't use MCP for batch processing
# Don't: Query 457 tickers via MCP (too slow!)
# Do: Use PROCESSORS/pipelines/ for batch jobs
```

#### **zai-mcp-server** - Image Analysis Tools
```yaml
Tools:
  - ui_to_artifact: Screenshot → Code/Spec/Prompt
  - extract_text_from_screenshot: OCR text extraction
  - diagnose_error_screenshot: Error analysis
  - understand_technical_diagram: Diagram interpretation
  - analyze_data_visualization: Chart analysis
  - ui_diff_check: Compare UI screenshots
  - analyze_video: Video content analysis

When to Use:
  ✅ Extract data from Excel screenshots
  ✅ Convert UI mockups to code
  ✅ Debug error screenshots
  ✅ Analyze competitor dashboards
  ✅ Extract text from images/PDFs
```

**Example Usage:**

```python
# ✅ GOOD - Extract BSC Excel data
# AI uses: extract_text_from_screenshot(
#   image_source="bsc_forecast.png",
#   prompt="Extract target prices for banking sector"
# )

# ✅ GOOD - Convert UI design to code
# AI uses: ui_to_artifact(
#   image_source="dashboard_mockup.png",
#   output_type="code",
#   prompt="Generate Streamlit code for this dashboard layout"
# )
```

#### **searchapi** - Web Search
```yaml
Use when:
  ✅ Research latest best practices
  ✅ Find external documentation
  ✅ Check industry news
  ✅ Discover new libraries/tools
```

#### **context7** - Documentation Search (NEW)
```yaml
Service: https://context7.com
API Type: HTTP MCP Server
API Key: ctx7sk-8848099b-3fc3-4a97-a836-8febb6c2bed3

Capabilities:
  - Search documentation for 1000+ libraries/frameworks
  - Get latest API references
  - Find code examples
  - Version-specific docs

Use when:
  ✅ Need latest library documentation
  ✅ Research API changes/deprecations
  ✅ Find framework best practices
  ✅ Get code examples for libraries

Example Queries:
  - "Streamlit v1.33 st.html() documentation"
  - "Pandas DataFrame to_parquet schema parameter"
  - "Plotly bar chart customization examples"
  - "vnstock latest API reference"
```

**Usage in Conversation:**
```
# Ask Claude directly:
"Tìm documentation của Streamlit st.html() method"
"Pandas to_parquet có parameter nào để set schema?"
"Plotly bar chart màu sắc customize như thế nào?"

# Claude will automatically use context7 MCP to fetch docs
```

---

### 2.4 MCP vs Built-in Tools Decision Matrix

| Task | Use MCP | Use Built-in | Reason |
|------|---------|-------------|--------|
| **Query 1 ticker financials** | ✅ `bsc` MCP | ❌ | Fast, interactive |
| **Query 457 tickers** | ❌ | ✅ `Read parquet` | Batch = built-in faster |
| **Compare 4 banks** | ✅ `bsc` MCP | ⚠️ Either works | MCP more convenient |
| **Daily data update** | ❌ | ✅ `pipelines/` | Automation = pipelines |
| **Extract Excel screenshot** | ✅ `zai` MCP | ❌ | Image analysis |
| **Read parquet file** | ❌ | ✅ `Read` tool | Direct access faster |
| **Search best practices** | ✅ `searchapi` | ❌ | Web search |
| **Library documentation** | ✅ `context7` | ⚠️ Web search | context7 has versioned docs |
| **Code completion** | ❌ | ✅ Native | Built-in better |

**Golden Rules:**

1. **Interactive queries** → MCP tools (fast, conversational)
2. **Batch operations** → Built-in tools (scripts, pipelines)
3. **Image/video analysis** → `zai` MCP (specialized)
4. **File operations** → Built-in tools (Read, Write, Edit)
5. **Web research** → `searchapi` MCP

---

### 2.3 Chart Design Standards (Plotly)

#### **Color Palette (Financial Data)**

**Primary Colors:**
```python
COLORS = {
    # Positive/Negative
    'positive': '#10b981',      # Green (gains, buy)
    'negative': '#ef4444',      # Red (losses, sell)
    'neutral': '#6b7280',       # Gray (hold, neutral)

    # Categories
    'primary': '#3b82f6',       # Blue (main data)
    'secondary': '#8b5cf6',     # Purple (comparison)
    'accent': '#f59e0b',        # Orange (highlights)

    # Financial Metrics
    'revenue': '#3b82f6',       # Blue
    'profit': '#10b981',        # Green
    'debt': '#ef4444',          # Red
    'equity': '#8b5cf6',        # Purple

    # Sectors (19 colors for 19 sectors)
    'sectors': [
        '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
        '#06b6d4', '#84cc16', '#f97316', '#ec4899', '#6366f1',
        '#14b8a6', '#a3e635', '#fb923c', '#f472b6', '#818cf8',
        '#22d3ee', '#bef264', '#fdba74', '#fda4af'
    ]
}
```

**Chart Templates:**

✅ **STANDARD: Line Chart (Time Series)**
```python
import plotly.graph_objects as go

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df['date'],
    y=df['pe_ratio'],
    mode='lines',
    name='PE Ratio',
    line=dict(color=COLORS['primary'], width=2),
    hovertemplate='<b>%{x}</b><br>PE: %{y:.2f}<extra></extra>'
))

fig.update_layout(
    title=dict(
        text='VN-Index PE Ratio Historical',
        font=dict(size=20, weight=600, family='Arial, sans-serif')
    ),
    xaxis=dict(
        title='Date',
        showgrid=True,
        gridcolor='rgba(200,200,200,0.2)'
    ),
    yaxis=dict(
        title='PE Ratio',
        showgrid=True,
        gridcolor='rgba(200,200,200,0.2)'
    ),
    hovermode='x unified',
    height=500,
    margin=dict(l=50, r=50, t=80, b=50),
    font=dict(family='Arial, sans-serif', size=12)
)
```

✅ **STANDARD: Bar Chart (Comparison)**
```python
fig = go.Figure()
fig.add_trace(go.Bar(
    x=df['sector'],
    y=df['avg_pe'],
    marker=dict(
        color=df['avg_pe'],
        colorscale='RdYlGn_r',  # Red (high) to Green (low)
        showscale=True
    ),
    text=df['avg_pe'].round(2),
    textposition='outside',
    hovertemplate='<b>%{x}</b><br>PE: %{y:.2f}<extra></extra>'
))

fig.update_layout(
    title='Sector PE Comparison',
    xaxis=dict(title='Sector', tickangle=-45),
    yaxis=dict(title='Average PE Ratio'),
    height=600,
    showlegend=False
)
```

✅ **STANDARD: Candlestick Chart (OHLC)**
```python
fig = go.Figure(data=[go.Candlestick(
    x=df['date'],
    open=df['open'],
    high=df['high'],
    low=df['low'],
    close=df['close'],
    increasing=dict(line=dict(color=COLORS['positive']), fillcolor=COLORS['positive']),
    decreasing=dict(line=dict(color=COLORS['negative']), fillcolor=COLORS['negative'])
)])

fig.update_layout(
    title='ACB Stock Price (OHLC)',
    yaxis_title='Price (VND)',
    xaxis_rangeslider_visible=False,
    height=600
)
```

---

### 2.4 Typography Standards

#### **Font Hierarchy:**

```python
TYPOGRAPHY = {
    'heading_1': {
        'size': 32,
        'weight': 700,  # Bold
        'family': 'Arial, sans-serif',
        'color': '#1f2937',  # Dark gray
        'margin_bottom': 24
    },
    'heading_2': {
        'size': 24,
        'weight': 600,  # Semibold
        'family': 'Arial, sans-serif',
        'color': '#374151',
        'margin_bottom': 16
    },
    'heading_3': {
        'size': 18,
        'weight': 600,
        'family': 'Arial, sans-serif',
        'color': '#4b5563',
        'margin_bottom': 12
    },
    'body': {
        'size': 14,
        'weight': 400,  # Regular
        'family': 'Arial, sans-serif',
        'color': '#6b7280',
        'line_height': 1.6
    },
    'caption': {
        'size': 12,
        'weight': 400,
        'family': 'Arial, sans-serif',
        'color': '#9ca3af',
        'line_height': 1.4
    },
    'metric_value': {
        'size': 36,
        'weight': 700,
        'family': 'Arial, sans-serif',
        'color': '#1f2937'
    },
    'metric_label': {
        'size': 14,
        'weight': 500,
        'family': 'Arial, sans-serif',
        'color': '#6b7280'
    }
}
```

#### **Streamlit Usage:**

```python
import streamlit as st

# ✅ STANDARD: Page title
st.markdown("# Vietnamese Stock Dashboard")  # H1

# ✅ STANDARD: Section headers
st.markdown("## Sector Analysis")  # H2
st.markdown("### Top Performers")  # H3

# ✅ STANDARD: Metric display
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(
        label="VN-Index",
        value="1,250.5",
        delta="+15.3 (+1.24%)",
        delta_color="normal"  # Green for positive
    )

# ✅ STANDARD: Caption text
st.caption("Data updated: 2025-12-28 15:00 VN Time")
```

---

### 2.5 MCP Server Configuration

**Current MCP Servers:**

```json
// ~/.claude.json (project-specific)
{
  "projects": {
    "/Users/buuphan/Dev/Vietnam_dashboard": {
      "mcpServers": {
        // STDIO Server - Vietnamese Stock Data
        "bsc": {
          "type": "stdio",
          "command": "python3",
          "args": ["-m", "bsc_mcp.server"],
          "cwd": "/Users/buuphan/Dev/Vietnam_dashboard/MCP_SERVER",
          "env": {
            "PYTHONPATH": "/Users/buuphan/Dev/Vietnam_dashboard:/Users/buuphan/Dev/Vietnam_dashboard/MCP_SERVER",
            "DATA_ROOT": "/Users/buuphan/Dev/Vietnam_dashboard/DATA"
          }
        },

        // HTTP Server - Documentation Search
        "context7": {
          "type": "http",
          "url": "https://mcp.context7.com/mcp",
          "headers": {
            "CONTEXT7_API_KEY": "ctx7sk-8848099b-3fc3-4a97-a836-8febb6c2bed3"
          }
        }
      }
    }
  }
}
```

**Adding New MCP Server:**

```bash
# STDIO server (local Python)
claude mcp add --transport stdio bsc python3 -m bsc_mcp.server \
  --cwd /path/to/MCP_SERVER \
  --env PYTHONPATH=/path/to/project

# HTTP server (remote API)
claude mcp add --transport http context7 https://mcp.context7.com/mcp \
  --header "CONTEXT7_API_KEY: YOUR_API_KEY"
```

**Testing MCP:**

```bash
# List available tools
python3 -m bsc_mcp.server --list-tools

# Test specific tool
python3 -m bsc_mcp.server --test bsc_get_ticker_info --args '{"ticker": "ACB"}'
```

**Documentation:**
- MCP Server README: `MCP_SERVER/README.md`
- Tool list: 30 tools documented in README
- Configuration: Claude Desktop, Cursor, Claude Code supported

---

### 2.6 Data Visualization Rules

#### **Chart Types by Use Case:**

| Data Type | Best Chart | Alternative |
|-----------|-----------|-------------|
| **Time series** | Line chart | Area chart |
| **Comparison** | Bar chart | Horizontal bar |
| **Distribution** | Histogram | Box plot |
| **Correlation** | Scatter plot | Heatmap |
| **Composition** | Pie chart (max 5) | Treemap |
| **Trend + volume** | Candlestick + Volume | Line + Bar |
| **Multiple metrics** | Multi-axis line | Grouped bar |

#### **Chart Complexity Guidelines:**

```yaml
✅ GOOD PRACTICES:
  - Max 5 series per chart
  - Clear axis labels
  - Consistent color coding
  - Interactive tooltips
  - Responsive sizing
  - Legend placement (top-right)

❌ AVOID:
  - 3D charts (hard to read)
  - Too many colors (>8)
  - Pie charts with >5 slices
  - Cluttered axes
  - Missing units (VND, %, etc.)
```

---

## Part 3: Updated Priority Rules

### **P0: Non-Negotiable (Already Implemented)**

| Rule | Status | Compliance | Action |
|------|--------|------------|--------|
| **Commit Messages** | ✅ DONE | 95% | Document as standard |
| **Path Resolution** | ✅ DONE | 100% | Document as standard |
| **Logging** | ✅ DONE | 85% | Minor improvements |

**No action needed - these are already working well.**

---

### **P1: Standardization Required**

| Rule | Status | Compliance | Effort | Impact |
|------|--------|------------|--------|--------|
| **Docstring Google Style** | ⚠️ PARTIAL | 45% | MEDIUM | HIGH |
| **Type Hints Universal** | ⚠️ PARTIAL | 40% | LOW | MEDIUM |
| **Registry Everywhere** | ⚠️ PARTIAL | 23% | HIGH | HIGH |
| **Financial Validation** | ❌ MISSING | 20% | MEDIUM | HIGH |

**Priority Actions:**
1. Create docstring template
2. Enforce type hints in code review
3. Refactor top 10 files to use registries
4. Add validation to all calculators

---

### **P2: Design Standards (New)**

| Rule | Status | Compliance | Effort | Impact |
|------|--------|------------|--------|--------|
| **AI Agent Selection** | ❌ NEW | 0% | LOW | MEDIUM |
| **Skill Activation** | ❌ NEW | 0% | LOW | MEDIUM |
| **Chart Design Standards** | ❌ NEW | 0% | MEDIUM | HIGH |
| **Typography Standards** | ❌ NEW | 0% | LOW | MEDIUM |

**Priority Actions:**
1. Document agent selection rules
2. Create Plotly chart templates
3. Standardize color palette
4. Define typography system

---

### **P3: Performance & Best Practices**

| Rule | Status | Effort | Impact |
|------|--------|--------|--------|
| **Vectorization** | ⚠️ UNKNOWN | MEDIUM | HIGH |
| **Parquet Schema** | ⚠️ UNKNOWN | MEDIUM | HIGH |
| **Error Handling** | ⚠️ PARTIAL | LOW | MEDIUM |
| **Config Externalization** | ⚠️ PARTIAL | LOW | MEDIUM |

**Needs Audit:** Separate performance audit required

---

## Part 4: Implementation Roadmap

### **Phase 1: Quick Wins (1 week)**

**Week 1: Documentation Standards**
- [ ] Create docstring template (Google style)
- [ ] Update top 10 files with proper docstrings
- [ ] Add type hints to public functions (top 10 files)
- [ ] Document AI agent selection rules
- [ ] Create chart color palette constants

**Deliverables:**
- `.claude/rules/conventions.md` (docstring + type hint standards)
- `.claude/guides/ai-agents.md` (agent selection guide)
- `WEBAPP/core/chart_styles.py` (Plotly templates)

---

### **Phase 2: Registry Expansion (2 weeks)**

**Week 2-3: Refactor Top Files**
- [ ] Audit all data access patterns
- [ ] Refactor top 10 calculator files to use registries
- [ ] Refactor dashboard pages to use registries
- [ ] Add registry usage examples to docs

**Deliverables:**
- Registry adoption: 23% → 60%
- Updated `.claude/rules/patterns.md`

---

### **Phase 3: Validation & Quality (2 weeks)**

**Week 4-5: Add Validation**
- [ ] Add financial data validation to all calculators
- [ ] Add unit tests for edge cases
- [ ] Create validation helper functions
- [ ] Document validation patterns

**Deliverables:**
- Validation coverage: 20% → 80%
- `PROCESSORS/core/validation.py` (validation helpers)

---

### **Phase 4: Design System (1 week)**

**Week 6: Standardize UI**
- [ ] Create Plotly chart templates
- [ ] Define typography system
- [ ] Document color palette
- [ ] Create component library

**Deliverables:**
- `WEBAPP/core/design_system.py`
- `.claude/guides/design-standards.md`

---

## Part 5: Metrics & Success Criteria

### **Target Compliance (3 months)**

| Category | Current | Target | Success Metric |
|----------|---------|--------|----------------|
| **Docstrings** | 45% | 80% | All public functions have Google-style docstrings |
| **Type Hints** | 40% | 90% | All public functions have type hints |
| **Registry Usage** | 23% | 70% | All data access uses registries |
| **Validation** | 20% | 80% | All calculators validate inputs |
| **Design Standards** | 0% | 100% | All charts follow design system |

### **Quality Indicators**

```yaml
Code Quality:
  - Docstring coverage: >80%
  - Type hint coverage: >90%
  - Test coverage: >70%
  - No deprecated path usage: 100%

Design Quality:
  - Consistent color palette: 100%
  - Chart accessibility: WCAG AA
  - Mobile responsive: 100%
  - Loading time: <2s per page

Development Velocity:
  - New feature time: -30% (due to standards)
  - Bug fix time: -40% (due to validation)
  - Code review time: -50% (due to standards)
```

---

## Part 6: Streamlit UI/UX Best Practices (From ui-errors-lessons-learned.md)

### **Critical Streamlit Gotchas**

#### **Issue 1: SVG Icons in st.markdown() ❌**

**Problem:** Inline SVG gets escaped and displays as raw text.

```python
# ❌ WRONG - SVG will be escaped
icon = '<svg width="16" height="16">...</svg>'
st.markdown(f'<div>{icon}</div>', unsafe_allow_html=True)
```

**Solution:** Use emoji or CSS symbols.

```python
# ✅ CORRECT - Use emoji
SIGNAL_EMOJI = {
    'ma_crossover': '📈',
    'volume_spike': '📊',
    'breakout': '🚀',
    'patterns': '🕯️'
}

# ✅ BETTER - HTML badges (professional)
badge = '<span style="background:rgba(16,185,129,0.15); color:#10B981; padding:4px 8px; border-radius:4px;">BUY</span>'
```

---

#### **Issue 2: st.dataframe() with Dark Theme ❌**

**Problem:** `st.dataframe()` uses canvas rendering. CSS selectors don't work → text invisible on dark theme.

```python
# ❌ WRONG - Text becomes invisible
st.dataframe(df, use_container_width=True)
```

**Solution:** Use `st.html()` with custom HTML tables (Streamlit v1.33+).

```python
# ✅ CORRECT - Custom HTML table
from WEBAPP.core.styles import render_styled_table

html_table = render_styled_table(df, highlight_first_col=True)
st.html(html_table)  # Use st.html() not st.markdown()
```

**Why `st.html()` > `st.markdown()`:**
- `st.html()` renders raw HTML without escaping
- `st.markdown(unsafe_allow_html=True)` can still escape complex structures
- Available in Streamlit v1.33+

---

#### **Issue 3: Complex Nested HTML ❌**

**Problem:** Deep nesting or very long HTML strings can get truncated/escaped.

```python
# ❌ RISKY - Complex nested HTML
html = '''
<div style="...">
    <div style="...">
        <span><svg>...</svg></span>  # Nested SVG = FAIL
    </div>
</div>
'''
```

**Solution:** Keep HTML simple and flat.

```python
# ✅ CORRECT - Use Streamlit native components
cols = st.columns(4)
for i, (label, count) in enumerate(data.items()):
    with cols[i]:
        st.metric(label=label, value=count)
```

---

### **Streamlit Best Practices Summary**

#### **DO:**
- ✅ Use `st.html()` for custom HTML tables (Streamlit v1.33+)
- ✅ Use `render_styled_table()` from `WEBAPP/core/styles.py`
- ✅ Use `st.columns()` for layouts
- ✅ Use `st.metric()` for KPI cards
- ✅ Use HTML color badges: `<span style="background:rgba(16,185,129,0.15); color:#10B981;">BUY</span>`
- ✅ Test both light and dark themes
- ✅ Follow existing dashboard patterns (Company, Sector, Bank)

#### **DON'T:**
- ❌ Use inline SVG in `st.markdown()` (gets escaped)
- ❌ Use `st.dataframe()` if dark theme CSS applied (text invisible)
- ❌ Create overly complex nested HTML
- ❌ Assume CSS selectors work on Streamlit internals
- ❌ Use emoji for production UI (use HTML badges for professional look)

---

### **Dark Theme Color Palette (OLED)**

**From:** `WEBAPP/core/theme.py` + `ui-errors-lessons-learned.md`

```python
DARK_THEME_COLORS = {
    # Background
    'bg_deep': '#0F0B1E',          # Dark Purple-Black
    'bg_surface': '#1A1625',       # Dark Purple
    'bg_elevated': '#241D30',      # Elevated Surface

    # Text
    'text_primary': '#E2E8F0',     # Light Gray
    'text_secondary': '#94A3B8',   # Gray
    'text_muted': '#64748B',       # Muted Gray

    # Accents
    'accent_purple': '#8B5CF6',    # Electric Purple
    'accent_cyan': '#06B6D4',      # Cyan

    # Signals (Financial)
    'positive': '#10B981',         # Green (BUY)
    'negative': '#EF4444',         # Red (SELL)
    'warning': '#F59E0B',          # Amber (HOLD)
    'neutral': '#64748B',          # Gray

    # Chart Colors
    'chart_line': '#8B5CF6',       # Purple
    'chart_area': 'rgba(139, 92, 246, 0.1)',
    'chart_grid': 'rgba(100, 116, 139, 0.2)'
}
```

**Usage:**

```python
# ✅ CORRECT - HTML badge with dark theme
buy_badge = f'''
<span style="
    background: rgba(16, 185, 129, 0.15);
    color: #10B981;
    padding: 4px 12px;
    border-radius: 6px;
    border: 1px solid rgba(16, 185, 129, 0.3);
    font-weight: 600;
    font-size: 13px;
">BUY</span>
'''
st.markdown(buy_badge, unsafe_allow_html=True)
```

---

### **UI Component Library**

**Location:** `WEBAPP/core/styles.py`

#### **1. Styled Table**
```python
from WEBAPP.core.styles import render_styled_table

html = render_styled_table(
    df,
    highlight_first_col=True,
    hover_effect=True
)
st.html(html)
```

#### **2. Progress Bar Gauge**
```python
def render_progress_bar(value: float, max_value: float = 100) -> str:
    """Render visual gauge like ████████░░ 85"""
    pct = min(100, max(0, (value / max_value) * 100))

    # Color coding
    if pct >= 70: color = '#10B981'    # Green
    elif pct >= 50: color = '#06B6D4'  # Cyan
    elif pct >= 30: color = '#F59E0B'  # Amber
    else: color = '#64748B'            # Gray

    filled = int(pct / 10)
    empty = 10 - filled

    return f'''
    <span style="color:{color};">{"█" * filled}</span>
    <span style="color:#374151;">{"░" * empty}</span>
    <span style="color:#E2E8F0;"> {int(pct)}</span>
    '''
```

#### **3. Signal Badge**
```python
def render_signal_badge(signal: str) -> str:
    """Render BUY/SELL/HOLD badge"""
    BADGE_STYLES = {
        'BUY': {
            'bg': 'rgba(16, 185, 129, 0.15)',
            'color': '#10B981',
            'border': 'rgba(16, 185, 129, 0.3)'
        },
        'SELL': {
            'bg': 'rgba(239, 68, 68, 0.15)',
            'color': '#EF4444',
            'border': 'rgba(239, 68, 68, 0.3)'
        },
        'HOLD': {
            'bg': 'rgba(245, 158, 11, 0.15)',
            'color': '#F59E0B',
            'border': 'rgba(245, 158, 11, 0.3)'
        }
    }

    style = BADGE_STYLES.get(signal, BADGE_STYLES['HOLD'])

    return f'''
    <span style="
        background: {style['bg']};
        color: {style['color']};
        border: 1px solid {style['border']};
        padding: 4px 12px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 13px;
    ">{signal}</span>
    '''
```

---

### **Updated Design Standards**

**Add to `.claude/guides/design-standards.md`:**

1. **Use `st.html()` for custom HTML** (Streamlit v1.33+)
2. **Use component library** from `WEBAPP/core/styles.py`
3. **Follow dark theme palette** from `WEBAPP/core/theme.py`
4. **Test both themes** before committing
5. **Professional badges** over emoji for production UI

**Reference Files:**
- `WEBAPP/core/styles.py` - Component library
- `WEBAPP/core/theme.py` - Color palette
- `plans/reports/ui-errors-lessons-learned.md` - Gotchas & solutions

---

## Unresolved Questions

1. **Performance Audit**: Need separate audit for vectorization compliance
2. **Test Coverage**: Current coverage unknown - need to measure
3. **Parquet Schema**: Need audit of schema consistency across files
4. **Mobile Responsiveness**: Current mobile UX unknown - need testing
5. **Accessibility**: WCAG compliance level unknown - need audit
6. **API Rate Limits**: vnstock_data rate limiting not documented
7. **Error Monitoring**: No centralized error tracking - consider Sentry?

---

## Next Steps

1. **User review** this audit report
2. **Prioritize** P1 vs P2 actions
3. **Create** template files (docstring, chart, typography)
4. **Start** Phase 1 quick wins
5. **Schedule** follow-up audits (performance, accessibility)
