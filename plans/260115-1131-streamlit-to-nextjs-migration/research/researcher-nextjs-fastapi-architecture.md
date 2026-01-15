# Research: Next.js + FastAPI Full-Stack Architecture

**Date:** 2026-01-15 | **Status:** Complete | **For:** Streamlit → Next.js Migration

---

## 1. Architecture Overview

**Recommended Structure:** Separate monorepo with Next.js frontend + FastAPI backend

```
project/
├── frontend/              # Next.js App Router
│   ├── app/
│   │   ├── api/          # Optional: lightweight proxy routes
│   │   ├── dashboard/
│   │   └── layout.tsx
│   └── package.json
├── backend/               # FastAPI
│   ├── app/
│   │   ├── main.py
│   │   ├── routes/       # API endpoints
│   │   └── dependencies/  # JWT, auth
│   └── requirements.txt
└── docker-compose.yml    # Local dev
```

**Key Pattern:** Frontend communicates directly with FastAPI backend on separate domain/port. NO Next.js API routes needed for this architecture.

---

## 2. API Integration Patterns

### Option A: Direct Backend Calls (Recommended for Beginners)
```typescript
// Next.js client component
'use client'

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL

export function useTickerData(ticker: string) {
  const [data, setData] = useState(null)

  useEffect(() => {
    fetch(`${BACKEND_URL}/api/tickers/${ticker}`, {
      headers: { 'Authorization': `Bearer ${token}` },
      credentials: 'include'  // For cookies
    })
    .then(r => r.json())
    .then(setData)
  }, [ticker, token])

  return data
}
```

### Option B: Next.js API Routes as Proxy
Lightweight wrapper for server-side secrets (API keys). Adds hop but cleaner separation:
```typescript
// app/api/tickers/[ticker]/route.ts
export async function GET(req: Request, { params }: Props) {
  const res = await fetch(
    `${process.env.BACKEND_URL}/api/tickers/${params.ticker}`,
    { headers: { 'Authorization': `Bearer ${req.headers.get('token')}` } }
  )
  return NextResponse.json(await res.json())
}
```

**Choose Option A:** Simple dashboard, read-heavy operations
**Choose Option B:** Sensitive data handling, custom logic needed

---

## 3. Authentication: JWT + HttpOnly Cookies

**Best Practice:** Store JWT in HttpOnly cookie set by FastAPI

### FastAPI Backend
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import jwt

app = FastAPI()

# CORS middleware (required for cross-origin requests)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/auth/login")
async def login(username: str, password: str):
    # Verify credentials
    token = jwt.encode(
        {"sub": username, "exp": datetime.utcnow() + timedelta(days=7)},
        "SECRET", algorithm="HS256"
    )
    response = JSONResponse({"ok": True})
    response.set_cookie("token", token, httponly=True, samesite="lax")
    return response

# Protected endpoint
async def get_current_user(request: Request):
    token = request.cookies.get("token")
    if not token:
        raise HTTPException(status_code=401)
    payload = jwt.decode(token, "SECRET", algorithms=["HS256"])
    return payload.get("sub")

@app.get("/api/metrics")
async def get_metrics(user: str = Depends(get_current_user)):
    return {"user": user, "data": [...]}
```

### Next.js Frontend
```typescript
// lib/auth.ts
export async function login(username: string, password: string) {
  const res = await fetch(`${BACKEND_URL}/auth/login`, {
    method: 'POST',
    body: JSON.stringify({ username, password }),
    credentials: 'include'  // Sends cookies
  })
  return res.ok
}

// Cookies sent automatically in subsequent requests
async function fetchMetrics() {
  const res = await fetch(`${BACKEND_URL}/api/metrics`, {
    credentials: 'include'
  })
  return res.json()
}
```

**Alternative:** NextAuth.js with [fastapi-nextauth-jwt](https://pypi.org/project/fastapi-nextauth-jwt/) for OAuth integration.

---

## 4. Data Fetching: SWR vs React Query

| Aspect | SWR | React Query |
|--------|-----|------------|
| **Bundle Size** | 5.3 KB | 16.2 KB |
| **Learning Curve** | Shallow | Moderate |
| **Financial Charts** | ✅ Good | ✅ Excellent |
| **Polling Support** | ✅ Native | ✅ Built-in |
| **Caching TTL** | Simple | Advanced |
| **For Stock Data** | Good (read-heavy) | Better (complex queries) |

### SWR Example (Simpler, Recommended)
```typescript
import useSWR from 'swr'

export function TickerChart({ ticker }: { ticker: string }) {
  const { data, error, isLoading } = useSWR(
    [`/api/technical/${ticker}`, token],
    ([url, t]) => fetch(url, {
      headers: { 'Authorization': `Bearer ${t}` },
      credentials: 'include'
    }).then(r => r.json()),
    { refreshInterval: 60000 }  // Refresh every 60s
  )

  if (error) return <div>Failed to load</div>
  if (isLoading) return <div>Loading...</div>
  return <Chart data={data} />
}
```

### React Query Example (More Features)
```typescript
import { useQuery } from '@tanstack/react-query'

export function TickerChart({ ticker }: { ticker: string }) {
  const { data, isPending } = useQuery({
    queryKey: ['ticker', ticker],
    queryFn: () => fetch(`/api/technical/${ticker}`, {
      credentials: 'include'
    }).then(r => r.json()),
    staleTime: 60000,
    refetchInterval: 120000
  })

  return <Chart data={data} />
}
```

**Recommendation:** Start with **SWR** (simpler for beginners), migrate to **React Query** if caching becomes complex.

---

## 5. Chart Libraries for Financial Data

| Library | Best For | Bundle | Learning |
|---------|----------|--------|----------|
| **Recharts** | React components, simple charts | 8 KB | Easy |
| **ApexCharts** | Professional look, animations | 45 KB | Easy |
| **Plotly.js** | Complex financial analysis | 2.8 MB | Hard |

### For Vietnam Dashboard Migration

**ApexCharts + React Wrapper:**
```typescript
import ApexCharts from 'apexcharts'
import dynamic from 'next/dynamic'

