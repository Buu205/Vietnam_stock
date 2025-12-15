# Claude Code Plugins - Usage Guide
# Hướng Dẫn Sử Dụng Plugins Claude Code

**Date:** 2025-12-15
**Status:** ✅ Installed & Ready
**Plugins:** `frontend-design`, `feature-dev`, `commit-commands`

---

## 📦 Installed Plugins

### 1. Frontend Design Plugin

**Purpose:** Create distinctive, production-grade frontend interfaces with bold aesthetic choices

**Auto-activated when:**
- Building Streamlit dashboard components
- Creating UI/UX elements
- Designing visual components
- Working on frontend styling

**Key Features:**
- ✅ Bold aesthetic choices (no generic AI look)
- ✅ Distinctive typography and color palettes
- ✅ High-impact animations and visual details
- ✅ Context-aware implementation
- ✅ Production-ready code

**Usage Examples:**

```bash
# Streamlit dashboard design
"Create a sector analysis dashboard for Vietnam stock market"
"Build a financial metrics comparison table with modern design"
"Design a dark mode settings panel for the dashboard"

# Component design
"Create a card component for displaying PE/PB ratios with visual indicators"
"Build an interactive chart component for sector performance"
"Design a stock screener interface with filters and sorting"
```

**Expected Output:**
- Clean, production-ready Streamlit code
- Custom CSS styling (when needed)
- Thoughtful color schemes and typography
- Smooth animations and transitions
- Mobile-responsive design (where applicable)

**Documentation:** [plugins/frontend-design/README.md](../plugins/frontend-design/README.md)

---

### 2. Feature Development Plugin

**Purpose:** Comprehensive 7-phase workflow for building new features systematically

**Command:** `/feature-dev [description]`

**7-Phase Workflow:**

#### Phase 1: Discovery 🔍
- Clarifies feature requirements
- Asks what problem you're solving
- Identifies constraints
- Confirms understanding

**Example:**
```bash
/feature-dev Add real-time stock price alerts
```
Claude will ask:
- What triggers should generate alerts?
- Where should alerts be displayed?
- How should alerts be stored?
- What notification methods? (UI, email, etc.)

#### Phase 2: Codebase Exploration 🗺️
- Launches 2-3 `code-explorer` agents in parallel
- Analyzes similar features in existing code
- Maps architecture and patterns
- Identifies key files to read

**Example Output:**
```
Found similar features:
- Sector analysis (PROCESSORS/sector/): Aggregation pattern
- Technical alerts (PROCESSORS/technical/indicators/): Alert detection pattern
- Valuation metrics (PROCESSORS/valuation/): Calculation pattern

Key files to understand:
- PROCESSORS/technical/indicators/alert_detector.py:45 - Alert detection logic
- WEBAPP/pages/technical_analysis.py:123 - Alert display UI
- config/business_logic/alerts/ - Alert configuration
```

#### Phase 3: Clarifying Questions ❓
- Reviews codebase findings
- Identifies underspecified aspects
- Asks edge case questions
- **WAITS for your answers before proceeding**

**Example:**
```
Before designing the architecture, I need to clarify:

1. Alert persistence: Store in parquet files or database?
2. Alert frequency: Real-time vs daily batch?
3. Integration: Add to existing TA pipeline or separate service?
4. UI placement: New page or add to existing dashboard?
5. Historical alerts: Keep history or only show current?
```

#### Phase 4: Architecture Design 🏗️
- Launches 2-3 `code-architect` agents
- Designs multiple implementation approaches
- Compares trade-offs
- Recommends best approach
- **Asks which approach you prefer**

**Example Output:**
```
I've designed 3 approaches:

Approach 1: Minimal Changes
- Extend TechnicalAlertDetector with new alert types
- Add alert persistence to existing TA pipeline
- Display in existing Technical Analysis dashboard
Pros: Fast (1-2 hours), low risk, reuses existing code
Cons: Couples alert logic, harder to extend later

Approach 2: Clean Architecture
- New AlertService with plugin architecture
- Separate alert storage service
- Dedicated Alerts dashboard page
Pros: Clean separation, highly extensible, testable
Cons: More files (8-10), more time (1-2 days)

Approach 3: Pragmatic Balance
- New StockAlertManager class in PROCESSORS/
- Integrate with existing TA pipeline
- Add Alerts tab to existing dashboard
Pros: Balanced complexity, good boundaries
Cons: Some coupling remains

Recommendation: Approach 3 - gives you clean boundaries without
excessive refactoring, fits existing architecture well.

Which approach would you like to use?
```

