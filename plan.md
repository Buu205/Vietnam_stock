
Claude’s Plan
🎨 Streamlit UI/UX Complete Redesign Plan
Project: Vietnam Stock Dashboard UI/UX Transformation Date: 2025-12-12 Scope: Migrate from PyEcharts to Plotly, redesign navigation, optimize performance Effort: 3-4 weeks (phased implementation)
📊 Current State Analysis
Existing Dashboard Structure (7 Pages, 8,921 LOC)
Page	LOC	Library	Issues
Company	1,199	PyEcharts	Duplicated chart builders (300+ LOC), inefficient data loading (5x queries)
Bank	2,141	PyEcharts	Largest file, mixed PyEcharts/Plotly, no component reuse
Securities	1,504	PyEcharts	Limited to 16 securities, duplicated code
Technical	1,907	Mixed	No main() function, inconsistent patterns
Valuation	518	Plotly	Well-structured, good use of Plotly
Forecast	1,392	Native	150 lines of custom CSS, good table design
News	260	Plotly	Cleanest code, good sentiment analysis
Critical Pain Points
Code Duplication: 300+ lines of duplicated PyEcharts builders across 3 files
Performance Issues: Company dashboard queries same parquet 5x per page load
Inconsistent Patterns: 5 different import strategies, mixed entry points (main() vs render_*)
PyEcharts Problems: Slow rendering, not always responsive, limited interactivity
Navigation Issues: News dashboard doesn't render top nav properly
Cache Chaos: TTL ranges from 60s to 3600s, no centralized strategy
🎯 Redesign Objectives
Primary Goals
✅ Migrate 100% to Plotly - Remove all PyEcharts dependencies
✅ Optimize Performance - Reduce data loading by 80%, implement smart caching
✅ Improve UX - Intuitive navigation, faster interactions, responsive design
✅ Reduce Code - Eliminate 300+ LOC duplication, create reusable components
✅ Standardize Patterns - Consistent imports, caching, error handling
User Experience Enhancements
Faster Loading: Target <2s initial load, <500ms navigation
Better Navigation: Grouped pages by analysis type, breadcrumbs
Modern Design: Dark mode support, cohesive color scheme, professional typography
Interactive Charts: Full Plotly interactivity (zoom, pan, hover, export)
Mobile Responsive: Charts adapt to screen size
🏗️ New Architecture Design
Proposed Page Grouping (8 Pages → 4 Categories)
Category 1: Fundamental Analysis (FA) - Separated by Entity Type (4 pages)
📊 Fundamental Analysis (FA)
├── 1. Company Analysis     (Company-specific financial statements)
│   ├── Overview Dashboard
│   ├── Income Statement    (CIS metrics: Revenue, COGS, SGA, EBIT, NPATMI)
│   ├── Balance Sheet       (CBS metrics: Assets, Liabilities, Equity)
│   ├── Cash Flow          (CCS metrics: Operating, Investing, Financing CF)
│   └── Financial Ratios    (ROE, ROA, Margins, Turnover)
│
├── 2. Banking Analysis     (Bank-specific financial statements)
│   ├── Overview Dashboard
│   ├── Income Statement    (BIS metrics: NII, Non-interest income, Provisions)
│   ├── Balance Sheet       (BBS metrics: Loans, Deposits, Equity)
│   ├── Banking Ratios      (NIM, CIR, CAR, NPL, LDR)
│   └── Credit Analysis     (Loan growth, Asset quality)
│
├── 3. Securities Analysis  (Securities/Brokerage-specific)
│   ├── Overview Dashboard
│   ├── Income Statement    (SIS metrics: Brokerage revenue, Investment income)
│   ├── Balance Sheet       (SBS metrics: Client deposits, Proprietary investments)
│   ├── Securities Ratios   (ROE, ROA, Revenue mix)
│   └── Market Share        (Trading volume, client accounts)
│
└── 4. Insurance Analysis   (Insurance-specific - NEW)
    ├── Overview Dashboard
    ├── Income Statement    (IIS metrics: Premiums, Claims, Investment income)
    ├── Balance Sheet       (IBS metrics: Reserves, Investments)
    ├── Insurance Ratios    (Combined ratio, Loss ratio, Expense ratio)
    └── Underwriting Analysis
