# 🚀 ENHANCED ROADMAP PART 2 - Custom MCP, Database & AI Integration

**Continuation from ENHANCED_ROADMAP.md**

---

## 🛠️ PHASE 3: CUSTOM MCP SERVERS FOR ANALYSIS (2-3 weeks)

### 3.1. MCP Architecture Overview

```
┌────────────────────────────────────────────────────────────────┐
│                    MCP ECOSYSTEM                                │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌───────────┐ │
│  │  Data Server    │    │ Analysis Server │    │ Portfolio │ │
│  │                 │    │                 │    │  Server   │ │
│  │  - Query data   │    │  - AI analysis  │    │  - Optim  │ │
│  │  - Schemas      │    │  - Reports      │    │  - Track  │ │
│  │  - Metadata     │    │  - Valuation    │    │  - Alloc  │ │
│  └─────────────────┘    └─────────────────┘    └───────────┘ │
│           │                       │                     │       │
│           └───────────────────────┴─────────────────────┘       │
│                                   │                             │
│                    ┌──────────────▼──────────────┐             │
│                    │   Claude Code               │             │
│                    │   (AI-powered queries)      │             │
│                    └─────────────────────────────┘             │
└────────────────────────────────────────────────────────────────┘
```

### 3.2. Financial Analysis MCP Server

