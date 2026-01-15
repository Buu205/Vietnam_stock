---
title: "Streamlit to Next.js + FastAPI Migration"
description: "Complete migration from Streamlit dashboard to modern web stack with Next.js frontend and FastAPI backend"
status: pending
priority: P2
effort: 20w
branch: main
tags: [migration, nextjs, fastapi, web, beginner-friendly]
created: 2026-01-15
---

# Streamlit to Next.js + FastAPI Migration Plan

## Overview

**Goal:** Migrate Vietnam Dashboard from Streamlit to a production-ready web application

**Why Migrate?**
- Multi-user concurrent access (Streamlit bottleneck)
- Full UI/UX customization control
- Professional deployment with custom domain
- Scalability for future growth
- Learning opportunity for modern web stack

**Target Stack:**
- **Frontend:** Next.js 14+ (App Router) + TypeScript + TailwindCSS
- **Backend:** FastAPI (Python) - reuses existing PROCESSORS/
- **Database:** **Hybrid approach** - DuckDB for stock data (query Parquet directly) + PostgreSQL for users/auth
- **Charts:** ApexCharts (candlesticks) + Recharts (simple charts)
- **Auth:** JWT tokens with HttpOnly cookies
- **Hosting:** Viettel Cloud VPS (Ubuntu 22.04 LTS + Docker + Nginx)
- **Data Updates:** Auto cron job + manual trigger options

**Timeline:** 20 weeks (realistic for beginner)

---

## Current State Summary

| Component | Count | Description |
|-----------|-------|-------------|
| Pages | 7 | Company, Bank, Security, Sector, Technical, Forecast, FX |
| Services | 18 | Data loading layer (BaseService pattern) |
| Components | 50+ | Streamlit UI components |
| Tickers | 457 | Across 4 entity types |
| Sectors | 19 | Vietnamese market sectors |
| Metrics | 2,099 | Vietnamese-English mapped |
| Data Size | ~500MB | Parquet files in DATA/ |

**Key Assets to Preserve:**
- `PROCESSORS/` - All business logic, calculators, transformers
- `config/registries/` - MetricRegistry, SectorRegistry, SchemaRegistry
- `WEBAPP/services/` - Data loading patterns (migrate to FastAPI)
- `MCP_SERVER/` - Reference for FastAPI patterns (28 tools)

---

## Phase Overview

| Phase | Duration | Focus | Key Deliverable |
|-------|----------|-------|-----------------|
| [Phase 1](./phases/phase-01-environment-setup-learning.md) | Week 1-4 | Foundation Learning | Dev environment + basic skills |
| [Phase 2](./phases/phase-02-backend-api.md) | Week 5-8 | Backend API | FastAPI server with core endpoints |
| [Phase 3](./phases/phase-03-frontend-core.md) | Week 9-12 | Frontend Core | Next.js shell + first page |
| [Phase 4](./phases/phase-04-feature-implementation.md) | Week 13-18 | Feature Build | All pages migrated |
| [Phase 5](./phases/phase-05-deployment.md) | Week 19-20 | Deployment | Production on Viettel Cloud |
| [Phase 6](./phases/phase-06-production.md) | Week 21+ | Production | Monitoring + optimization |

---

## Research References

- [Next.js + FastAPI Architecture](./research/researcher-nextjs-fastapi-architecture.md)
- [VPS Deployment + DevOps](./research/researcher-vps-deployment-devops.md)
- [Brainstorm: Migration Options](../reports/brainstorm-260115-1115-streamlit-to-web-migration.md)

---

## Architecture Diagram

```
                    PRODUCTION ARCHITECTURE
    ============================================================

    Browser (User)
         |
         | HTTPS (443)
         v
    +-------------------+
    |     NGINX         |  Reverse proxy + SSL termination
    |  (Let's Encrypt)  |
    +-------------------+
         |           |
         v           v
    +--------+   +----------+
    |Next.js |   | FastAPI  |   Docker containers
    | :3000  |   |  :8000   |
    +--------+   +----------+
         |           |
         |           +--------+
         |                    |
         v                    v
    +---------+         +-----------+    +----------+
    |   SWR   |         |PostgreSQL |    | DuckDB   |
    | (Cache) |         | (Users)   |    | (Stock)  |
    +---------+         +-----------+    +----------+
                                              |
                                         Parquet files
                                         (DATA/*.parquet)

    MONOREPO STRUCTURE
    ============================================================
    vietnam-dashboard-web/
    +-- frontend/              # Next.js 14 (App Router)
    |   +-- app/
    |   +-- components/
    |   +-- lib/
    |   +-- hooks/
    +-- backend/               # FastAPI
    |   +-- app/
    |   +-- routes/
    |   +-- services/          # Migrate from WEBAPP/services/
    |   +-- processors/        # Symlink or copy from PROCESSORS/
    +-- shared/                # Shared types/constants
    +-- docker-compose.yml
    +-- nginx.conf
```

