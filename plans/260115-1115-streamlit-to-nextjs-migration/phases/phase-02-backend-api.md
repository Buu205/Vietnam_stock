# Phase 2: Backend API (FastAPI)

**Duration:** Week 5-8 (4 weeks)
**Priority:** P1 - Core Infrastructure
**Status:** Pending
**Prerequisites:** Phase 1 complete

---

## Context Links

- [Main Plan](../plan.md)
- [Phase 1: Setup & Learning](./phase-01-environment-setup-learning.md)
- [Next.js + FastAPI Architecture](../research/researcher-nextjs-fastapi-architecture.md)
- [Current Services](../../../WEBAPP/services/)

---

## Overview

This phase builds the FastAPI backend that will serve data to the Next.js frontend. The key insight: **we reuse existing Python code** from `PROCESSORS/` and convert `WEBAPP/services/` patterns to API endpoints.

**Database Strategy (Validated):**
- **DuckDB** → Query stock data from Parquet files directly (NO migration needed!)
- **PostgreSQL** → Users, sessions, auth only (very small, simple tables)

**Goals:**
- Project structure following best practices
- Core API endpoints for ticker/company data
- DuckDB for stock data queries (Parquet direct)
- PostgreSQL for user authentication only
- JWT authentication system

---

## Key Insights from Research

1. **Reuse existing code** - PROCESSORS/ calculators work as-is
2. **BaseService pattern** - Migrate WEBAPP/services/ to FastAPI routes
3. **Pydantic for validation** - Type-safe request/response
4. **JWT in HttpOnly cookies** - Secure auth without localStorage
5. **DuckDB for stock data** - Query Parquet directly, no migration needed!
6. **PostgreSQL simplified** - Only 2-3 tables: users, sessions (not 500MB of stock data)

---

## Requirements

- Phase 1 environment setup complete
- Docker running
- Basic Python/FastAPI understanding

---

## Architecture: Backend Structure

```
backend/
+-- app/
|   +-- __init__.py
|   +-- main.py              # FastAPI app entry point
|   +-- config.py            # Settings, env vars
|   +-- database.py          # PostgreSQL connection
|   +-- dependencies.py      # Shared dependencies (auth, db)
|   +-- models/              # Pydantic models
|   |   +-- __init__.py
|   |   +-- ticker.py        # Ticker schemas
|   |   +-- company.py       # Company schemas
|   |   +-- user.py          # User schemas
|   +-- routes/              # API endpoints
|   |   +-- __init__.py
|   |   +-- auth.py          # Login, register, logout
|   |   +-- tickers.py       # /api/tickers/*
|   |   +-- company.py       # /api/company/*
|   |   +-- bank.py          # /api/bank/*
|   |   +-- technical.py     # /api/technical/*
|   |   +-- valuation.py     # /api/valuation/*
|   +-- services/            # Business logic (from WEBAPP/services)
|   |   +-- __init__.py
|   |   +-- base_service.py
|   |   +-- company_service.py
|   |   +-- bank_service.py
+-- tests/
|   +-- test_tickers.py
|   +-- test_auth.py
+-- requirements.txt
+-- Dockerfile
```

---

## Related Code Files (Current Codebase)

| File | Purpose | How to Use |
|------|---------|------------|
| `WEBAPP/services/base_service.py` | Base service pattern | Copy and adapt for FastAPI |
| `WEBAPP/services/company_service.py` | Company data loading | Reference for API logic |
| `config/registries/sector_lookup.py` | SectorRegistry | Import directly |
| `config/registries/metric_lookup.py` | MetricRegistry | Import directly |
| `MCP_SERVER/bsc_mcp/server.py` | FastMCP patterns | Reference for API design |

---

## Implementation Steps

### Week 5: Project Structure & Database

#### Step 2.1: Create Backend Structure

- [ ] **Create full directory structure**
  ```bash
  cd backend
  mkdir -p app/models app/routes app/services tests
  touch app/__init__.py
  touch app/models/__init__.py
  touch app/routes/__init__.py
  touch app/services/__init__.py
  ```