```python
# src/stock_dashboard/mcp/servers/analysis_server.py
"""
Custom MCP Server for Financial Analysis
Provides AI-powered tools for analyzing Vietnamese stocks
"""

from mcp.server import Server
import mcp.types as types
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
from anthropic import Anthropic

from stock_dashboard.database.repositories import (
    CompanyRepository,
    TechnicalRepository,
    ValuationRepository,
    NewsRepository
)
from stock_dashboard.ai.clients import ClaudeClient
from stock_dashboard.processors.valuation import PECalculator, PBCalculator

# Initialize MCP server
mcp = Server("financial-analysis")
claude = ClaudeClient()

# ============================================================
# TOOL 1: Comprehensive Financial Analysis
# ============================================================

@mcp.tool()
async def analyze_company_fundamentals(
    symbol: str,
    periods: int = 12,
    include_comparison: bool = True,
    comparison_symbols: Optional[List[str]] = None
) -> dict:
    """
    Phân tích toàn diện báo cáo tài chính của công ty.

    Args:
        symbol: Mã cổ phiếu (VD: VCB, ACB, HPG)
        periods: Số quý dữ liệu lịch sử (mặc định 12 = 3 năm)
        include_comparison: So sánh với các công ty khác
        comparison_symbols: Danh sách mã để so sánh (nếu None, tự động chọn cùng ngành)

    Returns:
        Dict chứa:
        - financial_metrics: Các chỉ số tài chính
        - trend_analysis: Phân tích xu hướng
        - ai_insights: Nhận định từ AI
        - comparison: So sánh với các công ty khác
        - recommendation: Khuyến nghị đầu tư
    """

    # 1. Fetch fundamental data
    repo = CompanyRepository()
    data = await repo.get_metrics(symbol, periods=periods)

    if data.empty:
        return {"error": f"No data found for {symbol}"}

    # 2. Calculate key ratios
    metrics = calculate_key_metrics(data)

    # 3. Trend analysis
    trends = analyze_trends(data)

    # 4. Comparison with peers
    comparison_data = None
    if include_comparison:
        if comparison_symbols is None:
            # Auto-select peers in same industry
            comparison_symbols = await get_industry_peers(symbol, limit=5)

        comparison_data = await compare_with_peers(symbol, comparison_symbols, periods)

    # 5. AI-powered analysis
    ai_prompt = f"""
Phân tích báo cáo tài chính công ty {symbol}:

## Dữ liệu {periods} quý gần nhất:
- Doanh thu (tỷ VND): {format_series(data['revenue'] / 1e9)}
- Lợi nhuận sau thuế (tỷ VND): {format_series(data['net_profit'] / 1e9)}
- ROE (%): {format_series(data['roe'] * 100)}
- ROA (%): {format_series(data['roa'] * 100)}
- Biên lợi nhuận (%): {format_series(data['profit_margin'] * 100)}
- Tỷ lệ nợ/vốn chủ: {format_series(data['debt_to_equity'])}

## Xu hướng:
{format_trends(trends)}

{"## So sánh với các công ty cùng ngành:" if comparison_data else ""}
{format_comparison(comparison_data) if comparison_data else ""}

Hãy phân tích và đưa ra:
1. Đánh giá sức khỏe tài chính (điểm từ 1-10)
2. Xu hướng tăng trưởng (tích cực/tiêu cực/ổn định)
3. Các điểm mạnh nổi bật
4. Các rủi ro cần lưu ý
5. Khuyến nghị đầu tư (MUA/GIỮ/BÁN) với lý do cụ thể

Trả lời bằng tiếng Việt, ngắn gọn và dễ hiểu.
"""

    ai_insights = await claude.generate(
        prompt=ai_prompt,
        max_tokens=2048,
        temperature=0.3  # Lower temperature for more consistent financial analysis
    )

    # 6. Extract recommendation from AI response
    recommendation = extract_recommendation(ai_insights)

    return {
        "symbol": symbol,
        "analysis_date": datetime.now().isoformat(),
        "periods_analyzed": periods,
        "metrics": metrics,
        "trends": trends,
        "comparison": comparison_data,
        "ai_insights": ai_insights,
        "recommendation": recommendation,
        "data_source": "TimescaleDB + MongoDB"
    }

# ============================================================
# TOOL 2: Technical Analysis with AI
# ============================================================

@mcp.tool()
async def generate_trading_signals(
    symbol: str,
    timeframe: str = "daily",
    lookback_days: int = 90
) -> dict:
    """
    Tạo tín hiệu giao dịch dựa trên phân tích kỹ thuật + AI.

    Args:
        symbol: Mã cổ phiếu
        timeframe: Khung thời gian (daily, weekly)
        lookback_days: Số ngày dữ liệu lịch sử

    Returns:
        Dict chứa tín hiệu giao dịch và phân tích
    """

    # 1. Fetch technical data
    tech_repo = TechnicalRepository()
    data = await tech_repo.get_indicators(
        symbol=symbol,
        start_date=datetime.now() - timedelta(days=lookback_days),
        end_date=datetime.now()
    )

    if data.empty:
        return {"error": f"No technical data for {symbol}"}

    # 2. Extract latest indicators
    latest = data.iloc[-1]
    prev_5 = data.iloc[-6:-1]  # Previous 5 days for trend

    indicators = {
        "price": latest['close'],
        "rsi": latest['rsi'],
        "macd": latest['macd'],
        "macd_signal": latest['macd_signal'],
        "macd_histogram": latest['macd_histogram'],
        "sma_20": latest['sma_20'],
        "sma_50": latest['sma_50'],
        "sma_200": latest['sma_200'],
        "bb_upper": latest['bb_upper'],
        "bb_middle": latest['bb_middle'],
        "bb_lower": latest['bb_lower'],
        "volume": latest['volume'],
        "volume_sma_20": latest['volume_sma_20']
    }

    # 3. Calculate signals
    signals = {
        "rsi_signal": get_rsi_signal(indicators['rsi']),
        "macd_signal": get_macd_signal(
            indicators['macd'],
            indicators['macd_signal'],
            indicators['macd_histogram']
        ),
        "moving_average_signal": get_ma_signal(
            indicators['price'],
            indicators['sma_20'],
            indicators['sma_50'],
            indicators['sma_200']
        ),
        "bollinger_signal": get_bb_signal(
            indicators['price'],
            indicators['bb_upper'],
            indicators['bb_middle'],
            indicators['bb_lower']
        ),
        "volume_signal": get_volume_signal(
            indicators['volume'],
            indicators['volume_sma_20']
        )
    }

    # 4. AI analysis
    ai_prompt = f"""
Phân tích kỹ thuật cho {symbol}:

## Chỉ báo hiện tại:
- Giá: {indicators['price']:,.0f} VND
- RSI(14): {indicators['rsi']:.2f} {"(Oversold)" if indicators['rsi'] < 30 else "(Overbought)" if indicators['rsi'] > 70 else ""}
- MACD: {indicators['macd']:.2f}, Signal: {indicators['macd_signal']:.2f}, Histogram: {indicators['macd_histogram']:.2f}
- SMA(20): {indicators['sma_20']:,.0f}, SMA(50): {indicators['sma_50']:,.0f}, SMA(200): {indicators['sma_200']:,.0f}
- Bollinger Bands: Upper {indicators['bb_upper']:,.0f}, Middle {indicators['bb_middle']:,.0f}, Lower {indicators['bb_lower']:,.0f}
- Volume: {indicators['volume']:,.0f} (Trung bình: {indicators['volume_sma_20']:,.0f})

## Tín hiệu tự động:
- RSI: {signals['rsi_signal']}
- MACD: {signals['macd_signal']}
- Moving Averages: {signals['moving_average_signal']}
- Bollinger Bands: {signals['bollinger_signal']}
- Volume: {signals['volume_signal']}

Dựa trên các chỉ báo trên, hãy:
1. Đưa ra tín hiệu giao dịch rõ ràng (MUA/BÁN/GIỮ)
2. Giải thích lý do ngắn gọn (2-3 câu)
3. Đề xuất mức giá vào lệnh (entry) và chốt lời (target)
4. Đề xuất mức cắt lỗ (stop-loss)
5. Đánh giá độ tin cậy của tín hiệu (cao/trung bình/thấp)

Trả lời bằng tiếng Việt, ngắn gọn.
"""

    ai_analysis = await claude.generate(
        prompt=ai_prompt,
        max_tokens=1024,
        temperature=0.2
    )

    # 5. Extract structured signal
    trading_signal = extract_trading_signal(ai_analysis)

    return {
        "symbol": symbol,
        "timestamp": datetime.now().isoformat(),
        "timeframe": timeframe,
        "indicators": indicators,
        "automated_signals": signals,
        "ai_analysis": ai_analysis,
        "trading_signal": trading_signal,
        "chart_url": generate_chart_url(symbol, lookback_days)
    }

# ============================================================
# TOOL 3: Fair Value Estimation
# ============================================================

@mcp.tool()
async def estimate_fair_value(
    symbol: str,
    method: str = "dcf",  # dcf, pe_multiple, pb_multiple, hybrid
    assumptions: Optional[Dict[str, float]] = None
) -> dict:
    """
    Ước tính giá trị hợp lý của cổ phiếu.

    Args:
        symbol: Mã cổ phiếu
        method: Phương pháp định giá (dcf, pe_multiple, pb_multiple, hybrid)
        assumptions: Các giả định cho model (growth_rate, discount_rate, etc.)

    Returns:
        Dict với giá trị hợp lý và phân tích
    """

    # Default assumptions
    if assumptions is None:
        assumptions = {
            "growth_rate": 0.10,  # 10% growth
            "discount_rate": 0.12,  # 12% discount rate
            "terminal_growth": 0.03,  # 3% terminal growth
            "projection_years": 5
        }

    # 1. Fetch financial data
    company_repo = CompanyRepository()
    data = await company_repo.get_metrics(symbol, periods=12)

    if data.empty:
        return {"error": f"No data for {symbol}"}

    # 2. Get current price and valuation ratios
    valuation_repo = ValuationRepository()
    current_valuation = await valuation_repo.get_latest(symbol)

    current_price = current_valuation['close']
    current_pe = current_valuation['pe']
    current_pb = current_valuation['pb']

    # 3. Calculate fair value based on method
    if method == "dcf":
        fair_value = calculate_dcf_value(data, assumptions)
        method_name = "Discounted Cash Flow (DCF)"

    elif method == "pe_multiple":
        fair_value = calculate_pe_multiple_value(data, current_valuation)
        method_name = "P/E Multiple"

    elif method == "pb_multiple":
        fair_value = calculate_pb_multiple_value(data, current_valuation)
        method_name = "P/B Multiple"

    else:  # hybrid
        dcf_value = calculate_dcf_value(data, assumptions)
        pe_value = calculate_pe_multiple_value(data, current_valuation)
        pb_value = calculate_pb_multiple_value(data, current_valuation)

        # Weighted average
        fair_value = (dcf_value * 0.5 + pe_value * 0.3 + pb_value * 0.2)
        method_name = "Hybrid (DCF + PE + PB)"

    # 4. Calculate upside/downside
    upside_pct = ((fair_value - current_price) / current_price) * 100

    # 5. AI valuation commentary
    ai_prompt = f"""
Phân tích định giá cho {symbol}:

## Thông tin hiện tại:
- Giá hiện tại: {current_price:,.0f} VND
- P/E hiện tại: {current_pe:.2f}
- P/B hiện tại: {current_pb:.2f}

## Kết quả định giá:
- Phương pháp: {method_name}
- Giá trị hợp lý ước tính: {fair_value:,.0f} VND
- Chênh lệch: {upside_pct:+.2f}%

## Giả định:
{format_assumptions(assumptions)}

## Dữ liệu tài chính:
- EPS (12 tháng gần nhất): {data['eps'].iloc[-4:].sum():,.0f} VND
- Book Value/Share: {data['book_value_per_share'].iloc[-1]:,.0f} VND
- ROE trung bình: {data['roe'].mean() * 100:.2f}%
- Tăng trưởng doanh thu trung bình: {calculate_revenue_growth(data) * 100:.2f}%

Hãy:
1. Đánh giá tính hợp lý của định giá (quá cao/hợp lý/quá thấp)
2. Giải thích ngắn gọn lý do
3. Đưa ra khuyến nghị (MUA/GIỮ/BÁN)
4. Nêu các rủi ro có thể ảnh hưởng đến định giá

Trả lời bằng tiếng Việt.
"""

    ai_commentary = await claude.generate(
        prompt=ai_prompt,
        max_tokens=1536,
        temperature=0.3
    )

    return {
        "symbol": symbol,
        "valuation_date": datetime.now().isoformat(),
        "method": method_name,
        "current_price": current_price,
        "fair_value": fair_value,
        "upside_downside_pct": upside_pct,
        "assumptions": assumptions,
        "valuation_metrics": {
            "current_pe": current_pe,
            "current_pb": current_pb,
            "estimated_pe": fair_value / (data['eps'].iloc[-4:].sum()) if method != "pb_multiple" else None,
            "estimated_pb": fair_value / data['book_value_per_share'].iloc[-1] if method != "pe_multiple" else None
        },
        "ai_commentary": ai_commentary,
        "recommendation": extract_recommendation(ai_commentary)
    }

# ============================================================
# TOOL 4: News Sentiment Analysis
# ============================================================

@mcp.tool()
async def analyze_news_sentiment(
    symbol: str,
    days: int = 7,
    min_articles: int = 3
) -> dict:
    """
    Phân tích sentiment từ tin tức về công ty.

    Args:
        symbol: Mã cổ phiếu
        days: Số ngày tin tức
        min_articles: Số bài viết tối thiểu

    Returns:
        Dict với sentiment analysis và key topics
    """

    # 1. Fetch news
    news_repo = NewsRepository()
    news_df = await news_repo.get_news(
        symbol=symbol,
        start_date=datetime.now() - timedelta(days=days),
        end_date=datetime.now()
    )

    if len(news_df) < min_articles:
        return {
            "error": f"Insufficient news articles for {symbol}",
            "articles_found": len(news_df),
            "required": min_articles
        }

    # 2. Calculate sentiment scores
    sentiment_scores = news_df['sentiment_score'].tolist()
    avg_sentiment = news_df['sentiment_score'].mean()

    # 3. Extract key topics using AI
    news_summaries = "\n\n".join([
        f"[{row['published_date']}] {row['title']}\n{row['summary'][:200]}..."
        for _, row in news_df.head(10).iterrows()
    ])

    ai_prompt = f"""
Phân tích tin tức về {symbol} trong {days} ngày qua:

Có {len(news_df)} bài viết. Sentiment trung bình: {avg_sentiment:.2f} (từ -1 đến +1)

## Các tin tức gần đây:
{news_summaries}

Hãy:
1. Tóm tắt các chủ đề chính (2-3 điểm)
2. Đánh giá sentiment tổng thể (tích cực/tiêu cực/trung lập)
3. Xác định các sự kiện quan trọng (nếu có)
4. Đánh giá tác động có thể lên giá cổ phiếu (tích cực/tiêu cực/không rõ ràng)

Trả lời bằng tiếng Việt, ngắn gọn.
"""

    ai_analysis = await claude.generate(
        prompt=ai_prompt,
        max_tokens=1024,
        temperature=0.4
    )

    return {
        "symbol": symbol,
        "period_days": days,
        "articles_analyzed": len(news_df),
        "sentiment_score": avg_sentiment,
        "sentiment_distribution": {
            "positive": len(news_df[news_df['sentiment_score'] > 0.3]),
            "neutral": len(news_df[(news_df['sentiment_score'] >= -0.3) & (news_df['sentiment_score'] <= 0.3)]),
            "negative": len(news_df[news_df['sentiment_score'] < -0.3])
        },
        "recent_headlines": news_df.head(5)[['published_date', 'title', 'sentiment_score']].to_dict('records'),
        "ai_analysis": ai_analysis,
        "impact_assessment": extract_impact(ai_analysis)
    }

# ============================================================
# TOOL 5: Portfolio Optimization
# ============================================================

@mcp.tool()
async def optimize_portfolio(
    symbols: List[str],
    objective: str = "sharpe",  # sharpe, min_volatility, max_return
    constraints: Optional[Dict[str, Any]] = None
) -> dict:
    """
    Tối ưu hóa danh mục đầu tư.

    Args:
        symbols: Danh sách mã cổ phiếu
        objective: Mục tiêu tối ưu (sharpe, min_volatility, max_return)
        constraints: Ràng buộc (max_position_size, min_position_size, sector_limits)

    Returns:
        Dict với allocation tối ưu
    """

    # Import optimization libraries
    import numpy as np
    from scipy.optimize import minimize

    # Default constraints
    if constraints is None:
        constraints = {
            "max_position_size": 0.30,  # Max 30% per stock
            "min_position_size": 0.05,  # Min 5% per stock
            "risk_free_rate": 0.05      # 5% risk-free rate
        }

    # 1. Fetch historical returns
    returns_data = {}
    for symbol in symbols:
        tech_repo = TechnicalRepository()
        data = await tech_repo.get_prices(
            symbol=symbol,
            start_date=datetime.now() - timedelta(days=365),
            end_date=datetime.now()
        )
        returns_data[symbol] = data['close'].pct_change().dropna()

    # 2. Calculate covariance matrix and expected returns
    returns_df = pd.DataFrame(returns_data)
    cov_matrix = returns_df.cov() * 252  # Annualized
    expected_returns = returns_df.mean() * 252  # Annualized

    # 3. Optimize portfolio
    n_assets = len(symbols)

    if objective == "sharpe":
        weights = optimize_sharpe_ratio(
            expected_returns,
            cov_matrix,
            constraints['risk_free_rate']
        )
    elif objective == "min_volatility":
        weights = optimize_min_volatility(cov_matrix)
    else:  # max_return
        weights = optimize_max_return(expected_returns, cov_matrix)

    # Apply constraints
    weights = apply_constraints(weights, constraints)

    # 4. Calculate portfolio metrics
    portfolio_return = np.dot(weights, expected_returns)
    portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
    sharpe_ratio = (portfolio_return - constraints['risk_free_rate']) / portfolio_volatility

    # 5. AI portfolio commentary
    allocation_str = "\n".join([
        f"- {symbol}: {weight*100:.2f}%"
        for symbol, weight in zip(symbols, weights)
    ])

    ai_prompt = f"""
Phân tích danh mục đầu tư tối ưu:

## Cấu trúc danh mục:
{allocation_str}

## Chỉ số:
- Lợi nhuận kỳ vọng hàng năm: {portfolio_return * 100:.2f}%
- Độ biến động (volatility): {portfolio_volatility * 100:.2f}%
- Sharpe Ratio: {sharpe_ratio:.2f}

## Mục tiêu tối ưu: {objective}

Hãy:
1. Đánh giá sự đa dạng hóa của danh mục
2. Nhận xét về rủi ro/lợi nhuận
3. Đề xuất điều chỉnh (nếu cần)
4. Đưa ra lưu ý khi đầu tư

Trả lời bằng tiếng Việt.
"""

    ai_commentary = await claude.generate(
        prompt=ai_prompt,
        max_tokens=1536,
        temperature=0.3
    )

    return {
        "optimization_date": datetime.now().isoformat(),
        "objective": objective,
        "symbols": symbols,
        "optimal_weights": {
            symbol: float(weight)
            for symbol, weight in zip(symbols, weights)
        },
        "portfolio_metrics": {
            "expected_return_annual": float(portfolio_return),
            "volatility_annual": float(portfolio_volatility),
            "sharpe_ratio": float(sharpe_ratio)
        },
        "constraints_applied": constraints,
        "ai_commentary": ai_commentary
    }

# ============================================================
# Resources: List available datasets
# ============================================================

@mcp.resource("financial://datasets")
async def list_datasets() -> List[types.Resource]:
    """List all available financial datasets."""

    datasets = [
        {
            "uri": "financial://ohlcv",
            "name": "OHLCV Price Data",
            "description": "Daily OHLCV data for all Vietnamese stocks",
            "source": "vnstock_data + TimescaleDB"
        },
        {
            "uri": "financial://fundamental",
            "name": "Fundamental Data",
            "description": "Quarterly financial statements (company, bank, insurance, security)",
            "source": "vnstock_data + TimescaleDB"
        },
        {
            "uri": "financial://technical",
            "name": "Technical Indicators",
            "description": "RSI, MACD, Bollinger Bands, Moving Averages, etc.",
            "source": "vnstock_ta + TimescaleDB"
        },
        {
            "uri": "financial://news",
            "name": "News & Sentiment",
            "description": "News articles with AI sentiment analysis",
            "source": "vnstock_news + MongoDB"
        },
        {
            "uri": "financial://valuation",
            "name": "Valuation Metrics",
            "description": "P/E, P/B, EV/EBITDA ratios",
            "source": "Custom calculators + TimescaleDB"
        }
    ]

    return [
        types.Resource(
            uri=ds["uri"],
            name=ds["name"],
            description=ds["description"],
            mimeType="application/json"
        )
        for ds in datasets
    ]

# ============================================================
# Helper Functions
# ============================================================

def calculate_key_metrics(data: pd.DataFrame) -> Dict[str, Any]:
    """Calculate key financial metrics."""
    latest = data.iloc[-1]

    return {
        "revenue_latest": float(latest['revenue']),
        "net_profit_latest": float(latest['net_profit']),
        "roe": float(latest['roe']),
        "roa": float(latest['roa']),
        "profit_margin": float(latest['profit_margin']),
        "debt_to_equity": float(latest['debt_to_equity']),
        "eps": float(latest['eps']),
        "book_value_per_share": float(latest['book_value_per_share'])
    }

def analyze_trends(data: pd.DataFrame) -> Dict[str, str]:
    """Analyze financial trends."""
    revenue_trend = "increasing" if data['revenue'].iloc[-1] > data['revenue'].iloc[0] else "decreasing"
    profit_trend = "increasing" if data['net_profit'].iloc[-1] > data['net_profit'].iloc[0] else "decreasing"
    margin_trend = "improving" if data['profit_margin'].iloc[-1] > data['profit_margin'].iloc[0] else "declining"

    return {
        "revenue": revenue_trend,
        "profit": profit_trend,
        "margin": margin_trend
    }

def format_series(series: pd.Series) -> str:
    """Format pandas series for prompt."""
    return ", ".join([f"{val:.2f}" for val in series.tail(4)])

def format_trends(trends: Dict[str, str]) -> str:
    """Format trends dict."""
    return "\n".join([f"- {key.title()}: {value}" for key, value in trends.items()])

def extract_recommendation(ai_text: str) -> Dict[str, Any]:
    """Extract structured recommendation from AI response."""
    # Simple keyword-based extraction (can be improved with regex/NLP)
    text_lower = ai_text.lower()

    if "mua" in text_lower or "buy" in text_lower:
        action = "BUY"
    elif "bán" in text_lower or "sell" in text_lower:
        action = "SELL"
    else:
        action = "HOLD"

    return {
        "action": action,
        "full_text": ai_text
    }

# Export MCP server
if __name__ == "__main__":
    import asyncio
    from mcp.server.stdio import stdio_server

    async def main():
        async with stdio_server() as (read_stream, write_stream):
            await mcp.run(
                read_stream,
                write_stream,
                mcp.create_initialization_options()
            )

    asyncio.run(main())
```

