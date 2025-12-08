"""
Data Models - Pydantic models for data validation
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from enum import Enum

class FrequencyType(str, Enum):
    """Frequency types for financial data"""
    DAILY = "D"
    WEEKLY = "W"
    MONTHLY = "M"
    QUARTERLY = "Q"
    ANNUAL = "A"
    TTM = "TTM"

class OHLCVBase(BaseModel):
    """Base OHLCV model"""
    symbol: str = Field(..., description="Stock symbol")
    date: date = Field(..., description="Trading date")
    open: float = Field(..., gt=0, description="Opening price")
    high: float = Field(..., gt=0, description="High price")
    low: float = Field(..., gt=0, description="Low price")
    close: float = Field(..., gt=0, description="Closing price")
    volume: int = Field(..., ge=0, description="Trading volume")
    resolution: str = Field(default="1D", description="Data resolution")
    
    @validator('high')
    def high_must_be_highest(cls, v, values):
        if 'open' in values and 'low' in values and 'close' in values:
            if v < max(values['open'], values['close']):
                raise ValueError('High must be >= max(open, close)')
        return v
    
    @validator('low')
    def low_must_be_lowest(cls, v, values):
        if 'open' in values and 'high' in values and 'close' in values:
            if v > min(values['open'], values['close']):
                raise ValueError('Low must be <= min(open, close)')
        return v

class OHLCVInDB(OHLCVBase):
    """OHLCV model for database storage"""
    id: Optional[int] = Field(None, description="Database ID")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Update timestamp")

class OHLCVStandardized(OHLCVBase):
    """Standardized OHLCV model"""
    market_cap: Optional[float] = Field(None, ge=0, description="Market capitalization")
    shares_outstanding: Optional[float] = Field(None, ge=0, description="Shares outstanding")
    currency: str = Field(default="VND", description="Currency")
    data_source: str = Field(default="vnstock", description="Data source")
    validation_status: str = Field(default="valid", description="Validation status")

class FundamentalBase(BaseModel):
    """Base fundamental model"""
    symbol: str = Field(..., description="Stock symbol")
    report_date: date = Field(..., description="Report date")
    year: int = Field(..., ge=2000, le=2030, description="Report year")
    quarter: int = Field(..., ge=1, le=4, description="Report quarter")
    freq_code: FrequencyType = Field(..., description="Frequency code")
    currency: str = Field(default="VND", description="Currency")
    data_source: str = Field(default="vnstock", description="Data source")

class BankMetrics(FundamentalBase):
    """Bank financial metrics"""
    # Profitability
    roea_ttm: Optional[float] = Field(None, description="ROE TTM (%)")
    roaa_ttm: Optional[float] = Field(None, description="ROA TTM (%)")
    nim_q: Optional[float] = Field(None, description="Net Interest Margin Q (%)")
    
    # Efficiency
    casa_ratio: Optional[float] = Field(None, ge=0, le=100, description="CASA Ratio (%)")
    cir: Optional[float] = Field(None, ge=0, description="Cost to Income Ratio (%)")
    nii_toi: Optional[float] = Field(None, ge=0, le=100, description="NII to TOI Ratio (%)")
    
    # Risk
    npl_ratio: Optional[float] = Field(None, ge=0, le=100, description="NPL Ratio (%)")
    ldr_pure: Optional[float] = Field(None, ge=0, description="Loan to Deposit Ratio (%)")
    llcr: Optional[float] = Field(None, ge=0, description="Loan Loss Coverage Ratio")
    
    # Per Share
    bvps: Optional[float] = Field(None, ge=0, description="Book Value Per Share")
    eps_ttm: Optional[float] = Field(None, description="EPS TTM")

class CompanyMetrics(FundamentalBase):
    """Company financial metrics"""
    # Profitability
    gross_margin: Optional[float] = Field(None, ge=-100, le=100, description="Gross Margin (%)")
    ebit_margin: Optional[float] = Field(None, ge=-100, le=100, description="EBIT Margin (%)")
    ebitda_margin: Optional[float] = Field(None, ge=-100, le=100, description="EBITDA Margin (%)")
    net_margin: Optional[float] = Field(None, ge=-100, le=100, description="Net Margin (%)")
    roe: Optional[float] = Field(None, description="Return on Equity (%)")
    roa: Optional[float] = Field(None, description="Return on Assets (%)")
    
    # Growth
    revenue_growth_yoy: Optional[float] = Field(None, description="Revenue Growth YoY (%)")
    profit_growth_yoy: Optional[float] = Field(None, description="Profit Growth YoY (%)")
    eps_growth_yoy: Optional[float] = Field(None, description="EPS Growth YoY (%)")
    
    # Efficiency
    asset_turnover: Optional[float] = Field(None, ge=0, description="Asset Turnover")
    inventory_turnover: Optional[float] = Field(None, ge=0, description="Inventory Turnover")
    receivables_turnover: Optional[float] = Field(None, ge=0, description="Receivables Turnover")
    
    # Per Share
    eps: Optional[float] = Field(None, description="Earnings Per Share")
    eps_ttm: Optional[float] = Field(None, description="EPS TTM")

class TechnicalIndicators(BaseModel):
    """Technical indicators model"""
    symbol: str = Field(..., description="Stock symbol")
    date: date = Field(..., description="Trading date")
    close: float = Field(..., gt=0, description="Closing price")
    volume: int = Field(..., ge=0, description="Trading volume")
    
    # Moving Averages
    sma_5: Optional[float] = Field(None, ge=0, description="SMA 5")
    sma_10: Optional[float] = Field(None, ge=0, description="SMA 10")
    sma_20: Optional[float] = Field(None, ge=0, description="SMA 20")
    sma_50: Optional[float] = Field(None, ge=0, description="SMA 50")
    sma_100: Optional[float] = Field(None, ge=0, description="SMA 100")
    sma_200: Optional[float] = Field(None, ge=0, description="SMA 200")
    
    # Exponential Moving Averages
    ema_12: Optional[float] = Field(None, ge=0, description="EMA 12")
    ema_26: Optional[float] = Field(None, ge=0, description="EMA 26")
    ema_50: Optional[float] = Field(None, ge=0, description="EMA 50")
    
    # Oscillators
    rsi_14: Optional[float] = Field(None, ge=0, le=100, description="RSI 14")
    rsi_21: Optional[float] = Field(None, ge=0, le=100, description="RSI 21")
    stoch_k: Optional[float] = Field(None, ge=0, le=100, description="Stochastic %K")
    stoch_d: Optional[float] = Field(None, ge=0, le=100, description="Stochastic %D")
    williams_r: Optional[float] = Field(None, ge=-100, le=0, description="Williams %R")
    
    # Momentum
    macd: Optional[float] = Field(None, description="MACD")
    macd_signal: Optional[float] = Field(None, description="MACD Signal")
    macd_histogram: Optional[float] = Field(None, description="MACD Histogram")
    roc: Optional[float] = Field(None, description="Rate of Change")
    momentum: Optional[float] = Field(None, description="Momentum")
    
    # Volatility
    atr_14: Optional[float] = Field(None, ge=0, description="ATR 14")
    atr_21: Optional[float] = Field(None, ge=0, description="ATR 21")
    bb_upper: Optional[float] = Field(None, ge=0, description="Bollinger Bands Upper")
    bb_middle: Optional[float] = Field(None, ge=0, description="Bollinger Bands Middle")
    bb_lower: Optional[float] = Field(None, ge=0, description="Bollinger Bands Lower")
    bb_width: Optional[float] = Field(None, ge=0, description="Bollinger Bands Width")
    bb_position: Optional[float] = Field(None, ge=0, le=1, description="Bollinger Bands Position")
    
    # Volume
    obv: Optional[float] = Field(None, description="On Balance Volume")
    ad_line: Optional[float] = Field(None, description="Accumulation/Distribution Line")
    cmf: Optional[float] = Field(None, ge=-1, le=1, description="Chaikin Money Flow")
    mfi: Optional[float] = Field(None, ge=0, le=100, description="Money Flow Index")
    vwap: Optional[float] = Field(None, ge=0, description="Volume Weighted Average Price")

class ValuationMetrics(BaseModel):
    """Valuation metrics model"""
    symbol: str = Field(..., description="Stock symbol")
    valuation_date: date = Field(..., description="Valuation date")
    current_price: float = Field(..., gt=0, description="Current stock price")
    market_cap: float = Field(..., ge=0, description="Market capitalization")
    shares_outstanding: float = Field(..., ge=0, description="Shares outstanding")
    
    # P/E Metrics
    pe_ttm: Optional[float] = Field(None, ge=0, description="P/E TTM")
    pe_forward: Optional[float] = Field(None, ge=0, description="Forward P/E")
    pe_5y_avg: Optional[float] = Field(None, ge=0, description="5-Year Average P/E")
    pe_sector_avg: Optional[float] = Field(None, ge=0, description="Sector Average P/E")
    pe_percentile: Optional[float] = Field(None, ge=0, le=100, description="P/E Percentile")
    pe_fair_value: Optional[float] = Field(None, ge=0, description="P/E Fair Value")
    
    # P/B Metrics
    pb_current: Optional[float] = Field(None, ge=0, description="Current P/B")
    pb_5y_avg: Optional[float] = Field(None, ge=0, description="5-Year Average P/B")
    pb_sector_avg: Optional[float] = Field(None, ge=0, description="Sector Average P/B")
    pb_percentile: Optional[float] = Field(None, ge=0, le=100, description="P/B Percentile")
    pb_fair_value: Optional[float] = Field(None, ge=0, description="P/B Fair Value")
    
    # EV Metrics
    enterprise_value: Optional[float] = Field(None, ge=0, description="Enterprise Value")
    ev_revenue: Optional[float] = Field(None, ge=0, description="EV/Revenue")
    ev_ebitda: Optional[float] = Field(None, ge=0, description="EV/EBITDA")
    ev_ebit: Optional[float] = Field(None, ge=0, description="EV/EBIT")
    ev_sector_avg: Optional[float] = Field(None, ge=0, description="Sector Average EV/EBITDA")
    ev_percentile: Optional[float] = Field(None, ge=0, le=100, description="EV/EBITDA Percentile")
    
    # DCF Metrics
    dcf_fair_value: Optional[float] = Field(None, ge=0, description="DCF Fair Value")
    dcf_upside_downside: Optional[float] = Field(None, description="DCF Upside/Downside (%)")
    wacc: Optional[float] = Field(None, ge=0, le=50, description="WACC (%)")
    terminal_growth_rate: Optional[float] = Field(None, ge=0, le=10, description="Terminal Growth Rate (%)")
    discount_rate: Optional[float] = Field(None, ge=0, le=30, description="Discount Rate (%)")
    
    # Relative Valuation
    sector_ranking: Optional[int] = Field(None, ge=1, description="Sector Ranking")
    market_ranking: Optional[int] = Field(None, ge=1, description="Market Ranking")
    value_score: Optional[float] = Field(None, ge=0, le=100, description="Value Score")
    attractiveness: Optional[str] = Field(None, description="Attractiveness Rating")

class DataQualityReport(BaseModel):
    """Data quality report model"""
    symbol: str = Field(..., description="Stock symbol")
    data_type: str = Field(..., description="Type of data")
    total_records: int = Field(..., ge=0, description="Total records")
    valid_records: int = Field(..., ge=0, description="Valid records")
    invalid_records: int = Field(..., ge=0, description="Invalid records")
    completeness_score: float = Field(..., ge=0, le=100, description="Completeness score")
    accuracy_score: float = Field(..., ge=0, le=100, description="Accuracy score")
    consistency_score: float = Field(..., ge=0, le=100, description="Consistency score")
    timeliness_score: float = Field(..., ge=0, le=100, description="Timeliness score")
    overall_score: float = Field(..., ge=0, le=100, description="Overall quality score")
    issues: List[str] = Field(default_factory=list, description="Quality issues")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")
    generated_at: datetime = Field(default_factory=datetime.now, description="Report generation time")