- [ ] **Create config.py for settings**
  ```python
  # backend/app/config.py
  from pydantic_settings import BaseSettings
  from functools import lru_cache

  class Settings(BaseSettings):
      """Application settings from environment variables."""

      # Database
      database_url: str = "postgresql://postgres:postgres@localhost:5432/vietnam_dashboard"

      # JWT
      secret_key: str = "your-secret-key-change-in-production"
      algorithm: str = "HS256"
      access_token_expire_days: int = 7

      # CORS
      frontend_url: str = "http://localhost:3000"

      # Data paths (link to existing data)
      data_root: str = "../DATA"  # Relative to backend/

      class Config:
          env_file = ".env"

  @lru_cache()
  def get_settings() -> Settings:
      return Settings()
  ```

- [ ] **Create .env file**
  ```bash
  # backend/.env
  DATABASE_URL=postgresql://postgres:postgres@localhost:5432/vietnam_dashboard
  SECRET_KEY=change-this-to-random-string-in-production
  DATA_ROOT=../DATA
  ```

#### Step 2.2: PostgreSQL with Docker

- [ ] **Create docker-compose.yml** (in project root)
  ```yaml
  version: '3.9'
  services:
    postgres:
      image: postgres:16-alpine
      container_name: vn_dashboard_db
      ports:
        - "5432:5432"
      environment:
        POSTGRES_USER: postgres
        POSTGRES_PASSWORD: postgres
        POSTGRES_DB: vietnam_dashboard
      volumes:
        - postgres_data:/var/lib/postgresql/data
      healthcheck:
        test: ["CMD-SHELL", "pg_isready -U postgres"]
        interval: 5s
        timeout: 5s
        retries: 5

  volumes:
    postgres_data:
  ```

- [ ] **Start PostgreSQL**
  ```bash
  docker-compose up -d postgres
  docker-compose logs postgres  # Check it's running
  ```

- [ ] **Create database.py**
  ```python
  # backend/app/database.py
  from sqlalchemy import create_engine
  from sqlalchemy.ext.declarative import declarative_base
  from sqlalchemy.orm import sessionmaker
  from app.config import get_settings

  settings = get_settings()

  engine = create_engine(settings.database_url)
  SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
  Base = declarative_base()

  def get_db():
      """Dependency that provides database session."""
      db = SessionLocal()
      try:
          yield db
      finally:
          db.close()
  ```

#### Step 2.3: Create Database Models

- [ ] **User model for authentication**
  ```python
  # backend/app/models/db_models.py
  from sqlalchemy import Column, Integer, String, DateTime, Boolean
  from sqlalchemy.sql import func
  from app.database import Base

  class User(Base):
      __tablename__ = "users"

      id = Column(Integer, primary_key=True, index=True)
      email = Column(String, unique=True, index=True, nullable=False)
      hashed_password = Column(String, nullable=False)
      full_name = Column(String)
      is_active = Column(Boolean, default=True)
      created_at = Column(DateTime(timezone=True), server_default=func.now())
  ```

- [ ] **Create tables**
  ```python
  # Run once to create tables
  from app.database import engine, Base
  from app.models.db_models import User

  Base.metadata.create_all(bind=engine)
  ```

### Week 6: Core API Endpoints

#### Step 2.4: Pydantic Models (Request/Response)

- [ ] **Create ticker models**
  ```python
  # backend/app/models/ticker.py
  from pydantic import BaseModel
  from typing import Optional, List

  class TickerBase(BaseModel):
      """Base ticker information."""
      ticker: str
      company_name: Optional[str] = None
      sector: Optional[str] = None
      entity_type: str  # COMPANY, BANK, INSURANCE, SECURITY

  class TickerInfo(TickerBase):
      """Full ticker information."""
      industry: Optional[str] = None

  class TickerList(BaseModel):
      """Response for ticker list."""
      tickers: List[str]
      count: int

  class PeerList(BaseModel):
      """Response for peer companies."""
      ticker: str
      sector: str
      peers: List[str]
  ```

