# Phase 4: Feature Implementation

**Duration:** Week 13-18 (6 weeks)
**Priority:** P2 - Feature Parity
**Status:** Pending
**Prerequisites:** Phase 3 complete (Company page working)

---

## Context Links

- [Main Plan](../plan.md)
- [Phase 3: Frontend Core](./phase-03-frontend-core.md)
- [Current Streamlit Pages](../../../WEBAPP/pages/)

**AI Skills for UI Development:**
- `/ui-ux-pro-max` - Design system, layouts, animations, dark mode polish
- `/frontend-development` - React patterns, component architecture

---

## Overview

This phase migrates all remaining pages from Streamlit to Next.js. Each page follows the same pattern established in Phase 3.

**Goals:**
- Complete all 7 dashboard pages
- Technical analysis with candlestick charts
- User settings and preferences
- Dark theme polish

---

## Page Migration Schedule

| Week | Page | Complexity | Notes |
|------|------|------------|-------|
| 13 | Bank Analysis | Medium | Similar to Company |
| 14 | Sector & Valuation | Medium | Aggregation views |
| 15 | Technical Analysis | High | Candlestick charts |
| 16 | BSC Forecast | Medium | Multiple tabs |
| 17 | Security + FX | Low | Simple pages |
| 18 | Polish & Testing | - | Bug fixes, UX |

---

## Week 13: Bank Analysis Page

### Backend Endpoints

- [ ] **Create bank service**
  ```python
  # backend/app/services/bank_service.py
  import pandas as pd
  from pathlib import Path
  from typing import Optional, Dict
  from app.config import get_settings

  class BankService:
      """Service for loading bank financial data."""

      def __init__(self):
          settings = get_settings()
          self.data_path = Path(settings.data_root) / "processed" / "fundamental" / "bank"

      def get_financial_data(
          self,
          ticker: str,
          period: str = "Quarterly",
          limit: Optional[int] = None
      ) -> pd.DataFrame:
          """Load bank financial metrics."""
          file_path = self.data_path / "bank_financial_metrics.parquet"

          if not file_path.exists():
              raise FileNotFoundError(f"Data file not found: {file_path}")

          df = pd.read_parquet(file_path)
          df = df[df['symbol'] == ticker.upper()].copy()

          if period == "Quarterly":
              df = df[df['freq_code'] == 'Q']
          elif period == "Yearly":
              df = df[df['freq_code'] == 'Y']

          df = df.sort_values('report_date')

          if limit:
              df = df.tail(limit)

          return df

      def get_latest_metrics(self, ticker: str) -> Dict:
          """Get latest bank metrics."""
          df = self.get_financial_data(ticker, "Quarterly", limit=1)
          if df.empty:
              return {}

          row = df.iloc[-1]
          return {
              "symbol": row.get("symbol"),
              "nim": row.get("nim"),
              "npl_ratio": row.get("npl_ratio"),
              "car": row.get("car"),
              "casa_ratio": row.get("casa_ratio"),
              "cir": row.get("cir"),
              "roe": row.get("roe"),
              "roa": row.get("roa"),
          }
  ```

- [ ] **Create bank routes**
  ```python
  # backend/app/routes/bank.py
  from fastapi import APIRouter, HTTPException, Query
  from app.services.bank_service import BankService
  from pydantic import BaseModel
  from typing import List, Optional

  router = APIRouter(prefix="/api/bank", tags=["bank"])

  class BankMetrics(BaseModel):
      symbol: str
      report_date: str
      nim: Optional[float] = None
      npl_ratio: Optional[float] = None
      car: Optional[float] = None
      casa_ratio: Optional[float] = None
      cir: Optional[float] = None
      roe: Optional[float] = None
      roa: Optional[float] = None

      class Config:
          from_attributes = True

  _service = None
  def get_service():
      global _service
      if _service is None:
          _service = BankService()
      return _service

  @router.get("/{ticker}/metrics")
  def get_bank_metrics(
      ticker: str,
      period: str = Query("Quarterly", enum=["Quarterly", "Yearly"]),
      limit: int = Query(8, le=40)
  ):
      service = get_service()
      df = service.get_financial_data(ticker, period, limit)

      if df.empty:
          raise HTTPException(status_code=404, detail=f"No data for {ticker}")

      return {
          "ticker": ticker.upper(),
          "period": period,
          "data": df.to_dict('records'),
          "count": len(df)
      }

  @router.get("/{ticker}/latest")
  def get_bank_latest(ticker: str):
      service = get_service()
      metrics = service.get_latest_metrics(ticker)

      if not metrics:
          raise HTTPException(status_code=404, detail=f"No data for {ticker}")

      return metrics
  ```