Rationale: Báo cáo tài chính của từng entity type khác nhau hoàn toàn:
Company: CIS/CBS/CCS - Doanh nghiệp sản xuất/dịch vụ truyền thống
Bank: BIS/BBS/BCS - Thu nhập lãi, cho vay, huy động vốn
Securities: SIS/SBS/SCS - Môi giới, tự doanh, margin lending
Insurance: IIS/IBS/ICS - Phí bảo hiểm, bồi thường, đầu tư
Category 2: Valuation Analysis - Cross-sector comparison (1 page)
💰 Valuation Analysis (Tách riêng, áp dụng cho TẤT CẢ entity types)
├── 1. Valuation Dashboard  (Universal for all stocks)
│   ├── PE/PB/EV Analysis   (Individual stock trends)
│   │   └── PE/PB candlestick charts (như render_pe_pb_dotplot)
│   ├── Sector Valuation    (Cross-sector comparison)
│   │   ├── Banking Sector PE/PB
│   │   ├── Securities Sector PE/PB
│   │   ├── Insurance Sector PE/PB
│   │   ├── Industry Sector PE/PB
│   │   └── Scatter plot: Sector PE vs Market Cap/Revenue
│   ├── Historical Percentiles (Where is current valuation?)
│   │   ├── PE percentile (vs 3-year history)
│   │   ├── PB percentile
│   │   └── EV/EBITDA percentile
│   └── Fair Value Calculator (DCF, Comparable valuation)
Rationale: Valuation metrics (PE, PB, EV/EBITDA) áp dụng universal cho tất cả stocks, nên tách riêng thành 1 page duy nhất.
Category 3: Technical Analysis (TA) - Stock-level + Market-level (2 pages)
📈 Technical Analysis (TA)
├── 1. Stock Technical      (Individual stock TA)
│   ├── Symbol Selector     (Choose any stock)
│   ├── Price Chart         (Candlestick/OHLC with volume)
│   ├── Moving Averages     (SMA 20/50/100/200, EMA)
│   ├── Oscillators        (RSI, MACD, Stochastic)
│   ├── Bollinger Bands    (Volatility analysis)
│   └── Pattern Recognition (Support/Resistance, Trendlines)
│
└── 2. Market Technical     (Market-wide TA)
    ├── MA Screening Table  (All stocks: MA alignment, cuts, approaches)
    ├── Market Breadth      (Advance/Decline, % above MA20/50/100)
    ├── Sector Rotation     (Which sectors are leading?)
    ├── Market Momentum     (VN-Index RSI, MACD)
    └── Macro Indicators    (Gold, Oil, USD/VND, Interest rates)
Rationale:
Stock Technical: Phân tích kỹ thuật cho 1 mã cụ thể (như TradingView)
Market Technical: Phân tích thị trường tổng thể, screening, breadth
Category 4: Market Intelligence (2 pages)
🔍 Market Intelligence
├── 1. Analyst Forecasts    (BSC forecast data)
│   ├── Target Prices
│   ├── Buy/Hold/Sell Ratings
│   ├── Earnings Estimates (EPS, P/E forward)
│   └── Dividend Forecasts
│
└── 2. News & Sentiment     (News analysis)
    ├── News Feed (Latest articles)
    ├── Sentiment Analysis (Positive/Negative/Neutral)
    ├── Market Events (Upcoming events, dividends, AGM)
    └── Coverage Summary (Which stocks are covered most)
New Navigation Structure
┌──────────────────────────────────────────────────────────────────┐
│  🏠 Vietnam Stock Dashboard                    🔍 Search  ⚙️ Settings │
├──────────────────────────────────────────────────────────────────┤
│  📊 Fundamental  │  📈 Technical  │  🔍 Intelligence  │  📚 Tools  │
└──────────────────────────────────────────────────────────────────┘
     ↓