const Chart = dynamic(() => import('react-apexcharts'), { ssr: false })

export function CandleChart({ ticker, data }: Props) {
  const options = {
    chart: { type: 'candlestick' },
    title: { text: ticker }
  }

  return (
    <Chart
      type="candlestick"
      options={options}
      series={[{ data: data.map(d => [d.date, d.o, d.h, d.l, d.c]) }]}
    />
  )
}
```

**Recharts (Lightweight Alternative):**
```typescript
import { LineChart, Line, XAxis, YAxis } from 'recharts'

export function PriceChart({ data }: Props) {
  return (
    <LineChart width={800} height={400} data={data}>
      <XAxis dataKey="date" />
      <YAxis />
      <Line type="monotone" dataKey="close" stroke="#8884d8" />
    </LineChart>
  )
}
```

**Verdict:** ApexCharts for professional candlestick/technical charts, Recharts for simpler line/bar charts.

---

## 6. CORS Configuration

### FastAPI (Backend)
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # Next.js dev
        "https://yourdomain.com"      # Production
    ],
    allow_credentials=True,           # Allow cookies
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
    max_age=3600,
)
```

### Next.js (Optional Proxy Route)
```typescript
// app/api/proxy/[...path]/route.ts
export async function GET(req: Request) {
  const url = new URL(req.url)
  const path = url.pathname.replace('/api/proxy', '')

  const res = await fetch(`${process.env.BACKEND_URL}${path}`, {
    headers: { 'Authorization': req.headers.get('authorization') || '' },
    credentials: 'include'
  })

  return res
}
```

---

## 7. Deployment Options

### Vercel + Railway (Recommended for Beginners)
- **Frontend (Next.js):** Deploy to Vercel (free tier available)
- **Backend (FastAPI):** Deploy to Railway, Render, or Fly.io
- **Database:** PostgreSQL on Railway

### Environment Variables
```bash
# .env.local (Next.js)
NEXT_PUBLIC_BACKEND_URL=https://api.yourdomain.com

# backend/.env (FastAPI)
DATABASE_URL=postgresql://...
SECRET_KEY=your-secret-key
```

### Docker Setup
```yaml
# docker-compose.yml
version: '3.8'
services:
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    environment:
      NEXT_PUBLIC_BACKEND_URL: http://backend:8000

  backend:
    build: ./backend
    ports: ["8000:8000"]
    environment:
      DATABASE_URL: postgresql://...

  db:
    image: postgres:16
    ports: ["5432:5432"]
    environment:
      POSTGRES_PASSWORD: password
```

---

## 8. Project Structure Example

```
frontend/
├── app/
│   ├── api/                    # Optional proxy routes
│   ├── (auth)/
│   │   └── login/
│   ├── dashboard/
│   │   ├── page.tsx
│   │   └── [ticker]/page.tsx
│   ├── layout.tsx
│   └── page.tsx                # Home
├── components/
│   ├── charts/
│   │   ├── CandleChart.tsx
│   │   └── TechnicalChart.tsx
│   └── tables/
│       └── MetricsTable.tsx
├── lib/
│   ├── api.ts                 # Fetch functions
│   ├── auth.ts                # Auth utilities
│   └── constants.ts
├── hooks/
│   ├── useTickerData.ts       # SWR hook
│   └── useTechnicals.ts
└── package.json

backend/
├── app/
│   ├── main.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── tickers.py
│   │   ├── technical.py
│   │   └── fundamental.py
│   ├── models.py              # Pydantic schemas
│   ├── database.py
│   └── dependencies.py        # Auth, DB
├── tests/
├── requirements.txt
└── Dockerfile
```

---

## Key Decisions for Beginners

1. **Direct API calls > Next.js proxy routes** (simpler, fewer hops)
2. **HttpOnly cookies > localStorage** (more secure, automatic)
3. **SWR > React Query** (simpler, fewer deps, good enough)
4. **ApexCharts > Recharts** (candlestick charts easier)
5. **Vercel + Railway** (managed, free tier, no DevOps)

---

## Next Steps

1. Set up monorepo structure (frontend + backend folders)
2. Create FastAPI skeleton with CORS + JWT auth
3. Build Next.js auth page (login form)
4. Migrate Streamlit pages → Next.js routes one-by-one
5. Replace Streamlit components with React components + ApexCharts
6. Connect to existing Python calculators via FastAPI endpoints

---

## References

- [Next.js FastAPI Integration Template](https://github.com/vintasoftware/nextjs-fastapi-template)
- [Nemanja Mitic: Next.js Server Actions with FastAPI](https://nemanjamitic.com/blog/2026-01-03-nextjs-server-actions-fastapi-openapi)
- [NextAuth.js with FastAPI JWT](https://tom.catshoek.dev/posts/nextauth-fastapi/)
- [FastAPI CORS Middleware](https://fastapi.tiangolo.com/tutorial/cors)
- [FastAPI JWT Authentication](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt)
- [React Query vs SWR 2025](https://dev.to/rigalpatel001/react-query-or-swr-which-is-best-in-2025-2oa3)
- [JavaScript Charting Libraries 2026](https://www.luzmo.com/blog/best-javascript-chart-libraries)
