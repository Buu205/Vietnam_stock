import streamlit as st

def render_top_nav():
    """
    Renders a top navigation bar with buttons for each dashboard page.
    Uses st.columns to arrange buttons horizontally.
    """
    
    # Define navigation items: (Label, Page Path)
    nav_items = [
        ("Company", "pages/company_dashboard_pyecharts.py"),
        ("Banking", "pages/bank_dashboard.py"),
        ("Securities", "pages/securities_dashboard.py"),
        ("Technical", "pages/technical_dashboard.py"),
        # ("News", "pages/news_dashboard.py"),  # Temporarily disabled
        ("Valuation", "pages/valuation_sector_dashboard.py"),
        ("Forecast", "pages/forecast_dashboard.py"),
    ]
    
    # Create a container for the nav bar
    with st.container():
        # Use columns for layout
        cols = st.columns(len(nav_items))
        
        for i, (label, page) in enumerate(nav_items):
            with cols[i]:
                # Check if this is the current page to highlight (optional, hard to detect perfectly in Streamlit)
                # For now, just render simple buttons
                if st.button(label, key=f"nav_{label}", width='stretch'):
                    st.switch_page(page)
        
        st.markdown("---")