┌──────────────────────────────────────────────────────────────────┐
│  Breadcrumb: Home > Fundamental > Company Deep Dive > VNM        │
├──────────────────────────────────────────────────────────────────┤
│  [Page Content with Tabs]                                        │
└──────────────────────────────────────────────────────────────────┘
Benefits:
Logical grouping by analysis type
Reduced cognitive load (3 categories vs 7 flat pages)
Clear hierarchy with breadcrumbs
Tools section for utilities (screeners, alerts, portfolio tracking)
📊 Chart Library Strategy
Recommended Approach: Mixed Strategy (Plotly + Lightweight Charts)
Dựa trên yêu cầu "biểu diễn chart đẹp" và tính đồng bộ, tôi đề xuất:
Primary: Plotly (90% charts)
Ưu điểm:
✅ Interactive tốt (zoom, pan, hover, export)
✅ Responsive design (tự động scale theo screen)
✅ Nhiều chart types (line, bar, scatter, heatmap, candlestick)
✅ Subplot support (multi-chart layouts)
✅ Theme customization dễ dàng
✅ Professional appearance
✅ Python-native (no JavaScript needed)
Nhược điểm:
⚠️ Performance với >10,000 data points
⚠️ File size lớn hơn PyEcharts
Use Cases:
Financial statements (bar, line, combo charts)
Valuation trends (line with bands, scatter plots)
Sector comparison (heatmaps, boxplots)
Market breadth (multi-line charts)
Secondary: Lightweight Charts (10% charts - Optional)
For advanced price charts only:
Candlestick charts với volume bars
Real-time streaming (nếu có live data sau này)
TradingView-style charts
Library: lightweight-charts-python (wrapper của TradingView Lightweight Charts) Use Cases:
Stock Technical page → Price chart with volume
Market Technical page → VN-Index chart
Eliminate: PyEcharts (0%)
Lý do:
❌ Không đồng bộ rendering
❌ Limited interactivity so với Plotly
❌ Less responsive
❌ Harder to customize theme
❌ Dependency conflict risks
Chart Type Mapping (PyEcharts → Plotly)
Current (PyEcharts)	New (Plotly)	Plotly Method	Notes
Bar	Bar	go.Bar()	Simple, fast
Line	Line	go.Scatter(mode='lines')	More flexible than PyEcharts
Bar + Line overlay	Bar + Line	make_subplots() + secondary_y=True	Better than PyEcharts overlap
Grid (5 charts)	Subplots	make_subplots(rows=3, cols=2)	More control
Line with bands	Multiple Scatter	go.Scatter() with fill='tonexty'	Statistical bands
Boxplot	Box	go.Box()	Built-in, better styling
Scatter	Scatter	go.Scatter(mode='markers')	Size, color encoding
Heatmap	Heatmap	go.Heatmap()	Better color scales
Candlestick	Candlestick	go.Candlestick()	NEW for valuation/price
Example Conversions
1. Bar + Line Combo (Company Income Statement)
Before (PyEcharts - 50 lines):
bar = Bar()
bar.add_xaxis(quarters)
bar.add_yaxis("Revenue", values, ...)
bar.set_global_opts(...)

line = Line()
line.add_xaxis(quarters)
line.add_yaxis("MA4", ma4_values, ...)

chart = bar.overlap(line)
st_pyecharts(chart)
After (Plotly - 15 lines):
from plotly.subplots import make_subplots
import plotly.graph_objects as go

fig = make_subplots(specs=[[{"secondary_y": True}]])

# Bar
fig.add_trace(go.Bar(x=quarters, y=values, name="Revenue"), secondary_y=False)

# Line
fig.add_trace(go.Scatter(x=quarters, y=ma4_values, mode='lines', name="MA4"), secondary_y=True)

fig.update_layout(title="Revenue Trend")
st.plotly_chart(fig, use_container_width=True)
2. PE/PB Candlestick (Valuation)
New (Plotly Candlestick):
fig = go.Figure(data=[go.Candlestick(
    x=df['date'],
    open=df['pe_open'],
    high=df['pe_high'],
    low=df['pe_low'],
    close=df['pe_close']
)])

fig.update_layout(
    title='PE Ratio Candlestick',
    yaxis_title='PE Ratio',
    xaxis_rangeslider_visible=False
)
st.plotly_chart(fig, use_container_width=True)
Benefits: Same visual as render_pe_pb_dotplot but with Plotly interactivity
3. Sector Heatmap (NEW)
Plotly Heatmap:
fig = go.Figure(data=go.Heatmap(
    z=sector_pe_matrix,
    x=sectors,
    y=metrics,
    colorscale='RdYlGn_r',  # Red (high) to Green (low)
    text=sector_pe_matrix,
    texttemplate='%{text:.1f}',
    colorbar=dict(title="PE Ratio")
))