### 3.3. MCP Server Configuration

```json
// configs/mcp_servers.json
{
  "mcpServers": {
    "stock-data": {
      "command": "python",
      "args": ["-m", "stock_dashboard.mcp.servers.data_server"],
      "description": "Query stock datasets (OHLCV, fundamental, technical)",
      "tools": [
        "query_ohlcv",
        "query_fundamental",
        "query_technical",
        "get_schema",
        "list_symbols"
      ]
    },

    "financial-analysis": {
      "command": "python",
      "args": ["-m", "stock_dashboard.mcp.servers.analysis_server"],
      "description": "AI-powered financial analysis",
      "tools": [
        "analyze_company_fundamentals",
        "generate_trading_signals",
        "estimate_fair_value",
        "analyze_news_sentiment",
        "optimize_portfolio"
      ],
      "requires": ["ANTHROPIC_API_KEY"]
    },

    "portfolio-manager": {
      "command": "python",
      "args": ["-m", "stock_dashboard.mcp.servers.portfolio_server"],
      "description": "Portfolio tracking and optimization",
      "tools": [
        "track_portfolio",
        "calculate_performance",
        "rebalance_portfolio",
        "risk_analysis",
        "tax_optimization"
      ]
    },

    "alert-manager": {
      "command": "python",
      "args": ["-m", "stock_dashboard.mcp.servers.alert_server"],
      "description": "Manage real-time alerts",
      "tools": [
        "create_alert",
        "list_alerts",
        "update_alert",
        "delete_alert",
        "get_alert_history"
      ]
    }
  }
}
```