- [ ] **Create company models**
  ```python
  # backend/app/models/company.py
  from pydantic import BaseModel
  from typing import Optional, List
  from datetime import date

  class CompanyMetrics(BaseModel):
      """Company financial metrics."""
      symbol: str
      report_date: date
      year: int
      quarter: Optional[int] = None

      # Income statement
      net_revenue: Optional[float] = None
      gross_profit: Optional[float] = None
      ebit: Optional[float] = None
      npatmi: Optional[float] = None  # Net profit after tax

      # Margins
      gross_profit_margin: Optional[float] = None
      ebit_margin: Optional[float] = None
      net_margin: Optional[float] = None

      # Ratios
      roe: Optional[float] = None
      roa: Optional[float] = None
      eps: Optional[float] = None
      bvps: Optional[float] = None

      class Config:
          from_attributes = True

  class CompanyMetricsResponse(BaseModel):
      """Response for company metrics."""
      ticker: str
      period: str
      data: List[CompanyMetrics]
      count: int
  ```

#### Step 2.5: Ticker Routes

- [ ] **Create ticker endpoints**
  ```python
  # backend/app/routes/tickers.py
  from fastapi import APIRouter, HTTPException, Query
  from typing import Optional
  import sys
  from pathlib import Path

  # Add project root to path for imports
  project_root = Path(__file__).resolve().parents[4]
  if str(project_root) not in sys.path:
      sys.path.insert(0, str(project_root))

  from config.registries import SectorRegistry
  from app.models.ticker import TickerInfo, TickerList, PeerList

  router = APIRouter(prefix="/api/tickers", tags=["tickers"])

  # Initialize registry (cached)
  _sector_reg = None
  def get_sector_registry():
      global _sector_reg
      if _sector_reg is None:
          _sector_reg = SectorRegistry()
      return _sector_reg

  @router.get("/", response_model=TickerList)
  def list_tickers(
      entity_type: Optional[str] = Query(None, description="Filter by BANK, COMPANY, etc"),
      sector: Optional[str] = Query(None, description="Filter by sector name"),
      limit: int = Query(50, le=500)
  ):
      """List all available tickers with optional filtering."""
      reg = get_sector_registry()

      if entity_type:
          tickers = reg.get_tickers_by_entity_type(entity_type)
      elif sector:
          tickers = reg.get_tickers_by_sector(sector)
      else:
          tickers = reg.get_all_tickers()

      tickers = sorted(tickers)[:limit]
      return TickerList(tickers=tickers, count=len(tickers))

  @router.get("/{ticker}", response_model=TickerInfo)
  def get_ticker_info(ticker: str):
      """Get detailed information about a specific ticker."""
      reg = get_sector_registry()
      info = reg.get_ticker(ticker.upper())

      if not info:
          raise HTTPException(status_code=404, detail=f"Ticker {ticker} not found")

      return TickerInfo(
          ticker=info.get("ticker"),
          company_name=info.get("company_name"),
          sector=info.get("sector"),
          entity_type=info.get("entity_type"),
          industry=info.get("industry")
      )

  @router.get("/{ticker}/peers", response_model=PeerList)
  def get_ticker_peers(ticker: str, limit: int = Query(10, le=20)):
      """Get peer companies in the same sector."""
      reg = get_sector_registry()
      info = reg.get_ticker(ticker.upper())

      if not info:
          raise HTTPException(status_code=404, detail=f"Ticker {ticker} not found")

      peers = reg.get_peers(ticker.upper(), limit=limit)

      return PeerList(
          ticker=ticker.upper(),
          sector=info.get("sector", "Unknown"),
          peers=peers
      )
  ```

#### Step 2.6: Company Routes