fig.update_layout(title='Sector PE Heatmap')
st.plotly_chart(fig, use_container_width=True)
🎨 Design System
Color Palette (Professional Theme)
COLORS = {
    # Primary brand colors
    'primary': '#1E40AF',      # Deep blue (main actions)
    'secondary': '#10B981',    # Green (positive/growth)
    'accent': '#F59E0B',       # Amber (highlights)

    # Semantic colors
    'success': '#10B981',      # Green
    'warning': '#F59E0B',      # Amber
    'danger': '#EF4444',       # Red
    'info': '#3B82F6',         # Blue

    # Chart palette (8 colors, color-blind friendly)
    'chart': [
        '#1E40AF',  # Blue
        '#10B981',  # Green
        '#F59E0B',  # Amber
        '#EF4444',  # Red
        '#8B5CF6',  # Purple
        '#EC4899',  # Pink
        '#14B8A6',  # Teal
        '#F97316',  # Orange
    ],

    # Neutral grays
    'gray': {
        50: '#F9FAFB',
        100: '#F3F4F6',
        200: '#E5E7EB',
        300: '#D1D5DB',
        500: '#6B7280',
        700: '#374151',
        900: '#111827',
    },

    # Dark mode support
    'dark': {
        'bg': '#1F2937',
        'surface': '#374151',
        'text': '#F9FAFB',
    }
}
Typography
FONTS = {
    'primary': 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    'monospace': 'JetBrains Mono, Consolas, Monaco, monospace',
    'sizes': {
        'xs': '0.75rem',    # 12px
        'sm': '0.875rem',   # 14px
        'base': '1rem',     # 16px
        'lg': '1.125rem',   # 18px
        'xl': '1.25rem',    # 20px
        '2xl': '1.5rem',    # 24px
        '3xl': '1.875rem',  # 30px
    }
}
Spacing System (Tailwind-inspired)
SPACING = {
    1: '0.25rem',   # 4px
    2: '0.5rem',    # 8px
    3: '0.75rem',   # 12px
    4: '1rem',      # 16px
    6: '1.5rem',    # 24px
    8: '2rem',      # 32px
    12: '3rem',     # 48px
    16: '4rem',     # 64px
}
🔧 Technical Implementation
Phase 1: Foundation & Components (Week 1)
1.1 Create Reusable Plotly Chart Components
File: WEBAPP/components/charts/plotly_builders.py (NEW)
"""
Reusable Plotly chart builders to replace PyEcharts
"""

class PlotlyChartBuilder:
    """Centralized chart building with consistent styling"""

    @staticmethod
    def line_chart(
        df: pd.DataFrame,
        x_col: str,
        y_cols: List[str],
        title: str,
        colors: List[str] = None,
        height: int = 400
    ) -> go.Figure:
        """Build responsive line chart with hover"""

    @staticmethod
    def bar_chart(
        df: pd.DataFrame,
        x_col: str,
        y_col: str,
        title: str,
        color: str = None,
        height: int = 400
    ) -> go.Figure:
        """Build bar chart with value labels"""

    @staticmethod
    def bar_line_combo(
        df: pd.DataFrame,
        x_col: str,
        bar_col: str,
        line_col: str,
        title: str,
        bar_name: str = "Value",
        line_name: str = "MA4",
        height: int = 400
    ) -> go.Figure:
        """Build bar + line combo (replaces PyEcharts overlap)"""

    @staticmethod
    def line_with_bands(
        df: pd.DataFrame,
        x_col: str,
        y_col: str,
        mean_col: str,
        std_col: str,
        title: str,
        height: int = 400
    ) -> go.Figure:
        """Build line with statistical bands (±1σ)"""

    @staticmethod
    def subplot_grid(
        charts: List[Tuple[go.Figure, str]],
        rows: int,
        cols: int,
        title: str,
        height: int = 800
    ) -> go.Figure:
        """Build multi-chart grid layout"""
Migration: Replaces 300+ LOC in bank/company/securities dashboards
1.2 Unified Data Service Layer
File: WEBAPP/services/data_service.py (NEW)
"""
Centralized data service with smart caching and batch loading
"""

