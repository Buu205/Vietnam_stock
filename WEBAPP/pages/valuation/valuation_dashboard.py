"""
Valuation Dashboard (DEPRECATED)
================================

This page has been consolidated into the Sector Analysis Dashboard.

All valuation features are now available in:
- Tab 1: VNIndex Analysis (VNINDEX, VNINDEX_EXCLUDE, BSC_INDEX variants)
- Tab 2: All Sectors Distribution (candlestick chart)
- Tab 3: Individual Analysis (single ticker with stats)

Run:
    streamlit run WEBAPP/pages/sector/sector_dashboard.py
"""

import streamlit as st
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from WEBAPP.core.styles import get_page_style

# Inject styles
st.markdown(get_page_style(), unsafe_allow_html=True)

# Deprecation notice
st.title("📊 Valuation Analysis")
st.markdown("---")

st.info("""
**📋 This page has been consolidated into Sector Analysis Dashboard**

All valuation features are now available with improved functionality:

| Feature | New Location |
|---------|-------------|
| PE/PB/EV-EBITDA Distribution | Sector Dashboard → All Sectors Distribution |
| Individual Stock Analysis | Sector Dashboard → Individual Analysis |
| VNIndex Metrics | Sector Dashboard → VNIndex Analysis |
| Histogram Distribution | Sector Dashboard → Individual Analysis |

**Why the change?**
- Unified charting with standardized components
- Centralized outlier filtering (PE > 100, PB > 20)
- Consistent Y-axis scaling across charts
- Histogram with 35 bins for better distribution visualization
""")

st.markdown("---")

# Navigation buttons
col1, col2 = st.columns(2)

with col1:
    if st.button("🚀 Go to Sector Dashboard", use_container_width=True, type="primary"):
        st.switch_page("pages/sector/sector_dashboard.py")

with col2:
    if st.button("📈 Go to BSC Forecast", use_container_width=True):
        st.switch_page("pages/forecast/forecast_dashboard.py")

st.markdown("---")
st.caption("Note: This redirect page will be removed in a future release. Please update your bookmarks.")