- [ ] **Create company service (using DuckDB)**
  ```python
  # backend/app/services/company_service.py
  import duckdb
  import pandas as pd
  from pathlib import Path
  from typing import Optional, Dict
  from app.config import get_settings

  class CompanyService:
      """Service for loading company financial data using DuckDB.

      DuckDB queries Parquet files directly - fast and no data migration needed!
      """

      def __init__(self):
          settings = get_settings()
          self.data_path = Path(settings.data_root) / "processed" / "fundamental" / "company"
          self.file_path = self.data_path / "company_financial_metrics.parquet"

      def get_financial_data(
          self,
          ticker: str,
          period: str = "Quarterly",
          limit: Optional[int] = None
      ) -> pd.DataFrame:
          """
          Load financial data for a company ticker using DuckDB.

          DuckDB advantages:
          - Queries Parquet directly (no loading entire file to memory)
          - SQL syntax for filtering, sorting, limiting
          - Much faster for large files
          """
          if not self.file_path.exists():
              raise FileNotFoundError(f"Data file not found: {self.file_path}")

          freq_code = 'Q' if period == "Quarterly" else 'Y'
          limit_clause = f"LIMIT {limit}" if limit else ""

          # DuckDB SQL query directly on Parquet
          query = f"""
              SELECT *
              FROM read_parquet('{self.file_path}')
              WHERE symbol = '{ticker.upper()}'
                AND freq_code = '{freq_code}'
              ORDER BY report_date DESC
              {limit_clause}
          """

          return duckdb.query(query).df()

      def get_latest_metrics(self, ticker: str) -> Dict:
          """Get latest quarter metrics for a ticker."""
          df = self.get_financial_data(ticker, "Quarterly", limit=1)
          if df.empty:
              return {}

          row = df.iloc[0]  # First row is latest (DESC order)
          return {
              "symbol": row.get("symbol"),
              "report_date": str(row.get("report_date")),
              "net_revenue": row.get("net_revenue"),
              "npatmi": row.get("npatmi"),
              "roe": row.get("roe"),
              "roa": row.get("roa"),
              "eps": row.get("eps"),
              "gross_profit_margin": row.get("gross_profit_margin"),
              "net_margin": row.get("net_margin")
          }
  ```

  **Why DuckDB?**
  - No need to migrate 500MB of Parquet data to PostgreSQL
  - SQL queries directly on Parquet files
  - Columnar storage = only reads columns you need
  - Fast filtering, sorting, aggregation

- [ ] **Create company endpoints**
  ```python
  # backend/app/routes/company.py
  from fastapi import APIRouter, HTTPException, Query
  from typing import List
  from app.services.company_service import CompanyService
  from app.models.company import CompanyMetrics, CompanyMetricsResponse

  router = APIRouter(prefix="/api/company", tags=["company"])

  # Service instance (could use dependency injection)
  _service = None
  def get_service():
      global _service
      if _service is None:
          _service = CompanyService()
      return _service

  @router.get("/{ticker}/metrics", response_model=CompanyMetricsResponse)
  def get_company_metrics(
      ticker: str,
      period: str = Query("Quarterly", enum=["Quarterly", "Yearly"]),
      limit: int = Query(8, le=40)
  ):
      """Get financial metrics for a company."""
      service = get_service()

      try:
          df = service.get_financial_data(ticker, period, limit)
      except FileNotFoundError as e:
          raise HTTPException(status_code=500, detail=str(e))

      if df.empty:
          raise HTTPException(
              status_code=404,
              detail=f"No data found for ticker {ticker}"
          )

      # Convert DataFrame to list of dicts
      records = df.to_dict('records')

      return CompanyMetricsResponse(
          ticker=ticker.upper(),
          period=period,
          data=[CompanyMetrics(**r) for r in records],
          count=len(records)
      )

  @router.get("/{ticker}/latest")
  def get_company_latest(ticker: str):
      """Get latest quarter metrics for a company."""
      service = get_service()
      metrics = service.get_latest_metrics(ticker)

      if not metrics:
          raise HTTPException(
              status_code=404,
              detail=f"No data found for ticker {ticker}"
          )

      return metrics
  ```