---

## Migration Priority (Pages)

Ordered by usage frequency and complexity:

1. **Company Analysis** (4 tabs) - Most used, moderate complexity
2. **Bank Analysis** (4 tabs) - Second most used, similar to Company
3. **Sector & Valuation** - Core feature, aggregation logic
4. **Technical Analysis** (3-layer system) - Complex charts
5. **BSC Forecast** (6 tabs) - Feature-rich
6. **Security Analysis** (4 tabs) - Similar to Company
7. **FX & Commodities** - Simplest, good for practice

---

## Learning Milestones (Beginner Focus)

**Week 1-2:** Python Fundamentals
- Variables, functions, classes
- File I/O, error handling
- Pandas basics (already familiar?)

**Week 3-4:** Web Fundamentals
- HTTP protocol, REST APIs
- HTML/CSS basics
- JavaScript fundamentals

**Week 5-6:** FastAPI Basics
- Routes, path parameters
- Pydantic models
- Dependency injection

**Week 7-8:** React/Next.js Basics
- Components, props, state
- Hooks (useState, useEffect)
- App Router patterns

**Week 9+:** Integration
- API calls from frontend
- Data fetching (SWR)
- Chart integration

---

## Risk Assessment

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Learning curve too steep | High | Medium | Phase 1 is 4 weeks of learning only |
| Timeline overrun | Medium | High | Prioritize core pages, defer extras |
| Data migration issues | Medium | Low | Keep Parquet as backup |
| Security vulnerabilities | High | Low | Use established auth patterns |
| VPS setup complexity | Medium | Medium | Follow detailed Phase 5 guide |

---

## Success Criteria

**Phase 1 Complete:**
- [ ] Dev environment working (Node.js, Python, Docker)
- [ ] Can explain HTTP request/response cycle
- [ ] First FastAPI endpoint returns data

**Phase 3 Complete:**
- [ ] Company Analysis page functional in Next.js
- [ ] Charts display correctly
- [ ] Auth flow works end-to-end

**Phase 5 Complete:**
- [ ] App live on custom domain with SSL
- [ ] <10 users can access simultaneously
- [ ] Daily data updates working

---

## Budget Estimate

| Item | Monthly Cost | Notes |
|------|-------------|-------|
| Viettel Cloud VPS | 300-500k VND | 2 vCPU, 2-4GB RAM |
| Domain (.com/.vn) | ~150k VND/year | One-time annual |
| SSL Certificate | Free | Let's Encrypt |
| **Total** | ~400k VND/month | Well within $10-50 budget |

---

## Next Steps

1. Read Phase 1 plan: [phase-01-environment-setup-learning.md](./phases/phase-01-environment-setup-learning.md)
2. Set up development environment
3. Complete learning milestones
4. Build first FastAPI endpoint

---

## Validation Summary

**Validated:** 2026-01-15
**Questions asked:** 6

### Confirmed Decisions

| Decision | User Choice | Notes |
|----------|-------------|-------|
| **Authentication** | Full JWT auth | Required for future expansion, professional approach |
| **Learning Time** | 4 weeks dedicated | User prioritizes understanding over speed |
| **Database Strategy** | DuckDB + PostgreSQL hybrid | Stock data stays in Parquet (DuckDB queries), users/auth in PostgreSQL |
| **Data Updates** | Auto cron + manual | Both options available on VPS |
| **Scale Target** | <10 users initially | Optimize for small group, scale later if needed |
| **DuckDB vs Postgres** | Hybrid approach | No data migration needed, DuckDB queries Parquet directly |
| **Server OS** | Ubuntu 22.04 LTS | Best Docker support, most tutorials, LTS until 2027 |

### Action Items (Plan Updates Needed)

- [x] Update Phase 2 to use DuckDB for stock data queries instead of PostgreSQL migration
- [x] Add DuckDB setup instructions in Phase 1
- [x] Update Phase 5 with both cron job AND manual update options
- [x] Simplify PostgreSQL setup (only users/sessions tables, not stock data)

**✅ All action items completed on 2026-01-15**

### Key Benefits of Validated Approach

1. **No data migration** - Parquet files work as-is with DuckDB
2. **Simpler architecture** - PostgreSQL only for auth, not 500MB of stock data
3. **Learning-first** - 4 weeks foundation ensures solid understanding
4. **Future-proof** - Full JWT auth ready for scaling

---

*Plan created: 2026-01-15 | Last updated: 2026-01-15 | Validated: 2026-01-15*