#### Phase 5: Implementation 💻
- **Waits for explicit approval**
- Reads all relevant files
- Implements following chosen architecture
- Follows codebase conventions (CLAUDE.md)
- Tracks progress with todos

#### Phase 6: Quality Review ✅
- Launches 3 `code-reviewer` agents in parallel
- Reviews for:
  - Simplicity/DRY/Elegance
  - Bugs/Correctness
  - Conventions/Abstractions
- Presents findings
- **Asks what you want to do** (fix now/later/proceed)

**Example Output:**
```
Code Review Results:

High Priority Issues:
1. Alert deduplication missing (PROCESSORS/alerts/alert_manager.py:45)
2. Memory leak: Alert history not bounded (PROCESSORS/alerts/alert_manager.py:89)

Medium Priority:
1. Could simplify alert filtering logic (PROCESSORS/alerts/alert_manager.py:120)
2. Consider extracting alert config validation

All tests pass. Code follows CLAUDE.md conventions.

What would you like to do?
```

#### Phase 7: Summary 📋
- Marks todos complete
- Summarizes what was built
- Lists key decisions
- Lists modified files
- Suggests next steps

---

## 🎯 Use Cases for Vietnam Dashboard

### Frontend Design Plugin

**Use for:**
1. **Dashboard Pages** - Creating new Streamlit dashboard pages
2. **Data Visualization** - Designing charts, tables, metrics displays
3. **UI Components** - Building reusable components (cards, filters, etc.)
4. **Styling** - Improving visual design of existing pages
5. **User Experience** - Enhancing interactivity and responsiveness

**Examples:**

```bash
# Sector Analysis Dashboard
"Create a comprehensive sector analysis dashboard showing:
- Sector performance comparison (bar chart)
- Top 3 stocks per sector (cards with metrics)
- Money flow visualization (sankey diagram)
- Sector rotation signals (color-coded table)"

# Stock Screener
"Build a stock screener interface with:
- Multi-criteria filters (PE, PB, ROE, etc.)
- Sort by any metric
- Save filter presets
- Export results to Excel"

# Valuation Dashboard
"Design a valuation metrics dashboard:
- PE/PB/EV-EBITDA historical charts
- VNINDEX valuation bands
- Sector PE comparison
- Interactive date range selector"
```

### Feature Development Plugin

**Use for:**
1. **New Features** - Adding significant new functionality
2. **Integrations** - Connecting new data sources or services
3. **Refactoring** - Restructuring existing features
4. **Complex Changes** - Multi-file, multi-component updates

**Examples:**

```bash
# Add Real-time Data
/feature-dev Add real-time stock price updates using WebSocket

# Forecast Integration
/feature-dev Integrate BSC forecast data into dashboard with comparison charts

# Alert System
/feature-dev Build price alert system with email notifications

# Portfolio Tracking
/feature-dev Add portfolio tracking feature with performance metrics

# Sector Rotation
/feature-dev Implement sector rotation detection and visualization
```

---

### 3. Commit Commands Plugin

**Purpose:** Streamline git workflow with simple commands for committing, pushing, and creating PRs

**Commands:**

| Command | Description |
|---------|-------------|
| `/commit` | Auto-generate commit message based on changes |
| `/commit-push-pr` | Commit + Push + Create PR in one step |
| `/clean_gone` | Clean up local branches deleted from remote |

**`/commit` - Auto Commit:**
```bash
/commit
```
- Analyzes staged and unstaged changes
- Reviews recent commit messages to match repo style
- Drafts appropriate commit message
- Stages relevant files
- Creates the commit

**`/commit-push-pr` - Full Workflow:**
```bash
/commit-push-pr
```
- Creates new branch (if on main)
- Commits changes with auto-generated message
- Pushes to origin
- Creates PR with summary and test plan
- Returns PR URL

**`/clean_gone` - Cleanup:**
```bash
/clean_gone
```
- Finds all branches marked as [gone]
- Removes associated worktrees
- Deletes stale local branches

**Requirements:**
- GitHub CLI (`gh`) must be installed: `brew install gh`
- GitHub authentication: `gh auth login`

**Documentation:** [plugins/commit-commands/README.md](../plugins/commit-commands/README.md)

---

