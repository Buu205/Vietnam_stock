# Brainstorm: Streamlit to Web Platform Migration

**Date:** 2026-01-15
**Session:** Architecture planning for Vietnam Dashboard web migration

---

## 1. Problem Statement

**Current State:**
- Streamlit dashboard với 7 pages, 50+ components
- Local parquet database (~500MB DATA/)
- 18 service classes xử lý data
- Premium dark theme với Plotly charts
- MCP Server (28 API tools) đã có sẵn

**Goals:**
- Multi-user concurrent access
- Performance improvement (faster loading)
- UI/UX customization
- Professional deployment (domain, SSL)
- Scalability (larger database, more functions)
- User management + community building

**Constraints:**
- Beginner in Python + Web dev
- Budget: ~$10-50/month hosting
- Timeline: 2-3 months
- Initial users: <10 people

---

## 2. Web Architecture Fundamentals

### What is Backend vs Frontend?

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER'S BROWSER                          │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    FRONTEND (Client)                       │  │
│  │  • HTML/CSS/JavaScript                                     │  │
│  │  • UI components, charts, tables                           │  │
│  │  • User interactions (clicks, inputs)                      │  │
│  │  • Sends requests to backend                               │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP Requests (API calls)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         CLOUD SERVER                            │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    BACKEND (Server)                        │  │
│  │  • Python/FastAPI                                          │  │
│  │  • Business logic, calculations                            │  │
│  │  • Authentication, authorization                           │  │
│  │  • Reads/writes to database                                │  │
│  └───────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                      DATABASE (Hybrid - VALIDATED)         │  │
│  │  • DuckDB → Query Parquet directly (stock data, ~500MB)    │  │
│  │  • PostgreSQL → Users/auth only (~few KB)                  │  │
│  │  ➡️ NO DATA MIGRATION NEEDED!                              │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Current Streamlit vs Target Architecture

| Aspect | Streamlit (Current) | Web App (Target) |
|--------|---------------------|------------------|
| Frontend | Python → HTML (auto) | React/Vue/HTML (manual) |
| Backend | Streamlit server | FastAPI/Flask |
| State | Session-based | API stateless + DB |
| Rendering | Server-side | Client-side (SPA) |
| Scaling | Limited | Horizontal scalable |
| Customization | Limited | Full control |

---

## 3. Tech Stack Options

### Option A: FastAPI + React (Recommended for Learning)

```
Frontend: React + TypeScript + TailwindCSS
Backend:  FastAPI (Python)
Database: PostgreSQL (or keep Parquet initially)
Hosting:  VPS (Viettel Cloud / DigitalOcean)
```

**Pros:**
- ✅ Most in-demand skills (career value)
- ✅ FastAPI uses Python (leverage existing code)
- ✅ React ecosystem is massive
- ✅ Best performance
- ✅ Full control over UI/UX

**Cons:**
- ❌ Steep learning curve (2 languages: Python + TypeScript)
- ❌ More complex setup
- ❌ 3+ months for beginner

**Learning Path:**
1. Python basics → FastAPI basics (2-3 weeks)
2. HTML/CSS → JavaScript basics (2 weeks)
3. React fundamentals (2-3 weeks)
4. Integration + deployment (2-3 weeks)

---

### Option B: FastAPI + HTMX (Simpler Alternative)

```
Frontend: HTML + HTMX + TailwindCSS (no JavaScript framework)
Backend:  FastAPI + Jinja2 templates
Database: PostgreSQL
Hosting:  VPS
```

**Pros:**
- ✅ No JavaScript framework needed
- ✅ Python-centric (templates in backend)
- ✅ Faster to learn
- ✅ Simpler mental model
- ✅ Good for data dashboards

**Cons:**
- ❌ Less interactive than React
- ❌ Smaller community
- ❌ May need JavaScript eventually for complex charts

**Learning Path:**
1. Python + FastAPI (2 weeks)
2. HTML + CSS + Tailwind (2 weeks)
3. HTMX basics (1 week)
4. Plotly.js or ApexCharts (1 week)
5. Deployment (1-2 weeks)

---

### Option C: Next.js Full-Stack (Modern, Complex)

```
Frontend: Next.js (React) + TypeScript
Backend:  Next.js API routes OR FastAPI separate
Database: PostgreSQL / Supabase
Hosting:  Vercel (managed) or VPS
```

