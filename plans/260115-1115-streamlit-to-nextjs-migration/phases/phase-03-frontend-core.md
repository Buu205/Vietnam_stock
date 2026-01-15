# Phase 3: Frontend Core (Next.js)

**Duration:** Week 9-12 (4 weeks)
**Priority:** P1 - User Interface Foundation
**Status:** Pending
**Prerequisites:** Phase 2 complete (FastAPI backend running)

---

## Context Links

- [Main Plan](../plan.md)
- [Phase 2: Backend API](./phase-02-backend-api.md)
- [Next.js + FastAPI Architecture](../research/researcher-nextjs-fastapi-architecture.md)
- [Current Streamlit UI](../../../WEBAPP/pages/)

---

## Overview

This phase builds the Next.js frontend shell and migrates the first page (Company Analysis). You'll learn React patterns while creating a production-ready UI.

**Goals:**
- Project structure following Next.js 14 best practices
- Reusable component library with TailwindCSS
- API integration with SWR
- Complete Company Analysis page

---

## Key Insights from Research

1. **App Router** - Use Next.js 14 App Router (not Pages Router)
2. **Client Components** - Use `'use client'` for interactive components
3. **SWR** - Simple data fetching with automatic caching
4. **ApexCharts** - Best for candlestick and financial charts
5. **Dark Mode** - TailwindCSS has built-in dark mode support

---

## Requirements

- Phase 2 backend running on http://localhost:8000
- Node.js v20 installed
- Basic React understanding from Phase 1

---

## Architecture: Frontend Structure

```
frontend/
+-- app/                      # Next.js App Router
|   +-- (auth)/               # Auth group (login, register)
|   |   +-- login/
|   |   |   +-- page.tsx
|   |   +-- register/
|   |       +-- page.tsx
|   +-- dashboard/            # Main dashboard
|   |   +-- page.tsx          # Dashboard home
|   |   +-- company/
|   |   |   +-- page.tsx      # Company list
|   |   |   +-- [ticker]/     # Dynamic route
|   |   |       +-- page.tsx  # Company detail
|   |   +-- layout.tsx        # Dashboard layout (sidebar)
|   +-- layout.tsx            # Root layout
|   +-- page.tsx              # Landing page
|   +-- globals.css           # Global styles
+-- components/               # Reusable components
|   +-- ui/                   # Base UI components
|   |   +-- Button.tsx
|   |   +-- Card.tsx
|   |   +-- Input.tsx
|   |   +-- Table.tsx
|   |   +-- Select.tsx
|   +-- charts/               # Chart components
|   |   +-- CandleChart.tsx
|   |   +-- LineChart.tsx
|   |   +-- BarChart.tsx
|   +-- layout/               # Layout components
|   |   +-- Sidebar.tsx
|   |   +-- Header.tsx
|   |   +-- Footer.tsx
|   +-- company/              # Company-specific components
|       +-- MetricsCard.tsx
|       +-- FinancialsTable.tsx
|       +-- PeerComparison.tsx
+-- lib/                      # Utilities
|   +-- api.ts                # API client
|   +-- auth.ts               # Auth helpers
|   +-- utils.ts              # Formatting utils
|   +-- constants.ts          # App constants
+-- hooks/                    # Custom hooks
|   +-- useAuth.ts
|   +-- useCompany.ts
|   +-- useTickers.ts
+-- types/                    # TypeScript types
|   +-- api.ts
|   +-- company.ts
+-- public/                   # Static assets
+-- package.json
+-- tailwind.config.ts
+-- next.config.js
```

---

## Related Code Files (Current Codebase)

| File | Purpose | How to Use |
|------|---------|------------|
| `WEBAPP/pages/company/company_dashboard.py` | Current Company page | Reference for UI structure |
| `WEBAPP/components/` | Streamlit components | Reference for component patterns |
| `WEBAPP/core/styles.py` | Current styling | Reference for dark theme colors |

---

## Implementation Steps

### Week 9: Project Setup & Base Components

#### Step 3.1: Initialize Next.js Project