## 🚀 Quick Start

### Step 1: Verify Plugins Installed

```bash
# Check settings
cat .claude/settings.json
```

Should show:
```json
{
  "plugins": [
    {"source": "local", "path": "plugins/frontend-design"},
    {"source": "local", "path": "plugins/feature-dev"},
    {"source": "local", "path": "plugins/commit-commands"}
  ]
}
```

### Step 2: Use Plugins

**Frontend Design (Auto-activated):**
```bash
# Just describe what you want to build
"Create a sector comparison dashboard"
```
Claude will automatically use `frontend-design` skill.

**Feature Development (Manual command):**
```bash
# Use /feature-dev command
/feature-dev Add stock watchlist feature with price alerts
```
Claude will guide you through 7 phases.

**Commit Commands (Manual commands):**
```bash
# Quick commit with auto-generated message
/commit

# Full workflow: commit + push + create PR
/commit-push-pr

# Clean up stale branches
/clean_gone
```

---

## 📋 Best Practices

### Frontend Design

1. **Be specific about data:** "Show PE ratio, PB ratio, and market cap"
2. **Describe interactions:** "Click to drill down into sector details"
3. **Mention design preferences:** "Modern, clean, dark mode support"
4. **Reference examples:** "Similar to Bloomberg terminal style"

### Feature Development

1. **Use full workflow for complex features:** Don't skip phases
2. **Answer clarifying questions thoughtfully:** Saves time later
3. **Choose architecture deliberately:** Read trade-offs carefully
4. **Don't skip code review:** Catches issues early
5. **Read suggested files:** Helps understand context

---

## 🛠️ Troubleshooting

### Plugin Not Loading

**Issue:** Plugin features not available

**Solutions:**
1. Check `.claude/settings.json` exists and has correct paths
2. Verify plugin folders exist: `ls -la plugins/`
3. Restart Claude Code session
4. Check plugin.json files are valid JSON

### Frontend Design Not Auto-Activating

**Issue:** Skill not triggered for frontend work

**Solutions:**
1. Be explicit: "Create a Streamlit dashboard page..."
2. Mention UI/UX keywords: "design", "interface", "dashboard"
3. Manually mention: "Use frontend-design skill to..."

### Feature-Dev Workflow Too Long

**Issue:** 7 phases take too much time

**Solutions:**
1. Skip for simple changes (use normal Claude instead)
2. Use only specific agents: "Launch code-explorer to analyze..."
3. Be more specific upfront to reduce clarifying questions
4. Say "whatever you think is best" if no strong preference

---

## 📚 Additional Resources

**Plugin Documentation:**
- [Frontend Design README](../plugins/frontend-design/README.md)
- [Feature Development README](../plugins/feature-dev/README.md)
- [Frontend Aesthetics Cookbook](https://github.com/anthropics/claude-cookbooks/blob/main/coding/prompting_for_frontend_aesthetics.ipynb)

**Project Documentation:**
- [CLAUDE.md](../CLAUDE.md) - AI/Developer guidelines
- [STREAMLIT_DASHBOARD_PLAN.md](CURRENT/STREAMLIT_DASHBOARD_PLAN.md) - Dashboard architecture
- [PROCESSORS/README.md](../PROCESSORS/README.md) - Data processing overview

**Claude Code Docs:**
- [Plugins Overview](https://docs.claude.com/en/docs/claude-code/plugins)
- [Agent SDK](https://docs.claude.com/en/api/agent-sdk/overview)

---

## 🎯 Next Steps

### Recommended First Projects

1. **Improve Existing Dashboard** (Frontend Design)
   ```
   "Redesign the Company Dashboard page with:
   - Modern card layout for metrics
   - Interactive charts with tooltips
   - Color-coded performance indicators
   - Responsive design for mobile"
   ```

2. **Add New Feature** (Feature Development)
   ```bash
   /feature-dev Add stock comparison feature that shows side-by-side
   metrics for 2-4 stocks with visual indicators
   ```

3. **Build Sector Analysis UI** (Both Plugins)
   ```bash
   # First use feature-dev to architect
   /feature-dev Build comprehensive sector analysis feature with
   FA/TA aggregation and signal generation

   # Then use frontend-design (auto-activated)
   "Create the sector analysis dashboard UI"
   ```

---

**Last Updated:** 2025-12-15
**Version:** 1.0.0
**Status:** ✅ Ready to Use