### Week 7: Authentication System

#### Step 2.7: JWT Authentication

- [ ] **Create auth dependencies**
  ```python
  # backend/app/dependencies.py
  from fastapi import Depends, HTTPException, status, Request
  from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
  from jose import JWTError, jwt
  from datetime import datetime, timedelta
  from passlib.context import CryptContext
  from app.config import get_settings
  from app.database import get_db
  from sqlalchemy.orm import Session
  from app.models.db_models import User

  settings = get_settings()
  pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
  security = HTTPBearer(auto_error=False)

  def verify_password(plain_password: str, hashed_password: str) -> bool:
      return pwd_context.verify(plain_password, hashed_password)

  def get_password_hash(password: str) -> str:
      return pwd_context.hash(password)

  def create_access_token(data: dict) -> str:
      to_encode = data.copy()
      expire = datetime.utcnow() + timedelta(days=settings.access_token_expire_days)
      to_encode.update({"exp": expire})
      return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

  def get_current_user_from_cookie(request: Request, db: Session = Depends(get_db)):
      """Extract user from HttpOnly cookie."""
      token = request.cookies.get("access_token")

      if not token:
          raise HTTPException(
              status_code=status.HTTP_401_UNAUTHORIZED,
              detail="Not authenticated"
          )

      try:
          payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
          email: str = payload.get("sub")
          if email is None:
              raise HTTPException(status_code=401, detail="Invalid token")
      except JWTError:
          raise HTTPException(status_code=401, detail="Invalid token")

      user = db.query(User).filter(User.email == email).first()
      if user is None:
          raise HTTPException(status_code=401, detail="User not found")

      return user
  ```

- [ ] **Create auth routes**
  ```python
  # backend/app/routes/auth.py
  from fastapi import APIRouter, HTTPException, Depends, Response
  from fastapi.responses import JSONResponse
  from sqlalchemy.orm import Session
  from pydantic import BaseModel, EmailStr
  from app.database import get_db
  from app.models.db_models import User
  from app.dependencies import (
      verify_password,
      get_password_hash,
      create_access_token,
      get_current_user_from_cookie
  )

  router = APIRouter(prefix="/auth", tags=["auth"])

  class UserCreate(BaseModel):
      email: EmailStr
      password: str
      full_name: str

  class UserLogin(BaseModel):
      email: EmailStr
      password: str

  class UserResponse(BaseModel):
      id: int
      email: str
      full_name: str
      is_active: bool

      class Config:
          from_attributes = True

  @router.post("/register", response_model=UserResponse)
  def register(user: UserCreate, db: Session = Depends(get_db)):
      """Register a new user."""
      # Check if email exists
      existing = db.query(User).filter(User.email == user.email).first()
      if existing:
          raise HTTPException(status_code=400, detail="Email already registered")

      # Create user
      db_user = User(
          email=user.email,
          hashed_password=get_password_hash(user.password),
          full_name=user.full_name
      )
      db.add(db_user)
      db.commit()
      db.refresh(db_user)

      return db_user

  @router.post("/login")
  def login(user: UserLogin, db: Session = Depends(get_db)):
      """Login and set HttpOnly cookie."""
      db_user = db.query(User).filter(User.email == user.email).first()

      if not db_user or not verify_password(user.password, db_user.hashed_password):
          raise HTTPException(status_code=401, detail="Invalid credentials")

      access_token = create_access_token(data={"sub": db_user.email})

      response = JSONResponse(content={"message": "Login successful"})
      response.set_cookie(
          key="access_token",
          value=access_token,
          httponly=True,
          samesite="lax",
          secure=False,  # Set True in production with HTTPS
          max_age=7 * 24 * 60 * 60  # 7 days
      )

      return response

  @router.post("/logout")
  def logout():
      """Logout by clearing cookie."""
      response = JSONResponse(content={"message": "Logged out"})
      response.delete_cookie(key="access_token")
      return response

  @router.get("/me", response_model=UserResponse)
  def get_current_user(user: User = Depends(get_current_user_from_cookie)):
      """Get current authenticated user."""
      return user
  ```