- [ ] **Create Next.js app with TypeScript**
  ```bash
  cd frontend
  # If not already created in Phase 1:
  npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir=false --import-alias="@/*"
  ```

- [ ] **Install dependencies**
  ```bash
  npm install swr                    # Data fetching
  npm install apexcharts react-apexcharts  # Charts
  npm install clsx                   # Class merging
  npm install @heroicons/react       # Icons
  ```

- [ ] **Configure dark mode in tailwind.config.ts**
  ```typescript
  import type { Config } from 'tailwindcss'

  const config: Config = {
    darkMode: 'class',  // Enable dark mode via class
    content: [
      './pages/**/*.{js,ts,jsx,tsx,mdx}',
      './components/**/*.{js,ts,jsx,tsx,mdx}',
      './app/**/*.{js,ts,jsx,tsx,mdx}',
    ],
    theme: {
      extend: {
        colors: {
          // Custom colors matching current dark theme
          background: '#0a0a0a',
          foreground: '#fafafa',
          card: {
            DEFAULT: '#1a1a1a',
            hover: '#2a2a2a',
          },
          primary: {
            DEFAULT: '#3b82f6',
            hover: '#2563eb',
          },
          success: '#22c55e',
          danger: '#ef4444',
          warning: '#f59e0b',
        },
      },
    },
    plugins: [],
  }

  export default config
  ```

#### Step 3.2: Create Base UI Components

- [ ] **Create Button component**
  ```tsx
  // frontend/components/ui/Button.tsx
  'use client'

  import { clsx } from 'clsx'
  import { ButtonHTMLAttributes, ReactNode } from 'react'

  interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: 'primary' | 'secondary' | 'danger'
    size?: 'sm' | 'md' | 'lg'
    children: ReactNode
  }

  export function Button({
    variant = 'primary',
    size = 'md',
    className,
    children,
    ...props
  }: ButtonProps) {
    return (
      <button
        className={clsx(
          'rounded-lg font-medium transition-colors',
          // Variants
          variant === 'primary' && 'bg-primary hover:bg-primary-hover text-white',
          variant === 'secondary' && 'bg-card hover:bg-card-hover text-white border border-gray-700',
          variant === 'danger' && 'bg-danger hover:bg-red-600 text-white',
          // Sizes
          size === 'sm' && 'px-3 py-1.5 text-sm',
          size === 'md' && 'px-4 py-2',
          size === 'lg' && 'px-6 py-3 text-lg',
          // Disabled
          'disabled:opacity-50 disabled:cursor-not-allowed',
          className
        )}
        {...props}
      >
        {children}
      </button>
    )
  }
  ```

- [ ] **Create Card component**
  ```tsx
  // frontend/components/ui/Card.tsx
  import { clsx } from 'clsx'
  import { ReactNode } from 'react'

  interface CardProps {
    title?: string
    children: ReactNode
    className?: string
  }

  export function Card({ title, children, className }: CardProps) {
    return (
      <div className={clsx(
        'bg-card rounded-lg p-4 border border-gray-800',
        className
      )}>
        {title && (
          <h3 className="text-lg font-semibold mb-3 text-white">{title}</h3>
        )}
        {children}
      </div>
    )
  }
  ```

- [ ] **Create MetricCard component**
  ```tsx
  // frontend/components/ui/MetricCard.tsx
  import { clsx } from 'clsx'

  interface MetricCardProps {
    label: string
    value: string | number
    change?: number
    format?: 'number' | 'percent' | 'currency'
  }

  export function MetricCard({ label, value, change, format }: MetricCardProps) {
    const formatValue = () => {
      if (typeof value === 'number') {
        switch (format) {
          case 'percent':
            return `${(value * 100).toFixed(2)}%`
          case 'currency':
            return value.toLocaleString('vi-VN') + ' VND'
          default:
            return value.toLocaleString('vi-VN')
        }
      }
      return value
    }

    return (
      <div className="bg-card rounded-lg p-4 border border-gray-800">
        <p className="text-gray-400 text-sm mb-1">{label}</p>
        <p className="text-2xl font-bold text-white">{formatValue()}</p>
        {change !== undefined && (
          <p className={clsx(
            'text-sm mt-1',
            change >= 0 ? 'text-success' : 'text-danger'
          )}>
            {change >= 0 ? '+' : ''}{(change * 100).toFixed(2)}%
          </p>
        )}
      </div>
    )
  }
  ```