**Pros:**
- ✅ All-in-one framework
- ✅ Excellent developer experience
- ✅ Built-in SSR/SSG (SEO, performance)
- ✅ Great for production apps

**Cons:**
- ❌ JavaScript/TypeScript heavy
- ❌ Complex for beginners
- ❌ Backend logic in JS (not Python)

---

### Option D: Streamlit Cloud + Enhancements (Quick Win)

```
Keep Streamlit, optimize performance, deploy to cloud
```

**Pros:**
- ✅ No rewrite needed
- ✅ Deploy in days
- ✅ Streamlit Cloud free tier available

**Cons:**
- ❌ Still has Streamlit limitations
- ❌ Multi-user performance issues remain
- ❌ Less learning opportunity

---

## 4. Tool Clarifications

### What You Asked About:

| Tool | What It Is | Use Case |
|------|-----------|----------|
| **FastAPI** | Python web framework | ✅ Backend API (RECOMMENDED) |
| **Tailwind CSS** | Utility-first CSS framework | ✅ Styling frontend (RECOMMENDED) |
| **HuggingFace** | AI/ML platform | ❌ Not needed for this project |
| **Firebase** | Google's BaaS (auth, db) | ⚠️ Overkill, use PostgreSQL |
| **Claude Code** | AI coding assistant | ✅ Use to help write code |

### Recommended Stack for Your Level:

```
Backend:   FastAPI (Python) - leverage existing skills
Frontend:  HTMX + Jinja2 templates (simpler) OR React (harder)
Database:  PostgreSQL (migrate from Parquet)
CSS:       Tailwind CSS (easy to learn)
Charts:    Plotly.js or ApexCharts
Auth:      FastAPI + JWT tokens
Hosting:   VPS (Viettel Cloud)
```

---

## 5. Hosting Options Analysis

### Option 1: Viettel Cloud VPS (Your Choice)

**Pricing:** ~300k-500k VND/month ($12-20 USD)

**Pros:**
- ✅ Local (Vietnam) - low latency for VN users
- ✅ Vietnamese support
- ✅ VND payment
- ✅ Full control

**Cons:**
- ❌ Manual setup (Linux, Docker, nginx)
- ❌ Manual SSL certificate setup
- ❌ Need to manage updates, security

**Best For:** Cost-effective, learn DevOps

---

### Option 2: DigitalOcean / Vultr / Linode

**Pricing:** $5-20 USD/month

**Pros:**
- ✅ Better documentation
- ✅ 1-click app deployments
- ✅ Global CDN options
- ✅ Good community tutorials

**Cons:**
- ❌ USD payment
- ❌ Still need manual setup
- ❌ Higher latency from Singapore/US

**Best For:** Learning standard cloud practices

---

### Option 3: Railway / Render (Managed PaaS)

**Pricing:** $5-25 USD/month

**Pros:**
- ✅ Auto deployment from Git
- ✅ Auto SSL, domains
- ✅ No server management
- ✅ PostgreSQL included
- ✅ Very beginner-friendly

**Cons:**
- ❌ Less control
- ❌ More expensive at scale
- ❌ USD only

**Best For:** Fast deployment, focus on code not ops

---

### Option 4: Vercel (Frontend) + Railway (Backend)

**Pricing:** Free tier available, ~$10-20 for production

**Pros:**
- ✅ Best performance (edge CDN)
- ✅ Auto deployments
- ✅ Great developer experience

**Cons:**
- ❌ Split architecture
- ❌ Complexity

**Best For:** Production-grade, scaling

---

### Hosting Recommendation

**For Your Level (Beginner, Learning):**

```
Phase 1: Railway or Render (managed)
- Focus on code, not DevOps
- Auto SSL, auto deploy
- ~$10-15/month

Phase 2 (later): Migrate to Viettel Cloud VPS
- When you understand the stack better
- Save costs at scale
```

---

## 6. Recommended Architecture

Given your constraints (beginner, learning focus, 2-3 months), I recommend:

### **"Option B: FastAPI + HTMX"** with phased approach