class DataService:
    """Single API for all data access across dashboards"""

    def __init__(self):
        self.cache_manager = CacheManager()
        self.paths = DataPaths()
        self.metrics_loader = FinancialMetricsLoader()

    # Batch operations
    def load_symbols_batch(
        self,
        entity_type: str,
        fields: List[str] = None
    ) -> Dict[str, pd.DataFrame]:
        """Load multiple symbols in one operation"""

    def load_sector_data(
        self,
        sector: str,
        metrics: List[str],
        start_date: str
    ) -> pd.DataFrame:
        """Load aggregated sector data"""

    # Smart caching
    def get_cache_key(
        self,
        operation: str,
        params: Dict
    ) -> str:
        """Generate intelligent cache key based on data state"""

    # Error handling
    def safe_load(
        self,
        loader_func: Callable,
        *args,
        fallback: Any = None,
        show_error: bool = True
    ) -> Any:
        """Wrapper with error handling and user feedback"""
Benefits:
Eliminates redundant queries (5x → 1x in company dashboard)
Centralized cache strategy (no more scattered TTLs)
Batch loading for sector/screener pages
Consistent error handling
1.3 Enhanced Navigation Component
File: WEBAPP/components/navigation/enhanced_nav.py (NEW)
"""
Modern navigation with categories and breadcrumbs
"""

def render_main_navigation():
    """Top-level category navigation"""

def render_breadcrumbs(
    path: List[str],
    current_page: str
):
    """Show current location in hierarchy"""

def render_page_tabs(
    tabs: List[str],
    default_tab: int = 0
) -> int:
    """Consistent tab navigation across pages"""

def render_symbol_selector(
    entity_type: str,
    default: str = None,
    key: str = "symbol_select"
) -> str:
    """Reusable symbol dropdown with search"""
1.4 Styling System
File: WEBAPP/styles/theme.py (NEW)
"""
Centralized theming and CSS injection
"""

class Theme:
    """Design system with colors, fonts, spacing"""

    @staticmethod
    def inject_global_css():
        """Load global styles once"""

    @staticmethod
    def get_plotly_theme() -> dict:
        """Plotly figure template matching design system"""

    @staticmethod
    def get_metric_card_style() -> str:
        """CSS for metric display cards"""
Phase 2: Migrate Core Dashboards (Week 2)
2.1 Company Deep Dive (Replaces Company + enhances)
File: WEBAPP/pages/1_fundamental/company_deep_dive.py (NEW) Structure:
def main():
    # 1. Setup
    st.set_page_config(layout="wide", page_title="Company Deep Dive")
    Theme.inject_global_css()
    render_main_navigation()
    render_breadcrumbs(["Home", "Fundamental", "Company Deep Dive"])

    # 2. Sidebar controls
    with st.sidebar:
        symbol = render_symbol_selector("COMPANY", default="VNM")
        year_range = st.slider("Year Range", 2020, 2025, (2022, 2025))

    # 3. Load data ONCE
    data = data_service.load_company_complete(symbol, year_range)

    # 4. Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Overview",
        "💰 Income Statement",
        "🏦 Balance Sheet",
        "💸 Cash Flow"
    ])

    with tab1:
        render_overview_dashboard(data)

    with tab2:
        render_income_statement(data)
    # ... etc
Charts to Build (using PlotlyChartBuilder):
Revenue trend with MA4 (bar + line combo)
Profitability metrics (4 lines: gross/EBIT/EBITDA/net margin)
Growth rates (bar chart: YoY, line: QoQ)
Balance sheet structure (stacked bar: assets vs liabilities)
Cash flow waterfall (Plotly waterfall chart - NEW type)
Performance Optimization:
Load data once at top level
Pass data to render functions (no re-queries)
Use st.cache_data with intelligent keys
2.2 Sector Comparison (Merges Bank + Securities + new Insurance)
File: WEBAPP/pages/1_fundamental/sector_comparison.py (NEW) Structure:
def main():
    # Sector selector
    sector = st.selectbox("Sector", ["Banking", "Securities", "Insurance", "All"])

    # Load sector data in BATCH
    sector_data = data_service.load_sector_data(sector)

    # Tabs by analysis type
    tab1, tab2, tab3 = st.tabs(["Overview", "Detailed Metrics", "Peer Comparison"])

    with tab1:
        # Sector-level KPIs
        render_sector_overview(sector_data)

    with tab2:
        # Multi-select symbols for detailed view
        symbols = st.multiselect("Select Stocks", sector_data.symbols)
        render_detailed_metrics(sector_data, symbols)

    with tab3:
        # Boxplots, scatter plots for peer comparison
        render_peer_comparison(sector_data)