### 3.4. Claude Skills cho Financial Analysis

```json
// .claude/skills/financial-analyst/skill.json
{
  "name": "financial-analyst",
  "version": "2.0.0",
  "description": "Comprehensive financial analysis for Vietnamese stocks with AI",
  "author": "Stock Dashboard Team",

  "triggers": [
    "analyze {symbol}",
    "phân tích {symbol}",
    "fundamental analysis {symbol}",
    "estimate fair value {symbol}",
    "trading signal {symbol}"
  ],

  "mcp_servers": [
    "financial-analysis",
    "stock-data"
  ],

  "tools": [
    {
      "server": "financial-analysis",
      "name": "analyze_company_fundamentals",
      "description": "Deep fundamental analysis with AI insights"
    },
    {
      "server": "financial-analysis",
      "name": "generate_trading_signals",
      "description": "Technical analysis and trading signals"
    },
    {
      "server": "financial-analysis",
      "name": "estimate_fair_value",
      "description": "Fair value estimation using multiple methods"
    }
  ],

  "prompts_dir": "./prompts",
  "examples_dir": "./examples"
}
```

```markdown
<!-- .claude/skills/financial-analyst/prompts/main.md -->
# Financial Analyst Skill

You are an expert financial analyst specializing in Vietnamese stock market.

## Your Capabilities

You have access to the following MCP tools:
1. **analyze_company_fundamentals**: Deep fundamental analysis
2. **generate_trading_signals**: Technical analysis with AI
3. **estimate_fair_value**: Valuation using DCF, PE, PB methods
4. **analyze_news_sentiment**: News sentiment analysis
5. **optimize_portfolio**: Portfolio optimization

## Response Format

When analyzing a stock, follow this structure:

### 1. Executive Summary
- Current price and valuation (PE, PB)
- Quick recommendation (BUY/HOLD/SELL)
- Key strength and risk (1-2 sentences each)

### 2. Fundamental Analysis
- Financial health score (1-10)
- Revenue and profit trends
- Profitability metrics (ROE, ROA, Margins)
- Comparison with industry peers

### 3. Technical Analysis
- Current technical indicators
- Trading signals (RSI, MACD, Moving Averages)
- Support/Resistance levels
- Entry/Exit recommendations

### 4. Valuation
- Fair value estimation
- Upside/Downside potential
- Valuation comparison (cheap/fair/expensive)

### 5. News & Sentiment
- Recent news summary
- Sentiment analysis
- Impact assessment

### 6. Final Recommendation
- Clear action (BUY/HOLD/SELL)
- Price targets (entry, target, stop-loss)
- Time horizon
- Risk level

## Example Usage

User: "Phân tích VCB"

You should:
1. Call `analyze_company_fundamentals(symbol="VCB", periods=12)`
2. Call `generate_trading_signals(symbol="VCB")`
3. Call `estimate_fair_value(symbol="VCB", method="hybrid")`
4. Call `analyze_news_sentiment(symbol="VCB", days=7)`
5. Synthesize all data into comprehensive analysis
6. Present in Vietnamese using the format above

## Important Notes

- Always use Vietnamese for responses
- Be objective and data-driven
- Clearly state assumptions
- Highlight both risks and opportunities
- Provide actionable recommendations
```