- [ ] **Create Table component**
  ```tsx
  // frontend/components/ui/Table.tsx
  import { clsx } from 'clsx'
  import { ReactNode } from 'react'

  interface Column<T> {
    key: keyof T | string
    header: string
    render?: (value: any, row: T) => ReactNode
    className?: string
  }

  interface TableProps<T> {
    columns: Column<T>[]
    data: T[]
    className?: string
  }

  export function Table<T extends Record<string, any>>({
    columns,
    data,
    className
  }: TableProps<T>) {
    return (
      <div className={clsx('overflow-x-auto', className)}>
        <table className="w-full text-left">
          <thead>
            <tr className="border-b border-gray-700">
              {columns.map((col) => (
                <th
                  key={String(col.key)}
                  className="px-4 py-3 text-gray-400 font-medium text-sm"
                >
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row, i) => (
              <tr
                key={i}
                className="border-b border-gray-800 hover:bg-card-hover transition-colors"
              >
                {columns.map((col) => {
                  const value = row[col.key as keyof T]
                  return (
                    <td
                      key={String(col.key)}
                      className={clsx('px-4 py-3 text-white', col.className)}
                    >
                      {col.render ? col.render(value, row) : String(value ?? '')}
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    )
  }
  ```

#### Step 3.3: Create API Client

- [ ] **Create API client with SWR**
  ```tsx
  // frontend/lib/api.ts
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  interface FetchOptions extends RequestInit {
    params?: Record<string, string | number>
  }

  export async function apiFetch<T>(
    endpoint: string,
    options: FetchOptions = {}
  ): Promise<T> {
    const { params, ...fetchOptions } = options

    // Build URL with query params
    let url = `${API_URL}${endpoint}`
    if (params) {
      const searchParams = new URLSearchParams()
      Object.entries(params).forEach(([key, value]) => {
        searchParams.append(key, String(value))
      })
      url += `?${searchParams.toString()}`
    }

    const response = await fetch(url, {
      ...fetchOptions,
      credentials: 'include',  // Send cookies
      headers: {
        'Content-Type': 'application/json',
        ...fetchOptions.headers,
      },
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({}))
      throw new Error(error.detail || `API Error: ${response.status}`)
    }

    return response.json()
  }

  // SWR fetcher
  export const fetcher = <T>(url: string): Promise<T> => apiFetch<T>(url)
  ```

- [ ] **Create auth helpers**
  ```tsx
  // frontend/lib/auth.ts
  import { apiFetch } from './api'

  interface LoginData {
    email: string
    password: string
  }

  interface RegisterData extends LoginData {
    full_name: string
  }

  interface User {
    id: number
    email: string
    full_name: string
    is_active: boolean
  }

  export async function login(data: LoginData): Promise<void> {
    await apiFetch('/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  export async function register(data: RegisterData): Promise<User> {
    return apiFetch('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  export async function logout(): Promise<void> {
    await apiFetch('/auth/logout', { method: 'POST' })
  }

  export async function getCurrentUser(): Promise<User> {
    return apiFetch('/auth/me')
  }
  ```

### Week 10: Layout & Navigation

#### Step 3.4: Create Layout Components

