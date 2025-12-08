"""Router chung: tự động load Company Dashboard khi vào giao diện."""

import streamlit as st
import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Page configuration
st.set_page_config(page_title="VN Finance Dashboard", layout="wide")

# Import and render Company Dashboard directly
from streamlit_app.pages.company_dashboard_pyecharts import render_company_dashboard

if __name__ == "__main__":
    render_company_dashboard()
