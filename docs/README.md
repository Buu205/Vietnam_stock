# Documentation

Tài liệu hướng dẫn và tham khảo.
Documentation and reference guides.

---

## 📁 Structure

```
docs/
├── CURRENT/                    # Active documentation
│   ├── FORMULA_IMPLEMENTATION_SUMMARY.md
│   ├── STREAMLIT_DASHBOARD_PLAN.md
│   └── ...
│
├── Formula/                    # Formula reference & guides
│   ├── AI_FORMULA_GUIDE.md     # AI formula implementation guide
│   ├── BANK_FORMULAS.md        # Banking sector formulas
│   ├── COMPANY_FORMULAS.md     # Company sector formulas
│   ├── INSURANCE_FORMULAS.md   # Insurance sector formulas
│   └── SECURITY_FORMULAS.md    # Securities/brokerage formulas
│
├── archive/                    # Historical documentation
│   ├── phase_0_history/        # Phase 0 implementation history
│   └── ...
│
├── mongodb_mcp/                # MongoDB integration docs
├── streamlit_UI_build/         # UI design documentation
├── troubleshooting/            # Debugging & troubleshooting
└── examples/                   # Code examples
```

---

## 🔍 Finding Documentation

### Current Implementation
- **Architecture:** [CURRENT/](CURRENT/)
- **Formula Reference:** [Formula/AI_FORMULA_GUIDE.md](Formula/AI_FORMULA_GUIDE.md)
- **Daily Pipelines:** [../PROCESSORS/pipelines/README.md](../PROCESSORS/pipelines/README.md)

### Formula Guides
- **Banking:** [Formula/BANK_FORMULAS.md](Formula/BANK_FORMULAS.md)
- **Companies:** [Formula/COMPANY_FORMULAS.md](Formula/COMPANY_FORMULAS.md)
- **Insurance:** [Formula/INSURANCE_FORMULAS.md](Formula/INSURANCE_FORMULAS.md)
- **Securities:** [Formula/SECURITY_FORMULAS.md](Formula/SECURITY_FORMULAS.md)

### Historical Changes
- **Phase 0 History:** [archive/phase_0_history/](archive/phase_0_history/)

---

## 📚 Key Documents

### CURRENT/ (Active Documentation)

**FORMULA_IMPLEMENTATION_SUMMARY.md**
- Summary of all implemented formulas
- Entity-specific metrics
- Data sources and transformations

**STREAMLIT_DASHBOARD_PLAN.md**
- Dashboard design and implementation plan
- UI/UX specifications
- Feature roadmap

### Formula/ (Formula Reference)

**AI_FORMULA_GUIDE.md**
- Comprehensive guide for AI assistants
- Formula implementation patterns
- Best practices

**Entity-Specific Formula Guides**
- Detailed formulas for each entity type
- Vietnamese names → English mappings
- Calculation methods

---

## 🛠️ Troubleshooting

### Common Issues
See [troubleshooting/](troubleshooting/) for debugging guides.

### Examples
See [examples/](examples/) for code examples and usage patterns.

---

## 📝 Documentation Standards

When creating new documentation:

1. **Use clear section headers** (##, ###)
2. **Include code examples** with proper syntax highlighting
3. **Add Vietnamese translations** for key terms
4. **Update this README** when adding new docs
5. **Link related documents** for easy navigation

---

## 🔗 Quick Links

- **Root README:** [../README.md](../README.md)
- **CLAUDE.md:** [../CLAUDE.md](../CLAUDE.md) - AI/Developer guidelines
- **Daily Pipelines:** [../PROCESSORS/pipelines/README.md](../PROCESSORS/pipelines/README.md)
- **Config Documentation:** [../config/README.md](../config/README.md)

---

**Author:** Claude Code
**Last Updated:** 2025-12-15
**Version:** 1.0.0