- [ ] **Create Sidebar component**
  ```tsx
  // frontend/components/layout/Sidebar.tsx
  'use client'

  import Link from 'next/link'
  import { usePathname } from 'next/navigation'
  import { clsx } from 'clsx'
  import {
    BuildingOfficeIcon,
    BanknotesIcon,
    ChartBarIcon,
    ArrowTrendingUpIcon,
    CurrencyDollarIcon,
  } from '@heroicons/react/24/outline'

  const navigation = [
    { name: 'Company', href: '/dashboard/company', icon: BuildingOfficeIcon },
    { name: 'Bank', href: '/dashboard/bank', icon: BanknotesIcon },
    { name: 'Sector', href: '/dashboard/sector', icon: ChartBarIcon },
    { name: 'Technical', href: '/dashboard/technical', icon: ArrowTrendingUpIcon },
    { name: 'FX & Commodities', href: '/dashboard/fx', icon: CurrencyDollarIcon },
  ]

  export function Sidebar() {
    const pathname = usePathname()

    return (
      <aside className="w-64 bg-card border-r border-gray-800 min-h-screen p-4">
        <div className="mb-8">
          <h1 className="text-xl font-bold text-white">VN Dashboard</h1>
          <p className="text-sm text-gray-400">Stock Analysis</p>
        </div>

        <nav className="space-y-1">
          {navigation.map((item) => {
            const isActive = pathname.startsWith(item.href)
            return (
              <Link
                key={item.name}
                href={item.href}
                className={clsx(
                  'flex items-center gap-3 px-3 py-2 rounded-lg transition-colors',
                  isActive
                    ? 'bg-primary text-white'
                    : 'text-gray-400 hover:bg-card-hover hover:text-white'
                )}
              >
                <item.icon className="h-5 w-5" />
                {item.name}
              </Link>
            )
          })}
        </nav>
      </aside>
    )
  }
  ```

- [ ] **Create Header component**
  ```tsx
  // frontend/components/layout/Header.tsx
  'use client'

  import { useAuth } from '@/hooks/useAuth'
  import { Button } from '../ui/Button'
  import { logout } from '@/lib/auth'
  import { useRouter } from 'next/navigation'

  export function Header() {
    const { user, mutate } = useAuth()
    const router = useRouter()

    const handleLogout = async () => {
      await logout()
      mutate(null)
      router.push('/login')
    }

    return (
      <header className="h-16 bg-card border-b border-gray-800 px-6 flex items-center justify-between">
        <div>
          {/* Search or breadcrumbs can go here */}
        </div>

        <div className="flex items-center gap-4">
          {user && (
            <>
              <span className="text-gray-400">{user.full_name}</span>
              <Button variant="secondary" size="sm" onClick={handleLogout}>
                Logout
              </Button>
            </>
          )}
        </div>
      </header>
    )
  }
  ```

- [ ] **Create Dashboard layout**
  ```tsx
  // frontend/app/dashboard/layout.tsx
  import { Sidebar } from '@/components/layout/Sidebar'
  import { Header } from '@/components/layout/Header'

  export default function DashboardLayout({
    children,
  }: {
    children: React.ReactNode
  }) {
    return (
      <div className="flex min-h-screen bg-background">
        <Sidebar />
        <div className="flex-1 flex flex-col">
          <Header />
          <main className="flex-1 p-6">
            {children}
          </main>
        </div>
      </div>
    )
  }
  ```

#### Step 3.5: Create Hooks

- [ ] **Create useAuth hook**
  ```tsx
  // frontend/hooks/useAuth.ts
  'use client'

  import useSWR from 'swr'
  import { fetcher } from '@/lib/api'

  interface User {
    id: number
    email: string
    full_name: string
    is_active: boolean
  }

  export function useAuth() {
    const { data, error, isLoading, mutate } = useSWR<User>(
      '/auth/me',
      fetcher,
      {
        // Don't retry on 401
        onErrorRetry: (error, key, config, revalidate, { retryCount }) => {
          if (error.message.includes('401')) return
          if (retryCount >= 3) return
          setTimeout(() => revalidate({ retryCount }), 5000)
        },
      }
    )

    return {
      user: data,
      isLoading,
      isAuthenticated: !!data && !error,
      error,
      mutate,
    }
  }
  ```

- [ ] **Create useTickers hook**
  ```tsx
  // frontend/hooks/useTickers.ts
  'use client'

  import useSWR from 'swr'
  import { fetcher } from '@/lib/api'

  interface TickerListResponse {
    tickers: string[]
    count: number
  }

  interface TickerInfo {
    ticker: string
    company_name: string
    sector: string
    entity_type: string
    industry: string
  }

  export function useTickers(entityType?: string) {
    const url = entityType
      ? `/api/tickers/?entity_type=${entityType}`
      : '/api/tickers/'

    const { data, error, isLoading } = useSWR<TickerListResponse>(url, fetcher)

    return {
      tickers: data?.tickers || [],
      count: data?.count || 0,
      isLoading,
      isError: error,
    }
  }

  export function useTickerInfo(ticker: string) {
    const { data, error, isLoading } = useSWR<TickerInfo>(
      ticker ? `/api/tickers/${ticker}` : null,
      fetcher
    )

    return {
      ticker: data,
      isLoading,
      isError: error,
    }
  }
  ```