Key Charts:
Sector heatmap (Plotly heatmap - NEW)
Metric distribution (Plotly box plot)
Peer scatter (size = market cap, color = ROE)
Time series comparison (multi-line with legend)
2.3 Valuation Analysis (Enhanced existing)
File: WEBAPP/pages/1_fundamental/valuation_analysis.py (REFACTOR) Enhancements:
Add DCF calculator (NEW feature)
Historical percentile bands (already exists, enhance)
Fair value range based on sector PE
Plotly candlestick for valuation cycles (NEW)
Phase 3: Technical & Intelligence Pages (Week 3)
3.1 Technical Indicators (Refactored Technical dashboard)
File: WEBAPP/pages/2_technical/indicators.py (REFACTOR) Changes:
Split MA screening into dedicated tab
Add RSI heatmap (all stocks, color by RSI level)
Interactive MACD signals with annotations
Volume profile chart (Plotly histogram)
3.2 Market Breadth (NEW - split from Technical)
File: WEBAPP/pages/2_technical/market_breadth.py (NEW) Features:
Advance/Decline line with zones
Sector rotation matrix (heatmap)
Market momentum gauge (Plotly indicator chart - NEW)
Correlation matrix (stocks vs VN-Index)
3.3 Analyst Forecasts (Enhanced Forecast)
File: WEBAPP/pages/3_intelligence/forecasts.py (REFACTOR) Enhancements:
Interactive table with sorting/filtering
Target price vs current price chart
Consensus rating distribution (pie chart)
Historical accuracy tracking (NEW)
3.4 News & Sentiment (Enhanced News)
File: WEBAPP/pages/3_intelligence/news_sentiment.py (REFACTOR) Enhancements:
Real-time sentiment gauge
Word cloud for trending topics (NEW)
News timeline with sentiment overlay
Source credibility scores
Phase 4: Advanced Features (Week 4)
4.1 Global Search
File: WEBAPP/components/search/global_search.py (NEW)
def render_global_search():
    """
    Search across:
    - Stock symbols (autocomplete)
    - Metrics (by Vietnamese/English name)
    - News articles
    - Pages/features
    """
4.2 Dark Mode Toggle
File: WEBAPP/styles/dark_mode.py (NEW)
def render_theme_toggle():
    """Switch between light/dark themes"""

def get_current_theme() -> str:
    """Get active theme from session state"""
4.3 Performance Dashboard (Admin tool)
File: WEBAPP/pages/admin/performance.py (NEW) Metrics:
Cache hit rates per page
Data loading times
User session analytics
Error logs
4.4 Export & Sharing
Features:
Export charts as PNG/SVG/HTML
Share analysis via URL parameters
Download data as CSV/Excel
Generate PDF reports
📁 New File Structure
WEBAPP/
├── main.py                          # Entry point (refactored)
│
├── pages/
│   ├── 1_fundamental/
│   │   ├── company_deep_dive.py     # NEW (replaces company_dashboard)
│   │   ├── sector_comparison.py     # NEW (merges bank + securities)
│   │   └── valuation_analysis.py    # REFACTOR (enhanced)
│   │
│   ├── 2_technical/
│   │   ├── indicators.py            # REFACTOR (split from technical)
│   │   └── market_breadth.py        # NEW (split from technical)
│   │
│   ├── 3_intelligence/
│   │   ├── forecasts.py             # REFACTOR (enhanced)
│   │   └── news_sentiment.py        # REFACTOR (enhanced)
│   │
│   └── 4_tools/
│       ├── screener.py              # NEW (stock screener)
│       ├── portfolio.py             # NEW (portfolio tracking)
│       └── alerts.py                # NEW (price alerts)
│
├── components/
│   ├── charts/
│   │   ├── plotly_builders.py       # NEW (reusable Plotly charts)
│   │   └── chart_templates.py       # NEW (pre-configured charts)
│   │
│   ├── navigation/
│   │   ├── enhanced_nav.py          # NEW (category nav + breadcrumbs)
│   │   └── page_tabs.py             # NEW (consistent tab component)
│   │
│   ├── data_display/
│   │   ├── metric_cards.py          # NEW (KPI cards)
│   │   ├── tables.py                # NEW (formatted tables)
│   │   └── tooltips.py              # NEW (info tooltips)
│   │
│   └── search/
│       └── global_search.py         # NEW (global search)
│
├── services/
│   ├── data_service.py              # NEW (unified data API)
│   ├── cache_manager.py             # NEW (smart caching)
│   └── ... (existing services)
│
├── styles/
│   ├── theme.py                     # NEW (design system)
│   ├── dark_mode.py                 # NEW (dark mode support)
│   └── custom.css                   # NEW (consolidated CSS)
│
├── utils/
│   ├── performance.py               # NEW (monitoring)
│   └── error_handlers.py            # NEW (centralized error handling)
│
└── config/
    ├── navigation_config.json       # NEW (page hierarchy)
    ├── chart_config.json            # NEW (default chart settings)
    └── cache_config.json            # NEW (caching strategy)