### Week 8: Integration & Testing

#### Step 2.8: Wire Up Main App

- [ ] **Update main.py with all routes**
  ```python
  # backend/app/main.py
  from fastapi import FastAPI
  from fastapi.middleware.cors import CORSMiddleware
  from app.config import get_settings
  from app.database import engine, Base
  from app.routes import auth, tickers, company

  # Create database tables
  Base.metadata.create_all(bind=engine)

  settings = get_settings()

  app = FastAPI(
      title="Vietnam Dashboard API",
      description="Backend API for Vietnam stock market dashboard",
      version="0.1.0"
  )

  # CORS middleware
  app.add_middleware(
      CORSMiddleware,
      allow_origins=[settings.frontend_url],
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
  )

  # Include routers
  app.include_router(auth.router)
  app.include_router(tickers.router)
  app.include_router(company.router)

  @app.get("/")
  def read_root():
      return {"status": "ok", "message": "Vietnam Dashboard API"}

  @app.get("/api/health")
  def health_check():
      return {"status": "healthy"}
  ```

#### Step 2.9: Write Tests

- [ ] **Create test for tickers endpoint**
  ```python
  # backend/tests/test_tickers.py
  from fastapi.testclient import TestClient
  from app.main import app

  client = TestClient(app)

  def test_list_tickers():
      response = client.get("/api/tickers/")
      assert response.status_code == 200
      data = response.json()
      assert "tickers" in data
      assert "count" in data
      assert len(data["tickers"]) > 0

  def test_get_ticker_info():
      response = client.get("/api/tickers/VNM")
      assert response.status_code == 200
      data = response.json()
      assert data["ticker"] == "VNM"
      assert "entity_type" in data

  def test_get_nonexistent_ticker():
      response = client.get("/api/tickers/XXXXXX")
      assert response.status_code == 404
  ```

- [ ] **Run tests**
  ```bash
  cd backend
  pip install pytest pytest-cov
  pytest tests/ -v
  ```

#### Step 2.10: API Documentation

- [ ] **Verify Swagger UI**
  - Start server: `uvicorn app.main:app --reload`
  - Open: http://localhost:8000/docs
  - Test all endpoints manually

---

## Success Criteria

### API Endpoints Working

- [ ] `GET /api/tickers/` - Lists tickers with filters
- [ ] `GET /api/tickers/{ticker}` - Returns ticker info
- [ ] `GET /api/tickers/{ticker}/peers` - Returns peer list
- [ ] `GET /api/company/{ticker}/metrics` - Returns financial data
- [ ] `POST /auth/register` - Creates new user
- [ ] `POST /auth/login` - Sets auth cookie
- [ ] `GET /auth/me` - Returns current user (protected)

### Database Setup

- [ ] PostgreSQL running in Docker
- [ ] User table created
- [ ] Can register and login users

### Code Quality

- [ ] All tests pass
- [ ] Swagger docs accessible
- [ ] No hardcoded secrets (use .env)

---

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Path resolution issues | Medium | Use absolute paths, verify imports |
| Database connection errors | Medium | Check Docker is running, verify .env |
| CORS errors | Medium | Match frontend URL exactly in settings |
| Parquet file not found | High | Verify DATA_ROOT points to correct location |

---

## Checkpoint Questions

Before moving to Phase 3, you should be able to answer:

1. What is the difference between a Pydantic model and SQLAlchemy model?
2. How does dependency injection work in FastAPI?
3. Why use HttpOnly cookies instead of localStorage for tokens?
4. What does `response_model` do in a FastAPI route?
5. How do you protect an endpoint to require authentication?

---

## Next Phase

After completing Phase 2, proceed to:
[Phase 3: Frontend Core](./phase-03-frontend-core.md)

---

*Phase created: 2026-01-15*