### Week 11: Company Page

#### Step 3.6: Create Company Components

- [ ] **Create useCompany hook**
  ```tsx
  // frontend/hooks/useCompany.ts
  'use client'

  import useSWR from 'swr'
  import { fetcher } from '@/lib/api'

  interface CompanyMetrics {
    symbol: string
    report_date: string
    year: number
    quarter?: number
    net_revenue?: number
    gross_profit?: number
    npatmi?: number
    gross_profit_margin?: number
    net_margin?: number
    roe?: number
    roa?: number
    eps?: number
  }

  interface CompanyMetricsResponse {
    ticker: string
    period: string
    data: CompanyMetrics[]
    count: number
  }

  export function useCompanyMetrics(
    ticker: string,
    period: string = 'Quarterly',
    limit: number = 8
  ) {
    const url = ticker
      ? `/api/company/${ticker}/metrics?period=${period}&limit=${limit}`
      : null

    const { data, error, isLoading } = useSWR<CompanyMetricsResponse>(
      url,
      fetcher
    )

    return {
      data: data?.data || [],
      isLoading,
      isError: error,
    }
  }

  export function useCompanyLatest(ticker: string) {
    const { data, error, isLoading } = useSWR<CompanyMetrics>(
      ticker ? `/api/company/${ticker}/latest` : null,
      fetcher
    )

    return {
      metrics: data,
      isLoading,
      isError: error,
    }
  }
  ```

- [ ] **Create FinancialsTable component**
  ```tsx
  // frontend/components/company/FinancialsTable.tsx
  'use client'

  import { Table } from '../ui/Table'
  import { formatNumber, formatPercent } from '@/lib/utils'

  interface CompanyMetrics {
    report_date: string
    year: number
    quarter?: number
    net_revenue?: number
    npatmi?: number
    gross_profit_margin?: number
    net_margin?: number
    roe?: number
    roa?: number
  }

  interface Props {
    data: CompanyMetrics[]
    period: string
  }

  export function FinancialsTable({ data, period }: Props) {
    const columns = [
      {
        key: 'period',
        header: 'Period',
        render: (_: any, row: CompanyMetrics) =>
          period === 'Quarterly'
            ? `Q${row.quarter}/${row.year}`
            : String(row.year),
      },
      {
        key: 'net_revenue',
        header: 'Revenue (B)',
        render: (v: number) => formatNumber(v / 1e9, 1),
        className: 'text-right',
      },
      {
        key: 'npatmi',
        header: 'Net Profit (B)',
        render: (v: number) => formatNumber(v / 1e9, 1),
        className: 'text-right',
      },
      {
        key: 'gross_profit_margin',
        header: 'Gross Margin',
        render: (v: number) => formatPercent(v),
        className: 'text-right',
      },
      {
        key: 'net_margin',
        header: 'Net Margin',
        render: (v: number) => formatPercent(v),
        className: 'text-right',
      },
      {
        key: 'roe',
        header: 'ROE',
        render: (v: number) => formatPercent(v),
        className: 'text-right',
      },
    ]

    return <Table columns={columns} data={data} />
  }
  ```

- [ ] **Create utils for formatting**
  ```tsx
  // frontend/lib/utils.ts
  export function formatNumber(value: number | undefined | null, decimals: number = 0): string {
    if (value === undefined || value === null || isNaN(value)) return '-'
    return value.toLocaleString('vi-VN', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    })
  }

  export function formatPercent(value: number | undefined | null): string {
    if (value === undefined || value === null || isNaN(value)) return '-'
    return `${(value * 100).toFixed(2)}%`
  }

  export function formatCurrency(value: number | undefined | null): string {
    if (value === undefined || value === null || isNaN(value)) return '-'
    return value.toLocaleString('vi-VN') + ' VND'
  }
  ```