```
┌─────────────────────────────────────────────────────────────────┐
│                      ARCHITECTURE                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Browser                                                       │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  HTML + HTMX + Tailwind CSS + Plotly.js               │   │
│   │  - Server-rendered pages (Jinja2 templates)            │   │
│   │  - HTMX for dynamic updates without full JS            │   │
│   │  - Plotly.js for interactive charts                    │   │
│   └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│   Railway / Render (Managed Hosting)                           │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  FastAPI Backend                                        │   │
│   │  - /api/* endpoints (JSON for charts)                   │   │
│   │  - /* pages (HTML rendered)                             │   │
│   │  - Reuse existing PROCESSORS/ logic                     │   │
│   │  - JWT authentication                                   │   │
│   └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  PostgreSQL Database                                    │   │
│   │  - Migrate from Parquet files                           │   │
│   │  - User management tables                               │   │
│   │  - Session/activity logs                                │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Why This Stack?

1. **FastAPI**: Python-based, reuse existing PROCESSORS/
2. **HTMX**: No JavaScript framework to learn
3. **Tailwind**: Easy CSS, dark mode built-in
4. **Plotly.js**: Same charts as Streamlit
5. **PostgreSQL**: Better for multi-user than Parquet
6. **Railway**: Auto deploy, no DevOps headache

---

## 7. Migration Plan Overview

### Phase 1: Foundation (Week 1-4)

**Goals:** Setup environment, learn basics

- [ ] Learn FastAPI fundamentals
- [ ] Learn HTML/CSS/Tailwind basics
- [ ] Setup PostgreSQL database
- [ ] Migrate ticker data from Parquet to PostgreSQL
- [ ] Create first API endpoint (list tickers)

### Phase 2: Core Features (Week 5-8)

**Goals:** Rebuild main dashboard pages

- [ ] Company Analysis page
- [ ] Bank Analysis page
- [ ] Charts with Plotly.js
- [ ] Basic authentication (login/register)

### Phase 3: Advanced (Week 9-12)

**Goals:** Full feature parity + deployment

- [ ] Technical Analysis page
- [ ] Valuation page
- [ ] User management
- [ ] Deploy to Railway/Render
- [ ] Custom domain + SSL

### Phase 4: Optimization (Post-launch)

- [ ] Performance tuning
- [ ] Migrate to Viettel Cloud (if needed)
- [ ] Community features

---

## 8. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Learning curve too steep | High | Start with HTMX, not React |
| Timeline overrun | Medium | Prioritize core features, defer extras |
| Data migration issues | Medium | Keep Parquet as backup, gradual migration |
| Performance problems | Low | Use caching, CDN, PostgreSQL indexes |
| Security vulnerabilities | High | Use established auth libraries, HTTPS |

---

## 9. Alternative: Hybrid Approach

If full rewrite feels overwhelming:

**Keep Streamlit for MVP, enhance gradually:**

1. Deploy Streamlit to Streamlit Cloud (1 day)
2. Add nginx reverse proxy for custom domain
3. Add authentication via Streamlit-Authenticator
4. Gradually build FastAPI backend alongside
5. Migrate page-by-page over 6 months

**Pros:** Faster initial deployment
**Cons:** Technical debt, still limited by Streamlit

---

## 10. Validated Architecture (Final Decision - 2026-01-15)

Sau khi thảo luận, bạn đã chọn **Next.js + FastAPI + DuckDB/PostgreSQL hybrid**.

### Final Tech Stack

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    VALIDATED PRODUCTION ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Browser (User)                                                            │
│        │                                                                    │
│        │ HTTPS (443)                                                        │
│        ▼                                                                    │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                         NGINX                                        │   │
│   │          Reverse proxy + SSL (Let's Encrypt)                        │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│        │                              │                                     │
│        ▼                              ▼                                     │
│   ┌────────────────┐           ┌────────────────┐                          │
│   │   Next.js 14   │           │    FastAPI     │   ← Docker containers    │
│   │   (Frontend)   │           │   (Backend)    │                          │
│   │   :3000        │           │   :8000        │                          │
│   │                │           │                │                          │
│   │  • React       │  ──API──▶ │  • PROCESSORS/ │                          │
│   │  • TypeScript  │  calls    │  • JWT Auth    │                          │
│   │  • TailwindCSS │           │  • DuckDB      │                          │
│   │  • SWR cache   │           │                │                          │
│   │  • ApexCharts  │           │                │                          │
│   └────────────────┘           └────────────────┘                          │
│                                       │                                     │
│                          ┌────────────┴────────────┐                       │
│                          ▼                         ▼                        │
│                  ┌──────────────┐          ┌──────────────┐                │
│                  │  PostgreSQL  │          │   DuckDB     │                │
│                  │  (Users)     │          │  (Stock)     │                │
│                  │              │          │              │                │
│                  │  • users     │          │  Queries     │                │
│                  │  • sessions  │          │  Parquet     │                │
│                  │  • ~few KB   │          │  directly!   │                │
│                  └──────────────┘          └──────────────┘                │
│                                                   │                        │
│                                                   ▼                        │
│                                         ┌──────────────────┐               │
│                                         │  DATA/*.parquet  │               │
│                                         │  (~500MB)        │               │
│                                         │  NO MIGRATION!   │               │
│                                         └──────────────────┘               │
│                                                                             │
│   HOSTING: Viettel Cloud VPS (Ubuntu 22.04 LTS, ~300-500k VND/month)       │
│   DOMAIN: Custom domain + Let's Encrypt SSL (free)                         │
│   DATA UPDATES: Cron (4:30 PM daily) + Manual trigger API                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Why DuckDB + PostgreSQL Hybrid?

| Database | Purpose | Size | Notes |
|----------|---------|------|-------|
| **DuckDB** | Stock data queries | 0 KB | Queries Parquet directly, NO migration! |
| **PostgreSQL** | Users, auth, sessions | ~few KB | Simple, small tables only |

**Key Benefit:** Không cần migrate 500MB Parquet data → DuckDB query trực tiếp!

### Monorepo Structure

```
vietnam-dashboard-web/
├── frontend/                 # Next.js 14 (App Router)
│   ├── app/                  # Pages, layouts
│   ├── components/           # React components
│   ├── hooks/                # useSWR custom hooks
│   └── lib/                  # Utils, API client
│
├── backend/                  # FastAPI
│   ├── app/
│   │   ├── main.py          # FastAPI app
│   │   ├── routes/          # API endpoints
│   │   ├── services/        # DuckDB queries (từ WEBAPP/services/)
│   │   └── models/          # Pydantic models
│   └── processors/          # Symlink hoặc copy từ PROCESSORS/
│
├── DATA/                     # Parquet files (mounted)
│   ├── processed/           # Stock data (~500MB)
│   └── raw/                 # Raw data
│
├── docker-compose.yml       # Container orchestration
├── nginx.conf               # Reverse proxy config
└── .env                     # Environment variables
```

### Data Flow

```
User Request → Next.js → FastAPI → DuckDB → Parquet files
                  │           │
                  │           └─→ PostgreSQL (auth only)
                  │
                  └─→ SWR Cache (frontend)