### Frontend Components

- [ ] **Create useBank hook**
  ```tsx
  // frontend/hooks/useBank.ts
  'use client'

  import useSWR from 'swr'
  import { fetcher } from '@/lib/api'

  export function useBankMetrics(ticker: string, period: string = 'Quarterly') {
    const url = ticker
      ? `/api/bank/${ticker}/metrics?period=${period}&limit=12`
      : null

    const { data, error, isLoading } = useSWR(url, fetcher)

    return {
      data: data?.data || [],
      isLoading,
      isError: error,
    }
  }

  export function useBankLatest(ticker: string) {
    const { data, error, isLoading } = useSWR(
      ticker ? `/api/bank/${ticker}/latest` : null,
      fetcher
    )

    return { metrics: data, isLoading, isError: error }
  }
  ```

- [ ] **Create BankMetricsCard component**
  ```tsx
  // frontend/components/bank/BankMetricsCard.tsx
  import { MetricCard } from '../ui/MetricCard'

  interface Props {
    metrics: {
      nim?: number
      npl_ratio?: number
      car?: number
      casa_ratio?: number
      cir?: number
    }
  }

  export function BankMetricsCard({ metrics }: Props) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <MetricCard label="NIM" value={metrics.nim || 0} format="percent" />
        <MetricCard label="NPL Ratio" value={metrics.npl_ratio || 0} format="percent" />
        <MetricCard label="CAR" value={metrics.car || 0} format="percent" />
        <MetricCard label="CASA" value={metrics.casa_ratio || 0} format="percent" />
        <MetricCard label="CIR" value={metrics.cir || 0} format="percent" />
      </div>
    )
  }
  ```

- [ ] **Create Bank pages**
  - `frontend/app/dashboard/bank/page.tsx` - Bank list
  - `frontend/app/dashboard/bank/[ticker]/page.tsx` - Bank detail

---

## Week 14: Sector & Valuation Page

### Backend Endpoints

- [ ] **Create sector service**
  ```python
  # backend/app/services/sector_service.py
  import pandas as pd
  from pathlib import Path
  from typing import List, Dict
  from app.config import get_settings

  class SectorService:
      """Service for sector-level data."""

      def __init__(self):
          settings = get_settings()
          self.data_path = Path(settings.data_root) / "processed"

      def get_sector_pe(self) -> pd.DataFrame:
          """Get sector PE ratios."""
          file_path = self.data_path / "valuation" / "pe" / "sector_pe.parquet"
          if not file_path.exists():
              return pd.DataFrame()
          return pd.read_parquet(file_path)

      def get_vnindex_valuation(self, limit: int = 60) -> pd.DataFrame:
          """Get VN-Index PE/PB history."""
          file_path = self.data_path / "valuation" / "pe" / "vnindex_pe.parquet"
          if not file_path.exists():
              return pd.DataFrame()

          df = pd.read_parquet(file_path)
          df = df.sort_values('date', ascending=False).head(limit)
          return df.sort_values('date')

      def get_sector_scores(self) -> List[Dict]:
          """Get sector FA/TA scores."""
          file_path = self.data_path / "forecast" / "bsc" / "sector_scores.parquet"
          if not file_path.exists():
              return []

          df = pd.read_parquet(file_path)
          return df.to_dict('records')
  ```

- [ ] **Create sector routes**
  ```python
  # backend/app/routes/sector.py
  from fastapi import APIRouter, Query
  from app.services.sector_service import SectorService

  router = APIRouter(prefix="/api/sector", tags=["sector"])

  _service = None
  def get_service():
      global _service
      if _service is None:
          _service = SectorService()
      return _service

  @router.get("/pe")
  def get_sector_pe():
      """Get sector PE ratios."""
      service = get_service()
      df = service.get_sector_pe()
      return {"data": df.to_dict('records')}

  @router.get("/scores")
  def get_sector_scores():
      """Get sector FA/TA scores."""
      service = get_service()
      return {"data": service.get_sector_scores()}
  ```

- [ ] **Create valuation routes**
  ```python
  # backend/app/routes/valuation.py
  from fastapi import APIRouter, Query
  from app.services.sector_service import SectorService

  router = APIRouter(prefix="/api/valuation", tags=["valuation"])

  _service = None
  def get_service():
      global _service
      if _service is None:
          _service = SectorService()
      return _service

  @router.get("/vnindex")
  def get_vnindex_valuation(limit: int = Query(60, le=500)):
      """Get VN-Index PE/PB history."""
      service = get_service()
      df = service.get_vnindex_valuation(limit)
      return {"data": df.to_dict('records')}
  ```

