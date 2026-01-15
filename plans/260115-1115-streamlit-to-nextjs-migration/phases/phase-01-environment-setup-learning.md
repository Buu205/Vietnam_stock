# Phase 1: Environment Setup & Learning

**Duration:** Week 1-4 (4 weeks)
**Priority:** P1 - Foundation
**Status:** Pending

---

## Context Links

- [Main Plan](../plan.md)
- [Next.js + FastAPI Architecture](../research/researcher-nextjs-fastapi-architecture.md)
- [Current Architecture](.claude/guides/architecture.md)

---

## Overview

This phase focuses on two parallel tracks:
1. **Setup:** Install tools and configure development environment
2. **Learning:** Build foundational skills before coding

**Why 4 weeks?** As a beginner, rushing past fundamentals leads to confusion later. This phase ensures you understand *why* things work, not just *how*.

---

## Key Insights from Research

1. **Monorepo structure** - Keep frontend/backend in same repo for easier development
2. **Direct API calls** - Frontend calls FastAPI directly (no proxy needed)
3. **SWR for data fetching** - Simpler than React Query for beginners
4. **ApexCharts for candlesticks** - Better financial chart support than Recharts
5. **DuckDB + PostgreSQL hybrid** - DuckDB queries Parquet directly (no migration), PostgreSQL only for users/auth

---

## Requirements

### Hardware
- Computer with 8GB+ RAM
- Stable internet connection
- 50GB+ free disk space

### Software Prerequisites
- Git installed
- VS Code (recommended IDE)
- Terminal comfort (basic commands)

---

## Architecture: Development Environment

```
YOUR COMPUTER (Development)
=======================================================

+------------------+     +------------------+
|    VS Code       |     |    Terminal      |
|  - ESLint        |     |  - bash/zsh      |
|  - Prettier      |     |  - git           |
|  - Python ext    |     |                  |
|  - TypeScript    |     |                  |
+------------------+     +------------------+
         |                       |
         v                       v
+--------------------------------------------------+
|              LOCAL DEVELOPMENT                    |
+--------------------------------------------------+
|                                                  |
|  +------------+  +------------+  +------------+  |
|  |  Node.js   |  |  Python    |  |   Docker   |  |
|  |  v20 LTS   |  |   3.13     |  |  Desktop   |  |
|  +------------+  +------------+  +------------+  |
|        |               |               |         |
|        v               v               v         |
|  +------------+  +------------+  +------------+  |
|  |  Next.js   |  |  FastAPI   |  | PostgreSQL |  |
|  |  :3000     |  |  :8000     |  |  :5432     |  |
|  +------------+  +------------+  +------------+  |
|                                                  |
+--------------------------------------------------+
```

---

## Related Code Files

| File | Purpose | Why Important |
|------|---------|---------------|
| `PROCESSORS/` | Business logic | Will be imported by FastAPI |
| `config/registries/` | Data registries | Core data access patterns |
| `WEBAPP/services/base_service.py` | Service pattern | Template for FastAPI services |
| `MCP_SERVER/bsc_mcp/server.py` | FastMCP server | Reference for FastAPI patterns |

---

## Implementation Steps

### Week 1: Environment Setup

#### Step 1.1: Install Core Tools

- [ ] **Install Node.js v20 LTS**
  ```bash
  # macOS (using Homebrew)
  brew install node@20

  # Verify installation
  node --version  # Should show v20.x.x
  npm --version   # Should show 10.x.x
  ```

- [ ] **Verify Python 3.13** (already installed)
  ```bash
  python3 --version  # Should show 3.13.x
  pip3 --version
  ```

- [ ] **Install Docker Desktop**
  - Download from: https://www.docker.com/products/docker-desktop
  - Install and start Docker Desktop
  - Verify: `docker --version`

- [ ] **Install VS Code Extensions**
  - ESLint
  - Prettier
  - Python
  - TypeScript and JavaScript Language Features
  - Tailwind CSS IntelliSense
  - Docker

#### Step 1.2: Create Project Structure

- [ ] **Create new project directory**
  ```bash
  cd ~/Dev
  mkdir vietnam-dashboard-web
  cd vietnam-dashboard-web
  git init
  ```

- [ ] **Create folder structure**
  ```bash
  mkdir -p frontend backend shared
  mkdir -p backend/app backend/routes backend/services backend/tests
  mkdir -p frontend/app frontend/components frontend/lib frontend/hooks
  ```

- [ ] **Create initial files**
  ```bash
  touch backend/requirements.txt
  touch backend/app/main.py
  touch frontend/package.json
  touch docker-compose.yml
  touch .gitignore
  ```

#### Step 1.3: Initialize Backend (FastAPI)