```

---

## 11. Decision Summary

### Final Decisions (Validated 2026-01-15):

| Aspect | Your Choice | Reason |
|--------|-------------|--------|
| **Backend** | FastAPI | Python, reuse existing PROCESSORS/ |
| **Frontend** | Next.js 14 + TypeScript + Tailwind | Full control, career value |
| **Database** | DuckDB + PostgreSQL hybrid | No migration! DuckDB queries Parquet |
| **Charts** | ApexCharts (candlesticks) + Recharts | Better financial chart support |
| **Data Fetching** | SWR | Simpler than React Query for beginners |
| **Auth** | JWT + HttpOnly cookies | Secure, professional approach |
| **Hosting** | Viettel Cloud VPS (Ubuntu 22.04 LTS) | Local VN, cost-effective (~300-500k/month) |
| **Data Updates** | Cron (4:30 PM) + Manual API | Both options available |
| **Timeline** | 20 weeks | Realistic for beginner with 4 weeks learning |

### Estimated Timeline (Realistic):

| Phase | Duration | Output |
|-------|----------|--------|
| Learning | 4 weeks | Understand stack |
| Core Build | 6 weeks | Main features |
| Polish + Deploy | 2-4 weeks | Production ready |
| **Total** | **12-14 weeks** | Full migration |

⚠️ **Note:** 2-3 months is ambitious for a beginner. Plan for 3-4 months realistically.

---

## 11. Next Steps

1. **Decide on frontend approach:** HTMX (simpler) vs React (harder but more powerful)
2. **Decide on hosting:** Railway (easy) vs Viettel Cloud (cheaper but complex)
3. **Start learning path:** FastAPI → HTML/CSS → chosen frontend
4. **Create detailed implementation plan** with Claude Code

---

## Unresolved Questions

1. Do you want real-time data updates (WebSocket) or periodic refresh is fine?
2. Mobile responsiveness - how important?
3. Data update pipeline - will you run daily updates on server or manually?
4. Budget for domain name (~$10-15/year)?

---

*Report generated by brainstormer agent | 2026-01-15*