### ✅ Ưu điểm Phase 3

1. **AI-powered analysis**: Claude phân tích sâu, không chỉ rule-based
2. **Comprehensive tools**: 5 tools cover all analysis needs
3. **Flexible**: Dễ thêm tools mới
4. **Standardized**: MCP protocol, tương thích với Claude Code
5. **Reusable**: Skills có thể share cho team

### ⚠️ Nhược điểm Phase 3

1. **API costs**: Claude API không free (nhưng affordable)
2. **Response time**: AI generation mất 2-5s
3. **Complexity**: Nhiều components phải maintain
4. **Accuracy**: AI có thể hallucinate, cần validate

### 💰 Chi phí Phase 3

- **Development**: 2-3 weeks
- **API costs (monthly)**:
  - Claude API: $10-50/month (depends on usage)
  - OpenAI Embeddings: $5-10/month
- **Total**: $15-60/month

---

## 💾 PHASE 4: SCALABLE DATABASE ARCHITECTURE (2 weeks)

### 4.1. Multi-Database Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DATABASE LAYER                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐    ┌──────────────────┐             │
│  │  TimescaleDB     │    │    MongoDB       │             │
│  │  (Time-series)   │    │   (Documents)    │             │
│  │                  │    │                  │             │
│  │  - OHLCV         │    │  - News          │             │
│  │  - Technical     │    │  - Reports       │             │
│  │  - Fundamental   │    │  - Alerts        │             │
│  │  - Valuation     │    │  - Analysis      │             │
│  └──────────────────┘    └──────────────────┘             │
│           │                        │                        │
│           └────────────┬───────────┘                        │
│                        │                                    │
│              ┌─────────▼────────┐                          │
│              │     Redis        │                          │
│              │  (Cache/Pub-Sub) │                          │
│              │                  │                          │
│              │  - Query cache   │                          │
│              │  - Session       │                          │
│              │  - Pub/Sub       │                          │
│              └──────────────────┘                          │
│                        │                                    │
│              ┌─────────▼────────┐                          │
│              │    Qdrant        │                          │
│              │  (Vector Store)  │                          │
│              │                  │                          │
│              │  - Embeddings    │                          │
│              │  - Semantic      │                          │
│              │    Search        │                          │
│              └──────────────────┘                          │
└─────────────────────────────────────────────────────────────┘
```

### 4.2. TimescaleDB Setup (Time-series)

```sql
-- init_timescaledb.sql