#### Step 3.7: Create Company Pages

- [ ] **Create Company List page**
  ```tsx
  // frontend/app/dashboard/company/page.tsx
  'use client'

  import { useState } from 'react'
  import Link from 'next/link'
  import { useTickers } from '@/hooks/useTickers'
  import { Card } from '@/components/ui/Card'
  import { Input } from '@/components/ui/Input'

  export default function CompanyListPage() {
    const { tickers, isLoading } = useTickers('COMPANY')
    const [search, setSearch] = useState('')

    const filteredTickers = tickers.filter(t =>
      t.toLowerCase().includes(search.toLowerCase())
    )

    if (isLoading) {
      return <div className="text-white">Loading...</div>
    }

    return (
      <div>
        <h1 className="text-2xl font-bold text-white mb-6">Company Analysis</h1>

        <Card className="mb-6">
          <input
            type="text"
            placeholder="Search ticker..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-background text-white px-4 py-2 rounded-lg border border-gray-700 focus:outline-none focus:border-primary"
          />
        </Card>

        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          {filteredTickers.map((ticker) => (
            <Link
              key={ticker}
              href={`/dashboard/company/${ticker}`}
              className="bg-card hover:bg-card-hover p-4 rounded-lg text-center transition-colors border border-gray-800"
            >
              <span className="text-white font-bold">{ticker}</span>
            </Link>
          ))}
        </div>
      </div>
    )
  }
  ```

- [ ] **Create Company Detail page**
  ```tsx
  // frontend/app/dashboard/company/[ticker]/page.tsx
  'use client'

  import { useState } from 'react'
  import { useTickerInfo } from '@/hooks/useTickers'
  import { useCompanyMetrics, useCompanyLatest } from '@/hooks/useCompany'
  import { Card } from '@/components/ui/Card'
  import { MetricCard } from '@/components/ui/MetricCard'
  import { FinancialsTable } from '@/components/company/FinancialsTable'
  import { Button } from '@/components/ui/Button'

  interface Props {
    params: { ticker: string }
  }

  export default function CompanyDetailPage({ params }: Props) {
    const { ticker } = params
    const [period, setPeriod] = useState<'Quarterly' | 'Yearly'>('Quarterly')

    const { ticker: tickerInfo, isLoading: infoLoading } = useTickerInfo(ticker)
    const { metrics: latest, isLoading: latestLoading } = useCompanyLatest(ticker)
    const { data: financials, isLoading: financialsLoading } = useCompanyMetrics(
      ticker,
      period,
      12
    )

    if (infoLoading || latestLoading) {
      return <div className="text-white">Loading...</div>
    }

    return (
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-white">{ticker}</h1>
          <p className="text-gray-400">
            {tickerInfo?.company_name} | {tickerInfo?.sector}
          </p>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <MetricCard
            label="ROE"
            value={latest?.roe || 0}
            format="percent"
          />
          <MetricCard
            label="ROA"
            value={latest?.roa || 0}
            format="percent"
          />
          <MetricCard
            label="Net Margin"
            value={latest?.net_margin || 0}
            format="percent"
          />
          <MetricCard
            label="EPS"
            value={latest?.eps || 0}
            format="number"
          />
        </div>

        {/* Financials Table */}
        <Card>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold text-white">Financial Metrics</h2>
            <div className="flex gap-2">
              <Button
                variant={period === 'Quarterly' ? 'primary' : 'secondary'}
                size="sm"
                onClick={() => setPeriod('Quarterly')}
              >
                Quarterly
              </Button>
              <Button
                variant={period === 'Yearly' ? 'primary' : 'secondary'}
                size="sm"
                onClick={() => setPeriod('Yearly')}
              >
                Yearly
              </Button>
            </div>
          </div>

          {financialsLoading ? (
            <div className="text-gray-400">Loading...</div>
          ) : (
            <FinancialsTable data={financials} period={period} />
          )}
        </Card>
      </div>
    )
  }
  ```