### Frontend Components

- [ ] **Create useSector hook**
- [ ] **Create SectorTable component**
- [ ] **Create ValuationChart component**
- [ ] **Create Sector page** (`frontend/app/dashboard/sector/page.tsx`)

---

## Week 15: Technical Analysis Page (Complex)

### Backend Endpoints

- [ ] **Create technical service**
  ```python
  # backend/app/services/technical_service.py
  import pandas as pd
  from pathlib import Path
  from typing import Optional
  from app.config import get_settings

  class TechnicalService:
      """Service for technical analysis data."""

      def __init__(self):
          settings = get_settings()
          self.data_path = Path(settings.data_root) / "processed" / "technical"
          self.ohlcv_path = Path(settings.data_root) / "raw" / "ohlcv"

      def get_ohlcv(self, ticker: str, limit: int = 100) -> pd.DataFrame:
          """Get OHLCV data for candlestick chart."""
          file_path = self.ohlcv_path / "OHLCV_mktcap.parquet"
          if not file_path.exists():
              return pd.DataFrame()

          df = pd.read_parquet(file_path)
          df = df[df['ticker'] == ticker.upper()].copy()
          df = df.sort_values('date', ascending=False).head(limit)
          return df.sort_values('date')

      def get_indicators(self, ticker: str, limit: int = 100) -> pd.DataFrame:
          """Get technical indicators."""
          file_path = self.data_path / "basic_data.parquet"
          if not file_path.exists():
              return pd.DataFrame()

          df = pd.read_parquet(file_path)
          df = df[df['ticker'] == ticker.upper()].copy()
          df = df.sort_values('date', ascending=False).head(limit)
          return df.sort_values('date')

      def get_alerts(self, ticker: Optional[str] = None, limit: int = 20) -> pd.DataFrame:
          """Get technical alerts."""
          file_path = self.data_path / "alerts" / "breakout_latest.parquet"
          if not file_path.exists():
              return pd.DataFrame()

          df = pd.read_parquet(file_path)
          if ticker:
              df = df[df['ticker'] == ticker.upper()]
          return df.head(limit)
  ```

- [ ] **Create technical routes**
  ```python
  # backend/app/routes/technical.py
  from fastapi import APIRouter, Query
  from typing import Optional
  from app.services.technical_service import TechnicalService

  router = APIRouter(prefix="/api/technical", tags=["technical"])

  _service = None
  def get_service():
      global _service
      if _service is None:
          _service = TechnicalService()
      return _service

  @router.get("/{ticker}/ohlcv")
  def get_ohlcv(ticker: str, limit: int = Query(100, le=500)):
      """Get OHLCV data for candlestick chart."""
      service = get_service()
      df = service.get_ohlcv(ticker, limit)
      return {"ticker": ticker.upper(), "data": df.to_dict('records')}

  @router.get("/{ticker}/indicators")
  def get_indicators(ticker: str, limit: int = Query(100, le=500)):
      """Get technical indicators."""
      service = get_service()
      df = service.get_indicators(ticker, limit)
      return {"ticker": ticker.upper(), "data": df.to_dict('records')}

  @router.get("/alerts")
  def get_alerts(
      ticker: Optional[str] = None,
      alert_type: Optional[str] = None,
      limit: int = Query(20, le=100)
  ):
      """Get technical alerts."""
      service = get_service()
      df = service.get_alerts(ticker, limit)
      return {"data": df.to_dict('records')}
  ```

### Frontend: Candlestick Chart

- [ ] **Create CandlestickChart component**
  ```tsx
  // frontend/components/charts/CandlestickChart.tsx
  'use client'

  import dynamic from 'next/dynamic'
  import { ApexOptions } from 'apexcharts'

  const Chart = dynamic(() => import('react-apexcharts'), { ssr: false })

  interface OHLCVData {
    date: string
    open: number
    high: number
    low: number
    close: number
    volume: number
  }

  interface Props {
    data: OHLCVData[]
    height?: number
  }

  export function CandlestickChart({ data, height = 400 }: Props) {
    const candleData = data.map(d => ({
      x: new Date(d.date),
      y: [d.open, d.high, d.low, d.close]
    }))

    const options: ApexOptions = {
      chart: {
        type: 'candlestick',
        background: 'transparent',
        toolbar: {
          show: true,
          tools: {
            download: false,
            selection: true,
            zoom: true,
            zoomin: true,
            zoomout: true,
            pan: true,
            reset: true,
          },
        },
      },
      theme: { mode: 'dark' },
      xaxis: {
        type: 'datetime',
        labels: {
          style: { colors: '#9ca3af' },
          datetimeFormatter: {
            year: 'yyyy',
            month: "MMM 'yy",
            day: 'dd MMM',
          },
        },
      },
      yaxis: {
        tooltip: { enabled: true },
        labels: {
          style: { colors: '#9ca3af' },
          formatter: (val) => val.toLocaleString(),
        },
      },
      plotOptions: {
        candlestick: {
          colors: {
            upward: '#22c55e',
            downward: '#ef4444',
          },
        },
      },
      grid: {
        borderColor: '#374151',
      },
    }

    const series = [{
      data: candleData,
    }]

    return (
      <Chart
        options={options}
        series={series}
        type="candlestick"
        height={height}
      />
    )
  }
  ```