-- Create database
CREATE DATABASE stock_timeseries;
\c stock_timeseries;

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- ============================================================
-- OHLCV Table (Hypertable)
-- ============================================================

CREATE TABLE ohlcv (
    time TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    open NUMERIC(15, 2),
    high NUMERIC(15, 2),
    low NUMERIC(15, 2),
    close NUMERIC(15, 2),
    volume BIGINT,
    trading_value NUMERIC(20, 2),
    shares_outstanding BIGINT,
    market_cap NUMERIC(20, 2)
);

-- Convert to hypertable
SELECT create_hypertable('ohlcv', 'time');

-- Create indexes
CREATE INDEX ON ohlcv (symbol, time DESC);
CREATE INDEX ON ohlcv (time DESC, symbol);

-- ============================================================
-- Technical Indicators Table
-- ============================================================

CREATE TABLE technical_indicators (
    time TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(20) NOT NULL,

    -- Moving Averages
    sma_5 NUMERIC(15, 2),
    sma_10 NUMERIC(15, 2),
    sma_20 NUMERIC(15, 2),
    sma_50 NUMERIC(15, 2),
    sma_200 NUMERIC(15, 2),
    ema_12 NUMERIC(15, 2),
    ema_26 NUMERIC(15, 2),

    -- Momentum Indicators
    rsi NUMERIC(5, 2),
    macd NUMERIC(10, 4),
    macd_signal NUMERIC(10, 4),
    macd_histogram NUMERIC(10, 4),

    -- Bollinger Bands
    bb_upper NUMERIC(15, 2),
    bb_middle NUMERIC(15, 2),
    bb_lower NUMERIC(15, 2),
    bb_width NUMERIC(10, 4),

    -- Volume Indicators
    volume_sma_20 BIGINT,
    volume_ratio NUMERIC(10, 4),

    -- Volatility
    atr NUMERIC(10, 4),
    volatility_30d NUMERIC(10, 6)
);

SELECT create_hypertable('technical_indicators', 'time');
CREATE INDEX ON technical_indicators (symbol, time DESC);

-- ============================================================
-- Fundamental Data Table
-- ============================================================

CREATE TABLE fundamental_data (
    time TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    entity_type VARCHAR(20), -- company, bank, insurance, security
    year INT,
    quarter INT,

    -- Income Statement
    revenue NUMERIC(20, 2),
    cost_of_goods_sold NUMERIC(20, 2),
    gross_profit NUMERIC(20, 2),
    operating_expenses NUMERIC(20, 2),
    operating_profit NUMERIC(20, 2),
    interest_expense NUMERIC(20, 2),
    pre_tax_profit NUMERIC(20, 2),
    tax_expense NUMERIC(20, 2),
    net_profit NUMERIC(20, 2),

    -- Balance Sheet
    total_assets NUMERIC(20, 2),
    current_assets NUMERIC(20, 2),
    fixed_assets NUMERIC(20, 2),
    total_liabilities NUMERIC(20, 2),
    current_liabilities NUMERIC(20, 2),
    long_term_debt NUMERIC(20, 2),
    equity NUMERIC(20, 2),

    -- Cash Flow
    operating_cash_flow NUMERIC(20, 2),
    investing_cash_flow NUMERIC(20, 2),
    financing_cash_flow NUMERIC(20, 2),
    free_cash_flow NUMERIC(20, 2),

    -- Ratios
    roe NUMERIC(10, 6),
    roa NUMERIC(10, 6),
    profit_margin NUMERIC(10, 6),
    debt_to_equity NUMERIC(10, 4),
    current_ratio NUMERIC(10, 4),
    quick_ratio NUMERIC(10, 4),

    -- Per Share
    eps NUMERIC(15, 2),
    book_value_per_share NUMERIC(15, 2),

    -- Metadata
    source VARCHAR(50),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

SELECT create_hypertable('fundamental_data', 'time');
CREATE INDEX ON fundamental_data (symbol, time DESC);
CREATE INDEX ON fundamental_data (entity_type, time DESC);
CREATE INDEX ON fundamental_data (year DESC, quarter DESC);

-- ============================================================
-- Valuation Metrics Table
-- ============================================================

CREATE TABLE valuation_metrics (
    time TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(20) NOT NULL,

    pe_ratio NUMERIC(10, 4),
    pb_ratio NUMERIC(10, 4),
    ps_ratio NUMERIC(10, 4),
    pcf_ratio NUMERIC(10, 4),
    ev_ebitda NUMERIC(10, 4),

    -- Historical percentiles
    pe_percentile_1y NUMERIC(5, 2),
    pb_percentile_1y NUMERIC(5, 2),

    -- Industry comparison
    industry_avg_pe NUMERIC(10, 4),
    industry_avg_pb NUMERIC(10, 4),

    updated_at TIMESTAMPTZ DEFAULT NOW()
);

SELECT create_hypertable('valuation_metrics', 'time');
CREATE INDEX ON valuation_metrics (symbol, time DESC);

-- ============================================================
-- Continuous Aggregates (for performance)
-- ============================================================

-- Daily OHLCV aggregate
CREATE MATERIALIZED VIEW ohlcv_daily
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 day', time) AS day,
    symbol,
    FIRST(open, time) AS open,
    MAX(high) AS high,
    MIN(low) AS low,
    LAST(close, time) AS close,
    SUM(volume) AS volume,
    SUM(trading_value) AS trading_value,
    LAST(market_cap, time) AS market_cap
FROM ohlcv
GROUP BY day, symbol;

-- Weekly OHLCV aggregate
CREATE MATERIALIZED VIEW ohlcv_weekly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('7 days', time) AS week,
    symbol,
    FIRST(open, time) AS open,
    MAX(high) AS high,
    MIN(low) AS low,
    LAST(close, time) AS close,
    SUM(volume) AS volume,
    SUM(trading_value) AS trading_value,
    AVG(market_cap) AS avg_market_cap
FROM ohlcv
GROUP BY week, symbol;

-- Add refresh policy
SELECT add_continuous_aggregate_policy('ohlcv_daily',
    start_offset => INTERVAL '3 days',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour');

SELECT add_continuous_aggregate_policy('ohlcv_weekly',
    start_offset => INTERVAL '3 weeks',
    end_offset => INTERVAL '1 day',
    schedule_interval => INTERVAL '1 day');

-- ============================================================
-- Compression Policy (save storage)
-- ============================================================

-- Enable compression
ALTER TABLE ohlcv SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'symbol',
    timescaledb.compress_orderby = 'time DESC'
);

-- Auto-compress data older than 7 days
SELECT add_compression_policy('ohlcv', INTERVAL '7 days');

-- Repeat for other hypertables
ALTER TABLE technical_indicators SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'symbol',
    timescaledb.compress_orderby = 'time DESC'
);
SELECT add_compression_policy('technical_indicators', INTERVAL '7 days');