Changes:
Delete: company_dashboard_pyecharts.py, bank_dashboard.py, securities_dashboard.py
Refactor: technical_dashboard.py → split into 2 files
Enhance: valuation_sector_dashboard.py, forecast_dashboard.py, news_dashboard.py
Add: 10+ new component files
🚀 Migration Strategy
Step-by-Step Rollout
Week 1: Foundation
 Create components/charts/plotly_builders.py
 Create services/data_service.py with cache manager
 Create styles/theme.py with design system
 Create components/navigation/enhanced_nav.py
 Test component isolation (unit tests)
Week 2: Core Pages
 Migrate Company dashboard → company_deep_dive.py
 Convert 5 income statement charts to Plotly
 Add cash flow waterfall chart
 Implement smart data loading
 Merge Bank + Securities → sector_comparison.py
 Build sector heatmap
 Convert boxplots to Plotly
 Add peer scatter plot
 Test performance (target: <2s load)
Week 3: Technical & Intelligence
 Refactor Technical → split into 2 pages
 Build RSI heatmap
 Add market breadth gauges
 Migrate MA screening table
 Enhance Forecast dashboard
 Add consensus charts
 Improve table interactivity
 Enhance News dashboard
 Add word cloud
 Build sentiment timeline
 Test cross-page navigation
Week 4: Polish & Advanced
 Implement global search
 Add dark mode toggle
 Build performance dashboard
 Add export features
 Comprehensive testing
 Documentation update
Rollback Plan
Keep old pages as _legacy/ backup for 2 weeks
Feature flag for new UI (env var: ENABLE_NEW_UI=true)
A/B testing option in settings
Gradual rollout: 25% → 50% → 100% users
📊 Success Metrics
Performance Targets
Metric	Current	Target	Improvement
Initial Load Time	4-6s	<2s	67% faster
Page Navigation	1-2s	<500ms	75% faster
Chart Render	800ms	<300ms	62% faster
Data Query Count	5-10x	1-2x	80% reduction
Code Duplication	300+ LOC	0 LOC	100% removal
Cache Hit Rate	~40%	>80%	2x efficiency
User Experience Metrics
 Mobile responsiveness score >90 (Lighthouse)
 Accessibility score >85 (WCAG 2.1 AA)
 Page load <3s on 3G connection
 Zero JavaScript errors in console
 All charts interactive (zoom, pan, export)
🎓 Component Library Documentation
PlotlyChartBuilder Usage Examples
# 1. Simple line chart
from WEBAPP.components.charts import PlotlyChartBuilder as pcb

fig = pcb.line_chart(
    df=revenue_df,
    x_col='quarter',
    y_cols=['net_revenue', 'gross_profit'],
    title='Revenue Trend',
    colors=[COLORS['primary'], COLORS['secondary']]
)
st.plotly_chart(fig, use_container_width=True)

# 2. Bar + Line combo (replaces PyEcharts overlap)
fig = pcb.bar_line_combo(
    df=margin_df,
    x_col='quarter',
    bar_col='gross_margin',
    line_col='gross_margin_ma4',
    title='Gross Margin with MA4',
    bar_name='Margin',
    line_name='MA4 Trend'
)
st.plotly_chart(fig, use_container_width=True)

# 3. Line with statistical bands
fig = pcb.line_with_bands(
    df=pe_df,
    x_col='date',
    y_col='pe_ratio',
    mean_col='pe_mean',
    std_col='pe_std',
    title='PE Ratio with ±1σ Bands'
)
st.plotly_chart(fig, use_container_width=True)