- [ ] **Create requirements.txt**
  ```
  fastapi==0.115.0
  uvicorn[standard]==0.32.0
  pydantic==2.9.0
  python-jose[cryptography]==3.3.0
  passlib[bcrypt]==1.7.4
  sqlalchemy==2.0.35
  psycopg2-binary==2.9.9
  pandas==2.2.3
  pyarrow==18.0.0
  duckdb==1.1.3
  ```

  **Why DuckDB?** DuckDB queries Parquet files directly - no need to migrate 500MB of stock data to PostgreSQL. PostgreSQL only stores users/auth data (~few KB).

- [ ] **Create basic FastAPI app (backend/app/main.py)**
  ```python
  """
  Vietnam Dashboard API
  A simple FastAPI backend for stock market data.
  """
  from fastapi import FastAPI
  from fastapi.middleware.cors import CORSMiddleware

  app = FastAPI(
      title="Vietnam Dashboard API",
      description="Backend API for Vietnam stock market dashboard",
      version="0.1.0"
  )

  # Allow requests from Next.js frontend
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["http://localhost:3000"],
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
  )

  @app.get("/")
  def read_root():
      """Health check endpoint."""
      return {"status": "ok", "message": "Vietnam Dashboard API"}

  @app.get("/api/health")
  def health_check():
      """API health check."""
      return {"status": "healthy"}
  ```

- [ ] **Test FastAPI locally**
  ```bash
  cd backend
  pip3 install -r requirements.txt
  uvicorn app.main:app --reload --port 8000
  # Open http://localhost:8000/docs to see Swagger UI
  ```

#### Step 1.4: Initialize Frontend (Next.js)

- [ ] **Create Next.js app**
  ```bash
  cd frontend
  npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir=false --import-alias="@/*"
  ```

- [ ] **Install additional dependencies**
  ```bash
  npm install swr
  npm install apexcharts react-apexcharts
  npm install @types/node --save-dev
  ```

- [ ] **Test Next.js locally**
  ```bash
  npm run dev
  # Open http://localhost:3000
  ```

### Week 2: Python & HTTP Fundamentals

#### Learning Resources