-- ============================================================
-- Data Retention Policy (optional)
-- ============================================================

-- Keep only 5 years of data
SELECT add_retention_policy('ohlcv', INTERVAL '5 years');
SELECT add_retention_policy('technical_indicators', INTERVAL '5 years');
SELECT add_retention_policy('fundamental_data', INTERVAL '10 years');
```

### 4.3. Repository Pattern Implementation

```python
# src/stock_dashboard/database/repositories/timeseries_repo.py
"""
Repository pattern for TimescaleDB time-series data.
Abstracts database queries and provides clean API.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, date
import pandas as pd
import asyncpg
from loguru import logger

from stock_dashboard.settings import settings

class TimeSeriesRepository:
    """Base repository for time-series data."""

    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self):
        """Create connection pool."""
        if self.pool is None:
            self.pool = await asyncpg.create_pool(
                str(settings.database.TIMESCALEDB_URI),
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            logger.info("Connected to TimescaleDB")

    async def disconnect(self):
        """Close connection pool."""
        if self.pool:
            await self.pool.close()
            self.pool = None
            logger.info("Disconnected from TimescaleDB")

    async def execute(self, query: str, *args) -> str:
        """Execute query without return."""
        await self.connect()
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)

    async def fetch(self, query: str, *args) -> List[Dict]:
        """Execute query and return results as list of dicts."""
        await self.connect()
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *args)
            return [dict(row) for row in rows]

    async def fetch_df(self, query: str, *args) -> pd.DataFrame:
        """Execute query and return results as DataFrame."""
        rows = await self.fetch(query, *args)
        return pd.DataFrame(rows)

class OHLCVRepository(TimeSeriesRepository):
    """Repository for OHLCV data."""

    async def get_prices(
        self,
        symbol: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        interval: str = "1D"
    ) -> pd.DataFrame:
        """
        Get OHLCV data for a symbol.

        Args:
            symbol: Stock symbol
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            interval: Data interval (1D, 1W)

        Returns:
            DataFrame with OHLCV data
        """

        # Select appropriate table based on interval
        if interval == "1W":
            table = "ohlcv_weekly"
            time_col = "week"
        else:  # 1D
            table = "ohlcv_daily"
            time_col = "day"

        # Build query
        query = f"""
            SELECT
                {time_col} as time,
                symbol,
                open,
                high,
                low,
                close,
                volume,
                trading_value,
                market_cap
            FROM {table}
            WHERE symbol = $1
        """

        params = [symbol]
        param_idx = 2

        if start_date:
            query += f" AND {time_col} >= ${param_idx}"
            params.append(start_date)
            param_idx += 1

        if end_date:
            query += f" AND {time_col} <= ${param_idx}"
            params.append(end_date)
            param_idx += 1

        query += f" ORDER BY {time_col} ASC"

        df = await self.fetch_df(query, *params)

        if not df.empty:
            df['time'] = pd.to_datetime(df['time'])
            df = df.set_index('time')

        return df

    async def get_latest_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get latest price for symbol."""

        query = """
            SELECT *
            FROM ohlcv_daily
            WHERE symbol = $1
            ORDER BY day DESC
            LIMIT 1
        """

        result = await self.fetch(query, symbol)
        return result[0] if result else None

    async def bulk_insert_ohlcv(self, data: pd.DataFrame):
        """
        Bulk insert OHLCV data.

        Args:
            data: DataFrame with columns [time, symbol, open, high, low, close, volume, ...]
        """

        await self.connect()

        # Prepare data for insertion
        records = [
            (
                row['time'],
                row['symbol'],
                row['open'],
                row['high'],
                row['low'],
                row['close'],
                row['volume'],
                row.get('trading_value'),
                row.get('shares_outstanding'),
                row.get('market_cap')
            )
            for _, row in data.iterrows()
        ]

        query = """
            INSERT INTO ohlcv (
                time, symbol, open, high, low, close, volume,
                trading_value, shares_outstanding, market_cap
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            ON CONFLICT (time, symbol) DO UPDATE SET
                open = EXCLUDED.open,
                high = EXCLUDED.high,
                low = EXCLUDED.low,
                close = EXCLUDED.close,
                volume = EXCLUDED.volume,
                trading_value = EXCLUDED.trading_value,
                shares_outstanding = EXCLUDED.shares_outstanding,
                market_cap = EXCLUDED.market_cap
        """

        async with self.pool.acquire() as conn:
            await conn.executemany(query, records)

        logger.info(f"Inserted {len(records)} OHLCV records")