# 4. Multi-chart grid
charts = [
    (revenue_chart, 'Revenue'),
    (profit_chart, 'Profit'),
    (margin_chart, 'Margins'),
    (growth_chart, 'Growth')
]
fig = pcb.subplot_grid(
    charts=charts,
    rows=2,
    cols=2,
    title='Financial Overview'
)
st.plotly_chart(fig, use_container_width=True)
DataService Usage Examples
from WEBAPP.services import DataService

ds = DataService()

# Load single symbol (cached intelligently)
company_data = ds.load_company_complete(
    symbol='VNM',
    year_range=(2022, 2025)
)

# Batch load for sector
banking_data = ds.load_sector_data(
    sector='Banking',
    metrics=['roe', 'roa', 'nim', 'cir'],
    start_date='2023-01-01'
)

# Safe loading with error handling
valuation = ds.safe_load(
    loader_func=ds.load_valuation,
    symbol='VNM',
    fallback=None,
    show_error=True  # Shows st.error() to user
)
🔐 Risk Mitigation
Technical Risks
Risk	Impact	Probability	Mitigation
Plotly performance worse than PyEcharts	High	Low	Benchmark early, optimize with webgl mode
Data service introduces latency	Medium	Medium	Implement async loading, progressive rendering
Cache invalidation bugs	High	Medium	Comprehensive testing, monitoring dashboard
Breaking changes in migration	High	Low	Feature flag, gradual rollout, legacy backup
User Impact Risks
Risk	Impact	Mitigation
Users lose familiar navigation	Medium	User testing, migration guide, feedback loop
Chart interactivity confusion	Low	Tooltips, onboarding tour
Dark mode issues	Low	Thorough testing, theme preview
📚 Dependencies & Compatibility
New Requirements
# requirements.txt additions
plotly>=5.18.0          # Latest stable (was 5.15.0)
streamlit>=1.29.0       # Latest with improved caching
pandas>=2.1.0           # No fill_method deprecation warnings
pydantic>=2.5.0         # V2 for better performance

# Remove
pyecharts==2.0.5        # DELETE
streamlit-echarts==0.4.0  # DELETE
Browser Compatibility
Chrome/Edge 90+ ✅
Firefox 88+ ✅
Safari 14+ ✅
Mobile browsers ✅ (responsive design)
🎯 Next Steps After Approval
Week 1 Kickoff:
Create component skeletons
Set up new directory structure
Write unit tests for PlotlyChartBuilder
Weekly Check-ins:
Demo progress each Friday
User feedback sessions
Performance benchmarking
Documentation:
Component library docs
Migration guide for future developers
User guide with screenshots
Deployment:
Staging environment testing (1 week)
Beta user testing (50 users, 1 week)
Full rollout with monitoring
💡 Future Enhancements (Post-MVP)
AI-Powered Features:
Natural language queries ("Show me top 5 stocks by ROE")
Anomaly detection alerts
Predictive analytics
Collaboration:
Share analysis snapshots
Team workspaces
Comments and annotations
Customization:
User-defined dashboards
Custom metric formulas
Saved filters and views
Mobile App:
Native iOS/Android apps
Push notifications for alerts
Offline mode
✅ Checklist for Implementation
Pre-Development
 Review and approve this plan
 Set up feature flag system
 Create backup of current pages
 Set up performance monitoring
 Create design mockups (Figma/Sketch)
Development (Weeks 1-4)
 Week 1: Foundation components
 Week 2: Core dashboard migration
 Week 3: Technical & intelligence pages
 Week 4: Polish & advanced features
Testing
 Unit tests for all components (>80% coverage)
 Integration tests for data flows
 Performance benchmarks
 User acceptance testing
 Accessibility audit
Deployment
 Staging deployment
 Beta user feedback
 Bug fixes and refinements
 Production rollout
 Monitoring and alerts
Post-Launch
 User feedback collection
 Performance optimization
 Documentation updates
 Training materials
Total Effort Estimate: 3-4 weeks (1 developer) Risk Level: Medium (manageable with phased approach) ROI: High (80% performance improvement, better UX, maintainable code) Recommended Decision: ✅ APPROVE & PROCEED This plan provides a comprehensive, phased approach to transforming the dashboard while minimizing risk and maximizing user value.
Stayed in plan mode