- [ ] **Create VolumeChart component**
- [ ] **Create useTechnical hook**
- [ ] **Create Technical page** (`frontend/app/dashboard/technical/page.tsx`)

---

## Week 16: BSC Forecast Page

### Backend Endpoints

- [ ] **Create forecast service**
  ```python
  # backend/app/services/forecast_service.py
  import pandas as pd
  from pathlib import Path
  from app.config import get_settings

  class ForecastService:
      """Service for BSC analyst forecasts."""

      def __init__(self):
          settings = get_settings()
          self.data_path = Path(settings.data_root) / "processed" / "forecast" / "bsc"

      def get_forecast(self, ticker: str):
          """Get BSC forecast for a ticker."""
          file_path = self.data_path / "bsc_forecasts.parquet"
          if not file_path.exists():
              return None

          df = pd.read_parquet(file_path)
          df = df[df['ticker'] == ticker.upper()]

          if df.empty:
              return None

          return df.iloc[-1].to_dict()

      def list_forecasts(self, rating: str = None, limit: int = 30):
          """List all BSC forecasts."""
          file_path = self.data_path / "bsc_forecasts.parquet"
          if not file_path.exists():
              return []

          df = pd.read_parquet(file_path)

          if rating:
              df = df[df['rating'] == rating]

          # Sort by upside potential
          if 'upside' in df.columns:
              df = df.sort_values('upside', ascending=False)

          return df.head(limit).to_dict('records')
  ```

- [ ] **Create forecast routes**

### Frontend Components

- [ ] **Create useForecast hook**
- [ ] **Create ForecastCard component**
- [ ] **Create ForecastTable component**
- [ ] **Create Forecast page** (`frontend/app/dashboard/forecast/page.tsx`)

---

## Week 17: Security Analysis + FX & Commodities

### Security Analysis

Similar to Company/Bank pages:
- [ ] Create security service
- [ ] Create security routes
- [ ] Create useSecurity hook
- [ ] Create Security pages

### FX & Commodities

Simpler page:
- [ ] Create macro service (for FX, commodity data)
- [ ] Create macro routes
- [ ] Create useMacro hook
- [ ] Create FX page with commodity price charts

---

## Week 18: Polish & Testing

### Tasks

- [ ] **Cross-browser testing** (Chrome, Firefox, Safari)
- [ ] **Mobile responsiveness** - Test on phone/tablet sizes
- [ ] **Loading states** - Ensure all async operations show loading
- [ ] **Error handling** - User-friendly error messages
- [ ] **Performance** - Check for unnecessary re-renders
- [ ] **Accessibility** - Keyboard navigation, screen readers

### Bug Fixes

- [ ] Review all pages for issues
- [ ] Fix any TypeScript errors
- [ ] Ensure consistent styling
- [ ] Verify all API calls work

### Documentation

- [ ] Document API endpoints (Swagger is auto-generated)
- [ ] Add README to frontend/
- [ ] Add README to backend/

---

## Success Criteria

### All Pages Working

- [ ] Company Analysis - Complete with charts
- [ ] Bank Analysis - Complete with bank-specific metrics
- [ ] Sector & Valuation - Sector PE, scores, VN-Index
- [ ] Technical Analysis - Candlestick chart, indicators
- [ ] BSC Forecast - Forecasts list, detail view
- [ ] Security Analysis - Complete
- [ ] FX & Commodities - Price charts

### Quality Checks

- [ ] All pages load without errors
- [ ] Charts display correctly
- [ ] Mobile responsive
- [ ] Dark theme consistent
- [ ] No console errors

---

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Candlestick chart complex | High | Use ApexCharts built-in candlestick |
| Data not available | Medium | Handle empty states gracefully |
| Too many API calls | Medium | Use SWR caching effectively |
| Timeline pressure | Medium | Prioritize core features |

---

## Next Phase

After completing Phase 4, proceed to:
[Phase 5: Deployment](./phase-05-deployment.md)

---

*Phase created: 2026-01-15*
