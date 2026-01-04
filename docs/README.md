# Documentation Index

Vietnam Dashboard documentation hub. Navigate to specific docs by category.

---

## Quick Links

| Need | Go To |
|------|-------|
| Understand system design | [architecture/](architecture/) |
| View page-specific logic | [logic/](logic/) |
| Follow tutorials | [guides/](guides/) |
| Code standards | [reference/standards.md](reference/standards.md) |

---

## Architecture

System design and data flow documentation.

| Doc | Description |
|-----|-------------|
| [system.md](architecture/system.md) | Full system architecture (72KB) - registries, pipelines, data flow |
| [webapp.md](architecture/webapp.md) | WEBAPP structure, components, services |
| [forecast.md](architecture/forecast.md) | Forecast module design (BSC vs Consensus) |

---

## Logic (Per Dashboard)

Pure business logic reference for each page. No code - just parameters and rules.

| Dashboard | Doc | Key Metrics |
|-----------|-----|-------------|
| Technical | [technical.md](logic/technical.md) | Signals, RRG, Breadth, Scanner |
| Bank | [bank.md](logic/bank.md) | NIM, NPL, CASA, LDR, CIR |
| Company | [company.md](logic/company.md) | ROE, Margins, D/E, Cash Flow |
| Sector | [sector.md](logic/sector.md) | PE/PB Distribution, Z-Score, Percentile |
| Forecast | [forecast.md](logic/forecast.md) | BSC Ratings, Upside, Consensus Comparison |
| Security | [security.md](logic/security.md) | ROAE, Leverage, Portfolio Mix |
| FX/Commodities | [fx-commodities.md](logic/fx-commodities.md) | Interest Rates, Exchange Rates, Commodity Prices |

---

## Reference

Quick lookup documentation.

| Doc | Description |
|-----|-------------|
| [codebase.md](reference/codebase.md) | Codebase summary and structure |
| [standards.md](reference/standards.md) | Code standards and conventions |
| [pdr.md](reference/pdr.md) | Product Development Requirements |

---

## Guides

Step-by-step tutorials and pipelines.

| Guide | Description |
|-------|-------------|
| [forecast-pipeline.md](guides/forecast-pipeline.md) | Consensus forecast extraction pipeline |

---

## Archive

Historical documentation (read-only).

Location: [archive/](archive/)

---

## Related Documentation

| Location | Description |
|----------|-------------|
| [CLAUDE.md](../CLAUDE.md) | AI assistant instructions |
| [.claude/rules/](../.claude/rules/) | Critical rules, conventions, patterns |
| [.claude/guides/](../.claude/guides/) | Architecture, data flow, development |
| [.claude/reference/](../.claude/reference/) | Commands, paths, formulas |
| [plans/](../plans/) | Active development plans |

---

## Editing Logic Docs

To update trading/analysis parameters:

1. Find relevant logic doc in [logic/](logic/)
2. Edit threshold values, color codes, or rules
3. Corresponding code locations listed at bottom of each doc

**Example:** Change NPL warning threshold
1. Open [logic/bank.md](logic/bank.md)
2. Find "Reference Lines on Charts" section
3. Note current NPL threshold (3%)
4. Find code location: `WEBAPP/pages/bank/bank_dashboard.py`
5. Update the `fig.add_hline(y=3, ...)` line