class TechnicalRepository(TimeSeriesRepository):
    """Repository for technical indicators."""

    async def get_indicators(
        self,
        symbol: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> pd.DataFrame:
        """Get technical indicators for symbol."""

        query = """
            SELECT *
            FROM technical_indicators
            WHERE symbol = $1
        """

        params = [symbol]
        param_idx = 2

        if start_date:
            query += f" AND time >= ${param_idx}"
            params.append(start_date)
            param_idx += 1

        if end_date:
            query += f" AND time <= ${param_idx}"
            params.append(end_date)

        query += " ORDER BY time ASC"

        df = await self.fetch_df(query, *params)

        if not df.empty:
            df['time'] = pd.to_datetime(df['time'])
            df = df.set_index('time')

        return df

    async def bulk_insert_indicators(self, data: pd.DataFrame):
        """Bulk insert technical indicators."""

        await self.connect()

        records = [
            (
                row['time'],
                row['symbol'],
                row.get('sma_5'), row.get('sma_10'), row.get('sma_20'),
                row.get('sma_50'), row.get('sma_200'),
                row.get('ema_12'), row.get('ema_26'),
                row.get('rsi'),
                row.get('macd'), row.get('macd_signal'), row.get('macd_histogram'),
                row.get('bb_upper'), row.get('bb_middle'), row.get('bb_lower'), row.get('bb_width'),
                row.get('volume_sma_20'), row.get('volume_ratio'),
                row.get('atr'), row.get('volatility_30d')
            )
            for _, row in data.iterrows()
        ]

        query = """
            INSERT INTO technical_indicators (
                time, symbol,
                sma_5, sma_10, sma_20, sma_50, sma_200,
                ema_12, ema_26,
                rsi,
                macd, macd_signal, macd_histogram,
                bb_upper, bb_middle, bb_lower, bb_width,
                volume_sma_20, volume_ratio,
                atr, volatility_30d
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21)
            ON CONFLICT (time, symbol) DO UPDATE SET
                sma_5 = EXCLUDED.sma_5,
                sma_10 = EXCLUDED.sma_10,
                -- (... repeat for all columns)
        """

        async with self.pool.acquire() as conn:
            await conn.executemany(query, records)

        logger.info(f"Inserted {len(records)} technical indicator records")
```

### 4.4. MongoDB for Documents

```python
# src/stock_dashboard/database/repositories/document_repo.py
"""
Repository for MongoDB document storage (news, reports, analysis).
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING
from loguru import logger

from stock_dashboard.settings import settings

class DocumentRepository:
    """Base repository for MongoDB documents."""

    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None

    async def connect(self):
        """Connect to MongoDB."""
        if self.client is None:
            self.client = AsyncIOMotorClient(str(settings.database.MONGODB_URI))
            self.db = self.client.get_default_database()
            logger.info("Connected to MongoDB")

    async def disconnect(self):
        """Disconnect from MongoDB."""
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
            logger.info("Disconnected from MongoDB")

class NewsRepository(DocumentRepository):
    """Repository for news articles."""

    async def get_news(
        self,
        symbol: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get news articles."""

        await self.connect()

        # Build query
        query = {}

        if symbol:
            query['symbols'] = symbol

        if start_date or end_date:
            query['published_date'] = {}
            if start_date:
                query['published_date']['$gte'] = start_date
            if end_date:
                query['published_date']['$lte'] = end_date

        # Execute query
        cursor = self.db.news.find(query).sort('published_date', DESCENDING).limit(limit)
        articles = await cursor.to_list(length=limit)

        return articles

    async def insert_news(self, article: Dict[str, Any]):
        """Insert news article."""

        await self.connect()

        # Add metadata
        article['inserted_at'] = datetime.now()

        # Upsert by URL (avoid duplicates)
        await self.db.news.update_one(
            {'url': article['url']},
            {'$set': article},
            upsert=True
        )

    async def bulk_insert_news(self, articles: List[Dict[str, Any]]):
        """Bulk insert news articles."""

        await self.connect()

        operations = [
            {
                'updateOne': {
                    'filter': {'url': article['url']},
                    'update': {'$set': article},
                    'upsert': True
                }
            }
            for article in articles
        ]

        if operations:
            result = await self.db.news.bulk_write(operations)
            logger.info(f"Inserted/Updated {result.upserted_count + result.modified_count} news articles")

class AnalysisRepository(DocumentRepository):
    """Repository for AI analysis results."""

    async def save_analysis(
        self,
        symbol: str,
        analysis_type: str,  # fundamental, technical, valuation, sentiment
        result: Dict[str, Any]
    ):
        """Save analysis result."""

        await self.connect()

        doc = {
            'symbol': symbol,
            'analysis_type': analysis_type,
            'result': result,
            'created_at': datetime.now()
        }

        await self.db.analysis.insert_one(doc)
        logger.info(f"Saved {analysis_type} analysis for {symbol}")

    async def get_latest_analysis(
        self,
        symbol: str,
        analysis_type: str
    ) -> Optional[Dict[str, Any]]:
        """Get latest analysis for symbol."""

        await self.connect()

        doc = await self.db.analysis.find_one(
            {'symbol': symbol, 'analysis_type': analysis_type},
            sort=[('created_at', DESCENDING)]
        )

        return doc

class AlertRepository(DocumentRepository):
    """Repository for alerts."""

    async def create_alert(self, alert: Dict[str, Any]):
        """Create new alert."""

        await self.connect()

        alert['created_at'] = datetime.now()
        alert['updated_at'] = datetime.now()
        alert['status'] = 'active'

        result = await self.db.alerts.insert_one(alert)
        return str(result.inserted_id)

    async def get_active_alerts(self, symbol: Optional[str] = None) -> List[Dict]:
        """Get active alerts."""

        await self.connect()

        query = {'status': 'active'}
        if symbol:
            query['symbol'] = symbol

        cursor = self.db.alerts.find(query)
        alerts = await cursor.to_list(length=None)

        return alerts

    async def update_alert_status(self, alert_id: str, status: str):
        """Update alert status."""

        await self.connect()

        from bson import ObjectId

        await self.db.alerts.update_one(
            {'_id': ObjectId(alert_id)},
            {
                '$set': {
                    'status': status,
                    'updated_at': datetime.now()
                }
            }
        )
```

### ✅ Ưu điểm Phase 4

1. **Scalable**: Handle millions of records efficiently
2. **Optimized**: TimescaleDB compression, continuous aggregates
3. **Flexible**: Multi-database approach, right tool for right data
4. **Fast queries**: Indexed properly, cached with Redis
5. **Clean API**: Repository pattern abstracts database complexity

### ⚠️ Nhược điểm Phase 4

1. **Infrastructure complexity**: Multiple databases to manage
2. **Migration effort**: Move existing data to new schema
3. **Learning curve**: Team needs to learn TimescaleDB, async Python
4. **Operational overhead**: Backups, monitoring for multiple DBs

### 💰 Chi phí Phase 4

- **Development**: 2 weeks
- **Infrastructure (monthly)**:
  - TimescaleDB: $0 (self-hosted Docker) or $50-200 (TimescaleDB Cloud)
  - MongoDB: $0 (self-hosted) or $25-60 (MongoDB Atlas M10)
  - Redis: $0 (self-hosted) or $5-10 (Redis Cloud)
  - Qdrant: $0 (self-hosted) or $25 (Qdrant Cloud)
- **Storage**: $10-50/month (depends on data volume)
- **Total**: $0-$350/month

---

Tôi sẽ tiếp tục với Phase 5 (AI API) và Phase 6 (Web Dashboard) + phân tích so sánh trong file tiếp theo. Bạn có muốn tôi tiếp tục không?