- [ ] **Python Basics** (if needed)
  - [Python Official Tutorial](https://docs.python.org/3/tutorial/)
  - Focus: functions, classes, modules, error handling
  - Time: 4-6 hours

- [ ] **HTTP Fundamentals**
  - [MDN HTTP Overview](https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview)
  - Understand: GET, POST, status codes, headers
  - Time: 2-3 hours

- [ ] **REST API Concepts**
  - [REST API Tutorial](https://restfulapi.net/)
  - Understand: endpoints, resources, JSON
  - Time: 2-3 hours

#### Practice Exercises

- [ ] **Exercise 1: Read a Parquet file with Python**
  ```python
  import pandas as pd

  # Read existing company metrics
  df = pd.read_parquet("DATA/processed/fundamental/company/company_financial_metrics.parquet")
  print(df.head())
  print(df.columns.tolist())
  ```

- [ ] **Exercise 2: Make HTTP request with Python**
  ```python
  import requests

  # Call your local FastAPI
  response = requests.get("http://localhost:8000/api/health")
  print(response.status_code)  # Should be 200
  print(response.json())       # Should be {"status": "healthy"}
  ```

- [ ] **Exercise 3: Create a FastAPI endpoint that returns data**
  ```python
  @app.get("/api/tickers")
  def list_tickers():
      """Return list of available tickers."""
      # For now, return hardcoded data
      return {
          "tickers": ["VNM", "FPT", "VCB", "ACB"],
          "count": 4
      }
  ```

### Week 3: HTML/CSS & JavaScript Basics

#### Learning Resources

- [ ] **HTML/CSS Basics**
  - [MDN Getting Started with HTML](https://developer.mozilla.org/en-US/docs/Learn/HTML/Introduction_to_HTML/Getting_started)
  - [MDN CSS First Steps](https://developer.mozilla.org/en-US/docs/Learn/CSS/First_steps)
  - Time: 4-6 hours

- [ ] **JavaScript Fundamentals**
  - [JavaScript.info - Fundamentals](https://javascript.info/first-steps)
  - Focus: variables, functions, arrays, objects, async/await
  - Time: 6-8 hours

- [ ] **Tailwind CSS Crash Course**
  - [Tailwind Official Docs](https://tailwindcss.com/docs/utility-first)
  - Focus: utility classes, responsive design, dark mode
  - Time: 2-3 hours

#### Practice Exercises

- [ ] **Exercise 4: Create a simple HTML page**
  ```html
  <!DOCTYPE html>
  <html>
  <head>
      <title>Stock Dashboard</title>
  </head>
  <body>
      <h1>Vietnam Stock Dashboard</h1>
      <p>Ticker: VNM</p>
      <p>Price: 85,000 VND</p>
  </body>
  </html>
  ```

- [ ] **Exercise 5: Style with Tailwind**
  Create `frontend/app/page.tsx`:
  ```tsx
  export default function Home() {
    return (
      <main className="min-h-screen bg-gray-900 text-white p-8">
        <h1 className="text-3xl font-bold mb-4">
          Vietnam Stock Dashboard
        </h1>
        <div className="bg-gray-800 rounded-lg p-4">
          <p className="text-lg">Ticker: VNM</p>
          <p className="text-green-400 text-2xl">85,000 VND</p>
        </div>
      </main>
    )
  }
  ```

- [ ] **Exercise 6: Fetch data with JavaScript**
  ```tsx
  'use client'
  import { useState, useEffect } from 'react'

  export default function TickerPage() {
    const [data, setData] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
      fetch('http://localhost:8000/api/tickers')
        .then(res => res.json())
        .then(data => {
          setData(data)
          setLoading(false)
        })
    }, [])

    if (loading) return <div>Loading...</div>

    return (
      <div>
        <h1>Available Tickers</h1>
        <p>Count: {data?.count}</p>
        <ul>
          {data?.tickers.map(t => <li key={t}>{t}</li>)}
        </ul>
      </div>
    )
  }
  ```

### Week 4: React & Integration

#### Learning Resources

- [ ] **React Fundamentals**
  - [React Official Tutorial](https://react.dev/learn)
  - Focus: components, props, state, hooks
  - Time: 6-8 hours

- [ ] **Next.js App Router**
  - [Next.js Learn Course](https://nextjs.org/learn)
  - Focus: routing, layouts, server/client components
  - Time: 4-6 hours

- [ ] **SWR Data Fetching**
  - [SWR Documentation](https://swr.vercel.app/)
  - Focus: useSWR hook, caching, error handling
  - Time: 2 hours

#### Practice Exercises

- [ ] **Exercise 7: Create a React component**
  ```tsx
  // frontend/components/TickerCard.tsx
  interface TickerCardProps {
    ticker: string
    price: number
    change: number
  }

  export function TickerCard({ ticker, price, change }: TickerCardProps) {
    const changeColor = change >= 0 ? 'text-green-400' : 'text-red-400'

    return (
      <div className="bg-gray-800 rounded-lg p-4">
        <h3 className="text-xl font-bold">{ticker}</h3>
        <p className="text-2xl">{price.toLocaleString()} VND</p>
        <p className={changeColor}>
          {change >= 0 ? '+' : ''}{change.toFixed(2)}%
        </p>
      </div>
    )
  }
  ```

- [ ] **Exercise 8: Use SWR for data fetching**
  ```tsx
  // frontend/hooks/useTickers.ts
  import useSWR from 'swr'

  const fetcher = (url: string) => fetch(url).then(r => r.json())

  export function useTickers() {
    const { data, error, isLoading } = useSWR(
      'http://localhost:8000/api/tickers',
      fetcher
    )

    return {
      tickers: data?.tickers,
      isLoading,
      isError: error
    }
  }
  ```

- [ ] **Exercise 9: Complete first integration**
  Create a page that:
  1. Fetches ticker list from FastAPI
  2. Displays them in TickerCard components
  3. Has loading and error states

---

## Success Criteria

### Environment Setup Complete

- [ ] Node.js v20 installed and working
- [ ] Python 3.13 verified
- [ ] Docker Desktop running
- [ ] VS Code configured with extensions
- [ ] Project structure created

### Learning Milestones Achieved

- [ ] Can explain what HTTP GET/POST requests do
- [ ] Can read and write basic Python functions
- [ ] Can create HTML with Tailwind styling
- [ ] Can write JavaScript async/await code
- [ ] Can create React components with props

### Technical Validation

- [ ] FastAPI server starts without errors
- [ ] FastAPI returns JSON from /api/tickers endpoint
- [ ] Next.js app displays in browser
- [ ] Frontend successfully fetches data from backend
- [ ] No CORS errors in browser console

---

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Learning curve overwhelming | High | Focus on one topic per day, take breaks |
| CORS issues | Medium | Use exact CORS config from Step 1.3 |
| Version conflicts | Low | Use exact versions in requirements.txt |
| Docker issues on Mac | Low | Ensure Docker Desktop is running first |

---

## Checkpoint Questions

Before moving to Phase 2, you should be able to answer:

1. What is the difference between frontend and backend?
2. What does HTTP status code 200 mean? 404? 500?
3. What is the difference between `useState` and `useEffect`?
4. Why do we need CORS middleware?
5. What is the purpose of `async/await`?

---

## Next Phase

After completing Phase 1, proceed to:
[Phase 2: Backend API](./phase-02-backend-api.md)

---

*Phase created: 2026-01-15*