### Week 12: Charts & Polish

#### Step 3.8: Create Chart Components

- [ ] **Create LineChart component with ApexCharts**
  ```tsx
  // frontend/components/charts/LineChart.tsx
  'use client'

  import dynamic from 'next/dynamic'
  import { ApexOptions } from 'apexcharts'

  // Load ApexCharts dynamically (no SSR)
  const Chart = dynamic(() => import('react-apexcharts'), { ssr: false })

  interface DataPoint {
    date: string
    value: number
  }

  interface Props {
    data: DataPoint[]
    title?: string
    color?: string
    height?: number
  }

  export function LineChart({
    data,
    title,
    color = '#3b82f6',
    height = 300
  }: Props) {
    const options: ApexOptions = {
      chart: {
        type: 'line',
        background: 'transparent',
        toolbar: { show: false },
      },
      theme: { mode: 'dark' },
      stroke: {
        curve: 'smooth',
        width: 2,
      },
      colors: [color],
      xaxis: {
        categories: data.map(d => d.date),
        labels: {
          style: { colors: '#9ca3af' },
        },
      },
      yaxis: {
        labels: {
          style: { colors: '#9ca3af' },
          formatter: (val) => val.toLocaleString(),
        },
      },
      grid: {
        borderColor: '#374151',
      },
      tooltip: {
        theme: 'dark',
      },
    }

    const series = [{
      name: title || 'Value',
      data: data.map(d => d.value),
    }]

    return (
      <div>
        {title && <h3 className="text-white font-medium mb-2">{title}</h3>}
        <Chart
          options={options}
          series={series}
          type="line"
          height={height}
        />
      </div>
    )
  }
  ```

- [ ] **Create RevenueChart for Company page**
  ```tsx
  // frontend/components/company/RevenueChart.tsx
  'use client'

  import { LineChart } from '../charts/LineChart'

  interface CompanyMetrics {
    report_date: string
    net_revenue?: number
    npatmi?: number
  }

  interface Props {
    data: CompanyMetrics[]
  }

  export function RevenueChart({ data }: Props) {
    const chartData = data.map(d => ({
      date: d.report_date,
      value: (d.net_revenue || 0) / 1e9,  // Convert to billions
    }))

    return (
      <LineChart
        data={chartData}
        title="Revenue (Billion VND)"
        color="#22c55e"
        height={250}
      />
    )
  }
  ```

#### Step 3.9: Add Charts to Company Page

- [ ] **Update Company Detail page with charts**
  ```tsx
  // Add to frontend/app/dashboard/company/[ticker]/page.tsx

  import { RevenueChart } from '@/components/company/RevenueChart'

  // In the JSX, add after Key Metrics section:
  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
    <Card title="Revenue Trend">
      <RevenueChart data={financials} />
    </Card>
    <Card title="Profitability">
      {/* Add ProfitabilityChart */}
    </Card>
  </div>
  ```

---

## Success Criteria

### UI Components Working

- [ ] All base components render correctly (Button, Card, Table, etc.)
- [ ] Dark theme applied consistently
- [ ] Responsive on mobile/tablet/desktop

### Navigation Working

- [ ] Sidebar shows all menu items
- [ ] Active state highlights correctly
- [ ] URL changes when navigating

### Company Page Complete

- [ ] Ticker list loads and displays
- [ ] Search filters tickers correctly
- [ ] Detail page shows metrics
- [ ] Period toggle switches data
- [ ] Charts display correctly

### API Integration

- [ ] SWR fetches data from FastAPI
- [ ] Loading states display
- [ ] Error states handled
- [ ] Data refreshes on navigation

---

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| ApexCharts SSR errors | Medium | Use dynamic import with ssr: false |
| Type mismatches | Medium | Define TypeScript interfaces carefully |
| Styling inconsistencies | Low | Use design tokens in Tailwind config |
| Performance issues | Low | Limit data fetched, use pagination |

---

## Next Phase

After completing Phase 3, proceed to:
[Phase 4: Feature Implementation](./phase-04-feature-implementation.md)

---

*Phase created: 2026-01-15*
