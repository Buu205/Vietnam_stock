"""
Global CSS styles for entire stock_dashboard
Apply Nunito font and yellow theme to all dashboards
"""

def get_global_css():
    """Return global CSS for all dashboards"""
    return """
    <style>
    /* ===== IMPORT NUNITO FONT ===== */
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;700&display=swap');
    
    /* ===== GLOBAL BACKGROUND ===== */
    .stApp {
        background-color: #fffbf0 !important;
        font-family: 'Nunito', sans-serif !important;
    }
    
    /* ===== GLOBAL FONT FOR ALL ELEMENTS ===== */
    * {
        font-family: 'Nunito', sans-serif !important;
    }
    
    .main .block-container {
        background-color: #fffbf0 !important;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* ===== SIDEBAR ===== */
    .css-1d391kg {
        background-color: #fff8e1 !important;
        font-family: 'Nunito', sans-serif !important;
    }
    
    /* ===== HEADER ===== */
    .stApp > header {
        background-color: #fff8e1 !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Nunito', sans-serif !important;
        font-weight: 700 !important;
        color: #2c3e50 !important;
    }
    
    /* ===== BUTTONS ===== */
    .stButton > button {
        font-family: 'Nunito', sans-serif !important;
        font-weight: 700 !important;
    }
    
    /* ===== CHARTS (PLOTLY) ===== */
    .stPlotlyChart {
        font-family: 'Nunito', sans-serif !important;
    }
    
    /* ===== CHARTS (PYECHARTS) ===== */
    .streamlit-echarts {
        font-family: 'Nunito', sans-serif !important;
    }
    
    /* ===== DATAFRAME/TABLE ===== */
    [data-testid="stDataFrame"] {
        font-family: 'Nunito', sans-serif !important;
        background-color: #fff8e1 !important;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        border: 1px solid #e1e4e8;
    }
    
    [data-testid="stDataFrame"] thead {
        position: sticky;
        top: 0;
        z-index: 100;
        background-color: #fff3e0 !important;
    }
    
    [data-testid="stDataFrame"] th {
        background-color: #fff3e0 !important;
        font-family: 'Nunito', sans-serif !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        padding: 10px 12px !important;
        color: #24292f !important;
        text-align: center !important;
        border-bottom: 2px solid #d0d7de !important;
        white-space: nowrap;
    }
    
    [data-testid="stDataFrame"] tbody tr:nth-child(even) {
        background-color: #fff8e1 !important;
    }
    
    [data-testid="stDataFrame"] tbody tr:nth-child(odd) {
        background-color: #fffbf0 !important;
    }
    
    [data-testid="stDataFrame"] tbody tr:hover {
        background-color: #ffe0b2 !important;
        transition: background-color 0.15s ease;
    }
    
    [data-testid="stDataFrame"] td {
        font-family: 'Nunito', sans-serif !important;
        font-size: 13px !important;
        padding: 8px 12px !important;
        line-height: 1.4 !important;
        color: #24292f;
        border-bottom: 1px solid #eaeef2;
    }
    
    /* ===== METRICS ===== */
    [data-testid="metric-container"] {
        font-family: 'Nunito', sans-serif !important;
    }
    
    [data-testid="metric-container"] [data-testid="metric-value"] {
        font-family: 'Nunito', sans-serif !important;
        font-weight: 700 !important;
    }
    
    [data-testid="metric-container"] [data-testid="metric-label"] {
        font-family: 'Nunito', sans-serif !important;
        font-weight: 400 !important;
    }
    
    /* ===== TABS ===== */
    .stTabs [data-baseweb="tab-list"] button {
        font-family: 'Nunito', sans-serif !important;
        font-weight: 600 !important;
    }
    
    /* ===== SELECTBOX, MULTISELECT ===== */
    .stSelectbox label,
    .stMultiSelect label {
        font-family: 'Nunito', sans-serif !important;
        font-weight: 600 !important;
    }
    
    /* ===== ALERTS ===== */
    .stAlert {
        font-family: 'Nunito', sans-serif !important;
    }
    
    /* ===== MARKDOWN ===== */
    .stMarkdown {
        font-family: 'Nunito', sans-serif !important;
    }
    
    /* ===== EXPANDER ===== */
    .streamlit-expanderHeader {
        font-family: 'Nunito', sans-serif !important;
        font-weight: 600 !important;
    }
    
    /* ===== CAPTIONS ===== */
    .stCaption {
        font-family: 'Nunito', sans-serif !important;
    }
    
    /* ===== DOWNLOAD BUTTON ===== */
    .stDownloadButton {
        font-family: 'Nunito', sans-serif !important;
    }
    
    /* ===== PROGRESS BAR ===== */
    .stProgress {
        font-family: 'Nunito', sans-serif !important;
    }
    
    /* ===== SPINNER ===== */
    .stSpinner {
        font-family: 'Nunito', sans-serif !important;
    }
    
    /* ===== SLIDER ===== */
    .stSlider label {
        font-family: 'Nunito', sans-serif !important;
        font-weight: 600 !important;
    }
    
    /* ===== NUMBER INPUT ===== */
    .stNumberInput label {
        font-family: 'Nunito', sans-serif !important;
        font-weight: 600 !important;
    }
    
    /* ===== TEXT INPUT ===== */
    .stTextInput label {
        font-family: 'Nunito', sans-serif !important;
        font-weight: 600 !important;
    }
    
    /* ===== SCROLLBAR STYLING ===== */
    [data-testid="stDataFrame"]::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    [data-testid="stDataFrame"]::-webkit-scrollbar-track {
        background: #f1f3f5;
        border-radius: 5px;
    }
    
    [data-testid="stDataFrame"]::-webkit-scrollbar-thumb {
        background: #adb5bd;
        border-radius: 5px;
    }
    
    [data-testid="stDataFrame"]::-webkit-scrollbar-thumb:hover {
        background: #868e96;
    }
    </style>
    """

def inject_global_styles():
    """Inject global CSS into Streamlit app"""
    import streamlit as st
    st.markdown(get_global_css(), unsafe_allow_html=True)
